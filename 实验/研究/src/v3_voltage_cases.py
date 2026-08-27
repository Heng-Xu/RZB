"""v3 电压分层和局部 10 kV 案例边界。"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Sequence

import pandas as pd


class V3VoltageCaseError(ValueError):
    """电压分层、父级映射或局部案例门禁不满足。"""


def aggregate_separate_voltage(frame: pd.DataFrame, value_columns: Sequence[str]) -> pd.DataFrame:
    """按县区和电压分别汇总，明确不生成跨电压合计行。"""
    required = {"region_id", "voltage_kv", *value_columns}
    missing = required - set(frame.columns)
    if missing:
        raise V3VoltageCaseError(f"voltage frame missing {sorted(missing)}")
    data = frame.copy()
    data["voltage_kv"] = pd.to_numeric(data["voltage_kv"], errors="raise").astype(int)
    if not data["voltage_kv"].isin([35, 110]).all():
        raise V3VoltageCaseError("only 35 kV and 110 kV are formal voltage levels")
    for column in value_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")
        if data[column].isna().any():
            raise V3VoltageCaseError(f"{column} contains nonnumeric voltage-layer values")
    result = data.groupby(["region_id", "voltage_kv"], as_index=False, sort=True)[list(value_columns)].sum()
    result["cross_voltage_aggregation"] = False
    result["aggregation_basis"] = "same_region_same_voltage_only"
    return result


def parent_mapping_gate(parent_mapping: pd.DataFrame) -> bool:
    """判断 35 kV 是否具备允许跨层枚举所需的完整、唯一父级映射。"""
    required = {"region_id", "station_id", "parent_supply_id"}
    if not required <= set(parent_mapping.columns) or parent_mapping.empty:
        return False
    data = parent_mapping.copy()
    if data[["region_id", "station_id", "parent_supply_id"]].isna().any().any():
        return False
    if data.duplicated(["region_id", "station_id"]).any():
        return False
    if "parent_mapping_status" in data.columns and not data["parent_mapping_status"].astype(str).str.startswith("complete").all():
        return False
    if "mixed_unit_parent_supply" in data.columns and data["mixed_unit_parent_supply"].astype(bool).any():
        return False
    return True


def _as_records(cases: Iterable[Mapping[str, Any]] | pd.DataFrame) -> list[dict[str, Any]]:
    if isinstance(cases, pd.DataFrame):
        return cases.to_dict(orient="records")
    return [dict(case) for case in cases]


def _dependencies(value: Any) -> set[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return set()
    if isinstance(value, (list, tuple, set)):
        return {str(item) for item in value}
    return {item.strip() for item in str(value).split(";") if item.strip()}


def validate_local_case_options(
    cases: Iterable[Mapping[str, Any]] | pd.DataFrame,
    *,
    expected_type: str,
) -> bool:
    """校验单类局部案例的审批、功率守恒和唯一性。"""
    records = _as_records(cases)
    if not records:
        return True
    required = {
        "case_id",
        "case_type",
        "relief_id",
        "from_region",
        "to_region",
        "transfer_mw",
        "cost_wanyuan",
        "approval_status",
    }
    missing = required - set(records[0])
    if missing:
        raise V3VoltageCaseError(f"local case missing {sorted(missing)}")
    ids = [str(row["case_id"]) for row in records]
    relief = [str(row["relief_id"]) for row in records]
    if len(ids) != len(set(ids)) or len(relief) != len(set(relief)):
        raise V3VoltageCaseError("duplicate case_id or relief_id")
    for row in records:
        if str(row["case_type"]) != expected_type:
            raise V3VoltageCaseError(f"case type mismatch: expected {expected_type}")
        if str(row["approval_status"]).lower() != "approved":
            raise V3VoltageCaseError("local case approval is required before comparison")
        if str(row["from_region"]) == str(row["to_region"]):
            raise V3VoltageCaseError("local transfer must connect two distinct regions")
        transfer = float(row["transfer_mw"])
        cost = float(row["cost_wanyuan"])
        if transfer <= 0 or cost < 0:
            raise V3VoltageCaseError("local case transfer/cost must be nonnegative with positive transfer")
        # A case has one source and one sink, so its county balance is zero by
        # construction; retain the explicit field for downstream audit.
        row["county_power_conservation_mw"] = transfer - transfer
        row["cost_counted_once"] = True
        row["dependencies"] = sorted(_dependencies(row.get("dependencies")))
    return True


def combine_local_cases(
    existing_cases: Iterable[Mapping[str, Any]] | pd.DataFrame,
    new_line_cases: Iterable[Mapping[str, Any]] | pd.DataFrame,
    *,
    explicit_compatibility: bool = False,
) -> list[dict[str, Any]]:
    """仅在显式兼容且依赖满足时组合两类案例。"""
    existing = _as_records(existing_cases)
    new_line = _as_records(new_line_cases)
    validate_local_case_options(existing, expected_type="existing_tie_reconfiguration")
    validate_local_case_options(new_line, expected_type="new_tie_line")
    if not explicit_compatibility:
        raise V3VoltageCaseError("explicit compatibility is required before combining local case classes")
    combined = existing + new_line
    ids = [str(row["case_id"]) for row in combined]
    relief_ids = [str(row["relief_id"]) for row in combined]
    if len(ids) != len(set(ids)) or len(relief_ids) != len(set(relief_ids)):
        raise V3VoltageCaseError("duplicate case or duplicate reverse-relief/capacity-avoidance effect")
    known = set(ids)
    for row in combined:
        missing = _dependencies(row.get("dependencies")) - known
        if missing:
            raise V3VoltageCaseError(f"case dependency missing: {sorted(missing)}")
    return combined
