#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""表A·推荐容载比主表(转置:列=分区Z1..Z5,行=指标;README §9.1 六板块照抄)。

M1 占位版:数值来自合成场景 results/runs/<run_id>/;首行"推荐容载比R(2030)"
取方案B r_after(加粗,md 用 **)。用法:python scripts/tab_A_zonematrix.py --run synthetic-m1
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # 保证 `python scripts/xx.py` 可 import src/scripts
import pandas as pd
import yaml

from scripts._common import ROOT, parse_args, load_run, write_table
from src.links_sigma import a_ntc


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%" if x == x else "—"


def main() -> None:
    args = parse_args("表A·推荐容载比主表(占位版,合成数据)")
    ctx = load_run(args.run)
    data, links, clr = ctx["data"], ctx["links"], ctx["clr"]
    sol_a, sol_b, vdlt = ctx["sol_a"], ctx["sol_b"], ctx["verify_dlt"]
    vflow, params = ctx["verify_flow"], ctx["params"]
    beta_cfg = params["beta"]
    zones = sorted(data.zones)

    shape = pd.read_csv(ROOT / "data/synthetic/pv_profiles/shape_xuzhou.csv")["p_norm"].to_numpy()
    theo_pv_mwh = float(data.pv_capacity.sum() * shape.sum())
    curtail_rate = sol_b["curtail_mwh"] / theo_pv_mwh if theo_pv_mwh > 0 else float("nan")

    # verify_dlt2041.csv 无 zone 列,按 station_id 反查(entity_id 即 station_id/county)
    margin_by_zone = {z: 0.0 for z in zones}
    for _, row in vdlt[vdlt["level"] == "station"].iterrows():
        sid = row["entity_id"]
        if sid in data.stations:
            margin_by_zone[data.stations[sid].zone_id] += float(row["margin_mw"])

    rows: list[list] = []

    def add(block: str, label: str, values: dict[str, str]) -> None:
        rows.append([block, label] + [values.get(z, "—") for z in zones])

    # 1. 推荐结果
    add("1.推荐结果", "推荐容载比R(2030)",
        {z: f"**{sol_b['r_after'][z]:.2f}**" for z in zones})
    add("1.推荐结果", "现状R", {z: f"{clr.loc[z, 'r']:.2f}" for z in zones})
    add("1.推荐结果", "参考R⁺",
        {z: ("∞" if clr.loc[z, "r_fwd"] == float("inf") else f"{clr.loc[z, 'r_fwd']:.2f}")
         for z in zones})
    add("1.推荐结果", "卡边方向",
        {z: ("反向" if clr.loc[z, "binding"] == "reverse" else "正向") for z in zones})
    # 2. 分区画像
    pv_zone = {z: sum(data.pv_capacity[s.station_id] for s in data.zones[z].stations) for z in zones}
    add("2.分区画像", "渗透率(PV装机/P⁺,近似最大负荷)",
        {z: _pct(pv_zone[z] / clr.loc[z, "p_fwd"]) if clr.loc[z, "p_fwd"] > 0 else "—" for z in zones})
    add("2.分区画像", "源荷比(PV装机/变电容量)",
        {z: _pct(pv_zone[z] / clr.loc[z, "cap_mva"]) for z in zones})
    add("2.分区画像", "KP档(近5年最大净负荷增长率)", {z: "—(M2,需5年史)" for z in zones})
    add("2.分区画像", "城乡", {z: ("城" if data.zones[z].area_type == "urban" else "乡") for z in zones})
    add("2.分区画像", "P⁺/P⁻(MW)",
        {z: f"{clr.loc[z, 'p_fwd']:.1f}/{clr.loc[z, 'p_rev']:.1f}" for z in zones})
    # 3. 联络度(站级 D/σ 按区内站简单均值近似;M2 应按站容量加权重估)
    add("3.联络度", "结构联络度D(区内站均值)",
        {z: f"{links.d_struct[[s.station_id for s in data.zones[z].stations]].mean():.2f}" for z in zones})
    add("3.联络度", "可切分度σ(区内站均值)",
        {z: f"{links.sigma[[s.station_id for s in data.zones[z].stations]].mean():.2f}" for z in zones})
    a_ntc_vals = {}
    for z in zones:
        pnet_zone = data.pnet[[s.station_id for s in data.zones[z].stations]].sum(axis=1)
        t_fwd = data.pnet.index.get_loc(pnet_zone.idxmax())
        t_rev = data.pnet.index.get_loc(pnet_zone.idxmin())
        fwd = a_ntc(data, links, t_fwd, "fwd")[z]
        rev = a_ntc(data, links, t_rev, "rev")[z]
        a_ntc_vals[z] = f"{fwd:.1f}/{rev:.1f}"
    add("3.联络度", "A_NTC/A_NTC⁻(MW,区自身峰时)", a_ntc_vals)
    util = {}
    for z in zones:
        zst = {s.station_id for s in data.zones[z].stations}
        touch = [t for t in links.ties if t.station_a in zst or t.station_b in zst]
        if not touch:
            util[z] = "—"; continue
        used = sum(sol_b["alpha"]["spring"].get(t.tie_id, 0) + sol_b["alpha"]["winter"].get(t.tie_id, 0)
                   for t in touch) / 2
        avail = sum(t.sigma_load for t in touch)
        util[z] = _pct(used / avail) if avail > 0 else "—"
    add("3.联络度", "切分利用率(方案B,|α|/σ)", util)
    # 4. 承载力与消纳
    add("4.承载力与消纳", "可开放容量(DL/T2041站级margin加总,MW)",
        {z: f"{margin_by_zone[z]:.1f}" for z in zones})
    rev_margin = {}
    for z in zones:
        beta_s = sum(s.beta_eff(beta_cfg) * s.cap_mva for s in data.zones[z].stations)
        rev_margin[z] = _pct((beta_s - clr.loc[z, "p_rev"]) / beta_s) if beta_s > 0 else "—"
    add("4.承载力与消纳", "反向承载力裕度(β·ΣS−P⁻)/β·ΣS", rev_margin)
    add("4.承载力与消纳", "年返送小时数(h)",
        {z: str(int((data.pnet[[s.station_id for s in data.zones[z].stations]].sum(axis=1) < 0).sum()))
         for z in zones})
    add("4.承载力与消纳", "弃光率/η(全网口径,M1未按分区拆分)",
        {z: f"{curtail_rate * 100:.2f}%/{params['eta']['base'] * 100:.0f}%" for z in zones})
    # 5. 成本(全网口径,M1未按分区拆分)
    base_costs_path = (ROOT / params["costs"]["source"]).resolve()
    with open(base_costs_path, encoding="utf-8") as f:
        base_costs = yaml.safe_load(f)
    ess_yuan_kw = base_costs["storage_BESS"]["power_cost_yuan_per_kw"]
    expand_yuan_kw = params["costs"]["expand_wanyuan_per_50mva"] * 10000 / 50000
    add("5.成本", "年化总成本(方案B,万元/年)", {z: f"{sol_b['total_cost_wanyuan_per_year']:.1f}" for z in zones})
    cb = sol_b["cost_breakdown"]
    fenxiang = (f"切分{cb['switch'] + cb['eps_switch']:.1f}|储能{cb['ess']:.1f}"
                f"|扩容{cb['expand']:.1f}|弃光{cb['curtail']:.1f}")
    add("5.成本", "分项(切分/储能/扩容/弃光,万元/年)", {z: fenxiang for z in zones})
    delta_c = sol_a["total_cost_wanyuan_per_year"] - sol_b["total_cost_wanyuan_per_year"]
    add("5.成本", "红线代价ΔC(A−B,万元/年)", {z: f"{delta_c:.2f}" for z in zones})
    add("5.成本", "单位措施成本(元/kW三档梯度)",
        {z: f"储能{ess_yuan_kw:.0f}|开关15万元/台|扩容{expand_yuan_kw:.0f}" for z in zones})
    shadow = sol_a["shadow_r_wan_per_0.1R"]
    add("5.成本", "R影子价格(方案A,万元/0.1R)",
        {z: (f"{shadow:.1f}" if shadow is not None else "—") for z in zones})
    # 6. 可靠性
    def _zone_of_element(eid: str) -> set[str]:
        if eid.startswith("X_"):
            sid = eid.split("_")[1]
            return {data.stations[sid].zone_id} if sid in data.stations else set()
        parts = eid.split("_")
        return {p for p in parts if p in zones}

    vflow2 = vflow.copy()
    vflow2["zones"] = vflow2["element_id"].apply(_zone_of_element)
    n1 = {}
    for z in zones:
        sub = vflow2[vflow2["zones"].apply(lambda s: z in s)]
        n1[z] = _pct((sub["loading_pct"] <= 100).mean()) if len(sub) else "—"
    add("6.可靠性", "N-1通过率(校核,%)", n1)
    add("6.可靠性", "EENS(MWh/年)", {z: "—(M2,需故障率数据)" for z in zones})

    rows.append(["末行", "导则表2区间(1.5~2.0)对照"] + ["1.5–2.0"] * len(zones))

    df = pd.DataFrame(rows, columns=["板块", "指标", *zones])
    write_table(df, "tab_A_zonematrix")
    print(f"表A 写入 {len(df)} 行 -> tables/tab_A_zonematrix.csv/.md")


if __name__ == "__main__":
    main()
