# =========================================================================
# SCRIPT TEST TẢI VÀ THỐNG KÊ HIỆU NĂNG SERVER (PHỤC VỤ NHIỆM VỤ NGÀY 3)
# - Test 50 - 100 requests (hoặc tùy chọn)
# - Đo Latency: Min, Max, Average (ms)
# - Thống kê RAM/CPU tiêu thụ thực tế
# =========================================================================

param(
    [string]$BaseUrl = "http://localhost:5000",
    [int]$Count = 50,
    [ValidateSet("ping", "logs", "both")]
    [string]$Type = "both"
)

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " [NT106] TEST TAI VA DO LUONG HIEU NANG SELF-HOSTED API   " -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Target Server URL: $BaseUrl" -ForegroundColor White
Write-Host "Tong so Request:   $Count requests" -ForegroundColor White
Write-Host "Loai Request:      $Type" -ForegroundColor White
Write-Host "Thoi gian bat dau: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "---------------------------------------------------------" -ForegroundColor DarkGray

# 1. Thu thập chỉ số Server TRƯỚC KHI TEST TẢI
$metricsBefore = $null
try {
    $metricsBefore = Invoke-RestMethod -Uri "$BaseUrl/api/metrics" -Method Get -TimeoutSec 10
    Write-Host "[TRUOC TEST] RAM tieu thu: $($metricsBefore.memoryWorkingSetMB) MB | Luong: $($metricsBefore.threadCount) | CPU Time: $($metricsBefore.totalProcessorTimeSeconds)s" -ForegroundColor Cyan
} catch {
    Write-Host "[CANH BAO] Khong the doc metrics truoc khi test tai (co the server chua chay): $_" -ForegroundColor Yellow
}

$latencies = New-Object System.Collections.Generic.List[double]
$successCount = 0
$failCount = 0

$totalStopwatch = [System.Diagnostics.Stopwatch]::StartNew()

# 2. Vòng lặp gửi Request
for ($i = 1; $i -le $Count; $i++) {
    $reqStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $isSuccess = $false

    try {
        if ($Type -eq "ping" -or ($Type -eq "both" -and ($i % 2 -eq 1))) {
            # Gửi GET /api/ping
            $res = Invoke-RestMethod -Uri "$BaseUrl/api/ping" -Method Get -TimeoutSec 10
            $isSuccess = $true
        } else {
            # Gửi POST /api/logs
            $body = @{
                deviceId = "TestRunner-TV3"
                level = "INFO"
                message = "Load testing packet seq_#$i"
                metadata = @{ testBatch = "Day3-LoadTest"; seq = "$i" }
            } | ConvertTo-Json

            $res = Invoke-RestMethod -Uri "$BaseUrl/api/logs" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
            $isSuccess = $true
        }
    } catch {
        $isSuccess = $false
    }

    $reqStopwatch.Stop()
    $elapsedMs = [Math]::Round($reqStopwatch.Elapsed.TotalMilliseconds, 2)
    $latencies.Add($elapsedMs)

    if ($isSuccess) {
        $successCount++
        if ($i % 10 -eq 0 -or $i -eq $Count) {
            Write-Host "  -> Request [$i/$Count]: OK | Latency: $($elapsedMs)ms" -ForegroundColor Green
        }
    } else {
        $failCount++
        Write-Host "  -> Request [$i/$Count]: FAILED" -ForegroundColor Red
    }
}

$totalStopwatch.Stop()
$totalElapsedSec = [Math]::Round($totalStopwatch.Elapsed.TotalSeconds, 2)

# 3. Thu thập chỉ số Server SAU KHI TEST TẢI
$metricsAfter = $null
try {
    $metricsAfter = Invoke-RestMethod -Uri "$BaseUrl/api/metrics" -Method Get -TimeoutSec 10
} catch { }

# 4. Tính toán số liệu thống kê Latency
$minLatency = ($latencies | Measure-Object -Minimum).Minimum
$maxLatency = ($latencies | Measure-Object -Maximum).Maximum
$avgLatency = [Math]::Round(($latencies | Measure-Object -Average).Average, 2)
$sortedLatencies = $latencies | Sort-Object
$p95Index = [int][Math]::Floor($sortedLatencies.Count * 0.95)
$p95Latency = if ($p95Index -lt $sortedLatencies.Count) { $sortedLatencies[$p95Index] } else { $maxLatency }
$rps = [Math]::Round($Count / [Math]::Max($totalElapsedSec, 0.001), 1)
$successPercent = [Math]::Round(($successCount / [Math]::Max($Count, 1)) * 100, 1)

# 5. In bảng tổng kết dữ liệu
Write-Host "=========================================================" -ForegroundColor Yellow
Write-Host "           BANG TONG KET KET QUA DO DAC HIEU NANG        " -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Yellow
Write-Host "1. KET QUA TRUYEN GOI TIN:" -ForegroundColor Cyan
Write-Host "   - Tong goi tin da gui:    $Count"
Write-Host "   - Gui thanh cong (200):   $successCount ($successPercent%)"
Write-Host "   - Goi tin that bai:       $failCount"
Write-Host "   - Tong thoi gian test:    $totalElapsedSec giay"
Write-Host "   - Toc do xu ly (RPS):     $rps req/giay"
Write-Host ""
Write-Host "2. DO TRE MANG (LATENCY ROUND-TRIP):" -ForegroundColor Cyan
Write-Host "   - Do tre toi thieu (Min): $minLatency ms"
Write-Host "   - Do tre trung binh (Avg):$avgLatency ms"
Write-Host "   - Do tre toi da (Max):    $maxLatency ms"
Write-Host "   - Phan vi 95% (P95):      $p95Latency ms"
Write-Host ""

if ($metricsBefore -ne $null -and $metricsAfter -ne $null) {
    $ramDiff = [Math]::Round($metricsAfter.memoryWorkingSetMB - $metricsBefore.memoryWorkingSetMB, 2)
    $cpuDiff = [Math]::Round($metricsAfter.totalProcessorTimeSeconds - $metricsBefore.totalProcessorTimeSeconds, 2)

    Write-Host "3. TAI NGUYEN TIEU THU (TASK NGAY 3 CUA VIN):" -ForegroundColor Cyan
    Write-Host "   - RAM truoc test:         $($metricsBefore.memoryWorkingSetMB) MB"
    Write-Host "   - RAM sau test:           $($metricsAfter.memoryWorkingSetMB) MB (Chenh lech: +$ramDiff MB)"
    Write-Host "   - CPU Processor Time:     $($metricsAfter.totalProcessorTimeSeconds) s (Tang: +$cpuDiff s)"
    Write-Host "   - Tong log dang luu tru:  $($metricsAfter.totalStoredLogsCount) ban ghi"
}

Write-Host "=========================================================" -ForegroundColor Yellow
Write-Host "[HOAN TAT] Ban va TV3 hay copy bang so lieu tren de dien vao Slide!" -ForegroundColor Green
