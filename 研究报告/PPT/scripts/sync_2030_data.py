"""原生PPT的2030数据同步：只改计划中的文字、表格单元及原图数据。"""
from pathlib import Path
from copy import deepcopy
from lxml import etree as E
import hashlib,json,re,sys,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[1]
WORK=BASE/'成果汇报_2030同步_20261026';AUTH=WORK/'authoring-svg-flat'
sys.path.insert(0,str(ROOT/'tools'))
from case_horizon import through_year
from report_summary import f

NS={'s':'http://www.w3.org/2000/svg'};sq=lambda n:'{'+NS['s']+'}'+n
plans={(r,c):through_year(json.loads((ROOT/f'研究报告/试算/20261017_逐年需求驱动2035/{r}/{c}/summary.json').read_text()),2030)
       for r in ['pizhou','city']for c in ['rigid','elastic_capacity']}
G='#007C78';BLUE='#376382';O='#C57434';GRAY='#68777D'
fontManager.addfont('/home/xh/.local/share/fonts/stage1/msyh.ttf')
SKILL=Path('/home/xh/.codex/skills/scientific-visualization')
plt.style.use(SKILL/'assets/presentation.mplstyle')
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Microsoft YaHei','Noto Sans CJK SC','DejaVu Sans'],
    'axes.unicode_minus':False,'font.size':12,'axes.labelsize':12,'xtick.labelsize':10,'ytick.labelsize':10,
    'legend.fontsize':10,'axes.linewidth':.8,'lines.linewidth':2,'lines.markersize':4,'svg.fonttype':'none','pdf.fonttype':42})


def panels(n=2,size=(9.1,2.75)):
    fig,axes=plt.subplots(1,n,figsize=size,layout='constrained');return fig,np.asarray(axes).reshape(-1)


def clean(ax):
    ax.spines[['top','right']].set_visible(False);ax.set_axisbelow(True);ax.grid(axis='y',alpha=.16,lw=.6)


def save(fig,key):
    folder=WORK/'images/data2030';folder.mkdir(exist_ok=True)
    for ext in ['png','svg','pdf']:fig.savefig(folder/(key+'.'+ext),dpi=300)
    plt.close(fig);return '../images/data2030/'+key+'.png'


def pictures():
    result={}
    # 以下图形参数沿用build_text_version_figures.py，唯一变化是数据范围和对应坐标上限。
    for r,key in [('pizhou','pizhou_capacity_cost'),('city','city_capacity_cost')]:
        fig,axes=panels()
        for case,color,ls,marker,lab in [('rigid',BLUE,'--','s','刚性'),('elastic_capacity',G,'-','o','弹性')]:
            aa=plans[r,case]['annual'];xx=[a['year']for a in aa]
            for ax,yy,label in zip(axes,[[a['capacity_mva']for a in aa],[a['cumulative_lifecycle_npv_10k']for a in aa]],['主变容量 / MVA','累计费用现值 / 万元']):
                ax.plot(xx,yy,color=color,ls=ls,marker=marker,markersize=3,label=lab);ax.set_ylabel(label);ax.set_xticks([2021,2025,2030]);clean(ax)
        axes[0].legend(ncol=2);result[key]=save(fig,key)
    fig,axes=panels(size=(9.1,2.4));xx=np.arange(3)
    for ax,r,cn in zip(axes,['pizhou','city'],['邳州','市区']):
        yy=np.array([sum(a[k]for a in plans[r,'elastic_capacity']['annual'])-sum(a[k]for a in plans[r,'rigid']['annual'])for k in ['transformer_npv_10k','storage_npv_10k','line_npv_10k']])
        bars=ax.bar(xx,yy,color=[O if v>0 else G for v in yy],width=.55);ax.axhline(0,color=GRAY,lw=.8)
        ax.set(xticks=xx,xticklabels=['主变','储能','联络'],ylabel=cn+' 弹性−刚性 / 万元',ylim=(-16500,18500));clean(ax)
        for bar,v in zip(bars,yy):ax.text(bar.get_x()+bar.get_width()/2,v+(500 if v>=0 else-500),f'{v:+.2f}',ha='center',va='bottom'if v>=0 else'top',fontsize=11)
    result['cost_difference']=save(fig,'cost_difference')
    fig,axes=panels(3);xx=np.arange(2)
    for ax,key,label in zip(axes,['capacity_mva','storage_mwh','cumulative_lines'],['在役主变 / MVA','储能额定能量 / MWh','累计新增联络 / 条']):
        for case,color,offset,lab in [('rigid',BLUE,-.18,'刚性'),('elastic_capacity',G,.18,'弹性')]:
            yy=[plans[r,case]['annual'][-1][key]for r in ['pizhou','city']];bars=ax.bar(xx+offset,yy,width=.32,label=lab,color=color)
            ax.bar_label(bars,labels=[str(int(v))if key=='cumulative_lines'else f'{v:.2f}'for v in yy],padding=3,fontsize=9)
        ax.set_xticks(xx,['邳州','市区']);ax.set_ylabel(label);ax.set_ylim(0,ax.get_ylim()[1]*1.25);clean(ax)
    axes[0].legend(ncol=2,fontsize=9,loc='upper left');result['equipment']=save(fig,'equipment')
    tables=json.loads((ROOT/'研究报告/02图表/当前版/计算表.json').read_text())
    rows=lambda k:[[x.strip()for x in line.strip('|').split('|')]for line in tables[k].splitlines()if line.startswith('|')][2:]
    fig,axes=panels(3);rr=rows('forecast_pv')
    for col,color,marker,lab in [(4,G,'-o','邳州'),(3,BLUE,'--s','市区')]:axes[0].plot([int(a[0])for a in rr],[float(a[col])for a in rr],marker,color=color,label=lab)
    axes[0].set(ylabel='光伏装机 / MW',xticks=[2025,2030]);axes[0].legend();clean(axes[0])
    # 2025年两项现状指标及其原表现方式保持。
    for ax,values,label in zip(axes[1:],[[1.63,.32],[40.,9.]],['2025装机渗透率','2025电量渗透率 / %']):
        bars=ax.bar(['邳州','市区'],values,color=[G,BLUE],width=.55);ax.bar_label(bars,labels=[f'{v:.2f}'for v in values],padding=4,fontsize=12);ax.set_ylim(0,max(values)*1.3);ax.set_ylabel(label);clean(ax)
    result['pv']=save(fig,'pv')
    return result


def cell_text(cell):
    if isinstance(cell,str):return cell
    return cell.get('text','')or''.join(r.get('text','')for p in cell.get('paragraphs',[])for r in p.get('runs',[]))


def cell_value(cell,value):
    if isinstance(cell,str):return value
    cell=deepcopy(cell)
    if 'paragraphs'in cell:
        p=cell['paragraphs'][0];run=deepcopy(p.get('runs',[{}])[0]);run['text']=str(value);p['runs']=[run];cell['paragraphs']=[p]
    else:cell['text']=str(value)
    return cell


def table_values(root,index,values):
    groups=root.xpath('//*[local-name()="g" and @data-pptx-replace-with="table"]');metadata=groups[index].find(sq('metadata'));d=json.loads(metadata.text)
    assert len(values)<=len(d['rows'])
    for row,vals in zip(d['rows'],values):
        assert len(row)==len(vals)
        for i,value in enumerate(vals):row[i]=cell_value(row[i],str(value))
    oldcount=len(d['rows']);d['rows']=d['rows'][:len(values)]
    if len(values)<oldcount:
        heights=d.get('row_heights',[])
        if heights:d['height']*=sum(heights[:len(values)])/sum(heights);d['row_heights']=heights[:len(values)]
    metadata.text=json.dumps(d,ensure_ascii=False,separators=(',',':'))


def replace_slot(root,contains,lines):
    candidates=[t for t in root.xpath('//*[local-name()="text"]')if contains in ''.join(t.itertext())]
    assert len(candidates)==1,(contains,len(candidates))
    node=candidates[0]
    for child in list(node):node.remove(child)
    node.text=None
    for i,line in enumerate(lines):
        child=E.SubElement(node,sq('tspan'))
        if i:child.set('data-paragraph-line-break','1')
        child.text=line


def update():
    images=pictures();edit_plan=json.loads((WORK/'2030数据替换计划.json').read_text())
    numbers=[r['输出页']for r in edit_plan['逐页映射']if r['处理']=='edited'];backup=WORK/'edit-baseline';backup.mkdir(exist_ok=True)
    for number in numbers:
        path=AUTH/f'slide_{number:02}.svg';baseline=backup/path.name
        if not baseline.exists():shutil.copy2(path,baseline)
        doc=E.parse(str(baseline));root=doc.getroot()
        for n in root.iter():
            if n.tag==sq('metadata'):continue
            if n.text:n.text=n.text.replace('2035','2030')
            if n.tail:n.tail=n.tail.replace('2035','2030')
        image_key={8:'pv',19:'pizhou_capacity_cost',20:'city_capacity_cost',21:'cost_difference',22:'equipment'}.get(number)
        if image_key:
            candidates=[n for n in root.xpath('//*[local-name()="image"]')if float(n.get('width','0'))>800 and float(n.get('height','0'))<500]
            assert len(candidates)==1;candidates[0].set('href',images[image_key])
        if number==19:
            replace_slot(root,'容量路径：',['容量路径：弹性方案2030年主变2388.50 MVA、容载比2.04；刚性分别为2125.50 MVA、','1.81。'])
            replace_slot(root,'措施替代：',['措施替代：期末弹性储能69.66 MWh、累计新增联络6条，均低于刚性。评价期费用','19668.62万元，较刚性减少1882.68万元。'])
        elif number==20:
            replace_slot(root,'市区费用优势',['市区2030年弹性费用高于刚性'])
            table_values(root,0,[['比较项目','刚性方案','弹性方案','工程含义'],['2030累计费用 / 万元','14819.77','16806.54','弹性增加1986.77万元'],['2030储能 / MWh','12.04','0.00','弹性未新增储能'],['2030新增联络累计 / 条','32','0','弹性未新增联络'],['2030主变 / MVA','3140.50','3413.00','站内补强增加272.50 MVA']])
        elif number==21:
            table_values(root,0,[['地区','刚性 / 万元','弹性 / 万元','弹性费用变化 / 万元','主要费用变化'],['邳州','21551.31','19668.62','减少1882.68','配套节省额超过主变投入增加'],['市区','14819.77','16806.54','增加1986.77','主变投入增加超过配套节省额']])
        elif number==22:
            replace_slot(root,'邳州组合：',['邳州组合：弹性主变容量较大，期末储能由刚性153.94 MWh减至69.66 MWh，累计新增联络由','25条减至6条，站内容量与配套支撑共同调整。'])
            replace_slot(root,'市区组合：',['市区组合：弹性主变较刚性多272.50 MVA，未新增储能和联络。刚性配储12.04 MWh，','累计新增联络32条。站内补强与配套工程的投入在2030年前形成不同费用。'])
        elif number==23:
            table_values(root,0,[['2030年站点','刚性主变 / MVA','弹性主变 / MVA','差异对应的任务'],['戴圩变','31.5+63','31.5+63','两方案均保留两台主变'],['兴塘变','20+40','31.5+40','N-1剩余容量20.00→31.50 MVA'],['八义集变','31.5+63','31.5+63','容量相同，两方案均未新增储能']])
            table_values(root,1,[['比较维度','代表站与结果','工程含义'],['设备结构','兴塘变：N-1剩余容量20.00→31.50 MVA','更换较小主变提高故障后剩余能力。'],['局部支撑','八义集变：主变容量相同，储能均0.00 MW','本地设备规模相同，转接任务按年度方案校核。']])
        elif number==28:
            replace_slot(root,'两地区弹性方案费用现值合计减少',['截至2030年，邳州弹性费用减少1882.68万元，','市区增加1986.77万元。六表288单元提供有条件','的容量初选窗口。'])
        elif number in [30,31]:
            group=root.xpath('//*[local-name()="g" and @data-pptx-replace-with="table"]')[0];d=json.loads(group.find(sq('metadata')).text)
            values=[[cell_text(c)for c in row]for row in d['rows']];values=[row for j,row in enumerate(values)if j==0 or int(row[0])<=2030]
            table_values(root,0,values)
        path.write_bytes(E.tostring(doc,xml_declaration=True,encoding='UTF-8'))
    notes={
        17:'各投运批次的初始投资、更新和固定运维统一折算至2021年末，再按主变、储能和线路项目汇总。固定运维从投运次年计至2041年，2022至2030年投运设备均未触发更新。期末残值、替换设备运维变化、储能购电和损耗、收益抵扣等沿用报告现有费用边界。',
        19:'2030年邳州弹性主变2388.50 MVA、容载比2.04，刚性分别为2125.50 MVA、1.81。弹性储能69.66 MWh、累计新增联络6条，低于刚性的153.94 MWh和25条。两方案费用现值分别为19668.62万元和21551.31万元，弹性减少1882.68万元。',
        20:'2030年市区弹性主变3413.00 MVA、容载比1.85，刚性为3140.50 MVA、1.70。弹性未新增储能和联络，刚性配储12.04 MWh、累计新增联络32条。弹性费用16806.54万元，高于刚性14819.77万元，配套工程节省额尚未抵消前期主变投入增加。',
        21:'费用按区县分别比较。邳州储能和联络费用下降共同抵消较多主变支出，弹性减少1882.68万元；市区主变支出增加超过储能与联络的节省额，弹性增加1986.77万元。费用均对应2030年前新增工程至2041年末的建设及固定运维现值。',
        22:'2030年邳州弹性主变容量较大，储能69.66 MWh、累计新增联络6条，刚性分别为153.94 MWh、25条。市区弹性主变比刚性多272.50 MVA，未新增储能和联络，刚性配储12.04 MWh、累计新增联络32条。',
        23:'2030年戴圩变和八义集变两方案均为31.50加63.00 MVA，均未新增储能。兴塘变刚性为20.00加40.00 MVA，弹性为31.50加40.00 MVA，最大单台停运后剩余容量分别为20.00 MVA和31.50 MVA。',
        28:'研究形成运行特征、工程费用、地区逐年方案和五参数推荐矩阵等成果。2030年邳州弹性费用减少1882.68万元，市区增加1986.77万元，分别反映两地源荷、网络和建设时序条件。六类场景288个窗口用于片区容量初选，并结合站级供电任务落实设备方案。'}
    for i,content in notes.items():(WORK/f'notes/slide_{i:02}.md').write_text(content+'\n')
    (WORK/'validation/2030数据同步登记.json').write_text(json.dumps({'状态':'已按原图表模式替换数据，待原生导出及WPS核验','编辑页':numbers,'图件':images,'原数据':'锁定20261017方案前缀；未更改模型或原结果','未列两地费用合计':True},ensure_ascii=False,indent=2))
    print('已更新原生页',numbers)


if __name__=='__main__':update()
