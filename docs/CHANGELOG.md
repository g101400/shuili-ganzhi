# 水利感知项目一张图 · 版本变更记录

当前版本：**1.76**（code 76）　buildDate：**2026-10-24**（本机构建环境落地）

## 2026-10-24 · 四端构建环境落地（新机 E 盘独立工程，重要）

- 依据 `perc_handoff.zip` 在 `E:\dev\ganzhi\perc` 落地独立工程；webroot 基线 33 文件 0 漂移。
- 工具链/缓存全落 E 盘（Gradle 8.10.2 / Android SDK 34 / NuGet / WiX v7 及扩展 junction），零 C 盘新增。
- 四端产物（7 项）：Win exe（单文件，实跑+WebView2 渲染进程双实证）、Win msi（WiX v7，Dialog 21 项完整、cab 36/36 MD5 对账、幂等构建）、UOS deb ×3 架构（纯 Python 打包器，各自校验 10/10）、Android APK（包名归位 `com.shuili.ganzhi`/v1.76 code 76，aapt 实证）、iOS PWA zip（实机 HTTP 托管渲染验证 11/11）。
- Git 独立仓库落地（main，靶向 add、密钥零入库）。
- 门禁 `gate_check.py` 11 断言；**反向验证 4 反例全拦**（基线字节漂移/webroot .bak/产物目录密钥/删产物 → exit=1）。
- 一键构建 `build_all.ps1` 全量实跑通过（Web 冒烟→Win→deb×3→Android→iOS→门禁，exit=0）。
- 修复：`gen_msi_files.py` 未排除 `*.msi` 导致二次构建嵌套夹带（25.39MB→修复回归 12.86MB，幂等验证通过）——与「出包前清旧包杜绝夹带」铁律同类问题的门禁补丁。
- Web 端菜单逐项回归：9 大菜单全展开 + 统计/列表视图功能页实测，0 新增报错（仅预期密钥 404）。

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

> AI生成
