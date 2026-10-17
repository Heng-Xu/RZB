"""只读核对后续报告固定采用的区县案例、原始解及主表对应关系。"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADOPTION = Path('研究报告/01研究推荐/当前版/后续报告案例采用版本.json')
VERSION = '20261017-annual-demand-driven-2035'
PUBLIC = Path('研究报告/01研究推荐/当前版/逐年需求驱动2035_20261017')
RAW = Path('研究报告/试算/20261017_逐年需求驱动2035')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def checked(root, item):
    path = root / item['path']
    assert path.is_file() and sha(path) == item['sha256'], '案例锁定文件变化：' + item['path']
    return path


def verify(root=ROOT):
    adopted = read_json(root / ADOPTION)
    assert adopted['状态'] == '用户确认固定'
    assert adopted['版本'] == VERSION and adopted['结果目录'] == str(PUBLIC)
    assert adopted['展示年度'] == list(range(2021, 2036))
    manifest = read_json(checked(root, adopted['锁定清单']))
    assert manifest['版本'] == VERSION and manifest['状态'] == '逐年可行方案已核对'
    assert manifest['锁定核对'] == '指定版本文件与原交付哈希一致'
    original = read_json(checked(root, manifest['原交付清单']))
    expected = {r['path']: r['sha256'] for r in original['files']
                if r['path'] not in ('memory/current.md', 'prompt.md') and '/未采用/' not in r['path']}
    assert {r['path']: r['sha256'] for r in manifest['files']} == expected, '固定文件范围与指定原交付不一致'
    for name, value in expected.items():
        checked(root, dict(path=name, sha256=value))
    proof = read_json(checked(root, adopted['独立核验']))
    assert proof['verified'] and proof['primary_hour_pairs'] == 12509280
    assert proof['full_hour_pairs'] == 18763920 and len(proof['schemes']) == 6
    schemes = adopted['主方案']
    assert len(schemes) == 4 and {(s['地区代码'], s['方案代码']) for s in schemes} == {
        (r, c) for r in ('city', 'pizhou') for c in ('rigid', 'elastic_capacity')}
    assert adopted['经济对照代码'] == 'elastic_engineering'
    costs = read_csv(root / PUBLIC / '费用分项汇总.csv')
    for item in schemes:
        region, case = item['地区代码'], item['方案代码']
        folder = RAW / region / case
        assert item['原始结果目录'] == str(folder)
        summary = read_json(root / folder / 'summary.json')
        assert [r['year'] for r in summary['annual']] == adopted['展示年度']
        assert summary['annual'][0]['capacity_mva'] == item['2021容量_MVA']
        assert item['2035结果'] == summary['annual'][-1]
        assert item['费用现值_万元'] == summary['cost_npv_10k']
        public_rows = read_csv(root / PUBLIC / f"{item['地区']}逐年左右对照.csv")
        assert [int(r['年份']) for r in public_rows] == adopted['展示年度']
        fields = {'规划峰值_MW': 'peak_mw', '年末容量_MVA': 'capacity_mva',
                  '当年净增容量_MVA': 'net_capacity_increment_mva', '容载比': 'clr',
                  '年末储能功率_MW': 'storage_nameplate_mw',
                  '年末累计新增联络_条': 'cumulative_lines'}
        for row, annual in zip(public_rows, summary['annual']):
            for column, field in fields.items():
                key = column if column == '规划峰值_MW' else item['主表列名'] + '_' + column
                assert abs(float(row[key]) - annual[field]) < 1e-8, f'{folder}/{annual["year"]}/{key}'
        cost = next(r for r in costs if (r['地区'], r['方案']) == (item['地区'], item['主表列名']))
        assert abs(float(cost['合计费用现值_万元']) - summary['cost_npv_10k']) < 1e-8
    return dict(状态='通过', 版本=VERSION, 主方案=4, 主方案年度记录=60,
                固定文件=len(expected), 主方案小时工况=proof['primary_hour_pairs'],
                报告同步=adopted['报告同步状态'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(verify(args.root.resolve()), ensure_ascii=False))
