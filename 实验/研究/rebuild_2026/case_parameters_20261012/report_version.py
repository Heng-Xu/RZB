"""登记用户选定的案例报告版本；原12组方案和其余对照保留。"""
import importlib.metadata
import json
import sys
from pathlib import Path

from . import capacity_run as base

VERSION='case_station_caps_normal_adjust_20261013'
RESULT=base.ROOT/'研究报告/01研究推荐/当前版/既有转供约束诊断_20261012'
REVIEW=base.ROOT/'研究报告/05_review/当前版/1012既有转供约束诊断'
OUT=base.ROOT/'研究报告/试算/20261012_既有转供约束诊断'
LOCK=REVIEW/'报告采用版本锁定清单.json'
MAIN_CASES=('elastic_no_floor','rigid_storage')


def purpose(policy,case):
    return '报告主方案' if policy=='station_caps' and case in MAIN_CASES else '保留对照'


def selected(records):
    main=[r for r in records if purpose(r['policy'],r['case'])=='报告主方案']
    assert {(r['region'],r['case']) for r in main}=={(a,c) for a in ('city','pizhou') for c in MAIN_CASES}
    return sorted(main,key=lambda r:(r['region'],MAIN_CASES.index(r['case'])))


def freeze():
    if LOCK.exists():raise FileExistsError('报告采用版本已登记，后续变更另建版本：'+str(LOCK))
    check=json.loads((REVIEW/'约束对照独立核验.json').read_text());assert check['verified']
    records=check['records'];assert len(records)==12
    main=selected(records);files=set()
    for r in main:
        folder=OUT/r['result_folder']
        assert r['input_sha256']==base.sha(folder.parent/'inputs.json')
        assert r['solution_sha256']==base.sha(folder/'chosen_solution.npz')
        files.add(folder.parent/'inputs.json');files.add(base.OUT/r['region']/'static_base.npz')
        files.add(base.OUT/r['region']/'inputs.json')
        for name in ('chosen_solution.npz','summary.json','stations.csv','projects.csv','years.csv','selected_pairs.json','independent_lp.json'):
            files.add(folder/name)
    files.update((base.ROOT/'研究报告/数据来源/当前版/既有转供逐站约束_20261012').glob('*'))
    from .run import TRANSFER_FILE,CABLE_FILE
    files.update([TRANSFER_FILE,CABLE_FILE,base.ROOT/'实验/研究/data/tuomin/变电站对应.md'])
    modules=set()
    for module in list(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if not filename:continue
        path=Path(filename).resolve()
        if path.is_relative_to(base.ROOT) and path.suffix=='.py' and path.is_file():modules.add(path)
    assert Path(__file__).resolve() in modules
    def hashes(paths):return [dict(path=str(p.relative_to(base.ROOT)),sha256=base.sha(p)) for p in sorted(paths) if p.is_file()]
    base.dump(LOCK,dict(version=VERSION,confirmed_date='2026-10-13',
        user_instruction='正常允许调整供区的弹性无下限和刚性作为撰写报告的数据和模型版本；其余方案保留。',
        scope='市区、邳州；2022—2025共同压缩起点的规划回算；逐站既有转供MW上限；正常及最大单台主变N−1静态截面。',
        main=main,comparisons=[r for r in records if purpose(r['policy'],r['case'])!='报告主方案'],
        model_files=hashes(modules),data_files=hashes(files),
        dependencies={name:importlib.metadata.version(name) for name in ('numpy','scipy','highspy','openpyxl')},
        cost_basis='已核验具体可行方案费用；保留有效费用下界和正间隙。',
        report_status='供后续撰写采用；正式六章和Word/PDF尚未切换。'))
    verify(records)
    print('LOCKED_REPORT_VERSION',VERSION,'4 main / 8 comparison',flush=True)


def verify(records):
    if not LOCK.exists():return
    manifest=json.loads(LOCK.read_text());assert manifest['version']==VERSION
    keys=('region','case','policy','result_folder','input_sha256','solution_sha256')
    assert {tuple(r[k] for k in keys) for r in selected(records)}=={tuple(r[k] for k in keys) for r in manifest['main']},'报告采用方案已变化，须另建版本'
    assert len(manifest['comparisons'])==8
    for r in manifest['model_files']+manifest['data_files']:
        path=base.ROOT/r['path'];assert path.is_file() and base.sha(path)==r['sha256'],r['path']
    print('VERIFIED_REPORT_VERSION',VERSION,flush=True)
