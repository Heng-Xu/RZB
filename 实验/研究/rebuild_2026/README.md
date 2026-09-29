# 110 kV 区县静态规划模型

本轮现行研究案例为**市区与邳州 2021 年共同反事实起点、2022—2025 年逐年优化**。结果及适用边界见[方案说明](../../../docs/2026-09-29-两区县可比方案与导则分档修订.md)。`reserve_policy_v4`、`two_districts_*`、`regional_revision_*` 等脚本及输出记录历史试算，不作为本轮推荐方案入口；其中部分旧模块仍提供数据读取、成本函数和 MILP 基础类，不能按文件名批量删除。

在 `实验/研究/` 下复现：

```bash
python -m rebuild_2026.two_district_ordered_guide_run
python -m rebuild_2026.two_district_ordered_cost_sensitivity
python -m rebuild_2026.two_district_ordered_result_audit
```

当前主入口调用 `regional_static_milp_v2.py`，输入为 `source_audit/` 已加工文件和 `data/tuomin/` 原表；独立约束成本核对见 `regional_static_milp_v2_audit.py`，原表单元格核对见 `two_district_source_audit.py`。结果只取 `outputs/ordered_guide_*`、`outputs/two_district_guide_growth_classification.csv`。新线、储能与主变造价来源见 `研究报告/数据来源/2026-09-28_10kV线路与成本依据/`。

`outputs/` 中旧试算已打包至 `历史归档/区域静态建模试算输出-2026-09-29.tar.gz`；早期区域来源诊断与未跟踪的诊断脚本分别存入同目录的 `区域静态建模来源诊断-2026-09-29.tar.gz`、`区域静态建模历史脚本-2026-09-29.zip`。各归档的同名 JSON 保存清单与 SHA-256。早期 v2/v3 输出另见 `历史归档/模型诊断-2026-09-26.zip`。历史文档中的原输出路径需要解包后才能复查。源数据、已加工输入和被现行模型调用的脚本保留在原路径。
