"""验证正常替代机制、固定基期以及期内重复采购限制。"""
import copy

import highspy
import numpy as np
from scipy.sparse import coo_matrix

from . import model as m


def test_normal_storage_covers_forward_and_reverse_deficits():
    inp,_,_=m.prepare('pizhou','compressed');inp=copy.deepcopy(inp)
    for e in inp['network']['edges']:e['capacity_mw']=0.
    ids=list(inp['stations']);j=ids.index('BDZ-00162')
    u=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);lp=m.OperatingLP(inp)
    for sign,load,coef in [(1,.95*u[j].sum()+5,.215*.76/2),(-1,-.8*.95*u[j].sum()-5,.215*.76/3)]:
        p=np.zeros(len(ids));p[j]=load;n=np.zeros(len(ids));n[j]=np.ceil(5/coef)
        assert not lp.check(p,lp.prepared(p,2025,u,np.zeros(len(ids)),set()),-1)['verified']
        assert lp.check(p,lp.prepared(p,2025,u,n,set()),-1)['verified']


def fixed_procurement(repeated):
    inp,scenes,_=m.prepare('pizhou','compressed');native,meta=m.build(inp,scenes,'elastic_free',set())
    sid=next(s for s,v in inp['stations'].items() if v['initial_units']==[20.,50.])
    for (s,slot,y,r),v in meta['x'].items():
        rating=inp['stations'][s]['initial_units'][slot]
        if s==sid and slot==0:rating=50. if repeated and y>=2024 else 31.5
        native.lower_bounds[v]=native.upper_bounds[v]=float(abs(r-rating)<1e-8)
    for v in [*meta['modules'].values(),*meta['third'].values(),*meta['edgevars'].values()]:native.upper_bounds[v]=0.
    return solve_native(native)


def solve_native(native):
    ri,ci,vv=zip(*native.entries);a=coo_matrix((vv,(ri,ci)),shape=(len(native.constraint_lower),len(native.costs))).tocsr()
    p=highspy.HighsLp();p.num_col_,p.num_row_=a.shape[1],a.shape[0]
    p.col_cost_,p.col_lower_,p.col_upper_=native.costs,native.lower_bounds,native.upper_bounds
    p.row_lower_,p.row_upper_=native.constraint_lower,native.constraint_upper
    p.integrality_=[highspy.HighsVarType.kInteger if k else highspy.HighsVarType.kContinuous for k in native.integrality]
    p.a_matrix_.format_=highspy.MatrixFormat.kRowwise;p.a_matrix_.start_,p.a_matrix_.index_,p.a_matrix_.value_=a.indptr,a.indices,a.data
    h=highspy.Highs();h.setOptionValue('threads',1);h.setOptionValue('log_to_console',False);h.passModel(p);h.run()
    return h.getModelStatus()


def test_single_purchase_can_remain_but_cannot_be_replaced_again():
    assert fixed_procurement(False)==highspy.HighsModelStatus.kOptimal
    assert fixed_procurement(True)==highspy.HighsModelStatus.kInfeasible


def test_planning_master_also_allows_normal_storage_substitution():
    inp,_,_=m.prepare('pizhou','compressed');ids=list(inp['stations']);sid='BDZ-00162';j=ids.index(sid)
    for demand,modules in [(43.,62),(-35.4,92)]:
        p=np.zeros((1,len(ids)));p[0,j]=demand
        for active in [False,True]:
            scenes={y:p for y in inp['years']};native,meta=m.build(inp,scenes,'elastic_free',{(2022,0,-1)})
            for (s,slot,y,r),v in meta['x'].items():
                native.lower_bounds[v]=native.upper_bounds[v]=float(abs(r-inp['stations'][s]['initial_units'][slot])<1e-8)
            for (s,y),v in meta['modules'].items():native.lower_bounds[v]=native.upper_bounds[v]=modules if active and s==sid else 0.
            for v in [*meta['third'].values(),*meta['edgevars'].values(),*[row[-1] for row in meta['network_flows']]]:native.upper_bounds[v]=0.
            status=solve_native(native)
            assert status==(highspy.HighsModelStatus.kOptimal if active else highspy.HighsModelStatus.kInfeasible)


def test_two_baselines_share_load_network_and_economic_inputs():
    for region,capacity in [('pizhou',2027.),('city',3113.5)]:
        a,sa,_=m.prepare(region,'compressed');b,sb,_=m.prepare(region,'annual_2021')
        assert a['years']==b['years']==[2022,2023,2024,2025]
        assert b['initial_capacity_mva']==capacity
        for key in ['network','cost_factors','existing_transfer_budget_by_year_mw']:assert a[key]==b[key]
        for y in a['years']:assert np.array_equal(sa[y],sb[y])
