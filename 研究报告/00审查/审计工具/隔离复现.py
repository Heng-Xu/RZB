"""复制原冻结文件后运行检查和六路径重求，不覆盖项目中的模型结果。"""
from pathlib import Path
import argparse,json,shutil,subprocess,sys,hashlib

ROOT=Path(__file__).resolve().parents[3]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',required=True,help='尚不存在的隔离输出目录，建议/tmp/rzb-stage0-new-review')
    args=parser.parse_args();destination=Path(args.destination).resolve()
    if destination.exists():raise SystemExit('输出目录已经存在，请另选目录，避免覆盖原审查证据。')
    if destination==ROOT or ROOT in destination.parents:raise SystemExit('隔离目录须位于原项目之外。')
    destination.mkdir(parents=True);clone=destination/'root';clone.mkdir();log=destination/'logs';log.mkdir()
    manifest=json.loads((ROOT/'docs/FREEZE-MANIFEST-2026-09-27.json').read_text())
    # 原409文件清单未包含根目录的储能价格注册及公告，使用阶段0扩展快照闭合依赖。
    snapshot=json.loads((ROOT/'研究报告/00审查/证据/输入与原结果快照.json').read_text())
    entries={r['path']:r for r in list(manifest['files'])+snapshot}
    entries['docs/FREEZE-MANIFEST-2026-09-27.json']={'path':'docs/FREEZE-MANIFEST-2026-09-27.json'}
    for r in entries.values():
        source=ROOT/r['path'];target=clone/r['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        if r.get('sha256') and hashlib.sha256(target.read_bytes()).hexdigest()!=r['sha256']:raise SystemExit('复制哈希不符：'+r['path'])
    cwd=clone/'实验/研究'
    tasks=[('冻结哈希',['-m','rebuild_2026.verify_frozen_v4']),
           ('模型测试',['-m','pytest','-q','rebuild_2026/tests','-p','no:cacheprovider']),
           ('六路径核查',['-m','rebuild_2026.simulation_reserve_policy_audit']),
           ('年度指标核查',['-m','rebuild_2026.annual_recommendation_audit']),
           ('价格敏感性核查',['-m','rebuild_2026.annual_cost_sensitivity_audit']),
           ('六路径重求',['-c',"from pathlib import Path; from rebuild_2026.simulation_reserve_policy import run; run(Path("+repr(str(destination/'reproduced'))+"))"])]
    status=[]
    for name,command in tasks:
        print('执行：'+name,flush=True)
        with (log/(name+'.log')).open('w') as f:
            result=subprocess.run([sys.executable]+command,cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
        status.append({'name':name,'returncode':result.returncode,'command':[sys.executable]+command})
        (log/'执行检查.json').write_text(json.dumps(status,ensure_ascii=False,indent=2))
        if result.returncode:raise SystemExit('未通过：'+name+'；请查看隔离日志。')
    print('隔离复现完成。重求结果未进入正文准入，须按冻结对账口径比较后另行登记。',flush=True)

if __name__=='__main__':main()
