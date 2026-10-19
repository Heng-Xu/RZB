"""在已交付清稿基础上局部替换正文块，保留批注并停用全部修订。"""
from collections import Counter
from copy import deepcopy
from difflib import SequenceMatcher
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import re

from lxml import etree as E
from docx import Document

from revise_report_in_place import package, xml, dump, fingerprint, text, qn, NS, R, P

ROOT = Path(__file__).resolve().parents[1]


def review_dir(root=ROOT):
    policy=json.loads((root/'tools/report_policy.json').read_text())
    return root/policy.get('plain_delivery_review', '研究报告/05_review/当前版/1019七项表述与清稿')


REVIEW = review_dir()
MODE = REVIEW/'交付模式.json'
BASE = REVIEW/'修前原件/研究报告/04_word/研究报告终稿.docx'
MODE_SETTINGS = json.loads(MODE.read_text()) if MODE.exists() else {}
FEEDBACK = REVIEW/MODE_SETTINGS.get('批注原件', '修前原件/研究报告/甲方反馈/10.17/10.17研究报告.docx')
TARGET = ROOT/'研究报告/04_word/研究报告终稿.docx'
GOAL = REVIEW/'装配目标.docx'
REVISION_NAMES = {'ins', 'del', 'moveFrom', 'moveTo', 'moveFromRangeStart',
                  'moveFromRangeEnd', 'moveToRangeStart', 'moveToRangeEnd',
                  'cellIns', 'cellDel', 'cellMerge', 'numberingChange'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def active(root=ROOT):
    marker = review_dir(root)/'交付模式.json'
    return marker.exists() and json.loads(marker.read_text())['修订模式'] is False


def has_revisions(root):
    return [n for n in root.iter() if E.QName(n).namespace == NS['w'] and
            (E.QName(n).localname in REVISION_NAMES or E.QName(n).localname.endswith('Change'))]


def check_plain_document(root, settings, comment_ids):
    assert not has_revisions(root), '清稿仍有历史或新增修订'
    assert not settings.findall(qn('trackRevisions')), '清稿仍开启修订'
    for tag in ['commentRangeStart', 'commentRangeEnd', 'commentReference']:
        assert Counter(n.get(qn('id')) for n in root.findall('.//'+qn(tag))) == Counter(comment_ids), '批注锚点不完整：'+tag


def block_key(node, parts):
    if node.xpath('.//w:instrText[contains(text(),"PAGEREF")]', namespaces=NS):
        return 'toc:'+''.join(node.xpath('.//w:hyperlink//w:t/text()', namespaces=NS))
    return fingerprint(node, parts)


def stable_toc_anchors(goal, previous, headings):
    """删改表注会改变装配段号，已有目录的真实书签按标题保持稳定。"""
    def toc(tree):
        result={}
        for p in tree.xpath('.//w:body/w:p[.//w:instrText[contains(text(),"PAGEREF")]]', namespaces=NS):
            title=''.join(p.xpath('.//w:hyperlink//w:t/text()', namespaces=NS))
            alias=re.search(r'PAGEREF\s+(\w+)', ''.join(p.xpath('.//w:instrText/text()', namespaces=NS)))[1]
            result[title]=alias
        return result
    original=toc(previous);current=toc(goal)
    assert set(original)==set(current)=={title for title,level,alias in headings}, '目录标题发生未登记变化'
    remap={current[title]:original[title] for title in current}
    for node in goal.findall('.//'+qn('bookmarkStart')):
        name=node.get(qn('name'))
        if name in remap:node.set(qn('name'),remap[name])
    for node in goal.findall('.//'+qn('hyperlink')):
        name=node.get(qn('anchor'))
        if name in remap:node.set(qn('anchor'),remap[name])
    for node in goal.findall('.//'+qn('instrText')):
        if node.text:node.text=re.sub(r'(PAGEREF\s+)(\w+)',lambda m:m[1]+remap.get(m[2],m[2]),node.text)
    return [(title,level,original[title]) for title,level,alias in headings]


def anchor_comment(paragraph, ident):
    """批注保留在对应内容段落；已删除旧段落的批注迁移至现有对应内容。"""
    start, end, run = E.Element(qn('commentRangeStart')), E.Element(qn('commentRangeEnd')), E.Element(qn('r'))
    start.set(qn('id'), ident); end.set(qn('id'), ident)
    ref = E.SubElement(run, qn('commentReference')); ref.set(qn('id'), ident)
    paragraph.insert(1 if paragraph.find(qn('pPr')) is not None else 0, start)
    paragraph.extend([end, run])


def install_comments(parts, root, feedback):
    markers = {
        '0': '工程运行要求为：正常运行主变负载率不超过80%',
        '1': '其中，学者Zhu等对铜芯电缆',
        '2': '110 kV变电站',
        '3': '八义集变',
        '4': '2025年4月《配电网规划设计技术导则（修订稿）》第6.2.2条将负荷增长',
        '5': '负荷分散系数为各站最大正向净负荷之和',
        '6': '新增联络能力的取值依据邳州局部六条10 kV馈线',
        '7': '5.3.1 供电安全及供电能力约束',
        '8': '邳州逐年容量及措施',
        '9': '保留2021实际容量的代表年度汇总',
        '10': '电缆长度占比≤10%、负荷分散系数1.00的容载比分档建议矩阵',
    }
    comments = xml(feedback['word/comments.xml'])
    assert {c.get(qn('id')) for c in comments} == set(markers)
    paragraphs = root.findall('.//'+qn('p'))
    locations = []
    for ident, marker in markers.items():
        if ident in {'2', '3'}:
            tables = [t for t in root.findall('.//'+qn('tbl')) if text(t).startswith('地区110 kV变电站最大正向净负荷/MW')]
            assert len(tables) == 1, '批注所指110 kV站级净负荷表未唯一定位'
            candidates = [p for p in tables[0].findall('.//'+qn('p')) if text(p) == marker]
        else:
            candidates = [p for p in paragraphs if marker in text(p)]
        assert len(candidates) == 1, ('批注定位不唯一', ident, marker, len(candidates))
        paragraph = candidates[0]
        existing=[root.xpath('.//w:'+tag+'[@w:id="'+ident+'"]', namespaces=NS)
                  for tag in ['commentRangeStart','commentRangeEnd','commentReference']]
        retained=all(len(nodes)==1 and next(nodes[0].iterancestors(qn('p')), None) is paragraph for nodes in existing)
        if not retained:
            for nodes in existing:
                for node in nodes:
                    parent=node.getparent();parent.remove(node)
                    if parent.tag==qn('r') and not any(c.tag!=qn('rPr') for c in parent):parent.getparent().remove(parent)
            anchor_comment(paragraph, ident)
        locations.append({'批注ID': ident, '锚定正文': text(paragraph), '范围': '对应内容段落'})
    names = [n for n in feedback if 'comment' in n.lower() or n == 'word/people.xml']
    assert all(not n.endswith('.rels') for n in names), '批注存在额外关系依赖，须逐项处理'
    for name in names: parts[name] = feedback[name]
    rels = xml(parts['word/_rels/document.xml.rels'])
    source_rels = xml(feedback['word/_rels/document.xml.rels'])
    types = xml(parts['[Content_Types].xml'])
    source_types = xml(feedback['[Content_Types].xml'])
    nextid = max(int(n.get('Id')[3:]) for n in rels if re.fullmatch(r'rId\d+', n.get('Id')))+1
    for item in source_rels:
        if 'word/'+item.get('Target') not in names: continue
        if not any(n.get('Type') == item.get('Type') for n in rels):
            copy = deepcopy(item);copy.set('Id', 'rId'+str(nextid));nextid += 1;rels.append(copy)
    for item in source_types:
        if item.get('PartName', '').lstrip('/') not in names: continue
        for old in list(types):
            if old.get('PartName') == item.get('PartName'): types.remove(old)
        types.append(deepcopy(item))
    parts['word/_rels/document.xml.rels'] = dump(rels)
    parts['[Content_Types].xml'] = dump(types)
    return locations


def apply():
    assert active()
    GOAL.write_bytes(TARGET.read_bytes())
    original, candidate, feedback = package(BASE), package(GOAL), package(FEEDBACK)
    root, goal = xml(original['word/document.xml']), xml(candidate['word/document.xml'])
    assert not has_revisions(root) and not has_revisions(goal)
    headings_path=ROOT/'研究报告/05_review/当前版/目录标题.json'
    headings=stable_toc_anchors(goal,root,json.loads(headings_path.read_text()))
    write(headings_path,headings)
    candidate['word/document.xml']=dump(goal)
    with ZipFile(GOAL,'w',ZIP_DEFLATED) as z:
        for name,data in candidate.items():z.writestr(name,data)
    before, after = list(root.find(qn('body'))), list(goal.find(qn('body')))
    # 相同关系ID须保持同一对象；不以重建覆盖原有媒体、字体和样式。
    oldrels = {n.get('Id'): n for n in xml(original['word/_rels/document.xml.rels'])}
    newrels = {n.get('Id'): n for n in xml(candidate['word/_rels/document.xml.rels'])}
    for rid in goal.xpath('.//@r:embed|.//@r:id', namespaces={'r': R}):
        assert dict(oldrels[rid].attrib) == dict(newrels[rid].attrib)
        name = 'word/'+oldrels[rid].get('Target')
        if name in candidate: assert original[name] == candidate[name], '原有关系对象变化：'+name
    old_style_ids = set(xml(original['word/styles.xml']).xpath('./w:style/@w:styleId', namespaces=NS))
    assert set(goal.xpath('.//w:pStyle/@w:val|.//w:rStyle/@w:val|.//w:tblStyle/@w:val', namespaces=NS)) <= old_style_ids
    body = root.find(qn('body')); kept = changed = 0
    for child in list(body): body.remove(child)
    changes = []
    matcher = SequenceMatcher(None, [block_key(n, original) for n in before], [block_key(n, candidate) for n in after], autojunk=False)
    for op, i, j, a, b in matcher.get_opcodes():
        blocks = before[i:j] if op == 'equal' else after[a:b]
        if op == 'equal': kept += len(blocks)
        else:
            changed += len(blocks)
            changes.append({'类型': op, '原块': [text(n) for n in before[i:j]], '新块': [text(n) for n in after[a:b]]})
        for node in blocks: body.append(deepcopy(node))
    locations = install_comments(original, root, feedback)
    original['word/document.xml'] = dump(root)
    settings = xml(original['word/settings.xml'])
    for node in list(settings.findall(qn('trackRevisions'))): settings.remove(node)
    original['word/settings.xml'] = dump(settings)
    with ZipFile(TARGET, 'w', ZIP_DEFLATED) as z:
        for name, data in original.items(): z.writestr(name, data)
    write(REVIEW/'原版局部装配.json', {'基线': str(BASE.relative_to(ROOT)), '基线SHA256': sha(BASE),
          '批注来源': str(FEEDBACK.relative_to(ROOT)), '批注来源SHA256': sha(FEEDBACK),
          '保留原XML正文块': kept, '替换正文块': changed, '正文变化': changes, '批注锚点': locations,
          '装配目标SHA256': sha(GOAL), '首次局部装配SHA256': sha(TARGET),
          '说明': '正文以04_word上一轮清稿为基线；未涉及块及原媒体样式保持，11条批注原部件保留；全部历史修订已接受。'})
    return verify()


def verify(final=False):
    from report_annual_update import sync
    from verify_future_case_results import verify as future
    assert active()
    frozen, assets = future(ROOT), sync(check=True)
    parts, expected, old = package(TARGET), package(GOAL), package(BASE)
    root, goal = xml(parts['word/document.xml']), xml(expected['word/document.xml'])
    ids = [c.get(qn('id')) for c in xml(parts['word/comments.xml'])]
    check_plain_document(root, xml(parts['word/settings.xml']), ids)
    for name in parts:
        if name.startswith('word/') and name.endswith('.xml') and 'comment' not in name.lower():
            assert not has_revisions(xml(parts[name])), '包部件残留修订：'+name
    assert [block_key(n, parts) for n in root.find(qn('body'))] == [block_key(n, expected) for n in goal.find(qn('body'))], '正文、表格或图片未对应当前源稿'
    original_comments = package(FEEDBACK)
    for name in original_comments:
        if 'comment' in name.lower() or name == 'word/people.xml':
            assert parts[name] == original_comments[name], '批注部件变化：'+name
    record = json.loads((REVIEW/'原版局部装配.json').read_text())
    for attr in ['id', 'name']:
        values=[n.get(qn(attr)) for n in root.findall('.//'+qn('bookmarkStart'))]
        assert len(values)==len(set(values)), '书签属性重复：'+attr
    assert Counter(n.get(qn('id')) for n in root.findall('.//'+qn('bookmarkStart'))) == Counter(n.get(qn('id')) for n in root.findall('.//'+qn('bookmarkEnd'))), '书签范围不完整'
    for row in record['批注锚点']:
        node = root.xpath('.//w:commentRangeStart[@w:id="'+row['批注ID']+'"]', namespaces=NS)[0]
        assert text(node.getparent()) == row['锚定正文'], '批注与对应内容脱离'
    for name in old:
        if name.startswith('word/media/') or name == 'word/styles.xml':
            assert parts[name] == old[name], '未涉及图件或样式变化：'+name
    ns = {'m': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}
    math = lambda tree: [E.tostring(n, method='c14n') for n in tree.xpath('.//m:oMath', namespaces=ns)]
    # 源稿本轮无公式修改，原生OMML逐对象保留。
    assert math(root) == math(xml(old['word/document.xml'])), '原生公式变化'
    tables = json.loads((ROOT/'研究报告/02图表/当前版/计算表.json').read_text())
    previous = json.loads((REVIEW/'修前原件/研究报告/02图表/当前版/计算表.json').read_text())
    assert set(tables) == set(previous)
    assert {k for k in tables if tables[k] != previous[k]} <= {'forecast_load', 'forecast_pv'}
    verify_forecast_rows(previous, tables, MODE_SETTINGS.get('全市光伏单位换算系数', 1))
    sections = Path('研究报告/02图表/当前版/生成段落.json')
    assert (ROOT/sections).read_bytes() == (REVIEW/'修前原件'/sections).read_bytes(), '逐站生成分析变化'
    from report_math_layout import check_equation_layout
    doc = Document(TARGET); equations = check_equation_layout(doc)
    from check_report_policy import check_figure_paragraphs
    policy = json.loads((ROOT/'tools/report_policy.json').read_text())
    figures = check_figure_paragraphs(doc, policy, 41)
    result = {'状态': '通过', '阶段': 'final' if final else 'docx', 'WordSHA256': sha(TARGET),
              '修订节点': 0, '原批注数': len(ids), '批注部件及锚点': '全部保留并对应有效正文',
              '锁定案例': frozen, '数据': assets, '原生公式': len(equations), '表格': len(doc.tables), **figures}
    if final:
        proof = json.loads((REVIEW/'WPS版面核验.json').read_text())
        assert proof['状态'] == '通过'
        for key, digest in [('DOCX', 'DOCX_SHA256'), ('PDF', 'PDF_SHA256')]:
            assert sha(ROOT/proof[key]) == proof[digest], 'WPS输出变化后须重新核验'
        assert proof['DOCX_SHA256'] == sha(TARGET)
        result['WPS版面'] = proof
    write(REVIEW/(('final' if final else 'docx')+'独立核验.json'), result)
    return result


def verify_forecast_rows(previous, current, pv_scale=1):
    """全市列仅作已登记单位转换，区域预测、相对倍数及负荷数据逐格保持。"""
    from decimal import Decimal
    rows=lambda value:[[c.strip() for c in line.strip('|').split('|')]
                       for line in value.splitlines() if line.startswith('|')][2:]
    assert rows(previous['forecast_load'])==rows(current['forecast_load']), '负荷预测表数值变化'
    before,after=rows(previous['forecast_pv']),rows(current['forecast_pv'])
    assert len(before)==len(after)==11
    for a,b in zip(before,after):
        assert a[0]==b[0] and a[2:]==b[2:], '地区光伏预测或增长比例变化：'+a[0]
        assert Decimal(b[1])==Decimal(a[1])*Decimal(str(pv_scale)), '全市光伏单位转换不对应：'+a[0]


def verify_release():
    result = verify(final=True)
    release = json.loads((REVIEW/'交付登记.json').read_text())
    assert release['状态'] == '三阶段核验及逐段复核通过'
    for name, digest in release['当前文件SHA256'].items(): assert sha(ROOT/name) == digest, '交付文件变化：'+name
    link = json.loads((REVIEW/'上一版交付衔接.json').read_text())
    assert sha(ROOT/link['父交付登记']) == link['父交付登记SHA256']
    parent = json.loads((ROOT/link['父交付登记']).read_text())
    assert set(link['原件映射']) == set(parent['当前文件SHA256'])
    for name, digest in parent['当前文件SHA256'].items():
        row = link['原件映射'][name]
        assert row['SHA256'] == digest and sha(ROOT/row['path']) == digest, '上一版原件变化：'+name
    for name, item in release['历史定档原件'].items(): assert sha(ROOT/item['原件归档']) == item['原SHA256'], name
    from report_prose_review import collect
    current = collect(ROOT, include_discussion=False)
    reviewed = json.loads((REVIEW/'正文逐段复核.json').read_text())['正文段落']
    assert len(current) == len(reviewed)
    for old, now in zip(reviewed, current):
        assert old['位置'] == now['位置'] and old['SHA256'] == now['SHA256'], '逐段复核过期：'+now['位置']
        assert old['复核结论'] == '通过' and old['理由']
    facts = json.loads((REVIEW/'事实与历史措辞核对.json').read_text())
    assert facts['状态'] == '通过'
    for name, digest in facts['依据SHA256'].items(): assert sha(ROOT/name) == digest, '核读依据变化：'+name
    prior = ROOT/facts['继承引文核读']
    records = json.loads(prior.read_text())['记录']; assert len(records) == 95
    for row in records:
        for key, dk in [('审定依据', 'SHA256'), ('原始文件', '原始文件SHA256')]:
            if dk in row: assert sha(ROOT/row[key]) == row[dk]
    assert release['文字复核']['规则扫描代替逐段判断'] is False
    print(json.dumps({'状态': '通过', '正文复核': len(current), '历史原件衔接': len(parent['当前文件SHA256']),
                      '原批注': result['原批注数'], '历史及新增修订': 0}, ensure_ascii=False))
    return release


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False))
