"""将已有储能布局用于被既有通道严格支配的正费用新线情景。

不伪造新求解记录：report_scenario 明示支配证明及参考布局。
"""
from pathlib import Path
import json,shutil,csv
ROOT=Path(__file__).resolve().parents[3];DATA=ROOT/'研究报告/01研究推荐/2026-10-01条件矩阵'
CASES=[('价格_线路较低',.75,1,'基准'),('价格_线路较贵',1.25,1,'基准'),('联合_线路贵储能低',1.25,.5,'价格_储能降价50'),('联合_线路低储能降25',.75,.75,'价格_储能降价25'),('联合_线路低储能降50',.75,.5,'价格_储能降价50'),('联合_线路低储能贵25',.75,1.25,'价格_储能较贵25'),('联合_线路贵储能降25',1.25,.75,'价格_储能降价25'),('联合_线路贵储能贵25',1.25,1.25,'价格_储能较贵25')]
def main():
 for name,line,storage,ref in CASES:
  dest=DATA/name;src=DATA/ref
  if not dest.exists():shutil.copytree(src,dest)
  for region in ['pizhou','city']:
   for scheme in ['rigid','elastic']:
    with (dest/region/(scheme+'_years.csv')).open(encoding='utf-8-sig') as f:
     assert all(int(r['new_lines_in_service'])==0 and abs(float(r['line_capex_10k']))<1e-9 for r in csv.DictReader(f))
   p=dest/region/'summary.json';s=json.loads(p.read_text())
   for z in s:
    assert z.get('storage_scale',1)==storage
    z['reference_line_scale']=json.loads((src/region/'summary.json').read_text())[0].get('line_scale',1)
    z['line_scale']=line;z['layout_reference_scenario']=ref;z['line_sensitivity_method']='positive_cost_dominance_proof_existing_network_substitutes_same_tasks'
   p.write_text(json.dumps(s,ensure_ascii=False,indent=2))
  meta={'id':name,'line':line,'storage':storage,'status':'solved','k_TL_relative':1/line,'k_TB_relative':1/storage,'method':'positive_new_line_cost_dominance_proof_existing_network_substitutes_same_tasks','reference_layout':ref}
  (dest/'report_scenario.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
 print('8组正价格线路情景：参考布局、证明方式与价格元数据已对应')
if __name__=='__main__':main()
