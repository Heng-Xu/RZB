"""核对当前矩阵分区报告的逐段复核、原件继承与三阶段交付证据。"""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'研究报告/05_review/当前版/1016矩阵分区与文献补充'
DETAILS=ROOT/'研究报告/05_review/当前版/1017细节表述修正'
RELEASE=DETAILS/'交付登记.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_matrix_release():
 r=json.loads((AUDIT/'交付登记.json').read_text());assert r['状态']=='三阶段核验及逐段复核通过'
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
def verify():
 if not RELEASE.exists():return verify_matrix_release()
 r=json.loads(RELEASE.read_text());assert r['状态']=='三阶段核验及逐段复核通过'
 from report_work_context import verify_context,maintenance_original
 context=verify_context(ROOT,RELEASE,r['当前文件SHA256'])
 for name,digest in r['当前文件SHA256'].items():
  original=ROOT/context[name]['原件归档'] if name in context else ROOT/name
  assert sha(original)==digest,'本轮交付文件变化，须重新核验：'+name
 previous=DETAILS/'上一版交付衔接.json';link=json.loads(previous.read_text())
 parent=ROOT/link['父交付登记'];assert sha(parent)==link['父交付登记SHA256']
 parent_record=json.loads(parent.read_text())
 assert set(link['原件映射'])==set(parent_record['当前文件SHA256'])
 for name,digest in parent_record['当前文件SHA256'].items():
  original=maintenance_original(ROOT,name,ROOT/link['原件映射'][name],digest)
  assert sha(original)==digest,'上一版交付原件不一致：'+name
  if original!=ROOT/link['原件映射'][name]:
   r['修改原件'].setdefault(name,dict(原SHA256=digest,原件归档=str(original.relative_to(ROOT))))
 before=json.loads((DETAILS/'修前文件登记.json').read_text())
 for name,digest in before.items():
  assert sha(DETAILS/'修前快照'/name)==digest,'修前快照不一致：'+name
 from report_prose_review import collect
 current=collect(ROOT,include_discussion=False)
 reviewed=json.loads((DETAILS/'正文逐段复核.json').read_text())['正文段落']
 assert len(current)==len(reviewed)
 for old,new in zip(reviewed,current):
  assert old['位置']==new['位置'] and old['SHA256']==new['SHA256'],'逐段复核过期：'+new['位置']
  assert old['复核结论']=='通过' and old['理由']
 for p in sorted((ROOT/'研究报告/03_MD/当前版').glob('0[1-6] *.md')):
  a=(DETAILS/'修前快照'/p.relative_to(ROOT)).read_text()
  assert re.findall(r'^#{1,4} .+',a,re.M)==re.findall(r'^#{1,4} .+',p.read_text(),re.M),'章节结构变化：'+p.name
 for name in ['生成段落.json']:
  rel=Path('研究报告/02图表/当前版')/name
  assert (ROOT/rel).read_bytes()==(DETAILS/'修前快照'/rel).read_bytes(),'逐站生成段落被改变'
 rel=Path('研究报告/02图表/当前版/计算表.json')
 a=json.loads((DETAILS/'修前快照'/rel).read_text());b=json.loads((ROOT/rel).read_text())
 assert set(a)==set(b)
 assert {k for k in a if a[k]!=b[k]}=={'storage_duration_cost','new_case_assumptions','economic_assumptions'},'非授权计算表发生变化'
 from report_storage_display import storage_duration_table
 assert b['storage_duration_cost']==storage_duration_table()
 from verify_report_review import formula_text
 word=Path('研究报告/04_word/研究报告终稿.docx')
 assert formula_text(ROOT/word)==formula_text(DETAILS/'修前快照'/word),'27个原生公式内容改变'
 facts=json.loads((DETAILS/'储能系数原文核读.json').read_text());assert facts['状态']=='通过'
 assert sha(ROOT/facts['原文'])==facts['原文SHA256']
 proof=json.loads((DETAILS/'WPS版面核验.json').read_text());assert proof['状态']=='通过'
 for key,digest in [('DOCX','DOCX_SHA256'),('PDF','PDF_SHA256')]:assert sha(ROOT/proof[key])==proof[digest]
 data=json.loads((DETAILS/'当前报告数据核验.json').read_text())
 assert data['状态']=='通过' and data['WordSHA256']==proof['DOCX_SHA256']
 assert data['采用结果']['静态校核工况']==30336 and data['逐站分析']==46
 assert r['文字复核']['规则扫描代替逐段判断'] is False
 from report_citations import verify as verify_citations
 citations=verify_citations(ROOT,'final')
 print(json.dumps(dict(状态='通过',正文逐段复核=len(current),本次有效引文=citations['文献数'],
  继承原件=len(link['原件映射']),独立公式='27式内容一致',计算结果='冻结成果与46站分析保持，储能表按完整精度复算'),ensure_ascii=False))
 return r

if __name__=='__main__':verify()
