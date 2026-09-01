# v3.2 自主复核与冻结闭环实施计划

> 本计划执行负责人 2026-09-01 已批准的接续要求，不重新讨论或改写 v3.2 主模型。

## 目标

在 `model-v3.2-autonomous-review` 上消除旧 v3.1 接续污染，统一 base/overlay/resolved 契约，补齐正式工作流依赖触发链，隔离旧年度模型入口，复现冻结结果并完成科学性与报告一致性终审。正式数值只有在证实存在真实模型缺陷时才允许更新，原冻结目录不得静默覆盖。

## 实施顺序

1. 保存当前冻结产物、manifest 与输入哈希，记录 Git/Actions 基线。
2. 先写失败测试，覆盖 active handoff、v3.2 resolved 契约、逐时审批门禁、正式产物禁词、legacy 入口、工作流依赖、冻结 manifest 和成本包含关系。
3. 清理 `prompt.md`、`NEXT-SESSION-PROMPT.md`、`memory/current.md`、`memory/INDEX.md` 及当前接续标记；历史 session 保留原文并标记 `HISTORICAL / SUPERSEDED`。
4. 修正 `model_contract.yaml` 与 overlay 的逐时审批状态和 elasticity schema；在 `src/v32_contract.py` 中校验 canonical resolved contract。
5. 建立 `.github` 依赖策略并修正七个 v3.2 workflow；快速 CI 广覆盖，重型流程按真实输入和传递依赖触发，均支持手动调度并记录 commit SHA。
6. 为 `scripts/run_annual_model.py` 增加默认拒绝执行的归档守卫，验证正式入口、工作流与正式产物均不引用 v2 口径。
7. 复跑 focused tests、actual baseline、frontier、refinement、既有 sensitivity；再按决策翻转风险选择少量联合压力场景。
8. 在临时目录重建 formal outputs，与冻结目录逐文件及逐字段比较；如数值有变化，先定位差异来源。
9. 最小化修正第四至第七章、正式矩阵及生成脚本中的口径/表述问题，执行 S1—S4 审查并完成 Word→PDF 渲染闭环。
10. 跑全量测试和最终冻结核验，按逻辑提交、推送，核对远端 SHA 与 Actions；最后刷新 memory/current 和 session 记录。

## 关键验证命令

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr pytest -q <focused tests>
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr python scripts/run_all.py --dataset real_2021_2025 --config model_contract.yaml --skip-gen
```

冻结比对至少覆盖 policy year/action/cost、QX-00005 chronology/SOC、coarse frontier、refined thresholds、sensitivity、110/35 kV formal matrices、recommendation outputs 与 manifest/hash。
