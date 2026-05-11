#!/usr/bin/env python3
"""Standalone HTTP server for sharing Allure reports"""
import os
import sys
import http.server
import socketserver
import socket


def get_lan_ip():
    """Get LAN IP, excluding virtual NICs/WSL"""
    try:
        addrs = socket.getaddrinfo(socket.gethostname(), None)
        for addr in addrs:
            ip = addr[4][0]
            # Exclude WSL/Hyper-V virtual subnets (172.16-31.x.x)
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
        pass  # Suppress log output, do not print each request

with socketserver.TCPServer(("0.0.0.0", port), SilentHandler) as httpd:
    print(f"Allure report server started!")
    print(f"====================================")
    if lan_ip:
        print(f"LAN access: http://{lan_ip}:{port}")
    else:
        print(f"Local access: http://localhost:{port}")
    print(f"====================================")
    print(f"Press Ctrl+C to stop the server")
    httpd.serve_forever()
