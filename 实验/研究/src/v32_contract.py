"""解析 v3.2 契约及其唯一的实际资产共同基线口径。"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


class V32ContractError(ValueError):
    pass


_OVERLAY_CONTRACT_KEYS = {
    "version",
    "status",
    "frozen_at",
    "change_note",
    "overlay_role",
    "base_contract_version_required",
}

_FRONTIER_FIELDS = [
    "rcap",
    "region_id",
    "cumulative_in_service_eac_wanyuan",
    "physical_clr_2025",
    "storage_modules",
    "capacity_action_delta_mva",
    "feasible",
]


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in overlay.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _validate_version_marker_overlay(
    base: dict[str, Any], overlay: dict[str, Any]
) -> None:
    """阻止 overlay 重复或静默改写 frozen v3.2 业务语义。"""
    unexpected_sections = sorted(set(overlay) - {"contract"})
    if unexpected_sections:
        raise V32ContractError(
            "v3.2 overlay semantic drift: only contract version metadata is allowed; "
            f"found {unexpected_sections}"
        )
    metadata = overlay.get("contract")
    if not isinstance(metadata, dict):
        raise V32ContractError("v3.2 overlay contract metadata is required")
    unexpected_keys = sorted(set(metadata) - _OVERLAY_CONTRACT_KEYS)
    if unexpected_keys:
        raise V32ContractError(
            "v3.2 overlay semantic drift: unexpected contract metadata "
            f"{unexpected_keys}"
        )
    if metadata.get("overlay_role") != "version_marker_only":
        raise V32ContractError("v3.2 overlay must be version_marker_only")
    required = metadata.get("base_contract_version_required")
    base_version = base.get("contract", {}).get("version")
    if required != base_version:
        raise V32ContractError(
            "v3.2 overlay base version requirement does not match canonical contract"
        )
    for key in ("version", "status", "frozen_at", "change_note"):
        if key in metadata and metadata[key] != base.get("contract", {}).get(key):
            raise V32ContractError(
                f"v3.2 overlay semantic drift: contract.{key} differs from canonical base"
            )


def load_v32_contract(
    root: Path,
    *,
    base_filename: str = "model_contract.yaml",
    overlay_filename: str = "model_contract_v3_2_overlay.yaml",
) -> dict[str, Any]:
    root = Path(root)
    base_path = root / base_filename
    overlay_path = root / overlay_filename
    if not base_path.is_file() or not overlay_path.is_file():
        raise V32ContractError("base contract and v3.2 overlay are both required")
    base = yaml.safe_load(base_path.read_text(encoding="utf-8"))
    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    if not isinstance(base, dict) or not isinstance(overlay, dict):
        raise V32ContractError("contracts must decode to mappings")
    _validate_version_marker_overlay(base, overlay)
    resolved = _deep_merge(base, overlay)
    if resolved.get("contract", {}).get("version") != "3.2.0":
        raise V32ContractError("resolved contract must be v3.2.0")

    baseline = resolved.get("planning_baseline", {})
    if baseline.get("formula") != "S0 = actual_2021_installed_capacity":
        raise V32ContractError("v3.2 primary baseline must be the actual 2021 asset state")
    if baseline.get("future_decision_year_information_allowed") is not False:
        raise V32ContractError("future decision-year information leakage is forbidden")
    if baseline.get("legacy_capacity_excess_treatment") != (
        "grandfather_existing_capacity_without_forced_retirement"
    ):
        raise V32ContractError("legacy capacity grandfathering is not frozen")
    if baseline.get("retirement_to_meet_rcap_forbidden") is not True:
        raise V32ContractError("forced retirement for Rcap compliance must be forbidden")
    if baseline.get("rigid_incremental_capacity_rule") != (
        "DeltaS_y <= max(Rcap * P_plus_y - S_2021, 0)"
    ):
        raise V32ContractError("grandfathered incremental Rcap rule is not frozen")

    optimization = resolved.get("optimization", {})
    if optimization.get("direct_policy_cost_comparison_allowed") is not True:
        raise V32ContractError("same-actual-baseline policy cost comparison must be enabled")
    if optimization.get("retirement_candidates_in_primary_policy_model") is not False:
        raise V32ContractError("retirement candidates are forbidden in the primary policy model")

    fields = resolved.get("elasticity_sweep", {}).get("output", {}).get("fields")
    if fields != _FRONTIER_FIELDS:
        raise V32ContractError("canonical v3.2 frontier output schema is not frozen")

    timeseries = resolved.get("data", {}).get("timeseries", {})
    if timeseries.get("current_status") != (
        "approved_for_2025_qx00005_110kv_operating_scope"
    ):
        raise V32ContractError("scoped formal time-series approval status is not frozen")
    if timeseries.get("formal_hourly_use_allowed") is not True:
        raise V32ContractError("formal hourly evidence gate must be open for its scoped use")
    if timeseries.get("grade_a_ready") is not True:
        raise V32ContractError("scoped QX-00005 110 kV grade-A gate is not ready")
    if timeseries.get("formal_scope_approved_transformers") != 40:
        raise V32ContractError("formal QX-00005 operating scope must contain 40 transformers")
    if timeseries.get("context_only_35kv_formal_hourly_use_allowed") is not False:
        raise V32ContractError("35 kV context-only columns cannot become formal hourly evidence")

    benchmark = resolved.get("standardized_policy_benchmark", {})
    if benchmark.get("formula") != "S_norm_0 = 2.0 * P_plus_2021":
        raise V32ContractError("standardized 2.0 baseline benchmark must remain explicit")
    if benchmark.get("role") != "secondary_sensitivity_only_not_primary_client_policy_model":
        raise V32ContractError("standardized baseline must remain secondary sensitivity only")
    return resolved


def write_resolved_v32_contract(root: Path, output_path: Path) -> Path:
    resolved = load_v32_contract(root)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(
            resolved,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        ),
        encoding="utf-8",
    )
    return output_path
