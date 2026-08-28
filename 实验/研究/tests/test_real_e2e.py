from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed/real_2021_2025"


def test_real_2021_2025_cli_writes_v32_auditable_baseline(tmp_path: Path) -> None:
    run_dir = tmp_path / "real-2021-2025-v32"
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
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=3600)
    assert result.returncode == 0, result.stderr or result.stdout

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["model_version"] == "3.2.0"
    assert manifest["dataset_id"] == "real_2021_2025"
    assert manifest["common_physical_baseline"] == "actual_2021_installed_capacity"
    assert manifest["direct_policy_cost_comparison_allowed"] is True
    assert manifest["retirement_candidates_enabled"] is False
    assert manifest["timeseries_formal_hourly_use_allowed"] is True
    assert manifest["initial_physical_diagnostics"]["rows"] == 16

    years = pd.read_csv(run_dir / "policy_path_year_results.csv")
    assert len(years) == 128
    assert set(years["path_id"]) == {
        "PATH_OPT_CLR_UNBOUNDED",
        "PATH_OPT_CLR_LE_2",
    }
    strict = years[
        (years.path_id == "PATH_OPT_CLR_LE_2")
        & (years.voltage_kv == 110)
        & years.status.eq("feasible")
    ]
    assert (strict["policy_control_ratio"] <= 2.0 + 1e-9).all()
    # 2021 存量豁免意味着物理 CLR 可以高于规划控制参数；两者必须分别留档。
    qx1 = strict[(strict.region_id == "QX-00001") & (strict.year == 2025)].iloc[0]
    assert qx1.physical_clr > 2.0
    assert qx1.policy_control_ratio <= 2.0 + 1e-9

    actual = pd.read_csv(run_dir / "actual_path_year_results.csv")
    assert len(actual) == 80
    assert set(actual["status"]) == {"fact"}
    assert not any("SCHEME_" in path.name for path in run_dir.iterdir())

    soc = pd.read_csv(run_dir / "qx00005_soc/qx00005_continuous_soc_summary.csv")
    assert len(soc) == 40
    as_bool = lambda series: series.astype(str).str.lower().eq("true")
    assert as_bool(soc["feasible"]).all()
    assert not as_bool(soc["soc_bounds_violation"]).any()
    assert not as_bool(soc["cross_zero_violation"]).any()
    assert not as_bool(soc["simultaneous_charge_discharge_violation"]).any()
    assert not as_bool(soc["physical_violation"]).any()
