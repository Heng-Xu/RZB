#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
双向Z4-LCC 全寿命周期成本仿真器（论文核心方法实现，v4 承重缺陷修复版）

v4 修复（对应 分析/07 独立复核报告 G0/bug#1/X4/X3；v3 的"弹性恒优/三区段"已被自身输出否证）：
  G0  承重对比口径纠正：论文主图改为"决策方法（候选R∈{1.5..2.6}逐档取最小LCC，
      见 sweep_experiments.build_candidate/sweep_penetration）vs 刚性R=2.0"。
      **不再是 v3 的固定2.0 vs 固定2.3——后者从不调用决策矩阵。**
  bug#1 弃光不双计：compute() 先算弃光，反向馈线+主变潮流扣除 curtailed_kw 并封顶反向限额，
      消除 v3 对弹性方案高渗透段成本的虚高。
  X4  N-1 对**未来峰荷** peak×(1+g)^n 校核（g/n 见 YAML reliability）：低 R 在负荷增长后
      N-1 不足→付可靠性代价（v3 在默认参数下该项恒为0、失效）。
      ⚠ 低 R 下探 floor 对 (g,n) 及 N-1 假设(n1_overload_factor/VOLL/n1_equiv_hours)敏感，
      详 sensitivity_growth.py / 实验03 §4.4。
  X3  联络度 CD 经 N-1 转供项 cd×峰荷 进入可靠性：CD 强→可接受更低 R（肖峻 TSC），梯度随 g 变化。

v2/v3 既有修复（保留）：F1 PV真实注入潮流 / F2 Z1低档+扩容系数 / F3 弃光惩罚 /
  口径拆分（源荷比 vs 电量渗透率）/ X2 Z4主变损耗（P0空载+Pk×β²负载，容载比-损耗真实耦合）

结论口径（详 实验/03_实验结果摘要 v4）：刚性单值2.0系统性次优、决策方法节省2-4%；
  **升方向(高渗透→R≥2.3)稳健**，**降方向(低渗透floor<2.0)条件于负荷增长与N-1假设**。

⚠ make_plan_a / make_plan_b 与 --compare 为**遗留单点对照**（固定R2.0 vs 固定R2.3），
  已被 G0 的自适应对比取代，仅作快速冒烟检查，**勿用于论文结论**。

用法：
    python lcc_simulator.py --compare --pv 9000   # 遗留单点对照（非论文口径）
    # 论文主图/矩阵：python sweep_experiments.py --out results
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"

REVERSE_LOAD_FACTOR = 0.3      # 春秋午间小负荷系数
PV_PEAK_FACTOR = 0.9           # PV出力峰值系数（相对装机）
REVERSE_TX_LIMIT = 0.85        # 主变反向负载限额（留15%裕度，2025导则反向重载校验）
CURTAIL_SHAPE_FACTOR = 0.5     # 弃光能量形状系数
ANNUAL_LOAD_HOURS = 4500       # 负荷年最大利用小时数
PV_ANNUAL_YIELD_PER_KWP = 1396  # 徐州 kWh/kWp/年（PVGIS实测校准）
N_TRANSFORMERS = 2             # 典型站主变台数
RIGID_RATIO = 2.0              # 刚性容载比基准
DEFAULT_CD = 0.45              # A/B扫描用的代表性联络度（中等）


def load_cost_params(path: Optional[Path] = None) -> dict:
    p = path or (DATASETS / "cost_params" / "baseline_costs.yaml")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_ieee33() -> tuple[pd.DataFrame, pd.DataFrame]:
    bus = pd.read_csv(DATASETS / "ieee33" / "ieee33_bus.csv")
    branch = pd.read_csv(DATASETS / "ieee33" / "ieee33_branch.csv")
    return bus, branch


def capital_recovery_factor(rate: float, years: int) -> float:
    if rate <= 0:
        return 1.0 / years
    f = (1 + rate) ** years
    return rate * f / (f - 1)


def salvage_value(initial_cost: float, lifetime: int, used_years: int, rate: float) -> float:
    if used_years >= lifetime:
        return initial_cost * rate
    remaining = (lifetime - used_years) / lifetime
    return initial_cost * (rate + (1 - rate) * remaining * 0.1)


# ──────────────────────────────────────────────────────────────────────────────
# Z4 损耗：馈线 + 主变（X2修复）
# ──────────────────────────────────────────────────────────────────────────────


def feeder_z4_loss(
    branch, p_fwd, p_rev, t_fwd, t_rev,
    alpha_fwd=1.0, alpha_rev=1.2, elec_price=0.55, v_kv=12.66,
) -> dict:
    """10kV馈线电阻损耗 Σ(P²R/V²)，分正反向。"""
    r = branch["r_ohm"].to_numpy()
    v2 = v_kv ** 2
    loss_fwd = (p_fwd ** 2 * r) / (v2 * 1000)
    loss_rev = (p_rev ** 2 * r) / (v2 * 1000)
    e_fwd = float(np.sum(loss_fwd) * t_fwd * alpha_fwd)
    e_rev = float(np.sum(loss_rev) * t_rev * alpha_rev)
    return {"fwd_kwh": e_fwd, "rev_kwh": e_rev}


def transformer_z4_loss(
    tx_capacity_mva, fwd_peak_kva, rev_peak_kva,
    p0_coeff, pk_coeff, t_fwd, t_rev,
    alpha_rev=1.2, elec_price=0.55,
) -> dict:
    """
    X2核心：主变损耗 = 空载损耗(恒定) + 负载损耗(∝β²)。
    S_rated↑(容载比↑) → P0↑(恒损)，β=flow/S_rated↓ → 负载损耗↓ ⇒ 容载比-损耗耦合。
    """
    s_rated_kva = tx_capacity_mva * 1000
    p0_kw = p0_coeff * s_rated_kva                      # 空载损耗（全年8760h恒定）
    pk_rated_kw = pk_coeff * s_rated_kva                # 额定负载损耗
    beta_fwd = fwd_peak_kva / s_rated_kva if s_rated_kva > 0 else 0
    beta_rev = rev_peak_kva / s_rated_kva if s_rated_kva > 0 else 0

    e_noload = p0_kw * 8760
    e_load_fwd = pk_rated_kw * (beta_fwd ** 2) * t_fwd
    e_load_rev = pk_rated_kw * (beta_rev ** 2) * t_rev * alpha_rev
    return {
        "noload_kwh": e_noload,
        "load_fwd_kwh": e_load_fwd,
        "load_rev_kwh": e_load_rev,
        "beta_fwd": beta_fwd,
        "beta_rev": beta_rev,
    }


# ──────────────────────────────────────────────────────────────────────────────
# 简化潮流（F1：PV真实注入）
# ──────────────────────────────────────────────────────────────────────────────


def estimate_branch_flow_simplified(
    bus, branch, pv_buses, pv_kwp_total, pv_factor, load_factor,
    storage_absorb_kw=0.0,
) -> tuple[np.ndarray, np.ndarray]:
    bus = bus.copy()
    bus["p_net_kw"] = bus["p_load_kw"] * load_factor
    if pv_buses and pv_kwp_total > 0 and pv_factor > 0:
        injection = max(0.0, pv_kwp_total * pv_factor - storage_absorb_kw)
        per_bus = injection / len(pv_buses)
        bus.loc[bus["bus"].isin(pv_buses), "p_net_kw"] -= per_bus

    children: dict = {b: [] for b in bus["bus"]}
    for _, br in branch.iterrows():
        children[br["from_bus"]].append(br["to_bus"])
    p_map = dict(zip(bus["bus"], bus["p_net_kw"]))
    cache: dict = {}

    def subtree(b):
        if b in cache:
            return cache[b]
        p = float(p_map[b])
        for c in children.get(b, []):
            p += subtree(c)
        cache[b] = p
        return p

    flows = np.array([subtree(br["to_bus"]) for _, br in branch.iterrows()], dtype=float)
    return np.where(flows > 0, flows, 0), np.where(flows < 0, -flows, 0)


# ──────────────────────────────────────────────────────────────────────────────
# 反向承载力校核（准入硬闸辅助）
# ──────────────────────────────────────────────────────────────────────────────


def reverse_voltage_max_pu(bus, branch, rev_flows, v_kv=12.66, q_flows=None) -> float:
    """
    反送场景下最大节点电压（标幺）。沿径向树从根累加压升：
      ΔU_pu(支路) = (P_rev·R + Q_rev·X) / (V_kV² · 1000)
    Q 缺省按单位功率因数取 0（与项目既有简化潮流口径一致）。返回 max(1.0+ΔU)。
    """
    r = branch["r_ohm"].to_numpy()
    x = branch["x_ohm"].to_numpy()
    p = np.asarray(rev_flows, dtype=float)
    q = np.zeros_like(p) if q_flows is None else np.asarray(q_flows, dtype=float)
    dv = (p * r + q * x) / (v_kv ** 2 * 1000.0)        # 每支路 p.u. 压升
    from_b = branch["from_bus"].to_numpy().astype(int)
    to_b = branch["to_bus"].to_numpy().astype(int)
    rise = {int(b): 0.0 for b in bus["bus"]}
    root = int(bus["bus"].min())                       # IEEE33 根节点（slack）
    assigned = {root}
    edges = list(zip(from_b, to_b, dv))
    changed = True
    while changed:                                     # 径向连通 → 逐层传播至收敛
        changed = False
        for f, t, d in edges:
            if f in assigned and t not in assigned:
                rise[t] = rise[f] + float(d)
                assigned.add(t)
                changed = True
    return 1.0 + max(rise.values())


def assess_reverse_capacity(rev_after_storage_kva, tx_mva, max_voltage_pu,
                            volt_limit=1.05) -> dict:
    """
    反向承载力校核：
      主变反向重载（准入硬闸）= 经本方案储能吸收后的主变反向视在 ≤ REVERSE_TX_LIMIT×额定。
        **不靠弃光补救**——弃光只是末端惩罚，不作为"通过"手段；纯主变方案越限即判不通过。
        （2025导则反向重载校验；容载比唯一能控制的量 tx=R×峰荷，故此判据对R单调区分。）
      反向电压：片区级承载力旗标，与R无关（馈线侧），**不参与R准入**；
        公开数据(IEEE33弱馈线)上仅作方法演示，真实阈值待Phase2用徐州实测R/X标定。
    """
    rev_limit_kva = tx_mva * 1000 * REVERSE_TX_LIMIT
    overload_kva = max(0.0, rev_after_storage_kva - rev_limit_kva)
    return {
        "passed": overload_kva <= 0.0,
        "reverse_overload_kw": round(float(overload_kva), 1),
        "max_voltage_pu": round(float(max_voltage_pu), 4),
        "voltage_exceed": bool(max_voltage_pu > volt_limit),
    }


# ──────────────────────────────────────────────────────────────────────────────
# 配置与结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class ScenarioConfig:
    name: str
    tx_capacity_mva: float
    pv_kwp_total: float
    pv_buses: list[int] = field(default_factory=list)
    with_storage: bool = False
    storage_mwh: float = 0.0
    storage_mw: float = 0.0
    line_expansion_km: float = 0.0
    expansion_from_mva: float = 0.0
    interconnection_cd: float = DEFAULT_CD   # X3：联络度（0弱~1强）


@dataclass
class LCCResult:
    scenario_name: str
    Z1_yuan: float
    Z2_yuan: float
    Z3_yuan_per_year: float
    Z4_yuan_per_year: float
    Z4_feeder_yuan: float
    Z4_transformer_yuan: float
    Z4_reverse_share: float
    Z5_yuan: float
    storage_capex_yuan: float
    curtailment_yuan_per_year: float
    curtailed_kwh_per_year: float
    reliability_yuan_per_year: float
    eens_kwh_per_year: float
    total_capex_yuan: float
    annualized_cost_yuan_per_year: float
    capacity_load_ratio: float
    source_load_ratio: float
    energy_penetration: float
    # 反向承载力校核
    reverse_check_passed: bool = True       # 主变反向重载准入硬闸（含本方案储能，不靠弃光救）
    reverse_overload_kw: float = 0.0        # 反向越限功率（>0=纯主变越限量=治理需求）
    max_reverse_voltage_pu: float = 1.0     # 片区级反送电压旗标
    voltage_exceed: bool = False            # 反送电压是否越上限（片区旗标，非R判据）
    curtail_ratio: float = 0.0              # 弃光率（信息项，可行方案应≈0）

    def to_dict(self) -> dict:
        return asdict(self)


class LCCSimulator:
    def __init__(self, cost_params: dict):
        self.c = cost_params

    def _z1(self, mva, expansion_from_mva=0.0):
        scale = self.c["Z1_substation"]["scaling"]
        x = np.array([s["capacity_mva"] for s in scale])
        y = np.array([s["cost_wan"] for s in scale]) * 1e4

        def interp(m):
            if m <= x[0]:
                return float(y[0] * (m / x[0]))
            if m >= x[-1]:
                return float(y[-1] * (m / x[-1]))
            return float(np.interp(m, x, y))

        if expansion_from_mva > 0 and mva > expansion_from_mva:
            ef = self.c["Z1_substation"]["expansion_factor"]
            base = interp(expansion_from_mva)
            return base + (interp(mva) - base) * ef
        return interp(mva)

    def _z2(self, branch, extra_km=0.0):
        km = branch["length_km_est"].sum() + extra_km
        return float(km * self.c["Z2_line"]["effective_cost_per_km"] * 1e4)

    def _z3(self, z1, z2, storage_capex=0.0):
        m = self.c["Z3_maintenance"]
        return float(z1 * m["rate_substation"] + z2 * m["rate_line"]
                     + storage_capex * m["rate_storage"])

    def _z5(self, z1, z2, horizon):
        z = self.c["Z5_salvage"]
        sub = salvage_value(z1, z["substation_lifetime_years"], horizon, z["salvage_rate"])
        line = salvage_value(z2, z["line_lifetime_years"], horizon, z["salvage_rate"])
        rate = self.c["economics"]["discount_rate"]
        return float((sub + line) / ((1 + rate) ** horizon))

    def _storage_capex(self, mwh, mw, factor=1.0):
        s = self.c["storage_BESS"]
        return float((mwh * 1000 * s["energy_cost_yuan_per_kwh"]
                      + mw * 1000 * s["power_cost_yuan_per_kw"]) * factor)

    def _curtailment(self, pv_kwp, load_min_kw, tx_mva, storage_mw, t_rev):
        rev_peak = max(0.0, pv_kwp * PV_PEAK_FACTOR - load_min_kw)
        rev_after_storage = max(0.0, rev_peak - storage_mw * 1000)
        rev_limit = tx_mva * 1000 * REVERSE_TX_LIMIT
        curtailed_kw = max(0.0, rev_after_storage - rev_limit)
        curtailed_kwh = curtailed_kw * t_rev * CURTAIL_SHAPE_FACTOR
        curtail_yuan = curtailed_kwh * self.c["Z4_loss"]["curtailment_penalty_yuan_per_kwh"]
        return curtailed_kwh, curtail_yuan, curtailed_kw

    def _reliability(self, tx_mva, peak_mva, peak_load_kw, cd):
        """
        X4+X3：正向N-1缺供风险成本（对**未来峰荷**校核——这是低R付出代价的物理来源）。
        容载比按现状峰荷定义，但N-1充裕度须在规划期内保持，故校核对象为
          未来峰荷 = 现状峰荷×(1+g)^n （g=年增长率, n=校核年限）。
        口径统一用视在容量（与容载比定义一致）：
          N-1可用容量 = n1_overload×(S/台数)×(台数-1) + CD×现状峰荷视在可转供
          容载比2.0+2台 → N-1余一台=S/2=现状峰荷视在；负荷增长后出现缺额。
          缺额需更高R或更强联络度CD补足（肖峻TSC机制，X3）：
            CD弱 → 低R缺额大、代价高 → 推荐R上移；
            CD强 → 站间互济补足 → 低R仍N-1充裕 → 可降R（X3梯度由此产生）。
        缺供电量按缺额视在×功率因数折有功 × 等效缺供小时。
        """
        rcfg = self.c["reliability"]
        peak_kva = peak_mva * 1000
        g = rcfg.get("load_growth_rate", 0.0)
        n = rcfg.get("growth_horizon_years", 0)
        future_peak_kva = peak_kva * (1.0 + g) ** n
        per_tx = tx_mva * 1000 / N_TRANSFORMERS
        n1_self = rcfg["n1_overload_factor"] * per_tx * (N_TRANSFORMERS - 1)
        n1_transfer = cd * peak_kva                       # 站间互济按现状峰荷可转供（X3）
        deficit_kva = max(0.0, future_peak_kva - n1_self - n1_transfer)
        pf = peak_load_kw / peak_kva if peak_kva > 0 else 0.95
        deficit_kw = deficit_kva * pf
        eens_kwh = deficit_kw * rcfg["n1_equiv_hours"]
        return eens_kwh, eens_kwh * rcfg["voll_yuan_per_kwh"]

    def compute(self, bus, branch, scenario, loss_hours_fwd=None, loss_hours_rev=None):
        eco = self.c["economics"]
        horizon = eco["project_horizon_years"]
        rate = eco["discount_rate"]
        z4cfg = self.c["Z4_loss"]
        txcfg = self.c["transformer_loss"]
        price = z4cfg["electricity_price_yuan_per_kwh"]

        peak_load_kw = float(bus["p_load_kw"].sum())
        load_min_kw = peak_load_kw * REVERSE_LOAD_FACTOR
        peak_mva = math.hypot(peak_load_kw, bus["q_load_kvar"].sum()) / 1000

        # 1) capex
        z1 = self._z1(scenario.tx_capacity_mva, scenario.expansion_from_mva)
        z2 = self._z2(branch, scenario.line_expansion_km)
        storage_capex = self._storage_capex(scenario.storage_mwh, scenario.storage_mw) \
            if scenario.with_storage else 0.0
        total_capex = z1 + z2 + storage_capex

        # 2) O&M
        z3 = self._z3(z1, z2, storage_capex)

        # 3) Z4 = 馈线 + 主变（X2）
        t_fwd = loss_hours_fwd or z4cfg["loss_utilization_hours"]["forward"]
        t_rev = loss_hours_rev or z4cfg["loss_utilization_hours"]["reverse"]
        storage_absorb = scenario.storage_mw * 1000 if scenario.with_storage else 0.0

        # 弃光先算（bug#1修复）：被弃掉的反向功率不流过主变/馈线，不应计入Z4反向损耗
        curtailed_kwh, curtail_yuan, curtailed_kw = self._curtailment(
            scenario.pv_kwp_total, load_min_kw, scenario.tx_capacity_mva,
            scenario.storage_mw if scenario.with_storage else 0.0, t_rev)
        rev_absorb = storage_absorb + curtailed_kw   # 储能吸收 + 弃光削减，二者均不流过设备

        fwd_peak, _ = estimate_branch_flow_simplified(
            bus, branch, scenario.pv_buses, scenario.pv_kwp_total, 0.0, 1.0)
        _, rev_peak = estimate_branch_flow_simplified(
            bus, branch, scenario.pv_buses, scenario.pv_kwp_total,
            PV_PEAK_FACTOR, REVERSE_LOAD_FACTOR, storage_absorb_kw=rev_absorb)

        feeder = feeder_z4_loss(branch, fwd_peak, rev_peak, t_fwd, t_rev,
                                z4cfg["alpha_forward"], z4cfg["alpha_reverse"], price)
        # 主变潮流：正向=峰荷视在，反向=PV峰注入-小负荷-储能-弃光（封顶反向限额，视在近似）
        tx_fwd_kva = peak_load_kw / 0.95
        tx_rev_kva = max(0.0, scenario.pv_kwp_total * PV_PEAK_FACTOR - load_min_kw
                         - rev_absorb)
        tx = transformer_z4_loss(
            scenario.tx_capacity_mva, tx_fwd_kva, tx_rev_kva,
            txcfg["p0_coeff_kw_per_kva"], txcfg["pk_coeff_kw_per_kva"],
            t_fwd, t_rev, z4cfg["alpha_reverse"], price)

        z4_feeder_kwh = feeder["fwd_kwh"] + feeder["rev_kwh"]
        z4_tx_kwh = tx["noload_kwh"] + tx["load_fwd_kwh"] + tx["load_rev_kwh"]
        z4_rev_kwh = feeder["rev_kwh"] + tx["load_rev_kwh"]
        z4_total_kwh = z4_feeder_kwh + z4_tx_kwh
        z4_total_yuan = z4_total_kwh * price

        # 4) 弃光成本已在 Z4 前算出（curtail_yuan / curtailed_kwh）

        # 4b) 反向承载力校核：主变反向重载=准入硬闸（仅计本方案储能，不靠弃光救）；电压=片区旗标
        rc_cfg = self.c.get("reverse_check", {})
        rev_after_storage = max(0.0, scenario.pv_kwp_total * PV_PEAK_FACTOR
                                - load_min_kw - storage_absorb)
        max_v = reverse_voltage_max_pu(bus, branch, rev_peak)
        rcheck = assess_reverse_capacity(
            rev_after_storage, scenario.tx_capacity_mva, max_v,
            rc_cfg.get("voltage_limit_pu", 1.05))
        pv_gross_kwh = scenario.pv_kwp_total * PV_ANNUAL_YIELD_PER_KWP
        curtail_ratio = curtailed_kwh / pv_gross_kwh if pv_gross_kwh > 0 else 0.0

        # 5) 可靠性（X4 + X3联络度）
        eens_kwh, reliability_yuan = self._reliability(
            scenario.tx_capacity_mva, peak_mva, peak_load_kw,
            scenario.interconnection_cd)

        # 6) 残值 + 年费用化
        z5_pv = self._z5(z1, z2, horizon)
        crf = capital_recovery_factor(rate, horizon)
        annualized = ((total_capex - z5_pv) * crf + z3 + z4_total_yuan
                      + curtail_yuan + reliability_yuan)

        # 7) 指标
        # 容载比按国标口径=主变容量(MVA)/最大有功负荷(MW)（非视在；DL/T5729）
        cap_load_ratio = scenario.tx_capacity_mva / (peak_load_kw / 1000) if peak_load_kw > 0 else float("inf")
        slr = scenario.pv_kwp_total / peak_load_kw if peak_load_kw > 0 else 0
        pv_annual_kwh = scenario.pv_kwp_total * PV_ANNUAL_YIELD_PER_KWP - curtailed_kwh
        epen = pv_annual_kwh / (peak_load_kw * ANNUAL_LOAD_HOURS) if peak_load_kw > 0 else 0

        return LCCResult(
            scenario_name=scenario.name,
            Z1_yuan=round(z1, 2), Z2_yuan=round(z2, 2),
            Z3_yuan_per_year=round(z3, 2),
            Z4_yuan_per_year=round(z4_total_yuan, 2),
            Z4_feeder_yuan=round(z4_feeder_kwh * price, 2),
            Z4_transformer_yuan=round(z4_tx_kwh * price, 2),
            Z4_reverse_share=round(z4_rev_kwh / z4_total_kwh if z4_total_kwh > 0 else 0, 4),
            Z5_yuan=round(z5_pv, 2),
            storage_capex_yuan=round(storage_capex, 2),
            curtailment_yuan_per_year=round(curtail_yuan, 2),
            curtailed_kwh_per_year=round(curtailed_kwh, 1),
            reliability_yuan_per_year=round(reliability_yuan, 2),
            eens_kwh_per_year=round(eens_kwh, 1),
            total_capex_yuan=round(total_capex, 2),
            annualized_cost_yuan_per_year=round(annualized, 2),
            capacity_load_ratio=round(cap_load_ratio, 3),
            source_load_ratio=round(slr, 3),
            energy_penetration=round(epen, 4),
            reverse_check_passed=rcheck["passed"],
            reverse_overload_kw=rcheck["reverse_overload_kw"],
            max_reverse_voltage_pu=rcheck["max_voltage_pu"],
            voltage_exceed=rcheck["voltage_exceed"],
            curtail_ratio=round(curtail_ratio, 4),
        )


# ──────────────────────────────────────────────────────────────────────────────
# 场景构造（X1：A方案触发式 + 开题口径G4）
# ──────────────────────────────────────────────────────────────────────────────


def _reverse_overload_kw(pv_kwp, peak_load_kw, tx_mva):
    """R=tx的主变在反送场景下的越限功率（kW），>0即需治理。"""
    load_min = peak_load_kw * REVERSE_LOAD_FACTOR
    rev_peak = max(0.0, pv_kwp * PV_PEAK_FACTOR - load_min)
    rev_limit = tx_mva * 1000 * REVERSE_TX_LIMIT
    return max(0.0, rev_peak - rev_limit)


def make_plan_a(peak_mva, pv_kwp, pv_buses, peak_load_kw=None, cd=DEFAULT_CD):
    """
    方案A（刚性R=2.0）：X1触发式——仅当R=2.0主变反送越限时才配储(按超限量)+联络。
    低渗透无越限 → A=纯刚性主变（不买储能/联络），与B在低渗透段公平对比。
    """
    if peak_load_kw is None:
        peak_load_kw = peak_mva * 1000 * 0.85
    tx_a = (peak_load_kw / 1000) * RIGID_RATIO   # 有功口径定容（国标容载比）
    overload_kw = _reverse_overload_kw(pv_kwp, peak_load_kw, tx_a)

    if overload_kw > 0:
        storage_mw = overload_kw / 1000          # 储能功率覆盖反送超限量
        storage_mwh = storage_mw * 2.0           # 2h时长
        return ScenarioConfig(
            name="方案A_刚性2.0_联络+配储",
            tx_capacity_mva=tx_a, pv_kwp_total=pv_kwp, pv_buses=pv_buses,
            with_storage=True, storage_mwh=storage_mwh, storage_mw=storage_mw,
            line_expansion_km=2.0, interconnection_cd=cd)
    return ScenarioConfig(
        name="方案A_刚性2.0_纯主变", tx_capacity_mva=tx_a,
        pv_kwp_total=pv_kwp, pv_buses=pv_buses,
        with_storage=False, line_expansion_km=0.0, interconnection_cd=cd)


def make_plan_b(peak_mva, pv_kwp, pv_buses, elastic_ratio=2.3, cd=DEFAULT_CD, peak_load_kw=None):
    """方案B（弹性R=2.3）：主变增容（增量按扩容系数计价），无网架/无储，反送超限弃光。"""
    p_mw = (peak_load_kw / 1000) if peak_load_kw is not None else peak_mva  # 有功口径定容（国标容载比）
    return ScenarioConfig(
        name=f"方案B_弹性{elastic_ratio}_增容",
        tx_capacity_mva=p_mw * elastic_ratio, pv_kwp_total=pv_kwp, pv_buses=pv_buses,
        with_storage=False, line_expansion_km=0.0,
        expansion_from_mva=p_mw * RIGID_RATIO, interconnection_cd=cd)


DEFAULT_PV_BUSES = [18, 22, 24, 25, 30, 32]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="ieee33", choices=["ieee33"])
    ap.add_argument("--pv", type=float, default=2500)
    ap.add_argument("--cd", type=float, default=DEFAULT_CD)
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--pv-buses", default="18,22,24,25,30,32")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cost = load_cost_params()
    bus, branch = load_ieee33()
    pv_buses = [int(b) for b in args.pv_buses.split(",") if b.strip()]
    peak_load_kw = float(bus["p_load_kw"].sum())
    peak_mva = math.hypot(peak_load_kw, bus["q_load_kvar"].sum()) / 1000
    sim = LCCSimulator(cost)

    if args.compare:
        a = sim.compute(bus, branch, make_plan_a(peak_mva, args.pv, pv_buses,
                                                 peak_load_kw, args.cd))
        b = sim.compute(bus, branch, make_plan_b(peak_mva, args.pv, pv_buses, cd=args.cd,
                                                 peak_load_kw=peak_load_kw))
        delta = a.annualized_cost_yuan_per_year - b.annualized_cost_yuan_per_year
        winner = "B(弹性)" if delta > 0 else "A(刚性)"
        if args.json:
            print(json.dumps({"A": a.to_dict(), "B": b.to_dict(),
                              "delta_yuan_per_year": round(delta, 2), "winner": winner},
                             ensure_ascii=False, indent=2))
        else:
            for tag, r in ((a.scenario_name, a), (b.scenario_name, b)):
                print(f"\n=== {tag} ===")
                for k, v in r.to_dict().items():
                    print(f"  {k:32s} = {v}")
            print(f"\n=== ΔLCC(A−B)={delta:+.0f} 元/年；优选 {winner} ===")
            print("⚠ 遗留单点对照（固定2.0 vs 固定2.3），非论文口径；"
                  "论文主图/矩阵见 sweep_experiments.py --out results")
        return 0

    scn = make_plan_b(peak_mva, args.pv, pv_buses, cd=args.cd, peak_load_kw=peak_load_kw)
    res = sim.compute(bus, branch, scn)
    print(json.dumps(res.to_dict(), ensure_ascii=False, indent=2) if args.json
          else "\n".join(f"{k:32s} = {v}" for k, v in res.to_dict().items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
