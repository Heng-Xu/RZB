"""10 kV 联络独立案例：QA 门禁固化与引擎行为测试。

数据基线 data/tuomin/10kv_case/（10kV_AgentReady_V5_2 解包，源 zip 只读）。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.tie_case.engine import (
    TieCaseError,
    feeder_boundary_p_mw,
    load_case,
    scenario_s1_forward,
    tie_transfer_scan,
)

CASE_ROOT = Path(__file__).resolve().parents[1] / "data" / "tuomin" / "10kv_case"


@pytest.fixture(scope="module")
def case():
    return load_case(CASE_ROOT)


def test_package_baseline_matches_declared_config(case) -> None:
    """QF07/QF08 前置：开关状态两源一致、TIE-002 就绪。"""
    assert case.confirmed_ties["TIE-007"] == "CLOSED"
    assert all(state == "OPEN" for tid, state in case.confirmed_ties.items() if tid != "TIE-007")


def test_preflight_qa_gates_are_all_present(case) -> None:
    """包自带 11 项 QA 门禁必须齐全且无 P0 阻断（load_case 内已强制）。"""
    assert len(case.preflight_qa) == 11
    statuses = case.preflight_qa["status"].astype(str)
    assert not statuses.str.fullmatch("FAIL").any()


def test_six_feeder_station_mapping_complete(case) -> None:
    """QF01：六馈线→两站归属完整。"""
    expected = {
        "PZXL-00099": "BDZ-00027", "PZXL-00097": "BDZ-00027", "PZXL-00092": "BDZ-00027",
        "PZXL-00154": "BDZ-00048", "PZXL-00161": "BDZ-00048", "PZXL-00173": "BDZ-00048",
    }
    mapping = dict(zip(case.feeders["feeder_id"], case.feeders["station_id"].astype(str)))
    for feeder_id, station in expected.items():
        assert mapping.get(feeder_id) == station


def test_hdong_boundary_p_is_proxy_flagged(case) -> None:
    """QF02：河东线 P 为代理值且必须带标记。"""
    value, proxy = feeder_boundary_p_mw(case, "PZXL-00154")
    assert proxy is True
    assert value > 0
    other, other_proxy = feeder_boundary_p_mw(case, "PZXL-00092")
    assert not other_proxy or str(case.feeders[case.feeders['feeder_id'].eq('PZXL-00092')].iloc[0]['model_boundary_p_source']).startswith("SRC06")


def test_branch_limits_use_effective_rule(case) -> None:
    """QF03：有效热限 = min(导线 Imax, SRC06 允许电流)。"""
    edges = case.edges.dropna(subset=["effective_rate_a_base"])
    ok = edges.apply(
        lambda r: abs(float(r["effective_rate_a_base"]) - min(float(r["ampacity_base_a"]), float(r["feeder_operating_limit_a"]))) < 1e-6
        if pd.notna(r.get("feeder_operating_limit_a")) else True,
        axis=1,
    )
    assert ok.all()


def test_station_boundaries_match_main_model(case) -> None:
    """跨包一致性：墩集 100 MVA、河湾 150 MVA。"""
    caps = dict(zip(case.preflight_qa["qa_id"], case.preflight_qa["status"]))
    assert caps.get("QF04") == "PASS"
    stations = pd.read_csv(CASE_ROOT / "data" / "station_boundary_2025.csv", encoding="utf-8-sig")
    cap = dict(zip(stations["station_id"], stations["rated_capacity_mva"]))
    assert cap["BDZ-00027"] == 100.0 and cap["BDZ-00048"] == 150.0


def test_s1_forward_stress_runs_all_feeders(case) -> None:
    """S1 正向应力：六馈线均可解且输出电压/负载率。"""
    for feeder_id in case.feeder_ids:
        result = scenario_s1_forward(case, feeder_id)
        assert result["umin_pu"] > 0.5
        assert result["served_load_mw"] >= 0


def test_s1_reports_topology_fragmentation_honestly(case) -> None:
    """PZXL-00099 结构化拓扑为碎片森林（负荷 seed 源端可达率 0%）：
    S1 必须如实报告未服务负荷与覆盖率，不得把边界功率冒充已校核负荷。"""
    result = scenario_s1_forward(case, "PZXL-00099")
    assert result["topology_fragmented"] is True
    assert result["unserved_mw"] > 0.9 * result["boundary_p_mw"]
    assert result["load_coverage_pct"] < 10.0


def test_s1_connected_feeder_full_coverage(case) -> None:
    """PZXL-00092 拓扑基本连通、负荷 seed 100% 源端可达：S1 无未服务负荷。"""
    result = scenario_s1_forward(case, "PZXL-00092")
    assert result["topology_fragmented"] is False
    assert result["unserved_mw"] == pytest.approx(0.0, abs=1e-6)
    assert result["load_coverage_pct"] == pytest.approx(100.0, abs=1e-6)


def test_s2_scaled_load_simulated_and_umax_reported(case) -> None:
    """S2 负荷降载必须在仿真内生效（不得只在报告字段缩放），并输出 umax
    用于高 PV 反送过电压校核。"""
    full = scenario_s1_forward(case, "PZXL-00097", pv_factor=1.0)
    scaled = scenario_s1_forward(case, "PZXL-00097", pv_factor=1.0, load_factor=0.3)
    assert scaled["served_load_mw"] == pytest.approx(full["served_load_mw"] * 0.3, abs=1e-3)
    assert scaled["umax_pu"] >= scaled["umin_pu"]
    assert scaled["umax_pu"] > 0.5


def test_tie002_transfer_scan_bounded_by_thermal_or_load(case) -> None:
    """S3：TIE-002 转供受路径热限/对侧备用/负荷耗尽三者之一约束。"""
    result = tie_transfer_scan(case, "TIE-002", direction="to_from")
    assert result["transfer_mw"] >= 0
    assert result["binding_constraint"]
    assert result["parameter_gate_pass"] is True


def test_unknown_tie_rejected(case) -> None:
    with pytest.raises(TieCaseError):
        tie_transfer_scan(case, "TIE-999", direction="from_to")
