# 110/35 kV 容载比弹性指标优化研究项目

本仓库保存项目从建模约束、数据血缘、真实数据计算、结果审查到研究报告撰写的完整工作链。核心研究目录为 [`实验/研究/`](实验/研究/)，后续报告工作以该目录的建模结果和 CSV/Markdown 证据为准。

## 接手顺序与状态依据

当前接手时必须先读根目录 [`claude_session_1.txt`](claude_session_1.txt)。负责人已确认：该文件是最新的 Claude 中断接续记录，在项目进度、完成状态、遗留事项和下一步方面优先于较旧的 `memory/INDEX.md`、`memory/current.md` 和根目录提示词。模型、物理、数据和报告口径仍以 [`AGENTS.md`](AGENTS.md)、[`实验/研究/model_contract.yaml`](实验/研究/model_contract.yaml) 及同步后的负责人决策为准。

随后读取：

1. [`memory/INDEX.md`](memory/INDEX.md) 和 [`memory/current.md`](memory/current.md)；
2. [`实验/研究/docs/IMPLEMENTATION-PLAN-REAL-2021-2025-V3.md`](实验/研究/docs/IMPLEMENTATION-PLAN-REAL-2021-2025-V3.md)；
3. [`实验/研究/docs/REAL-DATA-MODEL-SPEC.md`](实验/研究/docs/REAL-DATA-MODEL-SPEC.md)；
4. [`skills/xuzhou-real-model/SKILL.md`](skills/xuzhou-real-model/SKILL.md) 及其 [`agents/openai.yaml`](skills/xuzhou-real-model/agents/openai.yaml)；
5. [`skills/xuzhou-report-writing/SKILL.md`](skills/xuzhou-report-writing/SKILL.md)（涉及报告撰写时）。

最新接续记录登记：v3.2 建模主体、10 kV 联络案例重分析、七章研究报告活动稿、Word/PDF 渲染闭环和全量回归已完成；负责人仍需进行 Word/WPS 目录页码和版式终审。该状态以 `claude_session_1.txt` 为最新进度依据，不能只根据旧版计划文件的历史状态判断。

## 项目依赖主链

```text
负责人接续记录 + 项目 memory
             │（进度与历史决策）
             ▼
AGENTS.md / model_contract.yaml / 真实数据规格 / 项目 Skill
             │（硬约束、机器契约、执行规则）
             ▼
实验/研究/data/tuomin/       ──只读源数据──▶
实验/研究/data/processed/real_2021_2025/
             │（映射、质量标记、输入哈希）
             ▼
实验/研究/src/ + scripts/ + tests/
             │（指标、物理约束、候选、优化、局部案例、校核）
             ▼
实验/研究/results/runs/real-2021-2025-v32-frozen/
             │（路径结果、成本、前沿、矩阵、问题台账、manifest）
             ▼
实验/研究/分析/ + 研究报告/初稿/ + tools/
             │（解释、自查、章节、Word/PDF）
             ▼
全面、详实、科学严谨的弹性容载比规划研究报告
```

## 研究运行环境

所有相对命令在 `实验/研究/` 目录执行，并使用 Conda 环境 `xuzhou110kv_clr`：

```bash
cd 实验/研究
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr python scripts/run_all.py --dataset real_2021_2025 --config model_contract.yaml --skip-gen
```

正式研究只使用 v3.2 三个方案代码：`PATH_ACTUAL_2021_2025`、`PATH_OPT_CLR_UNBOUNDED` 和 `PATH_OPT_CLR_LE_2`。两条优化方案均从 2021 年实际在役资产起步；旧 `real_2025`、旧年度矩阵和 `SCHEME_C0/A/B` 只能用于归档或迁移回归。

## 关键证据入口

- 建模方法与自查：[实验/研究/分析/2026-08-26-建模思路与真实方法总结_甲方汇报辅助.md](实验/研究/分析/2026-08-26-建模思路与真实方法总结_甲方汇报辅助.md)
- 10 kV 局部案例边界：[实验/研究/分析/2026-08-26-10kV联络案例重分析_收资定稿口径.md](实验/研究/分析/2026-08-26-10kV联络案例重分析_收资定稿口径.md)
- v3.2 冻结结果：[实验/研究/results/runs/real-2021-2025-v32-frozen/](实验/研究/results/runs/real-2021-2025-v32-frozen/)
- 报告章节和审查材料：[研究报告/初稿/](研究报告/初稿/)
- 报告撰写工作流：[skills/xuzhou-report-writing/SKILL.md](skills/xuzhou-report-writing/SKILL.md)

## 公开仓库排除项

以下内容不上传：根目录 `Tushare.ma` 等本地凭据、机器本地配置和锁文件、缓存/编译产物、可能混入其他项目或本地配置的 `memory/codex-export/`，以及超过 GitHub 普通 Git 单文件限制且与解包目录重复的 `参考文献/前沿调研.tar.gz`。排除项及原因统一记录在 [`.gitignore`](.gitignore) 和 [`docs/PROJECT-REPOSITORY-MAP.md`](docs/PROJECT-REPOSITORY-MAP.md) 中。

其余项目材料按负责人确认纳入版本基线。源数据目录仍遵守只读约束，任何清洗和派生结果必须进入 `data/processed/real_2021_2025/` 并保留来源、转换、质量标记和输入哈希。
