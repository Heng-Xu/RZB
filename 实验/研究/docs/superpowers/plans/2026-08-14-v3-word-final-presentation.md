# v3 最终 Word 矩阵展示优化实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 `subagent-driven-development` 或 `executing-plans` 逐任务实现此计划。步骤使用复选框（`- [ ]`）跟踪进度。

**目标：** 在不改变 v3 业务口径和 CSV 精确查值源的前提下，生成可直接用于甲方人工审查的 110 kV 正式推荐 Word 和 35 kV 辅助 Word，并为主表补齐已验证的展示字段、样式、状态和结构验收。

**架构：** 上游 `src/v3_pipeline.py` 从已经验证的年度锚点和路径结果补齐矩阵展示字段；`src/v3_outputs.py` 使用字段注册表和标准库 XML 生成带样式的单表 DOCX。CSV 保留机器字段和原始值，DOCX 只负责中文标签、格式、颜色、分页和说明，不在 Word 层重新计算。

**技术栈：** Python 3、pandas、标准库 `zipfile`/XML 字符串、pytest、Conda 环境 `xuzhou110kv_clr`；所有实验命令使用 `MPLCONFIGDIR=/tmp/mplcfg_xuzhou`。

**执行状态：** 任务 1—6 已完成；最终验证为 177 项全量测试通过、真实 v3 入口通过、两套 DOCX 结构与 manifest 哈希审查通过。

---

## 文件清单与职责

| 文件 | 操作 | 职责 |
| --- | --- | --- |
| `src/v3_pipeline.py` | 修改 | 为两套矩阵补齐推荐中心值、区间样本/形成方法、容量、正向峰值和反向峰值状态字段 |
| `src/v3_outputs.py` | 修改 | 实现字段注册表、中文状态格式化、A4 横向样式、分组行、表头重复、页脚和 DOCX 包部件 |
| `tests/test_v3_outputs.py` | 修改 | 锁定字段注册、中文化、状态格式和 DOCX 结构的红—绿测试 |
| `tests/test_real_matrices.py` | 修改 | 锁定 110/35 kV 矩阵新增展示字段和旧路径字段不回流 |
| `tests/test_real_visuals.py` | 修改 | 锁定两套 v3 DOCX 的展示层、提示语和脱敏约束 |
| `docs/WORD-MATRIX-PRESENTATION-SPEC.md` | 修改 | 将已批准的详细设计链接纳入正式 Word 规范，并登记展示版本 |
| `docs/superpowers/specs/2026-08-14-v3-word-final-presentation-design.md` | 已创建 | 设计依据和人工审查标准 |
| `docs/superpowers/plans/2026-08-14-v3-word-final-presentation.md` | 新建 | 本实现计划 |
| `results/runs/real-2021-2025-contract-v3/real_2021_2025-v3/` | 生成 | 覆盖当前 v3 正式 CSV、DOCX、技术附表、问题台账和 manifest；不混入旧 `real_2025` 产物 |

当前项目 `.git` 是空占位目录，无法提交 commit；实现过程中仍按任务划分检查工作树和文件哈希，不初始化或改造 Git 仓库。

### 任务 1：先写 Word 展示契约失败测试

**文件：**

- 修改：`tests/test_v3_outputs.py`
- 修改：`tests/test_real_matrices.py`
- 修改：`tests/test_real_visuals.py`
- 测试对象：`src/v3_outputs.py`、`src/v3_pipeline.py`

- [ ] **步骤 1：扩展测试夹具中的矩阵字段。** 在 `tests/test_v3_outputs.py::_matrix` 中加入以下字段，确保后续渲染器不能继续静默少行：

```python
"recommended_clr_center": [2.0] * 8,
"recommended_clr_interval_effective_samples": [3] * 8,
"recommended_clr_interval_method": [
    "不限制容载比成本最小可行结果+cos_phi敏感性（0.90、0.95、1.00）"
] * 8,
"capacity_base_mva": [100.0] * 8,
"positive_peak_base_mw": [50.0] * 8,
"reverse_peak_base_mw": ["未形成同步反向峰值"] * 8,
```

- [ ] **步骤 2：新增 DOCX 结构测试。** 在 `tests/test_v3_outputs.py` 增加 `test_word_matrix_uses_v3_presentation_contract`，打开 DOCX ZIP 并断言：

```python
assert "word/styles.xml" in archive.namelist()
assert "word/footer1.xml" in archive.namelist()
document = archive.read("word/document.xml").decode("utf-8")
assert 'w:orient="landscape"' in document
assert "110 kV 县区正式推荐矩阵" in document
assert "口径与推荐结论" in document
assert "2025 年容载比｜不限制容载比优化" in document
assert "PATH_OPT_CLR_UNBOUNDED" not in document
assert "QX-00001" not in document
assert "styles.xml" not in document
```

- [ ] **步骤 3：新增中文化和状态测试。** 使用一列 `storage`、一列 `new_third_transformer`、一列 `不可行` 和一列 `未识别` 的夹具，断言文档中出现“储能”“新建第三台主变”“不可行”“未识别（设备动作成本未闭合）”，不出现原始动作代码或 `0.00` 替代未识别成本。

- [ ] **步骤 4：新增 110/35 kV 提示测试。** 在 `tests/test_real_visuals.py` 中断言 110 kV 文档包含“正式推荐”，35 kV 文档包含“辅助分析”和“不可行的片区不形成正式唯一推荐”。

- [ ] **步骤 5：运行新增测试确认红灯。**

运行：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh tests/test_v3_outputs.py tests/test_real_matrices.py tests/test_real_visuals.py -q
```

预期：新增的 `styles.xml`、横向页面、中文路径、分组行和新增字段断言失败；失败原因必须是当前 raw XML 生成器和矩阵字段确实没有实现目标，不得通过放宽断言消除红灯。

### 任务 2：补齐 v3 矩阵展示字段

**文件：**

- 修改：`src/v3_pipeline.py:240-335` 的 `_matrix`
- 修改：`tests/test_real_matrices.py`
- 修改：`tests/test_v3_outputs.py` 的矩阵夹具

- [ ] **步骤 1：为区间计算建立有限样本列表。** 在 `_matrix` 的 `sensitivity_clrs` 后增加只保留有限值的列表：

```python
finite_sensitivity_clrs = [value for value in sensitivity_clrs if math.isfinite(value)]
```

区间仍由 `[0.95 基准结果、0.90 敏感性结果、1.00 敏感性结果]` 中已可行且有限的结果取最小—最大；不得把不可行、空值或其他年度结果纳入区间。

- [ ] **步骤 2：在每个矩阵行中写入展示字段。** 在现有 `rows.append` 字典加入：

```python
"recommended_clr_center": clr_unbounded if math.isfinite(clr_unbounded) else "未形成推荐",
"recommended_clr_interval_effective_samples": len(finite_sensitivity_clrs),
"recommended_clr_interval_method": (
    "不限制容载比成本最小可行结果+cos_phi敏感性（0.90、0.95、1.00）"
),
"capacity_base_mva": float(row.official_capacity_mva),
"positive_peak_base_mw": float(row.official_positive_peak_mw),
"reverse_peak_base_mw": "未形成同步反向峰值",
```

`capacity_base_mva` 和 `positive_peak_base_mw` 只来自 `annual_reference.csv` 同电压 2025 年官方锚点；`reverse_peak_base_mw` 不得使用当前 `_annual_input` 的占位 0.0，也不得从静态站级极值相加得到。

- [ ] **步骤 3：增加字段门禁测试。** 在 `tests/test_real_matrices.py` 的矩阵必备字段集合中加入上述 6 个字段，并断言：

```python
assert (matrix["recommended_clr_interval_effective_samples"] >= 0).all()
assert matrix["recommended_clr_interval_method"].notna().all()
assert matrix["reverse_peak_base_mw"].astype(str).eq("未形成同步反向峰值").all()
```

- [ ] **步骤 4：运行矩阵测试确认实现通过。**

运行：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh tests/test_real_matrices.py tests/test_v3_outputs.py -q
```

预期：字段相关断言通过；Word 样式相关断言仍失败，保持任务边界清晰。

### 任务 3：实现 Word 字段注册表与格式化器

**文件：**

- 修改：`src/v3_outputs.py:1-120`
- 测试：`tests/test_v3_outputs.py`

- [ ] **步骤 1：定义稳定的展示注册表。** 在 `src/v3_outputs.py` 中新增以下常量和类型：

```python
WORD_PATH_LABELS = {
    "PATH_ACTUAL_2021_2025": "2021—2025 实际（事实对照）",
    "PATH_OPT_CLR_UNBOUNDED": "不限制容载比优化",
    "PATH_OPT_CLR_LE_2": "控制容载比不超过 2.0 优化",
}

WORD_REQUIRED_DISPLAY_FIELDS = {
    "asset_scope_id",
    "evidence_grade",
    "recommended_clr_interval",
    "recommended_clr_center",
    "capacity_base_mva",
    "positive_peak_base_mw",
    "reverse_peak_base_mw",
    "strict_path_incremental_cost",
    "positive_capacity_gap_mw",
    "reverse_hosting_gap_mw",
    "positive_gap_device_count",
    "reverse_gap_device_count",
    "measure_trigger_constraint",
    "recommended_measure",
}
```

注册表同时列出 6 个分组和表中行顺序；不得根据 DataFrame 当前列顺序自动出表。

- [ ] **步骤 2：实现 `_format_word_value(field, value)`。** 具体规则：

```python
if value is None or pd.isna(value):
    return "未提供"
if value == "未识别":
    return "未识别（设备动作成本未闭合）"
if field.endswith("_clr_2025") or field == "recommended_clr_center":
    return f"{float(value):.3f}"
if field.endswith("_cumulative_eac") or field == "strict_path_incremental_cost":
    return f"{float(value):,.2f}"
if field.endswith("_gap_mw"):
    return f"{float(value):,.2f}"
if field.endswith("_device_count"):
    return str(int(value))
```

在数值转换前保留 `不可行`、`未形成推荐`、`未形成同步反向峰值` 等中文状态；`storage`、`new_third_transformer`、触发约束和证据等级按设计文档中的映射转换。

- [ ] **步骤 3：实现 `_build_word_rows(matrix, voltage)`。** 输出由表头、6 个分组行和固定指标行组成；片区列按 `region_id` 稳定排序，显示为 `片区01`—`片区08`。缺少任一 `WORD_REQUIRED_DISPLAY_FIELDS` 时抛出 `V3OutputError` 并列出字段名，禁止静默少行。

- [ ] **步骤 4：为 35 kV 生成专用提示语。** `voltage == 35` 时在表前说明中固定加入“35 kV 辅助分析，不替代 110 kV 正式推荐；严格路径不可行的片区不形成正式唯一推荐”；110 kV 使用“正式推荐”说明。

- [ ] **步骤 5：运行格式化器单测。**

运行：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh tests/test_v3_outputs.py -q
```

预期：字段标签、状态字符串、数值精度和缺字段错误测试通过；DOCX XML 样式测试仍等待任务 4。

### 任务 4：实现可打印的 DOCX 包和样式

**文件：**

- 修改：`src/v3_outputs.py:36-112` 的 `_document_xml`、`write_transposed_word_matrix`
- 测试：`tests/test_v3_outputs.py`、`tests/test_real_visuals.py`

- [ ] **步骤 1：实现 DOCX 包部件。** 保持标准库实现，不引入运行时新依赖；ZIP 内必须写入：

```text
[Content_Types].xml
_rels/.rels
word/document.xml
word/styles.xml
word/footer1.xml
word/_rels/document.xml.rels
```

`styles.xml` 定义标题、说明、表头、正文和页脚样式；`footer1.xml` 包含固定审查层文字和 `PAGE` 字段。

- [ ] **步骤 2：实现页面和表格属性。** 在 `document.xml` 中写入 A4 横向页面：宽 16838 twips、高 11906 twips，页边距上/下 709 twips、左/右 680 twips；表格使用固定布局、指标列宽约 5.2 cm、8 个片区列均分剩余宽度。

- [ ] **步骤 3：实现表格视觉层级。** 为分组行使用 `w:gridSpan` 合并 9 列；表头行增加 `w:tblHeader`；按行/单元格写入深蓝表头、浅蓝分组、浅绿推荐、浅黄严格、浅红不可行和橙色证据缺口的 `w:shd`。不在文档中写入 raw `QX-`、`PATH_`、`SCHEME_` 或机器元数据。

- [ ] **步骤 4：实现标题、说明和表后边界说明。** 标题使用电压专用名称；副标题包含 8 片区、2021 年共同基准和 2022—2025 年决策期；表后固定写 4 条边界说明，并链接文字指向 `分析/v3真实数据问题补充说明_供甲方汇报.md`，不把机器路径写进单元格。

- [ ] **步骤 5：更新生成器调用。** `build_v3_artifacts` 继续写出原有两个 DOCX 文件名，只将 `title` 和 `voltage` 传给新渲染器；manifest 增加：

```python
"word_presentation_version": "3.1",
"word_presentation_spec": "docs/WORD-MATRIX-PRESENTATION-SPEC.md",
```

- [ ] **步骤 6：运行 Word 结构测试确认绿灯。**

运行：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh tests/test_v3_outputs.py tests/test_real_visuals.py -q
```

预期：测试通过；两个 DOCX 各自只有一张主矩阵表，存在 `styles.xml`、页脚和横向页面设置，没有图片部件和机器字段。

### 任务 5：同步规范并完成生产重生成

**文件：**

- 修改：`docs/WORD-MATRIX-PRESENTATION-SPEC.md`
- 读取：`分析/v3真实数据问题补充说明_供甲方汇报.md`
- 生成：`results/runs/real-2021-2025-contract-v3/real_2021_2025-v3/` 下的 v3 产物

- [ ] **步骤 1：更新正式 Word 规范。** 在 `docs/WORD-MATRIX-PRESENTATION-SPEC.md` 增加详细设计文档链接、展示版本 `3.1`、新增展示字段和“无图片、Word 只作人工审查层”的明确说明；不修改 v3 业务定义。

- [ ] **步骤 2：运行真实 v3 端到端入口重生成当前产物。**

运行：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr python scripts/run_all.py \
  --dataset real_2021_2025 \
  --config model_contract.yaml \
  --processed-dir data/processed/real_2021_2025 \
  --output-dir results/runs/real-2021-2025-contract-v3/real_2021_2025-v3 \
  --skip-gen
```

预期：退出码 0；输出目录的 CSV 与原 v3 口径一致，DOCX 时间戳和 manifest 哈希更新为本次生成，旧 `real_2025` 不被读取。

- [ ] **步骤 3：检查最终 Word 与 CSV 一致性。** 使用标准库 `zipfile` 解析两个 DOCX，检查标题、8 片区、6 个分组、路径中文名、状态和机器字段禁入；读取同目录 CSV 对比每个指标单元格的格式化来源。

- [ ] **步骤 4：检查最终交付完整性。** 确认同目录存在两套矩阵、技术附表、问题台账、manifest；确认补充说明文件存在且链接可解析；确认 Word 不含 `word/media/`。

### 任务 6：全量验证与交付审查

**文件：**

- 验证：`tests/` 全量测试、真实端到端输出、最终 manifest、两套 DOCX
- 读取：`results/runs/real-2021-2025-contract-v3/real_2021_2025-v3/manifest.json`

- [ ] **步骤 1：运行项目固定全量测试。**

运行：

```bash
env MPLCONFIGDIR=/tmp/mplcfg_xuzhou conda run -n xuzhou110kv_clr bash scripts/runtests.sh
```

预期：全量测试通过；不得用跳过测试或放宽断言替代修复。

- [ ] **步骤 2：再次运行真实 v3 入口。**

运行与任务 5 相同的 `scripts/run_all.py --dataset real_2021_2025 --skip-gen` 命令，确认生成过程在全量测试之后仍可复现。

- [ ] **步骤 3：验证 v3 业务门禁不被展示改动破坏。** 检查：

```python
assert manifest["contract_version"] == "3.0.0"
assert manifest["voltage_separation"] is True
assert manifest["path_cost_inclusion_validated"] is True
assert manifest["timeseries_grade_a_ready"] is True
assert not any("SCHEME_" in path.name for path in output_dir.iterdir())
```

并从 `path_year_results.csv` 验证严格路径所有可行年度 `clr <= 2.0 + 1e-9`，从 `path_cost_breakdown.csv` 验证不限制路径累计年化成本不高于严格路径。

- [ ] **步骤 4：记录展示版本和生产文件哈希。** 确认 `manifest.json` 的 `word_presentation_version` 为 `3.1`，两个 DOCX 的 SHA-256 与 manifest 的 `output_files` 一致，Word 与 CSV 的生成批次相同。

- [ ] **步骤 5：输出交付摘要。** 最终摘要只报告当前 v3 生产目录、两套 Word 文件、两套 CSV、技术附表、补充说明 MD、测试结果和任何仍需甲方知悉的质量标记；不引用旧 Word 或旧年度矩阵。

## 计划自检

- [x] 规格中的转置矩阵、A4 横向、颜色层级、中文化、状态、110/35 kV 差异、边界说明、字段来源、无图片和验收测试均有对应任务。
- [x] 当前矩阵缺少的容量、正向峰值、反向峰值和推荐中心值被明确安排在上游矩阵构建阶段补齐，未允许 Word 层猜算。
- [x] 每个测试修改先写失败断言，再运行红灯，再实现，再运行绿灯；没有通过删除旧测试或降低断言来迁移。
- [x] 任务中的函数名、字段名和文件路径与当前代码结构一致。
- [x] 未引入旧 `real_2025`、旧 C0/A/B、图片或跨电压合算。
- [x] 未把 Git 初始化、源数据覆盖或结果目录递归删除纳入计划。
