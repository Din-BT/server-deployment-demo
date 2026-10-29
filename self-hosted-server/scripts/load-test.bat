@echo off
title NT106 Load Testing Tool
echo =========================================================
echo  [NT106] CHAY TEST TAI VA DO LUONG HIEU NANG
echo =========================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\load-test.ps1" -BaseUrl "http://localhost:5000" -Count 50 -Type "both"
pause
