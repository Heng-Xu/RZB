"""旧 M1 合成链路优化器（仅用于历史回归，不得用于 real_2025）。

优化层:方案A/B 单目标成本最小化 MILP(linopy + HiGHS)。

方案A = 全工具 + 容载比红线 R≤2.0(允许受控扩容);方案B = 弹性无上限。
两方案成本差 = "红线代价"。变量/约束对应 README §4-§5 与 task-6-brief。

M1 近似声明(M2 收紧):
- 切分带曲线 band(t) 用 σ_load×站负荷、σ_pv×站PV 近似(裁决),非分段真值。
- O1 转带上界 T_tie = Σ n_channels·ampacity_mw·TIE_N1_AVAIL 常数,不做时变耦合。
- O6 红线线性化:对每分区在其"基态绑定方向峰值时刻 t*"处施加
  cap_扩后 ≤ 2.0·|pnet'_zone(t*)|(单时刻钉法)。可证 R_after=cap/max_t|pnet'|≤2.0,
  且避免了 brief 中 M_zone 自由上浮导致的退化(约束恒成立);等价实现其 z_dir 意图。
- 储能效率取单程 0.95(裁决,覆盖 baseline cycle_efficiency=0.88)。
- 典型日+储能仅在代表日展开,SOC 日内循环(日首=日末)。
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import yaml
from linopy import Model

from src.io_loader import ScenarioData
from src.links_sigma import LinkSet
from src.typical_days import TypicalDays, reduce_days

SPRING_MONTHS = {3, 4, 5, 9, 10}          # 裁决:这些月按 spring 切分方式,其余 winter
TIE_N1_AVAIL = 0.5                        # O1 转带事故可用率占位常数(裁决)
ETA_TRIP = 0.95                           # 储能单程充放效率(裁决)
EXPAND_STEP_MVA = 50.0                    # 单档扩容容量
MAX_EXPAND_UNITS = 2                      # n_expand ∈ {0,1,2}
R_REDLINE = 2.0                           # 方案A红线
RUN_ID = "synthetic-m1"
_TIME_BUDGET_S = 120.0                    # 单方案超时→典型日 12→8 重试一次
_ROOT = Path(__file__).resolve().parents[1]   # 研究/(src/ 的上一级),定位数据/成本/结果目录


@dataclass
class SolutionBundle:
    scheme: str
    status: str
    total_cost: float                     # 万元/年
    ess_mw: pd.Series
    ess_mwh: pd.Series
    alpha: pd.DataFrame                    # tie_id × season,切分比例(非负幅值 |α|)
    expand_mva: pd.Series
    curtail_mwh: float
    r_after: pd.Series
    shadow_r: float | None                # 万元/0.1R(A 的红线约束 LP 对偶折算)
    cost_breakdown: dict = field(default_factory=dict)
    solve_time_s: float = 0.0
    n_typical_days: int = 0


def _crf(r: float, n: int) -> float:
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def _load_cost_params(data: ScenarioData) -> dict:
    """从 params.costs.source 指向的 baseline_costs.yaml 读单价并做键名映射。"""
    src = (_ROOT / data.params["costs"]["source"]).resolve()
    with open(src, encoding="utf-8") as f:
        base = yaml.safe_load(f)
    disc = float(base["economics"]["discount_rate"])
    return {
        # 元/kWh→万元/MWh: ×1000/10000 = ×0.1;元/kW→万元/MW 同理
        "ess_power_wan_per_mw": base["storage_BESS"]["power_cost_yuan_per_kw"] * 0.1,
        "ess_energy_wan_per_mwh": base["storage_BESS"]["energy_cost_yuan_per_kwh"] * 0.1,
        "ess_life": int(base["Z5_salvage"]["storage_lifetime_years"]),
        "discount": disc,
        "crf_ess": _crf(disc, int(base["Z5_salvage"]["storage_lifetime_years"])),
        "crf_expand": _crf(disc, 30),
        "expand_wan": float(data.params["costs"]["expand_wanyuan_per_50mva"]),
        "switch_wan": float(data.params["costs"]["switch_install_wanyuan"]),
        "eps_switch": float(data.params["costs"]["switching_op_wanyuan"]),
        # 弃光 元/kWh→万元/MWh: ×0.1
        "curtail_wan_per_mwh": float(data.params["costs"]["curtail_price_yuan_kwh"]) * 0.1,
    }


def _rep_arrays(data: ScenarioData, tdays: TypicalDays):
    """构造代表日基态数组(station,day,hour)与季节/权重。"""
    stations = sorted(data.stations)
    days = list(tdays.day_index)
    shape = pd.read_csv(
        _ROOT / "data/synthetic/pv_profiles/shape_xuzhou.csv"
    )["p_norm"].to_numpy()
    pnet_full = data.pnet[stations].to_numpy()          # (8760, 12)
    n_st = len(stations)
    pnet = np.empty((n_st, len(days), 24))
    pv = np.empty_like(pnet)
    for j, d in enumerate(days):
        sl = slice(d * 24, d * 24 + 24)
        pnet[:, j, :] = pnet_full[sl, :].T
        pv[:, j, :] = data.pv_capacity[stations].to_numpy()[:, None] * shape[sl][None, :]
    load = pnet + pv
    months = np.array([data.pnet.index[d * 24].month for d in days])
    seasons = np.where(np.isin(months, list(SPRING_MONTHS)), "spring", "winter")
    weights = np.array([tdays.weights[d] for d in days])
    return stations, days, pnet, pv, load, seasons, weights


def _build(data: ScenarioData, links: LinkSet, tdays: TypicalDays, scheme: str,
           costs: dict, fix: dict | None = None, r_cap: float = R_REDLINE):
    """构建 linopy 模型;fix 提供整数解则退化为纯 LP(用于影子价格)。

    r_cap: 方案A红线上限(默认 R_REDLINE=2.0,对应 README §4.2/O6);仅
        scheme=='A' 时生效(Task 8 V4 R-成本曲线扫描用)。
    """
    stations, days, pnet, pv, load, seasons, weights = _rep_arrays(data, tdays)
    st_idx = pd.Index(stations, name="station")
    day_idx = pd.Index(days, name="day")
    hr_idx = pd.Index(range(24), name="hour")
    tie_ids = [t.tie_id for t in links.ties]
    tie_idx = pd.Index(tie_ids, name="tie")
    seas_idx = pd.Index(["spring", "winter"], name="season")

    def da3(arr):
        return xr.DataArray(arr, coords=[st_idx, day_idx, hr_idx])

    pnet_da, pv_da = da3(pnet), da3(pv)
    w_da = xr.DataArray(weights, coords=[day_idx])
    season_oh = xr.DataArray(
        np.stack([(seasons == s).astype(float) for s in ["spring", "winter"]], axis=1),
        coords=[day_idx, seas_idx],
    )

    m = Model()
    # 储能
    p_ess = m.add_variables(lower=0, coords=[st_idx], name="p_ess")
    e_ess = m.add_variables(lower=0, coords=[st_idx], name="e_ess")
    p_ch = m.add_variables(lower=0, coords=[st_idx, day_idx, hr_idx], name="p_ch")
    p_dis = m.add_variables(lower=0, coords=[st_idx, day_idx, hr_idx], name="p_dis")
    soc = m.add_variables(lower=0, coords=[st_idx, day_idx, hr_idx], name="soc")
    p_cur = m.add_variables(lower=0, coords=[st_idx, day_idx, hr_idx], name="p_cur")
    # 切分:ap=a→b, an=b→a(均≥0),|α|=ap+an≤σ_load
    sig_da = xr.DataArray([t.sigma_load for t in links.ties], coords=[tie_idx])
    ap = m.add_variables(lower=0, upper=sig_da, coords=[tie_idx, seas_idx], name="ap")
    an = m.add_variables(lower=0, upper=sig_da, coords=[tie_idx, seas_idx], name="an")

    if fix is None:
        n_exp = m.add_variables(lower=0, upper=MAX_EXPAND_UNITS, coords=[st_idx],
                                integer=True, name="n_exp")
        y_tie = m.add_variables(coords=[tie_idx], binary=True, name="y_tie")
        n_exp_val, y_val = n_exp, y_tie
    else:
        n_exp_val = xr.DataArray(fix["n_exp"], coords=[st_idx])
        y_val = xr.DataArray(fix["y_tie"], coords=[tie_idx])
        n_exp = y_tie = None

    # 切分带 delta(station,day,hour):逐 6 条 tie 累加
    tie_delta = None
    for i, tie in enumerate(links.ties):
        a, b = tie.station_a, tie.station_b
        ratio = tie.sigma_pv / tie.sigma_load if tie.sigma_load else 0.0
        Aband = xr.DataArray(load[stations.index(a)] - pv[stations.index(a)] * ratio,
                             coords=[day_idx, hr_idx])
        Bband = xr.DataArray(load[stations.index(b)] - pv[stations.index(b)] * ratio,
                             coords=[day_idx, hr_idx])
        ap_d = (ap.sel(tie=tie.tie_id) * season_oh).sum("season")   # LinearExpr(day)
        an_d = (an.sel(tie=tie.tie_id) * season_oh).sum("season")
        contrib_a = -ap_d * Aband + an_d * Bband                   # (day,hour)
        contrib_b = ap_d * Aband - an_d * Bband
        oh_a = xr.DataArray((st_idx == a).astype(float), coords=[st_idx])
        oh_b = xr.DataArray((st_idx == b).astype(float), coords=[st_idx])
        term = contrib_a * oh_a + contrib_b * oh_b
        tie_delta = term if tie_delta is None else tie_delta + term

    pnet_prime = pnet_da + p_ch - p_dis + p_cur + tie_delta

    # 站级常数
    cap = xr.DataArray([data.stations[s].cap_mva for s in stations], coords=[st_idx])
    maxunit = xr.DataArray(
        [max((t.capacity_mva for t in data.stations[s].transformers), default=0.0)
         for s in stations], coords=[st_idx])
    beta = xr.DataArray([data.stations[s].beta_eff(data.params["beta"]) for s in stations],
                        coords=[st_idx])
    ttie = {s: 0.0 for s in stations}
    for tie in links.ties:
        for s in (tie.station_a, tie.station_b):
            ttie[s] += tie.n_channels * tie.ampacity_mw * TIE_N1_AVAIL
    ttie_da = xr.DataArray([ttie[s] for s in stations], coords=[st_idx])
    k_ol = float(data.params["k_ol"])
    eta_base = float(data.params["eta"]["base"])

    # O1 正向过载(N-1):pnet' ≤ (cap+扩容−max_unit)·k_ol + T_tie
    m.add_constraints(
        pnet_prime - (k_ol * EXPAND_STEP_MVA) * n_exp_val
        <= (cap - maxunit) * k_ol + ttie_da, name="O1")
    # O2 反向过载:−pnet' ≤ beta·(cap+扩容)
    m.add_constraints(
        -pnet_prime - (beta * EXPAND_STEP_MVA) * n_exp_val <= beta * cap, name="O2")
    # O3 弃光上限:Σ p_cur·w ≤ (1−η)·Σ pv·w
    m.add_constraints(
        (p_cur * w_da).sum() <= (1 - eta_base) * float((pv_da * w_da).sum()), name="O3")
    # O4 储能:功率/能量界 + SOC 日内循环递推
    m.add_constraints(p_ch - p_ess <= 0, name="O4_pch")
    m.add_constraints(p_dis - p_ess <= 0, name="O4_pdis")
    m.add_constraints(soc - e_ess <= 0, name="O4_soc_cap")
    prev = soc.roll(hour=1)   # prev[h0]=soc[h23] → 日首=日末
    m.add_constraints(soc - prev - ETA_TRIP * p_ch + (1.0 / ETA_TRIP) * p_dis == 0,
                      name="O4_recur")
    # O5 切分界:|α|=ap+an ≤ σ_load,且 ≤ y·σ_load(触发开关加装)
    m.add_constraints(ap + an - sig_da <= 0, name="O5_sigma")
    m.add_constraints(ap + an - y_val * sig_da <= 0, name="O5_switch")

    # O6 红线(仅A):单时刻钉法
    redline_names: list[str] = []
    if scheme == "A":
        for zid in sorted(data.zones):
            zst = [s.station_id for s in data.zones[zid].stations]
            base_zone = pnet[[stations.index(s) for s in zst]].sum(axis=0)  # (day,hour)
            fwd, rev = base_zone.max(), (-base_zone).max()
            di, hi = (np.unravel_index(np.argmax(base_zone), base_zone.shape) if fwd >= rev
                      else np.unravel_index(np.argmax(-base_zone), base_zone.shape))
            d_star, h_star, is_rev = days[di], int(hi), rev > fwd
            prime_star = pnet_prime.sel(station=zst, day=d_star, hour=h_star).sum("station")
            cap_const = float(sum(data.stations[s].cap_mva for s in zst))
            n_sum = (EXPAND_STEP_MVA * n_exp_val.sel(station=zst)).sum()
            if is_rev:      # cap ≤ r_cap·(−prime) ⟺ cap + r_cap·prime ≤ 0
                m.add_constraints(cap_const + n_sum + r_cap * prime_star <= 0, name=f"redline_{zid}")
            else:           # cap ≤ r_cap·prime ⟺ cap − r_cap·prime ≤ 0
                m.add_constraints(cap_const + n_sum - r_cap * prime_star <= 0, name=f"redline_{zid}")
            redline_names.append(f"redline_{zid}")

    # 目标(万元/年)
    obj = (
        (p_ess * costs["ess_power_wan_per_mw"] + e_ess * costs["ess_energy_wan_per_mwh"]).sum()
        * costs["crf_ess"]
        + costs["curtail_wan_per_mwh"] * (p_cur * w_da).sum()
        + costs["eps_switch"] * (ap + an).sum()
    )
    if fix is None:
        obj = (obj
               + (n_exp * costs["expand_wan"] * costs["crf_expand"]).sum()
               + (y_tie * costs["switch_wan"]).sum())
    m.add_objective(obj, sense="min")

    return dict(m=m, stations=stations, days=days, pnet=pnet, pv=pv, load=load,
                seasons=seasons, weights=weights, links=links,
                p_ess=p_ess, e_ess=e_ess, p_ch=p_ch, p_dis=p_dis, p_cur=p_cur,
                ap=ap, an=an, n_exp=n_exp, y_tie=y_tie, redline_names=redline_names,
                zones={z: [s.station_id for s in data.zones[z].stations]
                       for z in sorted(data.zones)})


def _pnet_prime_np(ctx, sol) -> np.ndarray:
    """从解重建 pnet'(station,day,hour) 数值。"""
    stations, days = ctx["stations"], ctx["days"]
    pnet, pv, load, seasons = ctx["pnet"], ctx["pv"], ctx["load"], ctx["seasons"]
    prime = pnet + sol["p_ch"] - sol["p_dis"] + sol["p_cur"]
    s_onehot = np.stack([(seasons == "spring"), (seasons == "winter")], axis=1).astype(float)
    for i, tie in enumerate(ctx["links"].ties):
        a, b = tie.station_a, tie.station_b
        ia, ib = stations.index(a), stations.index(b)
        ratio = tie.sigma_pv / tie.sigma_load if tie.sigma_load else 0.0
        Aband = load[ia] - pv[ia] * ratio
        Bband = load[ib] - pv[ib] * ratio
        apv = sol["ap"][i] @ s_onehot.T   # (day,) 按季节选
        anv = sol["an"][i] @ s_onehot.T
        prime[ia] += (-apv[:, None] * Aband + anv[:, None] * Bband)
        prime[ib] += (apv[:, None] * Aband - anv[:, None] * Bband)
    return prime


def _extract_solution(ctx):
    def v(x):
        return None if x is None else np.asarray(x.solution.values)   # 固定整数的LP无n_exp/y_tie句柄
    return {
        "p_ess": v(ctx["p_ess"]), "e_ess": v(ctx["e_ess"]),
        "p_ch": v(ctx["p_ch"]), "p_dis": v(ctx["p_dis"]), "p_cur": v(ctx["p_cur"]),
        "ap": v(ctx["ap"]), "an": v(ctx["an"]),
        "n_exp": v(ctx["n_exp"]), "y_tie": v(ctx["y_tie"]),
    }


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_results(data: ScenarioData, bundle: SolutionBundle):
    root = _ROOT
    run_dir = root / "results" / "runs" / RUN_ID
    run_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "scheme": bundle.scheme, "status": bundle.status,
        "total_cost_wanyuan_per_year": bundle.total_cost,
        "cost_breakdown": bundle.cost_breakdown,
        "ess_mw": bundle.ess_mw.round(4).to_dict(),
        "ess_mwh": bundle.ess_mwh.round(4).to_dict(),
        "alpha": {c: bundle.alpha[c].round(4).to_dict() for c in bundle.alpha.columns},
        "expand_mva": bundle.expand_mva.round(1).to_dict(),
        "curtail_mwh": bundle.curtail_mwh,
        "r_after": bundle.r_after.round(4).to_dict(),
        "shadow_r_wan_per_0.1R": bundle.shadow_r,
        "solve_time_s": bundle.solve_time_s,
        "n_typical_days": bundle.n_typical_days,
    }
    (run_dir / f"solution_{bundle.scheme}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    data_dir = root / "data" / "synthetic"
    inputs = ["stations.csv", "transformers.csv", "ties.csv", "pv_registry.csv",
              "pv_profiles/shape_xuzhou.csv"]
    sha = {p: _sha256(data_dir / p) for p in inputs}
    sha["params.yaml"] = _sha256(root / "params.yaml")
    lc = sorted((data_dir / "load_curves").glob("*.csv"))
    sha["load_curves(all)"] = hashlib.sha256(
        "".join(_sha256(p) for p in lc).encode()).hexdigest()
    params_snap = {k: v for k, v in data.params.items() if k != "__root__"}
    (run_dir / "manifest.json").write_text(json.dumps(
        {"run_id": RUN_ID, "input_sha256": sha, "params_snapshot": params_snap},
        ensure_ascii=False, indent=2), encoding="utf-8")


def _shadow_price(data, links, tdays, costs, sol, ctx, r_cap: float = R_REDLINE) -> float | None:
    """方案A整数固定后重解 LP,取绑定红线约束对偶 → 万元/0.1R。"""
    try:
        fix = {"n_exp": np.round(sol["n_exp"]), "y_tie": np.round(sol["y_tie"])}
        lp = _build(data, links, tdays, "A", costs, fix=fix, r_cap=r_cap)
        lp["m"].solve(solver_name="highs")
        prime = _pnet_prime_np(lp, _extract_solution(lp))
        best = 0.0
        for zid, name in zip(sorted(data.zones), lp["redline_names"]):
            dual = float(np.abs(np.asarray(lp["m"].constraints[name].dual.values)))
            zst = lp["zones"][zid]
            idx = [lp["stations"].index(s) for s in zst]
            peak = float(np.max(np.abs(prime[idx].sum(axis=0))))
            best = max(best, dual * 0.1 * peak)   # 万元/0.1R = λ·0.1·peak
        return best if best > 0 else None
    except Exception:
        return None


def solve_scheme(data: ScenarioData, links: LinkSet, tdays: TypicalDays,
                 scheme: str, r_cap: float = R_REDLINE, write: bool = True) -> SolutionBundle:
    """求解方案A/B,组装 SolutionBundle 并落盘 results/runs/synthetic-m1/。

    r_cap: 方案A红线上限(默认 2.0,对应 README §4.2/O6);仅 scheme=='A' 生效,
        供 Task 8 V4 R-成本曲线扫描等场景重解不同红线取值,不改变默认行为。
    write: 是否落盘 solution_<scheme>.json / manifest.json(默认 True,与原行为
        一致);扫描/探索场景应传 False,避免覆盖 results/runs/ 下的正式解。
    """
    if scheme not in ("A", "B"):
        raise ValueError(f"scheme must be 'A' or 'B', got {scheme!r}")
    costs = _load_cost_params(data)
    mip_gap = float(data.params["milp"]["mip_gap"])

    def run(td):
        ctx = _build(data, links, td, scheme, costs, r_cap=r_cap)
        t0 = time.time()
        ctx["m"].solve(solver_name="highs", mip_rel_gap=mip_gap, time_limit=_TIME_BUDGET_S)
        return ctx, time.time() - t0

    ctx, elapsed = run(tdays)
    used = tdays
    if ctx["m"].termination_condition != "optimal" or elapsed > _TIME_BUDGET_S:
        used = reduce_days(data.pnet.sum(axis=1), 8)   # 超时/非最优→典型日 12→8 重试一次
        ctx, elapsed = run(used)

    m = ctx["m"]
    status = "ok" if m.termination_condition == "optimal" else str(m.termination_condition)
    sol = _extract_solution(ctx)
    stations, days = ctx["stations"], ctx["days"]

    n_exp_r = np.round(sol["n_exp"])
    ess_mw = pd.Series(sol["p_ess"], index=stations, name="ess_mw").round(6)
    ess_mwh = pd.Series(sol["e_ess"], index=stations, name="ess_mwh").round(6)
    expand_mva = pd.Series(n_exp_r * EXPAND_STEP_MVA, index=stations, name="expand_mva")
    alpha = pd.DataFrame(sol["ap"] + sol["an"], index=[t.tie_id for t in links.ties],
                         columns=["spring", "winter"]).round(6)
    alpha.index.name = "tie_id"
    curtail_mwh = float((sol["p_cur"] * ctx["weights"][None, :, None]).sum())

    prime = _pnet_prime_np(ctx, sol)
    r_after = {}
    for zid, zst in ctx["zones"].items():
        idx = [stations.index(s) for s in zst]
        peak = float(np.max(np.abs(prime[idx].sum(axis=0))))
        cap_after = float(sum(data.stations[s].cap_mva for s in zst)
                          + EXPAND_STEP_MVA * n_exp_r[idx].sum())
        r_after[zid] = cap_after / peak if peak > 0 else float("inf")
    r_after = pd.Series(r_after, name="r_after"); r_after.index.name = "zone_id"

    cb = {
        "ess": float((sol["p_ess"] * costs["ess_power_wan_per_mw"]
                      + sol["e_ess"] * costs["ess_energy_wan_per_mwh"]).sum() * costs["crf_ess"]),
        "expand": float((np.round(sol["n_exp"]) * costs["expand_wan"] * costs["crf_expand"]).sum()),
        "switch": float((np.round(sol["y_tie"]) * costs["switch_wan"]).sum()),
        "curtail": float(costs["curtail_wan_per_mwh"] * curtail_mwh),
        "eps_switch": float(costs["eps_switch"] * (sol["ap"] + sol["an"]).sum()),
    }
    shadow_r = (_shadow_price(data, links, used, costs, sol, ctx, r_cap=r_cap)
                if scheme == "A" and write else None)
    bundle = SolutionBundle(
        scheme=scheme, status=status, total_cost=float(m.objective.value),
        ess_mw=ess_mw, ess_mwh=ess_mwh, alpha=alpha, expand_mva=expand_mva,
        curtail_mwh=curtail_mwh, r_after=r_after, shadow_r=shadow_r,
        cost_breakdown=cb, solve_time_s=elapsed, n_typical_days=len(days))
    if write:
        _write_results(data, bundle)
    return bundle
