"""固定场景后只改变容载比上限；核对2.60研究边界的含义。"""
from pathlib import Path
import importlib.util,json
from 驱动因子分析 import table
HERE=Path(__file__).parent;R=HERE.parents[1];A=R/'02图表/当前版'
spec=importlib.util.spec_from_file_location('static_external',HERE/'通用参数外推.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
    records=[];display=[]
    for lt in ('架空为主','电缆为主'):
        for eta,g,h,area in [(.3,.02,3,'A'),(1.8,.08,4,'BC'),(3.,0.,6,'BC'),(3.,.08,6,'A')]:
            results=[m.solve(eta,g,h,area,1.,1.,'偏集中',lt,upper=cap,relative_gap=1e-8) for cap in (2.4,2.6,2.8)]
            costs=[r['全寿命费用万元'] for r in results]
            assert costs[0]+1e-3>=costs[1] and costs[1]+1e-3>=costs[2]
            records.append({'线路类型':lt,'源荷比':eta,'增长率':g,'峰段h':h,'类别':area,'上限':[2.4,2.6,2.8],'结果':results,'扩大至2.80费用降幅':1-costs[2]/costs[1]})
            display.append([lt,f'{eta:.2f}/{g*100:.2f}%/{h:.2f}',*[f"{r['推荐容载比']:.2f}/{r['全寿命费用万元']:.2f}" for r in results]])
    tables=json.loads((A/'计算表.json').read_text());tables['upper_bound_sensitivity']=table('表5-0 三种容载比上限的条件比较（结果为容载比/费用万元）',['线路类型','源荷比/增长率/峰段h','上限2.40','上限2.60','上限2.80'],display)
    (A/'计算表.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2));(HERE/'1003反馈修订/容载比上限比较.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    print(json.dumps([{'场景':[r['线路类型'],r['源荷比'],r['增长率'],r['峰段h']],'2.80相对2.60降幅':r['扩大至2.80费用降幅']} for r in records],ensure_ascii=False))
if __name__=='__main__':main()
