# 当前状态快照

快照时间：2026-08-29 07:40（Asia/Shanghai）
本次 memory 任务状态：`COMPLETE`
任务：在 GitHub 分支 `model-v3.2-autonomous-review` 的真实代码、输入、日志和结果基础上完成 v3.2 模型终审、冻结、正式结果与研究报告支撑材料输出。
状态依据：已读取根目录 `claude_session_1.txt` 并以其优先级接管；当前工作副本为 `/tmp/rzb-v32-work`，模型终审内容、CI 修正和记忆补充均已提交并推送到远端，最终本地分支与远端分支已完成 SHA 一致性核对。旧 v3.1 严格归一口径不再作为 v3.2 主模型。

## 本次接管核对

- 根仓库分支为 `main`，相对 `origin/main` 落后 6 个提交；根目录用户 `prompt.md` 和 memory 修改保留，不在根仓库直接覆盖。
- `/tmp/rzb-v32-work` 分支为 `model-v3.2-autonomous-review`，HEAD 为 `708a503643df85e166b8f6680c9b1c7d73856d7b`；v3.2 实现、测试、契约、正式结果、报告材料及正式基线 CI 修正已提交并推送。生成型合成结果文件为全量测试副作用，已恢复且未纳入修正提交。
- 推送后 Actions 中模型验证 `33219378246`、chronology preflight `33219378236`、实际资产主运行 `33219378228` 和 Rcap frontier `33219378257` 已 Success；正式基线 `33219378290` 曾 Failure。经本地复现确认，模型入口退出码为 0，失败原因是工作流读取已废弃的 `recommendation_matrix_v32_base.csv`，而当前入口实际生成 `policy_2025_summary.csv`；修正已提交为 `708a503`。新正式基线 `33220722649` 已 Success 并生成 1 个 artifact（digest `sha256:f43b3c88547fa9a5ab4b8aaed9ffa62df3b56beb4d8812af2dc2bf9ab6be0aca`），新模型验证 `33220722628` 已 Success。

## 契约版本

目标契约 `实验/研究/model_contract.yaml` v3.2.0，状态为终审中；AGENTS.md v3.4。主模型采用 2021 年实际在役资产共同基线，存量容量豁免，Rcap 只约束 2022—2025 年新增容量；`2×P2021` 仅作标准化对照/敏感性。Rcap 与优化后物理 CLR 分开，不恢复“Rcap 与 actual CLR 取交集”。

## 已完成（有证据）

- v3.2 实际资产主入口已运行成功，生成两条正式政策方案、年度结果、缺口诊断和连续 SOC 证据。
- QX-00005 8760 h 连续校核已落盘：40 行设备摘要、61,320 行曲线；弹性方案 465 柜、严格方案 962 柜；SOC、跨零、同时充放电、功率限制均无越界。
- Rcap 粗扫描 17 点并完成局部细化：QX-00001 动作切换约 `2.359→2.360`，QX-00005 约 `2.171→2.172`；QX-00003/04/07 在扫描范围内不绑定，QX-00008/09/10 未形成 110 kV 物理可行集。
- 参数压力场景覆盖负荷 ±5%、储能/扩容成本 ±20%、cosφ/beta OAT；光伏独立敏感性因缺同步负荷/PV分解和馈线点位证据不可执行，需作为边界记录。
- 10 kV 联络最终口径保持：TIE-001 不形成定量结论；TIE-002、TIE-003 和 NEW-TIE-01 只按容量包络/局部工程化互济能力表达，不宣称完整 AC 潮流；六馈线碎片森林导致跨站联络后电压与支路负载校核不可实现。

## 当前科学性审查结论

- 2021 官方容量锚点与当前设备表历史回溯不闭合；主模型可使用官方区域总量基线，但设备级物理证据明确限于 2025 在役口径，不能伪造 2021 设备重建。
- 2025 QX-00005 110 kV 运行口径为 20 站、40 台主变；BDZ-00056 两台年末新增设备不进入该口径。静态站表与主变表存在若干编码差异，必须进入数据质量终审表，不静默重映射。
- 活动文档中的 v3.1 严格归一起点、跨口径成本禁比、旧推荐值和 10 kV 过度潮流表述已清理；正式结果 manifest 已标记 `MODEL V3.2 FROZEN`。

## 关键证据路径

- Actions：模型验证 `33219378246`、`33220722628`；chronology preflight `33219378236`；实际资产主运行 `33219378228`；Rcap frontier `33219378257`；正式基线 `33220722649`。上述最终复验均为 Success。
- 本地基线临时结果：`/tmp/rzb-v32-local-actual-primary-v32`、`/tmp/rzb-v32-run-all`。
- Rcap：`/tmp/rzb-v32-frontier`、`/tmp/rzb-v32-refinement`。
- 参数场景：`/tmp/rzb-v32-sensitivity`、`/tmp/rzb-v32-sens-refined`、`/tmp/rzb-v32-sensitivity-suite`。
- 规范化数据：`实验/研究/data/processed/real_2021_2025/`。

## 最终验证证据（Git 已推送，Actions 已核验）

- 固定全量回归：在 `实验/研究/` 执行 `env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh`，退出码 0，收集 251 项，`251 passed, 14 warnings`，耗时 521.69 s；警告均为 Matplotlib/pyparsing 弃用提示。新增测试先在旧工作流下失败，修正后通过；精确复现正式入口退出码 0，后处理文件检查也退出码 0。
- 报告 S1–S4：`实验/研究/scripts/report_style_scan.py` 扫描第一至第七章，0 处标记；PDF 关键页第 40～43 页视觉抽查通过。
- Word→PDF：`研究报告/初稿/渲染审查/全文初稿_渲染审查_2026-08-29_v32.pdf`，48 页、3,547,205 bytes，SHA-256 `d83359750a74b6394e20d408176e1cee5a5f951149a13bb6fa5f6c8c9f8be6e7`。
- 正式结果：`实验/研究/results/runs/real-2021-2025-v32-frozen/manifest.json`，模型版本 `3.2.0`，粗扫描 136 点、局部细化 104 点、敏感性场景 11 组；终审记录副本 SHA-256 `df4aaadeeed096b0ba86d595b0539c5d4ddf3469a34e9a3812fdd8c70deb2b63`。
- v3.2 决策记录：`memory/decisions/2026-08-29-v3.2实际资产共同起点与冻结.md`。
- Git 推送：`git push origin model-v3.2-autonomous-review` 已成功上传终审内容、CI 修正及记忆记录；最终 `git ls-remote --heads origin model-v3.2-autonomous-review` 已核对返回与当前工作副本 HEAD 相同的 SHA。
- 推送后 Actions：模型验证 `33219378246`、chronology preflight `33219378236`、实际资产主运行 `33219378228`、Rcap frontier `33219378257` 已 Success；正式基线 `33219378290` Failure 已定位为 CI 后处理文件名错误；修正提交 `708a503` 已推送，新正式基线 `33220722649` 和模型验证 `33220722628` 均 Success，仅有 GitHub runner 的 Node.js 20 弃用 warning。
- 根目录同步：已按最终提交文件清单同步至项目根目录并逐项 `cmp` 通过；根目录 `main` 和原有 `prompt.md`/历史会话保留，不在根目录强行切换分支。

## 阻塞与下一步

- 无需暂停的业务阻塞。远端 artifact/log 权限限制只影响逐字下载，不影响本地同 SHA 复核；TIE-001 按负责人决定不再收资。
- v3.2 模型、报告、门禁、Git 上传、远端 SHA 核验和根目录同步均已完成，本任务结束。GitHub 的 Node.js 20 弃用 warning 不改变模型判定；若后续重新运行出现模型或数据失败，需重新打开终审而不是直接宣称完成。TIE-001 按负责人决定不再收资。
