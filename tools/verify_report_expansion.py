"""独立核对九张电缆分区矩阵、响应示例及图件来源。"""
from pathlib import Path
import hashlib
import itertools
import json
import math
import re
import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT/'研究报告/05_review/当前版/1016矩阵分区与文献补充'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify():
    asset = ROOT/'研究报告/02图表/当前版'
    source = ROOT/'研究报告/01研究推荐/当前版/参数联合情景_20261012/统一有效样本.csv'
    data = pd.read_csv(source)
    tables = json.loads((asset/'计算表.json').read_text())
    cuts = [(-math.inf,.02),(.02,.04),(.04,.07),(.07,math.inf)]
    eta = [(-math.inf,1),(1,2),(2,math.inf)]
    transfer = [(-math.inf,.3),(.3,.5),(.5,.7),(.7,math.inf)]
    records = []
    cables=[(-math.inf,.1),(.1,.3),(.3,math.inf)]
    for ci,kd in itertools.product(range(3),[1.,1.1,1.15]):
        key=f'lookup_matrix_{ci}_{kd:.2f}'
        rows=[[x.strip() for x in line.strip('|').split('|')]
              for line in tables[key].splitlines() if line.startswith('|')][2:]
        assert len(rows)==12 and all(len(row)==6 for row in rows)
        for gi,ei,ri in itertools.product(range(4),range(3),range(4)):
            mask=np.isclose(data['负荷分散系数'],kd)
            mask&=(data['电缆长度占比']>cables[ci][0]+1e-9)&(data['电缆长度占比']<=cables[ci][1]+1e-9)
            for field,(lo,hi) in zip(['年最大净负荷平均增长率','分布式电源装机渗透率','初始转供率'],
                                    [cuts[gi],eta[ei],transfer[ri]]):
                mask &= (data[field]>lo+1e-9)&(data[field]<=hi+1e-9)
            sample=data[mask];assert len(sample)
            lo=float(sample['容载比'].min());hi=float(sample['容载比'].max())
            shown=f'{math.floor((lo+1e-10)*100)/100:.2f}～{math.ceil((hi-1e-10)*100)/100:.2f}'
            assert rows[gi*3+ei][ri+2]==shown,(key,gi,ei,ri)
            records.append(dict(表键=key,电缆档=ci,增长档=gi,装机档=ei,转供档=ri,有效节点=len(sample),
                                电缆节点=sorted(sample['电缆长度占比'].unique().tolist()),
                                支撑时长=sorted(sample['储能支撑持续时间_h'].unique().tolist()),
                                容载比下界=lo,容载比上界=hi,展示区间=shown))
    assert len(records)==432 and sum(r['有效节点'] for r in records)==len(data)==32112
    # 直接按指定列过滤两个完整序列，独立核对高于2且逐档响应的示例。
    sequence_records=[]
    for key,driver,fixed,expected in [
        ('current_cable_sequence','电缆长度占比',{'分布式电源装机渗透率':2.75,'年最大净负荷平均增长率':.055,
          '初始转供率':.6,'储能支撑持续时间_h':2,'负荷分散系数':1.15},[710,760,760,820,820]),
        ('current_diversity_sequence','负荷分散系数',{'分布式电源装机渗透率':2.5,'年最大净负荷平均增长率':.07,
          '电缆长度占比':.1,'初始转供率':.5,'储能支撑持续时间_h':4},[710,786,820])]:
        mask=np.ones(len(data),dtype=bool)
        for name,value in fixed.items():mask&=np.isclose(data[name],value)
        frame=data[mask].sort_values(driver)
        assert frame[driver].tolist()==sorted(data[driver].unique().tolist())
        assert frame['主变容量_MVA'].tolist()==expected
        assert frame['容载比'].min()>2 and frame['容载比'].round(2).nunique()==3
        sequence_records.append(dict(表键=key,固定条件=fixed,节点=frame.to_dict('records')))
    figures=json.loads((AUDIT/'新增图件来源与图形选择.json').read_text())
    assert len(figures)==27
    for figure in figures:
        key=figure['图键'];png=asset/(key+'.png')
        assert sha(png)==figure['图件SHA256'],'图件已变化：'+key
        for path,digest in figure['原始依据'].items():
            original=ROOT/path
            if sha(original)!=digest:
                inheritance=ROOT/'研究报告/05_review/当前版/1017细节表述修正/图件来源承继.json'
                record=json.loads(inheritance.read_text())[path]
                assert record['原SHA256']==digest and record['复核结论']=='图形及计算关系保持'
                original=ROOT/record['原件归档']
            assert sha(original)==digest,'绘图来源已变化：'+path
        values=ROOT/figure['绘图数据'];assert len(pd.read_csv(values))>0
        for suffix in ['.pdf','.svg']:
            assert values.with_suffix(suffix).is_file()
        with Image.open(png) as image:
            assert image.width>=2300 and image.height>=1600,'图件分辨率不足：'+key
    source_text='\n'.join(p.read_text() for p in (ROOT/'研究报告/03_MD/当前版').glob('0[1-6] *.md'))
    for figure in figures:assert '[[FIG:'+figure['图键']+'|' in source_text
    result=dict(状态='通过',完整区间矩阵=9,矩阵单元=len(records),归纳有效节点=len(data),
                电缆条件='按≤10%、(10%,30%]、>30%分区，三个负荷分散系数分别列示',
                时长集合选择='2/4/6 h全部有效节点纳入各自分区，完整覆盖容量范围；只在核验资料登记',
                扩充图件=len(figures)-1,重绘技术路线=1,矩阵原始库SHA256=sha(source),单元=records,响应示例=sequence_records)
    (AUDIT/'矩阵与图件独立核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return {k:v for k,v in result.items() if k not in ['单元','响应示例']}


if __name__=='__main__':
    print(json.dumps(verify(),ensure_ascii=False))
