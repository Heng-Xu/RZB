"""核对用户确认的初步定档稿件、源及活动复现文件，修改后必须重新登记。"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'研究报告/05_review/当前版/1014初步定档与表述约束/初步定档清单.json'


def main():
    record = json.loads(MANIFEST.read_text())
    assert record['状态'] == '文件核验通过'
    for name, digest in record['文件SHA256'].items():
        p = ROOT/name
        assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == digest, '定档文件已变化: '+name
    from manage_preliminary_archive import verify
    verify()
    print(json.dumps({'状态':'通过','版本':record['版本'],'定档文件':len(record['文件SHA256']),
        'Git标签':record['Git标签']},ensure_ascii=False))


if __name__ == '__main__':
    main()
