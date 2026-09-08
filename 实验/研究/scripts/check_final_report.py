#!/usr/bin/env python3
"""校验终稿正文、Word、PDF、关键数值及样本参考矩阵，并生成内部追溯表。"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
from docx import Document
from lxml import etree


FORBIDDEN = [
    ".py", ".csv", "results/runs", "capacity_action_delta_mva", "storage_modules",
    "cumulative_eac", "physical_clr", "ROBUST", "WEAKLY_SENSITIVE", "SENSITIVE",
    "证据链", "候选包", "artifact", "manifest", "pipeline", "fallback",
    "GitHub Actions", "case id", "task id",
]


def strip_math(text: str) -> str:
    return re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)


def pdf_page_text(pdf: Path, page: int) -> str:
    result = subprocess.run(
        ["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def run_check(root: Path, markdown: Path, docx: Path, pdf: Path, output_dir: Path) -> dict:
    source = markdown.read_text(encoding="utf-8-sig")
    prose = strip_math(source)
    issues: list[str] = []

    chapters = re.findall(r"^# 第([一二三四五六七八九十]+)章", source, re.M)
    if chapters != list("一二三四五六七八九十"):
        issues.append(f"章节顺序异常：{chapters}")
    for token in FORBIDDEN:
        if token.lower() in prose.lower():
            issues.append(f"正文含禁止表达：{token}")
    snake = sorted(set(re.findall(r"\b[a-z]+_[a-z][a-z0-9_]*\b", prose)))
    if snake:
        issues.append(f"正文含程序式字段：{snake}")

    # 科学语义硬校验：正式目标是2022—2025年累计在役等年成本，不是某一年度年化成本。
    required_semantics = [
        "2022—2025年规划期累计在役等年成本",
        "规划期累计在役等年成本/万元",
        "样本内回代一致性检查",
        "不构成独立或外部验证",
        "110 kV线路统计负载余度",
    ]
    for phrase in required_semantics:
        if phrase not in source:
            issues.append(f"缺少关键科学口径：{phrase}")
    forbidden_semantics = [
        "年化规划成本/万元·年⁻¹",
        "年化规划成本188.1800万元/年",
        "年化规划成本481.9566万元/年",
        "年化规划成本1745.5283万元/年",
        "年化规划成本3359.0522万元/年",
        "独立查询结果与正式优化结果一致",
        "独立查询规则进行反向验证",
        "网络容量支撑裕度",
    ]
    for phrase in forbidden_semantics:
        if phrase in source:
            issues.append(f"正文仍含过时或过强口径：{phrase}")
    if re.search(r"(?<!\$)\$[^$]+\$(?!\$)", source):
        issues.append("正文存在行内LaTeX，DOCX渲染可能显示源码，应改为普通文字或显示公式")

    figure_refs = re.findall(r"!\[(图\s*\d+-\d+[^\]]*)\]\(([^)]+)\)", source)
    if len(figure_refs) != 6:
        issues.append(f"图件数量应为6，实际为{len(figure_refs)}")
    for _, relative in figure_refs:
        if not (markdown.parent / relative).exists():
            issues.append(f"图件不存在：{relative}")

    captions = re.findall(r"^\*\*表\s*(\d+-\d+)", source, re.M)
    expected_tables = ["2-1", "3-1", "4-1", "5-1", "5-2", "6-1", "7-1", "7-1", "7-2", "7-3"]
    if captions != expected_tables:
        issues.append(f"表编号异常：{captions}")
    for number in sorted(set(captions)):
        if len(re.findall(rf"表\s*{re.escape(number)}", source)) < 2:
            issues.append(f"表{number}未被正文明确引用")
    for caption, _ in figure_refs:
        number = re.search(r"\d+-\d+", caption).group(0)
        if len(re.findall(rf"图\s*{re.escape(number)}", source)) < 2:
            issues.append(f"图{number}未被正文明确引用")

    equation_numbers = re.findall(r"^（(\d+-\d+)）$", source, re.M)
    expected_equations = [f"3-{i}" for i in range(1, 9)] + [f"4-{i}" for i in range(1, 5)]
    if equation_numbers != expected_equations:
        issues.append(f"公式编号异常：{equation_numbers}")

    body_before_references = source.split("# 参考文献", 1)[0]
    cited: set[int] = set()
    for content in re.findall(r"\[([0-9,\-]+)\]", body_before_references):
        for part in content.split(","):
            if "-" in part:
                lo, hi = map(int, part.split("-", 1))
                cited.update(range(lo, hi + 1))
            else:
                cited.add(int(part))
    if cited != set(range(1, 21)):
        issues.append(f"参考文献正文引用覆盖异常：{sorted(cited)}")

    formal_path = root / "实验/研究/results/runs/real-2021-2025-v32-frozen/formal_matrix_110kv.csv"
    formal = pd.read_csv(formal_path).set_index("region_id")
    checks = [
        ("第五章", "表5-1", "QX-00001无上限实际物理容载比", formal.loc["QX-00001", "PATH_OPT_CLR_UNBOUNDED_clr_2025"], "| QX-00001 | 无上限 | 2.3597466 | 50 | 19 | 1.9 | 4.085 | 188.1800 |", "2.3597466"),
        ("第五章", "表5-1", "QX-00001控制值2.0实际物理容载比", formal.loc["QX-00001", "PATH_OPT_CLR_LE_2_clr_2025"], "| QX-00001 | 控制值2.0 | 2.2679276 | 0 | 138 | 13.8 | 29.670 | 481.9566 |", "2.2679276"),
        ("第五章", "表5-1", "QX-00001无上限累计在役等年成本", formal.loc["QX-00001", "PATH_OPT_CLR_UNBOUNDED_cumulative_eac"], "| QX-00001 | 无上限 | 2.3597466 | 50 | 19 | 1.9 | 4.085 | 188.1800 |", "188.1800"),
        ("第五章", "表5-1", "QX-00001控制值2.0累计在役等年成本", formal.loc["QX-00001", "PATH_OPT_CLR_LE_2_cumulative_eac"], "| QX-00001 | 控制值2.0 | 2.2679276 | 0 | 138 | 13.8 | 29.670 | 481.9566 |", "481.9566"),
        ("第五章", "表5-1", "QX-00005无上限实际物理容载比", formal.loc["QX-00005", "PATH_OPT_CLR_UNBOUNDED_clr_2025"], "| QX-00005 | 无上限 | 2.1715720 | 50 | 465 | 46.5 | 99.975 | 1745.5283 |", "2.1715720"),
        ("第五章", "表5-1", "QX-00005控制值2.0实际物理容载比", formal.loc["QX-00005", "PATH_OPT_CLR_LE_2_clr_2025"], "| QX-00005 | 控制值2.0 | 2.1192953 | 0 | 962 | 96.2 | 206.830 | 3359.0522 |", "2.1192953"),
        ("第五章", "表5-1", "QX-00005无上限累计在役等年成本", formal.loc["QX-00005", "PATH_OPT_CLR_UNBOUNDED_cumulative_eac"], "| QX-00005 | 无上限 | 2.1715720 | 50 | 465 | 46.5 | 99.975 | 1745.5283 |", "1745.5283"),
        ("第五章", "表5-1", "QX-00005控制值2.0累计在役等年成本", formal.loc["QX-00005", "PATH_OPT_CLR_LE_2_cumulative_eac"], "| QX-00005 | 控制值2.0 | 2.1192953 | 0 | 962 | 96.2 | 206.830 | 3359.0522 |", "3359.0522"),
        ("第七章", "表7-2", "QX-00001推荐下限", formal.loc["QX-00001", "rcap_robust_near_optimal_lower"], "| 技术可行；当前样本点 | 0.973 | 0.088 | 11.36% | 6.22% |", "2.50"),
        ("第七章", "表7-2", "QX-00005推荐下限", formal.loc["QX-00005", "rcap_robust_near_optimal_lower"], "| 技术可行；当前样本点 | 1.527 | 0.063 | 4.21% | 6.92% |", "2.30"),
    ]
    trace_rows = []
    for chapter, item, metric, official, context, report_value in checks:
        start = source.find(context)
        passed = start >= 0 and report_value in source[start:start + len(context) + 160]
        if not passed:
            issues.append(f"报告缺少关键值：{metric}={report_value}")
        trace_rows.append([chapter, item, metric, report_value, f"110 kV正式计算结果：{official}", "通过" if passed else "不通过"])

    if "2.50～" in source or "2.30～" in source:
        issues.append("正文存在可能的人为推荐上限")
    backtest_path = root / "实验/研究/reports/report_reconstruction/matrix_backtest.csv"
    backtest = pd.read_csv(backtest_path)
    if len(backtest) != 8 or not backtest["explains_formal_optimization"].all():
        issues.append("样本参考规则未合理解释全部已知片区")
    if int(backtest["matches_formal_optimization"].sum()) != 7:
        issues.append("样本回代直接一致片区数量应为7，QX-00007应保留为缺失数据例外")
    if backtest["artificial_upper_bound"].any():
        issues.append("参考矩阵存在人为上限")

    matrix_module_path = root / "实验/研究/src/report_interval_matrix.py"
    module_spec = importlib.util.spec_from_file_location("report_interval_matrix_check", matrix_module_path)
    matrix_module = importlib.util.module_from_spec(module_spec)
    assert module_spec.loader is not None
    module_spec.loader.exec_module(matrix_module)
    complete_indicators = [0.973, 0.088, 0.1136, 0.0622]
    for missing_index in range(4):
        values = complete_indicators.copy()
        values[missing_index] = None
        result = matrix_module.query_interval_matrix(
            technical_feasible=True,
            source_load_scale_ratio=values[0],
            local_reverse_flow_ratio=values[1],
            network_capacity_support_margin=values[2],
            positive_peak_cagr_2021_2025=values[3],
        )
        if result[1] != "D":
            issues.append(f"第{missing_index + 1}项核心指标缺失时未进入数据不足分支")
    for forbidden_range in ("0.90～1.25", "1.161～1.523", "大于1.25且不高于1.60"):
        if forbidden_range in source:
            issues.append(f"参考矩阵仍含单样本外推范围：{forbidden_range}")

    word = Document(docx)
    with ZipFile(docx) as archive:
        document_bytes = archive.read("word/document.xml")
        document_xml = document_bytes.decode("utf-8")
    xml_root = etree.fromstring(document_bytes)
    math_count = len(xml_root.findall(".//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath"))
    if math_count != 12:
        issues.append(f"Word原生公式数量应为12，实际为{math_count}")
    if document_xml.count("<w:drawing") != 6:
        issues.append("Word嵌入图件数量不是6")
    if len(word.tables) != 10:
        issues.append(f"Word表格数量应为10，实际为{len(word.tables)}")
    if "\\frac" in document_xml or "\\Delta" in document_xml or "$S_" in document_xml:
        issues.append("Word存在未转换的公式源码")
    for number in expected_equations:
        if f"（{number}）" not in document_xml:
            issues.append(f"Word缺少公式编号（{number}）")
    for table in word.tables:
        if len(table.rows) > 1 and table.rows[0]._tr.get_or_add_trPr().find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tblHeader") is None:
            issues.append("Word表格缺少重复表头设置")
            break

    info = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, text=True).stdout
    match = re.search(r"Pages:\s+(\d+)", info)
    page_count = int(match.group(1)) if match else 0
    if page_count < 30:
        issues.append(f"PDF页数异常：{page_count}")
    sparse_pages = []
    for page in range(1, page_count + 1):
        text = pdf_page_text(pdf, page)
        if len(re.sub(r"\s+", "", text)) < 20:
            sparse_pages.append(page)
    if sparse_pages:
        issues.append(f"PDF存在疑似空白页：{sparse_pages}")
    full_pdf_text = subprocess.run(["pdftotext", str(pdf), "-"], check=True, capture_output=True, text=True).stdout
    if re.search(r"\\(?:Delta|frac|mathrm|left|right|mbox)", full_pdf_text) or "$S_" in full_pdf_text:
        issues.append("PDF存在未编译公式源码")
    for phrase in ("2022—2025年累计在役等年成本/万元", "110 kV线路统计负载余度", "局部最大反向潮流比例"):
        if phrase not in source:
            issues.append(f"术语或单位缺失：{phrase}")

    figure_script = (root / "实验/研究/scripts/build_final_report_figures.py").read_text(encoding="utf-8")
    for old_term in (
        "累计年化成本 / 万元",
        "年化规划成本 / （万元/年）",
        "线路容量最小余度",
        "网络容量支撑裕度",
        "局部最大反向功率比",
    ):
        if old_term in figure_script:
            issues.append(f"图件生成文字未统一：{old_term}")
    for new_term in ("规划期累计在役等年成本 / 万元", "110 kV线路统计负载余度"):
        if new_term not in figure_script:
            issues.append(f"图件生成脚本缺少新口径：{new_term}")

    output_dir.mkdir(parents=True, exist_ok=True)
    trace_path = output_dir / "数值追溯表.csv"
    with trace_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["报告章节", "表/图", "指标", "报告值", "正式结果来源", "校验结果"])
        writer.writerows(trace_rows)

    result = {
        "passed": not issues,
        "issues": issues,
        "chapter_count": len(chapters),
        "figure_count": len(figure_refs),
        "table_count": len(word.tables),
        "native_math_count": math_count,
        "pdf_pages": page_count,
        "matrix_backtest_regions": len(backtest),
        "trace_rows": len(trace_rows),
    }
    (output_dir / "自动检查结果.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--docx", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run_check(
        args.root.resolve(),
        args.markdown.resolve(),
        args.docx.resolve(),
        args.pdf.resolve(),
        args.output_dir.resolve(),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
