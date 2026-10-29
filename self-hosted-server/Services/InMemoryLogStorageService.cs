using System.Collections.Concurrent;
using System.Diagnostics;
using System.Runtime.InteropServices;
using SelfHostedServer.Models;

namespace SelfHostedServer.Services;

/// <summary>
/// Interface định nghĩa các nghiệp vụ lưu trữ log và thu thập chỉ số hiệu năng
/// </summary>
public interface ILogStorageService
{
    /// <summary>
    /// Thêm một log mới vào kho lưu trữ
    /// </summary>
    NetworkLogItem AddLog(CreateLogRequest request, string clientIp, long payloadBytes);

    /// <summary>
    /// Lấy danh sách log đã lưu với bộ lọc và giới hạn số lượng
    /// </summary>
    IEnumerable<NetworkLogItem> GetLogs(int limit = 50, string? level = null, string? deviceId = null);

    /// <summary>
    /// Đếm tổng số log hiện đang lưu
    /// </summary>
    int GetLogCount();

    /// <summary>
    /// Xóa toàn bộ log hiện có (phục vụ reset trước khi test tải)
    /// </summary>
    void ClearLogs();

    /// <summary>
    /// Ghi nhận 1 request ping thành công
    /// </summary>
    void RecordPingRequest();

    /// <summary>
    /// Thu thập chỉ số hiệu năng thực tế của hệ điều hành và tiến trình server (RAM, CPU, Uptime)
    /// </summary>
    ServerMetricsResponse GetServerMetrics();

    /// <summary>
    /// Lấy thời gian server đã chạy liên tục tính bằng giây
    /// </summary>
    double GetUptimeSeconds();
}

/// <summary>
/// Triển khai dịch vụ lưu trữ log trong bộ nhớ RAM (In-Memory Thread-Safe).
/// Không cần cấu hình cơ sở dữ liệu cồng kềnh, tốc độ xử lý cực cao,
/// rất lý tưởng để demo và đo lường độ trễ mạng trong môn Lập trình mạng căn bản NT106.
/// </summary>
public class InMemoryLogStorageService : ILogStorageService
{
    private readonly ConcurrentQueue<NetworkLogItem> _logs = new();
    private readonly int _maxCapacity;
    private readonly DateTime _startTimeUtc = DateTime.UtcNow;

    // Các bộ đếm nguyên tử (Atomic Counters) để đo đạc tải chính xác
    private long _totalRequestsCount = 0;
    private long _totalPingCount = 0;
    private long _totalLogPostCount = 0;

    public InMemoryLogStorageService(int maxCapacity = 1000)
    {
        _maxCapacity = maxCapacity;
    }

    public NetworkLogItem AddLog(CreateLogRequest request, string clientIp, long payloadBytes)
    {
        Interlocked.Increment(ref _totalRequestsCount);
        Interlocked.Increment(ref _totalLogPostCount);

        var logItem = new NetworkLogItem
        {
            Id = Guid.NewGuid().ToString("N"),
            Timestamp = DateTime.UtcNow,
            ClientIp = clientIp,
            DeviceId = string.IsNullOrWhiteSpace(request.DeviceId) ? "Device-" + clientIp : request.DeviceId.Trim(),
            Level = string.IsNullOrWhiteSpace(request.Level) ? "INFO" : request.Level.Trim().ToUpperInvariant(),
            Message = request.Message ?? string.Empty,
            PayloadSizeBytes = payloadBytes,
            Metadata = request.Metadata
        };

        _logs.Enqueue(logItem);

        // Giữ kích thước hàng đợi trong giới hạn an toàn để không tràn RAM của Server Free-Tier
        while (_logs.Count > _maxCapacity && _logs.TryDequeue(out _))
        {
            // Bỏ bớt log cũ nhất khi vượt ngưỡng
        }

        return logItem;
    }

    public IEnumerable<NetworkLogItem> GetLogs(int limit = 50, string? level = null, string? deviceId = null)
    {
        Interlocked.Increment(ref _totalRequestsCount);

        IEnumerable<NetworkLogItem> query = _logs.ToArray().Reverse(); // Log mới nhất xếp trước

        if (!string.IsNullOrWhiteSpace(level))
        {
            query = query.Where(l => string.Equals(l.Level, level.Trim(), StringComparison.OrdinalIgnoreCase));
        }

        if (!string.IsNullOrWhiteSpace(deviceId))
        {
            query = query.Where(l => l.DeviceId.Contains(deviceId.Trim(), StringComparison.OrdinalIgnoreCase));
        }

        return query.Take(Math.Clamp(limit, 1, 500));
    }

    public int GetLogCount() => _logs.Count;

    public void ClearLogs()
    {
        _logs.Clear();
    }

    public void RecordPingRequest()
    {
        Interlocked.Increment(ref _totalRequestsCount);
        Interlocked.Increment(ref _totalPingCount);
    }

    public double GetUptimeSeconds()
    {
        return (DateTime.UtcNow - _startTimeUtc).TotalSeconds;
    }

    public ServerMetricsResponse GetServerMetrics()
    {
        Interlocked.Increment(ref _totalRequestsCount);

        var uptime = DateTime.UtcNow - _startTimeUtc;
        var process = Process.GetCurrentProcess();

        // Đo đạc RAM thực tế của tiến trình server (Working Set MB)
        double workingSetMB = Math.Round(process.WorkingSet64 / (1024.0 * 1024.0), 2);
        double allocatedMB = Math.Round(GC.GetTotalMemory(forceFullCollection: false) / (1024.0 * 1024.0), 2);

        // Đo đạc thời gian CPU tiêu thụ
        double cpuTimeSeconds = Math.Round(process.TotalProcessorTime.TotalSeconds, 2);

        return new ServerMetricsResponse
        {
            TimestampUtc = DateTime.UtcNow,
            UptimeSeconds = Math.Round(uptime.TotalSeconds, 1),
            UptimeFormatted = $"{uptime.Days}d {uptime.Hours:D2}h:{uptime.Minutes:D2}m:{uptime.Seconds:D2}s",
            MemoryWorkingSetMB = workingSetMB,
            MemoryAllocatedMB = allocatedMB,
            ThreadCount = process.Threads.Count,
            TotalProcessorTimeSeconds = cpuTimeSeconds,
            TotalRequestsReceived = Interlocked.Read(ref _totalRequestsCount),
            TotalPingRequests = Interlocked.Read(ref _totalPingCount),
            TotalLogPostRequests = Interlocked.Read(ref _totalLogPostCount),
            TotalStoredLogsCount = _logs.Count,
            OperatingSystem = RuntimeInformation.OSDescription,
            DotnetVersion = RuntimeInformation.FrameworkDescription,
            ProcessorCount = Environment.ProcessorCount
        };
    }
}
