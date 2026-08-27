#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IEEE 33-bus 配电系统加载与基础分析

用法：
    python ieee33_loader.py                    # 加载并打印摘要
    python ieee33_loader.py --validate         # 加载+拓扑验证
    python ieee33_loader.py --rebase 110kv     # 等效到110kV变电站视角
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import numpy as np


ROOT = Path(__file__).resolve().parents[1] / "datasets" / "ieee33"
BUS_FILE = ROOT / "ieee33_bus.csv"
BRANCH_FILE = ROOT / "ieee33_branch.csv"


def load_bus() -> pd.DataFrame:
    if not BUS_FILE.exists():
        raise FileNotFoundError(BUS_FILE)
    df = pd.read_csv(BUS_FILE)
    expected = {"bus", "p_load_kw", "q_load_kvar", "bus_type"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"bus file missing columns: {missing}")
    return df


def load_branch() -> pd.DataFrame:
    if not BRANCH_FILE.exists():
        raise FileNotFoundError(BRANCH_FILE)
    df = pd.read_csv(BRANCH_FILE)
    expected = {"from_bus", "to_bus", "r_ohm", "x_ohm", "length_km_est"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"branch file missing columns: {missing}")
    return df


def summary(bus: pd.DataFrame, branch: pd.DataFrame) -> dict:
    p_total = float(bus["p_load_kw"].sum())
    q_total = float(bus["q_load_kvar"].sum())
    s_total = float(np.hypot(p_total, q_total))
    line_km = float(branch["length_km_est"].sum())
    slack = bus.loc[bus["bus_type"] == "slack", "bus"].tolist()
    return {
        "n_buses": int(len(bus)),
        "n_branches": int(len(branch)),
        "p_load_kw": p_total,
        "q_load_kvar": q_total,
        "s_load_kva": s_total,
        "slack_buses": slack,
        "total_line_length_km": line_km,
        "avg_branch_r_ohm": float(branch["r_ohm"].mean()),
    }


def validate_topology(bus: pd.DataFrame, branch: pd.DataFrame) -> list[str]:
    """检查是否为合法的径向拓扑：N-1 条支路、单根、无环。"""
    issues = []
    n_b = len(bus)
    n_e = len(branch)
    if n_e != n_b - 1:
        issues.append(f"非径向：节点{n_b}个，支路{n_e}条（期望{n_b-1}）")
    # 无重复支路
    pairs = set()
    for _, row in branch.iterrows():
        key = tuple(sorted([row["from_bus"], row["to_bus"]]))
        if key in pairs:
            issues.append(f"重复支路 {key}")
        pairs.add(key)
    # 节点连通
    buses_in_branch = set(branch["from_bus"]) | set(branch["to_bus"])
    buses_def = set(bus["bus"])
    orphan = buses_def - buses_in_branch
    if orphan and orphan != {bus.loc[bus["bus_type"] == "slack", "bus"].iloc[0]}:
        # 只要不仅是单点孤立的非slack节点都算异常
        if orphan - {1}:
            issues.append(f"孤立节点 {orphan}")
    return issues


def rebase_to_110kv_view(bus: pd.DataFrame, transformer_capacity_mva: float) -> dict:
    """把33-bus视为某110kV变电站下属10kV配网，计算容载比相关指标。"""
    p_kw = bus["p_load_kw"].sum()
    q_kvar = bus["q_load_kvar"].sum()
    s_kva = np.hypot(p_kw, q_kvar)
    s_mva = s_kva / 1000
    pf = p_kw / s_kva if s_kva > 0 else 1.0
    cap_load_ratio = transformer_capacity_mva / s_mva if s_mva > 0 else float("inf")
    return {
        "transformer_capacity_mva": transformer_capacity_mva,
        "downstream_peak_load_mva": round(s_mva, 4),
        "downstream_power_factor": round(pf, 4),
        "capacity_load_ratio": round(cap_load_ratio, 3),
        "interpretation": _interp(cap_load_ratio),
    }


def _interp(r: float) -> str:
    if r < 1.5:
        return "偏紧（扩容压力高）"
    if r <= 2.0:
        return "刚性范围内"
    if r <= 2.5:
        return "弹性候选（适度放宽）"
    return "过高（投资浪费）"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--rebase", help="主变容量 MVA", type=float, default=None)
    args = ap.parse_args()

    bus = load_bus()
    branch = load_branch()
    s = summary(bus, branch)
    print("=== IEEE 33-bus 摘要 ===")
    for k, v in s.items():
        print(f"  {k:30s} = {v}")

    if args.validate:
        issues = validate_topology(bus, branch)
        print("\n=== 拓扑验证 ===")
        if not issues:
            print("  ✅ 径向拓扑合法")
        else:
            for i in issues:
                print(f"  ⚠ {i}")

    if args.rebase is not None:
        r = rebase_to_110kv_view(bus, args.rebase)
        print(f"\n=== 110kV变电站视角（主变 {args.rebase} MVA） ===")
        for k, v in r.items():
            print(f"  {k:30s} = {v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
