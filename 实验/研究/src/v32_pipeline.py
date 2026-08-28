"""v3.2 正式入口兼容层。

v3.2 的正式政策实验必须使用 2021 年实际在役资产共同起点，并由存量豁免
的增量 Rcap 规则约束规划期新增容量。旧的 v32_pipeline 候选实现曾把
2×P_plus_2021 作为主规划起点并生成退役候选，不能继续作为正式入口。

保留本模块名是为了兼容已有脚本；实际工作统一委托给
src.v32_actual_pipeline.run_v32_actual_baseline。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from src import v32_actual_pipeline


def run_v32_pipeline(
    project_root: Path,
    processed_root: Path,
    run_dir: Path,
) -> dict[str, Any]:
    """运行 v3.2 实际资产主流水线。

    run_v32_pipeline 是历史调用名，不再代表标准化 2.0 反事实基线。
    """
    return v32_actual_pipeline.run_v32_actual_baseline(
        Path(project_root),
        Path(processed_root),
        Path(run_dir),
    )
