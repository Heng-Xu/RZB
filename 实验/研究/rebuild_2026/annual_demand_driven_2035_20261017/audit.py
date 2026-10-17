"""以逐站加减源荷的另一条计算路径抽核关键年份，登记交付哈希。"""
import json
from pathlib import Path

import numpy as np

from . import model as m,prepare as p
from .verify import CASES


def run():
    proof=json.loads((p.REVIEW/'逐年方案独立核验.json').read_text());assert proof['verified']
    readback=json.loads((p.REVIEW/'工作簿回读.json').read_text());assert readback['verified']
    spots=[];maxerror=0.
    for region in p.REGIONS:
        inp,powers=p.load(region);ids=list(inp['stations']);aa=m.arcs(inp)
        for case in CASES:
            for y in (2022,2025,2030,2035):
                r=json.loads((p.RAW/region/case/str(y)/'adopted.json').read_text())
                u=np.array(r['units']);n=np.array(r['modules'])
                normal={int(k):v for k,v in r['normal'].items()};extra={int(k):v for k,v in r['extra'].items()}
                chosen={int(np.argmax(n)),int(np.argmax(u.sum(axis=1)))}
                for j in chosen:
                    worst=float('inf');worstfail=None
                    for failed in range(-1,len(ids)):
                        active=normal.copy()
                        if failed>=0:
                            for k,count in extra.items():
                                if aa[k]['sa']==failed:active[k]=active.get(k,0)+count
                        served=powers[y][:,j].copy()
                        for k,count in active.items():
                            a=aa[k];q=powers[y][:,a['sa']]*count/inp['block_count'][a['source']]
                            if a['sa']==j:served-=q
                            if a['sb']==j:served+=q
                        firm=.95*(u[j].sum()-(u[j].max() if failed==j else 0.))
                        forward=min(.1,.215*.76/max(1,inp['stations'][ids[j]]['forward_duration_h']))*n[j]
                        reverse=min(.1,.215*.76/max(1,inp['stations'][ids[j]]['reverse_duration_h']))*n[j]
                        margin=min(float(np.min(firm+forward-served)),float(np.min(firm*(1. if failed==j else .8)+reverse+served)))
                        if margin<worst:worst,worstfail=margin,failed
                        maxerror=max(maxerror,max(0.,-margin))
                        assert margin>=-1e-5,(region,case,y,ids[j],failed,margin)
                    spots.append(dict(地区=p.REGIONS[region],方案=case,年份=y,变电站=ids[j],
                        核对小时数=8760,核对工况数=len(ids)+1,最小余量_MW=worst,
                        最不利故障站='正常' if worstfail==-1 else ids[worstfail]))
    p.write_csv(p.REVIEW/'重点站逐时独立加减核对.csv',spots)
    code=Path(__file__).parent
    paths=[*code.glob('*.py'),code/'README.md',p.PUBLIC/'两地区逐年容量及措施_需求驱动左右对照.xlsx',
        p.PUBLIC/'逐年容量及措施_需求驱动左右对照.md',p.ROOT/'prompt.md',p.ROOT/'memory/current.md']
    paths.extend(p.RAW/region/name for region in p.REGIONS for name in ('inputs.json','hourly.npz','base_components.npz'))
    formal=[p.ROOT/'研究报告/01研究推荐/当前版/报告数据采用版本.json',p.ROOT/'研究报告/04_word/研究报告终稿.docx',p.ROOT/'研究报告/04_word/研究报告终稿.pdf']
    paths.extend(v for v in formal if v.exists())
    p.dump(p.REVIEW/'交付核验.json',dict(verified=True,confidence='附适用条件可用于研究比较',
        full_hour_pairs=proof['full_hour_pairs'],spot_station_years=len(spots),max_spot_error_mw=maxerror,
        workbook_cells=readback['cells'],max_matrix_error=proof['max_matrix_error'],max_cost_error_10k=proof['max_cost_error_10k'],
        files={str(v.relative_to(p.ROOT)):p.sha(v) for v in paths},
        caveats=['2021邳州固定设备事故缺口保留，规划补强年度从2022计',
            '2025收资能力用于早期回算，EQ路径与组数为研究代理，逐线拓扑及投运年份仍有资料缺口',
            '储能采用静态持续时长，未求解连续SOC；年度条件下界不可相加当作全期最优下界'],
        formal_report='本轮仅新增独立逐年方案与对照表；既有报告源稿、原生Word及WPS PDF三阶段复核通过，未替换冻结案例'))
    print('AUDIT_DEMAND',len(spots),maxerror,flush=True)


if __name__=='__main__':run()
