"""在当前讨论稿上增量修订十三项筛选及五参数矩阵，保留全部已有历史。"""
from copy import deepcopy
from pathlib import Path
from datetime import datetime, timezone
from zipfile import ZipFile
import hashlib
import json
import re

from lxml import etree as E
import revise_current_discussion as r
from discussion_expansion import table_like_report, verify_figures

ROOT = r.ROOT
AUDIT = ROOT/'研究报告/05_review/当前版/1014十三选五与报告修订/讨论稿'
BASELINE = ROOT/'研究报告/05_review/当前版/1014十三选五与报告修订/修前快照/研究报告/甲方反馈/10.11/供电公司讨论稿.docx'
REV_TAGS = ['ins', 'del', 'tblPrChange', 'tblGridChange', 'trPrChange', 'pPrChange', 'rPrChange']


def revision_nodes(root):
    return root.xpath('|'.join('.//w:'+tag for tag in REV_TAGS), namespaces=r.NS)


def revision_identity(node):
    return node.tag, node.get(r.qn('id')), node.get(r.qn('author')), node.get(r.qn('date'))


def reject_ids(root, ids):
    """只拒绝本轮ID，保留此前所有作者、日期及已有修订状态。"""
    result = deepcopy(root)
    belongs = lambda x: x.get(r.qn('id')) in ids
    for p in list(result.xpath('.//w:p[w:pPr/w:rPr/w:ins]', namespaces=r.NS)):
        if any(belongs(x) for x in p.xpath('./w:pPr/w:rPr/w:ins', namespaces=r.NS)):
            p.getparent().remove(p)
    for row in list(result.xpath('.//w:tr[w:trPr/w:ins]', namespaces=r.NS)):
        if any(belongs(x) for x in row.xpath('./w:trPr/w:ins', namespaces=r.NS)):
            row.getparent().remove(row)
    for table in list(result.xpath('.//w:tbl[not(w:tr)]', namespaces=r.NS)):
        table.getparent().remove(table)
    for node in list(revision_nodes(result)):
        if not belongs(node) or node.getparent() is None:
            continue
        parent = node.getparent()
        if E.QName(node).localname == 'del':
            position = parent.index(node)
            for child in list(node):
                for value in child.xpath('.//w:delText', namespaces=r.NS):
                    value.tag = r.qn('t')
                parent.insert(position, child)
                position += 1
        parent.remove(node)
    return result


def clean_template(node):
    result = deepcopy(node)
    for change in revision_nodes(result):
        if change.getparent() is not None:
            change.getparent().remove(change)
    return result


def expected_spec():
    t, _ = r.assets()
    with ZipFile(BASELINE) as book:
        body = r.xml(book.read('word/document.xml')).find(r.qn('body'))
    before = list(body)
    assert r.text(before[68]).startswith('5.1 六项参数')
    changes = {
        68: '5.1 十三项候选指标与两层参数筛选',
        69: '2025年4月《配电网规划设计技术导则（修订稿）》第6.2.2条将负荷增长、负荷分散和转移能力列为容载比影响因素，第7.4.2.2条要求校核新能源反向承载并比选增容与储能[1]。据此建立十三项候选指标，先评价其与容载比的关联，再归并信息重叠较多的指标，确定五项推广参数。（研究报告第3.5节）',
        74: '除装机、增长率、电缆占比、初始转供率和负荷分散系数外，候选指标还包括电量渗透率、站级负载率最大值、最大正反向净负荷、95%峰值持续时间、储能支撑持续时间及两项单位功率投资比，共十三项。电量渗透率为同范围发电量与用电量之比，负载率按站级净负荷绝对峰值及初始有功容量计算，功率极值单位MW，两个时间指标单位h，投资比为主变单位有功容量投资与线路有效转供或储能有效支撑功率投资之比，均无量纲。（研究报告第3.3节、第3.4节、第4.5.4节）',
        75: r.text(before[75]).replace('（6）', '（5）'),
        76: '表5 五项推广参数的采样节点与矩阵分类',
        78: '源荷、网络与支撑条件的34686个组合中有32112个有效配置，电量、峰段和相对价格的97548个组合中有90420个有效配置，覆盖888种网络及负荷背景。基础输入固定其余五项，电量、峰段及价格固定其余八项独立输入，对每组至少两个有效节点去组均值后汇总Pearson，节点等权并保留零容量响应组。以组内相关绝对值不低于0.40进行第一层筛选，再以参数间相关绝对值不低于0.70识别信息重叠，同组优先保留基础规划输入参数。阈值用于本研究的推广维度归纳，统计对象为有效仿真情景。',
        79: '表6 十三项指标与容载比的组内相关',
        81: '第一层有九项指标达到相关强度要求。95%峰值持续时间、储能支撑持续时间及两项投资比的相关绝对值为0.16～0.27，作为设备定容或费用条件参与比选。装机、电量、反向净负荷及站级负载率的相关为0.88～0.92，联系反向承载需求；增长率和初始转供率分别为－0.80、－0.74，联系负荷分母及网络支援；电缆占比和分散系数为0.45、0.52，分别保留联络造价及局部峰值任务的信息。',
        82: '表8 五项推广参数的Pearson相关矩阵',
        84: 'ηC、ḡ、α、r₀、KD依次表示装机渗透率、年最大净负荷平均增长率、电缆长度占比、初始转供率和负荷分散系数。五项最大参数间Pearson绝对值为0.29，Spearman最大绝对值为0.26，VIF为1.00～1.12，线性信息重叠较少。五项分别描述电源规模、负荷发展、线路经济条件、既有网络支援和局部峰值分布，作为主矩阵查表参数。',
        86: '五站模板每站初始两台50 MVA主变，区域基期网供峰值250 MW，开展基期后第4年的静态比选。32112个有效设备配置按电缆三档和分散系数1.00、1.10、1.15组织为9张五参数矩阵、432个单元，容载比总体范围1.36～3.15。各单元采用统一工程价格、日间负荷系数0.30和光伏出力系数0.75，归纳2、4、6 h支撑条件下的容载比范围。（研究报告第5.6节）',
        87: '表10～表14列示五参数矩阵的典型条件。以表10为基准，表11、表12改变电缆长度占比，表13、表14改变负荷分散系数，各表按平均增长率和装机渗透率选行，按初始转供率四档选列。储能规模再按片区功率缺口及连续支撑过程核定。',
        88: '表10 电缆长度占比>30%、负荷分散系数1.10时的容载比区间',
        90: '表11 电缆长度占比≤10%、负荷分散系数1.10时的容载比区间',
        92: '表12 电缆长度占比(10%,30%]、负荷分散系数1.10时的容载比区间',
        98: '表13 电缆长度占比>30%、负荷分散系数1.00时的容载比区间',
        100: '表14 电缆长度占比>30%、负荷分散系数1.15时的容载比区间',
        116: '表10中，装机渗透率≤1、平均增长率处于(4%,7%]时，初始转供率由≤30%档提高至>70%档，容载比区间由1.98～2.10降至1.52～1.78。较强的既有网络支援可利用邻站余量，减少部分本地主变需求。',
        126: '（3）查找对应单元。先按电缆长度占比和负荷分散系数确定矩阵，再按年最大净负荷平均增长率、装机渗透率及初始转供率查找容量区间。',
    }
    # 当前文件中的指定句若已被甲方删去，保持其现有最终视图。
    phrase = '，两项分母分别采用典型场景和样本外推估计'
    if phrase in r.text(before[17]):
        changes[17] = r.text(before[17]).replace(phrase, '')
    tables = {77: r.md_rows(t['new_parameter_bins']), 80: r.md_rows(t['current_controlled_correlations']),
        83: r.md_rows(t['current_input_correlations'])}
    for index, key in [(89, 'current_matrix_2_1.10'), (91, 'current_matrix_0_1.10'),
                       (93, 'current_matrix_1_1.10'), (99, 'current_matrix_2_1.00'), (101, 'current_matrix_2_1.15')]:
        tables[index] = r.md_rows(t[key])
    additions = {
        81: [('caption', '表7 高相关指标归并及代表参数'), ('table', r.md_rows(t['parameter_redundancy_groups'])),
            ('p', '电量渗透率、反向净负荷和站级负载率与装机渗透率的相关分别为0.92、0.89、0.78，采用直接描述接入规模的装机参数作为代表。正向净负荷与增长率的相关接近1.00，与目标时点峰值250(1+ḡ)⁴的计算关系一致，采用能够描述发展阶段的增长率作为代表。两层分析由十三项得到九项，再归纳为五项，电量及功率信息继续用于源荷场景和站级校核。')],
        84: [('caption', '表9 五项推广参数的共线性核验'), ('table', r.md_rows(t['five_parameter_vif']))],
    }
    deleted = [94, 95, 96, 97]
    return changes, tables, additions, deleted


def apply():
    AUDIT.mkdir(parents=True, exist_ok=True)
    assert r.sha(r.TARGET) == r.sha(BASELINE), '当前讨论稿已变化，须检查增量基线后再修改'
    with ZipFile(r.TARGET) as book:
        original = [(i, book.read(i.filename)) for i in book.infolist()]
    parts = {i.filename: data for i, data in original}
    root = r.xml(parts['word/document.xml'])
    elements = list(root.find(r.qn('body')))
    revision = r.Reviser(root)
    old_ids = {x.get(r.qn('id')) for x in revision_nodes(root)}
    changes, tables, additions, deleted = expected_spec()
    log = []
    for index, value in changes.items():
        paragraph = elements[index]
        old = r.text(paragraph)
        revision.replace(paragraph, value)
        log.append({'节点': index, '原文': old, '新文': value})
    for index in deleted:
        el = elements[index]
        if el.tag == r.qn('p'):
            revision.replace(el, '')
        else:
            for row in el.findall(r.qn('tr')):
                if row.xpath('./w:trPr/w:del', namespaces=r.NS):
                    continue
                pr = row.find(r.qn('trPr'))
                if pr is None:
                    pr = E.Element(r.qn('trPr'))
                    row.insert(0, pr)
                pr.append(revision.mark('del'))
                for p in row.findall('.//'+r.qn('p')):
                    revision.replace(p, '')
    # 旧表整体按行删除并在原处插入新表，保留旧属性修订及旧ID。
    for index, values in tables.items():
        old_table = elements[index]
        for row in old_table.findall(r.qn('tr')):
            if row.xpath('./w:trPr/w:del', namespaces=r.NS):
                continue
            pr = row.find(r.qn('trPr'))
            if pr is None:
                pr = E.Element(r.qn('trPr'))
                row.insert(0, pr)
            pr.append(revision.mark('del'))
            for p in row.findall('.//'+r.qn('p')):
                revision.replace(p, '')
        old_table.addnext(revision.new_table(old_table, values))
    for index, items in additions.items():
        anchor = elements[index]
        for kind, value in items:
            if kind == 'table':
                node = revision.new_table(elements[77], value)
            else:
                template = clean_template(elements[76] if kind == 'caption' else elements[81])
                node = revision.new_paragraph(template, value, kind)
            anchor.addnext(node)
            anchor = node
    new_ids = {x.get(r.qn('id')) for x in revision_nodes(root)}-old_ids
    settings = r.xml(parts['word/settings.xml'])
    track = settings.find(r.qn('trackRevisions'))
    if track is None:
        track = E.SubElement(settings, r.qn('trackRevisions'))
    track.set(r.qn('val'), 'true')
    core = r.xml(parts['docProps/core.xml'])
    namespaces = {'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties', 'dcterms': 'http://purl.org/dc/terms/'}
    core.find('cp:lastModifiedBy', namespaces).text = r.AUTHOR
    core.find('dcterms:modified', namespaces).text = revision.date
    replaced = {'word/document.xml': r.serialize(root), 'word/settings.xml': r.serialize(settings), 'docProps/core.xml': r.serialize(core)}
    record = {'状态': '待原生与版面检查', '基线': str(BASELINE.relative_to(ROOT)), '修前SHA256': r.sha(BASELINE),
        '新修订作者': r.AUTHOR, '新修订时间': revision.date, '正常系统UTC时间': True, '新修订ID': sorted(new_ids, key=int),
        '修改段落': log, '替换表格': list(tables), '删除时间条件矩阵节点': deleted,
        '仅修改包部件': list(replaced), '讨论稿新增表格来源': '研究报告当前已装配表格或同列数模板'}
    r.write_package(r.TARGET, original, replaced)
    record['修后SHA256'] = r.sha(r.TARGET)
    (AUDIT/'修订核验.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    check()


def check():
    record = json.loads((AUDIT/'修订核验.json').read_text())
    assert r.sha(r.TARGET) == record['修后SHA256']
    with ZipFile(BASELINE) as book:
        old = {name: book.read(name) for name in book.namelist()}
    with ZipFile(r.TARGET) as book:
        new = {name: book.read(name) for name in book.namelist()}
    assert set(old) == set(new)
    for name in old:
        if name not in record['仅修改包部件']:
            assert old[name] == new[name], '未涉及包部件变化:'+name
    before, after = r.xml(old['word/document.xml']), r.xml(new['word/document.xml'])
    prior = {revision_identity(n) for n in revision_nodes(before)}
    current = {revision_identity(n) for n in revision_nodes(after)}
    assert prior <= current, '已有修订作者、ID或日期变化'
    ids = set(record['新修订ID'])
    for node in revision_nodes(after):
        if node.get(r.qn('id')) in ids:
            assert node.get(r.qn('author')) == r.AUTHOR and node.get(r.qn('date')) == record['新修订时间']
    revision_ids = [n.get(r.qn('id')) for n in revision_nodes(after)]
    assert len(revision_ids) == len(set(revision_ids)), '修订ID重复'
    for kind in ['commentRangeStart', 'commentRangeEnd', 'commentReference']:
        assert before.xpath('.//w:'+kind+'/@w:id', namespaces=r.NS) == after.xpath('.//w:'+kind+'/@w:id', namespaces=r.NS)
    recovered = r.accept_view(reject_ids(after, ids))
    original_visible = r.accept_view(before)
    content = lambda tree: [(E.QName(n).localname, r.text(n)) for n in tree.find(r.qn('body'))]
    assert content(recovered) == content(original_visible), '拒绝本轮修订后与本轮前最终视图不同'
    changes, tables, additions, deleted = expected_spec()
    touched = set(changes)|set(tables)|set(additions)|set(deleted)
    after_elements = list(after.find(r.qn('body')))
    cursor = unchanged = 0
    for i, node in enumerate(before.find(r.qn('body'))):
        if i in touched:
            cursor += 1+(1 if i in tables else 0)+len(additions.get(i, []))
            continue
        assert E.tostring(node) == E.tostring(after_elements[cursor]), ('未涉及节点变化', i)
        cursor += 1
        unchanged += 1
    final = r.accept_view(after)
    body = final.find(r.qn('body'))
    visible = '\n'.join(r.text(p) for p in body.findall(r.qn('p')))
    assert '两项分母分别采用典型场景和样本外推估计' not in visible
    for stale in ['六项参数', '六参数', '27张', '1296个']:
        assert stale not in visible, stale
    from check_report_policy import body_policy_errors
    policy = json.loads((ROOT/'tools/report_policy.json').read_text())
    assert not body_policy_errors([('供电公司讨论稿.docx', visible)], {}, {}, policy['forbidden_body_patterns'])
    expected_tables = []
    old_elements = list(before.find(r.qn('body')))
    for i, node in enumerate(old_elements):
        if i in tables:
            expected_tables.append(tables[i])
        elif node.tag == r.qn('tbl') and i not in deleted:
            active = r.accept_view(node)
            rows = active.findall(r.qn('tr'))
            if rows:
                expected_tables.append([[r.text(c) for c in row.findall(r.qn('tc'))] for row in rows])
        expected_tables.extend(value for kind, value in additions.get(i, []) if kind == 'table')
    actual = body.findall(r.qn('tbl'))
    assert len(actual) == len(expected_tables) == 15
    for number, (tbl, values) in enumerate(zip(actual, expected_tables), 1):
        shown = [[r.text(c) for c in row.findall(r.qn('tc'))] for row in tbl.findall(r.qn('tr'))]
        assert shown == [[v.replace('\n', '') for v in row] for row in values], ('表值不一致', number)
        if number in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
            reference = table_like_report(values, r.REPORT)
            for prop in ['tblPr', 'tblGrid']:
                assert E.tostring(tbl.find(r.qn(prop)), method='c14n', exclusive=True) == E.tostring(reference.find(r.qn(prop)), method='c14n', exclusive=True), (number, prop)
            for cell, ref in zip(tbl.findall('.//'+r.qn('tc')), reference.findall('.//'+r.qn('tc'))):
                for xpath in ['w:tcPr', 'w:p/w:pPr', 'w:p//w:rPr']:
                    clean = lambda e: [E.tostring(n, method='c14n', exclusive=True) for n in e.xpath(xpath, namespaces=r.NS)]
                    assert clean(cell) == clean(ref), (number, xpath)
    verify_figures(ROOT, ROOT/'研究报告/05_review/当前版/1013讨论稿扩充', new)
    # 所有删除表行均删除其可见文字，原矩阵文字不会残留最终视图。
    for row in after.xpath('.//w:tr[w:trPr/w:del]', namespaces=r.NS):
        assert not row.xpath('.//w:t[not(ancestor::w:del)]', namespaces=r.NS)
    record.update(状态='原生修订核验通过，待WPS版面检查', 保留原有修订=len(prior), 新增修订=len(ids),
        未涉及原节点保持=unchanged, 最终视图表格数=len(actual), 研究报告SHA256=r.sha(r.REPORT),
        批注及原始包部件='保持', 拒绝本轮修订='恢复本轮前最终视图')
    proof = AUDIT/'WPS版面核验.json'
    if proof.exists():
        evidence = json.loads(proof.read_text())
        assert evidence['DOCX_SHA256'] == r.sha(r.TARGET)
        assert evidence['PDF_SHA256'] == r.sha(ROOT/evidence['PDF'])
        assert evidence['状态'] == '通过'
        record['状态'] = '原生修订及WPS版面核验通过'
    (AUDIT/'修订核验.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    (AUDIT/'最终视图正文.txt').write_text(visible+'\n')
    print(json.dumps({key: record[key] for key in ['状态', '保留原有修订', '新增修订', '未涉及原节点保持', '最终视图表格数']}, ensure_ascii=False))


if __name__ == '__main__':
    check()
