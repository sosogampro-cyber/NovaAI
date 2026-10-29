@echo off
chcp 65001 >nul
cd /d "%~dp0"
title NOVA - Installation et demarrage
color 0B
echo.
echo  ==================================================
echo       NOVA - IA LOCALE POUR WINDOWS
echo  ==================================================
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo [ERREUR] Python n'est pas installe.
  start "" "https://www.python.org/downloads/windows/"
  echo Installe Python 3, coche "Add python.exe to PATH" si propose, puis relance ce fichier.
  pause
  exit /b 1
)
py -3 --version
where ollama >nul 2>nul
if errorlevel 1 (
  echo.
  echo Ollama est necessaire comme moteur local, mais tu n'auras pas besoin d'ouvrir son application.
  echo NOVA le demarrera automatiquement en arriere-plan lors des prochains lancements.
  start "" "https://ollama.com/download/windows"
  echo Installe Ollama, puis relance ce fichier.
  pause
  exit /b 1
)
REM Demarre le serveur Ollama en arriere-plan si besoin.
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
if errorlevel 1 (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath (Get-Command ollama).Source -ArgumentList 'serve' -WindowStyle Hidden"
  timeout /t 3 /nobreak >nul
)
echo.
echo Etape 1/2 : verification du modele Qwen3 8B.
echo Si le modele manque, environ 5 Go seront telecharges une seule fois.
ollama list | findstr /i "qwen3:8b" >nul
if errorlevel 1 ollama pull qwen3:8b
if errorlevel 1 (
  echo [ERREUR] Le modele n'a pas pu etre telecharge. Verifie ta connexion Internet.
  pause
  exit /b 1
)
echo.
echo Etape 2/2 : lancement de NOVA. Tu n'as plus besoin d'ouvrir Ollama manuellement.
echo Pour creer des images, installe le moteur avec INSTALLER_IMAGES.bat.
echo.
py -3 app.py
if errorlevel 1 pause
