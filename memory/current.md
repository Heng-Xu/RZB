# 当前状态快照

快照时间：2026-09-01 13:58（Asia/Shanghai）
状态：`COMPLETE`
任务：在已完成的 v3.2 自主复核基础上，处理交接污染、敏感性语义、EAC 年化参数稳健性、冻结 provenance、治理测试和最终报告一致性。

## 本轮接管任务

- 当前分支 HEAD 以实时 `git rev-parse HEAD` 与远端核验为准；本轮冻结交付提交及不可变 annotated tag `v3.2-frozen-20260901` 的 peeled target 为 `470e8220a7c92f241c4b7a0449d98c584a15de56`。
- 当前最终 `v3.2 model validation` run `33475112177` 与 `v3.2 frozen package verification` run `33475112260` 均以 `470e8220a7c92f241c4b7a0449d98c584a15de56` 为 `head_sha` 且成功。年化敏感性 workflow run `33473134881` 以 `086509dcfb37b7a082bf279dbf76b62d30c643a0` 成功；其后仅有不改变年化结果的报告/receipt 文档提交。
- 当前仅允许增量治理和新增敏感性证据，不重新设计或调整 v3.2 主模型；本轮增量已完成并通过本地与 CI 验证。

## 当前 Git 与验证基线

- 分支：`model-v3.2-autonomous-review`。
- 本轮完整模型验证与冻结验证提交为 `470e8220a7c92f241c4b7a0449d98c584a15de56`；此前 `086509d` 上的全链路结果作为增量代码/证据先验核验，最终 470e822 已重新通过 model validation 与 freeze verification。
- GitHub Actions：最终 `v3.2 model validation` run `33475112177`（run 52）成功；最终 `v3.2 frozen package verification` run `33475112260`（run 8）成功；年化敏感性 run `33473134881`（run 1）成功。
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
- 固定全量入口：`298 passed, 14 warnings`，退出码 0，用时 522.56 s；新增打包、治理、provenance 测试均通过。
- `run_all.py --dataset real_2021_2025 --config model_contract.yaml --skip-gen` 在 470e822 当前代码上退出码 0；输出到 `/tmp/rzb-v32-formal-e2e-470` 的 baseline 21 个核心文件与 frozen baseline 逐文件一致，连续 SOC 61,320 条记录通过物理审计。
- 报告全文与第一至第三章已完成 Word→PDF 渲染审查；PDF SHA-256 分别为 `cebd154e8d40c7fa7333cc4b3688f9c4adfd3aaeecc4fc885511b9eea50f0006`、`225eedcd1e6bd6beaf6e875c09ac8ecb00e72f457af165c2bd4fc64ce4680fbd`。

## 仍然存在的科学限制

- 2021—2025 实际设备级毛动作和实际路径成本不能由现有历史锚点完整回溯，实际路径成本保持“未识别”。
- 光伏为 2026 站级快照，与 2025 负荷只作跨年背景；缺同步负荷—光伏分解，不执行纯 PV 事实敏感性。
- QX-00005 以外片区证据不高于 `EVIDENCE_B`；缺阻抗、完整拓扑和运行方式时不升级为精确 AC/DC 潮流。
- 10 kV 六馈线仍是碎片森林；跨站转供只按容量包络和受端同时段余量条件引用，TIE-001 不形成定量结论。

## 本轮已验证增量

- sensitivity CLI 的 `--scenario all` 已默认选择 17 个正式参数场景；显式 `physical`/`one-factor`/`interaction` 分别为 5/6/6 个。
- `pf095_beta080` 基准复现控制已用当前代码重跑，并与冻结主前沿 23 个共享字段、136 行逐项一致；聚焦治理/敏感性测试当前为 43 passed、2 deselected。
- 已实现契约范围内 10 个年化参数定向场景、独立 secondary standardized benchmark 和三层 SHA freeze receipt；年度敏感性正式目录已归档，全文 v33 Word/PDF 已完成 A4 渲染审查。
- 10 个场景目录 manifest 的逐文件字节数/SHA-256 门禁通过；20 条片区记录均为 `ROBUST`，QX-00001/QX-00005 阈值保持 2.359–2.360 / 2.171–2.172，稳健下限保持 2.5 / 2.3。
- 本地 `--scenario all --grid coarse` 重跑 17 个正式场景得到 2312 行；与 frozen sensitivity 22 个共享字段按唯一键在 `rtol/atol=1e-12` 内一致，最大绝对数值差 `2.84e-14`；基准控制详细 actions/cost breakdown 逐项一致。
- 报告 S1/S3 扫描 0 处标记；全文 v33 DOCX SHA-256 `b9bb28e3f731208127194d1789539e7cfc53570f7305712a2c1e8ce8c019317be`；A4 PDF 37 页、3,135,171 bytes，SHA-256 `2dc7e5dd2b73b97b4a04f1824ff274a0d9e0ceeb063b2c415b466d848931bf5b`。
- tracked freeze receipt 位于 `实验/研究/results/runs/real-2021-2025-v32-frozen/freeze_verification_receipt.json`：frozen manifest SHA `b23efc98f93c7e8c01bd5b642cad78b3219baa790151679a5c1c7c11459f78f9`；generated/package SHA 为 `b6c0429eabf639b83f309038dd7415c95cd0540c`；checkout/last verified SHA 为 `470e8220a7c92f241c4b7a0449d98c584a15de56`；workflow `33473134836`，PASS。
- 目标代码、正式证据、报告和治理变更均已提交；本快照随本次更新提交，工作区应保持干净。

## 下一步

本轮无待完成的实现或验证事项。后续只有在获得新的真实工程证据后，才可按现有 v3.2 契约新增复算；新会话仍先以 Git、Actions、契约、正式输入和本快照为准，历史 memory/session 不得覆盖它们。
