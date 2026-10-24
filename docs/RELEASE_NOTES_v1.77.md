# 水利感知项目一张图 V1.77 · 发布说明（tag v1.77）

> 构建批次：2026-10-24　主题：**感知设备基础数据全量更换**　上一版：v1.76

## 本版本要点

- **设备数据全量重建**：以 `F:\ganzhi\dev` 五份感知台账为唯一数据源，清除原 1125 条内置设备，重建为 **667 条**（视频监控 431 / 雨水情监测 26 / 大坝安全监测 41 / 地下水源监测 169）。
- **坐标体系一致直用**：台账奥维坐标与原库同基准（同站点坐标逐位一致；CGCS2000/WGS84 同域），无偏移转换。视频监控 431 点位经"归一名称+坐标"跨 6 个 sheet 去重合并；渠道太阳能 58 站点与视频台账重合并入（供电/IP/运维建议增补进 attrs）。
- **信息量增强**：雨水情新增测量频率/安装地址/管理单位等 attrs；大坝与地下水源修正中类（chan）取值（修复"载体设施中类*"误命中列）。
- **生成器入库可复现**：`build/gen_perception_data.py`（台账 → data.js + kb_building_seed.js 一键重建，`--dry-run` 预览），知识库种子（KB_BUILDING_SEED）与主数据 id 对齐同步重建。
- **老用户升级提示**：内置种子仅在首次启动播种；已初始化过的浏览器请用「数据维护 → 恢复出厂」载入 v1.77 台账（层内手工增改会被重置，请先导出备份）。
- **功能 0 删除**：9 大菜单/四类图例/统计与列表视图回归通过，浏览器冒烟 0 新增报错（仅预期密钥 404）。

## 产物（7 项，SHA256 见 docs/RELEASE_MANIFEST.md）

| 产物 | 说明 |
|---|---|
| `ShuiGanZhi_V1.77_win_x64.exe` | 单文件免安装 |
| `ShuiGanZhi_V1.77_Setup.msi` | perMachine 需管理员 |
| `shuili-ganzhi_1.77_{amd64,arm64,mips64el}.deb` | UOS 三架构 |
| `ShuiGanZhi_V1.77.apk` | release 签名 v2 verified |
| `ShuiGanZhi_V1.77_iOS_PWA.zip` | 解压 HTTPS 托管 |

## 门禁与验证

- 回归门禁 11/11（webroot 基线对账含数据文件白名单登记：data.js / kb_building_seed.js / version.json / app.js 允许业务更新，其余文件强对账不变）。
- 产物成员级抽查：APK / iOS zip / deb 内 `PERCEPTION_DATA=667、version=1.77`；四端产物 SHA256 逐项验包 7/7 PASS。

> AI生成
