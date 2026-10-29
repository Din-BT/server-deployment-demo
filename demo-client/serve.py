#!/usr/bin/env python3
"""
NT106 - DEMO CLIENT WEB RUNNER
Khởi động HTTP Server cục bộ cho ứng dụng Client Demo (cổng 8080) và tự động mở trình duyệt.
Thành viên phụ trách: TV3 (Client & Đo lường)
"""

import http.server
import os
import socketserver
import sys
import webbrowser

# Đảm bảo in tiếng Việt chuẩn trên Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Tránh cache để khi sửa HTML/JS được cập nhật ngay
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def run():
    os.chdir(DIRECTORY)
    print("=" * 60)
    print("  [NT106] DANG KHOI DONG CLIENT DEMO & DO LUONG")
    print(f"  Thu muc: {DIRECTORY}")
    print(f"  Dia chi: http://localhost:{PORT}")
    print("=" * 60)

    # Tự động mở trình duyệt web
    webbrowser.open(f"http://localhost:{PORT}")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server Client dang chay tai http://localhost:{PORT}")
        print("Nhan Ctrl+C de dung.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDa dung Client Demo Server.")


if __name__ == "__main__":
    run()
