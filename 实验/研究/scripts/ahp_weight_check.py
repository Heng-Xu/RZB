#!/usr/bin/env python3
"""第五章指标赋权的层次分析法计算与扰动检验（报告素材，模型假设登记用）。

判断矩阵由课题组按 Saaty 1~9 标度结合徐州地区规划运行经验构造，属模型假设；
本脚本完成三件事并落盘可追溯产物：
1. 计算四个准则维度的归一化权重、最大特征值与一致性比率 CR；
2. 对判断矩阵全部非对角元素做 ±20% 扰动，检验权重排序稳定性；
3. 说明片区分类依据为正式矩阵中的离散触发类型，不依赖权重连续取值。

用法：conda run -n xuzhou110kv_clr python scripts/ahp_weight_check.py \
        --output ../../研究报告/初稿/数据摘要/第五章_指标权重与扰动检验.csv
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

# 准则维度顺序：容量配置 A、新能源渗透 B、反向承载 C、经济代价 D
DIMENSIONS = ["容量配置", "新能源渗透", "反向承载", "经济代价"]

# 课题组判断矩阵（模型假设）：A>B>C>D，B 与 D 接近
JUDGMENT = np.array([
    [1.0, 3.0, 2.0, 4.0],
    [1.0 / 3.0, 1.0, 1.0 / 2.0, 1.0],
    [1.0 / 2.0, 2.0, 1.0, 3.0],
    [1.0 / 4.0, 1.0, 1.0 / 3.0, 1.0],
])

RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}


def principal_weights(matrix: np.ndarray) -> tuple[np.ndarray, float, float]:
    """返回归一化主特征向量、lambda_max 与一致性比率 CR。"""
    values, vectors = np.linalg.eig(matrix)
    index = int(np.argmax(values.real))
    lam_max = float(values[index].real)
    weights = np.abs(vectors[:, index].real)
    weights = weights / weights.sum()
    n = matrix.shape[0]
    ci = (lam_max - n) / (n - 1) if n > 1 else 0.0
    cr = ci / RI[n] if RI[n] > 0 else 0.0
    return weights, lam_max, cr


def perturbed(matrix: np.ndarray, i: int, j: int, factor: float) -> np.ndarray:
    """将 i,j 元素乘 factor、j,i 元素乘 1/factor，其余不变。"""
    result = matrix.copy()
    result[i, j] *= factor
    result[j, i] /= factor
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    weights, lam_max, cr = principal_weights(JUDGMENT)
    base_order = sorted(range(len(DIMENSIONS)), key=lambda k: -weights[k])

    rows: list[dict[str, object]] = []
    for k, name in enumerate(DIMENSIONS):
        rows.append({
            "case": "base",
            "perturbed_pair": "-",
            "factor": 1.0,
            "dimension": name,
            "weight": round(float(weights[k]), 6),
        })

    order_stable = True
    details: list[str] = []
    n = len(DIMENSIONS)
    for i, j in itertools.combinations(range(n), 2):
        for factor in (0.8, 1.2):
            matrix = perturbed(JUDGMENT, i, j, factor)
            w, _, cr_p = principal_weights(matrix)
            order = sorted(range(n), key=lambda k: -w[k])
            stable = order == base_order
            order_stable &= stable
            details.append(
                f"{DIMENSIONS[i]}-{DIMENSIONS[j]} x{factor}: "
                + ">".join(DIMENSIONS[k] for k in order)
                + ("（稳定）" if stable else "（变化）")
            )
            for k, name in enumerate(DIMENSIONS):
                rows.append({
                    "case": "perturb",
                    "perturbed_pair": f"{DIMENSIONS[i]}-{DIMENSIONS[j]}",
                    "factor": factor,
                    "dimension": name,
                    "weight": round(float(w[k]), 6),
                })

    frame = pd.DataFrame(rows)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out, index=False, encoding="utf-8-sig")

    summary = {
        "dimensions": DIMENSIONS,
        "judgment_matrix": JUDGMENT.tolist(),
        "weights": {name: round(float(weights[k]), 4) for k, name in enumerate(DIMENSIONS)},
        "lambda_max": round(lam_max, 4),
        "consistency_ratio": round(cr, 4),
        "cr_threshold": 0.10,
        "weight_order_stable_under_pm20pct": bool(order_stable),
        "perturbation_details": details,
        "classification_note": "片区分类依据正式推荐矩阵中的离散触发类型与措施字段，不依赖权重连续取值",
        "evidence_type": "model_assumption_ahp_judgment_with_perturbation_check",
        "output_csv": str(out),
        "output_sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
    }
    sidecar = out.with_name(out.stem + "_manifest.json")
    sidecar.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"权重：{summary['weights']}")
    print(f"lambda_max={summary['lambda_max']}, CR={summary['consistency_ratio']}（阈值 0.10）")
    print(f"±20% 扰动下权重排序稳定：{order_stable}")
    for line in details:
        print(" ", line)
    print(f"已生成 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
