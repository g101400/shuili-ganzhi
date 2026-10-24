# 水利感知项目一张图 V1.77 · 四端部署包交付说明

工程根：`E:\dev\ganzhi\perc`（独立工程，不引用兄弟工程，遵循交接包隔离红线）
构建日期：2026-10-24　门禁：**12/12 全过**（基线 0 漂移[数据白名单登记] / 密钥零入包 / 7 项产物实存 / 旧版产物零夹带）
本版主题：**感知设备基础数据全量更换**（五份台账重建 667 条；详见 `docs/RELEASE_NOTES_v1.77.md`）
发布地址：https://github.com/g101400/shuili-ganzhi/releases/tag/v1.77

## 部署包清单

| 平台 | 文件 | 大小 | 安装方式 |
|---|---|---|---|
| Windows | `win\水利感知项目一张图.exe` | 26.3 MB | 双击运行（WebView2 单文件，含 webroot，需 .NET 8 运行时） |
| Windows | `win\水利感知项目一张图_Setup.msi` | 13.4 MB | 管理员双击安装（带安装向导：选目录/许可/快捷方式） |
| 统信 UOS/麒麟 (x86_64) | `uos\shuili-ganzhi_1.77_amd64.deb` | 8.12 MB | `sudo dpkg -i shuili-ganzhi_1.77_amd64.deb`（依赖 python3-pyqt6 / qtwebengine） |
| 统信 UOS/麒麟 (arm64) | `uos\shuili-ganzhi_1.77_arm64.deb` | 8.12 MB | 同上（ARM 机型用） |
| 统信 UOS/麒麟 (mips64el) | `uos\shuili-ganzhi_1.77_mips64el.deb` | 8.12 MB | 同上（龙芯 mips 机型用） |
| Android | `android\水利感知项目一张图_V1.77.apk` | 8.83 MB | 直接安装（包名 com.shuili.ganzhi / code 77，**release 签名 v2 verified**，minSdk 24） |
| iOS | `ios\水利感知项目一张图_V1.77_iOS_PWA.zip` | 8.74 MB | HTTPS 托管解压内容 → Safari「添加到主屏幕」 |

## 各端要点

- **Windows exe**：`dotnet publish` 单文件发布（net8.0-windows / WebView2 / win-x64）。
- **Windows msi**：WiX v7 方案（`build\build_msi.ps1` 一键重建）。Dialog 表 21 项向导完整、cab 36/36 MD5 对账。perMachine 安装需管理员；非管理员静默装报 1603 属预期。
- **UOS deb**：纯 Python 打包（`build/build_deb_pure.py`），三架构各 10/10 自校验；**成员级抽查已验 v1.77 数据内嵌（667 条）**。
- **Android APK**：`com.shuili.ganzhi` / versionCode 77 / versionName 1.77；**正式发布签名**（keystore 在仓库外 `E:\dev\ganzhi\tools\keystore\`，v2 scheme verified，证书指纹见 `docs/RELEASE_MANIFEST.md`）；webroot 全量内嵌，成员级抽查 667 条确认。
- **iOS PWA zip**：39 条目 = webroot 33 文件 + PWA 增强层；`build\serve_https.py` 自签名 HTTPS 一键托管（附 `/_dev_cert.crt` 下载路由与真机信任步骤）。
- **数据说明**：感知设备 667 条（视频监控 431 / 雨水情 26 / 大坝 41 / 地下 169），全部真实坐标；水工建筑物层 557 条不变。**老用户升级**：已初始化过的浏览器/设备需「数据维护 → 恢复出厂」载入新台账（手工增改请先导出备份）。

## 密钥与安全（铁律）

本交付不含 `ai_seed.js` / `secure_boot_cred.js` / `sec_crypt.js` / `offline_tiles/`（密钥零入包，四端成员级扫描通过）。APK 发布 keystore 与口令在仓库外 `tools\keystore\`，**丢失将无法同签名升级**，请妥善备份。

## 回归门禁复跑

```
powershell -File E:\dev\ganzhi\perc\build\build_all.ps1 -Only gate   # 一键门禁（12 断言）
python E:\dev\ganzhi\perc\build\gate_check.py                        # 等价直跑
python E:\dev\ganzhi\perc\build\verify_release.py                    # 7 产物 SHA256 验包
```

## 门禁防假绿实证（2026-10-24）

5 类假漂移注入全部 exit=1 拦截：基线字节漂移 / webroot .bak 混入 / 产物目录混入密钥 / 删产物 / **旧版产物夹带（V1.76 假包）**；恢复后复跑 12/12 PASS。

## Git 与发版

- remote `origin` 已接 GitHub（g101400/shuili-ganzhi，无 token 干净 URL）；v1.76 / v1.77 已推送并建 Release，附件 7/7 字节数对账一致。
- 离线灾备：`E:\dev\ganzhi\backup\shuili-ganzhi_v1.77.bundle`（含全部提交+tag，还原演练通过）。
- 一键重建：`powershell -File E:\dev\ganzhi\perc\build\build_all.ps1`（约 5 分钟，exit=0 为过）。

> AI生成
