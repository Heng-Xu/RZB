from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.real_metrics import (
    V3_FORMAL_PATHS,
    V3MetricError,
    compute_path_metrics,
    path_net_load,
    reverse_beta,
    validate_storage_dispatch,
)


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed/real_2021_2025"


def test_real_metrics_exposes_only_the_three_v3_formal_paths() -> None:
    assert V3_FORMAL_PATHS == (
        "PATH_ACTUAL_2021_2025",
        "PATH_OPT_CLR_UNBOUNDED",
        "PATH_OPT_CLR_LE_2",
    )


def test_storage_red_lines_and_path_formula_are_enforced() -> None:
    actual = pd.Series([-0.4, 1.0], index=["reverse", "forward"])
    charge = pd.Series([0.3, 0.0], index=actual.index)
    discharge = pd.Series([0.0, 0.5], index=actual.index)
    validate_storage_dispatch(actual, charge, discharge)
    assert path_net_load(actual, charge, discharge).tolist() == pytest.approx([-0.1, 0.5])
    with pytest.raises(V3MetricError, match="cross zero"):
        validate_storage_dispatch(actual, pd.Series([0.5, 0.0], index=actual.index))
    with pytest.raises(V3MetricError, match="cause export"):
        validate_storage_dispatch(actual, discharge_mw=pd.Series([0.0, 1.1], index=actual.index))


def test_reverse_beta_applies_parallel_n_minus_1_ratio_once() -> None:
    assert reverse_beta([100.0], operation_mode="split") == pytest.approx(0.8)
    assert reverse_beta([100.0, 80.0], operation_mode="parallel") == pytest.approx(80.0 / 180.0)


def test_path_metrics_aggregates_synchronously_before_taking_peaks() -> None:
    frame = pd.DataFrame(
        [
            {"timestamp": "2025-01-01 00:00", "region_id": "QX-00005", "voltage_kv": 110, "transformer_uid": "T1", "p_actual_mw": 60.0, "capacity_mva": 100.0, "operation_mode": "split"},
            {"timestamp": "2025-01-01 00:00", "region_id": "QX-00005", "voltage_kv": 110, "transformer_uid": "T2", "p_actual_mw": 40.0, "capacity_mva": 100.0, "operation_mode": "split"},
            {"timestamp": "2025-01-01 01:00", "region_id": "QX-00005", "voltage_kv": 110, "transformer_uid": "T1", "p_actual_mw": -20.0, "capacity_mva": 100.0, "operation_mode": "split"},
            {"timestamp": "2025-01-01 01:00", "region_id": "QX-00005", "voltage_kv": 110, "transformer_uid": "T2", "p_actual_mw": -10.0, "capacity_mva": 100.0, "operation_mode": "split"},
        ]
    )
    result = compute_path_metrics(frame, path_id="PATH_ACTUAL_2021_2025")
    row = result.iloc[0]
    assert row.p_plus_mw == pytest.approx(100.0)
    assert row.p_minus_mw == pytest.approx(30.0)
    assert row.capacity_mva == pytest.approx(200.0)
    assert row.clr == pytest.approx(2.0)
    assert row.positive_capacity_gap_mw == pytest.approx(0.0)


def test_real_annual_anchor_remains_a_same_voltage_total_volume_reference() -> None:
    reference = pd.read_csv(PROCESSED / "annual_reference.csv")
    decision = reference[reference.year.isin([2022, 2023, 2024, 2025])]
    assert len(decision) == 64
    assert decision.groupby(["year", "voltage_kv"]).region_id.nunique().eq(8).all()
    assert not decision.groupby("year").official_capacity_mva.sum().eq(
        decision.groupby("year").official_capacity_mva.sum().iloc[0]
    ).all()
