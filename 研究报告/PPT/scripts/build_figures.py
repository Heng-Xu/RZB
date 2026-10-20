"""Read a stable report snapshot and draw presentation figures without changing the report."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as ET
from io import BytesIO
from datetime import datetime, timezone
import csv, hashlib, json, re, sys, shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[1]
WORK=BASE/'成果汇报_20261019'
FIG=WORK/'figures'; DATA=WORK/'data'; SRC=WORK/'sources'
for d in (FIG,DATA,SRC):d.mkdir(exist_ok=True,parents=True)
SKILL=Path('/home/xh/.codex/skills/scientific-visualization')
sys.path.insert(0,str(SKILL/'scripts'))
from figure_export import export_figure
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
GREEN='#007C78';BLUE='#376382';ORANGE='#C57434';GRAY='#68777D';LIGHT='#E7F1EF'
plt.style.use(SKILL/'assets/presentation.mplstyle')
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Microsoft YaHei','Noto Sans CJK SC','DejaVu Sans'],'axes.unicode_minus':False,'font.size':13,'axes.labelsize':13,'axes.titlesize':14,'xtick.labelsize':11,'ytick.labelsize':11,'legend.fontsize':11,'axes.linewidth':.8,'lines.linewidth':2,'lines.markersize':4,'svg.fonttype':'none','pdf.fonttype':42})

def digest(b):return hashlib.sha256(b).hexdigest()
def snapshot():
    report=ROOT/'研究报告/04_word/研究报告终稿.docx'
    raw=report.read_bytes()
    if raw!=report.read_bytes():raise RuntimeError('Report changed during read; retry after save')
    with ZipFile(BytesIO(raw)) as z:
        if z.testzip() is not None:raise RuntimeError('Invalid report ZIP')
        body=ET.fromstring(z.read('word/document.xml')).find('w:body',NS)
        rels={n.get('Id'):n.get('Target') for n in ET.fromstring(z.read('word/_rels/document.xml.rels'))}
        tables={};paras=[];figs=[];last=''
        for i,el in enumerate(body):
            if el.tag.endswith('}p'):
                txt=''.join(el.xpath('.//w:t/text()',namespaces=NS))
                if txt.strip():paras.append({'body_index':i,'text':txt});last=txt
                for rid in el.xpath('.//a:blip/@r:embed',namespaces=NS):
                    caption=''
                    for ne in list(body)[i+1:i+4]:
                        tx=''.join(ne.xpath('.//w:t/text()',namespaces=NS))
                        if tx.startswith('图'):caption=tx;break
                    if caption:
                        target=rels[rid];name=caption.split(' ')[0]+Path(target).suffix
                        dest=FIG/name;blob=z.read('word/'+target);dest.write_bytes(blob)
                        figs.append({'caption':caption,'file':name,'sha256':digest(blob)})
            elif el.tag.endswith('}tbl') and re.match(r'^表\d+-\d+ ',last):
                rows=[[''.join(c.xpath('.//w:t/text()',namespaces=NS)) for c in r.findall('w:tc',NS)] for r in el.findall('w:tr',NS)]
                key=last.split(' ')[0];tables[key]={'title':last,'body_index':i,'rows':rows}
                with (DATA/(key+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f).writerows(rows)
        sha=digest(raw);snap=SRC/f'研究报告来源_{sha[:12]}.docx'
        if not snap.exists():snap.write_bytes(raw)
    (DATA/'report_tables.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2))
    (DATA/'report_paragraphs.json').write_text(json.dumps(paras,ensure_ascii=False,indent=2))
    (DATA/'report_figures.json').write_text(json.dumps(figs,ensure_ascii=False,indent=2))
    meta={'source_path':str(report.relative_to(ROOT)),'sha256':sha,'snapshot':str(snap.relative_to(WORK)),'captured_utc':datetime.now(timezone.utc).isoformat(),'status':'report_finalized_by_user_20261020_ppt_review_draft','numbered_tables':len(tables),'figures':len(figs)}
    (WORK/'source_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    return tables,meta

T,M=snapshot()
def table_key(title):
    found=[k for k,v in T.items() if title in v['title']]
    if len(found)!=1:raise ValueError(f'Ambiguous source table: {title}: {found}')
    return found[0]
def rows(key):return T[key]['rows']
def num(v):return float(str(v).replace('%','').replace('－','-').replace(',',''))
def arr(key,col,condition=None):return np.array([num(r[col]) for r in rows(key)[1:] if condition is None or condition(r)])
REG=[]
def save(fig,name,sources,transformations):
    provenance={'report_sha256':M['sha256'],'source_tables':sources,'transformations':transformations,'medium':'4:3 projected presentation','uncertainty':'deterministic report outputs; no invented uncertainty','missing_data':'as documented in the report'}
    export_figure(fig,FIG/name,formats=['png','svg','pdf'],dpi=300,overwrite=True,bbox_inches=None,write_manifest=True,provenance=provenance)
    REG.append({'name':name,'sources':sources,'transformations':transformations});plt.close(fig)
def clean(ax,grid=True):
    ax.spines[['top','right']].set_visible(False)
    if grid:ax.grid(axis='y',alpha=.16,lw=.6)
    ax.set_axisbelow(True)
def panels(nrows=1,ncols=2,size=(9.1,3.45)):
    f,a=plt.subplots(nrows,ncols,figsize=size,layout='constrained');return f,np.asarray(a).reshape(-1)

# Historical data: capacity and load remain on separate axes with their own units.
f,axs=panels(1,3,(9.1,3.45))
for reg,color,style in [('邳州',GREEN,'-o'),('市区',BLUE,'--s')]:
    rr=[r for r in rows('表3-1')[1:] if r[0]==reg];x=[int(r[1]) for r in rr]
    for ax,c,lab in zip(axs,[2,3,4],['主变总容量 / MVA','年网供最大负荷 / MW','容载比']):
        ax.plot(x,[num(r[c]) for r in rr],style,label=reg,color=color);ax.set_ylabel(lab);ax.set_xticks([2021,2023,2025]);clean(ax)
axs[0].legend(loc='upper left');save(f,'F01_历史容量负荷',['表3-1'],['按地区保留2021—2025完整年度序列；容量、负荷和容载比分面显示'])

f,axs=panels(1,3,(9.1,3.3))
for reg,col,color,style in [('邳州',4,GREEN,'-o'),('市区',3,BLUE,'--s')]:
    x=arr('表3-6',0);y=arr('表3-6',col)
    axs[0].plot(x,y,style,label=reg,color=color)
axs[0].set_ylabel('光伏装机 / MW');axs[0].set_xticks([2025,2030,2035]);axs[0].legend();clean(axs[0])
for ax,col,title in [(axs[1],1,'2025装机渗透率'),(axs[2],2,'2025电量渗透率 / %')]:
    rr=rows('表3-12')[1:];y=[num(r[col]) for r in rr];b=ax.bar([r[0] for r in rr],y,color=[GREEN,BLUE],width=.55)
    ax.bar_label(b,labels=[f'{v:.2f}' for v in y],padding=4,fontsize=13);ax.set_ylim(0,max(y)*1.3);ax.set_ylabel(title);clean(ax)
save(f,'F02_光伏及渗透水平',['表3-6','表3-12'],['未来装机为报告预测情景；两项渗透率为报告2025年估计值'])

# Regional curves use the exact retained 8760-hour series, including imputation flags.
f,axs=panels(2,1,(9.1,3.6))
for ax,tag,reg,color in zip(axs,['pizhou','city'],['邳州','市区'],[GREEN,BLUE]):
    path=ROOT/f'研究报告/数据来源/当前版/区域时序/{tag}_8760.csv'
    with path.open(encoding='utf-8-sig') as fi:rr=list(csv.DictReader(fi))
    if len(rr)!=8760:raise ValueError('Expected 8760 hours')
    y=np.array([float(r['net_mw']) for r in rr]);thr=.95*np.max(abs(y))
    ax.plot(np.arange(8760),y,color=color,lw=.65,rasterized=False)
    ax.axhline(thr,color=ORANGE,lw=1,ls='--',label='95%峰值');ax.axhline(0,color=GRAY,lw=.7)
    ax.set_ylabel(reg+' / MW');ax.set_xlim(0,8759);ax.set_xticks([0,2160,4344,6552]);ax.set_xticklabels(['1月','4月','7月','10月']);clean(ax,False)
    (DATA/(tag+'_8760.csv')).write_bytes(path.read_bytes())
axs[0].legend(loc='upper right',ncol=1);save(f,'F03_区域净负荷',['表3-10'],['读取报告保留的补齐8760小时区域净负荷；95%线按区域曲线绝对峰值计算；受入为正，反送为负'])

f,axs=panels(1,2,(9.1,3.6))
rr=rows('表3-8')[1:]
for ax,reg,color in zip(axs,['邳州','市区'],[GREEN,BLUE]):
    rg=[r for r in rr if r[0]==reg];x=np.arange(len(rg));fw=np.array([num(r[2]) for r in rg]);rv=np.array([num(r[3]) for r in rg])
    ax.vlines(x,0,fw,color=color,alpha=.28,lw=3);ax.plot(x,fw,'o',color=color,label='最大正向');ax.plot(x,-rv,'v',color=ORANGE,label='最大反向')
    ax.axhline(0,color=GRAY,lw=.7);ax.set_xlabel(reg+'站点序号');ax.set_ylabel('净负荷极值 / MW');ax.set_xticks([0,len(rg)//2,len(rg)-1]);ax.set_xticklabels([1,len(rg)//2+1,len(rg)]);clean(ax)
axs[0].legend(ncol=2,loc='upper center');save(f,'F04_46站方向压力',['表3-8'],['覆盖20座邳州站与26座市区站；反向幅值绘于零线下方；站点顺序沿报告表格'])

f,ax=plt.subplots(figsize=(6.1,3.7),layout='constrained')
rr=rows('表3-15')[1:];labels=[r[0].replace('分布式电源','').replace('单位功率投资比','投资比') for r in rr];val=[num(r[3]) for r in rr]
bars=ax.barh(np.arange(len(rr)),val,color=[GREEN if abs(x)>=.4 else '#AEB9BB' for x in val],height=.64)
ax.set_yticks(np.arange(len(rr)),labels,fontsize=11);ax.invert_yaxis();ax.axvline(.4,color=ORANGE,ls='--',lw=1);ax.axvline(-.4,color=ORANGE,ls='--',lw=1);ax.axvline(0,color=GRAY,lw=.7);ax.set_xlim(-1.04,1.04);ax.set_xlabel('组内 Pearson 相关系数')
for b,v in zip(bars,val):ax.text(v+(.025 if v>=0 else -.025),b.get_y()+b.get_height()/2,f'{v:.2f}',ha='left' if v>=0 else 'right',va='center',fontsize=10)
clean(ax,False);save(f,'F05_十三项组内相关',['表3-15'],['保留13项有符号系数；正负0.40为本研究筛选线；不作因果或现实独立性结论'])

f,ax=plt.subplots(figsize=(5.4,3.7),layout='constrained');rr=rows('表3-19');values=np.array([[num(v) for v in r[1:]] for r in rr[1:]])
names=['装机渗透率','年最大净负荷\n平均增长率','电缆长度占比','初始转供率','负荷分散系数']
im=ax.imshow(values,vmin=-1,vmax=1,cmap='BrBG');ax.set_xticks(range(5),['装机\n渗透率','年最大\n净负荷\n平均增长率','电缆长度\n占比','初始\n转供率','负荷\n分散系数'],fontsize=9,ha='center');ax.set_yticks(range(5),names,fontsize=10)
for i in range(5):
    for j in range(5):ax.text(j,i,f'{values[i,j]:.2f}',ha='center',va='center',color='white' if abs(values[i,j])>.6 else '#1E3338',fontsize=12)
f.colorbar(im,ax=ax,fraction=.045,pad=.03,label='Pearson');save(f,'F06_五参数相关',['表3-19'],['固定色阶−1至1；中文参数标签；每个单元保留报告值'])

f,axs=panels(1,1,(5.4,3.3));rr=rows('表4-3')[1:];x=np.array([num(r[0]) for r in rr]);y=[num(r[4]) for r in rr]
axs[0].plot(x,y,'-o',color=GREEN);axs[0].set(xlabel='电缆长度占比 / %',ylabel='3 km联络投资 / 万元');clean(axs[0]);
for a,b in zip(x,y):axs[0].annotate(f'{b:.2f}',(a,b),xytext=(0,7),textcoords='offset points',ha='center',fontsize=10)
save(f,'F07_费用与有效功率',['表4-3'],['联络投资读取报告表格；固定3 km与6万元接入费用'])

def annual(key,fee_key,name):
    f,axs=panels(2,2,(9.1,3.9))
    for plan,c,ls,mk in [('刚性',BLUE,'--','s'),('弹性',GREEN,'-','o')]:
        rr=[r for r in rows(key)[1:] if r[0]==plan];x=[int(r[1]) for r in rr]
        fee=[r for r in rows(fee_key)[1:] if r[0]==plan];cum=np.cumsum([num(r[7]) for r in fee])
        for ax,y,lab in zip(axs,[[num(r[3]) for r in rr],[num(r[4]) for r in rr],[num(r[5]) for r in rr],cum],['主变容量 / MVA','容载比','储能额定功率 / MW','累计费用现值 / 万元']):
            ax.plot(x,y,color=c,ls=ls,marker=mk,markersize=3,label=plan);ax.set_ylabel(lab,fontsize=11);ax.set_xticks([2021,2025,2030,2035]);ax.tick_params(labelsize=10);clean(ax)
    axs[0].legend(ncol=2,fontsize=10);save(f,name,[key,fee_key],['2021—2035完整年度序列；费用按逐年当年措施现值求累计；历史为模型回算，未来为预测情景'])
annual('表5-4','表5-5','F08_邳州逐年方案');annual('表5-6','表5-7','F09_市区逐年方案')

f,axs=panels(1,2,(9.1,3.25));rr=rows('表5-11')[1:];cats=['主变','储能','联络'];x=np.arange(3)
for ax,reg in zip(axs,['邳州','市区']):
    a=next(r for r in rr if r[0]==reg and r[1]=='刚性');b=next(r for r in rr if r[0]==reg and r[1]=='弹性');delta=np.array([num(b[i])-num(a[i]) for i in (2,3,4)])
    bars=ax.bar(x,delta,color=[ORANGE if v>0 else GREEN for v in delta],width=.55);ax.axhline(0,color=GRAY,lw=.8);ax.set_xticks(x,cats);ax.set_ylabel(reg+' 弹性−刚性 / 万元');clean(ax)
    for bar,v in zip(bars,delta):ax.text(bar.get_x()+bar.get_width()/2,v+(500 if v>=0 else -500),f'{v:+.2f}',ha='center',va='bottom' if v>=0 else 'top',fontsize=11)
    ax.set_ylim(min(-13500,min(delta)*1.25),max(11000,max(delta)*1.25))
save(f,'F10_措施费用差',['表5-11'],['各地区按同一分项费用计算弹性减刚性；分项报告显示值因取整可与合计相差0.01万元'])

f,axs=panels(1,3,(9.1,3.25));rr=rows('表5-10')[1:];xx=np.arange(2)
for ax,col,lab in zip(axs,[2,5,6],['在役主变 / MVA','储能额定能量 / MWh','累计新增联络 / 条']):
    for plan,c,off in [('刚性',BLUE,-.18),('弹性',GREEN,.18)]:
        yy=[num(next(r for r in rr if r[0]==reg and r[1]==plan)[col]) for reg in ['邳州','市区']];bars=ax.bar(xx+off,yy,width=.32,label=plan,color=c)
        ax.bar_label(bars,labels=[str(int(v)) if col==6 else f'{v:.2f}' for v in yy],padding=3,fontsize=9)
    ax.set_xticks(xx,['邳州','市区']);ax.set_ylabel(lab);ax.set_ylim(0,ax.get_ylim()[1]*1.22);clean(ax)
axs[0].legend(ncol=2,fontsize=10,loc='upper left');save(f,'F11_2035设备组合',['表5-10'],['分面保持不同单位；刚性/弹性固定颜色和空间位置；储能为额定能量'])

transfer_keys=[table_key('场景1的完整转供率节点及设备方案'),table_key('场景2的完整转供率节点及设备方案')]
f,axs=panels(1,2,(9.1,3.25))
for ax,key,lab in zip(axs,transfer_keys,['场景1：增长4%，分散系数1.10','场景2：增长5.5%，分散系数1.00']):
    x=arr(key,0);y=arr(key,2);ax.plot(x,y,'-o',color=GREEN);ax.set_xticks([10,30,50,70,90]);ax.set(xlabel='初始转供率 / %',ylabel='容载比');clean(ax);ax.set_title(lab,fontsize=12)
save(f,'F12_完整转供响应',transfer_keys,['两场景装机渗透率均为50%；设备重新选配条件；保留每组9个节点、真实平台和局部回升；相邻点连线仅表示节点顺序'])

# A compact four-panel evidence summary retains the report's grouped equal-output slices.
f,axs=panels(2,2,(9.1,3.8))
response_keys=[table_key(s) for s in ['装机渗透率对应的设备配置变化','年最大净负荷平均增长率对应的容量及工程变化','电缆长度占比对应的造价与设备切换','负荷分散系数对应的容量平台及配套措施']]
diversity_source=ROOT/'研究报告/数据来源/当前版/负荷分散系数扩展_20261019/diversity_device_response.csv'
with diversity_source.open(encoding='utf-8-sig')as fi:diversity=list(csv.DictReader(fi))
assert len(diversity)==11
assert np.allclose([float(r['负荷分散系数']) for r in diversity],np.arange(1.05,1.251,.02))
assert all(float(r['分布式电源装机渗透率'])==2 and float(r['年最大净负荷平均增长率'])==.04 and float(r['电缆长度占比'])==.1 and float(r['初始转供率'])==.4 for r in diversity)
(DATA/'diversity_device_response.csv').write_bytes(diversity_source.read_bytes())
for ax,key,title in zip(axs,response_keys,['装机渗透率','年最大净负荷平均增长率 / %','电缆长度占比 / %','负荷分散系数']):
    x=[];y=[]
    for r in rows(key)[1:]:
        nums=re.findall(r'\d+(?:\.\d+)?',r[0]);points=[float(v) for v in nums]
        for v in points:x.append(v);y.append(num(r[2]))
    if key==response_keys[-1]:
        x=[float(r['负荷分散系数']) for r in diversity];y=[float(r['容载比']) for r in diversity]
        ax.set_xticks([1.05,1.11,1.15,1.21,1.25])
    ax.plot(x,y,'-o',color=GREEN,markersize=3);ax.set_xlabel(title,fontsize=10);ax.set_ylabel('容载比',fontsize=10);ax.tick_params(labelsize=9);clean(ax)
save(f,'F13_四参数设备响应',response_keys+[str(diversity_source.relative_to(ROOT))],['读取报告已归并的相同设备区段，区间用其端点表示；负荷分散系数直接读取完整11节点数据，条件为装机2.00、增长4%、电缆10%、转供40%；连线仅表示节点顺序'])

f,axs=panels(2,2,(9.1,3.9));x=[float(r['负荷分散系数'])for r in diversity]
for ax,col,lab,color in zip(axs,['容载比','主变容量_MVA','储能额定功率_MW','新增联络合计_条'],['容载比','主变容量 / MVA','储能额定功率 / MW','新增联络 / 条'],[GREEN,GREEN,BLUE,ORANGE]):
    y=[float(r[col])for r in diversity];ax.plot(x,y,'-o',color=color,markersize=4);ax.set_ylabel(lab,fontsize=11);ax.set_xticks([1.05,1.11,1.15,1.21,1.25]);ax.tick_params(labelsize=10);ax.axvline(1.15,color=GRAY,ls=':',lw=1);clean(ax)
    if col in ['储能额定功率_MW','新增联络合计_条']:ax.set_ylim(bottom=0)
    if col=='新增联络合计_条':ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    if col=='容载比':
        for j in [0,3,8,10]:ax.annotate(f'{y[j]:.2f}',(x[j],y[j]),xytext=(0,7),textcoords='offset points',ha='center',fontsize=10)
for ax in axs[2:]:ax.set_xlabel('负荷分散系数',fontsize=11)
save(f,'F14_分散系数完整设备响应',[response_keys[-1],str(diversity_source.relative_to(ROOT))],['完整保留11节点；四面板分别显示主变容载比及配套储能、联络；1.15虚线为矩阵分档界；装机2.00、增长4%、电缆10%、转供40%'])
(WORK/'figure_manifest.json').write_text(json.dumps({'report_sha256':M['sha256'],'figures':REG},ensure_ascii=False,indent=2))
print(json.dumps({'source_hash':M['sha256'],'figures':len(REG),'tables':len(T),'output':str(FIG)},ensure_ascii=False))
