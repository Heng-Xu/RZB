"""2021--2025 年度状态/诊断矩阵与最终推荐表生成。

本模块把 ``近5年容载比.xlsx`` 的年度静态锚点接入现有真实 C0/A/B
规划器。2022--2024 使用 2025 经验日形状迁移，2021 只有静态年度锚点；
因此这些年份的输出是诊断型年度方案，不能冒充审批后的真实 8760 回放。
所有最终输出使用带前缀的方案和证据代码，避免 ``方案A`` 与 ``证据等级A``
混淆。源文件只读，年度派生数据写入指定运行目录。
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from src.milp_planner import (
    StationOption,
    _select_county_options,
    a_incremental_capacity_limit,
    solve_real_c0ab,
)


ANNUAL_YEARS = [2021, 2022, 2023, 2024, 2025]
REGION_COUNT = 8
VOLTAGES = (110, 35)
SCHEME_CODES = ("SCHEME_C0", "SCHEME_A", "SCHEME_B")
ACTION_MODES = (
    "ACTION_EXPANSION_ONLY",
    "ACTION_STORAGE_ONLY",
    "ACTION_COMBINED_EXPANSION_STORAGE",
)
FINAL_REQUIRED_FIELDS = {
    "year",
    "region_id",
    "voltage_kv",
    "scheme_code",
    "evidence_grade",
    "action_mode",
    "status",
}
REQUIRED_ANNUAL_FIELDS = (
    "year",
    "region_id",
    "voltage_kv",
    "capacity_mva",
    "positive_peak_base_mw",
    "clr_model_base",
    "evidence_grade",
    "asset_scope_id",
    "quality_notes",
    "source_ref",
    "source_version",
    "transformation",
    "scenario_id",
    "quality_flag",
    "source_sha256",
)


class AnnualModelError(ValueError):
    """年度输入、方案代码或发布门禁不满足。"""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _frame_hash(frame: pd.DataFrame) -> str:
    payload = frame.sort_index(axis=1).sort_values(list(frame.columns), kind="stable").to_csv(
        index=False, lineterminator="\n"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonical_scheme_code(value: Any) -> str:
    text = str(value).strip().upper()
    aliases = {"C0": "SCHEME_C0", "SCHEME_C0": "SCHEME_C0", "A": "SCHEME_A", "SCHEME_A": "SCHEME_A", "B": "SCHEME_B", "SCHEME_B": "SCHEME_B"}
    if text not in aliases:
        raise AnnualModelError(f"unknown scheme code: {value!r}")
    return aliases[text]


def canonical_evidence_code(value: Any) -> str:
    text = str(value).strip().upper()
    aliases = {"A": "EVIDENCE_A", "EVIDENCE_A": "EVIDENCE_A", "B": "EVIDENCE_B", "EVIDENCE_B": "EVIDENCE_B", "C": "EVIDENCE_C", "EVIDENCE_C": "EVIDENCE_C"}
    if text not in aliases:
        raise AnnualModelError(f"unknown evidence grade: {value!r}")
    return aliases[text]


def _number(value: Any) -> float:
    result = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(result):
        raise AnnualModelError(f"expected numeric value, got {value!r}")
    return float(result)


def load_historical_reference(path: Path) -> pd.DataFrame:
    """解析年度官方静态容载比表，单位从“万”转换为 MW/MVA。"""
    path = Path(path)
    if not path.is_file():
        raise AnnualModelError(f"historical reference missing: {path}")
    raw = pd.read_excel(path, sheet_name=0, header=None)
    year_columns = {
        2021: (2, 3, 4),
        2022: (5, 6, 7),
        2023: (8, 9, 10),
        2024: (11, 12, 13),
        2025: (14, 15, 16),
    }
    rows: list[dict[str, Any]] = []
    source_hash = _sha256(path)
    last_region: str | None = None
    for row_index, row in raw.iterrows():
        region = row.iloc[0] if len(row) else None
        if isinstance(region, str) and region.strip().startswith("QX-"):
            last_region = region.strip()
        elif pd.isna(region):
            region = last_region
        voltage_text = row.iloc[1] if len(row) > 1 else None
        if not isinstance(region, str) or not region.strip().startswith("QX-"):
            continue
        voltage_text = str(voltage_text or "")
        voltage = 110 if "110" in voltage_text else 35 if "35" in voltage_text else None
        if voltage is None:
            continue
        for year, (capacity_col, peak_col, clr_col) in year_columns.items():
            capacity = _number(row.iloc[capacity_col]) * 10.0
            peak = _number(row.iloc[peak_col]) * 10.0
            official = _number(row.iloc[clr_col])
            if capacity <= 0 or peak <= 0 or official <= 0:
                raise AnnualModelError(f"invalid annual reference row {row_index}, year {year}")
            rows.append(
                {
                    "year": year,
                    "region_id": region.strip(),
                    "voltage_kv": voltage,
                    "capacity_mva": capacity,
                    "positive_peak_base_mw": peak,
                    "clr_model_base": capacity / peak,
                    "clr_official_reference": official,
                    "source_ref": f"{path.name}:Sheet1!row{row_index + 1}",
                    "source_version": "电网建模数据_Agent整合版_V1.2",
                    "transformation": "convert official 万千伏安/万千瓦 to MVA/MW; retain official CLR as reference",
                    "scenario_id": f"historical_reference_{year}",
                    "quality_flag": "official_static_anchor",
                    "source_sha256": source_hash,
                }
            )
    result = pd.DataFrame(rows)
    expected = REGION_COUNT * len(ANNUAL_YEARS) * len(VOLTAGES)
    if len(result) != expected or sorted(result["year"].unique().tolist()) != ANNUAL_YEARS:
        raise AnnualModelError(
            f"historical reference expected {expected} rows and five years, got {len(result)}"
        )
    if result[["region_id", "year", "voltage_kv"]].duplicated().any():
        raise AnnualModelError("historical reference has duplicate region-year-voltage keys")
    return result.sort_values(["year", "voltage_kv", "region_id"], kind="stable").reset_index(drop=True)


def build_annual_baseline(
    reference: pd.DataFrame,
    current_baseline: pd.DataFrame,
    year: int,
) -> pd.DataFrame:
    """把年度官方容量/峰值锚点转换为规划器所需的县区基线。"""
    if year not in ANNUAL_YEARS:
        raise AnnualModelError(f"year outside annual contract: {year}")
    required_reference = {"year", "region_id", "voltage_kv", "capacity_mva", "positive_peak_base_mw", "clr_official_reference"}
    if not required_reference <= set(reference.columns):
        raise AnnualModelError(f"historical reference missing {sorted(required_reference - set(reference.columns))}")
    current = current_baseline.copy()
    current["region_id"] = current["region_id"].astype(str)
    current["voltage_kv"] = current["voltage_kv"].astype(int)
    lookup = current.set_index(["region_id", "voltage_kv"])
    rows: list[dict[str, Any]] = []
    source_hash = _frame_hash(reference[reference["year"].eq(year)])
    for item in reference[reference["year"].eq(year)].itertuples(index=False):
        key = (str(item.region_id), int(item.voltage_kv))
        old = lookup.loc[key] if key in lookup.index else pd.Series(dtype=object)
        historical = year != 2025
        evidence = "EVIDENCE_C" if historical else canonical_evidence_code(old.get("evidence_grade", "C"))
        scope = "operating_2025" if year == 2025 else f"historical_{year}_reference_static"
        gap_note = (
            "official static anchor only; no same-year 8760, annual asset scope, PV snapshot or cost candidate closure"
            if year == 2021
            else "diagnostic replay: 8760 sample/mapping exists but same-year asset scope, PV and candidate cost closure is unresolved"
            if year in {2022, 2023}
            else "diagnostic replay: cross-year hourly sheet and 2024 anomaly review required; 2025 asset/cost scope reused as marked"
            if year == 2024
            else str(old.get("quality_notes", "2025 current-condition baseline"))
        )
        rows.append(
            {
                "year": year,
                "region_id": str(item.region_id),
                "voltage_kv": int(item.voltage_kv),
                "capacity_base_mva": float(item.capacity_mva),
                "capacity_mva": float(item.capacity_mva),
                "positive_peak_base_mw": float(item.positive_peak_base_mw),
                "positive_peak_static_upper_bound_mw": float(item.positive_peak_base_mw),
                "reverse_peak_base_mw": old.get("reverse_peak_base_mw", np.nan),
                "reverse_peak_static_lower_bound_mw": old.get("reverse_peak_static_lower_bound_mw", np.nan),
                "reverse_peak_static_upper_bound_mw": old.get("reverse_peak_static_upper_bound_mw", np.nan),
                "clr_model_base": float(item.capacity_mva) / float(item.positive_peak_base_mw),
                "clr_official_reference": float(item.clr_official_reference),
                "pv_capacity_snapshot_mw": old.get("pv_capacity_snapshot_mw", np.nan) if year == 2025 else np.nan,
                "pv_capacity_to_positive_peak_ratio": old.get("pv_capacity_to_positive_peak_ratio", np.nan) if year == 2025 else np.nan,
                "pv_pipeline_mw": old.get("pv_pipeline_mw", np.nan) if year == 2025 else np.nan,
                "pv_capacity_snapshot_year": old.get("pv_capacity_snapshot_year", np.nan) if year == 2025 else np.nan,
                "evidence_grade": evidence,
                "asset_scope_id": scope,
                "quality_notes": gap_note,
                "positive_capacity_gap_mw": old.get("positive_capacity_gap_mw", np.nan) if year == 2025 else np.nan,
                "reverse_hosting_gap_mw": old.get("reverse_hosting_gap_mw", np.nan) if year == 2025 else np.nan,
                "positive_gap_device_count": old.get("positive_gap_device_count", np.nan) if year == 2025 else np.nan,
                "reverse_gap_device_count": old.get("reverse_gap_device_count", np.nan) if year == 2025 else np.nan,
                "data_gap_device_count": old.get("data_gap_device_count", np.nan) if year == 2025 else np.nan,
                "measure_trigger_constraint": old.get("measure_trigger_constraint", "data_not_identified") if year == 2025 else "data_not_identified",
                "strict_r_lt_2_policy_status": old.get("strict_r_lt_2_policy_status", "not_evaluated_current_C0AB_scope") if year == 2025 else "not_evaluated_current_C0AB_scope",
                "source_ref": f"近5年容载比.xlsx + {old.get('source_ref', 'current baseline unavailable')}",
                "source_version": "电网建模数据_Agent整合版_V1.2",
                "transformation": "annual official capacity/peak anchor; no static extrema sum used as synchronous peak",
                "scenario_id": f"annual_{year}_reference_baseline",
                "quality_flag": "historical_static_reference_only" if year == 2021 else "historical_diagnostic_replay" if historical else "formal_2025_baseline_with_current_quality_gate",
                "source_sha256": source_hash,
            }
        )
    result = pd.DataFrame(rows)
    if len(result) != 16:
        raise AnnualModelError(f"annual baseline expected 16 rows for {year}, got {len(result)}")
    return result.sort_values(["voltage_kv", "region_id"], kind="stable").reset_index(drop=True)


def _parse_ids(value: Any) -> tuple[str, ...]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ()
    try:
        parsed = json.loads(str(value))
        if isinstance(parsed, list):
            return tuple(sorted(str(item) for item in parsed))
    except json.JSONDecodeError:
        pass
    return tuple(sorted(item for item in str(value).split(";") if item))


def _option_from_row(row: pd.Series) -> StationOption:
    return StationOption(
        station_id=str(row["station_id"]),
        selected_candidate_ids=_parse_ids(row.get("selected_candidate_ids", row.get("candidate_id"))),
        expansion_delta_mva=float(row["expansion_delta_mva"]),
        storage_modules=int(round(float(row["storage_modules"]))),
        forward_limit_mw=float(row["forward_limit_mw"]),
        reverse_limit_mw=float(row["reverse_limit_mw"]),
        capex_low_wanyuan=float(row["capex_low_wanyuan"]),
        capex_base_wanyuan=float(row["capex_base_wanyuan"]),
        capex_high_wanyuan=float(row["capex_high_wanyuan"]),
        eac_low_wanyuan_per_year=float(row["eac_low_wanyuan_per_year"]),
        eac_base_wanyuan_per_year=float(row["eac_base_wanyuan_per_year"]),
        eac_high_wanyuan_per_year=float(row["eac_high_wanyuan_per_year"]),
        feasible=bool(row["feasible"]),
        reason=str(row["reason"]),
    )


def _aggregate_options(chosen: list[StationOption]) -> dict[str, Any]:
    ids = tuple(candidate for option in chosen for candidate in option.selected_candidate_ids)
    return {
        "status": "feasible",
        "status_reason": "feasible",
        "expansion_delta_mva": sum(option.expansion_delta_mva for option in chosen),
        "storage_modules": sum(option.storage_modules for option in chosen),
        "capex_low_wanyuan": sum(option.capex_low_wanyuan for option in chosen),
        "capex_wanyuan": sum(option.capex_base_wanyuan for option in chosen),
        "capex_high_wanyuan": sum(option.capex_high_wanyuan for option in chosen),
        "eac_low_wanyuan_per_year": sum(option.eac_low_wanyuan_per_year for option in chosen),
        "eac_wanyuan_per_year": sum(option.eac_base_wanyuan_per_year for option in chosen),
        "eac_high_wanyuan_per_year": sum(option.eac_high_wanyuan_per_year for option in chosen),
        "selected_candidate_ids": json.dumps(ids, ensure_ascii=False),
    }


def build_action_mode_rows(
    options: pd.DataFrame,
    annual_baseline: pd.DataFrame,
    raw_solutions: pd.DataFrame,
    year: int,
    source_hash: str,
) -> pd.DataFrame:
    """从逐站离散选项派生“仅扩容/仅配储/联合”比较行。"""
    rows: list[dict[str, Any]] = []
    base = annual_baseline.set_index(["region_id", "voltage_kv"])
    raw = raw_solutions.copy()
    raw["scheme_code"] = raw["scheme"].map(canonical_scheme_code)
    for key, base_row in annual_baseline.set_index(["region_id", "voltage_kv"]).iterrows():
        region_id, voltage = key
        evidence = str(base_row["evidence_grade"])
        c0 = raw[(raw["region_id"].eq(region_id)) & (raw["voltage_kv"].eq(voltage)) & (raw["scheme"].eq("C0"))]
        if year == 2021:
            c0_status, c0_reason = "not_identifiable_or_data_gap", "no same-year 8760; C0 physical status cannot be uniquely verified"
        elif c0.empty:
            c0_status, c0_reason = "noncompliant", "historical_static_reference_no_dynamic_c0_replay"
        else:
            c0_status, c0_reason = str(c0.iloc[0]["status"]), str(c0.iloc[0]["status_reason"])
        rows.append(
            _mode_row(
                year,
                region_id,
                voltage,
                "SCHEME_C0",
                evidence,
                "ACTION_NONE",
                c0_status,
                c0_reason,
                base_row,
                {"expansion_delta_mva": 0.0, "storage_modules": 0, "capex_wanyuan": 0.0, "eac_wanyuan_per_year": 0.0, "selected_candidate_ids": "[]"},
                source_hash,
            )
        )
        option_subset = options[options["region_id"].eq(region_id) & options["voltage_kv"].eq(voltage)]
        station_options: dict[str, list[StationOption]] = {
            str(station_id): [_option_from_row(row) for _, row in group.iterrows()]
            for station_id, group in option_subset.groupby("station_id", sort=True)
        }
        for scheme_code, limit in (("SCHEME_A", a_incremental_capacity_limit(float(base_row["capacity_mva"]), float(base_row["positive_peak_base_mw"]))), ("SCHEME_B", None)):
            raw_scheme = "A" if scheme_code == "SCHEME_A" else "B"
            for action_mode in ACTION_MODES:
                filtered: dict[str, list[StationOption]] = {}
                for station_id, station_rows in station_options.items():
                    if action_mode == "ACTION_EXPANSION_ONLY":
                        selected = [option for option in station_rows if option.storage_modules == 0]
                    elif action_mode == "ACTION_STORAGE_ONLY":
                        selected = [option for option in station_rows if option.expansion_delta_mva <= 1e-9]
                    else:
                        selected = station_rows
                    filtered[station_id] = selected
                chosen, reason = _select_county_options(filtered, limit) if filtered else (None, "no_station_option_input")
                if chosen is None:
                    details = {"status": "infeasible", "status_reason": reason, "expansion_delta_mva": np.nan, "storage_modules": np.nan, "capex_wanyuan": np.nan, "eac_wanyuan_per_year": np.nan, "selected_candidate_ids": "[]"}
                else:
                    details = _aggregate_options(chosen)
                rows.append(_mode_row(year, region_id, voltage, scheme_code, evidence, action_mode, details["status"], details["status_reason"], base_row, details, source_hash))
    result = pd.DataFrame(rows)
    validate_annual_rows(result)
    return result.sort_values(["year", "voltage_kv", "region_id", "scheme_code", "action_mode"], kind="stable").reset_index(drop=True)


def _mode_row(
    year: int,
    region_id: str,
    voltage: int,
    scheme_code: str,
    evidence: str,
    action_mode: str,
    status: str,
    reason: str,
    base_row: pd.Series,
    details: dict[str, Any],
    source_hash: str,
) -> dict[str, Any]:
    delta = details.get("expansion_delta_mva", np.nan)
    return {
        "year": int(year),
        "region_id": str(region_id),
        "voltage_kv": int(voltage),
        "scheme_code": canonical_scheme_code(scheme_code),
        "evidence_grade": canonical_evidence_code(evidence),
        "action_mode": action_mode,
        "status": str(status),
        "status_reason": str(reason),
        "capacity_base_mva": float(base_row["capacity_mva"]),
        "positive_peak_base_mw": float(base_row["positive_peak_base_mw"]),
        "pv_capacity_snapshot_mw": base_row.get("pv_capacity_snapshot_mw", np.nan),
        "pv_capacity_to_positive_peak_ratio": base_row.get("pv_capacity_to_positive_peak_ratio", np.nan),
        "reverse_peak_base_mw": base_row.get("reverse_peak_base_mw", np.nan),
        "positive_capacity_gap_mw": base_row.get("positive_capacity_gap_mw", np.nan),
        "reverse_hosting_gap_mw": base_row.get("reverse_hosting_gap_mw", np.nan),
        "positive_gap_device_count": base_row.get("positive_gap_device_count", np.nan),
        "reverse_gap_device_count": base_row.get("reverse_gap_device_count", np.nan),
        "data_gap_device_count": base_row.get("data_gap_device_count", np.nan),
        "measure_trigger_constraint": base_row.get("measure_trigger_constraint", "data_not_identified"),
        "strict_r_lt_2_policy_status": base_row.get("strict_r_lt_2_policy_status", "not_evaluated_current_C0AB_scope"),
        "clr_model_base": float(base_row["clr_model_base"]),
        "clr_official_reference": float(base_row["clr_official_reference"]),
        "expansion_delta_mva": delta,
        "storage_modules": details.get("storage_modules", np.nan),
        "expansion_capex_wanyuan": details.get("capex_wanyuan", np.nan),
        "storage_capex_wanyuan": np.nan,
        "capex_wanyuan": details.get("capex_wanyuan", np.nan),
        "eac_wanyuan_per_year": details.get("eac_wanyuan_per_year", np.nan),
        "clr_after": (float(base_row["capacity_mva"]) + float(delta)) / float(base_row["positive_peak_base_mw"])
        if pd.notna(delta)
        else np.nan,
        "a_expansion_limit_mva": a_incremental_capacity_limit(float(base_row["capacity_mva"]), float(base_row["positive_peak_base_mw"])),
        "strict_stock_R_le_2_status": "infeasible_due_to_inherited_stock" if float(base_row["capacity_mva"]) > 2.0 * float(base_row["positive_peak_base_mw"]) else "stock_within_2.0",
        "selected_candidate_ids": details.get("selected_candidate_ids", "[]"),
        "asset_scope_id": str(base_row["asset_scope_id"]),
        "quality_notes": str(base_row["quality_notes"]),
        "source_ref": str(base_row["source_ref"]),
        "source_version": str(base_row["source_version"]),
        "transformation": "canonicalize scheme/evidence codes and compare expansion-only, storage-only and combined options",
        "scenario_id": f"annual_{year}_scheme_action_mode",
        "quality_flag": "annual_diagnostic_or_formal_2025_gate",
        "source_sha256": source_hash,
    }


def validate_annual_rows(frame: pd.DataFrame) -> bool:
    missing = FINAL_REQUIRED_FIELDS - set(frame.columns)
    if missing:
        raise AnnualModelError(f"annual output missing fields {sorted(missing)}")
    if not set(frame["scheme_code"].dropna()).issubset(set(SCHEME_CODES)):
        raise AnnualModelError("annual output contains non-canonical scheme codes")
    if not set(frame["evidence_grade"].dropna()).issubset({"EVIDENCE_A", "EVIDENCE_B", "EVIDENCE_C"}):
        raise AnnualModelError("annual output contains non-canonical evidence codes")
    if set(frame["scheme_code"]) & set(frame["evidence_grade"]):
        raise AnnualModelError("scheme and evidence code namespaces overlap")
    for key, group in frame.groupby(["year", "region_id", "voltage_kv"], sort=False):
        if set(group["scheme_code"]) != set(SCHEME_CODES):
            raise AnnualModelError(f"{key}: missing one of C0/A/B scheme codes")
        c0 = group[group["scheme_code"].eq("SCHEME_C0")]
        if set(c0["action_mode"]) != {"ACTION_NONE"}:
            raise AnnualModelError(f"{key}: C0 must have ACTION_NONE only")
        for scheme in ("SCHEME_A", "SCHEME_B"):
            modes = set(group[group["scheme_code"].eq(scheme)]["action_mode"])
            if modes != set(ACTION_MODES):
                raise AnnualModelError(f"{key}|{scheme}: missing action mode comparison")
    return True


def scale_empirical_profiles(
    profiles: pd.DataFrame,
    current_baseline: pd.DataFrame,
    annual_baseline: pd.DataFrame,
    year: int,
) -> pd.DataFrame:
    """按年度县域峰值迁移24小时经验形状；保留诊断性质和血缘字段。"""
    required = {"region_id", "voltage_kv", "station_id", "duration_scenario", "hour", "net_load_mw"}
    if not required <= set(profiles.columns):
        raise AnnualModelError(f"profiles missing {sorted(required - set(profiles.columns))}")
    base_peak = current_baseline.set_index(["region_id", "voltage_kv"])["positive_peak_base_mw"].astype(float)
    target_peak = annual_baseline.set_index(["region_id", "voltage_kv"])["positive_peak_base_mw"].astype(float)
    result = profiles.copy()
    factors: list[float] = []
    for row in result.itertuples(index=False):
        key = (str(row.region_id), int(row.voltage_kv))
        if key not in base_peak.index or key not in target_peak.index:
            raise AnnualModelError(f"profile scaling key absent from baseline: {key}")
        denominator = float(base_peak.loc[key])
        factor = float(target_peak.loc[key]) / denominator
        factors.append(factor)
    result["net_load_mw"] = result["net_load_mw"].astype(float).to_numpy() * np.asarray(factors)
    result["transformation"] = f"scale 2025 empirical duration shape to official annual {year} positive peak; not historical 8760"
    result["scenario_id"] = f"annual_{year}_empirical_duration_transfer"
    result["quality_flag"] = "static_anchor_scaled_empirical_duration"
    return result


def _copy_required_inputs(processed_root: Path, source_working_root: Path, year_working: Path) -> None:
    year_working.mkdir(parents=True, exist_ok=True)
    for filename in ("expansion_cost_library.csv", "empirical_scenario_index.csv", "empirical_station_scenarios.csv.gz"):
        shutil.copyfile(source_working_root / filename, year_working / filename)
    for filename in ("station_master.csv", "transformer_master.csv"):
        if not (processed_root / filename).is_file():
            raise AnnualModelError(f"processed input missing: {processed_root / filename}")


def run_annual_year(
    processed_root: Path,
    source_working_root: Path,
    contract_path: Path,
    output_root: Path,
    reference: pd.DataFrame,
    current_baseline: pd.DataFrame,
    year: int,
) -> pd.DataFrame:
    """运行一个年度的 C0/A/B 诊断求解并返回规范化比较长表。"""
    output_root.mkdir(parents=True, exist_ok=True)
    year_root = output_root / f"annual_{year}"
    year_working = year_root / "working"
    solver_output = year_root / "solver"
    _copy_required_inputs(processed_root, source_working_root, year_working)
    annual_baseline = build_annual_baseline(reference, current_baseline, year)
    annual_baseline.to_csv(year_working / "county_baseline.csv", index=False, lineterminator="\n")
    profiles = pd.read_csv(source_working_root / "empirical_station_scenarios.csv.gz", compression="gzip")
    scaled = scale_empirical_profiles(profiles, current_baseline, annual_baseline, year)
    scaled.to_csv(year_working / "empirical_station_scenarios.csv.gz", index=False, compression={"method": "gzip", "mtime": 0}, lineterminator="\n")
    # The scenario index is a shape index and remains the same; its final output is marked by annual source hash.
    solve_real_c0ab(processed_root, year_working, solver_output, contract_path)
    raw_options = pd.read_csv(solver_output / "real_plan_station_options.csv")
    raw_solutions = pd.read_csv(solver_output / "real_plan_county_solutions.csv")
    source_hash = _frame_hash(annual_baseline)
    modes = build_action_mode_rows(raw_options, annual_baseline, raw_solutions, year, source_hash)
    annual_baseline.to_csv(year_root / "annual_baseline.csv", index=False, lineterminator="\n")
    modes.to_csv(year_root / "annual_solution_modes.csv", index=False, lineterminator="\n")
    quality = annual_baseline[["year", "region_id", "voltage_kv", "evidence_grade", "quality_notes", "quality_flag", "source_ref", "source_sha256"]].copy()
    quality.to_csv(year_root / "annual_quality_issues.csv", index=False, lineterminator="\n")
    manifest = {
        "year": year,
        "year_status": "static_reference_only" if year == 2021 else "historical_replay_diagnostic" if year < 2025 else "formal_2025_current_condition",
        "evidence_policy": "EVIDENCE_C" if year < 2025 else sorted(set(annual_baseline["evidence_grade"])),
        "annual_baseline_sha256": source_hash,
        "output_files": {
            "annual_baseline.csv": _sha256(year_root / "annual_baseline.csv"),
            "annual_solution_modes.csv": _sha256(year_root / "annual_solution_modes.csv"),
            "annual_quality_issues.csv": _sha256(year_root / "annual_quality_issues.csv"),
        },
        "historical_backtest_claimed": False,
        "profile_basis": "official annual peak scaled 2025 empirical duration shapes; no historical 8760 claim",
    }
    (year_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return modes


def aggregate_annual_matrix(modes: pd.DataFrame, year: int, voltage: int) -> pd.DataFrame:
    """把规范长表转成每年/电压一张八行精确查值矩阵。"""
    subset = modes[(modes["year"].eq(year)) & (modes["voltage_kv"].eq(voltage))].copy()
    if subset.empty:
        raise AnnualModelError(f"no annual modes for {year}/{voltage}")
    baseline = subset.groupby("region_id", as_index=False).first()
    rows: list[dict[str, Any]] = []
    for region_id, group in subset.groupby("region_id", sort=True):
        base_row = group.iloc[0]
        row: dict[str, Any] = {
            "year": year,
            "region_id": region_id,
            "voltage_kv": voltage,
            "evidence_grade": base_row["evidence_grade"],
            "asset_scope_id": base_row["asset_scope_id"],
            "capacity_base_mva": base_row["capacity_base_mva"],
            "positive_peak_base_mw": base_row["positive_peak_base_mw"],
            "clr_model_base": base_row["clr_model_base"],
            "clr_official_reference": base_row["clr_official_reference"],
            "quality_notes": base_row["quality_notes"],
            "source_ref": base_row["source_ref"],
            "source_sha256": base_row["source_sha256"],
        }
        for field in (
            "pv_capacity_snapshot_mw",
            "positive_capacity_gap_mw",
            "reverse_hosting_gap_mw",
            "positive_gap_device_count",
            "reverse_gap_device_count",
            "data_gap_device_count",
            "measure_trigger_constraint",
        ):
            if field in base_row.index:
                row[field] = base_row[field]
        for scheme in ("SCHEME_C0", "SCHEME_A", "SCHEME_B"):
            scheme_rows = group[group["scheme_code"].eq(scheme)]
            for action in (["ACTION_NONE"] if scheme == "SCHEME_C0" else list(ACTION_MODES)):
                item = scheme_rows[scheme_rows["action_mode"].eq(action)]
                if item.empty:
                    continue
                value = item.iloc[0]
                prefix = f"{scheme}_{action}"
                for field in ("status", "status_reason", "expansion_delta_mva", "storage_modules", "capex_wanyuan", "eac_wanyuan_per_year", "clr_after", "selected_candidate_ids"):
                    row[f"{prefix}_{field}"] = value[field]
        c0_rows = group[group["scheme_code"].eq("SCHEME_C0") & group["action_mode"].eq("ACTION_NONE")]
        c0 = c0_rows.iloc[0] if not c0_rows.empty else None
        candidates = []
        if c0 is not None and str(c0["status"]) == "compliant":
            row["recommended_scheme_code"] = "SCHEME_C0"
            row["recommended_action_mode"] = "ACTION_NONE"
            row["recommended_current_measure"] = "SCHEME_C0;ACTION_NONE"
            row["recommended_clr"] = c0.get("clr_after", base_row["clr_model_base"])
            row["recommended_eac_wanyuan_per_year"] = 0.0
            rows.append(row)
            continue
        if c0 is not None and str(c0["status"]) == "not_identifiable":
            row["recommended_scheme_code"] = "NOT_IDENTIFIABLE"
            row["recommended_action_mode"] = "NOT_IDENTIFIABLE"
            row["recommended_current_measure"] = "not_identifiable_or_data_gap"
            row["recommended_clr"] = np.nan
            row["recommended_eac_wanyuan_per_year"] = np.nan
            rows.append(row)
            continue
        for scheme in ("SCHEME_A", "SCHEME_B"):
            item = group[(group["scheme_code"].eq(scheme)) & (group["action_mode"].eq("ACTION_COMBINED_EXPANSION_STORAGE")) & (group["status"].eq("feasible"))]
            if not item.empty and pd.notna(item.iloc[0]["eac_wanyuan_per_year"]):
                candidates.append((float(item.iloc[0]["eac_wanyuan_per_year"]), scheme, item.iloc[0]))
        if candidates:
            _cost, chosen_scheme, chosen = min(candidates, key=lambda value: (value[0], 0 if value[1] == "SCHEME_B" else 1))
            row["recommended_scheme_code"] = chosen_scheme
            row["recommended_action_mode"] = "ACTION_COMBINED_EXPANSION_STORAGE"
            row["recommended_current_measure"] = f"{chosen_scheme};ACTION_COMBINED_EXPANSION_STORAGE;storage_modules={int(chosen['storage_modules'])}"
            row["recommended_clr"] = chosen["clr_after"]
            row["recommended_eac_wanyuan_per_year"] = chosen["eac_wanyuan_per_year"]
        else:
            row["recommended_scheme_code"] = "NOT_IDENTIFIABLE"
            row["recommended_action_mode"] = "NOT_IDENTIFIABLE"
            row["recommended_current_measure"] = "not_identifiable_or_data_gap"
            row["recommended_clr"] = np.nan
            row["recommended_eac_wanyuan_per_year"] = np.nan
        rows.append(row)
    result = pd.DataFrame(rows).sort_values("region_id", kind="stable").reset_index(drop=True)
    if len(result) != REGION_COUNT:
        raise AnnualModelError(f"annual matrix expected {REGION_COUNT} rows, got {len(result)}")
    return result


def build_final_recommendation_interval(annual_matrices: Iterable[pd.DataFrame], current_matrix_2025: pd.DataFrame, voltage: int) -> pd.DataFrame:
    """形成“五年历史参考区间 + 2025成本推荐点”的最终区间矩阵。"""
    frames = [frame[frame["voltage_kv"].eq(voltage)].copy() for frame in annual_matrices]
    history = pd.concat(frames, ignore_index=True)
    rows: list[dict[str, Any]] = []
    current = current_matrix_2025.set_index("region_id")
    for region_id, group in history.groupby("region_id", sort=True):
        observed = pd.to_numeric(group["clr_official_reference"], errors="coerce")
        model_observed = pd.to_numeric(group["clr_model_base"], errors="coerce")
        rec = current.loc[region_id] if region_id in current.index else pd.Series(dtype=object)
        rec_clr = pd.to_numeric(pd.Series([rec.get("recommended_clr", np.nan)]), errors="coerce").iloc[0]
        hist_low, hist_high = float(observed.min()), float(observed.max())
        package_low = min(hist_low, float(rec_clr)) if pd.notna(rec_clr) else hist_low
        package_high = max(hist_high, float(rec_clr)) if pd.notna(rec_clr) else hist_high
        current_scheme = rec.get("recommended_scheme_code", "NOT_IDENTIFIABLE")
        final_evidence = rec.get("evidence_grade", "EVIDENCE_C")
        if current_scheme == "NOT_IDENTIFIABLE":
            final_evidence = "EVIDENCE_C"
        def interval(field: str) -> tuple[float, float]:
            values = pd.to_numeric(group.get(field, pd.Series(dtype=float)), errors="coerce").dropna()
            if values.empty:
                return float("nan"), float("nan")
            return float(values.min()), float(values.max())

        def status_text(field: str, mapping: dict[str, str] | None = None) -> str:
            if field not in group:
                return "NOT_IDENTIFIABLE"
            values = [str(value) for value in group[field].dropna().unique()]
            if len(values) == 1:
                return mapping.get(values[0], values[0]) if mapping else values[0]
            return "MIXED_ANNUAL_STATES"

        metric_ranges = {}
        for field in (
            "recommended_clr",
            "capacity_base_mva",
            "positive_peak_base_mw",
            "pv_capacity_snapshot_mw",
            "pv_capacity_to_positive_peak_ratio",
            "reverse_peak_base_mw",
            "positive_capacity_gap_mw",
            "reverse_hosting_gap_mw",
            "positive_gap_device_count",
            "reverse_gap_device_count",
            "recommended_eac_wanyuan_per_year",
        ):
            low, high = interval(field)
            metric_ranges[f"{field}_min"] = low
            metric_ranges[f"{field}_max"] = high
        rows.append(
            {
                "region_id": region_id,
                "voltage_kv": voltage,
                "history_years": "2021-2025",
                "history_clr_min": hist_low,
                "history_clr_max": hist_high,
                "history_model_clr_min": float(model_observed.min()),
                "history_model_clr_max": float(model_observed.max()),
                **metric_ranges,
                "current_recommended_scheme_code": current_scheme,
                "current_recommended_action_mode": rec.get("recommended_action_mode", "NOT_IDENTIFIABLE"),
                "current_recommended_clr": rec_clr,
                "current_recommended_eac_wanyuan_per_year": rec.get("recommended_eac_wanyuan_per_year", np.nan),
                "measure_trigger_constraint": status_text("measure_trigger_constraint"),
                "final_recommendation_interval_low": package_low,
                "final_recommendation_interval_high": package_high,
                "interpretation": "五年官方静态容载比参考区间与2025当前成本最小可行方案的包络，不是未来阈值或历史回测",
                "evidence_grade": final_evidence,
                "quality_notes": "历史年份资产/时序/候选缺口按年度矩阵标记；2025推荐点沿用正式运行质量门禁",
                "source_ref": "annual_solution_modes.csv + 2025 county matrix",
                "source_version": "xuzhou-clr-project-output-v1",
                "transformation": "min/max of 2021-2025 official static CLR and current cost recommendation",
                "scenario_id": "final_recommendation_interval_2021_2025",
                "quality_flag": "historical_reference_plus_current_recommendation",
                "source_sha256": _frame_hash(history),
            }
        )
    return pd.DataFrame(rows).sort_values("region_id", kind="stable").reset_index(drop=True)
