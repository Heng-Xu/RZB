"""独立冻结增容替代推荐结果，不改写前两轮模型清单。"""
import argparse
import json
from pathlib import Path

from . import model as m

MANIFEST=m.REVIEW/'本轮推荐成果清单.json'


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    if a.write:
        assert not MANIFEST.exists(),'已有冻结清单，后继修订应另行登记'
        result=json.loads((m.REVIEW/'最终推荐核验.json').read_text());assert result['verified']
        m.old.dump(m.REVIEW/'成果复核记录.json',result)
        files=set()
        for root in [Path(__file__).parent,m.RAW,m.PUBLIC,m.SOURCE,m.REVIEW]:
            files.update(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                and p.name not in ['本轮推荐成果清单.json','最终推荐核验.json'])
        m.old.dump(MANIFEST,dict(状态='逐项核验通过',版本='20261015-capacity-first-recommendation',
            文件SHA256={str(p.relative_to(m.ROOT)):m.old.sha(p) for p in sorted(files)}))
    record=json.loads(MANIFEST.read_text());assert record['状态']=='逐项核验通过'
    for name,digest in record['文件SHA256'].items():
        path=m.ROOT/name;assert path.is_file() and m.old.sha(path)==digest,'推荐成果已变化：'+name
    print('VERIFIED_RECOMMENDATION_ARTIFACTS',len(record['文件SHA256']))


if __name__=='__main__':main()
