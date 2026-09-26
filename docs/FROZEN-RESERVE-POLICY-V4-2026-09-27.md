# reserve_policy_v4 与年度推荐矩阵冻结说明

更新：2026-09-27。以用户认可的 v4 方案及数据为研究报告依据，增加年度指标参数、相关性和独立成本敏感性。

## 结果入口

- 基础方案：`实验/研究/docs/FINAL-POLICY-RECOMMENDATION-2026-09-24.md`。
- 矩阵说明：`实验/研究/rebuild_2026/source_audit/capacity_release_simulation/reserve_policy_v4/recommendation_matrix/推荐矩阵成果说明.md`。
- 中文Excel：同目录 `年度指标与推荐容载比矩阵.xlsx`。
- 基础矩阵：同目录 `annual_indicator_recommendation.csv`（12行）。
- 独立价格敏感性：同目录 `cost_sensitivity/`（4个情景、8路径、16行年度推荐）。
- 原始来源：`实验/研究/data/tuomin/`；当前输入及来源证据保留在 `rebuild_2026/source_audit/`。

## 原流程与超时修正

原流程先分配甲方2021区域容量，再从已审计的年度净峰、站级场景、2025 D95模板和成本来源生成六条路径。每条路径依次最小化费用、在同费用约束下最大化容量裕度、最后最小化不必要转供。

之前误用默认Python环境（SciPy 1.13.1），容量排序步骤在120和600秒超时。专用环境 `xuzhou110kv_clr`（Python3.13、SciPy1.18.0）按原120秒设置完整重算成功，六路径成本、12行年度容量/容载比/储能/转供及年度费用均与原结果一致。两份刚性逐站表存在等价分配；原v4明细保留，不把逐站字节一致作为唯一复现判据。证据见 `reserve_policy_v4/reproducibility_audit.json` 及 `reproducibility_evidence/`。

新增可选 highspy 后端，用上一阶段可行解启动下一阶段，保持相同矩阵、费用容差和最优间隙要求。未改变主成本目标和物理约束。价格敏感性使用该后端。只有取得最优状态才输出成功结果；超时不当作无解。

## 运行环境与复现

使用专用环境；本次实际依赖记录在 `实验/研究/rebuild_2026/requirements-frozen-v4.txt`。不要用默认Python环境替代。先核验冻结哈希，再按需完整重算；重算目录应独立于原版逐站明细。

```bash
conda activate xuzhou110kv_clr
cd 实验/研究
python -m rebuild_2026.verify_frozen_v4
python -m rebuild_2026.simulation_reserve_policy_audit
python -m rebuild_2026.annual_recommendation_matrix
python -m rebuild_2026.annual_recommendation_audit
XUZHOU_MILP_BACKEND=highspy python -m rebuild_2026.annual_cost_sensitivity
python -m rebuild_2026.annual_cost_sensitivity_audit
python -m rebuild_2026.finalize_recommendation_artifacts
```

如要独立重求基础方案，通过 `simulation_reserve_policy.run(output_dir=独立目录)` 指定输出，再调用 `simulation_reserve_policy_audit.audit(独立目录)`。相同最优费用及区域年度结果可能对应不同逐站分配。

## 假设和适用边界

源荷指标为非同时站级光伏出力/毛负荷代理比；正向分母采用已认可年度净峰，市区保持29站边界；反向极值为站级量；历史D95沿用2025模板。净峰CAGR是派生指标。统计相关性为12行/单元内4行的描述，不能作为独立随机样本的因果结论。

刚性容载比≤2、增配预算30%/3%/1%，弹性上界3.2，停运恢复比例60%/60%/45%均按现行研究情景。容量退出不计拆改与残值，存量沉没投资不另加差异性运维费。推荐是完整四年路径的成本选择，跨区域推广须匹配初始资产、站级负荷和转供条件；案例范围不是任意参数组合都可行的区间。

## 文件整理

增长诊断及v2/v3旧结果共86文件归档为 `历史归档/模型诊断-2026-09-26.zip`；清单 `docs/CLEANUP-2026-09-26.json`。保留当前输入生成脚本、原始数据和导则/价格证据。名称含planning的部分文件仍是当前输入，未按前缀整批删除。

冻结清单为 `docs/FREEZE-MANIFEST-2026-09-27.json`；质量汇总为 `docs/VALIDATION-RESOLVED-2026-09-27.json`。

## 最终验证结果

72项测试全部通过（4条原始Excel缺默认样式提示不影响数值读取）。基础六路径完整复现、12行年度参数独立审计和8条价格情景路径2731项独立检查均PASS；中文工作簿7张表已核对行数。三条过期测试断言按已认可的年度峰校准及线路经济性修正。质量详情见 `VALIDATION-RESOLVED-2026-09-27.json`。
