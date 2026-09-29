"""生成并校验本轮核心来源快照的路径、哈希和适用范围。"""

import csv
import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCES = [
    ("GUIDE_DLT5729_2023", "项目收资与已存档依据/DLT5729-2023_配电网规划设计技术导则.pdf",
     "参考政策/DL-T+5729-2023+配电网规划设计技术导则.pdf",
     "2.0.4网供负荷；2.0.9、6.3.2～6.3.5容载比；2.0.15、7.1.2转供能力与分区比例；PDF第12、13、17、24、28页",
     "2023正式版；图片扫描件，关键页人工核对；市区50%是导则范围内规划假定，非实际转供率"),
    ("LINE_HUARONG_2020", "华容县配电网规划报告_2020.html",
     "https://www.huarong.gov.cn/33157/64140/64170/content_1874487.html",
     "表7-1：JKLYJ-240 24万元/km；YJV22-400电气部分120万元/km；智能柱上开关3万元/台",
     "公开规划价；湖南2020；未含土建及征地；用于低价情景，不是徐州报价"),
    ("LINE_XUZHOU_TENDER_2025", "徐州10kV线路迁改招标公告_2025.html",
     "https://ggzy.zwb.xz.gov.cn/jyxx/003009/003009001/20250903/8c7d2dd2-dcab-4abf-827f-d0f5774799d3.html",
     "招标内容及项目概况：约116.17万元",
     "徐州本地整体工程；无线路里程，不能拆成每公里造价"),
    ("LINE_YANGCHENG_APPROVAL_2024", "阳城10kV联络工程核准_2024.pdf",
     "https://xxgk.yczf.gov.cn/xzf/yczsj/fdzdgknr/spjzdxmjsly/pzjgxx/202409/P020240918601093783700.pdf",
     "核准规模及投资：新建2.71km、改造2.58km、三台断路器、总投资170万元",
     "山西混合工程；扫描PDF；只作数量级交叉核对，不能当纯新线单价"),
    ("GUIDE_DRAFT_2025", "项目收资与已存档依据/配电网规划设计技术导则_2025修订稿.pdf",
     "参考文献/前沿调研/pdfs/D8_政策标准/《配电网规划设计技术导则（修订稿）》.pdf",
     "6.2.2容载比；7.1.2供需预测期限；9.2.1.2站间经中压网转供能力及原则上不设站间中压专用联络线",
     "现行正式依据改为 DL/T 5729—2023；修订稿仅供 2023 版未定义的研究指标参照"),
    ("XUZHOU_TX_PROJECT", "项目收资与已存档依据/徐州110kV工程投资汇总.xlsx",
     "实验/研究/data/tuomin/电网建模数据_Agent整合版_V1.2/江苏徐州邢楼110千伏变电站主变扩建等工程建设规模及投资汇总表(1).xlsx",
     "Sheet1第21行：王庄主变替换50/20MVA、静态总投资1151万元、另增9回10kV出线",
     "主变增容项目案例，含配套出线；不是纯主变单价"),
    ("XUZHOU_CLR_2021_2025", "项目收资与已存档依据/近5年容载比.xlsx",
     "实验/研究/data/tuomin/电网建模数据_Agent整合版_V1.2/近5年容载比.xlsx",
     "Sheet1区县年度行；邳州2021见第19行，市区2021见第9行",
     "年度容量和负荷原始收资；与2021仿真重设初始容量分开"),
    ("XUZHOU_PV_MONTHLY", "项目收资与已存档依据/逐月分县分布式光伏.xlsx",
     "实验/研究/data/tuomin/电网建模数据_Agent整合版_V1.2/逐月分县分布式光伏.xlsx",
     "2023—2025年12月并网装机；2021—2022无原表记录",
     "2021—2022没有原始光伏观测，不得把回推写作实测"),
    ("PIZHOU_10KV_ARCHIVE", "项目收资与已存档依据/邳州10kV馈线原始包.7z",
     "实验/研究/data/tuomin/10kv_case/source/10kv.7z",
     "墩振线PDF及明细；23—24杆区段经拓扑和节点负荷种子重建为7.491MW",
     "7.491MW是2025压力场景转移上界，非实际投运转供记录"),
    ("PIZHOU_10KV_TIE_TABLE", "项目收资与已存档依据/邳州10kV联络结构化原表_V2.xlsx",
     "实验/研究/data/tuomin/10kv_case/source/10kV案例建模前期准备_V2_新结构化表格与图纸.xlsx",
     "02_联络关系第2—4行：T01、T02、T03两侧馈线和开关位置",
     "部分联络拓扑存在待修复开关链；六馈线组合能力是筛查上界"),
    ("STORAGE_SZ_TENDER", "项目收资与已存档依据/苏州100kW_215kWh储能柜招标公告.pdf",
     "参考政策/储能成本依据/案例1_苏州100kW_215kWh储能户外柜招标公告.pdf",
     "储能子项最高限价27.2万元/100kW/215kWh",
     "招标上限而非中标成交价；只作小规模成本锚点"),
    ("STORAGE_LY_AWARD", "项目收资与已存档依据/浏阳1MW_2.2MWh储能中标公告.pdf",
     "参考政策/储能成本依据/案例2_浏阳1MW_2.2MWh用户侧储能中标公告.pdf",
     "中标价2104562.62元；设备至少1MW/2.15MWh",
     "湖南用户侧项目价；含设备安装等；按10柜包重复采购是模型假设"),
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    rows = []
    for source_id, relative, origin, locator, limitation in SOURCES:
        archive = HERE / relative
        if not archive.is_file():
            raise FileNotFoundError(archive)
        sha = digest(archive)
        if not origin.startswith("http"):
            original = ROOT / origin
            if not original.is_file() or digest(original) != sha:
                raise ValueError(f"本地原始文件与归档副本不一致：{source_id}")
        rows.append({"source_id": source_id,
                     "retrieved_or_copied_date": "2026-09-29" if source_id == "GUIDE_DLT5729_2023" else "2026-09-28",
                     "archive_path": relative, "origin": origin,
                     "original_locator_and_value": locator,
                     "use_and_limitation": limitation,
                     "sha256": sha})
    with (HERE / "source_manifest.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (HERE / "SHA256SUMS").write_text("".join(
        f"{r['sha256']}  {r['archive_path']}\n" for r in rows), encoding="utf-8")
    print(f"已核对并登记 {len(rows)} 份原始来源")


if __name__ == "__main__":
    main()
