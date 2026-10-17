"""固定案例被修改或主表误用经济对照时必须拒绝。"""
import json

import pytest

import verify_future_case_results as lock
from report_work_context import CONTEXT, digest, maintenance_original


def test_changed_locked_file_is_rejected(tmp_path):
    path = tmp_path / 'result.csv'
    path.write_text('confirmed result')
    item = dict(path=path.name, sha256=lock.sha(path))
    assert lock.checked(tmp_path, item) == path
    path.write_text('changed result')
    with pytest.raises(AssertionError, match='案例锁定文件变化'):
        lock.checked(tmp_path, item)


def test_economic_control_cannot_replace_primary(monkeypatch):
    original = lock.read_json

    def changed(path):
        data = original(path)
        if path == lock.ROOT / lock.ADOPTION:
            data = json.loads(json.dumps(data))
            data['主方案'][0]['方案代码'] = 'elastic_engineering'
        return data

    monkeypatch.setattr(lock, 'read_json', changed)
    with pytest.raises(AssertionError):
        lock.verify()


def test_maintenance_change_requires_exact_archived_original(tmp_path):
    name = 'tools/build_current_report.py'
    current = tmp_path / name
    current.parent.mkdir()
    current.write_text('new maintenance entry')
    archive = tmp_path / 'original.py'
    archive.write_text('old maintenance entry')
    expected = digest(archive)
    context = tmp_path / CONTEXT
    context.parent.mkdir(parents=True)
    context.write_text(json.dumps({'维护文件原件': {name: {
        '原SHA256': expected, '现SHA256': digest(current), '原件归档': archive.name}}}))
    assert maintenance_original(tmp_path, name, current, expected) == archive
    archive.write_text('changed archive')
    with pytest.raises(AssertionError, match='维护入口原件不一致'):
        maintenance_original(tmp_path, name, current, expected)


def test_report_data_cannot_use_maintenance_exception(tmp_path):
    current = tmp_path / 'data.json'
    current.write_text('changed data')
    with pytest.raises(AssertionError, match='非维护文件不能继承旧原件'):
        maintenance_original(tmp_path, '研究报告/02图表/当前版/计算表.json', current, 'original digest')
