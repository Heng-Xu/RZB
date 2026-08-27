# Git 基线推送与 Claude 优先级登记

- 时间：2026-08-27 15:19（Asia/Shanghai）
- 状态：`VERIFYING`
- 任务：按负责人确认的范围，以 `实验/研究/` 为核心建立项目 Git 基线并推送到 `Heng-Xu/RZB`；将 Claude 最新中断记录的接续优先级写入约束和 memory。

## 已完成

- 根目录 `claude_session_1.txt` 已纳入版本库，并在 `AGENTS.md` §1、§12.1、§12.5、`memory/README.md`、`memory/INDEX.md`、`memory/next-session-prompt.md` 和 `NEXT-SESSION-PROMPT.md` 中登记为进度接管最高优先级记录。
- 已补充 `README.md`、`docs/PROJECT-REPOSITORY-MAP.md` 和 `实验/研究/README.md`，说明从约束、skills/agents、数据血缘、模型代码、结果到研究报告的依赖关系。
- 公开上传范围按负责人确认执行：纳入约束、skills、agents、memory、脱敏数据、模型、测试、结果、报告及参考材料；排除本地凭据、机器配置/锁文件、机器级会话导出、缓存、`__pycache__` 和重复的大压缩包。
- 已初始化本地 `main`，首个提交为 `48acbd4a93ad3ba16c203ad0e335360bc33b0717`，提交统计为 1095 个文件、1,325,263 行新增。
- SSH 认证成功；远端原为空。`git push -u origin main` 退出码 0；推送后通过提升网络权限执行 `git ls-remote --heads origin`，确认 `origin/main` 指向同一完整提交。

## 验证命令与结果

| 命令 | 退出码 | 结果/证据 |
|---|---:|---|
| `env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr pytest -q tests/test_model_contract_v3.py`（工作目录 `实验/研究`） | 0 | `7 passed in 0.17s` |
| `env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh` | 130 | 包含多个会重复调用完整弹性扫描的真实 v3 测试/fixture；第一份临时 `manifest.json` 于 15:11:39 生成并完成结构校验，后续重复回归因耗时过长由本 Agent 中断，未宣称本次全量全绿 |
| `ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new -T git@github.com` | 1 | GitHub 返回“已认证但不提供 shell”，证明密钥认证成功；非 shell 访问失败属于预期 |
| `git commit --amend ...` | 0 | 修正提交正文中的换行表达，最终提交为上述完整 SHA |
| `git push -u origin main` | 0 | `main -> main`，并设置本地分支跟踪 `origin/main` |
| `git ls-remote --heads origin`（网络受限环境） | 128 | 沙箱 DNS 失败；随后提升网络权限复核成功 |
| `git ls-remote --heads origin`（提升网络权限） | 0 | 首次推送后返回 `48acbd4a93ad3ba16c203ad0e335360bc33b0717 refs/heads/main`；后续 memory 记录提交继续同步到同一远端 |

## 安全与边界审计

- 暂存文件数：1095；暂存内容未发现超过 GitHub 普通 Git 100 MB 限制的文件。
- 暂存路径未命中：`Tushare.ma`、`memory/codex-export/`、本地 `.claude` 锁/设置、缓存、`__pycache__`、`.gstack/` 和 `参考文献/前沿调研.tar.gz`。
- 对暂存文本执行常见私钥/令牌模式扫描，未发现命中；未读取或输出本地 `Tushare.ma` 内容。
- `参考文献/前沿调研.tar.gz` 大小为 171,513,560 bytes，与已解包参考文献目录重复，因未安装 Git LFS 且非核心可复现输入，未上传该压缩包。

## 下一步

1. Git 上传任务已完成；如需全量回归，拆分真实端到端入口或预留较长运行窗口，随后继续研究报告主线。
2. 继续围绕 `实验/研究/` 的 v3 模型结果、CSV/Markdown 证据和技术附表撰写全面、详实、科学严谨的弹性容载比规划研究报告。
3. 负责人完成 Word/WPS 目录页码与版式终审；后续接手 Agent 仍须先读 `claude_session_1.txt`，再读 `AGENTS.md` 与 memory。
