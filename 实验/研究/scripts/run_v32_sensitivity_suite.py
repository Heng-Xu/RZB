"""运行 v3.2 实际资产基线的可复现压力/成本敏感性场景。

``--scenario all`` 的默认语义是全部 17 个正式参数场景；需要限定场景族
时必须显式给出 ``--family``。
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from src.v32_contract import load_v32_contract
from src.v32_sensitivity import run_v32_parameter_frontier


BASELINE_PARAMETERS = {
    "cos_phi": 0.95,
    "reverse_beta": 0.80,
    "net_load_scale": 1.0,
    "storage_cost_multiplier": 1.0,
    "expansion_cost_multiplier": 1.0,
}
BASELINE_CONTROL_SCENARIO_ID = "pf095_beta080"

PHYSICAL_SCENARIOS = {
    "pf090_beta080": {**BASELINE_PARAMETERS, "cos_phi": 0.90},
    "pf095_beta060": {**BASELINE_PARAMETERS, "reverse_beta": 0.60},
    "pf095_beta080": dict(BASELINE_PARAMETERS),
    "pf095_beta100": {**BASELINE_PARAMETERS, "reverse_beta": 1.00},
    "pf100_beta080": {**BASELINE_PARAMETERS, "cos_phi": 1.00},
}

ONE_FACTOR_SCENARIOS = {
    "net_load_095": {
        **BASELINE_PARAMETERS,
        "net_load_scale": 0.95,
    },
    "net_load_105": {
        **BASELINE_PARAMETERS,
        "net_load_scale": 1.05,
    },
    "storage_cost_080": {
        **BASELINE_PARAMETERS,
        "storage_cost_multiplier": 0.80,
    },
    "storage_cost_120": {
        **BASELINE_PARAMETERS,
        "storage_cost_multiplier": 1.20,
    },
    "expansion_cost_080": {
        **BASELINE_PARAMETERS,
        "expansion_cost_multiplier": 0.80,
    },
    "expansion_cost_120": {
        **BASELINE_PARAMETERS,
        "expansion_cost_multiplier": 1.20,
    },
}

# 六个有明确判别目的的角点，不展开全笛卡尔积，也不引入证据不足的纯光伏变化。
INTERACTION_SCENARIOS = {
    "high_load_high_storage": {
        **BASELINE_PARAMETERS,
        "net_load_scale": 1.05,
        "storage_cost_multiplier": 1.20,
    },
    "high_load_low_expansion": {
        **BASELINE_PARAMETERS,
        "net_load_scale": 1.05,
        "expansion_cost_multiplier": 0.80,
    },
    "high_load_high_expansion": {
        **BASELINE_PARAMETERS,
        "net_load_scale": 1.05,
        "expansion_cost_multiplier": 1.20,
    },
    "low_beta_high_load": {
        **BASELINE_PARAMETERS,
        "reverse_beta": 0.60,
        "net_load_scale": 1.05,
    },
    "high_storage_low_expansion": {
        **BASELINE_PARAMETERS,
        "storage_cost_multiplier": 1.20,
        "expansion_cost_multiplier": 0.80,
    },
    "low_storage_high_expansion": {
        **BASELINE_PARAMETERS,
        "storage_cost_multiplier": 0.80,
        "expansion_cost_multiplier": 1.20,
    },
}

FORMAL_SCENARIOS = {
    **PHYSICAL_SCENARIOS,
    **ONE_FACTOR_SCENARIOS,
    **INTERACTION_SCENARIOS,
}

SCENARIO_FAMILIES = {
    "physical": PHYSICAL_SCENARIOS,
    "one-factor": ONE_FACTOR_SCENARIOS,
    "interaction": INTERACTION_SCENARIOS,
    "formal": FORMAL_SCENARIOS,
}


def select_scenario_names(
    scenario: str,
    *,
    family: str = "formal",
) -> list[str]:
    if scenario == "all":
        if family not in SCENARIO_FAMILIES:
            raise ValueError(f"unknown scenario family: {family}")
        return list(SCENARIO_FAMILIES[family])
    if scenario not in FORMAL_SCENARIOS:
        raise ValueError(f"unknown formal scenario: {scenario}")
    return [scenario]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run all formal v3.2 parameter scenarios unless --family is explicitly narrowed."
    )
    parser.add_argument("--scenario", choices=["all", *FORMAL_SCENARIOS], default="all")
    parser.add_argument(
        "--family",
        choices=list(SCENARIO_FAMILIES),
        default="formal",
        help="family used only when --scenario=all; default: formal (17 scenarios)",
    )
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
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    project_root = Path(__file__).resolve().parents[1]
    processed_root = project_root / "data/processed/real_2021_2025"
    contract = load_v32_contract(project_root)
    points = contract["elasticity_sweep"]["rcap_points"]
    if args.grid == "refined":
        points = [2.171, 2.172, 2.359, 2.360]
    elif args.grid == "threshold":
        points = [2.068, 2.069, 2.247, 2.248, 2.286, 2.287, 2.483, 2.484]
    names = select_scenario_names(args.scenario, family=args.family)
    for name in names:
        parameters = FORMAL_SCENARIOS[name]
        output_dir = args.output_root / args.grid / name
        run_v32_parameter_frontier(
            project_root,
            processed_root,
            output_dir,
            rcap_points=points,
            include_unbounded=True,
            scenario_name=name,
            **parameters,
        )
        print(f"completed {name}: {output_dir}")


if __name__ == "__main__":
    main()
