"""从六章正文、四项复算附录和书目生成本轮 Word/PDF 成品。"""

import hashlib
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Cm, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / '研究报告/03_MD'
OUT = ROOT / '研究报告/04_word'
QA = ROOT / '研究报告/05_review/2026-09-29重构'
CHAPTERS = sorted(SRC.glob('[0-9][0-9] *.md'))
APPENDICES = [SRC / f'附录{x} {title}.md' for x, title in [
    ('A', '原始资料与指标复算'), ('B', '逐站年度措施'),
    ('C', '条件矩阵与敏感性'), ('D', '联络与转供明细')]]
BIB = SRC / '参考文献.md'
ASSEMBLED = SRC / '研究报告装配稿.md'
DOCX = OUT / '研究报告终稿.docx'
PDF = OUT / '研究报告终稿.pdf'
PREVIEW = Path('/tmp/xuzhou_report_print_preview.html')
TEMPLATE = ROOT / '研究报告/中期研究报告初稿/03+XX项目-研究报告.docx'


def run(*args, **kwargs):
    result = subprocess.run(args, text=True, capture_output=True, **kwargs)
    if result.returncode:
        raise RuntimeError(f'{args}\n{result.stderr[-4000:]}')
    return result


def main():
    assert len(CHAPTERS) == 6, CHAPTERS
    assert all(x.exists() for x in APPENDICES)
    OUT.mkdir(exist_ok=True); QA.mkdir(parents=True, exist_ok=True)
    inputs = CHAPTERS + [BIB] + APPENDICES
    parts = [
        '---\n',
        'title: 徐州地区分布式新能源高渗透率地区110 kV电网容载比弹性指标优化研究\n',
        'subtitle: 研究报告\n',
        'author: 国网江苏电力设计咨询有限公司\n',
        'date: 2026年9月\n',
        'lang: zh-CN\n',
        '---\n\n',
    ]
    for path in inputs:
        parts.append(path.read_text(encoding='utf-8').rstrip() + '\n\n')
    ASSEMBLED.write_text(''.join(parts).rstrip() + '\n', encoding='utf-8')
    export_md = Path('/tmp/xuzhou_report_word_compatible.md')
    export_md.write_text(
        re.sub(r'\\tag\{([^}]+)\}', lambda m: r'\qquad\text{(' + m.group(1) + ')}',
               ASSEMBLED.read_text(encoding='utf-8')),
        encoding='utf-8')
    # Verify all local figure references before export.
    missing = []
    for path in inputs:
        for target in re.findall(r'!\[[^]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if not (path.parent / target).exists(): missing.append((path.name, target))
    assert not missing, missing
    run('pandoc', '-f', 'markdown+tex_math_single_backslash', '--standalone',
        '--toc', '--toc-depth=3', '--reference-doc', str(TEMPLATE),
        '--resource-path', str(SRC), '-o', str(DOCX), str(export_md))

    doc = Document(DOCX)
    sec = doc.sections[0]
    sec.top_margin = Cm(2.4); sec.bottom_margin = Cm(2.2)
    sec.left_margin = Cm(2.5); sec.right_margin = Cm(2.2)
    for name in ('Normal', 'Body Text'):
        if name in doc.styles:
            style = doc.styles[name]
            style.font.name = '宋体'; style.font.size = Pt(10.5)
            style._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), '宋体')
            style.paragraph_format.space_after = Pt(4)
    for name, size in [('Heading 1', 16), ('Heading 2', 14), ('Heading 3', 12)]:
        if name in doc.styles:
            style = doc.styles[name]
            style.font.name = '黑体'; style.font.size = Pt(size)
            style._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), '黑体')
            if name == 'Heading 1': style.paragraph_format.page_break_before = True
    for t in doc.tables:
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = True
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.font.size = Pt(8.5)
    for p in doc.paragraphs:
        if re.match(r'^(?:BDZ-\d+|SIM-CITY-)', p.text):
            p.paragraph_format.page_break_before = True
    for node in doc._element.body.xpath('.//w:sdtContent//w:t'):
        if node.text == 'Table of Contents':
            node.text = '目录'
    update_fields = OxmlElement('w:updateFields')
    update_fields.set(qn('w:val'), 'true')
    doc.settings.element.append(update_fields)
    # Footer page field, independent of any page numbers cached by WPS.
    footer = sec.footer.paragraphs[0] if sec.footer.paragraphs else sec.footer.add_paragraph()
    footer.alignment = 1
    field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'), 'PAGE')
    footer._p.append(field)
    doc.save(DOCX)
    with ZipFile(DOCX) as z:
        xml = z.read('word/document.xml').decode('utf-8')
        formula_count = xml.count('<m:oMath>') + xml.count('<m:oMathPara>')
        image_count = len([x for x in z.namelist() if x.startswith('word/media/')])
    assert formula_count >= 8, formula_count
    assert image_count >= 6, image_count

    # HTML print preview renders formulas as MathML; Chrome can print it to PDF.
    run('pandoc', '-f', 'markdown+tex_math_single_backslash', '--standalone',
        '--toc', '--toc-depth=3', '--mathml', '--self-contained',
        '--resource-path', str(SRC), '-t', 'html5', '-o', str(PREVIEW), str(export_md))
    html = PREVIEW.read_text(encoding='utf-8')
    css = '''<style>@page{size:A4;margin:20mm 19mm 20mm 21mm;}
body{font-family:"Noto Sans CJK SC","Noto Serif CJK SC",serif;font-size:10.5pt;line-height:1.55;color:#111;}
h1{page-break-before:always;font-size:17pt;margin-top:0;}
h2{font-size:13pt;margin-top:16pt;}h3{font-size:11pt;margin-top:12pt;}
h3[id^="bdz-"],h3[id^="sim-city-"]{page-break-before:always;}
h1,h2,h3{page-break-after:avoid;}table{border-collapse:collapse;width:100%;font-size:8pt;table-layout:auto;page-break-inside:auto;}
tr{page-break-inside:avoid;}th,td{border:0.4pt solid #888;padding:2.5pt 3pt;vertical-align:top;overflow-wrap:anywhere;}
p{margin:0 0 7pt;orphans:2;widows:2;}img{max-width:100%;height:auto;}
figure{margin:12pt 0;page-break-inside:avoid;}figcaption{text-align:center;font-size:9pt;}
#title-block-header{page-break-after:always;text-align:center;padding-top:28vh;}
#TOC{page-break-after:always;}#TOC ul{list-style:none;}#TOC a{text-decoration:none;color:#222;}
@media print{a{color:#111;text-decoration:none;}}</style>'''
    PREVIEW.write_text(html.replace('</head>', css+'</head>'), encoding='utf-8')
    pages = None
    if PDF.exists():
        info = run('pdfinfo', str(PDF)).stdout
        match = re.search(r'^Pages:\s*(\d+)', info, re.M)
        pages = int(match.group(1)) if match else None
    audit = {
        'chapters': len(CHAPTERS), 'appendices': len(APPENDICES),
        'markdown_bytes': ASSEMBLED.stat().st_size,
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'word_native_math_objects': formula_count, 'word_embedded_images': image_count,
        'pdf_status': 'print_preview_ready', 'pdf_pages_before_reprint': pages,
        'word_bytes': DOCX.stat().st_size,
    }
    (QA / '装配核验.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
