#!/usr/bin/env python3
"""研究报告语言逻辑、术语科学性与人类可读性最低门禁。

本脚本不尝试用规则替代人工审稿，只负责把项目中已经明确禁止的内部口吻、
术语漂移、明显超长句和质量合同缺失变成可自动阻断的构建错误。
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_CONTRACT_PHRASES = [
    "语言逻辑连贯",
    "术语科学准确",
    "符合人类阅读习惯",
]

REQUIRED_REPORT_TERMS = [
    "实际物理容载比",
    "2022—2025年规划期累计在役等年成本",
    "110 kV线路统计负载余度",
    "弹性容载比样本支持参考矩阵",
    "样本内一致性检查",
]

FORBIDDEN_INTERNAL_PHRASES = [
    "GitHub Actions",
    "artifact",
    "manifest",
    "pipeline",
    "fallback",
    "正式v3.2模型",
    "正式v3.2优化模型",
    "二次科学审查表明",
    "冻结结果",
    "脚本验证通过",
    "程序验证通过",
    "程序已复现",
    "脚本已复现",
    "提交SHA",
    "运行ID",
    "任务ID",
]

FORBIDDEN_OVERCLAIMS = [
    "充分证明",
    "全面证明",
    "完全证明",
    "显著提升了科学性",
    "显著提升科学性",
    "全面领先",
]

FORBIDDEN_TERM_DRIFT = [
    "网络容量支撑裕度",
    "年化规划成本/万元·年⁻¹",
    "独立查询规则进行反向验证",
    "独立查询结果与正式优化结果一致",
    "推荐上限3.0",
]

# 这些字段/文件名如果出现在对外正文，通常意味着内部实现信息泄漏。
PROGRAM_TOKEN_PATTERNS = [
    r"\b[a-z]+_[a-z][a-z0-9_]*\b",
    r"(?:^|[\s`'\"])(?:[^\s`'\"]+\.py|[^\s`'\"]+\.csv)(?=$|[\s`'\"，。；：])",
    r"results/runs",
]


def remove_non_prose(text: str) -> str:
    """移除公式、代码块、表格和图片标记，保留正文用于语言检查。"""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            continue
        if stripped.startswith("#"):
            continue
        if re.fullmatch(r"（\d+-\d+）", stripped):
            continue
        lines.append(line)
    return "\n".join(lines)


def body_without_references(text: str) -> str:
    return text.split("# 参考文献", 1)[0]


def prose_paragraphs(text: str) -> list[str]:
    prose = remove_non_prose(body_without_references(text))
    paras = []
    for block in re.split(r"\n\s*\n", prose):
        p = " ".join(line.strip() for line in block.splitlines() if line.strip())
        if not p:
            continue
        # 纯列表项不参与段长统计，但其内容仍参与禁词扫描。
        paras.append(p)
    return paras


def sentence_candidates(paragraph: str) -> list[str]:
    return [s.strip() for s in re.split(r"[。！？!?]", paragraph) if s.strip()]


def run_check(markdown: Path, contract: Path, output: Path | None) -> dict:
    source = markdown.read_text(encoding="utf-8-sig")
    contract_text = contract.read_text(encoding="utf-8-sig") if contract.exists() else ""
    body = body_without_references(source)
    prose = remove_non_prose(body)
    issues: list[str] = []
    warnings: list[str] = []

    if not contract.exists():
        issues.append(f"缺少终稿写作质量合同：{contract}")
    else:
        for phrase in REQUIRED_CONTRACT_PHRASES:
            if phrase not in contract_text:
                issues.append(f"质量合同缺少最高优先级原则：{phrase}")

    for term in REQUIRED_REPORT_TERMS:
        if term not in source:
            issues.append(f"正文缺少统一术语或关键口径：{term}")

    lowered = prose.lower()
    for phrase in FORBIDDEN_INTERNAL_PHRASES:
        if phrase.lower() in lowered:
            issues.append(f"正文含内部开发/审查口吻，不适合甲方终稿：{phrase}")

    for phrase in FORBIDDEN_OVERCLAIMS:
        if phrase in prose:
            issues.append(f"正文含无证据的强结论表达：{phrase}")

    for phrase in FORBIDDEN_TERM_DRIFT:
        if phrase in source:
            issues.append(f"正文含术语漂移或过时口径：{phrase}")

    for pattern in PROGRAM_TOKEN_PATTERNS:
        matches = sorted(set(re.findall(pattern, prose, flags=re.I | re.M)))
        if matches:
            preview = matches[:12]
            issues.append(f"正文含程序式字段/文件表达：{preview}")

    # 可读性硬底线。阈值故意设置得较宽，只阻断明显失控文本，避免替代人工判断。
    long_paragraphs = []
    long_sentences = []
    for idx, paragraph in enumerate(prose_paragraphs(source), start=1):
        compact = re.sub(r"\s+", "", paragraph)
        if len(compact) > 900:
            long_paragraphs.append((idx, len(compact), compact[:60]))
        for sentence in sentence_candidates(paragraph):
            compact_sentence = re.sub(r"\s+", "", sentence)
            if len(compact_sentence) > 220:
                long_sentences.append((idx, len(compact_sentence), compact_sentence[:70]))

    for idx, length, preview in long_paragraphs[:10]:
        issues.append(f"第{idx}个正文段落过长（{length}字符），需按逻辑拆分：{preview}…")
    for idx, length, preview in long_sentences[:10]:
        issues.append(f"第{idx}个正文段落含明显超长句（{length}字符），需重写：{preview}…")

    # 轻量提示：这些不能仅靠机器定性，因此作为 warning，不阻断构建。
    if prose.count("因此") > 25:
        warnings.append("“因此”使用频率较高，人工审查时注意避免机械衔接。")
    if prose.count("本研究") > 80:
        warnings.append("“本研究”重复较多，人工审查时注意句式变化与自然表达。")

    result = {
        "passed": not issues,
        "hard_principles": REQUIRED_CONTRACT_PHRASES,
        "issues": issues,
        "warnings": warnings,
        "markdown": str(markdown),
        "contract": str(contract),
        "note": "自动检查只承担最低门禁；甲方提交前仍需人工逐章通读。",
    }

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if issues:
        for item in issues:
            print(f"[FAIL] {item}")
    else:
        print("[PASS] 语言逻辑、术语科学性与人类可读性自动门禁通过。")
    for item in warnings:
        print(f"[WARN] {item}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    result = run_check(args.markdown, args.contract, args.output)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
