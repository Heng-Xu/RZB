"""清理后只读验证：冻结输入重建、原始统计、解向量、矩阵及独立网络证据。"""
import json
import tempfile
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix

from . import run as current
from .no_storage_analysis import DEST, VARIANTS
from ..official_annual import read_official_annual, DEFAULT_SOURCE


def verify():
    out=current.OUT;checks=[];manifest={}
    for r in ('city','pizhou'):
        for name in ('inputs.json','静态工况.csv','候选联络.csv'):
            manifest[r,name]=current.sha(out/r/name)
    with tempfile.TemporaryDirectory(prefix='rzb-static-input-check-') as tmp:
        try:
            current.OUT=Path(tmp);current.prepare()
            for (r,name),digest in manifest.items():assert current.sha(Path(tmp)/r/name)==digest,(r,name)
        finally:current.OUT=out
    actual={(r['region_id'],r['year']):r for r in read_official_annual(DEFAULT_SOURCE) if r['voltage_kv']==110}
    current.network.limits=current.actual_limits
    for region in ('city','pizhou'):
        root=out/region;inp=json.loads((root/'inputs.json').read_text());scenes=current.load_scenes(root,inp)
        for case in current.CASES:
            directory=root/case;s=json.loads((directory/'summary.json').read_text())
            if 'annual' not in s:
                assert s['solver']['proven_infeasible'];continue
            assert s['input_sha256']==current.sha(root/'inputs.json')
            chosen=directory/'chosen_solution.npz'
            z=np.load(chosen)['solution']
            m,meta=current.build(inp,scenes,case)
            rr,cc,vv=zip(*m.entries);a=coo_matrix((vv,(rr,cc)),shape=(len(m.constraint_lower),len(m.costs))).tocsr()
            az=a@z;ints=np.array(m.integrality,dtype=bool)
            violation=max(0.,float(np.max(np.asarray(m.constraint_lower)-az)),float(np.max(az-np.asarray(m.constraint_upper))),
                          float(np.max(np.asarray(m.lower_bounds)-z)),float(np.max(z-np.asarray(m.upper_bounds))),
                          float(np.max(np.abs(z[ints]-np.round(z[ints])))))
            assert violation<1e-5,(region,case,violation)
            error=abs(np.dot(m.costs,z)-s['cost_npv_10k']);assert error<.02
            for y in inp['years']:
                assets=current.assets_model.assets(inp,z,meta,y)
                built={e for (e,yy),v in meta['edgevars'].items() if yy==y and z[v]>.5}
                c,v=current.network.check_year(inp,scenes[y],y,assets[0],assets[1],built);assert not v
                row=next(r for r in s['annual'] if r['year']==y)
                assert row['peak_mw']==actual[inp['region_id'],y]['reported_downward_load_mw']
                assert abs(row['capacity_mva']-assets[0].sum())<1e-5
                assert abs(row['clr']-row['capacity_mva']/row['peak_mw'])<1e-9
            checks.append({'region':region,'case':case,'matrix_violation':violation,'objective_error_10k':error})
        for variant in VARIANTS:
            s=json.loads((DEST/region/variant/'summary.json').read_text());assert s['solver']['proven_infeasible']
            for path,digest in s['sources'].items():assert current.sha(current.ROOT/path)==digest
    p=current.ROOT/'研究报告/试算/归档记录_20261010/活动文件哈希.json'
    if p.exists():
        for path,digest in json.loads(p.read_text()).items():assert current.sha(current.ROOT/path)==digest,path
    result={'frozen_input_rebuild_identical':True,'solutions_checked':checks,'no_storage_infeasible_variants_checked':6,
            'original_annual_statistics_checked':True,'manifest_checked':p.exists()}
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':verify()
