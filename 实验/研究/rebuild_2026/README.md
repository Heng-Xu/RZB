# 现行模型维护

地区主方案入口为`case_parameters_20261012/transfer_diagnostic.py`，采用版本`case_station_caps_normal_adjust_20261013`：市区和邳州正常允许调整供区的刚性与弹性无下限，共4组，另8组保留对照。主方案原始库在`研究报告/试算/20261012_既有转供约束诊断`，输入、解与模型依赖由对应锁定清单管理。

推广结果入口为`matrix_20261012`和`tools/locked_parameter_results.py`，对应32112有效设备配置；补充指标入口为`indicator_extension_20261014`及`tools/expand_indicator_backgrounds.py`，用于十三项候选指标统计分析。当前报告采用五项推广参数，9表432格，矩阵单元归纳2/4/6 h设备条件。

`static_actual_20261010`、`network_case_20261010`、`synchronous_20261009`、`pilot_20261009`及`matrix_20261010`中仍导入的公共模块和必要输入保留。`source_audit`含当前求解与核验输入，原始收资在`../data/tuomin`，不因模块日期较早而移除。

无关旧外推、敏感性和一次性脚本已逐文件校验备份后移出，明细在`研究报告/05_review/当前版/1014初步定档与表述约束`。`当前状态.md`及项目维护流程列明活动原始库和保留中间对照。不得用旧生成流程覆盖当前结果或更改锁定经济参数。
