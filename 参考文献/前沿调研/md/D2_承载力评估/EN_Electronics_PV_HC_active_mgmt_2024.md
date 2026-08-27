<!--
source: D2_承载力评估/EN_Electronics_PV_HC_active_mgmt_2024.pdf
sha256: f30d6dda5aa68fa17eeca789d9083230ba9dd570e6b8363d8fcb6acf3472e305
method: pymupdf
pages: 21
-->

<!-- page 1/21 -->

Citation: Lin, T.; Wu, G.; Lai, S.; Hu,
H.; Hu, Z. Calculation of Distribution
Network PV Hosting Capacity
Considering Source–Load Uncertainty
and Active Management. Electronics
2024, 13, 4048. https://doi.org/
10.3390/electronics13204048
Academic Editor: Ahmed Abu-Siada
Received: 8 September 2024
Revised: 9 October 2024
Accepted: 10 October 2024
Published: 15 October 2024
Copyright: © 2024 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license (https://
creativecommons.org/licenses/by/
4.0/).
electronics
Article
Calculation of Distribution Network PV Hosting Capacity
Considering Source–Load Uncertainty and Active Management
Tingting Lin 1,2, Guilian Wu 1,2,3, Sudan Lai 1,2, Hao Hu 4,* and Zhijian Hu 4
1
Economic and Technological Research Institute, State Grid Fujian Electric Power Co., Ltd.,
Fuzhou 350013, China; lin_tingting1@fj.sgcc.com.cn (T.L.)
2
Distribution Network Planning and Operation Control Technology in Multiple Disaster Superimposed Areas
State Grid Corporation Laboratory, Ltd., Fuzhou 350013, China
3
School of Electronic Information and Electrical Engineering, Shanghai Jiao Tong University,
Shanghai 200240, China
4
School of Electrical Engineering and Automation, Wuhan University, Wuhan 430072, China;
zj.hu@whu.edu.cn
*
Correspondence: hu_hao@whu.edu.cn
Abstract: The access of a high proportion of photovoltaic (PV) will change the energy structure of
the distribution network (DN), resulting in a series of safety operation risks. This paper proposes a
two-stage PV hosting capacity (PVHC) calculation model to assess the maximum PVHC, considering
the uncertainty and active management (AM). Firstly, we employ a robust optimization model to
characterize the uncertainty of sources and loads in DN with PV and analyze the worst-case scenarios
for PVHC. Subsequently, we construct a PVHC calculation model that takes into account AM,
and convert the model into a mixed-integer second-order cone (MISOC) model using linearization
techniques. Finally, we apply “heuristic optimization + CPLEX solver” to solve the model and
introduce overvoltage and overcurrent indices to analyze the safety of the DN under PV limit access.
Case studies are carried out on the IEEE 33-bus system and a practical case. Results show that (1) only
the uncertainty that reduces the load or increases the output efficiency will affect PVHC; (2) for
DN limited by overvoltage, AM can better improve PVHC; however, for DN limited by maximum
transmission power, the effect of AM is low; (3) for most DN, SVC can improve PVHC, but the effect
is modest. And network reconfiguration can significantly increase PVHC on the system with poor
branch network, even reaching 150% of the original PVHC.
Keywords: distribution network; photovoltaic hosting capacity; source–load uncertainty; active
management
1. Introduction
1.1. Background
With the depletion of fossil energy such as oil and coal, energy crisis and energy
pollution are approaching. According to the International Energy Agency, the new installed
capacity of renewable energy in the world reached 510 GW in 2023. China’s national energy
administration has reported that China’s new installed power generation capacity was
about 290 GW in 2023. China’s installed capacity of renewable energy has surpassed that
of thermal power for the first time. As an important renewable energy source, the installed
capacity of photovoltaic (PV) accounts for a large proportion of renewable energy. In 2023,
the global new installed capacity of PV was 375 GW, accounting for 75% of all the new in-
stalled capacity of renewable energy. The rapid development of PV has led to an increasing
penetration rate in the distribution network (DN). It is important to consider the maximum
PV hosting capacity (PVHC).
Compared with conventional generators, PV is affected by lighting conditions and has
great uncertainty. Additionally, the transportation and installation processes of PV systems
Electronics 2024, 13, 4048. https://doi.org/10.3390/electronics13204048
https://www.mdpi.com/journal/electronics



<!-- page 2/21 -->

Electronics 2024, 13, 4048
2 of 21
can result in losses, further causing the actual output to deviate from the ideal output [1].
The uncertainty caused by the high proportion of PV access will cause a non-negligible
impact on DN. In addition, the load of DN also has uncertainty, and its uncertainty cannot
be ignored. Therefore, it is necessary to consider the uncertainty of PV and load and to
obtain the most unfavorable operation scenario for the maximum PV access to the DN.
In addition, the high proportion of PV access will also change the energy consumption
structure of the traditional DN. The energy consumption structure of the traditional DN
is to supply power to the DN through the superior grid, so as to meet the electricity
demand of DN. When the PV is large enough, the electricity load of the DN will be
entirely borne by the PV, and the excess PV power generation will flow to the superior
grid, causing the occurrence of the reverse transmission phenomenon (RTP) [2,3]. Figure 1
shows the energy flow of the traditional DN and the DN with a high proportion of PV
access. Squares represent balance buses, circles are load buses, triangles are PV grid-
connected buses, and arrows indicate the direction of energy flow. It can be seen that
the energy of the traditional DN flows from the balancing bus to the remaining load
buses. However, the energy flow direction of the DN with a high proportion of PV
access is from the PV buses to the rest of the load buses and the balance bus, so its
voltage will be higher than the reference voltage at the balance bus [4], which makes the
DN have the risk of overvoltage [5,6]. Therefore, although PV has been developed very
rapidly due to its environmental protection and renewability, its uncertainty and impact
on the security of the DN limit its HC [7,8]. The above analysis shows the adverse factors
that affect the PVHC. But, with the development and construction of the intelligent DN,
various active management (AM) strategies can effectively improve PVHC, such as network
reconfiguration and static Var compensator (SVC) control [9].
(a)
1
2
3
4
5
6
7
8
9
1
2
3
4
5
6
7
8
9
(b)
1
2
3
4
5
6
7
8
9
1
2
3
4
5
6
7
8
9
Figure 1. The energy flow direction of DN. (a) The traditional DN. (b) The DN with a high proportion
of PV access.
In summary, the PVHC calculation problem needs to maximize the PVHC using AM
while fully considering the DN security and source–load uncertainty.



<!-- page 3/21 -->

Electronics 2024, 13, 4048
3 of 21
1.2. Literature Review
PVHC is defined as the maximum installed PV capacity of the DN that does not violate
the constraints for the safe operation of the power grid [10]. At present, many scholars
have carried out research on the evaluation and calculation of PVHC.
On the evaluation of PVHC, ref. [11] has integrated the impact of distributed gener-
ation and new load access on the distribution network, and then established evaluation
indexes from five aspects of the distribution network: reliability, safety, economy, flexibility,
and quality. The evaluation index of the HC was constructed from the perspectives of
power grid architecture and operation state in ref. [12], and the HC was improved through
the expansion planning of the DN. On the basis of constructing the HC index, ref. [13] has
studied the effect of energy storage and adjusting the transformer tap on the improvement
of the HC. The aforementioned literature has assessed PVHC by constructing indicators,
yet it has not actually calculated the PVHC itself.
On the calculation of PVHC, ref. [14] has used ETAP simulation software (version: 16.0)
to calculate the power flow of the DN that contains PV power sources, under the condition
that the power grid voltage constraints and line power flow constraints are met, and com-
bined this with the actual load curve of a certain region, so as to obtain the maximum PVHC
that can be connected to the PV power sources. Based on voltage sensitivity and multi-
scenario power flow simulation, ref. [15] has proposed a PV acceptance ability evaluation
method, which can uniformly generate the possible access scheme of PV and simulates the
multi-power flow. In ref. [16], the voltage deviation index and reverse power transmission
of high-proportion PV DN were introduced to judge the rationality of the optimization
scheme and feed back to the modification layer of the access scheme; then, the calculation
results of the PVHC were obtained. In ref. [17], the evaluation system of renewable energy
hosting capacity index and the hosting capacity calculation model of the power grid were
established after fully considering the power quality, relay protection, and thermal stability
test. The particle swarm optimization (PSO) algorithm was used to solve the hosting ca-
pacity model. Although the aforementioned literature has calculated PVHC, it is based on
deterministic data and does not account for the uncertainty of PV and load within the DN.
It is important to consider the uncertainty of DN when calculating the PVHC. Ref. [18]
has used a weighted K-means algorithm to cluster the historical data of distributed PV
output to obtain typical scenario data. In refs. [19,20], Monte Carlo simulations were used
to counter the uncertainties and variability related to loading behavior and the randomness
in the location and size of PV. Considering the uncertainty of PV and load, the scenario
of minimum load and maximum PV is finally selected as the worst scenario to calculate
the PVHC. Ref. [21] has established a model with high temporal resolution to simulate
all the scenarios. Based on the results of the scenarios with different PV power rates and
storage capacities, the worst scenario is the scenario with maximum PV power rates and
minimum storage capacities. A multi-time scale optimization model is established in
Ref. [22], considering the uncertainty of source and load, to realize the calculation of PVHC.
After calculating the PVHC, AM can be taken to improve its HC [23]. In ref. [24],
the best number, location, and size of PV systems to be installed on a distribution feeder
and the control set-points of the PV inverters were determined to maximize the PVHC.
Genetic algorithm (GA) and PSO metaheuristics were employed to solve the optimization
problem. In ref. [25], network reconfiguration was studied in a multi-objective framework
to improve the voltage profile and decrease the total energy loss, as well as to improve the
PVHC. A solution strategy is proposed for the presented multi-objective problem based
on the implementation of the Non-dominated Sorting Genetic Algorithm II (NSGA-II) and
fuzzy decision-making method. Ref. [26] was devoted to a new multi-objective formulation
to maximize the PVHC and minimize the total energy losses while satisfying the operational
constraints and maximizing the energy transferred to off-peak hours. The Multi-Objective
Advanced Gray Wolf Optimization (MOAGWO) algorithm was used as a solution tool.
For fully exploiting the ability of DNs to accommodate PV, ref. [27] proposed a robust
comprehensive PVHC assessment method, considering three-phase power flow modelling



<!-- page 4/21 -->

Electronics 2024, 13, 4048
4 of 21
and AM techniques, including network reconfiguration, on-load-tap-changers regula-
tion (OLTC), and reactive power compensation. Ref. [28] has proposed a two-stage model,
in which the dispatching of soft open point (SOP) and management of electric vehicles (EVs)
were coordinated together with traditional AM techniques. A solving strategy based on
the column-and-constraint generation (C&CG) algorithm is developed to solve the model.
1.3. Contributions
The above literature studied PVHC from the perspectives of evaluation, calculation,
and improvement. This paper focuses on the calculation of PVHC to construct an accurate
PVHC calculation model. Noting that most of the calculation models directly make the
maximum PVHC the objective, but few of them have considered whether the objective
remains the fit for the model after the changes when it was linearized, this paper has
proposed a relaxation formula to verify the correctness of the objective. In addition,
considering that the PV has its own inverter and the DN has its own backup branch,
any DN can take SVC and network reconfiguration to improve the PVHC. Thus, it is
necessary to consider the SVC and network reconfiguration when constructing the PVHC
calculation model.
In this paper, a PVHC calculation model and improvement method considering the
uncertainty of DN has been proposed. The source–load uncertainty is described by robust
optimization. Meanwhile, the PVHC calculation model is constructed under the constraints
of DN safety and practical, PV configuration, RTP, and AM methods, and then linearized to
a mixed-integer second-order cone (MISOC) model. The validity of the objective is verified
by the relaxation verification formula, and the safety of DN operation is verified by the
overvoltage margin and overcurrent margin indexes. Table 1 compares the proposed model
of this paper with the relevant research on PVHC recently.
Table 1. Comparison of the relevant research.
Ref.
Uncertainty Analysis
Model Solution
PVHC Improvement
Model Evaluation
[17]
None
PSO
Energy storage
None
[20]
Monte carlo simulation
Traversal
algorithm
None
Overvoltage
limit violation,
equipment
ampacity violation
[21]
Stochastic simulation
High temporal
resolution
simulation
Distributed storage
Demand cover factor,
supply cover factor,
grid interaction supply
cover factor,
exported energy factor
[22]
Monte carlo simulation
MATLAB
optimization
toolbox
None
Line capacity,
node overvoltage,
net load deviation
[24]
None
GA and PSO
SVC
None
[25]
Probabilistic assessments
NSGA-II
Network reconfiguration
Fuzzy decision-making
[26]
None
MOAGWO
algorithm
Energy storage,
OLTC, SVC
None
[27]
Robust optimization
C&CG
algorithm
network reconfigura-
tion, OLTC,
reactive power
compensation
None
[28]
Robust optimization
C&CG
algorithm
EV management, SOP,
network reconfigura-
tion, OLTC,
reactive power
compensation
None
This paper
Robust optimization
Traversal algorithm,
CPLEX
Network
reconfiguration, SVC
Relaxation deviation,
overvoltage margin,
overcurrent margin
From the above, the key contributions of this study are listed below:



<!-- page 5/21 -->

Electronics 2024, 13, 4048
5 of 21
(1)
An MISOC model was established to calculate and improve the PVHC. Unlike other
papers, we propose a relaxation verification formula to assess the relaxation validity
of the MISOC model;
(2)
To evaluate the safety of the DN under PV limit access, the overvoltage and over-
current margin indexes are set. The effects of maximum current, maximum voltage,
maximum reverse transmission, and PV inversion angle on PVHC are analyzed by
sensitivity analysis;
(3)
To analyze the enhancement effect of the AM method on PVHC, we applied an AM
method to three kinds of DN systems that are susceptible to transmission power,
current, or voltage.
The remainder of this paper is organized as follows. In Section 2, a source–load
uncertainty model is constructed based on robust optimization, then the worst scenario
is obtained through PVHC analysis. Section 3 constructs a two-stage MISOC calculation
model considering safety constraints and AM methods. In Section 4, a solution framework
based on heuristic optimization and solver is elaborated. In Section 5, the proposed model
is demonstrated, analyzed, and discussed on the IEEE 33-bus system and a practical case in
Fuzhou, Fujian. And conclusions are provided in Section 6.
2. The Worst Scenario Considering Source–Load Uncertainty
2.1. Source–Load Uncertainty Analysis
The DN with PV access receives or transmits power to the higher power grid through
the transmission line; the main power generation source is PV, and the power consumption
sources are load and network loss, as shown in Figure 2. Among these, PV and load
have uncertainty [29,30]. Robust optimization ensures that, even in the worst scenario,
the optimization solution is feasible [31]. Refs. [32,33] established an adaptive robust
stochastic optimization model to address the renewable power uncertainty modeled as a
scenario-based ambiguity set. We describe the uncertainty of PV and load by this method.
Furthermore, considering the absolute nature of PVHC, any solution within the uncertainty
set should yield a value greater than the resulting PVHC. Therefore, the key to solving this
uncertainty problem lies in identifying the worst-case scenario for PVHC calculation. As
in (1)–(3), we describe the source–load uncertainty through box uncertainty sets.
Distribute 
network
Photovoltaic
Super network
Load
Net loss
Distribute 
network
Photovoltaic
Super network
Load
Net loss
Figure 2. DN source–load balance.
φv,s = φ′
v,s + αv+,s∆φv+,s −αv−,s∆φv−,s
(1)
Pv,i,s = φv,sSv,i,s
(2)
Pd,i,s = P′
d,i,s + αd+,i,s∆Pd+,i,s −αd−,i,s∆Pd−,i,s
(3)



<!-- page 6/21 -->

Electronics 2024, 13, 4048
6 of 21
where φv,s, φ′
v,s, ∆φv+,s, and ∆φv−,s are the actual, prediction, upward deviation, and
downward deviation of PV power generation efficiency in scenario s; the box uncertainty
set of φv,s is [φ′
v,s −∆φv−,s, φ′
v,s + ∆φv+,s] ; Pd,i,s, P′
d,i,s, ∆Pd+,i,s, and ∆Pd−,i,s are the actual,
prediction, upward deviation, and downward deviation of load in scenario s and bus
i; the box uncertainty set of Pd,i,s is [P′
d,i,s −∆Pd−,i,s, P′
d,i,s + ∆Pd+,i,s]; αv+,s, αv−,s, αd+,i,s, and
αd−,i,s are the source–load uncertainty deviation coefficients, which have values between 0
and 1; and Pv,i,s, Sv,i,s are the PV power generation and configured capacity in scenario s
and bus i.
2.2. PVHC Analysis
Equation (4) represents that PV output of each scenario that can be obtained based on
power balance. Without considering the abandonment of PV output, the output of PVHC
should always not exceed the PV output of each scene, as in (5).
Pv,s = Pd,s + Ploss,s + Pup,s
(4)
Sv ≤
1
φv,s
(Pd,s + Ploss,s + Pup,s)
(5)
where Pv,s, Pd,s, and Ploss,s are the DN’s total PV generation, load, and loss in scenario s;
Pup,s is the power transmission from the DN to the upper power network in scenario s. Sv
is the PVHC of DN.
From Equation (5), we can see that, the bigger the value of φv,s is and the smaller
the values of Pd,s and Pup,s, the worse the scenario. In ref. [19,34], it is also proven that
the worst scenario is the lowest load and the highest PV output through Monte Carlo
simulations. Therefore, the uncertain scenario with the largest Pd,s and the smallest φv,s
should be selected, as in (6) and (7).
φvmax,s = φ′
v,s + ∆φv+,s
(6)
Pdmin,i,s = P′
d,i,s −∆Pd−,i,s
(7)
where φvmax,s and Pdmin,i,s are the maximum PV power generation efficiency and the
minimum load.
3. Problem Description
The PVHC calculation problem proposed in this paper aims to find out where to
configure the PV and how much capacity of PV to configure in order to realize the maximum
PV capacity of the DN in scenarios, while making sure to fulfill many DN operation and
safety constraints, while also embracing the many constraints of the AM methods.
3.1. Problem Formulation
3.1.1. Objective Function
The objective function of PVHC estimation maximizes the capacity of PV that can be
installed for all buses. This can be expressed as follows:
maxSv,s =
nb
∑
i=1
Sv,i,s
(8)
where nb is the total number of buses.



<!-- page 7/21 -->

Electronics 2024, 13, 4048
7 of 21
3.1.2. DN Power Flow Constraints
In this part, power balance constraints, voltage balance constraints [35], and complex
power constraints are considered [36], as shown in (9)–(12).





Pv,i,s −Pd,i,s =
∑
j∈Ωup,i
Pj,s −
∑
j∈Ωdown,i
(Pj,s −rjI2
j,s)
Qv,i,s −Qd,i,s =
∑
j∈Ωup,i
Qj,s −
∑
j∈Ωdown,i
(Qj,s −xjI2
j,s)
(9)





−Pup,s =
∑
j∈Ωup,i
Pj,s −
∑
j∈Ωdown,i
(Pj,s −rjI2
j,s)
−Qup,s =
∑
j∈Ωup,i
Qj,s −
∑
j∈Ωdown,i
(Qj,s −xjI2
j,s)
(10)
V2
i2,s = V2
i1,s −2(rjPj,s + xjQj,s) + (r2
j + x2
j )I2
j,s
(11)
I2
j,sV2
i1,s = P2
j,s + Q2
j,s
(12)
where Pj,s, Qj,s, and Ij,s are the active power, reactive power, and branch current in scenario
s and branch j; rj and xj are the resistance and reactance of branch j; Qv,i,s, Qd,i,s are the
reactive PV power and reactive load in scenario s and bus i; Qup,s is the reactive power
transmission from the DN to the upper power network in scenario s; Ωup,i and Ωdown,i are
the branch set with bus i as the start and end bus; and Vi1,s and Vi2,s are the start bus and
end bus voltage of branch j in scenario s.
3.1.3. DN Safety Constraints
Equation (13) indicates that the voltage of each bus in DN should be within the voltage
safety threshold, and Equation (14) indicates that the current of each branch in DN cannot
exceed its maximum value [37].
Vmin ≤Vi,s ≤Vmax
(13)
Ij,s
 ≤Imax
(14)
where Vmin and Vmax are the minimum and maximum voltage threshold; Imax is the maxi-
mum current threshold.
3.1.4. RTP Constraints
When the DN supplies or sends power to the upper power network, the maximum
transmission power is limited due to the capacity constraint of the transformer [9], as
in (15).
Pup,s ≤Pup,max
(15)
where Pup,max are the maximum transmission power threshold.
3.1.5. PV Configuration Constraints
For PV buses, the configured capacity should be within the capacity threshold,
as in (16). The PV reactive power output is obtained by (17). If SVC is not considered, θv,i,s
is set to a fixed value. Otherwise, θv,i,s can be set within a certain range, as in (18).
Sv,min ≤Sv,i,s ≤Sv,max
(16)
Qv,i,s = Pv,i,stanθv,i,s
(17)
−θv,max ≤θv,i,s ≤θv,max
(18)
where Sv,min and Sv,max are the minimum and maximum PV configuration capacity; θv,i,s is
the inverse angle of scenario s and bus i; θv,max is the maximum inverse angle.



<!-- page 8/21 -->

Electronics 2024, 13, 4048
8 of 21
3.1.6. Network Reconfiguration Constraints
During the planning phase, the DN adopts a closed-loop design, whereas, during
actual operation, it needs to maintain an open-loop configuration. Consequently, backup
lines are available, making network reconfiguration feasible. Furthermore, since the
original DN topology design did not take into account the scenario of PV limit access,
it is of great significance to explore the optimal topology for PVHC through network
reconfiguration. The topology of the reconfigured DN must meet the radiation and
connectivity constraints [9,38].
∑
j∈Ωdown,i
Fj,s −∑
j∈Ωup,i
Fj,s = 1
(19)
∑
j∈Ωup,1
Fj,s = εg
(20)
nl
∑
j=1
Fj,s = nb −1
(21)
Pj,s = 0, Qj,s = 0, Ij,s = 0, Fj,s = 0, i f αj,s = 0
(22)
where αj,s and Fj,s are the branch switch status and virtual power of scenario s and branch
j; εg is an arbitrary number.
3.2. Linearization Analysis
There are nonlinear constraints in the constructed calculation model, which needs to
be linearized [39]. Introduce a quadratic variable I2
j,s/V2
i,s instead of I2,j,s/ V2,i,s to eliminate
the current and voltage squared terms, as in (23)–(26). When network reconfiguration is
considered in the model, all the parameters of the disconnected line are 0. The large M
method is introduced to linearize the above conditional constraints, as in (27) and (28).





Pv,i,s −Pd,i,s =
∑
j∈Ωup,i
Pj,s −
∑
j∈Ωdown,i
(Pj,s −rjI2,j,s)
Qv,i,s −Qd,i,s =
∑
j∈Ωup,i
Qj,s −
∑
j∈Ωdown,i
(Qj,s −xjI2,j,s)
(23)





−Pup,s =
∑
j∈Ωup,i
Pj,s −
∑
j∈Ωdown,i
(Pj,s −rjI2,j,s)
−Qup,s =
∑
j∈Ωup,i
Qj,s −
∑
j∈Ωdown,i
(Qj,s −xjI2,j,s)
(24)
V2
min ≤V2,i,s ≤V2
max
(25)
I2,j,s ≤I2
max
(26)
−Mαj,s ≤V2,i2,s −V2,i1,s + 2(rjPj,s + xjQj,s) −(r2
j + x2
j )I2,j,s ≤Mαj,s
(27)
−Mαj,s ≤Pj,s, Qj,s, I2,j,s, Fj,s ≤Mαj,s
(28)
where V2,i,s and I2,j,s are the square of voltage and current; M is a maximal positive value.
Equation (12) is transformed into a second-order cone form and treated with relax-
ation [40], as in (29).


2Pj,s, 2Qj,s, I2,j,s −V2,i1,s
T
2 ≤I2,j,s + V2,i1,s
(29)
When linearizing Equation (12), relaxation is carried out, so it is necessary to verify
whether the solution results still satisfy the original constraints, as in (30).
nl
∑
j=1
(I2,j,sV2,i1,s −P2
j,s −Q2
j,s)2 ≤εmin
(30)



<!-- page 9/21 -->

Electronics 2024, 13, 4048
9 of 21
where εmin is a minimal positive value close to zero.
When the model is verified by (30), it is found that the error is much larger than 0
when Equation (8) is used as the objective function, indicating that Equation (8) cannot be
relaxed under this objective function and the objective function needs to be adjusted. When
the objective function is adjusted to verify the effectiveness of second-order cone relaxation,
it is found that the relaxation results satisfy the original constraints when the loss of the
network is reduced by the objective function. Based on the above analysis, the model is
adjusted to a two-stage MISOC model with the maximum PVHC in the first stage and the
minimum network loss in the second stage, as in (31).







max Sv,s



min Ploss,s =
nl
∑
j=1
I2,j,srj
s.t. (15–21), (23–29)
(31)
4. Solution Methodology
The model is divided into two stages. The first stage is the outer max problem, which
maximizes the PVHC. The second stage is the inner layer min problem, which determines
the PV configuration plan, the switch status of each branch, and the power angle of the
inverter to minimize the network loss. To solve this problem, the method of “variable step
size traversal + solver” is adopted, as in Figure 3.
start
Obtain DN topology information
Example Import running scenario information
Set the PVHC to 0kW and step 
size L to 1000kW
Solve the second stage model
              min     Ploss,s
              Sv,i,s,αj,s,θv,i,s
         s.t. (15–21), (23–29)
yes
no
Solvable
Taken the maxium Sv,s as the 
result
Sv,s
 = Sv,s+L
end
L = 1
Sv,s = Sv,s− L
L = L/10,
no
yes
Figure 3. PVHC model solving strategy.



<!-- page 10/21 -->

Electronics 2024, 13, 4048
10 of 21
The specific solution strategy is as follows:
(1)
Input PV output efficiency and load data to obtain the model calculation scenario;
(2)
Set the PVHC to 0 kW and the initial step size to 1000 kW;
(3)
Put it into the second stage model, solve the model, and obtain the PV configuration
plan and the switch state of each branch;
(4)
Judge the safety of the result and calculate the overvoltage margin and overcurrent
margin, as in (32) and (33).
Vout,s = Vmax −max(Vi,s)
Vmax
(32)
Iout,s = Imax −max(Ij,s)
Imax
(33)
where Vout,s and Iout,s are the overvoltage and overcurrent margin;
(5)
If the result does not exceed the safety limit and meets Equation (30), increase the
PVHC by a step and return to step 3;
(6)
If the result makes the overvoltage or overcurrent not satisfy Equation (30) and if the
step is longer than 1, return to the previous PVHC and reduce the step size to one-
tenth of the original, then return to step 3. If the step length is 1, the last solution
result is output, and the PVHC at this time is the result.
5. Case Studies
The model is analyzed using the IEEE 33-bus system and a DN practical case in
Fuzhou, Fujian. The mathematical formulation of the proposed model is programmed in
Python 3.6. The solver is CPLEX 12.8. All the simulations are implemented in a Windows
11 environment with Inter (R) Core (TM) i7-13700 CPU (3.40 GHz, 16 GB RAM).
5.1. IEEE 33-Bus System
5.1.1. Data and Result Analysis
The rated capacity of the IEEE 33-bus system is 10 MVA, the rated voltage is 12.66 kV,
the voltage threshold is [0.95, 1.05] p.u. (expressed by unit value), and the maximum
current is 500 A [39]. The maximum transmission power is 6 MW. The branch and bus data
can be found in ref. [41]. Except for the balance bus, the remaining buses can be installed
PV generators, and the threshold is [100, 800] kW. εmin is set to 10−6. The load types of
buses are shown in Table 2.
According to the impact analysis of PVHC, the moment of output efficiency
[1, 0.9, 0.85, 0.8, 0.75] is selected as the scenario for analysis. Moreover, the moment with
the smallest load is selected as the load of the scene. Based on the above analysis, we have
set five typical scenarios, as shown in Table 3.
Table 2. Bus load type of the IEEE 33-bus system.
Load Type
Buses
Resident
4/7/10/13/16/19/22/25/28/31
Commercial
2/5/8/11/14/17/20/23/26/29/32
Industrial
3/6/9/12/15/18/21/24/27/30/33
Table 3. The bad scenarios of the IEEE 33-bus system.
Scenes
Efficiency
Resident (kW)
Commercial (kW)
Industrial (kW)
1
1
200
160
160
2
0.9
100
130
130
3
0.85
90
140
140
4
0.8
80
160
160
5
0.75
135
140
140



<!-- page 11/21 -->

Electronics 2024, 13, 4048
11 of 21
Without considering the uncertainty and AM (the standby branch disconnection and
θv,i,s are set to 5°), the results of each scenario are shown in Table 4. From the table, we see
that scenario 2 has the smallest PVHC. As such, scenario 2 is the worst scenario in DN,
and the PVHC of the DN is 11.073 MW. Comparing scenarios 2, 3, and 4, it is found that
PVHC increases as the PV output efficiency decreases under similar loads. This indicates
that the PV output efficiency of the worst scenario in which PVHC is calculated should
be as large as possible. Comparing scenarios 1 and 2, although scenario 2 has a smaller
output efficiency, its PVHC is smaller due to its smaller load. This further illustrates that
PVHC is proportional to the load size, and the scenarios with smaller loads are closer to
the worst scenario.
Table 4. Results of the five typical scenarios.
Scenes
Reverse Power (kW)
PVHC (kWp)
Overvoltage (%)
Overcurrent (%)
Relaxation Deviation
1
6000
11,623
2.29
3.70
10−7
2
6000
11,073
2.17
4.06
10−7
3
6000
11,882
1.81
3.84
10−7
4
5921
12,946
2.01
5.26
10−5
5
5373
13,196
2.28
13.94
10−5
The bus voltages and branch currents of each scenario are shown in Figures 4 and 5.
From the figures, it can be found that the voltage is minimum at the balancing bus and
gradually increases towards the PV configuration bus, and that the current is maximum
at the balancing bus and gradually decreases towards the PV configuration bus. This
phenomenon reflects the situation of DN with maximum access to PV. In this case, the RTP
that causes the power flow back occurs, making the voltage and current characteristics
opposite to the original.
Bus
1
4
7
10
13
16
19
22
25
28
31
34
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 Scene 5
Scene 4
Scene 3
Scene 2
Scene 1
1
4
7
10
13
16
19
22
25
28
31
34
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 Scene 5
Scene 4
Scene 3
Scene 2
Scene 1
Voltage/p.u.
Bus
1
4
7
10
13
16
19
22
25
28
31
34
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 
1.00
1.01
1.02
1.03
 Scene 5
Scene 4
Scene 3
Scene 2
Scene 1
Voltage/p.u.
Figure 4. Bus voltage in the five typical scenarios.
0
3
6
9
12
15
18
21
24
27
30
33
36
100
300
500
 
100
300
500
 
100
300
500
 
100
300
500
 
100
300
500
 
Scene 1
Scene 2
Scene 3
Scene 4
Scene 5
0
3
6
9
12
15
18
21
24
27
30
33
36
100
300
500
 
100
300
500
 
100
300
500
 
100
300
500
 
100
300
500
 
Scene 1
Scene 2
Scene 3
Scene 4
Scene 5
Branch
Current/A
0
3
6
9
12
15
18
21
24
27
30
33
36
100
300
500
 
100
300
500
 
100
300
500
 
100
300
500
 
100
300
500
 
Scene 1
Scene 2
Scene 3
Scene 4
Scene 5
Branch
Current/A
Figure 5. Branch current in the five typical scenarios.



<!-- page 12/21 -->

Electronics 2024, 13, 4048
12 of 21
The PV configuration scheme for scenario 2 is shown in Figure 6, and the data format
is bus/capacity (kW). Based on the configuration scheme, PV is mainly configured in the
buses that are near the balance bus, and only a small amount of PV is configured for other
buses. By analyzing the reasons for the above situation, it can be concluded that the strategy
of this paper is to first configure PV in each bus to absorb the load, and then configure PV
in the bus closer to the balance bus for reverse power supply. This strategy can effectively
shorten the power flow and alleviate the rise of voltage and current in the DN.
1/0
2/800
3/800
4/800
5/800
6/755
7/0
8/0
9/143
10/112
11/144
12/337
13/113
14/179
15/0
16/140
17/144
18/134
19/800
20/800
21/800
22/576
23/800
24/800
25/331
26/144
27/144
28/111
29/155
30/144
31/111
32/144
33/155
1/0
2/800
3/800
4/800
5/800
6/755
7/0
8/0
9/143
10/112
11/144
12/337
13/113
14/179
15/0
16/140
17/144
18/134
19/800
20/800
21/800
22/576
23/800
24/800
25/331
26/144
27/144
28/111
29/155
30/144
31/111
32/144
33/155
Figure 6. PV configuration scheme in scenario 2.
Taking scenario 2 as the base scenario, the paper analyzes the model validity, uncer-
tainty, sensitivity, and AM method as follows.
5.1.2. The Validity Analysis
We adjust the objective function of the model to the maximum PVHC and the maxi-
mum reverse power, and the relaxation deviation of the results are 3.831 and 4.216, respec-
tively. The result shows that second-order cone relaxation cannot be used to linearize the
model when the PVHC maximum is the objective function directly. The relaxation deviation
of the two-stage model established in this paper is less than 10 with the minimum loss as
the objective function. The two-stage model constructed in this paper aims to maximize the
PVHC in the first stage and minimize the loss in the second stage. The linearized model is
solved in the second stage, and the relaxation deviation is less than 10−5. It shows that the
results obtained by the model constructed in this paper still satisfy the original constraints.
5.1.3. The Uncertainty Analysis
This paper has concluded in the result analysis that the worst scenario has larger out-
put efficiency and smaller load. Therefore, only the uncertainty that stems from increasing
the output efficiency or decreasing load can make the scenario worse. And the worst uncer-
tainty scenario is the one with maximum output efficiency and minimum load. To prove
this conclusion, the output efficiency and load are adjusted respectively for comparative
analysis. The results are shown in Figure 7, where the horizontal coordinate represents the
adjustment ratio of efficiency or load. From the figure, it can be intuitively seen that PVHC
is inversely proportional to efficiency and proportional to load, and efficiency affects PVHC
more than load.



<!-- page 13/21 -->

Electronics 2024, 13, 4048
13 of 21
−5%
−2%
0
2%
5%
10,400
10,600
10,800
11,000
11,200
11,400
11,600
11,800
PVHC
Load
Efficiency
−5%
−2%
0
2%
5%
10,400
10,600
10,800
11,000
11,200
11,400
11,600
11,800
PVHC
Load
Efficiency
Figure 7. Uncertainty analysis results.
5.1.4. The Sensitivity Analysis
(1)
Maximum current.
In scenario 2, we set the maximum current to [300, 400, 500, 600, 700] A, and the
calculated results are shown in Table 5. It can be seen that the PVHC increases as the
maximum current increases from 300 to 500. But, when the maximum current is from
500 to 700, the PVHC does not increase. This is because PVHC is mainly limited by current
risk when the maximum current is low. Therefore, PVHC increases with the increase in
the maximum current. But, when the maximum current is high enough, PVHC is mainly
limited by the maximum reverse power, so that the PVHC does not increase with the
maximum current. After accurate calculation, the critical maximum current of the above
two cases is 480 A.
Table 5. Sensitivity analysis results of maximum current.
Current Maximum (A)
Reverse Power (kW)
PVHC (kWp)
Overvoltage (%)
Overcurrent (%)
300
3743
8482
3.63
0
400
4996
9909
3.03
0
500
6000
11,073
2.17
4.06
600
6000
11,073
2.17
20.05
700
6000
11,073
2.17
47.97
(2)
Maximum voltage.
We set the maximum voltage to [1.02, 1.03, 1.04, 1.05, 1.06] p.u.; the calculated results
are shown in Table 6. When the maximum voltage comparison is small, PVHC will increase
with the increase in the maximum voltage. But, when the maximum voltage is large, PVHC
does not increase. The critical maximum voltage of the above two cases is 1.0253 p.u..
Table 6. Sensitivity analysis results of maximum voltage.
Maximum Voltage (p.u.)
Reverse Power (kW)
PVHC (kWp)
Overvoltage (%)
Overcurrent (%)
1.02
5312
10,272
0
14.98
1.03
6000
11,073
0.27
4.06
1.04
6000
11,073
1.23
4.06
1.05
6000
11,073
2.17
20.05
1.06
6000
11,073
3.09
47.97
(3)
Maximum transmission power.
We set the maximum transmission power to [5, 5.5, 6, 6.5, 7] MW; the calculated
results are shown in Table 7. From the table, it can be seen that the PVHC increases with
the increase in the maximum transmission power before the critical value. But, when the
maximum transmission power reaches 6.256 MW, the overcurrent is 0, and the PVHC will
not increase again.



<!-- page 14/21 -->

Electronics 2024, 13, 4048
14 of 21
Table 7. Sensitivity analysis results of maximum transmission power.
Maximum Transmission
Power (MW)
Reverse Power (MW)
PVHC (kWp)
Overvoltage (%)
Overcurrent (%)
5
5
9915
2.86
19.90
5.5
5.5
10,490
2.71
11.98
6
6
11,073
2.17
4.06
6.5
6.256
11,365
2.18
0
7
6.256
11,365
2.18
0
(4)
The inverse angle.
We set θv,i,s to [−5, −2, 2, 5] MW; the calculated results are shown in Table 8. From the
table, if can be found that the fixed θv,i,s has little effect on PVHC. But, when a is close to 0,
the current of DN will decrease, which can effectively alleviate the risk of overcurrent.
Table 8. Sensitivity analysis results of the inverse angle.
θv,i,s
Reverse Power (kW)
PVHC (kWp)
Overvoltage (%)
Overcurrent (%)
−5
6000
11,080
2.67
3.64
−2
6000
11,070
2.58
46.20
2
6000
11,072
2.21
47.80
5
6000
11,073
2.17
4.06
5.1.5. The AM Methods Analysis
We set 3 cases to compare with the original results. Case 1 considers network recon-
figuration, and case 2 considers SVC, which can adjust θv,i,s between −5° and 5°. Case
3 considers both network reconfiguration and SVC. The results are shown in Table 9.
From the table, we can see that the difference between the results that take AM methods
and the original results is low. We think that this condition occurs because the PVHC of the
original DN system is mainly limited by the maximum transmission power, which cannot
be improved by AM methods.
Table 9. The AM methods analysis results of the original DN.
Case
Origin
1
2
3
AM
None
Reconfiguration
SVC
Both
Reverse power (kW)
6000
6000
6000
6000
PVHC (kWp)
11,073
11,067
11,072
11,069
Overvoltage (%)
2.17
2.39
2.24
2.52
Overcurrent (%)
4.06
4.36
4.82
4.80
Off branches
33/34/35/36/37
8/13/25/32/33
33/34/35/36/37
9/25/33/34/36
From the inverse angle sensitivity analysis, we see that SVC can alleviate the risk of
overcurrent. To verify this conclusion, we decrease the maximum current to 300 A, which
makes the DN more prone to overcurrent risk, and then compare the effects of the AM
methods again. The results are shown in Table 10. It can be seen that the SVC increases the
PVHC by 45 kW, but the effect of network reconfiguration is still low.
Based on the original system, the maximum voltage is adjusted to 1.02 p.u. The com-
parison between the results of the AM method and the original results is shown in Table 11.
From the table, we can see that both network reconfiguration and SVC can increase the
PVHC in the DN that is more prone to overvoltage. And SVC can increase the PVHC by
400 kW, while network reconfiguration increases the PVHC by 60 kW. This means that AM
methods are more effective in DN, which is prone to overvoltage.



<!-- page 15/21 -->

Electronics 2024, 13, 4048
15 of 21
Table 10. The AM methods analysis results of the overcurrent DN.
Case
Origin
1
2
3
AM
None
Reconfiguration
SVC
Both
Reverse power (kW)
3743
3735
3790
3790
PVHC (kWp)
8482
8471
8527
8529
Overvoltage (%)
3.63
3.60
3.81
3.80
Overcurrent (%)
0
0
0
0
Off branches
33/34/35/36/37
10/14/16/28/33
33/34/35/36/37
6/8/11/12/27
Table 11. The AM methods analysis results of the overvoltage DN.
Case
Origin
1
2
3
AM
None
Reconfiguration
SVC
Both
Reverse power (kW)
5312
5364
5674
5744
PVHC (kWp)
10,272
10,330
10,685
10,766
Overvoltage (%)
0
0
0
0
Overcurrent (%)
14.98
14.48
10.08
8.94
Off branches
33/34/35/36/37
11/14/17/27/33
33/34/35/36/37
6/8/13/26/37
5.2. Practical Case
To further demonstrate the applicability and practicability of the model, the PVHC
calculation model is applied in a practical case. As shown in Figure 8, the practical case
consists of 17 buses and 20 branches, in which branches 17, 18, 19, 20 are the spare branches.
In this system, the output efficiency is 0.9, and the resident, commercial, and industrial
loads are 200, 160, and 160 kW. The load type of buses is shown in Table 12, and the branch
data are shown in Table 13. The maximum transmission power is 7 MW. The data not
mentioned are the same as the IEEE 33-bus system. Four cases are set up according to the
type of AM method taken, and the calculation results are shown in Table 14.
From Table 14, it can be seen that the SVC increases the PVHC by 166 kW, which is
similar to the results of the IEEE 33-bus system. But network reconfiguration increased
the PVHC by 3272 kW, which is much larger than the IEEE 33-bus system. As for the
completely different effects of network reconfiguration in the two cases, we think that
these are due to the difference in the branch networks of each case. The branch network
in the IEEE 33-bus system is superior, so the effect of network reconfiguration on PVHC
improvement is small, while the branch network in the practical case is not suitable for the
situation of a large number of PV access, so the network reconfiguration can effectively
improve PVHC. Based on the above analysis, it can be concluded that SVC can improve
the PVHC, but the effect is mediocre. For systems with poor branch networks, network
reconfiguration can significantly increase PVHC by more than 50%.
110kV gate transfomer
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
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
Operating branch
Stanbdy branch
110kV gate transfomer
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
HW
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
Operating branch
Stanbdy branch
Figure 8. Topology of the practical case.



<!-- page 16/21 -->

Electronics 2024, 13, 4048
16 of 21
Table 12. Bus load type in the practical case.
Load Type
Buses
Resident
5/6/12/14/15
Commercial
4/7/9/10/11/13/16/17
Industrial
2/3/8
Table 13. Branch data for the practical case.
Branch
Begin Bus
End Bus
Resistance (Ω)
Reactance (Ω)
1
1
2
0.3431
0.1909
2
2
3
0.2244
0.1249
3
2
4
0.3392
0.1887
4
4
5
0.2494
0.1388
5
4
6
0.3292
0.1832
6
6
7
0.1496
0.0833
7
6
8
0.0948
0.0527
8
4
9
0.3392
0.1887
9
9
10
0.1692
0.0944
10
10
11
0.3611
0.2009
11
11
12
0.1337
0.0744
12
10
13
0.3641
0.2026
13
13
14
0.2244
0.1249
14
14
15
0.3112
0.1732
15
13
16
0.2025
0.1127
16
16
17
0.2753
0.1532
17
5
7
0.3392
0.1887
18
8
12
0.3392
0.1887
19
12
15
0.3392
0.1887
20
14
17
0.3392
0.1887
Table 14. The AM methods analysis results in the practical case.
Case
1
2
3
4
AM
None
Reconfiguration
SVC
Both
Reverse power (kW)
3378
6201
3521
6242
PVHC (kWp)
6873
10,145
7039
10,189
Overvoltage (%)
3.31
1.45
3.34
7.30
Overcurrent (%)
45.62
0
43.96
0
Off branches
17/18/19/20
6/11/13/16
17/18/19/20
6/11/14/15
5.3. Comparison of Solution Methods
The second-order cone relaxation method is adopted in the linearization. If the
model is solved directly, the relaxation deviation will be too large, resulting in the original
constraint becoming invalid. For this case, ref. [28] reduces the relaxation deviation by
iterative approximation. And the method proposed in this paper solves this problem by
constructing a two-stage model. In the second stage, the minimum loss is the goal while
trying to ensure the effectiveness of second-order cone relaxation, and, in the first stage,
the maximum PVHC is the goal while trying to obtain the calculation results. The results
of the two methods are listed in Table 15.
In the IEEE 33-bus system, the PVHC obtained by the two methods is almost the same
when the AM is not adopted. However, the PVHC obtained in ref. [28] is larger than that
in this paper after AM is adopted. The above situation occurs because the method in this
paper limits the loss. Therefore, different from ref. [28], the method in this paper does
not increase the PVHC by increasing the loss. In the practical case, ref. [28] already has
relatively large losses without considering the AM. The reason for this difference may be
the same as previously analyzed, from the point of loss, the branch network of IEEE 33-bus
system is better than the practical case. Therefore, the configuration of PV is not enough to
increase the loss of IEEE 33-bus system. Based on the above analysis, we conclude, only
from the PVHC calculation effect, that the method in ref. [28] is better. But, if the branch
network and loss are considered, the method in this paper is more effective.



<!-- page 17/21 -->

Electronics 2024, 13, 4048
17 of 21
Table 15. Results of the different methods.
Methods
Ref. [28]
This Paper
PVHC (kWp)
Loss (kW)
Relaxation
Deviation
PVHC (kWp)
Loss (kW)
Relaxation
Deviation
IEEE 33-bussystem
No AM
11,362
137
10−14
11,365
113
10−14
With AM
11,777
432
10−12
11,420
112
10−13
Practical case
No AM
7935
782
10−4
6873
48
10−6
With AM
11,030
943
10−4
10,189
167
10−9
6. Conclusions
Calculating and improving the PVHC is conducive to the orderly development of
the PV industry and the construction of green power grids. This paper presents a PVHC
calculation model and improvement method considering the uncertainty of source load
to achieve PVHC calculation as truly and accurately as possible. We have analyzed the
effectiveness of the model by the IEEE 33-bus system and practical case, and then obtained
the following conclusions:
(1)
The established calculation model of PVHC can ensure that all the constraints are not
exceeded, and the DN can operate safely and stably under the obtained PVHC;
(2)
The PVHC is affected by the load and PV power generation efficiency. The smaller the
load and the larger the PV power generation efficiency, the smaller the PVHC obtained;
(3)
To shorten the power flow and alleviate the rise of voltage and current, the strategy of
this paper is to first configure PV in each bus to absorb the load, and then configure
PV in the bus closer to the balance bus for reverse power supply;
(4)
SVC can improve the PVHC, but the effect is mediocre. For systems with poor branch
networks, network reconfiguration can significantly increase PVHC by more than 50%.
In order to solve the problem of calculating the PVHC, this paper discusses the
calculation method of PVHC by considering RTP and uncertainty and analyzes the AM
methods to improve PVHC. The PVHC calculation model significantly guides the PV
configuration of the distribution network. However, there are still many factors that are not
taken into account in the model constructed in this paper. New modules in DN systems
such as energy storage and EVs can increase the flexibility of the system and, thus, improve
the PVHC. And, in the real world, various system faults will reduce the PVHC. If these are
taken into account, the model will be more accurate. Moreover, due to ownership issues,
the distributed system operator does not have access to individual PV installations, making
the configuration of PV capacity not fully controllable, so the practical feasibility of the
PVHC calculation model needs to be further investigated. In the future, we will add the
energy storage and EVs models of DN system into the calculation model, and collect the
faults that may occur in the DN system to make the results more accurate and reliable.
In addition, we will further study the practical and feasible method for producing a PVHC
calculation model.
Author Contributions: Conceptualization, T.L. and G.W.; methodology, Z.H.; software, G.W.; valida-
tion, T.L., G.W., S.L. and Z.H.; formal analysis, S.L.; investigation, T.L.; resources, T.L.; data curation,
T.L.; writing—original draft preparation, H.H.; writing—review and editing, H.H.; visualization, T.L.;
supervision, T.L. and Z.H.; project administration, Z.H.; funding acquisition, Z.H. All authors have
read and agreed to the published version of the manuscript.
Funding: This research is funded by National Key R&D Program of China of 2022YFE0205300 and
the Special Research Program of the Economic and Technology Research Institute of State Grid Fujian
Electric Power Co., Ltd. of SGFJJY00GHJS2310137.
Informed Consent Statement: Informed consent was obtained from all subjects involved in the study.
Data Availability Statement: The original contributions presented in the study are included in the
article, further inquiries can be directed to the corresponding author.



<!-- page 18/21 -->

Electronics 2024, 13, 4048
18 of 21
Acknowledgments: The authors would also like to thank the anonymous reviewers for their valuable
comments and suggestions to improve the quality of the paper.
Conflicts of Interest: Authors Tingting Lin, Guilian Wu and Sudan Lai were employed by the
companies State Grid Fujian Electric Power Co., Ltd. and Distribution Network Planning and
Operation Control Technology in Multiple Disaster Superimposed Areas State Grid Corporation
Laboratory, Ltd. The remaining authors declare that the research was conducted in the absence of
any commercial or financial relationships that could be construed as a potential conflict of interest.
Nomenclature of Symbols and Abbreviations
Abbreviations
PV
Photovoltaic
DN
Distribution Network
PVHC
Photovoltaic Hosting Capacity
MISOC
Mixed-Integer Second-Order Cone
RTP
Reverse Transmission Phenomenon
AM
Active Management
SVC
Static Var Compensators
PSO
Particle Swarm Optimization
GA
Genetic Algorithm
NSGA-II
Non-dominated Sorting Genetic Algorithm II
MOAGWO
Multi-Objective Advanced Gray Wolf Optimization
OLTC
On-Load-Tap-Changers regulation
SOP
Soft Open Point
EVs
Electric Vehicles
C&CG
Column-and-Constraint Generation
Sets
I
Set of buses, indexed by i , and I = {1,2,. . . ,nb}
J
Set of branches, indexed by j, and J = {1,2,. . . ,nl}
S
Set of scenarios, indexed by s
Ωup,i
the branch set with bus i as the start bus
Ωdown,i
the branch set with bus i as the end bus
Parameters
φv,s
Actual PV power generation efficiency in scenario s
φ′v,s
Predicted PV power generation efficiency in scenario s
∆φv+,s
Upward deviation value of PV power generation efficiency in scenario s
∆φv−,s
Downward deviation value of PV power generation efficiency in scenario s
αv+,s
Upward deviation coefficient of PV power generation efficiency in scenario s
αv−,s
Downward deviation coefficient of PV power generation efficiency in scenario s
Pv,i,s
PV power generation of scenario s and bus i
Pd,i,s
Actual load of scenario s and bus i
P′
d,i,s
Predicted load of scenario s and bus i
∆Pd+,i,s
Upward deviation value of load of scenario s and bus i
∆Pd−,i,s
Downward deviation value of load of scenario s and bus i
αd+,i,s
Upward deviation coefficient of load of scenario s and bus i
αd−,i,s
Downward deviation coefficient of load of scenario s and bus i
Pv,s
Total PV generation of all buses in scenario s
Pd,s
Total load of all buses in scenario s
Ploss,s
Total loss in scenario s
Pup,s
Power transmission from the DN to the upper power network in scenario s
Sv
PVHC
φvmax,s
The maximum PV power generation efficiency in scenario s
Pdmin,i,s
The minimum load of scenario s and bus i
Qv,i,s
PV reactive power generation of scenario s and bus i
Qd,i,s
Reactive load of scenario s and bus i
rj
Resistance of branch j
xj
Reactance of branch j



<!-- page 19/21 -->

Electronics 2024, 13, 4048
19 of 21
Qup,s
Reactive power transmission from the DN to the upper power network
in scenario s
Vmin
Minimum voltage threshold
Vmax
Maximum voltage threshold
Imax
Maximum current threshold
Pup,max
Maximum transmission power threshold
Sv,min
Minimum PV configuration capacity
Sv,max
Maximum PV configuration capacity
θv,max
Maximum inverse angle
ϵg
Arbitrary number
ϵmin
A minimal positive value close to zero
M
A maximal positive value
Vout,s
Overvoltage margin of scenario s
Iout,s
Overcurrent margin of scenario s
Variables
Sv,i,s
PV configuration capacity of scenario s and bus i
Pj,s
Active power of scenario s and branch j
Qj,s
Reactive power of scenario s and branch j
Ij,s
Current of scenario s and branch j
Vi,s
Voltage of scenario s and bus i
θv,i,s
Inverse angle of scenario s and bus i
Fj,s
Virtual power of scenario s and branch j
αj,s
Branch switch status of scenario s and branch j
I2,j,s
Square of current of scenario s and branch j
V2,i,s
Square of voltage of scenario s and bus i
References
1.
Poulek, V.; Aleš, Z.; Finsterle, T.; Libra, M.; Beránek, V.; Severová, L.; Belza, R.; Mrázek, J.; Kozelka, M.; Svoboda, R. Reliability
characteristics of first-tier photovoltaic panels for agrivoltaic systems–practical consequences Int. Agrophys. 2024, 38, 383–391.
[CrossRef] [PubMed]
2.
Alturki, M.; Khodaei, A.; Paaso, A.; Bahramirad, S. Optimization-based distribution grid hosting capacity calculations. Appl.
Energy 2018, 219, 350–360. [CrossRef]
3.
Chathurangi, D.; Jayatunga, U.; Perera, S.; Agalgaonkar, A.; Siyambalapitiya, T. A nomographic tool to assess solar PV hosting
capacity constrained by voltage rise in low-voltage distribution networks. Int. J. Electr. Power Energy Syst. 2022, 134, 107409.
[CrossRef]
4.
Shayani, R.A.; de Oliveira, M.A.G. Photovoltaic Generation Penetration Limits in Radial Distribution Systems. IEEE Trans. Power
Syst. 2011, 26, 1625–1631. [CrossRef]
5.
Alyami, S.; Wang, Y.; Wang, C.; Zhao, J.; Zhao, B. Adaptive Real Power Capping Method for Fair Overvoltage Regulation of
Distribution Networks With High Penetration of PV Systems. IEEE Trans. Smart Grid 2014, 5, 2729–2738. [CrossRef]
6.
Olivier, F.; Aristidou, P.; Ernst, D.; Van Cutsem, T. Active Management of Low-Voltage Networks for Mitigating Overvoltages
Due to Photovoltaic Units. IEEE Trans. Smart Grid 2016, 7, 926–936. [CrossRef]
7.
Georgilakis, P.S.; Hatziargyriou, N.D. Optimal Distributed Generation Placement in Power Distribution Networks: Models,
Methods, and Future Research. IEEE Trans. Power Syst. 2013, 28, 3420–3428. [CrossRef]
8.
Khodaei, A.; Shahidehpour, M. Microgrid-Based Co-Optimization of Generation and Transmission Planning in Power Systems.
IEEE Trans. Power Syst. 2013, 28, 1582–1590. [CrossRef]
9.
Wu, H.; Yuan, Y.; Zhang, X.; Miao, A.; Zhu, J. Robust comprehensive PV hosting capacity assessment model for active distribution
networks with spatiotemporal correlation. Appl. Energy 2022, 323, 119558. [CrossRef]
10.
Munikoti, S.; Abujubbeh, M.; Jhala, K.; Natarajan, B. A novel framework for hosting capacity analysis with spatio-temporal
probabilistic voltage sensitivity analysis. Int. J. Electr. Power Energy Syst. 2022, 134, 107426. [CrossRef]
11.
Zhao, L.; Feng, C.; Lu, Z.; Wang, Z.; Zhao, J.; Du, T. Evaluation of distribution network carrying capacity considering multi
distributed resource access. In Proceedings of the 2022 IEEE 10th Joint International Information Technology and Artificial
Intelligence Conference (ITAIC), Chongqing, China, 17–19 June 2022; Volume 10, pp. 328–332. [CrossRef]
12.
Liu, X.; Ye, S.; Long, C.; Liu, L.; Li, D.; Li, H.; Pan, Y. Active Distribution Network Grid Expansion planning Technology Based on
Power Grid Carrying Capacity Improvement. In Proceedings of the 2022 2nd International Conference on Intelligent Technology
and Embedded Systems (ICITES), Chengdu, China, 23–26 September 2022; pp. 48–54. [CrossRef]
13.
Zhao, Y.; Chen, F.; Li, Z.; Zhu, M.; Xie, T. Optimal dispatch of distribution network considering comprehensive carrying capacity.
In Proceedings of the 2022 IEEE 10th Joint International Information Technology and Artificial Intelligence Conference (ITAIC),
Chongqing, China, 17–19 June 2022; Volume 10, pp. 333–337. [CrossRef]



<!-- page 20/21 -->

Electronics 2024, 13, 4048
20 of 21
14.
Zhang, X.; Zhang, Z.; Gong, X. Study on Consumption Capability of Large-Scale Photovoltaic Access to Regional Distribution
Network.
In Proceedings of the 2018 China International Conference on Electricity Distribution (CICED), Tianjin, China,
17–19 September 2018; pp. 2153–2157. [CrossRef]
15.
Huangfu, X.; Li, Q.; Ding, Y.; Guo, Y.; Zhao, H.; Li, C.; Sun, D.; Wang, D.; Hou, X.; Fan, J. Evaluation Method of Distributed
Photovoltaic Admission Capability Based on Voltage Sensitivity and Multi-Scenario Power Flow Simulation. In Proceedings
of the 2022 IEEE 5th International Electrical and Energy Conference (CIEEC), Nanjing, China, 27–29 May 2022; pp. 257–262.
[CrossRef]
16.
Yu, H.; Li, K.; Guo, X.; Quan, S.; Zhao, H.; Zhu, X.; Li, C.; Zhu, W.; Yan, J.; Gao, K. Evaluation Method of Distributed
Photovoltaic Carrying Capacity in Distribution Network Based on Voltage Sensitivity Ranking. In Proceedings of the 2022 IEEE
5th International Electrical and Energy Conference (CIEEC), Nanjing, China, 27–29 May 2022; pp. 238–243. [CrossRef]
17.
Tao, Y.; Xu, M.; Zhang, J.; Tan, J.; Guo, Z.; Yuan, Z. Research on Calculation and Lifting Method of Distribution Network
Hosting Capacity under High Permeability New Energy Access. In Proceedings of the 2022 IEEE 5th International Conference
on Automation, Electronics and Electrical Engineering (AUTEEE), Shenyang, China, 18–20 November 2022; pp. 1002–1007.
[CrossRef]
18.
Gu, T.; Lv, Q.; Fan, Q.; Li, B.; Lin, C.; Zhang, H.; Mao, J. Two-stage distributionally robust assessment method for distributed PV
hosting capacity of flexible distribution networks. Energy Rep. 2024, 11, 2266–2278. [CrossRef]
19.
Mulenga, E.; Etherden, N. Multiple distribution networks hosting capacity assessment using a stochastic approach. Sustain.
Energy Grids Netw. 2023, 36, 101170. [CrossRef]
20.
Qammar, N.; Arshad, A.; Miller, R.J.; Mahmoud, K.; Lehtonen, M. Probabilistic hosting capacity assessment towards efficient
PV-rich low-voltage distribution networks. Electr. Power Syst. Res. 2024, 226, 109940. [CrossRef]
21.
Palacios-Garcia, E.J.; Moreno-Muñoz, A.; Santiago, I.; Moreno-Garcia, I.M.; Milanés-Montero, M.I. PV Hosting Capacity Analysis
and Enhancement Using High Resolution Stochastic Modeling. Energies 2017, 10, 1488. [CrossRef]
22.
Cho, Y.; Lee, E.; Baek, K.; Kim, J. Stochastic Optimization-Based hosting capacity estimation with volatile net load deviation in
distribution grids. Appl. Energy 2023, 341, 121075. [CrossRef]
23.
Ismael, S.M.; Abdel Aleem, S.H.; Abdelaziz, A.Y.; Zobaa, A.F. State-of-the-art of hosting capacity in modern power systems with
distributed generation. Renew. Energy 2019, 130, 1002–1020. [CrossRef]
24.
Jaramillo-Leon, B.; Zambrano-Asanza, S.; Franco, J.F.; Soares, J.; Leite, J.B. Allocation and smart inverter setting of ground-
mounted photovoltaic power plants for the maximization of hosting capacity in distribution networks. Renew. Energy 2024,
223, 119968. [CrossRef]
25.
Kazemi-Robati, E.; Sepasian, M.S.; Hafezi, H.; Arasteh, H. PV-hosting-capacity enhancement and power-quality improvement
through multiobjective reconfiguration of harmonic-polluted distribution systems.
Int. J. Electr. Power Energy Syst. 2022,
140, 107972. [CrossRef]
26.
Ahmadi, B.; Ceylan, O.; Ozdemir, A. Reinforcement of the distribution grids to improve the hosting capacity of distributed
generation: Multi-objective framework. Electr. Power Syst. Res. 2023, 217, 109120. [CrossRef]
27.
Chen, X.; Wu, W.; Zhang, B. Robust Capacity Assessment of Distributed Generation in Unbalanced Distribution Networks
Incorporating ANM Techniques. IEEE Trans. Sustain. Energy 2018, 9, 651–663. [CrossRef]
28.
Zhang, S.; Fang, Y.; Zhang, H.; Cheng, H.; Wang, X. Maximum Hosting Capacity of Photovoltaic Generation in SOP-Based Power
Distribution Network Integrated With Electric Vehicles. IEEE Trans. Ind. Informatics 2022, 18, 8213–8224. [CrossRef]
29.
Solat, S.; Aminifar, F.; Shayanfar, H. Distributed generation hosting capacity in electric distribution network in the presence of
correlated uncertainties. IET Gener. Transm. Distrib. 2020, 15, 836–848. [CrossRef]
30.
Rabiee, A.; Mohseni-Bonab, S.M. Maximizing hosting capacity of renewable energy sources in distribution networks: A
multi-objective and scenario-based approach. Energy 2017, 120, 417–430. [CrossRef]
31.
Yao, H.; Qin, W.; Jing, X.; Zhu, Z.; Wang, K.; Han, X.; Wang, P. Possibilistic evaluation of photovoltaic hosting capacity on
distribution networks under uncertain environment. Appl. Energy 2022, 324, 119681. [CrossRef]
32.
Zou, Y.; Xu, Y.; Li, J. Aggregator-Network Coordinated Peer-to-Peer Multi-Energy Trading via Adaptive Robust Stochastic
Optimization. IEEE Trans. Power Syst. 2024, 1–13. [CrossRef]
33.
Zheng, X.; Khodayar, M.E.; Wang, J.; Yue, M.; Zhou, A. Distributionally Robust Multistage Dispatch with Discrete Recourse of
Energy Storage Systems. IEEE Trans. Power Syst. 2024, 1–14. [CrossRef]
34.
Lee, J.; Bérard, J.P.; Razeghi, G.; Samuelsen, S. Maximizing PV hosting capacity of distribution feeder microgrid. Appl. Energy
2020, 261, 114400. [CrossRef]
35.
Xu, X.; Li, J.; Xu, Z.; Zhao, J.; Lai, C.S. Enhancing photovoltaic hosting capacity—A stochastic approach to optimal planning of
static var compensator devices in distribution networks. Appl. Energy 2019, 238, 952–962. [CrossRef]
36.
Lazo, J.; Watts, D. Stochastic model for active distribution networks planning: An analysis of the combination of active network
management schemes. Renew. Sustain. Energy Rev. 2024, 191, 114156. [CrossRef]
37.
Xiang, Y.; Dai, J.; Xue, P.; Liu, J. Autonomous topology planning for distribution network expansion: A learning-based decoupled
optimization method. Appl. Energy 2023, 348, 121522. [CrossRef]
38.
Mejia, M.A.; Macedo, L.H.; Muñoz-Delgado, G.; Contreras, J.; Padilha-Feltrin, A. Active distribution system planning considering
non-utility-owned electric vehicle charging stations and network reconfiguration. Sustain. Energy Grids Netw. 2023, 35, 101101.
[CrossRef]



<!-- page 21/21 -->

Electronics 2024, 13, 4048
21 of 21
39.
Feizi, M.R.; Yin, S.; Khodayar, M.E. Solar photovoltaic dispatch margins with stochastic unbalanced demand in distribution
networks. Int. J. Electr. Power Energy Syst. 2022, 140, 107976. [CrossRef]
40.
Takenobu, Y.; Yasuda, N.; Minato, S-i.; Hayashi, Y. Scalable enumeration approach for maximizing hosting capacity of distributed
generation. Int. J. Electr. Power Energy Syst. 2019, 105, 867–876. [CrossRef]
41.
Albaker, A.; Alturki, M.; Abbassi, R.; Alqunun, K. Zonal-Based Optimal Microgrids Identification. Energies 2022, 15, 2446.
[CrossRef]
Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
