"""验证前推基数、两个独立增长因子以及经济口径的接续。"""
import json

import numpy as np

from . import run as m


def test_forecast_preserves_all_provided_nodes_and_interpolates_only_gaps():
    values={r['year']:r for r in m.forecasts()}
    assert values[2025]['city_load_mw']==2850
    assert values[2029]['city_load_mw']==3320 and values[2033]['city_load_mw']==3865
    assert values[2035]['city_load_mw']==4150 and values[2035]['citywide_pv_index']==1840
    assert values[2026]['city_load_mw']==2967.5 and values[2034]['city_load_mw']==4007.5
    assert values[2031]['citywide_pv_index']==1253.6
    assert values[2025]['load_factor']==values[2025]['pv_factor']==1.
    assert not values[2030]['pv_interpolated'] and values[2031]['pv_interpolated']


def test_new_cost_factors_match_frozen_formula_in_existing_years():
    old=json.loads((m.ORIGINAL/'inputs.json').read_text())
    for kind,life,om in [('transformer',m.TRANSFORMER_LIFE,m.TRANSFORMER_OM),
                         ('line',m.LINE_LIFE,m.LINE_OM),('storage',m.STORAGE_LIFE,m.STORAGE_OM)]:
        for year in [2022,2023,2024,2025]:
            assert abs(m.factor(year,life,om)-old['cost_factors'][kind][str(year)])<1e-12
        assert m.factor(2035,life,om)>0


def test_baseline_and_two_factors_are_not_conflated():
    inp=json.loads((m.RAW/'inputs.json').read_text())
    z=np.load(m.RAW/'base_components.npz')
    net=z['net_2025_mw'];d=z['demand_proxy_mw'];g=z['generation_proxy_mw']
    assert np.max(abs(d-g-net))<1e-10
    assert np.min(g)>=0
    assert abs(net.sum(axis=1).max()-1528.82)<1e-8
    assert inp['initial_capacity_mva']==3113.5 and inp['years']==list(range(2026,2036))
    assert abs(inp['annual_observed_peak_mw']['2035']-1528.82*4150/2850)<1e-9
    # 光伏增长高于负荷时，同期日间净功率须比共同缩放更低。
    with_pv=g>1e-6
    forecast=d*(4150/2850)-g*(1840/709)
    assert np.all(forecast[with_pv]<(net*(4150/2850))[with_pv])
