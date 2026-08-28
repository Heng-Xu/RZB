#!/usr/bin/env python3
"""为 v3.2 冻结结果生成少量可复核的报告支撑图。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib import font_manager  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
REGIONS = ["QX-00001", "QX-00005"]


def _register_cjk_font() -> str:
    candidates = (
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    )
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            font_manager.fontManager.addfont(str(path))
            return font_manager.FontProperties(fname=str(path)).get_name()
    return "DejaVu Sans"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=240, bbox_inches="tight")
    plt.close(fig)


def _plot_rcap_cost(formal: Path, out: Path, font_name: str) -> Path:
    frontier = pd.read_csv(formal / "elasticity_frontier_v32_actual_coarse.csv")
    frontier["rcap_x"] = pd.to_numeric(frontier["rcap_numeric"], errors="coerce")
    frontier["cost"] = pd.to_numeric(frontier["cumulative_in_service_eac_wanyuan"], errors="coerce")
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for region in REGIONS:
        subset = frontier[
            frontier["region_id"].eq(region)
            & frontier["feasible"].astype(str).str.lower().eq("true")
            & frontier["rcap_x"].notna()
            & frontier["cost"].notna()
        ].sort_values("rcap_x")
        ax.plot(subset["rcap_x"], subset["cost"], marker="o", ms=3.5, lw=1.5, label=region)
    ax.set_xlabel("规划控制参数 Rcap")
    ax.set_ylabel("2022—2025 年累计年化成本（万元）")
    ax.set_title("Rcap—累计年化成本前沿（实际资产共同起点）")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    path = out / "rcap_cost_frontier.png"
    _save(fig, path)
    return path


def _plot_capacity_storage(formal: Path, out: Path, font_name: str) -> Path:
    frontier = pd.read_csv(formal / "elasticity_frontier_v32_actual_coarse.csv")
    frontier["rcap_x"] = pd.to_numeric(frontier["rcap_numeric"], errors="coerce")
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 6.2), sharex=True)
    for region in REGIONS:
        subset = frontier[
            frontier["region_id"].eq(region)
            & frontier["feasible"].astype(str).str.lower().eq("true")
            & frontier["rcap_x"].notna()
        ].sort_values("rcap_x")
        axes[0].step(subset["rcap_x"], subset["capacity_action_delta_mva"], where="post", label=region)
        axes[1].step(subset["rcap_x"], subset["storage_modules"], where="post", label=region)
    axes[0].set_ylabel("新增容量（MVA）")
    axes[1].set_ylabel("储能柜数（柜）")
    axes[1].set_xlabel("规划控制参数 Rcap")
    axes[0].set_title("Rcap 对新增容量与储能配置的影响")
    for axis in axes:
        axis.grid(axis="y", alpha=0.25)
    axes[0].legend(frameon=False, ncol=2)
    fig.tight_layout()
    path = out / "rcap_capacity_storage.png"
    _save(fig, path)
    return path


def _plot_soc(formal: Path, out: Path, font_name: str) -> Path:
    curve = pd.read_csv(formal / "baseline/qx00005_soc/qx00005_continuous_soc_8760.csv.gz")
    curve["hour_index"] = pd.to_numeric(curve["hour_index"], errors="coerce")
    curve["soc_after_mwh"] = pd.to_numeric(curve["soc_after_mwh"], errors="coerce")
    aggregate = curve.groupby(["path_id", "hour_index"], as_index=False)["soc_after_mwh"].sum()
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    labels = {
        "PATH_OPT_CLR_UNBOUNDED": "不限制容载比方案",
        "PATH_OPT_CLR_LE_2": "严格 Rcap=2.0 方案",
    }
    for path_id, group in aggregate.groupby("path_id", sort=True):
        ax.plot(group["hour_index"], group["soc_after_mwh"], lw=0.65, label=labels.get(path_id, path_id))
    ax.set_xlabel("2025 年连续小时序号（h）")
    ax.set_ylabel("QX-00005 储能总 SOC（MWh）")
    ax.set_title("QX-00005 110 kV 储能 8760 h 连续 SOC 校核")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    path = out / "qx00005_soc_8760.png"
    _save(fig, path)
    return path


def _plot_gaps(formal: Path, out: Path, font_name: str) -> Path:
    frame = pd.read_csv(formal / "formal_matrix_110kv.csv").set_index("region_id")
    positive = pd.to_numeric(frame["positive_capacity_gap_mw"], errors="coerce").fillna(0.0)
    reverse = pd.to_numeric(frame["reverse_hosting_gap_mw"], errors="coerce").fillna(0.0)
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    x = range(len(frame))
    ax.bar(x, positive, label="正向容量缺口")
    ax.bar(x, reverse, bottom=positive, label="反向承载缺口")
    ax.set_xticks(list(x), frame.index.tolist())
    ax.set_ylabel("设备级缺口（MW）")
    ax.set_title("110 kV 物理缺口与措施触发原因")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    path = out / "constraint_gap_summary.png"
    _save(fig, path)
    return path


def _plot_10kv_case_boundary(out: Path, font_name: str) -> Path:
    """绘制六馈线局部案例的代号关系示意，不表示完整物理拓扑或潮流。"""
    left = {
        "PZXL-00099": 5.0,
        "PZXL-00097": 3.0,
        "PZXL-00092": 1.0,
    }
    right = {
        "PZXL-00154": 5.0,
        "PZXL-00161": 3.0,
        "PZXL-00173": 1.0,
    }
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.set_xlim(-0.25, 2.25)
    ax.set_ylim(0.0, 6.2)
    ax.axis("off")

    station_style = {
        "boxstyle": "round,pad=0.35",
        "facecolor": "#e8eef7",
        "edgecolor": "#345a86",
        "linewidth": 1.2,
    }
    feeder_style = {
        "boxstyle": "round,pad=0.25",
        "facecolor": "#f7f7f7",
        "edgecolor": "#707070",
        "linewidth": 1.0,
    }
    ax.text(0.0, 3.0, "BDZ-00027", ha="center", va="center", bbox=station_style, fontsize=10)
    ax.text(2.0, 3.0, "BDZ-00048", ha="center", va="center", bbox=station_style, fontsize=10)
    for feeder, y in left.items():
        ax.plot([0.23, 0.68], [3.0, y], color="#a0a0a0", lw=1.0, zorder=1)
        ax.text(0.72, y, feeder, ha="left", va="center", bbox=feeder_style, fontsize=9, zorder=3)
    for feeder, y in right.items():
        ax.plot([1.77, 1.32], [3.0, y], color="#a0a0a0", lw=1.0, zorder=1)
        ax.text(1.28, y, feeder, ha="right", va="center", bbox=feeder_style, fontsize=9, zorder=3)

    connections = [
        ("TIE-001", left["PZXL-00099"], right["PZXL-00154"], "#b24b4b", "不形成定量结论"),
        ("TIE-002", left["PZXL-00092"], right["PZXL-00161"], "#2f7d4a", "4.75 / 1.75 MW"),
        ("TIE-003", left["PZXL-00097"], right["PZXL-00161"], "#2f7d4a", "3.25 / 1.75 MW"),
        ("NEW-TIE-01", left["PZXL-00099"], right["PZXL-00154"], "#8867a8", "[4.0, 8.0] MW 包络"),
    ]
    for label, y_left, y_right, color, note in connections:
        linestyle = "--" if label != "NEW-TIE-01" else ":"
        ax.plot([0.72, 1.28], [y_left, y_right], color=color, lw=1.8, linestyle=linestyle, zorder=2)
        y_label = (y_left + y_right) / 2 + (0.18 if label == "NEW-TIE-01" else 0.0)
        ax.text(1.0, y_label, f"{label}\n{note}", ha="center", va="center", fontsize=8.2, color=color,
                bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "alpha": 0.9}, zorder=4)

    ax.text(
        1.0,
        0.28,
        "六馈线局部案例边界示意：仅表达站—馈线—联络关系；不代表完整拓扑、同步断面或 AC 潮流结果",
        ha="center",
        va="center",
        fontsize=8.5,
        color="#555555",
    )
    ax.set_title("10 kV 局部联络案例关系示意（代号）", fontsize=12, pad=10)
    fig.tight_layout()
    path = Path(out) / "10kv_local_case_boundary.png"
    _save(fig, path)
    return path


def build_figures(formal_dir: Path) -> dict[str, object]:
    formal = Path(formal_dir).resolve()
    if not (formal / "manifest.json").is_file():
        raise FileNotFoundError(f"v3.2 formal manifest is missing: {formal}")
    font_name = _register_cjk_font()
    plt.rcParams["font.family"] = font_name
    plt.rcParams["axes.unicode_minus"] = False
    out = formal / "figures"
    paths = [
        _plot_rcap_cost(formal, out, font_name),
        _plot_capacity_storage(formal, out, font_name),
        _plot_soc(formal, out, font_name),
        _plot_gaps(formal, out, font_name),
        _plot_10kv_case_boundary(out, font_name),
    ]
    manifest = {
        "model_version": "3.2.0",
        "formal_result_dir": str(formal.relative_to(ROOT.parent.parent)) if formal.is_relative_to(ROOT.parent.parent) else str(formal),
        "font": font_name,
        "figures": {
            str(path.relative_to(formal)): {"sha256": _sha256(path), "bytes": path.stat().st_size}
            for path in paths
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formal-dir", type=Path, default=ROOT / "results/runs/real-2021-2025-v32-frozen")
    args = parser.parse_args()
    print(json.dumps(build_figures(args.formal_dir), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
