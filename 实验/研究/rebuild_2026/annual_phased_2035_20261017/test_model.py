"""用上一版安全可行但首年集中建设的整数解检查新增分期边界。"""
import json
import unittest

import numpy as np
from scipy.sparse import coo_matrix

from . import model as m, prepare as p


class PhasedConstruction(unittest.TestCase):
    def test_old_front_loaded_solution_violates_new_construction_limit(self):
        for region in p.REGIONS:
            inp,powers=p.load(region);source=p.parent.RAW/region/'elastic_capacity'/'2022'
            state=json.loads((source/'adopted.json').read_text());previous=json.loads((source/'previous_assets.json').read_text())
            old=np.array(previous['units']);oldn=np.array(previous['modules']);replaced=np.array(previous['replaced'])
            args=(inp,powers[2022],2022,'elastic_capacity',old,oldn,set(),replaced,set(map(tuple,state['selected_pairs'])))
            native,meta,one=m.build(*args);z=np.load(source/'chosen_solution.npz')['solution']
            self.assertEqual(len(z),len(native.costs))
            rr,cc,vv=zip(*native.entries);A=coo_matrix((vv,(rr,cc)),shape=(len(native.constraint_upper),len(z))).tocsr()
            upper=A@z-np.array(native.constraint_upper)
            self.assertGreater(float(upper[-1]),0.)
            self.assertAlmostEqual(float(upper[-1]),state['annual']['capacity_mva']-m.schedule_limits(inp,2022,'elastic_capacity',old)[1],places=6)
            # 新增建设限制前，其余物理上界依然全部满足。
            self.assertLessEqual(float(max(upper[:-1])),1e-5)

    def test_actual_yearly_inputs_are_unchanged(self):
        for region in p.REGIONS:
            inp,powers=p.load(region);parent,original=p.parent.load(region)
            self.assertEqual(inp['annual_observed_peak_mw'],parent['annual_observed_peak_mw'])
            self.assertEqual(inp['common_floor_by_year'],parent['common_floor_by_year'])
            self.assertEqual(inp['initial_capacity_mva'],parent['initial_capacity_mva'])
            for y in range(2021,2036):np.testing.assert_array_equal(powers[y],original[y])

    def test_construction_constraint_is_shared(self):
        inp,powers=p.load('pizhou');old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
        for case in ('rigid','elastic_capacity'):
            native,meta,_=m.build(inp,powers[2022],2022,case,old,np.zeros(len(old),int),set(),np.zeros((len(old),2),bool),set())
            self.assertLessEqual(native.constraint_upper[-1],old.sum()*1.05)
            self.assertEqual(inp['annual_capacity_addition_limit_rate'],.05)

    def test_terminal_schedule_does_not_waive_last_year_rate(self):
        inp,_=p.load('city');old=np.array(inp['terminal_transformer_portfolios']['elastic_capacity'])*.9
        lower,upper=m.schedule_limits(inp,2035,'elastic_capacity',old)
        self.assertGreater(lower,upper)
        self.assertLessEqual(upper,old.sum()*1.05)


if __name__=='__main__':unittest.main()
