"""Author 25 main slides and the necessary readable evidence appendix."""
from pathlib import Path
from lxml import etree as E
from copy import deepcopy
from PIL import Image
import hashlib,json,math,re,shutil,unicodedata

BASE=Path(__file__).resolve().parents[1]; W=BASE/'成果汇报_20261019'; A=W/'authoring-svg-flat';S=W/'sources/original-authoring'
S.mkdir(exist_ok=True)
for n in range(1,5):
    name=f'slide_{n:02d}.svg'
    if not (S/name).exists():shutil.copyfile(A/name,S/name)
for p in [W/'notes',W/'validation',W/'exports']:p.mkdir(exist_ok=True)
NS='http://www.w3.org/2000/svg'; Q=lambda x:'{'+NS+'}'+x
FONT='Microsoft YaHei';G='#007C78';B='#376382';O='#C57434';TXT='#20393E';GRAY='#5E7077';TINT='#EAF3F1';WHITE='#FFFFFF'
TABLES=json.loads((W/'data/report_tables.json').read_text());MAN=json.loads((W/'source_manifest.json').read_text());ROSTER=[];CONTENT=[]
def rows(key):return TABLES[key]['rows']
def el(tag,parent=None,**attrs):
    a=E.Element(Q(tag),{k.replace('_','-'):str(v) for k,v in attrs.items()})
    if parent is not None:parent.append(a)
    return a
def width(s,size):return sum((1 if unicodedata.east_asian_width(c) in 'FW' else .59) for c in s)*size*1.08
def wrap(s,w,size):
    out=[]
    for para in str(s).split('\n'):
        part=''
        for ch in para:
            if part and width(part+ch,size)>w:out.append(part);part=ch
            else:part+=ch
        out.append(part)
    return out
def text(parent,x,y,s,size=22,color=TXT,bold=False,anchor='start',w=None,leading=None):
    ll=wrap(s,w,size) if w else str(s).split('\n');t=el('text',parent,x=x,y=y,font_family=FONT,font_size=size,fill=color,text_anchor=anchor,font_weight='bold' if bold else 'normal');t.text=ll[0]
    for ln in ll[1:]:sp=el('tspan',t,x=x,dy=leading or round(size*1.3,2));sp.text=ln
    return t
def group(root,id,x,y,w,h,role=None):
    g=el('g',root,id=id,font_family=FONT);g.set('data-pptx-bounds',f'{x} {y} {w} {h}')
    if role:g.set('data-pptx-role',role)
    el('rect',g,x=x,y=y,width=w,height=h,fill='none',stroke='none')
    return g
def rect(g,x,y,w,h,fill=TINT,stroke='none',rx=0):return el('rect',g,x=x,y=y,width=w,height=h,fill=fill,stroke=stroke,rx=rx)
def line(g,x1,y1,x2,y2,color=G,sw=2):return el('line',g,x1=x1,y1=y1,x2=x2,y2=y2,stroke=color,stroke_width=sw)
def arrow(g,x1,y1,x2,y2,color=G,sw=4):
    line(g,x1,y1,x2,y2,color,sw);ang=math.atan2(y2-y1,x2-x1);L=12;pts=[(x2,y2),(x2-L*math.cos(ang-.42),y2-L*math.sin(ang-.42)),(x2-L*math.cos(ang+.42),y2-L*math.sin(ang+.42))]
    return el('polygon',g,points=' '.join(f'{x:.2f},{y:.2f}' for x,y in pts),fill=color)
def picture(g,path,x,y,w,h):
    p=Path(path);p=(W/p) if not p.is_absolute() else p
    iw,ih=Image.open(p).size;scale=min(w/iw,h/ih);ww,hh=iw*scale,ih*scale
    return el('image',g,href='../'+str(p.relative_to(W)),x=x+(w-ww)/2,y=y+(h-hh)/2,width=ww,height=hh,preserveAspectRatio='xMidYMid meet')
def table(root,id,headers,data,x=35,y=270,w=890,h=300,size=19,weights=None):
    g=group(root,id,x,y,w,h);g.set('data-pptx-replace-with','table');weights=weights or [1]*len(headers);cw=[w*z/sum(weights) for z in weights]
    linecounts=[max(len(wrap(str(v),cw[j]-12,size)) for j,v in enumerate(row)) for row in [headers]+data]
    rowweights=[n*1.3+.6 for n in linecounts];heights=[h*z/sum(rowweights) for z in rowweights];head=heights[0]
    cols=[];body=[];xx=x
    for j,headtxt in enumerate(headers):
        cols.append({'text':str(headtxt),'align':'ctr','bold':True,'fill':G})
    payload={'schema':'ppt-master.semantic-table.v2','name':id,'x':x,'y':y,'width':w,'height':h,'columns':cols,'rows':body,'column_widths':weights,'row_heights':rowweights,'style':{'font_family':FONT,'font_size':size,'header_font_size':size,'header_fill':G,'header_text':WHITE,'body_fill':WHITE,'body_text':TXT,'band_row':True,'band_fill':'#EFF5F4','border_color':'#D0DEDB','border_width':.6,'padding':3,'valign':'middle'},'defaults':{'cell':{'align':'ctr','valign':'middle'}}}
    md=el('metadata',g,type='application/json');rect(g,x,y,w,head,G)
    for i,row in enumerate([headers]+data):
        yy=y+sum(heights[:i]);hh=heights[i]
        if i>0:
            rect(g,x,yy,w,hh,'#EFF5F4' if i%2==0 else WHITE);body.append([])
        xx=x
        for j,val in enumerate(row):
            val=str(val);isnum=bool(re.fullmatch(r'[+-]?\d+(\.\d+)?%?',val));align='r' if i>0 and isnum else 'ctr';anchor='end' if align=='r' else 'middle';cx=xx+cw[j]-8 if align=='r' else xx+cw[j]/2
            ll=wrap(val,cw[j]-12,size);ty=yy+hh/2-size*1.3*(len(ll)-1)/2+size*.20
            text(g,cx,ty,'\n'.join(ll),size,WHITE if i==0 else TXT,i==0,anchor)
            if i>0:body[-1].append({'text':val,'align':align,'fill':'#EFF5F4' if i%2==0 else WHITE})
            line(g,xx,yy,xx,yy+hh,'#D0DEDB',.6);xx+=cw[j]
        line(g,x,yy+hh,x+w,yy+hh,'#D0DEDB',.6)
    line(g,x+w,y,x+w,y+h,'#D0DEDB',.6);line(g,x,y,x+w,y,'#D0DEDB',.6);md.text=json.dumps(payload,ensure_ascii=False)
    return g
def change(root,gid,value,size=None):
    g=root.find(f'.//{Q("g")}[@id="{gid}"]')
    if g is None:return
    ts=list(g.iter(Q('text')))
    if not ts:return
    t=ts[0]
    if value=='':
        t.getparent().remove(t)
        return
    for c in list(t):t.remove(c)
    t.text=str(value)
    if size:t.set('font-size',str(size))
    t.set('font-family',FONT)
def bodypage(n,section,banner,claim,source):
    root=E.parse(str(S/'slide_03.svg')).getroot()
    for id,val in [('shape-13',str(section)),('shape-14',['','研究背景','研究目标和思路','研究内容','实证分析','项目成效','备查资料'][section]),('shape-2',str(n))]:change(root,id,val)
    change(root,'shape-19',banner,26.67)
    bg=root.find(f'.//{Q("g")}[@id="shape-19"]');bg.set('data-pptx-frame','3.57 145.97 364.43 42.01')
    bp=bg.find(Q('path'));bp.set('d','M 3.57 145.97 L 368 145.97 L 368 187.98 L 3.57 187.98 Z')
    # The imported nested arrow's native local coordinates differ from the SVG's
    # effective coordinates. Author its paint explicitly so the edited group
    # compiles in the same coordinate space as the new title.
    banner=root.find(f'.//{Q("g")}[@id="shape-18"]/{Q("path")}')
    banner.set('fill',G);banner.attrib.pop('filter',None)
    old=root.find(f'.//{Q("g")}[@id="shape-17"]')
    if old is not None:root.remove(old)
    gg=group(root,'page-claim',35,212,890,48);text(gg,35,243,claim,26,G,True,w=890,leading=31)
    fg=group(root,'source-note',35,663,850,30,'footer');text(fg,35,679,'依据：'+source,13,GRAY,w=850,leading=15)
    return root
def insight(root,s,x=35,y=610,w=890,h=48):
    g=group(root,'engineering-takeaway',x,y,w,h);rect(g,x,y,w,h,TINT);text(g,x+12,y+28,s,20,G,w=w-24,leading=24)
def figure(root,name,x=35,y=267,w=890,h=330,id='evidence-figure'):
    g=group(root,id,x,y,w,h);picture(g,'figures/'+name+'.png',x,y,w,h);return g
def blocks(root,items,x=35,y=275,w=890,h=300,cols=2):
    cw=(w-24*(cols-1))/cols;nr=math.ceil(len(items)/cols);rh=(h-20*(nr-1))/nr
    for i,(title,body) in enumerate(items):
        xx=x+(i%cols)*(cw+24);yy=y+(i//cols)*(rh+20);g=group(root,f'explanation-{i+1}',xx,yy,cw,rh)
        line(g,xx,yy+2,xx+cw,yy+2,G,2);text(g,xx+5,yy+29,title,22,G,True,w=cw-10);text(g,xx+5,yy+57,body,19,TXT,w=cw-10,leading=24)
def finalize(root,n,source_slide,title,source,notes):
    name=f'slide_{source_slide:02d}.svg' if n in (1,2,3,25) else f'p{n:02d}.svg'
    root.set('lang','zh-CN');E.ElementTree(root).write(str(A/name),encoding='utf-8',xml_declaration=False)
    (W/'notes'/Path(name).with_suffix('.md').name).write_text(notes.strip())
    row={'source_slide':source_slide}
    if name!=f'slide_{source_slide:02d}.svg':row['svg']=name
    ROSTER.append(row);CONTENT.append({'page':n,'title':title,'source_slide':source_slide,'svg':name,'source':source,'mode':'edited' if n in (1,2,3,25) else 'new_copy','report_sha256':MAN['sha256']})

# 01 cover, original template assets and geometry remain native.
r=E.parse(str(S/'slide_01.svg')).getroot();g=r.find(f'.//{Q("g")}[@id="shape-8"]');t=list(g.iter(Q('text')))[0];g.remove(t)
text(g,480,447,'徐州地区分布式新能源高渗透率地区\n110 kV电网容载比弹性指标优化研究\n成果汇报',31,G,True,anchor='middle',leading=48)
g=r.find(f'.//{Q("g")}[@id="shape-9"]')
for t in list(g.iter(Q('text'))):g.remove(t)
text(g,480,609,'国网江苏电力设计咨询有限公司\n徐州勘测设计分公司\n2026年10月',23,TXT,True,anchor='middle',leading=32);change(r,'shape-7','')
finalize(r,1,1,'成果汇报封面','项目名称及原逻辑参考稿署名','本次汇报围绕分布式新能源高渗透率下110 kV电网容载比与双向容量需求的协调问题，介绍运行特征、工程成本、联合配置结果及规划应用建议。')

# 02 agenda: retain the five-row template geometry; author the rows together
# so native local coordinates cannot displace an unchanged child badge.
r=E.parse(str(S/'slide_02.svg')).getroot()
for g in list(r.findall(Q('g'))):
    if g.get('data-pptx-source-ref','').startswith('slide:') and g.get('id')!='shape-2':r.remove(g)
change(r,'shape-2','2')
for i,(label,number) in enumerate(zip(['研究背景','研究目标和思路','研究内容','实证分析','项目成效'],'一二三四五')):
    y=175+i*98;g=group(r,f'agenda-row-{i+1}',158,y,660,62)
    rect(g,158,y,660,62,G if i==0 else '#F2F2F2',G)
    rect(g,158,y,53,62,G,G)
    text(g,184.5,y+42,number,32,WHITE,True,'middle')
    labelg=group(g,f'agenda-label-{i+1}',219,y,599,62)
    text(labelg,229,y+42,label,32,WHITE if i==0 else TXT,True)
finalize(r,2,2,'汇报目录','确认的五部分汇报逻辑','汇报分为五部分。首先说明规划问题和研究思路，然后介绍运行分析与成本模型，重点报告两地区逐年方案及五参数推荐范围，最后说明成果和应用条件。')

r=bodypage(3,1,'1.1 背景与规划问题','光伏接入使主变同时承担正向供电与反向输送任务','研究报告1.1—1.2；《配电网规划设计技术导则（修订稿，2025年4月）》')
g=group(r,'bidirectional-system',35,270,890,331);picture(g,'images/A1_双向容量任务.png',35,277,890,300)
text(g,300,292,'日间：本地消纳与余电反送',22,G,True,'middle');text(g,660,292,'晚间：上级电网供电',22,B,True,'middle')
arrow(g,300,440,300,357,G,4);arrow(g,660,357,660,440,B,4)
text(g,300,590,'反向容量校核',21,G,True,'middle');text(g,660,590,'正向峰值与主变N-1校核',21,B,True,'middle')
insight(r,'容载比由区域容量与年网供最大负荷共同决定，具体增容需联系站级任务。')
finalize(r,3,3,'双向容量任务','研究报告1.1—1.2','光伏出力较高时，本地负荷由分布式电源供给，剩余功率可能通过主变向上级电网反送。晚间光伏退出后，主变仍承担正向供电。研究据此把区域容载比与逐站正反向容量、主变N-1和站间支援联系起来。')

r=bodypage(4,2,'2.1 研究目标与思路','把片区推荐值落实为满足供电任务的工程配置','研究报告1.4—1.5、图1-1')
items=[('运行资料','年度容量、同范围负荷与光伏，46座站设备和转供资料'),('运行任务','识别正向、反向及局部高峰，保持同小时功率关系'),('工程费用','主变、联络、储能按统一范围及投运批次计费'),('联合比选','逐年承接已投运设备，校核正常与主变N-1条件'),('结果解释','用设备组合、投运时点和分项费用解释差异'),('条件推荐','从十三项候选指标归纳五项参数与查表范围')]
blocks(r,items,y=275,h=315,cols=3);insight(r,'资料、约束、费用和建设安排逐项衔接，形成“一片一策”的容量规划依据。')
finalize(r,4,3,'研究目标与技术路线','研究报告1.4—1.5','研究先从年度统计和站级资料识别运行任务，再用真实工程造价建立统一费用模型。在相同供电条件下联合选择主变、联络和储能，通过逐年设备与费用结果解释弹性容量的作用，并归纳五参数推荐范围。')

r=bodypage(5,3,'3.1 研究对象与数据','邳州与市区分别体现高光伏县域和负荷集中城区','研究报告3.1、表3-12、表5-1')
table(r,'regional-baseline',['2025年指标','邳州','市区'],[['站级分析范围','20座110 kV站','26座110 kV站'],['实际主变容量 / MVA','2139.50','3701.00'],['年网供最大负荷 / MW','956.45','1528.82'],['装机渗透率估计值','1.63','0.32'],['电量渗透率估计值','40%','9%']],y=270,h=260,size=21,weights=[1.6,1,1])
g=group(r,'study-timeline',35,551,890,48);text(g,35,577,'2021基期 → 2022—2025历史回算 → 2026—2035预测条件规划',22,G,True)
insight(r,'时序样本补齐为8760小时；年度规划峰值沿用同范围年度统计与预测输入。')
finalize(r,5,3,'研究对象及数据范围','研究报告3.1、表3-12、表5-1','两地区保留各自源荷与设备特征，站级分析覆盖邳州20座和市区26座110 kV变电站。历史统计用于描述现状，逐年方案以2021年实际容量为共同起点。时序样本按报告方法补齐为8760小时，装机和电量渗透率中相应估计范围保留。')

r=bodypage(6,3,'3.2 历史容量与负荷','两地区容载比变化反映不同的建设与负荷发展过程','研究报告表3-1、表3-2、表3-24');figure(r,'F01_历史容量负荷',h=325);insight(r,'邳州负荷增长快于容量增长；市区容量投放与负荷回落共同影响年度比值。')
finalize(r,6,3,'历史容量负荷变化','表3-1、3-2、3-24','2021—2025年邳州主变容量增加112.50 MVA，年网供最大负荷增加224.68 MW，容载比由2.77降至2.24。市区同期容量增加587.50 MVA，负荷增加79.05 MW，容载比由2.15升至2.42。比值需同时联系容量和负荷，而年度回落年份还应保留已投运设备的作用。')

r=bodypage(7,3,'3.3 光伏发展与渗透率','光伏规模及供能水平差异形成不同的双向运行任务','研究报告3.3、表3-6、表3-12');figure(r,'F02_光伏及渗透水平',h=325);insight(r,'邳州2025年装机渗透率约1.63、电量渗透率约40%；市区分别约0.32、9%。')
finalize(r,7,3,'光伏发展与渗透水平','研究报告3.3、表3-6、3-12','邳州2025年末光伏装机为1559.64 MW，市区为491.18 MW。两地区的装机和电量渗透率表明，邳州更需关注日间反送。未来光伏按报告的全市相对发展比例形成情景，并与负荷预测分别输入。')

r=bodypage(8,3,'3.4 净负荷与近峰特征','正反向峰值及持续过程共同决定容量与支撑需求','研究报告3.4、表3-10；保留补值标识的区域8760小时序列');figure(r,'F03_区域净负荷',h=310)
g=group(r,'peak-statistics',35,579,890,30);text(g,35,600,'95%峰值：邳州最长连续2 h、累计7 h；市区最长连续6 h、累计11 h。',20,G,True)
insight(r,'区域峰值先同小时汇总站级功率，再取绝对值；近峰时长在补齐序列上统计。')
finalize(r,8,3,'净负荷与95%峰值','研究报告3.4、表3-10及原保留时序','净负荷受入为正、反送为负，图中保留补齐后的全年序列。近峰阈值为区域净负荷绝对峰值的95%，邳州最长连续2小时、市区6小时。该统计描述运行过程，年度容载比仍使用年度统计峰值。')

r=bodypage(9,3,'3.5 站级容量压力','区域容量储备与少数站点的局部压力可以同时存在','研究报告表3-8、表3-22、表3-23');figure(r,'F04_46站方向压力',h=320);insight(r,'站级极值逐站比较，配置比选继续校核同期源荷、主变结构和邻站承接余量。')
finalize(r,9,3,'46站运行压力','表3-8、表3-22、表3-23','46座站的正反向极值展示了容量任务在空间上的差异。邳州有4座站反向幅值较大，市区有1座，其他站以正向任务为主。站级负载率是按容量和功率因数折算的计算指标，与逐台设备实测年最大负载率分别使用。')

r=bodypage(10,3,'3.6 核心指标筛选','十三项指标经组内筛选与高相关归并形成五项参数','研究报告3.5、表3-14—3-20');figure(r,'F05_十三项组内相关',x=35,y=270,w=590,h=325)
g=group(r,'selection-logic',650,275,275,315)
for yy,num_,title,detail in [(292,'13','候选指标','源荷、网络、时间及费用'),(398,'9','达到组内筛选要求','相关绝对值不低于0.40'),(504,'5','保留基础规划输入','高相关归并阈值0.70')]:
    text(g,654,yy+29,num_,38,G,True);text(g,715,yy+7,title,21,G,True,w=205);text(g,715,yy+43,detail,18,GRAY,w=205)
insight(r,'研究采用节点等权，保留零容量响应组；两个阈值用于推广维度归纳。')
finalize(r,10,3,'十三项至五项筛选','研究报告3.5、表3-14—3-20','首先在固定其他条件的受控组内，计算候选指标与容载比的Pearson相关，保留零容量响应组。十三项中九项达到绝对值0.40，再以参数间绝对值0.70归并信息重叠较多的组，优先采用具有明确规划含义的基础输入，形成五项推广参数。')

r=bodypage(11,3,'3.7 参数核验与分档','五项参数分别保留不同规划条件的信息','研究报告表3-19、表3-21');figure(r,'F06_五参数相关',x=35,y=274,w=470,h=320)
rr=rows('表3-21');table(r,'parameter-classes',['参数','矩阵分类'],[[a.replace('分布式电源',''),b] for a,b in rr[1:]],x=530,y=275,w=395,h=310,size=16,weights=[.95,1.2]);insight(r,'有效情景库内最大参数间Pearson绝对值为0.29，相关性结合计算关系解释。')
finalize(r,11,3,'五参数相关与分类','表3-19、表3-21','五项参数为装机渗透率、年最大净负荷平均增长率、电缆长度占比、初始转供率和负荷分散系数。有效情景库中最大参数间相关绝对值为0.29，五项保留电源规模、负荷发展、线路经济条件、既有支援和局部峰值分布的信息。')

r=bodypage(12,3,'3.8 工程费用模型','工程投资按采购规模、项目数量和投运时点计取','研究报告4.2—4.3、表4-2、表4-3');figure(r,'F07_费用与有效功率',x=35,y=275,w=520,h=300)
blocks(r,[('主变更换','按整台新购铭牌容量计价；净增容量扣除同期被替换容量'),('主变扩建','50 MVA扩建项目参考投资1223.00万元'),('新增联络','按地区电缆长度占比折算3 km单项费用，既有工程不重复计费')],x=590,y=280,w=335,h=305,cols=1)
insight(r,'邳州、市区单项新增联络参考投资分别为128.38、452.40万元。')
finalize(r,12,3,'工程费用输入','研究报告4.2—4.3','主变更换按整台新购容量计价，扩建按完整项目投资计价，新购容量与净增容量分别反映采购费用和区域容量变化。联络按实际新建条数与地区综合造价计费。三类措施后续统一按投运批次计算评价期费用。')

r=bodypage(13,3,'3.9 储能有效支撑','额定功率与可用电量共同限制持续支撑能力','研究报告4.4—4.6、表4-4、表4-5')
g=group(r,'storage-relationship',35,280,890,155);rect(g,35,280,890,155,TINT);text(g,480,320,'有效支撑功率 = min（额定功率，可用电量 ÷ 支撑时间）',25,G,True,'middle');text(g,480,361,'可用电量系数0.76：结合SOC可用窗口与单向放电效率',21,TXT,False,'middle');text(g,480,401,'柜型：100 kW / 215 kWh；参考投资：21.05万元/柜',22,TXT,True,'middle')
table(r,'storage-duration',['额定配置','2 h有效功率','4 h有效功率','6 h有效功率'],[['1.00 MW / 2.15 MWh','0.82 MW','0.41 MW','0.27 MW']],y=463,h=112,size=22,weights=[1.4,1,1,1]);insight(r,'地区正向支撑取邳州2 h、市区6 h，反向吸收按对应可充电空间与持续要求。')
finalize(r,13,3,'储能有效功率','研究报告4.4—4.6','储能支撑同时受功率和可用电量约束，研究取可用电量系数0.76。对额定1 MW、2.15 MWh配置，2、4、6小时有效支撑分别为0.82、0.41、0.27 MW。时间条件改变可用支撑规模，工程投资仍按新增整数柜及统一单价计取。')

r=bodypage(14,3,'3.10 三类措施联合配置','主变、联络与储能在相同安全约束下共同承担任务','研究报告5.2—5.3')
g=group(r,'planning-resources',35,270,890,320);picture(g,'images/A2_三类规划资源.png',35,275,890,240)
for xx,title,body in [(180,'主变补强','本站与故障后剩余能力'),(480,'联络支援','区段、通道及受端余量'),(780,'储能支撑','功率与可用电量条件')]:text(g,xx,538,title,24,G,True,'middle');text(g,xx,575,body,20,TXT,False,'middle')
insight(r,'正常运行负载率≤80%；最大单台主变N-1时剩余设备短时负载率≤130%。')
finalize(r,14,3,'三类资源联合配置','研究报告5.2—5.3','三类措施在同一供电任务下联合选择，设备按可选额定容量、台数和整台投运，储能柜数及新增联络数量取整数。正常运行和最大单台主变N-1条件共同限制方案，储能与转供在同年设备状态下参与容量支撑。')

r=bodypage(15,3,'3.11 逐年比选与经济评价','相同基期和源荷输入下比较完整建设路径','研究报告5.1—5.3、表4-1、表5-1、表5-3')
blocks(r,[('共同起点','2021年实际主变容量：邳州2027.00 MVA，市区3113.50 MVA'),('刚性基准','新增扩容按当年负荷两倍控制，负荷回落时保留上年在役容量'),('弹性方案','放宽2.0新增容量控制，在相同承载要求下比较措施费用'),('费用现值','投运批次折算至2021年末，统一评价到2041年，折现率6.00%')],y=280,h=305,cols=2)
insight(r,'费用包括新增建设及固定运维；地区结果为满足所设条件的具体可行方案。')
finalize(r,15,3,'逐年方案比较边界','研究报告5.1—5.3','两类方案使用相同2021年实际容量和各年源荷，后续承接已投运设备。刚性基准对新增扩容实行容量控制，弹性方案在相同正常和故障约束下比较主变、储能与联络费用。比较统一评价期内新增措施费用现值，不将求解可行结果称为已证明全局最优。')

r=bodypage(16,4,'4.1 邳州逐年方案','邳州弹性方案增加站内容量并减少部分配套需求','研究报告表5-4、表5-5、表5-9');figure(r,'F08_邳州逐年方案',y=269,h=330);insight(r,'2035年弹性容载比2.06、主变2901.00 MVA；全期费用较刚性减少848.32万元。')
finalize(r,16,3,'邳州逐年方案','表5-4、表5-5、表5-9','邳州弹性方案在若干建设节点形成更多站内容量，后期储能和联络需求相应改变。2035年弹性主变2901.00 MVA、容载比2.06，刚性分别为2678.00 MVA、1.90。全期弹性费用57521.36万元，比刚性减少848.32万元。')

r=bodypage(17,4,'4.2 市区逐年方案','市区费用优势由建设时序和联络替代逐步形成','研究报告表5-6、表5-7、表5-9');figure(r,'F09_市区逐年方案',y=269,h=330);insight(r,'2022年两方案相同，2030年弹性累计费用仍较高；全期费用减少2050.35万元。')
finalize(r,17,3,'市区逐年方案','表5-6、表5-7、表5-9','市区2022年两方案相同，2030年弹性累计费用仍高于刚性，后续建设共同形成全期费用优势。2035年弹性主变3608.50 MVA、容载比1.62，储能额定能量109.65 MWh高于刚性92.88 MWh，累计新增联络则从66条降至35条。全期费用减少2050.35万元。')

r=bodypage(18,4,'4.3 评价期费用分解','新增主变支出由其他措施费用下降部分抵消','研究报告表5-9、表5-11');figure(r,'F10_措施费用差',y=270,h=280)
table(r,'total-cost',['方案费用现值 / 万元','刚性','弹性','减少'],[['两地区合计','98006.53','95107.86','2898.67']],y=565,h=81,size=21,weights=[1.5,1,1,1])
finalize(r,18,3,'措施费用比较','表5-9、表5-11','两地区弹性方案的主变费用均增加，但储能及联络费用变化不同。邳州储能和联络费用下降共同抵消新增主变支出；市区主要由联络费用下降形成优势，储能费用略增。两地区合计费用现值减少2898.67万元，降幅2.96%。')

r=bodypage(19,4,'4.4 2035年设备组合','两类片区通过不同措施组合满足局部供电任务','研究报告表5-10');figure(r,'F11_2035设备组合',h=325);insight(r,'邳州弹性储能与联络均减少；市区弹性储能增加、联络减少，需分别解释。')
finalize(r,19,3,'期末设备组合','表5-10','2035年邳州弹性储能545.67 MWh、累计新增联络21条，刚性分别为568.25 MWh、58条。市区弹性储能109.65 MWh高于刚性，但累计新增联络35条低于刚性66条。容量、储能和联络必须作为同一配置组合比较。')

r=bodypage(20,4,'4.5 代表站设备分析','主变台数组合改变N-1剩余能力及局部支撑需求','研究报告表5-13、表5-15、表5-31及对应逐站分析')
table(r,'station-examples',['2035年站点','刚性主变 / MVA','弹性主变 / MVA','差异对应的任务'],[['戴圩变','50+63','50+63+50','弹性扩建第三台，减少本地配储'],['兴塘变','31.5+40+50','31.5+50+50','故障后剩余容量71.50→81.50 MVA'],['八义集变','50+63','50+63','容量相同，储能功率3.10→0.30 MW']],y=275,h=225,size=20,weights=[1,1.1,1.2,2])
blocks(r,[('设备位置与台数','增容效果取决于最大单台停运后剩余的实际设备组合'),('年度转接与本地储能','相同区域容量可对应不同转供任务及支撑规模')],y=530,h=100,cols=2)
finalize(r,20,3,'代表站差异分析','报告逐站分析及表5-13、5-15、5-31','戴圩变弹性方案扩建第三台50 MVA主变，2035年总容量由刚性113.00 MVA提高到163.00 MVA，配储需求改变。兴塘变通过不同主变组合提高N-1剩余容量；八义集变则在总容量相同条件下，储能和年度固定转接任务不同。逐站解释均对应本站实际配置。')

r=bodypage(21,4,'4.6 联络与共享资源','转供支援由源端、路径及接收侧能力共同决定','研究报告3.6、5.5、表5-59—5-61')
g=group(r,'transfer-topology',35,275,890,300)
for xx,title,desc in [(55,'源端站','可切换源荷区段'),(360,'共享馈线与联络','既有MW额度及通道热限'),(680,'受端站','馈线余量与主变容量')]:
    node=el('g',g);rect(node,xx,320,220,115,TINT,G);text(node,xx+110,358,title,23,G,True,'middle');text(node,xx+110,400,desc,19,TXT,False,'middle')
arrow(g,280,378,350,378);arrow(g,585,378,670,378);line(g,473,436,473,495,G,2)
rect(g,305,495,335,63,WHITE,G);text(g,472,535,'多条联络共用馈线与区段预算',21,G,True,'middle')
header=el('g',g);rect(header,100,275,760,40,'none');text(header,480,298,'正常方式与主变N-1分别安排年度固定转供方案',22,G,True,'middle')
g=group(r,'transfer-rating',35,570,890,32);text(g,35,591,'新增联络：485 A折算7.98 MW，工程取8.00 MW；示例区段有效转供7.49 MW。',18,TXT)
insight(r,'区段内负荷与光伏共同切换，区域内同小时转出与承接保持平衡。')
finalize(r,21,3,'联络约束与资源共享','研究报告3.6与5.5','联络将具体源荷区段切换至有余量的受端，负荷和区段内光伏共同切换。既有转供能力以逐站MW封顶，正常与事故追加共同占用路径和共享馈线预算。10 kV、485 A和功率因数0.95按三相有功关系折算为7.98 MW，工程取8.00 MW，示例区段有效转供7.49 MW。新增工程按实际项目计费，支撑作用通过源端可切负荷、通道和受端主变校核。')

r=bodypage(22,4,'4.7 五参数推荐范围','按片区条件定位推荐带，再核定具体设备方案','研究报告5.6、表3-21、表5-63')
steps=[('① 电缆占比','确定三类造价分区'),('② 负荷分散','按1.15划分两档'),('③ 源荷条件','增长率与装机渗透率选行'),('④ 初始转供','定位推荐区间列')]
for i,(t,s) in enumerate(steps):
    xx=35+i*225;g=group(r,f'lookup-step-{i}',xx,278,213,103);rect(g,xx,278,213,103,TINT);text(g,xx+12,313,t,23,G,True);text(g,xx+12,349,s,17,TXT,w=190)
example=next(row for row in rows('表5-63')[1:] if row[0]=='>7%' and row[1]=='(1,2]')
table(r,'lookup-example',['初始转供率','≤30%','(30%,50%]','(50%,70%]','>70%'],[['推荐容载比']+example[2:]],y=419,h=102,size=19,weights=[1.2,1,1,1,1])
g=group(r,'lookup-condition',35,540,890,62);text(g,35,565,'示例条件：电缆长度占比≤10%，负荷分散系数≤1.15，',20,TXT);text(g,35,593,'年最大净负荷平均增长率>7%，装机渗透率(1,2]。',20,TXT)
insight(r,'六表288单元；基准宽0.10、定位网格0.02，接近容量水平按中点共用界值。')
example_notes='、'.join(v.replace('～','至') for v in example[2:])
finalize(r,22,3,'推荐矩阵查表','研究报告5.6、表5-63','矩阵先按三档电缆占比和两档负荷分散系数选表，再以增长率和装机渗透率选行、初始转供率选列。示例四档推荐窗口为'+example_notes+'。各格由最接近中位数的真实节点定位基准宽0.10窗口，同距取较大值，定位网格为0.02，相近容量水平按中点共用界值并局部缩窄。查表后按实际主变、扩建位置和网络条件形成设备方案。')

r=bodypage(23,4,'4.8 参数响应与设备切换','网络支援改善体现为分档推荐带和设备组合变化','研究报告表5-69—5-75');figure(r,'F12_完整转供响应',x=35,y=270,w=890,h=270,id='transfer-response')
g=group(r,'response-interpretation',35,553,890,49);text(g,35,574,'装机与负荷增长改变容量任务；电缆造价和局部峰值分布可触发措施替代。',20,TXT,w=890)
insight(r,'两组均保留9个转供节点，平台与局部回升对应真实设备组合。')
finalize(r,23,3,'完整参数响应','表5-69—5-75','两组典型转供场景在设备重新选配条件下保留10%至90%的九个细节点，容量随转供改善总体降低，同时存在真实平台和局部回升。装机渗透率提高影响反向任务，增长率同时改变负荷分母与建设需求，电缆造价和局部峰值分散则在部分节点触发措施替代。推荐范围与具体设备响应共同使用。')

r=bodypage(24,5,'5.1 研究成果与规划应用','形成从运行特征到片区工程建议的完整研究链条','研究报告第六章、5.7')
blocks(r,[('运行特征与参数','46站分析、两层筛选及五项参数，解释地区差异'),('工程成本与联合配置','主变、储能和联络费用，逐年正常与N-1共同校核'),('地区方案与推荐范围','两地区建设路径、分项费用，六张条件推荐矩阵'),('一片一策应用','先查表，再落实设备和投运时点，结合新增资料滚动更新')],y=275,h=300,cols=2)
insight(r,'工程实施继续核实真实馈线、连续SOC、电压与保护条件，完善运行费用与资产价值。')
finalize(r,24,3,'成果与应用条件','研究报告第六章','研究形成运行特征、工程费用、地区逐年方案和五参数推荐矩阵四类成果。两地区所设条件下弹性费用现值合计降低2.96%，具体建设路径随片区源荷和网络条件变化。工程采用时还需核定连续储能运行、实际网络及相关费用条件，滚动更新设备与推荐范围。')

r=E.parse(str(S/'slide_04.svg')).getroot();change(r,'shape-2','25');finalize(r,25,4,'谢谢','模板封底','汇报完毕，敬请各位专家批评指正。')

for n,key,reg in [(26,'表5-4','邳州'),(27,'表5-6','市区')]:
    r=bodypage(n,6,'备查：逐年配置',reg+'逐年主变、储能及累计新增联络对照','研究报告'+key)
    rr=rows(key)[1:];data=[]
    for year in range(2021,2036):
        a=next(x for x in rr if x[0]=='刚性' and int(x[1])==year);b=next(x for x in rr if x[0]=='弹性' and int(x[1])==year)
        data.append([str(year)]+[a[k] for k in [3,4,5,6]]+[b[k] for k in [3,4,5,6]])
    table(r,'annual-comparison',['年份','刚性容量','刚性比值','刚性储能','刚性新线','弹性容量','弹性比值','弹性储能','弹性新线'],data,y=269,h=350,size=16,weights=[.65,1.1,.9,1.05,.85,1.1,.9,1.05,.85])
    g=group(r,'annual-units',35,632,890,26);text(g,35,651,'单位：容量MVA，储能为在役额定功率MW；新线为累计新增联络条数。',17,GRAY)
    finalize(r,n,3,'备查'+reg+'逐年配置',key,'本页逐年列示刚性和弹性方案的在役容量、容载比、储能额定功率和累计新增联络。历史年度为同一模型下的回算，未来为报告预测条件下的结果。')

r=bodypage(28,6,'备查：方法与经济参数','采样设计、有效样本和共同经济条件分别登记','研究报告表3-14、表3-15、表4-1')
data=[[x[0].replace('分布式电源','').replace('主变与线路单位功率投资比','主变/线路投资比').replace('主变与储能单位功率投资比','主变/储能投资比'),x[2],y[1],y[2]] for x,y in zip(rows('表3-14')[1:],rows('表3-15')[1:])]
table(r,'sampling-details',['候选指标','取点/计算','有效组数','有效节点数'],data,y=269,h=330,size=16,weights=[2.4,1.3,1,1.2])
g=group(r,'economic-parameters',35,608,890,54);text(g,35,630,'寿命：主变/线路/储能40/40/25年；维护费率4.2%/2.2%/3%；折现率6%。',17,GRAY);text(g,35,651,'评价基准2021年、截止2041年；采样实际取值节点保留于报告表3-14。',17,GRAY)
finalize(r,28,3,'备查采样及经济参数','表3-14、表3-15、表4-1','候选参数的取点与有效统计样本分别列示，参数间相关阈值仅用于本研究维度归纳。所有地区方案采用相同寿命、维护费率、折现率与共同评价期。')

for n,key,title,diversity in [(29,'表5-63','电缆长度占比≤10%','≤1.15'),(30,'表5-64','电缆长度占比≤10%','>1.15'),(31,'表5-65','电缆长度占比(10%,30%]','≤1.15'),(32,'表5-66','电缆长度占比(10%,30%]','>1.15'),(33,'表5-67','电缆长度占比>30%','≤1.15'),(34,'表5-68','电缆长度占比>30%','>1.15')]:
    r=bodypage(n,6,'备查：容载比推荐矩阵',title+'，负荷分散系数'+diversity,'研究报告'+key)
    rr=rows(key);hdr=['年最大净负荷平均增长率','装机渗透率']+rr[0][2:];table(r,'recommendation-matrix',hdr,rr[1:],y=270,h=355,size=17,weights=[1.45,1,1.2,1.2,1.2,1.2]);
    g=group(r,'matrix-note',35,636,890,25);text(g,35,654,'列为初始转供率；窗口基准宽0.10，相近水平按中点局部接续。',18,GRAY)
    finalize(r,n,3,'备查'+title+'、分散系数'+diversity+'矩阵',key,'本页负荷分散系数'+diversity+'，完整列出相应电缆占比分区下的推荐窗口。读取行列时同时核对增长率、装机渗透率及初始转供率。系数仿真范围1.05至1.25，每0.02取点，窗口用于初步容量比选。')

r=bodypage(35,6,'备查：四类参数响应','参数通过不同工程机制触发容量配置切换','研究报告表5-72—5-75');figure(r,'F13_四参数设备响应',y=270,h=335);insight(r,'分散系数三个增容节点形成四个平台，平台内储能和联络仍有调整。')
finalize(r,35,3,'备查四类参数响应','表5-72—5-75','装机渗透率、增长率、电缆长度占比和负荷分散系数分别改变源荷任务、比值分母、线路造价和局部峰值条件。负荷分散系数完整11节点中，1.11、1.21和1.25触发增容，形成2.05、2.14、2.26、2.43四个容量平台。平台内仍需调整储能和联络，完整节点见下一页。')

r=bodypage(36,6,'备查：局部高峰与设备替代','容量平台内的储能和联络仍随局部高峰调整','研究报告5.6.8、表5-75及对应11节点序列');figure(r,'F14_分散系数完整设备响应',y=276,h=306)
g=group(r,'diversity-condition',35,588,890,24);text(g,35,605,'固定条件：装机渗透率2.00，年最大净负荷平均增长率4%，电缆10%，转供40%。',18,GRAY)
insight(r,'1.11增容替代8.80 MW储能；1.21再次增容取消储能，1.25配10项联络。',y=619,h=42)
finalize(r,36,3,'备查负荷分散系数完整设备响应','表5-75及对应11节点原始序列','完整保留1.05至1.25、间隔0.02的11个节点，其余源荷和网络条件相同。1.11增容26 MVA替代8.80 MW储能并减少一项联络；其后同一容量平台内继续调整配套措施。1.21再次增容并取消储能，1.25容量达到710 MVA、配10项联络。全序列费用现值从4310.32万元增至8339.97万元。')

assert len(ROSTER)==36
(W/'page_plan.json').write_text(json.dumps({'schema':'ppt-master.roundtrip-page-plan.v1','pages':ROSTER},ensure_ascii=False,indent=2))
(W/'content_map.json').write_text(json.dumps({'user_confirmation':'25页主汇报，保留必要备查；20261020用户确认报告已定稿','main_pages':25,'appendix_pages':11,'appendix_reason':'六张矩阵各用一页，逐年结果、采样和四类响应保留，新补一页解释定稿新增的分散系数容量平台与配套替代','report_sha256':MAN['sha256'],'pages':CONTENT},ensure_ascii=False,indent=2))
(W/'animations.json').write_text(json.dumps({'version':1,'defaults':{'animation':{'effect':'none'},'transition':{'effect':'none','auto_advance':None}},'slides':{Path(c['svg']).stem:{'animation':{'effect':'none'},'transition':{'effect':'none','auto_advance':None}} for c in CONTENT}},ensure_ascii=False,indent=2))
(W/'exports/逐页讲稿.md').write_text('\n\n'.join('## '+str(c['page'])+' '+c['title']+'\n\n'+(W/'notes'/Path(c['svg']).with_suffix('.md').name).read_text() for c in CONTENT))
print(json.dumps({'pages':len(CONTENT),'main':25,'appendix':11,'report_hash':MAN['sha256']},ensure_ascii=False))
