#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成研究报告图6-1：TIE-002高光伏跨站供电边界重构示意。"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt


def setup_style() -> None:
    font = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    if font.is_file():
        fm.fontManager.addfont(str(font))
    plt.rcParams.update(
        {
            "font.sans-serif": ["Noto Sans CJK JP", "Noto Sans CJK SC", "SimHei"],
            "axes.unicode_minus": False,
            "font.size": 10.5,
            "figure.dpi": 140,
            "savefig.dpi": 300,
        }
    )


def box(ax, x, y, w, h, text, fc="#F7F8FA", ec="#4B5563", lw=1.3, fs=10.5):
    ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, text=None, color="#334155", lw=1.8, style="->", dy=0.18):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle=style, lw=lw, color=color))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, text, ha="center", va="center", fontsize=9.5, color=color)


def build(out: Path) -> None:
    setup_style()
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    # 110 kV站与10 kV馈线。
    box(ax, 0.35, 3.95, 1.7, 1.0, "墩集变\n110 kV", fc="#EAF2F8", ec="#2F5D7E", lw=1.6)
    box(ax, 9.95, 3.95, 1.7, 1.0, "河湾变\n110 kV", fc="#EAF2F8", ec="#2F5D7E", lw=1.6)
    box(ax, 2.45, 3.95, 2.1, 1.0, "墩南线\nPZXL-00092", fc="#F3F8F3", ec="#4E7D4E", lw=1.5)
    box(ax, 7.45, 3.95, 2.1, 1.0, "河炮线\nPZXL-00161", fc="#F3F8F3", ec="#4E7D4E", lw=1.5)

    arrow(ax, 2.05, 4.45, 2.45, 4.45, "原供电关系", color="#2F5D7E", dy=0.28)
    arrow(ax, 9.95, 4.45, 9.55, 4.45, "受端供电关系", color="#2F5D7E", dy=0.28)

    # 高光伏净外送单元。
    box(ax, 3.05, 2.0, 2.1, 1.05, "高光伏供电单元\nPV出力 > 本地负荷\n形成净外送 G", fc="#FFF7E6", ec="#B7791F", lw=1.5)
    arrow(ax, 4.10, 3.95, 4.10, 3.05, "反向功率上送", color="#B7791F", dy=0.0)

    # 现有联络。
    box(ax, 5.25, 3.95, 1.5, 1.0, "TIE-002\n既有联络", fc="#FCEFEF", ec="#A13D3D", lw=1.6)
    arrow(ax, 4.55, 4.45, 5.25, 4.45, "供电边界\n重构", color="#A13D3D", dy=0.38)
    arrow(ax, 6.75, 4.45, 7.45, 4.45, "跨站转移", color="#A13D3D", dy=0.28)

    # 站间功率效果。
    box(ax, 0.45, 1.10, 2.1, 1.15, "送端效果\n墩集变反向功率减小\nP_D' = P_D^0 + P_tr", fc="#EEF7EE", ec="#4E7D4E")
    box(ax, 9.45, 1.10, 2.1, 1.15, "受端效果\n河湾变反向功率增加\nP_R' = P_R^0 - P_tr", fc="#EEF7EE", ec="#4E7D4E")
    arrow(ax, 3.05, 2.52, 2.55, 1.68, "减压", color="#4E7D4E", dy=0.0)
    arrow(ax, 8.50, 3.95, 10.45, 2.25, "受端承载校核", color="#4E7D4E", dy=0.05)

    # 两级规划逻辑。
    box(ax, 3.15, 0.25, 5.7, 0.95,
        "两级规划：优先利用既有TIE-002；若 G > 既有联络可转移能力，\n再计算新增联络所需最小有效容量并筛选河东/河镇等候选受端馈线",
        fc="#F7F8FA", ec="#6B7280", lw=1.2, fs=10.0)

    ax.text(6.0, 5.55,
            "规划约束：保持10 kV单电源辐射运行；禁止两个110 kV电源经10 kV网络直接并列",
            ha="center", va="center", fontsize=10.5,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#6B7280", lw=1.0))
    ax.set_title("TIE-002高光伏跨站供电边界重构示意", pad=12, fontweight="bold", fontsize=14)

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
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
