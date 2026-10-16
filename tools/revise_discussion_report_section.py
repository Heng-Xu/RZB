"""在当前修订稿中完整复用报告3.5，保留此前修订、批注和其他内容。"""
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile
import json
import re

from lxml import etree as E
import revise_current_discussion as r
from revise_discussion_selection import reject_ids, revision_nodes, revision_identity

ROOT = r.ROOT
AUDIT = ROOT/'研究报告/05_review/当前版/1014讨论稿5.1与报告3.5一致'
BASELINE = AUDIT/'修前快照/研究报告/甲方反馈/10.11/供电公司讨论稿.docx'
STYLE_PREFIX = 'Report35_'


def package(path):
    with ZipFile(path) as z:
        return [(info, z.read(info.filename)) for info in z.infolist()]


def report_nodes():
    parts = dict((info.filename, data) for info, data in package(r.REPORT))
    body = r.xml(parts['word/document.xml']).find(r.qn('body'))
    nodes = list(body)
    start = next(i for i, n in enumerate(nodes) if r.text(n) == '3.5 核心参数依据与相关性分析')
    end = next(i for i in range(start+1, len(nodes)) if r.text(nodes[i]).startswith('3.6 '))
    refs = {int(m[1]): n for n in nodes if (m := re.match(r'^\[(\d+)\]', r.text(n)))}
    return nodes[start:end], refs, r.xml(parts['word/styles.xml'])


def citation_numbers(value):
    numbers = []
    for group in re.findall(r'\[([\d,、—–-]+)\]', value):
        for piece in re.split('[,、]', group):
            ends = re.split('[—–-]', piece)
            numbers += list(range(int(ends[0]), int(ends[1])+1)) if len(ends) == 2 else [int(piece)]
    return numbers


def citation_map(nodes):
    # 当前讨论稿已核验的五项依据，对应报告中的实际编号。
    mapping = {7: 1, 12: 2, 8: 3, 10: 4, 28: 5}
    for node in nodes:
        for number in citation_numbers(r.text(node)):
            if number not in mapping:
                mapping[number] = len(mapping)+1
    return mapping


def transform_text(value, mapping):
    def cite(match):
        return '['+','.join(str(mapping[n]) for n in citation_numbers(match[0]))+']'
    value = re.sub(r'\[([\d,、—–-]+)\]', cite, value)
    value = re.sub(r'^3\.5(?=\s|\.)', '5.1', value)
    value = re.sub(r'表3-(\d+)', lambda m: '表'+str(int(m[1])-3), value)
    # 报告章节/式号仍指向研究报告，避免在讨论稿中产生错误定位。
    value = value.replace('式（3-6）', '研究报告式（3-6）')
    value = re.sub(r'(?<!研究报告)第(3\.[346](?:[——–-]3\.[346])?(?:\.[\d]+)?|4\.[\d]+(?:\.[\d]+)?)节', r'研究报告第\1节', value)
    return value


def clean_copy(node, mapping):
    node = deepcopy(node)
    for bookmark in node.xpath('.//w:bookmarkStart|.//w:bookmarkEnd', namespaces=r.NS):
        bookmark.getparent().remove(bookmark)
    for el in node.iter():
        for attr in list(el.attrib):
            if E.QName(attr).localname in ['paraId', 'textId', 'rsidR', 'rsidRPr', 'rsidP', 'rsidRDefault']:
                del el.attrib[attr]
    for t in node.xpath('.//w:t', namespaces=r.NS):
        t.text = transform_text(t.text or '', mapping)
    for style in node.xpath('.//w:pStyle|.//w:rStyle|.//w:tblStyle', namespaces=r.NS):
        style.set(r.qn('val'), STYLE_PREFIX+style.get(r.qn('val')))
    return node


def copy_styles(original, source, nodes):
    result = deepcopy(original)
    available = {n.get(r.qn('styleId')): n for n in source.findall(r.qn('style'))}
    needed = {s.get(r.qn('val')).removeprefix(STYLE_PREFIX) for n in nodes
        for s in n.xpath('.//w:pStyle|.//w:rStyle|.//w:tblStyle', namespaces=r.NS)}
    done = set()
    while needed-done:
        key = sorted(needed-done)[0]
        done.add(key)
        node = deepcopy(available[key])
        node.set(r.qn('styleId'), STYLE_PREFIX+key)
        node.attrib.pop(r.qn('default'), None)
        name = node.find(r.qn('name'))
        if name is not None:
            name.set(r.qn('val'), '报告3.5 '+name.get(r.qn('val')))
        for link in node.xpath('./w:basedOn|./w:next|./w:link', namespaces=r.NS):
            old = link.get(r.qn('val'))
            needed.add(old)
            link.set(r.qn('val'), STYLE_PREFIX+old)
        result.append(node)
    return result, done


def mark_insert(node, revision):
    for row in node.findall(r.qn('tr')):
        pr = row.find(r.qn('trPr'))
        if pr is None:
            pr = E.Element(r.qn('trPr')); row.insert(0, pr)
        pr.append(revision.mark('ins'))
    paragraphs = [node] if node.tag == r.qn('p') else node.findall('.//'+r.qn('p'))
    for p in paragraphs:
        pr = p.find(r.qn('pPr'))
        if pr is None:
            pr = E.Element(r.qn('pPr')); p.insert(0, pr)
        rp = pr.find(r.qn('rPr'))
        if rp is None:
            rp = E.SubElement(pr, r.qn('rPr'))
        rp.append(revision.mark('ins'))
        for child in list(p):
            if child.tag == r.qn('pPr'):
                continue
            at = p.index(child); p.remove(child)
            ins = revision.mark('ins'); ins.append(child); p.insert(at, ins)
    return node


def delete_node(node, revision):
    if node.tag == r.qn('p'):
        revision.replace(node, '')
    elif node.tag == r.qn('tbl'):
        for row in node.findall(r.qn('tr')):
            if row.xpath('./w:trPr/w:del', namespaces=r.NS):
                continue
            pr = row.find(r.qn('trPr'))
            if pr is None:
                pr = E.Element(r.qn('trPr')); row.insert(0, pr)
            pr.append(revision.mark('del'))
            for p in row.findall('.//'+r.qn('p')):
                revision.replace(p, '')


def section_bounds(nodes):
    start = next(i for i, n in enumerate(nodes) if r.text(n).startswith('5.1 '))
    end = next(i for i in range(start+1, len(nodes)) if r.text(nodes[i]).startswith('5.2 '))
    return start, end


def expected():
    source, refs, styles = report_nodes()
    mapping = citation_map(source)
    return [clean_copy(n, mapping) for n in source], mapping, refs, styles


def apply():
    record_path = AUDIT/'修订核验.json'
    allowed = {r.sha(BASELINE)}
    if record_path.exists():
        previous = json.loads(record_path.read_text())
        allowed.add(previous['修后SHA256'])
    assert r.sha(r.TARGET) in allowed, '讨论稿有未核对的外部修改，禁止覆盖'
    original = package(BASELINE); parts = {i.filename: data for i, data in original}
    root = r.xml(parts['word/document.xml']); body = root.find(r.qn('body')); before = list(body)
    start, end = section_bounds(before)
    copied, mapping, refs, source_styles = expected()
    styles, style_keys = copy_styles(r.xml(parts['word/styles.xml']), source_styles, copied)
    revision = r.Reviser(root); old_ids = {n.get(r.qn('id')) for n in revision_nodes(root)}
    for node in before[start:end]:
        delete_node(node, revision)
    position = body.index(before[end])
    for node in copied:
        body.insert(position, mark_insert(node, revision)); position += 1
    # 复用范围新增六张表，原矩阵表10~15顺延为表16~21。
    touched = []
    for i, node in enumerate(before[end:], end):
        if node.tag != r.qn('p') or re.match(r'^\[\d+\]', r.text(node)):
            continue
        value = r.text(node)
        amended = re.sub(r'表(1[0-5])(?=\D|$)', lambda m: '表'+str(int(m[1])+6), value)
        if amended != value:
            revision.replace(node, amended); touched.append(i)
    template = next(n for n in before if r.text(n).startswith('[5] '))
    anchor = template
    for number, local in sorted(mapping.items(), key=lambda pair: pair[1]):
        if local <= 5:
            continue
        new_ref = deepcopy(refs[number])
        for mark in new_ref.xpath('.//w:bookmarkStart|.//w:bookmarkEnd', namespaces=r.NS):
            mark.getparent().remove(mark)
        values = new_ref.xpath('.//w:t', namespaces=r.NS)
        assert values and values[0].text.startswith(f'[{number}]')
        values[0].text = values[0].text.replace(f'[{number}]', f'[{local}]', 1)
        for style in new_ref.xpath('.//w:pStyle|.//w:rStyle', namespaces=r.NS):
            style.getparent().remove(style)
        new_ref = mark_insert(new_ref, revision)
        anchor.addnext(new_ref); anchor = new_ref
    settings = r.xml(parts['word/settings.xml'])
    track = settings.find(r.qn('trackRevisions'))
    if track is None: track = E.SubElement(settings, r.qn('trackRevisions'))
    track.set(r.qn('val'), 'true')
    core = r.xml(parts['docProps/core.xml'])
    for node in core:
        if E.QName(node).localname == 'lastModifiedBy': node.text = r.AUTHOR
        if E.QName(node).localname == 'modified': node.text = revision.date
    replaced = {'word/document.xml': r.serialize(root), 'word/settings.xml': r.serialize(settings),
        'word/styles.xml': r.serialize(styles), 'docProps/core.xml': r.serialize(core)}
    r.write_package(r.TARGET, original, replaced)
    ids = {n.get(r.qn('id')) for n in revision_nodes(root)}-old_ids
    record = {'状态': '待核验', '修前SHA256': r.sha(BASELINE), '修后SHA256': r.sha(r.TARGET),
        '基线': str(BASELINE.relative_to(ROOT)), '报告SHA256': r.sha(r.REPORT), '新修订作者': r.AUTHOR,
        '新修订时间': revision.date, '正常系统UTC时间': True, '新修订ID': sorted(ids, key=int),
        '替换节点范围': [start, end], '后续表号联动节点': touched, '报告引文至讨论稿引文': mapping,
        '复用报告节点数': len(copied), '复用报告表格数': 11, '仅修改包部件': list(replaced),
        '独立新增报告样式': sorted(style_keys)}
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    check()


def visible_blocks(root):
    return [(E.QName(n).localname, r.text(n), n.xpath('.//*[local-name()="oMath"]//*[local-name()="t"]/text()'))
        for n in r.accept_view(root).find(r.qn('body'))]


def strip_empty_properties(node):
    node = deepcopy(node)
    for p in node.xpath('.//w:pPr/w:rPr', namespaces=r.NS):
        if not len(p) and not p.attrib: p.getparent().remove(p)
    # 修订会拆分同格式文字run；比较可见内容与格式，不把拆分当作正文差异。
    for t in node.xpath('.//w:t', namespaces=r.NS):
        t.attrib.pop('{http://www.w3.org/XML/1998/namespace}space', None)
    for p in ([node] if node.tag == r.qn('p') else node.findall('.//'+r.qn('p'))):
        previous = None
        for child in list(p):
            plain = child.tag == r.qn('r') and all(n.tag in [r.qn('rPr'), r.qn('t')] for n in child)
            if not plain: previous = None; continue
            prop = lambda n: E.tostring(n.find(r.qn('rPr')), method='c14n', exclusive=True) if n.find(r.qn('rPr')) is not None else b''
            if previous is not None and prop(previous) == prop(child):
                text = ''.join(previous.xpath('./w:t/text()', namespaces=r.NS))+''.join(child.xpath('./w:t/text()', namespaces=r.NS))
                for t in list(previous.findall(r.qn('t'))): previous.remove(t)
                E.SubElement(previous, r.qn('t')).text = text
                p.remove(child)
            else: previous = child
    return node


def check():
    record = json.loads((AUDIT/'修订核验.json').read_text())
    # 用户本轮只修改研究报告，讨论稿继续对应其已审定的报告原件。
    from verify_report_release import RELEASE, AUDIT as report_audit
    if RELEASE.exists():
        preserved=report_audit/'修前快照/研究报告/04_word/研究报告终稿.docx'
        assert r.sha(preserved)==record['报告SHA256'],'讨论稿采用报告原件不一致'
        r.REPORT=preserved
    assert r.sha(r.TARGET) == record['修后SHA256'] and r.sha(r.REPORT) == record['报告SHA256']
    if '用户WPS保存核验' in record:
        return check_user_saved(record)
    old = {i.filename: data for i, data in package(BASELINE)}
    new = {i.filename: data for i, data in package(r.TARGET)}
    assert set(old) == set(new)
    for name in old:
        if name not in record['仅修改包部件']: assert old[name] == new[name], name
    before, after = r.xml(old['word/document.xml']), r.xml(new['word/document.xml'])
    prior = {revision_identity(n) for n in revision_nodes(before)}
    current = {revision_identity(n) for n in revision_nodes(after)}
    assert prior <= current, '已有修订作者、日期或ID变化'
    ids = set(record['新修订ID']); all_ids = []
    for n in revision_nodes(after):
        all_ids.append(n.get(r.qn('id')))
        if n.get(r.qn('id')) in ids:
            date = record.get('新修订时间映射', {}).get(n.get(r.qn('id')), record['新修订时间'])
            assert n.get(r.qn('author')) == r.AUTHOR and n.get(r.qn('date')) == date
    assert len(all_ids) == len(set(all_ids)), '修订ID重复'
    for kind in ['commentRangeStart', 'commentRangeEnd', 'commentReference']:
        assert before.xpath('.//w:'+kind+'/@w:id', namespaces=r.NS) == after.xpath('.//w:'+kind+'/@w:id', namespaces=r.NS)
    assert visible_blocks(reject_ids(after, ids)) == visible_blocks(before), '拒绝本轮修订不能恢复当前修前稿'
    previous_styles = r.xml(old['word/styles.xml']); styles = r.xml(new['word/styles.xml'])
    old_style_nodes = list(previous_styles)
    assert all(E.tostring(a) == E.tostring(b) for a, b in zip(old_style_nodes, list(styles))), '原有样式变化'
    final = r.accept_view(after); nodes = list(final.find(r.qn('body')))
    start, end = section_bounds(nodes); copied, mapping, refs, _ = expected()
    assert len(nodes[start:end]) == len(copied) == 49
    for i, (actual, reference) in enumerate(zip(nodes[start:end], copied)):
        canonical = lambda n: E.tostring(strip_empty_properties(n), method='c14n', exclusive=True)
        assert canonical(actual) == canonical(reference), ('与报告段落或表格不一致', i, r.text(reference)[:60])
    originals = list(before.find(r.qn('body')))
    a, b = record['替换节点范围']; touched = set(range(a, b))|set(record['后续表号联动节点'])
    for index, node in enumerate(originals):
        if index not in touched:
            # 所有原节点仍在包内，未涉及节点逐字节保留。
            assert any(E.tostring(n) == E.tostring(node) for n in after.find(r.qn('body'))), ('未涉及节点变化', index)
    bibliography = {int(m[1]): r.text(n) for n in nodes if (m := re.match(r'^\[(\d+)\]', r.text(n)))}
    for original, local in mapping.items():
        assert bibliography[local].removeprefix(f'[{local}]').strip() == r.text(refs[original]).removeprefix(f'[{original}]').strip(), ('引文依据错配', original, local)
    visible = '\n'.join(r.text(n) for n in nodes)
    from check_report_policy import body_policy_errors
    policy = json.loads((ROOT/'tools/report_policy.json').read_text())
    body_text = visible.split('参考依据')[0]
    assert not body_policy_errors([('供电公司讨论稿.docx最终视图', body_text)], {}, {}, policy['forbidden_body_patterns'])
    record.update(状态='原生修订与完整复用核验通过，待WPS版面检查', 保留原有修订=len(prior),
        新增修订=len(ids), 最终视图表格数=22, 复用原生行内公式=13, 批注及未涉及包部件='保持',
        拒绝本轮修订='恢复修前最终视图', 完整复用='49个节点，包括5个小节、11张表和13个行内OMML对象')
    proof_path = AUDIT/'WPS版面核验.json'
    if proof_path.exists() and json.loads(proof_path.read_text()).get('状态') == '通过':
        proof = json.loads(proof_path.read_text()); assert proof['状态'] == '通过'
        assert proof['DOCX_SHA256'] == r.sha(r.TARGET) and proof['PDF_SHA256'] == r.sha(ROOT/proof['PDF'])
        import pymupdf
        pdf = pymupdf.open(ROOT/proof['PDF']); norm = lambda s: re.sub(r'\s+', '', s or '')
        rendered = [(page.number+1, table.extract()) for page in pdf for table in page.find_tables().tables]
        tables = nodes and [n for n in nodes if n.tag == r.qn('tbl')]
        assert len(tables) == 22
        expected_rows = [[[norm(r.text(c)) for c in row.findall(r.qn('tc'))] for row in table.findall(r.qn('tr'))] for table in tables]
        flattened = [[norm(v) for v in row] for _, table in rendered for row in table]
        row_pages = [page for page, table in rendered for _ in table]
        captions = [r.text(n) for n in nodes if n.tag == r.qn('p') and re.match(r'^表\d+(?:[（(][ab][）)])?\s', r.text(n))]
        assert len(captions) == len(expected_rows)
        # 长相关矩阵可跨页重复表头，按实际序列逐行比对，保留全部中文表头。
        cursor = 0
        for caption, rows in zip(captions, expected_rows):
            assert norm(caption) in norm(pdf[row_pages[cursor]-1].get_text()), ('PDF表题与首行不在同页', caption)
            for i, row in enumerate(rows):
                if i and flattened[cursor] == rows[0]: cursor += 1
                assert flattened[cursor] == row, ('PDF表格不一致', cursor, row, flattened[cursor])
                cursor += 1
        assert cursor == len(flattened), 'PDF存在额外或未核对表格行'
        assert sum(len(page.get_image_info()) for page in pdf) == 4
        record.update(状态='原生修订、完整复用及WPS版面核验通过', PDF表格逐行核验='全部22表含跨页表头一致')
    (AUDIT/'修订核验.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    (AUDIT/'最终视图正文.txt').write_text(visible.rstrip()+'\n')
    print(json.dumps({k: record[k] for k in ['状态', '保留原有修订', '新增修订', '最终视图表格数', '完整复用']}, ensure_ascii=False))


def check_user_saved(record):
    """用户WPS保存会重编号及合并run，按已登记保存前后文件验证语义与历史删除内容。"""
    from collections import Counter, defaultdict
    proof = json.loads((ROOT/record['用户WPS保存核验']).read_text())
    before_path = ROOT/proof['保存前文件']; after_path = ROOT/proof['保存后文件']
    assert r.sha(before_path) == proof['保存前SHA256']
    assert r.sha(after_path) == proof['保存后SHA256'] == r.sha(r.TARGET)
    before_parts = {i.filename: data for i, data in package(before_path)}
    after_parts = {i.filename: data for i, data in package(r.TARGET)}
    before, after = r.xml(before_parts['word/document.xml']), r.xml(after_parts['word/document.xml'])
    def blocks(tree):
        return [(E.QName(n).localname, r.text(n), ''.join(n.xpath('.//*[local-name()="oMath"]//*[local-name()="t"]/text()')))
            for n in r.accept_view(tree).find(r.qn('body')) if r.text(n) or n.tag in [r.qn('tbl'), r.qn('sectPr')]
            or n.xpath('.//*[local-name()="drawing"]')]
    assert blocks(before) == blocks(after), '用户保存后出现未核对的正文变化'
    for name in before_parts:
        if name == 'word/comments.xml' or name.startswith('word/media/'):
            assert before_parts[name] == after_parts[name], '保存后批注或图件变化: '+name
    def deleted_chars(tree):
        result = defaultdict(Counter)
        for node in tree.xpath('.//w:del', namespaces=r.NS):
            result[node.get(r.qn('author'))].update(''.join(node.xpath('.//w:delText/text()', namespaces=r.NS)))
        return result
    assert deleted_chars(before) == deleted_chars(after), '保存后历史删除内容变化'
    nodes = list(r.accept_view(after).find(r.qn('body'))); start, end = section_bounds(nodes)
    copied, mapping, refs, _ = expected()
    signature = lambda n: (E.QName(n).localname, r.text(n), ''.join(n.xpath('.//*[local-name()="oMath"]//*[local-name()="t"]/text()')))
    assert len(nodes[start:end]) == len(copied) == 49
    assert [signature(n) for n in nodes[start:end]] == [signature(n) for n in copied], '完整复用正文、表格或公式变化'
    bibliography = {int(m[1]): r.text(n) for n in nodes if (m := re.match(r'^\[(\d+)\]', r.text(n)))}
    for original, local in mapping.items():
        assert bibliography[local].removeprefix(f'[{local}]').strip() == r.text(refs[original]).removeprefix(f'[{original}]').strip()
    visible = '\n'.join(r.text(n) for n in nodes)
    from check_report_policy import body_policy_errors
    policy = json.loads((ROOT/'tools/report_policy.json').read_text())
    assert not body_policy_errors([('供电公司讨论稿.docx最终视图', visible.split('参考依据')[0])], {}, {}, policy['forbidden_body_patterns'])
    record.update(状态='用户保存语义、完整复用核验通过，待WPS', 用户保存后修订数=len(revision_nodes(after)))
    p = AUDIT/'WPS版面核验.json'
    if p.exists() and json.loads(p.read_text()).get('状态') == '通过':
        render = json.loads(p.read_text()); assert render['DOCX_SHA256'] == r.sha(r.TARGET)
        assert render['PDF_SHA256'] == r.sha(ROOT/render['PDF'])
        import pymupdf
        pdf = pymupdf.open(ROOT/render['PDF']); norm = lambda s: re.sub(r'\s+', '', s or '')
        rendered = [(page.number+1, t.extract()) for page in pdf for t in page.find_tables().tables]
        flat = [[norm(v) for v in row] for _, t in rendered for row in t]
        pages = [page for page, t in rendered for _ in t]
        tables = [n for n in nodes if n.tag == r.qn('tbl')]
        captions = [r.text(n) for n in nodes if n.tag == r.qn('p') and re.match(r'^表\d+(?:[（(][ab][）)])?\s', r.text(n))]
        assert len(tables) == len(captions) == 22
        cursor = 0
        for caption, table in zip(captions, tables):
            rows = [[norm(r.text(c)) for c in row.findall(r.qn('tc'))] for row in table.findall(r.qn('tr'))]
            assert norm(caption) in norm(pdf[pages[cursor]-1].get_text()), ('表题分页', caption)
            for i, row in enumerate(rows):
                if i and flat[cursor] == rows[0]: cursor += 1
                assert flat[cursor] == row; cursor += 1
        assert cursor == len(flat) and sum(len(page.get_image_info()) for page in pdf) == 4
        record.update(状态='用户保存语义、完整复用及WPS版面核验通过')
    (AUDIT/'修订核验.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    (AUDIT/'最终视图正文.txt').write_text(visible.rstrip()+'\n')
    print(json.dumps({k:record[k] for k in ['状态','用户保存后修订数','最终视图表格数','完整复用']}, ensure_ascii=False))


if __name__ == '__main__':
    check()
