"""从冻结结果导出报告采用说明，修正原汇总兴塘段落的工况引用。"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / '研究报告/01研究推荐/当前版'
RESULTS = PUBLIC / '静态联合替代_20261015'
OUTPUT = PUBLIC / '报告采用数据说明.md'


def rows(name):
    with (RESULTS / name).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def mechanism_rows():
    return [r for r in rows('典型工况支撑.csv')
            if r['地区'] == '邳州' and r['起点'] == '共同仿真起点'
            and r['年份'] == '2025' and r['工况'] == 'N-1'
            and r['故障站'] == r['站名'] == '兴塘变']


def render():
    records = mechanism_rows()
    assert len(records) == 4
    assert {r['截面'] for r in records} == {'6', '15'}
    indexed = {(r['方案'], r['截面']): r for r in records}
    rigid = indexed['刚性方案', '6']
    elastic = indexed['弹性经济优选方案', '6']
    assert float(rigid['原净负荷_MW']) == float(elastic['原净负荷_MW']) < 0
    for r in [rigid, elastic]:
        assert float(r['转出_MW']) == float(r['转入_MW']) == 0
        assert abs(-float(r['原净负荷_MW']) - float(r['主变反向限值_MW'])
                   - float(r['所需充电_MW'])) < 1e-8
    text = (RESULTS / '两区县全套结果汇总.md').read_text()
    old = ('在同一反向极值工况，所需充电吸收由0.00 MW降至0.00 MW，'
           '对应储能由25.16 MWh降至1.72 MWh。容量补到局部短板后，'
           '储能需求下降有明确的功率平衡依据。')
    corrected = (f'在同一反向极值工况（截面6），站内净负荷为'
                 f'{float(rigid["原净负荷_MW"]):.2f} MW，所需充电吸收由'
                 f'{float(rigid["所需充电_MW"]):.2f} MW降至'
                 f'{float(elastic["所需充电_MW"]):.2f} MW，对应储能由'
                 '25.16 MWh降至1.72 MWh。该工况两方案转供均为0，'
                 '差异直接来自站内主变能力提高。')
    assert text.count(old) == 1
    text = text.replace(old, corrected)
    text = text.replace('# 两区县静态联合替代方案汇总',
                        '# 研究报告采用数据定稿说明\n\n'
                        '2026年10月15日经用户确认，本套8组结果作为后续研究报告的数据依据。'
                        '共同仿真起点4组作为主方案，保留2021原表容量4组作为补充对照。')
    old_scope = ('本套为独立结果包，正式研究报告及讨论稿尚未替换；'
                 '没有新增全年SOC或新能源利用率结论。')
    new_scope = ('本次完成数据定稿登记，正式研究报告正文、Word及WPS PDF待后续同步。'
                 '静态校核范围及费用比较沿用已核验结果。')
    assert text.count(old_scope) == 1
    text = text.replace(old_scope, new_scope)
    matrix = ['## 推广矩阵采用展示', '',
              '采用五站设备重新选配的典型模板，电缆长度占比50%、储能支撑4 h固定。'
              '以下两组在转供率四档间的推荐区间上下界均下降；10%—90%的九个细节点仍保留平台。'
              '线路费用条件集中说明，不单独按线路系数分类讨论。', '',
              '|装机渗透率|年最大净负荷平均增长率（小数）|负荷分散系数|≤30%|(30%,50%]|(50%,70%]|>70%|',
              '|---:|---:|---:|---|---|---|---|']
    for r in rows('典型响应推荐矩阵.csv'):
        matrix.append('|' + '|'.join([f'{float(r["装机渗透率"]):.0%}',
                      f'{float(r["年最大净负荷平均增长率"]):.3f}',
                      f'{float(r["负荷分散系数"]):.2f}',
                      *(r[k] for k in ['≤30%', '(30%,50%]', '(50%,70%]', '>70%'])]) + '|')
    matrix.extend(['', '区间沿用完整精度计算所得分档，适用条件及完整细节点共同保留。', ''])
    return text.replace('## 核验与使用范围', '\n'.join(matrix) + '\n## 核验与使用范围')


if __name__ == '__main__':
    if OUTPUT.exists():
        assert OUTPUT.read_text() == render(), '采用说明已变化，须先复核差异'
    else:
        OUTPUT.write_text(render())
    print(OUTPUT.relative_to(ROOT))
