# Kết quả đo phần Supabase (BaaS) — Tuyển

Điền các ô `[__]` sau khi chạy đo, rồi gửi cho Vuongnl để đưa vào bảng so sánh trên slide.

- Ngày đo: [__]    Máy / mạng: [__] (ví dụ: laptop, Wi-Fi nhà, Cần Thơ)
- Region Supabase: [__] (ví dụ: Singapore)

## 1. Độ trễ (đơn vị ms)

| Phép đo | Lệnh | Request đầu (lạnh) | Trung bình | Trung vị | p95 | Max |
|---|---|---|---|---|---|---|
| Ghi, 1 luồng, 50 request | `benchmark.py -n 50` | [__] | [__] | [__] | [__] | [__] |
| Đọc, 1 luồng, 50 request | `benchmark.py -n 50` | [__] | [__] | [__] | [__] | [__] |
| Ghi, tải 100 request, 5 luồng | `benchmark.py -n 100 -c 5` | [__] | [__] | [__] | [__] | [__] |
| Đọc, tải 100 request, 5 luồng | `benchmark.py -n 100 -c 5` | [__] | [__] | [__] | [__] | [__] |
| Độ trễ Realtime (gửi đến nhận) | `realtime_listener.py` + `push_log.py -n 50` | không áp dụng | [__] | không áp dụng | không áp dụng | [__] |

Thông lượng khi tải: ghi [__] request/s, đọc [__] request/s. Số request lỗi: [__].

## 2. Kích thước và độ phức tạp

| Tiêu chí | Giá trị |
|---|---|
| Kích thước bản tin (cột `payload_size`) | 110 byte |
| Kích thước thật trên đường truyền (Wireshark) | [__] byte |
| Thời gian setup (tạo project đến ghi thành công lần đầu) | [__] phút |
| Số bước cấu hình | 4: tạo project, chạy SQL, lấy URL và khoá, chạy script |
| Số dòng mã phía server phải viết | 0 |

## 3. Bảo mật

| Tiêu chí | Supabase |
|---|---|
| Truyền qua HTTPS/TLS | Có, mặc định (xác nhận bằng Wireshark: [__]) |
| Phân quyền | Row Level Security trên từng bảng; bảng mới không có policy thì bị chặn hết |
| Khoá đặt trong client | Có (khoá publishable/anon), nên RLS là lớp bảo vệ chính |
| Phải tự vá lỗi, quản lý server | Không |
| Rủi ro đã gặp | Policy demo mở cho `anon` đọc và ghi, cần siết khi dùng thật |

## 4. Nhận xét ngắn (viết lại theo số liệu thật)

- Ưu điểm: setup nhanh ([__] phút), không phải viết hay vận hành server, có sẵn Realtime.
- Hạn chế: độ trễ phụ thuộc region ([__] ms), phụ thuộc nhà cung cấp, bảo mật dựa hoàn toàn vào việc cấu hình RLS đúng.
- Kết luận cho phần BaaS: [__] (so với tự deploy của Vin: [__]).
