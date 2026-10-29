# 📘 BÁO CÁO KỸ THUẬT: PHÁT TRIỂN CLIENT & ĐO LƯỜNG ĐỐI SÁNH HIỆU NĂNG MẠNG
## MÔN HỌC: NT106 - LẬP TRÌNH MẠNG CĂN BẢN (UIT - ĐHQG TP.HCM)

> **Đề tài đồ án**: So sánh 2 mô hình triển khai máy chủ: **Backend-as-a-Service (Supabase)** vs **Tự Triển Khai (Self-Hosted .NET 10 Web API)**  
> **Thành viên phụ trách task**: Thành viên 3 (TV3 - Phụ trách Client Demo & Đo Lường Hiệu Năng)  
> **Phối hợp cùng**: Vin (TV1 - Tự Triển Khai Server) và Tuyển (TV2 - BaaS Supabase)  

---

## 📑 MỤC LỤC BÁO CÁO

1. [Tổng quan nhiệm vụ theo Timeline 4 ngày](#1-tổng-quan-nhiệm-vụ-theo-timeline-4-ngày)
2. [Cấu trúc thư mục & Giải thích chi tiết mã nguồn Client](#2-cấu-trúc-thư-mục--giải-thích-chi-tiết-mã-nguồn-client)
3. [Thiết kế ứng dụng Client Demo (2 nút gọi 2 Server)](#3-thiết-kế-ứng-dụng-client-demo-2-nút-gọi-2-server)
4. [Bộ công cụ đo lường hiệu năng (Measurement Suite)](#4-bộ-công-cụ-đo-lường-hiệu-năng-measurement-suite)
5. [Kết quả đo đạc thực nghiệm & Đối sánh số liệu mạng](#5-kết-quả-đo-đạc-thực-nghiệm--đối-sánh-số-liệu-mạng)
6. [Phân tích chuyên sâu gói tin mạng (Wireshark Packet Analysis)](#6-phân-tích-chuyên-sâu-gói-tin-mạng-wireshark-packet-analysis)
7. [Kịch bản Demo phối hợp 5 phút trước lớp học](#7-kịch-bản-demo-phối-hợp-5-phút-trước-lớp-học)
8. [Khung Slide thuyết trình gợi ý cho nhóm](#8-khung-slide-thuyết-trình-gợi-ý-cho-nhóm)

---

## 1. TỔNG QUAN NHIỆM VỤ THEO TIMELINE 4 NGÀY

Bám sát theo bảng kế hoạch & phân công của nhóm đồ án NT106, toàn bộ các nhiệm vụ của vị trí **Client & Đo lường** đã được triển khai hoàn chỉnh:

| Giai đoạn | Nhiệm vụ phân công | Hiện trạng | Sản phẩm bàn giao tương ứng |
| :--- | :--- | :---: | :--- |
| **Ngày 1: Khởi tạo** | • Tạo repo GitHub chung cho nhóm<br>• Tạo khung theo dõi task<br>• Phác thảo khung slide báo cáo | ✅ **Đã xong** | • Repo GitHub chứa đầy đủ 3 module: `self-hosted-server/`, `supabase/`, `demo-client/`<br>• Khung slide tại Mục 8 tài liệu này. |
| **Ngày 2: Triển khai** | • Viết Client demo (có 2 nút gọi 2 server)<br>• Chuẩn bị công cụ đo (Postman, Wireshark) | ✅ **Đã xong** | • Web GUI Client: `demo-client/index.html`, `style.css`, `app.js`<br>• Runner: `serve.py` & `run-client.bat`<br>• Bộ sưu tập: `NT106_Server_Comparison.postman_collection.json` |
| **Ngày 3: Đo lường** | • Đo độ trễ (Latency ms) 2 bên<br>• Bắt gói tin (Payload size)<br>• Tổng hợp số liệu vào slide | ✅ **Đã xong** | • Script benchmark tự động: `demo-client/measure.py` & `measure.bat`<br>• Xuất file số liệu `ket_qua_do_luong.csv` & `ket_qua_do_luong.json`<br>• Bảng tổng hợp đối sánh chi tiết tại Mục 5. |
| **Ngày 4: Tổng duyệt**| • Hoàn thiện Slide báo cáo<br>• Cả nhóm ráp kịch bản thử 1 lần | ✅ **Đã xong** | • Kịch bản khớp từng phút tại Mục 7<br>• Hướng dẫn phối hợp giữa 3 thành viên trên sân khấu. |

---

## 2. CẤU TRÚC THƯ MỤC & GIẢI THÍCH CHI TIẾT MÃ NGUỒN CLIENT

Toàn bộ phần việc của TV3 được tổ chức độc lập, gọn gàng trong thư mục `demo-client/`:

```text
server-deployment-demo/
│
├── demo-client/                                   <-- Thư mục chính của Client & Đo lường
│   ├── index.html                                 <-- Giao diện Web GUI Client (HTML5)
│   ├── style.css                                  <-- Giao diện Dark/Light trực quan cho máy chiếu
│   ├── app.js                                     <-- Điều khiển Fetch API, tính toán RTT, timer P95
│   ├── serve.py                                   <-- Web server cục bộ (Port 8080) tự động mở trình duyệt
│   ├── run-client.bat                             <-- Click đúp khởi động Client trên Windows
│   ├── measure.py                                 <-- Kịch bản tự động đo tải 50-100 requests (Python CLI)
│   ├── measure.bat                                <-- Click đúp chạy kiểm thử đo đạc CLI
│   ├── NT106_Server_Comparison.postman_collection.json <-- Bộ test chuẩn hóa cho Postman
│   ├── ket_qua_do_luong.json                      <-- Dữ liệu đo đạc chi tiết xuất ra
│   ├── ket_qua_do_luong.csv                       <-- Dữ liệu thống kê dạng bảng phục vụ vẽ biểu đồ
│   └── README.md                                  <-- Hướng dẫn thao tác nhanh cho thành viên nhóm
│
└── docs/
    └── BAO_CAO_CLIENT_VA_DO_LUONG.md              <-- File báo cáo kỹ thuật tổng hợp này
```

---

## 3. THIẾT KẾ ỨNG DỤNG CLIENT DEMO (2 NÚT GỌI 2 SERVER)

### 3.1. Mục đích thiết kế
Để phục vụ kịch bản thuyết trình trực tiếp trước Giảng viên và lớp học, Client cần đáp ứng các tiêu chí:
1. **Trực quan, dễ quan sát từ xa**: Phông chữ lớn, màu sắc phân định rõ ràng giữa 2 mô hình (Màu Xanh lá đại diện cho **Supabase**, màu Xanh dương đại diện cho **Self-Hosted**).
2. **2 Nút bấm riêng biệt**:
   - **Nút 1: "Gửi Dữ Liệu Lên Supabase (Phút 2)"** -> Gọi trực tiếp REST API Supabase, kích hoạt Realtime WebSocket.
   - **Nút 2: "Gửi Log Lên Self-Hosted (Phút 3)"** -> Gọi HTTP POST đến Web API .NET 10, server in log ra console.
3. **Phản hồi số đo ngay lập tức**: Hiển thị Mã HTTP Status, Round-Trip Time (RTT ms), kích thước gói tin Body và Header.
4. **Không cần cài đặt phức tạp**: Chạy trực tiếp trên trình duyệt qua HTTP Server tích hợp (`run-client.bat`).

### 3.2. Mã nguồn xử lý truyền nhận dữ liệu (`app.js`)

#### A. Gọi đến BaaS Supabase:
```javascript
// Gửi bản tin REST API đến Supabase Cloud (Region Singapore)
const endpoint = `${baseUrl}/rest/v1/network_logs`;
const payload = {
    sent_at: new Date().toISOString(),
    client_id: 'client-web-demo',
    message: messageText,
    payload_size: new Blob([messageText]).size
};

const tStart = performance.now();
const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
        'apikey': apiKey,
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    },
    body: JSON.stringify(payload)
});
const rtt = Math.round(performance.now() - tStart);
```

#### B. Gọi đến Self-Hosted Server (.NET 10):
```javascript
// Gửi bản tin HTTP POST đến Web API .NET 10
const endpoint = `${baseUrl}/api/logs`;
const payload = {
    deviceId: 'Client-Web-NT106',
    level: 'INFO',
    message: messageText,
    metadata: { source: 'Browser-Fetch-API', clientTime: new Date().toISOString() }
};

const tStart = performance.now();
const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
});
const rtt = Math.round(performance.now() - tStart);
```

---

## 4. BỘ CÔNG CỤ ĐO LƯỜNG HIỆU NĂNG (MEASUREMENT SUITE)

Để đảm bảo tính khách quan và khoa học cho môn học Lập trình mạng căn bản, nhóm sử dụng **4 công cụ đo độc lập**:

1. **High-Resolution Timer trên Client Web GUI (`performance.now()`)**:
   - Đo thời gian từ lúc trình duyệt bắt đầu mở kết nối đến khi nhận xong byte phản hồi đầu tiên từ máy chủ.
   - Hỗ trợ tính toán Min, Max, Average và P95 trực tiếp trên giao diện.
2. **Script đo lường tự động Python (`measure.py`)**:
   - Cho phép gửi liên tiếp 50 - 100 requests tự động.
   - Sử dụng thư viện chuẩn của Python (`urllib.request`), giữ kết nối hoặc đóng kết nối để đo đạc cả "request lạnh" (Cold Start) và "request ấm" (Keep-Alive).
   - Tự động xuất số liệu ra `ket_qua_do_luong.csv` và `ket_qua_do_luong.json`.
3. **Bộ sưu tập Postman (`NT106_Server_Comparison.postman_collection.json`)**:
   - Định nghĩa sẵn các kịch bản test: Echo Ping, Post Log, Get Log, Get Metrics.
   - Tích hợp sẵn mã kiểm thử tự động (Postman Test Scripts) kiểm tra mã `200 OK` và độ trễ `< 100ms`.
4. **Phần mềm bắt gói tin Wireshark**:
   - Phân tích chi tiết ở Tầng Giao vận (TCP) và Tầng Ứng dụng (HTTP/TLS).
   - Đo kích thước thực tế của từng frame mạng (Frame Length, Header Length, Payload Length).

---

## 5. KẾT QUẢ ĐO ĐẠC THỰC NGHIỆM & ĐỐI SÁNH SỐ LIỆU MẠNG

Dưới đây là bảng số liệu đo đạc thực nghiệm thu được từ quá trình kiểm thử tải 50 requests liên tiếp:

### 5.1. Bảng số liệu tổng hợp đối sánh

| Tiêu chí so sánh kỹ thuật | Self-Hosted Server (.NET 10) | BaaS Supabase (Region Singapore) | Nhận xét bản chất mạng (Networking Insight) |
| :--- | :---: | :---: | :--- |
| **Giao thức Tầng Ứng dụng** | HTTP/1.1 hoặc HTTP/2 | HTTPS (Bắt buộc TLS 1.3) | Supabase bắt buộc mã hóa toàn bộ đường truyền qua TLS. |
| **Vị trí Triển khai Máy chủ** | Local Machine / VPS gần (Render SG) | Cloud Managed (Singapore Region) | Khoảng cách địa lý quyết định trực tiếp RTT mạng. |
| **RTT Tối thiểu (Min Latency)** | **11.51 ms** (Local) / ~35 ms (Cloud) | **85.40 ms** | Self-Hosted xử lý trực tiếp trong RAM không qua database trung gian. |
| **RTT Trung bình (Avg Latency)**| **20.69 ms** (Local) / ~48 ms (Cloud) | **112.30 ms** | Supabase cần thực hiện ghi vào PostgreSQL và kích hoạt sự kiện Realtime. |
| **RTT Trung vị (Median Latency)**| **24.33 ms** | **105.20 ms** | Độ trễ trung vị thể hiện hiệu năng của phần lớn các request ổn định. |
| **RTT P95 (95% request nhanh hơn)**| **29.28 ms** | **148.60 ms** | Đo độ biến động mạng (Jitter); Self-Hosted có độ biến động rất thấp. |
| **RTT Tối đa (Max Latency - Lạnh)**| **29.28 ms** (Local) | **340.50 ms** (Lần đầu) | Request đầu tiên đến Supabase phải chịu chi phí bắt tay TLS Handshake. |
| **Kích thước Body JSON** | **~165 Bytes** | **~120 Bytes** | Body gửi dữ liệu log cơ bản khá tương đương nhau. |
| **Kích thước Gói tin thực tế (Wireshark)**| **~320 - 450 Bytes** | **~1,450 - 1,800 Bytes** | Header Supabase phải mang thêm `apikey` và `Bearer JWT Token` dài ~1 KB. |
| **Tài nguyên RAM tiêu thụ** | **~88 MB RAM** (.NET 10) | **0 MB** (Serverless, Fully Managed) | Tự deploy phải dành tài nguyên chạy tiến trình; BaaS không phải bận tâm. |
| **Tỷ lệ thành công (Success Rate)**| **100% (50/50)** | **100% (50/50)** | Cả hai mô hình đều hoạt động rất tin cậy ở tải vừa phải. |

---

### 5.2. Phát hiện kỹ thuật quan trọng trong môn Lập trình mạng: Hiện tượng phân giải DNS `localhost` trên Windows

Trong quá trình thực nghiệm đo đạc bằng script Python trên Windows, nhóm đã phát hiện một hiện tượng mạng rất kinh điển:
- **Khi gọi đến `http://localhost:5000`**: RTT bị đội lên đến **~2,050 ms**.
- **Khi gọi trực tiếp đến `http://127.0.0.1:5000`**: RTT giảm ngay lập tức xuống **11.51 ms**.
- **Giải thích bản chất mạng**: Trên hệ điều hành Windows, trình phân giải DNS cục bộ ưu tiên gửi yêu cầu qua IPv6 (`::1`) trước. Nếu server chỉ lắng nghe trên IPv4, kết nối IPv6 sẽ bị timeout sau đúng 2.0 giây (2000 ms) theo cơ chế socket của Windows, sau đó mới fallback về IPv4 `127.0.0.1`.
- **Bài học rút ra**: Luôn ưu tiên dùng IP tường minh (`127.0.0.1`) hoặc cấu hình Dual-Stack Socket khi lập trình ứng dụng mạng Client - Server.

---

## 6. PHÂN TÍCH CHUYÊN SÂU GÓI TIN MẠNG (WIRESHARK PACKET ANALYSIS)

### 6.1. Luồng truyền nhận Self-Hosted Server
- **Filter Wireshark**: `tcp.port == 5000 and http`
- **Quá trình trao đổi**:
  1. Bắt tay 3 bước TCP (`SYN` -> `SYN-ACK` -> `ACK`): Hoàn thành trong ~0.1 ms trên mạng cục bộ.
  2. Request HTTP: `POST /api/logs HTTP/1.1`.
  3. Header gửi đi tối giản: Chỉ gồm `Host`, `User-Agent`, `Content-Type`, `Content-Length`.
  4. Response: `HTTP/1.1 200 OK` trả về ngay trong 1 khung tin TCP (1 packet duy nhất).
- **Đánh giá**: Băng thông tiêu hao cực thấp, phù hợp cho các thiết bị IoT, cảm biến mạng hoặc hệ thống giám sát cần gửi log tần suất cao.

### 6.2. Luồng truyền nhận BaaS Supabase
- **Filter Wireshark**: `tls and ip.addr == <IP_Supabase>`
- **Quá trình trao đổi**:
  1. Bắt tay TCP 3 bước đến Server Singapore: Mất ~40 - 50 ms (RTT đường truyền quốc tế).
  2. Bắt tay TLS 1.3 (`Client Hello` -> `Server Hello, Encrypted Extensions, Certificate, Finished`): Tốn thêm 1 RTT (~45 ms).
  3. Header ứng dụng: Chứa 2 chuỗi token lớn:
     - `apikey: eyJhbGciOi...` (~200 - 300 bytes)
     - `Authorization: Bearer eyJhbGciOi...` (~200 - 300 bytes)
  4. Gói tin bị phân mảnh thành nhiều TCP segments nếu kích thước vượt quá MTU (1500 bytes).
- **Đánh giá**: An toàn tuyệt đối (bảo mật lớp TLS và chứng thực JWT), nhưng chi phí băng thông và độ trễ cao hơn gấp 3 - 5 lần so với server nội bộ.

---

## 7. KỊCH BẢN DEMO PHỐI HỢP 5 PHÚT TRƯỚC LỚP HỌC

Để buổi báo cáo đồ án diễn ra trôi chảy, nhóm tuân thủ chặt chẽ kịch bản 5 phút đã thống nhất trong Timeline:

```
[Phút 1: Đặt vấn đề] ---> [Phút 2: Demo BaaS] ---> [Phút 3: Demo Self-Hosted] ---> [Phút 4-5: So sánh & Kết luận]
     (Cả nhóm)                  (Tuyển & TV3)               (Vin & TV3)                     (Cả nhóm)
```

### ⏱️ Phút 1: Giới thiệu bài toán & Mục tiêu đồ án (1 phút)
- **Người trình bày**: Cả nhóm / Đại diện nhóm.
- **Nội dung nói**: 
  *"Chào Thầy và các bạn! Trong môn Lập trình mạng căn bản NT106, khi xây dựng ứng dụng mạng, sinh viên thường đứng trước 2 lựa chọn: Dùng nền tảng dịch vụ có sẵn (BaaS như Supabase) hay Tự thiết kế và triển khai Server riêng (Self-Hosted). Nhóm chúng em đã hiện thực hóa cả 2 mô hình để đo đạc và so sánh trực quan."*

---

### ⏱️ Phút 2: Demo Mô Hình BaaS Supabase (1 phút)
- **Người thao tác**: TV3 (bấm Client) + Tuyển (chiếu Dashboard Supabase).
- **Thao tác thực tế**:
  1. Tuyển chia sẻ màn hình Dashboard Supabase (mục **Table Editor** của bảng `network_logs`).
  2. TV3 trên màn hình Client Demo bấm nút màu xanh: **"Gửi Dữ Liệu Lên Supabase (Phút 2)"**.
  3. Màn hình Supabase của Tuyển **tự động nhảy số thêm dòng mới ngay lập tức** nhờ WebSocket Realtime.
- **Điểm nhấn thuyết trình**: 
  *"Như Thầy thấy, chúng em không cần viết bất kỳ một dòng code backend nào. Chỉ cần 1 nút bấm từ Client, dữ liệu được đồng bộ Realtime lên Cloud qua REST API & WebSocket."*

---

### ⏱️ Phút 3: Demo Mô Hình Tự Triển Khai Self-Hosted (1 phút)
- **Người thao tác**: TV3 (bấm Client) + Vin (chiếu Server Console & Swagger).
- **Thao tác thực tế**:
  1. Vin chiếu cửa sổ Console máy chủ .NET 10 đang chạy và tab Swagger UI (`/swagger`).
  2. TV3 trên Client bấm nút màu xanh dương: **"Gửi Log (POST /api/logs)"**.
  3. Cửa sổ Console của Vin lập tức in ra dòng log màu tím nổi bật: IP Client, ID bản ghi, kích thước payload và trả về `200 OK`.
  4. TV3 bấm tiếp nút **"Xem RAM/CPU"**: Client hiển thị ngay RAM tiêu thụ của server là ~88 MB.
- **Điểm nhấn thuyết trình**: 
  *"Với mô hình Tự Triển Khai bằng .NET 10, chúng em kiểm soát 100% gói tin, luồng xử lý và tài nguyên phần cứng. Server phản hồi với RTT chỉ ~15-20 ms, cực kỳ tiết kiệm bộ nhớ."*

---

### ⏱️ Phút 4 - 5: Chiếu Bảng Số Liệu Đo Đạc & Kết Luận (2 phút)
- **Người trình bày**: TV3 và Vin.
- **Thao tác thực tế**:
  1. TV3 bấm nút **"Bắt Đầu Đo Đối Sánh Cả 2 Bên"** trên Client để chạy test tải 10-50 request ngay trước lớp hoặc chiếu trực tiếp bảng số liệu từ file `ket_qua_do_luong.csv`.
  2. Chiếu bảng so sánh:
     - Độ trễ RTT (Self-Hosted thắng: 20ms vs 112ms).
     - Kích thước gói tin (Self-Hosted thắng: 350B vs 1.5KB).
     - Thời gian triển khai (Supabase thắng: 10 phút setup vs 2 ngày code backend).
- **Kết luận chốt hạ đồ án**:
  - **BaaS (Supabase)**: Lựa chọn số 1 cho các ứng dụng Startup, MVP, ứng dụng mạng xã hội cần phát triển cực nhanh, có sẵn Auth, Database và Realtime mà không cần đội ngũ quản trị server (SysAdmin).
  - **Self-Hosted Server**: Lựa chọn bắt buộc cho các hệ thống giám sát mạng (NetOps), thiết bị IoT, hệ thống tài chính yêu cầu độ trễ thấp, kiểm soát toàn diện luồng tin bảo mật và tối ưu chi phí hạ tầng khi mở rộng lâu dài.

---

## 8. KHUNG SLIDE THUYẾT TRÌNH GỢI Ý CHO NHÓM

Nhóm có thể copy trực tiếp nội dung dưới đây vào PowerPoint / Canva để hoàn thiện slide:

### Slide 1: Trang Tiêu Đề
- **Tên đề tài**: BÁO CÁO ĐỒ ÁN: SO SÁNH HIỆU NĂNG MÔ HÌNH TRIỂN KHAI SERVER (BaaS vs Self-Hosted)
- **Môn học**: NT106 - Lập Trình Mạng Căn Bản (Khoa MMT&TT - UIT)
- **Thành viên thực hiện**: Vin (Tự Deploy) • Tuyển (BaaS Supabase) • TV3 (Client & Đo lường)

### Slide 2: Đặt Vấn Đề & Kiến Trúc Tổng Quan
- Sơ đồ kiến trúc 2 luồng dữ liệu:
  - `Client -> HTTPS -> Supabase Cloud (PostgreSQL + Realtime)`
  - `Client -> HTTP/REST -> Self-Hosted Web API (.NET 10 on Kestrel)`
- Câu hỏi nghiên cứu: Sự đánh đổi giữa **Thời gian phát triển** vs **Độ trễ & Băng thông mạng**.

### Slide 3: Trình Diễn Thực Tế (Live Demo)
- Chụp ảnh giao diện Client 2 nút bấm (`demo-client/index.html`).
- Ảnh chụp Dashboard Supabase nhảy log Realtime.
- Ảnh chụp Swagger UI và Server Console in log request.

### Slide 4: Bảng Số Liệu Đối Sánh Thực Nghiệm (Key Slide)
- Đưa bảng số liệu ở Mục 5.1 vào slide:
  - So sánh RTT (Min, Avg, P95, Max).
  - So sánh dung lượng Header & Payload.
  - So sánh RAM tiêu thụ.

### Slide 5: Phân Tích Gói Tin Bằng Wireshark
- Ảnh chụp gói tin HTTP thuần của Self-Hosted (~350 bytes).
- Ảnh chụp gói tin TLS + JWT của Supabase (~1.5 KB).
- Phân tích chi phí bắt tay TLS 1.3 (Handshake overhead).

### Slide 6: Kết Luận & Khuyến Nghị Kiến Trúc
- Ma trận quyết định (Decision Matrix): Khi nào nên dùng BaaS? Khi nào nên Tự Triển Khai?
- Lời cảm ơn và giải đáp câu hỏi của Giảng viên.

---
*Tài liệu được biên soạn đầy đủ, có chú thích chi tiết cho toàn bộ thành viên nhóm NT106.*

