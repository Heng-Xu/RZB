from __future__ import annotations

import pandas as pd
import pytest

from src.v3_voltage_cases import (
    V3VoltageCaseError,
    aggregate_separate_voltage,
    combine_local_cases,
    parent_mapping_gate,
    validate_local_case_options,
)


def test_voltage_aggregation_never_cross_sums_110_and_35_kv() -> None:
    frame = pd.DataFrame(
        {
            "region_id": ["QX-00005", "QX-00005"],
            "voltage_kv": [110, 35],
            "capacity_mva": [100.0, 30.0],
            "positive_peak_mw": [40.0, 10.0],
            "eac_wanyuan": [5.0, 2.0],
        }
    )
    result = aggregate_separate_voltage(frame, ["capacity_mva", "positive_peak_mw", "eac_wanyuan"])
    assert set(result["voltage_kv"]) == {35, 110}
    assert result.set_index("voltage_kv").loc[110, "capacity_mva"] == pytest.approx(100.0)
    assert result.set_index("voltage_kv").loc[35, "capacity_mva"] == pytest.approx(30.0)
    assert result["capacity_mva"].sum() == pytest.approx(130.0)
    assert result["cross_voltage_aggregation"] .eq(False).all()


def test_parent_mapping_gate_requires_complete_unique_parent_context() -> None:
    complete = pd.DataFrame(
        {
            "region_id": ["QX-00005", "QX-00005"],
            "station_id": ["35-A", "35-B"],
            "parent_supply_id": ["110-A", "110-B"],
            "parent_mapping_status": ["complete", "complete"],
        }
    )
    incomplete = complete.copy()
    incomplete.loc[1, "parent_supply_id"] = None
    assert parent_mapping_gate(complete) is True
    assert parent_mapping_gate(incomplete) is False


def test_local_case_sets_are_independent_and_combination_requires_explicit_compatibility() -> None:
    existing = [
        {
            "case_id": "EX-1",
            "case_type": "existing_tie_reconfiguration",
            "relief_id": "RELIEF-A",
            "from_region": "QX-00005",
            "to_region": "QX-00003",
            "transfer_mw": 10.0,
            "cost_wanyuan": 2.0,
            "approval_status": "approved",
            "dependencies": [],
        }
    ]
    new_line = [
        {
            "case_id": "NL-1",
            "case_type": "new_tie_line",
            "relief_id": "RELIEF-B",
            "from_region": "QX-00005",
            "to_region": "QX-00004",
            "transfer_mw": 6.0,
            "cost_wanyuan": 4.0,
            "approval_status": "approved",
            "dependencies": [],
        }
    ]
    assert validate_local_case_options(existing, expected_type="existing_tie_reconfiguration") is True
    assert validate_local_case_options(new_line, expected_type="new_tie_line") is True
    with pytest.raises(V3VoltageCaseError, match="explicit compatibility"):
        combine_local_cases(existing, new_line)
    combined = combine_local_cases(existing, new_line, explicit_compatibility=True)
    assert len(combined) == 2
    assert sum(float(row["transfer_mw"]) for row in combined if row["from_region"] == "QX-00005") == pytest.approx(16.0)

    duplicate = [dict(new_line[0], relief_id="RELIEF-A")]
    with pytest.raises(V3VoltageCaseError, match="duplicate"):
        combine_local_cases(existing, duplicate, explicit_compatibility=True)
