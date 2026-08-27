#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""表C·红线代价表(README §9.3:分区/县两级,方案A/B成本|ΔC|R_A vs R_B|A被红线逼出的措施)。

M1 成本口径声明:milp_planner 按全网单一 MILP 求解,total_cost/cost_breakdown
不按分区/县拆分;C_A/C_B/ΔC 在分区/县行留"—",真实值只在"全网合计"行给出。
县级 R_A/R_B 为近似值(cap_after/县级原始净负荷峰,未叠加储能/切分对峰值的
削减效果,精确值需 8760 全年回代,留待 M2)。
用法:python scripts/tab_C_redline.py --run synthetic-m1
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd

from scripts._common import parse_args, load_run, write_table

NET_WIDE_NOTE = "—(全网口径,见全网合计行)"


def _measure_diff(zone, ties: list, sol_a: dict, sol_b: dict) -> str:
    """A 相对 B 多用的措施(=被红线逼出的代价构成),仅报告有明显差异的项。"""
    parts = []
    for s in zone.stations:
        d_ess = sol_a["ess_mw"].get(s.station_id, 0) - sol_b["ess_mw"].get(s.station_id, 0)
        if d_ess > 1e-3:
            parts.append(f"储能+{d_ess:.2f}MW@{s.station_id}")
        d_exp = sol_a["expand_mva"].get(s.station_id, 0) - sol_b["expand_mva"].get(s.station_id, 0)
        if d_exp > 1e-3:
            parts.append(f"扩容+{d_exp:.0f}MVA@{s.station_id}")
    zst = {s.station_id for s in zone.stations}
    for t in ties:
        if t.station_a not in zst and t.station_b not in zst:
            continue
        for season in ("spring", "winter"):
            d_a = (sol_a["alpha"][season].get(t.tie_id, 0)
                   - sol_b["alpha"][season].get(t.tie_id, 0))
            if abs(d_a) > 1e-3:
                parts.append(f"切分Δα{d_a:+.2f}@{t.tie_id}({season})")
    return "; ".join(parts) if parts else "无(A=B同解,红线未在此分区绑定)"


def main() -> None:
    args = parse_args("表C·红线代价表(占位版,合成数据)")
    ctx = load_run(args.run)
    data, sol_a, sol_b = ctx["data"], ctx["sol_a"], ctx["sol_b"]

    rows = []
    for z in sorted(data.zones):
        zone = data.zones[z]
        rows.append([
            z, NET_WIDE_NOTE, NET_WIDE_NOTE, NET_WIDE_NOTE,
            f"{sol_a['r_after'][z]:.2f}", f"{sol_b['r_after'][z]:.2f}",
            _measure_diff(zone, data.ties, sol_a, sol_b),
        ])

    for county in sorted({z.county for z in data.zones.values()}):
        st_ids = [sid for sid, s in data.stations.items() if s.county == county]
        cap = sum(data.stations[s].cap_mva for s in st_ids)
        exp_a = sum(sol_a["expand_mva"].get(s, 0) for s in st_ids)
        exp_b = sum(sol_b["expand_mva"].get(s, 0) for s in st_ids)
        pnet_c = data.pnet[st_ids].sum(axis=1)
        peak = max(float(pnet_c.max()), float(-pnet_c.min()))
        r_a = (cap + exp_a) / peak if peak > 0 else float("inf")
        r_b = (cap + exp_b) / peak if peak > 0 else float("inf")
        rows.append([f"{county}(县合计)", NET_WIDE_NOTE, NET_WIDE_NOTE, NET_WIDE_NOTE,
                     f"{r_a:.2f}(近似)", f"{r_b:.2f}(近似)", "—(县级不逐措施拆分)"])

    delta_c = sol_a["total_cost_wanyuan_per_year"] - sol_b["total_cost_wanyuan_per_year"]
    binding_zone = max(sol_a["r_after"], key=sol_a["r_after"].get)
    rows.append([
        "全网合计", f"{sol_a['total_cost_wanyuan_per_year']:.2f}",
        f"{sol_b['total_cost_wanyuan_per_year']:.2f}", f"{delta_c:.2f}", "—", "—",
        f"红线仅在 {binding_zone} 绑定(该区 r_after_A={sol_a['r_after'][binding_zone]:.2f} 达上限)",
    ])

    df = pd.DataFrame(rows, columns=[
        "分区/县", "C_A(万元/年)", "C_B(万元/年)", "ΔC(万元/年)",
        "R_A", "R_B", "A被红线逼出的措施构成",
    ])
    write_table(df, "tab_C_redline")
    print(f"表C 写入 {len(df)} 行 -> tables/tab_C_redline.csv/.md")


if __name__ == "__main__":
    main()
