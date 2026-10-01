# 110 kV区县年度规划模型

当前入口为`joint_shared_measure.py --case station_rate`，默认市区A类、全部转接后负荷。市区29座仿真站统一按用户确认的A类规划，样本原类别和既有设备事实另列保留；市区既有及目标转供率50%、上限70%。邳州仍按原B/C类别，既有率28.287889%、目标30%、上限50%。两个方案、两个区县均采用主变退出后保障全部转接后负荷的同一静态研究情景。

在`实验/研究/`下运行：

```bash
python -m rebuild_2026.joint_shared_measure --case station_rate --breakthrough all_years --n1-load-requirement full --city-area-class A --stage-seconds 1800 --primary-relative-gap 0.005 --capacity-relative-gap 0.005 --capacity-warm-start rebuild_2026/outputs/joint_shared_measure/station_rate_all_years_load_reallocation_full_service_city_A/capacity_preference_initial_seed.npz
python -m rebuild_2026.joint_shared_measure_audit rebuild_2026/outputs/joint_shared_measure/station_rate_all_years_load_reallocation_full_service_city_A
python -m rebuild_2026.build_load_reallocation_delivery
python -m rebuild_2026.station_transfer_equivalent
```

结果在`outputs/joint_shared_measure/station_rate_all_years_load_reallocation_full_service_city_A/`，交付在`docs/2026-10-01市区A类全负荷优化/`。刚性、弹性同步优化增容、储能及10 kV联络三类措施。392个站年通过独立复算：刚性每年R≤2.0，两区县弹性每年R≥2.001，同方案市区每年低于邳州至少0.001。两区县弹性费用均低于刚性；费用排序未作为强制投资约束。

| 区县 | 刚性现值万元 | 弹性现值万元 | 弹性节省比例 |
|---|---:|---:|---:|
| 邳州 | 139298.30 | 18914.64 | 86.42% |
| 市区 | 132777.13 | 24478.22 | 81.56% |

费用阶段实际认证间隙0.2736%；固定所选刚性整数布局后，容载比偏好阶段实际间隙0.5000%，均满足0.5%目标。最后固定全部整数布局求最小连续转接量。费用阶段独立从无外部初始解计算，容载比阶段共用经完整校核的可行种子并重新认证，18份CSV逐字节一致。偏好上界限于所选刚性基准，不称全部刚性布局上的精确全局最大容载比。 固定highspy单线程、随机种子0；时间上限只限制等待，不接纳未达到目标精度的阶段。`--resume`可续用已通过当前模型校核的费用断点，并重新求解后续阶段。

站级转供基数为优化前固定的年度正向峰值代理，尚非已核实的区域毛负荷；新增独立等效单元7.49106117 MW由局部区段标定，只提升转供能力比例。站间分配和项目双端配对供仿真计数，不证明实际线路可达性。储能按峰段持续时间折算静态支撑，SOC与充放电时序尚未显式求解。 两端关联单元数合计等于项目数两倍，每项目按106.8万元计费一次；全区县超出既有预算的实际转出量合计≤项目数×7.49106117 MW。

费用计同价新增措施全寿命现值；2021共享起点，2022—2025回算，保留原年度负荷。`regional_static_milp_v2_audit.py`逐站复算，`joint_shared_measure_audit.py`检查四路径、费用、硬约束与重复结果。原表审计由`two_district_source_audit.py`直接读取工作簿。

历史混合类别及首阶段最低供电量需显式加`--n1-load-requirement bc_min_service_static --city-area-class source`；旧初始解不能直接用于本轮，需通过当前矩阵全部约束和整数性校核。`--capacity-preference-scope global_joint`可扩展偏好搜索范围；更高证明精度耗时更长。回滚锚点`eb417e0`、回滚状态`3011fdc`已先推送。原始数据、价格证据和回滚对照保留，Word/PDF未重建。
