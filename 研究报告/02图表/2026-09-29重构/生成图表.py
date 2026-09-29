"""从两区县经核查的 CSV 重绘报告图，不读取旧版图表。"""

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "实验/研究/rebuild_2026/outputs"
YEARS = (2022, 2023, 2024, 2025)
COLORS = {"rigid": "#B95B45", "elastic": "#236B89"}

FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_manager.fontManager.addfont(FONT_PATH)
plt.rcParams.update({
    "font.family": font_manager.FontProperties(fname=FONT_PATH).get_name(),
    "axes.unicode_minus": False,
    "font.size": 10,
    "figure.dpi": 180,
    "savefig.dpi": 220,
})


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def series(region, scheme):
    folder = "ordered_guide_pizhou_n1" if region == "邳州" else "ordered_guide_city_n1"
    return rows(OUTPUT / folder / f"{scheme}_years.csv")


def finish(name):
    plt.tight_layout(pad=1.5)
    plt.savefig(HERE / name, bbox_inches="tight")
    plt.close()


def annual_clr():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, region in zip(axes, ("邳州", "市区")):
        for scheme, label in (("rigid", "刚性"), ("elastic", "弹性")):
            data = series(region, scheme)
            ax.plot(YEARS, [float(x["clr"]) for x in data], marker="o", lw=2,
                    color=COLORS[scheme], label=label)
        ax.set_title(region)
        ax.set_xticks(YEARS)
        ax.grid(alpha=.25)
        ax.set_xlabel("规划年份")
    axes[0].set_ylabel("规划区域容载比（MVA/MW）")
    axes[1].legend(frameon=False)
    finish("图5-1_两区县逐年容载比.png")


def capacity_load():
    fig, axes = plt.subplots(2, 1, figsize=(10, 7))
    for ax, region in zip(axes, ("邳州", "市区")):
        rigid = series(region, "rigid")
        elastic = series(region, "elastic")
        ax.plot(YEARS, [float(x["capacity_mva"]) for x in rigid], "-o",
                color=COLORS["rigid"], label="刚性主变容量（MVA）")
        ax.plot(YEARS, [float(x["capacity_mva"]) for x in elastic], "-o",
                color=COLORS["elastic"], label="弹性主变容量（MVA）")
        second = ax.twinx()
        second.plot(YEARS, [float(x["net_peak_proxy_mw"]) for x in rigid], "--s",
                    color="#777777", label="区域降压负荷代理（MW）")
        ax.set_title(region)
        ax.set_xticks(YEARS)
        ax.grid(alpha=.2)
        ax.legend(loc="upper left", frameon=False)
        second.legend(loc="lower right", frameon=False)
    finish("图5-3_容量与负荷变化.png")


def cost():
    vals = []
    for region, folder in (("邳州", "ordered_guide_pizhou_n1"),
                           ("市区", "ordered_guide_city_n1")):
        data = {x["scheme"]: x for x in json.loads(
            (OUTPUT / folder / "summary.json").read_text(encoding="utf-8"))}
        vals.append((region, data["rigid"]["objective_npv_10k"],
                     data["elastic"]["objective_npv_10k"]))
    fig, ax = plt.subplots(figsize=(8, 4.4))
    x = np.arange(len(vals))
    for delta, key, label in ((-.18, 1, "刚性"), (.18, 2, "弹性")):
        heights = [v[key] for v in vals]
        bars = ax.bar(x + delta, heights, .34,
                      color=COLORS["rigid" if key == 1 else "elastic"], label=label)
        ax.bar_label(bars, labels=[f"{z:.0f}" for z in heights], padding=3)
    ax.set_xticks(x, [v[0] for v in vals])
    ax.set_ylabel("增量费用现值（万元）")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=.2)
    finish("图5-5_刚弹费用对比.png")


def actions():
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    for col, region in enumerate(("邳州", "市区")):
        for scheme, label in (("rigid", "刚性"), ("elastic", "弹性")):
            data = series(region, scheme)
            x = np.arange(4)
            ax = axes[0, col]
            ax.bar(x + (-.16 if scheme == "rigid" else .16),
                   [float(y["new_transformer_purchase_mva"]) for y in data],
                   .3, label=label, color=COLORS[scheme])
            ax = axes[1, col]
            ax.bar(x + (-.16 if scheme == "rigid" else .16),
                   [float(y["new_storage_energy_mwh"]) for y in data],
                   .3, label=label, color=COLORS[scheme])
        for row in range(2):
            axes[row, col].set_xticks(np.arange(4), YEARS)
            axes[row, col].grid(axis="y", alpha=.2)
        axes[0, col].set_title(region)
    axes[0, 0].set_ylabel("当年购置主变（MVA）")
    axes[1, 0].set_ylabel("当年新增储能（MWh）")
    axes[0, 1].legend(frameon=False)
    finish("图5-4_主变与储能年度措施.png")


def sensitivity():
    data = rows(OUTPUT / "ordered_guide_cost_sensitivity.csv")
    labels = [("baseline", 1, "基准"), ("line", .8, "线路价-20%"),
              ("line", 1.2, "线路价+20%"), ("storage", .8, "储能价-20%"),
              ("storage", 1.2, "储能价+20%")]
    vals = []
    for comp, scale, label in labels:
        group = [x for x in data if x["changed_component"] == comp
                 and abs(float(x["price_scale"]) - scale) < 1e-8]
        rigid = sum(float(x["lifecycle_npv_10k"]) for x in group if x["scheme"] == "rigid")
        elastic = sum(float(x["lifecycle_npv_10k"]) for x in group if x["scheme"] == "elastic")
        vals.append((label, rigid - elastic))
    fig, ax = plt.subplots(figsize=(9, 4.2))
    bars = ax.bar([x[0] for x in vals], [x[1] for x in vals], color="#236B89")
    ax.bar_label(bars, labels=[f"{x[1]:.0f}" for x in vals], padding=3)
    ax.set_ylabel("两区县合计弹性节约现值（万元）")
    ax.grid(axis="y", alpha=.2)
    finish("图5-6_两价格系数敏感性.png")


def transfer():
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.barh(["邳州六馈线样本", "市区研究假定"], [.28287889, .5], color=["#B95B45", "#236B89"])
    ax.set_xlim(0, .7)
    ax.set_xlabel("可转移负荷占比（静态估计或假定）")
    for i, value in enumerate((.28287889, .5)):
        ax.text(value + .01, i, f"{value:.1%}", va="center")
    ax.grid(axis="x", alpha=.2)
    finish("图5-2_既有转供比例依据.png")


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    annual_clr()
    capacity_load()
    cost()
    actions()
    sensitivity()
    transfer()
    print("已生成 6 张新图")


if __name__ == "__main__":
    main()
