"""只读核对方案依据；输出写入本目录，不运行求解或正式报告生成器。"""
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
import csv
import hashlib
import itertools
import json
import re
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPORT = ROOT / '研究报告'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{' + NS['w'] + '}'


def dump(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(name, records):
    with (HERE / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def guide(g):
    if g <= .02:
        return 'g≤2%', [1.5, 1.7]
    if g <= .04:
        return '2%＜g≤4%', [1.6, 1.8]
    if g <= .07:
        return '4%＜g≤7%', [1.7, 1.9]
    return 'g＞7%', [1.8, 2.0]


def main():
    comment_path = REPORT / '甲方反馈/10.08/10.08研究报告_甲方批注.docx'
    with ZipFile(comment_path) as z:
        comments = ET.fromstring(z.read('word/comments.xml'))
        document = ET.fromstring(z.read('word/document.xml'))
    paragraphs = list(document.iter(W + 'p'))
    records = []
    for c in comments:
        cid = c.get(W + 'id')
        anchors = []
        for p in paragraphs:
            if any(n.get(W + 'id') == cid for tag in ('commentRangeStart', 'commentReference') for n in p.iter(W + tag)):
                anchors.append(''.join(t.text or '' for t in p.iter(W + 't')))
        records.append({'批注ID': cid, '作者': c.get(W + 'author'),
                        '批注原文': ''.join(t.text or '' for t in c.iter(W + 't')),
                        '锚定段落': '\n'.join(anchors)})
    assert len(records) == 10
    write_csv('10.08批注核对.csv', records)
    dump('10.08批注核对.json', records)

    annual_path = REPORT / '试算/20261010_实际年度负荷静态试算/原表容量负荷.csv'
    with annual_path.open(encoding='utf-8-sig') as f:
        annual = list(csv.DictReader(f))
    growth = []
    for rid, name in [('QX-00007', '市区'), ('QX-00005', '邳州')]:
        group = sorted((r for r in annual if r['region_id'] == rid), key=lambda r: int(r['year']))
        n = int(group[-1]['year']) - int(group[0]['year'])
        first, last = (float(group[k]['reported_downward_load_mw']) for k in (0, -1))
        g = (last / first) ** (1 / n) - 1
        interval, ratio = guide(g)
        growth.append({'地区': name, '开始年': int(group[0]['year']), '结束年': int(group[-1]['year']),
                       '增长间隔': n, '首年负荷MW': first, '末年负荷MW': last, 'CAGR': g,
                       '百分比展示': f'{g:.0%}', '所属导则区间': interval, '导则容载比范围': ratio})

    map_path = ROOT / '实验/研究/data/tuomin/变电站对应.md'
    mapping = {}
    for line in map_path.read_text().splitlines()[1:]:
        if not line.strip():
            continue
        full, short, sid = line.split('\t')
        assert sid not in mapping, sid
        mapping[sid] = {'全称': full, '简称': short}
    short_counts = Counter(v['简称'] for v in mapping.values())
    sources = sorted((REPORT / '03_MD/当前版').glob('*.md'))
    sources += [REPORT / '02图表/当前版' / x for x in ['计算表.json', '生成段落.json']]
    sources += sorted((REPORT / '试算/20261010_实际年度负荷静态试算').glob('*/*/stations.csv'))
    used = set()
    for p in sources:
        if p.exists():
            used.update(re.findall(r'BDZ-\d{5}', p.read_text(encoding='utf-8-sig')))
    display = [{'station_id': sid, **mapping[sid],
                '建议展示名': mapping[sid]['全称'] if short_counts[mapping[sid]['简称']] > 1 else mapping[sid]['简称']}
               for sid in sorted(used) if sid in mapping]
    write_csv('站名展示预检.csv', display)

    grid = {'eta': [0, .5, 1, 1.5, 2, 2.5, 3],
            'growth_rate': [0, .02, .03, .04, .055, .07, .08, .10],
            'line_cost_coefficient': [1, 1.65, 4.25, 6.85, 7.5],
            'initial_transfer_fraction': [.3, .4, .5, .6, .7],
            'support_duration_h': [2, 4, 6]}
    pilot = {'eta': [.5, 2.5], 'growth_rate': [.02, .08],
             'line_cost_coefficient': [1.65, 6.85], 'initial_transfer_fraction': [.3, .5],
             'support_duration_h': [2, 4, 6]}
    count = lambda d: len(list(itertools.product(*d.values())))
    assert count(grid) == 4200 and count(pilot) == 48
    assert guide(.02)[1] == [1.5, 1.7] and guide(.04)[1] == [1.6, 1.8] and guide(.07)[1] == [1.7, 1.9]
    line_costs = [{'线路成本系数': k, '电缆长度占比': (k - 1) / 6.5,
                   '单项投资万元': 3 * 24 * k + 6} for k in grid['line_cost_coefficient']]
    support = [{'持续时间h': h, '每柜支撑功率MW': min(.1, .215 * .76 / h)} for h in [2, 4, 6]]
    dump('参数设计.json', {
        '状态': '拟执行配置，尚未开展矩阵求解',
        '用户已确认': {'保留持续时间': True, '储能价格专项分析': True, '展示改中文站名': True},
        '主网格': grid, '主网格组合数': count(grid), '小样本': pilot,
        '小样本每模板组合数': count(pilot), '小样本网络模板数': 2, '小样本总数': count(pilot) * 2,
        '主表持续时间h': 4, '储能价格倍数专项': [.75, 1, 1.25], '储能降本压力点': .5,
        '负荷分散基准建议': 1.1, '负荷分散专项': [1, 1.1, 1.15],
        '弹性下限建议': 2.001, '统一容载比上限': None,
        '上限处理': '按设备候选形成物理上界，不把2.60作为外推硬约束',
        '统计范围': '主网格均衡统计；地区锚点、阈值近邻及专项检查另存',
        '增长区间': [{'条件': a, '建议容载比': b} for a, b in
                   [('g≤2%', [1.5, 1.7]), ('2%＜g≤4%', [1.6, 1.8]),
                    ('4%＜g≤7%', [1.7, 1.9]), ('g＞7%', [1.8, 2])]],
        '区间设置原则': '按范围分档，首尾开口，不以采样极值截断分类；参数固有物理定义仍有效',
        '增长分类下限': None, '增长分类上限': None,
        '采样与分类关系': '主网格为初始计算节点，0%和10%不是增长分类边界；验证范围另行登记',
        '增长尾部验证点': [-.02, .15],
        '转供区间': ['ρ0≤30%', '30%＜ρ0≤50%', 'ρ0＞50%'],
        '装机区间': ['η≤1', '1＜η≤2', 'η＞2'],
        '线路成本区间': ['kL≤1.65', '1.65＜kL≤6.85', 'kL＞6.85'],
        '持续时间区间': ['H≤2h', '2h＜H≤4h', 'H＞4h'],
        '阈值来源': '增长区间直接沿用表6.3.4；其他参数借鉴首尾开口形式，分界值为研究设置',
        '参数物理定义': {'eta': '非负', 'line_cost_coefficient': '正值',
                      'initial_transfer_fraction': '0至1', 'support_duration_h': '正值'},
        '4h基础展示单元数': 3 * 4 * 3 * 3,
        '全部区间基础单元数': 3 * 4 * 3 * 3 * 3,
        '未完成前置项': ['冻结显式网络模板及容量预算转换表', '确认静态工况与负荷分散独立变化',
                       '统一现行约束入口并完成独立复核', '先完成96组试点及两地4h对照'],
    })
    tracked = [comment_path, annual_path, map_path,
               ROOT / '参考政策/DL-T+5729-2023+配电网规划设计技术导则.pdf',
               ROOT / '实验/研究/rebuild_2026/current_economic_assumptions.py',
               ROOT / '实验/研究/rebuild_2026/static_actual_20261010/run.py',
               REPORT / '05_review/当前版/通用参数外推.py']
    dump('依据核验.json', {
        '仅依据核验': True, '新版矩阵已求解': False, '正式正文已修改': False,
        '批注数': len(records), '增长率复算': growth, '线路系数换算': line_costs,
        '静态支撑功率复算': support,
        '站名映射': {'映射总数': len(mapping), '检查到的不同编码数': len(used),
                   '已匹配数': len(display), '缺失编码': sorted(used - mapping.keys()),
                   '全映射简称重名数': sum(v > 1 for v in short_counts.values()),
                   '检查范围': [str(p.relative_to(ROOT)) for p in sources if p.exists()]},
        '导则原文已目视核对': ['PDF第24页：表6.3.4', 'PDF第28页：7.1.2第1款'],
        '来源SHA256': {str(p.relative_to(ROOT)): sha(p) for p in tracked},
    })
    print(json.dumps({'批注': len(records), '增长率': growth,
                      '映射预检': [len(mapping), len(used), len(display)],
                      '缺失编码': sorted(used - mapping.keys()), '主网格': count(grid)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
