"""以真实中位节点定位窗口，在相邻容量水平接近时共用界值。"""
from decimal import Decimal, ROUND_HALF_UP
import math
import json

import numpy as np
import pandas as pd

GROWTH = ['≤2%', '(2%,4%]', '(4%,7%]', '>7%']
ETA = ['≤1', '(1,2]', '>2']
TRANSFER = ['≤30%', '(30%,50%]', '(50%,70%]', '>70%']
CABLE = ['≤10%', '(10%,30%]', '>30%']
DIVERSITY_LABELS = ['≤1.15', '>1.15']
WIDTH = Decimal('.10')
STEP = Decimal('.02')
DIVERSITY_CONTROLS = {'分布式电源装机渗透率':2., '年最大净负荷平均增长率':.04,
                      '电缆长度占比':.1, '初始转供率':.4, '储能支撑持续时间_h':4}


def adjoining_windows(values):
    """基准宽0.10；接近的代表水平以中点接续，不跨越较大容量间隔。"""
    values = [Decimal(str(v)) for v in values]
    centers = [(v/STEP).quantize(Decimal('1'), rounding=ROUND_HALF_UP)*STEP for v in values]
    levels = sorted(set(centers))
    result=[]
    for value, center in zip(values, centers):
        i=levels.index(center)
        low, high=center-WIDTH/2, center+WIDTH/2
        if i: low=max(low,(levels[i-1]+center)/2)
        if i+1<len(levels): high=min(high,(center+levels[i+1])/2)
        assert low <= value <= high, '局部缩窄后仍须包含真实代表节点'
        result.append(f'{low:.2f}～{high:.2f}')
    return result


def window(value, width=WIDTH, step=STEP):
    """同一代表值给出同一窗口；不按转供档或显示次序添加偏移。"""
    value, width, step = Decimal(str(value)), Decimal(str(width)), Decimal(str(step))
    assert width > 0 and step > 0
    center = (value/step).quantize(Decimal('1'), rounding=ROUND_HALF_UP)*step
    low, high = center-width/2, center+width/2
    assert low <= value <= high, '窗口须包含定位代表值'
    return f'{low:.2f}～{high:.2f}'


def middle_node(values):
    """最接近中位数的观测值；偶数样本中间两点同距时取较大值。"""
    ordered=np.sort(np.asarray(values,dtype=float))
    assert len(ordered)
    return float(ordered[len(ordered)//2])


def records(data):
    """保留全部端点与窗口内节点数，窗口不充当全体样本包络。"""
    d = data.copy()
    fields = ['年最大净负荷平均增长率', '分布式电源装机渗透率',
              '初始转供率', '电缆长度占比']
    for field, cuts in zip(fields, [[.02,.04,.07], [1,2], [.3,.5,.7], [.1,.3]]):
        d['bin_'+field] = d[field].map(lambda v: sum(v > x+1e-9 for x in cuts))
    assert set(np.round(d['负荷分散系数'], 2)) == {round(1.05+i*.02,2) for i in range(11)}
    result = []
    for cable in range(3):
        for kd_bin, kd_label in enumerate(DIVERSITY_LABELS):
            frame = d[(d['bin_电缆长度占比'] == cable) &
                      ((d['负荷分散系数'] <= 1.15+1e-9) if kd_bin == 0
                       else (d['负荷分散系数'] > 1.15+1e-9))]
            for growth in range(4):
                for eta in range(3):
                    for transfer in range(4):
                        sub = frame[(frame['bin_'+fields[0]] == growth) &
                                    (frame['bin_'+fields[1]] == eta) &
                                    (frame['bin_'+fields[2]] == transfer)]
                        assert len(sub), (cable, kd_bin, growth, eta, transfer, '无有效节点不得补造窗口')
                        median = float(sub['容载比'].median())
                        representative = sub.sort_values('容载比',kind='stable').iloc[len(sub)//2]
                        band = window(float(representative['容载比']))
                        low, high = map(float, band.split('～'))
                        result.append(dict(表键=f'lookup_matrix_{cable}_{"low" if kd_bin == 0 else "high"}',
                            电缆档=cable, 电缆区间=CABLE[cable], 分散档=kd_bin,
                            负荷分散系数区间=kd_label, 增长档=growth, 装机档=eta, 转供档=transfer,
                            有效样本数=len(sub), 分散节点数=sub['负荷分散系数'].nunique(),
                            下界=float(sub['容载比'].min()), 上界=float(sub['容载比'].max()),
                            中位数=median, 代表节点容载比=float(representative['容载比']),
                            代表节点={f:float(representative[f]) for f in fields+['负荷分散系数','储能支撑持续时间_h']},
                            推荐窗口=band, 窗口内节点数=int(sub['容载比'].between(low-1e-9,high+1e-9).sum()),
                            窗口宽度=float(WIDTH), 滑动步长=float(STEP)))
    # 同一行四个转供档共同确定接续边界，保留真实平台及局部回升。
    for start in range(0,len(result),4):
        row=result[start:start+4]
        for item,band in zip(row,adjoining_windows([r['代表节点容载比'] for r in row])):
            low,high=map(float,band.split('～'))
            item.update(推荐窗口=band,窗口宽度=round(high-low,2),基准窗口宽度=float(WIDTH))
            mask=np.ones(len(data),dtype=bool)
            for field,idx in zip(fields,[item['增长档'],item['装机档'],item['转供档'],item['电缆档']]):
                mask &= d['bin_'+field].eq(idx)
            mask &= data['负荷分散系数'].le(1.15+1e-9) if item['分散档']==0 else data['负荷分散系数'].gt(1.15+1e-9)
            item['窗口内节点数']=int(data.loc[mask,'容载比'].between(low-1e-9,high+1e-9).sum())
    assert len(result) == 288
    assert sum(r['有效样本数'] for r in result) == len(data)
    return result


def assets(data, table):
    cells = records(data)
    tables, index = {}, []
    for cable in range(3):
        for kd_bin, kd_label in enumerate(DIVERSITY_LABELS):
            key = f'lookup_matrix_{cable}_{"low" if kd_bin == 0 else "high"}'
            subset = [r for r in cells if r['表键'] == key]
            rows = []
            for growth in range(4):
                for eta in range(3):
                    row = sorted([r for r in subset if r['增长档'] == growth and r['装机档'] == eta], key=lambda r:r['转供档'])
                    assert len(row) == 4
                    rows.append([GROWTH[growth], ETA[eta]]+[r['推荐窗口'] for r in row])
            tables[key] = table(f'表5-0 电缆长度占比{CABLE[cable]}、负荷分散系数{kd_label}的容载比分档建议矩阵',
                               ['年最大净负荷平均增长率', '装机渗透率']+TRANSFER, rows)
            index.append(dict(表键=key, 电缆档=cable, 电缆区间=CABLE[cable],
                              负荷分散系数区间=kd_label, 有效样本数=sum(r['有效样本数'] for r in subset), 区间单元=48))
    sections = dict(new_matrix_tables='\n\n'.join('[[TABLE:'+r['表键']+']]' for r in index)+'\n',
        new_matrix_summary='负荷分散系数在1.05—1.25内按0.02间隔取11个节点，以1.15为界划分为≤1.15和>1.15两档。矩阵按电缆长度占比≤10%、(10%,30%]、>30%分为三档，每档列示两个负荷分散系数区间，共六张表。每张表以年最大净负荷平均增长率四档和装机渗透率三档选行，以初始转供率四档选列，形成48个区间单元，合计288个单元。\n')
    return tables, sections, cells, index


def export(data, directory):
    cells = records(data)
    directory.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(cells)
    (directory/'窗口与原始节点依据.json').write_text(json.dumps(cells,ensure_ascii=False,indent=2)+'\n')
    flat = frame.drop(columns=['代表节点'])
    flat.to_csv(directory/'六表288单元推荐窗口.csv', index=False)
    with pd.ExcelWriter(directory/'推广矩阵与11点敏感性分析.xlsx', engine='openpyxl') as writer:
        for (cable, kd), group in frame.groupby(['电缆档','分散档']):
            rows = []
            for (growth, eta), sub in group.groupby(['增长档','装机档']):
                rows.append(dict(年最大净负荷平均增长率=GROWTH[growth], 装机渗透率=ETA[eta]) |
                            {TRANSFER[int(r['转供档'])]:r['推荐窗口'] for r in sub.to_dict('records')})
            pd.DataFrame(rows).to_excel(writer, sheet_name=f'矩阵_电缆{cable+1}_分散{kd+1}', index=False)
        flat.to_excel(writer, sheet_name='窗口定位与全样本包络', index=False)
        for width in ['.10', '.20', '.30']:
            candidate = flat.copy()
            candidate['候选窗口'] = candidate['代表节点容载比'].map(lambda v:window(v, width))
            candidate.to_excel(writer, sheet_name='窗口宽度'+width, index=False)
        fields = DIVERSITY_CONTROLS
        mask = np.ones(len(data), dtype=bool)
        for field, value in fields.items():mask &= np.isclose(data[field], value, atol=1e-10, rtol=0)
        sequence = data.loc[mask].sort_values('负荷分散系数')
        assert len(sequence) == 11
        sequence.to_excel(writer, sheet_name='负荷分散系数11点完整序列', index=False)
        sequence.to_csv(directory/'负荷分散系数11点完整序列.csv', index=False)
        data.groupby('负荷分散系数').agg(有效节点数=('容载比','size'),容载比最小值=('容载比','min'),
            容载比中位数=('容载比','median'),容载比最大值=('容载比','max')).to_excel(writer, sheet_name='各节点覆盖情况')
        book = writer.book
        for sheet in book:
            sheet.freeze_panes = 'C2';sheet.auto_filter.ref = sheet.dimensions
            for column in sheet.columns:
                letter = column[0].column_letter
                sheet.column_dimensions[letter].width = min(42, max(16, len(str(column[0].value))+4))
                for cell in column[1:]:
                    if isinstance(cell.value,float):
                        cell.number_format='0.00%' if column[0].value in ['年最大净负荷平均增长率','电缆长度占比','初始转供率'] else '0.00'
    return cells, sequence
