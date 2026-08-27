#!/usr/bin/env python
"""生成研究报告第三章使用的可追溯数据摘要和图件。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd


YEARS = (2022, 2023, 2024, 2025)
REGION = "QX-00005"
VOLTAGE_KV = 110
FONT_CJK = "Noto Sans CJK SC"
FONT_CJK_FILE = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
COLOR_MAIN = "#1F4E79"
COLOR_SECONDARY = "#6E7B87"
COLOR_ACCENT = "#A64B45"
COLOR_GRID = "#D9D9D9"
COLOR_FILL = "#EEF3F7"
COLOR_FILL_LIGHT = "#F7F7F7"


def _parse_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_count(path: Path) -> int:
    return len(pd.read_csv(path, usecols=[0]))


def _configure_matplotlib() -> None:
    font_name = FONT_CJK
    if FONT_CJK_FILE.is_file():
        font_manager.fontManager.addfont(str(FONT_CJK_FILE))
        font_name = font_manager.FontProperties(fname=str(FONT_CJK_FILE)).get_name()
    plt.rcParams.update(
        {
            "font.family": font_name,
            "font.sans-serif": [font_name, FONT_CJK, "DejaVu Sans"],
            "axes.unicode_minus": False,
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10.5,
            "legend.fontsize": 8.5,
            "axes.edgecolor": "#404040",
            "axes.linewidth": 0.8,
            "grid.color": COLOR_GRID,
            "grid.linewidth": 0.7,
            "legend.frameon": False,
            "figure.dpi": 120,
            "savefig.dpi": 240,
        }
    )


def load_annual_reference(data_dir: Path) -> pd.DataFrame:
    path = data_dir / "annual_reference.csv"
    annual = pd.read_csv(path)
    required = {
        "year",
        "region_id",
        "voltage_kv",
        "official_capacity_mva",
        "official_positive_peak_mw",
        "official_clr",
        "source_ref",
        "source_version",
        "transformation",
        "scenario_id",
        "quality_flag",
        "source_sha256",
    }
    missing = required - set(annual.columns)
    if missing:
        raise ValueError(f"annual_reference.csv 缺少字段：{sorted(missing)}")
    if len(annual) != 80:
        raise ValueError(f"年度锚点应为 80 行，实际为 {len(annual)} 行")
    if annual[["year", "region_id", "voltage_kv"]].duplicated().any():
        raise ValueError("年度锚点存在重复的年份、片区和电压组合")
    expected = {2021, 2022, 2023, 2024, 2025}
    if set(annual["year"].astype(int)) != expected:
        raise ValueError("年度锚点年份不完整")
    if set(annual["voltage_kv"].astype(int)) != {35, 110}:
        raise ValueError("年度锚点电压等级不是 35 kV 与 110 kV")
    return annual.sort_values(["year", "voltage_kv", "region_id"], kind="stable").reset_index(drop=True)


def read_known_2024_outliers(data_dir: Path) -> pd.DataFrame:
    issues = pd.read_csv(data_dir / "timeseries_quality_issues.csv")
    outliers = issues[
        issues["year"].eq(2024)
        & issues["raw_value_mw"].notna()
        & issues["timestamp"].notna()
    ].copy()
    expected = {-7319.0, -6858.0, 16630.0}
    actual = set(outliers["raw_value_mw"].astype(float))
    if actual != expected or len(outliers) != 3:
        raise ValueError(f"2024 年已知异常值不完整：{sorted(actual)}")
    return outliers.sort_values(["timestamp", "source_column_1_based"], kind="stable")


def build_hourly_quality_summary(data_dir: Path) -> pd.DataFrame:
    outliers = read_known_2024_outliers(data_dir)
    records: list[dict[str, Any]] = []
    usecols = [
        "timestamp",
        "transformer_uid",
        "station_id",
        "net_load_mw",
        "point_quality_flag",
        "mapping_approval_status",
        "formal_use_allowed",
    ]
    for year in YEARS:
        path = data_dir / f"transformer_hourly_{year}.csv.gz"
        hourly = pd.read_csv(path, usecols=usecols)
        formal = hourly[_parse_bool(hourly["formal_use_allowed"])].copy()
        formal_transformers = int(formal["transformer_uid"].nunique())
        formal_stations = int(formal["station_id"].nunique())
        formal_timestamps = int(formal["timestamp"].nunique())
        if year == 2025 and (formal_transformers, formal_stations, formal_timestamps) != (40, 20, 8760):
            raise ValueError("2025 年正式逐时范围不是 20 座站、40 台主变、8760 点")
        evidence_use = (
            "formal_2025_operating_scope"
            if year == 2025
            else "context_only_historical_asset_scope_not_closed"
        )
        records.append(
            {
                "year": year,
                "source_row_count": len(hourly),
                "source_timestamp_count": int(hourly["timestamp"].nunique()),
                "source_transformer_count": int(hourly["transformer_uid"].nunique()),
                "approved_mapping_transformer_count": int(
                    hourly.loc[
                        hourly["mapping_approval_status"].astype(str).eq("approved"),
                        "transformer_uid",
                    ].nunique()
                ),
                "formal_transformer_count": formal_transformers,
                "formal_station_count": formal_stations,
                "formal_timestamp_count": formal_timestamps,
                "formal_nonnull_point_count": int(formal["net_load_mw"].notna().sum()),
                "isolated_linear_imputation_count": int(
                    hourly["point_quality_flag"].astype(str).eq("imputed_linear_isolated").sum()
                ),
                "known_isolated_outlier_count": int(outliers["year"].eq(year).sum()),
                "evidence_use": evidence_use,
                "source_file": path.name,
                "source_sha256": _sha256(path),
            }
        )
    return pd.DataFrame(records)


def build_typical_2025_profile(data_dir: Path, annual: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    usecols = [
        "timestamp",
        "transformer_uid",
        "region_id",
        "voltage_kv",
        "station_id",
        "net_load_mw",
        "formal_use_allowed",
    ]
    hourly = pd.read_csv(data_dir / "transformer_hourly_2025.csv.gz", usecols=usecols)
    formal = hourly[
        hourly["region_id"].astype(str).eq(REGION)
        & hourly["voltage_kv"].astype(int).eq(VOLTAGE_KV)
        & _parse_bool(hourly["formal_use_allowed"])
    ].copy()
    transformer_count = int(formal["transformer_uid"].nunique())
    station_count = int(formal["station_id"].nunique())
    if transformer_count != 40 or station_count != 20:
        raise ValueError("典型片区 2025 年正式逐时范围不闭合")
    formal["timestamp"] = pd.to_datetime(formal["timestamp"])
    profile = (
        formal.groupby("timestamp", as_index=False)["net_load_mw"]
        .sum(min_count=1)
        .sort_values("timestamp", kind="stable")
    )
    if len(profile) != 8760 or profile["net_load_mw"].isna().any():
        raise ValueError("典型片区 2025 年逐时聚合不是完整 8760 点")
    anchor = annual[
        annual["year"].eq(2025)
        & annual["region_id"].astype(str).eq(REGION)
        & annual["voltage_kv"].astype(int).eq(VOLTAGE_KV)
    ]
    if len(anchor) != 1:
        raise ValueError("典型片区 2025 年 110 kV 官方锚点不唯一")
    official_peak = float(anchor.iloc[0]["official_positive_peak_mw"])
    raw_peak = float(profile["net_load_mw"].max())
    if raw_peak <= 0:
        raise ValueError("典型片区逐时正向峰值无效")
    scale = official_peak / raw_peak
    profile["net_load_mw"] = profile["net_load_mw"].astype(float) * scale
    profile["direction"] = np.select(
        [profile["net_load_mw"].gt(0), profile["net_load_mw"].lt(0)],
        ["positive_import", "reverse_export"],
        default="zero",
    )
    signs = np.sign(profile["net_load_mw"].to_numpy(dtype=float))
    nonzero = signs[signs != 0]
    transitions = int((nonzero[1:] != nonzero[:-1]).sum()) if len(nonzero) > 1 else 0
    reverse_min = float(profile["net_load_mw"].min())
    low_threshold = 0.2 * official_peak
    stats = {
        "year": 2025,
        "region_id": REGION,
        "voltage_kv": VOLTAGE_KV,
        "transformer_count": transformer_count,
        "station_count": station_count,
        "timestamp_count": len(profile),
        "raw_positive_peak_mw": raw_peak,
        "official_anchor_scale": scale,
        "positive_peak_mw": float(profile["net_load_mw"].max()),
        "positive_peak_timestamp": profile.loc[profile["net_load_mw"].idxmax(), "timestamp"].isoformat(),
        "reverse_peak_mw": max(-reverse_min, 0.0),
        "reverse_peak_timestamp": profile.loc[profile["net_load_mw"].idxmin(), "timestamp"].isoformat(),
        "positive_hours": int(profile["net_load_mw"].gt(0).sum()),
        "low_positive_hours": int(
            (profile["net_load_mw"].gt(0) & profile["net_load_mw"].le(low_threshold)).sum()
        ),
        "low_positive_threshold_mw": low_threshold,
        "reverse_hours": int(profile["net_load_mw"].lt(0).sum()),
        "direction_transition_count": transitions,
        "evidence_level": "EVIDENCE_A",
        "transformation": "sum same-voltage formal devices by timestamp, then scale to official positive peak anchor",
    }
    return profile, stats


def _save_figure(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)


def plot_research_route(path: Path) -> None:
    labels = [
        "1  规范与数据准备",
        "2  运行特征识别",
        "3  正反向约束校核",
        "4  多年度路径比较",
        "5  敏感性与案例验证",
        "6  差异化规划建议",
    ]
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.set_xlim(0, 9.2)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    positions = [(1.5, 3.8), (4.6, 3.8), (7.7, 3.8), (7.7, 1.45), (4.6, 1.45), (1.5, 1.45)]
    for x, y, label in zip((p[0] for p in positions), (p[1] for p in positions), labels):
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            fontsize=11.2,
            bbox={"boxstyle": "square,pad=0.65", "facecolor": COLOR_FILL, "edgecolor": COLOR_MAIN, "linewidth": 1.1},
        )
    for start, end in [
        ((2.45, 3.8), (3.62, 3.8)),
        ((5.55, 3.8), (6.72, 3.8)),
        ((7.7, 3.25), (7.7, 2.0)),
        ((6.72, 1.45), (5.55, 1.45)),
        ((3.62, 1.45), (2.45, 1.45)),
    ]:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "color": COLOR_MAIN, "lw": 1.35})
    _save_figure(fig, path)


def plot_annual_clr(annual: pd.DataFrame, path: Path) -> None:
    data = annual[annual["voltage_kv"].eq(110)].copy()
    fig, axes = plt.subplots(2, 4, figsize=(9.2, 5.2), sharex=True, sharey=True)
    regions = list(data["region_id"].drop_duplicates().sort_values())
    y_min = min(1.8, float(data["official_clr"].min()) - 0.1)
    y_max = float(data["official_clr"].max()) + 0.15
    for ax, region in zip(axes.flat, regions):
        group = data[data["region_id"].eq(region)]
        ax.plot(group["year"], group["official_clr"], marker="o", ms=3.8, lw=1.45, color=COLOR_MAIN)
        ax.axhline(2.0, color=COLOR_ACCENT, lw=0.9, ls="--")
        ax.set_title(region, fontsize=9.5, pad=3)
        ax.set_ylim(y_min, y_max)
        ax.set_xticks([2021, 2023, 2025])
        ax.grid(axis="y")
    fig.supylabel("110 kV 容载比", x=0.01, fontsize=10.5)
    fig.supxlabel("年度", y=0.01, fontsize=10.5)
    fig.text(0.98, 0.01, "虚线：R=2.0", ha="right", va="bottom", fontsize=8.5, color=COLOR_ACCENT)
    fig.tight_layout(rect=(0.025, 0.035, 1, 1), w_pad=0.7, h_pad=0.8)
    _save_figure(fig, path)


def plot_typical_annual(annual: pd.DataFrame, path: Path) -> None:
    data = annual[
        annual["region_id"].astype(str).eq(REGION)
        & annual["voltage_kv"].astype(int).eq(VOLTAGE_KV)
    ].copy()
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 5.8), sharex=True, gridspec_kw={"height_ratios": [1.25, 1]})
    axes[0].plot(data["year"], data["official_capacity_mva"], marker="o", lw=1.6, color=COLOR_MAIN, label="公用变容量（MVA）")
    axes[0].plot(data["year"], data["official_positive_peak_mw"], marker="s", lw=1.6, color=COLOR_ACCENT, label="同步正向峰值（MW）")
    axes[0].set_ylabel("容量 / 功率")
    axes[0].grid(axis="y")
    axes[0].legend(loc="upper center", ncol=2)
    axes[1].bar(data["year"], data["official_clr"], width=0.56, color="#8FA9BC", edgecolor=COLOR_MAIN, linewidth=0.6)
    axes[1].axhline(2.0, color=COLOR_ACCENT, lw=1.0, ls="--")
    axes[1].set_ylabel("容载比")
    axes[1].set_xlabel("年度")
    axes[1].set_xticks(data["year"])
    axes[1].grid(axis="y")
    for x, value in zip(data["year"], data["official_clr"]):
        axes[1].text(x, value + 0.04, f"{value:.2f}", ha="center", fontsize=9)
    fig.tight_layout()
    _save_figure(fig, path)


def plot_duration_curve(profile: pd.DataFrame, path: Path) -> None:
    values = np.sort(profile["net_load_mw"].to_numpy(dtype=float))[::-1]
    hours = np.arange(1, len(values) + 1)
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    ax.plot(hours, values, color=COLOR_MAIN, lw=1.5)
    ax.fill_between(hours, values, 0, where=values >= 0, color="#BFCFDC", alpha=0.65, label="正向供电")
    ax.fill_between(hours, values, 0, where=values < 0, color="#D8B4B0", alpha=0.7, label="反向送电")
    ax.axhline(0, color="#333333", lw=0.9)
    ax.set_xlabel("全年累计小时（按净负荷由高到低排序）")
    ax.set_ylabel("同步净负荷（MW）")
    ax.grid(axis="y")
    ax.legend(loc="upper right")
    _save_figure(fig, path)


def plot_typical_days(profile: pd.DataFrame, path: Path) -> None:
    data = profile.copy()
    data["date"] = data["timestamp"].dt.date
    positive_date = data.loc[data["net_load_mw"].idxmax(), "date"]
    reverse_date = data.loc[data["net_load_mw"].idxmin(), "date"]
    fig, axes = plt.subplots(2, 1, figsize=(9.2, 5.8), sharex=True)
    for ax, date_value, title in [
        (axes[0], positive_date, "正向峰值日"),
        (axes[1], reverse_date, "反向峰值日"),
    ]:
        day = data[data["date"].eq(date_value)].copy()
        hour = day["timestamp"].dt.hour
        net = day["net_load_mw"].to_numpy(dtype=float)
        ax.plot(hour, net, marker="o", ms=3.1, color=COLOR_MAIN, lw=1.45)
        ax.fill_between(hour, net, 0, where=net >= 0, color="#BFCFDC", alpha=0.65)
        ax.fill_between(hour, net, 0, where=net < 0, color="#D8B4B0", alpha=0.7)
        ax.axhline(0, color="#333333", lw=0.8)
        ax.set_ylabel("净负荷（MW）")
        ax.set_title(f"{title}：{date_value}", loc="left", fontsize=11)
        ax.grid(axis="y")
    axes[1].set_xlabel("时刻")
    axes[1].set_xticks(range(0, 24, 2))
    fig.tight_layout()
    _save_figure(fig, path)


def _diagram_box(ax: plt.Axes, x: float, y: float, text: str, color: str, width: float = 2.2) -> None:
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=10.5,
        bbox={"boxstyle": "square,pad=0.5", "facecolor": color, "edgecolor": COLOR_MAIN, "linewidth": 1.0},
    )


def plot_indicator_mechanism(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis("off")
    _diagram_box(ax, 1.5, 4.6, "源荷比\n装机容量关系", COLOR_FILL_LIGHT)
    _diagram_box(ax, 1.5, 1.5, "电量渗透率\n年度电量关系", COLOR_FILL_LIGHT)
    _diagram_box(ax, 5.1, 3.05, "逐时净负荷\n方向、峰值与持续时间", COLOR_FILL)
    _diagram_box(ax, 8.8, 4.5, "正式容载比\n正向容量配置", COLOR_FILL_LIGHT)
    _diagram_box(ax, 8.8, 1.6, "反向承载力\n设备级反向约束", COLOR_FILL_LIGHT)
    for start, end in [((2.55, 4.5), (4.0, 3.5)), ((2.55, 1.7), (4.0, 2.6)), ((6.25, 3.45), (7.65, 4.25)), ((6.25, 2.65), (7.65, 1.85))]:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.3, "color": COLOR_MAIN})
    _save_figure(fig, path)


def plot_database_flow(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.4)
    ax.axis("off")
    boxes = [
        (1.5, 4.4, "源数据\n年度、设备、逐时、光伏", COLOR_FILL_LIGHT),
        (5.0, 4.4, "对象与口径标准化\n编码、单位、电压层级", COLOR_FILL),
        (8.5, 4.4, "质量门禁\n映射、白名单、异常隔离", COLOR_FILL_LIGHT),
        (1.0, 1.7, "基础实体层\n片区、站点、设备", COLOR_FILL_LIGHT),
        (3.0, 1.7, "年度状态层\n容量、峰值、容载比", COLOR_FILL_LIGHT),
        (5.0, 1.7, "时序运行层\n净负荷、方向、质量", COLOR_FILL_LIGHT),
        (7.0, 1.7, "场景指标层\n正反向缺口", COLOR_FILL_LIGHT),
        (9.0, 1.7, "证据追溯层\n来源、转换、质量", COLOR_FILL_LIGHT),
    ]
    for x, y, label, color in boxes:
        _diagram_box(ax, x, y, label, color)
    arrows = [
        ((2.45, 4.4), (3.75, 4.4)),
        ((6.25, 4.4), (7.45, 4.4)),
        ((8.5, 3.8), (8.5, 2.45)),
        ((2.0, 1.7), (2.35, 1.7)),
        ((4.0, 1.7), (4.35, 1.7)),
        ((6.0, 1.7), (6.35, 1.7)),
        ((8.0, 1.7), (8.35, 1.7)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.2, "color": COLOR_MAIN})
    _save_figure(fig, path)


def write_database_lineage(data_dir: Path, output: Path, quality: pd.DataFrame) -> None:
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    pv = pd.read_csv(data_dir / "station_pv_snapshot.csv", usecols=["snapshot_min", "snapshot_max", "quality_flag"])
    counts = {
        "片区年度锚点": _read_count(data_dir / "annual_reference.csv"),
        "站点主表": _read_count(data_dir / "station_master.csv"),
        "主变主表": _read_count(data_dir / "transformer_master.csv"),
        "年度资产白名单": _read_count(data_dir / "annual_asset_whitelist.csv"),
        "110 kV 线路": _read_count(data_dir / "network_lines_110kv.csv"),
        "离散扩建候选": _read_count(data_dir / "expansion_candidates.csv"),
        "实际资产动作": _read_count(data_dir / "actual_asset_actions_2021_2025.csv"),
        "光伏 8760 曲线": _read_count(data_dir / "pv_profile_2025.csv"),
        "数据质量台账": _read_count(data_dir / "data_quality_issues.csv"),
    }
    lines = [
        "# 第三章数据库规模与血缘",
        "",
        "## 数据规模",
        "",
        "| 数据主题 | 记录数 |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {count} |" for name, count in counts.items())
    lines.extend(
        [
            "",
            "## 逐时证据范围",
            "",
            "| 年度 | 源记录数 | 时刻数 | 正式主变数 | 正式用途 |",
            "|---:|---:|---:|---:|---|",
        ]
    )
    for row in quality.itertuples(index=False):
        lines.append(
            f"| {row.year} | {row.source_row_count} | {row.source_timestamp_count} | "
            f"{row.formal_transformer_count} | {row.evidence_use} |"
        )
    lines.extend(
        [
            "",
            "2025 年 QX-00005 的 110 kV 运行口径为 20 座站、40 台主变，可用于正式逐时分析。2022—2024 年逐时文件保留作数据完整性和异常审计，因历史设备范围尚未闭合，本报告不据此形成正式设备级多工况结论。",
            "",
            "## 光伏数据口径",
            "",
            f"站级光伏数据的时间范围为 {pv['snapshot_min'].min()} 至 {pv['snapshot_max'].max()}，属于 2026 年快照。与 2025 年及以前负荷结合时，仅作为跨年背景和场景信息，不改写为历史年度实测装机。",
            "",
            "## 数据血缘",
            "",
            f"- 数据集标识：`{manifest['dataset_id']}`；契约版本：`{manifest['contract_version']}`。",
            f"- 数据集指纹：`{manifest['dataset_fingerprint']}`。",
            "- 派生摘要保留源文件 SHA-256；年度锚点、逐时数据、质量台账和光伏快照均可回查到 v3 manifest。",
            "- 110 kV 与 35 kV 分表统计，正式容载比采用同步正向最大净负荷，反向峰值与反向承载力单列。",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def build_report_assets(data_dir: Path | str, summary_dir: Path | str, figure_dir: Path | str) -> dict[str, Any]:
    data_dir = Path(data_dir).resolve()
    summary_dir = Path(summary_dir).resolve()
    figure_dir = Path(figure_dir).resolve()
    summary_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    _configure_matplotlib()

    annual = load_annual_reference(data_dir)
    annual_out = summary_dir / "第三章_年度片区指标.csv"
    annual.to_csv(annual_out, index=False, encoding="utf-8-sig", float_format="%.8g")

    quality = build_hourly_quality_summary(data_dir)
    quality_out = summary_dir / "第三章_逐时数据质量.csv"
    quality.to_csv(quality_out, index=False, encoding="utf-8-sig")

    profile, stats = build_typical_2025_profile(data_dir, annual)
    profile_out = summary_dir / "第三章_典型片区2025逐时聚合.csv.gz"
    profile.to_csv(profile_out, index=False, compression="gzip", encoding="utf-8", float_format="%.8f")
    stats_out = summary_dir / "第三章_典型片区多工况统计.csv"
    pd.DataFrame([stats]).to_csv(stats_out, index=False, encoding="utf-8-sig", float_format="%.8f")

    lineage_out = summary_dir / "第三章_数据库规模与血缘.md"
    write_database_lineage(data_dir, lineage_out, quality)

    plot_research_route(figure_dir / "图1-1_研究技术路线.png")
    plot_annual_clr(annual, figure_dir / "图3-1_八片区110kV容载比年度变化.png")
    plot_typical_annual(annual, figure_dir / "图3-2_典型片区容量同步峰值与容载比变化.png")
    plot_duration_curve(profile, figure_dir / "图3-3_典型年度净负荷持续曲线.png")
    plot_typical_days(profile, figure_dir / "图3-4_典型日正反向运行曲线.png")
    plot_indicator_mechanism(figure_dir / "图3-5_指标作用机制示意图.png")
    plot_database_flow(figure_dir / "图3-6_数据库构建流程.png")

    outliers = read_known_2024_outliers(data_dir)
    used_inputs = [
        "annual_reference.csv",
        "annual_asset_whitelist.csv",
        "asset_scope_summary.csv",
        "timeseries_quality_issues.csv",
        "data_quality_issues.csv",
        "station_pv_snapshot.csv",
        "manifest.json",
        *(f"transformer_hourly_{year}.csv.gz" for year in YEARS),
    ]
    output_paths = [annual_out, quality_out, profile_out, stats_out, lineage_out, *sorted(figure_dir.glob("*.png"))]
    report_manifest = {
        "dataset_id": "real_2021_2025",
        "generated_for": "research_report_chapters_1_to_3",
        "input_files": {
            name: {"sha256": _sha256(data_dir / name), "bytes": (data_dir / name).stat().st_size}
            for name in used_inputs
        },
        "quality_gate": {
            "formal_multicondition_years": [2025],
            "formal_region_id": REGION,
            "formal_voltage_kv": VOLTAGE_KV,
            "formal_transformer_count": 40,
            "formal_station_count": 20,
            "known_2024_anomaly_values_mw": sorted(outliers["raw_value_mw"].astype(float).tolist()),
            "pv_snapshot_role": "2026_cross_year_context_only",
        },
        "output_files": {
            str(path.relative_to(summary_dir.parent)): {"sha256": _sha256(path), "bytes": path.stat().st_size}
            for path in output_paths
        },
    }
    manifest_out = summary_dir / "第三章_数据摘要_manifest.json"
    manifest_out.write_text(json.dumps(report_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "summary_dir": str(summary_dir),
        "figure_dir": str(figure_dir),
        "formal_multicondition_years": [2025],
        "manifest": str(manifest_out),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--summary-dir", type=Path, required=True)
    parser.add_argument("--figure-dir", type=Path, required=True)
    args = parser.parse_args()
    result = build_report_assets(args.data_dir, args.summary_dir, args.figure_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
