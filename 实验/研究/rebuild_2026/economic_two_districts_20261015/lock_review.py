"""冻结用户选定经济主方案及新增两地区、两起点结果。"""
import argparse
import json
from pathlib import Path

from . import model as m

MANIFEST=m.REVIEW/'双区县经济方案成果清单.json'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');a=parser.parse_args()
    if a.write:
        assert not MANIFEST.exists(),'后继调整须单独登记'
        result=json.loads((m.REVIEW/'最终经济方案核验.json').read_text());assert result['verified']
        m.old.dump(m.REVIEW/'成果复核记录.json',result);files=set()
        for root in [Path(__file__).parent,m.RAW,m.PUBLIC,m.REVIEW,m.SOURCE]:
            files.update(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                and p.name not in [MANIFEST.name,'最终经济方案核验.json'])
        m.old.dump(MANIFEST,dict(状态='逐项核验通过',版本='20261015-two-districts-economic',
            文件SHA256={str(p.relative_to(m.ROOT)):m.old.sha(p) for p in sorted(files)}))
    record=json.loads(MANIFEST.read_text());assert record['状态']=='逐项核验通过'
    for name,digest in record['文件SHA256'].items():assert m.old.sha(m.ROOT/name)==digest,'经济方案成果已变化：'+name
    print('VERIFIED_TWO_DISTRICTS_ARTIFACTS',len(record['文件SHA256']))


if __name__=='__main__':main()
