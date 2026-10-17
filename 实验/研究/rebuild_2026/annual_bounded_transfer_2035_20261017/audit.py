"""保留转供机制诊断和本轮校准的直接依据。"""
import json

from . import prepare as p, model as m


def run():
    rows=[]
    for region,name in p.REGIONS.items():
        inp,_=p.parent.load(region);aa=m.arcs(inp)
        for y in range(2022,2036):
            raw=p.parent.RAW/region/'elastic_reserve'/str(y)/'adopted.json';r=json.loads(raw.read_text())
            for sid in inp['stations']:
                normal=sum(c for k,c in r['normal'].items() if aa[int(k)]['source']==sid)
                extra=sum(c for k,c in r['extra'].items() if aa[int(k)]['source']==sid)
                rows.append(dict(地区=name,年份=y,变电站=sid,正常转出比例=normal/inp['block_count'][sid],
                    事故追加转出比例=extra/inp['block_count'][sid],合计比例=(normal+extra)/inp['block_count'][sid],
                    原始解路径=str(raw.relative_to(p.ROOT)),原始解SHA256=p.sha(raw)))
    p.write_csv(p.SOURCE/'上一版逐年站级转供占比.csv',rows)
    candidates=[]
    for region in p.REGIONS:
        for case in ('elastic_capacity_auxcost','elastic_capacity_aux5','elastic_capacity_aux20_unreconciled','elastic_capacity'):
            path=p.RAW/region/case/'summary.json'
            if not path.exists():continue
            summary=json.loads(path.read_text());r=summary['annual'][-1]
            candidates.append(dict(region=region,case=case,adopted=case=='elastic_capacity',
                objective_reconciliation='已将储能与联络费用逐项对账' if case=='elastic_capacity' else '辅助目标漏计联络费用，独立对账未通过，未采用',
                capacity_mva=r['capacity_mva'],storage_mwh=r['storage_mwh'],
                lines=r['cumulative_lines'],cost_npv_10k=summary['cost_npv_10k'],summary_sha256=p.sha(path)))
    p.dump(p.SOURCE/'约束与优选校准记录.json',dict(target='用户要求偏向主变增容，弹性较刚性采用更高容量、更少储能和联络；保留真实年度例外',
        diagnosis='上一版既有与新增未共用站级总限额，正常永久跨站卸载与事故追加合计可达到约65%—68%；短期定容加全期单次采购限制后期增容。',
        physical='正常转供归零，既有与新增事故转供合计不超过本站20%区段，采购选型参考2035；刚弹共同适用。',
        selection='先试配套优选和5%/20%容差时，独立对账发现辅助目标漏计了在new_projects变量计价的联络费用，未采用这些候选；修复为按路径逐项计价并加入回归检查后，重算20%配套容差的采用候选。该20%与转供20%为两个独立研究设定，均非规范强制限值。',
        caveat='目标导向的工程情景，不能将期望排序解释成放宽容载比上限的普遍定理；不得以改写数字取得排序。',
        candidates=candidates))
    print('AUDITED_PREVIOUS_TRANSFER',len(rows),flush=True)


if __name__=='__main__':run()
