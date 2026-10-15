"""后继治理文件登记不放开正式稿件和模型数据。"""
import hashlib
import importlib.util
from pathlib import Path

import pytest


spec=importlib.util.spec_from_file_location('baseline_guard',Path(__file__).resolve().parents[4]/'tools/verify_preliminary_baseline.py')
guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)


def test_successor_keeps_both_original_and_current_hashes(tmp_path):
    (tmp_path/'AGENTS.md').write_text('current');(tmp_path/'original.md').write_text('original')
    old=guard.sha(tmp_path/'original.md')
    update={'AGENTS.md':{'原SHA256':old,'现SHA256':guard.sha(tmp_path/'AGENTS.md'),'原件归档':'original.md'}}
    guard.verify_files(tmp_path,{'AGENTS.md':old},update)
    (tmp_path/'AGENTS.md').write_text('later mutation')
    with pytest.raises(AssertionError):guard.verify_files(tmp_path,{'AGENTS.md':old},update)


def test_successor_cannot_exempt_report_or_model_files(tmp_path):
    with pytest.raises(AssertionError):guard.verify_files(tmp_path,{}, {'研究报告/04_word/研究报告终稿.docx':{}})
    with pytest.raises(AssertionError):guard.verify_files(tmp_path,{}, {'实验/研究/rebuild_2026/model.py':{}})
