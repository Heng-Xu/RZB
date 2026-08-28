from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src import v32_actual_pipeline, v32_model, v32_pipeline
from scripts.build_v32_formal_outputs import classify_recommendation_type

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_formal_v32_entrypoint_delegates_to_actual_asset_pipeline(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen: dict[str, Path] = {}

    def fake_run(
        project_root: Path, processed_root: Path, run_dir: Path
    ) -> dict[str, str]:
        seen["project_root"] = Path(project_root)
        seen["processed_root"] = Path(processed_root)
        seen["run_dir"] = Path(run_dir)
        return {"model_role": "primary_actual_asset_grandfathered_incremental_rcap"}

    monkeypatch.setattr(v32_actual_pipeline, "run_v32_actual_baseline", fake_run)
    result = v32_pipeline.run_v32_pipeline(
        tmp_path / "project",
        tmp_path / "processed",
        tmp_path / "run",
    )

    assert result["model_role"] == "primary_actual_asset_grandfathered_incremental_rcap"
    assert seen["run_dir"] == tmp_path / "run"


def test_common_planning_baseline_is_the_2021_actual_asset_state(
    tmp_path: Path,
) -> None:
    pd.DataFrame(
        [
            {
                "year": 2021,
                "region_id": "QX-A",
                "voltage_kv": 110,
                "official_positive_peak_mw": 40.0,
            }
        ]
    ).to_csv(tmp_path / "annual_reference.csv", index=False)
    annual = pd.DataFrame(
        [
            {
                "year": 2022,
                "region_id": "QX-A",
                "voltage_kv": 110,
                "baseline_capacity_mva": 100.0,
                "positive_peak_mw": 30.0,
            }
        ]
    )

    result = v32_model.apply_common_planning_baseline(annual, tmp_path)

    assert result["planning_baseline_capacity_mva"].tolist() == pytest.approx(
        [100.0]
    )
    assert result["reported_baseline_capacity_mva"].tolist() == pytest.approx(
        [100.0]
    )


def test_formal_recommendation_classification_does_not_force_rcap_value() -> None:
    assert (
        classify_recommendation_type(
            110,
            elastic_feasible=True,
            threshold_status="binding_threshold_bracketed",
        )
        == "经济释放阈值型"
    )
    assert (
        classify_recommendation_type(
            110,
            elastic_feasible=True,
            threshold_status="non_binding_not_identified_in_horizon",
        )
        == "当前不绑定型"
    )
    assert (
        classify_recommendation_type(
            110,
            elastic_feasible=False,
            threshold_status="not_formed_physical_infeasible",
        )
        == "技术约束优先型"
    )
    assert classify_recommendation_type(35, elastic_feasible=True, threshold_status=None) == "辅助层不施加逐年Rcap"


def test_formal_baseline_workflow_reads_only_entrypoint_outputs() -> None:
    workflow = (
        PROJECT_ROOT / ".github/workflows/v32-formal-baseline.yml"
    ).read_text(encoding="utf-8")

    for filename in (
        "policy_cost_comparison.csv",
        "policy_2025_summary.csv",
    ):
        assert (
            f"cat results/runs/real-2021-2025-contract-v32-candidate/{filename}"
            in workflow
        )
    assert (
        "p='results/runs/real-2021-2025-contract-v32-candidate/"
        "qx00005_chronology_comparison.csv'"
        in workflow
    )
    assert "recommendation_matrix_v32_base.csv" not in workflow
