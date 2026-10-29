@echo off
chcp 65001 >nul
color 0B
title NOVA - Installer le moteur d'images
cls
echo ==================================================
echo       NOVA - INSTALLER LE MOTEUR D'IMAGES
echo ==================================================
echo.
echo NOVA utilise ComfyUI pour generer des images sur ce PC.
echo Le telechargement de ComfyUI et d'un modele d'image prend plusieurs Go.
echo.
echo 1. Le site officiel va s'ouvrir.
echo 2. Installe ComfyUI pour Windows.
echo 3. Installe un checkpoint compatible SD 1.5 ou SDXL dans models\checkpoints.
echo 4. Demarre ComfyUI, puis lance NOVA et clique sur Creer une image.
echo.
start "" "https://www.comfy.org/download"
echo Guide complet : GUIDE.txt, section CREATION D'IMAGES.
echo.
pause
