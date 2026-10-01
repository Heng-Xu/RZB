import os,sys,re,json,subprocess,copy,math
from pathlib import Path
from docx import Document
from docx.shared import Cm,Pt,Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_BREAK,WD_LINE_SPACING,WD_TAB_ALIGNMENT,WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import cairosvg
ROOT=Path(__file__).resolve().parents[3]
TEXT=ROOT/'研究报告/03_MD/2026-10-01重构';REVIEW=Path(__file__).parent
ASSET=ROOT/'研究报告/02图表/2026-10-01重构';MATH=ASSET/'公式';MATH.mkdir(exist_ok=True)
OUT=ROOT/'研究报告/04_word/2026-10-01重构';OUT.mkdir(exist_ok=True,parents=True)
TITLE='徐州地区分布式新能源高渗透率地区110 kV电网容载比弹性指标优化研究'
TABLES=json.loads((ASSET/'计算表.json').read_text());SECTIONS=json.loads((ASSET/'生成段落.json').read_text())
def font(run,size=12,bold=False,east='仿宋_GB2312'):
 run.font.name='Times New Roman';run.font.size=Pt(size);run.font.bold=bold
 pr=run._element.get_or_add_rPr();rf=pr.find(qn('w:rFonts'))
 if rf is None:rf=OxmlElement('w:rFonts');pr.insert(0,rf)
 rf.set(qn('w:eastAsia'),east);rf.set(qn('w:ascii'),'Times New Roman');rf.set(qn('w:hAnsi'),'Times New Roman')
def style(s,size,bold=False,east='仿宋_GB2312'):
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
 mathlist=[]
 def equation(m):
  tex=m[1];tags=re.findall(r'\\tag\{([^}]+)\}',tex);assert len(tags)==1,tex
  number=tags[0];tex=re.sub(r'\\tag\{[^}]+\}','',tex)
  mathlist.append({'number':number,'tex':tex,'svg':str(MATH/(number+'.svg'))})
  return 'FORMULA_'+number
 txt=re.sub(r'\$\$([\s\S]*?)\$\$',equation,txt)
 assert '[[' not in txt
 (TEXT/'研究报告装配稿.md').write_text(txt)
 (MATH/'公式清单.json').write_text(json.dumps(mathlist,ensure_ascii=False,indent=2))
 subprocess.run(['node',str(REVIEW/'公式渲染.js'),str(MATH/'公式清单.json')],check=True)
 for it in mathlist:
  svg=Path(it['svg']).read_text();svg=re.sub(r'font-family="[^"]*"','font-family="Noto Serif CJK SC"',svg)
  vw=re.search(r'viewBox="([^"]+)"',svg);w,h=map(float,vw[1].split()[2:]);width=min(5.45,max(.7,w/1000*6/72))
  # MathJax单位1000=1em；以12pt设置实际版面尺寸。
  width=min(4.95,w/1000*12/72);height=width*h/w
  # ex属性按实际12pt字号重设，输出480dpi图；公式字号不依赖云端字体。
  svg=re.sub(r'width="[^"]+"',f'width="{width*96}px"',svg,count=1);svg=re.sub(r'height="[^"]+"',f'height="{height*96}px"',svg,count=1)
  cairosvg.svg2png(bytestring=svg.encode(),write_to=str(MATH/(it['number']+'.png')),scale=5,background_color='white')
  it['width_in']=width;it['height_in']=height
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
  elif t.startswith('FORMULA_'):
   it=mathlist[numeq];numeq+=1
   for child in list(p._element):
    if child.tag!=qn('w:pPr'):p._element.remove(child)
   pf.first_line_indent=Pt(0);pf.line_spacing=1;pf.space_before=Pt(5);pf.space_after=Pt(5);pf.keep_with_next=True
   pf.tab_stops.add_tab_stop(Cm(14.5),WD_TAB_ALIGNMENT.RIGHT)
   run=p.add_run();pic=run.add_picture(str(MATH/(it['number']+'.png')),width=Inches(it['width_in']))
   pic._inline.docPr.set('descr','公式（'+it['number']+'）：'+it['tex'])
   run=p.add_run('\t（'+it['number']+'）');font(run,10.5)
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
 # 页眉页脚采用域，WPS可以显示缓存值并自行更新。
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
 for text in [
 '本研究以徐州邳州、市区110 kV电网为容量规划计算对象，结合丰县资料开展新能源渗透率与主变负载率对照。按照配电网规划设计导则分别核定容载比、网供负荷及供电区域类别；对源荷比、电量渗透率、绝对净负荷峰值和95%峰值持续时间给出资料处理与计算方法。',
 '费用模型以徐州实际主变工程及公开储能、线路案例为依据，区分新购容量、容量净增与新增第三台工程，统一采用新增措施全寿命费用现值。2021年设置同地区两方案共同反事实起点，2022—2025年主变、储能及新线状态非减；两方案均允许增容、储能和正常负荷转接。',
 '模型联立求解两地区刚性、弹性四条年度路径。刚性容载比不超过2.0；弹性每年超过2.0，市区指标低于邳州，以上为研究规划条件。基准弹性年度指标为邳州2.1048、2.2812、2.1637、2.0351，市区2.0965、2.0120、2.1409、2.0297。两地区弹性全寿命费用合计79477.29万元，较基准刚性低34.66%。',
 '推荐矩阵包括18组基准、价格与技术条件，保留两项成本比例、源荷与电量背景、峰段持续时间及四年加权增长。费用排序由求解结果确定：在平滑增长及加快增长条件下，部分地区转为刚性费用较低。因此，年度推荐值与对应设备措施、结构模板及输入分母共同使用。',
 '结果通过逐站年度容量、负荷转接守恒和现金流复算。该研究属于静态规划仿真，储能采用理想能量支撑、联络采用仿真通道，单台主变退出按容量条件筛查。结论适用于所列条件下的方案比选，实际工程应结合可用储能能力、真实通道和恢复时间进一步校核。']:
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
 print('Word',OUT/'研究报告_WPS兼容稿.docx','表',len(doc.tables),'公式',numeq,'图',len(doc.inline_shapes)-numeq)
def main():refdoc();ml=assemble();configure_doc(ml)
if __name__=='__main__':main()
