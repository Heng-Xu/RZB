# 徐州 110 kV 项目记忆规范

本目录保存项目的跨会话可恢复状态，服务于模型切换、会话中断和长任务交接。它不是日志仓库或数据备份库。

## 文件层级

| 文件/目录 | 用途 | 策略 |
|---|---|---|
| `INDEX.md` | 新会话的唯一导航入口、当前状态指针 | 必读 |
| `current.md` | 当前任务的可执行快照；只保留最新状态 | 必读 |
| `../claude_session_1.txt` | 截至 2026-08-27 的历史 Claude 中断导出，已标记 `HISTORICAL / SUPERSEDED` | 历史追溯 |
| `next-session-prompt.md` | 下窗口提示词与根目录交接文件的差异说明 | 接手时读 |
| `decisions/` | 已确认且影响后续实现的长期决策 | 追加式 |
| `sessions/YYYY-MM-DD/` | 每次会话的追加式状态记录 | 只增不改 |
| `MEMORY.md` 及各主题 md | Agent 长期记忆索引与课题笔记（2026-07 主线记录） | 按需读 |
| `codex_export.py` | Codex 会话 JSONL → Markdown 导出工具（本机无 pwsh） | 工具 |
| `codex-export/` | 导出的原始会话记录 | 可随时重生成 |

## 自动加载

仓库根目录 `AGENTS.md` 第 12 节已将本目录纳入启动流程。新会话先以实时 Git/Actions、frozen contract、正式输入和正式结果建立事实基线，最后读取 `INDEX.md` 与 `current.md` 承接遗留项。`claude_session_1.txt`、`archive/` 和旧 session 只作历史追溯，不能覆盖 v3.2 当前事实。

## 状态写入

状态取值固定为 `PLANNING`、`IMPLEMENTING`、`VERIFYING`、`BLOCKED`、`INCOMPLETE`、`COMPLETE`。开始任务、状态改变、关键验证结束、进入阻塞和会话结束时必须自动更新 `current.md`；历史记录写入 `sessions/YYYY-MM-DD/` 的新文件，不覆盖旧记录。

每条状态记录必须能回答：在做什么、完成了什么、还缺什么、有何阻塞、执行过哪些命令及退出码、证据文件路径、下一步是什么。任何无法由文件、命令输出或哈希支持的内容只能标记为假设。

## 安全与证据

- 不保存 Token、密码、个人隐私或未脱敏的甲方敏感数据。
- 大文件只登记路径、大小、SHA-256 和退出码，不入库。
- 本项目现已接入 GitHub 仓库 `Heng-Xu/RZB`；记忆应记录实际分支、SHA 和 Actions `head_sha`，同时继续登记关键产物 SHA-256。提交记录不能替代文件内容和 manifest。
- `memory/` 不能替代 `model_contract.yaml`、实施计划、问题台账等权威文件；规则变更必须同步到对应权威文件后，才在 `decisions/` 登记。
- `codex-export/` 是机器级原始导出，可能混入其他项目和本地配置，不作为公开仓库的项目历史；当前接续以实时仓库事实、`current.md` 和新增 `sessions/` 为准。

## 原始会话导出（可选兜底）

需要回溯原始对话时手动执行：

```bash
python3 memory/codex_export.py --output memory/codex-export --days 31
```
