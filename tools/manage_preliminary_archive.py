"""按已审阅清单备份并移出无关历史文件；不处理原始资料和活动依赖。"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT/'研究报告/05_review/当前版/1014初步定档与表述约束'
BACKUP = ROOT/'研究报告/试算/历史本地备份/20261014_初步定档清理.zip'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive():
    assert not BACKUP.exists(), '备份已存在，禁止覆盖'
    plan = json.loads((AUDIT/'清理候选清单.json').read_text())
    files = [ROOT/p for p in plan['文件']]
    dependency = json.loads((AUDIT/'当前复现读取依赖.json').read_text())['文件']
    assert not set(plan['文件']) & set(dependency)
    protected = {}
    for directory in ['实验/研究', '参考政策', '参考文献', '课题前期资料', '课题规划',
                      '研究报告/甲方反馈', '研究报告/数据来源']:
        for p in (ROOT/directory).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc', '.log']:
                protected[str(p.relative_to(ROOT))] = sha(p)
    assert not set(plan['文件']) & set(protected)
    manifest = [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in files]
    assert all(p.is_file() and not p.is_symlink() for p in files)
    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(BACKUP, 'w', ZIP_DEFLATED, compresslevel=6) as z:
        for p in files: z.write(p, str(p.relative_to(ROOT)))
    with ZipFile(BACKUP) as z:
        assert z.testzip() is None and len(z.namelist()) == len(manifest)
        for row in manifest:
            assert hashlib.sha256(z.read(row['path'])).hexdigest() == row['sha256'], row['path']
    record = {'状态': '备份和逐文件SHA256核验通过', '清理前Git提交': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        '本地备份': str(BACKUP.relative_to(ROOT)), '备份SHA256': sha(BACKUP),
        '备份字节': BACKUP.stat().st_size, '文件数': len(manifest),
        '原文件字节': sum(r['bytes'] for r in manifest), '文件': manifest,
        '保留资料与依赖SHA256': protected,
        '说明': '本地校验备份被Git忽略；文件清单与原Git历史保留，未重写历史。'}
    (AUDIT/'历史清理与保留登记.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    for row in manifest:
        p = ROOT/row['path']; assert sha(p) == row['sha256']; p.unlink()
    for directory in plan['条目']:
        p = ROOT/directory
        if p.is_dir():
            for child in sorted(p.rglob('*'), key=lambda p: len(p.parts), reverse=True):
                if child.is_dir() and not any(child.iterdir()): child.rmdir()
            if not any(p.iterdir()): p.rmdir()
    verify()


def verify():
    record = json.loads((AUDIT/'历史清理与保留登记.json').read_text())
    assert all(not (ROOT/r['path']).exists() for r in record['文件']), '已归档历史文件仍在活动目录'
    from report_source_lineage import preserved_original
    for name, digest in record['保留资料与依赖SHA256'].items():
        assert sha(preserved_original(ROOT,name,digest)) == digest, '原始资料或当前依赖发生变化: '+name
    if BACKUP.exists():
        assert sha(BACKUP) == record['备份SHA256']
    print(json.dumps({'状态': '通过', '归档移出文件': record['文件数'],
        '移出字节': record['原文件字节'], '保留原始资料及依赖': len(record['保留资料与依赖SHA256'])}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', action='store_true')
    args = parser.parse_args()
    archive() if args.archive else verify()
