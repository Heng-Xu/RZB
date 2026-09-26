import pytest

from rebuild_2026.tie_section_audit import transferable_section


def test_original_switch28_isolates_a_discrete_downstream_load_block() -> None:
    section = transferable_section()
    assert section["switch_upstream_node_id"] == "PZXL-00092-N0048"
    assert section["switch_downstream_node_id"] == "PZXL-00092-N0049"
    assert section["section_node_count"] == 136
    assert section["2025_feeder_stress_section_p_seed_mw"] == pytest.approx(4.49651196)
    assert section["2025_feeder_stress_section_p_seed_mw"] < section["2025_feeder_stress_total_p_seed_mw"]
