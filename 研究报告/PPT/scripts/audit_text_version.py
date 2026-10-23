"""Check revision invariants without modifying the report or original deck."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import hashlib,json,re,statistics

B=Path(__file__).resolve().parents[1]
W=B/'成果汇报_文字增强版_20261021'
v1=B/'成果汇报_20261019/exports/徐州110kV容载比弹性指标优化研究_成果汇报初稿.pptx'
v2=W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报_文字增强版.pptx'
report=B.parent/'04_word/研究报告终稿.docx'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(v1)=='0e86beaaa7aaba62a2be0fdd6e2209ed0fcecccb5ed993610edbe20ffc68f2cb'
assert sha(report)=='4a9880aab102f3c436325867ebbc9148e6a258f38b179cd5aa822b4d19f0e92b'
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
text=lambda root:''.join(root.xpath('.//a:t/text()',namespaces=ns))
tables=lambda root:[[[text(c) for c in row.findall('a:tc',ns)] for row in t.findall('a:tr',ns)] for t in root.findall('.//a:tbl',ns)]
rows=[]
with ZipFile(v1) as old,ZipFile(v2) as new:
    for i in range(1,37):
        a=E.fromstring(old.read(f'ppt/slides/slide{i}.xml'))
        b=E.fromstring(new.read(f'ppt/slides/slide{i}.xml'))
        ta,tb=tables(a),tables(b)
        assert ta==tb,('native table changed',i)
        tr=b.find('p:transition',ns)
        assert tr is None or ('advTm' not in tr.attrib and tr.get('advClick','1')=='1'),('timed transition',i)
        rows.append({'page':i,'native_tables':len(tb),'native_table_cells':sum(sum(len(r) for r in t) for t in tb),'old_native_chars':len(re.sub(r'\s','',text(a))),'new_native_chars':len(re.sub(r'\s','',text(b)))})
    notes=[n for n in new.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+(?:_tf\d+)*\.xml',n)]
    assert len(notes)==36
    for n in notes:
        root=E.fromstring(new.read(n))
        body=root.xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]',namespaces=ns)
        assert body and text(body[0]).strip(),('empty speaker notes',n)
    props=E.fromstring(new.read('ppt/presProps.xml'))
    assert props.find('p:showPr',ns).get('useTimings')=='0'
    parts=[n for n in old.namelist() if n.startswith(('ppt/slideMasters/','ppt/slideLayouts/'))]
    assert all(n in new.namelist() and old.read(n)==new.read(n) for n in parts)
    expected_slides=[f'ppt/slides/slide{i}.xml' for i in range(1,37)]
    assert sorted(n for n in new.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n))==sorted(expected_slides)
counts={label:{'mean':round(statistics.mean(r[key] for r in rows[2:24]),2),'median':statistics.median(r[key] for r in rows[2:24])} for label,key in [('original','old_native_chars'),('text_enriched','new_native_chars')]}
result={'status':'passed','report_sha256':sha(report),'original_pptx_sha256':sha(v1),'new_pptx_sha256':sha(v2),'pages':36,'main_pages':25,'appendix_pages':11,'notes':len(notes),'native_tables_unchanged':sum(r['native_tables'] for r in rows),'native_table_cells_unchanged':sum(r['native_table_cells'] for r in rows),'master_layout_parts_byte_identical':len(parts),'manual_advancing':True,'native_text_counts_pages_3_to_24':counts,'count_limit':'Excludes words embedded in figures; counts describe native text only.','pages_detail':rows}
(W/'validation/revision_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='pages_detail'},ensure_ascii=False))
