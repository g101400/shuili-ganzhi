# 水利感知项目一张图 · 构建手册

> 构建脚本继承自单体仓库 `gujian4060`，**所有绝对路径须重指为本工程根**。
> 本工程只构建自己的 `webroot/`，绝不引用兄弟工程。

## 本机构建环境（2026-10-24 起，工程根 E:\dev\ganzhi\perc）

- 工具链与缓存全部落 E 盘（`E:\dev\ganzhi\tools\`）：Gradle 8.10.2、Android SDK（platform-tools / platforms;android-34 / build-tools;34.0.0）、gradle-home / nuget-packages / npm-cache / dotnet-home。
- 用户级环境变量已重定向：`GRADLE_USER_HOME` / `ANDROID_HOME` / `ANDROID_SDK_ROOT` / `NUGET_PACKAGES` / `NPM_CONFIG_CACHE` / `DOTNET_CLI_HOME` / `PERC_PROJECT_ROOT`。会话加载：`. E:\dev\ganzhi\tools\env.ps1`。
- JDK 沿用系统既有 `C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot`（未新增 C 盘文件）。
- **本机四端构建命令**（产物落 `releases/`）：
  - Win：`dotnet publish native-shell\win-webview2\ShuiliMap.csproj -c Release -r win-x64 -o releases\win`（构建前把 `webroot\` 复制到 `native-shell\win-webview2\webroot`）
  - Win msi：`powershell -File build\build_msi.ps1`（WiX v7 方案；wix 工具在 E:\dev\ganzhi\tools\dotnet-home\.dotnet\tools，UI 扩展缓存 junction 至 E:\dev\ganzhi\tools\wix-extensions；msi 为 perMachine 需管理员安装）
  - UOS deb：`python build\build_deb_pure.py [amd64|arm64|mips64el]`（纯 Python，零外部依赖）
  - Android APK：`build\targets\android` 下执行 gradle `--no-daemon clean assembleDebug`（包名已归位 `com.shuili.ganzhi`，webroot 同步至 `app\src\main\assets\www`）
  - iOS PWA：`python build\build_ios_pwa.py`（可托管 zip，工程 webroot 零改动）
  - 回归门禁：`python build\gate_check.py`（基线对账 / 密钥零入包 / 7 项产物实存，11 项断言）
- 新脚本全部以脚本位置推导 `PROJECT_ROOT`（无硬编码绝对路径），天然满足「路径锚定工程根」铁律。

## Git 独立仓库（2026-10-24 落地）

- 本地仓库已初始化（`main` 分支，首次提交 4f5047b，109 文件），隔离红线第 2 条落地。
- 提交方式：靶向 `git add .gitignore version.json webroot docs native-shell build`（**禁 add -A**），提交前 porcelain 核查密钥/备份 0 泄露。
- `.gitignore` 已补：`releases/`（产物不入库，仅留 README）、`native-shell/win-webview2/webroot/`（生成镜像）、Android gradle 缓存/`app/build/`/`assets/www/`（同步再生）、`local.properties`、`releases/_msi/`。
- remote `shuili-ganzhi` 待接入：本机未提供 GitHub token，需要发版时补 `git remote add origin <url>` 后 `git push -u origin main`（凭据走安全流程，勿入库）。

## 门禁反向验证（防假绿铁律实证，2026-10-24）

隔离副本注入 4 类假漂移，门禁全部 exit=1 拦截，恢复后复跑 11/11 PASS：

| 注入反例 | 预期拦截点 | 实测 |
|---|---|---|
| webroot\data.js 追加 1 字节 | 基线大小一致=0漂移 | exit=1 ✓ |
| webroot 混入 app.js.bak_test | webroot 无 .bak_* | exit=1 ✓ |
| releases\ios\ 混入 ai_seed.js | 密钥零泄露 | exit=1 ✓ |
| 删除 Android APK 产物 | 产物实存对账 | exit=1 ✓ |

## 原生壳

- win-webview2：Windows WebView2（Edge 内核）原生壳，窗口标题「水利感知项目一张图」
- uos-pyqt6：统信 UOS / 麒麟 PyQt6 + QWebEngineView 原生壳，窗口标题「水利感知项目一张图」
- （无独立 iOS 壳；如需 iOS 走可托管 PWA 思路，参考 shuili 工程的 water-ios 壳）

## 各端构建

### Windows（exe / msi）
- 壳源码：`native-shell/win-webview2/`（`Program.cs` 以 `AppContext.BaseDirectory/webroot` 承载网页，标题「水利感知项目一张图」）。
- 出 exe：`dotnet publish -c Release`（生成 `publish_win_perc/` 落地产物，已 `.gitignore`）。
- 出 msi：安装 [WiX Toolset](https://wixtoolset.org/) 并配置 `WIX` 环境变量后，双击/运行
  `native-shell/win-webview2/build_msi.bat`（基于 `build_msi.wxs`），产出 `水利感知项目一张图_Setup.msi`。

### 统信 UOS / 麒麟（deb，x86_64 / arm64 / mips64el）
- 壳源码：`native-shell/uos-pyqt6/`（`main.py` 以 `WEBROOT=<壳目录>/webroot` 承载网页）。
- 出包（在 UOS 本机执行）：
  ```bash
  sudo bash native-shell/uos-pyqt6/build_deb.sh            # 默认架构
  ARCH=mips64el sudo bash native-shell/uos-pyqt6/build_deb.sh   # 显式指定 mips64el
  ```
  产出 `shuili-ganzhi_<VERSION>_<ARCH>.deb`，依赖 `python3-pyqt6` 与 `python3-pyqt6.qtwebengine`。

### Android（APK）
- 工程：`build/targets/android/`（Gradle 工程，包名须为 `com.shuili.ganzhi`）。
- 入口：`build/targets/android/build_apk.sh`；或顶层 `build/build_all_v24.sh`。

### iOS（PWA 可托管包）
- 本工程**无独立 iOS 壳**，如确需可复用 shuili 工程的 `native-shell/water-ios/build_ios_zip.py` 思路生成可托管 zip（非 App Store .ipa）。

## 通用构建脚本（build/）

- `build_all_v24.sh` / `build_all_guijian.sh` —— 一键构建入口（**内部绝对路径须重指为本工程根**）。
- `build_deb.py` / `build_deb_mips.py` —— deb 打包；`finalize_debs.sh` —— deb 收尾。
- `bump_v*.py` —— 版本号自增；`docs_v*.py` —— 文档生成。
- `publish_release.py` / `upload_release.sh` —— 发布/上传。
- `push.py` / `sync_*.py` / `sync_targets.py` —— 同步到各端；`targets/` —— Android Gradle 工程。
- `make_public_data.py` / `gen_feature_matrix.py` / `verify_myml_ar.py` —— 数据脱敏 / 特性矩阵 / 校验。

## 关键规则（防互相影响 / 防假绿）

1. 每个工程只构建自己的 `webroot/`，绝不引用兄弟工程目录。
2. 构建脚本路径用 `PROJECT_ROOT` 锚定，禁止 CWD 相对路径。
3. 出包前清同版本旧包，避免 `_bak_*` / `webroot_bak_*` 夹带污染（曾把安装包撑大 50 倍）。
4. 门禁断言计数必须 >0 且等于登记下限，零覆盖「全部通过」是假绿。

> AI生成
