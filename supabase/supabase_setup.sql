-- Chạy toàn bộ file này trong Supabase Dashboard > SQL Editor > New query > Run
-- Ngày 1: tạo bảng network_logs + cấu hình RLS. Ngày 2: bật Realtime.

-- 1. Bảng lưu bản tin mạng
create table if not exists public.network_logs (
  id           bigint generated always as identity primary key,
  created_at   timestamptz not null default now(),  -- giờ server Supabase nhận bản tin
  sent_at      timestamptz,                         -- giờ client gửi (để đo độ trễ)
  client_id    text,
  message      text,
  payload_size integer                              -- kích thước bản tin (byte)
);

-- 2. Bật Row Level Security (bắt buộc, mặc định chặn hết)
alter table public.network_logs enable row level security;

-- 3. Quyền truy cập cho demo: cho phép khoá anon được thêm và xem
--    Không cho sửa hoặc xoá. Khi dùng thật phải siết chặt hơn.
drop policy if exists "anon_insert_logs" on public.network_logs;
create policy "anon_insert_logs"
  on public.network_logs for insert
  to anon
  with check (true);

drop policy if exists "anon_select_logs" on public.network_logs;
create policy "anon_select_logs"
  on public.network_logs for select
  to anon
  using (true);

-- 4. Bật Realtime cho bảng (Ngày 2)
alter publication supabase_realtime add table public.network_logs;
