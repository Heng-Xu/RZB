#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成研究报告10 kV高光伏跨站供电边界重构示意图。

图件仅表达规划级供电边界重构与反向功率空间转移关系，
不表示现场实时开关状态、保护动作或具体倒闸顺序。
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def setup_style() -> None:
    font = Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc")
    if font.is_file():
        fm.fontManager.addfont(str(font))
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["FangSong", "FangSong_GB2312", "Noto Serif CJK SC", "Noto Serif CJK JP", "SimSun"],
            "axes.unicode_minus": False,
            "font.size": 13,
            "figure.dpi": 220,
            "savefig.dpi": 600,
        }
    )


def box(ax, x, y, w, h, text, *, fc="#F7F8FA", ec="#53606D", lw=1.5, fs=12.4):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.018,rounding_size=0.035",
        facecolor=fc, edgecolor=ec, linewidth=lw,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, linespacing=1.40)


def arrow(ax, x1, y1, x2, y2, *, text=None, color="#44515E", lw=1.9, text_y=None):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=color, mutation_scale=14))
    if text:
        y = (y1 + y2) / 2 if text_y is None else text_y
        ax.text((x1 + x2) / 2, y, text, ha="center", va="bottom", fontsize=11.2, color=color)


def build(out: Path) -> None:
    setup_style()
    fig, ax = plt.subplots(figsize=(13.0, 7.2))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    ax.text(6.5, 6.80, "高光伏条件下的跨站供电边界重构与反向功率转移",
            ha="center", va="center", fontsize=16, fontweight="bold")
    ax.text(6.5, 6.30,
            "规划约束：保持10 kV单电源辐射运行；不允许两个110 kV电源经10 kV网络直接并列",
            ha="center", va="center", fontsize=11.8,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#FAFBFC", edgecolor="#6B7280", linewidth=1.1))

    # 主网络关系：四个信息块水平展开，避免文字、箭头互相覆盖。
    y = 4.35
    box(ax, 0.35, y, 1.75, 1.15, "墩集变\n110 kV送端", fc="#EAF2F8", ec="#315B7D", lw=1.7)
    box(ax, 2.75, y, 2.55, 1.15, "墩南线高光伏供电单元\n光伏出力高于本地负荷\n形成净外送功率", fc="#FFF7E8", ec="#9A6B2E", lw=1.7)
    box(ax, 5.95, y, 1.95, 1.15, "墩南—河炮\n既有联络通道", fc="#FCEFEF", ec="#9B4545", lw=1.7)
    box(ax, 8.55, y, 2.15, 1.15, "河炮线\n受端10 kV通道", fc="#F1F7F1", ec="#4F7658", lw=1.7)
    box(ax, 11.20, y, 1.45, 1.15, "河湾变\n110 kV受端", fc="#EAF2F8", ec="#315B7D", lw=1.7)

    arrow(ax, 2.10, y + 0.58, 2.75, y + 0.58, text="原供电边界", color="#315B7D", text_y=5.12)
    arrow(ax, 5.30, y + 0.58, 5.95, y + 0.58, text="边界调整", color="#9B4545", text_y=5.12)
    arrow(ax, 7.90, y + 0.58, 8.55, y + 0.58, text="反向功率转移", color="#9B4545", text_y=5.12)
    arrow(ax, 10.70, y + 0.58, 11.20, y + 0.58, text="受端承接", color="#4F7658", text_y=5.12)

    # 下方按规划逻辑拆成三个独立信息块。
    box(ax, 0.65, 2.15, 3.35, 1.25,
        "送端减压\n跨站转移后，墩集变承担的反向功率减小\n用于缓解局部110 kV反向承载压力",
        fc="#F3F8F3", ec="#4F7658", fs=11.8)
    box(ax, 4.82, 2.15, 3.35, 1.25,
        "既有联络优先\n同时校核送端路径、受端路径和河湾变\n剩余反向承接能力",
        fc="#F7F8FA", ec="#53606D", fs=11.8)
    box(ax, 9.00, 2.15, 3.35, 1.25,
        "能力不足时再新增联络\n计算剩余需转移功率和最小有效容量\n筛选具备容量条件的候选受端馈线",
        fc="#FFF8ED", ec="#9A6B2E", fs=11.8)

    arrow(ax, 4.03, 4.35, 2.35, 3.40, color="#4F7658")
    arrow(ax, 6.92, 4.35, 6.50, 3.40, color="#53606D")
    arrow(ax, 9.63, 4.35, 10.68, 3.40, color="#9A6B2E")

    box(ax, 1.55, 0.48, 9.90, 0.82,
        "研究边界：本模型用于规划级拓扑与容量筛查；实时开关状态、具体倒闸顺序、交流潮流、短路电流及继电保护定值在工程实施阶段专项校核。",
        fc="#FAFBFC", ec="#6B7280", lw=1.1, fs=11.4)

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=600, bbox_inches="tight", pad_inches=0.18, facecolor="white")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("研究报告/终稿/图表/图6-1_TIE002分段联络示意.png"),
    )
    args = parser.parse_args()
    build(args.output)
    print(f"generated: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
