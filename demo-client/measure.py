#!/usr/bin/env python3
"""
NT106 - LẬP TRÌNH MẠNG CĂN BẢN (UIT - ĐHQG TP.HCM)
Kịch bản đo lường hiệu năng đối sánh (Benchmark Suite):
- Mô hình 1: Self-Hosted Server (.NET 10 Web API - Vin)
- Mô hình 2: Backend-as-a-Service (Supabase REST API - Tuyển)

Nhiệm vụ: TV3 (Client & Đo lường) - Ngày 3 & Phút 4-5 kịch bản Demo
Chỉ số đo đạc:
1. RTT (Round-Trip Time): Min, Avg, Median, P95, Max
2. Kích thước bản tin (Payload Size & Header Overheads)
3. Độ ổn định & Tỷ lệ thành công (Success Rate %)
4. Tài nguyên hệ thống tiêu thụ (RAM, CPU qua /api/metrics)
"""

import argparse
import csv
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

# Đảm bảo in tiếng Việt có dấu chuẩn xác trên console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def percentile(data, p):
    """Tính phân vị thứ p (0-100) của mảng dữ liệu đã sắp xếp."""
    if not data:
        return 0.0
    s = sorted(data)
    idx = min(len(s) - 1, round((p / 100.0) * (len(s) - 1)))
    return s[idx]


def test_self_hosted(base_url, count=50, delay=0.05):
    """
    Gửi liên tiếp các bản tin POST đến Web API Self-Hosted và đo độ trễ RTT.
    Endpoint: POST /api/logs
    """
    endpoint = f"{base_url.rstrip('/')}/api/logs"
    print(f"\n[1/3] Đang đo Self-Hosted Server ({endpoint})...")
    
    rtts = []
    successes = 0
    total_bytes_sent = 0

    for i in range(1, count + 1):
        payload = {
            "deviceId": "Benchmark-Script-TV3",
            "level": "INFO",
            "message": f"Benchmark request #{i} at {time.time()}",
            "metadata": {
                "iteration": str(i),
                "sender": "measure.py"
            }
        }
        body_bytes = json.dumps(payload).encode("utf-8")
        total_bytes_sent += len(body_bytes)

        req = urllib.request.Request(
            endpoint,
            data=body_bytes,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "NT106-Measure-Client/1.0"
            },
            method="POST"
        )

        t_start = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.status
                resp.read()
                t_end = time.perf_counter()
                rtt_ms = (t_end - t_start) * 1000.0
                rtts.append(rtt_ms)
                if status in (200, 201):
                    successes += 1
        except Exception as e:
            t_end = time.perf_counter()
            rtt_ms = (t_end - t_start) * 1000.0
            print(f"  [LỖI] Request #{i}: {e}")

        if delay > 0:
            time.sleep(delay)

    # Lấy metrics RAM/CPU từ server
    metrics_info = {}
    try:
        req_m = urllib.request.Request(f"{base_url.rstrip('/')}/api/metrics")
        with urllib.request.urlopen(req_m, timeout=5) as resp:
            metrics_info = json.loads(resp.read().decode("utf-8"))
    except Exception:
        pass

    return {
        "target": "Self-Hosted (.NET 10)",
        "count": count,
        "success": successes,
        "success_rate": round((successes / count) * 100, 1),
        "rtts": rtts,
        "min": round(min(rtts), 2) if rtts else 0,
        "avg": round(statistics.mean(rtts), 2) if rtts else 0,
        "median": round(statistics.median(rtts), 2) if rtts else 0,
        "p95": round(percentile(rtts, 95), 2) if rtts else 0,
        "max": round(max(rtts), 2) if rtts else 0,
        "avg_body_size": round(total_bytes_sent / count, 1),
        "metrics": metrics_info
    }


def test_supabase(url, anon_key, count=50, delay=0.05):
    """
    Gửi liên tiếp các bản tin POST đến Supabase REST API và đo độ trễ RTT.
    Endpoint: POST /rest/v1/network_logs
    """
    if not url or not anon_key:
        print("\n[2/3] Bỏ qua Supabase do chưa có SUPABASE_URL hoặc SUPABASE_ANON_KEY.")
        return None

    endpoint = f"{url.rstrip('/')}/rest/v1/network_logs"
    print(f"\n[2/3] Đang đo Supabase BaaS ({endpoint})...")

    rtts = []
    successes = 0
    total_bytes_sent = 0

    for i in range(1, count + 1):
        payload = {
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "client_id": "benchmark-tv3",
            "message": f"Benchmark request #{i} at {time.time()}",
            "payload_size": 120
        }
        body_bytes = json.dumps(payload).encode("utf-8")
        total_bytes_sent += len(body_bytes)

        req = urllib.request.Request(
            endpoint,
            data=body_bytes,
            headers={
                "apikey": anon_key,
                "Authorization": f"Bearer {anon_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
                "User-Agent": "NT106-Measure-Client/1.0"
            },
            method="POST"
        )

        t_start = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.status
                resp.read()
                t_end = time.perf_counter()
                rtt_ms = (t_end - t_start) * 1000.0
                rtts.append(rtt_ms)
                if status in (200, 201, 204):
                    successes += 1
        except Exception as e:
            t_end = time.perf_counter()
            rtt_ms = (t_end - t_start) * 1000.0
            print(f"  [LỖI] Request #{i}: {e}")

        if delay > 0:
            time.sleep(delay)

    return {
        "target": "BaaS (Supabase)",
        "count": count,
        "success": successes,
        "success_rate": round((successes / count) * 100, 1),
        "rtts": rtts,
        "min": round(min(rtts), 2) if rtts else 0,
        "avg": round(statistics.mean(rtts), 2) if rtts else 0,
        "median": round(statistics.median(rtts), 2) if rtts else 0,
        "p95": round(percentile(rtts, 95), 2) if rtts else 0,
        "max": round(max(rtts), 2) if rtts else 0,
        "avg_body_size": round(total_bytes_sent / count, 1)
    }


def print_comparison_table(res_self, res_supa):
    """In bảng so sánh hiệu năng trực quan ra màn hình Console."""
    print("\n" + "=" * 80)
    print("      BẢNG TỔNG HỢP KẾT QUẢ ĐO LƯỜNG HIỆU NĂNG MẠNG (NT106)")
    print("=" * 80)
    print(f"{'Tiêu chí đánh giá':<35} | {'Self-Hosted (.NET 10)':<20} | {'BaaS Supabase':<20}")
    print("-" * 80)

    supa_min = f"{res_supa['min']} ms" if res_supa else "N/A"
    print(f"{'1. RTT Tối thiểu (Min Latency)':<35} | {res_self['min']:<17} ms | {supa_min:<20}")

    supa_avg = f"{res_supa['avg']} ms" if res_supa else "N/A"
    print(f"{'2. RTT Trung bình (Avg Latency)':<35} | {res_self['avg']:<17} ms | {supa_avg:<20}")

    supa_med = f"{res_supa['median']} ms" if res_supa else "N/A"
    print(f"{'3. RTT Trung vị (Median Latency)':<35} | {res_self['median']:<17} ms | {supa_med:<20}")

    supa_p95 = f"{res_supa['p95']} ms" if res_supa else "N/A"
    print(f"{'4. RTT P95 (95% request nhanh hơn)':<35} | {res_self['p95']:<17} ms | {supa_p95:<20}")

    supa_max = f"{res_supa['max']} ms" if res_supa else "N/A"
    print(f"{'5. RTT Tối đa (Max Latency - Lạnh)':<35} | {res_self['max']:<17} ms | {supa_max:<20}")

    supa_succ = f"{res_supa['success_rate']} %" if res_supa else "N/A"
    print(f"{'6. Tỷ lệ thành công (Success)':<35} | {res_self['success_rate']:<17} %  | {supa_succ:<20}")

    supa_body = f"{res_supa['avg_body_size']} B" if res_supa else "N/A"
    print(f"{'7. Kích thước JSON Body':<35} | {res_self['avg_body_size']:<17} B  | {supa_body:<20}")

    # Header Overheads (Ước tính theo giao thức)
    print(f"{'8. Overhead Header & Token':<35} | ~250 B (Gọn nhẹ)     | ~1200 B (Bearer JWT) ")

    # RAM tiêu thụ
    ram_str = f"{res_self['metrics'].get('memoryWorkingSetMB', 'N/A')} MB" if res_self.get('metrics') else "N/A"
    print(f"{'9. RAM Server tiêu thụ':<35} | {ram_str:<20} | Serverless (Managed)")
    print("=" * 80)


def export_results(res_self, res_supa, output_csv="ket_qua_do_luong.csv", output_json="ket_qua_do_luong.json"):
    """Lưu kết quả đo ra file CSV và JSON."""
    # 1. Xuất file JSON
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "self_hosted": res_self,
        "supabase": res_supa
    }
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n[XUẤT FILE] Đã lưu kết quả chi tiết vào: {output_json}")

    # 2. Xuất file CSV so sánh từng request
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Request_Index", "Target", "RTT_ms"])
        for idx, rtt in enumerate(res_self["rtts"], 1):
            writer.writerow([idx, "Self-Hosted", rtt])
        if res_supa:
            for idx, rtt in enumerate(res_supa["rtts"], 1):
                writer.writerow([idx, "Supabase", rtt])
    print(f"[XUẤT FILE] Đã lưu dữ liệu từng gói tin vào: {output_csv}")


def main():
    parser = argparse.ArgumentParser(description="NT106 - Script đo lường hiệu năng đối sánh Server")
    parser.add_argument("--self-url", default="http://127.0.0.1:5000", help="URL của Self-Hosted Server (khuyên dùng 127.0.0.1 để tránh trễ phân giải IPv6 localhost)")
    parser.add_argument("--supa-url", default=os.environ.get("SUPABASE_URL", ""), help="URL Supabase Project")
    parser.add_argument("--supa-key", default=os.environ.get("SUPABASE_ANON_KEY", ""), help="Anon Key Supabase")
    parser.add_argument("-n", "--count", type=int, default=50, help="Số lượng request đo (mặc định 50)")
    parser.add_argument("--delay", type=float, default=0.05, help="Độ trễ giữa các request (giây)")
    args = parser.parse_args()

    print("=" * 80)
    print("      KHỞI ĐỘNG BỘ ĐO LƯỜNG HIỆU NĂNG MẠNG - NT106 (TV3)")
    print("=" * 80)
    print(f"Self-Hosted Target: {args.self_url}")
    print(f"Supabase Target   : {args.supa_url or 'Chưa cấu hình (Bỏ qua)'}")
    print(f"Số lượng request  : {args.count}")

    # Chạy đo Self-Hosted
    res_self = test_self_hosted(args.self_url, count=args.count, delay=args.delay)

    # Chạy đo Supabase
    res_supa = test_supabase(args.supa_url, args.supa_key, count=args.count, delay=args.delay)

    # In kết quả đối sánh
    print_comparison_table(res_self, res_supa)

    # Lưu file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "ket_qua_do_luong.csv")
    json_path = os.path.join(script_dir, "ket_qua_do_luong.json")
    export_results(res_self, res_supa, output_csv=csv_path, output_json=json_path)


if __name__ == "__main__":
    main()
