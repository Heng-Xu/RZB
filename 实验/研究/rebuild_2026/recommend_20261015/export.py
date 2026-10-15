"""最终逐年方案、站间收支及正常8760小时复核。"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ..review_20261015 import export as old_export
from ..review_20261015.target_warm import cost
from . import model as m

LABEL={'rigid':'刚性方案','elastic_free':'弹性经济参考','elastic_selected':'弹性增容替代方案'}


def full_normal(inp,folder,year,lp,units,n,built,fractions):
    z=np.load(m.ROOT/'研究报告/数据来源/当前版/区域时序/pizhou_stations.npz');ids=list(inp['stations'])
    order=[list(z['station_ids']).index(s) for s in ids];raw=z['power_mw'][:,order]
    profile=raw*inp['annual_observed_peak_mw'][str(year)]/raw.sum(axis=1).max()
    station_out=np.zeros_like(profile);station_in=np.zeros_like(profile);edge_use={}
    for arc in lp.arcs:
        k,e,d,a,b,sa,sb=arc;value=fractions.get((e['id'],d),0.)*np.maximum(profile[:,sa],0.)
        station_out[:,sa]+=value;station_in[:,sb]+=value
        edge_use[e['id']]=edge_use.get(e['id'],0.)+value
    served=profile-station_out+station_in;full=.95*units.sum(axis=1)
    violations=np.maximum(np.maximum(served-full,-served-.8*full),0.)
    assert abs((served-profile).sum(axis=1)).max()<1e-7
    # 正常方式比例全为零时，静态各站极值覆盖8760容量约束且通道不用；
    # 非零方案逐时以原馈线、通道和接收约束核查固定调度。
    worst=float(violations.max());bad=[]
    if any(v>1e-9 for v in fractions.values()):
        for h,p in enumerate(profile):
            r=lp.dispatch_fixed(p,lp.prepared(p,year,units,n,built),-1,fractions)
            if not r['verified']:bad.append(dict(hour=h,violation_mw=r['max_violation_mw']))
            worst=max(worst,r['max_violation_mw'])
    else:
        bad=[dict(hour=int(h),violation_mw=float(violations[h].max())) for h in np.flatnonzero(violations.max(axis=1)>1e-5)]
    return dict(year=year,hours=len(profile),station_hours=len(profile)*len(ids),
        max_normal_transfer_mw=float(station_out.sum(axis=1).max()),max_violation_mw=worst,
        violating_hours=len(bad),verified=not bad,failures=bad[:20],filled_station_hours=int((~z['observed'][:,order]).sum()))


def generate():
    for p in (m.PUBLIC,m.REVIEW,m.SOURCE):p.mkdir(parents=True,exist_ok=True)
    inp,scenes,root=m.prepare();lp=m.OperatingLP(inp);ids=list(inp['stations'])
    names={r['station']:r['name'] for r in m.old.old.station_evidence(inp)}
    annual=[];station=[];projects=[];fees=[];balances=[];normal=[];proofs=[];sources=[]
    for case in LABEL:
        folder=m.best(case)
        if folder is None:continue
        summary=json.loads((folder/'summary.json').read_text());states={};built_by_year={}
        fractions=json.loads((folder/'normal_fractions.json').read_text())
        fractions_by_year={y:{(r['edge'],r['direction']):r['fraction'] for r in fractions if r['year']==y} for y in inp['years']}
        sources.append(dict(case=case,folder=str(folder.relative_to(m.ROOT)),input_sha256=m.old.sha(root/'inputs.json'),
            solution_sha256=m.old.sha(folder/'chosen_solution.npz'),stations_sha256=m.old.sha(folder/'stations.csv'),
            projects_sha256=m.old.sha(folder/'projects.csv'),normal_fractions_sha256=m.old.sha(folder/'normal_fractions.json')))
        fees.append(dict(方案=LABEL[case],费用现值_万元=summary['cost_npv_10k'],费用下界_万元=summary['solver']['dual_bound'],
            相对间隙=summary['solver']['mip_gap'],选择条件=json.dumps(summary['selection_conditions'],ensure_ascii=False)))
        for a in summary['annual']:
            y=a['year'];units,n,built=m.old.old.assets_from_csv(inp,folder,y);states[y]=(units,n);built_by_year[y]=built
            annual.append(dict(方案=LABEL[case],年份=y,规划负荷_MW=a['peak_mw'],年末主变_MVA=a['capacity_mva'],容载比=a['clr'],
                当年新购主变_MVA=a['purchased_transformer_mva'],当年净增容量_MVA=a['capacity_mva']-(inp['initial_capacity_mva'] if y==inp['years'][0] else summary['annual'][inp['years'].index(y)-1]['capacity_mva']),
                当年新增储能_MWh=a['new_storage_mwh'],年末储能_MWh=a['storage_mwh'],年末储能额定功率_MW=a['storage_nameplate_mw'],
                年末储能正向有效功率_MW=float(n.sum()*.215*.76/2),当年新增联络_条=a['new_lines'],累计新增联络_条=a['cumulative_lines'],
                主变费用现值_万元=a['transformer_npv_10k'],储能费用现值_万元=a['storage_npv_10k'],联络费用现值_万元=a['line_npv_10k']))
            oldunits=np.array([s['initial_units']+[0.] for s in inp['stations'].values()]) if y==inp['years'][0] else states[y-1][0]
            for j,sid in enumerate(ids):
                station.append(dict(方案=LABEL[case],年份=y,站号=sid,站名=names[sid],主变组合=' + '.join(f'{v:g}' for v in units[j] if v),
                    主变_MVA=float(units[j].sum()),储能_MWh=float(n[j]*.215),本站N1主变有功能力_MW=float(.95*(units[j].sum()-units[j].max())),
                    既有转供率=inp['station_transfer_rates'][sid],当年既有转出上限_MW=inp['existing_transfer_budget_by_year_mw'][str(y)][sid]))
            norm=full_normal(inp,folder,y,lp,units,n,built,fractions_by_year[y]);normal.append(dict(case=case,**norm))
            assert norm['verified'],(case,y,norm)
            for h,p in enumerate(scenes[y]):
                prepared=lp.prepared(p,y,units,n,built)
                for f in range(-1,len(ids)):
                    dispatch=lp.dispatch_fixed(p,prepared,f,fractions_by_year[y])
                    assert dispatch.get('verified',True)
                    flow=dispatch['flow'];out=np.zeros(len(ids));incoming=np.zeros(len(ids))
                    for arc,v in flow:
                        *_,sa,sb=lp.arcs[arc];out[sa]+=v;incoming[sb]+=v
                    served=p-out+incoming;capacity=.95*units.sum(axis=1);reverse=.8*capacity
                    if f>=0:capacity[f]-=.95*units[f].max();reverse[f]=capacity[f]
                    discharge=np.maximum(served-capacity,0.);charge=np.maximum(-served-reverse,0.)
                    allowed_forward=n*.215*.76/2 if f>=0 else np.zeros(len(ids))
                    allowed_reverse=np.array([min(.1,.215*.76/max(1,inp['stations'][s]['reverse_duration_h'])) for s in ids])*n if f>=0 else np.zeros(len(ids))
                    assert np.max(discharge-allowed_forward)<1e-5 and np.max(charge-allowed_reverse)<1e-5
                    assert abs(served.sum()-p.sum())<1e-7
                    proofs.append(dict(case=case,year=y,scenario=h,failed=f,transfer_mw=float(out.sum()),
                        existing_mw=dispatch['existing_mw'],verified=True))
                    if f<0 or h in (int(np.argmax(scenes[y][:,max(0,f)])),int(np.argmin(scenes[y][:,max(0,f)]))):
                        for j,sid in enumerate(ids):balances.append(dict(方案=LABEL[case],年份=y,截面=h,故障站='正常' if f<0 else names[ids[f]],
                            站名=names[sid],原净负荷_MW=float(p[j]),转出_MW=float(out[j]),转入_MW=float(incoming[j]),转接后净负荷_MW=float(served[j]),
                            正向主变限值_MW=float(capacity[j]),反向主变限值_MW=float(reverse[j]),所需放电_MW=float(discharge[j]),所需充电_MW=float(charge[j])))
            for r in m.old.old.base.previous.rows(folder/'projects.csv'):
                if int(r['year'])==y:projects.append(dict(方案=LABEL[case],**r))
            print('EXPORT_RECOMMEND',case,y,flush=True)
        assert abs(cost(inp,states,built_by_year)-summary['cost_npv_10k'])<1e-4
    frames={'逐年推荐结果':pd.DataFrame(annual),'逐站设备':pd.DataFrame(station),'联络项目':pd.DataFrame(projects),
        '费用及条件':pd.DataFrame(fees),'正常8760核验':pd.DataFrame(normal),'典型工况功率收支':pd.DataFrame(balances)}
    notes=pd.DataFrame([dict(事项='主比较',说明='相同年度负荷、逐站既有上限及网络；正常按年固定转供比例，不使用备用储能；事故仅直接相连通道转接'),
        dict(事项='增容替代偏好',说明='弹性各年容量至少为刚性105%，储能不超过刚性50%，联络累计不多于刚性、末年至少少2条；是规划选择条件'),
        dict(事项='转供范围',说明='既有上限来自J/(J+K)和J；76条等效通道继承原网络，属于研究聚合路径；新增候选绑定馈线/站端，实际路线待核'),
        dict(事项='正常供区',说明='同一年每条通道按送端正向净负荷固定比例转接，是规划比例代理，未声称逐区段开关方式已校核'),
        dict(事项='结果边界',说明='静态正反向/N-1、8760正常净负荷容量及网络约束校核；未计算全年新能源利用率、上级反送接纳及电压')])
    old_export.workbook(m.PUBLIC/'邳州逐年推荐方案.xlsx',{'说明':notes,**frames})
    for name,df in frames.items():df.to_csv(m.PUBLIC/(name+'.csv'),index=False,encoding='utf-8-sig')
    m.old.dump(m.REVIEW/'推荐方案独立核验.json',dict(verified=True,sources=sources,static_pairs=len(proofs),
        normal_station_hours=sum(r['station_hours'] for r in normal),normal_checks=normal,dispatch_records=proofs))
    return frames


if __name__=='__main__':generate()
