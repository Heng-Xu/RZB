from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.v3_pipeline import _network_screen


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data/processed/real_2021_2025"


def test_real_network_screen_is_internal_capacity_only_and_not_a_flow_claim() -> None:
    screen = _network_screen(PROCESSED)
    source = pd.read_csv(PROCESSED / "network_lines_110kv.csv")
    assert len(screen) == len(source) == 364
    assert set(screen.voltage_kv) == {110}
    assert set(screen.screen_type) == {"internal_capacity_network_screen"}
    assert set(screen.n_minus_1_method) == {"capacity_network_contingency_screen"}
    assert not screen.precise_ac_or_dc_claim.astype(bool).any()
    assert not screen.visible_in_client_matrix.astype(bool).any()
    assert set(screen.screen_status) == {"screen_only_without_impedance"}


def test_network_screen_preserves_line_identity_and_current_limits() -> None:
    screen = _network_screen(PROCESSED)
    source = pd.read_csv(PROCESSED / "network_lines_110kv.csv")
    assert screen.line_id.is_unique
    assert set(screen.line_id) == set(source.line_id)
    assert screen.current_limit_a.gt(0).all()
