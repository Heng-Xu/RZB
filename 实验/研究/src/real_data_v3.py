"""v3 真实数据阶段 1：静态标准化、跨年时序、年度资产和血缘清单。"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.annual_asset_scope import (
    ADAPTER_VERSION,
    DATASET_ID,
    HOURLY_FILE,
    LINEAGE_FIELDS,
    _annual_reference,
    _sha256,
    _write_frame,
    build_actual_asset_actions,
    build_annual_asset_whitelist,
    build_annual_reconciliation,
    build_cross_year_timeseries_artifacts,
)
from src.real_data_adapter import (
    SRC01_02,
    SRC03_04,
    SRC05,
    SRC08,
    SRC10,
    SRC14,
    SOURCE_VERSION,
    _asset_scope_summary,
    _base_quality_issues,
    _cost_cases,
    _equipment,
    _expansion_candidates,
    _network_lines,
    _pv_profile,
    _pv_snapshot,
    _source_registry,
    _station_tables,
    _transformer_tables,
)


class RealDataV3Error(ValueError):
    """v3 真实数据适配或质量门禁失败。"""


def _relabel_v3(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    if "scenario_id" in result.columns:
        result["scenario_id"] = DATASET_ID
    return result


def _write_manifest(output_root: Path, contract_path: Path, source_files: dict[str, dict[str, Any]]) -> dict[str, Any]:
    output_files = {
        path.name: {"sha256": _sha256(path), "bytes": path.stat().st_size}
        for path in sorted(output_root.iterdir(), key=lambda item: item.name)
        if path.is_file() and path.name != "manifest.json"
    }
    payload = {
        "adapter_version": ADAPTER_VERSION,
        "contract_sha256": _sha256(contract_path),
        "source_hashes": {name: value["sha256"] for name, value in sorted(source_files.items())},
    }
    fingerprint = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    manifest = {
        "dataset_id": DATASET_ID,
        "adapter_version": ADAPTER_VERSION,
        "contract_id": "xuzhou-clr-real-data-2021-2025",
        "contract_version": "3.1.0",
        "contract_sha256": _sha256(contract_path),
        "dataset_fingerprint": fingerprint,
        "source_root_name": "电网建模数据_Agent整合版_V1.2",
        "source_files": source_files,
        "output_files": output_files,
        "timeseries_gate": {
            "grade_a_ready": False,
            "formal_hourly_use_allowed": False,
            "annual_gate_rule": "annual_asset_whitelist",
            "approval_authority": "project_owner",
            "qx00005_2025_110kv_operating_transformers_required": 40,
            "year_end_only_excluded_from_2025_operating_gate": [
                "QX-00005|110|BDZ-00056|#1",
                "QX-00005|110|BDZ-00056|#2",
            ],
        },
        "quality_gate": {
            "qx00005_stations_110kv": 21,
            "qx00005_operating_2025_stations_110kv": 20,
            "qx00005_transformers_110kv": 42,
            "qx00005_operating_2025_transformers_110kv": 40,
            "qx00005_transformers_35kv_context": 16,
            "hourly_series_total": 58,
            "annual_reference_years": [2021, 2022, 2023, 2024, 2025],
            "known_2024_anomaly_count": 3,
        },
    }
    (output_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def adapt_real_2021_2025(
    source_root: Path,
    output_root: Path,
    contract_path: Path,
    candidate_map_path: Path | None = None,
) -> dict[str, Any]:
    """生成 v3 阶段 1 标准化数据、跨年映射、年度资产和实际行动台账。"""
    source_root = Path(source_root).resolve()
    output_root = Path(output_root).resolve()
    contract_path = Path(contract_path).resolve()
    if not source_root.is_dir():
        raise RealDataV3Error(f"source root not found: {source_root}")
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if contract["contract"]["version"] != "3.1.0":
        raise RealDataV3Error("v3 adapter requires model contract 3.1.0")
    regions = set(contract["scope"]["regions"])
    source_files = _source_registry(source_root)
    before_hashes = {name: item["sha256"] for name, item in source_files.items()}

    def source_hash(name: str) -> str:
        if name not in source_files:
            raise RealDataV3Error(f"required source missing: {name}")
        return str(source_files[name]["sha256"])

    equipment, raw_expansion = _equipment(source_root, regions, source_hash(SRC03_04))
    transformer_master, transformer_static, issues_a = _transformer_tables(
        source_root, regions, equipment, source_hash(SRC01_02)
    )
    station_master, station_static, issues_b = _station_tables(
        source_root, regions, transformer_master, source_hash(SRC01_02)
    )
    candidates = _expansion_candidates(raw_expansion, station_master)
    pv_snapshot = _pv_snapshot(source_root, regions, source_hash(SRC05))
    pv_profile = _pv_profile(source_root, source_hash(SRC14))
    network_lines = _network_lines(source_root, regions, source_hash(SRC03_04))
    # 保留 2025 参考表供现有指标层使用，另行生成五年年度锚点。
    from src.real_data_adapter import _county_reference

    county_reference = _county_reference(source_root, regions, source_hash(SRC08))
    cost_cases = _cost_cases(source_root, source_hash(SRC10))
    asset_scopes = _asset_scope_summary(station_master, county_reference, source_hash(SRC01_02))
    annual_reference = _annual_reference(source_root, regions, source_hash(SRC08))
    whitelist = build_annual_asset_whitelist(transformer_master, annual_reference, source_hash(SRC01_02))
    reconciliation = build_annual_reconciliation(whitelist, annual_reference, source_hash(SRC01_02))
    actual_actions = build_actual_asset_actions(reconciliation, transformer_master, source_hash(SRC01_02))

    frames = {
        "station_master.csv": (_relabel_v3(station_master), ["region_id", "voltage_kv", "asset_scope_id", "station_id"]),
        "transformer_master.csv": (_relabel_v3(transformer_master), ["region_id", "voltage_kv", "station_id", "unit_id"]),
        "expansion_candidates.csv": (_relabel_v3(candidates), ["region_id", "station_id", "candidate_id"]),
        "station_static_load.csv": (_relabel_v3(station_static), ["region_id", "voltage_kv", "station_id"]),
        "transformer_static_load.csv": (_relabel_v3(transformer_static), ["region_id", "voltage_kv", "station_id", "unit_id"]),
        "station_pv_snapshot.csv": (_relabel_v3(pv_snapshot), ["region_id", "voltage_kv", "station_id"]),
        "pv_profile_2025.csv": (_relabel_v3(pv_profile), ["hour_index"]),
        "network_lines_110kv.csv": (_relabel_v3(network_lines), ["region_id", "line_id"]),
        "county_clr_reference.csv": (_relabel_v3(county_reference), ["region_id", "voltage_kv"]),
        "cost_cases.csv": (_relabel_v3(cost_cases), ["voltage_kv", "cost_case_id"]),
        "asset_scope_summary.csv": (_relabel_v3(asset_scopes), ["region_id", "voltage_kv"]),
        "annual_reference.csv": (_relabel_v3(annual_reference), ["year", "region_id", "voltage_kv"]),
        "annual_asset_whitelist.csv": (_relabel_v3(whitelist), ["year", "region_id", "voltage_kv", "asset_scope_id", "transformer_uid"]),
        "annual_asset_reconciliation.csv": (_relabel_v3(reconciliation), ["year", "region_id", "voltage_kv"]),
        "actual_asset_actions_2021_2025.csv": (_relabel_v3(actual_actions), ["year", "region_id", "voltage_kv", "action_id"]),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    for filename, (frame, keys) in frames.items():
        _write_frame(output_root / filename, frame, keys)

    mapping_artifacts = build_cross_year_timeseries_artifacts(
        source_root,
        output_root,
        contract_path,
        candidate_map_path=candidate_map_path,
    )

    quality_frames = [
        pd.DataFrame(_base_quality_issues(source_hash(SRC01_02))),
        pd.DataFrame(issues_a),
        pd.DataFrame(issues_b),
        mapping_artifacts["quality_issues"],
    ]
    quality = pd.concat([_relabel_v3(frame) for frame in quality_frames if not frame.empty], ignore_index=True, sort=False)
    # 阶段 1 的质量账本必须明确 v3 跨年映射和审批主体。
    quality = pd.concat(
        [
            quality,
            pd.DataFrame(
                [
                    {
                        "issue_id": "DQ-V3-MAPPING-APPROVAL",
                        "severity": "blocking_for_grade_A",
                        "entity_id": "QX-00005",
                        "description": "cross-year mapping remains conditional/rejected until project_owner approval",
                        **{
                            **{
                                "source_ref": "SRC07+candidate_map",
                                "source_version": SOURCE_VERSION,
                                "transformation": "annual whitelist gate",
                                "scenario_id": DATASET_ID,
                                "quality_flag": "project_owner_approval_pending",
                                "source_sha256": source_hash(HOURLY_FILE),
                            }
                        },
                    }
                ]
            ),
        ],
        ignore_index=True,
        sort=False,
    )
    _write_frame(output_root / "data_quality_issues.csv", quality, ["issue_id"])

    after_hashes = {name: _sha256(source_root / name) for name in before_hashes}
    if after_hashes != before_hashes:
        raise RealDataV3Error("source package changed during v3 adaptation")
    manifest = _write_manifest(output_root, contract_path, source_files)
    manifest["timeseries_review"] = mapping_artifacts["result"]
    manifest["output_files"] = {
        path.name: {"sha256": _sha256(path), "bytes": path.stat().st_size}
        for path in sorted(output_root.iterdir(), key=lambda item: item.name)
        if path.is_file() and path.name != "manifest.json"
    }
    (output_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
