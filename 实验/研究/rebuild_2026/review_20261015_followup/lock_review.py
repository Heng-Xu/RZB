"""独立冻结第二轮成果，不改写第一轮541项清单。"""
import argparse
import json
from pathlib import Path

from . import cases as c

MANIFEST=c.REVIEW/'本轮深化成果清单.json'


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    if a.write:
        assert not MANIFEST.exists(),'已有冻结清单，后继修订应单独登记'
        result=json.loads((c.REVIEW/'最终深化核验.json').read_text());assert result['verified']
        c.prior.dump(c.REVIEW/'成果复核记录.json',result)
        files=set()
        for root in [Path(__file__).parent,c.RAW,c.PUBLIC,c.SOURCE,c.REVIEW]:
            files.update(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                         and p.name not in ['本轮深化成果清单.json','最终深化核验.json'])
        c.prior.dump(MANIFEST,dict(状态='逐项核验通过',版本='20261015-model-review-02',
            文件SHA256={str(p.relative_to(c.ROOT)):c.prior.sha(p) for p in sorted(files)}))
    record=json.loads(MANIFEST.read_text());assert record['状态']=='逐项核验通过'
    for name,digest in record['文件SHA256'].items():
        path=c.ROOT/name;assert path.is_file() and c.prior.sha(path)==digest,'深化成果已变化：'+name
    print('VERIFIED_FOLLOWUP_ARTIFACTS',len(record['文件SHA256']))


if __name__=='__main__':main()
