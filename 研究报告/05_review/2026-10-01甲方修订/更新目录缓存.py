from pathlib import Path
import json,re,zipfile,tempfile
from lxml import etree
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import pymupdf
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).parent;OUT=ROOT/'研究报告/04_word/2026-10-01甲方修订'
def norm(s):return re.sub(r'\s+','',s)
def main():
 pdf=pymupdf.open(OUT/'研究报告_WPS兼容稿.pdf');assert len(pdf)>30,len(pdf)
 pages=[norm(p.get_text()) for p in pdf];headings=json.loads((R/'目录标题.json').read_text());indices={};entries=[]
 for title,level,anchor in headings:
  matches=[i+1 for i,t in enumerate(pages) if i>=4 and norm(title) in t];assert matches,(title,'未找到实际正文页')
  num=matches[0];indices[anchor]=num;entries.append({'标题':title,'页码':num,'锚点':anchor})
 doc=Document(OUT/'研究报告_WPS兼容稿.docx');done=0
 for field in doc._element.xpath('.//w:fldSimple'):
  instr=field.get(qn('w:instr'),'');m=re.search(r'PAGEREF\s+(\w+)',instr)
  if not m:continue
  assert m[1] in indices
  texts=list(field.iter(qn('w:t')));assert len(texts)==1;texts[0].text=str(indices[m[1]]);done+=1
 assert done==len(headings),(done,len(headings))
 settings=doc.settings.element
 for e in settings.findall(qn('w:updateFields')):settings.remove(e)
 u=OxmlElement('w:updateFields');u.set(qn('w:val'),'false');settings.append(u)
 doc.save(OUT/'研究报告_WPS兼容稿.docx')
 path=OUT/'研究报告_WPS兼容稿.docx';tmp=path.with_suffix('.tmp.docx')
 with zipfile.ZipFile(path) as inp,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as out:
  for info in inp.infolist():
   data=inp.read(info.filename)
   if info.filename=='docProps/app.xml':
    tree=etree.fromstring(data);ns={'ep':'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'};e=tree.find('ep:Pages',ns)
    if e is not None:e.text=str(len(pdf))
    data=etree.tostring(tree,encoding='UTF-8',xml_declaration=True,standalone=True)
   out.writestr(info,data)
 tmp.replace(path)
 (R/'目录页码核对.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2));print('目录缓存',done,'项；实际PDF',len(pdf),'页')
if __name__=='__main__':main()
