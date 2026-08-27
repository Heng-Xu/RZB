# 徐州 110 kV 项目记忆规范

本目录保存项目的跨会话可恢复状态，服务于模型切换、会话中断和长任务交接。它不是日志仓库或数据备份库。

## 文件层级

| 文件/目录 | 用途 | 策略 |
|---|---|---|
| `INDEX.md` | 新会话的唯一导航入口、当前状态指针 | 必读 |
| `current.md` | 当前任务的可执行快照；只保留最新状态 | 必读 |
| `../claude_session_1.txt` | 负责人确认的最新 Claude 中断接续记录；进度冲突时优先于旧 memory | 必读 |
| `next-session-prompt.md` | 下窗口提示词与根目录交接文件的差异说明 | 接手时读 |
| `decisions/` | 已确认且影响后续实现的长期决策 | 追加式 |
| `sessions/YYYY-MM-DD/` | 每次会话的追加式状态记录 | 只增不改 |
| `MEMORY.md` 及各主题 md | Agent 长期记忆索引与课题笔记（2026-07 主线记录） | 按需读 |
| `codex_export.py` | Codex 会话 JSONL → Markdown 导出工具（本机无 pwsh） | 工具 |
| `codex-export/` | 导出的原始会话记录 | 可随时重生成 |

## 自动加载

仓库根目录 `AGENTS.md` 第 12 节已将本目录纳入强制启动流程。新会话必须先读根目录 `claude_session_1.txt`，再读 `INDEX.md` 和 `current.md`，然后按第 1 节顺序读取其余必读文件。就进度、完成状态、遗留项和下一步而言，`claude_session_1.txt` 优先于较旧 memory；模型与业务口径仍以 `AGENTS.md`、`model_contract.yaml` 及同步后的负责人决策为准。

## 状态写入

状态取值固定为 `PLANNING`、`IMPLEMENTING`、`VERIFYING`、`BLOCKED`、`INCOMPLETE`、`COMPLETE`。开始任务、状态改变、关键验证结束、进入阻塞和会话结束时必须自动更新 `current.md`；历史记录写入 `sessions/YYYY-MM-DD/` 的新文件，不覆盖旧记录。

每条状态记录必须能回答：在做什么、完成了什么、还缺什么、有何阻塞、执行过哪些命令及退出码、证据文件路径、下一步是什么。任何无法由文件、命令输出或哈希支持的内容只能标记为假设。

## 安全与证据

- 不保存 Token、密码、个人隐私或未脱敏的甲方敏感数据。
- 大文件只登记路径、大小、SHA-256 和退出码，不入库。
- 本项目 `.git` 曾确认不可用：记忆以文件本身为准，关键产物登记 SHA-256；若日后 git 可用，可在每次记忆更新后附加一次提交，但不得以提交记录替代文件。
- `memory/` 不能替代 `model_contract.yaml`、实施计划、问题台账等权威文件；规则变更必须同步到对应权威文件后，才在 `decisions/` 登记。
- `codex-export/` 是机器级原始导出，可能混入其他项目和本地配置，不作为公开仓库的项目历史；项目接续以 `claude_session_1.txt` 和 `sessions/` 为准。

## 原始会话导出（可选兜底）

需要回溯原始对话时手动执行：

```bash
python3 memory/codex_export.py --output memory/codex-export --days 31
```
