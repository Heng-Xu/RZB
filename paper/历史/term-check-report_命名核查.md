# 术语核查报告 Term Check Report（命名聚焦）

稿件: `paper/02_论文大纲_v2_EPG-NSGA-II_中文.md`（英文全稿尚未起草，此为对本 session 新锁定英文名称的聚焦核查）
日期: 2026-07-04 | 领域锚定: evolutionary algorithm / multi-objective optimization | 验证源: openalex+s2 | 缓存: scratchpad/.term-check-cache.json

> 域内惯用词（capacity-load ratio、generation-to-load ratio、tie-line interconnection level、hypervolume、EENS、非支配排序等）已在既有报告 `实验/有EA/term-check-report.md` 核过，本次不重复消耗额度。本次只查**本 session 新造的方法名/组件名**及其构成词是否地道、是否与已有方法命名冲突。

## 一、自创名称：命名冲突检查（Stage 2d，只查冲突、不做翻译腔判定）

| 名称 | 命中 | 判定 | 说明 |
|---|---|---|---|
| EPG-NSGA-II | 0 | 自创（无冲突） | acronym 未被任何已发表方法占用，可安全使用 |
| Engineering-Prior-Guided NSGA-II | 0 | 自创（无冲突） | 无同名方法；"engineering prior (knowledge)" 概念在文献有据（约 6） |
| Feasibility-Preserving Warm-Start Sampling | 0 | 自创（无冲突） | 组件① 名；构成词均地道（见下表） |
| Constraint-Ordered Repair Projection | 0 | 自创（无冲突） | 组件② 名；对应老师原词"修复算子投影" |
| capacity-load-ratio elasticity | 0 | 自创（须定义） | 本文核心概念，首次出现须给定义（大纲 II-A 已含） |

## 二、构成词地道性（确认自创名由领域惯用词拼成、非翻译腔）

| 构成词 | 命中 | 判定 | 证据示例 |
|---|---|---|---|
| feasibility repair | 106 | 规范（约束优化惯用） | *PSO+: a new PSO for constrained optimization* |
| feasibility-preserving | 87 | 规范 | *Local Search in Combinatorial Optimization* |
| warm-start initialization | 68 | 规范 | *Warm-Started QAOA …* |
| capacity-load ratio | 41 | 规范（领域惯用，沿用） | （电力/结构领域） |
| constraint handling (EA) | 15 | 规范（领域标准） | *Blessings of maintaining infeasible solutions for constrained MOO* |
| constraint-ordered | 16 | 可用（描述性修饰，多见他域） | 机器人 QP 等；作修饰词语义清楚 |
| repair projection | 5（top 不相关） | 自创描述词（须定义） | 无固定用法；"投影回可行集"语义清楚，可用但须定义 |

## 三、需作者确认 / 待定
无。所有名称均无命名冲突，且由地道 EC / 约束优化词构成，非翻译腔。

## 四、应用修改（Stage 8）
**无需替换。** 名称已是与用户/老师定稿的英文，且核查通过。唯一动作（写作提醒，非术语替换）：
- `Engineering-Prior-Guided NSGA-II (EPG-NSGA-II)`、`Feasibility-Preserving Warm-Start Sampling`、`Constraint-Ordered Repair Projection`、`capacity-load-ratio elasticity` **均须在首次出现给出全称/定义**（前三者在 II-B、后者在 II-A）。

## 五、总体评价
本 session 的命名安全：方法名与两组件名**零冲突**、构成词**全部地道**（feasibility repair 106 / feasibility-preserving 87 / warm-start initialization 68 均为约束优化惯用），读者会读作自然的自创术语而非直译腔。`repair projection` 与 `capacity-load-ratio elasticity` 是自创描述词，靠正文定义支撑即可，不必改。扩写英文全稿后，建议再跑一次**全稿** term-check（抽取 40 候选），以覆盖届时新引入的表述。
