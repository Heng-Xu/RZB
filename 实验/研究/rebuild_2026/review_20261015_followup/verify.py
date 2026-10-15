"""核验新运行约束、逐年费用及输入解绑定的全静态工况证书。"""
import argparse
import json
import math
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import load_workbook

from ..review_20261015.target_warm import cost
from . import audit,cases as c
from .matrix_audit import cost_bounds_check


def lp_check(chosen):
    folder=c.ROOT/chosen['folder'];inp=json.loads((folder.parent/'inputs.json').read_text())
    scenes=c.prior.old.base.load_scenes(c.prior.old.base.OUT/'pizhou',inp);lp=c.OperatingLP(inp);pairs=0
    for y in inp['years']:
        units,n,built=c.prior.old.assets_from_csv(inp,folder,y)
        for p in scenes[y]:
            ready=lp.prepared(p,y,units,n,built)
            for f in range(-1,len(inp['stations'])):
                r=lp.check(p,ready,f);assert r['verified'],(chosen,y,f,r);pairs+=1
    print('VERIFIED_FOLLOWUP_LP',chosen['policy'],chosen['case'],pairs,flush=True)
    return dict(**chosen,checked_pairs=pairs,verified=True)


def signatures():
    a=json.loads((c.REVIEW/'案例收支及8760核验.json').read_text());assert a['verified']
    source=[]
    for item in a['sources']:
        folder=c.ROOT/item['folder']
        assert c.prior.sha(folder.parent/'inputs.json')==item['input_sha256']
        assert c.prior.sha(folder/'chosen_solution.npz')==item['solution_sha256']
        source.append(dict(**item,stations_sha256=c.prior.sha(folder/'stations.csv'),projects_sha256=c.prior.sha(folder/'projects.csv')))
    return source


def verify_costs(sources):
    for chosen in sources:
        folder=c.ROOT/chosen['folder'];inp=json.loads((folder.parent/'inputs.json').read_text())
        summary=json.loads((folder/'summary.json').read_text());states={};built_by_year={}
        if inp.get('followup_options',{}).get('station_floor'):
            reference=c.ROOT/inp['station_floor_reference']
            assert c.prior.sha(reference/'stations.csv')==inp['station_floor_reference_sha256']
            for y in inp['years']:
                assert list(inp['station_floor_by_year'][str(y)].values())==c.prior.old.assets_from_csv(inp,reference,y)[0].sum(axis=1).tolist()
        previous=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);previous_n=np.zeros(len(previous));previous_built=set()
        for a in summary['annual']:
            y=a['year'];units,n,built=c.prior.old.assets_from_csv(inp,folder,y)
            assert np.all(units>=previous-1e-8) and np.all(n>=previous_n) and built>=previous_built
            assert abs(units.sum()-a['capacity_mva'])<1e-7
            assert abs(units.sum()/a['peak_mw']-a['clr'])<1e-9
            assert abs(n.sum()*.215-a['storage_mwh'])<1e-7
            assert len(built)==a['cumulative_lines']
            if chosen['case']=='rigid':assert units.sum()<=max(previous.sum(),2*a['peak_mw'])+1e-7
            if inp.get('followup_options',{}).get('station_floor'):
                assert all(units[j].sum()>=inp['station_floor_by_year'][str(y)][sid]-1e-7 for j,sid in enumerate(inp['stations']))
            states[y]=(units,n);built_by_year[y]=built;previous,previous_n,previous_built=units,n,built
        value=cost(inp,states,built_by_year);assert abs(value-summary['cost_npv_10k'])<1e-4
        assert summary['solver']['dual_bound']<=value+1e-4
        assert abs(max(0.,(value-summary['solver']['dual_bound'])/value)-summary['solver']['mip_gap'])<1e-8


def verify_workbooks():
    def normalized(v):
        if v is None:return ''
        if isinstance(v,str):
            if v in ('True','False'):return v=='True'
            try:return float(v)
            except ValueError:return v
        return v
    results=[]
    for filename in ['邳州运行约束深化对照.xlsx','五参数平台完整审查.xlsx']:
        book=load_workbook(c.PUBLIC/filename,read_only=True,data_only=True);cells=0
        for sheet in book:
            if sheet.title=='说明':continue
            expected=pd.read_csv(c.PUBLIC/(sheet.title+'.csv'),keep_default_na=False)
            actual=list(sheet.values);assert list(actual[0])==list(expected.columns)
            assert len(actual)==len(expected)+1
            for row,record in zip(actual[1:],expected.itertuples(index=False,name=None)):
                for x,y in zip(row,record):
                    x,y=normalized(x),normalized(y)
                    if isinstance(x,(int,float)) and isinstance(y,(int,float)):
                        assert math.isclose(x,y,rel_tol=1e-10,abs_tol=1e-8),(filename,sheet.title,x,y)
                    else:assert x==y,(filename,sheet.title,x,y)
                    cells+=1
        results.append(dict(file=filename,cells=cells,sha256=c.prior.sha(c.PUBLIC/filename),verified=True));book.close()
    return results


def main():
    p=argparse.ArgumentParser();p.add_argument('--full-lp',action='store_true');p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    sources=signatures();verify_costs(sources);new=[r for r in sources if r['policy']!='previous']
    proof=c.REVIEW/'新方案全工况独立LP.json'
    if a.full_lp:
        results=[]
        with ProcessPoolExecutor(max_workers=a.workers) as pool:
            futures=[pool.submit(lp_check,r) for r in new]
            for f in as_completed(futures):results.append(f.result())
        results.sort(key=lambda r:(r['policy'],r['case']))
        c.prior.dump(proof,dict(verified=True,records=results))
    saved=json.loads(proof.read_text());assert saved['verified']
    assert [{k:r[k] for k in new[0]} for r in saved['records']]==sorted(new,key=lambda r:(r['policy'],r['case']))
    normal=pd.read_csv(c.PUBLIC/'8760正常方式.csv');assert normal['正常无储能无转供通过'].all()
    assert normal['正常无储能无转供最大越限_MW'].max()<1e-6
    for name in ['五参数平台核验.json','转供及价格费用边界核验.json']:
        r=json.loads((c.REVIEW/name).read_text());assert r['verified']
    assert cost_bounds_check()==json.loads((c.REVIEW/'转供及价格费用边界核验.json').read_text())
    result=dict(verified=True,schemes=len(sources),new_schemes=len(new),
        new_static_pairs=sum(r['checked_pairs'] for r in saved['records']),
        normal_station_hours=int((normal['小时数']*normal['站点数']).sum()),workbooks=verify_workbooks())
    c.prior.dump(c.REVIEW/'最终深化核验.json',result);print('VERIFIED_FOLLOWUP',result,flush=True)


if __name__=='__main__':main()
