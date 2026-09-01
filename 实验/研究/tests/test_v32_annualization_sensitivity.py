from __future__ import annotations

from pathlib import Path
import hashlib
import json

import pandas as pd
import pytest

from src.v32_annualization import (
    ANNUALIZATION_FIELDS,
    apply_annualization_overrides,
    build_annualization_scenarios,
    validate_annualization_overrides,
)
from src.v32_contract import load_v32_contract


ROOT = Path(__file__).resolve().parents[1]


def test_annualization_registry_uses_only_contract_review_ranges() -> None:
    contract = load_v32_contract(ROOT)
    scenarios = build_annualization_scenarios(contract)
    assert list(scenarios) == [
        "discount_rate_low",
        "discount_rate_high",
        "storage_life_short",
        "storage_life_long",
        "transformer_life_short",
        "transformer_life_long",
        "storage_high_om_transformer_low_om",
        "storage_low_om_transformer_high_om",
        "annualization_storage_unfavorable",
        "annualization_storage_favorable",
    ]
    assert len(scenarios) == 10
    annual = contract["costs"]["annualization"]
    for overrides in scenarios.values():
        assert set(overrides) == set(ANNUALIZATION_FIELDS)
        for field in ANNUALIZATION_FIELDS:
            assert overrides[field] in annual["sensitivity"][field]


def test_annualization_override_validation_rejects_values_outside_contract_range() -> None:
    contract = load_v32_contract(ROOT)
    with pytest.raises(ValueError, match="discount_rate"):
        validate_annualization_overrides(contract, {"discount_rate": 0.03})


def test_annualization_override_isolated_copy_preserves_primary_contract() -> None:
    contract = load_v32_contract(ROOT)
    changed = apply_annualization_overrides(
        contract,
        {
            "discount_rate": 0.04,
            "storage_life_years": 8,
            "transformer_measure_life_years": 30,
            "storage_fixed_om_fraction_per_year": 0.03,
            "transformer_fixed_om_fraction_per_year": 0.018,
        },
    )
    assert changed is not contract
    assert changed["costs"]["annualization"]["discount_rate"] == 0.04
    assert contract["costs"]["annualization"]["discount_rate"] == 0.06


def test_annualization_scenario_manifest_can_reconstruct_every_input_field() -> None:
    contract = load_v32_contract(ROOT)
    scenarios = build_annualization_scenarios(contract)
    for name, parameters in scenarios.items():
        reconstructed = validate_annualization_overrides(contract, parameters)
        assert reconstructed == parameters, name


def test_packaged_annualization_evidence_has_expected_scope_and_stable_conclusions() -> None:
    root = ROOT / "results/runs/real-2021-2025-v32-annualization-sensitivity"
    manifest_path = root / "manifest.json"
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["scenario_count"] == 10
    assert manifest["region_ids"] == ["QX-00001", "QX-00005"]
    assert manifest["primary_model_unchanged"] is True
    for relative, evidence in manifest["files"].items():
        path = root / relative
        assert path.is_file(), relative
        assert evidence["bytes"] == path.stat().st_size, relative
        assert evidence["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(), relative

    summary = pd.read_csv(root / "annualization_core_summary.csv")
    assert set(summary["classification"]) == {"ROBUST"}
    assert set(summary.loc[summary["region_id"].eq("QX-00001"), "annualization_robust_lower"]) == {2.5}
    assert set(summary.loc[summary["region_id"].eq("QX-00005"), "annualization_robust_lower"]) == {2.3}
    for name, parameters in build_annualization_scenarios(load_v32_contract(ROOT)).items():
        scenario_manifest = json.loads(
            (root / name / "scenario_manifest.json").read_text(encoding="utf-8")
        )
        assert scenario_manifest["scenario_id"] == name
        assert scenario_manifest["annualization"] == parameters
