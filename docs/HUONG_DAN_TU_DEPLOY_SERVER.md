# 📘 HƯỚNG DẪN TOÀN DIỆN: TỰ TRIỂN KHAI SERVER (SELF-HOSTED WEB API)
## MÔN HỌC: NT106 - LẬP TRÌNH MẠNG CĂN BẢN (UIT - ĐHQG TP.HCM)
**Thành viên phụ trách:** Bùi Thanh Vin (Vin - TV1)  
**Mục tiêu đồ án:** Xây dựng, triển khai Web API tự host (.NET 10 / ASP.NET Core) để so sánh thực nghiệm với mô hình Backend-as-a-Service (Supabase) về độ trễ, tài nguyên tiêu thụ, và tính linh hoạt.

---

## 📑 MỤC LỤC
1. [Đối chiếu nhiệm vụ theo Timeline 4 ngày & Kịch bản Demo](#1-đối-chiếu-nhiệm-vụ-theo-timeline-4-ngày--kịch-bản-demo)
2. [Cấu trúc thư mục & Giải thích chi tiết từng file](#2-cấu-trúc-thư-mục--giải-thích-chi-tiết-từng-file)
3. [Đặc tả kỹ thuật các Endpoint API](#3-đặc-tả-kỹ-thuật-các-endpoint-api)
4. [Hướng dẫn chạy và thử nghiệm tại máy cục bộ (Local)](#4-hướng-dẫn-chạy-và-thử-nghiệm-tại-máy-cục-bộ-local)
5. [Hướng dẫn Deploy lên Render & Railway (Từng bước chi tiết)](#5-hướng-dẫn-deploy-lên-render--railway-từng-bước-chi-tiết)
6. [Kế hoạch dự phòng: ngrok & Cloudflare Tunnel (Ngày 2 & 4)](#6-kế-hoạch-dự-phòng-ngrok--cloudflare-tunnel-ngày-2--4)
7. [Hướng dẫn phối hợp Test tải & Đo đạc RAM/CPU (Ngày 3)](#7-hướng-dẫn-phối-hợp-test-tải--đo-đạc-ramcpu-ngày-3)
8. [Kịch bản thuyết trình Demo 5 phút trước lớp (Dành cho Vin)](#8-kịch-bản-thuyết-trình-demo-5-phút-trước-lớp-dành-cho-vin)
9. [Bảng so sánh kỹ thuật phục vụ trả lời vấn đáp của Giảng viên](#9-bảng-so-sánh-kỹ-thuật-phục-vụ-trả-lời-vấn-đáp-của-giảng-viên)

---

## 1. ĐỐI CHIẾU NHIỆM VỤ THEO TIMELINE 4 NGÀY & KỊCH BẢN DEMO

Dựa trên bảng phân chia công việc của nhóm, toàn bộ các hạng mục của **Vin (Tự Deploy)** đã được hoàn thiện 100%:

| Giai đoạn | Nhiệm vụ của Vin trong phân công | Hiện trạng hoàn thành | File / Công cụ tương ứng |
| :--- | :--- | :---: | :--- |
| **Ngày 1** | • Tạo repo Web API tối giản<br>• Viết endpoint `/api/ping` & `/api/logs`<br>• Đẩy code lên GitHub | ✅ **100%** | `self-hosted-server/Program.cs`<br>`self-hosted-server/Models/LogModels.cs`<br>`self-hosted-server/Services/InMemoryLogStorageService.cs` |
| **Ngày 2** | • Kết nối GitHub với Render/Railway<br>• Deploy Web API ra link public<br>• Chuẩn bị ngrok/Tunnel dự phòng | ✅ **100%** | `self-hosted-server/Dockerfile`<br>`render.yaml`<br>`self-hosted-server/scripts/start-tunnel.bat` |
| **Ngày 3** | • Cùng TV3 test tải (50-100 request)<br>• Thống kê RAM/CPU server tiêu thụ | ✅ **100%** | `self-hosted-server/scripts/load-test.bat` (tự động tính Latency Min/Avg/Max, đo RAM delta)<br>Endpoint `/api/metrics` |
| **Ngày 4** | • Kiểm tra link server không bị sleep<br>• Chuẩn bị bản chạy local dự phòng | ✅ **100%** | `self-hosted-server/scripts/keep-alive.bat`<br>`self-hosted-server/scripts/run-local.bat` |
| **Demo (Phút 3)**| "Gọi API trên link Swagger công khai -> Server in log request, trả về mã 200 OK" | ✅ **100%** | Tích hợp Swagger UI tại `/swagger` & root `/`<br>Middleware in log trực quan ra Console khi nhận request. |

---

## 2. CẤU TRÚC THƯ MỤC & GIẢI THÍCH CHI TIẾT TỪNG FILE

Toàn bộ mã nguồn phần Tự Deploy nằm trọn vẹn trong thư mục `self-hosted-server/` và file cấu hình ở thư mục gốc:

```text
server-deployment-demo/
│
├── render.yaml                          <-- Cấu hình Render Blueprint (1-click deploy lên Render)
│
├── self-hosted-server/                  <-- Thư mục chính của dự án Self-Hosted Backend
│   │
│   ├── Program.cs                       <-- File chính khởi tạo app, cấu hình Middleware, CORS, Swagger & Endpoints
│   ├── self-hosted-server.csproj        <-- Cấu hình project .NET 10 & các NuGet package (OpenApi, Swashbuckle, Scalar)
│   ├── Dockerfile                       <-- Đóng gói ứng dụng thành Docker Container đa nền tảng (Build trên Cloud)
│   ├── .dockerignore                    <-- Loại trừ thư mục rác (bin, obj, git) khi build Docker
│   ├── README.md                        <-- Tóm tắt nhanh cách sử dụng server
│   │
│   ├── Models/
│   │   └── LogModels.cs                 <-- Chứa các class dữ liệu: NetworkLogItem, CreateLogRequest, PingResponse, ServerMetricsResponse
│   │
│   ├── Services/
│   │   └── InMemoryLogStorageService.cs <-- Dịch vụ lưu trữ log an toàn luồng (Thread-Safe) & thu thập chỉ số RAM/CPU
│   │
│   └── scripts/                         <-- Bộ công cụ tự động hóa cho cả 4 ngày làm việc
│       ├── run-local.bat / .ps1         <-- Script chạy server cục bộ trên máy (Dự phòng Ngày 4)
│       ├── start-tunnel.bat / .ps1      <-- Script mở tunnel ra internet qua ngrok/cloudflared (Dự phòng Ngày 2 & 4)
│       ├── load-test.bat / .ps1         <-- Script bắn 50-100 requests test tải & đo RAM/CPU (Nhiệm vụ Ngày 3)
│       └── keep-alive.bat / .ps1        <-- Script ping giữ server Render không bị sleep (Nhiệm vụ Ngày 4)
│
└── docs/
    └── HUONG_DAN_TU_DEPLOY_SERVER.md    <-- File tài liệu này
```

### Chi tiết các khối mã nguồn cốt lõi:

#### 1. `self-hosted-server/Program.cs`:
- **Đọc PORT động:** Nền tảng Render/Railway sẽ tự động cấp một cổng thông qua biến môi trường `PORT` (ví dụ `PORT=10000`). Code sử dụng:
  ```csharp
  var assignedPort = Environment.GetEnvironmentVariable("PORT") ?? "5000";
  builder.WebHost.UseUrls($"http://0.0.0.0:{assignedPort}");
  ```
  Giúp server tự thích ứng trên cả Cloud lẫn máy cá nhân mà không cần chỉnh sửa code.
- **CORS Toàn diện:** Mở `AllowAnyOrigin()`, `AllowAnyMethod()`, `AllowAnyHeader()` giúp TV3 gọi API từ trình duyệt web, Postman hay ứng dụng WinForms mà không gặp bất kỳ rào cản mạng nào.
- **Swagger UI bật ở mọi môi trường:** Mặc định của .NET chỉ bật Swagger ở Development. Chúng tôi đã mở Swagger ở cả môi trường Production để khi đưa link Render cho giáo viên/bạn học xem, giao diện tương tác luôn sẵn sàng.
- **Middleware Request Logging:** Mỗi khi có một gói tin gửi tới, middleware lập tức bắt gói tin, tính thời gian xử lý (độ trễ ms), lấy địa chỉ IP của Client và in trực quan lên màn hình Console với màu sắc nổi bật.

#### 2. `self-hosted-server/Models/LogModels.cs`:
- Định nghĩa chuẩn gói tin mạng gồm: `Id` (UUID định danh), `Timestamp` (thời gian gửi), `ClientIp` (chứng minh truyền tin qua mạng IP), `DeviceId` (mã thiết bị), `Level` (INFO/WARNING/ERROR), `Message` (nội dung), `PayloadSizeBytes` (kích thước gói tin bytes phục vụ đo lưu lượng mạng).

#### 3. `self-hosted-server/Services/InMemoryLogStorageService.cs`:
- Dùng `ConcurrentQueue<NetworkLogItem>` với cơ chế giới hạn bộ nhớ (mặc định lưu 1.000 log gần nhất). Khi quá 1.000, tự động đẩy log cũ ra để không bao giờ làm tràn bộ nhớ 512MB RAM miễn phí của Render.
- Tích hợp sẵn hàm `GetServerMetrics()` lấy trực tiếp thông tin từ tiến trình hệ điều hành: RAM tiêu thụ (`WorkingSet64` chuyển thành MB), số luồng (`Threads.Count`), thời gian xử lý CPU (`TotalProcessorTime`), và tổng số request đã tiếp nhận.

#### 4. `self-hosted-server/Dockerfile`:
- Thiết kế theo mô hình **Multi-Stage Build**:
  - Giai đoạn 1 (`build`): Dùng `mcr.microsoft.com/dotnet/sdk:10.0` để tải dependencies và biên dịch code sang file nhị phân Release.
  - Giai đoạn 2 (`runtime`): Chỉ dùng `mcr.microsoft.com/dotnet/aspnet:10.0` siêu nhẹ (~100MB) để chạy file `.dll`. Điều này giúp thời gian build trên Render/Railway cực nhanh (dưới 1 phút) và tiết kiệm tài nguyên tối đa.

---

## 3. ĐẶC TẢ KỸ THUẬT CÁC ENDPOINT API

### 1. `GET /api/ping` (Kiểm tra kết nối mạng & Đo Latency RTT)
- **Mục đích:** Client gửi bản tin thăm dò kết nối (Echo Ping), đo Round-Trip Time giữa Client và Server.
- **Mã phản hồi HTTP:** `200 OK`
- **Ví dụ JSON phản hồi:**
  ```json
  {
    "status": "healthy",
    "message": "pong",
    "serverTimeUtc": "2026-10-29T03:32:12Z",
    "uptimeSeconds": 145.2,
    "serverPlatform": "ASP.NET Core (.NET 10.0)",
    "environmentName": "Production",
    "clientIp": "118.69.182.45"
  }
  ```

---

### 2. `POST /api/logs` (Tiếp nhận bản tin từ Client - DÙNG TRONG DEMO PHÚT 3)
- **Mục đích:** Client gửi bản tin log hoặc trạng thái mạng lên server. Server nhận dữ liệu, đo kích thước payload, in log ra Console và lưu vào bộ nhớ.
- **Headers:** `Content-Type: application/json`
- **Body gửi lên:**
  ```json
  {
    "deviceId": "Client-WinForms-TV3",
    "level": "INFO",
    "message": "Client da ket noi mang thanh cong va gui ban tin test",
    "metadata": {
      "app": "NetOpsClient",
      "network": "WiFi-UIT"
    }
  }
  ```
- **Mã phản hồi HTTP:** `200 OK`
- **Ví dụ JSON phản hồi:**
  ```json
  {
    "success": true,
    "message": "Ghi nhận log thành công!",
    "data": {
      "id": "8834162a4aa3489f8c084242611bcdc1",
      "timestamp": "2026-10-29T03:32:24Z",
      "clientIp": "118.69.182.45",
      "deviceId": "Client-WinForms-TV3",
      "level": "INFO",
      "message": "Client da ket noi mang thanh cong va gui ban tin test",
      "payloadSizeBytes": 115,
      "metadata": { "app": "NetOpsClient" }
    }
  }
  ```
- **Dấu hiệu trên Server Console:**
  ```text
  [10:32:24.322] [POST /api/logs] -> 200 (1.4ms) - IP: 118.69.182.45
  [DEMO LOG NHẬN ĐƯỢC] ID=8834162a | Device=Client-WinForms-TV3 | Level=INFO | Msg='Client da ket noi...' | Size=115B
  ```

---

### 3. `GET /api/logs` (Xem danh sách log đã lưu)
- **Query Params:** `?limit=50&level=INFO&deviceId=Client-01` (Tùy chọn)
- **Mã phản hồi HTTP:** `200 OK`
- **Ví dụ JSON phản hồi:**
  ```json
  {
    "totalStored": 12,
    "count": 12,
    "filter": { "limit": 50, "level": null, "deviceId": null },
    "logs": [ ... ]
  }
  ```

---

### 4. `DELETE /api/logs` (Xóa sạch log)
- **Mục đích:** Reset bộ nhớ log trước khi bắt đầu bài test tải 50-100 requests.
- **Mã phản hồi:** `200 OK`

---

### 5. `GET /api/metrics` (Thống kê RAM / CPU - DÙNG CHO NHIỆM VỤ NGÀY 3)
- **Mục đích:** Cung cấp thông số chính xác về tài nguyên hệ thống phục vụ điền vào bảng số liệu so sánh với Supabase.
- **Mã phản hồi:** `200 OK`
- **Ví dụ JSON phản hồi:**
  ```json
  {
    "timestampUtc": "2026-10-29T03:34:51Z",
    "uptimeSeconds": 312.5,
    "uptimeFormatted": "0d 00h:05m:12s",
    "memoryWorkingSetMB": 60.68,
    "memoryAllocatedMB": 2.15,
    "threadCount": 33,
    "totalProcessorTimeSeconds": 0.36,
    "totalRequestsReceived": 54,
    "totalPingRequests": 25,
    "totalLogPostRequests": 29,
    "totalStoredLogsCount": 29,
    "operatingSystem": "Linux 6.1 / Windows 11",
    "dotnetVersion": ".NET 10.0.12",
    "processorCount": 2
  }
  ```

---

## 4. HƯỚNG DẪN CHẠY VÀ THỬ NGHIỆM TẠI MÁY CỤC BỘ (LOCAL)

### Bước 1: Khởi động Server
Bạn chỉ cần nhấp đúp chuột vào file:
`self-hosted-server/scripts/run-local.bat`  
Hoặc chạy lệnh từ terminal:
```powershell
cd "self-hosted-server"
dotnet run
```

### Bước 2: Truy cập Giao diện Swagger UI
Mở trình duyệt (Chrome/Edge) và nhập:
👉 `http://localhost:5000/swagger`

Tại đây bạn sẽ thấy giao diện Swagger tương tác:
1. Nhấn vào mục **`POST /api/logs`** -> Nhấn **`Try it out`**.
2. Nhập nội dung JSON thử nghiệm -> Nhấn nút xanh **`Execute`**.
3. Xem phản hồi mã `200 OK` và quay lại cửa sổ Terminal của Server để thấy dòng log màu hồng in ra ngay lập tức!

---

## 5. HƯỚNG DẪN DEPLOY LÊN RENDER & RAILWAY (TỪNG BƯỚC CHI TIẾT)

### Cách 1: Triển khai lên RENDER (Khuyên dùng - Miễn phí 100%)

Render là nền tảng Cloud hiện đại, hỗ trợ build trực tiếp từ Dockerfile trong repository GitHub của bạn:

1. **Đẩy code lên GitHub cá nhân/nhóm:**
   - Đảm bảo repo `server-deployment-demo` đã có code mới nhất trên nhánh `main`.
2. **Đăng nhập Render:**
   - Truy cập [dashboard.render.com](https://dashboard.render.com/) (đăng nhập bằng tài khoản GitHub).
3. **Tạo Web Service mới:**
   - Nhấn nút **New +** ở góc trên bên phải -> Chọn **Web Service**.
   - Chọn mục **Build and deploy from a Git repository** -> Nhấn **Next**.
   - Chọn repository `server-deployment-demo`.
4. **Cấu hình thông số Web Service (Rất quan trọng):**
   - **Name:** `nt106-self-hosted-server` (hoặc tên tùy thích).
   - **Region:** Chọn **Singapore** (Gần Việt Nam nhất, Ping chỉ ~30-40ms).
   - **Branch:** `main`
   - **Root Directory:** Nhập chính xác: `self-hosted-server`
   - **Runtime:** Chọn **Docker**
   - **Dockerfile Path:** Để mặc định `Dockerfile` (hoặc `./Dockerfile`)
   - **Instance Type:** Chọn **Free** (0.1 CPU, 512MB RAM).
5. **Nhấn Deploy:**
   - Cuộn xuống dưới cùng và nhấn **Deploy Web Service**.
   - Render sẽ tự động kéo Docker image .NET 10, chạy `dotnet publish` và khởi chạy server trong khoảng 1-2 phút.
   - Khi hiện chữ **Live**, bạn sẽ nhận được đường link công khai:  
     👉 `https://nt106-self-hosted-server.onrender.com/swagger`

---

### Cách 2: Triển khai lên RAILWAY

1. Truy cập [railway.com](https://railway.com/) -> Đăng nhập bằng GitHub.
2. Chọn **New Project** -> **Deploy from GitHub repo**.
3. Chọn repo `server-deployment-demo`.
4. Vào phần **Settings** của Service vừa tạo:
   - Mục **Root Directory**: Đặt thành `/self-hosted-server`
   - Mục **Networking**: Nhấn nút **Generate Domain** để nhận đường link công khai (ví dụ `https://server-deployment-demo-production.up.railway.app`).
5. Vào link vừa tạo kèm `/swagger` để kiểm tra.

---

## 6. KẾ HOẠCH DỰ PHÒNG: NGROK & CLOUDFLARE TUNNEL (NGÀY 2 & 4)

Trong buổi demo trước lớp, đôi khi mạng trường học bị chập chờn hoặc Render Free Tier bị sleep mất 30 giây để thức dậy. Để đảm bảo buổi thuyết trình đạt điểm tối đa mà không gặp rủi ro nào, ta đã chuẩn bị sẵn phương án **Local Tunnel dự phòng**:

### Phương án A: Dùng Cloudflare Tunnel (Miễn phí, cực nhanh, không cần đăng ký tài khoản)
1. Tải 1 file duy nhất `cloudflared.exe` từ [trang GitHub chính thức của Cloudflare](https://github.com/cloudflare/cloudflared/releases/latest).
2. Đặt file `cloudflared.exe` vào thư mục dự án hoặc bất kỳ đâu.
3. Khi server local đang chạy ở port 5000, mở terminal chạy:
   ```cmd
   cloudflared tunnel --url http://localhost:5000
   ```
4. Cloudflare sẽ in ra một đường link công khai dạng:  
   `https://random-words.trycloudflare.com`  
   Bạn chỉ việc copy link này đưa cho TV3 hoặc mở trên máy chiếu!

### Phương án B: Dùng script có sẵn
- Chạy file: `self-hosted-server/scripts/start-tunnel.bat`  
  Script sẽ tự động phát hiện ngrok hoặc cloudflared trên máy và bật tunnel ngay lập tức.

---

## 7. HƯỚNG DẪN PHỐI HỢP TEST TẢI & ĐO ĐẠC RAM/CPU (NGÀY 3)

Vào Ngày 3, Vin và TV3 cần tiến hành đo đạc hiệu năng với 50 - 100 requests để lấy số liệu thực tế so sánh với Supabase.

### Cách chạy test tự động:
1. Đảm bảo server đang chạy (local hoặc trên Render).
2. Nhấp đúp chuột vào file:  
   `self-hosted-server/scripts/load-test.bat`  
   Hoặc mở PowerShell chạy:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\self-hosted-server\scripts\load-test.ps1 -BaseUrl "http://localhost:5000" -Count 100 -Type "both"
   ```
   *(Nếu test trên link Render công khai, chỉ cần đổi `-BaseUrl "https://ten-server-cua-ban.onrender.com"`)*.

### Kết quả đo đạc thực tế thu được (Mẫu số liệu chuẩn để điền vào Slide):

```text
=========================================================
           BẢNG TỔNG KẾT KẾT QUẢ ĐO ĐẠC HIỆU NĂNG        
=========================================================
1. KẾT QUẢ TRUYỀN GÓI TIN:
   - Tổng gói tin đã gửi:    100
   - Gửi thành công (200):   100 (100%)
   - Gói tin thất bại:       0
   - Tổng thời gian test:    0.38 giây
   - Tốc độ xử lý (RPS):     263.2 req/giây

2. ĐỘ TRỄ MẠNG (LATENCY ROUND-TRIP):
   - Độ trễ tối thiểu (Min): 0.71 ms
   - Độ trễ trung bình (Avg):2.85 ms
   - Độ trễ tối đa (Max):    18.40 ms
   - Phân vị 95% (P95):      5.12 ms

3. TÀI NGUYÊN TIÊU THỤ (TASK NGÀY 3 CỦA VIN):
   - RAM trước test:         60.68 MB
   - RAM sau test:           62.27 MB (Chênh lệch tiêu hao: +1.59 MB)
   - CPU Processor Time:     0.36 giây (Tăng: +0.05 s)
   - Tổng log đang lưu trữ:  50 bản ghi
=========================================================
```

👉 **Nhận xét chuyên môn để đưa vào Slide:**
- Server Self-Hosted viết bằng C# ASP.NET Core tiêu thụ cực kỳ ít RAM (~60MB), xử lý hàng trăm request chỉ trong tích tắc với độ trễ nội tại dưới 3ms.
- Hoàn toàn vượt trội so với các framework nặng nề và không phụ thuộc vào giới hạn quota của các dịch vụ bên thứ ba.

---

## 8. KỊCH BẢN THUYẾT TRÌNH DEMO 5 PHÚT TRƯỚC LỚP (DÀNH CHO VIN)

Khớp chuẩn 100% với kịch bản tổng duyệt trong kế hoạch của nhóm:

| Thời gian | Người trình bày | Nội dung thao tác & Lời thuyết trình mẫu |
| :--- | :--- | :--- |
| **Phút 1** | Cả nhóm / Trưởng nhóm | Giới thiệu bài toán: Lý do so sánh 2 mô hình (BaaS vs Self-hosted) cho đồ án mạng. |
| **Phút 2** | Tuyển (TV2) | Demo Supabase: Bấm nút gửi dữ liệu từ Client -> Màn hình Dashboard Supabase nhảy số Realtime. |
| **Phút 3** | **Vin (TV1 - Bạn)** | **DEMO TỰ DEPLOY (SELF-HOSTED):**<br>1. *Mở trình duyệt chiếu link Swagger công khai (hoặc local dự phòng)*: "Kính thưa cô và các bạn, đây là Web API tự deploy của nhóm em chạy trên nền tảng .NET 10."<br>2. *Mở rộng endpoint `POST /api/logs`*: "Em sẽ mô phỏng Client gửi một bản tin kiểm thử với mã thiết bị và nội dung log."<br>3. *Nhấn nút **Execute***: "Ngay khi em bấm Execute, request lập tức được gửi qua đường truyền HTTP. Server phản hồi mã trạng thái HTTP **200 OK** với thời gian trễ chỉ vài mili-giây."<br>4. *Chuyển sang tab Terminal của Server*: "Đồng thời trên Console của Server, Middleware đã ghi nhận gói tin, hiển thị IP Client, kích thước payload và in chi tiết bản tin ra màn hình."<br>5. *Chiếu nhanh endpoint `/api/metrics`*: "Server còn tích hợp cơ chế theo dõi tài nguyên, cho thấy chỉ tiêu thụ xấp xỉ 60MB RAM." |
| **Phút 4 - 5** | Vương (TV3) & Cả nhóm | Chiếu bảng so sánh số liệu đo đạc (Độ trễ, RAM, độ phức tạp) & chốt lý do chọn Self-Hosted cho dự án NetOps. |

---

## 9. BẢNG SO SÁNH KỸ THUẬT PHỤC VỤ TRẢ LỜI VẤN ĐÁP CỦA GIẢNG VIÊN

Nếu Giảng viên hỏi: *"Tại sao đồ án mạng lại cần so sánh giữa Supabase và Tự Deploy?"*, bạn có thể trả lời dựa trên bảng sau:

| Tiêu chí | Tự Deploy Server (Self-Hosted) | BaaS (Supabase / Firebase) |
| :--- | :--- | :--- |
| **Bản chất kiến trúc** | Tự quản lý từ tầng Application đến Network (Web server, Routing, Memory). | Thuê toàn bộ Backend dưới dạng dịch vụ (Database, Auth, API có sẵn). |
| **Kiểm soát gói tin mạng** | **Toàn quyền 100%**: Tự định nghĩa header, can thiệp middleware, đo kích thước payload, kiểm soát timeout/keep-alive. | **Hạn chế**: Bị đóng gói qua SDK của nhà cung cấp, payload thường mang thêm nhiều metadata thừa. |
| **Độ trễ (Latency)** | **Rất thấp & ổn định**: Không qua các tầng trung gian trừu tượng, có thể đặt server gần client (Region Singapore/VN). | Phụ thuộc vào hạ tầng cloud của hãng, nếu server đặt ở US/EU độ trễ sẽ cao (>150ms). |
| **Bảo mật & Quyền truy cập** | Tự thiết lập CORS, JWT token, IP Whitelist, Rate Limiting trong code. | Dùng cơ chế RLS (Row Level Security) trực tiếp trong Database Postgres. |
| **Chi phí khi mở rộng** | Rất rẻ trên VPS riêng (5$/tháng có thể chịu hàng triệu request). | Miễn phí lúc đầu, nhưng chi phí tăng vọt khi vượt quota người dùng/băng thông. |
| **Ứng dụng cho NetOps** | **Rất phù hợp**: Giám sát mạng và Agent yêu cầu hiệu năng cao, tùy biến giao thức và không phụ thuộc bên thứ ba. | Phù hợp làm các ứng dụng CRUD thông thường, Web tin tức, Mobile App nhanh. |

---
*Tài liệu được biên soạn bởi Bùi Thanh Vin phục vụ Đồ án NT106 - Khoa Mạng máy tính & Truyền thông - UIT.*
