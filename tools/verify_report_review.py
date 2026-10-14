"""核对事实与文字审阅记录对应当前源稿、成果和原始依据。"""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'研究报告/05_review/当前版/1014事实与文字复核'
AUDIT=ROOT/'研究报告/05_review/当前版/1014十三选五与报告修订'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def formula_text(path):
 with ZipFile(path) as z:r=E.fromstring(z.read('word/document.xml'))
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
 return [''.join(t.xpath('.//m:t/text()',namespaces=ns)) for t in r.xpath('.//w:tbl[w:tblPr/w:tblCaption[@w:val="ReportEquation"]]//m:oMath',namespaces=ns)]
def main():
 record=json.loads((AUDIT/'复核完成登记.json').read_text());assert record['状态']=='通过'
 for name,digest in record['当前文件SHA256'].items():assert sha(ROOT/name)==digest,'审阅记录已过期，须核对变化后重新登记: '+name
 assert sha(PRIOR/'引文依据核读登记.json')==record['事实核验']['既有依据登记SHA256']
 facts=json.loads((PRIOR/'引文依据核读登记.json').read_text())['记录'];assert len(facts)==95
 for row in facts:
  for key,dk in [('审定依据','SHA256'),('原始文件','原始文件SHA256')]:
   if dk in row:assert sha(ROOT/row[key])==row[dk],f'依据发生变化: [{row["原编号"]}] '+row[key]
 snapshot=PRIOR/'修前快照';table=Path('研究报告/02图表/当前版/计算表.json')
 before_tables=json.loads((snapshot/table).read_text());after_tables=json.loads((ROOT/table).read_text())
 from report_parameter_selection import assets
 parameter_tables=assets()
 allowed=set(parameter_tables)|{f'current_matrix_{i}_{k:.2f}' for i in range(3) for k in [1.,1.1,1.15]}
 assert set(before_tables)<=set(after_tables),'原有计算结果被删除'
 for key,value in before_tables.items():
  if key not in allowed:assert after_tables[key]==value,'非本轮参数表发生变化: '+key
 assert set(after_tables)-set(before_tables)<=allowed|{'five_parameter_vif'},'出现未经登记的新增计算表'
 for key,value in parameter_tables.items():assert after_tables[key]==value,'参数展示未对应复算结果: '+key
 source=(ROOT/'研究报告/03_MD/当前版/研究报告装配稿.md').read_text()
 assert '[[TABLE:five_parameter_vif]]' not in source and '方差膨胀因子' not in source and 'VIF' not in source
 selection=json.loads((AUDIT/'参数与矩阵独立核验.json').read_text())
 assert selection['状态']=='通过' and selection['第一层通过指标数']==9 and selection['推广矩阵单元数']==432
 for name,digest in selection['原始依据'].items():assert sha(ROOT/name)==digest,'筛选原始依据发生变化: '+name
 before=json.loads((snapshot/'研究报告/02图表/当前版/生成段落.json').read_text());after=json.loads((ROOT/'研究报告/02图表/当前版/生成段落.json').read_text())
 pattern=r'[+-]?\d+(?:\.\d+)?(?:\+\d+(?:\.\d+)?)*\s*(?:MVA|MW(?:h)?|%)'
 for key in ['restore_pizhou_profiles','restore_city_profiles']:
  assert sorted(re.findall(pattern,before[key]))==sorted(re.findall(pattern,after[key])),'逐站叙述数值变化: '+key
 doc=Path('研究报告/04_word/研究报告终稿.docx')
 assert len(formula_text(ROOT/doc))==27 and formula_text(ROOT/doc)==formula_text(snapshot/doc),'原生独立公式内容变化'
 assert record['文字复核']['规则扫描代替人工判断'] is False
 from report_prose_review import collect
 reviewed=json.loads((AUDIT/'正文复核定位.json').read_text())['正文段落'];current=collect(ROOT)
 assert len(reviewed)==len(current),'正文复核段落数已变化，须复核新增或删改内容'
 for old,new in zip(reviewed,current):
  assert old['位置']==new['位置'] and old['SHA256']==new['SHA256'],'正文逐段复核记录已过期: '+new['位置']
  assert old.get('复核结论') and old.get('理由'),'缺少逐段判断: '+new['位置']
 for path in [AUDIT/'研究报告版面/WPS版面核验.json',AUDIT/'讨论稿/WPS版面核验.json']:
  proof=json.loads(path.read_text());assert proof['状态']=='通过'
  assert sha(ROOT/proof['PDF'])==proof['PDF_SHA256']
  assert sha(ROOT/proof['DOCX'])==proof['DOCX_SHA256']
 print(json.dumps({'状态':'通过','引文依据':len(facts),'正文复核段落':len(current),'计算表':'参数展示对应复算；其他结果原值一致','逐站叙述数字':'原值一致','独立公式':'27式内容一致','稿件与复核记录':'哈希一致'},ensure_ascii=False))
if __name__=='__main__':main()
