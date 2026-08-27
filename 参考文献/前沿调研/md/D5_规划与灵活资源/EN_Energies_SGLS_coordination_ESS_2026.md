<!--
source: D5_规划与灵活资源/EN_Energies_SGLS_coordination_ESS_2026.pdf
sha256: 5137b017e39fc8a71e606209eeef0caca295bfb42a92c5d98e96a5b18ea3756a
method: pymupdf
pages: 23
-->

<!-- page 1/23 -->

 
 
 
 
Energies 2026, 19, 415 
https://doi.org/10.3390/en19020415 
Article 
Research on Source–Grid–Load–Storage Coordinated  
Optimization and Evolutionarily Stable Strategies for  
High Renewable Energy 
Yu Shi 1, Yiwen Yao 1, Yiran Li 2, Jing Wang 1, Rui Zhou 3, Xiaomin Lu 1, Xinhong Wang 1, Dingheng Wang 1, 
Xuefeng Gao 1, Xin Xu 1, Zilai Ou 2, Leilei Jiang 2 and Zhe Ma 2,* 
1 Power Economic Research Institute of Jilin Electric Power Co., Ltd., Changchun 130021, China 
2 State Key Laboratory of Coastal and Offshore Engineering, Dalian University of Technology,  
Dalian 116024, China 
3 State Grid Jilin Electric Power Co., Ltd., Changchun 130021, China 
* Correspondence: deep_mzh@dlut.edu.cn 
Abstract 
In the context of large-scale renewable energy integration driven by China’s dual-carbon 
goals, and under distribution network scenarios with continuously increasing shares of 
wind and photovoltaic generation, this paper proposes a source–grid–load–storage coor-
dinated planning method embedded with a multi-agent game mechanism. First, the in-
terest transmission pathways among distributed generation operators (DGOs), distribu-
tion network operators (DNOs), energy storage operators (ESOs), and electricity users are 
mapped, based on which a profit model is established for each stakeholder. Building on 
this, a coordinated planning framework for active distribution networks (DN) is devel-
oped under the assumption of bounded rationality. Through an evolutionary-game pro-
cess among DGOs, DNOs, and ESOs, and in combination with user-side demand re-
sponse, the model jointly determines the optimal network reinforcement scheme as well 
as the optimal allocation of distributed generation (DG) and energy storage system (ESS) 
resources. Case studies are then conducted to verify the feasibility and effectiveness of the 
proposed method. The results demonstrate that the approach enables coordinated plan-
ning of DN, DG, and ESS, effectively guides users to participate in demand response, and 
improves both planning economy and renewable energy accommodation. Moreover, by 
explicitly capturing the trade-offs among multiple stakeholders through evolutionary-
game interactions, the planning outcomes align better with real-world operational char-
acteristics. 
Keywords: source–grid–load–storage; multi-agent coordination; evolutionary game;  
demand response 
 
1. Introduction 
Under the accelerated implementation of China’s dual-carbon strategy, the installed 
capacity of renewable energy sources such as wind and photovoltaic power in distribu-
tion networks (DNs) continues to grow. Their high-penetration integration introduces 
pronounced variability, intermittency, and uncertainty into the system [1,2]. The rapid 
fluctuations and spatially uneven distribution of renewable energy output can easily 
Received: 16 December 2025 
Revised: 9 January 2026 
Accepted: 12 January 2026 
Published: 14 January 2026 
Copyright: © 2026 by the authors. 
Licensee MDPI, Basel, Switzerland. 
This article is an open access article 
distributed under the terms and 
conditions of the Creative Commons 
Attribution (CC BY) license.



<!-- page 2/23 -->

Energies 2026, 19, 415 
2 of 23 
 
https://doi.org/10.3390/en19020415 
trigger issues such as voltage violations, reverse power flows, line overloading, and re-
newable curtailment, thereby posing severe challenges to the traditional “passive accom-
modation” operating paradigm of conventional DNs [3–5]. To enhance renewable energy 
accommodation and improve system flexibility, a coordinated source–grid–load–storage 
(SGLS) optimization framework is established by integrating multiple flexible resources—
including distributed generation (DG), energy storage systems (ESSs), flexible loads, and 
demand response (DR). This enables the DN to transition from a “passive response” mode 
toward an “active control” paradigm [6–10]. 
However, flexibility resources are typically invested in and operated by different 
stakeholders, resulting in pronounced differences in their objectives and behavioral in-
centives: distributed generation operators (DGOs) seek to maximize generation revenues; 
distribution network operators prioritize network reinforcement costs and operational se-
curity; energy storage operators (ESOs) rely on price arbitrage for profit; and users aim to 
reduce energy expenditures through DR. The coupling of objectives and the inherent con-
flicts of interest among these agents impart strong game-theoretic characteristics to DN 
planning. Without an effective coordination mechanism, planning decisions are prone to 
becoming suboptimal or even mutually constraining [11]. 
In recent years, extensive research has been conducted on scenarios with high renew-
able energy penetration. Some studies focus on enhancing the flexibility of active DNs, for 
example, by integrating energy storage, exploiting multi-energy complementarity, or lev-
eraging integrated energy systems to improve the accommodation capability of renewa-
ble resources [12,13]. Mao et al. [14] unified flexible resources such as electric vehicles, 
hydrogen storage, and HVAC loads as “generalized energy storage” and coordinated 
them across day-ahead, intra-day, and real-time timescales to address renewable uncer-
tainty, thereby improving system cost-effectiveness and reliability. Liu et al. [15] propose 
a source–grid expansion planning framework for incremental DN that coordinates DG 
deployment, line construction, and network investments to enhance power quality and 
renewable energy accommodation. Another body of research focuses on the coordinated 
planning of transmission–DNs or wind-PV–storage systems, where second-order cone re-
laxation and decomposition-based coordination algorithms are employed to improve the 
computational efficiency of large-scale planning models [6]. Saldaña-González et al. [16] 
apply Long Short-Term Memory-based forecasting for load and DG, coupling time-series 
prediction with the planning model to improve the accuracy of long-term DN expansion 
decisions. Li et al. [11] incorporate distribution locational marginal pricing and distributed 
market mechanisms into DN planning to strengthen the alignment between planning 
schemes and the evolving electricity market environment. Mehrjerdi [17] develop an en-
ergy storage planning model that simultaneously achieves peak shaving and voltage sup-
port, leveraging the reactive power regulation capability of inverters to improve power 
quality and enhance storage investment returns. Gao et al. [7] introduce a Kullback–
Leibler divergence-based distributionally robust planning method that integrates multi-
ple forms of DR—including interruptible loads (IL) and transferable loads (TL)—and co-
ordinates with multi-energy stations to increase DN flexibility. Suryakiran et al. [18] for-
mulate a DSO-based day-ahead market coordination model that improves active DN op-
erational efficiency through flexible resource scheduling and price-driven signals. Mao et 
al. [19] provide a state-of-the-art review on the optimal operation of CCHP systems under 
high-penetration renewables, summarizing flexibility-enabled and uncertainty-aware 
scheduling (robust/stochastic/hybrid and data-driven methods) and identifying open is-
sues in multi-energy coupling, computational tractability, and multi-stakeholder coordi-
nation across timescales—insights that motivate our SGLS coordinated planning model 
for active distribution networks.



<!-- page 3/23 -->

Energies 2026, 19, 415 
3 of 23 
 
https://doi.org/10.3390/en19020415 
Meanwhile, the trend toward market-oriented multi-agent interaction has become 
increasingly prominent, prompting researchers to incorporate methods such as Stackel-
berg games, multi-level games, and system dynamics to characterize strategic competition 
and interest trade-offs among participants [20,21]. Zhou et al. [22] develop an evolution-
ary-game model among generation entities to analyze the profit evolution of virtual 
power plants under different strategic choices, providing theoretical support for market 
operations involving multiple stakeholders. Wu et al. [23] propose a bi-level robust game-
theoretic planning framework for DNs and microgrids, aiming to account for bilateral en-
ergy transactions among diverse stakeholders in emerging electricity markets. The frame-
work employs a linear robust dual formulation to address non-convexities induced by 
renewable energy uncertainty. Singh et al. [24] introduce a three-layer hierarchical deci-
sion-making approach for multi-microgrid energy management in active distribution sys-
tems, which coordinates energy resources across various operational agents—including 
distribution companies, microgrid operators, and end users. Li et al. [25] present a two-
stage dynamic robust DN planning method that accounts for correlation structures, ad-
dressing reliability challenges arising from the widespread presence of heterogeneous 
load entities. 
Although existing studies have made significant progress in areas such as flexibility 
enhancement in active DN, coordinated transmission–distribution planning, multi-agent 
game mechanisms, and data-driven scenario generation, several limitations remain. First, 
the interests and behavioral patterns of multiple stakeholders are often simplified as static 
or one-shot decisions, which fails to capture the strategy evolution of SGLS participants 
under long-term and dynamic interactions. Second, few studies integrate DG, energy stor-
age, DN operation, and DR within a unified evolutionary-game framework, making it 
difficult to systematically analyze how multi-agent competition–cooperation relation-
ships influence DN planning and renewable energy accommodation. Therefore, con-
structing an evolutionary-game-based coordinated planning model that characterizes 
bounded rationality, multi-round decision-making, and adaptive strategy adjustment is 
of both theoretical significance and practical value for supporting high renewable pene-
tration in active DN involving multiple stakeholders. 
Motivated by these gaps, this paper proposes an evolutionary-game-driven SGLS co-
ordinated planning approach for active DN. By modeling the strategy adaptation pro-
cesses of DGOs, DNOs, ESOs, and users under price signals, revenue mechanisms, and 
risk constraints, the proposed method enables planning decisions driven by multi-agent 
behavioral evolution. This framework provides a new pathway for enhancing renewable 
energy accommodation, reducing DN reinforcement costs, and improving system flexi-
bility. 
2. Stakeholder Game Relationships 
In a market-oriented power system, the divergent objectives and revenue preferences 
of different participants inevitably give rise to conflicts of interest, thereby forming a land-
scape of mutual constraints and strategic interactions. Achieving benefit alignment among 
multiple agents in complex DN planning—and motivating all parties to jointly participate 
in network development and improve overall planning performance—first requires a 
clear understanding of the benefit flows and information exchange pathways among 
DGOs, DNOs, ESOs, and electricity users. Accordingly, this study analyzes the interrela-
tions and interactions among these stakeholders, as illustrated in Figure 1.



<!-- page 4/23 -->

Energies 2026, 19, 415 
4 of 23 
 
https://doi.org/10.3390/en19020415 
 
Figure 1. Interaction and information flow among stakeholders. 
In SGLS coordinated planning, each participant exhibits distinct priorities. The stor-
age business model adopted in this work assumes that ESSs purchase electricity preferen-
tially from DG units, with additional electricity procured from the DN when necessary. 
To reduce renewable curtailment, ESOs first engage in bilateral transactions with DGOs 
and leverage the remaining battery capacity to perform price arbitrage—charging during 
low-price periods and discharging during high-price periods under the time-of-use (TOU) 
tariff. DGOs determine their capacity investments by considering construction and oper-
ation and maintenance (O&M) costs, expected electricity sales revenue, and potential in-
come from green certificate trading. 
DG capacity not only affects the traded electricity volume and revenue between ESOs 
and DGOs but also influences the power purchase and sales costs of DNOs. DNOs aim to 
ensure secure and economic grid operation, striving to minimize network reinforcement 
and operational costs while maintaining supply reliability. Their grid expansion deci-
sions, however, constrain the maximum allowable DG hosting capacity, which in turn 
affects the profitability of ESOs. When determining ESS capacity, ESOs weigh DG–ESS 
transaction profits, arbitrage revenues from “low-price charging and high-price discharg-
ing,” and ESS investment and operating costs. The resulting storage scale then feeds back 
to DG curtailment levels and affects the DNOs’ grid reinforcement requirements and op-
erational expenditures. 
These interactions demonstrate that DGOs, DNOs, and ESOs have partially aligned 
yet interdependent interests. By contrast, electricity users participating in DR primarily 
focus on reducing electricity bills and improving compensation under outage or incentive 
mechanisms. As user benefits are largely determined by electricity prices and incentive 
schemes—and are not directly affected by the decision variables of the three main market 
players—this study does not include users as game participants. Instead, users are mod-
eled as external actors that adjust their consumption in response to predefined tariffs and



<!-- page 5/23 -->

Energies 2026, 19, 415 
5 of 23 
 
https://doi.org/10.3390/en19020415 
incentives to maximize their own benefits, with their DR outcomes unidirectionally fed 
back to the DNOs. 
3. Profit Models of Stakeholders 
3.1. Profit Model of DGOs 
(1) Objective function 
This study considers the coordinated planning of wind and photovoltaic generation 
to achieve wind–solar complementarity. DGOs aim to reduce construction and operation 
costs and maximize revenues from electricity sales to the DN and ESSs, as well as income 
from green certificate trading. Accordingly, DGOs determine the installed capacity of DG 
based on the objective of maximizing its own profit. The objective function is defined as 
max 𝐹dg = 𝐹dg,sel + 𝐹ess,sel −𝐶dg,con −𝐶dg,ope 
(1)
𝐹dg,sel = ∑(
𝑇
𝑡=1
∑𝐸dg,WT
𝑊
𝑤=1
𝑃WT,𝑤
𝑡
+ ∑𝐸dg,PV
𝑉
𝑣=1
𝑃PV,𝑣
𝑡
) 
(2)
𝐹ess,sel = ∑𝐸dg,ess
𝑇
𝑡=1
𝑃chl
𝑡 
(3)
𝐶dg,con = ∑
𝑁WT,𝑤Pdg
WT,𝑤𝐸dg,con
WT,𝑤𝑟(1 + 𝑟)𝑇dg
WT,𝑤
(1 + 𝑟)𝑇dg
WT,𝑤
−1
𝑊
𝑤=1
+ 
∑
NPV,𝑣𝑃dg
PV,𝑣Edg,con
PV,𝑣𝑟(1 + 𝑟)𝑇dg
PV,𝑣
(1 + 𝑟)𝑇dg
PV,𝑣
−1
𝑉
𝑣=1
 
(4)
𝐶dg,ope = ∑∑𝐸dg,ope
WT,𝑤
𝑊
𝑤=1
𝑇
𝑡=1
𝑃WT,𝑤
𝑡,pro + ∑∑𝐸𝑑𝑔,𝑜𝑝𝑒
𝑃𝑉,𝑣
𝑉
𝑣=1
𝑃𝑃𝑉,𝑣
𝑡,𝑝𝑟𝑜
𝑇
𝑡=1
 
(5)
where Fdg denotes the annual net revenue of DGOs; Fdg,sel represents the electricity sales 
revenue obtained by DGOs; Fess,sel denotes the revenue earned from selling electricity to 
ESOs; Cdg,con is the investment cost of DG construction, expressed in annualized form us-
ing the capital recovery factor to account for equipment lifetime. The annualized cost of 
lines and energy storage systems is treated in the same manner. For equipment lifetime n, 
the capital recovery factor is given by 𝑟(1 + 𝑟)𝑛/[(1 + 𝑟)𝑛−1] where r is the discount 
rate. Cdg,ope represents the O&M cost of the DG units.; T denotes the number of operating 
periods; w denotes the number of wind turbine (WT) types, and v denotes the number of 
photovoltaic (PV) types; 𝑃WT,𝑤
t
 is the actual output of WT type w in period t, and; 𝑃PV,𝜈
t
 
denotes the actual output of PV type v in period t; Edg,WT and Edg,PV are the unit electricity 
sale prices for WT and PV generation, respectively; Edg,ess denotes the transaction electric-
ity price between DGOs and ESOs; 𝑃𝑐ℎ1
𝑡
represents the charging power traded between 
the ESO and the DGO during time period t. NWT,w represents the number of installed WTs 
of type w; 𝑃dg
WT,wis the rated power of a single WT of type w; 𝐸dg,con
WT,w denotes the unit ca-
pacity investment cost of WT type w. NPV,ν is the number of PV units of type v; 𝑃dg
PV,νis the 
rated capacity of a single PV unit of type v; 𝐸dg,con
PV,ν denotes the unit capacity investment 
cost of PV type v; 𝑇dg
WT,ν and 𝑇dg
PV,ν are the lifetimes of WT type w and PV type v, respec-
tively; Edg,ope
WT,ν denotes the O&M cost per unit energy output of WT type w, and; 𝑃WT,𝑤
𝑡,pro is 
its scheduled output in period t; 𝐸dg,ope
PV,ν represents the O&M cost of a single PV unit of 
type v; 𝑃PV,𝑣
𝑡,prodenotes the scheduled PV output in period t.



<!-- page 6/23 -->

Energies 2026, 19, 415 
6 of 23 
 
https://doi.org/10.3390/en19020415 
(2) Constraints 
DG installation quantity constraints 
𝑁𝑊𝑇≤𝑁𝑊𝑇,𝑚𝑎𝑥 
(6)
𝑁𝑃𝑉≤𝑁𝑃𝑉,𝑚𝑎𝑥 
(7)
where NWT,max denotes the upper limit on the number of installed WTs, and NPV,max repre-
sents the maximum allowable number of installed PV units. 
Output constraints of DG units: 
0 ≤𝑃𝑑𝑔,𝑊𝑇
𝑡
≤𝑃𝑑𝑔,𝑊𝑇
𝑡,𝑝𝑟𝑜 
(8)
0 ≤𝑃𝑑𝑔,𝑃𝑉
𝑡
≤𝑃𝑑𝑔,𝑃𝑉
𝑡,𝑝𝑟𝑜 
(9)
3.2. Profit Model of DNOs 
(1) Objective function 
DNOs seek to ensure secure and economic operation of the DN by jointly considering 
electricity purchase and sales revenues, network reinforcement costs, network loss costs, 
and fault-related costs. Accordingly, DNOs determine the network expansion plan with 
the objective of maximizing its net profit. The objective function is formulated as 
max 𝐹dn = 𝐹dn,sel −𝐶dn,ch −𝐶dn,line −𝐶dn,loss −𝐶dn,fau −𝐶dn,aba 
(10)
𝑊dn,sel = ∑𝐸dn,sel
𝑡
𝑇
𝑡=1
𝑃dn
𝑡 
(11)
Cdn,ch = Cdn,grid + Cdn,up 
(12)
Cdn,line =
r(1 + 𝑟)TL
(1 + 𝑟)TL −1 ∑𝐶l
𝑁l
l=1
𝐿l 
(13)
Cdn,loss = ∑𝑃dn,loss
t
T
t=1
Edn,sel
t
 
(14)
Cdn,fau = ∑𝑃ENS
t
T
t=1
Edn,sel
t
 
(15)
Cdn,aba = ∑(
T
t=1
𝑃dn,aba
t,WT Edn,aba
WT
+ 𝑃dn,aba
t,𝑃V
Edn,aba
𝑃V
) 
(16)
where Fdn denotes the annual net revenue of the DNO; Fdn,sel represents the electricity sales 
revenue of the DNO; Cdn,ch is the electricity purchase cost; Cdn,line denotes the network re-
inforcement (line investment) cost; Cdn,loss is the cost associated with network losses; Cdn,fau 
denotes the cost of supply interruptions or failures; Cdn,aba represents the cost incurred due 
to WT and PV curtailment; 𝐸dn,sel
𝑡
 is the unit electricity selling price in period t; 𝑃g
t de-
notes the electricity sales volume in period t; Cdn,grid represents the cost of electricity pur-
chased from the local grid, and Cdn,up denotes the cost of electricity purchased from the 
upper-level grid; TL is the lifetime of distribution lines; Cdn,line denotes the investment cost 
for newly constructed lines; Nl is the total number of new lines; Cl represents the unit-
length construction cost of the new lines; Ll is the length of the l-th new line; 𝑃dn,loss
𝑡
 de-
notes the network loss in period t; 𝑃ENS
t
 represents the expected energy-not-served in



<!-- page 7/23 -->

Energies 2026, 19, 415 
7 of 23 
 
https://doi.org/10.3390/en19020415 
period t; 𝐸dn,aba
WT
 and 𝐸dn,aba
𝑃V
 denote the unit penalty cost for curtailed WT power and cur-
tailed PV power, respectively; 𝑃dn,aba
t,WT  is the amount of WT power curtailment in period t; 
𝑃dn,aba
t,PV
 is the amount of PV power curtailment in period t. 
(2) Constraints 
Branch power flow constraints: 
{  
  𝑃𝑆𝑖−𝑃𝐿𝑖= 𝑈𝑖∑𝑈𝑗
𝑗∈𝑖
(𝐺𝑖𝑗𝑐𝑜𝑠𝜃𝑖𝑗+ 𝐵𝑖𝑗𝑠𝑖𝑛𝜃𝑖𝑗)
𝑄𝑆𝑖−𝑄𝐿𝑖= 𝑈𝑖∑𝑈𝑗
𝑗∈𝑖
(𝐺𝑖𝑗𝑠𝑖𝑛𝜃𝑖𝑗−𝐵𝑖𝑗𝑠𝑖𝑛𝜃𝑖𝑗)
 
(17)
where PSi denotes the total active power injected at node i by the DG units and ESSs; QSi 
represents the total reactive power injected at node i; PLi is the sum of the active power 
consumed by the loads connected to node i and the charging power absorbed by the en-
ergy storage systems; QLi denotes the total reactive power consumed by the loads at node 
i; Ui and Uj are the voltage magnitudes at nodes i and j, respectively; Gij and Bij represent 
the conductance and susceptance of the line between nodes i and j; θij is the voltage phase-
angle difference between nodes i and j. 
Nodal voltage constraints: 
𝑈𝑖,𝑚𝑖𝑛≤𝑈𝑖≤𝑈𝑖,𝑚𝑎𝑥 
(18)
where Ui,min and Ui,max denote the lower and upper bounds of the voltage magnitude at 
node i, respectively. 
Line power flow constraints: 
𝑃𝑖𝑗≤𝑃𝑖𝑗,𝑚𝑎𝑥 
(19)
where Pij denotes the active power transmitted through the line between nodes i and j, 
and Pij,max represents the maximum allowable active power flow on that line. 
3.3. Profit Model of ESOs 
(1) Objective function 
ESOs aim to maximize their total profit by increasing revenue from electricity trans-
actions with DGOs and from price-arbitrage activities—charging during low-price peri-
ods and discharging during high-price periods—while minimizing the construction and 
operation costs of the ESS. Accordingly, ESOs determine the installed storage capacity 
based on the objective of profit maximization. The objective function is formulated as 
max 𝐹ess = 𝐹ess,ptv + 𝐹ess,sub −𝐶ess,bus −𝐶ess,con −𝐶ess,ope 
(20)
𝐶ess,bus = 𝐹ess,sel 
(21)
𝐹ess,ptv = ∑𝐸dn,sel
𝑡
𝑇
𝑡=1
(𝑃dch2
𝑡
−𝑃ch2
𝑡
) 
(22)
𝐹ess,sub = ∑𝐸ess,sub
𝑇
𝑡=1
𝑃ch1
𝑡
 
(23)
𝐶ess,con = 𝐸ess,con𝑁ess𝑃ess𝑟(1 + 𝑟)𝑇ess
(1 + 𝑟)𝑇𝑒𝑠𝑠−1
 
(24)
𝐶ess,ope = 𝐸s,ope𝑁𝑠 
(25)



<!-- page 8/23 -->

Energies 2026, 19, 415 
8 of 23 
 
https://doi.org/10.3390/en19020415 
where Fess denotes the annual net revenue of ESOs; Fess,ptv represents the revenue earned 
from price arbitrage (charging at low prices and discharging at high prices); Fess,sub denotes 
the government subsidies received by ESOs; Cess,con is the construction cost of the ESS; 
Cess,bus represents the electricity purchase cost from DGOs; Cess,ope denotes the O&M cost of 
the ESS; 𝑃dch2
𝑡
 and 𝑃ch2
𝑡
 represent the discharging and charging power of the storage sys-
tem in period t, respectively, associated with price arbitrage activities; Eess,sub is the subsidy 
amount provided by the government; Eess,con denotes the unit capacity construction cost of 
the ESS; Ps is the rated capacity of a single storage unit; Ns represents the number of in-
stalled storage units; Tess is the service lifetime of the storage system; Eess,ope denotes the 
O&M cost per kilowatt-hour of storage capacity. 
The charging and discharging power of the ESS are expressed in Equations (26) and 
(27): 
𝑃dch
𝑡
= (𝑃ess,sur
𝑡−1
−𝑃ess,sur
𝑡
)𝜂dch 
(26)
𝑃ch
𝑡= (𝑃ess,sur
𝑡
−𝑃ess,sur
𝑡−1
)/𝜂ch 
(27)
where 𝑃s,sur
𝑡−1  and 𝑃s,sur
𝑡
 denote the state of charge (SOC) of the ESS at the end of periods t 
− 1 and t, respectively; ηdch is the discharging efficiency of the storage system; ηch repre-
sents the charging efficiency. The SOC of the ESS in period t is given by 
𝑆𝑒𝑠𝑠
𝑡
= 𝑃𝑒𝑠𝑠,𝑠𝑢𝑟
𝑡
𝑃𝑒𝑠𝑠
 
(28)
(2) Constraints 
Energy storage installation quantity constraint: 
𝑁ess ≤𝑁ess,max 
(29)
where Ness,max denotes the upper limit on the number of installed energy storage units. 
SOC constraints of the ESS: 
𝑆ess,min ≤𝑆𝑒𝑠𝑠
𝑡
≤𝑆ess,max 
(30)
where Sess,max and Sess,min denote the upper and lower bounds of the SOC of the ESS, respec-
tively. 
Charging and discharging power constraints of the ESS: 
0 ≤𝑃𝑐ℎ1
𝑡
+ 𝑃𝑐ℎ2
𝑡
≤𝑃𝑐ℎ,𝑚𝑎𝑥 
(31)
0 ≤𝑃𝑑𝑐ℎ1
𝑡
+ 𝑃𝑑𝑐ℎ2
𝑡
≤𝑃𝑑𝑐ℎ,𝑚𝑎𝑥 
(32)
where Pch,max and Pdch,max denote the rated charging and discharging power of the ESS, re-
spectively; 𝑃𝑑𝑐ℎ1
𝑡
 represents the discharging power traded between ESOs and DGOs in 
period t. 
Charging and discharging power constraints for transactions between ESOs and 
DGOs: 
𝜂ch ∑𝑃𝑐ℎ1
𝑡
𝑇
𝑡=1
= ∑𝑃𝑑𝑐ℎ1
𝑡
𝜂𝑑𝑐ℎ
𝑇
𝑡=1
 
(33)
0 ≤𝑃𝑐ℎ1
𝑡
≤𝑃𝑑𝑔,𝑝𝑟𝑜
𝑡
−𝑃𝑑𝑔
𝑡 
(34)
Charging and discharging state constraints of the ESS: 
𝑥ch
𝑡+ 𝑥dch
𝑡
≤1 
(35)
where 𝑥ch
𝑡 and 𝑥dch
𝑡
 denote the charging and discharging state variables of the ESS in pe-
riod t, respectively, and 𝑥ch
𝑡∈[0,1], where 𝑥ch
𝑡= 0 indicates that the ESS is not charging



<!-- page 9/23 -->

Energies 2026, 19, 415 
9 of 23 
 
https://doi.org/10.3390/en19020415 
in period t, and 𝑥ch
𝑡= 1 indicates that it is in the charging state. Similarly, 𝑥dch
𝑡
∈[0,1], 
where 𝑥dch
𝑡
= 0 indicates that the ESS is not discharging in period t, and 𝑥dch
𝑡
= 1 indi-
cates that it is in the discharging state t. Equation (35) ensures that the ESS cannot be in 
the charging and discharging states simultaneously. 
3.4. Profit Model of Electricity Users 
Electricity users determine their DR actions based on electricity price signals and in-
centive mechanisms provided by the DNO, with the objective of maximizing their satis-
faction—or equivalently, their net benefit—from participating in load response programs. 
Two types of DR are considered in this study: IL and TL. IL refers to the reduction in 
electricity consumption during peak periods without altering consumption in other peri-
ods, in exchange for financial incentives from the utility. TL allows users to shift part of 
their electricity consumption from high-price peak periods to low-price valley periods, 
thereby reducing their electricity expenses. 
(1) Objective function 
Electricity users adjust their consumption behavior to maximize the additional reve-
nue obtained through participation in demand-side response programs. The objective 
function is formulated as 
max 𝐹l = 𝐹l,IL + 𝐹l,TL 
(36)
𝐹l,IL = ∑𝐸𝑙,𝐼𝐿
𝑇
𝑡=1
𝑃l,IL
𝑡 
(37)
𝐹l,TL = ∑𝐸𝑔,𝑠𝑒𝑙
𝑡
𝑇
𝑡=1
(𝑃l,IL
𝑡
+ 𝑃l,TL
𝑡
) 
(38)
where Fl denotes the annual additional revenue obtained by electricity users through par-
ticipation in demand-side response; Fl,IL represents the subsidy income from IL; Fl,TL de-
notes the reduction in electricity expenses resulting from TL; El,IL is the unit subsidy for 
IL; 𝑃l,IL
𝑡 represents the amount of load interruption in period t; 𝑃l,TL
𝑡
 denotes the quantity 
of load shifting in period t, where a negative value indicates load shifting into the period, 
and a positive value indicates load shifting out of the period. 
(2) Constraints 
IL constraints: 
𝑃l,IL,min
𝑡
≤𝑃l,IL
𝑡
≤𝑃l,IL,max
𝑡
 
(39)
where 𝑃l,IL,max
𝑡
 and 𝑃l,IL,min
𝑡
 denote the upper and lower limits of the IL in period t, re-
spectively. 
TL constraints: 
𝑃l,TL,min
𝑡
≤𝑃l,TL
𝑡
≤𝑃l,TL,max
𝑡
 
(40)
∑𝑃𝑙,𝑇𝐿
𝑡
𝑇
𝑡=1
= 0 
(41)
where 𝑃l,TL,max
𝑡
and 𝑃l,TL,min
𝑡
 denote the upper and lower limits of the TL in period t, re-
spectively. 
4. Coordinated Planning Model and Solution Method for SGLS in DN 
This study develops a coordinated planning model for SGLS in complex DN while 
incorporating the bounded rationality of multiple stakeholders. Electricity users



<!-- page 10/23 -->

Energies 2026, 19, 415 
10 of 23 
 
https://doi.org/10.3390/en19020415 
determine their consumption patterns based on electricity price signals and incentive 
mechanisms and subsequently provide their DR information to DNOs. Meanwhile, 
DGOs, DNOs, and ESOs engage in an evolutionary game, each pursuing its own profit-
maximization objective. By integrating user-side DR into the decision-making process, the 
proposed framework yields network reinforcement plans and DG/ESS capacity alloca-
tions that reflect the bounded rationality and interactive behavior of all participating 
stakeholders. 
4.1. Evolutionary Game Model for Multiple Stakeholders 
(1) Strategy sets of game participants 
In the evolutionary game, DGOs, DNOs, and ESOs are treated as three distinct pop-
ulations, denoted as Pdg, Pdn, and Pess, respectively. Each stakeholder constructs its strategy 
set based on its own decision variables, namely, DG installation capacity, network rein-
forcement scheme, and energy storage installation capacity. 
The strategy set of DGOs is defined as 𝑆dg = {𝑆dg1, 𝑆dg2, … , 𝑆dg𝑁}  where 𝑆dg𝑁=
{𝑁dg𝑁
1
, 𝑁dg𝑁
2
, ⋯, 𝑁dg𝑁
𝑀}, and 𝑁dg𝑁
𝑀 denotes the DG installation quantity at node M under the 
N-th strategy. The strategy set of DNOs is given by 𝑆dn = {𝑆dnl, 𝑆dn2, … , 𝑆dnN} , 𝑆dnN =
{𝑥dn,1
1,𝑁, 𝑥dn,2
1,𝑁, ⋯, 𝑥dn,nl
1,𝑁} , 𝑥dn,nl
1,𝑁
∈[0,1] , where 𝑥dn,nl
1,𝑁
= 0 indicates that line rnl is not con-
structed under the N-th strategy, and 𝑥dn,nl
1,𝑁
= 1 indicates that line rnl is constructed under 
the N-th strategy. The strategy set of ESOs is expressed as 𝑆ess = {𝑆ess1, 𝑆ess2, … , 𝑆ess𝑁} , 
𝑆ess𝑁= {𝑁ess𝑁
1
, 𝑁ess𝑁
2
, ⋯, 𝑁ess𝑁
𝑀
}, 𝑁ess𝑁
𝑀
 represents the number of storage units installed at 
node M under the N-th strategy. 
For each population, the probability that a particular strategy is selected is defined as 
follows: DGO strategy selection probabilities: 𝑝dg = {𝑝dg1, 𝑝dg2, … , 𝑝dgN} , where 𝑝dg1 +
𝑝dg2 + ⋯+ 𝑝dgN = 1; The probability that a strategy in the DNO’s strategy set is selected 
by individuals in population Pdn is denoted as 𝑝dn = {𝑝dnl, 𝑝dn2, … , 𝑝dnN} , where 𝑝dnl +
𝑝dn2 + ⋯+ 𝑝dnN = 1. Similarly, the probability that a strategy in ESO’s strategy set is se-
lected by individuals in population Pess is given by 𝑝ess = {𝑝ess1, 𝑝ess2, … , 𝑝ess𝑁} , where 
𝑝essl + 𝑝ess2 + ⋯+ 𝑝ess𝑁= 1. 
(2) Evolutionary Game Selection Mechanism 
In evolutionary-game theory, stakeholders are assumed to exhibit bounded rational-
ity, meaning that they cannot identify their optimal strategies at the outset. Instead, they 
iteratively adjust their strategies through learning and imitation, eventually converging 
to an evolutionarily stable strategy. The strategy adaptation process is governed by the 
replicator dynamic equations. The continuous-time replicator dynamics for the three pop-
ulations are expressed as 
{
𝑑𝑝𝑑𝑔𝑥/𝑑𝑡= 𝑝𝑑𝑔𝑥(𝑈𝑑𝑔𝑥−𝑈𝑑𝑔)
𝑑𝑝𝑑𝑛𝑦/𝑑𝑡= 𝑝𝑑𝑛𝑦(𝑈𝑑𝑛𝑦−𝑈𝑑𝑛)
𝑑𝑝𝑒𝑠𝑠𝑧/𝑑𝑡= 𝑝𝑒𝑠𝑠𝑧(𝑈𝑒𝑠𝑠𝑧−𝑈𝑒𝑠𝑠)
 
(42)
where pdgx is the probability that an individual in population Pdg selects strategy Sdgx; Udgx 
is the expected payoff of selecting strategy Sdgx; Udg denotes the average expected payoff 
of population Pdg. Similarly, pdny is the probability that an individual in population Pdn 
selects strategy Sdny; Udny is the expected payoff when strategy Sdny is selected; Udn repre-
sents the average expected payoff of population Pdn. Likewise, pessz is the probability that 
an individual in population Pess selects strategy Sessz; Uessz is the expected payoff associated 
with strategy Sessz; and Uess denotes the average expected payoff of population Pess. 
Let the pure strategy sets of DGOs, DNOs, and ESOs be Sdg = {1,…,X}, Sdn = {1,…,Y}, 
and Sess = {1,…,Z}, respectively. For any strategy profile (x,y,z) ∈ Sdg × Sdn × Sess, denote the 
resulting payoffs (profits) of the three stakeholders by Πdg(x,y,z), Πdn (x,y,z), and Πess



<!-- page 11/23 -->

Energies 2026, 19, 415 
11 of 23 
 
https://doi.org/10.3390/en19020415 
(x,y,z), which are obtained by evaluating the corresponding profit models in Section 3 un-
der the planning/operation outcomes associated with(x,y,z). 
Given the mixed-strategy probabilities pdgx, pdny, and pessz, the expected payoffs of 
choosing strategy 𝑥, 𝑦, and 𝑧 are calculated as 
𝑈𝑑𝑔𝑥= ∑∑𝑝𝑑𝑛𝑦
𝑍
𝑧=1
𝑌
𝑦=1
 𝑝𝑒𝑠𝑠𝑧 𝛱𝑑𝑔(𝑥, 𝑦, 𝑧) 
(43)
𝑈𝑑𝑛𝑦= ∑∑𝑝𝑑𝑔𝑥
𝑍
𝑧=1
𝑋
𝑥=1
 𝑝𝑒𝑠𝑠𝑧 𝛱𝑑𝑛(𝑥, 𝑦, 𝑧) 
(44)
𝑈𝑒𝑠𝑠𝑧= ∑∑𝑝𝑑𝑔𝑥
𝑌
𝑦=1
𝑋
𝑥=1
 𝑝𝑑𝑛𝑦 𝛱𝑒𝑠𝑠(𝑥, 𝑦, 𝑧) 
(45)
Accordingly, the average expected payoffs of the three populations are 
𝑈𝑑𝑔= ∑𝑝𝑑𝑔𝑥
𝑋
𝑥=1
𝑈𝑑𝑔𝑥, 𝑈𝑑𝑛= ∑𝑝𝑑𝑛𝑦
𝑌
𝑦=1
𝑈𝑑𝑛𝑦, 𝑈𝑒𝑠𝑠= ∑𝑝𝑒𝑠𝑠𝑧
𝑍
𝑧=1
𝑈𝑒𝑠𝑠𝑧 
(46)
In numerical simulations, Equation (47) is discretized using a simulation step size as 
follows: 
{
𝑝𝑑𝑔𝑥(𝑘+ 1) = 𝑝𝑑𝑔𝑥(𝑘) + 𝜆𝑑𝑔𝑝𝑑𝑔𝑥(𝑘)[𝑈𝑑𝑔𝑥(𝑘) −𝑈𝑑𝑔(𝑘)]
𝑝𝑑𝑛𝑦(𝑘+ 1) = 𝑝𝑑𝑛𝑦(𝑘) + 𝜆𝑑𝑛𝑝𝑑𝑛𝑦(𝑘)[𝑈𝑑𝑛𝑦(𝑘) −𝑈𝑑𝑛(𝑘)]
𝑝𝑒𝑠𝑠𝑧(𝑘+ 1) = 𝑝𝑒𝑠𝑠𝑧(𝑘) + 𝜆𝑒𝑠𝑠𝑝𝑒𝑠𝑠𝑧(𝑘)[𝑈𝑒𝑠𝑠𝑧(𝑘) −𝑈𝑒𝑠𝑠(𝑘)
 
(47)
where pdgx(k) and pdgx(k + 1) denote the probabilities that an individual in population Pdg 
selects strategy Sdgx in iterations k and k + 1, respectively; λdg is the simulation step size for 
population Pdg. Similarly, pdny(k) and pdny(k + 1) represent the probabilities that an individ-
ual in population Pdn selects strategy Sdnx in iterations k and k + 1, respectively; λdn is the 
simulation step size for population Pdn. Likewise, Pessz(k) and Pessz(k + 1) are the probabili-
ties that an individual in population Pess selects strategy Ssz in iterations k and k + 1, re-
spectively; λess is the simulation step size for population Pess. 
To enable evolutionary-game simulation with finite strategy sets, the decision varia-
bles of each stakeholder are discretized according to the physical installation granularity 
and the corresponding upper bounds. For DGOs, the strategy is represented by integer 
DG unit numbers deployed at candidate buses, subject to the maximum installation limits. 
For DNOs, each candidate reinforcement line is modeled as a binary decision (0: not con-
structed, 1: constructed). For ESOs, the storage planning strategy is defined by the integer 
number of storage units installed at candidate buses, bounded by the maximum allowable 
number. The discretization ranges are consistent with the investment and technical con-
straints defined in Section 3, and therefore, the strategy sets cover feasible investment de-
cisions under the adopted planning assumptions. 
4.2. Solution Method for the Coordinated SGLS Planning Model 
This study develops a coordinated planning model for SGLS in DNs that accounts 
for the bounded rationality of multiple stakeholders. The evolutionary-game algorithm is 
integrated into the solution process, and the overall procedure is illustrated in Figure 2. 
The detailed steps for solving the planning model are as follows: 
(1) Generation and screening of strategy sets: DGOs, DNOs and ESOs generate candi-
date strategies by enumerating discretized decision variables within their admissible 
ranges. To avoid including evidently infeasible candidates, strategies violating basic 
installation limits are removed directly. For the remaining candidates, feasibility is



<!-- page 12/23 -->

Energies 2026, 19, 415 
12 of 23 
 
https://doi.org/10.3390/en19020415 
further checked during payoff evaluation under the operational constraints; infeasi-
ble strategies are discarded so that they will not survive in the evolutionary process. 
By enumerating all discretized combinations within the prescribed ranges, the strat-
egy space ensures coverage of potential optimal solutions under the adopted discreti-
zation granularity. 
(2) Initialization of populations: The initial populations for DGOs, DNOs, and ESOs are 
randomly generated to serve as the starting point of the evolutionary game. 
(3) Evolutionary-game process: (a) Electricity users determine their consumption behav-
ior by synthesizing TOU pricing information and incentive mechanisms provided by 
the DNO. The resulting DR-adjusted load profile is then passed to the DNO; (b) in-
dividuals in each population randomly select strategies from their corresponding 
strategy sets until all strategies have been sampled; (c) for each combination of strat-
egies, the profit function and payoff of each individual are computed; (d) the ex-
pected payoff of each strategy and the average expected payoff of each population 
are obtained; (e) based on the replicator dynamic equations, the strategy selection 
probabilities of each population are updated. 
(4) Iteration: Steps (3) are repeated until the evolutionary process converges to an evo-
lutionarily stable state. 
(5) Output: Upon convergence, the model outputs: the DNO’s network reinforcement 
scheme; DGO’s DG capacity allocation strategy; ESO’s storage capacity configura-
tion; electricity user consumption schedules after participating in DR. 
 
Figure 2. Flowchart of the model solution process. 
5. Case Study Analysis 
5.1. Key Assumptions and Baseline Settings 
To validate the proposed source–network–load–storage collaborative planning 
model, a case study is conducted on the IEEE 33-bus distribution system. The original



<!-- page 13/23 -->

Energies 2026, 19, 415 
13 of 23 
 
https://doi.org/10.3390/en19020415 
system capacity is 3715 kW + j2300 kvar, and its initial topology is shown in Figure 3. To 
accommodate the continuously growing load demand, four new load buses (Bus 34–37) 
are added in Table 1. After the expansion, the maximum system load increases to 4175 kW 
+ j2560 kvar. Candidate lines for network reinforcement are marked with red dashed lines; 
the construction cost is CNY 100,000/km, and the line resistance and reactance are 0.27 
Ω/km and 0.40 Ω/km, respectively. The corresponding line lengths and node connections 
are listed in Table 1. The purchasing price of electricity from the upper-level grid is set to 
CNY 0.4/kWh. The planning horizon is 10 years, and the annual discount rate is 6%. The 
discount rate mainly affects the planning outcomes through the capital recovery factor 
(CRF), which annualizes the upfront investments of DG, network reinforcement, and ESSs 
into comparable annual costs, and therefore, influences the payoff evaluation of long-term 
strategies. 
 
Figure 3. Topology of the DN. 
Table 1. Locations and lengths of newly added nodes. 
To bus 
From Bus 
Line Length (km) 
34 
9 
3.34 
10 
3.08 
11 
2.47 
35 
19 
2.46 
20 
2.08 
21 
3.69 
22 
3.39 
36 
23 
2.72 
24 
2.1 
25 
2.28 
26 
1.91 
37 
29 
3.52 
30 
2.06 
31 
2.13 
32 
2.48 
On the demand side, all loads are assumed to be TLs participating in price-based DR. 
The TOU tariff structure is provided in Table 2. The parameters of DG and ESSs used in 
this case study are summarized in Table 3. The peak–valley price spread determines the 
strength of the price signal, directly shaping both (i) the arbitrage potential of ESSs (charg-
ing at low-price hours and discharging at high-price hours) and (ii) the incentive for de-
mand shifting in the DR module; hence, it is a key driver of benefit allocation among 
DNOs/ESOs (and the overall coordination effect). Bus 25 is designated as an IL node, with



<!-- page 14/23 -->

Energies 2026, 19, 415 
14 of 23 
 
https://doi.org/10.3390/en19020415 
the interruptible period defined as 11:00–22:00 and an IL compensation rate of CNY 
0.4/kWh. 
Table 2. TOU electricity price parameters. 
Time Period 
Electricity Price (CNY·kWh−1) 
Peak 8:00–10:00, 16:00–21:00 
0.575 
Shoulder 5:00–8:00, 10:00–11:00, 14:00–16:00, 21:00–23:00 
0.425 
Valley 00:00–5:00, 11:00–14:00, 23:00–24:00 
0.325 
Table 3. Parameters of wind power, photovoltaic generation, and energy storage systems. 
Type 
Parameter 
Value 
wind 
Maximum installation capacity (kW) 
600 
Investment cost (CNY·kWh−1) 
4000 
O&M cost (CNY·kWh−1) 
0.15 
Electricity selling price (CNY·kWh−1) 
0.2 
Candidate installation buses 
5, 13, 21, 33 
PV 
Maximum installation capacity (kW) 
600 
Investment cost (CNY·kWh−1) 
4000 
O&M cost (CNY·kWh−1) 
0.15 
Electricity selling price (CNY·kWh−1) 
0.34 
Candidate installation bus 
28 
ESS 
Maximum installation capacity 
240 kW/800 kWh 
Investment cost (CNY·kWh−1) 
600 
O&M cost (CNY·kWh−1) 
0.01 
Upper/lower SOC limits 
0.9/0.1 
Charging/discharging efficiency 
0.9 
Candidate installation buses 
17, 32 
The initial time-series data for load and renewable generation are obtained from the 
operation records of a real distribution network in Northeast China. Specifically, a full-
year dataset (January–December, 365 days) is collected, including hourly active-power 
demand at the feeder/substation level and the aggregated hourly active-power outputs of 
grid-connected wind and photovoltaic units in the same area (Δt = 1 h). Prior to scenario 
extraction, the raw data are time-aligned and cleaned by filling occasional missing sam-
ples via linear interpolation and filtering abnormal spikes using a standard z-score rule. 
Finally, the load, wind, and PV series are normalized by their annual maxima to form per-
unit profiles for subsequent clustering and planning analysis. 
Based on the preprocessed one-year dataset, each day is represented by concatenat-
ing the 24 h per-unit profiles of load, wind power, and photovoltaic generation. A Gauss-
ian mixture model (GMM) is employed to cluster these daily vectors into four representa-
tive typical-day scenarios. The cluster centroids and their occurrence probabilities are 
used to construct the typical-day profiles shown in Figure 4, which are then used for sub-
sequent planning and simulation analysis. In practical operation, such typical-day profiles 
can also be constructed from short-term forecasts; for example, machine-learning PV fore-
casting models can provide day-ahead inputs to support operational optimization in de-
centralized systems [26]. 
All numerical experiments are implemented in MATLAB 2025b. The demand-re-
sponse scheduling of electricity users is formulated as a linear programming problem and 
solved using the Optimization Toolbox solver linprog. The evolutionary-game simulation 
is performed by a discrete-time replicator-dynamics iteration with Monte Carlo sampling



<!-- page 15/23 -->

Energies 2026, 19, 415 
15 of 23 
 
https://doi.org/10.3390/en19020415 
until convergence. Typical-day clustering is conducted via a GMM using the Statistics and 
Machine 
Learning 
Toolbox 
(https://ww2.mathworks.cn/products/statis-
tics.html?s_tid=AO_PR_info, accessed on 15 December 2025). 
 
Figure 4. Typical-day profiles of load, wind power, and photovoltaic generation. 
5.2. Results Analysis 
Under consideration of user-side DR, the proposed collaborative planning model in-
corporates the bounded rationality of stakeholders and determines the optimal planning 
scheme for DN reinforcement, DG deployment, and ESS allocation through an evolution-
ary game among DGOs, DNOs, and ESOs. 
The evolutionary stable strategies emerging from the game, along with the corre-
sponding variations in strategy selection probabilities during the evolution process, are 
illustrated in Figure 5. 
0
6
12
18
24
0.0
0.2
0.4
0.6
0.8
1.0
 Load
 PV
 WT
per-unit value
Typical Day 1
0
6
12
18
24
0.0
0.2
0.4
0.6
0.8
1.0
per-unit value
Typical Day 2
0
6
12
18
24
0.0
0.2
0.4
0.6
0.8
1.0
per-unit value
Typical Day 3
0
6
12
18
24
0.0
0.2
0.4
0.6
0.8
1.0
per-unit value
Typical Day 4



<!-- page 16/23 -->

Energies 2026, 19, 415 
16 of 23 
 
https://doi.org/10.3390/en19020415 
 
Figure 5. Convergence curves of the evolutionary game. 
During the evolutionary process, the strategy selection probabilities of DGOs, DNOs, 
and ESOs are continuously updated with each iteration. Ultimately, the probability of se-
lecting a single strategy converges to 1, while the probabilities associated with all other 
strategies converge to 0. This indicates that, as the iterations progress, individuals within 
each population gradually refine their strategic choices through continuous learning and 
imitation, eventually reaching an evolutionarily stable state. The evolutionary-game ap-
proach effectively captures the bounded rationality of real-world decision-makers and 
highlights the iterative process through which agents converge by repeatedly learning, 
imitating, and adjusting strategies. 
(1) Allocation and Profit Analysis of Source–Grid–Storage Planning 
To further assess how different typical-day scenarios influence the benefit structure 
of the coordinated SGLS planning model, Table 4 presents the optimal installation capac-
ities of DG and energy storage under four representative typical days. The ten-year total 
revenues and corresponding net present values (NPV) for DGOs, DNOs, and ESOs are 
summarized in Table 5. The results indicate that the load profiles and renewable output 
patterns associated with different typical days significantly affect both the overall system 
economics and the benefit distribution among stakeholders. 
Table 4. Installed capacities of distributed generation and energy storage under typical-day scenar-
ios. 
Typical Day 
Indicator 
Installed Capacity 
1 
wind 
1900 kW 
PV 
0 
ESS 
1600 kWh 
2 
wind 
2150 kW 
PV 
250 kW 
ESS 
1600 kWh 
3 
wind 
1900 kW 
PV 
0 
ESS 
1600 kWh 
4 
wind 
2150 kW 
PV 
250 kW 
ESS 
1600 kWh 
0
5
10
15
20
25
0.0
0.2
0.4
0.6
0.8
1.0
maximum population proportion
number of iterations
 max(pdg)
 max(pdn)
 max(pess)



<!-- page 17/23 -->

Energies 2026, 19, 415 
17 of 23 
 
https://doi.org/10.3390/en19020415 
Table 5. Revenues of different stakeholders under typical-day scenarios. 
Typical Day 
Stakeholder 
Ten-Year Total Revenue 
(104 CNY) 
Ten-Year Net Revenue 
(104 CNY) 
1 
DGO 
615 
453 
DNO 
2234 
1644 
ESO 
26 
19 
2 
DGO 
653 
481 
DNO 
2441 
1796 
ESO 
26 
19 
3 
DGO 
69 
51 
DNO 
1628 
1198 
ESO 
26 
19 
4 
DGO 
870 
640 
DNO 
2697 
1985 
ESO 
26 
19 
As shown in Table 4, the optimal DG and ESS installation schemes across the four 
typical days exhibit both consistency and scenario-specific diversity. 
First, in Typical Day 1 and Typical Day 3, the model selects the same configuration—
1900 kW of wind, 0 kW of PV capacity, and 1600 kWh of storage. This reflects that, under 
the load–resource conditions represented by these two typical days, wind power provides 
higher utilization potential than PV. PV generation is not selected because the early-morn-
ing and evening load levels are relatively high or the midday load is insufficient to absorb 
PV output, leading to limited economic benefits. This indicates that the load curves and 
renewable-resource characteristics of Typical Days 1 and 3 are more compatible with wind 
power as the primary renewable resource. 
Second, in Typical Days 2 and 4, the model deploys a portfolio of 2150 kW of wind, 
250 kW of PV capacity, and 1600 kWh of storage. Unlike Typical Days 1 and 3, the appear-
ance of non-zero PV installation in Typical Days 2 and 4 implies that the midday load is 
higher or the matching between PV output and demand is stronger, allowing PV to pro-
vide effective energy substitution during peak periods and thereby improve system eco-
nomics. The increase in wind capacity from 1900 kW to 2150 kW further suggests that, 
under these scenarios, the marginal benefit of wind generation increases due to more fa-
vorable resource conditions, enabling wind and PV to operate synergistically. 
It is noteworthy that the optimal storage capacity remains constant at 1600 kWh 
across all typical-day scenarios. This indicates that, within this planning context, storage 
primarily functions to perform peak shaving and valley filling, increase renewable energy 
accommodation, and reduce power purchase costs. The variations in load shapes across 
typical days are insufficient to motivate the model to expand storage capacity. Thus, stor-
age sizing is influenced more by price signals and the overall system economic structure 
than by the characteristics of individual typical days. 
These findings demonstrate that typical-day clustering effectively captures the struc-
tural differences in annual load patterns and renewable output characteristics. The result-
ing optimal configurations exhibit clear structural regularities: when PV is poorly aligned 
with the load profile, the model tends to favor larger wind installations; conversely, when 
midday loads are higher or wind-PV complementarities are stronger, a combined wind-
PV configuration emerges. This validates the capability of the typical-day-based optimi-
zation framework to autonomously select economically optimal SGLS configurations un-
der diverse resource and load scenarios.



<!-- page 18/23 -->

Energies 2026, 19, 415 
18 of 23 
 
https://doi.org/10.3390/en19020415 
Analysis of the data in Table 5 reveals that typical-day variations exert a significant 
influence on the ten-year total and net revenues of DGOs, the DNO, and ESOs. However, 
the sensitivity of each stakeholder to these variations differs markedly. 
From the perspective of DGOs, revenue exhibits a clear upward trend as the typical-
day index increases. The ten-year total revenue rises from CNY 6.15 million in Typical 
Day 1 to CNY 8.70 million in Typical Day 4, while the corresponding net revenue increases 
from CNY 4.53 million to CNY 6.42 million. This indicates that typical days characterized 
by more favorable renewable output conditions significantly enhance DG substitution ca-
pability and profitability. The highest DG revenue occurs under Typical Day 4, suggesting 
that this daily load profile and renewable availability pattern provides the most advanta-
geous conditions for DG utilization. 
Note that the unusually low DGO revenue on Typical Day 3 is caused by the renew-
able-resource condition represented by this typical-day scenario. As shown in Figure 4, 
Typical Day 3 corresponds to a low renewable-output (particularly low wind) profile. 
Since the planning configuration under Typical Day 3 installs wind at only 1900 kW with 
0 PV, the DGO’s revenue is almost entirely determined by wind electricity sales. Conse-
quently, the limited wind availability, together with the relatively lower load level indi-
cated by the reduced DNO revenue in Table 5, results in a much smaller amount of re-
newable energy being utilized and sold, leading to the sharp decline in DGO revenue, 
CNY 69 × 104. 
DNOs consistently achieves the highest revenue among the three stakeholders. Its 
ten-year total revenue increases from CNY 22.34 million (Typical Day 1) to CNY 26.97 
million (Typical Day 4), while net revenue increases from CNY 16.44 million to CNY 19.85 
million. The monotonic increase reflects that Typical Day 4 is associated with the highest 
overall load level and the largest electricity purchase volume, enabling the grid to earn 
more through retail electricity sales. In contrast, Typical Day 3 results in significantly 
lower total revenue (CNY 16.28 million) and net revenue (CNY 11.98 million), highlight-
ing the adverse impact of lower load levels on grid-side economic returns. 
In comparison, the revenues of the ESS remain highly stable across all four typical 
days. The ten-year total revenue remains approximately CNY 260,000, with net present 
values around CNY 190,000, indicating minimal sensitivity to typical-day variation. This 
stability suggests that, under the current TOU price structure and modest peak–valley 
price differentials, the profitability of small-scale ESS installations is driven primarily by 
fixed arbitrage opportunities rather than renewable variability. Moreover, ESS profitabil-
ity is considerably lower than that of DG and DN, highlighting that the existing market 
mechanism does not fully compensate for the flexibility value provided by storage in peak 
shaving, load shifting, and renewable accommodation. To stimulate investment in inde-
pendent storage, additional incentive mechanisms—such as capacity payments, ancillary-
service compensation, or increased peak–valley price spreads—may be needed. 
From a market-design perspective, the above mechanisms can be viewed as mone-
tizing different components of the flexibility value provided by ESS. A capacity remuner-
ation scheme can compensate storage for firm capacity and peak support that are not fully 
reflected by energy arbitrage under a modest peak–valley spread. Ancillary-service mar-
kets (e.g., regulation and reserves) provide an additional revenue stream that rewards fast 
response and ramping capability. Moreover, enlarging the peak–valley spread or adopt-
ing more granular time-varying pricing can strengthen the arbitrage signal, thereby im-
proving ESO investment incentives. These measures are complementary and could be im-
plemented through performance-based payments or long-term contracts. 
The economic comparison across the four typical days demonstrates that load shapes 
and renewable generation patterns directly determine the benefit distribution within the 
SGLS system. Higher peak loads and larger peak–valley price spreads significantly



<!-- page 19/23 -->

Energies 2026, 19, 415 
19 of 23 
 
https://doi.org/10.3390/en19020415 
increase DG and DNO revenues. When renewable energy generation aligns more closely 
with high-price periods, DG profitability improves further due to reduced curtailment 
and enhanced substitution of grid electricity. Composite wind-PV configurations outper-
form single-resource configurations in most scenarios, reflecting their superior adaptabil-
ity to diverse load conditions. Meanwhile, ESS revenue remains stable but relatively low, 
suggesting that its flexibility value is not fully monetized under current electricity pricing 
mechanisms. 
Overall, the classification and weighting of typical days exert a substantial impact on 
the economic evaluation of the system. They shape renewable energy utilization, influence 
the effectiveness of price signals, and determine the revenue distribution among stake-
holders. Thus, typical-day selection is a critical component of comprehensive energy sys-
tem planning. 
The behavioral characteristics of the four typical-day scenarios significantly affect the 
economic performance of the coordinated SGLS planning schemes. Compared with sin-
gle-source renewable configurations, wind-PV hybrid deployments yield superior eco-
nomic outcomes, particularly under Typical Day 4, where all stakeholders achieve their 
highest ten-year revenues. Furthermore, under the existing pricing mechanism, DNOs re-
main the primary beneficiary, whereas ESO gains limited economic return—underscoring 
the necessity of refining compensation mechanisms to enhance the attractiveness of ESS 
investment. 
(2) Necessity of Considering Multi-Agent Game Mechanisms 
To evaluate the necessity of incorporating a multi-agent evolutionary game into the 
planning framework, we compare the complex DN planning outcomes and stakeholder 
revenue distributions with and without the game-theoretic mechanism. The resulting 
planning decisions are presented in Table 6, while the revenues of different stakeholders 
are summarized in Table 7. 
Table 6. Distribution network planning results. 
 
Indicator 
Installed Capacity 
With game-theoretic interac-
tion 
wind 
1900 kw 
PV 
0 
ESS 
1600 kwh 
Without game-theoretic in-
teraction 
wind 
1900 kw 
PV 
0 
ESS 
0 
Table 7. Revenues of different stakeholders. 
Typical Day 
Stakeholder 
Ten-Year Total Revenue 
(104 CNY) 
Ten-Year Net Revenue 
(104 CNY) 
With game-theo-
retic interaction 
DG 
615 
453 
Grid 
2234 
1644 
ESS 
26 
19 
Without game-the-
oretic interaction 
DG 
615 
453 
Grid 
2308 
1699 
ESS 
0 
0 
As shown in Table 6, the incorporation of a multi-agent game mechanism has a sub-
stantial impact on both the planning outcomes and the distribution of benefits among 
stakeholders. When the game-theoretic interaction is considered, the system deploys 1900 
kW of WT, 0 kW of PV, and 1600 kWh of energy storage. This allocation enables ESOs to 
earn stable profits through price arbitrage. In contrast, when the game mechanism is not



<!-- page 20/23 -->

Energies 2026, 19, 415 
20 of 23 
 
https://doi.org/10.3390/en19020415 
considered, the storage investment is completely eliminated by the planning model. This 
indicates that conventional single-objective planning tends to prioritize the interests of 
DNOs and fails to reflect the investment incentives of ESOs. 
In terms of revenues, Table 7 shows that DG earnings remain unchanged between 
the two scenarios. DNO’s revenue increases slightly in the non-game scenario due to 
higher electricity purchases; however, ESO’s revenue drops to zero, resulting in weakened 
coordination among stakeholders. By comparison, the game-theoretic approach not only 
enables reasonable storage deployment but also yields a system-wide revenue structure 
that more closely matches the interactions observed in real electricity markets. These re-
sults confirm the necessity and rationality of introducing evolutionary-game mechanisms 
into SGLS coordinated planning. 
(3) Impact of DR on benefit allocation and coordination 
To evaluate how DR affects multi-stakeholder coordination, we compare two scenar-
ios—with DR and without DR—across four typical-day cases (Tables 5 and 8), focusing 
on the 10-year total and net revenues of the DNO, DGO, and ESO. 
DNO: In all typical days, the DNO’s revenues decrease after DR is introduced. For 
Typical Day 1, the 10-year total revenue drops from CNY 25.02 to 22.34 million, and the 
net revenue decreases from CNY 18.41 to 16.44 million. This indicates that DR suppresses 
peak demand via load-side regulation, reducing the DNO’s margin associated with high-
price periods and high-load operation, and confirming a clear peak-shaving effect. 
DGO: The DGO’s revenues remain unchanged under both scenarios for all typical 
days (e.g., CNY 6.15 million total and CNY 4.53 million net in Typical Day 1). This sug-
gests that, under the current case settings, DR does not directly affect DG output or reve-
nue; system improvements are achieved through load adjustment rather than reducing 
renewable returns. 
ESO: In contrast, the ESO benefits from DR in all typical days. For Typical Day 1, the 
ESO’s 10-year total revenue increases from CNY 0.21 to 0.26 million, and the net revenue 
rises from CNY 0.15 to 0.19 million. DR improves the operating environment and provides 
more stable opportunities for storage, enhancing its economic performance. 
Overall, DR reshapes the benefit-allocation structure while keeping DGO revenues 
stable, indicating a shift in regulation responsibility from the grid side toward the load-
and-storage side and clarifying functional coordination among SGLS entities. 
Table 8. The revenues of each stakeholder without considering DR. 
Typical Day 
Stakeholder 
Ten-Year Total Revenue 
(104 CNY) 
Ten-Year Net Revenue 
(104 CNY) 
1 
DG 
615 
453 
Grid 
2502 
1841 
ESS 
21 
15 
2 
DG 
653 
481 
Grid 
2650 
1951 
ESS 
21 
15 
3 
DG 
69 
51 
Grid 
1856 
1366 
ESS 
21 
15 
4 
DG 
870 
640 
Grid 
2926 
2154 
ESS 
21 
15



<!-- page 21/23 -->

Energies 2026, 19, 415 
21 of 23 
 
https://doi.org/10.3390/en19020415 
6. Conclusions 
This study develops a multi-agent evolutionary-game-based coordinated planning 
model for active DNs under high renewable energy penetration. By integrating DGOs, 
DNOs, ESOs, and user-side DR, the proposed framework captures the strategy learning 
and dynamic adjustment processes of stakeholders under bounded rationality. It enables 
coordinated optimization of SGLS resources with respect to economic efficiency, opera-
tional security, and system flexibility. The case studies demonstrate the following key 
findings: 
(1) The evolutionary game mechanism effectively drives the strategies of the three oper-
ators toward an evolutionarily stable equilibrium, thereby avoiding the suboptimal 
configurations that commonly arise in conventional planning due to conflicting 
stakeholder objectives. 
(2) Distinct installation patterns emerge across typical-day scenarios. On days where the 
load profile aligns poorly with PV output, the system favors wind-dominated con-
figurations. Conversely, when solar irradiance is strong and midday demand is high, 
a complementary wind-PV deployment becomes the optimal choice. 
(3) Benefit analysis reveals substantial heterogeneity among stakeholders. DNOs remain 
the primary beneficiary, while DG profits increase with improved renewable gener-
ation conditions. ESS revenues, however, remain relatively stable but modest, indi-
cating that the current market mechanisms still fall short of fully reflecting the sys-
tem-level flexibility value provided by storage. 
Overall, the proposed evolutionary-game-based coordinated planning framework 
provides an effective theoretical foundation and methodological reference for promoting 
multi-agent collaboration and maximizing renewable energy utilization in active DNs. 
Author Contributions: Conceptualization, Y.S., X.L., X.W. and L.J.; methodology, R.Z. and D.W.; 
software, X.W. and L.J.; formal analysis, X.G.; investigation, Y.Y.; resources, X.L.; data curation, J.W. 
and X.X.; writing—original draft preparation, Y.L.; writing—review and editing, Z.O. and Z.M. All 
authors have read and agreed to the published version of the manuscript. 
Funding: This research was funded by the Research on Business Models of Source–Grid–Load–
Storage Coordinated Demand Response under the Revitalization of Northeast China’s Old Indus-
trial Base, 2025 (SGJLJY00LNJS2500036). 
Data Availability Statement: Data available on request due to restrictions privacy. The data pre-
sented in this study are available on request from the corresponding author because the modeled 
data for this study was obtained from the corresponding author, and the raw data required permis-
sion from the first author. 
Conflicts of Interest: Authors Yu Shi, Yiwen Yao, Jing Wang, Xiaomin Lu, Xinhong Wang, Din-
gheng Wang, Xuefeng Gao and Xin Xu were employed by the Power Economic Research Institute 
of Jilin Electric Power Co., Ltd. Author Rui Zhou was employed by State Grid Jilin Electric Power 
Co., Ltd. The remaining authors declare that the research was conducted in the absence of any com-
mercial or financial relationships that could be construed as a potential conflict of interest. This 
study was supported and sponsored by Power Economic Research Institute of Jilin Electric Power 
Co., Ltd. and State Grid Jilin Electric Power Co., Ltd. State Key Laboratory of Coastal and Offshore 
Engineering, Dalian University of Technology completed the study and informed Power Economic 
Research Institute of Jilin Electric Power Co., Ltd. and State Grid Jilin Electric Power Co., Ltd. of the 
results, which were published with Power Economic Research Institute of Jilin Electric Power Co., 
Ltd. and State Grid Jilin Electric Power Co., Ltd.’s permission. There are no other conflicts of in-
terest.



<!-- page 22/23 -->

Energies 2026, 19, 415 
22 of 23 
 
https://doi.org/10.3390/en19020415 
Reference 
1. 
Adewuyi, O.B.; Aki, H. Optimal planning for high renewable energy integration considering demand response, uncertainties, 
and operational performance flexibility. Energy 2024, 313, 134021. 
2. 
Dini, A.; Hassankashi, A.; Pirouzi, S.; Lehtonen, M.; Arandian, B.; Baziar, A.A. A flexible-reliable operation optimization model 
of the networked energy hubs with distributed generations, energy storage systems and demand response. Energy 2022, 239, 
121923.  
3. 
Wang, C.; Liu, C.; Chen, J.; Zhang, G. Cooperative planning of renewable energy generation and multi-timescale flexible re-
sources in active distribution networks. Appl. Energy 2024, 356, 122429.  
4. 
Li, A.; Xiao, F.; Zhang, C.; Fan, C. Attention-based interpretable neural network for building cooling load prediction. Appl. 
Energy 2021, 299, 117238.  
5. 
Zhang, J.; Wang, C.; Zuo, J.; Gao, C.; Zheng, S.; Cheng, R.; Duan, Y.; Wang, Y. Multi-Stage Rolling Grid Expansion Planning for 
Distribution Networks Considering Conditional Value at Risk. Energies 2024, 17, 5134.  
6. 
Cai, D.; Wang, Z.; Miao, S.; Chen, R.; Zheng, Z.; Zhou, K. Wind-Photovoltaic-Energy Storage System Collaborative Planning 
Strategy Considering the Morphological Evolution of the Transmission and Distribution Network. Energies 2022, 15, 1481.  
7. 
Gao, H.; Li, Y.; He, S.; Tang, Z.; Liu, J. Distributionally robust planning for power distribution network considering multi-energy 
station enabled integrated demand response. Energy 2024, 306, 132460.  
8. 
He, Y.; Wu, H.; Bi, R.; Qiu, R.; Ding, M.; Sun, M.; Xu, B.; Sun, L. Coordinated planning of distributed generation and soft open 
points in active distribution network based on complete information dynamic game. Int. J. Electr. Power Energy Syst. 2022, 138, 
107953.  
9. 
Song, X.; Shu, M.; Wei, Y.; Liu, J. A Study on the Multi-Agent Based Comprehensive Benefits Simulation Analysis and Syner-
gistic Optimization Strategy of Distributed Energy in China. Energies 2018, 11, 3260.  
10. 
Dong, X.; Quan, C.; Jiang, T. Optimal Planning of Integrated Energy Systems Based on Coupled CCHP. Energies 2018, 11, 2621.  
11. 
Li, J.; Wang, T.; Tang, S.; Jiang, J.; Chen, S. Planning distribution network using the multi-agent game and distribution system 
operators. Front. Energy Res. 2023, 11, 1244394.  
12. 
Wang, C.; Liu, C.; Zhou, X.; Zhang, G. Flexibility-based expansion planning of active distribution networks considering optimal 
operation of multi-community integrated energy systems. Energy 2024, 307, 132601.  
13. 
Zhou, M.; Ma, F.; Jin, W. Long-term cost planning of data-driven wind-storage hybrid systems. Renew. Energy 2024, 223, 120073.  
14. 
Mao, Y.; Yuan, J.; Jiao, X. Optimal Operation of Combined Cooling, Heating, and Power Systems with High-Penetration Re-
newables: A State-of-the-Art Review. Processes 2025, 13, 2595.  
15. 
Liu, Y.; Yang, N.; Dong, B.; Wu, L.; Yan, J.; Shen, X.; Xing, C.; Liu, S.; Huang, Y. Multi-Lateral Participants Decision-Making: A 
Distribution System Planning Approach with Incomplete Information Game. IEEE Access 2020, 8, 88933–88950.  
16. 
Saldaña-González, A.E.; Aragüés-Peñalba, M.; Sumper, A. Distribution network planning method: Integration of a recurrent 
neural network model for the prediction of scenarios. Electr. Power Syst. Res. 2024, 229, 110125.  
17. 
Mehrjerdi, H. Simultaneous load leveling and voltage profile improvement in distribution networks by optimal battery storage 
planning. Energy 2019, 181, 916–926.  
18. 
Suryakiran, B.V.; Nizami, S.; Verma, A.; Saha, T.K.; Mishra, S. A DSO-based day-ahead market mechanism for optimal opera-
tional planning of active distribution network. Energy 2023, 282, 128902.  
19. 
Mao, Y.; Cai, Z.; Jiao, X.; Long, D. Multi-timescale optimization scheduling of integrated energy systems oriented towards gen-
eralized energy storage services. Sci. Rep. 2025, 15, 8549. 
20. 
Budi, R.F.S.; Sarjiya; Hadi, S.P. Multi-level game theory model for partially deregulated generation expansion planning. Energy 
2021, 237, 121565.  
21. 
Yang, N.; Xiong, Z.; Ding, L.; Liu, Y.; Wu, L.; Liu, Z.; Shen, X.; Zhu, B.; Li, Z.; Huang, Y. A game-based power system planning 
approach considering real options and coordination of all types of participants. Energy 2024, 312, 133400.  
22. 
Zhou, J.; Chen, K.; Wang, W. A Power Evolution Game Model and Its Application Contained in Virtual Power Plants. Energies 
2023, 16, 4373.  
23. 
Wu, Z.; Xu, Z.; Gu, W.; Zhou, S.; Yang, X. Decentralized Game-Based Robustly Planning Scheme for Distribution Network and 
Microgrids Considering Bilateral Energy Trading. IEEE Trans. Sustain. Energy 2022, 13, 803–817.  
24. 
Singh, A.; Sethi, B.K.; Kumar, A.; Singh, D.; Misra, R.K. Three-Level Hierarchical Management of Active Distribution System 
with Multimicrogrid. IEEE Syst. J. 2023, 17, 605–616.



<!-- page 23/23 -->

Energies 2026, 19, 415 
23 of 23 
 
https://doi.org/10.3390/en19020415 
25. 
Li, J.; Zhou, B.; Yao, W.; Zhao, W.; Cheng, R.; Ou, M.; Wang, T.; Mao, T. Research on dynamic robust planning method for active 
distribution network considering correlation. Front. Energy Res. 2023, 11, 1338136.  
26. 
Alhassan, M.O.; Gyamfi, S.; Aboagye, B.; Diawuo, F.A.; Kwarteng, M. In-situ PV generation forecasting of utility-scale solar 
power plants in Ghana: Single and hybrid machine learning approaches. Sol. Energy Adv. 2025, 5, 100124.  
Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual au-
thor(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to 
people or property resulting from any ideas, methods, instructions or products referred to in the content.
