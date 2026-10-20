"""Verify source synchronization and every cell in the six PPT matrix tables."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from lxml import etree as E
from datetime import datetime,timezone
import json,hashlib,re

B=Path(__file__).resolve().parents[1];W=B/'成果汇报_20261019'
T=json.loads((W/'data/report_tables.json').read_text());M=json.loads((W/'source_manifest.json').read_text())
N={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
report=B.parent/'04_word/研究报告终稿.docx';raw=report.read_bytes();assert raw==report.read_bytes()
with ZipFile(BytesIO(raw))as z:body=E.fromstring(z.read('word/document.xml')).find('w:body',N)
tables={};paras=[];last=''
for el in body:
    if el.tag.endswith('}p'):
        tx=''.join(el.xpath('.//w:t/text()',namespaces=N))
        if tx.strip():last=tx;paras.append(tx)
    elif el.tag.endswith('}tbl')and re.match(r'^表\d+-\d+ ',last):
        tables[last.split(' ')[0]]={'title':last,'rows':[[''.join(c.xpath('.//w:t/text()',namespaces=N))for c in r.findall('w:tc',N)]for r in el.findall('w:tr',N)]}
changed=[k for k in set(T)|set(tables)if k not in T or k not in tables or T[k]['title']!=tables[k]['title']or T[k]['rows']!=tables[k]['rows']]
def content(pp):
    start=next(i for i,s in enumerate(pp)if re.fullmatch(r'第一章\s+绪论',s))
    return pp[start:]
oldp=[x['text']for x in json.loads((W/'data/report_paragraphs.json').read_text())]
same_body=content(oldp)==content(paras)
pptx=W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报初稿.pptx';cells=0;checks=[]
with ZipFile(pptx)as z:
    notes=[s for s in z.namelist()if re.fullmatch(r'ppt/notesSlides/notesSlide\d+(?:_\w+)?\.xml',s)]
    assert all(E.fromstring(z.read(s)).xpath('.//a:t/text()',namespaces=N)for s in notes)
    total_tables=sum(len(E.fromstring(z.read(s)).findall('.//a:tbl',N))for s in z.namelist()if re.fullmatch(r'ppt/slides/slide\d+\.xml',s))
    for s in z.namelist():
        if re.fullmatch(r'ppt/slides/slide\d+\.xml',s):
            root=E.fromstring(z.read(s))
            for tr in root.findall('.//p:transition',N):assert tr.get('advTm')is None and tr.get('advClick','1')=='1',(s,dict(tr.attrib))
    for page,key in zip(range(29,35),[f'表5-{i}'for i in range(63,69)]):
        root=E.fromstring(z.read(f'ppt/slides/slide{page}.xml'));tbls=root.findall('.//a:tbl',N);assert len(tbls)==1
        rows=[[''.join(c.xpath('.//a:t/text()',namespaces=N))for c in row.findall('a:tc',N)]for row in tbls[0].findall('a:tr',N)]
        assert rows==T[key]['rows'],(page,key)
        cells+=(len(rows)-1)*(len(rows[0])-2)
        checks.append({'page':page,'source_table':key,'body_cells_equal':True})
    root=E.fromstring(z.read('ppt/slides/slide22.xml'));vals=root.xpath('.//a:tbl/a:tr[2]/a:tc//a:t/text()',namespaces=N)
    example=next(r for r in T['表5-63']['rows'][1:]if r[0]=='>7%'and r[1]=='(1,2]')
    assert vals==['推荐容载比']+example[2:]
assert cells==288 and len(notes)==36 and not changed and same_body, {'cells':cells,'notes':len(notes),'changed':changed,'body_equal':same_body}
stations=T['表3-8']['rows'][1:]
assert sum(r[0]=='邳州'for r in stations)==20 and sum(r[0]=='市区'for r in stations)==26
manifest=json.loads((W/'figure_manifest.json').read_text());assert len(manifest['figures'])==14 and manifest['report_sha256']==M['sha256']
r={'checked_utc':datetime.now(timezone.utc).isoformat(),'status':'passed','ppt_source_sha256':M['sha256'],'current_report_sha256':hashlib.sha256(raw).hexdigest(),'source_tables':len(T),'changed_tables':changed,'body_paragraphs_equal':same_body,'notes':len(notes),'native_tables':total_tables,'matrix_cells_verified':cells,'matrix_checks':checks,'lookup_example_equal':True,'station_scope':[20,26],'new_data_figures':14,'concept_plates':2,'manual_advance_only':True,'scope':'本检查验证PPT内容与当前报告一致；不改写报告、不替代报告已有核验。'}
(W/'validation/content_sync_check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print(json.dumps(r,ensure_ascii=False))
