#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""依据冻结 v3.2 结果生成研究报告终稿图件。"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report_interval_matrix import build_report_interval_outputs  # noqa: E402


def setup_style() -> None:
    font = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    if Path(font).is_file():
        fm.fontManager.addfont(font)
    plt.rcParams.update(
        {
            "font.sans-serif": ["Noto Sans CJK JP", "Noto Sans CJK SC", "SimHei"],
            "axes.unicode_minus": False,
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "legend.fontsize": 10,
            "figure.dpi": 140,
            "savefig.dpi": 300,
        }
    )


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def flow_figure(out: Path, *, application: bool) -> None:
    if application:
        labels = [
            "获取片区运行与规划数据",
            "计算 4 项核心指标",
            "核查网络技术可行性",
            "逐项匹配具体指标区间",
            "识别未覆盖的指标组合",
            "取得建议下限或非数值结论",
            "比选扩建、储能与网络互济措施",
        ]
        title = "弹性容载比工程应用流程"
    else:
        labels = [
            "年度容量、同步正向峰值与设备资料",
            "正向容量与反向承载校核",
            "离散扩建、储能及网络措施",
            "2021 年实际在役资产共同起点",
            "弹性容载比控制值扫描与敏感性分析",
            "片区指标—规划响应—建议映射",
        ]
        title = "研究技术路线"
    fig, ax = plt.subplots(figsize=(7.1, 8.0 if application else 7.2))
    ax.axis("off")
    ys = np.linspace(0.88, 0.10, len(labels))
    for i, (label, y) in enumerate(zip(labels, ys)):
        ax.text(
            0.5,
            y,
            label,
            ha="center",
            va="center",
            fontsize=12,
            bbox=dict(boxstyle="round,pad=0.55", fc="#F3F7FB", ec="#235789", lw=1.5),
        )
        if i < len(labels) - 1:
            ax.annotate(
                "",
                xy=(0.5, ys[i + 1] + 0.045),
                xytext=(0.5, y - 0.045),
                arrowprops=dict(arrowstyle="->", color="#235789", lw=1.6),
            )
    ax.set_title(title, pad=14, fontweight="bold")
    save(fig, out)


def concept_figure(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.axis("off")
    boxes = [
        (0.02, 0.58, 0.43, 0.30, "实际物理容载比\n在役变电容量 ÷ 同期正向年最大供电负荷\n用于描述实际容量配置状态"),
        (0.55, 0.58, 0.43, 0.30, "弹性容载比控制值\n只约束规划期新增变电容量\n用于控制新增容量空间"),
        (0.16, 0.10, 0.68, 0.25, "2021 年实际在役容量作为共同起点并保留\n因此实际物理容载比可高于规划控制值，且不构成违规"),
    ]
    for x, y, w, h, text in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, fc="#F6F8FA", ec="#234F7D", lw=1.6))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", linespacing=1.5)
    ax.annotate("概念分离", xy=(0.50, 0.71), xytext=(0.50, 0.71), ha="center", color="#9C2F2F")
    ax.annotate("", xy=(0.36, 0.35), xytext=(0.25, 0.58), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate("", xy=(0.64, 0.35), xytext=(0.75, 0.58), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.set_title("实际物理容载比与规划控制值的关系", pad=10, fontweight="bold")
    save(fig, out)


def indicator_figure(indicators: pd.DataFrame, out: Path) -> None:
    d = indicators.sort_values("region_id")
    labels = d["region_id"].tolist()
    specs = [
        ("source_load_scale_ratio", "现状源荷规模比", "—"),
        ("local_reverse_flow_ratio", "局部最大反向潮流比例", "%"),
        ("network_capacity_support_margin", "网络容量支撑裕度", "%"),
        ("positive_peak_cagr_2021_2025", "正向峰值负荷年均变化率", "%"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 7.0), constrained_layout=True)
    colors = ["#2F6B9A", "#5B8C5A", "#C27A28", "#8B5E83"]
    for ax, (col, title, unit), color in zip(axes.flat, specs, colors):
        values = d[col].astype(float).to_numpy()
        shown = values * 100 if unit == "%" else values
        y = np.arange(len(labels))
        ax.axvline(0, color="#777", lw=0.8)
        ax.scatter(shown, y, s=42, color=color, zorder=3)
        for x, yy in zip(shown, y):
            if np.isnan(x):
                ax.text(0, yy, "未识别", va="center", ha="left", color="#777")
            else:
                suffix = "%" if unit == "%" else ""
                ax.text(x, yy - 0.22, f"{x:.2f}{suffix}", va="center", ha="center", fontsize=8)
        ax.set_yticks(y, labels)
        ax.invert_yaxis()
        ax.set_title(title)
        ax.grid(axis="x", color="#E4E7EB", lw=0.8)
        ax.set_xlabel(unit)
    fig.suptitle("典型片区核心指标实际值", fontweight="bold")
    save(fig, out)


def frontier_figures(out_cost: Path, out_actions: Path) -> None:
    path = ROOT / "results/runs/real-2021-2025-v32-frozen/elasticity_frontier_v32_actual_coarse.csv"
    d = pd.read_csv(path)
    d = d[d["region_id"].isin(["QX-00001", "QX-00005"]) & d["rcap_numeric"].notna()].copy()
    colors = {"QX-00001": "#2F6B9A", "QX-00005": "#D9792B"}

    fig, axes = plt.subplots(2, 1, figsize=(7.5, 6.3), sharex=True, constrained_layout=True)
    for ax, region in zip(axes, ["QX-00001", "QX-00005"]):
        x = d[d.region_id.eq(region)].sort_values("rcap_numeric")
        ax.plot(x["rcap_numeric"], x["cumulative_in_service_eac_wanyuan"], marker="o", color=colors[region])
        ax.set_title(region)
        ax.set_ylabel("年化规划成本 / （万元/年）")
        ax.grid(color="#E4E7EB")
    axes[-1].set_xlabel(r"弹性容载比控制值 $R_{\mathrm{cap}}$")
    fig.suptitle("弹性容载比控制值与年化规划成本", fontweight="bold")
    save(fig, out_cost)

    fig, axes = plt.subplots(2, 2, figsize=(8.0, 6.4), sharex=True, constrained_layout=True)
    for row, region in enumerate(["QX-00001", "QX-00005"]):
        x = d[d.region_id.eq(region)].sort_values("rcap_numeric")
        axes[row, 0].step(x["rcap_numeric"], x["capacity_action_delta_mva"], where="post", color=colors[region])
        axes[row, 1].step(x["rcap_numeric"], x["storage_modules"], where="post", color=colors[region])
        axes[row, 0].set_ylabel(f"{region}\n新增容量 / MVA")
        axes[row, 1].set_ylabel("储能配置数量 / 个")
        for ax in axes[row]:
            ax.grid(color="#E4E7EB")
    axes[0, 0].set_title("新增变电容量")
    axes[0, 1].set_title("储能配置数量")
    for ax in axes[-1]:
        ax.set_xlabel(r"弹性容载比控制值 $R_{\mathrm{cap}}$")
    fig.suptitle("控制值变化引起的规划措施转换", fontweight="bold")
    save(fig, out_actions)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    setup_style()
    support_dir = ROOT / "reports/report_reconstruction"
    outputs = build_report_interval_outputs(ROOT, support_dir)
    indicators = pd.read_csv(outputs["candidate_indicators"])
    out = args.output_dir
    flow_figure(out / "图1-1_研究技术路线.png", application=False)
    concept_figure(out / "图3-1_物理容载比与规划控制值.png")
    indicator_figure(indicators, out / "图4-1_典型片区核心指标.png")
    frontier_figures(out / "图5-1_弹性控制值成本前沿.png", out / "图5-2_弹性控制值规划响应.png")
    flow_figure(out / "图8-1_工程应用流程.png", application=True)
    print(f"WROTE 6 figures to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
