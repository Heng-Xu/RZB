"""用现有原精度数据复算候选指标相关性与参数配对效应。"""
from pathlib import Path
import csv,json,sys,itertools
import numpy as np
from scipy.stats import pearsonr,spearmanr
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
HERE=Path(__file__).parent;R=ROOT/'研究报告';A=R/'02图表/当前版';D=R/'01研究推荐/当前版'

def table(title,headers,rows):
    return title+'\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,row))+' |\n' for row in rows)

def main():
    data=json.loads((A/'图件原始数值.json').read_text());monthly=np.array(data['月度指标'])
    variables={'电量渗透率':monthly[:,1],'月度容载比':monthly[:,2],'主变负载率估计':monthly[:,3],'光伏电量':monthly[:,4],'用户电量':monthly[:,5],'月正向峰值':monthly[:,6]}
    correlations=[]
    for x,y in itertools.combinations(variables,2):
        correlations.append({'尺度':'邳州2025年月度','指标一':x,'指标二':y,'样本量':12,'Pearson':float(pearsonr(variables[x],variables[y]).statistic),'Spearman':float(spearmanr(variables[x],variables[y]).statistic)})
    growth_rows=[]
    for region,years in data['年度容量与负荷'].items():
        values=np.array([years[str(y)] for y in range(2021,2026)]);capacity,load=values.T;ratio=capacity/load
        rates=load[1:]/load[:-1]-1
        growth_rows.append([region,f'{100*np.dot(rates,[1,2,3,4])/10:.2f}%',f'{100*rates.mean():.2f}%',f'{100*((load[-1]/load[0])**.25-1):.2f}%'])
        for name,v,target,n in [('年网供最大负荷',load,ratio,5),('公用主变容量',capacity,ratio,5),('年度同比增长率',rates,ratio[1:],4)]:
            correlations.append({'尺度':region+'年度','指标一':name,'指标二':'年度容载比','样本量':n,'Pearson':float(pearsonr(v,target).statistic),'Spearman':float(spearmanr(v,target).statistic)})
    tables=json.loads((A/'计算表.json').read_text())
    candidates=[
        ['负荷密度','负荷/有效供电面积','缺同范围面积记录','用于供电区域类别核定'],
        ['供电区域类别','导则分类及设备台账','案例类别；市区按A类假定','结构条件，按类别校核'],
        ['装机渗透率（源荷比）','同范围装机/用户最大负荷','案例典型场景估计','核心源荷参数'],
        ['电量渗透率','发电量/用户电量','月度装机与样本电量估计','与装机指标换算，辅助校核'],
        ['主变最大负载率及趋势','设备极值/额定容量','2025年负载率；缺多年同台记录','现状诊断，趋势待补充'],
        ['正向、反向净负荷峰值','逐时功率方向极值','样本时序及典型场景','直接进入容量约束'],
        ['年负荷平均增长率','年度同比率加权','五年同范围年度负荷','核心需求参数'],
        ['95%峰值持续时间','连续近峰段最长时长','2025年方向峰段模板','核心支撑参数'],
        ['负荷分散系数','各站最大负荷之和/站群同时最大负荷','导则影响因素；案例样本及研究情景','结构条件，保留差异'],
        ['初始转供率','可转负荷/源端负荷','邳州样本；市区假定','技术能力条件'],
        ['主变台数、规格及扩建条件','设备台账及预留位置','案例设备；模板规格','设备候选及实施约束'],
        ['线路类型、长度与敷设比例','架空/电缆及工程长度','案例参考；两类敷设假定','分类成本条件'],
        ['主变与线路、储能成本比','同有效MW初始投资之比','工程资料及价格情景','储能比为核心参数；线路比为费用条件'],
        ['储能可用能量与效率','保证出力及荷电状态','本次采用铭牌静态折算','工程阶段连续时序校核'],
    ]
    tables['driver_candidates']=table('表3-0 候选指标及筛选处理',['候选指标','计算或作用方式','资料条件','处理结果'],candidates)
    selected=[]
    for x in correlations:
        if x['指标二'] in ('月度容载比','年度容载比'):selected.append(x)
        elif x['指标一']=='月度容载比':selected.append({**x,'指标一':x['指标二'],'指标二':x['指标一']})
    tables['driver_correlations']=table('表3-0 候选指标与容量负荷比的样本相关性',['样本范围','被解释指标','候选指标','样本量','Pearson','Spearman'],[[x['尺度'],x['指标二'],x['指标一'],x['样本量'],f"{x['Pearson']:.2f}",f"{x['Spearman']:.2f}"] for x in selected])
    selected=[x for x in correlations if x['尺度']=='邳州2025年月度' and '月度容载比' not in (x['指标一'],x['指标二']) and ('电量渗透率' in (x['指标一'],x['指标二']) or (x['指标一'],x['指标二'])==('主变负载率估计','月正向峰值'))]
    tables['driver_intercorrelations']=table('表3-0 候选指标之间的相关性',['指标一','指标二','Pearson','处理依据'],[[x['指标一'],x['指标二'],f"{x['Pearson']:.2f}",'同口径季节关联' if x['Pearson']<.999 else '直接换算，合并使用'] for x in selected])
    tables['growth_method_comparison']=table('表3-0 三种年增长率估计方法',['地区','递增加权平均','四年等权平均','四年复合增长率'],growth_rows)
    rows=json.loads((D/'外推逐点结果.json').read_text())
    params=['装机渗透率','年负荷平均增长率','95%峰值持续时间h','供电区域','线路价格倍数','储能价格倍数','负荷分布','线路类型']
    encoded=np.array([[r[k] for k in ('装机渗透率','年负荷平均增长率','95%峰值持续时间h','主变线路成本比','主变储能成本比_3h')] for r in rows])
    effects=[]
    for key in ['装机渗透率','年负荷平均增长率','95%峰值持续时间h','线路价格倍数','储能价格倍数','线路类型']:
        groups={}
        for row in rows:
            fixed=tuple(row[k] for k in params if k!=key);groups.setdefault(fixed,[]).append(row)
        delta=[];cost_delta=[];cost_relative=[];project_delta=[]
        for group in groups.values():
            ordered=sorted(group,key=lambda r:r[key]);low,high=ordered[0],ordered[-1]
            delta.append(high['推荐容载比']-low['推荐容载比']);cost_delta.append(high['全寿命费用万元']-low['全寿命费用万元'])
            cost_relative.append((high['全寿命费用万元']-low['全寿命费用万元'])/low['全寿命费用万元'])
            project_delta.append(high['联络项目数']-low['联络项目数'])
        delta=np.array(delta)
        effects.append({'参数':key,'配对数量':len(delta),'容载比变化平均':float(delta.mean()),'容载比绝对变化中位数':float(np.median(abs(delta))),'容载比改变比例':float(np.mean(abs(delta)>1e-6)),'最大绝对变化':float(max(abs(delta))), '费用变化平均万元':float(np.mean(cost_delta)),'费用变化率平均':float(np.mean(cost_relative)),'联络项目数改变比例':float(np.mean(np.abs(project_delta)>0)), '说明':'同一组其余参数下该参数最大值减最小值；线路类型为电缆为主减架空为主；仅比较端点，不是相邻步长变化'})
    fmt=lambda v:f'{0.0 if abs(v)<.005 else v:.2f}'
    tables['controlled_driver_effects']=table('表5-0 固定其他条件时单参数端点变化的影响',['变化参数','配对数','容载比平均变化','最大绝对变化','比值改变占比','费用平均变化/万元'],[[e['参数'],e['配对数量'],fmt(e['容载比变化平均']),fmt(e['最大绝对变化']),f"{e['容载比改变比例']*100:.2f}%",fmt(e['费用变化平均万元'])] for e in effects])
    tables['driver_selection_evidence']=table('表3-0 入选参数的证据与使用范围',['参数或条件','筛选依据','在本研究中的使用'],[
        ['装机渗透率','反向容量约束；模型端点比值均变化','独立源荷维度，结论限于所设日间场景'],
        ['电量渗透率','月度关联；外推中由装机指标换算','源荷背景及反向校核参考，非独立维度'],
        ['年负荷平均增长率','导则容量储备分档；年度预测及模型配对','独立需求维度；历史小样本关联仅作描述'],
        ['95%峰值持续时间','功率能量关系；19.17%的端点配对比值变化','独立支撑维度，需补充连续时序核定'],
        ['主变与储能成本比','投资资料；17.93%的端点配对比值变化','独立费用维度，按实际持续时间计费'],
        ['线路类型及主变与线路成本比','分类造价；模型配对未出现容量变化','费用条件；暂未证实容载比对其敏感'],
        ['供电类别、转供率及负荷分散系数','设备及网络作用；按模板共同设置','结构条件，查表时保留对应结构'],
        ['负载率趋势、负荷密度','缺多年同台负载率或同范围面积','待补资料；不作为已验证的独立驱动'],
    ])
    result={'样本相关性':correlations,'增长率比较':growth_rows,'配对参数影响':effects,'外推核心数值参数相关矩阵':np.corrcoef(encoded.T).tolist(),'参数矩阵顺序':['源荷比','增长率','持续时间','主变线路成本比','主变储能成本比'],'装机与电量指标相关系数':1.0,'筛选原则':'资料筛查、样本相关性、共享分母及换算关系、技术约束作用、控制参数配对分析；小样本不作因果结论'}
    (HERE/'1003反馈修订/驱动因子复算.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (A/'计算表.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2))
    print(json.dumps({'相关性记录':len(correlations),'参数配对效应':effects,'增长估计':growth_rows},ensure_ascii=False))
if __name__=='__main__':main()
