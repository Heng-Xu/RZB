"""10 kV 高光伏场景跨站反向功率转移规划模型。

本模块解决的核心问题不是故障恢复，而是：当一个 110 kV 变电站下辖 10 kV
馈线在高光伏、低负荷时形成较强反向功率时，利用既有站间联络，必要时配置
新的联络通道，将部分净发电供电单元调整至相邻变电站供电范围，从而降低原站
反向承载压力。

模型分两层：
1. 既有联络优化：优先利用已确认的 TIE-002（墩南线—河炮线），通过“开原
   供电边界 + 合站间联络”保持开环运行，并计算可转移净光伏富余功率。
2. 新建联络容量定型：当既有联络在项目反向潮流控制条件下不足时，计算剩余
   需转移功率及新联络所需的最小规划有效容量，并对河湾变侧候选馈线进行
   馈线级承接能力筛查。由于现有资料没有 GIS 坐标和候选廊道长度，本模块不
   虚构具体新建线路路径或工程量。

重要边界：
- 这是规划级“供电边界重构 + 容量约束”模型，不是完整 AC 潮流、短路电流、
  继电保护定值或现场倒闸操作票模型。
- 墩南线 7.34 MW 为实际光伏峰值出力锚点，不等同于完整装机容量。
- 负荷采用年度最大馈线有功乘规划场景 load_factor 构造空间应力代理；与光伏
  峰值及两站年度最小负荷不声明为同一历史同步断面。
- 甲方给定的“反向潮流不超过 80%”只用于反向功率通道控制，不作为普通正向
  负荷转供的通用负载率限制，也不解释为国家/行业统一标准。
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class ReverseTransferCase:
    tie_id: str
    donor_station_id: str
    donor_station_name: str
    receiver_station_id: str
    receiver_station_name: str
    donor_feeder_id: str
    donor_feeder_alias: str
    receiver_feeder_id: str
    receiver_feeder_alias: str
    donor_feeder_peak_p_mw: float
    receiver_feeder_peak_p_mw: float
    donor_path_conductor_limit_mva: float
    receiver_path_conductor_limit_mva: float
    donor_feeder_operating_limit_mva: float
    receiver_feeder_operating_limit_mva: float
    donor_path_km: float
    receiver_path_km: float
    donor_station_min_net_load_mw: float
    receiver_station_min_net_load_mw: float
    receiver_station_n1_screen_mva: float
    pv_peak_anchor_mw: float
    tie_normal_state: str
    client_reverse_ratio: float = 0.80

    @property
    def donor_path_effective_limit_mva(self) -> float:
        return min(self.donor_path_conductor_limit_mva, self.donor_feeder_operating_limit_mva)

    @property
    def receiver_path_effective_limit_mva(self) -> float:
        return min(self.receiver_path_conductor_limit_mva, self.receiver_feeder_operating_limit_mva)

    @property
    def existing_tie_reverse_capacity_mw(self) -> float:
        """TIE-002 在规划级反向转移下的保守有功上限。

        光伏按 unity-PF 基准处理。送端路径只校核规划有效容量；受端路径额外应用
        项目反向潮流 80% 控制线。由于缺少同一时刻受端本地负荷，这里不使用
        河炮线本地负荷去抵消反向潮流，属于保守口径。
        """
        receiver_control = self.client_reverse_ratio * self.receiver_path_effective_limit_mva
        return min(self.donor_path_effective_limit_mva, receiver_control)

    @property
    def receiver_station_reverse_headroom_mw(self) -> float:
        """河湾变站级保守容量筛查余量。

        以“最大主变退出后剩余容量”作为规划级热容量筛查上限。该指标不能替代
        反向保护、母线电压和完整 N-1 潮流校核。
        """
        base_reverse = max(-self.receiver_station_min_net_load_mw, 0.0)
        return max(self.receiver_station_n1_screen_mva - base_reverse, 0.0)


def _extract_pv_mw(text: object) -> float | None:
    """从汇总字段中提取规划级 PV 数值并统一为 MW。"""
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return None
    raw = str(text).strip()
    match = re.search(r"[-+]?\d+(?:\.\d+)?", raw)
    if not match:
        return None
    value = float(match.group(0))
    lowered = raw.lower()
    if "kva" in lowered or "kw" in lowered:
        return value / 1000.0
    if "mva" in lowered or "mw" in lowered:
        return value
    return value


def load_reverse_transfer_case(
    data_dir: Path,
    tie_id: str = "TIE-002",
    client_reverse_ratio: float = 0.80,
) -> tuple[ReverseTransferCase, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """读取 TIE-002、馈线、站级边界和光伏锚点。"""
    ties = pd.read_csv(data_dir / "tie_master.csv", encoding="utf-8-sig")
    paths = pd.read_csv(data_dir / "key_tie_path_parameter_impact.csv", encoding="utf-8-sig")
    feeders = pd.read_csv(data_dir / "feeder_master.csv", encoding="utf-8-sig")
    injections = pd.read_csv(data_dir / "injection_summary.csv", encoding="utf-8-sig")
    stations = pd.read_csv(data_dir / "station_boundary_2025.csv", encoding="utf-8-sig")
    station_pv = pd.read_csv(data_dir / "station_pv_anchors_2026.csv", encoding="utf-8-sig")

    if not 0 < client_reverse_ratio <= 1:
        raise ValueError("client_reverse_ratio must be within (0, 1]")

    tie_rows = ties.loc[ties["tie_id"] == tie_id]
    if tie_rows.empty:
        raise ValueError(f"unknown tie_id: {tie_id}")
    if tie_id != "TIE-002":
        raise ValueError("当前首个正式高光伏跨站案例锁定 TIE-002")
    tie = tie_rows.iloc[0]

    donor_feeder_id = str(tie["from_feeder_id"])
    receiver_feeder_id = str(tie["to_feeder_id"])
    donor_station_id = str(tie["from_station_id"])
    receiver_station_id = str(tie["to_station_id"])

    donor_feeder = feeders.loc[feeders["feeder_id"] == donor_feeder_id].iloc[0]
    receiver_feeder = feeders.loc[feeders["feeder_id"] == receiver_feeder_id].iloc[0]
    donor_injection = injections.loc[injections["feeder_id"] == donor_feeder_id].iloc[0]
    receiver_injection = injections.loc[injections["feeder_id"] == receiver_feeder_id].iloc[0]
    donor_station = stations.loc[stations["station_id"] == donor_station_id].iloc[0]
    receiver_station = stations.loc[stations["station_id"] == receiver_station_id].iloc[0]

    tie_paths = paths.loc[paths["tie_id"] == tie_id]
    donor_path = tie_paths.loc[tie_paths["feeder_alias"] == tie["from_feeder_alias"]].iloc[0]
    receiver_path = tie_paths.loc[tie_paths["feeder_alias"] == tie["to_feeder_alias"]].iloc[0]

    pv_anchor = _extract_pv_mw(donor_injection["pv_total_or_anchor"])
    if pv_anchor is None:
        raise ValueError("TIE-002 donor feeder lacks a usable PV output anchor")

    case = ReverseTransferCase(
        tie_id=tie_id,
        donor_station_id=donor_station_id,
        donor_station_name=str(tie["from_station"]),
        receiver_station_id=receiver_station_id,
        receiver_station_name=str(tie["to_station"]),
        donor_feeder_id=donor_feeder_id,
        donor_feeder_alias=str(tie["from_feeder_alias"]),
        receiver_feeder_id=receiver_feeder_id,
        receiver_feeder_alias=str(tie["to_feeder_alias"]),
        donor_feeder_peak_p_mw=float(donor_injection["model_boundary_p_mw"]),
        receiver_feeder_peak_p_mw=float(receiver_injection["model_boundary_p_mw"]),
        donor_path_conductor_limit_mva=float(donor_path["thermal_base_mva"]),
        receiver_path_conductor_limit_mva=float(receiver_path["thermal_base_mva"]),
        donor_feeder_operating_limit_mva=float(donor_feeder["max_allowed_mva_at_10kv"]),
        receiver_feeder_operating_limit_mva=float(receiver_feeder["max_allowed_mva_at_10kv"]),
        donor_path_km=float(donor_path["nominal_path_km"]),
        receiver_path_km=float(receiver_path["nominal_path_km"]),
        donor_station_min_net_load_mw=float(donor_station["2025_annual_min_load_mw"]),
        receiver_station_min_net_load_mw=float(receiver_station["2025_annual_min_load_mw"]),
        receiver_station_n1_screen_mva=float(receiver_station["surviving_capacity_after_largest_outage_mva"]),
        pv_peak_anchor_mw=float(pv_anchor),
        tie_normal_state=str(tie["normal_state"]),
        client_reverse_ratio=float(client_reverse_ratio),
    )
    return case, feeders, injections, station_pv


def net_export_surplus_mw(
    case: ReverseTransferCase,
    load_factor: float,
    pv_scale: float,
) -> tuple[float, float, float]:
    """构造墩南线高光伏场景的净外送富余功率。

    surplus = max(PV - load, 0)。负荷采用年度最大有功乘 load_factor，仅作为
    规划场景代理；不是同步历史量测。
    """
    if load_factor < 0 or pv_scale < 0:
        raise ValueError("load_factor and pv_scale must be non-negative")
    gross_pv = case.pv_peak_anchor_mw * pv_scale
    local_load_proxy = case.donor_feeder_peak_p_mw * load_factor
    surplus = max(gross_pv - local_load_proxy, 0.0)
    return gross_pv, local_load_proxy, surplus


def scenario_sweep(
    case: ReverseTransferCase,
    load_factors: Iterable[float] = (0.0, 0.3, 0.5, 0.7),
    pv_scales: Iterable[float] = (0.8, 0.9, 1.0, 1.2, 1.5),
) -> pd.DataFrame:
    """两层规划扫描：先用既有联络，再计算新联络容量需求。"""
    rows: list[dict[str, float | str | bool]] = []
    tie_cap = case.existing_tie_reverse_capacity_mw
    station_headroom = case.receiver_station_reverse_headroom_mw
    donor_reverse_base = max(-case.donor_station_min_net_load_mw, 0.0)

    for load_factor in load_factors:
        for pv_scale in pv_scales:
            gross_pv, local_load, surplus = net_export_surplus_mw(case, load_factor, pv_scale)

            existing_transfer = min(surplus, tie_cap, station_headroom)
            residual_after_existing = max(surplus - existing_transfer, 0.0)

            remaining_station_headroom = max(station_headroom - existing_transfer, 0.0)
            new_transfer = min(residual_after_existing, remaining_station_headroom)
            unresolved_after_station = max(residual_after_existing - new_transfer, 0.0)

            required_new_effective_mva = (
                new_transfer / case.client_reverse_ratio if new_transfer > 0 else 0.0
            )
            total_transfer = existing_transfer + new_transfer

            donor_after_existing = case.donor_station_min_net_load_mw + existing_transfer
            receiver_after_existing = case.receiver_station_min_net_load_mw - existing_transfer
            donor_after_all = case.donor_station_min_net_load_mw + total_transfer
            receiver_after_all = case.receiver_station_min_net_load_mw - total_transfer

            evidence = (
                "ZERO_LOCAL_LOAD_CONSERVATIVE_UPPER_BOUND"
                if abs(load_factor) < 1e-12
                else "S2_PLANNING_LOAD_FACTOR_WITH_REAL_PV_OUTPUT_ANCHOR"
            )

            rows.append(
                {
                    "load_factor": float(load_factor),
                    "pv_scale": float(pv_scale),
                    "gross_pv_anchor_scaled_mw": gross_pv,
                    "local_load_proxy_mw": local_load,
                    "net_export_surplus_mw": surplus,
                    "existing_tie_reverse_capacity_mw": tie_cap,
                    "existing_tie_transfer_mw": existing_transfer,
                    "existing_tie_receiver_path_loading_pct": (
                        existing_transfer / case.receiver_path_effective_limit_mva * 100.0
                    ),
                    "existing_tie_client_reverse_80_pass": (
                        existing_transfer
                        <= case.client_reverse_ratio * case.receiver_path_effective_limit_mva + 1e-12
                    ),
                    "receiver_station_reverse_headroom_mw": station_headroom,
                    "residual_after_existing_tie_mw": residual_after_existing,
                    "new_tie_transfer_required_mw": new_transfer,
                    "new_tie_min_effective_capacity_mva": required_new_effective_mva,
                    "unresolved_after_receiver_station_screen_mw": unresolved_after_station,
                    "new_tie_required": bool(new_transfer > 1e-9),
                    "donor_station_2025_min_anchor_mw": case.donor_station_min_net_load_mw,
                    "receiver_station_2025_min_anchor_mw": case.receiver_station_min_net_load_mw,
                    "donor_station_after_existing_screen_mw": donor_after_existing,
                    "receiver_station_after_existing_screen_mw": receiver_after_existing,
                    "donor_station_after_all_screen_mw": donor_after_all,
                    "receiver_station_after_all_screen_mw": receiver_after_all,
                    "donor_reverse_relief_pct_of_2025_min_anchor": (
                        total_transfer / donor_reverse_base * 100.0 if donor_reverse_base > 0 else 0.0
                    ),
                    "scenario_evidence": evidence,
                    "synchronization_status": "PLANNING_ENVELOPE_NOT_HISTORICAL_SYNCHRONOUS",
                }
            )
    return pd.DataFrame(rows)


def receiver_feeder_screen(
    case: ReverseTransferCase,
    feeders: pd.DataFrame,
    injections: pd.DataFrame,
    load_factor: float,
    pv_scale: float,
    required_transfer_mw: float = 0.0,
) -> pd.DataFrame:
    """对河湾变下辖馈线进行新联络承接能力的馈线级预筛。

    该筛查只使用馈线运行允许容量、规划负荷代理和已知 PV 汇总。它不能替代
    新联络接入点到站端的真实路径热限、电压及短路校核，因此只用于确定候选
    馈线优先级，不直接给出线路落点。
    """
    receiver_feeders = feeders.loc[feeders["station_id"] == case.receiver_station_id].copy()
    rows: list[dict[str, float | str | bool]] = []

    for _, feeder in receiver_feeders.iterrows():
        feeder_id = str(feeder["feeder_id"])
        inj_rows = injections.loc[injections["feeder_id"] == feeder_id]
        if inj_rows.empty:
            continue
        inj = inj_rows.iloc[0]
        pv_mw = _extract_pv_mw(inj["pv_total_or_anchor"])
        pv_mw = 0.0 if pv_mw is None else pv_mw

        load_proxy = float(inj["model_boundary_p_mw"]) * load_factor
        pv_proxy = pv_mw * pv_scale
        pre_transfer_net = load_proxy - pv_proxy
        feeder_reverse_control_mw = case.client_reverse_ratio * float(feeder["max_allowed_mva_at_10kv"])
        # pre_transfer_net > 0 表示本地负荷可先吸收外来光伏；<0 表示馈线已反送。
        additional_export_headroom = max(feeder_reverse_control_mw + pre_transfer_net, 0.0)

        is_existing_receiver = feeder_id == case.receiver_feeder_id
        if is_existing_receiver:
            route_status = "EXISTING_TIE002_ROUTE_READY"
            route_specific_headroom = case.existing_tie_reverse_capacity_mw
        else:
            route_status = "FEEDER_LEVEL_SCREEN_ONLY_ROUTE_AND_CORRIDOR_PENDING"
            route_specific_headroom = float("nan")

        rows.append(
            {
                "feeder_id": feeder_id,
                "feeder_alias": str(feeder["feeder_alias"]),
                "load_factor": float(load_factor),
                "pv_scale": float(pv_scale),
                "local_load_proxy_mw": load_proxy,
                "known_pv_proxy_mw": pv_proxy,
                "pre_transfer_net_load_mw": pre_transfer_net,
                "feeder_operating_limit_mva": float(feeder["max_allowed_mva_at_10kv"]),
                "feeder_reverse_80_control_mw": feeder_reverse_control_mw,
                "additional_export_headroom_feeder_level_mw": additional_export_headroom,
                "required_transfer_mw": float(required_transfer_mw),
                "feeder_level_capacity_pass": additional_export_headroom + 1e-12 >= required_transfer_mw,
                "is_existing_tie002_receiver": is_existing_receiver,
                "route_specific_existing_headroom_mw": route_specific_headroom,
                "route_status": route_status,
                "new_route_independent_path_required": bool(is_existing_receiver),
            }
        )

    result = pd.DataFrame(rows)
    if result.empty:
        return result
    result["alternate_new_tie_priority"] = (~result["is_existing_tie002_receiver"]).astype(int)
    result = result.sort_values(
        ["feeder_level_capacity_pass", "alternate_new_tie_priority", "additional_export_headroom_feeder_level_mw"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    result["screen_rank"] = range(1, len(result) + 1)
    return result.drop(columns=["alternate_new_tie_priority"])


def build_case_summary(case: ReverseTransferCase, sweep: pd.DataFrame) -> pd.DataFrame:
    """提取首轮工程讨论需要的关键数值。"""
    def pick(load_factor: float, pv_scale: float) -> pd.Series:
        rows = sweep.loc[
            (sweep["load_factor"].sub(load_factor).abs() < 1e-12)
            & (sweep["pv_scale"].sub(pv_scale).abs() < 1e-12)
        ]
        if rows.empty:
            raise ValueError(f"missing scenario load_factor={load_factor}, pv_scale={pv_scale}")
        return rows.iloc[0]

    z_current = pick(0.0, 1.0)
    s2_current = pick(0.3, 1.0)
    z_future12 = pick(0.0, 1.2)
    s2_future15 = pick(0.3, 1.5)

    items = [
        ("model_core", "HIGH_PV_REVERSE_POWER_CROSS_STATION_BOUNDARY_RECONFIGURATION"),
        ("tie_id", case.tie_id),
        ("donor_station", case.donor_station_name),
        ("receiver_station", case.receiver_station_name),
        ("donor_feeder", case.donor_feeder_id),
        ("receiver_feeder", case.receiver_feeder_id),
        ("pv_peak_output_anchor_mw", case.pv_peak_anchor_mw),
        ("donor_path_effective_limit_mva", case.donor_path_effective_limit_mva),
        ("receiver_path_effective_limit_mva", case.receiver_path_effective_limit_mva),
        ("existing_tie_reverse_capacity_mw", case.existing_tie_reverse_capacity_mw),
        ("receiver_station_n1_screen_headroom_mw", case.receiver_station_reverse_headroom_mw),
        ("current_zero_load_export_mw", float(z_current["net_export_surplus_mw"])),
        ("current_zero_load_existing_tie_loading_pct", float(z_current["existing_tie_receiver_path_loading_pct"])),
        ("current_zero_load_new_tie_required", bool(z_current["new_tie_required"])),
        ("current_s2_lf030_export_mw", float(s2_current["net_export_surplus_mw"])),
        ("future_120pct_zero_load_residual_after_existing_mw", float(z_future12["residual_after_existing_tie_mw"])),
        ("future_120pct_zero_load_new_tie_min_effective_mva", float(z_future12["new_tie_min_effective_capacity_mva"])),
        ("future_150pct_lf030_residual_after_existing_mw", float(s2_future15["residual_after_existing_tie_mw"])),
        ("future_150pct_lf030_new_tie_min_effective_mva", float(s2_future15["new_tie_min_effective_capacity_mva"])),
        ("station_anchor_semantics", "INDEPENDENT_STRESS_ANCHORS_NOT_SYNCHRONOUS_DUAL_STATION_FLOW"),
    ]
    return pd.DataFrame(items, columns=["item", "value"])
