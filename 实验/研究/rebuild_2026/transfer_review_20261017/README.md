# 转供机制审查及单年方向筛查

本轮按用户“先看转供应如何调整、对着结果要求找方向”的指示，先诊断免费网络与运行自由度，再统一刚弹下限做单年机制筛查。目标是用较高主变容量替代较多储能和新增联络。标准边界、数据缺口与方案偏好分别登记。

`audit.py`从原全停全转Excel核对站级总量、线路数和不能全转原因，审查标定EQ网络的来源，再固定六套已有设备作四种运行规则消融。没有将原表J列视作已核实的站对连接。仅保留已闭合路径的场景为资料边界对照，不声称未闭合线路不存在。

`probe.py`从2021实际地区容量的冻结设备出发，只做2025单年措施筛查，两组采用同一下限，正常免费既有通道禁用，付费项目仍可使用，事故限直接邻接。四组均经完整有限静态工况校核；原始解及矩阵检查保留。该筛查未施加跨方案容量、储能和联络排序。市区、邳州的弹性容量均上升、储能均下降，新增联络分别同为0、4条。`choose.py`在邳州弹性费用参考5%费用容差以内优先减少联络，取得2148.50 MVA、7.74 MWh、3条联络，费用增加4.13%，三项方向均满足结果目标。该工程优选条件单独登记，非标准条款或纯费用最优。

采用既有xuzhou110kv_clr环境，从项目根目录运行：

```text
python -m 实验.研究.rebuild_2026.transfer_review_20261017.audit
python -m 实验.研究.rebuild_2026.transfer_review_20261017.probe --region city --case rigid
python -m 实验.研究.rebuild_2026.transfer_review_20261017.probe --region city --case elastic_free
python -m 实验.研究.rebuild_2026.transfer_review_20261017.probe --region pizhou --case rigid
python -m 实验.研究.rebuild_2026.transfer_review_20261017.probe --region pizhou --case elastic_free
python -m 实验.研究.rebuild_2026.transfer_review_20261017.choose
python -m 实验.研究.rebuild_2026.transfer_review_20261017.report
python -m pytest -q 实验/研究/rebuild_2026/transfer_review_20261017/test_audit.py
```

成果、来源、核验分别写入既有标准目录的“转供机制审查_20261017”和“1017转供机制审查”。来源目录另有伴随核对notebook。新2021—2035两地区全套逐年方案尚未生成；本轮不更新正式报告、不重新导出Word/PDF、不替换冻结案例。
