"""计算层:典型日压缩(k-means 代表日 + 强制双极端日)+ 全年回代骨架。

MILP 用 k(+0~2)个代表日近似全年 8760 时序以降规模;playback_violations
提供方案落地后全年逐时回代校核的调用入口(M1 只搭骨架,真实校核逻辑由
调用方通过 constraints_fn 注入,归 Task 7 verify_* 模块)。
纯函数,不做 IO——pnet_total 由调用方(如 data.pnet.sum(axis=1))传入。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

# 与全局合成数据种子一致(params.yaml: synthetic.seed),保证聚类结果可复现
SEED = 20260721
_HOURS_PER_DAY = 24


@dataclass
class TypicalDays:
    """Task 5 对外接口:典型日压缩结果。"""

    day_index: list[int]       # 入选日序号(升序,取值0..364),k个聚类代表+双极端日去重
    weights: dict[int, float]  # 日序号 -> 权重(所代表天数);极端日权重=1;Σ==365


def reduce_days(pnet_total: pd.Series, k: int) -> TypicalDays:
    """k-means 压缩全年 365 天为 k 个代表日,并强制附加正/反极端日。

    特征矩阵 = 365x24(每日24h县总净负荷向量,pnet_total 8760小时按天reshape)。
    每簇代表日 = 离簇心欧氏距离最近的真实日(而非质心本身,保证回代用的是真实曲线)。
    极端日 = 全年 pnet_total 最大值(正向峰)/最小值(反向峰)所在日;若已是其所属
    簇的代表日则不重复加;否则以权重1强制加入,并从其所属簇代表日的权重里扣1
    (保证Σweights==365 守恒不变)。
    """
    values = pnet_total.to_numpy()
    n_hours = len(values)
    assert n_hours % _HOURS_PER_DAY == 0, (
        f"pnet_total length {n_hours} not divisible by {_HOURS_PER_DAY}"
    )
    n_days = n_hours // _HOURS_PER_DAY
    features = values.reshape(n_days, _HOURS_PER_DAY)

    km = KMeans(n_clusters=k, random_state=SEED, n_init=10)
    labels = km.fit_predict(features)

    rep_of_cluster: dict[int, int] = {}
    count_of_cluster: dict[int, int] = {}
    for c in range(k):
        members = np.flatnonzero(labels == c)
        count_of_cluster[c] = len(members)
        dists = np.linalg.norm(features[members] - km.cluster_centers_[c], axis=1)
        rep_of_cluster[c] = int(members[int(np.argmin(dists))])

    day_index_set = set(rep_of_cluster.values())
    weights: dict[int, float] = {
        rep_of_cluster[c]: float(count_of_cluster[c]) for c in range(k)
    }

    fwd_day = int(np.argmax(values)) // _HOURS_PER_DAY
    rev_day = int(np.argmin(values)) // _HOURS_PER_DAY

    for extreme_day in (fwd_day, rev_day):
        cluster = int(labels[extreme_day])
        rep = rep_of_cluster[cluster]
        if extreme_day == rep or extreme_day in day_index_set:
            continue  # 已在代表日集合中,不重复加(裁决:day_index 去重)
        day_index_set.add(extreme_day)
        weights[extreme_day] = 1.0
        weights[rep] -= 1.0

    return TypicalDays(day_index=sorted(day_index_set), weights=weights)


def playback_violations(
    solution: Any,
    data: Any,
    constraints_fn: Callable[[Any, Any, int], list[str]],
) -> list[dict]:
    """M1 骨架:对全年 8760 个时刻逐一调用 constraints_fn 回代校核。

    constraints_fn(solution, data, t) -> 该时刻违约描述列表(str);空列表=该
    时刻无违约、不计入结果。聚合返回 [{'t': int, 'violations': [...]}, ...]。
    真实校核逻辑(潮流/N-1/DL-T2041)由 Task 7 verify_* 模块的 constraints_fn 实现。
    """
    n_hours = len(data.pnet)
    result: list[dict] = []
    for t in range(n_hours):
        violations = constraints_fn(solution, data, t)
        if violations:
            result.append({"t": t, "violations": violations})
    return result
