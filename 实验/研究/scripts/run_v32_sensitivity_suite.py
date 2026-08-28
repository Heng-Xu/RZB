"""运行 v3.2 实际资产基线的可复现压力/成本敏感性场景。"""
from __future__ import annotations

import argparse
from pathlib import Path

from src.v32_contract import load_v32_contract
from src.v32_sensitivity import run_v32_parameter_frontier


SCENARIOS = {
    "net_load_095": {
        "net_load_scale": 0.95,
        "storage_cost_multiplier": 1.0,
        "expansion_cost_multiplier": 1.0,
    },
    "net_load_105": {
        "net_load_scale": 1.05,
        "storage_cost_multiplier": 1.0,
        "expansion_cost_multiplier": 1.0,
    },
    "storage_cost_080": {
        "net_load_scale": 1.0,
        "storage_cost_multiplier": 0.80,
        "expansion_cost_multiplier": 1.0,
    },
    "storage_cost_120": {
        "net_load_scale": 1.0,
        "storage_cost_multiplier": 1.20,
        "expansion_cost_multiplier": 1.0,
    },
    "expansion_cost_080": {
        "net_load_scale": 1.0,
        "storage_cost_multiplier": 1.0,
        "expansion_cost_multiplier": 0.80,
    },
    "expansion_cost_120": {
        "net_load_scale": 1.0,
        "storage_cost_multiplier": 1.0,
        "expansion_cost_multiplier": 1.20,
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["all", *SCENARIOS], default="all")
    parser.add_argument(
        "--grid",
        choices=["coarse", "refined", "threshold"],
        default="coarse",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("results/runs/real-2021-2025-v32-sensitivity"),
    )
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    processed_root = project_root / "data/processed/real_2021_2025"
    contract = load_v32_contract(project_root)
    points = contract["elasticity_sweep"]["rcap_points"]
    if args.grid == "refined":
        points = [2.171, 2.172, 2.359, 2.360]
    elif args.grid == "threshold":
        points = [2.068, 2.069, 2.247, 2.248, 2.286, 2.287, 2.483, 2.484]
    names = list(SCENARIOS) if args.scenario == "all" else [args.scenario]
    for name in names:
        parameters = SCENARIOS[name]
        output_dir = args.output_root / args.grid / name
        run_v32_parameter_frontier(
            project_root,
            processed_root,
            output_dir,
            cos_phi=float(contract["technical_parameters"]["cos_phi"]["baseline"]),
            reverse_beta=float(
                contract["technical_parameters"]["reverse_beta"]["split_or_single"]
            ),
            rcap_points=points,
            include_unbounded=True,
            **parameters,
        )
        print(f"completed {name}: {output_dir}")


if __name__ == "__main__":
    main()
