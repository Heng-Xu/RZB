# 当前报告维护流程

当前有效约束为根目录及研究报告目录的 `AGENTS.md`。正式源是六章Markdown、计算表及生成段落JSON；不要从历史正文快照恢复覆盖。环境使用 `/home/xh/anaconda3/envs/xuzhou110kv_clr/bin/python`。

1. 从已确认模型更新时，先运行`tools/sync_current_report_results.py`，仅同步计算表与生成段落，保持锁定结果和经济参数不变；运行`tools/refresh_report_comparison_figures.py`同步图件。修改当前六章源；若涉及小时数据，运行 `tools/prepare_regional_profiles.py`，核对补值日志和区域峰段。实际年度相关分析运行 `tools/prepare_case_correlations.py`，从原始Excel分别提取两地区年度样本；源稿、Word和最终检查均重新核对样本、系数及展示表。
2. 执行 `python tools/build_current_report.py --rebuild`。自动先查源稿规则，再装配原生Word，最后核对公式、式中段落和目录结构。
3. 在WPS打开新Word，更新全部域并导出PDF。执行 `python tools/build_current_report.py --accept-wps-pdf <PDF路径>`，按实际标题页回填目录缓存。
4. 重新打开更新后的Word，再次导出并接收，直到目录页码、正文页码和链接目标一致。PDF必须由原生Word经WPS输出，不能以公式图片副本替换。
5. 查看目录、改动页、长公式、相关图表及分页，记录本次实际观察结果。执行 `python tools/build_current_report.py --check-only`，完成自动约束、逐格表格、原始计算和Word/PDF一致性核验。
6. 更新 `memory/current.md` 及本轮修订说明；清理失效资料后Git提交。保留用户原有 `prompt.md` 内容，并按最新要求纳入提交。

自动约束由 `tools/report_policy.json` 定义，检查入口为 `tools/check_report_policy.py --stage source|docx|final`。装配器直接调用前两阶段，交付核验调用最后阶段。版本管理前运行全部检查；不能用修改哈希或计数绕过失败。

源稿规则仅处理可客观定位的问题，不代替编辑复核。新增常见问题时，应同时修复正文、生成脚本和检测规则。长期规则只保留一份有效状态，历史条目归档，不继续追加矛盾规则。

排除式说明按章节检索并逐段判断，覆盖实际引用的生成段落及表注。修订记录保留段落前后对照，以及实质约束、数据缺口等否定表述的保留理由；检查器报告源文件行号和JSON键名。`tools/test_report_prose_policy.py` 验证问题示例、必要表述及嵌套引用定位，Git提交和CI同步执行。

讨论稿源文为 `研究报告/供电公司讨论稿/讨论稿.md`，以 `04_word/研究报告终稿.docx` 为唯一内容依据。运行 `python tools/build_current_report.py --discussion --rebuild` 直接替换原讨论稿，`python tools/build_discussion_brief.py --check` 核验源文、终稿表格和原生Word。本轮按用户要求不生成PDF，最终直接在WPS逐页复核，登记Word哈希及页面截图后运行 `python tools/build_discussion_brief.py --check --final`；讨论稿核验与完整报告核验分别执行；本轮仅修订完整报告，旧讨论稿尚待同步，完整报告检查不读取旧讨论稿。原讨论稿PDF为修前文件。终稿自身的源稿、原生Word和WPS PDF流程仍按上述步骤执行。

图片段落和图题由装配器显式清零点值、字符及悬挂缩进并设为居中；Word检查逐段验证，PDF检查同时验证图件实际中心位置。该规则在构建、提交和CI中自动启用，不依赖人工记忆。

参数结果采用独立锁定流程，入口为`tools/locked_parameter_results.py`。已确认工作簿位于`研究报告/01研究推荐/当前版/参数联合情景_20261012`，原始库位于`研究报告/试算/20261012_参数联合情景锁定`；来源与核验归入各自标准目录。默认核验文件哈希、从原始库复算相关与矩阵、回算设备费用，并核对来源CSV及工作簿；`--lp`重新检查矩阵端点和分层节点。`--export-to`与`--solve-to`只写独立空目录。锁定版不随正文构建自动覆盖，后续调整须另建经审查的版本。提交钩子与CI同时核验锁定数据。

正文采用确认的全部六项参数，不作筛选。相关分析集中于第3.5节，参数间关系与参数对容载比的组内相关分别呈现；实际年度平均增长率采用与推广一致的复合定义。报告展示层将储能支撑时间与负荷分散系数按各自三个定值分开，锁定工作簿及原始库保持原件。研究报告依用户最新要求按普通模式修改，讨论稿要求由其对应任务决定；设备寿命和评价期只修改内容表述。

案例正文后续采用`研究报告/01研究推荐/当前版/既有转供约束诊断_20261012/报告采用版本说明.md`指定的4组主方案，以对应的`报告采用版本锁定清单.json`核对模型、输入和解。正常供区固定及2.0下限组保留用于对照分析；不得从历史零费用版或其他对照组替换主方案。先登记版本，再导出带用途标记的完整工作簿；`transfer_diagnostic --verify`同时核验版本与导出哈希。

本版数据核验入口为`tools/verify_current_report.py`，以报告采用版本、锁定参数库和当前源稿逐项复算；原`1010统一修订/核验.py`保留供历史结果审查，退出当前交付入口。`tools/build_current_report.py --check-only`依次检查当前约束、全部Word表格及本版数据。新增表达规则须有文件或JSON键定位；公式控制字符和Pandoc数学转换失败均阻止构建。
