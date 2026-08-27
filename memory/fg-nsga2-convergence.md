---
name: fg-nsga2-convergence
description: MIND 2026 EA轨 FG-NSGA-II（Feasibility-Guided NSGA-II）县级多站容载比弹性寻优——收敛扫描的应用结果 + 速度/质量/消融定论（2026-07-03，run beyb8rsgp）
metadata:
  type: reference
---

# FG-NSGA-II 收敛实验：应用结果 + 速度/质量/消融定论

> 这是 **MIND 2026 EA 轨**（≠ 无EA/山东电力轨；见 [[project-state]] 的旧态）的当前权威结果。
> 工作目录 `实验/有EA/`；数据源 `实验/有EA/results/`，全部来自单进程收敛扫描 **run `beyb8rsgp`（2026-07-03，17.4h，12核）**，时间戳一致。

## 方法命名（锁定）
- **所提方法 = `FG-NSGA-II`（Feasibility-Guided NSGA-II）** = 经典 NSGA-II + **可行性修复算子** + **可行热启动**（照 CNSGA-II 命名法；"可行性引导"统摄两组件）。全文/图/表/代码统一此名（代码内部变体键 `fg`）。
- baseline：经典 NSGA-II（`classic`）、NSGA-III（`nsga3`，das-dennis，预算严格相等）。消融变体：`repair_only`（仅修复）、`warmstart_only`（仅热启动）。
- **约束是"处理"非"求解"**：物理模型判定 G；修复=直接近似可行化投影（非数学投影、不调 compute）；EA=可行性优先选择压力。

## 统一收敛扫描（ea_converge.py，运行级并行 10 worker）
- Part A：5 变体 × 4 K{10,20,30,40} × 3 seed，跑到收敛（classic/nsga3 gen800，fg/消融 gen400），逐代 HV → `ea_converge.csv`（33600 行）。
- Part B：K=20 收敛应用变体 E3(4带)/E6(6县)/E7(4×R₂₂₀)；K=20 fg 那一跑产出 E1 前沿+一站一策+E2b。
- Part C：E2 验证 / E4 规模（口径不变）。
- **单写入者铁律**：results/ 同时只允许一个写入进程；曾因两后台并发写同批文件而污染，重跑修复。**TaskList 不列后台 bash；"exit0 但输出空"可能仍在跑。**

## 应用结果（FG-NSGA-II，K=20 收敛）
- **E1**：Pareto 100 点；拐点 f₁=**18882 万/年**、f₂=**114 MWh**、聚合容载比=**1.80**。
- **一站一策**：**11 站配储为主 / 9 站低容载比+强联络 / 0 站需 R>2.0**（最大 R\*≈1.96）；高源荷比→配储，低源荷比→低容载比无储。印证"向下弹性、配储替代增容"。
- **E2b（头条应用）**：全县刚性 2.0 = 21836 万 → 同风险 FG = 18986 万，**省 13.1%**（收敛口径；此前 pop100/gen200 为 12.9%）。
- **E6 鲁棒**：6 县 **12.1%±1.3%… 收敛后 12.3%±1.3%、范围[10.1,13.7]、全为正**。
- **E7 系统约束**：加约束成本下限 Δ≈+25 万（<0.3%）→ **本合成县近乎不绑定**（±噪声内，符号会翻），如实记录。
- **E2 验证**：小 K 增强+经典 HV比≈1（parity）→ 求解器达真前沿。**E4**：穷举 K=8=1.38e11、K≥12 不可枚举，NSGA-II 近线性 → EA 必要。

## 算法定论（★ 速度 vs 质量 vs 消融——写论文按此，诚实）
- **头条（公平、无关预算点）**：**FG 用一半预算（gen400）就胜过 classic/NSGA-III 的 gen800**（每个 K 都是）；等价地 **FG 用 ~5–12× 更少代数达 baseline 800 代收敛质量**（K=40：classic 84 代→9.5×，NSGA-III 68 代→11.8×）。
- **以效率为主（预算无关度量）**：效率＝**iso-quality 加速比**（FG 达 baseline gen800 收敛质量所需代数，~5–12×，见上"头条"）；**不采用任意固定预算点**（曾用 gen100 的 1.355× 作头条，已弃——是曲线上任意一刀、易被挑）。**充分收敛后 baseline 大体追平** → 收敛 fg/classic 仅 1.007→1.048、fg/NSGA-III 1.009→1.064（fig_front_compare 前沿叠加图已弃：收敛近平价、可视化弱，效率用收敛曲线+加速比+收敛HV表即可）。
- **收敛质量边际（精确）**：fg/classic 收敛比 **K≤30 都 <1%，到 K=40 才跳到 4.8%**（非平滑增长；就 K40 一点显著，且 std~0.5% 内可信）。
- **消融（两组件都保留、各有定位）**：
  - **修复 = 主驱动**：`repair_only ≈ fg`（收敛处处相等；K=40 都 +4.8% vs classic）。
  - **热启动 = 早期加速器**：gen100 处 `fg/repair_only`=1.003→**1.023**（随 K 增），`warmstart_only` 早期即超 classic（K40 +4.6%）；**但收敛后洗掉**（收敛 warmstart_only ≈ 甚至略低于 classic）。→ 热启动加速早期收敛、不改终极最优。
- **诚实框架**（应用为主）：算法故事＝"**有限算力下 FG 达更优前沿、省 5–12× 代数，优势随规模放大（效率）**；修复是驱动、热启动加速早期"；**明确交代"充分收敛后 baseline 大体追平"**——这份诚实堵死"把 baseline 多跑就翻盘"的审稿风险。应用结果（省 13.1%、一站一策）扛论文主线。

## 文件与复现
- 代码 `实验/有EA/scripts/`：`county_model.py`、`ea_county.py`（`run_nsga2`/`run_nsga3`/`run_nsga2_enhanced`(=fg)/`run_repair_only`/`run_warmstart_only`）、`ea_converge.py`（并行收敛扫描 + 组装）、`ea_figures.py`。
- 结果 `results/`：`ea_converge.csv`(逐代HV) + `ea_converge_termgen.csv` + 应用 CSV（pareto/strategy_knee/baseline/band_effect/robustness/system_constraint+fronts/validation/scaling）；`figures/` 7 图（county_pareto/strategy/scaling/band_effect/system_constraint/scaling_gap/enhanced_convergence）——**投稿级**：PDF 矢量 + 600dpi PNG 双出，Liberation Serif（Times 度量）+ Okabe-Ito 色觉友好，`pdf/ps.fonttype=42`（Type-3 已排除，pdffonts 验证），图内标题由 `ea_figures.py` 的 `SHOW_TITLE` 开关（投稿置 False）。**render-only 重制不改数**（2026-07-03 复核：scaling_gap 6.6/4.8/5.3/9.5× 与 7.5/9.1/11.1/11.8×、strategy 11/9/0 R\*max1.96、pareto knee 18882/114 均未漂移）。
- **标准重跑（勿并发）**：`cd 实验/有EA/scripts && python3 -u ea_converge.py && python3 -u ea_figures.py`（smoke：`ea_converge.py smoke`）。~17h/12核。
- 论文规划：`paper/01_论文大纲_中文_v1.md`（逻辑线：结构=经典失效之因=FG之用；含"写作/排版规范·对齐MIND范文" + "图表清单与要求·4图2表"两节）+ `paper/02_图表与实验补全方案.md`；全面分析 `分析/10_项目全面分析_背景方法建模实验结果.md`。对标范文 md 在 `分析/md_cache/参考文献/对标期刊/`（长篇 Water MOGA 为主骨架）。
- **交付脚本（2026-07-03）**：① 组会 PPT `report/06.26/make_mind_ppt_0626.py`→3 页、算法创新为核心（框架+创新点｜对比图fig_scaling_gap+收敛HV对比表｜应用），对比表/鲁棒从 CSV 动态读防漂移；② Word 大纲 `paper/build_outline_docx.py`→`paper/徐州110kV容载比_MIND2026大纲_XH.docx`（**作者XH**、单栏骨架、附录落 Fig.2/3/4 PNG + Fig.1 占位&绘图要求 + Table I/II 动态数据、三线表）。**docx 用 PNG（不能嵌 PDF）；图路径=有EA/results/figures。旧 `paper/build_sd_docx.py` 是无EA山东电力全文脚本，勿混用**。
- 陈旧数警戒（曾埋在旧 PPT）：K=10/pop120/gen300、省12.3%当头条、旧HV 117906单点、"NSGA-II"命名——全为旧轨；正确=K=20主算例、省13.1%头条（12.3%±1.3%是6县鲁棒均值、非头条）、收敛HV对比表+加速比、FG-NSGA-II命名。

相关：[[project-state]]（无EA/山东电力旧轨）、[[experiment-model-design]]（Z4-LCC 仿真器）、[[paper-writing-plan]]。
