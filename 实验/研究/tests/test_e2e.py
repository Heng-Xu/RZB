"""Task 9 test: 端到端冒烟(subprocess 跑 scripts/run_all.py --skip-gen)。

断言:exit 0、stdout 含汇总块("ΔC" 字样)、3表6图产物存在且 mtime 更新、
manifest.json 含全部输入 sha256(与 milp_planner._write_results 落盘的键一致)。
先 RED(run_all.py 不存在/未跑通时必失败)后 GREEN(scripts/run_all.py 实现后跑通)。
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "results" / "runs" / "synthetic-m1"

TAB_FILES = [
    "tables/tab_A_zonematrix.csv", "tables/tab_A_zonematrix.md",
    "tables/tab_B_lookup.csv", "tables/tab_B_lookup.md",
    "tables/tab_C_redline.csv", "tables/tab_C_redline.md",
]
FIG_FILES = [
    f"figures/fig_V{i}_{n}.png"
    for i, n in [(1, "grid"), (2, "netload"), (3, "waterfall"),
                 (4, "rcost"), (5, "heatmap"), (6, "split")]
]
ALL_OUTPUTS = TAB_FILES + FIG_FILES

_EXPECTED_SHA_KEYS = {
    "stations.csv", "transformers.csv", "ties.csv", "pv_registry.csv",
    "pv_profiles/shape_xuzhou.csv", "params.yaml", "load_curves(all)",
}


def _mtimes() -> dict[str, float | None]:
    return {p: (ROOT / p).stat().st_mtime if (ROOT / p).exists() else None
            for p in ALL_OUTPUTS}


def test_run_all_skip_gen_end_to_end():
    """完成判据(task-9-brief Step 4):单命令全绿。"""
    before = _mtimes()

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_all.py"), "--skip-gen"],
        cwd=ROOT, capture_output=True, text=True, timeout=600,
    )
    assert result.returncode == 0, (result.stdout[-3000:] + "\n" + result.stderr[-3000:])
    assert "ΔC" in result.stdout

    for p in ALL_OUTPUTS:
        fp = ROOT / p
        assert fp.exists(), f"缺产物 {p}"
        if before[p] is not None:
            assert fp.stat().st_mtime > before[p], f"{p} mtime 未更新"

    manifest = json.loads((RUN_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert _EXPECTED_SHA_KEYS <= set(manifest["input_sha256"])
