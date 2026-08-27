<!--
source: D5_规划与灵活资源/Bi-level coordinated expansion planning of high-PV-penetration active.pdf
sha256: f65ee7213b4a74bafa24018abb232ba0047afeec982dd57a58eaa86b8c1900d8
method: pymupdf
pages: 16
-->

<!-- page 1/16 -->

Bi-level coordinated expansion planning of high-PV-penetration active 
distribution networks incorporating multiple flexible resources considering 
WGAN-GP-based uncertainty generation
Jianjing Li a, Fan Li a, Kai Sun b, Bo Sun a,*
a School of Control Science and Engineering, Shandong University, Jingshi Road 17923, Jinan, 250061, China
b Department of Electrical Engineering, State Key Laboratory of Power System Operation and Control, Tsinghua University, Beijing, 100084, China
A R T I C L E  I N F O
Index Terms:
Active distribution network
Expansion planning
High-penetration photovoltaics
Uncertainty
WGAN-GP
A B S T R A C T
Integrating high-penetration random photovoltaics (PVs) into the active distribution network (ADN) often causes 
overvoltage issues, which can even trigger ADN failures. To accommodate high-penetration PVs integration 
while maintaining economic efficiency and flexibility of ADN, a bi-level collaborative expansion planning model 
considering uncertainty generation and reduction is proposed in this paper. Based on described uncertainty 
scenarios of PV and load obtained by proposed Wasserstein Generative Adversarial Network with Gradient 
Penalty (WGAN-GP) and K-means method, the upper level firstly configures soft open points to adjust the ADN 
topology, then optimizes the siting and sizing of PVs, electric vehicle charging stations, energy storage systems, 
and active management resources (on-load tap changers, and static var compensators) with minimum investment 
cost. Lower level uses multi-objective mixed-integer second-order cone programming (MISOCP) model with 
network loss, PV curtailment and voltage deviation of different attributes to optimize ADN scheduling. To solve 
this planning model, a hybrid algorithm that integrates an adaptive particle swarm optimization algorithm with 
SOCP is proposed, employing the technique for order preference by similarity to an ideal solution (TOPSIS) to 
address the multi-objective issue. Finally, the presented model was tested in the actual rural 41-bus and urban 
40-bus ADN of Gansu, China, demonstrating that total costs decreased by 14.4 % and 12.5 % respectively 
compared to plans without active management resources.
Nomenclature
Abbreviation
ADN
Active distribution network
DNO
Distribution network operator
ESS
Energy storage systems
EVCS
Electric vehicle charging station
MISOCP
mixed-integer second-order cone programming
OLTC
On-load tap changer
PV
Photovoltaic
RES
Renewable energy source
SOCR
Second-order cone relaxation
SOCP
Second-order cone programming
SOP
Soft open point
SVC
Static var compensator
Sets and indices
(i, j)/Ω
Index/set of MV buses
(continued on next column)
(continued)
h/ Ωi
h
Index/set of LV buses and relevant MV/LV 
transformer units connected to MV bus i
k
Index of sample variations of EV charging stations
l/ Ωij
l
Index/set of lines where i is the sending bus and j is 
the receiving bus
s/S
Index/set of uncertain scenarios
t/T
Index/set of hours
Parameters
ASOP
i
Loss coefficient of SOP at node i
Bl
Shunt susceptance of line l
CADN
ADN investment construction cost
CPV, CEVCS, CESS
CSOP, COLTC, CSVC
Investment construction cost of PV, ESS, EVCS, SOP, 
OLTC and SVC
cPV
cons, cEVCS
cons , cESS
cons
cSOP
cons, cOLTC
cons , cSVC
cons
Installation costs of unit capacity of PV, ESS, EVCS, 
SOP, OLTC and SVC
Ca
opt
Annual operating cost of distribution network
(continued on next page)
* Corresponding author.
E-mail address: sunbo@sdu.edu.cn (B. Sun). 
Contents lists available at ScienceDirect
Energy
journal homepage: www.elsevier.com/locate/energy
https://doi.org/10.1016/j.energy.2025.136685
Received 27 June 2024; Received in revised form 18 April 2025; Accepted 19 May 2025  
Energy 330 (2025) 136685 
Available online 21 May 2025 
0360-5442/© 2025 Published by Elsevier Ltd.



<!-- page 2/16 -->

(continued)
Ca
b,Ca
p,Ca
m
Annual cost of buying and selling electricity, PV 
curtailment and maintenance cost of ADN operation
cb, ce
Unit price of purchasing and selling electricity to the 
superior distribution network
cp
Unit cost of PV curtailment
E
Unit energy capacity of ESS
EESS
ini
Initial energy state of ESS unit
gj, bj
Conductance and susceptance of bus j
la
loss
Annual network loss of ADN
̃Imin,̃Imax
Minimum and maximum limited current square
ma
pv, ma
EVCS, ma
ESS
ma
SOP, ma
OLTC, ma
SVC
Unit annual maintenance cost of PV, ESS, EVCS, SOP, 
OLTC and SVC
PPV rated
Rated power of unit PV generation
PEVCS rated
Rated power of unit EVCS
QSVC rated
Rated power of unit SVC
SSOP rated
Rated power of unit SOP
PESS
Unit charging or discharging power upper limit of 
ESS
Pp load,MV
i
Peak of load demand directly connected to MV bus i
Pp load,LV
h,i
Peak of load demand at the LV bus h of MV bus i
rl
Resistance of line l
∂min
i
,∂max
i
Minimum and maximum the square of OLTC 
adjustable ratio
Sl
Flow limit of branch l
TRlim
h,i
Rated power of MV/LV transformer between MV bus 
i and LV bus h
Vd
Total voltage deviation of distribution network
Vmean
The average node voltage
̃Vmin, ̃Vmax
Minimum and maximum limited voltage square for 
MV buses
xl
Reactance of line l
y
Service life of module installed to network
γs
Total days of scenario s throughout the year
aPV
s,t
Scenarios of PV generation during uncertainty 
description
aEVCS
s,k,t
The k-type sample of EV charging trend in period t of 
scenario s
ρ
Maximum PV integration ratio permitted for 
transformer
ζ
Minimum photovoltaic penetration for distribution 
network issued by management
λch, λdis
ESS charging and discharging efficiency
ε
Discharge depth of ESS units
Decision variables
ΩPV, ΩESS,ΩEVCS, ΩOLTC, 
ΩSVC, ΩSOP
Candidate Set of PV, ESS, EVCS, OLTC, SVC 
installation notes and SOP construction
Ωi,PV
h
Set of candidate PV installation notes of LV bus h 
connected to MV bus i
Is,l,t,̃Is,l,t
Current and square current of line l in period t of 
scenario s
nMV,PV,i,nLV,PV,i,h
Number of reference PV panels installed within MV 
bus i or LV bus h of MV bus i
nEVCS,k,h,i,nESS,h,i
Number of EV charging station and ESS installed 
within LV bus h of MV bus i for sample EV load k
nSVC,i,nSOP,i
Number of reference SVC and SOP installed within 
MV bus i
EESS
s,h,i,t,EESS
s,h,i,t−1
State of energy of ESS units connected to LV bus h of 
MV bus i in period t or period t-1 of scenario s
Pcap,PV
Total PV capacity connected to distribution network
Pcap,PV,MV
i
,Pcap,PV,LV
h,i
PV capacity directly connected to MV bus i and LV 
bus h of MV bus i
Pcap,EVCS
i
, Pcap,ESS
i
Qcap,SVC
i
, Pcap,OLTC
i
, SSOP
i
Total EVCS, ESS, SVC, OLTC and SOP capacity 
integrated to the bus i
Ps,l,t,Qs,l,t
Active, reactive power flow at receiving end of line l 
in period t of scenario s
PSub
s,t ,QSub
s,t
Active transactive power through substation node in 
scenario s and hour t
PSOP
s,i,t ,QSOP
s,i,t
Active/reactive power generated by SOP node i in 
scenario s and hour t
PSOP,loss
s,l,t
SOP transmission loss of line l in scenario s and hour t
PPV,MV
s,i,t
PV power available at the MV bus i in period t of 
scenario s
PG
s,j,t,QG
s,j,t
Injected active, reactive power at bus j in period t of 
scenario s and hour t
(continued on next column)
(continued)
PL
s,j,t,QL
s,j,t
Received active, reactive power at bus j in period t of 
scenario s and hour t
PPV,LV
s,h,i,t
PV power available at the LV bus h in period t of 
scenario s
PESS,ch
s,h,i,t ,PESS,dis
s,h,i,t
ESS charging and discharging power at the LV bus h 
of MV bus i in period t of scenario s
PPV,LV
s,h,i,t
Total PV power available at the LV bus h of MV bus i 
in period t of scenario s
PL,MV
s,h,i,t
Load demand at the bus i in period t of scenario s
PL,LVother
s,h,i,t
Other load at the LV bus h of MV bus i in period t of 
scenario s
PEVCS,LV
s,h,i,t
Total EV charging power by LV bus h to the MV bus i 
in period t of scenario s
Ps,h,i,t
LV+,Ps,h,i,t
LV−
Total power injected/drawn by LV bus to MV bus i in 
period t of scenario s
Smax
p
,Smax
q
Upper limits of active and reactive power exchanged 
with the upstream grid
QSVC
s,i,t
Reactive power compensation of SVC at the bus i in 
period t of scenario s
∂s,i,t
Discrete value variable for the ratio of the secondary 
side to the primary side of OLTC
usub,s,t
Binary variable for transactive power through 
substation node of hour t in scenario s. Power 
obtained from the superior network is 1, otherwise 0
uESS
s,h,i,t
Binary variable for ESS model at the bus i of hour t in 
scenario s. 1 if ESS model is charging, otherwise 0.
uOLTC
s,i,t
Binary variable for OLTC action of the node i at 
period t in scenario s. 1 if the OLTC increases the 
voltage, otherwise 0.
Vs,i,t, ̃Vs,j,t
Voltage magnitude and voltage square of the node i 
at period t in scenario s
uLV
s,h,i,t
Binary variable of logical constraints for the power 
decomposition of LV bus h
1. Introduction
Vigorously developing renewable energy source (RES) and 
increasing the installation capacity of RES are key to China’s energy 
transition and hold significant strategic importance. A large-scale inte­
gration of distributed photovoltaics (PVs) into active distribution net­
works (ADNs) is an inevitable trend. In the process of advancing 
“County-Wide Photovoltaics” projects in China, to meet the demands of 
high photovoltaic penetration, it is often necessary to rent residential 
rooftops and collaborate with distribution network operators (DNOs) to 
construct PVs. The interest generated from selling electricity is then used 
to subsidize the residents. Moreover, new loads such as electric vehicle 
charging stations (EVCSs) has been integrated into ADNs. Their 
continuous integrations on both sides of source and load increase un­
certainties throughout the ADN by changing the voltage distribution and 
power flow direction [1–3], which greatly reduces stability and creates 
significant challenges for ADN expansion planning (ADNEP) [4,5], even 
the ADN cannot accommodate high-penetration PV integration. DNOs 
urgently need a long-term planning strategy for improving network 
flexibility while maintaining economic efficiency [6].
DNOs have considered integrating energy storage systems (ESSs), on- 
load tap changers (OLTC), and static var compensators (SVCs) to 
enhance the operational flexibility of ADNs [7]. On the demand side, 
demand response (DR) is a mean of mitigating the uncertainty and 
intermittency of renewable generation [8]. Especially with the 
increasing demand for EVCSs, providing guidance for users with 
charging needs helps with the large-scale integration of PVs into an 
ADN. Planning investment in PVs and integrating new technologies such 
as ESSs and EVCS to comply with policies set by higher levels of gov­
ernment to encourage PV penetration is a widespread problem [9].
In recent years, with the assistance of these active management re­
sources, a great variety of studies have focused on extensive integrations 
of RES in ADN. Reference [10] considers a practical situation that the 
siting choice of individual RES owners could be conflict with systems 
operation, a trilevel ESS planning formulation with “min-max” risk 
constraint is developed. Reference [11,12] research the co-planning of 
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
2



<!-- page 3/16 -->

renewable generation and storage resources for the ADN to determine 
their construction time, siting location, and capacity sizing. A 
chance-constrained information gap decision model is proposed to 
handle multi-scale and multi-type uncertainties in ADN planning [13]. 
In addition to the co-configuration of RES and ESS, the optimal opera­
tion of substations’ on-load tap changers (OLTC) and network reconfi­
guration with radial and closed-loop operation topologies are also 
adapted to maximize the RES hosting capacity of the network [14,15]. 
Meanwhile, the relevance of DR in the expansion planning modeling is 
stressed in Ref. [16], and a multi-stage model is proposed to accurately 
include DR in the joint RES expansion planning problem of ADN.
Besides enhancing the capacity of RES, some researches integrate 
ADN with EVs. Adoption of EVs expands the application range of RES, 
but the uncertainty in RES increases the operational burden of ADN. A 
coordinated optimal planning model for EVCS and RES is proposed to 
coordinate several planning objectives, including system reliability and 
investment cost, power loss, and voltage stability [17]. Reference [18] 
incorporates various investment options, including distributed genera­
tion and network reinforcement, and proposes an integrated planning 
framework to effectively accommodate EVs in ADN. Considering the 
incorporation of reliability into ADN emphatically, reference [19] pro­
poses an enhanced alternative mixed-integer linear programming model 
for multistage reliability-constrained ADNP, which overcomes low 
computational efficiency or oversimplification of heuristic approaches. 
Unlike the aforementioned studies that consider only static values for 
generation and load requirements, reference [9] simultaneously con­
siders time-varying profiles of RES production, load, and EVCS demand 
to address temporal mismatches between them. Based on soft open point 
(SOP), the voltage control can be applied to mitigate operation costs and 
voltage violations of RES integrated ADN [20]. And the dispatching of 
SOP coordinated with ESS has been demonstrated in the literature [21] 
to enhance the system’s flexibility and the maximum PV hosting ca­
pacity. Lastly, a comprehensive literature study considering the expan­
sion planning of ADN is provided in Ref. [22].
The representative uncertainty description of RES generation and 
demand is extremely important for ADN planning, and its accuracy af­
fects the adaptability of the plan. Some research neglects or over­
simplifies the RES uncertainties and load variability [23,24], while 
many researches focus on robust optimization and stochastic optimiza­
tion in order to deal with the random variables introduced by these 
uncertainties [25,26]. Robust optimization adjusts the uncertainty in­
terval of new energy and load without establishing a specific probability 
distribution. To deal with the uncertainties of PV locations and capac­
ities, the proposed allocation problem is formulated as an adaptive 
robust optimization model with integer recourse variables [27], but the 
optimization result is too conservative, especially for the generation and 
load outputs with periodic characteristics.
Another widely used stochastic optimization usually assumes that 
random variables obey the given probability distribution, and trans­
forms uncertain problems into deterministic ones by sampling and other 
methods [28]. Specifically, optimal planning of EVCS and RES is pre­
sented in Ref. [29] using k-means clustering technique to consider the 
uncertainties related to renewable power sources and EV demand. 
Furthermore, reference [30] uses heuristic moment matching method to 
reduce the complexity of high-dimensional discrete variables. Mean­
while, the Monte Carlo Sampling method is applied in Ref. [31] to 
construct the joint probability distribution scenarios for stochastic var­
iables. However, its computational cost is greatly increased to achieve 
satisfactory approximate accuracy of probability distribution. Many 
studies use adversarial learning to generate scenes in a model-free way 
[32]. builds a Wasserstein generative adversarial network (GAN) for 
wind scenario generation, which accurately captures the uncertainty 
features [33]. proposes a generative model integrated with federated 
learning and GAN, and demonstrates the effectiveness of the generative 
model in terms of spatiotemporal correlation.
At present, a majority of studies present ADN planning models 
considering different flexible resources and optimization methods. 
Based on the literature survey, the major research gaps can be summa­
rized as follows: 1) Some studies, such as references [10–14,21,25,34,
35], only consider the coordinated planning of PV, ESS, and SOP to 
increase the integration capacity. The demand-side charging guidance 
and ADN active managements are not discussed sufficiently, which can 
enhance the carrying capacity by improving voltage quality and power 
flow distribution. 2) Although references [7], [9], [36] and [49] 
comprehensively consider various flexible resource characteristics and 
their coordinated configurations, their optimization processes focus 
solely on economic objectives without accounting for ADN security in­
dexes with distinct dimensions. Furthermore, the solvers struggle to 
handle the large number of discrete variables related to integration sites, 
making it challenging to provide DSOs with more comprehensive and 
better planning solutions that accommodate diverse preferences. The 
traditional heuristic algorithms, such as references [34,35,37], have 
simple and clear solution ideas, but generally take long convergence 
times and tend to fall into local optima. 3) In ADN planning studies 
considering the influence of high PV integration, references [7–9,18–20,
34,35,37–39] either neglect uncertainty impacts or remain confined to 
explicit modeling of complex features, with an over-reliance on the 
precise probability distributions. Reference [32,33] provide the adver­
sarial learning methods. They are prone to gradient vanishing or ex­
ploding issues, ensuring reliable ADN operation is difficult when the 
actual scenario deviates from the preset conditions.
To highlight the contributions of this paper, the features of the 
Table 1 
Summary of previous studies in distribution network planning.
Reference
Multiple flexible resources with PV
Multi-objective
Uncertainty
Optimization methodology
ESS
EVCS
SVC
OLTC
SOP
Ec.
Se.
[7]
✓
​
✓
✓
✓
✓
​
​
MISOCP by CPLEX solver
[9]
✓
✓
​
​
​
✓
​
​
SOCP by CPLEX solver
[20]
✓
✓
​
​
✓
✓
​
​
MISOCP by solver
[34]
✓
​
​
​
​
✓
​
PDF sequences
IBPSO algorithm
[35]
✓
​
​
​
✓
✓
✓
​
Particle swarm optimizer
[36]
✓
✓
✓
​
​
✓
​
WGAN-GP
MISOCP by CPLEX solver
[21]
✓
​
​
​
✓
✓
​
Interval robust set
MICP and by CCG and solver
[25]
✓
​
​
​
​
✓
​
FDA
Robust-based IGDT
[31]
✓
​
✓
​
​
✓
​
Monte Carlo
Markov decision learning
[37]
✓
​
✓
​
​
✓
✓
Kantorovich distance
Genetic algorithm
[38]
✓
✓
​
​
✓
✓
​
​
MILP by CPLEX solver
[39]
✓
✓
✓
✓
​
✓
​
​
Decomposed MILP and MISOCP subproblems
[40]
✓
​
​
​
✓
​
​
LHS
Robust optimization
This paper
✓
✓
✓
✓
✓
✓
✓
WGAN-GP
APSO, MISOCP with TOPSIS
Acronyms: CCG: Column and constraint generation, Ec.: Economic index, FDA: Flow direction algorithm, IBPSO: Improved binary particle swarm optimization, IGDT: 
Information gap decision theory, LHS: Latin Hypercube Sampling, MILP: Mixed integer linear programming, PDF: Probability density function, Se.: Security index.
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
3



<!-- page 4/16 -->

proposed model for ADN planning incorporating flexible resources 
compared to the previous works are summarized in Table 1. To fill the 
above research gaps, a bi-level multi-objective coordinated expansion 
planning method for high-penetration PV integration is proposed. The 
novelty and main contributions of this paper mainly lies in three parts. 
1) This paper cooperatively configures EVCSs with orderly charging 
guidance, ESSs and active management resources (SOPs, SVCs, and 
OLTC), aiming to solve the problem of high-penetration PV inte­
gration while minimizing cost and keeping flexibility for DNO. The 
proposed method based on described uncertainties simultaneously 
determines the siting, sizing, and scheduling of heterogeneous flex­
ible resources in the ADN.
2) A novel bi-level collaborative planning model considering multiple 
objectives with different attributes such as investment cost, voltage 
deviation and network loss is proposed. The original non-convex 
problem is transformed into a solvable mixed-integer second-order 
cone programming (MISOCP) problem by second-order cone relax­
ation. And a hybrid algorithm combining adaptive particle swarm 
optimization (APSO) and SOCP with TOPSIS is proposed to address 
this problem.
3) An uncertainty description method based on WGAN-GP and K-means 
for PV generation and load demand is proposed. The Wasserstein loss 
function and gradient penalty are introduced on traditional GAN 
model to solve problem of gradient disappearing or explosion, 
avoiding model assumptions or prior distributions.
with information entropy-based TOPSIS is proposed to solve the 
mixed-integer second-order cone programming (MISOCP) problem.
The remainder of the paper is organized as follows. Section 2 pre­
sents proposed planning model. In Section 3, a detailed method of un­
certainty description is introduced. Section 4 presents the case study to 
evaluate the performance of proposed model. Finally, the conclusions 
are drawn in Section 5.
2. Modeling and problem formulation
The objective of this study is to facilitate PV integration into an ADN 
by minimizing the costs for the DNO while maintaining the security and 
flexibility of the ADN. To address the problem of the lack of PV and load 
actual scenarios required for ADN planning, an uncertainty description 
method based on Wasserstein Generative Adversarial Network with 
Gradient Penalty (WGAN-GP) and k-means is used to generate uncertain 
scenarios and reduce them to approximate reality. As shown in Fig. 1, 
the proposed bi-level ADNEP model has two levels. The upper level is 
focused on optimizing the siting and sizing of flexible resources (e.g., 
PVs, ESSs, EVCSs, SOPs, OLTCs and SVCs). Based on location and 
capacity results of upper-level selection, the lower level is focused on 
optimizing ADN operation and guiding users to charge EVs orderly. The 
mixed-integer second-order cone programming (MISOCP) problem is 
solved through adaptive particle swarm optimization with information 
entropy-based TOPSIS and SOCP method in MATLAB.
2.1. Upper-level problem formulation
The optimization objective of the upper level is to minimize the total 
investment cost of flexible resources, as introduced in (1). The decision 
variables include site and capacity selection. The total investment cost 
comprises the installation costs of the PV, EVCS, ESS, SOP, OLTC, and 
SVC, which are formulated in Equations (2)–(7). 
min CADN = CPV + CEVCS + CESS + CSOP + COLTC + CSVC
(1) 
CPV =
∑
i∈ΩPV
R ⋅cPV
cons ⋅
(
Pcap,PV,MV
i
+ Pcap,PV,LV
h,i
)
(2) 
CEVCS =
∑
i∈ΩEVCS
R⋅cEVCS
cons ⋅Pcap,EVCS
i
(3) 
CESS =
∑
i∈ΩESS
R⋅cESS
cons⋅Pcap,ESS
i
(4) 
CSOP =
∑
i∈ΩSVC
R⋅cSOP
cons⋅Scap,SOP
i
(5) 
COLTC =
∑
i∈ΩOLTC
R⋅cOLTC
cons ⋅Pcap,OLTC
i
(6) 
CSVC =
∑
i∈ΩSVC
R⋅cSVC
cons⋅Qcap,SVC
i
(7) 
where R is the capital recovery factor and is derived from the discount 
rate r, and service life ∂, of Equation (8). 
R = r⋅(1 + r)∂
(1 + r)∂−1
(8) 
2.2. Lower-level problem formulation
The multiple objectives of the lower level are to minimize the annual 
operational cost and voltage deviation as demonstrated in (9) and (10). 
Including the voltage deviation of nΩ nodes as another optimization 
objective should help ensure the security of the ADN in different PV and 
load scenarios.
The lower-level multiple objectives include annual operational costs, 
network loss, and voltage deviation. Due to inconsistent dimensions, 
they are described separately. The annual operational cost includes 
power purchased from the superior network, PV curtailment, and 
maintenance costs, which are calculated by Equation (9). The network 
losses and voltage deviation are calculated by Equations (10) and (11). 
min Ca
opt = Ca
b + Ca
p + Ca
m
(9) 
min Vd =
∑
s∈S
∑
T
t=1
∑
i∈Ω
⃒⃒Vs,i,t −Vmean
⃒⃒
S⋅T⋅nΩ
(10) 
min la
loss =
∑
s∈S
∑
T
t=1
⎡
⎢⎣
∑
l∈Ωij
l
(
rl ⋅Is,l,t
2)
⎤
⎥⎦△t
(11) 
Fig. 1. Framework of the proposed bi-level ADN expansion planning model.
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
4



<!-- page 5/16 -->

⎧
⎪
⎪
⎪
⎪
⎪
⎪
⎪
⎪
⎪
⎪
⎪
⎪
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
⎪
⎪
⎪
⎪
⎪
⎪
⎪
⎪
⎪
⎪
⎪
⎪
⎩
Ca
b =
∑
s∈S
∑
T
t=1
[
PSub
s,t ⋅
( (
1 −usub,s,t
)
⋅ce + cb⋅usub,s,t
)]
Ca
p = cp⋅
∑
s∈S
∑
T
t=1
∑
i∈ΩPV
⎡
⎢⎣
γs⋅
(
Pcap,PV,MV
i
⋅aPV
s,t −PPV,MV
s,i,t
)
+
(
Pcap,PV,LV
i
⋅aPV
s,t −PPV,LV
s,i,t
)
⎤
⎥⎦
Ca
m = ma
pv⋅Pcap,PV +
∑
i∈ΩEVCS
ma
EVCS⋅Pcap,EVCS
i
+
∑
i∈ΩSOP
ma
SOP⋅Scap,SOP
i
∑
i∈ΩESS
ma
ESS⋅Pcap,ESS
i
+
∑
i∈ΩOLTC
ma
OLTC⋅Pcap,OLTC
i
+
∑
i∈ΩSVC
ma
SVC⋅Qcap,SVC
i
(12) 
2.3. Power flow constraints
In this study, the conic form of the power flow equation was adopted 
because it can realize a more precise model than the DC power flow 
model and represents the power flow more simply but reasonably than 
the full AC power flow model. Fig. 2 presents a conceptual illustration of 
the power flow and the integration sites of flexible resources on both the 
MV and LV buses. According to Ref. [41], the general formulation of the 
branch flow model-based optimal power flow (BFM-OPF) is employed in 
this paper. The following constraints (13)-(14) ensure the active and 
reactive power balances at each MV bus in different scenarios. 
PG
s,j,t −PL
s,j,t =
∑
l∈Ωjk
l
Ps,l,t −
∑
l∈Ωij
l
(
Ps,l,t −Is,l,t
2rl
)
+ gjVs,j,t
2,
∀j ∈Ω, ∀s ∈S, ∀t ∈T
(13) 
QG
s,j,t −QL
s,j,t =
∑
l∈Ωjk
l
Qs,l,t −
∑
l∈Ωij
l
(
Qs,l,t −Is,l,t
2xl
)
+ bjVs,j,t
2,
∀j ∈Ω, ∀s ∈S, ∀t ∈T
(14) 
The available power of each MV bus is decomposed into the injected 
power of the substation, PV power directly integrated into the MV bus, 
and excess power injected from LV buses as in Equation (15): 
PG
s,i,t = PSub
s,t + PPV,MV
s,i,t
+ PSOP
s,i,t +
∑
h∈Ωi
h
Ps,h,i,t
LV+,
∀h ∈Ωi
h, ∀i ∈Ω, ∀s ∈S, ∀t ∈T
(15) 
QG
s,i,t = QSub
s,t + QSOP
s,i,t + QSVC
s,i,t , ∀h ∈Ωi
h, ∀i ∈Ω, ∀s ∈S, ∀t ∈T
(16) 
The following constraint (17) emphasizes that the system load in­
cludes inelastic demand and the power deficiency of LV buses. 
PL
s,i,t = PL,MV
s,i,t
+
∑
h∈Ωi
h
Ps,h,i,t
LV−, ∀h ∈Ωi
h, ∀i ∈Ω, ∀s ∈S, ∀t ∈T
(17) 
The constraint of node voltage and line current can be expressed by 
the following Equations (18) and (19). 
Vs,j,t
2 = Vs,i,t
2 −2
(
Ps,l,trl + Qs,l,trl
)
+ Is,l,t
2(
rl
2 + xl
2)
,
∀l ∈Ωij
l , ∀i, j ∈Ω, ∀s ∈S, ∀t ∈T
(18) 
Is,l,t
2 = Ps,l,t
2 + Qs,l,t
2
Vs,j,t
2
, ∀l ∈Ωij
l , ∀j ∈Ω, ∀s ∈S, ∀t ∈T
(19) 
The original BFM-OPF is a non-convex nonlinear programming 
model. Let ̃Vs,i,t = V2
s,i,t, ̃Is,l,t = I2
s,l,t. Equations (13), (14) and (18) are 
transformed to the following Equations: 
PG
s,j,t −PL
s,j,t =
∑
l∈Ωjk
l
Ps,l,t −
∑
l∈Ωij
l
(
Ps,l,t −̃Is,l,trl
)
+ gj̃Vs,j,t,
∀j ∈Ω, ∀s ∈S, ∀t ∈T
(20) 
QG
s,j,t −QL
s,j,t =
∑
l∈Ωjk
l
Qs,l,t −
∑
l∈Ωij
l
(
Qs,l,t −̃Is,l,txl
)
+ bj̃Vs,j,t,
∀j ∈Ω, ∀s ∈S, ∀t ∈T
(21) 
̃Vs,j,t = ̃Vs,i,t −2
(
Ps,l,trl + Qs,l,trl
)
+̃Is,l,t
(
rl
2 + xl
2)
,
∀l ∈Ωij
l , ∀i, j ∈Ω, ∀s ∈S, ∀t ∈T
(22) 
The effectiveness of the second-order cone relaxation (SOCR) has 
been thoroughly studied in Ref. [42], which proves that for most ADN 
structures, SOCR is strictly accurate when the objective function strictly 
increasing. This paper analyzes this relaxation error in case study to 
demonstrate the precision of SOCR. Equation (19) is transformed to 
Equation (23) by SOCR. 
⃦⃦⃦⃦⃦⃦
2Ps,l,t
2Qs,l,t
̃Is,l,t −
̃Vs,j,t
⃦⃦⃦⃦⃦⃦
2
≤̃Is,l,t + ̃Vs,j,t, ∀l ∈Ωij
l , ∀j ∈Ω, ∀s ∈S, ∀t ∈T
(23) 
In addition, the following constraint ensures that the node voltage and 
line current remain within the allowable upper and lower limits, as 
shown in Equation (24) and (25). 
̃Vmin ≤̃Vs,i,t ≤̃Vmax, ∀i ∈Ω, ∀s ∈S, ∀t ∈T
(24) 
̃Imin ≤̃Is,l,t ≤̃Imax, ∀l ∈Ωij
l , ∀s ∈S, ∀t ∈T
(25) 
The following Equations (26) and (27) ensure a power balance be­
tween the LV bus and MV/LV power transmission. The bidirectional 
transmission power cannot exceed the rated power of the transformer. 
PPV,LV
s,h,i,t + PESS,dis
s,h,i,t −PL,LVother
s,h,i,t
−PEVCS,LV
s,h,i,t
−PESS,ch
s,h,i,t = Ps,h,i,t
LV+ −Ps,h,i,t
LV−,
∀h ∈Ωi
h, ∀i ∈Ω, ∀s ∈S, ∀t ∈T
(26) 
Ps,h,i,t
LV+ ≤TRlim
h,i ⋅uLV
s,h,i,t, Ps,h,i,t
LV−≤TRlim
h,i ⋅
(
1 −uLV
s,h,i,t
)
∀h ∈Ωi
h, ∀i ∈Ω, ∀s ∈S, ∀t ∈T
(27) 
2.4. Constraints of multiple flexible resources
In this paper, flexible resources are distributed across the network, 
load, and energy storage sides according to their physical locations. On 
the network side, the power flow paths can be flexibly adjusted by 
Fig. 2. Integration of flexible resources into an ADN.
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
5



<!-- page 6/16 -->

configuring soft open points (SOPs). The on-load tap changer (OLTC) 
regulates output voltage, and the static var compensators (SVCs) provide 
rapid response to voltage changes and adjust reactive power. On the 
load and energy storage sides, the electric vehicle charging stations 
(EVCSs) and energy storage systems (ESSs) can smooth out active power 
fluctuations respectively by guiding orderly charging and balancing 
time-based differences in power consumption, while simultaneously 
reducing system operating costs. The aforementioned flexibility re­
sources play crucial roles in different performance of ADN. ESS and 
EVCS are primarily focused on mitigating fluctuations in power levels, 
while SVC, OLTC, and SOP are concentrated on reactive power voltage 
control and power flow regulation.
In the proposed multi-objective planning model, the location, ca­
pacity, and operational strategies of each resource are optimized from 
the DNO’s perspective and input into the optimization model. By setting 
different objective preferences, the model can reflect the role and 
configuration of flexible resources with different characteristics. 
Through their coordinated operation, the total stability and flexibility of 
ADN can be effectively improved to accommodate the high-proportion 
PV integration.
To simplify the proposed bi-level ADN planning model, the influence 
of meteorological and geographical differences on the ADN is ignored. 
The limit of PV generation is expressed in Equations (28) and (29). 
0 ≤PPV,MV
s,i,t
≤aPV
s,t ⋅Pcap,PV,MV
i
, ∀i ∈ΩPV, ∀s ∈S, ∀t ∈T
(28) 
0 ≤PPV,LV
s,h,i,t ≤aPV
s,t ⋅Pcap,PV,LV
h,i
, ∀h ∈Ωi,PV
h
, ∀i ∈ΩPV, ∀s ∈S, ∀t ∈T
(29) 
The integrated PV capacity of the ADN is determined by the total 
installed PV capacity from the MV and LV buses as in Equations (30)– 
(32). 
Pcap,PV,MV
i
= PPV rated⋅nMV,PV,i, i ∈ΩPV
(30) 
Pcap,PV,LV
h,i
= PPV rated⋅nLV,PV,i,h, h ∈Ωi,PV
h
(31) 
Pcap,PV =
∑
i∈ΩPV
⎛
⎜
⎝Pcap,PV,MV
i
+
∑
h∈Ωi,PV
h
Pcap,PV,LV
h,i
⎞
⎟
⎠, i ∈ΩPV, h ∈Ωi,PV
h
(32) 
PV systems with different capacities were assumed to have the same 
trend of generation for a given scenario. It is ensured that the reverse 
power to the upper network is less than the capacity of transformer in 
Equation (33). 
Pcap,PV,LV
h,i
≤ρ⋅TRlim
h,i , i ∈ΩPV, h ∈Ωi,PV
h
(33) 
For the ADN planning problem oriented to improve PV penetration, 
it is necessary to ensure that the requirement issued by the management 
department of grid needs to be satisfied. The following constraint ex­
presses penetration as the ratio of the total PV integration to the peak 
load. 
ζ ≥
Pcap,PV
∑
i∈Ω
Pp load,MV
i
+ ∑
h∈Ωi
h
Pp load,LV
h,i
× 100%
(34) 
The SOP can control active and reactive power of ADN to balance the 
load across different feeders or locations, preventing line overload. A 
flexible interconnection model based on back-to-back soft open point 
(SOP) is adopted to flexibly control the active power transmitted be­
tween two feeders, and its operation meet the following Equations (35) 
and (36). 
PSOP
s,i,t + PSOP
s,j,t + PSOP,loss
s,l,t
= 0,
∀i, j ∈ΩSOP, ∀l ∈Ωij
l , ∀s ∈S, ∀t ∈T
(35) 
PSOP
s,l,t = ASOP
i
⃒⃒⃒PSOP
s,i,t
⃒⃒⃒+ ASOP
j
⃒⃒⃒PSOP
s,j,t
⃒⃒⃒,
∀i, j ∈ΩSOP, ∀l ∈Ωij
l , ∀s ∈S, ∀t ∈T
(36) 
SOP capacity constraints are expressed in Equations (37)–(39). 
̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅
(
PSOP
s,i,t
)2
+
(
QSOP
s,i,t
)2
√
≤Scap,SOP
i
, ∀i ∈ΩSOP, ∀s ∈S, ∀t ∈T
(37) 
̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅
(
PSOP
s,j,t
)2
+
(
QSOP
s,j,t
)2
√
≤Scap,SOP
j
, ∀j ∈ΩSOP, ∀s ∈S, ∀t ∈T
(38) 
Scap,SOP
i
= nsop,i⋅SSOP rated, ∀i ∈ΩSOP
(39) 
The load of EV charging on each LV bus h can be derived in a similar 
manner. The same type of EVCS was assumed throughout the ADN. 
Considering the different charging habits of EV users and the different 
deployment scenarios in working and residential districts, the EV 
charging load of each node is determined by the installation number of 
LV bus h. It can flexibly respond to DNO guidance, and the adjustment 
interval of charging power is set as ±20 %. 
PEVCS
h,i,t = aEVCS
s,k,t ⋅
∑
k∈Ωi
k
nEVCS,k,h,i, ∀i ∈ΩEVCS, ∀s ∈S, ∀t ∈T
(40) 
Pcap,EVCS
i
= PEVCS rated⋅
∑
h∈ΩEVCS
∑
k∈Ωi
k
nEVCS,k,h,i
(41) 
ESS is primarily used to balance grid load fluctuations, support the 
PV integration, and provide power balancing services. The power 
charging and discharging decisions are constrained by Equations (42) 
and (43), respectively. The ESS state is updated in time steps according 
to the charging or discharging action, and it has upper and lower limits 
in Equations (44)–(47). 
0 ≤PESS,ch
s,h,i,t ≤nESS,h,i⋅PESS⋅uESS
s,h,i,t, ∀i ∈ΩESS, ∀s ∈S, ∀t ∈T
(42) 
0 ≤PESS,dis
s,h,i,t ≤nESS,h,i ⋅PESS ⋅
(
1 −uESS
s,h,i,t
)
, ∀i ∈ΩESS, ∀s ∈S, ∀t ∈T
(43) 
EESS
s,h,i,t = EESS
s,h,i,t−1 +
(
λch ⋅PESS,ch
s,h,i,t −PESS,ch
s,h,i,t
/
λdis)
⋅△t, ∀t ≥1
(44) 
EESS
s,h,i,t = nESS,h,i⋅EESS
ini , if t = 1
(45) 
nESS,h,i ⋅(1 −ε)E ≤EESS
h,i,t ≤nESS,h,i⋅ε⋅E, ∀i ∈ΩESS, ∀t ∈T
(46) 
Pcap,ESS
i
= E⋅
∑
h∈Ωi
h
nESS,h,i, ∀i ∈ΩESS
(47) 
OLTC is capable of adjusting the transformer tap voltage in response 
to load variations without disconnecting the power supply. By changing 
the tap position of the transformer, it mainly adjusts the voltage on the 
MV side of an HV/MV bus. The bus node voltage of a substation is 
converted into an adjustable variable, as shown in Equations (48)–(50). 
V2
min ≤V2
i,t⋅∂s,i,t ≤V2
max, ∀t ∈T, ∀i ∈ΩOLTC
(48) 
∂min
i
≤∂s,i,t ≤∂max
i
, ∀t, ∀i ∈ΩOLTC
(49) 
∂s,i,t = ∂min
i
+
∑
i
∂min
i
⋅uOLTC
s,i,t , ∀t ∈T, ∀i ∈ΩOLTC
(50) 
The exchanged active power and reactive power through a substat­
ion node are limited by the transactive capacity as given in Equations 
(51) and (52). 
−Smax
p
≤PSub
s,t ≤Smax
p
, ∀s ∈S, ∀t ∈T
(51) 
−Smax
q
≤QSub
s,t ≤Smax
q
, ∀s ∈S, ∀t ∈T
(52) 
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
6



<!-- page 7/16 -->

The quadratic form of the branch power flow constraints is given by 
Equation (53). 
Ps,l,t
2 + Qs,l,t
2 ≤Sl
2, ∀l ∈Ωij
l , ∀t ∈T
(53) 
SVC possesses fast dynamic regulation capability and can adjust the 
grid voltage by absorbing or injecting reactive power, thereby 
enhancing voltage stability. The amount of reactive power compensa­
tion is constrained by the upper and lower limits of power 
compensation. 
0 ≤QSVC
i,t
≤Qcap,SVC
i
, ∀t ∈T, ∀i ∈ΩSVC
(54) 
Qcap,SVC
i
= nSVC,i⋅QSVC rated, ∀i ∈ΩSVC
(55) 
2.5. Solution method for bi-level planning problem
The ADN planning problem has bi-level optimization objectives, 
requiring parameter transmission between upper and lower levels. Due 
to the multiplication of binary siting and integer sizing variables in this 
problem, the commercial solvers struggle to find solutions. Therefore, 
we consider using an Adaptive Particle Swarm Optimization (APSO) 
algorithm for solving it. Moreover, due to the diverse dimensions of 
multiple optimization objectives, weighted conversion is essential to 
obtain appropriate weights. To solve the lower multi-objective sched­
uling problem, this paper employs an SOCP (GUROBI solver) combined 
with technique for order preference by similarity to ideal solution 
(TOPSIS) method, which adjusts the weights of multiple objectives. The 
detailed solving process is shown in Fig. 3.
Firstly, the inertia weight of APSO is improved adaptively by 
analyzing the distance between particles and optimal particle. The dif­
ference in their position vectors xk
id, was used to guide the value of the 
inertia weight. In Equation (56), wk
i value is nonlinearly adjusted ac­
cording to the gap. 
wk
i = ws −(ws −we)
(
xk
i −1
)2
(56) 
where wk
i is the weight of particle i in iteration k. ws, we are beginning 
and ending values of the inertia weight respectively.
A dynamic mirror Pareto set is used to update the particle speed and 
position. In initial distribution stage, a mirror image is established with 
the optimal particle as an optimal Pareto set. As iteration proceeds, the 
average value of particles is calculated between each two mirrors, and 
the optimal solution is the global optimum at this time, so that the speed 
and position of particles are updated, as shown in Equations (57) and 
(58). 
vk+1
id (t + 1) = wk
i vk
id(t) + c1r1
[
pid(t) −xt+1
id (t)
]
+c2r2
[
Γ
(
pk
gd(t)
)
−xt
id(t)
]
(57) 
xk+1
id
= xk
id + xk+1
id
(58) 
where k is the iteration numbers, vk
id, xk
id is the velocity and position of 
particle i after iteration k. wk
i is the inertia weight. c1, c2 are the accel­
eration factor. r1, r2 ∈[0, 1] as random numbers. pk
gd is the optimal par­
ticle of current Pareto sets. Γ
(
pk
gd
)
is the superior particle of Pareto sets 
in two mirrors.
In multi-objective optimization problems, objectives are interde­
pendent and mutually influenced through the variables, and optimizing 
one objective often comes at the expense of others. Due to the potential 
inconsistency in evaluation scales across different objectives, it is chal­
lenging to directly assess the quality of solutions for this problem. 
Therefore, the TOPSIS method based on information entropy is used to 
solve the problem of multi-objective weight allocation in the optimiza­
tion process. After the normalization, information entropy and weights 
of objectives to measure uncertainty and diversity of the objectives are 
calculated by Equations (59) and (60). 
H(Y) = −
∑
n
i=1
(P(yi)log2 P(yi))
(59) 
Wi =
1 −H(yi)
∑
m
j=1
(1 −H(yi))
(60) 
where H(Y) represents information entropy of objectives, yi represents 
each possible value of objectives, and P(yi) is the probability of value 
being yi. Wi denotes entropy weight of the optimization objective, and m 
is the total number of objectives.
3. Uncertainty description of PV and load scenarios
An uncertainty description method based on Wasserstein Generative 
Adversarial Network with Gradient Penalty (WGAN-GP) and K-means 
was proposed to describe the uncertainties associated with PV genera­
tion and load demand. The installed EVCS and PV modules were 
assumed to remain unchanged, and the load was assumed to increase 
proportionally in different construction stages. Local historical mea­
surements of meteorological information and the historical load demand 
were taken as conditional values. When the unsupervised confrontation 
is completed, data x′ are generated. The loss functions of the generator 
and discriminator [31] are represented by LG and LD in Equations (61) 
and (62), respectively. 
LG = Exʹ∼p xʹ{log[1 −D(xʹ)]}
(61) 
LD = Ex∼p x[log D(x)] + Exʹ∼p xʹ{log[1 −D(xʹ)]}
(62) 
where E is the expectation, D(⋅) is the output value of the discriminator, 
and “~” indicates that the data follow the corresponding probability 
distribution. Particularly, x and x′ separately follow probability distri­
bution p_x and p_x′.
Unlike the GAN model, WGAN-GP can provide a smoother gradient 
by using the Wasserstein distance instead of the original Jensen- 
Shannon divergence as the discriminator loss function to measure the 
distance between the distribution of generated samples and the distri­
n
Fig. 3. Solving diagram based on APSO and SOCP for bi-level problem.
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
7



<!-- page 8/16 -->

bution of real samples. As shown in Fig. 4, the Wasserstein loss can help 
to improve the stability of training and provide a more useful gradient. 
Meanwhile, the gradient penalty term ensures that the discriminator 
satisfies the 1-Lipschitz constraint, further enhancing training stability. 
And it does not theoretically require balancing the training level of the 
generator and the discriminator, thus avoiding gradient vanishing and 
mode collapse. Therefore, its optimization goal becomes: 
min
G max
D V(G, D) = Ex∼p x[log D(x)] + Ex,∼p x,{log[1 −D(x,)]}
−ϑE˜x∼p ˜x
[
(‖∇˜xD(̃x)‖ −1)2]
(63) 
where ‖ ⋅‖ represents the 1-norm, ̃x = εx + (1 −
ε)G(x,), and ε obeys a 
uniform distribution on [0,1], ϑ denotes the regular term coefficient.
To avoid the problem of low efficiency caused by too many scenarios, 
a k-means clustering algorithm based on Euclidean distance is used to 
obtain typical scenarios.
4. Case study
4.1. Two test systems, data, and assumptions
To evaluate its effectiveness, the proposed bi-level planning model 
was applied to two different ADNs in Gansu Province, China: a 10-kV 41- 
bus rural network with a low load and 10-kV 40-bus urban network with 
a high load. Differences in the load characteristics and configurable 
Fig. 4. Basic structure of WGAN-GP.
Fig. 5. Distribution network of different characteristics.
Table 2 
Detailed impedance values of each branch in the 41-bus rural network.
From
To
Z = R + jX (Ω)
From
To
Z = R + jX (Ω)
From
To
Z = R + jX (Ω)
From
To
Z = R + jX (Ω)
41
1
0.67+j0.42
5
11
0.78+j0.49
19
21
0.57+j0.36
25
31
0.16+j0.10
1
2
0.67+j0.42
11
12
0.31+j0.20
20
22
0.05+j0.03
26
32
0.07+j0.05
2
3
0.78+j0.49
12
13
0.21+j0.13
21
23
0.21+j0.13
27
33
2.06+j1.31
3
4
0.21+j0.13
11
14
0.05+j0.03
22
24
0.62+j0.39
18
34
0.52+j0.32
4
5
0.21+j0.13
11
15
0.57+j0.36
23
25
0.05+j0.03
34
35
0.10+j0.07
5
6
0.05+j0.03
14
16
0.31+j0.20
24
26
0.78+j0.49
35
36
0.62+j0.40
6
7
0.93+j0.59
14
17
0.62+j0.39
25
27
0.10+j0.06
36
37
0.21+j0.13
7
8
0.08+j0.04
12
18
0.10+j0.07
27
28
0.36+j0.23
34
38
0.31+j0.20
2
9
0.05+j0.03
8
19
0.26+j0.16
22
29
0.94+j0.59
35
39
0.31+j0.20
4
10
0.05+j0.03
18
20
0.16+j0.90
20
30
0.59+j0.37
37
40
0.10+j0.06
Fig. 6. Typical power demand curves of charging EVs in working or residen­
tial areas.
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
8



<!-- page 9/16 -->

resource space of an ADN affect the plan for increasing PV penetration. 
The urban network had a greater transformer capacity than the rural 
network. Fig. 5 shows the architectures of the two ADNs. For the rural 
network, some nodes on the 10-kV main feeder are communal and 
correspond to 400-V LV buses. The red dashed line represents the set 
interconnection ties of ADN. The impedance of a branch is calculated 
based on the pole distance between two nodes according to Z = 0.650 +
j0.412 Ω/km. The impedances of each branch in the 41-bus rural 
network are exhibited in Table 2. Meteorological information used to 
describe the trend of PV generation includes the local measured irradi­
ance, temperature, and humidity. The EVCS charging information is 
provided by the manufacturer. A 20 kW EVCS was selected for both 
working and residential areas. Fig. 6 shows the typical power demand 
curves obtained when charging EVs.
Consistent module parameters are adopted, including the investment 
and maintenance costs of the PV, ESS, EVCS, SVC, and OLTC as well as 
the capacity of the minimum installed unit, as given in Table 3 [43]. 
Table 4 presents the baseline values of the operational parameters of the 
10-kV networks. The voltage upper and lower limits are set to 0.95 and 
1.05 respectively. The candidate nodes of flexible resources are shown in 
Table 5.
The WGAN-GP algorithm is run in Keras environment of TensorFlow 
2.1 and all other algorithms are run on MATLAB R2018. The algorithms 
are installed on a computer with an Intel Core i7-8700 CPU operating at 
3.20 GHz.
4.2. Results analysis of uncertainty description
For the uncertainty analysis, the model is trained using 1 months of 
limited PV output information from a PV plant in western China as a 
testing dataset with samples comprising 24-h PV outputs in 1-h in­
tervals. Fig. 7(a) shows the generated samples. The thin lines are power 
output curves generated by the WGAN-GP to reflect the PV time-series 
characteristics. PV output is usually characterized according to the 
weather [44]. The k-means clustering algorithm is used to obtain typical 
scenarios for different types of weather, as shown by the thick lines in 
Fig. 7(a). While the PV output depends on the weather, building loads 
(including EVCSs) often exhibit periodic characteristics that depend on 
the working state. During nonworking hours, the load trend is more 
complex and variable, which affects the GAN result. The k-means clus­
tering algorithm is used to reduce the number of generated samples and 
improve the correlation to real load demand scenarios.
The proposed uncertainty description method is verified by com­
parison with Latin hypercube sampling (LHS), which generates new 
scenarios by grouping random sampling. Fig. 8 shows the Taylor dia­
gram comparing the performances of the two methods in terms of the 
heuristic distance with the corresponding observation [45]. The method 
based on WGAN-GP outperforms traditional GAN in terms of SD and 
correlation when describing PV uncertainty, by 0.03 and 2.9 % 
respectively.
4.3. Planning results description
The planning process is different for the two ADNs owing to the large 
difference in resource endowment and transformer capacity. In this part, 
we select a stage Pcap,pv ≥3.0 MW to describe the coordinating plan of 
siting and sizing. To meet the integrated PV capacity requirement and 
consider the actual charging demand of EV users, ten PV and three EVCS 
candidate nodes are selected for the rural network. Meanwhile, five PV 
and four EVCS candidate nodes are selected for the urban network.
Fig. 9 shows the optimization results of the two networks. For the 
rural network (high-PV and low-load situation), some transformers had 
a small capacity; hence, a single node had a small PV integration ca­
pacity. The largest PV integration capacity is 600 kW. The total inte­
grated PV capacity is 3.1 MW, and the PV penetration rate reaches 124 
%, as shown in Fig. 9(a). The EVCSs are deployed at nodes 32, 36, and 39 
with a total installed capacity of 240 kW. OLTC is installed at node 41 
with a capacity of 6 MVA. The SOP location and capacity are shown in 
Table 6. For the rural network, charging and discharging by the ESSs are 
mainly used to stabilize fluctuations in PV generation. Rural networks 
relying solely on ESSs and orderly charging guidance find it challenging 
to support high-penetration PVs. SOPs flexibly balance the power flow 
between feeders to reduce the impact of PV and fluctuations on feeders 
and node voltage collaborated with OLTC. Fig. 10(a) shows the opti­
mization results of the rural network in sunny weather. From 10:00 to 
17:00, PV generated enough power to not only meet the load demand of 
the rural network but also send a large amount of power back to the 
upper network. The ESSs installed at different sites have different 
charging behavior, but through the superimposed bar chart of all ESSs, 
they generally charge during the daytime and discharge at night.
In contrast to the rural network (high-PV and high-load situation), 
the 40-bus urban network has a larger transformer capacity. Deploying 
EVCSs in the urban network has a positive effect on PV integration. The 
orderly charging behavior of EVCSs is considered from the perspective 
of the DNO. Fig. 9(b) shows the optimal siting and sizing results of the 
urban network. The installed PV capacity was 3.25 MW, and PV 
Table 3 
Major parameters of the modules(PV, ESS, EVCS, SVC, AND OLTC).
Module
Description
Value
PV
Investment cost of PV unit capacity cPV
cons ($/kW)
856.9
Unit curtailment cost cp ($/kWh)
0.086
Minimum rated power of installed PV PPV rated (kW)
20
Annual maintenance cost ma
pv ($/kW)
12.9
ESS
Investment cost of ESS unit capacity cESS
cons ($/kWh)
513.6
Unit energy capacity of ESS modules E (kWh)
20
Charging/discharging efficiency λch/ λdis
95 %
Depth of discharge ζ
90 %
Annual maintenance cost ma
ESS ($/kWh)
10.3
EVCS
Investment cost of EVCS modules cEVCS
cons ($/kW)
92.9
Unit capacity of EVCS modules PEVCS rated (kW)
20
Annual maintenance cost ma
EVCS ($/kW)
1.9
SOP
Investment cost of unit capacity cSOP
cons ($/kVA)
142.8
Unit capacity of SOP SSOP_rated (kVA)
100
Loss coefficient ASOP
i
0.02
Annual maintenance cost ma
SOP ($/kVA)
2.8
SVC
Investment cost of unit capacity cSVC
cons ($/kVA)
142.8
Unit capacity of SVC modules Qsvc_rated (kVA)
10
Annual maintenance cost ma
SVC ($/kVA)
2.8
OLTC
Investment cost of ESS unit capacity cOLTC
cons ($/kVA)
62.5
Annual maintenance cost ma
OLTC ($/kVA)
0.167
Service life of each component ∂
15
Discount rate r
0.065
Table 4 
Baseline values of network operational parameters.
Parameter
Description
Value
Vmax/Vmin
Voltage upper and lower limits
0.95/1.05
Smax
p
/ Smax
q
Substation capacity limit (MW, Mvar)
3.2/2.1
Sl
Branch flow limit (MVA)
2.9
Electricity prices
1:00–2:00, 5–6:00, 0.5. 3:00–4:00, 10:00–17:00,0.26 
7:00–9:00, 18:00–24:00, 0.76
Table 5 
The candidate nodes of flexible resources in the different network.
Candidate sites
41-bus rural network
40-bus urban network
PV
[1–40]
[6,8,10,12,15,18,20,26–33,35,38]
ESS
[6,9–12,15,20–26,28–31]
[4, 10, 14, 18, 22, 
32-35, 37, 39]
EVCS
[ 12, 13, 15–17, 25–40]
[3, 6, 9, 14, 18, 20, 
28-33, 36, 39]
SVC
[8–12,25–30]
[9,11,14,16,20,26–28,34,36,37]
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
9



<!-- page 10/16 -->

Fig. 7. Uncertainty of PV generation and total load demand.
Fig. 8. Taylor diagrams comparing correlations of proposed uncertainty description method (WGAN-GP, green dot) and benchmark method (GAN, blue dot; LHS, red 
dot) against the observed point (brown dot).
Fig. 9. Optimal siting and sizing results of different networks.
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
10



<!-- page 11/16 -->

penetration reached 104.8 %. The optimal EVCS locations are nodes 10, 
26, 28, and 37 with a total capacity of 1.6 MW. Fig. 10(b) shows the 
optimal operation results of the urban network on an overcast day. Be­
sides improving the economy of ADN operation, the safety objective of 
the voltage deviation and network loss is to ensure that ESSs complete 
their charging at night. In this paper, the DNO’s response not only meets 
the rigid demand for EV charging, but also regulates 20 % of the set 
charging load. During the period of daytime from 9:00 to 18:00, the EV 
charging power increases, which consumes the excess PV power gen­
eration during the noon period, thereby alleviating the overvoltage 
problem. The guidance of orderly charging also plays an important role 
in the improvement of PV integration.
4.4. Case study of different planning strategy
On the premise of meeting the PV penetration of ADN, the following 
cases are considered to compare the performance of the proposed model 
with other typical planning strategies in terms of investment cost, 
operational cost, and ADN security. 
Case A.
Consider the ADN planning including the construction of PV, 
EVCS and ESS;
Case B.
An LHS-based uncertainty description method and consider 
the construction of PVs, ESSs, EVCSs and active management resources 
(SOPs, SVCs, OLTC);
Case C.
A robust optimization method that fully considers the PV 
output and load scenarios in extreme weather, consider the construction 
of PVs, ESSs, EVCSs and active management resources (±20 interval);
Case D.
(Proposed method): A WGAN-GP-based uncertainty descrip­
tion method, and consider construction of PVs, ESSs, EVCS, SVCs, OLTC 
Table 6 
Locations and capacities of SOP.
Case
41-bus ADN
40-bus ADN
SOP location
TS1
TS2
TS3
TS1
TS2
TS3
Capacity (kVA)
300
300
/
200
/
300
Fig. 10. Daily optimal operation results in different distribution network: (a) 
rural distribution network, (b) urban distribution network.
Table 7 
Performance index of ADN investment and annual operational cost with 
different planning (A) 41-bus rural network (ζ = 1.2).
Planning 
Solution
Total 
cost(M$)
Investment 
cost(M$)
Operational 
cost(M$)
PV curtailment 
(k$)
Case A
14.93
0.91
14.02
50.43
Case B
13.19
0.84
12.35
53.85
Case C
14.15
0.83
13.32
45.30
Case D
12.78
0.77
12.01
48.12
(B) 40-bus urban network (ζ = 1.2)
Planning 
Solution
Total 
cost(M$)
Investment 
cost(M$)
Operational 
cost(M$)
PV curtailment 
(k$)
Case A
25.36
0.93
24.43
50.25
Case B
23.01
0.78
22.23
45.86
Case C
23.58
0.85
22.73
36.12
Case D
22.18
0.75
21.43
38.44
Fig. 11. Voltage distribution in different ADN under overcast condition.
Fig. 12. Voltage deviation and minimum voltage values abstained for 
both feeders.
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
11



<!-- page 12/16 -->

and SOPs.
The PV integration capacity is set to exceed 3 MW. Table 7 presents 
the results of the different planning strategies for the two networks. With 
Case A, In Case 1, a larger-capacity ESS needs to be configured to 
compensate for the lack of voltage regulation capability, and due to the 
high unit cost of ESS, the investment costs actually increase instead of 
decreasing. And the PV curtailment is increased by 4.8 % compared with 
Case D for the rural network, as shown in Table 7. From the investment 
cost index, Case C install more flexible resources than the proposed 
method owing to its consideration of extreme weather conditions. In 
rural network, although the PV curtailment cost is reduced by 2.82k$ 
compared with the proposed method, the investment and operational 
cost are increased by 7.79 % and 10.91 %, and the overall cost is not 
optimal. With Case D, the investment costs of the rural and urban net­
works are similar, but the rural network has a lower annual operational 
cost by 9.42 M$. The proposed method reduces the investment cost and 
annual operational cost of the rural network by 9.1 % and 2.8 % 
compared with Case B that using LHS-based method, which demon­
strates the advantages of the proposed method.
The voltage deviation and minimum voltage of power flow in 
different feeders are shown in Fig. 12. Note that for all considered cases, 
the minimum voltage value of each bus at each time step will not be 
lower than the predefined minimum voltage, which is 0.95 p.u. In 
comparison of different plans, the robust plan has more stable minimum 
voltage, followed by the ADNEP method proposed in this paper. The 
voltage distribution of rural and urban ADN is shown in Fig. 11, node 
voltages fluctuate from 0.98 to 1.05 when planning PV and other flexible 
resources, and the voltage value decreases with the distance from the 
substation.
To offer a more comprehensive comparison with other similar 
planning methods, the following experiments are carried out: The 
improved robust optimization method by the generation of source-load 
scenarios using LHS to reduce the conservativeness [40] (Case 1); Based 
on WGAN-CG method, a solving method using SOCR (Gurobi), without 
considering OLTC and SOPs [36] (Case 2); A multi-objective PSO-based 
method using iterative power flow calculation (Matpower) [35] (Case 
3); The proposed method based on WGAN-CG and the iterative solving 
process of APSO and SOCP (Gurobi) (Case 4).
Based on the representative scenarios obtained from scenario gen­
eration and clustering, autocorrelation coefficients are employed to 
further compare the WGAN-GP and LHS method. As shown in Fig. 13(a), 
the autocorrelation curve from WGAN-GP closely matches that of the 
original series, indicating it captures temporal dependencies more 
accurately than LHS in Case 1. Under identical experimental settings, the 
algorithm convergence is also evaluated in Fig. 13(b), which demon­
strates that the proposed APSO converges more rapidly than PSO.
The total cost and voltage deviation results are presented in Fig. 14. 
In Case 1, after reducing conservativeness of robust optimization using 
LHS, the total cost decreased by 6.7 % compared to the traditional robust 
method of Case C in Table 7. However, this improvement led to an in­
crease in voltage fluctuation of 1.8 % increase. Compared to the random 
optimization method proposed in this paper at ζ = 1.2, the cost increases 
by 0.42 M$, while the voltage deviation is reduced by 0.05 %. In Case 2, 
the absence of OLTC voltage regulation and SOP overload mitigation 
results in the regulation cost being absorbed by other resources, such as 
ESS, leading to worse performance. In Case 3, the fluctuation of PV 
outputs is not considered, and a higher smoothing factor for PV output is 
selected. It increases the total power generation and reduces fluctuations 
under the minimum requirement of PV integration. As a result, the 
reserve capacity is not needed to address short-term fluctuations, 
reducing the required ESS capacity. The needs for SVC and SOP capacity 
also decrease due to smaller voltage and flow fluctuations, resulting in a 
lower total cost of 0.16 M$ than the proposed method. However, when 
faced with other PV output scenarios, the average voltage fluctuation in 
case 3 increases by 1.36 %, as shown in Fig. 14(b).
The computation times are shown in Table 8. In Case 3, the nested 
power flow calculation based on Matpower, rather than optimization, 
results in shorter computation time. Compared to Case 1, the time is 
reduced by 0.12 h due to the absence of neural network training. In Case 
2, the solver struggles with the strong nonlinearity caused by the 
product of discrete site variables and other integer variables, so an outer 
site combination search is used in this case, increasing the computation 
time by 0.04 h compared to the proposed method. Despite differences in 
solution approaches, all cases are solved within a reasonable time for 
planning tasks that do not require strict real-time requirements.
Fig. 13. Comparison of autocorrelation and convergence process.
Fig. 14. Comparison of total cost and voltage deviation in different cases.
Table 8 
Comparative analysis of computing efficiency of different cases.
Case
Case 1
Case 2
Case 3
Case 4
Calculation time (h)
1.51
1.67
1.23
1.63
Table 9 
ADN planning with different stage of PV penetration in 41-bus rural network.
Parametric index
Planning stages with minimum penetration ζ
ζ = 0.8
ζ = 1.0 
(increment)
ζ = 1.2 
(increment)
Increment of 
resource capacity
PV (MW)
2.15
0.5
0.45
EVCS 
(MW)
0.16
0.03
0.05
ESS 
(MWh)
0.80
0.10
0.16
SVC 
(MVA)
0.40
0.10
0.15
OLTC 
(MVA)
6
/
/
SOP 
(MVA)
0.6
0.1
0.2
Increment of investment (M$)
0.57
0.09
0.11
Annual operational cost (M$)
10.21
11.18
12.01
Voltage deviation
1.76 %
1.83 %
1.85 %
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
12



<!-- page 13/16 -->

4.5. Case study in different PV penetration
To evaluate the evolution of resource configuration at different 
stages of PV penetration, three minimum PV penetration indices were 
defined: 0.8, 1.0, and 1.2. Table 9 presents the results of the proposed bi- 
level ADN planning model in different stages of the 41-bus rural 
network. At ζ = 0.8, the proposed model configured the various flexible 
resources to ensure a small voltage deviation and small network loss 
while minimizing the operational costs and providing space for future 
increments in PV penetration. At ζ = 1.0 and ζ = 1.2, more flexible 
resources need to be configured, which increased the investment costs 
and annual operational costs by 0.02 M$ and 0.83 M$, respectively. It 
can be seen from the voltage deviation that with the gradual increase of 
PV integration, the voltage fluctuation becomes larger and increases the 
risk of voltage crossing the limit.
4.6. Description of SOCR accuracy and multi-objective optimization
To address the non-convex problems associated with power flow 
constraints, the proposed model performs a SOCR approximation in 
terms of the AC power flow constraints. The following calculation for­
mula of SOCR error Δdiff
ij,t is defined: 
Δdiff
ij,t = Ui,tIi,t −
(
P2
ij,t + Q2
ij,t
)
(64) 
The relaxation errors of each branch across all time are calculated 
and presented in Fig. 15. As shown in Fig. 15(a), the maximum relaxa­
tion error is on the order of 10−6. Notably, the 41-node network exhibits 
higher errors than the 40-node distribution network, yet both satisfy the 
precision requirements and the feasibility of the relaxation approach 
implemented by SOCR. It also implies that the condition that the SOCR 
solution is a global optimum of the original problem is basically satis­
fied. And the results align with reference [36].
Under the same basic parameter settings, this paper analyzes the 
performance of operational schemes under different optimization ob­
jectives, including operational cost, distribution network loss, and 
voltage deviation. The TOPSIS method is used to find the optimal 
compromise point between these multi-objectives with different di­
mensions. The Pareto front is shown in Fig. 16. The Pareto front curve 
maintains continuity, and the solution set exhibits relatively uniform 
distribution. The curve clearly demonstrates the relationships among 
the three objectives. Overall, the operational cost is inversely propor­
tional to the other two security objectives. As ADN network loss or 
voltage deviation increases, the daily operational cost decreases 
accordingly, which aligns with practical operation scenarios.
Table 10 presents three typical solutions with a focus on different 
objective functions. The DNO can choose different options based on 
their preferences. Among them, Solution 1 focuses on economic benefits, 
and although its cost is lower than the other solutions, the other in­
dicators are noticeably higher. Solution 2 places more emphasis on ADN 
network loss and voltage deviation. In this case, the network loss is 
reduced by 162 kW, and the voltage deviation is reduced by 4.95 %. 
Solution 3 considers the relationship between the three indicators. 
Compared to 1, although the operational cost increases, the network loss 
and voltage deviation are significantly reduced, achieving a higher 
overall satisfaction and balancing all three indicators.
4.7. Operational results of multiple flexible resources
The 41-bus rural ADN is employed to illustrate the supporting roles 
of multiple flexible resources. The typical PV output scenarios under 
sunny and cloudy conditions are depicted by the red line in Fig. 7(a). The 
maximum number of daily voltage adjustments is set to 5 times. Fig. 17
presents the outcomes of OLTC voltage regulation and SVC reactive 
power compensation. In the early morning when there is no PV power 
generation, the overall voltage is low. The SVC operates at a higher tap 
setting while adjusting the OLTC ratio to maintain voltage stability. 
Around midday, when the PV output reaches its peak, both the OLTC 
and SVC remain at lower settings to stabilize the voltage, particularly 
under the sunny scenario, as shown in Fig. 17(a). By contrast, under the 
overcast condition, the OLTC and SVC generally operate at higher tap 
positions to compensate for the reduced PV generation. Between 12:00 
and 16:00, as the load decreases, the OLTC ratio is lowered accordingly 
to accommodate voltage changes.
To evaluate the ESS response strategy for flexible regulation re­
quirements, Fig. 18 presents the optimal operational schemes and ca­
pacity variations of four ESS units in a 41-bus rural ADN. These units 
exhibit similar operational patterns and capacity trends. During midday 
peak PV generation periods, the ESS units charge to prevent overvoltage 
risk. In early morning and nighttime hours, they compensate for 
demand-supply imbalances, improving system economic efficiency. 
Notably, despite low load conditions between 3:00 and 4:00, the ESS 
units utilize low electricity prices to charge, thereby increasing the 
overall system load. During this period without PV generation, both 
reactive power compensation and OLTC operate at elevated settings (as 
demonstrated in Fig. 17) to ensure ADN stability.
To examine the impact of flexible resources on system voltage 
regulation, Fig. 19 presents the voltage profiles at nodes 6 and 29 under 
different PV output scenarios. Under the sunny scenario with only the 
high-proportion PV generation, the voltage at these nodes rises signifi­
cantly, posing an overvoltage risk. Once flexible resources are incorpo­
rated, the voltage fluctuation is notably reduced. By contrast, under the 
overcast condition, At the end-of-line node 29, midday PV output is 
relatively low, while the load is comparatively high, leading to a 
maximum voltage of 1.027 p.u. Between 1:00 and 7:00, the load is 
Fig. 15. SOCR error scatter plot.
Fig. 16. Pareto optimal solution sets.
Table 10 
Analysis of 41-bus ADN planning results of single and multiple objective.
Results
Daily operational cost (k$)
Network loss (kW)
Voltage deviation
1
45.3
480
6.05 %
2
62.0
313
1.36 %
3
59.8
318
1.76 %
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
13



<!-- page 14/16 -->

minimal, resulting in lower line currents and reduced voltage drops. 
Consequently, with a stable upstream voltage, the end-of-line nighttime 
voltage is higher than at midday. Through the coordinated operation of 
the OLTC and SVC, voltage stability is further enhanced.
4.8. Validation on the rural 109-bus distribution network
To validate the scalability and effectiveness of the proposed planning 
method in large-scale distribution networks, this paper also selects an 
actual rural 109-bus network in Gansu Province, with active and reac­
tive power demands of 16.5 MW and 12.38 Mvar, respectively. Given 
that this ADN has more branches and a longer power supply radius 
between line terminals and the substation, which leads to significant 
voltage drop issues, as shown in Fig. 20. Therefore, a greater number of 
flexible resources are deployed to mitigate power fluctuations and 
enhance voltage stability across the complex feeders. Other parameters 
remain consistent with the 41-node test system.
The optimization results for sites and capacities of flexible resources 
are shown in Fig. 21. To reduce the search space for location variables, 
the candidate nodes for PV installation are set on the main feeders. 
Among these nodes, the one closest to the substation (node 6) hosts the 
Fig. 17. OLTC and SVC actions under different PV scenarios.
Fig. 18. ESS optimization results in different sites of ADN.
Fig. 19. Node voltage under the integration of multiple flexible resources.
Fig. 20. 109-bus rural network.
Fig. 21. Optimal siting and sizing results in 109-bus networks.
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
14



<!-- page 15/16 -->

highest PV capacity at 1.5 MW. Overall, the total PV capacity amounts to 
13.3 MW, yielding a penetration level ζ of 80.6 % and fulfilling the first- 
stage PV deployment requirements. To avoid the pronounced voltage 
drops at the terminal due to the higher cumulative impedance, SVC with 
a capacity of 3.1Mvar is integrated. The SOP switches are all in the open 
state. Through reactive power compensation, the node voltage is 
maintained within an acceptable range, as shown in Fig. 22. The node 
voltage distribution is analyzed from the perspective of the DSO’s 
preference for voltage stability. At midday, the coordinated action of 
OLTC voltage reduction and ESS smoothing effectively prevents any 
significant voltage increase despite high PV generation, keeping the 
voltage near its designated standard value. At night, some node voltages 
hover around 0.96 p.u. The overall voltage fluctuations remain at a 
relatively low level, demonstrating the effectiveness of the coordinated 
planning strategy.
Table 11 presents the economic benefits of the proposed planning 
method under different cases, with settings consistent with Section 4.4. 
In Case A, although ESS and EVCS help smooth supply-demand fluctu­
ations, in the absence of active voltage regulation, when excessive PV 
generation drives the voltage to its upper limit, a portion of the power 
must be curtailed, resulting in an annual curtailment penalty increase of 
0.02 M$. Overall, total costs are reduced by up to 1.29 M$ compared to 
other cases. Despite the increased number of nodes and more complex 
power flows add to the computational burden, the APSO algorithm, by 
invoking the Gurobi solver with an optimality tolerance of 0.001, can 
still obtain the optimal solution. These results demonstrate that the 
proposed method is adaptable to ADNs of various scales and delivers 
better performance.
5. Conclusion
In this paper, a bi-level coordinated ADN expansion planning method 
is proposed to accommodate high-penetration PVs integration while 
maintaining economic efficiency and flexibility of ADN. An uncertainty 
description method based on WGAN-GP and k-means is presented to 
generate uncertain scenarios to approximate reality. Compared to 
traditional GAN, the correlation index for describing PV uncertainty 
using presented method has been improved by 2.9 %. Based on 
described uncertainties, this paper cooperatively configures EVCSs with 
orderly charging guidance, ESSs and active management resources. To 
solve this MISOCP problem, a hybrid algorithm combining adaptive 
particle swarm optimization (APSO) and SOCP with information 
entropy-based TOPSIS is proposed. The proposed method is evaluated 
using rural and urban networks, compared to plans without active 
resource management, total costs of the proposed coordinated plan is 
respectively decreased by 14.4 % and 12.5 %. It can significantly 
enhance the economic operation of distribution systems, especially in 
integration of high penetration of PVs. Although SOP and OLTC instal­
lation requires extra budget, the operational cost of ADN can be 
considerably reduced owing to the flexibility offered by this active 
management resources.
However, this paper does not consider the three-phase unbalanced 
power flow that exist in LV networks. The allocation of flexible resources 
is mainly discussed within the MV network. This issue will be addressed 
in future research, and the multi-stage planning around the uncertainty 
of line outages during emergencies will be also investigated.
CRediT authorship contribution statement
Jianjing Li: Writing – original draft, Methodology, Conceptualiza­
tion. Fan Li: Validation, Funding acquisition. Kai Sun: Writing – review 
& editing, Methodology, Data curation. Bo Sun: Writing – review & 
editing, Validation.
Declaration of competing interest
The authors declare that they have no known competing financial 
interests or personal relationships that could have appeared to influence 
the work reported in this paper.
Acknowledgements
This work was supported in part by the National Natural Science 
Foundation of China (Grant No. 62192753, 62133008), the National 
Key Research and Development Program of China (Grant No. 
2023YFB4004500).
Data availability
Data will be made available on request.
References
[1] Li Y, Feng B, Wang B, Sun S. Joint planning of distributed generations and energy 
storage in active distribution networks: a Bi-Level programming approach. Energy 
(Calg) Apr. 2022;245:123226.
[2] Asensio M, Quevedo P, Mu˜noz-Delgado G, Contreras J. Joint distribution network 
and renewable energy expansion planning considering demand response and 
energy storage—Part I: stochastic programming model. IEEE Trans Smart Grid Mar. 
2018;9(2):655–66.
[3] Suryakiran B, Nizami S, Verma A, Saha T, Mishra S. A DSO-Based day-ahead 
market mechanism for optimal operational planning of active distribution network. 
Energy (Calg) Nov. 2023;282:128902.
[4] Liang H, Pirouzi S. Energy management system based on economic Flexi-reliable 
operation for the smart distribution network including integrated energy system of 
hydrogen storage and renewable sources. Energy (Calg) 2024;293(Apr).
[5] Liu J, Gao H, Ma Z, Li Y. Review and prospect of active distribution system 
planning. J. Mod. Power Syst. Clean Energy Dec. 2015;3(4):457–67.
[6] Abdollah R. Distribution network expansion planning: an updated review of 
current methods and new challenges. Renew. Sust. Energ. Rev Jan. 2024;189: 
114062.
[7] Home-Ortiz J, Macedo L, Vargas R, Romero R, Mantovani J, Catal˜ao J. Increasing 
RES hosting capacity in distribution networks through closed-loop reconfiguration 
and volt/var control. IEEE Trans Ind Appl Aug. 2022;58(4):4424–35.
[8] Paterakis NG, Erdinc O, Bakirtzis AG, Catalao JPS. Qualification and quantification 
of reserves in power systems under high wind generation penetration considering 
demand response. IEEE Trans Sustain Energy Jan. 2015;6(1):88–103.
[9] Erdinc A Tascikaraoglu, Paterakis N, Dursun I, Sinim M, Catal˜ao J. Comprehensive 
optimization model for sizing and siting of DG units, EV charging stations, and 
energy storage systems. IEEE Trans Smart Grid Jul. 2018;9(4):3871–82.
[10] Cao X, Cao T, Gao F, Guan X. Risk-averse storage planning for improving RES 
hosting capacity under uncertain siting choices. IEEE Trans Sustain Energy Oct. 
2021;12(4):1984–95.
Fig. 22. Node voltages of 109-bus network under sunny condition.
Table 11 
Performance index of 109-bus ADN investment and annual operational cost with 
different plans (ζ = 0.8).
Planning 
Solution
Total 
cost(M$)
Investment 
cost(M$)
Operational 
cost(M$)
PV curtailment 
(M$)
Case A
76.49
1.26
75.23
0.20
Case B
75.76
1.67
74.09
0.21
Case C
76.57
1.76
74.81
0.16
Case D
75.28
1.62
73.66
0.18
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
15



<!-- page 16/16 -->

[11] Gautam P, Karki R, Piya P. Probabilistic modeling of energy storageto quantify 
market constrained reliability value to active distribution systems. IEEE Trans 
Sustain Energy Apr. 2020;11(2):1043–53.
[12] Yang Z, Xia L, Guan X. Fluctuation reduction of wind power and sizing of battery 
energy storage systems in microgrids. IEEE Trans. Automat. Sci. Eng. Jul. 2020;17 
(3):1195–207.
[13] Cao X, Wang J, Zeng B. A chance constrained information-gap decision model for 
multi-period microgrid planning. IEEE Trans Power Syst May 2018;33(3):2684–95.
[14] Fu Y, Chiang H. Toward optimal multiperiod network reconfiguration for 
increasing the hosting capacity of distribution networks. IEEE Trans. Power Del. 
Oct. 2018;33(5):2294–304.
[15] Toghranegar S, Rabiee A, Mohseni-Bonab SM. Increasing unbalanced distribution 
network’s hosting capacity for distributed energy resources by voltage regulators. 
IEEE Access Mar. 2023;11:22664–79.
[16] Asensio M, Munoz-Delgado G, Contreras J. Bi-Level approach to distribution 
network and renewable energy expansion planning considering demand response. 
IEEE Trans Power Syst Nov. 2017;32(6):4298–309.
[17] Ahmadian A, Sedghi M, Aliakbar-Golkar M. Fuzzy load modeling of plug-in electric 
vehicles for optimal storage and DG planning in active distribution network. IEEE 
Trans Veh Technol May 2017;66(5):3622–31.
[18] Aldhanhani T, Al-Durra A, El-Saadany EF. Optimal design of electric vehicle 
charging stations integrated with renewable DG. Proc. IEEE innov. Smart grid 
technol. Asia (ISGT-Asia), Auckland, New Zealand. Dec. 2017. p. 1–6.
[19] Jooshaki M, Abbaspour A, Fotuhi-Firuzabad M, Mu˜noz-Delgado G, Contreras J, 
Lehtonen M, Arroyo J. An enhanced MILP model for reliability-constrained 
distribution network expansion planning. IEEE Trans Power Syst Jan. 2022;37(1): 
118–31.
[20] Shen Y, Zhang S, Ding M, Cheng H, Li C, Liu D. Expansion planning of soft open 
points based distribution system considering EV traffic flow. IEEE Trans Ind Appl 
Jan. 2024;60(1):1229–39.
[21] Sarantakos I, et al. A robust mixed-integer convex model for optimal scheduling of 
integrated energy storage—Soft open point devices. IEEE Trans Smart Grid Sep. 
2022;13(5):4072–87.
[22] Koltsaklis NE, Dagoumas AS. State-of-the-art generation expansion planning: a 
review. Appl Energy Nov. 2018;230:563–89.
[23] Xiang Y, Liu J, Liu Y. Robust energy management of microgrid with uncertain 
renewable generation and load. IEEE Trans Smart Grid Mar. 2016;7(2):1034–43.
[24] Shen X, Shahidehpour M, Han Y, Zhu S, Zheng J. Expansion planning of active 
distribution networks with centralized and distributed energy storage systems. 
IEEE Trans Sustain Energy Jan. 2017;8(1):126–34.
[25] Boroumandfar G, Khajehzadeh A, Eslami M, Syah R. Information gap decision 
theory with risk aversion strategy for robust planning of hybrid photovoltaic/ 
wind/battery storage system in distribution networks considering uncertainty. 
Energy (Calg) 2023;278:127778.
[26] Arias N, Tabares A, Franco J, Marina L, Ruben R. Novel multi-stage stochastic DG 
investment planning with recourse. IEEE Trans Sustain Energy Jan. 2017;8(1): 
164–78.
[27] Wang B, Zhang C, Dong ZY, Li X. Improving hosting capacity of unbalanced 
distribution networks via robust allocation of battery energy storage systems. IEEE 
Trans Power Syst May 2021;36(3):2174–85.
[28] Xing H, Cheng H, Zhang Y, Zeng P. Active distribution network expansion planning 
integrating dispersed energy storage systems. IET Gener. Transmiss. Distrib. Feb. 
2016;10(3):638–44.
[29] de Lima TD, Franco JF, Lezama F, Soares J, V ale Z. Joint optimal allocation of 
electric vehicle charging stations and renewable energy sources including CO2 
emissions. Energy Informat Sep. 2021;4(S2).
[30] Ehsan A, Y ang Q. Coordinated investment planning of distributed multi-type 
stochastic generation and battery storage in active distribution networks. IEEE 
Trans Sustain Energy Oct. 2019;10(4):1813–22.
[31] Zhang X, Hua W, Liu Y, et al. Reinforcement learning for active distribution 
network planning based on monte carlo tree search. Int J Electr Power Energy Syst 
2022;138:107885.
[32] Li Y, Wang B, Yang Z, et al. Hierarchical stochastic scheduling of multi-community 
integrated energy systems in uncertain environments via stackelberg game. Appl 
Energy Feb. 2022;308:118392.
[33] Li Y, Li J, Wang Y. Privacy-preserving spatiotemporal scenario generation of 
renewable energies: a federated deep generative learning approach. IEEE Trans. 
Ind. Informat. Jul. 2021;18(4):2310–20.
[34] Li Y, Feng B, Wang B, et al. Joint planning of distributed generations and energy 
storage in active distribution networks: a Bi-Level programming approach. Energy 
(Calg) 2022;245:123226.
[35] Mukhopadhyay B, Das D. Multi-objective dynamic and static reconfiguration with 
optimized allocation of PV-DG and battery energy storage system. Renew Sustain 
Energy Rev 2020;124(February):109777.
[36] Wang C, Liu C, Chen J, et al. Cooperative planning of renewable energy generation 
and multi-timescale flexible resources in active distribution networks. Appl Energy 
2024;356:122429.
[37] Sharma S, Niazi K, Verma K, Rawat T. Coordination of different DGs, BESS and 
demand response for multi-objective optimization of distribution network with 
special reference to Indian power sector. Int J Electr Power Energy Syst 2020;121: 
106074.
[38] De Lima T, Franco J, Lezama F, et al. A specialized long-term distribution system 
expansion planning method with the integration of distributed energy resources. 
IEEE Access 2022;10:19133–48.
[39] Wang Y, Shen X, Xu Y. Joint planning of active distribution network and ev 
charging stations considering vehicle-to-grid functionality and reactive power 
support. CSEE Journal of Power and Energy Systems 2023;10(5):2100–13.
[40] Zhou S, Han Y, Chen S, et al. A multiple uncertainty-based bi-level expansion 
planning paradigm for distribution networks complying with energy storage 
system functionalities. Energy (Calg) 2023;275:127511.
[41] Farivar M, Low S. Branch flow model: relaxations and convexification—Part I. IEEE 
Trans Power Syst 2013;28(3):2554–64.
[42] Low S. “convex relaxation of optimal power flow—Part I: formulations and 
equivalence. IEEE Transactions on Control of Network Systems 2014;1(1):15–27.
[43] Yao W, Zhao J, Wen F, Dong Z, Xue Y, Xu Y. A multi-objective collaborative 
planning strategy for integrated power distribution and electric vehicle charging 
systems. IEEE Trans. on Power Syst., col Jan. 2014;29(4):1811–21.
[44] Li J, Zhang C, Sun B. Two-stage hybrid deep learning with strong adaptability for 
detailed day-ahead photovoltaic power forecasting. IEEE Trans Sustain Energy Jan. 
2023;14(1):193–205.
[45] Taylor KE. Summarizing multiple aspects of model performance in a single 
diagram. J. Geophys. Res.-Atmos. Apr. 2001;106(7):7183–92.
J. Li et al.                                                                                                                                                                                                                                         
Energy 330 (2025) 136685 
16
