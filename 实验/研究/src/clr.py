"""正式正向容载比与反向诊断指标。

正式 CLR 始终使用干预前正向同步峰值；反向峰值只作独立诊断。
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.io_loader import ScenarioData


@dataclass
class CLRResult:
    """单分区双向容载比结果。"""

    p_fwd: float   # P⁺ = max(pnet, 0) 的最大值(正向/受电峰)
    p_rev: float   # P⁻ = max(-pnet, 0) 的最大值(反向/送出峰)
    r: float       # 正式 CLR = ΣS / 干预前 P⁺
    r_fwd: float   # 正式正向 CLR 的兼容列
    binding: str   # 仅表示诊断峰值方向，不改变正式分母


def compute_zone_clr(
    pnet_zone: pd.Series,
    cap_mva: float,
    positive_peak_base: float | None = None,
) -> CLRResult:
    """计算正式正向 CLR，并单列当前序列的正/反向峰值。

    ``positive_peak_base`` 用于 C0/A/B 共用干预前分母；省略时取当前序列
    的正向同步峰值。储能或其他措施后的序列只影响诊断峰值，不影响该分母。
    """
    p_fwd = max(float(pnet_zone.max()), 0.0)
    p_rev = max(float(-pnet_zone.min()), 0.0)
    binding = "reverse" if p_rev > p_fwd else "forward"
    denom = p_fwd if positive_peak_base is None else float(positive_peak_base)
    if denom < 0:
        raise ValueError("positive_peak_base must be nonnegative")
    r = cap_mva / denom if denom > 0 else float("inf")
    r_fwd = r
    return CLRResult(p_fwd=p_fwd, p_rev=p_rev, r=r, r_fwd=r_fwd, binding=binding)


def compute_all(data: ScenarioData) -> pd.DataFrame:
    """对 ScenarioData 中全部分区批量计算双向容载比。

    分区净负荷时序 = data.pnet[该区 station 列].sum(axis=1) 后再取峰
    (逐时刻先加总,同时率在聚合顺序中内生;不得用各站峰值直接相加)。
    """
    rows: dict[str, dict[str, object]] = {}
    for zone_id in sorted(data.zones):
        zone = data.zones[zone_id]
        station_ids = [st.station_id for st in zone.stations]
        pnet_zone = data.pnet[station_ids].sum(axis=1)
        cap_mva = sum(st.cap_mva for st in zone.stations)
        result = compute_zone_clr(pnet_zone, cap_mva)
        rows[zone_id] = {
            "county": zone.county,
            "area_type": zone.area_type,
            "cap_mva": cap_mva,
            "p_fwd": result.p_fwd,
            "p_rev": result.p_rev,
            "r": result.r,
            "r_fwd": result.r_fwd,
            "binding": result.binding,
        }
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index.name = "zone_id"
    return df
