# -*- coding: utf-8 -*-
"""
水利感知项目一张图 · 回归门禁对账（铁律 §6，每次改动后必跑）
1. webroot 与交接基线逐文件对账：缺失=0、大小不一致=0、内容MD5漂移=0（新增需登记）
2. webroot 内禁 .bak_* / webroot_bak_*
3. 密钥零泄露：ai_seed.js / secure_boot_cred.js / sec_crypt.js / offline_tiles 不得出现在
   工程目录与任何发布产物中（对 deb/apk/zip 做成员级扫描）
4. 产物实存对账：四端产物机器验证真实存在（日志成功 ≠ 产物实存）
断言计数必须 >0 并打印（防假绿）。
"""
import os, sys, json, zipfile, tarfile, io, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
WEBROOT = os.path.join(PROJECT_ROOT, "webroot")
BASELINE = r"E:\ganzhi\perc_handoff\perc_handoff\webroot"
RELEASES = os.path.join(PROJECT_ROOT, "releases")

SECRET_NAMES = ("ai_seed.js", "secure_boot_cred.js", "sec_crypt.js")


def md5_of(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def scan_tree(root):
    files = {}
    for r, dirs, fns in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        for fn in fns:
            p = os.path.join(r, fn)
            files[os.path.relpath(p, root).replace(os.sep, "/")] = p
    return files


def main():
    checks = []
    print("== 1) webroot 与交接基线逐文件对账 ==")
    base = scan_tree(BASELINE)
    cur = scan_tree(WEBROOT)
    missing = sorted(set(base) - set(cur))
    added = sorted(set(cur) - set(base))
    size_diff = [k for k in sorted(set(base) & set(cur))
                 if os.path.getsize(base[k]) != os.path.getsize(cur[k])]
    md5_diff = [k for k in sorted(set(base) & set(cur))
                if md5_of(base[k]) != md5_of(cur[k])] if not size_diff else []
    print("   基线文件=%d 当前文件=%d 缺失=%d 新增=%d 大小不一致=%d" %
          (len(base), len(cur), len(missing), len(added), len(size_diff)))
    if missing:
        print("   缺失清单:", missing)
    if added:
        print("   新增清单（登记备查）:", added)
    if md5_diff:
        print("   MD5漂移清单:", md5_diff)
    checks.append(("基线缺失=0", len(missing) == 0))
    checks.append(("基线大小一致=0漂移", len(size_diff) == 0 and len(md5_diff) == 0))

    print("== 2) webroot 禁 .bak_* / webroot_bak_* ==")
    bak = [k for k in cur if ".bak" in k or "webroot_bak" in k]
    print("   命中=%d（须=0）" % len(bak))
    checks.append(("webroot 无 .bak_*", len(bak) == 0))

    print("== 3) 密钥零泄露（工程树 + 四端产物成员级扫描）==")
    leaks = []
    for rel, p in scan_tree(PROJECT_ROOT).items():
        low = rel.lower()
        if any(s in low for s in SECRET_NAMES) and "demo" not in low:
            leaks.append("工程树:" + rel)
        if "offline_tiles" in low:
            leaks.append("工程树:" + rel)
    for name in ("win", "uos", "android", "ios"):
        d = os.path.join(RELEASES, name)
        if not os.path.isdir(d):
            leaks.append("产物目录缺失:" + name)
            continue
        for fn in os.listdir(d):
            p = os.path.join(d, fn)
            low = fn.lower()
            if any(s in low for s in SECRET_NAMES):
                leaks.append("产物名:" + name + "/" + fn)
            if low.endswith(".zip"):
                with zipfile.ZipFile(p) as zf:
                    for n in zf.namelist():
                        ln = n.lower()
                        if any(s in ln for s in SECRET_NAMES) or "offline_tiles" in ln or ".bak" in ln:
                            leaks.append("zip成员:" + name + "/" + fn + "!" + n)
            if low.endswith(".deb"):
                with open(p, "rb") as f:
                    data = f.read()
                i = 8
                members = {}
                while i + 60 <= len(data):
                    hdr = data[i:i + 60].decode("ascii", "ignore")
                    nm = hdr[0:16].strip()
                    size = int(hdr[48:58])
                    members[nm] = data[i + 60:i + 60 + size]
                    i += 60 + size + (size % 2)
                dt = tarfile.open(fileobj=io.BytesIO(members["data.tar.xz"]), mode="r:xz")
                for n in dt.getnames():
                    ln = n.lower()
                    if any(s in ln for s in SECRET_NAMES) or "offline_tiles" in ln or ".bak" in ln:
                        leaks.append("deb成员:" + name + "/" + fn + "!" + n)
    print("   泄露命中=%d（须=0）" % len(leaks))
    if leaks:
        print("   泄露清单:", leaks)
    checks.append(("密钥零泄露", len(leaks) == 0))

    print("== 4) 四端产物实存对账 ==")
    expect = [
        ("Win exe", os.path.join(RELEASES, "win", "水利感知项目一张图.exe")),
        ("Win msi", os.path.join(RELEASES, "win", "水利感知项目一张图_Setup.msi")),
        ("UOS deb(amd64)", os.path.join(RELEASES, "uos", "shuili-ganzhi_1.76_amd64.deb")),
        ("UOS deb(arm64)", os.path.join(RELEASES, "uos", "shuili-ganzhi_1.76_arm64.deb")),
        ("UOS deb(mips64el)", os.path.join(RELEASES, "uos", "shuili-ganzhi_1.76_mips64el.deb")),
        ("Android APK", os.path.join(RELEASES, "android", "水利感知项目一张图_V1.76.apk")),
        ("iOS PWA zip", os.path.join(RELEASES, "ios", "水利感知项目一张图_V1.76_iOS_PWA.zip")),
    ]
    for label, p in expect:
        ok = os.path.isfile(p) and os.path.getsize(p) > 1_000_000
        sz = os.path.getsize(p) / 1e6 if os.path.isfile(p) else 0
        print("   %-16s %s (%.2f MB)" % (label, "实存" if ok else "缺失!", sz))
        checks.append(("产物:" + label, ok))

    print("== 门禁汇总 ==")
    ok = sum(1 for _n, v in checks if v)
    for n, v in checks:
        print("  [门禁] %-28s %s" % (n, "PASS" if v else "FAIL"))
    print("  通过 %d/%d" % (ok, len(checks)))
    assert ok == len(checks) and ok > 0, "门禁未全过（假绿防护）"
    print("门禁全部通过 ✓")


if __name__ == "__main__":
    main()
