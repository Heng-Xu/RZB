from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from src.v32_contract import V32ContractError, load_v32_contract


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_STATUS = "approved_for_2025_qx00005_110kv_operating_scope"
EXPECTED_FRONTIER_FIELDS = [
    "rcap",
    "region_id",
    "cumulative_in_service_eac_wanyuan",
    "physical_clr_2025",
    "storage_modules",
    "capacity_action_delta_mva",
    "feasible",
]


def _yaml(name: str) -> dict:
    return yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))


def test_timeseries_contract_matches_scoped_formal_gate_and_approval_rows() -> None:
    contract = load_v32_contract(ROOT)
    timeseries = contract["data"]["timeseries"]
    manifest = json.loads(
        (ROOT / "data/processed/real_2021_2025/manifest.json").read_text(
            encoding="utf-8"
        )
    )
    gate = manifest["timeseries_gate"]
    approval = pd.read_csv(
        ROOT / "data/processed/real_2021_2025/timeseries_mapping_approval.csv"
    )

    assert timeseries["current_status"] == EXPECTED_STATUS
    assert timeseries["formal_scope_id"] == gate["formal_scope_id"]
    assert timeseries["formal_hourly_use_allowed"] is gate["formal_hourly_use_allowed"] is True
    assert timeseries["grade_a_ready"] is gate["grade_a_ready"] is True
    assert timeseries["formal_scope_approved_transformers"] == 40
    assert timeseries["formal_scope_required_transformers"] == 40
    assert int(approval["formal_use_allowed"].astype(bool).sum()) == 40
    assert not approval.loc[approval["transformer_uid"].str.contains("\\|35\\|"), "formal_use_allowed"].astype(bool).any()
    assert int(approval["approval_status"].eq("rejected").sum()) == 2


def test_base_overlay_and_resolved_use_one_frontier_schema() -> None:
    base = _yaml("model_contract.yaml")
    overlay = _yaml("model_contract_v3_2_overlay.yaml")
    resolved = load_v32_contract(ROOT)
    assert base["elasticity_sweep"]["output"]["fields"] == EXPECTED_FRONTIER_FIELDS
    if "elasticity_sweep" in overlay:
        assert overlay["elasticity_sweep"]["output"]["fields"] == EXPECTED_FRONTIER_FIELDS
    assert resolved["elasticity_sweep"]["output"]["fields"] == EXPECTED_FRONTIER_FIELDS


def test_loader_rejects_semantic_drift_in_overlay(tmp_path: Path) -> None:
    base = _yaml("model_contract.yaml")
    overlay = _yaml("model_contract_v3_2_overlay.yaml")
    overlay.setdefault("elasticity_sweep", {}).setdefault("output", {})["fields"] = [
        "rcap",
        "expansion_mva",
    ]
    (tmp_path / "model_contract.yaml").write_text(
        yaml.safe_dump(base, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    (tmp_path / "model_contract_v3_2_overlay.yaml").write_text(
        yaml.safe_dump(overlay, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    with pytest.raises(V32ContractError, match="semantic drift"):
        load_v32_contract(tmp_path)
