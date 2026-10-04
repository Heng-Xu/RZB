# 当前报告维护流程

正式成果只有 `研究报告/04_word/研究报告终稿.docx`。当前 Word 是用户认可的102页版本，归档时不修改其内容。内部 PDF、计算工作簿及核验记录用于继续维护，不另设交付包。

## 文件入口

| 用途 | 路径 |
| --- | --- |
| 六章正文源 | `研究报告/03_MD/当前版/01` 至 `06` 开头的Markdown文件 |
| 表格、生成段落与图件 | `研究报告/02图表/当前版` |
| 原始精度计算结果及两份工作簿 | `研究报告/01研究推荐/当前版` |
| 数据来源、原始文件哈希与工程依据 | `研究报告/数据来源/当前版` |
| 构建、复核与数学排版脚本 | `研究报告/05_review/当前版` |
| 当前模型及八份测试文件 | `实验/研究/rebuild_2026` |
| 原始收资及10 kV案例 | `实验/研究/data/tuomin` |
| 标准与论文原文 | `参考政策`、`参考文献` |
| 最新甲方批注 | `研究报告/甲方反馈/10.03 最新稿件的意见反馈` |

## 核验及重建

使用 Conda 环境 `xuzhou110kv_clr`。本机可直接调用 `/home/xh/anaconda3/envs/xuzhou110kv_clr/bin/python`；新环境安装 `tools/requirements-current.txt`。构建还需要 Pandoc、Node.js、LibreOffice 和指定字体，进入 `研究报告/05_review/当前版` 后执行 `npm install` 安装 MathJax。可通过环境变量 `XUZHOU_LIBREOFFICE` 指定本地 soffice 路径。

```bash
# 对现有成果作完整核验，不覆盖 Word
python tools/build_current_report.py --check-only

# 修改六章源后，重建 Word 和内部 PDF，并核对实际目录页码
python tools/build_current_report.py --rebuild

# 仅为现有 Word 刷新内部排版 PDF
python tools/build_current_report.py --pdf-only

# 维护模型代码时，执行当前相关测试
python -m pytest -q 实验/研究/rebuild_2026/tests
```

重建依次装配六章源、生成原生OMML Word、制作数学排版副本、导出内部PDF、刷新目录缓存并再次导出，最后校核模型、12600组外推和文档一致性。核验结果写入 `05_review/当前版/最终核验.json`，正式 Word 始终保留原生可编辑公式。

当前数据保留原精度。不要将正文、图件或工作簿的两位小数显示值回填求解。重新寻优使用 `05_review/当前版/统一起点情景.py --output <独立目录>`，通用外推使用 `通用参数外推.py`；这两项会实际求解，普通文字修改无需重算。图件刷新脚本支持独立输出目录，替换前检查字体、数值及正文图名。

改稿后核对各章连续性、引文对应、公式解释和表格居中，再更新当前状态并提交 Git。历史恢复应在单独目录或 worktree 进行，不覆盖正在维护的基线。
