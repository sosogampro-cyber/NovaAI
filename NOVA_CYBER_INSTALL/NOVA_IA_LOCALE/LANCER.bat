@echo off
chcp 65001 >nul
cd /d "%~dp0"
title NOVA - IA locale
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3 est introuvable. Lance INSTALLER_ET_DEMARRER.bat une premiere fois.
  pause
  exit /b 1
)
where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama doit etre installe une seule fois pour faire tourner le modele local.
  echo Tu n'auras ensuite pas besoin d'ouvrir son application : NOVA le demarrera en arriere-plan.
  start "" "https://ollama.com/download/windows"
  pause
  exit /b 1
)
REM Si le serveur Ollama ne repond pas, demarre-le discretement en arriere-plan.
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
if errorlevel 1 (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath (Get-Command ollama).Source -ArgumentList 'serve' -WindowStyle Hidden"
  set /a tries=0
  :waitollama
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
  if not errorlevel 1 goto ready
  set /a tries+=1
  if %tries% GEQ 20 (
    echo NOVA n'arrive pas a demarrer son moteur local. Verifie qu'Ollama est installe.
    pause
    exit /b 1
  )
  timeout /t 1 /nobreak >nul
  goto waitollama
)
:ready
py -3 app.py
if errorlevel 1 pause
