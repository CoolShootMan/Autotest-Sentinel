#!/usr/bin/env python3
"""独立的 HTTP 服务器，用于共享 Allure 报告"""
import os
import sys
import http.server
import socketserver
import socket


def get_lan_ip():
    """获取局域网 IP，排除虚拟网卡/WSL"""
    try:
        addrs = socket.getaddrinfo(socket.gethostname(), None)
        for addr in addrs:
            ip = addr[4][0]
            # 排除 WSL/Hyper-V 虚拟网段 (172.16-31.x.x)
            if ip.startswith("172."):
                octet2 = int(ip.split(".")[1])
                if 16 <= octet2 <= 31:
                    continue
            if ip.startswith("192.168.") and not any(ip.startswith(f"192.168.{x}.") for x in ["56", "88", "23"]):
                return ip
        for addr in addrs:
            ip = addr[4][0]
            if ip.startswith("127.") or ":" in ip:
                continue
            if ip.startswith("172."):
                octet2 = int(ip.split(".")[1])
                if 16 <= octet2 <= 31:
                    continue
            return ip
    except Exception:
        pass
    return None


if len(sys.argv) < 3:
    print("Usage: python http_server.py <report_dir> <port>")
    sys.exit(1)

report_dir = sys.argv[1]
port = int(sys.argv[2])
os.chdir(report_dir)

lan_ip = get_lan_ip()

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 静默日志，不打印每个请求

with socketserver.TCPServer(("0.0.0.0", port), SilentHandler) as httpd:
    print(f"Allure 报告服务已启动!")
    print(f"====================================")
    if lan_ip:
        print(f"同事访问: http://{lan_ip}:{port}")
    else:
        print(f"本机访问: http://localhost:{port}")
    print(f"====================================")
    print(f"按 Ctrl+C 停止服务")
    httpd.serve_forever()
