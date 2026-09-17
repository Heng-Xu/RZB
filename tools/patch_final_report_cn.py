#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性规范终稿中文术语、行内公式、显示公式行距与图件样式。"""
from pathlib import Path
import re

REPORT = Path('研究报告/终稿/国网徐州公司徐州地区分布式新能源高渗透率地区110kV电网容载比弹性指标优化研究-研究报告终稿.md')
BUILDER = Path('tools/build_report_docx.py')
FIGS = Path('实验/研究/scripts/build_final_report_figures.py')
TIEFIG = Path('实验/研究/scripts/build_10kv_reverse_transfer_figure.py')
QA = Path('实验/研究/scripts/check_final_report.py')


def patch_report() -> None:
    text = REPORT.read_text(encoding='utf-8-sig')
    replacements = [
        ('弹性容载比规划控制值（以下简称Rcap）', '弹性容载比规划控制值（公式中记为[[MATH:R_{\\mathrm{cap}}]]）'),
        ('Rcap规划控制值', '弹性容载比规划控制值'),
        ('Rcap控制值', '弹性容载比规划控制值'),
        ('Rcap=2.0', '弹性容载比规划控制值为2.0'),
        ('Rcap较紧', '弹性容载比规划控制值较紧'),
        ('Rcap上限', '弹性容载比规划控制值上限'),
        ('Rcap范围', '弹性容载比规划控制值范围'),
        ('Rcap建议', '弹性容载比规划控制值建议'),
        ('Rcap专项', '弹性容载比专项'),
        ('Rcap扫描', '弹性容载比规划控制值扫描'),
        ('Rcap区间', '弹性容载比规划控制区间'),
        ('Rcap取值', '弹性容载比规划控制值取值'),
        ('Rcap不是', '弹性容载比规划控制值不是'),
        ('Rcap并非', '弹性容载比规划控制值并非'),
        ('Rcap不', '弹性容载比规划控制值不'),
        ('Rcap的', '弹性容载比规划控制值的'),
        ('Rcap仍', '弹性容载比规划控制值仍'),
        ('Rcap变化', '弹性容载比规划控制值变化'),
        ('Rcap', '弹性容载比规划控制值'),
        ('AHP判断矩阵', '层次分析法判断矩阵'),
        ('AHP权重值', '层次分析法权重值'),
        ('AHP结果', '层次分析法结果'),
        ('AHP部分', '层次分析法部分'),
        ('SOC运行范围', '荷电状态运行范围'),
        ('GIS坐标', '地理信息系统坐标'),
        ('墩南线PZXL-00092', '墩南线'),
        ('河炮线PZXL-00161', '河炮线'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)

    text = text.replace(
        '研究对象为徐州地区8个110 kV典型片区，片区名称统一采用QX编号。',
        '研究对象为徐州地区8个110 kV典型片区。现有正式数据成果中尚未形成可核验的“样本编码—中文片区名称”统一映射，因此对暂无法确认中文名称的样本仅保留单一编码标识，待正式名称核定后统一替换。'
    )
    text = text.replace('其中，墩南线与河炮线之间的TIE-002作为典型案例',
                        '其中，墩南线与河炮线之间的既有联络（TIE-002）作为典型案例')
    text = text.replace('以TIE-002为案例', '以墩南—河炮既有联络为案例')
    text = text.replace('### 6.3.1 TIE-002高光伏跨站供电边界重构案例验证',
                        '### 6.3.1 墩南—河炮既有联络高光伏跨站供电边界重构案例验证')
    text = text.replace('**表 6-3 TIE-002高光伏跨站反向功率转移规划结果**',
                        '**表 6-3 墩南—河炮既有联络高光伏跨站反向功率转移规划结果**')
    text = text.replace('TIE-002案例', '墩南—河炮既有联络案例')
    text = text.replace('TIE-002通道', '墩南—河炮既有联络通道')
    text = text.replace('既有TIE-002', '墩南—河炮既有联络')

    text = text.replace(
        '式中，S_y为第y年在役变电总容量；P_y^+为同一规划路径下重新计算的正向年最大供电负荷。考虑储能充放电和局部互济后，P_y^+由净负荷序列确定：',
        '式中，[[MATH:S_y]] 为第 [[MATH:y]] 年在役变电总容量；[[MATH:P_y^{+}]] 为同一规划路径下重新计算的正向年最大供电负荷。考虑储能充放电和局部互济后，[[MATH:P_y^{+}]] 由净负荷序列确定：'
    )
    text = text.replace('式中，C_inv为初始投资，C_om为年固定运维成本。',
                        '式中，[[MATH:C_{\\mathrm{inv}}]] 为初始投资，[[MATH:C_{\\mathrm{om}}]] 为年固定运维成本。')
    text = text.replace(
        '式中，cosφtr为跨站反向功率转移的功率因数；β为反向功率通道控制系数。依据本项目专题分析采用的反向潮流控制条件，β取0.80。当前高光伏规划案例按cosφtr≈1.0进行容量换算。',
        '式中，[[MATH:\\cos\\varphi_{\\mathrm{tr}}]] 为跨站反向功率转移的功率因数；[[MATH:\\beta]] 为反向功率通道控制系数。依据本项目专题分析采用的反向潮流控制条件，[[MATH:\\beta]] 取0.80。当前高光伏规划案例按 [[MATH:\\cos\\varphi_{\\mathrm{tr}}\\approx1.0]] 进行容量换算。'
    )
    REPORT.write_text(text, encoding='utf-8')


def patch_builder() -> None:
    b = BUILDER.read_text(encoding='utf-8')
    exact = '''def _set_exact_line_spacing(paragraph, line_twips: int = BODY_LINE_TWIPS) -> None:\n    ppr = paragraph._p.get_or_add_pPr()\n    spacing = ppr.find(qn("w:spacing"))\n    if spacing is None:\n        spacing = OxmlElement("w:spacing")\n        ppr.append(spacing)\n    spacing.set(qn("w:line"), str(line_twips))\n    spacing.set(qn("w:lineRule"), "exact")\n'''
    if '_set_at_least_line_spacing' not in b:
        addition = exact + '''\n\ndef _set_at_least_line_spacing(paragraph, line_twips: int) -> None:\n    """公式段落采用最小行距，避免分式、根号及上下标被裁切。"""\n    ppr = paragraph._p.get_or_add_pPr()\n    spacing = ppr.find(qn("w:spacing"))\n    if spacing is None:\n        spacing = OxmlElement("w:spacing")\n        ppr.append(spacing)\n    spacing.set(qn("w:line"), str(line_twips))\n    spacing.set(qn("w:lineRule"), "atLeast")\n'''
        if exact not in b:
            raise RuntimeError('cannot locate exact line spacing function')
        b = b.replace(exact, addition)
    b = b.replace('_set_exact_line_spacing(paragraph, int(max(760, (height_pt + 12.0) * 20)))',
                  '_set_at_least_line_spacing(paragraph, int(max(960, (height_pt + 22.0) * 20)))\n        paragraph.paragraph_format.space_before = Pt(4)\n        paragraph.paragraph_format.space_after = Pt(4)')

    old_runs = '''def _add_runs(paragraph, text: str, size: float, *, bold: bool = False, cjk: str = CJK):\n    for segment, segment_bold in _split_bold(_clean_inline(text), bold):\n        run = paragraph.add_run(segment)\n        set_run_fonts(run, size, bold=segment_bold, cjk=cjk)\n'''
    if 'def _pandoc_inline_math_element' not in b:
        new_runs = r'''def _pandoc_inline_math_element(latex: str):
    """将LaTeX片段转换为可嵌入正文段落的Word原生行内公式。"""
    with tempfile.TemporaryDirectory(prefix="report-inline-math-") as tmp_dir:
        tmp = Path(tmp_dir)
        source = tmp / "inline.md"
        output = tmp / "inline.docx"
        source.write_text(f"${latex.strip()}$\n", encoding="utf-8")
        subprocess.run(["pandoc", "--from", "markdown", "--to", "docx", str(source), "-o", str(output)],
                       check=True, capture_output=True, text=True)
        with ZipFile(output) as archive:
            root = etree.fromstring(archive.read("word/document.xml"))
        math = root.find(f".//{{{MATH_NS}}}oMath")
        if math is None:
            raise RuntimeError(f"未生成Word行内公式：{latex}")
        return deepcopy(math)


def _add_runs(paragraph, text: str, size: float, *, bold: bool = False, cjk: str = CJK):
    marker = re.compile(r"\[\[MATH:(.+?)\]\]")
    for segment, segment_bold in _split_bold(_clean_inline(text), bold):
        cursor = 0
        for match in marker.finditer(segment):
            if match.start() > cursor:
                run = paragraph.add_run(segment[cursor:match.start()])
                set_run_fonts(run, size, bold=segment_bold, cjk=cjk)
            paragraph._p.append(_pandoc_inline_math_element(match.group(1)))
            cursor = match.end()
        if cursor < len(segment):
            run = paragraph.add_run(segment[cursor:])
            set_run_fonts(run, size, bold=segment_bold, cjk=cjk)
'''
        if old_runs not in b:
            raise RuntimeError('cannot locate _add_runs')
        b = b.replace(old_runs, new_runs)
    BUILDER.write_text(b, encoding='utf-8')


def patch_figures() -> None:
    f = FIGS.read_text(encoding='utf-8')
    replacements = [
        ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'),
        ('"font.sans-serif": ["Noto Sans CJK JP", "Noto Sans CJK SC", "SimHei"],', '"font.family": "serif",\n            "font.serif": ["Noto Serif CJK SC", "Noto Serif CJK JP", "SimSun"],'),
        ('"font.size": 11,', '"font.size": 12,'),
        ('"axes.titlesize": 13,', '"axes.titlesize": 13.5,'),
        ('"axes.labelsize": 11,', '"axes.labelsize": 12,'),
        ('"legend.fontsize": 10,', '"legend.fontsize": 11,'),
        ('"figure.dpi": 140,', '"figure.dpi": 180,'),
        ('"savefig.dpi": 300,', '"savefig.dpi": 360,'),
        ('bbox_inches="tight", facecolor="white")', 'bbox_inches="tight", pad_inches=0.10, facecolor="white")'),
        ('判断是否需要专项 Rcap 扫描', '判断是否需要专项规划控制值扫描'),
        ('Rcap 扫描、局部细化与敏感性分析', '规划控制值扫描、局部细化与敏感性分析'),
        ('形成数值型Rcap建议片区核心指标实际值', '形成数值型弹性容载比建议片区核心指标'),
        ('r"弹性容载比控制值 $R_{\\mathrm{cap}}$"', '"弹性容载比规划控制值"'),
        ('fig, axes = plt.subplots(2, 2, figsize=(8.0, 7.0), constrained_layout=True)', 'fig, axes = plt.subplots(2, 2, figsize=(8.6, 7.6), constrained_layout=True)'),
        ('fig, axes = plt.subplots(2, 1, figsize=(7.5, 6.3), sharex=True, constrained_layout=True)', 'fig, axes = plt.subplots(2, 1, figsize=(8.2, 6.8), sharex=True, constrained_layout=True)'),
        ('fig, axes = plt.subplots(2, 2, figsize=(8.0, 6.4), sharex=True, constrained_layout=True)', 'fig, axes = plt.subplots(2, 2, figsize=(8.6, 7.0), sharex=True, constrained_layout=True)'),
        ('fontsize=8)', 'fontsize=10)'),
    ]
    for old, new in replacements:
        f = f.replace(old, new)
    FIGS.write_text(f, encoding='utf-8')

    t = TIEFIG.read_text(encoding='utf-8')
    trepl = [
        ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'),
        ('"font.sans-serif": ["Noto Sans CJK JP", "Noto Sans CJK SC", "SimHei"],', '"font.family": "serif",\n            "font.serif": ["Noto Serif CJK SC", "Noto Serif CJK JP", "SimSun"],'),
        ('"font.size": 10.5,', '"font.size": 11.5,'),
        ('"figure.dpi": 140,', '"figure.dpi": 180,'),
        ('"savefig.dpi": 300,', '"savefig.dpi": 360,'),
        ('fig, ax = plt.subplots(figsize=(10.8, 5.8))', 'fig, ax = plt.subplots(figsize=(11.8, 6.4))'),
        ('"墩南线\\nPZXL-00092"', '"墩南线"'),
        ('"河炮线\\nPZXL-00161"', '"河炮线"'),
        ('"高光伏供电单元\\nPV出力 > 本地负荷\\n形成净外送 G"', '"高光伏供电单元\\n光伏出力高于本地负荷\\n形成净外送功率"'),
        ('"TIE-002\\n既有联络"', '"墩南—河炮\\n既有联络"'),
        ('"两级规划：优先利用既有TIE-002；若 G > 既有联络可转移能力，\\n再计算新增联络所需最小有效容量并筛选河东/河镇等候选受端馈线"', '"两级规划：优先利用墩南—河炮既有联络；既有能力不足时，\\n再计算新增联络所需最小有效容量，并筛选河东、河镇等候选受端馈线"'),
        ('"TIE-002高光伏跨站供电边界重构示意"', '"高光伏跨站供电边界重构示意"'),
        ('bbox_inches="tight", facecolor="white")', 'bbox_inches="tight", pad_inches=0.10, facecolor="white")'),
    ]
    for old, new in trepl:
        t = t.replace(old, new)
    TIEFIG.write_text(t, encoding='utf-8')


def patch_qa() -> None:
    q = QA.read_text(encoding='utf-8')
    q = q.replace('"Rcap只约束规划期新增",', '"弹性容载比规划控制值只约束规划期新增",')
    q = q.replace('"本报告不虚构具体AHP权重值",', '"本报告不虚构具体层次分析法权重值",')
    QA.write_text(q, encoding='utf-8')


def main() -> None:
    patch_report()
    patch_builder()
    patch_figures()
    patch_qa()
    text = REPORT.read_text(encoding='utf-8')
    if re.search(r'\bRcap\b', text, flags=re.I):
        raise RuntimeError('Rcap remains in report')
    if '墩南线PZXL-00092' in text or '河炮线PZXL-00161' in text:
        raise RuntimeError('duplicate feeder code remains')
    if '[[MATH:' not in text:
        raise RuntimeError('inline math markers missing')
    print('final report Chinese terminology/layout patch completed')


if __name__ == '__main__':
    main()
