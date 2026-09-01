# RZB v3.2 当前接续

更新时间：2026-09-01

## 五分钟事实基线

- 工作分支：`model-v3.2-autonomous-review`。
- 当前 HEAD：以 `git rev-parse HEAD` 及 `git ls-remote origin refs/heads/model-v3.2-autonomous-review` 的实时结果为准；本文件不固化会过期的提交 SHA。
- 模型契约：`contract=3.2.0 frozen`。
- 正式结果：`实验/研究/results/runs/real-2021-2025-v32-frozen/`。
- 最近验证、冻结验证和冻结包生成来源的提交 SHA 分开登记，具体值以 `memory/current.md` 和 GitHub Actions 的 `head_sha` 共同核对。

## 唯一正式模型

两条优化方案共享 2021 年实际在役资产起点，既有容量存量豁免。`PATH_OPT_CLR_UNBOUNDED` 不设统一 Rcap 上限；`PATH_OPT_CLR_LE_2` 从 2022 年起仅对 110 kV 规划期新增容量施加：

```text
DeltaS_y <= max(Rcap * P_plus_y - S_2021, 0)
```

物理 CLR 等于同电压等级在役实物容量除以方案自身同步正向最大净负荷，与规划控制参数 Rcap 分开；存量豁免后物理 CLR 可以高于 Rcap。两方案的基线、候选、物理约束、成本库和求解精度相同，两者均可行时直接比较累计年化成本，并校验弹性方案成本不高于刚性方案。

`2×P2021` 只保留为二级标准化敏感性基准。主模型不为满足 Rcap 生成退役候选，不设置弃光变量；EENS 无完整证据时不得填 0。历史版本和旧入口只作追溯，不能进入正式成果。

## 接管顺序

1. 先核对 Git、远端分支、最新 commits 和 GitHub Actions 的 `head_sha`。
2. 依次读取 `AGENTS.md`、base contract、v3.2 overlay、`load_v32_contract()` resolved contract、processed manifest 与逐时审批表。
3. 核对 frozen baseline/frontier/refinement/sensitivity/formal matrices，再读报告和报告脚本。
4. 最后读 `memory/current.md`；`claude_session_1.txt`、`memory/archive/` 和旧 session 仅用于历史追溯。

模型定义优先级为：`AGENTS.md` → frozen base/overlay/resolved contract → 正式代码 → 正式输入与结果 → 报告 → memory/历史记录。

## 当前状态

本文件只保留接管背景和固定口径；具体任务状态、已完成验证、证据路径和下一步只以 `memory/current.md` 最新快照及实时 Git/Actions 为准。

除 `AGENTS.md` 明列的真实业务冲突外，继续自动执行，不重新询问是否确认 v3.2。
