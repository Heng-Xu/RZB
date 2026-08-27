from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.real_costs import (
    V3CostError,
    build_real_cost_library,
    storage_capex_wanyuan,
    validate_integer_storage_schedule,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "model_contract.yaml"
PROCESSED = ROOT / "data/processed/real_2021_2025"


def _contract() -> dict:
    import yaml

    return yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))


def test_v3_cost_library_is_2025_price_year_and_keeps_discrete_source_candidates(tmp_path: Path) -> None:
    manifest = build_real_cost_library(PROCESSED, tmp_path, CONTRACT)
    expansion = pd.read_csv(tmp_path / "expansion_cost_library.csv")
    assert manifest["dataset_id"] == "real_2021_2025"
    assert manifest["price_year"] == 2025
    assert expansion["candidate_id"].is_unique
    assert set(expansion["candidate_type"]) <= {
        "new_third_transformer",
        "replacement_or_uprating",
        "new_station",
        "line_or_bay_project",
    }
    assert not (expansion["capex_center_wanyuan"] == 800.0).any()
    assert set(expansion["scenario_id"]) == {"real_2021_2025_cost_library"}
    assert {"source_ref", "source_sha256", "quality_flag"} <= set(expansion.columns)


def test_storage_cost_blocks_and_no_continuous_module_counts() -> None:
    contract = _contract()
    assert storage_capex_wanyuan(1, contract) == pytest.approx(27.2)
    assert storage_capex_wanyuan(10, contract) == pytest.approx(210.456262)
    assert storage_capex_wanyuan(11, contract) == pytest.approx(237.656262)
    with pytest.raises(ValueError):
        storage_capex_wanyuan(1.5, contract)


def test_integer_storage_schedule_enforces_soc_cycle_and_local_direction() -> None:
    contract = _contract()
    modules = 10
    actual = [-0.5, 1.0] + [0.0] * 22
    charge = [0.1, 0.0] + [0.0] * 22
    discharge = [0.0, 0.09025] + [0.0] * 22
    soc = [1.095, 1.0] + [1.0] * 22
    audit = validate_integer_storage_schedule(actual, charge, discharge, soc, modules, contract)
    assert audit["feasible"] is True
    assert audit["daily_soc_residual_mwh"] == pytest.approx(0.0, abs=1e-9)

    with pytest.raises(V3CostError, match="cross zero"):
        validate_integer_storage_schedule(
            [-0.1] + [0.0] * 23,
            [0.2] + [0.0] * 23,
            [0.0] * 24,
            [1.0] * 24,
            modules,
            contract,
        )
    with pytest.raises(V3CostError, match="export"):
        validate_integer_storage_schedule(
            [0.1] + [0.0] * 23,
            [0.0] * 24,
            [0.2] + [0.0] * 23,
            [1.0] * 24,
            modules,
            contract,
        )
