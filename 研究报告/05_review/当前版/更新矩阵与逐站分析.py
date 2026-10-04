from pathlib import Path
import json,csv,math,itertools
from openpyxl import Workbook,load_workbook
from openpyxl.styles import Font,PatternFill,Alignment
HERE=Path(__file__).resolve().parent;R=HERE.parents[1];IT='当前版'
D=R/'01研究推荐'/IT;A=R/'02图表'/IT;T=R/'03_MD'/IT
BASE=D/'统一起点基准'
tables=json.loads((A/'计算表.json').read_text());sections=json.loads((A/'生成段落.json').read_text())
def table(title,headers,rows):
 return title+'\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(str(x) for x in r)+' |\n' for r in rows)
def dec(x):return f'{float(x):.2f}'
def readcsv(p):
 with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def f(r,k):return float(r[k])
def main():
 rows=json.loads((D/'外推逐点结果.json').read_text());matrix=[]
 l_bins=[(.90,1.10),(1.10,1.40),(1.40,1.70)];b_bins=[(.04,.05),(.05,.08),(.08,.12)]
 case_points=[{'地区':'邳州','eta':1.63065,'g':.080742,'h':4,'R':2.2118},{'地区':'市区','eta':.31788,'g':.018,'h':5,'R':2.2102}]
 checks=[]
 for kl,(llo,lhi) in enumerate(l_bins):
  for elo,ehi in [(0,1),(1,2),(2,3)]:
   for glo,ghi in [(0,.02),(.02,.07),(.07,.1)]:
    for hlo,hhi in [(1,3),(3,6)]:
     for kb,(blo,bhi) in enumerate(b_bins):
      selected=[r for r in rows if elo<=r['装机渗透率']<=ehi and (glo<r['年负荷平均增长率']<=ghi or glo==0 and r['年负荷平均增长率']==0) and hlo<=r['95%峰值持续时间h']<=hhi and (llo<r['主变线路成本比']<=lhi or kl==0 and r['主变线路成本比']==llo) and (blo<r['主变储能成本比_3h']<=bhi or kb==0 and r['主变储能成本比_3h']==blo)]
      assert selected
      values=[r['推荐容载比'] for r in selected]
      matched=[]
      for c in case_points:
       if elo<=c['eta']<=ehi and glo<c['g']<=ghi and hlo<=c['h']<=hhi and llo<1.22364<=lhi and blo<.05941<=bhi:
        values.append(c['R']);matched.append(c['地区']);checks.append({'地区':c['地区'],'矩阵行':len(matrix)+1,'容载比':c['R']})
      low=math.floor((min(values)+1e-10)/.05)*.05;high=math.ceil((max(values)-1e-10)/.05)*.05
      matrix.append({'分布式电源装机渗透率':f'{elo:.2f}～{ehi:.2f}','年负荷平均增长率':('＞' if glo else '')+f'{100*glo:.2f}%～{100*ghi:.2f}%','95%峰值持续时间':f'{hlo}～{hhi} h','主变与线路成本比':('＞' if kl else '')+f'{llo:.2f}～{lhi:.2f}','主变与储能成本比_3h':('＞' if kb else '')+f'{blo:.2f}～{bhi:.2f}','推荐容载比区间':f'{low:.2f}～{min(2.6,high):.2f}','计算点数':len(selected)})
 assert len(matrix)==162 and {x['地区'] for x in checks}=={'邳州','市区'}
 (D/'通用推荐矩阵.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2))
 (HERE/'案例与矩阵衔接核对.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
 headers=['分布式电源装机渗透率','年负荷平均增长率','95%峰值持续时间','主变与线路成本比','主变与储能成本比','推荐弹性容载比']
 keys=list(matrix[0])[:-1]
 blocks=[]
 for k in range(3):
  sub=matrix[k*54:(k+1)*54]
  key='cost_matrix_'+str(k)
  tables[key]=table('表5-0 主变与线路成本比'+sub[0]['主变与线路成本比']+'的弹性容载比推荐区间',headers,[[r[x] for x in keys] for r in sub])
  blocks.append('[[TABLE:'+key+']]')
 sections['cost_banded_matrix']='\n\n'.join(blocks)
 tables.pop('general_matrix',None)
 tables['general_assumptions']=tables['general_assumptions'].replace('(0.75,0.50)/(1,1)/(1.25,1.25)/(0.75,1.25)/(1.25,0.50)','线路0.75/1.00/1.25；储能0.50/1.00/1.25').replace('四角及中心','九组交叉价格').replace('1.057和1.113','1.06和1.11')
 wb=Workbook();ws=wb.active;ws.title='弹性推荐矩阵';ws.append(headers+['计算点数'])
 for r in matrix:ws.append([r[x] for x in keys]+[r['计算点数']])
 ws=wb.create_sheet('参数与计算点');ws.append(list(rows[0]));[ws.append(list(r.values())) for r in rows]
 ws=wb.create_sheet('案例对应');ws.append(['地区','装机渗透率','年负荷平均增长率','95%峰值持续时间/h','弹性容载比','推荐区间'])
 for c in case_points:
  check=next(x for x in checks if x['地区']==c['地区']);ws.append([c['地区'],c['eta'],c['g'],c['h'],c['R'],matrix[check['矩阵行']-1]['推荐容载比区间']])
 ws=wb.create_sheet('使用说明');ws.append(['项目','内容'])
 for row in [['矩阵参数','装机渗透率、增长率、持续时间和两个成本比'],['成本比分档','两个成本比各3档，9组价格组合'],['储能成本比尺度','3 h参考峰段，按有效MW初始投资比较'],['区间形成','同档计算点与案例点的包络，0.05向外取整'],['规划建议','按片区参数选择范围，再用实际设备和线路条件比选'],['计算精度','原始数值用于计算，工作簿显示两位小数']]:ws.append(row)
 for sh in wb:
  sh.freeze_panes='A2';sh.auto_filter.ref=sh.dimensions
  for cell in sh[1]:cell.font=Font(name='宋体',bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='29465B');cell.alignment=Alignment(wrap_text=True)
  for row in sh.iter_rows(min_row=2):
   for cell in row:
    if isinstance(cell.value,float):cell.number_format='0.00% ' if ('增长率' in str(sh.cell(1,cell.column).value) or '电量渗透率估计'==sh.cell(1,cell.column).value) else '0.00'
  for col in sh.columns:sh.column_dimensions[col[0].column_letter].width=22
 wb.save(D/'通用容载比推荐矩阵.xlsx')
 # 逐站段落使用当前已复核年度状态，既有历史版只提供分析组织思路。
 profile_meta=[]
 for region,name in [('pizhou','邳州'),('city','市区')]:
  datasets={scheme:readcsv(BASE/region/(scheme+'_stations.csv')) for scheme in ['rigid','elastic']}
  stations=sorted({x['station'] for x in datasets['elastic']})
  blocks=['### 5.4.'+('4' if region=='pizhou' else '5')+' '+name+'逐站规划方案\n\n'+('邳州各站同时考虑正向供电与反向净负荷。以下结合各站设备结构、负荷转接及储能规模说明弹性方案的配置依据。' if region=='pizhou' else '市区各站按A类供电区域进行规划，站级需求以正向供电和单台主变退出为主。以下结合重载站负荷转出和承接站容量配置说明建设安排。')]
  for station in stations:
   states={sch:sorted([x for x in ds if x['station']==station],key=lambda x:int(x['year'])) for sch,ds in datasets.items()}
   e=states['elastic'][-1];r=states['rigid'][-1];first=states['elastic'][0]
   initial=f(first,'prior_unit_1_mva')+f(first,'prior_unit_2_mva')
   blocks.append('#### '+station+'站规划分析')
   lead=f"该站基期主变配置为{dec(first['prior_unit_1_mva'])}+{dec(first['prior_unit_2_mva'])} MVA，规划第4年转接前最大正向、反向净负荷分别为{dec(e['forward_mw'])} MW和{dec(e['reverse_mw'])} MW，正向95%峰值持续时间为{dec(e['forward_duration_h'])} h。"
   events=[]
   for ix,row in enumerate(states['elastic']):
    acts=[]
    if f(row,'third_transformer_commissioned')>.5:acts.append('扩建50 MVA主变')
    purchase=f(row,'purchased_unit_mva')-(50 if f(row,'third_transformer_commissioned')>.5 else 0)
    if purchase>1e-5:acts.append(f'实施主变增容，新购容量{purchase:.2f} MVA')
    if f(row,'new_storage_power_mw')>1e-5:acts.append(f"新增储能{dec(row['new_storage_power_mw'])} MW/{dec(row['new_storage_energy_mwh'])} MWh")
    if acts:events.append('第'+str(ix+1)+'年'+ '，'.join(acts))
   if events:build='弹性方案'+ '；'.join(events)+'。'
   else:build='弹性方案沿用基期主变容量，后续各年通过站间负荷转接满足容量需求。'
   if f(e,'normal_load_transferred_out_mw')>1e-5:
    role=f"第4年转出{dec(e['normal_load_transferred_out_mw'])} MW、承接{dec(e['normal_load_transferred_in_mw'])} MW后，正向校核负荷为{dec(e['post_transfer_forward_mw'])} MW。负荷转出降低正向需求，同时将反向校核上界提高至{dec(e['post_transfer_reverse_upper_mw'])} MW，配置按两个方向共同确定。"
   elif f(e,'normal_load_transferred_in_mw')>1e-5:
    role=f"第4年承接{dec(e['normal_load_transferred_in_mw'])} MW，正向校核负荷增至{dec(e['post_transfer_forward_mw'])} MW。该站利用相应主变容量承担片区内部负荷，接收能力按承接后的负荷进行正常运行及单台主变退出校核。"
   else:role=f"第4年正向校核负荷为{dec(e['post_transfer_forward_mw'])} MW，设备配置主要承担本站供电与反向输送需求。"
   margin=.95*(f(e,'capacity_mva')-max(f(e,k) for k in ['unit_1_mva','unit_2_mva','unit_3_mva']))+f(e,'storage_energy_mwh')/max(2.15,f(e,'forward_duration_h'))-f(e,'post_transfer_forward_mw')
   comparison=f"刚性方案第4年主变总容量为{dec(r['capacity_mva'])} MVA，储能为{dec(r['storage_power_mw'])} MW；弹性方案相应为{dec(e['capacity_mva'])} MVA和{dec(e['storage_power_mw'])} MW。"
   if f(r,'storage_power_mw')-f(e,'storage_power_mw')>.001:
    comparison+=f"弹性方案储能减少{f(r,'storage_power_mw')-f(e,'storage_power_mw'):.2f} MW，退出工况的容量支撑更多由在役主变和站间负荷配置承担。"
   elif f(e,'capacity_mva')>f(r,'capacity_mva')+.001:comparison+='弹性方案增加主变容量，为本站或片区承接负荷提供支撑。'
   else:comparison+='两类方案的本站主变配置接近，差异主要通过区域其他站点的容量和负荷安排体现。'
   blocks.extend([lead+build,role+comparison])
   tk=region+'_'+station+'_profile';rows_station=[]
   for sch,label in [('rigid','刚性'),('elastic','弹性')]:
    q=states[sch][-1];units='+'.join(dec(q[k]) for k in ['unit_1_mva','unit_2_mva','unit_3_mva'] if f(q,k)>0)
    rows_station.append([label,units,dec(q['storage_power_mw'])+'/'+dec(q['storage_energy_mwh']),dec(q['normal_load_transferred_out_mw']),dec(q['normal_load_transferred_in_mw']),dec(q['post_transfer_forward_mw'])])
   tables[tk]=table('表5-0 '+station+'站第4年配置与负荷转接',['方案','主变组合/MVA','储能/MW/MWh','转出/MW','承接/MW','正向负荷/MW'],rows_station)
   blocks.append('[[TABLE:'+tk+']]')
   profile_meta.append({'区县':name,'站':station,'弹性目标容量MVA':f(e,'capacity_mva'),'刚性目标容量MVA':f(r,'capacity_mva'),'弹性最不利退出余量MW':margin,'年度状态':len(states['elastic'])})
  sections[region+'_station_profiles']='\n\n'.join(blocks)
 p=next(T.glob('05 *.md'));s=p.read_text()
 if '[[SECTION:pizhou_station_profiles]]' not in s:
  s=s.replace('## 5.5 措施作用与工程衔接','[[SECTION:pizhou_station_profiles]]\n\n[[SECTION:city_station_profiles]]\n\n## 5.5 措施作用与工程衔接');p.write_text(s)
 (HERE/'逐站分析对应记录.json').write_text(json.dumps(profile_meta,ensure_ascii=False,indent=2))
 (A/'计算表.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2));(A/'生成段落.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2))
 path=D/'统一起点逐年方案与复核.xlsx';wb=load_workbook(path)
 for ws in wb:
  for row in ws:
   for cell in row:
    if isinstance(cell.value,float):cell.number_format='0.00'
    if isinstance(cell.value,str):cell.value=cell.value.replace('第三台','扩建主变')
 wb.save(path)
 print('推荐矩阵',len(matrix),'行；逐站分析',len(profile_meta),'站')
if __name__=='__main__':main()
