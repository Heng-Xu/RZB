#!/usr/bin/env python3
"""绘制八片区「容载比上限—累计年化成本」弹性前沿图（报告第四章素材）。

用法：conda run -n xuzhou110kv_clr python scripts/plot_elasticity_frontier.py \
        --frontier results/runs/real-2021-2025-contract-v3/real_2021_2025-v3/elasticity_frontier.csv \
        --output 研究报告/初稿/图表/图4-1_弹性扫描前沿.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.v3_outputs import recommended_clr_interval  # noqa: E402


def _register_cjk_font() -> str:
    """注册系统中文字体；缺失时回退 Droid Sans Fallback，杜绝中文方块。"""
    for candidate in (
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ):
        try:
            font_manager.fontManager.addfont(candidate)
        except Exception:
            continue
    names = [f.name for f in font_manager.fontManager.ttflist if "CJK" in f.name]
    if names:
        return names[0]
    return "Droid Sans Fallback"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--frontier", required=True)
    parser.add_argument("--output", default="图4-1_弹性扫描前沿.png")
    args = parser.parse_args()

    font_name = _register_cjk_font()
    plt.rcParams["font.sans-serif"] = [font_name, "Droid Sans Fallback"]
    plt.rcParams["axes.unicode_minus"] = False

    frame = pd.read_csv(args.frontier, encoding="utf-8-sig")
    frame["rcap_num"] = pd.to_numeric(frame["rcap"], errors="coerce")
    fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=200)

    regions = sorted(frame["region_id"].unique())
    for index, region in enumerate(regions):
        sub = frame[(frame["region_id"].eq(region)) & frame["rcap_num"].notna() & frame["feasible"].astype(bool)]
        if sub.empty:
            continue
        sub = sub.sort_values("rcap_num")
        ax.plot(sub["rcap_num"], sub["cumulative_in_service_eac_wanyuan"] / 1e4,
                marker="o", markersize=3.5, linewidth=1.4, label=region)

    ax.axvline(2.0, color="grey", linestyle="--", linewidth=1.0)
    ax.annotate("R=2.0 严格优化方案的比较约束线", xy=(2.0, ax.get_ylim()[1]),
                xytext=(2.03, ax.get_ylim()[1] * 0.96), fontsize=9, color="grey")
    ax.set_xlabel("容载比上限 Rcap")
    ax.set_ylabel("累计年化成本（亿元，2022—2025 在役）")
    ax.set_title("八片区容载比上限—累计年化成本弹性前沿（110 kV，归一约定起点）")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.legend(ncol=4, fontsize=8)
    fig.tight_layout()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"[frontier] 已生成 {out}")

    # 附属：各片区推荐区间（近优带 5%）CSV
    rows = []
    for region in regions:
        rows.append(recommended_clr_interval(frame, region_id=region))
    interval_path = out.with_name(out.stem + "_推荐区间.csv")
    pd.DataFrame(rows).to_csv(interval_path, index=False, encoding="utf-8-sig")
    print(f"[frontier] 推荐区间 {interval_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
