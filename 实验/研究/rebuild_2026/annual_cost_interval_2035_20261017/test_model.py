"""覆盖四年窗口边界和年度模型的实际设备选择边界。"""
import copy

import numpy as np
import pytest

from . import model as m, prepare as p


def test_replacement_interval_boundaries():
    last = np.array([[2022, 0], [2025, 2023]])
    np.testing.assert_array_equal(m.locked_positions(last, 2026), [[False, False], [True, True]])
    np.testing.assert_array_equal(m.locked_positions(last, 2027), [[False, False], [True, False]])
    np.testing.assert_array_equal(m.locked_positions(last, 2029), np.zeros((2, 2), bool))
    with pytest.raises(AssertionError):
        m.locked_positions([[2026, 0]], 2026)


def test_actual_transformer_choice_unlocks_after_four_years():
    inp, powers = p.load('city')
    old = np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
    last = np.zeros((len(old), 2), int)
    last[0, 0] = 2022
    sid = next(iter(inp['stations']))
    for year, expected in ((2025, 0.), (2026, 1.)):
        native, meta, _ = m.build(inp, powers[year], year, 'elastic', old,
                                  np.zeros(len(old), int), set(), last, set())
        v = meta['x'][sid, 0, year, 80.]
        assert native.upper_bounds[v] == expected


def test_future_forecast_does_not_change_current_year_model():
    inp, powers = p.load('pizhou')
    old = np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
    args = (old, np.zeros(len(old), int), set(), np.zeros((len(old), 2), int), {(0, -1)})
    first, _, _ = m.build(inp, powers[2026], 2026, 'elastic', *args)
    altered = copy.deepcopy(inp)
    for year in range(2027, 2036):
        altered['annual_observed_peak_mw'][str(year)] *= 10.
    second, _, _ = m.build(altered, powers[2026], 2026, 'elastic', *args)
    assert first.costs == second.costs
    assert first.entries == second.entries
    assert first.constraint_lower == second.constraint_lower
    assert first.constraint_upper == second.constraint_upper


def test_transfer_and_economic_inputs_are_inherited_exactly():
    from ..annual_demand_driven_2035_20261017 import prepare as parent
    for region in p.REGIONS:
        inp, _ = p.load(region)
        original, _ = parent.load(region)
        for key in ('existing_transfer_budget_by_year_mw', 'port_group_count', 'network',
                    'baseline_normal_blocks', 'station_transfer_evidence', 'cost_factors',
                    'transformer_price_10k_per_purchased_mva', 'third_50mva_capex_10k',
                    'storage_module_capex_10k', 'line_capex_10k'):
            assert inp[key] == original[key]


def test_late_probe_feasible_set_expands_when_new_ties_are_optional():
    # 实例回归：开放候选线路不得强制全部建设而破坏间隔资源约束。
    import json
    result = p.RAW/'city/late_probes/2031/transformer_only/result.json'
    if not result.exists():
        pytest.skip('完整逐年与后期探测尚未生成')
    only = json.loads(result.read_text())
    optional = json.loads((result.parent.parent/'transformer_and_ties/result.json').read_text())
    assert only['status']=='可行' and optional['status']=='可行'
    for region in p.REGIONS:
        for year in range(2031,2036):
            root = p.RAW/region/'late_probes'/str(year)
            fixed = json.loads((root/'transformer_only/result.json').read_text())
            opened = json.loads((root/'transformer_and_ties/result.json').read_text())
            if fixed['status']=='可行':
                assert opened['status']=='可行'
            for r in (fixed,opened):
                assert r['status']=='可行' or r['solver']['proven_infeasible']


def test_duplicate_writer_is_rejected():
    from .run import case_lock
    with case_lock('test','test'):
        with pytest.raises(RuntimeError,match='拒绝并发写入'):
            with case_lock('test','test'):
                raise AssertionError('重复进程取得了同一方案的锁')


def test_storage_completion_preserves_assets_and_all_hour_safety():
    import json
    from .repair import complete_storage
    region,case,year = 'pizhou','elastic',2035
    inp,powers = p.load(region)
    folder = p.RAW/region/case/str(year)
    r = json.loads((folder/'adopted.json').read_text())
    pr = json.loads((folder/'previous_assets.json').read_text())
    native,meta,_ = m.build(inp,powers[year],year,case,np.array(pr['units']),np.array(pr['modules']),
        set(pr['built']),np.array(pr['last_replacement_year']),{tuple(v) for v in r['selected_pairs']})
    original = np.load(folder/'chosen_solution.npz')['solution']
    reduced = original.copy()
    for j,sid in enumerate(inp['stations']):
        reduced[meta['modules'][sid,year]] = pr['modules'][j]
    completed = complete_storage(inp,powers[year],reduced,meta,native)
    assert completed is not None
    u,n,bs,normal,extra = m.layout(inp,completed,meta)
    np.testing.assert_array_equal(u,r['units'])
    assert np.all(n>=pr['modules']) and np.all(n<=r['modules'])
    assert bs==set(r['built'])
    assert float(np.array(native.costs)@completed)<=float(np.array(native.costs)@original)+1e-5
    checked,bad = m.verify(inp,powers[year],year,u,n,bs,normal,extra)
    assert checked['verified'] and not bad
