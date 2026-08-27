# 徐州 2021—2025 真实数据 v3 实现计划

> **面向 AI 代理的工作者：** 本计划直接执行已批准的 v3 方案；每个行为变更必须先写失败测试、确认失败原因，再实现最小代码并回归验证。当前项目根目录不是可用 Git 仓库，不能虚构提交记录。

**目标：** 将 `实验/研究/` 从 v2 单年 C0/A/B 脚手架迁移为以 2021 年实际状态为共同基准、覆盖 2022—2025 年的三路径真实数据模型，并完成映射、联合优化、矩阵、Word 与全流程验证。

**架构：** 先以 YAML 契约和 v3 测试锁定唯一业务定义，再建立跨年映射与年度资产门禁；指标层、动作/成本层和多年度路径层通过可追溯标准化表连接。110 kV 与 35 kV 分层运行，正式输出由 CSV/Markdown 作为查值源、Word 作为人工审查层。

**技术栈：** Python 3、PyYAML、pandas、pytest、现有 MILP/逐时求解代码、python-docx（如环境已提供）；所有命令使用 Conda 环境 `xuzhou110kv_clr`，Matplotlib 使用 `/tmp/mplcfg_xuzhou`。

---

### 阶段 0：机器契约迁移

**文件：**
- 修改：`model_contract.yaml`、`docs/REAL-DATA-MODEL-SPEC.md`、`docs/PROJECT-OUTPUT-CONVENTIONS.md`、`docs/ANNUAL-2021-2025-RUNBOOK.md`、`skills/xuzhou-real-model/SKILL.md`
- 修改/新增测试：`tests/test_model_contract_v3.py` 与相关旧契约测试迁移标记

- [x] 先运行 `pytest -q tests/test_model_contract_v3.py`，记录 v2 字段导致的 5 个失败。
- [x] 将契约更新为 `3.0.0`，定义 2021 基准、2022—2025 决策期、三条正式路径、累计在役 EAC、逐路径 CLR、年度资产白名单和两个独立 10 kV 接口。
- [x] 把旧固定分母、`SCHEME_C0/A/B`、`real_2025` 和五张正式年度矩阵移入历史说明，不能保留为正式字段。
- [x] 逐项运行契约测试并确认每次绿灯均由期望字段实现，不放宽断言。
- [x] 运行旧契约相关测试，生成迁移清单；保留仍有效的物理断言并标记旧业务测试。

### 阶段 1：跨年映射与年度资产

**文件：**
- 创建或修改：`src/timeseries_mapping.py`、`src/annual_asset_scope.py`、`scripts/approve_timeseries_mapping.py`
- 测试：`tests/test_timeseries_mapping.py`、新增年度门禁测试
- 产物：`data/processed/real_2021_2025/` 下映射、白名单、对账、行动台账、质量问题和 `manifest.json`

- [x] 为 2022—2026 58 列保留源表头、原始列号、候选目标、审批状态、候选哈希和源 SHA-256。
- [x] 以项目负责人为审批主体；第 11/12/27/28 列保留双字段；2025 QX-00005 110 kV 白名单只要求 40 台，排除 BDZ-00056 年末新增两台。
- [x] 隔离 2024 三个异常值，保留原值、时间、列号和质量标记；建立年度资产容量与官方锚点对账。
- [x] 先运行失败门禁测试，再实现审批读取、哈希核验、年度白名单和正式逐时门禁。

### 阶段 2：路径自身指标与物理缺口

**文件：**
- 修改/创建：`src/real_metrics.py`、`src/real_pipeline.py` 或拆分出的指标模块
- 测试：`tests/test_real_metrics.py`、新增 v3 CLR/反向红线测试

- [x] 测试同一年度不同路径必须分别计算 `P_plus`、`P_minus` 和 `R`；正向分母只取同步聚合后的正向峰值。
- [x] 测试反向充电不能跨零、放电不能反送，源净负荷不能二次扣光伏，并列 beta 不能二次乘 0.8。
- [x] 输出设备级正向容量缺口、反向承载缺口、缺口设备数、触发约束和县区同步峰值。

### 阶段 3：真实离散动作与成本

**文件：**
- 修改/创建：`src/real_costs.py`、候选/动作模块、成本数据标准化脚本
- 测试：`tests/test_real_costs.py` 与新增离散候选、储能 SOC、成本血缘测试

- [x] 读取 SRC03/SRC10 真实扩容候选；减容只允许整台退役、已识别替换或审核组合，不生成连续容量。
- [x] 建立 100 kW/215 kWh 整数柜、SOC、效率、日循环和禁止套利规则；使用已批准的分段储能成本公式和 2025 年价格。
- [x] 每个候选保存 `source_ref`、价格性质、工程范围、`source_sha256`、审批状态和 EAC；实际路径设备级动作未闭合时输出“未识别”。

### 阶段 4：多年度联合优化

**文件：**
- 修改/创建：`src/milp_planner.py`、`src/annual_modeling.py`、`src/real_pipeline.py`
- 测试：`tests/test_real_planner.py`、`tests/test_annual_modeling.py` 与新增三路径约束测试

- [x] 先写失败测试证明 2022 投运动作必须持续在役、目标是 2022—2025 累计在役 EAC，而非逐年贪心或单次 CAPEX。
- [x] 实现两条优化路径共享候选、约束、成本和精度；严格路径从 2022 年起逐年施加 `R<=2.0`。
- [x] 输出 `path_year_results`、`path_action_results`、`path_cost_breakdown`，并验证严格路径逐年约束及不限制路径成本包含关系。

### 阶段 5：电压分层与局部案例接口

**文件：**
- 修改/创建：分层模型、网络压力检查、局部案例解析模块和 `scripts/run_all.py`
- 测试：`tests/test_real_e2e.py`、网络/跨电压/局部案例新增测试

- [x] 110 kV 与 35 kV 分开聚合、求解、计费和输出；父级映射与候选不完整时不做联合枚举。
- [x] 实现 `--existing-tie-case-options` 与 `--new-tie-line-case-options`，两个入口独立审批、独立失败、默认分别比较。
- [x] 用功率守恒、兼容组、依赖、反向功率和成本去重测试接口。

### 阶段 6：正式产物

**文件：**
- 修改/创建：矩阵、Word、manifest 和归档脚本
- 产物：`results/runs/real-2021-2025-contract-v3/<run_id>/`

- [x] 生成 `county_110_recommendation_matrix.csv` 和 `county_35_recommendation_matrix.csv`，主表采用转置式指标行与脱敏片区列。
- [x] 生成 QX-00005 三路径逐年技术附表、措施清单、成本分解、容量网络压力检查、问题台账、契约快照和输入/输出哈希。
- [x] 使用 Word 作为人工审查层；旧矩阵和旧可视化归档并明确“旧契约、不得正式引用”。

### 阶段 7：全流程验证

**命令：**
- `env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr pytest -q tests/test_model_contract_v3.py`
- `env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh`
- `env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr python scripts/run_all.py --dataset real_2021_2025 --config model_contract.yaml --skip-gen`

- [x] 阅读完整输出并核查求解状态、空值、映射审批、年度容量守恒、逐年 `R<=2.0`、成本包含关系、110/35 kV 分离、无弃光和哈希。
- [x] 只有契约测试、全量测试、质量断言、真实端到端和正式产物清单全部满足时，才声明 v3 完成。

---

## 计划自检

- 三路径、共同基准、价格年、目标函数和严格约束均由阶段 0 锁定，后续阶段只实现不重新定义。
- 阶段 1 覆盖源数据血缘、跨年映射、审批、白名单、异常和实际路径成本前置条件。
- 阶段 2—5 覆盖物理指标、离散动作、联合优化、电压分层和局部案例边界。
- 阶段 6—7 覆盖所有指定正式文件、归档、验证和完成门槛。
