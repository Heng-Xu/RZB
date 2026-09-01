"""v3.2 弹性前沿：规划控制上限 Rcap 与实现 CLR 必须分离。"""
from __future__ import annotations

import pandas as pd
import pytest

from src.v32_model import (
    intersect_unique_rcap_point_sets,
    recommended_rcap_interval,
    robust_rcap_interval,
)


def _frontier(rows: list[tuple[float | str, str, float | None, float | None, int | None, float | None, bool]]) -> pd.DataFrame:
    return pd.DataFrame(
        rows,
        columns=[
            "rcap",
            "region_id",
            "cumulative_in_service_eac_wanyuan",
            "clr_2025",
            "storage_modules",
            "capacity_action_delta_mva",
            "feasible",
        ],
    )


def test_recommendation_returns_rcap_band_and_realized_clr_band_as_different_fields() -> None:
    frontier = _frontier(
        [
            (1.9, "QX-A", 150.0, 1.82, 8, 50.0, True),
            (2.0, "QX-A", 100.0, 1.91, 4, 50.0, True),
            (2.1, "QX-A", 102.0, 1.96, 4, 50.0, True),
            (2.2, "QX-A", 140.0, 2.03, 6, 100.0, True),
            ("unbounded", "QX-A", 100.0, 2.17, 2, 50.0, True),
        ]
    )
    result = recommended_rcap_interval(frontier, region_id="QX-A", near_optimal_band=0.05)

    # 数值 Rcap 点的最低成本为 100，5%近优带={2.0, 2.1}。
    assert result["rcap_interval_low"] == pytest.approx(2.0)
    assert result["rcap_interval_high"] == pytest.approx(2.1)
    # 对应实现 CLR 是另一个量，绝不能拿 1.91~1.96 与 2.0~2.1 直接求交。
    assert result["realized_clr_2025_low"] == pytest.approx(1.91)
    assert result["realized_clr_2025_high"] == pytest.approx(1.96)
    assert result["rcap_points"] == [2.0, 2.1]


def test_measure_flip_forces_interval_only() -> None:
    frontier = _frontier(
        [
            (2.0, "QX-B", 100.0, 1.90, 4, 50.0, True),
            (2.1, "QX-B", 103.0, 1.95, 8, 100.0, True),
        ]
    )
    result = recommended_rcap_interval(frontier, region_id="QX-B")
    assert result["interval_only"] is True
    assert result["rcap_point_estimate"] is None
    assert result["measure_flip"] is True


def test_robust_band_intersects_rcap_with_rcap_not_with_realized_clr() -> None:
    base = _frontier(
        [
            (2.0, "QX-C", 100.0, 1.82, 4, 50.0, True),
            (2.1, "QX-C", 103.0, 1.88, 4, 50.0, True),
            (2.2, "QX-C", 120.0, 1.95, 5, 50.0, True),
        ]
    )
    low_pf = _frontier(
        [
            (2.0, "QX-C", 102.0, 1.79, 5, 50.0, True),
            (2.1, "QX-C", 100.0, 1.85, 5, 50.0, True),
            (2.2, "QX-C", 104.0, 1.92, 5, 50.0, True),
        ]
    )
    high_pf = _frontier(
        [
            (2.0, "QX-C", 101.0, 1.86, 3, 50.0, True),
            (2.1, "QX-C", 100.0, 1.91, 3, 50.0, True),
            (2.2, "QX-C", 130.0, 1.98, 3, 50.0, True),
        ]
    )
    result = robust_rcap_interval(
        base,
        {"cos_phi_0.90": low_pf, "cos_phi_1.00": high_pf},
        region_id="QX-C",
        near_optimal_band=0.05,
    )

    # base={2.0,2.1}; low_pf={2.0,2.1,2.2}; high_pf={2.0,2.1};
    # 同维度稳健交集={2.0,2.1}。
    assert result["robust_rcap_points"] == [2.0, 2.1]
    assert result["robust_rcap_interval_low"] == pytest.approx(2.0)
    assert result["robust_rcap_interval_high"] == pytest.approx(2.1)
    assert result["robust"] is True


def test_robust_intersection_deduplicates_baseline_control_point_sets() -> None:
    assert intersect_unique_rcap_point_sets(
        [{2.3, 2.4, 2.5}, {2.3, 2.4, 2.5}, {2.4, 2.5, 2.6}]
    ) == [2.4, 2.5]


def test_no_feasible_numeric_rcap_returns_explicit_reason() -> None:
    frontier = _frontier(
        [(1.5, "QX-D", None, None, None, None, False)]
    )
    result = recommended_rcap_interval(frontier, region_id="QX-D")
    assert result["rcap_interval_low"] is None
    assert result["reason"] == "no_feasible_numeric_rcap"
