"""固定2021基期、原表总量及两地区储能时长的回归检查。"""
import json

from . import model as m


def test_fixed_baseline_and_annual_input_are_shared():
    expected={'pizhou':(1463.5,2027.,2),'city':(2900.,3113.5,6)}
    for region,(compressed,original,duration) in expected.items():
        a,sa,_=m.prepare(region,'compressed');b,sb,_=m.prepare(region,'annual_2021')
        assert a['initial_capacity_mva']==compressed and b['initial_capacity_mva']==original
        assert a['years']==b['years']==[2022,2023,2024,2025]
        assert a['network']==b['network'] and a['cost_factors']==b['cost_factors']
        assert a['existing_transfer_budget_by_year_mw']==b['existing_transfer_budget_by_year_mw']
        assert all(s['forward_duration_h']==duration for s in a['stations'].values())
        for y in a['years']:assert (sa[y]==sb[y]).all()


def test_economic_model_inherits_no_comparison_preference():
    inp,scenes,_=m.prepare('pizhou','compressed')
    selected={(y,0,-1) for y in inp['years']}
    native,meta=m.build(inp,scenes,'elastic_free',selected)
    oldinp=json.loads((m.parent.RAW/'邳州/inputs.json').read_text())
    original,om=m.parent.build(oldinp,scenes,'elastic_free',selected)
    assert native.costs==original.costs and native.entries==original.entries
    assert native.constraint_lower==original.constraint_lower and native.constraint_upper==original.constraint_upper
    assert {k[2] for k in meta['x']}=={2022,2023,2024,2025}
