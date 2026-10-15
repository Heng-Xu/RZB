"""核对用户定稿的八组报告数据及其采用范围；不求解、不修改成果。"""
import csv
import hashlib
import json
from pathlib import Path

from export_adopted_report_summary import render

ROOT = Path(__file__).resolve().parents[1]
ADOPTION = ROOT / '研究报告/01研究推荐/当前版/报告数据采用版本.json'
ADOPTION_MANIFEST = ROOT / '研究报告/05_review/当前版/1015研究报告数据定稿/定稿登记清单.json'
EXPECTED_MANIFEST_SHA = 'a6551b064aab3352cf019bb8f67cb937c4e0a6420b0537db5694121a9bb87ad0'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(item):
    path = ROOT / item['path']
    assert path.is_file() and sha(path) == item['sha256'], '采用文件变化：' + item['path']
    return path


def read_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def verify():
    registration = json.loads(ADOPTION_MANIFEST.read_text())
    assert registration['状态'] == '用户确认及数据核验通过'
    for name, digest in registration['文件SHA256'].items():
        assert sha(ROOT / name) == digest, '定稿登记变化：' + name
    adopted = json.loads(ADOPTION.read_text())
    assert adopted['状态'] == '用户确认定稿'
    assert adopted['版本'] == '20261015-static-joint'
    assert adopted['结果清单']['sha256'] == EXPECTED_MANIFEST_SHA
    manifest = json.loads(checked(adopted['结果清单']).read_text())
    assert manifest['状态'] == '八组逐项核验通过'
    for name, digest in manifest['文件SHA256'].items():
        assert sha(ROOT / name) == digest, '冻结成果变化：' + name
    proof = json.loads(checked(adopted['完整复核']).read_text())
    assert proof['verified'] and proof['full_lp_recomputed']
    assert proof['schemes'] == 8 and proof['static_pairs'] == 30336
    assert proof['normal_storage_verified']
    sources = json.loads(checked(adopted['案例来源']).read_text())
    assert sources['verified'] and sources['schemes'] == 8
    source_map = {(r['region'], r['baseline'], r['case']): r for r in sources['sources']}
    model_sources = json.loads(checked(adopted['输入与模型来源']).read_text())
    for item in model_sources['sources'] + model_sources['依赖源码']:
        checked(item)
    for name in ['逐年工作簿', '模型与方案条件', '经济参考']:
        checked(adopted[name])
    annual = read_rows(checked(adopted['逐年结果']))
    final = read_rows(checked(adopted['末年与费用']))
    assert len(annual) == 40 and len(final) == 8
    expected = {(r, b, c) for r in ['pizhou', 'city']
                for b in ['compressed', 'annual_2021'] for c in ['rigid', 'elastic_free']}
    schemes = adopted['方案采用']
    assert len(schemes) == 8
    assert {(r['地区代码'], r['起点代码'], r['方案代码']) for r in schemes} == expected
    initial_capacities = {('pizhou', 'compressed'): 1463.5, ('city', 'compressed'): 2900.,
                          ('pizhou', 'annual_2021'): 2027., ('city', 'annual_2021'): 3113.5}
    for r in schemes:
        key = r['地区代码'], r['起点代码'], r['方案代码']
        source = source_map[key]
        assert r['结果目录'] == source['folder']
        assert r['用途'] == ('主方案' if key[1] == 'compressed' else '原表起点补充对照')
        inp_path = checked(r['输入'])
        assert sha(inp_path) == source['input_sha256']
        inp = json.loads(inp_path.read_text())
        assert inp['fixed_baseline_year'] == 2021 and inp['years'] == [2022, 2023, 2024, 2025]
        assert not inp['normal_supply_area_fixed'] and not inp['selection_conditions']
        assert inp['initial_capacity_mva'] == initial_capacities[key[:2]] == r['2021初始容量_MVA']
        summary_path = checked(r['方案汇总'])
        assert summary_path.parent == ROOT / source['folder']
        assert sha(summary_path) == source['files']['summary.json']
        summary = json.loads(summary_path.read_text())
        selected = [a for a in annual if (a['地区'], a['起点'], a['方案']) == (r['地区'], r['起点'], r['方案'])]
        assert len(selected) == 5 and {int(a['年份']) for a in selected} == {2021, 2022, 2023, 2024, 2025}
        assert len(summary['annual']) == 4
        for a in summary['annual']:
            row = next(x for x in selected if int(x['年份']) == a['year'])
            for column, field in [('年末主变_MVA', 'capacity_mva'), ('容载比', 'clr'),
                                  ('年末储能_MWh', 'storage_mwh'), ('累计新增联络_条', 'cumulative_lines')]:
                assert abs(float(row[column]) - a[field]) < 1e-8
        last = next(a for a in final if (a['地区'], a['起点'], a['方案']) == (r['地区'], r['起点'], r['方案']))
        for column, value in r['2025结果及费用'].items():
            assert abs(float(last[column]) - value) < 1e-8
    for item in adopted['推广矩阵']['文件']:
        checked(item)
    corrections = read_rows(checked(adopted['兴塘工况核对']))
    originals = read_rows(checked(adopted['典型工况支撑']))
    assert len(corrections) == 4 and all(row in originals for row in corrections)
    assert checked(adopted['采用说明']).read_text() == render()
    return {'状态': '通过', '版本': adopted['版本'], '主方案': 4, '补充方案': 4,
            '优化年度记录': 32, '静态校核工况': proof['static_pairs'],
            '冻结文件': len(manifest['文件SHA256'])}


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False))
