# -*- coding: utf-8 -*-
"""
水利感知项目一张图 · 纯 Python 构建 UOS/麒麟 deb 包（零外部依赖，Windows 本机可跑）
继承自交接包 build/build_deb.py 的 ar+tar.xz 合成方案，目录结构对齐
native-shell/uos-pyqt6/build_deb.sh（/opt/shuili-ganzhi/{webroot,main.py} + 启动器 + desktop）。

铁律落地：
  1. PROJECT_ROOT 由本文件绝对路径锚定（禁 CWD 相对路径）；
  2. 出包前清同版本旧包；产物落 releases/uos/；
  3. 密钥零入包：ai_seed.js / secure_boot_cred.js / sec_crypt.js / offline_tiles/ / *.bak* 硬排除；
  4. 自校验断言计数必须 >0 并打印（防假绿）。

用法：python build_deb_pure.py [ARCH]   （默认 amd64，可传 arm64 / mips64el）
"""
import os, io, sys, json, tarfile, lzma, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))          # build/
PROJECT_ROOT = os.path.dirname(HERE)                        # 工程根 E:\dev\ganzhi\perc
NATIVE_UOS = os.path.join(PROJECT_ROOT, "native-shell", "uos-pyqt6")
WEBROOT = os.path.join(PROJECT_ROOT, "webroot")
RELEASE_DIR = os.path.join(PROJECT_ROOT, "releases", "uos")

PKG = "shuili-ganzhi"
VERSION = "1.76"
ARCH = sys.argv[1] if len(sys.argv) > 1 else "amd64"
APP_DIR = "/opt/" + PKG
MAINTAINER = "小七 <xiaoyi@example.com>"

# 铁律：密钥/凭据/备份零入包（防御性硬排除，即使源目录意外混入也拦下）
EXCLUDE_FILES = {"ai_seed.js", "secure_boot_cred.js", "sec_crypt.js"}
EXCLUDE_DIRS = {"offline_tiles", "__pycache__", ".git"}
EXCLUDE_SUFFIX = (".bak", ".bak_win", ".log", ".pyc", ".deb", ".zip", ".exe")


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_version():
    """版本单一事实来源：工程根 version.json（铁律：不写死，防漂移）。"""
    global VERSION
    vj = os.path.join(PROJECT_ROOT, "version.json")
    try:
        with open(vj, encoding="utf-8") as f:
            j = json.load(f)
        if j.get("version"):
            VERSION = str(j["version"]).lstrip("v")
    except Exception as e:
        print("  [warn] version.json 读取失败，回退默认 %s：%s" % (VERSION, e))


def is_excluded(name):
    return (name in EXCLUDE_FILES or name.endswith(EXCLUDE_SUFFIX)
            or ".bak_" in name or name.startswith("_deb_build"))


def collect_entries():
    """(src, arcpath) 清单 + 排除命中计数（门禁要求计数>0）。"""
    entries, excluded = [], 0
    for root, dirs, files in os.walk(WEBROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            if is_excluded(fn):
                excluded += 1
                continue
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, WEBROOT).replace(os.sep, "/")
            entries.append((src, APP_DIR + "/webroot/" + rel))
    mainpy = os.path.join(NATIVE_UOS, "main.py")
    entries.append((mainpy, APP_DIR + "/main.py"))
    return entries, excluded


def build_data_tar_xz(entries):
    tmp_tar = os.path.join(RELEASE_DIR, "_data.tar")
    md5lines = []
    with tarfile.open(tmp_tar, "w", format=tarfile.GNU_FORMAT) as tf:
        dirs = set()
        for _s, arc in entries:
            d = os.path.dirname(arc).lstrip("/")
            while d:
                dirs.add(d)
                d = os.path.dirname(d)
        for d in sorted(dirs, key=lambda x: (x.count("/"), x)):
            ti = tarfile.TarInfo(d)
            ti.type = tarfile.DIRTYPE
            ti.mode = 0o755
            ti.mtime = 0
            tf.addfile(ti)
        for src, arc in entries:
            ti = tf.gettarinfo(src, arc)
            if ti.isreg():
                executable = arc.endswith("main.py") or arc.endswith("/usr/bin/" + PKG) or arc.startswith("/usr/bin/")
                ti.mode = 0o755 if executable else 0o644
                with open(src, "rb") as f:
                    tf.addfile(ti, f)
            else:
                tf.addfile(ti)
            md5lines.append("%s  %s" % (md5_of(src), arc.lstrip("/")))
    tmp_xz = os.path.join(RELEASE_DIR, "_data.tar.xz")
    with open(tmp_tar, "rb") as fin, lzma.open(tmp_xz, "wb", preset=1,
            format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64) as fout:
        fout.write(fin.read())
    os.remove(tmp_tar)
    return tmp_xz, "\n".join(md5lines) + "\n"


LAUNCHER = "#!/bin/bash\nexec python3 %s/main.py \"$@\"\n" % APP_DIR

DESKTOP = """[Desktop Entry]
Name=水利感知项目一张图
Comment=水利感知设施一张图（原生壳）
Exec=%s
Terminal=false
Type=Application
Icon=webview
Categories=Utility;Science;
""" % PKG

CONTROL = """Package: %s
Version: %s
Section: utils
Priority: optional
Architecture: %s
Depends: python3, python3-pyqt6, python3-pyqt6.qtwebengine
Maintainer: %s
Description: 水利感知项目一张图（统信 UOS 原生壳）
 PyQt6 + QWebEngineView 承载网页，取代 :7205 python http.server，无后台服务残留。
"""


def build_control_tar_xz(md5sums):
    tmp = os.path.join(RELEASE_DIR, "_control.tar")
    with tarfile.open(tmp, "w", format=tarfile.GNU_FORMAT) as tf:
        def add_str(name, content, mode):
            b = content.encode("utf-8")
            ti = tarfile.TarInfo(name)
            ti.size = len(b)
            ti.mode = mode
            ti.mtime = 0
            ti.type = tarfile.TarTYPE if hasattr(tarfile, "TarTYPE") else tarfile.REGTYPE
            tf.addfile(ti, io.BytesIO(b))
        add_str("control", CONTROL % (PKG, VERSION, ARCH, MAINTAINER), 0o644)
        add_str("conffiles", "", 0o644)
        add_str("md5sums", md5sums, 0o644)
    tmp_xz = os.path.join(RELEASE_DIR, "_control.tar.xz")
    with open(tmp, "rb") as fin, lzma.open(tmp_xz, "wb", preset=1,
            format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64) as fout:
        fout.write(fin.read())
    os.remove(tmp)
    return tmp_xz


def build_data_with_launcher(entries):
    """把 /usr/bin 启动器与 desktop 临时落盘并入 data 条目。"""
    import tempfile
    tmpd = tempfile.mkdtemp(dir=RELEASE_DIR)
    launcher = os.path.join(tmpd, "launcher")
    with io.open(launcher, "w", encoding="utf-8", newline="\n") as f:
        f.write(LAUNCHER)
    desktop = os.path.join(tmpd, "app.desktop")
    with io.open(desktop, "w", encoding="utf-8", newline="\n") as f:
        f.write(DESKTOP)
    entries.append((launcher, "/usr/bin/" + PKG))
    entries.append((desktop, "/usr/share/applications/%s.desktop" % PKG))
    return entries, tmpd


def build_ar(deb_path, members):
    with open(deb_path, "wb") as out:
        out.write(b"!<arch>\n")
        for data, name in members:
            hdr = "%-16s%-12d%-6d%-6d%-8o%-10d`\n" % (name[:16], 0, 0, 0, 0o100644, len(data))
            out.write(hdr.encode("ascii"))
            out.write(data)
            if len(data) % 2 == 1:
                out.write(b"\n")


def self_verify(deb_path):
    """门禁自校验：断言逐项打印，计数必须>0（防假绿）。"""
    checks = []
    with open(deb_path, "rb") as f:
        assert f.read(8) == b"!<arch>\n", "ar 魔数错误"
        members = {}
        while True:
            hdr = f.read(60)
            if len(hdr) < 60:
                break
            name = hdr[0:16].decode().strip()
            size = int(hdr[48:58].decode().strip())
            data = f.read(size)
            if size % 2 == 1:
                f.read(1)
            members[name] = data
    checks.append(("debian-binary", members.get("debian-binary") == b"2.0\n"))
    ctrl = tarfile.open(fileobj=io.BytesIO(members["control.tar.xz"]), mode="r:xz")
    cnames = ctrl.getnames()
    checks.append(("control/存在", "control" in cnames))
    checks.append(("control/md5sums", "md5sums" in cnames))
    data = tarfile.open(fileobj=io.BytesIO(members["data.tar.xz"]), mode="r:xz")
    dnames = data.getnames()
    checks.append(("main.py 主程序", any(n.endswith("/main.py") for n in dnames)))
    checks.append(("webroot/index.html", any(n.endswith("webroot/index.html") for n in dnames)))
    checks.append(("webroot/leaflet.js", any(n.endswith("leaflet/leaflet.js") for n in dnames)))
    checks.append(("webroot/data.js", any(n.endswith("webroot/data.js") for n in dnames)))
    checks.append(("usr/bin 启动器", any(n in ("usr/bin/" + PKG, "/usr/bin/" + PKG) for n in dnames)))
    checks.append((".desktop", any(n.endswith(".desktop") for n in dnames)))
    # 密钥零入包反向断言
    checks.append(("密钥零入包", not any(("ai_seed.js" in n or "secure_boot_cred" in n
                  or "offline_tiles" in n or ".bak" in n) for n in dnames)))
    ok = sum(1 for _n, v in checks if v)
    for n, v in checks:
        print("  [自校验] %-24s %s" % (n, "PASS" if v else "FAIL"))
    assert ok == len(checks) and ok > 0, "自校验失败：通过 %d/%d" % (ok, len(checks))
    print("  [自校验] 通过 %d/%d ✓" % (ok, len(checks)))
    return ok


def main():
    os.makedirs(RELEASE_DIR, exist_ok=True)
    load_version()
    out_deb = os.path.join(RELEASE_DIR, "%s_%s_%s.deb" % (PKG, VERSION, ARCH))
    # 铁律：出包前清同版本旧包
    if os.path.exists(out_deb):
        os.remove(out_deb)
        print("  [清理] 同版本旧包已删除: %s" % os.path.basename(out_deb))

    print("== 收集文件清单（PROJECT_ROOT=%s）==" % PROJECT_ROOT)
    entries, excluded = collect_entries()
    entries, tmpd = build_data_with_launcher(entries)
    print("   文件数=%d，密钥/备份排除命中=%d（须=0，防泄露与污染）" % (len(entries), excluded))

    print("== 构建 data.tar.xz ==")
    data_xz, md5sums = build_data_tar_xz(entries)
    print("   data.tar.xz size=%d" % os.path.getsize(data_xz))

    print("== 构建 control.tar.xz ==")
    ctrl_xz = build_control_tar_xz(md5sums)

    print("== 合成 .deb ==")
    ctrl_bytes = open(ctrl_xz, "rb").read()
    data_bytes = open(data_xz, "rb").read()
    os.remove(ctrl_xz); os.remove(data_xz)
    import shutil; shutil.rmtree(tmpd, ignore_errors=True)
    build_ar(out_deb, [
        (b"2.0\n", "debian-binary"),
        (ctrl_bytes, "control.tar.xz"),
        (data_bytes, "data.tar.xz"),
    ])
    print("   deb -> %s" % out_deb)
    print("   size=%d bytes (%.2f MB)" % (os.path.getsize(out_deb), os.path.getsize(out_deb) / 1e6))

    print("== 本机结构自校验 ==")
    self_verify(out_deb)
    print("\n完成。请到统信 UOS (%s) 真机执行: sudo dpkg -i %s" % (ARCH, out_deb))


if __name__ == "__main__":
    main()
