"""v3.2 时序物理适配层。

QX-00005 110 kV 使用经批准的 2025 年 8760 h 同步序列，并采用全年连续
SOC 约束；其他片区/电压继续沿用 v3.1 的三个非概率经验日情景。v3.1
日循环结果同时保留为 QX-00005 的保守对照，不作为 v3.2 主定容口径。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from src.milp_planner import _operation_limits
from src.v3_planner import StatePhysicsResult
from src.v3_time_physics import V3TimePhysicsEvaluator, evaluate_station_profiles
from src.v32_storage import (
    minimum_storage_modules_continuous,
    playback_continuous_storage,
)


class V32TimePhysicsError(ValueError):
    """v3.2 连续时序物理校核失败。"""


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
    """在 v3.1 资产/情景映射之上替换 A 级片区的储能时序边界。"""

    def __init__(
        self,
        processed_root: Path,
        working_root: Path,
        candidates: pd.DataFrame,
        scenario_contract_path: Path,
    ) -> None:
        # v3.1 评估器继续负责已经审定的设备白名单、经验情景构造、
        # QX-00005 8760 h 原始映射/官方正峰校准以及非 A 级片区门禁。
        self.base = V3TimePhysicsEvaluator(
            processed_root,
            working_root,
            candidates,
            scenario_contract_path,
        )
        self.contract = self.base.contract
        self.scenario_manifest = self.base.scenario_manifest
        self.synchronized_base_peaks = self.base.synchronized_base_peaks
        self._continuous_cache: dict[
            tuple[str, int, int, tuple[str, ...], float], StatePhysicsResult
        ] = {}

    def _qx00005_station_contexts(
        self,
        selected_candidate_ids: tuple[str, ...],
        *,
        cos_phi: float,
    ) -> tuple[_ContinuousStationContext, ...] | StatePhysicsResult:
        """按最终设备组合形成 QX-00005 110 kV 各站连续时序上下文。

        该步骤不依赖 v3.1 的日循环可行性判断，因此不会出现“日循环先失败，
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
