"""2025 真实数据现状指标与设备级反向承载力。

县域正式容载比只使用 SRC08 的同电压等级公用变容量和正向同步峰值
锚点。站级年度极值仅形成静态边界，绝不冒充县域同步峰值。
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd
import yaml


BASELINE_VERSION = "1.0.0"
LINEAGE_FIELDS = (
    "source_ref",
    "source_version",
    "transformation",
    "scenario_id",
    "quality_flag",
    "source_sha256",
)


class RealMetricError(ValueError):
    """真实现状指标输入或冻结口径不满足。"""


class V3MetricError(RealMetricError):
    """v3 路径指标或物理红线不满足。"""


V3_FORMAL_PATHS = (
    "PATH_ACTUAL_2021_2025",
    "PATH_OPT_CLR_UNBOUNDED",
    "PATH_OPT_CLR_LE_2",
)
V3_LINEAGE_FIELDS = LINEAGE_FIELDS


def _aligned_numeric(value: Any, index: pd.Index, name: str) -> pd.Series:
    """把可选调度量按实际时序索引对齐，并拒绝隐式重排。"""
    if value is None:
        return pd.Series(0.0, index=index, name=name)
    series = value if isinstance(value, pd.Series) else pd.Series(value, index=index)
    if not series.index.equals(index):
        raise V3MetricError(f"{name} index must match actual net-load index")
    result = pd.to_numeric(series, errors="coerce").astype(float)
    if not np.isfinite(result.to_numpy()).all():
        raise V3MetricError(f"{name} contains non-finite values")
    return result.rename(name)


def validate_storage_dispatch(
    actual_net_load_mw: pd.Series,
    charge_mw: pd.Series | None = None,
    discharge_mw: pd.Series | None = None,
    *,
    tolerance_mw: float = 1e-9,
) -> None:
    """校验储能只处理本时段已有的反向/正向功率。

    正值是向上级电网受电，负值是反送。充电不能把反向功率推过零，放电不能
    把正向负荷推过零；同时充放电也不允许。该函数不接收光伏字段，源净负荷
    已经包含现状光伏时不会被二次扣减。
    """
    actual = _aligned_numeric(actual_net_load_mw, actual_net_load_mw.index, "actual_net_load_mw")
    charge = _aligned_numeric(charge_mw, actual.index, "charge_mw")
    discharge = _aligned_numeric(discharge_mw, actual.index, "discharge_mw")
    if (charge < -tolerance_mw).any() or (discharge < -tolerance_mw).any():
        raise V3MetricError("storage charge and discharge must be nonnegative")
    if ((charge > tolerance_mw) & (discharge > tolerance_mw)).any():
        raise V3MetricError("simultaneous charge and discharge are not allowed")
    reverse_surplus = (-actual).clip(lower=0.0)
    positive_load = actual.clip(lower=0.0)
    if (charge - reverse_surplus > tolerance_mw).any():
        raise V3MetricError("storage charge would cross zero")
    if (discharge - positive_load > tolerance_mw).any():
        raise V3MetricError("storage discharge would cause export")


def path_net_load(
    actual_net_load_mw: pd.Series,
    charge_mw: pd.Series | None = None,
    discharge_mw: pd.Series | None = None,
    tie_mw: pd.Series | None = None,
) -> pd.Series:
    """按冻结 v3 公式计算一条路径的净负荷。"""
    actual = _aligned_numeric(actual_net_load_mw, actual_net_load_mw.index, "actual_net_load_mw")
    charge = _aligned_numeric(charge_mw, actual.index, "charge_mw")
    discharge = _aligned_numeric(discharge_mw, actual.index, "discharge_mw")
    tie = _aligned_numeric(tie_mw, actual.index, "tie_mw")
    validate_storage_dispatch(actual, charge, discharge)
    return (actual + charge - discharge + tie).rename("p_net_mw")


def reverse_beta(
    capacities_mva: Sequence[float],
    *,
    operation_mode: str,
    split_beta: float = 0.8,
) -> float:
    """计算单台/分列或并列组的反向承载 beta，N-1 比例只应用一次。"""
    capacities = np.asarray(list(capacities_mva), dtype=float)
    if capacities.size == 0 or not np.isfinite(capacities).all() or (capacities <= 0).any():
        raise V3MetricError("reverse-beta capacities must be finite and positive")
    if not 0.0 < float(split_beta) <= 1.0:
        raise V3MetricError("split_beta must be in (0, 1]")
    mode = str(operation_mode).strip().lower()
    if mode in {"split", "single"}:
        return float(split_beta)
    if mode == "parallel":
        total = float(capacities.sum())
        largest = float(capacities.max())
        return float(min(float(split_beta), (total - largest) / total))
    raise V3MetricError(f"unknown operation mode for reverse beta: {operation_mode!r}")


def _trigger_constraints(positive_gap: float, reverse_gap: float, tolerance_mw: float) -> str:
    constraints: list[str] = []
    if positive_gap > tolerance_mw:
        constraints.append("positive_capacity_gap")
    if reverse_gap > tolerance_mw:
        constraints.append("reverse_hosting_gap")
    return ";".join(constraints) if constraints else "none"


def compute_path_metrics(
    frame: pd.DataFrame,
    *,
    path_id: str,
    timestamp_col: str = "timestamp",
    group_cols: Sequence[str] = ("region_id", "voltage_kv"),
    asset_id_col: str = "transformer_uid",
    actual_col: str = "p_actual_mw",
    charge_col: str = "p_charge_mw",
    discharge_col: str = "p_discharge_mw",
    tie_col: str = "p_tie_mw",
    capacity_col: str = "capacity_mva",
    operation_mode_col: str = "operation_mode",
    cos_phi: float = 0.95,
    split_beta: float = 0.8,
    tolerance_mw: float = 1e-9,
) -> pd.DataFrame:
    """计算路径自身的同步正/反向峰值、CLR和设备级缺口。

    输入是设备逐时长表。先按时间和县区/电压聚合，再取峰值；因此不会把
    静态站级极值相加冒充同步峰值。每条路径都从自己的 ``p_net_mw`` 重新取
    ``p_plus_mw``，储能或联络措施可以改变正式 CLR 分母。
    """
    if path_id not in V3_FORMAL_PATHS:
        raise V3MetricError(f"unknown formal path: {path_id}")
    if not 0.0 < float(cos_phi) <= 1.0:
        raise V3MetricError("cos_phi must be in (0, 1]")
    group_cols = tuple(group_cols)
    required = {
        timestamp_col,
        *group_cols,
        asset_id_col,
        actual_col,
        capacity_col,
        operation_mode_col,
    }
    missing = required - set(frame.columns)
    if missing:
        raise V3MetricError(f"path frame missing columns {sorted(missing)}")
    data = frame.copy()
    data[timestamp_col] = pd.to_datetime(data[timestamp_col], errors="raise")
    for column in (actual_col, capacity_col):
        data[column] = pd.to_numeric(data[column], errors="coerce")
        if data[column].isna().any() or not np.isfinite(data[column].to_numpy()).all():
            raise V3MetricError(f"{column} contains non-finite values")
    if (data[capacity_col] <= 0).any():
        raise V3MetricError("capacity_mva must be positive")
    if data.duplicated([timestamp_col, *group_cols, asset_id_col]).any():
        raise V3MetricError("path frame has duplicate asset timestamps")
    actual = pd.Series(data[actual_col].to_numpy(float), index=data.index)
    charge = _aligned_numeric(data[charge_col] if charge_col in data else None, data.index, charge_col)
    discharge = _aligned_numeric(data[discharge_col] if discharge_col in data else None, data.index, discharge_col)
    tie = _aligned_numeric(data[tie_col] if tie_col in data else None, data.index, tie_col)
    validate_storage_dispatch(actual, charge, discharge, tolerance_mw=tolerance_mw)
    data["p_net_mw"] = (actual + charge - discharge + tie).to_numpy()
    data["p_charge_mw"] = charge.to_numpy()
    data["p_discharge_mw"] = discharge.to_numpy()

    aggregate_keys = [timestamp_col, *group_cols]
    aggregate = data.groupby(aggregate_keys, as_index=False, sort=True)["p_net_mw"].sum()
    peaks = (
        aggregate.groupby(list(group_cols), as_index=False, sort=True)["p_net_mw"]
        .agg(
            p_plus_mw=lambda values: float(values.clip(lower=0).max()),
            p_minus_mw=lambda values: float((-values).clip(lower=0).max()),
        )
    )
    static_keys = [*group_cols, asset_id_col]
    static = data.sort_values([*static_keys, timestamp_col], kind="stable").drop_duplicates(static_keys)
    capacity = static.groupby(list(group_cols), as_index=False)[capacity_col].sum().rename(
        columns={capacity_col: "capacity_mva"}
    )
    device = data.groupby(static_keys, as_index=False, sort=True).agg(
        forward_peak_mw=("p_net_mw", lambda values: float(values.clip(lower=0).max())),
        reverse_peak_mw=("p_net_mw", lambda values: float((-values).clip(lower=0).max())),
    )
    device = device.merge(static[static_keys + [capacity_col, operation_mode_col]], on=static_keys, how="left", validate="one_to_one")
    device["forward_limit_mw"] = device[capacity_col] * float(cos_phi)
    device["reverse_beta"] = float(split_beta)
    for key, members in device.groupby(list(group_cols), sort=False):
        indices = members.index
        modes = {str(value).strip().lower() for value in members[operation_mode_col].dropna()}
        mode = "parallel" if "parallel" in modes else "split"
        beta = reverse_beta(members[capacity_col].tolist(), operation_mode=mode, split_beta=split_beta)
        device.loc[indices, "reverse_beta"] = beta
    device["reverse_limit_mw"] = device[capacity_col] * float(cos_phi) * device["reverse_beta"]
    device["positive_gap_mw"] = (device["forward_peak_mw"] - device["forward_limit_mw"]).clip(lower=0)
    device["reverse_gap_mw"] = (device["reverse_peak_mw"] - device["reverse_limit_mw"]).clip(lower=0)
    gaps = device.groupby(list(group_cols), as_index=False).agg(
        positive_capacity_gap_mw=("positive_gap_mw", "sum"),
        reverse_hosting_gap_mw=("reverse_gap_mw", "sum"),
        positive_gap_device_count=("positive_gap_mw", lambda values: int((values > tolerance_mw).sum())),
        reverse_gap_device_count=("reverse_gap_mw", lambda values: int((values > tolerance_mw).sum())),
    )
    result = peaks.merge(capacity, on=list(group_cols), validate="one_to_one").merge(
        gaps, on=list(group_cols), validate="one_to_one"
    )
    result["path_id"] = path_id
    result["clr"] = result["capacity_mva"] / result["p_plus_mw"].replace(0.0, np.nan)
    result["clr"] = result["clr"].fillna(np.inf)
    result["measure_trigger_constraint"] = [
        _trigger_constraints(float(positive), float(reverse), tolerance_mw)
        for positive, reverse in zip(
            result["positive_capacity_gap_mw"], result["reverse_hosting_gap_mw"], strict=True
        )
    ]
    return result[[
        "path_id",
        *group_cols,
        "capacity_mva",
        "p_plus_mw",
        "p_minus_mw",
        "clr",
        "positive_capacity_gap_mw",
        "reverse_hosting_gap_mw",
        "positive_gap_device_count",
        "reverse_gap_device_count",
        "measure_trigger_constraint",
    ]].sort_values(list(group_cols), kind="stable").reset_index(drop=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _combined_hash(paths: Iterable[Path]) -> str:
    payload = {path.name: _sha256(path) for path in sorted(paths, key=lambda p: p.name)}
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _read_required(root: Path, filename: str, columns: Iterable[str]) -> pd.DataFrame:
    path = root / filename
    if not path.is_file():
        raise RealMetricError(f"required processed table missing: {path}")
    frame = pd.read_csv(path)
    missing = set(columns) - set(frame.columns)
    if missing:
        raise RealMetricError(f"{filename}: missing columns {sorted(missing)}")
    return frame


def _lineage(
    source_ref: str,
    source_version: str,
    transformation: str,
    quality_flag: str,
    source_sha256: str,
) -> dict[str, str]:
    return {
        "source_ref": source_ref,
        "source_version": source_version,
        "transformation": transformation,
        "scenario_id": "real_2025_baseline",
        "quality_flag": quality_flag,
        "source_sha256": source_sha256,
    }


def _write_frame(path: Path, frame: pd.DataFrame, sort_by: list[str]) -> None:
    if frame.empty:
        raise RealMetricError(f"{path.name}: refusing to write empty table")
    missing = set(LINEAGE_FIELDS) - set(frame.columns)
    if missing:
        raise RealMetricError(f"{path.name}: missing lineage columns {sorted(missing)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.sort_values(sort_by, kind="stable").reset_index(drop=True).to_csv(
        path,
        index=False,
        lineterminator="\n",
        float_format="%.10g",
    )


def _approved_hourly_gate(processed_root: Path) -> bool:
    path = processed_root / "timeseries_column_map_2025.csv"
    if not path.is_file():
        return False
    mapping = pd.read_csv(path)
    if len(mapping) != 58 or "formal_use_allowed" not in mapping:
        return False
    allowed = mapping["formal_use_allowed"]
    if allowed.dtype != bool:
        allowed = allowed.astype(str).str.lower().eq("true")
    counts = mapping.groupby("voltage_kv").size().to_dict()
    return bool(allowed.all() and counts == {35: 16, 110: 42})


def _transformer_metrics(
    master: pd.DataFrame,
    static: pd.DataFrame,
    cos_phi: float,
    split_beta: float,
    source_version: str,
    lineage_hash: str,
) -> pd.DataFrame:
    load_columns = [
        "transformer_uid",
        "annual_max_net_load_mw",
        "annual_min_net_load_mw",
    ]
    merged = master.merge(static[load_columns], on="transformer_uid", how="left", validate="1:1")
    merged["forward_peak_static_mw"] = merged["annual_max_net_load_mw"].clip(lower=0)
    merged["reverse_peak_static_mw"] = (-merged["annual_min_net_load_mw"]).clip(lower=0)
    merged["forward_limit_mw"] = merged["capacity_mva"] * cos_phi
    merged["reverse_beta_split"] = split_beta
    merged["reverse_limit_split_mw"] = merged["capacity_mva"] * cos_phi * split_beta
    merged["forward_gap_static_mw"] = (
        merged["forward_peak_static_mw"] - merged["forward_limit_mw"]
    ).clip(lower=0)
    merged["reverse_gap_split_static_mw"] = (
        merged["reverse_peak_static_mw"] - merged["reverse_limit_split_mw"]
    ).clip(lower=0)
    keep = [
        "region_id",
        "voltage_kv",
        "station_id",
        "transformer_uid",
        "unit_id",
        "capacity_mva",
        "operation_mode",
        "forward_peak_static_mw",
        "reverse_peak_static_mw",
        "forward_limit_mw",
        "reverse_beta_split",
        "reverse_limit_split_mw",
        "forward_gap_static_mw",
        "reverse_gap_split_static_mw",
    ]
    result = merged[keep].copy()
    lineage = _lineage(
        "transformer_master.csv+transformer_static_load.csv",
        source_version,
        "apply device-level forward S*cos(phi) and split/single reverse 0.8*S*cos(phi)",
        "static_device_screen_not_synchronous",
        lineage_hash,
    )
    for key, value in lineage.items():
        result[key] = value
    return result


def _station_metrics(
    master: pd.DataFrame,
    station_static: pd.DataFrame,
    cos_phi: float,
    split_beta: float,
    source_version: str,
    lineage_hash: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    keys = ["region_id", "voltage_kv", "station_id"]
    static_lookup = station_static.set_index(keys)
    for key, units in master.groupby(keys, sort=True):
        region_id, voltage_kv, station_id = key
        capacities = units["capacity_mva"].astype(float)
        total = float(capacities.sum())
        largest = float(capacities.max())
        count = int(len(units))
        parallel_beta = split_beta if count == 1 else min(split_beta, (total - largest) / total)
        split_limit = split_beta * total * cos_phi
        parallel_limit = parallel_beta * total * cos_phi
        if key in static_lookup.index:
            load = static_lookup.loc[key]
            if isinstance(load, pd.DataFrame):
                raise RealMetricError(f"duplicate station_static_load key: {key}")
            forward_peak = max(float(load["annual_max_net_load_mw"]), 0.0)
            reverse_peak = max(-float(load["annual_min_net_load_mw"]), 0.0)
        else:
            forward_peak = float("nan")
            reverse_peak = float("nan")
        known_modes = {str(value).lower() for value in units["operation_mode"].dropna()}
        if count == 1:
            assessment = "single_transformer_split_rule"
        elif known_modes == {"split"}:
            assessment = "split"
        elif known_modes == {"parallel"}:
            assessment = "parallel"
        else:
            assessment = "split_parallel_sensitivity_interval"
        rows.append(
            {
                "region_id": region_id,
                "voltage_kv": int(voltage_kv),
                "station_id": station_id,
                "transformer_count": count,
                "capacity_year_end_mva": total,
                "largest_transformer_mva": largest,
                "forward_peak_static_mw": forward_peak,
                "reverse_peak_static_mw": reverse_peak,
                "forward_limit_mw": total * cos_phi,
                "reverse_beta_split": split_beta,
                "reverse_beta_parallel": parallel_beta,
                "reverse_limit_split_mw": split_limit,
                "reverse_limit_parallel_mw": parallel_limit,
                "reverse_limit_lower_mw": min(split_limit, parallel_limit),
                "reverse_limit_upper_mw": max(split_limit, parallel_limit),
                "reverse_gap_split_static_mw": max(reverse_peak - split_limit, 0.0)
                if pd.notna(reverse_peak)
                else float("nan"),
                "reverse_gap_parallel_static_mw": max(reverse_peak - parallel_limit, 0.0)
                if pd.notna(reverse_peak)
                else float("nan"),
                "operation_mode_assessment": assessment,
            }
        )
    result = pd.DataFrame(rows)
    lineage = _lineage(
        "transformer_master.csv+station_static_load.csv",
        source_version,
        "report split and parallel reverse-capacity scenarios; parallel beta includes N-1 ratio once",
        "static_station_bounds_operation_mode_sensitivity",
        lineage_hash,
    )
    for key, value in lineage.items():
        result[key] = value
    return result


def _evidence_grade(region_id: str, voltage_kv: int, hourly_approved: bool) -> str:
    if region_id == "QX-00005" and not hourly_approved:
        return "C"
    if voltage_kv == 35:
        # SRC03 only provides 110-kV discrete expansion candidates; the auxiliary
        # 35-kV result therefore retains a candidate/parent-mapping gap.
        return "C"
    return "B"


def _county_metrics(
    reference: pd.DataFrame,
    stations: pd.DataFrame,
    pv: pd.DataFrame,
    hourly_approved: bool,
    source_version: str,
    lineage_hash: str,
) -> pd.DataFrame:
    equipment = (
        stations.groupby(["region_id", "voltage_kv"], as_index=False)
        .agg(
            capacity_year_end_equipment_mva=("capacity_year_end_mva", "sum"),
            station_count_equipment=("station_id", "nunique"),
            positive_peak_static_upper_bound_mw=("forward_peak_static_mw", "sum"),
            reverse_peak_static_lower_bound_mw=("reverse_peak_static_mw", "max"),
            reverse_peak_static_upper_bound_mw=("reverse_peak_static_mw", "sum"),
            reverse_gap_split_static_mw=("reverse_gap_split_static_mw", "sum"),
            reverse_gap_parallel_static_mw=("reverse_gap_parallel_static_mw", "sum"),
        )
    )
    pv_sum = (
        pv.groupby(["region_id", "voltage_kv"], as_index=False)[["pv_online_mw", "pv_pipeline_mw"]]
        .sum()
        .rename(columns={"pv_online_mw": "pv_capacity_snapshot_mw"})
    )
    result = reference.merge(
        equipment, on=["region_id", "voltage_kv"], how="left", validate="1:1"
    ).merge(pv_sum, on=["region_id", "voltage_kv"], how="left", validate="1:1")
    result["pv_capacity_snapshot_mw"] = result["pv_capacity_snapshot_mw"].fillna(0.0)
    result["pv_pipeline_mw"] = result["pv_pipeline_mw"].fillna(0.0)
    result["asset_scope_id"] = "operating_2025"
    result["capacity_base_mva"] = result["capacity_mva"].astype(float)
    result["positive_peak_base_mw"] = result["positive_peak_anchor_mw"].astype(float)
    result["reverse_peak_base_mw"] = float("nan")
    result["reverse_peak_basis"] = "static_station_extrema_bounds_not_synchronous_peak"
    result["clr_model_base"] = result["capacity_base_mva"] / result["positive_peak_base_mw"]
    result["clr_official_reference"] = result["official_clr_reference"]
    result["equipment_capacity_gap_mva"] = (
        result["capacity_year_end_equipment_mva"] - result["capacity_base_mva"]
    )
    result["pv_capacity_snapshot_year"] = 2026
    result["pv_capacity_to_capacity_ratio"] = (
        result["pv_capacity_snapshot_mw"] / result["capacity_base_mva"]
    )
    result["pv_capacity_to_positive_peak_ratio"] = (
        result["pv_capacity_snapshot_mw"] / result["positive_peak_base_mw"]
    )
    result["evidence_grade"] = [
        _evidence_grade(str(region), int(voltage), hourly_approved)
        for region, voltage in zip(result["region_id"], result["voltage_kv"], strict=True)
    ]
    result["quality_notes"] = [
        (
            "2025 transformer-hour map is not source-owner approved; reverse static extrema are "
            "bounds, not synchronous county peaks; 2026 PV is context only"
            if region == "QX-00005" and not hourly_approved
            else "reverse static extrema are bounds, not synchronous county peaks; 2026 PV is context only"
        )
        for region in result["region_id"]
    ]
    keep = [
        "region_id",
        "voltage_kv",
        "evidence_grade",
        "asset_scope_id",
        "capacity_base_mva",
        "capacity_year_end_equipment_mva",
        "equipment_capacity_gap_mva",
        "station_count_equipment",
        "positive_peak_base_mw",
        "positive_peak_static_upper_bound_mw",
        "reverse_peak_base_mw",
        "reverse_peak_static_lower_bound_mw",
        "reverse_peak_static_upper_bound_mw",
        "reverse_peak_basis",
        "reverse_gap_split_static_mw",
        "reverse_gap_parallel_static_mw",
        "clr_model_base",
        "clr_official_reference",
        "pv_capacity_snapshot_mw",
        "pv_pipeline_mw",
        "pv_capacity_snapshot_year",
        "pv_capacity_to_capacity_ratio",
        "pv_capacity_to_positive_peak_ratio",
        "quality_notes",
    ]
    result = result[keep].copy()
    lineage = _lineage(
        "county_clr_reference.csv+station_static_load.csv+transformer_master.csv+station_pv_snapshot.csv",
        source_version,
        "use official same-voltage operating capacity and positive synchronous peak anchor; aggregate static extrema as explicit bounds only",
        "official_positive_anchor_static_reverse_bounds",
        lineage_hash,
    )
    for key, value in lineage.items():
        result[key] = value
    return result


def build_real_baseline(
    processed_root: Path,
    output_dir: Path,
    contract_path: Path,
) -> dict[str, Any]:
    """生成设备、站级和县域 2025 现状基线。"""
    processed_root = Path(processed_root).resolve()
    output_dir = Path(output_dir).resolve()
    contract_path = Path(contract_path).resolve()
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if contract["contract"]["version"] != "2.0.0":
        raise RealMetricError("real baseline requires model contract 2.0.0")
    cos_phi = float(contract["technical_parameters"]["cos_phi"]["baseline"])
    split_beta = float(contract["technical_parameters"]["reverse_beta"]["split_or_single"])

    required_paths = [
        processed_root / "transformer_master.csv",
        processed_root / "transformer_static_load.csv",
        processed_root / "station_static_load.csv",
        processed_root / "county_clr_reference.csv",
        processed_root / "station_pv_snapshot.csv",
    ]
    master = _read_required(
        processed_root,
        "transformer_master.csv",
        ["transformer_uid", "region_id", "voltage_kv", "station_id", "capacity_mva", "operation_mode"],
    )
    transformer_static = _read_required(
        processed_root,
        "transformer_static_load.csv",
        ["transformer_uid", "annual_max_net_load_mw", "annual_min_net_load_mw"],
    )
    station_static = _read_required(
        processed_root,
        "station_static_load.csv",
        ["region_id", "voltage_kv", "station_id", "annual_max_net_load_mw", "annual_min_net_load_mw"],
    )
    reference = _read_required(
        processed_root,
        "county_clr_reference.csv",
        ["region_id", "voltage_kv", "capacity_mva", "positive_peak_anchor_mw", "official_clr_reference"],
    )
    pv = _read_required(
        processed_root,
        "station_pv_snapshot.csv",
        ["region_id", "voltage_kv", "station_id", "pv_online_mw", "pv_pipeline_mw"],
    )
    source_versions = sorted(
        set(master["source_version"].dropna().astype(str))
        | set(reference["source_version"].dropna().astype(str))
    )
    source_version = "+".join(source_versions)
    lineage_hash = _combined_hash(required_paths)
    hourly_approved = _approved_hourly_gate(processed_root)

    transformer_result = _transformer_metrics(
        master, transformer_static, cos_phi, split_beta, source_version, lineage_hash
    )
    station_result = _station_metrics(
        master, station_static, cos_phi, split_beta, source_version, lineage_hash
    )
    county_result = _county_metrics(
        reference, station_result, pv, hourly_approved, source_version, lineage_hash
    )
    if len(county_result) != 16:
        raise RealMetricError(f"county baseline must contain 16 voltage-separated rows, got {len(county_result)}")
    if county_result[["region_id", "voltage_kv"]].duplicated().any():
        raise RealMetricError("county baseline has duplicate region-voltage keys")

    output_dir.mkdir(parents=True, exist_ok=True)
    frames = {
        "transformer_reverse_capacity.csv": (
            transformer_result,
            ["region_id", "voltage_kv", "station_id", "unit_id"],
        ),
        "station_baseline.csv": (
            station_result,
            ["region_id", "voltage_kv", "station_id"],
        ),
        "county_baseline.csv": (county_result, ["voltage_kv", "region_id"]),
    }
    for filename, (frame, keys) in frames.items():
        _write_frame(output_dir / filename, frame, keys)
    output_files = {
        filename: {"sha256": _sha256(output_dir / filename), "rows": int(len(frame))}
        for filename, (frame, _keys) in sorted(frames.items())
    }
    manifest: dict[str, Any] = {
        "baseline_version": BASELINE_VERSION,
        "contract_version": contract["contract"]["version"],
        "contract_sha256": _sha256(contract_path),
        "input_fingerprint": lineage_hash,
        "hourly_mapping_approved": hourly_approved,
        "cos_phi": cos_phi,
        "split_beta": split_beta,
        "output_files": output_files,
    }
    (output_dir / "baseline_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
