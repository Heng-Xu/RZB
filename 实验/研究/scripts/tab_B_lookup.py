#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""表B·经典区间查找表骨架(README §9.2:行=渗透率档×源荷比档×城乡=18行,列=推荐R区间+首选措施)。

M1 只有 5 个真实分区落点(用当前渗透率/源荷比/城乡定位所在格,值标"(实测)");
其余格留"—(M3情景扫描)"。用法:python scripts/tab_B_lookup.py --run synthetic-m1
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd

from scripts._common import parse_args, load_run, write_table

PEN_BANDS = ["<40%", "40%~80%", "≥80%"]
SLR_BANDS = ["<0.5", "0.5~0.9", "≥0.9"]  # source-to-load ratio
AREA_TYPES = ["城", "乡"]
PLACEHOLDER = "—(M3情景扫描)"


def _pen_band(pct: float) -> str:
    if pct < 40:
        return PEN_BANDS[0]
    if pct < 80:
        return PEN_BANDS[1]
    return PEN_BANDS[2]


def _slr_band(ratio: float) -> str:
    """source-to-load ratio 档位(PV装机/正向峰负荷)"""
    if ratio < 0.5:
        return SLR_BANDS[0]
    if ratio < 0.9:
        return SLR_BANDS[1]
    return SLR_BANDS[2]


def main() -> None:
    args = parse_args("表B·经典区间查找表骨架(占位版,合成数据)")
    ctx = load_run(args.run)
    data, sol_b, clr = ctx["data"], ctx["sol_b"], ctx["clr"]

    # 5 个真实分区落点:(渗透率档, 源荷比档, 城乡) -> [(zone_id, R, 首选措施), ...]
    # 注意:格粒度粗于分区数,多分区可能落入同一格(如实并列展示,不可覆盖丢弃)。
    real_points: dict[tuple[str, str, str], list[tuple[str, float, str]]] = {}
    for z in sorted(data.zones):
        zone = data.zones[z]
        pv = sum(data.pv_capacity[s.station_id] for s in zone.stations)
        pen_pct = pv / clr.loc[z, "p_fwd"] * 100 if clr.loc[z, "p_fwd"] > 0 else 0.0
        slr = pv / clr.loc[z, "cap_mva"] if clr.loc[z, "cap_mva"] > 0 else 0.0
        area = "城" if zone.area_type == "urban" else "乡"
        # 措施判定:切分实际使用(alpha>0 涉及该区任一联络)优先于扩容/储能
        zst = {s.station_id for s in zone.stations}
        used_tie = any(
            (t.station_a in zst or t.station_b in zst)
            and (sol_b["alpha"]["spring"].get(t.tie_id, 0) > 0
                 or sol_b["alpha"]["winter"].get(t.tie_id, 0) > 0)
            for t in data.ties
        )
        if used_tie:
            measure = "切分(联络挪常开点,已生效)"
        elif any(sol_b["expand_mva"].get(s.station_id, 0) > 0 for s in zone.stations):
            measure = "扩容"
        elif any(sol_b["ess_mw"].get(s.station_id, 0) > 0 for s in zone.stations):
            measure = "储能"
        else:
            measure = "无需额外措施"
        key = (_pen_band(pen_pct), _slr_band(slr), area)
        real_points.setdefault(key, []).append((z, sol_b["r_after"][z], measure))

    rows = []
    n_real = 0
    for pen_band in PEN_BANDS:
        for slr_band in SLR_BANDS:
            for area in AREA_TYPES:
                pts = real_points.get((pen_band, slr_band, area))
                if pts:
                    n_real += len(pts)
                    r_col = "; ".join(f"{r:.2f}(实测:{zid})" for zid, r, _ in pts)
                    m_col = "; ".join(f"{zid}:{m}" for zid, _, m in pts)
                    rows.append([pen_band, slr_band, area, r_col, m_col])
                else:
                    rows.append([pen_band, slr_band, area, PLACEHOLDER, PLACEHOLDER])

    df = pd.DataFrame(rows, columns=["渗透率档", "源荷比档", "城乡", "推荐R区间", "首选措施"])
    write_table(df, "tab_B_lookup")
    print(f"表B 写入 {len(df)} 行(实测点 {n_real} 个,覆盖 {len(real_points)} 个真实分区)-> tables/tab_B_lookup.csv/.md")


if __name__ == "__main__":
    main()
