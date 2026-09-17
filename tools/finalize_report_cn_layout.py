#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性收敛中文研究报告的术语、行内公式和Word公式版式。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "研究报告/终稿/国网徐州公司徐州地区分布式新能源高渗透率地区110kV电网容载比弹性指标优化研究-研究报告终稿.md"
BUILDER = ROOT / "tools/build_report_docx.py"
WORKFLOW = ROOT / ".github/workflows/report-final-build.yml"


def replace(text: str, old: str, new: str) -> str:
    if old in text:
        return text.replace(old, new)
    return text


# ---------- 1. 报告正文：中文术语 + 公式变量行内格式 ----------
text = REPORT.read_text(encoding="utf-8-sig")
text = text.replace("Rcap", "弹性容载比规划控制值")
text = text.replace("Spearman秩相关", "斯皮尔曼秩相关")
text = text.replace("AHP更适合作为", "层次分析法更适合作为")
text = text.replace("连续SOC", "连续荷电状态")
text = text.replace("GIS坐标", "地理信息系统坐标")
text = text.replace("当前PV锚点", "当前光伏锚点")
text = text.replace("1.2倍PV", "1.2倍光伏")
text = text.replace("1.5倍PV", "1.5倍光伏")
text = text.replace(
    r"P_{\mathrm{TIE002,tr}}^{\max}=\min",
    r"P_{\mathrm{tr}}^{\max}=\min",
)

text = replace(
    text,
    "（2-2）\n\n该定义保留了传统容载比",
    "（2-2）\n\n式中，[[MATH:P_{\\mathrm{actual},i,t}]] 为节点或变电站 [[MATH:i]] 在时刻 [[MATH:t]] 的基础净负荷；[[MATH:P_{\\mathrm{c},i,t}]]、[[MATH:P_{\\mathrm{d},i,t}]] 分别为储能充电和放电功率；[[MATH:P_{\\mathrm{tie},i,t}]] 为局部网络互济引起的净功率调整量，符号按统一功率方向约定取值。\n\n该定义保留了传统容载比",
)
text = replace(
    text,
    "（2-3）\n\n当既有容量已经高于控制值对应的容量水平时",
    "（2-3）\n\n式中，[[MATH:\\Delta S_y]] 为第 [[MATH:y]] 年相对于2021年共同资产起点允许新增的变电容量；[[MATH:R_{\\mathrm{cap}}]] 为弹性容载比规划控制值；[[MATH:S_{2021}]] 为2021年实际在役变电容量。\n\n当既有容量已经高于控制值对应的容量水平时",
)
text = replace(
    text,
    "其中，[[MATH:E_t]] 为时刻 [[MATH:t]] 的储能电量，[[MATH:P_{c,t}]] 和 [[MATH:P_{d,t}]] 分别为充电功率和放电功率。",
    "其中，[[MATH:E_t]] 为时刻 [[MATH:t]] 的储能电量，[[MATH:P_{c,t}]] 和 [[MATH:P_{d,t}]] 分别为充电功率和放电功率，[[MATH:\\eta_c]] 和 [[MATH:\\eta_d]] 分别为充电效率和放电效率，[[MATH:\\Delta t]] 为时间步长，[[MATH:E_{\\mathrm{rated}}]] 为储能额定电量。",
)
text = replace(
    text,
    "（3-1）\n\n该指标反映新能源装机相对于片区正向峰值负荷的规模关系",
    "（3-1）\n\n式中，[[MATH:R_{\\mathrm{SL}}^{*}]] 为现状源荷规模比，[[MATH:C_{\\mathrm{RE,snap}}]] 为最新新能源装机快照，[[MATH:P_{\\mathrm{load,max,base}}^{+}]] 为最近完整年度正向最大供电负荷。\n\n该指标反映新能源装机相对于片区正向峰值负荷的规模关系",
)
text = replace(
    text,
    "（3-2）\n\n该指标突出片区内最受反向潮流影响的局部接入点",
    "（3-2）\n\n式中，[[MATH:R_{\\mathrm{rev}}]] 为局部最大反向潮流比例，[[MATH:P_{\\mathrm{rev,max},i}]] 为变电站 [[MATH:i]] 的年度最大反向潮流功率，[[MATH:P_{\\mathrm{load,max}}^{+}]] 为片区正向最大供电负荷。\n\n该指标突出片区内最受反向潮流影响的局部接入点",
)
text = replace(
    text,
    "（3-3）\n\n当K_line为负时",
    "（3-3）\n\n式中，[[MATH:K_{\\mathrm{line}}]] 为110 kV线路统计负载余度，[[MATH:\\lambda_l]] 为线路 [[MATH:l]] 的统计最大负载率。\n\n当[[MATH:K_{\\mathrm{line}}]]为负时",
)
text = replace(
    text,
    "（3-4）\n\n![图 3-1",
    "（3-4）\n\n式中，[[MATH:g_P]] 为2021—2025年正向峰值负荷年均变化率，[[MATH:P_{2021}^{+}]] 和 [[MATH:P_{2025}^{+}]] 分别为2021年、2025年正向最大供电负荷。\n\n![图 3-1",
)
text = replace(
    text,
    "（3-5）\n\n当净有功功率小于0时",
    "（3-5）\n\n式中，[[MATH:P_k]] 为供电单元 [[MATH:k]] 的净有功功率，[[MATH:P_{L,k}]] 为本地负荷功率，[[MATH:P_{PV,k}]] 为光伏出力。\n\n当净有功功率小于0时",
)
text = replace(
    text,
    "（3-6）\n\n定义二元供电归属变量",
    "（3-6）\n\n式中，[[MATH:G_k]] 为供电单元 [[MATH:k]] 可用于跨站转移的光伏富余功率。\n\n定义二元供电归属变量 [[MATH:x_k]]：取0表示仍由原110 kV变电站供电，取1表示通过供电边界重构调整至相邻变电站供电范围，则跨站转移功率为：",
)
text = text.replace(
    "定义二元供电归属变量：取0表示仍由原110 kV变电站供电，取1表示通过供电边界重构调整至相邻变电站供电范围，则跨站转移功率为：\n\n$$\nP_{\\mathrm{tr}}=\\sum_k x_kG_k\n$$\n（3-7）",
    "$$\nP_{\\mathrm{tr}}=\\sum_k x_kG_k\n$$\n（3-7）\n\n式中，[[MATH:P_{\\mathrm{tr}}]] 为跨站转移有功功率；[[MATH:x_k]] 为供电单元归属决策变量。",
)

text = replace(
    text,
    "对既有联络e，其可用于反向功率转移的能力同时受到送端路径、受端路径和受端变电站承接能力限制。设送端、受端路径规划有效容量分别为S_e,D^eff和S_e,R^eff，受端站剩余反向承接能力为H_R，则既有联络可转移有功功率满足：",
    "对既有联络 [[MATH:e]]，其可用于反向功率转移的能力同时受到送端路径、受端路径和受端变电站承接能力限制。设送端、受端路径规划有效容量分别为 [[MATH:S_{e,D}^{\\mathrm{eff}}]] 和 [[MATH:S_{e,R}^{\\mathrm{eff}}]]，受端站剩余反向承接能力为 [[MATH:H_R]]，则既有联络可转移有功功率满足：",
)
text = replace(
    text,
    "（5-2）\n\n其中规定正值为净负荷、负值为反向送电。",
    "（5-2）\n\n式中，[[MATH:P_D^0]]、[[MATH:P_R^0]] 分别为供电边界重构前送端站、受端站的净功率，[[MATH:P_{\\mathrm{tr}}]] 为跨站转移有功功率。本文规定正值为净负荷、负值为反向送电。",
)
text = replace(
    text,
    "（5-3）\n\n当仍存在正的剩余转移需求",
    "（5-3）\n\n式中，[[MATH:G]] 为待转移的净富余功率，[[MATH:G_{\\mathrm{res}}]] 为既有联络利用后的剩余转移需求。\n\n当仍存在正的剩余转移需求",
)
text = replace(
    text,
    "式（5-4）给出了由剩余有功转移需求反推新增联络容量的统一换算关系。当前案例取cosφtr≈1.0，因此所得MVA值可近似作为相应MW有功转移需求在80%控制条件下的有效容量下限。",
    "式（5-4）给出了由剩余有功转移需求反推新增联络容量的统一换算关系。其中，[[MATH:S_{\\mathrm{new}}^{\\min}]] 为新增联络最小规划有效容量。当前案例取 [[MATH:\\cos\\varphi_{\\mathrm{tr}}\\approx1.0]]，因此所得MVA值可近似作为相应MW有功转移需求在80%控制条件下的有效容量下限。",
)
text = text.replace("对n阶判断矩阵", "对[[MATH:n]]阶判断矩阵")
text = replace(
    text,
    "（5-5）\n\n当CR小于0.10时，通常认为判断矩阵的一致性可以接受。",
    "（5-5）\n\n式中，[[MATH:CI]] 为一致性指标，[[MATH:CR]] 为一致性比率，[[MATH:RI]] 为平均随机一致性指标，[[MATH:\\lambda_{\\max}]] 为判断矩阵最大特征根。通常当一致性比率 [[MATH:CR]] 小于0.10时，认为判断矩阵的一致性可以接受。",
)
text = replace(
    text,
    "（6-1）\n\n在最保守的“本地负荷为0”包络下",
    "（6-1）\n\n式中，[[MATH:P_{\\mathrm{tr}}^{\\max}]] 为既有联络在本研究规划控制条件下的最大可转移有功功率。\n\n在最保守的“本地负荷为0”包络下",
)
text = replace(
    text,
    "（6-2）\n\n对应河炮侧路径利用率约56.49%",
    "（6-2）\n\n式中，[[MATH:G]] 为该规划场景下墩南线需要跨站转移的净富余有功功率。\n\n对应河炮侧路径利用率约56.49%",
)

# 清理正文可见英文缩写；标准电气单位和公式符号不在此列。
text = text.replace("AHP", "层次分析法")
text = text.replace("SOC", "荷电状态")
REPORT.write_text(text, encoding="utf-8")


# ---------- 2. Word构建器：行内数学与显示公式留白 ----------
b = BUILDER.read_text(encoding="utf-8")
b = b.replace('fontsize=18, color="black",', 'fontsize=20, color="black",')
b = b.replace('bbox_inches="tight", pad_inches=0.025,', 'bbox_inches="tight", pad_inches=0.080,')
b = b.replace(
    '_set_at_least_line_spacing(paragraph, int(max(960, (height_pt + 22.0) * 20)))\n        paragraph.paragraph_format.space_before = Pt(4)\n        paragraph.paragraph_format.space_after = Pt(4)',
    '_set_at_least_line_spacing(paragraph, int(max(1320, (height_pt + 34.0) * 20)))\n        paragraph.paragraph_format.space_before = Pt(7)\n        paragraph.paragraph_format.space_after = Pt(7)',
)

old_fallback = '''    # 未预定义的简单标记以数学斜体文本兜底；禁止将LaTeX源码裸露到Word正文。\n    clean = (latex.replace('\\\\mathrm{', '').replace('}', '')\n                  .replace('\\\\varphi', 'φ').replace('\\\\beta', 'β')\n                  .replace('\\\\approx', '≈').replace('\\\\cos', 'cos '))\n    _add_math_run(paragraph, clean, size)\n'''
new_fallback = '''    # 常见“变量+上下标”采用可编辑文字级数学格式，供公式后的变量说明使用。\n    if latex == "\\\\Delta S_y":\n        _add_math_run(paragraph, "Δ", size)\n        _add_math_run(paragraph, "S", size)\n        _add_math_run(paragraph, "y", size, subscript=True)\n        return\n    simplified = re.sub(r"\\\\mathrm\\{([^{}]+)\\}", r"\\1", latex)\n    greek_map = {"\\\\lambda": "λ", "\\\\eta": "η"}\n    generic = re.fullmatch(\n        r"(\\\\lambda|\\\\eta|[A-Za-z]+)(?:_\\{([^{}]+)\\}|_([A-Za-z0-9,]+))?(?:\\^\\{([^{}]+)\\}|\\^([A-Za-z0-9+*'\\-]+))?",\n        simplified,\n    )\n    if generic:\n        base, sub_braced, sub_plain, sup_braced, sup_plain = generic.groups()\n        base_text = greek_map.get(base, base)\n        _add_math_run(paragraph, base_text, size)\n        sub = sub_braced or sub_plain\n        sup = sup_braced or sup_plain\n        if sub:\n            _add_math_run(paragraph, sub, size, italic=False, subscript=True)\n        if sup:\n            _add_math_run(paragraph, sup, size, italic=False, superscript=True)\n        return\n\n    # 最后兜底仅用于简单数学标记；禁止将LaTeX源码裸露到Word正文。\n    clean = (latex.replace('\\\\mathrm{', '').replace('}', '')\n                  .replace('\\\\varphi', 'φ').replace('\\\\beta', 'β')\n                  .replace('\\\\lambda', 'λ').replace('\\\\eta', 'η')\n                  .replace('\\\\approx', '≈').replace('\\\\cos', 'cos '))\n    _add_math_run(paragraph, clean, size)\n'''
if old_fallback in b:
    b = b.replace(old_fallback, new_fallback)
else:
    raise SystemExit("build_report_docx.py inline-math fallback block not found")
BUILDER.write_text(b, encoding="utf-8")


# ---------- 3. 构建工作流：禁止旧补丁重新引入英文缩写/内部联络码 ----------
w = WORKFLOW.read_text(encoding="utf-8")
w = w.replace("Rcap", "弹性容载比规划控制值")
w = w.replace("TIE-002通道上限", "墩南—河炮既有联络通道上限")
w = w.replace("**表 6-3 TIE-002高光伏跨站反向功率转移规划结果**", "**表 6-3 墩南—河炮既有联络高光伏跨站反向功率转移规划结果**")
WORKFLOW.write_text(w, encoding="utf-8")

print("final report Chinese terminology/layout patch applied")
