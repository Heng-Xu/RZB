"""核验时临时恢复已归档日志，结束后仅删除本次恢复且摘要未变的文件。"""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = Path('docs/历史归档/20261020/锁定日志归档.json')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def registered(root):
    record = json.loads((root / REGISTRY).read_text())
    rows = record['文件']
    assert len({r['path'] for r in rows}) == len(rows), '日志登记重复'
    for row in rows:
        name = PurePosixPath(row['path'])
        assert not name.is_absolute() and '..' not in name.parts and name.suffix == '.log'
        assert (root / name).resolve().is_relative_to(root.resolve()), row['path']
    return record, {r['path']: r for r in rows}


def materialize(root, state):
    record, rows = registered(root)
    archive = root / record['归档包']
    assert sha(archive) == record['归档包SHA256'], '日志归档包摘要不一致'
    created = []
    state.write_text(json.dumps(dict(root=str(root.resolve()), created=created)))
    with tarfile.open(archive, 'r:gz') as bundle:
        members = bundle.getmembers()
        assert len(members) == len(rows) and {m.name for m in members} == set(rows)
        for member in members:
            row = rows[member.name]
            assert member.isfile() and member.size == row['bytes'], member.name
            with bundle.extractfile(member) as stream:
                data = stream.read()
            assert hashlib.sha256(data).hexdigest() == row['sha256'], member.name
            path = root / member.name
            if path.exists():
                assert path.is_file() and sha(path) == row['sha256'], '已有日志变化，禁止覆盖：' + member.name
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(data)
            created.append(member.name)
            state.write_text(json.dumps(dict(root=str(root.resolve()), created=created)))


def cleanup(state):
    if not state.exists():
        return
    if not state.stat().st_size:
        state.unlink()
        return
    saved = json.loads(state.read_text())
    root = Path(saved['root']).resolve()
    _, rows = registered(root)
    for name in saved['created']:
        assert name in rows, name
        path = root / name
        if path.exists():
            assert sha(path) == rows[name]['sha256'], '临时日志已变化，保留供检查：' + name
            path.unlink()
    state.unlink()


@contextmanager
def temporary_logs(root=ROOT):
    with tempfile.NamedTemporaryFile(prefix='xuzhou-log-evidence-', suffix='.json', delete=False) as stream:
        state = Path(stream.name)
    try:
        materialize(root, state)
        yield
    finally:
        cleanup(state)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--materialize', type=Path, metavar='STATE')
    group.add_argument('--cleanup', type=Path, metavar='STATE')
    args = parser.parse_args()
    if args.materialize:
        try:
            materialize(ROOT, args.materialize)
        except BaseException:
            cleanup(args.materialize)
            raise
    else:
        cleanup(args.cleanup)
