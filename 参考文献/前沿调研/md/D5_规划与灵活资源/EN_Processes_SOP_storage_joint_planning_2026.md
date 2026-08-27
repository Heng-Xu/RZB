<!--
source: D5_规划与灵活资源/EN_Processes_SOP_storage_joint_planning_2026.pdf
sha256: a02afd3a18ab7a2f6c3f401ae68ce2e4cf42bc419de2ca331f958d3476488e63
method: pymupdf
pages: 19
-->

<!-- page 1/19 -->

Academic Editor: Massimo Caruso
Received: 14 February 2026
Revised: 14 March 2026
Accepted: 17 March 2026
Published: 21 March 2026
Copyright: © 2026 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license.
Article
Joint Planning Method for Soft Open Points and Energy Storage
in Hybrid Distribution Networks Based on Improved DC
Power Flow
Wei Luo 1, Chenwei Zhang 1, Xionghui Han 1, Fang Chen 1, Zhenyu Lv 2,*
and Yuntao Zhang 2
1
Meizhou Power Supply Bureau of Guangdong Power Grid, Guangdong Power Grid Corporation,
Meizhou 514021, China; lwgd86@126.com (W.L.); 13723633386@163.com (C.Z.); yliu202501@163.com (X.H.);
fangchen03@126.com (F.C.)
2
School of Electrical and Automation Engineering, Nanjing Normal University, Nanjing 210023, China;
yuntaozhang9@gmail.com
*
Correspondence: zhenyu_lv@nnu.edu.cn
Abstract
Intelligent soft open points (SOPs) and energy storage systems (ESSs) are effective ways
to absorb distributed new energy in the spatial and temporal dimensions, and play an
important role in improving the new-energy-carrying capacity of distribution networks.
Existing planning models for SOPs and ESSs in distribution networks are often nonlinear
and non-convex, and are usually transformed into a mixed-integer second-order cone opti-
mization (MISOCP) model. However, this transformation often needs stringent relaxation
conditions, and the solution speed and convergence performance of the model are poor.
These disadvantages make traditional MISOCP models unsuitable for optimal planning
for complex hybrid networks. To overcome these limitations, a joint planning method
for AC/DC hybrid networks based on an improved DC power flow (IDCPF) algorithm
is proposed in this paper. The proposed method transforms the original nonlinear model
into an approximate linear model, improving the solution speed and accuracy of the model.
The effectiveness of the proposed method is validated through case studies on an improved
AC/DC 43-node network, which demonstrates the accuracy and numerical stability of the
planning model.
Keywords: DC power flow; energy storage system; hybrid distribution network; joint
planning; soft open point
1. Introduction
As the penetration rate of new energy generation continues to increase, its inter-
mittency and uncertainty pose significant challenges to the stable operation of power
systems [1–3]. Therefore, it is imperative to effectively assess the new-energy-carrying
capacity of existing power grids and utilize system flexibility resources to improve the
proportion of new energy as well as the quality and reliability of the power supply.
Currently, to address the impacts brought about by distributed generation (DG) in-
tegration, numerous studies have focused on planning and regulation methods for high-
penetration DG access. References [4–6] employ network reconfiguration strategies during
distribution network planning to achieve DG configuration in high-penetration scenarios,
while Ref. [7] develops a tripartite optimization model coordinating the interests of DG
operators, distribution companies, and consumers through carbon/green certificate trading
Processes 2026, 14, 1013
https://doi.org/10.3390/pr14061013



<!-- page 2/19 -->

Processes 2026, 14, 1013
2 of 19
mechanisms. The model incorporates demand response programs and energy storage
flexibility to improve DG utilization while reducing carbon footprint in power generation
and transmission. To address active distribution network planning, Ref. [8] establishes
a multi-agent framework involving distributed generator owners, load aggregators, and
distribution network operators (DNOs). This hierarchical structure features a bi-level
optimization where DNOs optimize network expansion at the upper level while other
stakeholders coordinate DG configuration at the lower level. Building on this, Ref. [9] pro-
poses a multi-stage expansion planning framework with a two-layer optimization model.
The upper layer determines optimal DG allocation schemes across planning phases, while
the lower layer optimizes dispatch under various scenarios. From a power electronics
perspective, Ref. [10] presents a smart inverter control strategy for PV-battery systems,
implementing optimized Volt/Var regulation to enhance DG hosting capacity through
reactive power compensation and optimal siting of distributed resources. Most of the afore-
mentioned studies improve the new-energy-carrying capacity of the distribution network
and enhance power quality by establishing multi-layer optimization models that include
both DG planning and distribution network optimization stages. However, the proposed
methods mainly focus on the temporal dimension for planning and configuring flexibility
resources, without considering the influence of the distribution network’s interconnection
structure and spatial power flow distribution on DG integration capacity, which limit the
effectiveness of improving the new-energy-carrying capacity.
The soft open point (SOP) is a power electronic device capable of replacing traditional
interconnection switches, enabling flexible interconnection between different feeders in dis-
tribution networks and optimizing power flow distribution in the spatial dimension [11–13].
This has led to extensive research on planning and configuration methods for flexible inter-
connection distribution networks based on SOPs. Ref. [14] proposes a two-level coordinated
planning model for DG and SOPs, leveraging the characteristics of unbalanced distribution
networks. A multi-objective stochastic information gap decision model to minimize the
comprehensive cost for distributed system operators (DSOs) in SOP planning is developed
to address the cost uncertainties in [15]. Ref. [16] employs a two-stage robust optimization
approach to evaluate photovoltaic (PV) carrying capacity in scenarios integrating SOPs
and electric vehicles (EVs), enhancing solution efficiency through convex relaxation and
column-and-constraint generation algorithms.
In joint planning, most studies involve DG and energy storage systems (ESSs); thus,
the complementary spatial and temporal characteristics of ESSs and SOPs in power trans-
mission have emerged as a research focus. Ref. [17] introduces a multi-port SOP and
ESS collaborative planning method, optimizing distribution network flexibility based on
the branch current distribution and network loss sensitivity indices. The effectiveness of
this method was validated through comparisons using the IEEE 33-node test system. An
integrated planning approach for ESOP devices (ESSs and SOPs) to achieve economic and
flexible operation of distribution networks was proposed in [18]. Additionally, some stud-
ies have explored SOP planning and configuration from the perspective of fault recovery
and resilience enhancement in distribution networks. Ref. [19] proposes a collaborative
planning model for SOPs and remote-controlled switches (RCSs) to improve distribution
network resilience. This model incorporates multiple fault recovery stages and optimized
configurations to minimize equipment investment costs and load disconnection penalties,
with its effectiveness verified through case studies.
However, most existing studies focus primarily on economic aspects, neglecting the
impact of ESS and SOP joint planning on key indicators such as the distributed generation
carrying capacity, power quality, supply capability, and reliability of distribution networks.
Furthermore, multi-objective joint planning of ESSs and SOPs remains underexplored.
https://doi.org/10.3390/pr14061013



<!-- page 3/19 -->

Processes 2026, 14, 1013
3 of 19
The aforementioned methods exhibit certain limitations. Second-order cone relaxation
methods require carefully designed objective functions to drive the relaxation process
toward optimal solutions. Therefore, these methods impose stringent requirements on
relaxation conditions, limiting their general applicability and convergence performance. As
the distribution network scale increases, the relaxation of numerous constraints significantly
affects model solution speed, rendering these methods unsuitable for rapid assessment of
renewable energy systems.
The DC power flow model simplifies power flow calculations by ignoring the rela-
tionship between reactive power and voltage, thereby reducing the computational burden
of the model. Currently, extensive research is being conducted on the application scope
of the DC power flow model and the factors affecting its solution accuracy. Ref. [20] in-
vestigates the impact of factors such as line series resistance, line impedance ratio, and
voltage phase angle difference at both ends of the line on the accuracy of DC power flow.
Ref. [21] proposes an extended DC power flow (EDCPF) model incorporating voltage
magnitude, based on the quasi-linear relationship between voltage angle and voltage
magnitude. The reliability and accuracy of the EDCPF model were validated through
standard test systems. Ref. [22] develops a sensitivity analysis-based power flow (SAPF)
method for multi-terminal high-voltage DC systems based on voltage source converters
(VSCs). This method calculates state variables of extended AC grids through sensitivity
analysis, significantly reducing computational burden and avoiding convergence issues in
traditional sequential methods.
In summary, a clear research gap remains in the current literature. Although existing
works have explored SOP and ESS integration, they predominantly focus on economic
objectives and rely heavily on nonlinear or mixed-integer second-order cone optimization
(MISOCP) models that suffer from stringent relaxation conditions and high computational
burdens. There is a critical lack of a comprehensive, multi-objective joint planning frame-
work that concurrently optimizes spatial–temporal flexibility, renewable hosting capacity,
and power quality, while fundamentally overcoming the mathematical bottlenecks of
traditional AC power flow in large-scale hybrid networks.
To achieve the joint planning of SOPs and ESSs in AC/DC hybrid networks, this paper
proposes a bi-level optimization model for the flexible interconnection distribution network
based on an improved DC power flow algorithm. The power flow constraints in this model
are approximate linear equations, which avoids the cone relaxation of large-scale nonlinear
constraints. This eliminates convergence issues while improving solution efficiency. Finally,
the proposed model is validated using the improved AC/DC 43-node system.
The remainder of this paper is organized as follows: Section 2 details the proposed
improved DC power flow (IDCPF) algorithm and formulates the multi-objective bi-level
joint planning model for SOPs and ESSs. Section 3 presents the simulation results and
comparative analysis. Finally, Section 4 concludes the paper.
2. Joint Planning Method for Hybrid Networks Based on Improved DC
Power Flow Algorithm
2.1. Improved DC Power Flow Algorithm
In high-voltage power transmission networks, the DC power flow algorithm is com-
monly used to quickly calculate the power flow. However, in medium- and low-voltage
distribution networks, the traditional DC power flow algorithm is no longer applicable.
Therefore, an improved DC power flow (IDCPF) algorithm is introduced in this paper first.
The improved algorithm is demonstrated by the following distribution network.
As it shows in Figure 1, in the analysis of the above radial distribution networks, the
active and reactive power of each. This process is based on the power injection at each
https://doi.org/10.3390/pr14061013



<!-- page 4/19 -->

Processes 2026, 14, 1013
4 of 19
node and the network’s topology, while disregarding the active and reactive power losses
in the lines.





Pij = Pjj + ∑
k∈Bj
Pjk
Qij = Qjj + ∑
k∈Bj
Qjk
(1)
where Pij and Qij are the active and reactive power flows through branch ij, and Pjj and
Qjj are the respect power injections at node j. Bj denotes the child sets of node j. Thus, the
active and reactive power of each branch can be recursively calculated using Equation (1).
Based on the power flow distribution of the branches, the voltage phase angle at each node
can be back-calculated using the following linear equation:
(
θj = θi −(xijPij −rijQij)
θ0 = 0
(2)
where θi and θj represent the voltage phase angles at nodes i and j, respectively. Next, to
calculate the voltage magnitude at each node, the complex power flow equation for an
N-node distribution network is established as follows:
S = diag[V]·Y∗·V∗
(3)
where S, Y and V represent the complex power injection vector, the complex admittance
matrix, and the complex voltage vector of the distribution network nodes, respectively.
Diag[V] denotes a diagonal matrix with elements from the complex vector V on its diagonal.
Additionally, the complex voltage at node i can be expressed in the following form:
Vi = (Vb
i + ∆Vi)eiθi
(4)
where the real number Vib represents the reference value of the voltage magnitude, and the
real number ∆Vi represents its correction term. Substituting Equation (4) into Equation (3)
yields the following form of the power flow equation:
S = diag[Vb + ∆V]·[Y∗∗θ]·[Vb + ∆V]
(5)
where θ is an N-order complex matrix of phase angle differences, in which the elements
θij = ej(θi−θj). The real vectors Vb and ∆V represent the reference voltage vector and
the correction vector, respectively. Let Y+ = Y∗∗θ; then, Equation (5) can be expanded
as follows:
S = diag[Vb]·Y+·∆V + diag[∆V]·Y+·∆V
+diag[Vb]·Y+·Vb + diag[∆V]·Y+·Vb
(6)
1
2
3
4
5
7
8
6
9
Figure 1. Topology of a 9-node radial distribution network.
https://doi.org/10.3390/pr14061013



<!-- page 5/19 -->

Processes 2026, 14, 1013
5 of 19
Assuming ∆V is small and ignoring the higher-order terms, Equation (6) can be further
simplified to:
(
∆S = diag[∆V]·Y+·Vb + diag[Vb]·Y+·∆V
∆S = S −diag[Vb]·Y+·Vb
(7)
diag[Y+Vb]·∆V = diag[∆V]·Y+·Vb
(8)
Substituting Equation (8) into Equation (7) yields the following form of the power
flow equation:
[∆S]PQ = As·[∆V]PQ
(9)
where [•]PQ represents the matrix obtained after eliminating the data for PV nodes and
slack nodes. The complex matrix As is given by diag[Y+Vb] + diag[Vb]·Y+, which is also
obtained after eliminating the data for PV nodes and slack nodes. Separating the real and
imaginary parts of the above complex matrix yields the following equations:
(
[∆S]PQ = [∆P]PQ + j[∆Q]PQ
As = AP + jAQ
(10)
Substituting Equation (10) into Equation (9) gives:





[∆S]PQ = As·[∆V]PQ
[∆P]PQ = AP·[∆V]PQ
[∆Q]PQ = AQ·[∆V]PQ
(11)
Finally, the active and reactive power equations in Equation (11) can be combined into
an overdetermined system of equations, and the least squares solution for this overdeter-
mined system is as follows:
[∆V]PQ =
 
[AT
P AT
Q]·
"
AP
AQ
#!−1
·
 
[AT
P AT
Q]·
"
[∆P]PQ
[∆Q]PQ
#!
(12)
This solution is the least squares format (LSQ) for solving the voltage magnitude.
After calculating the voltage correction terms at the PQ nodes using the above formats,
the voltage magnitude and phase angle information for all nodes in the entire distribution
network can be obtained.
2.2. Joint Planning Model Based on the IDCPF Algorithm
The optimal allocation of DG, SOP, and ESS within distribution networks presents
itself as a multi-objective optimization challenge that necessitates balancing the interests of
multiple stakeholders. In order to holistically take into account elements like the economic
benefit of the distribution network, renewable energy accommodation capacity, power
supply proficiency, and power quality when arranging ESSs and SOPs, this study devises a
multi-objective bi-level joint planning model for an SOP and ESS.
2.2.1. Upper-Level Planning Model
Objective Function 1: Optimal Economic Benefit.
The economic benefit of the distribution network is primarily composed of three main
components: revenue from electricity sales, operational costs of the distribution network,
and investment costs associated with the ESS and SOP. The optimization objective is to
maximize the revenue of the distribution network. The operational costs of the distribution
network are primarily attributed to three factors: the cost of electricity exchange between
https://doi.org/10.3390/pr14061013



<!-- page 6/19 -->

Processes 2026, 14, 1013
6 of 19
the distribution network and the upstream grid, the operational costs of DG, and the
network loss costs. These components are mathematically represented in Equation (13):
minf1 = cS ∗SSOP + cE ∗SESS + CG −CS + CDG + CLOSS
(13)
where CG represents the cost incurred from energy exchange between the distribution
network and the upper-level grid. CS is the revenue from electricity sales to users by
the distribution network. CDG denotes the cost of purchasing electricity from DG by the
distribution network. CLOSS refers to the cost of network losses within the distribution
network. cS is the annualized cost per unit capacity of SOP equipment over its entire
lifecycle, and SSOP is the installed capacity of the SOP within the distribution network.
cE represents the annualized cost per unit capacity of energy storage equipment over
its entire lifecycle, and SESS is the total installed capacity of energy storage within the
distribution network.
The annualized cost over the entire lifecycle for each piece of equipment can be
calculated from its net present value (NPV) cost, expressed as follows:
(
cE = ζ(r, l)[CE,init + CE,rep −CE,sal + CE,om]
cS = ζ(r, l)[CS,init + CS,om]
(14)
where CE,init and CS,init represent the initial net present value (NPV) cost of the unit capacity
for energy storage and the SOP, respectively. CE,om and CS,om represent the annual operation
and maintenance NPV cost of the unit capacity for energy storage and the SOP, respectively.
CE,rep and CE,sal refer to the replacement cost and salvage income of the unit capacity
for energy storage, respectively. ζ(r,l) is the capital recovery factor, where r is the actual
discount rate and l is the equipment’s service life. The formula for calculating the capital
recovery factor is shown below:
ζ(r, l) =
T
365
r(1 + r)l
(1 + r)l −1
(15)
In this formula, T represents the number of daily sampling points within the optimiza-
tion period. The cost incurred from energy exchange between the distribution network and
the upper-level grid can be expressed by Equation (16):
CG =
T
∑
t=1
λG
t Pex,t∆t
(16)
where λtG is the price at which the distribution network purchases or sells electricity
from or to the upper-level grid during time period t. Pex,t represents the exchange power
between the distribution network and the upper-level grid during time period t. The cost
CDG of purchasing electricity from distributed generation by the distribution network can
be expressed as follows:
CDG =
NDG
∑
i=1
T
∑
t=1
λDG
i,t PDG
i,t ∆t
(17)
In this formula, NDG is the number of grid-connected distributed generators in the
system. λi,tDG represents the feed-in tariff of the i-th grid-connected DG during time period
t. Pi,tDG denotes the output power of the i-th grid-connected DG during time period t.
Objective Function 2: Maximum Renewable Energy Hosting Capacity.
The maximum renewable energy hosting capacity is defined as the sum of the capaci-
ties of distributed energy sources connected to each node in the distribution network, with
https://doi.org/10.3390/pr14061013



<!-- page 7/19 -->

Processes 2026, 14, 1013
7 of 19
the objective of maximizing the installed capacity of distributed energy sources. This value,
denoted as SDG, can be calculated using the following equation:
minf2 = −SDG
(18)
Objective Function 3: Optimal Power Supply Capability.
The supply capability of the distribution network is a key indicator for evaluating the
stable operation of the system. In this model, the system’s supply capability is primarily
assessed through two critical metrics: branch load margin and transformer load margin. To
derive the optimal objective function for the system’s supply capability, a normalization
method is employed. The optimization goal is to minimize the weighted sum of the branch
load margin and transformer load margin, as formulated in Equation (19).
minf3 = −(w1IM + w2TM)
(19)
In this formula, w1 is the weighting coefficient for the branch load margin, IM rep-
resents the branch load margin of the system, w2 is the weighting coefficient for the
transformer load margin, and TM denotes the transformer load margin of the system, with
w1 + w2 = 1.
The branch load margin, as defined in the equation above, represents the ratio of the
available capacity of a branch in the distribution network to its maximum line capacity. A
higher branch load margin indicates that the available capacity of the branch is sufficient to
meet the actual load demand. Conversely, a lower margin suggests that the branch may be
at risk of overloading. The specific calculation method is as follows:
IM =
1
TNL
T
∑
t=1
∑
ij∈AL∪DL
(Slmax −Sij,t)/Slmax
(20)
where AL and DL represent the sets of AC lines and DC lines, respectively. NL is the total
number of branches in the system. Slmax is the maximum capacity limit of branch ij, and
Sij,t is the apparent power of branch ij at time t. The concept of transformer load margin in
the distribution network is similar to that of the branch load margin. It is the ratio between
the transformer’s rated capacity and the actual load. The calculation method is shown in
Equation (21).
TM = 1
T
T
∑
t=1
ST
max −ST
t
STmax
(21)
where SmaxT represents the rated capacity of the transformer at the substation node in the
distribution system, and StT denotes the apparent power of the transformer at time t.
Objective Function 4: Optimal Power Quality of the System.
Voltage deviation rate is a key indicator for assessing the power quality in a distribu-
tion network. The comprehensive voltage deviation rate of the distribution network can
represent this quality. The optimization goal is to minimize the voltage deviation rate, as
shown in Equation (22).
minf4 =
1
TND
T
∑
t=1
∑
i∈AN∪DN
(Ui,t −Ui, ref )2
(22)
where AN and DN represent the sets of AC nodes and DC nodes, respectively. ND is the
total number of nodes in the system, and Ui,t denotes the voltage value at node i during
time period t. Ui,ref represents the rated voltage at node i.
Constraints:
https://doi.org/10.3390/pr14061013



<!-- page 8/19 -->

Processes 2026, 14, 1013
8 of 19
0 ≤SDG ≤
∑
i∈AN∪DN
αiSDGmax
(23)
0 ≤SESS ≤
∑
i∈AN∪DN
βiESSmax
(24)
∑
i∈AN∪DN
αi = NDG
(25)
∑
i∈AN∪DN
βi = NESS
(26)
In these formulas, SDGmax represents the upper limit of the capacity of DGs that can
be connected to each node, and ESSmax represents the upper limit of the capacity of ESSs
configured at each node, both of which are predetermined values. αi and βi represent
the connection status, which are 0–1 variables: a value of 0 indicates that the node does
not connect to a distributed generator or energy storage, while a value of 1 indicates
a connection. NDG denotes the allowed number of DG connections in the system, and
NESS denotes the allowed number of ESS connections in the system, both of which are
predetermined values.
2.2.2. Lower-Level Operation Model
Objective Function: Sum of network losses and SOP losses.
The lower-level operational model focuses on identifying the ideal operational status
of the distribution network. This is achieved by reducing the combined total of network
losses and SOP losses, following the determination of the total installed capacity and
locations of photovoltaic and energy storage devices. The objective function is articulated
as follows:
minf =
T
∑
t=1
∑
ij∈AL∪DL
RijI2
ij,t +
T
∑
t=1
NSOP
∑
i=1
P SOP,loss
i,t
(27)
where Rij represents the resistance of the corresponding line, NSOP is the number of SOPs
connected to the distribution network, and Pi,tSOP,loss denotes the active power loss of the
i-th SOP during time period t.
Constraints:
(1)
SOP Operating Constraints
The soft open point aims to replace traditional feeder tie switches with controllable
power electronic converters, thereby achieving flexible and soft connections between
feeders under normal conditions. This allows for flexible, fast, and precise power exchange
control and power flow optimization [23–25]. In this paper, a back-to-back voltage source-
type SOP is used, and the following relevant constraints are considered.
(a)
SOP Active Power Balance Constraint
The active power output from the SOP should be equal to the active power input to
the SOP plus the total power losses generated by the converters at both ports. Therefore,
the SOP active power balance constraint can be described as follows:
PSOP
i,t
+ PSOP
j,t
+ PSOP,loss
i,t
+ PSOP,loss
j,t
= 0
(28)
where Pi,tSOP represents the active power transmitted by the SOP at the port connected
to node i during time period t, and Pj,tSOP represents the active power transmitted by
the SOP at the port connected to node j during time period t. Pi,tSOP,loss represents the
converter power loss at the SOP port connected to node i during time period t, and Pj,tSOP,loss
https://doi.org/10.3390/pr14061013



<!-- page 9/19 -->

Processes 2026, 14, 1013
9 of 19
represents the converter power loss at the SOP port connected to node j during time
period t.
(b)
SOP Active Power Loss Constraint
The loss of each port converter of the SOP is proportional to the sum of the squares
of the active and reactive power it transmits. The SOP active power loss constraint is
described as follows:
PSOP,loss
i,t
= ASOP
i
r
PSOP
i,t
2
+

QSOP
i,t
2
(29)
PSOP,loss
j,t
= ASOP
j
r
PSOP
j,t
2
+

QSOP
j,t
2
(30)
where AiSOP is the loss coefficient of the SOP converter connected at node i, and AjSOP is
the loss coefficient of the SOP converter connected at node j. Qi,tSOP represents the reactive
power transmitted by the SOP at the port connected to node i during time period t, and
Qj,tSOP represents the reactive power transmitted by the SOP at the port connected to node
j during time period t.
(c)
SOP Capacity Limit Constraint
At any given time, the active and reactive power transmitted by the converters at
each SOP port should be less than their rated capacity. The SOP capacity limit constraint is
described as follows:
r
PSOP
i,t
2
+

QSOP
i,t
2
≤SSOP
i
(31)
r
PSOP
j,t
2
+

QSOP
j,t
2
≤SSOP
j
(32)
where SiSOP represents the capacity of the SOP converter connected at node i, and SjSOP
represents the capacity of the SOP converter connected at node j.
(2)
AC Line Power Flow and Voltage Constraints
(a)
Power Flow Constrains
To avoid second-order cone relaxation, this paper does not employ the conventional
branch power flow equations, but instead uses the improved DC power flow algorithm to
describe the line power flow constraints.





Pji,t = ∑
k∈Bi
Pik,t + Pinj
i,t
Qji,t = ∑
k∈Bi
Qik,t + Qinj
i,t
∀i ∈Bj ∩AN
(33)
(
PDG
i,t
+ PSOP
i,t
−Pload
i,t
−Pbess
i.t
−PVSC,AC
i,t
= Pinj
i,t
QSOP
i,t
−Qload
i,t
−QVSC,AC
i,t
= Qinj
i,t
(34)
where Pij,t and Qij,t represent the active and reactive power flowing through branch ij at
time t, respectively. Pi,tinj and Qi,tinj are the active and reactive power injected into node i,
respectively. Pi,tDG and Pi,tload are the active power of distributed renewable energy and
the load at node i at time t, respectively. Qi,tload is the reactive power of the load at node i
at time t. Pi,tbess is the output power of the ESS at node i at time t. Pi,tVSC,AC and Qi,tVSC,AC
are the active and reactive power injected into the AC side of the voltage source converter
(VSC) at time t, respectively.
(b)
Node Voltage Constrains
https://doi.org/10.3390/pr14061013



<!-- page 10/19 -->

Processes 2026, 14, 1013
10 of 19







∆U = A−1
s ·∆S
∆Si,t = Pinj
i,t + jQinj
i,t −∑
j∈Bi
y+
ij Ub
i Ub
j
Vl,A ≤∆Ui,t + Ub
i ≤Vu,A
∀i ∈AN
(35)
where Vl,A and Vu,A are the lower and upper limits of AC line voltage. Uib represents the
reference value of the voltage magnitude of node i, and ∆Ui,t represents its correction term
at time t. The remaining parameters have the same meaning as above.
(3)
DC Line Power Flow and Voltage Constraints
(a)
Power Flow Constrains
Similar to the AC lines, the power flow constraints for the DC lines can also be obtained.



Pji,t = ∑
k∈Bi
Pik,t + Pinj
i,t
PDG
i,t
−Pload
i,t
−Pbess
i,t
+ PVSC,DC
i,t
= Pinj
i,t
∀i ∈Bi ∩DN
(36)
where Pi,tVSC,DC is the active power injected into the DC side of the VSC at time t. The
remaining parameters have the same meaning as above.
(b)
Node Voltage Constrains
(
U = B−1
s ·PL
V2
l,D ≤Ui,t ≤V2
u,D
∀i ∈DN
(37)
where U represents the vector of the square of the amplitude of the DC node voltage,
and PL represents the DC line power vector. The matrix Bs is determined by the system
admittance matrix. Vl,D and Vu,D are the lower and upper limits of DC line voltage.
(4)
Energy Storage System Operating Constraints
(a)
Energy Storage Capacity Constraint
Considering the impact of the State of Charge (SOC) on the battery’s lifespan, it is
necessary to set upper and lower limits on the real-time capacity of the energy storage
system, which can be expressed as:





ESSi,t+∆t = ESSi,t + kbiPbess-in
i,t
∆t + Pbess-out
i,t
∆t/kbo
ηminESSi ≤ESSi,t ≤ηmaxESSi
Pbess
i,t
= Pbess-in
i,t
+ Pbess-out
i,t
(38)
In this formula, ESSi,t and ESSi,t+∆t represent the remaining energy storage capacity at
node i at times t and t + ∆t, respectively. ηmin and ηmax are the minimum and maximum
values of the State of Charge (SOC), respectively. ESSi represents the energy storage
capacity configured at node i. Pi,tbess-in and Pi,tbess-out are the charging and discharging
power of the energy storage at node iii at time t, respectively. kbi and kbo represent the
charging and discharging efficiency of the energy storage, respectively.
(b) Energy Storage Charging and Discharging Power Constraint
Since the energy storage batteries are connected to the grid through converters, the
charging and discharging power of the energy storage system is influenced not only by the
https://doi.org/10.3390/pr14061013



<!-- page 11/19 -->

Processes 2026, 14, 1013
11 of 19
charging and discharging rate of each battery but also by the capacity of the grid-connected
converter. The constraint is as follows:





0 ≤Pbess-in
i,t
≤Ui,ch,tPmax
i,ch
Ui,dis,tPmax
i,dis ≤Pbess-out
i,t
≤0
Ui,ch,t + Ui,dis,t ≤1
(39)
where Ui,ch,t and Ui,dis,t represent the charging and discharging states of the energy storage
at node i at time t, respectively. Ui,ch,t = 1 indicates that the energy storage is charging at that
time, while Ui,dis,t = 1 indicates that it is discharging. Pi,chmax and Pi,dismax are the maximum
charging and discharging power limits of the energy storage at node i, respectively.
(5)
VSC Operating Constraints
The VSC serves as the connection point for the AC-DC lines, and its constraints include
capacity constraints and line power constraints.
(
(PVSC,AC
i,t
)
2 + (QVSC,AC
i,t
)
2 ≤S2
i,VSC
PVSC,AC
i,t
+ PVSC,DC
i,t
= 0
(40)
where Si, VSC represents the rated apparent power of the VSC at node i. The remaining
parameters have the same meaning as above.
2.2.3. Solution for the Bi-Level Optimization Model
To streamline the solution process, an enhanced Multi-objective Particle Swarm Op-
timization (MOPSO) algorithm is used in the model. MOPSO is utilized to ascertain the
upper-level DG and energy storage siting and sizing strategies, whereas the lower-level
model is solved by the business solver Gurobi. The flowchart is depicted in Figure 2.
Input distribution network data and Particle 
Swarm Optimization (PSO) parameters and 
randomly generate the initial population.
Considering the constraints and calculate the 
objective function value of the current 
population.
The upper-layer DG , SOP and ESS siting 
and sizing schemes are passed to the lower 
layer
Transform the model into a Second-Order 
Cone Programming (SOCP) model
Solve the optimal operation state of the 
flexible AC/DC network to obtain the current 
decision-based SOP configuration scheme
The results from the lower layer are returned 
to the upper layer to calculate the upper-layer 
objective function
Sort the objective function values to find the current optimal 
solution and the global optimal solution
Calculate the particle position difference value and the 
dynamic inertia weight, and update the particle's position 
and velocity
Particle crossover mutation
Calculate the objective function 
values of the offspring population
Sort the new population based on the objective function 
values, and select the better particles to form the next 
generation population
Check if the 
number of iterations has been 
reached
Output the optimal results
Yes
No
 
Figure 2. Hybrid algorithm flowchart.
https://doi.org/10.3390/pr14061013



<!-- page 12/19 -->

Processes 2026, 14, 1013
12 of 19
3. Simulation Analysis and Algorithm Validation
3.1. Case Overview and Parameter Settings
This paper modifies the IEEE 33-node system into a 43-node AC/DC flexible intercon-
nected distribution network, and verifies and analyzes the double-layer planning model
and method proposed in the above text. This AC/DC distribution network has two DC
lines, as shown in Figure 3, and the load conditions of each node on the DC lines are shown
in Table 1. The rated voltage of the AC part is 12.66 kV, the rated voltage of the DC part is
±10 kV, the capacity of the VSC is 500 kVA, the minimum installation capacity of the SOP
is 100 kVA, the maximum installation capacity is 500 kVA, and the power loss coefficient of
the converter at each end is 0.02. The capacity of the distribution network transformer is
10 MVA, and the maximum allowable reverse power does not exceed 80% of the
transformer capacity.
The remaining parameters are the same as the IEEE 33-node
standard case.
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
AC Line
DC Line
34
35
36
37
38
39
40
41
42
43
SOP1
SOP2
SOP3
VSC1
VSC2
VSC3
VSC4
 
Figure 3. The topology of the improved 43-node AC/DC hybrid distribution network.
Table 1. Load on DC line.
Node
Load/kW
Node
Load/kW
34
40
39
40
35
120
40
140
36
80
41
60
37
50
42
70
38
150
43
100
Distributed power generation, exemplified by photovoltaic systems, involves 24 dis-
crete sampling points within a single day, derived from a comprehensive dataset encom-
passing 8760 annual operational hours. The K-means algorithm is employed to perform
clustering operations, extracting representative daily source-load unit capacity curves, as
illustrated in Figure 4. Within the system, the node voltage is meticulously maintained
within a per-unit range of 0.95 to 1.05, ensuring stable operational conditions. Addition-
ally, the SOC for energy storage components is confined between 0.2 and 1.0 to optimize
performance and longevity. Parameters pertinent to SOP and energy storage devices are
comprehensively detailed in Table 2. The parameters for the Particle Swarm Optimization
(PSO) algorithm are set as follows: the population size is 100, the number of iterations
is 200, the mutation rate is 0.05, the crossover rate is 0.1, the minimum inertia coefficient
ωmin is 0.4, ωmax is 0.9, and the dynamic learning factors are c1k = 2.5 + (0.5-2.5)k/gen and
c2k = 0.5 + (2.5-0.5)k/gen, where k is the current number of iterations and gen is the
total number of iterations. The testing environment is the 12th Gen Intel(R) Core(TM)
i7-12700H CPU with a main frequency of 2.70 GHz and 16 GB of memory, the development
environment is Win 11 64-bit, and the simulation software is Matlab R2020b.
https://doi.org/10.3390/pr14061013



<!-- page 13/19 -->

Processes 2026, 14, 1013
13 of 19
0
5
10
15
20
25
Time/h
0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9
1
P/p.u.
PV Output
Load Curve
 
Figure 4. Typical-day DG output and load curve.
Table 2. SOP and storage device parameters.
Parameter
Value
Discount Rate
0.08
Economic Service Life/Years
20
SOP Unit Capacity Investment
Cost/(Yuan/kVA)
1000
SOP Loss Coefficient
0.02
SOP Operation and Maintenance
Coefficient
0.01
Energy Storage Capacity
Cost/(Yuan/kWh)
1000
Energy Storage Power Cost/(Yuan/kW)
1500
Energy Storage Operation and
Maintenance Cost /(Yuan/kWh)
0.0195
3.2. Planning Results and Analysis
Using the parameters and solution methods mentioned above, the multi-objective
joint planning model for intelligent soft open points and energy storage in AC/DC flexible
interconnected distribution networks is solved. Since the upper-level model is a multi-
objective optimization problem, the solution is a set of Pareto optimal solutions, as depicted
in Figure 5. To select the optimal solution from these Pareto optimal solutions, this study
employs the Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS)
method. This method compares each alternative solution with the positive and negative
ideal solutions, and ultimately determines the optimal solution. The weight values of the
indicators used in the TOPSIS method are provided in Table 3. Finally, the optimal planning
schemes for SOP, ESS, and DG are presented in Table 4.
Table 3. Index weight value.
Category
f1
f2
f3
f4
Indicator Weights
0.316
0.344
0.24
0.1
Table 4. Configuration scheme of distribution network.
Category
Access Node
Access Capacity
Units
DG
2, 7, 21, 37, 39, 43
6, 1.33, 1.63, 0.79, 1.07, 0.77
MW
ESS
7, 31, 38
0.18, 1.0, 0.92
MWh
SOP
8–22, 9–15, 18–33
0.5, 0.25, 0.3
MVA
https://doi.org/10.3390/pr14061013



<!-- page 14/19 -->

Processes 2026, 14, 1013
14 of 19
 
-0.466 -0.456 -0.447-0.438 -0.429 -0.420 -0.410-0.401 -0.392 -0.383 -0.374
f3/p.u.
3.2545
3.2721
3.2896
3.3072
3.3248
3.3424
3.3599
3.3775
3.3951
3.4127
3.4303
f4/%
−0.466 
f3/p.u. 
0.456 
− 
0.447 
− 
0.438 
−
0.429 
− 
0.420 
−
0.410 
− 
0.401 
− 
0.392 
−
0.383
− 
0.374 
−
-14.6 -12.8 -10.9
-9.0
-7.1
-5.2
-3.3
-1.5
-0.5
1.3
3.1
f1/Yuan
-15
-13.8
-12.7
-11.6
-10.4
-9.3
-8.2
-7.0
-5.9
-4.8
-3.6
f2/MW
x103
−14.6 −12.8 − 10.9 − 9.0
− 7.1 −5.2
−3.3 − 1.5
−0.5 1.3
3.1
f1/Yuan
− 15 
− 13.8 
− 12.7 
− 11.6 
− 10.4 
− 9.3 
− 8.2 
− 7.0 
− 5.9 
− 4.8 
− 3.6 
f2/MW 
×103 
Figure 5. Pareto frontier.
To verify the effectiveness of the proposed multi-objective optimization method, this
paper sets up the following three scenarios to compare the DG penetration rate and distri-
bution network performance indicators under different scenarios.
Scenario I: Only the SOP is connected.
Scenario II: On the basis of SOP connection, a 2.1 MWh energy storage device is
connected at a single point (Node 31).
Scenario III: The proposed joint plan.
The supremacy of the proposed method is concluded by the numerical values, which
are shown in Table 5.
Table 5. Index comparison between different scenarios.
f1/Yuan
f2/MW
f3/p.u.
f4/%
Scenario I
−11.1 × 103
8.9
−0.32
3.5
Scenario II
−12.8 × 103
10.4
−0.41
3.33
Scenario III
−13.5 × 103
11.59
−0.42
3.3
https://doi.org/10.3390/pr14061013



<!-- page 15/19 -->

Processes 2026, 14, 1013
15 of 19
From Table 5, it can be seen that due to the additional energy storage equipment config-
ured in Scenarios II and III, the access capacity of DG has significantly increased, resulting
in a substantial reduction in the purchase cost of the distribution network. Although the
one-time cost of purchasing energy storage is relatively high, the cost apportionments of
the ESS still lead to an increase in the overall revenue. Additionally, with the increase in DG,
although the random fluctuation increases, the SOP and ESS effectively improve the power
quality of the distribution network. Further, the method proposed in this paper enables the
SOP and ESS to optimize the line flow in both the spatial and temporal dimensions; thus,
the capability to supply power will be better.
Figure 6 shows the active power transmission of SOP (9–15) and SOP (8–22) within
a typical day, in which P denotes the active power measured in kilowatts (kW), and t
represents time, measured in hours (h). The three curves in the figure represent different op-
eration conditions under the aforementioned three scenarios in the flexible interconnected
AC/DC distribution network.
Figure 6. Active power transmission of SOPs under different scenarios.
In Scenario I, the absence of energy storage devices leads to a significant imbalance
between generation and load across feeders. This results in marked fluctuations in the active
power transmitted by the SOP, frequent power flow direction changes, and an intensified
power flow imbalance, all of which negatively impact the stability of the distribution
network. In Scenario II, despite the connection of energy storage devices, the reduction in
power transmission fluctuation is limited. The energy storage devices are only connected at
a single point and do not consider the complementary interaction between energy storage
and the SOP, leading to a decrease in total transmitted power and an underutilization of the
SOP’s power transfer capability. Scenario III, however, takes into account the flexibility of
dispersed energy storage connections and fully exploits the complementary effect between
the SOP and the energy storage devices. This results in more stable power transmission
and a higher total power output.
Figure 7 illustrates the magnitude of the charging and discharging power of the energy
storage in the AC/DC flexible distribution network during a typical day in Scenario III.
https://doi.org/10.3390/pr14061013



<!-- page 16/19 -->

Processes 2026, 14, 1013
16 of 19
0
5
10
15
20
25
-0.8
-0.6
-0.4
-0.2
0
0.2
0.4
0.6
0.8
1
1.2
Node7
Node31
Node38
P/kW
t/h
 
Figure 7. Energy storage charging and discharging power.
From Figure 7, it can be observed that the energy storage devices at each node mainly
charge during the night-time load valley period (0–5 h) and the midday high photovoltaic
generation period (11–14 h). On the one hand, charging during the load valley period allows
for peak-shaving and valley-filling arbitrage. Additionally, the charging power during
the midday is higher and highly coincides with the period of peak photovoltaic output,
indicating that the energy storage batteries absorb the excess photovoltaic generation
in the system during the middle of the day, achieving power transfer in the temporal
dimension, smoothing the midday photovoltaic peak, and enhancing the distribution
network’s capacity to accommodate photovoltaic generation. At other times during the
day, the energy storage focuses on discharging during the morning and evening load peak
periods, smoothing the load peaks. At the same time, in conjunction with the spatial power
transfer function of the SOP, it makes the power flow between feeders more balanced,
improving the system’s power supply capability and reducing network losses.
Figures 8–10 offer a comparison of voltage deviation across the entire day, voltage
variations at the node with significant voltage fluctuations (Node 18), and line loading
conditions during the midday peak photovoltaic generation period in the AC/DC flexible
distribution network across the three discussed scenarios.
0
5
10
15
20
25
0.000
0.005
0.010
0.015
t/h
 Scenario Ⅰ
 
 
Scenario Ⅱ
Scenario Ⅲ
Voltage Deviation/p.u.
Figure 8. Voltage deviation under different scenarios.
https://doi.org/10.3390/pr14061013



<!-- page 17/19 -->

Processes 2026, 14, 1013
17 of 19
0
5
10
15
20
25
0.96
0.98
1.00
1.02
t/h
Node Voltage/p.u.
 Scenario Ⅰ
 
 
Scenario Ⅱ
Scenario Ⅲ
 
Figure 9. Voltage values under different scenarios.
10
20
30
40
0
0.2
0.4
0.6
0.8
1.0
 
 
 
Scenario Ⅰ
Scenario Ⅱ
Scenario Ⅲ
0
Line number
Line Load Rate/p.u.
Figure 10. Line load rate comparison under different scenarios.
The results in Figures 8–10 demonstrate that the flexible AC/DC distribution network
configuration, derived from the multi-objective planning method presented in this paper,
exhibits several key advantages. The configuration shows enhanced complementarity
among devices, ensuring more effective interaction between components. It also provides a
planning scheme that is better suited to the existing distribution network structure, making
it more practical for implementation. Furthermore, the configuration exhibits improved
performance, leading to reduced system voltage deviation, mitigated voltage fluctuations,
and optimized branch load distribution. These improvements collectively contribute to a
more flexible and reliable system, better equipped to handle varying operational conditions
and enhance the overall power supply quality.
Finally, in order to verify the solution performance of the IDCPF algorithm, this paper
takes the solution time of the traditional SOCP method as the benchmark, and uses these
two algorithms to solve the lower-level operation model within the three scenarios. The
results are shown in Table 6.
Table 6. Solution time comparison between the two methods.
SOCP/s
IDCPF/s
Scenario I
15.3
8.9
Scenario II
18.1
13.4
Scenario III
28.7
22.5
From Table 6, it can be seen that the traditional SOCP method takes more time to
solve the model compared to the proposed IDCPF method. Specifically, in Scenario I,
https://doi.org/10.3390/pr14061013



<!-- page 18/19 -->

Processes 2026, 14, 1013
18 of 19
due to a large number of quadratic constraints brought about by the second-order cone
relaxation of the power flow equation, the solution time of SOCP is slower. Similarly, in
Scenario II, only the decision variables for energy storage charging and discharging have
been added; thus, the solution time of IDCPF is also faster. In Scenario III, in addition to
the aforementioned variables, decision variables (integer variables) for the storage capacity
at different locations are also introduced. In this scenario, although the IDCPF algorithm
approximately linearizes the power flow equations, it still takes a considerable amount
of time to handle the integer variables. Thus, the advantages of the proposed algorithm
are not sufficiently prominent. It is worth noting that the solution time above is only
for lower-level operation model; the locations of ESSs (0–1 variables) are given by the
upper-level model. However, if the location is the decision variable, the solution time of
Scenario III is 442.3 s. Thus, the 0–1 variables consume a lot of time during the solution
process, which is the reason why the joint planning model in this paper is decomposed into
a two-level model for solution.
4. Conclusions
This paper addresses the optimization configuration problem of various devices such
as DG, energy storage, and SOP devices in flexible AC/DC distribution networks. A multi-
objective particle swarm algorithm based on an improved DC power flow algorithm is used
to solve the joint planning model. From the case study of the improved 43-node flexible
AC/DC distribution network, it can be concluded that the multi-objective joint planning
model not only considers the enhancement of the distribution network’s new-energy-
carrying capacity but also takes into account the economic operation of the distribution
network and the improvement in the overall power quality of the system. Compared with
the pre-planning scenario, the economic benefit, DG capacity, and power supply capability
increased by 21.6%, 30.2%, and 31.25%, respectively. Additionally, the hybrid algorithm
based on IDCPF can be applied to large-scale mixed-integer nonlinear programming
problems. Combined with the optimal solution evaluation strategy, it can obtain the
optimal configuration scheme for AC/DC flexible distribution networks. However, this
research also faced certain challenges, primarily in balancing conflicting multi-objective
dimensions (e.g., economic cost vs. power quality) and ensuring the numerical convergence
of the IDCPF algorithm when scaling to complex network topologies.
Author Contributions: Conceptualization, W.L. and Z.L.; methodology, W.L. and C.Z.; software, Y.Z.;
validation, W.L., Z.L. and Y.Z.; formal analysis, W.L.; investigation, C.Z.; resources, Z.L.; data curation,
X.H.; writing—original draft preparation, W.L.; writing—review and editing, Z.L.; visualization, F.C.;
supervision, Z.L.; project administration, Z.L.; funding acquisition, Z.L. All authors have read and
agreed to the published version of the manuscript.
Funding: This work was supported by the China Southern Power Grid Project under grant
031400KC23120011.
Data Availability Statement: The original contributions presented in this study are included in the
article. Further inquiries can be directed to the corresponding author.
Conflicts of Interest: The authors declare that this study receive funding from China Southern Power
Grid. The funder was not involved in the study design; the collection, analysis, or interpretation of
data; the writing of this article; or the decision to submit it for publication.
References
1.
Hou, Q.; Du, E.; Zhang, N.; Kang, C. Impact of high renewable penetration on the power system operation mode: A data-driven
approach. IEEE Trans. Power Syst. 2020, 35, 731–741. [CrossRef]
https://doi.org/10.3390/pr14061013



<!-- page 19/19 -->

Processes 2026, 14, 1013
19 of 19
2.
Mahzarnia, M.; Moghaddam, M.P.; Baboli, P.T.; Siano, P. A Review of the Measures to Enhance Power Systems Resilience. IEEE
Syst. J. 2020, 14, 4059–4070. [CrossRef]
3.
Zhang, N.; Jia, H.; Hou, Q.; Zhang, Z.; Xia, T.; Cai, X.; Wang, J. Data-Driven Security and Stability Rule in High Renewable
Penetrated Power System Operation. Proc. IEEE 2023, 111, 788–805. [CrossRef]
4.
Behbahani, M.R.; Jalilian, A.; Bahmanyar, A.; Ernst, D. Comprehensive Review on Static and Dynamic Distribution Network
Reconfiguration Methodologies. IEEE Access 2024, 12, 9510–9525. [CrossRef]
5.
Home-Ortiz, J.M.; Macedo, L.H.; Vargas, R.; Romero, R.; Mantovani, J.R.S.; Catalao, J.P.S. Increasing RES Hosting Capacity in
Distribution Networks Through Closed-Loop Reconfiguration and Volt/VAr Control. IEEE Trans. Ind. Appl. 2022, 58, 4424–4435.
[CrossRef]
6.
Ma,
L.-Y.;
Wang,
Y.-C.;
Wang,
C.-T. Robust Planning of Distributed Generators in Active Distribution Net-
work Considering Network Reconfiguration.
Autom.
Electr.
Power Syst.
2018, 42, 94–101.
Available online:
https://link.cnki.net/urlid/32.1180.TP.20180424.1547.016 (accessed on 24 April 2018). (In Chinese)
7.
Cheng, J.; Wang, L.; Pan, T. Optimized Configuration of Distributed Power Generation Based on Multi-Stakeholder and Energy
Storage Synergy. IEEE Access 2023, 11, 129773–129787. [CrossRef]
8.
Kabirifar, M.; Fotuhi-Firuzabad, M.; Moeini-Aghtaie, M.; Pourghaderi, N.; Shahidehpour, M. Reliability-Based Expansion
Planning Studies of Active Distribution Networks With Multiagents. IEEE Trans. Smart Grid 2022, 13, 4610–4623. [CrossRef]
9.
Kabirifar, M.; Fotuhi-Firuzabad, M.; Moeini-Aghtaie, M.; Pourghaderi, N.; Dehghanian, P. A Bi-Level Framework for Expansion
Planning in Active Power Distribution Networks. IEEE Trans. Power Syst. 2022, 37, 2639–2654. [CrossRef]
10.
Gush, T.; Kim, C.-H.; Admasie, S.; Kim, J.-S.; Song, J.-S. Optimal Smart Inverter Control for PV and BESS to Improve PV Hosting
Capacity of Distribution Networks Using Slime Mould Algorithm. IEEE Access 2021, 9, 52164–52176. [CrossRef]
11.
Fuad, K.S.; Hafezi, H.; Kauhaniemi, K.; Laaksonen, H. Soft Open Point in Distribution Networks.
IEEE Access 2020,
8, 210550–210565. [CrossRef]
12.
Farzamnia, A.; Marjani, S.; Galvani, S.; Kin, K.T.T. Optimal Allocation of Soft Open Point Devices in Renewable Energy Integrated
Distribution Systems. IEEE Access 2022, 10, 9309–9320. [CrossRef]
13.
Li, P.; Ji, H.; Wang, C.; Zhao, J.; Song, G.; Ding, F.; Wu, J. Coordinated Control Method of Voltage and Reactive Power for Active
Distribution Networks Based on Soft Open Point. IEEE Trans. Sustain. Energy 2017, 8, 1430–1442. [CrossRef]
14.
Wang, J.; Zhou, N.; Chung, C.Y.; Wang, Q. Coordinated Planning of Converter-Based DG Units and Soft Open Points Incorporating
Active Management in Unbalanced Distribution Networks. IEEE Trans. Sustain. Energy 2020, 11, 2015–2027. [CrossRef]
15.
Li, J.; Ge, S.; Zhang, S.; Xu, Z.; Wang, L.; Wang, C.; Liu, H. A multi-objective stochastic-information gap decision model for soft
open points planning considering power fluctuation and growth uncertainty. Appl. Energy 2022, 317, 119141. [CrossRef]
16.
Zhang, S.; Fang, Y.; Zhang, H.; Cheng, H.; Wang, X. Maximum Hosting Capacity of Photovoltaic Generation in SOP-Based Power
Distribution Network Integrated With Electric Vehicles. IEEE Trans. Ind. Inform. 2022, 18, 8213–8224. [CrossRef]
17.
Diao, H.; Li, P.; Tu, C.; Che, L. Optimal Co-Planning of Multi-Port Soft Open Points and Energy Storage Systems for Improving
Hosting Capacity and Operation Efficiency in Distribution Networks. IEEE Trans. Power Deliv. 2025, 40, 459–471. [CrossRef]
18.
Huang, Z.; Xu, Y.; Chen, L.; Ye, X. Coordinated Planning Method Considering Flexible Resources of Active Distribution Network
and Soft Open Point Integrated with Energy Storage System. IET Gener. Transm. Distrib. 2023, 17, 5273–5285. [CrossRef]
19.
Yang, X.; Zhou, Z.; Zhang, Y.; Liu, J.; Wen, J.; Wu, Q.; Cheng, S.-J. Resilience-Oriented Co-Deployment of Remote- Controlled
Switches and Soft Open Points in Distribution Networks. IEEE Trans. Power Syst. 2023, 38, 1350–1365. [CrossRef]
20.
Overbye, T.; Cheng, X.; Sun, Y. A comparison of the AC and DC power flow models for LMP calculations. In Proceedings of the
37th Annual Hawaii International Conference on System Sciences; IEEE: New York, NY, USA, 2004.
21.
Liu, D.; Liu, L.; Cheng, H.; Zhang, S.; Xin, J. An Extended DC Power Flow Model Considering Voltage Magnitude. J. Mod. Power
Syst. Clean Energy 2021, 9, 679–683. [CrossRef]
22.
Li, Q.; Zhao, N. General Power Flow Calculation for Multi-Terminal HVDC System Based on Sensitivity Analysis and Extended
AC Grid. IEEE Trans. Sustain. Energy 2022, 13, 1886–1899. [CrossRef]
23.
Ji, H.; Wang, C.; Li, P.; Ding, F.; Wu, J. Robust Operation of Soft Open Points in Active Distribution Networks With High
Penetration of Photovoltaic Integration. IEEE Trans. Sustain. Energy 2019, 10, 280–289. [CrossRef]
24.
You, R.; Lu, X. Voltage Unbalance Compensation in Distribution Feeders Using Soft Open Points. J. Mod. Power Syst. Clean Energy
2022, 10, 1000–1008. [CrossRef]
25.
Çiçek, A. A novel resilience-oriented energy management strategy for hydrogen-based green buildings. J. Clean. Prod. 2024,
470, 143297. [CrossRef]
Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
https://doi.org/10.3390/pr14061013
