"""只读检查阶段0冻结清单，发现变动立即返回非零状态。"""
from pathlib import Path
import hashlib,json,sys

ROOT=Path(__file__).resolve().parents[3]
def main():
    path=ROOT/'研究报告/00审查/证据/阶段0冻结清单.json'
    manifest=json.loads(path.read_text());bad=[]
    for item in manifest['files']:
        p=ROOT/item['path']
        if not p.is_file():bad.append(item['path']+'：缺文件');continue
        if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:bad.append(item['path']+'：哈希变化')
    for p in manifest['removed_directories']:
        if (ROOT/p).exists():bad.append(p+'：旧结果目录重新出现')
    report={'status':'FAIL' if bad else 'PASS','verified_files':len(manifest['files']),'problems':bad,'rule':'冻结清单自身哈希由外部保管；本检查不修改任何文件'}
    print(json.dumps(report,ensure_ascii=False));return bool(bad)
if __name__=='__main__':sys.exit(main())
