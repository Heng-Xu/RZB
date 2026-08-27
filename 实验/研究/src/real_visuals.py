"""Generate auditable real_2025 recommendation visuals.

The matrix CSV/Markdown files remain the source of record.  This module only
reads the finalized run, keeps 110/35 kV separate, and writes a review package
under ``results/real_2025_visuals`` through the CLI wrapper.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


RUN_ID = "real-2025-contract-v2"
VOLTAGES = (110, 35)
MATRIX_FIELDS = (
    "region_id",
    "evidence_grade",
    "asset_scope_id",
    "capacity_base_mva",
    "positive_peak_base_mw",
    "reverse_peak_base_mw",
    "clr_model_base",
    "clr_official_reference",
    "pv_capacity_snapshot_mw",
    "C0_status",
    "C0_capex_wanyuan",
    "A_status",
    "A_expansion_action",
    "A_storage_modules",
    "A_capex_wanyuan",
    "A_eac_wanyuan_per_year",
    "A_clr_after",
    "B_status",
    "B_expansion_action",
    "B_storage_modules",
    "B_capex_wanyuan",
    "B_eac_wanyuan_per_year",
    "B_clr_after",
    "candidate_clr_range",
    "candidate_clr_min",
    "candidate_clr_max",
    "recommended_current_measure",
    "cost_sensitivity_range",
    "duration_sensitivity_range",
    "quality_notes",
)

VISUAL_FIELDS = (
    "region_id",
    "voltage_kv",
    "evidence_grade",
    "clr_official_reference",
    "candidate_clr_min",
    "candidate_clr_max",
    "C0_status",
    "A_status",
    "B_status",
    "A_clr_after",
    "B_clr_after",
    "A_eac_wanyuan_per_year",
    "B_eac_wanyuan_per_year",
    "A_expansion_action",
    "B_expansion_action",
    "A_storage_modules",
    "B_storage_modules",
    "recommended_current_measure",
    "quality_notes",
)

PALETTE = {
    "ink": "#263238",
    "muted": "#667085",
    "grid": "#D9E0E7",
    "range": "#B8C4D0",
    "baseline": "#263238",
    "a": "#D97706",
    "b": "#2563EB",
    "good": "#2F855A",
    "bad": "#B42318",
    "warn": "#B54708",
    "grade_b": "#3B82F6",
    "grade_c": "#F59E0B",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _setup_fonts() -> None:
    font_path = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    if font_path.is_file():
        try:
            fm.fontManager.addfont(str(font_path))
        except Exception:
            pass
    plt.rcParams["font.sans-serif"] = [
        "Noto Sans CJK SC",
        "Noto Sans CJK JP",
        "WenQuanYi Zen Hei",
        "SimHei",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def _validate_matrix(df: pd.DataFrame, voltage: int, source: Path) -> None:
    missing = sorted(set(MATRIX_FIELDS) - set(df.columns))
    if missing:
        raise ValueError(f"{source.name} missing required fields: {missing}")
    if len(df) != 8:
        raise ValueError(f"{source.name} must contain 8 region rows, got {len(df)}")
    if set(df["voltage_kv"].astype(int)) != {voltage}:
        raise ValueError(f"{source.name} mixes voltage levels")
    if not df["region_id"].astype(str).str.fullmatch(r"QX-[0-9]{5}").all():
        raise ValueError(f"{source.name} contains non-anonymized region IDs")
    if df.astype(str).apply(lambda s: s.str.contains("P50|P90", case=False, regex=True)).any().any():
        raise ValueError(f"{source.name} contains forbidden P50/P90 label")


def prepare_visual_data(run_dir: str | Path) -> pd.DataFrame:
    """Load the finalized matrices into one long review table without aggregation."""
    run_path = Path(run_dir)
    manifest_path = run_path / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("run_id") != RUN_ID or manifest.get("dataset") != "real_2025":
        raise ValueError("visuals require the finalized real_2025-contract-v2 run")

    frames: list[pd.DataFrame] = []
    for voltage in VOLTAGES:
        path = run_path / f"county_{voltage}_matrix.csv"
        if not path.is_file():
            raise FileNotFoundError(path)
        frame = pd.read_csv(path)
        _validate_matrix(frame, voltage, path)
        frame = frame.loc[:, list(VISUAL_FIELDS)].copy()
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    if len(data) != 16 or data.groupby("voltage_kv").size().to_dict() != {35: 8, 110: 8}:
        raise ValueError("visual data must keep 8 rows for each voltage level")
    return data


def _fmt_value(value: Any, digits: int = 2) -> str:
    if pd.isna(value):
        return "—"
    return f"{float(value):.{digits}f}"


def _fmt_percent(numerator: Any, denominator: Any) -> str:
    if pd.isna(numerator) or pd.isna(denominator) or float(denominator) <= 0:
        return "—"
    return f"{100.0 * float(numerator) / float(denominator):.1f}%"


def _measure_action(status: Any, action: Any, storage: Any) -> str:
    if status != "feasible":
        return f"不可行：{_short_reason(action)}"
    expansion = "无扩容" if pd.isna(action) or str(action) in {"", "none"} else str(action)
    storage_text = "—" if pd.isna(storage) else f"{int(float(storage))}模块"
    return f"{expansion}；储能{storage_text}"


def _selected_scheme(row: pd.Series) -> tuple[str | None, float | None]:
    """Select the minimum-EAC feasible A/B result, preferring B on ties."""
    candidates: list[tuple[float, int, str, float]] = []
    for scheme, tie_rank in (("A", 1), ("B", 0)):
        status = row[f"{scheme}_status"]
        eac = row[f"{scheme}_eac_wanyuan_per_year"]
        clr_after = row[f"{scheme}_clr_after"]
        if status == "feasible" and pd.notna(eac) and pd.notna(clr_after):
            candidates.append((float(eac), tie_rank, scheme, float(clr_after)))
    if not candidates:
        return None, None
    _, _, scheme, clr_after = min(candidates)
    return scheme, clr_after


def build_recommendation_table(run_dir: str | Path, voltage: int) -> pd.DataFrame:
    """Build the client-facing transposed indicator recommendation matrix.

    Columns are anonymized regions/high-voltage partitions and rows are the
    indicator/profile/cost/evidence fields.  The first result row is the
    current cost-minimizing feasible recommendation, not a future-year target.
    """
    run_path = Path(run_dir)
    source = run_path / f"county_{voltage}_matrix.csv"
    if not source.is_file():
        raise FileNotFoundError(source)
    frame = pd.read_csv(source)
    _validate_matrix(frame, voltage, source)
    frame = frame.sort_values("region_id").reset_index(drop=True)
    regions = frame["region_id"].astype(str).tolist()
    rows: list[dict[str, str]] = []

    def add(label: str, values: dict[str, str]) -> None:
        rows.append({"指标": label, **{region: values.get(region, "—") for region in regions}})

    rec: dict[str, str] = {}
    rec_scheme: dict[str, str] = {}
    for row in frame.itertuples(index=False):
        series = pd.Series(row._asdict())
        scheme, clr_after = _selected_scheme(series)
        if scheme is None or clr_after is None:
            rec[row.region_id] = "不可行"
            rec_scheme[row.region_id] = "A/B不可行"
        elif voltage == 35:
            rec[row.region_id] = f"辅助：{clr_after:.2f}（非唯一最优）"
            rec_scheme[row.region_id] = f"{scheme}（辅助）"
        else:
            rec[row.region_id] = f"{clr_after:.2f}"
            rec_scheme[row.region_id] = scheme
    add(f"推荐容载比 R_rec（EAC最小可行；{voltage} kV{'正式' if voltage == 110 else '辅助'}）", rec)
    add("推荐方案/状态", rec_scheme)
    add("现状正式 R0", {r.region_id: _fmt_value(r.clr_model_base) for r in frame.itertuples()})
    add("官方 R参考", {r.region_id: _fmt_value(r.clr_official_reference) for r in frame.itertuples()})
    add("光伏容量渗透率 PV/S0", {r.region_id: _fmt_percent(r.pv_capacity_snapshot_mw, r.capacity_base_mva) for r in frame.itertuples()})
    add("光伏功率比 PV/P+", {r.region_id: _fmt_percent(r.pv_capacity_snapshot_mw, r.positive_peak_base_mw) for r in frame.itertuples()})
    add("公用变容量 S0 (MVA)", {r.region_id: _fmt_value(r.capacity_base_mva, 1) for r in frame.itertuples()})
    add("正向峰值 P+ (MW)", {r.region_id: _fmt_value(r.positive_peak_base_mw, 2) for r in frame.itertuples()})
    add("反向峰值 P− (MW)", {r.region_id: _fmt_value(r.reverse_peak_base_mw, 2) for r in frame.itertuples()})
    add("A措施（扩容；储能）", {r.region_id: _measure_action(r.A_status, r.A_expansion_action, r.A_storage_modules) for r in frame.itertuples()})
    add("A EAC (万元/年)", {r.region_id: _fmt_value(r.A_eac_wanyuan_per_year, 1) for r in frame.itertuples()})
    add("B措施（扩容；储能）", {r.region_id: _measure_action(r.B_status, r.B_expansion_action, r.B_storage_modules) for r in frame.itertuples()})
    add("B EAC (万元/年)", {r.region_id: _fmt_value(r.B_eac_wanyuan_per_year, 1) for r in frame.itertuples()})
    add("当前经济措施", {r.region_id: str(r.recommended_current_measure) for r in frame.itertuples()})
    add("C0状态", {r.region_id: str(r.C0_status) for r in frame.itertuples()})
    add("证据等级", {r.region_id: str(r.evidence_grade) for r in frame.itertuples()})
    add("数据/可行性备注", {r.region_id: str(r.quality_notes) for r in frame.itertuples()})
    return pd.DataFrame(rows, columns=["指标", *regions])


def _write_recommendation_tables(run_dir: Path, output_dir: Path) -> list[str]:
    generated: list[str] = []
    for voltage in VOLTAGES:
        table = build_recommendation_table(run_dir, voltage)
        csv_name = f"recommendation_matrix_{voltage}kv.csv"
        md_name = f"recommendation_matrix_{voltage}kv.md"
        table.to_csv(output_dir / csv_name, index=False, encoding="utf-8-sig")
        title = f"# {voltage} kV 容载比推荐主表（2025现状）\n\n"
        note = (
            "> 甲方转置式指标矩阵：第一列为指标，后续列为脱敏片区；首行推荐值来自当前成本最小可行 A/B 方案。"
            "35 kV 仅为辅助技术需求，不代表唯一离散最优。\n\n"
        )
        (output_dir / md_name).write_text(title + note + table.to_markdown(index=False) + "\n", encoding="utf-8")
        generated.extend([csv_name, md_name])
    return generated


def _save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> list[str]:
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    paths: list[str] = []
    for suffix in ("png", "svg"):
        path = output_dir / f"{stem}.{suffix}"
        fig.savefig(path, dpi=180, bbox_inches="tight")
        paths.append(path.name)
    plt.close(fig)
    return paths


def _status_text(status: Any) -> str:
    if pd.isna(status):
        return "missing"
    return str(status)


def _short_reason(value: Any) -> str:
    """Keep the chart reason legible while preserving the matrix as exact source."""
    text = "" if pd.isna(value) else str(value)
    if "storage_required_but_no_available_connection_bay" in text:
        return "connection_bay_unavailable"
    if "missing_three_scenarios" in text:
        return "missing_three_scenarios"
    if "no_35kv_station_candidate" in text:
        return "no_35kv_station_candidate"
    if not text:
        return "see_matrix_quality_notes"
    return text[:44]


def _plot_clr_interval(data: pd.DataFrame, voltage: int, output_dir: Path) -> list[str]:
    subset = data[data["voltage_kv"] == voltage].sort_values("region_id").reset_index(drop=True)
    y = np.arange(len(subset))[::-1]
    xmin = min(float(subset["candidate_clr_min"].min()), float(subset["clr_official_reference"].min())) - 0.15
    xmax = max(float(subset["candidate_clr_max"].max()), float(subset["clr_official_reference"].max())) + 0.75
    fig, ax = plt.subplots(figsize=(13.5, 6.8))
    for i, row in subset.iterrows():
        yy = y[i]
        lo, hi = row["candidate_clr_min"], row["candidate_clr_max"]
        if pd.notna(lo) and pd.notna(hi):
            ax.plot([lo, hi], [yy, yy], color=PALETTE["range"], linewidth=8, solid_capstyle="round", zorder=1)
        baseline = row["clr_official_reference"]
        if pd.notna(baseline):
            ax.scatter(baseline, yy, s=58, color=PALETTE["baseline"], marker="o", zorder=4)
        if row["A_status"] == "feasible" and pd.notna(row["A_clr_after"]):
            ax.scatter(row["A_clr_after"], yy, s=70, color=PALETTE["a"], marker="D", zorder=5)
        if row["B_status"] == "feasible" and pd.notna(row["B_clr_after"]):
            ax.scatter(row["B_clr_after"], yy, s=72, color=PALETTE["b"], marker="s", zorder=5)
        if row["A_status"] != "feasible" or row["B_status"] != "feasible":
            text = f"A/B不可行：{_short_reason(row['recommended_current_measure'])}"
            ax.text(xmax - 0.02, yy + 0.12, text, ha="right", va="bottom", fontsize=8, color=PALETTE["bad"])

    labels = [f"{r.region_id}  [{r.evidence_grade}]" for r in subset.itertuples()]
    ax.set_yticks(y, labels)
    ax.set_xlim(xmin, xmax)
    ax.set_xlabel("容载比 CLR（无量纲；容量 / 干预前正向最大净负荷）")
    ax.set_ylabel("脱敏县区 / 证据等级")
    ax.grid(axis="x", color=PALETTE["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(f"{voltage} kV 现状与候选措施容载比区间", color=PALETTE["ink"], fontsize=15, pad=14)
    ax.text(
        0,
        1.01,
        "黑圆=现状参考；橙菱形=A后；蓝方形=B后；灰线=候选/经验情景范围；不可行方案不绘制伪造 CLR",
        transform=ax.transAxes,
        fontsize=9,
        color=PALETTE["muted"],
        va="bottom",
    )
    from matplotlib.lines import Line2D

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PALETTE["baseline"], label="现状参考", markersize=7),
        Line2D([0], [0], marker="D", color="none", markerfacecolor=PALETTE["a"], label="A方案后", markersize=7),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=PALETTE["b"], label="B方案后", markersize=7),
        Line2D([0], [0], color=PALETTE["range"], linewidth=8, label="候选/经验范围"),
    ]
    ax.legend(handles=handles, loc="upper right", frameon=False, ncol=2)
    fig.text(
        0.01,
        0.005,
        "数据范围：2025现状；运行：real-2025-contract-v2。35 kV图仅作辅助技术需求，不代表唯一离散最优。",
        fontsize=8,
        color=PALETTE["muted"],
    )
    return _save_figure(fig, output_dir, f"clr_interval_{voltage}kv")


def _plot_feasibility_eac(data: pd.DataFrame, voltage: int, output_dir: Path) -> list[str]:
    subset = data[data["voltage_kv"] == voltage].sort_values("region_id").reset_index(drop=True)
    y = np.arange(len(subset))[::-1]
    fig, ax = plt.subplots(figsize=(13.5, 6.8))
    for i, row in subset.iterrows():
        yy = y[i]
        for offset, scheme, color, marker in ((0.14, "A", PALETTE["a"], "D"), (-0.14, "B", PALETTE["b"], "s")):
            status = row[f"{scheme}_status"]
            value = row[f"{scheme}_eac_wanyuan_per_year"]
            ypos = yy + offset
            if status == "feasible" and pd.notna(value):
                ax.barh(ypos, value, height=0.22, color=color, alpha=0.82, zorder=2)
                ax.text(float(value), ypos, f"  {value:,.0f}", va="center", ha="left", fontsize=8, color=PALETTE["ink"])
            else:
                ax.scatter(0, ypos, marker="x", color=PALETTE["bad"], s=45, zorder=4)
                reason = _short_reason(row["recommended_current_measure"])
                ax.text(0.02, ypos, f"{scheme}: {status} ({reason})", transform=ax.get_yaxis_transform(), va="center", fontsize=8, color=PALETTE["bad"])
    finite = pd.concat([subset["A_eac_wanyuan_per_year"], subset["B_eac_wanyuan_per_year"]]).dropna()
    xmax = max(1.0, float(finite.max()) * 1.35) if len(finite) else 1.0
    ax.set_xlim(0, xmax)
    ax.set_yticks(y, [f"{r.region_id}  [{r.evidence_grade}]  C0:{r.C0_status}" for r in subset.itertuples()])
    ax.set_xlabel("等效年成本 EAC（万元/年；可行方案）")
    ax.set_ylabel("脱敏县区 / 证据等级 / C0状态")
    ax.grid(axis="x", color=PALETTE["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(f"{voltage} kV A/B方案可行性与等效年成本", color=PALETTE["ink"], fontsize=15, pad=14)
    ax.text(0, 1.01, "橙色=A；蓝色=B；叉号=不可行，不绘制成本伪值；C0成本恒为0但不合规时不作为推荐。", transform=ax.transAxes, fontsize=9, color=PALETTE["muted"], va="bottom")
    from matplotlib.patches import Patch

    ax.legend(handles=[Patch(facecolor=PALETTE["a"], label="A EAC"), Patch(facecolor=PALETTE["b"], label="B EAC")], loc="lower right", frameon=False)
    fig.text(0.01, 0.005, "来源：最终推荐矩阵；B方案只在真实候选和物理约束下求解。", fontsize=8, color=PALETTE["muted"])
    return _save_figure(fig, output_dir, f"feasibility_eac_{voltage}kv")


def _plot_evidence_quality(data: pd.DataFrame, run_dir: Path, output_dir: Path) -> list[str]:
    issues_path = run_dir / "data_quality_issues.csv"
    issues = pd.read_csv(issues_path) if issues_path.is_file() else pd.DataFrame(columns=["severity"])
    fig, (ax_grade, ax_issue) = plt.subplots(1, 2, figsize=(12.8, 5.6), gridspec_kw={"width_ratios": [1, 1.25]})
    grade = (
        data.groupby(["voltage_kv", "evidence_grade"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=[110, 35], columns=["A", "B", "C"], fill_value=0)
    )
    grade.plot(kind="bar", ax=ax_grade, color=[PALETTE["good"], PALETTE["grade_b"], PALETTE["grade_c"]], width=0.72)
    ax_grade.set_title("证据等级分布", color=PALETTE["ink"])
    ax_grade.set_xlabel("电压等级")
    ax_grade.set_ylabel("县区数")
    ax_grade.set_xticklabels(["110 kV", "35 kV"], rotation=0)
    ax_grade.grid(axis="y", color=PALETTE["grid"], linewidth=0.8)
    ax_grade.set_axisbelow(True)
    severity = issues["severity"].value_counts().reindex(["blocking_for_grade_A", "blocking_for_unique_optimum", "warning"], fill_value=0)
    ax_issue.barh(severity.index, severity.values, color=[PALETTE["bad"], PALETTE["warn"], PALETTE["grade_b"]])
    ax_issue.set_title("已登记数据问题数量", color=PALETTE["ink"])
    ax_issue.set_xlabel("问题条数")
    ax_issue.grid(axis="x", color=PALETTE["grid"], linewidth=0.8)
    ax_issue.set_axisbelow(True)
    for i, value in enumerate(severity.values):
        ax_issue.text(value + 0.05, i, str(value), va="center", fontsize=9)
    fig.suptitle("real_2025 证据与数据质量审查", fontsize=15, color=PALETTE["ink"])
    fig.text(0.01, 0.005, "C级表示映射、资产口径或候选存在未解决缺口；问题登记不等于整个模型无法运行。", fontsize=8, color=PALETTE["muted"])
    return _save_figure(fig, output_dir, "evidence_quality")


def _write_readme(output_dir: Path, data: pd.DataFrame) -> None:
    (output_dir / "README.md").write_text(
        "# real_2025 可视化审查包\n\n"
        "本目录由最终运行 `real-2025-contract-v2` 生成，图表只用于人工审查和解释，精确查值仍以 `county_110_matrix.csv`、`county_35_matrix.csv` 为准。\n\n"
        "## 文件\n\n"
        "- `clr_interval_110kv.*`、`clr_interval_35kv.*`：现状参考 CLR、A/B 后 CLR 和候选/经验范围。\n"
        "- `feasibility_eac_110kv.*`、`feasibility_eac_35kv.*`：A/B 可行性和 EAC；不可行不绘制伪成本。\n"
        "- `evidence_quality.*`：证据等级与数据问题数量。\n"
        "- `recommendation_matrix_110kv.*`、`recommendation_matrix_35kv.*`：甲方转置式指标推荐主表；第一列为指标，首行是当前推荐 R_rec。\n"
        "- `visual_data.csv`：图表使用的 16 行长表，110/35 kV 不聚合。\n"
        "- `visual_manifest.json`：输入/输出 SHA-256、运行 ID 和图表契约。\n\n"
        "## 口径\n\n"
        "CLR 使用同电压等级公用变容量除以干预前正向最大净负荷；C0/A/B 共用固定分母。35 kV 为辅助技术需求矩阵，不宣称唯一离散最优。N-1 和无阻抗网络筛查不进入本图包。\n\n"
        f"数据行数：{len(data)}（110 kV 8 行，35 kV 8 行）。\n",
        encoding="utf-8",
    )


def render_real_2025_visuals(run_dir: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """Render the review package and return the manifest payload."""
    run_path = Path(run_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    _setup_fonts()
    data = prepare_visual_data(run_path)
    generated: list[str] = []
    for voltage in VOLTAGES:
        generated.extend(_plot_clr_interval(data, voltage, out))
        generated.extend(_plot_feasibility_eac(data, voltage, out))
    generated.extend(_plot_evidence_quality(data, run_path, out))
    generated.extend(_write_recommendation_tables(run_path, out))
    data.to_csv(out / "visual_data.csv", index=False, encoding="utf-8-sig")
    generated.append("visual_data.csv")
    _write_readme(out, data)
    generated.append("README.md")

    input_names = ["county_110_matrix.csv", "county_35_matrix.csv", "manifest.json"]
    input_files = {name: {"sha256": _sha256(run_path / name)} for name in input_names}
    chart_contracts = {
        "clr_interval": {"family": "uncertainty_and_benchmark", "measure": "CLR", "voltage_separated": True},
        "feasibility_eac": {"family": "comparison_and_ranking", "measure": "EAC", "infeasible_without_fake_value": True},
        "evidence_quality": {"family": "comparison_and_ranking", "measure": "evidence_grade_and_issue_count", "voltage_separated": True},
        "recommendation_matrix": {
            "family": "tables_and_scorecards",
            "measure": "current_cost_minimizing_R_rec_and_profile",
            "voltage_separated": True,
            "transposed_indicator_matrix": True,
        },
    }
    manifest: dict[str, Any] = {
        "visualization_version": "1.1.0",
        "dataset": "real_2025",
        "run_id": RUN_ID,
        "voltage_levels": [35, 110],
        "row_count": int(len(data)),
        "input_files": input_files,
        "chart_contracts": chart_contracts,
        "output_files": {},
        "environment": {"required_conda_environment": "xuzhou110kv_clr"},
    }
    for rel in generated:
        path = out / rel
        manifest["output_files"][rel] = {"bytes": path.stat().st_size, "sha256": _sha256(path)}
    (out / "visual_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest
