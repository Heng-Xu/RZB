"""绘制局部三联络的共享馈线审查图；不改动区县优化模型。"""

import csv
import json
from hashlib import sha256
from itertools import product
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
from scipy.optimize import linprog

from .feeder_2025 import FEEDER_SOURCE
from .pizhou_existing_ties import TOPOLOGY_SOURCE, build_feeder_headroom, read_cross_station_ties


ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "docs/2026-10-01局部联络仿真依据"
POLICY = ROOT / "参考政策/DL-T+5729-2023+配电网规划设计技术导则.pdf"
NAMES = {
    "PZXL-00092": "墩南线", "PZXL-00097": "墩西线", "PZXL-00099": "墩振线",
    "PZXL-00154": "河东线", "PZXL-00161": "河炮线", "PZXL-00173": "河镇线",
}
PATH_CAPACITY_SOURCE = Path(__file__).resolve().parents[1] / "data/tuomin/10kv_case/data/key_tie_path_parameter_impact.csv"
BLUE, ORANGE, INK, GREY = "#2465a5", "#c27821", "#243447", "#7e8994"
font_manager.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "font.size": 12,
                     "axes.unicode_minus": False, "svg.fonttype": "none"})


def box(ax, xy, width, height, text, face="#ffffff", edge=BLUE, size=12):
    x, y = xy
    patch = FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.04,rounding_size=0.12",
                          fc=face, ec=edge, lw=1.5, zorder=3)
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, text, ha="center", va="center",
            fontsize=size, color=INK, zorder=4, linespacing=1.65)


def arrow(ax, a, b, color=BLUE, lw=2.3, style="-|>", curved=0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=17, lw=lw,
                                color=color, connectionstyle=f"arc3,rad={curved}", zorder=2))


def save(fig, name):
    for suffix in ("png", "svg"):
        fig.savefig(DEST / f"{name}.{suffix}", dpi=180, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def screen(feeders, ties, mode):
    """与旧六馈线筛查同口径：共享发送负荷、共享接纳余量，分别约束。"""
    best = None
    for directions in product((-1, 0, 1), repeat=len(ties)):
        edges = []
        for tie, d in zip(ties, directions):
            if not d:
                continue
            a, b = tie["from_feeder_id"], tie["to_feeder_id"]
            if d == -1:
                a, b = b, a
            if mode == "A_to_B" and feeders[a]["station_id"] != "BDZ-00027":
                continue
            if mode == "B_to_A" and feeders[a]["station_id"] != "BDZ-00048":
                continue
            edges.append((tie["tie_id"], a, b))
        if not edges:
            continue
        matrix, limits = [], []
        for fid, row in feeders.items():
            matrix.append([float(a == fid) for _, a, _ in edges])
            limits.append(row["current_equivalent_active_power_mw"])
            matrix.append([float(b == fid) for _, _, b in edges])
            limits.append(row["receiving_current_headroom_mw"])
        result = linprog([-1] * len(edges), A_ub=matrix, b_ub=limits,
                         bounds=(0, None), method="highs")
        if result.success and (best is None or -result.fun > best["gross_mw"] + 1e-8):
            best = {
                "gross_mw": -float(result.fun),
                "net_A_to_B_mw": sum(float(q) * (1 if feeders[a]["station_id"] == "BDZ-00027" else -1)
                                       for (_, a, _), q in zip(edges, result.x)),
                "moves": [{"tie_id": t, "donor_feeder": a, "receiver_feeder": b, "q_mw": float(q)}
                          for (t, a, b), q in zip(edges, result.x) if q > 1e-8],
            }
    return best


def basis_figure():
    fig, ax = plt.subplots(figsize=(13.5, 6))
    ax.set(xlim=(0, 13.5), ylim=(0, 6)); ax.axis("off")
    ax.text(.2, 5.8, "规范中的典型结构：一条馈线分段、多点联络", fontsize=20, weight="bold", color=INK)
    ax.text(.2, 5.35, "依据 DL/T 5729—2023 图 C.0.1-3 作概念示意；本图不表示案例的实际开关位置。",
            fontsize=11, color=GREY)
    ax.plot([.7, .7], [2.8, 3.8], color=INK, lw=3)
    ax.text(.1, 4.05, "站端电源", color=INK)
    ax.plot([.7, 12.5], [3.3, 3.3], color=INK, lw=2)
    for x, label in ((1.5, "局部区段 P1"), (5.3, "局部区段 P2"), (9.1, "局部区段 P3")):
        box(ax, (x, 3.05), 2.2, .5, label, face="#eef4fb", size=12)
    for x in (4.3, 8.1):
        ax.plot([x - .12, x + .12], [3.1, 3.5], color=INK, lw=2)
        ax.text(x, 3.9, "分段点", ha="center", fontsize=11)
    for x, top, label in ((2.6, False, "邻近馈线1"), (6.4, True, "邻近馈线2"), (10.2, False, "邻近馈线3")):
        y = 4.45 if top else 1.85
        ax.plot([x, x], [3.3, y], color=BLUE, lw=2)
        ax.add_patch(Circle((x, (3.3 + y) / 2), .075, fc="white", ec=BLUE, lw=1.8, zorder=5))
        box(ax, (x - 1.1, y if top else y - .65), 2.2, .65, label, face="#edf6f5", size=12)
    ax.text(.35, .55, "局部负荷基数 = P1 + P2 + P3，按区段去重。\n多个联络点共享馈线和路径余量；联络数量不能直接乘整条馈线负荷。",
            fontsize=13, color=INK, linespacing=1.6)
    save(fig, "01_规范典型结构")


def topology_figure(feeders):
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set(xlim=(0, 16), ylim=(0, 9)); ax.axis("off")
    ax.text(.15, 8.72, "案例连接关系：三条跨站联络，共享河炮馈线", fontsize=21, weight="bold", color=INK)
    ax.text(.15, 8.27, "蓝线为基础跨站联络；灰线为站内增强情景。连接关系不表示这些开关同时合闸。",
            fontsize=11, color=GREY)
    for x, title in ((.3, "A站：墩集变 BDZ-00027"), (10.55, "B站：河湾变 BDZ-00048")):
        ax.add_patch(FancyBboxPatch((x, .8), 5.05, 7.1, boxstyle="round,pad=0.05,rounding_size=0.2",
                                   fc="#f7f9fc", ec="#cbd5df", lw=1.1))
        ax.text(x + 2.525, 7.55, title, ha="center", fontsize=14, weight="bold", color=INK)
    positions = {"PZXL-00092": (1.2, 6.4), "PZXL-00097": (1.2, 4.2), "PZXL-00099": (1.2, 2),
                 "PZXL-00161": (11.1, 5.4), "PZXL-00154": (11.1, 3), "PZXL-00173": (11.1, 1.05)}
    for fid, (x, y) in positions.items():
        row = feeders[fid]
        text = (f"{NAMES[fid]}  {fid}\n负荷 {row['current_equivalent_active_power_mw']:.3f} MW"
                f" / 余量 {row['receiving_current_headroom_mw']:.3f} MW")
        box(ax, (x, y), 3.8, 1.05, text,
            face="#fff1da" if fid == "PZXL-00161" else "white",
            edge=ORANGE if fid == "PZXL-00161" else BLUE, size=11)
    for name, a, b, label_y in (("T01", "PZXL-00092", "PZXL-00161", 6.87),
                               ("T03", "PZXL-00097", "PZXL-00161", 4.95),
                               ("T02", "PZXL-00099", "PZXL-00154", 2.96)):
        xa, ya = positions[a]; xb, yb = positions[b]
        ax.plot([xa + 3.8, xb], [ya + .525, yb + .525], color=BLUE, lw=2.4, zorder=2)
        ax.text(8.03, label_y, name, ha="center", color=BLUE, fontsize=14,
                bbox={"fc": "white", "ec": "none", "pad": 2})
    arrow(ax, (1.16, 4.7), (1.16, 2.53), color=GREY, style="-", curved=.7, lw=1.5)
    ax.text(.42, 3.67, "T05\n站内", fontsize=10, color=GREY, ha="center")
    arrow(ax, (14.96, 3.5), (14.96, 1.57), color=GREY, style="-", curved=-.45, lw=1.5)
    ax.text(15.4, 2.57, "T04\n站内", fontsize=10, color=GREY, ha="center")
    box(ax, (5.6, 7.13), 4.55, .75, "T01、T03共用河炮线\n接纳余量和可发送负荷各算一次", face="#fff6e8", edge=ORANGE, size=12)
    box(ax, (5.7, 1.04), 4.35, 1.1, "基础单元：5条馈线、3条联络\n去重局部负荷：29.270 MW\nT04、T05另作站内重构情景", face="#eef4fb", size=11)
    ax.text(.3, .31, "数据：原始线路台账 + V2联络关系表；负荷按10 kV、PF=0.95和2025最大电流折算。\n年度各馈线峰值组成静态压力包络，数值用于仿真标定，不是同一时刻的实测潮流。", color=GREY, fontsize=10)
    save(fig, "02_案例共享馈线结构")


def sharing_figure(feeders, result):
    fig, axes = plt.subplots(1, 2, figsize=(16, 8.2))
    fig.suptitle("同一组三联络，两个方向的共享瓶颈不同", fontsize=21, weight="bold", color=INK, y=.98)
    for ax in axes:
        ax.set(xlim=(0, 8), ylim=(0, 8)); ax.axis("off")
    ax = axes[0]
    ax.text(.1, 7.65, "A站 → B站：共享接纳余量", color=BLUE, fontsize=17, weight="bold")
    box(ax, (.15, 5.52), 2.9, .85, "墩南可发送 6.459 MW\n经T01", size=12)
    box(ax, (.15, 3.97), 2.9, .85, "墩西可发送 3.432 MW\n经T03", size=12)
    box(ax, (4.42, 4.5), 3.15, 1.22, "河炮线共用余量\nH = 7.714 MW", face="#fff1da", edge=ORANGE, size=14)
    arrow(ax, (3.1, 5.94), (4.38, 5.15)); arrow(ax, (3.1, 4.39), (4.38, 5.03))
    ax.text(.4, 3.36, "T01、T03同向转入：q01 + q03 ≤ 7.714 MW", color=ORANGE, fontsize=13)
    ax.text(.4, 2.87, "T02另受河东余量限制：≤ 0.912 MW", color=INK, fontsize=13)
    box(ax, (.4, 1.66), 7.1, .75, f"整组同向上限：7.714 + 0.912 = {result['A_to_B']['gross_mw']:.3f} MW",
        face="#e9f3fb", size=14)
    ax.text(.4, 1.1, "逐条独立相加会得到10.803 MW，重复使用河炮余量。", color=GREY, fontsize=11)
    ax = axes[1]
    ax.text(.1, 7.65, "B站 → A站：共享发送负荷", color=BLUE, fontsize=17, weight="bold")
    box(ax, (.2, 4.5), 3.15, 1.22, "河炮线共用负荷\nP = 2.077 MW", face="#fff1da", edge=ORANGE, size=14)
    box(ax, (4.55, 5.52), 2.95, .85, "墩南接纳余量1.522 MW\n经T01", size=11)
    box(ax, (4.55, 3.97), 2.95, .85, "墩西接纳余量4.549 MW\n经T03", size=11)
    arrow(ax, (3.38, 5.15), (4.5, 5.94)); arrow(ax, (3.38, 5.03), (4.5, 4.39))
    ax.text(.4, 3.36, "T01、T03同向转出：q01 + q03 ≤ 2.077 MW", color=ORANGE, fontsize=13)
    ax.text(.4, 2.87, "T02另受墩振余量限制：≤ 1.448 MW", color=INK, fontsize=13)
    box(ax, (.4, 1.66), 7.1, .75, f"整组同向上限：2.077 + 1.448 = {result['B_to_A']['gross_mw']:.3f} MW",
        face="#e9f3fb", size=14)
    ax.text(.4, 1.1, "逐条独立相加会得到5.046 MW，重复使用河炮负荷。", color=GREY, fontsize=11)
    fig.text(.04, .03, "数值为源端静态筛查上限：已计共享馈线限制；尚未计分段负荷块、路径热限与电压约束。\n"
             "用于解释标定方法，不能将8.626、3.525直接标为已验证的实际转接能力。", color=GREY, fontsize=11)
    fig.subplots_adjust(left=.03, right=.98, top=.9, bottom=.13, wspace=.06)
    save(fig, "03_共享资源与方向差异")


def design_channel_basis(feeders):
    """以允许电流和路径参数定义热容量上界，不用历史负荷和历史接纳余量标定。"""
    with PATH_CAPACITY_SOURCE.open(encoding="utf-8-sig", newline="") as h:
        path_rows = [r for r in csv.DictReader(h) if r["tie_id"] == "TIE-002"]
    if {r["feeder_alias"] for r in path_rows} != {"dnan", "hpao"}:
        raise ValueError("T01两侧路径容量依据不完整")
    component_limits = {
        "donor_feeder_source_allowed_current_a": feeders["PZXL-00092"]["allowed_current_a"],
        "receiver_feeder_source_allowed_current_a": feeders["PZXL-00161"]["allowed_current_a"],
        **{r["feeder_alias"] + "_path_simulation_base_current_a": float(r["imax_base_a"]) for r in path_rows},
    }
    limit = min(component_limits.values())
    import math
    s_max = math.sqrt(3) * 10 * limit / 1000
    normal_loading_limit = .70
    p_ceiling = s_max * .95
    return {
        "unit_id": "LOCAL_FEEDER_PLANNING_LOAD_BASE_V1",
        "status": "proposed_standard_local_load_base_with_explicit_planning_assumptions",
        "unit_definition": "sending_side_supply_area_of_one_standard_multi_section_multi_tie_10kv_feeder",
        "reference_relation": "V2:T01 = TIE-002 = dnan_to_hpao",
        "component_current_limits_a": component_limits,
        "simulation_limiting_current_a": limit,
        "nominal_line_voltage_kv": 10.0,
        "assumed_power_factor": 0.95,
        "channel_apparent_load_ceiling_mva": s_max,
        "channel_active_load_ceiling_mw": p_ceiling,
        "normal_planning_loading_limit": normal_loading_limit,
        "local_load_base_upper_mw": normal_loading_limit * p_ceiling,
        "load_base_calculation": "normal_planning_loading_limit * sqrt(3) * nominal_line_voltage_kv * limiting_current_a * power_factor / 1000",
        "loading_limit_reference": {
            "standard": "DB11/T 2077-2023",
            "position": "6.1.4 Table 3,overhead_multi_section_moderate_tie",
            "url": "https://bzh.scjgj.beijing.gov.cn/bzh/apifile/file/2023/20230505/0064b6d2-bccf-4406-9aed-da02e86dea64.pdf",
            "scope": "reference_for_simulation_not_mandatory_Xuzhou_requirement",
        },
        "calculation": "sqrt(3) * nominal_line_voltage_kv * limiting_current_a * power_factor / 1000",
        "transfer_fraction_upper": None,
        "fraction_status": "provided_by_upper_model_policy_configuration_not_reestimated_in_this_review",
        "transfer_fraction_definition": "DL/T5729-2023_2.0.15_transferable_load_divided_by_total_load_of_the_same_defined_supply_area",
        "local_fraction_interface": "Q_local_upper = specified_transfer_fraction * local_load_base_upper_mw",
        "do_not_change_existing_fraction_values_here": True,
        "shared_feeder_rule": "one_feeder_has_one_local_load_base_and_one_outgoing_budget_shared_by_all_its_ties",
        "thermal_flow_constraint": "q_A_to_B + q_B_to_A <= channel_active_load_ceiling_mw",
        "tighter_bound_requires": ["switchable_section_design_capacity", "shared_feeder_and_path_capacity", "chosen_design_operating_scenario"],
        "upper_model_checks": ["post_transfer_transformer_capacity", "post_transfer_supply_security_capacity"],
        "normal_transfer_scope": "normal_load_reallocation_not_fault_restoration",
        "fixed_year_comparison_policy": "reuse_design_specification_without_county_load_scaling",
        "copy_rule": "using_the_reference_spec_for_other_channels_is_an_explicit_simulation_assumption",
        "equipment_assumption": "additional_equivalent_channel_elements_do_not_have_lower_current_limits",
        "source_hashes": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                          for p in (FEEDER_SOURCE, PATH_CAPACITY_SOURCE, POLICY)},
    }


def load_base_figure(design):
    fig, ax = plt.subplots(figsize=(15, 7.7))
    ax.set(xlim=(0, 15), ylim=(0, 7.7)); ax.axis("off")
    ax.text(.2, 7.4, "局部负荷基数：先确定统计区域，再构造规划负荷上限", fontsize=20, weight="bold", color=INK)
    labels = ["线路规格\n10kV / 485A / PF=0.95", "承载能力校核\n7.980 MW",
              "规划负载率上限\n70%（参考标准）", f"局部区域负荷基数\n{design['local_load_base_upper_mw']:.3f} MW"]
    for i, text in enumerate(labels):
        box(ax, (.3 + i * 3.7, 5.66), 3.25, 1.0, text,
            face="#e9f3fb" if i == 3 else "white", size=12)
        if i < 3:
            arrow(ax, (3.6 + i * 3.7, 6.16), (3.91 + i * 3.7, 6.16))
    box(ax, (.5, 2.22), 5.8, 2.2,
        f"发送侧局部供电区域：一条标准馈线\n规划最大负荷 P_base = {design['local_load_base_upper_mw']:.3f} MW\n"
        "多条联络共享同一份区域负荷基数", face="#eef4fb", size=14)
    box(ax, (9.5, 3.65), 4.7, .9, "接收馈线1：另校核接纳余量", face="#edf6f5", size=13)
    box(ax, (9.5, 1.85), 4.7, .9, "接收馈线2：另校核接纳余量", face="#edf6f5", size=13)
    arrow(ax, (6.36, 3.48), (9.44, 4.07)); arrow(ax, (6.36, 3.06), (9.44, 2.28))
    ax.text(7.83, 4.13, "q1", ha="center", color=BLUE, fontsize=14)
    ax.text(7.83, 2.32, "q2", ha="center", color=BLUE, fontsize=14)
    box(ax, (4.05, .73), 7.7, .85, "q1 + q2 ≤ ρ × P_base；共享负荷只计一次\nρ沿用导则定义，70%是规划负载率，不是转供率", face="#fff1da", edge=ORANGE, size=13)
    ax.text(.3, .2, "依据：本项目台账与路径规格；DB11/T 2077—2023第6.1.4条表3作为仿真规划参考。\n"
            "设计单元采用多分段适度联络类型；不宣称实际线路已满足该目标，也不将北京标准表述为徐州强制参数。",
            color=GREY, fontsize=10)
    save(fig, "04_局部负荷基数定义")


def write_review(feeders, ties, results, bounds):
    participating = {fid for t in ties for fid in (t["from_feeder_id"], t["to_feeder_id"])}
    base = sum(feeders[f]["current_equivalent_active_power_mw"] for f in participating)
    all_base = sum(r["current_equivalent_active_power_mw"] for r in feeders.values())
    rows = []
    for fid, row in feeders.items():
        rows.append({"馈线": NAMES[fid], "馈线编号": fid, "站编号": row["station_id"],
                     "2025最大电流A": row["observed_max_current_a"],
                     "电流折算负荷MW": row["current_equivalent_active_power_mw"],
                     "接纳余量MW": row["receiving_current_headroom_mw"],
                     "三联络基础单元是否涉及": int(fid in participating),
                     "原始文件行号": row["source_row"]})
    with (DEST / "六馈线负荷与共享资源.csv").open("w", encoding="utf-8-sig", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    with (DEST / "三联络方向边界.csv").open("w", encoding="utf-8-sig", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=list(bounds[0])); writer.writeheader(); writer.writerows(bounds)
    snapshot = {
        "scope": "source_end_static_upper_screen_excluding_intra_station_ties_and_path_constraints",
        "scheme": "observed_load_condition_screen_for_explaining_shared_resources_not_design_upper_basis",
        "source_hashes": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                          for p in (FEEDER_SOURCE, TOPOLOGY_SOURCE, POLICY)},
        "base_cross_station_feeder_count": len(participating), "base_cross_station_tie_count": len(ties),
        "local_unique_load_base_mw": base, "six_sample_load_base_mw": all_base,
        "group_direction_fractions_on_unique_base": {m: results[m]["gross_mw"] / base for m in ("A_to_B", "B_to_A")},
        "direction_screens": results, "individual_edge_upper_bounds": bounds,
        "policy_positions": {"structure": "7.1.4(2),7.3.2-7.3.4,Appendix C Fig.C.0.1-3",
                             "local_pdf_pages_1_based": [28, 29, 30, 53]},
        "excluded_from_certification": ["simultaneous_measured_peaks", "actual_switching_blocks",
                                         "path_thermal_and_voltage", "actual_county_network_coverage"],
    }
    (DEST / "计算与来源核验.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    unit = {
        "unit_id": "PZ_LOCAL_THREE_TIE_SHARED_V1",
        "status": "observed_load_condition_example_not_selected_design_upper_basis",
        "reference_year": 2025,
        "local_load_base_mw": base,
        "base_definition": "sum_of_unique_five_participating_feeder_loads",
        "fixed_year_comparison_policy": "reuse_reference_parameters_without_county_load_scaling",
        "positive_net_transfer": "A_to_B",
        "net_transfer_lower_mw": -results["B_to_A"]["gross_mw"],
        "net_transfer_upper_mw": results["A_to_B"]["gross_mw"],
        "direction_fractions": snapshot["group_direction_fractions_on_unique_base"],
        "feeders": [{"feeder_id": f, "station_role": "A" if feeders[f]["station_id"] == "BDZ-00027" else "B",
                     "load_mw": feeders[f]["current_equivalent_active_power_mw"],
                     "receiving_headroom_mw": feeders[f]["receiving_current_headroom_mw"]}
                    for f in sorted(participating)],
        "ties": [{"tie_id": t["tie_id"], "from_feeder_id": t["from_feeder_id"],
                  "to_feeder_id": t["to_feeder_id"]} for t in ties],
        "resource_rule": "all_outflows_share_donor_load_and_all_inflows_share_receiving_headroom",
        "upper_model_load_update": ["L_A_after = L_A_before - net_transfer", "L_B_after = L_B_before + net_transfer"],
        "require_upper_model_checks": ["post_transfer_transformer_capacity", "post_transfer_supply_security_capacity"],
        "normal_transfer_scope": "normal_load_reallocation_not_fault_restoration",
        "new_tie_rule": "add_specific_feeder_edge_and_recompute_shared_group_capacity",
        "cost_unit_rule": "one_tie_edge_cost_is_distinct_from_three_tie_group_cost",
        "coverage_rule": "declare_station_pairs_and_unit_count_and_do_not_duplicate_feeder_resources",
        "simplifications": snapshot["excluded_from_certification"],
        "source_hashes": snapshot["source_hashes"],
    }
    (DEST / "现状条件共享约束示例.json").write_text(json.dumps(unit, ensure_ascii=False, indent=2) + "\n")
    design = design_channel_basis(feeders)
    design["status"] = "historical_local_feeder_basis_not_current_station_rate_denominator"
    design["current_scheme"] = "站级转供率与10kV联络方案.md"
    (DEST / "固定局部仿真单元参数.json").write_text(json.dumps(design, ensure_ascii=False, indent=2) + "\n")
    load_base_figure(design)
    brief = f"""# 局部负荷基数确认

推荐固定基数：**{design['local_load_base_upper_mw']:.6f}MW／一个标准发送馈线供电区域**，展示取5.59MW，计算保留原值。转供率继续由上层按导则口径提供，本轮不重新估计比例。

DL/T 5729—2023第2.0.15定义的分母是同一供电区域总负荷。仿真统计区域明确为标准发送馈线所供的局部区域；接收侧是其转供去向，不加入该发送区域的分母。定义可查项目内[正式导则](../../参考政策/DL-T+5729-2023+配电网规划设计技术导则.pdf)PDF第13页／印刷第3页。

选T01作为规格原型，因为其两侧联络和源端路径能追溯。本项目台账中墩南线允许电流485A、河炮线595A，路径仿真基准分别500A、550A，取限流规格485A。在10kV、PF=0.95的明确仿真假定下，承载能力为√3×10×485×0.95/1000={design['channel_active_load_ceiling_mw']:.6f}MW。

采用多分段适度联络架空馈线作为标准仿真类型。[北京市市场监督管理局公开的DB11/T 2077—2023](https://bzh.scjgj.beijing.gov.cn/bzh/apifile/file/2023/20230505/0064b6d2-bccf-4406-9aed-da02e86dea64.pdf)第6.1.4条表3给出70%的负载率上限。用它构造规划工况：P_base=0.70×{design['channel_active_load_ceiling_mw']:.6f}={design['local_load_base_upper_mw']:.6f}MW。

70%是规划负载率λ，和转供率ρ分别记录。引用北京地方标准是仿真参考，不是声称它是徐州的强制参数，也不声称实际T01已满足所选规划接线与负载率。所选基数是标准单元的规划负荷上限，现状峰值只用于对照。

接口：Q_local_upper=ρ×P_base=ρ×{design['local_load_base_upper_mw']:.6f}MW。多条联络若共用同一发送馈线，只设一份该区域负荷和转出预算，由这些联络共同分配；共用接收馈线时合计校核接纳余量。约7.98MW承载能力、可切换区段和转接后的站容量另行校核。

![局部负荷基数定义](04_局部负荷基数定义.png)

本次确认局部仿真基数；尚未把新基数接入区县逐年求解，原年度结果不作本轮新结果。
"""
    current_notice = (
        "> 当前采用[站级转供率与10 kV联络等效方案](站级转供率与10kV联络方案.md)："
        "站级负荷基数乘转供率得到能力，新增独立联络以局部区段7.49106117 MW标定比例增量。"
        "本文件以下保留此前局部馈线分析；5.59 MW不作为当前站级转供率的分母。\n\n")
    (DEST / "局部负荷基数确认.md").write_text(
        current_notice + brief.rstrip() + "\n", encoding="utf-8")
    feeder_table = "\n".join(f"| {r['馈线']} | {r['馈线编号']} | {r['电流折算负荷MW']:.6f} | {r['接纳余量MW']:.6f} | {'是' if r['三联络基础单元是否涉及'] else '否，仅由站内T04间接参与'} |" for r in rows)
    edge_table = "\n".join(f"| {r['tie_id']} | {r['A_feeder']}—{r['B_feeder']} | {r['A_to_B_upper_mw']:.6f} | {r['B_to_A_upper_mw']:.6f} |" for r in bounds)
    text = f"""# 局部联络仿真：规范依据、共享馈线与推荐方案

本轮只确认“局部负荷基数”，不重算或修改上层已采用的转供比例。转供率继续按DL/T 5729—2023第2.0.15定义：特定停运条件下可转移负荷占同一供电区域总负荷的比例。标准仿真单元的统计区域明确为一条发送侧典型馈线所供的局部区域；比例所乘的分母是该区域的规划最大负荷，不能直接用导线热容量替代。

推荐固定局部负荷基数为 **{design['local_load_base_upper_mw']:.6f}MW（展示为约5.59MW）**。规格参考本项目T01路径：限流基准485A，10kV，PF=0.95；另按官方公开的DB11/T 2077—2023第6.1.4条表3，参考多分段适度联络架空线路70%的负载率上限构造规划工况。485A来自本项目数据，70%是北京地方标准的仿真参考，PF=0.95为研究假定。该数值不是六馈线平均负荷，也不是徐州的强制统一负荷值。

约7.98MW另作承载能力校核，不作为上述分母。下面第2—4节保留现状条件的共享约束案例；29.270MW是五馈线样本统计负荷和，29.47%/12.04%是该样本场景的方向筛查结果，均不替换本轮基准或既定比例。旧28.29%数值如由上层继续采用，应按明确的局部统计范围作为仿真参数使用，不能称为已验证的全区县导则转供率。

本次交付为建模方案审查；现有区县求解模型、逐年结果和成本没有在本次更改。

## 1. 规范与文献依据

| 来源 | 已核位置 | 能支持的建模选择 |
| --- | --- | --- |
| DL/T 5729—2023《配电网规划设计技术导则》正式版 | 7.1.4(2)；PDF第28页／印刷18页 | 在同一供电网格或单元内组织中压联络，避免过多接线组混杂交织；多分段适度联络是典型结构之一。 |
| 同上 | 7.3.2；PDF第29页／印刷19页 | 结合变电站位置、负荷分布，以供电网格为单位设计目标网架和逐年过渡方案。 |
| 同上 | 7.3.3、7.3.4；PDF第29—30页／印刷19—20页 | 分段应依据线路长度与负荷分布；联络点数量依据周边电源和线路负载，一般不超过3个。 |
| 同上 | 附录C图C.0.1-3；PDF第53页／印刷43页 | 一条馈线可以在不同区段联络多条邻近馈线；这种结构天然共享线路和区段资源。 |
| Baran、Wu，1989 | 论文第1页引言、图1；后续网络重构模型 | 通过分段开关与联络开关改变供电归属以平衡负荷、缓解过载；可研究站间、馈线间或支线间正常负荷转接。 |

[国家能源局发布清单，序号264](https://zfxxgk.nea.gov.cn/1310759283_17047031765681n.pdf)；[全国标准信息公共服务平台](https://hbba.sacinfo.org.cn/stdDetail/4326449b56df49cdc18fb406b61818086261bab5fb90fa318e864e4b499b08e7)。

条款已对照项目内[正式PDF](../../参考政策/DL-T+5729-2023+配电网规划设计技术导则.pdf)人工核读。结构示意按概念重新绘制，未把当前案例直接命名为完整“三分段三联络”：案例中的“三条跨站联络”是两站多馈线之间的三条边，分段位置仍应单独定义。

参考文献：Baran M E, Wu F F. Network reconfiguration in distribution systems for loss reduction and load balancing. IEEE Transactions on Power Delivery, 1989, 4(2): 1401–1407. [DOI:10.1109/61.25627](https://doi.org/10.1109/61.25627)；[作者所在高校托管的原文](https://ecal.studentorg.berkeley.edu/tbsi/Energy-Systems-Optimization-Course/References/Baran89%20-%20UCB%20-%20DistFlow.pdf)。

规范支持接线与校核原则；它没有为这个仿真单元规定8.215MW、11.764MW、28.29%等固定参数。DL/T 5729—2023第7.1.2(1)中的站间转供比例处于故障或检修语境。本轮保留既定转供率作为站级等效规划能力情景，正常配置用途参照第2.0.16条，不声称比例来自逐站实测。

![规范典型结构](01_规范典型结构.png)

## 2. 案例结构与共享馈线

三条跨站联络按V2工作簿“02_联络关系”第2—4行：

- T01：墩南线（A站）合金厂支线4杆 ↔ 河炮线（B站）59杆。
- T02：墩振线（A站）王场湖支线17杆 ↔ 河东线（B站）93杆。
- T03：墩西线（A站）王场湖支线14 ↔ 河炮线（B站）王场湖支线1杆。

T01和T03分别接入河炮线的不同位置，共享其站端通路及相关馈线容量；不能视作两条独立河炮线。仅凭现有关系表不能断言两段路径完全重合，精细仿真应逐段检查共享路径和可切换负荷块。

T04连接河东与河镇，同属B站；T05为墩西与墩振之间的站内开闭所关系。同站重构本身不改变两站净负荷，但可能改变馈线接纳余量，宜作为增强情景重新求解。不能把T04或T05直接加成新的跨站容量。河镇不是三条基础跨站边的端点，所以基础单元去重为5条馈线、3条联络。

![案例连接关系](02_案例共享馈线结构.png)

## 3. 负荷和容量依据

统一折算采用P=√3×10kV×I×0.95/1000（MW），接纳余量H=√3×10kV×max(I允许−I最大,0)×0.95/1000。功率因数0.95为仿真假定；统一使用最大电流避开河东有功记录为0但电流非0的矛盾。

| 馈线 | 编号 | 折算负荷MW | 接纳余量MW | 三联络基础单元涉及 |
| --- | --- | ---: | ---: | --- |
{feeder_table}

基础单元去重总负荷为 **{base:.6f} MW**。六馈线样本总负荷为 **{all_base:.6f} MW**。逐条累加三条联络两端负荷则为31.346942MW，其中河炮的2.076720MW被重复一次；这三种基数不能混用。

各馈线年度最大电流通常不在同一时刻。上述负荷是规划压力包络，不是同步实测总负荷，也不用于替换区县容载比分母。

## 4. 共享约束与方向性

令q为局部负荷转接量，每条馈线的所有转出量之和不超过其可发送负荷，所有转入量之和不超过其接纳余量。为说明原比例为何有偏差，先沿用原源端筛查口径：可发送负荷暂以整条局部馈线负荷作为上界；尚未加入分段负荷块、路径热限和电压约束。

| 联络 | 两端馈线 | A→B单条独立筛查上限MW | B→A单条独立筛查上限MW |
| --- | --- | ---: | ---: |
{edge_table}

A→B时，T01、T03均转入河炮，需满足q01+q03≤7.713697MW；T02≤0.912072MW。整组上限为 **{results['A_to_B']['gross_mw']:.6f} MW**，而独立相加会得到10.802533MW。

B→A时，T01、T03均从河炮转出，需满足q01+q03≤2.076720MW；T02≤1.447994MW。整组上限为 **{results['B_to_A']['gross_mw']:.6f} MW**，而独立相加会得到5.046425MW。

线性规划枚举方向并检查共享约束得到上述结果。A→B最优分配并非唯一，附件保存了一组可行最优解。这些是源端静态上限，不能冒称完整配电潮流已验证的转接能力。

![共享容量和方向差异](03_共享资源与方向差异.png)

原六馈线比例计算得到9.983428MW，是允许不同联络取相反站间方向时的毛转接量：T01 A→B 6.458714MW，T02 B→A 1.447994MW，T03 B→A 2.076720MW。该解的A→B净转接量仅为 **2.934000MW**。毛转接量除以六馈线35.292234MW所得28.2879%，不能直接作为某一站减负比例。

## 5. 确定可乘转供率的局部负荷基数

以已有T01为设计规格参照（不是以其现状流量为参照）：

| 限流环节 | 依据 | 电流上限A |
| --- | --- | ---: |
| 墩南馈线 | 原始线路台账“最大允许电流” | 485 |
| 河炮馈线 | 原始线路台账“最大允许电流” | 595 |
| 墩南侧路径导线 | 参数库中的路径仿真基准值 | 500 |
| 河炮侧路径导线 | 参数库中的路径仿真基准值 | 550 |

先取限流规格I_lim=485A。S_ceiling=√3×10×485/1000={design['channel_apparent_load_ceiling_mva']:.6f}MVA；P_ceiling=S_ceiling×0.95={design['channel_active_load_ceiling_mw']:.6f}MW。导线参数为仿真基准，PF=0.95和其他等效元件不设置更低限流值为明确研究假定。

再选定多分段适度联络架空馈线为标准仿真接线。[DB11/T 2077—2023官方公开文本](https://bzh.scjgj.beijing.gov.cn/bzh/apifile/file/2023/20230505/0064b6d2-bccf-4406-9aed-da02e86dea64.pdf)第6.1.4条表3给出该类型70%的线路负载率控制上限。于是局部区域的规划负荷基数P_base=0.70×P_ceiling={design['local_load_base_upper_mw']:.6f}MW。这里70%是规划负载率，和导则定义的转供率ρ分别记录；不改变ρ。

北京地方标准用于确定本仿真的规划工况参考，不表述为徐州强制执行要求。T01提供线路和路径规格原型，不宣称该实际馈线已经采用或满足所选标准接线与70%目标。其现状峰值可以超过所选仿真规划值；本轮建立的是固定标准单元。

接口为Q_local_upper=ρ×P_base，即ρ×5.586297MW；ρ按上层既定的导则口径提供。ρ的分子和分母指向同一个局部供电区域，不用两端负荷相加或整站负荷替代发送侧区域分母。“固定局部仿真单元参数.json”保存基数和校核能力，现状示例另存，比例留由原配置提供。

正常站间负荷转接量作为另一个优化变量，在这一联络能力预算内选择；不把正常运行转接量称为导则停运条件下已经验证的转供率。线路能力、接纳余量、可切换区段和站级容量同时校核。

## 6. 联络结构接入站级模型的规则

1. 保留基础五馈线、三联络结构及T01/T03共用河炮的关系。设计能力按通道及馈线容量设置；现状P、H作为验证场景输入，不作为不变的物理转供比例上限。六馈线原始数据全部保留，T04/T05另作站内重构增强情景。
2. 每个参与区县站对配置明确数量的局部单元，登记其对应模拟馈线资源。不同单元不得重复占用同一馈线负荷和余量；既有网络不默认全部站对互联。
3. 在局部子模型中选择可切换负荷块和开关状态，保证供电归属单一、正常运行保持辐射结构，并检查馈线和共享路径容量。精细潮流可参考Baran—Wu的配电网重构建模；轻量研究模型可采用明确标注的源端共享资源代理。
4. 一条发送馈线供电区域使用第5节约5.59MW的局部基数。多个联络共享同一发送馈线时，只登记一份区域负荷和ρ×P_base转出预算，由这些联络共同分配；共用受端馈线时合计检查接纳余量。约7.98MW承载能力另行校核。现状条件筛查的方向比例不替换原比例配置。
5. 上层用有符号净转接量t更新站负荷：L'_A=L_A−t，L'_B=L_B+t。按转接后负荷校核主变容量与供电安全要求，区县总负荷守恒。刚性、弹性使用同一局部单元和成本口径。
6. 新建决策添加具体馈线之间的联络边，重新计算整组能力；如果新增边仍绑定同一共享瓶颈，它的容量收益可以为0。只有新增边同时拓展可发送负荷或可接纳路径时，整组能力才可能增加。单条新线成本和完整三联络组成本分别计费。
7. 固定单元用于2022—2025年对比时，逐年沿用明确的局部参考参数。若另研究局部负荷增长，应调整局部馈线P并重新计算余量和方向能力，不能无条件按区县总负荷增长同比增加转接能力。

采用这一方案后，局部负荷基数来自线路规格与所选规划负载率上限；转供率定义和配置保持独立。实际转接量在局部能力预算及共享约束内由年度优化选择。

## 7. 复算与附件

从“实验/研究”执行：

```bash
/home/xh/anaconda3/envs/xuzhou110kv_clr/bin/python -m rebuild_2026.build_local_tie_review
```

附件：四张PNG和对应SVG；局部负荷基数确认说明；六馈线资源CSV；三联络方向边界CSV；固定局部仿真单元参数JSON；计算与来源核验JSON（原始文件SHA256、枚举方向LP结果、毛转接与净转接记录）。
"""
    history = text.split("## 1. 规范与文献依据", 1)[1]
    overview = (
        "# 10 kV联络：当前等效方案与局部数据依据\n\n"
        + current_notice
        + "当前方案不要求全区县既有馈线拓扑。既有能力为rho_initial × B_station；"
        "一个独立新增单元的比例提升为7.49106117 / B_station，"
        "新增线路不改变站负荷基数，不重复叠加能力。\n\n"
        + "参数接口为rebuild_2026.station_transfer_equivalent；"
        "当前参数见[站级等效转供参数](站级等效转供参数.json)，"
        "参照表见[逐站逐年转供基数与单线增量](逐站逐年转供基数与单线增量参照.csv)。"
        "年度求解器已接入站级能力约束，具体口径见"
        "[三措施优化模型说明](../2026-10-01站级转供率三措施优化/模型与参数说明.md)。\n\n"
        + "以下是规范、样本共享关系和此前局部基数讨论的计算记录。\n\n"
        + "## 1. 规范与文献依据")
    (DEST / "README.md").write_text(overview + history.rstrip() + "\n", encoding="utf-8")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    feeders = {r["feeder_id"]: r for r in build_feeder_headroom()}
    ties = read_cross_station_ties()
    results = {mode: screen(feeders, ties, mode) for mode in ("A_to_B", "B_to_A", "mixed_gross")}
    bounds = []
    for tie in ties:
        a, b = tie["from_feeder_id"], tie["to_feeder_id"]
        bounds.append({"tie_id": tie["tie_id"], "A_feeder": NAMES[a], "B_feeder": NAMES[b],
                       "A_to_B_upper_mw": min(feeders[a]["current_equivalent_active_power_mw"], feeders[b]["receiving_current_headroom_mw"]),
                       "B_to_A_upper_mw": min(feeders[b]["current_equivalent_active_power_mw"], feeders[a]["receiving_current_headroom_mw"])})
    basis_figure(); topology_figure(feeders); sharing_figure(feeders, results)
    write_review(feeders, ties, results, bounds)
    print(json.dumps({"output_dir": str(DEST), "A_to_B_mw": results["A_to_B"]["gross_mw"],
                      "B_to_A_mw": results["B_to_A"]["gross_mw"],
                      "mixed_gross_mw": results["mixed_gross"]["gross_mw"],
                      "mixed_net_A_to_B_mw": results["mixed_gross"]["net_A_to_B_mw"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
