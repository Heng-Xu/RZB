"""同步1008外推重算结果，并按相邻同区间规则压缩推荐表；不改两地区案例。"""
from pathlib import Path
import json,math,itertools,statistics,collections,re
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
from 展示术语 import apply_workbook_terms
from 规划档位矩阵 import select,summarize
HERE=Path(__file__).resolve().parent;R=HERE.parents[1];D=R/'01研究推荐/当前版';A=R/'02图表/当前版';O=HERE/'1008线路经济替代修订'
AREA={'A':'A类','BC':'B/C类'};KD={'较均匀':1.,'偏集中':1.15};LT=['架空为主','电缆为主']
ETA=[(0,1),(1,2),(2,3)];G=[(0,.02),(.02,.07),(.07,.1)];H=[(1,3),(3,6)];B=[(.04,.05),(.05,.08),(.08,.12)];PR=[1.25,1.,.75]
def read(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2))
def fmt(x):return f'{0 if abs(x)<.005 else x:.2f}'
def interval(vals):return f'{math.floor((min(vals)+1e-10)*100)/100:.2f}～{math.ceil((max(vals)-1e-10)*100)/100:.2f}'
def table(title,headers,rows):return title+'\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)+'\n'
def selection(rows,m):
 e=tuple(map(float,m['分布式电源装机渗透率'].split('～')));g=tuple(float(v.replace('＞','').replace('%',''))/100 for v in m['年负荷平均增长率'].split('～'));h=tuple(map(float,m['95%峰值持续时间'].replace(' h','').split('～')));b=tuple(float(v.replace('＞','')) for v in m['主变与储能成本比_3h'].split('～'))
 return select(rows,m['线路类型'],e,g,h,b)
def update_summary(m,sub):
 chosen,share,lo,hi,counts=summarize(sub)
 return {**m,'主选参考档位':fmt(chosen),'主选档占比':share,'覆盖参考档位':max(counts,key=float),'涉及参考档位':'/'.join(counts),'容载比最小值':lo,'容载比最大值':hi,'档位计数':counts,'计算点数':len(sub),'计算容载比范围':interval([lo,hi])}
def merge_rectangles(cells):
 # Merge only contiguous rectangles with identical displayed outward endpoints.
 # Every original cell is retained in the union; no holes or endpoint clipping.
 changed=True
 while changed:
  changed=False
  for axis in [4,3,2,0,1]:
   groups=collections.defaultdict(list)
   for c in cells:groups[(c['interval'],tuple(v for k,v in enumerate(c['box']) if k!=axis))].append(c)
   new=[]
   for group in groups.values():
    group.sort(key=lambda c:c['box'][axis]);current=group[0]
    for nxt in group[1:]:
     if current['box'][axis][1]+1==nxt['box'][axis][0]:
      box=list(current['box']);box[axis]=(box[axis][0],nxt['box'][axis][1]);current={'box':tuple(box),'interval':current['interval'],'ids':current['ids']|nxt['ids'],'source_cells':current['source_cells']+nxt['source_cells']};changed=True
     else:new.append(current);current=nxt
    new.append(current)
   cells=new
 return sorted(cells,key=lambda c:c['box'])
def label(bounds,axis):
 l,h=bounds
 if axis==0:return f'{ETA[l][0]:.2f}～{ETA[h][1]:.2f}'
 if axis==1:return ('＞' if G[l][0] else '')+f'{G[l][0]*100:.2f}%～{G[h][1]*100:.2f}%'
 if axis==2:return f'{H[l][0]:.2f}～{H[h][1]:.2f}'
 if axis==3:return ('＞' if l else '')+f'{B[l][0]:.2f}～{B[h][1]:.2f}'
def main():
 rows=read(D/'外推逐点结果.json');tables=read(A/'计算表.json');sections=read(A/'生成段落.json')
 ids={id(r):i for i,r in enumerate(rows)}
 matrix=[update_summary(m,selection(rows,m)) for m in read(D/'通用推荐矩阵.json')]
 structured=[]
 for i,m in enumerate(matrix,1):
  for area,shape in itertools.product(AREA,('偏集中','较均匀')):
   sub=[r for r in selection(rows,m) if r['供电区域']==area and r['负荷分布']==shape]
   structured.append({'总矩阵行':i,'供电区域':area,'负荷分布':shape,**update_summary(m,sub)})
 save(D/'通用推荐矩阵.json',matrix);save(D/'按供电类别与分布推荐矩阵.json',structured)
 formal=[];merge_audit=[];blocks=[];unmerged=[]
 headers=['分布式电源装机渗透率','年最大净负荷平均增长率','95%峰值持续时间/h','主变与储能单位功率投资比（3 h）','主变与线路单位功率投资比','容载比推荐区间']
 for lt,area,shape in itertools.product(LT,AREA,KD):
  cells=[]
  for ei,gi,hi,bi,pi in itertools.product(range(3),range(3),range(2),range(3),range(3)):
   sub=[r for r in select(rows,lt,ETA[ei],G[gi],H[hi],B[bi]) if r['供电区域']==area and r['负荷分布']==shape and r['线路价格倍数']==PR[pi]]
   assert sub
   cells.append({'box':tuple((x,x) for x in [ei,gi,hi,bi,pi]),'interval':interval([r['推荐容载比'] for r in sub]),'ids':{ids[id(r)] for r in sub},'source_cells':[(ei,gi,hi,bi,pi)]})
  unmerged.extend([{'线路类型':lt,'供电区域':area,'负荷分布':shape,'参数索引':c['source_cells'][0],'点索引':sorted(c['ids']),'容载比推荐区间':c['interval']} for c in cells])
  merged=merge_rectangles(cells);records=[]
  for c in merged:
   sub=[rows[i] for i in sorted(c['ids'])];vals=[r['推荐容载比'] for r in sub];lr=[r['主变线路成本比'] for r in sub]
   investment=fmt(min(lr)) if max(lr)-min(lr)<1e-10 else f'{min(lr):.2f}～{max(lr):.2f}'
   entry={'供电区域类别':AREA[area],'负荷分散系数':KD[shape],'线路类型':lt,**{headers[k]:label(c['box'][k],k) for k in range(4)},headers[4]:investment,headers[5]:interval(vals),'容载比最小值':min(vals),'容载比最大值':max(vals),'计算点数':len(sub)}
   assert entry[headers[5]]==c['interval']
   formal.append(entry);records.append(entry)
   merge_audit.append({'推荐行':len(formal),'原始单元':c['source_cells'],'参数索引范围':c['box'],'点索引':sorted(c['ids']),'线路价格倍数':sorted(set(r['线路价格倍数'] for r in sub))})
  key=f'classified_{len(blocks)}';title=f'表5-0 {AREA[area]}、负荷分散系数{KD[shape]:.2f}的容载比推荐区间（{lt}）'
  tables[key]=table(title,headers,[[e[k] for k in headers] for e in records])+'注：投资比均为无量纲量；容载比按MVA/MW计。相邻条件对应相同显示区间时合并列示，端点覆盖合并前全部计算结果。\n'
  widths=[e['容载比最大值']-e['容载比最小值'] for e in records]
  block=f'#### {AREA[area]}供电区域，负荷分散系数{KD[shape]:.2f}，{lt}\n\n'
  block+=f'该类站群初始单台主变容量为{50 if area=="A" else 40} MVA，本节既有联络剩余可转负荷为{0.0:.2f} MW。按分布式电源装机规模、负荷增长、持续时间和工程投资条件比较后，归纳为{len(records)}组推荐范围，区间宽度中位数为{statistics.median(widths):.2f}。表中对结果相同的相邻参数范围合并列示，使持续时间或相对价格变化没有引起容量调整的条件能够集中查阅。\n\n'
  block+='主变与线路单位功率投资比随线路造价变化，主变与储能单位功率投资比按3 h参考条件列示。查表时同时选择两类投资比，能够区分通过新增联络利用邻站容量、增加本地主变容量以及配置储能的不同经济条件。表内保留主变离散规格形成的容量变化，推荐区间均由相应方案的设备容量与目标年最大负荷计算。\n\n[[TABLE:'+key+']]\n\n'
  for eta in ['0.00～1.00','1.00～2.00','2.00～3.00']:
   q=[r for r in structured if r['线路类型']==lt and r['供电区域']==area and r['负荷分布']==shape and r['分布式电源装机渗透率']==eta]
   desc='；'.join(f'年最大净负荷平均增长率{g}时为{interval([v for r in q if r["年负荷平均增长率"]==g for v in [r["容载比最小值"],r["容载比最大值"]]])}' for g in dict.fromkeys(r['年负荷平均增长率'] for r in q))
   block+=f'分布式电源装机渗透率为{eta}时，合并所列持续时间及价格条件，容载比范围为：{desc}。具体取值按表内两类投资比及持续时间进一步定位，避免将不同经济条件下的配置混为一个推荐值。\n\n'
  blocks.append(block)
 sections['cost_banded_matrix']='\n'.join(blocks)
 sections['matrix_results']=f'全部技术经济情景按供电区域类别、负荷分散系数和线路类型展开，形成1296个包含线路价格条件的基础单元；合并相邻同区间条件后，正文列出{len(formal)}组推荐范围。合并保留各单元的完整计算结果和区间端点，逐点方案与合并前后对应关系见配套工作簿。'
 save(D/'分类容载比推荐区间.json',formal);save(O/'区间合并追溯.json',merge_audit);save(O/'合并前1296单元.json',unmerged)
 update_tables(rows,tables,formal)
 save(A/'计算表.json',tables);save(A/'生成段落.json',sections)
 update_workbook(rows,matrix,structured,formal,merge_audit,tables)
 update_prose(rows,formal,tables,sections)
 plot(rows)
 save(O/'成果同步核对.json',{'状态':'通过','逐点数':len(rows),'分类基础单元':len(unmerged),'合并后推荐行':len(formal),'合并前后全部点覆盖':len(set(i for r in merge_audit for i in r['点索引'])),'区间宽度中位数':statistics.median(r['容载比最大值']-r['容载比最小值'] for r in formal)})
 print('同步完成，推荐行',len(formal))
def get_profile(rows,area,shape,kind):
 q=[r for r in rows if r['供电区域']==area and r['负荷分布']==shape and r['线路类型']=='架空为主' and r['线路价格倍数']==1 and (kind=='eta' or r['装机渗透率']==1.8) and (kind=='growth' or r['年负荷平均增长率']==.04) and (kind=='duration' or r['95%峰值持续时间h']==3) and (kind=='price' or r['储能价格倍数']==1)]
 field={'eta':'装机渗透率','growth':'年负荷平均增长率','duration':'95%峰值持续时间h','price':'储能价格倍数'}[kind]
 return sorted(q,key=lambda r:r[field],reverse=kind=='price')
def update_tables(rows,t,formal):
 groups=collections.defaultdict(dict)
 fixed=['供电区域','负荷分布','装机渗透率','年负荷平均增长率','95%峰值持续时间h','储能价格倍数','线路类型']
 for r in rows:groups[tuple(r[k] for k in fixed)][r['线路价格倍数']]=r
 pairs=[]
 for group in groups.values():
  lo=group[1.25];hi=group[.75]
  pairs.append({'供电区域类别':AREA[lo['供电区域']],'线路类型':lo['线路类型'],'低投资比':lo['主变线路成本比'],'高投资比':hi['主变线路成本比'],'容载比变化':hi['推荐容载比']-lo['推荐容载比'],'联络项目数变化':hi['联络项目数']-lo['联络项目数'],'费用现值变化万元':hi['全寿命费用万元']-lo['全寿命费用万元']})
 paired=[]
 for ar,lt in itertools.product(AREA.values(),LT):
  q=[r for r in pairs if r['供电区域类别']==ar and r['线路类型']==lt]
  paired.append([ar,lt,f'{q[0]["低投资比"]:.2f}→{q[0]["高投资比"]:.2f}',len(q),fmt(statistics.mean(r['容载比变化'] for r in q)),f'{100*sum(abs(r["容载比变化"])>1e-6 for r in q)/len(q):.2f}%',fmt(statistics.mean(r['费用现值变化万元'] for r in q))])
 t['line_ratio_paired']=table('表5-0 主变与线路单位功率投资比提高时的配对结果',['供电区域类别','线路类型','投资比变化','配对数','容载比平均变化','容载比变化情景占比','费用现值平均变化/万元'],paired)
 save(O/'线路投资比配对分析.json',pairs)
 # A documented representative case: maximum within-type price response,
 # breaking ties by lower PV penetration, growth and duration. All samples retained.
 selected=max(groups.values(),key=lambda g:(round(abs(g[.75]['推荐容载比']-g[1.25]['推荐容载比']),8),-abs(g[1.]['装机渗透率']-1.8),-abs(g[1.]['95%峰值持续时间h']-3),-abs(g[1.]['储能价格倍数']-1),-g[1.]['年负荷平均增长率']))[1.]
 q=[r for r in rows if all(r[k]==selected[k] for k in fixed if k!='线路类型')];q.sort(key=lambda r:(LT.index(r['线路类型']),r['线路价格倍数']))
 t['line_ratio_effects']=table('表5-0 主变与线路单位功率投资比变化下的典型方案比较',['线路类型','线路价格倍数','主变与线路单位功率投资比','容载比','公用主变总容量/MVA','新增联络项目数/项','评价期费用现值/万元'],[[r['线路类型'],fmt(r['线路价格倍数']),fmt(r['主变线路成本比']),fmt(r['推荐容载比']),fmt(r['总容量MVA']),r['联络项目数'],fmt(r['全寿命费用万元'])] for r in q])
 save(O/'典型线路价格情景.json',{'选择规则':'所有同线路类型价格端点配对中容载比变化最大的一组；同幅度时优先装机渗透率接近1.80、持续时间接近3 h、储能基准价的条件，再按增长率排序；用于展示替代过程，不代表平均效应','参数':{k:selected[k] for k in fixed if k!='线路类型'},'结果':q})
 params=['装机渗透率','年负荷平均增长率','95%峰值持续时间h','供电区域','线路价格倍数','储能价格倍数','负荷分布','线路类型'];effects=[]
 names={'装机渗透率':'分布式电源装机渗透率','年负荷平均增长率':'年最大净负荷平均增长率','95%峰值持续时间h':'95%峰值持续时间/h'}
 for key in [params[i] for i in [0,1,2,4,5,7]]:
  grouped=collections.defaultdict(list)
  for r in rows:grouped[tuple(r[k] for k in params if k!=key)].append(r)
  ds=[];cs=[];ns=[]
  for v in grouped.values():
   v.sort(key=lambda r:r[key]);a,b=v[0],v[-1];ds.append(b['推荐容载比']-a['推荐容载比']);cs.append(b['全寿命费用万元']-a['全寿命费用万元']);ns.append(b['联络项目数']-a['联络项目数'])
  effects.append({'参数':names.get(key,key),'配对数量':len(ds),'容载比变化平均':statistics.mean(ds),'最大绝对变化':max(map(abs,ds)),'容载比改变比例':sum(abs(x)>1e-6 for x in ds)/len(ds),'费用变化平均万元':statistics.mean(cs),'联络项目数改变比例':sum(x!=0 for x in ns)/len(ns)})
 t['controlled_driver_effects']=table('表5-0 固定其他条件时单参数端点变化的影响',['变化参数','配对数','容载比平均变化','最大绝对变化','容载比变化情景占比','费用平均变化/万元'],[[e['参数'],e['配对数量'],fmt(e['容载比变化平均']),fmt(e['最大绝对变化']),f'{100*e["容载比改变比例"]:.2f}%',fmt(e['费用变化平均万元'])] for e in effects]);save(O/'单参数配对效应.json',effects)
 for area,shape,kind in itertools.product(AREA,KD,['eta','growth','duration','price']):
  key=f'{kind}_profile_{area}_{KD[shape]:.2f}';old=t[key];head=[s.strip() for s in old.splitlines()[2].strip('|').split('|')];q=get_profile(rows,area,shape,kind);data=[]
  for r in q:
   clr=r['推荐容载比'];cap=r['总容量MVA'];power=r['储能柜数']*.1;cost=r['全寿命费用万元']
   if kind=='eta':v=[r['装机渗透率'],clr,cap,power,r['转接负荷MW'],cost]
   elif kind=='growth':v=[f'{100*r["年负荷平均增长率"]:.2f}%',cap/clr,cap,clr,power,cost]
   elif kind=='duration':v=[r['95%峰值持续时间h'],clr,cap,power,r['储能柜数']*.215,cost]
   else:v=[r['储能价格倍数'],r['主变储能成本比_3h'],clr,cap,power,cost]
   data.append([fmt(x) if isinstance(x,(int,float)) else x for x in v])
  t[key]=table(old.splitlines()[0],head,data)
 widths=[]
 for lt,area,kd in itertools.product(LT,AREA.values(),KD.values()):
  q=[r['容载比最大值']-r['容载比最小值'] for r in formal if r['线路类型']==lt and r['供电区域类别']==area and r['负荷分散系数']==kd]
  widths.append([area,fmt(kd),lt,len(q),fmt(min(q)),fmt(statistics.median(q)),fmt(max(q)),sum(x<=.100000001 for x in q)])
 t['interval_width_summary']=table('表5-0 不同类别推荐区间的宽度统计',['供电区域类别','负荷分散系数','线路类型','区间数','最小宽度','宽度中位数','最大宽度','宽度不超过0.10的区间数'],widths)+'注：按合并后推荐行统计，宽度采用未取整端点之差，单位MVA/MW。\n'
 examples=[]
 for area,shape,lt in itertools.product(AREA,KD,LT):
  q=[r for r in select(rows,lt,(1,2),(.02,.07),(1,3),(.05,.08)) if r['供电区域']==area and r['负荷分布']==shape and r['线路价格倍数']==1]
  examples.append([AREA[area],fmt(KD[shape]),lt,fmt(q[0]['主变线路成本比']),interval([r['推荐容载比'] for r in q])])
 unused_recommended_examples=table('表5-0 相同源荷条件下两类线路的分类推荐示例',['供电区域类别','负荷分散系数','线路类型','主变与线路单位功率投资比','容载比推荐区间'],examples)
 unused_driver_selection=t['driver_selection_evidence'].replace('按线路类型和价格情景比较费用，并校核容量配置是否变化','与可转负荷和承接站余量共同影响联络及主变配置；按线路类型和价格条件归纳推荐')
 t['general_assumptions']=t['general_assumptions'].replace('| 初始站间转供率 | A类50%；B/C类28.29% | 案例参数外推 |','| 既有联络剩余可转负荷 | 0.00 MW | 新增转供需求通过建设联络获得 |').replace('| 线路类型 | 架空为主/电缆为主；电缆占比10.00%/90.00% | 与供电区域类别交叉计算 |','| 架空为主 | 架空长度占90.00%，电缆长度占10.00% | 每项3 km、两台开关，基准投资124.80万元 |\n| 电缆为主 | 架空长度占10.00%，电缆长度占90.00% | 每项3 km、两台开关，基准投资499.20万元 |\n| 单项联络可转负荷 | 两类线路均为7.49 MW | 保持技术能力相同，比较敷设造价差异 |')
 t['general_assumptions']+='| 主变N-1校核 | 各站最大单台主变分别停运 | 健康邻站按正常可用容量承接转供负荷 |\n| 新增联络 | 各站对为候选，单项可转负荷7.49 MW | 按容量需求与费用比较确定建设数量 |\n'
def update_workbook(rows,matrix,structured,formal,merge_audit,tables):
 wb=Workbook();wb.remove(wb.active)
 keys=['线路类型','分布式电源装机渗透率','年负荷平均增长率','95%峰值持续时间','主变与线路成本比','主变与储能成本比_3h','主选参考档位','主选档占比','计算容载比范围','计算点数','覆盖参考档位','涉及参考档位']
 for name,data,heads in [('分类推荐区间',formal,list(formal[0])),('参数与计算点',rows,list(rows[0])),('弹性推荐矩阵',matrix,keys),('按供电类别与分布查表',structured,['总矩阵行','供电区域','负荷分布']+keys)]:
  ws=wb.create_sheet(name);ws.append(heads)
  for r in data:ws.append([r[k] for k in heads])
 ws=wb.create_sheet('线路投资比分析')
 for line in tables['line_ratio_effects'].splitlines()[2:]:
  if line.startswith('|') and not line.startswith('| ---'):ws.append([v.strip() for v in line.strip('|').split('|')])
 ws=wb.create_sheet('推荐合并追溯');ws.append(['推荐行','合并前单元数','逐点索引（从0起）','线路价格倍数'])
 for r in merge_audit:ws.append([r['推荐行'],len(r['原始单元']),','.join(map(str,r['点索引'])),','.join(map(str,r['线路价格倍数']))])
 ws=wb.create_sheet('使用说明');ws.append(['项目','内容'])
 for x in [('推荐入口','分类推荐区间按供电区域类别、负荷分散系数和线路类型选择，再定位源荷、增长、持续时间及两类投资比。'),('同区间合并','相邻参数单元显示区间相同时合并；只合并完整连续的参数组合，不遗漏中间条件；未计算的连续参数应进一步比选。'),('线路经济性','单台主变分别停运，健康邻站承接；新增联络与本地主变扩容按费用选择，正常与事故转供共用线路能力。'),('费用方向','主变价格保持不变，线路价格越低，主变与线路单位功率投资比越高。'),('区间端点','全部计算配置的最小值至最大值，向外保留两位小数；合并时不截掉端点。'),('详细追溯','参数与计算点保存25200组；推荐合并追溯逐行登记原始计算点。'),('案例保持','邳州、市区四年案例数据保持；本次只重算五站外推。')]:ws.append(x)
 apply_workbook_terms(wb)
 for name in ['弹性推荐矩阵','按供电类别与负荷分散系数查表']:wb[name].sheet_state='hidden'
 for ws in wb:
  ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
  for c in ws[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='29465B');c.alignment=Alignment(wrap_text=True,vertical='center')
  for col in ws.columns:ws.column_dimensions[col[0].column_letter].width=24
  for row in ws.iter_rows(min_row=2):
   for c in row:
    if isinstance(c.value,float):c.number_format='0.00'
    c.alignment=Alignment(wrap_text=True,vertical='center')
 wb.active=0;wb.save(D/'通用容载比推荐矩阵.xlsx')
 cases=read(HERE/'案例与矩阵衔接核对.json')
 for c in cases:
  row=matrix[c['矩阵行']-1];c['落入模板计算范围']=row['容载比最小值']<=c['容载比']<=row['容载比最大值']
 save(HERE/'案例与矩阵衔接核对.json',cases)

def update_prose(rows,formal,tables,sections):
 path=next((R/'03_MD/当前版').glob('05 *.md'));original=path.read_text();prefix,s=original.split('## 5.6 参数拓展与通用推荐矩阵',1);s,suffix=s.split('## 5.7 规划建议',1);s='## 5.6 参数拓展与通用推荐矩阵'+s+'## 5.7 规划建议'+suffix
 s=s.replace('新购规格、扩建50 MVA主变、储能柜及联络能力与前述计算方法一致。','新购规格、扩建50 MVA主变、储能柜及单项联络能力沿用前述参数。外推分别考察每座站最大单台主变停运后的供电状态，健康邻站按其正常可用容量承接转供负荷；新增联络按站对选择建设，正常与事故转供共同受已建线路能力限制。该比较体现主变配置与站间支援的联系[4]。')
 s=s.replace('主变与线路单位功率投资比在各分类表下注明，同时在第5.6.4节列出三档价格的配对分析。架空为主和电缆为主分别计算，容载比在本次线路价格范围内保持一致，费用按各档价格分别比较。','主变与线路单位功率投资比作为推荐表的一列，与主变及储能的相对投资共同定位容载比范围。架空为主和电缆为主分别比较三档价格；当新增联络和主变扩容的费用排序改变时，推荐区间相应调整。对于相邻参数范围内推荐区间相同的情景，合并其参数范围，减少重复列示。')
 sel=read(O/'典型线路价格情景.json');p=sel['参数'];q=sel['结果']
 s=s.replace('下表按供电区域与敷设方式列出价格变化对应的容载比范围、联络建设规模和平均费用现值。各行平均费用覆盖相同的源荷、增长、负荷分散系数及储能条件，可用于比较线路价格的影响。',f'下表选取价格变化引起容量配置调整的一组典型条件：{AREA[p["供电区域"]]}、负荷分散系数{KD[p["负荷分布"]]:.2f}、分布式电源装机渗透率{p["装机渗透率"]:.2f}、年最大净负荷平均增长率{100*p["年负荷平均增长率"]:.2f}%、95%峰值持续时间{p["95%峰值持续时间h"]:.2f} h，储能价格为基准的{p["储能价格倍数"]:.2f}倍。两类线路保持相同技术能力，分别比较价格变化下的建设规模和费用，展示联络与主变扩容的替代过程。')
 start='A类情景利用既有联络完成负荷转接，';end='[[TABLE:controlled_driver_effects]]'
 a=s.index(start);b=s.index(end,a)
 t=[]
 for lt in LT:
  v=[r for r in q if r['线路类型']==lt];lo,hi=v[0],v[-1]
  t.append(f'{lt}条件下，线路价格由基准的0.75倍升至1.25倍，新增联络由{lo["联络项目数"]}项变为{hi["联络项目数"]}项，公用主变总容量由{lo["总容量MVA"]:.2f} MVA变为{hi["总容量MVA"]:.2f} MVA，容载比由{lo["推荐容载比"]:.2f}变为{hi["推荐容载比"]:.2f}。')
 s=s[:a]+''.join(t)+'联络造价提高后，利用邻站余量所需的新增线路费用上升，本地增容可能成为较经济的选择。上表用于说明配置发生切换时的工程关系，全部情景的响应比例见配对统计。\n\n'+s[b:]
 effects=read(O/'单参数配对效应.json');ed={e['参数']:e for e in effects}
 a=s.index('配对结果中，源荷比从');b=s.index('在能量受限时，',a)
 s=s[:a]+f'配对结果中，分布式电源装机渗透率从0.00增至3.00，容载比平均变化为{ed["分布式电源装机渗透率"]["容载比变化平均"]:.2f}；年最大净负荷平均增长率从0.00%增至10.00%，对应平均变化为{ed["年最大净负荷平均增长率"]["容载比变化平均"]:.2f}。95%峰值持续时间和储能价格的端点变化分别使{100*ed["95%峰值持续时间/h"]["容载比改变比例"]:.2f}%和{100*ed["储能价格倍数"]["容载比改变比例"]:.2f}%的配对容载比发生变化。负荷增长同时扩大容载比分母，容量需求需结合主变在役规模共同分析。\n\n'+f'线路价格从0.75倍提高至1.25倍，有{100*ed["线路价格倍数"]["容载比改变比例"]:.2f}%的配对容载比发生变化，最大绝对变化为{ed["线路价格倍数"]["最大绝对变化"]:.2f}；线路由架空为主改为电缆为主时，变化比例为{100*ed["线路类型"]["容载比改变比例"]:.2f}%。相对投资影响配置的条件主要出现在本地存在容量缺口、邻站能够承接且新增线路与增容费用相近的组合中。已有联络足够或主变主要受反向功率约束时，价格变化仍可能只改变费用或保持原配置。\n\n'+s[b:]
 for area,shape,kind in itertools.product(AREA,KD,['eta','growth','duration','price']):
  key=f'{kind}_profile_{area}_{KD[shape]:.2f}';marker='[[TABLE:'+key+']]';a=s.index(marker)+len(marker);b=s.find('\n#### ',a);c=s.find('\n### ',a);b=min(x for x in [b,c,len(s)] if x>=0)
  segment=s[a:b];v=get_profile(rows,area,shape,kind);lo,hi=v[0],v[-1]
  if kind=='eta':
   first=f'分布式电源装机渗透率由{lo["装机渗透率"]:.2f}增加到{hi["装机渗透率"]:.2f}，容载比由{lo["推荐容载比"]:.2f}变为{hi["推荐容载比"]:.2f}；公用主变总容量由{lo["总容量MVA"]:.2f} MVA变为{hi["总容量MVA"]:.2f} MVA。储能额定功率分别为{lo["储能柜数"]*.1:.2f} MW和{hi["储能柜数"]*.1:.2f} MW，评价期费用现值由{lo["全寿命费用万元"]:.2f}万元变为{hi["全寿命费用万元"]:.2f}万元。增长率固定，容载比分母保持一致，差异来自容量配置调整。'
  elif kind=='growth':
   first=f'年最大净负荷平均增长率由0.00%提高至10.00%，年网供最大负荷由{lo["总容量MVA"]/lo["推荐容载比"]:.2f} MW增至{hi["总容量MVA"]/hi["推荐容载比"]:.2f} MW；公用主变总容量由{lo["总容量MVA"]:.2f} MVA变为{hi["总容量MVA"]:.2f} MVA，容载比由{lo["推荐容载比"]:.2f}变为{hi["推荐容载比"]:.2f}。评价期费用现值由{lo["全寿命费用万元"]:.2f}万元变为{hi["全寿命费用万元"]:.2f}万元。负荷增长与整台主变投运的变化幅度不同，容载比随两者共同变化。'
  elif kind=='duration':
   first=f'95%峰值持续时间由1.00 h延长至6.00 h，容载比由{lo["推荐容载比"]:.2f}变为{hi["推荐容载比"]:.2f}，公用主变总容量由{lo["总容量MVA"]:.2f} MVA变为{hi["总容量MVA"]:.2f} MVA。储能额定能量由{lo["储能柜数"]*.215:.2f} MWh变为{hi["储能柜数"]*.215:.2f} MWh，评价期费用现值由{lo["全寿命费用万元"]:.2f}万元变为{hi["全寿命费用万元"]:.2f}万元。持续时间通过储能可持续功率影响配置；由主变与联络满足需求的条件可以保持相同容量。'
  else:
   first=f'主变与储能单位功率投资比由{lo["主变储能成本比_3h"]:.2f}提高至{hi["主变储能成本比_3h"]:.2f}，容载比由{lo["推荐容载比"]:.2f}变为{hi["推荐容载比"]:.2f}，储能额定功率由{lo["储能柜数"]*.1:.2f} MW变为{hi["储能柜数"]*.1:.2f} MW。评价期费用现值由{lo["全寿命费用万元"]:.2f}万元变为{hi["全寿命费用万元"]:.2f}万元。相对价格变化首先影响所需储能的费用，是否调整主变容量还取决于局部容量缺口及持续时间。'
  paragraphs=segment.strip().split('\n\n');paragraphs[0]=first
  # Numerical second paragraphs in old profiles must also follow the new solve.
  for i,para in enumerate(paragraphs[1:],1):
   if any(c.isdigit() for c in para.replace('N-1','')):
    paragraphs[i]='各计算点按同一设备候选和经济评价方法进行比选。容量配置是否变化，取决于当前措施能否继续满足正常运行、主变停运和反向功率要求。既有设备仍有余量时，参数变化可以不增加主变容量；需要新增措施时，则同时比较增容、储能及联络建设的费用。'
  s=s[:a]+'\n\n'+'\n\n'.join(paragraphs)+'\n'+s[b:]
 s=s.replace('前者在本次范围内主要改变联络工程费用，后者在部分条件下改变主变与储能组合。','前者在部分条件下改变新增联络与主变容量的组合，后者联系储能价格和可持续功率，两者共同影响方案费用。')
 a=s.index('A类供电区域、负荷分散系数1.00的区间宽度中位数');b=s.index('## 5.7 规划建议',a)
 paras=[]
 for area,kd in itertools.product(AREA.values(),KD.values()):
  q=[r for r in formal if r['供电区域类别']==area and r['负荷分散系数']==kd]
  desc=[]
  for lt in LT:
   w=[r['容载比最大值']-r['容载比最小值'] for r in q if r['线路类型']==lt]
   desc.append(f'{lt}归纳为{len(w)}组，区间宽度中位数为{statistics.median(w):.2f}，其中{sum(x<=.100000001 for x in w)}组不超过0.10')
  paras.append(f'{area}、负荷分散系数{kd:.2f}条件下，'+'；'.join(desc)+'。区间数量同时受参数引起的容量差异和相邻同区间合并影响，不宜仅按行数多少判断方案优劣。')
 paras+=['重复区间的合并以参数范围连续为前提。例如相邻的两段持续时间在其余条件相同时得到相同容载比区间，可以扩大持续时间范围后列为一行；若中间某一价格或增长条件出现不同配置，则继续分别列示。合并后每一行对应完整的参数组合，能够减少重复查阅，同时保留产生容量差异的条件。','合并采用表内向外保留两位小数后的区间进行判断，再用全部原精度计算点重新确定端点。因此，显示相同但末位存在微小差异的结果可以集中列示，合并区间仍覆盖所有原始配置。工作簿保留每一行对应的计算点和参数范围，可以追溯设备规模及工程费用。','线路造价影响新增联络与主变扩容之间的选择，但这种影响具有条件性。既有转供能力充足时，新增线路价格并不参与所选建设方案；邻站余量不足时，增加联络也不能替代本地容量。推荐表对这些同结果条件作适度合并，对确实发生配置变化的价格条件单独保留。',f'合并后共有{len(formal)}组推荐范围，原精度区间宽度中位数为{statistics.median(r["容载比最大值"]-r["容载比最小值"] for r in formal):.2f}。各行仍保留对应技术经济情景的全部端点，较宽区间可结合片区已明确的装机、负荷和价格条件进一步定位。']
 s=s[:a]+'\n\n'.join(paras)+'\n\n'+s[b:]
 s=s.replace('架空为主线路对应主变与线路单位功率投资比0.84～1.40。按供电区域类别和负荷分散系数细分后的结果如下。','线路与储能均采用基准价格，分别比较架空为主和电缆为主条件。按供电区域类别和负荷分散系数细分后的结果如下。')
 s=s.replace('这些条件的源荷范围和相对工程价格相同，推荐区间仍有差异','这些条件的源荷范围和储能价格相同，线路敷设类型及其投资比不同，推荐区间可能出现差异')
 # Rebuild figure narrative around line price, keeping the existing figure slot.
 s=s.replace('图5-0 不同供电区域类别与负荷分散系数下的容载比变化','图5-0 不同线路投资条件下的容载比变化')
 s=s.replace('图中分布式电源装机渗透率取1.80，95%峰值持续时间取3 h，线路采用架空为主基准价。四幅子图分别对应两类供电区域与两种负荷分散系数，曲线表示三种主变与储能单位功率投资比。各点来自相应参数组合的容量配置结果，连线用于观察变化趋势。','图中分布式电源装机渗透率取1.80，95%峰值持续时间取3 h，储能采用基准价格。四幅子图分别对应两类供电区域与两种负荷分散系数；曲线比较两类线路基准造价及电缆价格变化下的容载比。重合部分表示所选主变容量相同，分离部分表示线路经济条件改变了配置选择。')
 s=s.replace('初始转供率采用50%和28.29%，分别对应两类站群；','本节比较既有联络无剩余可用能力、新增转供需求需建设联络的条件；')
 s=s.replace('参数变化通过站级正向、反向负荷和持续支撑系数进入约束，以评价期费用确定对应配置。','本节为新增联络需求条件下的专项外推，既有联络剩余可转负荷取0.00 MW，新增转供通过建设线路获得，推荐范围对应这一供电条件。容载比依据负荷增长要求、正常与故障供电能力及工程经济性确定；费用较低的联络方案可能减少本地主变建设。参数变化通过站级正向、反向负荷和持续支撑系数进入约束，以评价期费用确定对应配置。')
 s=s.replace('95%峰值持续时间及主变与储能单位功率投资比确定容载比范围。','95%峰值持续时间、主变与储能单位功率投资比及主变与线路单位功率投资比确定容载比范围。')
 s=s.replace('曲线比较两类线路基准造价及电缆价格变化下的容载比。','曲线比较架空为主基准造价与电缆为主两种价格条件下的容载比。')
 s=s.replace('供电区域类别同时关联初始规格与转供率，二者不能据此分别识别独立效应。','供电区域类别同时关联初始主变规格与站间可转负荷上限，二者的影响在本次分类条件下共同体现。')
 s=s.replace('已有联络足够或主变主要受反向功率约束时，价格变化仍可能只改变费用或保持原配置。','当主变主要受反向功率约束，或已选线路与主变组合在所考察价格范围内仍具有费用优势时，价格变化可能只改变费用或保持原配置。')
 s=s.replace('原站和受端容量共同约束可转负荷，已有能力得到充分使用后才产生新增投资需求。','转出站、承接站的容量及已建线路能力共同约束可转负荷。')
 s=s.replace('既有转供能力充足时，新增线路价格并不参与所选建设方案；邻站余量不足时，增加联络也不能替代本地容量。','当既定建设组合在不同价格下仍具有费用优势时，推荐容载比可以保持相同；邻站余量不足时，增加联络也不能替代本地容量。')
 path.write_text(prefix+s.split('## 5.7 规划建议',1)[0]+'## 5.7 规划建议'+suffix)

def plot(rows):
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib import font_manager
 from matplotlib.ticker import FormatStrFormatter
 font_manager.fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF');font_manager.fontManager.addfont('/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf')
 plt.rcParams.update({'font.family':['Times New Roman',font_manager.FontProperties(fname='/usr/share/fonts/wps-office/FZFSK.TTF').get_name()],'font.size':10,'axes.unicode_minus':False})
 fig,axes=plt.subplots(2,2,figsize=(8,7.2),sharex=True,sharey=True)
 for ax,(area,shape) in zip(axes.flat,itertools.product(AREA,KD)):
  for lt,price,col,style in [('架空为主',1,'#29465b','-'),('电缆为主',.75,'#778f68','--'),('电缆为主',1.25,'#9b4b39',':')]:
   q=[r for r in rows if r['供电区域']==area and r['负荷分布']==shape and r['装机渗透率']==1.8 and r['95%峰值持续时间h']==3 and r['储能价格倍数']==1 and r['线路类型']==lt and r['线路价格倍数']==price];q.sort(key=lambda r:r['年负荷平均增长率'])
   ax.plot([100*r['年负荷平均增长率'] for r in q],[r['推荐容载比'] for r in q],marker='o',ms=3,lw=1.2,ls=style,color=col,label=f'{lt}；投资比{q[0]["主变线路成本比"]:.2f}')
  ax.set_title(f'{AREA[area]}；负荷分散系数{KD[shape]:.2f}');ax.grid(alpha=.2);ax.set_ylim(1.45,2.62);ax.set_xticks([0,2,4,7,10]);ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'));ax.legend(fontsize=7)
 fig.supxlabel('年最大净负荷平均增长率 / %');fig.supylabel('容载比 /（MVA/MW）');fig.tight_layout();fig.savefig(A/'planning_tier_heatmap.png',dpi=300,bbox_inches='tight');plt.close(fig)
if __name__=='__main__':main()
