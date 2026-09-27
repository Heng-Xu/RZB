"""比较隔离重求的区域结果及共同起点；保留原逐站等价分配。"""
from pathlib import Path
import argparse,csv,json,math,sys

ROOT=Path(__file__).resolve().parents[3]
ORIGINAL=ROOT/'实验/研究/rebuild_2026/source_audit/capacity_release_simulation/reserve_policy_v4'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reproduced',required=True)
    parser.add_argument('--output',help='可选对账JSON；不填写时只输出到终端')
    args=parser.parse_args();folder=Path(args.reproduced);errors=[];count=0;additional={}
    names=['summary.csv','annual_matrix.csv','baseline_layers.csv','baseline_stations.csv']
    names += sorted(p.name for p in ORIGINAL.glob('*_years.csv'))
    names += sorted(p.name for p in ORIGINAL.glob('*_ties.csv'))
    for name in names:
        if not (folder/name).is_file():errors.append('缺文件：'+name);continue
        a,b=read(ORIGINAL/name),read(folder/name)
        if len(a)!=len(b):errors.append('行数：'+name);continue
        for row,(old,new) in enumerate(zip(a,b),2):
            if old.keys()-new.keys():errors.append('缺原字段：'+name);continue
            if new.keys()-old.keys():additional[name]=sorted(new.keys()-old.keys())
            for field,value in old.items():
                count+=1
                try:ok=math.isclose(float(value),float(new[field]),rel_tol=1e-8,abs_tol=1e-5)
                except (ValueError,TypeError):ok=value==new[field]
                if not ok:errors.append(f'{name}:行{row}:{field}')
    layouts=[p.name for p in ORIGINAL.glob('*_stations.csv') if p.name!='baseline_stations.csv' and (folder/p.name).is_file() and p.read_bytes()!=(folder/p.name).read_bytes()]
    result={'status':'FAIL' if errors else 'PASS','checks':count,'errors':errors,'reproduced_directory':str(folder.resolve()),'compared_files':names,'additional_reproduced_fields':additional,'station_layout_differences':layouts,'rule':'原字段逐项对账，附加求解诊断仅登记；共同起点、区域年度指标及费用按1e-5绝对容差、1e-8相对容差对账；不以不同逐站分配覆盖原版'}
    if args.output:Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False));return bool(errors)
if __name__=='__main__':sys.exit(main())
