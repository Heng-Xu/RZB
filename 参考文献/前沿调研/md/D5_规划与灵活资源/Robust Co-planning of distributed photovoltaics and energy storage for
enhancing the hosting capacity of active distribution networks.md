<!--
source: D5_规划与灵活资源/Robust Co-planning of distributed photovoltaics and energy storage for
enhancing the hosting capacity of active distribution networks.pdf
sha256: 3c966f3b635f87f28e44a193cfe8d0a8521c868f63133035576075f300dd06d3
method: pymupdf
pages: 13
-->

<!-- page 1/13 -->

Robust Co-planning of distributed photovoltaics and energy storage for 
enhancing the hosting capacity of active distribution networks
Yingzi Wu a, Yuwei Chen b, Zhiyi Li a,*
, Sajjad Golshannavaz c
a College of Electrical Engineering, Zhejiang University, Hangzhou, China
b PowerChina Huadong Engineering Co., Ltd., Hangzhou, China
c Electrical Engineering Department, Urmia University, Urmia, Iran
A R T I C L E  I N F O
Keywords:
Distributed PVs and ESSs planning
Short-circuit current
Voltage deviation
Distributionally robust optimization
A B S T R A C T
The inherent uncertainty of photovoltaic systems (PVs) combined with the limited hosting capacity of conven­
tional distribution networks constrains accessible PV capacity, consequently reducing both economic efficiency 
and voltage stability. To address these challenges, this study proposes an integrated co-planning framework that 
explicitly incorporates PV uncertainty via a distributionally-robust optimization model designed to enhance grid 
hosting capacity. The proposed framework systematically embeds short-circuit current constraints to co-optimize 
economic benefits and operational security. The methodology employs a two-stage optimization approach. First, 
a distributionally-robust optimization algorithm constructs a probability distribution set for PV uncertainty to 
improve scenario representation. Subsequently, a second-order cone programming (SOCP) model is formulated 
for coordinated PV and the energy storage system (ESS) deployment under multiple scenarios, aiming to mini­
mize total economic costs and voltage deviations. Notably, the model incorporates dynamic short-circuit current 
constraints at grid connection points, in which PV uncertainty is accounted for through iterative calculations 
using an equivalent voltage source method. To enhance computational efficiency, an improved column-and- 
constraint generation (C&CG) algorithm is developed by integrating cutting planes derived from short-circuit 
current validation results. Case studies conducted on a 43-bus distribution network in Zhejiang Province 
demonstrate that the proposed method achieves a 60% increase in permissible PV capacity and a 16.7% 
reduction in voltage deviation compared to conventional approaches without ESS coordination or those using 
decoupled planning strategies. These results validate the effectiveness of integrated short-circuit current con­
straints in facilitating high renewable penetration while maintaining grid operational security.
1. Introduction
The large-scale integration of distributed photovoltaic (PV) systems 
with high uncertainty, has increasingly strained the hosting capacity of 
existing distribution infrastructure. This constraint not only limits PV 
penetration levels but also degrades economic efficiency, thus creating 
bottlenecks for renewable energy integration. In active distribution 
networks, hosting capacity is quantified as the maximum permissible 
renewable generation capacity while maintaining operational security 
metrics (e.g., short-circuit current, voltage deviation), within allowable 
thresholds [1]. Structural weaknesses in existing networks, compounded 
by uneven load distribution, frequently lead to line congestion and 
system imbalance, further restricting renewable integration. Conse­
quently, developing systematic methodologies for hosting capacity 
enhancement emerges as a critical research priority for achieving high 
renewable penetration.
Energy storage systems (ESSs), as flexible resources, play a pivotal 
role in high-renewable-penetration networks. ESSs mitigate PV output 
volatility through dual-mode regulation (power smoothing and tempo­
ral energy shifting), enabling economically viable planning solutions 
[2].Existing research primarily focuses on voltage regulation optimiza­
tion [3,4] andcost minimization [5,6]. For example, Reference [7] 
proposes a bi-level planning model for distributed PV-ESS to maximize 
revenue, while Reference [8] presents a multi-objective planning model 
to determine the economic capacity of ESS for solar PV support. How­
ever, these studies neglect the synergistic potential of coordinated PV 
and ESS deployment.
Independent planning of PV generation and ESSs fails to adequately 
* Corresponding author.
E-mail address: zhiyi@zju.edu.cn (Z. Li). 
Contents lists available at ScienceDirect
Renewable Energy
journal homepage: www.elsevier.com/locate/renene
https://doi.org/10.1016/j.renene.2025.123645
Received 18 November 2024; Received in revised form 30 May 2025; Accepted 1 June 2025  
Renewable Energy 253 (2025) 123645 
Available online 2 June 2025 
0960-1481/© 2025 Elsevier Ltd. All rights are reserved, including those for text and data mining, AI training, and similar technologies.



<!-- page 2/13 -->

coordinate supply with grid demand. For example, when all PV output is 
directly fed into the network, the economic motivation for deploying 
ESSs diminishes significantly. Consequently, ESS installations often 
remain underutilized, leading to high idle rates and prolonged payback 
periods. Furthermore, mitigating PV variability requires the grid to hold 
substantial backup capacity, thereby increasing operational complexity 
and costs, ultimately compromising system stability.
Techno-economic limitations of ESSs further hinder their effective 
utilization. During stable grid conditions with low electricity prices, the 
marginal benefit of operating storage units (especially those with high 
power ratings and low state-of-charge) is negligible, resulting in sub­
optimal usage and reduced returns on investment. Therefore, the 
absence of coordinated PV-ESS planning diminishes the overall PV 
integration capacity and adversely affects the economic performance of 
distribution networks.
To overcome these challenges, this paper proposes an integrated PV- 
ESS configuration that leverages synergies. This coordinated scheme 
yields several key advantages. First, ESSs can swiftly absorb or inject 
active and reactive power, enabling dynamic power exchange to 
improve voltage regulation, mitigate voltage sags, and enhance power 
quality. Second, due to their “low-SOC, high-C-rate” characteristic, ESSs 
can buffer PV output fluctuations before grid injection, thereby stabi­
lizing power delivery. Third, co-located ESS units (e.g., battery packs) 
and PV arrays at a common point of interconnection (PCC) can discharge 
substantial energy rapidly during faults; this increases the short-circuit 
current at the PCC and allows circuit breakers to trip promptly, 
ensuring effective fault isolation. Finally, although integrated PV-ESS 
planning may increase inverter rating requirements, sharing auxiliary 
infrastructure (e.g., transformers) can reduce overall costs and improve 
economic efficiency and enhance load-carrying capability.
In the planning process, two operational constraints—short-circuit 
current and voltage deviation—are intimately linked to power flow and 
significantly influenced by PV uncertainty, making them critical de­
terminants of PV hosting capacity. Worldwide, methods for calculating 
short-circuit currents at the PCC in distribution systems are under 
continuous development. The IEC 61660 standard [9] offers a method 
for short-circuit current calculation, but it is ill-suited for modern AC/DC 
hybrid networks. Reference [10] presents a short-circuit current calcu­
lation method based on discrete-time modeling. Reference [11] pro­
poses a Graph Attention Network (GAT)-based model to balance 
computational precision and speed. Reference [12] performs 
short-circuit analysis based on a cluster or distributed inverter-based 
distributed generation (IBDG) to calculate the unbalanced short-circuit 
current flowing. An affine optimization model is first established to 
characterize the short-circuit current interval of a transmission line and 
is constrained in Ref. [13]. Reference [14] proposes a short-circuit 
current partitioning calculation method considering the degree of 
voltage drop at the grid-connected point of DG. Nevertheless, PV un­
certainty can induce voltage sags at PV-integrated buses, causing dy­
namic variations in short-circuit currents that existing methods often 
neglect. This oversight leads to overly conservative planning and 
diminished economic efficiency in distribution networks.
Furthermore, with large-scale PV integration, traditional “passive” 
distribution networks are evolving into “active” ones, shifting from 
unidirectional to bidirectional power flow and increasing voltage 
deviations. Reference [15] proposes an effective control strategy for 
voltage regulators to maintain network voltage. Reference [16] presents 
a hierarchical optimal control framework to support voltage. A bi-level 
inter-phase coordinated control method for voltage regulation is 
employed in Ref. [17]. Reference [18] proposes a cost-effectiveness 
analysis method when combining reactive power compensators and 
storage batteries. A decentralized control method for coordinating of 
on-load tap changer (OLTC) transformers and PV inverters is proposed 
in Ref. [19]. Although the above studies mitigate voltage deviation is­
sues through devices such as converters to enhance network security, the 
associated construction costs negatively impact economic efficiency.
Table 1 provides a taxonomy of existing planning methods for 
distributed PVs and ESSs. A comprehensive review of the literature re­
veals the following research gaps: Current studies fail to harness the 
synergistic benefits of co-planning for PVs and ESSs, which restricts PV 
capacity, reduces economic efficiency, and exacerbates voltage fluctu­
ations. Additionally, many previous studies overlook the impact of PV 
uncertainty on PCC short-circuit current levels, which risks non- 
compliance with short-circuit constraints and compromising planning 
schemes under extreme weather conditions. This narrow focus has 
hindered the coordinated development of PVs and ESSs, highlighting the 
need for a co-planning approach that integrates PV uncertainty.
To fill this research gap, this paper establishes a co-planning model 
for distributed PVs and ESSs that incorporates PV uncertainty while 
embedding short-circuit current constraints. The model aims to optimize 
planning costs and voltage deviation while enhancing network hosting 
capacity under security constraints. First, a distributionally robust 
optimization algorithm is employed to construct a probability distribu­
tion set for PV uncertainty, generating both representative and extreme 
scenarios. Optimal siting and sizing for PVs and ESSs are then deter­
mined across various scenarios to minimize economic costs and voltage 
deviation. Subsequently, the short-circuit current level at PCC is itera­
tively calculated using the equivalent voltage source method, and an 
improved C&CG algorithm is proposed to efficiently solve the model.
The innovations of this paper are as follows: 
(1) To enhance the hosting capacity of active distribution networks, a 
SOCP model for co-planning distributed PVs and ESSs is devel­
oped. This model integrates the probabilistic distribution of PV 
uncertainty and incorporates short-circuit current constraints to 
improve planning rationality and effectiveness.
(2) To address the challenge of solving high-dimensional models, an 
improved C&CG algorithm that utilizes short-circuit current 
constraints as cutting planes is proposed. This algorithm itera­
tively calculates PCC short-circuit current levels by accounting 
for power flow variations, thereby enhancing computational ef­
ficiency without sacrificing accuracy.
This paper is organized as follows. In Section 2, the planning 
frameworks of PVs and ESSs are analyzed, and a method to address these 
issues is proposed. Section 3 proposes a method for accurately calcu­
lating the level of short-circuit current and voltage deviation. Section 4
proposes a co-planning model considering the probabilistic distribution 
of PV uncertainty. The verification of the proposed model via case 
studies is shown in Section 5. Finally, Section 6 summarizes the 
Table 1 
A taxonomy of reviewed papers on distributed PV and ESS planning.
Ref.
Co-planning
PV uncertainty
Accurate probability distribution set
Efficient short-circuit current calculation method
Voltage deviation optimization
[3,4,8,15,19]
£
£
£
£
✓
[5,6,7]
£
£
£
£
£
[10–14]
£
£
£
✓
£
[16–18]
×
✓
×
×
✓
This paper
✓
✓
✓
✓
✓
*√: The item is considered. £: The item is not considered.
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
2



<!-- page 3/13 -->

conclusions of the study.
2. Co-planning framework of distributed PVs and ESSs
This section proposes the co-planning framework of distributed PVs 
and ESS at the same bus to achieve stable operation of the distribution 
network with minimal economic cost.
2.1. Problem description
The factors influencing the hosting capacity of distribution networks 
can be broadly classified into two main categories: 
1) Environmental factors: The output time series of PV generation and 
load demand are significantly impacted by weather conditions, cloud 
cover, and seasonal temperature fluctuations. These uncertainties 
impose substantial constraints on the network’s hosting capacity. If 
planning relies solely on representative scenarios without accounting 
for extreme cases caused by severe weather, the PV integration re­
sults may be overly optimistic, introducing considerable risks to the 
planning scheme. Conversely, focusing exclusively on extreme sce­
narios could lead to an underestimation of PV capacity, resulting in 
overly conservative planning that reduces the economic efficiency of 
the distribution network.
2) Grid factors: The network’s hosting capacity is influenced both by 
the maximum capacity of power electronics within the network 
(including transformer types, connection methods, line lengths, and 
the overall network structure) and by security constraints such as 
power quality, reliability, and economic efficiency. Power quality is 
mainly reflected in bus voltage deviations, while safety reliability is 
linked to short-circuit currents, and economic efficiency is associated 
with operational costs. Among these factors, short-circuit current 
and voltage deviations, both closely related to power flow, are 
crucial elements impacting hosting capacity.
With the large-scale integration of distributed PVs, the short-circuit 
current characteristics at the PCC in traditional distribution networks 
have changed significantly [20], and voltage fluctuations have notice­
ably increased. Due to the limited capacity of power electronics (e.g., PV 
inverters), the PCC short-circuit current provided by PVs is relatively 
low, which reduces protection sensitivity and increasing the risk of 
circuit breaker failure. In the event of a circuit fault, delayed discon­
nection can jeopardize the protection of other equipment. Additionally, 
PV generation variability—affected by solar radiation, ambient 
Fig. 1. The co-planning framework of the distributed PVs and ESSs.
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
3



<!-- page 4/13 -->

temperature, and cloud cover—can induce reverse fault currents 
through the PCC, potentially triggering protection malfunctions and 
amplifying bus voltage fluctuations, thereby degrading power quality. 
Furthermore, PV generation instability can lead to inaccuracies in 
short-circuit current calculations; excessively high short-circuit currents 
in extreme scenarios may damage electrical equipment. Thus, it is 
essential to accurately calculate PCC short-circuit current levels, control 
them within a safe range, and optimize voltage deviations in the dis­
tribution network to enhance the network’s hosting capacity and reduce 
economic costs.
2.2. Planning framework
To address these challenges, it is essential to strengthen the distri­
bution network is essential to support large-scale integration of 
distributed PVs and ESSs. This paper proposes solutions from both 
planning and modeling perspectives: 
1) Planning perspective: A co-planning approach is proposed for 
collocating PVs and ESSs at the same bus, leveraging their synergy to 
stabilize PV output fluctuations and enhance network security. The 
bundled ESSs can quickly absorb or release active and reactive 
power, thereby improving voltage deviation, reducing voltage sags, 
and enhancing power quality. Additionally, the ESSs’ energy-shifting 
capabilities help smooth PV output, thereby mitigating the impact of 
uncertainty. During grid faults, ESSs can rapidly supply energy, 
boosting the short-circuit current at the PCC to ensure the timely 
operation of circuit breakers and isolation of faulted circuits. The 
ESSs can also absorb PV power during voltage sags, balancing power 
on both sides of the DC bus and suppressing inverter output to 
maintain stable network operation [21]. Although bundling PVs and 
ESSs increases inverter costs, the overall economic efficiency and PV 
capacity of the network improve through shared infrastructure such 
as transformers.
2) Modeling perspective: Based on a distributionally robust optimiza­
tion (DRO) algorithm, a probabilistic distribution set for PV uncer­
tainty caused by factors such as solar irradiance is constructed. 
Scenarios with the most volatile PV outputs are defined as extreme 
scenarios, while those with the highest annual occurrence proba­
bility are defined as representative scenarios. The comprehensive 
planning for PVs and ESSs across various scenarios enhances the 
effectiveness of scenario selection. Furthermore, an integrated 
second-order cone programming (SOCP) model is developed to 
improve the network’s hosting capacity. The model embeds PCC 
short-circuit current constraints for PVs and ESSs, with the aim of 
optimize voltage deviation and economic costs under security con­
straints while enhancing computational efficiency.
The framework for the co-planning of PVs and ESSs, which considers 
PV uncertainty, is illustrated in Fig. 1. This framework enhances the 
hosting capacity of the distribution network by generating scenarios 
based on environmental factors and optimizing indicators that consider 
grid factors. The co-planning model, which incorporates short-circuit 
current constraints, is solved iteratively using an enhanced column- 
and-constraint generation (C&CG) algorithm.
3. Short-circuit current and voltage deviation calculation 
method
In this section, a method is proposed for accurately calculating two 
security indicators: short-circuit current and voltage deviation, to ensure 
the stable operation of the distribution network.
3.1. Short-circuit current calculation considering distribution network 
topology
When distributed PVs and ESSs connect to the distribution network, 
they contribute to an increase in the short-circuit current at the PCC. 
However, traditional PVs and ESSs typically connect to the distribution 
network through inverters, which are often approximated as current 
sources [22]. During a short circuit, the current-limiting control of in­
verters restricts their contribution to the short-circuit current, making it 
challenging to meet the required short-circuit current constraints at the 
PCC. To address this, a method is proposed for co-planning distributed 
PVs and ESS as an equivalent voltage source. By considering the network 
topology, this approach enables an accurate calculation of short-circuit 
current levels at the PCC to satisfy security requirements.
Fig. 2 provides a detailed illustration of the equivalent circuit model 
for distributed PVs and ESSs. As depicted, PVs and ESSs share common 
infrastructure, such as transformers and circuit breakers, and are con­
nected to the 10 kV bus of the distribution network through a shared AC/ 
DC converter and grid connection point. The power flow at the point of 
common coupling (PCC) is simplified, with the short-circuit current 
consisting of contributions from the equivalent voltage source, the 
controlled current source, and associated equipment, including 
transformers.
The initial PCC short-circuit current is calculated using the equiva­
lent voltage source method recommended by GB/T 15544 [23]. The 
initial short-circuit current of PVs is determined based on the PV module 
conductance and nominal voltage, with the specific formula given in (1). 
Equation (2) represents the calculation of the equivalent conductance of 
PVs. The PV access point is denoted as i. 
Ii,PV = cUN̅̅̅
3
√Gki,PV + Gki,PV
∑
i,j
ΔIti,PV
Gij
∀i, j ∈B
(1) 
Gki,PV = EPVGi,PV
∀i ∈B
(2) 
when energy storage is connected to the distribution network, the in­
ternal converging lines are equivalent to an equivalent impedance, and 
each energy storage unit is represented as an equivalent energy storage 
unit. The equivalent energy storage unit and the equivalent impedance 
are connected in series, and the short-circuit current output by the 
equivalent energy storage unit is the sum of the output currents from 
each energy storage unit, with the initial value calculated as shown in 
(3). The ESS access point is denoted as j. 
Itj,ess = cUN̅̅̅
3
√Gtj,ess + Gtj,ess
∑
i,j
Δ˙Itj,ess
Gij
∀i, j ∈B
(3) 
Gtj,ess = EessGj,ess
∀j ∈B
(4) 
The PCC short-circuit current l includes the short-circuit currents 
Fig. 2. Equivalent circuit model of distributed PVs and ESSs.
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
4



<!-- page 5/13 -->

injected by the PVs, ESS, and transformers, with the calculation formula 
shown in (5). The short-circuit current injected by the transformer is 
calculated based on its short-circuit capacity and impedance percentage, 
as shown in (6). 
ISCC,l = Itl,PV + Itl,ess + IR,l
∀l ∈B
(5) 
IR,l = SSCR
Uk%
∀l ∈B
(6) 
3.2. Calculation of voltage deviation in the distribution network 
considering power sources
With the large-scale integration of photovoltaic systems, fluctuations 
in photovoltaic output power caused by factors such as weather and 
environmental temperature severely impact the power quality of the 
distribution network. Coordinated planning of energy storage can 
effectively reduce voltage deviation in the distribution network. When 
only photovoltaic systems are connected, the normal operating output 
power of the photovoltaic system will cause voltage fluctuations at the 
point of common coupling (PCC), with the calculation formula shown in 
(7). 
ΔU = ΔPPVR0 + ΔQPVX0
U2
N
(7) 
The reactive power from photovoltaic systems can be negligible, 
simplifying (7) as shown in (8). 
ΔU = ΔPPVR
U2
N
(8) 
when coordinating the configuration of photovoltaic systems and energy 
storage, the voltage at the point of common coupling (PCC) is calculated 
as shown in (9): 
⎧
⎪
⎨
⎪
⎩
Ui = Ug,i + PessZess
U2
N,i
Zess = Z0 + ZG‖ZL‖ZPV
(9) 
4. Distributed PVs and ESS coordinated planning model
This section constructs a coordinated planning model for distributed 
PVs and ESS using DRO to address the PV uncertainty, aiming to opti­
mize voltage deviation and annual comprehensive costs, while embed­
ding short-circuit current constraints.
4.1. Uncertainty probability distribution set
The output time series of PV generation and load demand are 
significantly affected by weather conditions, cloud cover, and seasonal 
temperature variations, which introduce considerable uncertainty. 
Existing methods for modeling such uncertainty can generally be 
categorized into two types: scenario-based approaches and probability- 
driven approaches.
Scenario-based methods generate PV output sequences using a set of 
representative scenarios. While these methods offer computational ef­
ficiency and simplicity, they often fail to accurately capture the sto­
chastic nature of real-world conditions. In contrast, probability-driven 
methods, such as stochastic optimization and robust optimization, are 
widely employed for uncertainty modeling. Robust optimization, spe­
cifically, aims to determine a solution that remains feasible under worst- 
case conditions by defining a bounded uncertainty set and solving for 
the optimal decision at its extreme values. Consequently, the construc­
tion of the uncertainty set is critical for balancing the accuracy and 
computational efficiency of robust optimization models. However, a 
major limitation of robust optimization is its neglect of the probability 
distribution of uncertain variables, as it focuses exclusively on worst- 
case scenarios, which can lead to overly conservative solutions.
To address these limitations, distributionally robust optimization 
(DRO) has been proposed as a more balanced approach. DRO integrates 
the probabilistic characteristics of stochastic optimization with the 
consevativeness of robust optimization by seeking solutions that are 
optimal under the worst-case probability distribution within a specified 
ambiguity set. This method mitigates the over-conservatism of tradi­
tional robust optimization and reduces dependence on precise proba­
bilistic information, which is often unavailable or difficult to estimate 
accurately. Therefore, in this study, a probability distribution set rep­
resenting PV uncertainty is constructed using the DRO framework, to 
provide a more realistic and flexible modeling approach.
Specifically, based on the historical time series set Z of PV output, k- 
medoids clustering is used to obtain K scenario sets, with the center of 
each set defined as a representative scenario S, i.e., S = {S1, S2, …, Sk}. 
PVs and ESS are bundled across different scenarios to improve the uni­
versality and rationality of the planning results. As illustrated in Fig. 3, 
each representative scenario has an annual occurrence probability of 
Ns(1≤s ≤k). The probability distribution set for these scenarios is P0 =
[P1
0, P2
0 …, Ps
0], where the original probability distribution is given by Ps
0 
= Ns/Z (1≤s ≤k). Using the L1-norm, the actual probability distribution 
set Ω for PV is defined as detailed in equation (10). A distributionally 
robust optimization algorithm is then applied to establish the uncertain 
probability distribution set for PV, based on the actual probability. As 
the parameter γ1 increases, the fluctuation range of PV characterized by 
this probability distribution set also expands, enhancing the robustness 
of the model. 
Ω =
{
P
⃒⃒⃦⃦P −P0⃦⃦≤γ1
}
=
⎧
⎪
⎪
⎪
⎪
⎪
⎨
⎪
⎪
⎪
⎪
⎪
⎩
ps
⃒⃒⃒⃒⃒⃒⃒⃒⃒⃒⃒
∑
k
s=1
⃒⃒Ps −Ps
0⃒⃒≤γ1
∑
k
s=1
ps = 1
ps ≥0, s = 1, 2, …, k
⎫
⎪
⎪
⎪
⎪
⎪
⎪
⎬
⎪
⎪
⎪
⎪
⎪
⎪
⎭
(10) 
Since the scenario with the most significant PV fluctuation occurs at 
the vertices of the feasible domain, two 0–1 variables, α, and β, are used 
Fig. 3. Implementation procedure of the PV uncertainty set.
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
5



<!-- page 6/13 -->

to describe the upper and lower boundaries of the photovoltaic output, 
as shown in (11). When α = 1, the output reaches the maximum fluc­
tuation value. When β = 1, the output reaches the minimum fluctuation 
value. 
PPV = PPV,f + αγ1 −βγ1
(11) 
{ α + β ≤1
∑
(α + β) ≤Γ
(12) 
Equation (12) shows the constraints of the PV fluctuation variables, 
which are mutually exclusive. Γ limits the number that simultaneously 
reaches the fluctuation limit. The larger Γ, the more intense the PV 
fluctuation, and the more extreme scenarios.
The current conventional method achieves planning by determining 
the variation range of the PV uncertainty parameter, which requires 
extensive computation and is inefficient. This paper establishes a PV 
uncertainty probability distribution set based on DRO and generates 
different scenarios, thus improving the effectiveness of scenarios.
4.2. The co-planning model
A second-order cone programming model with embedded short- 
circuit current constraints is then established to determine the optimal 
sizing and siting scheme. This model aims to optimize voltage deviation 
and overall cost for the distribution network, encompassing both plan­
ning and operational expenses. The objective function, defined in 
equation (13), includes decision variables x, which represent the access 
buses and capacities of PV and ESS. The occurrence probabilities of 
different scenarios, all of which are contained within the probability 
distribution set Ω. The objective function’s calculation formula is pro­
vided below: 
f(x) = min
Ps∈Ω
(
Cinv + σCop + Cvol
)
(13) 
Typically, the investment cost includes the cost of the PV system and 
the ESS. The operation cost is the electricity purchased from the main 
grid, which is given by: 
Cinv =
δ(1 + δ)y
(1 + δ)y −1
( ρpinvPess + ρeinvEess
)
+ CPV,invEPV + Cess,omEess
(14) 
Cop =
∑
i
ρpbuyPg
(15) 
Cvol =
∑
N
i=2
|Ui −U1|
(16) 
1) Investment constraints of PVs and ESSs
Equations (17) and (18) define the capacity of the PV system and the 
ESS limits concerning the grid. The capacity constraints of the PV system 
and the ESS are as follows: 
EPV,min ≤EPV ≤EPV,max
(17) 
Eess,min ≤Eess ≤Eess,max
(18) 
2) Operational constraints of ESS devices
Equations (19) and (20) model the charging and discharging con­
straints of the ESS and the SOC balance, respectively. Here, the charging 
and discharging of the ESS are controlled by the variables udch and uch. 
Moreover, (19) indicates that the BESS cannot charge and discharge at 
the same time. The SOC is calculated from the initial SOC capacity and 
charge/discharge power per hour. Equation (20) shows that the SOC 
must be less than or equal to the maximum SOC and greater than or 
equal to the minimum SOC. 
⎧
⎪
⎪
⎨
⎪
⎪
⎩
udch(t) × Pdch,min ≤Pdch(t) ≤udch(t) × Pdch,max
uch(t) × Pch,min ≤Pch(t) ≤uch(t) × Pch,max
udch(t) + uch(t) ≤1
∀t ∈T
(19) 
⎧
⎪
⎪
⎨
⎪
⎪
⎩
SOCess,min ≤SOCess(t) ≤SOCess,max
SOCess(t) = SOCess(t −1) + ηchPch(t) −Pdch(t)
ηdch
∀t ∈T
(20) 
3) Power flow constraints
Equation (21) models the constraints of active and reactive power 
balance. Here, the active power variables include the uncertain output 
of the PV PPV
j, the active power load Pload
,j
, the battery output power Pess
j . 
Let ̃Iij = I2
ij and ̃
Uij = U2
ij, the power flow constraints would be as follows: 
⎧
⎪
⎪
⎪
⎨
⎪
⎪
⎪
⎩
∑
i∈P(j)
(
Pij −̃Iijrij
)
−
∑
l∈C(j)
Pjl = Pload
j
−PPV
j
−Pess
j
∑
i∈P(j)
(
Qij −̃Iijxij
)
−
∑
l∈C(j)
Qjl = Qload
j
∀i, j, l ∈B
(21) 
Fig. 4. Workflow of the proposed two-stage coordinated model.
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
6



<!-- page 7/13 -->

4) Voltage constraint
Equation (22) defines the voltage for bus j, where rij and xij represent 
the resistance and reactance values of branch ij, respectively. 
̃Uj(t) = ̃Ui(t) −2
(
Pij(t)r(t)ij + Qij(t)xij(t)
)
+̃Iij(t)
(
r2
ij(t) + x2
ij(t)
)
, ∀i, j ∈B
(22) 
U2
j ≤̃Uj(t) ≤U2
j , ∀j ∈B
(23) 
5) Current constraint
Equation (24) enforces the bound for the current of branch ij. 
I2
ij ≤̃Iij(t) ≤I2
ij, ∀i, j ∈B
(24) 
6) Second-order cone constraint
Through relaxation deformation, (23) and (24) are transformed into 
a second-order cone constraint: 
⃦⃦⃦⃦⃦⃦
2Pij
2Qij
̃Iij −
̃Uj
⃦⃦⃦⃦⃦⃦
≤̃Iij + ̃Uj, ∀i, j ∈B
(25) 
4.3. Security verification
The initial planning scheme obtained from the above model is sub­
jected to security verification, primarily considering whether the short- 
circuit current and the port voltage exceed limits. Using the short-circuit 
conductance of PVs and ESS and the admittance matrix, the k-th port 
voltage of bus j is calculated, as shown in (26)-(27). 
Uti,PV(k) = cmin −cmaxGk
Gi
+
∑
i∈B
ΔIkti(k)
Gi
∀t ∈T
(26) 
Utj,ess(k) = cmin −cmaxGk
Gj
+ +
∑
j∈B
ΔItj,ess(k)
Gj
∀t ∈T
(27) 
Based on the obtained port voltage, (28) and (29) respectively 
calculate the short-circuit current for PVs and ESS. 
⎧
⎨
⎩
Ikq(k) = min
[
KLvrt
(
0.9 −Uti,PV(k)
)
IN, KqlimIN
]
Uk < 0.9
Ikp(k) = min
[
̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅
(KiIN)2 −I(k)2
kq
√
,
(
P0
/
Uti,PV(k)
)
IN
]
(28) 
˙Ikti(k) =
̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅
I2
kp(k) + I2
kq(k)
√
ej arctan(−Ikq(t)/Ikp(t))
(29) 
After obtaining the k-th short-circuit current component, the fault 
component of the steady-state short-circuit current at bus j is calculated, 
as shown in equation (30): 
ΔIkti(k) = |Ikti(k) −Ikti(k −1)|
(30) 
Then, the short-circuit current injected by ESS is calculated after 
obtaining the steady-state component, considering the impact of its 
charging and discharging states on the short-circuit current. In the dis­
charging state, the short-circuit current is calculated as shown in (31)- 
(32). 
˙Ikj,ess=
⎧
⎪
⎪
⎪
⎨
⎪
⎪
⎪
⎩
Pref −jQref
SN
IN UkPCC≥UL
min
{Pref
SN
IN,
̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅
I2
max−min
{
I2
qref,I2
min
}
√
}
−jmin
{
Iqref,Imax
}
UkPCC<UL
(31) 
Iqref = KL(UL −UkPCC)
UN
IN
(32) 
In the charging state, the short-circuit current is calculated according to 
(33), where Pref is positive when flowing into the system.  
Therefore, the fault component of the steady-state short-circuit cur­
rent at bus j is detailed in (34). 
Δ˙Itj,ess(k) =
⃒⃒⃒⃒˙Itj,ess(k) −
˙Itj,ess(k −1)
⃒⃒⃒⃒
∀j ∈B
(34) 
The iterative process continues until the difference between Uti,PV 
and Utj,ess in two successive iterations falls below a predefined threshold. 
Once this convergence criterion is satisfied, the iteration terminates, and 
both the short-circuit current at the point of common coupling (PCC) 
and the port voltage are determined.
The initial values of the short-circuit current by PV and ESS are 
calculated according to (4) and (6).
Based on the principle of short-circuit protection, the short-circuit 
current of distributed PVs and ESS during a fault should exceed the 
rated breaking current allowed by the circuit breaker, so that the 
breaker can quickly disconnect the line to achieve the purpose of short- 
circuit protection. At the same time, the short-circuit current ISCC,l 
during a fault must not exceed the breaking capacity of the circuit 
breaker to ensure that it can function properly and disconnect the circuit 
during a short circuit. Therefore, based on the requirements for circuit 
breaker short-circuit protection, a short-circuit current constraint is 
imposed as (35). 
Incl ≤ISCC,l ≤Iz
∀l ∈B
(35) 
4.4. Improved C&CG algorithm
The proposed SOCP model for co-planning of distributed PV and ESS 
is solved sequentially. To enhance solution efficiency, an improved 
Column-and-Constraint Generation (C&CG) algorithm utilizing short- 
circuit current cut sets is introduced. This algorithm operates itera­
tively: first, the master problem is solved using the SOCP model, fol­
lowed by the subproblem calculation based on the preliminary planning 
solution. A cut set for PV and ESS accessible capacity is constructed 
based on short-circuit current constraints, with the iterative process 
continuing until model convergence is achieved.
For clarity, the detailed solution procedure of the model is illustrated 
in Fig. 4. The details are as follows: 
˙Ikj,ess =
⎧
⎪
⎪
⎪
⎨
⎪
⎪
⎪
⎩
−
⃒⃒Pref
⃒⃒−jQref
SN
IN
UkPCC ≥UL
min
{−
⃒⃒Pref
⃒⃒
SN
IN,
̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅
I2
max −min
{
I2
qref, I2
min
}
√
}
−j min
{
Iqref, Imax
}
UkPCC < UL
(33) 
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
7



<!-- page 8/13 -->

1) Characterization of PV uncertainty: The DRO algorithm is used to 
construct the PV uncertainty probability distribution set Ω according 
to equation (10).
2) Set initial values: Set the convergence threshold ϵ for the iteration and 
initialize the number of iterations k = 1.
3) Solving the master problem: Solve the economic optimization problem 
F under different scenarios, where Ps represents the extreme scenario 
in the PV probability distribution set. The linearized objective 
function of the master problem is detailed in (36). The constraints 
include equations (17)–(22). The solution of the master problem 
yields the objective function value F1* and the preliminary planning 
scheme X*, as shown in equation (37). The lower bound is updated as 
LP=F1*.
F = min
Ps∈Ω
(
Cinv + σCop + Cvol
)
(36) 
X* =
{
xPV, xess, xbuy
}
(37) 
4) Solving the subproblem: Based on scheme X*, the subproblem F2 is 
solved using equation (38), yielding the corresponding objective 
function value F2*. Simultaneously, the PCC short-circuit current 
level I*SCC,l for the distributed PV and ESS is iteratively computed 
using equations (25)–(33).
ΔEess =
̅̅̅
3
√
UN
(
Inel −ISCC,l
)
∀l ∈B
(38) 
minF2 = δ(1 + δ)y(ρeinvΔEess)
(1 + δ)y −1
+ Cess,omΔEess
(39) 
5) Short-circuit current verification: According to equation (34), verify 
whether the PCC short-circuit current I*SCC,l meets the requirements. 
If the short-circuit current satisfies the circuit breaker protection 
requirements, update the upper bound as UP= F1*+F2*; otherwise, 
add an ESS capacity constraint using the cutting plane method that 
considers short-circuit current constraints and add it to the master 
problem, then return to step 3 to solve again. The cut set formulas are 
shown in equations (40) and (41).
EPV + Eess ≥
̅̅̅
3
√
UNInel
(40) 
PPV = PPV,f + αγ1
(41) 
6) Convergence loop: Compare the difference between the upper and 
lower bounds. If the difference is smaller than the convergence 
threshold ϵ, the iteration ends, and the planning scheme X* is ob­
tained. Otherwise, set k = k+1 and continue iterating until the model 
converges.
The proposed co-planning model integrates short-circuit current 
constraint while accounting for PV uncertainties, thereby enhancing the 
hosting capacity of the distribution network. Practitioners can utilize the 
proposed method to balance both economy and security, facilitating the 
optimal siting and sizing of distributed PVs and ESS. This approach 
improves the accessible capacity of PVs within security constraints and 
offers a computationally efficient solution. Consequently, this model 
supports both economic gains and voltage stability, benefiting society 
with greater reliability and cost-effectiveness.
5. Case study
This section reports the results of the case study. The experiments are 
based on the distribution network of a 43-bus system in Zhejiang, China, 
which includes 43 buses, 42 existing lines, 43 loads, and 17 candidate 
buses for distributed PVs and ESS installations. The set of candidate 
buses is {2, 4, 7, 13, 15, 18, 19, 20, 21, 23, 26, 28, 29, 31}. We assume 
that the capacity and location of PVs and ESS are decision variables.
Based on the annual historical output data, the representative sce­
narios with the highest occurrence probabilities in each of the four 
seasons are selected, and the extreme scenario with the most significant 
PV fluctuations in each season is selected. Fig. 5(a) shows the load 
representative scenarios of bus 2, specifically {S1, S2, S3, S4}. After 
constructing the uncertainty probability distribution set for PV using the 
DRO, the extreme PV scenarios were obtained in Fig. 5(b).
All parameters of the planning model are listed in Tab. A 2. All tests 
are run using Gurobi 10.0.3 on an Intel(R) Core (TM) i5-8250U CPU at 
1.60 GHz.
5.1. Optimal planning scheme of distributed PVs and ESSs
The proposed co-planning method for distributed PVs and ESSs is 
compared with two alternative planning methods to better demonstrate 
the superiority of this coordinated approach. The daily PV outputs are 
recorded at 15-min intervals, resulting in a total of 96 sample points.
Method 1: Only distributed PVs are considered without ESS [24].
Method 2: Distributed PVs and ESSs are planned separately [25].
Method 3: The proposed co-planning model is applied considering 
PV uncertainty.
By solving the models, the economically optimal planning solutions 
for the representative scenarios are obtained. The economic perfor­
mance of the different planning methods is compared, as shown in 
Table 2. Lines 2–3 in Table 2 display the access capacities of PVs and 
ESSs, while lines 4–5 present the annual comprehensive costs and the 
total voltage deviation. As illustrated in Table 2, Method 3 results in a 
Fig. 5. Time series of output at bus 2.
Table 2 
Distributed PVs and ESSs configuration.
Technical Index
Method 1
Method 2
Method 3
Capacity of PV(MW)
3.00
4.80
4.80
Capacity of ESS(MWh)
0
1.94
1.94
Overall costs( × 104¥/year)
6141.4
7698
7698
Voltage deviation(p.u./year)
10746
7981.3
6839.7
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
8



<!-- page 9/13 -->

25.9 % increase in the total capacity of PVs and ESSs compared to 
Method 1, along with an 11 % reduction in economic costs and a 20 % 
decrease in voltage deviation. In comparison to Method 2, although 
Method 3 maintains the same PV and ESS access capacity, it reduces 
voltage deviation by 16.7 %, highlighting its effectiveness in improving 
voltage stability.
Fig. 6(a) displays the coordinated configuration of distributed PVs 
and ESSs obtained using Method 3. The x-axis represents the candidate 
buses, while the y-axis represents the accessible capacity. Buses 13, 15, 
and 18 are selected for PV and ESS placement. To further emphasize the 
superiority of Method 3, Fig. 6(b) compares the economic cost and 
voltage deviation of the planning solutions. The x-axis represents 
different planning methods, the left y-axis represents the annual 
comprehensive economic cost, and the right y-axis represents the 
voltage deviation. As shown in Fig. 6(b), the planning scheme obtained 
by Method 3 achieves the lowest economic cost and the smallest voltage 
deviation in the distribution network.
Fig. 7 illustrates the average voltage changes at the buses. The results 
demonstrate that the coordinated configuration of PVs and ESSs in 
Method 3 significantly reduces average voltage fluctuations. This 
improvement is attributed to the ESS effectively smoothing out PV 
output fluctuations before being connected to the grid, thereby reducing 
voltage instability.
The results further demonstrate that the proposed method exhibits 
superior performance in improving economic efficiency and maintain­
ing voltage stability. When only PVs are planned, the distribution 
network must rely heavily on electricity purchases from the main grid to 
meet load demands and mitigate PV fluctuations, resulting in high 
procurement costs. By co-planning ESSs, PV fluctuations are smoothed, 
and the dependence on costly grid electricity is substantially reduced, 
greatly boosting both economic efficiency and voltage stability. More­
over, compared to planning PVs and ESSs individually, co-planning 
enables ESSs to smooth out fluctuations before grid connection, thus 
maintaining voltage stability. It also promotes the sharing of infra­
structure (such as substations), further reducing investment costs. 
Consequently, the co-planning of distributed PVs and ESSs not only 
optimizes economic efficiency and voltage stability but also maximizes 
the accessible PV capacity.
5.2. Short-circuit current calculation
After obtaining the optimal planning scheme of distributed PVs and 
ESSs, the short-circuit current at the PCC is further verified to ensure 
security. To streamline the calculations, this section computes the PCC 
short-circuit current using the proposed method. The circuit breaker 
model used for PVs and ESS is the TGB2D-80RW, while the circuit 
breaker for the transformer connection is the ZN12-10/1250. The 
transformer has a rated capacity of 100 kVA and a short-circuit 
impedance of 4 %. The specific parameters required for short-circuit 
current calculations are provided in Tab. A 3.
Table 3 compares the impact of co-planning versus separate planning 
(with the same capacity) on the short-circuit current at the PCC. In 
Method 2, ESSs are independently planned at buses 14, 16, and 19, while 
PVs are independently planned at buses 13, 15, and 18. In Method 3, PVs 
and ESS are co-planned together at buses 13, 15, and 18. As shown in 
Tables 3 ，when PVs and ESSs are independently planned, the average 
PV short-circuit current at the PCC fails to reach the rated breaking 
current of the circuit breaker, leading to a delayed response during a 
short-circuit fault and hindering rapid fault clearance. Furthermore, the 
average short-circuit current of ESSs at the PCC is too low to provide 
effective short-circuit protection. In contrast, the co-planning of PVs and 
ESSs appropriately increases the average short-circuit current to levels 
above the rated breaking current yet within the interrupting current 
limit. During a short-circuit fault, the proposed co-planning method 
ensures that the current rapidly reaches the breaker’s set threshold, 
Fig. 6. Distributed PVs and ESSs planning scheme in three methods.
Fig. 7. Comparison of average voltage at distribution network buses.
Table 3 
Comparison of average short-circuit current.
Buses
13
14
15
16
18
19
Method 2
4.82
3.535
4.82
4.124
4.82
3.623
Method 3
8.13
/
8.43
/
8.19
/
Inel
6
6
6
6
6
6
Fig. 8. Buses average voltage in extreme scenarios.
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
9



<!-- page 10/13 -->

enabling prompt fault clearance. This approach satisfies short-circuit 
current constraints and ensures the stable operation of power elec­
tronics equipment. Additionally, the co-planning scheme effectively 
reduces the average short-circuit current at non-connection buses, thus 
preventing unnecessary losses caused by equipment inadvertent 
operation.
To further illustrate the impact of voltage deviations across different 
buses under extreme scenarios, Fig. 8 shows voltage variations at each 
bus during a fault. The blue-shaded area represents voltage fluctuations 
due to PV uncertainties. The results indicate that during faults, voltage 
fluctuations are relatively moderate in the spring and autumn, but more 
pronounced in the summer and winter. However, all bus voltages remain 
within the permissible range of 0.95–1.05 p.u.
In summary, the co-planning method proposed in this paper signif­
icantly enhances economic efficiency while optimizing voltage devia­
tion and adhering to short-circuit current constraints. Even at the most 
vulnerable buses during a fault, voltage fluctuations remain within 
permissible limits, ensuring stable operation. This planning model offers 
an optimal scheme that effectively balances economic efficiency and 
security.
5.3. Efficiency and convergence analysis
To clearly demonstrate the improvement in computational efficiency 
achieved by the enhanced column-and-constraint generation (C&CG) 
algorithm, a comparative analysis was conducted against the scenario- 
based direct solution model [26] and the traditional C&CG algorithm 
[27].
As shown in Table 4, the solution times for the different methods 
indicate that the improved C&CG algorithm—by incorporating short- 
circuit current constraints as cutting planes—significantly improves 
computational efficiency while effectively addressing the uncertainty 
associated with PV generation. In contrast, the direct solution method 
relies on a large number of representative scenarios, which substantially 
increases the computational burden and reduces the overall model ef­
ficiency. Although the traditional C&CG algorithm is more efficient than 
the direct approach, it requires multiple iterations of repeated cuts to 
converge to the optimal solution. Furthermore, it does not guarantee 
that short-circuit current constraints at the point of common coupling 
(PCC) will be satisfied, which compromises the secure operational ca­
pacity of the distribution system.
Fig. 9 illustrates the convergence behavior of the proposed algo­
rithm. Both the master problem and the subproblem converge within 
five iterations, demonstrating strong convergence characteristics and 
high computational efficiency.
5.4. Sensitivity analysis
To study the impact of different investment parameters on the 
planning of distributed PVs and ESSs, we analyze the planning results 
Table 4 
Comparison of calculation efficiency.
Solution
Required time(s)
Improved efficiency (%)
Improved C&CG
107
/
Direct solution
1348
92.06
C&CG
348
69.25
Fig. 9. Iteration number of C&CG.
Fig. 10. The costs/voltage deviation with different parameters of PV and ESS.
Fig. 11. Sensitivity analysis of number of scenarios.
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
10



<!-- page 11/13 -->

under varying unit investment costs for both PV and ESS. Specifically, 
given that unit construction costs for PV and ESS are expected to 
decrease with technological advancements, we use the parameters 
shown in Tab. A 2 as the baseline and vary the relative costs of PV and 
ESS from 0.5 to 1 times the baseline value. The results are shown in 
Fig. 10. As shown, a reduction in the unit investment costs for both PV 
and ESS significantly reduces the overall economic cost of the planning 
scheme. In particular, for distributed PV, a 50 % reduction in unit in­
vestment costs leads to a 2.64 % reduction in overall costs, which un­
derscores the important role of technological advancements in 
improving the system’s economic efficiency. The voltages in the distri­
bution system remains stable, with no noticeable deviations.
In addition, this study uses a PV uncertainty modeling method based 
on generating an uncertainty set through representative scenarios. For 
the k-medoids clustering technique, the number of clusters is a crucial 
capacity planning parameter that must be carefully selected for capacity 
planning. Therefore, a sensitivity analysis of the number of scenarios for 
PV and ESS planning was conducted, with the results presented in 
Fig. 11. It can be observed that as the number of scenarios approaches 8, 
both the PV planning capacity and the economic cost of the plan 
converge. Specifically, when the number of representative scenarios 
exceeds 8, the PV planning capacity and overall costs stabilize even with 
further increases in the number of representative scenarios. However, 
increasing the number of representative scenarios also increases 
computational time. Consequently, in this study, the number of repre­
sentative scenarios is determined by balancing overall costs and 
computational time.
6. Conclusion
In this paper, a two-stage optimization model is proposed to address 
the co-planning of distributed PVs and ESSs under uncertainty. The first 
stage determines the optimal investment decisions, including the sizing 
and siting of PVs and ESSs, within a distributionally robust optimization 
(DRO) framework that explicitly accounts for PV generation uncer­
tainty. Building on these investment outcomes, the second stage de­
velops operational strategies across a set of generated scenarios, each 
incorporating short-circuit current constraints to ensure network secu­
rity under varying operating conditions. The model is iteratively refined 
by updating the uncertainty set and the associated operational responses 
until convergence criteria are met, thereby ensuring both robustness and 
feasibility. By effectively integrating planning and operational decision- 
making and capturing the nonlinear characteristics of fault currents 
through a second-order cone programming (SOCP) formulation, the 
proposed approach significantly enhances system performance. The 
solution is efficiently obtained using an enhanced column-and- 
constraint generation (C&CG) algorithm, which utilizes short-circuit 
current constraints as cutting planes. Nevertheless, the scope of this 
study does not exhaustively cover all aspects of the proposed method­
ology, as the SOCP model relies on scenario-based analysis. Conse­
quently, future research should focus on the development of advanced 
techniques for identifying optimal representative scenarios, thereby 
enhancing both the accuracy and efficacy of scenario selection.
CRediT authorship contribution statement
Yingzi Wu: Writing – original draft, Visualization, Software, Meth­
odology, Investigation, Conceptualization. Yuwei Chen: Writing – 
original draft, Software, Methodology, Investigation. Zhiyi Li: Writing – 
review & editing, Validation, Supervision, Resources, Methodology. 
Sajjad Golshannavaz: Writing – review & editing, Validation, Super­
vision, Methodology.
Declaration of competing interest
The authors declare that they have no known competing financial 
interests or personal relationships that could have appeared to influence 
the work reported in this paper.
Acknowledgement
This work was supported by National Natural Science Foundation of 
China (52477132).
Appendix A 
Tab. A 1 
Variables and implications in Appendix A
Varibles
Implications
Varibles
Implication
Ω
Set of PV uncertainty probability distribution.
U1
Voltage of root bus.
P
Set of buses connected with PV.
EPV,min/max
Limits of photovoltaic capacity.
E
Set of buses connected with ESS.
Eess,min/max
Limits of ESS capacity.
B
Set of distribution network buses.
Pdch,min/max
Power limits of ESS discharge.
Г
Set of PV uncertainty.
Pch,min/max
Power limits of ESS charge.
s
The s-th scenario.
SOCess,min/ 
max
SOC limits of ESS discharge.
t
The t-th period.
ηdch/ch
Charge and discharge efficiency.
i
The i-th bus.
udch/ch
Charge and discharge ratios.
j
The j-th bus.
Pij
Active power of branch ij.
l
The l-th bus.
Qij
Reactive power of branch ij.
k
The k-th iteration.
rij
Resistance of branch ij.
f(x)
Objection function for investment x.
xij
Inductance of branch ij.
R0/L
The resistance of the transmission line and the connected load.
I2
ij,I2
ij
Limits of the square of the current.
X0/L
The reactance of the transmission line and the connected load.
U2
j ,U2
j
Limits of the square of the voltage.
RPV
The equivalent resistance of PV.
Uj
The voltage of root bus j.
Ress
The equivalent resistance of ESS.
Pj
load
Load active power of bus j.
RR
The equivalent resistance of the transformer.
Qj
load
Load reactive power of bus j.
c
The voltage coefficient.
Pj
PV
Active power of the PV system of bus j.
Un
The nominal voltage.
Pj
ess
Active power of ESS of bus j.
(continued on next page)
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
11



<!-- page 12/13 -->

Tab. A 1 (continued)
Varibles 
Implications 
Varibles 
Implication
GkPV/kBESS, 
j
The equivalent short-circuit conductance at bus j of PV or ESS.
PPV,f
Predicted value of the PV outputs.
Gij
The magnitude of the admittance matrix of branch ij.
Pload,f
Predicted value of the load outputs.
ΔIti,PV/tj,ess
The current increment before and after the fault at bus j of PV or ESS.
cmax/min
Limits of voltage coefficients.
Gi,PV/j,ess
The per unit value unit conductance of PV or ESS.
ΔIkti
The k-th fault component of steady-state short-circuit current of bus i for PV.
IR,l
The short-circuit current by the transformer of bus l.
ΔIktj,ess
The k-th fault component of steady-state short-circuit current of bus j for ESS.
SSCR
The short-circuit capacity of the transformer.
Ikq/kp
The reactive/active component of PV short-circuit current.
Uk%
The impedance percentage of the transformer.
KLvrt
The reactive current coefficient of PV for low voltage ride-through.
ΔPPV/esss
The increments of active power by PV or ESS.
Kqlim
The maximum value of the reactive component of PV.
ΔQPV
The increments of PV reactive power.
Ki
The maximum overload coefficient of PV.
Ug,i
The voltage of bus i.
SN
Rated capacity of converter.
Zess/PV
The equivalent impedance of ESS and PV.
IN
Rated current of converter.
Z0
The unit impedance of ESS.
Imax
Maximum output current of ESS.
ZG//L
The impedance of grid and load.
Pref/Qref
Reference active/reactive power before the fault.
Ps
The actual probability distribution of s-th scenario.
KL
The reactive current coefficient of ESS for low voltage ride-through.
γ1
The uncertainty range of PV.
Uk
The fault voltage of ESS.
PPV
The actual output curve of PV.
UL
The voltage threshold for entering the low voltage ride-through state.
Cinv/op
Annual investment cost and operation cost.
Incl
Rated breaking current of the circuit breaker.
Cvol
Voltage deviation.
Iz
The interrupting current of the circuit breaker.
Pg
Electricity purchased from the main grid.
σ
Number of operating days.
ρpinv/einv
Investment cost per unit of ESS power capacity and energy capacity.
δ
Discount rate.
ρpbuy
Unit price of electricity purchased from the grid.
y
Service life of storage.
Cess,om
Operation and maintenance costs of ESS.
Eess/PV
Capacity of the ESS or PV system.
CPV,inv
Construction cost of PVs.
Pess/PV
Power of the ESS or PV system.
All parameters of the co-planning model are listed in Tab. A 2:
Tab. A 2 
Basic parameters of the model
Parameters
Values
δ
0.95
ρpinv (¥/kW)
3600
ρeinv (¥/kWh)
1800
CPV,inv (¥/kW)
2940
Cess,om (¥/kW)
600
ρg (¥/kW)
250 (0:00–6:00)
750 (6:00–12:00)
500 (12:00–17:00)
750 (17:00–19:00)
250 (19:00–24:00)
e (¥/t)
377
θ
0.97
The specific parameters required for short-circuit current calculations are provided in Tab. A 3.
Tab. A 3 
Parameters of short-circuit current
Indicators
Values
cmin, cmax
0.9,1.05
KLvrt
1.5
Kqlim
1.05
Ki
1.1
Inel(kA)
6
Iz(kA)
10.4
GBess(S•MW−1)
27.6
GPV(S•MW−1)
2.54
ZG(Ω•MW−1)
0.5079
ZL(Ω•MW−1)
0.1302
Z0(Ω•MW−1)
0.036
ZPV(Ω•MW−1)
0.39
References
[1] H. Liu, R. Cao, J. Han, et al., Research status and future prospect of distributed 
generation hosting capacity assessment of distribution network, Autom. Electr. 
Power Syst. 1–13 (2024-08-07).
[2] P. Siratarnsophon, K.W. Lao, D. Rosewater, et al., A voltage smoothing algorithm 
using energy storage PQ control in PV-Integrated power grid, IEEE Trans. Power 
Deliv. 34 (6) (2019) 2248–2250.
[3] K. Prakash, M. Ali, M.A. Hossain, et al., Planning battery energy storage system in 
line with grid support parameters enables circular economy aligned ancillary 
services in low voltage networks, Renew. Energy 201 (Part 1) (2022) (ISSN 0960- 
1481) 802-820.
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
12



<!-- page 13/13 -->

[4] S.K. Wankhede, P. Paliwal, M.K. Kirar, Bi-Level multi-objective planning model of 
solar PV-Battery storage-based DERs in smart grid distribution system, IEEE Access 
10 (2022) 14897–14913.
[5] T. Liu, J. Chen, W. Zhang, et al., Joint planning for PV-SESS-MESS in distribution 
network towards 100% self-consumption of PV via consensus-based ADMM, 
J. Energy Storage 90 (Part A) (2024) 111747. ISSN 2352-152X.
[6] H.M.A. Ahmed, H.F. Sindi, M.A. Azzouz, et al., Optimal sizing and scheduling of 
Mobile energy storage toward high penetration levels of renewable energy and fast 
charging stations, IEEE Trans. Energy Convers. 37 (2) (2022) 1075–1086.
[7] S. Yang, X. Wang, Y. Yang, et al., Bi-level planning model of distributed PV-energy 
storage system connected to distribution network under the coordinated operation 
of electricity-carbon market, Sustain. Cities Soc. 89 (2023) (ISSN 2210-6707) 
104347.
[8] G. Memarzadeh, F. Keynia, A new hybrid CBSA-GA optimization method and 
MRMI-LSTM forecasting algorithm for PV-ESS planning in distribution networks, 
J. Energy Storage 72 (Part D) (2023) 108582. ISSN 2352-152X.
[9] S. Skok, A. Marusic, S. Tesnjak, Transient short-circuit currents in auxiliary DC 
installations in power plants and substations. 2003 IEEE Bologna Power Tech 
Conference Proceedings, 2003. Bologna, Italy.
[10] Y. Liu, M. Huang, X. Zha, et al., Short-circuit current estimation of modular 
multilevel converter using discrete-time modeling, IEEE Trans. Power Electron. 34 
(1) (2019) 40–45.
[11] R. Ye, H. Wang, Y. Ma, et al., Enhancing short-circuit current calculation in active 
distribution networks through fusing superposition theorem and data-driven 
approach, Int. J. Electr. Power Energy Syst. 161 (ISSN 0142–0615) (2024) 110196.
[12] M.A. Khan, A. Haque, V.S.B. Kurukuru, Dynamic voltage support for low-voltage 
ride-through operation in single-phase grid-connected photovoltaic systems, IEEE 
Trans. Power Electron. 36 (10) (2021) 12102–12111.
[13] Y. Zhang, B. Du, B. Pan, et al., An algorithm for short-circuit current interval in 
distribution networks with inverter type distributed generation based on affine 
arithmetic, Energy Eng. J. Assoc. Energy Eng. 121 (7) (2024) (ISSN 0199-8595) 
1903-1920.
[14] W. Wang, Q. Shao, S. Wang, et al., Partitioning calculation method of short-circuit 
current for high proportion DG access to distribution network, Energy Eng. J. 
Assoc. Energy Eng. 121 (9) (2024) 2569–2584 (ISSN 0199-8595.
[15] A. Bedawy, N. Yorino, K. Mahmoud, et al., Optimal voltage control strategy for 
voltage regulators in active unbalanced distribution systems using multi-agents, 
IEEE Trans. Power Syst. 35 (2) (2020) 1023–1035.
[16] G.E. Mejia-Ruiz, M. R, et al., Fast hierarchical coordinated controller for 
distributed battery energy storage systems to mitigate voltage and frequency 
deviations, Appl. Energy 323 (ISSN 0306–2619) (2022) 119622.
[17] F. Rezaei, S. Esmaeili, A bi-level inter-phase coordinated control method for 
voltage regulation in unbalanced LV distribution networks using PV-battery energy 
storage systems, J. Energy Storage 101 (Part B) (2024) (ISSN 2352-152X) 113943.
[18] M. Takagi, K. Fukushima, N. Tagashira, et al., Cost-effectiveness analysis method 
for voltage stabilization in case of combining storage battery and reactive power 
compensator, J. Energy Storage 93 (ISSN 2352–152X) (2024) 112065.
[19] M.R. Jafari, M. Parniani, M.H. Ravanji, Decentralized control of OLTC and PV 
inverters for voltage regulation in radial distribution networks with high PV 
penetration, IEEE Trans. Power Deliv. 37 (6) (2022) 4827–4837.
[20] K. Li, Q. Huang, R. Fan, et al., Experimental verification of the impact of high 
proportion distributed photovoltaic access on distribution network protection, 
Electrotech. Appl. 42 (12) (2023) 16–24.
[21] B. Deng, Y. Wen, L. Yu, et al., Sort-circuit current suppression strategy for 
receiving-end power grid based on coordination of current limiter configuration 
and network structure optimization, Autom. Electr. Power Syst. 48 (9) (2024) 
151–161.
[22] S. Favuzza, M. Mitolo, S. Moradi, et al., A general methodology for short-circuit 
calculations in hybrid AC/DC microgrids, IEEE Trans. Ind. Appl. 59 (3) (2023) 
2742–2749.
[23] Q/GDW 10738—2020[S]. Beijing, The Guide of Planning and Design of 
Distribution Network, 2020-12-31.
[24] J. Liu, K. Sun, Z. Ding, et al., Multi-stage planning of distribution network with 
high penetration renewable energy considering reliability index, IEEE Trans. Ind. 
Appl. 60 (2) (2024) 2344–2356.
[25] S. Wang, G. Geng, Q. Jiang, et al., Generation expansion planning considering 
discrete storage model and renewable energy uncertainty: a bi-interval 
optimization approach, IEEE Trans. Ind. Inf. 19 (3) (2023) 2973–2983.
[26] X. Cao, T. Cao, F. Gao, et al., Risk-averse storage planning for improving RES 
hosting capacity under uncertain siting choices, IEEE Trans. Sustain. Energy 12 (4) 
(2021) 1984–1995.
[27] H. Zeng, et al., Data-driven robust planning for distribution network based on 
extreme scenarios. 2022 Power System and Green Energy Conference (PSGEC), 
2022, pp. 739–743. Shanghai, China.
Y. Wu et al.                                                                                                                                                                                                                                      
Renewable Energy 253 (2025) 123645 
13
