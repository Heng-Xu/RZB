# 当前报告维护流程

当前有效约束为根目录及研究报告目录的 `AGENTS.md`。正式源是六章Markdown、计算表及生成段落JSON；不要从历史正文快照恢复覆盖。环境使用 `/home/xh/anaconda3/envs/xuzhou110kv_clr/bin/python`。

1. 修改当前源；若涉及小时数据，运行 `tools/prepare_regional_profiles.py`，核对补值日志和区域峰段。涉及负载率或案例敏感性图时，运行 `tools/refresh_report_comparison_figures.py`。
2. 执行 `python tools/build_current_report.py --rebuild`。自动先查源稿规则，再装配原生Word，最后核对公式、式中段落和目录结构。
3. 在WPS打开新Word，更新全部域并导出PDF。执行 `python tools/build_current_report.py --accept-wps-pdf <PDF路径>`，按实际标题页回填目录缓存。
4. 重新打开更新后的Word，再次导出并接收，直到目录页码、正文页码和链接目标一致。PDF必须由原生Word经WPS输出，不能以公式图片副本替换。
5. 查看目录、改动页、长公式、相关图表及分页，记录本次实际观察结果。执行 `python tools/build_current_report.py --check-only`，完成自动约束、逐格表格、原始计算和Word/PDF一致性核验。
6. 更新 `memory/current.md` 及本轮修订说明；清理失效资料后Git提交。保留用户原有 `prompt.md` 内容，并按最新要求纳入提交。

自动约束由 `tools/report_policy.json` 定义，检查入口为 `tools/check_report_policy.py --stage source|docx|final`。装配器直接调用前两阶段，交付核验调用最后阶段。版本管理前运行全部检查；不能用修改哈希或计数绕过失败。

源稿规则仅处理可客观定位的问题，不代替编辑复核。新增常见问题时，应同时修复正文、生成脚本和检测规则。长期规则只保留一份有效状态，历史条目归档，不继续追加矛盾规则。

讨论稿源文为 `研究报告/供电公司讨论稿/讨论稿.md`，运行 `python tools/build_discussion_brief.py`，方案及逐年措施表自动读取当前地区计算记录，推荐区间摘录当前计算表；当年新增与年末累计分别标注。WPS导出同目录PDF后运行 `python tools/build_discussion_brief.py --check --pdf`；该检查也已接入完整报告最终约束和提交钩子。正文无响应切片不再展示，原始结果保留。参数相关性复算记录在 `1011局部优化/相关性复算.json`，原始记录哈希和正文展示值须同步。

图片段落和图题由装配器显式清零点值、字符及悬挂缩进并设为居中；Word检查逐段验证，PDF检查同时验证图件实际中心位置。该规则在构建、提交和CI中自动启用，不依赖人工记忆。
