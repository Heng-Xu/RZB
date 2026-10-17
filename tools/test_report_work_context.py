"""工作上下文例外不得放开正式稿件、原始解或历史原件检查。"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_work_context import CONTEXT, digest, verify_context


def put(root, name, value):
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value) if isinstance(value,dict) else value)
    return p


def fixture(root):
    release=put(root,'release.json',{})
    old=put(root,'archive/current.md','旧状态')
    current=put(root,'memory/current.md','独立新任务')
    expected={'memory/current.md':digest(old)}
    lp=put(root,'solution/independent_lp.json',dict(verified=True,records=[dict(verified=True)]))
    proof=put(root,'proof.json',dict(verified=True,schemes=[{},{}],solution_sources=[dict(folder='solution',files={'independent_lp.json':digest(lp)})]))
    manifest=put(root,'manifest.json',dict(状态='逐年可行方案已核对',files=[dict(path='proof.json',sha256=digest(proof))]))
    put(root,CONTEXT,dict(状态='独立后继任务已核验',父交付登记SHA256=digest(release),
        上下文变更={'memory/current.md':dict(原SHA256=digest(old),现SHA256=digest(current),原件归档='archive/current.md')},
        独立成果清单='manifest.json',独立成果清单SHA256=digest(manifest),独立核验记录='proof.json',独立核验记录SHA256=digest(proof)))
    return release,expected


def test_verified_independent_context_passes():
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder);release,expected=fixture(root)
        assert set(verify_context(root,release,expected))=={'memory/current.md'}


@pytest.mark.parametrize('name',['archive/current.md','solution/independent_lp.json','proof.json'])
def test_evidence_or_archive_change_is_rejected(name):
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder);release,expected=fixture(root);put(root,name,'被改动')
        with pytest.raises(AssertionError):verify_context(root,release,expected)


def test_formal_report_change_is_rejected():
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder);release,expected=fixture(root)
        put(root,'研究报告/正文.md','新的正文');expected['研究报告/正文.md']=hashlib.sha256(b'old').hexdigest()
        with pytest.raises(AssertionError):verify_context(root,release,expected)
