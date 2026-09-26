# 徐州地区 110/35 kV 容载比弹性指标优化研究

现行报告依据为 **reserve_policy_v4 + 年度指标推荐矩阵（2026-09-27）**；专用环境下六路径完整复现通过，年度矩阵和独立价格敏感性已核验。

- [当前方案及推荐矩阵](实验/研究/docs/FINAL-POLICY-RECOMMENDATION-2026-09-24.md)
- [冻结说明、复现流程和验证记录](docs/FROZEN-RESERVE-POLICY-V4-2026-09-27.md)
- [年度指标矩阵成果](实验/研究/rebuild_2026/source_audit/capacity_release_simulation/reserve_policy_v4/recommendation_matrix/推荐矩阵成果说明.md)
- [文件导航](docs/CURRENT-WORKFLOW.md)
- [导则与负荷—容量关系](实验/研究/docs/容载比负荷容量关系-导则核验-2026-09-23.md)

研究范围：邳州 35 kV、邳州 110 kV、市区 29 站 110 kV。目标为增量全寿命成本现值最小；刚性逐年 R≤2.0，弹性联合比选扩容、储能和线路转供。研究假设及工程边界以现行方案为准。

原始交付数据位于 `实验/研究/data/tuomin/`；现行结果位于 `实验/研究/rebuild_2026/source_audit/capacity_release_simulation/reserve_policy_v4/`。前版结果不能用于本版报告。

已将增长诊断脚本及 v2/v3 结果收拢到 `历史归档/模型诊断-2026-09-26.zip`，清单见 `docs/CLEANUP-2026-09-26.json`。其余输入生成脚本、成本与来源证据保留，以支持追溯。
