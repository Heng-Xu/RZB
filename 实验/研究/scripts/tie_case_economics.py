#!/usr/bin/env python3
"""10 kV 联络局部案例经济比选：新建联络 vs 储能 vs 主变扩容。

定位：局部案例范围的措施比选，不进入主体优化目标（AGENTS.md §5）。
数据基线：10kV_AgentReady_V5_2 包内已有数据（负责人 2026-08-26 确认不再收资）——
新建联络的转供能力按与既有联络相同的"三重约束取最先绑定"扫描计算，
送侧可转负荷取 S1 边界功率（最近一次 run_tie_case 产物），受端站备用取包内
station_boundary_2025.csv，线路能力取 JKLYJ/Q-10-240 基准。
单位公里造价为行业典型值（包内无 10 kV 单价，SRC11 仅 110 kV 案例），
按负责人 2026-08-26 确认作为既定假设使用，敏感性 ±30%×长度 ±20% 已覆盖。

用法：
    conda run -n xuzhou110kv_clr python scripts/tie_case_economics.py \
        [--output output/tie_case] [--case-root data/tuomin/10kv_case]
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from src.real_costs import storage_capex_wanyuan  # noqa: E402

COS_PHI = 0.95
STEP_MW = 0.25  # 与 tie_case.engine.tie_transfer_scan 一致
LINE_MVA = 9.5263  # JKLYJ/Q-10-240 能力基准（TIE-002 主干同型式）
NEW_TIE = {
    "length_km": 2.5,
    "unit_cost_wanyuan_per_km": 60.0,
    "cost_sensitivity": 0.30,
    "length_sensitivity": 0.20,
    # 走径：PZXL-00099 主干末端 ↔ PZXL-00154 主干中段（V5_2 结构化拓扑）
    "from_feeder": "PZXL-00099",
    "to_feeder": "PZXL-00154",
    "from_station": "BDZ-00027",
    "to_station": "BDZ-00048",
}
STORAGE_MODULE_COUNT = 10
TRANSFORMER = {
    "capex_low_wanyuan": 1170.0,
    "capex_center_wanyuan": 1343.0,
    "capex_high_wanyuan": 1516.0,
    "capacity_mva": 50.0,
}


def _latest_boundary_loads(tie_output: Path) -> dict[str, float]:
    """从最近一次 run_tie_case 产物读取六馈线 S1 边界功率。"""

    run_dirs = sorted(p for p in tie_output.iterdir() if p.is_dir() and p.name[:8].isdigit())
    if not run_dirs:
        raise SystemExit(f"no tie_case run outputs under {tie_output}")
    case_csv = run_dirs[-1] / "case_results.csv"
    loads: dict[str, float] = {}
    with case_csv.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            note = row.get("notes", "")
            if row.get("scenario_id") == "S1_FEEDER_STRESS" and "boundary_P=" in note:
                feeder = note.split("boundary_P=")[0].strip(". ")
                loads[feeder] = float(note.split("boundary_P=")[1].split("MW")[0])
    if not loads:
        raise SystemExit(f"no S1 boundary loads found in {case_csv}")
    return loads


def _station_spare(case_root: Path, station_id: str) -> float:
    with (case_root / "data" / "station_boundary_2025.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            if row["station_id"] == station_id:
                return float(row["normal_spare_at_annual_max_mva"])
    raise SystemExit(f"station {station_id} not in station_boundary_2025.csv")


def transfer_scan(line_mw: float, sending_load_mw: float, host_spare_mva: float) -> tuple[float, str]:
    """与 tie_case.engine.tie_transfer_scan 相同的三重约束扫描。"""

    transferred = 0.0
    binding = "sending_feeder_load_exhausted"
    steps = int(max(line_mw, sending_load_mw, host_spare_mva) / STEP_MW)
    for step in range(1, steps + 1):
        candidate = round(step * STEP_MW, 4)
        if candidate > sending_load_mw:
            return transferred, f"sending_feeder_load_exhausted({sending_load_mw:.2f}MW)"
        if candidate > host_spare_mva:
            return transferred, f"host_station_spare({host_spare_mva:.2f}MVA)"
        if candidate >= line_mw:
            return transferred, f"path_thermal_limit({line_mw:.2f}MW)"
        transferred = candidate
    return transferred, binding


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", default=str(HERE / "output" / "tie_case"))
    parser.add_argument("--case-root", default=str(HERE / "data" / "tuomin" / "10kv_case"))
    parser.add_argument("--contract", default=str(HERE / "model_contract.yaml"))
    args = parser.parse_args()

    contract = yaml.safe_load(Path(args.contract).read_text(encoding="utf-8"))
    if str(contract["contract"]["version"]) not in {"3.1.0", "3.2.0"}:
        raise SystemExit("requires model contract 3.1.0 or 3.2.0")
    module_power = float(contract["storage"]["module"]["power_mw"])
    case_root = Path(args.case_root)
    tie_output = Path(args.output)

    line_mw = LINE_MVA * COS_PHI
    loads = _latest_boundary_loads(tie_output)
    send_from = loads[NEW_TIE["from_feeder"]]
    send_to = loads[NEW_TIE["to_feeder"]]
    spare_to = _station_spare(case_root, NEW_TIE["to_station"])
    spare_from = _station_spare(case_root, NEW_TIE["from_station"])
    cap_from_to, bind_from_to = transfer_scan(line_mw, send_from, spare_to)
    cap_to_from, bind_to_from = transfer_scan(line_mw, send_to, spare_from)
    capability_mw = min(cap_from_to, cap_to_from)  # 保守取较弱方向

    center_capex = NEW_TIE["length_km"] * NEW_TIE["unit_cost_wanyuan_per_km"]
    low_capex = (
        NEW_TIE["length_km"] * (1 - NEW_TIE["length_sensitivity"])
        * NEW_TIE["unit_cost_wanyuan_per_km"] * (1 - NEW_TIE["cost_sensitivity"])
    )
    high_capex = (
        NEW_TIE["length_km"] * (1 + NEW_TIE["length_sensitivity"])
        * NEW_TIE["unit_cost_wanyuan_per_km"] * (1 + NEW_TIE["cost_sensitivity"])
    )

    storage_single = storage_capex_wanyuan(1, contract)
    storage_batch = storage_capex_wanyuan(STORAGE_MODULE_COUNT, contract)
    storage_batch_mw = STORAGE_MODULE_COUNT * module_power
    transformer_mw = TRANSFORMER["capacity_mva"] * COS_PHI

    def per_mw(capex: float, mw: float) -> float:
        return round(capex / mw, 1)

    rows = [
        {
            "measure": "新建10kV联络（NEW-TIE-01）",
            "capability_mw": round(capability_mw, 3),
            "capability_kind": (
                f"站间转供：正向 {cap_from_to:.2f} MW（绑定 {bind_from_to}），"
                f"反向 {cap_to_from:.2f} MW（绑定 {bind_to_from}，河东线边界为代理值）；取较弱方向"
            ),
            "capex_low_wanyuan": round(low_capex, 1),
            "capex_center_wanyuan": round(center_capex, 1),
            "capex_high_wanyuan": round(high_capex, 1),
            "capex_per_mw_low": per_mw(low_capex, capability_mw),
            "capex_per_mw_center": per_mw(center_capex, capability_mw),
            "capex_per_mw_high": per_mw(high_capex, capability_mw),
            "cost_basis": "60万元/km行业典型值（±30%）×长度2.5km（±20%）；负责人2026-08-26确认按已有数据定稿",
            "quality_flag": "model_assumption_confirmed_owner_2026_08_26",
        },
        {
            "measure": "储能一体化柜（单柜）",
            "capability_mw": module_power,
            "capability_kind": "本地反向吸收＋正向支撑（含能量时移，0.215MWh/柜）",
            "capex_low_wanyuan": round(storage_single, 3),
            "capex_center_wanyuan": round(storage_single, 3),
            "capex_high_wanyuan": round(storage_single, 3),
            "capex_per_mw_low": per_mw(storage_single, module_power),
            "capex_per_mw_center": per_mw(storage_single, module_power),
            "capex_per_mw_high": per_mw(storage_single, module_power),
            "cost_basis": "苏州单套最高限价27.2万元（招标公告）",
            "quality_flag": "source_backed",
        },
        {
            "measure": "储能一体化柜（十柜批量）",
            "capability_mw": round(storage_batch_mw, 2),
            "capability_kind": "同上，批量采购水平",
            "capex_low_wanyuan": round(storage_batch, 3),
            "capex_center_wanyuan": round(storage_batch, 3),
            "capex_high_wanyuan": round(storage_batch, 3),
            "capex_per_mw_low": per_mw(storage_batch, storage_batch_mw),
            "capex_per_mw_center": per_mw(storage_batch, storage_batch_mw),
            "capex_per_mw_high": per_mw(storage_batch, storage_batch_mw),
            "cost_basis": "浏阳1MW/2.2MWh中标价210.456万元",
            "quality_flag": "source_backed",
        },
        {
            "measure": "50 MVA第三台主变",
            "capability_mw": round(transformer_mw, 2),
            "capability_kind": "新增正向供电容量（不治理反向）",
            "capex_low_wanyuan": TRANSFORMER["capex_low_wanyuan"],
            "capex_center_wanyuan": TRANSFORMER["capex_center_wanyuan"],
            "capex_high_wanyuan": TRANSFORMER["capex_high_wanyuan"],
            "capex_per_mw_low": per_mw(TRANSFORMER["capex_low_wanyuan"], transformer_mw),
            "capex_per_mw_center": per_mw(TRANSFORMER["capex_center_wanyuan"], transformer_mw),
            "capex_per_mw_high": per_mw(TRANSFORMER["capex_high_wanyuan"], transformer_mw),
            "cost_basis": "徐州同类型工程区间（SRC10+SRC03，74个候选点）",
            "quality_flag": "source_backed",
        },
    ]

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = tie_output / f"economics-{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "local_case_measure_comparison.csv"
    with out_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("== 局部案例措施比选（每 MW 能力投资，万元/MW）==")
    for row in rows:
        print(
            f"{row['measure']}: 中心 {row['capex_per_mw_center']}"
            f"（区间 {row['capex_per_mw_low']}~{row['capex_per_mw_high']}，"
            f"能力 {row['capability_mw']} MW）"
        )
    print(f"新建联络能力明细：{rows[0]['capability_kind']}")
    storage_per_mw = storage_batch / storage_batch_mw
    tie_per_mw = center_capex / capability_mw
    print(
        f"新建联络每 MW 转供能力投资约为储能批量价的 1/{storage_per_mw / tie_per_mw:.1f}"
        "；前提：受端有可转入负荷，联络转移负荷、储能就地吸收，维度不同"
    )
    print("WROTE:", out_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
