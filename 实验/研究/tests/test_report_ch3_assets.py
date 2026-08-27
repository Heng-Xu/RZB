from __future__ import annotations

import importlib.util
import json
import warnings
from pathlib import Path

import pandas as pd
import pytest
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "real_2021_2025"
SCRIPT = ROOT / "scripts" / "build_report_ch3_assets.py"


def _load_builder():
    assert SCRIPT.is_file(), "第三章可追溯数据摘要与图表生成脚本尚未实现"
    spec = importlib.util.spec_from_file_location("build_report_ch3_assets", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_report_asset_builder_exists() -> None:
    assert SCRIPT.is_file(), "第三章可追溯数据摘要与图表生成脚本尚未实现"


@pytest.fixture(scope="module")
def built_assets(tmp_path_factory: pytest.TempPathFactory):
    module = _load_builder()
    target = tmp_path_factory.mktemp("report_ch3_assets")
    summary_dir = target / "summary"
    figure_dir = target / "figures"
    result = module.build_report_assets(DATA, summary_dir, figure_dir)
    return module, result, summary_dir, figure_dir


def test_annual_summary_preserves_official_voltage_separated_anchors(built_assets) -> None:
    _, _, summary_dir, _ = built_assets
    annual = pd.read_csv(summary_dir / "第三章_年度片区指标.csv")

    assert len(annual) == 80
    assert set(annual["year"]) == {2021, 2022, 2023, 2024, 2025}
    assert set(annual["voltage_kv"]) == {35, 110}
    assert annual["region_id"].nunique() == 8
    assert annual.groupby(["year", "voltage_kv"]).size().eq(8).all()

    recomputed = annual["official_capacity_mva"] / annual["official_positive_peak_mw"]
    assert (recomputed.round(2) - annual["official_clr"]).abs().max() <= 0.01


def test_hourly_summary_marks_only_closed_device_scope_as_formal(built_assets) -> None:
    _, _, summary_dir, _ = built_assets
    quality = pd.read_csv(summary_dir / "第三章_逐时数据质量.csv").set_index("year")

    assert list(quality.index) == [2022, 2023, 2024, 2025]
    assert quality.loc[2025, "formal_transformer_count"] == 40
    assert quality.loc[2025, "formal_station_count"] == 20
    assert quality.loc[2025, "formal_timestamp_count"] == 8760
    assert quality.loc[2025, "evidence_use"] == "formal_2025_operating_scope"
    assert quality.loc[[2022, 2023, 2024], "evidence_use"].eq(
        "context_only_historical_asset_scope_not_closed"
    ).all()
    assert quality.loc[2024, "known_isolated_outlier_count"] == 3


def test_typical_region_profile_uses_40_transformers_and_official_peak_anchor(built_assets) -> None:
    _, _, summary_dir, _ = built_assets
    stats = pd.read_csv(summary_dir / "第三章_典型片区多工况统计.csv")

    assert len(stats) == 1
    row = stats.iloc[0]
    assert row["year"] == 2025
    assert row["region_id"] == "QX-00005"
    assert row["voltage_kv"] == 110
    assert row["transformer_count"] == 40
    assert row["station_count"] == 20
    assert row["timestamp_count"] == 8760
    assert row["positive_peak_mw"] == pytest.approx(956.45, abs=1e-6)
    assert row["reverse_peak_mw"] > 0
    assert row["reverse_hours"] > 0
    assert row["direction_transition_count"] > 0


def test_known_2024_outliers_remain_auditable_and_do_not_enter_formal_stats(built_assets) -> None:
    _, result, summary_dir, _ = built_assets
    manifest = json.loads((summary_dir / "第三章_数据摘要_manifest.json").read_text(encoding="utf-8"))

    assert manifest["quality_gate"]["known_2024_anomaly_values_mw"] == [-7319.0, -6858.0, 16630.0]
    assert manifest["quality_gate"]["formal_multicondition_years"] == [2025]
    assert result["formal_multicondition_years"] == [2025]


def test_outputs_include_cross_year_pv_warning_and_all_planned_figures(built_assets) -> None:
    _, _, summary_dir, figure_dir = built_assets
    database_note = (summary_dir / "第三章_数据库规模与血缘.md").read_text(encoding="utf-8")
    assert "2026 年快照" in database_note
    assert "跨年背景" in database_note

    expected = {
        "图1-1_研究技术路线.png",
        "图3-1_八片区110kV容载比年度变化.png",
        "图3-2_典型片区容量同步峰值与容载比变化.png",
        "图3-3_典型年度净负荷持续曲线.png",
        "图3-4_典型日正反向运行曲线.png",
        "图3-5_指标作用机制示意图.png",
        "图3-6_数据库构建流程.png",
    }
    assert {path.name for path in figure_dir.glob("*.png")} == expected
    assert all(path.stat().st_size > 20_000 for path in figure_dir.glob("*.png"))
    for path in figure_dir.glob("*.png"):
        with Image.open(path) as image:
            aspect_ratio = image.width / image.height
            assert 1.25 <= aspect_ratio <= 2.10, f"{path.name} 的宽高比不适合 A4 正文版心"

    script_text = SCRIPT.read_text(encoding="utf-8")
    assert "CSV / Markdown" not in script_text


def test_chinese_figure_rendering_has_no_missing_glyph_warning(tmp_path: Path) -> None:
    module = _load_builder()
    output = tmp_path / "中文图件.png"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        module._configure_matplotlib()
        module.plot_indicator_mechanism(output)
    missing = [warning for warning in caught if "Glyph" in str(warning.message)]
    assert not missing, "中文图件仍存在字体缺字警告"
