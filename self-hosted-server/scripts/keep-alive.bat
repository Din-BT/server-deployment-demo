@echo off
title NT106 Anti-Sleep Keep Alive Bot
echo =========================================================
echo  [NT106] BOT CHONG SLEEP SERVER RENDER (TASK NGAY 4)
echo =========================================================
set /p SERVER_URL="Nhap URL server (Enter de mac dinh http://localhost:5000): "
if "%SERVER_URL%"=="" set SERVER_URL=http://localhost:5000

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\keep-alive.ps1" -ServerUrl "%SERVER_URL%" -IntervalMinutes 10
pause
