"""v3.2 实际资产共同基线与存量豁免控制测试。"""
from __future__ import annotations

import pandas as pd
import pytest

from src.v32_policy import V32PolicyError, prepare_grandfathered_rcap_control


def _annual() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "year": 2021,
                "region_id": "QX-A",
                "voltage_kv": 110,
                "baseline_capacity_mva": 2000.0,
                "positive_peak_mw": 800.0,
            },
            {
                "year": 2022,
                "region_id": "QX-A",
                "voltage_kv": 110,
                "baseline_capacity_mva": 2000.0,
                "positive_peak_mw": 750.0,
            },
            {
                "year": 2022,
                "region_id": "QX-B",
                "voltage_kv": 35,
                "baseline_capacity_mva": 500.0,
                "positive_peak_mw": 310.0,
            },
        ]
    )


def test_v32_uses_actual_baseline_and_grandfathers_existing_capacity() -> None:
    source = _annual()
    out = prepare_grandfathered_rcap_control(source, rcap=2.0)

    qx_a_2022 = out[(out.region_id == "QX-A") & (out.year == 2022)].iloc[0]
    # 2021 实际存量 2000 MVA 不被压回 2×750=1500；只有新增容量受限。
    assert qx_a_2022.baseline_capacity_mva == pytest.approx(2000.0)
    assert qx_a_2022.planning_baseline_capacity_mva == pytest.approx(2000.0)
    assert qx_a_2022.reported_baseline_capacity_mva == pytest.approx(1500.0)
    assert bool(qx_a_2022.legacy_capacity_grandfathered) is True
    assert qx_a_2022.policy_rcap == pytest.approx(2.0)

    # 35 kV 辅助层不施加逐年 Rcap 上界，物理和规划基线保持实际值。
    qx_b = out[out.region_id == "QX-B"].iloc[0]
    assert qx_b.reported_baseline_capacity_mva == pytest.approx(500.0)
    assert qx_b.policy_rcap == float("inf")
    assert bool(qx_b.legacy_capacity_grandfathered) is False


def test_v32_rejects_nonpositive_rcap_and_missing_baseline_columns() -> None:
    with pytest.raises(V32PolicyError):
        prepare_grandfathered_rcap_control(_annual(), rcap=0.0)
    with pytest.raises(V32PolicyError):
        prepare_grandfathered_rcap_control(
            _annual().drop(columns=["baseline_capacity_mva"]), rcap=2.0
        )
