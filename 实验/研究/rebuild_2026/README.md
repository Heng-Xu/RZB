# 110 kV区县年度规划模型

2026-10-01恢复9月29日 `eb417e0` 的同措施集成本优化。[回滚记录](../../../docs/ROLLBACK-2026-10-01.md)列出旧版限制和新轮目标。刚性、弹性都允许主变增容、储能、10 kV联络（既有转供及新建）。新轮优化在回滚状态提交推送后启动，输出另存。

在 `实验/研究/` 下复现9月29日基线：

```bash
python -m rebuild_2026.two_district_ordered_guide_run
python -m rebuild_2026.two_district_ordered_cost_sensitivity
python -m rebuild_2026.two_district_ordered_result_audit
```

基线结果为 `outputs/ordered_guide_*`。核心求解器是 `regional_static_milp_v2.py`，逐站约束与费用核验为 `regional_static_milp_v2_audit.py`，原表核验为 `two_district_source_audit.py`。数据读取、成本函数和MILP基础类有历史模块依赖，继续保留。

原始数据在 `../data/tuomin/`，加工输入在 `source_audit/`。成本依据见 `研究报告/数据来源/2026-09-28_10kV线路与成本依据/`。基线市区刚性1.8和额外排序条件不是本轮已定结果。删除了9月30日无联络弹性和实际路线旁支，清单见 `docs/CLEANUP-2026-10-01.json`。独立假定区域矩阵仅作为待复核辅助材料。
