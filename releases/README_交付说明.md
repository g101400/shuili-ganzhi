# 水利感知项目一张图 V1.76 · 四端部署包交付说明

工程根：`E:\dev\ganzhi\perc`（独立工程，不引用兄弟工程，遵循交接包隔离红线）
构建日期：2026-10-24　门禁：11/11 全过（基线 0 漂移 / 密钥零入包 / 7 项产物实存）

## 部署包清单

| 平台 | 文件 | 大小 | 安装方式 |
|---|---|---|---|
| Windows | `win\水利感知项目一张图.exe` | 26.3 MB | 双击运行（WebView2 单文件，含 webroot，需 .NET 8 运行时） |
| Windows | `win\水利感知项目一张图_Setup.msi` | 12.8 MB | 管理员双击安装（带安装向导：选目录/许可/快捷方式） |
| 统信 UOS/麒麟 (x86_64) | `uos\shuili-ganzhi_1.76_amd64.deb` | 8.12 MB | `sudo dpkg -i shuili-ganzhi_1.76_amd64.deb`（依赖 python3-pyqt6 / qtwebengine） |
| 统信 UOS/麒麟 (arm64) | `uos\shuili-ganzhi_1.76_arm64.deb` | 8.12 MB | 同上（ARM 机型用） |
| 统信 UOS/麒麟 (mips64el) | `uos\shuili-ganzhi_1.76_mips64el.deb` | 8.12 MB | 同上（兆芯/龙芯 mips 机型用） |
| Android | `android\水利感知项目一张图_V1.76.apk` | 9.7 MB | 直接安装（包名 com.shuili.ganzhi，debug 签名，minSdk 24） |
| iOS | `ios\水利感知项目一张图_V1.76_iOS_PWA.zip` | 8.75 MB | HTTPS 托管解压内容 → Safari「添加到主屏幕」 |

## 各端要点

- **Windows exe**：`dotnet publish` 单文件发布（net8.0-windows / WebView2 / RuntimeIdentifier win-x64），实跑验证进程正常启动。
- **Windows msi**：WiX v7 方案（工具与扩展全落 E 盘，`build\build_msi.ps1` 一键重建）。已验证：Dialog 表 21 项安装向导完整、ProductName/Version 中文正确、cab 内容与源产物 36/36 MD5 全对账。注意：msi 为 perMachine 安装，需管理员权限安装；非管理员静默安装会报 1603（InstallFiles 本身成功，仅为写入系统 Installer 区权限不足）。
- **UOS deb**：纯 Python 打包（`build/build_deb_pure.py`，ar+tar.xz 合成，不依赖 dpkg/WSL），含 /opt/shuili-ganzhi/{webroot,main.py}、/usr/bin 启动器、desktop 入口，三架构（amd64/arm64/mips64el）各 10/10 自校验通过。
- **Android APK**：包名/版本已按交接铁律归位（`com.shuili.ganzhi` / versionCode 76 / versionName 1.76 / 标签「水利感知项目一张图」），webroot 全量内嵌 `assets/www/`（33 文件），aapt 验证通过。发布签名 keystore 未随交接包提供，按脚本设计自动降级 debug 签名。
- **iOS PWA zip**：39 条目 = webroot 基线 33 文件 + PWA 增强层（manifest / sw.js / apple-touch-icon / 部署说明），index.html 仅在 zip 副本内注入，工程 webroot 零改动。已实机验证：解压后 HTTP 托管页面渲染与工程原版一致（四子系统图例/1125 条记录/菜单完整），manifest/sw.js/icons 全部 200 可达。

## 密钥与安全（铁律）

本交付不含 `ai_seed.js` / `secure_boot_cred.js` / `sec_crypt.js` / `offline_tiles/`（密钥零入包，成员级扫描通过）。需要 AI/口令功能时按 `docs/AGENT_HANDOFF.md` §7 单独补齐，勿入库入包。

## 回归门禁复跑

```
powershell -File E:\dev\ganzhi\perc\build\build_all.ps1 -Only gate   # 一键门禁
python E:\dev\ganzhi\perc\build\gate_check.py                     # 等价直跑
```

## 门禁防假绿实证（2026-10-24）

隔离副本注入 4 类假漂移（基线字节漂移 / webroot .bak 混入 / 产物目录混入密钥 / 删产物），门禁全部 exit=1 拦截；恢复后复跑 11/11 PASS。门禁具备真实拦截力，非零覆盖假绿。

## Git 独立仓库

- 本地 `main` 分支已建（首次提交 4f5047b，109 文件，靶向 add、密钥零入库）。
- 发版接 GitHub `shuili-ganzhi`：补 remote + token 后 `git push -u origin main`（凭据安全流程下发，勿入库）。

## 一键重建

```
powershell -File E:\dev\ganzhi\perc\build\build_all.ps1     # 四端全量 + 门禁（约 5 分钟）
```

> AI生成
