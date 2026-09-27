"""在交付核验通过后建立本阶段文件清单，不修改模型输入和原结果。"""
from pathlib import Path
import hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'研究报告/00审查';E=OUT/'证据'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def main():
    manifest_path=E/'阶段0冻结清单.json'
    if manifest_path.exists():raise SystemExit('本阶段已经封存；不得覆盖清单，新增工作应另建版本。')
    quality=read(E/'交付核验.json');assert quality['status']=='PASS'
    recheck=read(E/'交付工具隔离复验/通过日志/执行检查.json')
    assert len(recheck)==6 and all(r['returncode']==0 for r in recheck)
    compare=read(E/'交付工具隔离复验/对账.json');assert compare['status']=='PASS'
    stats=read(E/'交付统计.json');cleanup=read(E/'废弃结果清理.json')
    # 允许用户原有prompt修改和明确归档的旧结果删除，禁止混入模型代码修改。
    modified=subprocess.check_output(['git','diff','--name-only','--diff-filter=M','-z'],cwd=ROOT).decode().split('\0')
    assert all(p in ['','prompt.md'] for p in modified),modified
    deleted=subprocess.check_output(['git','diff','--name-only','--diff-filter=D','-z'],cwd=ROOT).decode().split('\0')
    assert all(not p or any(p.startswith(d+'/') for d in cleanup['removed_directories']) for p in deleted),deleted
    dump(E/'工作区变动说明.json',{'status':'PASS','original_user_modified_files':[p for p in modified if p],'deleted_tracked_files':[p for p in deleted if p],'model_code_modified':False,'git_commit_created':False,'git_pushed':False,'scope':'原有prompt修改保留；仅清理名单内旧结果删除；新增文件为阶段0底稿与归档'})
    stage=OUT/'阶段0完成报告.md'
    appendix='\n## 交付文件与封存\n\n'
    appendix+='\n'.join('- ['+name+']('+name+')' for name in ['最终模型说明.md','最终数据字典.xlsx','结果冻结报告.md','公式与术语审查.md','成本模型说明.md','数据来源审查.pdf','data_source.json'])
    appendix+=f'\n\n交付复现工具已按491文件扩展快照从头执行：冻结哈希、72项模型测试、基础六路径、年度指标、价格敏感性及完整六路径重求全部通过。另对共同起点及原区域结果完成{compare["checks"]}项字段对账。重求汇总新增求解阶段诊断字段，仅作运行证据，不进入报告数值准入；原模型结果没有替换。\n'
    appendix+=f'\n\n人工审查PDF共{quality["pdf_pages"]}页，全部{stats["report_admitted_records"]}项准入记录均可检索。交付核验已核对来源图、源位置、工作簿及JSON的一致性；逐项检查记录见`证据/交付核验.json`。旧结果共{cleanup["archived_files"]}文件，经压缩包完整性及逐文件哈希核验后移除活动副本，清单见《废弃结果清理清单》。\n\n本阶段清单按文件SHA256封存，复核命令见审计工具使用说明。对封存资料的后续修改会被核验程序识别，应另建版本。冻结清单不包含自身及其相邻校验说明，清单的外部校验值单独留存。\n'
    assert '## 交付文件与封存' not in stage.read_text()
    stage.write_text(stage.read_text()+appendix)
    # 本次交付的实际浏览器打印与最终PDF哈希记录。
    dump(E/'PDF最终打印记录.json',{'status':'PASS','renderer':'Google Chrome headless，本地HTML，无外部素材','raw_pdf':str((E/'数据来源审查_浏览器打印.pdf').relative_to(ROOT)),'raw_pdf_sha256':sha(E/'数据来源审查_浏览器打印.pdf'),'final_pdf_sha256':sha(OUT/'数据来源审查.pdf'),'pages':quality['pdf_pages'],'note':'独立浏览器命令获准执行；生成程序--skip-print使用同源打印件添加页码'})
    snapshot=read(E/'输入与原结果快照.json');paths={ROOT/r['path'] for r in snapshot}
    for r in snapshot:assert sha(ROOT/r['path'])==r['sha256'],r['path']
    paths.add(ROOT/'docs/FREEZE-MANIFEST-2026-09-27.json')
    paths.add(ROOT/cleanup['archive'])
    paths.update(p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in [manifest_path,E/'阶段0冻结说明.md'])
    paths.update(p for p in (ROOT/'研究报告/数据来源').iterdir() if p.name in ['data_source.json','数据来源审查.pdf'])
    entries=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)]
    manifest={'version':'stage0_local_v4_2026-09-27','status':'FROZEN_WITH_DECLARED_LIMITATIONS','baseline_commit':read(E/'版本核验.json')['local_commit'],'original_result_unchanged':True,'files':entries,'removed_directories':cleanup['removed_directories'],'original_snapshot_files':len(snapshot),'records':stats['records'],'chapter_references':'拟引用位置；正式正文形成后另建引用定位版本','exclusions':['本清单自身','阶段0冻结说明.md：包含清单哈希，避免循环校验','__pycache__缓存'],'unresolved_items':read(OUT/'data_source.json')['unresolved_items']}
    dump(manifest_path,manifest)
    digest=sha(manifest_path)
    note=f'# 阶段0冻结说明\n\n本阶段以用户确认的本地v4封存。文件清单为`阶段0冻结清单.json`，共{len(entries)}个文件，覆盖原始证据、最终结果、本阶段七项交付、复核工具和废弃结果归档。原输入及原结果快照保持一致。\n\n清单SHA256：\n\n```text\n{digest}\n```\n\n该值用于外部留档核对清单；清单自身及本说明不纳入循环哈希。运行`审计工具/核验冻结.py`可只读检查清单内文件与旧目录状态。检查通过表示文件一致，不表示尚缺的工程校核已经完成。\n\n冻结状态为“附已说明限制的冻结”。模型、数据或费用范围发生变化时另建版本；正式正文形成后另建图表与段落引用定位，不修改本版原值。\n'
    (E/'阶段0冻结说明.md').write_text(note)
    print(json.dumps({'status':manifest['status'],'files':len(entries),'manifest_sha256':digest},ensure_ascii=False))
if __name__=='__main__':main()
