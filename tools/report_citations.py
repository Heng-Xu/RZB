"""按首次引用编排，并独立核验源稿、原生Word及WPS PDF的文献对应。"""
from pathlib import Path
import json
import re

MARK = r'\[([0-9]+(?:\s*[—–－,，、-]\s*[0-9]+)*)\]'
CLUSTER = r'(?:' + MARK + r'\s*)+'


def typography(value):
    """仅归一排版器的空白及智能引号，保留标题、版本、数字和作者。"""
    return re.sub(r'\s+', '', value).translate(str.maketrans({'“':'"','”':'"','‘':"'",'’':"'"}))


def numbers(value):
    result = []
    for part in re.split(r'[,，、]', value):
        ends = re.split(r'[—–－-]', part)
        lo, hi = int(ends[0]), int(ends[-1])
        assert lo <= hi, '引文范围倒置：' + value
        result.extend(range(lo, hi + 1))
    return result


def stream(value):
    return [numbers(m[1]) for m in re.finditer(MARK, value)]


def arrange(body, registry):
    order = []
    for group in stream(body):
        for number in group:
            assert number in registry, f'正文引文[{number}]缺少文献登记'
            if number not in order:
                order.append(number)
    mapping = {old: new for new, old in enumerate(order, 1)}

    def replace(match):
        # 相邻标注为同一引用簇；映射后升序排列，重复来源只列一次。
        cited = sorted({mapping[n] for group in stream(match[0]) for n in group})
        tail = re.search(r'\s*$', match[0])[0]
        return '[' + ','.join(map(str, cited)) + ']' + tail

    text = re.sub(CLUSTER, replace, body)
    entries = [registry[n] for n in order]
    assert len(entries) == len(set(entries)), '同一文献登记为多个来源编号'
    refs = '# 参考文献\n\n' + '\n\n'.join(f'[{i}] {entry}' for i, entry in enumerate(entries, 1)) + '\n'
    records = [dict(原编号=n, 新编号=mapping[n], 条目=registry[n]) for n in order]
    validate(text, entries)
    return text, refs, records


def validate(body, entries):
    groups = stream(body)
    seen = []
    for group in groups:
        assert group == sorted(set(group)), '同一处引文须升序且无重复：' + str(group)
        for n in group:
            assert 1 <= n <= len(entries), f'引文[{n}]无对应条目'
            if n not in seen:
                seen.append(n)
    assert seen == list(range(1, len(entries) + 1)), '首次引用次序或正文与文献条目对应错误'
    assert len(set(entries)) == len(entries), '文末存在重复著录'
    return groups


def verify(root, stage):
    review = root/'研究报告/05_review/当前版'
    asset = root/'研究报告/02图表/当前版'
    sources = sorted((root/'研究报告/03_MD/当前版').glob('0[1-6] *.md'))
    sections = json.loads((asset/'生成段落.json').read_text())
    tables = json.loads((asset/'计算表.json').read_text())
    raw = '\n\n'.join(p.read_text().strip() for p in sources)
    raw = re.sub(r'\[\[SECTION:([^\]]+)\]\]', lambda m: sections[m[1]], raw)
    raw = re.sub(r'\[\[TABLE:([^\]]+)\]\]', lambda m: tables[m[1]], raw)
    registry = {int(k): v for k, v in json.loads((review/'文献原编号登记.json').read_text()).items()}
    for p in sources:
        for line_no,line in enumerate(p.read_text().splitlines(),1):
            for group in stream(line):
                for n in group:
                    assert n in registry, f'{p.relative_to(root)}:{line_no}: 引文[{n}]无来源登记'
    expected, refs, records = arrange(raw, registry)
    groups = stream(expected)
    if stage != 'source':
        assembled = (root/'研究报告/03_MD/当前版/研究报告装配稿.md').read_text()
        body, bibliography = assembled.split('# 参考文献\n', 1)
        assert stream(body) == groups, '装配稿引文与六章源不一致'
        assert '# 参考文献\n' + bibliography == refs, '装配稿文末著录或序号不一致'
        assert json.loads((review/'引文顺序与对应.json').read_text()) == records, '引文映射未同步'
        from docx import Document
        doc = Document(root/'研究报告/04_word/研究报告终稿.docx')
        paragraphs = [p.text for p in doc.paragraphs]
        cut = paragraphs.index('参考文献')
        # 正文表格也可能带引文；按XML文档顺序读取，避开目录域。
        from docx.oxml.ns import qn
        blocks = []
        for block in doc.element.body:
            text = ''.join(block.xpath('.//w:t/text()'))
            if text == '参考文献':
                break
            blocks.append(text)
        assert stream('\n'.join(blocks)) == groups, '原生Word正文引文次序不同'
        actual = [p for p in paragraphs[cut+1:] if p.strip()]
        wanted = [f'[{r["新编号"]}] {r["条目"]}' for r in records]
        assert list(map(typography, actual)) == list(map(typography, wanted)), '原生Word文献条目与正文映射不一致'
    if stage == 'final':
        import pymupdf
        with pymupdf.open(root/'研究报告/04_word/研究报告终稿.pdf') as pdf:
            texts = '\n'.join(p.get_text(clip=pymupdf.Rect(0,55,p.rect.width,p.rect.height-55)) for p in pdf)
        # WPS可在数字和逗号处换行；先消除空白再按参考文献标题分段。
        compact = re.sub(r'\s+', '', texts)
        cut = compact.rfind('参考文献')
        assert cut >= 0
        pdf_body, pdf_refs = compact[:cut], compact[cut+4:]
        assert stream(pdf_body) == groups, 'WPS PDF引文标注与Word不一致'
        pdf_refs = typography(pdf_refs)
        labels = [int(m[1]) for m in re.finditer(r'\[(\d{1,3})\]', pdf_refs)]
        assert labels == list(range(1,len(records)+1)), 'WPS PDF文末序号缺项、重复或顺序不一致'
        for record in records:
            label = f'[{record["新编号"]}]' + typography(record['条目'])
            assert label in pdf_refs, f'WPS PDF文献[{record["新编号"]}]缺项或著录错误'
    result = dict(状态='通过', 阶段=stage, 文献数=len(records), 引用标注数=len(groups),
                  编排='首次引用连续编号；同处升序去重；重复引用同号；正文和文末逐条对应')
    (review/f'{stage}引文一致性核验.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return result
