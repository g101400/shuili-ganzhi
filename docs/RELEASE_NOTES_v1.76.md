# 水利感知项目一张图 V1.76 · 发布说明（GitHub Release 正文，tag v1.76）

> 构建批次：2026-10-24　工程：`E:\dev\ganzhi\perc`（main @ 第 6 次提交后）　产物哈希对账：`docs/RELEASE_MANIFEST.md`

## 本版本要点

- **四端交付**：Windows（exe 免安装 + msi 安装包）、统信 UOS deb（amd64 / arm64 / mips64el 三架构）、Android APK（release 签名）、iOS PWA 包。
- **包名与签名归位**：Android `com.shuili.ganzhi` / versionName 1.76 / code 76；APK 采用正式发布签名（v2 scheme verified，`CN=Shuili Ganzhi Release`，证书 SHA-256 见发布清单）。
- **质量门禁**：11 断言回归门禁全过（webroot 与交接基线 33 文件 0 漂移、webroot 禁 .bak、密钥零泄露四端成员级扫描、7 产物实存），并通过 4 类假漂移反向验证（全部 exit=1 拦截）。
- **已知缺陷修复**：msi 二次构建嵌套夹带（未排除旧 `*.msi`）已修复，幂等构建验证通过（36 组件 / 12.86MB 稳定）。
- **功能 0 删除**：9 大菜单逐项回归 + 统计/列表视图功能页实测，0 新增报错（仅预期密钥 404）。

## 产物清单（7 项，SHA256 见 docs/RELEASE_MANIFEST.md）

| 产物 | 说明 |
|---|---|
| `win/水利感知项目一张图.exe` | 单文件免安装（25.11MB），双击运行 |
| `win/水利感知项目一张图_Setup.msi` | 安装包（12.86MB，perMachine 需管理员） |
| `uos/shuili-ganzhi_1.76_amd64.deb` | UOS x86_64 |
| `uos/shuili-ganzhi_1.76_arm64.deb` | UOS 飞腾/鲲鹏 |
| `uos/shuili-ganzhi_1.76_mips64el.deb` | UOS 龙芯 |
| `android/水利感知项目一张图_V1.76.apk` | release 签名（8.43MB），minSdk 24 |
| `ios/水利感知项目一张图_V1.76_iOS_PWA.zip` | 解压 HTTPS 托管 → Safari 添加到主屏幕 |

## 安装要点

- **Windows**：exe 直接运行；msi 右键"以管理员身份安装"。
- **UOS**：`sudo dpkg -i shuili-ganzhi_1.76_<架构>.deb`，桌面入口「水利感知项目一张图」。
- **Android**：允许安装未知来源后直装；上架商店请核对发布清单中的签名指纹。
- **iOS**：解压 zip 后经 HTTPS 静态托管（工具：`build/serve_https.py` 自签名一键起服），iPhone 同一 Wi-Fi 内 Safari 访问 → 添加到主屏幕。

## 已知事项（交付前必读）

1. **密钥件零分发**：`ai_seed.js` / `secure_boot_cred.js` / `sec_crypt.js` 与离线瓦片（`offline_tiles/`）不随任何发布包分发（铁律）；仓库仅含 `*.demo.js` 模板，接收方按 `docs/BUILD.md` 自行落位真实件。
2. **msi 需管理员**：perMachine 安装，非管理员静默安装返回 1603 属预期。
3. **iOS Service Worker**：HTTP 托管可添加到主屏幕；SW 离线缓存需 HTTPS 且证书受信（自签名需在 iPhone「设置 → 通用 → VPN 与设备管理」信任描述文件）。
4. **deb 真机验证**：三架构 deb 均通过结构自校验（10/10），UOS 真机 `dpkg -i` 实测待接收方执行。

> AI生成
