"""Task 5 测试:src/typical_days.py 典型日压缩(k-means 代表日 + 双极端日)+ 回代骨架。

覆盖简报 Step 1 三断言(k=12,真实合成数据 pnet_total = data.pnet.sum(axis=1)):
1. len(day_index) ∈ [12, 14](k 个聚类代表 + 0~2 个强制极端日,去重后)
2. Σweights == 365(代表日"代表天数"权重与强制极端日权重,扣减后总量守恒)
3. 全年 P⁺(pnet_total 最大值)、P⁻(最小值)所在日必在 day_index 集合内

另覆盖:
4. day_index 升序且与 weights 键集合一致
5. 8760 小时不能整除 24 时直接 assert(输入契约违反)
6. playback_violations 骨架:constraints_fn 恒返回 [] 时,回代结果为空列表
7. playback_violations 骨架:对逐时刻真实调用 constraints_fn,按非空结果聚合 {'t','violations'}
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.io_loader import load_scenario
from src.typical_days import TypicalDays, playback_violations, reduce_days

ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="module")
def scenario():
    return load_scenario(ROOT)


@pytest.fixture(scope="module")
def pnet_total(scenario):
    return scenario.pnet.sum(axis=1)


@pytest.fixture(scope="module")
def k(scenario):
    return scenario.params["milp"]["typical_days"]


@pytest.fixture(scope="module")
def typdays(pnet_total, k):
    return reduce_days(pnet_total, k)


# ---------------------------------------------------------------------------
# Step 1 三断言(逐字入测)
# ---------------------------------------------------------------------------


def test_day_index_length_in_range(typdays, k):
    assert len(typdays.day_index) in (k, k + 1, k + 2)


def test_weights_sum_to_365(typdays):
    assert sum(typdays.weights.values()) == pytest.approx(365.0)


def test_extreme_days_in_day_index(typdays, pnet_total):
    values = pnet_total.to_numpy()
    fwd_day = int(np.argmax(values)) // 24
    rev_day = int(np.argmin(values)) // 24
    assert fwd_day in typdays.day_index
    assert rev_day in typdays.day_index


# ---------------------------------------------------------------------------
# 结构一致性
# ---------------------------------------------------------------------------


def test_day_index_sorted_and_unique(typdays):
    assert typdays.day_index == sorted(set(typdays.day_index))


def test_day_index_matches_weights_keys(typdays):
    assert set(typdays.day_index) == set(typdays.weights.keys())


def test_day_index_in_valid_range(typdays):
    assert all(0 <= d <= 364 for d in typdays.day_index)


# ---------------------------------------------------------------------------
# 输入契约:8760 = 365*24 整除,不齐直接 assert
# ---------------------------------------------------------------------------


def test_reduce_days_rejects_non_divisible_length():
    bad = pd.Series(np.zeros(100))
    with pytest.raises(AssertionError):
        reduce_days(bad, k=3)


# ---------------------------------------------------------------------------
# playback_violations:M1 骨架 + 空跑
# ---------------------------------------------------------------------------


def test_playback_violations_empty_lambda_returns_empty_list(scenario):
    result = playback_violations(solution=None, data=scenario, constraints_fn=lambda solution, data, t: [])
    assert result == []


def test_playback_violations_aggregates_nonempty_hits(scenario):
    def constraints_fn(solution, data, t):
        return ["overload"] if t == 5 else []

    result = playback_violations(solution=None, data=scenario, constraints_fn=constraints_fn)
    assert result == [{"t": 5, "violations": ["overload"]}]


def test_playback_violations_covers_all_8760_hours(scenario):
    calls = []

    def constraints_fn(solution, data, t):
        calls.append(t)
        return []

    playback_violations(solution=None, data=scenario, constraints_fn=constraints_fn)
    assert calls == list(range(8760))
