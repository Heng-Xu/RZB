# 徐州真实数据 v3 输出规范

规范编号：`xuzhou-clr-project-output-v3`  
适用范围：`实验/研究/` 下的 CSV、Markdown、Word、日志、技术附表和 manifest。  
权威契约：`model_contract.yaml`。本文件只规定机器字段和人工呈现，不改变已冻结的业务定义。

## 1. 正式路径代码

正式产物、运行日志、文件名、表题和图题只使用以下路径代码：

| 路径代码 | 中文名称 | 用途 |
| --- | --- | --- |
| `PATH_ACTUAL_2021_2025` | 2021—2025 实际 | 事实对照，不参与最优排名；设备级事实动作未闭合时成本写“未识别”。 |
| `PATH_OPT_CLR_UNBOUNDED` | 不限制容载比优化 | 以 2021 年实际状态为共同基准，使用真实离散候选和全部物理约束，以累计在役 EAC 最小为目标。 |
| `PATH_OPT_CLR_LE_2` | 控制容载比不超过 2.0 优化 | 与不限制路径完全共享输入、候选、成本、物理约束和精度，从 2022 年起逐年施加 `R<=2.0`。 |

`SCHEME_C0`、`SCHEME_A`、`SCHEME_B` 只允许出现在历史归档和迁移清单中，不得进入 v3 正式文件、日志、表题或图题。`EVIDENCE_A/B/C` 是证据等级，不是路径代码。

## 2. 共同口径与成本字段

- 共同基准为 2021 年实际状态；2021 年既有资产是共同沉没成本，不计入增量成本。
- 决策期为 2022—2025 年；所有路径统一按 2025 年价格计价。
- 目标为 2022—2025 年累计在役等效年成本（EAC）最小。
- 同时输出年度新增 CAPEX、年度在役 EAC、累计 CAPEX 和累计在役 EAC。
- 正式中文成本字段统一写“累计年化成本”；机器字段使用 `cumulative_in_service_eac_wanyuan`。
- 必须满足：`cumulative_eac(PATH_OPT_CLR_UNBOUNDED) <= cumulative_eac(PATH_OPT_CLR_LE_2)`。

## 3. 指标字段与物理红线

每条路径按自身干预后的时序计算：

```text
P_net = P_actual + P_charge - P_discharge + P_tie
P_plus = max_t(max(P_net, 0))
P_minus = max_t(max(-P_net, 0))
S = S_2021 + 累计扩容 - 累计减容
R = S / P_plus
```

- 先对同县区、同电压等级的同步时序聚合，再取正向峰值和反向峰值。
- 正式容载比只使用正向 `P_plus`；反向峰值和反向承载力单列。
- 源主变负荷按净负荷解释，不得再次扣减现状光伏。
- 储能充电只能吸收本时段原有反向功率，不得跨过零点制造正向峰值；放电只能服务本地正向负荷，不得形成反送或无约束套利。
- 反向承载力按设备级计算：单台/分列 `beta=0.8`；并列组 `beta=min(0.8,(S_total-S_largest)/S_total)`，不得二次乘 0.8。
- 容载比大于 2.0 本身不自动触发扩容或储能；措施触发原因是正向容量缺口、反向承载缺口或严格路径约束。
- 不设置弃光变量或弃光成本；不具备物理可行性时必须明确标记不可行。

## 4. 正式 CSV/Markdown 精确查值源

正式运行目录为：

```text
results/runs/real-2021-2025-contract-v3/<run_id>/
```

至少包含：

```text
manifest.json
mapping_and_asset_quality.csv
path_year_results.csv
path_action_results.csv
path_cost_breakdown.csv
county_110_recommendation_matrix.csv
county_35_recommendation_matrix.csv
qx00005_path_validation.csv
内部容量网络压力检查.csv
问题与修正台账.md
```

所有派生表至少保留：

```text
source_ref, source_version, transformation, scenario_id,
quality_flag, source_sha256
```

主矩阵至少显示：

- 脱敏片区 ID、证据等级、资产范围；
- 推荐容载比区间和中心推荐值；
- 三条路径的 2025 容载比、累计年化成本；
- 严格约束增量成本；
- 正向/反向缺口及缺口设备数；
- 推荐措施和证据等级。

推荐区间来自不限制路径的成本最小可行结果及经过验证的成本/时长敏感性，不得机械取五个独立年度最优值的最小—最大。

## 5. Word 人工审查层

正式 Word 只使用一种转置式矩阵：第一列为中文指标，后续列为脱敏片区。说明字段放在表前或表后，不进入主表。机器字段、哈希、JSON、候选编号和长备注不得混入甲方主表。

110 kV 输出八县区正式推荐矩阵，35 kV 输出八县区辅助矩阵；两套矩阵分开建模、聚合、计费和出表。QX-00005 三路径逐年轨迹、措施和成本分解放技术附表，不再制作五张正式年度 Word 矩阵。

推荐措施按缺口和路径结果表述，不把 `R<=2.0` 写成已经改变存量资产的事实。35 kV 候选或父级映射未闭合时，主表写技术需求量、成本范围和证据缺口，不输出伪精确唯一最优方案。

## 6. 归档规则

旧 `real_2025`、旧五张年度矩阵、旧 C0/A/B Word 和旧可视化只能放入明确标记为“旧契约、不得正式引用”的归档目录。归档保留证据和哈希，不覆盖源数据，不与 v3 正式运行目录混放。
