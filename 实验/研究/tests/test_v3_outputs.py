from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.v3_outputs import build_v3_artifacts, write_transposed_word_matrix


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "model_contract.yaml"


def _matrix(voltage: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region_id": [f"QX-{index:05d}" for index in range(1, 9)],
            "voltage_kv": [voltage] * 8,
            "evidence_grade": ["EVIDENCE_B"] * 8,
            "asset_scope_id": ["operating_2025"] * 8,
            "recommended_clr_interval": ["2.0–2.0"] * 8,
            "recommended_clr_center": [2.0] * 8,
            "recommended_clr_interval_effective_samples": [3] * 8,
            "recommended_clr_interval_method": [
                "不限制容载比成本最小可行结果+cos_phi敏感性（0.90、0.95、1.00）"
            ] * 8,
            "capacity_base_mva": [100.0] * 8,
            "positive_peak_base_mw": [50.0] * 8,
            "reverse_peak_base_mw": ["未形成同步反向峰值"] * 8,
            "PATH_ACTUAL_2021_2025_clr_2025": [2.0] * 8,
            "PATH_OPT_CLR_UNBOUNDED_clr_2025": [2.0] * 8,
            "PATH_OPT_CLR_LE_2_clr_2025": [2.0] * 8,
            "PATH_ACTUAL_2021_2025_cumulative_eac": ["未识别"] * 8,
            "PATH_OPT_CLR_UNBOUNDED_cumulative_eac": [0.0] * 8,
            "PATH_OPT_CLR_LE_2_cumulative_eac": [1.0] * 8,
            "strict_path_incremental_cost": [1.0] * 8,
            "positive_capacity_gap_mw": [0.0] * 8,
            "reverse_hosting_gap_mw": [0.0] * 8,
            "positive_gap_device_count": [0] * 8,
            "reverse_gap_device_count": [0] * 8,
            "measure_trigger_constraint": ["none"] * 8,
            "recommended_measure": ["无"] * 8,
            "source_ref": ["test"] * 8,
            "source_version": ["test"] * 8,
            "transformation": ["test"] * 8,
            "scenario_id": ["real_2021_2025"] * 8,
            "quality_flag": ["test"] * 8,
            "source_sha256": ["test"] * 8,
        }
    )


def test_transposed_word_matrix_uses_indicator_rows_and_anonymized_region_columns(tmp_path: Path) -> None:
    path = tmp_path / "matrix.docx"
    write_transposed_word_matrix(_matrix(110), path, title="110 kV 正式推荐矩阵")
    assert path.is_file()
    import zipfile

    with zipfile.ZipFile(path) as archive:
        document = archive.read("word/document.xml").decode("utf-8")
    assert "指标" in document
    assert "片区01" in document
    assert "QX-00001" not in document


def test_word_matrix_uses_v3_presentation_contract(tmp_path: Path) -> None:
    path = tmp_path / "matrix.docx"
    matrix = _matrix(110)
    matrix.loc[0, "recommended_measure"] = "storage"
    matrix.loc[1, "recommended_measure"] = "new_third_transformer"
    matrix["PATH_OPT_CLR_LE_2_clr_2025"] = matrix["PATH_OPT_CLR_LE_2_clr_2025"].astype(object)
    matrix.loc[2, "PATH_OPT_CLR_LE_2_clr_2025"] = "不可行"
    write_transposed_word_matrix(matrix, path, title="110 kV 县区正式推荐矩阵")

    import zipfile

    with zipfile.ZipFile(path) as archive:
        assert "word/styles.xml" in archive.namelist()
        assert "word/footer1.xml" in archive.namelist()
        document = archive.read("word/document.xml").decode("utf-8")
    assert 'w:orient="landscape"' in document
    assert "110 kV 县区正式推荐矩阵" in document
    assert "口径与推荐结论" in document
    assert document.count('<w:gridSpan w:val="9"/>') == 6
    assert document.count("<w:tbl>") == 1
    assert "2025 年容载比｜不限制容载比优化" in document
    assert "储能" in document
    assert "新建第三台主变" in document
    assert "不可行" in document
    assert "未识别（设备动作成本未闭合）" in document
    assert "PATH_OPT_CLR_UNBOUNDED" not in document
    assert "storage" not in document
    assert "new_third_transformer" not in document
    assert "QX-00001" not in document
    assert "styles.xml" not in document


def test_build_v3_artifacts_writes_two_matrices_appendices_word_and_manifest(tmp_path: Path) -> None:
    path_year = pd.DataFrame(
        {
            "path_id": ["PATH_OPT_CLR_UNBOUNDED"],
            "year": [2025],
            "region_id": ["QX-00005"],
            "voltage_kv": [110],
            "status": ["feasible"],
            "clr": [2.0],
        }
    )
    actions = pd.DataFrame(
        {
            "path_id": ["PATH_OPT_CLR_LE_2"],
            "year": [2022],
            "region_id": ["QX-00005"],
            "voltage_kv": [110],
            "action_type": ["retirement"],
        }
    )
    costs = pd.DataFrame(
        {
            "path_id": ["PATH_OPT_CLR_UNBOUNDED", "PATH_OPT_CLR_LE_2"],
            "region_id": ["QX-00005", "QX-00005"],
            "voltage_kv": [110, 110],
            "cumulative_in_service_eac_wanyuan": [0.0, 1.0],
        }
    )
    manifest = build_v3_artifacts(
        tmp_path,
        _matrix(110),
        _matrix(35),
        path_year,
        actions,
        costs,
        CONTRACT,
        problem_log="mapping approval pending",
    )
    required = {
        "county_110_recommendation_matrix.csv",
        "county_35_recommendation_matrix.csv",
        "county_110_recommendation_matrix.docx",
        "county_35_recommendation_matrix.docx",
        "qx00005_path_validation.csv",
        "path_year_results.csv",
        "path_action_results.csv",
        "path_cost_breakdown.csv",
        "内部容量网络压力检查.csv",
        "问题台账.md",
        "manifest.json",
    }
    assert required <= {path.name for path in tmp_path.iterdir()}
    saved = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert saved["dataset_id"] == "real_2021_2025"
    assert saved["formal_matrices"]["110kv_rows"] == 8
    assert saved["word_presentation_version"] == "3.1"
    assert manifest["output_files"]
