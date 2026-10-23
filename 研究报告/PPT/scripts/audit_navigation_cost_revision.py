"""Validate preserved results, five navigation states, and native cost math."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import hashlib,json,re
B=Path(__file__).resolve().parents[1];W=B/'成果汇报_章节导航与成本模型优化_20261022'
source=B/'成果汇报_甲方修正版_20261022/exports/徐州110kV容载比弹性指标优化研究_成果汇报_甲方修正版.pptx'
output=W/'exports/徐州110kV容载比弹性指标优化研究_成果汇报_章节导航与成本模型优化版.pptx'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','a14':'http://schemas.microsoft.com/office/drawing/2010/main'}
text=lambda r:''.join(r.xpath('.//a:t/text()',namespaces=ns))
tables=lambda r:[[[text(c)for c in rr.findall('a:tc',ns)]for rr in t.findall('a:tr',ns)]for t in r.findall('.//a:tbl',ns)]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def canon(e):return[e.tag,sorted(e.attrib.items()),e.text.strip()if e.text and e.text.strip()else'',[canon(c)for c in e]]
def objects(r):
 d={}
 for c in r.find('p:cSld/p:spTree',ns):
  ids=c.xpath('./*/p:cNvPr/@id',namespaces=ns)
  if ids:d[ids[0]]=c
 return d
manifest=json.loads((W/'source_manifest.json').read_text());plan=json.loads((W/'content_map.json').read_text())['pages'];fs=json.loads((W/'formula_sources.json').read_text())
assert sha(source)==manifest['sha256'];assert sha(B.parent/'04_word/研究报告终稿.docx')==manifest['report_sha256']
untouched=0;mathcount=0;matrixcount=0;nav=[]
with ZipFile(source)as old,ZipFile(output)as new:
 assert len(E.fromstring(new.read('ppt/presentation.xml')).find('p:sldIdLst',ns))==len(plan)==38
 for row in plan:
  j=row['page'];i=row['source_slide'];a=E.fromstring(old.read(f'ppt/slides/slide{i}.xml'));b=E.fromstring(new.read(f'ppt/slides/slide{j}.xml'));oa,ob=objects(a),objects(b)
  if 'section'in row or i==2:
   sec=row.get('section',1)
   for k,id in enumerate([5,13,21,29,37],1):
    shape=b.xpath(f'.//p:sp[p:nvSpPr/p:cNvPr[@id="{id}"]]',namespaces=ns)[0]
    colors=shape.xpath('./p:spPr/a:solidFill/a:srgbClr/@val',namespaces=ns)
    assert colors==['007C78'if k==sec else'F2F2F2'],('navigation state',j,k,colors)
   nav.append({'physical_page':j,'active_section':sec})
  elif i not in [12,13,14,15]:
   for id,obj in oa.items():
    if id=='2':continue
    assert id in ob and canon(obj)==canon(ob[id]),('unplanned object change',i,j,id)
    untouched+=1
   assert tables(a)==tables(b),('result table changed',i,j)
  if i>=29:matrixcount+=1
  if j>=3:
   foot=b.xpath('.//p:sp[p:nvSpPr/p:cNvPr[@id="2"]]',namespaces=ns)
   if 'section'in row:foot=b.xpath('.//p:sp[p:nvSpPr/p:cNvPr[@name="navigation-page-number"]]',namespaces=ns)
   if not foot and 'section'in row:
    foot=[s for s in b.findall('.//p:sp',ns)if text(s)==str(j-2)]
   assert foot and text(foot[0])==str(j-2),('footer',j)
  math=b.findall('.//a14:m',ns);expected=[f for f in fs if f['page_svg']==row['svg']];assert len(math)==len(expected)
  for actual,f in zip(math,expected):
   compiled=E.fromstring(f['compiled_omml']);assert actual.xpath('.//m:t/text()',namespaces=ns)==compiled.xpath('.//m:t/text()',namespaces=ns),('math tokens',f['id'])
   for tag in ['f','sSub','sSup','sSubSup','nary','d']:
    assert len(actual.findall('.//m:'+tag,ns))==len(compiled.findall('.//m:'+tag,ns)),('math structure',f['id'],tag)
   faces=actual.xpath('.//a:rPr/a:latin/@typeface',namespaces=ns);assert faces and set(faces)=={'Times New Roman'}
   mathcount+=1
  tr=b.find('p:transition',ns);assert tr is None or ('advTm'not in tr.attrib and tr.get('advClick','1')=='1')
 parts=[n for n in old.namelist()if n.startswith(('ppt/slideMasters/','ppt/slideLayouts/'))];assert all(old.read(n)==new.read(n)for n in parts)
 notes=[n for n in new.namelist()if re.fullmatch(r'ppt/notesSlides/notesSlide\d+(?:_tf\d+)*\.xml',n)];assert len(notes)==38
 for n in notes:
  body=E.fromstring(new.read(n)).xpath('.//p:sp[p:nvSpPr/p:nvPr/p:ph[@type="body"]]',namespaces=ns);assert body and text(body[0]).strip()
 assert E.fromstring(new.read('ppt/presProps.xml')).find('p:showPr',ns).get('useTimings')=='0'
assert len(nav)==5 and matrixcount==6 and mathcount==9
r={'status':'passed','source_preserved':True,'report_preserved':True,'pages':38,'main_pages':29,'appendix_pages':9,'navigation':nav,'native_equations':mathcount,'equation_font':'Times New Roman','equation_tokens_and_structures_match_compiler':True,'untouched_source_objects_verified':untouched,'six_recommendation_matrices_unchanged':True,'prior_three_comparison_tables_unchanged':True,'speaker_notes':38,'master_layout_parts_byte_identical':len(parts),'manual_advancing':True,'source_sha256':sha(source),'output_sha256':sha(output)}
(W/'validation/revision_audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))
