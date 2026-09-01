# 项目仓库依赖与接续地图

更新时间：2026-08-27

本文件说明项目根目录为什么作为 Git 仓库根、`实验/研究/` 如何连接到研究报告，以及后续 Agent 的接手顺序。它不替代 `AGENTS.md`、`model_contract.yaml` 或真实数据模型规格。

## 1. 权威层次

| 层级 | 文件或目录 | 作用 |
|---|---|---|
| 进度接管 | `claude_session_1.txt` | 负责人确认的最新 Claude 接续记录；在进度、完成状态、遗留项和下一步方面优先于旧 memory |
| 项目硬约束 | `AGENTS.md` | 环境、模型红线、报告文风、记忆和公开输出边界；当前 v3.4 |
| 记忆承接 | `memory/INDEX.md`、`memory/current.md`、`memory/sessions/`、主题 memory | 长期决策、过程记录和当前快照；读取 Claude 记录后刷新 |
| 机器契约 | `实验/研究/model_contract.yaml` | v3.2.0 模型参数、路径、指标、成本、输出和硬断言 |
| 执行方案 | `实验/研究/docs/IMPLEMENTATION-PLAN-REAL-2021-2025-V3.md` | v3 阶段方案和验收方法；其中早期状态段可能是历史记录 |
| 建模规格 | `实验/研究/docs/REAL-DATA-MODEL-SPEC.md` | 真实数据接入、指标、约束、优化和发布口径 |
| 执行 Skill | `skills/xuzhou-real-model/` | 建模 Agent 的执行规则及 `agents/openai.yaml` |
| 报告 Skill | `skills/xuzhou-report-writing/` | 章节证据矩阵、事实审、文风审、Word/PDF 闭环 |

当文件描述的是进度时，优先顺序为 `claude_session_1.txt` → 当前刷新后的 `memory`；当文件描述模型和物理口径时，仍按 `AGENTS.md` → `model_contract.yaml` → v3 计划 → 模型规格执行。

## 2. 从数据到报告的依赖关系

### 2.1 输入与标准化

| 输入 | 主要消费者 | 产物或用途 |
|---|---|---|
| `实验/研究/data/tuomin/电网建模数据_Agent整合版_V1.2/` | `src/io_loader.py`、映射与审计脚本 | 站、主变、线路、光伏、成本和时序源数据；源目录只读 |
| `实验/研究/data/tuomin/10kv_case/` | `src/tie_case/`、`scripts/run_tie_case.py` | TIE 局部案例的结构化输入、质量门禁和证据 |
| `实验/研究/data/processed/real_2021_2025/` | `src/real_data_adapter.py`、`src/v32_actual_pipeline.py` | 标准化主表、跨年映射、年度资产白名单、光伏曲线、小时序列和数据文件清单 |
| `参考政策/储能成本依据/`、外部成本依据 | `src/real_costs.py`、成本审查 | 储能和扩容成本参数及适用说明 |

### 2.2 计算、校核与结果

| 层级 | 关键文件 | 责任 |
|---|---|---|
| 物理指标 | `src/real_metrics.py`、`src/v3_time_physics.py`、`src/clr.py` | 路径自身正向峰值、正式容载比、反向峰值、缺口和储能方向红线 |
| 候选与成本 | `src/real_costs.py`、`src/v3_planner.py`、`src/milp_planner.py` | 可追溯离散扩容、减容、替换、储能候选和累计在役 EAC |
| 110/35 kV 分层 | `src/real_matrices.py`、`src/v3_voltage_cases.py` | 两电压等级独立聚合、求解和矩阵输出 |
| 10 kV 局部案例 | `src/tie_case/engine.py`、`scripts/run_tie_case.py` | 现有联络切分、新建线路独立解析；不做全县联络优化 |
| 质量与网络筛查 | `src/real_network_check.py`、`src/verify_flow_n1.py`、`src/verify_dlt2041.py` | 容量网络压力筛查、设备/县区缺口和边界说明；缺阻抗时不宣称精确潮流 |
| 测试 | `tests/` | 契约、数据、指标、规划、案例、输出和报告构建回归 |
| 运行入口 | `scripts/run_all.py`；`scripts/run_annual_model.py --legacy-archive-only` | 前者是 v3.2 真实端到端入口；后者仅复现 v2 历史年度归档，默认拒绝执行 |
| 正式结果 | `results/runs/real-2021-2025-v32-frozen/` | 数据文件清单、方案年度结果、措施、成本、弹性前沿、矩阵、问题台账和附表 |

### 2.3 结果到报告

研究报告只从已审查的 CSV/Markdown 和技术附表取数；Word/PDF 是人工审查层。推荐工作顺序为：

```text
正式运行 manifest
  → path_year_results / path_action_results / path_cost_breakdown
  → elasticity_frontier 与两套推荐矩阵
  → 分析目录中的方法总结、数据问题和案例边界
  → 研究报告章节证据与审查清单
  → Word 生成 → PDF 渲染闭环 → 负责人版式终审
```

报告正文必须遵守项目统一编码，不把站名、线路名和区县名写入面向甲方的正文、表格、图题或图内文字。技术底稿和源数据按 `AGENTS.md` 的边界管理。

## 3. 接手操作

1. 读取 `claude_session_1.txt`，确认最新进度和未完成项。
2. 读取 `AGENTS.md`、`memory/INDEX.md`、`memory/current.md`，将旧快照与最新 Claude 记录对齐。
3. 涉及 `实验/研究/` 时按 `AGENTS.md` 第 1 节依次读取 v3 计划、契约、数据规格、建模 Skill 和数据说明书；涉及报告时再加载报告 Skill。
4. 只在 `实验/研究/` 目录使用 `xuzhou110kv_clr` 环境执行测试和模型入口。
5. 以 `results/runs/real-2021-2025-v32-frozen/` 下的数据文件清单、CSV/Markdown 和问题台账作为精确查值入口。
6. 每次状态改变都刷新 `memory/current.md`，并在 `memory/sessions/YYYY-MM-DD/` 新增记录。

## 4. Git 追踪边界

按负责人确认，本仓库纳入研究代码、测试、脱敏源数据、处理数据、正式及历史结果、报告材料、参考材料、约束、项目 Skill、agents、项目级 memory 和 `claude_session_1.txt`。

明确排除：

- `Tushare.ma`、密钥/环境文件：本地凭据；
- `.claude/settings.local.json`、锁文件、`.cc-writes`、`__pycache__`、`.pytest_cache`、日志和 `paper/.gstack`：机器或运行时状态；
- `memory/codex-export/`：机器级会话导出，含无关项目和本地配置，不等同于项目 memory；
- `参考文献/前沿调研.tar.gz`：171,513,560 bytes，超过普通 Git 单文件限制，且其内容由已解包的 `参考文献/前沿调研/` 保留。

上述规则写入根目录 `.gitignore`。任何后续新增凭据或机器配置，先加入排除规则，再进行 `git add`。
