"""验证临时核验日志不会覆盖已有文件或误删变化后的文件。"""
import hashlib
import io
import json
import tarfile

import pytest

from tools import archive_log_evidence as logs


@pytest.fixture
def evidence(tmp_path):
    payloads = {'checks/old.log': b'old evidence\n', 'checks/new.log': b'new evidence\n'}
    archive = tmp_path / 'logs.tar.gz'
    with tarfile.open(archive, 'w:gz') as bundle:
        for name, data in payloads.items():
            member = tarfile.TarInfo(name)
            member.size = len(data)
            bundle.addfile(member, io.BytesIO(data))
    registry = tmp_path / logs.REGISTRY
    registry.parent.mkdir(parents=True)
    registry.write_text(json.dumps(dict(归档包='logs.tar.gz', 归档包SHA256=logs.sha(archive),
        文件=[dict(path=n, bytes=len(d), sha256=hashlib.sha256(d).hexdigest()) for n, d in payloads.items()])))
    return tmp_path, tmp_path / 'state.json', payloads


def test_cleanup_preserves_preexisting_file(evidence):
    root, state, payloads = evidence
    old = root / 'checks/old.log'
    old.parent.mkdir()
    old.write_bytes(payloads['checks/old.log'])
    logs.materialize(root, state)
    assert (root / 'checks/new.log').read_bytes() == payloads['checks/new.log']
    logs.cleanup(state)
    assert old.read_bytes() == payloads['checks/old.log']
    assert not (root / 'checks/new.log').exists() and not state.exists()


def test_materialize_refuses_overwrite(evidence):
    root, state, _ = evidence
    old = root / 'checks/old.log'
    old.parent.mkdir()
    old.write_bytes(b'changed locally')
    with pytest.raises(AssertionError, match='禁止覆盖'):
        logs.materialize(root, state)
    logs.cleanup(state)
    assert old.read_bytes() == b'changed locally'


def test_cleanup_preserves_changed_file(evidence):
    root, state, payloads = evidence
    logs.materialize(root, state)
    changed = root / 'checks/old.log'
    changed.write_bytes(b'new output')
    with pytest.raises(AssertionError, match='保留供检查'):
        logs.cleanup(state)
    assert changed.read_bytes() == b'new output' and state.exists()
    changed.write_bytes(payloads['checks/old.log'])
    logs.cleanup(state)


def test_materialize_rejects_corrupt_archive(evidence):
    root, state, _ = evidence
    with (root / 'logs.tar.gz').open('ab') as stream:
        stream.write(b'corrupt')
    with pytest.raises(AssertionError, match='归档包摘要不一致'):
        logs.materialize(root, state)
    assert not (root / 'checks').exists()
