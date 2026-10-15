"""独立复算原解、费用、起点、矩阵与工作簿，保留不可行结论。"""
import json
import math

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from scipy.sparse import coo_matrix

from ..review_20261015.target_warm import cost
from . import model as m
from . import matrices


def verify_cases():
    proof=json.loads((m.REVIEW/'两区县独立运行核验.json').read_text());assert proof['verified'] and len(proof['sources'])==8
    assert sum(s['feasible'] for s in proof['sources'])==7
    expected={(r,b,c) for r in m.REGIONS for b in m.BASELINES for c in m.CASES}
    assert {(s['region'],s['baseline'],s['case']) for s in proof['sources']}==expected
    count=0
    for record in proof['sources']:
        r,b,c=(record[k] for k in ['region','baseline','case']);inp,scenes,root=m.prepare(r,b)
        assert inp['years']==[2022,2023,2024,2025] and inp['fixed_baseline_year']==2021
        assert m.old.sha(root/'inputs.json')==record['input_sha256']
        original=json.loads((m.old.OUT/r/(b+'_reverse80')/'inputs.json').read_text())
        for k in ['stations','network','initial_capacity_mva','initial_peak_mw','cost_factors','existing_transfer_budget_by_year_mw']:
            assert inp[k]==original[k]
        assert abs(sum(sum(v['initial_units']) for v in inp['stations'].values())-inp['initial_capacity_mva'])<1e-8
        if b=='annual_2021':assert inp['initial_capacity_mva']==inp['annual_observed_capacity_mva']['2021']
        if not record['feasible']:
            assert (r,b,c)==('pizhou','annual_2021','rigid')
            certificate=json.loads((m.REVIEW/'邳州原表起点刚性无解独立证据.json').read_text())
            assert certificate['verified'] and certificate['input_sha256']==record['input_sha256']
            assert m.old.sha(root/'rigid_main/iteration_01_solver.json')==certificate['solver_sha256']
            assert max(x['最小松弛_MW'] for x in certificate['records'])>4.9
            continue
        folder=m.ROOT/record['folder']
        for name in ['chosen_solution.npz','selected_pairs.json','stations.csv','projects.csv','normal_fractions.json','summary.json']:
            assert m.old.sha(folder/name)==record[name]
        summary=json.loads((folder/'summary.json').read_text());assert not summary['selection_conditions']
        selected={tuple(v) for v in json.loads((folder/'selected_pairs.json').read_text())}
        native,meta=m.build(inp,scenes,c,selected);z=np.load(folder/'chosen_solution.npz')['solution'];assert len(z)==len(native.costs)
        ri,ci,values=zip(*native.entries);lhs=coo_matrix((values,(ri,ci)),shape=(len(native.constraint_lower),len(z))).tocsr()@z
        assert max(np.max(np.array(native.constraint_lower)-lhs),np.max(lhs-np.array(native.constraint_upper)),
            np.max(np.array(native.lower_bounds)-z),np.max(z-np.array(native.upper_bounds)))<1e-5
        integers=z[np.array(native.integrality,dtype=bool)];assert np.max(abs(integers-np.rint(integers)))<1e-5
        assert abs(np.dot(native.costs,z)-summary['cost_npv_10k'])<1e-4
        fractions={(x['year'],x['edge'],x['direction']):x['fraction'] for x in json.loads((folder/'normal_fractions.json').read_text())}
        assert all(abs(z[v]-fractions.get(key,0.))<1e-8 for key,v in meta['normal_fractions'].items())
        oldunits=np.array([v['initial_units']+[0.] for v in inp['stations'].values()]);oldn=np.zeros(len(oldunits));oldbuilt=set();states={};byyear={}
        for a in summary['annual']:
            y=a['year'];u,n,built=m.old.old.assets_from_csv(inp,folder,y);nu,nn,_,_=m.old.old.base.assets.assets(inp,z,meta,y)
            assert np.allclose(u,nu,atol=1e-8,rtol=0) and np.array_equal(n,nn)
            assert {eid for (eid,yy),v in meta['edgevars'].items() if yy==y and z[v]>.5}==built
            assert np.all(u>=oldunits-1e-8) and np.all(n>=oldn) and built>=oldbuilt
            if c=='rigid':assert u.sum()<=max(oldunits.sum(),2*a['peak_mw'])+1e-8
            assert abs(u.sum()-a['capacity_mva'])<1e-8 and abs(u.sum()/a['peak_mw']-a['clr'])<1e-9
            oldunits,oldn,oldbuilt=u,n,built;states[y]=(u,n);byyear[y]=built
        value=cost(inp,states,byyear);assert abs(value-summary['cost_npv_10k'])<1e-4
        assert summary['solver']['dual_bound']<=value+1e-4
        assert abs(max(0.,(value-summary['solver']['dual_bound'])/max(1.,abs(value)))-summary['solver']['mip_gap'])<1e-9
        count+=1;print('VERIFIED_ECONOMIC_CASE',r,b,c,flush=True)
    assert all(x['verified'] and x['max_violation_mw']<1e-5 for x in proof['normal_checks']) and all(x['verified'] for x in proof['dispatch_records'])
    return dict(feasible_schemes=count,infeasible_schemes=1,static_pairs=proof['static_pairs'],normal_station_hours=proof['normal_station_hours'])


def verify_matrices():
    source,formal,stats,chosen,mat,nodes,fs=matrices.select();proof=json.loads((m.REVIEW/'典型矩阵独立核验.json').read_text())
    assert proof['verified'] and proof['source_sha256']==m.old.sha(source) and proof['formal_source_sha256']==m.old.sha(formal)
    assert {r['raw_line'] for r in proof['records']}=={r['raw_line'] for r in chosen}
    assert all(r['verified'] and r['max_violation_mw']<1e-5 for r in proof['records'])
    pd.testing.assert_frame_equal(mat,pd.read_csv(m.PUBLIC/'典型响应推荐矩阵.csv'),check_dtype=False)
    pd.testing.assert_frame_equal(nodes,pd.read_csv(m.PUBLIC/'典型场景完整节点.csv'),check_dtype=False)
    return dict(matrix_nodes=len(chosen),matrix_scenarios=len(mat))


def verify_workbooks():
    reports=[]
    for name in ['两区县逐年经济方案.xlsx','推广典型响应矩阵.xlsx']:
        book=load_workbook(m.PUBLIC/name,read_only=True,data_only=True);count=0
        for s in book:
            frame=pd.read_csv(m.PUBLIC/(s.title+'.csv'),keep_default_na=False);rows=list(s.values)
            assert list(rows[0])==list(frame.columns) and len(rows)==len(frame)+1
            for aa,bb in zip(rows[1:],frame.itertuples(index=False,name=None)):
                for a,b in zip(aa,bb):
                    a='' if a is None else a
                    try:av,bv=float(a),float(b)
                    except (TypeError,ValueError):assert str(a)==str(b),(name,s.title,a,b)
                    else:assert math.isclose(av,bv,rel_tol=1e-10,abs_tol=1e-8),(name,s.title,a,b)
                    count+=1
        reports.append(dict(file=name,cells=count,sha256=m.old.sha(m.PUBLIC/name),verified=True));book.close()
    return reports


def main():
    result=dict(verified=True,**verify_cases(),**verify_matrices(),workbooks=verify_workbooks())
    m.old.dump(m.REVIEW/'最终经济方案核验.json',result);print('VERIFIED_TWO_DISTRICTS',result,flush=True)


if __name__=='__main__':main()
