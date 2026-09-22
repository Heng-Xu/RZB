# 2026 年独立重构管线

模型口径以 [`../docs/REBUILD-2026-MODEL-SPEC.md`](../docs/REBUILD-2026-MODEL-SPEC.md) 为准。本目录只读取交付原始文件，不以旧版加工表或结果填补缺口。所有当前输出仍是输入核对或候选试算，不是正式推荐值。

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
python -m pytest -q rebuild_2026/tests
```

输入核对与未闭合问题见 [`source_audit/2025-hourly-findings.md`](source_audit/2025-hourly-findings.md)。邳州 56 个有效逐时列已完成站/主变跨源复核，年底新站 2 列无可用于主变编号判别的负荷；市区只匹配 24/30 座在役 110 kV 站，另有 632 MVA 资产缺可核定时序。市区年度容量还有 13 MVA 未解释差额。因此两地统一成本优化、正式容载比推荐和报告重写尚未开始。
