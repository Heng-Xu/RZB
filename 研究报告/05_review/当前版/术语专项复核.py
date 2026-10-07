"""检查当前交付的名称、逐表登记、公式索引与原始数值保持情况。"""
from pathlib import Path
import hashlib,json,re
import numpy as np
from docx import Document

HERE=Path(__file__).resolve().parent
R=HERE.parents[1]
AUDIT=HERE/'1007术语再审与WPS兼容'
REG=HERE/'1007术语及分类推荐专项修订'
def read(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=(R/'03_MD/当前版/研究报告装配稿.md').read_text()
 doc=Document(R/'04_word/研究报告终稿.docx')
 text='\n'.join(n.text or '' for n in doc._element.xpath('.//w:t'))
 forbidden=['容量负荷比','容量／负荷比','月度容载比','被解释指标','峰段持续时间','峰段/h','弹性费用降幅','口径','公用公用主变','储能储能单位']
 for word in forbidden:
  assert word not in source and word not in text,word
 for word in ['容载比（月度分析值）','分布式电源装机渗透率','分布式电源电量渗透率','主变与线路单位功率投资比','指标一','指标二']:
  assert word in source,word
 registry=read(REG/'术语登记.json');glossary=(R/'核心语料与审查_20261006/02_核心术语与语料依据.md').read_text()
 for term in registry:assert term['统一名称'] in glossary,term['统一名称']
 all_tables=list(re.finditer(r'^(表\d+-\d+[^\n]+)\n\n(\|[^\n]+)',source,re.M))
 coverage=read(AUDIT/'全部数据表逐列术语核对.json')
 assert len(all_tables)==len(coverage)==120
 for table,row in zip(all_tables,coverage):
  assert table[1]==row['表题']
  assert [s.strip() for s in table[2].strip('|').split('|')]==[c['表头'] for c in row['列']]
  for col in row['列']:
   assert col['对应统一术语'] or col['性质']=='标识、分类或说明列',col
 equations=read(R/'02图表/当前版/公式/公式清单.json');index=read(REG/'公式逐式登记.json')
 assert len(equations)==len(index)==35
 for actual,registered in zip(equations,index):
  assert actual['number']==registered['编号'] and actual['tex'].strip()==registered['公式']
 prior=read(AUDIT/'计算数据修改前哈希.json')
 assert all(digest(R.parent/file)==expected for file,expected in prior.items())
 raw=read(R/'01研究推荐/当前版/外推逐点结果.json')
 x=np.array([r['装机渗透率'] for r in raw]);y=np.array([r['电量渗透率估计'] for r in raw]);factor=y[x>0]/x[x>0]
 assert np.ptp(factor)<1e-12 and np.all(y[x==0]==0)
 result={'状态':'通过','统一术语登记':len(registry),'逐表覆盖':len(coverage),'独立公式索引':len(index),
  '禁用及混用词检查':forbidden,'原始计算数据文件保持':len(prior),'外推情景':len(raw),
  '两类渗透率相关系数':float(np.corrcoef(x,y)[0,1]),'固定换算因子':float(factor[0]),
  'WordSHA256':digest(R/'04_word/研究报告终稿.docx'),'装配稿SHA256':digest(R/'03_MD/当前版/研究报告装配稿.md'),
  '来源说明':'容载比等采用导则定义；月度分析值、费用分项和换算关系据本文数据与计算定义，未冒称标准新增指标。'}
 (AUDIT/'专项术语审核.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({k:result[k] for k in ['状态','统一术语登记','逐表覆盖','独立公式索引','原始计算数据文件保持']},ensure_ascii=False))
if __name__=='__main__':main()
