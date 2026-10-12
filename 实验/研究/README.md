# 当前报告计算模型

现行模型位于 `rebuild_2026`，保留正式报告及锁定参数结果需要的依赖模块与相关测试。原始收资和10 kV案例保留在 `data/tuomin`，模型必要输入位于 `rebuild_2026/source_audit`。

当前结果位于 `../../研究报告/01研究推荐/当前版`，正文和外推脚本位于相应 `当前版` 目录。使用 Conda 环境 `xuzhou110kv_clr`，依赖见 `../../tools/requirements-current.txt`。

正常文字修订只需运行 `../../tools/build_current_report.py --check-only`，无需重新寻优。完整流程及模型范围见 `../../docs/CURRENT-WORKFLOW.md`。旧仿真框架、派生数据与历史输出从工作目录清理，Git历史保持。
