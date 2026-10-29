# Phần của Tuyển: BaaS với Supabase (NT106)

Mục tiêu: dựng phía Supabase để so sánh với tự deploy (Vin), và cung cấp số liệu cho Vuongnl tổng hợp.

## Ngày 1: Khởi tạo

1. Vào https://supabase.com, đăng ký và tạo project mới (ghi lại **thời điểm bắt đầu** để tính thời gian setup).
2. Chọn region gần nhất (Singapore) và đặt mật khẩu database.
3. Mở **SQL Editor**, dán toàn bộ `supabase_setup.sql`, bấm Run. File này tạo bảng `network_logs`, bật RLS, tạo policy cho khoá `anon` và bật Realtime.
4. Vào **Project Settings > API**, chép hai giá trị:
   - Project URL (`https://xxxx.supabase.co`)
   - `anon` public key
5. Kiểm tra: vào **Table Editor**, thấy bảng `network_logs` có nhãn RLS đã bật.

## Ngày 2: Đẩy dữ liệu và Realtime

```bash
export SUPABASE_URL="https://xxxx.supabase.co"
export SUPABASE_ANON_KEY="eyJ..."

# Terminal 1: nghe Realtime
pip install websockets
python realtime_listener.py

# Terminal 2: đẩy bản tin
python push_log.py -n 5
```

Kết quả mong đợi: Terminal 1 in ra từng bản tin kèm độ trễ, và bảng `network_logs` trên Dashboard có thêm dòng mới.
Test từ xa: đưa `push_log.py` cho Vuongnl hoặc Vin chạy từ máy khác, kiểm tra dữ liệu vẫn về được.

## Ngày 3: Đo lường (làm cùng Vuongnl)

| Việc | Lệnh hoặc cách làm | Ghi lại |
|---|---|---|
| RTT khi ghi dữ liệu | `python push_log.py -n 100 --delay 0.1` | min, trung bình, p95, max (ms) |
| Độ trễ Realtime | chạy `realtime_listener.py` và `push_log.py -n 50` trên cùng máy | trung bình, max (ms) |
| Kích thước bản tin | cột `payload_size`; Wireshark lọc theo `tls` hoặc tên miền Supabase | byte |
| Thời gian setup | từ lúc bấm tạo project đến khi chạy được `push_log.py` | phút |
| Bảo mật | xem bảng dưới | có hoặc không |

**Bảng ghi nhận bảo mật Supabase** (điền khi làm):

| Tiêu chí | Supabase |
|---|---|
| Truyền qua HTTPS/TLS | Có (mặc định) |
| Cần cấu hình RLS | Có, bảng mới không có policy thì bị chặn hết |
| Khoá anon bị lộ trong client | Có, nên RLS là lớp bảo vệ duy nhất |
| Cần tự quản lý server, vá lỗi | Không |

## Ngày 4: Tổng duyệt

- Mở sẵn tab **Table Editor** của `network_logs` và tab **Realtime** trong Dashboard.
- Kiểm tra mạng ổn định, chạy thử `push_log.py -n 3` để chắc dữ liệu hiện ngay.
- Chuẩn bị sẵn terminal đã `export` biến môi trường.
- Dự phòng: quay video đoạn demo Phút 2 phòng khi mất mạng.

## Phút 2 trong kịch bản demo (Demo Supabase)

1. Mở Dashboard Supabase ở màn hình chia sẻ.
2. Chạy `python push_log.py -n 3` (hoặc bấm nút gửi trên client của Vuongnl).
3. Chỉ vào bảng `network_logs`: dòng mới xuất hiện ngay, nói rõ "không phải dựng server nào cả".

## Lưu ý

- Chưa chạy thử với project Supabase thật, vì không có tài khoản của bạn. `push_log.py` đã chạy thử với server giả; `realtime_listener.py` mới kiểm tra cú pháp. Nếu listener không nhận được tin, kiểm tra lại bước `alter publication supabase_realtime add table` đã chạy chưa.
- Không đưa `anon key` và URL thật lên repo GitHub chung; dùng biến môi trường như trên.
- Policy trong `supabase_setup.sql` mở cho `anon` đọc và ghi, chỉ phù hợp để demo.
