# Fig. 1 图注（`fig1_weaktie_cdslr.png`）— 供手改

> 说明：本图是 **EPG-NSGA-II 寻优所得的差异化容载比方案**，但算例是**人为构造的"弱联络+高渗透"情景**（非代表性徐州实测）。图注中已如实标注，请勿删除"constructed scenario"字样，否则易被审稿人质疑。

---

## A. 论文用英文图注（精简，直接放正文）

**Fig. 1.** Differentiated capacity–load ratio (CLR) scheme obtained by EPG-NSGA-II on a **constructed weakly-interconnected, high-PV county test case** (K = 20). Cells are ordered by generation-to-load ratio *s* (labeled per cell); the value *R* and the cell color give each substation's optimized CLR, and the figure below each *R* is the recommended storage power rating (0 = no storage). Substations with higher PV penetration and weaker interconnection adopt an **elastic CLR above the conventional 2.0 limit (up to 2.64)**, whereas lower-penetration, well-interconnected substations stay within the conventional band and rely on interconnection and storage.

## B. 中文图注（可选，若正文中文）

**图 1** 弱联络、高渗透构造算例（K=20）下由 EPG-NSGA-II 寻优得到的差异化容载比方案。方格按源荷比 *s* 排列（每格标注 *s*）；数值 *R* 与格子颜色表示各变电站优化后的容载比，*R* 下方为推荐储能额定功率（0 表示不配储）。源荷比高、联络弱的站采用**突破 2.0 上限的弹性容载比（最高 2.64）**；源荷比低、联络强的站维持常规带内，依靠站间互济与储能。

---

## C. 情景与参数（写入正文/脚注，务必保留"构造"口径）

- **测试系统**：K = 20 座 110 kV 变电站的**构造县域算例**（非实测徐州）。
- **高渗透**：源荷比 *s* ~ U[1.8, 3.5]。
- **弱联络且与渗透率反相关**：联络度 CD 随 *s* 线性递减，从低 *s* 的 0.45 到高 *s* 的 0.10（体现"高光伏地区往往弱联络"）。
- **储能成本按更全面口径**：取名义造价的 **2.5×**（≈10 年电池在 25 年周期内更换 ×1.74，叠加衰减/扩容 ×1.4）。
- **弹性容载比带** [1.8, 3.0]；单站容载比界 [1.2, 3.0]；储能功率 ≤ 6 MW（数量不限，靠成本经济性驱动）。
- **县内口径**：不施加上级 220 kV 反向承载约束。
- **可复现**：固定随机种子（seed=1）。

## D. 关键结果（数据）

| 指标 | 值 |
|---|---|
| 突破 2.0 的站数 | **15 / 20** |
| 最高容载比 maxR | **2.64** |
| corr(源荷比, 容载比) | **0.72**（高 *s* → 高 *R*） |
| EENS（N-1 供电风险） | **0 MWh**（低 *s* 站强联络清零风险） |
| 可行性 | 20/20 |
| 年化成本 f1 | 22843 万元/年 |

## E. 编码说明（图内元素）

- **格子颜色 / R 值**：该站优化后的容载比 *R*（色阶 1.2–2.7，越黄越高）。
- **顶部 $s$=**：该站源荷比。
- **底部 +X.X MW / 0**：推荐储能额定功率（0 = 无储能）。
- 方格按 *s* 从小到大排列（左上→右下）。

## F. 一句话结论（可放正文承接）

> 在弱联络、高渗透且储能成本按全寿命口径核算的县域中，差异化规划将**弹性容载比（R>2.0）定向配置于"高渗透 + 弱联络"的变电站**，其余站维持常规带并借助互济，实现"一站一策"且 N-1 零缺供。
