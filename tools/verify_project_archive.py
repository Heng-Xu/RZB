"""核对项目历史归档的压缩包及逐文件摘要；只读，不恢复或覆盖活动文件。"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

ROOT = Path(__file__).resolve().parents[1]
RECORD = Path('docs/历史归档/20261020/归档清单.json')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def safe_name(name):
    path = PurePosixPath(name)
    assert not path.is_absolute() and '..' not in path.parts, name
    assert str(path) == name and name != '.', name
    return name


def verify(root=ROOT, check_preserved=False):
    record = json.loads((root / RECORD).read_text())
    archive = root / safe_name(record['归档包'])
    assert sha(archive) == record['归档包SHA256'], '归档包摘要不一致'
    rows = record['文件']
    names = [safe_name(row['path']) for row in rows]
    assert len(names) == len(set(names)) == record['文件数'], '归档条目重复或缺失'
    assert sum(row['bytes'] for row in rows) == record['原文件字节']
    expected = {row['path']: row for row in rows}
    seen = set()
    with tarfile.open(archive, 'r:gz') as bundle:
        for member in bundle:
            assert member.isfile() and member.name in expected, member.name
            assert member.name not in seen, '压缩包条目重复：' + member.name
            row = expected[member.name]
            assert member.size == row['bytes'], member.name
            with bundle.extractfile(member) as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == row['sha256'], member.name
            assert not (root / member.name).exists(), '已归档文件仍在活动目录：' + member.name
            seen.add(member.name)
    assert seen == set(expected), '压缩包缺少登记文件'
    backup = root / safe_name(record['本地备份'])
    if backup.exists():
        assert sha(backup) == record['归档包SHA256'], '本地备份与归档包不一致'
    if check_preserved:
        retained = json.loads((root / record['保留文件登记']).read_text())['文件SHA256']
        for name, digest in retained.items():
            assert sha(root / safe_name(name)) == digest, '清理时保留文件发生变化：' + name
    result = dict(状态='通过', 归档文件=len(rows), 原文件字节=record['原文件字节'],
                  归档包字节=archive.stat().st_size, 保留文件核对=check_preserved)
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--check-preserved', action='store_true', help='核对清理时保留文件快照；后续合法修改后不适用')
    args = parser.parse_args()
    verify(args.root.resolve(), args.check_preserved)
