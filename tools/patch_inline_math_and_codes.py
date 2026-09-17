#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修正终稿行内公式为Word文字级上下标样式，并清理已有中文映射的资产编码。"""
from pathlib import Path
import re

REPORT = Path('研究报告/终稿/国网徐州公司徐州地区分布式新能源高渗透率地区110kV电网容载比弹性指标优化研究-研究报告终稿.md')
BUILDER = Path('tools/build_report_docx.py')


def patch_report():
    text = REPORT.read_text(encoding='utf-8-sig')

    # 已有明确中文馈线名称的资产编码不在正式中文报告中重复展示。
    for code in ['PZXL-00099', 'PZXL-00097', 'PZXL-00092', 'PZXL-00154', 'PZXL-00161', 'PZXL-00173']:
        text = text.replace(code, '')
    text = re.sub(r'(墩振线|墩西线|墩南线|河东线|河炮线|河镇线)\s+', r'\1', text)

    # TIE-002已有清晰的中文拓扑关系，正文统一称“墩南—河炮既有联络”。
    text = text.replace('墩南线与河炮线之间的既有联络（TIE-002）', '墩南线与河炮线之间的既有联络')
    text = text.replace('TIE-002连接墩南线与河炮线', '墩南线与河炮线之间已形成既有联络')
    text = text.replace('TIE-002', '墩南—河炮既有联络')
    text = text.replace('墩南—河炮既有联络高光伏', '墩南—河炮既有联络高光伏')
    text = text.replace('既有墩南—河炮既有联络', '墩南—河炮既有联络')
    text = text.replace('墩南—河炮既有联络既有联络', '墩南—河炮既有联络')

    # 公式变量说明统一使用行内公式标记，DOCX生成时转换为文字级上下标/斜体数学样式。
    text = text.replace(
        '其中，E_t为时刻t的储能电量，P_c,t和P_d,t分别为充电功率和放电功率。QX-00005具备2025年8760小时连续运行时序，储能SOC按全年序列连续传递；',
        '其中，[[MATH:E_t]] 为时刻 [[MATH:t]] 的储能电量，[[MATH:P_{c,t}]] 和 [[MATH:P_{d,t}]] 分别为充电功率和放电功率。QX-00005具备2025年8760小时连续运行时序，储能荷电状态按全年序列连续传递；'
    )
    text = text.replace(
        '其中，r为折现率，n为设备经济寿命。',
        '其中，[[MATH:r]] 为折现率，[[MATH:n]] 为设备经济寿命。'
    )
    text = text.replace('储能SOC', '储能荷电状态')

    REPORT.write_text(text, encoding='utf-8')


def patch_builder():
    b = BUILDER.read_text(encoding='utf-8')
    start = b.index('def _pandoc_inline_math_element')
    end = b.index('\ndef add_paragraph(', start)
    replacement = r'''def _add_math_run(paragraph, text: str, size: float, *, italic: bool = True,
                  subscript: bool = False, superscript: bool = False):
    """添加文字级数学run；避免OMML在LibreOffice/WPS转换中的兼容性问题。"""
    run = paragraph.add_run(text)
    set_run_fonts(run, size, cjk=CJK)
    run.font.name = LATIN
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), LATIN)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), LATIN)
    run.italic = italic
    run.font.subscript = subscript
    run.font.superscript = superscript
    return run


def _add_inline_math_runs(paragraph, latex: str, size: float):
    """将报告中少量行内数学标记转换为可编辑的斜体/上下标文字，不生成OMML。"""
    latex = latex.strip()
    simple = {"y", "t", "r", "n", "\\beta"}
    if latex in simple:
        _add_math_run(paragraph, "β" if latex == "\\beta" else latex, size)
        return
    if latex == "S_y":
        _add_math_run(paragraph, "S", size)
        _add_math_run(paragraph, "y", size, subscript=True)
        return
    if latex == "P_y^{+}":
        _add_math_run(paragraph, "P", size)
        _add_math_run(paragraph, "y", size, subscript=True)
        _add_math_run(paragraph, "+", size, italic=False, superscript=True)
        return
    if latex == "C_{\\mathrm{inv}}":
        _add_math_run(paragraph, "C", size)
        _add_math_run(paragraph, "inv", size, italic=False, subscript=True)
        return
    if latex == "C_{\\mathrm{om}}":
        _add_math_run(paragraph, "C", size)
        _add_math_run(paragraph, "om", size, italic=False, subscript=True)
        return
    if latex == "E_t":
        _add_math_run(paragraph, "E", size)
        _add_math_run(paragraph, "t", size, subscript=True)
        return
    if latex in {"P_{c,t}", "P_{d,t}"}:
        _add_math_run(paragraph, "P", size)
        _add_math_run(paragraph, "c,t" if "c,t" in latex else "d,t", size, subscript=True)
        return
    if latex in {"\\cos\\varphi_{\\mathrm{tr}}", "\\cos\\varphi_{\\mathrm{tr}}\\approx1.0"}:
        _add_math_run(paragraph, "cos ", size, italic=False)
        _add_math_run(paragraph, "φ", size)
        _add_math_run(paragraph, "tr", size, italic=False, subscript=True)
        if "approx" in latex:
            _add_math_run(paragraph, " ≈ 1.0", size, italic=False)
        return
    if latex == "R_{\\mathrm{cap}}":
        _add_math_run(paragraph, "R", size)
        _add_math_run(paragraph, "cap", size, italic=False, subscript=True)
        return

    # 未预定义的简单标记以数学斜体文本兜底；禁止将LaTeX源码裸露到Word正文。
    clean = (latex.replace('\\mathrm{', '').replace('}', '')
                  .replace('\\varphi', 'φ').replace('\\beta', 'β')
                  .replace('\\approx', '≈').replace('\\cos', 'cos '))
    _add_math_run(paragraph, clean, size)


def _add_runs(paragraph, text: str, size: float, *, bold: bool = False, cjk: str = CJK):
    marker = re.compile(r"\[\[MATH:(.+?)\]\]")
    for segment, segment_bold in _split_bold(_clean_inline(text), bold):
        cursor = 0
        for match in marker.finditer(segment):
            if match.start() > cursor:
                run = paragraph.add_run(segment[cursor:match.start()])
                set_run_fonts(run, size, bold=segment_bold, cjk=cjk)
            _add_inline_math_runs(paragraph, match.group(1), size)
            cursor = match.end()
        if cursor < len(segment):
            run = paragraph.add_run(segment[cursor:])
            set_run_fonts(run, size, bold=segment_bold, cjk=cjk)

'''
    b = b[:start] + replacement + b[end+1:]
    BUILDER.write_text(b, encoding='utf-8')


def main():
    patch_report()
    patch_builder()
    text = REPORT.read_text(encoding='utf-8')
    assert 'PZXL-' not in text
    assert 'TIE-002' not in text
    assert '储能SOC' not in text
    print('patched inline math compatibility and visible codes')


if __name__ == '__main__':
    main()
