"""增量成本的来源清单、设备事件和折现运算；不把案例价冒充通用报价。"""

import argparse
import csv
from pathlib import Path

from .city_mapping_audit import write_csv
from .cost_references import read_cost_references
from .hourly_source_profile import OUTPUT_DIR
from .official_annual import STUDY_DIR
from .transformer_only_path_2021_2025 import build_transformer_only_path


PROJECT_DIR = STUDY_DIR.parents[1]
STORAGE_SOURCES = PROJECT_DIR / "参考政策/储能成本依据/sources.csv"
LINE_BASE_10K_PER_KM = 44.543
LINE_HIGH_10K_PER_KM = 60.0
MODULE_POWER_MW = 0.1
MODULE_ENERGY_MWH = 0.215
BASE_YEAR = 2021
END_YEAR = 2041


def storage_anchors(source: Path = STORAGE_SOURCES) -> tuple[float, float]:
    with Path(source).open(encoding="utf-8-sig", newline="") as handle:
        by_id = {row["source_id"]: row for row in csv.DictReader(handle)}
    return (
        float(by_id["SZ_TENDER"]["amount_yuan"]) / 10_000,
        float(by_id["LY_AWARD"]["amount_yuan"]) / 10_000,
    )


def storage_capex_10k_cny(modules: int, source: Path = STORAGE_SOURCES) -> float:
    """仅在 1—10 柜区间做两案例插值；0 柜无新增投资。"""
    if not isinstance(modules, int) or not 0 <= modules <= 10:
        raise ValueError("储能案例插值仅支持 0—10 柜；更大规模需单独报价")
    if modules == 0:
        return 0.0
    single, ten = storage_anchors(source)
    return single + (modules - 1) * (ten - single) / 9


def storage_replicated_package_capex_10k_cny(modules: int, source: Path = STORAGE_SOURCES) -> float:
    """仿真假设：超过 10 柜时重复采购 10 柜包；不声称大站市场报价。"""
    if not isinstance(modules, int) or modules < 0:
        raise ValueError("储能柜数须为非负整数")
    packages, remainder = divmod(modules, 10)
    return packages * storage_capex_10k_cny(10, source) + storage_capex_10k_cny(remainder, source)


def line_capex_10k_cny(length_km: float, unit_cost_10k_per_km: float = LINE_BASE_10K_PER_KM) -> float:
    if length_km < 0:
        raise ValueError("规划线路长度不能为负")
    return length_km * unit_cost_10k_per_km


def discount_to_2021(amount_10k_cny: float, year: int, discount_rate: float) -> float:
    if not BASE_YEAR < year <= END_YEAR or discount_rate < 0:
        raise ValueError("现金流年份须在 2022—2041 年，折现率须非负")
    return amount_10k_cny / (1 + discount_rate) ** (year - BASE_YEAR)


def npv_10k_cny(cashflows: list[dict], discount_rate: float) -> float:
    """现金流每行须有 year 与 amount_10k_cny；调用者明确提供价格及费用科目。"""
    return sum(
        discount_to_2021(float(row["amount_10k_cny"]), int(row["year"]), discount_rate)
        for row in cashflows
    )


def lifecycle_cashflows(
    initial_capex_10k_cny: float,
    commissioning_year: int,
    life_years: int,
    fixed_om_fraction: float,
) -> list[dict]:
    """等价实价的显式假设：投运年投资、次年起运维、寿命届满且仍需服务时原价更新。"""
    if not BASE_YEAR < commissioning_year <= 2025 or life_years <= 0 or fixed_om_fraction < 0:
        raise ValueError("投运年须在 2022—2025 年，寿命与运维费率须非负且有效")
    rows = [{"year": commissioning_year, "component": "initial_capex", "amount_10k_cny": initial_capex_10k_cny}]
    renewal = commissioning_year + life_years
    while renewal < END_YEAR:
        rows.append({"year": renewal, "component": "renewal_capex", "amount_10k_cny": initial_capex_10k_cny})
        renewal += life_years
    rows.extend(
        {"year": year, "component": "fixed_om", "amount_10k_cny": initial_capex_10k_cny * fixed_om_fraction}
        for year in range(commissioning_year + 1, END_YEAR + 1)
    )
    return rows


def replacement_cost_coefficients() -> list[dict]:
    """同电压替换工程静态总投资÷新购主变额定容量；不按净增容量摊价。"""
    rows = []
    for voltage in (35, 110):
        cases = [
            case for case in read_cost_references()
            if case["voltage_kv"] == voltage and case["measure_type"] == "transformer_replacement"
        ]
        purchased = sum(case["purchased_transformer_mva"] for case in cases)
        total = sum(case["static_total_10k_cny"] for case in cases)
        case_coefficients = [
            case["static_total_10k_cny"] / case["purchased_transformer_mva"]
            for case in cases
        ]
        rows.append({
            "voltage_kv": voltage,
            "source_case_rows": ";".join(str(case["source_row"]) for case in cases),
            "case_count": len(cases),
            "purchased_transformer_mva_sum": purchased,
            "static_project_investment_10k_cny_sum": total,
            "base_coefficient_10k_cny_per_purchased_mva": round(total / purchased, 9),
            "low_case_coefficient_10k_cny_per_purchased_mva": round(min(case_coefficients), 9),
            "high_case_coefficient_10k_cny_per_purchased_mva": round(max(case_coefficients), 9),
            "basis": "local_replacement_project_static_total_per_purchased_mva",
            "applicability": (
                "35kV_cases_without_new_10kV_feeders" if voltage == 35
                else "110kV_cases_include_1_or_9_new_10kV_feeders_scope_mismatch"
            ),
            "source_file": cases[0]["source_file"],
            "source_sha256": cases[0]["source_sha256"],
        })
    return rows


def transformer_upgrade_events(station_path: list[dict]) -> list[dict]:
    """逐台记录仿真双主变规格变化；2021 起点不作为新增购置。"""
    coefficients = {row["voltage_kv"]: row for row in replacement_cost_coefficients()}
    events = []
    for row in station_path:
        if int(row["year"]) == BASE_YEAR:
            continue
        before = sorted(float(row[f"prior_unit_{i}_mva"]) for i in (1, 2))
        after = sorted(float(row[f"selected_unit_{i}_mva"]) for i in (1, 2))
        for slot, (old, new) in enumerate(zip(before, after), start=1):
            if new == old:
                continue
            if new < old:
                raise ValueError(f"主变路径出现降档：{row['model_station_id']} {row['year']} 年")
            coefficient = coefficients[int(row["voltage_kv"])]
            base = coefficient["base_coefficient_10k_cny_per_purchased_mva"]
            low = coefficient["low_case_coefficient_10k_cny_per_purchased_mva"]
            high = coefficient["high_case_coefficient_10k_cny_per_purchased_mva"]
            events.append(
                {
                    "study_region_id": row["study_region_id"],
                    "voltage_kv": int(row["voltage_kv"]),
                    "year": int(row["year"]),
                    "reverse_variant": row["reverse_variant"],
                    "model_station_id": row["model_station_id"],
                    "simulation_unit_slot": slot,
                    "old_unit_mva": old,
                    "purchased_unit_mva": new,
                    "net_capacity_increment_mva": new - old,
                    "operation": "simulated_replacement_uprating",
                    "cost_coefficient_10k_cny_per_purchased_mva": base,
                    "investment_10k_cny": round(new * base, 6),
                    "low_case_investment_10k_cny": round(new * low, 6),
                    "high_case_investment_10k_cny": round(new * high, 6),
                    "cost_source_rows": coefficient["source_case_rows"],
                    "price_status": "simulation_scaled_local_replacement_cases",
                    "technical_status": row["technical_status"],
                }
            )
    return events


def summarize_transformer_capex(events: list[dict], layers: list[dict]) -> list[dict]:
    summary = []
    for layer in layers:
        year = int(layer["year"])
        if year == BASE_YEAR:
            continue
        matching = [
            event for event in events
            if event["study_region_id"] == layer["study_region_id"]
            and event["voltage_kv"] == int(layer["voltage_kv"])
            and event["year"] == year
            and event["reverse_variant"] == layer["reverse_variant"]
        ]
        summary.append({
            "study_region_id": layer["study_region_id"],
            "voltage_kv": int(layer["voltage_kv"]),
            "year": year,
            "reverse_variant": layer["reverse_variant"],
            "upgraded_transformer_count": len(matching),
            "purchased_transformer_mva": round(sum(row["purchased_unit_mva"] for row in matching), 6),
            "net_capacity_increment_mva": round(sum(row["net_capacity_increment_mva"] for row in matching), 6),
            "base_capex_10k_cny": round(sum(row["investment_10k_cny"] for row in matching), 6),
            "low_case_capex_10k_cny": round(sum(row["low_case_investment_10k_cny"] for row in matching), 6),
            "high_case_capex_10k_cny": round(sum(row["high_case_investment_10k_cny"] for row in matching), 6),
            "cost_status": "case_scaled_transformer_only_path_not_optimum",
        })
    return summary


def cost_parameter_inventory() -> list[dict]:
    def item(key, value, unit, status, source, note):
        return {"parameter": key, "value": value, "unit": unit, "status": status, "source": source, "note": note}

    spec = "docs/REBUILD-2026-MODEL-SPEC.md"
    source_note = "参考政策/储能成本依据/来源与适用说明.md"
    single, ten = storage_anchors()
    rows = [
        item("existing_tie_incremental_capex", 0, "万元", "owner_confirmed", spec, "仅既有六条馈线、两站之间正常双向转供；开放容量另作硬约束"),
        item("new_tie_line_base_unit_cost", LINE_BASE_10K_PER_KM, "万元/km", "planning_assumption_confirmed", spec, "90% 架空、10% 电缆折算；线路长度待候选路径确定，不计开关费"),
        item("new_tie_line_high_unit_cost", LINE_HIGH_10K_PER_KM, "万元/km", "sensitivity_only", spec, "高造价敏感性，不是本地实测单价"),
        item("storage_module_power", MODULE_POWER_MW, "MW/柜", "owner_confirmed", spec, "本轮全部为新增储能"),
        item("storage_module_energy", MODULE_ENERGY_MWH, "MWh/柜", "owner_confirmed", spec, "静态场景持续时长仍需约束"),
        item("storage_one_module_cost", single, "万元/柜", "tender_ceiling_not_award", "参考政策/储能成本依据/sources.csv:SZ_TENDER", "苏州储能子项最高限价，不是实际成交价"),
        item("storage_ten_module_cost", ten, "万元/10柜", "award_different_region_and_year", "参考政策/储能成本依据/sources.csv:LY_AWARD", "浏阳 1 MW/2.15 MWh 实际中标；与单柜案例的范围/时间差需敏感性"),
        item("storage_modules_interpolation_max", 10, "柜/站", "evidence_boundary_not_site_limit", source_note, "1—10 柜仅为价格插值有效区间，不代表已证明站址可容纳 10 柜"),
        item("storage_above_10_package_rule", "10柜整包重复+余数插值", "仿真计价规则", "simulation_only_unverified_large_site", spec, "仅供超出案例规模时的静态成本筛查；不是大规模报价、站址或全寿命成本认证"),
        item("discount_rate", 0.06, "1/年", "research_base_case_with_4_8pct_sensitivity", source_note, "来源说明原为示例假设；现由本轮模型显式采用，不是甲方核定融资利率"),
        item("storage_life_years", 10, "年", "research_base_case_with_8_12yr_sensitivity", source_note, "寿命届满且仍需服务时更新，同实价现金流计入"),
        item("storage_fixed_om_rate", 0.03, "1/年", "research_base_case", source_note, "按本轮新增储能原价计固定运维"),
        item("transformer_life_years", 20, "年", "planning_assumption", spec, "研究计算寿命；不是徐州设备实测寿命或当地强制标准"),
        item("line_life_years", 20, "年", "planning_assumption", spec, "与主变统一计算口径；本轮基准解未选新线"),
        item("network_fixed_om_rate", 0.01, "1/年", "research_base_case_with_0_2pct_sensitivity", spec, "主变和新线按新增投资原价计固定运维"),
        item("planned_new_tie_route_length", 2.52, "km", "drawing_based_simulation_estimate", "data/tuomin/补充数据/pizhou.pdf", "约 42 个 60 m 等效档距；不是测绘里程"),
    ]
    for coefficient in replacement_cost_coefficients():
        rows.append(item(
            f"transformer_replacement_{coefficient['voltage_kv']}kv_per_purchased_mva",
            coefficient["base_coefficient_10k_cny_per_purchased_mva"],
            "万元/新购MVA",
            "simulation_case_scaled_coefficient",
            f"{coefficient['source_file']}:Sheet1:{coefficient['source_case_rows']}",
            f"同电压替换工程静态总投资 {coefficient['static_project_investment_10k_cny_sum']} 万元 / 新购主变 {coefficient['purchased_transformer_mva_sum']} MVA；{coefficient['applicability']}；不是本地逐站报价",
        ))
    for case in read_cost_references():
        rows.append(item(
            f"project_case_sheet1_row_{case['source_row']}",
            case["static_total_10k_cny"],
            "万元/工程",
            "source_case_not_generic_price",
            f"{case['source_file']}:Sheet1:{case['source_row']}",
            f"{case['measure_type']}；购置 {case['purchased_transformer_mva']} MVA，净增 {case['project_capacity_increment_mva']} MVA；含配套工程",
        ))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="生成新增措施成本来源和主变路径设备事件")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    station_path, layers = build_transformer_only_path()
    events = transformer_upgrade_events(station_path)
    write_csv(events, args.output_dir / "transformer_only_incremental_events_2022_2025.csv")
    write_csv(replacement_cost_coefficients(), args.output_dir / "transformer_replacement_cost_coefficients.csv")
    write_csv(summarize_transformer_capex(events, layers), args.output_dir / "transformer_only_capex_layer_2022_2025.csv")
    write_csv(cost_parameter_inventory(), args.output_dir / "cost_parameter_inventory.csv")
    print(f"已生成 {len(events)} 条逐台主变升级事件（两种反向情景分别列示），按本地替换工程折算投资；未计算措施组合最优成本。")


if __name__ == "__main__":
    main()
