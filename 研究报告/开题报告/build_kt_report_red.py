#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""以“红色文字”标记修订：逐字 diff 原文与新文——不变的字保持黑色原格式，
新增/改写的字标红，删除的字标红加删除线。任何阅读器（Word/WPS/LibreOffice）
一致显示，不依赖“修订/审阅”开关。修改内容复用 build_kt_report.py 单一事实源。
用法: python3 build_kt_report_red.py [base.docx] [out.docx]
默认 base = LibreOffice 转换稿；正式保真请传甲方 Word 另存的 .docx。
"""
import os, sys, copy, difflib
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import build_kt_report as R  # MODS, INSERT_AFTER, ROOT

RED = "FF0000"

def ptext(p):
    return "".join(t.text or "" for t in p.iter(qn('w:t')))

def find(paras, sub):
    for p in paras:
        if sub in ptext(p):
            return p
    return None

def mk_run(text, rpr_tmpl, color=None, strike=False):
    r = OxmlElement('w:r')
    rpr = copy.deepcopy(rpr_tmpl) if rpr_tmpl is not None else OxmlElement('w:rPr')
    for tag in ('w:color', 'w:strike'):
        e = rpr.find(qn(tag))
        if e is not None:
            rpr.remove(e)
    if color:
        c = OxmlElement('w:color'); c.set(qn('w:val'), color); rpr.append(c)
    if strike:
        rpr.append(OxmlElement('w:strike'))
    r.append(rpr)
    t = OxmlElement('w:t'); t.set(qn('xml:space'), 'preserve'); t.text = text
    r.append(t)
    return r

def redline(p, old, new):
    """清空 p 的 run，按字级 diff 重建：equal→黑；insert→红；delete→红删除线；replace→红删除线旧+红新。"""
    runs = p.findall(qn('w:r'))
    rpr_tmpl = runs[0].find(qn('w:rPr')) if runs else None
    for r in runs:
        p.remove(r)
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            p.append(mk_run(old[i1:i2], rpr_tmpl))
        elif tag == 'insert':
            p.append(mk_run(new[j1:j2], rpr_tmpl, color=RED))
        elif tag == 'delete':
            p.append(mk_run(old[i1:i2], rpr_tmpl, color=RED, strike=True))
        elif tag == 'replace':
            p.append(mk_run(old[i1:i2], rpr_tmpl, color=RED, strike=True))
            p.append(mk_run(new[j1:j2], rpr_tmpl, color=RED))

def insert_red_after(after_p, text, template_p):
    new = OxmlElement('w:p')
    tpPr = template_p.find(qn('w:pPr'))
    if tpPr is not None:
        new.append(copy.deepcopy(tpPr))
    runs = template_p.findall(qn('w:r'))
    rpr_tmpl = runs[0].find(qn('w:rPr')) if runs else None
    new.append(mk_run(text, rpr_tmpl, color=RED))
    after_p.addnext(new)
    return new

def main():
    base = sys.argv[1] if len(sys.argv) > 1 else (
        "/tmp/claude-1000/-home-roscy-ws-HengXU-----------------110kV-------------/"
        "82c317ed-50d5-443f-8486-14080e420a5e/scratchpad/kt_edit/"
        "国网徐州公司徐州地区分布式新能源高渗透率地区110kV电网容载比弹性指标优化研究-开题报告0601.docx")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        R.ROOT, "研究报告/开题报告/"
        "国网徐州公司徐州地区分布式新能源高渗透率地区110kV电网容载比弹性指标优化研究-开题报告(定稿-红色修订).docx")
    d = Document(base)
    body = d.element.body
    paras = list(body.iter(qn('w:p')))
    miss = []
    # 先定位(在原始文档上)，再统一改写，避免改后文本互相干扰
    jobs = []
    for anchor, new in R.MODS:
        p = find(paras, anchor)
        if p is None:
            miss.append(anchor); continue
        jobs.append((p, ptext(p), new))
    insert_target = find(paras, R.MODS[1][0])           # 研究目的第二段
    tmpl = find(paras, "本项目需收集的数据")             # 干净正文段作格式模板
    for p, old, new in jobs:
        redline(p, old, new)
    if insert_target is None or tmpl is None:
        miss.append("[INSERT]")
    else:
        insert_red_after(insert_target, R.INSERT_AFTER[1], tmpl)
    d.core_properties.author = "XH"
    d.core_properties.last_modified_by = "XH"
    d.save(out)
    print("saved:", out)
    print("missing:", miss if miss else "none")

if __name__ == "__main__":
    main()
