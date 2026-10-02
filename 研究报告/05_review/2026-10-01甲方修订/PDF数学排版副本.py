"""PDF输出副本；最终Word保留全部OMML数学对象。

本地LibreOffice 7.3对部分OMML组合存在解析问题，PDF副本按相同LaTeX源
生成数学图形；字体与原稿保持，式号单独置于右栏。
"""
import re,json,subprocess,copy
from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import cairosvg
from lxml import etree
HERE=Path(__file__).parent;R=HERE.parents[1];OUT=R/'04_word/2026-10-01甲方修订';CACHE=R/'02图表/2026-10-01甲方修订/PDF数学';CACHE.mkdir(exist_ok=True)
source=(R/'03_MD/2026-10-01甲方修订/研究报告装配稿.md').read_text()
items=[]
for i,m in enumerate(re.finditer(r'\$\$([\s\S]*?)\$\$|\$([^$\n]+)\$',source)):
 items.append({'number':str(i),'tex':m[1] if m[1] is not None else m[2],'display':m[1] is not None,'svg':str(CACHE/f'{i:03d}.svg')})
(CACHE/'清单.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
subprocess.run(['node',str(R/'05_review/2026-10-01重构/公式渲染.js'),str(CACHE/'清单.json')],check=True)
doc=Document(OUT/'研究报告_WPS兼容稿.docx');objects=doc._element.xpath('.//m:oMath');assert len(objects)==len(items),(len(objects),len(items))
for obj,it in zip(objects,items):
 svg=Path(it['svg']).read_text().replace('font-family="serif"','font-family="方正仿宋_GBK"')
 tree=etree.fromstring(svg.encode());size=lambda t:float(re.match(r'([\d.]+)',t)[1])
 w=size(tree.get('width'))*6;h=size(tree.get('height'))*6
 scale=min(1,(11.75/2.54*72)/w) if it['display'] else 1
 w*=scale;h*=scale
 png=Path(it['svg']).with_suffix('.png');cairosvg.svg2png(bytestring=svg.encode(),write_to=str(png),output_width=round(w*300/72),output_height=round(h*300/72))
 placeholder=doc.add_paragraph();run=placeholder.add_run();run.add_picture(str(png),width=Pt(w),height=Pt(h));el=copy.deepcopy(run._r);placeholder._p.getparent().remove(placeholder._p)
 if not it['display']:
  descent=re.search(r'vertical-align:\s*(-?[\d.]+)ex',tree.get('style',''));position=float(descent[1])*6 if descent else 0
  rp=OxmlElement('w:rPr');pos=OxmlElement('w:position');pos.set(qn('w:val'),str(round(position*2)));rp.append(pos);el.insert(0,rp)
 for prop in el.xpath('.//wp:docPr'):prop.set('descr',it['tex'])
 target=obj.getparent() if it['display'] else obj
 target.addprevious(el);target.getparent().remove(target)
assert not doc._element.xpath('.//m:oMath')
doc.save(OUT/'PDF排版副本.docx');print('PDF排版副本数学对象',len(items),'最终Word保留原生公式')
