"""v3.2 年化 EAC 参数的受控敏感性场景注册。

年化参数属于冻结契约中的模型假设。本模块只从契约登记的 base/range
中构造少量有工程含义的定向场景，不扩展参数范围，也不改变主模型默认值。
"""
from __future__ import annotations

from copy import deepcopy
import math
from typing import Any, Mapping


ANNUALIZATION_FIELDS = (
    "discount_rate",
    "storage_life_years",
    "transformer_measure_life_years",
    "storage_fixed_om_fraction_per_year",
    "transformer_fixed_om_fraction_per_year",
)


class V32AnnualizationError(ValueError):
    """年化参数不在 frozen contract 登记范围内。"""


def _annualization(contract: Mapping[str, Any]) -> Mapping[str, Any]:
    try:
        annual = contract["costs"]["annualization"]
    except (KeyError, TypeError) as exc:
        raise V32AnnualizationError("contract annualization section is missing") from exc
    if not isinstance(annual, Mapping):
        raise V32AnnualizationError("contract annualization section must be a mapping")
    return annual


def _numeric(value: Any, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise V32AnnualizationError(f"{field} must be numeric") from exc
    if not math.isfinite(result):
        raise V32AnnualizationError(f"{field} must be finite")
    return result


def _normalise(field: str, value: Any) -> float | int:
    number = _numeric(value, field)
    if field.endswith("life_years"):
        if not number.is_integer() or number <= 0:
            raise V32AnnualizationError(f"{field} must be a positive integer")
        return int(number)
    if number < 0:
        raise V32AnnualizationError(f"{field} must be nonnegative")
    return number


def _allowed_values(annual: Mapping[str, Any], field: str) -> list[float | int]:
    sensitivity = annual.get("sensitivity")
    if not isinstance(sensitivity, Mapping) or field not in sensitivity:
        raise V32AnnualizationError(f"annualization sensitivity range missing {field}")
    values = [_normalise(field, value) for value in sensitivity[field]]
    if not values:
        raise V32AnnualizationError(f"annualization sensitivity range is empty for {field}")
    return values


def validate_annualization_overrides(
    contract: Mapping[str, Any],
    overrides: Mapping[str, Any],
) -> dict[str, float | int]:
    """校验并标准化部分年化覆盖值；未覆盖字段不被补写。"""
    if not isinstance(overrides, Mapping):
        raise V32AnnualizationError("annualization overrides must be a mapping")
    unknown = sorted(set(overrides) - set(ANNUALIZATION_FIELDS))
    if unknown:
        raise V32AnnualizationError(f"unknown annualization override fields: {unknown}")
    annual = _annualization(contract)
    result: dict[str, float | int] = {}
    for field, value in overrides.items():
        normalised = _normalise(field, value)
        allowed = _allowed_values(annual, field)
        if not any(math.isclose(float(normalised), float(item), rel_tol=0, abs_tol=1e-12) for item in allowed):
            raise V32AnnualizationError(
                f"{field}={normalised} is outside the frozen contract sensitivity range {allowed}"
            )
        result[field] = normalised
    return result


def apply_annualization_overrides(
    contract: Mapping[str, Any],
    overrides: Mapping[str, Any],
) -> dict[str, Any]:
    """返回带年化覆盖值的独立契约副本。"""
    validated = validate_annualization_overrides(contract, overrides)
    result = deepcopy(dict(contract))
    result.setdefault("costs", {}).setdefault("annualization", {}).update(validated)
    return result


def _base_values(contract: Mapping[str, Any]) -> dict[str, float | int]:
    annual = _annualization(contract)
    return {
        field: _normalise(field, annual[field])
        for field in ANNUALIZATION_FIELDS
    }


def _edge(contract: Mapping[str, Any], field: str, side: str) -> float | int:
    values = _allowed_values(_annualization(contract), field)
    return min(values) if side == "low" else max(values)


def build_annualization_scenarios(
    contract: Mapping[str, Any],
) -> dict[str, dict[str, float | int]]:
    """构造 A-J 定向场景，每个场景均为可重构的完整年化参数集合。"""
    base = _base_values(contract)

    def with_changes(**changes: float | int) -> dict[str, float | int]:
        values = {**base, **changes}
        return validate_annualization_overrides(contract, values)

    scenarios = {
        "discount_rate_low": with_changes(
            discount_rate=_edge(contract, "discount_rate", "low")
        ),
        "discount_rate_high": with_changes(
            discount_rate=_edge(contract, "discount_rate", "high")
        ),
        "storage_life_short": with_changes(
            storage_life_years=_edge(contract, "storage_life_years", "low")
        ),
        "storage_life_long": with_changes(
            storage_life_years=_edge(contract, "storage_life_years", "high")
        ),
        "transformer_life_short": with_changes(
            transformer_measure_life_years=_edge(
                contract, "transformer_measure_life_years", "low"
            )
        ),
        "transformer_life_long": with_changes(
            transformer_measure_life_years=_edge(
                contract, "transformer_measure_life_years", "high"
            )
        ),
        "storage_high_om_transformer_low_om": with_changes(
            storage_fixed_om_fraction_per_year=_edge(
                contract, "storage_fixed_om_fraction_per_year", "high"
            ),
            transformer_fixed_om_fraction_per_year=_edge(
                contract, "transformer_fixed_om_fraction_per_year", "low"
            ),
        ),
        "storage_low_om_transformer_high_om": with_changes(
            storage_fixed_om_fraction_per_year=_edge(
                contract, "storage_fixed_om_fraction_per_year", "low"
            ),
            transformer_fixed_om_fraction_per_year=_edge(
                contract, "transformer_fixed_om_fraction_per_year", "high"
            ),
        ),
        "annualization_storage_unfavorable": with_changes(
            discount_rate=_edge(contract, "discount_rate", "high"),
            storage_life_years=_edge(contract, "storage_life_years", "low"),
            storage_fixed_om_fraction_per_year=_edge(
                contract, "storage_fixed_om_fraction_per_year", "high"
            ),
        ),
        "annualization_storage_favorable": with_changes(
            discount_rate=_edge(contract, "discount_rate", "low"),
            storage_life_years=_edge(contract, "storage_life_years", "high"),
            storage_fixed_om_fraction_per_year=_edge(
                contract, "storage_fixed_om_fraction_per_year", "low"
            ),
        ),
    }
    return scenarios
