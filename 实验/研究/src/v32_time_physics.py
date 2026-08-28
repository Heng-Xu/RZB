"""v3.2 时序物理适配层。

QX-00005 110 kV 使用经批准的 2025 年 8760 h 同步序列，并采用全年连续
SOC 约束；其他片区/电压继续沿用已审定的三个非概率经验日情景。日循环
结果同时保留为 QX-00005 的保守对照，不作为 v3.2 主定容口径。
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from src.milp_planner import _operation_limits
from src.v3_planner import StatePhysicsResult
from src.v3_time_physics import V3TimePhysicsEvaluator, evaluate_station_profiles
from src.v32_storage import (
    ContinuousStoragePlayback,
    minimum_storage_modules_continuous,
    playback_continuous_storage,
)


class V32TimePhysicsError(ValueError):
    """v3.2 连续时序物理校核失败。"""


def continuous_playback_row_audit(
    profile_mw: float,
    charge_mw: float,
    discharge_mw: float,
    soc_mwh: float,
    *,
    storage_energy_mwh: float,
    soc_min_fraction: float,
    soc_max_fraction: float,
    tolerance: float = 2e-7,
) -> dict[str, bool]:
    """核验连续回放单个时段的 SOC、功率方向和同时动作。"""
    values = (profile_mw, charge_mw, discharge_mw, soc_mwh)
    if not np.isfinite(values).all():
        return {
            "soc_bounds_violation": True,
            "cross_zero_violation": True,
            "simultaneous_charge_discharge_violation": True,
            "physical_violation": True,
        }
    lower = float(soc_min_fraction) * float(storage_energy_mwh)
    upper = float(soc_max_fraction) * float(storage_energy_mwh)
    soc_bounds = bool(
        soc_mwh < lower - tolerance or soc_mwh > upper + tolerance
    )
    cross_zero = bool(
        (charge_mw > tolerance and profile_mw >= 0)
        or (discharge_mw > tolerance and profile_mw <= 0)
    )
    simultaneous = bool(
        charge_mw > tolerance and discharge_mw > tolerance
    )
    return {
        "soc_bounds_violation": soc_bounds,
        "cross_zero_violation": cross_zero,
        "simultaneous_charge_discharge_violation": simultaneous,
        "physical_violation": bool(soc_bounds or cross_zero or simultaneous),
    }


def summarize_continuous_playback(
    playback: ContinuousStoragePlayback,
    profile_mw: np.ndarray,
    *,
    storage_modules: int,
    module_energy_mwh: float,
    soc_min_fraction: float,
    soc_max_fraction: float,
    tolerance: float = 2e-7,
) -> dict[str, object]:
    """把连续 SOC 回放压缩为可审查的设备级汇总。

    ``soc_mwh`` 是每个时段结束时的 SOC；全年连续循环的初始 SOC
    因而等于最后一个时段结束时的 SOC。该定义同时记录 SOC 闭合残差，
    避免只凭一条曲线视觉判断年度循环是否成立。
    """
    profile = np.asarray(profile_mw, dtype=float)
    if profile.ndim != 1 or profile.size < 2 or not np.isfinite(profile).all():
        raise ValueError("profile_mw must be a finite one-dimensional series")
    if len(playback.charge_mw) != len(profile):
        raise ValueError("playback and profile lengths must match")
    modules = int(storage_modules)
    if modules < 0:
        raise ValueError("storage_modules must be nonnegative")
    energy = modules * float(module_energy_mwh)
    charge = np.asarray(playback.charge_mw, dtype=float)
    discharge = np.asarray(playback.discharge_mw, dtype=float)
    soc = np.asarray(playback.soc_mwh, dtype=float)
    net_after = np.asarray(playback.net_after_mw, dtype=float)
    soc_min_allowed = float(soc_min_fraction) * energy
    soc_max_allowed = float(soc_max_fraction) * energy
    soc_bounds_violation = bool(
        (soc < soc_min_allowed - tolerance).any()
        or (soc > soc_max_allowed + tolerance).any()
    )
    cross_zero_violation = bool(
        (charge[profile >= 0] > tolerance).any()
        or (discharge[profile <= 0] > tolerance).any()
    )
    simultaneous_violation = bool(
        ((charge > tolerance) & (discharge > tolerance)).any()
    )
    physical_violation = bool(
        not playback.feasible
        or soc_bounds_violation
        or cross_zero_violation
        or simultaneous_violation
        or not np.isfinite(soc).all()
        or not np.isfinite(net_after).all()
    )
    return {
        "continuous_points": int(len(profile)),
        "storage_modules": modules,
        "storage_energy_mwh": float(energy),
        "soc_min_mwh": float(soc.min()),
        "soc_max_mwh": float(soc.max()),
        "soc_min_fraction": (
            float(soc.min() / energy) if energy > 0 else 0.0
        ),
        "soc_max_fraction": (
            float(soc.max() / energy) if energy > 0 else 0.0
        ),
        "soc_initial_mwh": float(soc[-1]),
        "soc_final_mwh": float(soc[-1]),
        "soc_residual_mwh": float(playback.soc_residual_mwh),
        "max_charge_mw": float(charge.max()),
        "max_discharge_mw": float(discharge.max()),
        "charge_energy_mwh": float(charge.sum()),
        "discharge_energy_mwh": float(discharge.sum()),
        "soc_bounds_violation": soc_bounds_violation,
        "cross_zero_violation": cross_zero_violation,
        "simultaneous_charge_discharge_violation": simultaneous_violation,
        "physical_violation": physical_violation,
        "feasible": bool(playback.feasible and not physical_violation),
        "playback_reason": str(playback.reason),
    }


@dataclass(frozen=True)
class _ContinuousStationContext:
    station_id: str
    profile_mw: np.ndarray
    forward_limit_mw: float
    reverse_limit_mw: float
    site_available: bool
    repair_candidate_ids: tuple[str, ...]
    daily_cyclic_modules: int | None
    daily_cyclic_feasible: bool
    daily_cyclic_reason: str


class V32TimePhysicsEvaluator:
    """在既有资产/情景映射之上替换 A 级片区的储能时序边界。"""

    def __init__(
        self,
        processed_root: Path,
        working_root: Path,
        candidates: pd.DataFrame,
        scenario_contract_path: Path,
        *,
        net_load_scale: float = 1.0,
    ) -> None:
        scale = float(net_load_scale)
        if not np.isfinite(scale) or scale <= 0:
            raise V32TimePhysicsError("net_load_scale must be positive and finite")
        # 基础评估器继续负责已经审定的设备白名单、经验情景构造、
        # QX-00005 8760 h 原始映射/官方正峰校准以及非 A 级片区门禁。
        self.base = V3TimePhysicsEvaluator(
            processed_root,
            working_root,
            candidates,
            scenario_contract_path,
        )
        self.net_load_scale = scale
        if not np.isclose(scale, 1.0):
            self._scale_loaded_profiles(scale)
        self.contract = self.base.contract
        self.scenario_manifest = self.base.scenario_manifest
        self.synchronized_base_peaks = self.base.synchronized_base_peaks
        self._continuous_cache: dict[
            tuple[str, int, int, tuple[str, ...], float], StatePhysicsResult
        ] = {}

    def _scale_loaded_profiles(self, scale: float) -> None:
        """按同一比例缩放已加载的净负荷序列和同步峰值。

        当前数据没有足以支持“只改负荷”或“只改光伏”的同步拆分；压力
        场景因此明确作为系统净负荷压力场景。2021 实际资产容量不在此处
        改写，仍由主模型输入单独保留。
        """
        value = float(scale)
        scaled: dict[tuple[str, int, str], object] = {}
        for key, bundle in self.base.profiles.items():
            scaled_profiles = tuple(
                np.asarray(profile, dtype=float) * value
                for profile in bundle.profiles
            )
            scaled[key] = type(bundle)(
                labels=bundle.labels,
                profiles=scaled_profiles,
                timestamps=bundle.timestamps,
                basis=f"{bundle.basis};net_load_scale_{value:.12g}",
                synchronized_county_evidence=bundle.synchronized_county_evidence,
            )
        self.base.profiles = scaled  # type: ignore[assignment]
        self.base.synchronized_base_peaks = {
            key: (float(positive) * value, float(reverse) * value)
            for key, (positive, reverse) in self.base.synchronized_base_peaks.items()
        }

    def _qx00005_station_contexts(
        self,
        selected_candidate_ids: tuple[str, ...],
        *,
        cos_phi: float,
    ) -> tuple[_ContinuousStationContext, ...] | StatePhysicsResult:
        """按最终设备组合形成 QX-00005 110 kV 各站连续时序上下文。

        该步骤不依赖保守日循环可行性判断，因此不会出现“日循环先失败，
        连续模型无机会评估”的旧边界泄漏。日循环仅在同一设备组合上并行
        计算作保守对照。
        """
        group = self.base.master[
            self.base.master["region_id"].astype(str).eq("QX-00005")
            & self.base.master["voltage_kv"].eq(110)
        ].copy()
        if group.empty:
            return StatePhysicsResult(
                False,
                0,
                reason="missing_2025_operating_station_scope",
            )

        retired, additions, candidate_connection_sites = self.base._candidate_effects(  # noqa: SLF001
            selected_candidate_ids
        )
        split_beta = float(
            self.contract["technical_parameters"]["reverse_beta"]["split_or_single"]
        )
        contexts: list[_ContinuousStationContext] = []
        for station_id_raw, base_units in group.groupby("station_id", sort=True):
            station_id = str(station_id_raw)
            bundle = self.base.profiles.get(("QX-00005", 110, station_id))
            if bundle is None or not bundle.synchronized_county_evidence:
                return StatePhysicsResult(
                    False,
                    0,
                    reason=f"{station_id}:missing_approved_synchronized_8760_profile",
                )
            profile = np.concatenate(bundle.profiles)
            if profile.shape != (8760,) or not np.isfinite(profile).all():
                raise V32TimePhysicsError(
                    f"{station_id}: expected 8760 finite chronological values"
                )

            retained = base_units[
                ~base_units["transformer_uid"].astype(str).isin(retired)
            ]
            added_here = tuple(sorted(additions.get(station_id, [])))
            capacities = retained["capacity_mva"].astype(float).tolist()
            capacities.extend(float(value) for value in added_here)
            # 模型没有“整站退出后由别站永久转供”的拓扑变量，因此不能把
            # 站内主变全部退役后再让储能虚拟承担整个站负荷。
            if not capacities:
                repair = self.base._unselected_station_candidates(  # noqa: SLF001
                    "QX-00005", 110, station_id, selected_candidate_ids
                )
                return StatePhysicsResult(
                    False,
                    0,
                    reason=f"{station_id}:no_transformer_remaining_after_actions",
                    repair_candidate_ids=repair,
                )

            modes = set(retained["operation_mode"].dropna().astype(str).str.lower())
            if added_here:
                modes.add("unknown")
            forward_limit, reverse_limit = _operation_limits(
                capacities,
                modes,
                float(cos_phi),
                split_beta,
            )
            site_available = bool(
                (
                    pd.to_numeric(
                        base_units["available_10kv_bays"], errors="coerce"
                    ).fillna(0.0)
                    > 0
                ).any()
            ) or station_id in candidate_connection_sites
            repair = self.base._unselected_station_candidates(  # noqa: SLF001
                "QX-00005", 110, station_id, selected_candidate_ids
            )

            # 对照模型只用于报告保守性，不参与 v3.2 主门禁。
            daily = evaluate_station_profiles(
                bundle.profiles,
                unit_capacities_mva=capacities,
                operation_modes=modes,
                site_available=site_available,
                contract=self.contract,
                cos_phi=float(cos_phi),
            )
            contexts.append(
                _ContinuousStationContext(
                    station_id=station_id,
                    profile_mw=profile,
                    forward_limit_mw=float(forward_limit),
                    reverse_limit_mw=float(reverse_limit),
                    site_available=site_available,
                    repair_candidate_ids=repair,
                    daily_cyclic_modules=(
                        int(daily.required_storage_modules)
                        if daily.required_storage_modules is not None
                        else None
                    ),
                    daily_cyclic_feasible=bool(daily.feasible),
                    daily_cyclic_reason=str(daily.reason),
                )
            )
        return tuple(contexts)

    def _evaluate_qx00005_continuous(
        self,
        selected_candidate_ids: tuple[str, ...],
        *,
        cos_phi: float,
    ) -> StatePhysicsResult:
        contexts_or_failure = self._qx00005_station_contexts(
            selected_candidate_ids,
            cos_phi=float(cos_phi),
        )
        if isinstance(contexts_or_failure, StatePhysicsResult):
            return contexts_or_failure
        contexts = contexts_or_failure

        required_modules = 0
        aggregate_after: np.ndarray | None = None
        improvement_ids: set[str] = set()
        for station in contexts:
            modules = minimum_storage_modules_continuous(
                station.profile_mw,
                forward_limit_mw=station.forward_limit_mw,
                reverse_limit_mw=station.reverse_limit_mw,
                contract=self.contract,
            )
            if modules is None:
                return StatePhysicsResult(
                    False,
                    required_modules,
                    reason=f"{station.station_id}:continuous_8760_storage_dispatch_infeasible",
                    repair_candidate_ids=station.repair_candidate_ids,
                )
            modules = int(modules)
            if modules > 0:
                improvement_ids.update(station.repair_candidate_ids)
            if modules > 0 and not station.site_available:
                return StatePhysicsResult(
                    False,
                    required_modules + modules,
                    reason=f"{station.station_id}:storage_required_but_no_available_connection_bay",
                    repair_candidate_ids=station.repair_candidate_ids,
                )

            profile = station.profile_mw
            if (
                float(np.max(profile)) <= station.forward_limit_mw + 1e-9
                and float(-np.min(profile)) <= station.reverse_limit_mw + 1e-9
            ):
                net_after = profile.copy()
            else:
                playback = playback_continuous_storage(
                    profile,
                    storage_modules=modules,
                    forward_limit_mw=station.forward_limit_mw,
                    reverse_limit_mw=station.reverse_limit_mw,
                    contract=self.contract,
                )
                if not playback.feasible:
                    return StatePhysicsResult(
                        False,
                        required_modules,
                        reason=f"{station.station_id}:{playback.reason}",
                        repair_candidate_ids=station.repair_candidate_ids,
                    )
                net_after = playback.net_after_mw

            required_modules += modules
            aggregate_after = (
                net_after.copy()
                if aggregate_after is None
                else aggregate_after + net_after
            )

        if aggregate_after is None or aggregate_after.shape != (8760,):
            raise V32TimePhysicsError(
                "QX-00005 continuous playback did not form 8760 points"
            )
        return StatePhysicsResult(
            True,
            int(required_modules),
            p_plus_mw=max(float(aggregate_after.max()), 0.0),
            p_minus_mw=max(float(-aggregate_after.min()), 0.0),
            reason="approved_2025_8760_continuous_soc_playback_feasible",
            improvement_candidate_ids=tuple(sorted(improvement_ids)),
        )

    def evaluator(
        self, cos_phi: float
    ) -> Callable[[str, int, int, tuple[str, ...]], StatePhysicsResult]:
        """返回规划器所需状态回调。"""

        base_evaluator = self.base.evaluator(float(cos_phi))

        def evaluate(
            region_id: str,
            voltage_kv: int,
            year: int,
            selected_candidate_ids: tuple[str, ...],
        ) -> StatePhysicsResult:
            key = (
                str(region_id),
                int(voltage_kv),
                int(year),
                tuple(sorted(selected_candidate_ids)),
                round(float(cos_phi), 12),
            )
            cached = self._continuous_cache.get(key)
            if cached is not None:
                return cached
            if key[2] == 2025 and key[0] == "QX-00005" and key[1] == 110:
                result = self._evaluate_qx00005_continuous(
                    key[3], cos_phi=float(cos_phi)
                )
            else:
                result = base_evaluator(key[0], key[1], key[2], key[3])
            self._continuous_cache[key] = result
            return result

        return evaluate

    def chronology_comparison(
        self,
        selected_candidate_ids: tuple[str, ...],
        *,
        cos_phi: float,
    ) -> pd.DataFrame:
        """输出 QX-00005 各站日循环与连续 8760 h 定容差异。"""
        contexts_or_failure = self._qx00005_station_contexts(
            tuple(sorted(selected_candidate_ids)),
            cos_phi=float(cos_phi),
        )
        if isinstance(contexts_or_failure, StatePhysicsResult):
            raise V32TimePhysicsError(
                f"cannot form chronology comparison: {contexts_or_failure.reason}"
            )
        rows: list[dict[str, object]] = []
        for station in contexts_or_failure:
            continuous = minimum_storage_modules_continuous(
                station.profile_mw,
                forward_limit_mw=station.forward_limit_mw,
                reverse_limit_mw=station.reverse_limit_mw,
                contract=self.contract,
            )
            rows.append(
                {
                    "region_id": "QX-00005",
                    "voltage_kv": 110,
                    "station_id": station.station_id,
                    "daily_cyclic_feasible": station.daily_cyclic_feasible,
                    "daily_cyclic_reason": station.daily_cyclic_reason,
                    "daily_cyclic_modules": station.daily_cyclic_modules,
                    "continuous_8760_modules": continuous,
                    "module_difference_daily_minus_continuous": (
                        None
                        if continuous is None or station.daily_cyclic_modules is None
                        else int(station.daily_cyclic_modules) - int(continuous)
                    ),
                    "forward_limit_mw": station.forward_limit_mw,
                    "reverse_limit_mw": station.reverse_limit_mw,
                    "site_available": station.site_available,
                }
            )
        return pd.DataFrame(rows)

    def write_qx00005_continuous_soc_artifacts(
        self,
        planner: dict[str, pd.DataFrame],
        output_dir: Path,
        *,
        cos_phi: float,
    ) -> dict[str, object]:
        """写出 QX-00005 110 kV 两条主路径的连续 8760 h SOC 证据。

        汇总表覆盖每条路径的全部运行站；逐时曲线只保留实际配置储能的
        站点，以控制成果体量。站点无储能时仍在汇总表中记录 8760 点回放
        和零 SOC，不能把“未配置储能”误读为“未做时序校核”。
        """
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        years = planner["path_year_results"]
        actions = planner["path_action_results"]
        costs = planner["path_cost_breakdown"]
        module_energy = float(self.contract["storage"]["module"]["energy_mwh"])
        soc_min_fraction = float(self.contract["storage"]["soc"]["min_fraction"])
        soc_max_fraction = float(self.contract["storage"]["soc"]["max_fraction"])
        tolerance = 2e-7
        summary_rows: list[dict[str, object]] = []
        curve_rows: list[dict[str, object]] = []

        selected_costs = costs[
            costs["region_id"].astype(str).eq("QX-00005")
            & costs["voltage_kv"].astype(int).eq(110)
        ].sort_values("path_id", kind="stable")
        if selected_costs.empty:
            raise V32TimePhysicsError("QX-00005 110 kV path cost rows are missing")

        for cost_row in selected_costs.itertuples(index=False):
            path_id = str(cost_row.path_id)
            group_actions = actions[
                actions["path_id"].astype(str).eq(path_id)
                & actions["region_id"].astype(str).eq("QX-00005")
                & actions["voltage_kv"].astype(int).eq(110)
            ]
            selected_ids = tuple(
                sorted(
                    value
                    for value in group_actions.get(
                        "candidate_id", pd.Series(dtype=str)
                    ).dropna().astype(str)
                    if value
                )
            )
            year_row = years[
                years["path_id"].astype(str).eq(path_id)
                & years["region_id"].astype(str).eq("QX-00005")
                & years["voltage_kv"].astype(int).eq(110)
                & years["year"].eq(2025)
            ]
            path_feasible = str(cost_row.status) == "feasible" and len(year_row) == 1
            if not path_feasible:
                summary_rows.append(
                    {
                        "path_id": path_id,
                        "region_id": "QX-00005",
                        "voltage_kv": 110,
                        "station_id": "__PATH__",
                        "path_status": str(cost_row.status),
                        "selected_candidate_ids": json.dumps(
                            selected_ids, ensure_ascii=False
                        ),
                        "continuous_soc_audit_feasible": False,
                        "audit_reason": "optimization_path_infeasible",
                    }
                )
                continue

            installed_modules = int(round(float(year_row.iloc[0]["storage_modules"])))
            contexts_or_failure = self._qx00005_station_contexts(
                selected_ids,
                cos_phi=float(cos_phi),
            )
            if isinstance(contexts_or_failure, StatePhysicsResult):
                raise V32TimePhysicsError(
                    f"{path_id}: cannot form continuous SOC contexts: "
                    f"{contexts_or_failure.reason}"
                )
            contexts = contexts_or_failure
            required_by_station: dict[str, int] = {}
            for station in contexts:
                required = minimum_storage_modules_continuous(
                    station.profile_mw,
                    forward_limit_mw=station.forward_limit_mw,
                    reverse_limit_mw=station.reverse_limit_mw,
                    contract=self.contract,
                )
                if required is None:
                    raise V32TimePhysicsError(
                        f"{path_id}|{station.station_id}: continuous SOC minimum is infeasible"
                    )
                required_by_station[station.station_id] = int(required)
            minimum_total = sum(required_by_station.values())
            if installed_modules < minimum_total:
                raise V32TimePhysicsError(
                    f"{path_id}: installed storage {installed_modules} is below "
                    f"continuous minimum {minimum_total}"
                )
            allocation = dict(required_by_station)
            extra_modules = installed_modules - minimum_total
            if extra_modules:
                extra_sites = sorted(
                    station.station_id for station in contexts if station.site_available
                )
                if not extra_sites:
                    raise V32TimePhysicsError(
                        f"{path_id}: no approved site for extra storage modules"
                    )
                allocation[extra_sites[0]] += extra_modules

            for station in contexts:
                modules = int(allocation[station.station_id])
                playback = playback_continuous_storage(
                    station.profile_mw,
                    storage_modules=modules,
                    forward_limit_mw=station.forward_limit_mw,
                    reverse_limit_mw=station.reverse_limit_mw,
                    contract=self.contract,
                )
                if not playback.feasible:
                    raise V32TimePhysicsError(
                        f"{path_id}|{station.station_id}: SOC playback failed: "
                        f"{playback.reason}"
                    )
                audit = summarize_continuous_playback(
                    playback,
                    station.profile_mw,
                    storage_modules=modules,
                    module_energy_mwh=module_energy,
                    soc_min_fraction=soc_min_fraction,
                    soc_max_fraction=soc_max_fraction,
                    tolerance=tolerance,
                )
                if bool(audit["physical_violation"]):
                    raise V32TimePhysicsError(
                        f"{path_id}|{station.station_id}: continuous SOC audit failed"
                    )
                timestamps = tuple(
                    timestamp
                    for day in self.base.profiles[
                        ("QX-00005", 110, station.station_id)
                    ].timestamps
                    for timestamp in day
                )
                if len(timestamps) != len(station.profile_mw):
                    raise V32TimePhysicsError(
                        f"{station.station_id}: SOC timestamps do not cover 8760 hours"
                    )
                summary_rows.append(
                    {
                        "path_id": path_id,
                        "region_id": "QX-00005",
                        "voltage_kv": 110,
                        "station_id": station.station_id,
                        "path_status": str(cost_row.status),
                        "selected_candidate_ids": json.dumps(
                            selected_ids, ensure_ascii=False
                        ),
                        "installed_storage_modules_total": installed_modules,
                        "minimum_continuous_storage_modules_total": minimum_total,
                        "installed_storage_modules_at_station": modules,
                        "minimum_continuous_storage_modules_at_station": required_by_station[
                            station.station_id
                        ],
                        "forward_limit_mw": station.forward_limit_mw,
                        "reverse_limit_mw": station.reverse_limit_mw,
                        "profile_basis": "approved_2025_8760_station_profile_scaled_to_official_positive_peak",
                        "curve_points_written": int(len(station.profile_mw)) if modules > 0 else 0,
                        **audit,
                    }
                )
                if modules == 0:
                    continue
                soc_before = np.concatenate(
                    [np.asarray([playback.soc_mwh[-1]]), playback.soc_mwh[:-1]]
                )
                for hour_index, timestamp in enumerate(timestamps):
                    profile_value = float(station.profile_mw[hour_index])
                    charge_value = float(playback.charge_mw[hour_index])
                    discharge_value = float(playback.discharge_mw[hour_index])
                    soc_value = float(playback.soc_mwh[hour_index])
                    net_after_value = float(playback.net_after_mw[hour_index])
                    curve_rows.append(
                        {
                            "path_id": path_id,
                            "region_id": "QX-00005",
                            "voltage_kv": 110,
                            "station_id": station.station_id,
                            "hour_index": hour_index,
                            "timestamp": timestamp,
                            "profile_basis": "approved_2025_8760_station_profile_scaled_to_official_positive_peak",
                            "net_load_before_mw": profile_value,
                            "charge_mw": charge_value,
                            "discharge_mw": discharge_value,
                            "soc_before_mwh": float(soc_before[hour_index]),
                            "soc_after_mwh": soc_value,
                            "net_load_after_mw": net_after_value,
                            "storage_modules_at_station": modules,
                            "forward_limit_mw": station.forward_limit_mw,
                            "reverse_limit_mw": station.reverse_limit_mw,
                            **continuous_playback_row_audit(
                                profile_value,
                                charge_value,
                                discharge_value,
                                soc_value,
                                storage_energy_mwh=modules * module_energy,
                                soc_min_fraction=soc_min_fraction,
                                soc_max_fraction=soc_max_fraction,
                                tolerance=tolerance,
                            ),
                        }
                    )

        summary = pd.DataFrame(summary_rows)
        curve = pd.DataFrame(curve_rows)
        if summary.empty:
            raise V32TimePhysicsError("QX-00005 continuous SOC summary is empty")
        if not curve.empty and curve["physical_violation"].any():
            raise V32TimePhysicsError("QX-00005 continuous SOC curve has violations")
        summary_path = output_dir / "qx00005_continuous_soc_summary.csv"
        curve_path = output_dir / "qx00005_continuous_soc_8760.csv.gz"
        summary.sort_values(["path_id", "station_id"], kind="stable").to_csv(
            summary_path,
            index=False,
            lineterminator="\n",
            float_format="%.10g",
        )
        curve.sort_values(
            ["path_id", "station_id", "hour_index"], kind="stable"
        ).to_csv(
            curve_path,
            index=False,
            lineterminator="\n",
            float_format="%.10g",
            compression={"method": "gzip", "mtime": 0},
        )
        return {
            "qx00005_continuous_soc_summary.csv": {
                "rows": int(len(summary)),
                "sha256": _sha256(summary_path),
            },
            "qx00005_continuous_soc_8760.csv.gz": {
                "rows": int(len(curve)),
                "sha256": _sha256(curve_path),
            },
            "paths": sorted(summary["path_id"].astype(str).unique().tolist()),
            "curve_points": int(len(curve)),
            "continuous_soc_validation": "all_written_curve_rows_passed_SOC_physical_audit",
        }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
