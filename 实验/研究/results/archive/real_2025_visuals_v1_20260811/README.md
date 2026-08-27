# real_2025 可视化审查包

本目录由最终运行 `real-2025-contract-v2` 生成，图表只用于人工审查和解释，精确查值仍以 `county_110_matrix.csv`、`county_35_matrix.csv` 为准。

## 文件

- `clr_interval_110kv.*`、`clr_interval_35kv.*`：现状参考 CLR、A/B 后 CLR 和候选/经验范围。
- `feasibility_eac_110kv.*`、`feasibility_eac_35kv.*`：A/B 可行性和 EAC；不可行不绘制伪成本。
- `evidence_quality.*`：证据等级与数据问题数量。
- `recommendation_matrix_110kv.*`、`recommendation_matrix_35kv.*`：甲方转置式指标推荐主表；第一列为指标，首行是当前推荐 R_rec。
- `visual_data.csv`：图表使用的 16 行长表，110/35 kV 不聚合。
- `visual_manifest.json`：输入/输出 SHA-256、运行 ID 和图表契约。

## 口径

CLR 使用同电压等级公用变容量除以干预前正向最大净负荷；C0/A/B 共用固定分母。35 kV 为辅助技术需求矩阵，不宣称唯一离散最优。N-1 和无阻抗网络筛查不进入本图包。

数据行数：16（110 kV 8 行，35 kV 8 行）。
