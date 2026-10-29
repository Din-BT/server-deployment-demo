# NT106 - Self-Hosted Web API Server (.NET 10)

> **Môn học**: NT106 - Lập trình mạng căn bản (UIT - ĐHQG TP.HCM)  
> **Thành viên phụ trách**: Vin (TV1 - Tự Deploy Server)  
> **Nhiệm vụ**: Xây dựng Web API tối giản, deploy lên Cloud (Render/Railway), chuẩn bị kịch bản Demo trước lớp và so sánh với BaaS (Supabase).

---

## 📌 1. Danh sách Endpoint API

| Method | Endpoint | Mô tả | Ứng dụng trong Đồ án |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Tự động chuyển hướng về `/swagger` | Tiện lợi cho người chấm mở link |
| `GET` | `/swagger` | Giao diện Swagger UI tương tác | **Kịch bản Demo Phút 3** trước lớp |
| `GET` | `/scalar/v1` | Giao diện tài liệu Scalar UI hiện đại | Xem chi tiết schema gói tin |
| `GET` | `/api/ping` | Kiểm tra kết nối mạng (Echo / Ping) | TV3 đo Round-Trip Time (RTT) |
| `POST` | `/api/logs` | Gửi bản tin log lên server | Nhận dữ liệu từ Client & in console |
| `GET` | `/api/logs` | Xem danh sách các log đã nhận | Kiểm tra dữ liệu đã lưu trữ |
| `DELETE`| `/api/logs` | Xóa sạch bộ nhớ log | Reset trước khi chạy test tải |
| `GET` | `/api/metrics` | Thống kê RAM, CPU, Uptime, Request count | **Nhiệm vụ Ngày 3**: Đưa số liệu vào slide |
| `GET` | `/health` | Health Check siêu nhẹ | Chống sleep server trên Render Free Tier |

---

## 🚀 2. Cách chạy nhanh tại máy cục bộ (Local)

### Cách 1: Chạy bằng file script có sẵn (Khuyên dùng)
- Double click vào file `scripts/run-local.bat` hoặc mở PowerShell chạy:
  ```powershell
  .\scripts\run-local.ps1
  ```
- Mở trình duyệt truy cập: `http://localhost:5000/swagger`

### Cách 2: Chạy bằng lệnh dotnet CLI
```bash
cd self-hosted-server
dotnet run
```

---

## 🛠️ 3. Các công cụ hỗ trợ kèm theo trong thư mục `scripts/`

1. `run-local.bat`: Chạy server local dự phòng (Nhiệm vụ Ngày 4).
2. `start-tunnel.bat`: Kích hoạt ngrok hoặc Cloudflare Tunnel để đưa server local ra internet khi mạng trường có vấn đề (Nhiệm vụ Ngày 2 & Ngày 4).
3. `load-test.bat`: Bắn 50 - 100 requests để đo Latency (Min, Max, Avg) và đo RAM/CPU tiêu thụ (Nhiệm vụ Ngày 3).
4. `keep-alive.bat`: Bot tự động ping 10 phút/lần chống Render Free Tier bị sleep (Nhiệm vụ Ngày 4).

---

## 🌐 4. Triển khai lên Cloud (Render / Railway)

- Đã tích hợp sẵn file `Dockerfile` chuẩn multi-stage build cho .NET 10.
- Đã tích hợp sẵn file cấu hình Render Blueprint `render.yaml` ở thư mục gốc.
- Xem tài liệu hướng dẫn từng bước chi tiết tại: `docs/HUONG_DAN_TU_DEPLOY_SERVER.md`.
