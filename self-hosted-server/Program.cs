using System.Diagnostics;
using Microsoft.OpenApi;
using Scalar.AspNetCore;
using SelfHostedServer.Models;
using SelfHostedServer.Services;

var builder = WebApplication.CreateBuilder(args);

// =========================================================================================
// 1. CẤU HÌNH PORT VÀ ĐỊA CHỈ LẮNG NGHE (PHỤC VỤ DEPLOY RENDER / RAILWAY / CLOUD DOCKER)
// =========================================================================================
// Trên Render, Railway hoặc VPS Docker, nền tảng sẽ cung cấp biến môi trường PORT (ví dụ PORT=10000 hoặc 8080).
// Ta đọc biến PORT này để bind vào 0.0.0.0:PORT. Nếu chạy local thì mặc định là cổng 5000.
var assignedPort = Environment.GetEnvironmentVariable("PORT") ?? "5000";
builder.WebHost.UseUrls($"http://0.0.0.0:{assignedPort}");

// =========================================================================================
// 2. ĐĂNG KÝ CÁC DỊCH VỤ (DEPENDENCY INJECTION)
// =========================================================================================
// Đăng ký dịch vụ lưu trữ log trong bộ nhớ (In-Memory Singleton) để giữ log xuyên suốt phiên chạy
builder.Services.AddSingleton<ILogStorageService, InMemoryLogStorageService>();

// Cấu hình CORS: Cho phép mọi domain, method, header truy cập.
// Điều này cực kỳ quan trọng để Thành viên 3 (Client WinForms / Web / Postman) gọi API không bị chặn CORS.
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAllPolicy", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Cấu hình OpenAPI & Swagger Documentation
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddOpenApi();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "NT106 - Self-Hosted Web API (Nhóm Demo)",
        Version = "v1",
        Description = "Web API tự triển khai (Self-Hosted) cho đồ án NT106 - Lập trình mạng căn bản (UIT).\n" +
                      "- Mục đích: So sánh với mô hình BaaS (Supabase).\n" +
                      "- Thành viên phụ trách Tự Deploy: Vin (TV1).\n" +
                      "- Hỗ trợ kiểm thử độ trễ, kích thước gói tin, và giám sát RAM/CPU.",
        Contact = new OpenApiContact
        {
            Name = "Bui Thanh Vin",
            Email = "thanhvin2007@gmail.com"
        }
    });
});

var app = builder.Build();

// =========================================================================================
// 3. CẤU HÌNH HTTP REQUEST PIPELINE & MIDDLEWARE
// =========================================================================================

// Kích hoạt CORS trước khi tiếp nhận request
app.UseCors("AllowAllPolicy");

// Kích hoạt Swagger UI trên CẢ Development LẪN Production.
// LÝ DO: Khi deploy lên Render/Railway, môi trường chạy là Production.
// Nếu chỉ bật ở Development thì link demo công khai sẽ bị lỗi 404 khi vào /swagger!
app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "Self-Hosted API v1");
    c.RoutePrefix = "swagger"; // Truy cập tại /swagger
    c.DocumentTitle = "NT106 - Self-Hosted API Swagger UI";
});

// Kích hoạt Scalar UI hiện đại tại /scalar/v1
app.MapOpenApi();
app.MapScalarApiReference();

// MIDDLEWARE GHI NHẬN LOG MẠNG VÀ THỜI GIAN PHẢN HỒI (LATENCY)
// Giúp console của server in ra rõ ràng từng request đến để phục vụ trình chiếu Demo phút 3 trước lớp
app.Use(async (context, next) =>
{
    var stopwatch = Stopwatch.StartNew();
    var clientIp = context.Connection.RemoteIpAddress?.ToString() ?? "Unknown";

    // Ghi nhận header X-Forwarded-For nếu đi qua Proxy của Render / Railway / ngrok
    if (context.Request.Headers.TryGetValue("X-Forwarded-For", out var forwardedFor))
    {
        clientIp = forwardedFor.ToString().Split(',')[0].Trim();
    }

    // Cho phép đọc lại Body nhiều lần nếu cần
    context.Request.EnableBuffering();

    await next(context);

    stopwatch.Stop();

    // In log ra Console với màu sắc trực quan
    var method = context.Request.Method;
    var path = context.Request.Path;
    var statusCode = context.Response.StatusCode;
    var elapsedMs = stopwatch.Elapsed.TotalMilliseconds;

    var logColor = statusCode switch
    {
        >= 200 and < 300 => ConsoleColor.Green,
        >= 400 and < 500 => ConsoleColor.Yellow,
        >= 500 => ConsoleColor.Red,
        _ => ConsoleColor.Cyan
    };

    var originalColor = Console.ForegroundColor;
    Console.ForegroundColor = ConsoleColor.DarkGray;
    Console.Write($"[{DateTime.UtcNow:HH:mm:ss.fff}] ");
    Console.ForegroundColor = logColor;
    Console.Write($"[{method} {path}] -> {statusCode} ");
    Console.ForegroundColor = ConsoleColor.White;
    Console.WriteLine($"({elapsedMs:F1}ms) - IP: {clientIp}");
    Console.ForegroundColor = originalColor;
});

// =========================================================================================
// 4. ĐỊNH NGHĨA CÁC ENDPOINT API (THEO YÊU CẦU ĐỒ ÁN)
// =========================================================================================

/// <summary>
/// Root endpoint: Điều hướng tự động về Swagger UI để giáo viên và bạn bè mở link là thấy ngay giao diện test
/// </summary>
app.MapGet("/", () => Results.Redirect("/swagger"))
   .ExcludeFromDescription();

/// <summary>
/// Health Check nhanh (phục vụ UptimeRobot chống server sleep trên Render Free Tier)
/// </summary>
app.MapGet("/health", () => Results.Ok(new { status = "healthy", timestamp = DateTime.UtcNow }))
   .WithName("HealthCheck")
   .WithTags("Health");

/// <summary>
/// ENDPOINT 1: GET /api/ping
/// Nhiệm vụ: Kiểm tra kết nối mạng (Echo / Ping) với độ trễ thấp nhất.
/// Phục vụ TV3 đo Latency Round-Trip Time (RTT).
/// </summary>
app.MapGet("/api/ping", (HttpContext httpContext, ILogStorageService storageService) =>
{
    storageService.RecordPingRequest();

    var clientIp = httpContext.Connection.RemoteIpAddress?.ToString() ?? "127.0.0.1";
    if (httpContext.Request.Headers.TryGetValue("X-Forwarded-For", out var forwarded))
    {
        clientIp = forwarded.ToString().Split(',')[0].Trim();
    }

    var response = new PingResponse
    {
        Status = "healthy",
        Message = "pong",
        ServerTimeUtc = DateTime.UtcNow,
        UptimeSeconds = Math.Round(storageService.GetUptimeSeconds(), 1),
        ServerPlatform = "ASP.NET Core (.NET 10.0)",
        EnvironmentName = app.Environment.EnvironmentName,
        ClientIp = clientIp
    };

    return Results.Ok(response);
})
.WithName("PingServer")
.WithTags("Testing Endpoints")
.WithSummary("Kiểm tra kết nối và độ trễ (Ping/Pong)")
.WithDescription("Trả về trạng thái server 'healthy', thông điệp 'pong', IP client và thời gian chạy.");

/// <summary>
/// ENDPOINT 2: POST /api/logs
/// Nhiệm vụ: Tiếp nhận bản ghi mạng từ Client, in trực tiếp ra console, và lưu vào bộ nhớ.
/// Đây là endpoint chính dùng trong kịch bản DEMO Phút 3:
/// 'Gọi API trên link Swagger công khai -> Server in log request, trả về mã 200 OK'.
/// </summary>
app.MapPost("/api/logs", async (HttpContext httpContext, CreateLogRequest request, ILogStorageService storageService) =>
{
    // Lấy IP Client thực tế
    var clientIp = httpContext.Connection.RemoteIpAddress?.ToString() ?? "127.0.0.1";
    if (httpContext.Request.Headers.TryGetValue("X-Forwarded-For", out var forwarded))
    {
        clientIp = forwarded.ToString().Split(',')[0].Trim();
    }

    // Tính toán kích thước payload thực tế từ header hoặc nội dung JSON
    long payloadSize = httpContext.Request.ContentLength ?? 0;
    if (payloadSize == 0 && request.Message != null)
    {
        payloadSize = System.Text.Encoding.UTF8.GetByteCount(request.Message);
    }

    // Kiểm tra dữ liệu đầu vào cơ bản
    if (string.IsNullOrWhiteSpace(request.Message))
    {
        return Results.BadRequest(new
        {
            success = false,
            error = "Nội dung 'message' không được để trống."
        });
    }

    // Lưu log vào dịch vụ In-Memory
    var savedLog = storageService.AddLog(request, clientIp, payloadSize);

    // In log nổi bật ra Console để trình chiếu trực tiếp trên máy chiếu
    var originalColor = Console.ForegroundColor;
    Console.ForegroundColor = ConsoleColor.Magenta;
    Console.WriteLine($"[DEMO LOG NHẬN ĐƯỢC] ID={savedLog.Id[..8]} | Device={savedLog.DeviceId} | Level={savedLog.Level} | Msg='{savedLog.Message}' | Size={payloadSize}B");
    Console.ForegroundColor = originalColor;

    return Results.Ok(new
    {
        success = true,
        message = "Ghi nhận log thành công!",
        data = savedLog
    });
})
.WithName("CreateLog")
.WithTags("Logging Endpoints")
.WithSummary("Gửi bản tin log lên server (DEMO Phút 3)")
.WithDescription("Tiếp nhận dữ liệu từ Client (WinForms/Postman/Swagger), in ra Console server và phản hồi mã 200 OK.");

/// <summary>
/// ENDPOINT 3: GET /api/logs
/// Nhiệm vụ: Xem danh sách các log đã nhận từ trước đến nay.
/// Hỗ trợ lọc theo level, thiết bị, và giới hạn số lượng.
/// </summary>
app.MapGet("/api/logs", (int? limit, string? level, string? deviceId, ILogStorageService storageService) =>
{
    int safeLimit = limit.HasValue ? Math.Clamp(limit.Value, 1, 500) : 50;
    var logs = storageService.GetLogs(safeLimit, level, deviceId).ToList();

    return Results.Ok(new
    {
        totalStored = storageService.GetLogCount(),
        count = logs.Count,
        filter = new { limit = safeLimit, level, deviceId },
        logs
    });
})
.WithName("GetLogs")
.WithTags("Logging Endpoints")
.WithSummary("Lấy danh sách log mạng đã lưu")
.WithDescription("Trả về danh sách các log gần nhất đã được gửi lên server.");

/// <summary>
/// ENDPOINT 4: DELETE /api/logs
/// Nhiệm vụ: Xóa sạch bộ nhớ log để chuẩn bị trước mỗi đợt chạy test tải (Load testing ngày 3).
/// </summary>
app.MapDelete("/api/logs", (ILogStorageService storageService) =>
{
    storageService.ClearLogs();
    return Results.Ok(new
    {
        success = true,
        message = "Đã dọn dẹp sạch toàn bộ log trong bộ nhớ."
    });
})
.WithName("ClearLogs")
.WithTags("Logging Endpoints")
.WithSummary("Dọn sạch toàn bộ log trong bộ nhớ");

/// <summary>
/// ENDPOINT 5: GET /api/metrics
/// Nhiệm vụ: Thu thập thông số RAM, CPU, Uptime và lưu lượng request.
/// Phục vụ trực tiếp cho TASK NGÀY 3: 'Thống kê RAM/CPU server tiêu thụ' và đưa số liệu vào Slide so sánh.
/// </summary>
app.MapGet("/api/metrics", (ILogStorageService storageService) =>
{
    var metrics = storageService.GetServerMetrics();
    return Results.Ok(metrics);
})
.WithName("GetServerMetrics")
.WithTags("Performance & Metrics")
.WithSummary("Thống kê RAM, CPU và số lượng Request (Task Ngày 3)")
.WithDescription("Cung cấp các số liệu thực tế về tài nguyên tiêu thụ của server Self-Hosted.");

// =========================================================================================
// 5. KHỞI CHẠY TIẾN TRÌNH SERVER
// =========================================================================================
Console.WriteLine("====================================================================");
Console.WriteLine($"   NT106 SELF-HOSTED WEB API SERVER ĐANG KHỞI CHẠY");
Console.WriteLine($"   Cổng dịch vụ (Port): {assignedPort}");
Console.WriteLine($"   Địa chỉ Swagger UI: http://localhost:{assignedPort}/swagger");
Console.WriteLine($"   Địa chỉ Scalar UI:  http://localhost:{assignedPort}/scalar/v1");
Console.WriteLine("====================================================================");

app.Run();
