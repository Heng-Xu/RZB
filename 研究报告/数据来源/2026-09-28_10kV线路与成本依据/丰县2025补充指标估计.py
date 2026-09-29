"""补充丰县 2025 年描述性指标；仅原表装机和负载率为观测值。"""

import csv
from datetime import datetime
from pathlib import Path
from statistics import mean, median

from openpyxl import load_workbook


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "实验/研究/data/tuomin/电网建模数据_Agent整合版_V1.2"
OUTPUT = HERE / "丰县2025补充指标估计.csv"
REGION = "QX-00001"


def run():
    pv = load_workbook(DATA / "逐月分县分布式光伏.xlsx", read_only=True,
                       data_only=True).active
    rows = [(i, row) for i, row in enumerate(pv.iter_rows(values_only=True), 1)
            if row[0] == REGION]
    assert len(rows) >= 3 and rows[1][0] == 21 and rows[2][0] == 34
    prev = [float(v) * 10 for v in rows[1][1][1:13]]
    current = [float(v) * 10 for v in rows[2][1][1:13]]
    curve = load_workbook(DATA / "光伏8760小时数据.xlsx", read_only=True,
                          data_only=True).active
    factors = [(row[1], float(row[4])) for row in curve.iter_rows(min_row=2, values_only=True)
               if isinstance(row[1], datetime) and row[1].year == 2025]
    pv_energy = sum(factor * (current[hour.month - 1] +
                    (prev[-1] if hour.month == 1 else current[hour.month - 2])) / 2
                    for hour, factor in factors)
    network = load_workbook(DATA / "近5年容载比.xlsx", read_only=True,
                            data_only=True).active
    assert network["A34"].value == REGION
    transformer = float(network["O34"].value) * 10
    downward_load = float(network["P34"].value) * 10
    assets = load_workbook(DATA / "2025设备负载统计表.xlsx", read_only=True,
                           data_only=True)["主变1"]
    rates = [float(row[15]) for row in assets.iter_rows(min_row=3, values_only=True)
             if row[1] == 110 and row[2] == REGION and isinstance(row[15], (int, float))]
    load_factor = mean((4216392.395 / (956.45 * 8760),
                        6791485.096 / (1545.194683 * 8760)))
    user_energy = downward_load * 8760 * load_factor
    result = {
        "区县": "丰县", "年份": 2025,
        "年末分布式光伏装机MW_原表": current[-1],
        "分布式光伏原表格": "逐月分县分布式光伏.xlsx!M34×10；前月参考M21×10",
        "110kV降压负荷MW_原表": downward_load,
        "110kV公用主变容量MVA_原表": transformer,
        "负荷与容量原表格": "近5年容载比.xlsx!P34×10,O34×10",
        "原表口径容量负荷比": transformer / downward_load,
        "最大用户负荷MW_夜间场景估计": downward_load,
        "源荷比_估计": current[-1] / downward_load,
        "分布式光伏年发电量MWh_月装机曲线估计": pv_energy,
        "用户年用电量MWh_借用负荷率估计": user_energy,
        "用户年负荷率_借用市区邳州估计": load_factor,
        "电量渗透率_估计": pv_energy / user_energy,
        "110kV主变负载率原表样本台数": len(rates),
        "110kV主变负载率原表均值百分数": mean(rates),
        "110kV主变负载率原表中位数百分数": median(rates),
        "负载率原表格": "2025设备负载统计表.xlsx!主变1，按B列110kV、C列QX-00001筛选P列",
        "证据限制": "丰县用户电量采用市区与邳州估计负荷率的平均值推算；电量渗透率不是实测统计；主变负载率为逐台原表指标，非区县同期负载率",
    }
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result), lineterminator="\n")
        writer.writeheader()
        writer.writerow(result)
    return result


if __name__ == "__main__":
    print(run())
