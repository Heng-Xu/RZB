# D5 规划与灵活资源 — 3篇文献结构化提取笔记

---

FILE: EN04_arxiv_dynamic_resource.md
SUBTHEME: T1 (柔性/主动配电网规划高PV) + T3 (源网荷储协同) — 核心为多DER动态协同提升寄生容量
BIB: Vineet Jagadeesan Nair, Morteza Vahid-Ghavidel, Anuradha M. Annaswamy (2026). "Dynamic resource coordination can increase grid hosting capacity to support more renewables, storage, and electrified load growth". arXiv:2604.02170v1 [eess.SY], 2 Apr 2026. (MIT + Univ. of Vaasa). 期刊页码待核(为arXiv预印本).
方法/模型:
- 三种HC估计方法并比：(1) 确定性迭代法; (2) 两阶段混合整数二阶锥随机规划 (2-SSP / MISOCP, two-stage mixed integer second order cone stochastic program), 联合优化4类DER的选址定容(siting & sizing); (3) Monte Carlo扩展(不确定性).
- 潮流: 支路潮流模型 + SOCP凸松弛(radial网exact). 动态情形求解ACOPF (MISOCP), 目标含: 最小化PV弃光、线损、热不适、HP/BS/EV循环、PCC购电成本(含LMP价格信号), 并鼓励PV给BS/EV充电.
- 加速: k-means场景缩减 + Monte Carlo采样 + warm start. 静态情形仅做AC可行性校验(无协同).
- 测试网络: 改造版 IEEE 123-node test feeder(平衡化), 约984户(每节点~8户), 总峰荷~3.4 MW (3,444 kW).
关键结论与数据:
- 确定性法(PV最大化, BS渗透=峰荷5%, 5%家庭有EV/HP): 动态法PV渗透达 83% vs 静态 48% → 相对提升约70%; 总PV从 1758 kW(59节点) 增至 2491 kW(101节点); 动态维持电压在1.05 p.u.上限内, 75%PV前电压低, 83%时不可行.
- 设备容量: BS功率147 kW(占最大负荷2930 kVA的5%), 储能441 kWh; HP容量168 kW(5%电气化户); EV容量396 kW/2700 kWh(中午多不可用).
- HP最大化案例(10%BS, 20%PV, 5%EV): 动态HP渗透从静态9%提至 55%; HP容量从226 kW(8节点)增至1381 kW(49节点); 关注7-8PM晚高峰.
- 2-SSP(20%BS, 20%HP, 10%EV, N=25代表场景): 动态PV HC = 98% vs 静态 24.2%; 优化自发产生BS与PV共址(co-location), DER间Spearman相关全为正(PV与BS/HP强正相关).
- 灵敏度(BS×HP×PV): 动态使可行(PV×HP×BS)组合体积增约 22倍(over 22×); 可达 200%太阳能 + 100%电池 + 90%热泵渗透; 静态可行域仅约45%BS/35%HP/50%PV. 储能(BS)对PV互补效应强于HP.
- 关键技术排序: 电池(batteries)最关键, 其次热泵, 再EV. HP灵活性对缓解热(电流)约束作用最大.
- 随机迭代法(5%BS+5%HP, 100场景, Table 1): 平均HC 静态51.08% vs 动态83.63%; 标准差 静态2.36% vs 动态3.44% → 动态波动率高约46% (摘要语"46% higher volatility under dynamic operation"); 动态显著降低网络平均/中位电流, 但放大不确定性.
- 文献引用数据点: 时变中压背景电压使HC平均降32%; 贝叶斯优化使概率HC提升25%; 集中协同使过载变压器比例从~81%降至28%、峰荷降17%(到2050); 全美电气化或需312 GW配网加固、成本$183–415 billion, 需求侧管理可降本至多92%; 公平动态HC配合≤5%弃光可使HC增≥50%.
局限/适用边界: 仅medium-scale配网(IEEE 123), 大网需Benders/SDDP分解(随机MINLP仍前沿); 假设radial平衡网(meshed/不平衡留待未来); 仅grid-following逆变器; 未做详细成本分析(成本效益为定性预期); 动态法引入更高不确定性/波动(主要风险); 需柔性接入协议+新传感通信编排基础设施(尚未广泛采用).

---

FILE: EN_Sustainability_SNS_coordinated_PV_2025.md
SUBTHEME: T1 + T2 (储能定址定容) + T3 (源网荷储/源网储协同) + T5(差异化/效益评价, 含灵敏度) — 核心为源-网-储协同随机规划提升PV消纳
BIB: Wang, J.; Chang, C.; Le, J.(通讯); Liao, X.; Wang, W. (2025). "Sustainable Distribution Network Planning for Enhancing PV Accommodation: A Source–Network–Storage Coordinated Stochastic Approach". Sustainability 2025, 17(12), 5324. https://doi.org/10.3390/su17125324 (MDPI; 武汉大学等; Received 17 Apr 2025, Published 9 Jun 2025).
方法/模型:
- 基于Copula理论的源荷时空相关概率模型(Gumbel/Clayton/Frank Copula, 极大似然估参, Kendall/Spearman秩相关+欧氏距离+非参核密度做拟合优度判别).
- Monte Carlo采样生成场景 + K-means聚类场景缩减(肘部法+轮廓系数定K), 提取代表性典型日.
- 源-网-储协同规划模型: 目标=最小化年综合成本(=PV弃光惩罚 + 网架扩建投资 + ESS投资/运维). 决策含PV与ESS选址定容(0-1变量)及网架扩建.
- PV用最优逆变器调度(OID)控有功无功; ESS充放电(SOC 0.2-0.9); 网架扩建用单商品流(SCF)保辐射连通; 潮流用二阶锥松弛(SOCR)→MISOCP; 含CB/SVC/OLTC等无功电压设备.
- 算例: 25-node 与 54-node 配网系统; 4种方案对比(方案1基准, 2=仅PV, 3=仅ESS, 4=PV+ESS协同).
关键结论与数据:
- 54-node(Scenario 1, 表15-17): 方案4比方案2 PV安装容量提升约25.1%、总发电量增约27.45%; 方案2/方案4相比方案1综合成本分别升约151.23%/35.61%, PV装机分别增17.37 MW/21.73 MW, 总发电量由0增至14,103.26 MWh / 17,975.25 MWh; 方案4 ESS总安装视在功率较方案3提升约70.27%、容量提升64%; ESS容量由0增至2.6 MWh(方案3)/4.2 MWh(方案4).
- 25-node(Scenario 1, 表13): 方案4 PV装机提升20%、总发电量增约35.37%; 方案2/4综合成本较方案1升约214.36%/57.71%, PV装机增9.85 MW/11.82 MW, 发电量由0增至7019.54 MWh / 9502.61 MWh; ESS视在功率方案4增约54.55%、容量增37.7%, ESS容量由0增至1.6 MWh(方案3)/2.2 MWh(方案4).
- 经济性: "PV+ESS"协同(方案4)相对基准仅增成本约2.23%却增PV发电17,975.25 MWh, 大幅提升消纳并平滑电压波动.
- 场景缩减对比(表20): K-means缩减计算时间6.5 s(文中另处称8.5 s)vs SBR 362.3 s; 25-bus综合成本 K-means 975.03 vs SBR 942.65(CNY万); 54-bus 1865.02 vs 1808.70; K-means成本仅比SBR高3.44%(25)/3.11%(54)但速度显著占优.
- 鲁棒性: 引入±10%PV/负荷预测误差检验; 灵敏度分析弃光惩罚系数与单位线路造价对PV/ESS/网架配置的影响.
局限/适用边界: 仅25/54-node两算例验证; 高弃光惩罚系数会致缓解措施过投资抬高综合成本(需权衡); 线路单位造价直接影响网架投资并间接改变PV/ESS策略(低造价倾向扩网, 高造价倾向本地储能/就近消纳); 采用辐射状拓扑.

---

FILE: EN_Energies_flexible_interconnect_SOP_storage_2026.md
SUBTHEME: T3 (柔性互联SOP/源网储协同消纳) + T2 (共享储能/E-SOP定容) + T4(Shapley公平成本分摊≈MCDM分配) + T1
BIB: Zhu, J.; Liu, Z.(通讯); Dai, F.; Ou, W.; Jiao, Y.; Xiang, Y. (2026). "Coordinated Planning of Unbalanced Flexible Interconnected Distribution Networks Based on Distributed Optimization". Energies 2026, 19(7), 1769. https://doi.org/10.3390/en19071769 (MDPI; 华南理工大学; Received 4 Mar 2026, Published 3 Apr 2026).
方法/模型:
- 多区域柔性互联配网协同规划, 核心装置=E-SOP(软开关SOP集成电池储能BES, 多端口共享DC母线). 集成PV+多端SOP+共享储能联合投资与运行.
- 模型为集中式MINLP, 目标=最小化年综合成本(投资+运维O&M+上网购电); 三相不平衡支路潮流; 非凸约束处理: rank-one松弛→半定规划SDP + 凸/线性近似; 电压不平衡约束凸化.
- 分布式求解: 在多端SOP公共DC母线解耦, 改进ADMM(自适应惩罚因子)分解为各区域子问题, 仅交换耦合变量(保护隐私).
- 成本分摊: 基于Shapley值(合作博弈)在多利益主体间公平分配总成本.
- 电压限值0.95-1.05 p.u.; 电压不平衡上限2%(IEEE Std 1159-2019 / 141-1993). 算例N=3个配电网.
关键结论与数据:
- 经济性(Case IV为最优, 相比规划前pre-planning): 系统年总综合成本降 14.90%(降6.998 million CNY); 购电成本降 28.61%(降13.431 million CNY); 各分项: 投资成本/运维成本上升(因SOP端口+BES投资增), 购电成本-28.61%(另列-24.88%/-28.14%为不同case分量).
- 电压质量(表8): 初始(Case I)各网最大电压不平衡 N1=2.18%、N2=2.68%、N3=3.08%(均超2%阈值, 且网2/3电压低于安全下限); Case IV降至全部2.00%以内 → 绝对降0.18/0.68/1.08个百分点, 相对降8.26%/25.37%/35.06%; 同时抬升电压幅值.
- 算法收敛: 标准ADMM 40次迭代仍不收敛; 改进ADMM约 25次迭代收敛至接近集中式结果; 不同惩罚因子下相对间隙0.02%-0.58%; 改进ADMM在不同初值下分别32次、12次收敛, 显著更快.
- Shapley分配: 全合作联盟{N1,N2,N3}为成本最优结构, 各网分摊成本均低于非合作情形, 无子联盟能同时改善全部成员(联盟稳定), 保证公平性提升参与意愿.
- 背景数据: 3%电压不平衡使电机损耗增约9%、绕组寿命降至约1/4. SOP工程: 英国FUN-LV、苏州四端口SOP、美ABB Mackinac HVDC、瑞士REEL Chapelle-sur-Moudon.
局限/适用边界: 算例仅3区域配网; 半定松弛exact性依赖rank-one条件满足; 现有文献ADMM多用于运行调度, 用于规划尚少(本文填补); 主要针对三相不平衡+多区域耦合+共享储能+公平分摊的联合场景.

---

## 注意事项 (attribution)
- 知识库中另存在他文(电力系统保护与控制中文54节点表、含"Typical Day 1-4 wind/PV/storage"的D7文献、陈璨MHC文献), 已与上述3篇严格区分, 未混入. 三个目标文件均完整可读(非乱码/空), pymupdf解析的公式区域为OCR碎片但摘要/方法/结论/算例文字完整, 关键数字均可定位核实.
