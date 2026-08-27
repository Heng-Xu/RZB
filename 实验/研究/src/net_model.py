"""对象层:变电站/主变/联络/分区数据模型。

只做纯数据结构 + 派生属性,不做 IO(IO 归 io_loader.py)。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Transformer:
    """主变压器(transformers.csv 一行)。"""

    station_id: str
    unit_id: str
    capacity_mva: float
    operation_mode: str  # "split" | "parallel"


@dataclass
class Station:
    """110kV 变电站(stations.csv 一行 + 挂载的主变列表)。"""

    station_id: str
    county: str
    zone_id: str
    area_type: str
    transformers: list[Transformer] = field(default_factory=list)

    @property
    def cap_mva(self) -> float:
        """站内主变容量之和(MVA)。"""
        return sum(t.capacity_mva for t in self.transformers)

    def beta_eff(self, beta_cfg: dict) -> float:
        """最大反向负载率折算系数。

        分列(split)/单台运行:beta_cfg['split_mode']
        并列(parallel):min(split_beta, (S_total-S_largest)/S_total)。
        N-1 比例已经包含最大单台退出后的折减，禁止再乘一次 split_beta。
        """
        modes = {t.operation_mode for t in self.transformers}
        if "parallel" in modes:
            if not self.transformers:
                raise ValueError(f"station {self.station_id}: no transformers to compute beta_eff")
            total = sum(t.capacity_mva for t in self.transformers)
            if total <= 0:
                raise ValueError(f"station {self.station_id}: nonpositive transformer capacity")
            largest = max(t.capacity_mva for t in self.transformers)
            return min(float(beta_cfg["split_mode"]), (total - largest) / total)
        return beta_cfg["split_mode"]


@dataclass
class TiePair:
    """10kV/110kV 联络对(ties.csv 一行)。"""

    tie_id: str
    station_a: str
    station_b: str
    n_channels: int
    conductor_type: str
    ampacity_mw: float
    sigma_load: float
    sigma_pv: float
    switch_mode: str  # "loop" | "outage" | "forbidden"
    sensitive: bool

    @property
    def usable(self) -> bool:
        """可用联络:非禁用开关模式,且非敏感联络。"""
        return self.switch_mode != "forbidden" and not self.sensitive


@dataclass
class Zone:
    """高压分区(由若干 Station 汇聚)。"""

    zone_id: str
    county: str
    area_type: str
    stations: list[Station] = field(default_factory=list)
