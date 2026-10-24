# -*- coding: utf-8 -*-
"""
水利感知项目一张图 · msi files.wxs 生成器（替代 wix heat，零外部依赖）
扫描 publish 目录（releases/win）生成 WiX v3 语法组件清单：
- 排除构建临时文件（wxs/rtf/bat/pdb/xml 文档）
- 每文件一 Component（Guid="*"），子目录以 DirectoryRef 递归表达
- 挂到 INSTALLFOLDER，与 build_msi.wxs 的 ComponentGroupRef MainComponents 对齐
PROJECT_ROOT 由本文件位置锚定（铁律）。
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
PUBLISH_DIR = os.path.join(PROJECT_ROOT, "releases", "win")

EXCLUDE_EXT = (".wxs", ".rtf", ".bat", ".pdb", ".xml")
EXCLUDE_NAMES = {"license.rtf", "build_msi.wxs", "files.wxs", "app.ico"}


def xml_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def collect():
    files = []
    for root, dirs, fns in os.walk(PUBLISH_DIR):
        for fn in fns:
            if fn in EXCLUDE_NAMES or fn.endswith(EXCLUDE_EXT):
                continue
            rel = os.path.relpath(os.path.join(root, fn), PUBLISH_DIR).replace(os.sep, "\\")
            files.append((rel, os.path.join(root, fn)))
    return files


def dir_ids(rels):
    """收集全部子目录的 WiX Id（相对 INSTALLFOLDER 的路径）。"""
    dirs = set()
    for rel, _ in files:
        parts = rel.split("\\")
        for i in range(1, len(parts)):
            dirs.add("\\".join(parts[:i]))
    return dirs


def dir_id_of(path):
    return "d_%04d" % dir_index[path]


def file_id_of(rel):
    return "f_%04d" % file_index[rel]


files = collect()
print("收集文件数=%d（排除 pdb/xml/构建临时文件）" % len(files))
files.sort()
file_index = {rel: i + 1 for i, (rel, _s) in enumerate(files)}
dirs = sorted(dir_ids([r for r, _ in files]))
dir_index = {d: i + 1 for i, d in enumerate(dirs)}

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">',
         '  <Fragment>',
         '    <ComponentGroup Id="MainComponents">']
for rel, _ in files:
    lines.append('      <ComponentRef Id="%s" />' % file_id_of(rel))
lines.append('    </ComponentGroup>')
lines.append('  </Fragment>')
lines.append('  <Fragment>')
lines.append('    <DirectoryRef Id="INSTALLFOLDER">')
for d in dirs:
    parent = "\\".join(d.split("\\")[:-1])
    parent_id = dir_id_of(parent) if parent else "INSTALLFOLDER"
    lines.append('      <Directory Id="%s" Name="%s" />' % (dir_id_of(d), xml_escape(d.split("\\")[-1])))
for rel, src in files:
    parts = rel.split("\\")
    dirname = "\\".join(parts[:-1])
    dir_id = dir_id_of(dirname) if dirname else "INSTALLFOLDER"
    lines.append('      <Component Id="%s" Guid="*" Directory="%s">' % (file_id_of(rel), dir_id))
    lines.append('        <File Id="%s" Source="$(var.SourceDir)\\%s" KeyPath="yes" />' % (file_id_of(rel) + "_src", xml_escape(rel)))
    lines.append('      </Component>')
lines.append('    </DirectoryRef>')
lines.append('  </Fragment>')
lines.append('</Wix>')

out = os.path.join(PROJECT_ROOT, "releases", "_msi", "files.wxs")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("files.wxs -> %s（组件 %d / 目录 %d）" % (out, len(files), len(dirs)))
