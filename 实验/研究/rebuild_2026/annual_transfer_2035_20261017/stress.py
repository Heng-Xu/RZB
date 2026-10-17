"""2035固定设备与固定预案的源荷+5%承载压力检查；不重算投资。"""
import json

import numpy as np

from . import model as m, prepare as p
from .verify import CASES


def run():
    results=[]
    for region,name in p.REGIONS.items():
        inp,powers=p.load(region);data=np.load(p.RAW/region/'base_components.npz')
        prediction=p.forecasts(region)[-1];demand=data['demand_proxy']*prediction['load_factor']
        pv=data['generation_proxy']*prediction['pv_factor'];ids=list(inp['stations']);aa=m.arcs(inp)
        for case in CASES:
            r=json.loads((p.RAW/region/case/'2035/adopted.json').read_text())
            units=np.array(r['units']);n=np.array(r['modules'])
            bp=np.array([min(.1,.215*.76/max(1,s['forward_duration_h'])) for s in inp['stations'].values()])*n
            bn=np.array([min(.1,.215*.76/max(1,s['reverse_duration_h'])) for s in inp['stations'].values()])*n
            for label,loadfactor,pvfactor in [('原预测',1.,1.),('负荷增加5%',1.05,1.),('光伏增加5%',1.,1.05)]:
                power=demand*loadfactor-pv*pvfactor;worst=0.;bad=0;worststation='';worstf=''
                for f in range(-1,len(ids)):
                    T=np.eye(len(ids))
                    for field in ('normal','extra'):
                        for key,count in r[field].items():
                            a=aa[int(key)]
                            if field=='extra' and a['sa']!=f:continue
                            fraction=count/inp['block_count'][a['source']]
                            T[a['sa'],a['sa']]-=fraction;T[a['sa'],a['sb']]+=fraction
                    served=power@T;cap=.95*units.sum(axis=1)
                    if f>=0:cap[f]-=.95*units[f].max()
                    reverse=.8*cap
                    if f>=0:reverse[f]=cap[f]
                    gap=np.maximum(served-cap-bp,-served-reverse-bn)
                    h,j=np.unravel_index(np.argmax(gap),gap.shape)
                    if gap[h,j]>worst:worst=float(gap[h,j]);worststation=ids[j];worstf=ids[f] if f>=0 else '正常'
                    bad+=int(np.any(gap>1e-5,axis=1).sum())
                results.append(dict(地区=name,方案=case,年份=2035,压力条件=label,主变与储能最大约束缺口_MW=worst,
                    承载约束失败小时工况数=bad,最差站=worststation,最差故障=worstf,
                    范围='固定设备与预案的主变/储能承载约束压力测试，不重新投资，不替代路径全约束核验'))
    p.write_csv(p.REVIEW/'2035源荷增长敏感性.csv',results)
    p.dump(p.REVIEW/'敏感性口径.json',dict(verified=True,rows=12,assumption='5%是确定性压力幅度，不是置信区间',
        scope='仅变更预测源荷分量并重建转移后承载约束；没有声称压力工况满足全部路径及分段设计约束'))
    return results


if __name__=='__main__':run()
