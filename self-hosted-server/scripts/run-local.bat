@echo off
title NT106 Self-Hosted Server Local Runner
echo =========================================================
echo  [NT106] DANG KHOI DONG SELF-HOSTED SERVER (LOCAL)
echo =========================================================
cd /d "%~dp0\.."
echo Dang lang nghe tai: http://localhost:5000
echo Swagger UI: http://localhost:5000/swagger
echo.
dotnet run
pause
