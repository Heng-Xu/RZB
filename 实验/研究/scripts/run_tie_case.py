#!/usr/bin/env python3
"""10 kV 联络独立案例分析入口（两站范围：墩集 BDZ-00027 / 河湾 BDZ-00048）。

执行 S1 正向应力、S2 高 PV 反送、S3 转供扫描与既定敏感性，
按包模板 case_results_template.csv 输出结果与 Markdown 结论。
用法：
  conda run -n xuzhou110kv_clr python scripts/run_tie_case.py \
      --case-root data/tuomin/10kv_case --output output/tie_case [--ties TIE-002]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.tie_case.engine import (  # noqa: E402
    V_HARD,
    TieCaseError,
    load_case,
    scenario_s1_forward,
    tie_transfer_scan,
)

RESULT_COLUMNS = [
    "run_id", "scenario_id", "tie_id", "direction", "transfer_mw",
    "served_load_mw", "unserved_mw", "umin_pu", "max_loading_pct",
    "binding_constraint", "sectionalizing_switches", "tie_state",
    "formal_or_debug", "parameter_gate_pass", "notes",
]

PF_SENSITIVITY = (0.90, 0.95, 0.98)
PV_FACTORS_S2 = (0.8, 0.9, 1.0)
LOAD_FACTORS_S2 = (0.3, 0.5, 0.7)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    here = Path(__file__).resolve().parents[1]
    parser.add_argument("--case-root", default=str(here / "data" / "tuomin" / "10kv_case"))
    parser.add_argument("--output", default=str(here / "output" / "tie_case"))
    parser.add_argument("--ties", default="TIE-002", help="逗号分隔，如 TIE-002,TIE-003")
    args = parser.parse_args()

    try:
        case = load_case(Path(args.case_root))
    except TieCaseError as exc:
        print(f"[tie-case] 门禁拒绝: {exc}", file=sys.stderr)
        return 2

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.output) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    feeder_rows: list[dict] = []

    # S1 正向应力包络（拓扑碎片化馈线如实降级：负荷 seed 源端可达率不足时
    # 电压/负载结果仅代表可达分量，门禁记 False 并注明覆盖率）
    for feeder_id in case.feeder_ids:
        result = scenario_s1_forward(case, feeder_id)
        feeder_rows.append({"run_id": run_id, "scenario_id": "S1_FEEDER_STRESS", **result})
        proxy_note = " hdong P=proxy_i_pf095(√3×10kV×I×0.95)" if result["proxy_i_pf095"] else ""
        frag_note = (
            f" topology_fragmented(load_coverage={result['load_coverage_pct']}%)"
            if result["topology_fragmented"] else ""
        )
        gate = result["voltage_pass_hard"] and not result["topology_fragmented"]
        binding = ""
        if not result["voltage_pass_hard"]:
            binding = "VOLTAGE"
        if result["topology_fragmented"]:
            binding = "TOPOLOGY_FRAGMENTED" if not binding else f"{binding}+TOPOLOGY_FRAGMENTED"
        rows.append({
            "run_id": run_id, "scenario_id": "S1_FEEDER_STRESS", "tie_id": "-",
            "direction": "-", "transfer_mw": "", "served_load_mw": result["served_load_mw"],
            "unserved_mw": result["unserved_mw"], "umin_pu": result["umin_pu"],
            "max_loading_pct": result["max_loading_pct"],
            "binding_constraint": binding,
            "sectionalizing_switches": "", "tie_state": "-",
            "formal_or_debug": "PLANNING_ENVELOPE", "parameter_gate_pass": gate,
            "notes": f"{feeder_id} boundary_P={result['boundary_p_mw']}MW.{proxy_note}{frag_note}",
        })

    # S2 高 PV 反送（负荷降载在仿真内生效；最劣组合按电压偏差含 umax 过电压）
    for feeder_id in case.feeder_ids:
        worst = None
        worst_score = None
        for load_factor in LOAD_FACTORS_S2:
            for pv_factor in PV_FACTORS_S2:
                scaled = scenario_s1_forward(case, feeder_id, pv_factor=pv_factor, load_factor=load_factor)
                score = max(
                    scaled["umax_pu"] - V_HARD[1],
                    V_HARD[0] - scaled["umin_pu"],
                    scaled["umax_pu"] - 1.0,
                    1.0 - scaled["umin_pu"],
                    0.0,
                )
                if worst_score is None or score > worst_score:
                    worst_score = score
                    worst = {**scaled, "load_factor": load_factor, "pv_factor": pv_factor}
        feeder_rows.append({"run_id": run_id, "scenario_id": f"S2_REVERSE_PV(lf={worst['load_factor']},pv={worst['pv_factor']})", **worst})

    # S3 转供扫描（双向）
    tie_ids = [item.strip() for item in args.ties.split(",") if item.strip()]
    for tie_id in tie_ids:
        for direction in ("from_to", "to_from"):
            scan = tie_transfer_scan(case, tie_id, direction=direction)
            state = case.confirmed_ties.get(tie_id, "OPEN")
            rows.append({
                "run_id": run_id, "scenario_id": "S3_TRANSFER_SWEEP", "tie_id": tie_id,
                "direction": direction, **{k: scan[k] for k in (
                    "transfer_mw", "served_load_mw", "unserved_mw")},
                "umin_pu": "", "max_loading_pct": "",
                "binding_constraint": scan["binding_constraint"],
                "sectionalizing_switches": f"{tie_id} CLOSED; 分段开关序列待拓扑闭环后细化",
                "tie_state": f"normal={state}; operation=CLOSE_FOR_TRANSFER",
                "formal_or_debug": scan["formal_or_debug"],
                "parameter_gate_pass": scan["parameter_gate_pass"],
                "notes": f"host_spare={scan['host_station_spare_mva']}MVA path_min={scan['path_thermal_min_mva']}MVA"
                         + (" proxy_i_pf095" if scan["proxy_i_pf095"] else ""),
            })

    results = out_dir / "case_results.csv"
    pd.DataFrame(rows, columns=RESULT_COLUMNS).to_csv(results, index=False, encoding="utf-8-sig")
    pd.DataFrame(feeder_rows).to_csv(out_dir / "feeder_stress_results.csv", index=False, encoding="utf-8-sig")

    summary = {
        "run_id": run_id,
        "case_root": str(args.case_root),
        "ties": tie_ids,
        "qa_gates": "11 项 final_preflight_qa 已在 load_case 强制校验",
        "outputs": [results.name, "feeder_stress_results.csv"],
        "口径": "规划包络场景；六馈线年度极值非同步断面；河东线引用带 proxy_i_pf095 标记",
    }
    (out_dir / "run_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[tie-case] 完成：{results}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
