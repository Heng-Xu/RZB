#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M1 端到端冒烟入口(Task 9)。

顺序:gen_synthetic(可用 --skip-gen 跳过)→load_scenario→clr.compute_all→
build_linkset→reduce_days→solve_scheme(A/B)→校核(run_n1/device_level/
county_check,基于方案B解,落盘 verify_flow.csv/verify_dlt2041.csv)→
回代补全(方案A解的全年8760时刻O2反向β检查)→全部 tab_*/fig_* 脚本(subprocess)。
末尾打印汇总块。任何一步失败立即打印步骤名并非零退出。

用法:python scripts/run_all.py --dataset real_2021_2025 --config model_contract.yaml --skip-gen
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.clr import compute_all
from src.io_loader import load_scenario
from src.links_sigma import build_linkset
from src.milp_planner import RUN_ID, solve_scheme
from src.typical_days import playback_violations, reduce_days
from src.verify_dlt2041 import county_check, device_level
from src.verify_flow_n1 import _normalize_solution, _pnet_prime_at, run_n1

RUN_DIR = ROOT / "results" / "runs" / RUN_ID
TAB_SCRIPTS = ["tab_A_zonematrix", "tab_B_lookup", "tab_C_redline"]
FIG_SCRIPTS = ["fig_V1_grid", "fig_V2_netload", "fig_V3_waterfall",
               "fig_V4_rcost", "fig_V5_heatmap", "fig_V6_split"]


def _fail(step: str, exc: BaseException | str) -> None:
    print(f"[run_all] 步骤失败: {step}: {exc}", file=sys.stderr)
    sys.exit(1)


def _step(name: str, fn, *args, **kwargs):
    t0 = time.time()
    try:
        result = fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - 需捕获任意步骤异常并定位步骤名
        _fail(name, exc)
    print(f"[run_all] {name} 完成 ({time.time() - t0:.1f}s)")
    return result


def _run_subprocess(step_name: str, argv: list[str]) -> None:
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        _fail(step_name, proc.stderr[-3000:] or proc.stdout[-3000:])
    print(f"[run_all] {step_name} 完成")


def _write_verify_csvs(data, bundle_b) -> pd.DataFrame:
    """方案B解跑通两校核器,落盘 verify_flow.csv/verify_dlt2041.csv。

    合并 schema 与 tests/test_verify.py::test_full_flow_solution_b_writes_verify_csv
    一致(tab_A_zonematrix.py/fig_V5_heatmap.py 依赖此 schema)。
    """
    flow_df = run_n1(data, bundle_b)
    dev_df = device_level(data, bundle_b).rename_axis("entity_id").reset_index()
    dev_df.insert(0, "level", "station")
    cty_df = county_check(data, bundle_b).rename_axis("entity_id").reset_index()
    cty_df.insert(0, "level", "county")
    combined = pd.concat([dev_df, cty_df], ignore_index=True, sort=False)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    flow_df.to_csv(RUN_DIR / "verify_flow.csv", index=False)
    combined.to_csv(RUN_DIR / "verify_dlt2041.csv", index=False)
    return flow_df


def _playback_o2(data, bundle_a) -> list[dict]:
    """回代补全:方案A解的全年8760时刻O2(反向β)回代检查。

    Task6 留档"全8760红线仅代表日保证"的实测回应。净负荷重构口径复用
    src.verify_flow_n1._pnet_prime_at(而非 milp_planner._build 内部的
    ap/an 带状公式)——SolutionBundle 落盘只保留聚合 |α|=ap+an,没有逐时
    p_ch/p_dis/ap/an 符号,milp 内部口径不可从落盘解精确重演。
    _pnet_prime_at 是既有、已被 test_verify.py 覆盖的从聚合α重构口径:
    储能仅在全年P⁺/P⁻两个峰值时刻各按额定功率满出力削峰,其余时刻按
    "非代表日无储能调度"取0;tie 按两端净负荷高低推断转移方向,量=
    该季α比例×回路容量。因此本检查得到的违约计数是**保守上界**,不等价于
    典型日展开内 milp 逐日最优调度下的真实越限率(如实报告,不算失败)。
    """
    sol = _normalize_solution(bundle_a)
    total = data.pnet.sum(axis=1)
    fwd_idx, rev_idx = int(total.values.argmax()), int(total.values.argmin())
    beta_cfg = data.params["beta"]
    beta = {sid: st.beta_eff(beta_cfg) for sid, st in data.stations.items()}
    cap = {sid: st.cap_mva for sid, st in data.stations.items()}
    expand = sol["expand_mva"]

    def constraints_fn(_solution, _data, t):
        prime = _pnet_prime_at(data, sol, t, fwd_idx, rev_idx)
        out = []
        for sid in data.stations:
            limit = beta[sid] * (cap[sid] + float(expand.get(sid, 0.0)))
            reverse = -float(prime[sid])
            if reverse > limit + 1e-6:   # 浮点噪声容差
                out.append(f"{sid}:reverse={reverse:.2f}>limit={limit:.2f}")
        return out

    return playback_violations(solution=bundle_a, data=data, constraints_fn=constraints_fn)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        choices=["synthetic", "real_2021_2025", "real_2025"],
        default="synthetic",
        help="运行合成回归、v3真实闭环或旧real_2025迁移入口",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "model_contract.yaml",
        help="v3 模型合同路径",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=ROOT / "data/processed/real_2021_2025",
        help="v3 标准化数据输出目录",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/runs/real-2021-2025-contract-v3/real_2021_2025-v3",
        help="v3 运行结果目录",
    )
    parser.add_argument(
        "--existing-tie-case-options",
        type=Path,
        help="现有10 kV联络切分案例（独立审批输入）",
    )
    parser.add_argument(
        "--new-tie-line-case-options",
        type=Path,
        help="新建10 kV联络线路案例（独立审批输入）",
    )
    parser.add_argument("--skip-gen", action="store_true",
                         help="跳过 gen_synthetic(data/synthetic 已存在时)")
    args = parser.parse_args()

    if args.dataset == "real_2021_2025":
        from src.v3_pipeline import run_v3_pipeline

        if args.skip_gen:
            print("[real_2021_2025] --skip-gen accepted: v3 real pipeline has no synthetic generator")
        run_v3_pipeline(
            project_root=ROOT,
            processed_root=args.processed_dir,
            run_dir=args.output_dir,
            contract_path=args.config,
            existing_tie_case_options=args.existing_tie_case_options,
            new_tie_line_case_options=args.new_tie_line_case_options,
        )
        return 0

    if args.dataset == "real_2025":
        print(
            "[real_2025] legacy migration entry is archive-only; use --dataset real_2021_2025 for formal v3",
            file=sys.stderr,
        )
        return 2

    t_start = time.time()

    if args.skip_gen:
        print("[run_all] --skip-gen: 跳过 gen_synthetic")
    else:
        _run_subprocess("gen_synthetic",
                         [sys.executable, str(ROOT / "scripts" / "gen_synthetic.py")])

    data = _step("load_scenario", load_scenario, ROOT, track="synthetic")
    _step("clr.compute_all", compute_all, data)
    links = _step("build_linkset", build_linkset, data)
    k = int(data.params["milp"]["typical_days"])
    tdays = _step("reduce_days", reduce_days, data.pnet.sum(axis=1), k)

    bundle_a = _step("solve_scheme(A)", solve_scheme, data, links, tdays, "A")
    bundle_b = _step("solve_scheme(B)", solve_scheme, data, links, tdays, "B")

    flow_df = _step("verify(run_n1+device_level+county_check, 方案B)",
                     _write_verify_csvs, data, bundle_b)
    playback = _step("回代补全(O2, 方案A, 全年8760)", _playback_o2, data, bundle_a)

    for name in TAB_SCRIPTS + FIG_SCRIPTS:
        _run_subprocess(f"{name}.py",
                         [sys.executable, str(ROOT / "scripts" / f"{name}.py"),
                          "--run", RUN_ID])

    elapsed = time.time() - t_start
    delta_c = bundle_a.total_cost - bundle_b.total_cost
    n1_viol = int((flow_df["loading_pct"] > 100).sum())

    print("=" * 60)
    print(f"M1 端到端冒烟汇总 (run_id={RUN_ID})")
    print("-" * 60)
    print(f"方案A 总成本(万元/年): {bundle_a.total_cost:.2f}")
    print(f"方案B 总成本(万元/年): {bundle_b.total_cost:.2f}")
    print(f"ΔC (A-B, 红线代价, 万元/年): {delta_c:.2f}")
    print("各分区推荐R(方案B r_after):")
    for zid, r in bundle_b.r_after.items():
        print(f"  {zid}: {r:.4f}")
    print(f"N-1越限行数(loading_pct>100, 全年P+/P-两断面): {n1_viol}")
    print(f"全年O2(反向β)回代违约时刻数(方案A解,保守上界,见函数注释): {len(playback)}")
    print(f"总耗时: {elapsed:.1f}s")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
