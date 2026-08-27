<!--
source: D5_规划与灵活资源/EN_NatureComm_2024_flexible_distribution.pdf
sha256: e77d0a3df37e0deded642aced560978843d4a7cb0b967053c9be1381970a5e00
method: pymupdf
pages: 14
-->

<!-- page 1/14 -->

Article
https://doi.org/10.1038/s41467-024-48862-5
Multi-resource dynamic coordinated
planning of ﬂexible distribution network
Rui Wang1,6, Haoran Ji1,6, Peng Li
1
, Hao Yu
1
, Jinli Zhao1, Liang Zhao2,
Yue Zhou3, Jianzhong Wu
3, Linquan Bai4, Jinyue Yan
5 & Chengshan Wang1
The ﬂexible distribution network presents a promising architecture to
accommodate highly integrated distributed generators and increasing loads in
an efﬁcient and cost-effective way. The distribution network is characterised
by ﬂexible interconnections and expansions based on soft open points, which
enables it to dispatch power ﬂow over the entire system with enhanced con-
trollability and compatibility. Herein, we propose a multi-resource dynamic
coordinated planning method of ﬂexible distribution network that allows
allocation strategies to be determined over a long-term planning period.
Additionally, we establish a probabilistic framework to address source-load
uncertainties, which mitigates the security risks of voltage violations and line
overloads. A practical distribution network is adopted for ﬂexible upgrading
based on soft open points, and its cost beneﬁts are evaluated and compared
with that of traditional planning approaches. By adjusting the acceptable
violation probability in chance constraints, a trade-off between investment
efﬁciency and operational security can be realised.
A distribution network serves as a critical infrastructure that delivers
electricity directly to customers in a power system1. Owing to the low-
carbon transformation in energy ﬁeld2, the distribution network is
developing into a public platform that fulﬁls diversiﬁed user demand
and enables clean energy generation3. Distribution network planning
aims to satisfy the development of sources and loads while ensuring
system security over a period by allocating various resources effec-
tively and economically4. In recent years, conventional distribution
networks have been inundated with signiﬁcant challenges5. For
example, renewable energy sources such as distributed photovoltaics
(PVs) are widely integrated into distribution networks6, and electric
vehicles (EVs) are developing rapidly as an emerging load demand7.
Considering China’s statistics as an example, the cumulative installed
capacity of distributed PVs increased by 46.61% year-on-year to
157.62 million kW in 20228, and the number of new energy vehicles
reached 13.1F million, with a year-on-year increase of 67.13%9. The
radial structure of a conventional distribution network renders it
difﬁcult to manage the bidirectional power ﬂow caused by large-scale
distributed generators (DGs) and increased loads10. In addition, the
inherent volatility originating from the sources and loads inevitably
results in voltage violations, line overloads and other security issues in
distribution networks11. Nevertheless, traditional planning approaches,
such
as
constructing
new
substations
and
expanding
feeder
capacities12, have low asset utilisation because of their insufﬁcient
ﬂexibility and are becoming increasingly unaffordable for imple-
mentations in a well-developed urban grid. Therefore, a novel archi-
tecture for distribution networks and the corresponding planning
methodology are required.
As a typical ﬂexible distribution device, the soft open point (SOP)
offers multiple advantages, such as spatial power ﬂow regulation and
real-time responses to variations13. Based on SOPs, a ﬂexible distribu-
tion network (FDN) has been established, which presents a promising
architecture to accommodate diverse elements and address the
source-load uncertainties in a more efﬁcient and cost-effective
Received: 2 September 2023
Accepted: 15 May 2024
Check for updates
1Key Laboratory of Smart Grid of Ministry of Education, Tianjin University, Tianjin 300072, China. 2State Grid Tianjin Electric Power Company, Tianjin 300010,
China. 3School of Engineering, Cardiff University, Cardiff CF24 3AA, UK. 4Department of Electrical Engineering and Computer Science, University of
Tennessee, Knoxville 37996, USA. 5School of Sustainable Development of Society and Technology, Mälardalen University, Västerås 721 23, Sweden. 6These
authors contributed equally: Rui Wang, Haoran Ji.
e-mail: lip@tju.edu.cn; tjuyh@tju.edu.cn
Nature Communications|   (2024) 15:4576 
1
1234567890():,;
1234567890():,;



<!-- page 2/14 -->

manner14. In FDNs, feeders do not operate in isolation; however, fee-
ders that have complementary resources or suffer from violations can
be interconnected ﬂexibly15. With the powerful regulation of SOPs, an
FDN can operate in closed loop and exchange energy across regions16.
In addition, the common DC bus of SOP can serve as an interface for
future expansion, which enables the topological evolution of FDN to
satisfy the growth of sources and loads17. Therefore, in contrast to
conventional distribution networks, the FDN exhibits a meshed
architecture characterised by ﬂexible interconnections and expan-
sions based on SOPs, thereby providing enhanced controllability and
compatibility for emerging demands. The potential of FDNs to balance
energy generation and consumption between areas is exploited, and
the random ﬂuctuations in FDNs can be better alleviated, as illustrated
in Fig. 1.
The grid updating and the development of DG facilities and EV
charging stations (EVCSs) require a considerable amount of time,
lasting for years or even decades. As a result, FDN planning entails a
phased approach for reinforcement of the distribution network18. The
terminal number and converter capacity of SOPs can expand by
stage19, which enables the conﬁguration of SOPs to adapt to demand
changes. The investment cost can be reasonably assigned to each
planning stage, ensuring the consistency of FDN planning and avoiding
investment reset. Hence, the dynamic evolution of FDN topology
needs to be considered when decisions are required for long-term
planning.
The FDN planning is conducted from the perspective of power
companies, who aim to optimize the siting and sizing of SOPs for the
distribution network to improve its hosting capability of EVCSs and
PVs. The increasing EVCSs and PVs will change the power ﬂow of dis-
tribution networks, which affects the location and capacity of SOPs20.
Thus, the power companies have the motivation to perform a coor-
dinated planning of SOPs, EVCSs, and PVs, and the FDN planning
model should accommodate the allocation strategy of EVCSs and PVs.
On the other hand, as the EVCSs and PVs in distribution networks are
invested and built by public stakeholders, the planning schemes of
EVCSs and PVs are provided as guidance and suggestions for them.
Therefore, the coordinated planning of SOPs, EVCSs and PVs to max-
imise the overall social beneﬁts is investigated in this paper, which
provides comprehensive planning guidance for power companies,
energy suppliers and users in distribution networks. To ensure that the
FDN planning strategy satisﬁes the security requirements in actual
operations, the planning method also needs to incorporate the
uncertainties of the sources and loads21.
The motivation behind this work is to explore and design an
architecture of distribution networks based on SOPs with the inte-
gration of high penetration of DGs and ﬂexible loads. The paper
highlights the ﬂexible regulation and interconnection capabilities of
SOPs in spatial dimension, which enables an interconnected and
extensible
architecture
for
distribution
networks.
The
ﬂexible
upgrading of the distribution network can enhance its energy man-
agement and DG hosting capability22, making it a more cost-effective
alternative to constructing new substations or feeders. Therefore, the
speciﬁc questions that we aim to address are, how to develop a suc-
cessive FDN planning strategy over a long duration, and how to
determine the siting and sizing of SOPs, EVCSs and PVs simultaneously,
while considering source-load uncertainties.
The contributions of this paper are summarised as follows.
(1) A multi-resource dynamic planning method of FDNs is pro-
posed, in which the conﬁguration of SOPs, PVs and EVCSs is coordi-
nated over a long-term planning period. The ﬂexible reinforcement of
the FDN can be implemented in multiple stages, and favourable cost
beneﬁts can be achieved compared with the traditional planning
approach.
(2) In the FDN planning model, a probabilistic framework is
established to address the strong source-load uncertainties. The
security risks are formulated by chance constraints, and the stochastic
nonlinear optimisation model is effectively solved based on the
modiﬁed iterative algorithm. By adjusting the acceptable violation
probability in chance constraints, a trade-off between investment
efﬁciency and operational security can be obtained.
Results
A probabilistic framework for FDN planning
To address the uncertainties stemming from the sources and loads in
FDN planning, a probabilistic framework is established, as shown in
Fig. 2. We classify the framework into ﬁve main parts; FDN modelling,
chance-constrained programming, uncertainty quantiﬁcation, uncer-
tainty propagation, and modiﬁed iterative algorithm.
Load/DG increases
Electric vehicle
Photovoltaic
Wind turbine
Soft open point
Energy storage
Substation
Signal tower
Security alert
Conventional distribution network with integration of DGs and EVs
Flexible distribution network based on SOPs
SOP
SOP
Fig. 1 | Illustration of conventional and ﬂexible distribution networks with
highly integrated DGs and EVs. The conventional distribution network used to be
built in a radial structure, especially with multi-sectioned or double-loop
enhancement in urban grids. This structure is generally adopted for unidirectional
power ﬂow from generators to loads. When DGs and loads increase as time pro-
gresses, the conventional distribution network is threatened by security risks, such
as voltage violations and line overloads. However, in FDNs, ﬂexible
interconnections between feeders are established based on SOPs. The sources and
loads in different areas are better coordinated, and the stochastic power ﬂow of the
entire system is regulated more efﬁciently. Owing to its ability to accommodate
large-scale DGs and EVs, the meshed architecture of an FDN offers the potential to
establish an eco-friendly power supply system in an economical and efﬁcient
manner.
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
2



<!-- page 3/14 -->

FDN modelling is performed to mathematically describe the
operation and planning mechanisms of FDN. Security risks are for-
mulated by chance constraints. Compared with the multi-scenario
analysis23 and robust optimization method24, chance-constrained
programming can probabilistically characterise the uncertainties in
FDNs, and allow a speciﬁed degree of constraint violations25, thus
enabling a trade-off between investment costs and operational secur-
ity. Next, uncertainty quantiﬁcation is performed to model the random
variables as inputs involved in the chance constraints26. Uncertainty
propagation is applied to obtain the statistical characteristics of FDN
states, such as nodal voltages and branch currents27, which are gen-
erally subjected to security guidelines.
Additionally, a modiﬁed iterative algorithm is developed to solve
the chance-constrained FDN planning model. In this algorithm, the
deterministic model with iterative formats is established by correcting
the margins of security constraints based on the acceptable violation
probability, which can be solved efﬁciently by commercial solvers in
each iteration. Margin corrections are obtained via a sampling
approach28 that can manage arbitrary random inputs without the
assumption of symmetric distributions.
Practical distribution network
A modiﬁed practical distribution network29 is adopted to verify the
effectiveness of FDN planning. The case includes 11 feeders of 11.4 kV,
and the structural diagram is illustrated in Supplementary Fig. 1. The
planning period is 20 years and is divided into four stages. According
to the annual growth rate of conventional load, and EV and PV pene-
trations for each stage, the allocation of SOPs, EVCSs and PVs can be
determined to accommodate the expected capacity of the sources
and loads.
Price is a key factor that affects planning decisions. The prices
associated with equipment investment, land exploitation, line con-
struction, and electricity purchase are listed in Supplementary Table 1.
The prices of land exploitation and line construction are assumed to
increase over the planning horizon since the available urban space is
gradually occupied. However, the prices of equipment and electricity
are expected to decrease as manufacturing and technology advance
further.
The maximum capacities of the candidate nodes for EVCS
and PV are 2 MVA and 3 MVA, respectively. The power factor of the
PV converter is 0.95. Considering that the efﬁciency of converter
has reached > 98%30, the loss factor of SOP converter is set to 0.0231.
The maximum converter capacity of a single SOP is 10 MVA,
and the unit module capacity is set to 10 kVA. The lower and upper
limits of nodal voltage are set as 0.95 and 1.05 p.u., respectively. The
rated current of the distribution network is 400 A, with a maximum
load rate of 1.0. The maximum number of iterations kmax = 30, the
sample
size
N = 20,000,
and
the
acceptable
violation
prob-
ability γ = 5%.
To obtain the planning results of the practical distribution net-
work, the proposed planning method is applied, which is formally
speciﬁed in the Methods section. Programs are executed using Python
3.7 on a computer with an Intel Core i7-9700 3 GHz CPU and 64 GB
RAM. In addition, a cost-beneﬁt analysis is conducted and compared
with that of traditional planning approaches, where the results
demonstrate that ﬂexible upgrading offers greater economic advan-
tages. To elucidate the efﬁciency of the iterative algorithm, the con-
vergence of security risks in FDNs to a predeﬁned level is analysed.
Finally, the effect of the acceptable violation probability on planning
results is investigated.
Planning strategy formulation
With the consideration of source-load uncertainties, ﬁve cases are
designed for FDN planning, and their planning results and cost beneﬁts
are further analysed.
Case I: The multi-resource dynamic coordinated planning of FDN
is performed.
Case II: The coordinated FDN planning is performed without stage
division.
Case III: The energy storage systems (ESSs) planning is performed
in the distribution network.
Case IV: The traditional planning method is performed, where the
larger-capacity lines and transformers are invested for overloaded
feeders.
Case V: The distribution network is not reinforced with the
increase of sources and loads.
Fig. 2 | Probabilistic framework for FDN planning. a A multi-resource dynamic
coordinated planning model for FDNs is established, where the topology evolution
of SOP and the coordination of PV and EVCS are considered. b The security risks of
FDN, including voltage violations and line overloads, are formulated by chance
constraints. c The source-load uncertainties in FDNs are quantiﬁed based on
Gaussian mixture model without relying on the assumption of typical probability
functions, and the correlations between uncertainties are addressed by Nataf
transformation. d The uncertainty propagation in FDNs can be realised based on
Monte Carlo simulation, and the low-rank approximation method can be adopted
as an alternative to improve computational efﬁciency. e The stochastic optimisa-
tion model is solved by the modiﬁed iterative algorithm. f The planning strategy for
FDN is formulated.
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
3



<!-- page 4/14 -->

For Case I, the evolution of FDN throughout the planning period is
shown in Fig. 3, and the siting and sizing of SOPs, EVCSs and PVs are
given in Table 1. It can be observed from the results when PV and EV
penetrations are low in the initial stage, no SOP is planned and the
distribution network retains its original structure. In particular, EVCSs
are preferentially allocated to a few positions owing to the land
exploitation costs, whereas PVs exhibit a more decentralised proﬁle to
avoid over-centralization that could lead to violations. In the sub-
sequent stages, the adoption of PVs and EVs further increases, result-
ing in more investment in purchasing converters and constructing
charging stations.
In Stage II, a two-terminal SOP is planned owing to the heavy loads
on Feeders A and I. The converter capacity of SOP in this stage is
primarily used to provide reactive power compensation. Power
transmission lines of the SOP are built along geographical boundaries,
among which the existing switch line (12, 72) is directly reused without
incurring new construction costs. In Stage III, the SOP evolves into
three-terminal, enabling ﬂexible interconnection among Feeders A, I,
and K. The converter capacity of each SOP terminal also increases to
transfer more active power between the feeders. In Stage IV, the ori-
ginal SOP develops into a four-terminal structure owing to the newly-
installed PVs in Feeder H. In addition, a new two-terminal SOP is con-
structed between Feeders D and E, with the existing switch (29, 39)
reused directly. Subsequently, the excess power generated by PVs is
transferred to other feeders, ensuring that the system achieves 100%
localised PV hosting within the predeﬁned risk level.
Driven by the large-scale integration of PVs and EVs, the conven-
tional distribution network with a multi-sectioned structure has gra-
dually evolved into a new form with ﬂexible interconnections based on
multi-terminal SOPs. Because the dynamic expansion of SOPs and
coordinated planning of PVs and EVCSs are taken into account, the
investment is deferred, and the utilization efﬁciency is improved. The
present value of the annualised costs for each stage is shown in Table 2,
and the total cost is 40.70 × 106 CNY.
Cost-beneﬁt analysis
The economy efﬁciency of the above cases in alleviating security risks
is further investigated. The costs of different planning schemes are
illustrated in Fig. 4.
In Case II, the FDN planning is conducted within one stage, where
the network evolution and the gradual growth in equipment capacity
are not considered. The costs are calculated at current prices, and the
A
B
C
D
E
H
K
G
J
0.16MVA
0.04MVA
*
0.81MVA
0.64MVA
0.79MVA
*
0.81MVA
1.06MVA
1.76MVA
*
3.34MVA
0.96MVA
0.97MVA
Stage II
Stage IV
Stage I
Stage III
Substation
Load point
Feeder section
Tie line
Block boundary
Unit length: 1km
PV allocation
EVCS allocation
Soft open point
F
I
A
B
C
D
E
H
K
G
J
F
I
A
B
C
D
E
H
K
G
J
F
I
A
B
C
D
E
H
K
G
J
F
I
*
Reused line
*
Fig. 3 | Multi-resource dynamic coordinated planning scheme of FDN. The
annual growth rates of conventional load are 2%, 1.5%, 1% and 0.5% in Stage I-IV,
respectively. EV penetration is set to 5%, 15%, 20% and 24%, and that of PV is set to
15%, 30%, 50% and 65% in Stage I-IV, respectively. Driven by the increase of sources
and loads, the radial structure of the original distribution network evolved into a
ﬂexible interconnected form based on SOPs. Blue and green dots respectively
denote the siting of EVCSs and PVs. The red annotations denote SOP converter
capacities. Based on the coordinated planning of EVCSs and PVs, a four-terminal
SOP (connecting Feeders A, H, I and K) and a two-terminal SOP (connecting Feeders
D and E) are established in the ﬁnal stage.
Table 1 | Planning results of Case I
Stage
SOP allocation position (capa-
city /MVA)
EVCS allocation position (capa-
city /MVA)
PV allocation position (capacity /MVA)
I
-
49(1.65)
10(2.87) 24(0.45) 39(0.79) 40(0.04) 55(0.79) 64(0.31)
II
7-72(0.16, 0.04)
28(2.00) 49(2.00) 68(1.96)
10(3.00) 24(1.63) 29(1.92) 39(1.81) 40(0.04) 55(2.54) 60(0.15) 63(0.70)
64(0.55) 76(0.23)
III
7-72-83(0.81, 0.64, 0.79)
28(2.00) 49(2.00) 68(2.00)
72(1.60) 83(1.27)
10(3.00) 11(3.00) 24(2.78) 29(3.00) 39(2.81) 40(0.04) 55(3.00)
60(1.52) 63(0.74) 64(0.58) 76(2.88)
IV
7-64-72-83(0.81, 3.34, 1.06, 1.76) 29-
39(0.96, 0.97)
28(2.00) 49(2.00) 68(2.00) 72(2.00)
82(1.48) 83(2.00)
10(3.00) 11(3.00) 24(3.00) 29(3.00) 39(3.00) 40(2.72) 55(3.00)
60(3.00) 63(3.00) 64(3.00) 76(3.00)
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
4



<!-- page 5/14 -->

investments are paid at the initial to meet the needs over the entire
planning period. The total cost is the highest at 90.48 × 106 CNY.
In Case III, ESSs are planned to ensure the safe operation of the
distribution network. The ESS investment is used to build the site and
purchase converters and batteries. The allowed minimum and max-
imum state of charge (SOC) of ESSs are set to 10% and 90%. Assume
that the battery of ESS can be charged or discharged by its maximum
available capacity, and the sequential energy constraints are not con-
sidered, which will result in a smaller capacity investment cost of the
battery. However, conﬁned to the radial structure of the distribution
network, ESSs need to be installed independently at each overrunning
feeder, thus causing a higher site construction cost. The total cost of
planning ESSs is larger than that of planning SOPs in Case I, indicating
that the ﬂexible interconnected structure based on SOPs is econom-
ically promising for it offers resource sharing among feeders.
In Case IV, the feeders that violate security criteria in each stage
are identiﬁed to be reinforced. In this case, Feeders A and I in Stage II,
Feeder K in Stage III, and Feeders E and H in Stage IV are reinforced.
The maximum capacity of the expanded line is 1.5 times that of the
original line, and the cost of expanding the line per unit length is thrice
that of line construction32. Additionally, the transformer capacity of
the reinforced feeder needs to be expanded as well. The operational
risk of the distribution network is reduced by planning larger-capacity
lines and transformers. However, inadequate ﬂexibility in capacity
allocation leads to higher expansion costs. The total cost reaches
43.63 × 106 CNY.
Planning different resources to enhance the ﬂexibility of the dis-
tribution network mayincur additional investment expenses; however,
it can reduce operational costs, such as those associated with system
losses, voltage violations, and line overloads. The results of Case V
show that not implementing planning measures saves the investment
cost, but voltage violations and line overloads severely jeopardise the
safe operation of the distribution network, thus resulting in a higher
penalty cost.
In summary, a dynamic coordinated FDN planning method is
adopted in Case I, which alleviates operational risks while maintaining
a lower investment cost. The total cost reduces by 55.02%, 14.06%,
6.72%, and 23.08% as compared with those of Case II-V, respectively.
The results indicate that the ﬂexible upgrading based on SOPs in a
multi-stage framework offers better economy efﬁciency for managing
security risks in distribution networks.
Probabilistic analysis in iterative solution
There is no analytical representation for chance constraints. Direct
methods involve high-dimensional integral operations. Therefore, a
modiﬁed iterative algorithm is executed to obtain an efﬁcient solution
for non-linear systems, where the predeﬁned risk margin and com-
putational performance are guaranteed.
First, the source-load uncertainties in FDNs are quantiﬁed. The
probability density functions of conventional load, EVCS charging load
and solar radiation are established using Gaussian mixture models
(GMMs) based on historical observations33–35, as shown in Supple-
mentary Fig. 2. The probability density functions of sources and loads
are not symmetric and cannot be accurately described by any typical
distributions, like Normal, Beta or Weibull distribution. In addition, the
dependences between uncertainties are also considered, which reﬂect
the variation consistency of random variables and are generally deﬁned
by a correlation matrix. Specially, the randomness of the PV output is
mainly owing to the volatility of solar radiation, so we primarily
quantify the uncertainty in solar radiation for further calculations36.
Based on the quantiﬁed source-load uncertainties, the probability
density functions of FDN states are obtained at each iteration, which
reﬂect operational proﬁles and provide statistical data for iterative
corrections. In the 0-th iteration, the probability density functions of
Table 2 | Planning cost of Case I
Stage
Investment cost (106CNY)
Operational cost (106CNY)
Sum
(106CNY)
SOP
EVCS
PV
System loss
Line
overload
Voltage
violation
Land
exploitation
Converter
purchase
Line
construction
Land
exploitation
Converter
purchase
Converter
purchase
I
0.00
0.00
0.00
3.00
1.32
4.20
2.36
0.11
0.66
11.64
II
2.17
0.07
0.15
4.35
1.61
2.73
1.37
1.15
1.12
14.70
III
0.00
0.31
0.35
3.08
0.45
1.66
0.84
2.13
0.15
8.97
IV
1.20
0.32
0.23
1.20
0.13
0.45
0.58
1.18
0.10
5.38
Total
4.80
15.13
9.04
5.15
4.56
2.02
40.70
Fig. 4 | Costs of different planning cases. Under a moderate investment cost for
establishing a ﬂexible interconnected structure based on SOPs, the operational
penalty cost for voltage violations and line overloads can be reduced. Compared
with Case II, the multi-stage planning framework can delay investment. Compared
with Case III, the resource sharing is promising based on the ﬂexible interconnected
structure. Compared with Case IV, the proposed planning method exhibits better
ﬂexibility for expansion. Compared with Case V, the proposed planning method
effectively addresses the security issue caused by the integration of PVs and EVCSs.
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
5



<!-- page 6/14 -->

node 83 voltage on Feeder K, node 64 voltage on Feeder H, and line
(109, 65) load rate on Feeder I over the entire planning horizon are
selected for illustrations, as shown in Fig. 5. It can be found that there is
an under-voltage violation risk at node 83 due to the heavy load of
Feeder K, an over-voltage violation risk at node 64 due to the PV
integration of Feeder H, and an overloading risk at line (109, 65). In
addition, the variances of voltages and load rates progressively
increase by stage, implying that the random ﬂuctuations of FDN states
are magniﬁed and the operational proﬁles are exacerbated with the
growing penetration of PVs and EVCSs.
To solve the stochastic optimisation for FDN planning, the mod-
iﬁed iterative algorithm is proposed in the paper. To analyse the per-
formance of the solution algorithm, a comparison between the general
and the modiﬁed iterative algorithm is conducted. The solution results
obtained by the two algorithms are almost the same, but the general
algorithm necessitates 21 iterations to converge, which requires
57.46 h. However, using the modiﬁed iterative algorithm, only 6
iterations are necessitated to attain convergence, which requires
9.40 h. In each iteration, the deterministic optimisation model is
solved within 49.93 min on average, and optimal solution is guaran-
teed with the maximum gap smaller than tolerance 1e-3. The com-
parison indicates that the modiﬁed iterative algorithm has a better
performance, and its improvements are described in detail mathe-
matically in the Methods section. Moreover, by using low-rank
approximation to replace Monte Carlo simulation for uncertainty
propagation, the convergence time can be further reduced to 5.53 h.
As shown in Fig. 6, the violation probabilities exceed 30% when no
SOP is implemented at the initial iteration. By correcting the upper and
lower margins of security constraints iteratively, the planning strategy
is resolved and the violation risks under the solution gradually con-
verge to a predeﬁned level. In this case, after four iterations, the risks of
voltage violations and line overloads are controlled within 5%.
Scenario analysis
Four scenarios are designed with acceptable violation probabilities of
3%, 5%, 10%, and 15%. The dynamic planning schemes for FDN are
shown in Fig. 7. When the acceptable violation probability is lower, the
SOP is constructed in the earlier stage with a larger converter capacity.
For example, when γ = 3%, a two-terminal SOP is built in Stage I to
address the under-voltage risk caused by the heavy load at the end of
Feeder A. When γ = 5% in Case I, SOP planning begins in Stage II. When γ
= 10% and 15%, the planning of SOP is postponed to Stage III. In the ﬁnal
stage, four- and three-terminal SOPs are built when γ = 3%, and Feeders
A, B, E, H, I and K are interconnected together for resource sharing and
power regulations. When γ = 5% and 10%, four- and two-terminal SOPs
are planned, whereas three- and two-terminal SOPs are constructed
when γ = 15%. the total SOP converter capacities of the four scenarios
are 9.54, 8.90, 7.98, and 6.35 MVA, respectively.
The cost beneﬁts of the above scenarios are further analysed, as
shown in Fig. 8. The acceptable violation probability of FDN has a
signiﬁcant impact on the cost. A lower permitted risk corresponds to a
more conservative planning scheme, along with a higher investment
cost, but a lower operational penalty cost. When γ = 3%, the total cost
of FDN planning is minimised. In practical engineering, the trade-off
between economy and security can be achieved by adjusting the
acceptable violation probability based on actual demands.
Discussion
The ﬂexibly interconnected and extensible architecture enables FDN
to dispatch power ﬂow over the entire system in closed-loop opera-
tion. This architecture is based on SOPs that provide strong controll-
ability for wide-area active power transfer and local reactive power
compensation. Consequently, the FDN offers a promising way to rea-
lize capacity expansion and low-carbon transformation in power sys-
tems with highly integrated PVs and EVs. The topology of distribution
network is progressively updated and enhanced by segmenting the
long planning period into several stages. The establishment of FDN will
take years or even decades to fulﬁl the developing needs of users. A
four-terminal SOP may evolve into a six- or eight-terminal structure
that encompasses more power supply areas. Compared with tradi-
tional planning approaches, such as constructing new substations and
expanding the capacity of feeders, the ﬂexible evolution of FDN
enables signiﬁcant cost reduction.
SOP takes part as the key infrastructure for the structure evolution
of distribution networks, which is the priority to be considered in the
FDN planning. Other controllable resources, such as energy storage
systems and demand responses, can be further considered in sub-
sequent research. In addition, the common DC bus of SOP is a
Fig. 5 | Probability density functions of nodal voltages and line load rates. At
each iteration, an FDNplanning strategy isformulated,and the operational states of
FDN are obtained by uncertainty propagation. The violation probabilities of nodal
voltages and line load rates are identiﬁed, then the corrected margins are adopted
for solving the FDN planning model at the next iteration. Compared with Monte
Carlosimulation (MCS), low-rank approximation (LRA) method can produce similar
results, but with a lower computational burden. a Probability density functions of
node 83 voltage. b Probability density functions of node 64 voltage. c Probability
density functions of line (109, 65) load rate.
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
6



<!-- page 7/14 -->

Fig. 6 | Violation risks of FDN during iterations. FDN planning strategy is updated
iteratively with the corrected margins of security constraints, thus ensuring the
violation risks converge to the predeﬁned level. Convergence efﬁciency is
improved using the modiﬁed iterative algorithm. The x-axis ticks represent the
indices of stage. At each stage interval (divided by grey dashed lines), the violation
risks of nodal voltages or line currents are illustrated, with labels (A, B, ..., K) at the
top indicating corresponding feeder names. The y-axis ticks represent the violation
risks. The initial violation risks (blue lines) are rapidly reduced to the vicinity of 5%
(dark red dashed line) only after one iteration (orange lines). Then, slight reduc-
tions of violation risks are conducted during later iterations. The iteration stops
(red lines) when all violation risks are controlled below the acceptable probability.
a Violation risk of the lower bound for voltages. b Violation risk of the upper bound
for voltages. c Violation risk of the upper bound for currents.
Stage I
Stage II
Stage III
Stage IV
A
B
C
D
E
F
H
K
G
I
J
G
A
H
I
B
C
K
J
E
D
F
A
B
C
D
E
F
H
K
G
I
J
(a)¤=3%
A
B
C
D
E
F
H
K
G
I
J
(b)¤=5%
G
A
H
I
B
C
K
J
E
D
F
G
A
H
I
B
C
K
J
E
D
F
A
B
C
D
E
F
H
K
G
I
J
A
B
C
D
E
F
H
K
G
I
J
(c)¤=10%
G
A
H
I
B
C
K
J
E
D
F
G
A
H
I
B
C
K
J
E
D
F
G
A
H
I
B
C
K
J
E
D
F
G
A
H
I
B
C
K
J
E
D
F
A
B
C
D
E
F
H
K
G
I
J
A
B
C
D
E
F
H
K
G
I
J
A
B
C
D
E
F
H
K
G
I
J
A
B
C
D
E
F
H
K
G
I
J
(d)¤=15%
G
A
H
I
B
C
K
J
E
D
F
G
A
H
I
B
C
K
J
E
D
F
G
A
H
I
B
C
K
J
E
D
F
G
A
H
I
B
C
K
J
E
D
F
G
A
H
I
B
C
K
J
E
D
F
*
*
*
G
A
H
I
B
C
K
J
E
D
F
G
A
H
I
B
C
K
J
E
D
F
A
B
C
D
E
F
H
K
G
I
J
G
A
H
I
B
C
K
J
E
D
F
*
A
B
C
D
E
F
H
K
G
I
J
G
A
H
I
B
C
K
J
E
D
F
*
A
B
C
D
E
F
H
K
G
I
J
G
A
H
I
B
C
K
J
E
D
F
*
A
B
C
D
E
F
H
K
G
I
J
G
A
H
I
B
C
K
J
E
D
F
*
A
B
C
D
E
F
H
K
G
I
J
G
A
H
I
B
C
K
J
E
D
F
*
A
B
C
D
E
F
H
K
G
I
J
G
A
H
I
B
C
K
J
E
D
F
*
A
B
C
D
E
F
H
K
G
I
J
G
A
H
I
B
C
K
J
E
D
F
*
A
B
C
D
E
F
H
K
G
I
J
G
A
H
I
B
C
K
J
E
D
F
*
A
B
C
D
E
F
H
K
G
I
J
*
G
A
H
I
B
C
K
J
E
D
F
*
A
B
C
D
E
F
H
K
G
I
J
*
G
A
H
I
B
C
K
J
E
D
F
*
A
B
C
D
E
F
H
K
G
I
J
*
G
A
H
I
B
C
K
J
E
D
F
*
A
B
C
D
E
F
H
K
G
I
J
*
G
A
H
I
B
C
K
J
E
D
F
*
*
Fig. 7 | Planning results of FDN with different acceptable violation prob-
abilities. The stage to begin ﬂexible reconstruction and the ﬁnal evolutionary
topology of the distribution network differ in terms of the acceptable violation
probabilities. Owing to adapting the same penetrations ofsources and loads in each
stage, the allocations of PVs and EVCSs in the four scenarios are almost the same.
The feeders connected by the same SOP are represented in the same colour. When
γ = 3%, Feeder H is connected by two SOPs in Stage IV simultaneously, which is
represented in an additional colour. a γ = 3%. b γ = 5%. c γ = 10%. d γ = 15%.
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
7



<!-- page 8/14 -->

compatible interface that provides access to DC loads, DC sources, and
energy storage systems. In summary, FDN is both eco-friendly and
economical to host emerging elements with diverse characteristics.
To address the high-dimensional uncertainties derived from the
sources and loads in FDNs, we establish a probabilistic framework.
Violation risks are formulated by chance constraints, and a modiﬁed
iterative algorithm is developed to solve the chance-constrained
optimisation problem. In our example, the solution can be obtained
within hours via a few iterations, and the security risks are reduced to
an acceptable level. In practice, the decision maker can modify the FDN
planning strategy by adjusting the acceptable threshold to achieve a
balance between economy and security.
With the orientation of coordinated planning results, the EVCSs
and PVs constructed atthe suggested positions will be better regulated
and supported by SOPs to ensure the secure hosting of renewable
generation and charging load. Therefore, it is beneﬁcial to formulate
planning guidance for individual users, especially for the energy sup-
pliers that make proﬁts by providing public generating and charging
services. With the simultaneous consideration of grid, source and load
in a multi-stage planning model, the planning guidance exhibits high
compatibility for all participants in the distribution network. In this
way, the construction of distribution network can cover the interests
of multiple parties and offer better power supply service in practical
operations. At the same time, note that the energy suppliers and users
are not mandated to follow the allocation result of sources and loads.
But the user-built EVCSs and PVs may bring operational violations to
the distribution network, resulting in the inability to plug themselves
into the grid. Under such conditions, users have to pay additional costs
to dispatch energy storage systems or other controllable resources for
regulations, while wasting the public services provided by conﬁg-
ured SOPs.
An additional case is investigated as Case VI, where the siting and
sizing of SOPs are formulated without the consideration of increasing
EVCSs and PVs, while the allocation of EVCSs and PVs is determined
and invested by users. Compared with Case I, the number and capacity
of SOP in Stage III-IV are smaller, and SOP investment cost is reduced
by 9.17%. However, for a stochastically generated allocation of EVCSs
and PVs, the voltage violation risk of the distribution network in Stage
II-IV exceeds 15%, while the line overload risk exceeds 25%. As a result,
the operational cost for violations increases by 4.70 times, and the
total cost increases by 3.31 times. The case indicates that if FDN plan-
ning is not performed in a coordinated framework, the regulation
ability of SOPs cannot be fully utilized, and the randomness caused by
sources and loads will exacerbate the operation of distribution net-
work. The separate decision-making leads to worse economic out-
comes for the overall beneﬁt of society.
The coordinated planning method of FDN is essentially a multi-
objective optimization model. In this paper, the multiple interests are
formulated and normalized as costs, which can be summed as a single-
objective function in a straightforward way. Then, the FDN planning
model can be converted into a mixed-integer second-order conic
programming (MISOCP) problem, which can be solved effectively by
commercial solvers. In this sense, the proposed planning method is to
maximise social beneﬁts and achieve the overall economy efﬁciency
for power companies, energy suppliers, and users. As for multi-
objective optimization problems, the Pareto frontier is also known as a
promising approach, which provides a wide range of alternative solu-
tions for decision-making. In the Pareto frontier, each objective is
considered as equally good. Additionally, game theory is also suited to
solving multi-stakeholder problems based on Nash equilibrium, where
the interests of power companies, energy suppliers, and users are
optimized simultaneously. This paper focuses on how to establish a
ﬂexible interconnected architecture of FDN based on SOPs, and the
handling of multi-objective optimization will be further studied in
future works due to the limited space.
The simultaneous use of SOP and line reinforcement is further
investigated as Case VII. In a feasible planning scheme, Feeder K is
reinforced in Stage III, and a two-terminal SOP is planned in Stage II and
evolves into a four-terminal structure in the ﬁnal stage with the coor-
dination planning with EVCSs and PVs. Compared with Case I, its
investment cost (29.72 × 106 CNY) is larger, but its operational cost
(9.26 × 106 CNY) is much smaller. As a result, the total cost of Case VI is
reduced by 1.71 × 106 CNY (reduction of 4.20%), which exhibits
potential economy efﬁciency.
Under failure conditions, the loads and DGs on the faulted feeder
can be transferred via SOPs without incurring any power outages. The
interconnected architecture has the potential to improve the load
recovery in FDNs. However, this implies that the transfer capacity of
SOP needs to be further optimised. FDN planning considering relia-
bility enhancement will be investigated in future studies.
The paper mainly studies the method of how to establish a ﬂexibly
interconnected and extensible architecture of the distribution net-
work based on multi-terminal SOPs, which has laid the foundation for
the realisation of the honeycomb FDN37. As shown in Fig. 7, the power
supply areas are abstractly denoted as a couple of closely packed
hexagons, thus representing a primary visualisation of the honeycomb
FDN. In our prospect, the honeycomb distribution system may be an
advanced FDN structure in the future, which enables a more robust
grid, by segmenting it into largely autonomous cells. It can be applied
to the current grid step by step and may contribute to increasing the
penetration of renewable energy resources. The decision maker will
focus on the planning of ﬂexible interconnections and expansions
from a global perspective, whereas the sources, loads, and energy
storage systems are self-organised in each local area.
We conclude that the multi-resource dynamic and coordinated
planning method of FDN is feasible and advantageous. The probabil-
istic framework aimed at addressing source-load uncertainties effec-
tively conﬁnes security risks within a predeﬁned range. The case study
demonstrates that the proposed iterative algorithm performs efﬁ-
ciently in solving chance-constrained programming problems. The
ﬂexible architecture and probabilistic planning method of FDN allow it
to host high-penetration PVs and EVs in power systems.
Methods
Solution procedure
The detailed procedure for solving the FDN planning model is given as
follows.
1) Input the distribution network parameters, and determine the
random variables and correlation matrix;
2) Quantify the source-load uncertainties based on Gaussian
mixture model in Eq. (1) and generate samples based on Nataf trans-
formation in Eq. (2);
3) Set iteration counter κ = 0;
4) Check whether κ is less than or equal to κmax. If satisﬁed, con-
tinue to Step 5; otherwise, proceed to Step 9;
Fig. 8 | Cost analysis of the scenarios with different acceptable violation
probabilities. Golden and red points respectively denote investment and total
costs, referring to the left y-axis. Blue points denote operational cost for system
loss, voltage violation, and line overload, referring to the right y-axis.
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
8



<!-- page 9/14 -->

5) Solve the deterministic planning model in Eq. (25) to obtain the
planning strategy, including the optimised allocation of SOPs, EVCSs
and PVs;
6) Execute uncertainty propagation to obtain the probabilistic
characteristics of nodal voltages and line currents;
7) Check whether all chance constraints satisfy the predeﬁned risk
level. If satisﬁed, proceed to Step 9; otherwise, continue to Step 8;
8) Update the bounds of the security constraints; update κ = κ + 1
and proceed to Step 4;
9) Record the solved planning strategy and calculate the
total cost.
Gaussian mixture model
The conventional load of residents, the charging load of EVCSs, and
the output of PVs are regarded as random variables in the FDN plan-
ning model, and their probability density functions can be formulated
by Gaussian mixture model as follows.
pðξÞ =
X
M
m = 1
πmN ξ; μm,Σm


ð1aÞ
X
M
m = 1
πm = 1
ð1bÞ
N ξ; μm, Σm


=
exp  1
2 ξ  μm

TΣ1
m ξ  μm




ﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃ
det 2πΣm


q
ð1cÞ
where M denotes the maximum number of components. πm denotes
the weighting factor. N ξ; μm,Σm


presents a Gaussian distribution
with mean vector μm and covariance matrix Σm. In addition, the
dependence between random variables is described by Pearson cor-
relation matrix.
Nataf transformation
Consider a n-dimensional random vector ξ = (ξ1, . . . , ξn) with correla-
tion matrix ρ, where element ρij denotes the correlation coefﬁcient
between variables ξi and ξj. With Nataf transformation38, a new random
vector ς = (ς1, . . . , ςn) in standard normal space and its correlation
matrix ρϕ can be obtained.
ςi = Φ1 Gi ξi




ð2aÞ
ρij =
Z Z G1
i
Φ ςi
 


 μi
σi
×
G1
j
Φ ςj
 


 μj
σj
× ϕ2 ςi,ςj,ρϕ
ij


dςidςj
ð2bÞ
where Gi( ⋅), G1
i ðÞ, μi and σi respectively denote the cumulative dis-
tribution, inverse cumulative distribution, mean and standard variance
of ξi. Φ( ⋅) and Φ( ⋅) respectively denote the cumulative distribution
and inverse cumulative distribution of univariate standard normal
distribution. ϕ2( ⋅) denotes the bivariate standard normal distribution.
Element ρϕ
ij denotes the correlation coefﬁcient between variables ςi
and ςj. Furthermore, the independent random vector ζ in standard
normal space can be obtained based on Choleskey decomposition.
ρϕ = LLT
ð3aÞ
ζ = L1ς
ð3bÞ
where L denotes the lower triangular matrix.
Low-rank approximation
Low-rank approximation is used to express the target response in
highly compressed formats as the sum of rank-one functions via
canonical decomposition.
Consider an independent random vector ξ = (ξ1, . . . , ξn) with
marginal distribution gi(i = 1, . . . , n), namely the probability density
functions of sources and loads established based on Gaussian mixture
models. The desired response h of FDN, such as the nodal voltage and
line current, can be formulated as follows.
h = f LRAðξÞ =
X
r
l = 1
blωlðξÞ =
X
r
l = 1
bl
Y
n
i = 1
vðiÞ
l
ξi
 
 
!
ð4Þ
where bl denotes the weighting factor. vðiÞ
l denotes the i-th dimensional
univariate function of the rank-one function ωl. In practice, vðiÞ
l
is
expanded on a polynomial basis
χðiÞ
q ,q 2 N
n
o
in practice, which is
orthogonal to the function gi. Thus, the rank-r approximation of h
results in the following form.
h =
X
r
l = 1
bl
Y
n
i = 1
X
θ
q = 0
zðiÞ
q,lχðiÞ
q ξi
 
 
!
 
!
ð5Þ
where χðiÞ
q denotes the q-th degree univariate polynomial in the i-th
random variable. zðiÞ
q,l is the coefﬁcient of χðiÞ
q
in the l-th rank-one
function, and θ is the maximum degree.
To determine the parameters in low-rank approximation, the
sequential correction-updating algorithm39 is employed. In addition,
to tackle the correlation between random variables, the inverse Nataf
transformation T 1ðÞ is introduced. The response h can be expressed
as h = f ðξÞ = f ðT 1ðζÞÞ, where ζ is sampled from independent standard
normal distributions.
Evolution of FDN planning
The number of terminals, and the siting and sizing of SOP
can be ﬂexibly designed in each stage. First, a set of available
nodes is determined for SOP connections. In this paper, the
terminal nodes of existing tie lines are selected as the available
nodes. Second, the topologies of SOP planning schemes are gen-
erated without exceeding the maximum number of SOP terminals,
and the length of the line to be reconstructed in each scheme is
calculated.
L = UNf
k = 1LðkÞ = UNf
k = 1UMf
τ = 2Lðk,τÞ
ð6aÞ
Lðk,2Þ = kjcrad Ωk


= 2


ð6bÞ
Lðk,3Þ = k0jcrad Ωk0


= 3,Ωk0  Ωk


ð6cÞ
Lðk,4Þ =
k
00jcrad Ωk
00


= 4,Ωk
00  Ωk
n
o
ð6dÞ
Li = kjΩk 3 i,8i 2 Ωs


ð6eÞ
where Ωs denotes the set of available nodes. k denotes the
scheme index. Ωk denotes the set of nodes in scheme k. Nf denotes
the number of schemes. Mf denotes the maximum number of
SOP terminals. L denotes the set of total schemes. Li denotes the set of
SOP planning schemes containing node i. LðkÞ denotes the set of
schemes evolved from scheme k, and Lðk,τÞ denotes the τ-terminal
SOP planning schemes in set LðkÞ. crad( ⋅) denotes the cardinality
of a set.
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
9



<!-- page 10/14 -->

Objective function of FDN planning
The FDN planning model is established to minimise the comprehen-
sive expense, including investment cost ϕCO
u
and operational cost ϕOP
u .
f = min
X
u2ΩU
X
y2ΩY
λyu εϕCO
u
+ ϕOP
u


ð7aÞ
λyu = ð1 + dÞ½ðu1ÞY + y
ð7bÞ
ε = dð1 + dÞL= ð1 + dÞL  1
h
i
ð7cÞ
where ΩU and ΩY denote the set of stages and years, respectively. Y
denotes the duration of each planning stage. y denotes the index of
years in each planning stage. ε denotes the capital recovery factor,
which share the construction costs equally to each year of the payback
period L. λyu denotes the present value coefﬁcient, which calculates the
present value of an annualized cost in terms of interest rate d.
The investment cost primarily includes the cost for building SOPs,
EVCSs, and PVs for land exploitation, converter purchases and line
construction. Meanwhile, the operational cost is mainly attributed to
network and SOP converter losses.
ϕCO
u
= ϕSOP,ST
u
+ ϕSOP,CT
u
+ ϕSOP,BR
u
+ ϕEVCS,ST
u
+ ϕEVCS,CT
u
+ ϕPV,CT
u
ð8aÞ
ϕSOP,ST
u
= cST
u
X
k2L
αk,u 
X
k2L
αk,u1
 
!
ð8bÞ
ϕSOP,CT
u
= cCT
u
X
k2L
SSOP
k,u 
X
k2L
SSOP
k,u1
 
!
ð8cÞ
ϕSOP,BR
u
= cBR
u
X
k2L
Dkαk,u 
X
k2L
Dkαk,u1
 
!
ð8dÞ
ϕEVCS,ST
u
= cST
u
X
i2Ωe
βi,u 
X
i2Ωe
βi,u1
0
@
1
A
ð8eÞ
ϕEVCS,CT
u
= cCT
u
X
i2Ωe
SEVCS
i,u

X
i2Ωe
SEVCS
i,u1
0
@
1
A
ð8fÞ
ϕPV,CT
u
= cCT
u
X
i2Ωg
SPV
i,u 
X
i2Ωg
SPV
i,u1
0
@
1
A
ð8gÞ
where ϕSOP,ST
u
, ϕSOP,CT
u
and ϕSOP,BR
u
denote the land exploitation, con-
verter purchase and line construction cost of SOP in stage u, respec-
tively. ϕEVCS,ST
u
and ϕEVCS,CT
u
denote the land exploitation and converter
purchase cost of EVCS in stage u. ϕPV,CT
u
denotes the converter pur-
chase cost of PV in stage u. cST
u , cCT
u
and cBR
u
denote the price of land
exploitation, converter purchase and line construction in stage u,
respectively. Ωe and Ωg denote the nodes available for EVCS and PV
installations, respectively. αk,u is a binary variable, indicating whether
SOP planning scheme k is selected in stage u. βi,u is a binary variable,
indicating whether the EVCS is constructed at node i in stage u. SSOP
k,u
denotes the converter capacity of SOP planning scheme k in stage u.
SEVCS
i,u
and SPV
i,u denote the converter capacity of EVCS and PV at node i in
stage u, respectively. Dk denotes the length of the line to be
constructed in SOP planning scheme k. The existing tie lines involved
in scheme k do not introduce new investment, which can be directly
utilised.
ϕOP
u = 8760 
ϕNET,LS
u
+ ϕSOP,LS
u


ð9aÞ
ϕNET,LS
u
= cSL
u
X
ij2Ωb
RijI2
ij,u
ð9bÞ
ϕSOP,LS
u
= cSL
u
X
k2L
X
i2Ωk
PSOP,LS
i,k,u
ð9cÞ
where ϕNET,LS
u
and ϕSOP,LS
u
denote the network loss and SOP converter
loss cost, respectively. cSL
u denotes the price of power loss in stage u,
which is generally assigned as electricity price. Rij denotes the resis-
tance of branch ij. Iij,u denotes the current magnitude of branch ij in
stage u. PSOP,LS
i,k,u
denotes the active power loss of SOP converter at node
i in scheme k in stage u.
Constraints of FDN planning
The investment constraints of SOP are formulated as follows. The same
terminalcan only be used in one SOP planning scheme. When a scheme
is determined in the previous stage, one of its evolutionary schemes
should be selected in the next stage. The converter capacity of SOP is
formulated as continuous variables for effective solutions. However,
considering the modularisation requirements, the indeed installed
SOP capacity is determined by rounding the corresponding variables
in the solution.
X
k2Li
αk,u ≤1
ð10aÞ
αk,u1 ≤
X
k02LðkÞ
αk0,u
ð10bÞ
X
k2Li
SSOP
i,k,u1 ≤
X
k2Li
SSOP
i,k,u
ð10cÞ
SSOP
k,u =
X
i2Ωk
SSOP
i,k,u
ð10dÞ
παk,u ≤SSOP
k,u ≤SSOP, max
k
αk,u
ð10eÞ
where SSOP
i,k,u denotes the converter capacity at node i in scheme k in
stage u. SSOP, max
k
denotes the maximum capacity of SOP in scheme k. π
denotes a minimal positive value. The investment constraints of EVCS
are formulated as follows.
βi,u1 ≤βi,u, SEVCS
i,u1 ≤SEVCS
i,u
ð11aÞ
πβi,u ≤SEVCS
i,u
≤SEVCS, max
i
βi,u
ð11bÞ
PEV,rated
i,u
≤SEVCS
i,u
ð11cÞ
X
i2Ωe
PEV,rated
i,u
= PEV,pen
u
ð11dÞ
where SEVCS,max
i
denotes the maximum capacity of EVCS at node i.
PEV,rated
i,u
denotes the rated EV demand at node i in stage u. PEV,pen
u
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
10



<!-- page 11/14 -->

denotes the total EV demand in stage u. The investment constraints of
PV are formulated as follows.
δi,u1 ≤δi,u, SPV
i,u1 ≤SPV
i,u
ð12aÞ
πδi,u ≤SPV
i,u ≤SPV, max
i
δi,u
ð12bÞ
PPV,rated
i,u
≤μmin
i
SPV
i,u
ð12cÞ
X
i2Ωg
PPV,rated
i,u
= PPV,pen
u
ð12dÞ
where δi,u is a binary variable, indicating whether PV is constructed at
node i in stage u. SPV, max
i
denotes the maximum capacity of PV at node
i. μmin
i
denotes the minimum power factor of PV at node i. PPV,rated
i,u
denotes the rated PV output at node i in stage u. PPV,pen
u
denote the
total PV output in stage u.
Constraints of FDN operation
The power ﬂow constraints of distribution network are formulated
based on DistFlow branch model40, which describes the power ﬂow
mechanism precisely and has been applied widely in distribution
networks41.
X
ij2Ωb
Pij,u  RijI2
ij,u


+ Pj,u =
X
jr2Ωb
Pjr,u
ð13aÞ
X
ij2Ωb
Qij,u  XijI2
ij,u


+ Qj,u =
X
jr2Ωb
Qjr,u
ð13bÞ
V 2
i,u  V 2
j,u + R2
ij + X2
ij


I2
ij,u  2 RijPij,u + XijQij,u


= 0
ð13cÞ
I2
ij,uV 2
i,u 
P2
ij,u + Q2
ij,u


= 0
ð13dÞ
Pi,u = PS
i,u + PDG
i,u +
X
k2L
PSOP
i,k,u  PLD
i,u  PEV
i,u
ð13eÞ
Qi,u = QS
i,u + QDG
i,u +
X
k2L
QSOP
i,k,u  QLD
i,u
ð13fÞ
where Ωb denotes the set of branches. Pij,u and Qij,u denote the active
and reactive power ﬂow of branch ij in stage u, respectively. Rij and Xij
denote the resistance and reactance of branch ij, respectively. Vi,u
denotes the voltage magnitude of node i in stage u. Pi,u and Qi,u denote
the total active and reactive power injection at node i in stage u,
respectively. PS
i,u, QS
i,u, PPV
i,u, QPV
i,u, PLD
i,u and QLD
i,u denote the active and
reactive power injection by substation, PV and load at node i in stage u,
respectively. PSOP
i,k,u and QSOP
i,k,u denote the active and reactive power
injection by SOP at node i in scheme k in stage u, respectively. PEV
i,u
denotes the active power injection by EV at node i in stage u.
Note that the proposed FDN planning problem is a mixed-integer
nonlinear programming (MINLP) model. A convex relaxation42 is
adopted to convert the MINLP model to a mixed-integer second-order
conic programming (MISOCP) formulation, which can be efﬁciently
computed by commercial solvers. The convex relaxation of power ﬂow
constraints is mathematically described as follows.
X
ij2Ωb
Pij,u  Rijlij,u


+ Pj,u =
X
jr2ΩbPjr,u
ð14aÞ
X
ij2Ωb
Qij,u  Xijlij,u


+ Qj,u =
X
jr2ΩbQjr,u
ð14bÞ
vi,u  vj,u + R2
ij + X2
ij


lij,u  2 RijPij,u + XijQij,u


= 0
ð14cÞ
2Pij,u,
2Qij,u
lij,u  vi,u
							
							
2
≤lij,u + vi,u
ð14dÞ
where lij,u denotes the square of current magnitude of branch ij in stage
u. vi,u denotes the square of voltage magnitude of node i in stage u.
Namely, lij,u = I2
ij,u and vi,u = V 2
i,u. To evaluate the accuracy of the convex
relaxation for the proposed model, an index43 is deﬁned to quantify the
relaxation deviation as follows.
Ju = lij,uvi,u  P2
ij,u  Q2
ij,u
			
			
1
ð15Þ
where Ju denotes the index to evaluate the relaxation deviation, indi-
cating whether the SOCP-relaxed optimal solution is accurate or not. If
the gap is smaller than a pre-speciﬁed tolerance, the optimal solution is
accepted as exact. Particularly, the demand of conventional loads and
EVCSs, as well as the generation of PVs, are deﬁned as random
variables.
Pϑ
i,u = ξϑ
i,u  Pϑ,rated
i,u
,ϑ = fLD,EV,PVg
ð16Þ
where ϑ denotes the index of different devices. ξϑ
i,u denotes the ran-
dom proﬁles of device ϑ at node i in stage u. The rated load power at
node i in stage u is determined as PLD,rated
i,u
= PLD,rated
i,u1
ð1 + ρLD
u Þ
Y, and ρLD
u
denotes the annual increase rate of load in stage u. Assume the power
factors of loads remain constant. The operational constraints of SOP
are formulated as follows.
X
i2Ωk
PSOP
i,k,u  PSOP,LOS
i,k,u


= 0
ð17aÞ
PSOP,LOS
i,k,u
= ϖ
ﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃ
PSOP
i,k,u

2
+ QSOP
i,k,u

2
r
ð17bÞ
SSOP
i,k,u ≥
ﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃﬃ
PSOP
i,k,u

2
+ QSOP
i,k,u

2
r
ð17cÞ
SSOP
i,k,u ≤PSOP
i,k,u ≤SSOP
i,k,u
ð17dÞ
SSOP
i,k,u ≤QSOP
i,k,u ≤SSOP
i,k,u
ð17eÞ
where ϖ denotes the loss factor of SOP converters. Chance constraints
are formulated to represent the security risks of FDN with a predeﬁned
violation probability.
P V 2
min ≤vi,u ≤V 2
max
n
o
≥1  γ
ð18aÞ
P lij,u ≤I2
max
n
o
≥1  γ
ð18bÞ
where V min and V max respectively denote the lower and upper bounds
of nodal voltages, and Imax denotes the upper bound of line currents. γ
denotes the acceptable violation probability.
Revised operational cost
After the planning strategy of FDN is determined, a large number of
power ﬂow calculations based on Monte Carlo method is executed to
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
11



<!-- page 12/14 -->

compute the revised operational cost. The penalty cost is attributed to
the load loss affected by potential security risks. Especially, the penalty
cost for voltage violation is computed asthe sum of the active power of
the loads on the nodes where voltages exceed the safe range. The
penalty cost for line overloading is computed as the sum of the active
power of the loads located at the downstream nodes of the overload
line. The calculation method is formulated as follows.
ϕOP,all
u
= 8760 
ϕFDN,LS
u
+ ϕVOLT,VL
u
+ ϕCURT,VL
u


ð19aÞ
ϕFDN,LS
u
= cSL
u E
X
ij2Ωb
Rijlij,u +
X
k2L
X
i2Ωk
PSOP,LS
i,k,u
2
4
3
5
ð19bÞ
ϕVOLT,VL
u
= cVL
u E
X
i2Ωn
PLD
i,u : vi,u<V 2
min k vi,u>V 2
max
2
4
3
5
ð19cÞ
ϕCURT,VL
u
= cVL
u E
X
ij2Ωb
X
r2Ωn,ij
PLD
r,u : lij,u>I2
max
2
4
3
5
ð19dÞ
where ϕFDN,LS
u
denotes the cost of FDN loss. ϕVOLT,VL
u
and ϕCURT,VL
u
denote the costs of voltage violation and line overload, respectively.
Ωn denotes the set of nodes, and Ωn,ij denotes the set of the nodes
downstream of branch ij. cVL
u denotes the penalty price, which is gen-
erally assigned as the electricity price.
Additionally, the above penalty costs are not included in the
objective of planning model, for the reason that the nodal voltages and
line currents are restricted within a safe range in Eq. (18). However, the
chance constrains allow violations within a permitted probability, so
the costs of voltage violation and line overload are involved in the
economic estimation of the planning scheme.
Chance-constrained programming
The compact formulation of chance-constrained programming is
expressed as follows.
minx2Xf ðxÞ
ð20aÞ
sðx,w,ξÞ = 0
ð20bÞ
mðx,w,ξÞ ≤0
ð20cÞ
Pfzðx,w,ξÞ 2 Zg ≥1  γ
ð20dÞ
where x denotes the vector of state variable. w denotes the vector of
decision variables. s(x, w, ξ) and m(x, w, ξ) denote the equality and
inequality constraints, respectively. z(x, w, ξ) is modelled as chance
constraints, and Z denotes the feasible region determined by lower
and upper limits zmin and zmax.
With the adoption of Distﬂow constraints, the original problem
deﬁned in Eq. (20) is essentially a chance-constrained MISOCP model.
However, there is no analytical expression for the chance constraints in
a non-linear system. To obtain the violation probability of the dis-
tribution network, it is straightforward to use the sampling method.
First, a sample set ξN =
ξðjÞ
n
oN
j = 1 is generated based on the modelling of
uncertainties. Then, FDN states xN = xðjÞ

N
j = 1 are obtained when
planning scheme w is adopted. Hence, the chance constraints can be
further expressed as follows.
P ziðx,w,ξÞ 2 Zi


= E I zi xN,w,ξ N






ð21aÞ
I zi xðjÞ,w,ξðjÞ




=
1
zi xðjÞ,w,ξ ðjÞ


2 Zi
0
zi xðjÞ,w,ξðjÞ


=2Zi
8
>
<
>
:
ð21bÞ
where IðÞ denotes the signature function, and E½ denotes the
expectation operator.
General iterative format
The chance constrains in Eq. (20) are reformulated as follows using the
expectation of random variables28.
zðx,w,E½ξÞ ≥zκ
min
zðx,w,E½ξÞ ≤zκ
max

ð22aÞ
zκ
min = zκ1
min + Δzκ1
min
zκ
max = zκ1
max  Δzκ1
max
(
ð22bÞ
Δzκ
min = Qðz,Pfz 2 ZgÞ  Qðz,γÞ
Δzκ
max = Qðz,1  γÞ  Qðz,Pfz 2 ZgÞ

ð22cÞ
where QðÞ denotes the quantile function. Δzκ1
min and Δzκ1
max are both
non-negative values, which are used to update the upper and lower
bounds zκ
min and zκ
max of the inequality constraints, respectively. The
initialisation conditions are z0
min = zmin, z0
max = zmax.
In this way, the chance-constrained optimisation model described
in Eq. (20) is transformed into a deterministic model, which is solved
with the updated bounds in each iteration until all the security con-
straints satisfy the predeﬁned risk level. Constraints that occur outside
of bounds are deﬁned as valid constraints; otherwise, they are deﬁned
as invalid constraints. During the iteration process, only the correc-
tions to the valid constraints need to be calculated and iteratively
updated, whereas the invalid constraints remain unchanged. There-
fore, using updated bounds to iteratively solve the planning scheme
not only ensures a predetermined margin of safety, but also prevents
the result from being overly conservative. Although this type of
iterative algorithm does not have a convergence guarantee44, it per-
forms well in practical engineering applications.
Modiﬁed iterative algorithm
In the general iteration format, there are two drawbacks to be
improved. In the general iteration format, there are two limitations to
be improved. First, the constraint bounds are updated from the pre-
vious bounds, as shown in Eq. (22b). However, the initial bounds are
relatively relaxed, so that the bounds updated at the beginning of the
iterations do not affect the solution, thus resulting in slow con-
vergence. Hence, new bounds can be obtained in a straightforward
manner by correcting the solution of the deterministic planning
model, and Eq. (22b) can be rewritten as follows.
zκ
min = min zκ1
det + Δzκ1
min,zκ
max


zκ
max = max zκ1
det  Δzκ1
max,zκ
min


(
ð23Þ
where zκ1
det denotes the solution of deterministic planning model in the
(κ −1)-th iteration. The minðÞ and maxðÞ operations are performed to
avoid numerical conﬂicts between the upper and lower bounds. Dur-
ing the iterative process, only the corrections of the valid constraints
need to be calculated and iteratively updated. The invalid constraint
remains unchanged, thus satisfying zκ
min = zκ1
min and zκ
max = zκ1
max.
The other limitation of the general iterative method is that at the
end of the iterations, when the violation risk is adjacent to the
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
12



<!-- page 13/14 -->

predetermined threshold, a smaller bound correction and slower
convergence are resulted. Therefore, a penalised correction approach
is proposed to ensure that the iterative process can be completed
rapidly, and Eq. (22b) can be rewritten as follows.
γκ
p = γ  eaκ=κmax
ð24aÞ
Δzκ
min = Qðz,Pfz 2 ZgÞ  Q z,γκ
p


Δzκ
max = Q z,1  γκ
p


 Qðz,Pfz 2 ZgÞ
8
>
<
>
:
ð24bÞ
where κmax denotes the maximum number of iterations. aκ denotes the
cumulative number of times that the security constraints violate the
risk assessment during iterations. Finally, the chance-constrained
problem established in Eq. (20) is converted into a deterministic
MISOCP model with an iterative format, which is formulated as follows.
At each iteration, the model can be effectively solved by commercial
solvers, such as Mosek or Gurobi.
min
x2X f ðxÞ
s:t:ð20bÞ  ð20cÞ,ð20dÞ,ð23Þ,ð24Þ
ð25Þ
Reporting summary
Further information on research design is available in the Nature
Portfolio Reporting Summary linked to this article.
Data availability
The price data of grid assets over the entire planning period is available
in the Supplementary Information ﬁle. The processed input data is
sampled from the probabilistic distributions of sources and loads. The
output data is generated by performing the multi-resource dynamic
coordinated planning of ﬂexible distribution network. Source data are
provided with this paper.
Code availability
The mathematical programming models are written by Python 3.7 and
solved with the commercial solver Gurobi 10.0.1. Detailed descriptions
of the sets, parameters, objective function, constraints, and variables
are available in the Method section. Information about the code used
in this research, including how to access it, are available on GitHub
(https://github.com/fdn-planning/FDN_Model).
References
1.
Ehsan, A. & Yang, Q. State-of-the-art techniques for modelling of
uncertainties in active distribution network planning: a review. Appl.
Energy 239, 1509–1523 (2019).
2.
Huo, Y., Bouffard, F. & Joós, G. Spatio-temporal ﬂexibility man-
agement in low-carbon power systems. IEEE Trans. Sustain. Energy
11, 2593–2605 (2020).
3.
Zwickl-Bernhard, S. & Auer, H. Open-source modeling of a low-
carbon urban neighborhood with high shares of local renewable
generation. Appl. Energy 282, 116166 (2021).
4.
Ding, T., Qu, M. & Huang, C. Multi-period active distribution network
planning using multi-stage stochastic programming and nested
decomposition by SDDIP. IEEE Trans. Power Syst. 36, 2281–2292
(2020).
5.
Arias, N. B., Tabares, A. & Franco, J. F. Robust joint expansion
planning of electrical distribution systems and EV charging stations.
IEEE Trans. Sustain. Energy 9, 884–894 (2017).
6.
Huang, N., Zhao, X., Guo, Y., Cai, G. & Wang, R. Distribution network
expansion planning considering a distributed hydrogen-thermal
storage system based on photovoltaic development of the whole
county of China. Energy 278, 127761 (2023).
7.
Mejia, M. A., Macedo, L. H., Muñoz-Delgado, G., Contreras, J. &
Padilha-Feltrin, A. Multistage planning model for active distribution
systems and electric vehicle charging stations considering voltage-
dependent load behaviour. IEEE Trans. Smart Grid 13, 1383–1397
(2021).
8.
National Energy Administration. Statistics on PV construction in
2022. http://www.nea.gov.cn/2023-02/17/c1310698128.htm
(2023).
9.
The Ministry of Public Security of the People’s Republic of China.
National statistics on motor vehicle ownership and drivers in 2022.
https://app.mps.gov.cn/gdnps/pc/content.jsp?id=8837602
(2023).
10.
Chai, Y. et al. Network partition and voltage coordination control for
distribution networks with high penetration of distributed PV units.
IEEE Trans. Power Syst. 33, 3396–3407 (2018).
11.
Chen, X., Qiu, J., Reedman, L. & Dong, Z. A statistical risk assess-
ment framework for distribution network resilience. IEEE Trans.
Power Syst. 34, 4773–4783 (2019).
12.
Zhang, T., Wang, C., Luo, F., Li, P. & Yao, L. Optimal design of the
sectional switch and tie line for the distribution network based on
the fault incidence matrix. IEEE Trans. Power Syst. 34, 4869–4879
(2019).
13.
Cao, W., Wu, J., Jenkins, N., Wang, C. & Green, T. Beneﬁts analysis of
soft open points for electrical distribution network operation. Appl.
Energy 165, 36–47 (2016).
14.
Xiao, J. et al. Flexible distribution network: deﬁnition, conﬁguration,
operation, and pilot project. IET Gener. Transm. Dis. 12,
4492–4498 (2018).
15.
Ji, H. et al. Peer-to-peer electricity trading of interconnected ﬂexible
distribution networks based on distributed ledger. IEEE Trans.
Industr. Inform. 18, 5949–5960 (2021).
16.
Long, C., Wu, J., Thomas, L. & Jenkins, N. Optimal operation of soft
open points in medium voltage electrical distribution networks with
distributed generation. Appl. Energy 184, 427–437 (2016).
17.
Jiang, X., Zhou, Y., Ming, W., Yang, P. & Wu, J. An overview of soft
open points in electricity distribution networks. IEEE Trans. Smart
Grid 13, 1899–1910 (2022).
18.
Shen, X., Shahidehpour, M., Zhu, S., Han, Y. & Zheng, J. Multi-stage
planning of active distribution networks considering the co-
optimization of operation strategies. IEEE Trans. Smart Grid 9,
1425–1433 (2016).
19.
Bloemink, J. M. & Green, T. C. Beneﬁts of distribution-level power
electronics for supporting distributed generation growth. IEEE
Trans. Power Deliver. 28, 911–919 (2013).
20. Khezri, R., Mahmoudi, A. & Aki, H. Optimal planning of solar pho-
tovoltaic and battery storage systems for grid-connected residen-
tial sector: review, challenges and new perspectives. Renew.
Sustain. Energy Rev. 153, 111763 (2022).
21.
Yang, Y., Wu, W., Wang, B. & Li, M. Analytical reformulation for
stochastic unit commitment considering wind power uncertainty
with gaussian mixture model. IEEE Trans. Power Syst. 35,
2769–2782 (2019).
22. Pamshetti, V. B. et al. Cooperative operational planning model for
distributed energy resources with soft open point in active dis-
tribution network. IEEE Trans. Industr. Appl. 59, 2140–2151 (2022).
23. Jian, J. et al. Supply restoration of data centers in ﬂexible distribu-
tion networks with spatial-temporal regulation. IEEE Trans. Smart
Grid 15, 340–354 (2024).
24. Rahim, S., Wang, Z. & Ju, P. Overview and applications of robust
optimization in the avant-garde energy grid infrastructure: a sys-
tematic review. Appl. Energy 319, 119140 (2022).
25. Charnes, A. & Cooper, W. W. Chance-constrained programming.
Manag. Sci. 6, 73–79 (1959).
26. Gao, Y., Xu, X., Yan, Z. & Shahidehpour, M. Gaussian mixture model
for multivariate wind power based on kernel density estimation and
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
13



<!-- page 14/14 -->

component number reduction. IEEE Trans. Sustain. Energy 13,
1853–1856 (2022).
27.
Sheng, H. & Wang, X. Probabilistic power ﬂow calculation using
non-intrusive low-rank approximation method. IEEE Trans. Power
Syst. 34, 3014–3025 (2019).
28. Xu, Y. et al. An iterative response-surface-based approach for
chance-constrained ac optimal power ﬂow considering dependent
uncertainty. IEEE Trans. Smart Grid 12, 2696–2707 (2021).
29. Su, C. T. & Lee, C. S. Network reconﬁguration of distribution sys-
tems using improved mixed-integer hybrid differential evolution.
IEEE Trans. Power Deliver. 18, 1022–1027 (2003).
30. Zhang, S., Fang, Y., Zhang, H., Cheng, H. & Wang, X. Maximum
hosting capacity of photovoltaic generation in sop-based power
distribution network integrated with electric vehicles. IEEE Trans.
Industr. Inform. 18, 8213–8224 (2022).
31.
Wang, C. et al. Optimal siting and sizing of soft open points in active
electrical distribution networks. Appl. Energy 189, 301–309 (2017).
32. Shu, Y. Planning Design of Distribution Network (China Electric
Power Press, 2018).
33. Wang, S., Wang, X., Wang, S. & Wang, D. Bi-directional long short-
term memory method based on attention mechanism and rolling
update for short-term load forecasting. Int. J. Electr. Power Energy
Syst. 109, 470–479 (2019).
34. Lee, Z. J., Li, T. & Low, S. H. ACN-data: Analysis and applications
of an open ev charging dataset. Proc. Tenth ACM. Int. Conf.
Future Energy Syst. 139–149, https://doi.org/10.1145/3307772.
3328313 (2019).
35. Breakah, T. M., Williams, R. C., Herzmann, D. E. & Takle, E. S. Effects
of using accurate climatic conditions for mechanistic-empirical
pavement design. J. Transp. Eng. 137, 84–90 (2011).
36. Wang, R. et al. Identiﬁcation of critical uncertain factors of dis-
tribution networks with high penetration of photovoltaics and
electric vehicles. Appl. Energy 329, 120260 (2023).
37. Ji, H. et al. An enhanced SOCP-based method for feeder load bal-
ancing using the multi-terminal soft open point in active distribution
networks. Appl. Energy 208, 986–995 (2017).
38. Chen, Y., Wen, J. & Cheng, S. Probabilistic load ﬂow method based
on Nataf transformation and Latin hypercube sampling. IEEE Trans.
Sustain. Energy 4, 294–301 (2012).
39. Konakli, K. & Sudret, B. Polynomial meta-models with canonical
low-rank approximations: numerical insights and comparison to
sparse polynomial chaos expansions. J. Comput. Phys. 321,
1144–1169 (2016).
40. Baran, M. E. & Wu, F. F. Optimal capacitor placement on radial
distribution systems. IEEE Trans. Power Deliv. 4, 725–734 (1989).
41.
Daniel, K. M. et al. A survey of distributed optimization and control
algorithms for electric power systems. IEEE Trans. Smart Grid 8,
2941–2962 (2017).
42. Lavaei, J. & Low, S. H. Zero duality gap in optimal power ﬂow pro-
blem. IEEE Trans. Power Syst. 27, 92–107 (2012).
43. Wei, W., Wang, J., Li, N. & Mei, S. Optimal power ﬂow of radial
networks and its variations: a sequential convex optimization
approach. IEEE Trans. Smart Grid 8, 2974–2987 (2017).
44. Roald, L. & Andersson, G. Chance-constrained AC optimal power
ﬂow: reformulations and efﬁcient algorithms. IEEE Trans. Power
Syst. 33, 2906–2918 (2017).
Acknowledgements
This work is supported by National Natural Science Foundation of China
“Clustering control of ﬂexible distribution networks with large-scale DG
integration” (No. U22B20114), “Trading mechanism and design of
decentralized electric power market in distribution systems based on
ﬂexibility pricing” (No. 52277117), and the project of “Integrated opera-
tion and planning for smart electric distribution networks (OPEN)” from
the UK and China. The researchers would like to acknowledge and thank
the funders.
Author contributions
R.W. and H.J. conceived the paper, wrote the code and drafted
the manuscript. P.L. and H.Y. conceived the multi-resource dynamic
and coordinated planning of ﬂexible distribution network. J.Z. pro-
cessed and analysed data. L.Z. collected and analysed data, and
proofread the manuscript. Y.Z., J.W., L.B. and J.Y. edited and revised
the manuscript. C.W. provided institutional and material support for
the research.
Competing interests
The authors declare no competing interests.
Additional information
Supplementary information The online version contains
supplementary material available at
https://doi.org/10.1038/s41467-024-48862-5.
Correspondence and requests for materials should be addressed to
Peng Li or Hao Yu.
Peer review information Nature Communications thanks David Green-
wood and the other, anonymous, reviewer(s) for their contribution to the
peer review of this work. A peer review ﬁle is available.
Reprints and permissions information is available at
http://www.nature.com/reprints
Publisher’s note Springer Nature remains neutral with regard to jur-
isdictional claims in published maps and institutional afﬁliations.
Open Access This article is licensed under a Creative Commons
Attribution 4.0 International License, which permits use, sharing,
adaptation, distribution and reproduction in any medium or format, as
long as you give appropriate credit to the original author(s) and the
source, provide a link to the Creative Commons licence, and indicate if
changes were made. The images or other third party material in this
article are included in the article’s Creative Commons licence, unless
indicated otherwise in a credit line to the material. If material is not
included in the article’s Creative Commons licence and your intended
use is not permitted by statutory regulation or exceeds the permitted
use, you will need to obtain permission directly from the copyright
holder. To view a copy of this licence, visit http://creativecommons.org/
licenses/by/4.0/.
© The Author(s) 2024
Article
https://doi.org/10.1038/s41467-024-48862-5
Nature Communications|   (2024) 15:4576 
14
