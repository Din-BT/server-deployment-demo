#!/usr/bin/env python3
"""Đo hiệu năng Supabase REST cho Ngày 3: RTT ghi (POST), RTT đọc (GET), tải nhiều request.

Khác push_log.py: dùng kết nối HTTPS giữ nguyên (keep-alive), nên tách được
thời gian bắt tay TLS (request đầu, "lạnh") khỏi thời gian request thật ("ấm").

Không cần cài thư viện. Cách dùng:
    export SUPABASE_URL="https://xxxx.supabase.co"
    export SUPABASE_ANON_KEY="sb_publishable_..."
    python benchmark.py                          # 50 ghi + 50 đọc
    python benchmark.py -n 100 -c 5 --csv ket_qua.csv   # 100 request, 5 luồng song song

Các dòng ghi dùng client_id = "benchmark". Xoá sau khi đo (Dashboard > SQL Editor):
    delete from public.network_logs where client_id = 'benchmark';
"""
import argparse
import csv
import http.client
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlparse

OK_STATUS = (200, 201, 204)


def percentile(values, p):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round(p / 100 * (len(ordered) - 1)))]


def make_connection(parsed):
    if parsed.scheme == "https":
        return http.client.HTTPSConnection(parsed.netloc, timeout=20)
    return http.client.HTTPConnection(parsed.netloc, timeout=20)


def worker(parsed, headers, op, count, start_index):
    """Một luồng: giữ một kết nối, gửi `count` request, trả về danh sách kết quả."""
    connection = make_connection(parsed)
    results = []
    for k in range(count):
        index = start_index + k
        if op == "write":
            row = {
                "client_id": "benchmark",
                "message": f"benchmark #{index}",
                "sent_at": datetime.now(timezone.utc).isoformat(),
            }
            row["payload_size"] = len(json.dumps(row).encode("utf-8"))
            body = json.dumps(row).encode("utf-8")
            method, path = "POST", "/rest/v1/network_logs"
            request_headers = {**headers, "Content-Type": "application/json", "Prefer": "return=minimal"}
        else:
            body, method = None, "GET"
            path = "/rest/v1/network_logs?select=id,message&order=id.desc&limit=10"
            request_headers = headers

        start = time.perf_counter()
        try:
            connection.request(method, path, body=body, headers=request_headers)
            response = connection.getresponse()
            response.read()
            status = response.status
        except Exception as error:  # mất kết nối, hết thời gian chờ...
            status = f"ERR:{type(error).__name__}"
            connection.close()
            connection = make_connection(parsed)
        elapsed_ms = (time.perf_counter() - start) * 1000
        results.append({"op": op, "index": index, "ms": round(elapsed_ms, 1), "status": status})
    connection.close()
    return results


def run_phase(parsed, headers, op, count, concurrency):
    """Chạy một pha (ghi hoặc đọc), chia đều `count` request cho `concurrency` luồng."""
    shares = [count // concurrency + (1 if i < count % concurrency else 0) for i in range(concurrency)]
    starts = [sum(shares[:i]) + 1 for i in range(concurrency)]
    begin = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [
            pool.submit(worker, parsed, headers, op, share, start)
            for share, start in zip(shares, starts)
            if share > 0
        ]
        results = [row for future in futures for row in future.result()]
    wall = time.perf_counter() - begin
    results.sort(key=lambda row: row["index"])
    return results, wall


def summarize(label, results, wall):
    good = [row["ms"] for row in results if row["status"] in OK_STATUS]
    errors = len(results) - len(good)
    print(f"\n=== {label} ===")
    print(f"Thành công: {len(good)}/{len(results)}  Lỗi: {errors}  "
          f"Tổng thời gian: {wall:.2f} s  Thông lượng: {len(results) / wall:.1f} request/s")
    if not good:
        return
    print(f"Request đầu (có bắt tay TLS): {results[0]['ms']:.1f} ms")
    warm = [row["ms"] for row in results[1:] if row["status"] in OK_STATUS] or good
    spread = statistics.stdev(warm) if len(warm) > 1 else 0.0
    print(f"Các request sau (ms): min {min(warm):.1f} | trung bình {statistics.mean(warm):.1f} | "
          f"trung vị {statistics.median(warm):.1f} | p95 {percentile(warm, 95):.1f} | "
          f"max {max(warm):.1f} | độ lệch chuẩn {spread:.1f}")


def main():
    parser = argparse.ArgumentParser(description="Đo hiệu năng Supabase REST")
    parser.add_argument("-n", "--count", type=int, default=50, help="số request mỗi pha (ghi, đọc)")
    parser.add_argument("-c", "--concurrency", type=int, default=1, help="số luồng song song")
    parser.add_argument("--csv", help="lưu từng request ra file CSV")
    args = parser.parse_args()
    if args.count < 1 or args.concurrency < 1:
        sys.exit("--count và --concurrency phải >= 1")

    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    api_key = os.environ.get("SUPABASE_ANON_KEY", "")
    if not base_url or not api_key:
        sys.exit("Thiếu biến môi trường SUPABASE_URL hoặc SUPABASE_ANON_KEY")
    if not api_key.isascii() or " " in api_key:
        sys.exit("SUPABASE_ANON_KEY không hợp lệ: hãy dán khoá thật từ Project Settings > API Keys")

    parsed = urlparse(base_url)
    headers = {"apikey": api_key, "Authorization": f"Bearer {api_key}"}
    concurrency = min(args.concurrency, args.count)
    print(f"Đo {args.count} request ghi + {args.count} request đọc, {concurrency} luồng, tới {parsed.netloc}")

    all_rows = []
    for op, label in (("write", "GHI (POST)"), ("read", "ĐỌC (GET)")):
        results, wall = run_phase(parsed, headers, op, args.count, concurrency)
        summarize(label, results, wall)
        all_rows.extend(results)

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["op", "index", "ms", "status"])
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"\nĐã lưu {len(all_rows)} dòng vào {args.csv}")


if __name__ == "__main__":
    main()
