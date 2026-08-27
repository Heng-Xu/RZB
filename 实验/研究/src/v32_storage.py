"""v3.2 连续时序储能回放与最小整数定容。

与 :mod:`src.milp_planner` 的 24 h 日循环模型并存。本模块用于 QX-00005
等具备 A 级连续时序证据的年度/跨日校核：SOC 在所有小时之间连续传递，
只在整个输入时序首尾建立循环边界，不在每个自然日强制闭合。
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix


MAX_CONTINUOUS_STORAGE_MODULES = 100_000


@dataclass(frozen=True)
class ContinuousStoragePlayback:
    feasible: bool
    charge_mw: np.ndarray
    discharge_mw: np.ndarray
    soc_mwh: np.ndarray
    net_after_mw: np.ndarray
    reason: str
    soc_residual_mwh: float


def _empty(profile: np.ndarray, reason: str) -> ContinuousStoragePlayback:
    zeros = np.zeros(len(profile), dtype=float)
    return ContinuousStoragePlayback(
        feasible=False,
        charge_mw=zeros.copy(),
        discharge_mw=zeros.copy(),
        soc_mwh=zeros.copy(),
        net_after_mw=np.asarray(profile, dtype=float).copy(),
        reason=reason,
        soc_residual_mwh=float("nan"),
    )


def playback_continuous_storage(
    profile_mw: Iterable[float],
    *,
    storage_modules: int,
    forward_limit_mw: float,
    reverse_limit_mw: float,
    contract: dict[str, Any],
) -> ContinuousStoragePlayback:
    """验证固定整数储能规模在连续小时序列上的物理可行性。

    规则与现有日循环模型保持一致：
    - 原始净负荷为负时才允许充电，且不得通过充电跨过零点；
    - 原始净负荷为正时才允许放电，且不得通过放电形成反向送电；
    - 禁止同时充放电；
    - SOC 受上下限、充放电效率约束；
    - 仅要求整个输入序列首尾 SOC 闭合。
    """
    if isinstance(storage_modules, bool) or not isinstance(storage_modules, int):
        raise ValueError("storage_modules must be an integer")
    if storage_modules < 0:
        raise ValueError("storage_modules must be nonnegative")

    profile = np.asarray(list(profile_mw), dtype=float)
    if profile.ndim != 1 or profile.size < 2 or not np.isfinite(profile).all():
        raise ValueError("profile_mw must be a finite one-dimensional series with at least two hours")

    forward_limit = float(forward_limit_mw)
    reverse_limit = float(reverse_limit_mw)
    if not math.isfinite(forward_limit) or not math.isfinite(reverse_limit):
        raise ValueError("physical limits must be finite")
    if forward_limit < 0 or reverse_limit < 0:
        raise ValueError("physical limits must be nonnegative")

    storage = contract["storage"]
    module = storage["module"]
    efficiency = storage["efficiency"]
    soc_cfg = storage["soc"]
    power = storage_modules * float(module["power_mw"])
    energy = storage_modules * float(module["energy_mwh"])
    eta_charge = float(efficiency["charge"])
    eta_discharge = float(efficiency["discharge"])
    if power < 0 or energy < 0 or not (0 < eta_charge <= 1) or not (0 < eta_discharge <= 1):
        raise ValueError("invalid storage module or efficiency parameters")

    reverse_required = np.maximum(-profile - reverse_limit, 0.0)
    forward_required = np.maximum(profile - forward_limit, 0.0)
    charge_upper = np.minimum(power, np.maximum(-profile, 0.0))
    discharge_upper = np.minimum(power, np.maximum(profile, 0.0))
    if np.any(reverse_required > charge_upper + 1e-10):
        return _empty(profile, "storage_power_insufficient_for_reverse_limit")
    if np.any(forward_required > discharge_upper + 1e-10):
        return _empty(profile, "storage_power_insufficient_for_forward_limit")

    n = int(profile.size)
    # 变量顺序：charge[n], discharge[n], soc_after_hour[n]。
    objective = np.r_[np.ones(n), np.ones(n), np.zeros(n)]
    equality = lil_matrix((n, 3 * n), dtype=float)
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
    if not (0 <= soc_min <= soc_max <= energy + 1e-12):
        raise ValueError("invalid SOC limits")
    bounds.extend([(soc_min, soc_max)] * n)

    result = linprog(
        objective,
        A_eq=equality.tocsr(),
        b_eq=np.zeros(n),
        bounds=bounds,
        method="highs",
        options={"presolve": True},
    )
    if not result.success:
        return _empty(profile, f"continuous_soc_infeasible:{result.status}")

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
    return ContinuousStoragePlayback(
        feasible=valid,
        charge_mw=charge,
        discharge_mw=discharge,
        soc_mwh=soc,
        net_after_mw=net_after,
        reason="feasible" if valid else "post_solve_physical_assertion_failed",
        soc_residual_mwh=residual,
    )


def minimum_storage_modules_continuous(
    profile_mw: Iterable[float],
    *,
    forward_limit_mw: float,
    reverse_limit_mw: float,
    contract: dict[str, Any],
    max_modules: int = MAX_CONTINUOUS_STORAGE_MODULES,
) -> int | None:
    """返回连续时序上满足全部约束的最小整数储能柜数。"""
    profile = np.asarray(list(profile_mw), dtype=float)
    if profile.ndim != 1 or profile.size < 2 or not np.isfinite(profile).all():
        raise ValueError("profile_mw must be a finite one-dimensional series")
    module_power = float(contract["storage"]["module"]["power_mw"])
    if module_power <= 0:
        raise ValueError("storage module power must be positive")

    peak_deficit = max(
        float(np.maximum(-profile - float(reverse_limit_mw), 0.0).max()),
        float(np.maximum(profile - float(forward_limit_mw), 0.0).max()),
    )
    lower = max(0, int(math.ceil(peak_deficit / module_power - 1e-10)))

    def feasible(modules: int) -> bool:
        return playback_continuous_storage(
            profile,
            storage_modules=modules,
            forward_limit_mw=forward_limit_mw,
            reverse_limit_mw=reverse_limit_mw,
            contract=contract,
        ).feasible

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
