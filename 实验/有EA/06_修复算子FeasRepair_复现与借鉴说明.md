# 可行性修复算子 FeasRepair —— 复现 / 借鉴说明（可直接交给 AI 实现）

> 本文件自包含：读完即可（1）**原样复现**本项目的修复算子，或（2）**迁移借鉴**到别的「强约束 + 大规模 + 评价昂贵」的多目标进化优化问题。
> 面向执行者 = AI Agent。文末附「给 AI 的任务指令模板」与「验收标准」。
> 事实源：`实验/有EA/scripts/ea_county.py`（`_repair_one` / `FeasRepair` / `WarmStartSampling` / `run_nsga2_enhanced`）、`county_model.py`（常量与物理量）、`lcc_simulator.py`（反送常量）。pymoo 0.6.1.x。

---

## 0. 一句话

在 NSGA-II 每一代对**不可行个体做一次前向、闭式/贪心的"近似可行化投影"**：按约束优先级依次修，**先动便宜的执行变量（储能 P）、后动结构变量（容载比 R）**，**全程不调用目标函数**（不占评估预算），残余越限交给 pymoo 的约束支配（constraint-domination）兜底。这一个算子是 FG-NSGA-II 相对经典 NSGA-II 提速 ~5–12× 的**主驱动**（热启动只是早期加速器）。

---

## 1. 什么时候值得借鉴（适用判据）

同时满足越多、收益越大：

- **强约束、可行域稀疏**：随机初始化/变异后大多数个体不可行；惩罚法要么调参困难、要么把搜索卡在边界。
- **规模大**：决策维度随实例增大，随机"撞进"可行域的概率指数下降（本项目：站数 K↑ → 经典 NSGA-II 前期几乎全不可行、收敛慢）。
- **约束可解析/可闭式投影**：给定一个不可行解，能用**领域知识**低成本地算出"最近的近似可行解"（不必最优投影，够用即可）。
- **评价昂贵**：目标函数是仿真/黑盒（本项目 `compute()` ≈3.8 ms/次）；修复**不调用**它，因此不消耗评估预算。
- **目标 vs 约束可分**：约束主要由部分变量决定，可与"优化目标"解耦地先满足。

不适用/收益小：约束本身就是目标的一部分、或没有便宜的可行化手段、或可行域本就宽松（随机初始化即可行）。

---

## 2. 核心思想（**可迁移的模式**，与本问题无关）

把"约束处理"当**处理**而非**求解**——三分：**判定**（problem 只算违反量 G）／**修复**（把解投影回近似可行）／**选择**（EA 施加可行性优先压力）。修复算子的可迁移配方：

1. **变量分层**：把决策变量分成
   - **执行变量（actuator，便宜、可自由增减、不破坏其它约束）** —— 本项目 = 储能功率 P；
   - **结构变量（structural，贵、牵一发动全身、决定关键耦合约束）** —— 本项目 = 容载比 R（同时决定"带"约束）。
2. **约束按"耦合范围"排序**，从全局到局部再回补：
   - 先修**全局耦合约束**（本项目：县聚合容载比带，由所有 R 共同决定）；
   - 再修**逐个体局部约束**（本项目：每站反送闸），**优先加执行变量、执行变量到顶再动结构变量**；
   - 再修**聚合型约束**（本项目：上级系统潮流，Σ反送 ≤ 限额），**只用执行变量**、从违反最大的个体开始贪心削减；
   - 最后**回补被裁剪破坏的全局约束**（升结构变量只朝"更满足局部/聚合约束"的方向，不反向破坏它们）。
3. **闭式/贪心、O(维度)、一次前向**：每步都是解析公式或单次贪心扫描，绝不迭代调用目标/仿真。
4. **允许近似**：修复不保证严格可行，残余违反由 EA 的约束支配（feasibility-first）收尾——所以修复只需"快而接近"，不需"精确投影"。
5. **保持多样性**：修复是"就近投影"（乘性缩放 / 局部增补），不把所有解拍到同一点；否则会损失前沿多样性。

> 记住这条经验：**执行变量先行、结构变量兜底；全局约束先修、聚合约束后修、破坏了再回补**。顺序错了会互相打架（例：先升 R 满足闸，会把聚合容载比顶出带）。

---

## 3. 本问题的决策 / 约束 / 常量（复现所需的全部定义）

**决策向量** `x = [R_1..R_K, P_1..P_K]`（K 个站）：`R_j` 站容载比，`P_j` 站储能功率(MW)。

**目标（min，越小越好）**：`f1` 县总年化成本(万元)、`f2` 县 N-1 缺供 EENS(MWh)。**修复不碰目标。**

**约束（G ≤ 0，共 K+2 或 K+3 个）**——见 `evaluate_county()`，全部**归一化到 O(1)** 再交 pymoo（否则 kW 与容载比量纲悬殊、CV 聚合会相互压制）：

| 约束 | 公式（归一化前的物理量） | 归一化 G |
|---|---|---|
| 逐站反送闸 ×K | `overload_kw_j`（站净反送超出主变反向许用的量） | `overload_kw_j / max(1, peak_j)` |
| 聚合容载比带·下限 | `agg_R = Σ(tx_j) / (diversity·Σpeak_j)` | `(band_lo − agg_R)/band_lo` |
| 聚合容载比带·上限 | 同上 | `(agg_R − band_hi)/band_hi` |
| 上级系统潮流（可选） | `Σ_j rev_up_j·η − L_rev` | `(…)/max(1,L_rev)` |

**关键物理量（`county_model.py` / `lcc_simulator.py`）**：
```
站净反向上送(kW):  rev_up_j = max(0, PV_PEAK_FACTOR*pv_kwp_j − REVERSE_LOAD_FACTOR*peak_kw_j − P_j*1000)
逐站反送闸限额(kW): lim_j    = REVERSE_TX_LIMIT * R_j * peak_kw_j
上级反向限额(kW):   L_rev    = REVERSE_TX_LIMIT * r220 * (DIVERSITY_FACTOR * Σ peak_kw)
聚合容载比:         agg_R    = Σ(R_j*peak_j) / (DIVERSITY_FACTOR * Σ peak_j)   # 修复内用 tx≈R*peak 近似
```

**常量（原样复现用这些值）**：
```
R_LO, R_HI          = 1.2, 3.0      # 站容载比上下界
P_LO, P_HI          = 0.0, 6.0      # 站储能功率(MW)上下界
DEFAULT_BAND        = (1.8, 2.2)    # 县聚合容载比带 [lo, hi]
DIVERSITY_FACTOR    = 0.85          # 县正向同时率
REVERSE_COINCIDENCE = 1.0           # 反向同时率（光伏齐发，保守取 1）
R220_DEFAULT        = 1.8           # 上级 220kV 容载比（None=关闭系统约束）
REVERSE_TX_LIMIT    = 0.85          # 主变反向负载限额（15% 裕度）
PV_PEAK_FACTOR      = 0.9           # PV 出力峰值系数（相对装机 pv_kwp）
REVERSE_LOAD_FACTOR = 0.3           # 春秋午间小负荷系数
```
`Station` 必需字段：`peak_kw`（站峰荷 kW）、`pv_kwp`（站 PV 装机 kWp）。

---

## 4. 修复算法（精确伪代码）

输入不可行解 `x=[R,P]`，输出近似可行 `x'`。四步，一次前向，**不调用 f1/f2**：

```
① 夹取 R∈[R_LO,R_HI]、P∈[P_LO,P_HI]
② 带（全局耦合，先修）：
     agg_R = Σ(R_j·peak_j) / (DIVERSITY_FACTOR·Σpeak_j)
     若 agg_R < band_lo:  R ← clip(R · band_lo/agg_R)     # 整体等比放大
     若 agg_R > band_hi:  R ← clip(R · band_hi/agg_R)     # 整体等比缩小
③ 逐站反送闸（局部，执行变量优先）：
     对每个 rev_up_j > lim_j 的站 j:
        P_j ← min(P_HI, P_j + (rev_up_j − lim_j)/1000)     # 先补储能吸收反送
        重算 rev_up_j；若仍 > REVERSE_TX_LIMIT·R_j·peak_j:
           R_j ← min(R_HI, rev_up_j/(REVERSE_TX_LIMIT·peak_j))  # 储能到顶才升 R
④ 上级系统潮流（聚合，只用执行变量）：  # r220 非 None 时
     L_rev = REVERSE_TX_LIMIT·r220·(DIVERSITY_FACTOR·Σpeak)
     excess = Σ rev_up · REVERSE_COINCIDENCE − L_rev
     按 rev_up 降序遍历站 j，excess>0 时:
        cut = min((P_HI−P_j)·1000, rev_up_j, excess/REVERSE_COINCIDENCE)
        P_j ← P_j + cut/1000;  excess −= cut·REVERSE_COINCIDENCE
⑤ 带下限回补（修 ② 里 R 触顶被裁导致的 agg_R 不足）：
     若 agg_R < band_lo 且存在 R_j<R_HI 的站:
        把缺额 (band_lo·denom − Σ(R·peak)) 均摊到这些站的 R（升 R 只帮闸/系统，不破坏它们）
返回 clip(R), clip(P)
```
> 顺序不可乱：③ 升 R 会抬 agg_R（可能顶破带上限，但带上限已在 ② 修过，升 R 只会让 agg_R 更靠上限侧，需 ⑤ 只在"下限不足"时回补、且回补也是升 R 同向）；④ 只加储能不动 R，故不破坏带与闸。

---

## 5. 完整源码（原样复制即可复现）

```python
import numpy as np
from pymoo.core.repair import Repair
from pymoo.core.sampling import Sampling
from pymoo.operators.sampling.lhs import LHS
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

# —— 常量（见 §3）——
R_LO, R_HI, P_LO, P_HI = 1.2, 3.0, 0.0, 6.0
DIVERSITY_FACTOR, REVERSE_COINCIDENCE = 0.85, 1.0
REVERSE_TX_LIMIT, PV_PEAK_FACTOR, REVERSE_LOAD_FACTOR = 0.85, 0.9, 0.3

def _repair_one(x, stations, band, r220):
    """把决策向量投影到(近似)可行：①缩R入带 ②逐站补储/必要时升R过闸 ③补储满足系统约束 ④带下限回补。"""
    k = len(stations)
    R = np.clip(np.asarray(x[:k], float), R_LO, R_HI)
    P = np.clip(np.asarray(x[k:], float), P_LO, P_HI)
    peaks = np.array([s.peak_kw for s in stations])
    pv    = np.array([s.pv_kwp  for s in stations])
    denom = DIVERSITY_FACTOR * peaks.sum()
    # ① 带：等比缩放 R 使聚合容载比 ∈ [lo,hi]
    aggR = (R * peaks).sum() / denom
    if band[0] > 0   and aggR < band[0]: R = np.clip(R * (band[0] / aggR), R_LO, R_HI)
    elif band[1] < 1e8 and aggR > band[1]: R = np.clip(R * (band[1] / aggR), R_LO, R_HI)
    # ② 逐站反送闸：先补储能，储能到顶仍越限再升 R
    rev = np.maximum(0.0, PV_PEAK_FACTOR * pv - REVERSE_LOAD_FACTOR * peaks - P * 1000.0)
    lim = REVERSE_TX_LIMIT * R * peaks
    for j in np.where(rev - lim > 0)[0]:
        P[j] = min(P_HI, P[j] + (rev[j] - lim[j]) / 1000.0)
        rev_j = max(0.0, PV_PEAK_FACTOR * pv[j] - REVERSE_LOAD_FACTOR * peaks[j] - P[j] * 1000.0)
        if rev_j > REVERSE_TX_LIMIT * R[j] * peaks[j]:
            R[j] = min(R_HI, rev_j / (REVERSE_TX_LIMIT * peaks[j]))
    # ③ 上级系统约束：Σrev·η ≤ L_rev，不足则给反送最大的站继续补储能
    if r220 is not None:
        L_rev = REVERSE_TX_LIMIT * r220 * denom
        rev = np.maximum(0.0, PV_PEAK_FACTOR * pv - REVERSE_LOAD_FACTOR * peaks - P * 1000.0)
        excess = rev.sum() * REVERSE_COINCIDENCE - L_rev
        for j in np.argsort(-rev):
            if excess <= 0: break
            cut = min((P_HI - P[j]) * 1000.0, rev[j], excess / REVERSE_COINCIDENCE)
            if cut <= 0: continue
            P[j] = min(P_HI, P[j] + cut / 1000.0); excess -= cut * REVERSE_COINCIDENCE
    # ④ 带下限回补（修 ① 里 R 触顶被裁造成的 agg_R 不足；升 R 只帮闸/系统、不破坏）
    aggR = (R * peaks).sum() / denom
    if band[0] > 0 and aggR < band[0]:
        room = R < R_HI - 1e-9
        if room.any():
            deficit = band[0] * denom - (R * peaks).sum()
            R[room] = np.clip(R[room] + deficit / peaks[room].sum(), R_LO, R_HI)
    return np.concatenate([np.clip(R, R_LO, R_HI), np.clip(P, P_LO, P_HI)])


class FeasRepair(Repair):                       # ← 每代对整个种群逐个修复
    def __init__(self, stations, band, r220):
        super().__init__(); self.stations, self.band, self.r220 = stations, band, r220
    def _do(self, problem, X, **kwargs):
        X = np.atleast_2d(X).astype(float)
        for i in range(len(X)):
            X[i] = _repair_one(X[i], self.stations, self.band, self.r220)
        return X


class WarmStartSampling(Sampling):              # ← 早期加速器（可选，非主驱动）
    """LHS 多样性 + 25% 注入「低R+0储」种子；全部经修复 → 初始种群即可行。"""
    def __init__(self, stations, band, r220):
        super().__init__(); self.stations, self.band, self.r220 = stations, band, r220
    def _do(self, problem, n, **kwargs):
        X = LHS()._do(problem, n).astype(float); k = len(self.stations)
        r_seed = max(R_LO, min(R_HI, self.band[0] * DIVERSITY_FACTOR)) if self.band[0] > 0 else R_LO
        for i in range(max(1, n // 4)):         # 25% 低成本可行种子
            X[i, :k] = r_seed; X[i, k:] = 0.0
        for i in range(n):
            X[i] = _repair_one(X[i], self.stations, self.band, self.r220)
        return X


def run_fg_nsga2(problem, stations, band, r220, pop=100, gen=400, seed=1):
    """完整 FG-NSGA-II = 经典 NSGA-II + 热启动采样 + 每代修复。"""
    algo = NSGA2(pop_size=pop,
                 sampling=WarmStartSampling(stations, band, r220),
                 repair=FeasRepair(stations, band, r220))
    return minimize(problem, algo, ("n_gen", gen), seed=seed, verbose=False, save_history=True)
```

**接线方式（pymoo）**：`NSGA2(..., repair=FeasRepair(...))` —— pymoo 会在**每代评价前**对新个体调用 `Repair._do`。`sampling=WarmStartSampling(...)` 只影响初始种群。其余（交叉/变异/非支配排序/拥挤度/约束支配）全用 pymoo 默认，**无需改动**。

---

## 6. 为什么这样设计（逐条，迁移时要保留的原则）

1. **不调目标函数**：修复只用解析式（rev/lim/agg_R），零仿真调用 → 修复几乎免费，评估预算全留给"成本↔风险"权衡搜索。**这是提速的关键**，务必保持。
2. **执行变量先行**：储能 P 能吸收反送而**不改 R、不动带**；R 是"贵且耦合"的结构变量，只在储能到顶后作兜底。迁移时先识别你问题里的"廉价执行变量"。
3. **约束按耦合范围排序 + 回补**：全局带 → 局部闸 → 聚合系统 → 回补带。次序错会互相破坏（见 §4 注）。
4. **近似即可**：修复后仍可能有残余违反（例如所有站储能都到顶仍超限），交给 pymoo 约束支配（feasibility-first 选择）淘汰——所以修复要"快"不要"全"。
5. **就近投影、保多样性**：带用**乘性等比缩放**、闸/系统用**局部增补**，不会把种群拍到一点。切忌把所有解投影到同一个"标准可行解"。
6. **约束归一化**：不同量纲的 G 先各自除以自身尺度到 O(1)，pymoo 的 CV=Σmax(0,G) 才不会被大量纲项主导（这属于 problem 侧，但和修复配套）。
7. **热启动是次要件**：只给初始种群一个可行高起点（早期加速），充分收敛后收益washout；**主驱动是每代修复**。消融已证：`repair_only ≈ 完整FG`，`warmstart_only ≈ classic`。

---

## 7. 如何迁移到你自己的问题（分步 recipe + 通用模板）

**Step 1 — 列清单**：写出所有可行性约束 `g_i(x) ≤ 0`；能解析算出违反量的才适合修复（黑盒约束不适合）。
**Step 2 — 变量分层**：把 x 分成「执行变量（增减便宜、只影响少数约束）」与「结构变量（贵、决定关键耦合约束）」。
**Step 3 — 约束排序**：按耦合范围排：全局/耦合最强的先修，逐个体次之，聚合型再次，最后回补被前面步骤破坏的。
**Step 4 — 每约束写闭式投影**：给定违反，用领域公式算"最小代价的可行化动作"（优先动执行变量）。
**Step 5 — 兜底**：残余违反交约束支配；problem 的 G 做归一化。
**Step 6 — 验证**：见 §8。

**通用模板（把 TODO 换成你的问题）**：
```python
def repair_one(x, ctx):
    x = clip_to_bounds(x, ctx)                 # 夹取变量界
    # ① 全局/强耦合约束：整体缩放结构变量使聚合量入可行区间
    #    TODO: agg = aggregate(x); if agg<lo: scale structural up; if agg>hi: scale down
    # ② 逐个体局部约束：执行变量优先，到顶再动结构变量
    #    TODO: for each violating unit: actuator += need; if still violating: structural += ...
    # ③ 聚合型约束：只用执行变量，从违反最大的个体贪心削减
    #    TODO: excess = sum(local) - limit; for unit in sorted desc: actuator += min(headroom, excess)
    # ④ 回补：修 ① 里因触界被裁而破坏的全局约束（只朝不破坏 ②③ 的方向）
    return clip_to_bounds(x, ctx)

class MyRepair(Repair):
    def _do(self, problem, X, **k):
        X = np.atleast_2d(X).astype(float)
        for i in range(len(X)): X[i] = repair_one(X[i], self.ctx)
        return X
# NSGA2(pop_size=..., sampling=LHS(), repair=MyRepair(ctx))   # 先只加修复，再考虑热启动
```

---

## 8. 复现与验证清单（做完打勾）

- [ ] **修复有效性**：随机/变异生成一批不可行解，过 `_repair_one` 后重算约束 → 绝大多数 CV≈0（残余小量交 EA）。
- [ ] **不占预算**：确认修复内**没有**调用目标/仿真（grep 无 `compute`/`evaluate` 调用）。
- [ ] **消融对照**（本项目关键证据，迁移后也应复现同型结论）：
  - `repair_only`（LHS + FeasRepair，无热启动）收敛 HV ≈ 完整 FG（本项目比值 0.997–1.000）→ **修复=主驱动**；
  - `warmstart_only`（WarmStart，无每代修复）早期超 classic、**收敛后 washout ≈ classic** → 热启动=早期加速器。
- [ ] **iso-quality 加速比**：让 baseline 跑到收敛（如 gen800），记其收敛 HV；测完整方法达到该 HV 所需代数 → 加速比 = 基线代数 / 方法代数（本项目 4.8–11.8×，预算无关；因 pop 固定，代数∝评价次数∝墙钟）。
- [ ] **公平对比口径**：baseline 与方法**同 problem、同 pop、同 seed 集、每 K 共同 HV 参考点**；只比"达到同质量所需预算"，不吹终态 HV（本项目终态仅略高、如实披露）。

**本项目参考数字**（迁移后不必相同，用于判断"方向对不对"）：主算例 K=20；`repair_only/FG` 收敛比 0.997–1.000；`warmstart_only` gen100 超 classic 至 +6.3%、收敛≈classic；加速比 vs classic 6.6/4.8/5.3/9.5×、vs NSGA-III 7.5/9.1/11.1/11.8×（K=10/20/30/40）。

---

## 9. 陷阱

- **过度修复**：把所有解投影到同一可行点 → 前沿多样性崩塌、HV 反降。要"就近、乘性、局部增补"。
- **顺序错误**：先升结构变量满足局部约束、再修全局约束，会来回打架、不收敛。严格按 §4 次序。
- **修复太贵**：修复里循环调仿真/迭代求解 → 抵消提速。保持 O(维度)、闭式/单遍贪心。
- **忘了兜底**：修复不保证严格可行，problem 侧必须仍返回真实 G（别在修复后谎报可行），由约束支配淘汰残余。
- **量纲未归一化**：多约束量纲悬殊时 CV 被大项主导，可行性压力失真。
- **pymoo 版本**：0.6.x 的 `Repair._do(self, problem, X)` 签名；旧版签名不同，迁移注意。

---

## 10. 环境

`python3 -m pip install "pymoo==0.6.1.3" numpy pandas`（anaconda 用 `python3 -m pip`，非 uv）。原样复现还需本项目 `county_model.py` + `lcc_simulator.py`（提供 `Station`、`eval_station`、`evaluate_county`、上述常量与物理量函数）。仅借鉴**模式**则不需要，用 §7 模板 + 你自己的 problem 即可。

---

## 附：给 AI 的任务指令模板（直接粘贴）

> 你将复现/迁移一个"多目标进化优化的可行性修复算子"。请阅读本文件 §2–§6：
> **任务 A（原样复现）**：用 §5 源码 + §3 常量，在 pymoo 0.6.1.x 上搭 `NSGA2(sampling=WarmStartSampling, repair=FeasRepair)`，对给定 `CountyProblem` 跑 pop=100/gen=400，并按 §8 清单做消融（classic / repair_only / warmstart_only / fg）与 iso-quality 加速比，产出逐代 HV 曲线与收敛 HV 表。
> **任务 B（迁移借鉴）**：按 §7 recipe，对我给出的新约束多目标问题：①列约束并分类变量（执行/结构）；②按耦合范围排序；③为每约束写闭式投影填进 §7 模板的 TODO；④只加 `repair`（先不加热启动）跑通，再按 §8 验证。
> **硬性要求**：修复内绝不调用目标/仿真；修复后 problem 仍返回真实 G；保持就近投影与多样性；给出 §8 全部验收项的结果。若某约束无法闭式投影，明确指出并降级为惩罚/拒绝，不要臆造公式。
