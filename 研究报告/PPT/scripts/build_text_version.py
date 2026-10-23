"""Add report-backed explanation to the imported V1 deck; never overwrite V1."""
from pathlib import Path
from lxml import etree as E
from PIL import Image
from copy import deepcopy
import json,unicodedata,re,hashlib,math

B=Path(__file__).resolve().parents[1];W=B/'成果汇报_文字增强版_20261021';A=W/'authoring-svg-flat';S=W/'sources/authoring-baseline'
NS='http://www.w3.org/2000/svg';Q=lambda s:'{'+NS+'}'+s
G='#007C78';BLUE='#376382';TXT='#20393E';GRAY='#5E7077';TINT='#EAF3F1';FONT='Microsoft YaHei'
OLD=json.loads((B/'成果汇报_20261019/content_map.json').read_text())['pages'];MAN=json.loads((W/'source_manifest.json').read_text());MAP=[]
def el(tag,parent=None,**attrs):
    z=E.Element(Q(tag),{k.replace('_','-'):str(v)for k,v in attrs.items()})
    if parent is not None:parent.append(z)
    return z
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
    return t,len(ll)
def group(r,id,x,y,w,h):
    g=el('g',r,id='v2-'+id,font_family=FONT);g.set('data-pptx-bounds',f'{x} {y} {w} {h}');el('rect',g,x=x,y=y,width=w,height=h,fill='none',stroke='none');return g
def rect(g,x,y,w,h,fill=TINT,stroke='none'):return el('rect',g,x=x,y=y,width=w,height=h,fill=fill,stroke=stroke)
def line(g,x1,y1,x2,y2,color=G,sw=2):return el('line',g,x1=x1,y1=y1,x2=x2,y2=y2,stroke=color,stroke_width=sw)
def arrow(g,x1,y1,x2,y2):
    line(g,x1,y1,x2,y2,G,3);a=math.atan2(y2-y1,x2-x1);L=11
    points=[(x2,y2),(x2-L*math.cos(a-.45),y2-L*math.sin(a-.45)),(x2-L*math.cos(a+.45),y2-L*math.sin(a+.45))]
    el('polygon',g,points=' '.join(f'{x:.2f},{y:.2f}'for x,y in points),fill=G)
def frame(g):return [float(s)for s in g.get('data-pptx-frame','0 0 0 0').split()]
def isbody(g):
    ff=frame(g);return g.get('data-pptx-source-ref','').startswith('slide:')and 265<=ff[1]<660
def wipe(r,keep=()):
    for g in list(r.findall(Q('g'))):
        if isbody(g)and g.get('id')not in keep:r.remove(g)
def find_table(r):return [g for g in r.findall(Q('g'))if isbody(g)and g.get('data-pptx-native-authority')=='json']
def old_picture(r):
    for g in r.findall(Q('g')):
        if isbody(g)and g.get('data-pptx-native-authority')!='json':
            z=g.find('.//'+Q('image'))
            if z is not None:return z.get('href'),deepcopy(g)
    raise ValueError('No body picture')
def picture(r,id,path,x=35,y=267,w=890,h=269):
    path=Path(path);file=path if path.is_absolute()else(A/path).resolve();iw,ih=Image.open(file).size;s=min(w/iw,h/ih);ww,hh=iw*s,ih*s
    g=group(r,id,x,y,w,h);el('image',g,href='../'+str(file.relative_to(W.resolve())),x=x+(w-ww)/2,y=y+(h-hh)/2,width=ww,height=hh,preserveAspectRatio='xMidYMid meet');return g
def fig(r,id,name,**kwargs):return picture(r,id,(W/'figures'/name).resolve(),**kwargs)
def paragraphs(r,id,pp,y=543,h=115,size=18.5,leading=24,x=35,w=890,background=False):
    g=group(r,id,x,y,w,h)
    if background:rect(g,x,y,w,h,TINT)
    yy=y+20;used=[]
    for p in pp:
        ll=wrap('▪ '+p,w-24,size);t=el('text',g,x=x+12,y=yy,font_family=FONT,font_size=size,fill=TXT)
        first=ll[0];label,sep,rest=first.partition('：');t.text='▪ '
        if sep:
            lead=el('tspan',t,fill=G,font_weight='bold');lead.text=label.removeprefix('▪ ')+'：';lead.tail=rest
        else:t.text=first
        for ln in ll[1:]:el('tspan',t,x=x+12,dy=leading).text=ln
        yy+=len(ll)*leading+6;used.append(len(ll))
    assert yy-leading-6+size*.3<=y+h+1,(id,used,yy,y+h)
    return g
def block(r,id,x,y,w,h,title,body,size=18):
    g=group(r,id,x,y,w,h);line(g,x,y+2,x+w,y+2);text(g,x+5,y+25,title,21,G,True,w=w-10,leading=25)
    _,nn=text(g,x+5,y+50,body,size,w=w-10,leading=23)
    assert 50+(nn-1)*23+size*.3<=h,(id,nn,h)
    return g

SPECS={
3:{'source':'研究报告1.1—1.2、1.4','paragraphs':[
 '运行变化：日间光伏优先供应本地负荷，剩余电力经主变反送；晚间光伏退出，主变继续承担正向供电任务。',
 '规划问题：区域容载比由主变容量和年网供最大负荷共同决定，站级需求还受主变台数、局部峰值和邻站支援影响。',
 '研究任务：结合邳州与市区源荷特征，在正常运行和主变N-1条件下联合比选主变、储能与10 kV联络，形成分片区的容量规划建议。']},
4:{'source':'研究报告1.4—1.5、图1-1','blocks':[
 ('① 运行资料','整理年度容量、同范围负荷和光伏，匹配46座站的设备、净负荷与既有转供资料。'),
 ('② 运行任务','按同小时功率关系识别正向供电、日间反送及局部近峰过程，明确站级容量需求。'),
 ('③ 工程费用','区分主变更换与扩建，按储能柜数和新增联络项目计费，并统一折算投运批次费用。'),
 ('④ 联合比选','逐年承接已投运设备，在正常与主变N-1约束下共同选择主变、储能和联络措施。'),
 ('⑤ 结果解释','联系设备台数组合、建设节点与分项费用，解释地区差异及各措施的替代关系。'),
 ('⑥ 条件推荐','由十三项候选指标筛选五项参数，按片区条件组织推荐矩阵，再落实具体工程方案。')]},
5:{'source':'研究报告3.1、3.3、5.1','paragraphs':[
 '统计与仿真：现状统计描述实际容量与源荷；逐年方案以2021年实际容量为共同起点，2022—2025年为历史回算，2026—2035年为预测条件规划。',
 '指标含义：装机渗透率为光伏装机与用户最大负荷之比，电量渗透率为光伏年发电量占用户年用电量的比例；本页两项均为报告估计值。']},
6:{'source':'研究报告3.1、表3-1—3-2、3.7','paragraphs':[
 '邳州：2021—2025年容量增加112.50 MVA、负荷增加224.68 MW，负荷增长快于容量增长，容载比由2.77降至2.24。',
 '市区：同期容量增加587.50 MVA，负荷增加79.05 MW，容载比由2.15升至2.42；年度比值需结合容量投放与负荷回落共同解释。']},
7:{'source':'研究报告3.3、表3-6、表3-12','paragraphs':[
 '地区差异：2025年邳州光伏装机1559.64 MW、市区491.18 MW，装机与电量渗透水平均为邳州较高，日间反送任务更突出。',
 '规划作用：光伏出力改变正反向净负荷，容量校核需同时覆盖日间反送和晚间供电；未来装机按报告预测情景输入，并与负荷预测共同作用。']},
8:{'source':'研究报告3.4、表3-10及区域8760小时序列','paragraphs':[
 '近峰过程：以区域净负荷绝对峰值的95%为阈值，邳州最长连续2 h、累计7 h，市区分别为6 h、11 h，反映两地区持续支撑任务的差异。',
 '计算关系：先按同一小时汇总站级净负荷再取区域峰值，统计使用补齐后的8760小时序列；年度容载比继续采用年度统计峰值。']},
9:{'source':'研究报告3.4、3.6、表3-8、表3-22—3-23','paragraphs':[
 '空间差异：46座站分别呈现正向与反向容量任务，邳州4座、市区1座站反向幅值较大，区域容量储备与少数站局部压力可以同时存在。',
 '设备判断：本站可用能力取决于主变结构及N-1剩余容量，邻站支援还受路径和受端余量限制；应把站级净负荷、设备与转供条件共同纳入比选。']},
10:{'source':'研究报告3.5.2—3.5.5、表3-14—3-20','paragraphs':[
 '统计说明：采用受控组内Pearson相关、节点等权并保留零响应组。0.40与0.70用于本研究参数归纳，筛选结果结合计算关系和规划含义解释。']},
11:{'source':'研究报告3.5.4—3.5.5、表3-19、3-21','paragraphs':[
 '五项参数分别保留电源规模、负荷发展、联络造价、既有支援和局部峰值分布的信息。有效情景库内最大参数间Pearson绝对值为0.29，结合计算关系核验后用于推广分档。']},
12:{'source':'研究报告4.2—4.3、表4-2—4-3','blocks':[
 ('主变更换','按整台新购铭牌容量计价，净增容量扣除同期被替换容量，采购支出与增容效果分别核算。'),
 ('主变扩建','按完整扩建项目计费，50 MVA扩建参考投资1223.00万元，实际方案还受预留位置限制。'),
 ('新增联络','以电缆长度占比折算3 km项目费用，既有工程不重复计建设费，新增项目按投运年计费。')],
 'paragraphs':['地区造价：邳州、市区单项新增联络参考投资分别为128.38、452.40万元。电缆占比提高使联络支援成本上升，进而影响其与站内补强、配储的费用比较。']},
13:{'source':'研究报告4.4.3—4.4.4、图4-5','paragraphs':[
 '采购规模：同样承担1.00 MW连续支撑任务，2 h、4 h、6 h分别需要13、25、37柜。较长持续时间受可用电量限制，柜数按整数取值，进而形成对应投资。']},
14:{'source':'研究报告5.2—5.3、表5-3','blocks':[
 ('主变补强','更换或扩建改变本站容量与最大单台停运后的剩余能力，设备按可选额定容量、台数和整台投运。'),
 ('联络支援','切换具体源荷区段至有余量的受端，支援能力由可切负荷、共享通道和接收主变共同限制。'),
 ('储能支撑','以额定功率和可用电量共同折算有效功率，按整数柜配置，并与同年的主变及转供方案衔接。')]},
15:{'source':'研究报告5.1—5.3、表4-1、表5-1、表5-3','blocks':[
 ('共同起点与承接','以2021年实际容量为基期，邳州2027.00 MVA、市区3113.50 MVA。后续各年承接已投运设备，源荷输入与安全要求保持一致。'),
 ('刚性基准','新增扩容按当年负荷两倍控制，负荷回落时保留上年在役容量；局部任务继续由储能和联络共同承担。'),
 ('弹性方案','放宽2.0新增容量控制，在相同正常和故障承载要求下比较措施组合，结合站级缺口和受端承接能力形成设备方案。'),
 ('统一费用评价','投运批次折算至2021年末，评价截止2041年，折现率6.00%。建设和固定运维计入费用，比较完整建设路径的新增支出。')]},
16:{'source':'研究报告5.4.1、表5-4、5-5、5-9—5-11','paragraphs':[
 '容量路径：弹性方案在局部需求出现时增加站内容量，2035年达到2901.00 MVA、容载比2.06；刚性分别为2678.00 MVA、1.90。',
 '措施替代：期末弹性储能545.67 MWh、累计新增联络21条，均低于刚性。储能及联络支出下降抵消较多主变投入，全期费用减少848.32万元。']},
17:{'source':'研究报告5.4.2、表5-6、5-7、5-9—5-11','paragraphs':[
 '建设时序：弹性前期以站内补强承接局部需求，2030年累计费用16806.54万元，高于刚性14819.77万元；费用优势由后续各年工程支出共同形成。',
 '期末组合：2035年弹性储能109.65 MWh高于刚性92.88 MWh，累计新增联络由66条减至35条；联络费用下降支持全期减少2050.35万元。']},
18:{'source':'研究报告5.4.4、表5-9、5-11','paragraphs':[
 '费用来源：邳州由储能和联络费用下降共同抵消较多主变支出，市区主要由联络费用下降形成优势。两地区合计减少2898.67万元，降幅2.96%。']},
19:{'source':'研究报告5.4.3—5.4.4、表5-10','paragraphs':[
 '邳州组合：弹性主变容量较大，期末储能由刚性568.25 MWh减至545.67 MWh，累计新增联络由58条减至21条，站内容量与配套支撑共同调整。',
 '市区组合：弹性主变仅较刚性多21.50 MVA，储能增加而联络减少。区域容量接近时，各站缺口和建设时点仍会形成不同的支撑配置与费用。']},
20:{'source':'研究报告5.4.5对应逐站分析、表5-13、5-15、5-31','blocks':[
 ('结构作用','扩建第三台与更换已有主变，对最大单台停运后剩余容量的改善不同。兴塘变的71.50与81.50 MVA对应两方案实际设备组合。'),
 ('局部任务','八义集变两方案主变容量相同，年度固定转接任务与配储需求仍有差异。逐站分析需联系本站源荷、受端承接和设备状态解释。')]},
21:{'source':'研究报告3.6、4.3.3、5.5','paragraphs':[
 '共同校核：区段内负荷与光伏一同切换，源端可切负荷、路径共享和受端主变余量共同限制转供；正常与N-1分别采用年度固定方案。',
 '工程取值：10 kV、485 A及功率因数0.95折算有功7.98 MW，工程上限取8.00 MW；示例区段有效转供7.49 MW，新增项目按投运年计费。']},
22:{'source':'研究报告5.6.2、表5-63','paragraphs':[
 '窗口用于容量初选，再按站级缺口、主变结构与可实施措施落实设备方案。']},
23:{'source':'研究报告5.6.3—5.6.8、表5-69—5-75','paragraphs':[
 '受控对照：两组均固定装机渗透率50%、电缆长度占比50%，采用设备重新选配条件，保留初始转供率10%—90%的九个细节点。',
 '响应机制：转供改善总体降低容量需求，平台与局部回升对应真实设备组合。其他参数分别改变反向任务、负荷规模、线路造价和局部高峰，触发不同措施替代。']},
24:{'source':'研究报告第六章、5.7','blocks':[
 ('运行特征与参数','完成46站正反向任务分析，经两层筛选形成五项参数，把电源、负荷、网络和局部峰值条件与容量规划联系起来。'),
 ('工程费用与联合配置','建立主变更换、扩建、储能柜和联络项目的统一费用关系，在正常与N-1条件下逐年承接设备，解释措施替代。'),
 ('地区方案与推荐矩阵','两地区弹性方案费用现值合计减少2898.67万元、降幅2.96%。六表288单元提供有条件的容量初选窗口。'),
 ('一片一策落地','先核定同范围源荷与网络参数，再查表并落实设备、间隔和投运时点；结合真实馈线与储能运行资料滚动更新。')]}
}

for n,spec in SPECS.items():
    root=E.parse(str(S/f'slide_{n:02d}.svg')).getroot();pp=spec.get('paragraphs',[]);bl=spec.get('blocks',[])
    if n==3:
        href,_=old_picture(root);wipe(root);picture(root,'concept-plate',href,x=35,y=304,w=590,h=246)
        g=group(root,'concept-labels',35,270,590,294)
        text(g,182,291,'日间：本地消纳与余电反送',18,G,True,anchor='middle');text(g,478,291,'晚间：上级电网供电',18,BLUE,True,anchor='middle')
        arrow(g,182,438,182,369);arrow(g,478,369,478,438)
        text(g,182,556,'反向容量校核',18,G,True,anchor='middle');text(g,478,556,'正向峰值与主变N-1校核',18,BLUE,True,anchor='middle')
        block(root,'background-day',640,277,285,135,'双向运行',pp[0].split('：',1)[1],17.5)
        block(root,'background-plan',640,420,285,135,'区域与站级',pp[1].split('：',1)[1],17.5)
        paragraphs(root,'background-task',[pp[2]],y=562,h=93,size=19)
    elif n in [4,15,24]:
        wipe(root);cols=3 if n==4 else 2;cw=(890-24*(cols-1))/cols;rh=153 if n==4 else 151;start=274
        for j,(title,body)in enumerate(bl):block(root,f'method-{n}-{j}',35+j%cols*(cw+24),start+j//cols*(rh+18),cw,rh,title,body,18)
        note={4:'研究输出：由运行特征、费用与设备结果形成五参数推荐范围，服务分片区容量规划。',15:'比较结果为所设条件下的具体可行方案，费用优势由各年度主变、储能与联络现金流共同支持。',24:'应用条件：工程实施继续核定连续SOC、电压与保护条件，并补充运行费用和资产价值。'}[n]
        paragraphs(root,f'closing-{n}',[note],y=616,h=44,size=18,background=True)
    elif n==5:
        keep=[g.get('id')for g in find_table(root)];wipe(root,keep);paragraphs(root,'data-notes',pp,y=540,h=118,size=18)
    elif n in [6,7,8,9,16,17,19,23]:
        wipe(root);name={6:'V2_F01_历史容量负荷',7:'V2_F02_光伏与渗透',8:'V2_F03_区域净负荷',9:'V2_F04_46站方向压力',16:'V2_F08_邳州容量与费用',17:'V2_F09_市区容量与费用',19:'V2_F11_2035设备组合',23:'V2_F12_完整转供响应'}[n]
        fig(root,f'figure-{n}',name+'.png',y=267,h=269);paragraphs(root,f'analysis-{n}',pp)
    elif n==10:
        pic=old_picture(root)[1];wipe(root,keep=[pic.get('id')])
        for j,(title,body)in enumerate([('① 十三项候选','覆盖源荷、网络、峰段与工程价格，先明确各指标的定义和取值。'),('② 九项关联指标','组内相关绝对值达到0.40，保留能够反映容载比变化的信息。'),('③ 五项基础参数','按0.70高相关阈值归并，优先采用具有明确规划含义的基础输入。')]):block(root,f'screen-{j}',650,275+j*105,275,102,title,body,17.5)
        paragraphs(root,'screen-note',pp,y=602,h=57,size=17.5,leading=22)
    elif n==11:
        for g in list(root.findall(Q('g'))):
            if isbody(g)and frame(g)[1]>=610:root.remove(g)
        paragraphs(root,'parameter-meaning',pp,y=599,h=60,size=18,leading=23)
    elif n==12:
        pic=old_picture(root)[1];wipe(root,keep=[pic.get('id')])
        for j,(title,body)in enumerate(bl):block(root,f'cost-{j}',590,273+j*105,335,103,title,body,17.5)
        paragraphs(root,'cost-mechanism',pp,y=600,h=59,size=18,leading=23)
    elif n==13:
        for g in list(root.findall(Q('g'))):
            if isbody(g)and frame(g)[1]>=610:root.remove(g)
        paragraphs(root,'storage-procurement',pp,y=586,h=73,size=18.5,leading=24)
    elif n==14:
        href,_=old_picture(root);wipe(root);picture(root,'equipment',href,x=35,y=290,w=480,h=220)
        for x,label in [(115,'主变'),(275,'联络'),(435,'储能')]:text(group(root,'resource-'+label,x-55,520,110,32),x,543,label,21,G,True,anchor='middle')
        for j,(title,body)in enumerate(bl):block(root,f'resource-{j}',550,274+j*107,375,105,title,body,18)
        paragraphs(root,'security-constraints',['共同约束：正常运行负载率≤80%，最大单台主变N-1时剩余设备短时负载率≤130%；储能和转供按同年设备状态参与支撑。'],y=610,h=49,size=18,leading=23,background=True)
    elif n==18:
        keep=[g.get('id')for g in find_table(root)];wipe(root,keep);fig(root,'cost-delta','V2_F10_措施费用差.png',y=266,h=237);paragraphs(root,'cost-explanation',pp,y=509,h=53,size=18,leading=23)
    elif n==20:
        keep=[g.get('id')for g in find_table(root)];wipe(root,keep)
        for j,(title,body)in enumerate(bl):block(root,f'station-{j}',35+j*457,519,433,137,title,body,18.5)
    elif n==21:
        wipe(root);g=group(root,'transfer-network',35,274,890,224);text(g,480,295,'正常方式与主变N-1分别安排年度固定转供方案',21,G,True,anchor='middle')
        for x,title,desc in [(55,'源端站','可切换源荷区段'),(360,'共享馈线与联络','既有MW额度及通道热限'),(680,'受端站','馈线余量与主变容量')]:
            node=group(g,'transfer-node-'+str(x),x,318,220,87);rect(node,x,318,220,87,TINT,G);text(node,x+110,350,title,22,G,True,anchor='middle');text(node,x+110,383,desc,18,anchor='middle')
        arrow(g,280,360,350,360);arrow(g,585,360,670,360);line(g,473,405,473,435)
        rect(g,305,435,335,48,'#FFFFFF',G);text(g,472,465,'多条联络共用馈线与区段预算',20,G,True,anchor='middle')
        paragraphs(root,'transfer-analysis',pp,y=517,h=140,size=19,leading=25)
    elif n==22:
        paragraphs(root,'lookup-purpose',pp,y=383,h=34,size=17.5,leading=22)
    spec['title']=OLD[n-1]['title'];spec['svg']=f'slide_{n:02d}.svg';spec['source_slide']=n
    E.ElementTree(root).write(str(A/f'slide_{n:02d}.svg'),encoding='utf-8',xml_declaration=False)

for n in range(1,37):
    entry={'page':n,'title':OLD[n-1]['title'],'source_slide':n,'svg':f'slide_{n:02d}.svg','mode':'edited'if n in SPECS else'referenced','source':SPECS[n]['source']if n in SPECS else OLD[n-1]['source'],'report_sha256':MAN['sha256']}
    if n in SPECS:entry['visible_additions']={k:v for k,v in SPECS[n].items()if k in ['paragraphs','blocks']}
    MAP.append(entry)
(W/'content_map.json').write_text(json.dumps({'user_authorization':'20261021参照统计分析PPT，适当增加可见文字并保留旧稿','main_pages':25,'appendix_pages':11,'report_sha256':MAN['sha256'],'pages':MAP},ensure_ascii=False,indent=2))
(W/'exports/逐页讲稿_文字增强版.md').write_text('\n\n'.join('## '+str(r['page'])+' '+r['title']+'\n\n'+(W/'notes'/Path(r['svg']).with_suffix('.md').name).read_text()for r in MAP))
print(json.dumps({'edited':len(SPECS),'referenced':36-len(SPECS),'pages':36},ensure_ascii=False))
