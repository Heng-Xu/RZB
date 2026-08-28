from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict:
    return yaml.safe_load((ROOT / "model_contract.yaml").read_text(encoding="utf-8"))


def test_real_contract_is_v3_and_covers_eight_anonymized_regions() -> None:
    contract = _contract()
    assert contract["contract"]["version"] == "3.2.0"
    assert contract["scope"]["common_baseline_year"] == 2021
    assert contract["scope"]["decision_years"] == [2022, 2023, 2024, 2025]
    assert len(contract["scope"]["regions"]) == 8
    assert all(region.startswith("QX-") for region in contract["scope"]["regions"])


def test_real_contract_separates_voltage_and_blocks_unapproved_global_actions() -> None:
    contract = _contract()
    assert contract["cross_voltage"]["separate_matrices"] is True
    assert contract["cross_voltage"]["aggregate_35_and_110"] is False
    assert contract["local_10kv_cases"]["global_optimization_enabled"] is False
    assert contract["pv"]["curtailment"]["active_decision"] is False
    assert contract["metrics"]["formal_clr"]["denominator_direction"] == "positive_only"
    assert contract["metrics"]["formal_clr"]["denominator_fixed_across_paths"] is False


def test_real_contract_keeps_official_2025_rows_as_reference_anchors() -> None:
    rows = _contract()["official_2025_reference"]["rows"]
    assert len(rows) == 16
    rows_110 = [row for row in rows if row["voltage_kv"] == 110]
    rows_35 = [row for row in rows if row["voltage_kv"] == 35]
    assert len(rows_110) == 8
    assert len(rows_35) == 8
    regions = set(_contract()["scope"]["regions"])
    assert {row["region_id"] for row in rows_110} == regions
    assert {row["region_id"] for row in rows_35} == regions
    assert all(row["clr"] > 2.0 for row in rows_110)


def test_contract_referenced_sources_exist() -> None:
    contract = _contract()
    relative_paths = [
        contract["contract"]["authoritative_spec"],
        contract["contract"]["execution_plan"],
        contract["data"]["source_contract"],
        contract["data"]["archive"]["file"],
        contract["costs"]["storage_capex"]["source_note"],
    ]
    assert all((ROOT / path).resolve().is_file() for path in relative_paths)
    assert contract["environment"]["command_working_directory"] == "实验/研究"


def test_strict_path_starts_in_2022_without_changing_2021_baseline() -> None:
    contract = _contract()
    strict = contract["paths"]["PATH_OPT_CLR_LE_2"]
    assert strict["common_baseline_year"] == 2021
    assert strict["rcap"] == 2.0
    assert strict["constraint_start_year"] == 2022
    assert contract["planning_baseline"]["formula"] == "S0 = actual_2021_installed_capacity"
    assert strict["legacy_capacity_grandfathered"] is True
    assert strict["forced_retirement_for_rcap_compliance"] is False
    assert contract["optimization"]["objective"]["includes_2021_existing_assets"] is False


def test_storage_cost_anchors_and_block_rule() -> None:
    storage = _contract()["costs"]["storage_capex"]
    assert 6.8382 + 20.3618 == 27.2
    assert abs(6.8382 + 20.3618 * 10 - storage["block_cost_wanyuan"]) < 1e-3
    assert storage["direct_linear_extrapolation_above_10_allowed"] is False
    assert storage["sensitivity_yuan_per_wh"] == [0.9789, 1.2651]


def test_legacy_params_are_not_authoritative() -> None:
    legacy = yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))["legacy_notice"]
    assert legacy["status"] == "deprecated_for_real_data"
    assert legacy["authoritative_contract"] == "model_contract.yaml"
    assert legacy["allowed_use"] == "synthetic_m1_regression_only"


def test_active_documents_have_no_skill_template_placeholders() -> None:
    project_root = ROOT.parents[1]
    active = [
        project_root / "AGENTS.md",
        project_root / "NEXT-SESSION-PROMPT.md",
        project_root / "skills/xuzhou-real-model/SKILL.md",
        ROOT / "README.md",
        ROOT / "docs/REAL-DATA-MODEL-SPEC.md",
        ROOT / "docs/EXECUTION-PLAN.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in active)
    assert "[TODO" not in text
    assert "TODO:" not in text
