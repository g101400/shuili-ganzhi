# 水利感知项目一张图 · 版本变更记录

当前版本：**1.77**（code 77）　buildDate：**2026-10-24**（感知设备基础数据全量更换）

## 2026-10-24 · v1.77 感知设备基础数据全量更换（重要）

- 数据源切换：以 `F:\ganzhi\dev` 五份台账（视频监控点位汇总+5分区 / 雨水情站点 / 大坝安全 / 地下水源 / 渠道太阳能）为唯一数据源，**清除原 1125 条内置设备，重建 667 条**（视频 431 / 雨水情 26 / 大坝 41 / 地下水 169）。
- 新增生成器 `build/gen_perception_data.py`（台账→data.js+kb_building_seed.js，--dry-run 预览；数据文件头标注自动生成勿手改）；知识库种子与主数据 id 对齐同步重建。
- 坐标体系核验：台账奥维坐标与原库同站点逐位一致（CGCS2000/WGS84 同域），直用无偏移；视频 6 sheet 按（归一名称+坐标6位）去重合并（跨 sheet 重名 84 对同坐标合并）；渠道太阳能 58 站无坐标→与视频重名并入 attrs（供电类型/IP/运行状态/运维建议）。
- 修复台账解析三坑：复合分组表头二级行定位、`载体设施中类*` 误命中真中类列、attrs 模板说明文本（"此处应填写…"）清洗；雨水情坐标在二级表头第 36/37 列。
- 版本 bump 1.76→1.77（version.json ×2 / app.js / gradle / deb / iOS / msi RTF / 各构建脚本版本引用与产物名 V1.77）；gate_check 数据白名单登记（data.js / kb_building_seed.js / version.json / app.js 允许业务更新，存在性保护不变，其余强对账）；门禁补"大小漂移清单"打印。
- 踩坑记录：Python 文本写默认 newline=None 会把 `\n` 翻译成 CRLF，bump 曾致 app.js 全行 diff（+16123B）——基线为 LF，已恢复并以 `newline='\n'` 显式锚定。
- 验证：浏览器冒烟（感知设备 667 条·水工建筑物 557 条、四类图例、菜单 0 缺失、0 新增报错）；APK/iOS/deb 成员级抽查 PERCEPTION_DATA=667 version=1.77；build_all 全量 exit=0；门禁 11/11；验包 7/7。

## 2026-10-24 · GitHub 发版完成（v1.76 上线）

- 发现目标仓 `g101400/shuili-ganzhi`（public）旧历史含敏感件 `webroot/secure_boot_cred.js`（CHANGELOG 2026-10-23 复盘同源事故痕迹）→ 经用户确认执行**删仓重建**（旧 commit 彻底消失，零残留），push 本地权威历史。
- 推送 `main`（10 commits）+ tag `v1.76`（token 一次性 URL、零落盘、输出过滤）。
- GitHub Release `v1.76` 建成（正文 RELEASE_NOTES_v1.76.md）：https://github.com/g101400/shuili-ganzhi/releases/tag/v1.76
- 附件 7/7 上传并字节数对账通过；踩坑记录：**curl.exe 命令行传 Unicode asset 名丢中文**（产出 default.exe 等坏名）→ 删坏件改用 Invoke-RestMethod + ASCII 安全名重传；PS5.1 `-Body` 中文字符串须转 UTF-8 字节 + `charset=utf-8`。
- 远端树敏感件终扫零命中；本次会话所用 PAT 建议立即撤销轮换。

## 2026-10-24 · 交付自验与离线灾备（同日第四批）

- `build/verify_release.py`：接收方验包脚本——解析 RELEASE_MANIFEST 的 7 产物表逐项重算 SHA256 对账（大小+哈希双校验，FAIL 提示刷新清单），实测 **7/7 PASS**。
- git bundle 离线灾备：`E:\dev\ganzhi\backup\shuili-ganzhi_v1.76.bundle`（7.98MB，--all 含 tag），bundle verify 完整历史 + **还原演练通过**（clone 得 6 提交/tag v1.76/HEAD 一致）——远程仓就绪前的唯一副本风险已缓解。
- iOS `_site` 解压就绪（39 文件，index/manifest/sw.js 齐），`serve_https.py` 可直接起服。
- RELEASE_MANIFEST 刷新对齐第 6 次提交后门禁实况（产物未重建，哈希不变）。
- `push_ready.ps1` 演练两轮抓出并修复真缺陷：网络不可达时 push 永久挂起（低速中止管不住 connect 阶段）→ 推送段改 **Job 兜底超时**（`-PushTimeout` 默认 120s）+ 低速中止双保险；演练矩阵实测：无 token / 工作区不干净 / 网络不可达三种失败路径均 exit=1 且 token 零回显，三道预检链生效。
- 待办移交：GitHub push（token）/ 百度网盘（授权码）为仅余的外部凭据动作。

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
