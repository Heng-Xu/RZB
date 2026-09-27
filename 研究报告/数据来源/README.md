# 数据来源说明及审查记录

报告配套说明使用 [数据来源说明.pdf](数据来源说明.pdf)，共六节，正文源文件为03_MD/数据来源说明.md，可编辑版本为同名Word文件。

详细核验使用 [当前报告数据来源与计算审查.pdf](当前报告数据来源与计算审查.pdf)，需要编辑说明时使用同名Word文件。脚本读取 [当前报告数据来源.json](当前报告数据来源.json)。两份说明均绑定当前报告Word和PDF的SHA256，并列出报告位置、来源文件、原始定位、单位、计算办法及适用限制。

当前索引涵盖17图、15表、29组公式、640条直接来源记录和24条区县指标复算。`data_source.json` 及此前已有的说明文件保留为历史完整字典；当前索引记录其哈希。正文数值候选相等只用于追溯，不能单独证明指标出处，需结合年度、工程范围和计算含义核对。

从项目根目录运行以下命令可重复检查当前交付文件；命令中的Python环境包含所需依赖：

```bash
/home/xh/anaconda3/envs/xuzhou110kv_clr/bin/python tools/check_current_report_artifacts.py
/home/xh/anaconda3/envs/xuzhou110kv_clr/bin/python 实验/研究/scripts/check_final_report.py --root . --markdown 研究报告/03_MD --docx 研究报告/04_word/研究报告终稿.docx --pdf 研究报告/04_word/研究报告终稿.pdf --output-dir 研究报告/05_review/闭环核验/最终正文核验
```

检查结果及修正说明位于 `研究报告/05_review/闭环核验`。成品检查会读取当前文件并写出核验JSON，不重算优化路径。

报告内容变动时，先按 `研究报告/AGENTS.md` 及[humanizer技能](/home/xh/.codex/skills/humanizer/SKILL.md)检查正文、表格文字和图内标签，再装配Word、转换PDF、更新来源说明，最后执行上述两项检查并人工查看分页。图件由 `tools/redraw_current_report_figures.py` 生成，报告由 `tools/build_current_report.py` 装配；PDF转换和字体嵌入分别由 `tools/export_current_report_pdf.py`、`tools/finalize_current_report.py` 完成。独立配套说明由 `tools/build_report_source_note.py` 生成。详细审查记录由 `tools/audit_current_report.py` 生成，随后通过 `tools/export_source_audit_pdf.py` 转换为PDF。

PDF转换脚本依赖本机LibreOffice UNO服务。程序扫描不能替代humanizer通读及人工版式审查。标准公式、原始数据、计算代码和引用路径必须保留其确切含义与可追溯写法。
