#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 F:\\ganzhi\\dev 感知设备基础数据（5 个台账）生成 webroot/data.js 与 kb_building_seed.js。
用法：
  python build/gen_perception_data.py --dry-run   # 只输出统计预览，不写 webroot
  python build/gen_perception_data.py             # 生成并覆盖 webroot 数据文件
规则：
  - 数据源即真源：全量替换 PERCEPTION_DATA / KB_BUILDING_SEED（不保留旧设备）
  - 视频监控：xlsx 汇总 + 5 个分区 sheet，键=(归一名称, 坐标6位) 去重；无坐标条目键=(归一名称, office)
  - 渠道太阳能：无坐标，noCoord=true；名称与视频集合精确重合时并入已有条目（attrs 增补）
  - 雨水情/大坝/地下水：标准台账结构，坐标=采集点经纬度，CGCS2000 与现库同基准直用
  - id 重新顺序编号 p1..pN；PERCEPTION_META.offices/counts 重算；types 保留原结构
铁律：PROJECT_ROOT 由脚本位置锚定；生成文件头注明自动生成（勿手改）。
"""
import io, json, os, re, sys, datetime
from collections import Counter, OrderedDict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import openpyxl, xlrd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(PROJECT_ROOT, "webroot")
DEV = r"F:\ganzhi\dev"
DRY = "--dry-run" in sys.argv

VIDEO_XLSX = "26.04.13%2B视频监控点位要素信息汇总表-奥维坐标（一机一档基础%2B市级局级感知属性)1009.xlsx"
RAIN_XLSX = "250710 雨水情监测站点台账(更新奥维坐标).xlsx"
DAM_XLSX = "传感监测设施台账--大坝安全监测260618.xlsx"
GROUND_XLS = "传感监测设施台账--地下水源260615.xls"
SOLAR_XLSX = "渠道监控太阳能站点清单12.29xlsx.xlsx"
VIDEO_SHEETS = ["汇总", "水库68+4渠道", "渠道168", "渠道广播（84）", "大院安防55", "备用水源102"]

def norm_name(s):
    """归一名称：去空白、去前导序号前缀（001xxx/01xxx，2位以上数字才算序号，防误伤'1-1水源井'类短编号）"""
    t = re.sub(r"\s+", "", str(s or ""))
    t = re.sub(r"^[0-9]{2,4}(?=[^0-9])", "", t)
    return t

NOTE_PAT = re.compile(r"此处应填写|注：|示例|（填|填写说明")

def clean_attr(v):
    """attrs 值清洗：去换行；剔除模板说明性文本"""
    t = re.sub(r"\s*\n\s*", "", str(v or "")).strip()
    return "" if NOTE_PAT.search(t) else t

def fnum(x):
    if x in (None, ""):
        return None
    try:
        return round(float(x), 8)
    except Exception:
        return None

def clean(x):
    if x is None:
        return ""
    return str(x).strip()

def rows_from(fn, sheet=None):
    p = os.path.join(DEV, fn)
    out = []
    if fn.lower().endswith(".xls"):
        wb = xlrd.open_workbook(p)
        for sh in wb.sheets():
            if sheet and sh.name != sheet:
                continue
            out.append((sh.name, [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]))
    else:
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        for sh in wb.worksheets:
            if sheet and sh.title != sheet:
                continue
            out.append((sh.title, [list(r) for r in sh.iter_rows(values_only=True)]))
        wb.close()
    return out

def find_col(hdr, patterns, exclude=None):
    for i, x in enumerate(hdr):
        t = re.sub(r"\s+", "", str(x)) if x not in (None, "") else ""
        if not t:
            continue
        if exclude and any(e in t for e in exclude):
            continue
        if all(p in t for p in patterns):
            return i
    return None

# ---------------- 视频监控 ----------------
def load_video():
    recs, report = [], []
    merged = OrderedDict()   # key -> rec
    for sname in VIDEO_SHEETS:
        _, rows = rows_from(VIDEO_XLSX, sname)[0]
        hi = next(i for i, r in enumerate(rows[:4]) if any(str(x).strip() == "设备名称" for x in r if x))
        hdr = rows[hi]
        c_name = find_col(hdr, ["设备名称"])
        c_office = find_col(hdr, ["所属管理所"])
        c_lon = find_col(hdr, ["经度"])
        c_lat = find_col(hdr, ["纬度"])
        c_pos = find_col(hdr, ["感知位置"])
        c_obj = find_col(hdr, ["感知对象名称"])
        c_type = find_col(hdr, ["设备类型"], exclude=["载体"])          # 模拟/数字
        c_ctrl = find_col(hdr, ["是否可控"])
        c_trans = find_col(hdr, ["信息传输方式"])
        c_code = find_col(hdr, ["设备编码"])
        c_upload = find_col(hdr, ["是否已上传"])
        c_vendor = find_col(hdr, ["设备厂商"], exclude=["载体"])
        c_ptype = find_col(hdr, ["监控点位类型"])
        n_coord = n_nocoord = 0
        for r in rows[hi + 1:]:
            name = clean(r[c_name]) if c_name is not None and c_name < len(r) else ""
            if not name or name == "例":
                continue
            lon, lat = (fnum(r[c_lon]) if c_lon is not None and c_lon < len(r) else None,
                        fnum(r[c_lat]) if c_lat is not None and c_lat < len(r) else None)
            office = clean(r[c_office]) if c_office is not None and c_office < len(r) else ""
            attrs = []
            for lbl, ci in [("设备类型", c_type), ("是否可控", c_ctrl), ("信息传输方式", c_trans),
                            ("设备编码", c_code), ("是否已上传局平台", c_upload), ("设备厂商", c_vendor),
                            ("监控点位类型", c_ptype)]:
                v = clean_attr(r[ci]) if ci is not None and ci < len(r) else ""
                if v:
                    attrs.append([lbl, v])
            station = clean(r[c_pos]) if c_pos is not None and c_pos < len(r) else ""
            rec = {"name": name, "office": office, "btype": "视频监控", "station": station,
                   "chan": "", "lon": lon, "lat": lat, "attrs": attrs, "noCoord": lon is None or lat is None,
                   "subsystem": "视频监控", "_sheet": sname}
            if rec["noCoord"]:
                n_nocoord += 1
                key = ("N", norm_name(name), office)
            else:
                n_coord += 1
                key = ("C", norm_name(name), round(lon, 6), round(lat, 6))
            if key in merged:
                old = merged[key]
                if len(attrs) > len(old["attrs"]):
                    old["attrs"] = attrs
                old.setdefault("_sheets", [old["_sheet"]]).append(sname)
            else:
                merged[key] = rec
        report.append(f"  sheet[{sname}] 有效行: 有坐标={n_coord} 无坐标={n_nocoord} 合并后累计={len(merged)}")
    return list(merged.values()), report

# ---------------- 雨水情 ----------------
def load_rain():
    _, rows = rows_from(RAIN_XLSX, "Sheet1")[0]
    # 二级表头行=1（列21+ 的列名），一级行0 含前 21 列列名
    hdr2 = rows[1]
    hdr0 = rows[0]
    def col(pats, base=None):
        c = find_col(hdr2, pats)
        return c if c is not None else (find_col(hdr0, pats) if base is None else None)
    c_name = find_col(hdr0, ["测点名称"])
    c_obj = find_col(hdr0, ["感知对象名称"])
    c_mid = find_col(hdr0, ["中类"])
    c_sub = find_col(hdr0, ["小类"])
    c_code = find_col(hdr0, ["测站编码"])
    c_trans = find_col(hdr0, ["信息传输方式"])
    c_freq = find_col(hdr0, ["测量频率"])
    c_lon = find_col(hdr2, ["采集点经度"])
    c_lat = find_col(hdr2, ["采集点纬度"])
    c_addr = find_col(hdr2, ["安装地址"])
    c_mgr = find_col(hdr2, ["管理单位"])
    c_time = find_col(hdr2, ["安装时间"])
    recs = []
    for r in rows[2:]:
        name = clean(r[c_name]) if c_name is not None and c_name < len(r) else ""
        if not name:
            continue
        lon = fnum(r[c_lon]) if c_lon is not None and c_lon < len(r) else None
        lat = fnum(r[c_lat]) if c_lat is not None and c_lat < len(r) else None
        attrs = []
        for lbl, ci in [("中类", c_mid), ("小类", c_sub), ("信息传输方式", c_trans),
                        ("测量频率", c_freq), ("设备编码", c_code), ("管理单位", c_mgr), ("安装地址", c_addr)]:
            v = clean_attr(r[ci]) if ci is not None and ci < len(r) else ""
            if v:
                attrs.append([lbl, v])
        recs.append({"name": name, "office": clean(r[c_mgr]) if c_mgr is not None and c_mgr < len(r) else "",
                     "btype": "雨水情监测", "station": clean(r[c_obj]) if c_obj is not None and c_obj < len(r) else "",
                     "chan": clean(r[c_mid]) if c_mid is not None and c_mid < len(r) else "",
                     "lon": lon, "lat": lat, "attrs": attrs,
                     "noCoord": lon is None or lat is None, "subsystem": "雨水情监测",
                     "_install": clean(r[c_time]) if c_time is not None and c_time < len(r) else ""})
    return recs

# ---------------- 大坝 / 地下水（同构 34 列） ----------------
def load_sensor(fn, subsystem):
    _, rows = rows_from(fn)[0]
    hi = next(i for i, r in enumerate(rows[:4]) if any("设备名称" in str(x) for x in r if x))
    hdr = rows[hi]
    hdr0 = rows[0] if hi > 0 else hdr   # 一级表头行（感知设施/中类* 等在行0）

    def col(pats, exclude=None):
        c = find_col(hdr, pats, exclude)
        return c if c is not None else find_col(hdr0, pats, exclude)

    c_name = col(["设备名称"])
    c_code = col(["设备编码"], exclude=["载体", "城市码"])
    c_mid = col(["中类"], exclude=["载体"])     # 防'载体设施中类*'误命中（真实中类在一级表头行）
    c_sub = col(["小类"], exclude=["载体"])
    c_lon = col(["采集点经度"])
    c_lat = col(["采集点纬度"])
    c_addr = col(["安装地址"])
    c_mgr = col(["管理单位"], exclude=["联系人", "电话"])
    c_time = col(["安装时间"])
    recs = []
    for r in rows[hi + 1:]:
        name = clean(r[c_name]) if c_name is not None and c_name < len(r) else ""
        if not name:
            continue
        lon = fnum(r[c_lon]) if c_lon is not None and c_lon < len(r) else None
        lat = fnum(r[c_lat]) if c_lat is not None and c_lat < len(r) else None
        attrs = []
        for lbl, ci in [("中类", c_mid), ("小类", c_sub), ("设备编码", c_code), ("安装地址", c_addr), ("管理单位", c_mgr)]:
            v = clean_attr(r[ci]) if ci is not None and ci < len(r) else ""
            if v:
                attrs.append([lbl, v])
        recs.append({"name": name, "office": clean(r[c_mgr]) if c_mgr is not None and c_mgr < len(r) else "",
                     "btype": subsystem, "station": "", "chan": clean(r[c_mid]) if c_mid is not None and c_mid < len(r) else "",
                     "lon": lon, "lat": lat, "attrs": attrs,
                     "noCoord": lon is None or lat is None, "subsystem": subsystem,
                     "_install": clean(r[c_time]) if c_time is not None and c_time < len(r) else ""})
    return recs

# ---------------- 渠道太阳能（无坐标） ----------------
def load_solar(video_names):
    _, rows = rows_from(SOLAR_XLSX, "Sheet2")[0]
    hi = next(i for i, r in enumerate(rows[:4]) if any(str(x).strip() == "站点名称" for x in r if x))
    hdr = rows[hi]
    c_name = find_col(hdr, ["站点名称"])
    c_ip = find_col(hdr, ["IP地址"])
    c_addr = find_col(hdr, ["安装地址"])
    c_pwr = find_col(hdr, ["供电类型"])
    c_stat = find_col(hdr, ["运行状态"])
    c_adv = find_col(hdr, ["运维建议"])
    c_note = find_col(hdr, ["备注"])
    recs, merged_n, new_n = [], 0, 0
    for r in rows[hi + 1:]:
        name = clean(r[c_name]) if c_name is not None and c_name < len(r) else ""
        if not name:
            continue
        attrs = []
        for lbl, ci in [("供电类型", c_pwr), ("IP地址", c_ip), ("运行状态", c_stat), ("运维建议", c_adv), ("备注", c_note)]:
            v = clean(r[ci]) if ci is not None and ci < len(r) else ""
            if v:
                attrs.append([lbl, v])
        target = None
        for vr in video_names:
            if norm_name(vr["name"]) == norm_name(name):
                target = vr
                break
        if target is not None:   # 与视频台账重合 → 并入已有条目
            have = {k: v for k, v in target["attrs"]}
            for k, v in attrs:
                if k not in have:
                    target["attrs"].append([k, v])
            merged_n += 1
        else:
            recs.append({"name": name, "office": "", "btype": "视频监控", "station": clean(r[c_addr]) if c_addr is not None and c_addr < len(r) else "",
                         "chan": "", "lon": 116.637, "lat": 40.376, "attrs": attrs, "noCoord": True,
                         "subsystem": "视频监控", "_sheet": "渠道太阳能", "_install": ""})
            new_n += 1
    return recs, merged_n, new_n

# ---------------- 生成 ----------------
def main():
    print("== 读取台账 ==")
    video, rep = load_video()
    for line in rep:
        print(line)
    rain = load_rain()
    dam = load_sensor(DAM_XLSX, "大坝安全监测")
    ground = load_sensor(GROUND_XLS, "地下水源监测")
    print(f"雨水情原始={len(rain)} 大坝={len(dam)} 地下水={len(ground)}")
    # 台账内去重：视频=(归一名,坐标)；传感器类(大坝/地下水)同井多设备共用坐标，键必须含编码/小类防误并
    def dedup(recs, tag, sensor=False):
        m = OrderedDict()
        for d in recs:
            geo = (round(d["lon"], 6), round(d["lat"], 6)) if not d["noCoord"] else ("N",)
            code = dict((k, v) for k, v in d["attrs"]).get("设备编码", "")
            key = (norm_name(d["name"]), code if sensor else "", geo)
            if key in m:
                if len(d["attrs"]) > len(m[key]["attrs"]):
                    m[key]["attrs"] = d["attrs"]
            else:
                m[key] = d
        print(f"  {tag}: {len(recs)} -> 去重后 {len(m)}")
        return list(m.values())
    rain = dedup(rain, "雨水情")
    dam = dedup(dam, "大坝", sensor=True)
    ground = dedup(ground, "地下水", sensor=True)
    solar, merged_n, new_n = load_solar(video)
    print(f"渠道太阳能: 与视频并入={merged_n} 新增={new_n}")
    allrecs = video + solar + rain + dam + ground
    # 重编 id（视频在前与现库分段习惯一致）
    for i, d in enumerate(allrecs, 1):
        d["id"] = f"p{i}"
    cnt = Counter(d["subsystem"] for d in allrecs)
    offices = sorted({d["office"] for d in allrecs if d["office"]})
    print(f"\n== 总计 {len(allrecs)} 条 == " + json.dumps(dict(cnt), ensure_ascii=False))
    print("offices(%d): %s" % (len(offices), "、".join(offices)))
    lonv = [d["lon"] for d in allrecs if d["lon"] and not d["noCoord"]]
    latv = [d["lat"] for d in allrecs if d["lat"] and not d["noCoord"]]
    print(f"有坐标 {len(lonv)} 条  经度域 {min(lonv):.3f}~{max(lonv):.3f}  纬度域 {min(latv):.3f}~{max(latv):.3f}")
    print(f"无坐标 {sum(1 for d in allrecs if d['noCoord'])} 条")
    print("样例:", json.dumps(allrecs[0], ensure_ascii=False)[:300])
    print("样例:", json.dumps([d for d in allrecs if d["subsystem"] == "雨水情监测"][0], ensure_ascii=False)[:300])
    print("样例:", json.dumps([d for d in allrecs if d["subsystem"] == "地下水源监测"][0], ensure_ascii=False)[:300])
    print("样例:", json.dumps([d for d in allrecs if d["subsystem"] == "大坝安全监测"][0], ensure_ascii=False)[:300])
    if DRY:
        print("\n[dry-run] 未写 webroot")
        return

    # 现库 META.types 结构保留
    old = io.open(os.path.join(WEB, "data.js"), encoding="utf-8-sig").read()
    m = re.search(r"window\.PERCEPTION_META\s*=\s*(\{.*?\});", old, re.S)
    old_meta = json.loads(m.group(1))
    meta = OrderedDict()
    meta["title"] = old_meta.get("title", "水利感知项目一张图")
    meta["author"] = old_meta.get("author", "科技推广中心")
    meta["offices"] = offices
    meta["types"] = old_meta.get("types", list(cnt.keys()))
    meta["counts"] = dict(cnt)
    today = "2026-10-24"
    def fmt_ts(s):
        if not s:
            return ""
        t = clean(s).replace("-", "/").replace(".", "/")
        m2 = re.match(r"^(\d{4})/(\d{1,2})/(\d{1,2})", t)
        return f"{m2.group(1)}/{int(m2.group(2))}/{int(m2.group(3))} 00:00:00" if m2 else ""

    def dump(rec, kb=False):
        if kb:
            return OrderedDict([("id", rec["id"]), ("name", rec["name"]), ("office", rec["office"]),
                                ("station", rec["station"]), ("btype", rec["btype"]), ("chan", rec["chan"]),
                                ("ts", fmt_ts(rec.get("_install", ""))), ("lon", rec["lon"]), ("lat", rec["lat"]),
                                ("subsystem", rec["subsystem"]), ("photos", rec.get("photos", [])),
                                ("attrs", rec["attrs"])])
        return OrderedDict([("id", rec["id"]), ("name", rec["name"]), ("office", rec["office"]),
                            ("btype", rec["btype"]), ("station", rec["station"]), ("chan", rec["chan"]),
                            ("geom", "Point"), ("lat", rec["lat"]), ("lon", rec["lon"]),
                            ("attrs", rec["attrs"]), ("photos", rec.get("photos", [])),
                            ("noCoord", rec["noCoord"]), ("subsystem", rec["subsystem"])])

    src = f"F:\\ganzhi\\dev 台账（自动生成：build/gen_perception_data.py，勿手改）"
    data_js = ("// 自动生成（gen_perception_data.py），请勿手改。\n"
               f"// 感知设备主数据：共 {len(allrecs)} 条（来源：{src}）；buildDate {today}。\n"
               "window.PERCEPTION_META = " + json.dumps(meta, ensure_ascii=False, separators=(", ", ": ")) + ";\n"
               "window.PERCEPTION_DATA = " + json.dumps([dump(d) for d in allrecs], ensure_ascii=False) + ";\n")
    kb_js = ("// 自动生成（gen_perception_data.py），请勿手改。\n"
             f"// 知识库建筑种子：共 {len(allrecs)} 条，与 data.js 同源（id 对齐）；buildDate {today}。\n"
             "window.KB_BUILDING_SEED = " + json.dumps([dump(d, kb=True) for d in allrecs], ensure_ascii=False) + ";\n")
    io.open(os.path.join(WEB, "data.js"), "w", encoding="utf-8").write(data_js)
    io.open(os.path.join(WEB, "kb_building_seed.js"), "w", encoding="utf-8").write(kb_js)
    print(f"\n已写入: webroot/data.js ({len(data_js):,} B)  webroot/kb_building_seed.js ({len(kb_js):,} B)")

if __name__ == "__main__":
    main()
