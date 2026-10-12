# 本轮供讨论方案的原始求解库

主入口`实验/研究/rebuild_2026/case_parameters_20261012/capacity_run.py`。两地均保存刚性、弹性有2.0下限、弹性无2.0下限三组，使用相同地区输入、既有网络和静态截面。

`inputs.json`保存参数、2025参考设备标定、固定通道及压缩起点能力重算；`static_base.npz`和`静态工况.csv`保存同期截面及补值标记。每组`chosen_solution.npz`、`summary.json`、`stations.csv`、`projects.csv`、`years.csv`为所选方案；迭代文件与`candidate_*`保留工况加入过程。`selected_pairs.json`用于复建原约束矩阵；`independent_lp.json`保留全部静态截面的独立校核。

导出结果位于`研究报告/01研究推荐/当前版/案例承载力复核_20261012`；费用、设备、约束矩阵和独立转供校核位于`研究报告/05_review/当前版/1012案例承载力复核`。既有原始文件不覆盖，重新寻优应使用独立副本。
