"""独立冻结本轮八组静态联合替代方案。"""
import argparse
import json
from pathlib import Path

from . import model as m

MANIFEST=m.REVIEW/'静态联合替代成果清单.json'


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    if args.write:
        assert not MANIFEST.exists()
        check=json.loads((m.REVIEW/'最终核验.json').read_text());assert check['verified'] and check['schemes']==8 and check['full_lp_recomputed']
        m.old.dump(m.REVIEW/'完整复核记录.json',check)
        paths=set()
        for root in [Path(__file__).parent,m.RAW,m.PUBLIC,m.REVIEW,m.SOURCE]:
            paths.update(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                and p.name not in [MANIFEST.name,'最终核验.json'])
        m.old.dump(MANIFEST,dict(状态='八组逐项核验通过',版本='20261015-static-joint',
            文件SHA256={str(p.relative_to(m.ROOT)):m.old.sha(p) for p in sorted(paths)}))
    record=json.loads(MANIFEST.read_text());assert record['状态']=='八组逐项核验通过'
    for name,digest in record['文件SHA256'].items():assert m.old.sha(m.ROOT/name)==digest,'本轮成果变化：'+name
    print('VERIFIED_STATIC_JOINT_ARTIFACTS',len(record['文件SHA256']))


if __name__=='__main__':main()
