# RZB v3.2 新会话接续提示词

更新时间：2026-09-01

```text
继续接管本地 RZB 电科院咨询项目，全程在 model-v3.2-autonomous-review 分支工作。不要重新设计模型，也不要重新询问是否确认既有 v3.2 方案。

开始时按以下顺序建立事实基线：
1. git fetch、git status、当前分支、git log 和远端最新 HEAD；
2. GitHub Actions 最新状态及 head_sha；
3. AGENTS.md；
4. 实验/研究/model_contract.yaml；
5. 实验/研究/model_contract_v3_2_overlay.yaml；
6. src/v32_contract.py 解析的 resolved contract；
7. data/processed/real_2021_2025/manifest.json 与 timeseries_mapping_approval.csv；
8. results/runs/real-2021-2025-v32-frozen/ 的 baseline、frontier、sensitivity、formal matrices 和 manifest；
9. 当前报告及生成/审查脚本；
10. 最后读取 memory/current.md。claude_session_1.txt、memory/archive 和旧 session 只作 HISTORICAL / SUPERSEDED 历史追溯。

当前 contract=3.2.0 frozen。正式主模型固定为“2021实际在役资产共同起点 + 存量容量豁免 + Rcap只约束110 kV规划期新增容量”。两方案均可行时可以直接比较累计年化成本；弹性方案可行域包含刚性方案可行域。物理 CLR 与 Rcap 分离，物理 CLR 可以因既有存量而高于 Rcap。2×P2021 只作二级标准化敏感性基准；主模型不为满足 Rcap 生成退役候选。

正式结果目录：实验/研究/results/runs/real-2021-2025-v32-frozen/。

接手时先执行 prompt.md 和 memory/current.md 登记的真实遗留项，按失败测试先行完成修复、复跑、冻结比对、报告一致性审查、提交推送和最终 HEAD Actions 验证。旧 SCHEME_C0/A/B、固定干预前分母、旧 real_2025、不同规划起点、成本不可比、EENS=0 和弃光=0 均不得回到正式成果。
```
