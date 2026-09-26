"""把求解结果封装为可离线核阅的技术报告；HTML 由统一交付器生成。"""

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .baseline_2021 import read_csv
from .hourly_source_profile import OUTPUT_DIR


def reviewed_sql_snapshot(rows: list[dict], table: str, order_field: str) -> tuple[list[dict], str]:
    """先把已复核的 CSV 合成行装载入 SQLite，再执行实际的展示查询。"""
    columns = list(rows[0])
    connection = sqlite3.connect(":memory:")
    declared = ", ".join(f'"{column}" {"REAL" if isinstance(rows[0][column], (float, int)) else "TEXT"}'
                          for column in columns)
    connection.execute(f'CREATE TABLE "{table}" ({declared})')
    placeholders = ", ".join("?" for _ in columns)
    connection.executemany(f'INSERT INTO "{table}" VALUES ({placeholders})',
                           (tuple(row[column] for column in columns) for row in rows))
    sql = f'SELECT {", ".join(chr(34) + column + chr(34) for column in columns)} FROM "{table}" ORDER BY "{order_field}"'
    selected = [dict(zip(columns, record)) for record in connection.execute(sql)]
    connection.close()
    return selected, sql


def build_artifact(source: Path = OUTPUT_DIR) -> dict:
    scan = read_csv(source / "joint_lifecycle_elastic_cap_scan.csv")
    matrices = {v: read_csv(source / f"joint_lifecycle_conditional_matrix_{v}kv.csv") for v in (35, 110)}
    rigid = read_csv(source / "joint_lifecycle_rigid_layers.csv")
    sensitivity = read_csv(source / "joint_lifecycle_sensitivity.csv")
    cost_by_layer = {(r["study_region_id"], int(r["voltage_kv"])): float(r["objective_npv_10k_cny"])
                     for r in rigid}
    best_by_layer = {}
    for row in scan:
        key = row["study_region_id"], int(row["voltage_kv"])
        if key not in best_by_layer or float(row["objective_npv_10k_cny"]) < float(best_by_layer[key]["objective_npv_10k_cny"]) - 1e-5:
            best_by_layer[key] = row
    group_names = {("QX-00005", 35): "邳州 35 kV", ("QX-00005", 110): "邳州 110 kV",
                   ("QX-00007", 110): "市区 110 kV"}
    group_rows = []
    for key in (("QX-00005", 35), ("QX-00005", 110), ("QX-00007", 110)):
        matched = next(r for r in matrices[key[1]] if (r["study_region_id"], int(r["voltage_kv"]), int(r["year"])) == (*key, 2025))
        group_rows.append({"group": group_names[key], "rigid_cost": round(cost_by_layer[key], 2),
                           "elastic_cost": round(float(best_by_layer[key]["objective_npv_10k_cny"]), 2),
                           "least_cost_cap": float(best_by_layer[key]["clr_cap"]),
                           "rigid_r_2025": float(matched["rigid_actual_clr"]),
                           "elastic_r_2025": float(matched["elastic_actual_clr"]),
                           "storage_2025": int(next(r["storage_modules_in_service"] for r in read_csv(source / "joint_lifecycle_conditional_recommendations.csv")
                                                    if (r["study_region_id"], int(r["voltage_kv"]), int(r["year"])) == (*key, 2025)))})
    scan_sql = ("SELECT CAST(clr_cap AS TEXT) AS cap_label, clr_cap AS cap, "
                "ROUND(objective_npv_10k_cny, 2) AS npv, max_actual_clr AS actual_max_r "
                "FROM joint_lifecycle_elastic_cap_scan "
                "WHERE study_region_id = 'QX-00005' AND voltage_kv = 35 ORDER BY clr_cap")
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE joint_lifecycle_elastic_cap_scan "
                       "(study_region_id TEXT, voltage_kv INTEGER, clr_cap REAL, "
                       "objective_npv_10k_cny REAL, max_actual_clr REAL)")
    connection.executemany("INSERT INTO joint_lifecycle_elastic_cap_scan VALUES (?, ?, ?, ?, ?)",
                           ((r["study_region_id"], int(r["voltage_kv"]), float(r["clr_cap"]),
                             float(r["objective_npv_10k_cny"]), float(r["max_actual_clr"])) for r in scan))
    columns = ("cap_label", "cap", "npv", "actual_max_r")
    cap_rows = [dict(zip(columns, row)) for row in connection.execute(scan_sql)]
    connection.close()
    year_rows = [{"year": int(r["year"]), "rigid_r": round(float(r["rigid_actual_clr"]), 3),
                  "elastic_r": round(float(r["elastic_actual_clr"]), 3),
                  "growth_pct": round(100 * float(r["annual_net_peak_growth_vs_previous"]), 1),
                  "h95_forward": int(r["forward_h95_hours_2025_template"]),
                  "h95_reverse": int(r["reverse_h95_hours_2025_template"])}
                 for r in matrices[35]]
    cases = {}
    for r in sensitivity:
        if (r["study_region_id"], int(r["voltage_kv"])) == ("QX-00005", 35):
            cases.setdefault(r["case"], {})[r["scheme"]] = float(r["objective_npv_10k_cny"])
    sensitivity_rows = [{"case": case, "rigid": round(values["rigid"], 1),
                         "elastic": round(values["elastic"], 1),
                         "saving": round(values["rigid"] - values["elastic"], 1)}
                        for case, values in cases.items()]
    year_rows, year_sql = reviewed_sql_snapshot(year_rows, "year35_snapshot", "year")
    group_rows, group_sql = reviewed_sql_snapshot(group_rows, "group_comparison_snapshot", "group")
    sensitivity_rows, sensitivity_sql = reviewed_sql_snapshot(sensitivity_rows, "sensitivity35_snapshot", "case")
    now = datetime.now(timezone.utc).isoformat()
    title = "徐州容载比模型重构：分电压仿真结果"
    sources = [
        {"id": "cost_scan", "label": "邳州 35 kV 弹性上限扫描", "path": "rebuild_2026/source_audit/joint_lifecycle_elastic_cap_scan.csv",
         "query": {"engine": "SQLite over reviewed model CSV", "sql": scan_sql,
                   "description": "离散主变、储能和年度容载比上限的全寿命成本最小化；邳州 35 kV 九个扫描档",
                   "tables_used": ["joint_lifecycle_elastic_cap_scan.csv"],
                   "metric_definitions": ["成本为 2022—2041 年增量投资、运维及更新折至 2021 年末，单位万元；扫描上限不等于实际容载比。"]}},
        {"id": "matrix35", "label": "邳州 35 kV 条件推荐", "path": "rebuild_2026/source_audit/joint_lifecycle_conditional_matrix_35kv.csv",
         "query": {"engine": "SQLite over reviewed model CSV", "sql": year_sql,
                   "description": "邳州 35 kV 逐年刚性与最低成本弹性设备路径",
                   "tables_used": ["joint_lifecycle_conditional_matrix_35kv.csv"],
                   "metric_definitions": ["实际容载比=同方案年度在役主变 MVA/同步正向最大有功净负荷 MW。"]}},
        {"id": "matrix110", "label": "邳州和市区 110 kV 条件推荐", "path": "rebuild_2026/source_audit/joint_lifecycle_conditional_matrix_110kv.csv",
         "query": {"engine": "Python", "description": "110 kV 两片区逐年刚性与弹性路径",
                   "tables_used": ["joint_lifecycle_conditional_matrix_110kv.csv"]}},
        {"id": "rigid", "label": "刚性方案年度与分组结果", "path": "rebuild_2026/source_audit/joint_lifecycle_rigid_layers.csv",
         "query": {"engine": "SQLite over reviewed model CSV", "sql": group_sql,
                   "description": "刚性上限 2.0；邳州 110 kV 纳入局部联络；组别汇总由刚性、弹性及逐年矩阵合成",
                   "tables_used": ["joint_lifecycle_rigid_layers.csv", "joint_lifecycle_rigid_years.csv"]}},
        {"id": "sensitivity", "label": "全寿命参数敏感性", "path": "rebuild_2026/source_audit/joint_lifecycle_sensitivity.csv",
         "query": {"engine": "SQLite over reviewed model CSV", "sql": sensitivity_sql,
                   "description": "折现率、运维率、储能寿命和早期光伏情景变动后的重求解",
                   "tables_used": ["joint_lifecycle_sensitivity.csv"]}},
    ]
    blocks = [
        {"id": "title", "type": "markdown", "body": f"# {title}"},
        {"id": "summary", "type": "markdown", "body": "## 技术摘要\n\n2021 年共同仿真起点已按接近且不超过容载比 2.0 重新选择，并核查后续不拆减主变的刚性路径。基准价格下，邳州 35/110 kV 和市区 110 kV 的最低全寿命成本均在扫描上限 2.0 时取得，分别为 2390.21、3555.79、2664.61 万元；继续放宽上限没有降低成本。邳州 110 kV 新起点下未选用既有联络或新线。当前条件表只有三个独立单元，尚不能发布相对通用的推荐区间。", "layout": "full"},
        {"id": "definitions", "type": "markdown", "body": "## 三个独立组别与指标口径\n\n样本为邳州 20 座 110 kV、8 座 35 kV 站和市区 29 座 110 kV 站；两电压不合并。2021 年容量是仿真起点；2022—2025 年逐年选择设备，2022—2041 年计算现金流。实际容载比以同片区、同电压、同方案的同步正向最大有功净负荷为分母；2022—2024 年静态场景为年度代理，2025 年场景取逐时样本。", "layout": "full"},
        {"id": "finding35", "type": "markdown", "body": "## 邳州 35 kV：基准价格下 2.0 起为成本平台\n\n图中横轴是研究性容载比上限、纵轴为全寿命增量成本现值。加密到 0.01 档后，2.0—2.4 仍无成本台阶；因此扫描上限不是可直接发布的实际推荐 R。价格扰动仅作为条件情景，不能冒充新的实测样本。", "layout": "full"},
        {"id": "cap_chart_block", "type": "chart", "chartId": "cap_chart", "layout": "full"},
        {"id": "year_note", "type": "markdown", "body": "2023 年官方正向净负荷峰值 86.70 MW 较低，最优路径该年的实际 R 为 1.984；2025 年为 1.592。表中 H95 是 2025 年时序模板，不伪称历史年度实测时长。", "layout": "full"},
        {"id": "year_table_block", "type": "table", "tableId": "year_table", "layout": "full"},
        {"id": "finding110", "type": "markdown", "body": "## 110 kV：放宽上限没有降低成本\n\n邳州 110 kV 刚性方案允许两站六馈线联络，弹性方案不含联络；新起点下刚性没有实际选择联络，两个方案成本与设备路径相同。市区 110 kV 两方案也一致。联络源端余量尚不能证明下游转供能力。", "layout": "full"},
        {"id": "group_table_block", "type": "table", "tableId": "group_table", "layout": "full"},
        {"id": "method", "type": "markdown", "body": "## 成本寻优与静态约束\n\n优化器同时比较离散双主变升级、0.1 MW/0.215 MWh 整柜储能和邳州刚性方案内的双向既有/新建联络，单目标为增量全寿命成本现值最小。基准折现率 6%；主变与新线计算寿命 20 年、固定运维 1%/年；储能计算寿命 10 年、固定运维 3%/年。主变折算价 110/35 kV 分别为 16.5733/15.48 万元/新购 MVA。年度站级正向供电、反向风险、储能功率与 D95、六馈线源端余量及片区 R 上限均为硬约束。模型按原定义保留 DL/T 2041—2025 第 6.3 节设备级公式；当前结果是站级静态规划仿真，不把聚合风险上界称作设备级承载力核定。", "layout": "full"},
        {"id": "robustness", "type": "markdown", "body": "## 成本与起点敏感性\n\n折现率 4%—8%、电网设备运维 0%—2%、储能寿命 8—12 年和早期高光伏代理下，基准价格的三组路径均未因放宽上限而降费。邳州 35 kV 若主变单价减半或储能单价翻倍，才在研究性价格情景中出现小幅弹性收益。旧最小容量起点下的较大收益在新起点下消失，说明起点校准是决定性假设。690 条措施现金流已与优化目标复算一致。", "layout": "full"},
        {"id": "sensitivity_table_block", "type": "table", "tableId": "sensitivity_table", "layout": "full"},
        {"id": "next", "type": "markdown", "body": "## 使用建议与后续\n\n当前两张表仅为三单元的逐年条件案例，尚未达到相对通用推荐矩阵的证据要求。须在同一新起点上补足有来源的源荷、净负荷和措施价格情景，逐案复算设备路径与成本前沿，再由负责人审定区间。系统级年度时序生产模拟、逐台导则评估、潮流和可实施转供尚未完成；最终研究报告暂不改写。", "layout": "full"},
    ]
    return {
        "surface": "report",
        "manifest": {"version": 1, "surface": "report", "title": title, "generatedAt": now,
                     "blocks": blocks, "sources": sources,
                     "charts": [{"id": "cap_chart", "title": "邳州 35 kV 弹性上限与全寿命成本",
                                 "subtitle": "2022—2041 年新增措施现值，万元；9 个研究性扫描档",
                                 "type": "bar", "dataset": "cap_scan", "sourceId": "cost_scan",
                                 "encodings": {"x": {"field": "cap_label", "type": "ordinal", "label": "扫描上限"},
                                               "y": {"field": "npv", "type": "quantitative", "label": "全寿命成本现值", "unit": "万元"}},
                                 "layout": "full"}],
                     "tables": [
                         {"id": "year_table", "title": "邳州 35 kV 逐年实际容载比", "dataset": "year35",
                          "subtitle": "2022—2025 年；H95 栏为 2025 年模板", "sourceId": "matrix35",
                          "defaultSort": {"field": "year", "direction": "asc"}, "density": "spacious", "layout": "full",
                          "columns": [{"field": "year", "label": "年份"}, {"field": "rigid_r", "label": "刚性实际 R"},
                                      {"field": "elastic_r", "label": "弹性实际 R"},
                                      {"field": "growth_pct", "label": "峰值同比(%)"},
                                      {"field": "h95_forward", "label": "正向 H95 模板(h)"},
                                      {"field": "h95_reverse", "label": "反向 H95 模板(h)"}]},
                         {"id": "group_table", "title": "分电压方案成本与 2025 年实际指标", "dataset": "groups",
                          "subtitle": "成本为 2022—2041 年增量现值，万元；邳州 110 kV 两方案措施边界不同", "sourceId": "rigid",
                          "defaultSort": {"field": "group", "direction": "asc"}, "density": "spacious", "layout": "full",
                          "columns": [{"field": "group", "label": "研究组别"},
                                      {"field": "rigid_cost", "label": "刚性成本(万元)"},
                                      {"field": "elastic_cost", "label": "弹性最低成本(万元)"},
                                      {"field": "least_cost_cap", "label": "最低成本首档"},
                                      {"field": "rigid_r_2025", "label": "刚性 2025 R"},
                                      {"field": "elastic_r_2025", "label": "弹性 2025 R"},
                                      {"field": "storage_2025", "label": "2025 储能柜数"}]},
                         {"id": "sensitivity_table", "title": "邳州 35 kV 参数敏感性", "dataset": "sensitivity35",
                          "subtitle": "固定弹性扫描档 2.4；成本现值单位万元", "sourceId": "sensitivity",
                          "defaultSort": {"field": "case", "direction": "asc"}, "density": "dense", "layout": "full",
                          "columns": [{"field": "case", "label": "情景"},
                                      {"field": "rigid", "label": "刚性成本"},
                                      {"field": "elastic", "label": "弹性成本"},
                                      {"field": "saving", "label": "节省额"}]},
                     ]},
        "snapshot": {"version": 1, "generatedAt": now, "status": "model_review_matrix_not_released",
                     "datasets": {"cap_scan": cap_rows, "year35": year_rows,
                                  "groups": group_rows, "sensitivity35": sensitivity_rows}},
        "sources": sources,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="生成技术结果报告的规范化输入")
    parser.add_argument("--source-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR / "model_result_artifact.json")
    args = parser.parse_args()
    args.output.write_text(json.dumps(build_artifact(args.source_dir), ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
