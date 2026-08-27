from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.real_costs import annualized_eac_wanyuan, storage_capex_wanyuan


ROOT = Path(__file__).resolve().parents[1]


def test_v3_real_e2e_entrypoint_writes_verified_formal_artifacts(tmp_path: Path) -> None:
    output = tmp_path / "real-2021-2025-contract-v3"
    command = [
        sys.executable,
        str(ROOT / "scripts/run_all.py"),
        "--dataset",
        "real_2021_2025",
        "--config",
        str(ROOT / "model_contract.yaml"),
        "--processed-dir",
        str(ROOT / "data/processed/real_2021_2025"),
        "--output-dir",
        str(output),
        "--skip-gen",
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr or result.stdout

    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["dataset_id"] == "real_2021_2025"
    # 3.1.0：严格方案起点为归一约定状态，跨口径 EAC 包含关系废止；机器标记固定为 False 并附口径说明。
    assert manifest["path_cost_inclusion_validated"] is False
    assert "归一约定" in manifest["path_comparison_note"]
    assert "跨口径增量比较" in manifest["path_comparison_note"]
    assert manifest["voltage_separation"] is True
    assert manifest["timeseries_grade_a_ready"] is True
    assert manifest["timeseries_formal_hourly_use_allowed"] is True
    assert manifest["time_physics_hard_gate_2025"] is True
    for voltage in (110, 35):
        matrix = pd.read_csv(output / f"county_{voltage}_recommendation_matrix.csv")
        assert len(matrix) == 8
        assert set(matrix["voltage_kv"]) == {voltage}
        assert {
            "recommended_clr_interval",
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
        } <= set(matrix.columns)
        assert not matrix["quality_flag"].astype(str).str.contains("mapping_pending").any()
    matrix_110 = pd.read_csv(output / "county_110_recommendation_matrix.csv")
    qx_110 = matrix_110[matrix_110["region_id"].eq("QX-00005")]
    assert len(qx_110) == 1
    assert qx_110.iloc[0]["evidence_grade"] == "EVIDENCE_A"
    assert float(qx_110.iloc[0]["reverse_peak_base_mw"]) > 0.0
    years = pd.read_csv(output / "path_year_results.csv")
    assert set(years["path_id"]) == {
        "PATH_ACTUAL_2021_2025",
        "PATH_OPT_CLR_UNBOUNDED",
        "PATH_OPT_CLR_LE_2",
    }
    actual = years[years["path_id"] == "PATH_ACTUAL_2021_2025"]
    assert len(actual) == 80
    assert set(actual["status"]) == {"fact"}
    strict = years[(years["path_id"] == "PATH_OPT_CLR_LE_2") & (years["status"] == "feasible")]
    assert (strict["clr"] <= 2.0 + 1e-9).all()
    optimization_years = years[
        years["path_id"].isin(
            ["PATH_OPT_CLR_UNBOUNDED", "PATH_OPT_CLR_LE_2"]
        )
    ]
    for _, group in optimization_years.groupby(
        ["path_id", "region_id", "voltage_kv"]
    ):
        assert len(group) == 4
        assert len(set(group["complete_path_status"])) == 1
        if group["complete_path_status"].iloc[0] == "feasible":
            assert set(group["status"]) == {"feasible"}
    actions = pd.read_csv(output / "path_action_results.csv")
    costs = pd.read_csv(output / "path_cost_breakdown.csv")
    contract = yaml.safe_load((ROOT / "model_contract.yaml").read_text(encoding="utf-8"))
    annualization = contract["costs"]["annualization"]
    storage_actions = actions[
        actions["path_id"].isin(
            ["PATH_OPT_CLR_UNBOUNDED", "PATH_OPT_CLR_LE_2"]
        )
        & actions["action_type"].eq("storage")
    ]
    for storage_action in storage_actions.itertuples(index=False):
        modules = int(storage_action.storage_modules_delta)
        expected_capex = storage_capex_wanyuan(modules, contract)
        expected_eac = annualized_eac_wanyuan(
            expected_capex,
            float(annualization["discount_rate"]),
            int(annualization["storage_life_years"]),
            float(annualization["storage_fixed_om_fraction_per_year"]),
        )
        assert float(storage_action.capex_wanyuan) == pytest.approx(expected_capex)
        assert float(storage_action.eac_wanyuan_per_year) == pytest.approx(expected_eac)
    baseline_capacity = actual[actual["year"].eq(2021)][
        ["region_id", "voltage_kv", "installed_capacity_mva"]
    ].rename(columns={"installed_capacity_mva": "base_capacity_mva"})
    optimization_costs = costs[
        costs["path_id"].isin(
            ["PATH_OPT_CLR_UNBOUNDED", "PATH_OPT_CLR_LE_2"]
        )
        & costs["status"].eq("feasible")
    ]
    for cost_row in optimization_costs.itertuples(index=False):
        group_years = years[
            years["path_id"].eq(cost_row.path_id)
            & years["region_id"].eq(cost_row.region_id)
            & years["voltage_kv"].eq(cost_row.voltage_kv)
        ].merge(
            baseline_capacity,
            on=["region_id", "voltage_kv"],
            how="left",
            validate="many_to_one",
        )
        group_actions = actions[
            actions["path_id"].eq(cost_row.path_id)
            & actions["region_id"].eq(cost_row.region_id)
            & actions["voltage_kv"].eq(cost_row.voltage_kv)
        ]
        expected_cumulative_eac = 0.0
        for year_row in group_years.sort_values("year").itertuples(index=False):
            in_service = group_actions[group_actions["year"].le(year_row.year)]
            commissioned = group_actions[group_actions["year"].eq(year_row.year)]
            expected_capacity = float(year_row.base_capacity_mva) + pd.to_numeric(
                in_service["delta_capacity_mva"], errors="coerce"
            ).fillna(0.0).sum()
            expected_modules = pd.to_numeric(
                in_service["storage_modules_delta"], errors="coerce"
            ).fillna(0.0).sum()
            expected_annual_capex = pd.to_numeric(
                commissioned["capex_wanyuan"], errors="coerce"
            ).fillna(0.0).sum()
            expected_annual_eac = pd.to_numeric(
                in_service["eac_wanyuan_per_year"], errors="coerce"
            ).fillna(0.0).sum()
            expected_cumulative_eac += expected_annual_eac

            assert year_row.installed_capacity_mva == pytest.approx(expected_capacity)
            assert year_row.storage_modules == pytest.approx(expected_modules)
            assert float(year_row.annual_capex_wanyuan) == pytest.approx(
                expected_annual_capex
            )
            assert float(year_row.annual_in_service_eac_wanyuan) == pytest.approx(
                expected_annual_eac
            )
            assert float(year_row.cumulative_in_service_eac_wanyuan) == pytest.approx(
                expected_cumulative_eac
            )
        assert float(
            group_years.sort_values("year").iloc[-1][
                "cumulative_in_service_eac_wanyuan"
            ]
        ) == pytest.approx(float(cost_row.cumulative_in_service_eac_wanyuan))
    assert not any("SCHEME_" in path.name for path in output.iterdir())

    physics = pd.read_csv(output / "path_physics_state_audit.csv")
    feasible_costs = costs[
        costs["path_id"].isin(
            ["PATH_OPT_CLR_UNBOUNDED", "PATH_OPT_CLR_LE_2"]
        )
        & costs["status"].eq("feasible")
    ][["path_id", "region_id", "voltage_kv"]]
    audited_feasible = physics[physics["status"].eq("feasible")][
        ["path_id", "region_id", "voltage_kv"]
    ]
    assert set(map(tuple, feasible_costs.to_numpy())) == set(
        map(tuple, audited_feasible.to_numpy())
    )
    assert physics.loc[physics["status"].eq("feasible"), "site_gate_passed"].all()
    assert physics.loc[physics["status"].eq("feasible"), "soc_gate_passed"].all()

    playback = pd.read_csv(output / "path_storage_dispatch_playback.csv.gz")
    assert not playback["physical_violation"].astype(bool).any()
    qx_playback = playback[
        playback["region_id"].eq("QX-00005")
        & playback["voltage_kv"].eq(110)
        & playback["profile_basis"].astype(str).str.contains("approved_2025_8760")
    ]
    assert not qx_playback.empty
    for path_id, group in qx_playback.groupby("path_id"):
        assert group["timestamp"].nunique() == 8760
        aggregate = group.groupby("timestamp", as_index=False)["net_load_after_mw"].sum()
        expected = years[
            years["path_id"].eq(path_id)
            & years["region_id"].eq("QX-00005")
            & years["voltage_kv"].eq(110)
            & years["year"].eq(2025)
        ]
        assert len(expected) == 1
        assert aggregate["net_load_after_mw"].max() == pytest.approx(
            float(expected.iloc[0]["p_plus_mw"]), abs=1e-6
        )
