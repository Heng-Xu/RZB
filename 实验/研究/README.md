# 徐州 110/35 kV 容载比真实数据 v3

状态：v3 建模与研究报告主体已完成；后续以最新 Claude 接续记录和项目 memory 为进度依据，继续依托建模结果完善研究报告。定版日期：2026-08-27。

## 权威入口

在 `实验/研究/` 工作前，先读取项目根目录 `claude_session_1.txt`。负责人已确认该记录在进度、完成状态、遗留项和下一步方面优先于较旧的项目 memory。随后依次读取：

1. 项目根目录 `AGENTS.md`；
2. `memory/INDEX.md` 与 `memory/current.md`；
3. `docs/IMPLEMENTATION-PLAN-REAL-2021-2025-V3.md`；
4. `model_contract.yaml`；
5. `docs/REAL-DATA-MODEL-SPEC.md`；
6. `../../skills/xuzhou-real-model/SKILL.md`；
7. `data/tuomin/电网建模数据_Agent整合版_V1.2/README_Agent_建模数据引用与使用说明_V1.2.md`；
8. 涉及储能成本时读取项目根目录 `参考政策/储能成本依据/来源与适用说明.md`。

## v3 研究口径

- 共同基准为 2021 年实际状态，决策期为 2022—2025 年，统一按 2025 年价格计价；
- 正式路径为 `PATH_ACTUAL_2021_2025`、`PATH_OPT_CLR_UNBOUNDED`、`PATH_OPT_CLR_LE_2`；
- 目标为 2022—2025 年累计在役 EAC 最小，同时输出年度 CAPEX、年度在役 EAC、累计 CAPEX 和累计在役 EAC；
- 110 kV 与 35 kV 分开建模和出表；主体不做全县 10 kV 联络优化；
- 正式容载比使用每条路径自身的同步正向最大净负荷，反向峰值和反向承载力单列；
- 源净负荷不再次扣减现状光伏；主体模型不设置弃光变量或弃光成本。

## 运行

契约测试：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr pytest -q tests/test_model_contract_v3.py
```

全量测试：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh
```

真实 v3 端到端：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr python scripts/run_all.py --dataset real_2021_2025 --config model_contract.yaml --skip-gen
```

旧 `real_2025`、synthetic M1、旧年度矩阵和旧 Word 只能用于迁移回归或归档，不能作为 v3 最终结果。

最新方法、自查和局部案例边界见 `分析/2026-08-26-建模思路与真实方法总结_甲方汇报辅助.md`、`分析/2026-08-26-10kV联络案例重分析_收资定稿口径.md`。正式数值优先从 `results/runs/real-2021-2025-contract-v3/` 下的 CSV/Markdown、manifest 和问题台账读取。
