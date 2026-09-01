# 当前状态快照

快照时间：2026-09-01 11:40（Asia/Shanghai）
状态：`COMPLETE`
任务：完成 v3.2 自主接管、模型/契约/CI 治理、联合稳健性复核、报告终审、冻结复现和远端验证。

## 当前 Git 与验证基线

- 分支：`model-v3.2-autonomous-review`。
- 本轮最终模型验证与冻结验证的基准提交：`fee3625c43d3f42b7514fbade69d7585813d38ec`；后续仅有 memory/handoff 文档提交，当前分支尖以 `git rev-parse HEAD` 为准。
- GitHub Actions：`v3.2 model validation` run `33466902615`（run 50）成功；`v3.2 frozen package verification` run `33466902676`（run 6）成功。
- 冻结清单生成验证提交：`b6c0429eabf639b83f309038dd7415c95cd0540c`；冻结包 manifest SHA-256：`b23efc98f93c7e8c01bd5b642cad78b3219baa790151679a5c1c7c11459f78f9`。
- 正式结果：`实验/研究/results/runs/real-2021-2025-v32-frozen/`；契约 SHA-256 `073e49e4e0ae49a1c221e1b26176e87117946506e941801dcccdb31d0671685d`；processed manifest SHA-256 `18a4570a6078e3e2673e710a34c85e79f5c3b8703d4f2fa1c66991c058881985`。

## 冻结主模型口径

- `contract=3.2.0 frozen`；两条优化路径均从 2021 实际在役资产共同起点出发，存量容量豁免。
- `PATH_OPT_CLR_UNBOUNDED` 不设统一 Rcap 上限；`PATH_OPT_CLR_LE_2` 仅约束 110 kV 规划期新增容量：`DeltaS_y <= max(2.0 * P_plus_y - S_2021, 0)`。
- 物理 CLR 与规划控制参数 Rcap 分离；不为满足 Rcap 生成退役候选；两路径均可行时直接比较累计在役等效年成本，弹性成本不高于刚性成本。
- `2×P2021` 仅二级标准化敏感性基准；EENS 与弃光无完整证据时不填 0。

## 已完成工作与验证证据

- 接续文档已清除 active v3.1 污染；旧提示词和历史 session 保留并标记 `HISTORICAL / SUPERSEDED`。
- base/overlay/resolved 契约统一；逐时门禁限定为 QX-00005 2025 110 kV 运行口径 40 台主变，35 kV context-only 与 2 台年末设备不进入正式逐时门禁；前沿字段统一为 `capacity_action_delta_mva`。
- CI 依赖触发链、workflow_dispatch、真实 SHA 溯源和重型流程防扇出已加固；冻结工作流补齐 numpy/scipy/xarray/linopy/highspy/networkx/scikit-learn 依赖。
- `scripts/run_annual_model.py` 已隔离为显式 legacy 入口，正式 v3.2 入口/工作流不调用它。
- 正式敏感性共 17 个情景，其中 6 个非笛卡尔联合压力情景；QX-00001 稳健近优下限仍为 `≥2.500`，QX-00005 仍为 `≥2.300`，扫描范围内未识别上界。
- 冻结数值复现：baseline、SOC、核心成本/动作/矩阵/阈值逐字节一致；前沿旧字段值一致，仅新增 3 个审计乘数列；敏感性由 11 增至 17 情景，旧 22 个模型/物理/成本字段一致。
- 固定全量入口：`278 passed`，退出码 0，用时 522.54 s；v3.2 专项测试 `67 passed`；报告/冻结/治理专项测试均通过。
- `run_all.py --dataset real_2021_2025 --config model_contract.yaml --skip-gen` 退出码 0；当前 HEAD 运行结果与冻结 baseline 18 个核心文件逐字节一致，连续 SOC 61,320 条记录通过物理审计。
- 报告全文与第一至第三章已完成 Word→PDF 渲染审查；PDF SHA-256 分别为 `cebd154e8d40c7fa7333cc4b3688f9c4adfd3aaeecc4fc885511b9eea50f0006`、`225eedcd1e6bd6beaf6e875c09ac8ecb00e72f457af165c2bd4fc64ce4680fbd`。

## 仍然存在的科学限制

- 2021—2025 实际设备级毛动作和实际路径成本不能由现有历史锚点完整回溯，实际路径成本保持“未识别”。
- 光伏为 2026 站级快照，与 2025 负荷只作跨年背景；缺同步负荷—光伏分解，不执行纯 PV 事实敏感性。
- QX-00005 以外片区证据不高于 `EVIDENCE_B`；缺阻抗、完整拓扑和运行方式时不升级为精确 AC/DC 潮流。
- 10 kV 六馈线仍是碎片森林；跨站转供只按容量包络和受端同时段余量条件引用，TIE-001 不形成定量结论。

## 下一步

无待修复的实现阻塞。若后续继续，只能在获得新的真实工程证据后按现有 v3.2 契约复算；新会话仍先以 Git、Actions、契约、正式输入和本快照为准，历史 memory/session 不得覆盖它们。
