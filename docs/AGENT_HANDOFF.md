# 水利感知项目一张图 · 智能体接手说明（AGENT_HANDOFF）

> 本文件是「详细说明」：**其他智能体依据本压缩包进行下一步开发的首要阅读对象**。
> 本工程是 `gujian4060` 单体仓库拆分出的三个独立工程之一（另两个：shuili 水利 / gujian 古建 / perc 感知），请只负责本工程。

---

## 0. 接手范围（必读）

- 你接手的是 **水利感知项目一张图** 的独立工程，目录 **`D:/Users/WorkBuddy/perc/`**（2026-10-24 起新机工程根为 **`E:\dev\ganzhi\perc`**，构建环境见 `docs/BUILD.md`）。
- 你是**唯一负责本项目**的智能体：**不要触碰** `D:/Users/WorkBuddy/shuili/`、`D:/Users/WorkBuddy/gujian/` 中**非本项目**的目录与 Git 仓库。
- 包名 `com.shuili.ganzhi`，版本 `1.77`（code 77，2026-10-24 感知设备基础数据全量更换），数据量 667 条监测记录（recordCount；源 F:\ganzhi\dev 五台账），视频监控 / 雨水情监测 / 大坝安全监测 / 地下水源监测 四大子系统。

## 1. 应用是什么

水利感知项目「一张图」：整合视频监控、雨水情监测、大坝安全监测、地下水源监测四大子系统，在地图上以四类设备图标（摄像头 / 雨量 / 大坝 / 地下水）展示感知点，支持离线瓦片，目标是在手机端与电脑端都能查看水利感知设施。

**已知特性：**
- 四大子系统：视频监控 / 雨水情监测 / 大坝安全监测 / 地下水源监测。
- 感知图例四类设备（摄像头/雨量/大坝/地下水），曾修复图例缺设备四类（已知坑）。
- 类型图形图标升级：地图标记按类型显示专属图形，图例同步图标化。
- AI 子菜单默认隐藏，可一键显示/隐藏。
- 运行维护菜单含「备忘录」；设置菜单含软件升级 / 数据导出 / 导入。
- 支持离线瓦片（offline_tiles/ + offline_manifest.json）；water_data.js 承载监测数据。
- 支持从奥维互动地图（OvitalMap）采集对象经 ovobj_bridge.js 桥接导入；mdb_reader.js 读取 Access(.mdb)。

## 2. 技术栈与运行方式

- 纯前端 **Web 单页应用**（HTML/JS + Leaflet 地图），由原生壳承载：
  - Windows → WebView2（`native-shell/win-webview2/Program.cs`）
  - 统信 UOS / 麒麟 → PyQt6（`native-shell/uos-pyqt6/main.py`）
  - iOS → 可托管 PWA zip（本工程无独立壳，参考 shuili 的 water-ios 思路）
- **本地运行**（开发与调试）：
  ```bash
  cd D:/Users/WorkBuddy/perc/webroot
  python -m http.server 8080
  # 浏览器打开 http://localhost:8080/index.html
  ```
- 数据来源：data.js 内嵌 667 条监测记录（v1.77 起由 build/gen_perception_data.py 从 F:\ganzhi\dev 五台账重建）；water_data.js 内嵌四大子系统监测数据；mdb_reader.js 读取 Access(.mdb)；ovobj_bridge.js 桥接奥维对象；可经「设置 → 数据导入/导出」增量更新。offline_tiles/ 为离线地图瓦片（体积大、可再生成，不入库）。

## 3. 源码文件地图（webroot/）

- `index.html` —— 入口页，加载 `app.js` 与各模块。
- `app.js` —— **主逻辑（最大文件，切勿整段替换）**：地图渲染、菜单系统、交互、数据绑定。改动须走增量 diff。
- `data.js` / `data.demo.js` —— 内嵌 667 条监测记录；**真实 `data.js` 已入库**，仅 `data.demo.js` 作模板/脱敏样例。
- `water_data.js` / `water_data.demo.js` —— 四大子系统监测数据；**真实 `water_data.js` 已入库**，仅 demo 模板另存。
- `ai_module.js` —— AI 助手子模块（默认隐藏，可一键切换显示）。
- `kb_core.js` / `kb_rag.js` / `kb_source.js` / `kb_vector.js` / `kb_building_seed.js` —— 本地知识库（核心 / 检索 / 来源 / 向量 / 建筑种子），均已入库。
- `ai_seed.demo.js` / `ai_seed.js` —— AI 知识种子；**`ai_seed.js` 是密钥，不入库、不进 ZIP**，仅 `ai_seed.demo.js` 模板入库。
- `mdb_reader.js` —— 读取 Access `.mdb`（奥维/外部采集数据导入）。
- `ovobj_bridge.js` —— 奥维互动地图（OvitalMap）对象桥接导入。
- `secure_boot.js` / `secure_boot_cred.js` —— 安全启动与凭据；**`secure_boot_cred.js` 含访问口令凭据，敏感，不入库、不进 ZIP**（2026-10-23 安全复盘标记）。
- `ctx_menu.js` —— 右键 / 上下文菜单。
- `photo_gesture.js` —— 照片手势交互。
- `jszip.min.js` —— 前端 zip 库（数据导出）。
- `leaflet/` —— Leaflet 地图库（**必需，已进包**）。
- `ocr/` —— OCR 相关资源（**必需，已进包**）。
- `version.json` —— 版本信息（与工程根 `version.json` 同源）。
- `offline_manifest.json` —— 离线瓦片清单。
- `offline_tiles/` —— 离线地图瓦片目录（体积大、可再生成，**不入库、不进 ZIP**）。

> 本工程 ZIP 已包含运行所需的 `leaflet/`、`ocr/`、`data.js`、`water_data.js` 等真实资源，解压即可 `python -m http.server` 运行地图。
> 仅 `ai_seed.js` / `secure_boot_cred.js` / `offline_tiles/` 因密钥/体积原因未进包，需要时按 §7 说明补齐。

## 4. 原生壳与构建脚本

**native-shell/ 真实结构（本工程只有这两个壳）：**
- `win-webview2/Program.cs` —— WebView2 主程序，`AppContext.BaseDirectory/webroot` 承载网页，标题「水利感知项目一张图」。
- `win-webview2/build_msi.wxs` + `build_msi.bat` —— WiX 安装包（msi）定义与一键脚本。
- `win-webview2/ShuiliMap.csproj` / `app.ico` —— 工程定义与图标。
- `uos-pyqt6/main.py` —— PyQt6 主程序，`WEBROOT=<壳目录>/webroot` 承载网页。
- `uos-pyqt6/build_deb.sh` —— deb 打包脚本（`PKG=shuili-ganzhi`，支持 x86_64/arm64/mips64el）。
- `publish_win_perc/`、`*2026*.cs/.wxs/.bat/.py` 等 —— 构建产物与时间戳备份，**不进 ZIP**。

**build/ 脚本：**
- `build_all_v24.sh` / `build_all_guijian.sh` —— 一键构建入口（**内部绝对路径须重指本工程根 `D:/Users/WorkBuddy/perc`**）。
- `build_deb.py` / `build_deb_mips.py` —— deb 打包；`finalize_debs.sh` —— deb 收尾。
- `bump_v*.py` —— 版本号自增；`docs_v*.py` —— 文档生成。
- `publish_release.py` / `upload_release.sh` —— 发布/上传。
- `push.py` / `sync_*.py` / `sync_targets.py` —— 同步到各端；`targets/` —— Android Gradle 工程（包名 `com.shuili.ganzhi`）。
- `make_public_data.py` / `gen_feature_matrix.py` / `verify_myml_ar.py` —— 数据脱敏 / 特性矩阵 / 校验。

四端构建命令详见 `BUILD.md`。

## 5. 隔离红线（违反会互相影响，不可碰）

1. 目录隔离：三工程根目录互不相同（`shuili/` `gujian/` `perc/`），**不互相 import/require/共享子目录**；新代码只进本项目 `webroot/`。
2. Git 隔离：各自独立仓库（main 分支）、独立 remote `shuili-ganzhi`；**禁止**把三工程合进同一仓。
3. 文档/构建脚本隔离：各自根 README/BUILD 与 `build/` 副本，构建脚本绝对路径须重指本工程根。
4. 密钥隔离：`ai_seed.js` / `secure_boot_cred.js` 不入库、不进 ZIP；`.secrets/`、`.github_token` 永不入库。
5. 历史残留隔离：webroot 内**禁止任何 `.bak_*`**；备份落工程外 `perc/_bak_<日期>/`。
6. 发版隔离：GitHub 独立仓 `shuili-ganzhi` 推送；百度网盘独立子目录 `水利感知` 归置，互不复用。

## 6. 改动后回归门禁（每次必做）

- 菜单逐项实跑，确认功能与菜单 **0 删除、0 报错**。
- `webroot` 与基线逐文件对账（缺失 = 0、大小不一致 = 0）—— 见「功能与菜单 0 删除」门禁。
- 构建脚本绝对路径已重指本工程根 `D:/Users/WorkBuddy/perc`；出包前清同版本旧包，杜绝 `webroot_bak_*` 夹带污染。
- 密钥零泄露：`ai_seed.js` / `secure_boot_cred.js` / `offline_tiles/` 不入库、不进 ZIP（见 `.gitignore`）。

## 7. 版本与发版

- 版本号见工程根 `version.json`（buildDate 2026-10-22，含「三项目独立化」条目；2026-10-23 增补安全硬门禁）。
- **GitHub**：独立仓 `shuili-ganzhi`，`git push -u origin main`（remote 已配 token）。
- **百度网盘**：云端 `/apps/bypy/shuili-ganzhi/`（四端发版包 APK / exe+msi / deb / iOS zip）。
- **补齐未进包资源（如需）**：
  - AI 功能：复制 `webroot/ai_seed.demo.js` → `webroot/ai_seed.js` 并填值（密钥，勿入库）。
  - 访问凭据：`webroot/secure_boot_cred.js` 由安全流程单独下发，勿随包传播。
  - 离线瓦片：运行后按 `offline_manifest.json` 在本地生成 `webroot/offline_tiles/`。

## 8. 已知坑清单（经验内化）

- **webroot 内禁止 `.bak_*` / `webroot_bak_*`**：曾把安装包从 7.1MB 撑到 346.8MB；备份一律落工程外 `perc/_bak_<日期>/`。
- **禁用 `git add -A` 整目录**：曾误把旧密钥文件入库，须 `git reset` + 补 `.gitignore`（2026-10-23 安全复盘已硬门禁 scan_secrets）。
- **密钥/凭据零入包**：`ai_seed.js`（AI 种子）、`secure_boot_cred.js`（访问口令 AES-GCM 凭据）、`sec_crypt.js`、`offline_tiles/` 均不进 ZIP 与版本库。
- **门禁断言计数必须 >0 且等于登记下限**：零覆盖的「全部通过」是假绿；须可构造反例做反向验证（注入假漂移须 exit≠0）。
- **探针必须锚定 PROJECT_ROOT**：CWD 相对路径换目录跑不报错、只给假绿灯。
- **日志成功 ≠ 产物实存**：发布后须机器对账产物真实存在。
- **修复件须进生产实跑**：躺 `_bak_*` 不算修好。

## 9. 本压缩包内容清单

```
perc_handoff.zip
├── webroot/          应用源码（含 leaflet/ ocr/ 运行必需资源；无 .bak_*/时间戳备份/密钥/离线瓦片）
├── native-shell/     原生壳源码（win-webview2 / uos-pyqt6；剔除 publish_*/时间戳备份/构建产物）
├── build/            构建与发版脚本（剔除 __pycache__/*.pyc）
├── docs/             README.md / BUILD.md / 交接卡.md / CHANGELOG.md / AGENT_HANDOFF.md
├── version.json      版本信息
└── .gitignore        工程级忽略规则
```

> 解压后进入 `webroot/` 跑 `python -m http.server 8080` 即可直接查看地图（无需联网、无需兄弟工程）。

## 10. 接手检查清单（收到包后照做）

1. [ ] 解压到**独立目录**（不要解压进 shuili/ 或 gujian/ 目录内）。
2. [ ] 读 `docs/AGENT_HANDOFF.md` 全文（本文件）。
3. [ ] 本地运行：`cd webroot && python -m http.server 8080` → 浏览器开 `index.html`，确认地图与四类设备图例正常。
4. [ ] 逐项点菜单，确认功能与菜单 **0 删除、0 报错**。
5. [ ] 改代码只动本工程 `webroot/`；提交前 `git status` 确认无 `ai_seed.js` / `secure_boot_cred.js` / `offline_tiles/` 泄露。
6. [ ] 发版走 GitHub `shuili-ganzhi` 独立仓 + 百度网盘 `水利感知` 独立目录，不碰另两工程。

> AI生成
