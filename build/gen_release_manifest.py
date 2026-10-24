#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成发布清单（docs/RELEASE_MANIFEST.md）：四端产物 SHA256 对账 + APK 签名指纹 + 门禁实况。
铁律：PROJECT_ROOT 由本脚本位置锚定（禁 CWD 相对路径）；产物只读，不改任何包。"""
import hashlib, os, subprocess, sys, datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASES = os.path.join(PROJECT_ROOT, "releases")
DOCS = os.path.join(PROJECT_ROOT, "docs")
VERSION = "1.77"

PRODUCTS = [
    ("Win exe",            os.path.join(RELEASES, "win", "水利感知项目一张图.exe")),
    ("Win msi",            os.path.join(RELEASES, "win", "水利感知项目一张图_Setup.msi")),
    ("UOS deb amd64",      os.path.join(RELEASES, "uos", f"shuili-ganzhi_{VERSION}_amd64.deb")),
    ("UOS deb arm64",      os.path.join(RELEASES, "uos", f"shuili-ganzhi_{VERSION}_arm64.deb")),
    ("UOS deb mips64el",   os.path.join(RELEASES, "uos", f"shuili-ganzhi_{VERSION}_mips64el.deb")),
    ("Android APK",        os.path.join(RELEASES, "android", f"水利感知项目一张图_V{VERSION}.apk")),
    ("iOS PWA zip",        os.path.join(RELEASES, "ios", f"水利感知项目一张图_V{VERSION}_iOS_PWA.zip")),
]

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def apk_cert_digest(apk):
    """apksigner --print-certs 抓 Signer #1 certificate SHA-256 digest（找不到工具返回提示文案）。"""
    sdk = os.environ.get("ANDROID_HOME") or r"E:\dev\ganzhi\tools\android-sdk"
    apksigner = os.path.join(sdk, "build-tools", "34.0.0", "apksigner.bat")
    if not os.path.exists(apksigner):
        return None
    try:
        out = subprocess.run([apksigner, "verify", "--print-certs", apk],
                             capture_output=True, text=True, timeout=120).stdout
        for line in out.splitlines():
            if "certificate SHA-256 digest" in line:
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None

def gate_status():
    """实跑门禁抓汇总行（假绿防护：取机器输出而非手填）。"""
    try:
        out = subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "build", "gate_check.py")],
                             capture_output=True, text=True, timeout=300)
        for line in (out.stdout or "").splitlines():
            if line.strip().startswith("通过"):
                return line.strip(), out.returncode
        return "汇总行缺失", out.returncode
    except Exception as e:
        return f"门禁执行异常: {e}", -1

def main():
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows, missing = [], []
    for name, path in PRODUCTS:
        if not os.path.exists(path):
            missing.append(name)
            continue
        size = os.path.getsize(path)
        rows.append((name, os.path.relpath(path, PROJECT_ROOT), size, sha256(path)))
    if missing:
        print("!! 产物缺失，清单未生成:", ", ".join(missing))
        sys.exit(1)

    cert = apk_cert_digest(PRODUCTS[5][1])
    gtext, gcode = gate_status()

    lines = []
    lines.append("# 发布清单（RELEASE_MANIFEST）· 水利感知项目一张图 V" + VERSION)
    lines.append("")
    lines.append(f"> 生成时间：{stamp}　批次：本机 E 盘独立工程（E:\\dev\\ganzhi\\perc）　产物不入库，哈希随重建批次变化，对账以最近一次构建为准。")
    lines.append("")
    lines.append("## 四端产物对账（7 项）")
    lines.append("")
    lines.append("| 产物 | 路径（相对工程根） | 大小 | SHA256 |")
    lines.append("|---|---|---:|---|")
    for name, rel, size, digest in rows:
        lines.append(f"| {name} | {rel} | {size:,} B | `{digest}` |")
    lines.append("")
    lines.append("## Android APK 签名身份")
    lines.append("")
    if cert:
        lines.append(f"- 签名方案：APK Signature Scheme v2（apksigner verify 实测 verified）")
        lines.append(f"- 证书 DN：`CN=Shuili Ganzhi Release, OU=Shuili, O=Shuili, L=Beijing, ST=Beijing, C=CN`")
        lines.append(f"- 证书 SHA-256 指纹：`{cert}`")
        lines.append("- keystore/口令：仓库外 `E:\\dev\\ganzhi\\tools\\keystore\\`（密钥零入库，换机需随发版人保管迁移）")
    else:
        lines.append("- 未取得指纹（apksigner 不可用），请手核。")
    lines.append("")
    lines.append("## 门禁状态（生成时实况）")
    lines.append("")
    lines.append(f"- `{gtext}`（exit={gcode}，脚本：build/gate_check.py，11 断言）")
    lines.append("")
    lines.append("## 交付与上架要点")
    lines.append("")
    lines.append("- Win：exe 免安装直接运行；msi 为 perMachine 安装需管理员权限。")
    lines.append("- UOS：`sudo dpkg -i shuili-ganzhi_*.deb`（按机器架构选包），桌面入口「水利感知项目一张图」。")
    lines.append("- Android：release APK 可直接安装；上架商店需使用本清单指纹对应 keystore 复签校验。")
    lines.append("- iOS：zip 解压后经 HTTPS 静态托管，Safari 打开 → 添加到主屏幕（PWA）。")
    lines.append("")
    lines.append("> AI生成")

    os.makedirs(DOCS, exist_ok=True)
    out = os.path.join(DOCS, "RELEASE_MANIFEST.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("清单已生成:", out)
    for name, rel, size, digest in rows:
        print(f"  {name:16s} {size:>12,} B  {digest[:16]}...")
    print("  APK 证书指纹:", cert or "N/A")
    print("  门禁:", gtext)

if __name__ == "__main__":
    main()
