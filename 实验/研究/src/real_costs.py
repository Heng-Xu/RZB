"""真实扩容候选与储能模块的 CAPEX/EAC 成本库。"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


COST_LIBRARY_VERSION = "3.0.0"
V3_COST_SCENARIO_ID = "real_2021_2025_cost_library"
LINEAGE_FIELDS = (
    "source_ref",
    "source_version",
    "transformation",
    "scenario_id",
    "quality_flag",
    "source_sha256",
)


class RealCostError(ValueError):
    """成本输入、候选或参数不满足冻结合同。"""


class V3CostError(RealCostError):
    """v3 离散成本或储能物理校验不满足。"""


def validate_integer_storage_schedule(
    actual_net_load_mw: Any,
    charge_mw: Any,
    discharge_mw: Any,
    soc_mwh: Any,
    storage_modules: int,
    contract: dict[str, Any],
    *,
    tolerance: float = 1e-8,
) -> dict[str, Any]:
    """验证整数柜储能的功率、SOC、逐日循环和本地功率方向。"""
    if isinstance(storage_modules, bool) or not isinstance(storage_modules, int) or storage_modules < 0:
        raise V3CostError("storage_modules must be a nonnegative integer")
    actual = np.asarray(list(actual_net_load_mw), dtype=float)
    charge = np.asarray(list(charge_mw), dtype=float)
    discharge = np.asarray(list(discharge_mw), dtype=float)
    soc = np.asarray(list(soc_mwh), dtype=float)
    if actual.ndim != 1 or len(actual) == 0 or len(actual) % 24 != 0:
        raise V3CostError("storage schedule must contain one or more complete 24-hour days")
    if not (len(charge) == len(discharge) == len(soc) == len(actual)):
        raise V3CostError("storage schedule arrays must have equal length")
    if not all(np.isfinite(values).all() for values in (actual, charge, discharge, soc)):
        raise V3CostError("storage schedule contains non-finite values")
    if (charge < -tolerance).any() or (discharge < -tolerance).any():
        raise V3CostError("storage charge and discharge must be nonnegative")
    if ((charge > tolerance) & (discharge > tolerance)).any():
        raise V3CostError("simultaneous charge and discharge are not allowed")
    if (charge - np.maximum(-actual, 0.0) > tolerance).any():
        raise V3CostError("storage charge would cross zero")
    if (discharge - np.maximum(actual, 0.0) > tolerance).any():
        raise V3CostError("storage discharge would cause export")
    module = contract["storage"]["module"]
    efficiency = contract["storage"]["efficiency"]
    soc_cfg = contract["storage"]["soc"]
    power_limit = float(storage_modules) * float(module["power_mw"])
    energy_limit = float(storage_modules) * float(module["energy_mwh"])
    if (charge > power_limit + tolerance).any() or (discharge > power_limit + tolerance).any():
        raise V3CostError("storage schedule exceeds integer cabinet power")
    soc_min = float(soc_cfg["min_fraction"]) * energy_limit
    soc_max = float(soc_cfg["max_fraction"]) * energy_limit
    if (soc < soc_min - tolerance).any() or (soc > soc_max + tolerance).any():
        raise V3CostError("storage SOC is outside configured bounds")
    eta_charge = float(efficiency["charge"])
    eta_discharge = float(efficiency["discharge"])
    residuals: list[float] = []
    for start in range(0, len(actual), 24):
        end = start + 24
        previous = float(soc[end - 1])
        for index in range(start, end):
            expected = previous + eta_charge * charge[index] - discharge[index] / eta_discharge
            residuals.append(float(soc[index] - expected))
            previous = float(soc[index])
    max_residual = max(abs(value) for value in residuals)
    if max_residual > tolerance:
        raise V3CostError("daily SOC recursion or cyclic condition is violated")
    net_after = actual + charge - discharge
    return {
        "feasible": True,
        "storage_modules": storage_modules,
        "net_after_mw": net_after,
        "daily_soc_residual_mwh": max_residual,
        "soc_min_mwh": soc_min,
        "soc_max_mwh": soc_max,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def capital_recovery_factor(discount_rate: float, life_years: int) -> float:
    """计算资本回收系数 CRF。"""
    rate = float(discount_rate)
    years = int(life_years)
    if years <= 0 or years != life_years:
        raise ValueError("life_years must be a positive integer")
    if rate < 0:
        raise ValueError("discount_rate must be nonnegative")
    if rate == 0:
        return 1.0 / years
    factor = (1.0 + rate) ** years
    return rate * factor / (factor - 1.0)


def annualized_eac_wanyuan(
    capex_wanyuan: float,
    discount_rate: float,
    life_years: int,
    fixed_om_fraction_per_year: float,
) -> float:
    """把一次性投资折算为含固定运维的等效年成本。"""
    capex = float(capex_wanyuan)
    om = float(fixed_om_fraction_per_year)
    if capex < 0 or om < 0:
        raise ValueError("capex and fixed O&M fraction must be nonnegative")
    return capex * (capital_recovery_factor(discount_rate, life_years) + om)


def storage_capex_wanyuan(storage_modules: int, contract: dict[str, Any]) -> float:
    """按 10 柜整块加余数块计算储能投资，禁止直接线性外推。"""
    if isinstance(storage_modules, bool) or not isinstance(storage_modules, int):
        raise ValueError("storage_modules must be an integer")
    if storage_modules < 0:
        raise ValueError("storage_modules must be nonnegative")
    if storage_modules == 0:
        return 0.0
    config = contract["costs"]["storage_capex"]
    block_size = int(config["block_size_modules"])
    block_cost = float(config["block_cost_wanyuan"])
    full_blocks, remainder = divmod(storage_modules, block_size)
    remainder_cost = 0.0
    if remainder:
        # 合同已冻结为 1 至 10 柜的截距+斜率公式。
        remainder_cost = 6.8382 + 20.3618 * remainder
    return full_blocks * block_cost + remainder_cost


def _coefficient_range(annual: dict[str, Any], asset: str) -> tuple[float, float, float]:
    if asset == "storage":
        life_key = "storage_life_years"
        om_key = "storage_fixed_om_fraction_per_year"
    elif asset == "transformer":
        life_key = "transformer_measure_life_years"
        om_key = "transformer_fixed_om_fraction_per_year"
    else:
        raise ValueError(f"unknown asset annualization class: {asset}")
    base = capital_recovery_factor(annual["discount_rate"], annual[life_key]) + float(
        annual[om_key]
    )
    sensitivity = annual["sensitivity"]
    coefficients = [
        capital_recovery_factor(rate, life) + float(om)
        for rate in sensitivity["discount_rate"]
        for life in sensitivity[life_key]
        for om in sensitivity[om_key]
    ]
    return min(coefficients), base, max(coefficients)


def _cost_or_nan(value: Any) -> float:
    result = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return float(result) if pd.notna(result) else float("nan")


def _expansion_library(
    candidates: pd.DataFrame,
    contract: dict[str, Any],
) -> pd.DataFrame:
    required = {
        "candidate_id",
        "candidate_type",
        "old_capacity_mva",
        "new_capacity_mva",
        "delta_capacity_mva",
        "capex_low_wanyuan",
        "capex_high_wanyuan",
        "capex_center_wanyuan",
        "source_row",
        *LINEAGE_FIELDS,
    }
    missing = required - set(candidates.columns)
    if missing:
        raise RealCostError(f"expansion_candidates.csv missing {sorted(missing)}")
    if candidates["candidate_id"].duplicated().any():
        raise RealCostError("candidate_id must be unique")
    if (candidates["source_row"] <= 0).any():
        raise RealCostError("every expansion candidate must retain a positive source_row")
    allowed_types = {
        "new_third_transformer",
        "replacement_or_uprating",
        "new_station",
        "line_or_bay_project",
    }
    unknown_types = set(candidates["candidate_type"].dropna().astype(str)) - allowed_types
    if unknown_types:
        raise RealCostError(f"unsupported continuous or unapproved candidate types: {sorted(unknown_types)}")
    numeric = candidates[["old_capacity_mva", "new_capacity_mva", "delta_capacity_mva"]].apply(
        pd.to_numeric, errors="coerce"
    )
    if numeric.isna().any().any() or (numeric < 0).any().any():
        raise RealCostError("candidate capacities must be finite and nonnegative")

    result = candidates.copy()
    replacement = result["candidate_type"].eq("replacement_or_uprating")
    expected_delta = result["new_capacity_mva"] - result["old_capacity_mva"]
    if not result.loc[replacement, "delta_capacity_mva"].equals(expected_delta.loc[replacement]):
        differences = (
            result.loc[replacement, "delta_capacity_mva"] - expected_delta.loc[replacement]
        ).abs()
        if (differences > 1e-9).any():
            raise RealCostError("replacement/uprating candidates must use net capacity increase")

    annual = contract["costs"]["annualization"]
    low_coef, base_coef, high_coef = _coefficient_range(annual, "transformer")
    lows = result["capex_low_wanyuan"].map(_cost_or_nan)
    highs = result["capex_high_wanyuan"].map(_cost_or_nan)
    centers = result["capex_center_wanyuan"].map(_cost_or_nan)
    result["eac_low_wanyuan_per_year"] = lows * low_coef
    result["eac_center_wanyuan_per_year"] = centers * base_coef
    result["eac_high_wanyuan_per_year"] = highs * high_coef
    result["annualization_class"] = "transformer_measure"
    result["discount_rate_base"] = float(annual["discount_rate"])
    result["life_years_base"] = int(annual["transformer_measure_life_years"])
    result["fixed_om_fraction_base"] = float(
        annual["transformer_fixed_om_fraction_per_year"]
    )
    result["cost_status"] = "cost_range_available"
    result.loc[lows.isna() | highs.isna(), "cost_status"] = "cost_gap_not_optimizable"
    result.loc[centers.notna(), "cost_status"] = "cost_center_and_range_available"
    result["transformation"] = (
        result["transformation"].astype(str)
        + "; annualize source-backed range with explicit contract assumptions"
    )
    result["scenario_id"] = V3_COST_SCENARIO_ID
    result["quality_flag"] = result["quality_flag"].astype(str) + ";" + result["cost_status"]
    return result


def _storage_boundaries(
    contract: dict[str, Any],
    contract_hash: str,
    policy_hash: str,
) -> pd.DataFrame:
    storage = contract["storage"]["module"]
    capex = contract["costs"]["storage_capex"]
    annual = contract["costs"]["annualization"]
    low_coef, base_coef, high_coef = _coefficient_range(annual, "storage")
    price_low, price_high = [float(value) for value in capex["sensitivity_yuan_per_wh"]]
    energy_wh = float(storage["energy_mwh"]) * 1_000_000.0
    rows: list[dict[str, Any]] = []
    for modules in (0, 1, 10, 11, 20):
        base_capex = storage_capex_wanyuan(modules, contract)
        low_capex = modules * energy_wh * price_low / 10000.0
        high_capex = modules * energy_wh * price_high / 10000.0
        if modules == 0:
            low_capex = high_capex = 0.0
        rows.append(
            {
                "region_id": "QX-ALL",
                "storage_modules": modules,
                "storage_power_mw": modules * float(storage["power_mw"]),
                "storage_energy_mwh": modules * float(storage["energy_mwh"]),
                "capex_low_wanyuan": low_capex,
                "capex_base_wanyuan": base_capex,
                "capex_high_wanyuan": high_capex,
                "eac_low_wanyuan_per_year": low_capex * low_coef,
                "eac_base_wanyuan_per_year": base_capex * base_coef,
                "eac_high_wanyuan_per_year": high_capex * high_coef,
                "source_ref": "model_contract.yaml+参考政策/储能成本依据/来源与适用说明.md",
                "source_version": f"model_contract_{contract['contract']['version']}",
                "transformation": "apply 10-module block CAPEX rule; sensitivity uses source yuan/Wh bounds",
                "scenario_id": V3_COST_SCENARIO_ID,
                "quality_flag": "policy_anchor_with_model_annualization_assumptions",
                "source_sha256": hashlib.sha256(
                    f"{contract_hash}:{policy_hash}".encode("utf-8")
                ).hexdigest(),
            }
        )
    return pd.DataFrame(rows)


def _assumptions(contract: dict[str, Any], contract_hash: str) -> pd.DataFrame:
    annual = contract["costs"]["annualization"]
    rows: list[dict[str, Any]] = []
    for parameter in (
        "discount_rate",
        "storage_life_years",
        "transformer_measure_life_years",
        "storage_fixed_om_fraction_per_year",
        "transformer_fixed_om_fraction_per_year",
    ):
        rows.append(
            {
                "assumption_id": f"COST-{parameter}",
                "parameter": parameter,
                "base_value": annual[parameter],
                "sensitivity_values": json.dumps(
                    annual["sensitivity"][parameter], ensure_ascii=False
                ),
                "evidence_type": annual["evidence_type"],
                "source_ref": "model_contract.yaml",
                "source_version": f"model_contract_{contract['contract']['version']}",
                "transformation": "copy frozen base and sensitivity values without reinterpretation",
                "scenario_id": V3_COST_SCENARIO_ID,
                "quality_flag": "explicit_model_assumption",
                "source_sha256": contract_hash,
            }
        )
    return pd.DataFrame(rows)


def _write(path: Path, frame: pd.DataFrame, sort_by: list[str]) -> None:
    missing = set(LINEAGE_FIELDS) - set(frame.columns)
    if missing:
        raise RealCostError(f"{path.name}: missing lineage fields {sorted(missing)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.sort_values(sort_by, kind="stable").reset_index(drop=True).to_csv(
        path, index=False, lineterminator="\n", float_format="%.10g"
    )


def build_real_cost_library(
    processed_root: Path,
    output_dir: Path,
    contract_path: Path,
) -> dict[str, Any]:
    """生成真实离散候选和储能模块的可追溯成本库。"""
    processed_root = Path(processed_root).resolve()
    output_dir = Path(output_dir).resolve()
    contract_path = Path(contract_path).resolve()
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if contract["contract"]["version"] != "3.1.0":
        raise RealCostError("v3 cost library requires model contract 3.1.0")
    if contract["costs"]["expansion_capex"]["generic_800_wanyuan_per_50mva_allowed"]:
        raise RealCostError("generic 800-wanyuan expansion placeholder must be disabled")
    candidate_path = processed_root / "expansion_candidates.csv"
    candidates = pd.read_csv(candidate_path)
    contract_hash = _sha256(contract_path)
    source_note = (contract_path.parent / contract["costs"]["storage_capex"]["source_note"]).resolve()
    if not source_note.is_file():
        raise RealCostError(f"storage cost source note missing: {source_note}")
    policy_hash = _sha256(source_note)

    expansion = _expansion_library(candidates, contract)
    storage = _storage_boundaries(contract, contract_hash, policy_hash)
    assumptions = _assumptions(contract, contract_hash)
    frames = {
        "expansion_cost_library.csv": (expansion, ["region_id", "station_id", "candidate_id"]),
        "storage_module_cost_boundaries.csv": (storage, ["storage_modules"]),
        "cost_assumptions.csv": (assumptions, ["assumption_id"]),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, (frame, keys) in frames.items():
        _write(output_dir / filename, frame, keys)
    manifest: dict[str, Any] = {
        "dataset_id": "real_2021_2025",
        "cost_library_version": COST_LIBRARY_VERSION,
        "contract_version": contract["contract"]["version"],
        "price_year": int(contract["costs"]["price_year"]),
        "formal_paths": [
            "PATH_OPT_CLR_UNBOUNDED",
            "PATH_OPT_CLR_LE_2",
        ],
        "contract_sha256": contract_hash,
        "storage_policy_note_sha256": policy_hash,
        "candidate_input_sha256": _sha256(candidate_path),
        "model_assumption_gate": "explicit",
        "output_files": {
            filename: {"sha256": _sha256(output_dir / filename), "rows": int(len(frame))}
            for filename, (frame, _keys) in sorted(frames.items())
        },
    }
    (output_dir / "cost_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
