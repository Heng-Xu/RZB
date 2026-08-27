from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from src.v3_pipeline import run_v3_pipeline


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed/real_2021_2025"
CONTRACT_PATH = ROOT / "model_contract.yaml"


@pytest.fixture(scope="module")
def matrices(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    run_dir = tmp_path_factory.mktemp("real_v3_matrices")
    manifest = run_v3_pipeline(ROOT, PROCESSED, run_dir, CONTRACT_PATH)
    return run_dir, manifest


def test_two_voltage_matrices_are_separate_eight_region_outputs(
    matrices: tuple[Path, dict],
) -> None:
    run_dir, _ = matrices
    matrix_110 = pd.read_csv(run_dir / "county_110_recommendation_matrix.csv")
    matrix_35 = pd.read_csv(run_dir / "county_35_recommendation_matrix.csv")
    assert len(matrix_110) == len(matrix_35) == 8
    assert set(matrix_110.voltage_kv) == {110}
    assert set(matrix_35.voltage_kv) == {35}
    assert set(matrix_110.region_id) == set(matrix_35.region_id)
    assert not matrix_110.region_id.duplicated().any()


def test_matrix_contains_v3_paths_gaps_and_evidence_without_legacy_scheme_fields(
    matrices: tuple[Path, dict],
) -> None:
    run_dir, _ = matrices
    matrix = pd.read_csv(run_dir / "county_110_recommendation_matrix.csv")
    required = {
        "recommended_clr_interval",
        "recommended_clr_center",
        "recommended_clr_interval_effective_samples",
        "recommended_clr_interval_method",
        "capacity_base_mva",
        "positive_peak_base_mw",
        "reverse_peak_base_mw",
        "PATH_ACTUAL_2021_2025_clr_2025",
        "PATH_OPT_CLR_UNBOUNDED_clr_2025",
        "PATH_OPT_CLR_LE_2_clr_2025",
        "PATH_ACTUAL_2021_2025_cumulative_eac",
        "PATH_OPT_CLR_UNBOUNDED_cumulative_eac",
        "PATH_OPT_CLR_LE_2_cumulative_eac",
        "strict_path_incremental_cost",
        "positive_capacity_gap_mw",
        "reverse_hosting_gap_mw",
        "recommended_measure",
        "evidence_grade",
    }
    assert required <= set(matrix.columns)
    assert not any("SCHEME_" in column for column in matrix.columns)
    assert matrix.evidence_grade.isin(["EVIDENCE_A", "EVIDENCE_B", "EVIDENCE_C"]).all()
    assert (matrix["recommended_clr_interval_effective_samples"] >= 0).all()
    assert matrix["recommended_clr_interval_method"].notna().all()
    qx_formal = matrix[matrix["region_id"].eq("QX-00005")]
    assert len(qx_formal) == 1
    assert float(qx_formal.iloc[0]["reverse_peak_base_mw"]) == pytest.approx(
        397.22936552970606
    )
    no_sync_reverse_evidence = matrix[~matrix["region_id"].eq("QX-00005")]
    assert (
        no_sync_reverse_evidence["reverse_peak_base_mw"]
        .astype(str)
        .eq("未形成同步反向峰值")
        .all()
    )


def test_strict_path_rows_are_either_feasible_at_two_or_explicitly_infeasible(
    matrices: tuple[Path, dict],
) -> None:
    run_dir, _ = matrices
    years = pd.read_csv(run_dir / "path_year_results.csv")
    strict = years[years.path_id.eq("PATH_OPT_CLR_LE_2")]
    feasible = strict[strict.status.eq("feasible")]
    assert (feasible.clr <= 2.0 + 1e-9).all()
    assert set(strict.status) <= {"feasible", "infeasible"}
    for _, group in strict.groupby(["region_id", "voltage_kv"]):
        assert len(group) == 4
        assert len(set(group["complete_path_status"])) == 1


def test_manifest_and_word_matrices_are_present_and_machine_readable(
    matrices: tuple[Path, dict],
) -> None:
    run_dir, manifest = matrices
    saved = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert saved["dataset_id"] == "real_2021_2025"
    assert saved["voltage_separation"] is True
    # 3.1.0：严格路径起点为归一约定状态，跨口径 EAC 包含关系废止，
    # manifest 以口径说明字段替代旧的包含关系标记。
    assert manifest["path_cost_inclusion_validated"] is False
    assert "归一" in str(manifest.get("path_comparison_note", ""))
    for voltage in (110, 35):
        docx = run_dir / f"county_{voltage}_recommendation_matrix.docx"
        with zipfile.ZipFile(docx) as archive:
            assert "word/document.xml" in archive.namelist()
