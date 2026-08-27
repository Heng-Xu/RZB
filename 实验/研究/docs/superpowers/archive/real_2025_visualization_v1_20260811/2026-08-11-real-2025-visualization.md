# real_2025 可视化实现计划

> **面向 AI 代理的工作者：** 本计划已由当前会话用户授权执行；所有实现必须使用 `xuzhou110kv_clr` 和 TDD。

**目标：** 从最终真实矩阵生成一版可复现、可审查的 110/35 kV 分面静态可视化。

**架构：** `src/real_visuals.py` 负责读取矩阵、长表标准化、图表生成和清单输出；`scripts/plot_real_2025_visuals.py` 负责 CLI 入口。图表只写入新建 `results/real_2025_visuals/`，不改写正式矩阵。

**技术栈：** Python 3.13、pandas、Matplotlib、JSON/SHA-256、pytest。

---

### 任务 1：定义可视化输入契约

**文件：**
- 创建：`src/real_visuals.py`
- 测试：`tests/test_real_visuals.py`

- [x] 先写失败测试：要求 `prepare_visual_data()` 保留两个电压等级、证据等级、C0/A/B 状态、CLR 和 EAC 字段，并拒绝跨电压聚合。
- [x] 运行定点测试确认红灯：正常应报出模块不存在。
- [x] 实现最小长表标准化和输入门禁。
- [x] 重新运行定点测试。

### 任务 2：生成静态图与发布清单

**文件：**
- 创建：`scripts/plot_real_2025_visuals.py`
- 创建：`results/real_2025_visuals/`
- 测试：`tests/test_real_visuals.py`

- [x] 生成 110/35 kV CLR 区间图、方案状态/EAC 图、证据质量图。
- [x] 导出 PNG、SVG、长表 CSV、README 和包含指纹的 `visual_manifest.json`。
- [x] 在静态图中显示单位、固定分母说明、证据等级和不可行原因。

### 任务 3：验收与约束记录

**文件：**
- 修改：`AGENTS.md`
- 修改：`docs/REAL-2025-RUNBOOK.md`
- 修改：`docs/EXECUTION-PLAN.md`

- [x] 记录 `results/real_2025_visuals/` 输出目录和人工审查约束。
- [x] 使用 `view_image` 检查 PNG，检查字体、标签、不可行文字、分母和电压等级边界。
- [x] 运行可视化定点测试、固定全量测试和真实输入门禁。

### 任务 4：补齐甲方转置式推荐主表

**文件：**
- 修改：`src/real_visuals.py`
- 修改：`tests/test_real_visuals.py`
- 修改：`AGENTS.md`
- 修改：`docs/REAL-2025-RUNBOOK.md`
- 修改：`docs/EXECUTION-PLAN.md`

- [x] 先写失败测试：要求首列为 `指标`、首行输出当前成本最小可行 `R_rec`，并分别输出 110/35 kV。
- [x] 运行定点测试确认红灯：缺少 `build_recommendation_table` 时按预期失败。
- [x] 实现转置式 CSV/Markdown 主表；110 kV 标正式推荐，35 kV 标辅助/非唯一最优，不写未来年份标签。
- [x] 将两套主表纳入 `visual_manifest.json` 和 README，并完成全量测试与发布审计。
