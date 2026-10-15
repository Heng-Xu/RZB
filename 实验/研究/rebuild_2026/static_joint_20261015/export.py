"""两地区、两种固定起点、刚弹八组方案的逐年结果与静态功率依据。"""
import json
import os
import shutil
from decimal import Decimal,ROUND_HALF_UP

import numpy as np
import pandas as pd

from ..review_20261015.export import workbook
from . import model as m
from .choose import selected


def f2(value):
    return str(Decimal(str(round(float(value),9))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))


def generate():
    for p in [m.PUBLIC,m.REVIEW,m.SOURCE]:p.mkdir(parents=True,exist_ok=True)
    annual=[];fees=[];stations=[];projects=[];rates=[];balances=[];sources=[];checks=[];explain=[];construction=[];reference_rows=[]
    for region,rname in m.REGIONS.items():
        for baseline,bname in m.BASELINES.items():
            inp,scenes,root=m.prepare(region,baseline);ids=list(inp['stations']);lp=m.OperatingLP(inp)
            evidence=m.old.old.station_evidence(inp);names={r['station']:r['name'] or r['station'] for r in evidence}
            for e in evidence:
                for y in inp['years']:rates.append(dict(地区=rname,起点=bname,年份=y,站号=e['station'],站名=names[e['station']],
                    逐站转供率=inp['station_transfer_rates'][e['station']],原表J_MW=e['transferable_mw'],原表K_MW=e['unserved_mw'],
                    既有转供上限_MW=inp['existing_transfer_budget_by_year_mw'][str(y)][e['station']],来源行=e['source_row']))
            for case,cname in m.CASES.items():
                folder=selected(region,baseline,case);assert folder,(region,baseline,case)
                summary=json.loads((folder/'summary.json').read_text());label=dict(地区=rname,起点=bname,方案=cname)
                sources.append(dict(region=region,baseline=baseline,case=case,folder=str(folder.relative_to(m.ROOT)),
                    input_sha256=m.old.sha(root/'inputs.json'),files={name:m.old.sha(folder/name) for name in
                    ['summary.json','stations.csv','projects.csv','chosen_solution.npz','selected_pairs.json','independent_lp.json']}))
                reference=summary['method'].get('reference_cost',summary['cost_npv_10k'])
                fees.append(dict(**label,费用现值_万元=summary['cost_npv_10k'],费用下界_万元=summary['solver']['dual_bound'],
                    相对间隙=summary['solver']['mip_gap'],经济参考费用_万元=reference,
                    较经济参考费用增加占比=summary['cost_npv_10k']/reference-1 if reference else 0.,结果来源=summary['method']['type']))
                annual.append(dict(**label,年份=2021,规划负荷_MW=inp['initial_peak_mw'],年末主变_MVA=inp['initial_capacity_mva'],
                    容载比=inp['initial_capacity_mva']/inp['initial_peak_mw'],当年新购主变_MVA=0.,当年净增容量_MVA=0.,
                    当年新增储能_MWh=0.,年末储能_MWh=0.,当年新增联络_条=0,累计新增联络_条=0))
                before=inp['initial_capacity_mva']
                previous_units=np.array([s['initial_units']+[0.] for s in inp['stations'].values()])
                if case=='elastic_free':
                    ref_folder=m.best(region,baseline,case);ref_summary=json.loads((ref_folder/'summary.json').read_text())
                    reference_rows.extend(dict(地区=rname,起点=bname,年份=r['year'],主变_MVA=r['capacity_mva'],容载比=r['clr'],
                        储能_MWh=r['storage_mwh'],累计新联络_条=r['cumulative_lines'],全期费用现值_万元=ref_summary['cost_npv_10k']) for r in ref_summary['annual'])
                for a in summary['annual']:
                    y=a['year'];u,n,built=m.old.old.assets_from_csv(inp,folder,y)
                    bp=np.array([min(.1,.215*.76/max(1,inp['stations'][s]['forward_duration_h'])) for s in ids])*n
                    bn=np.array([min(.1,.215*.76/max(1,inp['stations'][s]['reverse_duration_h'])) for s in ids])*n
                    annual.append(dict(**label,年份=y,规划负荷_MW=a['peak_mw'],年末主变_MVA=a['capacity_mva'],容载比=a['clr'],
                        当年新购主变_MVA=a['purchased_transformer_mva'],当年净增容量_MVA=a['capacity_mva']-before,
                        当年新增储能_MWh=a['new_storage_mwh'],年末储能_MWh=a['storage_mwh'],
                        储能正向有效功率_MW=float(bp.sum()),储能反向有效功率_MW=float(bn.sum()),
                        当年新增联络_条=a['new_lines'],累计新增联络_条=a['cumulative_lines'],
                        主变费用现值_万元=a['transformer_npv_10k'],储能费用现值_万元=a['storage_npv_10k'],联络费用现值_万元=a['line_npv_10k']))
                    before=a['capacity_mva']
                    for j,sid in enumerate(ids):
                        if np.any(u[j]>previous_units[j]+1e-8):
                            bought=float(np.where(u[j,:2]>previous_units[j,:2]+1e-8,u[j,:2],0).sum()+u[j,2]-previous_units[j,2])
                            construction.append(dict(**label,年份=y,站号=sid,站名=names[sid],
                                原主变组合='+'.join(f'{v:g}' for v in previous_units[j] if v),
                                新主变组合='+'.join(f'{v:g}' for v in u[j] if v),净增容量_MVA=float(u[j].sum()-previous_units[j].sum()),新购容量_MVA=bought))
                    previous_units=u.copy()
                    for j,sid in enumerate(ids):stations.append(dict(**label,年份=y,站号=sid,站名=names[sid],
                        第一台_MVA=float(u[j,0]),第二台_MVA=float(u[j,1]),第三台_MVA=float(u[j,2]),
                        主变组合='+'.join(f'{v:g}' for v in u[j] if v),主变_MVA=float(u[j].sum()),
                        最大单台退出后有功能力_MW=float(.95*(u[j].sum()-u[j].max())),储能_MWh=float(n[j]*.215),
                        正向有效储能_MW=float(bp[j]),反向有效储能_MW=float(bn[j])))
                    # 正常取每站正/反向极值及地区极值，事故取故障站自身正/反向极值。
                    normal_hours=set(map(int,np.argmax(scenes[y],axis=0)))|set(map(int,np.argmin(scenes[y],axis=0)))
                    normal_hours|={int(np.argmax(scenes[y].sum(axis=1))),int(np.argmin(scenes[y].sum(axis=1)))}
                    critical={(h,-1) for h in normal_hours}
                    critical|={(int(np.argmax(scenes[y][:,j])),j) for j in range(len(ids))}
                    critical|={(int(np.argmin(scenes[y][:,j])),j) for j in range(len(ids))}
                    normal_max=fault_max=normal_storage=0.
                    for h,f in sorted(critical):
                        p=scenes[y][h];ready=lp.prepared(p,y,u,n,built);dispatch=lp.dispatch(p,ready,f)
                        outgoing=np.zeros(len(ids));incoming=np.zeros(len(ids))
                        for arc,value in dispatch['flow']:
                            *_,sa,sb=lp.arcs[arc];outgoing[sa]+=value;incoming[sb]+=value
                        served=p-outgoing+incoming;cap=.95*u.sum(axis=1);rev=.8*cap
                        if f>=0:cap[f]-=.95*u[f].max();rev[f]=cap[f]
                        discharge=np.maximum(served-cap,0.);charge=np.maximum(-served-rev,0.)
                        assert np.max(discharge-bp)<1e-5 and np.max(charge-bn)<1e-5
                        assert abs(served.sum()-p.sum())<1e-7
                        if f<0:normal_max=max(normal_max,dispatch['total_mw']);normal_storage=max(normal_storage,float(max(discharge.max(),charge.max())))
                        else:fault_max=max(fault_max,dispatch['total_mw'])
                        for j,sid in enumerate(ids):
                            show=(f<0 and (h in {int(np.argmax(scenes[y].sum(axis=1))),int(np.argmin(scenes[y].sum(axis=1))),
                                int(np.argmax(scenes[y][:,j])),int(np.argmin(scenes[y][:,j]))})) or (f>=0 and (j==f or outgoing[j]>1e-7 or incoming[j]>1e-7))
                            if not show:continue
                            balances.append(dict(**label,年份=y,截面=h,
                            工况='正常' if f<0 else 'N-1',故障站='正常' if f<0 else names[ids[f]],
                            站号=sid,站名=names[sid],原净负荷_MW=float(p[j]),转出_MW=float(outgoing[j]),转入_MW=float(incoming[j]),
                            转供后净负荷_MW=float(served[j]),主变正向限值_MW=float(cap[j]),主变反向限值_MW=float(rev[j]),
                            所需放电_MW=float(discharge[j]),所需充电_MW=float(charge[j]),储能正向上限_MW=float(bp[j]),储能反向上限_MW=float(bn[j])))
                    explain.append(dict(**label,年份=y,所列典型工况数=len(critical),正常最大转供_MW=normal_max,N1最大转供_MW=fault_max,
                        正常所需单站最大储能支撑_MW=normal_storage))
                projects.extend(dict(**label,**r) for r in m.old.old.base.previous.rows(folder/'projects.csv'))
                proof=json.loads((folder/'independent_lp.json').read_text())
                checks.extend(dict(**label,**r) for r in proof['checks'])
                print('EXPORTED_JOINT',region,baseline,case,flush=True)
    frames={'逐年方案':pd.DataFrame(annual),'费用及精度':pd.DataFrame(fees),'逐站设备':pd.DataFrame(stations),
        '联络项目':pd.DataFrame(projects),'逐站转供依据':pd.DataFrame(rates),'典型工况支撑':pd.DataFrame(balances),
        '典型转供汇总':pd.DataFrame(explain),'静态全工况核验':pd.DataFrame(checks),'逐年主变建设':pd.DataFrame(construction),
        '弹性经济参考':pd.DataFrame(reference_rows)}
    # 在同一极值、同一故障下比较本站支撑，避免只用地区容量解释储能差异。
    bd=frames['典型工况支撑'];st=frames['逐站设备'];key=['地区','起点','年份','截面','工况','故障站','站号','站名']
    r=bd[(bd['方案']==m.CASES['rigid'])&(bd['年份']==2025)&(bd['工况']=='N-1')&(bd['故障站']==bd['站名'])].copy()
    r['支撑大小']=np.maximum(r['原净负荷_MW']-r['主变正向限值_MW'],-r['原净负荷_MW']-r['主变反向限值_MW'])
    r=r.sort_values('支撑大小',ascending=False).drop_duplicates(['地区','起点','站号'])
    e=bd[bd['方案']==m.CASES['elastic_free']]
    paired=r.merge(e,on=key,suffixes=('_刚性','_弹性'));comparison=[]
    for d in paired.to_dict('records'):
        label={k:d[k] for k in ['地区','起点','年份','站号','站名']}
        row=dict(**label,截面=d['截面'],方向='反向吸收' if d['原净负荷_MW_刚性']<0 else '正向支撑',原净负荷_MW=d['原净负荷_MW_刚性'])
        for cname,suffix in [(m.CASES['rigid'],'刚性'),(m.CASES['elastic_free'],'弹性')]:
            sr=st[(st['地区']==d['地区'])&(st['起点']==d['起点'])&(st['年份']==2025)&(st['站号']==d['站号'])&(st['方案']==cname)].iloc[0]
            row.update({suffix+'主变组合':sr['主变组合'],suffix+'主变_MVA':sr['主变_MVA'],suffix+'储能_MWh':sr['储能_MWh'],
                suffix+'N1主变_MW':d['主变正向限值_MW_'+suffix],suffix+'转出_MW':d['转出_MW_'+suffix],suffix+'转入_MW':d['转入_MW_'+suffix],
                suffix+'所需放电_MW':d['所需放电_MW_'+suffix],suffix+'所需充电_MW':d['所需充电_MW_'+suffix]})
        comparison.append(row)
    frames['关键站替代关系']=pd.DataFrame(comparison)
    notes=pd.DataFrame([
        dict(事项='规划起点',说明='2021年固定共同起点，2022—2025逐年优化；原表补充组保留2021地区总容量，逐站组合为既有冻结标定'),
        dict(事项='共同替代',说明='正常与N-1均允许储能和10kV联络参与；共同投资设备、逐工况运行，区域转供守恒'),
        dict(事项='工程实施条件',说明='每一主变位置在四年内最多更换一次，新购设备继续在役；两方案共同采用的建设组织假设，不是新增安全标准'),
        dict(事项='刚弹差异',说明='刚性保留容载比2.0新增容量控制及在役容量保留，弹性取消该控制；正常及事故物理边界一致，无两方案容量/储能/联络排序约束'),
        dict(事项='弹性工程优选',说明='保留费用寻优所得可行解为经济参考，在其费用5%以内优先减少末年累计新联络，次选费用较低布局；5%为本研究工程优选容差，增量费用单列，不称自由费用最优'),
        dict(事项='静态储能',说明='有效功率同时受100kW/215kWh单柜额定功率及76%可用电量/持续时间约束；邳州正向2h、市区6h，反向沿用各站规定时长'),
        dict(事项='采购容量',说明='新购主变容量为更换与扩建采购铭牌容量之和，净增容量扣除同期被替换容量'),
        dict(事项='范围',说明='保留有限正常/N-1同期截面，不新增SOC；典型转供取固定设备下最小总转供的可行运行方式'),
        dict(事项='经济参数',说明='主变/线路/储能寿命40/40/25年，运维4.2%/2.2%/3%，折现6%，评价截止2041；原价格不变'),
        dict(事项='费用精度',说明='正间隙为已核验可行方案与有效费用下界之差，保留求解状态，不将固定布局LP最优称为规划全局最优')])
    frames={'方案说明':notes,**frames}
    last=frames['逐年方案'].query('年份==2025').merge(frames['费用及精度'],on=['地区','起点','方案'])
    frames['末年与费用对比']=last
    for name,frame in frames.items():frame.to_csv(m.PUBLIC/(name+'.csv'),index=False,encoding='utf-8-sig')
    workbook(m.PUBLIC/'两区县全套逐年方案.xlsx',frames)
    m.old.dump(m.REVIEW/'案例来源与校核.json',dict(verified=True,sources=sources,checks=checks,
        static_pairs=sum(r['checked_pairs'] for r in checks),schemes=len(sources),normal_storage_allowed=True))
    source_files=[m.old.OUT/r/(b+'_reverse80')/'inputs.json' for r in m.REGIONS for b in m.BASELINES]
    m.old.dump(m.SOURCE/'输入与模型来源.json',dict(sources=[dict(path=str(p.relative_to(m.ROOT)),sha256=m.old.sha(p)) for p in source_files],
        工程条件='新购主变在四年期内不重复更换；正常储能与联络恢复参与静态平衡',初始年份=2021,优化年份=[2022,2023,2024,2025]))
    return frames


def matrix_copy():
    src=m.ROOT/'研究报告/01研究推荐/当前版/双区县经济方案_20261015'
    names=['推广典型响应矩阵.xlsx','矩阵说明.csv','典型响应推荐矩阵.csv','典型场景完整节点.csv','全部完整组响应审查.csv']
    records=[]
    for name in names:
        source=src/name;shutil.copyfile(source,m.PUBLIC/name)
        assert m.old.sha(source)==m.old.sha(m.PUBLIC/name)
        records.append(dict(path=str(source.relative_to(m.ROOT)),sha256=m.old.sha(source)))
    m.old.dump(m.SOURCE/'推广矩阵继承依据.json',dict(来源=records,
        说明='推广原本采用正常及N-1共同静态替代，单期采购无期内重复更换；保留原始18典型节点和四档响应，不重写数值'))


def memo(frames):
    a=frames['逐年方案'];f=frames['费用及精度'];parts=['# 两区县静态联合替代方案汇总','',
        '本套共8组：邳州、市区×共同仿真起点、保留2021原表容量起点×刚性、弹性经济优选方案。2021年固定，2022—2025年逐年规划。',
        '', '正常运行恢复储能支撑与联络转供，N-1继续作为共同安全校核。主变、储能与联络共同按费用比选；新购主变在四年内继续使用，避免同一位置短期重复更换。该建设条件对两方案一致，不设置两方案结果排序。',
        '', '弹性保留自由费用可行解作为经济参考，在参考费用5%以内优先简化联络工程，实际增量费用单列。该项是工程优选条件，不把结果称为自由费用全局最优。', '']
    for baseline,bname in m.BASELINES.items():
        parts+=['## '+bname,'','|地区|方案|2021起点/MVA|2022主变/MVA|2023主变/MVA|2024主变/MVA|2025主变/MVA|2025容载比|2025储能/MWh|累计新联络/条|费用现值/万元|','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for region,rname in m.REGIONS.items():
            for case,cname in m.CASES.items():
                sub=a[(a['地区']==rname)&(a['起点']==bname)&(a['方案']==cname)].sort_values('年份');fee=f[(f['地区']==rname)&(f['起点']==bname)&(f['方案']==cname)].iloc[0];last=sub.iloc[-1]
                vals=[rname,cname,*[f2(v) for v in sub['年末主变_MVA']],f2(last['容载比']),f2(last['年末储能_MWh']),str(int(last['累计新增联络_条'])),f2(fee['费用现值_万元'])]
                parts.append('|'+ '|'.join(vals)+'|')
        parts+=['']
    parts+=['## 逐年新增与年末累计','',
        '|地区|起点|方案|年份|容载比|当年净增主变/MVA|当年新增储能/MWh|年末储能/MWh|当年新增联络/条|累计新增联络/条|',
        '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for row in a[a['年份']>2021].itertuples(index=False):
        d=row._asdict();parts.append('|'+ '|'.join([d['地区'],d['起点'],d['方案'],str(d['年份']),f2(d['容载比']),f2(d['当年净增容量_MVA']),f2(d['当年新增储能_MWh']),f2(d['年末储能_MWh']),str(d['当年新增联络_条']),str(d['累计新增联络_条'])])+'|')
    parts+=['','## 工程简化的费用变化','',
        '|地区|起点|弹性经济参考/万元|采用方案/万元|增加占比|','|---|---|---:|---:|---:|']
    for r in f[f['方案']==m.CASES['elastic_free']].to_dict('records'):
        parts.append(f'|{r["地区"]}|{r["起点"]}|{f2(r["经济参考费用_万元"])}|{f2(r["费用现值_万元"])}|{r["较经济参考费用增加占比"]:.0%}|')
    key=frames['关键站替代关系']
    x=key[(key['地区']=='邳州')&(key['起点']==m.BASELINES['compressed'])&(key['站名']=='兴塘变')]
    if len(x):
        r=x.iloc[0]
        parts+=['','## 容量与配套减少如何对应','',
            f'邳州兴塘是直接的主变替代储能例子：刚性主变为{r["刚性主变组合"]} MVA，弹性为{r["弹性主变组合"]} MVA。最大单台退出后，主变有功能力由{f2(r["刚性N1主变_MW"])} MW提高到{f2(r["弹性N1主变_MW"])} MW。',
            f'在同一反向极值工况，所需充电吸收由{f2(r["刚性所需充电_MW"])} MW降至{f2(r["弹性所需充电_MW"])} MW，对应储能由{f2(r["刚性储能_MWh"])} MWh降至{f2(r["弹性储能_MWh"])} MWh。容量补到局部短板后，储能需求下降有明确的功率平衡依据。',
            '地区总容量差还包含其他站点配置调整，因此要同时查看逐站容量和最大单台退出后的剩余能力，不能把地区净增MVA直接与储能铭牌MWh相减。']
    parts+=['','## 逐年建设节点分析','',
        '邳州共同起点：2022年弹性提前补强邳城、兴塘，并在邢楼扩建第三台主变，减少早期对储能和联络的依赖。刚性在2.0新增容量控制内安排建设，土山直接更换到50 MVA，保持新购设备期内不再更换。2023年负荷回落，两方案设备均保持，容载比随负荷下降而上升。2024年刚性补建邳城和邢楼，弹性补强八义集较小的一台主变，为减少后续联络提供接收与故障支撑能力。2025年两方案主变均保持，新增需求由储能和联络承担，兴塘的站内补强使弹性所需储能明显较少。',
        '市区共同起点：2022年弹性将翟山40 MVA主变更换为63 MVA，最大单台80 MVA退出后的剩余有功能力由38.00 MW提高到59.85 MW；刚性保留原组合并建设联络。2023年负荷回升，刚性再增加2条联络，弹性利用已有网络及补强后的站内能力。2024年负荷回落，2025年再次回升，两方案均保持此前设备。弹性没有新增联络，既有联络仍参与正常和N-1转供。',
        '邳州原表起点：2027 MVA存量高于各年2倍地区负荷，刚性保留该容量，通过储能及联络补足局部缺口。弹性2022年在戴庄、铁富、土山、邢楼及兴塘补强，之后保持主变。2023年负荷回落而设备保持，容载比上升；2024年刚性增加储能，弹性已投运设备继续承担需求。2025年两者增加配套措施，刚性储能同时承担正常反向吸收及事故支撑，弹性以较多站内容量降低储能依赖。',
        '市区原表起点：四年两方案均可利用3113.50 MVA在役主变和既有联络完成本次静态校核，保留零新增结果。2022—2025年的容载比变化来自年度负荷变化，正常与N-1仍存在转供任务，零新增费用对应存量网络继续承担需求。']
    parts+=['','## 核验与使用范围','',
        '全部8组均完成所列地区及各站局部极值的正常与最大单台主变N-1静态校核。保留原表容量的邳州刚性允许储能参与正常反向吸收，已恢复可行。',
        '市区原表起点若两方案均无新增措施，表示该标定设备及本次静态负荷条件已满足校核，结果如实保留。',
        '推广矩阵保留原已核验的典型四档响应，配套给出完整细节点。线路价格条件集中列明，不另作独立分类讨论。',
        '本套为独立结果包，正式研究报告及讨论稿尚未替换；没有新增全年SOC或新能源利用率结论。', '',
        '费用比较采用具体可行方案；各组费用下界及相对间隙见“费用及精度”。']
    (m.PUBLIC/'两区县全套结果汇总.md').write_text('\n'.join(parts)+'\n',encoding='utf-8')


def figures(frames):
    os.environ.setdefault('MPLCONFIGDIR','/tmp/xuzhou-static-joint-mpl')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FormatStrFormatter
    from matplotlib.font_manager import fontManager,FontProperties
    path='/usr/share/fonts/wps-office/FZFSK.TTF';fontManager.addfont(path);font=FontProperties(fname=path).get_name()
    plt.rcParams.update({'font.family':['Times New Roman',font],'axes.unicode_minus':False,'font.size':11})
    out=m.PUBLIC/'图件';out.mkdir(exist_ok=True);a=frames['逐年方案']
    fig,axes=plt.subplots(2,2,figsize=(11,7))
    for i,region in enumerate(m.REGIONS.values()):
        for j,baseline in enumerate(m.BASELINES.values()):
            ax=axes[i,j]
            for case,color,style in [('刚性方案','#5485A2','o-'),('弹性经济优选方案','#D88344','s--')]:
                sub=a[(a['地区']==region)&(a['起点']==baseline)&(a['方案']==case)].sort_values('年份')
                ax.plot(sub['年份'],sub['容载比'],style,color=color,label=case)
            ax.set_title(region+'：'+baseline);ax.set_xticks(range(2021,2026));ax.set_ylabel('容载比');ax.grid(alpha=.2)
            ax.set_ylim((1.70,2.90) if region=='邳州' else (1.80,2.25));ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    axes[0,0].legend(loc='upper right',fontsize=9)
    fig.tight_layout();fig.savefig(out/'两区县逐年容载比.png',dpi=200);fig.savefig(out/'两区县逐年容载比.pdf');plt.close(fig)


if __name__=='__main__':
    data=generate();matrix_copy();memo(data);figures(data)
