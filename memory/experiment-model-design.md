---
name: experiment-model-design
description: 双向Z4-LCC仿真器的模型设计、关键参数、四轮修复史（含v4承重缺陷修复）、复现方法与易错点
metadata:
  type: reference
---

# 实验模型设计（实验/scripts/）

## 模型本质
公开数据双轨制：论文用 IEEE33-bus + PVGIS实测气象（A轨），主报告用甲方数据（B轨）。
核心是 `lcc_simulator.py` 的双向Z4-LCC全寿命周期成本（年费用法，Z1-Z5）。
**论文主对比（v4起）= 决策方法（候选R∈{1.5,1.8,2.0,2.3,2.6}逐档取最小LCC）vs 刚性R=2.0**，
统一候选构造走 `sweep_experiments.build_candidate()`，决策矩阵27格同口径逐格选优。

## 四轮修复史（重要——勿回退）
- **v1（作废）**：PV未进潮流、增容免费、循环论证——"弹性恒优"是假设的同义反复。
- **v2**：F1 PV真实注入潮流 / F2 Z1补低容量档+扩容系数0.6 / F3 弃光惩罚 / G4 场景要素归位 / 口径拆分源荷比vs电量渗透率 / AHP改Saaty整数标度(CR=0.012)。
- **v3（过度声称，已被自身输出否证）**：X1触发式/X2主变损耗/X4 VOLL/X3联络度。**但**：主图实为固定2.0vs2.3（从不调用决策矩阵）、X4在默认参数下恒0、弃光重复计损、X3退化(中=强)。详 `分析/06`(原)+`分析/07`(复核)。
- **v4（当前，2026-06-15，对应 分析/07 独立复核）**：
  - **G0**：`sweep_penetration` 改为"自适应R(决策矩阵)vs刚性2.0"——主图首次真正检验"一片一策"。`sensitivity_analysis` 同步改自适应口径。
  - **bug#1**：`compute()` 先算弃光，反向馈线+主变潮流扣 curtailed_kw 并封顶反向限额，消除对弹性方案高渗透成本虚高。
  - **X4**：`_reliability` 对**未来峰荷** peak×(1+g)^n 校核（非现状峰荷）→低R在负荷增长后N-1不足→付代价（v3恒0问题解决）。
  - **X3**：联络度CD经 cd×峰荷 N-1转供项 + (1+g)^n 共同产生梯度（弱2.3/中1.8/强1.5）。
  - X2 主变损耗保留不变。

## 核心结论（v4，诚实版；详 实验/03、分析/07）
- 刚性单值2.0系统性次优；决策方法相对2.0节省 **2-4%**（物理可解释、复现确定）。
- 🟢 **升方向稳健**：高渗透→R≥2.3（15/15 g×n组合成立，反送/弃光驱动，与负荷增长无关）。**论文承重腿、真·DG现象。**
- 🟠 **降方向条件性**：低渗透下探floor随负荷增长g与N-1假设在{1.5,1.8,2.0,2.3,2.6}漂移——**不可声称固定1.8**。本质是N-1主变定容问题，与高渗透DG弱相关→作条件性次要发现。
- 区域三地（徐州/嘉兴/莱芜）最优R均1.8（同源荷比），气候改变反送暴露量级而非R；真实长反送(~3000h)下升方向落到"1.8+配储"而非升R2.3（t_rev-PV耦合，主图用1362h）。

## 关键模型常数（论文需声明）
- **负荷增长 g=5%/年、校核年限 n=5年**（v4新增，降方向floor的关键敏感量，须做g×n敏感性）
- N-1等效缺供 90h（FOR≈0.0103），n1_overload_factor=1.0（单台不计短时过载，最不利口径；真实~1.3×会恢复降弹性）
- 主变 P0=0.0007、Pk=0.0045 kW/kVA（SZ11级）；VOLL 15元/kWh；反向限额0.85；弃光形状0.5；α_rev=1.2
- PVGIS徐州：1396 kWh/kWp/年、容量因子15.9%；储能按反送超限量触发；扩容系数0.6

## 易错点（修改前必读）
- `_reliability` 用**视在容量口径**(peak_mva)，且**对未来峰荷 peak×(1+g)^n 校核**（v4）；判R付代价(cd=0.45,2台,factor=1)解析判据：`R < 2·((1+g)^n − cd)`。
- 降方向floor与X3梯度坐落在该判据的不连续点上→对(g,n)极敏感，任何降方向结论必须配 `sensitivity_growth.py` 的g×n扫描，**勿单点headline**。
- 现状/未来口径混用：主变容量与矩阵分档轴按现状峰荷，N-1按未来峰荷——规划简化，论文须显式声明。
- `make_plan_a/make_plan_b` 与 `lcc_simulator --compare` 是**遗留单点对照(固定2.0vs2.3)**，勿用于论文结论（已加运行时警告）。

## 复现命令
```bash
cd 实验
python scripts/sweep_experiments.py --out results     # 自适应主图+27格矩阵+pv_tx
python scripts/ahp_robustness.py --out results        # AHP CR=0.012, ±20%鲁棒
python scripts/sensitivity_analysis.py                # 折现率×储能45组合 → fig7
python scripts/sensitivity_growth.py                  # 负荷增长g×n → fig9（v4新增,最关键）
python scripts/regional_cases.py                      # 徐州/嘉兴/莱芜最优R+反送时长 → fig8
python scripts/generate_figures.py                    # fig1-6 + 3表（AR PL UMing CN中文字体）
```

## 产物
- `results/`：sweep_penetration（自适应vs刚性2.0）、decision_matrix_raw（27格）、sweep_pv_tx、sensitivity_econ、**sensitivity_growth（v4新增）**、regional_cases、ahp_robustness_results
- `results/figures/fig1-9.png`（**fig9=负荷增长敏感性**）、`results/tables/tab1-3.csv`
- `results_v3_stale/`：v3旧结果备份（溯源对比）
- 关系见 [[project-state]]、[[paper-writing-plan]]

## 反向承载力校核准入闸（v5，2026-06-25，甲方认可）
把反向承载力校核做成**准入硬闸**：只有过校核的容载比方案才进 LCC 比选与一片一策。**矫正了建模算法根因**——旧选优纯 `min(年化成本)` 无硬闸，且治理在R上自动不对称（储能↔低R、弃光↔高R），任何施于"已治理方案"的硬闸都反转升方向。三处修正：
- **判据=裸主变反向重载**（reverse≤0.85×R×峰荷，不计治理、不靠弃光救；2025导则口径），对R单调区分。
- **配储改显式独立方案 `build_storage_plan`（方案A）**，恒可行参与比选；`build_candidate` 改为**纯主变**（去掉自动配储/弃光）。两阶段选优 `select_by_gate`：纯主变各R过硬闸→幸存者+配储→min-LCC。
- **电压=片区级旗标**（R无关，不参与R准入）；IEEE33弱馈线抬压是阻抗假象，非徐州真实值，仅方法演示，待Phase2用实测R/X。
- 新结论：源荷比<1.9→纯主变R1.5(降,经济)；1.9–2.7→**推荐R=承载力下限R_min**(1.8→2.6,升方向变物理硬约束)；>2.9→刚性2.0+配储。27格中高源荷比9格全配储、电压旗标18/27。
- **caveat**：取代03文档§2.1/§2.2纯经济headline；现稿paper/01基于校核前v4、需按 `paper/校核版_正文对齐清单.md` 对齐(§3校核准入/§3.2上探2.6+极高配储/§3.6/去弃光治理/节省0~4.65%)。
- **regional_cases已重设计为反送时长扫描**(fig8)：固定源荷比≈2.56(PV=9500,R_min=2.6),扫t_rev比"升容载比R2.6增容"vs"刚性2.0+配储",**翻转点t_rev≈2300h**(短增容/长配储);三地实测(徐州3017/嘉兴2841/莱芜3103h)均>2300h→均配储,坐实创新3。PV=11000(源荷比3)会被承载力一刀切掩盖机理。新产物 `regional_trev_sweep.csv`。
- 新件：`lcc_simulator.reverse_voltage_max_pu/assess_reverse_capacity`、LCCResult加 `reverse_check_passed/reverse_overload_kw/max_reverse_voltage_pu/voltage_exceed/curtail_ratio`；`results/reverse_capacity_check.csv`、`fig10_reverse_capacity.png`；yaml `reverse_check.voltage_limit_pu`。复现：`sweep_experiments.py --what all`（含 check）+ 重跑 ahp/regional/generate_figures。
