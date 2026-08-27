<!--
source: D1_容载比理论/Optimal substation capacity planning method in high-density load.pdf
sha256: cbdbe48d984b0f88be1c66bbc95dff4ac5fc378aab4716b4618f1ce5f457dc85
method: pymupdf
pages: 11
-->

<!-- page 1/11 -->

Available online at www.sciencedirect.com
ScienceDirect
Energy Reports 9 (2023) 1520–1530
www.elsevier.com/locate/egyr
2022 International Conference on Frontiers of Energy and Environment Engineering, CFEEE
2022, 16–18 December, 2022, Beihai, China
Optimal substation capacity planning method in high-density load
areas considering renewable energy
Jianhua Huanga, Zhanyu Sunb, Haohui Xiea, Jiahao Dengb, Huilin Ouyanga,
Zhaobin Dub,∗, Nanxing Chenb
a Dongguan Electric Power Design Institute Co., Ltd, Dongguan, China
b School of Electric Power, South China University of Technology, Guangzhou, China
Received 30 March 2023; accepted 10 April 2023
Available online 25 April 2023
Abstract
With the increasing penetration of renewable energy, the adaptability of the existing substation planning model in terms
of capacity and quantity of transformer needs to be further studied when preferring large-capacity substations. Considering
the variations of renewable energy penetration rate and load, this paper proposes a method to optimize the total capacity of
substations in distribution networks. This paper introduces the influence of renewable energy access on power supply reliability
and introduces the idea of partitioning for economic analysis of reliability. An economic analysis model for simultaneously
optimizing the capacity and quantity of substation transformer in the distribution network is constructed, taking into account
the effects of reducing net load and enhancing the reliability of the distribution feeders resulting from renewable energy access
to the medium and low voltage side of the substation. Various wiring means of the distribution network are retained and the
impact of renewable energy access on the reliability of the network power supply is quantified. The optimization model is
solved by the multivariate universe optimizer(MVO) algorithm with stronger optimality finding capability and short solving
time. Finally, the case study results of a regional distribution network are employed to demonstrate and verify the validity and
rationality of the method.
© 2023 The Authors. Published by Elsevier Ltd. This is an open access article under the CC BY-NC-ND license
(http://creativecommons.org/licenses/by-nc-nd/4.0/).
Peer-review under responsibility of the scientific committee of the 2022 International Conference on Frontiers of Energy and Environment
Engineering, CFEEE, 2022.
Keywords: Large capacity substation; Renewable energy; Multivariate universe optimizer; Reliability; Economic analysis
1. Introduction
With the rapid development of modern society, the urban load density increases continuously, resulting in
transformers in frequently heavy-loaded condition and more demand for substations and land. For instance, the
maximum electricity load of the Guangdong power grid, as the load center of the southern region of China, is
∗Corresponding author.
E-mail address:
epduzb@scut.edu.cn (Z. Du).
https://doi.org/10.1016/j.egyr.2023.04.104
2352-4847/© 2023 The Authors.
Published by Elsevier Ltd. This is an open access article under the CC BY-NC-ND license (http:
//creativecommons.org/licenses/by-nc-nd/4.0/).
Peer-review under responsibility of the scientific committee of the 2022 International Conference on Frontiers of Energy and Environment
Engineering, CFEEE, 2022.



<!-- page 2/11 -->

J. Huang, Z. Sun, H. Xie et al.
Energy Reports 9 (2023) 1520–1530
expected to be 173,000 MW in 2025 and there will be 2365 substations of 110 kV voltage level with a capacity
of 252,140 MVA. In order to solve the contradiction between grid substations construction and land shortage in
developed areas, it is necessary to allocate larger capacity substations for loads, so as to reduce the resources
occupation of stations and lines and ensure that the planning schemes can be implemented in time.
Large capacity substations in terms of capacity and quantity of transformer can increase the power supply
capability of a closed area, but also require a greater number of incoming and outgoing lines from different voltage
levels. Further, the capacity and scale of main transformers can perform well in need of the match of the number of
wiring and proper wiring types, which are related to the economy and reliability from the perspective of network
interconnection strength. Therefore, it is necessary to consider substation scale impact on different operation and
management indicators, such as load rate, loss and reliability, etc. Ref. [1] points out that different wiring structures
have different effects on power supply reliability, in terms of ring rate and component failure rate. Ref. [2] indicates
that the scale of urban distribution systems is growing, and additional losses may occur due to improper grid
structures.
Clearly, the increasing penetration of renewable energy affects the selection of substation capacity for the net
load to be put down. However, the uncertain generating way of renewable energy featured by salient randomness
cannot exert its full capacity just as its rated power. In addition, the renewable energy can also bring positive
effects to the reliability improvement of the distribution network, and appropriately reduce the requirements for
substation capacity under the maintenance of power supply reliability targets [3,4]. When a fault occurs on some
middle point of the section line, the fault and the affected portion of the line are disconnected from the substation,
while the end part of the line in a single source wire structure must fail. But such power failure can be reduced
or even avoided when renewable energy sources access parts of the distribution network. Ref. [5] proposes that
distributed photovoltaic integrated to the distribution network can improve the reliability of the original system.
With the increase of distributed photovoltaic capacity, all of the average outage time, the frequency of outages and
the average outage power of the system decrease gradually. Therefore, it is necessary for system planners to study
the coordination between substation capacity optimization and renewable energy consumption in high-density load
areas.
Existing substation planning models can be divided into two categories. The first category mainly focused on
the optimal locations and capacity of the substation. Ref. [6] presents a new model for the optimal locations and
capacity of substations based on the whole life cycle cost of equipment. It involves the one-time investment cost
of the substation, the operation and maintenance cost of the system, the failure cost and the disposal cost. Ref. [7]
considers the minimum investment and annual operating cost as the objective function to determine the location
of the substation, the transformer capacity combination, and the power supply range. The second category mainly
focuses on the optimal power supply radius. In Ref. [8], a substation radius optimization model was constructed
to find the minimum annual cost per unit of the supply area. Ref. [9] considers the capacity–load ratio constraint
applicable to large capacity transformers. It investigates the relationship between transformer capacity, transformer
number, and supply radius, and gives its optimal combination. Ref. [10] compares the indicators of comprehensive
investment, operating costs, reliability of power supply, and conditions for the construction of the grid, for electricity
demanded by regional development. In this way, the transformers’ number, capacity and power supply radius are
defined, and the number and length of lines are estimated.
Based on the references, existing substation planning models mainly focus on the relationship between three
variables: load density, supply radius, and substation capacity. They usually study two of three variables by fixing
the remaining one for simplicity. As for some potentially larger substation schemes, such as 4 ∗63 MVA and
3 ∗80 MVA in 110 kV system, few studies have been compared in a comprehensive model, considering their
similar total substation capacity but the unequal number of transformer units and discriminative individual capacity.
In addition, the existing models rarely consider the impact of renewable energy access and involve the reliability cost
analysis under different grid wiring means [11,12]. The adaptability of this traditional substation planning model
might weaken when the penetration of renewable energy sources increases.
Thus, this paper presents an optimization model of the capacity and number of substation transformers in the
distribution network with minimum construction and operation costs as the objective function. It is characterized by
the reliability cost of renewable energy access and the grid structure of the transformer’s secondary side. The impact
of renewable energy access on feeders reliability in terms of network structures is considered in the proposed model,
which makes the economic indexes of reliability more important and subtler in a whole problem. The reliability
1521



<!-- page 3/11 -->

J. Huang, Z. Sun, H. Xie et al.
Energy Reports 9 (2023) 1520–1530
index is calculated by the idea of partitioning for the sake of reliability estimation efficiency. Based on the features
of the model, an algorithm called the multivariate universe optimizer (MVO) is made to solve the problem. Some
examples are tested and the results of the case study verify the superiority of the method in substation planning,
which would be a promising tool for the selection of the number of transformers in large capacity substations.
The rest of this paper is organized as follows. The Section 2 analyzes the impact of renewable energy access on
power supply reliability. Section 3 presents the economic analysis model for substation construction and operation.
Section 4 introduces the MVO algorithm. Section 5 shows the case results of a regional distribution network in the
Guangdong power grid. Finally, the main conclusions of this study are summarized in Section 6.
2. Influence of renewable energy access on power supply reliability
2.1. Economic analysis of reliability of distribution network connection mode
Reliability is one of the important evaluation indexes of distribution network connection mode planning, which
mainly reflects the continuous power supply capability of the power system. The economic analysis of the reliability
of the distribution connection mode, or network structure, in this paper is to convert the reliability index into
economic cost on the premise of meeting the requirements of power supply reliability, and its core is the calculation
of the economic cost of reliability. The main evaluation index of distribution reliability is the system average power
supply reliability rate [13].
Rs =
[
1 −
m
∑
i=1
(Niµi)/
m
∑
i=1
(8760Ni)
]
× 100%
(1)
where m is the number of loads in the typical wiring of the distribution network; Ni is the number of customers at
load i, and µi is the average annual outage time at the load point i.
Different wiring methods will correspond to different reliability economic costs. Referring to the literature [14],
the reliability indexes and the reliability economic cost per unit load for typical wiring methods of urban medium
voltage distribution networks obtained under a unified distribution network planning scenario are shown in Table 1.
Table 1. Reliability index and reliable economic cost per unit load for each typical wiring method of urban medium voltage distribution
network.
Typical wiring methods
Reliability index Rs
Economic index/(million yuan/MW)
Construction cost
Operating cost
Outage loss cost
The economic
cost of reliability
Double-loop network
99.99865%
35.1750
11.5567
5.664
52.3957
Single-loop network
99.99804%
27.1455
9.6644
8.256
45.0659
2-contact and 3-section network
99.99136%
29.8220
10.4104
36.288
76.5204
As can be seen from Table 1, without considering renewable energy access, the research results for typical wiring
show that the reliability of double-loop network, single-loop network and 2-contact and 3-section network is close,
but the economic cost of reliability varies greatly. In terms of outage loss costs, the 2-contact and 3-section network
is more than six times higher than the double-loop network. Therefore, the planning of large-capacity substations
must take into account the impact of different wiring methods.
2.2. Economic analysis of reliability considering renewable energy access
Distributed generator is connected to the distribution network as planned, which makes a fact that there might
be more than one power source in a feeder. When a fault occurs in the system, after fault isolation and switch
switching, different areas on a feeder have different operation modes according to the power source location. These
areas can be roughly divided into four categories [15]: Class A partition: fault occurrence area, only when the fault
is repaired, this partition can resume power supply; Class B partition: fault affected area, the outage time of such
partition depends on the sum of fault isolation time and switch switching time; Class C partition: islanded area with
the distributed generator, the outage time of this partition depends on the fault isolation time; Class D partition:
fault-free area, this partition is located upstream of the fault point, close to the substation.
1522



<!-- page 4/11 -->

J. Huang, Z. Sun, H. Xie et al.
Energy Reports 9 (2023) 1520–1530
Taking the radial network as an example, as in Fig. 1, the system is divided into seven zones based on switching
elements, where zone Z4 is connected to the renewable energy DG. It is assumed that only the switch between Z1
and Z2 is a circuit breaker and has an automatic opening and closing function, while the others are non-automatic
load switches. When a fault occurs at point K in zone Z3, the seven zones can be further divided into 4 class sets,
which are A = {Z3, Z6, Z7}, B = {Z2}, C = {Z4, Z5}, and D = {Z1}. It can be seen that, due to the addition of
DG, two regions in C can restore power supply, making the average partition outage time lower.
It is known that the outage loss in class D partition is 0, while the outage loss in class A\B\C partitions will
be affected by the outage time and outage load. Therefore, typical faults in all areas are counted and the areas are
classified, and thus the average outage time in a year is calculated for class A\B\C partitions.
Fig. 1. Zoning map of the impact of renewable energy access.
(1) Class A partition: fault occurrence area
TA =
∑
i=NA
λi + γi +
∑
i=NA
λ′
iγ ′
i
(2)
L A = PA × TA
(3)
where λi and λ′
i are the failure rate and planned maintenance rate of the components, respectively; γi and γ ′
i are the
average outage duration and average planned outage duration of the components, respectively; NA is the number of
all components in the class A partition; L A is the average annual outage loss; and PA is the average annual outage
load.
(2) Class B partition: fault affected area
TB =
∑
i=NB
pi
∑
j=NB
λ jt1 +
∑
i=NB
(1 −pi)
∑
j=NB
λ jt2 +
∑
j=NB
λ′
jγ ′
j
(4)
L B = PB × TB
(5)
where t1 is the fault isolation and switching time; t2 is the fault repair time; pi is the probability that component i
in the class B partition can be supplied with distributed electricity; NB is the number of all components in the class
B partition. L B is the average annual outage loss; PB is the average annual outage load.
(3) Class C partition: island formation area
TC =
∑
i=NC
pi
∑
j=NC
λ jt3 +
∑
i=NC
(1 −pi)
∑
j=NC
λ jt2 +
∑
j=NC
λ′
jγ ′
j
(6)
LC = PC × TC
(7)
where t1 is the fault isolation time; NC is the number of all components in the class C partition. LC is the average
annual outage loss; and PC is the average annual outage load.
(4) Class D partition: without impact area
The average outage rate and average outage time within such areas are both zero.
After a fault occurs, through fault isolation and switchover, an island is formed in part of the partition, and
the probability of reliable power supply from distributed power sources can be obtained by determining the loads
within the island. The average outage load and average outage time for each type of partition with different fault
1523



<!-- page 5/11 -->

J. Huang, Z. Sun, H. Xie et al.
Energy Reports 9 (2023) 1520–1530
conditions are summed up. Thus, the reliability of power supply by renewable energy access in a region can be
calculated from Eqs. (2)–(7).
3. Optimization model
A substation optimization model is presented in this paper to consider the economy of large-capacity substation
construction and system operation, like the reliability of secondary distribution network, with renewable energy
involved. By quantifying the reliability cost and the influence of renewable energy on the substation scale directly
and indirectly, the optimization model to minimize the total cost of 10 years of construction and operation is
obtained. The decisive variables are the number of transformers, the capacity of each transformer, and the number
of incoming and outgoing lines of the primary and secondary sides of the transformer. The model not only considers
the characteristics of the substation itself and its subordinate distribution network, but also takes into account various
connection modes of the distribution feeders and analyzes the impact of renewable energy access on the network
power supply reliability. In general, the total construction and operation cost of substations include five parts: input
line investment cost (f1), outgoing line investment cost (f2), substation investment cost (f3), substation operation and
maintenance cost (f4), and reliability cost (f5).
Take the 110 kV substation with the low-voltage side of 10 kV as an example to build the following optimization
model. The optimization model is based on the following assumptions:
• The power supply area is circular and the substation is located at the ideal center.
• The annual growth rate of load density is the same every year.
• Transformers of equal capacity have the same number of outgoing lines.
3.1. Objective function
The objective function expression of the optimization model is as follows:
min F =
n
∑
t=1
f (t) × (1 + k)n−t
(8)
where f(t) is the total construction and operation costs of the substation in tth year; k is the discount rate of the
electric power industry; n is the economic operation life of the equipment.
It is assumed that the supply radius of the large capacity substation is R, and the capacity of transformer is Si
and N(t) is the number of transformers in the substation in tth year. Then the construction and operation cost of
the substation in the ith year can be obtained as follows:
f (i) = f1 + f2 + f3 + f4 + f5
(9)
• Investment cost of incoming lines
The investment cost of the incoming lines can be expressed as follows.
f1 = (C0 + αRC1) × [M1(t) −M1(t −1)] × N(t)
(10)
where C0 is the constant cost of each incoming line, C1 is the investment cost of a unit length of the incoming line,
M1(t) is the number of incoming lines in the year t. α is the incoming line zigzag coefficient, and its value is taken
as 2[9].
• Investment cost of outgoing lines
f2 = (C2 + RC3) × [M2(t) −M2(t −1)] × N(t)
(11)
where C2 is the constant cost of each outgoing line, C3 is the investment cost of a unit length of the out-line, M2(t)
is the number of outgoing lines in year t.
• Investment cost of the substation
The investment cost of a substation has consisted of the constant cost of substation construction and the
investment cost of the transformer. The expression is shown as follows.
f3 = ab0 +
N(t)
∑
i=1
(ab + bbSi)
(12)
1524



<!-- page 6/11 -->

J. Huang, Z. Sun, H. Xie et al.
Energy Reports 9 (2023) 1520–1530
where ab0 is the constant cost of substation construction, including the investment costs of the substation and other
equipment. ab is the constant cost of a single transformer, which mainly reflects the costs of land, incoming and
outgoing intervals. bb is the cost factor associated with the transformer capacity.
• Operation and maintenance costs of the substation
f4 = op + mp
(13)
where op is the operating cost of the substation, which includes the load loss and the reactive power compensation
devices required for renewable energy access, and is calculated as follows.
op =
N(t)
∑
i=1
ω∆Pd(i)( πl2σ(t)
Stotal cos ϕ )
(14)
where ω is the electricity price, ∆Pd(i) is the unloaded loss of the ith transformer, Stotal is the total capacity of the
substation, cosϕ is the power factor of the transformer.
mp denotes the maintenance cost of the substation, which is generally taken as a percentage of the investment
cost.
mp = b1 f1 + b2 f2 + b3 f3
(15)
where b1, b2 and b3 are the factors of cost (f1), cost (f2) and cost (f3), respectively.
• Reliability Cost
The number of outgoing lines will be affected by the number of substation capacity units. Further, the
combination of different numbers of outgoing lines and wiring methods will affect reliability costs, as shown in
Table 1.
f5 =
N(t)
∑
k=1
(L Ak + L Bk + LCk) × ω
(16)
where L Ak, L Bk, LCk are the average outage losses in year k of partitions A, B, and C, respectively.
3.2. Constraints
Section headings should be left justified, bold, with the first letter capitalized and numbered consecutively, starting
with the Introduction. Sub-section headings should be in capital and lower-case italic letters, numbered 1.1, 1.2,
etc, and left justified, with second and subsequent lines indented. All headings should have a minimum of three
text lines after them before a page or column break. Ensure the text area is not blank except for the last page.
• The constraint with the numbers of incoming and outgoing lines
Since the number of incoming and outgoing lines in the substation needs to comply with the relevant local
distribution network planning guidelines, the number of lines for each wiring means on the 10 kV side needs to
satisfy the following constraints.
M1 min ≤M1(t) ≤M1 max
(17)
M2 min ≤M2(t) ≤M2 max
(18)
N1(t) + N2(t) + N3(t) = M2(t)N(t)
(19)
where N1(t), N2(t), N3(t) are the numbers of wiring in multi-segment multi-contact network, single ring network,
and double ring network, respectively.
It is worth noting that, based on the reliability targets for each type of power supply area and the reliability
indicators for typical wiring patterns, the wiring methods and their corresponding numbers applicable to each
type of power supply area can be roughly screened. The distribution network planned will necessarily meet the
reliability requirements (lower limit) [16], but the specific combination of different network structures depends on
the management target.
• “N −1” constraints on transformers and lines
1525



<!-- page 7/11 -->

J. Huang, Z. Sun, H. Xie et al.
Energy Reports 9 (2023) 1520–1530
“N −1” constraint of transformers means when a transformer is withdrawn from operation due to a fault, the
remaining transformers bear the entire load without overloading. The constraint inequality of capacity and number
of transformers is as follows.
π R2σ(t)
[N(t) −1]Si cos ϕ ≤k1
(20)
where k1 is the short-time overload rate of the transformer.
“N −1” constraint of lines means when a line is withdrawn from operation due to a fault or maintenance, the
remaining lines can carry the full load without overloading. The constraint inequalities are as follows.
π R2σ(t)
[M1(t) −1]∆S1 cos ϕ1
≤k2
(21)
π R2σ(t)
[M2(t) −1]∆S2 cos ϕ2
≤k3
(22)
where ∆S1 and ∆S2 are the maximum capacity of the incoming and outgoing lines, respectively. k2 and k3 are the
short-time allowable overload rates of incoming and outgoing lines, respectively. cos ϕ1 and cos ϕ2 are the power
factors of incoming and outgoing lines, respectively.
The constraint of delivery capacity is as follows.
(N1 × β1% + N2 × β2% + N3 × β3%) × Sline ≥Stotal
(23)
where β1, β2 and β3 are the maximum load factor of lines 1, 2 and 3, respectively. Sline is the maximum transmission
capacity of the line.
• Constraint on transformer capacity–load ratio
The capacity–load ratio E is the ratio of the transformer’s capacity to its maximum load, and the following
constraints should be satisfied in the transformer capacity planning.
Emin ≤
N(t)
∑
i=1
Si cos ϕ
π R2σ(t)
≤Emax
(24)
where Emin and Emax are the minimum and maximum values of the capacity–load ratio, respectively.
4. Algorithm
Substation planning is affected by dynamic changes in load density and renewable energy output, and there are
more options for capacity and number of station transformers. Meanwhile, the model constructed in the previous
section is characterized by many variables and complex constraints. The MVO algorithm is a meta-heuristic
optimization algorithm proposed in 2016 with stronger optimality finding capability [17–19]. Therefore, combining
the model characteristics and algorithm advantages, this paper adopts the MVO algorithm to solve the model.
The feasible solutions in the MVO algorithm correspond to universes, and the fitness of the solutions corresponds
to the expansion rate of that universe. In each iteration, the universes are sorted according to the expansion rate,
and a universe is randomly selected as a white hole through roulette, and the universes exchange matter through
black and white holes. Assume that the initial value of the multi-universe population is :
Z =
⎡
⎢⎢⎢⎢⎣
z1
1
z2
1
· · ·
zd
1
z1
2
z2
2
· · ·
zd
2
...
...
...
z1
s
z2
s
· · ·
zd
s
⎤
⎥⎥⎥⎥⎦
(25)
where d is the number of parameters; s is the number of universes.
According to the roulette mechanism update, a white hole or black hole transfers cosmic objects body as shown
in Eq. (26).
z j
i =
{
z j
k,r1 < NC (Zi)
z j
i ,r1 ⩾NC (Zi)
(26)
1526



<!-- page 8/11 -->

J. Huang, Z. Sun, H. Xie et al.
Energy Reports 9 (2023) 1520–1530
where Zi is the ith universe; NC (Zi) is the normalized expansion rate of the ith universe, which differs for each
individual universe; r1 is the random value of [0,1]; z j
k is the jth dimensional component of the kth universe selected
by the roulette wheel.
Matter is randomly transferred between universes through wormholes to ensure population diversity, while all
exchange matter with the optimal universe to increase the expansion rate.
z j
i =
⎧
⎪⎨
⎪⎩
{
z j + KTDR
[(
uc j −wc j
)
× r4 + wc j
]
,r3 < 0.5
z j −KTDR
[(
uc j −wc j
)
× r4 + wc j
]
,r3 ⩾0.5
z j
i ,r2 ⩾KWEP
(27)
where KWEP, KTDR are the wormhole existence rate and travel distance, respectively. r2, r3, r4 are random values
in [0,1]. uc j and wc j are the upper and lower bounds of the dynamic boundary, respectively.
The wormhole existence rate KWEP and the travel distance rate KTDR are two extremely important parameters
in the MVO algorithm that need to be increased linearly over iterations in order to emphasize the search during
the optimization process. The variation of KWEP, KTDR in the iteration is able to get a more accurate global/local
search in the best universe.
KWEP = KWEPmin + t ×
( KWEPmax −KWEPmin
T
)
(28)
KTDR = 1 −t1/p
T 1/p
(29)
where KWEPmax and KWEPmin are the upper and lower bounds of parameter KWEP, which are taken as 1 and 0.2,
respectively; t is the current number of iterations; T is the maximum number of iterations; p is the development
accuracy of the algorithm, p = 6.
5. Simulation
The simulation in this Section is based on a computer with a CPU of Intel Core12700 and 16 GB of memory,
and the model is programmed in Python and solved by MVO algorithm.
5.1. The setting of simulation parameters
Assuming that the regional load density is 10 MW/km2 and the regional power supply radius is 1.5 km. The
annual growth rate of the load is assumed to be given. In order to simplify the dynamic changes of renewable
energy growth and load growth, the renewable energy growth is equivalent to reducing the load density, reducing
the annual load growth rate to 5%. The Operator and Maintainer coefficients b1, b2, and b3 are the same, 0.032.
The 10 kV side outgoing line adopts three types of wiring: multi-contact and multi-section network, single-loop
network and double-loop network, and the wires model used are JKLYJ-240, YJV22-3 × 400 and YJV22-3 × 300
respectively, with the maximum allowable load capacity corresponding to 550 A, 550 A and 600 A. The number of
feeder switches has been optimized according to the conclusions of the literature [20] to ensure a better reliability.
The current 110 kV substation transformer capacity is mostly 3 ∗50 MVA, or 3 ∗63 MVA, and this optimization
focuses on the preferred high-capacity substation, of which the single transformer capacity is 63 MVA or 80 MVA
and the number of transformers is 3 or 4. The remaining parameters of the simulation are shown in Table 2.
Table 2. The simulation parameters of transformer with capacity of 63 MVA and 80 MVA.
Parameters
63 MVA
80 MVA
Electricity price ω (yuan)
0.6
0.6
Transformer price (million yuan)
14.3
16
the constant cost of each incoming line C0 (million yuan)
0.8
1
investment cost of a unit length of the incoming line C1 (million yuan/km)
3
3.5
the constant cost of each outgoing line C2 (million yuan)
0.8
0.8
investment cost of a unit length of out-line C3 (million yuan/km)
0.95
0.95
1527



<!-- page 9/11 -->

J. Huang, Z. Sun, H. Xie et al.
Energy Reports 9 (2023) 1520–1530
5.2. Analysis of simulation results
This example compares the planning of high-capacity substations by considering renewable energy access or not.
The simulation results are shown in Tables 3 and 4 below.
Table 3. The optimization results for large capacity substation (63 MVA).
Unit capacity
63 MVA (Renewable energy)
63 MVA (Without renewable energy)
Original unit no.
3
3
final scale
4
4
Year of commissioning of
new transformer
4th
3rd
Year order
multi-segment
multi-contact
network
single ring
network
double ring
network
multi-segment
multi-contact
network
single ring
network
double ring
network
1
5
3
3
4
4
7
2
5
5
5
4
4
7
3
5
5
5
4
5
7
4
7
7
6
7
6
7
5
7
7
6
7
6
7
6
7
7
6
7
6
7
7
7
7
6
7
6
7
8
7
7
6
7
6
7
9
7
7
7
7
7
7
10
7
7
7
7
7
7
Reliability cost
21.43 million ¥
27.46 million ¥
Total costs
1444.6489 million ¥
1452.3974 million ¥
Table 4. The optimization results for large capacity substation (80 MVA)
Unit capacity
80 MVA (Renewable energy)
80 MVA (Without renewable energy)
Original unit no.
2
2
final scale
3
3
Year of commissioning of
new transformer
3rd
3rd
Year order
multi-segment
multi-contact
network
single ring
network
double ring
network
multi-segment
multi-contact
network
single ring
network
double ring
network
1
4
4
3
5
5
4
2
4
7
6
5
7
5
3
4
7
7
7
7
6
4
4
7
7
7
7
6
5
4
7
7
7
7
6
6
5
7
7
7
7
7
7
7
7
7
7
7
7
8
7
7
7
7
7
7
9
7
7
7
7
7
7
10
7
7
7
7
7
7
Reliability cost
22.80 million ¥
25.64 million ¥
Total costs
1412.4109 million ¥
1414.9560 million ¥
It can be seen from Table 3 that the number of transformers put into the substation in the first year is 3 when the
transformer capacity is 63 MVA. When considering renewable energy access, the fourth transformer was put into the
substation in the fourth year. The initial number of outgoing lines is as follows: 5 for multi-segment multi-contact
network, 3 for single ring network, and 3 for double ring network, as a total of 11. The final number of lines for all
1528



<!-- page 10/11 -->

J. Huang, Z. Sun, H. Xie et al.
Energy Reports 9 (2023) 1520–1530
three wiring types is 7. The total cost of this scheme is 1444.6489 million ¥. When renewable energy access is not
considered, the fourth transformer was put into the substation in the third year. The initial number of outgoing lines
is as follows: 4 for multi-segment multi-contact network, 4 for single ring network, and 7 for double ring network,
as a total of 15. The final number of lines for all three wiring types is 7. The total cost of this scheme is 1452.3974
million ¥.
When the capacity of the transformer is selected as 80 MVA, 2 transformers were put into use for the substation
in the first year. When considering renewable energy access, the third transformer was introduced into the substation
in the third year. The similar large capacity substation, as compared to the previous scheme 4∗63 MVA, eventually
forms a 3∗80 MVA structure. The initial number of outgoing lines is as follows: 4 for multi-segment multi-contact
network, 4 for single ring network, and 3 for double rings network. The final number of lines for all three wiring
structures is 7. The total cost of this scheme is 1412.4109 million ¥. When renewable energy access is not considered,
the third transformer was put into the substation in the third year. The initial number of outgoing lines is as follows:
5 for multi-segment multi-contact network, 5 for single ring network, and 4 for double ring network, as a total of
14. The final number of lines for all three wiring types is 7. The total cost of this scheme is 1414.9560 million ¥.
The addition of renewable energy sources allows the reliability of the area covered by the large capacity substation
to be increased, which can reduce reliability costs. At the same time, the renewable energy source can offset some
of the load growth and delay the commissioning of the new main transformer resulting in lower total investment
costs. It can be seen that when a 63 MVA transformer is selected as the main transformer for a large capacity
substation, considering the access of renewable energy can reduce the substation investment by approximately ¥7.7
million, and when an 80 MVA transformer is selected as the main transformer for a large capacity substation, it
can reduce the substation investment by approximately ¥2.5 million.
By comparison of the examples, the total cost of the 3∗80 MVA scheme is lower, so the distribution companies
in the area prefer to build 3 ∗80 MVA large capacity substations based on this method.
6. Conclusion
Considering the variation of renewable energy penetration rate and load, this paper proposes a method to optimize
the capacity of substations in distribution networks. The economic analysis model for optimizing the capacity and
the number of a substation transformer in the distribution network considers the renewable energy access and the
reliability of the secondary network of the substation. Various classical wiring structures of the distribution network
are retained and the impact of renewable energy access on the reliability of the distribution supply is analyzed and
quantified. Moreover, reliability indicators are transformed into economic indicators in the form of energy outage
losses. The optimization model is solved by the MVO algorithm with satisfactory results in test examples, which
are employed to demonstrate and verify the validity and rationality of the method.
Declaration of competing interest
The authors declare that they have no known competing financial interests or personal relationships that could
have appeared to influence the work reported in this paper.
Data availability
No data was used for the research described in the article
Acknowledgments
This paper is supported in part by the 2022 Power Planning Theme Research Project of Guangdong Power Grid
Company, China (0300002022030301GH00029).
References
[1] Cai X, Zhou Q. Influence of distribution system connection modes on power supply reliability. Proc CSU-EPSA 2010;22(04):85–8+106.
[2] Wang W. Reliability study of distribution network wiring methods. Sci Technol Innov 2016;15:171.
[3] Tajdinian M, Shirali R, Behdani B, Abbasi M, Chamorro HR. Allocating different types of distributed generations concentrating on
transient stability enhancement in distribution network. In: 2022 IEEE international conference on environment and electrical engineering
and 2022 IEEE industrial and commercial power systems Europe. EEEIC/I & CPS Europe, 2022.
1529



<!-- page 11/11 -->

J. Huang, Z. Sun, H. Xie et al.
Energy Reports 9 (2023) 1520–1530
[4] He Y, Li F, Wang X, Shen S, Zhu K. Research on instability of distributed renewable energy power access to distribution network.
In: 2019 IEEE 3rd information technology, networking, electronic and automation control conference. ITNEC, 2019, p. 38–41.
[5] Zheng Y. Research on reliability of power distribution network with distributed photovoltaic. Shanxi Electr Power 2020;02:18–21.
[6] Li X, Wu J, Sun W. Substation locating and sizing base on improved firefly algorithm. J Xiangtan Univ Nat Sci Ed 2020;42(06):67–78.
[7] Gao
F,
Zhang
P,
Sai
X.
Substations
locating
and
sizing
in
uncertainty
load
environment.
Power
Syst
Prot
Control
2010;38(15):75–80+109.
[8] Cheng J, Li F, Mo H. Economic power supply radius of a substation in a distribution network. Power Syst Prot Control
2022;50(15):129–37.
[9] Wang Q, Qin K, Chen D. Power supply radius optimization for substations with large capacity transformers. Power Syst Clean Energy
2014;30(04):18–23.
[10] Liu Y, Li X. Discussion on economical capacity and economical power supply radius for transformer substations. Guangdong Electr
Power 2005;11:7–9.
[11] Luo Z, Liu Y, Wang C. Review on coordination and planning of active distribution network. In: 2020 5th International conference on
power and renewable energy. ICPRE.
[12] Liu J, Zhang J, Da Z. Effect of distributed generation on power supply reliability of distribution network. In: International conference
on grid & distributed computing. IEEE; 2015.
[13] Wang B. Research on reliability assessment and optimization of connection modes of distribution networks. South China University
of Technology; 2010.
[14] Xu K, Dai X, Qin Y. Reliability economic analysis of typical connection modes of urban middle-voltage distribution network. Water
Resour Power 2015;33(03):196–201.
[15] Ren J, Li Y. Reliability evaluation of the distributed network containing distributed generation based on feeder partition. J North China
Electr Power Univ Nat Sci Ed 2015;42(06):29–34.
[16] Liu J, Yu G, Li W. Reliability-based quick selection of medium voltage distribution line connection modes. Power Syst Clean Energy
2017;33(12):12–7+22.
[17] Mirjalili S, Mirjalili SM, Hatamlou A. Multi-verse optimizer: A nature-inspired algorithm for global optimization. Neural Comput Appl
2015;27(2):495–513.
[18] Kumar P, Garg S, Singh A, Batra S, Kumar N, You I. MVO-based 2-D path planning scheme for providing quality of service in UAV
environment. IEEE Internet Things J 2018;5(3):1698–707.
[19] Shaheen AM, El-Sehiemy RA. Application of multi-verse optimizer for transmission network expansion planning in power systems.
In: 2019 international conference on innovative trends in computer engineering. ITCE, 2019, p. 371–6.
[20] Cao H, Chen Y, Wu Y. General quantitative expression of optimal segment number of MV feeder. Power Syst Technol
2019;43(08):2991–7.
1530
