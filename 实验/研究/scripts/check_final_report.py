#!/usr/bin/env python3
"""现行七章报告检查入口；Markdown为正文来源，成品检查按需执行。"""
from __future__ import annotations
import argparse,importlib.util,json,re,subprocess
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

EXPECTED_CHAPTER_TITLES=['第一章 研究背景与意义','第二章 国内外研究现状','第三章 研究对象与数据基础','第四章 弹性容载比优化模型','第五章 优化结果分析','第六章 典型区域案例分析','第七章 工程应用建议与总结']

def run_check(root: Path, markdown: Path, docx: Path | None, pdf: Path | None, output_dir: Path) -> dict:
    files=sorted(markdown.glob('[0-9][0-9] *.md')) if markdown.is_dir() else [markdown]
    source='\n\n'.join(p.read_text(encoding='utf-8-sig') for p in files)
    titles=re.findall(r'^# (第[一二三四五六七]+章[^\n]*)$',source,re.M)
    issues=[]
    if titles!=EXPECTED_CHAPTER_TITLES:issues.append('章节结构与当前七章底稿不符')
    spec=importlib.util.spec_from_file_location('writing_quality',Path(__file__).with_name('check_report_writing_quality.py'))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    writing=mod.run_check(markdown,root/'研究报告/终稿/写作与科学表达硬约束.md',None)
    issues.extend(writing['issues'])
    if markdown.resolve()==(root/'研究报告/03_MD').resolve():
        proc=subprocess.run(['python',str(root/'研究报告/03_MD/检查证据/核验阶段2.py')],cwd=root,capture_output=True,text=True)
        if proc.returncode:issues.append('阶段2数据核验失败：'+proc.stdout[-3000:]+proc.stderr[-1000:])
    math_count=None
    if docx is not None:
        with ZipFile(docx) as z:xml=ET.fromstring(z.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
        text=''.join(x.text or '' for x in xml.findall('.//w:t',ns))
        if any(t not in text for t in titles):issues.append('Word缺少当前章节标题')
        if re.search(r'\\(?:frac|mathrm|tag|Delta)|\\\[',text):issues.append('Word含未渲染公式源码')
        math_count=len(xml.findall('.//m:oMath',ns))
        if math_count<29:issues.append('Word原生公式数量少于正文29组公式')
    pages=None
    if pdf is not None:
        info=subprocess.run(['pdfinfo',str(pdf)],check=True,capture_output=True,text=True).stdout
        pages=int(re.search(r'Pages:\s*(\d+)',info)[1])
        text=subprocess.run(['pdftotext',str(pdf),'-'],check=True,capture_output=True,text=True).stdout
        compact=re.sub(r'\s+','',text)
        if any(re.sub(r'\s+','',t) not in compact for t in titles):issues.append('PDF缺少当前章节标题')
        if re.search(r'\\(?:frac|mathrm|tag|Delta)',text):issues.append('PDF含未渲染公式源码')
    result={'passed':not issues,'issues':issues,'chapter_count':len(titles),'native_math_count':math_count,'pdf_pages':pages,'scope':'当前模型Markdown内容检查；Word/PDF仅在传入时检查，版式仍需逐页复核'}
    output_dir.mkdir(parents=True,exist_ok=True)
    (output_dir/'自动检查结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--markdown',type=Path,required=True);p.add_argument('--docx',type=Path);p.add_argument('--pdf',type=Path);p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args();result=run_check(a.root.resolve(),a.markdown.resolve(),a.docx,a.pdf,a.output_dir.resolve());print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
