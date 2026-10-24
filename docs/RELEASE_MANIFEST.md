# 发布清单（RELEASE_MANIFEST）· 水利感知项目一张图 V1.77

> 生成时间：2026-10-24 23:45:57　批次：本机 E 盘独立工程（E:\dev\ganzhi\perc）　产物不入库，哈希随重建批次变化，对账以最近一次构建为准。

## 四端产物对账（7 项）

| 产物 | 路径（相对工程根） | 大小 | SHA256 |
|---|---|---:|---|
| Win exe | releases\win\水利感知项目一张图.exe | 26,334,283 B | `c2dce38363e4b3509b7f98b529c503ba2945174d476617941c7bcebe125bb33d` |
| Win msi | releases\win\水利感知项目一张图_Setup.msi | 13,406,208 B | `eb40de8a50e0f7f1c03973a80e8f7bf32ff6ac925aec186f78e83d35f489d8bd` |
| UOS deb amd64 | releases\uos\shuili-ganzhi_1.77_amd64.deb | 8,123,032 B | `82f019da6ea8450e437ad316e654e8f10788e12412839ee93566cbb67bf650e2` |
| UOS deb arm64 | releases\uos\shuili-ganzhi_1.77_arm64.deb | 8,123,036 B | `bfdcbd99d93fdf537ac90bcdf431cb553df043747fdd5801921de1b060020751` |
| UOS deb mips64el | releases\uos\shuili-ganzhi_1.77_mips64el.deb | 8,123,040 B | `135699270e25c41440450638c55a0bbf5b0e3800da732e401bbab3540beb1ace` |
| Android APK | releases\android\水利感知项目一张图_V1.77.apk | 8,828,837 B | `7fe5155cc9321c6c2d08498dbd6fb4df17511dc43cc5cb57ab1e993b7eaa58ec` |
| iOS PWA zip | releases\ios\水利感知项目一张图_V1.77_iOS_PWA.zip | 8,737,214 B | `07d6200a7da7b5f3b82c01a23f1fbf2509049bab7644cdfa42b74d21c9fa8c47` |

## Android APK 签名身份

- 签名方案：APK Signature Scheme v2（apksigner verify 实测 verified）
- 证书 DN：`CN=Shuili Ganzhi Release, OU=Shuili, O=Shuili, L=Beijing, ST=Beijing, C=CN`
- 证书 SHA-256 指纹：`6696e4e354d41324e0e9fc155b98e768ba7389443732c0bd5ab8ad343178726e`
- keystore/口令：仓库外 `E:\dev\ganzhi\tools\keystore\`（密钥零入库，换机需随发版人保管迁移）

## 门禁状态（生成时实况）

- `通过 11/11`（exit=0，脚本：build/gate_check.py，11 断言）

## 交付与上架要点

- Win：exe 免安装直接运行；msi 为 perMachine 安装需管理员权限。
- UOS：`sudo dpkg -i shuili-ganzhi_*.deb`（按机器架构选包），桌面入口「水利感知项目一张图」。
- Android：release APK 可直接安装；上架商店需使用本清单指纹对应 keystore 复签校验。
- iOS：zip 解压后经 HTTPS 静态托管，Safari 打开 → 添加到主屏幕（PWA）。

> AI生成
