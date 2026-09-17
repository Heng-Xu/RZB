#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""依据项目正式结果生成研究报告终稿图件。"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.report_interval_matrix import build_report_interval_outputs  # noqa: E402


def setup_style() -> None:
    """统一图件中文字体、字号和输出精度，尽量与中文报告正文保持一致。"""
    font = Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc")
    if font.is_file():
        fm.fontManager.addfont(str(font))
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["FangSong", "FangSong_GB2312", "Noto Serif CJK SC", "Noto Serif CJK JP", "SimSun"],
            "axes.unicode_minus": False,
            "font.size": 13,
            "axes.titlesize": 15,
            "axes.labelsize": 13,
            "legend.fontsize": 12,
            "xtick.labelsize": 11.5,
            "ytick.labelsize": 11.5,
            "figure.dpi": 220,
            "savefig.dpi": 600,
        }
    )


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=600, bbox_inches="tight", pad_inches=0.18, facecolor="white")
    plt.close(fig)


def _rounded_box(ax, x, y, w, h, text, *, fc="#F6F8FA", ec="#355C7D", fs=13, lw=1.6) -> None:
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=fc, edgecolor=ec, linewidth=lw,
        transform=ax.transAxes,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, transform=ax.transAxes,
            ha="center", va="center", fontsize=fs, linespacing=1.38)


def flow_figure(out: Path, *, application: bool) -> None:
    if application:
        labels = [
            "获取片区运行与规划数据",
            "计算四项核心运行指标",
            "核查设备、网络与接入技术条件",
            "检索已验证的相似典型样本",
            "开展弹性容载比规划控制值专项扫描",
            "识别稳健建议下限及适用边界",
            "比选变电扩建、储能与网络互济措施",
        ]
        title = "弹性容载比工程应用流程"
        fig_h = 9.8
    else:
        labels = [
            "数据整理与口径统一\n容量、负荷、新能源及线路资料",
            "运行特征识别\n正向供电压力与局部反向承载压力",
            "工程措施建模\n变电扩建、储能及局部网络互济",
            "统一规划起点\n2021年实际在役资产保持不变",
            "规划优化分析\n控制值扫描、阈值细化与敏感性分析",
            "差异化规划建议\n形成运行特征—规划响应—建议映射",
        ]
        title = "研究技术路线"
        fig_h = 8.9

    fig, ax = plt.subplots(figsize=(9.2, fig_h))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.965, title, transform=ax.transAxes, ha="center", va="top",
            fontsize=16, fontweight="bold")

    top, bottom = 0.88, 0.07
    ys = np.linspace(top, bottom, len(labels))
    h = 0.085 if application else 0.10
    for i, (label, y) in enumerate(zip(labels, ys)):
        _rounded_box(ax, 0.13, y - h / 2, 0.74, h, label,
                     fc="#F5F8FB" if i % 2 == 0 else "#FAFBFC", fs=13.2)
        if i < len(labels) - 1:
            next_y = ys[i + 1]
            ax.annotate(
                "",
                xy=(0.5, next_y + h / 2 + 0.006),
                xytext=(0.5, y - h / 2 - 0.006),
                xycoords=ax.transAxes,
                arrowprops=dict(arrowstyle="-|>", color="#355C7D", lw=1.7, mutation_scale=13),
            )
    save(fig, out)


def concept_figure(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.6, 5.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.95, "实际物理容载比与弹性容载比规划控制值的关系",
            ha="center", va="top", fontsize=16, fontweight="bold", transform=ax.transAxes)

    _rounded_box(ax, 0.05, 0.56, 0.40, 0.24,
                 "实际物理容载比\n在役变电总容量 ÷ 同期正向年最大供电负荷\n用于描述规划方案形成后的实际容量配置状态",
                 fc="#F4F8FB", ec="#315B7D", fs=12.6)
    _rounded_box(ax, 0.55, 0.56, 0.40, 0.24,
                 "弹性容载比规划控制值\n仅约束规划期允许新增的变电容量\n用于调节扩建、储能和网络措施的选择空间",
                 fc="#F8F6F1", ec="#8A673A", fs=12.6)
    _rounded_box(ax, 0.16, 0.15, 0.68, 0.20,
                 "共同规划基础：2021年实际在役容量保持在役并执行存量豁免\n规划控制值不追溯压减既有资产，因此实际物理容载比可高于规划控制值",
                 fc="#F7F8FA", ec="#5E6875", fs=12.8)
    for x in (0.25, 0.75):
        ax.annotate("", xy=(0.50, 0.36), xytext=(x, 0.56), xycoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#5E6875", mutation_scale=12))
    save(fig, out)


def indicator_figure(indicators: pd.DataFrame, out: Path) -> None:
    d = indicators[indicators["region_id"].isin(["QX-00001", "QX-00005"])].sort_values("region_id")
    labels = d["region_id"].tolist()
    specs = [
        ("source_load_scale_ratio", "现状源荷规模比", ""),
        ("local_reverse_flow_ratio", "局部最大反向潮流比例", "%"),
        ("network_capacity_support_margin", "110 kV线路统计负载余度", "%"),
        ("positive_peak_cagr_2021_2025", "正向峰值负荷年均变化率", "%"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(10.0, 7.8), constrained_layout=True)
    colors = ["#355C7D", "#4F7B61", "#A06B32", "#775D78"]
    for ax, (col, title, unit), color in zip(axes.flat, specs, colors):
        values = d[col].astype(float).to_numpy()
        shown = values * 100 if unit == "%" else values
        y = np.arange(len(labels))
        ax.scatter(shown, y, s=72, color=color, zorder=3)
        span = np.nanmax(shown) - np.nanmin(shown) if len(shown) else 1.0
        offset = max(span * 0.08, 0.02 if unit == "" else 0.35)
        for x, yy in zip(shown, y):
            suffix = "%" if unit == "%" else ""
            ax.text(x + offset, yy, f"{x:.2f}{suffix}", va="center", ha="left", fontsize=11.5)
        ax.set_yticks(y, labels)
        ax.invert_yaxis()
        ax.set_title(title, pad=10, fontweight="bold")
        ax.grid(axis="x", color="#D9DEE5", lw=0.8, alpha=0.9)
        ax.set_xlabel("比例" if unit == "%" else "比值")
        ax.margins(x=0.22, y=0.35)
    fig.suptitle("形成数值型规划建议的典型片区核心运行指标", fontsize=16, fontweight="bold")
    save(fig, out)


def frontier_figures(out_cost: Path, out_actions: Path) -> None:
    path = ROOT / "results/runs/real-2021-2025-v32-frozen/elasticity_frontier_v32_actual_coarse.csv"
    d = pd.read_csv(path)
    d = d[d["region_id"].isin(["QX-00001", "QX-00005"]) & d["rcap_numeric"].notna()].copy()
    colors = {"QX-00001": "#355C7D", "QX-00005": "#A86432"}

    fig, axes = plt.subplots(2, 1, figsize=(9.6, 7.8), sharex=True, constrained_layout=True)
    for ax, region in zip(axes, ["QX-00001", "QX-00005"]):
        x = d[d.region_id.eq(region)].sort_values("rcap_numeric")
        ax.plot(x["rcap_numeric"], x["cumulative_in_service_eac_wanyuan"],
                marker="o", markersize=4.8, linewidth=2.0, color=colors[region])
        ax.set_title(region, loc="left", fontweight="bold")
        ax.set_ylabel("规划期累计在役等年成本/万元")
        ax.grid(color="#D9DEE5", linewidth=0.8)
    axes[-1].set_xlabel("弹性容载比规划控制值")
    fig.suptitle("规划控制值变化与规划期累计在役等年成本", fontsize=16, fontweight="bold")
    save(fig, out_cost)

    fig, axes = plt.subplots(2, 2, figsize=(10.0, 7.8), sharex=True, constrained_layout=True)
    for row, region in enumerate(["QX-00001", "QX-00005"]):
        x = d[d.region_id.eq(region)].sort_values("rcap_numeric")
        axes[row, 0].step(x["rcap_numeric"], x["capacity_action_delta_mva"], where="post",
                          linewidth=2.0, color=colors[region])
        axes[row, 1].step(x["rcap_numeric"], x["storage_modules"], where="post",
                          linewidth=2.0, color=colors[region])
        axes[row, 0].set_ylabel(f"{region}\n新增容量/MVA")
        axes[row, 1].set_ylabel(f"{region}\n储能模块/个")
        for ax in axes[row]:
            ax.grid(color="#D9DEE5", linewidth=0.8)
    axes[0, 0].set_title("新增变电容量", fontweight="bold")
    axes[0, 1].set_title("2025年储能配置", fontweight="bold")
    for ax in axes[-1]:
        ax.set_xlabel("弹性容载比规划控制值")
    fig.suptitle("规划控制值变化引起的工程措施转换", fontsize=16, fontweight="bold")
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
    from build_10kv_reverse_transfer_figure import build as build_reverse_transfer_figure
    build_reverse_transfer_figure(out / "图6-1_TIE002分段联络示意.png")
    print(f"WROTE 7 figures to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
