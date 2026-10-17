"""回到设备原表及工程投资原表，核对第三台候选资料边界。"""
from collections import Counter

from openpyxl import load_workbook

from ..cost_references import read_cost_references, SOURCE as COST_SOURCE
from ..station_grid_feasibility import ASSETS
from . import prepare as p


def run():
    wb = load_workbook(ASSETS,read_only=True,data_only=True)
    raw = list(wb['110千伏变电站1'].values)
    wb.close()
    rows = []
    for region,name in p.REGIONS.items():
        inp,_ = p.load(region)
        for sid,s in inp['stations'].items():
            md = s['metadata']
            number = md['asset_source_row']
            if number=='':
                assert not s['allow_third']
                continue
            r = raw[number-1]
            assert r[3]==sid and int(r[10] or 0)==md['available_third_slots']
            assert float(r[11] or 0)==md['available_third_mva']
            rows.append(dict(地区=name,变电站=sid,原表行号=number,可扩建台数=int(r[10] or 0),
                可扩建容量_MVA=float(r[11] or 0),本模型允许第三台=s['allow_third']))
    refs = [r for r in read_cost_references() if r['voltage_kv']==110 and r['measure_type']=='third_transformer_expansion']
    assert len(refs)==2 and all(r['purchased_transformer_mva']==50 for r in refs)
    for region in p.REGIONS:
        inp,_ = p.load(region)
        assert abs(sum(r['static_total_10k_cny'] for r in refs)/len(refs)-inp['third_50mva_capex_10k'])<1e-9
    p.write_csv(p.SOURCE/'第三台扩建余量原表核对.csv',rows)
    p.write_csv(p.SOURCE/'第三台扩建造价原表摘录.csv',refs)
    p.dump(p.SOURCE/'第三台扩建证据.json',dict(verified=True,source=str(ASSETS.relative_to(p.ROOT)),sha256=p.sha(ASSETS),
        cost_source=str(COST_SOURCE.relative_to(p.ROOT)),cost_source_sha256=p.sha(COST_SOURCE),rows=len(rows),
        capacity_counts={str(k):v for k,v in Counter(r['可扩建容量_MVA'] for r in rows).items()},
        higher_capacity_stations=[r for r in rows if r['可扩建容量_MVA']>50],
        conclusion='9座站有超过50MVA的预留扩建容量；可计价工程实例只对应50MVA第三台。本轮保留50MVA候选；扩大规格的造价仍有资料缺口，未认定原表无更大扩建空间。'))
    print('SOURCE_ASSETS',len(rows),'stations,',sum(r['可扩建容量_MVA']>50 for r in rows),'above50',flush=True)


if __name__=='__main__':
    run()
