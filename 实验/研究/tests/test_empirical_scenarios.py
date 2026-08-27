from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src import io_loader


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed/real_2021_2025"
CONTRACT = ROOT / "model_contract.yaml"
SCENARIOS = {"empirical_short", "empirical_central", "empirical_long"}


def test_empirical_scenario_builder_has_parameterized_entrypoint() -> None:
    assert hasattr(io_loader, "build_empirical_duration_scenarios")


@pytest.fixture(scope="module")
def scenarios(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    output = tmp_path_factory.mktemp("empirical_scenarios")
    result = io_loader.build_empirical_duration_scenarios(PROCESSED, output, CONTRACT)
    return output, result


def test_exactly_three_named_nonprobabilistic_scenarios_per_valid_station(
    scenarios: tuple[Path, dict],
) -> None:
    output, _ = scenarios
    index = pd.read_csv(output / "empirical_scenario_index.csv")
    assert set(index["duration_scenario"]) == SCENARIOS
    assert index.groupby(["region_id", "voltage_kv", "station_id"]).size().eq(3).all()
    serialized = index.to_csv(index=False).lower()
    assert "p50" not in serialized
    assert "p90" not in serialized
    assert "confidence interval" not in serialized


def test_profiles_are_daily_and_preserve_each_target_static_peak(
    scenarios: tuple[Path, dict],
) -> None:
    output, _ = scenarios
    profiles = pd.read_csv(output / "empirical_station_scenarios.csv.gz")
    static = pd.read_csv(PROCESSED / "station_static_load.csv")
    keys = ["region_id", "voltage_kv", "station_id"]
    expected = static.dropna(
        subset=["annual_max_net_load_mw", "annual_min_net_load_mw"]
    ).set_index(keys)
    assert profiles.groupby(keys + ["duration_scenario"])["hour"].nunique().eq(24).all()
    extrema = profiles.groupby(keys + ["duration_scenario"])["net_load_mw"].agg(
        ["max", "min"]
    )
    for key, row in extrema.iterrows():
        target = expected.loc[key[:3]]
        assert row["max"] == pytest.approx(max(float(target["annual_max_net_load_mw"]), 0.0))
        assert row["min"] == pytest.approx(min(float(target["annual_min_net_load_mw"]), 0.0))


def test_reference_samples_match_voltage_and_record_sample_count(
    scenarios: tuple[Path, dict],
) -> None:
    output, _ = scenarios
    index = pd.read_csv(output / "empirical_scenario_index.csv")
    assert (index["reference_region_id"] == "QX-00005").all()
    assert (index["reference_voltage_kv"] == index["voltage_kv"]).all()
    assert (index["matched_sample_count"] >= 3).all()
    assert set(index["shape_evidence_status"]) == {
        "conditional_mapping_for_empirical_shape_only"
    }
    assert set(index["county_anchor_role"]) == {
        "formal_positive_peak_anchor_kept_separate_from_station_scenario_sum"
    }


def test_duration_order_is_explicit_and_deterministic(scenarios: tuple[Path, dict]) -> None:
    output, manifest = scenarios
    index = pd.read_csv(output / "empirical_scenario_index.csv")
    pivot = index.pivot(
        index=["region_id", "voltage_kv", "station_id"],
        columns="duration_scenario",
        values="equivalent_reverse_duration_hours",
    )
    assert (pivot["empirical_short"] <= pivot["empirical_central"]).all()
    assert (pivot["empirical_central"] <= pivot["empirical_long"]).all()
    assert len(manifest["scenario_fingerprint"]) == 64


def test_empirical_outputs_preserve_lineage(scenarios: tuple[Path, dict]) -> None:
    output, _ = scenarios
    required = {
        "source_ref",
        "source_version",
        "transformation",
        "scenario_id",
        "quality_flag",
        "source_sha256",
    }
    for filename in ("empirical_scenario_index.csv", "empirical_station_scenarios.csv.gz"):
        frame = pd.read_csv(output / filename)
        assert required <= set(frame.columns)
        assert frame[list(required)].notna().all().all()
