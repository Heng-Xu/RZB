"""设备与MW支撑分解、站级收支和补齐8760小时正常方式核验。"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ..review_20261015 import export as previous_export
from . import cases as c

LABEL={'normal_fixed':'正常供区固定','standby':'固定供区及储能备用','local_standby':'固定供区及直接事故转接',
       'transfer80':'既有转供按80%可用','transfer60':'既有转供按60%可用','station_floor':'逐站容量不退减替代对照'}


def selected():
    records=[];root=c.prior.OUT/'pizhou/compressed_reverse80'
    for case in ('rigid','elastic_free','elastic_target'):
        records.append(dict(policy='previous',case=case,folder=c.prior.best_folder(root,case)))
    for policy in c.POLICIES:
        for case in ('rigid','elastic_free'):
            folder=c.best(policy,case)
            if folder:records.append(dict(policy=policy,case=case,folder=folder))
    return records


def full_normal(inp,units,year):
    path=c.ROOT/'研究报告/数据来源/当前版/区域时序/pizhou_stations.npz';z=np.load(path)
    ids=list(inp['stations']);order=[list(z['station_ids']).index(s) for s in ids]
    raw=z['power_mw'][:,order];power=raw*inp['annual_observed_peak_mw'][str(year)]/raw.sum(axis=1).max()
    capacity=.95*units.sum(axis=1);reverse=.8*capacity
    violation=float(max(0.,np.max(power-capacity),np.max(-power-reverse)))
    return dict(小时数=len(power),站点数=len(ids),补值站时数=int((~z['observed'][:,order]).sum()),
        正向峰值_MW=float(power.sum(axis=1).max()),反向峰值_MW=float(-power.sum(axis=1).min()),
        正常无储能无转供最大越限_MW=violation,正常无储能无转供通过=violation<1e-6,
        样本SHA256=c.prior.sha(path),口径='补齐8760小时净负荷，按原年度规划峰值统一缩放；未优化SOC、未计算新能源利用率')


def main():
    for p in (c.PUBLIC,c.REVIEW,c.SOURCE):p.mkdir(parents=True,exist_ok=True)
    annual=[];station=[];fees=[];normal=[];balances=[];sources=[];checks=[]
    names={r['station']:r['name'] for r in c.prior.old.station_evidence(json.loads((c.prior.OUT/'pizhou/compressed_reverse80/inputs.json').read_text()))}
    for chosen in selected():
        folder=chosen['folder'];summary=json.loads((folder/'summary.json').read_text());inp=json.loads((folder.parent/'inputs.json').read_text())
        policy=chosen['policy'];case=chosen['case'];label=LABEL.get(policy,'上一轮')
        scenes=c.prior.old.base.load_scenes(c.prior.old.base.OUT/'pizhou',inp)
        lp=c.prior.StationLP(inp) if policy=='previous' else c.OperatingLP(inp)
        sources.append(dict(policy=policy,case=case,folder=str(folder.relative_to(c.ROOT)),
            input_sha256=c.prior.sha(folder.parent/'inputs.json'),solution_sha256=c.prior.sha(folder/'chosen_solution.npz')))
        fees.append(dict(运行条件=label,方案=previous_export.CASE[case],费用现值_万元=summary['cost_npv_10k'],
            费用下界_万元=summary['solver']['dual_bound'],相对间隙=summary['solver']['mip_gap'],原始目录=str(folder.relative_to(c.ROOT))))
        for a in summary['annual']:
            y=a['year'];units,n,built=c.prior.old.assets_from_csv(inp,folder,y);ids=list(inp['stations'])
            bp=np.array([min(.1,.215*.76/max(1,inp['stations'][s]['forward_duration_h'])) for s in ids])*n
            bn=np.array([min(.1,.215*.76/max(1,inp['stations'][s]['reverse_duration_h'])) for s in ids])*n
            annual.append(dict(运行条件=label,方案=previous_export.CASE[case],年份=y,年末主变_MVA=float(units.sum()),
                容载比=a['clr'],年末储能_MWh=float(n.sum()*.215),正向有效储能_MW=float(bp.sum()),
                反向有效储能_MW=float(bn.sum()),累计新增联络_条=len(built),当年新增联络_条=a['new_lines'],
                主变正常有功能力_MW=float(.95*units.sum()),
                各站N1剩余容量之和_MVA=float((units.sum(axis=1)-units.max(axis=1)).sum())))
            for j,sid in enumerate(ids):
                station.append(dict(运行条件=label,方案=previous_export.CASE[case],年份=y,站号=sid,站名=names[sid],
                    主变组合=' + '.join(f'{r:g}' for r in units[j] if r),主变_MVA=float(units[j].sum()),
                    本站N1有功能力_MW=float(.95*(units[j].sum()-units[j].max())),
                    储能_MWh=float(n[j]*.215),正向有效储能_MW=float(bp[j]),反向有效储能_MW=float(bn[j])))
            if inp.get('followup_options',{}).get('reserve_only'):
                r=full_normal(inp,units,y);assert r['正常无储能无转供通过']
                normal.append(dict(运行条件=label,方案=previous_export.CASE[case],年份=y,**r))
            # 每站正、反向局部极值下最大单台停运及正常模式，逐站列出功率收支。
            critical={(int(np.argmax(scenes[y][:,j])),j) for j in range(len(ids))}
            critical|={(int(np.argmin(scenes[y][:,j])),j) for j in range(len(ids))}
            critical|={(h,-1) for h in {int(np.argmax(scenes[y].sum(axis=1))),int(np.argmin(scenes[y].sum(axis=1)))}}
            for h,f in sorted(critical):
                p=scenes[y][h];prepared=lp.prepared(p,y,units,n,built);dispatch=lp.dispatch(p,prepared,f)
                out=np.zeros(len(ids));incoming=np.zeros(len(ids))
                for arc,value in dispatch['flow']:
                    *_,sa,sb=lp.arcs[arc];out[sa]+=value;incoming[sb]+=value
                served=p-out+incoming;available=.95*units.sum(axis=1)
                if f>=0:available[f]-=.95*units[f].max()
                reverse=.8*.95*units.sum(axis=1)
                if f>=0:reverse[f]=available[f]
                discharge=np.maximum(served-available,0.);charge=np.maximum(-served-reverse,0.)
                assert abs(served.sum()-p.sum())<1e-7
                reserve_normal=f<0 and inp.get('followup_options',{}).get('reserve_only')
                assert np.max(discharge-(0. if reserve_normal else bp))<1e-5
                assert np.max(charge-(0. if reserve_normal else bn))<1e-5
                for j,sid in enumerate(ids):
                    balances.append(dict(运行条件=label,方案=previous_export.CASE[case],年份=y,截面=h,
                        原始小时=inp['station_snapshot_roles'][h]['source_hour'],故障站=ids[f] if f>=0 else '正常',
                        站名=names[sid],站号=sid,原净负荷_MW=float(p[j]),转出_MW=float(out[j]),转入_MW=float(incoming[j]),
                        转接后净负荷_MW=float(served[j]),正向主变限值_MW=float(available[j]),
                        反向主变限值_MW=float(reverse[j]),所需放电_MW=float(discharge[j]),所需充电_MW=float(charge[j]),
                        储能正向上限_MW=float(bp[j]) if f>=0 or not inp.get('followup_options',{}).get('reserve_only') else 0.,
                        储能反向上限_MW=float(bn[j]) if f>=0 or not inp.get('followup_options',{}).get('reserve_only') else 0.))
            checks.append(dict(policy=policy,case=case,year=y,verified=True,critical_pairs=len(critical)))
        print('AUDITED_FOLLOWUP',policy,case,flush=True)
    frames={'逐年方案及有效功率':pd.DataFrame(annual),'逐站设备及有效功率':pd.DataFrame(station),
        '费用及精度':pd.DataFrame(fees),'8760正常方式':pd.DataFrame(normal),'典型工况逐站收支':pd.DataFrame(balances)}
    for name,df in frames.items():df.to_csv(c.PUBLIC/(name+'.csv'),index=False,encoding='utf-8-sig')
    notes=pd.DataFrame([dict(事项='容量和功率',定义='主变容量MVA按功率因数0.95折算MW；储能有效功率同时受额定MW及76%可用能量/支撑时长约束'),
        dict(事项='N1剩余容量汇总',定义='各站分别停最大一台的剩余容量之和，用于配置比较；同一事故只停一站一台，按具体工况表校核'),
        dict(事项='固定供区及储能备用',定义='正常站间转供为零，正常充放电支撑为零；事故仍受原有通道、馈线、逐站额度及接收主变限制'),
        dict(事项='直接事故转接',定义='在备用条件上，事故仅开放故障站与直接相连站之间的通道，为共同运行策略对照'),
        dict(事项='转供80%',定义='原逐站可用上限乘80%的研究裕度敏感性；不是标准规定的转供率或已核实事故可用能力'),
        dict(事项='逐站不退减',定义='以所列刚性建设方案各站逐年总容量为下限的投资替代对照，须具备既定主变计划这一前提，不作为自由寻优结果')])
    previous_export.workbook(c.PUBLIC/'邳州运行约束深化对照.xlsx',{'说明':notes,**frames})
    c.prior.dump(c.REVIEW/'案例收支及8760核验.json',dict(verified=True,sources=sources,critical_cases=checks,
        normal_8760=normal,case_count=len(sources)))
    print('AUDITED_FOLLOWUP_ALL',len(sources),sum(r['小时数']*r['站点数'] for r in normal),flush=True)


if __name__=='__main__':main()
