"""覆盖新增边界：既有/新增合并、禁止正常卸载与远景采购。"""
import unittest

import numpy as np

from . import model as m, prepare as p


class TransferBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inp,cls.powers=p.load('city');cls.ids=list(cls.inp['stations']);cls.aa=m.arcs(cls.inp)
        cls.old=np.array([s['initial_units']+[0.] for s in cls.inp['stations'].values()])
        cls.n=np.zeros(len(cls.ids),int)

    def test_normal_export_rejected_even_with_paid_line(self):
        k=next(k for k,a in enumerate(self.aa) if not a['existing'])
        with self.assertRaisesRegex(AssertionError,'正常跨站'):
            m.verify(self.inp,self.powers[2035],2035,self.old,self.n,{self.aa[k]['id']},{k:1},{})

    def test_existing_and_new_share_one_station_limit(self):
        for sid in self.ids:
            limit=m.block_limit(self.inp,sid)
            old=[(k,a) for k,a in enumerate(self.aa) if a['source']==sid and a['existing']]
            paid=[(k,a) for k,a in enumerate(self.aa) if a['source']==sid and not a['existing']]
            if not old or sum(a['limit'] for k,a in paid)<limit:continue
            first=min(old[0][1]['limit'],limit);counts={old[0][0]:first};left=limit+1-first
            for k,a in paid:
                take=min(a['limit'],left);counts[k]=take;left-=take
                if not left:break
            if left:continue
            self.assertLessEqual(first,limit)
            self.assertLessEqual(sum(counts.values())-first,limit)
            with self.assertRaises(AssertionError):
                m.verify(self.inp,self.powers[2035],2035,self.old,self.n,set(),{},counts)
            return
        self.fail('未找到既有与新增分别合规、合计越界的真实代理站')

    def test_purchase_respects_future_but_preserves_original_unit(self):
        native,meta,_=m.build(self.inp,self.powers[2022],2022,'elastic_capacity',self.old,self.n,set(),
            np.zeros((len(self.ids),2),bool),set())
        checked=0
        for (sid,slot,y,r),v in meta['x'].items():
            old=self.old[self.ids.index(sid),slot];target=self.inp['replacement_rating_target_mva'][sid]
            if r>old+1e-7 and r<target-1e-7:
                self.assertEqual(native.upper_bounds[v],0.);checked+=1
            if abs(r-old)<1e-7:self.assertGreaterEqual(native.upper_bounds[v],1.)
        self.assertGreater(checked,0)

    def test_hourly_data_and_common_floors_unchanged(self):
        parent,pp=p.parent.load('city')
        self.assertEqual(self.inp['common_floor_by_year'],parent['common_floor_by_year'])
        self.assertEqual(self.inp['annual_observed_peak_mw'],parent['annual_observed_peak_mw'])
        for y in range(2021,2036):np.testing.assert_array_equal(self.powers[y],pp[y])

    def test_auxiliary_objective_prices_paid_path(self):
        from .capacity import objective_vectors
        native,meta,_=m.build(self.inp,self.powers[2022],2022,'elastic_capacity',self.old,self.n,set(),
            np.zeros((len(self.ids),2),bool),set())
        price,support=objective_vectors(self.inp,native,meta,2022,self.n,set())
        v=next(iter(meta['edgevars'].values()))
        self.assertEqual(price[v],0.)
        self.assertAlmostEqual(support[v],self.inp['line_capex_10k']*self.inp['cost_factors']['line']['2022'])
        self.assertGreater(support[v],0.)


if __name__=='__main__':unittest.main()
