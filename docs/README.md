# 水利感知项目一张图 · 工程说明

- 包名：`com.shuili.ganzhi`　版本：`1.76`（code 76）　数据量：1125 条监测记录（recordCount），视频监控 / 雨水情监测 / 大坝安全监测 / 地下水源监测
- 独立 Git 仓库：`shuili-ganzhi`（main 分支）
- 百度网盘子目录：`水利感知`
- 工程根：`D:/Users/WorkBuddy/perc/`

## 这是什么

水利感知项目「一张图」：整合视频监控、雨水情监测、大坝安全监测、地下水源监测四大子系统，在地图上以四类设备图标（摄像头 / 雨量 / 大坝 / 地下水）展示感知点，支持离线瓦片，目标是在手机端与电脑端都能查看水利感知设施。

## 目录（本工程已独立）

```
perc/
├── webroot/        应用源码（智能体编辑边界，功能/菜单 0 删除；含 leaflet/ ocr/ 运行必需资源）
├── native-shell/   原生壳源码（win-webview2 / uos-pyqt6，仅本项目）
├── build/          构建与发版脚本（继承自单体仓库 gujian4060，路径须重指本工程根）
├── docs/           README / BUILD / 交接卡 / CHANGELOG / AGENT_HANDOFF
├── version.json    版本信息
└── .gitignore      工程级忽略（ai_seed.js / secure_boot_cred.js / offline_tiles/ 等）
```

## 快速开始（本地运行）

```bash
cd D:/Users/WorkBuddy/perc/webroot
python -m http.server 8080
# 浏览器打开 http://localhost:8080/index.html
```

> 接手智能体请优先阅读本目录 **`AGENT_HANDOFF.md`**（接手详细说明），含隔离红线、回归门禁与发版流程。

## 原生壳

- win-webview2：Windows WebView2（Edge 内核）原生壳，窗口标题「水利感知项目一张图」
- uos-pyqt6：统信 UOS / 麒麟 PyQt6 + QWebEngineView 原生壳，窗口标题「水利感知项目一张图」
- （无独立 iOS 壳；如需 iOS 走可托管 PWA 思路，参考 shuili 工程的 water-ios 壳）

## 已知特性

- 四大子系统：视频监控 / 雨水情监测 / 大坝安全监测 / 地下水源监测。
- 感知图例四类设备（摄像头/雨量/大坝/地下水），曾修复图例缺设备四类（已知坑）。
- 类型图形图标升级：地图标记按类型显示专属图形，图例同步图标化。
- AI 子菜单默认隐藏，可一键显示/隐藏。
- 运行维护菜单含「备忘录」；设置菜单含软件升级 / 数据导出 / 导入。
- 支持离线瓦片（offline_tiles/ + offline_manifest.json）；water_data.js 承载监测数据。
- 支持从奥维互动地图（OvitalMap）采集对象经 ovobj_bridge.js 桥接导入；mdb_reader.js 读取 Access(.mdb)。

> 隔离规范与经验教训见 `AGENT_HANDOFF.md` 第 5/8 节。本工程是三独立工程（shuili / gujian / perc）之一，只负责本工程。
