@echo off
title NT106 Public Tunnel Runner
echo =========================================================
echo  [NT106] KHOI TAO PUBLIC TUNNEL CHO DEMO
echo =========================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\start-tunnel.ps1"
pause
