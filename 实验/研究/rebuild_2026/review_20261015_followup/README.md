# 运行约束与五参数深化

本轮源、数据和结果独立于`review_20261015`与正式报告初步定档，上一轮541项成果不改写。入口对应用户第二轮两项疑问。

`cases.py`给刚性和弹性施加共同运行条件：正常供区固定，储能只在N−1时提供原规定时长的备用支撑；另比较事故只允许故障站直接相连通道转接，以及既有转供按80%可用的研究裕度。后两项分别为运行策略、研究敏感性，均不冒称DL/T 2041—2025强制条款。所有求解记录和未通过全部静态工况的候选保留；只从通过全工况的方案中选择可行费用最低者。

`station_floor`为逐站不退减的主变投资替代对照，引用`standby`刚性建设计划并绑定其逐站CSV哈希。两个方案采用同一正常固定供区及储能备用策略；弹性各站逐年容量不低于引用计划。它以既定站点建设计划为前提，未加地区容量差或储能、联络排序要求。此组正间隙较大，只报告具体可行方案和下界，不称经济最优或确定节省。

`audit.py`逐站重组负荷、转出、转入及主变和储能支撑，检查区域守恒。对备用方案另用补齐8760小时、按年度统计峰值缩放的站级净负荷核对正常方式主变容量，不新增SOC优化，不报告全年新能源利用率。

`matrix_audit.py`分别统计现报告原始库、上一轮存量模型和全部重新选配模型的五参数完整受控序列、相邻设备变化、推荐区间原始端点与展示区间重复比例及最低容量命中。现报告432格逐项与当前正文的定值展示矩阵原始上下界核对。电缆占比在当前模型只改变线路价格；相同区间与容量保持分别统计，不将平台全部归因于最小规格或显示精度。

`verify.py --full-lp`对7组新方案的全部15288个静态工况重新做独立LP；默认检查源、解、设备CSV和原证书绑定，复算费用、容量、单元格及转供和价格费用上下界关系。两工作簿697624个数据单元格复核，4905600个正常站时点通过。3项机制测试覆盖正常储能禁用、直接事故转接和逐站可用系数。

```bash
python -m 实验.研究.rebuild_2026.review_20261015_followup.cases --policy standby --seconds 100
python -m 实验.研究.rebuild_2026.review_20261015_followup.cases --policy local_standby --seconds 120
python -m 实验.研究.rebuild_2026.review_20261015_followup.cases --policy transfer80 --seconds 120
python -m 实验.研究.rebuild_2026.review_20261015_followup.cases --policy transfer80 --case elastic_free --seconds 240 --attempt refine
python -m 实验.研究.rebuild_2026.review_20261015_followup.cases --policy station_floor --case elastic_free --seconds 180
python -m 实验.研究.rebuild_2026.review_20261015_followup.matrix_audit
python -m 实验.研究.rebuild_2026.review_20261015_followup.audit
python -m 实验.研究.rebuild_2026.review_20261015_followup.verify --full-lp
python -m 实验.研究.rebuild_2026.review_20261015_followup.memo
```

结果在`研究报告/01研究推荐/当前版/运行约束及五参数深化_20261015`，原始解在`研究报告/试算/20261015_运行约束及五参数深化`，来源在对应数据来源目录，核验在`研究报告/05_review/当前版/1015运行约束及五参数深化`。`研究报告待补充说明.md`为后续局部同步准备的技术段落，正式六章、Word和PDF尚未替换。
