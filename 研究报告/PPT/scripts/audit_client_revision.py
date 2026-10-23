"""Audit approved local changes against the preserved delivered source deck."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import hashlib,json,re

B=Path(__file__).resolve().parents[1];W=B/'成果汇报_甲方修正版_20261022'
source=B/'成果汇报_文字增强版_20261021/exports/徐州110kV容载比弹性指标优化研究_成果汇报.pptx'
output=W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报_甲方修正版.pptx'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/package/2006/relationships'}
text=lambda x:''.join(x.xpath('.//a:t/text()',namespaces=ns))
normal=lambda x:re.sub(r'\s+','',x)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(el):return [el.tag,sorted(el.attrib.items()),el.text.strip()if el.text and el.text.strip()else'',*[canonical(c) for c in el]]
def objects(root):
    out={}
    for child in root.find('p:cSld/p:spTree',ns):
        ids=child.xpath('./*/p:cNvPr/@id',namespaces=ns)
        if ids:out[ids[0]]=child
    return out
def tables(root):return [[[text(c) for c in row.findall('a:tc',ns)] for row in t.findall('a:tr',ns)] for t in root.findall('.//a:tbl',ns)]
assert sha(source)=='8286be255cc8a290f0053275f63770e296f97998cebf6ac94b30632c03e9feda'
manifest=json.loads((W/'source_manifest.json').read_text())
assert sha(B.parent/'04_word/研究报告终稿.docx')==manifest['report_current_sha256_before']
specs=json.loads((W/'table_changes.json').read_text());rows=[];unchanged=0;cellcount=0
with ZipFile(source) as old,ZipFile(output) as new:
    assert len(E.fromstring(new.read('ppt/presentation.xml')).find('p:sldIdLst',ns))==34
    assert not any(re.fullmatch(r'ppt/slides/slide(?:35|36)\.xml',n) for n in new.namelist())
    for i in range(1,35):
        a=E.fromstring(old.read(f'ppt/slides/slide{i}.xml'));b=E.fromstring(new.read(f'ppt/slides/slide{i}.xml'))
        oa,ob=objects(a),objects(b)
        changed={'2'} if i>1 else set()
        changed.update({17:['22'],18:['22','23'],20:['22','27']}.get(i,[]))
        for id,obj in oa.items():
            if id in changed:continue
            assert id in ob and canonical(obj)==canonical(ob[id]),('unexpected visible-object change',i,id)
            unchanged+=1
        if i<=2:assert '2' not in ob
        else:assert text(ob['2'])==str(i-2),('wrong footer',i,text(ob.get('2')))
        ta,tb=tables(a),tables(b)
        if i not in [17,18,20]:assert ta==tb,('table changed',i)
        elif i==20:assert ta[0]==tb[0]
        if str(i) in specs:
            s=specs[str(i)];want=[s['header']]+s['rows'];got=tb[-1]
            assert len(want)==len(got)
            assert [[normal(c)for c in rr]for rr in want]==[[normal(c)for c in rr]for rr in got],('new table mismatch',i,want,got)
        tr=b.find('p:transition',ns);assert tr is None or ('advTm'not in tr.attrib and tr.get('advClick','1')=='1')
        cellcount+=sum(sum(len(r)for r in t)for t in tb)
        rows.append({'physical_page':i,'old_wps_number':i-1,'footer':None if i<3 else i-2,'tables':len(tb),'unchanged_source_objects':sum(id not in changed for id in oa)})
    parts=[n for n in old.namelist() if n.startswith(('ppt/slideMasters/','ppt/slideLayouts/'))]
    assert all(n in new.namelist()and old.read(n)==new.read(n)for n in parts)
    notes=[n for n in new.namelist()if re.fullmatch(r'ppt/notesSlides/notesSlide\d+(?:_tf\d+)*\.xml',n)]
    assert len(notes)==34
    for n in notes:
        body=E.fromstring(new.read(n)).xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]',namespaces=ns)
        assert body and text(body[0]).strip()
    assert E.fromstring(new.read('ppt/presProps.xml')).find('p:showPr',ns).get('useTimings')=='0'
result={'status':'passed','source_sha256':sha(source),'output_sha256':sha(output),'report_unchanged':True,'pages':34,'main_pages':25,'appendix_pages':9,'bottom_table_changes_physical_pages':[17,18,20],'bottom_table_changes_old_wps_numbers':[16,17,19],'deleted_source_physical_pages':[35,36],'deleted_old_wps_numbers':[34,35],'footer_sequence':'cover/agenda hidden; physical pages 3–34 display 1–32','untouched_source_objects_verified':unchanged,'native_tables':sum(r['tables']for r in rows),'native_table_cells':cellcount,'six_recommendation_matrices_unchanged':True,'speaker_notes':len(notes),'master_layout_parts_byte_identical':len(parts),'manual_advancing':True,'pages_detail':rows}
(W/'validation/revision_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items()if k!='pages_detail'},ensure_ascii=False))
