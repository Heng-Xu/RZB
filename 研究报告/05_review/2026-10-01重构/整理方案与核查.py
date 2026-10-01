import csv,json,sys,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
sys.path.insert(0,str(Path(__file__).resolve().parent))
from 整理数据与图表 import ROOT,OUT,DATA,table,TABLES,METRICS,plt,save,COLORS,num,rows
TABLES.update(json.loads((OUT/'计算表.json').read_text()))
SECTIONS={};AUDIT=[];RESULT={}
CASES=['基准','价格_线路较低','价格_线路较贵','价格_储能降价25','价格_储能降价50','价格_储能较贵25','联合_线路贵储能低','联合_线路低储能降25','联合_线路低储能降50','联合_线路低储能贵25','联合_线路贵储能降25','联合_线路贵储能贵25','源荷_光伏规模减20','源荷_光伏规模增20','持续时间_缩短1h','持续时间_延长1h','增长_四年加权','增长_加权增2个百分点']
LABEL={s:s.replace('价格_','').replace('源荷_','').replace('持续时间_','').replace('增长_','').replace('联合_','').replace('25','25%').replace('50','50%').replace('减20','减20%').replace('增20','增20%') for s in CASES}
REG={'pizhou':'邳州','city':'市区'};SCHEME={'rigid':'刚性','elastic':'弹性'}
def readj(p):return json.loads(Path(p).read_text())
def v(r,k):return float(r[k])
def md(title,headers,data):
 return title+'\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in data)+'\n\n'
def cash(year,life,om):
 init=1/(1.06**(year-2021));maint=sum(om/(1.06**(t-2021)) for t in range(year+1,2042))
 renew=sum(1/(1.06**(t-2021)) for t in range(year+life,2041,life))
 return np.array([init,maint,renew])
def margins(r,derate=1,forward=None,units=None,energy=None,reverse=None):
 u=[v(r,'unit_1_mva'),v(r,'unit_2_mva'),v(r,'unit_3_mva')] if units is None else units
 u=[x for x in u if x>0];s=sum(u);e=v(r,'storage_energy_mwh') if energy is None else energy
 p=v(r,'post_transfer_forward_mw') if forward is None else forward
 rev=v(r,'post_transfer_reverse_upper_mw') if reverse is None else reverse
 b=derate*e/max(2.15,v(r,'forward_duration_h'));br=derate*e/max(2.15,v(r,'reverse_duration_h'))
 d=p if r['area_class']=='A' else max(0,min(p-12,p*2/3))
 return [.95*s+b-p,.95*s+br-rev,.95*(s-max(u))+b-d],d,b
def units(r):return '/'.join(f'{v(r,k):g}' for k in ['unit_1_mva','unit_2_mva','unit_3_mva'] if v(r,k)>0)
def compute():
 for case in CASES:
  p=DATA/case;meta=readj(p/'report_scenario.json');review=readj(p/'review.json');RESULT[case]={'meta':meta,'review':review,'regions':{}}
  for region in REG:
   sums={r['scheme']:r for r in readj(p/region/'summary.json')};rr={}
   for scheme in SCHEME:
    yrs=rows(p/region/(scheme+'_years.csv'));stations=rows(p/region/(scheme+'_stations.csv'));trans=rows(p/region/(scheme+'_transfers.csv'))
    out=defaultdict(float);inc=defaultdict(float)
    for t in trans:
     assert v(t,'mw')>=-1e-8;out[int(t['year']),t['donor']]+=v(t,'mw');inc[int(t['year']),t['receiver']]+=v(t,'mw')
    component=np.zeros((3,3));minmargin=1e9;counts=0;previous={};sumry=sums[scheme]
    for yrow in yrs:
     y=int(yrow['year']);a=[r for r in stations if int(r['year'])==y]
     def eq(a,b,tol=1e-5):assert abs(a-b)<tol,(case,region,scheme,y,a,b)
     eq(sum(v(r,'capacity_mva') for r in a),v(yrow,'capacity_mva'));eq(v(yrow,'clr'),v(yrow,'capacity_mva')/v(yrow,'net_peak_proxy_mw'))
     eq(sum(v(r,'normal_load_transferred_out_mw') for r in a),sum(v(r,'normal_load_transferred_in_mw') for r in a))
     eq(sum(v(r,'forward_mw') for r in a),sum(v(r,'post_transfer_forward_mw') for r in a))
     eq(sum(v(r,'normal_load_transferred_out_mw') for r in a),v(yrow,'existing_transfer_mw'))
     for j,(typ,life,om) in enumerate([('transformer',20,.01),('storage',10,.03),('line',20,.01)]):
      capex=v(yrow,typ+'_capex_10k');component[j]+=capex*cash(y,life,om)
      if typ!='line':eq(capex,sum(v(r,typ+'_capex_10k') for r in a),1e-3)
     assert int(yrow['new_lines_in_service'])==0
     assert 1.5-1e-5 <= v(yrow,'clr')<= (2 if scheme=='rigid' else 2.6)+1e-5
     if scheme=='elastic':assert v(yrow,'clr')>=2.001-1e-6
     for r in a:
      sid=r['station'];key=y,sid;u=[v(r,k) for k in ['unit_1_mva','unit_2_mva','unit_3_mva']]
      prior=previous.get(sid,[v(r,'prior_unit_1_mva'),v(r,'prior_unit_2_mva'),0,0]);e=v(r,'storage_energy_mwh')
      assert all(new+1e-5>=old for new,old in zip(u,prior[:3]));assert e+1e-5>=prior[3]
      eq(sum(u),v(r,'capacity_mva'));eq(out[key],v(r,'normal_load_transferred_out_mw'));eq(inc[key],v(r,'normal_load_transferred_in_mw'))
      assert out[key]<=.1*v(r,'forward_mw')+1e-4
      eq(v(r,'post_transfer_forward_mw'),v(r,'forward_mw')-out[key]+inc[key]);eq(v(r,'post_transfer_reverse_upper_mw'),v(r,'reverse_mw')+out[key])
      eq(e,int(r['storage_modules'])*.215);eq(v(r,'storage_power_mw'),int(r['storage_modules'])*.1)
      eq(e-prior[3],v(r,'new_storage_energy_mwh'));eq(v(r,'new_storage_energy_mwh'),int(r['new_storage_modules'])*.215)
      replaced=sum(new for new,old in zip(u[:2],prior[:2]) if new>old+1e-5);third=u[2]-prior[2]
      eq(replaced+third,v(r,'purchased_unit_mva'));eq(v(r,'transformer_capex_10k'),replaced*sumry['transformer_price_10k_per_purchased_mva']*sumry.get('transformer_scale',1)+third/50*1223,1e-3)
      eq(v(r,'storage_capex_10k'),int(r['new_storage_modules'])*21.0456262*sumry.get('storage_scale',1),1e-3)
      if u[2]>0:assert int(r['source_available_third_slots'])>=1
      m,_,_=margins(r);assert min(m)>=-1e-4,(case,region,scheme,y,sid,m);minmargin=min(minmargin,min(m));counts+=1
      previous[sid]=[*u,e]
     assert sum(out[y,r['station']] for r in a)<=.1*v(yrow,'net_peak_proxy_mw')+1e-4
    assert abs(component.sum()-sumry['objective_npv_10k'])<.002,(case,region,scheme,component.sum(),sumry['objective_npv_10k'])
    if 'growth' not in case and not meta.get('smooth'):pass
    rr[scheme]={'years':yrs,'stations':stations,'transfers':trans,'summary':sumry,'costs':component.tolist()}
    AUDIT.append({'情景':case,'地区':REG[region],'方案':SCHEME[scheme],'站年':counts,'最低静态余量MW':minmargin,'费用复算万元':float(component.sum()),'费用偏差万元':float(component.sum()-sumry['objective_npv_10k']),'核查':'通过'})
   for y in range(4):
    assert v(rr['elastic']['years'][y],'clr')>v(rr['rigid']['years'][y],'clr')+.001-1e-6
   RESULT[case]['regions'][region]=rr
  for scheme in SCHEME:
   for y in range(4):assert v(RESULT[case]['regions']['city'][scheme]['years'][y],'clr')+.001<=v(RESULT[case]['regions']['pizhou'][scheme]['years'][y],'clr')+1e-6
def tbase():
 table('indicator_roles','表5-1 推荐参数的定义依据与模型作用',['参数','定义及依据','进入模型的方式'],[
 ['容载比','主变容量／年网供最大负荷[4]','年度结果；降压负荷代理'],['源荷比','装机／用户最大负荷[69]','地区背景；光伏外推条件'],['电量渗透率','发电量／用户年电量[69]','条件标签；电量估计'],['绝对净峰','正反向峰的较大值（式3-6）','方向分别约束；不相互抵消'],['95%峰值持续时间','本方向95%门槛最长连续段（式3-7）','储能能量约束'],['净负荷增长','四个同比率递增加权（式3-1）','外推负荷路径'],['主变／线路成本比','同有效MW费用比（式4-7）','调整线路工程费用'],['主变／储能成本比','带峰段时间费用比（式4-8）','调整储能购置及更新费用']])
 base=RESULT['基准']['regions']
 table('baseline_states','表5-2 共同反事实初态及现状区别[76]',['地区','模型容量/MVA','原表容量/MVA','降压负荷/MW','模型比值'],[[REG[c],num(base[c]['rigid']['summary']['baseline_2021_capacity_mva'],1),2027 if c=='pizhou' else 3113.5,num(base[c]['rigid']['summary']['baseline_2021_load_mw']),num(base[c]['rigid']['summary']['baseline_2021_clr'],6)] for c in REG])
 hist=RESULT['基准']['review']['solve_history']
 table('solver_stages','表5-3 基准三阶段求解信息',['阶段','目标','耗时/s','最优性间隙','状态'],[[i+1,['全寿命费用201113.7877万元','弹性容载比合计16.863909','固定布局转接1231.7117 MW'][i],num(r['elapsed_seconds'],2),num(r['mip_gap'],6),'已证明最优'] for i,r in enumerate(hist)])
 for c in REG:
  for s in SCHEME:
   d=base[c][s];data=[];prior=d['summary']['baseline_2021_capacity_mva']
   for r in d['years']:
    data.append([r['year'],num(r['capacity_mva'],1),num(r['capacity_mva']) if False else num(v(r,'capacity_mva')-prior,1),num(r['new_transformer_purchase_mva'],1),num(r['new_storage_power_mw'],1)+'/'+num(r['new_storage_energy_mwh'],3),num(r['existing_transfer_mw']),num(r['clr'],4)])
    prior=v(r,'capacity_mva')
   table(c+'_'+s+'_years',f'表5-{4+list(REG).index(c)*2+list(SCHEME).index(s)} {REG[c]}{SCHEME[s]}年度措施及指标',['年份','在役/MVA','净增/MVA','采购/MVA','新增储能MW/MWh','正常转接/MW','容载比'],data)
 plt.figure(figsize=(6.8,3.8))
 for c in REG:
  for s in SCHEME:
   ds=base[c][s]['years'];plt.plot(range(2022,2026),[v(r,'clr') for r in ds],marker='o',linestyle='-' if s=='elastic' else '--',label=REG[c]+SCHEME[s],color=COLORS[list(REG).index(c)])
 plt.axhline(2,lw=.6,color='gray');plt.xticks(range(2022,2026));plt.ylabel('容载比');plt.legend(ncol=2);plt.grid(alpha=.2);save('annual_clr')
 totals=[];comp=[];ct=[];paths=[]
 for c in REG:
  for s in SCHEME:
   d=base[c][s];ys=d['years'];total=sum(v(r,'new_transformer_purchase_mva') for r in ys);last=ys[-1];paths.append(REG[c]+SCHEME[s])
   totals.append([REG[c],SCHEME[s],num(total,1),sum(int(r['new_third_transformers']) for r in ys),num(last['installed_storage_power_mw'],1)+'/'+num(last['installed_storage_energy_mwh']),num(sum(v(r,'existing_transfer_mw') for r in ys)),0])
   a=np.array(d['costs']);comp.append([REG[c],SCHEME[s],*map(lambda x:num(x,2),a.sum(axis=1)),num(a.sum(),2)])
  cr=base[c]['rigid']['summary']['objective_npv_10k'];ce=base[c]['elastic']['summary']['objective_npv_10k'];ct.append([REG[c],num(cr,2),num(ce,2),num(cr-ce,2),num((1-ce/cr)*100,2)+'%'])
 table('measure_totals','表5-8 全期措施累计与年末在役状态',['地区','方案','采购/MVA','第三台/项','储能MW/MWh','年度转接之和/MW','新线/条'],totals)
 table('cost_comparison','表5-9 新增措施全寿命现值比较',['地区','刚性/万元','弹性/万元','差额/万元','弹性费用降幅'],ct)
 table('cost_components','表5-10 全寿命费用按措施分解（式4-10）',['地区','方案','主变/万元','储能/万元','线路/万元','合计/万元'],comp)
 fig,axes=plt.subplots(1,2,figsize=(7.1,3.7))
 axes[0].bar(paths,[float(r[2]) for r in totals],color=[COLORS[0],COLORS[1]]*2);axes[0].set_ylabel('全期主变采购 / MVA')
 axes[1].bar(paths,[float(r[4].split('/')[0]) for r in totals],color=[COLORS[0],COLORS[1]]*2);axes[1].set_ylabel('年末储能铭牌功率 / MW')
 for ax in axes:ax.tick_params(axis='x',labelrotation=35)
 save('measure_comparison')
 plt.figure(figsize=(6.5,3.8));bottom=np.zeros(4)
 for j,lab in enumerate(['主变','储能','线路']):
  vals=[float(r[2+j]) for r in comp];plt.bar(paths,vals,bottom=bottom,label=lab,color=COLORS[j]);bottom+=vals
 plt.ylabel('全寿命现值 / 万元');plt.legend();save('lifecycle_components')
 dc=[];ab=[];der=[];tr=[]
 for c in REG:
  for s in SCHEME:
   d=base[c][s];ps=d['summary']['baseline_2021_capacity_mva'];pp=d['summary']['baseline_2021_load_mw']
   for r in d['years']:
    ss=v(r,'capacity_mva');p=v(r,'net_peak_proxy_mw');dc.append([REG[c],SCHEME[s],r['year'],num((ss-ps)/p,6),num(ps*(1/p-1/pp),6),num(ss/p-ps/pp,6)]);ps=ss;pp=p
    aa=[x for x in d['stations'] if x['year']==r['year']];tr.append([REG[c],SCHEME[s],r['year'],len([x for x in d['transfers'] if x['year']==r['year'] and v(x,'mw')>1e-5]),num(r['existing_transfer_mw']),num(v(r,'existing_transfer_mw')/p*100,2)+'%'])
   ns={k:0 for k in ['转接','储能','主变']};dn=0;dm=0
   for r in d['stations']:
    # 与交付材料一致：撤销检查只计最紧的单台退出容量条件。
    none_transfer=margins(r,forward=v(r,'forward_mw'),reverse=v(r,'reverse_mw'))[0][2]
    none_storage=margins(r,energy=0)[0][2]
    first=next(x for x in d['stations'] if x['station']==r['station'])
    none_upgrade=margins(r,units=[v(first,'prior_unit_1_mva'),v(first,'prior_unit_2_mva'),0])[0][2]
    for key,m in zip(ns,[none_transfer,none_storage,none_upgrade]):ns[key]+=m< -1e-5
    m=margins(r,derate=.8)[0][2];dn+=m< -1e-5;dm=max(dm,-m)
   ab.append([REG[c],SCHEME[s],*[ns[k] for k in ns],len(d['stations'])]);der.append([REG[c],SCHEME[s],dn,num(dm),len(d['stations'])])
 table('clr_decomposition','表5-11 年度容载比变化的恒等分解（式5-15）',['地区','方案','年份','容量贡献','分母贡献','合计变化'],dc)
 table('ablation_checks','表5-12 固定布局撤销措施的退出容量不足站年数',['地区','方案','撤销转接','撤销储能','撤销新增主变','总站年'],ab)
 table('storage_derating','表5-13 固定布局下80%理想储能支撑压力检查',['地区','方案','不足站年','最大缺口/MW','总站年'],der)
 table('annual_transfer_summary','表5-21 基准正常转接规模与使用情况',['地区','方案','年份','非零站对/项','转接/MW','占区域代理峰/%'],tr)
 assert [r[2:5] for r in ab]==[[31,18,30],[16,2,38],[49,43,48],[33,18,58]],ab
 assert [r[2] for r in der]==[17,2,30,15],der
 fig,axs=plt.subplots(1,3,figsize=(7.2,3.5))
 for j,ax in enumerate(axs):
  dat=[[max(0,margins(r)[0][j]) for r in base[c][s]['stations']] for c in REG for s in SCHEME]
  ax.boxplot(dat,tick_labels=['邳刚','邳弹','市刚','市弹'],showfliers=False);ax.set_title(['正向总容量','反向总容量','最紧单台退出'][j]);ax.set_ylabel('静态余量 / MW')
 save('station_constraint_margins')
def scenarios():
 econ=[];pr=[];tech=[];matrix=[];cond=[];allrange=defaultdict(list);details=[];measure=[];stress=[];elastic_matrix=[];elastic_measure=[]
 g=readj(OUT/'指标复算.json');eta={'pizhou':(1.630652935,.402778151),'city':(.317875803,.086939913)}
 for idx,case in enumerate(CASES):
  z=RESULT[case];me=z['meta'];tl=me.get('k_TL_relative',1);tb=me.get('k_TB_relative',1);f=me.get('pv',1);h=me.get('duration_delta',0)
  if 'line_scale' in me:tl=1/me['line_scale']
  if 'storage_scale' in me:tb=1/me['storage_scale']
  analytic='dominance_proof' in me.get('method','')
  if idx<12:econ.append([f'C{idx:02}',LABEL[case],num(tl,4),num(tb,4),'既有通道支配证明' if analytic else '完整重新求解'])
  if idx>=12:tech.append([f'C{idx:02}',LABEL[case],f'{f:g}倍' if f!=1 else '保持',f'{h:+g} h，下限1 h' if h else '模板不变','四年加权'+('＋2个百分点' if me.get('growth_delta',0) else '') if me.get('smooth') else '原年度负荷'])
  for c in REG:
   zz=z['regions'][c];costs={s:zz[s]['summary']['objective_npv_10k'] for s in SCHEME};chosen=min(costs,key=costs.get);ys=zz[chosen]['years'];sg=1 if chosen=='elastic' else 0
   if idx<12:
    for s in SCHEME:
     r=zz[s]['years'][-1];pr.append([f'C{idx:02}',REG[c],SCHEME[s],num(costs[s],2),num(r['clr'],4),num(r['installed_storage_power_mw'],1)+'/'+num(r['installed_storage_energy_mwh']),num(sum(v(x,'new_transformer_purchase_mva') for x in zz[s]['years']),1)])
   cond.append([f'C{idx:02}',REG[c],num(eta[c][0]*f,4),num(eta[c][1]*f*100,2)+'%',('原模板' if not h else f'模板{h:+g} h'),num(g[REG[c]+'_growth']*100+me.get('growth_delta',0)*100,4)+'%',num((16.573333333/.95)/(106.8/7.491)*tl,4),num((16.573333333/.95)/(210.456262*3/2.15)*tb,5)])
   matrix.append([f'C{idx:02}',REG[c],SCHEME[chosen],*[num(r['clr'],4) for r in ys],num(costs[chosen],2)])
   measure.append([f'C{idx:02}',REG[c]+SCHEME[chosen],num(sum(v(r,'new_transformer_purchase_mva') for r in ys),1),sum(int(r['new_third_transformers']) for r in ys),num(ys[-1]['installed_storage_power_mw'],1)+'/'+num(ys[-1]['installed_storage_energy_mwh']),num(min(v(r,'existing_transfer_mw') for r in ys),2)+'～'+num(max(v(r,'existing_transfer_mw') for r in ys),2),0])
   ey=zz['elastic']['years']
   elastic_matrix.append([f'C{idx:02}',REG[c],SCHEME[chosen],*[num(r['clr'],4) for r in ey],num(costs['elastic'],2)])
   elastic_measure.append([f'C{idx:02}',REG[c]+'弹性',num(sum(v(r,'new_transformer_purchase_mva') for r in ey),1),sum(int(r['new_third_transformers']) for r in ey),num(ey[-1]['installed_storage_power_mw'],1)+'/'+num(ey[-1]['installed_storage_energy_mwh']),num(min(v(r,'existing_transfer_mw') for r in ey),2)+'～'+num(max(v(r,'existing_transfer_mw') for r in ey),2),0])
   st=[r for r in zz[chosen]['stations'] if r['year']=='2025'];hf=[v(r,'forward_duration_h') for r in st if v(r,'forward_mw')>0];hr=[v(r,'reverse_duration_h') for r in st if v(r,'reverse_mw')>0]
   stress.append([f'C{idx:02}',REG[c],num(ys[-1]['net_peak_proxy_mw'],2),num(max(max(v(r,'forward_mw'),v(r,'reverse_mw')) for r in st)),f'{min(hf):g}～{max(hf):g}',f'{min(hr):g}～{max(hr):g}' if hr else '无事件',sum(v(r,'reverse_mw')>0 for r in st)])
   for s in SCHEME:
    for r in zz[s]['years']:allrange[c,s,int(r['year'])].append(v(r,'clr'))
  # 各情景设备路径仅列真实重算的变化情景；价格支配证明以文字交叉说明。
  if idx==0 or analytic:continue
  details.append(f'#### C{idx:02} {LABEL[case]}\n\n')
  d=[]
  for c in REG:
   for s in SCHEME:
    zz=z['regions'][c][s]
    for r in zz['years']:d.append([REG[c]+SCHEME[s],r['year'],num(r['net_peak_proxy_mw'],2),num(r['capacity_mva'],1),num(r['clr'],4),num(r['new_transformer_purchase_mva'],1),num(r['installed_storage_power_mw'],1)+'/'+num(r['installed_storage_energy_mwh'],3),num(r['existing_transfer_mw'],2)])
  details.append(md(f'表5-22-{idx} {LABEL[case]}的逐年措施路径（式5-3至式5-14）',['地区方案','年份','分母/MW','在役/MVA','容载比','当年采购/MVA','在役储能MW/MWh','正常转接/MW'],d))
  for c in REG:
   zz=z['regions'][c];cr=zz['rigid']['summary']['objective_npv_10k'];ce=zz['elastic']['summary']['objective_npv_10k'];best='弹性' if ce<cr else '刚性';diff=abs(ce-cr)
   b=RESULT['基准']['regions'][c]['elastic'];e=zz['elastic'];change=sum(v(r,'new_transformer_purchase_mva') for r in e['years'])-sum(v(r,'new_transformer_purchase_mva') for r in b['years']);se=v(e['years'][-1],'installed_storage_energy_mwh')-v(b['years'][-1],'installed_storage_energy_mwh')
   details.append(f'{REG[c]}在该情景中，刚性现值为{cr:.2f}万元、弹性为{ce:.2f}万元，{best}较低{diff:.2f}万元。弹性全期主变采购较基准{("增加" if change>=0 else "减少")}{abs(change):.1f} MVA，年末储能能量{("增加" if se>=0 else "减少")}{abs(se):.3f} MWh。年度比值需与本表分母和在役容量一并使用。\n\n')
 table('price_scenarios','表5-14 两个经济比例的情景设定（相对基准）',['情景号','变化条件','主变／线路比例倍数','主变／储能比例倍数','计算方式'],econ)
 table('price_results','表5-15 价格情景的费用与措施结果',['情景','地区','方案','现值/万元','2025容载比','年末储能MW/MWh','全期采购/MVA'],pr)
 table('technical_scenarios','表5-16 技术条件外推的构造范围',['情景号','条件','光伏规模','95%时间','增长路径'],tech)
 table('conditional_matrix','表5-17a 推荐矩阵的条件参数（第5.9节）',['情景','地区','源荷比标签','电量渗透率标签','95%时间','加权增长率','主变／线路','主变／储能（3 h）'],cond)
 TABLES['conditional_matrix']+=md('表5-17b 同情景弹性年度指标及费用比较选择',['情景','地区','费用优选','弹性2022年','弹性2023年','弹性2024年','弹性2025年','弹性现值/万元'],elastic_matrix)
 TABLES['conditional_matrix']+=md('表5-17c 同情景弹性措施汇总（对应年度指标）',['情景','地区方案','全期采购/MVA','第三台/项','年末储能MW/MWh','年度转接范围/MW','新线/条'],elastic_measure)
 TABLES['conditional_matrix']+=md('表5-17d 2025年方向压力和时间条件',['情景','地区','区域分母/MW','最大站绝对峰/MW','正向H95范围/h','反向H95范围/h','反送站数'],stress)
 table('recommended_ranges','表5-18 18个情景的年度指标包络（保持模板条件）',['地区','方案','年份','最低值','最高值','样本情景数'],[[REG[c],SCHEME[s],y,num(min(a),4),num(max(a),4),len(a)] for (c,s,y),a in allrange.items()])
 SECTIONS['scenario_paths']=''.join(details)
 # 工作簿与正文共用未经四舍五入的路径，含全部站年和站对措施。
 wb=Workbook();wb.remove(wb.active)
 for name,header,data in [('条件矩阵', ['情景','地区','源荷比估计','电量渗透率估计','95%时间变化','加权增长率','主变／线路比例','主变／储能比例3h'],cond),('弹性指标',['情景','地区','费用优选','弹性2022容载比','弹性2023容载比','弹性2024容载比','弹性2025容载比','弹性现值万元'],elastic_matrix),('弹性措施',['情景','地区方案','全期采购MVA','第三台项数','年末储能MW_MWh','年度转接范围MW','新线条数'],elastic_measure),('经济推荐',['情景','地区','优选方案','2022容载比','2023容载比','2024容载比','2025容载比','现值万元'],matrix),('推荐措施',['情景','地区方案','全期采购MVA','第三台项数','年末储能MW_MWh','年度转接范围MW','新线条数'],measure),('压力时间条件',['情景','地区','2025区域分母MW','2025最大站绝对峰MW','正向H95范围h','反向H95范围h','反送站数'],stress),('独立复核',list(AUDIT[0]),[list(a.values()) for a in AUDIT])]:
  ws=wb.create_sheet(name);ws.append(header)
  for row in data:ws.append(row)
 for kind in ['years','stations','transfers']:
  ws=wb.create_sheet({'years':'全部年度措施','stations':'全部站年措施','transfers':'全部站对转接'}[kind]);first=True
  for case in CASES:
   for c in REG:
    for s in SCHEME:
     data=RESULT[case]['regions'][c][s][kind]
     if not data:continue
     if first:ws.append(['情景','地区','方案']+list(data[0]));first=False
     for row in data:ws.append([case,REG[c],SCHEME[s]]+[int(x) if k in ['year','storage_modules','new_storage_modules'] else float(x) if k not in ['station','area_class','transfer_purpose','kind','donor','receiver','pair','scheme','load_scenario'] and _isnum(x) else x for k,x in row.items()])
 for ws in wb:
  ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
  for cell in ws[1]:cell.fill=PatternFill('solid',fgColor='29465B');cell.font=Font(name='宋体',bold=True,color='FFFFFF');cell.alignment=Alignment(wrap_text=True)
  for col in ws.columns:ws.column_dimensions[col[0].column_letter].width=min(38,max(12,len(str(col[0].value))*1.2))
 wb.save(DATA/'容载比条件矩阵与全部措施.xlsx')
def _isnum(x):
 try:float(x);return True
 except:return False
def cases():
 base=RESULT['基准']['regions'];allannual=[]
 for c in REG:
  blocks=[];rs={s:{(r['station'],int(r['year'])):r for r in base[c][s]['stations']} for s in SCHEME}
  ids=sorted({k[0] for k in rs['rigid']})
  for j,sid in enumerate(ids,1):
   first=rs['rigid'][sid,2022];last=rs['elastic'][sid,2025];one=rs['rigid'][sid,2025];classlabel=first['area_class'];h=last['forward_duration_h'];hr=last['reverse_duration_h']
   blocks.append(f'#### {sid}：{classlabel}类供电任务与设备配置\n\n')
   slot=int(first['source_available_third_slots']);pred=f"{v(first,'prior_unit_1_mva'):g}＋{v(first,'prior_unit_2_mva'):g} MVA"
   blocks.append(f'该站共同初态为{pred}，模型可用第三台位置{slot}个。2025年原正向任务{v(last,"forward_mw"):.3f} MW、反向任务{v(last,"reverse_mw"):.3f} MW，绝对峰取两者较大值{max(v(last,"forward_mw"),v(last,"reverse_mw")):.3f} MW。正向95%峰段为{h} h，反向为{hr} h；其数值按第三章时序或模板口径使用[78][79]。\n\n')
   data=[]
   for s in SCHEME:
    for y in range(2022,2026):
     r=rs[s][sid,y];m,d,b=margins(r);data.append([SCHEME[s],y,num(v(r,'post_transfer_forward_mw'),3),num(d),num(b),*[num(x,3) for x in m]])
   blocks.append(md(f'表5-19-{list(REG).index(c)+1}-{j} {sid}两方案年度静态容量校核（式5-9至式5-12）',['方案','年份','转接后正向/MW','退出服务量/MW','储能支撑/MW','正向余量/MW','反向余量/MW','退出余量/MW'],data))
   r=one;e=last;mr,dr,br=margins(r);me,de,be=margins(e)
   detail=[]
   for s in SCHEME:
    events=[]
    for y in range(2022,2026):
     q=rs[s][sid,y];buy=v(q,'purchased_unit_mva');eng=v(q,'new_storage_energy_mwh')
     if buy or eng:
      events.append(str(y)+'年'+('采购'+num(buy,1)+' MVA主变' if buy else '')+('并' if buy and eng else '')+('配置'+num(v(q,'new_storage_power_mw'),1)+' MW/'+num(eng,3)+' MWh储能' if eng else ''))
    detail.append(SCHEME[s]+'路径'+('，'.join(events)+'。' if events else '四年保持共同初态设备。'))
   blocks.append(''.join(detail)+'\n\n')
   blocks.append(f'到2025年，刚性主变为{units(r)} MVA，转出／转入分别为{v(r,"normal_load_transferred_out_mw"):.3f}／{v(r,"normal_load_transferred_in_mw"):.3f} MW；弹性主变为{units(e)} MVA，对应{v(e,"normal_load_transferred_out_mw"):.3f}／{v(e,"normal_load_transferred_in_mw"):.3f} MW。表中退出余量按最大在役单台退出计算，其他较小设备退出的剩余容量更多。\n\n')
   idx=int(np.argmin(me));label=['正向总容量','反向总容量','单台退出容量'][idx]
   term=(f'A类静态退出服务量保留全部{de:.3f} MW负荷。' if classlabel=='A' else f'B、C类服务量按min(L′−12,2L′/3)及非负下限得到{de:.3f} MW。')
   blocks.append(f'弹性路径2025年最紧条件为{label}，余量{max(0,me[idx]):.3f} MW。{term}储能以{be:.3f} MW进入正向及退出容量式，反向按本方向峰段另算；转出负荷仍增加原站反送上界。上述余量用于检查所选布局，不替代实际恢复时间或全年充放电校核。\n\n')
  SECTIONS[c+'_station_cases']=''.join(blocks)
  for s in SCHEME:
   for y in range(2022,2026):
    data=[]
    for sid in ids:
     r=rs[s][sid,y];data.append([sid,units(r),num(r['purchased_unit_mva'],1),num(r['storage_power_mw'],1)+'/'+num(r['storage_energy_mwh']),num(v(r,'normal_load_transferred_out_mw')-v(r,'normal_load_transferred_in_mw')),num(r['post_transfer_forward_mw']),num(r['post_transfer_reverse_upper_mw'])])
    allannual.append(f'#### {REG[c]}{SCHEME[s]}{y}年\n\n'+md(f'表5-20-{list(REG).index(c)+1}-{list(SCHEME).index(s)+1}-{y} 年度在役布局及措施（式5-2、式5-4、式5-8）',['站号','主变布局/MVA','当年采购/MVA','在役储能MW/MWh','净转出/MW','正向任务/MW','反向上界/MW'],data))
 SECTIONS['annual_station_tables']=''.join(allannual)
def main():
 compute();tbase();scenarios();cases();supporting_analysis()
 (OUT/'计算表.json').write_text(json.dumps(TABLES,ensure_ascii=False,indent=2));(OUT/'生成段落.json').write_text(json.dumps(SECTIONS,ensure_ascii=False,indent=2))
 (ROOT/'研究报告/05_review/2026-10-01重构/矩阵独立复核.json').write_text(json.dumps(AUDIT,ensure_ascii=False,indent=2))
 print('复核路径',len(AUDIT),'复核站年',sum(r['站年'] for r in AUDIT),'表键',len(TABLES),'生成文字字符',sum(len(v) for v in SECTIONS.values()))
def supporting_analysis():
 data=[];tot=np.zeros(4)
 for y in range(2022,2042):
  investment=210.456262 if y==2022 else 0;maintenance=6.31368786 if y>=2023 else 0;renew=210.456262 if y==2032 else 0
  df=1.06**-(y-2021);npv=(investment+maintenance+renew)*df
  data.append([y,num(investment,3),num(maintenance,3),num(renew,3),num(df,6),num(npv,3)]);tot+=np.array([investment,maintenance,renew,npv])
 data.append(['合计',*map(lambda x:num(x,3),tot[:3]),'—',num(tot[3],3)])
 table('storage_cashflow_example','表4-9 2022年投运10柜包的评价期现金流（式4-10）',['年份','初始投资/万元','固定运维/万元','更新/万元','折现系数','当年现值/万元'],data)
 data=[]
 for name,i,l,q in [('更换50 MVA主变',50*16.573333333,20,.01),('增加第三台50 MVA',1223,20,.01),('10柜储能包',210.456262,10,.03),('参考联络线',106.8,20,.01)]:
  for y in [2022,2025]:
   cf=i*cash(y,l,q);data.append([name,y,num(i,3),*map(lambda x:num(x,3),cf),num(cf.sum(),3)])
 table('project_npv_examples','表4-10 不同投运年份的单项工程现值演算（式4-10）',['工程','年份','初始原价/万元','投资现值/万元','运维现值/万元','更新现值/万元','合计现值/万元'],data)
 bc=[];base=RESULT['基准']['regions']
 for c in REG:
  for s in SCHEME:
   d=base[c][s];cf=np.array(d['costs']);capex=sum(v(r,k+'_capex_10k') for r in d['years'] for k in ['transformer','storage','line']);bc.append([REG[c],SCHEME[s],num(capex,2),*map(lambda x:num(x,2),cf.sum(axis=0)),num(cf.sum(),2)])
 table('base_cash_components','表4-11 四条基准路径初始原价与全寿命现值',['地区','方案','初始投资合计/万元','首次投资现值/万元','运维现值/万元','更新现值/万元','总现值/万元'],bc)
 rankings=[]
 for c in REG:
  a=base[c]['elastic']['stations'];ids=sorted({r['station'] for r in a});lookup={(r['station'],int(r['year'])):r for r in a};vals=np.array([[max(v(lookup[sid,y],'forward_mw'),v(lookup[sid,y],'reverse_mw')) for y in range(2022,2026)] for sid in ids])
  order=np.argsort(vals[:,-1])[::-1];ids=[ids[i] for i in order];vals=vals[order]
  plt.figure(figsize=(6.8,7.4 if c=='city' else 6.3));plt.imshow(vals,aspect='auto',cmap='YlOrBr');plt.yticks(range(len(ids)),ids,fontsize=8);plt.xticks(range(4),range(2022,2026));plt.colorbar(label='建模绝对峰 / MW')
  for i in range(len(ids)):
   for j in range(4):plt.text(j,i,f'{vals[i,j]:.1f}',ha='center',va='center',fontsize=7,color='white' if vals[i,j]>np.max(vals)*.7 else 'black')
  save(c+'_modeled_peaks')
  for sid in ids[:6]:
   r=lookup[sid,2025];rankings.append([REG[c],sid,r['area_class'],num(r['forward_mw']),num(r['reverse_mw']),num(max(v(r,'forward_mw'),v(r,'reverse_mw'))),r['forward_duration_h'],r['reverse_duration_h']])
 table('modeled_peak_rankings','表3-12 两地区2025年模型绝对峰较高站的任务特征',['地区','站号','类别','正向/MW','反向/MW','绝对峰/MW','正向时间/h','反向时间/h'],rankings)
 costs=[]
 for case in CASES:
  for c in REG:
   z=RESULT[case]['regions'][c];cr=z['rigid']['summary']['objective_npv_10k'];ce=z['elastic']['summary']['objective_npv_10k'];costs.append([LABEL[case],REG[c],cr,ce,(cr-ce)/cr*100])
 fig,axes=plt.subplots(1,2,figsize=(7.2,5.2))
 for ax,c,col in zip(axes,REG,COLORS):
  ar=[r for r in costs if r[1]==REG[c]];ax.barh(range(len(ar)),[r[4] for r in ar],color=[col if r[4]>=0 else COLORS[1] for r in ar]);ax.set_yticks(range(len(ar)),[r[0] for r in ar],fontsize=7);ax.axvline(0,color='black',lw=.6);ax.set_title(REG[c]);ax.set_xlabel('弹性相对刚性费用降幅 / %');ax.invert_yaxis()
 save('scenario_cost_preference')
 # 关键技术情景的分阶段信息，用实际求解记录区别支配证明。
 stages=[]
 for case in CASES:
  z=RESULT[case];method=z['meta'].get('method','')
  if 'dominance_proof' in method:
   stages.append([LABEL[case],'支配证明','既有通道可替代新增任务','原可行布局','不重复整数求解']);continue
  h=z['review']['solve_history'];stages.append([LABEL[case],num(h[0]['mip_gap'],6),num(h[1]['mip_gap'],6),num(h[2]['mip_gap'],6),'三阶段已证明最优'])
 table('scenario_solver_stages','表5-23 情景计算的最优性与证明方式',['情景','费用阶段间隙','容量阶段间隙','转接阶段间隙','计算状态'],stages)
if __name__=='__main__':main()
