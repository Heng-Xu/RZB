"""严格路径起点归一约定（3.1.0，记账式）的单元测试。

定版口径（2026-08-24）：S0 = min(S_2021, 2 × min(P_2021, min决策年峰))。
归一只写 ``reported_baseline_capacity_mva`` 报告口径列；物理容量
``baseline_capacity_mva`` 保持 2021 实际状态不动——设备级缺口、储能定容
仍按真实资产评估。峰值保持官方锚点原值。
"""
from __future__ import annotations

import pandas as pd
import pytest

from src.v3_pipeline import V3PipelineError, _apply_strict_baseline


def _reference_csv(tmp_path):
    rows = [
        ("2021", "QX-A", "110", 2000.0, 800.0),
        ("2021", "QX-B", "110", 500.0, 300.0),
    ]
    lines = ["year,region_id,voltage_kv,official_capacity_mva,official_positive_peak_mw"]
    lines += [f"{y},{r},{v},{s},{p}" for y, r, v, s, p in rows]
    path = tmp_path / "annual_reference.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _annual() -> pd.DataFrame:
    # QX-A: 报告口径 2×min(800,700)=1400；QX-B: 本已合规保持 500。
    rows = []
    for year, peak_a, peak_b in ((2022, 750.0, 310.0), (2023, 700.0, 290.0), (2024, 760.0, 305.0), (2025, 780.0, 315.0)):
        rows.append({"year": year, "region_id": "QX-A", "voltage_kv": 110,
                     "capacity_mva": 2000.0, "baseline_capacity_mva": 2000.0, "positive_peak_mw": peak_a})
        rows.append({"year": year, "region_id": "QX-B", "voltage_kv": 110,
                     "capacity_mva": 500.0, "baseline_capacity_mva": 500.0, "positive_peak_mw": peak_b})
    return pd.DataFrame(rows)


def test_strict_baseline_adds_reported_column_without_touching_physical_state(tmp_path: pytest.Path) -> None:
    ref = _reference_csv(tmp_path)
    source = _annual()
    out = _apply_strict_baseline(source, ref.parent)

    a = out[out["region_id"].eq("QX-A")]
    b = out[out["region_id"].eq("QX-B")]
    # 记账口径：报告起点按安全峰归一
    assert (a["reported_baseline_capacity_mva"] == 1400.0).all()
    assert (b["reported_baseline_capacity_mva"] == 500.0).all()
    # 物理容量与峰值必须保持原值
    assert (out["baseline_capacity_mva"] == source["baseline_capacity_mva"]).all()
    assert (out["positive_peak_mw"] == source["positive_peak_mw"]).all()


def test_strict_baseline_requires_full_reference_coverage(tmp_path: pytest.Path) -> None:
    ref = _reference_csv(tmp_path)
    annual = _annual()
    extra = pd.DataFrame([{"year": 2022, "region_id": "QX-C", "voltage_kv": 110,
                           "capacity_mva": 100.0, "baseline_capacity_mva": 100.0,
                           "positive_peak_mw": 50.0}])
    with pytest.raises(V3PipelineError):
        _apply_strict_baseline(pd.concat([annual, extra], ignore_index=True), ref.parent)
