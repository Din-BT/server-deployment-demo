# =========================================================================
# SCRIPT CHẠY SERVER LOCAL (DỰ PHÒNG KHI DEMO TRƯỚC LỚP)
# =========================================================================

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " [NT106] DANG KHOI DONG SELF-HOSTED SERVER (LOCAL)       " -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Cyan

$CurrentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $CurrentDir

Set-Location $ProjectDir

Write-Host "Thu muc du an: $ProjectDir" -ForegroundColor Gray
Write-Host "Dang lang nghe tren: http://localhost:5000" -ForegroundColor Green
Write-Host "Swagger UI: http://localhost:5000/swagger" -ForegroundColor Green
Write-Host "Bam Ctrl + C de dung server." -ForegroundColor Yellow
Write-Host "---------------------------------------------------------" -ForegroundColor DarkGray

dotnet run
