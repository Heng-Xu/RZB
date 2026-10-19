"""无损压缩扩展原始库，逐字节校验后登记可移植来源。"""
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from extend_matrix_scenarios import TRIAL,SOURCE,REVIEW,write
from locked_parameter_results import sha


def raw_path():
    compressed=TRIAL/'原始求解记录.jsonl.gz'
    return compressed if compressed.exists() else TRIAL/'原始求解记录.jsonl'


def open_raw(path=None):
    path=path or raw_path()
    return gzip.open(path,'rt',encoding='utf-8') if path.suffix=='.gz' else path.open(encoding='utf-8')


def main():
    original=TRIAL/'原始求解记录.jsonl';compressed=original.with_suffix('.jsonl.gz')
    result=json.loads((REVIEW/'求解核验.json').read_text())
    assert result['设计节点数']==127578
    assert result['原始库SHA256']==sha(original)
    with original.open('rb') as source,compressed.open('wb') as output:
        with gzip.GzipFile(filename='',mode='wb',fileobj=output,mtime=0) as target:shutil.copyfileobj(source,target)
    digest=hashlib.sha256()
    with gzip.open(compressed,'rb') as source:
        while chunk:=source.read(1<<20):digest.update(chunk)
    assert digest.hexdigest()==sha(original),'原始库压缩前后不一致'
    write(SOURCE/'原始库无损归档.json',dict(状态='逐字节SHA256校验通过',
        压缩库=str(compressed.relative_to(ROOT)),压缩库SHA256=sha(compressed),
        解压后原始库SHA256=sha(original),原始字节数=original.stat().st_size,压缩字节数=compressed.stat().st_size,
        说明='Git保留无损压缩库；未压缩JSONL为可恢复的工作副本，未删除。'))
    provenance=json.loads((SOURCE/'计算来源.json').read_text())
    provenance.update(扩展原始库=str(compressed.relative_to(ROOT)),扩展原始库SHA256=sha(compressed),
                      解压后原始库SHA256=sha(original))
    write(SOURCE/'计算来源.json',provenance)
    print('无损原始库归档',compressed.stat().st_size,'/',original.stat().st_size,'字节')


if __name__=='__main__':main()
