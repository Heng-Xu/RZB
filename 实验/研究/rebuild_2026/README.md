# reserve_policy_v4 建模流程

[现行方案](../docs/FINAL-POLICY-RECOMMENDATION-2026-09-24.md)；[冻结说明](../../../docs/FROZEN-RESERVE-POLICY-V4-2026-09-27.md)。

在 `实验/研究/` 运行：

```bash
export XUZHOU_MILP_TIME_LIMIT_SECONDS=600
python -m rebuild_2026.baseline_historical_proxy
python -m rebuild_2026.simulation_reserve_policy
python -m rebuild_2026.simulation_reserve_policy_audit
python -m rebuild_2026.simulation_reserve_sensitivity
```

依次完成历史区域容量分配、六条刚弹路径求解、独立约束与成本审计、参数敏感性。原始数据及已加工输入随项目保留；输入来源与哈希见冻结清单。默认每次 MILP 求解时限仍为 120 秒，完整复现可设为 600 秒；只有取得最优性证明才接受求解结果。

`joint_lifecycle_optimizer.py` 为共享优化内核；`annual_no_tie_investment_submodel.py` 提供 MILP 和储能参数；`incremental_cost.py` 提供全寿命现金流；`baseline_historical_proxy.py` 提供共同起点。其他来源处理脚本保留用于数据追溯，不代表另一个现行推荐方案。

已归档的增长模型与 v2/v3 结果见根目录 `历史归档/模型诊断-2026-09-26.zip`。旧文档中的运行命令仅代表历史过程。
