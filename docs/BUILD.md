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
  - Android APK：`powershell -File build\build_all.ps1 -Only android`（gradle assembleRelease；keystore 在仓库外 `tools\keystore\`，无则自动降级 debug 签名）
  - iOS PWA：`python build\build_ios_pwa.py`（可托管 zip，工程 webroot 零改动）
  - 回归门禁：`python build\gate_check.py`（基线对账[含数据白名单] / 密钥零入包 / 7 项产物实存 / 旧版产物零夹带，**12 项断言**）
  - 一键全量：`powershell -File build\build_all.ps1`（Web 冒烟→Win→deb×3→Android→iOS→门禁，exit=0 为过）
- 新脚本全部以脚本位置推导 `PROJECT_ROOT`（无硬编码绝对路径），天然满足「路径锚定工程根」铁律。

## 感知设备数据重建（2026-10-24 v1.77 新增）

- **生成器**：`python build\gen_perception_data.py [--dry-run]` —— 从 `F:\ganzhi\dev` 五份感知台账（视频监控点位汇总+5 分区 / 雨水情站点 / 大坝安全 / 地下水源 / 渠道太阳能）重建 `webroot\data.js` + `webroot\kb_building_seed.js`（id 对齐、知识库种子同步）；`--dry-run` 只出统计预览不写盘。
- **基线白名单**（gate_check 登记）：`data.js / kb_building_seed.js / version.json / app.js` 允许业务更新（仅验存在），其余文件仍与交接基线逐字节强对账。
- **换行铁律**：改 webroot 内 JS 必须保留原换行风格（基线 app.js 为 LF+BOM；Python 文本写需显式 `newline='\n'`，否则 CRLF 化致全行 diff）。
- **版本 bump 要点**：全链引用清单见 `build/gen_perception_data.py` 同批次脚本思路——version.json ×2 / app.js APP_VERSION+APP_BUILD_DATE / gradle versionCode+versionName / deb、iOS、msi、manifest、push、网盘脚本 VERSION / gate_check 产物名。
- **旧版产物清理**：deb/apk/zip 产物名带版本号，bump 后旧版残留即夹带——门禁第 12 断言拦截；发现命中时删除旧包后复跑（v1.77 曾实测 5 件残留全清）。

## Git 独立仓库与发版（2026-10-24 落地并上线）

- 本地仓库（`main` 分支）已与 GitHub 同步：remote `origin = https://github.com/g101400/shuili-ganzhi.git`（无 token 干净 URL，凭据走管理器）；v1.76 / v1.77 均已推送并建 Release（含 7 附件字节数对账）。
- 提交方式：靶向 `git add <路径>`（**禁 add -A**），提交前 porcelain 核查密钥/备份 0 泄露。
- `.gitignore` 要点：`releases/*`（反选 README_交付说明）、`native-shell/win-webview2/webroot/`（生成镜像）、Android gradle 缓存/`app/build/`/`assets/www/`（同步再生）、`local.properties`、`keystore.properties` 镜像位、`releases/_msi/`、`build/.temp/`。
- 发版推送：`powershell -File build\push_ready.ps1 -Owner <用户名>`（token 仅进程内存/一次性 URL/输出过滤；三道预检：工作区干净/tag 存在/敏感件零入库；`-PushTimeout` 兑底超时）。
- 离线灾备：`git bundle create E:\dev\ganzhi\backup\shuili-ganzhi_v1.77.bundle --all`（含全部提交+tag，还原演练通过）。

## 门禁反向验证（防假绿铁律实证，2026-10-24）

隔离副本注入 4 类假漂移，门禁全部 exit=1 拦截，恢复后复跑 PASS；另 v1.77 期新增第 5 类：

| 注入反例 | 预期拦截点 | 实测 |
|---|---|---|
| webroot\data.js 追加 1 字节 | 基线大小一致=0漂移 | exit=1 ✓ |
| webroot 混入 app.js.bak_test | webroot 无 .bak_* | exit=1 ✓ |
| releases\ios\ 混入 ai_seed.js | 密钥零泄露 | exit=1 ✓ |
| 删除 Android APK 产物 | 产物实存对账 | exit=1 ✓ |
| releases 混入 V1.76 假旧包 | 旧版产物零夹带（第12断言） | exit=1 ✓ |

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
