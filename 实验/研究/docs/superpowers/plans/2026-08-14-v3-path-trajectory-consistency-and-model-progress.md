# v3 最终路径轨迹一致性修复与建模进度底稿实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 让 `path_year_results.csv` 完整回放 2025 年最终最优动作路径，并在验证通过后生成可直接用于研究报告写作的详细建模进度底稿。

**架构：** 动态规划继续负责搜索并保留最终状态；新增内部回放逻辑，根据最终状态的动作列表逐年重建容量、储能、CLR 和成本轨迹。生产流水线重新生成 CSV、Word 与 manifest，报告仅引用修复后的正式产物。

**技术栈：** Python 3、pandas、pytest、Conda `xuzhou110kv_clr`、Markdown、python-docx。

---

## 文件职责

- 修改 `tests/test_v3_planner.py`：增加最终路径不同于滚动前缀时的回归测试。
- 修改 `src/v3_planner.py`：从最终最优状态逐年回放正式轨迹。
- 修改 `tests/test_v3_e2e.py`：增加最终动作、逐年轨迹和成本分解的端到端一致性断言。
- 重新生成 `results/runs/real-2021-2025-contract-v3/real_2021_2025-v3/`：更新正式 CSV、Word 和 manifest。
- 创建 `研究报告/建模进度/当前建模进度与阶段成果总结_v3.md`：汇总当前方法、进度、结果、验证、限制与后续写作映射。

项目根目录没有可用 Git 仓库，不能执行 worktree 或 commit。每个任务以目标测试输出、正式运行日志和 manifest SHA-256 作为审计证据。

### 任务 1：建立最终路径逐年回放的失败测试

**文件：**

- 修改：`tests/test_v3_planner.py`

- [ ] **步骤 1：加入最小失败测试**

```python
def test_year_rows_replay_final_path_instead_of_rolling_prefix_optima() -> None:
    annual = pd.DataFrame(
        {
            "year": [2022, 2023, 2024, 2025],
            "region_id": ["QX-00005"] * 4,
            "voltage_kv": [110] * 4,
            "capacity_mva": [100.0] * 4,
            "positive_peak_mw": [45.0, 40.0, 40.0, 40.0],
            "reverse_peak_mw": [0.0] * 4,
            "reverse_beta": [0.8] * 4,
        }
    )
    candidates = pd.DataFrame(
        [
            {
                "candidate_id": "RETIRE-SMALL",
                "candidate_group": "RETIRE-GROUP",
                "region_id": "QX-00005",
                "voltage_kv": 110,
                "candidate_type": "retirement",
                "delta_capacity_mva": -10.0,
                "capex_base_wanyuan": 10.0,
                "eac_base_wanyuan_per_year": 1.0,
                "cost_status": "cost_center_and_range_available",
                "source_ref": "synthetic-test-source",
            },
            {
                "candidate_id": "RETIRE-LARGE",
                "candidate_group": "RETIRE-GROUP",
                "region_id": "QX-00005",
                "voltage_kv": 110,
                "candidate_type": "retirement",
                "delta_capacity_mva": -20.0,
                "capex_base_wanyuan": 20.0,
                "eac_base_wanyuan_per_year": 2.0,
                "cost_status": "cost_center_and_range_available",
                "source_ref": "synthetic-test-source",
            },
        ]
    )

    result = optimize_joint_paths(annual, candidates)
    strict = result["path_year_results"].query(
        "path_id == 'PATH_OPT_CLR_LE_2'"
    ).sort_values("year")
    actions = result["path_action_results"].query(
        "path_id == 'PATH_OPT_CLR_LE_2'"
    )
    cost = result["path_cost_breakdown"].query(
        "path_id == 'PATH_OPT_CLR_LE_2'"
    ).iloc[0]

    assert actions["candidate_id"].tolist() == ["RETIRE-LARGE"]
    assert actions["year"].tolist() == [2022]
    assert strict["installed_capacity_mva"].tolist() == pytest.approx([80.0] * 4)
    assert strict["annual_in_service_eac_wanyuan"].tolist() == pytest.approx([2.0] * 4)
    assert strict["cumulative_in_service_eac_wanyuan"].tolist() == pytest.approx(
        [2.0, 4.0, 6.0, 8.0]
    )
    assert strict.iloc[-1]["cumulative_in_service_eac_wanyuan"] == pytest.approx(
        cost["cumulative_in_service_eac_wanyuan"]
    )
```

- [ ] **步骤 2：运行测试并确认预期红灯**

运行：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr pytest -q tests/test_v3_planner.py::test_year_rows_replay_final_path_instead_of_rolling_prefix_optima
```

预期：测试失败，首个差异为 2022 年 `installed_capacity_mva` 得到 `90.0`、期望 `80.0`，证明当前写出的是滚动前缀最优。

### 任务 2：按最终状态回放逐年轨迹

**文件：**

- 修改：`src/v3_planner.py`
- 测试：`tests/test_v3_planner.py`

- [ ] **步骤 1：新增内部回放函数**

在 `_append_candidate_actions` 后新增 `_replay_final_path_year_rows`。函数输入最终 `_State`、年度输入、候选、路径参数和片区键；按动作投运年份逐年重建候选掩码与储能柜数，调用 `_evaluate_state`，并从同一动作列表计算四类成本字段。

- [ ] **步骤 2：替换可行组的滚动前缀输出**

在组内四年搜索结束且 `states` 非空时选定一次 `final_state`，使用回放函数生成四条正式年度记录；动作表和成本表也使用同一个 `final_state`。最终不可行组继续保留当前显式不可行记录。

- [ ] **步骤 3：运行目标测试验证绿灯**

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr pytest -q tests/test_v3_planner.py tests/test_real_planner.py
```

预期：全部通过，新增测试中 2022—2025 容量均为 `80.0 MVA`，累计 EAC 为 `2、4、6、8 万元`。

### 任务 3：增加真实端到端跨表一致性门禁

**文件：**

- 修改：`tests/test_v3_e2e.py`

- [ ] **步骤 1：读取动作表和成本表**

在端到端测试中读取 `path_action_results.csv` 与 `path_cost_breakdown.csv`，对最终状态为 `feasible` 的两条优化路径逐组复算每年容量、储能柜数、年度 CAPEX、年度在役 EAC 和累计在役 EAC。

- [ ] **步骤 2：断言逐年表与最终动作表一致**

使用实际路径同年官方容量作为动作前基础容量；所有数值误差上限为 `1e-6`。额外断言每个最终可行组的 2025 年累计 EAC 等于成本分解表。

- [ ] **步骤 3：运行端到端目标测试**

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr pytest -q tests/test_v3_e2e.py
```

预期：通过且不再出现 32 条严格路径不一致记录。

### 任务 4：重新生成并验证正式生产产物

**文件：**

- 更新：`results/runs/real-2021-2025-contract-v3/real_2021_2025-v3/path_year_results.csv`
- 更新：`results/runs/real-2021-2025-contract-v3/real_2021_2025-v3/qx00005_path_validation.csv`
- 更新：同目录矩阵、Word 和 `manifest.json`

- [ ] **步骤 1：运行 v3 契约测试**

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr pytest -q tests/test_model_contract_v3.py
```

- [ ] **步骤 2：运行全量测试**

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh
```

- [ ] **步骤 3：运行真实端到端生产入口**

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr python scripts/run_all.py --dataset real_2021_2025 --config model_contract.yaml --skip-gen
```

- [ ] **步骤 4：复核正式产物**

验证 110 kV 严格路径四年均 `R<=2.0`、路径成本包含关系、110/35 kV 分离、逐年轨迹与动作/成本零差异、两套 Word 结构和 manifest 哈希。

### 任务 5：撰写详细建模进度底稿

**文件：**

- 创建：`研究报告/建模进度/当前建模进度与阶段成果总结_v3.md`

- [ ] **步骤 1：写技术摘要和阶段 0—7 进度表**

明确当前已完成内容、生产结果、修复后的验证状态和仍受证据限制的事项。

- [ ] **步骤 2：写数据、指标、约束、候选和联合优化方法**

引用 v3 计划、机器契约、模型规格、数据说明和储能成本说明；不引用旧 `real_2025` 作为最终依据。

- [ ] **步骤 3：写 110/35 kV 结果和 QX-00005 技术轨迹**

所有精确数字从修复后的正式 CSV 提取；110 kV 是正式推荐矩阵，35 kV 是辅助矩阵且明确严格路径不可行边界。

- [ ] **步骤 4：写数据问题、证据等级和报告复用建议**

链接 `实验/研究/分析/v3真实数据问题补充说明_供甲方汇报.md`，区分已解决映射、保留质量例外、实际成本未识别和后续本地数据需求。

- [ ] **步骤 5：校验文档**

检查路径代码、年份、单位、成本字段、表格行数、文件链接和“旧结果不得正式引用”提示；确认无图片依赖。

### 任务 6：最终审查与交付

**文件：**

- 审查：修复后的正式运行目录
- 审查：`研究报告/建模进度/当前建模进度与阶段成果总结_v3.md`

- [ ] **步骤 1：执行完成声明前验证**

调用 verification-before-completion 流程，记录全量测试、真实端到端、跨表回放、Word 和 manifest 检查结果。

- [ ] **步骤 2：记录无 Git 环境说明**

确认根目录 `.git` 不可用，不虚构 commit；交付时列出修改文件和最终验证证据。
