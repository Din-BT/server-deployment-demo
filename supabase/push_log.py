#!/usr/bin/env python3
"""Đẩy bản tin lên Supabase qua REST API và đo thời gian phản hồi (RTT).

Không cần cài thêm thư viện (chỉ dùng thư viện chuẩn của Python).

Cách dùng:
    export SUPABASE_URL="https://xxxx.supabase.co"
    export SUPABASE_ANON_KEY="eyJ..."
    python push_log.py                       # gửi 1 bản tin
    python push_log.py -n 50 --delay 0.2     # gửi 50 bản tin, đo RTT
"""
import argparse
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


def percentile(values, p):
    ordered = sorted(values)
    index = min(len(ordered) - 1, round(p / 100 * (len(ordered) - 1)))
    return ordered[index]


def main():
    parser = argparse.ArgumentParser(description="Đẩy bản tin lên Supabase và đo RTT")
    parser.add_argument("-n", "--count", type=int, default=1, help="số bản tin cần gửi")
    parser.add_argument("-m", "--message", default="hello from Tuyen", help="nội dung bản tin")
    parser.add_argument("--client-id", default="tuyen-script", help="tên client")
    parser.add_argument("--delay", type=float, default=0.5, help="giây nghỉ giữa các lần gửi")
    args = parser.parse_args()

    base_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    api_key = os.environ.get("SUPABASE_ANON_KEY", "")
    if not base_url or not api_key:
        sys.exit("Thiếu biến môi trường SUPABASE_URL hoặc SUPABASE_ANON_KEY")

    endpoint = f"{base_url}/rest/v1/network_logs"
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    rtts = []
    failures = 0
    for i in range(1, args.count + 1):
        row = {
            "client_id": args.client_id,
            "message": f"{args.message} #{i}",
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
        row["payload_size"] = len(json.dumps(row).encode("utf-8"))
        data = json.dumps(row).encode("utf-8")

        request = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                status = response.status
        except urllib.error.HTTPError as error:
            failures += 1
            print(f"[{i}] LỖI {error.code}: {error.read().decode('utf-8', 'replace')}")
            continue
        except urllib.error.URLError as error:
            failures += 1
            print(f"[{i}] LỖI kết nối: {error.reason}")
            continue

        rtt_ms = (time.perf_counter() - start) * 1000
        rtts.append(rtt_ms)
        print(f"[{i}] HTTP {status}  {rtt_ms:7.1f} ms  {row['payload_size']} byte")
        if i < args.count:
            time.sleep(args.delay)

    print("\n--- Tổng kết ---")
    print(f"Thành công: {len(rtts)}  Thất bại: {failures}")
    if rtts:
        print(
            f"RTT (ms): min {min(rtts):.1f} | trung bình {statistics.mean(rtts):.1f} | "
            f"p95 {percentile(rtts, 95):.1f} | max {max(rtts):.1f}"
        )


if __name__ == "__main__":
    main()
