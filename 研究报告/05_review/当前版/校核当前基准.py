"""复核保留方案的输入、约束、负荷守恒及费用，不重新求解。"""
import importlib.util, json, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('current_start',HERE/'统一起点情景.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.apply_current_economics()
module.reg.input_data=module.inputs;module.audit.input_data=module.inputs
data=ROOT/'研究报告/01研究推荐/当前版/统一起点基准'
results={region:module.audit.audit(data/region) for region in ('pizhou','city')}
module.source_check([data/'pizhou',data/'city'],HERE/'统一起点输入核对.json')
module.source_check([data/'pizhou',data/'city'],data/'source_audit.json')
from 实验.研究.rebuild_2026 import joint_shared_measure_audit as portfolio_audit
portfolio_audit.cost_factors=module.cost_factors
joint_check=portfolio_audit.audit(data)
(HERE/'联合方案复核.json').write_text(json.dumps(joint_check,ensure_ascii=False,indent=2))
sources=json.loads((ROOT/'研究报告/数据来源/当前版/原始文件登记.json').read_text())
for item in sources:
 path=ROOT/item['文件'];assert path.stat().st_size==item['字节数']
 assert hashlib.sha256(path.read_bytes()).hexdigest()==item['SHA256'],item['文件']
report={'状态':'通过','模型':results,'联合方案':'通过','原始文件校验数量':len(sources)}
(HERE/'模型基准校核.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('保留方案约束与费用复核通过；原始文件校验',len(sources))
