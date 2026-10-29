# ⚡ NOVA IA CYBER — GUIDE OFFICIEL

## 🤖 Présentation de NOVA

Bienvenue dans **NOVA IA CYBER**, ton intelligence artificielle personnelle conçue pour fonctionner localement sur ton ordinateur Windows.

NOVA possède une interface futuriste de style cyberpunk, avec un thème sombre, des néons bleus et verts, et deux fonctions principales : discuter avec une intelligence artificielle et créer des images à partir de descriptions textuelles.

### 💬 1. Utiliser le chat IA

Le chat te permet de poser des questions, demander des explications, créer du code, obtenir de l'aide pour tes projets et discuter avec NOVA en français.

**Comment l'utiliser :**
1. Ouvre NOVA avec le fichier `LANCER.bat`.
2. Attends que l'interface s'ouvre dans ton navigateur.
3. Écris ta question dans la zone de message.
4. Appuie sur Entrée ou clique sur le bouton d'envoi.
5. Lis la réponse de NOVA et poursuis la conversation.

Le moteur de texte utilisé est Ollama, avec le modèle Qwen3 8B.

### 🎨 2. Créer des images avec NOVA

NOVA possède un studio de création d'images qui permet de générer des images à partir de descriptions.

**Comment créer une image :**
1. Démarre ComfyUI et attends qu'il soit prêt.
2. Ouvre NOVA.
3. Accède à la section « Créer une image ».
4. Décris précisément l'image souhaitée. Exemple : « Un robot cyberpunk bleu et vert dans une ville futuriste, éclairage néon, détails réalistes ».
5. Choisis un modèle disponible, une résolution et un nombre d'étapes.
6. Clique sur « Générer l'image ».
7. Consulte le résultat dans la galerie et enregistre ta création.

Les images générées sont enregistrées dans le dossier `generated_images` situé à côté du fichier `app.py`.

Pour créer des images, ComfyUI doit être démarré et un modèle compatible doit être installé. NOVA utilise notamment des modèles de type Stable Diffusion 1.5 ou SDXL.

## 🛠️ 3. Installer les applications nécessaires

### Application 1 — Python

**Rôle :** Python permet de démarrer le serveur local de NOVA.

Lien officiel : https://www.python.org/downloads/windows/

Installation :
1. Télécharge la version de Python pour Windows.
2. Lance l'installateur.
3. Termine l'installation.
4. Si l'option « Add Python to PATH » est proposée, coche-la.
5. Relance l'installation de NOVA.

### Application 2 — Ollama

**Rôle :** Ollama fait fonctionner le modèle d'intelligence artificielle qui répond à tes messages.

Lien officiel : https://ollama.com/download/windows

Installation :
1. Télécharge Ollama pour Windows.
2. Ouvre le fichier d'installation.
3. Suis les instructions à l'écran.
4. Laisse Ollama démarrer en arrière-plan.
5. Double-clique sur `INSTALLER_ET_DEMARRER.bat` dans le dossier NOVA.

Le programme téléchargera le modèle Qwen3 8B, qui nécessite plusieurs gigaoctets d'espace disque et une connexion Internet lors du premier téléchargement.

Il n'est pas nécessaire d'utiliser manuellement le chat d'Ollama pour discuter dans NOVA.

### Application 3 — ComfyUI

**Rôle :** ComfyUI est le moteur local chargé de générer les images.

Lien officiel : https://www.comfy.org/download

Installation :
1. Télécharge ComfyUI depuis le site officiel.
2. Installe l'application en suivant les instructions.
3. Lance ComfyUI et attends son démarrage complet.
4. Installe un modèle de génération compatible avec le workflow de NOVA.
5. Vérifie que ComfyUI est accessible à l'adresse locale suivante : http://127.0.0.1:8188
6. Laisse ComfyUI ouvert pendant la génération des images.

Pour les installations classiques de ComfyUI, les modèles checkpoint compatibles se placent généralement dans le dossier `ComfyUI/models/checkpoints`. Avec d'autres installations, notamment ComfyUI Desktop, l'emplacement peut varier.

Documentation officielle : https://docs.comfy.org/

## 🚀 4. Démarrer NOVA

Après avoir installé les applications nécessaires :

1. Extrais tous les fichiers de l'archive ZIP dans un dossier.
2. Ouvre le dossier `NOVA_IA_LOCALE`.
3. Pour la première installation, double-clique sur `INSTALLER_ET_DEMARRER.bat`.
4. Attends le téléchargement du modèle et le démarrage du programme.
5. Pour les utilisations suivantes, double-clique sur `LANCER.bat`.
6. L'interface s'ouvre normalement dans ton navigateur à l'adresse http://127.0.0.1:8765.

Garde la fenêtre noire de NOVA ouverte pendant son utilisation. Pour créer des images, garde également ComfyUI ouvert.

## 🔧 5. Résoudre les problèmes fréquents

**NOVA ne répond pas :**
Vérifie qu'Ollama est installé, démarré et que le modèle Qwen3 8B est téléchargé.

**Le chat affiche une erreur de connexion :**
Vérifie qu'Ollama fonctionne et que son service local est accessible.

**La création d'images affiche « ComfyUI non démarré » :**
Démarre ComfyUI et vérifie l'adresse http://127.0.0.1:8188.

**Aucun modèle d'image n'apparaît :**
Installe un modèle checkpoint compatible, vérifie son dossier et redémarre ComfyUI.

**La génération est trop lente :**
Essaie une image de 512 × 512 pixels avec 8 étapes de génération.

**L'installation ne fonctionne pas :**
Vérifie que Python et Ollama sont correctement installés, que les fichiers ZIP ont été extraits et que ta connexion Internet fonctionne pendant la configuration initiale.

## 🔒 6. Confidentialité et fonctionnement local

NOVA est conçu pour utiliser les moteurs locaux installés sur ton ordinateur. Les conversations avec le modèle de texte passent par Ollama en local, tandis que les demandes d'images passent par ComfyUI en local.

Une connexion Internet reste nécessaire pour télécharger les applications et les modèles. Une fois les ressources nécessaires installées, les fonctions locales peuvent être utilisées hors ligne.

Les performances dépendent du processeur, de la mémoire vive, de la carte graphique et des modèles choisis.

## 🌐 7. Liens utiles

- **NOVA :** utiliser les fichiers fournis dans le dossier de l'application.
- **Python :** https://www.python.org/downloads/windows/
- **Ollama :** https://ollama.com/download/windows
- **ComfyUI :** https://www.comfy.org/download
- **Documentation ComfyUI :** https://docs.comfy.org/
- **Dépôt officiel ComfyUI :** https://github.com/Comfy-Org/ComfyUI

**NOVA IA CYBER — Ton intelligence artificielle, ton ordinateur, tes créations.**
