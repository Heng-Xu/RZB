"""沿用已核验模型，补算负荷分散系数1.00和1.15；原主网格保持。"""
from pathlib import Path
import sys,json,inspect
from concurrent.futures import ProcessPoolExecutor
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from 实验.研究.rebuild_2026.matrix_20261010 import run as m
# 等价索引替代逐行扫描稀疏系数，提高模型创建速度。
s=inspect.getsource(m.solve)
s=s.replace('    for r in range(len(m.constraint_lower)):\n        terms={c:v for rr,c,v in m.entries if rr==r}', '    by_row={}\n    for rr,c,v in m.entries: by_row.setdefault(rr,{})[c]=v\n    for r in range(len(m.constraint_lower)):\n        terms=by_row.get(r,{})')
exec(s,m.__dict__)
OUT=ROOT/'研究报告/试算/20261010_负荷分散系数扩展';OUT.mkdir(exist_ok=True)
def one(p):
 r=m.solve(p);r['extension_id']=p['extension_id'];return r
if __name__=='__main__':
 cases=[{**p,'diversity':kd,'extension_id':i+4200*j,'seconds':30,'sample_set':'diversity_extension'} for j,kd in enumerate([1.,1.15]) for i,p in enumerate(m.task_cases('main'))]
 path=OUT/'extension.jsonl';done={json.loads(x)['extension_id'] for x in path.read_text().splitlines()} if path.exists() else set()
 cases=[p for p in cases if p['extension_id'] not in done]
 with path.open('a') as f,ProcessPoolExecutor(max_workers=10) as pool:
  for i,r in enumerate(pool.map(one,cases,chunksize=1),1):
   f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush()
   if i%100==0:print(i,len(cases),r['verified'],flush=True)
 print('DONE',flush=True)
