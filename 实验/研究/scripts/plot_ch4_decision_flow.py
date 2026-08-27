#!/usr/bin/env python3
"""绘制图 4-2：刚性与弹性场景决策流程示意（报告第四章素材）。

用法：conda run -n xuzhou110kv_clr python scripts/plot_ch4_decision_flow.py \
        --output ../../研究报告/初稿/图表/图4-2_刚性与弹性场景决策流程.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

FONT_CJK_FILE = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
COLOR_MAIN = "#1F4E79"
COLOR_FILL = "#EEF3F7"
COLOR_FILL_LIGHT = "#F7F7F7"
COLOR_ACCENT_FILL = "#F5EFEA"


def _register_cjk_font() -> str:
    for candidate in (
        str(FONT_CJK_FILE),
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ):
        try:
            font_manager.fontManager.addfont(candidate)
        except Exception:
            continue
    names = [f.name for f in font_manager.fontManager.ttflist if "CJK" in f.name]
    return names[0] if names else "Droid Sans Fallback"


def _box(ax, x, y, text, fill, width=None):
    ax.text(
        x, y, text, ha="center", va="center", fontsize=10.5,
        bbox={"boxstyle": "square,pad=0.5", "facecolor": fill, "edgecolor": COLOR_MAIN, "linewidth": 1.0},
    )


def _arrow(ax, start, end):
    ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.2, "color": COLOR_MAIN})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    font_name = _register_cjk_font()
    plt.rcParams["font.sans-serif"] = [font_name, "Droid Sans Fallback"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(9.6, 6.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8.2)
    ax.axis("off")

    # 第一层：共同数据基础
    _box(ax, 2.0, 7.5, "官方年度基准数据\n容量、同步峰值", COLOR_FILL_LIGHT)
    _box(ax, 6.0, 7.5, "站级设备与站址条件\n在役清单、接入间隔", COLOR_FILL_LIGHT)
    _box(ax, 10.0, 7.5, "措施成本库\n徐州工程与招标锚点", COLOR_FILL_LIGHT)

    # 第二层：共同物理校核
    _box(ax, 2.6, 5.8, "设备级正反向缺口校核", COLOR_FILL)
    _box(ax, 6.0, 5.8, "站级逐时情景筛查\n经验短时/中心/长时", COLOR_FILL)
    _box(ax, 9.4, 5.8, "网络容量压力筛查", COLOR_FILL)
    _arrow(ax, (2.0, 7.05), (2.4, 6.25))
    _arrow(ax, (6.0, 7.05), (6.0, 6.25))
    _arrow(ax, (10.0, 7.05), (9.6, 6.25))

    # 第三层：两类方案
    _box(ax, 3.2, 3.9, "弹性优化方案\n离散候选经济比选", COLOR_ACCENT_FILL)
    _box(ax, 8.8, 3.9, "严格优化方案\n归一约定起点（容载比 2.0）\n逐年上限校验（仅 110 kV）", COLOR_ACCENT_FILL)
    _arrow(ax, (3.6, 5.35), (3.3, 4.55))
    _arrow(ax, (8.4, 5.35), (8.7, 4.55))

    # 第四层：成本核算
    _box(ax, 6.0, 2.3, "累计年化成本（各自口径，不做跨口径比较）", COLOR_FILL)
    _arrow(ax, (3.9, 3.45), (5.0, 2.7))
    _arrow(ax, (8.1, 3.45), (7.0, 2.7))

    # 第五层：前沿扫描与推荐区间
    _box(ax, 6.0, 0.7, "容载比上限弹性扫描（1.5～3.0）→ 近优带∩场景可行∩功率因数敏感性\n→ 分片区推荐容载比区间与技术方案组合", COLOR_FILL_LIGHT)
    _arrow(ax, (6.0, 1.85), (6.0, 1.25))

    fig.tight_layout()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200)
    print(f"[decision-flow] 已生成 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
