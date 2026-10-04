"""核对甲方费用边界在规划评价期内的现金流含义。"""
import pytest
from 实验.研究.rebuild_2026.current_economic_assumptions import cost_factors,line_capex
from 实验.研究.rebuild_2026.incremental_cost import lifecycle_cashflows

def test_all_current_asset_lifetimes_extend_beyond_evaluation_end():
    for year in range(2022,2026):
        for life,maintenance in [(40,.042),(40,.022),(25,.03)]:
            flows=lifecycle_cashflows(100,year,life,maintenance)
            assert not any(f['component']=='renewal_capex' for f in flows)
            maintenance_flows=[f for f in flows if f['component']=='fixed_om']
            assert [f['year'] for f in maintenance_flows]==list(range(year+1,2042))
            assert sum(f['amount_10k_cny'] for f in maintenance_flows)==pytest.approx(100*maintenance*(2041-year))

def test_transformer_and_line_maintenance_have_distinct_present_values():
    factors=cost_factors()
    assert factors['transformer'][2022]==pytest.approx(1.3855102760854008)
    assert factors['line'][2022]==pytest.approx(1.1749797762423977)
    assert factors['storage'][2022]==pytest.approx(1.2591919761795989)
    assert factors['transformer'][2025]>factors['line'][2025]

def test_cable_civil_cost_enters_both_line_categories():
    assert line_capex(.1)==pytest.approx(124.8)
    assert line_capex(.9)==pytest.approx(499.2)
    assert line_capex(1)==pytest.approx(546)
    with pytest.raises(ValueError):line_capex(1.1)
