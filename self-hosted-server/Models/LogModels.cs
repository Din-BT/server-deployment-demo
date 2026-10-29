namespace SelfHostedServer.Models;

/// <summary>
/// Model đại diện cho một bản ghi log được gửi từ Client lên Server.
/// Được lưu trữ và phục vụ cho việc thống kê, kiểm tra gói tin trong môn NT106.
/// </summary>
public class NetworkLogItem
{
    /// <summary>
    /// Định danh duy nhất của bản ghi log (UUID)
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString("N");

    /// <summary>
    /// Thời điểm server nhận và ghi log (UTC ISO-8601)
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Địa chỉ IP của Client gửi yêu cầu (hữu ích để chứng minh kết nối mạng qua Internet / LAN)
    /// </summary>
    public string ClientIp { get; set; } = "Unknown";

    /// <summary>
    /// Tên hoặc mã thiết bị gửi log (ví dụ: "Client-WinForms-01", "Postman", "Tester-Vuong")
    /// </summary>
    public string DeviceId { get; set; } = "Anonymous-Device";

    /// <summary>
    /// Mức độ log: INFO, WARNING, ERROR, DEBUG
    /// </summary>
    public string Level { get; set; } = "INFO";

    /// <summary>
    /// Nội dung thông điệp log
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Kích thước dữ liệu payload (bytes) để phục vụ đo đạc băng thông mạng
    /// </summary>
    public long PayloadSizeBytes { get; set; } = 0;

    /// <summary>
    /// Dữ liệu bổ sung tùy chọn (Metadata dạng key-value)
    /// </summary>
    public Dictionary<string, string>? Metadata { get; set; }
}

/// <summary>
/// DTO (Data Transfer Object) nhận từ Client khi gọi POST /api/logs
/// </summary>
public class CreateLogRequest
{
    /// <summary>
    /// Mã thiết bị gửi (Tùy chọn, mặc định "Client-Default")
    /// </summary>
    public string? DeviceId { get; set; }

    /// <summary>
    /// Mức độ log: INFO, WARNING, ERROR, DEBUG (Tùy chọn, mặc định "INFO")
    /// </summary>
    public string? Level { get; set; }

    /// <summary>
    /// Nội dung thông điệp log cần ghi nhận (Bắt buộc)
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Dữ liệu phụ đính kèm (nếu có)
    /// </summary>
    public Dictionary<string, string>? Metadata { get; set; }
}

/// <summary>
/// Model phản hồi khi gọi GET /api/ping
/// </summary>
public class PingResponse
{
    public string Status { get; set; } = "healthy";
    public string Message { get; set; } = "pong";
    public DateTime ServerTimeUtc { get; set; } = DateTime.UtcNow;
    public double UptimeSeconds { get; set; }
    public string ServerPlatform { get; set; } = "ASP.NET Core (.NET 10.0)";
    public string EnvironmentName { get; set; } = "Production";
    public string ClientIp { get; set; } = string.Empty;
}

/// <summary>
/// Model thống kê hiệu năng Server phục vụ Ngày 3 (RAM, CPU, tổng request)
/// </summary>
public class ServerMetricsResponse
{
    public DateTime TimestampUtc { get; set; } = DateTime.UtcNow;
    public double UptimeSeconds { get; set; }
    public string UptimeFormatted { get; set; } = string.Empty;
    
    // Thống kê bộ nhớ RAM
    public double MemoryWorkingSetMB { get; set; }
    public double MemoryAllocatedMB { get; set; }

    // Thống kê CPU & Luồng
    public int ThreadCount { get; set; }
    public double TotalProcessorTimeSeconds { get; set; }

    // Thống kê lượng Request mạng đã tiếp nhận
    public long TotalRequestsReceived { get; set; }
    public long TotalPingRequests { get; set; }
    public long TotalLogPostRequests { get; set; }
    public long TotalStoredLogsCount { get; set; }

    // Thông tin nền tảng
    public string OperatingSystem { get; set; } = string.Empty;
    public string DotnetVersion { get; set; } = string.Empty;
    public int ProcessorCount { get; set; }
}
