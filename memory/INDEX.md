# 徐州 110 kV 项目记忆索引

更新时间：2026-08-27（Asia/Shanghai）
当前状态：本次 Git 接管任务 `VERIFYING`；项目总体按最新 Claude 接续记录维持 v3 完成门槛，遗留负责人版式终审。进度冲突时以根目录 `claude_session_1.txt` 为准。
工作目录：`/home/xh/postgraduate/干活/徐州电科院项目咨询/徐州地区分布式新能源高渗透率地区110kV电网容载比弹性指标优化研究`

## 新会话必读（顺序固定）

1. [最新 Claude 接续记录](../claude_session_1.txt)（负责人确认的最新进度依据）
2. [项目代理约束](../AGENTS.md)（当前 v3.4 硬约束）
3. [当前状态快照](current.md)，以最新 Claude 记录修正旧状态
4. [下窗口提示词](../NEXT-SESSION-PROMPT.md) 与 [差异说明](next-session-prompt.md)
5. `skills/xuzhou-real-model/SKILL.md`
6. 其余按 AGENTS.md 第 1 节顺序读取

## 按任务读取

- [建模思路与真实方法总结（甲方汇报辅助＋自查标准）](../实验/研究/分析/2026-08-26-建模思路与真实方法总结_甲方汇报辅助.md) — 汇报前必读；含建模自查 10 问与报告章节映射
- [10 kV 联络案例重分析（收资定稿口径）](../实验/研究/分析/2026-08-26-10kV联络案例重分析_收资定稿口径.md) — 联络案例汇报/答疑前必读；能力区间、碎片化边界、代理稳健性
- [v3 建模进度与当前结果（报告急用版）](../研究报告/建模进度/2026-08-14_v3建模进度与当前结果_报告急用版.md) — 最新建模结论汇总
- [数据问题与甲方解释汇总](../实验/研究/分析/v3真实数据问题补充说明_供甲方汇报.md)
- 课题背景笔记：[FG-NSGA-II 收敛结果](fg-nsga2-convergence.md)、[项目状态](project-state.md)、[实验模型设计](experiment-model-design.md)、[论文写作方案](paper-writing-plan.md)（均为 2026-07 论文轨记录，与 v3 业务定义冲突时以 AGENTS.md 为准）

## 记忆写入入口

- 当前状态只更新 [`current.md`](current.md)。
- 已确认的长期决策写入 `decisions/`，并同步 AGENTS.md、`model_contract.yaml` 或 Skill。
- 过程记录追加写入 `sessions/YYYY-MM-DD/HHMM-主题.md`，不覆盖旧文件。
- 每次任务状态改变和会话结束前必须自动更新，不要只在聊天窗口保留交接信息。

## 当前阶段指针

Git 基线建立与公开范围核验 → 后续以 `实验/研究/` 的建模证据支撑研究报告撰写；具体已完成项和下一步以 `claude_session_1.txt`、随后刷新的 `current.md` 为准。旧结果不得冒充 v3 正式结果。

## 历史导出

项目级 Claude 接续记录为根目录 `claude_session_1.txt`；`codex-export/` 是机器级原始会话导出，可能含其他项目或本地配置，公开 Git 版本默认排除。
