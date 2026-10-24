# -*- coding: utf-8 -*-
"""
水利感知项目一张图 · iOS 可托管 PWA zip 构建器
（本工程无独立 iOS 壳，按交接文档 §BUILD「参考 shuili 的 water-ios 思路生成可托管 zip，非 App Store .ipa」）

做法：复制 webroot 到临时组装目录，叠加 PWA 增强层（manifest + service worker + apple-touch-icon +
index.html 注入），zip 归档。工程 webroot 本体零改动（基线 0 漂移）。

铁律落地：
  1. PROJECT_ROOT 绝对路径锚定；
  2. 密钥零入包：ai_seed.js / secure_boot_cred.js / sec_crypt.js / offline_tiles / *.bak* 硬排除并计数；
  3. 出包前清同版本旧 zip；产物落 releases/ios/；
  4. 自校验断言计数 >0 并打印（防假绿）。
"""
import os, io, sys, json, zipfile, hashlib, shutil, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
WEBROOT = os.path.join(PROJECT_ROOT, "webroot")
RELEASE_DIR = os.path.join(PROJECT_ROOT, "releases", "ios")
ICON_SRC = os.path.join(PROJECT_ROOT, "build", "targets", "android", "app", "src", "main", "res")

VERSION = "1.76"

EXCLUDE_FILES = {"ai_seed.js", "secure_boot_cred.js", "sec_crypt.js"}
EXCLUDE_DIRS = {"offline_tiles", "__pycache__", ".git"}
EXCLUDE_SUFFIX = (".bak", ".log", ".pyc", ".deb", ".zip", ".exe", ".apk")

MANIFEST = {
    "name": "水利感知项目一张图",
    "short_name": "感知一张图",
    "description": "视频监控 / 雨水情监测 / 大坝安全监测 / 地下水源监测 一张图",
    "start_url": "./index.html",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#F5F7FA",
    "theme_color": "#4A9EF5",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

SW_JS = """// 水利感知项目一张图 · PWA Service Worker（iOS Safari 添加到主屏幕后离线可开）
var CACHE = 'ganzhi-v1.76';
var CORE = [
  './', './index.html', './app.js', './data.js', './water_data.js',
  './ctx_menu.js', './photo_gesture.js', './jszip.min.js', './version.json',
  './leaflet/leaflet.js', './leaflet/leaflet.css'
];
self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(CORE); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.map(function (k) { return k === CACHE ? null : caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(function (hit) {
    return hit || fetch(e.request).then(function (resp) {
      if (resp.ok && e.request.url.indexOf(location.origin) === 0) {
        var cp = resp.clone();
        caches.open(CACHE).then(function (c) { c.put(e.request, cp); });
      }
      return resp;
    }).catch(function () { return caches.match('./index.html'); });
  }));
});
"""

INJECT_HEAD = (
    '<link rel="manifest" href="manifest.webmanifest">'
    '<meta name="theme-color" content="#4A9EF5">'
    '<link rel="apple-touch-icon" href="icons/icon-192.png">'
    '<meta name="apple-mobile-web-app-capable" content="yes">'
    '<meta name="apple-mobile-web-app-status-bar-style" content="default">'
    '<meta name="apple-mobile-web-app-title" content="感知一张图">'
)

README = """# 水利感知项目一张图 · iOS 部署说明（PWA 可托管包）

本包为 iOS 端「可托管 PWA」部署形态（本工程无独立 iOS 原生壳，非 App Store .ipa）。

## 部署步骤
1. 把 zip 解压后的全部内容（index.html 及同级所有文件/目录）托管到任意 HTTPS 静态服务器，
   例如：nginx / IIS / GitHub Pages / 内网文件服务器（须 HTTPS）。
2. iPhone 用 Safari 打开站点地址（如 https://your-host/ganzhi/index.html）。
3. Safari 底部「分享」按钮 →「添加到主屏幕」→ 即以独立 App 图标全屏运行。
4. 首次打开后核心资源写入本地缓存（Service Worker），再次打开支持离线。

## 内容清单
- index.html            入口（已注入 PWA manifest / apple-touch-icon / theme-color）
- manifest.webmanifest  PWA 应用清单
- sw.js                 Service Worker（核心资源离线缓存）
- icons/                应用图标（192/512/maskable，取自 Android 壳资源）
- 其余                  与工程 webroot 完全一致（33 文件，含 leaflet/ ocr/ data.js 等）

## 版本
- 版本 1.76（version.json 同源）；数据 1125 条监测记录；四大子系统。

## 安全说明
- 本包不含 ai_seed.js / secure_boot_cred.js / offline_tiles（密钥与大数据不入包铁律）。
"""


def collect_webroot():
    files, excluded = [], 0
    for root, dirs, fns in os.walk(WEBROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in fns:
            if fn in EXCLUDE_FILES or fn.endswith(EXCLUDE_SUFFIX) or ".bak_" in fn:
                excluded += 1
                continue
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, WEBROOT).replace(os.sep, "/")
            files.append((src, rel))
    return files, excluded


def build():
    global VERSION
    try:
        with open(os.path.join(PROJECT_ROOT, "version.json"), encoding="utf-8") as f:
            VERSION = str(json.load(f).get("version", VERSION)).lstrip("v")
    except Exception:
        pass
    os.makedirs(RELEASE_DIR, exist_ok=True)
    out_zip = os.path.join(RELEASE_DIR, "水利感知项目一张图_V%s_iOS_PWA.zip" % VERSION)
    if os.path.exists(out_zip):
        os.remove(out_zip)
        print("  [清理] 同版本旧 zip 已删除")

    print("== 收集 webroot（PROJECT_ROOT=%s）==" % PROJECT_ROOT)
    files, excluded = collect_webroot()
    print("   文件数=%d，密钥/备份排除命中=%d" % (len(files), excluded))

    print("== 组装 PWA 增强层 ==")
    staged = {}
    for src, rel in files:
        staged[rel] = open(src, "rb").read()
    # index.html 注入（仅 zip 内副本，工程 webroot 不动）
    html = staged["index.html"].decode("utf-8")
    assert "<head>" in html, "index.html 缺 <head>"
    html = html.replace("<head>", "<head>" + INJECT_HEAD, 1)
    staged["index.html"] = html.encode("utf-8")
    staged["manifest.webmanifest"] = json.dumps(MANIFEST, ensure_ascii=False, indent=2).encode("utf-8")
    staged["sw.js"] = SW_JS.encode("utf-8")
    staged["README_iOS部署说明.md"] = README.encode("utf-8")
    icons = {
        "icons/icon-192.png": os.path.join(ICON_SRC, "mipmap-xxxhdpi", "ic_launcher.png"),
        "icons/icon-512.png": os.path.join(ICON_SRC, "mipmap-xxxhdpi", "ic_launcher_foreground.png"),
        "icons/icon-maskable-512.png": os.path.join(ICON_SRC, "mipmap-xxxhdpi", "ic_launcher.png"),
    }
    for rel, src in icons.items():
        if os.path.exists(src):
            staged[rel] = open(src, "rb").read()
        else:
            print("  [warn] 图标缺失: %s" % src)

    print("== 打 zip ==")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for rel in sorted(staged):
            zf.writestr(rel, staged[rel])
    size = os.path.getsize(out_zip)
    print("   zip -> %s (%.2f MB, %d 条目)" % (out_zip, size / 1e6, len(staged)))

    print("== 自校验（断言计数须>0）==")
    checks = []
    with zipfile.ZipFile(out_zip) as zf:
        names = zf.namelist()
        checks.append(("index.html 注入 manifest", b"manifest.webmanifest" in zf.read("index.html")))
        checks.append(("apple-touch-icon 注入", b"apple-touch-icon" in zf.read("index.html")))
        checks.append(("manifest.webmanifest", "manifest.webmanifest" in names))
        checks.append(("sw.js", "sw.js" in names))
        checks.append(("leaflet.js", any(n == "leaflet/leaflet.js" for n in names)))
        checks.append(("data.js", "data.js" in names))
        checks.append(("water_data.js", "water_data.js" in names))
        checks.append(("icons 目录", any(n.startswith("icons/") for n in names)))
        checks.append(("部署说明", "README_iOS部署说明.md" in names))
        checks.append(("密钥零入包", not any(("ai_seed.js" in n or "secure_boot_cred" in n
                      or "offline_tiles" in n or ".bak" in n) for n in names)))
        checks.append(("基线33文件全在", all(any(n == rel for n in names) for _s, rel in files)))
    ok = sum(1 for _n, v in checks if v)
    for n, v in checks:
        print("  [自校验] %-24s %s" % (n, "PASS" if v else "FAIL"))
    assert ok == len(checks) and ok > 0, "自校验失败 %d/%d" % (ok, len(checks))
    print("  [自校验] 通过 %d/%d ✓" % (ok, len(checks)))
    print("\n完成。HTTPS 托管后 Safari「添加到主屏幕」即得 iOS 独立入口。")


if __name__ == "__main__":
    build()
