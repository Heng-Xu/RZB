from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "model_contract.yaml"
PROCESSED = ROOT / "data/processed/real_2021_2025"


def _contract() -> dict:
    return yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_storage_module_cost_uses_ten_module_blocks_at_all_boundaries() -> None:
    from src.real_costs import storage_capex_wanyuan

    contract = _contract()
    assert storage_capex_wanyuan(0, contract) == 0.0
    assert storage_capex_wanyuan(1, contract) == pytest.approx(27.2)
    assert storage_capex_wanyuan(10, contract) == pytest.approx(210.456262)
    assert storage_capex_wanyuan(11, contract) == pytest.approx(237.656262)
    assert storage_capex_wanyuan(20, contract) == pytest.approx(420.912524)
    with pytest.raises(ValueError):
        storage_capex_wanyuan(1.5, contract)


def test_crf_and_eac_match_hand_calculation() -> None:
    from src.real_costs import annualized_eac_wanyuan, capital_recovery_factor

    crf = 0.06 * 1.06**10 / (1.06**10 - 1)
    assert capital_recovery_factor(0.06, 10) == pytest.approx(crf)
    assert annualized_eac_wanyuan(100.0, 0.06, 10, 0.03) == pytest.approx(
        100.0 * (crf + 0.03)
    )


def test_cost_library_keeps_discrete_candidates_and_explicit_ranges(tmp_path: Path) -> None:
    from src.real_costs import build_real_cost_library

    manifest = build_real_cost_library(PROCESSED, tmp_path, CONTRACT_PATH)
    expansion = pd.read_csv(tmp_path / "expansion_cost_library.csv")
    original = pd.read_csv(PROCESSED / "expansion_candidates.csv")
    assert len(expansion) == len(original)
    assert expansion["candidate_id"].is_unique
    assert (expansion["source_row"] > 0).all()
    assert set(expansion["candidate_id"]) == set(original["candidate_id"])
    assert not (expansion["capex_center_wanyuan"] == 800.0).any()
    unmatched = expansion[expansion["new_capacity_mva"].isin([63.0, 80.0, 100.0])]
    assert unmatched["capex_center_wanyuan"].isna().all()
    assert (unmatched["capex_high_wanyuan"] > unmatched["capex_low_wanyuan"]).all()
    assert manifest["model_assumption_gate"] == "explicit"


def test_replacement_candidates_use_net_increment_not_new_rating(tmp_path: Path) -> None:
    from src.real_costs import build_real_cost_library

    build_real_cost_library(PROCESSED, tmp_path, CONTRACT_PATH)
    expansion = pd.read_csv(tmp_path / "expansion_cost_library.csv")
    replacement = expansion[expansion["candidate_type"] == "replacement_or_uprating"]
    if not replacement.empty:
        assert replacement["delta_capacity_mva"].to_numpy() == pytest.approx(
            (replacement["new_capacity_mva"] - replacement["old_capacity_mva"]).to_numpy()
        )


def test_cost_outputs_include_eac_ranges_assumptions_and_lineage(tmp_path: Path) -> None:
    from src.real_costs import build_real_cost_library

    build_real_cost_library(PROCESSED, tmp_path, CONTRACT_PATH)
    expansion = pd.read_csv(tmp_path / "expansion_cost_library.csv")
    storage = pd.read_csv(tmp_path / "storage_module_cost_boundaries.csv")
    assumptions = pd.read_csv(tmp_path / "cost_assumptions.csv")
    assert {0, 1, 10, 11, 20} == set(storage["storage_modules"])
    one = storage.set_index("storage_modules").loc[1]
    assert one["capex_low_wanyuan"] == pytest.approx(0.9789 * 215_000 / 10_000)
    assert one["capex_high_wanyuan"] == pytest.approx(1.2651 * 215_000 / 10_000)
    assert {
        "eac_low_wanyuan_per_year",
        "eac_high_wanyuan_per_year",
        "source_ref",
        "source_sha256",
        "quality_flag",
    } <= set(expansion.columns)
    costed = expansion.dropna(
        subset=["eac_low_wanyuan_per_year", "eac_high_wanyuan_per_year"]
    )
    assert (costed["eac_high_wanyuan_per_year"] >= costed["eac_low_wanyuan_per_year"]).all()
    assert expansion.loc[expansion["capex_low_wanyuan"].isna(), "cost_status"].eq(
        "cost_gap_not_optimizable"
    ).all()
    assert set(assumptions["evidence_type"]) == {
        "model_assumptions_requiring_sensitivity"
    }
