# 水利感知项目一张图 · 版本变更记录

当前版本：**1.76**（code 76）　buildDate：**2026-10-22**

## 2026-10-23 · 安全复盘（重要）

- 推送前硬门禁 `scan_secrets` + `.gitignore` 排除敏感件（`ai_seed.js` / `secure_boot_cred.js` / `sec_crypt.js`）。
- 修复件落库前复核，避免旧密钥随 `git add -A` 推上 public 仓。

## 2026-10-22 · 三项目独立化（重要）

- 从单体仓库 `gujian4060` 拆分为独立工程 `D:/Users/WorkBuddy/perc/`，webroot 独立、互不引用。
- 独立 Git 仓库（分支 main）、独立根文档与构建脚本、独立 .gitignore。
- 功能与菜单 **0 删除**（webroot 与源逐字节一致，已对账）。

## 已知特性要点（继承）

- 四大子系统：视频监控 / 雨水情监测 / 大坝安全监测 / 地下水源监测。
- 感知图例四类设备（摄像头/雨量/大坝/地下水），曾修复图例缺设备四类（已知坑）。
- 类型图形图标升级：地图标记按类型显示专属图形，图例同步图标化。
- AI 子菜单默认隐藏，可一键显示/隐藏。
- 运行维护菜单含「备忘录」；设置菜单含软件升级 / 数据导出 / 导入。
- 支持离线瓦片（offline_tiles/ + offline_manifest.json）；water_data.js 承载监测数据。
- 支持从奥维互动地图（OvitalMap）采集对象经 ovobj_bridge.js 桥接导入；mdb_reader.js 读取 Access(.mdb)。

> 完整迭代见各版本发布说明；本文件仅记录独立化后要点。接手智能体见 `AGENT_HANDOFF.md`。
