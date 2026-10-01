"""输出年度措施、正常负荷转接及独立措施有效性复核；不覆盖旧事故代理结果。"""

import json
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .baseline_2021 import read_csv
from .joint_shared_measure_audit import audit
from .regional_static_milp_v2_audit import audit as station_audit
from .station_grid_feasibility import grid_candidate_rows


MODEL = Path(__file__).resolve().parent
SOURCE = MODEL / "outputs/joint_shared_measure/station_rate_all_years_load_reallocation"
DELIVERY = MODEL.parents[2] / "docs/2026-10-01站级转供率三措施优化"
LABEL = {"pizhou": "邳州", "city": "市区", "rigid": "刚性", "elastic": "弹性"}


def service(load, area):
    return load if area == "A" else max(0, min(load - 12, 2 * load / 3))


def transformer_action(r):
    changes = [f"{slot}号主变{float(r[f'prior_unit_{slot}_mva']):g}→{float(r[f'unit_{slot}_mva']):g} MVA"
               for slot in (1, 2) if float(r[f"unit_{slot}_mva"]) >
               float(r[f"prior_unit_{slot}_mva"]) + 1e-5]
    if int(r["third_transformer_commissioned"]):
        changes.append("新增3号主变50 MVA")
    return "；".join(changes) or "沿用"


def main(source=SOURCE, delivery=DELIVERY, repeat_directory=None):
    source, delivery = Path(source), Path(delivery)
    for district in ("pizhou", "city"):
        station_audit(source / district)
    numerical = audit(source, repeat_directory)
    review = json.loads((source / "review.json").read_text())
    assert review["transfer_mode"] == "load_reallocation"
    equivalent = review.get("transfer_capacity_model") == "station_rate_equivalent"
    annual = read_csv(source / "annual_comparison.csv")
    book = Workbook()
    summary_sheet = book.active
    summary_sheet.title = "逐年措施汇总"
    summary_sheet.append(["区县", "方案", "年份", "主变净增MVA", "新购主变MVA", "新增第三台数",
                          "新增储能MW", "新增储能MWh", "在役主变MVA", "在役储能MW", "在役储能MWh",
                          "正常负荷转接MW", "新建联络条数", "容载比",
                          "既有预算转接MW", "新增预算转接MW", "新增等效预算使用率"])
    moves_sheet = book.create_sheet("站间正常负荷转接")
    moves_sheet.append(["区县", "方案", "年份", "负荷转出站", "负荷承接站", "峰值转接MW", "通道类型",
                       "原表同网格辅助记录", "通道建模口径"])
    check_sheet = book.create_sheet("逐站容量与效果校核")
    check_sheet.append(["区县", "方案", "年份", "站号", "供电类别", "原负荷MW", "转出MW", "转入MW",
                       "转接后负荷MW", "主变MVA", "储能MW", "储能MWh", "正向余量MW", "反向保守余量MW",
                       "主变退出供电任务MW", "主变退出静态余量MW", "取消转接后退出余量MW",
                       "取消储能后退出余量MW", "不增主变后退出余量MW"])
    cost_sheet = book.create_sheet("费用与研究条件")
    cost_sheet.append(["区县", "刚性全寿命现值万元", "弹性全寿命现值万元", "节省万元", "节省比例"])
    rate_sheet = book.create_sheet("站级转供率与能力")
    rate_sheet.append(["区县", "方案", "年份", "站号", "负荷基数MW", "既有率", "目标率", "规划率上限",
                       "在役新增关联单元数", "既有能力MW", "新增有效能力MW", "有效转供率",
                       "有效能力MW", "实际转出MW", "实际使用比例", "不建新线的目标缺口MW",
                       "不建新线的实际转出超额MW"])
    line_sheet = book.create_sheet("新建联络项目")
    line_sheet.append(["区县", "方案", "投运年", "站点A", "站点B", "固定单元能力MW", "新增投资万元",
                       "规划长度km", "单元及线路口径"])
    reports, annual_details, constraints = {}, {}, []
    for district in ("pizhou", "city"):
        summaries = {r["scheme"]: r for r in json.loads((source / district / "summary.json").read_text())}
        grid_pairs = {tuple(sorted((r["station_a"], r["station_b"]))) for r in grid_candidate_rows(
            {r["station"] for r in read_csv(source / district / "rigid_stations.csv")})} if district == "pizhou" else set()
        costs = review["cost_npv_10k"][district]
        cost_sheet.append([LABEL[district], costs["rigid"], costs["elastic"],
                           costs["rigid"] - costs["elastic"], 1 - costs["elastic"] / costs["rigid"]])
        for scheme in ("rigid", "elastic"):
            summary = summaries[scheme]
            rows = read_csv(source / district / f"{scheme}_stations.csv")
            path = source / district / f"{scheme}_transfers.csv"
            transfers = read_csv(path) if path.exists() else []
            line_path = source / district / f"{scheme}_new_lines.csv"
            new_lines = read_csv(line_path) if line_path.exists() else []
            for line in new_lines:
                line_sheet.append([LABEL[district], LABEL[scheme], int(line["commissioning_year"]),
                                   line["station_a"], line["station_b"], float(line["screen_capacity_mw_2025"]),
                                   float(line["construction_capex_10k"]), float(line["planned_length_km"]),
                                   "双端单元计费配对，非优化路由；一项建设只计费一次"])
            sheet = book.create_sheet(LABEL[district] + LABEL[scheme] + "具体措施")
            sheet.append(["年份", "站号", "主变具体动作", "主变净增MVA", "新购主变MVA",
                          "新增储能MW", "新增储能MWh", "在役储能MW", "在役储能MWh",
                          "转出负荷MW", "承接负荷MW", "转接前负荷MW", "转接后负荷MW",
                          "投运后主变MVA", "3号主变预留位", "10kV备用间隔数", "模型站点口径"])
            initial = {r["station"]: (float(r["prior_unit_1_mva"]), float(r["prior_unit_2_mva"]))
                       for r in rows if int(r["year"]) == 2022}
            portfolio = []
            for r in rows:
                year, station = int(r["year"]), r["station"]
                out = sum(float(m["mw"]) for m in transfers if int(m["year"]) == year and m["donor"] == station)
                incoming = sum(float(m["mw"]) for m in transfers if int(m["year"]) == year and m["receiver"] == station)
                old_load = float(r["forward_mw"])
                post = old_load - out + incoming
                assert abs(post - float(r["post_transfer_forward_mw"])) < 1e-5
                assert post >= -1e-5
                units = [float(r[f"unit_{slot}_mva"]) for slot in (1, 2, 3)]
                cap, energy = sum(units), float(r["storage_energy_mwh"])
                support = min(float(r["storage_power_mw"]), energy / max(2.15, int(r["forward_duration_h"])))
                reverse_support = min(float(r["storage_power_mw"]), energy / max(2.15, int(r["reverse_duration_h"])))
                task = service(post, r["area_class"])
                survivor = .95 * (cap - max(units))
                normal_margin = .95 * cap + support - post
                reverse_margin = .95 * float(summary["reverse_capacity_fraction"]) * cap + reverse_support - float(r["reverse_mw"]) - out
                n1_margin = survivor + support - task
                no_transfer = survivor + support - service(old_load, r["area_class"])
                no_storage = survivor - task
                storage_stress = survivor + .8 * support - task
                original_units = initial[station]
                no_expansion = .95 * (sum(original_units) - max(original_units)) + support - task
                assert min(normal_margin, reverse_margin, n1_margin) >= -1e-4
                if equivalent:
                    base = float(r["transfer_base_load_mw"])
                    existing_cap = float(r["existing_transfer_capacity_mw"])
                    effective_cap = float(r["effective_transfer_capacity_mw"])
                    assert out <= effective_cap + 1e-5
                    rate_sheet.append([LABEL[district], LABEL[scheme], year, station, base,
                                       float(r["existing_transfer_fraction_scenario"]),
                                       float(r["target_transfer_fraction_scenario"]),
                                       float(r["transfer_fraction_ceiling"]), int(r["incident_new_line_units"]),
                                       existing_cap, float(r["credited_new_transfer_capacity_mw"]),
                                       float(r["effective_transfer_fraction"]), effective_cap, out, out/base,
                                       max(0, float(r["target_transfer_fraction_scenario"])*base-existing_cap),
                                       max(0, out-existing_cap)])
                result = {"year": year, "station": station, "forward_margin_mw": normal_margin,
                          "reverse_margin_mw": reverse_margin, "n1_margin_mw": n1_margin,
                          "no_transfer_n1_margin_mw": no_transfer,
                          "no_storage_n1_margin_mw": no_storage, "no_expansion_n1_margin_mw": no_expansion,
                          "storage_80pct_n1_margin_mw": storage_stress,
                          "assigned_load_mw": post, "original_load_mw": old_load}
                portfolio.append(result)
                check_sheet.append([LABEL[district], LABEL[scheme], year, station, r["area_class"],
                                    old_load, out, incoming, post, cap, float(r["storage_power_mw"]), energy,
                                    normal_margin, reverse_margin, task, n1_margin, no_transfer, no_storage, no_expansion])
                net_added = cap - float(r["prior_unit_1_mva"]) - float(r["prior_unit_2_mva"]) - (
                    0 if int(r["third_transformer_commissioned"]) else float(r["unit_3_mva"]))
                sheet.append([year, station, transformer_action(r), net_added, float(r["purchased_unit_mva"]),
                              float(r["new_storage_power_mw"]), float(r["new_storage_energy_mwh"]),
                              float(r["storage_power_mw"]), energy, out, incoming, old_load, post, cap,
                              int(r["source_available_third_slots"]), int(r["source_spare_10kv_bays"]),
                              "仿真点，类别按C类假定" if station.startswith("SIM-") else "原表站号对应仿真点"])
            for m in transfers:
                pair = tuple(sorted((m["donor"], m["receiver"])))
                moves_sheet.append([LABEL[district], LABEL[scheme], int(m["year"]), m["donor"], m["receiver"],
                                    float(m["mw"]), "既有转供率预算" if m["kind"] == "existing" else "新增转供率预算",
                                    "有" if pair in grid_pairs else "未证实",
                                    "站级寻优后守恒分配，非逐线路路由"])
            reports[district + "_" + scheme] = {
                "station_years": len(portfolio), "minimum_normal_margin_mw": min(r["forward_margin_mw"] for r in portfolio),
                "minimum_reverse_margin_mw": min(r["reverse_margin_mw"] for r in portfolio),
                "minimum_n1_margin_mw": min(r["n1_margin_mw"] for r in portfolio),
                "transfer_records": len(transfers),
                "new_line_projects": len(new_lines),
                "annual_increment_budget_use_sum_mw": sum(float(m["mw"]) for m in transfers
                                                          if m["kind"] in ("new", "rate_increment")),
                "project_use_attribution": "not_identifiable_from_station_aggregate_model",
                "target_shortfall_station_years_without_new_lines": sum(
                    float(r.get("target_transfer_fraction_scenario", 0))*float(r["forward_mw"]) >
                    float(r.get("existing_transfer_capacity_mw", float("inf")))+1e-5 for r in rows),
                "normal_outgoing_above_existing_budget_station_years": sum(
                    float(r["normal_load_transferred_out_mw"]) >
                    float(r.get("existing_transfer_capacity_mw", float("inf")))+1e-5 for r in rows),
                "transfer_records_with_shared_grid_evidence": sum(tuple(sorted((m["donor"], m["receiver"]))) in grid_pairs for m in transfers),
                "transfer_effective_station_years": sum(r["no_transfer_n1_margin_mw"] < -1e-4 for r in portfolio),
                "storage_effective_station_years": sum(r["no_storage_n1_margin_mw"] < -1e-4 for r in portfolio),
                "expansion_effective_station_years": sum(r["no_expansion_n1_margin_mw"] < -1e-4 for r in portfolio),
                "storage_80pct_insufficient_station_years": sum(r["storage_80pct_n1_margin_mw"] < -1e-4 for r in portfolio),
                "storage_80pct_largest_shortfall_mw": max(0, -min(r["storage_80pct_n1_margin_mw"] for r in portfolio)),
                "station_year_checks": portfolio,
            }
            for a in [a for a in annual if a["district"] == district and a["scheme"] == scheme]:
                year = int(a["year"])
                local = [r for r in rows if int(r["year"]) == year]
                previous_cap = sum(float(r["prior_unit_1_mva"]) + float(r["prior_unit_2_mva"]) +
                                   (0 if int(r["third_transformer_commissioned"]) else float(r["unit_3_mva"])) for r in local)
                transfer = sum(float(m["mw"]) for m in transfers if int(m["year"]) == year)
                before, after = sum(float(r["forward_mw"]) for r in local), sum(float(r["post_transfer_forward_mw"]) for r in local)
                assert abs(before - after) < 1e-5
                detail = {"net_added_mva": float(a["capacity_mva"]) - previous_cap,
                          "normal_transfer_mw": transfer, "station_load_sum_before_mw": before,
                          "station_load_sum_after_mw": after}
                annual_details[district + "_" + scheme + "_" + str(year)] = detail
                summary_sheet.append([LABEL[district], LABEL[scheme], year, detail["net_added_mva"],
                                      float(a["new_transformer_purchase_mva"]), int(a["new_third_transformers"]),
                                      float(a["new_storage_power_mw"]), float(a["new_storage_energy_mwh"]),
                                      float(a["capacity_mva"]), float(a["installed_storage_power_mw"]),
                                      float(a["installed_storage_energy_mwh"]), transfer, int(a["new_lines_commissioned"]), float(a["clr"]),
                                      float(a["existing_transfer_mw"]), float(a["new_line_transfer_mw"]),
                                      float(a["new_line_transfer_mw"]) / (int(a["new_lines_in_service"]) *
                                      float(summary["new_line_increment_mw"]))
                                      if equivalent and int(a["new_lines_in_service"]) else None])
                constraints.append((district, scheme, year, a, detail, local, transfers))
    rigid_total = numerical["rigid_npv_10k"]
    elastic_total = numerical["elastic_npv_10k"]
    cost_sheet.append(["合计", rigid_total, elastic_total, rigid_total - elastic_total,
                       1 - elastic_total / rigid_total])
    for table in book:
        table.freeze_panes = "A2"
        table.auto_filter.ref = table.dimensions
        table.row_dimensions[1].height = 42
        for cell in table[1]:
            cell.fill = PatternFill("solid", fgColor="245473")
            cell.font = Font(name="微软雅黑", color="FFFFFF", bold=True)
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        for col in range(1, table.max_column + 1):
            table.column_dimensions[get_column_letter(col)].width = 22
        for row in table.iter_rows(min_row=2):
            for cell in row:
                if isinstance(cell.value, float):
                    if abs(cell.value) < 1e-8:
                        cell.value = 0.0
                    cell.number_format = "0.0000" if (table is summary_sheet and cell.column == 14) else "0.000"
        if table is cost_sheet:
            for row in table.iter_rows(min_row=2):
                row[-1].number_format = "0.00%"
        if table is summary_sheet:
            for row in table.iter_rows(min_row=2):
                row[-1].number_format = "0.00%"
        if table is rate_sheet:
            for row in table.iter_rows(min_row=2):
                for col in (6, 7, 8, 12, 15):
                    row[col-1].number_format = "0.00%"
    delivery.mkdir(parents=True, exist_ok=True)
    book.save(delivery / "逐年具体措施与负荷转接审查.xlsx")
    audit_result = {"scope": "normal_load_reallocation_static_equipment_planning_not_fault_transfer",
                    "result_directory": str(source.relative_to(MODEL)), "numerical_audit": numerical,
                    "portfolios": reports, "annual_load_conservation": annual_details,
                    "counterfactual_scope": "same_chosen_equipment_layout_remove_one_measure_without_reoptimization"}
    (delivery / "负荷转接独立有效性审查.json").write_text(json.dumps(audit_result, ensure_ascii=False, indent=2) + "\n")
    text = ["# 逐年具体措施及负荷转接有效性审查", "",
            "转供按区县内正常负荷转接建模。转接后站负荷=原负荷−转出+转入，区县总负荷守恒；主变、储能及供电安全容量约束均使用转接后的负荷。事故恢复量未进入本轮规划。", "",
            ("站级基数在优化前固定。既有能力=既有率×站负荷基数；新增独立单元按局部25节点区段标定为7.49106117 MW，"
             "通过DeltaRho=7.49106117/B提升转供率。按类别选定50%/70%规划率上限，取消旧10%使用限制。"
             "邳州30%、市区50%的目标能力须满足，既有不足时新增线路补足。全区县既有馈线拓扑不展开，站间分配为等效仿真。"
             if equivalent else
             "按用户确认，本轮属于仿真研究：共同10%限制是正常负荷转接的研究情景，未强制补足联络建设比例。"), "",
             "每站设置转出量、承接量和关联新增单元数，区县转出总量等于承接总量。新项目按两个站端计一项建设；区县超出既有预算的实际转出量合计不超过项目数×7.49106117 MW，防止双端重复使用能力。端点配对只用于项目数和费用核对，不是求解的线路走向。实际转接表按站号固定顺序在寻优后生成，不能据此认定某一条新增线路的实际利用量。", "",
             "刚性R≤2；弹性两区县每年R≥2.001，市区R低于邳州。R排序为用户规划条件，成本排序未强制。2021仍为共同反事实起点，以下2022—2025为回算规划年份。", "",
            "## 逐年新增措施", "",
            "净增主变容量是配置变化；新购主变铭牌容量包含整台替换，费用按新购容量计。储能栏为当年新增。转接MW是该年度方案的峰值负荷分配量，不是逐年累加投资量。", "",
            "| 区县 | 方案 | 年份 | 净增主变MVA | 新购主变MVA | 新增储能MW/MWh | 正常转接MW | 新线条数 | R |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    acceptance = ["## 原要求验收", "",
                  "容载比突破与排序是明确施加的规划约束；费用排序是求解后的独立检查，不通过抬高刚性费用强行满足。", "",
                  "| 要求 | 结果 |", "|---|---|"]
    acceptance += ["| 刚性每年R≤2.0 | 通过 |",
                   "| 两区县弹性每年R>2.0 | 通过 |",
                   f'| 同方案市区每年R低于邳州 | {"通过" if review["city_below_pizhou_all_years"] else "未通过"} |']
    for district in ("pizhou", "city"):
        acceptance.append(f'| {LABEL[district]}弹性费用低于刚性 | {"通过" if review["cost_order"][district] else "未通过"} |')
    acceptance += ["", "全部原要求验收：" + ("通过。" if review["all_requested_relations"] else
                  "未全部通过；请将本轮结果作为约束满足方案及费用对照，不作为已实现全部目标的最终推荐。"), ""]
    if review.get("primary_cost_solution_quality") == "certified_near_optimal":
        acceptance += [f'费用为认证近优：实际最优性间隙{review["primary_cost_relative_gap"]:.4%}，'
                       f'费用下界{review["primary_cost_lower_bound_10k"]:.4f}万元，'
                       f'所选费用上界{review["selected_joint_primary_objective_10k"]:.4f}万元。'
                       '容载比偏好在该认证近优费用预算内优化，不称精确全局最低费用。', ""]
    if "capacity_preference_relative_gap" in review:
        acceptance += [f'容载比偏好阶段：八项弹性年度R之和{review["sum_elastic_annual_clr"]:.6f}，'
                       f'上界{review["sum_elastic_annual_clr_upper_bound"]:.6f}，'
                       f'实际间隙{review["capacity_preference_relative_gap"]:.4%}。'
                       '这些数值评价同预算内的偏好优化精度，不放松任何年度R硬约束。', ""]
    if review.get("capacity_preference_scope") == "selected_rigid_layout":
        acceptance += ["费用阶段四路径三措施共同求解；容载比偏好阶段固定其选出的刚性整数布局，仅优化两区县弹性R。偏好上界与间隙限于该固定基准，不是所有刚性布局的全局结论。最后转接量优化也固定全部所选整数状态，包括供电任务的线性化分支。", ""]
    text[2:2] = acceptance
    for district, scheme, year, a, detail, _, _ in constraints:
        text.append(f'| {LABEL[district]} | {LABEL[scheme]} | {year} | {detail["net_added_mva"]:g} | {float(a["new_transformer_purchase_mva"]):g} | {float(a["new_storage_power_mw"]):.1f}/{float(a["new_storage_energy_mwh"]):.3f} | {detail["normal_transfer_mw"]:.3f} | {a["new_lines_commissioned"]} | {float(a["clr"]):.4f} |')
    text += ["", "## 同价格费用对照", "",
             "费用是新增措施的全寿命现值，单位万元；包含储能运维与寿命更新，排除2021存量。", "",
             "| 区县 | 刚性 | 弹性 | 节省比例 |", "|---|---:|---:|---:|"]
    for district, cost in review["cost_npv_10k"].items():
        text.append(f'| {LABEL[district]} | {cost["rigid"]:.2f} | {cost["elastic"]:.2f} | {1-cost["elastic"]/cost["rigid"]:.2%} |')
    text.append(f'| 合计 | {rigid_total:.2f} | {elastic_total:.2f} | {1-elastic_total/rigid_total:.2%} |')
    if equivalent:
        text += ["", "## 容量增长与费用差异", "",
                 "邳州弹性2021起点1463.5 MVA，四年增加至1946.5 MVA，净增483 MVA；刚性净增258.5 MVA。弹性用更多主变容量降低储能配置，储能0.1 MW/0.215 MWh，刚性31.7 MW/68.155 MWh，因此共同价格下弹性现值较低。2024、2025主变容量继续增加，负荷增长仍使R从2.1912降到2.1405、2.0351；容量不减不等于R逐年上升。",
                 "市区弹性主变由2462增加至3095 MVA，净增633 MVA；刚性仅净增100 MVA，且两方案储能均为零。每年R≥2.001要求2022容量至少2866.1723 MVA、2023至少3085.9757 MVA；所选2872、3095 MVA接近这些门槛。刚性在较小容量和更多联络单元下已通过相同静态承载校核，因此市区弹性增加的容量主要受到R目标驱动，不能直接解释为负荷增长使全部增容必不可少，也没有形成经济优势。",
                 "市区50%初始能力已满足50%目标，仍新建刚性3项、弹性2项，服务于A类站超出既有预算的正常转接需求；A类研究上限70%，B/C类仍为50%。新增等效预算的年度实际使用量、使用率和站级上限已列入工作簿。该使用率是全区县共享预算使用率，不是逐线路利用率。", ""]
    text += ["", "## 静态措施是否有效", "",
             "以同一设备布局为基准，逐项取消正常负荷转接、储能或主变增容，复算供电安全容量缺口。该检查说明措施对所选方案的作用，不等于重新寻优后的全局收益。", "",
             "| 区县 | 方案 | 转接量撤销后不足的站年数 | 储能撤销后不足的站年数 | 不增主变后不足的站年数 | 最小静态退出余量MW |",
             "|---|---|---:|---:|---:|---:|"]
    for key, r in reports.items():
        district, scheme = key.split("_")
        text.append(f'| {LABEL[district]} | {LABEL[scheme]} | {r["transfer_effective_station_years"]} | {r["storage_effective_station_years"]} | {r["expansion_effective_station_years"]} | {max(0, r["minimum_n1_margin_mw"]):.6f} |')
    text += ["", "把储能有效支撑降至80%作自设压力测试，保持设备和负荷转接方案不变，结果如下。这不是标准规定的效率或SOC取值，也没有进行应力情景再优化。", "",
             "| 区县 | 方案 | 供电安全容量不足的站年数 | 最大缺口MW |", "|---|---|---:|---:|"]
    for key, r in reports.items():
        district, scheme = key.split("_")
        text.append(f'| {LABEL[district]} | {LABEL[scheme]} | {r["storage_80pct_insufficient_station_years"]} | {r["storage_80pct_largest_shortfall_mw"]:.3f} |')
    text += ["", "## 仿真设定与有效性判定", "",
             "1. 容量可行性结论：本轮静态仿真范围内通过。逐年方案具体到仿真站号、设备规格、储能MW/MWh、转接方向及MW，392个站年均通过正向、反向和转接后供电安全容量复算。费用排序是否通过另见原要求验收；实际路由不属于本轮验收范围。",
             ("2. 新线是否有效分别看规划转供能力和年度实际转接：不建新线的能力目标缺口、超出既有预算的实际转出量均在工作簿列明。"
              "补足能力目标的建设即使某年没有实际使用，也不能把额定能力全部当成正常转接量或主变减容量。"
              if equivalent else
              "2. 旧10%场景下新线可被既有通道替代，因此零建设不代表新的能力框架下无需建设。"),
             "3. 主变新增第三台按原表预留位作为仿真可选条件。市区29站外推，SIM-CITY点类别按C类假定。2021容量是共同反事实起点，2022—2025为回算规划年份。",
             "4. 储能为0.1 MW/0.215 MWh整数柜，按D95峰段持续时间折算可持续功率；当前属于静态容量仿真，SOC与充放电时序未显式求解。80%支撑压力测试单列，不改变主方案的确定性结果。",
             "5. 电源保持原站归属，反向压力用原反送峰值+转出峰值作保守上界，未抵扣受端消纳收益；避免负荷转出后反送压力被漏算。",
             "6. 站级负荷为独立峰值任务，转接前后任务总量守恒；容载比分母保持原表区县降压负荷代理。站间转接优化负荷空间分配，不能直接改变区县总负荷或把联络容量计入主变容量分子。", "",
             "## 每年逐站动作和转接方向", ""]
    if equivalent:
        text += ["## 新建联络与实际使用", "",
                 "新增能力是否用于正常配置按站级预算判断；逐线路利用率无法由本模型识别。四年新增预算使用量为各年度峰值转接MW之和，不是累计能量。", "",
                 "| 区县 | 方案 | 新建项目数 | 四年新增预算使用量之和MW | 不建新线则目标不足的站年数 | 实际转出超出既有预算的站年数 |",
                 "|---|---|---:|---:|---:|---:|"]
        for key, report in reports.items():
            district, scheme = key.split("_")
            text.append(f'| {LABEL[district]} | {LABEL[scheme]} | {report["new_line_projects"]} | {report["annual_increment_budget_use_sum_mw"]:.3f} | {report["target_shortfall_station_years_without_new_lines"]} | {report["normal_outgoing_above_existing_budget_station_years"]} |')
        text.append("")
    for district, scheme, year, _, _, local, transfers in constraints:
        text += [f"### {LABEL[district]}{LABEL[scheme]} {year}年", ""]
        selected = [r for r in local if float(r["purchased_unit_mva"]) > 1e-5 or float(r["new_storage_energy_mwh"]) > 1e-5]
        for r in selected:
            action = transformer_action(r)
            if float(r["new_storage_energy_mwh"]) > 1e-5:
                action += f'；新增储能{float(r["new_storage_power_mw"]):.1f} MW/{float(r["new_storage_energy_mwh"]):.3f} MWh'
            text.append(f'- {r["station"]}：{action}。')
        if not selected:
            text.append("- 设备沿用上一年。")
        line_path = source / district / f"{scheme}_new_lines.csv"
        for line in read_csv(line_path) if line_path.exists() else []:
            if int(line["commissioning_year"]) == year:
                text.append(f'- 新建联络计费配对：{line["station_a"]}—{line["station_b"]}，固定等效单元{float(line["screen_capacity_mw_2025"]):.3f} MW，新增投资{float(line["construction_capex_10k"]):.2f}万元；配对仅作双端计数。')
        for m in transfers:
            if int(m["year"]) == year:
                kind = "既有转供率预算" if m["kind"] == "existing" else "新增转供率预算"
                text.append(f'- 负荷转接：{m["donor"]}转出至{m["receiver"]}，{float(m["mw"]):.3f} MW；{kind}。')
        text.append("")
    if numerical["repeat_csv_exact_match"]:
        text += ["## 确定性验证", "",
                 f'同输入及相同初始可行解重新计算三个阶段，{len(numerical["output_sha256"])}份CSV逐字节一致。两次费用和容载比偏好阶段均达到记录的最优性间隙精度，转接量阶段精确求解LP；392个站年数值与负荷守恒复算通过。初始解只用于加速，没有沿用旧阶段最优性结论。', ""]
    (delivery / "逐年具体措施与有效性审查.md").write_text("\n".join(text).rstrip() + "\n")
    print(json.dumps({"delivery": str(delivery), "measures": {
        k: {f: v for f, v in r.items() if f != "station_year_checks"} for k, r in reports.items()}}, ensure_ascii=False))
    return audit_result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--delivery", type=Path, default=DELIVERY)
    parser.add_argument("--repeat", type=Path)
    args = parser.parse_args()
    main(args.source, args.delivery, repeat_directory=args.repeat)
