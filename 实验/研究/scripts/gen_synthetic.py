#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合成示例县数据生成器(M1 Task 1)。

产出:
  data/synthetic/stations.csv
  data/synthetic/transformers.csv
  data/synthetic/ties.csv
  data/synthetic/pv_registry.csv
  data/synthetic/load_curves/S01.csv ... S12.csv
  data/synthetic/pv_profiles/shape_xuzhou.csv
  data/synthetic/_manifest.json

这些 CSV 的列名是收资数据接口定版(M2 真实数据落 data/raw/ 时沿用同列名)。
全部随机性来自 numpy.random.default_rng(seed),seed 从 params.yaml 的
synthetic.seed 读取,不在代码里另写死。

TMY 解析说明(重要,读代码前先看):
  ../有EA/datasets/pv_profiles/xuzhou_tmy.csv 实际内容是 PVGIS 2005-2020
  共16年逐时数据(列 time,P,G_i,T2m,WS10m),并非单一"典型年"文件;
  G_i(平面辐照)列全空,故取 P(PV 出力,单位 W)列。
  为避免用多年平均把真实天气波动"抹平"(该数据集的用途之一就是制造
  反送场景,需要保留真实的晴/阴天差异),这里只取其中一个非闰年
  (2005,8760 行,行数与目标一致)做归一化,不做跨年平均。
  时间戳原始为 UTC;徐州地处中国,本地时区 CST=UTC+8,若不做时区平移,
  光伏出力峰值会被错误地贴到本地凌晨 3~4 点的索引位置,与负荷曲线的
  午间谷值对不上,下游"午间反送"场景将失真。因此对 8760 点序列做
  np.roll(shift=8) 完成 UTC->CST 的整点近似平移(跨年边界自然环绕,
  12-31 深夜的值绕到 01-01 凌晨,气候学上无害)。
  解析全程带断言(行数==8760、归一化后最大值==1.0、凌晨深夜时段==0);
  任一断言失败即判定解析失败,程序在打印 "BLOCKED:" 前缀信息后 raise,
  不会退化为正弦波替身。

调参记录(分区反向卡边验收,任务:合成数据需能演示"高PV分区反向峰超正向峰
→β约束逼出扩容→容载比弹过2.0"的机制):
  原参数下乡镇站(rural) pv_ratio 统一 uniform(0.9,1.3),站级 min 可到 -39MW,
  但分区聚合(同分区多站逐时相加后取峰,非站峰值直接相加)后 P⁻/P⁺ 最高仅
  0.68,且无一站 P⁻>0.8×站容量,机制无法触发。现改为按分区分档:
    Z2(新沂乡镇B)、Z5(邳州乡镇E) pv_ratio: uniform(0.9,1.3) → uniform(1.9,2.6)
      (推高至> 2 倍峰荷装机,制造分区级反向卡边 P⁻>P⁺ 且站级 P⁻>0.8×容量)
    Z3(新沂乡镇C) pv_ratio: uniform(0.9,1.3) → uniform(1.0,1.3)
      (保留中等 PV 渗透率,作梯度对照组,验证机制随渗透率单调)
  仅动 pv_ratio 抽样区间(按 zone_id 分支),未改 schema/站数/分区结构/seed
  机制;城区(urban)站 pv_ratio 区间不变,全年仍应正向卡边。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import numpy as np
import pandas as pd
import yaml

ROOT = pathlib.Path(__file__).parents[1]          # 研究/
OUT = ROOT / "data" / "synthetic"
TMY_PATH = ROOT / ".." / "有EA" / "datasets" / "pv_profiles" / "xuzhou_tmy.csv"
PARAMS_PATH = ROOT / "params.yaml"

TIMELINE_START = pd.Timestamp("2025-01-01 00:00:00")   # 基准年占位,tz-naive
N_HOURS = 8760

# ---------------------------------------------------------------------------
# 分区/站点静态拓扑(裁决口径,详见 task-1-brief.md 补充裁决)
# ---------------------------------------------------------------------------
ZONES = [
    # zone_id, county, area_type, zone_name(中文,用于 name 列),  station ids
    ("Z1", "XY", "urban", "新沂城区A", ["S01", "S02", "S03"]),
    ("Z2", "XY", "rural", "新沂乡镇B", ["S04", "S05", "S06"]),
    ("Z3", "XY", "rural", "新沂乡镇C", ["S07", "S08"]),
    ("Z4", "PZ", "urban", "邳州城区D", ["S09", "S10"]),
    ("Z5", "PZ", "rural", "邳州乡镇E", ["S11", "S12"]),
]
PARALLEL_STATIONS = {"S05", "S11"}   # 3x50MVA 并列,其余 2x50MVA 分列
VOLTAGE_KV = 110

STATION_ZONE = {sid: z for z, *_r, sids in ZONES for sid in sids}
STATION_COUNTY = {sid: c for z, c, *_r, sids in ZONES for sid in sids}
STATION_AREA = {sid: a for z, c, a, _n, sids in ZONES for sid in sids}
STATION_ZONE_NAME = {sid: n for z, c, a, n, sids in ZONES for sid in sids}
ALL_STATIONS = [sid for *_r, sids in ZONES for sid in sids]

MONTH_SEASON_FACTOR = {   # 夏冬双季调制:冬夏偏高,春秋偏低
    1: 1.08, 2: 1.05, 3: 0.95, 4: 0.90, 5: 0.92, 6: 1.00,
    7: 1.10, 8: 1.12, 9: 1.00, 10: 0.90, 11: 0.92, 12: 1.05,
}
WEEKEND_FACTOR = 0.85      # 周末衰减


def load_params() -> dict:
    with open(PARAMS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def sha256_of(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Step A: PV 归一化形状 (shape_xuzhou.csv)
# ---------------------------------------------------------------------------
def build_pv_shape() -> pd.DataFrame:
    if not TMY_PATH.exists():
        print(f"BLOCKED: TMY 文件不存在: {TMY_PATH}")
        raise FileNotFoundError(str(TMY_PATH))

    raw = pd.read_csv(TMY_PATH)
    print(f"[gen_synthetic] TMY 列名: {list(raw.columns)}")
    try:
        assert "time" in raw.columns, "缺少 time 列"
        assert "P" in raw.columns, "缺少 P(出力)列"

        # G_i(平面辐照)常见但本文件全空,记录供人工核查,不作为解析依据
        gi_nonnull = int(raw["G_i"].notna().sum()) if "G_i" in raw.columns else 0
        print(f"[gen_synthetic] G_i 非空行数: {gi_nonnull}(0 表示该列不可用,退回用 P 列)")

        ts = pd.to_datetime(raw["time"], format="%Y%m%d:%H%M")
        raw = raw.assign(_ts=ts, _year=ts.dt.year)

        # 只取一个非闰年整年(2005),避免多年平均抹平真实晴/阴天波动
        year0 = 2005
        one_year = raw[raw["_year"] == year0].sort_values("_ts")
        assert len(one_year) == N_HOURS, (
            f"年份 {year0} 行数={len(one_year)},应为 {N_HOURS}(可能含闰日或缺测)"
        )

        p = one_year["P"].to_numpy(dtype=float)
        assert np.isfinite(p).all(), "P 列含非数值/缺测"
        assert p.max() > 0, "P 列全零,无法归一化"

        # UTC -> CST(+8h)整点近似平移,使光伏峰值落在本地午间附近,
        # 与负荷曲线的午间低谷场景对齐(跨年边界环绕,气候学上无害)
        p_shifted = np.roll(p, 8)

        p_norm = p_shifted / p_shifted.max()

        assert len(p_norm) == N_HOURS
        assert np.isclose(p_norm.max(), 1.0), f"归一化最大值={p_norm.max()},应为 1.0"
        # 深夜(本地 00:00-03:00,对应平移后序列前 3 个整点)应为 0,
        # 窗口取窄一点以避开曙暮光时段的非零值(见生成器顶部说明)
        deep_night = p_norm[0:3]
        assert np.all(deep_night == 0.0), f"深夜时段非零: {deep_night}"
        assert p_norm.min() == 0.0, "全年应存在真实的 0 出力(夜间)时段"
    except AssertionError as e:
        print(f"BLOCKED: TMY 解析断言失败: {e}")
        raise

    timestamps = pd.date_range(TIMELINE_START, periods=N_HOURS, freq="h")
    return pd.DataFrame({"timestamp": timestamps, "p_norm": p_norm})


# ---------------------------------------------------------------------------
# Step B: 负荷形状(双峰工作日 + 夏冬双季调制 + 周末衰减)
# ---------------------------------------------------------------------------
def _daily_shape() -> np.ndarray:
    """0~23 时的基础形状(未归一化),双峰:早峰 10-11h,晚峰 19-21h。
    夜间/午间设有较高的地板值,避免低 PV 占比的城区站在午间也被拉出负值。
    """
    hours = np.arange(24)
    floor = 0.48
    morning = 0.42 * np.exp(-0.5 * ((hours - 10.5) / 1.6) ** 2)
    evening = 0.50 * np.exp(-0.5 * ((hours - 20.0) / 1.8) ** 2)
    night_dip = 0.18 * np.exp(-0.5 * ((hours - 3.0) / 2.2) ** 2)
    shape = floor + morning + evening - night_dip
    return np.clip(shape, 0.15, None)


def build_load_shape_series() -> np.ndarray:
    """返回长度 8760 的负荷归一化系数序列(峰值≈1.0),对齐 2025-01-01 起时间轴。"""
    timestamps = pd.date_range(TIMELINE_START, periods=N_HOURS, freq="h")
    daily = _daily_shape()
    vals = np.empty(N_HOURS, dtype=float)
    for i, ts in enumerate(timestamps):
        base = daily[ts.hour]
        season = MONTH_SEASON_FACTOR[ts.month]
        weekend = WEEKEND_FACTOR if ts.dayofweek >= 5 else 1.0
        vals[i] = base * season * weekend
    vals = vals / vals.max()   # 归一化,使全年峰值系数恰为 1.0
    return vals


# ---------------------------------------------------------------------------
# 主生成流程
# ---------------------------------------------------------------------------
def main() -> None:
    params = load_params()
    seed = params["synthetic"]["seed"]
    rng = np.random.default_rng(seed)

    (OUT / "load_curves").mkdir(parents=True, exist_ok=True)
    (OUT / "pv_profiles").mkdir(parents=True, exist_ok=True)

    # ---- pv_profiles/shape_xuzhou.csv ----
    pv_shape_df = build_pv_shape()
    pv_shape_path = OUT / "pv_profiles" / "shape_xuzhou.csv"
    pv_shape_df.to_csv(pv_shape_path, index=False)
    p_norm = pv_shape_df["p_norm"].to_numpy()

    load_shape = build_load_shape_series()

    # ---- stations.csv ----
    station_rows = []
    for zone_id, county, area_type, zone_name, sids in ZONES:
        for idx, sid in enumerate(sids, start=1):
            station_rows.append({
                "station_id": sid,
                "name": f"{zone_name}-{sid}",
                "county": county,
                "zone_id": zone_id,
                "voltage_kv": VOLTAGE_KV,
                "area_type": area_type,
            })
    stations_df = pd.DataFrame(station_rows).sort_values("station_id").reset_index(drop=True)
    stations_df.to_csv(OUT / "stations.csv", index=False)

    # ---- 峰荷 + PV 装机(每站一次 rng 抽样,load_curves 与 pv_registry 共用同一批数值) ----
    # 第二轮调参(跨任务修复:基线超线与抬峰,见文件头"调参记录"第2条)。
    # 逐站给定 (peak_lo, peak_hi, pvf_lo, pvf_hi);抽样次数/顺序不变(每站先 peak
    # 后 pv_factor,共 2 次 rng.uniform)→ 下游 ties.csv 与逐时噪声的随机流位置不变,
    # 城区各站(含 S01)与 Z3 各站区间保持不变 → test_loader 的 S01 装机基准值不动。
    STATION_TUNE = {
        # Z2(新沂乡镇B):PV 集中在 S04 制造站级反向超标(P->0.8x100=80MW)逼扩容;
        #   S05/S06 低 PV,使分区聚合 P- 落入 [~180, 200) 窗口 → 基线 R<=1.95 且
        #   方案B 扩容后 R=(350+50)/P- 弹过 2.0。
        "S04": (55.0, 62.0, 2.2, 2.5),
        "S05": (32.0, 45.0, 1.25, 1.55),
        "S06": (50.0, 60.0, 1.55, 1.80),
        # Z5(邳州乡镇E):抬高负荷幅值、下调 PV,使正向峰主导 → 基线 R 从 2.10 降至
        #   <=1.95(消除"容量富余逼抬峰"根因),且无站级反向超标。
        #   负荷集中在 3x50 的 S11(N-1 裕度 130MW,不触发扩容);S12(2x50,N-1
        #   裕度仅 65MW)负荷压到 <65MW,避免其正向 N-1 过载逼扩容——否则小峰值
        #   Z5 被迫扩容后 cap↑ 会让方案A 为守 R<=2.0 而抬正向峰(抬峰复发)。
        "S11": (85.0, 95.0, 1.0, 1.2),
        "S12": (50.0, 60.0, 1.0, 1.3),
    }
    peak_mw = {}
    pv_capacity_mw = {}
    for sid in ALL_STATIONS:
        area = STATION_AREA[sid]
        if sid in STATION_TUNE:
            plo, phi, flo, fhi = STATION_TUNE[sid]
            peak = rng.uniform(plo, phi)
            pv_factor = rng.uniform(flo, fhi)
        elif area == "urban":
            peak = rng.uniform(60.0, 90.0)
            pv_factor = rng.uniform(0.2, 0.4)
        else:   # Z3(新沂乡镇C):乡镇中等渗透率对照组,区间不变
            peak = rng.uniform(30.0, 60.0)
            pv_factor = rng.uniform(1.0, 1.3)
        peak_mw[sid] = peak
        pv_capacity_mw[sid] = peak * pv_factor

    # ---- transformers.csv ----
    tx_rows = []
    for sid in ALL_STATIONS:
        if sid in PARALLEL_STATIONS:
            for unit in (1, 2, 3):
                tx_rows.append({"station_id": sid, "unit_id": unit,
                                 "capacity_mva": 50.0, "operation_mode": "parallel"})
        else:
            for unit in (1, 2):
                tx_rows.append({"station_id": sid, "unit_id": unit,
                                 "capacity_mva": 50.0, "operation_mode": "split"})
    tx_df = pd.DataFrame(tx_rows)
    tx_df.to_csv(OUT / "transformers.csv", index=False)

    # ---- pv_registry.csv(与 load_curves 共用同一 pv_capacity_mw) ----
    pv_rows = []
    for pid, sid in enumerate(ALL_STATIONS, start=1):
        pv_rows.append({
            "pv_id": f"PV{pid:02d}",
            "station_id": sid,
            "feeder": "F01",
            "capacity_mw": round(pv_capacity_mw[sid], 3),
            "cod_year": 2023,
        })
    pv_df = pd.DataFrame(pv_rows)
    pv_df.to_csv(OUT / "pv_registry.csv", index=False)

    # ---- ties.csv: 9 条(同分区5 + 跨分区3 + 另1条,含 >=1 forbidden、>=1 sensitive) ----
    zone_stations = {z: sids for z, *_r, sids in ZONES}
    same_zone_pairs = []
    for z, sids in zone_stations.items():
        for i in range(len(sids)):
            for j in range(i + 1, len(sids)):
                same_zone_pairs.append((sids[i], sids[j]))
    cross_zone_pairs = [
        ("S03", "S04"),   # Z1-Z2 (XY 内跨区)
        ("S06", "S07"),   # Z2-Z3 (XY 内跨区)
        ("S10", "S11"),   # Z4-Z5 (PZ 内跨区)
    ]
    idx_same = rng.choice(len(same_zone_pairs), size=5, replace=False)
    same_zone_selected = [same_zone_pairs[i] for i in idx_same]
    # 第9条(另1条):从未选中的同分区候选里再取1条
    remaining = [p for i, p in enumerate(same_zone_pairs) if i not in set(idx_same)]
    extra_pair = remaining[int(rng.integers(0, len(remaining)))]

    tie_pairs = same_zone_selected + cross_zone_pairs + [extra_pair]
    conductor_types = ["LGJ-240", "LGJ-185", "LGJ-150"]
    switch_modes = ["loop", "outage"]

    tie_rows = []
    for i, (a, b) in enumerate(tie_pairs, start=1):
        n_channels = int(rng.integers(1, 3))            # 1~2
        conductor_type = conductor_types[int(rng.integers(0, len(conductor_types)))]
        ampacity_mw = float(rng.uniform(8.0, 12.0))
        sigma_load = float(rng.uniform(0.10, 0.30))
        sigma_pv = float(rng.uniform(0.05, 0.25))
        switch_mode = switch_modes[int(rng.integers(0, len(switch_modes)))]
        sensitive = bool(rng.uniform() < 0.3)
        tie_rows.append({
            "tie_id": f"T{i:02d}",
            "station_a": a, "station_b": b,
            "n_channels": n_channels,
            "conductor_type": conductor_type,
            "ampacity_mw": round(ampacity_mw, 3),
            "sigma_load": round(sigma_load, 4),
            "sigma_pv": round(sigma_pv, 4),
            "switch_mode": switch_mode,
            "sensitive": sensitive,
        })
    # 强制:最后一条(第9条,extra_pair)= forbidden,测试筛除逻辑
    tie_rows[-1]["switch_mode"] = "forbidden"
    # 强制:至少一条 sensitive=True(若 rng 抽样未命中,人工在第1条补齐)
    if not any(r["sensitive"] for r in tie_rows):
        tie_rows[0]["sensitive"] = True
    ties_df = pd.DataFrame(tie_rows)
    ties_df.to_csv(OUT / "ties.csv", index=False)

    # ---- load_curves/<station_id>.csv ----
    timestamps = pd.date_range(TIMELINE_START, periods=N_HOURS, freq="h")
    curve_paths = []
    for sid in ALL_STATIONS:
        # 站间幅值差异已由 peak_mw 的 rng 抽样体现;再叠加小幅逐时噪声增加真实感
        noise = 1.0 + rng.normal(0.0, 0.015, size=N_HOURS)
        gross_load_mw = peak_mw[sid] * load_shape * noise
        p_net_mw = gross_load_mw - pv_capacity_mw[sid] * p_norm
        curve_df = pd.DataFrame({
            "timestamp": timestamps,
            "p_net_mw": np.round(p_net_mw, 4),
        })
        path = OUT / "load_curves" / f"{sid}.csv"
        curve_df.to_csv(path, index=False)
        curve_paths.append(path)

    # ---- _manifest.json ----
    produced_files = (
        [OUT / "stations.csv", OUT / "transformers.csv", OUT / "ties.csv",
         OUT / "pv_registry.csv", pv_shape_path] + curve_paths
    )
    manifest = {
        "generator": "scripts/gen_synthetic.py",
        "params_snapshot": {
            "seed": seed,
            "n_stations": len(ALL_STATIONS),
            "n_zones": len(ZONES),
            "counties": params["synthetic"]["counties"],
            "zone_map": {z: {"county": c, "area_type": a, "stations": sids}
                         for z, c, a, _n, sids in ZONES},
            "parallel_stations": sorted(PARALLEL_STATIONS),
            "tmy_source_year": 2005,
            "tmy_utc_to_cst_shift_hours": 8,
        },
        "files": {
            str(p.relative_to(OUT)): sha256_of(p) for p in produced_files
        },
    }
    with open(OUT / "_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"[gen_synthetic] 完成: {len(ALL_STATIONS)} 站, {len(ties_df)} 条联络线, "
          f"{len(produced_files)} 个产物文件 -> {OUT}")


if __name__ == "__main__":
    try:
        main()
    except AssertionError:
        sys.exit(1)
