"""输出可按表中数字复算的首末年重点站点。"""
import json

import numpy as np

from . import model as m, prepare as p


def run():
    out=[]
    for region,name in p.REGIONS.items():
        inp,powers=p.load(region);aa=m.arcs(inp);ids=list(inp['stations'])
        for case in ('rigid','elastic_capacity'):
            for y in (2022,2035):
                source=p.RAW/region/case/str(y)/'adopted.json';r=json.loads(source.read_text())
                u=np.array(r['units']);n=np.array(r['modules']);scores=[]
                for j,sid in enumerate(ids):
                    fraction=sum(c for k,c in r['extra'].items() if aa[int(k)]['source']==sid)/inp['block_count'][sid]
                    for sign,key in ((1,'forward_duration_h'),(-1,'reverse_duration_h')):
                        h=int(np.argmax(sign*powers[y][:,j]));need=max(0.,float(sign*powers[y][h,j]))*(1-fraction)
                        firm=.95*(u[j].sum()-u[j].max());b=min(.1,.215*.76/max(1,inp['stations'][sid][key]))*n[j]
                        scores.append(dict(地区=name,方案=case,年份=y,站名=sid,方向='正向' if sign==1 else '反向',小时序号=h,
                            主变总容量_MVA=float(u[j].sum()),最大主变_MVA=float(u[j].max()),N1剩余主变有效容量_MW=firm,
                            转供区段比例=fraction,本站保留源荷需求_MW=need,储能额定功率_MW=float(n[j]*.1),
                            储能有效支撑_MW=b,复算余量_MW=firm+b-need,原始解SHA256=p.sha(source)))
                for direction in ('正向','反向'):
                    q=min((v for v in scores if v['方向']==direction),key=lambda v:v['复算余量_MW'])
                    assert q['复算余量_MW']>=-1e-5;out.append(q)
    p.write_csv(p.REVIEW/'重点站点抽样复算.csv',out)
    print('CHECKED_ENGINEERING_SAMPLES',len(out),flush=True)


if __name__=='__main__':run()
