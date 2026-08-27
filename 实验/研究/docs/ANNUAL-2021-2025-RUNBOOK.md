# 徐州 2021—2025 真实数据 v3 运行手册

## 1. 固定环境与入口

所有相对命令均在 `实验/研究/` 目录执行，并使用 Conda 环境 `xuzhou110kv_clr`。Matplotlib 缓存固定为 `/tmp/mplcfg_xuzhou`。

契约测试：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr pytest -q tests/test_model_contract_v3.py
```

全量测试：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh
```

真实数据 v3 端到端：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr python scripts/run_all.py --dataset real_2021_2025 --config model_contract.yaml --skip-gen
```

正式运行目录为 `results/runs/real-2021-2025-contract-v3/<run_id>/`。运行 ID、契约快照、输入 SHA-256、求解状态、质量台账和输出 SHA-256 必须同时落盘。

## 2. 运行顺序

1. 读取 v3 契约并校验 2021 共同基准、2022—2025 决策期、2025 价格年和三条路径。
2. 读取源文件但不修改 `data/tuomin/`；生成 `data/processed/real_2021_2025/` 标准化数据。
3. 生成 2022—2026 跨年列映射审查、项目负责人审批表和年度资产白名单。
4. 按年度运行白名单判断逐时门禁。2025 QX-00005 110 kV 只要求 20 座站、40 台运行主变；BDZ-00056 年末新增两台不阻塞其余设备。
5. 隔离 2024 年 `-7319`、`-6858` 和 `16630 MW` 三个异常值，保留原值和质量标记。
6. 先计算路径自身同步正向/反向峰值、正式容载比和设备级缺口，再进入动作和优化层。
7. 用同一候选、物理约束、成本库和精度联合求解两条优化路径；严格路径从 2022 年起逐年施加 `R<=2.0`。
8. 分开生成 110 kV、35 kV 矩阵和技术附表；局部 10 kV 案例默认关闭、分别比较。
9. 生成 Word 人工审查层、问题台账、契约快照和 manifest。

## 3. 门禁与证据等级

- `EVIDENCE_A`：年度运行白名单内全部设备已审批，逐时质量合格，完整时序回放通过。
- `EVIDENCE_B`：真实静态数据、官方县峰锚点和经验短时/中心/长时情景；不得使用 P50/P90 表述。
- `EVIDENCE_C`：资产范围、映射、父级关系、光伏口径或候选成本未闭合。

门禁按年度白名单判定，不要求年末新增且未纳入运行口径的设备通过正式逐时资格。实际路径设备级毛动作未闭合时，成本写“未识别”，不能写 0。

## 4. 结果审查

运行结束后不能只看退出码。必须检查：

- 求解状态不是空值，所有不可行对象都有原因；
- 每年资产范围、容量与官方锚点的差额可追溯；
- 严格路径 2022、2023、2024、2025 年逐年 `R<=2.0`；
- 不限制路径累计年化成本不高于严格路径；
- 110 kV 与 35 kV 未混算，父级映射不完整时未做联合枚举；
- 无弃光变量、伪成本、伪容载比、未标记插补和随机馈线光伏事实化；
- 两套矩阵、Word、技术附表、问题台账和 manifest 齐全，所有输出哈希已登记。

## 5. 旧入口

旧 `--dataset real_2025`、synthetic M1、`run_annual_model.py` 和旧年度矩阵只用于迁移回归或归档，不能证明 v3 模型正确，也不能作为正式推荐结果。
