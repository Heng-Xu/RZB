"""v3.2 时序物理适配层。

QX-00005 110 kV 使用经批准的 2025 年 8760 h 同步序列，并采用全年连续
SOC 约束；其他片区/电压继续沿用 v3.1 的三个非概率经验日情景。v3.1
日循环结果同时保留为 QX-00005 的保守对照，不作为 v3.2 主定容口径。
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from src.v3_planner import StatePhysicsResult
from src.v3_time_physics import V3TimePhysicsEvaluator
from src.v32_storage import (
    minimum_storage_modules_continuous,
    playback_continuous_storage,
)


class V32TimePhysicsError(ValueError):
    """v3.2 连续时序物理校核失败。"""


class V32TimePhysicsEvaluator:
    """在 v3.1 站级资产/情景映射之上替换 A 级片区储能时序边界。"""

    def __init__(
        self,
        processed_root: Path,
        working_root: Path,
        candidates: pd.DataFrame,
        scenario_contract_path: Path,
    ) -> None:
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

    def evaluator(
        self, cos_phi: float
    ) -> Callable[[str, int, int, tuple[str, ...]], StatePhysicsResult]:
        """返回规划器所需状态回调。

        非 QX-00005 110 kV 状态原样使用 v3.1 时序门禁；QX-00005 2025
        可行状态重新按 8760 h 连续 SOC 定容和回放。若日循环门禁已因站址
        缺失等与连续时序无关的物理原因判为不可行，则保持该不可行结论。
        """

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

            group = self.base._evaluate_group(  # noqa: SLF001 - deliberate v3.2 adapter
                key[0], key[1], key[2], key[3], float(cos_phi)
            )
            daily_result = group.result
            if key[2] != 2025 or key[0] != "QX-00005" or key[1] != 110:
                self._continuous_cache[key] = daily_result
                return daily_result
            if not daily_result.feasible:
                # 站址缺失、设备范围缺失等并非日循环边界造成；不以连续模型
                # 越过这些硬约束。
                self._continuous_cache[key] = daily_result
                return daily_result

            required_modules = 0
            aggregate_after: np.ndarray | None = None
            for station in group.stations:
                if not station.bundle.synchronized_county_evidence:
                    raise V32TimePhysicsError(
                        f"{station.station_id}: QX-00005 formal bundle is not synchronized"
                    )
                profile = np.concatenate(station.bundle.profiles)
                if profile.shape != (8760,):
                    raise V32TimePhysicsError(
                        f"{station.station_id}: expected 8760 chronological values"
                    )
                forward_limit = float(station.evaluation.forward_limit_mw)
                reverse_limit = float(station.evaluation.reverse_limit_mw)
                modules = minimum_storage_modules_continuous(
                    profile,
                    forward_limit,
                    reverse_limit,
                    self.contract,
                )
                if modules is None:
                    result = StatePhysicsResult(
                        False,
                        required_modules,
                        reason=f"{station.station_id}:continuous_8760_storage_dispatch_infeasible",
                        repair_candidate_ids=daily_result.improvement_candidate_ids,
                    )
                    self._continuous_cache[key] = result
                    return result
                if modules > 0 and not station.site_available:
                    result = StatePhysicsResult(
                        False,
                        required_modules + int(modules),
                        reason=f"{station.station_id}:storage_required_but_no_available_connection_bay",
                        repair_candidate_ids=daily_result.improvement_candidate_ids,
                    )
                    self._continuous_cache[key] = result
                    return result

                if (
                    float(np.max(profile)) <= forward_limit + 1e-9
                    and float(-np.min(profile)) <= reverse_limit + 1e-9
                ):
                    net_after = profile.copy()
                else:
                    playback = playback_continuous_storage(
                        profile,
                        int(modules),
                        forward_limit,
                        reverse_limit,
                        self.contract,
                    )
                    if not playback.feasible:
                        result = StatePhysicsResult(
                            False,
                            required_modules,
                            reason=f"{station.station_id}:{playback.reason}",
                            repair_candidate_ids=daily_result.improvement_candidate_ids,
                        )
                        self._continuous_cache[key] = result
                        return result
                    net_after = playback.net_after_mw

                required_modules += int(modules)
                aggregate_after = (
                    net_after.copy()
                    if aggregate_after is None
                    else aggregate_after + net_after
                )

            if aggregate_after is None or aggregate_after.shape != (8760,):
                raise V32TimePhysicsError("QX-00005 continuous playback did not form 8760 points")
            result = StatePhysicsResult(
                True,
                int(required_modules),
                p_plus_mw=max(float(aggregate_after.max()), 0.0),
                p_minus_mw=max(float(-aggregate_after.min()), 0.0),
                reason="approved_2025_8760_continuous_soc_playback_feasible",
                improvement_candidate_ids=daily_result.improvement_candidate_ids,
            )
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
        group = self.base._evaluate_group(  # noqa: SLF001 - deliberate audit adapter
            "QX-00005",
            110,
            2025,
            tuple(sorted(selected_candidate_ids)),
            float(cos_phi),
        )
        rows: list[dict[str, object]] = []
        for station in group.stations:
            profile = np.concatenate(station.bundle.profiles)
            continuous = minimum_storage_modules_continuous(
                profile,
                float(station.evaluation.forward_limit_mw),
                float(station.evaluation.reverse_limit_mw),
                self.contract,
            )
            rows.append(
                {
                    "region_id": "QX-00005",
                    "voltage_kv": 110,
                    "station_id": station.station_id,
                    "daily_cyclic_modules": int(station.evaluation.required_storage_modules),
                    "continuous_8760_modules": continuous,
                    "module_difference_daily_minus_continuous": (
                        None
                        if continuous is None
                        else int(station.evaluation.required_storage_modules) - int(continuous)
                    ),
                    "forward_limit_mw": float(station.evaluation.forward_limit_mw),
                    "reverse_limit_mw": float(station.evaluation.reverse_limit_mw),
                    "site_available": bool(station.site_available),
                }
            )
        return pd.DataFrame(rows)
