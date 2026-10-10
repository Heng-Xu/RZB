"""固定源荷/价格，隔离核查实体候选连接和共享馈线余量的影响。

同网格只作为新建候选证据，不作为已建连通证据。已知T01路径之外的
既有网络余量不外推；结果是资料覆盖条件下的保守案例，不是全县竣工规划。
储能先沿用P/E持续时间代理，另做连续时序复核，不冒称静态代理已满足SOC。
"""
import argparse
import csv
import json
import math
from collections import defaultdict

import numpy as np
from openpyxl import load_workbook
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow

from ..pilot_20261009.run import ROOT, PF, CASES, dump, write_csv, sha, solve_model
from ..synchronous_20261009 import model as previous
from ..synchronous_20261009.prepare import OUT as PREVIOUS
from ..station_grid_feasibility import FEEDERS, grid_candidate_rows
from ..tie_section_audit import transferable_section

OUT=ROOT/'研究报告/试算/20261010_网络约束案例'
SCALE=10**5  # scipy最大流内部32位流量，需保留全区需求总量的溢出余量。
NETWORK_TOLERANCE_MW=.001  # 各边1e-5MW量化累计误差，远小于0.1MW设备粒度。


def case_root(width=1,new_feeders=False,usable=1.):
    return OUT/('pizhou_soc_reserve' if usable<1 else ('pizhou_new_feeders' if new_feeders else ('pizhou' if width==1 else 'pizhou_expanded')))


def prepare(width=1,new_feeders=False,usable=1.):
    root=case_root(width,new_feeders,usable);root.mkdir(parents=True,exist_ok=True)
    inp=json.loads((PREVIOUS/'pizhou/inputs.json').read_text())
    ids=list(inp['stations']);feeders={}
    w=load_workbook(FEEDERS,read_only=True,data_only=True)
    for nr,row in enumerate(w.worksheets[0].iter_rows(min_row=2,values_only=True),2):
        if row[12] not in ids or not row[1]:continue
        if not isinstance(row[7],(int,float)) or row[7]<=0:continue
        if not isinstance(row[8],(int,float)) or row[8]<0:continue
        feeders[row[1]]={'id':row[1],'station':row[12],'grid':row[4],
                        'thermal_mw':math.sqrt(3)*10*PF*row[7]/1000,
                        'maximum_load_proxy_2025_mw':math.sqrt(3)*10*PF*row[8]/1000,
                        'source_row':nr,'source_reported_active_mw':row[9]}
    w.close()
    candidates=grid_candidate_rows(set(ids));edges=[];seen=set()
    # 每个站—网格按允许电流排序，保留至多width组匹配作为首轮候选；完整馈线表也输出，
    # 便于随后扩展候选集，不能宣称已遍历全部馈线接法。
    for row in candidates:
        pools=[[f for f in row[k].split('|') if f in feeders] for k in ('station_a_feeders','station_b_feeders')]
        if not all(pools):continue
        pools=[sorted(pool,key=lambda f:(feeders[f]['thermal_mw'],-feeders[f]['maximum_load_proxy_2025_mw'],f),reverse=True)[:width] for pool in pools]
        for k in range(max(map(len,pools))):
            a,b=[pool[k%len(pool)] for pool in pools]
            if (a,b) in seen:continue
            seen.add((a,b))
            edges.append({'id':f'NEW-{len(edges)+1:03d}','a':a,'b':b,'station_a':feeders[a]['station'],
                          'station_b':feeders[b]['station'],'capacity_mw':inp['line_increment_mw'],
                          'existing':False,'grid':row['shared_grid'],'source_section_fraction':1.,
                          'bidirectional':True,'route_length_km_assumption':3.,
                          'basis':'同网格、指定既有馈线端点的新建联络候选；路径与可切负荷块尚未闭合'})
    source_feeder_count=len(feeders)
    if new_feeders:
        # 同网格中的既有负荷馈线可接至邻站新出线；新出线单独占用受站间隔，
        # 不再挤占受站已有馈线的2—3MW余量。源端仍受同一既有馈线负荷块上限。
        new_seen=set()
        for row in candidates:
            for source_side,target_side in (('a','b'),('b','a')):
                receiver=row[f'station_{target_side}']
                if inp['stations'][receiver]['metadata']['spare_10kv_bays']<=0:continue
                pool=[f for f in row[f'station_{source_side}_feeders'].split('|') if f in feeders]
                pool=sorted(pool,key=lambda f:feeders[f]['maximum_load_proxy_2025_mw'],reverse=True)[:2]
                for f in pool:
                    if (f,receiver) in new_seen:continue
                    new_seen.add((f,receiver));eid=f'FEEDER-{len(new_seen):03d}';nf='SIM-'+eid
                    feeders[nf]={'id':nf,'station':receiver,'grid':row['shared_grid'],
                                 'thermal_mw':inp['line_increment_mw'],'maximum_load_proxy_2025_mw':0.,
                                 'source_row':'planning_new_feeder','source_reported_active_mw':0.}
                    edges.append({'id':eid,'a':f,'b':nf,'station_a':feeders[f]['station'],'station_b':receiver,
                                  'capacity_mw':inp['line_increment_mw'],'existing':False,'grid':row['shared_grid'],
                                  'source_section_fraction':1.,'bidirectional':False,'route_length_km_assumption':3.,
                                  'basis':'同网格既有馈线负荷接邻站新出线，源端区段待核；新出线占受站备用间隔',
                                  'new_bay_station':receiver})
    # CSV统一字段；已有馈线之间联络不占新的站内出线间隔。
    for edge in edges:edge.setdefault('new_bay_station','')
    section=transferable_section()
    edges.insert(0,{'id':'T01','a':'PZXL-00092','b':'PZXL-00161',
                    'station_a':feeders['PZXL-00092']['station'],'station_b':feeders['PZXL-00161']['station'],
                    'capacity_mw':4.75,'existing':True,'grid':'known_section',
                    'source_section_fraction':section['2025_feeder_stress_section_p_seed_mw']/section['2025_feeder_stress_total_p_seed_mw'],
                    'bidirectional':False,'route_length_km_assumption':0.,'new_bay_station':'',
                    'basis':'已闭合的墩南28开关下游区段至河炮接收路径，按核实方向使用；负荷为节点种子代理'})
    used={e[k] for e in edges for k in ('a','b')}
    inp.update(network={'feeders':{f:feeders[f] for f in sorted(used)},'edges':edges,
                        'source_file':str(FEEDERS.relative_to(ROOT)),'source_sha256':sha(FEEDERS),
                        'all_source_feeder_count':source_feeder_count,'shared_grid_rows':len(candidates),
                        'shared_grid_unique_station_pairs':len({(r['station_a'],r['station_b']) for r in candidates}),
                        'known_existing_only':True,'section':section,'candidate_width':width,'allow_new_receiving_feeders':new_feeders},
               scope='邳州20站，指定馈线端点、共享余量、付费新建候选；相同净负荷与造价的网络约束隔离案例',
               storage_usable_energy_fraction=usable,
               storage_basis='静态有效功率min(0.1MW,0.215MWh×可用电量系数/持续时间)；可用系数0.76为80%SOC窗口×95%单向效率；连续SOC另查',
               line_basis='已有馈线互联不占新间隔；新出线只占受站间隔。每条候选均计原3km及6万元端部设备参考价；未另取得站内间隔改造报价，须作追加费用敏感性；路线待勘测',
               initial_transfer_fraction_usage='28%保留为六馈线样本指标，不生成全县免费转供能力')
    dump(root/'inputs.json',inp)
    (root/'hourly.npz').write_bytes((PREVIOUS/'pizhou/hourly.npz').read_bytes())
    write_csv(root/'全部馈线源数据.csv',list(feeders.values()))
    write_csv(root/'网络候选.csv',edges)
    write_csv(root/'同网格证据.csv',candidates)
    print('PREPARED',len(feeders),'feeders',len(edges)-1,'paid candidates',flush=True)


def limits(inp,p,y):
    """出端采用同期站负荷缩放的馈线代理；入端采用当年峰值电流代理余量。

    接收余量按各馈线自身峰值计算，具有保守性；不能当作同期实测余量。
    """
    ids=list(inp['stations']);station_index={sid:j for j,sid in enumerate(ids)}
    g=inp['growth_rate'];annual=(1+g)**(y-2025)
    donor={};receive={}
    for f,row in inp['network']['feeders'].items():
        sid=row['station'];j=station_index[sid]
        peak2025=inp['stations'][sid]['base_forward_mw']*(1+g)**4
        donor[f]=row['maximum_load_proxy_2025_mw']*max(0,float(p[j]))/peak2025
        receive[f]=max(0,row['thermal_mw']-row['maximum_load_proxy_2025_mw']*annual)
    return donor,receive


def storage_power(inp,n):
    usable=inp.get('storage_usable_energy_fraction',1.)
    return tuple(np.array([min(.1,.215*usable/max(1,s[key])) for s in inp['stations'].values()])*n
                 for key in ('forward_duration_h','reverse_duration_h'))


def add_network_scene(m,inp,p,y,failed,caps,modules,edgevars,flowmeta):
    ids=list(inp['stations']);idx={s:j for j,s in enumerate(ids)}
    donor,receive=limits(inp,p,y)
    outgoing=defaultdict(dict);incoming=defaultdict(dict);station_out=defaultdict(dict);net=defaultdict(dict)
    for edge in inp['network']['edges']:
        variables=[]
        for direction in range(2 if edge['bidirectional'] else 1):
            a,b=(edge['a'],edge['b']) if direction==0 else (edge['b'],edge['a'])
            sa=inp['network']['feeders'][a]['station'];sb=inp['network']['feeders'][b]['station']
            v=m.variable(0,upper=edge['capacity_mw'],integer=0);variables.append(v)
            outgoing[a][v]=1;incoming[b][v]=1;station_out[sa][v]=1
            net[sa][v]=1;net[sb][v]=-1
            if edge['existing']:m.constraint({v:1},upper=donor[a]*edge['source_section_fraction'])
            flowmeta.append((y,failed,edge['id'],direction,v))
        terms={v:1 for v in variables}
        if edge['existing']:m.constraint(terms,upper=edge['capacity_mw'])
        else:m.constraint({**terms,edgevars[edge['id'],y]:-edge['capacity_mw']},upper=0)
    for f in inp['network']['feeders']:
        m.constraint(outgoing[f],upper=donor[f]);m.constraint(incoming[f],upper=receive[f])
    for sid in ids:
        j=idx[sid];s=inp['stations'][sid]
        m.constraint(station_out[sid],upper=max(0,float(p[j])))
        for cap in caps[sid,y,failed]:
            for sign,duration in ((1,s['forward_duration_h']),(-1,s['reverse_duration_h'])):
                terms={v:PF*c for v,c in cap.items()}
                terms[modules[sid,y]]=min(.1,.215*inp.get('storage_usable_energy_fraction',1.)/max(1,duration))
                for v,c in net[sid].items():terms[v]=sign*c
                m.constraint(terms,lower=sign*float(p[j]))


def build(inp,power,selected,case):
    # 复用相同资产及费用约束，完全不创建旧的全区自由转供场景。
    m,meta=previous.build(inp,power,[],case)
    edgevars={};caps={};flowmeta=[]
    for y in inp['years']:
        for edge in inp['network']['edges']:
            if edge['existing']:continue
            v=m.variable(0);edgevars[edge['id'],y]=v
            if y>inp['years'][0]:m.constraint({v:1,edgevars[edge['id'],y-1]:-1},lower=0)
        m.constraint({meta['projects'][y]:1,**{edgevars[e['id'],y]:-1 for e in inp['network']['edges'] if not e['existing']}},0,0)
        for sid,s in inp['stations'].items():
            ends={edgevars[e['id'],y]:-1 for e in inp['network']['edges'] if not e['existing'] and sid in (e['station_a'],e['station_b'])}
            m.constraint({meta['ends'][sid,y]:1,**ends},0,0)
            bays={edgevars[e['id'],y]:1 for e in inp['network']['edges'] if e.get('new_bay_station')==sid}
            m.constraint(bays,upper=s['metadata']['spare_10kv_bays'])
            full={v:r for (ss,slot,yy,r),v in meta['x'].items() if ss==sid and yy==y}
            if (sid,y) in meta['third']:full[meta['third'][sid,y]]=50
            for failed in {f for h,f in selected}:
                variants=[full]
                if failed==list(inp['stations']).index(sid):
                    # 两台原主变按非减排序，最大原主变是slot1；第三台50可能更大。
                    # 对两种最大值分别约束；未建第三台时扣除50的约束不激活。
                    variants=[]
                    cap={v:r for (ss,slot,yy,r),v in meta['x'].items() if ss==sid and yy==y and slot!=1}
                    if (sid,y) in meta['third']:cap[meta['third'][sid,y]]=50
                    variants.append(cap)
                    # 第三台失效时，剩余两台之和总不小于slot0 + existing max;
                    # initial slot1>=50时无需另查；否则加一个等价线性剩余容量。
                    if s['allow_third'] and max(s['initial_units'])<50:
                        cap3={v:r for (ss,slot,yy,r),v in meta['x'].items() if ss==sid and yy==y}
                        # 加虚拟50*(1-third)使未建第三台时非限制。
                        # 通过固定1变量表达，不改变容量指标。
                        one=m.variable(0);m.lower_bounds[one]=1
                        cap3[one]=50;cap3[meta['third'][sid,y]]=-50
                        variants.append(cap3)
                caps[sid,y,failed]=variants
        for h,failed in selected:
            start=len(flowmeta)
            add_network_scene(m,inp,power[h]*(1+inp['growth_rate'])**(y-2021),y,failed,caps,meta['modules'],edgevars,flowmeta)
            flowmeta[start:]=[(y,h,f,e,d,v) for y,f,e,d,v in flowmeta[start:]]
    meta.update(edgevars=edgevars,network_flows=flowmeta)
    return m,meta


def circulation_check(n,arcs,lo,hi,return_witness=False):
    """带站净转出区间的网络环流；独立最大流核验，MW→1e-5MW整数。

    arcs = (from,to,capacity)。额外R→站边带下上界；负下界合法。
    最大流不足量为网络约束缺口；不是预计失负荷。
    """
    if np.min(hi-lo)<-1e-6:return float(np.max(lo-hi)),None
    R=n;S=n+1;T=n+2;dem=np.zeros(n+1);edges=list(arcs)
    for j,(l,u) in enumerate(zip(lo,hi)):
        edges.append((R,j,max(0,float(u-l))));dem[R]-=l;dem[j]+=l
    for j,b in enumerate(dem):
        if b>1e-9:edges.append((S,j,float(b)))
        elif b<-1e-9:edges.append((j,T,float(-b)))
    rows,cols,values=zip(*edges)
    graph=coo_matrix((np.rint(np.asarray(values)*SCALE).astype(np.int64),(rows,cols)),shape=(n+3,n+3)).tocsr()
    required=np.rint(np.maximum(dem,0)*SCALE).sum()
    assert required<2**31-1 and graph.max()<2**31-1,'最大流整数缩放溢出'
    result=maximum_flow(graph,S,T)
    gap=max(0,(required-result.flow_value)/SCALE)
    return float(gap),(result,graph) if return_witness else None


def network_arcs(inp,p,y,built):
    ids=list(inp['stations']);idx={s:j for j,s in enumerate(ids)}
    donor,receive=limits(inp,p,y)
    active=[e for e in inp['network']['edges'] if e['existing'] or e['id'] in built]
    used=sorted({e[k] for e in active for k in ('a','b')})
    # 站的总转出门节点限制自有负荷，不允许把接收负荷再作为新增可转负荷。
    N=len(ids);outgate={s:N+j for j,s in enumerate(ids)}
    fout={f:2*N+2*j for j,f in enumerate(used)};fin={f:v+1 for f,v in fout.items()}
    arcs=[(idx[s],outgate[s],max(0,float(p[j]))) for j,s in enumerate(ids)]
    for f in used:
        s=inp['network']['feeders'][f]['station']
        arcs.extend([(outgate[s],fout[f],donor[f]),(fin[f],idx[s],receive[f])])
    for e in active:
        capacity=e['capacity_mw']
        if e['existing']:capacity=min(capacity,donor[e['a']]*e['source_section_fraction'])
        arcs.append((fout[e['a']],fin[e['b']],capacity))
        if e['bidirectional']:arcs.append((fout[e['b']],fin[e['a']],capacity))
    return 2*N+2*len(used),arcs


def check_year(inp,power,y,units,n,built,stop_after=None):
    N=len(units);full=PF*units.sum(axis=1);survive=full-PF*units.max(axis=1)
    bp,bn=storage_power(inp,n);violations=[];checked=0;maxgap=0.;worst=None
    # 无需转供即可满足的场景直接证明可行；其余场景做独立网络最大流。
    for h,p in enumerate(power):
        normal_ok=np.all(p<=full+bp+1e-6) and np.all(-p<=full+bn+1e-6)
        faileds=[f for f in range(N) if not normal_ok or p[f]>survive[f]+bp[f]+1e-6 or -p[f]>survive[f]+bn[f]+1e-6]
        if not normal_ok:faileds.insert(0,-1)
        if not faileds:continue
        nodes,arcs=network_arcs(inp,p,y,built)
        for failed in faileds:
            cap=full.copy()
            if failed>=0:cap[failed]=survive[failed]
            lo=np.zeros(nodes);hi=np.zeros(nodes);lo[:N]=p-cap-bp;hi[:N]=p+cap+bn
            gap,_=circulation_check(nodes,arcs,lo,hi);checked+=1
            if gap>maxgap:maxgap=gap;worst=(h,failed)
            if gap>NETWORK_TOLERANCE_MW:violations.append((gap,h,failed))
        if stop_after and len(violations)>=stop_after:break
    # 每个故障的最差10个时刻，避免重复加入同一邻近峰段。
    chosen=[]
    for f in range(-1,N):chosen.extend(sorted((v for v in violations if v[2]==f),reverse=True)[:3])
    return {'year':y,'total_hour_contingency_pairs':len(power)*(N+1),'network_maxflow_checks':checked,
            'direct_zero_transfer_checks':len(power)*(N+1)-checked,'max_network_deficit_mw':maxgap,
            'violating_pairs':len(violations),'worst':worst,'quantized_check_tolerance_mw':NETWORK_TOLERANCE_MW},chosen


def extract(inp,power,case,z,meta,solver,history,checks):
    ids=list(inp['stations']);oldunits=np.array([s['initial_units']+[0] for s in inp['stations'].values()])
    oldn=np.zeros(len(ids));oldbuilt=set();annual=[];stations=[];projects=[];total=0.
    for y in inp['years']:
        units,n,ends,_=previous.assets(inp,z,meta,y)
        built={e['id'] for e in inp['network']['edges'] if not e['existing'] and z[meta['edgevars'][e['id'],y]]>.5}
        bought=np.where(units[:,:2]>oldunits[:,:2]+1e-6,units[:,:2],0).sum(axis=1)
        third=(units[:,2]-oldunits[:,2])/50
        tc=bought.sum()*inp['transformer_price_10k_per_purchased_mva']+third.sum()*inp['third_50mva_capex_10k']
        bc=(n-oldn).sum()*inp['storage_module_capex_10k'];lc=len(built-oldbuilt)*inp['line_capex_10k']
        comp={k:c*inp['cost_factors'][k][str(y)] for k,c in [('transformer',tc),('storage',bc),('line',lc)]}
        cost=sum(comp.values());total+=cost
        annual.append({'year':y,'planning_year':y-2021,'peak_mw':meta['peaks'][y],'capacity_mva':float(units.sum()),
                       'clr':float(units.sum()/meta['peaks'][y]),'purchased_transformer_mva':float(bought.sum()+50*third.sum()),
                       'new_third_count':int(third.sum()),'new_lines':len(built-oldbuilt),'cumulative_lines':len(built),
                       'storage_nameplate_mw':float(.1*n.sum()),'storage_mwh':float(.215*n.sum()),
                       'new_storage_mwh':float(.215*(n-oldn).sum()),'construction_capex_10k':tc+bc+lc,
                       'added_lifecycle_npv_10k':cost,'cumulative_lifecycle_npv_10k':total,
                       **{k+'_npv_10k':v for k,v in comp.items()}})
        for j,sid in enumerate(ids):
            stations.append({'year':y,'station':sid,'unit_1_mva':units[j,0],'unit_2_mva':units[j,1],
                             'unit_3_mva':units[j,2],'capacity_mva':float(units[j].sum()),
                             'storage_modules':int(n[j]),'storage_mwh':float(.215*n[j]),
                             'purchased_transformer_mva':float(bought[j]+50*third[j])})
        projects.extend({'year':y,**e} for e in inp['network']['edges'] if e['id'] in built-oldbuilt)
        oldunits,oldn,oldbuilt=units,n,built
    assert abs(total-solver['objective'])<.02,(total,solver['objective'])
    return {'region':'pizhou','case':case,'cost_npv_10k':total,'annual':annual,'solver':solver,
            'scenario_iterations':history,'full_hour_network_checks':checks,'cost_recomputation_error_10k':abs(total-solver['objective']),
            'scope':'全年8760小时及各站单台最大主变N-1，指定候选馈线网络静态代理通过；非SOC时序、非实测全县拓扑'},stations,projects


def run(case,seconds=180,width=1,new_feeders=False,usable=1.):
    root=case_root(width,new_feeders,usable);inp=json.loads((root/'inputs.json').read_text());data=np.load(root/'hourly.npz');power=data['power_base_mw']
    directory=root/case;directory.mkdir(exist_ok=True)
    selected={(int(np.argmax(power.sum(axis=1))),-1),(int(np.argmin(power.sum(axis=1))),-1)}
    for j in range(power.shape[1]):
        selected.add((int(np.argmax(power[:,j])),j));selected.add((int(np.argmin(power[:,j])),j))
    history=[]
    for iteration in range(1,21):
        m,meta=build(inp,power,sorted(selected),case)
        if usable<1:
            from .solver import solve
            warmroot=case_root(width,new_feeders)/case
            z,result=solve(m,directory,f'iteration_{iteration:02}',seconds,.01,inp,meta,warmroot)
        else:z,result=solve_model(m,directory,f'iteration_{iteration:02}',seconds,.005)
        history.append({'iteration':iteration,'selected_scenarios':len(selected),'solver':result})
        if not result['accepted'] and not result.get('feasible_incumbent',False):
            dump(directory/'summary.json',{'case':case,'region':'pizhou','solver':result,'scenario_iterations':history});return
        result['accepted_for_feasibility_pilot']=bool(result.get('feasible_incumbent',False))
        result['cost_optimality_claim']='目标MIP间隙内' if result['accepted'] else '有可行整数解，最优性间隙见mip_gap，不称全局最优'
        checks=[];violations=[]
        for y in inp['years']:
            units,n,_,_=previous.assets(inp,z,meta,y)
            built={e for (e,yy),v in meta['edgevars'].items() if yy==y and z[v]>.5}
            check,v=check_year(inp,power*(1+inp['growth_rate'])**(y-2021),y,units,n,built)
            checks.append(check);violations.extend(v)
            print('CHECK',case,y,check['violating_pairs'],check['max_network_deficit_mw'],flush=True)
        history[-1]['checks']=checks
        if not violations:
            summary,stations,projects=extract(inp,power,case,z,meta,result,history,checks)
            dump(directory/'summary.json',summary);write_csv(directory/'years.csv',summary['annual'])
            write_csv(directory/'stations.csv',stations);write_csv(directory/'projects.csv',projects)
            dump(directory/'selected_scenarios.json',sorted(selected))
            dump(directory/'inputs_hashes.json',{'inputs':sha(root/'inputs.json'),'hourly':sha(root/'hourly.npz'),'code':sha(__file__)})
            print('COMPLETE',case,summary['cost_npv_10k'],flush=True);return
        additions={(h,f) for _,h,f in sorted(violations,reverse=True)[:80]}-selected
        if not additions:raise RuntimeError('主模型与独立网络核验不一致')
        selected.update(additions)
    raise RuntimeError('场景分离未收敛')


if __name__=='__main__':
    raise SystemExit('该历史独立入口已归档；请使用 实验.研究.rebuild_2026.static_actual_20261010。公共函数仍保留供现行模型导入。')
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--case',choices=CASES)
    parser.add_argument('--seconds',type=int,default=180);parser.add_argument('--width',type=int,default=1)
    parser.add_argument('--new-feeders',action='store_true');parser.add_argument('--usable',type=float,default=1.);args=parser.parse_args()
    if args.prepare:prepare(args.width,args.new_feeders,args.usable)
    if args.case:run(args.case,args.seconds,args.width,args.new_feeders,args.usable)
