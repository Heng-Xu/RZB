"""独立核对本轮反馈响应的证据边界；诊断结果不替换现行规划方案。"""
from pathlib import Path
import collections
import importlib.util
import itertools
import json
import math
import sys

HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent
ROOT = REVIEW.parents[2]
sys.path.insert(0, str(ROOT))
DATA = ROOT / '研究报告/01研究推荐/当前版'


def main():
    rows = json.loads((DATA / '外推逐点结果.json').read_text())
    matrix = json.loads((DATA / '通用推荐矩阵.json').read_text())
    line_counts = {}
    for area in ('A', 'BC'):
        subset = [r for r in rows if r['供电区域'] == area]
        line_counts[area] = dict(collections.Counter(r['联络项目数'] for r in subset))
    details = [json.loads(line) for line in (DATA / '外推站级方案.jsonl').read_text().splitlines()]
    minimum_projects = collections.Counter()
    for detail in details:
        area = detail['参数'][3]
        rho, target = (.50, .50) if area == 'A' else (.28287889, .30)
        counts = [max(0, math.ceil((target - rho) * s['负荷MW'] / 7.49106117 - 1e-12))
                  for s in detail['站级']]
        # 每项目两个端点且不允许同站自连，所需项目数至少为以下两者之大。
        minimum = max(max(counts), math.ceil(sum(counts) / 2))
        assert detail['项目数'] >= minimum
        minimum_projects[(area, minimum, detail['项目数'])] += 1

    spec = importlib.util.spec_from_file_location('current_static', REVIEW / '通用参数外推.py')
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    comparisons = []
    for area, shape, line_type, (eta, growth, hours) in itertools.product(
        ('A', 'BC'), ('偏集中', '较均匀'), ('架空为主', '电缆为主'),
        ((0., .10, 1), (3., 0., 6))
    ):
        constrained = model.solve(eta, growth, hours, area, 1., 1., shape, line_type,
                                  relative_gap=1e-8)
        relaxed = model.solve(eta, growth, hours, area, 1., 1., shape, line_type,
                              relative_gap=1e-8, lower=0.)
        assert relaxed['全寿命费用万元'] <= constrained['全寿命费用万元'] + 1e-3
        comparisons.append({'供电区域': area, '负荷分布': shape, '线路类型': line_type,
                            '源荷比': eta, '增长率': growth, '峰段h': hours,
                            '突破下限方案': constrained, '仅保留增长分档下限方案': relaxed,
                            '费用降幅': 1 - relaxed['全寿命费用万元'] / constrained['全寿命费用万元']})
        print(json.dumps({'诊断已完成': len(comparisons), '共': 16,
                          '取消突破下限后容载比': relaxed['推荐容载比']}, ensure_ascii=False), flush=True)
    result = {
        '性质': '反馈响应复核及16组下限诊断；现行四年案例与25200组正式结果保持原值',
        '外推组合': len(rows), '各供电类别联络项目数分布': line_counts,
        '规划目标推导的项目下界与实际项目数': [
            {'供电区域': k[0], '项目数下界': k[1], '实际项目数': k[2], '组合数': n}
            for k, n in sorted(minimum_projects.items())],
        '矩阵单元': len(matrix),
        '主选档不足覆盖单元数': sum(float(r['主选参考档位']) + 1e-9 < r['容载比最大值'] for r in matrix),
        '多档单元数': sum(len(r['档位计数']) > 1 for r in matrix),
        '下限诊断': comparisons,
        '诊断限制': '只检查所列模板；未撤销两地区四年案例的跨地区排序，也未完成连续SOC或实际馈线校核。'}
    (HERE / '二轮技术复核.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    sys.path.insert(0, str(REVIEW))
    from 驱动因子分析 import table
    assets = ROOT / '研究报告/02图表/当前版'
    tables = json.loads((assets / '计算表.json').read_text())
    tables['breakthrough_floor_diagnostic'] = table(
        '表5-0 是否要求突破2.00的条件比较（源荷比0.00、增长率10.00%、峰段1 h）',
        ['供电类别', '负荷分布', '线路类型', '要求突破的容载比', '取消该下限的容载比', '费用降幅'],
        [[r['供电区域'].replace('BC', 'B/C'), r['负荷分布'], r['线路类型'],
          f"{r['突破下限方案']['推荐容载比']:.2f}",
          f"{r['仅保留增长分档下限方案']['推荐容载比']:.2f}",
          f"{max(0., r['费用降幅']) * 100:.2f}%"]
         for r in comparisons if r['源荷比'] == 0.]
    )
    (assets / '计算表.json').write_text(json.dumps(tables, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
