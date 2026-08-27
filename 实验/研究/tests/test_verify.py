"""Task 7 tests: 校核层(verify_flow_n1 / verify_dlt2041)。

断言取自 task-7-brief.md Step 1;并对 solution_B.json 跑通两器、落盘
results/runs/synthetic-m1/verify_flow.csv 与 verify_dlt2041.csv 作为完成判据。
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.io_loader import load_scenario
from src.milp_planner import SolutionBundle
from src.verify_dlt2041 import county_check, device_level, s_dev_max
from src.verify_flow_n1 import build_synthetic_grid, run_n1

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "results" / "runs" / "synthetic-m1"

_data = load_scenario(ROOT, track="synthetic")


def _load_solution(scheme: str) -> dict:
    with open(RUN_DIR / f"solution_{scheme}.json", encoding="utf-8") as f:
        return json.load(f)


_solution_b = _load_solution("B")


def _as_bundle(sol: dict) -> SolutionBundle:
    """把 json dict 包成 SolutionBundle,验证 run_n1/device_level 接受两种输入。"""
    return SolutionBundle(
        scheme=sol["scheme"], status=sol["status"], total_cost=sol["total_cost_wanyuan_per_year"],
        ess_mw=pd.Series(sol["ess_mw"]), ess_mwh=pd.Series(sol["ess_mwh"]),
        alpha=pd.DataFrame(sol["alpha"]), expand_mva=pd.Series(sol["expand_mva"]),
        curtail_mwh=sol["curtail_mwh"], r_after=pd.Series(sol["r_after"]),
        shadow_r=sol["shadow_r_wan_per_0.1R"],
    )


_bundle_b = _as_bundle(_solution_b)


def test_run_n1_row_count_matches_elements_x_snapshots():
    """行数 == 元件数(每回线路,含多回按 n_channels 拆分 + 每台主变) × 断面数。"""
    graph = build_synthetic_grid(_data)
    n_lines = sum(attrs["n_channels"] for _, _, attrs in graph.edges(data=True))
    n_xfmr = sum(len(st.transformers) for st in _data.stations.values())
    snapshots = [0, 4000]
    df = run_n1(_data, _solution_b, snapshots=snapshots)
    assert list(df.columns) == ["element_id", "snapshot", "loading_pct"]
    assert len(df) == (n_lines + n_xfmr) * len(snapshots)


def test_run_n1_default_snapshots_are_annual_peaks():
    df = run_n1(_data, _solution_b)
    assert df["snapshot"].nunique() == 2
    total = _data.pnet.sum(axis=1)
    expected = {int(total.values.argmax()), int(total.values.argmin())}
    assert set(df["snapshot"].unique()) == expected
    assert (df["loading_pct"] >= 0).all()


def test_device_level_manual_check():
    """手算对照(brief):cap=100,β=0.8,τ=0.95,无储能,P_load=30
    → (30−0+0+100×0.95×0.8)/0.95 = 111.578947..."""
    val = s_dev_max(p_load=30.0, p_g=0.0, p_ess=0.0, s_r=100.0,
                     cos_phi=0.95, beta=0.8, tau=0.95)
    assert val == pytest.approx(111.578947, rel=1e-6)


def test_device_level_columns_and_structure():
    df = device_level(_data, _solution_b)
    assert list(df.columns) == ["s_dev_max_mw", "pv_installed_mw", "margin_mw"]
    assert set(df.index) == set(_data.stations)
    assert df["margin_mw"].to_numpy() == pytest.approx(
        (df["s_dev_max_mw"] - df["pv_installed_mw"]).to_numpy()
    )


def test_county_check_columns_and_min_logic():
    df = county_check(_data, _solution_b)
    assert list(df.columns) == [
        "s_system_mw", "s_device_mw", "s_final_mw", "pv_installed_mw", "open_capacity_mw",
    ]
    assert (df["s_final_mw"] <= df["s_system_mw"] + 1e-9).all()
    assert (df["s_final_mw"] <= df["s_device_mw"] + 1e-9).all()
    assert (df["open_capacity_mw"] >= -1e-9).all()


def test_accepts_solutionbundle_same_as_dict():
    """solution 参数接受 dict 或 SolutionBundle,结果应一致。"""
    df_dict = run_n1(_data, _solution_b, snapshots=[0, 4000])
    df_bundle = run_n1(_data, _bundle_b, snapshots=[0, 4000])
    pd.testing.assert_frame_equal(df_dict, df_bundle)

    dev_dict = device_level(_data, _solution_b)
    dev_bundle = device_level(_data, _bundle_b)
    pd.testing.assert_frame_equal(dev_dict, dev_bundle)


def test_full_flow_solution_b_writes_verify_csv():
    """完成判据:对方案B解跑通两器,落盘 verify_flow.csv 与 verify_dlt2041.csv。"""
    flow_df = run_n1(_data, _solution_b)
    dev_df = device_level(_data, _solution_b).rename_axis("entity_id").reset_index()
    dev_df.insert(0, "level", "station")
    cty_df = county_check(_data, _solution_b).rename_axis("entity_id").reset_index()
    cty_df.insert(0, "level", "county")
    combined = pd.concat([dev_df, cty_df], ignore_index=True, sort=False)

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    flow_df.to_csv(RUN_DIR / "verify_flow.csv", index=False)
    combined.to_csv(RUN_DIR / "verify_dlt2041.csv", index=False)

    assert (RUN_DIR / "verify_flow.csv").exists()
    assert (RUN_DIR / "verify_dlt2041.csv").exists()
    assert len(pd.read_csv(RUN_DIR / "verify_flow.csv")) == len(flow_df)
