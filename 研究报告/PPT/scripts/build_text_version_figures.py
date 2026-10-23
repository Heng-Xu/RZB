"""Reflow existing report figures for explanation-rich 4:3 slides."""
from pathlib import Path
import json,sys,csv,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

B=Path(__file__).resolve().parents[1];W=B/'成果汇报_文字增强版_20261021'
K=Path('/home/xh/.codex/skills/scientific-visualization');sys.path.insert(0,str(K/'scripts'))
from figure_export import export_figure
T=json.loads((W/'data/report_tables.json').read_text());M=json.loads((W/'source_manifest.json').read_text())
G='#007C78';BLUE='#376382';O='#C57434';GRAY='#68777D'
plt.style.use(K/'assets/presentation.mplstyle')
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Microsoft YaHei','Noto Sans CJK SC','DejaVu Sans'],'axes.unicode_minus':False,'font.size':12,'axes.labelsize':12,'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':10,'axes.linewidth':.8,'lines.linewidth':2,'lines.markersize':4,'svg.fonttype':'none','pdf.fonttype':42})
R=[]
def rows(k):return T[k]['rows']
def num(s):return float(str(s).replace('%','').replace(',','').replace('－','-'))
def panels(n=2,rows_=1,size=(9.1,2.75)):
    f,a=plt.subplots(rows_,n,figsize=size,layout='constrained');return f,np.asarray(a).reshape(-1)
def clean(ax,grid=True):
    ax.spines[['top','right']].set_visible(False);ax.set_axisbelow(True)
    if grid:ax.grid(axis='y',alpha=.16,lw=.6)
def save(f,name,sources,details):
    provenance={'report_sha256':M['sha256'],'sources':sources,'transformations':details,'purpose':'4:3汇报：保留图内字号，为可见分析文字安排空间','uncertainty':'确定性统计或模型结果，未添加误差范围'}
    export_figure(f,W/'figures'/name,formats=['png','svg','pdf'],dpi=300,overwrite=True,bbox_inches=None,write_manifest=True,provenance=provenance)
    R.append({'name':name,'sources':sources,'transformations':details});plt.close(f)

f,aa=panels(3)
for reg,c,sty in [('邳州',G,'-o'),('市区',BLUE,'--s')]:
    rr=[r for r in rows('表3-1')[1:]if r[0]==reg];x=[int(r[1])for r in rr]
    for ax,col,lab in zip(aa,[2,3,4],['主变总容量 / MVA','年网供最大负荷 / MW','容载比']):
        ax.plot(x,[num(r[col])for r in rr],sty,color=c,label=reg);ax.set_ylabel(lab);ax.set_xticks([2021,2023,2025]);clean(ax)
aa[0].legend();save(f,'V2_F01_历史容量负荷',['表3-1'],['完整保留2021—2025各年度与三项指标；画布改为9.1×2.75英寸'])

f,aa=panels(3)
for reg,col,c,sty in [('邳州',4,G,'-o'),('市区',3,BLUE,'--s')]:
    rr=rows('表3-6')[1:];aa[0].plot([int(r[0])for r in rr],[num(r[col])for r in rr],sty,color=c,label=reg)
aa[0].set(ylabel='光伏装机 / MW',xticks=[2025,2030,2035]);aa[0].legend();clean(aa[0])
for ax,col,lab in zip(aa[1:],[1,2],['2025装机渗透率','2025电量渗透率 / %']):
    rr=rows('表3-12')[1:];yy=[num(r[col])for r in rr];bb=ax.bar([r[0]for r in rr],yy,color=[G,BLUE],width=.55);ax.bar_label(bb,labels=[f'{v:.2f}'for v in yy],padding=4,fontsize=12);ax.set_ylim(0,max(yy)*1.3);ax.set_ylabel(lab);clean(ax)
save(f,'V2_F02_光伏与渗透',['表3-6','表3-12'],['保留原预测装机序列及两项2025年估计指标；未来装机属于预测情景'])

f,aa=panels(1,2)
for ax,tag,reg,c in zip(aa,['pizhou','city'],['邳州','市区'],[G,BLUE]):
    with (W/f'data/{tag}_8760.csv').open(encoding='utf-8-sig')as fi:rr=list(csv.DictReader(fi))
    assert len(rr)==8760;y=np.array([float(r['net_mw'])for r in rr]);threshold=.95*np.max(abs(y))
    ax.plot(np.arange(8760),y,color=c,lw=.65);ax.axhline(threshold,color=O,ls='--',lw=1,label='95%峰值');ax.axhline(0,color=GRAY,lw=.6);ax.set(ylabel=reg+' / MW',xlim=(0,8759),xticks=[0,2160,4344,6552]);ax.set_xticklabels(['1月','4月','7月','10月']);clean(ax,False)
aa[0].legend(loc='upper right');save(f,'V2_F03_区域净负荷',['补齐后的区域8760小时序列','表3-10'],['保留8760小时与补值标识；先同小时汇总后取绝对峰值；受入为正、反送为负'])

f,aa=panels()
for ax,reg,c in zip(aa,['邳州','市区'],[G,BLUE]):
    rr=[r for r in rows('表3-8')[1:]if r[0]==reg];xx=np.arange(len(rr));fw=[num(r[2])for r in rr];rv=[-num(r[3])for r in rr]
    ax.vlines(xx,0,fw,color=c,alpha=.28,lw=3);ax.plot(xx,fw,'o',color=c,label='最大正向');ax.plot(xx,rv,'v',color=O,label='最大反向');ax.axhline(0,color=GRAY,lw=.7);ax.set(ylabel='净负荷极值 / MW',xlabel=reg+'站点序号',xticks=[0,len(rr)//2,len(rr)-1]);ax.set_xticklabels([1,len(rr)//2+1,len(rr)]);clean(ax)
aa[0].legend(ncol=2,loc='upper center');save(f,'V2_F04_46站方向压力',['表3-8'],['保留20座邳州站和26座市区站，原顺序不变'])

for key,fee,name in [('表5-4','表5-5','V2_F08_邳州容量与费用'),('表5-6','表5-7','V2_F09_市区容量与费用')]:
    f,aa=panels()
    for plan,c,ls,mk in [('刚性',BLUE,'--','s'),('弹性',G,'-','o')]:
        rr=[r for r in rows(key)[1:]if r[0]==plan];ff=[r for r in rows(fee)[1:]if r[0]==plan];xx=[int(r[1])for r in rr];cum=np.cumsum([num(r[7])for r in ff])
        assert len(rr)==len(ff)==15
        for ax,yy,lab in zip(aa,[[num(r[3])for r in rr],cum],['主变容量 / MVA','累计费用现值 / 万元']):
            ax.plot(xx,yy,color=c,ls=ls,marker=mk,markersize=3,label=plan);ax.set_ylabel(lab);ax.set_xticks([2021,2025,2030,2035]);clean(ax)
    aa[0].legend(ncol=2);save(f,name,[key,fee],['保留2021—2035完整年度；主图展示容量与累计费用，容载比及储能列在解释、期末设备页和逐年备查；费用按当年新增措施现值逐年累计'])

f,aa=panels(size=(9.1,2.4));xx=np.arange(3)
for ax,reg in zip(aa,['邳州','市区']):
    rr=rows('表5-11')[1:];a=next(r for r in rr if r[0]==reg and r[1]=='刚性');b=next(r for r in rr if r[0]==reg and r[1]=='弹性');yy=np.array([num(b[i])-num(a[i])for i in [2,3,4]])
    bars=ax.bar(xx,yy,color=[O if v>0 else G for v in yy],width=.55);ax.axhline(0,color=GRAY,lw=.8);ax.set(xticks=xx,xticklabels=['主变','储能','联络'],ylabel=reg+' 弹性−刚性 / 万元',ylim=(-16500,13500));clean(ax)
    for bar,v in zip(bars,yy):ax.text(bar.get_x()+bar.get_width()/2,v+(500 if v>=0 else -500),f'{v:+.2f}',ha='center',va='bottom'if v>=0 else'top',fontsize=11)
save(f,'V2_F10_措施费用差',['表5-11'],['与原图同一分项显示值相减；不改变费用符号或比较范围，分项与合计可能有0.01万元取整差'])

f,aa=panels(3);xx=np.arange(2)
for ax,col,lab in zip(aa,[2,5,6],['在役主变 / MVA','储能额定能量 / MWh','累计新增联络 / 条']):
    for plan,c,offset in [('刚性',BLUE,-.18),('弹性',G,.18)]:
        yy=[num(next(r for r in rows('表5-10')[1:]if r[0]==reg and r[1]==plan)[col])for reg in ['邳州','市区']];bars=ax.bar(xx+offset,yy,width=.32,label=plan,color=c);ax.bar_label(bars,labels=[str(int(v))if col==6 else f'{v:.2f}'for v in yy],padding=3,fontsize=9)
    ax.set_xticks(xx,['邳州','市区']);ax.set_ylabel(lab);ax.set_ylim(0,ax.get_ylim()[1]*1.25);clean(ax)
aa[0].legend(ncol=2,fontsize=9,loc='upper left');save(f,'V2_F11_2035设备组合',['表5-10'],['保留三类设备的地区、方案与单位，数值和原图一致'])

f,aa=panels()
for ax,key,lab in zip(aa,['表5-70','表5-71'],['场景1：增长4%，分散系数1.10','场景2：增长5.5%，分散系数1.00']):
    rr=rows(key)[1:];ax.plot([num(r[0])for r in rr],[num(r[2])for r in rr],'-o',color=G);ax.set(xlabel='初始转供率 / %',ylabel='容载比',xticks=[10,30,50,70,90]);ax.set_title(lab,fontsize=12);clean(ax)
save(f,'V2_F12_完整转供响应',['表5-70','表5-71'],['两组设备重新选配场景，每组9节点全部保留；装机渗透率50%、电缆长度占比50%；相邻点连线仅表示节点顺序'])
(W/'figure_manifest_v2.json').write_text(json.dumps({'report_sha256':M['sha256'],'figures':R},ensure_ascii=False,indent=2))
print('Reflowed',len(R),'figures')
