# 站级限额与远景定容的2021—2035逐年方案

独立后继试算，沿用前轮逐小时源荷输入、2021实际地区总容量、共同容载比下限及价格。正式六章和20261015采用结果不变。

共同物理边界：正常跨站区段切换为零；事故原属区段经既有与新增联络转出合计不超过本站区段数20%，向下取整。原有馈线组、路径共享、受端余量、既有J列及局部事故预案限制继续适用。20%是响应本轮偏增容目标的研究情景假设，不能写成标准强制数值。两方案使用相同限额。

原主变位置仍全期最多更换一次。发生替换时，参考本站2035正反向峰值除0.95后选31.5、50、63、80MVA中的对应规格，超过80按80；保留原机不触发采购。原允许的第三台仍为50MVA。该规则共同适用，以免短期小规格采购锁死后期增长，并不保证单站可脱离配套独立满足2035全部工况。

刚性逐年比较工程总费用，并保留max(上年容量,年度规划峰值×2.0)上限。弹性放宽该上限，先减少新增联络与储能费用，在自身候选配套费用20%容差内减少联络，再比较总费用；主变投资不受原5%总费用包络限制。该偏好是为满足用户要求选取的工程情景，不是放宽容量上限必然得到三项排序的数学定理。采用结果没有刚弹之间的排序约束。

重算入口（项目根目录，Python使用xuzhou110kv_clr环境，OPENBLAS_NUM_THREADS=1）：

1. `python -m 实验.研究.rebuild_2026.annual_bounded_transfer_2035_20261017.prepare`
2. `python -m 实验.研究.rebuild_2026.annual_bounded_transfer_2035_20261017.run --region city --case rigid --seconds 8`，邳州改为pizhou。
3. `python -m 实验.研究.rebuild_2026.annual_bounded_transfer_2035_20261017.capacity --region city --seconds 8`，邳州改为pizhou。
4. `python -m 实验.研究.rebuild_2026.annual_bounded_transfer_2035_20261017.verify`
5. `python -m 实验.研究.rebuild_2026.annual_bounded_transfer_2035_20261017.export`
6. `python -m 实验.研究.rebuild_2026.annual_bounded_transfer_2035_20261017.audit`
7. `python -m 实验.研究.rebuild_2026.annual_bounded_transfer_2035_20261017.test_model`

采用原始结果位于`研究报告/试算/20261017_远景定容站级限额逐年2035/{city,pizhou}/{rigid,elastic_capacity}`。`elastic_capacity_auxcost`、`elastic_capacity_aux5`和`elastic_capacity_aux20_unreconciled`为未采用过程：独立对账发现这些候选的辅助目标漏计联络费用，不能作为完成优选的成果。联络费用在原模型的new_projects变量计价，修复后按已建路径逐项计入辅助目标并添加测试、年度对账断言，采用方案全部重算。`20261017_站级限额逐年2035`保留尚未加入远景选型的初次试算，也不混作采用方案。

交付工作簿前两页为市区、邳州逐年左右对照，主表沿用表5-4的容量、容载比、储能额定功率、累计新线列项，追加当年净增容量。其余页列当年工程、费用和核验。单独交付Excel和Markdown表，符合用户指定的主要展示形式。

核验从原始整数解重建约束，直接检查固定预案下8760小时正常及逐站N-1工况，另用本站保留负荷比例给出独立必要条件。`independent_lp.json`仅为项目兼容命名，method明确是矩阵检查。2021保持固定资产，零切换缺口单列。规划候选不是全期联合全局最优，条件搜索的下界不冒称原总费用全局下界。
