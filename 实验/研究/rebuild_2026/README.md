# 110 kV区县年度规划模型

现行模型为 `joint_shared_measure.py --case station_rate`：同步优化邳州、市区的刚性和弹性四条路径，两方案均允许增容、储能、10 kV联络。回滚锚点 `eb417e0`、回滚状态 `3011fdc` 已先提交推送。

在 `实验/研究/` 下运行：

```bash
python -m rebuild_2026.joint_shared_measure --case station_rate --breakthrough all_years --stage-seconds 900 --primary-relative-gap 0.005 --capacity-relative-gap 0.005 --warm-start rebuild_2026/outputs/joint_shared_measure/station_rate_all_years_load_reallocation/initial_feasible_seed.npz
python -m rebuild_2026.joint_shared_measure_audit rebuild_2026/outputs/joint_shared_measure/station_rate_all_years_load_reallocation
python -m rebuild_2026.build_load_reallocation_delivery
```

输出在 `outputs/joint_shared_measure/station_rate_all_years_load_reallocation/`，交付说明、工作簿和参数说明在 `docs/2026-10-01站级转供率三措施优化/`。每区县各年弹性R≥2.001、刚性R≤2.0，同方案市区低于邳州至少0.001；费用排序单独验收。容量条件均通过，但市区弹性费用17201.60万元高于刚性2818.17万元，邳州弹性13855.33万元低于刚性19558.17万元。当前未实现全部原要求。市区弹性额外增容主要由容载比下限驱动。

区县内正常负荷转接用站级转出、承接量建模，总量守恒，容量安全要求按转接后负荷校核。既有能力为转供率乘转接前年度站级负荷基数：邳州28.2879%、市区50%，两方案共用；当前基数为正向峰值代理，尚非核实的供电区域毛负荷。新增独立联络单元7.49106117 MW由局部线路原型标定，只增加能力比例。A类比例上限70%、B/C类50%；双端计数、共享新增预算及106.8万元单项目价格避免重复计算。站间分配及端点配对在求解后生成，供仿真计数和配置核对，不据此推断真实馈线路由。

固定highspy单线程、种子0，每阶段限时900秒。费用阶段0.5%认证间隙；固定费用阶段所选刚性整数布局后，以0.5%间隙优选弹性R；最后固定所有整数布局求最小连续转接量。记录费用下界、R之和上界和实际间隙，仅交付达到约定精度的结果。容载比、负荷守恒和容量约束始终严格核验。正式重复求解18份CSV逐字节一致，不将认证近优称为精确全局最优。

可省略 `--warm-start` 从无初始解开始；初始解须经当前全部约束、边界及整数性校验。`--capacity-preference-scope global_joint` 可展开全部刚性布局的偏好搜索；两阶段分别设 `--primary-relative-gap 1e-9 --capacity-relative-gap 1e-9` 可要求更高证明精度，耗时更长。`--resume` 续算须采用相同转供口径和当前矩阵。

`regional_static_milp_v2.py` 构造模型及输出，`station_transfer_equivalent.py` 提供等效能力和局部标定，`regional_static_milp_v2_audit.py` 逐站复算，`joint_shared_measure_audit.py` 核对四路径关系、费用和重复计算。原表核验由 `two_district_source_audit.py` 直接读取工作簿。

此前 `transfer_10pct_all_years_load_reallocation/` 为10%正常转接历史对照；`transfer_10pct_all_years/` 和 `shared_measure_deterministic/` 为旧事故代理口径。9月29日 `ordered_guide_*` 保留为回滚基线。原始数据、价格证据和依赖继续保留，Word/PDF尚未按本轮结果重建。
