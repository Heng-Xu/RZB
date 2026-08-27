# 负责人决策：Claude 接续记录优先于旧项目 memory

日期：2026-08-27

## 决策内容

根目录 `claude_session_1.txt` 是当前项目最新的 Claude 中断接续记录。就项目进度、已完成项、遗留项、阻塞状态和下一步安排而言，它优先于较早生成的 `memory/INDEX.md`、`memory/current.md` 和根目录 `NEXT-SESSION-PROMPT.md`。

## 执行规则

1. 新会话先读取 `claude_session_1.txt`，再读取 `AGENTS.md`、`memory/INDEX.md` 和 `memory/current.md`。
2. 如果上述进度记录冲突，以 `claude_session_1.txt` 为准，并将最新状态刷新到 `memory/current.md`，同时在 `memory/sessions/YYYY-MM-DD/` 追加过程记录。
3. 该优先级只处理接管状态，不改变已经冻结的模型、物理、数据和报告口径。模型定义或长期业务决策必须同步进入 `AGENTS.md`、`model_contract.yaml` 或对应 Skill 后才生效。
4. `memory/codex-export/` 是机器级导出，可能混入其他项目或本地配置，不作为项目历史优先级来源，也不应原样公开上传。

## 依据

- 负责人在 2026-08-27 会话中明确确认本决策。
- 最新接续记录：根目录 `claude_session_1.txt`。
- 约束落点：根目录 `AGENTS.md` §1、§12.1、§12.5；`memory/README.md`；`memory/INDEX.md`；`memory/next-session-prompt.md`。
