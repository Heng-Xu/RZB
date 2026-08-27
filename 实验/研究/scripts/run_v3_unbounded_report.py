"""生成基准一致的不限制路径当前结果，供研究报告快速查值。

该入口不替代正式 ``scripts/run_all.py``，也不发布严格路径成本。它用于在
严格路径全空间搜索尚未完成时，先形成事实对照与不限制路径的可审计结果。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.real_costs import (
    annualized_eac_wanyuan,
    build_real_cost_library,
    storage_capex_wanyuan,
)
from src.v3_pipeline import (
    _annual_input,
    _physical_gap_matrix,
    _retirement_candidates,
)
from src.v3_planner import PATH_OPT_UNBOUNDED, optimize_path
from src.v3_time_physics import V3TimePhysicsEvaluator

def run(output_dir: Path) -> dict[str, object]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    processed = ROOT / "data/processed/real_2021_2025"
    contract_path = ROOT / "model_contract.yaml"
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    build_real_cost_library(
        processed,
        output_dir / "cost_library",
        contract_path,
    )
    annual = _annual_input(processed)
    physical_gaps = _physical_gap_matrix(processed)
    annual = annual.merge(
        physical_gaps,
        on=["region_id", "voltage_kv"],
        how="left",
        validate="many_to_one",
    )
    annual["forward_requirement_mw"] = annual["positive_peak_mw"]
    annual["reverse_requirement_mw"] = (
        annual["capacity_mva"] * 0.95 * annual["reverse_beta"]
    )
    current_year = annual["year"].eq(2025)
    annual.loc[current_year, "forward_requirement_mw"] += annual.loc[
        current_year, "positive_capacity_gap_mw"
    ].fillna(0.0)
    annual.loc[current_year, "reverse_requirement_mw"] += annual.loc[
        current_year, "reverse_hosting_gap_mw"
    ].fillna(0.0)
    annual["measure_trigger_required"] = (
        annual["positive_capacity_gap_mw"].fillna(0.0).gt(1e-9)
        | annual["reverse_hosting_gap_mw"].fillna(0.0).gt(1e-9)
    ) & current_year

    cost_library = pd.read_csv(
        output_dir / "cost_library/expansion_cost_library.csv"
    )
    cost_library["available_year"] = 2022
    retirements = _retirement_candidates(processed, cost_library)
    candidates = pd.concat(
        [cost_library, retirements], ignore_index=True, sort=False
    )
    physics = V3TimePhysicsEvaluator(
        processed,
        output_dir / "time_physics",
        candidates,
        contract_path,
    )

    def storage_capex(modules: int) -> float:
        return storage_capex_wanyuan(modules, contract)

    def storage_eac(modules: int) -> float:
        annualization = contract["costs"]["annualization"]
        return annualized_eac_wanyuan(
            storage_capex(modules),
            float(annualization["discount_rate"]),
            int(annualization["storage_life_years"]),
            float(annualization["storage_fixed_om_fraction_per_year"]),
        )

    result = optimize_path(
        annual,
        candidates,
        path_id=PATH_OPT_UNBOUNDED,
        cos_phi=float(contract["technical_parameters"]["cos_phi"]["baseline"]),
        module_power_mw=float(contract["storage"]["module"]["power_mw"]),
        storage_capex_wanyuan_for_modules=storage_capex,
        storage_eac_wanyuan_for_modules=storage_eac,
        state_physics_evaluator=physics.evaluator(
            float(contract["technical_parameters"]["cos_phi"]["baseline"])
        ),
    )
    physics.write_selected_artifacts(
        result,
        output_dir,
        cos_phi=float(contract["technical_parameters"]["cos_phi"]["baseline"]),
    )
    result["path_year_results"].to_csv(
        output_dir / "path_year_results.csv", index=False
    )
    result["path_action_results"].to_csv(
        output_dir / "path_action_results.csv", index=False
    )
    result["path_cost_breakdown"].to_csv(
        output_dir / "path_cost_breakdown.csv", index=False
    )
    summary: dict[str, object] = {
        "status": "current_unbounded_only_not_formal_full_delivery",
        "dataset_id": "real_2021_2025",
        "capacity_state": "2021_common_baseline_plus_selected_actions",
        "strict_path_included": False,
        "formal_entry_still_required": True,
    }
    (output_dir / "README.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False))


if __name__ == "__main__":
    main()
