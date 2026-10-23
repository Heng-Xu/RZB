"""Add chapter navigation and report-based editable cost equations."""
from pathlib import Path
from lxml import etree as E
from copy import deepcopy
import json,re,unicodedata,sys
import matplotlib
matplotlib.use('Agg')
from matplotlib.mathtext import MathTextParser
from matplotlib.font_manager import FontProperties
sys.path.insert(0,'/home/xh/.codex/skills/ppt-master/scripts')
from svg_to_pptx.native_objects.formula_compiler import compile_latex_to_omml

B=Path(__file__).resolve().parents[1];W=B/'成果汇报_章节导航与成本模型优化_20261022';A=W/'authoring-svg-flat';S=W/'sources/authoring-baseline'
(W/'exports').mkdir(exist_ok=True)
NS='http://www.w3.org/2000/svg';Q=lambda s:'{'+NS+'}'+s
G='#007C78';TXT='#20393E';TINT='#EFF5F4';BORDER='#D0DEDB';FONT='Microsoft YaHei'
FORMULAS=[];TABLES=[]
def el(tag,parent=None,**attrs):
    z=E.Element(Q(tag),{k.replace('_','-'):str(v)for k,v in attrs.items()})
    if parent is not None:parent.append(z)
    return z
def group(r,id,x,y,w,h):
    g=el('g',r,id=id,font_family=FONT);g.set('data-pptx-bounds',f'{x} {y} {w} {h}');el('rect',g,x=x,y=y,width=w,height=h,fill='none',stroke='none');return g
def rect(g,x,y,w,h,fill,stroke='none'):return el('rect',g,x=x,y=y,width=w,height=h,fill=fill,stroke=stroke,stroke_width=.6)
def width(s,size):return sum(1 if unicodedata.east_asian_width(c)in'FW'else .55 for c in s)*size*1.07
def wrap(s,w,size):
    out=[]
    for part in str(s).split('\n'):
        buf=''
        for token in re.findall(r'[A-Za-z0-9]+(?:[.%/][A-Za-z0-9]+)*|.',part):
            if buf and width(buf+token,size)>w:out.append(buf);buf=token
            else:buf+=token
        out.append(buf)
    return out
def text(g,x,y,s,size=19,color=TXT,bold=False,w=None,leading=24,anchor='start'):
    ll=wrap(s,w,size)if w else s.split('\n');t=el('text',g,x=x,y=y,font_family=FONT,font_size=size,fill=color,font_weight='bold'if bold else'normal',text_anchor=anchor);t.text=ll[0]
    for ln in ll[1:]:el('tspan',t,x=x,dy=leading).text=ln
    return len(ll)
def para(r,id,x,y,w,h,s,size=18,leading=23,tint=False):
    g=group(r,id,x,y,w,h)
    if tint:rect(g,x,y,w,h,TINT)
    n=text(g,x+7,y+size+2,s,size,w=w-14,leading=leading)
    assert size+2+(n-1)*leading+size*.28<=h,(id,n,h)
    return g
def label(r,id,x,y,w,title):
    g=group(r,id,x,y,w,34);el('line',g,x1=x,y1=y,x2=x+w,y2=y,stroke=G,stroke_width=1.3);text(g,x+4,y+25,title,21,G,True)

def formula(r,id,x,y,w,h,latex,fs,source):
    # Compile now: unsupported syntax fails before publication.
    compiled=compile_latex_to_omml(latex)
    g=group(r,id,x,y,w,h);g.set('font-family','Times New Roman')
    for k,v in [('data-pptx-replace-with','formula'),('data-pptx-x',x),('data-pptx-y',y),('data-pptx-width',w),('data-pptx-height',h)]:g.set(k,str(v))
    el('metadata',g,type='application/json').text=json.dumps({'latex':latex,'display':'block','font_size':fs,'color':TXT,'align':'center'},ensure_ascii=False)
    # Materialize a vector SVG preview; the PPT exporter replaces it with OMML.
    with matplotlib.rc_context({'mathtext.fontset':'stix','font.family':'Times New Roman'}):
        p=MathTextParser('path').parse('$'+latex+'$',dpi=72,prop=FontProperties(size=fs))
    assert p.width<=w+4,(id,'formula too wide',p.width,w)
    assert p.height<=h+4,(id,'formula too tall',p.height,h)
    ox=x+(w-p.width)/2;baseline=y+(h-p.height)/2+p.height-p.depth
    for ft,size,code,gx,gy in p.glyphs:
        t=el('text',g,x=f'{ox+gx:.3f}',y=f'{baseline-gy:.3f}',font_family='Times New Roman',font_size=f'{size:.3f}',font_style='italic'if'italic'in ft.postscript_name.lower()else'normal',fill=TXT);t.text=chr(code)
    for xx,yy,ww,hh in p.rects:
        rx=ox+xx;ry=baseline-yy-hh
        el('path',g,d=f'M {rx:.3f} {ry:.3f} h {ww:.3f} v {hh:.3f} h {-ww:.3f} Z',fill=TXT)
    FORMULAS.append({'page_svg':CURRENT,'id':id,'latex':latex,'font_size_px':fs,'source':source,'compiled_omml':compiled})

def table(r,id,x,y,w,h,columns,rows,widths,heights,fs=18,numeric=()):
    g=group(r,id,x,y,w,h);g.set('data-pptx-replace-with','table')
    payload={'schema':'ppt-master.semantic-table.v2','name':id,'x':x,'y':y,'width':w,'height':h,'strict_grid':True,'header_rows':1,'column_widths':widths,'row_heights':heights,'style':{'font_family':FONT,'font_size':fs,'header_font_size':fs,'header_fill':G,'header_text':'#FFFFFF','body_fill':'#FFFFFF','body_text':TXT,'band_fill':TINT,'band_row':True,'border_color':BORDER,'border_width':.6,'valign':'middle'},'defaults':{'cell':{'align':'ctr','valign':'middle','padding':{'left':4,'right':4,'top':1,'bottom':1}}},'columns':[],'rows':[]}
    m=el('metadata',g,type='application/json');yy=y
    for ri,(rr,rh)in enumerate(zip([columns]+rows,heights)):
        xx=x;cc=[]
        for ci,(s,cw)in enumerate(zip(rr,widths)):
            head=ri==0;fill=G if head else TINT if ri%2==0 else'#FFFFFF';color='#FFFFFF'if head else TXT;align='r'if not head and ci in numeric else'ctr'
            ll=wrap(s,cw-8,fs);assert len(ll)*fs*1.15<=rh+1,(id,s,ll,rh)
            cc.append({'text':''.join(ll),'fill':fill,'color':color,'align':align,'bold':head,'font_size':fs})
            rect(g,xx,yy,cw,rh,fill,BORDER);tx=xx+cw-4 if align=='r'else xx+cw/2;baseline=yy+(rh-len(ll)*fs*1.15)/2+fs*.88
            text(g,tx,baseline,'\n'.join(ll),fs,color,head,leading=fs*1.15,anchor='end'if align=='r'else'middle')
            xx+=cw
        if ri==0:payload['columns']=cc
        else:payload['rows'].append(cc)
        yy+=rh
    m.text=json.dumps(payload,ensure_ascii=False,separators=(',',':'));TABLES.append({'page_svg':CURRENT,**payload})

def change_text(root,id,s):
    g=root.find(Q('g')+f"[@id='{id}']");assert g is not None
    ts=g.findall('.//'+Q('text'));assert len(ts)==1,(id,len(ts))
    t=ts[0]
    for child in list(t):t.remove(child)
    t.text=s
    for k in ['data-pptx-text-model','data-paragraph-line-height']:t.attrib.pop(k,None)
def wipe_body(root):
    for g in list(root.findall(Q('g'))):
        if g.get('data-pptx-source-ref','').startswith('slide:'):
            f=g.get('data-pptx-frame','0 0 0 0').split()
            if 265<=float(f[1])<663:root.remove(g)

mapping=json.loads((W/'content_map.json').read_text());titles={12:('3.8 主变工程投资','按新购整台容量计费，容量净增另行统计','依据：研究报告4.1—4.2，式（4-1）—（4-3）'),13:('3.9 10 kV联络投资','电缆占比决定造价，接入费单独计取','依据：研究报告4.3，式（4-4）、表4-3'),14:('3.10 储能采购与有效支撑','新增整数柜决定投资，功率与可用电量共同限制支撑','依据：研究报告4.4，式（4-5）—（4-6）、表4-5'),15:('3.11 现金流现值与评价边界','同一截止年下比较完整建设路径费用','依据：研究报告4.6，单项工程现值及方案汇总公式')}
for row in mapping['pages']:
    CURRENT=row['svg'];i=row['source_slide'];root=E.parse(str(S/f'slide_{i:02d}.svg')).getroot()
    if 'section'in row:
        sec=row['section']
        for k,gid in enumerate([11,19,27,35,43],1):
            g=root.find(Q('g')+f"[@id='shape-{gid}']")
            # The first whole-row painted rectangle carries the active section.
            for child in g.findall(Q('g')):
                ff=child.get('data-pptx-frame','').split()
                path=child.find(Q('path'))
                if len(ff)==4 and ff[2:]==['660','62']and path is not None and path.get('fill')!='none':path.set('fill',G if k==sec else'#F2F2F2')
            for t in g.findall('.//'+Q('text')):
                if ''.join(t.itertext())not in ['一','二','三','四','五']:t.set('fill','#FFFFFF'if k==sec else TXT)
        fg=group(root,'navigation-page-number',930,682,28,34);fg.set('data-pptx-role','page-number');text(fg,950.4,702.46666667,str(row['visible_page_number']),16,'#000000',anchor='end')
        (W/'notes'/Path(CURRENT).with_suffix('.md').name).write_text('下面进入'+['研究背景','研究目标和思路','研究内容','实证分析','项目成效'][sec-1]+'部分。')
    elif i>=3:change_text(root,'shape-2',str(row['visible_page_number']))
    if i in titles and 'section'not in row:
        wipe_body(root);bar,claim,src=titles[i];change_text(root,'shape-11',bar);change_text(root,'shape-10',claim)
        oldsource=root.find(Q('g')+"[@id='shape-17']");root.remove(oldsource)
        para(root,'report-source',35,663,850,29,src,13,16)
        row['title']=bar;row['source']=src;row['change']='成本模型公式、单位、边界及讲稿调整；页码顺排'
        if i==12:
            label(root,'transformer-basis',35,274,425,'工程案例与加权系数')
            formula(root,'transformer-rate',35,310,425,79,r'c_{\mathrm{T}}=\frac{1151+1335}{50+100}\approx16.57',28,'报告式4-1，万元/MVA')
            para(root,'rate-unit',35,389,425,28,'单位：万元/MVA；按采购容量加权。',17.5)
            table(root,'transformer-cases',35,425,425,108,['工程','投资/万元','新购/MVA','净增/MVA'],[['王庄','1151.00','50.00','30.00'],['鲁庙','1335.00','100.00','37.00']],[80,125,110,110],[36,36,36],17.5,(1,2,3))
            para(root,'purchase-boundary',35,542,425,61,'更换费用按整台新购容量计取，容量净增扣除被替换容量；参考系数包含配套工程。',18,23)
            label(root,'transformer-projects',492,274,433,'更换与扩建分别计价')
            formula(root,'replacement-investment',492,310,433,66,r'I_{\mathrm{T},iky}=c_{\mathrm{T}}S^{\mathrm{new}}_{iky}z_{iky}',29,'报告式4-2：投资/万元')
            formula(root,'net-capacity',492,383,433,68,r'\Delta S_{iky}=(S^{\mathrm{new}}_{iky}-S^{\mathrm{old}}_{ik,y-1})z_{iky}',25,'报告式4-2：容量/MVA，z取0或1')
            formula(root,'extension-investment',492,465,433,61,r'I_{\mathrm{T,exp}}=\frac{1206+1240}{2}=1223',25,'报告式4-3，万元/项')
            para(root,'extension-boundary',492,538,433,70,'更换状态取0或1，新旧容量以MVA计。扩建为50 MVA整项，1223.00万元/项，限具备预留位置的站点。',17.5,22)
            para(root,'shared-security',35,613,890,47,'共同条件：正常负载率≤80%、主变N-1短时≤130%。刚性保留2.0新增容量控制，弹性放宽该上限；同一主变位置全期最多更换一次。',17.5,22,True)
        elif i==13:
            formula(root,'line-investment',35,272,890,75,r'I_{\mathrm{L}}=24Lk_{\mathrm{L}}+6,\qquad k_{\mathrm{L}}=1+6.5\alpha',32,'报告式4-4及4.3.2')
            original=E.parse(str(S/'slide_12.svg')).getroot();oldgroup=original.find(Q('g')+"[@id='shape-22']");im=oldgroup.find('.//'+Q('image'));assert im is not None
            g=group(root,'line-cost-curve',35,363,520,292);el('image',g,href=im.get('href'),x=35,y=363,width=520,height=292,preserveAspectRatio='xMidYMid meet')
            para(root,'line-definitions',580,363,345,95,'计价参数：投资单位万元，线路长度L以km计；电缆长度占比α取0—1。架空24万元/km，电缆综合180万元/km。',18,23)
            para(root,'fixed-connection',580,467,345,77,'项目边界：基准长度3 km，另加两台等效开关6.00万元；固定接入费保持独立。',18,23)
            para(root,'regional-line-fee',580,553,345,105,'地区单价：邳州128.38、市区452.40万元/项。既有工程不重复计建设费，新增按投运条数计费；校核源端、共享通道及受端余量。',18,23)
        elif i==14:
            para(root,'storage-package',35,270,890,31,'柜型100 kW/215 kWh；10柜成套成交210.46万元，按新增整数柜采购。',19)
            formula(root,'storage-investment',35,307,890,75,r'c_{\mathrm{B}}=\frac{2104562.62}{10000\times10}\approx21.05,\qquad I_{\mathrm{B},iy}=c_{\mathrm{B}}\Delta n_{iy}',29,'报告式4-5，cB万元/柜，IB万元')
            formula(root,'storage-effective-power',35,386,890,86,r'B(n,H)=\min\left\{0.10n,\frac{0.215\times0.76n}{H}\right\},\qquad H>0',31,'报告式4-6，功率/MW、时长/h')
            para(root,'storage-definitions',35,475,890,46,'单柜参考21.05万元；n为在役柜数，Δn为当年新增整数柜数，H为支撑时长/h，B为有效功率/MW。',17.5)
            table(root,'storage-duration-comparison',35,526,890,84,['支撑时长 / h','2','4','6'],[['10柜有效功率 / MW','0.82','0.41','0.27'],['1.00 MW所需柜数 / 柜','13','25','37']],[308,194,194,194],[28,28,28],18,(1,2,3))
            para(root,'storage-boundary',35,613,890,47,'正向支撑与反向吸收分别采用对应时长；0.76包含SOC可用窗口与单向放电效率，按静态功率折算，实际运行再核定充电、恢复及连续SOC。',17.5,22,True)
        else:
            formula(root,'cash-flow-present-value',35,273,890,123,r'C(I,y,L,q)=\frac{I}{(1+r)^{y-2021}}+\sum_{k\geq1,\,y+kL<T}\frac{I}{(1+r)^{y+kL-2021}}+\sum_{t=y+1}^{T}\frac{qI}{(1+r)^{t-2021}}',24,'报告4.6.1：投运投资+评价期内更新+次年起运维')
            formula(root,'plan-present-value',35,399,890,46,r'C_{\mathrm{plan}}=\sum_{e\in\mathcal{E}_{\mathrm{T}}}C_e+\sum_{e\in\mathcal{E}_{\mathrm{B}}}C_e+\sum_{e\in\mathcal{E}_{\mathrm{L}}}C_e',23,'报告4.6.3')
            para(root,'cash-flow-definitions',35,449,890,46,'I为初始投资/万元，y为投运年，L为寿命/年，q为固定运维率；基准为2021年末，r=6.00%，T=2041，C为费用现值/万元。',17.5,21)
            table(root,'economic-parameters',35,498,890,60,['共同参数','主变','联络','储能'],[['寿命 / 固定运维率','40年 / 4.20%','40年 / 2.20%','25年 / 3.00%']],[260,210,210,210],[30,30],18)
            para(root,'cash-flow-boundaries',35,567,890,92,'投运与更新：初始投资在投运年发生，固定运维从次年计至2041年；更新年严格早于2041年，本期2022—2035年投运设备的更新支出为零。\n费用范围：纳入新增建设及固定运维；既有建设费、期末残值、被替换设备运维变化、储能购电与损耗及收益抵扣不纳入。',17.5,22,True)
        NOTE={12:'主变更换按整台新购容量计价，净增容量扣除原有被替换设备。王庄与鲁庙工程形成16.57万元每MVA的采购容量加权参考系数。扩建按50 MVA完整项目1223万元计取，限具备预留位置的站点。刚性与弹性方案采用相同供电安全要求，只对新增容量控制作区别。',13:'联络投资由线路敷设与固定接入两部分构成。电缆长度占比通过成本系数进入线路造价，3 km基准工程另计6万元等效开关接入费。邳州和市区单项投资分别为128.38万元和452.40万元，按实际新增投运条数计算。支援还需满足送端可转负荷、共享通道与受端容量条件。',14:'储能采购按100 kW、215 kWh整柜计费，成套项目折算参考单柜21.05万元。有效功率取额定功率和可用电量除以时长的较小值，0.76综合反映SOC可用窗口与单向放电效率。承担1 MW连续支撑任务，2、4、6小时分别需要13、25、37柜。正反向分别采用相应时长，运行应用继续核定充电、恢复和连续SOC。',15:'各投运批次的初始投资、更新和固定运维统一折算至2021年末，再按主变、储能和线路项目集合汇总。固定运维从投运次年计至2041年，更新要求投运年加整倍寿命严格早于2041年。本期2022至2035年投运设备均未触发更新，因此现值比较覆盖新增建设和固定运维。期末残值、替换存量设备运维变化、储能购电和损耗、收益抵扣等尚未纳入，费用降幅按这一共同范围解释。'}
        (W/'notes'/Path(CURRENT).with_suffix('.md').name).write_text(NOTE[i])
    # Only author pages whose visible content or footer changes.
    if i>=3 or 'section'in row:E.ElementTree(root).write(str(A/CURRENT),encoding='utf-8',xml_declaration=False)
(W/'content_map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2))
(W/'formula_sources.json').write_text(json.dumps(FORMULAS,ensure_ascii=False,indent=2))
(W/'new_table_sources.json').write_text(json.dumps(TABLES,ensure_ascii=False,indent=2))
(W/'exports/逐页讲稿_章节导航与成本模型优化版.md').write_text('\n\n'.join('## '+('封面'if r['page']==1 else'章节导航'if r['page']==2 else'第'+str(r['visible_page_number'])+'页')+' '+r['title']+'\n\n'+(W/'notes'/Path(r['svg']).with_suffix('.md').name).read_text()for r in mapping['pages']))
print('Authored',len(mapping['pages']),'pages and',len(FORMULAS),'native formulas')
