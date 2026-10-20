"""十三项指标筛选及五参数矩阵的报告展示；只读已核验情景资料。"""
from pathlib import Path
from functools import lru_cache
import hashlib
import json
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT/'研究报告/01研究推荐/当前版/参数联合情景_20261012'
NEW = ROOT/'研究报告/01研究推荐/当前版/补充指标全背景扩展_20261014'
AUDIT = ROOT/'研究报告/05_review/当前版/1014十三选五与报告修订'
FIVE = ['分布式电源装机渗透率', '年最大净负荷平均增长率', '电缆长度占比', '初始转供率', '负荷分散系数']
METRICS = ['分布式电源装机渗透率', '分布式电源电量渗透率', '站级负载率最大值',
    '最大正向净负荷_MW', '最大反向净负荷_MW', '年最大净负荷平均增长率',
    '95%峰值持续时间_h', '负荷分散系数', '初始转供率', '主变与线路单位功率投资比',
    '主变与储能单位功率投资比', '电缆长度占比', '储能支撑持续时间_h']
SYMBOLS = ['ηC', 'ηE', 'βmax', 'P⁺', 'P⁻', 'ḡ', 'H95', 'KD', 'r₀', 'RTL', 'RTB', 'α', 'H']
INDEPENDENT = [METRICS[i] for i in [0, 1, 5, 11, 8, 6, 7]]+['线路价格倍率', '储能价格倍率']
FIRST_ABS_R = .40
REDUNDANT_ABS_R = .70


def label(name):
    return name.removesuffix('_MW').removesuffix('_h')


def table(title, headers, rows):
    return title+'\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join(
        '| '+' | '.join(map(str, row))+' |\n' for row in rows)


def fmt(v):
    return f'{0 if abs(float(v)) < .005 else float(v):.2f}'


@lru_cache(maxsize=1)
def frames():
    old = pd.read_csv(OLD/'统一有效样本.csv')
    new = pd.read_csv(NEW/'有效样本.csv')
    old_corr = pd.read_csv(OLD/'固定其余五项后的组内相关.csv')
    new_corr = pd.read_csv(NEW/'新增指标组内相关.csv')
    merged = {}
    for r in old_corr.to_dict('records'):
        name = '储能支撑持续时间_h' if r['参数'] == '储能支撑持续时间' else r['参数']
        merged[name] = dict(指标=name, 有效组数=r['有效受控组数'], 有效节点数=r['有效节点数'],
            Pearson=r['组内Pearson'], 容量响应组占比=r['主变容量响应组占比'])
    for r in new_corr.to_dict('records'):
        merged[r['指标']] = dict(指标=r['指标'], 有效组数=r['有效组数'], 有效节点数=r['有效节点数'],
            Pearson=r['组内Pearson'], 容量响应组占比=r['主变容量响应组占比'])
    combined = pd.DataFrame([merged[m] for m in METRICS])
    passing = combined.loc[combined.Pearson.abs().ge(FIRST_ABS_R), '指标'].tolist()
    assert len(passing) == 9 and set(FIVE) <= set(passing)
    cm = new[METRICS].corr()
    saved = pd.read_csv(NEW/'十三项指标Pearson.csv', index_col=0)
    np.testing.assert_allclose(cm, saved, atol=1e-12)
    selected = new[FIVE].corr()
    vif = np.diag(np.linalg.inv(selected.to_numpy()))
    z = (new[FIVE]-new[FIVE].mean())/new[FIVE].std(ddof=0)
    direct = []
    for j in range(5):
        y = z.iloc[:, j].to_numpy()
        x = np.delete(z.to_numpy(), j, axis=1)
        fitted = x@np.linalg.lstsq(x, y, rcond=None)[0]
        direct.append(float(y@y/((y-fitted)@(y-fitted))))
    np.testing.assert_allclose(vif, direct, rtol=1e-10, atol=1e-10)
    return old, new, combined, cm, selected, vif


def assets():
    old, new, correlations, cm, selected, vif = frames()
    t = {}
    t['current_controlled_correlations'] = table('表3-0 十三项指标与容载比的组内相关',
        ['指标', '有效组数', '有效节点数', 'Pearson', '容量响应组占比'],
        [[label(r['指标']), r['有效组数'], r['有效节点数'], fmt(r['Pearson']),
          f'{r["容量响应组占比"]*100:.0f}%'] for r in correlations.to_dict('records')])
    t['new_parameter_bins'] = table('表3-0 采用指标与推广矩阵分类',
        ['采用指标', '矩阵分类'], [
        [FIVE[0], '≤1；(1,2]；>2'],
        [FIVE[1], '≤2%；(2%,4%]；(4%,7%]；>7%'],
        [FIVE[2], '≤10%；(10%,30%]；>30%'],
        [FIVE[3], '≤30%；(30%,50%]；(50%,70%]；>70%'],
        [FIVE[4], '≤1.15；>1.15' if json.loads((ROOT/'tools/report_policy.json').read_text())['matrix_display'].get('diversity_cut')==1.15 else '1.00；1.10；1.15']])
    t['extended_parameter_nodes'] = table('表3-0 候选指标的采样节点与点数',
        ['指标', '采样节点或计算方式', '点数'], [
        [METRICS[0], '0～3.00，步长0.125', 25],
        [METRICS[1], '0～65%，步长2.5个百分点', 27],
        [METRICS[2], '随源荷情景计算各站负载率并取最大值', '由源荷节点计算'],
        [label(METRICS[3]), '按同期区域净负荷取正向极值', '由源荷节点计算'],
        [label(METRICS[4]), '按同期区域净负荷取反向极值', '由源荷节点计算'],
        [METRICS[5], '0、1%、2%、3%、4%、5%、5.5%、6%、7%、7.1%、7.5%、8%、9%、10%', 14],
        [label(METRICS[6]), '1～8 h，步长1 h', 8],
        [METRICS[7], '1.05～1.25，步长0.02', 11],
        [METRICS[8], '10%～90%，步长10个百分点', 9],
        [METRICS[9], '线路价格取参考值的70%～130%，步长10个百分点，按有效功率折算', '7个价格节点'],
        [METRICS[10], '储能价格取参考值的70%～130%，步长10个百分点，按有效功率折算', '7个价格节点'],
        [METRICS[11], '10%、30%、50%、80%、90%', 5],
        [label(METRICS[12]), '1～8 h，步长1 h', 8]])
    for part, indices in enumerate([list(range(7)), list(range(7, 13))], 1):
        t['extended_indicator_correlations_'+str(part)] = table(
            f'表3-0 十三项指标的Pearson相关矩阵（{part}）',
            ['指标']+[label(METRICS[i]) for i in indices],
            [[label(METRICS[j])]+[fmt(cm.iloc[j, i]) for i in indices] for j in range(13)])
    pairs = [(METRICS[1], FIVE[0], FIVE[0]), (METRICS[4], FIVE[0], FIVE[0]),
             (METRICS[2], FIVE[0], FIVE[0]), (METRICS[3], FIVE[1], FIVE[1])]
    t['parameter_redundancy_groups'] = table('表3-0 高相关指标归并及代表参数',
        ['候选指标', '对应基础参数', 'Pearson', '代表参数'],
        [[label(a), b, fmt(cm.loc[a, b]), c] for a, b, c in pairs])
    t['current_input_correlations'] = table('表3-0 五项推广参数的Pearson相关矩阵',
        ['参数']+FIVE, [[n]+[fmt(v) for v in selected.loc[n]] for n in FIVE])
    t['parameter_selection_summary'] = table('表3-0 十三项指标至五项推广参数的筛选结果',
        ['环节', '指标数', '处理结果'], [
        ['候选指标', 13, '涵盖源荷规模、运行压力、网络支援、时间及相对投资'],
        ['容载比相关性筛选', 9, '95%峰值持续时间、储能支撑持续时间及两项投资比的相关强度较低'],
        ['高相关指标归并', 5, '电量、反向净负荷和站级负载率归入装机指标组，正向净负荷归入增长指标组'],
        ['参数间相关核验', 5, '最大Pearson绝对值为'+fmt(np.max(np.abs(selected.to_numpy()-np.eye(5))))+'，五项间信息重叠较少']])
    base = dict(zip(INDEPENDENT, [2., .4, .04, .1, .4, 4., 1.1, 1., 1.]))
    sequences = {}
    for driver in [METRICS[1], METRICS[6]]+INDEPENDENT[-2:]:
        mask = np.ones(len(new), dtype=bool)
        for field, value in base.items():
            if field != driver:
                mask &= np.isclose(new[field], value, atol=1e-10, rtol=0)
        sequences[driver] = new.loc[mask].sort_values(driver)
    energy_rows = []
    for r in sequences[METRICS[1]].to_dict('records'):
        values = [fmt(r['主变容量_MVA']), fmt(r['容载比']), fmt(r['储能额定功率_MW']),
                  int(r['新增联络_条']), fmt(r['费用现值_万元'])]
        value = f'{r[METRICS[1]]*100:.0f}%'
        if energy_rows and energy_rows[-1][1:] == values:
            energy_rows[-1][0] += '、'+value
        else:
            energy_rows.append([value]+values)
    t['extended_energy_sequence'] = table('表5-0 固定装机条件下的电量与配置变化',
        ['电量渗透率', '主变/MVA', '容载比', '储能/MW', '新增联络/条', '费用现值/万元'], energy_rows)
    t['extended_duration_sequence'] = table('表5-0 固定主变与联络条件下的峰段支撑配置',
        ['95%峰值持续时间/h', '储能额定功率/MW', '费用现值/万元'],
        [[int(r[METRICS[6]]), fmt(r['储能额定功率_MW']), fmt(r['费用现值_万元'])]
         for r in sequences[METRICS[6]].to_dict('records')])
    t['extended_price_comparison'] = table('表5-0 固定设备配置下的两类价格比较',
        ['变化条件', '参考价格比例', '费用现值/万元'],
        [[name, '70%～130%', fmt(seq['费用现值_万元'].min())+'～'+fmt(seq['费用现值_万元'].max())]
         for name, seq in [("线路价格", sequences[INDEPENDENT[-2]]), ("储能价格", sequences[INDEPENDENT[-1]])]])
    return t


def verify():
    """独立重算十三项受控系数和五参数矩阵，绑定原始库核验。"""
    old, new, correlations, cm, selected, vif = frames()
    sampling = {}
    counts = dict(zip(INDEPENDENT+[METRICS[12]], [25,27,14,5,9,8,4,7,7,8]))
    for field, count in counts.items():
        nodes = set(new[field].round(10))
        if field in old:
            nodes |= set(old[field].round(10))
        assert len(nodes) == count, ('采样点数未对应真实节点', field, len(nodes), count)
        sampling[field] = {'点数': count, '实际节点': sorted(nodes)}
    for prefix in ['补充指标全背景扩展_20261014', '五参数推广矩阵新旧对比_20261014']:
        folder = ROOT/('研究报告/05_review/当前版/'+('1014补充指标全背景扩展' if prefix.startswith('补充') else '1014五参数推广矩阵新旧对比'))
        registry = json.loads((folder/'结果文件登记.json').read_text())
        files = registry.get('结果文件', registry)
        for name, digest in files.items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    original = FIVE[:4]+['储能支撑持续时间_h', FIVE[4]]
    expanded = new.copy()
    expanded[INDEPENDENT] = expanded[INDEPENDENT].round(10)
    driver = {METRICS[1]: METRICS[1], METRICS[2]: METRICS[1], METRICS[3]: FIVE[1],
        METRICS[4]: METRICS[1], METRICS[6]: METRICS[6], METRICS[9]: '线路价格倍率', METRICS[10]: '储能价格倍率'}
    checked = []
    for row in correlations.to_dict('records'):
        name = row['指标']
        data, fields, change = (old, original, name) if name in original else (expanded, INDEPENDENT, driver[name])
        fixed = [f for f in fields if f != change]
        eligible = data.groupby(fixed)[change].transform('nunique').ge(2)
        sub = data[eligible]
        # 原始一二阶矩分组求和，与先去均值后相关的生产路径相互独立。
        sums = np.zeros(3, dtype=np.longdouble)
        count = groups = responses = 0
        for _, group in sub.groupby(fixed):
            x = group[name].to_numpy(dtype=np.longdouble)
            y = group.容载比.to_numpy(dtype=np.longdouble)
            n = len(group)
            sums += [np.dot(x, y)-x.sum()*y.sum()/n,
                     np.dot(x, x)-x.sum()**2/n, np.dot(y, y)-y.sum()**2/n]
            count += n
            groups += 1
            responses += float(group.主变容量_MVA.max()-group.主变容量_MVA.min()) > 1e-7
        r = float(sums[0]/np.sqrt(sums[1]*sums[2]))
        assert abs(r-row['Pearson']) < 1e-10, (name, r, row['Pearson'])
        assert count == row['有效节点数'] and groups == row['有效组数']
        assert abs(responses/groups-row['容量响应组占比']) < 1e-12
        checked.append(row | {'独立复算Pearson': r})
    from compare_five_parameter_matrices import matrix
    actual = matrix(old)
    expected = pd.read_csv(ROOT/'研究报告/01研究推荐/当前版/五参数推广矩阵新旧对比_20261014/原数据五参数矩阵单元.csv')
    pd.testing.assert_frame_equal(actual, expected, check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-10)
    record = {'状态': '通过', '采样点数核验': sampling, '十三项组内相关复算': checked, '五参数最大绝对相关': float(np.max(np.abs(selected.to_numpy()-np.eye(5)))),
        '五参数VIF': dict(zip(FIVE, map(float, vif))), '推广矩阵单元数': len(actual),
        '有效节点数': len(old), '门限': {'与容载比相关绝对值': FIRST_ABS_R, '高相关归并绝对值': REDUNDANT_ABS_R},
        '第一层通过指标数': int(correlations.Pearson.abs().ge(FIRST_ABS_R).sum()),
        '基础模型及补充映射': '既定仿真方法；两类受控背景的输入和取值口径分别记录，未变更寻优模型',
        '原始依据': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [
            OLD/'统一有效样本.csv', NEW/'有效样本.csv', OLD/'固定其余五项后的组内相关.csv', NEW/'新增指标组内相关.csv']}}
    AUDIT.mkdir(parents=True, exist_ok=True)
    (AUDIT/'参数与矩阵独立核验.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    return record


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
