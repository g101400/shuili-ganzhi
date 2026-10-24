# 水利感知项目一张图 · 版本变更记录

当前版本：**1.76**（code 76）　buildDate：**2026-10-24**（本机构建环境落地）

## 2026-10-24 · 发版最后一公里配套（同日第三批）

- `docs/RELEASE_NOTES_v1.76.md`：GitHub Release 正文（要点/产物表/四端安装/已知事项，与 RELEASE_MANIFEST 呼应）。
- `build/upload_baidupan.ps1`：百度网盘一键上传（bypy 幂等装至 `tools\pylibs` 零 C 盘；仅传 7 项清单产物，缺失即中止防半包；云端 list 对账）。首次运行需粘贴授权码。
- `build/serve_https.py`：iOS PWA 自签名 HTTPS 一键托管（Git openssl 证书落 `tools\certs` 不入库；`/_dev_cert.crt` 路由供 iPhone 下载描述文件；附真机信任步骤）。冒烟中修复真缺陷：服务目录未锚定（-d 不生效致 404），改 `functools.partial(directory=)` 显式锚定。
- bypy 1.8.9 预装就绪；至此本机侧发版准备全部闭环，仅余外部凭据动作（GitHub token / 网盘授权码）。

## 2026-10-24 · 发布签名与发版基建（同日第二批）

- APK 发布签名落地：keystore 生成于仓库外 `tools\keystore\`（RSA2048/30年/alias=shuili），口令文件同址——密钥零入库；`build.gradle` 签名段归位（清除 yijitun/GUJIAN_* 残留，支持 `SHUILI_KEYSTORE_PROPS` 环境变量或工程根 keystore.properties 定位，缺失自动降级 debug 签名保证公开库可构建）。
- `build_all.ps1` Android 段 assembleDebug→assembleRelease（产物 8.43MB），apksigner 实测 **v2 签名 verified**，证书 `CN=Shuili Ganzhi Release`。
- 发布清单基建：`build/gen_release_manifest.py` 生成 `docs/RELEASE_MANIFEST.md`（7 产物 SHA256+大小+APK 证书指纹+门禁实况），哈希随批次变化、对账以最近构建为准。
- 一键发版推送：`build/push_ready.ps1`（token 仅进程内存、一次性 URL 不入 .git/config、输出过滤回显；推送前三道预检：工作区干净/tag 存在/敏感件零入库复扫）。
- `build_apk.sh` 归位：清除古建/GujianApp/4060/旧机路径残留，路径锚定脚本位置、源指向 webroot、默认 assembleRelease。
- 发布标签：git tag `v1.76`；`.gitignore` 补 `build/targets/android/keystore.properties` 镜像位排除。

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
