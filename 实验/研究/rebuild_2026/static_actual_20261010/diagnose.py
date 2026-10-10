"""给全部候选免费可建的宽松条件，独立求无储能容量必要下界。"""
import itertools
import json
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow
from .run import OUT,load_scenes,network,actual_limits,write_csv,dump


def run():
    network.limits=actual_limits;detail=[];result=[]
    for region in ('city','pizhou'):
        inp=json.loads((OUT/region/'inputs.json').read_text());scenes=load_scenes(OUT/region,inp)
        ids=list(inp['stations']);built={e['id'] for e in inp['network']['edges']}
        rolling_upper=inp['initial_capacity_mva']
        for y,power in scenes.items():
            chosen=[]
            for j,sid in enumerate(ids):
                needs=[]
                for p in power:
                    for sign in (1,-1):
                        nn,arcs=network.network_arcs(inp,p,y,built)
                        arcs.extend((k,nn,10000.) if sign==1 else (nn,k,10000.) for k in range(len(ids)) if k!=j)
                        rr,cc,vv=zip(*arcs)
                        a=coo_matrix((np.ceil(np.array(vv)*network.SCALE).astype(np.int64),(rr,cc)),shape=(nn+1,nn+1)).tocsr()
                        transfer=(maximum_flow(a,j,nn) if sign==1 else maximum_flow(a,nn,j)).flow_value/network.SCALE
                        needs.append(max(0.,sign*p[j]-transfer))
                need=max(needs);s=inp['stations'][sid]
                ratings=[sorted({old,*[r for r in (31.5,50,63,80) if r>=old]}) for old in s['initial_units']]
                values=[a+b+t for a,b,t in itertools.product(*ratings,(0,50) if s['allow_third'] else (0,))
                        if a<=b and .95*(a+b+t-max(a,b,t))>=need-1e-5]
                c=min(values) if values else None;chosen.append(c)
                detail.append({'地区':inp['region_name'],'年份':y,'站点':sid,'必需剩余承载力_MW':need,'必要容量下界_MVA':c})
            total=sum(chosen) if all(v is not None for v in chosen) else None
            rolling_upper=max(rolling_upper,2*inp['annual_observed_peak_mw'][str(y)])
            # 该递推只作刚性规则必然满足的宽松上界；不是实际规划的可新增额度。
            result.append({'地区':inp['region_name'],'年份':y,'必要容量下界_MVA':total,
                           '含被动超限的宽松容量上界_MVA':rolling_upper,
                           '独立证明刚性无储能无解':total is None or total>rolling_upper+1e-5})
    write_csv(OUT/'无储能必要容量明细.csv',detail);write_csv(OUT/'无储能必要条件.csv',result)
    dump(OUT/'无储能必要条件.json',{'annual':result,'scope':'全部候选免费投运，放松邻站主变和备用间隔；仍保留馈线共享余量。必要容量之和只用于无解旁证，非实际配置。'})
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':run()
