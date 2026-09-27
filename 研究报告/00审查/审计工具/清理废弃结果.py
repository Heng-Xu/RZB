"""按明确名单归档并移除旧结果；不删除模型代码、输入或原冻结文件。"""
from pathlib import Path
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'研究报告/00审查'
TARGETS=['实验/无EA/results','实验/无EA/results_v4_apparent_backup',
         '实验/有EA/results','实验/研究/results/runs',
         '实验/研究/results/annual_2021_2025',
         '实验/研究/results/real_2025_visuals',
         '实验/研究/results/10kv_section_tie_case']
ARCHIVE=ROOT/'历史归档/阶段0废弃结果-2026-09-27.zip'
MANIFEST=OUT/'证据/废弃结果清理.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not ARCHIVE.exists(), '已有归档，不重复清理；请先核查清单'
    protected={r['path'] for r in json.loads((OUT/'证据/输入与原结果快照.json').read_text())}
    entries=[]
    for target in TARGETS:
        folder=ROOT/target
        assert folder.is_dir() and not folder.is_symlink(), target
        for p in sorted(folder.rglob('*')):
            assert not p.is_symlink(), str(p)
            if p.is_file():
                key=str(p.relative_to(ROOT));assert key not in protected,key
                entries.append({'path':key,'bytes':p.stat().st_size,'sha256':sha(p)})
    ARCHIVE.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(ARCHIVE,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for r in entries:z.write(ROOT/r['path'],r['path'])
        z.writestr('归档索引.json',json.dumps(entries,ensure_ascii=False,indent=2))
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        for r in entries:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
    # 用户明确要求删除废弃结果。先验证可恢复的压缩副本，再删除活动目录中的旧副本。
    for r in entries:
        p=ROOT/r['path'];assert sha(p)==r['sha256'];p.unlink()
    for target in TARGETS:
        folder=ROOT/target
        for p in sorted((x for x in folder.rglob('*') if x.is_dir()),key=lambda x:len(x.parts),reverse=True):p.rmdir()
        folder.rmdir()
    evidence={'status':'PASS','archive':str(ARCHIVE.relative_to(ROOT)),'archive_sha256':sha(ARCHIVE),'removed_directories':TARGETS,'archived_files':len(entries),'original_bytes':sum(r['bytes'] for r in entries),'entries':entries,'retained':'原冻结409文件、原输入、当前v4结果、real_data_audit、implementation_log及既有archive保持不变'}
    MANIFEST.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    lines=['# 废弃结果清理清单','','已按用户要求移除旧结果活动副本。删除前逐文件建立SHA256索引，写入压缩包并验证每个归档文件的哈希与压缩完整性。旧数字不进入本阶段报告准入名单。','',f'共归档并移除{len(entries)}个文件，原文件合计{sum(r["bytes"] for r in entries)}字节。压缩包为`{ARCHIVE.relative_to(ROOT)}`，归档索引及校验值见`证据/废弃结果清理.json`。','','## 移除目录','']
    lines += ['- `'+x+'`' for x in TARGETS]
    lines += ['','## 保留依据','','原冻结409文件及本阶段491文件原件快照均保持一致。当前v4、价格敏感性完整路径、原始数据和模型代码未删除。部分包含planning、transformer_only等名称的中间表仍是当前运行输入；这些文件按实际依赖保留，不能仅凭名称判断废弃。','', '研究目录中real_data_audit、implementation_log和既有archive属于原资料审查及历史记录，保留作追溯。原冻结目录内的早期预算、恢复比例及其他诊断文件保留历史证据资格，禁止自动转作最终结果。','','## 恢复与引用','','如需历史比对，在隔离目录解压本压缩包，不恢复到当前运行目录。归档只保留审查证据；历史结果重新准入必须核查数据、模型、费用口径和完整路径。']
    (OUT/'废弃结果清理清单.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in evidence.items() if k!='entries'},ensure_ascii=False))

if __name__=='__main__':main()
