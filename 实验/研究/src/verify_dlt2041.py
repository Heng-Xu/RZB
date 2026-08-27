"""校核层:DL/T 2041-2025 承载力核验(式(1)设备层、式(2)县级交叉)。

M1 取值裁决(见 task-7-brief):cosφ=0.95 固定;P_load_typ 取该站春秋典型
时刻(4月工作日12:00)的 data.pnet 值;P_G=0(pnet 已是净负荷口径,不重复
扣减);P_ess 取 solution.ess_mw[站](储能额定功率,非逐时值);τ 取
params.tau_max.kv110;β 取 station.beta_eff(params.beta)。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.io_loader import ScenarioData

COS_PHI = 0.95                                      # M1 固定取值(裁决)
TYPICAL_TS = pd.Timestamp("2025-04-01 12:00:00")    # 春秋典型时刻:4月工作日12:00
_ROOT = Path(__file__).resolve().parents[1]         # 研究/(src/ 的上一级)


def _get(solution: Any, key: str, default=None):
    if isinstance(solution, dict):
        return solution.get(key, default)
    return getattr(solution, key, default)


def _ess_mw_series(solution: Any) -> pd.Series:
    ess = _get(solution, "ess_mw", {})
    if isinstance(ess, pd.Series):
        return ess
    return pd.Series({k: float(v) for k, v in ess.items()})


def s_dev_max(p_load: float, p_g: float, p_ess: float, s_r: float,
              cos_phi: float, beta: float, tau: float) -> float:
    """式(1):S_dev_max = (P_load − P_G + P_ess + S_r·cosφ·β) / τ。

    手算对照(task-7-brief):cap=100,β=0.8,τ=0.95,无储能,P_load=30
    → (30−0+0+100×0.95×0.8)/0.95 = 111.578947...
    """
    return (p_load - p_g + p_ess + s_r * cos_phi * beta) / tau


def device_level(data: ScenarioData, solution: Any) -> pd.DataFrame:
    """逐站式(1)。P_load_typ=该站典型时刻净负荷,P_G=0,P_ess=储能额定功率,
    S_r=站容量 cap_mva,cosφ=0.95,β=station.beta_eff,τ=tau_max.kv110。

    返回 DataFrame(station_id, s_dev_max_mw, pv_installed_mw,
    margin_mw=s_dev_max−pv_installed)。
    """
    if TYPICAL_TS not in data.pnet.index:
        raise ValueError(f"typical timestamp {TYPICAL_TS} not found in data.pnet.index")
    typ_row = data.pnet.loc[TYPICAL_TS]

    ess_mw = _ess_mw_series(solution)
    tau = float(data.params["tau_max"]["kv110"])
    beta_cfg = data.params["beta"]

    rows: dict[str, dict[str, float]] = {}
    for sid in sorted(data.stations):
        st = data.stations[sid]
        p_load = float(typ_row[sid])
        p_ess = float(ess_mw.get(sid, 0.0))
        beta = st.beta_eff(beta_cfg)
        s_dev = s_dev_max(p_load, 0.0, p_ess, st.cap_mva, COS_PHI, beta, tau)
        pv_installed = float(data.pv_capacity.get(sid, 0.0))
        rows[sid] = {
            "s_dev_max_mw": s_dev,
            "pv_installed_mw": pv_installed,
            "margin_mw": s_dev - pv_installed,
        }
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index.name = "station_id"
    return df


def _shape_full_hours() -> float:
    """PV 归一化出力曲线全年积分(等效满发小时数),用于估算县年PV发电量。"""
    shape = pd.read_csv(_ROOT / "data/synthetic/pv_profiles/shape_xuzhou.csv")["p_norm"]
    return float(shape.sum())


def county_check(data: ScenarioData, solution: Any) -> pd.DataFrame:
    """县级交叉式(2):S=[min(Ss,SD)]。

    SD = 该县各站 device_level 结果之和(Σ s_dev_max_mw)。
    Ss = 系统级代理:县弃光率反推(=县PV装机×(1−弃光率/(1−η)))。M1 solution
    只落盘全年汇总 curtail_mwh(无逐县拆分),按各县PV装机占比分摊近似
    弃光量,除以该县年PV发电量估算(=装机×_shape_full_hours())得弃光率;
    若该县弃光率数值上等于0(如总弃光量为0或该县无PV装机),取 SD×1.1
    作为上界代理(brief 裁决)。

    返回 DataFrame(county, s_system_mw, s_device_mw, s_final_mw=min(二者),
    pv_installed_mw, open_capacity_mw=max(s_final−installed, 0))。
    """
    dev = device_level(data, solution)
    counties = pd.Series({sid: st.county for sid, st in data.stations.items()})

    sd_by_county = dev["s_dev_max_mw"].groupby(counties).sum()
    pv_by_county = data.pv_capacity.groupby(counties).sum()
    energy_by_county = pv_by_county * _shape_full_hours()

    curtail_total = float(_get(solution, "curtail_mwh", 0.0))
    pv_total = float(pv_by_county.sum())
    eta = float(data.params["eta"]["base"])

    rows: dict[str, dict[str, float]] = {}
    for county in sorted(sd_by_county.index):
        sd_c = float(sd_by_county[county])
        pv_c = float(pv_by_county.get(county, 0.0))
        energy_c = float(energy_by_county.get(county, 0.0))
        curtail_c = curtail_total * (pv_c / pv_total) if pv_total > 0 else 0.0
        rate = curtail_c / energy_c if energy_c > 0 else 0.0

        if rate <= 0.0:
            ss_c = sd_c * 1.1     # brief 裁决:弃光率=0 时取 SD×1.1 上界代理
        else:
            ss_c = pv_c * (1 - rate / (1 - eta))

        s_final = min(ss_c, sd_c)
        rows[county] = {
            "s_system_mw": ss_c,
            "s_device_mw": sd_c,
            "s_final_mw": s_final,
            "pv_installed_mw": pv_c,
            "open_capacity_mw": max(s_final - pv_c, 0.0),
        }
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index.name = "county"
    return df
