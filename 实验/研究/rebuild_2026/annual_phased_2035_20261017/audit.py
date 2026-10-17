"""首年跳增、完整建设序列和分期代价逐项核对。"""
import json

import numpy as np

from . import prepare as p


def run():
    rows=[];metrics=[]
    for region,name in p.REGIONS.items():
        inp,_=p.load(region)
        for case in ('rigid','elastic_capacity'):
            original=p.parent.RAW/region/case/'summary.json';current=p.RAW/region/case/'summary.json'
            old=json.loads(original.read_text());new=json.loads(current.read_text())
            previous=inp['initial_capacity_mva']
            for a,b in zip(old['annual'],new['annual']):
                y=b['year'];rate=0. if y==2021 else b['net_capacity_increment_mva']/previous
                rows.append(dict(地区=name,方案=case,年份=y,原方案容量_MVA=a['capacity_mva'],分期容量_MVA=b['capacity_mva'],
                    原净增_MVA=a['net_capacity_increment_mva'],分期净增_MVA=b['net_capacity_increment_mva'],
                    分期净增率=rate,分期累计费用现值_万元=b['cumulative_lifecycle_npv_10k']))
                if y>2021:assert rate<=.05+1e-8
                previous=b['capacity_mva']
            assert old['annual'][-1]['capacity_mva']==new['annual'][-1]['capacity_mva']
            final=json.loads((p.RAW/region/case/'2035/adopted.json').read_text())
            np.testing.assert_array_equal(np.array(final['units']),np.array(inp['terminal_transformer_portfolios'][case]))
            metrics.append(dict(region=region,case=case,first_year_old_mva=old['annual'][1]['net_capacity_increment_mva'],
                first_year_new_mva=new['annual'][1]['net_capacity_increment_mva'],
                construction_years_old=sum(a['net_capacity_increment_mva']>1e-6 for a in old['annual'][1:]),
                construction_years_new=sum(a['net_capacity_increment_mva']>1e-6 for a in new['annual'][1:]),
                positive_future_years=sum(a['net_capacity_increment_mva']>1e-6 for a in new['annual'] if a['year']>=2026),
                terminal_capacity_mva=new['annual'][-1]['capacity_mva'],terminal_portfolio_retained=True,
                old_cost_npv_10k=old['cost_npv_10k'],new_cost_npv_10k=new['cost_npv_10k'],
                cost_change_npv_10k=new['cost_npv_10k']-old['cost_npv_10k'],cost_change_rate=new['cost_npv_10k']/old['cost_npv_10k']-1,
                old_summary_sha256=p.sha(original),new_summary_sha256=p.sha(current)))
    p.write_csv(p.SOURCE/'分期建设完整序列.csv',rows)
    proof_path=p.REVIEW/'逐年方案独立核验.json'
    proof=json.loads(proof_path.read_text());assert proof['verified']
    proof.update(artifact_kind='annual_phased_construction_planning',
        construction_scope='固定各自2035逐站主变工程清单，优化年度投运安排及配套；年度建设上限5%、累计进度余量50MVA，终年逐站匹配',
        construction_check_sha256=p.sha(p.REVIEW/'逐年建设进度核对.csv'))
    p.dump(proof_path,proof)
    p.dump(p.REVIEW/'分期效果与费用核对.json',dict(verified=True,metrics=metrics,
        method='固定各自已认可2035主变清单，按负荷趋势排程；每年重新求解配套和固定事故预案并校核，未对输出容量作插值',
        retained='2021实际总容量、原逐小时负荷与光伏、共同容载比下限、费用参数、站级20%转供限额',
        assumptions='年度净增上限5%，累计进度容许50MVA整台工程余量；均为本轮建设排程研究假设',
        caveat='条件建设排程的逐年可行候选，非全部投资规模自由选择的全期联合最优；早期储能与联络按原规则逐年保留，分期代价须计入'))
    print('AUDITED_PHASED_SEQUENCE',len(rows),flush=True)


if __name__=='__main__':run()
