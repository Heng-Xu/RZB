# 110 kV区县年度规划模型

现行模型为 `joint_shared_measure.py`：同步优化邳州、市区的刚性和弹性四条路径，两方案都采用增容、储能、10 kV联络。回滚锚点eb417e0、回滚状态3011fdc已先提交推送。

在 `实验/研究/` 下运行：

```bash
python -m rebuild_2026.joint_shared_measure --case transfer_10pct --breakthrough all_years
python -m rebuild_2026.joint_shared_measure_audit rebuild_2026/outputs/joint_shared_measure/transfer_10pct_all_years_load_reallocation
python -m rebuild_2026.build_load_reallocation_delivery
```

按两区县每年弹性R>2.0验收；刚性R≤2.0、市区R低于邳州。R关系是指定规划条件，成本排序由求解产生。转供按区县内正常负荷转接建模，采用仿真联络通道；用户已确认保留转接后负荷的供电安全容量要求。10%是正常转接研究情景，额外事故恢复量不进入规划。转接减少原站供电任务并增加承接站供电任务，总量守恒。

输出为 `outputs/joint_shared_measure/transfer_10pct_all_years_load_reallocation/`，交付说明和工作簿在 `docs/2026-10-01三措施联合优化/`。固定highspy单线程、种子0，阶段限时480s，只接受最优状态。保存最低费用断点，续算可加 `--resume`，断点核验转供用途。三阶段依次求最低总费用、同价解更大弹性R、选定设备布局下更少正常负荷转接。

`regional_static_milp_v2.py`构造单路径问题及输出，`regional_static_milp_v2_audit.py`逐站复算，`joint_shared_measure_audit.py`独立核对四路径关系、费用和重复计算。原表核验由`two_district_source_audit.py`直接读取工作簿。

现行默认转供用途为`load_reallocation`。按`--transfer-mode legacy_outage_proxy`可追溯旧事故代理口径，该口径原结果在`outputs/joint_shared_measure/transfer_10pct_all_years/`，无额外R排序历史对照在`outputs/shared_measure_deterministic/`。9月29日`ordered_guide_*`保留为回滚基线，数据、价格和依赖继续保留。通用推荐矩阵与报告装配不是当前交付。
