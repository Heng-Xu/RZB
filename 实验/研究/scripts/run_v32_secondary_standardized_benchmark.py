#!/usr/bin/env python3
"""运行 S_norm_0=2×P_plus_2021 的二级标准化反事实基准。

该入口只生成标准化容量基准表，不调用主政策优化器，不形成客户成本结论，
也不写入 formal_matrix 或冻结主结果目录。
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.v32_contract import load_v32_contract


ROLE = "secondary_standardized_counterfactual_benchmark"
SCENARIO_ID = "S_NORM_2P_PLUS_2021"


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_secondary_standardized_benchmark(
    project_root: Path,
    processed_root: Path,
    output_dir: Path,
) -> dict[str, Any]:
    project_root = Path(project_root).resolve()
    processed_root = Path(processed_root).resolve()
    output_dir = Path(output_dir).resolve()
    contract = load_v32_contract(project_root)
    benchmark = contract["standardized_policy_benchmark"]
    if not benchmark.get("enabled"):
        raise ValueError("standardized secondary benchmark is disabled by contract")
    if benchmark.get("formula") != "S_norm_0 = 2.0 * P_plus_2021":
        raise ValueError("standardized benchmark formula is not frozen")
    if benchmark.get("direct_client_cost_conclusion_allowed") is not False:
        raise ValueError("secondary benchmark must not form a direct client cost conclusion")

    annual_path = processed_root / "annual_reference.csv"
    annual = pd.read_csv(annual_path)
    required = {"year", "region_id", "voltage_kv", "official_positive_peak_mw"}
    missing = required - set(annual.columns)
    if missing:
        raise ValueError(f"annual_reference.csv missing {sorted(missing)}")
    reference = annual[
        annual["year"].astype(int).eq(2021)
        & annual["voltage_kv"].astype(int).eq(110)
    ].copy()
    if reference.empty:
        raise ValueError("2021 110 kV annual reference is empty")
    peaks = pd.to_numeric(reference["official_positive_peak_mw"], errors="coerce")
    if peaks.isna().any() or (peaks <= 0).any():
        raise ValueError("2021 positive peak must be finite and positive")

    result = pd.DataFrame(
        {
            "region_id": reference["region_id"].astype(str),
            "voltage_kv": 110,
            "benchmark_year": 2021,
            "p_plus_2021_mw": peaks.to_numpy(dtype=float),
        }
    )
    result["s_norm_0_mva"] = 2.0 * result["p_plus_2021_mw"]
    result["formula"] = benchmark["formula"]
    result["role"] = ROLE
    result["primary_policy_model"] = False
    result["direct_client_cost_conclusion_allowed"] = False
    result["scenario_id"] = SCENARIO_ID
    result["source_ref"] = "data/processed/real_2021_2025/annual_reference.csv"
    result["source_version"] = str(reference["source_version"].iloc[0]) if "source_version" in reference else "processed_real_2021_2025"
    result["transformation"] = "S_norm_0 = 2.0 * synchronized 2021 positive peak; physical asset state remains separate"
    result["quality_flag"] = "secondary_counterfactual_not_primary_policy_model"
    result = result.sort_values("region_id", kind="stable").reset_index(drop=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "standardized_baseline.csv"
    result.to_csv(output_path, index=False, lineterminator="\n", float_format="%.10g")
    manifest = {
        "schema_version": "v3.2.secondary-standardized-benchmark.v1",
        "model_version": contract["contract"]["version"],
        "role": ROLE,
        "scenario_id": SCENARIO_ID,
        "enabled": True,
        "formula": benchmark["formula"],
        "primary_policy_model": False,
        "direct_client_cost_conclusion_allowed": False,
        "not_for_formal_matrix": True,
        "not_for_client_main_conclusion": True,
        "physical_asset_state_separate": True,
        "input_files": {
            "data/processed/real_2021_2025/annual_reference.csv": {
                "sha256": _sha256(annual_path),
                "bytes": annual_path.stat().st_size,
            }
        },
        "files": {
            "standardized_baseline.csv": {
                "sha256": _sha256(output_path),
                "bytes": output_path.stat().st_size,
            }
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path("results/runs/real-2021-2025-v32-secondary-standardized-benchmark"))
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    manifest = build_secondary_standardized_benchmark(
        project_root,
        project_root / "data/processed/real_2021_2025",
        args.output_root,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
