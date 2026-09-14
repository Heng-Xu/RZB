"""10 kV 分段—联络规划级案例模型。

用途：
1. 解释“分段开关负责隔离、联络开关负责转供”的拓扑逻辑；
2. 对 TIE-002（墩南线—河炮线）进行规划级容量与反向潮流包络校核；
3. 用可复现的三等值分段图模型演示故障隔离、连通分量重构和联络恢复。

重要边界：
- 本模块是拓扑状态 + 容量约束 + 网络重构的规划级模型，不是完整 AC 潮流、
  短路电流、继电保护定值或现场倒闸操作票模型。
- 当前墩南线普通分段开关的现场功能身份尚未逐台闭环，因此 A1/A2/A3 仍是
  等值教学分段；真实分段负荷结论必须等开关边界校准后再生成。
- 甲方给定的 80% 仅按本专题“邻线反向潮流控制线”使用，不作为普通正向
  负荷转供的通用 80% 负载率限制，也不解释为国家/行业统一标准。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class TieCaseInput:
    tie_id: str
    source_feeder_id: str
    receiving_feeder_id: str
    source_peak_p_mw: float
    receiving_peak_p_mw: float
    source_path_conductor_limit_mva: float
    receiving_path_conductor_limit_mva: float
    source_feeder_operating_limit_mva: float
    receiving_feeder_operating_limit_mva: float
    source_path_km: float
    receiving_path_km: float
    tie_normal_state: str
    pf: float = 0.95
    client_reverse_ratio: float = 0.80
    section_count: int = 3
    pv_peak_anchor_mw: float = 7.34

    @property
    def source_effective_limit_mva(self) -> float:
        """送端路径规划有效上限：导线热限与馈线运行允许值取严。"""
        return min(self.source_path_conductor_limit_mva, self.source_feeder_operating_limit_mva)

    @property
    def receiving_effective_limit_mva(self) -> float:
        """受端路径规划有效上限：导线热限与馈线运行允许值取严。"""
        return min(self.receiving_path_conductor_limit_mva, self.receiving_feeder_operating_limit_mva)


def apparent_from_p(p_mw: float, pf: float) -> float:
    """按给定功率因数将有功功率换算为视在功率。"""
    if not 0 < pf <= 1:
        raise ValueError("pf must be within (0, 1]")
    return abs(float(p_mw)) / pf


def path_loading_ratio(total_s_mva: float, limit_mva: float) -> float:
    if limit_mva <= 0:
        raise ValueError("path limit must be positive")
    return float(total_s_mva) / float(limit_mva)


def load_case_inputs(data_dir: Path, tie_id: str = "TIE-002") -> TieCaseInput:
    injection = pd.read_csv(data_dir / "injection_summary.csv", encoding="utf-8-sig")
    paths = pd.read_csv(data_dir / "key_tie_path_parameter_impact.csv", encoding="utf-8-sig")
    ties = pd.read_csv(data_dir / "tie_master.csv", encoding="utf-8-sig")
    feeders = pd.read_csv(data_dir / "feeder_master.csv", encoding="utf-8-sig")

    tie_rows = ties.loc[ties["tie_id"] == tie_id]
    if tie_rows.empty:
        raise ValueError(f"unknown tie_id: {tie_id}")
    tie = tie_rows.iloc[0]
    if tie_id != "TIE-002":
        raise ValueError("当前正式演示只锁定 TIE-002 首个规划案例")

    source_feeder = str(tie["from_feeder_id"])
    receiving_feeder = str(tie["to_feeder_id"])
    src = injection.loc[injection["feeder_id"] == source_feeder].iloc[0]
    rec = injection.loc[injection["feeder_id"] == receiving_feeder].iloc[0]
    src_master = feeders.loc[feeders["feeder_id"] == source_feeder].iloc[0]
    rec_master = feeders.loc[feeders["feeder_id"] == receiving_feeder].iloc[0]

    tie_paths = paths.loc[paths["tie_id"] == tie_id]
    src_path = tie_paths.loc[tie_paths["feeder_alias"] == tie["from_feeder_alias"]].iloc[0]
    rec_path = tie_paths.loc[tie_paths["feeder_alias"] == tie["to_feeder_alias"]].iloc[0]

    return TieCaseInput(
        tie_id=tie_id,
        source_feeder_id=source_feeder,
        receiving_feeder_id=receiving_feeder,
        source_peak_p_mw=float(src["model_boundary_p_mw"]),
        receiving_peak_p_mw=float(rec["model_boundary_p_mw"]),
        source_path_conductor_limit_mva=float(src_path["thermal_base_mva"]),
        receiving_path_conductor_limit_mva=float(rec_path["thermal_base_mva"]),
        source_feeder_operating_limit_mva=float(src_master["max_allowed_mva_at_10kv"]),
        receiving_feeder_operating_limit_mva=float(rec_master["max_allowed_mva_at_10kv"]),
        source_path_km=float(src_path["nominal_path_km"]),
        receiving_path_km=float(rec_path["nominal_path_km"]),
        tie_normal_state=str(tie["normal_state"]),
    )


def normal_source_path(case: TieCaseInput) -> dict[str, float | str | bool]:
    """送端馈线在自身年度峰值边界下的路径利用率。"""
    s = apparent_from_p(case.source_peak_p_mw, case.pf)
    conductor_loading = path_loading_ratio(s, case.source_path_conductor_limit_mva)
    effective_loading = path_loading_ratio(s, case.source_effective_limit_mva)
    return {
        "scenario": "NORMAL_SOURCE_PATH_ANNUAL_PEAK_ENVELOPE",
        "source_peak_p_mw": case.source_peak_p_mw,
        "path_s_mva": s,
        "conductor_limit_mva": case.source_path_conductor_limit_mva,
        "feeder_operating_limit_mva": case.source_feeder_operating_limit_mva,
        "effective_limit_mva": case.source_effective_limit_mva,
        "conductor_loading_pct": conductor_loading * 100,
        "effective_loading_pct": effective_loading * 100,
        "effective_capacity_pass": effective_loading <= 1.0 + 1e-12,
        "client_reverse_80_applicable": False,
    }


def full_feeder_transfer(case: TieCaseInput) -> dict[str, float | str | bool]:
    """源端/整线失电时，以两条馈线各自年度峰值构造保守转供包络。

    这里是正向负荷转供，不套用“邻线反向潮流≤80%”控制线。容量检查使用
    受端路径的规划有效上限。两个年度峰值不是同步断面，因此结果属于保守包络。
    """
    source_s = apparent_from_p(case.source_peak_p_mw, case.pf)
    receiving_s = apparent_from_p(case.receiving_peak_p_mw, case.pf)
    total_s = source_s + receiving_s
    effective_limit = case.receiving_effective_limit_mva
    loading = path_loading_ratio(total_s, effective_limit)
    max_transfer_p = max(effective_limit - receiving_s, 0.0) * case.pf
    full_transfer_feasible = source_s + receiving_s <= effective_limit + 1e-12
    residual_mva = effective_limit - total_s
    residual_transfer_p = max(max_transfer_p - case.source_peak_p_mw, 0.0)

    return {
        "scenario": "SOURCE_OUTAGE_FULL_FEEDER_TRANSFER_ANNUAL_PEAK_ENVELOPE",
        "transfer_p_mw": case.source_peak_p_mw,
        "source_peak_s_mva": source_s,
        "receiving_own_s_mva": receiving_s,
        "receiving_total_s_mva": total_s,
        "receiving_conductor_limit_mva": case.receiving_path_conductor_limit_mva,
        "receiving_feeder_operating_limit_mva": case.receiving_feeder_operating_limit_mva,
        "receiving_effective_limit_mva": effective_limit,
        "receiving_effective_loading_pct": loading * 100,
        "capacity_pass": full_transfer_feasible,
        "max_transfer_p_under_effective_limit_mw": max_transfer_p,
        "residual_margin_after_full_transfer_mva": residual_mva,
        "residual_transfer_headroom_mw": residual_transfer_p,
        "client_reverse_80_applicable": False,
        "simultaneity": "ANNUAL_MAXIMA_ENVELOPE_NOT_SYNCHRONOUS",
    }


def equal_section_transfer_demo(case: TieCaseInput) -> pd.DataFrame:
    """三等值分段容量演示：逐步增加由联络线承担的健康分段数量。"""
    section_p = case.source_peak_p_mw / case.section_count
    receiving_own_s = apparent_from_p(case.receiving_peak_p_mw, case.pf)
    rows: list[dict[str, float | int | bool | str]] = []
    for n in range(1, case.section_count + 1):
        transfer_p = section_p * n
        total_s = receiving_own_s + apparent_from_p(transfer_p, case.pf)
        loading = path_loading_ratio(total_s, case.receiving_effective_limit_mva)
        rows.append(
            {
                "equivalent_sections_transferred": n,
                "equivalent_section_p_mw": section_p,
                "transfer_p_mw": transfer_p,
                "receiving_total_s_mva": total_s,
                "receiving_effective_limit_mva": case.receiving_effective_limit_mva,
                "receiving_path_loading_pct": loading * 100,
                "capacity_pass": loading <= 1.0 + 1e-12,
                "client_reverse_80_applicable": False,
                "evidence_level": "METHOD_DEMO_EQUAL_SECTION_NOT_MEASURED",
            }
        )
    return pd.DataFrame(rows)


def pv_reverse_envelope(case: TieCaseInput, scales: Iterable[float] = (1.0, 1.2, 1.5)) -> pd.DataFrame:
    """反向潮流保守包络。

    以墩南线7.34 MW实际光伏峰值出力锚点为基准，并令受、送两侧本地负荷均不
    抵消反送，得到穿越河炮侧路径的保守上界。该场景才应用甲方给定的80%反向
    潮流控制线。
    """
    rows: list[dict[str, float | bool | str]] = []
    limit = case.receiving_effective_limit_mva
    reverse_limit = case.client_reverse_ratio * limit
    for scale in scales:
        gross_export_p = case.pv_peak_anchor_mw * float(scale)
        # 光伏逆变器在规划上界中近似单位功率因数；不以本地负荷抵消反送。
        gross_export_s = gross_export_p
        loading = path_loading_ratio(gross_export_s, limit)
        rows.append(
            {
                "pv_scale": float(scale),
                "gross_reverse_export_upper_bound_mw": gross_export_p,
                "gross_reverse_export_upper_bound_mva": gross_export_s,
                "receiving_effective_limit_mva": limit,
                "client_reverse_80_limit_mva": reverse_limit,
                "receiving_reverse_path_loading_pct": loading * 100,
                "thermal_operating_pass": loading <= 1.0 + 1e-12,
                "client_reverse_80_pass": loading <= case.client_reverse_ratio + 1e-12,
                "interpretation": "ZERO_LOCAL_LOAD_CONSERVATIVE_REVERSE_UPPER_BOUND_NOT_SYNCHRONOUS_FLOW",
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 等值三分段拓扑状态仿真
# ---------------------------------------------------------------------------

DEMO_NODES = ("A_SOURCE", "A1", "A2", "A3", "B_SOURCE")
DEMO_EDGES = {
    "CB_A": ("A_SOURCE", "A1", "BREAKER"),
    "S1": ("A1", "A2", "SECTIONAL"),
    "S2": ("A2", "A3", "SECTIONAL"),
    "TIE": ("A3", "B_SOURCE", "TIE"),
}


def connected_components(
    nodes: Iterable[str],
    edges: dict[str, tuple[str, str, str]],
    closed_state: dict[str, bool],
) -> list[set[str]]:
    """按当前闭合边计算无向连通分量；不依赖networkx，便于结果复现。"""
    node_set = set(nodes)
    adjacency = {node: set() for node in node_set}
    for edge_id, (u, v, _kind) in edges.items():
        if not closed_state.get(edge_id, False):
            continue
        if u not in node_set or v not in node_set:
            raise ValueError(f"edge {edge_id} references unknown node")
        adjacency[u].add(v)
        adjacency[v].add(u)

    components: list[set[str]] = []
    unseen = set(node_set)
    while unseen:
        start = unseen.pop()
        comp = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            for nxt in adjacency[current]:
                if nxt in unseen:
                    unseen.remove(nxt)
                    comp.add(nxt)
                    stack.append(nxt)
        components.append(comp)
    return components


def identify_sections_demo(case: TieCaseInput) -> pd.DataFrame:
    """在分段识别阶段临时断开S1/S2，得到A1/A2/A3三个等值供电单元。"""
    if case.section_count != 3:
        raise ValueError("当前等值教学拓扑固定为三分段")
    states = {"CB_A": False, "S1": False, "S2": False, "TIE": False}
    comps = connected_components(DEMO_NODES, DEMO_EDGES, states)
    section_p = case.source_peak_p_mw / 3
    rows = []
    for node in ("A1", "A2", "A3"):
        comp_id = next(i for i, comp in enumerate(comps, start=1) if node in comp)
        rows.append(
            {
                "section_id": node,
                "component_id": comp_id,
                "equivalent_peak_p_mw": section_p,
                "boundary_method": "TEMPORARILY_OPEN_SECTIONAL_EDGES_S1_S2",
                "evidence_level": "METHOD_DEMO_EQUAL_SECTION_NOT_MEASURED",
            }
        )
    return pd.DataFrame(rows)


def _node_supply_labels(states: dict[str, bool], faulted: set[str] | None = None) -> dict[str, str]:
    """返回A1/A2/A3当前由哪个源供电；故障节点强制标记FAULT。"""
    faulted = faulted or set()
    labels = {node: "DEENERGIZED" for node in ("A1", "A2", "A3")}
    components = connected_components(DEMO_NODES, DEMO_EDGES, states)
    for comp in components:
        sources = []
        if "A_SOURCE" in comp:
            sources.append("A_SOURCE")
        if "B_SOURCE" in comp:
            sources.append("B_SOURCE")
        label = "DEENERGIZED" if not sources else "+".join(sorted(sources))
        for node in ("A1", "A2", "A3"):
            if node in comp:
                labels[node] = label
    for node in faulted:
        if node in labels:
            labels[node] = "FAULT"
    return labels


def _no_parallel_sources(states: dict[str, bool]) -> bool:
    """规划级开环检查：任一连通分量不得同时含A、B两个电源。"""
    for comp in connected_components(DEMO_NODES, DEMO_EDGES, states):
        if "A_SOURCE" in comp and "B_SOURCE" in comp:
            return False
    return True


def switching_sequence_demo(case: TieCaseInput, fault_section: int = 2) -> pd.DataFrame:
    """用实际图连通状态演示三分段第二段故障的隔离—恢复过程。

    A2故障后：出口断路器跳闸 → S1/S2断开隔离 → 原源恢复A1 → 校核候选
    TIE → 在容量、开环拓扑通过且“规划演示假设保护允许”的前提下闭合TIE，A3由
    B侧恢复。现场操作仍需保护与调度专业确认。
    """
    if case.section_count != 3 or fault_section != 2:
        raise ValueError("当前教学演示固定为三分段、第二段故障")

    one_section_p = case.source_peak_p_mw / 3
    one_section_s = apparent_from_p(one_section_p, case.pf)
    receiving_own_s = apparent_from_p(case.receiving_peak_p_mw, case.pf)
    tie_loading = (receiving_own_s + one_section_s) / case.receiving_effective_limit_mva
    capacity_pass = tie_loading <= 1.0 + 1e-12

    states = {"CB_A": True, "S1": True, "S2": True, "TIE": False}
    rows: list[dict[str, object]] = []

    def record(step: int, action: str, note: str, fault_active: bool = True) -> None:
        labels = _node_supply_labels(states, {"A2"} if fault_active else set())
        rows.append(
            {
                "step": step,
                "action": action,
                "CB_A": "CLOSED" if states["CB_A"] else "OPEN",
                "S1": "CLOSED" if states["S1"] else "OPEN",
                "S2": "CLOSED" if states["S2"] else "OPEN",
                "TIE": "CLOSED" if states["TIE"] else "OPEN",
                "A1_supply": labels["A1"],
                "A2_supply": labels["A2"],
                "A3_supply": labels["A3"],
                "radial_no_parallel_sources": _no_parallel_sources(states),
                "candidate_transfer_p_mw": one_section_p if step >= 5 else 0.0,
                "candidate_receiving_loading_pct": tie_loading * 100 if step >= 5 else 0.0,
                "capacity_pass": capacity_pass if step >= 5 else True,
                "client_reverse_80_applicable": False,
                "protection_status": "REVIEW_REQUIRED" if step >= 5 else "NOT_APPLICABLE",
                "note": note,
            }
        )

    record(0, "NORMAL", "正常开环运行；尚未发生故障", fault_active=False)

    states["CB_A"] = False
    record(1, "TRIP", "A2故障后源端断路器跳闸，A侧三段暂失电")

    states["S1"] = False
    record(2, "ISOLATE_UPSTREAM", "断开A2上游边界S1")

    states["S2"] = False
    record(3, "ISOLATE_DOWNSTREAM", "断开A2下游边界S2，A2完成两侧隔离")

    states["CB_A"] = True
    record(4, "RESTORE_UPSTREAM", "原馈线源端恢复，A1由A_SOURCE供电；A3仍失电")

    candidate_states = dict(states)
    candidate_states["TIE"] = True
    candidate_radial = _no_parallel_sources(candidate_states)
    planning_candidate = capacity_pass and candidate_radial
    record(
        5,
        "CHECK_TIE",
        (
            f"试合TIE-002前校核：A3转供{one_section_p:.4f} MW，受端路径"
            f"{tie_loading*100:.2f}%；容量与开环拓扑"
            f"{'通过' if planning_candidate else '不通过'}，保护方向性仍需专项复核"
        ),
    )

    if planning_candidate:
        states["TIE"] = True
        record(
            6,
            "CLOSE_TIE_PLANNING_DEMO",
            "仅在规划仿真假设保护/调度允许时闭合TIE-002；A3由B_SOURCE恢复",
        )
    else:
        record(6, "TIE_NOT_CLOSED", "容量或开环拓扑不满足，联络不闭合")

    record(7, "FINAL", "A2保持隔离；A1原源供电；A3按规划候选由联络侧恢复")
    return pd.DataFrame(rows)


def build_summary(case: TieCaseInput) -> pd.DataFrame:
    normal = normal_source_path(case)
    full = full_feeder_transfer(case)
    demo = equal_section_transfer_demo(case)
    pv = pv_reverse_envelope(case)
    max_demo_pass = demo.loc[demo["capacity_pass"], "equivalent_sections_transferred"].max()
    max_demo_pass = int(max_demo_pass) if pd.notna(max_demo_pass) else 0
    pv100 = pv.loc[pv["pv_scale"] == 1.0].iloc[0]
    pv120 = pv.loc[pv["pv_scale"] == 1.2].iloc[0]

    rows = [
        {
            "item": "TIE-002_normal_state",
            "value": case.tie_normal_state,
            "unit": "state",
            "conclusion": "正常按已确认状态开环；故障/检修重构时才考虑闭合",
        },
        {
            "item": "dnan_source_path_conductor_loading",
            "value": f"{normal['conductor_loading_pct']:.2f}",
            "unit": "%",
            "conclusion": "按240绝缘导线基准热限8.6603 MVA计算",
        },
        {
            "item": "dnan_source_path_effective_loading",
            "value": f"{normal['effective_loading_pct']:.2f}",
            "unit": "%",
            "conclusion": "按min(导线热限,馈线485 A运行允许值)=8.4004 MVA计算；正向负荷率，不套反向80%线",
        },
        {
            "item": "full_dnan_peak_transfer_to_hpao_loading",
            "value": f"{full['receiving_effective_loading_pct']:.2f}",
            "unit": "%",
            "conclusion": "两馈线年度峰值同时出现的保守包络；容量通过但余度较小；不套反向80%线",
        },
        {
            "item": "full_dnan_peak_transfer_capacity_pass",
            "value": str(bool(full["capacity_pass"])),
            "unit": "bool",
            "conclusion": "受端有效路径上限9.5263 MVA下通过规划级容量筛查；保护仍需专项复核",
        },
        {
            "item": "max_transfer_under_effective_path_limit",
            "value": f"{full['max_transfer_p_under_effective_limit_mw']:.4f}",
            "unit": "MW",
            "conclusion": "按PF=0.95和受端有效路径上限计算的正向转供容量上限",
        },
        {
            "item": "three_equal_section_demo_capacity_max_sections",
            "value": str(max_demo_pass),
            "unit": "sections",
            "conclusion": "三等值段教学演示中3段均满足容量底线；分段仍用于故障隔离、选择性恢复和保留运行余度",
        },
        {
            "item": "pv_1p0_reverse_loading",
            "value": f"{pv100['receiving_reverse_path_loading_pct']:.2f}",
            "unit": "%",
            "conclusion": "零负荷抵消的保守反送上界；低于甲方80%反向潮流控制线",
        },
        {
            "item": "pv_1p2_reverse_loading",
            "value": f"{pv120['receiving_reverse_path_loading_pct']:.2f}",
            "unit": "%",
            "conclusion": "零负荷抵消的保守反送上界；超过甲方80%反向潮流控制线但尚未超过路径容量底线",
        },
    ]
    return pd.DataFrame(rows)
