#!/usr/bin/env python3
"""Nghe Supabase Realtime: in ra bản tin mới và đo độ trễ từ lúc client gửi đến lúc nhận.

Cài thư viện:  pip install websockets
Cách dùng:
    export SUPABASE_URL="https://xxxx.supabase.co"
    export SUPABASE_ANON_KEY="eyJ..."
    python realtime_listener.py        # mở terminal này, rồi chạy push_log.py ở terminal khác
    Nhấn Ctrl+C để dừng và xem thống kê.

Lưu ý: độ trễ tính bằng (giờ nhận - sent_at) nên phải chạy listener và push_log.py
trên CÙNG MỘT máy, nếu không đồng hồ hai máy lệch nhau sẽ làm sai số.
"""
import asyncio
import json
import os
import statistics
import sys
from datetime import datetime, timezone

import websockets

TOPIC = "realtime:public:network_logs"


async def heartbeat(ws):
    ref = 100
    while True:
        await asyncio.sleep(25)
        ref += 1
        await ws.send(json.dumps({"topic": "phoenix", "event": "heartbeat", "payload": {}, "ref": str(ref)}))


async def listen(url, key):
    ws_url = url.replace("https://", "wss://").replace("http://", "ws://")
    ws_url = f"{ws_url}/realtime/v1/websocket?apikey={key}&vsn=1.0.0"
    latencies = []
    try:
        async with websockets.connect(ws_url) as ws:
            join = {
                "topic": TOPIC,
                "event": "phx_join",
                "payload": {
                    "config": {
                        "postgres_changes": [
                            {"event": "INSERT", "schema": "public", "table": "network_logs"}
                        ]
                    }
                },
                "ref": "1",
            }
            await ws.send(json.dumps(join))
            beat = asyncio.create_task(heartbeat(ws))
            print("Đã kết nối, đang chờ bản tin mới... (Ctrl+C để dừng)")
            try:
                async for raw in ws:
                    message = json.loads(raw)
                    event = message.get("event")
                    if event == "phx_reply" and message.get("topic") == TOPIC:
                        status = message.get("payload", {}).get("status")
                        print(f"Đăng ký kênh: {status}")
                    elif event == "postgres_changes":
                        record = message["payload"]["data"]["record"]
                        received = datetime.now(timezone.utc)
                        line = f"Nhận: {record.get('message')} ({record.get('payload_size')} byte)"
                        if record.get("sent_at"):
                            sent = datetime.fromisoformat(record["sent_at"])
                            delay_ms = (received - sent).total_seconds() * 1000
                            latencies.append(delay_ms)
                            line += f"  độ trễ {delay_ms:.1f} ms"
                        print(line)
            finally:
                beat.cancel()
    finally:
        if latencies:
            print("\n--- Độ trễ Realtime (ms) ---")
            print(
                f"Số bản tin: {len(latencies)} | min {min(latencies):.1f} | "
                f"trung bình {statistics.mean(latencies):.1f} | max {max(latencies):.1f}"
            )


def main():
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        sys.exit("Thiếu biến môi trường SUPABASE_URL hoặc SUPABASE_ANON_KEY")
    try:
        asyncio.run(listen(url, key))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
