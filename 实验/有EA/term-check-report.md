# 术语核查报告 Term Check Report

稿件: `05_论文图表清单_MIND2026.md` 术语表（英文全稿未成，做聚焦核查） | 日期: 2026-07-04 | 领域锚定: distribution network / power distribution system | 验证源: **Semantic Scholar（high-confidence）**（OpenAlex 无 key 自动降级） | 查询: 30 候选 + 12 域内二次

> 判据（`rubric.md`）：主信号 = 倍数比 R = A_max/C；R≥100 或（R≥20 且高可疑度）→ 不规范；20≤R<100 → 存疑；C≥50 → 规范；C<5 且 A_max≥100 → 不规范。带域内 F 的用 F 重走判定（消歧）。

## 一、判定总表

| # | 原文/候选英文 | 判定 | 证据（S2 命中 C；域内 F） | 建议 |
|---|---|---|---|---|
| 1 | **capacity-load ratio**（容载比） | **规范（领域惯用）** | C=40，域内 F=15，**在所有变体中全局与域内双第一**；capacity-to-load ratio C=22/F=4；reserve capacity ratio C=6 | **保留** `capacity-load ratio`；可接受同义 `capacity-to-load ratio`。绝对量偏低是因"容载比"本属中国电网规划术语，非翻译腔 |
| 2 | source-load ratio（源荷比 slr） | **需作者确认（偏冷僻）** | C=6/F=3；generation-to-load ratio C=10；penetration ratio **C=1130/F=23** | 见 §四问题①：改 `generation-to-load ratio`，或作为本文合成站属性**显式定义**；`penetration ratio` 语义偏"装机/负荷"，不完全等价 |
| 3 | connection degree（联络度 CD） | **存疑** | 全局 C=717 但**域内 F=5**；域内 `network connectivity` F=113 → R_域内≈22.6 | 见 §四问题②：域内主流是 `network connectivity` / `interconnection`；`connection degree` 域内弱 |
| 4 | contact degree（联络度 误译） | **不规范（calque：联络→contact）** | 全局 C=275，**域内 F=1** | **弃用** |
| 5 | capacity-load ratio elasticity（容载比弹性） | **自创（本文核心贡献框架）** | C=0（所有变体 0） | 非既有文献术语——**首次出现必须明确定义**；这是论文的 novelty 框架，允许自造但需下定义 |
| 6 | rigid capacity-load ratio（刚性容载比） | **自创/calque（刚性→rigid）** | C=0；fixed / uniform capacity-load ratio 亦 C=0 | 改 `fixed capacity-load ratio` 或 `uniform capacity-load ratio`（"刚性"直译 rigid 生硬），首次出现说明"a single ratio applied uniformly" |
| 7 | reverse power flow（反送） | **规范** | C=1336；`reverse power` 单独 C=2015 但不完整 | 用完整式 `reverse power flow` |
| 8 | bidirectional power flow（双向潮流） | **规范** | C=3064 | 采用 |
| 9 | bidirectional network loss（双向网损 Z4） | **不规范（生造组合）** | C=3；`bidirectional power loss` C=0 | 改述 `network losses under bidirectional (two-way) power flow` 或 `bidirectional power-flow losses` |
| 10 | hypervolume（HV） | **规范** | C=2876 | ✓ |
| 11 | expected energy not supplied（EENS） | **规范** | C=501 | ✓ |
| 12 | inverted generational distance（IGD） | **规范** | C=485 | ✓ |
| 13 | non-dominated sorting（NSGA 的 ND 排序） | **规范** | C=11979 | ✓ |
| 14 | feasibility repair（可行性修复） | **规范** | C=106 | ✓ 支撑 FG-NSGA-II 命名合理 |
| 15 | repair operator（修复算子） | **规范** | C=511 | ✓ |
| 16 | warm start（热启动） | **规范** | C=2807 | ✓ |
| 17 | high penetration distributed generation（高渗透分布式电源） | **规范（描述性短语）** | 精确 4-gram C=35，但"high penetration of DG/renewables"极常见 | 用 `high-penetration distributed generation`（连字符作定语） |

## 二、自创术语（命名冲突检查）
- `FG-NSGA-II (Feasibility-Guided NSGA-II)`：本文方法名，`feasibility repair`(C=106)/`non-dominated sorting`(C=11979) 均为规范成分，命名合理、无命名冲突。
- `capacity-load ratio elasticity`（容载比弹性）、`rigid capacity-load ratio`：本文自创框架，C=0，无冲突，但**须显式定义**。

## 三、作者确认保留
- `capacity-load ratio`：证据支持保留（域内第一），不改。

## 四、作者已确认（2026-07-04）
1. **源荷比 slr → `generation-to-load ratio`**（作者选定；贴合"发电/负荷"、比值可>1 读法自然）。首次出现给定义："generation-to-load ratio (local renewable output to peak load)"。
2. **联络度 CD → `tie-line interconnection level`**（作者选定；表征站/馈线间联络互济能力）。首次出现给定义。`contact degree`/`connection degree` 均弃用。

## 五、总体评价
术语问题密度**低**：18 个受检术语中 10 个规范、1 个领域惯用（capacity-load ratio，核心术语无需改）、2 个自创（本文贡献框架，需定义）、3 个需修（contact degree/bidirectional network loss/rigid → 有更地道表达）、2 个待作者确认（slr、CD）。共性模式 = **偏正结构逐字直译（calque）**：contact degree（联络→contact）、rigid（刚性→rigid）、bidirectional network loss（双向网损逐字）。学习建议：中国电网规划专有概念（容载比）保留直译无碍，但"刚性/联络/双向网损"这类修饰性复合词优先改用英文文献的地道搭配（fixed/uniform、network connectivity、bidirectional power-flow losses）。**验证源为 S2（high-confidence）；配 OpenAlex key 后建议对 slr/CD/capacity-load ratio 复核一遍。**
