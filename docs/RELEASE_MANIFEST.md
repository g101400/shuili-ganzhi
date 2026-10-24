# 发布清单（RELEASE_MANIFEST）· 水利感知项目一张图 V1.76

> 生成时间：2026-10-24 21:03:55　批次：本机 E 盘独立工程（E:\dev\ganzhi\perc）　产物不入库，哈希随重建批次变化，对账以最近一次构建为准。

## 四端产物对账（7 项）

| 产物 | 路径（相对工程根） | 大小 | SHA256 |
|---|---|---:|---|
| Win exe | releases\win\水利感知项目一张图.exe | 26,334,283 B | `bdf76b543465bb5087ea04dc6e491fbca328916ca475b1626a27171cb161619e` |
| Win msi | releases\win\水利感知项目一张图_Setup.msi | 13,479,936 B | `82d57b907fc114282982d2015f10aca52a2cab6ee2abce31645e03c5c35e0df1` |
| UOS deb amd64 | releases\uos\shuili-ganzhi_1.76_amd64.deb | 8,121,448 B | `3afb52375a0c24ca6606da1d785b2df121d0bcb7f870819f7767464f36ff9bd7` |
| UOS deb arm64 | releases\uos\shuili-ganzhi_1.76_arm64.deb | 8,121,444 B | `1152e625796cc91b751259ff3472401fe3ec0981b74c60ac6ece6906f1281c39` |
| UOS deb mips64el | releases\uos\shuili-ganzhi_1.76_mips64el.deb | 8,121,448 B | `e323447060d10520d56c1d849e53527ef22cd34df4db0f7953c75a55714070fe` |
| Android APK | releases\android\水利感知项目一张图_V1.76.apk | 8,836,845 B | `fa4c38497c6d66c22554a774cbe13d195488d3549161c415bc90c5f2d1ab30f4` |
| iOS PWA zip | releases\ios\水利感知项目一张图_V1.76_iOS_PWA.zip | 8,745,222 B | `9d664e310525153887ea6d24245f169489f8d0df731a3c848fb590bba1fa46f9` |

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
