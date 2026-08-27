from __future__ import annotations

import pandas as pd
import pytest

from src.v32_physics import build_station_gap_diagnostics


def _contract() -> dict:
    return {
        "technical_parameters": {
            "cos_phi": {"baseline": 1.0},
            "reverse_beta": {"split_or_single": 0.8},
        }
    }


def _write_inputs(tmp_path, *, operation_mode: str) -> None:
    pd.DataFrame(
        [
            {
                "transformer_uid": "T1",
                "region_id": "QX-A",
                "voltage_kv": 110,
                "station_id": "S1",
                "capacity_mva": 50.0,
                "operation_mode": operation_mode,
            },
            {
                "transformer_uid": "T2",
                "region_id": "QX-A",
                "voltage_kv": 110,
                "station_id": "S1",
                "capacity_mva": 50.0,
                "operation_mode": operation_mode,
            },
        ]
    ).to_csv(tmp_path / "transformer_master.csv", index=False)
    pd.DataFrame(
        [
            {
                "year": 2025,
                "asset_scope_id": "operating_2025",
                "transformer_uid": "T1",
                "in_annual_operating_whitelist": True,
            },
            {
                "year": 2025,
                "asset_scope_id": "operating_2025",
                "transformer_uid": "T2",
                "in_annual_operating_whitelist": True,
            },
        ]
    ).to_csv(tmp_path / "annual_asset_whitelist.csv", index=False)
    pd.DataFrame(
        [
            {
                "region_id": "QX-A",
                "voltage_kv": 110,
                "station_id": "S1",
                "annual_max_net_load_mw": 90.0,
                "annual_min_net_load_mw": -60.0,
            }
        ]
    ).to_csv(tmp_path / "station_static_load.csv", index=False)


def test_parallel_reverse_limit_uses_station_group_nminus1_lower_bound(tmp_path) -> None:
    _write_inputs(tmp_path, operation_mode="parallel")
    station, summary = build_station_gap_diagnostics(tmp_path, _contract())
    row = station.iloc[0]
    assert row["forward_limit_mw"] == pytest.approx(100.0)
    # 两台50 MVA并列，反向有效beta=min(0.8,(100-50)/100)=0.5。
    assert row["reverse_limit_mw"] == pytest.approx(50.0)
    assert row["reverse_gap_mw"] == pytest.approx(10.0)
    assert summary.iloc[0]["measure_trigger_constraint"] == "reverse_hosting_gap"


def test_split_mode_uses_beta_times_total_capacity(tmp_path) -> None:
    _write_inputs(tmp_path, operation_mode="split")
    station, summary = build_station_gap_diagnostics(tmp_path, _contract())
    row = station.iloc[0]
    assert row["reverse_limit_mw"] == pytest.approx(80.0)
    assert row["reverse_gap_mw"] == pytest.approx(0.0)
    assert summary.iloc[0]["measure_trigger_constraint"] == "none"


def test_beta_sensitivity_changes_reverse_limit_without_touching_clr_definition(tmp_path) -> None:
    _write_inputs(tmp_path, operation_mode="split")
    station, _summary = build_station_gap_diagnostics(
        tmp_path,
        _contract(),
        reverse_beta=0.6,
    )
    assert station.iloc[0]["reverse_limit_mw"] == pytest.approx(60.0)
    assert station.iloc[0]["reverse_beta"] == pytest.approx(0.6)
