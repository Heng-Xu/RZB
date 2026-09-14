"""10 kV 分段-联络规划级案例模型。

该模块用于解释“分段开关负责隔离、联络开关负责转供”的拓扑逻辑，
并对 TIE-002（墩南线-河炮线）进行规划级容量与反向潮流包络校核。

重要边界：
1. 这是拓扑/容量/转供层面的规划模型，不是完整 AC 潮流、短路或保护定值模型。
2. 普通分段开关的正常合闸规则可用于情景仿真，但具体现场设备位置仍需图纸/现场校准。
3. 三分段演示采用等负荷分段，仅用于说明“线路切分以后如何仿真”；不得当作实测分段负荷。
4. 80% 为甲方给定专题场景控制线，不解释为普适国家/行业标准。
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
    source_path_limit_mva: float
    receiving_path_limit_mva: float
    source_path_km: float
    receiving_path_km: float
    tie_normal_state: str
    pf: float = 0.95
    control_ratio: float = 0.80
    section_count: int = 3
    pv_peak_anchor_mw: float = 7.34


def apparent_from_p(p_mw: float, pf: float) -> float:
    """按给定功率因数将有功功率换算为视在功率。"""
    if not 0 < pf <= 1:
        raise ValueError("pf must be within (0, 1]")
    return abs(float(p_mw)) / pf


def path_loading_ratio(total_s_mva: float, limit_mva: float) -> float:
    if limit_mva <= 0:
        raise ValueError("path limit must be positive")
    return total_s_mva / limit_mva


def load_case_inputs(data_dir: Path, tie_id: str = "TIE-002") -> TieCaseInput:
    injection = pd.read_csv(data_dir / "injection_summary.csv", encoding="utf-8-sig")
    paths = pd.read_csv(data_dir / "key_tie_path_parameter_impact.csv", encoding="utf-8-sig")
    ties = pd.read_csv(data_dir / "tie_master.csv", encoding="utf-8-sig")

    tie = ties.loc[ties["tie_id"] == tie_id].iloc[0]
    if tie_id != "TIE-002":
        raise ValueError("当前正式演示只锁定 TIE-002 首个规划案例")

    source_feeder = str(tie["from_feeder_id"])
    receiving_feeder = str(tie["to_feeder_id"])
    src = injection.loc[injection["feeder_id"] == source_feeder].iloc[0]
    rec = injection.loc[injection["feeder_id"] == receiving_feeder].iloc[0]

    tie_paths = paths.loc[paths["tie_id"] == tie_id]
    src_path = tie_paths.loc[tie_paths["feeder_alias"] == tie["from_feeder_alias"]].iloc[0]
    rec_path = tie_paths.loc[tie_paths["feeder_alias"] == tie["to_feeder_alias"]].iloc[0]

    return TieCaseInput(
        tie_id=tie_id,
        source_feeder_id=source_feeder,
        receiving_feeder_id=receiving_feeder,
        source_peak_p_mw=float(src["model_boundary_p_mw"]),
        receiving_peak_p_mw=float(rec["model_boundary_p_mw"]),
        source_path_limit_mva=float(src_path["thermal_base_mva"]),
        receiving_path_limit_mva=float(rec_path["thermal_base_mva"]),
        source_path_km=float(src_path["nominal_path_km"]),
        receiving_path_km=float(rec_path["nominal_path_km"]),
        tie_normal_state=str(tie["normal_state"]),
    )


def full_feeder_transfer(case: TieCaseInput) -> dict[str, float | str | bool]:
    """源馈线整体失电时，尝试由受端馈线承担整条源馈线峰值负荷。"""
    source_s = apparent_from_p(case.source_peak_p_mw, case.pf)
    receiving_s = apparent_from_p(case.receiving_peak_p_mw, case.pf)
    total_s = source_s + receiving_s
    loading = path_loading_ratio(total_s, case.receiving_path_limit_mva)
    control_limit_s = case.control_ratio * case.receiving_path_limit_mva
    residual_s = max(control_limit_s - receiving_s, 0.0)
    max_transfer_p = residual_s * case.pf
    restored_ratio = min(max_transfer_p / case.source_peak_p_mw, 1.0)

    return {
        "scenario": "SOURCE_OUTAGE_FULL_FEEDER_TRANSFER",
        "transfer_p_mw": case.source_peak_p_mw,
        "source_peak_s_mva": source_s,
        "receiving_own_s_mva": receiving_s,
        "receiving_total_s_mva": total_s,
        "receiving_path_limit_mva": case.receiving_path_limit_mva,
        "receiving_path_loading_pct": loading * 100,
        "thermal_pass": loading <= 1.0 + 1e-12,
        "client_80pct_pass": loading <= case.control_ratio + 1e-12,
        "max_transfer_p_under_80pct_mw": max_transfer_p,
        "max_restorable_fraction_under_80pct": restored_ratio,
        "unserved_if_strict_80pct_mw": max(case.source_peak_p_mw - max_transfer_p, 0.0),
    }


def normal_source_path(case: TieCaseInput) -> dict[str, float | str | bool]:
    """源馈线在自身峰值边界下的源端-联络点路径利用率。"""
    s = apparent_from_p(case.source_peak_p_mw, case.pf)
    loading = path_loading_ratio(s, case.source_path_limit_mva)
    return {
        "scenario": "NORMAL_SOURCE_PATH_PEAK_ENVELOPE",
        "transfer_p_mw": case.source_peak_p_mw,
        "path_s_mva": s,
        "path_limit_mva": case.source_path_limit_mva,
        "path_loading_pct": loading * 100,
        "thermal_pass": loading <= 1.0 + 1e-12,
        "client_80pct_pass": loading <= case.control_ratio + 1e-12,
    }


def equal_section_transfer_demo(case: TieCaseInput) -> pd.DataFrame:
    """三分段等值演示：逐步增加由联络线承担的健康分段数量。"""
    section_p = case.source_peak_p_mw / case.section_count
    receiving_own_s = apparent_from_p(case.receiving_peak_p_mw, case.pf)
    rows: list[dict[str, float | int | bool | str]] = []
    for n in range(1, case.section_count + 1):
        transfer_p = section_p * n
        total_s = receiving_own_s + apparent_from_p(transfer_p, case.pf)
        loading = path_loading_ratio(total_s, case.receiving_path_limit_mva)
        rows.append(
            {
                "equivalent_sections_transferred": n,
                "equivalent_section_p_mw": section_p,
                "transfer_p_mw": transfer_p,
                "receiving_total_s_mva": total_s,
                "receiving_path_loading_pct": loading * 100,
                "thermal_pass": loading <= 1.0 + 1e-12,
                "client_80pct_pass": loading <= case.control_ratio + 1e-12,
                "evidence_level": "METHOD_DEMO_EQUAL_SECTION_NOT_MEASURED",
            }
        )
    return pd.DataFrame(rows)


def pv_reverse_envelope(case: TieCaseInput, scales: Iterable[float] = (1.0, 1.2, 1.5)) -> pd.DataFrame:
    """零本地负荷保守上界：以已知 dnan 光伏出力峰值锚点评估联络路径反送包络。"""
    rows: list[dict[str, float | bool | str]] = []
    for scale in scales:
        gross_export_p = case.pv_peak_anchor_mw * float(scale)
        # 作为保守上界，假设光伏近似单位功率因数，且本地负荷为0。
        gross_export_s = gross_export_p
        loading = path_loading_ratio(gross_export_s, case.receiving_path_limit_mva)
        rows.append(
            {
                "pv_scale": float(scale),
                "gross_reverse_export_upper_bound_mw": gross_export_p,
                "gross_reverse_export_upper_bound_mva": gross_export_s,
                "receiving_path_loading_pct": loading * 100,
                "thermal_pass": loading <= 1.0 + 1e-12,
                "client_80pct_pass": loading <= case.control_ratio + 1e-12,
                "interpretation": "ZERO_LOCAL_LOAD_CONSERVATIVE_UPPER_BOUND_NOT_SYNCHRONOUS_ACTUAL_FLOW",
            }
        )
    return pd.DataFrame(rows)


def switching_sequence_demo(case: TieCaseInput, fault_section: int = 2) -> pd.DataFrame:
    """标准三分段故障隔离-转供序列。

    演示模型采用 A1-A2-A3 三个等值段：A2故障后，上游A1由原电源恢复，
    下游A3通过 TIE-002 由相邻馈线恢复。该顺序特意避免把“所有健康段都由邻线反送”
    当作一般分段故障的默认逻辑。
    """
    if case.section_count != 3 or fault_section != 2:
        raise ValueError("当前教学演示固定为三分段、第二段故障")
    one_section = case.source_peak_p_mw / 3
    receiving_total_s = apparent_from_p(case.receiving_peak_p_mw + one_section, case.pf)
    loading = receiving_total_s / case.receiving_path_limit_mva
    pass_80 = loading <= case.control_ratio + 1e-12

    rows = [
        (0, "NORMAL", "源端断路器CLOSED；分段S1/S2 CLOSED；TIE-002 OPEN", "基准开环运行"),
        (1, "TRIP", "故障发生于A2，源端断路器跳闸", "A1-A3暂时失电"),
        (2, "ISOLATE_UPSTREAM", "断开A2上游边界分段开关S1", "切断A1-A2连接"),
        (3, "ISOLATE_DOWNSTREAM", "断开A2下游边界分段开关S2", "故障段A2被两侧隔离"),
        (4, "RESTORE_UPSTREAM", "重合/合上原馈线源端断路器", "A1由原电源恢复；不是默认由邻线反送"),
        (5, "CHECK_TIE", f"校核TIE-002受端路径：转供A3={one_section:.4f} MW，路径负载率={loading*100:.1f}%", "通过80%控制线" if pass_80 else "不通过80%控制线"),
        (6, "CLOSE_TIE", "在容量、反向潮流、开环拓扑和保护方向性均允许后合TIE-002", "A3由河炮线侧恢复供电"),
        (7, "FINAL", "A2保持隔离；A1原源供电；A3联络转供", "仅故障段停电，健康段恢复"),
    ]
    return pd.DataFrame(rows, columns=["step", "action", "switch_operation_or_check", "result"])


def build_summary(case: TieCaseInput) -> pd.DataFrame:
    normal = normal_source_path(case)
    full = full_feeder_transfer(case)
    demo = equal_section_transfer_demo(case)
    max_demo_pass = demo.loc[demo["client_80pct_pass"], "equivalent_sections_transferred"].max()
    max_demo_pass = int(max_demo_pass) if pd.notna(max_demo_pass) else 0

    rows = [
        {
            "item": "TIE-002_normal_state",
            "value": case.tie_normal_state,
            "unit": "state",
            "conclusion": "正常开环；故障/检修转供时才闭合",
        },
        {
            "item": "dnan_source_to_tie_peak_loading",
            "value": f"{normal['path_loading_pct']:.2f}",
            "unit": "%",
            "conclusion": "规划包络下热限通过；接近甲方80%控制线",
        },
        {
            "item": "full_dnan_peak_transfer_to_hpao_loading",
            "value": f"{full['receiving_path_loading_pct']:.2f}",
            "unit": "%",
            "conclusion": "热限通过但超过甲方80%控制线；不建议把整线峰值负荷作为直接可转供量",
        },
        {
            "item": "max_transfer_under_client_80pct",
            "value": f"{full['max_transfer_p_under_80pct_mw']:.4f}",
            "unit": "MW",
            "conclusion": "在PF=0.95与当前路径热限下的规划级上限",
        },
        {
            "item": "restorable_fraction_under_client_80pct",
            "value": f"{100*full['max_restorable_fraction_under_80pct']:.2f}",
            "unit": "%",
            "conclusion": "按整线峰值负荷口径的最大可转供比例；实际应按分段负荷重新计算",
        },
        {
            "item": "three_equal_section_demo_max_sections",
            "value": str(max_demo_pass),
            "unit": "sections",
            "conclusion": "三等值段教学演示中，最多2段同时转供可满足80%控制线；非实测分段结论",
        },
    ]
    return pd.DataFrame(rows)
