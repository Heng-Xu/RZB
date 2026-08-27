from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed/real_2021_2025"


def test_real_2021_2025_single_command_writes_v3_release_artifacts(tmp_path: Path) -> None:
    run_dir = tmp_path / "real-2021-2025-v3"
    command = [
        sys.executable,
        str(ROOT / "scripts/run_all.py"),
        "--dataset",
        "real_2021_2025",
        "--config",
        str(ROOT / "model_contract.yaml"),
        "--processed-dir",
        str(PROCESSED),
        "--output-dir",
        str(run_dir),
        "--skip-gen",
    ]
    # v3.1.0 恢复容载比上限弹性扫描（Rcap 1.5~3.0 × 八片区）后，端到端时长超出旧 600 秒预算。
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=3600)
    assert result.returncode == 0, result.stderr or result.stdout
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["dataset_id"] == "real_2021_2025"
    assert manifest["contract_version"] == "3.1.0"
    # 3.1.0：严格方案起点为归一约定状态，跨口径 EAC 包含关系废止；机器标记固定为 False 并附口径说明。
    assert manifest["path_cost_inclusion_validated"] is False
    assert "归一约定" in manifest["path_comparison_note"]
    assert "跨口径增量比较" in manifest["path_comparison_note"]
    assert {"county_110_recommendation_matrix.csv", "county_35_recommendation_matrix.csv", "问题台账.md"} <= set(manifest["output_files"])
    years = pd.read_csv(run_dir / "path_year_results.csv")
    strict = years[(years.path_id == "PATH_OPT_CLR_LE_2") & years.status.eq("feasible")]
    assert (strict.clr <= 2.0 + 1e-9).all()
    assert not any("SCHEME_" in path.name for path in run_dir.iterdir())
