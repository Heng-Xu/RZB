from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed/real_2021_2025"


def test_processed_annual_reference_keeps_two_voltage_matrices_separate() -> None:
    reference = pd.read_csv(PROCESSED / "annual_reference.csv")
    assert len(reference) == 80
    assert set(reference["voltage_kv"]) == {35, 110}
    for voltage in (110, 35):
        frame = reference[(reference.voltage_kv == voltage) & (reference.year == 2025)]
        assert len(frame) == 8
        assert set(frame.region_id) == {
            "QX-00001", "QX-00003", "QX-00004", "QX-00005",
            "QX-00007", "QX-00008", "QX-00009", "QX-00010",
        }
        assert not frame.region_id.duplicated().any()


def test_annual_reference_contains_required_v32_evidence_fields() -> None:
    reference = pd.read_csv(PROCESSED / "annual_reference.csv")
    required = {
        "year", "region_id", "voltage_kv", "official_capacity_mva",
        "official_positive_peak_mw", "official_clr",
        "source_ref", "source_version", "transformation", "scenario_id",
        "quality_flag", "source_sha256",
    }
    assert required <= set(reference.columns)
    assert reference["region_id"].astype(str).str.fullmatch(r"QX-\d{5}").all()
    assert not reference.astype(str).apply(
        lambda column: column.str.contains("P50|P90", case=False, regex=True).any()
    ).any()


def test_v32_formal_output_is_not_backfilled_by_legacy_scheme_fields() -> None:
    contract = (ROOT / "model_contract.yaml").read_text(encoding="utf-8")
    assert 'version: "3.2.0"' in contract
    assert "SCHEME_C0" in contract  # only the explicit legacy-history declaration
    assert "2 × P2021" not in contract
