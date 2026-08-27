#!/usr/bin/env python3
"""研究报告去 AI 味 S1 机械扫描（xuzhou-report-writing skill 第 4 节）。

检查项：模板连接词密度（每千字≤1）、空泛动词短语、程度词、句长方差。
用法：python scripts/report_style_scan.py 章节文件.md [章节文件2.md ...]
输出：逐项标记清单（供人工复核后登记审查清单）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TEMPLATES = ["首先", "其次", "再次", "最后", "综上所述", "值得注意的是", "总而言之", "在……背景下", "在...背景下"]
FILLER_VERBS = ["进行了", "作出了", "开展了", "有着重要", "具有重要意义"]
DEGREES = ["显著", "大幅", "明显", "极大", "远远"]


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"[。！？；\n]", text)
    return [p.strip() for p in parts if len(p.strip()) >= 6]


def scan(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    body = re.sub(r"[|#*`>\-\[\]()\d\s]", "", text)
    n_chars = max(len(body), 1)
    n_thousand = n_chars / 1000
    findings: list[str] = []

    for word in TEMPLATES:
        count = text.count(word)
        if count and count / n_thousand > 1.0:
            lines = [i + 1 for i, line in enumerate(text.splitlines()) if word in line]
            findings.append(f"[S1 连接词超限] 「{word}」{count} 次（阈值 {n_thousand:.1f}）行 {lines}")
    for phrase in FILLER_VERBS:
        for i, line in enumerate(text.splitlines(), 1):
            if phrase in line:
                findings.append(f"[S1 空泛动词] 行 {i}: …{line[max(0, line.find(phrase) - 12):line.find(phrase) + 18]}…")
    for word in DEGREES:
        for i, line in enumerate(text.splitlines(), 1):
            if word in line and not re.search(r"\d", line):
                findings.append(f"[S3 程度词无数据] 行 {i}: 「{word}」")

    sentences = split_sentences(text)
    lengths = [len(re.sub(r"[^一-鿿]", "", s)) for s in sentences]
    lengths = [n for n in lengths if n > 0]
    stats = {}
    if lengths:
        mean = sum(lengths) / len(lengths)
        variance = sum((n - mean) ** 2 for n in lengths) / len(lengths)
        stats = {"句子数": len(lengths), "平均句长": round(mean, 1), "句长方差": round(variance, 1)}
        if variance < 40 and len(lengths) >= 10:
            findings.append(f"[S1 句长方差过低] 方差 {variance:.0f} < 40，句式可能机械等长")

    return {"file": str(path), "chars": n_chars, "sentence_stats": stats, "findings": findings}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    total = 0
    for arg in sys.argv[1:]:
        result = scan(Path(arg))
        print(f"\n== {result['file']} （{result['chars']} 字，{result['sentence_stats']}）")
        if not result["findings"]:
            print("  S1/S3 扫描通过，无超限标记。")
            continue
        for item in result["findings"]:
            print(f"  {item}")
            total += 1
    print(f"\n共 {total} 处标记，请人工复核后登记审查清单（S2/S4 需人工执行）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
