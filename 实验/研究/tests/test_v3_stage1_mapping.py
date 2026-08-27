from __future__ import annotations

import json
from pathlib import Path
from dataclasses import replace

import pandas as pd
import pytest

from src import io_loader
from scripts import approve_timeseries_mapping


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "data/tuomin/电网建模数据_Agent整合版_V1.2"
CONTRACT = ROOT / "model_contract.yaml"
LINEAGE = {
    "source_ref",
    "source_version",
    "transformation",
    "scenario_id",
    "quality_flag",
    "source_sha256",
}


def test_v3_stage1_exposes_cross_year_adapter_and_approval_entrypoints() -> None:
    assert hasattr(io_loader, "adapt_real_2021_2025")
    assert hasattr(io_loader, "approve_real_timeseries_mapping")


@pytest.fixture(scope="module")
def processed(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    output = tmp_path_factory.mktemp("real_2021_2025")
    manifest = io_loader.adapt_real_2021_2025(SOURCE_ROOT, output, CONTRACT)
    return output, manifest


def test_v3_stage1_writes_cross_year_mapping_asset_and_actual_action_tables(
    processed: tuple[Path, dict],
) -> None:
    output, _ = processed
    required = {
        "timeseries_column_map_2022_2026_review.csv",
        "timeseries_mapping_approval.csv",
        "transformer_hourly_2022.csv.gz",
        "transformer_hourly_2023.csv.gz",
        "transformer_hourly_2024.csv.gz",
        "transformer_hourly_2025.csv.gz",
        "annual_asset_whitelist.csv",
        "annual_asset_reconciliation.csv",
        "actual_asset_actions_2021_2025.csv",
        "data_quality_issues.csv",
        "manifest.json",
    }
    assert required <= {path.name for path in output.iterdir()}
    for path in sorted(output.glob("*.csv")):
        frame = pd.read_csv(path)
        assert LINEAGE <= set(frame.columns), path.name
        assert frame[list(LINEAGE)].notna().all().all(), path.name


def test_v3_mapping_preserves_source_headers_and_approved_target_candidates(
    processed: tuple[Path, dict],
) -> None:
    output, _ = processed
    review = pd.read_csv(output / "timeseries_column_map_2022_2026_review.csv")
    assert len(review) == 58 * 5
    assert {"year", "source_sheet", "source_header_station_id", "transformer_uid"} <= set(review)

    conflicts = review[review["series_column_1_based"].isin([11, 12, 27, 28])]
    assert set(conflicts.loc[conflicts["series_column_1_based"].isin([11, 12]), "source_header_station_id"]) == {"BDZ-00158"}
    assert set(conflicts.loc[conflicts["series_column_1_based"].isin([27, 28]), "source_header_station_id"]) == {"BDZ-00005"}
    assert set(conflicts.loc[conflicts["series_column_1_based"].isin([11, 12]), "station_id"]) == {"BDZ-00290"}
    assert set(conflicts.loc[conflicts["series_column_1_based"].isin([27, 28]), "station_id"]) == {"BDZ-00247"}

    approval = pd.read_csv(output / "timeseries_mapping_approval.csv")
    assert len(approval) == 58
    assert {
        "series_column_1_based",
        "source_header_station_id",
        "transformer_uid",
        "approval_status",
        "approval_authority",
        "approval_date",
        "approval_basis",
        "candidate_map_sha256",
        "source_sha256",
    } <= set(approval)
    assert set(approval["approval_authority"]) == {"project_owner"}
    assert not approval["approval_status"].eq("approved").any()


def test_v3_annual_gate_excludes_2025_year_end_only_transformers(
    processed: tuple[Path, dict],
) -> None:
    output, _ = processed
    whitelist = pd.read_csv(output / "annual_asset_whitelist.csv")
    qx_2025 = whitelist[
        (whitelist["year"] == 2025)
        & (whitelist["region_id"] == "QX-00005")
        & (whitelist["voltage_kv"] == 110)
        & (whitelist["asset_scope_id"] == "operating_2025")
        & (whitelist["in_annual_operating_whitelist"])
    ]
    assert len(qx_2025) == 40
    assert not qx_2025["transformer_uid"].str.contains("BDZ-00056").any()

    year_end = whitelist[
        (whitelist["year"] == 2025)
        & (whitelist["region_id"] == "QX-00005")
        & (whitelist["voltage_kv"] == 110)
        & (whitelist["asset_scope_id"] == "year_end_2025")
    ]
    assert len(year_end) == 42


def test_v3_quality_ledger_keeps_three_2024_anomaly_raw_values(
    processed: tuple[Path, dict],
) -> None:
    output, _ = processed
    issues = pd.read_csv(output / "data_quality_issues.csv")
    anomalies = issues[issues["issue_id"].str.startswith("TS-2024-ANOMALY")]
    assert set(anomalies["raw_value_mw"]) == {-7319.0, -6858.0, 16630.0}
    assert set(anomalies["source_column_1_based"]) == {31, 32}
    assert set(anomalies["quality_flag"]) == {"isolated_quantity_outlier"}


def test_v3_manifest_records_gate_and_input_output_hashes(processed: tuple[Path, dict]) -> None:
    output, manifest = processed
    saved = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert saved["dataset_id"] == "real_2021_2025"
    assert saved["contract_version"] == "3.1.0"
    assert saved["timeseries_gate"]["grade_a_ready"] is False
    assert saved["timeseries_gate"]["annual_gate_rule"] == "annual_asset_whitelist"
    assert saved["source_files"]
    assert saved["output_files"]
    assert manifest["dataset_fingerprint"] == saved["dataset_fingerprint"]


def test_v3_approval_cli_validates_project_owner_copy_without_touching_source(
    processed: tuple[Path, dict], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output, _ = processed
    submitted = pd.read_csv(output / "timeseries_mapping_approval.csv")
    submitted["approval_status"] = "approved"
    submitted["approval_date"] = "2026-08-13"
    submitted["approval_basis"] = "project_owner_review_copy_for_gate_test"
    approval_file = tmp_path / "approval.csv"
    submitted.to_csv(approval_file, index=False)

    exit_code = approve_timeseries_mapping.main(
        [
            "--processed-root",
            str(output),
            "--approval-file",
            str(approval_file),
            "--output-file",
            str(tmp_path / "approved.csv"),
        ]
    )

    assert exit_code == 0
    result = json.loads(capsys.readouterr().out)
    assert result["approval_status_counts"] == {"approved": 58}
    assert (tmp_path / "approved.csv").is_file()


def test_v3_approval_gate_uses_2025_operating_whitelist_not_year_end_rows(
    processed: tuple[Path, dict], tmp_path: Path
) -> None:
    output, _ = processed
    submitted = pd.read_csv(output / "timeseries_mapping_approval.csv")
    submitted.loc[submitted["series_column_1_based"] <= 56, "approval_status"] = "approved"
    submitted.loc[submitted["series_column_1_based"] > 56, "approval_status"] = "rejected"
    submitted["approval_date"] = "2026-08-14"
    submitted["approval_basis"] = submitted["series_column_1_based"].map(
        lambda column: (
            "project_owner_approved_candidate_mapping_for_2025_operating_scope"
            if column <= 56
            else "project_owner_excluded_year_end_only_from_2025_operating_scope"
        )
    )
    approval_file = tmp_path / "approved_operating_scope.csv"
    submitted.to_csv(approval_file, index=False)

    result = io_loader.approve_real_timeseries_mapping(output, approval_file)

    assert result["formal_use_allowed"] is True
    assert result["required_formal_rows"] == 40
    assert result["approved_formal_rows"] == 40
    formal = result["approval"].set_index("series_column_1_based")["formal_use_allowed"]
    assert int(formal.loc[1:56].sum()) == 40
    assert not bool(formal.loc[[57, 58]].any())

    canonical_map = pd.read_csv(output / "timeseries_column_map_2025.csv")
    assert int(canonical_map["formal_use_allowed"].sum()) == 40
    assert not canonical_map["approval_status"].eq("conditional").any()
    saved_manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert saved_manifest["timeseries_review"]["conditional_columns"] == 0
    quality = pd.read_csv(output / "data_quality_issues.csv")
    candidate_issue = quality.loc[quality["issue_id"].eq("DQ-TIMESERIES-CANDIDATE")].iloc[0]
    assert candidate_issue["quality_flag"] == "project_owner_approved_with_scope_exceptions"
    assert not quality["description"].astype(str).str.contains("candidate-only until stage-2").any()
