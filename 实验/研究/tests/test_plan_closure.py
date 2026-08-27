from __future__ import annotations

import pandas as pd
import pytest


def test_station_gap_summary_uses_maximum_and_device_counts() -> None:
    from src.real_matrices import _physical_gap_summary

    stations = pd.DataFrame(
        [
            {
                "region_id": "QX-00001",
                "voltage_kv": 110,
                "forward_peak_static_mw": 12.0,
                "forward_limit_mw": 10.0,
                "reverse_gap_parallel_static_mw": 1.0,
            },
            {
                "region_id": "QX-00001",
                "voltage_kv": 110,
                "forward_peak_static_mw": 11.0,
                "forward_limit_mw": 10.0,
                "reverse_gap_parallel_static_mw": 4.0,
            },
        ]
    )

    result = _physical_gap_summary(stations).iloc[0]

    assert result["positive_capacity_gap_mw"] == pytest.approx(2.0)
    assert result["reverse_hosting_gap_mw"] == pytest.approx(4.0)
    assert result["positive_gap_device_count"] == 2
    assert result["reverse_gap_device_count"] == 2
    assert result["measure_trigger_constraint"] == "positive_and_reverse_gap"


