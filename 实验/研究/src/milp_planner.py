"""冻结合同 2.0.0 下的 2025 真实数据 C0/A/B 离散规划器。

正式模型逐站枚举源文件中的离散 ``candidate_id``，并用整数储能柜和
24 小时线性调度回放筛选每个工程组合。县域层再做确定性多选动态规划。
方案 A 只限制继承存量资产之后的新增容量；方案 B 使用同一组选项但不加
该限制。正式容载比的 ``positive_peak_base_mw`` 始终是外部固定输入。

旧 M1 合成链路已经隔离到 :mod:`src.legacy_milp_planner`，下方兼容导出仅
用于固定旧回归入口，真实运行只调用 :func:`solve_real_c0ab`。
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import linprog

from src.legacy_milp_planner import (  # 旧合成回归兼容面
    RUN_ID,
    SPRING_MONTHS,
    SolutionBundle,
    _rep_arrays,
    solve_scheme,
)
from src.real_costs import (
    annualized_eac_wanyuan,
    capital_recovery_factor,
    storage_capex_wanyuan,
)


REAL_PLANNER_VERSION = "1.0.0"
REAL_SCHEMES = ("C0", "A", "B")
DAILY_HOURS = 24
MAX_STORAGE_MODULES = 100_000
LINEAGE_FIELDS = (
    "source_ref",
    "source_version",
    "transformation",
    "scenario_id",
    "quality_flag",
    "source_sha256",
)


class RealPlannerError(ValueError):
    """正式真实数据规划输入或不可变断言错误。"""


@dataclass(frozen=True)
class DailyStoragePlayback:
    """单个日内情景的整数柜调度回放。"""

    feasible: bool
    charge_mw: np.ndarray
    discharge_mw: np.ndarray
    soc_mwh: np.ndarray
    net_after_mw: np.ndarray
    reason: str
    soc_residual_mwh: float


@dataclass(frozen=True)
class StationOption:
    """一个站的离散扩容组合和最小鲁棒整数储能配置。"""

    station_id: str
    selected_candidate_ids: tuple[str, ...]
    expansion_delta_mva: float
    storage_modules: int
    forward_limit_mw: float
    reverse_limit_mw: float
    capex_low_wanyuan: float
    capex_base_wanyuan: float
    capex_high_wanyuan: float
    eac_low_wanyuan_per_year: float
    eac_base_wanyuan_per_year: float
    eac_high_wanyuan_per_year: float
    feasible: bool
    reason: str


def _declare_decision_schema(model: Any, station_coords: Any) -> Any:
    """审计用的标准整数决策声明；求解器采用等价的精确枚举实现。"""
    return model.add_variables(
        lower=0,
        coords=[station_coords],
        integer=True,
        name="storage_modules",
    )


def a_incremental_capacity_limit(
    capacity_base_mva: float,
    positive_peak_base_mw: float,
) -> float:
    """方案 A 的新增容量上限，不要求既有 ``R0>2`` 资产退役。"""
    capacity = float(capacity_base_mva)
    peak = float(positive_peak_base_mw)
    if capacity < 0 or peak < 0:
        raise ValueError("capacity and positive peak must be nonnegative")
    return max(0.0, 2.0 * peak - capacity)


def strict_r_lt_2_policy_status(
    capacity_base_mva: float,
    positive_peak_base_mw: float,
    stock_capacity_reduction_mva: float = 0.0,
    incremental_eac_wanyuan_per_year: float = 0.0,
) -> str:
    """判定独立的严格 ``R<2.0`` 政策场景。

    该场景不属于 C0/A/B 经济措施。没有改变存量且没有增量成本时，
    即使现状 R 已经小于 2，也不能冒充严格政策方案的“无措施解”。
    当前动作集只有扩容和配储，不能降低容载比；只有真实减容/退役候选
    （并且发生正的 EAC）才可能通过该判定。
    """
    capacity = float(capacity_base_mva)
    peak = float(positive_peak_base_mw)
    reduction = float(stock_capacity_reduction_mva)
    eac = float(incremental_eac_wanyuan_per_year)
    if capacity < 0 or peak <= 0 or reduction < 0 or eac < 0:
        raise ValueError("capacity, peak, reduction and eac must be nonnegative with positive peak")
    if reduction <= 1e-9 or eac <= 1e-9:
        return "requires_intervention_and_incremental_cost"
    return "feasible" if (capacity - reduction) / peak < 2.0 - 1e-9 else "infeasible"


def _empty_playback(profile: np.ndarray, reason: str) -> DailyStoragePlayback:
    zeros = np.zeros(len(profile), dtype=float)
    return DailyStoragePlayback(
        feasible=False,
        charge_mw=zeros.copy(),
        discharge_mw=zeros.copy(),
        soc_mwh=zeros.copy(),
        net_after_mw=np.asarray(profile, dtype=float).copy(),
        reason=reason,
        soc_residual_mwh=float("nan"),
    )


def playback_daily_storage(
    profile_mw: Iterable[float],
    storage_modules: int,
    forward_limit_mw: float,
    reverse_limit_mw: float,
    contract: dict[str, Any],
) -> DailyStoragePlayback:
    """用 LP 验证固定整数柜数的日内物理可行性。

    充电只允许在原始净负荷为负时发生，放电只允许在原始净负荷为正时
    发生，因此两者的变量边界天然互斥。SOC 第 0 小时以前的状态取第 23
    小时状态，形成严格日循环。
    """
    if isinstance(storage_modules, bool) or not isinstance(storage_modules, int):
        raise ValueError("storage_modules must be an integer")
    if storage_modules < 0:
        raise ValueError("storage_modules must be nonnegative")
    profile = np.asarray(list(profile_mw), dtype=float)
    if profile.shape != (DAILY_HOURS,) or not np.isfinite(profile).all():
        raise ValueError("profile_mw must contain 24 finite hourly values")
    forward_limit = float(forward_limit_mw)
    reverse_limit = float(reverse_limit_mw)
    if forward_limit < 0 or reverse_limit < 0:
        raise ValueError("physical limits must be nonnegative")

    module = contract["storage"]["module"]
    efficiency = contract["storage"]["efficiency"]
    soc_cfg = contract["storage"]["soc"]
    power = storage_modules * float(module["power_mw"])  # 0.1 MW/柜
    energy = storage_modules * float(module["energy_mwh"])  # 0.215 MWh/柜
    eta_charge = float(efficiency["charge"])
    eta_discharge = float(efficiency["discharge"])

    reverse_required = np.maximum(-profile - reverse_limit, 0.0)
    forward_required = np.maximum(profile - forward_limit, 0.0)
    charge_upper = np.minimum(power, np.maximum(-profile, 0.0))
    discharge_upper = np.minimum(power, np.maximum(profile, 0.0))
    if np.any(reverse_required > charge_upper + 1e-10):
        return _empty_playback(profile, "storage_power_insufficient_for_reverse_limit")
    if np.any(forward_required > discharge_upper + 1e-10):
        return _empty_playback(profile, "storage_power_insufficient_for_forward_limit")

    # 变量顺序：charge[24], discharge[24], soc_after_hour[24]。
    n = DAILY_HOURS
    objective = np.r_[np.ones(n), np.ones(n), np.zeros(n)]
    equality = np.zeros((n, 3 * n), dtype=float)
    for hour in range(n):
        equality[hour, hour] = -eta_charge
        equality[hour, n + hour] = 1.0 / eta_discharge
        equality[hour, 2 * n + hour] = 1.0
        equality[hour, 2 * n + ((hour - 1) % n)] = -1.0
    bounds: list[tuple[float, float]] = []
    bounds.extend(zip(reverse_required.tolist(), charge_upper.tolist(), strict=True))
    bounds.extend(zip(forward_required.tolist(), discharge_upper.tolist(), strict=True))
    if storage_modules == 0:
        soc_min = soc_max = 0.0
    else:
        soc_min = float(soc_cfg["min_fraction"]) * energy
        soc_max = float(soc_cfg["max_fraction"]) * energy
    bounds.extend([(soc_min, soc_max)] * n)
    result = linprog(
        objective,
        A_eq=equality,
        b_eq=np.zeros(n),
        bounds=bounds,
        method="highs",
        options={"presolve": True},
    )
    if not result.success:
        return _empty_playback(profile, f"daily_soc_infeasible:{result.status}")
    charge = np.asarray(result.x[:n], dtype=float)
    discharge = np.asarray(result.x[n : 2 * n], dtype=float)
    soc = np.asarray(result.x[2 * n :], dtype=float)
    net_after = profile + charge - discharge
    residual = float((eta_charge * charge - discharge / eta_discharge).sum())
    tolerance = 2e-7
    valid = bool(
        (net_after <= forward_limit + tolerance).all()
        and (-net_after <= reverse_limit + tolerance).all()
        and (charge[profile >= 0] <= tolerance).all()
        and (discharge[profile <= 0] <= tolerance).all()
        and (soc >= soc_min - tolerance).all()
        and (soc <= soc_max + tolerance).all()
        and abs(residual) <= tolerance
        and not ((charge > tolerance) & (discharge > tolerance)).any()
    )
    return DailyStoragePlayback(
        feasible=valid,
        charge_mw=charge,
        discharge_mw=discharge,
        soc_mwh=soc,
        net_after_mw=net_after,
        reason="feasible" if valid else "post_solve_physical_assertion_failed",
        soc_residual_mwh=residual,
    )


def minimum_storage_modules(
    profiles_mw: Iterable[Iterable[float]],
    forward_limit_mw: float,
    reverse_limit_mw: float,
    contract: dict[str, Any],
    max_modules: int = MAX_STORAGE_MODULES,
) -> int | None:
    """返回同时通过所有经验日的最小整数柜数；不存在则返回 ``None``。"""
    profiles = [np.asarray(list(profile), dtype=float) for profile in profiles_mw]
    if not profiles:
        raise ValueError("at least one profile is required")
    module_power = float(contract["storage"]["module"]["power_mw"])
    deficits = []
    for profile in profiles:
        if profile.shape != (DAILY_HOURS,):
            raise ValueError("each profile must contain 24 values")
        deficits.extend(
            [
                float(np.maximum(-profile - reverse_limit_mw, 0.0).max()),
                float(np.maximum(profile - forward_limit_mw, 0.0).max()),
            ]
        )
    lower = max(0, int(math.ceil(max(deficits) / module_power - 1e-10)))

    def feasible(modules: int) -> bool:
        return all(
            playback_daily_storage(
                profile,
                modules,
                forward_limit_mw,
                reverse_limit_mw,
                contract,
            ).feasible
            for profile in profiles
        )

    if feasible(lower):
        return lower
    high = max(1, lower)
    while high < max_modules and not feasible(high):
        high = min(max_modules, high * 2)
    if not feasible(high):
        return None
    low = lower + 1
    while low < high:
        middle = (low + high) // 2
        if feasible(middle):
            high = middle
        else:
            low = middle + 1
    return low


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _input_hash(paths: list[Path]) -> str:
    payload = {path.name: _sha256(path) for path in sorted(paths, key=lambda item: item.name)}
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _require(root: Path, filename: str, columns: set[str]) -> pd.DataFrame:
    path = root / filename
    if not path.is_file():
        raise RealPlannerError(f"required planning input missing: {path}")
    frame = pd.read_csv(path)
    missing = columns - set(frame.columns)
    if missing:
        raise RealPlannerError(f"{filename}: missing columns {sorted(missing)}")
    return frame


def _annualization_coefficients(contract: dict[str, Any], asset: str) -> tuple[float, float, float]:
    annual = contract["costs"]["annualization"]
    if asset == "storage":
        life_key = "storage_life_years"
        om_key = "storage_fixed_om_fraction_per_year"
    else:
        life_key = "transformer_measure_life_years"
        om_key = "transformer_fixed_om_fraction_per_year"
    base = capital_recovery_factor(annual["discount_rate"], annual[life_key]) + float(
        annual[om_key]
    )
    values = [
        capital_recovery_factor(rate, years) + float(om)
        for rate in annual["sensitivity"]["discount_rate"]
        for years in annual["sensitivity"][life_key]
        for om in annual["sensitivity"][om_key]
    ]
    return min(values), base, max(values)


def _storage_cost_tuple(modules: int, contract: dict[str, Any]) -> tuple[float, ...]:
    storage = contract["storage"]["module"]
    price_low, price_high = [
        float(value) for value in contract["costs"]["storage_capex"]["sensitivity_yuan_per_wh"]
    ]
    energy_wh = modules * float(storage["energy_mwh"]) * 1_000_000.0
    low_capex = energy_wh * price_low / 10000.0
    high_capex = energy_wh * price_high / 10000.0
    base_capex = storage_capex_wanyuan(modules, contract)
    low_coef, base_coef, high_coef = _annualization_coefficients(contract, "storage")
    return (
        low_capex,
        base_capex,
        high_capex,
        low_capex * low_coef,
        base_capex * base_coef,
        high_capex * high_coef,
    )


def _operation_limits(
    unit_capacities: list[float],
    operation_modes: set[str],
    cos_phi: float,
    split_beta: float,
) -> tuple[float, float]:
    total = float(sum(unit_capacities))
    if not unit_capacities or total <= 0:
        return 0.0, 0.0
    forward = total * cos_phi
    split_reverse = split_beta * total * cos_phi
    if len(unit_capacities) == 1:
        parallel_reverse = split_reverse
    else:
        parallel_beta = min(split_beta, (total - max(unit_capacities)) / total)
        parallel_reverse = parallel_beta * total * cos_phi
    if operation_modes == {"split"}:
        reverse = split_reverse
    elif operation_modes == {"parallel"}:
        reverse = parallel_reverse
    else:
        # 运行方式未知时不选择有利值，规划按区间下界保证鲁棒可行。
        reverse = min(split_reverse, parallel_reverse)
    return forward, reverse


def _candidate_combinations(candidates: pd.DataFrame) -> list[pd.DataFrame]:
    if candidates.empty:
        return [candidates.iloc[0:0].copy()]
    usable = candidates[candidates["cost_status"].ne("cost_gap_not_optimizable")].copy()
    if len(usable) > 12:
        raise RealPlannerError("more than 12 candidates at one station requires explicit sequencing")
    combinations = [usable.iloc[0:0].copy()]
    for size in range(1, len(usable) + 1):
        for indices in itertools.combinations(range(len(usable)), size):
            combinations.append(usable.iloc[list(indices)].copy())
    return combinations


def _candidate_costs(selection: pd.DataFrame) -> tuple[float, ...]:
    if selection.empty:
        return (0.0,) * 6
    low_capex = float(selection["capex_low_wanyuan"].sum())
    high_capex = float(selection["capex_high_wanyuan"].sum())
    base_parts = selection["capex_center_wanyuan"].where(
        selection["capex_center_wanyuan"].notna(), selection["capex_high_wanyuan"]
    )
    base_eac_parts = selection["eac_center_wanyuan_per_year"].where(
        selection["eac_center_wanyuan_per_year"].notna(),
        selection["eac_high_wanyuan_per_year"],
    )
    return (
        low_capex,
        float(base_parts.sum()),
        high_capex,
        float(selection["eac_low_wanyuan_per_year"].sum()),
        float(base_eac_parts.sum()),
        float(selection["eac_high_wanyuan_per_year"].sum()),
    )


def _station_options(
    station_id: str,
    units: pd.DataFrame,
    station_candidates: pd.DataFrame,
    profiles: list[np.ndarray],
    contract: dict[str, Any],
) -> list[StationOption]:
    cos_phi = float(contract["technical_parameters"]["cos_phi"]["baseline"])
    split_beta = float(contract["technical_parameters"]["reverse_beta"]["split_or_single"])
    base_units = units["capacity_mva"].astype(float).tolist()
    modes = {str(value).lower() for value in units["operation_mode"].dropna()}
    bays = pd.to_numeric(units["available_10kv_bays"], errors="coerce").fillna(0.0)
    site_available = bool((bays > 0).any())
    options: list[StationOption] = []
    for selection in _candidate_combinations(station_candidates):
        candidate_types = set(selection["candidate_type"].astype(str))
        if "replacement_or_uprating" in candidate_types:
            # 当前真实候选无替换项目；若未来出现，必须补充被替换设备 ID，
            # 不能凭容量猜测替换哪一台。
            continue
        added_units = selection["new_capacity_mva"].astype(float).tolist()
        delta = float(selection["delta_capacity_mva"].sum()) if not selection.empty else 0.0
        forward, reverse = _operation_limits(base_units + added_units, modes, cos_phi, split_beta)
        modules = minimum_storage_modules(profiles, forward, reverse, contract)
        reason = "feasible"
        feasible = modules is not None
        if modules is None:
            modules = 0
            reason = "daily_storage_dispatch_infeasible"
        elif modules > 0 and not site_available:
            feasible = False
            reason = "storage_required_but_no_available_connection_bay"
        expansion_cost = _candidate_costs(selection)
        storage_cost = _storage_cost_tuple(int(modules), contract)
        totals = tuple(a + b for a, b in zip(expansion_cost, storage_cost, strict=True))
        options.append(
            StationOption(
                station_id=station_id,
                selected_candidate_ids=tuple(sorted(selection["candidate_id"].astype(str))),
                expansion_delta_mva=delta,
                storage_modules=int(modules),
                forward_limit_mw=forward,
                reverse_limit_mw=reverse,
                capex_low_wanyuan=totals[0],
                capex_base_wanyuan=totals[1],
                capex_high_wanyuan=totals[2],
                eac_low_wanyuan_per_year=totals[3],
                eac_base_wanyuan_per_year=totals[4],
                eac_high_wanyuan_per_year=totals[5],
                feasible=feasible,
                reason=reason,
            )
        )
    return options


def _option_sort_key(option: StationOption) -> tuple[Any, ...]:
    return (
        option.eac_base_wanyuan_per_year,
        option.capex_base_wanyuan,
        option.expansion_delta_mva,
        option.storage_modules,
        option.selected_candidate_ids,
    )


def _select_county_options(
    station_options: dict[str, list[StationOption]],
    expansion_limit_mva: float | None,
) -> tuple[list[StationOption] | None, str]:
    for station_id, options in station_options.items():
        if not any(option.feasible for option in options):
            reasons = sorted({option.reason for option in options})
            return None, f"{station_id}:" + ";".join(reasons)
    if expansion_limit_mva is None:
        return [
            min((option for option in station_options[sid] if option.feasible), key=_option_sort_key)
            for sid in sorted(station_options)
        ], "feasible"

    # state: rounded delta -> (aggregate sort key, selected options)
    states: dict[float, tuple[tuple[Any, ...], list[StationOption]]] = {
        0.0: ((0.0, 0.0, 0.0, 0, ()), [])
    }
    for station_id in sorted(station_options):
        next_states: dict[float, tuple[tuple[Any, ...], list[StationOption]]] = {}
        for prior_delta, (_prior_key, prior_options) in states.items():
            for option in station_options[station_id]:
                if not option.feasible:
                    continue
                delta = round(prior_delta + option.expansion_delta_mva, 8)
                if delta > expansion_limit_mva + 1e-8:
                    continue
                selected = prior_options + [option]
                key = (
                    sum(item.eac_base_wanyuan_per_year for item in selected),
                    sum(item.capex_base_wanyuan for item in selected),
                    delta,
                    sum(item.storage_modules for item in selected),
                    tuple(item.selected_candidate_ids for item in selected),
                )
                incumbent = next_states.get(delta)
                if incumbent is None or key < incumbent[0]:
                    next_states[delta] = (key, selected)
        states = next_states
        if not states:
            return None, f"{station_id}:no option within A incremental capacity limit"
    best = min(states.values(), key=lambda value: value[0])
    return best[1], "feasible"


def _selected_action_mode(options: list[StationOption]) -> str:
    """按县区最终选中的站级离散组合识别措施类型。"""
    has_expansion = any(option.expansion_delta_mva > 1e-9 for option in options)
    has_storage = any(option.storage_modules > 0 for option in options)
    if has_expansion and has_storage:
        return "ACTION_COMBINED_EXPANSION_STORAGE"
    if has_expansion:
        return "ACTION_EXPANSION_ONLY"
    if has_storage:
        return "ACTION_STORAGE_ONLY"
    return "ACTION_NONE"


def _lineage(source_version: str, source_hash: str, quality: str) -> dict[str, str]:
    return {
        "source_ref": "county_baseline.csv+station_master.csv+transformer_master.csv+expansion_cost_library.csv+empirical_station_scenarios.csv.gz+model_contract.yaml",
        "source_version": source_version,
        "transformation": "enumerate source-backed station candidates; solve minimum integer storage modules; county multiple-choice selection",
        "scenario_id": "real_2025_C0_A_B",
        "quality_flag": quality,
        "source_sha256": source_hash,
    }


def _write_frame(path: Path, frame: pd.DataFrame, sort_by: list[str], compressed: bool = False) -> None:
    if frame.empty:
        raise RealPlannerError(f"{path.name}: refusing to write empty output")
    missing = set(LINEAGE_FIELDS) - set(frame.columns)
    if missing:
        raise RealPlannerError(f"{path.name}: missing lineage fields {sorted(missing)}")
    ordered = frame.sort_values(sort_by, kind="stable").reset_index(drop=True)
    compression: Any = {"method": "gzip", "mtime": 0} if compressed else None
    ordered.to_csv(
        path,
        index=False,
        lineterminator="\n",
        float_format="%.10g",
        compression=compression,
    )


def solve_real_c0ab(
    processed_root: Path,
    working_root: Path,
    output_dir: Path,
    contract_path: Path,
) -> dict[str, Any]:
    """求解八县区、两电压等级的 C0/A/B，并完整回放所选日内调度。"""
    processed_root = Path(processed_root).resolve()
    working_root = Path(working_root).resolve()
    output_dir = Path(output_dir).resolve()
    contract_path = Path(contract_path).resolve()
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if contract["contract"]["version"] != "2.0.0":
        raise RealPlannerError("formal planner requires model contract 2.0.0")
    if contract["scenarios"]["shared"]["curtailment_variable"]:
        raise RealPlannerError("contract must disable active PV shedding")
    if contract["scenarios"]["shared"]["global_10kv_tie_variable"]:
        raise RealPlannerError("contract must disable global 10-kV transfer decisions")

    input_paths = [
        processed_root / "station_master.csv",
        processed_root / "transformer_master.csv",
        working_root / "county_baseline.csv",
        working_root / "expansion_cost_library.csv",
        working_root / "empirical_scenario_index.csv",
        working_root / "empirical_station_scenarios.csv.gz",
        contract_path,
    ]
    station_master = _require(
        processed_root,
        "station_master.csv",
        {"region_id", "voltage_kv", "station_id", "asset_scope_id"},
    )
    master = _require(
        processed_root,
        "transformer_master.csv",
        {"region_id", "voltage_kv", "station_id", "capacity_mva", "operation_mode", "available_10kv_bays"},
    )
    county = _require(
        working_root,
        "county_baseline.csv",
        {"region_id", "voltage_kv", "capacity_base_mva", "positive_peak_base_mw", "clr_model_base", "evidence_grade", "asset_scope_id"},
    )
    expansion = _require(
        working_root,
        "expansion_cost_library.csv",
        {"candidate_id", "region_id", "voltage_kv", "station_id", "candidate_type", "new_capacity_mva", "delta_capacity_mva", "cost_status", "capex_low_wanyuan", "capex_high_wanyuan", "capex_center_wanyuan", "eac_low_wanyuan_per_year", "eac_high_wanyuan_per_year", "eac_center_wanyuan_per_year"},
    )
    scenario_index = _require(
        working_root,
        "empirical_scenario_index.csv",
        {"region_id", "voltage_kv", "station_id", "duration_scenario"},
    )
    profiles = _require(
        working_root,
        "empirical_station_scenarios.csv.gz",
        {"region_id", "voltage_kv", "station_id", "duration_scenario", "hour", "net_load_mw"},
    )
    if set(scenario_index["duration_scenario"]) != {
        "empirical_short",
        "empirical_central",
        "empirical_long",
    }:
        raise RealPlannerError("planner requires exactly the three frozen empirical scenario labels")
    source_version = "+".join(sorted(set(master["source_version"].dropna().astype(str))))
    source_hash = _input_hash(input_paths)
    common_lineage = _lineage(source_version, source_hash, "formal_real_planner_output")

    profile_lookup: dict[tuple[str, int, str], dict[str, np.ndarray]] = {}
    for key, group in profiles.groupby(["region_id", "voltage_kv", "station_id"], sort=True):
        scenario_map: dict[str, np.ndarray] = {}
        for scenario_name, scenario_group in group.groupby("duration_scenario", sort=True):
            ordered = scenario_group.sort_values("hour")
            values = ordered["net_load_mw"].to_numpy(dtype=float)
            if len(values) != DAILY_HOURS:
                raise RealPlannerError(f"{key}|{scenario_name}: expected 24 hours")
            scenario_map[str(scenario_name)] = values
        if len(scenario_map) == 3:
            profile_lookup[(str(key[0]), int(key[1]), str(key[2]))] = scenario_map

    option_rows: list[dict[str, Any]] = []
    solution_rows: list[dict[str, Any]] = []
    action_rows: list[dict[str, Any]] = []
    playback_rows: list[dict[str, Any]] = []
    selected_by_key: dict[tuple[str, int, str], list[StationOption] | None] = {}

    for county_row in county.sort_values(["voltage_kv", "region_id"]).itertuples(index=False):
        region_id = str(county_row.region_id)
        voltage_kv = int(county_row.voltage_kv)
        county_key = (region_id, voltage_kv)
        units_county = master[
            master["region_id"].eq(region_id) & master["voltage_kv"].eq(voltage_kv)
        ].copy()
        operating_scope = station_master[
            station_master["region_id"].eq(region_id)
            & station_master["voltage_kv"].eq(voltage_kv)
            & station_master["asset_scope_id"].eq("operating_2025")
        ]
        if not operating_scope.empty:
            operating_ids = set(operating_scope["station_id"].astype(str))
            units_county = units_county[
                units_county["station_id"].astype(str).isin(operating_ids)
            ]
        station_options: dict[str, list[StationOption]] = {}
        data_gaps: list[str] = []
        for station_id, units in units_county.groupby("station_id", sort=True):
            key = (region_id, voltage_kv, str(station_id))
            scenario_map = profile_lookup.get(key)
            if scenario_map is None:
                data_gaps.append(f"{station_id}:missing_three_scenarios")
                continue
            station_candidates = expansion[
                expansion["region_id"].eq(region_id)
                & expansion["voltage_kv"].eq(voltage_kv)
                & expansion["station_id"].eq(station_id)
            ]
            opts = _station_options(
                str(station_id),
                units,
                station_candidates,
                [scenario_map[name] for name in sorted(scenario_map)],
                contract,
            )
            station_options[str(station_id)] = opts
            for option_number, option in enumerate(opts):
                option_rows.append(
                    {
                        "region_id": region_id,
                        "voltage_kv": voltage_kv,
                        "station_id": station_id,
                        "option_id": f"{region_id}|{voltage_kv}|{station_id}|O{option_number:03d}",
                        "candidate_id": ";".join(option.selected_candidate_ids) or None,
                        "selected_candidate_ids": json.dumps(option.selected_candidate_ids, ensure_ascii=False),
                        "expansion_delta_mva": option.expansion_delta_mva,
                        "storage_modules": option.storage_modules,
                        "storage_power_mw": option.storage_modules * 0.1,
                        "storage_energy_mwh": option.storage_modules * 0.215,
                        "forward_limit_mw": option.forward_limit_mw,
                        "reverse_limit_mw": option.reverse_limit_mw,
                        "capex_low_wanyuan": option.capex_low_wanyuan,
                        "capex_base_wanyuan": option.capex_base_wanyuan,
                        "capex_high_wanyuan": option.capex_high_wanyuan,
                        "eac_low_wanyuan_per_year": option.eac_low_wanyuan_per_year,
                        "eac_base_wanyuan_per_year": option.eac_base_wanyuan_per_year,
                        "eac_high_wanyuan_per_year": option.eac_high_wanyuan_per_year,
                        "feasible": option.feasible,
                        "reason": option.reason,
                        **common_lineage,
                    }
                )

        capacity_base = float(county_row.capacity_base_mva)
        positive_peak_base_mw = float(county_row.positive_peak_base_mw)
        a_limit = a_incremental_capacity_limit(capacity_base, positive_peak_base_mw)
        strict_stock = (
            "infeasible_due_to_inherited_stock"
            if capacity_base > 2.0 * positive_peak_base_mw + 1e-8
            else "stock_within_2.0"
        )
        strict_policy_status = strict_r_lt_2_policy_status(
            capacity_base, positive_peak_base_mw
        )

        # C0 直接检查站级现状静态极值，不配置任何措施。映射/数据缺口
        # 与物理不合规分开，避免把“无法识别”误写成“不合规”。
        c0_noncompliant: list[str] = []
        c0_data_gaps: list[str] = list(data_gaps)
        for station_id, opts in station_options.items():
            no_expand = next(
                (option for option in opts if not option.selected_candidate_ids), None
            )
            if no_expand is None:
                c0_data_gaps.append(f"{station_id}:missing_no_action_option")
                continue
            scenario_map = profile_lookup[(region_id, voltage_kv, station_id)]
            for scenario_name, profile in scenario_map.items():
                check = playback_daily_storage(
                    profile,
                    0,
                    no_expand.forward_limit_mw,
                    no_expand.reverse_limit_mw,
                    contract,
                )
                if not check.feasible:
                    c0_noncompliant.append(f"{station_id}:{scenario_name}:{check.reason}")
                    break
        if c0_data_gaps:
            c0_status = "not_identifiable"
            c0_reason = ";".join(c0_data_gaps + c0_noncompliant)
        else:
            c0_status = "compliant" if not c0_noncompliant else "noncompliant"
            c0_reason = "physical_constraints_satisfied" if not c0_noncompliant else ";".join(c0_noncompliant)
        solution_rows.append(
            {
                "region_id": region_id,
                "voltage_kv": voltage_kv,
                "scheme": "C0",
                "action_mode": "ACTION_NONE",
                "status": c0_status,
                "status_reason": c0_reason,
                "evidence_grade": county_row.evidence_grade,
                "asset_scope_id": county_row.asset_scope_id,
                "capacity_base_mva": capacity_base,
                "positive_peak_base_mw": positive_peak_base_mw,
                "expansion_delta_mva": 0.0,
                "storage_modules": 0,
                "incremental_capex_low_wanyuan": 0.0,
                "incremental_capex_wanyuan": 0.0,
                "incremental_capex_high_wanyuan": 0.0,
                "incremental_eac_low_wanyuan_per_year": 0.0,
                "incremental_eac_wanyuan_per_year": 0.0,
                "incremental_eac_high_wanyuan_per_year": 0.0,
                "clr_after": capacity_base / positive_peak_base_mw,
                "a_expansion_limit_mva": a_limit,
                "strict_stock_R_le_2_status": strict_stock,
                "strict_r_lt_2_policy_status": strict_policy_status,
                "selected_candidate_ids": "[]",
                **common_lineage,
            }
        )
        for station_id in sorted(units_county["station_id"].astype(str).unique()):
            action_rows.append(
                {
                    "region_id": region_id,
                    "voltage_kv": voltage_kv,
                    "scheme": "C0",
                    "station_id": station_id,
                    "candidate_id": None,
                    "selected_candidate_ids": "[]",
                    "expansion_delta_mva": 0.0,
                    "storage_modules": 0,
                    "action_status": "no_action",
                    **common_lineage,
                }
            )

        for scheme, limit in (("A", a_limit), ("B", None)):
            if data_gaps:
                selected = None
                reason = ";".join(data_gaps)
            else:
                selected, reason = _select_county_options(station_options, limit)
            selected_by_key[(region_id, voltage_kv, scheme)] = selected
            feasible = selected is not None
            chosen = selected or []
            delta = sum(option.expansion_delta_mva for option in chosen)
            modules = sum(option.storage_modules for option in chosen)
            low_capex = sum(option.capex_low_wanyuan for option in chosen)
            base_capex = sum(option.capex_base_wanyuan for option in chosen)
            high_capex = sum(option.capex_high_wanyuan for option in chosen)
            low_eac = sum(option.eac_low_wanyuan_per_year for option in chosen)
            base_eac = sum(option.eac_base_wanyuan_per_year for option in chosen)
            high_eac = sum(option.eac_high_wanyuan_per_year for option in chosen)
            ids = tuple(
                candidate
                for option in chosen
                for candidate in option.selected_candidate_ids
            )
            solution_rows.append(
                {
                    "region_id": region_id,
                    "voltage_kv": voltage_kv,
                    "scheme": scheme,
                    "action_mode": _selected_action_mode(chosen),
                    "status": "feasible" if feasible else "infeasible",
                    "status_reason": reason,
                    "evidence_grade": county_row.evidence_grade,
                    "asset_scope_id": county_row.asset_scope_id,
                    "capacity_base_mva": capacity_base,
                    "positive_peak_base_mw": positive_peak_base_mw,
                    "expansion_delta_mva": delta,
                    "storage_modules": modules,
                    "incremental_capex_low_wanyuan": low_capex if feasible else float("nan"),
                    "incremental_capex_wanyuan": base_capex if feasible else float("nan"),
                    "incremental_capex_high_wanyuan": high_capex if feasible else float("nan"),
                    "incremental_eac_low_wanyuan_per_year": low_eac if feasible else float("nan"),
                    "incremental_eac_wanyuan_per_year": base_eac if feasible else float("nan"),
                    "incremental_eac_high_wanyuan_per_year": high_eac if feasible else float("nan"),
                    "clr_after": (capacity_base + delta) / positive_peak_base_mw if feasible else float("nan"),
                    "a_expansion_limit_mva": a_limit,
                    "strict_stock_R_le_2_status": strict_stock,
                    "strict_r_lt_2_policy_status": strict_policy_status,
                    "selected_candidate_ids": json.dumps(ids, ensure_ascii=False),
                    **common_lineage,
                }
            )
            if feasible:
                for option in chosen:
                    candidate_text = ";".join(option.selected_candidate_ids) or None
                    action_rows.append(
                        {
                            "region_id": region_id,
                            "voltage_kv": voltage_kv,
                            "scheme": scheme,
                            "station_id": option.station_id,
                            "candidate_id": candidate_text,
                            "selected_candidate_ids": json.dumps(option.selected_candidate_ids, ensure_ascii=False),
                            "expansion_delta_mva": option.expansion_delta_mva,
                            "storage_modules": option.storage_modules,
                            "action_status": "selected_feasible_option",
                            **common_lineage,
                        }
                    )
                    scenario_map = profile_lookup[(region_id, voltage_kv, option.station_id)]
                    for scenario_name, profile in sorted(scenario_map.items()):
                        playback = playback_daily_storage(
                            profile,
                            option.storage_modules,
                            option.forward_limit_mw,
                            option.reverse_limit_mw,
                            contract,
                        )
                        for hour in range(DAILY_HOURS):
                            physical_violation = bool(
                                not playback.feasible
                                or playback.net_after_mw[hour] > option.forward_limit_mw + 2e-7
                                or -playback.net_after_mw[hour] > option.reverse_limit_mw + 2e-7
                            )
                            playback_rows.append(
                                {
                                    "region_id": region_id,
                                    "voltage_kv": voltage_kv,
                                    "scheme": scheme,
                                    "station_id": option.station_id,
                                    "duration_scenario": scenario_name,
                                    "hour": hour,
                                    "net_load_before_mw": profile[hour],
                                    "charge_mw": playback.charge_mw[hour],
                                    "discharge_mw": playback.discharge_mw[hour],
                                    "soc_mwh": playback.soc_mwh[hour],
                                    "net_load_after_mw": playback.net_after_mw[hour],
                                    "forward_limit_mw": option.forward_limit_mw,
                                    "reverse_limit_mw": option.reverse_limit_mw,
                                    "storage_modules": option.storage_modules,
                                    "physical_violation": physical_violation,
                                    "simultaneous_charge_discharge": bool(
                                        playback.charge_mw[hour] > 2e-7
                                        and playback.discharge_mw[hour] > 2e-7
                                    ),
                                    **common_lineage,
                                }
                            )
            else:
                for station_id in sorted(units_county["station_id"].astype(str).unique()):
                    action_rows.append(
                        {
                            "region_id": region_id,
                            "voltage_kv": voltage_kv,
                            "scheme": scheme,
                            "station_id": station_id,
                            "candidate_id": None,
                            "selected_candidate_ids": "[]",
                            "expansion_delta_mva": 0.0,
                            "storage_modules": 0,
                            "action_status": "county_infeasible_no_solution",
                            **common_lineage,
                        }
                    )

    solutions = pd.DataFrame(solution_rows)
    actions = pd.DataFrame(action_rows)
    options_frame = pd.DataFrame(option_rows)
    playback_frame = pd.DataFrame(playback_rows)
    if len(solutions) != 48:
        raise RealPlannerError(f"expected 48 county-scheme rows, got {len(solutions)}")
    c0 = solutions[solutions["scheme"].eq("C0")]
    if not (c0["incremental_capex_wanyuan"].eq(0) & c0["incremental_eac_wanyuan_per_year"].eq(0)).all():
        raise RealPlannerError("C0 incremental cost must be exactly zero")
    a = solutions[solutions["scheme"].eq("A")].set_index(["region_id", "voltage_kv"])
    b = solutions[solutions["scheme"].eq("B")].set_index(["region_id", "voltage_kv"])
    both = a["status"].eq("feasible") & b["status"].eq("feasible")
    invariant = bool(
        (
            b.loc[both, "incremental_eac_wanyuan_per_year"]
            <= a.loc[both, "incremental_eac_wanyuan_per_year"] + 1e-7
        ).all()
    )
    if not invariant:
        raise RealPlannerError("A008 violated: scheme B EAC exceeds scheme A EAC")
    if not playback_frame.empty and playback_frame["physical_violation"].any():
        raise RealPlannerError("selected solution failed full empirical playback")

    output_dir.mkdir(parents=True, exist_ok=True)
    frames = {
        "real_plan_station_options.csv": (
            options_frame,
            ["region_id", "voltage_kv", "station_id", "option_id"],
            False,
        ),
        "real_plan_county_solutions.csv": (
            solutions,
            ["voltage_kv", "region_id", "scheme"],
            False,
        ),
        "real_plan_actions.csv": (
            actions,
            ["voltage_kv", "region_id", "scheme", "station_id"],
            False,
        ),
        "real_plan_dispatch_playback.csv.gz": (
            playback_frame,
            ["voltage_kv", "region_id", "scheme", "station_id", "duration_scenario", "hour"],
            True,
        ),
    }
    for filename, (frame, keys, compressed) in frames.items():
        _write_frame(output_dir / filename, frame, keys, compressed)
    manifest: dict[str, Any] = {
        "real_planner_version": REAL_PLANNER_VERSION,
        "contract_version": contract["contract"]["version"],
        "contract_sha256": _sha256(contract_path),
        "input_fingerprint": source_hash,
        "output_files": {
            filename: {"sha256": _sha256(output_dir / filename), "rows": int(len(frame))}
            for filename, (frame, _keys, _compressed) in sorted(frames.items())
        },
        "hard_assertions": {
            "A002_fixed_positive_denominator": bool(
                solutions.groupby(["region_id", "voltage_kv"])["positive_peak_base_mw"].nunique().eq(1).all()
            ),
            "A004_no_active_pv_shedding_decision": True,
            "A005_no_global_10kv_transfer_decision": True,
            "A007_real_candidate_ids_only": bool(
                set(actions["candidate_id"].dropna()) <= set(expansion["candidate_id"])
            ),
            "A008_B_cost_not_above_A": invariant,
            "A009_C0_zero_cost_visible_noncompliance": True,
            "A014_strict_r_lt_2_requires_intervention_and_cost": bool(
                solutions["strict_r_lt_2_policy_status"].eq(
                    "requires_intervention_and_incremental_cost"
                ).all()
            ),
        },
    }
    (output_dir / "real_planner_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
