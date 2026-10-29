@echo off
title NT106 Performance Measurement Tool
echo =========================================================
echo  [NT106] CHAY BENCHMARK DO LUONG HIEU NANG SERVER (TV3)
echo =========================================================
cd /d "%~dp0"
python measure.py --self-url "http://127.0.0.1:5000" -n 50
pause

