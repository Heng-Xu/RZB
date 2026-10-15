"""冻结本轮模型、原始解、来源和交付文件，后续检查逐项验证。"""
import argparse
import json
from pathlib import Path

from . import cases

MANIFEST=cases.REVIEW/'本轮成果清单.json'


def paths():
    roots=[Path(__file__).parent,cases.OUT.parent,cases.PUBLIC,cases.SOURCE,cases.REVIEW/'规范核读']
    selected=set()
    for root in roots:
        selected.update(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for name in ['统计核验.json','转供调度核验.json','矩阵端点独立LP.json','工作簿逐格核验.json','成果复核记录.json']:
        selected.add(cases.REVIEW/name)
    return sorted(selected)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    if args.write:
        assert not MANIFEST.exists(),'成果清单已存在；后续修订须建立独立后继记录'
        checked=json.loads((cases.REVIEW/'最终模型核验.json').read_text());assert checked['verified']
        cases.dump(cases.REVIEW/'成果复核记录.json',checked)
        hashes={str(p.relative_to(cases.ROOT)):cases.sha(p) for p in paths()}
        cases.dump(MANIFEST,dict(状态='逐项核验通过',版本='20261015-model-review-01',
            正式报告数据='保留20261014初步定档，本清单为独立模型复核成果',文件SHA256=hashes))
    record=json.loads(MANIFEST.read_text());assert record['状态']=='逐项核验通过'
    for name,digest in record['文件SHA256'].items():
        path=cases.ROOT/name
        assert path.is_file() and cases.sha(path)==digest,'本轮成果已变化：'+name
    print('VERIFIED_REVIEW_ARTIFACTS',len(record['文件SHA256']))


if __name__=='__main__':main()
