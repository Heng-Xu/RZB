# 修订日志 — 老师意见 v3 轮（2026-07-14）

**依据：** ① PDF 批注 28 条（`许恒-Engineering-Prior-Guided…Penetration.pdf`）② 会议纪要（`许恒预定的会议-元宝纪要.txt`）③ 术语修正说明书（`论文术语修正说明书.md`）。逐字句说明书见 `老师修改意见_逐字句修正说明书.md`。

**内容源：** `paper/历史/build_paper_docx.py`（原文件已备份 `build_paper_docx.py.bak_20260714`）。
**产物（均已生成+核验）：**
- `paper/epg-nsga-ii-paper_revised_v2.docx`（IEEE 双栏，3 页）
- `paper/epg-nsga-ii-paper_revised_v2.pdf`（libreoffice 转，3 页，逐页目检通过）
- 图 `实验/有EA/results/figures/fig1_matrix.{png,pdf,svg}` 已重出（仅换轴标签，数据不变）

---

## A. 四项决策（本轮已采纳）

| 决策 | 采纳口径 |
|---|---|
| Elastic → **Differentiated** | 标题/方法/贡献/结论/图轴全稿改用 differentiated；引言加一句 differentiated CLR 定义（含 CLR=计划主变容量/预测峰荷 分子分母）作桥接 |
| 热启动命名 | **保留 Warm-Start Sampling**（Feasibility-Preserving），未采纳术语文档 §10.1 的 "problem-informed initialization" 改名 |
| K=20 主算例 | **保留 K=20 承载降本/Fig.1**，III-C 加"代表性县域规模"说明句；摘要改成 **K=10–40 趋势/峰值**叙述（消除"选择性列举 20/40 跳 30"）。**未重跑实验** |
| 交付形式 | 干净 docx + PDF + 本修订日志 |

**K=20 现实性依据（内部，不入正文/暂不引用）：** 徐州睢宁县实测 110 kV 变电站 11 座（《睢宁热电联产规划 2017-2020》），按 5%/年规划口径推到规划年≈14-15；更发达县/县级市（沛县/邳州/新沂）更多 → 徐州一般县域 110 kV 站数量级"十几到二十几"。**K=20 = 徐州发达县代表性规模，K=10–40 覆盖小县→大县级市。** 正文用软性"representative county size"，未写县名、未加引用（发表前再补文献）。

---

## B. 逐处修改（原 → 新）

### 标题
- `…for Elastic Capacity-Load Ratio Planning under High Distributed Photovoltaic Penetration`
  → `…for Differentiated Capacity-Load Ratio Optimization in County-Level 110-kV Grid Planning under High Distributed PV Penetration`
  〔批注#1 加 110kV 电网主体；会L32/35/42；术§13.1〕

### 摘要（整段重写）
- `High-penetration distributed PV` → `High penetration of distributed photovoltaic (PV) generation`〔批注#2/#12，术§6.2〕
- `challenges fixed capacity-load ratio planning in county 110 kV grids by introducing reverse power and changing N-1 supply risk` → 拆句：`…a uniform capacity-load ratio (CLR) over-invests… while under-constraining reverse power flow…, and transformer capacity must still preserve supply adequacy under N-1 contingencies`〔批注#3/#4"断句/术语检查"，会L23；术§7/§8〕
- `This paper` → `This study`〔批注#5/#11，会L45〕
- `elastic per-station planning model` → `multiobjective planning model that coordinates multiple 110-kV substations within a county and jointly optimizes differentiated capacity-load ratios and storage power ratings`〔批注#6"逐站?"，术§4/§9〕
- `annualized cost index` → `annualized cost`〔批注#8，术§11.1〕；`under equal EENS` → `at the same EENS level`〔术§11.2〕
- `EENS` 首现加全拼 `expected energy not supplied (EENS)`〔批注#10，会L25，术§8.4〕
- `synthetic county case` → `public-data-informed synthetic county test system`〔批注#7/#19"生成的?"，术§11.4〕
- `comparable hypervolume … than plain NSGA-II` + `K=20…K=40` 跳选 → **K=10–40 趋势**：`converged normalized hypervolume rises from near-parity at small K to +4.8% over standard NSGA-II at K=40 … about 9.5× fewer evaluations`〔批注#8/#9/#26，会L16/51，术§10.4/§11.3〕
- Index Terms → `Capacity-load ratio, distributed photovoltaic generation, multiobjective optimization, reverse power flow, substation planning.`（去 storage planning）〔术§16〕

### 引言
- `High-penetration distributed PV … increasingly bidirectional` → `High penetration of distributed PV generation … into bidirectional networks`〔批注#12，会L52〕
- `causing reverse power and changing the N-1 supply margin` → `causing reverse power flow and supply adequacy under N-1 contingencies shifts with net load`〔批注#14，术§7.3/§8〕
- `failing to reflect reverse-power pressure at PV-dense stations` → `under-constrains reverse power flow at substations with high distributed-PV penetration`〔批注#15/#16"引发困惑"，会L13，术§7.3/§12〕
- `rigid or empirical rules` → `fixed or empirical rules`〔批注#16，术§4〕
- `This paper proposes` → `This study proposes`；`non-dominated` → `nondominated`〔批注#5/#17，术§17.1〕
- `warm start … repair projection` → `feasibility-preserving warm start … constraint-ordered repair projection`
- **新增 differentiated CLR 定义句**（术§15 要求；解决批注#18"elastic/N-1 奇怪"）
- 贡献 `elastic capacity-load ratio model with … N-1 constraints` → `multiobjective model with differentiated capacity-load ratios under an aggregate-CLR band and reverse-power-flow constraints and an EENS-based supply-adequacy objective under N-1 contingencies`〔批注#18，术§8.2〕
- `synthetic county case` → `synthetic county test system`〔批注#19〕

### II 方法
- 小节标题 `A. Elastic Capacity-Load Ratio Model` → `A. Differentiated Capacity-Load Ratio Model`
- `per-station capacity-load ratio and storage` → `capacity-load ratio and storage power rating of each substation`〔批注#6〕
- `regional capacity-load ratio` → `load-weighted aggregate capacity-load ratio`（**δ 保留**，仅措辞）〔术§12；红线1〕
- naked `reverse power`/`reverse-power constraints` → `reverse power flow`/`reverse-power-flow constraints`（式(3)(5) 相关）〔术§7〕
- **II-B WarmStartSampling 散文形式化**（批注#24"公式？更形式化"）：`samples each ratio R_j within [1.2,3.0], projects the aggregate ratio into band (4), and allocates storage … in descending order of residual reverse-power-flow pressure r_j⁰/(R_j L_j^p)`
- **II-B RepairProjection 对称形式化**（批注#25 与#24 同一句批注，故等量处理）：`clips each ratio to [1.2,3.0] and each storage rating to [0,6] MW … rescales into band (4) … enforcing the residual reverse-power-flow gate (5) … re-checks band (4)`——显式给出界/带(4)/闸(5)交叉引用，与 #24 平衡
- Algorithm 1 `non-dominated` → `nondominated`〔批注#17〕

### III 实验 + Table I（任务3）
- **Table I 已是 5 行、归一到 standard NSGA-II=1.000**（NSGA-II/NSGA-III/Warm-start-only/Repair-only/EPG-NSGA-II），与 `make_table1_full.py` 的 `TAB_ROWS` 一致 → 任务3 达成（老师 PDF 里的旧 3 行 EPG=1.000 表已被替换）
- 全稿 `plain NSGA-II` → `standard NSGA-II`〔批注#26，术§10.4〕
- SETUP `synthetic county` → `synthetic county test system`
- 描述段 EFF：按 NSGA-II=1.000 基线（+0.7%@K10→+4.8%@K40；repair-only 主驱动；warm-start 早期加速；NSGA-III 弱基线）；K=40 约 84 代≈9.5×〔术§11.3〕
- III-C：加 **K=20 代表性规模句**；`regional capacity-load ratio 1.80`→`load-weighted aggregate…`；`annualized cost index`→`annualized cost`；`high generation-to-load stations`→`substations with high generation-to-load ratios`；`regional coincident ratio 2.35`→`load-weighted aggregate ratio 2.35`；`elastic band/planning`→`planning band/differentiated planning`；`at equal EENS`→`at the same EENS level`
- Fig.1 caption `Elastic planning configuration … per-station ratio R` → `Differentiated planning configuration … station capacity-load ratio R`；**图轴 colorbar `per-station ratio R` → `capacity-load ratio R`**（重出图，数据不变）

### IV 结论
- `elastic capacity-load ratio planning … lower cost index under equal EENS and improved search efficiency compared with plain NSGA-II` → `feasibility-preserving warm start and repair projection reduced annualized cost … at the same EENS level, and improved the converged hypervolume over standard NSGA-II … reaching +4.8% with about 9.5× fewer evaluations at K=40`〔术§11.1/§11.3/§18 禁 unquantified "improved efficiency"〕

---

## C. 三条红线（守住，未越界）

1. **δ 保留** 于式(4) 聚合容载比（δ=0.85 县同时率）——只改措辞为 "load-weighted aggregate"，δ 未删。去 δ 会击穿拐点下界并需全套 EA 重跑（`paper-v2-delta-decision` 记忆）。
2. **数字诚实**：13.1%（K=20，`ea_baseline.csv`）、+4.8%@K40 HV、9.5× 更少评估、maxR*1.96、聚合 R 1.80/2.35 全部沿用真值，无重跑、无编造。
3. **无夸大**：differentiated 有定义；warm-start 命名保留经老师锁定名；K=20 用软性代表性表述、不宣称真实徐州县案例。

---

## D. 未采纳 / 待定 / 残留

- **术§10.1 warm-start → problem-informed initialization：未采纳**（用户决定保留 Warm-Start Sampling 命名）。
- **术§10.2 repair projection → feasibility-repair operator：部分**——算子名保留 `RepairProjection`，但正文以 "constraint-ordered … feasibility preservation" 表述其性质（与锁定名 Constraint-Ordered Repair Projection 一致）。
- **新增参考文献：未加**（用户要求发表前再补；K=20 代表性规模的文献支撑已备好：徐州睢宁 11 座 / MDPI Electronics 2025 区域电网 12 座 / 苏北 County A ~1.2–1.5 GW）。
- **摘要偏长**（~160 词，含 3 结果：降本/HV 趋势/效率）：如版面吃紧可压到 ~150 词（先删效率子句）。
- **可选后续**：若老师坚持"降本也上大规模"，需重跑 `ea_baseline@K=40` + 重画 40 站 Fig.1（本轮按"保持 K=20 + 改叙述"处理，未做）。
- **标题排版**：紧凑版标题在 24pt 下换 4 行、"Penetration" 单独成行（轻微孤行，可接受；若要消除可再缩题）。

---

## E. 终审微调（advisor 复核后）

1. **#24/#25 对称**：批注#24、#25 是**同一句批注**分别写在 WarmStartSampling 与 RepairProjection 两段并列句上。首轮只形式化了 #24；复核后把 III_C(RepairProjection) 也等量形式化（显式界 [1.2,3.0]/[0,6] MW + 带(4) + 闸(5) 引用），两处对称，避免老师看到"一段给了公式、一段没给"。
2. **摘要 9.5× 主语对齐**：摘要原写 "its warm start reaches … 9.5× fewer evaluations"，但正文 84 代/9.5× 是在**完整方法 EPG-NSGA-II** 上测得。改摘要为 "…and **it**(=EPG-NSGA-II) reaches …"，与正文主语一致（热启动是早期加速器的定性仍在正文 EFF 第二段）。
3. 均已重编 + 逐页目检确认。
