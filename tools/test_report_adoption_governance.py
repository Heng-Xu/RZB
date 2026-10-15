"""报告采用规则变更仍须保留原件，正文和计算结果继续保持定档校验。"""
import pytest

from verify_preliminary_baseline import sha, verify_files


def test_report_rules_successor_preserves_frozen_report_data(tmp_path):
    rules = tmp_path / '研究报告/AGENTS.md'
    rules.parent.mkdir()
    rules.write_text('adopt eight confirmed schemes')
    archived = tmp_path / 'archived_rules.md'
    archived.write_text('previous report rules')
    data = tmp_path / '研究报告/计算表.json'
    data.write_text('frozen data')
    expected = {'研究报告/AGENTS.md': sha(archived), '研究报告/计算表.json': sha(data)}
    updates = {'研究报告/AGENTS.md': {'原SHA256': sha(archived), '现SHA256': sha(rules),
                                  '原件归档': archived.name}}
    verify_files(tmp_path, expected, updates)
    data.write_text('changed without review')
    with pytest.raises(AssertionError, match='定档文件已变化'):
        verify_files(tmp_path, expected, updates)


def test_report_rules_successor_requires_archived_original(tmp_path):
    rules = tmp_path / '研究报告/AGENTS.md'
    rules.parent.mkdir()
    rules.write_text('new rules')
    archived = tmp_path / 'archived_rules.md'
    archived.write_text('original rules')
    original_sha = sha(archived)
    updates = {'研究报告/AGENTS.md': {'原SHA256': original_sha, '现SHA256': sha(rules),
                                  '原件归档': archived.name}}
    archived.write_text('changed archive')
    with pytest.raises(AssertionError, match='继承基线原件不一致'):
        verify_files(tmp_path, {'研究报告/AGENTS.md': original_sha}, updates)
