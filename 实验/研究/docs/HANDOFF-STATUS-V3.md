# v3 新模型交接状态

更新时间：2026-08-13  
权威详细计划：`IMPLEMENTATION-PLAN-REAL-2021-2025-V3.md`  
可复制提示词：项目根目录 `NEXT-SESSION-PROMPT.md`

## 已完成

- 冻结 2021 共同基准、2022—2025 决策期、2025 价格年和累计在役 EAC 目标；
- 冻结三路径 `PATH_ACTUAL_2021_2025`、`PATH_OPT_CLR_UNBOUNDED`、`PATH_OPT_CLR_LE_2`；
- 冻结路径自身 CLR、储能防刷峰、离散减容、两条 10 kV 独立接口和两套转置矩阵格式；
- 写入完整阶段 0—7 实施计划、已核验数据事实、自动继续和暂停规则；
- 升级根目录 `AGENTS.md` 和项目 `skills/xuzhou-real-model/SKILL.md`；
- 新增 `tests/test_model_contract_v3.py` 并保留 v3 契约预期红灯证据；
- 重写 `NEXT-SESSION-PROMPT.md`，可在新对话直接使用。

## 当前验证基线

- 旧 v2 全量基线：`160 passed, 14 warnings`；仅证明旧脚手架可运行。
- v3 契约首次红灯：`6 failed`；当时机器契约、Skill 和提示词均未迁移。
- AGENTS、Skill 和提示词现已迁移；复测结果为 `5 failed, 1 passed`，剩余失败只对应旧机器契约。`model_contract.yaml` 更新前不得报告全绿。

## 下一模型第一批动作

1. 完整读取 `AGENTS.md`、v3 计划、旧机器契约、模型规格、项目 Skill 和数据说明书。
2. 在 `实验/研究/` 运行 `pytest -q tests/test_model_contract_v3.py`，记录剩余失败。
3. 把 `model_contract.yaml` 升级到 `3.0.0`，同步迁移模型规格、输出规范、运行手册及受影响旧测试。
4. 使阶段 0 目标测试全绿，再按详细计划连续执行阶段 1—7。

## 不能声称的事项

- 尚未完成 v3 真实数据模型、正式映射审批或正式求解；
- 尚无可交付的 v3 最终推荐容载比矩阵；
- 旧 `real_2025`、旧年度 C0/A/B 矩阵和旧 Word 均不得作为本轮最终结果。

## 用户是否还需确认

当前冻结方案下没有常规待确认事项。只有 `AGENTS.md` 第 9 节列明的定义冲突才暂停；局部数据缺口、工程实现、异常隔离和证据降级均自动处理。
