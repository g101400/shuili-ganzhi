#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iOS PWA / 局域网 HTTPS 静态托管（自签名一键起服）。
PWA 的 Service Worker 要求安全上下文：本工具自动生成自签证书并起 HTTPS 服务。

用法（PROJECT_ROOT 由脚本位置锚定）：
  python build/serve_https.py                        # 默认服务 releases/ios/_site，端口 8443
  python build/serve_https.py -d <目录> -p 8443      # 指定目录/端口
  python build/serve_https.py --http                 # 纯 HTTP 模式（可添加主屏，SW 不注册）

iPhone 使用步骤：
  1) 与电脑同一 Wi-Fi，Safari 打开 https://<下方打印的局域网IP>:8443
  2) 出现证书警告 → 「显示详细信息」→「访问此网站」（快速验证路径）
  3) 分享 → 添加到主屏幕（图标与 manifest 生效）
  4) 如需 Service Worker 离线缓存完整生效：Safari 打开 https://<IP>:8443/_dev_cert.crt
     下载描述文件 → 设置→通用→VPN与设备管理→安装 → 关于本机→证书信任设置→开启完全信任
安全提示：自签名证书仅限局域网发版验证，公网发版请使用正规 CA 证书。"""
import argparse, functools, os, socket, ssl, subprocess, sys, datetime
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.environ.get("SHUILI_TOOLS") or os.path.join(os.path.dirname(PROJECT_ROOT), "tools")
CERT_DIR = os.path.join(TOOLS, "certs")
CRT = os.path.join(CERT_DIR, "shuili-dev.crt")
KEY = os.path.join(CERT_DIR, "shuili-dev.key")


def lan_ip():
    """取局域网出口 IP（UDP connect 不实际发包）。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("223.5.5.5", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def ensure_cert():
    """证书不存在则用 Git 自带 openssl 生成自签证书（证书不入库，落 tools\certs）。"""
    if os.path.exists(CRT) and os.path.exists(KEY):
        return
    openssls = [r"C:\Program Files\Git\usr\bin\openssl.exe", "/usr/bin/openssl"]
    exe = next((p for p in openssls if os.path.exists(p)), None)
    if not exe:
        print("!! 未找到 openssl，请自备证书：", CRT, KEY)
        sys.exit(1)
    os.makedirs(CERT_DIR, exist_ok=True)
    subprocess.run([exe, "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                    "-keyout", KEY, "-out", CRT, "-days", "3650",
                    "-subj", "/CN=Shuili Ganzhi Dev"], check=True, capture_output=True)
    print("自签证书已生成:", CRT)


class CertHandler(SimpleHTTPRequestHandler):
    """在静态服务基础上附加 /_dev_cert.crt 路由，便于 iPhone Safari 直接下载描述文件。"""

    def do_GET(self):
        if self.path.split("?")[0] == "/_dev_cert.crt":
            data = open(CRT, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "application/x-x509-ca-cert")
            self.send_header("Content-Disposition", 'attachment; filename="shuili-dev.crt"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()

    def log_message(self, fmt, *args):
        print("[%s] %s" % (datetime.datetime.now().strftime("%H:%M:%S"), fmt % args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", default=os.path.join(PROJECT_ROOT, "releases", "ios", "_site"),
                    help="服务目录（默认 releases/ios/_site，需先解压 iOS PWA zip）")
    ap.add_argument("-p", type=int, default=8443)
    ap.add_argument("--http", action="store_true", help="纯 HTTP 模式（SW 不注册）")
    a = ap.parse_args()

    if not os.path.isdir(a.d):
        print("!! 目录不存在:", a.d, "\n   先解压 releases/ios/水利感知项目一张图_V1.77_iOS_PWA.zip 到该目录（或用 -d 指定）")
        sys.exit(1)

    ip = lan_ip()
    handler = functools.partial(CertHandler, directory=a.d)   # 显式锚定服务目录（不依赖进程 CWD，防假绿）
    if a.http:
        srv = ThreadingHTTPServer(("0.0.0.0", a.p), handler)
        print(f"HTTP  http://{ip}:{a.p}/  （SW 不注册；仅快速验证）")
    else:
        ensure_cert()
        srv = ThreadingHTTPServer(("0.0.0.0", a.p), handler)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(CRT, KEY)
        srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
        print(f"HTTPS https://{ip}:{a.p}/   证书下载: https://{ip}:{a.p}/_dev_cert.crt")
    print(f"服务目录: {a.d}   Ctrl+C 停止")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
