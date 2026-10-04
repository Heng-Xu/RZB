"""复核保留方案的输入、约束、负荷守恒及费用，不重新求解。"""
import importlib.util, json, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('current_start',HERE/'统一起点情景.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.reg.input_data=module.inputs;module.audit.input_data=module.inputs
data=ROOT/'研究报告/01研究推荐/当前版/统一起点基准'
results={region:module.audit.audit(data/region) for region in ('pizhou','city')}
module.source_check([data/'pizhou',data/'city'],HERE/'统一起点输入核对.json')
sources=json.loads((ROOT/'研究报告/数据来源/当前版/原始文件登记.json').read_text())
for item in sources:
 path=ROOT/item['文件'];assert path.stat().st_size==item['字节数']
 assert hashlib.sha256(path.read_bytes()).hexdigest()==item['SHA256'],item['文件']
report={'状态':'通过','模型':results,'原始文件校验数量':len(sources)}
(HERE/'模型基准校核.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('保留方案约束与费用复核通过；原始文件校验',len(sources))
