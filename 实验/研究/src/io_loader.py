"""数据层读取 + schema 校验 → ScenarioData。

只读 data/<track>/*.csv 与 params.yaml,不做任何计算(计算归 clr/links_sigma 等)。
synthetic/raw 双轨同构,track 参数切换目录,列名/校验规则不变。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from src.net_model import Station, TiePair, Transformer, Zone


class SchemaError(ValueError):
    """数据文件不满足接口约定(列缺失/引用不闭合/行数不符)。"""


def adapt_real_2025(
    source_root: Path,
    output_root: Path,
    contract_path: Path,
) -> dict:
    """参数化执行 2025 真实数据适配，并返回确定性运行清单。"""
    from src.real_data_adapter import adapt_real_2025 as _adapt_real_2025

    return _adapt_real_2025(
        source_root=Path(source_root),
        output_root=Path(output_root),
        contract_path=Path(contract_path),
    )


def adapt_real_2021_2025(
    source_root: Path,
    output_root: Path,
    contract_path: Path,
    candidate_map_path: Path | None = None,
) -> dict:
    """生成 v3 2021—2025 标准化数据、年度资产白名单和跨年时序产物。"""
    from src.real_data_v3 import adapt_real_2021_2025 as _adapt_real_2021_2025

    return _adapt_real_2021_2025(
        source_root=Path(source_root),
        output_root=Path(output_root),
        contract_path=Path(contract_path),
        candidate_map_path=Path(candidate_map_path) if candidate_map_path is not None else None,
    )


def approve_real_timeseries_mapping(
    processed_root: Path,
    approval_path: Path,
    output_path: Path | None = None,
) -> dict:
    """读取项目负责人审批文件并校验候选哈希。"""
    from src.annual_asset_scope import approve_real_timeseries_mapping as _approve

    return _approve(
        processed_root=Path(processed_root),
        approval_path=Path(approval_path),
        output_path=Path(output_path) if output_path is not None else None,
    )


def review_real_timeseries_mapping(
    source_root: Path,
    candidate_map_path: Path,
    processed_root: Path,
    contract_path: Path,
) -> dict:
    """交叉验证 58 列候选映射并输出审批门禁与逐点质量结果。"""
    from src.timeseries_mapping import review_real_timeseries_mapping as _review

    return _review(
        source_root=Path(source_root),
        candidate_map_path=Path(candidate_map_path),
        processed_root=Path(processed_root),
        contract_path=Path(contract_path),
    )


def build_real_baseline(
    processed_root: Path,
    output_dir: Path,
    contract_path: Path,
) -> dict:
    """按冻结口径生成 2025 真实数据现状基线与反向承载力诊断。"""
    from src.real_metrics import build_real_baseline as _build_real_baseline

    return _build_real_baseline(
        processed_root=Path(processed_root),
        output_dir=Path(output_dir),
        contract_path=Path(contract_path),
    )


def build_empirical_duration_scenarios(
    processed_root: Path,
    output_dir: Path,
    contract_path: Path,
) -> dict:
    """从 QX-00005 条件映射样本构造非概率经验时长情景。"""
    from src.empirical_scenarios import build_empirical_duration_scenarios as _build

    return _build(
        processed_root=Path(processed_root),
        output_dir=Path(output_dir),
        contract_path=Path(contract_path),
    )


def build_real_matrices(
    processed_root: Path,
    run_dir: Path,
    contract_path: Path,
) -> dict:
    """生成八县区 110 kV 正式矩阵、35 kV 辅助矩阵及跨层映射清单。"""
    from src.real_matrices import build_real_matrices as _build

    return _build(
        processed_root=Path(processed_root),
        run_dir=Path(run_dir),
        contract_path=Path(contract_path),
    )


def run_real_capacity_network_screen(
    processed_root: Path,
    run_dir: Path,
    contract_path: Path,
) -> dict:
    """执行仅供内部使用的 110 kV 容量网络故障压力筛查。"""
    from src.real_network_check import run_real_capacity_network_screen as _run

    return _run(
        processed_root=Path(processed_root),
        run_dir=Path(run_dir),
        contract_path=Path(contract_path),
    )


# 各 CSV 必备列(据 README/PLAN-M1 §Task2 接口 + Task1 交付列名)
_STATIONS_COLS = ["station_id", "name", "county", "zone_id", "voltage_kv", "area_type"]
_TRANSFORMERS_COLS = ["station_id", "unit_id", "capacity_mva", "operation_mode"]
_TIES_COLS = [
    "tie_id", "station_a", "station_b", "n_channels", "conductor_type",
    "ampacity_mw", "sigma_load", "sigma_pv", "switch_mode", "sensitive",
]
_PV_REGISTRY_COLS = ["pv_id", "station_id", "feeder", "capacity_mw", "cod_year"]
_LOAD_CURVE_COLS = ["timestamp", "p_net_mw"]

_EXPECTED_HOURS = 8760


@dataclass
class ScenarioData:
    """Task 2 对外唯一接口:后续所有计算/优化模块只认这些字段。"""

    zones: dict[str, Zone]
    stations: dict[str, Station]
    ties: list[TiePair]
    pnet: pd.DataFrame       # index=DatetimeIndex(8760), columns=station_id(字典序)
    pv_capacity: pd.Series   # index=station_id → 装机 MW(pv_registry 聚合)
    params: dict


def load_params(root: Path) -> dict:
    """读取 params.yaml(全局参数,禁止硬编码复刻)。"""
    path = Path(root) / "params.yaml"
    if not path.exists():
        raise SchemaError(f"params.yaml: file not found at {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _read_csv_checked(path: Path, required_cols: list[str]) -> pd.DataFrame:
    """读 CSV 并校验必备列齐全,否则抛 SchemaError(含文件名+缺失列名)。"""
    if not path.exists():
        raise SchemaError(f"{path.name}: file not found at {path}")
    df = pd.read_csv(path)
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise SchemaError(f"{path.name}: missing columns {missing}")
    return df


def _check_refs(values: pd.Series, valid_ids: set[str], src_file: str, col: str) -> None:
    """校验外键引用闭合(如 station_id),否则抛 SchemaError(含文件名+列名)。"""
    bad = sorted(set(values.astype(str)) - valid_ids)
    if bad:
        raise SchemaError(f"{src_file}: column '{col}' has unknown references {bad}")


def _build_zones(stations: dict[str, Station]) -> dict[str, Zone]:
    zones: dict[str, Zone] = {}
    for st in stations.values():
        zone = zones.get(st.zone_id)
        if zone is None:
            zone = Zone(zone_id=st.zone_id, county=st.county, area_type=st.area_type, stations=[])
            zones[st.zone_id] = zone
        zone.stations.append(st)
    return zones


def _load_pnet(data_dir: Path, station_ids: list[str]) -> pd.DataFrame:
    """按 station_id 字典序拼接 load_curves/*.csv → DataFrame(index=DatetimeIndex)。"""
    series_map: dict[str, pd.Series] = {}
    index_ref = None
    for sid in sorted(station_ids):
        path = data_dir / "load_curves" / f"{sid}.csv"
        df = _read_csv_checked(path, _LOAD_CURVE_COLS)
        if len(df) != _EXPECTED_HOURS:
            raise SchemaError(
                f"load_curves/{sid}.csv: expected {_EXPECTED_HOURS} rows, got {len(df)}"
            )
        ts = pd.to_datetime(df["timestamp"])
        if index_ref is None:
            index_ref = ts
        elif not ts.equals(index_ref):
            raise SchemaError(
                f"load_curves/{sid}.csv: column 'timestamp' does not align with other stations"
            )
        series_map[sid] = pd.Series(df["p_net_mw"].to_numpy(), index=ts, name=sid)
    pnet = pd.DataFrame(series_map)
    pnet = pnet[sorted(pnet.columns)]
    pnet.index.name = "timestamp"
    if len(pnet) != _EXPECTED_HOURS:
        raise SchemaError(f"load_curves: assembled pnet has {len(pnet)} rows, expected {_EXPECTED_HOURS}")
    return pnet


def load_scenario(root: Path, track: str = "synthetic") -> ScenarioData:
    """读取 data/<track>/ 全部 CSV + params.yaml,组装并校验 ScenarioData。"""
    root = Path(root)
    data_dir = root / "data" / track
    params = load_params(root)

    stations_df = _read_csv_checked(data_dir / "stations.csv", _STATIONS_COLS)
    valid_station_ids = set(stations_df["station_id"].astype(str))

    transformers_df = _read_csv_checked(data_dir / "transformers.csv", _TRANSFORMERS_COLS)
    _check_refs(transformers_df["station_id"], valid_station_ids, "transformers.csv", "station_id")

    ties_df = _read_csv_checked(data_dir / "ties.csv", _TIES_COLS)
    _check_refs(ties_df["station_a"], valid_station_ids, "ties.csv", "station_a")
    _check_refs(ties_df["station_b"], valid_station_ids, "ties.csv", "station_b")

    pv_df = _read_csv_checked(data_dir / "pv_registry.csv", _PV_REGISTRY_COLS)
    _check_refs(pv_df["station_id"], valid_station_ids, "pv_registry.csv", "station_id")

    # 主变分组挂载(unit_id 按字符串排序,保证同站内顺序确定)
    transformers_by_station: dict[str, list[Transformer]] = {sid: [] for sid in valid_station_ids}
    for row in transformers_df.itertuples(index=False):
        transformers_by_station[str(row.station_id)].append(
            Transformer(
                station_id=str(row.station_id),
                unit_id=str(row.unit_id),
                capacity_mva=float(row.capacity_mva),
                operation_mode=str(row.operation_mode),
            )
        )
    for sid, units in transformers_by_station.items():
        units.sort(key=lambda t: t.unit_id)

    stations: dict[str, Station] = {}
    for row in stations_df.itertuples(index=False):
        sid = str(row.station_id)
        stations[sid] = Station(
            station_id=sid,
            county=str(row.county),
            zone_id=str(row.zone_id),
            area_type=str(row.area_type),
            transformers=transformers_by_station.get(sid, []),
        )

    zones = _build_zones(stations)

    ties: list[TiePair] = [
        TiePair(
            tie_id=str(row.tie_id),
            station_a=str(row.station_a),
            station_b=str(row.station_b),
            n_channels=int(row.n_channels),
            conductor_type=str(row.conductor_type),
            ampacity_mw=float(row.ampacity_mw),
            sigma_load=float(row.sigma_load),
            sigma_pv=float(row.sigma_pv),
            switch_mode=str(row.switch_mode),
            sensitive=bool(row.sensitive),
        )
        for row in ties_df.itertuples(index=False)
    ]

    pv_capacity = pv_df.groupby("station_id")["capacity_mw"].sum()
    pv_capacity = pv_capacity.reindex(sorted(valid_station_ids)).fillna(0.0)
    pv_capacity.index.name = "station_id"

    pnet = _load_pnet(data_dir, list(valid_station_ids))
    if pnet.shape[1] != len(valid_station_ids):
        raise SchemaError(
            f"load_curves: expected {len(valid_station_ids)} station files, got {pnet.shape[1]}"
        )

    return ScenarioData(
        zones=zones,
        stations=stations,
        ties=ties,
        pnet=pnet,
        pv_capacity=pv_capacity,
        params=params,
    )
