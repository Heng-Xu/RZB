from __future__ import annotations

import pandas as pd
import pytest

from src.real_metrics import (
    V3MetricError,
    compute_path_metrics,
    path_net_load,
    reverse_beta,
    validate_storage_dispatch,
)


def _frame() -> pd.DataFrame:
    timestamps = pd.date_range("2025-01-01 00:00", periods=3, freq="h")
    return pd.DataFrame(
        {
            "timestamp": list(timestamps) * 2,
            "region_id": ["QX-00005"] * 6,
            "voltage_kv": [110] * 6,
            "transformer_uid": ["T1"] * 3 + ["T2"] * 3,
            "capacity_mva": [100.0] * 3 + [60.0] * 3,
            "operation_mode": ["split"] * 6,
            "p_actual_mw": [10.0, -5.0, 20.0, 0.0, 0.0, 0.0],
            "p_charge_mw": [0.0] * 6,
            "p_discharge_mw": [0.0] * 6,
            "p_tie_mw": [0.0] * 6,
        }
    )


def test_path_metrics_recomputes_positive_denominator_after_path_dispatch() -> None:
    frame = _frame()
    unbounded = compute_path_metrics(frame, path_id="PATH_OPT_CLR_UNBOUNDED")
    dispatched = frame.copy()
    dispatched.loc[(dispatched["transformer_uid"] == "T1") & dispatched["timestamp"].eq(pd.Timestamp("2025-01-01 02:00")), "p_discharge_mw"] = 5.0
    dispatched_result = compute_path_metrics(
        dispatched, path_id="PATH_OPT_CLR_UNBOUNDED"
    )

    assert unbounded.loc[0, "p_plus_mw"] == pytest.approx(20.0)
    assert dispatched_result.loc[0, "p_plus_mw"] == pytest.approx(15.0)
    assert dispatched_result.loc[0, "clr"] == pytest.approx(160.0 / 15.0)
    assert dispatched_result.loc[0, "clr"] != pytest.approx(unbounded.loc[0, "clr"])


def test_path_metrics_aggregates_before_peak_and_keeps_reverse_separate() -> None:
    frame = _frame()
    frame.loc[frame["transformer_uid"].eq("T1"), "p_actual_mw"] = [10.0, -5.0, 0.0]
    frame.loc[frame["transformer_uid"].eq("T2"), "p_actual_mw"] = [0.0, 20.0, -30.0]
    result = compute_path_metrics(frame, path_id="PATH_ACTUAL_2021_2025")

    assert result.loc[0, "p_plus_mw"] == pytest.approx(15.0)
    assert result.loc[0, "p_minus_mw"] == pytest.approx(30.0)
    assert result.loc[0, "capacity_mva"] == pytest.approx(160.0)


def test_storage_rules_forbid_cross_zero_export_and_simultaneous_dispatch() -> None:
    actual = pd.Series([-2.0, 3.0, 0.0])
    with pytest.raises(V3MetricError, match="cross zero"):
        validate_storage_dispatch(actual, pd.Series([3.0, 0.0, 0.0]), pd.Series([0.0, 0.0, 0.0]))
    with pytest.raises(V3MetricError, match="export"):
        validate_storage_dispatch(actual, pd.Series([0.0, 0.0, 0.0]), pd.Series([0.0, 4.0, 0.0]))
    with pytest.raises(V3MetricError, match="simultaneous"):
        validate_storage_dispatch(actual, pd.Series([0.0, 1.0, 0.0]), pd.Series([0.0, 1.0, 0.0]))

    net = path_net_load(actual, pd.Series([2.0, 0.0, 0.0]), pd.Series([0.0, 2.0, 0.0]))
    assert net.tolist() == pytest.approx([0.0, 1.0, 0.0])


def test_parallel_reverse_beta_contains_n_minus_1_ratio_once() -> None:
    assert reverse_beta([60.0, 40.0], operation_mode="parallel") == pytest.approx(0.4)
    assert reverse_beta([60.0, 40.0], operation_mode="split") == pytest.approx(0.8)
    assert reverse_beta([100.0], operation_mode="single") == pytest.approx(0.8)


def test_device_gaps_are_reported_separately_from_clr_trigger() -> None:
    frame = _frame()
    frame.loc[frame["transformer_uid"].eq("T2"), "p_actual_mw"] = [70.0, 0.0, -60.0]
    result = compute_path_metrics(frame, path_id="PATH_ACTUAL_2021_2025")

    assert result.loc[0, "positive_capacity_gap_mw"] == pytest.approx(13.0)
    assert result.loc[0, "reverse_hosting_gap_mw"] == pytest.approx(14.4)
    assert result.loc[0, "positive_gap_device_count"] == 1
    assert result.loc[0, "reverse_gap_device_count"] == 1
    assert "positive_capacity_gap" in result.loc[0, "measure_trigger_constraint"]
    assert "reverse_hosting_gap" in result.loc[0, "measure_trigger_constraint"]
