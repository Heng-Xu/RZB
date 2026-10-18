"""按五项采用参数归纳锁定节点；时长集合仅在核验资料登记。"""
import math
import numpy as np

GROWTH = ['≤2%', '(2%,4%]', '(4%,7%]', '>7%']
ETA = ['≤1', '(1,2]', '>2']
TRANSFER = ['≤30%', '(30%,50%]', '(50%,70%]', '>70%']
CABLE = ['≤10%', '(10%,30%]', '>30%']


def adjoining_bands(intervals):
    """由四档容量下界划定相接的规划推荐带；输入的节点包络另行保留。"""
    from decimal import Decimal
    bounds = [tuple(Decimal(x) for x in value.split('～')) for value in intervals]
    assert len(bounds) == 4 and all(lo <= hi for lo, hi in bounds)
    lows = [lo for lo, hi in bounds]
    assert all(a >= b for a, b in zip(lows, lows[1:])), '容量下界出现回升，须另选场景或核查，不能自动压平'
    ends = [bounds[0][1]] + lows
    return [f'{ends[j+1]:.2f}～{ends[j]:.2f}' for j in range(4)]


def assets(data, table, interval):
    """节点包络留存依据，正文按四档容量下界衔接规划推荐带。"""
    subset = data.copy()
    fields = ['年最大净负荷平均增长率', '分布式电源装机渗透率', '初始转供率', '电缆长度占比']
    cuts = [[.02, .04, .07], [1, 2], [.3, .5, .7], [.1, .3]]
    for field, limits in zip(fields, cuts):
        subset['bin_' + field] = subset[field].map(lambda x: sum(x > c + 1e-9 for c in limits))
    tables, cells, indexes = {}, [], []
    for cable, kd in [(c, k) for c in range(3) for k in [1., 1.1, 1.15]]:
        frame = subset[np.isclose(subset['负荷分散系数'], kd) & (subset['bin_电缆长度占比'] == cable)]
        rows = []
        key = f'lookup_matrix_{cable}_{kd:.2f}'
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
                    cells.append(dict(表键=key, 电缆档=cable, 负荷分散系数=kd, 增长档=g, 装机档=eta, 转供档=transfer,
                                      有效样本数=len(sub), 下界=float(lo), 上界=float(hi), 展示区间=text,
                                      下界原始节点=sub.loc[sub['容载比'].idxmin(), fields + ['储能支撑持续时间_h']].to_dict(),
                                      上界原始节点=sub.loc[sub['容载比'].idxmax(), fields + ['储能支撑持续时间_h']].to_dict()))
                bands = adjoining_bands(values)
                for cell, band in zip(cells[-4:], bands):
                    cell['节点包络'] = cell['展示区间']
                    cell['推荐带'] = band
                rows.append([GROWTH[g], ETA[eta]] + bands)
        tables[key] = table(f'表5-0 电缆长度占比{CABLE[cable]}、负荷分散系数{kd:.2f}的容载比分档建议矩阵',
                            ['年最大净负荷平均增长率', '装机渗透率'] + TRANSFER, rows)
        indexes.append(dict(表键=key, 电缆档=cable, 电缆区间=CABLE[cable], 负荷分散系数=kd,
                            电缆长度占比节点=sorted(frame['电缆长度占比'].unique().tolist()),
                            支撑时长_h=[2, 4, 6], 有效样本数=len(frame), 区间单元=48))
    assert len(cells) == 432 and sum(c['有效样本数'] for c in cells) == len(subset)
    sections = dict(new_matrix_tables='\n\n'.join('[[TABLE:' + x['表键'] + ']]' for x in indexes) + '\n',
                    new_matrix_summary='矩阵按电缆长度占比≤10%、(10%,30%]、>30%划分三档，每档分别列示负荷分散系数1.00、1.10、1.15的结果，共九张表。每张表以年最大净负荷平均增长率四档和装机渗透率三档选行，以初始转供率四档选列，形成48个区间单元，合计432个单元。\n')
    return tables, sections, cells, indexes
