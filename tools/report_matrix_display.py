"""从锁定有效节点生成不单独按线路系数分类的查表矩阵。"""
import math
import numpy as np

GROWTH = ['≤2%', '(2%,4%]', '(4%,7%]', '>7%']
ETA = ['≤1', '(1,2]', '>2']
TRANSFER = ['≤30%', '(30%,50%]', '(50%,70%]', '>70%']


def assets(data, table, interval):
    """电缆节点和2/4/6 h在单元内归纳，按三个分散定值列示。"""
    subset = data.copy()
    fields = ['年最大净负荷平均增长率', '分布式电源装机渗透率', '初始转供率']
    cuts = [[.02, .04, .07], [1, 2], [.3, .5, .7]]
    for field, limits in zip(fields, cuts):
        subset['bin_' + field] = subset[field].map(lambda x: sum(x > c + 1e-9 for c in limits))
    tables, cells, indexes = {}, [], []
    for kd in [1., 1.1, 1.15]:
        frame = subset[np.isclose(subset['负荷分散系数'], kd)]
        rows = []
        key = f'lookup_matrix_{kd:.2f}'
        for g in range(4):
            for eta in range(3):
                values = []
                for transfer in range(4):
                    sub = frame[(frame['bin_' + fields[0]] == g) &
                                (frame['bin_' + fields[1]] == eta) &
                                (frame['bin_' + fields[2]] == transfer)]
                    assert len(sub), (kd, g, eta, transfer)
                    lo, hi = sub['容载比'].min(), sub['容载比'].max()
                    text = interval(lo, hi)
                    values.append(text)
                    cells.append(dict(表键=key, 负荷分散系数=kd, 增长档=g, 装机档=eta, 转供档=transfer,
                                      有效样本数=len(sub), 下界=float(lo), 上界=float(hi), 展示区间=text,
                                      下界原始节点=sub.loc[sub['容载比'].idxmin(), fields + ['储能支撑持续时间_h']].to_dict(),
                                      上界原始节点=sub.loc[sub['容载比'].idxmax(), fields + ['储能支撑持续时间_h']].to_dict()))
                rows.append([GROWTH[g], ETA[eta]] + values)
        tables[key] = table(f'表5-0 负荷分散系数{kd:.2f}的容载比区间矩阵',
                            ['年最大净负荷平均增长率', '装机渗透率'] + TRANSFER, rows)
        indexes.append(dict(表键=key, 负荷分散系数=kd, 电缆长度占比节点=[.1,.3,.5,.8,.9],
                            支撑时长_h=[2, 4, 6], 有效样本数=len(frame), 区间单元=48))
    assert len(cells) == 144 and sum(c['有效样本数'] for c in cells) == len(subset)
    sections = dict(new_matrix_tables='\n\n'.join('[[TABLE:' + x['表键'] + ']]' for x in indexes) + '\n',
                    new_matrix_summary='矩阵按负荷分散系数1.00、1.10、1.15分别列示。每张表以年最大净负荷平均增长率四档和装机渗透率三档选行，以初始转供率四档选列，形成48个区间单元，三张表共144个单元。电缆长度占比10%～90%的已计算节点与储能支撑持续时间2、4、6 h的有效配置共同归入相应单元。\n')
    return tables, sections, cells, indexes
