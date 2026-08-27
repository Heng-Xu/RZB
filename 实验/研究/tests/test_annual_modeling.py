from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.annual_modeling import (
    ANNUAL_YEARS,
    REQUIRED_ANNUAL_FIELDS,
    build_annual_baseline,
    canonical_evidence_code,
    canonical_scheme_code,
    load_historical_reference,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "data" / "tuomin" / "电网建模数据_Agent整合版_V1.2"


def test_historical_reference_has_five_years_eight_regions_and_two_voltages() -> None:
    frame = load_historical_reference(SOURCE_ROOT / "近5年容载比.xlsx")
    assert sorted(frame["year"].unique().tolist()) == ANNUAL_YEARS
    assert frame["region_id"].nunique() == 8
    assert set(frame["voltage_kv"]) == {35, 110}
    assert len(frame) == 5 * 8 * 2
    assert (frame["capacity_mva"] > 0).all()
    assert (frame["positive_peak_base_mw"] > 0).all()


def test_scheme_and_evidence_codes_cannot_be_confused() -> None:
    assert canonical_scheme_code("C0") == "SCHEME_C0"
    assert canonical_scheme_code("A") == "SCHEME_A"
    assert canonical_scheme_code("B") == "SCHEME_B"
    assert canonical_evidence_code("A") == "EVIDENCE_A"
    assert canonical_evidence_code("B") == "EVIDENCE_B"
    assert canonical_evidence_code("C") == "EVIDENCE_C"
    assert set(canonical_scheme_code(value) for value in ("C0", "A", "B")).isdisjoint(
        {canonical_evidence_code(value) for value in ("A", "B", "C")}
    )


def test_annual_baseline_preserves_fixed_peak_and_lineage_fields() -> None:
    reference = load_historical_reference(SOURCE_ROOT / "近5年容载比.xlsx")
    current = pd.read_csv(ROOT / "results" / "runs" / "real-2025-contract-v2" / "county_baseline.csv")
    baseline = build_annual_baseline(reference, current, 2022)
    assert set(REQUIRED_ANNUAL_FIELDS) <= set(baseline.columns)
    assert len(baseline) == 16
    assert (baseline["year"] == 2022).all()
    assert baseline["asset_scope_id"].str.startswith("historical_2022").all()
    assert baseline["source_sha256"].notna().all()
    assert (baseline["capacity_mva"] / baseline["positive_peak_base_mw"] - baseline["clr_model_base"]).abs().max() < 1e-9
    assert baseline["clr_official_reference"].notna().all()


def test_final_annual_rows_require_all_action_modes() -> None:
    from src.annual_modeling import validate_annual_rows

    row = pd.DataFrame(
        [
            {"year": 2022, "region_id": "QX-00001", "voltage_kv": 110, "scheme_code": "SCHEME_C0", "evidence_grade": "EVIDENCE_C", "action_mode": "ACTION_NONE", "status": "noncompliant"},
            {"year": 2022, "region_id": "QX-00001", "voltage_kv": 110, "scheme_code": "SCHEME_A", "evidence_grade": "EVIDENCE_C", "action_mode": "ACTION_EXPANSION_ONLY", "status": "not_identifiable_or_data_gap"},
            {"year": 2022, "region_id": "QX-00001", "voltage_kv": 110, "scheme_code": "SCHEME_A", "evidence_grade": "EVIDENCE_C", "action_mode": "ACTION_STORAGE_ONLY", "status": "not_identifiable_or_data_gap"},
            {"year": 2022, "region_id": "QX-00001", "voltage_kv": 110, "scheme_code": "SCHEME_A", "evidence_grade": "EVIDENCE_C", "action_mode": "ACTION_COMBINED_EXPANSION_STORAGE", "status": "not_identifiable_or_data_gap"},
            {"year": 2022, "region_id": "QX-00001", "voltage_kv": 110, "scheme_code": "SCHEME_B", "evidence_grade": "EVIDENCE_C", "action_mode": "ACTION_EXPANSION_ONLY", "status": "not_identifiable_or_data_gap"},
            {"year": 2022, "region_id": "QX-00001", "voltage_kv": 110, "scheme_code": "SCHEME_B", "evidence_grade": "EVIDENCE_C", "action_mode": "ACTION_STORAGE_ONLY", "status": "not_identifiable_or_data_gap"},
            {"year": 2022, "region_id": "QX-00001", "voltage_kv": 110, "scheme_code": "SCHEME_B", "evidence_grade": "EVIDENCE_C", "action_mode": "ACTION_COMBINED_EXPANSION_STORAGE", "status": "not_identifiable_or_data_gap"},
        ]
    )
    assert validate_annual_rows(row) is True
