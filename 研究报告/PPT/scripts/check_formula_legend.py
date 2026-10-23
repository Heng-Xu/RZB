"""Audit the single-page supplement and its current WPS PDF."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import hashlib,json,shutil
import pymupdf as fitz
B=Path(__file__).resolve().parents[1];W=B/'成果汇报_公式释义补充_20261022'
old=B/'成果汇报_章节导航与成本模型优化_20261022/exports/徐州110kV容载比弹性指标优化研究_成果汇报.pptx'
new=W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报_公式释义补充版.pptx'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','a14':'http://schemas.microsoft.com/office/drawing/2010/main'}
with ZipFile(old)as z1,ZipFile(new)as z2:
    for i in range(1,39):
        if i!=17:assert z1.read(f'ppt/slides/slide{i}.xml')==z2.read(f'ppt/slides/slide{i}.xml'),i
    a=E.fromstring(z1.read('ppt/slides/slide17.xml'));r=E.fromstring(z2.read('ppt/slides/slide17.xml'));math=r.findall('.//a14:m',ns);assert len(math)==8
    for x,y in zip(a.findall('.//a14:m',ns),math[:2]):assert x.xpath('.//m:t/text()',namespaces=ns)==y.xpath('.//m:t/text()',namespaces=ns)
    assert all(set(m.xpath('.//a:latin/@typeface',namespaces=ns))=={'Times New Roman'}for m in math)
    for n in z1.namelist():
        if n.startswith(('ppt/slideMasters/','ppt/slideLayouts/')):assert z1.read(n)==z2.read(n)
manifest=json.loads((W/'source_manifest.json').read_text());assert sha(old)==manifest['sha256'];assert sha(B.parent/'04_word/研究报告终稿.docx')==manifest['report_sha256']
audit={'status':'passed','pages':38,'changed_physical_page':17,'changed_wps_number':16,'footer':15,'other_37_slides_xml_byte_identical':True,'original_two_equations_tokens_unchanged':True,'new_inline_symbol_definitions':6,'equation_faces':'Times New Roman','source_unchanged':True,'report_unchanged':True,'output_sha256':sha(new)}
(W/'validation/revision_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
alias=Path('/tmp/xuzhou-report-ppt-draft.pptx');source=Path('/tmp/xuzhou-report-ppt-draft.pdf');assert sha(alias)==sha(new);assert source.stat().st_mtime>=alias.stat().st_mtime
pdf=W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报_公式释义补充版.pdf';shutil.copy2(source,pdf);doc=fitz.open(pdf);assert len(doc)==38;page=doc[16];actual=''.join(page.get_text().split())
for phrase in ['为方案费用现值','为建设改造项目','的费用现值，单位万元','分别为主变、储能和线路投运项目集合']:assert phrase in actual,phrase
preview=W/'previews/wps';preview.mkdir(parents=True,exist_ok=True);page.get_pixmap(matrix=fitz.Matrix(2,2)).save(preview/'page_17.png')
issues=[]
for block in page.get_text('dict')['blocks']:
    for line in block.get('lines',[]):
        for span in line['spans']:
            box=fitz.Rect(span['bbox'])
            if box.x0<0 or box.y0<0 or box.x1>page.rect.width+.5 or box.y1>page.rect.height+.5:issues.append(span['text'])
assert not issues,issues
(W/'validation/wps_export_check.json').write_text(json.dumps({'status':'passed','pages':38,'checked_physical_page':17,'supplement_phrases_present':True,'outside_page_text':issues,'fonts':[f[3]for f in page.get_fonts()],'visual_review':'pending','pdf_sha256':sha(pdf)},ensure_ascii=False,indent=2))
print('Single-page audit and WPS text checks passed')
