"""核对当前矩阵分区报告的逐段复核、原件继承与三阶段交付证据。"""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'研究报告/05_review/当前版/1016矩阵分区与文献补充'
RELEASE=AUDIT/'交付登记.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 r=json.loads(RELEASE.read_text());assert r['状态']=='三阶段核验及逐段复核通过'
 for name,digest in r['当前文件SHA256'].items():
  assert sha(ROOT/name)==digest,'本轮交付文件变化，须重新核验：'+name
 before=json.loads((AUDIT/'修前文件登记.json').read_text())
 for name,row in r['本轮修改原件'].items():
  assert row['原SHA256']==before[name]
  assert sha(ROOT/row['原件归档'])==row['原SHA256'],'修前原件变化：'+name
 # 历史引文核读保持其原始资料及逐条内容，本轮新增条款核读单独登记。
 prior=ROOT/'研究报告/05_review/当前版/1014事实与文字复核/引文依据核读登记.json'
 assert sha(prior)==r['承继引文核读SHA256']
 facts=json.loads(prior.read_text())['记录'];assert len(facts)==95
 for row in facts:
  for k,dk in [('审定依据','SHA256'),('原始文件','原始文件SHA256')]:
   if dk in row:assert sha(ROOT/row[k])==row[dk],'引文原始依据变化：'+row[k]
 supplemental=json.loads((AUDIT/'新增论述原文核读.json').read_text())
 assert supplemental['状态']=='通过' and len(supplemental['记录'])==14
 for row in supplemental['记录']:
  assert sha(ROOT/row['原文'])==row['SHA256'],'本轮新增论述原文变化：'+row['原文']
 from report_prose_review import collect
 current=collect(ROOT,include_discussion=False)
 reviewed=json.loads((AUDIT/'正文逐段复核.json').read_text())['正文段落']
 assert len(reviewed)==len(current)
 for old,new in zip(reviewed,current):
  assert old['位置']==new['位置'] and old['SHA256']==new['SHA256'],'逐段复核过期：'+new['位置']
  assert old['复核结论'] and old['理由']
 # 按用户要求删除原5.6.8及5.6.10，原5.6.9顺延；其余标题保留。
 for p in sorted((ROOT/'研究报告/03_MD/当前版').glob('0[1-6] *.md')):
  old=(AUDIT/'修前快照'/p.relative_to(ROOT)).read_text()
  a=re.findall(r'^#{1,3} .+',old,re.M);b=re.findall(r'^#{1,3} .+',p.read_text(),re.M)
  removed={'### 5.6.8 储能持续时间与有效功率配置','### 5.6.10 电量、峰段及相对投资条件下的配置'}
  renames={'### 5.6.9 负荷分散系数与局部高峰承载':'### 5.6.8 负荷分散系数与局部高峰承载'}
  assert [renames.get(x,x) for x in a if x not in removed]==b,'用户指定范围外的章节结构变化：'+p.name
 source=(ROOT/'研究报告/03_MD/当前版/研究报告装配稿.md').read_text()
 assert len(re.findall(r'^#### .*规划分析$',source,re.M))==46
 proof=json.loads((AUDIT/'WPS版面核验.json').read_text());assert proof['状态']=='通过'
 for k,dk in [('PDF','PDF_SHA256'),('DOCX','DOCX_SHA256')]:assert sha(ROOT/proof[k])==proof[dk]
 data=json.loads((AUDIT/'当前报告数据核验.json').read_text());assert data['状态']=='通过' and data['WordSHA256']==proof['DOCX_SHA256']
 assert data['采用结果']['静态校核工况']==30336 and data['逐站分析']==46
 assert data['矩阵与图文扩充']['矩阵单元']==432
 assert proof['六章正文页数']>=157 and proof['完整矩阵表数']==9
 assert r['文字复核']['规则扫描代替逐段判断'] is False
 previous=ROOT/'研究报告/05_review/当前版/1016图文扩充与术语复核/交付登记.json'
 assert sha(previous)==r['承继上一版交付登记SHA256']
 old_release=json.loads(previous.read_text())
 supplement=json.loads((AUDIT/'上一版交付衔接.json').read_text())
 for name,digest in old_release['当前文件SHA256'].items():
  candidate=ROOT/supplement[name]
  assert sha(candidate)==digest,'上一版交付继承不一致：'+name
 from verify_report_expansion import verify as verify_expansion
 verify_expansion()
 from report_citations import verify as verify_citations
 citations=verify_citations(ROOT,'final')
 print(json.dumps(dict(状态='通过',引文依据承继=len(facts),本次有效引文=citations['文献数'],正文逐段复核=len(current),逐站分析=46,
     章节结构='六章保留；按授权删两小节并顺延一节',本轮事实核验='8组冻结数据、432区间单元、完整响应序列及新增引文论述'),ensure_ascii=False))
 return r
if __name__=='__main__':verify()
