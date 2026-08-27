"""Task 8 tests: 三表六图脚手架。

按 task-8-brief.md Step 1 逐脚本 subprocess 调用,断言:产物文件存在、
表A md 首个数据行 label=="推荐容载比R(2030)"、PNG 尺寸>10KB。
先 RED(脚本/产物不存在时必失败)后 GREEN(scripts/*.py 实现后跑通)。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "synthetic-m1"

TABLE_SCRIPTS = ["tab_A_zonematrix", "tab_B_lookup", "tab_C_redline"]
FIG_SCRIPTS = ["fig_V1_grid", "fig_V2_netload", "fig_V3_waterfall",
               "fig_V4_rcost", "fig_V5_heatmap", "fig_V6_split"]
ALL_SCRIPTS = TABLE_SCRIPTS + FIG_SCRIPTS


def _run(name: str, timeout: int = 90) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / f"{name}.py"), "--run", RUN_ID],
        cwd=ROOT, capture_output=True, text=True, timeout=timeout,
    )


@pytest.mark.parametrize("name", TABLE_SCRIPTS)
def test_table_script_runs_and_writes_outputs(name):
    result = _run(name)
    assert result.returncode == 0, result.stderr[-2000:]
    assert (ROOT / "tables" / f"{name}.csv").exists()
    md = ROOT / "tables" / f"{name}.md"
    assert md.exists()
    assert len(md.read_text(encoding="utf-8")) > 0


@pytest.mark.parametrize("name", FIG_SCRIPTS)
def test_fig_script_runs_and_writes_outputs(name):
    timeout = 180 if name == "fig_V4_rcost" else 60
    result = _run(name, timeout=timeout)
    assert result.returncode == 0, result.stderr[-2000:]
    png = ROOT / "figures" / f"{name}.png"
    assert png.exists()
    assert png.stat().st_size > 10 * 1024, f"{png} 过小,疑似空图/渲染失败"
    assert (ROOT / "figures" / f"{name}.data.csv").exists()


def test_table_a_first_row_label_is_recommended_r():
    _run("tab_A_zonematrix")
    md_path = ROOT / "tables" / "tab_A_zonematrix.md"
    lines = [l for l in md_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    header_lines = [l for l in lines if l.startswith("|")]
    data_lines = header_lines[2:]  # 0=表头 1=分隔线 2..=数据行
    assert data_lines, "表A md 无数据行"
    first_cells = [c.strip() for c in data_lines[0].split("|")[1:-1]]
    label = first_cells[1]  # 列顺序:板块, 指标, Z1..Z5
    assert label == "推荐容载比R(2030)"


def test_table_a_recommended_r_value_is_bold():
    _run("tab_A_zonematrix")
    md_path = ROOT / "tables" / "tab_A_zonematrix.md"
    lines = [l for l in md_path.read_text(encoding="utf-8").splitlines() if l.startswith("|")]
    first_data = lines[2]
    cells = [c.strip() for c in first_data.split("|")[1:-1]]
    assert all(c.startswith("**") and c.endswith("**") for c in cells[2:])


def test_all_scripts_present():
    for name in ALL_SCRIPTS:
        assert (ROOT / "scripts" / f"{name}.py").exists(), f"缺 scripts/{name}.py"
    assert (ROOT / "scripts" / "_common.py").exists()
