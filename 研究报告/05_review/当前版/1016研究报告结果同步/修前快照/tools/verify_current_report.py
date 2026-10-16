"""核对当前报告的数据出处、定值矩阵、逐站结果及Word图件。"""
from pathlib import Path
import csv,hashlib,json,math,re
from docx import Document
from docx.oxml.ns import qn
import sync_current_report_results as sync
from report_math_layout import equation_tables

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_annual_guide():
    import pymupdf
    annual=ROOT/'研究报告/数据来源/当前版/实际案例相关性/年度样本.csv'
    measures=sync.CASE/'报告主方案逐年措施.csv'
    policy=ROOT/'参考政策/《配电网规划设计技术导则（修订稿）》.pdf'
    with pymupdf.open(policy) as pdf:
        page=pdf[19].get_text()
        for phrase in ['6.2.2.1','1.5～','1.7～1.9','1.5～1.7','增加转供能力']:
            assert phrase in page,'政策原文缺少:'+phrase
    samples=list(csv.DictReader(annual.open(encoding='utf-8-sig')))
    rows=list(csv.DictReader(measures.open(encoding='utf-8-sig')))
    records=[]
    for region,expected_kp,lo,hi in [('邳州',.06923192559398039,1.7,1.9),('市区',.01336129306847722,1.5,1.7)]:
        actual={int(r['year']):r for r in samples if r['region']==region}
        kp=(float(actual[2025]['peak_mw'])/float(actual[2021]['peak_mw']))**.25-1
        assert math.isclose(kp,expected_kp,abs_tol=1e-12)
        assert (0.04<kp<=.07) if region=='邳州' else kp<=.02
        for r in rows:
            if r['地区']!=region or r['方案']!='弹性无下限':continue
            y=int(r['年份']);capacity=float(r['年末容量_MVA']);load=float(r['年度负荷_MW']);ratio=capacity/load
            assert math.isclose(load,float(actual[y]['peak_mw']),abs_tol=1e-8)
            assert math.isclose(ratio,float(r['容载比']),abs_tol=1e-12)
            assert ratio>=lo
            records.append(dict(地区=region,年份=y,统一分档KP=kp,建议下限=lo,建议上限=hi,
                容量_MVA=capacity,负荷_MW=load,容载比=ratio,高于分档上限=ratio>hi,高于总体上限=ratio>2))
    assert {(r['地区'],r['年份']) for r in records if r['高于总体上限']}=={('邳州',2022),('邳州',2023),('市区',2022),('市区',2024)}
    assert {(r['地区'],r['年份']) for r in records if not r['高于分档上限']}=={('邳州',2025)}
    chapter=next((ROOT/'研究报告/03_MD/当前版').glob('05 *.md')).read_text()
    added=chapter.split('### 5.4.3 弹性方案与导则建议范围的逐年对照')[1].split('### 5.4.4')[0]
    assert '目标年' not in added and '[69]' in added
    for row in ['| 饱和期 | KP≤2% | 1.5～1.7 |','| 较慢增长 | 2%＜KP≤4% | 1.6～1.8 |','| 中等增长 | 4%＜KP≤7% | 1.7～1.9 |','| 较快增长 | KP＞7% | 1.8～2.0 |']:
        assert row in added, '导则分档表与原文不一致: '+row
    assert f'{1528.82*1.7:.2f}' in added and '翟山变' in added
    (sync.REVIEW/'逐年导则对照核验.json').write_text(json.dumps(dict(状态='通过',
        政策版本='2025年4月修订稿，第6.2.2.1条及表2，PDF第20页',
        来源SHA256={str(p.relative_to(ROOT)):sha(p) for p in [annual,measures,policy]},
        逐年对照=records,市区2025年按1点7折算容量_MVA=1528.82*1.7,
        市区初始容量超出折算容量_MVA=2900-1528.82*1.7),ensure_ascii=False,indent=2)+'\n')

def main():
    verify_annual_guide()
    pt,ps,cells,index,data=sync.parameter_assets();ct,cs,evidence=sync.case_assets()
    t=sync.read(sync.A/'计算表.json');s=sync.read(sync.A/'生成段落.json')
    for k,v in (pt|ct).items():assert t[k]==v,'计算表.json:'+k
    for k,v in (ps|cs).items():assert s[k]==v,'生成段落.json:'+k
    from report_parameter_selection import verify as verify_selection
    selection=verify_selection()
    source=ROOT/'研究报告/03_MD/当前版/研究报告装配稿.md';text=source.read_text()
    expected=re.findall(r'^!\[\]\(([^)]+)\)',text,re.M)
    word=ROOT/'研究报告/04_word/研究报告终稿.docx';doc=Document(word)
    assert not doc.element.xpath('.//w:ins | .//w:del'),'研究报告按普通模式修改'
    assert not doc.settings.element.xpath('./w:trackRevisions'),'研究报告不启用修订模式'
    assert len(doc.inline_shapes)==len(expected)
    for shape,path in zip(doc.inline_shapes,expected):
        blip=shape._inline.xpath('.//a:blip')[0];part=doc.part.related_parts[blip.get(qn('r:embed'))]
        assert hashlib.sha256(part.blob).hexdigest()==sha(ROOT/path),'图件未同步:'+path
    assert len(re.findall(r'^#### .*规划分析$',text,re.M))==46
    assert len(cells)==432 and len(index)==9 and sum(c['有效样本数'] for c in cells)==32112
    assert all(r['最小余量_MW']>-1e-6 for r in evidence)
    body=text.split('# 参考文献')[0]
    for stale in ['12600组','648个','2.001','邳州124.80','市区499.20','年度同比增长率','案例敏感性','储能价格的专项比较']:
        assert stale not in body,'仍有旧版表述:'+stale
    for item in sync.read(sync.LOCK)['model_files']:
        assert sha(ROOT/item['path'])==item['sha256'],'模型锁定文件变化:'+item['path']
    result=dict(状态='通过',有效参数节点=32112,五参数矩阵=9,区间单元=432,逐站分析=46,
        指标筛选=selection,
        图件=len(expected),原生公式=len(equation_tables(doc)),
        WordSHA256=sha(word),模型经济参数='锁定文件哈希一致，未改动',
        原始依据SHA256={str(p.relative_to(ROOT)):sha(p) for p in [sync.LOCK,
            sync.PUBLIC/'统一有效样本.csv',sync.PUBLIC/'固定其余五项后的组内相关.csv',
            sync.PUBLIC/'六参数输入相关.csv',sync.CASE/'报告主方案逐年措施.csv']})
    (sync.REVIEW/'当前报告数据核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='原始依据SHA256'},ensure_ascii=False))
if __name__=='__main__':main()
