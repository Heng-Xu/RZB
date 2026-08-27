"""v3.2 站级正向/反向物理缺口诊断。

旧 v3.1 ``_physical_gap_matrix`` 按单台主变静态极值直接使用固定
``0.95*0.8*S``，而终态时序门禁按变电站主变组合与运行方式计算限额，
两者可能产生触发原因与最终措施不一致。本模块统一到站级运行方式口径。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.milp_planner import _operation_limits


class V32PhysicsError(ValueError):
    pass


def _parse_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def build_station_gap_diagnostics(
    processed_root: Path,
    contract: dict[str, Any],
    *,
    cos_phi: float | None = None,
    reverse_beta: float | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """返回 2025 站级缺口明细与片区/电压聚合诊断。

    静态极值只用于诊断；最终工程措施可行性仍由 v3_time_physics 的站级
    时序回放决定，避免把静态诊断再叠加成第二套强制措施约束。
    """
    root = Path(processed_root)
    master_path = root / "transformer_master.csv"
    whitelist_path = root / "annual_asset_whitelist.csv"
    static_path = root / "station_static_load.csv"
    for path in (master_path, whitelist_path, static_path):
        if not path.is_file():
            raise V32PhysicsError(f"required input missing: {path}")

    master = pd.read_csv(master_path)
    whitelist = pd.read_csv(whitelist_path)
    static = pd.read_csv(static_path)
    operating = whitelist[
        whitelist["year"].eq(2025)
        & whitelist["asset_scope_id"].eq("operating_2025")
        & _parse_bool(whitelist["in_annual_operating_whitelist"])
    ][["transformer_uid"]]
    equipment = master.merge(
        operating,
        on="transformer_uid",
        how="inner",
        validate="one_to_one",
    )
    if equipment.empty:
        raise V32PhysicsError("2025 operating transformer scope is empty")

    power_factor = (
        float(contract["technical_parameters"]["cos_phi"]["baseline"])
        if cos_phi is None
        else float(cos_phi)
    )
    beta = (
        float(contract["technical_parameters"]["reverse_beta"]["split_or_single"])
        if reverse_beta is None
        else float(reverse_beta)
    )
    if not (0 < power_factor <= 1):
        raise V32PhysicsError("cos_phi must be in (0,1]")
    if not (0 <= beta <= 1):
        raise V32PhysicsError("reverse_beta must be in [0,1]")

    static = static.copy()
    static["region_id"] = static["region_id"].astype(str)
    static["station_id"] = static["station_id"].astype(str)
    static_lookup = static.set_index(["region_id", "voltage_kv", "station_id"])
    rows: list[dict[str, Any]] = []
    for (region_id, voltage_kv, station_id), group in equipment.groupby(
        ["region_id", "voltage_kv", "station_id"], sort=True
    ):
        key = (str(region_id), int(voltage_kv), str(station_id))
        if key not in static_lookup.index:
            rows.append(
                {
                    "region_id": key[0],
                    "voltage_kv": key[1],
                    "station_id": key[2],
                    "forward_limit_mw": float("nan"),
                    "reverse_limit_mw": float("nan"),
                    "annual_max_net_load_mw": float("nan"),
                    "annual_min_net_load_mw": float("nan"),
                    "positive_gap_mw": float("nan"),
                    "reverse_gap_mw": float("nan"),
                    "diagnostic_status": "missing_station_static_extrema",
                }
            )
            continue
        record = static_lookup.loc[key]
        if isinstance(record, pd.DataFrame):
            raise V32PhysicsError(f"duplicate station static rows: {key}")
        capacities = pd.to_numeric(group["capacity_mva"], errors="raise").tolist()
        modes = set(group["operation_mode"].dropna().astype(str).str.lower())
        forward_limit, reverse_limit = _operation_limits(
            capacities,
            modes,
            power_factor,
            beta,
        )
        pmax = float(record["annual_max_net_load_mw"])
        pmin = float(record["annual_min_net_load_mw"])
        positive_gap = max(pmax, 0.0) - forward_limit
        reverse_peak = max(-pmin, 0.0)
        reverse_gap = reverse_peak - reverse_limit
        rows.append(
            {
                "region_id": key[0],
                "voltage_kv": key[1],
                "station_id": key[2],
                "forward_limit_mw": forward_limit,
                "reverse_limit_mw": reverse_limit,
                "annual_max_net_load_mw": pmax,
                "annual_min_net_load_mw": pmin,
                "positive_gap_mw": max(positive_gap, 0.0),
                "reverse_gap_mw": max(reverse_gap, 0.0),
                "positive_gap": bool(positive_gap > 1e-9),
                "reverse_gap": bool(reverse_gap > 1e-9),
                "cos_phi": power_factor,
                "reverse_beta": beta,
                "operation_modes": ";".join(sorted(modes)) or "unknown",
                "unit_count": int(len(group)),
                "diagnostic_status": "station_operation_mode_aligned",
            }
        )

    station = pd.DataFrame(rows)
    valid = station[station["diagnostic_status"].eq("station_operation_mode_aligned")].copy()
    if valid.empty:
        raise V32PhysicsError("no valid station-level physical gap diagnostics")
    summary = valid.groupby(["region_id", "voltage_kv"], as_index=False).agg(
        positive_capacity_gap_mw=("positive_gap_mw", "sum"),
        reverse_hosting_gap_mw=("reverse_gap_mw", "sum"),
        positive_gap_device_count=("positive_gap", "sum"),
        reverse_gap_device_count=("reverse_gap", "sum"),
        station_count=("station_id", "nunique"),
    )
    summary["measure_trigger_constraint"] = summary.apply(
        lambda row: ";".join(
            item
            for item, condition in (
                ("positive_capacity_gap", float(row["positive_capacity_gap_mw"]) > 1e-9),
                ("reverse_hosting_gap", float(row["reverse_hosting_gap_mw"]) > 1e-9),
            )
            if condition
        )
        or "none",
        axis=1,
    )
    summary["diagnostic_basis"] = (
        "2025 station static extrema + operating transformer group + operation-mode-aligned limits"
    )
    summary["cos_phi"] = power_factor
    summary["reverse_beta"] = beta
    return station, summary
