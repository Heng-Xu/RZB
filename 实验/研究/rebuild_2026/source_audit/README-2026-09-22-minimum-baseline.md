# 2026 年独立重构管线

项目根目录 `prompt.md` 是最高任务依据；已确认模型口径见 [`../docs/REBUILD-2026-MODEL-SPEC.md`](../docs/REBUILD-2026-MODEL-SPEC.md)，执行关口见 [`../docs/REBUILD-2026-EXECUTION-FLOW.md`](../docs/REBUILD-2026-EXECUTION-FLOW.md)。本目录只读取交付原始文件，不以旧版加工表或结果填补缺口。现已有完整的三组仿真成本寻优、分电压条件矩阵和独立结果汇报；它们不是旧版结果，也不代替正式报告的工程审定。

在 `实验/研究/` 下依次运行：

```bash
python -m rebuild_2026.official_annual
python -m rebuild_2026.asset_2025
python -m rebuild_2026.feeder_2025
python -m rebuild_2026.cost_references
python -m rebuild_2026.hourly_source_profile
python -m rebuild_2026.pizhou_mapping_candidates
python -m rebuild_2026.pizhou_mapping_evidence
python -m rebuild_2026.city_mapping_audit
python -m rebuild_2026.pizhou_scenarios
python -m rebuild_2026.pizhou_station_scenarios
python -m rebuild_2026.city_scenarios
python -m rebuild_2026.model_station_inputs
python -m rebuild_2026.baseline_2021
python -m rebuild_2026.annual_forward_scenes
python -m rebuild_2026.pv_source_audit
python -m rebuild_2026.rooftop_area_audit
python -m rebuild_2026.source_load_scan_ceiling
python -m rebuild_2026.reverse_screen_2025
python -m rebuild_2026.transformer_only_screen_2025
python -m rebuild_2026.annual_reverse_proxy
python -m rebuild_2026.transformer_only_path_2021_2025
python -m rebuild_2026.incremental_cost
python -m rebuild_2026.pizhou_existing_ties
python -m rebuild_2026.static_storage_screen_2025
python -m rebuild_2026.marginal_measure_comparison_2025
python -m rebuild_2026.submodel_2025_no_tie
python -m rebuild_2026.annual_no_tie_investment_submodel --reverse-variant night_central
python -m rebuild_2026.annual_no_tie_investment_submodel --reverse-variant night_central --research-ceilings
python -m rebuild_2026.annual_no_tie_cap_scan
python -m rebuild_2026.model_consistency_audit
python -m rebuild_2026.joint_lifecycle_optimizer --scheme rigid
python -m rebuild_2026.joint_lifecycle_scan
python -m rebuild_2026.joint_lifecycle_sensitivity
python -m rebuild_2026.joint_lifecycle_result_matrix
python -m rebuild_2026.matrix_readiness_audit
python -m rebuild_2026.cost_ratio_sweep
python -m rebuild_2026.measure_scope_diagnostic
python -m rebuild_2026.peak_trough_sensitivity
python -m rebuild_2026.replacement_credit_sensitivity
python -m rebuild_2026.tie_transfer_sensitivity
python -m rebuild_2026.cap_frontier_35kv
python -m rebuild_2026.joint_lifecycle_cashflow
python -m rebuild_2026.generate_model_report
python -m pytest -q rebuild_2026/tests
```

2026-09-23 复核：条件矩阵的 12 行只有 3 个独立片区—电压组，组内源荷比、H95 和价格比没有变化。`matrix_readiness_audit.json` 将其判为案例表，尚不满足甲方所需的相对通用推荐矩阵；邳州 35 kV 的五组独立价格系数复算也没有形成新的推荐阈值。详见 `source_audit/建模重构与结果汇报-2026-09-22.md` 末节。最终研究报告继续等待矩阵结果审定。

输入核对与未闭合问题见 [`source_audit/2025-hourly-findings.md`](source_audit/2025-hourly-findings.md)，首轮有效性判断见 [`source_audit/model-validity-review.md`](source_audit/model-validity-review.md)。邳州 56 个有效逐时列已完成站/主变跨源复核，年底新站 2 列无可用于主变编号判别的负荷。市区按时序文件确定 29 个 110 kV 样本站：24 站与 QX-00007 设备表匹配；夹河、茱萸由负责人确认属于市区研究样本，但原设备区县仍保留为不同值；昆仑、杏子山、玉泉有已确认的时序/电压/研究归属，但无可核定 BDZ 或容量，按选定方案分别建立独立仿真设备站，绝不伪称已有真实设备记录。五站补充对应见 [`city_2025_mapping_supplement.csv`](city_2025_mapping_supplement.csv)。房亭/秦洪两份 220 kV 时序确定排除，未核定电压的全零矿大序列也不合并。QX-00007 年度容量以年度表 3701 MVA 为原表基准，设备表的 3714 MVA 只作差异披露；该年度容量与当前 29 站时序样本尚非同一边界，不直接计算正式容载比。联合仿真求解、条件推荐和结果汇报见文末，历史终稿尚未重写。

当前已生成两地 2025 年站级与片区同步静态场景。邳州场景默认使用已复核逐列映射，1 个缺值小时仅线性补值作敏感性；市区 29 站共同缺失 421 小时，以最近前后同星期、同小时均值作规划估算，原始观测和估算分别保存。市区片区观测正向峰值 1307.32 MW、H95 为 11 小时，补值试算未改变两者；片区全年净负荷为正，但 9 座站有站级反送，设备约束仍须看逐站反向场景。场景表不是容量—成本最优解。

`source_audit/model_station_inputs_2025.csv` 已合成 57 个站—电压输入：邳州 28、市区 29。市区 26 座有原设备表容量，共 3263.5 MVA（其中夹河、茱萸的原设备区县与研究归属不同），三座仿真设备站没有原表容量，保留为空；其规划候选容量另在 2021 年起点表给出。该输入表的设备容量只是 2025 年源表快照，不能直接充当 2021 年规划起点，也不能与市区原 QX-00007 年度汇总 3701 MVA 混作同一边界。

`baseline_2021.py` 已按同一规则为 57 站构造**2021 年仿真候选起点**，逐站规格见 `source_audit/baseline_2021_station_candidates.csv`，分层结果见 `baseline_2021_layer_check.csv`。基准为每站两台主变，规格只取对应片区、对应电压的原设备明细出现过的额定值；把站级 2025 正向极值按年度峰值变化比例缩放到 2021 年，取功率因数 0.95，以正向峰值不过双机额定视在容量为初筛，再从离散组合中取容量最小者。邳州 2021 峰值分别锚定年度表 731.77 MW（110 kV）、80.76 MW（35 kV）；市区年度表与 29 站样本边界不同，只借用 2021/2025 增长比例，不把年度绝对峰值强加给样本。三层仿真容量分别为 1014.5、128、2403 MVA，对应同边界容载比 1.386、1.585、1.938。它们既非历史在役容量，也**不是已完成反送、N−1、潮流及导则承载力校核的可实施方案**。

市区三座仿真站基准均为 2×40 MVA；若三站统一改为 2×50 MVA，片区 R=1.987，仍低于 2.0；统一改为 2×63 MVA 时 R=2.050，超出起点上限。逐档结果在 `source_audit/baseline_2021_virtual_city_sensitivity.csv`。2021 年没有可核定的站级光伏出力，故反向约束仍未评估；这些候选值目前只通过正向负荷和容载比初筛，不能直接投入后续成本优化形成正式推荐。

`annual_forward_scenes.py` 另生成 2021—2025 年每层、每站的**同步正向峰值静态代理**，见 `source_audit/annual_forward_layer_scenes_2021_2025.csv` 和 `annual_forward_station_scenes_2021_2025.csv`。2025 年保持样本实际观测峰值（邳州 110/35 kV 为 951.66/147.57 MW，市区 29 站为 1307.315366 MW），不拿年度表峰值覆盖原时序；2021—2024 年借用该 2025 同步时刻的逐站净负荷构成，按年度峰值变化比例统一缩放。邳州目标峰值按年度表定标，市区只用年度比例。历史年份的时刻和站级分布都是情景假设，不能标为当年实测；此正向缩放也**不产生**可信的当年反向峰值或 95% 峰值持续时间。

`pv_source_audit.py` 已固定光伏来源边界：分县逐月表在邳州和 QX-00007 均只有 2023—2025 年完整月份，2021—2022 年为空；原表没有说明数值单位，也没有到站分配，因此历史年度反向代理仅使用同区县、同月份的**无量纲变化比例**。另一张《光伏装机.xlsx》是 2026 年典型时刻表，邳州有 110/35 kV 记录，QX-00007 没有行；不能回填为市区或 2021—2025 年站级光伏容量。《光伏8760小时数据.xlsx》是单个 3408 MW 机组的源场景 `1/1`，只是把 8760 小时映射到 2025 日历，并非 2025 年各站分布式光伏实测。覆盖与元数据见 `source_audit/pv_monthly_source_coverage.csv`、`pv_asset_source_coverage.csv`、`pv_hourly_proxy_metadata.csv`。尤其不能把光伏容量增长比例直接乘到**净负荷**反送峰值上，因为净负荷还包含用电负荷。

`source_load_scan_ceiling.py` 另为**研究性弹性搜索域**作一次独立换算：暂将逐月光伏原表值按 `10 MW/单位` 推断量级，并借单机光伏系数构造非实测的用户负荷代理；用江苏省 2030 年分布式光伏翻番目标作源荷压力情景，以《电网技术》2026 年论文 `2.07` 的**确定性负荷分母**算例上缘和本项目**净负荷分母**差异给出向上取档的覆盖上限：邳州 110/35 kV 各扫至 `4.0`、市区 110 kV 扫至 `3.0`。可复算结果见 `source_audit/source_load_scan_ceiling_research.csv`，文献、面积研究和限制见项目 `参考政策/容载比弹性扫描依据/来源与适用说明.md`。这些档位不是标准限值、技术准入或推荐值，若最优解触顶仍须扩域。

`rooftop_area_audit.py` 对甲方新增 `data/tuomin/补充数据/屋顶数据.xlsx` 做社区/村粒度核验，避免把「农村居民合计」重复计入面积；邳州市 498 个区域为 8939.19 万 m²，其中 496 个镇村与台区页精确对应。鼓楼/云龙/泉山三区合计 4082.36 万 m²，但仅是行政代理，不能直接代表市区 29 站样本。按徐州地铁可用屋顶案例 `0.10 kW/m²`，将可利用比例设为 20%/40%/60% 仅作资源敏感性，详见 `source_audit/rooftop_area_district_audit.csv`、`rooftop_resource_sensitivity.csv`。原表未提供可利用面积或已装屋顶光伏，故目前不改变 4.0/3.0 的研究扫描覆盖上限，也不据此判定电网承载力。

`reverse_screen_2025.py` 把 2021 仿真容量假定原样保留到 2025 年，以实测站级反送极值和宽松的 `β=0.8` 上界定位风险：邳州 35/110 kV 各有 6 站超出；市区 9 站有反送，但没有站超出该上界。随后 `transformer_only_screen_2025.py` 在**不采取转供或储能**的条件下，按本地双主变离散规格同时满足站级正向峰值和上述反向上界，所得容量分别为邳州 35 kV 232 MVA（R=1.572）、邳州 110 kV 1255 MVA（R=1.319）、市区 110 kV 2440 MVA（R=1.866）。逐站方案见 `source_audit/transformer_only_station_screen_2025.csv`。这仅是变压器单措施、站级聚合的宽松筛查值，**不是**与转供/储能比较后的最优解，也不是按导则设备级典型时刻算出的承载力或可实施方案；通过上界并不证明实际运行方式或 N−1 合规。

`annual_reverse_proxy.py` 已给 2021—2024 年构造**站级反向静态代理**，另保留 2025 年观测模板作校准。每站在 2025 年春秋季工作日 10:00—15:00 内选最低净负荷时刻 `N_25`；同月夜间净负荷中位数作白天用电负荷代理 `L_25`，推得光伏出力代理 `G_25=L_25−N_25`。其他年份用 `N_y=a_y L_25−b_y G_25`：`a_y` 取本轮年度正向负荷比例，`b_y` 取分县原表同月/2025 同月比例。2021—2022 年没有原始光伏记录，中心情景用 2023—2024 年同月增幅作几何回推；另以“2021—2022 年维持 2023 年同月水平”作高光伏压力。夜间负荷代理同时做 ±20% 敏感性，所有情景在 2025 模板时刻都还原原观测净负荷。输出见 `source_audit/annual_reverse_station_proxy_2021_2025.csv`、`annual_reverse_layer_summary_2021_2025.csv`。不同站的模板时刻不同，片区摘要不是同步反送峰值；模板时刻也未由逐站光伏出力证实为导则要求的最大出力时刻，历史 H95 不能由它推得。

`transformer_only_path_2021_2025.py` 用上述中心与早期高光伏两套反向代理，叠加逐年正向峰值，检查**不转供、不配储能、逐台主变规格只升不降**的双主变路径。初版仅限制站级总容量不下降，曾出现 11 个单台降档事件，不能据此计价；已改为在排序后的两台主变上分别施加不降档约束。两套情景的片区容量相同：邳州 35 kV 为 `128→166→166→186→234` MVA，邳州 110 kV 为 `1014.5→1093→1093→1104.5→1268` MVA，市区 110 kV 为 `2403→2403→2446→2446→2446` MVA；30 个片区—年—情景结果的 R 均不超过 2.0。逐站设备变化及片区容载比见 `source_audit/transformer_only_path_station_2021_2025.csv`、`transformer_only_path_layer_2021_2025.csv`。这仅证明简化筛查下存在一条主变单措施路径，不是成本最优推荐，也不证明导则设备级可开放容量已通过。

`incremental_cost.py` 已把主变路径逐台升级展开为 `source_audit/transformer_only_incremental_events_2022_2025.csv`，2021 年仿真起点不计新增购置；两种反向情景分别列示，不能相加。按负责人确认的仿真折算口径，优先从原工程投资表中选取**主变替换**而非新增第三台的案例：110 kV 两项静态总投资合计 2486 万元、新购 150 MVA，取 `16.573333333 万元/新购 MVA`；35 kV 四项合计 1548 万元、新购 100 MVA，取 `15.48 万元/新购 MVA`。逐台投资为对应电压系数乘**新购主变额定容量**，不是乘净增容量；各案例单位造价的最小、最大值另作成本敏感性，不能称统计置信区间。来源、工程范围及系数见 `source_audit/transformer_replacement_cost_coefficients.csv`，逐层逐年投资见 `source_audit/transformer_only_capex_layer_2022_2025.csv`。110 kV 两案例分别含 9 回和 1 回新增 10 kV 出线，折算后未剔除这些配套费用，因此是仿真工程造价、不是不含出线的设备裸价，也不是逐站概算；若后续把出线/间隔单列计价，必须消除重计。

`source_audit/cost_parameter_inventory.csv` 还区分了已确认的既有转供零新增投资、新线 44.543 万元/km 规划单价、储能 0.1 MW/0.215 MWh 模块及本地投资/公开招标案例。苏州 27.2 万元/柜是招标最高限价，浏阳 210.456262 万元/10 柜等效规模是不同地区和年份的实际中标价；1—10 柜线性插值只供首轮敏感性，不能当作徐州成交价或外推到更大规模。折现、运维及寿命由调用者显式输入；现金流函数按投运当年投资、次年起运维、窗口内寿命届满时同实价更新，不自动继承历史模型参数。当前已可对**仅主变路径**核算 2022—2025 年投资，但尚未求解转供/储能/主变的措施组合，不能把该成本称为最优成本或推荐容载比。

`pizhou_existing_ties.py` 从原始六线台账和《10kV 案例建模前期准备 V2》的图纸关系表核出三条**跨站既有联络**：墩南↔河炮、墩振↔河东、墩西↔河炮；河东↔河镇为同站联络，不作跨站通道。六线 2025 年受端电流余量按 `√3×10kV×(允许电流−记录最大电流)×0.95` 折算，并与作为参照的 2025 年仅主变路径站级正/反向余量、供端年度最大电流功率代理共同取最小值，得到每个方向的**源端静态上侧筛查**。见 `source_audit/pizhou_six_feeder_receiving_headroom_2025.csv`、`pizhou_existing_cross_station_ties.csv`、`pizhou_existing_tie_direction_screen_2025.csv`。河东线原表最大有功为 0 MW，却记录最大电流 544.57 A，本轮保留冲突并只用电流差算受端余量，绝不把 0 MW 当真实零负荷。V2 的联络常态开合状态未可靠判定；本研究按负责人已确认的“可调整为长期正常转供”作为仿真假设，使用既有联络时新增投资为零。`check_simultaneous_transfers` 可在给定同一场景站级净负荷和容量后，检验多联络的共同供受端馈线占用、站级正反向限额及片区净负荷守恒；不把两条联络共享的河炮线余量重复使用。图纸到实际转供段的负荷、下游载流量及开关运行方式未闭合，当前数值**不是可直接实施的转供容量，也不是联络—主变—储能成本最优解**。

`static_storage_screen_2025.py` 针对同一 57 站输出三套 2025 年容量情景：保留 2021 仿真容量、保留 2024 年仅主变路径容量、采用 2025 年仅主变路径容量，见 `source_audit/static_storage_need_screen_2025.csv`。站级正向缺口为 `max(0, P正峰−0.95S)`，反向缺口为 `max(0, P反峰−0.8×0.95S)`；输出同时保留客户要求的全年 `H95`（达到峰值 95% 的总小时数）和最长连续段 `D95`，仅用**峰值缺口×D95**构造矩形能量情景，再按 0.1 MW/0.215 MWh 的**标称**模块容量向上取整，两方向取较大柜数。该乘积不是实际全年超限电量、也未模拟效率、SOC 恢复或站址，因此不能证明储能可实施或符合导则。保留 2021 容量时，26 站出现缺口、25 站超出 10 柜报价案例规模；保留 2024 容量到 2025 年时，分别为 22 站和 21 站。超出 10 柜时以 10 柜整包重复加余数插值，只是本轮大规模静态**仿真计价假设**，不是徐州报价。2025 年仅主变路径下此筛查无需储能，是该路径按同一峰值/反向上界选容的直接结果；不得据此宣称主变路径全寿命成本最优。下一步需把六线可转供段、离散主变、储能的场景动作及逐年现金流放在同一约束和目标下比较。

`marginal_measure_comparison_2025.py` 从**同一条 2024 年仅主变路径**出发，分别保持该容量并仅新增储能、或继续执行 2025 年仅主变升级，生成 `source_audit/marginal_measure_comparison_2025.csv`。只对比 2025 年新增投资：邳州 35 kV 两方案分别约 6008.41/2662.56 万元，邳州 110 kV 分别约 16633.19/9554.53 万元；市区 110 kV 两方案均无该年新增措施。这个诊断说明在当前**大规模储能包价假设**下，两个邳州单措施储能情景的静态投资均高于主变升级；它未计寿命、运维、既有转供、新线、场景调度与设备级承载，不能据此判定成本最优措施或推荐容载比。

`model_consistency_audit.py` 是进入联合求解前的独立对账关口，读取已生成 CSV，而不是再调用场景生成函数。`source_audit/model_consistency_checks.csv` 当前 151/151 项通过，覆盖站集、2021 双主变起点、2021—2025 同步正向求和与反向代理站集、逐台不降档、站级正反向静态屏查、片区容载比、主变投资事件、储能柜数、单措施对照及受限数值子模型。测试还验证改坏一条站级场景后会报错。通过仅说明这些**仿真输出内部一致**，不证明原数据无误、导则设备级合规或全寿命最优；技术有效性关口和刚性/弹性求解仍待执行。

`guide_device_formula.py` 已按本地 DL/T 2041—2025 扫描件核对第 6.3、8.5 节公式：既有灵活调节资源充电功率在分子内，计划新增规模区间在除以 `τ_max` 后相加；可开放并网与备案容量分别扣减已并网和已备案未并网装机，负值不截零，以保留导则分级判断。该模块目前没有可核定的逐台 `P/P_G/τ_max` 等输入，不能因公式已实现就称已有导则评估结果。

`submodel_2025_no_tie.py` 是**数值寻优内核的受限验证**：固定 2024 年仅主变路径起点，在 2025 年为每站枚举不降档双主变与最多 10 柜储能，以静态正/反向峰值和 D95 矩形代理筛选候选，按片区 `R≤2.0` 用整数规划最小化**2025 年新增投资**。输出 `source_audit/submodel_2025_no_tie_stations.csv`、`submodel_2025_no_tie_layers.csv`。三层解的当年投资分别为邳州 35 kV `2282.97 万元`、邳州 110 kV `8387.03 万元`、市区 110 kV `0 万元`，均不高于同起点仅主变候选；邳州分别选 10 柜、5 柜。这里的“最优”严格限于这个单年、无联络、无新线、无全寿命费用、无设备级导则证明的候选集，**不是**正式刚性方案最优成本或推荐容载比。

`annual_no_tie_investment_submodel.py` 把同一无联络候选集扩展到 2022—2025 年逐年投资现值，允许对已固化的研究性上限做对照；`annual_no_tie_cap_scan.py` 核查成本随上限放宽不应上升，输出 `source_audit/annual_no_tie_cap_scan_night_central.csv`。邳州 35 kV 在此受限模型中从 `R_cap=2.0` 的 `2992.09 万元` 降至 `R_cap=2.4` 的 `2417.32 万元`，上限继续放宽至 `3.0/4.0` 不再变化；邳州 110 kV 和市区 110 kV 的成本没有因放宽而变化。逐年的主变与储能选择见对应输出文件。这些是**站级聚合屏查与 2022—2025 年投资现值**下的子模型最优，不含既有/新建 10 kV 联络、运维、更新、完整全寿命目标或 DL/T 2041—2025 设备级承载力评估，不能当作正式刚性/弹性推荐。

## 联合全寿命求解与结果

`joint_lifecycle_optimizer.py` 从本轮源审计 CSV 构造三组独立 MILP，逐年选择离散双主变替换与 0—10 柜储能；刚性方案上限为 2.0，且仅邳州 110 kV 可在两站六馈线内选择既有/规划联络；弹性方案不含联络。目标把 2022—2025 年措施事件展开为 2022—2041 年投资、固定运维和期内更新并折至 2021 年末。基准参数在 `cost_parameter_inventory.csv`；敏感性在 `joint_lifecycle_sensitivity.csv`。`joint_lifecycle_cashflow.py` 从设备事件独立重建 1204 条现金流，已与优化目标逐组对账。完整设备、联络、逐年和组别结果分别见 `joint_lifecycle_rigid_*.csv`、`joint_lifecycle_elastic_scan_*.csv`、`joint_lifecycle_elastic_cap_scan.csv`。

基准结果为：邳州 35 kV 刚性/最低成本弹性现值分别 3429.33/2779.64 万元，加密扫描后最低成本路径首次进入可行域的上限为 2.31834；实际设备路径 2023 年 R=2.318339、2025 年 R=1.531。邳州 110 kV 刚性含既有联络为 9795.80 万元，弹性无联络为 9887.96 万元，不能把此差额归因于容载比；市区 110 kV 两方案均为 3481.98 万元。两组 110 kV 在研究扫描域内放宽上限未降低无联络成本；基准求解未选新线。两张独立矩阵为 `joint_lifecycle_conditional_matrix_35kv.csv`（邳州 4 年）和 `joint_lifecycle_conditional_matrix_110kv.csv`（邳州、市区各 4 年），不跨电压合并。

完整技术叙述见 [`source_audit/建模重构与结果汇报-2026-09-22.md`](source_audit/建模重构与结果汇报-2026-09-22.md)，可离线打开的结果报告为 [`source_audit/model_result_report.html`](source_audit/model_result_report.html)，规范化报告输入为 `model_result_artifact.json`，由 `generate_model_report.py` 和 Data Analytics 公用封装器生成。HTML 已通过数据结构、来源和自包含封装校验；当前环境无可用 headless-shell，未完成增强阅读器的浏览器视口验收。旧研究终稿未改写。
