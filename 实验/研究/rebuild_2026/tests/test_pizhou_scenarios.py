from pathlib import Path

import pytest

from rebuild_2026.pizhou_scenarios import build_provisional_scenarios


STUDY_DIR = Path(__file__).resolve().parents[2]
AUDIT_DIR = Path(__file__).resolve().parents[1] / "source_audit"


def test_synchronized_2025_scenarios_keep_voltage_layers_separate():
    rows = build_provisional_scenarios(
        STUDY_DIR / "data/tuomin/电网建模数据_Agent整合版_V1.2/邳州主变负载率.xlsx",
        AUDIT_DIR / "pizhou_2025_mapping_candidates.csv",
        AUDIT_DIR / "official_annual.csv",
    )
    assert len(rows) == 2
    by_voltage = {r["voltage_kv"]: r for r in rows}
    assert by_voltage[110]["valid_hours"] == 8759
    assert by_voltage[35]["valid_hours"] == 8759
    assert by_voltage[110]["forward_peak_mw"] == pytest.approx(951.66)
    assert by_voltage[35]["forward_peak_mw"] == pytest.approx(147.57)
    assert by_voltage[110]["reverse_peak_mw"] == pytest.approx(395.24)
    assert by_voltage[35]["reverse_peak_mw"] == pytest.approx(115.28)
    assert by_voltage[110]["forward_h95_observed"] == 7
    assert by_voltage[35]["forward_h95_observed"] == 4
    assert by_voltage[110]["reverse_h95_observed"] == 8
    assert by_voltage[35]["reverse_h95_observed"] == 10
    assert by_voltage[110]["excluded_sparse_station"] == "BDZ-00056"
    assert by_voltage[110]["missing_hour"] == "2025-03-09 02:00:00"
    assert by_voltage[110]["missing_hour_linear_estimate_mw"] == pytest.approx(304.08)
    assert by_voltage[35]["missing_hour_linear_estimate_mw"] == pytest.approx(46.82)
    assert all(not row["linear_fill_changes_peak"] for row in rows)
    assert all(not row["linear_fill_changes_h95"] for row in rows)
    assert {r["scenario_status"] for r in rows} == {"provisional"}
