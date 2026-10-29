# =========================================================================
# SCRIPT GIỮ SERVER KHÔNG BỊ SLEEP TRÊN RENDER FREE TIER (TASK NGÀY 4)
# Định kỳ mỗi 10 phút gửi 1 GET /health để Render luôn ở trạng thái Active
# =========================================================================

param(
    [string]$ServerUrl = "http://localhost:5000",
    [int]$IntervalMinutes = 10
)

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " [NT106] ANTI-SLEEP KEEP-ALIVE BOT CHO RENDER / CLOUD    " -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Server URL:        $ServerUrl" -ForegroundColor White
Write-Host "Chu ky Ping:       Moi $IntervalMinutes phut" -ForegroundColor White
Write-Host "Bam Ctrl + C de dung script." -ForegroundColor Yellow
Write-Host "---------------------------------------------------------" -ForegroundColor DarkGray

$counter = 0

while ($true) {
    $counter++
    $timeStr = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $res = Invoke-RestMethod -Uri "$ServerUrl/health" -Method Get -TimeoutSec 15
        $sw.Stop()
        Write-Host "[$timeStr] [#$counter] Ping thanh cong -> Latency: $([Math]::Round($sw.Elapsed.TotalMilliseconds, 1))ms | Status: $($res.status)" -ForegroundColor Green
    }
    catch {
        Write-Host "[$timeStr] [#$counter] Ping that bai (Server co the dang khoi dong hoac loi mang): $_" -ForegroundColor Red
    }

    Start-Sleep -Seconds ($IntervalMinutes * 60)
}
