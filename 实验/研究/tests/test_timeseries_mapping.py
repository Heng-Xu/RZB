from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src import io_loader


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "data/tuomin/电网建模数据_Agent整合版_V1.2"
CONTRACT = ROOT / "model_contract.yaml"


@pytest.fixture(scope="module")
def reviewed(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    processed = tmp_path_factory.mktemp("reviewed_real_2021_2025")
    result = io_loader.adapt_real_2021_2025(SOURCE_ROOT, processed, CONTRACT)
    return processed, result


def test_cross_year_review_keeps_five_years_and_58_columns(
    reviewed: tuple[Path, dict],
) -> None:
    processed, _ = reviewed
    mapping = pd.read_csv(processed / "timeseries_column_map_2022_2026_review.csv")
    assert len(mapping) == 58 * 5
    assert mapping.groupby("year").size().to_dict() == {
        2022: 58,
        2023: 58,
        2024: 58,
        2025: 58,
        2026: 58,
    }
    assert mapping.groupby(["year", "series_column_1_based"]).size().eq(1).all()
    assert set(mapping.voltage_kv) == {35, 110}


def test_source_header_conflicts_are_preserved_and_targets_are_explicit(
    reviewed: tuple[Path, dict],
) -> None:
    processed, _ = reviewed
    mapping = pd.read_csv(processed / "timeseries_column_map_2022_2026_review.csv")
    selected = mapping[mapping.series_column_1_based.isin([11, 12, 27, 28])]
    assert set(selected.source_header_station_id) == {"BDZ-00158", "BDZ-00005"}
    assert set(selected.loc[selected.series_column_1_based.isin([11, 12]), "station_id"]) == {"BDZ-00290"}
    assert set(selected.loc[selected.series_column_1_based.isin([27, 28]), "station_id"]) == {"BDZ-00247"}
    assert selected.transformer_uid.notna().all()


def test_project_owner_gate_never_self_approves_formal_timeseries(
    reviewed: tuple[Path, dict],
) -> None:
    processed, _ = reviewed
    approval = pd.read_csv(processed / "timeseries_mapping_approval.csv")
    assert len(approval) == 58
    assert set(approval.approval_status) <= {"conditional", "rejected"}
    assert not approval.approval_status.eq("approved").any()
    assert set(approval.approval_authority) == {"project_owner"}
    assert approval.approval_date.isna().all()


def test_hourly_outputs_keep_complete_year_axes_and_anomaly_ledger(
    reviewed: tuple[Path, dict],
) -> None:
    processed, _ = reviewed
    expected_hours = {2022: 8760, 2023: 8760, 2024: 8784, 2025: 8760}
    for year, hours in expected_hours.items():
        hourly = pd.read_csv(processed / f"transformer_hourly_{year}.csv.gz")
        assert len(hourly) == 58 * hours
        assert hourly.groupby("series_column_1_based").timestamp.nunique().eq(hours).all()
        assert {"net_load_mw_raw", "net_load_mw", "mapping_approval_status", "formal_use_allowed"} <= set(hourly.columns)
        assert not hourly.formal_use_allowed.astype(bool).any()
    issues = pd.read_csv(processed / "data_quality_issues.csv")
    anomalies = issues[issues.issue_id.astype(str).str.startswith("TS-2024-ANOMALY")]
    assert set(anomalies.raw_value_mw) == {-7319.0, -6858.0, 16630.0}
    assert set(anomalies.source_column_1_based) == {31.0, 32.0}
