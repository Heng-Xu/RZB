"""核对相邻同区间合并的完整性、原始端点及两地区案例保持。"""
from pathlib import Path
import json,itertools,hashlib,math,collections
HERE=Path(__file__).resolve().parent;R=HERE.parents[1];D=R/'01研究推荐/当前版';O=HERE/'1008线路经济替代修订'
def read(p):return json.loads(p.read_text())
def interval(vals):return f'{math.floor((min(vals)+1e-10)*100)/100:.2f}～{math.ceil((max(vals)-1e-10)*100)/100:.2f}'
def main():
 raw=read(D/'外推逐点结果.json');formal=read(D/'分类容载比推荐区间.json');mapping=read(O/'区间合并追溯.json');base=read(O/'合并前1296单元.json')
 assert len(formal)==len(mapping) and len(base)==1296
 lookup={(r['线路类型'],r['供电区域'],r['负荷分布'],tuple(r['参数索引'])):r for r in base}
 seen=[];allpoints=set()
 for entry,m in zip(formal,mapping):
  group=(entry['线路类型'],{'A类':'A','B/C类':'BC'}[entry['供电区域类别']],{1.:'较均匀',1.15:'偏集中'}[entry['负荷分散系数']])
  expected=set(itertools.product(*(range(a,b+1) for a,b in m['参数索引范围'])))
  assert expected=={tuple(c) for c in m['原始单元']},'合并范围含空洞'
  source=[lookup[(*group,c)] for c in expected]
  assert {x['容载比推荐区间'] for x in source}=={entry['容载比推荐区间']},'不同推荐区间被混并'
  points=set(i for x in source for i in x['点索引']);assert points==set(m['点索引'])
  vals=[raw[i]['推荐容载比'] for i in points]
  assert min(vals)==entry['容载比最小值'] and max(vals)==entry['容载比最大值']
  assert interval(vals)==entry['容载比推荐区间'] and len(points)==entry['计算点数']
  seen.extend((*group,c) for c in expected);allpoints.update(points)
 assert len(seen)==len(set(seen))==1296 and len(allpoints)==25200
 baseline=read(O/'案例保持基线.json')
 for p,h in baseline.items():assert hashlib.sha256((R.parent/p).read_bytes()).hexdigest()==h,p
 # Exactly the original input grid: no reranked, omitted or newly invented data points.
 old=read(HERE/'1007术语再审与WPS兼容/计算数据修改前哈希.json')
 original=__import__('subprocess').check_output(['git','show','80184d5:研究报告/01研究推荐/当前版/外推逐点结果.json'],cwd=R.parent)
 oldrows=json.loads(original)
 keys=['装机渗透率','电量渗透率估计','年负荷平均增长率','95%峰值持续时间h','供电区域','负荷分布','线路类型','电缆长度占比','线路价格倍数','储能价格倍数','主变线路成本比','主变储能成本比_3h','基期容载比']
 assert len(oldrows)==len(raw)
 assert all(r['初始转供率']==0 for r in raw),'专项外推应无既有联络剩余可用能力'
 for a,b in zip(oldrows,raw):assert all(a[k]==b[k] for k in keys)
 result={'状态':'通过','外推唯一改变的输入字段':'初始转供率改为0，对应既有联络无剩余可用能力的专项条件','原始输入逐项保持':len(raw)*len(keys),'原始情景':len(raw),'基础单元':len(base),'合并推荐行':len(formal),'覆盖计算点':len(allpoints),'区间合并':'仅相邻同显示区间；参数组合无空洞、基础单元无重复或遗漏、原精度端点完整保留','两地区案例保持文件':len(baseline)}
 (O/'推荐区间及案例保持复核.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(result)
if __name__=='__main__':main()
