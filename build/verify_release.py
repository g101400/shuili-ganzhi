#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交付验包脚本：对 docs/RELEASE_MANIFEST.md 中的 7 产物逐项重算 SHA256 比对。
用途：接收方/发版人在任意机器验证包完整性（防传输损坏/夹带）。
  python build/verify_release.py
铁律：PROJECT_ROOT 由本脚本位置锚定；只读校验，不改任何文件。
注意：产物哈希随重建批次变化——如 FAIL 且包确为最近重建，先跑
  build/gen_release_manifest.py 刷新清单再验。"""
import hashlib, os, re, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(PROJECT_ROOT, "docs", "RELEASE_MANIFEST.md")
ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([\d,]+)\s*B\s*\|\s*`([0-9a-f]{64})`\s*\|\s*$")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not os.path.exists(MANIFEST):
        print("!! 清单不存在:", MANIFEST)
        sys.exit(1)
    rows = []
    with open(MANIFEST, encoding="utf-8") as f:
        for line in f:
            m = ROW.match(line.rstrip("\n"))
            if m:
                rows.append((m.group(1), m.group(2).strip(), int(m.group(3).replace(",", "")), m.group(4)))
    if len(rows) != 7:
        print(f"!! 清单行数异常：解析到 {len(rows)} 行（须 7），请检查 docs/RELEASE_MANIFEST.md 格式")
        sys.exit(1)

    print("== 交付验包（SHA256 逐项对账）==")
    fails = 0
    for name, rel, size, expect in rows:
        path = os.path.join(PROJECT_ROOT, rel.replace("\\", os.sep))
        if not os.path.exists(path):
            print(f"  [FAIL] {name}: 产物缺失 {rel}")
            fails += 1
            continue
        actual_size = os.path.getsize(path)
        actual = sha256(path)
        ok_size = actual_size == size
        ok_hash = actual == expect
        if ok_size and ok_hash:
            print(f"  [PASS] {name}  {actual_size:,} B  {actual[:16]}...")
        else:
            fails += 1
            print(f"  [FAIL] {name}")
            if not ok_size:
                print(f"         大小不符: 清单 {size:,} B / 实存 {actual_size:,} B")
            if not ok_hash:
                print(f"         哈希不符: 清单 {expect[:16]}... / 实存 {actual[:16]}...")
    print(f"== 结果：通过 {7 - fails}/7 ==")
    if fails:
        print("提示：若产物确为最近重建，请先运行 build/gen_release_manifest.py 刷新清单。")
        sys.exit(1)
    print("验包全部通过 ✓")


if __name__ == "__main__":
    main()
