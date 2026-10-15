"""所选方案及分时长矩阵的独立核验。"""
import argparse
import json
import math
from concurrent.futures import ProcessPoolExecutor,as_completed

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from scipy.sparse import coo_matrix

from ..review_20261015 import export as old_export,matrix as old_matrix
from ..review_20261015.target_warm import cost
from . import model as m


def matrix_endpoints():
    _,rows=old_export.collect_matrix(old_matrix.OUT/'transfer_grid_procurement.jsonl');groups={}
    for row in rows:
        if row['mode']!='greenfield' or not row['verified']:continue
        r=row['initial_transfer_fraction'];b=0 if r<=.3+1e-9 else 1 if r<=.5+1e-9 else 2 if r<=.7+1e-9 else 3
        key=tuple(row[k] for k in old_matrix.old.FIELDS if k!='initial_transfer_fraction')+(b,)
        groups.setdefault(key,[]).append(row)
    endpoints={}
    for group in groups.values():
        for row in [min(group,key=lambda r:r['clr']),max(group,key=lambda r:r['clr'])]:
            endpoints[tuple(row[k] for k in old_matrix.old.FIELDS)]=row
    return endpoints


def endpoint_check(row):
    p={k:row[k] for k in old_matrix.old.FIELDS};p['normal_reverse_limit_fraction']=.8
    r=old_matrix.independent_lp_check(p,row['units'],row['modules'],set(row['built']));assert r['verified'],(p,r)
    return dict(parameters=p,raw_line=row['raw_line'],**r)


def matrix_verify(full=False):
    chosen=matrix_endpoints();path=m.REVIEW/'分时长矩阵端点LP.json'
    source=old_matrix.OUT/'transfer_grid_procurement.jsonl'
    if full:
        proofs=[]
        with ProcessPoolExecutor(max_workers=8) as pool:
            futures=[pool.submit(endpoint_check,r) for r in chosen.values()]
            for i,f in enumerate(as_completed(futures),1):
                proofs.append(f.result())
                if i%100==0:print('VERIFIED_RECOMMEND_MATRIX',i,'/',len(chosen),flush=True)
        m.old.dump(path,dict(verified=True,source_sha256=m.old.sha(source),records=proofs))
    proof=json.loads(path.read_text());assert proof['verified'] and proof['source_sha256']==m.old.sha(source)
    assert {tuple(r['parameters'][k] for k in old_matrix.old.FIELDS) for r in proof['records']}==set(chosen)
    assert all(r['verified'] and r['max_violation_mw']<1e-5 for r in proof['records'])
    return len(chosen)


def workbook_verify():
    result=[]
    for filename in ['邳州逐年推荐方案.xlsx','五参数推荐矩阵与响应.xlsx']:
        book=load_workbook(m.PUBLIC/filename,read_only=True,data_only=True);cells=0
        for sheet in book:
            csv=m.PUBLIC/(sheet.title+'.csv')
            if not csv.exists():continue
            frame=pd.read_csv(csv,keep_default_na=False);values=list(sheet.values)
            assert list(values[0])==list(frame.columns) and len(values)==len(frame)+1
            for actual,expected in zip(values[1:],frame.itertuples(index=False,name=None)):
                for a,b in zip(actual,expected):
                    if a is None:a=''
                    try:aa,bb=float(a),float(b)
                    except (TypeError,ValueError):assert str(a)==str(b),(filename,sheet.title,a,b)
                    else:assert math.isclose(aa,bb,rel_tol=1e-10,abs_tol=1e-8),(filename,sheet.title,a,b)
                    cells+=1
        result.append(dict(file=filename,cells=cells,sha256=m.old.sha(m.PUBLIC/filename),verified=True));book.close()
    return result


def case_verify():
    proof=json.loads((m.REVIEW/'推荐方案独立核验.json').read_text());assert proof['verified']
    assert len(proof['sources'])==3
    summaries={};inp=json.loads((m.RAW/'邳州/inputs.json').read_text())
    for chosen in proof['sources']:
        folder=m.ROOT/chosen['folder'];assert m.old.sha(folder.parent/'inputs.json')==chosen['input_sha256']
        for name,key in [('chosen_solution.npz','solution_sha256'),('stations.csv','stations_sha256'),('projects.csv','projects_sha256'),('normal_fractions.json','normal_fractions_sha256')]:
            assert m.old.sha(folder/name)==chosen[key]
        summary=json.loads((folder/'summary.json').read_text());summaries[chosen['case']]=summary;states={};built_by_year={}
        selected={tuple(r) for r in json.loads((folder/'selected_pairs.json').read_text())}
        reference={r['year']:r for r in summary['reference_annual']} or None
        _,scenes,_=m.prepare();native,meta=m.build(inp,scenes,chosen['case'],selected,reference)
        solution=np.load(folder/'chosen_solution.npz')['solution']
        assert len(solution)==len(native.costs)
        ri,ci,data=zip(*native.entries)
        lhs=coo_matrix((data,(ri,ci)),shape=(len(native.constraint_lower),len(solution))).tocsr()@solution
        assert np.max(np.array(native.constraint_lower)-lhs)<1e-5 and np.max(lhs-np.array(native.constraint_upper))<1e-5
        assert np.max(np.array(native.lower_bounds)-solution)<1e-5 and np.max(solution-np.array(native.upper_bounds))<1e-5
        integers=solution[np.array(native.integrality,dtype=bool)];assert np.max(abs(integers-np.rint(integers)))<1e-5
        assert abs(np.dot(native.costs,solution)-summary['cost_npv_10k'])<1e-4
        expected_fractions={(r['year'],r['edge'],r['direction']):r['fraction'] for r in json.loads((folder/'normal_fractions.json').read_text())}
        for key,v in meta['normal_fractions'].items():assert abs(solution[v]-expected_fractions.get(key,0.))<1e-8
        previous=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);previous_n=np.zeros(len(previous));previous_built=set()
        for a in summary['annual']:
            y=a['year'];units,n,built=m.old.old.assets_from_csv(inp,folder,y)
            native_units,native_n,_,_=m.old.old.base.assets.assets(inp,solution,meta,y)
            native_built={eid for (eid,yy),v in meta['edgevars'].items() if yy==y and solution[v]>.5}
            assert np.allclose(native_units,units,atol=1e-8,rtol=0) and np.allclose(native_n,n,atol=1e-8,rtol=0) and native_built==built
            assert np.all(units>=previous-1e-8) and np.all(n>=previous_n) and built>=previous_built
            assert abs(units.sum()-a['capacity_mva'])<1e-7 and abs(units.sum()/a['peak_mw']-a['clr'])<1e-9
            if chosen['case']=='rigid':assert units.sum()<=max(previous.sum(),2*a['peak_mw'])+1e-7
            states[y]=(units,n);built_by_year[y]=built;previous,previous_n,previous_built=units,n,built
        recomputed=cost(inp,states,built_by_year);assert abs(recomputed-summary['cost_npv_10k'])<1e-4
        assert summary['solver']['dual_bound']<=recomputed+1e-4
        assert abs(max(0.,(recomputed-summary['solver']['dual_bound'])/recomputed)-summary['solver']['mip_gap'])<1e-9
    for a,b in zip(summaries['rigid']['annual'],summaries['elastic_selected']['annual']):
        assert b['capacity_mva']>=a['capacity_mva']*m.PREFERENCE['min_capacity_ratio']-1e-8
        assert b['storage_mwh']<=a['storage_mwh']*m.PREFERENCE['max_storage_ratio']+1e-8
        assert b['cumulative_lines']<=a['cumulative_lines']-(m.PREFERENCE['final_line_reduction'] if a['year']==2025 else 0)
    assert all(r['verified'] and r['max_violation_mw']<1e-5 for r in proof['normal_checks'])
    assert all(r['verified'] for r in proof['dispatch_records'])
    return dict(static_pairs=proof['static_pairs'],normal_station_hours=proof['normal_station_hours'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--matrix-lp',action='store_true');a=p.parse_args()
    count=matrix_verify(a.matrix_lp)
    cases=case_verify();books=workbook_verify();result=dict(verified=True,**cases,matrix_endpoint_count=count,workbooks=books)
    m.old.dump(m.REVIEW/'最终推荐核验.json',result);print('VERIFIED_RECOMMENDATION',result,flush=True)


if __name__=='__main__':main()
