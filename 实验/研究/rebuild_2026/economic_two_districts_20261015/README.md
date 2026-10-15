# 两区县经济方案与原表容量起点对照

用户确认采用原“弹性经济参考”，补齐市区，并增加保留初始年度原表地区容量的两地区结果。2021年固定共同设备，不参与优化；决策年份固定2022—2025。此前提出的2021首期优化已按用户要求停止，本目录不引用该未采用计算。

主组初始容量：邳州1463.50 MVA、市区2900 MVA。补充组：2021原表邳州2027 MVA、市区3113.50 MVA，逐站双主变组合继承第一轮已冻结的比例标定。原表总量有统计依据，逐站组合不是完整历史逐台设备复原。

复用 `recommend_20261015.model.build` 和 `OperatingLP`，正常按年固定比例转供、不使用事故备用储能，故障仅直接相连通道转接，正常及健康站反向80%。费用为唯一经济目标，刚性保留2.0扩容控制，不添加容量105%、储能50%等规划排序条件。邳州共同仿真起点两解原值继承并重新独立核验；其余六组按同一运行规则计算。全工况分离失败的早期候选与求解间隙保留。

邳州原表起点刚性方案已证不可行，另以全部候选线路放开这一宽松网络对照独立定位正常反向缺口，不将无解方案伪装成可行结果。其余七组按共同边界验证。

`matrices.py`审查原报告与重新选配库的完整九节点序列，筛选四个转供分档区间上下界均严格下降的典型场景，固定电缆50%、支撑4小时。线路系数只列固定条件，后续正文不独立分类讨论。原始不响应节点全部保留，18个展示节点重新作独立LP；筛选结果不能扩展为所有参数背景均单调或九个细节点均有容量响应。

项目根目录、既有 xuzhou110kv_clr 环境运行：

```text
python -m 实验.研究.rebuild_2026.economic_two_districts_20261015.model --region city --baseline compressed --case rigid
python -m 实验.研究.rebuild_2026.economic_two_districts_20261015.model --region city --baseline compressed --case elastic_free
# 补充组：region 取 city / pizhou，baseline 取 annual_2021，case 取 rigid / elastic_free
python -m 实验.研究.rebuild_2026.economic_two_districts_20261015.export
python -m 实验.研究.rebuild_2026.economic_two_districts_20261015.matrices
python -m 实验.研究.rebuild_2026.economic_two_districts_20261015.verify
python -m 实验.研究.rebuild_2026.economic_two_districts_20261015.memo
python -m 实验.研究.rebuild_2026.economic_two_districts_20261015.lock_review --write
```

首次准备四组输入及继承已确认邳州两解，调用 `model.prepare(region,baseline)` 和 `model.inherit_pizhou()`。冻结后入口只核验与读取，不覆盖原成果。完整结果位于标准的试算、01研究推荐、数据来源及05_review目录，各以“双区县经济方案_20261015”或“1015双区县经济方案”命名。正式六章源及Word/PDF未同步本轮新结果。
