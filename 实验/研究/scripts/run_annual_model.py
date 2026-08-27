#!/usr/bin/env python
"""生成 2021--2025 年度 C0/A/B 诊断矩阵和最终 Word 推荐表。"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.annual_modeling import (
    ACTION_MODES,
    ANNUAL_YEARS,
    aggregate_annual_matrix,
    build_final_recommendation_interval,
    load_historical_reference,
    run_annual_year,
)
from src.real_pipeline import require_formal_approval


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fmt(value: object) -> str:
    if pd.isna(value):
        return "—"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _word_value(value: object, field: str) -> str:
    """把机器代码转换成甲方主表可读的中文短值。"""
    if pd.isna(value):
        return "—"
    schemes = {
        "SCHEME_C0": "现状不干预方案",
        "SCHEME_A": "存量继承、增量 2.0 约束方案",
        "SCHEME_B": "扩容储能综合优化方案",
        "NOT_IDENTIFIABLE": "未识别",
        "NO_FEASIBLE_SOLUTION": "不可行",
    }
    actions = {
        "ACTION_NONE": "无措施",
        "ACTION_EXPANSION_ONLY": "仅扩容",
        "ACTION_STORAGE_ONLY": "仅配储",
        "ACTION_COMBINED_EXPANSION_STORAGE": "扩容+配储",
        "NOT_IDENTIFIABLE": "未形成唯一推荐",
    }
    triggers = {
        "no_material_physical_gap": "无明显物理缺口",
        "positive_capacity_gap": "正向容量缺口",
        "reverse_hosting_gap": "反向承载缺口",
        "positive_and_reverse_gap": "正向与反向均有缺口",
        "data_not_identified": "数据未识别",
        "MIXED_ANNUAL_STATES": "年度状态存在差异",
        "NOT_IDENTIFIABLE": "未识别",
    }
    if field in {"recommended_scheme_code", "current_recommended_scheme_code"}:
        return schemes.get(str(value), str(value))
    if field in {"recommended_action_mode", "current_recommended_action_mode"}:
        return actions.get(str(value), str(value))
    if field == "measure_trigger_constraint":
        return triggers.get(str(value), str(value))
    return _fmt(value)


def _transposed_markdown(matrix: pd.DataFrame, title: str) -> str:
    regions = matrix["region_id"].astype(str).tolist()
    row_specs = [
        ("当前推荐容载比 R_rec（成本最小可行方案）", "recommended_clr"),
        ("模型现状容载比 R0", "clr_model_base"),
        ("公用变容量（MVA）", "capacity_base_mva"),
        ("正向最大净负荷（MW）", "positive_peak_base_mw"),
        ("光伏容量（MW）", "pv_capacity_snapshot_mw"),
        ("光伏渗透率（%）", "pv_capacity_to_positive_peak_ratio"),
        ("反向峰值（MW）", "reverse_peak_base_mw"),
        ("正向设备容量缺口（MW）", "positive_capacity_gap_mw"),
        ("反向承载缺口（MW）", "reverse_hosting_gap_mw"),
        ("正向缺口设备数", "positive_gap_device_count"),
        ("反向缺口设备数", "reverse_gap_device_count"),
        ("措施触发约束", "measure_trigger_constraint"),
        ("推荐方案", "recommended_scheme_code"),
        ("推荐措施", "recommended_action_mode"),
        ("等效年成本（万元/年）", "recommended_eac_wanyuan_per_year"),
    ]
    lines = [f"### {title}", "", "| 指标 | " + " | ".join(regions) + " |", "|---|" + "---|" * len(regions)]
    for label, field in row_specs:
        values: list[str] = []
        for _, row in matrix.iterrows():
            value = row.get(field)
            if field == "pv_capacity_to_positive_peak_ratio" and pd.notna(value):
                value = float(value) * 100.0
            values.append(_word_value(value, field).replace("|", "\\|"))
        lines.append("| " + label + " | " + " | ".join(values) + " |")
    lines.append("")
    return "\n".join(lines)


def _interval_text(row: pd.Series, field: str, percent: bool = False) -> str:
    low = row.get(f"{field}_min", float("nan"))
    high = row.get(f"{field}_max", float("nan"))
    if pd.isna(low) or pd.isna(high):
        return "—"
    if percent:
        low, high = float(low) * 100.0, float(high) * 100.0
    return f"{float(low):.2f}–{float(high):.2f}"


def _transposed_interval_markdown(interval: pd.DataFrame, title: str) -> str:
    regions = interval["region_id"].astype(str).tolist()
    row_specs = [
        ("当前推荐容载比区间（2021—2025 年有效年度）", "recommended_clr", False),
        ("模型现状容载比区间", "history_model_clr", False),
        ("公用变容量区间（MVA）", "capacity_base_mva", False),
        ("正向最大净负荷区间（MW）", "positive_peak_base_mw", False),
        ("光伏容量区间（MW）", "pv_capacity_snapshot_mw", False),
        ("光伏渗透率区间（%）", "pv_capacity_to_positive_peak_ratio", True),
        ("反向峰值区间（MW）", "reverse_peak_base_mw", False),
        ("正向设备容量缺口区间（MW）", "positive_capacity_gap_mw", False),
        ("反向承载缺口区间（MW）", "reverse_hosting_gap_mw", False),
        ("正向缺口设备数区间", "positive_gap_device_count", False),
        ("反向缺口设备数区间", "reverse_gap_device_count", False),
        ("措施触发约束", "measure_trigger_constraint", False),
        ("推荐方案", "current_recommended_scheme_code", False),
        ("推荐措施", "current_recommended_action_mode", False),
        ("等效年成本区间（万元/年）", "recommended_eac_wanyuan_per_year", False),
    ]
    lines = [f"### {title}", "", "| 指标 | " + " | ".join(regions) + " |", "|---|" + "---|" * len(regions)]
    for label, field, percent in row_specs:
        values: list[str] = []
        for _, row in interval.iterrows():
            if field in {"measure_trigger_constraint", "current_recommended_scheme_code", "current_recommended_action_mode"}:
                value = _word_value(row.get(field), "measure_trigger_constraint" if field == "measure_trigger_constraint" else field)
            elif field == "history_model_clr":
                value = _interval_text(row, field)
            else:
                value = _interval_text(row, field, percent)
            values.append(str(value).replace("|", "\\|"))
        lines.append("| " + label + " | " + " | ".join(values) + " |")
    lines.append("")
    return "\n".join(lines)


def _rowwise_markdown(matrix: pd.DataFrame, title: str) -> str:
    fields = [
        "region_id",
        "evidence_grade",
        "capacity_base_mva",
        "positive_peak_base_mw",
        "clr_model_base",
        "recommended_scheme_code",
        "recommended_clr",
        "recommended_eac_wanyuan_per_year",
        "quality_notes",
    ]
    labels = {
        "region_id": "脱敏片区",
        "evidence_grade": "证据等级",
        "capacity_base_mva": "S0（MVA）",
        "positive_peak_base_mw": "P_plus_base（MW）",
        "clr_model_base": "R0",
        "recommended_scheme_code": "当前推荐方案",
        "recommended_clr": "R_rec",
        "recommended_eac_wanyuan_per_year": "推荐EAC（万元/年）",
        "quality_notes": "质量备注",
    }
    lines = [f"### {title}（精确查值表）", "", "| " + " | ".join(labels[field] for field in fields) + " |", "|" + "---|" * len(fields)]
    for _, row in matrix.iterrows():
        lines.append("| " + " | ".join(_fmt(row[field]).replace("|", "\\|") for field in fields) + " |")
    lines.append("")
    return "\n".join(lines)


def _final_interval_markdown(interval: pd.DataFrame, title: str) -> str:
    fields = [
        ("脱敏片区", "region_id"),
        ("证据等级", "evidence_grade"),
        ("五年历史参考下限 R", "history_clr_min"),
        ("五年历史参考上限 R", "history_clr_max"),
        ("五年模型口径下限 R", "history_model_clr_min"),
        ("五年模型口径上限 R", "history_model_clr_max"),
        ("2025当前推荐方案", "current_recommended_scheme_code"),
        ("2025当前推荐 R_rec", "current_recommended_clr"),
        ("最终推荐区间下限", "final_recommendation_interval_low"),
        ("最终推荐区间上限", "final_recommendation_interval_high"),
        ("解释", "interpretation"),
    ]
    lines = [f"### {title}", "", "| " + " | ".join(label for label, _ in fields) + " |", "|" + "---|" * len(fields)]
    for _, row in interval.iterrows():
        lines.append("| " + " | ".join(_fmt(row[field]).replace("|", "\\|") for _, field in fields) + " |")
    lines.append("")
    return "\n".join(lines)


def build_outputs(years: list[int]) -> Path:
    research_root = ROOT
    processed_root = research_root / "data" / "processed" / "real_2025"
    source_root = research_root / "data" / "tuomin" / "电网建模数据_Agent整合版_V1.2"
    formal_run = research_root / "results" / "runs" / "real-2025-contract-v2"
    contract_path = research_root / "model_contract.yaml"
    output_root = research_root / "results" / "runs" / "annual_2021_2025"
    final_root = research_root / "results" / "annual_2021_2025"
    final_root.mkdir(parents=True, exist_ok=True)

    formal_manifest_path = formal_run / "manifest.json"
    if not formal_manifest_path.is_file():
        raise RuntimeError("annual formal output blocked: real-2025 formal manifest is missing")
    formal_manifest = json.loads(formal_manifest_path.read_text(encoding="utf-8"))
    require_formal_approval(
        {
            "grade_a_ready": formal_manifest.get("timeseries_grade_a_ready", False),
            "formal_hourly_use_allowed": formal_manifest.get("timeseries_grade_a_ready", False),
        }
    )

    reference = load_historical_reference(source_root / "近5年容载比.xlsx")
    current_baseline = pd.read_csv(formal_run / "county_baseline.csv")
    all_modes: list[pd.DataFrame] = []
    annual_matrices: dict[tuple[int, int], pd.DataFrame] = {}
    for year in years:
        modes = run_annual_year(
            processed_root,
            formal_run,
            contract_path,
            output_root,
            reference,
            current_baseline,
            year,
        )
        all_modes.append(modes)
        for voltage in (110, 35):
            matrix = aggregate_annual_matrix(modes, year, voltage)
            annual_matrices[(year, voltage)] = matrix
            matrix.to_csv(final_root / f"annual_matrix_{year}_{voltage}kv.csv", index=False, lineterminator="\n")
            (final_root / f"annual_matrix_{year}_{voltage}kv.md").write_text(
                _rowwise_markdown(matrix, f"{year}年{voltage} kV年度方案矩阵"), encoding="utf-8"
            )
    modes_frame = pd.concat(all_modes, ignore_index=True)
    modes_frame.to_csv(final_root / "annual_solution_modes_2021_2025.csv", index=False, lineterminator="\n")
    intervals: dict[int, pd.DataFrame] = {}
    for voltage in (110, 35):
        interval = build_final_recommendation_interval(
            [annual_matrices[(year, voltage)] for year in years], annual_matrices[(2025, voltage)], voltage
        )
        intervals[voltage] = interval
        interval.to_csv(final_root / f"final_recommendation_interval_{voltage}kv.csv", index=False, lineterminator="\n")
        (final_root / f"final_recommendation_interval_{voltage}kv.md").write_text(
            _final_interval_markdown(interval, f"{voltage} kV最终推荐区间矩阵"), encoding="utf-8"
        )

    sections = [
        "# 2021—2025 年度容载比方案矩阵与最终推荐区间",
        "",
        "## 口径说明",
        "",
        "方案代码使用 `SCHEME_C0/SCHEME_A/SCHEME_B`，证据等级使用 `EVIDENCE_A/EVIDENCE_B/EVIDENCE_C`。每年分别比较仅扩容、仅配储、扩容+配储；2021为静态参考，2022—2024为诊断回放，2025为当前正式优化入口。缺少同年8760或资产/候选闭环时不填伪造EAC。容载比分母固定为干预前正向同步峰值，110/35 kV不混算。",
        "",
    ]
    for year in years:
        for voltage in (110, 35):
            matrix = annual_matrices[(year, voltage)]
            sections.append(_transposed_markdown(matrix, f"{year}年{voltage} kV甲方转置式推荐主表"))
    for voltage in (110, 35):
        sections.append(_transposed_interval_markdown(intervals[voltage], f"{voltage} kV五年汇总推荐区间矩阵"))
    markdown_path = final_root / "五年年度容载比推荐矩阵与最终区间.md"
    markdown_path.write_text("\n".join(sections), encoding="utf-8")
    docx_path = final_root / "五年年度容载比推荐矩阵与最终区间.docx"
    try:
        subprocess.run(["pandoc", str(markdown_path), "-o", str(docx_path)], check=True, capture_output=True, text=True)
        docx_status = "created"
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        docx_status = f"failed:{exc}"

    output_files = {}
    for path in sorted(final_root.iterdir()):
        if path.is_file():
            output_files[path.name] = {"bytes": path.stat().st_size, "sha256": _sha256(path)}
    manifest = {
        "run_id": "annual_2021_2025_project_output_v1",
        "years": years,
        "voltage_levels_kv": [110, 35],
        "source_reference_sha256": _sha256(source_root / "近5年容载比.xlsx"),
        "formal_2025_run_manifest_sha256": _sha256(formal_run / "manifest.json"),
        "contract_sha256": _sha256(contract_path),
        "historical_backtest_claimed": False,
        "docx_status": docx_status,
        "output_files": output_files,
        "constraints": {
            "scheme_codes": ["SCHEME_C0", "SCHEME_A", "SCHEME_B"],
            "evidence_codes": ["EVIDENCE_A", "EVIDENCE_B", "EVIDENCE_C"],
            "action_modes": list(ACTION_MODES),
            "fixed_positive_denominator": True,
            "cross_voltage_aggregation": False,
        },
    }
    (final_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return final_root


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int, default=ANNUAL_YEARS)
    args = parser.parse_args()
    invalid = sorted(set(args.years) - set(ANNUAL_YEARS))
    if invalid:
        parser.error(f"years must be within {ANNUAL_YEARS}, got {invalid}")
    output = build_outputs(sorted(set(args.years)))
    print(f"ANNUAL MODEL CLOSED LOOP PASS\noutput_root={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
