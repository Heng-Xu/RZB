from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd

from src.v3_outputs import write_transposed_word_matrix


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed/real_2021_2025"


def _review_matrix() -> pd.DataFrame:
    regions = [f"QX-{index:05d}" for index in (1, 3, 4, 5, 7, 8, 9, 10)]
    row = {
        "voltage_kv": 110,
        "evidence_grade": "EVIDENCE_B",
        "asset_scope_id": "operating_2025",
        "recommended_clr_interval": "本规划期Rcap不构成有效约束",
        "recommended_clr_center": "不适用",
        "recommended_clr_interval_effective_samples": 0,
        "recommended_clr_interval_method": "不输出数值推荐",
        "capacity_base_mva": 100.0,
        "positive_peak_base_mw": 50.0,
        "reverse_peak_base_mw": "未形成同步反向峰值",
        "strict_path_incremental_cost": "未形成直接比较",
        "positive_capacity_gap_mw": 0.0,
        "reverse_hosting_gap_mw": 0.0,
        "positive_gap_device_count": 0,
        "reverse_gap_device_count": 0,
        "measure_trigger_constraint": "none",
        "recommended_measure": "无",
    }
    for path in ("PATH_ACTUAL_2021_2025", "PATH_OPT_CLR_UNBOUNDED", "PATH_OPT_CLR_LE_2"):
        row[f"{path}_clr_2025"] = 2.0
        row[f"{path}_cumulative_eac"] = 0.0
    return pd.DataFrame([{**row, "region_id": region} for region in regions])


def test_v32_review_data_keeps_two_eight_region_matrices() -> None:
    reference = pd.read_csv(PROCESSED / "annual_reference.csv")
    for voltage in (110, 35):
        frame = reference[(reference.year == 2025) & (reference.voltage_kv == voltage)]
        assert len(frame) == 8
        assert frame.region_id.astype(str).str.fullmatch(r"QX-\d{5}").all()
    assert not reference.astype(str).apply(
        lambda column: column.str.contains("P50|P90", case=False, regex=True).any()
    ).any()


def test_v32_word_review_layer_uses_codes_and_r_cap_labels(tmp_path: Path) -> None:
    path = tmp_path / "matrix.docx"
    write_transposed_word_matrix(_review_matrix(), path, title="110 kV 县区正式推荐矩阵")
    with zipfile.ZipFile(path) as archive:
        document = archive.read("word/document.xml").decode("utf-8")
    assert "QX-00001" in document
    assert "片区01" not in document
    assert "推荐 Rcap 区间" in document
    assert "110 kV 县区正式推荐矩阵" in document
