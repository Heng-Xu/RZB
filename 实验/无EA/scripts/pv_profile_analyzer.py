#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PV出力曲线分析器：
- 验证 PVGIS 数据正确性（峰值/年发电量/容量因子）
- 提取季节性统计（春秋反送 vs 夏冬重载）
- 与典型负荷曲线叠加，计算反送小时数
- 输出供 lcc_simulator.py 使用的 t_fwd / t_rev 参数

用法：
    python pv_profile_analyzer.py --pv datasets/pv_profiles/xuzhou_tmy.csv
    python pv_profile_analyzer.py --pv ... --installed-kwp 2500 \\
        --load-peak-kw 1000 --load-min-kw 300
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import numpy as np


def load_pv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # PVGIS time is "YYYYMMDD:HHMM"; parse it
    df["dt"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M", errors="coerce")
    df["P_kw"] = df["P"] / 1000.0  # W → kW
    df["month"] = df["dt"].dt.month
    df["hour"] = df["dt"].dt.hour
    df["year"] = df["dt"].dt.year
    return df


def basic_stats(df: pd.DataFrame, installed_kwp: float = 1.0) -> dict:
    P = df["P_kw"] * installed_kwp
    n_hours = len(df)
    n_years = n_hours / 8760
    total_kwh = P.sum()
    return {
        "n_hours": int(n_hours),
        "n_years": round(n_years, 2),
        "annual_yield_kwh": round(total_kwh / n_years, 1) if n_years > 0 else 0,
        "annual_yield_per_kwp": round(total_kwh / n_years / installed_kwp, 1)
            if n_years > 0 and installed_kwp > 0 else 0,
        "peak_kw": round(P.max(), 2),
        "operating_hours_per_year": round((P > 0).sum() / n_years, 1) if n_years > 0 else 0,
        "capacity_factor_pct": round(P.mean() / installed_kwp * 100, 2),
    }


def seasonal_split(df: pd.DataFrame, installed_kwp: float) -> pd.DataFrame:
    """Split into 4 seasons and report avg/peak."""
    seasons = {"spring(3-5)": [3, 4, 5], "summer(6-8)": [6, 7, 8],
               "autumn(9-11)": [9, 10, 11], "winter(12-2)": [12, 1, 2]}
    rows = []
    for name, months in seasons.items():
        sub = df[df["month"].isin(months)]
        P = sub["P_kw"] * installed_kwp
        rows.append({
            "season": name,
            "hours": int(len(sub)),
            "mean_kw": round(P.mean(), 2),
            "peak_kw": round(P.max(), 2),
            "noon_avg_kw": round(P[sub["hour"].between(10, 14)].mean(), 2),
        })
    return pd.DataFrame(rows)


def reverse_hours(
    df: pd.DataFrame,
    installed_kwp: float,
    load_peak_kw: float,
    load_min_kw: float,
) -> dict:
    """
    与典型日负荷曲线叠加，找出反送小时数。

    简化负荷模型：以日为单位的余弦近似
        L(h) = L_min + (L_peak - L_min) × max(0, sin(π(h-8)/12))
    （白天09-21峰、夜间谷）

    反送条件：PV_actual_kw > L(h)
    """
    P_kw_actual = df["P_kw"] * installed_kwp
    h = df["hour"].to_numpy()
    # 简化日负荷曲线
    load_kw = load_min_kw + (load_peak_kw - load_min_kw) * np.maximum(
        0, np.sin(np.pi * (h - 8) / 12)
    )
    net = P_kw_actual - load_kw
    rev = (net > 0)
    n_years = len(df) / 8760

    rev_hours_per_year = rev.sum() / n_years if n_years > 0 else 0
    fwd_hours_per_year = (~rev).sum() / n_years if n_years > 0 else 0

    # 反送能量
    rev_energy_kwh = float(net[rev].sum() / n_years) if n_years > 0 else 0
    fwd_energy_kwh = float(load_kw.sum() / n_years) if n_years > 0 else 0

    return {
        "load_peak_kw": load_peak_kw,
        "load_min_kw": load_min_kw,
        "installed_kwp": installed_kwp,
        "ratio_pv_to_peak_load": round(installed_kwp / load_peak_kw, 3),
        "reverse_hours_per_year": round(rev_hours_per_year, 1),
        "forward_hours_per_year": round(fwd_hours_per_year, 1),
        "reverse_energy_kwh_per_year": round(rev_energy_kwh, 1),
        "forward_load_energy_kwh_per_year": round(fwd_energy_kwh, 1),
        "reverse_share_of_year_pct": round(rev_hours_per_year / 8760 * 100, 2),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pv", type=Path, required=True, help="PVGIS CSV路径")
    ap.add_argument("--installed-kwp", type=float, default=1000,
                    help="片区PV装机 kWp（默认1000=1MWp）")
    ap.add_argument("--load-peak-kw", type=float, default=1000,
                    help="日峰荷 kW（默认1000=1MW）")
    ap.add_argument("--load-min-kw", type=float, default=300,
                    help="日谷荷 kW（默认300=0.3MW）")
    ap.add_argument("--season", action="store_true", help="是否输出季节细分")
    args = ap.parse_args()

    df = load_pv(args.pv)
    if df["dt"].isna().all():
        print("[ERROR] 时间解析失败，请检查PVGIS时间字段", file=sys.stderr)
        return 1

    print(f"=== PV曲线基本统计 ({args.pv.name}, 装机 {args.installed_kwp} kWp) ===")
    for k, v in basic_stats(df, args.installed_kwp).items():
        print(f"  {k:30s} = {v}")

    if args.season:
        print("\n=== 季节分解 ===")
        seasonal = seasonal_split(df, args.installed_kwp)
        print(seasonal.to_string(index=False))

    print(f"\n=== 反送场景分析（负荷峰{args.load_peak_kw}kW/谷{args.load_min_kw}kW） ===")
    rev = reverse_hours(df, args.installed_kwp, args.load_peak_kw, args.load_min_kw)
    for k, v in rev.items():
        print(f"  {k:35s} = {v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
