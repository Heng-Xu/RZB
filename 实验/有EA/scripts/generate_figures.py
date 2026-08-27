#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
论文图表生成器：从 results/ 中的CSV生成6图+3表

输出：
  results/figures/fig1_dilemma.png
  results/figures/fig2_framework.png
  results/figures/fig3_decision_matrix.png
  results/figures/fig4_topology.png
  results/figures/fig5_lcc_comparison.png
  results/figures/fig6_sensitivity.png
  results/tables/tab1_ahp_matrix.csv     (复制自 ahp 步骤)
  results/tables/tab2_cases_params.csv
  results/tables/tab3_recommendation.csv

中文标签：尝试使用系统CJK字体，失败回退英文。
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGS = RESULTS / "figures"
TABS = RESULTS / "tables"


def setup_fonts():
    """尝试设置中文字体；如未在 matplotlib 缓存中则手动注册"""
    from matplotlib import font_manager as fm
    import os, glob

    candidates = [
        "Noto Sans CJK SC", "Noto Serif CJK SC", "WenQuanYi Zen Hei",
        "WenQuanYi Micro Hei", "Microsoft YaHei", "SimHei", "SimSun",
        "PingFang SC", "Source Han Sans CN", "AR PL UMing CN", "AR PL UMing TW",
    ]

    # 显式扫描系统CJK字体目录并注册到matplotlib
    search_dirs = [
        "/usr/share/fonts/opentype/noto",
        "/usr/share/fonts/truetype/wqy",
        "/usr/share/fonts/truetype/arphic",
        "/usr/share/fonts",
        os.path.expanduser("~/.fonts"),
    ]
    patterns = ["*CJK*.ttc", "*CJK*.otf", "*wqy*.ttc", "*wqy*.ttf",
                "uming*.ttc", "ukai*.ttc"]
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for pat in patterns:
            for f in glob.glob(os.path.join(d, "**", pat), recursive=True):
                try:
                    fm.fontManager.addfont(f)
                except Exception:
                    pass

    available = {f.name for f in fm.fontManager.ttflist}
    for c in candidates:
        if c in available:
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["font.sans-serif"] = [c] + plt.rcParams["font.sans-serif"]
            plt.rcParams["axes.unicode_minus"] = False
            print(f"[FONT] using {c}")
            return True
    print("[WARN] no CJK font found; using English labels")
    plt.rcParams["axes.unicode_minus"] = False
    return False


CJK_OK = setup_fonts()


def L(zh: str, en: str) -> str:
    return zh if CJK_OK else en


# ──────────────────────────────────────────────────────────────────────
# Figure 1: Two-way pressure dilemma
# ──────────────────────────────────────────────────────────────────────


def fig1_dilemma():
    fig, ax = plt.subplots(figsize=(8, 5))
    scenarios = [L("夏冬重载", "Sum/Win Peak"), L("春秋反送", "Spr/Aut Reverse")]
    rigid = [85, 30]   # 主变负载率
    elastic = [70, 75]
    x = np.arange(len(scenarios))
    w = 0.35
    ax.bar(x - w/2, rigid, w, label=L("刚性R≤2.0", "Rigid R<=2.0"), color="#c0392b")
    ax.bar(x + w/2, elastic, w, label=L("弹性R∈[1.8,2.4]", "Elastic R in [1.8,2.4]"), color="#27ae60")
    ax.axhline(100, color="black", ls=":", lw=1, label=L("主变容量上限", "Tx Capacity Limit"))
    ax.set_xticks(x); ax.set_xticklabels(scenarios)
    ax.set_ylabel(L("主变负载率(%)", "Tx Load Rate (%)"))
    ax.set_title(L("两难困境：源荷双向运行压力", "Bidirectional Operation Dilemma"))
    ax.legend(loc="upper right"); ax.set_ylim(0, 120)
    plt.tight_layout()
    out = FIGS / "fig1_dilemma.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ──────────────────────────────────────────────────────────────────────
# Figure 2: Framework flowchart (simple boxes)
# ──────────────────────────────────────────────────────────────────────


def fig2_framework():
    fig, ax = plt.subplots(figsize=(11, 7.5))
    ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    boxes = [
        (0.5, 0.93, L("输入：源荷比/渗透率/联络度", "Input: SLR / Penetration / CD")),
        (0.5, 0.75, L("反向承载力校核准入（裸主变反向重载 ≤ 0.85·R·峰荷）",
                      "Reverse hosting-capacity check (admission gate)")),
        (0.5, 0.57, L("过校核者进入：方案A 刚性2.0+配储 ／ 方案B 弹性放宽+增容",
                      "Survivors: Plan A Rigid2.0+BESS / Plan B Elastic+Expand")),
        (0.5, 0.39, L("双向Z4-LCC对比（年费用法）", "Bidirectional Z4-LCC Comparison")),
        (0.5, 0.21, L("AHP多准则权重", "AHP Multi-Criteria Weighting")),
        (0.5, 0.03, L("一片一策决策矩阵", "Zone-Specific Decision Matrix")),
    ]
    colors = ["#3498db", "#e74c3c", "#9b59b6", "#e67e22", "#16a085", "#c0392b"]
    bw, bh = 0.86, 0.09
    for (x, y, txt), c in zip(boxes, colors):
        ax.add_patch(plt.Rectangle((x-bw/2, y-bh/2), bw, bh,
                                    facecolor=c, alpha=0.78, edgecolor="black"))
        ax.text(x, y, txt, ha="center", va="center", fontsize=9.5, color="white",
                weight="bold")
    for i in range(len(boxes)-1):
        ax.annotate("", xy=(0.5, boxes[i+1][1] + bh/2), xytext=(0.5, boxes[i][1] - bh/2),
                    arrowprops=dict(arrowstyle="->", lw=2, color="gray"))
    ax.set_title(L("决策框架流程图（含反向承载力校核准入）",
                   "Decision Framework (with reverse hosting-capacity gate)"), fontsize=13)
    plt.tight_layout()
    out = FIGS / "fig2_framework.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ──────────────────────────────────────────────────────────────────────
# Figure 3: Decision matrix heatmap
# ──────────────────────────────────────────────────────────────────────


def fig3_decision_matrix():
    df = pd.read_csv(RESULTS / "decision_matrix_raw.csv")

    # 3个联络度面板的 3×3 矩阵
    cd_labels = ["弱", "中", "强"]
    sl_labels = ["低", "中", "高"]
    pe_labels = ["低", "中", "高"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax_idx, cd in enumerate(cd_labels):
        sub = df[df["interconnection_level"] == cd]
        mat = np.zeros((3, 3))
        for i, sl in enumerate(sl_labels):
            for j, pe in enumerate(pe_labels):
                v = sub[(sub["source_load_level"] == sl) &
                        (sub["penetration_level"] == pe)]
                if not v.empty:
                    mat[i, j] = v["best_cap_load_ratio"].iloc[0]

        ax = axes[ax_idx]
        im = ax.imshow(mat, cmap="RdYlGn_r", vmin=1.5, vmax=2.6, aspect="auto")
        ax.set_xticks(range(3))
        ax.set_xticklabels([L(f"渗透{p}", f"Pen.{p}") for p in pe_labels])
        ax.set_yticks(range(3))
        ax.set_yticklabels([L(f"源荷{s}", f"SLR.{s}") for s in sl_labels])
        ax.set_title(L(f"联络度: {cd}", f"CD: {cd}"), fontsize=12)
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f"{mat[i, j]:.1f}", ha="center", va="center",
                       color="black", fontsize=11, weight="bold")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    plt.suptitle(L("三维分类决策矩阵——推荐容载比",
                  "3D Classification Decision Matrix - Recommended R"), fontsize=14)
    plt.tight_layout()
    out = FIGS / "fig3_decision_matrix.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ──────────────────────────────────────────────────────────────────────
# Figure 4: IEEE 33-bus topology
# ──────────────────────────────────────────────────────────────────────


def fig4_topology():
    bus = pd.read_csv(ROOT / "datasets" / "ieee33" / "ieee33_bus.csv")
    branch = pd.read_csv(ROOT / "datasets" / "ieee33" / "ieee33_branch.csv")

    # 用简化布局：spring layout 近似（手动放置主干 + 分支）
    pos = {}
    pos[1] = (0, 0)
    # 主干 1→18
    for b in range(2, 19):
        pos[b] = (b - 1, 0)
    # 分支1: 2→19→22
    for k, b in enumerate(range(19, 23), 1):
        pos[b] = (1 + k * 0.6, 1.5)
    # 分支2: 3→23→25
    for k, b in enumerate(range(23, 26), 1):
        pos[b] = (2 + k * 0.6, 2.5)
    # 分支3: 6→26→33
    for k, b in enumerate(range(26, 34), 1):
        pos[b] = (5 + k * 0.6, -1.5)

    fig, ax = plt.subplots(figsize=(13, 6))
    pv_buses = {18, 22, 24, 25, 30, 32}
    # 画支路
    for _, br in branch.iterrows():
        a, b = pos.get(br["from_bus"]), pos.get(br["to_bus"])
        if a and b:
            ax.plot([a[0], b[0]], [a[1], b[1]], "k-", lw=1.2, alpha=0.5)
    # 画节点
    for b in bus["bus"]:
        x, y = pos.get(b, (0, 0))
        if b == 1:
            ax.scatter(x, y, s=300, c="#e74c3c", marker="s", zorder=5,
                       label=L("110kV变电站", "110kV Substation") if b == 1 else None)
        elif b in pv_buses:
            ax.scatter(x, y, s=200, c="#f39c12", marker="^", zorder=5)
        else:
            ax.scatter(x, y, s=100, c="#3498db", zorder=4)
        ax.text(x, y - 0.25, str(b), ha="center", fontsize=8)

    ax.scatter([], [], s=200, c="#f39c12", marker="^",
               label=L("PV注入节点", "PV Injection Node"))
    ax.scatter([], [], s=100, c="#3498db", label=L("负荷节点", "Load Node"))
    ax.legend(loc="upper right")
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs) - 1, max(xs) + 1)      # 自动适配，避免主干 13-18 被裁剪
    ax.set_ylim(min(ys) - 1.2, max(ys) + 1)
    ax.set_title(L("IEEE 33-bus 测试系统含PV注入", "IEEE 33-bus Test System with PV"))
    ax.axis("off")
    plt.tight_layout()
    out = FIGS / "fig4_topology.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ──────────────────────────────────────────────────────────────────────
# Figure 5: A vs B LCC comparison curve
# ──────────────────────────────────────────────────────────────────────


def fig5_lcc_comparison():
    df = pd.read_csv(RESULTS / "sweep_penetration.csv")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    x = df["energy_penetration_pct"]

    ax1.plot(x, df["rigid_annual_wan"], "o-",
             color="#c0392b", lw=2,
             label=L("刚性容载比 R=2.0", "Rigid R=2.0"))
    ax1.plot(x, df["adaptive_annual_wan"], "s-",
             color="#27ae60", lw=2,
             label=L("自适应容载比（决策矩阵）", "Adaptive R (matrix)"))
    # 标注自适应所选R（每隔一点，显示双向：低渗透降R、高渗透升R）
    for i in range(0, len(df), 2):
        ax1.annotate(f"R{df['adaptive_R'].iloc[i]}",
                     (x.iloc[i], df["adaptive_annual_wan"].iloc[i]),
                     textcoords="offset points", xytext=(0, -12),
                     fontsize=7.5, color="#1e8449", ha="center")
    ax1.set_xlabel(L("电量渗透率 (%)", "Energy Penetration (%)"))
    ax1.set_ylabel(L("年化总成本 (万元/年)", "Annualized Cost (10k CNY/yr)"))
    ax1.set_title(L("刚性2.0 vs 自适应容载比 年化成本",
                    "Rigid 2.0 vs Adaptive Cost"))
    ax1.legend(); ax1.grid(alpha=0.3)

    cmap = {"降容载比": "#2980b9", "升容载比": "#e67e22", "维持2.0": "#7f8c8d"}
    ax2.bar(x, df["saving_wan_year"], width=2.5,
            color=[cmap.get(d, "#7f8c8d") for d in df["direction"]])
    ax2.axhline(0, color="black", lw=0.8)
    ax2.set_xlabel(L("电量渗透率 (%)", "Energy Penetration (%)"))
    ax2.set_ylabel(L("相对刚性2.0年化节省 (万元/年)", "Saving vs Rigid 2.0 (10k CNY/yr)"))
    ax2.set_title(L("自适应容载比节省（蓝=降R/橙=升R）",
                    "Adaptive Saving (blue=down/orange=up)"))
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    out = FIGS / "fig5_lcc_comparison.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ──────────────────────────────────────────────────────────────────────
# Figure 6: AHP weight sensitivity radar
# ──────────────────────────────────────────────────────────────────────


def fig6_sensitivity():
    import yaml
    with (ROOT / "datasets" / "cost_params" / "baseline_costs.yaml").open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    criteria = cfg["ahp_criteria"]
    names = [c["name"] for c in criteria]
    base = [c["weight_init"] for c in criteria]

    # 模拟 ±20% 包络
    upper = [w * 1.2 for w in base]
    lower = [w * 0.8 for w in base]
    # 归一化
    s_u, s_l, s_b = sum(upper), sum(lower), sum(base)
    upper = [w / s_u for w in upper]
    lower = [w / s_l for w in lower]
    base = [w / s_b for w in base]

    # Radar setup
    angles = np.linspace(0, 2 * np.pi, len(names), endpoint=False).tolist()
    base += base[:1]; upper += upper[:1]; lower += lower[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.plot(angles, base, "o-", linewidth=2, color="#2c3e50",
            label=L("基线权重", "Baseline"))
    ax.fill_between(angles, lower, upper, alpha=0.2, color="#3498db",
                    label=L("±20%扰动范围", "±20% Range"))
    ax.set_xticks(angles[:-1])
    if CJK_OK:
        ax.set_xticklabels(names, fontsize=10)
    else:
        ax.set_xticklabels(["C1-Econ", "C2-Reliab", "C3-RE", "C4-Imp", "C5-Pol"])
    ax.set_ylim(0, max(upper) * 1.1)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.set_title(L("AHP准则权重±20%扰动包络",
                   "AHP Criteria Weights ±20% Envelope"), pad=20, fontsize=13)
    plt.tight_layout()
    out = FIGS / "fig6_sensitivity.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out}")


# ──────────────────────────────────────────────────────────────────────
# Tables
# ──────────────────────────────────────────────────────────────────────


def export_tables():
    # tab1: AHP判断矩阵（已生成，仅复制）
    src = RESULTS / "ahp_judgment_matrix.csv"
    if src.exists():
        shutil.copy(src, TABS / "tab1_ahp_matrix.csv")
        print(f"[OK] {TABS / 'tab1_ahp_matrix.csv'}")

    # tab2: 典型片区参数（自适应容载比 vs 刚性2.0，双口径）
    df_p = pd.read_csv(RESULTS / "sweep_penetration.csv")
    df_p = df_p[["pv_kwp", "source_load_ratio", "energy_penetration_pct",
                 "rigid_annual_wan", "adaptive_R", "adaptive_annual_wan",
                 "saving_wan_year", "saving_pct", "direction"]].copy()
    df_p.columns = ["PV装机(kWp)", "源荷比", "电量渗透率(%)", "刚性2.0年成本(万)",
                    "自适应R", "自适应年成本(万)", "节省(万/年)",
                    "节省占比(%)", "容载比方向"]
    df_p.to_csv(TABS / "tab2_cases_params.csv", index=False, encoding="utf-8")
    print(f"[OK] {TABS / 'tab2_cases_params.csv'}")

    # tab3: 一片一策推荐表（含数据基础标注）
    df_m = pd.read_csv(RESULTS / "decision_matrix_raw.csv")
    df_m_pub = df_m[["source_load_level", "penetration_level", "interconnection_level",
                      "best_cap_load_ratio", "recommended_range",
                      "best_annual_cost_wan", "tech_scheme", "basis"]].copy()
    df_m_pub.columns = ["源荷比", "电量渗透率", "联络度", "推荐R", "推荐区间",
                        "最优年成本(万)", "技术方案组合", "数据基础"]
    df_m_pub.to_csv(TABS / "tab3_recommendation.csv", index=False, encoding="utf-8")
    print(f"[OK] {TABS / 'tab3_recommendation.csv'}")


def fig10_reverse_capacity():
    """反向承载力可行域：(PV/源荷比 × 容载比R) 裸反向重载校核通过/越限 + 反送电压片区旗标。"""
    import matplotlib.patches as mpatches
    src = RESULTS / "reverse_capacity_check.csv"
    if not src.exists():
        print(f"[SKIP] fig10: {src} 不存在")
        return
    df = pd.read_csv(src)
    pvs = sorted(df.pv_kwp.unique())
    Rs = sorted(df.cap_load_ratio.unique())
    slr = {pv: df[df.pv_kwp == pv].source_load_ratio.iloc[0] for pv in pvs}
    Z = np.zeros((len(pvs), len(Rs)))
    V = np.zeros((len(pvs), len(Rs)), dtype=bool)
    for i, pv in enumerate(pvs):
        for j, r in enumerate(Rs):
            row = df[(df.pv_kwp == pv) & (df.cap_load_ratio == r)].iloc[0]
            Z[i, j] = 1.0 if row.reverse_check_passed else 0.0
            V[i, j] = bool(row.voltage_exceed)

    from matplotlib.colors import ListedColormap
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(Z, cmap=ListedColormap(["#e74c3c", "#2ecc71"]),
              aspect="auto", origin="lower", vmin=0, vmax=1)
    for i in range(len(pvs)):
        for j in range(len(Rs)):
            if V[i, j]:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False,
                                           hatch="///", edgecolor="#2c3e50", lw=0))
    ax.set_xticks(range(len(Rs))); ax.set_xticklabels([f"{r:g}" for r in Rs])
    ax.set_yticks(range(len(pvs)))
    ax.set_yticklabels([f"{pv/1000:g}MWp(ρ={slr[pv]:.1f})" for pv in pvs], fontsize=8)
    ax.set_xlabel(L("容载比 R", "Capacity-load ratio R"))
    ax.set_ylabel(L("PV装机 / 源荷比ρ", "PV capacity / source-load ratio"))
    ax.set_title(L("反向承载力可行域（裸主变反向重载校核）",
                   "Reverse hosting-capacity feasible region"), fontsize=12)
    handles = [
        mpatches.Patch(color="#2ecc71", label=L("通过（纯主变可消纳反送）", "Pass")),
        mpatches.Patch(color="#e74c3c", label=L("越限（需配储/治理→方案A）", "Overload")),
        mpatches.Patch(facecolor="white", hatch="///", edgecolor="#2c3e50",
                       label=L("反送电压旗标越限（片区级,演示）", "Voltage flag")),
    ]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=9)
    plt.tight_layout()
    out = FIGS / "fig10_reverse_capacity.png"
    plt.savefig(out, dpi=300, bbox_inches="tight"); plt.close()
    print(f"[OK] {out}")


def main() -> int:
    FIGS.mkdir(parents=True, exist_ok=True)
    TABS.mkdir(parents=True, exist_ok=True)

    fig1_dilemma()
    fig2_framework()
    fig3_decision_matrix()
    fig4_topology()
    fig5_lcc_comparison()
    fig6_sensitivity()
    fig10_reverse_capacity()
    export_tables()

    print(f"\n[DONE] all figures and tables generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
