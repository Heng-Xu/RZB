from __future__ import annotations

import math
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_authoritative_files_exist() -> None:
    required = [
        PROJECT_ROOT / "AGENTS.md",
        PROJECT_ROOT / "NEXT-SESSION-PROMPT.md",
        PROJECT_ROOT / "skills/xuzhou-real-model/SKILL.md",
        ROOT / "docs/REAL-DATA-MODEL-SPEC.md",
        ROOT / "docs/IMPLEMENTATION-PLAN-REAL-2021-2025-V3.md",
        ROOT / "docs/PROJECT-OUTPUT-CONVENTIONS.md",
        ROOT / "docs/ANNUAL-2021-2025-RUNBOOK.md",
        ROOT / "model_contract.yaml",
    ]
    assert all(path.is_file() for path in required)


def test_contract_scope_and_reference_rows() -> None:
    contract = _load(ROOT / "model_contract.yaml")
    assert contract["contract"]["version"] == "3.2.0"
    assert contract["scope"]["common_baseline_year"] == 2021
    assert contract["scope"]["decision_years"] == [2022, 2023, 2024, 2025]

    rows = contract["official_2025_reference"]["rows"]
    assert len(rows) == 16
    rows_110 = [row for row in rows if row["voltage_kv"] == 110]
    rows_35 = [row for row in rows if row["voltage_kv"] == 35]
    assert len(rows_110) == 8
    assert len(rows_35) == 8
    regions = set(contract["scope"]["regions"])
    assert {row["region_id"] for row in rows_110} == regions
    assert {row["region_id"] for row in rows_35} == regions
    for row in rows:
        calculated = row["capacity_mva"] / row["peak_mw"]
        assert math.isclose(calculated, row["clr"], abs_tol=0.015)


def test_contract_referenced_sources_exist() -> None:
    contract = _load(ROOT / "model_contract.yaml")
    relative_paths = [
        contract["contract"]["authoritative_spec"],
        contract["contract"]["execution_plan"],
        contract["data"]["source_contract"],
        contract["data"]["archive"]["file"],
        contract["costs"]["storage_capex"]["source_note"],
    ]
    assert all((ROOT / path).resolve().is_file() for path in relative_paths)
    assert contract["environment"]["command_working_directory"] == "实验/研究"


def test_strict_path_and_path_cost_invariant_are_machine_readable() -> None:
    contract = _load(ROOT / "model_contract.yaml")
    strict = contract["paths"]["PATH_OPT_CLR_LE_2"]
    assert strict["rcap"] == 2.0
    assert strict["constraint_start_year"] == 2022
    assert contract["planning_baseline"]["formula"] == "S0 = actual_2021_installed_capacity"
    assert strict["legacy_capacity_grandfathered"] is True
    assert strict["forced_retirement_for_rcap_compliance"] is False
    assert "both_formal_paths_present_for_every_region_voltage" in contract["optimization"]["invariants"]
    assert "elastic_cost_not_greater_than_rigid_cost_when_both_feasible" in contract["optimization"]["invariants"]
    sweep = contract["elasticity_sweep"]
    assert sweep["applies_to_voltage_kv"] == [110]
    assert sweep["include_unbounded_point"] is True


def test_scenario_and_metric_hard_rules() -> None:
    contract = _load(ROOT / "model_contract.yaml")
    metrics = contract["metrics"]["formal_clr"]
    assert metrics["denominator_direction"] == "positive_only"
    assert metrics["denominator_fixed_across_paths"] is False
    assert metrics["denominator_recomputed_from_path_net_load"] is True
    assert contract["metrics"]["anti_gaming"]["storage_charge_may_cross_zero_to_positive"] is False
    assert contract["metrics"]["anti_gaming"]["storage_discharge_may_export"] is False
    assert contract["outputs"]["n_minus_1_visible_row_allowed"] is False
    assert contract["cross_voltage"]["aggregate_35_and_110"] is False


def test_storage_cost_anchors_and_block_rule() -> None:
    storage = _load(ROOT / "model_contract.yaml")["costs"]["storage_capex"]
    c1 = 6.8382 + 20.3618
    c10 = 6.8382 + 20.3618 * 10
    assert math.isclose(c1, 27.2, abs_tol=1e-9)
    assert math.isclose(c10, storage["block_cost_wanyuan"], abs_tol=1e-3)
    assert storage["direct_linear_extrapolation_above_10_allowed"] is False
    assert storage["sensitivity_yuan_per_wh"] == [0.9789, 1.2651]


def test_active_documents_have_no_skill_template_placeholders() -> None:
    active = [
        PROJECT_ROOT / "AGENTS.md",
        PROJECT_ROOT / "NEXT-SESSION-PROMPT.md",
        PROJECT_ROOT / "skills/xuzhou-real-model/SKILL.md",
        ROOT / "README.md",
        ROOT / "docs/REAL-DATA-MODEL-SPEC.md",
        ROOT / "docs/EXECUTION-PLAN.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in active)
    assert "[TODO" not in text
    assert "TODO:" not in text
