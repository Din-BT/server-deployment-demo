# Ứng Dụng Client Demo & Bộ Công Cụ Đo Lường - NT106

> **Môn học**: NT106 - Lập trình mạng căn bản (UIT - ĐHQG TP.HCM)  
> **Thành viên phụ trách**: TV3 (Client & Đo lường)  
> **Mục tiêu**: Cung cấp Client có giao diện trực quan phục vụ kịch bản thuyết trình Demo 5 phút trước lớp (Phút 2 & Phút 3), đồng thời cung cấp bộ công cụ đo lường RTT, kích thước gói tin và so sánh hiệu năng giữa hai mô hình **BaaS (Supabase)** và **Self-Hosted (.NET 10)**.

---

## 📂 Danh mục File trong Thư mục `demo-client/`

| File | Định dạng | Chức năng chính |
| :--- | :---: | :--- |
| **`index.html`** | HTML5 | Giao diện Web Client trực quan, tích hợp 2 nút bấm gọi 2 server phục vụ demo. |
| **`style.css`** | CSS3 | Giao diện hiện đại, tối ưu cho màn hình trình chiếu máy chiếu tại lớp học. |
| **`app.js`** | JavaScript | Điều khiển Fetch API, tính toán RTT, timer chính xác cao (`performance.now()`), xuất file CSV. |
| **`serve.py`** | Python | Khởi động máy chủ cục bộ (port 8080) và tự động mở trình duyệt web. |
| **`run-client.bat`** | Windows Batch | **Click đúp để chạy nhanh** toàn bộ Client trên máy Windows. |
| **`measure.py`** | Python CLI | Kịch bản tự động đo tải 50-100 request đối sánh 2 server, tính Min/Avg/P95/Max RTT. |
| **`measure.bat`** | Windows Batch | **Click đúp để chạy nhanh** bộ đo lường CLI không cần mở trình duyệt. |
| **`NT106_Server_Comparison.postman_collection.json`** | JSON | Bộ test API chuẩn hóa để import vào Postman. |

---

## 🚀 1. Hướng Dẫn Sử Dụng Client Demo Trực Tiếp (Phút 2 & Phút 3)

### Cách khởi động nhanh:
Chỉ cần **click đúp vào file `run-client.bat`** (hoặc mở Terminal gõ `python serve.py`).  
Trình duyệt sẽ tự động mở trang web tại địa chỉ: `http://localhost:8080`.

### Kịch bản thao tác khi Demo trước lớp:
1. **Kiểm tra kết nối**: Đảm bảo server Self-Hosted đang chạy (`http://localhost:5000` hoặc link public) và điền Supabase URL/Key vào phần **Cấu hình**.
2. **Demo Phút 2 (Supabase - BaaS)**:
   - Bấm nút **"Gửi Dữ Liệu Lên Supabase (Phút 2)"**.
   - Quan sát Client báo mã `201 Created` và thời gian RTT.
   - Chiếu màn hình Dashboard Supabase (Table Editor): Dữ liệu nhảy vào ngay lập tức qua WebSocket/Realtime mà không cần bất kỳ server trung gian nào.
3. **Demo Phút 3 (Self-Hosted Server)**:
   - Bấm nút **"Gửi Log (POST /api/logs)"**.
   - Quan sát Server Console của Vin: In ra thông tin request, địa chỉ IP và mã `200 OK`.
   - Bấm nút **"Xem RAM/CPU"**: Client lấy ngay chỉ số tiêu thụ tài nguyên thực tế (`/api/metrics`) để chứng minh server .NET 10 siêu nhẹ chỉ chiếm ~25-40 MB RAM.

---

## 📊 2. Hướng Dẫn Đo Lường Hiệu Năng Đối Sánh (Nhiệm vụ Ngày 3)

### Cách 1: Đo trực tiếp trên Web GUI Client
- Tại mục **"3. Bộ Đo Lường Đối Sánh Hiệu Năng Tự Động"**, chọn số lượng request (10, 50, hoặc 100).
- Bấm **"Bắt Đầu Đo Đối Sánh Cả 2 Bên"**.
- Bảng tổng hợp sẽ tự động hiển thị:
  - RTT Tối thiểu (Min)
  - RTT Trung bình (Avg)
  - RTT P95 (Độ biến động mạng / Jitter)
  - RTT Tối đa (Max)
  - Tỷ lệ thành công (%)
- Bấm nút **"📥 Xuất Dữ Liệu Ra File CSV"** để tải file số liệu về vẽ biểu đồ cho Slide.

### Cách 2: Đo tự động bằng Python CLI (`measure.py`)
Mở PowerShell/CMD hoặc click đúp file `measure.bat`:
```bash
python measure.py --self-url "http://localhost:5000" -n 50
```
Script sẽ tự động:
- Bắn 50 request đến Self-Hosted.
- Bắn 50 request đến Supabase (nếu có biến môi trường `SUPABASE_URL` và `SUPABASE_ANON_KEY`).
- In bảng so sánh trực quan ra màn hình terminal và tự động xuất ra 2 file: `ket_qua_do_luong.csv` và `ket_qua_do_luong.json`.

---

## 🔍 3. Hướng Dẫn Đo Bằng Wireshark & Postman (Nhiệm vụ Ngày 2 & Ngày 3)

### Sử dụng Postman:
1. Mở Postman -> Chọn **Import** -> Chọn file `NT106_Server_Comparison.postman_collection.json`.
2. Chỉnh sửa biến `SELF_HOSTED_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY` trong tab Variables của Collection.
3. Sử dụng công cụ **Collection Runner** để chạy tự động kiểm thử toàn bộ requests.

### Phân tích gói tin bằng Wireshark:
1. Mở Wireshark, chọn Card mạng đang hoạt động (Wi-Fi hoặc Ethernet, hoặc Adapter for loopback traffic nếu test local).
2. Bộ lọc (Display Filter):
   - Bắt gói tin Self-Hosted Local: `tcp.port == 5000 and http`
   - Bắt gói tin Supabase: `tls and (ip.addr == <IP_Supabase>)` hoặc `dns contains "supabase"`
3. Quan sát và phân tích:
   - **Gói tin Self-Hosted**: Dùng HTTP thuần (hoặc TLS tùy môi trường), Header ngắn gọn (~250-350 bytes), không có token phức tạp.
   - **Gói tin Supabase**: Bắt buộc TLS 1.3, có Header `apikey` và `Authorization: Bearer <JWT Token>` dài (~1.2 - 1.5 KB), làm tăng kích thước gói tin gửi đi trên đường truyền.

