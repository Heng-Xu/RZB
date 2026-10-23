"""Supplement only the plan-cost symbol definitions on source slide 17."""
from pathlib import Path
from lxml import etree as E
import json
import matplotlib
matplotlib.use('Agg')
from matplotlib.mathtext import MathTextParser
from matplotlib.font_manager import FontProperties
B=Path(__file__).resolve().parents[1];W=B/'成果汇报_公式释义补充_20261022'
NS='http://www.w3.org/2000/svg';Q=lambda s:'{'+NS+'}'+s
r=E.parse(str(W/'sources/authoring-baseline/slide_17.svg')).getroot()
specs=json.loads((B/'成果汇报_章节导航与成本模型优化_20261022/formula_sources.json').read_text())
def el(tag,parent=None,**attrs):
    e=E.Element(Q(tag),{k.replace('_','-'):str(v)for k,v in attrs.items()})
    if parent is not None:parent.append(e)
    return e
for id,y,h,key in [('shape-23',261,80,'cash-flow-present-value'),('shape-24',344,46,'plan-present-value')]:
    g=r.find(Q('g')+f"[@id='{id}']");g.set('data-pptx-frame',f'35 {y} 890 {h}');g.set('data-pptx-y',str(y));g.set('data-pptx-height',str(h));g.set('data-pptx-bounds',f'35 {y} 890 {h}')
    for e in list(g):
        if e.tag!=Q('metadata'):g.remove(e)
    m=json.loads(g.find(Q('metadata')).text);latex=next(f['latex']for f in specs if f['id']==key);fs=m['font_size']
    with matplotlib.rc_context({'mathtext.fontset':'stix'}):p=MathTextParser('path').parse('$'+latex+'$',dpi=72,prop=FontProperties(size=fs))
    assert p.width<890 and p.height<h
    el('rect',g,x=35,y=y,width=890,height=h,fill='none',stroke='none')
    ox=35+(890-p.width)/2;baseline=y+(h-p.height)/2+p.height-p.depth
    for ft,sz,c,x0,y0 in p.glyphs:
        t=el('text',g,x=f'{ox+x0:.3f}',y=f'{baseline-y0:.3f}',font_family='Times New Roman',font_size=f'{sz:.3f}',font_style='italic'if'italic'in ft.postscript_name.lower()else'normal',fill='#20393E');t.text='ℰ'if c==0xE231 else chr(c)
    for xx,yy,ww,hh in p.rects:
        x0=ox+xx;y0=baseline-yy-hh;el('path',g,d=f'M {x0:.3f} {y0:.3f} h {ww:.3f} v {hh:.3f} h {-ww:.3f} Z',fill='#20393E')
g=el('g',r,id='plan-cost-symbol-definitions',font_family='Microsoft YaHei');g.set('data-pptx-bounds','35 390 890 58');el('rect',g,x=35,y=390,width=890,height=58,fill='none',stroke='none')
t=el('text',g,x=42,y=406,font_family='Microsoft YaHei',font_size=17.5,fill='#20393E');t.text='式中，'
def symbol(parent,latex,preview,tail):
    s=el('tspan',parent,font_family='Times New Roman');s.set('data-pptx-inline-formula',latex);s.text=preview;s.tail=tail
symbol(t,r'C_{\mathrm{plan}}','Cplan','为方案费用现值，')
symbol(t,r'C_e','Ce','为建设改造项目')
symbol(t,r'e','e','的费用现值，单位万元；')
line=el('tspan',t,x=42,dy=23)
symbol(line,r'\mathcal{E}_{\mathrm{T}}','ℰT','、')
symbol(line,r'\mathcal{E}_{\mathrm{B}}','ℰB','、')
symbol(line,r'\mathcal{E}_{\mathrm{L}}','ℰL','分别为主变、储能和线路投运项目集合。')
E.ElementTree(r).write(str(W/'authoring-svg-flat/slide_17.svg'),encoding='utf-8',xml_declaration=False)
note=W/'notes/slide_17.md'
base=note.read_text()
addition='其中，方案费用现值由建设改造项目的费用现值相加得到，三类投运项目集合分别对应主变、储能和线路，费用单位均为万元。'
if addition not in base:note.write_text(base+'\n\n'+addition)
print('Added plan-cost symbol definitions to WPS slide 16')
