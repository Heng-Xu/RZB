"""基于 QX-00005 条件映射样本的日内经验持续时间情景。

这些曲线只迁移日内形状，不是实测同步县域曲线，也不具有概率含义。
目标站的静态正/反向峰值逐项保持；官方县域正向峰值只作为正式 CLR
锚点单列，禁止与站级经验曲线求和混用。
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


SCENARIO_BUILDER_VERSION = "1.0.0"
SCENARIO_NAMES = ("empirical_short", "empirical_central", "empirical_long")
MATCHED_SAMPLE_LIMIT = 60
LINEAGE_FIELDS = (
    "source_ref",
    "source_version",
    "transformation",
    "scenario_id",
    "quality_flag",
    "source_sha256",
)


class EmpiricalScenarioError(ValueError):
    """经验情景输入、映射或守恒关系不满足。"""


@dataclass(frozen=True)
class ShapeSample:
    voltage_kv: int
    station_id: str
    day_of_year: int
    normalized: np.ndarray
    equivalent_reverse_duration_hours: float
    reverse_hours: int
    pv_capacity_ratio: float
    reverse_forward_ratio: float
    transformer_scale_mva: float

    @property
    def sample_id(self) -> str:
        return f"QX-00005|{self.voltage_kv}|{self.station_id}|D{self.day_of_year:03d}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _combined_hash(paths: list[Path]) -> str:
    values = {path.name: _sha256(path) for path in sorted(paths, key=lambda p: p.name)}
    return hashlib.sha256(
        json.dumps(values, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _require(processed_root: Path, filename: str, columns: set[str]) -> pd.DataFrame:
    path = processed_root / filename
    if not path.is_file():
        raise EmpiricalScenarioError(f"required input missing: {path}")
    frame = pd.read_csv(path)
    missing = columns - set(frame.columns)
    if missing:
        raise EmpiricalScenarioError(f"{filename}: missing columns {sorted(missing)}")
    return frame


def _station_features(
    master: pd.DataFrame,
    pv: pd.DataFrame,
) -> pd.DataFrame:
    capacity = (
        master.groupby(["region_id", "voltage_kv", "station_id"], as_index=False)
        .agg(
            capacity_mva=("capacity_mva", "sum"),
            transformer_scale_mva=("capacity_mva", "mean"),
        )
    )
    pv_sum = (
        pv.groupby(["region_id", "voltage_kv", "station_id"], as_index=False)["pv_online_mw"]
        .sum()
    )
    result = capacity.merge(
        pv_sum, on=["region_id", "voltage_kv", "station_id"], how="left", validate="1:1"
    )
    result["pv_online_mw"] = result["pv_online_mw"].fillna(0.0)
    result["pv_capacity_ratio"] = result["pv_online_mw"] / result["capacity_mva"]
    return result


def _source_samples(
    hourly: pd.DataFrame,
    features: pd.DataFrame,
) -> dict[int, list[ShapeSample]]:
    status = hourly["mapping_approval_status"].astype(str).str.lower()
    usable = hourly[status.isin({"conditional", "approved"}) & hourly["net_load_mw"].notna()].copy()
    if usable.empty:
        raise EmpiricalScenarioError("no approved or conditional QX-00005 hourly shapes are available")
    usable["timestamp"] = pd.to_datetime(usable["timestamp"])
    usable["date"] = usable["timestamp"].dt.date
    station_hourly = (
        usable.groupby(["voltage_kv", "station_id", "timestamp", "date"], as_index=False)[
            "net_load_mw"
        ]
        .sum()
        .sort_values(["voltage_kv", "station_id", "timestamp"], kind="stable")
    )
    feature_lookup = features[
        features["region_id"].eq("QX-00005")
    ].set_index(["voltage_kv", "station_id"])
    samples: dict[int, list[ShapeSample]] = {35: [], 110: []}
    for (voltage, station_id, date), group in station_hourly.groupby(
        ["voltage_kv", "station_id", "date"], sort=True
    ):
        if len(group) != 24 or group["timestamp"].dt.hour.nunique() != 24:
            continue
        values = group.sort_values("timestamp")["net_load_mw"].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            continue
        forward = max(float(values.max()), 0.0)
        reverse = max(float(-values.min()), 0.0)
        if forward <= 0 or reverse <= 0:
            continue
        normalized = np.where(values >= 0, values / forward, values / reverse)
        feature = feature_lookup.loc[(int(voltage), str(station_id))]
        if isinstance(feature, pd.DataFrame):
            raise EmpiricalScenarioError(f"duplicate source station feature: {voltage}|{station_id}")
        sample = ShapeSample(
            voltage_kv=int(voltage),
            station_id=str(station_id),
            day_of_year=int(pd.Timestamp(date).dayofyear),
            normalized=normalized,
            equivalent_reverse_duration_hours=float((-np.minimum(normalized, 0.0)).sum()),
            reverse_hours=int((normalized < 0).sum()),
            pv_capacity_ratio=float(feature["pv_capacity_ratio"]),
            reverse_forward_ratio=reverse / forward,
            transformer_scale_mva=float(feature["transformer_scale_mva"]),
        )
        samples[int(voltage)].append(sample)
    for voltage, pool in samples.items():
        if len(pool) < 3:
            raise EmpiricalScenarioError(f"{voltage} kV has fewer than three usable source days")
    return samples


def _feature_distance(
    sample: ShapeSample,
    target_pv_ratio: float,
    target_reverse_forward_ratio: float,
    target_transformer_scale_mva: float,
) -> float:
    def log_distance(left: float, right: float) -> float:
        return abs(float(np.log1p(max(left, 0.0))) - float(np.log1p(max(right, 0.0))))

    return (
        2.0 * log_distance(sample.pv_capacity_ratio, target_pv_ratio)
        + 2.0 * log_distance(sample.reverse_forward_ratio, target_reverse_forward_ratio)
        + log_distance(sample.transformer_scale_mva, target_transformer_scale_mva)
    )


def _select_samples(
    pool: list[ShapeSample],
    target_pv_ratio: float,
    target_reverse_forward_ratio: float,
    target_transformer_scale_mva: float,
) -> tuple[dict[str, ShapeSample], int, dict[str, float]]:
    scored = sorted(
        (
            (
                _feature_distance(
                    sample,
                    target_pv_ratio,
                    target_reverse_forward_ratio,
                    target_transformer_scale_mva,
                ),
                sample.sample_id,
                sample,
            )
            for sample in pool
        ),
        key=lambda item: (item[0], item[1]),
    )[:MATCHED_SAMPLE_LIMIT]
    ranked = sorted(
        scored,
        key=lambda item: (item[2].equivalent_reverse_duration_hours, item[1]),
    )
    positions = (0, (len(ranked) - 1) // 2, len(ranked) - 1)
    selected: dict[str, ShapeSample] = {}
    distances: dict[str, float] = {}
    for name, position in zip(SCENARIO_NAMES, positions, strict=True):
        distance, _sample_id, sample = ranked[position]
        selected[name] = sample
        distances[name] = float(distance)
    return selected, len(ranked), distances


def _build_outputs(
    static: pd.DataFrame,
    features: pd.DataFrame,
    reference: pd.DataFrame,
    pools: dict[int, list[ShapeSample]],
    source_version: str,
    source_hash: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    keys = ["region_id", "voltage_kv", "station_id"]
    feature_lookup = features.set_index(keys)
    anchor_lookup = reference.set_index(["region_id", "voltage_kv"])[
        "positive_peak_anchor_mw"
    ]
    profile_rows: list[dict[str, Any]] = []
    index_rows: list[dict[str, Any]] = []
    issue_rows: list[dict[str, Any]] = []
    lineage = {
        "source_ref": "transformer_hourly_2025.csv.gz+station_static_load.csv+station_pv_snapshot.csv+county_clr_reference.csv",
        "source_version": source_version,
        "transformation": "match same-voltage QX-00005 station-day shapes and piecewise-scale to exact target static positive/reverse peaks",
        "scenario_id": "real_2025_empirical_duration",
        "quality_flag": "conditional_mapping_for_empirical_shape_only_not_measured_target_timeseries",
        "source_sha256": source_hash,
    }
    for row in static.sort_values(keys, kind="stable").itertuples(index=False):
        key = (str(row.region_id), int(row.voltage_kv), str(row.station_id))
        if pd.isna(row.annual_max_net_load_mw) or pd.isna(row.annual_min_net_load_mw):
            issue_rows.append(
                {
                    "region_id": key[0],
                    "voltage_kv": key[1],
                    "station_id": key[2],
                    "issue": "missing_static_extrema_no_empirical_scenario",
                    **lineage,
                }
            )
            continue
        if key not in feature_lookup.index:
            issue_rows.append(
                {
                    "region_id": key[0],
                    "voltage_kv": key[1],
                    "station_id": key[2],
                    "issue": "missing_equipment_feature_no_empirical_scenario",
                    **lineage,
                }
            )
            continue
        feature = feature_lookup.loc[key]
        if isinstance(feature, pd.DataFrame):
            raise EmpiricalScenarioError(f"duplicate target station feature: {key}")
        target_forward = max(float(row.annual_max_net_load_mw), 0.0)
        target_reverse = max(-float(row.annual_min_net_load_mw), 0.0)
        target_ratio = target_reverse / target_forward if target_forward > 0 else target_reverse
        selected, sample_count, distances = _select_samples(
            pools[key[1]],
            float(feature["pv_capacity_ratio"]),
            target_ratio,
            float(feature["transformer_scale_mva"]),
        )
        anchor = float(anchor_lookup.loc[(key[0], key[1])])
        for scenario_name in SCENARIO_NAMES:
            sample = selected[scenario_name]
            scaled = np.where(
                sample.normalized >= 0,
                sample.normalized * target_forward,
                sample.normalized * target_reverse,
            )
            if not np.isclose(max(float(scaled.max()), 0.0), target_forward):
                raise EmpiricalScenarioError(f"positive peak not preserved for {key}|{scenario_name}")
            if not np.isclose(max(float(-scaled.min()), 0.0), target_reverse):
                raise EmpiricalScenarioError(f"reverse peak not preserved for {key}|{scenario_name}")
            index_rows.append(
                {
                    "region_id": key[0],
                    "voltage_kv": key[1],
                    "station_id": key[2],
                    "duration_scenario": scenario_name,
                    "target_forward_peak_mw": target_forward,
                    "target_reverse_peak_mw": target_reverse,
                    "county_positive_peak_anchor_mw": anchor,
                    "county_anchor_role": "formal_positive_peak_anchor_kept_separate_from_station_scenario_sum",
                    "reference_region_id": "QX-00005",
                    "reference_voltage_kv": sample.voltage_kv,
                    "reference_station_id": sample.station_id,
                    "reference_sample_id": sample.sample_id,
                    "reference_day_of_year": sample.day_of_year,
                    "matched_sample_count": sample_count,
                    "feature_distance": distances[scenario_name],
                    "reverse_hours": sample.reverse_hours,
                    "equivalent_reverse_duration_hours": sample.equivalent_reverse_duration_hours,
                    "shape_evidence_status": "conditional_mapping_for_empirical_shape_only",
                    "evidence_grade": "C" if key[0] == "QX-00005" or key[1] == 35 else "B",
                    **lineage,
                }
            )
            for hour, value in enumerate(scaled):
                profile_rows.append(
                    {
                        "region_id": key[0],
                        "voltage_kv": key[1],
                        "station_id": key[2],
                        "duration_scenario": scenario_name,
                        "hour": hour,
                        "net_load_mw": float(value),
                        "reference_sample_id": sample.sample_id,
                        **lineage,
                    }
                )
    if not issue_rows:
        issue_rows.append(
            {
                "region_id": "QX-ALL",
                "voltage_kv": 0,
                "station_id": "BDZ-NONE",
                "issue": "no_missing_target_station_extrema",
                **lineage,
            }
        )
    return pd.DataFrame(index_rows), pd.DataFrame(profile_rows), pd.DataFrame(issue_rows)


def _write_csv(path: Path, frame: pd.DataFrame, sort_by: list[str], compressed: bool = False) -> None:
    missing = set(LINEAGE_FIELDS) - set(frame.columns)
    if missing:
        raise EmpiricalScenarioError(f"{path.name}: missing lineage fields {sorted(missing)}")
    ordered = frame.sort_values(sort_by, kind="stable").reset_index(drop=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    compression: Any = {"method": "gzip", "mtime": 0} if compressed else None
    ordered.to_csv(
        path,
        index=False,
        lineterminator="\n",
        float_format="%.10g",
        compression=compression,
    )


def build_empirical_duration_scenarios(
    processed_root: Path,
    output_dir: Path,
    contract_path: Path,
) -> dict[str, Any]:
    """构造三类非概率日内经验时长情景并记录匹配证据。"""
    processed_root = Path(processed_root).resolve()
    output_dir = Path(output_dir).resolve()
    contract_path = Path(contract_path).resolve()
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    names = tuple(contract["time_model"]["other_regions"]["scenarios"])
    if names != SCENARIO_NAMES:
        raise EmpiricalScenarioError(f"unexpected scenario labels: {names}")
    if contract["time_model"]["other_regions"]["p50_p90_labels_allowed"]:
        raise EmpiricalScenarioError("probabilistic P50/P90 labels must remain disabled")

    paths = [
        processed_root / "transformer_hourly_2025.csv.gz",
        processed_root / "transformer_master.csv",
        processed_root / "station_static_load.csv",
        processed_root / "station_pv_snapshot.csv",
        processed_root / "county_clr_reference.csv",
    ]
    hourly = _require(
        processed_root,
        "transformer_hourly_2025.csv.gz",
        {"timestamp", "voltage_kv", "station_id", "net_load_mw", "mapping_approval_status"},
    )
    master = _require(
        processed_root,
        "transformer_master.csv",
        {"region_id", "voltage_kv", "station_id", "capacity_mva"},
    )
    static = _require(
        processed_root,
        "station_static_load.csv",
        {"region_id", "voltage_kv", "station_id", "annual_max_net_load_mw", "annual_min_net_load_mw"},
    )
    pv = _require(
        processed_root,
        "station_pv_snapshot.csv",
        {"region_id", "voltage_kv", "station_id", "pv_online_mw"},
    )
    reference = _require(
        processed_root,
        "county_clr_reference.csv",
        {"region_id", "voltage_kv", "positive_peak_anchor_mw"},
    )
    features = _station_features(master, pv)
    pools = _source_samples(hourly, features)
    source_hash = _combined_hash(paths)
    source_versions = sorted(set(hourly["source_version"].dropna().astype(str)))
    source_version = "+".join(source_versions)
    index, profiles, issues = _build_outputs(
        static, features, reference, pools, source_version, source_hash
    )
    if index.empty or profiles.empty:
        raise EmpiricalScenarioError("no empirical scenarios were generated")
    counts = index.groupby(["region_id", "voltage_kv", "station_id"]).size()
    if not counts.eq(3).all():
        raise EmpiricalScenarioError("every valid target station must have exactly three scenarios")

    output_dir.mkdir(parents=True, exist_ok=True)
    frames = {
        "empirical_scenario_index.csv": (
            index,
            ["region_id", "voltage_kv", "station_id", "duration_scenario"],
            False,
        ),
        "empirical_station_scenarios.csv.gz": (
            profiles,
            ["region_id", "voltage_kv", "station_id", "duration_scenario", "hour"],
            True,
        ),
        "empirical_scenario_issues.csv": (
            issues,
            ["region_id", "voltage_kv", "station_id"],
            False,
        ),
    }
    for filename, (frame, keys, compressed) in frames.items():
        _write_csv(output_dir / filename, frame, keys, compressed)
    fingerprint_payload = {
        "builder_version": SCENARIO_BUILDER_VERSION,
        "contract_sha256": _sha256(contract_path),
        "input_hash": source_hash,
        "sample_limit": MATCHED_SAMPLE_LIMIT,
    }
    fingerprint = hashlib.sha256(
        json.dumps(fingerprint_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    manifest: dict[str, Any] = {
        "scenario_builder_version": SCENARIO_BUILDER_VERSION,
        "scenario_fingerprint": fingerprint,
        "contract_sha256": _sha256(contract_path),
        "input_fingerprint": source_hash,
        "scenario_labels": list(SCENARIO_NAMES),
        "probabilistic_interpretation_allowed": False,
        "source_sample_counts": {str(key): len(value) for key, value in pools.items()},
        "target_station_count": int(counts.size),
        "output_files": {
            filename: {"sha256": _sha256(output_dir / filename), "rows": int(len(frame))}
            for filename, (frame, _keys, _compressed) in sorted(frames.items())
        },
    }
    (output_dir / "empirical_duration_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
