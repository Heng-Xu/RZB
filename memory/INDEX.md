# 徐州 110 kV 项目记忆索引

更新时间：2026-09-01 11:40（Asia/Shanghai）
当前阶段：`model-v3.2-autonomous-review` 分支 v3.2 自主复核已完成；`contract=3.2.0 frozen`。

## 新会话读取顺序

1. 先以 Git 建立实时事实：`fetch/status/branch/log`、远端 HEAD、GitHub Actions `head_sha`。
2. 读取 [`AGENTS.md`](../AGENTS.md)。
3. 读取 base contract、v3.2 overlay、`load_v32_contract()` resolved contract、processed manifest、审批表和 frozen 正式结果。
4. 读取 [`current.md`](current.md) 获取正在执行的遗留项、命令与验证证据。
5. 按任务读取项目 Skill、报告和技术底稿。

根目录 [`prompt.md`](../prompt.md) 与 [`NEXT-SESSION-PROMPT.md`](../NEXT-SESSION-PROMPT.md) 是短接续入口。`claude_session_1.txt`、`memory/archive/` 及 2026-09-01 前 session 均为 **HISTORICAL / SUPERSEDED**；可用于追溯决策过程，不能覆盖当前 Git、frozen v3.2 contract、正式输入和正式结果。

## 当前权威位置

- 当前状态与下一步：[`current.md`](current.md)
- 最近一次完整模型/冻结验证基准：提交 `fee3625c43d3f42b7514fbade69d7585813d38ec`，Actions run `33466902615` / `33466902676` 均成功；当前尖以 Git 实时查值为准。
- 长期业务约束：[`AGENTS.md`](../AGENTS.md)
- 模型契约：[`model_contract.yaml`](../实验/研究/model_contract.yaml) 与 [`model_contract_v3_2_overlay.yaml`](../实验/研究/model_contract_v3_2_overlay.yaml)
- 正式结果：`实验/研究/results/runs/real-2021-2025-v32-frozen/`
- 本轮计划：`实验/研究/docs/superpowers/plans/2026-09-01-v32-autonomous-review.md`
- 新记录：`sessions/YYYY-MM-DD/HHMM-主题.md`，只增不改

## 不再作为当前接续依据的材料

- [`claude_session_1.txt`](../claude_session_1.txt)：截至 2026-08-27 的中断会话导出，含已被 v3.2 取代的进度事实。
- [`sessions/2026-08-27/1519-Git基线推送与Claude优先级登记.md`](sessions/2026-08-27/1519-Git基线推送与Claude优先级登记.md)：历史 Git 建仓记录。
- [`sessions/2026-08-27/1552-ChatGPT接管复核与方案讨论基线.md`](sessions/2026-08-27/1552-ChatGPT接管复核与方案讨论基线.md)：v3.1 历史讨论基线。
- `archive/2026-09-01-*-pre-v32-review.md`：治理前的混合提示词原文。

这些文件保留原始内容，不删除历史证据；文件头的归档标识决定其读取角色。

## 记忆写入

- 状态变化、关键验证和会话结束时更新 `current.md`。
- 过程证据新增到 `sessions/`，不得覆盖旧 session。
- 已确认且影响后续实现的长期决策写入 `decisions/`，并同步到 `AGENTS.md`、contract 或项目 Skill。
- 大型产物只登记路径、大小、SHA-256、命令和退出码。
