"""将明确排除的本轮试算校验备份后移出活动目录；不处理原始收资或正式报告。"""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
TRIAL=ROOT/'研究报告/试算'
RECORD=TRIAL/'归档记录_20261010'
BACKUP=TRIAL/'历史本地备份/20261010_已排除试算.zip'
OLD_DIRS=[TRIAL/name for name in (
    '20261009_两地同期重建','20261009_市区40','20261010_两地逐年方案审查',
    '20261010_网络约束案例','20261010_转供与承载力约束审查',
    '20261010_实际年度负荷静态试算/city_first_pool_diagnostic')]
CODE=ROOT/'实验/研究/rebuild_2026'
OLD_CODE={
    'network_case_20261010':['build_review.py','infeasibility.py','report.py','share.py','soc_repair.py','README.md'],
    'synchronous_20261009':['compare.py','endpoint_sensitivity_20261010.py','report.py','test_endpoint_sensitivity.py','test_model.py','transfer_audit_20261010.py'],
    'pilot_20261009':['render.py','test_pilot.py'],
}


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    if BACKUP.exists():raise SystemExit('备份已存在；不重复执行清理。请查归档清单。')
    RECORD.mkdir(parents=True,exist_ok=True);BACKUP.parent.mkdir(parents=True,exist_ok=True)
    files=[p for d in OLD_DIRS if d.exists() for p in d.rglob('*') if p.is_file()]
    files += [CODE/d/f for d,fs in OLD_CODE.items() for f in fs if (CODE/d/f).is_file()]
    files=sorted(set(files));manifest=[];summaries=[]
    for p in files:
        assert p.is_relative_to(TRIAL) or any(p==CODE/d/f for d,fs in OLD_CODE.items() for f in fs)
        assert not p.is_symlink()
        raw=p.read_bytes();manifest.append({'path':str(p.relative_to(ROOT)),'bytes':len(raw),'sha256':sha(raw)})
        if p.name in ('summary.json','案例结论核对.json','审查摘要.json'):
            try:
                data=json.loads(raw)
                summaries.append({'original_path':str(p.relative_to(ROOT)),
                                  'summary':{k:v for k,v in data.items() if k in ('region','case','cost_npv_10k','annual','solver','scope')}})
            except (ValueError,UnicodeError):pass
    with ZipFile(BACKUP,'w',ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,str(p.relative_to(ROOT)))
    with ZipFile(BACKUP) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(manifest)
        for r in manifest:assert sha(z.read(r['path']))==r['sha256']
    record={'backup_path':str(BACKUP.relative_to(ROOT)),'backup_sha256':sha(BACKUP.read_bytes()),
            'backup_bytes':BACKUP.stat().st_size,'backup_git_policy':'仅本地备份，不推送Git；本清单及历史结果摘要推送',
            'verified_zip_and_all_file_hashes':True,'file_count':len(files),'original_bytes':sum(r['bytes'] for r in manifest),
            'files':manifest}
    (RECORD/'清理清单.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    (RECORD/'已排除方案结果摘要.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2)+'\n')
    # 只在全部备份检查通过后删除明确枚举的原文件；不递归删除其他路径。
    for p in files:
        assert sha(p.read_bytes())==next(r['sha256'] for r in manifest if r['path']==str(p.relative_to(ROOT)))
        p.unlink()
    for d in OLD_DIRS:
        if d.exists():
            for sub in sorted((p for p in d.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):sub.rmdir()
            d.rmdir()
    print(json.dumps({k:v for k,v in record.items() if k!='files'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
