# 下窗口提示词差异说明

根目录 [`claude_session_1.txt`](../claude_session_1.txt) 是负责人确认的最新 Claude 接续记录，在进度、完成状态、遗留项和下一步方面优先于本文件、[`current.md`](current.md) 和根目录 [`NEXT-SESSION-PROMPT.md`](../NEXT-SESSION-PROMPT.md)。后续 Agent 必须先读该记录，再用当前 memory 承接并刷新状态。

## 相对模板已变化的部分

| 模板表述 | 实际状态（2026-08-24） |
|---|---|
| v3 契约测试 5 failed / 1 passed 红灯起步 | 阶段 0 已迁移完成；不限制路径端到端已跑通并出结果 |
| 无可交付的 v3 结果 | 已有不限制路径建模结果、QX-00005 附表、甲方解释文档、报告前三章初稿 Word |
| 未提及记忆体系 | 新增 `memory/`（AGENTS.md §12）；接手时先读 `claude_session_1.txt`，再读 `memory/INDEX.md` 与 `memory/current.md` |

## 推荐的第一条消息

```text
请接手本地项目：
/home/xh/postgraduate/干活/徐州电科院项目咨询/徐州地区分布式新能源高渗透率地区110kV电网容载比弹性指标优化研究

先读取根目录 `claude_session_1.txt`；它是负责人确认的最新进度依据。再读取 AGENTS.md（含第 12 节记忆规则）、memory/INDEX.md、memory/current.md，随后按 AGENTS.md 第 1 节顺序读取必读文件和 skills/xuzhou-real-model/SKILL.md。

当前状态与下一步以 `claude_session_1.txt` 的最新内容为准；本次 Git 接管完成后，继续围绕 `实验/研究/` 建模结果撰写全面、详实、科学严谨的弹性容载比规划研究报告。每次状态改变和会话结束前按 AGENTS.md 第 12 节更新 `memory/current.md` 并在 `memory/sessions/YYYY-MM-DD/` 追加记录。
```
