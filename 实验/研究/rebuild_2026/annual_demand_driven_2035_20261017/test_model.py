"""只覆盖年度承接、转供证据与安全校核的关键反例。"""
import copy
import unittest

import numpy as np

from . import model as m, prepare as p
from .verify import independent_cost


class AnnualDemandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inp,cls.powers=p.load('pizhou')
        cls.old=np.array([s['initial_units']+[0.] for s in cls.inp['stations'].values()])
        cls.n=np.zeros(len(cls.old),int)

    def build(self,inp=None,replaced=None,oldn=None):
        return m.build(inp or self.inp,self.powers[2022],2022,'elastic_engineering',self.old,
            self.n if oldn is None else oldn,set(),np.zeros((len(self.old),2),bool) if replaced is None else replaced,{(0,-1)})

    def test_future_demand_does_not_select_current_equipment(self):
        inp=copy.deepcopy(self.inp)
        for y in range(2023,2036):
            # 2025是本次历史回算的固定空间模板与馈线标定基数。
            if y==2025:continue
            inp['annual_observed_peak_mw'][str(y)]*=100
            inp['common_floor_by_year'][str(y)]=10
            for kind in ('transformer','storage','line'):inp['cost_factors'][kind][str(y)]*=100
        a,_,_=self.build();b,_,_=self.build(inp)
        for key in ('costs','lower_bounds','upper_bounds','entries','constraint_lower','constraint_upper'):
            self.assertEqual(getattr(a,key),getattr(b,key))

    def test_in_service_storage_is_retained_and_not_rebought(self):
        n=self.n.copy();n[0]=100
        native,meta,_=self.build(oldn=n);sid=next(iter(self.inp['stations']))
        self.assertEqual(native.lower_bounds[meta['modules'][sid,2022]],100)
        self.assertAlmostEqual(native.costs[meta['one']],-100*self.inp['storage_module_capex_10k']*self.inp['cost_factors']['storage']['2022'])
        _,capex,npvs=independent_cost(self.inp,2022,self.old,n,set(),self.old,n,set())
        self.assertEqual(sum(capex),0);self.assertEqual(sum(npvs),0)

    def test_replaced_position_cannot_be_replaced_again(self):
        locked=np.zeros((len(self.old),2),bool);locked[0,0]=True
        native,meta,_=self.build(replaced=locked);sid=next(iter(self.inp['stations']))
        for (s,slot,y,r),v in meta['x'].items():
            if s==sid and slot==0:self.assertEqual(native.upper_bounds[v],float(abs(r-self.old[0,0])<1e-8))

    def test_existing_transfer_cannot_exceed_original_budget(self):
        inp=copy.deepcopy(self.inp);aa=m.arcs(inp)
        k=next(k for k,a in enumerate(aa) if a['existing']);sid=aa[k]['source']
        inp['existing_transfer_budget_by_year_mw']['2022'][sid]=0
        with self.assertRaises(AssertionError):m.verify(inp,self.powers[2022],2022,self.old,self.n,set(),{}, {k:1})

    def test_missing_assets_are_detected_under_n1(self):
        units=self.old.copy();units[0]=0
        checked,bad=m.verify(self.inp,self.powers[2022],2022,units,self.n,set(),{}, {})
        self.assertFalse(checked['verified']);self.assertTrue(bad)

    def test_baseline_normal_blocks_can_return_but_cannot_expand(self):
        inp,powers=p.load('city');old=np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
        native,meta,_=m.build(inp,powers[2033],2033,'rigid',old,np.zeros(len(old),int),set(),
            np.zeros((len(old),2),bool),{(0,-1)})
        for k,a in enumerate(meta['arcs']):
            if a['existing']:
                v=meta['normal_blocks'][k]
                self.assertEqual(native.lower_bounds[v],0.)
                self.assertEqual(native.upper_bounds[v],inp['baseline_normal_blocks'].get(str(k),0))

    def test_support_objective_counts_new_lines_with_auxiliary_purchase_costs(self):
        from .capacity import objective_vectors
        native,meta,_=self.build()
        _,support=objective_vectors(self.inp,native,meta,2022,self.n,set())
        self.assertTrue(meta['edgevars'])
        price=self.inp['line_capex_10k']*self.inp['cost_factors']['line']['2022']
        for v in meta['edgevars'].values():self.assertAlmostEqual(support[v],price)

    def test_purchase_auxiliary_values_match_selected_equipment(self):
        native,meta,_=self.build();ids=list(self.inp['stations'])
        for key,purchase in meta['purchases'].items():
            sid,slot,y,r=key;chosen=meta['x'][key]
            if abs(r-self.old[ids.index(sid),slot])<1e-8:
                self.assertEqual(native.upper_bounds[purchase],0.)
            else:
                rows=[row for row,column,value in native.entries if column==purchase and value==1.]
                self.assertTrue(any(native.constraint_lower[row]==0. and native.constraint_upper[row]==0.
                    and (row,chosen,-1.) in native.entries for row in rows))


if __name__=='__main__':unittest.main()
