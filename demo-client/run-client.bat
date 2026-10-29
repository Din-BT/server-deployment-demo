@echo off
title NT106 Client Demo Runner
echo =========================================================
echo  [NT106] DANG KHOI DONG CLIENT DEMO & DO LUONG (PORT 8080)
echo =========================================================
cd /d "%~dp0"
python serve.py
pause

