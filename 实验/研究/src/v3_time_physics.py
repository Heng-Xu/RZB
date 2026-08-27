"""v3 站级时序物理门禁与储能回放。

QX-00005 110 kV 在 2025 年正式 40 台运行主变的 8760 点上按站
汇总、按日循环回放；其他片区/电压使用三类非概率经验时长情景。
经验曲线只决定物理可行性和储能定容，不冒充县域同步峰值。
"""
from __future__ import annotations

import json
import hashlib
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np
import pandas as pd
import yaml

from src.empirical_scenarios import build_empirical_duration_scenarios
from src.milp_planner import (
    _operation_limits,
    minimum_storage_modules,
    playback_daily_storage,
)
from src.v3_planner import StatePhysicsResult


class V3TimePhysicsError(ValueError):
    """时序物理输入、站址或回放门禁不满足。"""


@dataclass(frozen=True)
class StationProfileEvaluation:
    feasible: bool
    required_storage_modules: int
    forward_limit_mw: float
    reverse_limit_mw: float
    reason: str


@dataclass(frozen=True)
class _ProfileBundle:
    labels: tuple[str, ...]
    profiles: tuple[np.ndarray, ...]
    timestamps: tuple[tuple[str, ...], ...]
    basis: str
    synchronized_county_evidence: bool


@dataclass(frozen=True)
class _StationState:
    station_id: str
    evaluation: StationProfileEvaluation
    bundle: _ProfileBundle
    site_available: bool
    net_after_flat_mw: np.ndarray | None = None


@dataclass(frozen=True)
class _GroupState:
    result: StatePhysicsResult
    stations: tuple[_StationState, ...]


def _profile_violates_limits(
    profile: np.ndarray,
    forward_limit_mw: float,
    reverse_limit_mw: float,
    tolerance: float = 1e-9,
) -> bool:
    return bool(
        float(np.max(profile)) > forward_limit_mw + tolerance
        or float(-np.min(profile)) > reverse_limit_mw + tolerance
    )


def evaluate_station_profiles(
    profiles_mw: Iterable[Iterable[float]],
    *,
    unit_capacities_mva: Iterable[float],
    operation_modes: set[str],
    site_available: bool,
    contract: dict[str, Any],
    cos_phi: float | None = None,
) -> StationProfileEvaluation:
    """计算同一供电站内所有时长情景的最小整数储能柜数。"""
    profiles = tuple(np.asarray(list(profile), dtype=float) for profile in profiles_mw)
    if not profiles:
        raise V3TimePhysicsError("at least one station profile is required")
    if any(profile.shape != (24,) or not np.isfinite(profile).all() for profile in profiles):
        raise V3TimePhysicsError("each station profile must contain 24 finite values")
    capacities = [float(value) for value in unit_capacities_mva]
    if any(not math.isfinite(value) or value <= 0 for value in capacities):
        if capacities:
            raise V3TimePhysicsError("station unit capacities must be positive and finite")
    power_factor = (
        float(contract["technical_parameters"]["cos_phi"]["baseline"])
        if cos_phi is None
        else float(cos_phi)
    )
    split_beta = float(
        contract["technical_parameters"]["reverse_beta"]["split_or_single"]
    )
    forward_limit, reverse_limit = _operation_limits(
        capacities,
        {str(value).lower() for value in operation_modes},
        power_factor,
        split_beta,
    )
    active_profiles = tuple(
        profile
        for profile in profiles
        if _profile_violates_limits(profile, forward_limit, reverse_limit)
    )
    if not active_profiles:
        return StationProfileEvaluation(
            feasible=True,
            required_storage_modules=0,
            forward_limit_mw=forward_limit,
            reverse_limit_mw=reverse_limit,
            reason="no_storage_required",
        )
    modules = minimum_storage_modules(
        active_profiles,
        forward_limit,
        reverse_limit,
        contract,
    )
    if modules is None:
        return StationProfileEvaluation(
            feasible=False,
            required_storage_modules=0,
            forward_limit_mw=forward_limit,
            reverse_limit_mw=reverse_limit,
            reason="daily_storage_dispatch_infeasible",
        )
    if modules > 0 and not site_available:
        return StationProfileEvaluation(
            feasible=False,
            required_storage_modules=int(modules),
            forward_limit_mw=forward_limit,
            reverse_limit_mw=reverse_limit,
            reason="storage_required_but_no_available_connection_bay",
        )
    return StationProfileEvaluation(
        feasible=True,
        required_storage_modules=int(modules),
        forward_limit_mw=forward_limit,
        reverse_limit_mw=reverse_limit,
        reason="full_profile_set_feasible",
    )


def _parse_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def _parse_transformer_uids(row: pd.Series) -> tuple[str, ...]:
    raw = row.get("transformer_uids")
    if raw is not None and not (isinstance(raw, float) and math.isnan(raw)):
        if isinstance(raw, (list, tuple)):
            return tuple(str(value) for value in raw)
        text = str(raw).strip()
        if text:
            try:
                decoded = json.loads(text)
            except json.JSONDecodeError:
                decoded = [value for value in text.split(";") if value]
            if isinstance(decoded, list):
                return tuple(str(value) for value in decoded)
    source_ref = str(row.get("source_ref", ""))
    if row.get("candidate_type") == "retirement" and ":" in source_ref:
        return tuple(value for value in source_ref.split(":", 1)[1].split(";") if value)
    return ()


class V3TimePhysicsEvaluator:
    """在 v3 多年路径搜索中缓存 2025 终态站级时序检查。"""

    def __init__(
        self,
        processed_root: Path,
        working_root: Path,
        candidates: pd.DataFrame,
        contract_path: Path,
    ) -> None:
        self.processed_root = Path(processed_root).resolve()
        self.working_root = Path(working_root).resolve()
        self.contract_path = Path(contract_path).resolve()
        self.contract = yaml.safe_load(self.contract_path.read_text(encoding="utf-8"))
        self.candidates = candidates.copy()
        self.candidates["candidate_id"] = self.candidates["candidate_id"].astype(str)
        self.candidate_lookup = self.candidates.set_index("candidate_id", drop=False)
        self.master = self._operating_master()
        self.profiles: dict[tuple[str, int, str], _ProfileBundle] = {}
        self.synchronized_base_peaks: dict[
            tuple[str, int], tuple[float, float]
        ] = {}
        self._cache: dict[tuple[str, int, int, tuple[str, ...], float], _GroupState] = {}
        self._station_cache: dict[
            tuple[str, int, str, tuple[str, ...], tuple[float, ...], bool, float],
            _StationState,
        ] = {}
        self.working_root.mkdir(parents=True, exist_ok=True)
        self.scenario_manifest = build_empirical_duration_scenarios(
            self.processed_root,
            self.working_root,
            self.contract_path,
        )
        self._load_empirical_profiles()
        self._load_qx00005_exact_2025()

    def _operating_master(self) -> pd.DataFrame:
        master = pd.read_csv(self.processed_root / "transformer_master.csv")
        whitelist = pd.read_csv(self.processed_root / "annual_asset_whitelist.csv")
        operating = whitelist[
            whitelist["year"].eq(2025)
            & whitelist["asset_scope_id"].eq("operating_2025")
            & _parse_bool(whitelist["in_annual_operating_whitelist"])
        ][["transformer_uid"]]
        result = master.merge(operating, on="transformer_uid", how="inner", validate="one_to_one")
        if result.empty:
            raise V3TimePhysicsError("2025 operating transformer whitelist is empty")
        return result

    def _load_empirical_profiles(self) -> None:
        frame = pd.read_csv(self.working_root / "empirical_station_scenarios.csv.gz")
        for key, group in frame.groupby(
            ["region_id", "voltage_kv", "station_id"], sort=True
        ):
            labels: list[str] = []
            profiles: list[np.ndarray] = []
            timestamps: list[tuple[str, ...]] = []
            for label, scenario in group.groupby("duration_scenario", sort=True):
                ordered = scenario.sort_values("hour", kind="stable")
                values = ordered["net_load_mw"].to_numpy(dtype=float)
                if values.shape != (24,):
                    raise V3TimePhysicsError(f"{key}|{label}: empirical profile is not 24 hours")
                labels.append(str(label))
                profiles.append(values)
                timestamps.append(tuple(f"H{hour:02d}" for hour in range(24)))
            self.profiles[(str(key[0]), int(key[1]), str(key[2]))] = _ProfileBundle(
                labels=tuple(labels),
                profiles=tuple(profiles),
                timestamps=tuple(timestamps),
                basis="empirical_short_central_long_not_synchronous_county_profile",
                synchronized_county_evidence=False,
            )

    def _load_qx00005_exact_2025(self) -> None:
        usecols = [
            "timestamp",
            "transformer_uid",
            "region_id",
            "voltage_kv",
            "station_id",
            "net_load_mw",
            "formal_use_allowed",
        ]
        hourly = pd.read_csv(
            self.processed_root / "transformer_hourly_2025.csv.gz",
            usecols=usecols,
        )
        hourly = hourly[
            hourly["region_id"].astype(str).eq("QX-00005")
            & hourly["voltage_kv"].eq(110)
            & _parse_bool(hourly["formal_use_allowed"])
        ].copy()
        if hourly["transformer_uid"].nunique() != 40:
            raise V3TimePhysicsError("QX-00005 2025 formal playback requires exactly 40 transformers")
        hourly["timestamp"] = pd.to_datetime(hourly["timestamp"])
        station_hourly = hourly.groupby(
            ["station_id", "timestamp"], as_index=False
        )["net_load_mw"].sum(min_count=1)
        county_hourly = station_hourly.groupby("timestamp")["net_load_mw"].sum(min_count=1)
        raw_peak = float(county_hourly.max())
        reference = pd.read_csv(self.processed_root / "annual_reference.csv")
        anchor = reference[
            reference["year"].eq(2025)
            & reference["region_id"].astype(str).eq("QX-00005")
            & reference["voltage_kv"].eq(110)
        ]
        if len(anchor) != 1 or raw_peak <= 0:
            raise V3TimePhysicsError("QX-00005 official 2025 positive peak anchor is unavailable")
        official_peak = float(anchor.iloc[0]["official_positive_peak_mw"])
        scale = official_peak / raw_peak
        station_hourly["net_load_mw"] = station_hourly["net_load_mw"].astype(float) * scale
        scaled_county = station_hourly.groupby("timestamp")["net_load_mw"].sum(
            min_count=1
        )
        self.synchronized_base_peaks[("QX-00005", 110)] = (
            max(float(scaled_county.max()), 0.0),
            max(float(-scaled_county.min()), 0.0),
        )
        station_hourly["date"] = station_hourly["timestamp"].dt.date
        exact_stations = set(
            self.master[
                self.master["region_id"].astype(str).eq("QX-00005")
                & self.master["voltage_kv"].eq(110)
            ]["station_id"].astype(str)
        )
        for station_id in sorted(exact_stations):
            station = station_hourly[station_hourly["station_id"].astype(str).eq(station_id)]
            labels: list[str] = []
            profiles: list[np.ndarray] = []
            timestamps: list[tuple[str, ...]] = []
            for date, day in station.groupby("date", sort=True):
                ordered = day.sort_values("timestamp", kind="stable")
                values = ordered["net_load_mw"].to_numpy(dtype=float)
                if values.shape != (24,):
                    raise V3TimePhysicsError(f"QX-00005|110|{station_id}|{date}: incomplete day")
                labels.append(str(date))
                profiles.append(values)
                timestamps.append(
                    tuple(ordered["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S"))
                )
            if len(profiles) != 365:
                raise V3TimePhysicsError(
                    f"QX-00005|110|{station_id}: expected 365 complete playback days"
                )
            self.profiles[("QX-00005", 110, station_id)] = _ProfileBundle(
                labels=tuple(labels),
                profiles=tuple(profiles),
                timestamps=tuple(timestamps),
                basis=f"approved_2025_8760_scaled_to_official_peak_factor_{scale:.12g}",
                synchronized_county_evidence=True,
            )

    def evaluator(self, cos_phi: float) -> Callable[[str, int, int, tuple[str, ...]], StatePhysicsResult]:
        def evaluate(
            region_id: str,
            voltage_kv: int,
            year: int,
            selected_candidate_ids: tuple[str, ...],
        ) -> StatePhysicsResult:
            return self._evaluate_group(
                str(region_id),
                int(voltage_kv),
                int(year),
                tuple(sorted(selected_candidate_ids)),
                float(cos_phi),
            ).result

        return evaluate

    def _candidate_effects(
        self,
        selected_candidate_ids: tuple[str, ...],
    ) -> tuple[set[str], dict[str, list[float]], set[str]]:
        retired: set[str] = set()
        additions: dict[str, list[float]] = {}
        candidate_connection_sites: set[str] = set()
        for candidate_id in selected_candidate_ids:
            if candidate_id not in self.candidate_lookup.index:
                raise V3TimePhysicsError(f"unknown selected candidate: {candidate_id}")
            row = self.candidate_lookup.loc[candidate_id]
            if isinstance(row, pd.DataFrame):
                raise V3TimePhysicsError(f"duplicate candidate ID: {candidate_id}")
            if str(row["candidate_type"]) == "retirement":
                retired.update(_parse_transformer_uids(row))
                continue
            station_id = str(row.get("station_id", ""))
            new_capacity = row.get("new_capacity_mva")
            if station_id and pd.notna(new_capacity) and float(new_capacity) > 0:
                additions.setdefault(station_id, []).append(float(new_capacity))
                bays = pd.to_numeric(
                    pd.Series([row.get("available_10kv_bays")]), errors="coerce"
                ).fillna(0.0).iloc[0]
                if float(bays) > 0:
                    candidate_connection_sites.add(station_id)
        return retired, additions, candidate_connection_sites

    def _unselected_station_candidates(
        self,
        region_id: str,
        voltage_kv: int,
        station_id: str,
        selected_candidate_ids: tuple[str, ...],
    ) -> tuple[str, ...]:
        frame = self.candidates[
            self.candidates["region_id"].astype(str).eq(region_id)
            & self.candidates["voltage_kv"].astype(int).eq(voltage_kv)
            & self.candidates.get("station_id", pd.Series(index=self.candidates.index, dtype=str))
            .astype(str)
            .eq(station_id)
            & ~self.candidates["candidate_type"].astype(str).eq("retirement")
            & ~self.candidates["candidate_id"].isin(selected_candidate_ids)
        ].copy()
        usable: list[str] = []
        for row in frame.itertuples(index=False):
            values = row._asdict()
            eac = next(
                (
                    values.get(name)
                    for name in (
                        "eac_base_wanyuan_per_year",
                        "eac_center_wanyuan_per_year",
                        "eac_high_wanyuan_per_year",
                        "eac_low_wanyuan_per_year",
                    )
                    if pd.notna(values.get(name))
                ),
                None,
            )
            if eac is not None:
                usable.append(str(values["candidate_id"]))
        return tuple(sorted(usable))

    def _evaluate_group(
        self,
        region_id: str,
        voltage_kv: int,
        year: int,
        selected_candidate_ids: tuple[str, ...],
        cos_phi: float,
    ) -> _GroupState:
        key = (region_id, voltage_kv, year, selected_candidate_ids, round(cos_phi, 12))
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        if year != 2025:
            result = _GroupState(
                StatePhysicsResult(True, 0, reason="historical_device_scope_not_closed_no_hard_hourly_gate"),
                (),
            )
            self._cache[key] = result
            return result

        group = self.master[
            self.master["region_id"].astype(str).eq(region_id)
            & self.master["voltage_kv"].eq(voltage_kv)
        ].copy()
        if group.empty:
            result = _GroupState(
                StatePhysicsResult(False, 0, reason="missing_2025_operating_station_scope"),
                (),
            )
            self._cache[key] = result
            return result
        retired, additions, candidate_connection_sites = self._candidate_effects(
            selected_candidate_ids
        )
        station_states: list[_StationState] = []
        for station_id, base_units in group.groupby("station_id", sort=True):
            station_id = str(station_id)
            bundle = self.profiles.get((region_id, voltage_kv, station_id))
            if bundle is None:
                result = _GroupState(
                    StatePhysicsResult(
                        False,
                        0,
                        reason=f"{station_id}:missing_three_scenarios_or_exact_8760",
                    ),
                    tuple(station_states),
                )
                self._cache[key] = result
                return result
            retained = base_units[
                ~base_units["transformer_uid"].astype(str).isin(retired)
            ]
            retired_here = tuple(
                sorted(
                    set(base_units["transformer_uid"].astype(str)).intersection(retired)
                )
            )
            added_here = tuple(sorted(additions.get(station_id, [])))
            station_cache_key = (
                region_id,
                voltage_kv,
                station_id,
                retired_here,
                added_here,
                station_id in candidate_connection_sites,
                round(cos_phi, 12),
            )
            cached_station = self._station_cache.get(station_cache_key)
            if cached_station is not None:
                station_states.append(cached_station)
                if not cached_station.evaluation.feasible:
                    repair_ids = self._unselected_station_candidates(
                        region_id,
                        voltage_kv,
                        station_id,
                        selected_candidate_ids,
                    )
                    result = _GroupState(
                        StatePhysicsResult(
                            False,
                            sum(
                                item.evaluation.required_storage_modules
                                for item in station_states
                            ),
                            reason=(
                                f"{station_id}:"
                                f"{cached_station.evaluation.reason}"
                            ),
                            repair_candidate_ids=repair_ids,
                        ),
                        tuple(station_states),
                    )
                    self._cache[key] = result
                    return result
                continue
            capacities = retained["capacity_mva"].astype(float).tolist()
            capacities.extend(added_here)
            modes = set(retained["operation_mode"].dropna().astype(str).str.lower())
            if added_here:
                modes.add("unknown")
            site_available = bool(
                (
                    pd.to_numeric(
                        base_units["available_10kv_bays"], errors="coerce"
                    ).fillna(0.0)
                    > 0
                ).any()
            ) or station_id in candidate_connection_sites
            evaluation = evaluate_station_profiles(
                bundle.profiles,
                unit_capacities_mva=capacities,
                operation_modes=modes,
                site_available=site_available,
                contract=self.contract,
                cos_phi=cos_phi,
            )
            net_after_flat: np.ndarray | None = None
            if evaluation.feasible and bundle.synchronized_county_evidence:
                after_days: list[np.ndarray] = []
                for profile in bundle.profiles:
                    if _profile_violates_limits(
                        profile,
                        evaluation.forward_limit_mw,
                        evaluation.reverse_limit_mw,
                    ):
                        playback = playback_daily_storage(
                            profile,
                            evaluation.required_storage_modules,
                            evaluation.forward_limit_mw,
                            evaluation.reverse_limit_mw,
                            self.contract,
                        )
                        if not playback.feasible:
                            raise V3TimePhysicsError(
                                f"minimum storage failed playback: {station_id}"
                            )
                        after_days.append(playback.net_after_mw)
                    else:
                        after_days.append(profile.copy())
                net_after_flat = np.concatenate(after_days)
            state = _StationState(
                station_id=station_id,
                evaluation=evaluation,
                bundle=bundle,
                site_available=site_available,
                net_after_flat_mw=net_after_flat,
            )
            self._station_cache[station_cache_key] = state
            station_states.append(state)
            if not evaluation.feasible:
                repair_ids = self._unselected_station_candidates(
                    region_id,
                    voltage_kv,
                    station_id,
                    selected_candidate_ids,
                )
                result = _GroupState(
                    StatePhysicsResult(
                        False,
                        sum(item.evaluation.required_storage_modules for item in station_states),
                        reason=f"{station_id}:{evaluation.reason}",
                        repair_candidate_ids=repair_ids,
                    ),
                    tuple(station_states),
                )
                self._cache[key] = result
                return result

        required_modules = sum(
            item.evaluation.required_storage_modules for item in station_states
        )
        improvement_ids = tuple(
            sorted(
                {
                    candidate_id
                    for station in station_states
                    if station.evaluation.required_storage_modules > 0
                    for candidate_id in self._unselected_station_candidates(
                        region_id,
                        voltage_kv,
                        station.station_id,
                        selected_candidate_ids,
                    )
                }
            )
        )
        p_plus: float | None = None
        p_minus: float | None = None
        if region_id == "QX-00005" and voltage_kv == 110:
            aggregate: np.ndarray | None = None
            for station in station_states:
                station_after = station.net_after_flat_mw
                if station_after is None:
                    raise V3TimePhysicsError(
                        f"missing synchronized station playback: {station.station_id}"
                    )
                aggregate = (
                    station_after.copy()
                    if aggregate is None
                    else aggregate + station_after
                )
            if aggregate is None or aggregate.shape != (8760,):
                raise V3TimePhysicsError("QX-00005 synchronized playback did not form 8760 points")
            p_plus = max(float(aggregate.max()), 0.0)
            p_minus = max(float(-aggregate.min()), 0.0)
        result = _GroupState(
            StatePhysicsResult(
                True,
                int(required_modules),
                p_plus_mw=p_plus,
                p_minus_mw=p_minus,
                reason=(
                    "approved_2025_8760_station_playback_feasible"
                    if p_plus is not None
                    else "three_empirical_duration_scenarios_feasible"
                ),
                improvement_candidate_ids=improvement_ids,
            ),
            tuple(station_states),
        )
        self._cache[key] = result
        return result

    def write_selected_artifacts(
        self,
        planner: dict[str, pd.DataFrame],
        output_dir: Path,
        *,
        cos_phi: float,
    ) -> dict[str, Any]:
        """对最终两条优化路径写出状态门禁和逐时回放底稿。"""
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        years = planner["path_year_results"]
        actions = planner["path_action_results"]
        costs = planner["path_cost_breakdown"]
        audit_rows: list[dict[str, Any]] = []
        playback_rows: list[dict[str, Any]] = []
        tolerance = 2e-7
        module_energy = float(self.contract["storage"]["module"]["energy_mwh"])
        soc_min_fraction = float(self.contract["storage"]["soc"]["min_fraction"])

        for cost_row in costs.sort_values(
            ["path_id", "region_id", "voltage_kv"], kind="stable"
        ).itertuples(index=False):
            path_id = str(cost_row.path_id)
            region_id = str(cost_row.region_id)
            voltage_kv = int(cost_row.voltage_kv)
            group_actions = actions[
                actions["path_id"].astype(str).eq(path_id)
                & actions["region_id"].astype(str).eq(region_id)
                & actions["voltage_kv"].astype(int).eq(voltage_kv)
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
            state = self._evaluate_group(
                region_id,
                voltage_kv,
                2025,
                selected_ids,
                float(cos_phi),
            )
            year_row = years[
                years["path_id"].astype(str).eq(path_id)
                & years["region_id"].astype(str).eq(region_id)
                & years["voltage_kv"].astype(int).eq(voltage_kv)
                & years["year"].eq(2025)
            ]
            path_feasible = str(cost_row.status) == "feasible"
            installed_modules = (
                int(round(float(year_row.iloc[0]["storage_modules"])))
                if path_feasible and len(year_row) == 1
                else 0
            )
            physical_feasible = bool(state.result.feasible)
            audit_status = "feasible" if path_feasible and physical_feasible else "infeasible"
            audit_rows.append(
                {
                    "path_id": path_id,
                    "region_id": region_id,
                    "voltage_kv": voltage_kv,
                    "year": 2025,
                    "status": audit_status,
                    "optimization_status": str(cost_row.status),
                    "physical_reason": state.result.reason,
                    "installed_storage_modules": installed_modules,
                    "minimum_physical_storage_modules": int(
                        state.result.required_storage_modules
                    ),
                    "site_gate_passed": bool(path_feasible and physical_feasible),
                    "soc_gate_passed": bool(path_feasible and physical_feasible),
                    "synchronized_peak_recomputed": bool(
                        state.result.p_plus_mw is not None
                    ),
                    "p_plus_playback_mw": state.result.p_plus_mw,
                    "p_minus_playback_mw": state.result.p_minus_mw,
                    "selected_candidate_ids": json.dumps(
                        selected_ids, ensure_ascii=False
                    ),
                    "profile_method": (
                        "approved_2025_8760_station_playback_scaled_to_official_positive_peak"
                        if region_id == "QX-00005" and voltage_kv == 110
                        else "three_nonprobabilistic_empirical_duration_scenarios"
                    ),
                    "quality_flag": (
                        "EVIDENCE_A_2025_operating_scope"
                        if region_id == "QX-00005" and voltage_kv == 110
                        else "EVIDENCE_B_or_C_empirical_duration_transfer"
                    ),
                }
            )
            if not path_feasible or not physical_feasible:
                continue
            minimum_modules = sum(
                station.evaluation.required_storage_modules
                for station in state.stations
            )
            if installed_modules < minimum_modules:
                raise V3TimePhysicsError(
                    f"{path_id}|{region_id}|{voltage_kv}: installed storage below physical minimum"
                )
            allocation = {
                station.station_id: station.evaluation.required_storage_modules
                for station in state.stations
            }
            extra_modules = installed_modules - minimum_modules
            if extra_modules:
                extra_sites = [
                    station.station_id
                    for station in state.stations
                    if station.site_available
                ]
                if not extra_sites:
                    raise V3TimePhysicsError(
                        f"{path_id}|{region_id}|{voltage_kv}: no site for installed storage portfolio"
                    )
                allocation[sorted(extra_sites)[0]] += extra_modules

            for station in state.stations:
                modules = int(allocation[station.station_id])
                for profile_index, profile in enumerate(station.bundle.profiles):
                    if _profile_violates_limits(
                        profile,
                        station.evaluation.forward_limit_mw,
                        station.evaluation.reverse_limit_mw,
                    ):
                        playback = playback_daily_storage(
                            profile,
                            modules,
                            station.evaluation.forward_limit_mw,
                            station.evaluation.reverse_limit_mw,
                            self.contract,
                        )
                        charge = playback.charge_mw
                        discharge = playback.discharge_mw
                        soc = playback.soc_mwh
                        net_after = playback.net_after_mw
                        feasible = playback.feasible
                    else:
                        charge = np.zeros(24, dtype=float)
                        discharge = np.zeros(24, dtype=float)
                        soc = np.full(
                            24,
                            soc_min_fraction * modules * module_energy,
                            dtype=float,
                        )
                        net_after = profile.copy()
                        feasible = True
                    for hour in range(24):
                        violation = bool(
                            not feasible
                            or net_after[hour]
                            > station.evaluation.forward_limit_mw + tolerance
                            or -net_after[hour]
                            > station.evaluation.reverse_limit_mw + tolerance
                            or charge[hour] > max(-profile[hour], 0.0) + tolerance
                            or discharge[hour] > max(profile[hour], 0.0) + tolerance
                            or (
                                charge[hour] > tolerance
                                and discharge[hour] > tolerance
                            )
                        )
                        playback_rows.append(
                            {
                                "path_id": path_id,
                                "region_id": region_id,
                                "voltage_kv": voltage_kv,
                                "station_id": station.station_id,
                                "profile_label": station.bundle.labels[profile_index],
                                "hour": hour,
                                "timestamp": station.bundle.timestamps[profile_index][hour],
                                "profile_basis": station.bundle.basis,
                                "net_load_before_mw": float(profile[hour]),
                                "charge_mw": float(charge[hour]),
                                "discharge_mw": float(discharge[hour]),
                                "soc_mwh": float(soc[hour]),
                                "net_load_after_mw": float(net_after[hour]),
                                "installed_storage_modules_at_station": modules,
                                "minimum_storage_modules_at_station": int(
                                    station.evaluation.required_storage_modules
                                ),
                                "forward_limit_mw": station.evaluation.forward_limit_mw,
                                "reverse_limit_mw": station.evaluation.reverse_limit_mw,
                                "site_available": station.site_available,
                                "physical_violation": violation,
                                "simultaneous_charge_discharge": bool(
                                    charge[hour] > tolerance
                                    and discharge[hour] > tolerance
                                ),
                            }
                        )

        audit = pd.DataFrame(audit_rows)
        playback = pd.DataFrame(playback_rows)
        if audit.empty or playback.empty:
            raise V3TimePhysicsError("selected path physical artifacts cannot be empty")
        if playback["physical_violation"].any():
            raise V3TimePhysicsError("selected path failed storage physical playback")
        audit_path = output_dir / "path_physics_state_audit.csv"
        playback_path = output_dir / "path_storage_dispatch_playback.csv.gz"
        audit.to_csv(
            audit_path,
            index=False,
            lineterminator="\n",
            float_format="%.10g",
        )
        playback.sort_values(
            [
                "path_id",
                "voltage_kv",
                "region_id",
                "station_id",
                "profile_label",
                "hour",
            ],
            kind="stable",
        ).to_csv(
            playback_path,
            index=False,
            lineterminator="\n",
            float_format="%.10g",
            compression={"method": "gzip", "mtime": 0},
        )
        return {
            "path_physics_state_audit.csv": {
                "rows": int(len(audit)),
                "sha256": _sha256(audit_path),
            },
            "path_storage_dispatch_playback.csv.gz": {
                "rows": int(len(playback)),
                "sha256": _sha256(playback_path),
            },
        }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
