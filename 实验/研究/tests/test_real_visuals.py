from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from src.v3_pipeline import run_v3_pipeline


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed/real_2021_2025"
CONTRACT = ROOT / "model_contract.yaml"


@pytest.fixture(scope="module")
def release(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    output = tmp_path_factory.mktemp("real_v3_visual_review")
    return output, run_v3_pipeline(ROOT, PROCESSED, output, CONTRACT)


def test_v3_review_data_keeps_two_eight_region_matrices(release: tuple[Path, dict]) -> None:
    output, _ = release
    frames = [pd.read_csv(output / f"county_{voltage}_recommendation_matrix.csv") for voltage in (110, 35)]
    assert [len(frame) for frame in frames] == [8, 8]
    assert [set(frame.voltage_kv) for frame in frames] == [{110}, {35}]
    assert all(frame.region_id.str.fullmatch(r"QX-\d{5}").all() for frame in frames)
    assert all(not frame.astype(str).apply(lambda column: column.str.contains("P50|P90", case=False, regex=True).any()).any() for frame in frames)


def test_v3_review_package_uses_csv_as_exact_source_and_word_as_review_layer(
    release: tuple[Path, dict],
) -> None:
    output, manifest = release
    assert manifest["dataset_id"] == "real_2021_2025"
    assert manifest["contract_version"] == "3.1.0"
    for voltage in (110, 35):
        csv_path = output / f"county_{voltage}_recommendation_matrix.csv"
        docx_path = output / f"county_{voltage}_recommendation_matrix.docx"
        assert csv_path.name in manifest["output_files"]
        assert docx_path.is_file()
        with zipfile.ZipFile(docx_path) as archive:
            assert "word/document.xml" in archive.namelist()
            document = archive.read("word/document.xml").decode("utf-8")
            assert "片区01" in document
            if voltage == 110:
                assert "正式推荐" in document
            else:
                assert "辅助分析" in document
                assert "不可行的片区不形成正式唯一推荐" in document
    saved = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert saved["voltage_separation"] is True
