from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src import io_loader


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "data/tuomin/电网建模数据_Agent整合版_V1.2"
CONTRACT_PATH = ROOT / "model_contract.yaml"
LINEAGE = {"source_ref", "source_version", "transformation", "scenario_id", "quality_flag", "source_sha256"}


def test_v3_adapter_has_cross_year_entrypoint() -> None:
    assert hasattr(io_loader, "adapt_real_2021_2025")


@pytest.fixture(scope="module")
def adapted(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    output = tmp_path_factory.mktemp("real_2021_2025_adapter")
    manifest = io_loader.adapt_real_2021_2025(SOURCE_ROOT, output, CONTRACT_PATH)
    return output, manifest


def test_adapter_writes_v3_static_annual_and_timeseries_tables(adapted: tuple[Path, dict]) -> None:
    output, _ = adapted
    required = {
        "station_master.csv", "transformer_master.csv", "expansion_candidates.csv",
        "station_static_load.csv", "transformer_static_load.csv", "station_pv_snapshot.csv",
        "pv_profile_2025.csv", "network_lines_110kv.csv", "county_clr_reference.csv",
        "cost_cases.csv", "asset_scope_summary.csv", "annual_reference.csv",
        "annual_asset_whitelist.csv", "annual_asset_reconciliation.csv",
        "actual_asset_actions_2021_2025.csv", "timeseries_column_map_2022_2026_review.csv",
        "timeseries_mapping_approval.csv", "transformer_hourly_2022.csv.gz",
        "transformer_hourly_2023.csv.gz", "transformer_hourly_2024.csv.gz",
        "transformer_hourly_2025.csv.gz", "data_quality_issues.csv", "manifest.json",
    }
    assert required <= {path.name for path in output.iterdir()}


def test_qx00005_annual_scope_keeps_year_end_and_operating_counts(adapted: tuple[Path, dict]) -> None:
    output, _ = adapted
    whitelist = pd.read_csv(output / "annual_asset_whitelist.csv")
    qx = whitelist[(whitelist.year == 2025) & (whitelist.region_id == "QX-00005") & (whitelist.voltage_kv == 110)]
    assert len(qx[qx.asset_scope_id == "year_end_2025"]) == 42
    operating = qx[(qx.asset_scope_id == "operating_2025") & qx.in_annual_operating_whitelist.astype(str).str.lower().eq("true")]
    assert len(operating) == 40
    assert not operating.transformer_uid.str.contains("BDZ-00056").any()


def test_v3_mapping_preserves_source_rows_and_voltage_split(adapted: tuple[Path, dict]) -> None:
    output, _ = adapted
    master = pd.read_csv(output / "transformer_master.csv")
    assert {"source_row", "equipment_source_row"} <= set(master.columns)
    assert set(master.voltage_kv) == {35, 110}
    mapping = pd.read_csv(output / "timeseries_mapping_approval.csv")
    mapping = mapping.merge(
        master[["transformer_uid", "voltage_kv"]],
        on="transformer_uid",
        how="left",
        validate="one_to_one",
    )
    assert mapping.voltage_kv.value_counts().to_dict() == {110: 42, 35: 16}
    assert set(mapping.approval_status) <= {"conditional", "rejected"}
    assert mapping.approval_status.value_counts().to_dict() == {"conditional": 56, "rejected": 2}
    assert not mapping.approval_status.eq("approved").any()


def test_v3_pv_profile_and_annual_reference_close(adapted: tuple[Path, dict]) -> None:
    output, _ = adapted
    profile = pd.read_csv(output / "pv_profile_2025.csv")
    reference = pd.read_csv(output / "annual_reference.csv")
    assert len(profile) == 8760
    assert profile.phi_pv_raw.between(0.0, 1.0).all()
    assert len(reference) == 80
    assert set(reference.year) == {2021, 2022, 2023, 2024, 2025}
    assert reference.groupby(["year", "voltage_kv"]).region_id.nunique().eq(8).all()


def test_v3_candidates_are_discrete_and_source_backed(adapted: tuple[Path, dict]) -> None:
    output, _ = adapted
    candidates = pd.read_csv(output / "expansion_candidates.csv")
    assert candidates.candidate_id.is_unique
    assert set(candidates.candidate_type) <= {"new_third_transformer", "new_station"}
    assert (candidates.delta_capacity_mva == candidates.new_capacity_mva).all()
    assert (candidates.source_row > 0).all()
    assert not (candidates.capex_center_wanyuan == 800.0).any()


def test_v3_anomaly_ledger_retains_all_three_raw_values(adapted: tuple[Path, dict]) -> None:
    output, _ = adapted
    issues = pd.read_csv(output / "data_quality_issues.csv")
    anomaly = issues[issues.issue_id.astype(str).str.startswith("TS-2024-ANOMALY")]
    assert set(anomaly.raw_value_mw) == {-7319.0, -6858.0, 16630.0}
    assert set(anomaly.source_column_1_based) == {31.0, 32.0}
    assert set(anomaly.quality_flag) == {"isolated_quantity_outlier"}


def test_v3_all_csv_tables_preserve_lineage_and_voltage(adapted: tuple[Path, dict]) -> None:
    output, _ = adapted
    for path in sorted(output.glob("*.csv")):
        frame = pd.read_csv(path)
        assert LINEAGE <= set(frame.columns), path.name
        assert frame[list(LINEAGE)].notna().all().all(), path.name
        if "voltage_kv" in frame:
            assert set(frame.voltage_kv.dropna().astype(int)) <= {35, 110}


def test_v3_manifest_reproducibly_hashes_sources_and_outputs(adapted: tuple[Path, dict], tmp_path: Path) -> None:
    output, first = adapted
    second = io_loader.adapt_real_2021_2025(SOURCE_ROOT, tmp_path / "repeat", CONTRACT_PATH)
    saved = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert first["dataset_fingerprint"] == second["dataset_fingerprint"]
    assert saved["dataset_id"] == "real_2021_2025"
    assert saved["contract_version"] == "3.2.0"
    assert all(len(item["sha256"]) == 64 for item in saved["source_files"].values())
