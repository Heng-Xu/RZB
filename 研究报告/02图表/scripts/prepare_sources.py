"""只读核验冻结来源并提取准入数据；不绘图、不求解。"""
from pathlib import Path
import json,hashlib,csv,collections
import openpyxl
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'研究报告/02图表/source_data'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False))
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 original=ROOT/'研究报告/00审查/data_source.json';j=json.loads(original.read_text());allowed=set(j['admitted_record_ids']);rr=[r for r in j['records'] if r['id'] in allowed]
 frozen=json.loads((ROOT/'研究报告/00审查/证据/阶段0冻结清单.json').read_text());manifest={r['path']:r['sha256'] for r in frozen['files']}
 checks=[]
 sources=collections.defaultdict(list)
 for r in rr:sources[r['source']].append(r)
 for source,records in sources.items():
  p=ROOT/source;actual=sha(p);expected={r['source_sha256'] for r in records};assert expected=={actual},(source,expected,actual)
  checks.append({'source':source,'sha256':actual,'admitted_records':len(records),'passed':True})
 w=openpyxl.load_workbook(ROOT/'研究报告/00审查/最终数据字典.xlsx',read_only=True,data_only=True)
 cells={r[0]:r for r in list(w['报告准入数据'].values)[1:]};assert set(cells)==allowed
 for r in rr:
  a,b=cells[r['id']][3],r['value']
  assert (abs(a-b)<=1e-12*max(1,abs(b)) if isinstance(a,(float,int)) and isinstance(b,(float,int)) else a==b),r['id']
  assert cells[r['id']][5]==r['source'],r['id']
 extras=['研究报告/01研究推荐/研究推荐数据.json','研究报告/01研究推荐/区县口径更新说明.md','研究报告/00审查/最终模型说明.md','研究报告/00审查/成本模型说明.md','研究报告/00审查/公式与术语审查.md','研究报告/00审查/结果冻结报告.md']
 for source in extras:
  p=ROOT/source;actual=sha(p);assert source in manifest and manifest[source]==actual,(source,'freeze mismatch')
  checks.append({'source':source,'sha256':actual,'passed':True})
 update=json.loads((ROOT/extras[0]).read_text())
 for x in update['source_hashes']:
  assert sha(ROOT/x['file'])==x['sha256'],x['file']
 numeric_sources=collections.defaultdict(dict)
 for source,records in sources.items():
  if not source.endswith('.csv'):continue
  rows=list(csv.DictReader((ROOT/source).open(encoding='utf-8-sig')))
  for r in records:
   import re
   m=re.search(r'CSV物理行(\d+)；字段(.+)',r['source_location'])
   if not m:continue
   idx=int(m[1])-2;field=m[2];raw=rows[idx][field];v=r['value']
   if isinstance(v,(int,float)):assert abs(float(raw)-v)<=1e-10*max(1,abs(v)),r['id']
   elif v is None:assert raw in ('','nan','NaN'),r['id']
   else:assert str(v)==raw,r['id']
   numeric_sources[source].setdefault(str(idx),{})[field]={'value':v,'record_id':r['id'],'source_location':r['source_location'],'unit':r['unit'],'formula':r['formula'],'limitation':r['limitation']}
 write('准入记录快照.json',{'origin':str(original.relative_to(ROOT)),'origin_sha256':sha(original),'records':rr,'region_mapping':j['region_mapping']})
 write('准入CSV字段定位.json',numeric_sources)
 write('区县口径展示快照.json',{'source':extras[0],'sha256':sha(ROOT/extras[0]),'data':update})
 write('来源核验.json',{'status':'PASS','dictionary_records':len(cells),'json_records':len(rr),'source_checks':checks,'numeric_policy':'绘图所用数值必须对应准入编号或阶段0已登记的区县口径更新；不调用优化模型','model_or_results_modified':False})
 print(json.dumps({'status':'PASS','admitted_records':len(rr),'verified_sources':len(checks)},ensure_ascii=False))
if __name__=='__main__':main()
