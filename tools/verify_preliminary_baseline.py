"""核对用户确认的初步定档稿件、源及活动复现文件，修改后必须重新登记。"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'研究报告/05_review/当前版/1014初步定档与表述约束/初步定档清单.json'
SUCCESSOR = ROOT/'研究报告/05_review/当前版/1015会后建模复核/后继变更登记.json'
GOVERNANCE_FILES = {'AGENTS.md', '研究报告/AGENTS.md', 'docs/CURRENT-WORKFLOW.md', 'prompt.md',
                    'tools/verify_preliminary_baseline.py', 'tools/verify_report_review.py'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_files(root, expected, updates):
    assert set(updates) <= GOVERNANCE_FILES, '后继登记不能放开正式稿件、模型或数据的定档校验'
    for name, digest in expected.items():
        p = root/name
        assert p.is_file(), '定档文件缺失: '+name
        if name in updates:
            change = updates[name]
            assert change['原SHA256'] == digest
            archived = root/change['原件归档']
            assert archived.is_file() and sha(archived) == digest, '继承基线原件不一致: '+name
            assert sha(p) == change['现SHA256'], '后继文件已变化，须重新审阅登记: '+name
        else:
            assert sha(p) == digest, '定档文件已变化: '+name


def verified_successor():
    """读取有原件归档及独立证据的治理变更，正文和数据保持原哈希。"""
    updates = {}
    if SUCCESSOR.exists():
        successor = json.loads(SUCCESSOR.read_text())
        assert successor['状态'] == '逐项审阅及独立核验通过'
        assert successor['父清单SHA256'] == sha(MANIFEST)
        updates = successor['治理文件变更']
        for item in successor['核验依据']:
            assert sha(ROOT/item['path']) == item['sha256'], '后继核验依据已变化: '+item['path']
    return updates


def main():
    record = json.loads(MANIFEST.read_text())
    assert record['状态'] == '文件核验通过'
    updates = verified_successor()
    from verify_report_release import RELEASE, verify as verify_release
    if RELEASE.exists():
        release=verify_release()
        for name,digest in record['文件SHA256'].items():
            original=ROOT/name
            historical=release.get('历史定档原件', {})
            if name in historical:
                original=ROOT/historical[name]['原件归档']
            elif name in release['修改原件']:
                original=ROOT/release['修改原件'][name]['原件归档']
            if name in updates:
                assert updates[name]['原SHA256']==digest
                assert sha(ROOT/updates[name]['原件归档'])==digest
                digest=updates[name]['现SHA256']
            assert sha(original)==digest,'历史定档原件不一致：'+name
    else:
        verify_files(ROOT, record['文件SHA256'], updates)
    from manage_preliminary_archive import verify
    verify()
    print(json.dumps({'状态':'通过','版本':record['版本'],'定档文件':len(record['文件SHA256']),
        'Git标签':record['Git标签'],'后继治理文件':len(updates)},ensure_ascii=False))


if __name__ == '__main__':
    main()
