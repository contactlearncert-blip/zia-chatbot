@echo off
set /p GITHUB_USER="Entrez votre nom d'utilisateur GitHub : "

git init
git add .
git commit -m "Initial commit: Zia chatbot"

git remote remove origin 2>nul
git remote add origin https://github.com/contactlearncert-blip/zia-chatbot.git

git push -u origin main

echo.
echo ✅ Projet poussé sur https://github.com/contactlearncert-blip/zia-chatbot
echo.
pause