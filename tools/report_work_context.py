"""独立后继任务只更新工作上下文时，保留正式报告原件核验。"""
import hashlib
import json
from pathlib import Path

ALLOWED = {'memory/current.md', 'prompt.md', 'tools/verify_report_release.py',
           'docs/CURRENT-WORKFLOW.md'}
CONTEXT = Path('研究报告/05_review/当前版/工作上下文衔接.json')
MAINTENANCE_FILES = {'研究报告/AGENTS.md', 'tools/build_current_report.py',
                     '.githooks/pre-commit', '.github/workflows/report-policy.yml'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def maintenance_original(root, name, path, expected):
    """维护入口升级后仍按旧交付哈希核验其原件，正文与数据不可走此分支。"""
    if digest(path) == expected:
        return path
    assert name in MAINTENANCE_FILES, '非维护文件不能继承旧原件：' + name
    record = json.loads((root/CONTEXT).read_text())['维护文件原件'][name]
    assert record['原SHA256'] == expected
    archived = root/record['原件归档']
    assert digest(archived) == expected, '维护入口原件不一致：' + name
    assert digest(root/name) == record['现SHA256'], '维护入口尚未登记：' + name
    return archived


def verify_context(root, release, expected):
    changed = {name for name, value in expected.items() if digest(root/name) != value}
    if not changed:
        return {}
    assert changed <= ALLOWED, '报告正文、数据或非上下文文件变化，须重新核验：'+', '.join(sorted(changed-ALLOWED))
    record = json.loads((root/CONTEXT).read_text())
    assert record['状态'] == '独立后继任务已核验'
    assert record['父交付登记SHA256'] == digest(release)
    updates = record['上下文变更']
    assert set(updates) == changed, '上下文衔接范围与实际变更不一致'
    for name in changed:
        item = updates[name]
        assert item['原SHA256'] == expected[name]
        assert digest(root/item['原件归档']) == expected[name], '历史上下文原件不一致：'+name
        assert digest(root/name) == item['现SHA256'], '当前上下文尚未登记：'+name
    manifest_path = root/record['独立成果清单']
    assert digest(manifest_path) == record['独立成果清单SHA256']
    manifest = json.loads(manifest_path.read_text())
    assert manifest['状态'] in {'逐年可行方案已核对', '机制审查及单年筛查已核对'}
    for item in manifest['files']:
        assert digest(root/item['path']) == item['sha256'], '后继成果变化：'+item['path']
    proof_path = root/record['独立核验记录']
    assert digest(proof_path) == record['独立核验记录SHA256']
    proof = json.loads(proof_path.read_text())
    assert proof['verified'] and proof['schemes'] and proof['solution_sources']
    if manifest['状态']=='机制审查及单年筛查已核对':
        assert proof['artifact_kind']=='model_mechanism_review'
        assert proof['limitation'] and proof['static_pairs_probes']>0
    for source in proof['solution_sources']:
        folder = root/source['folder']
        for name, value in source['files'].items():
            assert digest(folder/name) == value, '后继原始解变化：'+str(folder/name)
        lp = json.loads((folder/'independent_lp.json').read_text())
        assert lp['verified'] and lp['records'] and all(row['verified'] for row in lp['records'])
    return updates
