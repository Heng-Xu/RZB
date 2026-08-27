#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 8 三表六图公共读取/输出工具(≤80行:只做 IO + 画图基础设施,业务口径留各脚本)。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
import yaml

from src.clr import compute_all
from src.io_loader import load_scenario
from src.links_sigma import build_linkset

ROOT = Path(__file__).resolve().parents[1]
WATERMARK = "合成数据,收资后替换"
PALETTE = {"blue": "#4878CF", "orange": "#EE854A", "green": "#6ACC64",
           "red": "#D65F5F", "gray": "#797979"}
# matplotlib 对 .ttc 只暴露首个 family(注册后名为 'Noto Sans CJK JP',与 fc-list
# 报告的 'SC' 同字重同字形,占位图可用);'SC' 留列表首位兼容未来独立 .otf 场景。
_CJK_TTC = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def setup_fonts() -> None:
    """注册中文字体 + 统一 rcParams(每个 fig_* 脚本开头调用一次)。"""
    try:
        fm.fontManager.addfont(_CJK_TTC)
    except Exception:
        pass
    plt.rcParams["font.sans-serif"] = [
        "Noto Sans CJK SC", "Noto Sans CJK JP", "WenQuanYi Zen Hei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def parse_args(desc: str) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=desc)
    p.add_argument("--run", default="synthetic-m1", help="results/runs/<run_id>")
    return p.parse_args()


def run_dir(run_id: str) -> Path:
    return ROOT / "results" / "runs" / run_id
def tables_dir() -> Path:
    d = ROOT / "tables"; d.mkdir(exist_ok=True); return d
def figures_dir() -> Path:
    d = ROOT / "figures"; d.mkdir(exist_ok=True); return d
def load_run(run_id: str) -> dict:
    """加载 Task 8 各脚本共需的数据源:场景对象+联络+CLR+双方案解+校核+参数。"""
    data = load_scenario(ROOT, track="synthetic")
    rd = run_dir(run_id)
    with open(ROOT / "params.yaml", encoding="utf-8") as f:
        params = yaml.safe_load(f)
    return dict(
        data=data, links=build_linkset(data), clr=compute_all(data),
        sol_a=json.loads((rd / "solution_A.json").read_text(encoding="utf-8")),
        sol_b=json.loads((rd / "solution_B.json").read_text(encoding="utf-8")),
        manifest=json.loads((rd / "manifest.json").read_text(encoding="utf-8")),
        verify_flow=pd.read_csv(rd / "verify_flow.csv"),
        verify_dlt=pd.read_csv(rd / "verify_dlt2041.csv"),
        params=params,
    )
def write_table(df: pd.DataFrame, name: str) -> None:
    """写 tables/<name>.csv + tables/<name>.md(index=False,表眉附水印注)。"""
    td = tables_dir()
    with open(td / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as f:
        f.write(f"# {WATERMARK}\n")
        df.to_csv(f, index=False)
    md = f"**{WATERMARK}**\n\n" + df.to_markdown(index=False) + "\n"
    (td / f"{name}.md").write_text(md, encoding="utf-8")
def save_fig(fig, name: str, data_df: pd.DataFrame | None = None) -> None:
    """存 figures/<name>.png(150dpi,右下角水印)+ 同名 .data.csv。"""
    fd = figures_dir()
    fig.text(0.99, 0.01, WATERMARK, ha="right", va="bottom",
              fontsize=7, color=PALETTE["gray"], alpha=0.75)
    fig.savefig(fd / f"{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    if data_df is not None:
        data_df.to_csv(fd / f"{name}.data.csv", index=False, encoding="utf-8-sig")
