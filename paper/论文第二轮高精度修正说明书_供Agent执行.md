# 论文第二轮高精度修正说明书（供 Agent 执行）

## 0. 任务信息

### 0.1 输入文件

1. **老师批注稿 PDF**：`许恒-Engineering-Prior-Guided NSGA-II for Elastic Capacity-Load Ratio Planning under High Distributed Photovoltaic Penetration(1).pdf`
2. **当前 Word 修订稿**：`epg-nsga-ii-paper_final_compressed_revised.docx`

### 0.2 修改目标

依据老师在 PDF 中的高亮、文字批注和自由文本批注，对当前 Word 修订稿进行第二轮高精度修正，使其同时满足：

- 老师的每一项批注意见均有明确响应；
- 标题、摘要、引言、方法、实验和结论之间术语完全统一；
- 数学模型、算法步骤、实验指标和结论表述科学、可复核；
- 公式、表格、图和参考文献符合 IEEE 会议论文常用规范；
- 不改变未经核验的实验数据和算法逻辑；
- 维持双栏、两页版式，避免溢出、遮挡、公式截断和字体异常。

### 0.3 已确认的特别要求

- **删除当前参考文献 [4]**：M. Nicolini 关于给水网络多目标优化的会议论文。
- 删除后必须同步更新全文引用编号和参考文献编号。

---

# 1. Agent 执行原则

## 1.1 必须遵守

1. **先备份原 Word 文件**，不得覆盖唯一原件。
2. 内容修改以老师批注为最高优先级。
3. 不得自行修改以下数值，除非能够从原始实验记录或代码中核验：
   - 13.1%；
   - 188.82 million CNY/yr；
   - 114 MWh/yr；
   - K=10、20、30、40；
   - population 100；
   - three seeds；
   - 400、800 generations；
   - 84 generations；
   - 表 I 中全部 HV 数值；
   - CLR、储能功率及各工程参数的上下界。
4. 不得为了补充数学形式而虚构算法步骤。形式化表达必须与实际代码或现有文字逻辑一致。
5. 不得使用普通文本模拟公式。公式须使用 Word 原生公式对象（OMML）或可稳定渲染的等价对象。
6. 修改完成后必须：
   - 重新导出 PDF；
   - 逐页检查两栏排版；
   - 检查公式、并集符号、上下标、希腊字母、参考文献编号；
   - 确认仍为两页。

## 1.2 修改优先级

- **P0：阻断提交的问题**——公式损坏、老师批注未响应、未定义符号、引用编号错误、结论与表格不一致。
- **P1：科学与术语问题**——概念歧义、过度结论、方法描述不规范、统计口径不清。
- **P2：语言与版式优化**——句式、连字符、大小写、图注、段落间距。

---

# 2. 老师批注逐项响应矩阵

| 序号 | PDF 中的批注或高亮 | 当前 Word 状态 | Agent 必须执行的处理 |
|---|---|---|---|
| 1 | 标题批注：`of county-wise/regional 110kV grid under` | 已从 Elastic Planning 改为 Differentiated Optimization，但 `County 110-kV Grids` 仍不够自然 | 标题改为 **in a County-Level 110-kV Grid**；若作者坚持面向一般方法，可用复数 **in County-Level 110-kV Grids**，但本稿默认采用单数，因为模型对应一个县域电网内的多座变电站 |
| 2 | `High Distributed Photovoltaic Penetration` 术语检查 | 已基本改为 `High penetration of distributed PV generation` | 正文统一用 **high penetration of distributed PV generation** 或 **under high distributed PV penetration**；不要在同一段混用多种变体 |
| 3 | `county 110 kV grids`，批注 `of county-wise 110 kV grids` | 摘要、引言已用 `county-level 110-kV grids`，标题未统一 | 统一为 **county-level 110-kV grid(s)**；作前置定语时必须写 `110-kV` |
| 4 | `reverse power and changing N-1 supply risk`：术语检查、断句 | 已改为 reverse power flow + supply adequacy，但句子仍称电网“bidirectional” | 彻底删除 `grids bidirectional`；改为“reverse conventional power-flow directions”或“cause reverse power flow” |
| 5 | `This paper`，批注 `study / research` | 已改为 `This study` | 保持 |
| 6 | `elastic per-station planning model`，批注“逐站？” | 已改为协调县域内多座 110-kV 变电站 | 保持“coordinates the 110-kV substations within a county”，避免 `per-station planning` |
| 7 | `synthetic county case`，批注“生成的？” | 已改为 `public-data-informed synthetic county test system` | 保持，并在实验部分明确由 scaled IEEE 33-bus feeders 和 PVGIS 数据构建 |
| 8 | `EENS`，批注“缩写 全拼？” | 摘要已补全 `expected energy not supplied (EENS)` | 保持；正文后续只用 EENS |
| 9 | 引言中 `grids increasingly bidirectional`，批注“引起困惑” | 当前仍写 `is turning ... grids bidirectional` | **未完成，必须重写** |
| 10 | `reverse-power pressure`，批注“术语确认” | 已改为 `under-constrains reverse power flow` | 保持，但建议用 `does not adequately constrain reverse power flow`，避免语义过强 |
| 11 | `PV-dense stations`，批注“引发困惑” | 已改为 `substations with high distributed-PV penetration` | 保持；推荐进一步改为 `substations with high generation-to-load ratios`，与图 1 横轴一致 |
| 12 | `nondominated sorting`，批注 `non-dominated?` | 当前正文和算法仍为 `nondominated` | 正文、算法输出统一改为 **non-dominated**；参考文献原始题名中的 `Nondominated` 不得擅改 |
| 13 | 贡献中 `N-1 constraints`，批注“确认是否正确，N-1 奇怪” | 已改为 EENS-based supply-adequacy objective | 继续统一：不要把 EENS 简称为 `N-1 risk`；改为 `supply-adequacy objective under N-1 contingencies` |
| 14 | WarmStartSampling 批注：`公式？或者更形式化、规范化的表达？` | 仍为自然语言 | 必须加入简洁数学定义或集合投影表达 |
| 15 | RepairProjection 批注：`公式？或者更形式化、规范化的表达？` | 仍为自然语言 | 必须加入约束修复表达，并明确无法修复时如何处理 |
| 16 | K=20、K=40 等数值高亮 | 未给出明确文字批注 | 保留数值，但必须补充 K 的定义，且统计口径必须说清楚 |

---

# 3. 全局术语与写法统一表

Agent 应全文搜索并统一替换，避免局部修改后前后不一致。

| 不推荐或需检查 | 统一写法 | 说明 |
|---|---|---|
| county 110 kV grid | county-level 110-kV grid | `110-kV` 作前置定语 |
| 110 kV substations | 110-kV substations | 作前置定语 |
| grids are bidirectional | reverse power flow occurs / conventional power-flow directions are reversed | “电网双向”概念易歧义 |
| reverse power | reverse power flow | 电力系统常用完整术语 |
| reverse-power-flow constraints | reverse-power-flow constraints | 作复合定语时保留连字符 |
| distributed photovoltaics | distributed photovoltaic generation / distributed PV generation | 摘要首次出现写全称 |
| PV-dense station | substation with a high generation-to-load ratio | 与图 1 和模型变量一致 |
| elastic CLR | differentiated CLR | 本稿已从“弹性”转向“差异化优化” |
| planning model / optimization model 混用 | multiobjective planning model 或 multiobjective optimization model | 选一个主称谓；建议正文用 `multiobjective planning model`，标题用 `optimization` |
| nondominated | non-dominated | 正文和算法按老师批注统一；文献原题名除外 |
| crowding select | crowding-distance selection | 规范算法术语 |
| N-1 risk objective | EENS-based supply-adequacy objective under N-1 contingencies | 避免把 EENS 笼统称“风险” |
| feasibility-preserving warm-start | feasibility-aware warm-start sampling | 当前文字仅称 near-feasible，不能宣称完全保持可行性 |
| repair projection | engineering repair operator / repair projection operator | 若不是严格欧氏投影，优先使用 `repair operator` |
| +4.8% over | 4.8% higher than | 科学英语更自然 |
| 9.5× fewer | uses approximately 10.5% as many evaluations / reduces evaluations by approximately 89.5% | 避免倍数歧义 |
| K=10–40 | K ∈ {10, 20, 30, 40} | 实际只测试四个离散规模，不是连续区间 |
| high distributed-PV penetration | high penetration of distributed PV generation | 正文中更自然 |

---

# 4. 标题修改

## 4.1 推荐最终标题

> **Engineering-Prior-Guided NSGA-II for Differentiated Capacity-Load Ratio Optimization in a County-Level 110-kV Grid under High Distributed PV Penetration**

## 4.2 选择理由

- `Differentiated` 明确表示不同变电站采用不同 CLR；
- `Optimization` 与多目标求解一致；
- `a County-Level 110-kV Grid` 表示一个县域电网内包含多座 110-kV 变电站，避免误解为“县级行政分析角度”或多个孤立电网；
- 保留 `under High Distributed PV Penetration`，与研究场景一致。

## 4.3 可接受备选

若作者强调方法可用于多个县域电网，可改为：

> **... in County-Level 110-kV Grids under High Distributed PV Penetration**

全文标题、摘要、引言和图注必须采用同一单复数逻辑。

---

# 5. 摘要整段替换稿

建议直接用下列文本整体替换当前摘要，避免继续局部修补导致逻辑重复：

> **Abstract—High penetration of distributed photovoltaic (PV) generation can cause reverse power flow in county-level 110-kV grids and alter supply adequacy under N-1 contingencies. This study formulates a bi-objective planning model that coordinates the 110-kV substations within a county by optimizing differentiated capacity-load ratios (CLRs) and storage power ratings. The model minimizes annualized cost and expected energy not supplied (EENS), subject to a load-weighted aggregate CLR band and station-level and upstream reverse-power-flow constraints. Engineering-Prior-Guided NSGA-II (EPG-NSGA-II) introduces feasibility-aware warm-start sampling and an engineering repair operator. On a public-data-informed synthetic county test system, the selected design reduces annualized cost by 13.1% relative to a uniform R=2.0 baseline at the same EENS. For the largest case with K=40 substations, EPG-NSGA-II achieves a 4.8% higher converged hypervolume than standard NSGA-II and reaches the latter’s converged hypervolume in approximately 84 generations.**

## 5.1 摘要修改说明

- 删除 `makes ... grids bidirectional`；
- 用 `bi-objective` 明确只有两个目标；
- 用 `within a county` 回应“逐站？”和“县级/县域”问题；
- `K=40 substations` 在摘要中直接定义 K 的物理含义；
- 删除 `reaches +4.8% over`；
- 不在摘要中写 `9.5× fewer`，避免评价口径歧义；
- 若全文数据不是“converged HV”，将 `converged hypervolume` 改为 `final hypervolume`。

---

# 6. Index Terms 修改

推荐：

> **Index Terms—Capacity-load ratio, distributed photovoltaic generation, multiobjective optimization, reverse power flow, 110-kV grid planning.**

说明：

- `substation planning` 可用，但 `110-kV grid planning` 更贴近全文层级；
- 关键词不要使用未在正文稳定采用的 `elastic planning`。

---

# 7. 引言修改

## 7.1 第一段整体替换稿

> **High penetration of distributed PV generation can produce midday net power export at 110-kV substations, causing reverse power flow and altering supply adequacy under N-1 contingencies [1]. A uniform capacity-load ratio may overinvest at substations with moderate generation-to-load ratios while failing to adequately represent reverse-power-flow constraints at substations with high distributed-PV penetration [2], [3]. Existing planning commonly relies on fixed or empirical CLR rules, whereas evolutionary multiobjective optimization can directly search the trade-off between annualized cost and supply adequacy [2]–[4]. Related evolutionary transfer studies also indicate that prior search knowledge can improve optimization efficiency [5]. However, random initialization and variation under strongly coupled engineering constraints can generate a large proportion of infeasible individuals.**

## 7.2 该段的引用编号以前述“删除当前文献 [4]”后的新编号为准

删除当前参考文献 [4] 后：

- 当前 [5] NSGA-II → 新 [4]；
- 当前 [6] transfer optimization → 新 [5]。

## 7.3 引用准确性约束

- 当前 [1] 的 duck-curve 文献主要支撑高 PV 渗透引起的净负荷变化、灵活性需求等，不宜单独承担全部“N-1 供电充裕度”论断。
- 如现有 [2]、[3] 实际讨论 N-1、供电能力或容载比约束，可将 N-1 句的引用扩展为 `[1]–[3]`。
- Agent 不得在未核对文献正文时随意给某句追加引用。

## 7.4 第二段整体替换稿

> **This study proposes EPG-NSGA-II, which retains the non-dominated sorting and crowding-distance selection mechanisms of NSGA-II and introduces two engineering-prior operators: feasibility-aware warm-start sampling and a feasibility-restoring repair operator. The contributions are threefold. First, a bi-objective planning model jointly optimizes differentiated CLRs and storage power ratings under a load-weighted aggregate CLR band and station-level and upstream reverse-power-flow constraints, with EENS quantifying supply inadequacy under N-1 contingencies. Second, EPG-NSGA-II embeds engineering knowledge into population initialization and post-variation repair. Third, a public-data-informed synthetic county test system is used for comparative and ablation studies.**

## 7.5 必须避免

- 不要继续使用 `grids bidirectional`；
- 不要把 `EENS` 直接称作 `N-1 risk`；
- 不要使用不完整短语式贡献句 `Contributions: ...`；
- 不要声称算法“feasibility-preserving”，除非全部个体在初始化后均严格可行且代码可证明。

---

# 8. Planning Model 部分修正

## 8.1 第一段建议替换

> **The model considers the set \(\mathcal J=\{1,\ldots,K\}\) of 110-kV substations within a county-level grid, where \(K\) is the number of substations. Each substation \(j\in\mathcal J\) is assigned two planning variables: the capacity-load ratio \(R_j\) and the storage power rating \(P_j\) used to mitigate reverse power flow. With an annual load-growth rate of 5% over a five-year horizon, the planning-year peak load of substation \(j\) is denoted by \(L_j^p\) and is used consistently in the capacity, reverse-power-flow, and supply-adequacy calculations.**

## 8.2 式（1）及其说明

公式应重建为：

\[
\tilde r_j(P_j)=\max\{0,r_j^0-P_j\}.
\tag{1}
\]

紧接的说明建议写为：

> **Here, \(r_j^0\) is the pre-storage midday reverse injection at substation \(j\), and \(\tilde r_j(P_j)\) is the residual reverse power flow after storage absorption. The decision bounds are \(R_j\in[1.2,3.0]\) and \(P_j\in[0,6]\) MW.**

## 8.3 式（2）

重建为：

\[
R_{\mathrm L}\le
\frac{\sum_{j\in\mathcal J}R_jL_j^p}
{\sum_{j\in\mathcal J}L_j^p}
\le R_{\mathrm U},
\quad R_{\mathrm L}=1.8,\;R_{\mathrm U}=2.2.
\tag{2}
\]

说明建议：

> **The middle term in (2) is the load-weighted aggregate CLR of the county-level grid.**

注意：当前 Word 中式（2）存在 `\(`、`\)` 残留，必须删除并重建公式对象。

## 8.4 式（3）

重建为两行约束：

\[
\tilde r_j(P_j)\le \beta R_jL_j^p,\quad \forall j\in\mathcal J,
\]

\[
\eta\sum_{j\in\mathcal J}\tilde r_j(P_j)
\le \beta R_{220}\delta\sum_{j\in\mathcal J}L_j^p.
\tag{3}
\]

参数说明建议改为完整句：

> **Here, \(\beta=0.85\) is the transformer reverse-loading limit, \(R_{220}=1.8\) is the upper-level CLR, \(\delta=0.85\) is the upstream coincidence factor, and \(\eta=1.0\) is the reverse-power coincidence factor. The first constraint limits residual reverse power flow at each substation, whereas the second limits the coincident reverse power flow at the upstream interface.**

## 8.5 式（4）

重建为：

\[
\min_{\mathbf R,\mathbf P}\;\bigl(f_1(\mathbf R,\mathbf P),f_2(\mathbf R)\bigr),
\]

\[
f_1=\sum_{j\in\mathcal J}
\left(c_RR_jL_j^p+c_PP_j+C_j^{\mathrm{loss}}+C_j^{\mathrm{om}}\right),
\]

\[
f_2=\sum_{j\in\mathcal J}\mathrm{EENS}_j.
\tag{4}
\]

正文说明：

> **The first objective \(f_1\) is the annualized cost, where \(c_R\) and \(c_P\) are annualized unit costs and \(C_j^{\mathrm{loss}}\) and \(C_j^{\mathrm{om}}\) are the annualized loss and operation-and-maintenance costs. The second objective \(f_2\) is total EENS and quantifies supply inadequacy under N-1 contingencies.**

### 关于当前公式中的 \(T_j\)

当前式（4）含有 `EENS_j(R_j,T_j,L_j^p)`，但全文未定义 \(T_j\)。Agent 必须执行以下校核：

- 若 \(T_j\) 在代码中是实际输入（例如变压器配置或联络支援参数），在首次出现时明确定义；
- 若 \(T_j\) 并非独立变量或没有进入 EENS 计算，**从公式中删除**；
- 不得保留未定义符号。

默认建议删除 \(T_j\)，将 \(f_2\) 直接写为总 EENS。

## 8.6 式（5）

重建为：

\[
\mathrm{EENS}_j=
\sum_{s\in\Omega_j}p_sh_s\max\{0,L_j^p-S_{j,s}\}.
\tag{5}
\]

正文说明：

> **In (5), \(\Omega_j\) is the outage-state set for substation \(j\), \(p_s\) and \(h_s\) are the probability and duration of state \(s\), and \(S_{j,s}\) is the available supply determined by transformer capacity and fixed tie-line support. Storage is modeled only as a reverse-power-flow mitigation resource and is not credited as firm capacity under N-1 contingencies.**

## 8.7 当前公式版式 P0 问题

当前 Word 渲染存在以下问题，必须全部修复：

1. 式（2）、式（4）、式（5）存在 LaTeX 定界符残留；
2. 第 2 页顶部的式（5）被裁切；
3. 个别上下标位置异常；
4. 公式与编号间距不一致；
5. 公式中英文普通字符和数学斜体混杂。

处理方式：

- 删除原公式对象后用 Word 原生公式重新输入；
- 不输入外层 `\(` 和 `\)`；
- 公式段落不得设置过小的固定行距；
- 式（5）与前一段设置“与下段同页”或适当调整分页；
- 导出 PDF 后逐式放大检查。

---

# 9. EPG-NSGA-II Procedure 形式化修正

老师对 WarmStartSampling 和 RepairProjection 的核心意见尚未完成。Agent 应用形式化表达替换目前两个纯自然语言段落。

## 9.1 算法前导段替换

> **EPG-NSGA-II retains the NSGA-II backbone [4] and applies a feasibility-aware warm start before the first objective evaluation and an engineering repair operator after each variation step. Let \(\mathbf R=(R_1,\ldots,R_K)\) and \(\mathbf P=(P_1,\ldots,P_K)\). The feasible aggregate-CLR set is**

\[
\mathcal R=\left\{\mathbf R:\;R_{\min}\le R_j\le R_{\max},\;
R_{\mathrm L}\le \frac{\sum_jR_jL_j^p}{\sum_jL_j^p}\le R_{\mathrm U}\right\}.
\]

## 9.2 WarmStartSampling 推荐表达

> **WarmStartSampling first draws \(R_j^{(0)}\sim\mathcal U(R_{\min},R_{\max})\) and maps the sampled vector to the aggregate-CLR feasible set, \(\mathbf R\leftarrow\Pi_{\mathcal R}(\mathbf R^{(0)})\). Given \(\mathbf R\), the minimum station-level storage requirement is initialized by**

\[
P_j\leftarrow
\Pi_{[0,P_{\max}]}
\left([r_j^0-\beta R_jL_j^p]_+\right),
\quad [x]_+=\max\{0,x\}.
\]

> **If the upstream constraint remains violated, additional storage is allocated to substations in descending order of residual reverse injection until (3) is satisfied or all storage ratings reach \(P_{\max}\).**

## 9.3 RepairProjection 推荐表达

> **After variation, RepairProjection first clips the decision variables to their bounds and projects the CLR vector onto \(\mathcal R\). It then updates each storage rating as**

\[
P_j\leftarrow
\Pi_{[0,P_{\max}]}
\left(\max\left\{P_j,[r_j^0-\beta R_jL_j^p]_+\right\}\right),
\]

> **followed by the same residual-pressure-based repair for the upstream constraint. A final feasibility test is then performed.**

## 9.4 必须明确“最终仍不可行”如何处理

当前稿只写 `runs a final feasibility check`，但没有说明失败后的处置。Agent 必须对照真实代码，选择并写明唯一正确的处理方式：

- **方案 A：重采样**
  > Individuals that remain infeasible after repair are discarded and resampled.

- **方案 B：惩罚/约束支配**
  > Remaining constraint violations are retained and handled by constraint-domination based on total violation.

- **方案 C：保证可修复**
  > The implemented bounds and repair sequence guarantee feasibility for all generated individuals.

不得在没有代码依据时选择方案 C。

## 9.5 “Projection”术语校核

- 若代码真正求解到集合 \(\mathcal R\) 的最小距离投影，可保留 `projection`；
- 若代码仅按比例缩放或逐项贪心修复，应写 `repair mapping` 或 `repair operator`，不要宣称严格数学投影；
- 算法名 `RepairProjection` 可保留为函数名，但正文需说明实际机制。

---

# 10. Algorithm 1 修改

## 10.1 算法输入定义

在算法前或算法说明中定义：

> **Here, \(\mathcal D\) denotes the planning data, \(N\) is the population size, and \(G\) is the maximum number of generations.**

若 `D` 实际表示决策维数而不是数据集，必须按代码修改，不得猜测。

## 10.2 推荐算法文本

```text
Algorithm 1  EPG-NSGA-II
Input: planning data 𝒟, variable bounds, CLR band, reverse-power-flow parameters, population size N, and generation limit G.
Output: feasible non-dominated set A.
1: P ← WarmStartSampling(𝒟, N)
2: P ← RepairOperator(P)
3: Evaluate f1 and f2 for all individuals in P
4: for t = 1 to G do
5:     Q ← Variation(P)
6:     Q ← RepairOperator(Q)
7:     Evaluate f1 and f2 for all individuals in Q
8:     U ← P ∪ Q
9:     P ← NonDominatedSortingAndCrowdingSelection(U, N)
10: end for
11: A ← feasible non-dominated individuals in P
12: return A
```

## 10.3 必修版式问题

- 第 8 行必须显示数学并集符号 `∪`，不能显示普通字母 U；
- `nondominated sort + crowding select` 改为 `non-dominated sorting and crowding-distance selection`；
- 输出改为 `feasible non-dominated set`；
- 函数命名统一：正文和算法不得同时混用 `RepairProjection`、`Repair projection`、`repair operator` 而不解释；
- 检查 Algorithm 1 上下横线、行号和正文间距。

---

# 11. Experiments 修改

## 11.1 Setup 整段替换稿

删除当前参考文献 [4] 并重新编号后，建议写为：

> **The benchmark is a public-data-informed synthetic county test system constructed from scaled IEEE 33-bus feeders [6] and PVGIS irradiance data [7]. Four system sizes are considered, \(K\in\{10,20,30,40\}\), where \(K\) denotes the number of 110-kV substations. The population size is \(N=100\), and each setting is evaluated over three independent runs. Standard NSGA-II and NSGA-III [8] are run for 800 generations as longer-budget references, whereas EPG-NSGA-II and its ablations are run for 400 generations.**

## 11.2 必须澄清的统计口径

当前文本只说 `three seeds per setting`，但表 I 只有一个数字。Agent 必须核验并采用真实口径：

- 若表中是三次运行均值：写 `mean HV over three independent runs`；
- 若为中位数：写 `median HV`；
- 若为最好一次：必须写 `best-run HV`，但不推荐；
- 若数值未做多次汇总，需回到实验结果重新计算，不能假称均值。

推荐表题：

> **TABLE I. MEAN NORMALIZED HYPERVOLUME OVER THREE INDEPENDENT RUNS**

推荐表后首句：

> **Table I reports the mean final HV over three independent runs, normalized by the corresponding mean HV of standard NSGA-II for each \(K\).**

如果这些数值代表“收敛后”而不是“固定预算最终值”，必须在方法中说明收敛判据，否则使用 `final HV` 更稳妥。

## 11.3 表 I 分析段替换稿

> **EPG-NSGA-II matches or exceeds standard NSGA-II for all four system sizes, with the largest improvement of 4.8% at \(K=40\). Repair-only closely tracks the full method, indicating that the repair operator accounts for most of the final-HV improvement in this experiment. Warm-start-only remains close to the baseline and is primarily associated with early-stage acceleration. NSGA-III yields lower final HV than standard NSGA-II for the tested bi-objective instances.**

注意：

- `indicating` 比 `proving` 更合适；
- 不能仅凭一个表格断言修复算子在一般情况下“决定”算法性能；
- 不要写 `widening to +4.8%`。

## 11.4 84 generations 句子替换

当前：

> `roughly 9.5× fewer evaluations`

替换为：

> **At \(K=40\), EPG-NSGA-II attains the final HV of the 800-generation standard NSGA-II reference after approximately 84 generations, corresponding to about 10.5% as many objective evaluations under the same population size.**

如评价次数包含初始种群，Agent 应按真实计数公式核验比例；如无法精确核验，改为：

> **... after approximately 84 generations, using substantially fewer objective evaluations under the same population size.**

---

# 12. County-Level Application at K=20 修改

## 12.1 小标题

建议保留：

> **C. County-Level Application at \(K=20\)**

## 12.2 整段替换稿

> **The \(K=20\) case is used as a representative county-level application. Its knee solution has a load-weighted aggregate CLR of 1.80, an annualized cost of 188.82 million CNY/yr, and an EENS of 114 MWh/yr. In the selected solution, storage is preferentially allocated to substations with higher generation-to-load ratios, whereas substations assigned lower CLRs rely more on fixed tie-line support (Fig. 1). Relative to the uniform \(R=2.0\) baseline, the differentiated design reduces annualized cost by 13.1% at the same EENS level.**

## 12.3 修改原因

- `High generation-to-load substations` 缺少 `ratios`；
- `low-ratio ones` 不明确是低源荷比还是低 CLR；
- `fixed tie-line support` 与式（5）的定义保持一致；
- `The K=20 case` 比 `K=20 is a representative county size` 更自然。

## 12.4 图 1 图注

建议：

> **Fig. 1. Differentiated CLR and storage configuration for the synthetic county test system with \(K=20\).**

图 1 视觉检查：

- 裁掉不必要的白边；
- 确保每个格点的 CLR 和 BESS 数值在 100% 缩放时可辨认；
- 横轴 `low → high generation-to-load ratio` 与正文术语一致；
- 色条名称建议改为 `capacity-load ratio R` 或 `CLR R`，不要只写含糊的 `capacity-load ratio`。

---

# 13. Conclusion 整段替换稿

> **EPG-NSGA-II combines feasibility-aware warm-start sampling with an engineering repair operator for differentiated CLR optimization in a county-level 110-kV grid under high distributed PV penetration. In the synthetic test cases, the method reduces annualized cost at the same EENS level and achieves equal or higher final HV than standard NSGA-II, with the largest improvement of 4.8% at \(K=40\). Future work will focus on calibration using real-grid data, energy-limited storage modeling, and more extensive statistical testing.**

说明：

- 删除 `feasibility-preserving`；
- 删除 `widening to +4.8%`；
- 使用完整句 `Future work will...`；
- 若表 I 实际使用 converged HV，可把 `final HV` 改为 `converged HV`，但全文必须一致。

---

# 14. 删除文献 [4] 及引用重排

## 14.1 删除项

删除当前：

> **[4] M. Nicolini, "Multi-objective genetic algorithms in designing redundant water distribution systems," in Proc. 2025 IEEE Int. Conf. MIND, 2025.**

## 14.2 新编号映射

| 当前编号 | 删除后编号 | 文献 |
|---|---:|---|
| [1] | [1] | Hou et al., probabilistic duck curve |
| [2] | [2] | Xiao et al., substation capacity-load ratio |
| [3] | [3] | Wang et al., multi-voltage-level CLR planning |
| [4] | 删除 | Nicolini, water distribution systems |
| [5] | [4] | Deb et al., NSGA-II |
| [6] | [5] | Xue et al., evolutionary sequential transfer optimization |
| [7] | [6] | Baran and Wu, IEEE 33-bus feeder source |
| [8] | [7] | PVGIS |
| [9] | [8] | Deb and Jain, NSGA-III |

## 14.3 全文引用同步替换

- EPG-NSGA-II Procedure：`NSGA-II backbone [5]` → `[4]`；
- Setup：`feeders [7] and PVGIS [8]` → `[6]`、`[7]`；
- Setup：`NSGA-III [9]` → `[8]`；
- 引言中原 `[2], [3], [4], [5]` 必须根据改写后的句子重新分配，禁止机械替换导致错误引用；
- 引言中原 `[6]` → `[5]`。

## 14.4 参考文献 [1] 补全

建议改为：

> **[1] Q. Hou, N. Zhang, E. Du, M. Miao, F. Peng, and C. Kang, “Probabilistic duck curve in high PV penetration power system: Concept, modeling, and empirical analysis in China,” Applied Energy, vol. 242, pp. 205–215, 2019, doi: 10.1016/j.apenergy.2019.03.067.**

## 14.5 参考文献 [5] 的适用性说明

删除原 [4] 后，Xue et al. 变为新 [5]。该文属于演化迁移优化，不是工程约束修复算法。正文只能用来支持“先验搜索经验可能提高演化优化效率”，不能直接宣称其支持本文的 warm-start 或 repair operator。

若篇幅紧张，作者可后续决定是否删除该文；本轮 Agent 不得未经确认删除。

## 14.6 参考文献格式统一

- 页码统一使用 `pp. 205–215` 等；
- 期刊缩写格式统一；
- 中文文献统一保留 `(in Chinese)`；
- 英文引号统一；
- 参考文献题名按原始题名保留拼写，不能因正文采用 `non-dominated` 而修改正式题名中的 `nondominated`；
- 全部文献必须被正文引用，正文全部引用必须有对应文献。

---

# 15. 版式与格式修正清单

## 15.1 P0 版式问题

1. 第 2 页顶部式（5）被裁切；
2. 式（2）、式（4）、式（5）存在转义符/定界符残留；
3. Algorithm 1 第 8 行并集符号可能显示为普通 U；
4. 公式中的符号在文本提取时缺失，说明公式对象需重新验证；
5. `EENS_j`、上下标和求和下限必须完整显示。

## 15.2 一致性

- 标题：Title Case；
- 章节标题：IEEE 模板格式；
- `Fig. 1.`、`Table I` 格式统一；
- 表题置于表上方，图注置于图下方；
- `K=20`、`R=2.0` 等数学量用数学字体；
- 单位前留空格：`6 MW`、`114 MWh/yr`；
- `CNY/yr` 全文统一；
- 数值范围使用一致的短横线或集合表示，不混用乱码长横线。

## 15.3 两页约束下的压缩顺序

若补充形式化表达后超过两页，按下列顺序压缩：

1. 删减重复的自然语言，而不是缩小字体；
2. 用集合定义替代多句重复约束说明；
3. 缩短引言中的一般性背景；
4. 压缩 Conclusion，不删除关键结果；
5. 裁剪图 1 白边；
6. 不得将正文或参考文献字体缩小到明显低于模板标准；
7. 不得通过负行距造成公式截断。

---

# 16. 最终验收标准

Agent 修改完成后，逐项打勾并输出检查结果。

## 16.1 老师批注验收

- [ ] 标题已体现 county-level 110-kV grid；
- [ ] 摘要不再使用 `grids bidirectional`；
- [ ] `reverse power flow`、`supply adequacy` 术语已修正；
- [ ] `This study` 已统一；
- [ ] 已消除 `per-station` 歧义；
- [ ] synthetic county 已解释为 public-data-informed；
- [ ] EENS 首次出现已有全称；
- [ ] `PV-dense` 和 `reverse-power pressure` 已替换；
- [ ] 正文统一使用 `non-dominated`；
- [ ] N-1 与 EENS 的关系表述准确；
- [ ] WarmStartSampling 已形式化；
- [ ] RepairProjection 已形式化；
- [ ] 已说明修复失败后的处理方式。

## 16.2 科学内容验收

- [ ] K 已定义为 110-kV 变电站数量；
- [ ] \(T_j\) 已定义或删除；
- [ ] D、N、G 已定义；
- [ ] HV 是 mean/median/best/final/converged 中的哪一种已明确；
- [ ] 三次独立运行的汇总口径已明确；
- [ ] 84 generations 与评价次数比例已核验；
- [ ] 13.1%、4.8%、188.82、114 与正文、表格、图一致；
- [ ] 储能不作为 N-1 firm capacity 的假设已明确；
- [ ] 所有新公式与实际代码逻辑一致。

## 16.3 引用验收

- [ ] 当前文献 [4] 已删除；
- [ ] 参考文献已连续编号为 [1]–[8]；
- [ ] 所有正文引用编号已更新；
- [ ] 无未引用文献；
- [ ] 无引用不存在的编号；
- [ ] 文献 [1] 信息已补全；
- [ ] 正式文献题名未被错误改写。

## 16.4 视觉验收

- [ ] 总页数仍为 2 页；
- [ ] 两栏没有重叠；
- [ ] 式（1）–（5）均完整；
- [ ] 式（5）顶部没有裁切；
- [ ] 无 `\(`、`\)`、`\{` 等残留；
- [ ] Algorithm 1 的 `∪` 正确；
- [ ] 图 1 数字和色条可读；
- [ ] 表 I 数字、列名和横线完整；
- [ ] 参考文献没有超出页边界；
- [ ] 导出的 PDF 中无乱码、缺字和字体替换。

---

# 17. Agent 最终输出要求

修改任务完成后，Agent 应提交：

1. 修订后的 `.docx`；
2. 用该 Word 导出的校核版 `.pdf`；
3. 一份简短变更日志，按以下格式：

```markdown
## 已完成
- 标题：……
- 摘要：……
- 老师批注 1–15：均已处理
- 公式：重建式（1）–（5）
- 算法：……
- 参考文献：删除原 [4]，全文重排为 [1]–[8]

## 需作者确认
- 修复后仍不可行个体的真实处理方式：……
- T_j 的实际定义或是否删除：……
- 表 I 数值的统计口径：……
- 84 generations 的评价次数计数方式：……

## 版式检查
- 页数：2
- 公式截断：无
- 引用编号：通过
- 图表可读性：通过
```

---

# 18. 可直接交给 Agent 的执行提示词

```text
请读取老师批注稿 PDF 和当前 Word 修订稿，严格按照《论文第二轮高精度修正说明书（供 Agent 执行）》进行修改。

硬性要求：
1. 删除当前参考文献 [4]（M. Nicolini 的给水网络论文），并更新全文所有引用编号；
2. 不得修改未经原始结果核验的实验数值；
3. 删除“grids bidirectional”等概念歧义表达；
4. 正文统一使用 non-dominated；
5. 将 WarmStartSampling 和 RepairProjection 改为与真实实现一致的形式化表达；
6. 定义 K、D、N、G，并处理未定义的 T_j；
7. 重建式（1）–（5），清除 LaTeX 定界符残留，修复式（5）裁切；
8. 修复 Algorithm 1 第 8 行并集符号；
9. 明确表 I 的三次运行统计口径和 HV 口径；
10. 修改后重新导出 PDF，逐页检查，保持 IEEE 双栏两页版式。

对无法从论文或代码确认的技术细节，不得虚构；在变更日志的“需作者确认”中单独列出。
```

