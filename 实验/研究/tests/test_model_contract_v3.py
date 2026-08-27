from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]


def _contract() -> dict:
    return yaml.safe_load((ROOT / "model_contract.yaml").read_text(encoding="utf-8"))


def test_v3_contract_uses_one_2021_baseline_and_three_paths() -> None:
    contract = _contract()
    assert contract["contract"]["id"] == "xuzhou-clr-real-data-2021-2025"
    assert contract["contract"]["version"] == "3.1.0"
    assert contract["scope"]["common_baseline_year"] == 2021
    assert contract["scope"]["decision_years"] == [2022, 2023, 2024, 2025]
    assert set(contract["paths"]) == {
        "PATH_ACTUAL_2021_2025",
        "PATH_OPT_CLR_UNBOUNDED",
        "PATH_OPT_CLR_LE_2",
    }
    assert contract["paths"]["PATH_ACTUAL_2021_2025"]["eligible_for_optimization_rank"] is False


def test_v3_contract_recomputes_each_path_clr_and_prevents_storage_peak_gaming() -> None:
    metrics = _contract()["metrics"]
    assert metrics["formal_clr"]["denominator_fixed_across_paths"] is False
    assert metrics["formal_clr"]["denominator_recomputed_from_path_net_load"] is True
    assert metrics["formal_clr"]["denominator_direction"] == "positive_only"
    assert metrics["anti_gaming"]["storage_charge_may_cross_zero_to_positive"] is False
    assert metrics["anti_gaming"]["storage_discharge_may_export"] is False


def test_v3_contract_uses_cumulative_eac_and_strict_clr_from_2022() -> None:
    contract = _contract()
    objective = contract["optimization"]["objective"]
    assert objective["code"] == "MIN_CUMULATIVE_IN_SERVICE_EAC_2022_2025"
    assert objective["price_year"] == 2025
    assert objective["years"] == [2022, 2023, 2024, 2025]
    strict = contract["paths"]["PATH_OPT_CLR_LE_2"]
    assert strict["clr_limit"] == 2.0
    assert strict["constraint_start_year"] == 2022
    # 3.1.0: 严格路径起点为归一约定状态，废止跨口径 EAC 包含关系。
    normalization = strict["baseline_normalization"]
    assert normalization["applies_to_voltage_kv"] == [110]
    assert (
        normalization["formula"]
        == "S0 = min(S_2021, 2 × min(P_2021, min_decision_year_peak))"
    )
    assert normalization["side"] == "capacity_only_peaks_remain_official_src08_anchors"
    assert contract["optimization"]["invariants"] == [
        "both_formal_paths_present_for_every_region_voltage",
        "strict_path_clr_limit_applies_to_110kv_only",
    ]


def test_v3_contract_restores_elasticity_sweep_as_third_experiment() -> None:
    sweep = _contract()["elasticity_sweep"]
    assert sweep["applies_to_voltage_kv"] == [110]
    points = sweep["rcap_points"]
    assert points[0] == 1.5 and points[-1] == 3.0
    assert len(points) == 16
    assert all(abs(points[i + 1] - points[i] - 0.1) < 1e-9 for i in range(len(points) - 1))
    assert sweep["include_unbounded_point"] is True
    assert sweep["baseline"] == "same_normalized_strict_start_state"
    assert sweep["recommendation_rule"].strip() != ""


def test_v3_mapping_gate_is_annual_asset_whitelist_based() -> None:
    mapping = _contract()["data"]["timeseries"]
    assert mapping["approval_authority"] == "project_owner"
    assert mapping["grade_a_gate"] == "all_devices_in_annual_operating_whitelist_approved"
    assert mapping["operating_whitelist_2025_110kv_transformers"] == 40
    assert mapping["year_end_only_exclusions_2025"] == [
        "QX-00005|110|BDZ-00056|#1",
        "QX-00005|110|BDZ-00056|#2",
    ]


def test_v3_contract_keeps_two_independent_10kv_case_interfaces() -> None:
    cases = _contract()["local_10kv_cases"]
    assert cases["global_optimization_enabled"] is False
    assert cases["existing_tie_reconfiguration"]["cli_option"] == "--existing-tie-case-options"
    assert cases["new_tie_line"]["cli_option"] == "--new-tie-line-case-options"
    assert cases["combination_rule"] == "explicit_compatibility_and_dependencies_only"


def test_project_constraints_and_skill_reference_v3_terms() -> None:
    agents = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    skill = (PROJECT_ROOT / "skills/xuzhou-real-model/SKILL.md").read_text(encoding="utf-8")
    prompt = (PROJECT_ROOT / "NEXT-SESSION-PROMPT.md").read_text(encoding="utf-8")
    required = {
        "PATH_ACTUAL_2021_2025",
        "PATH_OPT_CLR_UNBOUNDED",
        "PATH_OPT_CLR_LE_2",
        "累计年化成本",
        "年度资产白名单",
    }
    for text in (agents, skill, prompt):
        assert required <= {term for term in required if term in text}

