"""复算八组资产、原始解、费用及工作簿；可独立重跑全部静态运行LP。"""
import argparse
import json
import math

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from scipy.sparse import coo_matrix

from ..review_20261015.target_warm import cost
from . import model as m
from .choose import selected as selected_folder


def verify(full_lp=False):
    record=json.loads((m.REVIEW/'案例来源与校核.json').read_text());assert record['verified']
    expected={(r,b,c) for r in m.REGIONS for b in m.BASELINES for c in m.CASES}
    assert {(r['region'],r['baseline'],r['case']) for r in record['sources']}==expected
    cases=[]
    for source in record['sources']:
        region,baseline,case=(source[k] for k in ['region','baseline','case'])
        inp,scenes,root=m.prepare(region,baseline);folder=m.ROOT/source['folder']
        assert folder==selected_folder(region,baseline,case)
        assert m.old.sha(root/'inputs.json')==source['input_sha256']
        for name,digest in source['files'].items():assert m.old.sha(folder/name)==digest,(source,name)
        original=json.loads((m.old.OUT/region/(baseline+'_reverse80')/'inputs.json').read_text())
        for key in ['stations','network','cost_factors','initial_capacity_mva','existing_transfer_budget_by_year_mw']:
            assert inp[key]==original[key]
        assert inp['fixed_baseline_year']==2021 and inp['years']==[2022,2023,2024,2025]
        assert not inp['normal_supply_area_fixed'] and not inp['selection_conditions']
        selected={tuple(r) for r in json.loads((folder/'selected_pairs.json').read_text())}
        native,meta=m.build(inp,scenes,case,selected);z=np.load(folder/'chosen_solution.npz')['solution']
        assert len(z)==len(native.costs)
        ri,ci,vv=zip(*native.entries);lhs=coo_matrix((vv,(ri,ci)),shape=(len(native.constraint_lower),len(z))).tocsr()@z
        violation=max(0.,float(np.max(np.array(native.constraint_lower)-lhs)),float(np.max(lhs-np.array(native.constraint_upper))),
            float(np.max(np.array(native.lower_bounds)-z)),float(np.max(z-np.array(native.upper_bounds))))
        integer=z[np.array(native.integrality,dtype=bool)]
        violation=max(violation,float(np.max(abs(integer-np.rint(integer)))));assert violation<1e-5
        summary=json.loads((folder/'summary.json').read_text());assert not summary['selection_conditions']
        assert abs(np.dot(native.costs,z)-summary['cost_npv_10k'])<1e-4
        before=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);oldn=np.zeros(len(before));oldbuilt=set()
        states={};byyear={};repeat=np.zeros((len(before),2),dtype=int)
        for a in summary['annual']:
            y=a['year'];u,n,built=m.old.old.assets_from_csv(inp,folder,y)
            zu,zn,_,_=m.old.old.base.assets.assets(inp,z,meta,y)
            assert np.allclose(u,zu,atol=1e-8,rtol=0) and np.array_equal(n,zn)
            assert np.all(u>=before-1e-8) and np.all(n>=oldn) and built>=oldbuilt
            assert {e for (e,yy),v in meta['edgevars'].items() if yy==y and z[v]>.5}==built
            assert abs(u.sum()-a['capacity_mva'])<1e-8 and abs(u.sum()/a['peak_mw']-a['clr'])<1e-9
            assert abs(n.sum()*.215-a['storage_mwh'])<1e-8 and len(built)==a['cumulative_lines']
            if case=='rigid':assert u.sum()<=max(before.sum(),2*a['peak_mw'])+1e-7
            repeat+=(u[:,:2]>before[:,:2]+1e-8);states[y]=(u,n);byyear[y]=built;before,oldn,oldbuilt=u,n,built
        assert repeat.max()<=1
        value=cost(inp,states,byyear);assert abs(value-summary['cost_npv_10k'])<1e-4
        solver=summary['solver'];assert solver['dual_bound']<=value+1e-4
        assert abs(solver['mip_gap']-max(0.,(value-solver['dual_bound'])/max(1.,abs(value))))<1e-9
        if 'reference_cost' in summary['method']:
            method=summary['method'];assert method['no_cross_scheme_ordering_constraints']
            assert value<=method['reference_cost']*1.05+1e-5
            assert abs(value/method['reference_cost']-1-method['actual_premium'])<1e-9
        proof=json.loads((folder/'independent_lp.json').read_text());assert proof['verified']
        pairs=0
        for y in inp['years']:
            checks=[r for r in proof['checks'] if r['year']==y];assert len(checks)==1 and checks[0]['verified']
            assert checks[0]['checked_pairs']==len(scenes[y])*(len(inp['stations'])+1)
            pairs+=checks[0]['checked_pairs']
        assert len(proof['records'])==pairs and all(r['verified'] for r in proof['records'])
        if full_lp:
            checks,violations,details=m.old.old.base.check_all(inp,scenes,z,meta,m.OperatingLP(inp));assert not violations
        cases.append(dict(region=region,baseline=baseline,case=case,verified=True,static_pairs=pairs,
            cost_npv_10k=value,lower_bound=solver['dual_bound'],gap=solver['mip_gap'],max_master_violation=violation))
        print('VERIFIED_STATIC_JOINT',region,baseline,case,pairs,flush=True)
    # 逐站功率平衡同时验证正常储能确实参与，而非只保留了一个空变量。
    balance=pd.read_csv(m.PUBLIC/'典型工况支撑.csv')
    served=balance['原净负荷_MW']-balance['转出_MW']+balance['转入_MW']
    assert np.max(abs(served-balance['转供后净负荷_MW']))<1e-7
    assert np.max(balance['所需放电_MW']-balance['储能正向上限_MW'])<1e-5
    assert np.max(balance['所需充电_MW']-balance['储能反向上限_MW'])<1e-5
    residual=served-balance['所需放电_MW']+balance['所需充电_MW']
    assert np.max(residual-balance['主变正向限值_MW'])<1e-5 and np.max(-residual-balance['主变反向限值_MW'])<1e-5
    normal=balance[balance['工况']=='正常'];assert normal[['所需放电_MW','所需充电_MW']].to_numpy().max()>4.9
    key=pd.read_csv(m.PUBLIC/'关键站替代关系.csv');assets=pd.read_csv(m.PUBLIC/'逐站设备.csv')
    assert len(key)==2*(20+29)
    for row in key.to_dict('records'):
        assert row['方向']==('反向吸收' if row['原净负荷_MW']<0 else '正向支撑')
        common=(balance['地区']==row['地区'])&(balance['起点']==row['起点'])&(balance['年份']==2025)&(balance['站号']==row['站号'])
        common&=(balance['截面']==row['截面'])&(balance['工况']=='N-1')&(balance['故障站']==row['站名'])
        for cname,suffix in [(m.CASES['rigid'],'刚性'),(m.CASES['elastic_free'],'弹性')]:
            b=balance[common&(balance['方案']==cname)];assert len(b)==1;b=b.iloc[0]
            a=assets[(assets['地区']==row['地区'])&(assets['起点']==row['起点'])&(assets['年份']==2025)&(assets['站号']==row['站号'])&(assets['方案']==cname)].iloc[0]
            for name in ['转出_MW','转入_MW','所需放电_MW','所需充电_MW']:
                assert abs(row[suffix+name]-b[name])<1e-8
            assert abs(row[suffix+'N1主变_MW']-b['主变正向限值_MW'])<1e-8
            assert abs(row[suffix+'储能_MWh']-a['储能_MWh'])<1e-8
    workbooks=[]
    book=load_workbook(m.PUBLIC/'两区县全套逐年方案.xlsx',read_only=True,data_only=True);count=0
    for sheet in book:
        frame=pd.read_csv(m.PUBLIC/(sheet.title+'.csv'),keep_default_na=False);rows=list(sheet.values)
        assert list(rows[0])==list(frame.columns) and len(rows)==len(frame)+1
        for aa,bb in zip(rows[1:],frame.itertuples(index=False,name=None)):
            for a,b in zip(aa,bb):
                a='' if a is None else a
                try:av,bv=float(a),float(b)
                except (TypeError,ValueError):assert str(a)==str(b)
                else:assert math.isclose(av,bv,rel_tol=1e-10,abs_tol=1e-8)
                count+=1
    book.close();workbooks.append(dict(file='两区县全套逐年方案.xlsx',cells=count,sha256=m.old.sha(m.PUBLIC/'两区县全套逐年方案.xlsx')))
    matrix=json.loads((m.SOURCE/'推广矩阵继承依据.json').read_text())
    for row in matrix['来源']:
        source=m.ROOT/row['path'];assert m.old.sha(source)==row['sha256']==m.old.sha(m.PUBLIC/source.name)
    return dict(verified=True,schemes=len(cases),static_pairs=sum(r['static_pairs'] for r in cases),
        full_lp_recomputed=full_lp,cases=cases,workbooks=workbooks,normal_storage_verified=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--full-lp',action='store_true');args=p.parse_args()
    result=verify(args.full_lp);m.old.dump(m.REVIEW/'最终核验.json',result);print('VERIFIED_STATIC_JOINT_ALL',result,flush=True)
