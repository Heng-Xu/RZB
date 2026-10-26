"""案例展示年度：只截取已锁定序列，不改变模型、年度配置或现金流截止年。"""
from copy import deepcopy
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def end_year(root=ROOT):
    return int(json.loads((root/'tools/report_policy.json').read_text())
               .get('case_display', {}).get('end_year', 2035))


def through_year(plan, last):
    result = deepcopy(plan)
    result['annual'] = [a for a in result['annual'] if a['year'] <= last]
    assert result['annual'][-1]['year'] == last
    result['cost_npv_10k'] = sum(a['added_lifecycle_npv_10k'] for a in result['annual'])
    return result
