from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path
import json
import threading
import webbrowser
import os
import re
import base64
import time
import uuid
import random
from urllib.parse import urlsplit, parse_qs, urlencode

APP_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8765
OLLAMA_BASE = "http://127.0.0.1:11434"
COMFY_BASE = "http://127.0.0.1:8188"
GENERATED_DIR = APP_DIR / "generated_images"
GENERATED_DIR.mkdir(exist_ok=True)
SYSTEM_PROMPT = (
    "Tu es NOVA, une IA locale utile, claire et amicale. Réponds en français sauf si l'utilisateur "
    "demande une autre langue. Donne des réponses pratiques, explique les étapes simplement, et "
    "signale clairement toute incertitude. Pour le code, fournis des exemples complets et lisibles. "
    "Ne prétends pas avoir accès à Internet ou à des fichiers qui ne sont pas fournis."
)

class Handler(BaseHTTPRequestHandler):
    server_version = "NOVA-Local/1.0"

    def log_message(self, fmt, *args):
        print("[NOVA] " + (fmt % args))

    def send_json(self, status, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def comfy_get_json(self, path, timeout=8):
        req = Request(COMFY_BASE + path, headers={"Accept": "application/json"})
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_checkpoint_names(self):
        info = self.comfy_get_json("/object_info/CheckpointLoaderSimple", timeout=8)
        node = info.get("CheckpointLoaderSimple", {})
        required = node.get("input", {}).get("required", {})
        values = required.get("ckpt_name", [[]])[0]
        return [str(value) for value in values if isinstance(value, str)]

    def generate_local_image(self, payload):
        prompt = str(payload.get("prompt", "")).strip()
        negative_prompt = str(payload.get("negative_prompt", "")).strip()
        if not prompt:
            self.send_json(400, {"error": "Décris l'image que tu veux créer."})
            return
        if len(prompt) > 5000 or len(negative_prompt) > 2000:
            self.send_json(400, {"error": "La description est trop longue. Raccourcis-la."})
            return

        try:
            checkpoints = self.get_checkpoint_names()
        except Exception as exc:
            self.send_json(503, {
                "error": "Le moteur d'images ComfyUI n'est pas détecté.",
                "detail": "Démarre ComfyUI et attends qu'il soit prêt sur http://127.0.0.1:8188. " + str(exc)[:250],
            })
            return
        if not checkpoints:
            self.send_json(409, {
                "error": "Aucun modèle d'image n'est installé dans ComfyUI.",
                "detail": "Place un modèle compatible (.safetensors ou .ckpt) dans ComfyUI/models/checkpoints, puis redémarre ComfyUI.",
            })
            return

        model = str(payload.get("model", ""))
        if model not in checkpoints:
            model = checkpoints[0]
        try:
            width = int(payload.get("width", 768))
            height = int(payload.get("height", 768))
            steps = int(payload.get("steps", 12))
        except (TypeError, ValueError):
            self.send_json(400, {"error": "Les paramètres de l'image sont invalides."})
            return
        if width not in (512, 640, 768, 896, 1024) or height not in (512, 640, 768, 896, 1024):
            self.send_json(400, {"error": "Choisis une résolution proposée dans l'interface."})
            return
        if width * height > 1_048_576:
            self.send_json(400, {"error": "La résolution choisie est trop élevée."})
            return
        steps = max(5, min(30, steps))
        seed = random.randint(0, 2**31 - 1)
        client_id = uuid.uuid4().hex
        workflow = {
            "3": {"class_type": "KSampler", "inputs": {
                "seed": seed, "steps": steps, "cfg": 6.5, "sampler_name": "euler",
                "scheduler": "normal", "denoise": 1.0, "model": ["4", 0],
                "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]
            }},
            "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": model}},
            "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative_prompt or "low quality, blurry, distorted, watermark, text", "clip": ["4", 1]}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
            "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "NOVA", "images": ["8", 0]}}
        }

        try:
            body = json.dumps({"prompt": workflow, "client_id": client_id}, ensure_ascii=False).encode("utf-8")
            req = Request(COMFY_BASE + "/prompt", data=body, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
            with urlopen(req, timeout=20) as response:
                queued = json.loads(response.read().decode("utf-8"))
            prompt_id = queued.get("prompt_id")
            if not prompt_id:
                self.send_json(502, {"error": "ComfyUI n'a pas accepté la génération.", "detail": str(queued.get("error", queued))[:500]})
                return

            end_at = time.time() + 900
            image_entry = None
            while time.time() < end_at:
                time.sleep(1)
                history = self.comfy_get_json("/history/" + prompt_id, timeout=10)
                item = history.get(prompt_id, {})
                outputs = item.get("outputs", {})
                for node_output in outputs.values():
                    images = node_output.get("images", []) if isinstance(node_output, dict) else []
                    if images:
                        image_entry = images[0]
                        break
                if image_entry:
                    break
                status = item.get("status", {})
                if status.get("status_str") == "error" or status.get("completed") is False and status.get("messages") and any("execution_error" in str(m) for m in status.get("messages", [])):
                    self.send_json(502, {"error": "ComfyUI n'a pas pu créer l'image.", "detail": "Vérifie que le modèle installé est compatible et que le PC dispose d'assez de mémoire."})
                    return
            if not image_entry:
                self.send_json(504, {"error": "La génération prend trop de temps.", "detail": "Vérifie la fenêtre ComfyUI. Tu peux réessayer avec une résolution plus petite et moins d'étapes."})
                return

            query = urlencode({
                "filename": str(image_entry.get("filename", "")),
                "subfolder": str(image_entry.get("subfolder", "")),
                "type": str(image_entry.get("type", "output")),
            })
            req = Request(COMFY_BASE + "/view?" + query, headers={"Accept": "image/png,image/*"})
            with urlopen(req, timeout=30) as response:
                image_bytes = response.read()
            if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
                self.send_json(502, {"error": "ComfyUI a renvoyé un fichier d'image invalide."})
                return
            filename = "nova_" + uuid.uuid4().hex + ".png"
            target = GENERATED_DIR / filename
            target.write_bytes(image_bytes)
            self.send_json(200, {
                "ok": True,
                "image_url": "/generated/" + filename,
                "filename": filename,
                "model": model,
                "seed": seed,
                "width": width,
                "height": height,
                "steps": steps,
                "bytes": len(image_bytes),
            })
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:900]
            self.send_json(502, {"error": "Le moteur d'images a renvoyé une erreur.", "detail": detail or str(exc)})
        except URLError as exc:
            self.send_json(503, {"error": "Impossible de contacter ComfyUI.", "detail": str(exc.reason)[:300]})
        except Exception as exc:
            self.send_json(500, {"error": "Erreur pendant la création de l'image.", "detail": str(exc)[:400]})

    def do_GET(self):
        parsed = urlsplit(self.path)
        path = parsed.path
        if path == "/api/image-status":
            try:
                models = self.get_checkpoint_names()
                self.send_json(200, {
                    "ok": True,
                    "ready": bool(models),
                    "models": models,
                    "engine": "ComfyUI local",
                    "detail": "" if models else "ComfyUI répond, mais aucun modèle d'image n'est installé."
                })
            except Exception as exc:
                self.send_json(200, {
                    "ok": False,
                    "ready": False,
                    "models": [],
                    "engine": "ComfyUI local",
                    "error": "ComfyUI n'est pas démarré sur le port local 8188.",
                    "detail": str(exc)[:300],
                })
            return

        if path == "/api/images":
            files = []
            try:
                for item in sorted(GENERATED_DIR.glob("nova_*.png"), key=lambda f: f.stat().st_mtime, reverse=True)[:50]:
                    files.append({"filename": item.name, "url": "/generated/" + item.name, "created": int(item.stat().st_mtime), "bytes": item.stat().st_size})
            except OSError:
                pass
            self.send_json(200, {"images": files})
            return

        if path.startswith("/generated/"):
            filename = path.rsplit("/", 1)[-1]
            if not re.fullmatch(r"nova_[0-9a-f]{32}\.png", filename):
                self.send_error(404, "Image introuvable")
                return
            target = GENERATED_DIR / filename
            try:
                raw = target.read_bytes()
            except OSError:
                self.send_error(404, "Image introuvable")
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(raw)
            return

        if path == "/api/status":
            try:
                req = Request(OLLAMA_BASE + "/api/tags", headers={"Accept": "application/json"})
                with urlopen(req, timeout=3) as response:
                    data = json.loads(response.read().decode("utf-8"))
                models = [item.get("name", "") for item in data.get("models", []) if item.get("name")]
                self.send_json(200, {"ok": True, "models": models, "engine": "Ollama local"})
            except Exception as exc:
                self.send_json(200, {
                    "ok": False,
                    "models": [],
                    "error": "Ollama ne répond pas. Vérifie qu'Ollama est installé et lancé.",
                    "detail": str(exc)[:300],
                })
            return

        if path in ("/", "/index.html"):
            try:
                content = (APP_DIR / "index.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(content)
            except OSError:
                self.send_error(500, "Le fichier index.html est manquant.")
            return

        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        self.send_error(404, "Page introuvable")

    def do_POST(self):
        if self.path == "/api/image":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 100_000:
                    self.send_json(400, {"error": "Requête vide ou trop volumineuse."})
                    return
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(payload, dict):
                    self.send_json(400, {"error": "Paramètres invalides."})
                    return
                self.generate_local_image(payload)
            except json.JSONDecodeError:
                self.send_json(400, {"error": "Le format de la requête est invalide."})
            except Exception as exc:
                try:
                    self.send_json(500, {"error": "Erreur locale inattendue.", "detail": str(exc)[:400]})
                except Exception:
                    pass
            return

        if self.path != "/api/chat":
            self.send_error(404, "Endpoint introuvable")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 2_000_000:
                self.send_json(400, {"error": "Requête vide ou trop volumineuse."})
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            model = str(payload.get("model", "qwen3:8b"))[:120]
            incoming = payload.get("messages", [])
            if not isinstance(incoming, list) or not incoming:
                self.send_json(400, {"error": "Ajoute un message avant d'envoyer."})
                return
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for item in incoming[-40:]:
                if not isinstance(item, dict):
                    continue
                role = item.get("role")
                content = item.get("content")
                if role in ("user", "assistant") and isinstance(content, str) and content.strip():
                    messages.append({"role": role, "content": content[:100_000]})
            if len(messages) < 2 or messages[-1]["role"] != "user":
                self.send_json(400, {"error": "Le dernier message doit être un message utilisateur."})
                return

            body = json.dumps({
                "model": model,
                "messages": messages,
                "stream": True,
                "think": False,
                "options": {"temperature": 0.65, "num_ctx": 8192},
            }, ensure_ascii=False).encode("utf-8")
            req = Request(
                OLLAMA_BASE + "/api/chat",
                data=body,
                headers={"Content-Type": "application/json", "Accept": "application/x-ndjson"},
                method="POST",
            )
            try:
                upstream = urlopen(req, timeout=900)
            except HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:1000]
                self.send_json(502, {"error": "Ollama a renvoyé une erreur.", "detail": detail})
                return
            except URLError as exc:
                self.send_json(503, {"error": "Impossible de contacter Ollama sur cet ordinateur.", "detail": str(exc.reason)[:300]})
                return

            with upstream:
                self.send_response(200)
                self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Connection", "close")
                self.end_headers()
                try:
                    for line in upstream:
                        self.wfile.write(line)
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    pass
            self.close_connection = True
        except json.JSONDecodeError:
            self.send_json(400, {"error": "Le format de la requête est invalide."})
        except Exception as exc:
            try:
                self.send_json(500, {"error": "Erreur locale inattendue.", "detail": str(exc)[:400]})
            except Exception:
                pass


def main():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    httpd.daemon_threads = True
    url = f"http://{HOST}:{PORT}"
    print("=" * 58)
    print(" NOVA — IA LOCALE")
    print("=" * 58)
    print(f"Interface : {url}")
    print("Les requêtes restent sur cet ordinateur (127.0.0.1).")
    print("Garde cette fenêtre ouverte pendant l'utilisation.")
    print("Pour arrêter NOVA, ferme cette fenêtre ou appuie sur Ctrl+C.")
    print("=" * 58)
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print("\nArrêt de NOVA…")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    main()
