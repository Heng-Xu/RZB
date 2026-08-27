# real_2025 自动化运行手册

本文档只说明真实数据闭环的运行、产物和门禁，不替代业务规格，也不是对外正式报告。业务定义以项目根目录 `AGENTS.md`、`model_contract.yaml` 和 `docs/REAL-DATA-MODEL-SPEC.md` 为准。

## 1. 运行环境

- Conda 环境：`xuzhou110kv_clr`；
- 工作目录：项目内 `实验/研究/`；
- Matplotlib 缓存：`MPLCONFIGDIR=/tmp/mplcfg_xuzhou`；
- 正式基准年：2025；
- 默认结果目录：`results/runs/real-2025-contract-v2/`。

## 2. 单命令闭环

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou \
  conda run -n xuzhou110kv_clr \
  python scripts/run_all.py \
  --dataset real_2025 \
  --config model_contract.yaml \
  --skip-gen
```

`--skip-gen` 在真实数据模式下仅为兼容固定验收命令；真实链路不会调用旧合成数据生成器。

如需隔离试运行，可追加：

```bash
--processed-dir /tmp/xuzhou_real_2025_processed \
--output-dir /tmp/xuzhou_real_2025_run
```

## 3. 流水线顺序

1. 只读源包适配并写入 `data/processed/real_2025/`；
2. 交叉核验 QX-00005 的 58 列候选映射，并执行外部审批门禁；
3. 生成设备、站级和县域现状基线；
4. 建立扩容/储能成本库和年化参数敏感性；
5. 构造经验短时、中心、长时三类非概率日内情景；
6. 求解 C0/A/B，回放整数储能的全部经验情景；
7. 生成 110 kV 正式矩阵和 35 kV 辅助矩阵；
8. 执行仅供内部使用的容量网络故障压力筛查；
9. 汇总行动清单、成本分解、质量问题和数据血缘；
10. 执行全部硬断言，只有通过后才写出最终 `manifest.json`。

## 4. 核心产物

- `county_110_matrix.csv`：八县区 110 kV 正式比较矩阵；
- `county_35_matrix.csv`：八县区 35 kV 辅助矩阵；
- `actions_C0.csv`、`actions_A.csv`、`actions_B.csv`：分方案站级行动；
- `cost_breakdown.csv`：扩容、储能和合计 CAPEX/EAC；
- `quality_flags.csv`：适配、时序和经验情景质量标记；
- `real_plan_dispatch_playback.csv.gz`：所选 A/B 方案逐站逐情景回放；
- `internal_capacity_network_summary.csv`：内部容量网络筛查摘要；
- `validation_report.json`：发布硬断言；
- `manifest.json`：环境、输入指纹和全部输出 SHA-256。

## 4.1 可视化审查包

在正式矩阵通过验收后，使用同一次运行生成人工审查图包：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou \
  conda run -n xuzhou110kv_clr \
  python scripts/plot_real_2025_visuals.py \
  --run-dir results/runs/real-2025-contract-v2 \
  --output-dir results/real_2025_visuals
```

`results/real_2025_visuals/` 必须包含 110/35 kV 分开的甲方“转置式指标推荐主表”（第一列指标、后续列脱敏片区/高压分区、首行当前推荐 R_rec）、CLR 区间图、A/B 可行性与 EAC 图、证据质量图、图表长表、README 和 `visual_manifest.json`。矩阵仍是精确查值主源；主表必须使用当前 2025 成本最小可行方案，不得写 `R(2030)`；图表必须显示固定正向分母、证据等级和不可行原因，N-1 内部筛查不得混入推荐图。

## 5. 当前自动降级规则

- QX-00005 时序映射没有源方审批时，`grade_a_ready=false`，不得输出 A 级 8760 结论；
- 35 kV 无闭合站级离散候选时，只输出技术需求和本地案例成本区间，不给唯一最优；
- 父级映射或容量口径未闭合时，禁止跨层成本相加；
- 网络节点映射或阻抗缺失时，只做内部容量压力筛查，不写精确潮流结论；
- 任一方案物理不可行时，保留 `infeasible` 和具体原因，不返回伪最优成本。
