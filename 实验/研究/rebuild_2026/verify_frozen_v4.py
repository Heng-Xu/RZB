"""核验冻结输入、代码、结果哈希及项目运行环境。"""
from pathlib import Path
import hashlib,json,sys,importlib.metadata as metadata


def verify():
    root=Path(__file__).resolve().parents[3]
    manifest=json.loads((root/'docs/FREEZE-MANIFEST-2026-09-27.json').read_text())
    problems=[]
    if list(sys.version_info[:2])!=manifest['python_major_minor']:problems.append('Python版本与冻结环境不同')
    for name,version in manifest['dependencies'].items():
        try:actual=metadata.version(name)
        except metadata.PackageNotFoundError:actual='missing'
        if actual!=version:problems.append(f'{name}: expected {version}, got {actual}')
    for r in manifest['files']:
        p=root/r['path']
        if not p.is_file():problems.append(f'missing: {r["path"]}')
        elif hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:problems.append(f'changed: {r["path"]}')
    result={'status':'PASS' if not problems else 'FAIL','checked_files':len(manifest['files']),'problems':problems}
    if problems:raise ValueError(result)
    return result

if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False))
