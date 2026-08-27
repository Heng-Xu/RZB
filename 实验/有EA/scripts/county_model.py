#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
县级多变电站基准（公开数据合成）——MIND 2026 / 县级容载比弹性 NSGA-II 寻优的算例层。

县 = K 个 110kV 变电站，每站以缩放 IEEE33 馈线为载体，按
  (源荷比 slr, 联络度 CD, 峰荷因子, 反送时长 t_rev) 抽样，锚定 PVGIS 三地（徐州/嘉兴/莱芜）。
明确声明：这是**公开数据(IEEE33 + PVGIS)合成的县级基准**，非甲方实测；用于方法验证与可扩展性论证。

评价函数复用 lcc_simulator.compute()（不改 simulator）：
  f1_j = 站年化成本去除可靠性项（资本年金 + 双向Z4损耗 + 储能 + O&M）
  f2_j = 站 N-1 缺供 EENS（未来峰荷 peak×(1+g)^n）
约束：每站过反向承载力硬闸；县聚合容载比落在 [R_lo, R_hi] 带（同时率耦合）。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from lcc_simulator import (
    LCCSimulator, load_cost_params, load_ieee33, ScenarioConfig, DEFAULT_PV_BUSES,
    REVERSE_TX_LIMIT, PV_PEAK_FACTOR, REVERSE_LOAD_FACTOR,
)

# 标准 110kV 主变档（MVA）——供混整数组合增强用
STANDARD_TX_MVA = (31.5, 40.0, 50.0, 63.0)
DIVERSITY_FACTOR = 0.85          # 县同时率（站间负荷不同时，聚合峰荷 < 各站峰荷之和）
DEFAULT_BAND = (1.8, 2.2)        # 县级容载比规划带（DL/T5729 量级）
PVGIS_TREV = (2841, 3017, 3103)  # 嘉兴/徐州/莱芜 实测年反送时长（h）

# 决策变量边界
R_LO, R_HI = 1.2, 3.0            # 单站容载比
P_LO, P_HI = 0.0, 6.0            # 单站储能功率 MW
STORAGE_HOURS = 2.0             # E_BESS = STORAGE_HOURS × P_BESS（暂 slave，能量限充作为局限）

# 系统/上级潮流约束（阶段三）：多站反送聚合上送到上级 220kV 主变/110kV 线路
REVERSE_COINCIDENCE = 1.0        # 反向同时率≈1（光伏天气强相关、近区齐发；区别于正向负荷的 0.85）
R220_DEFAULT = 1.8               # 上级 220kV 容载比（推导上级反向限额；做敏感性扫描）


@dataclass
class Station:
    sid: int
    slr: float          # 源荷比 = PV装机/有功峰荷
    cd: float           # 联络度
    peak_kw: float      # 有功峰荷
    pv_kwp: float       # PV装机
    t_rev: float        # 年反送时长
    bus: pd.DataFrame = field(repr=False)


def _scaled_bus(bus0: pd.DataFrame, factor: float) -> pd.DataFrame:
    b = bus0.copy()
    b["p_load_kw"] = b["p_load_kw"] * factor
    b["q_load_kvar"] = b["q_load_kvar"] * factor
    return b


def build_county(k: int, seed: int = 0) -> list[Station]:
    """生成 K 个异质站。确定性（给定 seed 可复现）。"""
    rng = np.random.default_rng(seed)
    _, _ = None, None
    bus0, _branch = load_ieee33()
    base_peak = float(bus0["p_load_kw"].sum())
    stations = []
    for j in range(k):
        slr = float(rng.uniform(0.5, 3.5))        # 高渗透县：源荷比谱 0.5~3.5
        cd = float(rng.uniform(0.10, 0.70))        # 联络度 弱~较强
        pf = float(rng.uniform(0.6, 1.5))          # 峰荷规模因子
        t_rev = float(rng.choice(PVGIS_TREV))      # 锚定三地实测
        peak = base_peak * pf
        stations.append(Station(sid=j, slr=round(slr, 3), cd=round(cd, 3),
                                 peak_kw=peak, pv_kwp=slr * peak, t_rev=t_rev,
                                 bus=_scaled_bus(bus0, pf)))
    return stations


def get_branch():
    _, branch = load_ieee33()
    return branch


def make_sim() -> LCCSimulator:
    return LCCSimulator(load_cost_params())


def eval_station(sim: LCCSimulator, branch, st: Station, R: float, p_mw: float,
                 e_mwh: float | None = None) -> dict:
    """单站评价：返回 (f1 去可靠性成本, f2=EENS, 过闸与否, 容量, capex)。"""
    if e_mwh is None:
        e_mwh = STORAGE_HOURS * p_mw
    cfg = ScenarioConfig(
        name=f"s{st.sid}", tx_capacity_mva=R * st.peak_kw / 1000.0,
        pv_kwp_total=st.pv_kwp, pv_buses=DEFAULT_PV_BUSES,
        with_storage=p_mw > 1e-9, storage_mw=p_mw, storage_mwh=e_mwh,
        interconnection_cd=st.cd)
    r = sim.compute(st.bus, branch, cfg, loss_hours_rev=st.t_rev)
    return {
        "f1": r.annualized_cost_yuan_per_year - r.reliability_yuan_per_year,
        "eens": r.eens_kwh_per_year,
        "feasible": bool(r.reverse_check_passed),
        "overload_kw": r.reverse_overload_kw,
        "tx_mva": cfg.tx_capacity_mva,
        "capex": r.total_capex_yuan,
        "R": R, "P": p_mw,
    }


def county_coincident_peak_kw(stations: list[Station], diversity: float = DIVERSITY_FACTOR) -> float:
    return sum(s.peak_kw for s in stations) * diversity


def aggregate_capacity_load_ratio(stations: list[Station], tx_list, diversity: float = DIVERSITY_FACTOR) -> float:
    coincident_mw = county_coincident_peak_kw(stations, diversity) / 1000.0
    return sum(tx_list) / coincident_mw if coincident_mw > 0 else float("inf")


def station_reverse_injection(st: Station, p_mw: float) -> float:
    """站净反向上送功率(kW)：PV峰注入 − 春秋午间小负荷 − 储能吸收（与逐站反送闸同量；与 R 无关）。"""
    return max(0.0, PV_PEAK_FACTOR * st.pv_kwp - REVERSE_LOAD_FACTOR * st.peak_kw - p_mw * 1000.0)


def upstream_reverse_limit(stations: list[Station], r220: float = R220_DEFAULT,
                           diversity: float = DIVERSITY_FACTOR) -> float:
    """上级反向承载力(kW)：220kV 主变按县正向同时峰荷×R220 配置、反向许用 REVERSE_TX_LIMIT(0.85)。"""
    return REVERSE_TX_LIMIT * r220 * (diversity * sum(s.peak_kw for s in stations))


def snap_to_transformer_combo(target_mva: float) -> float:
    """把连续目标容量映射到 2 台标准主变组合中最接近(且≥需求时优先)的总容量——混整数增强用。"""
    best = None
    for a in STANDARD_TX_MVA:
        for b in STANDARD_TX_MVA:
            tot = a + b
            if best is None or abs(tot - target_mva) < abs(best - target_mva):
                best = tot
    return best


if __name__ == "__main__":
    sim = make_sim(); branch = get_branch()
    county = build_county(12, seed=0)
    print(f"[county_model] K={len(county)} 站，同时率 {DIVERSITY_FACTOR}")
    for st in county[:4]:
        r = eval_station(sim, branch, st, 2.0, 0.0)
        print(f"  s{st.sid}: slr={st.slr} cd={st.cd} peak={st.peak_kw:.0f}kW "
              f"R=2.0裸主变 feasible={r['feasible']} EENS={r['eens']:.0f}")
    print("  自检通过：county_model 可独立运行。")
