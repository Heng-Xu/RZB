"""Local native-deck revision requested on 2026-10-22; preserve its source."""
from pathlib import Path
from lxml import etree as E
from decimal import Decimal
import json,re,unicodedata

B=Path(__file__).resolve().parents[1];W=B/'成果汇报_甲方修正版_20261022'
A=W/'authoring-svg-flat';S=W/'sources/authoring-baseline'
NS='http://www.w3.org/2000/svg';Q=lambda x:'{'+NS+'}'+x
GREEN='#007C78';TEXT='#20393E';BAND='#EFF5F4';BORDER='#D0DEDB';FONT='Microsoft YaHei'
T=json.loads((W/'data/report_tables.json').read_text())
COST={(r[0],r[1]):r[2] for r in T['表5-9']['rows'][1:]}
ASSETS={(r[0],r[1]):r for r in T['表5-10']['rows'][1:]}
FEE=lambda area,mode:COST[area,mode]
f2=lambda n:f'{Decimal(n):.2f}'
SAVING={a:f2(Decimal(FEE(a,'刚性'))-Decimal(FEE(a,'弹性'))) for a in ['邳州','市区']}
TABLES={
17:{'name':'city-path-comparison','x':35,'y':540,'width':890,'height':120,'font_size':18,
    'widths':[235,130,130,395],'heights':[24]*5,
    'header':['比较项目','刚性方案','弹性方案','工程含义'],
    'rows':[
        ['2030累计费用 / 万元','14819.77','16806.54','弹性前期站内补强投入较多'],
        ['2035储能 / MWh',ASSETS['市区','刚性'][5],ASSETS['市区','弹性'][5],'期末储能配置高于刚性'],
        ['2035新增联络累计 / 条',ASSETS['市区','刚性'][6],ASSETS['市区','弹性'][6],'联络建设减少'],
        ['全期费用现值 / 万元',FEE('市区','刚性'),FEE('市区','弹性'),'联络费用下降，合计减少'+SAVING['市区']+'万元']],
    'numeric_columns':[1,2],
    'source':'表5-9、5-10；2030累计费用保持来源PPT既有核验值，不由逐年显示取整值重新累加。'},
18:{'name':'regional-cost-comparison','x':35,'y':514,'width':890,'height':142,'font_size':19,
    'widths':[95,145,145,135,370],'heights':[30,38,38,36],
    'header':['地区','刚性 / 万元','弹性 / 万元','减少 / 万元','主要费用变化'],
    'rows':[
        ['邳州',FEE('邳州','刚性'),FEE('邳州','弹性'),SAVING['邳州'],'储能及联络支出下降，抵消较多主变投入'],
        ['市区',FEE('市区','刚性'),FEE('市区','弹性'),SAVING['市区'],'主要由联络费用下降形成优势'],
        ['合计',f2(sum(Decimal(FEE(a,'刚性')) for a in ['邳州','市区'])),f2(sum(Decimal(FEE(a,'弹性')) for a in ['邳州','市区'])),f2(sum(Decimal(v) for v in SAVING.values())),'总费用降幅2.96%']],
    'numeric_columns':[1,2,3],
    'source':'表5-9、5-11；总降幅为既有报告和来源PPT结论。'},
20:{'name':'station-mechanism-comparison','x':35,'y':519,'width':890,'height':138,'font_size':18.5,
    'widths':[105,335,450],'heights':[28,55,55],
    'header':['比较维度','代表站与结果','工程含义'],
    'rows':[
        ['设备结构','兴塘变：N-1剩余容量\n71.50→81.50 MVA','扩建第三台与更换已有主变，\n对故障后剩余能力的改善不同。'],
        ['局部支撑','八义集变：主变容量相同，\n储能功率3.10→0.30 MW','年度转接任务与配储需求存在差异，\n需结合源荷、受端及设备状态判断。']],
    'numeric_columns':[],
    'source':'保留原代表站表；底部原有结构作用、局部任务分析改为对照表，数值保持来源PPT。'}
}

def el(tag,parent=None,**attrs):
    z=E.Element(Q(tag),{k.replace('_','-'):str(v) for k,v in attrs.items()})
    if parent is not None:parent.append(z)
    return z
def width(s,fs):return sum(1 if unicodedata.east_asian_width(c)in'FW' else .55 for c in s)*fs*1.04
def wrap(s,w,fs):
    ll=[]
    for part in str(s).split('\n'):
        buf=''
        for token in re.findall(r'[A-Za-z0-9]+(?:[.%/][A-Za-z0-9]+)*|.',part):
            if buf and width(buf+token,fs)>w:ll.append(buf);buf=token
            else:buf+=token
        ll.append(buf)
    return ll
def draw_table(root,spec):
    name=spec['name'];x=spec['x'];y=spec['y'];w=spec['width'];h=spec['height'];fs=spec['font_size']
    group=el('g',root,id=name,font_family=FONT);group.set('data-pptx-bounds',f'{x} {y} {w} {h}');group.set('data-pptx-replace-with','table')
    payload={'schema':'ppt-master.semantic-table.v2','name':name,'x':x,'y':y,'width':w,'height':h,'strict_grid':True,'header_rows':1,'column_widths':spec['widths'],'row_heights':spec['heights'],
        'style':{'font_family':FONT,'font_size':fs,'header_font_size':fs,'header_fill':GREEN,'header_text':'#FFFFFF','body_fill':'#FFFFFF','body_text':TEXT,'band_fill':BAND,'band_row':True,'border_color':BORDER,'border_width':.6,'valign':'middle'},
        'defaults':{'cell':{'align':'ctr','valign':'middle','padding':{'left':6,'right':6,'top':1,'bottom':1}}},'columns':[],'rows':[]}
    metadata=el('metadata',group,type='application/json')
    allrows=[spec['header']]+spec['rows'];yy=y
    for ri,(row,rh) in enumerate(zip(allrows,spec['heights'])):
        xx=x;cells=[]
        for ci,(s,cw) in enumerate(zip(row,spec['widths'])):
            ishead=ri==0;summary=ri==len(allrows)-1 and spec['name']=='regional-cost-comparison'
            fill=GREEN if ishead else BAND if ri%2==0 or summary else '#FFFFFF'
            color='#FFFFFF' if ishead else GREEN if summary or ci==0 else TEXT
            bold=ishead or summary;align='r' if not ishead and ci in spec['numeric_columns'] else 'ctr'
            lines=wrap(s,cw-12,fs);assert len(lines)*fs*1.15<=rh+1,(name,ri,ci,s,lines,rh)
            rendered=''.join(lines)
            cell={'text':rendered,'align':align,'valign':'middle','fill':fill,'color':color,'bold':bold,'font_size':fs}
            cells.append(cell)
            el('rect',group,x=xx,y=yy,width=cw,height=rh,fill=fill,stroke=BORDER,stroke_width=.6)
            tx=xx+cw-6 if align=='r' else xx+cw/2;anchor='end'if align=='r'else'middle'
            leading=fs*1.15;baseline=yy+(rh-len(lines)*leading)/2+fs*.88
            t=el('text',group,x=tx,y=f'{baseline:.3f}',font_size=fs,fill=color,font_weight='bold'if bold else'normal',text_anchor=anchor)
            t.text=lines[0]
            for ln in lines[1:]:el('tspan',t,x=tx,dy=f'{leading:.3f}').text=ln
            xx+=cw
        if ri==0:payload['columns']=cells
        else:payload['rows'].append(cells)
        yy+=rh
    metadata.text=json.dumps(payload,ensure_ascii=False,separators=(',',':'))

for i in range(2,35):
    root=E.parse(str(S/f'slide_{i:02d}.svg')).getroot()
    footer=root.find(".//"+Q('g')+"[@id='shape-2']")
    assert footer is not None,(i,'missing footer')
    if i==2:root.remove(footer)
    else:
        ts=footer.findall('.//'+Q('text'));assert len(ts)==1
        for sub in list(ts[0]):ts[0].remove(sub)
        ts[0].text=str(i-2)
    if i in TABLES:
        remove={17:['shape-22'],18:['shape-22','shape-23'],20:['shape-22','shape-27']}[i]
        for id in remove:
            g=root.find(Q('g')+f"[@id='{id}']");assert g is not None,(i,id)
            root.remove(g)
        draw_table(root,TABLES[i])
    E.ElementTree(root).write(str(A/f'slide_{i:02d}.svg'),encoding='utf-8',xml_declaration=False)
(W/'table_changes.json').write_text(json.dumps(TABLES,ensure_ascii=False,indent=2))
print('Modified three bottom sections and renumbered pages from background = 1')
