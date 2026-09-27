from pathlib import Path
import csv,json,re,hashlib
from decimal import Decimal

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'研究报告/03_MD'
SRC=ROOT/'研究报告/02图表/source_data'
results=[]
def check(name,ok,detail=None):
 results.append({'check':name,'passed':bool(ok),'detail':detail})
index=json.loads((SRC/'交付索引.json').read_text())
mapping=json.loads((OUT/'检查证据/图表改号对应.json').read_text())
chapters=sorted(OUT.glob('[0-9][0-9] *.md'))
check('七章文件数量',len(chapters)==7,len(chapters))
for name in ['公式符号说明.md','数据来源说明.md']:
 check('配套文件 '+name,(OUT/name).is_file())
alltext='\n'.join(p.read_text() for p in chapters)
references=[]
for item in index:
 source_number=item['number']; n=mapping[source_number]; owners=[]
 for p in chapters:
  s=p.read_text()
  display=re.search(r'!\['+re.escape(n)+r' ',s) if n.startswith('图') else re.search(r'^'+re.escape(n)+r' ',s,re.M)
  if display:
   owners.append(p.name)
   before=s[:display.start()]
   check(n+' 展示前正文引用',bool(re.search(r'(?:如|见|详见|参见|见于|说明|所示)[^\n]*'+re.escape(n),before)) or bool(re.search(re.escape(n)+r'[^\n]*(?:所示|见|说明|引用)',before)))
   if n.startswith('表'):
    actual=[]
    for line in s[display.end():].splitlines():
     if line.startswith('|'):
      cells=[v.strip() for v in line.strip('|').split('|')]
      if not all(v=='---' for v in cells):actual.append(cells)
     elif actual:break
    with (SRC/f'{source_number}.csv').open(encoding='utf-8-sig',newline='') as f:
     expected=[[re.sub(r'(?:图|表)\d+-\d+(?!\d)',lambda m:mapping.get(m[0],m[0]),v.replace('\n','').replace('|','／')) for v in r] for r in csv.reader(f)]
    check(n+' 逐单元格显示值一致',actual==expected)
 check(n+' 恰有一处正式展示',len(owners)==1,owners)
 references.append({'number':n,'chapter':owners})
for p in chapters+[OUT/'公式符号说明.md',OUT/'数据来源说明.md']:
 s=p.read_text()
 for target in re.findall(r'\]\(([^)]+)\)',s):
  if not target.startswith(('http','app:')):
   check(p.name+' 相对链接 '+target,(p.parent/target).exists())
 blocks=list(re.finditer(r'\\\[(.*?)\\\]',s,re.S))
 for b in blocks:
  after=s[b.end():].lstrip().split('\n\n',1)[0]
  check(p.name+' 公式后变量单位解释',after.startswith('其中') and '单位' in after,b[1][-35:])
 prose=re.sub(r'\\\[.*?\\\]|\\\(.*?\\\)','',s,flags=re.S)
 prose=re.sub(r'!\[[^\]]*\]\([^)]*\)','',prose)
 if p in chapters:
  prose=prose.split('## 参考文献')[0]
  prose=re.sub(r'\]\(https?://[^)]+\)',']',prose)
  for bad in ['首次提出','填补空白','国际领先','充分证明','全面证明','效果显著','显著提升科学性','冻结结果','GitHub Actions','pipeline','artifact','manifest']:
   check(p.name+' 无禁止表达 '+bad,bad not in prose)
  check(p.name+' 无程序字段进入正文',not re.search(r'(?<![a-zA-Z0-9_])[a-z]+_[a-z][a-z0-9_]*(?![a-zA-Z0-9_])',prose,re.I))
  check(p.name+' 无未展开的生成占位',not re.search(r'\[\[(?:图|表)',s))
ch4=(OUT/'04 第四章 弹性容载比优化模型.md').read_text()
labels=re.findall(r'\\tag\{([^}]+)\}',ch4)
check('29组公式编号连续',labels==[f'4-{x}' for x in range(1,30)],labels)
appendix=(OUT/'公式符号说明.md').read_text()
check('公式附录与正文LaTeX完全一致',re.findall(r'\\\[(.*?)\\\]',ch4,re.S)==re.findall(r'\\\[(.*?)\\\]',appendix,re.S))
rule_delta=json.loads((OUT/'检查证据/旧规则替换登记.json').read_text())
allowed={'研究报告/AGENTS.md','研究报告/终稿/写作与科学表达硬约束.md'}
deltas={x['path']:x for x in rule_delta['files'] if x['path'] in allowed}
for path in ['docs/FREEZE-MANIFEST-2026-09-27.json','研究报告/00审查/证据/阶段0冻结清单.json']:
 manifest=json.loads((ROOT/path).read_text())
 for x in manifest['files']:
  p=ROOT/x['path']; digest=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
  if x['path'] in deltas:
   d=deltas[x['path']]
   check('已授权规则替换 '+x['path'],x['sha256']==d['original_sha256'] and digest==d['current_sha256'] and hashlib.sha256((ROOT/d['archive']).read_bytes()).hexdigest()==x['sha256'])
  else:
   check('冻结科学文件不变 '+x['path'],digest==x['sha256'])
admitted={r['id']:r for r in json.loads((ROOT/'研究报告/00审查/data_source.json').read_text())['records']}
record_ids=set()
for it in index:
 info=json.loads((SRC/f"{it['number']}.json").read_text())
 for r in info.get('records',[]):
  record_ids.add(r['id'])
  expected=admitted.get(r['id'])
  check(it['number']+' 准入记录 '+r['id'],expected is not None and all(r.get(k)==expected.get(k) for k in ['value','source','source_location','source_sha256']))
  p=ROOT/r['source']
  check(it['number']+' 原来源哈希 '+r['id'],p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==r['source_sha256'])
ch2=json.loads((OUT/'检查证据/第二章文献核定.json').read_text())
chapter2=(OUT/'02 第二章 国内外研究现状.md').read_text()
body,refs=chapter2.split('## 参考文献',1)
cited=set(map(int,re.findall(r'\[(\d+)\]',body)))
listed=set(map(int,re.findall(r'^\[(\d+)\]',refs,re.M)))
verified={r['original_number'] for r in ch2['references']}
check('第二章引用与核定书目完全对应',cited==listed==verified,{'cited':sorted(cited),'listed':sorted(listed)})
check('原综述未修改',hashlib.sha256((ROOT/ch2['original_source']).read_bytes()).hexdigest()==ch2['original_sha256'])
for r in ch2['references']:
 check('核定书目与正文一致 '+str(r['original_number']),r['bibliography'] in refs and (r['source_url'] is None or r['source_url'] in refs))
for p in chapters:
 number=int(p.name[:2]);s=p.read_text()
 for kind in ['图','表']:
  displays=re.findall(r'^!\[('+kind+r'\d+-\d+) ' if kind=='图' else r'^('+kind+r'\d+-\d+) ',s,re.M)
  check(p.name+' '+kind+'编号按展示顺序',displays==[f'{kind}{number}-{i}' for i in range(1,len(displays)+1)],displays)
for r in json.loads((OUT/'图表引用登记.json').read_text()):
 original=json.loads((ROOT/r['source']).read_text())
 revised=json.loads((OUT/'图表/source_data'/f"{r['number']}.json").read_text())
 check(r['number']+' 改号数据不变',revised['data']==original['data'] and revised['source_number']==r['source_number'] and revised['source_sha256']==hashlib.sha256((ROOT/r['source']).read_bytes()).hexdigest())
 if r['number'].startswith('图'):
  check(r['number']+' 图内题号一致',r['number']+' '+revised['title'] in revised['display_text'])
# Compare all decimal quantities in the analytical chapters with same-stage data values.
pool={}
for it in index:
 info=json.loads((SRC/f"{it['number']}.json").read_text())
 def visit(v):
  if isinstance(v,dict):
   for z in v.values():visit(z)
  elif isinstance(v,list):
   for z in v:visit(z)
  elif isinstance(v,(int,float)) or isinstance(v,str):
   for token in re.findall(r'(?<![a-zA-Z0-9_.])-?\d+\.\d+(?![a-zA-Z0-9_.])',str(v)):
    pool.setdefault(token,[]).append(it['number'])
 visit(info.get('data'));visit(info.get('records'))
 def addnum(x):
  try:
   value=Decimal(str(x))
   if not value.is_finite():return
   for digits in range(1,10):
    token=f'{value:.{digits}f}'
    pool.setdefault(token,[]).append(it['number'])
  except Exception:pass
 for r in info.get('records',[]):addnum(r.get('value'))
 def nested(v):
  if isinstance(v,dict):
   for z in v.values():nested(z)
  elif isinstance(v,list):
   for z in v:nested(z)
  else:addnum(v)
 nested(info.get('data'))
for r in admitted.values():
 addnum(r.get('value'))
 for token in re.findall(r'(?<![a-zA-Z0-9_.])-?\d+\.\d+(?![a-zA-Z0-9_.])',str(r.get('value'))):
  pool.setdefault(token,[]).append(r['id'])
ledger=[]
for p in [OUT/'03 第三章 研究对象与数据基础.md',OUT/'05 第五章 优化结果分析.md',OUT/'06 第六章 典型区域案例分析.md',OUT/'07 第七章 工程应用建议与总结.md']:
 s='\n'.join(l for l in p.read_text().splitlines() if not l.startswith(('#','|')))
 s=re.sub(r'!\[[^\]]*\]\([^)]*\)','',s)
 for m in re.finditer(r'(?<![a-zA-Z0-9_.])-?\d+\.\d+(?![a-zA-Z0-9_.])',s):
  n=m[0]; evidence=sorted(set(pool.get(n,[])))
  check('正文数值可定位 '+p.name+' '+n,bool(evidence),evidence)
  ledger.append({'chapter':p.name,'value':n,'context':s[max(0,m.start()-28):m.end()+30],'source_figures_tables':evidence})
# Recalculate the two stated cost reductions from unrounded source values.
with (SRC/'图4-2.csv').open(encoding='utf-8-sig',newline='') as f: costrows=list(csv.DictReader(f))
# The display tables preserve the cited reduction; verify against primary annual matrix too.
primary=ROOT/'实验/研究/rebuild_2026/source_audit/capacity_release_simulation/reserve_policy_v4/annual_matrix.csv'
with primary.open(encoding='utf-8-sig',newline='') as f:annual=list(csv.DictReader(f))
for region,voltage,expected in [('QX-00005','110','15.92'),('QX-00007','110','40.45'),('QX-00005','35','59.39')]:
 row=next(r for r in annual if r['study_region_id']==region and r['voltage_kv']==voltage)
 delta=(Decimal(row['rigid_cost_npv_10k_cny'])-Decimal(row['elastic_cost_npv_10k_cny']))/Decimal(row['rigid_cost_npv_10k_cny'])*100
 check('费用降幅独立重算 '+region,f'{delta:.2f}'==expected,str(delta))
unit={('QX-00005','110'):'邳州110 kV',('QX-00007','110'):'市区29站110 kV',('QX-00005','35'):'邳州35 kV（支撑层）'}
with (SRC/'表5-1.csv').open(encoding='utf-8-sig',newline='') as f:
 table=list(csv.reader(f))
for a in annual:
 row=next(r for r in table[1:] if r[0]==unit[(a['study_region_id'],a['voltage_kv'])] and r[1]==a['year'])
 expected=[f"{Decimal(a['reference_peak_mw']):.3f}",f"{Decimal(a['elastic_capacity_mva']):.1f}",f"{Decimal(a['elastic_clr']):.3f}",str(int(float(a['elastic_storage_modules'])))]
 check('推荐年度表对原路径 '+row[0]+a['year'],row[2:]==expected,{'table':row[2:],'primary':expected})
check('费用目标使用现值',all('2022至2041' in p.read_text() for p in [OUT/'04 第四章 弹性容载比优化模型.md',OUT/'05 第五章 优化结果分析.md']))
check('缺项未当真实零费用','损耗和其他项尚未评估，不将其真实费用填为零' in ch4)
check('完整标准公式与求解范围区分','不作为本报告已求得的承载力结果' in ch4)
summary={'passed':all(r['passed'] for r in results),'checks':len(results),'failed':[r for r in results if not r['passed']], 'formal_materials':len(index),'figures':sum(x['number'].startswith('图') for x in index),'tables':sum(x['number'].startswith('表') for x in index),'formulas':len(labels),'unique_admitted_records':len(record_ids),'narrative_decimal_occurrences_checked':len(ledger),'checks_detail':results,'limits':['核定文献限于本版实际引用内容；不宣称逐条核实原88条书目','科学模型及数据不变，只有两项已授权写作规则作为哈希变更例外','Markdown核验不替代Word分页或工程建设校核']}
(OUT/'检查证据/阶段2自动核验.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(OUT/'检查证据/正文数值定位.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='checks_detail'},ensure_ascii=False,indent=2))
raise SystemExit(0 if summary['passed'] else 1)
