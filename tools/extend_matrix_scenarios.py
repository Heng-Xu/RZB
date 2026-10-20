"""独立补算1.05—1.25的11个分散系数节点；保留原锁定库。"""
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import sys
import time
from unittest.mock import patch

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'tools'))
from locked_parameter_results import allowed_pairs, key, public_frame, sha
from 实验.研究.rebuild_2026.matrix_20261012 import model

TRIAL = ROOT/'研究报告/试算/20261019_负荷分散系数扩展'
PUBLIC = ROOT/'研究报告/01研究推荐/当前版/负荷分散系数扩展_20261019'
SOURCE = ROOT/'研究报告/数据来源/当前版/负荷分散系数扩展_20261019'
REVIEW = ROOT/json.loads((ROOT/'tools/report_policy.json').read_text())['plain_delivery_review']
DIVERSITY = [round(1.05+.02*i, 2) for i in range(11)]


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def tasks():
    # 每个分散节点使用同一完整联合域及7%增长边界，避免按输出挑选组合。
    result = []
    for kd in DIVERSITY:
        for eta, growth, duration, pair in itertools.product(
                [i/4 for i in range(13)], [0,.02,.03,.04,.055,.07,.08,.1],
                [2,4,6], allowed_pairs()):
            result.append(dict(eta=eta, growth_rate=growth, support_duration_h=duration,
                               cable_fraction=pair[0], initial_transfer_fraction=pair[1],
                               diversity=kd, node_purpose='11节点完整联合采样'))
        for eta, growth, cable, duration in itertools.product(
                [.5,1.5,2.5], [.071,.075], [.1,.3,.5], [2,4,6]):
            result.append(dict(eta=eta, growth_rate=growth, cable_fraction=cable,
                               initial_transfer_fraction=.3, support_duration_h=duration,
                               diversity=kd, node_purpose='7%增长边界补充'))
    assert len({key(r) for r in result}) == len(result)
    return result


def solve(parameters):
    try:
        row = model.solve(dict(parameters, gap=1e-7, seconds=30))
    except AssertionError:
        # 仅收紧求解器数值容差；锁定模型、物理残差门限和约束均不更改。
        constructor=model.highspy.Highs
        def strict_highs():
            solver=constructor()
            for option in ['mip_feasibility_tolerance','primal_feasibility_tolerance','dual_feasibility_tolerance']:
                solver.setOptionValue(option,1e-8)
            return solver
        with patch.object(model.highspy,'Highs',strict_highs):
            row=model.solve(dict(parameters,gap=1e-7,seconds=120,numerical_feasibility_tolerance=1e-8))
        row['numerical_retry_reason']='默认数值容差下物理或矩阵残差未通过；收紧至1e-8后重新求解'
    if not row['verified'] and row['status'] != 'Infeasible':
        row = model.solve(dict(parameters, gap=1e-7, seconds=120))
    assert row['verified'] or row['status'] == 'Infeasible', (key(row), row['status'])
    row['record_origin'] = '11节点扩展独立求解'
    return row


def run(workers):
    for folder in [TRIAL, PUBLIC, SOURCE, REVIEW]:
        folder.mkdir(parents=True, exist_ok=True)
    jobs = tasks()
    model_path = Path(model.__file__)
    design = dict(用途='补算推广矩阵及完整负荷分散系数敏感性序列',
                  负荷分散系数节点=DIVERSITY, 间隔=.02, 分档界值=1.15,
                  分档=['[1.05,1.15]', '(1.15,1.25]'], 任务数=len(jobs),
                  联合域=model.AREA_SCENARIOS, 求解模型=str(model_path.relative_to(ROOT)),
                  模型SHA256=sha(model_path), 参数字段=model.FIELDS,
                  新增联络有效功率_MW=7.49106117, 工程限值_MVA=8,
                  说明='工程8 MVA按功率因数0.95折算7.60 MW；既有区段转移规模低于该限值，沿用有效功率与锁定费用条件。')
    design_path = TRIAL/'试算设计.json'
    if design_path.exists():
        assert json.loads(design_path.read_text()) == design, '续算设计或模型发生变化'
    else:
        write(design_path, design)
    raw_path = TRIAL/'原始求解记录.jsonl'
    if not raw_path.exists() and raw_path.with_suffix('.jsonl.gz').exists():
        import gzip,shutil
        with gzip.open(raw_path.with_suffix('.jsonl.gz'),'rb') as source,raw_path.open('wb') as output:
            shutil.copyfileobj(source,output)
    rows = [json.loads(line) for line in raw_path.open()] if raw_path.exists() else []
    done = {key(r) for r in rows}
    assert len(done) == len(rows)
    # 1.15与原库相同的节点逐项核对模型后复用，原始求解状态/间隙保留。
    old_manifest = json.loads((ROOT/'研究报告/05_review/当前版/1012参数结果锁定/锁定清单.json').read_text())
    assert any(r['sha256'] == sha(model_path) for r in old_manifest['文件'] if r['path'] == str(model_path.relative_to(ROOT)))
    legacy_path = ROOT/'研究报告/试算/20261012_参数联合情景锁定/统一原始求解记录.jsonl'
    legacy = {key(r):r for r in (json.loads(line) for line in legacy_path.open())}
    reused = []
    for p in jobs:
        k = key(p)
        if k in legacy and k not in done:
            r = dict(legacy[k], node_purpose=p['node_purpose'], record_origin='同模型同输入锁定节点复用')
            reused.append(r)
    with raw_path.open('a') as handle:
        for row in reused:
            handle.write(json.dumps(row, ensure_ascii=False)+'\n')
            rows.append(row); done.add(key(row))
        handle.flush()
        pending = [r for r in jobs if key(r) not in done]
        print(f'设计{len(jobs)}节点，已有{len(rows)}，待求解{len(pending)}，进程{workers}', flush=True)
        started = time.monotonic()
        with ProcessPoolExecutor(max_workers=workers, mp_context=get_context('spawn')) as pool:
            for i, row in enumerate(pool.map(solve, pending, chunksize=8), 1):
                handle.write(json.dumps(row, ensure_ascii=False)+'\n')
                rows.append(row)
                if i % 200 == 0 or i == len(pending):
                    handle.flush()
                    print(f'{len(rows)}/{len(jobs)}；已用{time.monotonic()-started:.0f}s', flush=True)
    assert {key(r) for r in rows} == {key(r) for r in jobs}
    good = [r for r in rows if r['verified']]
    data = public_frame(pd.DataFrame(good)).sort_values(list(public_frame(pd.DataFrame(good)).columns[:6]))
    data.to_csv(PUBLIC/'统一有效样本.csv', index=False)
    pd.DataFrame([r for r in rows if not r['verified']]).to_csv(PUBLIC/'不可行节点.csv', index=False)
    from collections import Counter
    summary = dict(状态='求解完成，待矩阵及独立LP核验', 设计节点数=len(jobs),
                   有效节点数=len(good), 不可行节点数=len(rows)-len(good),
                   求解状态=dict(Counter(r['status'] for r in rows)),
                   最大相对间隙=max(r['relative_gap'] for r in good),
                   最大物理约束残差_MW=max(r['physical_check']['max_violation_mw'] for r in good),
                   原始库SHA256=sha(raw_path), 试算设计SHA256=sha(design_path),
                   有效样本SHA256=sha(PUBLIC/'统一有效样本.csv'))
    write(REVIEW/'求解核验.json', summary)
    write(SOURCE/'计算来源.json', design | dict(原锁定节点来源=str(legacy_path.relative_to(ROOT)),
          原锁定节点来源SHA256=sha(legacy_path), 扩展原始库=str(raw_path.relative_to(ROOT)),
          扩展原始库SHA256=sha(raw_path)))
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--sensitivity-only',action='store_true',help='另行预核算11点完整序列，不改主原始库')
    args = parser.parse_args()
    if args.sensitivity_only:
        rows=[solve(dict(eta=2.5,growth_rate=.07,cable_fraction=.1,initial_transfer_fraction=.5,
                        support_duration_h=4,diversity=kd,node_purpose='11点敏感性独立预核算')) for kd in DIVERSITY]
        assert all(r['verified'] for r in rows)
        write(SOURCE/'11点序列独立预核算.json',dict(状态='预核算完成，待与完整库逐点核对',节点=rows))
        for r in rows:print(r['diversity'],r['capacity_mva'],f"{r['clr']:.4f}",r['storage_mw'],r['line_count'],f"{r['cost']:.2f}")
    else:run(args.workers)
