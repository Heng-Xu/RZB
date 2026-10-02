import os,sys,re,json,subprocess,copy,math
from pathlib import Path
from docx import Document
from docx.shared import Cm,Pt,Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_BREAK,WD_LINE_SPACING,WD_TAB_ALIGNMENT,WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import cairosvg
ROOT=Path(__file__).resolve().parents[3]
TEXT=ROOT/'研究报告/03_MD/2026-10-01甲方修订';REVIEW=Path(__file__).parent
ASSET=ROOT/'研究报告/02图表/2026-10-01甲方修订';MATH=ASSET/'公式';MATH.mkdir(exist_ok=True)
OUT=ROOT/'研究报告/04_word/2026-10-01甲方修订';OUT.mkdir(exist_ok=True,parents=True)
TITLE='徐州地区分布式新能源高渗透率地区110 kV电网容载比弹性指标优化研究'
TABLES=json.loads((ASSET/'计算表.json').read_text());SECTIONS=json.loads((ASSET/'生成段落.json').read_text())
def font(run,size=12,bold=False,east='方正仿宋_GBK'):
 run.font.name='Times New Roman';run.font.size=Pt(size);run.font.bold=bold
 pr=run._element.get_or_add_rPr();rf=pr.find(qn('w:rFonts'))
 if rf is None:rf=OxmlElement('w:rFonts');pr.insert(0,rf)
 rf.set(qn('w:eastAsia'),east);rf.set(qn('w:ascii'),'Times New Roman');rf.set(qn('w:hAnsi'),'Times New Roman')
def style(s,size,bold=False,east='方正仿宋_GBK'):
 s.font.name='Times New Roman';s.font.size=Pt(size);s.font.bold=bold
 rf=s.element.get_or_add_rPr().find(qn('w:rFonts'))
 if rf is None:rf=OxmlElement('w:rFonts');s.element.get_or_add_rPr().append(rf)
 rf.set(qn('w:eastAsia'),east)
def refdoc():
 source=ROOT/'研究报告/范文与语料/国网宿迁公司宿迁市“十五五”电网侧新型储能发展项目研究报告-初稿.docx'
 doc=Document(source);body=doc._element.body
 for el in list(body):
  if el.tag!=qn('w:sectPr'):body.remove(el)
 for sec in doc.sections:
  sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=Cm(2.54);sec.bottom_margin=Cm(2.54);sec.left_margin=Cm(3.1697);sec.right_margin=Cm(3.1697)
  for part in [sec.header,sec.footer,sec.first_page_header,sec.first_page_footer]:
   for el in list(part._element):part._element.remove(el)
 style(doc.styles['Normal'],12);fmt=doc.styles['Normal'].paragraph_format;fmt.line_spacing=1.25;fmt.space_before=Pt(0);fmt.space_after=Pt(0);fmt.first_line_indent=Pt(24)
 for n,size in [(1,18),(2,16),(3,13),(4,12)]:
  s=doc.styles['Heading '+str(n)];style(s,size,True);s.paragraph_format.line_spacing=1.5;s.paragraph_format.first_line_indent=Pt(0);s.paragraph_format.space_before=Pt(8 if n>1 else 0);s.paragraph_format.space_after=Pt(6);s.paragraph_format.keep_with_next=True
 for nm in ['Body Text','First Paragraph','Compact']:
  if nm in doc.styles:
   s=doc.styles[nm];style(s,12);s.paragraph_format.line_spacing=1.25;s.paragraph_format.first_line_indent=Pt(24);s.paragraph_format.space_before=Pt(0);s.paragraph_format.space_after=Pt(0)
 doc.save(REVIEW/'排版参照.docx')
def assemble():
 txt='\n\n'.join(p.read_text().strip() for p in sorted(TEXT.glob('0[1-6] *.md')))
 txt=re.sub(r'\[\[TABLE:([^\]]+)\]\]',lambda m:TABLES[m[1]],txt)
 txt=re.sub(r'\[\[SECTION:([^\]]+)\]\]',lambda m:SECTIONS[m[1]],txt)
 txt=re.sub(r'\[\[FIG:([^|]+)\|([^\]]+)\]\]',lambda m:'![]('+str(ASSET/(m[1]+'.png'))+'){width=5.6in}\n\n'+m[2],txt)
 refs=(ROOT/'研究报告/03_MD/参考文献.md').read_text()
 refs+='\n\n[78] 徐州项目收资资料. 2025设备负载统计表[Z]. 脱敏数据整合版V1.2，2025.\n\n[79] 徐州项目收资资料. 邳州与市区站级净负荷小时序列[Z]. 脱敏数据整合版V1.2，2025.\n\n[80] 徐州项目收资资料. 光伏8760小时数据[Z]. 系统光伏资料典型曲线，2025映射时间轴.\n'
 txt+='\n\n'+refs
 # 按正文顺序连续编号，公式引用同步改号。
 counters={};mapping={}
 for match in re.finditer(r'\\tag\{(\d+)-(\d+)\}',txt):
  chapter=match[1];counters[chapter]=counters.get(chapter,0)+1;mapping[match[1]+'-'+match[2]]=chapter+'-'+str(counters[chapter])
 txt=re.sub(r'\\tag\{([^}]+)\}',lambda m:'\\tag{'+mapping[m[1]]+'}',txt)
 txt=re.sub(r'式([（(]?)(\d+-\d+)',lambda m:'式'+m[1]+mapping.get(m[2],m[2]),txt)
 for kind in ['表','图']:
  counts={}
  def caption(m):
   c=m[1];counts[c]=counts.get(c,0)+1;return kind+c+'-'+str(counts[c])+' '
  txt=re.sub(r'^'+kind+r'(\d+)-[\da-z-]+\s+',caption,txt,flags=re.M)
 # 公式保留LaTeX源，经Pandoc转换为Word原生OMML。
 mathlist=[]
 def equation(m):
  tex=m[1];tags=re.findall(r'\\tag\{([^}]+)\}',tex)
  number=tags[0] if tags else str(len(mathlist)+1)
  tex=re.sub(r'\\tag\{[^}]+\}','',tex)
  mathlist.append({'number':number,'tex':tex})
  return '$$'+tex+'$$'
 txt=re.sub(r'\$\$([\s\S]*?)\$\$',equation,txt)
 assert '[[' not in txt
 (TEXT/'研究报告装配稿.md').write_text(txt)
 (MATH/'公式清单.json').write_text(json.dumps(mathlist,ensure_ascii=False,indent=2))
 subprocess.run(['pandoc',str(TEXT/'研究报告装配稿.md'),'--reference-doc='+str(REVIEW/'排版参照.docx'),'--from=markdown+tex_math_dollars','--to=docx','--output='+str(REVIEW/'原始装配.docx')],check=True)
 return mathlist
def configure_doc(mathlist):
 doc=Document(REVIEW/'原始装配.docx');sec=doc.sections[0]
 sec.different_first_page_header_footer=True;sec.header_distance=Cm(1.27);sec.footer_distance=Cm(1.27)
 sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=Cm(2.54);sec.bottom_margin=Cm(2.54);sec.left_margin=Cm(3.1697);sec.right_margin=Cm(3.1697)
 # 清除模板悬挂的多级编号，正文编号已经写在标题文本。
 for n in range(1,5):
  s=doc.styles['Heading '+str(n)];ppr=s.element.get_or_add_pPr()
  for node in ppr.findall(qn('w:numPr')):ppr.remove(node)
 normal=doc.styles['Normal'];style(normal,12);normal.paragraph_format.line_spacing=1.25
 numeq=0
 for p in doc.paragraphs:
  pf=p.paragraph_format;t=p.text.strip();level=int(p.style.name.split()[-1]) if p.style.name.startswith('Heading ') else 0
  if level:
   ppr=p._p.get_or_add_pPr()
   for nd in ppr.findall(qn('w:numPr')):ppr.remove(nd)
   np=OxmlElement('w:numPr');ni=OxmlElement('w:numId');ni.set(qn('w:val'),'0');np.append(ni);ppr.append(np)
   size={1:18,2:16,3:13,4:12}.get(level,12);pf.first_line_indent=Pt(0);pf.line_spacing=1.5;pf.keep_with_next=True;pf.space_before=Pt(8 if level>1 else 0);pf.space_after=Pt(6)
   if level==1:pf.page_break_before=True
   for r in p.runs:font(r,size,True)
  elif p._element.xpath('.//m:oMathPara'):
   it=mathlist[numeq];numeq+=1
   pf.alignment=WD_ALIGN_PARAGRAPH.CENTER;pf.first_line_indent=Pt(0);pf.line_spacing=1.15;pf.space_before=Pt(5);pf.space_after=Pt(5);pf.keep_with_next=True
   for mp in p._element.xpath('.//m:oMathPara'):
    pr=mp.find(qn('m:oMathParaPr'))
    if pr is None:pr=OxmlElement('m:oMathParaPr');mp.insert(0,pr)
    jc=OxmlElement('m:jc');jc.set(qn('m:val'),'center');pr.append(jc)
   # 编号单独置于行尾，数学对象独立居中。
   p.add_run('（'+it['number']+'）')
  elif p._element.xpath('.//w:drawing'):
   pf.alignment=WD_ALIGN_PARAGRAPH.CENTER;pf.first_line_indent=Pt(0);pf.line_spacing=1;pf.space_before=Pt(6);pf.space_after=Pt(0);pf.keep_with_next=True
  elif t.startswith('表') and re.match(r'表\d+-',t):
   pf.alignment=WD_ALIGN_PARAGRAPH.CENTER;pf.first_line_indent=Pt(0);pf.line_spacing=1.25;pf.space_before=Pt(6);pf.space_after=Pt(4);pf.keep_with_next=True
   for r in p.runs:font(r,10.5,False,'宋体')
  elif t.startswith('图') and re.match(r'图\d+-',t):
   pf.alignment=WD_ALIGN_PARAGRAPH.CENTER;pf.first_line_indent=Pt(0);pf.line_spacing=1.25;pf.space_before=Pt(3);pf.space_after=Pt(6)
   for r in p.runs:font(r,10.5,False,'宋体')
  else:
   pf.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;pf.first_line_indent=Pt(24);pf.line_spacing=1.25;pf.space_before=Pt(0);pf.space_after=Pt(0);pf.widow_control=True
   if re.match(r'^\[\d+\]',t):pf.first_line_indent=Pt(0);pf.line_spacing=1.15;pf.space_after=Pt(4);pf.alignment=WD_ALIGN_PARAGRAPH.LEFT
   for r in p.runs:font(r,10.5 if re.match(r'^\[\d+\]',t) else 12)
 assert numeq==len(mathlist),(numeq,len(mathlist))
 # 重建为标准Word表格，消除转换器沿用模板时产生的无效表格样式和结构。
 for old in list(doc.tables):
  values=[[c.text for c in row.cells] for row in old.rows]
  new=doc.add_table(rows=len(values),cols=len(values[0]))
  for row,vs in zip(new.rows,values):
   for cell,text in zip(row.cells,vs):cell.text=text
  old._tbl.addprevious(new._tbl);old._tbl.getparent().remove(old._tbl)
 for tab in doc.tables:
  tab.autofit=False;tab.alignment=1;n=len(tab.rows[0].cells);total=14.6606
  weights=[1]*n
  head=[c.text for c in tab.rows[0].cells]
  if any('站号' in x for x in head):weights[head.index(next(x for x in head if '站号' in x))]=1.2
  for j,x in enumerate(head):
   if 'MW/MWh' in x:weights[j]=1.45
  if head[0]=='资料':weights=[1.2,1.2,1.2,1.2]
  if head[0]=='参数' and n==3:weights=[1.1,2,2]
  if head[0]=='参数' and n==2:weights=[1,2]
  widths=[Cm(total*w/sum(weights)) for w in weights]
  grid=tab._tbl.tblGrid
  for child in list(grid):grid.remove(child)
  for width in widths:
   gc=OxmlElement('w:gridCol');gc.set(qn('w:w'),str(width.twips));grid.append(gc)
  for col,width in zip(tab.columns,widths):col.width=width
  pr=tab._tbl.tblPr
  tw=pr.find(qn('w:tblW'));tw.set(qn('w:type'),'dxa');tw.set(qn('w:w'),str(Cm(total).twips))
  bord=pr.find(qn('w:tblBorders'))
  if bord is None:bord=OxmlElement('w:tblBorders');pr.append(bord)
  for edge in ['top','bottom','insideH','insideV','left','right']:
   el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'555555');bord.append(el)
  for idx,row in enumerate(tab.rows):
   trp=row._tr.get_or_add_trPr();csp=OxmlElement('w:cantSplit');trp.append(csp)
   if idx==0:repeat=OxmlElement('w:tblHeader');trp.append(repeat)
   for j,cell in enumerate(row.cells):
    cell.width=widths[j];cell.vertical_alignment=1
    cp=cell._tc.get_or_add_tcPr();mar=OxmlElement('w:tcMar')
    for side in ['left','right']:
     e=OxmlElement('w:'+side);e.set(qn('w:w'),'70');e.set(qn('w:type'),'dxa');mar.append(e)
    cp.append(mar)
    for p in cell.paragraphs:
     f=p.paragraph_format;f.first_line_indent=Pt(0);f.alignment=WD_ALIGN_PARAGRAPH.CENTER;f.line_spacing=Pt(13);f.space_before=Pt(1);f.space_after=Pt(1);f.keep_with_next=False
     for r in p.runs:font(r,9,idx==0,'宋体')
 # 公式采用等宽侧栏，数学对象居中，式号独立在右栏。
 for p in list(doc.paragraphs):
  if not p._element.xpath('.//m:oMathPara'):continue
  number=p.runs[-1].text
  p.runs[-1]._r.getparent().remove(p.runs[-1]._r)
  tab=doc.add_table(rows=1,cols=3);tab.autofit=False;tab.alignment=1
  widths=[Cm(1.3),Cm(12.0606),Cm(1.3)]
  for col,w in zip(tab.columns,widths):col.width=w
  for cell,w in zip(tab.rows[0].cells,widths):
   cell.width=w;cell.vertical_alignment=1
   margin=OxmlElement('w:tcMar')
   for side in ['left','right']:
    nd=OxmlElement('w:'+side);nd.set(qn('w:w'),'0');nd.set(qn('w:type'),'dxa');margin.append(nd)
   cell._tc.get_or_add_tcPr().append(margin)
  pr=tab._tbl.tblPr;tw=pr.find(qn('w:tblW'));tw.set(qn('w:type'),'dxa');tw.set(qn('w:w'),str(Cm(14.6606).twips))
  borders=OxmlElement('w:tblBorders')
  for edge in ['top','bottom','insideH','insideV','left','right']:
   e=OxmlElement('w:'+edge);e.set(qn('w:val'),'nil');borders.append(e)
  pr.append(borders)
  rowpr=tab.rows[0]._tr.get_or_add_trPr();rowpr.append(OxmlElement('w:cantSplit'))
  mid=tab.cell(0,1);mid._tc.remove(mid.paragraphs[0]._p)
  p._p.addprevious(tab._tbl);mid._tc.append(p._p)
  for cell in [tab.cell(0,0),tab.cell(0,2)]:
   pp=cell.paragraphs[0];pp.paragraph_format.first_line_indent=Pt(0);pp.paragraph_format.space_before=Pt(0);pp.paragraph_format.space_after=Pt(0)
  pp=tab.cell(0,2).paragraphs[0];pp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
  font(pp.add_run(number),9)
 # 页眉页脚采用页码域与目录缓存。
 h=sec.header.add_paragraph('徐州地区110 kV电网容载比弹性指标优化研究');h.alignment=1
 for r in h.runs:font(r,9,False,'宋体')
 f=sec.footer.add_paragraph();f.alignment=1;r=f.add_run();field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');r._r.addnext(field)
 # 封面、内容提要、目录由同一版面生成；不插空白填充页。
 body=doc._element.body;front=Document();frontsec=front.sections[0]
 def add(text='',size=12,bold=False,align=0):
  p=front.add_paragraph();p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.line_spacing=1.25;p.alignment=align
  r=p.add_run(text);font(r,size,bold);return p
 p=add(TITLE,22,True,1);p.paragraph_format.space_before=Pt(140);p.paragraph_format.space_after=Pt(50)
 add('研究报告',20,True,1);p=add('2026年10月',14,False,1);p.paragraph_format.space_before=Pt(120)
 p=add('内容提要',18,True,1);p.paragraph_format.page_break_before=True;p.paragraph_format.space_after=Pt(20)
 for text in json.loads((REVIEW/'内容提要.json').read_text()):
  p=add(text);p.paragraph_format.first_line_indent=Pt(24);p.alignment=3;p.paragraph_format.space_after=Pt(10)
 p=add('目  录',18,True,1);p.paragraph_format.page_break_before=True;p.paragraph_format.space_after=Pt(15)
 headings=[]
 for i,p in enumerate(doc.paragraphs):
  if p.style.name in ['Heading 1','Heading 2']:
   text=p.text;level=int(p.style.name[-1]);anchor='h'+str(i)
   bs=OxmlElement('w:bookmarkStart');bs.set(qn('w:id'),str(1000+i));bs.set(qn('w:name'),anchor);be=OxmlElement('w:bookmarkEnd');be.set(qn('w:id'),str(1000+i));p._p.insert(0,bs);p._p.append(be)
   headings.append((text,level,anchor));t=add(text,12,level==1);t.paragraph_format.left_indent=Pt(12 if level==2 else 0);t.paragraph_format.space_after=Pt(2);t.paragraph_format.tab_stops.add_tab_stop(Cm(14.5),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
   t.add_run('\t');fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGEREF '+anchor+' \\h');rr=OxmlElement('w:r');tt=OxmlElement('w:t');tt.text='0';rr.append(tt);fld.append(rr);t._p.append(fld)
   for r in t.runs:font(r,12,level==1)
 for el in reversed(list(front._element.body)):
  if el.tag!=qn('w:sectPr'):body.insert(0,copy.deepcopy(el))
 (REVIEW/'目录标题.json').write_text(json.dumps(headings,ensure_ascii=False,indent=2))
 # Word常见标点与单位保留，关闭修订和注释；作者为项目组。
 doc.core_properties.author='研究项目组';doc.core_properties.last_modified_by='研究项目组';doc.core_properties.title=TITLE;doc.core_properties.subject='110 kV容量规划与措施经济比选'
 settings=doc.settings.element
 for node in settings.findall(qn('w:trackRevisions')):settings.remove(node)
 doc.save(OUT/'研究报告_WPS兼容稿.docx')
 print('Word',OUT/'研究报告_WPS兼容稿.docx','表',len(doc.tables),'公式',numeq,'图',len(doc.inline_shapes))
def main():refdoc();ml=assemble();configure_doc(ml)
if __name__=='__main__':main()
