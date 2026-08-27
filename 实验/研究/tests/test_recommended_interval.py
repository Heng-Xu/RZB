"""推荐容载比区间（弹性前沿导出）单元测试。"""
from __future__ import annotations

import pandas as pd

from src.v3_outputs import recommended_clr_interval


def _frontier(rows: list[tuple[str, float, float, int, float, bool]]) -> pd.DataFrame:
    return pd.DataFrame(
        rows,
        columns=[
            "rcap",
            "region_id",
            "cumulative_in_service_eac_wanyuan",
            "storage_modules",
            "expansion_mva",
            "feasible",
        ],
    )


def test_interval_from_near_optimal_band() -> None:
    rows = [
        ("1.5", "QX-A", 500.0, 10, 0.0, True),
        ("2.0", "QX-A", 100.0, 4, 50.0, True),
        ("2.5", "QX-A", 102.0, 4, 50.0, True),
        ("3.0", "QX-A", 140.0, 6, 100.0, True),
        ("unbounded", "QX-A", 90.0, 2, 50.0, True),
    ]
    result = recommended_clr_interval(_frontier(rows), region_id="QX-A")
    # 近优带：≤ min(100)×1.05=105 → {2.0, 2.5}
    assert result["interval_low"] == 2.0
    assert result["interval_high"] == 2.5
    assert result["interval_only"] is True
    assert result["point_estimate"] is None
    assert result["unbounded_feasible"] is True


def test_point_estimate_when_band_is_single_stable_point() -> None:
    rows = [
        ("1.9", "QX-B", 300.0, 8, 0.0, True),
        ("2.0", "QX-B", 100.0, 3, 50.0, True),
        ("2.1", "QX-B", 150.0, 5, 80.0, True),
    ]
    result = recommended_clr_interval(_frontier(rows), region_id="QX-B")
    assert result["point_estimate"] == 2.0
    assert result["interval_only"] is False


def test_infeasible_region_returns_reason() -> None:
    rows = [("1.5", "QX-C", None, None, None, False)]
    result = recommended_cls = recommended_clr_interval(_frontier(rows), region_id="QX-C")
    assert result["interval_only"] is True
    assert result.get("reason") == "no_feasible_point"


def test_measure_flip_forces_interval_even_on_single_rcap() -> None:
    # 同一带内两行同 rcap 但措施不同 → 翻转，不给点估计。
    rows = [
        ("2.0", "QX-D", 100.0, 3, 50.0, True),
        ("2.0", "QX-D", 104.0, 5, 60.0, True),
    ]
    result = recommended_clr_interval(_frontier(rows), region_id="QX-D")
    assert result["interval_only"] is True
    assert result["point_estimate"] is None
