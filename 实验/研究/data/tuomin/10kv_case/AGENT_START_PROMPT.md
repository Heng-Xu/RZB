# 本地Agent启动指令（V5.1）

前期数据整理已经完成，不要再把“解析旧脱敏包”作为工作阶段。

1. 读取 MODEL_CONFIG.yaml、data/final_preflight_qa.csv。
2. 建基准拓扑：TIE-001~006/008 OPEN，TIE-007 CLOSED。
3. 用TIE-007(CLOSED)与TIE-001/002/003(OPEN)反标图纸黑/空白开关语义。
4. 直接读取 node_load_seed_pf095.csv 与 node_pv_seed.csv。
5. 支路限额使用 effective_rate_a_base。
6. 首先运行TIE-002：S1正向、S2反向、S3转供扫描。
7. 必做PF、X、Imax、负荷空间分布敏感性。
8. 若某具体开关成为绑定约束且无铭牌额定值，只输出“定点复核该开关”，不要扩大收资范围。
9. TIE-001/003在拓扑patch闭环后计算。
10. 输出转供MW、瓶颈、Umin、最大负载率、站端余量、开关序列和数据质量标签。
