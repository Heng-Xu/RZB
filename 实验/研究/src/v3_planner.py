"""v3 多年度、路径分离的离散联合规划器。

规划器只接受离散候选和整数储能柜。2021 年容量是共同存量基准；动作从
2022 年起按年度投运并持续在役，目标把每年在役 EAC 相加到 2025 年。两条
优化路径使用同一候选集合和同一物理检查，严格路径只额外增加 ``R<=2``。
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Sequence

import numpy as np
import pandas as pd


YEARS = (2022, 2023, 2024, 2025)
PATH_OPT_UNBOUNDED = "PATH_OPT_CLR_UNBOUNDED"
PATH_OPT_STRICT = "PATH_OPT_CLR_LE_2"
OPT_PATHS = (PATH_OPT_UNBOUNDED, PATH_OPT_STRICT)


class V3PlannerError(ValueError):
    """v3 联合规划输入或物理/经济门禁不满足。"""


@dataclass(frozen=True)
class StatePhysicsResult:
    """候选状态的站级时序物理回放结果。

    ``p_plus_mw`` / ``p_minus_mw`` 只在有同步时序证据时返回；经验
    时长情景只用于物理可行性和储能定容，不伪造县域同步峰值。
    """

    feasible: bool
    required_storage_modules: int
    p_plus_mw: float | None = None
    p_minus_mw: float | None = None
    reason: str = "physical_playback_not_required"
    repair_candidate_ids: tuple[str, ...] = ()
    improvement_candidate_ids: tuple[str, ...] = ()


StatePhysicsEvaluator = Callable[
    [str, int, int, tuple[str, ...]], StatePhysicsResult
]


class V3StatePhysicsInfeasible(V3PlannerError):
    """保留时序回放给出的定向修复候选，用于搜索剪枝。"""

    def __init__(self, result: StatePhysicsResult) -> None:
        super().__init__(f"state physics infeasible: {result.reason}")
        self.result = result


@dataclass(frozen=True)
class _Candidate:
    candidate_id: str
    candidate_type: str
    delta_capacity_mva: float
    capex_wanyuan: float
    eac_wanyuan_per_year: float
    cost_basis: str
    source_ref: str
    candidate_group: str
    available_year: int


@dataclass
class _State:
    mask: int
    storage_modules: int
    cumulative_eac: float
    actions: list[dict[str, Any]]


def _finite(value: Any, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise V3PlannerError(f"{name} must be finite")
    return result


def _numeric_column(row: pd.Series, names: Sequence[str], default: float | None = None) -> float | None:
    for name in names:
        if name in row.index and pd.notna(row[name]):
            return _finite(row[name], name)
    return default


def _candidate_frame(frame: pd.DataFrame) -> list[_Candidate]:
    if frame.empty:
        return []
    required = {"candidate_id", "candidate_type", "delta_capacity_mva"}
    missing = required - set(frame.columns)
    if missing:
        raise V3PlannerError(f"candidate frame missing {sorted(missing)}")
    if frame["candidate_id"].duplicated().any():
        raise V3PlannerError("candidate_id must be unique in the shared candidate set")
    candidates: list[_Candidate] = []
    for row in frame.itertuples(index=False):
        values = row._asdict()
        candidate_id = str(values["candidate_id"])
        delta = _finite(values["delta_capacity_mva"], "delta_capacity_mva")
        capex = _numeric_column(pd.Series(values), ("capex_base_wanyuan", "capex_center_wanyuan", "capex_high_wanyuan", "capex_low_wanyuan"))
        eac = _numeric_column(pd.Series(values), ("eac_base_wanyuan_per_year", "eac_center_wanyuan_per_year", "eac_high_wanyuan_per_year", "eac_low_wanyuan_per_year"))
        if capex is None or eac is None or capex < 0 or eac < 0:
            # 未闭合的成本候选保留在成本库，但不能进入可排名的优化解。
            continue
        if str(values.get("cost_status", "")).startswith("cost_gap") and "eac_base_wanyuan_per_year" not in values:
            continue
        raw_group = values.get("candidate_group")
        candidate_group = (
            candidate_id
            if raw_group is None or pd.isna(raw_group)
            else str(raw_group)
        )
        candidates.append(
            _Candidate(
                candidate_id=candidate_id,
                candidate_type=str(values["candidate_type"]),
                delta_capacity_mva=delta,
                capex_wanyuan=capex,
                eac_wanyuan_per_year=eac,
                cost_basis=(
                    "base"
                    if "eac_base_wanyuan_per_year" in values and pd.notna(values.get("eac_base_wanyuan_per_year"))
                    else "center"
                    if "eac_center_wanyuan_per_year" in values and pd.notna(values.get("eac_center_wanyuan_per_year"))
                    else "range_high_or_low"
                ),
                source_ref=str(values.get("source_ref", "candidate_table")),
                candidate_group=candidate_group,
                available_year=int(
                    _numeric_column(
                        pd.Series(values), ("available_year",), default=2022.0
                    )
                    or 2022
                ),
            )
        )
        if candidates[-1].available_year not in YEARS:
            raise V3PlannerError("candidate available_year must be within 2022-2025")
    return candidates


def _required_storage_modules(
    capacity_mva: float,
    positive_peak_mw: float,
    reverse_peak_mw: float,
    forward_requirement_mw: float,
    reverse_requirement_mw: float,
    reverse_beta_value: float,
    previous_modules: int,
    *,
    cos_phi: float,
    module_power_mw: float,
    path_id: str,
    clr_limit: float,
    clr_reporting_mva: float | None = None,
) -> tuple[int, float, float, float, float, float, float, tuple[str, ...]]:
    if module_power_mw <= 0:
        raise V3PlannerError("storage module power must be positive")
    forward_gap = max(forward_requirement_mw - capacity_mva * cos_phi, 0.0)
    reverse_gap = max(reverse_requirement_mw - capacity_mva * cos_phi * reverse_beta_value, 0.0)
    if forward_gap > positive_peak_mw + 1e-9:
        raise V3PlannerError("forward capacity requirement exceeds locally available positive peak")
    forward_modules = int(math.ceil(forward_gap / module_power_mw - 1e-10))
    reverse_modules = int(math.ceil(reverse_gap / module_power_mw - 1e-10))
    required = max(forward_modules, reverse_modules)
    modules = max(int(previous_modules), required)
    forward_power = forward_modules * module_power_mw
    reverse_power = reverse_modules * module_power_mw
    if forward_power > positive_peak_mw + 1e-8:
        raise V3PlannerError("storage discharge would exceed locally available positive power")
    if reverse_power > max(reverse_peak_mw, reverse_requirement_mw) + 1e-8:
        raise V3PlannerError("storage charge would exceed locally available reverse power")
    # 静态设备缺口可以给出储能功率下界，但不具有县域同步时序
    # 证据，因此不能直接从官方正向峰值中扣减后改写 CLR 分母。
    # 只有下游 state_physics_evaluator 的同步回放才能覆盖正/反向峰值。
    p_plus = positive_peak_mw
    p_minus = reverse_peak_mw
    if path_id == PATH_OPT_STRICT:
        # 3.1.0：CLR 按报告口径容量（归一约定起点）核算；物理容量只用于缺口与储能定容。
        reporting = capacity_mva if clr_reporting_mva is None else clr_reporting_mva
        if p_plus <= 1e-12 or reporting / p_plus > clr_limit + 1e-9:
            raise V3PlannerError("strict CLR limit is infeasible for this installed state")
    return modules, p_plus, p_minus, forward_gap, reverse_gap, forward_power, reverse_power


def _evaluate_state(
    state_mask: int,
    previous_storage: int,
    candidates: list[_Candidate],
    annual_row: pd.Series,
    path_id: str,
    *,
    cos_phi: float,
    module_power_mw: float,
    clr_limit: float,
    state_physics_evaluator: StatePhysicsEvaluator | None = None,
) -> tuple[int, float, float, float, float, float, float]:
    # Counterfactual paths must remain on the approved 2021 common asset
    # baseline.  ``capacity_mva`` may retain the factual annual anchor for
    # audit, but factual 2022--2025 asset changes are not free optimization
    # actions and therefore cannot enter the path capacity state.
    base_capacity = _finite(
        annual_row.get("baseline_capacity_mva", annual_row["capacity_mva"]),
        "baseline_capacity_mva",
    )
    positive_peak = max(_finite(annual_row["positive_peak_mw"], "positive_peak_mw"), 0.0)
    reverse_peak = max(_finite(annual_row.get("reverse_peak_mw", 0.0), "reverse_peak_mw"), 0.0)
    beta = _finite(annual_row.get("reverse_beta", 0.8), "reverse_beta")
    forward_requirement = max(
        _finite(annual_row.get("forward_requirement_mw", positive_peak), "forward_requirement_mw"),
        positive_peak,
    )
    reverse_requirement = max(
        _finite(annual_row.get("reverse_requirement_mw", reverse_peak), "reverse_requirement_mw"),
        reverse_peak,
    )
    capacity = base_capacity + sum(candidate.delta_capacity_mva for index, candidate in enumerate(candidates) if state_mask & (1 << index))
    if capacity <= 0:
        raise V3PlannerError("installed capacity must remain positive")
    # 3.1.0 记账口径：报告容量 = 归一约定起点 + 同一动作增量；物理容量不变。
    reported_base = _numeric_column(
        annual_row, ("reported_baseline_capacity_mva",), default=base_capacity
    )
    reported_capacity = reported_base + sum(
        candidate.delta_capacity_mva for index, candidate in enumerate(candidates) if state_mask & (1 << index)
    )
    if reported_capacity <= 0:
        raise V3PlannerError("reported installed capacity must remain positive")
    modules, p_plus, p_minus, forward_gap, reverse_gap, _forward_power, reverse_power = _required_storage_modules(
        capacity,
        positive_peak,
        reverse_peak,
        forward_requirement,
        reverse_requirement,
        beta,
        previous_storage,
        cos_phi=cos_phi,
        module_power_mw=module_power_mw,
        path_id=path_id,
        clr_limit=clr_limit,
        clr_reporting_mva=reported_capacity,
    )
    if state_physics_evaluator is not None:
        selected_ids = tuple(
            sorted(
                candidate.candidate_id
                for index, candidate in enumerate(candidates)
                if state_mask & (1 << index)
            )
        )
        physics = state_physics_evaluator(
            str(annual_row["region_id"]),
            int(annual_row["voltage_kv"]),
            int(annual_row["year"]),
            selected_ids,
        )
        if not isinstance(physics, StatePhysicsResult):
            raise V3PlannerError("state physics evaluator must return StatePhysicsResult")
        if not physics.feasible:
            raise V3StatePhysicsInfeasible(physics)
        required_modules = physics.required_storage_modules
        if isinstance(required_modules, bool) or not isinstance(required_modules, int):
            raise V3PlannerError("state physics storage modules must be an integer")
        if required_modules < 0:
            raise V3PlannerError("state physics storage modules must be nonnegative")
        modules = max(modules, required_modules)
        if physics.p_plus_mw is not None:
            p_plus = max(_finite(physics.p_plus_mw, "state_physics.p_plus_mw"), 0.0)
        if physics.p_minus_mw is not None:
            p_minus = max(_finite(physics.p_minus_mw, "state_physics.p_minus_mw"), 0.0)
        if path_id == PATH_OPT_STRICT and (
            p_plus <= 1e-12 or reported_capacity / p_plus > clr_limit + 1e-9
        ):
            raise V3PlannerError(
                "strict CLR limit is infeasible after synchronized physical playback"
            )
    # Storage can remove a physical forward/reverse gap, but it never counts as
    # a capacity addition and R is always recomputed from this path's p_plus.
    reverse_requirement_gap = max(
        reverse_requirement - capacity * cos_phi * beta - reverse_power,
        0.0,
    )
    branch_candidate_ids = (
        physics.improvement_candidate_ids
        if state_physics_evaluator is not None
        else ()
    )
    return (
        modules,
        capacity,
        p_plus,
        p_minus,
        forward_gap,
        reverse_requirement_gap,
        reported_capacity / p_plus if p_plus > 0 else float("inf"),
        tuple(branch_candidate_ids),
    )


def _append_candidate_actions(
    actions: list[dict[str, Any]],
    selected_mask: int,
    previous_mask: int,
    candidates: list[_Candidate],
    year: int,
) -> list[dict[str, Any]]:
    result = list(actions)
    for index, candidate in enumerate(candidates):
        bit = 1 << index
        if selected_mask & bit and not previous_mask & bit:
            result.append(
                {
                    "year": year,
                    "action_id": candidate.candidate_id,
                    "candidate_id": candidate.candidate_id,
                    "action_type": candidate.candidate_type,
                    "delta_capacity_mva": candidate.delta_capacity_mva,
                    "storage_modules_delta": 0,
                    "capex_wanyuan": candidate.capex_wanyuan,
                    "eac_wanyuan_per_year": candidate.eac_wanyuan_per_year,
                    "cost_basis": candidate.cost_basis,
                    "source_ref": candidate.source_ref,
                }
            )
    return result


def _replay_final_path_year_rows(
    final_state: _State,
    annual_group: pd.DataFrame,
    candidates: list[_Candidate],
    group_key: tuple[Any, Any],
    path_id: str,
    years: Sequence[int],
    *,
    cos_phi: float,
    module_power_mw: float,
    clr_limit: float,
    state_physics_evaluator: StatePhysicsEvaluator | None = None,
) -> list[dict[str, Any]]:
    """按 2025 年最终最优动作逐年回放同一条正式路径。"""
    candidate_index = {
        candidate.candidate_id: index for index, candidate in enumerate(candidates)
    }
    rows: list[dict[str, Any]] = []
    actions = list(final_state.actions)
    for year in years:
        annual_row = annual_group[annual_group["year"].eq(year)].iloc[0]
        in_service_actions = [
            action for action in actions if int(action["year"]) <= year
        ]
        selected_mask = 0
        for action in in_service_actions:
            candidate_id = str(action.get("candidate_id", ""))
            if not candidate_id:
                continue
            if candidate_id not in candidate_index:
                raise V3PlannerError(
                    f"final action references unknown candidate: {candidate_id}"
                )
            selected_mask |= 1 << candidate_index[candidate_id]
        storage_modules = sum(
            int(action.get("storage_modules_delta", 0))
            for action in in_service_actions
        )
        (
            evaluated_modules,
            capacity,
            p_plus,
            p_minus,
            forward_gap,
            reverse_gap,
            clr,
            _branch_candidate_ids,
        ) = _evaluate_state(
            selected_mask,
            storage_modules,
            candidates,
            annual_row,
            path_id,
            cos_phi=cos_phi,
            module_power_mw=module_power_mw,
            clr_limit=clr_limit,
            state_physics_evaluator=state_physics_evaluator,
        )
        if evaluated_modules != storage_modules:
            raise V3PlannerError(
                "final path action history does not reproduce required storage modules"
            )
        annual_capex = sum(
            float(action["capex_wanyuan"])
            for action in actions
            if int(action["year"]) == year
        )
        annual_in_service = sum(
            float(action["eac_wanyuan_per_year"])
            for action in in_service_actions
        )
        cumulative_capex = sum(
            float(action["capex_wanyuan"])
            for action in in_service_actions
        )
        cumulative_annual_eac = sum(
            float(action["eac_wanyuan_per_year"])
            * (year - int(action["year"]) + 1)
            for action in in_service_actions
        )
        rows.append(
            {
                "year": year,
                "region_id": group_key[0],
                "voltage_kv": int(group_key[1]),
                "path_id": path_id,
                "status": "feasible",
                "reason": "feasible",
                "installed_capacity_mva": capacity,
                "reported_capacity_mva": (clr * p_plus) if p_plus > 0 else None,
                "storage_modules": evaluated_modules,
                "storage_power_mw": evaluated_modules * module_power_mw,
                "p_plus_mw": p_plus,
                "p_minus_mw": p_minus,
                "clr": clr,
                "positive_capacity_gap_mw": max(
                    forward_gap - evaluated_modules * module_power_mw,
                    0.0,
                ),
                "reverse_hosting_gap_mw": reverse_gap,
                "annual_capex_wanyuan": annual_capex,
                "annual_in_service_eac_wanyuan": annual_in_service,
                "cumulative_capex_wanyuan": cumulative_capex,
                "cumulative_in_service_eac_wanyuan": cumulative_annual_eac,
            }
        )
    if rows and not math.isclose(
        float(rows[-1]["cumulative_in_service_eac_wanyuan"]),
        final_state.cumulative_eac,
        rel_tol=0.0,
        abs_tol=1e-7,
    ):
        raise V3PlannerError(
            "final path replay cumulative EAC does not match optimized state"
        )
    return rows


def optimize_path(
    annual: pd.DataFrame,
    candidates: pd.DataFrame,
    *,
    path_id: str,
    years: Sequence[int] = YEARS,
    cos_phi: float = 0.95,
    clr_limit: float = 2.0,
    module_power_mw: float = 0.1,
    module_capex_wanyuan: float = 27.2,
    module_eac_wanyuan_per_year: float = 4.5,
    storage_capex_wanyuan_for_modules: Callable[[int], float] | None = None,
    storage_eac_wanyuan_for_modules: Callable[[int], float] | None = None,
    state_physics_evaluator: StatePhysicsEvaluator | None = None,
) -> dict[str, pd.DataFrame]:
    """按县区/电压独立求解一条优化路径，再合并为路径结果。"""
    if path_id not in OPT_PATHS:
        raise V3PlannerError(f"unknown optimization path: {path_id}")
    years = tuple(int(year) for year in years)
    if years != YEARS:
        raise V3PlannerError("v3 joint planner decision years must be 2022-2025")
    required = {"year", "region_id", "voltage_kv", "capacity_mva", "positive_peak_mw"}
    missing = required - set(annual.columns)
    if missing:
        raise V3PlannerError(f"annual frame missing {sorted(missing)}")
    if annual.duplicated(["year", "region_id", "voltage_kv"]).any():
        raise V3PlannerError("annual frame has duplicate year-region-voltage rows")
    candidate_objects = _candidate_frame(candidates)
    group_cols = ["region_id", "voltage_kv"]
    year_rows: list[dict[str, Any]] = []
    action_rows: list[dict[str, Any]] = []
    cost_rows: list[dict[str, Any]] = []
    annual = annual.copy()
    annual["year"] = annual["year"].astype(int)
    if set(annual["year"]) != set(years):
        raise V3PlannerError("each region-voltage group must have all four decision years")
    storage_capex = storage_capex_wanyuan_for_modules or (
        lambda modules: modules * module_capex_wanyuan
    )
    storage_eac = storage_eac_wanyuan_for_modules or (
        lambda modules: modules * module_eac_wanyuan_per_year
    )

    for group_key, group in annual.groupby(group_cols, sort=True):
        group = group.sort_values("year", kind="stable")
        group_candidates = list(candidate_objects)
        if "region_id" in candidates.columns and "voltage_kv" in candidates.columns:
            allowed_ids = set(
                candidates.loc[
                    candidates["region_id"].astype(str).eq(str(group_key[0]))
                    & candidates["voltage_kv"].astype(int).eq(int(group_key[1])),
                    "candidate_id",
                ].astype(str)
            )
            group_candidates = [candidate for candidate in candidate_objects if candidate.candidate_id in allowed_ids]
        states: dict[tuple[int, int], _State] = {(0, 0): _State(0, 0, 0.0, [])}
        group_year_rows: list[dict[str, Any]] = []
        for year in years:
            annual_row = group[group["year"].eq(year)].iloc[0]
            previous_states = states
            next_states: dict[tuple[int, int], _State] = {}
            for (previous_mask, previous_storage), previous in previous_states.items():
                # Enumerate all discrete candidate supersets that can be
                # installed in this year; no candidate can be installed twice.
                stack = [previous_mask]
                visited = {previous_mask}
                while stack:
                    mask = stack.pop()
                    directed_branch_ids: set[str] | None = None
                    try:
                        (
                            modules,
                            capacity,
                            p_plus,
                            p_minus,
                            forward_gap,
                            reverse_gap,
                            clr,
                            branch_candidate_ids,
                        ) = _evaluate_state(
                            mask,
                            previous_storage,
                            group_candidates,
                            annual_row,
                            path_id,
                            cos_phi=cos_phi,
                            module_power_mw=module_power_mw,
                            clr_limit=clr_limit,
                            state_physics_evaluator=state_physics_evaluator,
                        )
                    except V3StatePhysicsInfeasible as exc:
                        directed_branch_ids = set(exc.result.repair_candidate_ids)
                        modules = capacity = p_plus = p_minus = forward_gap = reverse_gap = clr = None  # type: ignore[assignment]
                        branch_candidate_ids = ()
                    except V3PlannerError:
                        modules = capacity = p_plus = p_minus = forward_gap = reverse_gap = clr = None  # type: ignore[assignment]
                        branch_candidate_ids = ()
                    trigger_requires_measure = bool(annual_row.get("measure_trigger_required", False))
                    measure_in_service = bool(mask) or bool(modules)
                    if modules is not None and (not trigger_requires_measure or measure_in_service):
                        new_candidate_actions = _append_candidate_actions(
                            previous.actions, mask, previous_mask, group_candidates, year
                        )
                        new_candidate_ids = {
                            action["candidate_id"] for action in new_candidate_actions
                            if action["year"] == year and action["action_type"] != "storage"
                        }
                        candidate_cost = sum(
                            candidate.eac_wanyuan_per_year * (2025 - year + 1)
                            for candidate in group_candidates
                            if candidate.candidate_id in new_candidate_ids
                        )
                        storage_delta = int(modules - previous_storage)
                        storage_delta_capex = _finite(
                            storage_capex(storage_delta),
                            "storage_delta_capex_wanyuan",
                        )
                        storage_delta_eac = _finite(
                            storage_eac(storage_delta),
                            "storage_delta_eac_wanyuan_per_year",
                        )
                        if storage_delta_capex < 0 or storage_delta_eac < 0:
                            raise V3PlannerError("storage action costs must be nonnegative")
                        storage_cost = storage_delta_eac * (2025 - year + 1)
                        total_cost = previous.cumulative_eac + candidate_cost + storage_cost
                        actions = list(new_candidate_actions)
                        if storage_delta:
                            actions.append(
                                {
                                    "year": year,
                                    "action_id": f"STORAGE-{group_key[0]}-{group_key[1]}-{year}",
                                    "candidate_id": "",
                                    "action_type": "storage",
                                    "delta_capacity_mva": 0.0,
                                    "storage_modules_delta": storage_delta,
                                    "capex_wanyuan": storage_delta_capex,
                                    "eac_wanyuan_per_year": storage_delta_eac,
                                    "cost_basis": "contract_storage_module",
                                    "source_ref": "model_contract.yaml+储能成本依据",
                                }
                            )
                        state = _State(mask, modules, total_cost, actions)
                        key = (mask, modules)
                        old = next_states.get(key)
                        if old is None or (state.cumulative_eac, str(state.actions)) < (old.cumulative_eac, str(old.actions)):
                            next_states[key] = state
                        if year != 2025 or not branch_candidate_ids:
                            continue
                        directed_branch_ids = set(branch_candidate_ids)
                    selected_groups = {
                        candidate.candidate_group
                        for index, candidate in enumerate(group_candidates)
                        if mask & (1 << index)
                    }
                    physical_base = _finite(
                        annual_row.get(
                            "baseline_capacity_mva",
                            annual_row["capacity_mva"],
                        ),
                        "baseline_capacity_mva",
                    )
                    reported_base = _numeric_column(
                        annual_row,
                        ("reported_baseline_capacity_mva",),
                        default=physical_base,
                    )
                    current_capacity = reported_base + sum(
                        candidate.delta_capacity_mva
                        for index, candidate in enumerate(group_candidates)
                        if mask & (1 << index)
                    )
                    # For the strict path, p_plus can never exceed the raw
                    # positive peak because storage only serves local load.
                    # Once installed capacity is already above 2*p_plus_raw,
                    # adding a nonnegative-capacity candidate cannot restore
                    # R<=2.  Keep only the discrete reduction/retirement
                    # branches in this part of the search tree.  This is a
                    # physical dominance rule, not a candidate deletion: all
                    # candidates remain in the shared cost library and can be
                    # considered once the capacity bound is restored.
                    strict_positive_bound = (
                        path_id == PATH_OPT_STRICT
                        and current_capacity
                        > clr_limit * _finite(annual_row["positive_peak_mw"], "positive_peak_mw") + 1e-9
                    )
                    remaining = ((1 << len(group_candidates)) - 1) ^ mask
                    bit = remaining
                    while bit:
                        one = bit & -bit
                        bit -= one
                        candidate_index = int(math.log2(one))
                        if (
                            directed_branch_ids is not None
                            and group_candidates[candidate_index].candidate_id
                            not in directed_branch_ids
                        ):
                            continue
                        if group_candidates[candidate_index].available_year > year:
                            continue
                        if strict_positive_bound and group_candidates[candidate_index].delta_capacity_mva >= -1e-12:
                            continue
                        if group_candidates[candidate_index].candidate_group in selected_groups:
                            continue
                        candidate_mask = mask | one
                        if candidate_mask not in visited:
                            visited.add(candidate_mask)
                            stack.append(candidate_mask)
            if not next_states:
                # Preserve one explicit infeasible row per year for the formal
                # technical appendix rather than silently dropping a path.
                group_year_rows.append(
                    {
                        "year": year,
                        "region_id": group_key[0],
                        "voltage_kv": int(group_key[1]),
                        "path_id": path_id,
                        "status": "infeasible",
                        "reason": "no_discrete_candidate_storage_state_satisfies_physical_and_path_constraints",
                    }
                )
                states = {}
                continue
            states = next_states
            best = min(states.values(), key=lambda item: (item.cumulative_eac, item.mask, item.storage_modules))
            annual_in_service = sum(float(action["eac_wanyuan_per_year"]) for action in best.actions if int(action["year"]) <= year)
            annual_capex = sum(float(action["capex_wanyuan"]) for action in best.actions if int(action["year"]) == year)
            cumulative_capex = sum(float(action["capex_wanyuan"]) for action in best.actions if int(action["year"]) <= year)
            prior_rows = [row for row in group_year_rows if row.get("status") == "feasible"]
            cumulative_annual_eac = sum(float(row["annual_in_service_eac_wanyuan"]) for row in prior_rows) + annual_in_service
            (
                modules,
                capacity,
                p_plus,
                p_minus,
                forward_gap,
                reverse_gap,
                clr,
                _branch_candidate_ids,
            ) = _evaluate_state(
                best.mask,
                best.storage_modules,
                group_candidates,
                annual_row,
                path_id,
                cos_phi=cos_phi,
                module_power_mw=module_power_mw,
                clr_limit=clr_limit,
                state_physics_evaluator=state_physics_evaluator,
            )
            group_year_rows.append(
                {
                    "year": year,
                    "region_id": group_key[0],
                    "voltage_kv": int(group_key[1]),
                    "path_id": path_id,
                    "status": "feasible",
                    "reason": "feasible",
                    "installed_capacity_mva": capacity,
                    "reported_capacity_mva": (clr * p_plus) if p_plus > 0 else None,
                    "storage_modules": modules,
                    "storage_power_mw": modules * module_power_mw,
                    "p_plus_mw": p_plus,
                    "p_minus_mw": p_minus,
                    "clr": clr,
                    "positive_capacity_gap_mw": max(forward_gap - modules * module_power_mw, 0.0),
                    "reverse_hosting_gap_mw": reverse_gap,
                    "annual_capex_wanyuan": annual_capex,
                    "annual_in_service_eac_wanyuan": annual_in_service,
                    "cumulative_capex_wanyuan": cumulative_capex,
                    "cumulative_in_service_eac_wanyuan": cumulative_annual_eac,
                }
            )
        final_state = (
            min(
                states.values(),
                key=lambda item: (
                    item.cumulative_eac,
                    item.mask,
                    item.storage_modules,
                ),
            )
            if states
            else None
        )
        if final_state is not None:
            group_year_rows = _replay_final_path_year_rows(
                final_state,
                group,
                group_candidates,
                group_key,
                path_id,
                years,
                cos_phi=cos_phi,
                module_power_mw=module_power_mw,
                clr_limit=clr_limit,
                state_physics_evaluator=state_physics_evaluator,
            )
            action_rows.extend(
                [
                    {
                        **action,
                        "region_id": group_key[0],
                        "voltage_kv": int(group_key[1]),
                        "path_id": path_id,
                    }
                    for action in final_state.actions
                ]
            )
            for row in group_year_rows:
                row["complete_path_status"] = "feasible"
                row["complete_path_reason"] = "complete_2022_2025_feasible_path"
        else:
            # Preserve annual prefix diagnostics, but distinguish them from a
            # publishable complete four-year path.  A feasible prefix is not a
            # feasible 2022--2025 path when no terminal continuation exists.
            for row in group_year_rows:
                row["complete_path_status"] = "infeasible"
                row["complete_path_reason"] = (
                    "no_complete_2022_2025_feasible_path"
                )
        year_rows.extend(group_year_rows)
        final_cost = (
            float(final_state.cumulative_eac)
            if final_state is not None
            else float("inf")
        )
        final_action_count = len(final_state.actions) if final_state is not None else 0
        cost_rows.append(
            {
                "path_id": path_id,
                "region_id": group_key[0],
                "voltage_kv": int(group_key[1]),
                "status": "feasible" if states else "infeasible",
                "cumulative_in_service_eac_wanyuan": final_cost,
                "selected_action_count": final_action_count,
            }
        )

    years_result = pd.DataFrame(year_rows)
    actions_result = pd.DataFrame(action_rows)
    costs_result = pd.DataFrame(cost_rows)
    if actions_result.empty:
        actions_result = pd.DataFrame(columns=["path_id", "region_id", "voltage_kv", "year", "candidate_id", "action_type"])
    return {
        "path_year_results": years_result,
        "path_action_results": actions_result,
        "path_cost_breakdown": costs_result,
    }


def optimize_joint_paths(
    annual: pd.DataFrame,
    candidates: pd.DataFrame,
    **kwargs: Any,
) -> dict[str, pd.DataFrame]:
    """使用完全相同输入分别求解不限制与严格路径。"""
    outputs = []
    for path_id in OPT_PATHS:
        outputs.append(optimize_path(annual, candidates, path_id=path_id, **kwargs))
    return {
        "path_year_results": pd.concat([item["path_year_results"] for item in outputs], ignore_index=True, sort=False),
        "path_action_results": pd.concat([item["path_action_results"] for item in outputs], ignore_index=True, sort=False),
        "path_cost_breakdown": pd.concat([item["path_cost_breakdown"] for item in outputs], ignore_index=True, sort=False),
    }


def validate_path_inclusion(cost_breakdown: pd.DataFrame) -> bool:
    """验证不限制路径累计 EAC 不高于严格路径。"""
    required = {
        "path_id",
        "region_id",
        "voltage_kv",
        "cumulative_in_service_eac_wanyuan",
    }
    if not required <= set(cost_breakdown.columns):
        raise V3PlannerError(f"cost breakdown missing {sorted(required - set(cost_breakdown.columns))}")
    for (region_id, voltage_kv), group in cost_breakdown.groupby(
        ["region_id", "voltage_kv"], sort=True
    ):
        rows = group.set_index("path_id")
        if PATH_OPT_UNBOUNDED not in rows.index or PATH_OPT_STRICT not in rows.index:
            raise V3PlannerError(
                f"both formal optimization paths are required for {region_id}|{voltage_kv}"
            )
        unbounded_row = rows.loc[PATH_OPT_UNBOUNDED]
        strict_row = rows.loc[PATH_OPT_STRICT]
        unbounded = float(unbounded_row["cumulative_in_service_eac_wanyuan"])
        strict = float(strict_row["cumulative_in_service_eac_wanyuan"])
        unbounded_feasible = (
            str(unbounded_row.get("status", "feasible")) == "feasible"
            and math.isfinite(unbounded)
        )
        strict_feasible = (
            str(strict_row.get("status", "feasible")) == "feasible"
            and math.isfinite(strict)
        )
        if strict_feasible and not unbounded_feasible:
            raise V3PlannerError(
                f"path feasible-set inclusion violated for {region_id}|{voltage_kv}: "
                "strict feasible while unbounded infeasible"
            )
        if unbounded_feasible and strict_feasible and unbounded > strict + 1e-7:
            raise V3PlannerError(
                f"path cost inclusion violated for {region_id}|{voltage_kv}: "
                f"unbounded={unbounded}, strict={strict}"
            )
    return True
