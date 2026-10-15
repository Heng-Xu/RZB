"""两地区、两起点经济方案及逐站运行收支。"""
import json

import numpy as np
import pandas as pd

from ..review_20261015.export import workbook
from ..review_20261015.target_warm import cost
from . import model as m


def full_normal(region,inp,year,lp,units,n,built,fractions):
    path=m.ROOT/f'研究报告/数据来源/当前版/区域时序/{region}_stations.npz'
    z=np.load(path);ids=list(inp['stations']);order=[list(z['station_ids']).index(s) for s in ids]
    raw=z['power_mw'][:,order];profile=raw*inp['annual_observed_peak_mw'][str(year)]/raw.sum(axis=1).max()
    outgoing=np.zeros_like(profile);incoming=np.zeros_like(profile)
    for arc in lp.arcs:
        _,e,d,_,_,sa,sb=arc;v=fractions.get((e['id'],d),0.)*np.maximum(profile[:,sa],0.)
        outgoing[:,sa]+=v;incoming[:,sb]+=v
    served=profile-outgoing+incoming;capacity=.95*units.sum(axis=1)
    violations=np.maximum(np.maximum(served-capacity,-served-.8*capacity),0.)
    worst=float(violations.max());bad=[]
    if any(v>1e-9 for v in fractions.values()):
        for h,p in enumerate(profile):
            r=lp.dispatch_fixed(p,lp.prepared(p,year,units,n,built),-1,fractions)
            worst=max(worst,r['max_violation_mw'])
            if not r['verified']:bad.append(dict(hour=h,violation_mw=r['max_violation_mw']))
    else:bad=[dict(hour=int(h),violation_mw=float(violations[h].max())) for h in np.flatnonzero(violations.max(axis=1)>1e-5)]
    assert abs((served-profile).sum(axis=1)).max()<1e-7
    return dict(year=year,hours=len(profile),station_hours=len(profile)*len(ids),verified=not bad,
        max_violation_mw=worst,max_normal_transfer_mw=float(outgoing.sum(axis=1).max()),violating_hours=len(bad),failures=bad[:20],
        filled_station_hours=int((~z['observed'][:,order]).sum()),profile_sha256=m.old.sha(path))


def infeasible_certificate():
    inp,scenes,root=m.prepare('pizhou','annual_2021');folder=root/'rigid_main'
    solver=json.loads((folder/'iteration_01_solver.json').read_text());assert solver['proven_infeasible']
    lp=m.OperatingLP(inp);units=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]);n=np.zeros(len(units))
    built={e['id'] for e in inp['network']['edges'] if not e['existing']};records=[]
    names={r['station']:r['name'] for r in m.old.old.station_evidence(inp)}
    for y in inp['years']:
        assert 2*inp['annual_observed_peak_mw'][str(y)]<inp['initial_capacity_mva']
        for h,p in enumerate(scenes[y]):
            r=lp.check(p,lp.prepared(p,y,units,n,built),-1)
            if not r['verified']:
                for sid,gap in r['station_deficits'].items():records.append(dict(年份=y,截面=h,站号=sid,站名=names[sid],最小松弛_MW=gap,
                    原净负荷_MW=float(p[list(inp['stations']).index(sid)]),本站初始容量_MVA=sum(inp['stations'][sid]['initial_units'])))
    assert records
    proof=dict(verified=True,input_sha256=m.old.sha(root/'inputs.json'),solver_sha256=m.old.sha(folder/'iteration_01_solver.json'),
        假设='刚性地区容量上限保留2027 MVA，逐站容量非减使全部初始主变冻结；正常储能备用。放开全部候选线路及间隔数量作为原问题的宽松对照，仍有正常反向缺口。',records=records)
    m.old.dump(m.REVIEW/'邳州原表起点刚性无解独立证据.json',proof)
    return records


def annual_record(label,year,peak,capacity=None,status='可行',**extra):
    return dict(**label,年份=year,状态=status,规划负荷_MW=peak,年末主变_MVA=capacity,
        容载比=None if capacity is None else capacity/peak,**extra)


def generate():
    for p in [m.PUBLIC,m.REVIEW,m.SOURCE]:p.mkdir(parents=True,exist_ok=True)
    annual=[];stations=[];initial=[];projects=[];fees=[];normals=[];balances=[];proofs=[];sources=[];rates=[]
    for region,rname in m.REGIONS.items():
        for baseline,bname in m.BASELINES.items():
            inp,scenes,root=m.prepare(region,baseline);lp=m.OperatingLP(inp);ids=list(inp['stations'])
            evidence=m.old.old.station_evidence(inp);names={r['station']:r['name'] or r['station'] for r in evidence}
            initial.append(dict(地区=rname,起点=bname,基期年份=2021,固定容量_MVA=inp['initial_capacity_mva'],
                基期负荷_MW=inp['initial_peak_mw'],基期容载比=inp['initial_capacity_mva']/inp['initial_peak_mw'],
                设备说明='原共同仿真设备' if baseline=='compressed' else '地区总量为2021原表；逐站组合继承已冻结比例标定'))
            for r in evidence:
                for y in inp['years']:rates.append(dict(地区=rname,起点=bname,年份=y,站号=r['station'],站名=names[r['station']],
                    原表J_MW=r['transferable_mw'],原表K_MW=r['unserved_mw'],逐站转供率=inp['station_transfer_rates'][r['station']],
                    当年既有转出上限_MW=inp['existing_transfer_budget_by_year_mw'][str(y)][r['station']],来源行=r['source_row'],匹配=r['matched']))
            for case,cname in m.CASES.items():
                label=dict(地区=rname,起点=bname,方案=cname);folder=m.best(region,baseline,case)
                annual.append(annual_record(label,2021,inp['initial_peak_mw'],inp['initial_capacity_mva'],status='固定基期',
                    当年新购主变_MVA=0.,当年净增容量_MVA=0.,当年新增储能_MWh=0.,年末储能_MWh=0.,
                    储能正向有效功率_MW=0.,当年新增联络_条=0,累计新增联络_条=0))
                if folder is None:
                    assert region=='pizhou' and baseline=='annual_2021' and case=='rigid'
                    solver=json.loads((root/'rigid_main/iteration_01_solver.json').read_text());assert solver['proven_infeasible']
                    fees.append(dict(**label,状态='该起点标定下不可行',费用现值_万元=None,费用下界_万元=None,相对间隙=None))
                    sources.append(dict(region=region,baseline=baseline,case=case,feasible=False,input_sha256=m.old.sha(root/'inputs.json')))
                    for y in inp['years']:annual.append(annual_record(label,y,inp['annual_observed_peak_mw'][str(y)],status='不可行'))
                    continue
                summary=json.loads((folder/'summary.json').read_text());assert not summary['selection_conditions']
                source=dict(region=region,baseline=baseline,case=case,feasible=True,folder=str(folder.relative_to(m.ROOT)),input_sha256=m.old.sha(root/'inputs.json'))
                for name in ['chosen_solution.npz','selected_pairs.json','stations.csv','projects.csv','normal_fractions.json','summary.json']:source[name]=m.old.sha(folder/name)
                sources.append(source)
                fees.append(dict(**label,状态='可行',费用现值_万元=summary['cost_npv_10k'],费用下界_万元=summary['solver']['dual_bound'],相对间隙=summary['solver']['mip_gap']))
                fractions=json.loads((folder/'normal_fractions.json').read_text());states={};built_by_year={};previous=inp['initial_capacity_mva']
                for a in summary['annual']:
                    y=a['year'];u,n,built=m.old.old.assets_from_csv(inp,folder,y);states[y]=(u,n);built_by_year[y]=built
                    ff={(r['edge'],r['direction']):r['fraction'] for r in fractions if r['year']==y}
                    coefficient=np.array([min(.1,.215*.76/max(1,inp['stations'][sid]['forward_duration_h'])) for sid in ids])
                    annual.append(annual_record(label,y,a['peak_mw'],a['capacity_mva'],当年新购主变_MVA=a['purchased_transformer_mva'],
                        当年净增容量_MVA=a['capacity_mva']-previous,当年新增储能_MWh=a['new_storage_mwh'],年末储能_MWh=a['storage_mwh'],
                        储能正向有效功率_MW=float((coefficient*n).sum()),当年新增联络_条=a['new_lines'],累计新增联络_条=a['cumulative_lines'],
                        主变费用现值_万元=a['transformer_npv_10k'],储能费用现值_万元=a['storage_npv_10k'],联络费用现值_万元=a['line_npv_10k']))
                    previous=a['capacity_mva']
                    for j,sid in enumerate(ids):stations.append(dict(**label,年份=y,站号=sid,站名=names[sid],
                        主变组合=' + '.join(f'{v:g}' for v in u[j] if v),主变_MVA=float(u[j].sum()),储能_MWh=float(n[j]*.215),
                        本站N1主变有功能力_MW=float(.95*(u[j].sum()-u[j].max()))))
                    normal=full_normal(region,inp,y,lp,u,n,built,ff);assert normal['verified'],(label,normal)
                    normals.append(dict(**label,**normal))
                    for h,p in enumerate(scenes[y]):
                        prepared=lp.prepared(p,y,u,n,built)
                        for f in range(-1,len(ids)):
                            dispatch=lp.dispatch_fixed(p,prepared,f,ff);assert dispatch.get('verified',True)
                            outgoing=np.zeros(len(ids));incoming=np.zeros(len(ids))
                            for arc,v in dispatch['flow']:
                                *_,sa,sb=lp.arcs[arc];outgoing[sa]+=v;incoming[sb]+=v
                            served=p-outgoing+incoming;cap=.95*u.sum(axis=1);rev=.8*cap
                            if f>=0:cap[f]-=.95*u[f].max();rev[f]=cap[f]
                            discharge=np.maximum(served-cap,0.);charge=np.maximum(-served-rev,0.)
                            forward=coefficient*n if f>=0 else np.zeros(len(ids))
                            reverse=np.array([min(.1,.215*.76/max(1,inp['stations'][sid]['reverse_duration_h'])) for sid in ids])*n if f>=0 else np.zeros(len(ids))
                            assert max(np.max(discharge-forward),np.max(charge-reverse))<1e-5 and abs(served.sum()-p.sum())<1e-7
                            proofs.append(dict(region=region,baseline=baseline,case=case,year=y,scenario=h,failed=f,verified=True,
                                transfer_mw=dispatch['total_mw'],existing_mw=dispatch['existing_mw']))
                            if f<0 or h in (int(np.argmax(scenes[y][:,max(0,f)])),int(np.argmin(scenes[y][:,max(0,f)]))):
                                for j,sid in enumerate(ids):balances.append(dict(**label,年份=y,截面=h,故障站='正常' if f<0 else names[ids[f]],站名=names[sid],
                                    原净负荷_MW=float(p[j]),转出_MW=float(outgoing[j]),转入_MW=float(incoming[j]),转接后净负荷_MW=float(served[j]),
                                    正向主变限值_MW=float(cap[j]),反向主变限值_MW=float(rev[j]),所需放电_MW=float(discharge[j]),所需充电_MW=float(charge[j])))
                    print('EXPORT_TWO_DISTRICTS',region,baseline,case,y,flush=True)
                for row in m.old.old.base.previous.rows(folder/'projects.csv'):projects.append(dict(**label,**row))
                assert abs(cost(inp,states,built_by_year)-summary['cost_npv_10k'])<1e-4
    no_solution=infeasible_certificate()
    notes=pd.DataFrame([dict(事项='采用方案',说明='弹性经济参考作为主方案；两方案均按费用目标选配，刚性保留2.0扩容控制，弹性采用共同安全条件'),
        dict(事项='时间',说明='2021为固定共同基期，首期优化为2022，2021行不含新增建设；2022—2025沿用实际年度负荷'),
        dict(事项='两种起点',说明='主组保留邳州1463.50、市区2900 MVA；补充组保留2021原表2027、3113.50 MVA地区总量，逐站组合为已冻结标定'),
        dict(事项='共同运行',说明='正常按年固定通道比例，不调用事故备用储能；事故仅故障站直接相连通道转接。正常及健康站反向80%，最大单台退出校核剩余主变'),
        dict(事项='储能',说明='邳州正向支撑2h，市区6h，额定功率及76%可用能量共同限制，假定事故前备用能量可用'),
        dict(事项='无解',说明='邳州原表起点刚性容量受2027 MVA上限且各站设备非减，无法补强邢楼的正常反向缺口；单列不可行结果及独立放宽网络的证据'),
        dict(事项='来源范围',说明='既有等效通道继承2025收资标定。部分站级设备及源荷为空缺条件下的研究设置；保留原表总量不等同完整2021逐台历史复原'),
        dict(事项='校核范围',说明='静态正常/N-1及补齐8760正常净负荷、固定通道比例校核；未计算全年SOC、新能源利用率、完整电压及上级反送接纳')])
    frames={'建模说明':notes,'固定2021起点':pd.DataFrame(initial),'逐年方案':pd.DataFrame(annual),'费用及精度':pd.DataFrame(fees),
        '逐站设备':pd.DataFrame(stations),'逐站转供设置':pd.DataFrame(rates),'联络项目':pd.DataFrame(projects),
        '正常8760核验':pd.DataFrame(normals),'典型工况功率收支':pd.DataFrame(balances),'不可行原因':pd.DataFrame(no_solution)}
    workbook(m.PUBLIC/'两区县逐年经济方案.xlsx',frames)
    for name,frame in frames.items():frame.to_csv(m.PUBLIC/(name+'.csv'),index=False,encoding='utf-8-sig')
    m.old.dump(m.REVIEW/'两区县独立运行核验.json',dict(verified=True,sources=sources,static_pairs=len(proofs),
        normal_station_hours=sum(r['station_hours'] for r in normals),normal_checks=normals,dispatch_records=proofs))
    return frames


if __name__=='__main__':generate()
