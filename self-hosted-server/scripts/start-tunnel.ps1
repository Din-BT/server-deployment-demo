# =========================================================================
# SCRIPT KẾT NỐI TUNNEL DỰ PHÒNG (NGROK / CLOUDFLARE TUNNEL)
# Phục vụ: Nhiệm vụ Ngày 2 & Ngày 4 - Chuẩn bị tunnel dự phòng cho buổi Demo
# =========================================================================

param(
    [int]$Port = 5000,
    [string]$TunnelType = "auto"
)

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " [NT106] KHOI TAO PUBLIC TUNNEL DU PHONG CHO DEMO       " -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Port local server: $Port" -ForegroundColor Gray

# 1. Kiem tra ngrok
$hasNgrok = (Get-Command ngrok -ErrorAction SilentlyContinue) -ne $null

# 2. Kiem tra cloudflared
$hasCloudflared = (Get-Command cloudflared -ErrorAction SilentlyContinue) -ne $null

if ($hasNgrok) {
    Write-Host "[OK] Tim thay ngrok trong he thong! Dang mo tunnel qua ngrok..." -ForegroundColor Green
    Write-Host "Lenh thuc thi: ngrok http $Port" -ForegroundColor DarkGray
    ngrok http $Port
}
elseif ($hasCloudflared) {
    Write-Host "[OK] Tim thay Cloudflare Tunnel (cloudflared)! Dang mo quick tunnel..." -ForegroundColor Green
    Write-Host "Lenh thuc thi: cloudflared tunnel --url http://localhost:$Port" -ForegroundColor DarkGray
    cloudflared tunnel --url "http://localhost:$Port"
}
else {
    Write-Host "[CHU Y] Chua tim thay 'ngrok' hoac 'cloudflared' trong PATH he thong." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Cac cach kich hoat tunnel du phong cuc ky de dang:" -ForegroundColor Cyan
    Write-Host "  Cach 1 (Khuyen nghi): Dung Cloudflare Tunnel (Mien phi 100%, khong can tao tai khoan)" -ForegroundColor White
    Write-Host "     1. Tai file cloudflared.exe tu: https://github.com/cloudflare/cloudflared/releases/latest" -ForegroundColor Gray
    Write-Host "     2. Chay lenh: .\cloudflared.exe tunnel --url http://localhost:$Port" -ForegroundColor Gray
    Write-Host "     3. Cloudflare se cap ngay 1 duong link https://xxx.trycloudflare.com ra internet." -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Cach 2: Dung ngrok" -ForegroundColor White
    Write-Host "     1. Tai ngrok tu https://ngrok.com/download" -ForegroundColor Gray
    Write-Host "     2. Chay lenh: ngrok http $Port" -ForegroundColor Gray
    Write-Host "     3. Copy link Forwarding (https://xxx.ngrok-free.app) gui cho TV3." -ForegroundColor Gray
    Write-Host "=========================================================" -ForegroundColor Cyan
}
