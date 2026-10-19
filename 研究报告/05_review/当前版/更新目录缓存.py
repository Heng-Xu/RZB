from pathlib import Path
import json,re,zipfile,tempfile
from lxml import etree
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import pymupdf
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).parent;OUT=ROOT/'研究报告/04_word'
def norm(s):return re.sub(r'\s+','',s)
def main():
 # python-docx保存时会重序列化批注；目录回填须保留原批注部件字节。
 with zipfile.ZipFile(OUT/'研究报告终稿.docx') as original:
  preserved_comments={n:original.read(n) for n in original.namelist() if 'comment' in n.lower() or n=='word/people.xml'}
 pdf=pymupdf.open(OUT/'研究报告终稿.pdf');assert len(pdf)>30,len(pdf)
 pages=[norm(p.get_text()) for p in pdf];headings=json.loads((R/'目录标题.json').read_text());indices={};entries=[]
 for title,level,anchor in headings:
  matches=[i+1 for i,t in enumerate(pages) if i>=3 and norm(title) in t];assert matches,(title,'未找到实际正文页')
  num=matches[0];indices[anchor]=num;entries.append({'标题':title,'页码':num,'锚点':anchor})
 doc=Document(OUT/'研究报告终稿.docx');done=0
 for field in doc._element.xpath('.//w:fldSimple'):
  instr=field.get(qn('w:instr'),'');m=re.search(r'PAGEREF\s+(\w+)',instr)
  if not m:continue
  assert m[1] in indices
  texts=list(field.iter(qn('w:t')));assert len(texts)==1;texts[0].text=str(indices[m[1]]);done+=1
 for p in doc._element.xpath('.//w:p[w:r/w:instrText]'):
  instruction=''.join(p.xpath('./w:r/w:instrText/text()'))
  m=re.search(r'PAGEREF\s+(\w+)',instruction)
  if not m:continue
  assert m[1] in indices
  within=False;result=[]
  for r in p.findall(qn('w:r')):
   marks=r.findall(qn('w:fldChar'))
   if any(x.get(qn('w:fldCharType'))=='separate' for x in marks):within=True;continue
   if any(x.get(qn('w:fldCharType'))=='end' for x in marks):within=False
   if within:result.extend(r.findall(qn('w:t')))
  assert result,(m[1],'无页码域结果')
  result[0].text=str(indices[m[1]])
  for node in result[1:]:node.text=''
  done+=1
 assert done==len(headings),(done,len(headings))
 settings=doc.settings.element
 for e in settings.findall(qn('w:updateFields')):settings.remove(e)
 u=OxmlElement('w:updateFields');u.set(qn('w:val'),'true');settings.append(u)
 doc.save(OUT/'研究报告终稿.docx')
 path=OUT/'研究报告终稿.docx';tmp=path.with_suffix('.tmp.docx')
 with zipfile.ZipFile(path) as inp,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as out:
  for info in inp.infolist():
   data=preserved_comments.get(info.filename,inp.read(info.filename))
   if info.filename=='docProps/app.xml':
    tree=etree.fromstring(data);ns={'ep':'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'};e=tree.find('ep:Pages',ns)
    if e is not None:e.text=str(len(pdf))
    data=etree.tostring(tree,encoding='UTF-8',xml_declaration=True,standalone=True)
   out.writestr(info,data)
 tmp.replace(path)
 (R/'目录页码核对.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2));print('目录缓存',done,'项；实际PDF',len(pdf),'页')
if __name__=='__main__':main()
