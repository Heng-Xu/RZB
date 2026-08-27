<!--
source: D5_规划与灵活资源/EN_extra_stochastic_pre_event.pdf
sha256: bd65bab1750a5541702a61209e3ff567407b5ca8ffe702b78f64c7ebbac9272a
method: pymupdf
pages: 37
-->

<!-- page 1/37 -->

Stochastic Pre-Event Preparation for Enhancing
Resilience of Distribution Systems with High DER
Penetration
Qianzhi Zhanga,∗, Zhaoyu Wanga, Shanshan Mab, Anmar Arifc
aDepartment of Electrical and Computer Engineering, Iowa State University, Ames, IA
50011, USA
bSchool of Electrical, Computer and Energy Engineering, Arizona State University,
Tempe, AZ 85287, USA
cDepartment of Electrical Engineering, King Saud University, Riyadh 11451, Saudi
Arabia
Abstract
This paper proposes a stochastic optimal preparation and resource allocation
method for upcoming extreme weather events in distribution systems, which
can assist utilities to achieve faster and more eﬃcient post-event restora-
tion. With the objective of maximizing served load and minimizing oper-
ation cost, this paper develops a two-stage stochastic mixed-integer linear
programming (SMILP) model. The ﬁrst-stage determines the optimal posi-
tions and numbers of mobile resources, fuel resources, and labor resources.
The second-stage considers network operational constraints and repair crew
scheduling constraints. The proposed stochastic pre-event preparation model
is solved by a scenario decomposition method, Progressive Hedging (PH), to
ease the computational complexity introduced by a large number of scenar-
ios. Furthermore, to show the impact of solar photovoltaic (PV) generation
∗Corresponding author
Email address: qianzhi@iastate.edu (Qianzhi Zhang)
Preprint submitted to Renewable and Sustainable Energy Reviews
December 25, 2020
arXiv:2012.13043v1  [eess.SY]  24 Dec 2020



<!-- page 2/37 -->

on system resilience, we consider three types of PV systems during power
outage and compare the resilience improvements with diﬀerent PV penetra-
tion levels. Numerical results from simulations on a large-scale (more than
10,000 nodes) distribution feeder have been used to validate the scalability
and eﬀectiveness of the proposed method.
Keywords:
Pre-event preparation, progressive hedging, PV systems,
resource allocation, two-stage stochastic model
1. Introduction
Extreme weather events have brought signiﬁcant damage to power grid
infrastructure and caused 50%-60% of power outages in the U.S. [1]. Among
those outages, around 90% of them were due to failures in distribution sys-
tems [2]. After severe weather events, the major challenge for utilities is
the shortage of various resources to repair damage and restore power sup-
ply. Pre-event resource allocation is one of the most eﬀective ways to mitigate
extreme events’ impacts on power distribution system. It can allocate appro-
priate amounts of ﬂexible resources to optimal positions before the extreme
events. These ﬂexible resources include emergency power supply resources,
equipment resources and labor resources. Therefore, pre-event preparation
enables faster and more eﬃcient post-event restoration of the power gird.
There are exist studies that have investigated resource allocation prob-
lems for the resilience enhancement of electric distribution systems.
In
[3, 4, 5], proactive resource management in microgrids and proactive op-
eration strategies in distribution systems are considered to enhance system
resilience during extreme events. In [6], the number and location of depots are
2



<!-- page 3/37 -->

determined at the pre-disturbance stage to manage the available resources.
In [7], repair crews are pre-allocated to depots and integrated with restora-
tion process to enhance the resilience of electric distribution systems.
In
[8], a two-stage stochastic model is developed to select staging locations and
allocate repair crews for disaster preparation, while considering distribution
system operation and crew routing constraints. In [9], the authors developed
a stochastic model for optimizing proactive operation actions. The study
optimized the topology of the network and position of crews for upcoming
disturbances. In [10] and [11], a two-stage framework is developed to position
mobile emergency generators (MEGs) for pre- and post-disasters. Mobile en-
ergy storage devices (MESs) are investigated in [12] and [13] for resilience
enhancement of power distribution systems. However, there remain limita-
tions in the above studies on pre-event preparation and resource allocation.
These limitations are described in the following:
(1) Pre-allocation of various ﬂexible resources:
In practice, pre-event
preparation includes allocation of various ﬂexible resources, such as MEGs,
MESs, fuel resources for diesel generators, and repair crews. The optimal al-
location of those ﬂexible resources can help utilities to achieve faster and more
eﬃcient post-event power restoration. However, previous studies mainly fo-
cused on allocating speciﬁc ﬂexible resources, rather than formulating a com-
plete optimization problem to pre-allocate various ﬂexible resources together.
(2) Impacts of solar PV power on system resilience: Due to intermit-
tent characteristic of traditional distributed energy resources (DERs), such
as solar power, PV systems are not considered as a reliable resilient solu-
tion. However, the distributed nature of PV power can contribute to a more
3



<!-- page 4/37 -->

resilient power system. In practice, PV systems can be coupled with en-
ergy storage technology, to enable continues operation during outages [14].
However, diﬀerent types of PV systems are ignored in most existing research.
(3) Scalability of the solution algorithm: On one side, the stochastic pre-
event preparation model may suﬀer from computational ineﬃciency due to
a large number of scenarios; on the other side, a limited number of scenarios
may inﬂuence the stability and quality of the solutions. Therefore, the trade-
oﬀbetween computation time and solution accuracy needs to be studied for
stochastic pre-event preparation methods. In addition, a large-scale system
is needed to verify the scalability of solution algorithms.
To address these challenges, we propose a two-stage stochastic mixed
integer linear program (SMILP) for pre-event preparation with pre-allocation
of mobile resources, fuel resources and labour resources. Furthermore, the
proposed pre-event preparation model considers diﬀerent types of PV systems
and facilitates the beneﬁts of leveraging high PV penetration for improving
the resilience of distribution grids.
In this paper, resilience improvement
is quantiﬁed by the increased served load and reduced outage duration. To
deal with the massive computation burden, the proposed two-stage stochastic
pre-event preparation problem is solved by a scenario decomposition method,
Progressive Hedging (PH) [15], while maintaining the accuracy and stability
of the solution [16]. Also, the quality of the solution is validated by a multiple
replication procedure (MRP). The main contribution of this paper is three-
folded:
• We propose a two-stage SMILP model for pre-event preparation, where
the ﬁrst-stage allocates MEGs, MESs, fuel, and repair crews, while the
4



<!-- page 5/37 -->

second-stage considers distribution system operation and repair crew
scheduling constraints.
• The proposed model considers three types of PV systems.
We also
demonstrate the improvement of resilience and the reduction of outage
duration with diﬀerent PV penetration levels.
• The proposed solution algorithm is tested through a solution validation
method to show its quality. In addition, a large-scale system, consist-
ing of more than 10,000 nodes, is used to verify the scalability of the
proposed pre-event preparation model.
The remainder of the paper is organized as follows: Section 2 describes
the proposed two-stage SMILP for pre-event preparation and resource alloca-
tion. Section 3 presents the PH solution algorithm, convergence analysis and
solution validation. Simulation results and conclusions are given in Section
4 and Section 5, respectively.
2. Two-stage Stochastic Pre-event Preparation Model
The general framework of the proposed two-stage stochastic pre-event
preparation model is shown in Figure 1.
Damage scenarios for extreme
weather events are generated based on: (1) identiﬁcation of extreme weather
events, such as ﬂood, hurricane and winter storm; (2) extreme weather event
data and metric; (3) fragility model of test systems, which describes the be-
havior of components under extreme weather events; (4) damage status of
components in test system subject to speciﬁc extreme weather events. To
approximate the impact of extreme weather events to grid infrastructures,
5



<!-- page 6/37 -->

Fragility analysis
Extreme event forecast Weather forecast
Historical data
Uncertainty and scenario generation
Two-stage stochastic pre-event model
First-stage
Allocation of flexible resources
(mobile resources, fuel resources 
and repair crews)
Network operational constraints
(PV connectivity, repair crew 
dispatch, power flow...)
Second-stage
Figure 1: The proposed two-stage stochastic pre-event model.
damage scenarios can be generated by mapping the weather data set to failure
probability of grid infrastructures. Adopted from [17], the failure probability
of an overhead line being damaged by hurricane can be expressed as follows:
pl,ij(w(t)) = 1 −
m
Y
k=1

1 −plk(w(t))

n
Y
k=1

1 −pfc,k(w(t))

(1)
where pl,ij(w(t)) is the failure probability of the overhead line ij with wind
speed w(t). plk(w(t)) is deﬁned as the conditional failure probability of pole k
at line ij as a log-normal cumulative distribution function (CDF) of the wind
speed w(t), which is expressed in equation (2). m and n are the number of
distribution poles supporting line ij and the number of conductor wires be-
tween two adjacent poles at line ij, respectively. In equation (3), pfc,k(w(t))
6



<!-- page 7/37 -->

represents the failure probability of conductor k between two poles.
plk(w(t)) = Φ
h
ln
w(t)/mR
ξR
i
(2)
pfc,k(w(t)) = (1 −pu) max

pfw,k(w(t)), αpftr,k(w(t))

(3)
where mR and ξR are the median capacity and the logarithmic standard devi-
ation of intensity measurement, respectively. pfw,k(w(t)) represents the direct
wind-induced failure probability of conductor k and pftr,k(w(t)) represents
the fallen tree-induced failure probability of conductor k. pu is the probabil-
ity that conductor k is underground, which is more invulnerable to extreme
weather events. α represents the average tree-induced damage probability
of overhead conductors. More details of weather forecasting methodologies,
line fragility models and scenario generation can be found in [18].
As shown in Figure 1, the proposed SMILP pre-event preparation model
has two stages: (i) Flexible resources are allocated in the ﬁrst-stage, in-
cluding the optimal number and position of MEGs and MESs, allocation
of available fuel to generators, and pre-position of repair crews to depots.
(ii) The second-stage optimizes the operation of the distribution system and
assign crews to the damaged components. Constraints in the second-stage
includes unbalanced optimal power ﬂow constraints, network reconﬁguration
and isolation constraints, and repair crew scheduling constraints.
2.1. Model Objective Function
The objective function (4) is set to minimize operation costs and maximize
load served. There are three cost related terms in the objective, cost of fuel
7



<!-- page 8/37 -->

CF, cost of switching operation CSW, and cost of load shedding CD
i . The
objective is formulated as follows:
min
X
∀s
Pr(s)

CFrF X
∀t
X
∀φ
X
∀i
P G
i,φ,t,s + CSW X
∀t
X
∀k∈ΩSW
γk,t,s
+
X
∀t
X
∀φ
X
∀i
CD
i (1 −yi,t,s)dp
i,φ,t

(4)
where Pr(s) is the probability of occurrence for scenario s, rF is the rate of
fuel consumption of a generator, and P G
i,φ,t,s is the active power output for
fuel-based generator at bus i, phase φ, time t, and scenario s. Binary variable
γk,t,s represents the status of each switch, if switch k is operated at time t
on scenario s, then γk,t,s = 1. The binary variable yi,t,s represents the status
of load at bus i, time t, and scenario s. If the demand (dp
i,φ,t) is served, then
yi,t,s = 1.
2.2. First-Stage Constraints
The ﬁrst-stage constraints revolve around pre-allocating four critical re-
sources that will be utilized after an extreme event: (i) MEGs, (ii) MESs,
(iii) fuel and (iv) repair crews.
2.2.1. Mobile Resources Allocation Constraints
Mobile resources can be used to restore energy for isolated areas that are
not damaged, and to restore critical customers. In addition, fuel management
is critical after an extreme event to operate emergency generators. Distribut-
ing fuel after an extreme event maybe diﬃcult due to road conditions. As for
repair crews, pre-assigning them to diﬀerent locations provides a faster and
8



<!-- page 9/37 -->

more organized response. The constraints for allocating the mobile resources
are modeled as follows:
X
∀i∈ΩCN
nMEG
i
= N MEG
(5)
X
∀i∈ΩCN
nMES
i
= N MES
(6)
nMEG
i
+ nMES
i
≤N MU
i
, ∀i ∈ΩCN
(7)
where binary variables nMEG
i
and nMES
i
equal 1 if an MEG and MES are
allocated to bus i, respectively. The set ΩCN represents the set of candidate
buses for MEGs and MESs. Constraints (5) and (6) indicates that the number
of installed MEGs and MESs are equal to the number of available devices
(N MEG and N MES). We assume that each bus can only have a limited number
of mobile units N MU
i
, which is enforced by (7).
2.2.2. Fuel Resources Allocation Constraints
Deﬁne the set ΩG = ΩEG ∪ΩCN, where ΩEG is the set of buses that have
fuel-based emergency generators. The fuel allocated to ΩG must be limited
to the available amount of fuel. We model the fuel allocation constraints as
follows:
X
∀i∈ΩG
nFuel
i
≤N Fuel
(8)
F G
i ≤nFuel
i
≤F max
i
, ∀i ∈ΩG
(9)
9



<!-- page 10/37 -->

Constraint (8) limits the total amount of allocated fuel to the amount
of fuel available (N Fuel), where nFuel
i
is the amount of fuel allocated to the
generator at bus i. Constraint (9) limits the amount of fuel on each site,
where F G
i
is the amount of fuel already present for the generator at bus i,
and F max
i
represents the maximum capacity of fuel at bus i.
2.2.3. Repair Crew Allocation Constraints
In order to allocate the repair crews, we divide the network into diﬀerent
regions ΩR.
Each region will be assigned with diﬀerent crews, who will
conduct the repairs in that region. The repair crews are pre-positioned to
the regions using constraints (10) and (11), as follows:
X
∀r∈ΩR
nCrew
r
= N Crew
(10)
N Crew,min
r
≤nCrew
r
≤N Crew,max
r
, ∀r ∈ΩR
(11)
where nCrew
r
is the number of repair crews in region r and N Crew is the total
number of crews. The number of repair crews is limited in each region, using
N Crew,min
r
and N Crew,max
r
, depending on the size and capacity of the staging
locations.
2.3. Second-Stage Constraints
In the second-stage of the proposed pre-event preparation model, the
constraints of PV systems and repair crew dispatch are mainly discussed. The
model also considers unbalanced power ﬂow constraints, voltage constraints
and reconﬁguration constraints [19, 20].
10



<!-- page 11/37 -->

2.3.1. PV System Constraints
To fully investigate the impact of PV systems on system resilience, three
types of PV systems [20] are considered in the second-stage, ΩPV = ΩG
PV ∪
ΩH
PV ∪ΩC
PV: (i) Type 1: on-grid (grid-following) PV (ΩG
PV), where during an
outage, the PV is switched oﬀ. (ii) Type 2: hybrid on-grid/oﬀ-grid PV +
energy storage system (ESS) (ΩH
PV), where the PV system operates on-grid in
normal conditions, and oﬀ-grid during an outage. (iii) Type 3: grid-forming
PV + ESS with grid-forming capability (ΩC
PV), this system can restore part
of the network that is not damaged if the fault is isolated. The output power
of the PV systems is determined using the following equations:
0 ≤P PV
i,φ,t,s ≤
Iri,t,s
1000W/m2P rate
i
, ∀i ∈ΩPV/ΩG
PV, φ, t, s
(12)
0 ≤P PV
i,φ,t,s ≤χi,t,s
Iri,t,s
1000W/m2P rate
i
, ∀i ∈ΩG
PV, φ, t, s
(13)
(P PV
i,φ,t,s)2 + (QPV
i,φ,t,s)2 ≤(SPV
i
)2, ∀i ∈ΩPV/ΩG
PV, φ, t, s
(14)
(P PV
i,φ,t,s)2 + (QPV
i,φ,t,s)2 ≤χi,t,s(SPV
i
)2, ∀i ∈ΩG
PV, φ, t, s
(15)
The active power output P PV
i,φ,t,s of a PV depends on the rating of the solar
cell P rate
i
and the solar irradiance Iri,t,s [21]. The generated output power from
the PV can be determined in constraints (12) and (13), respectively. The
binary variable χi,t,s equals 1 if bus i is energized at time t and scenario s.
Using advanced PV smart inverters [22], the PVs can provide reactive power
11



<!-- page 12/37 -->

support QPV
i,φ,t,s, which is constrained by the capacity SPV
i
in (14) and (15).
During an outage, on-grid PVs are disconnected and the on-site load is not
served by the PVs, therefore, constraints (13) and (15) are multiplied by
χi,t,s. PV systems of types ΩC
PV and ΩH
PV can disconnect from the grid and
serve the on-site load.
An example network with damaged line is given in Figure 2, where the
network is divided into three islands due to the damaged line. In this work,
we assume that the network can be restored using the grid-forming sources
in ΩC
PV ∪ΩG. While PV system in types ΩG
PV or ΩH
PV can connect to the grid
only after the PV bus is energized. Island A has a grid-forming generator,
therefore, a microgrid is created and the PV system can participate. Island
B must be isolated because of the damaged line. Island C does not have any
grid-forming generators; hence, it will not be active and the grid-tied PV will
be disconnected.
G
Grid-forming generator
Damaged line
Open switch
Load
Island A
Island B
Island C
Figure 2: A single line diagram of an example network with one damaged line.
To determine the connection status of the PV systems, we design a virtual
network in parallel to the distribution network. The example network shown
in Figure 2 is transformed to a virtual network shown in Figure 3. A virtual
network with virtual sources, loads, and ﬂow is built to identify if an island
12



<!-- page 13/37 -->

VS
Virtual source/generator
Virtual load
Energized
Figure 3: A virtual network created for the example network in Figure 2.
can be energized by grid-forming generators. Each grid-forming generator
is replaced by a virtual source with inﬁnite capacity. Other power sources
without grid-forming capability (e.g., grid-tied PVs) are removed. The actual
loads are replaced by virtual loads with magnitude of 1. The virtual network
scheme is modeled using constraints (16)-(20).
X
∀j∈ΩC
PV∪ΩG
vS
j,t,s +
X
∀k∈ΩK(.,i)
vf
k,t,s = χi,t,s +
X
∀k∈ΩK(i,.)
vf
k,t,s, ∀i, t, s
(16)
−(uk,t,s)M ≤vf
k,t,s ≤(uk,t,s)M, ∀k ∈ΩK, t, s
(17)
0 ≤vS
k,t,s ≤(nMEG
i
+ nMES
i
)M, ∀i ∈ΩCN, t, s
(18)
χi,t,s ≥yi,t,s, ∀i ∈ΩN/{ΩC
PV ∪ΩH
PV ∪ΩG}, t, s
(19)
χi,t,s + nMEG
i
+ nMES
i
≥yi,t,s, ∀i ∈ΩCN, t, s
(20)
13



<!-- page 14/37 -->

A power-balance equation is added for each virtual bus, which means that
if the virtual load at a bus is served, then that bus is energized. Therefore,
for islands without grid-forming generators, all buses will be de-energized as
the virtual loads in the island cannot be served. Constraint (16) is the node
balance constraint for the virtual network. Virtual source vS is connected to
buses with power sources that have the capability to restore the system. The
variable vf
k represents the virtual ﬂow on line k and each bus is given a load of
1 that is multiplied by χi. Therefore, χi = 1 (bus i is energized) if the virtual
load can be served by a virtual source and 0 (bus i is de-energized) otherwise.
The virtual ﬂow is limited by (17). The limits are multiplied by the status
of the line (uk,t,s) so that the virtual ﬂow is 0 if a line is disconnected. The
virtual source can be used only if a generator is installed, as enforced by (18).
Deﬁne ΩN as the set of all buses. If bus i is de-energized, then the load must
be shed (19), unless bus i has a local power source with disconnect switch.
Constraint (20) is similar to (19) but with the presence of mobile sources.
2.3.2. Repair Crews Constraints
In the second-stage, repair crews are assigned to damaged components
that are in the area at which they are positioned. Note that the travel time
is neglected in this study, as the travel distances between components in the
same area is assumed to be small. An example for crew assignment is given
in Figure 4, where two working areas are assigned for the crews. In this
example, four damaged lines in Area 1 will be repaired by crews 1-3, while
crews 4 and 5 are responsible for the two damaged lines in Area 2. The repair
14



<!-- page 15/37 -->

crews constraints are formulated as follows:
X
∀k∈ΩDL(s)
zk,t,s ≤nCrew
r
, ∀r, t, s
(21)
X
∀t
zk,t,s ≤T r
k,s, ∀k ∈ΩDL(s), s
(22)
1
T r
k,s
t−1
X
τ=1
zk,τ,s −1 + ϵ ≤uk,t,s ≤
1
T r
k,s
t−1
X
τ=1
zk,τ,s, ∀k ∈ΩDL(s), t, s
(23)
Figure 4: A crew assignment example with 2 depots and 5 crews.
Deﬁne zk,t,s as a binary variable that equals 1 if line k is being repaired
at time t on scenario s, and ΩDL(s) as the set of damaged lines on scenario
s. Constraint (21) limits the number of repairs being conducted in each area
according to the number of crews nCrew
r
available. Constraint (22) deﬁnes the
repair time for each damaged line. The line status uk,t,s equals 0 until the
repair process is conducted for T r
k,s time periods. Based on constraint (23),
let T r
k,s = 3, zk,t,s = {0, 0, 1, 1, 1, 0, 0}, then uk,t,s = {0, 0, 0, 0, 0, 1, 1}. For
example, when t = 6 and ϵ = 0.001, then constraint (23) becomes 0.668 ≤
uk,6,s ≤1, therefore, uk,6,s = 1.
15



<!-- page 16/37 -->

2.3.3. Network Operational Constraints
The next set of constraints are related to the operation of distribution
systems. We consider unbalanced power ﬂow equations, radiality constraints,
fuel consumption, and energy storage constraints. The unbalanced distribu-
tion system constraints are given below:
X
b∈ΩK(i,.)
P K
b,φ,t,s −
X
k∈ΩK(.,i)
P K
k,φ,t,s = P G
i,φ,t,s + P PV
i,φ,t,s
+ (P Ch
i,φ,t,s −P Dis
i,φ,t,s) −yi,t,sdP
i,φ,t, ∀i, φ, t, s
(24)
X
b∈ΩK(i,.)
QK
b,φ,t,s −
X
k∈ΩK(.,i)
QK
k,φ,t,s = QG
i,φ,t,s + QPV
i,φ,t,s
+ QESS
i,φ,t,s −yi,t,sdQ
i,φ,t, ∀i, φ, t, s
(25)
−uk,t,sP K,max
k
≤P K
k,φ,t,s ≤uk,t,sP K,max
k
, ∀k ∈ΩK, φ, t, s
(26)
−uk,t,sQK,max
k
≤QK
k,φ,t,s ≤uk,t,sQK,max
k
, ∀k ∈ΩK, φ, t, s
(27)
0 ≤P G
i,φ,t,s ≤P G,max
i
, ∀i ∈ΩEG, φ, t, s
(28)
0 ≤QG
i,φ,t,s ≤QG,max
i
, ∀i ∈ΩEG, φ, t, s
(29)
16



<!-- page 17/37 -->

0 ≤P G
i,φ,t,s ≤nMEG
i
P G,max
i
, ∀i ∈ΩCN, φ, t, s
(30)
0 ≤QG
i,φ,t,s ≤nMEG
i
QG,max
i
, ∀i ∈ΩCN, φ, t, s
(31)
Ui,φ,t,s −Uj,φ,t,s ≥2( ˆRijP K
ij,φ,t,s + ˆXijQK
ij,φ,t,s)
+ (uk,t,s + pij,φ −2)M, ∀k, ij ∈ΩK, φ, t, s
(32)
Ui,φ,t,s −Uj,φ,t,s ≤2( ˆRijP K
ij,φ,t,s + ˆXijQK
ij,φ,t,s)
+ (2 −uk,t,s −pij,φ)M, ∀k, ij ∈ΩK, φ, t, s
(33)
χi,t,sU min
i
≤Ui,φ,t,s ≤χi,t,sU max
i
, ∀i, φ, t, s
(34)
X
k∈∈ΩB(l)
uk,t,s ≤|ΩB(l)|−1, ∀l ∈Ωloop, t, s
(35)
Constraints (24) and (25) are the active and reactive nodal power balance
constraints, where P K
ij,φ,t,s and QK
ij,φ,t,s are the active and reactive line ﬂows,
and P G
i,φ,t,s and QG
i,φ,t,s are the power outputs of the generators. The active
charging/discharging and reactive power outputs of energy storage systems
are denoted by P Ch
i,φ,t,s, P Dis
i,φ,t,s and QESS
i,φ,t,s. Constraints (26)-(27) represent the
active and reactive power limits of the lines, where the limits (P K,max
k
and
QK,max
k
) are multiplied by the line status binary variable uk,t,s. Therefore, if a
17



<!-- page 18/37 -->

line is disconnected or damaged, power cannot ﬂow through it. Constraints
(28)-(29) limit the output of the generators to P G,max
i
and QG,max
i
. Similarly,
we limit the output of the MEGs in (30)-(31) if an MEG is installed (nMEG
i
=
1).
Constraints (32) and (33) calculate the voltage diﬀerence along line k
between bus i and bus j, where Ui,φ,t,s is the square of voltage magnitude of
bus i. We use the big-M method to relax constraints (32) and (33), if lines
are damaged or disconnected.
ˆRij and ˆXij are the unbalanced three-phase
resistance matrix and reactance matrix of line ij, which can be referred
to [22]. The vector pij,φ represents the phases of line ij. Constraint (34)
guarantees that the voltage is limited within a speciﬁed region (U min
i
and
U max
i
), and is set to 0 if the bus is in an outage area. Constraint (35) can
guarantee the radiality network during the network reconﬁguration. In this
paper, we assume that all the possible loops can be identiﬁed by depth-ﬁrst
search method. The set of loops are given by Ωloop, and the set of switches
in loop l is given by ΩB(l).
For each fuel-based generator, the total fuel
consumption Fi,s is limited by the available fuel resources nFuel
i
in constraint
(36), as follows:
Fi,s = rf X
∀t
X
∀φ
P G
i,φ,t,s ≤nFuel
i
, ∀i ∈ΩG, φ, t, s
(36)
Next, we model the operation constraints for ESSs and MESs. The con-
straints include the change in state of charge (SOC), charging and discharging
limits, and reactive power limits. Let ΩES be the set of buses with ESSs, and
ΩESC = ΩES ∪ΩCN. We can then deﬁne the energy storage constraints as
18



<!-- page 19/37 -->

follows:
ESOC
i,t,s =ESOC
i,t−1,s+
∆t
(P
∀φ P Ch
i,φ,t,sηCh −P
∀φ P Dis
i,φ,t,s/ηDis)
ECap
i
, ∀i ∈ΩESC, φ, t, s
(37)
ESOC,min
i
≤ESOC
i,t,s ≤ESOC,max
i
, ∀i ∈ΩESC, t, s
(38)
0 ≤P Ch
i,φ,t,s ≤hi,t,sP Ch,max
i
, ∀i ∈ΩESC, φ, t, s
(39)
0 ≤P Dis
i,φ,t,s ≤(1 −hi,t,s)P Dis,max
i
, ∀i ∈ΩESC, φ, t, s
(40)
−QESS,max
i
≤QESS
i,φ,t,s ≤QESS,max
i
, ∀i ∈ΩES, φ, t, s
(41)
0 ≤P Ch
i,φ,t,s ≤nMES
i
P Ch,max
i
, ∀i ∈ΩCN, φ, t, s
(42)
0 ≤P Dis
i,φ,t,s ≤nMES
i
P Dis,max
i
, ∀i ∈ΩCN, φ, t, s
(43)
−nMES
i
QESS,max
i
≤QESS
i,φ,t,s ≤nMES
i
QESS,max
i
, ∀i ∈ΩCN, φ, t, s
(44)
Constraint (37) determines the state of charge of ESSs (ESOC
i,t,s ). ECap
i
denotes the maximum capacity of the storage system. To ensure safe ESS
operation, the SOC and charging (P Ch
i,φ,t,s) and discharging (P Dis
i,φ,t,s) power
19



<!-- page 20/37 -->

of ESSs are constrained as shown in (38)-(40). Here, ESOC,min
i
, ESOC,max
i
,
P Ch,max
i
and P Dis,max
i
deﬁne the permissible range of SOC, and maximum
charging and discharging power, respectively. In constraints (39)-(40), the
binary variable hi,t,s indicates that ESSs cannot charge and discharge at the
same time instant. The ESS charging/discharging eﬃciency are represented
by ηCh/ηDis. The reactive power of ESS, QESS
i,φ,t,s, is kept within maximum
limit, QESS,max
i
, through constraint (41). For MES units, we add constraint
(42)-(43) so that if nMES
i
= 0, the output power is 0 at bus i. The same
method is applied for the reactive power in (44).
3. Solution Algorithm
When the number of scenarios is ﬁnite, a two-stage stochastic problem
can be modeled as a single-stage large linear programming model, where each
constraint in the problem is duplicated for each realization of the random
data. For problems where the number of realization is too large or inﬁnite,
the Monte Carlo sampling technique can be used to generate a manageable
number of scenarios. In this work, we use the scenario decomposing method
PH to solve the proposed two-stage stochastic pre-event preparation problem.
3.1. Two-stage Progressive Hedging Algorithm
The proposed two-stage stochastic pre-event preparation problem (4)-(44)
can be compactly reformulated with an extensive form (EF) as follows:
ξ = min
x,ys aTx +
X
∀s
Pr(s)bT
s ys
(45)
20



<!-- page 21/37 -->

s.t. (x, ys) ∈Qs, ∀s
(46)
where a and bs are vectors containing the coeﬃcients associated with the
compact ﬁrst-stage variable x and compact second-stage variable ys in the
objective (45), respectively. The constraint (46) represents the subproblem
constraints that ensure a feasible solution. The PH algorithm decomposes
the extensive form into scenario-based subproblems, by relaxing the non-
anticipativity of the ﬁrst-stage variables. Hence, with the total number S
of scenarios, the proposed stochastic pre-event preparation problem is de-
composed into S subproblems.
The proposed two-stage PH algorithm is
presented in Algorithm 1. Deﬁne τ as iteration number, ρ as a penalty fac-
tor and ϵ as a termination threshold. The PH algorithm starts by solving
the subproblems with individual scenarios. Note that for an individual sce-
nario, the two-stage model is reformulated to a single-level problem. In Step
4, the ﬁrst-stage solution obtained from Step 2 is aggregated to obtain the
expected value ¯x. Step 5 calculates the value of the multiplier ηs. In Step
8, the subproblems are solved, where each subproblem is augmented with
a linear term proportional to the multiplier ητ−1
s
and a squared two norm
term penalizing the diﬀerence of x from ¯xτ−1. Steps 9-10 are similar as Steps
4-5. The algorithm terminates once all ﬁrst-stage decisions xs converge to a
common ¯x.
3.2. Convergence and Solution Validation
As shown in Algorithm 1, the convergence metric gτ of progressive hedg-
ing algorithm at each iteration τ is expressed as the deviation from the mean
21



<!-- page 22/37 -->

Algorithm 1 The Two-Stage PH Algorithm
1: Initialization: Let τ := 0.
2: For all s ∈S, compute.
3: x(τ)
s
:= arg minx{aTx + bT
s ys : (x, ys) ∈Qs}.
4: ¯x(τ) := P
∀s∈S Pr(s)x(τ)
s .
5: η(τ)
s
:= ρ(x(τ)
s
−¯x(τ)).
6: τ := τ + 1.
7: For all s ∈S, compute.
8: x(τ)
s
:= arg minx{aTx + bT
s ys + η(τ−1)
s
x + ρ
2∥x(τ)
s
−¯x(τ)∥2: (x, ys) ∈Qs}.
9: ¯x(τ) := P
∀s∈S Pr(S)x(τ)
s .
10: η(τ)
s
:= η(τ−1)
s
+ ρ(x(τ)
s
−¯x(τ)).
11: if P
∀s∈S Pr(s)∥x(τ)
s
−¯x(τ)∥≤ε then
12:
Go to Step 5.
13: else
14:
terminate.
15: end if
summed across all ﬁrst-stage variables xs(τ) and the average value of the
ﬁrst-stage variable ¯xτ as follows:
gτ =
X
s∈S
Pr(s)∥xs(τ) −¯xτ∥
(47)
Numerical results for convergence analysis are given in case study section.
In order to test the solution quality based on the limited generated damage
scenarios, we follow the suggestion from [20] and apply MRP to test the
stability and quality of the candidate solutions, as shown in Algorithm 2.
MRP is to repeat the procedure of generating S scenarios and solving the
proposed model for S times and construct the conﬁdence interval (CI) for
the optimality gap. The detailed steps in MRP is shown in Algorithm 2,
where ¯
Gn(ng) is the gap estimate and s2
G(ng) is the sample variance.
22



<!-- page 23/37 -->

Algorithm 2 Multiple Replication Procedure
1: Input: Value α ∈(0, 1) (e.g., α = 0.05), sample size n, replication size
ng and a candidate solution ˆx ∈X.
2: Output: Approximate (1 −α) as the level conﬁdence interval on µˆx.
3: For k = 1, 2, ..., ng.
4: Sample i.i.d. observations ζk1, ζk2, ..., ζkn from the distribution of ζ.
5: Solve (SPn) using ζk1, ζk2, ..., ζkn to obtain xk∗
n .
6: Gk
n(ˆx) := n−1 Pn
j=1(f(ˆx, ζkj) −f(xk∗
n , ζkj)).
7:
¯
Gn(ng) :=
1
ng
Png
k=1 Gk
n(ˆx).
8: s2
G(ng) :=
1
ng−1
Png
k=1(Gk
n(ˆx) −¯
Gn(ng))2.
9: ϵ := tng−1,αSG(ng)/√ng.
10: Obtain one-sided CI on [0, ¯
Gn(ng) + ϵg].
4. Case Study
In this section, a large-scale system is used as a test case to verify the scal-
ability and eﬀectiveness of the two-stage stochastic pre-event resource alloca-
tion model. This large-scale system consists of 3 existing test systems, EPRI
ckt5, ckt7 systems [23], and IEEE 8500 bus system [24], Following the sugges-
tions from [25], the cost parameters in the simulation are CD = 14$/kWh,
CSW = 8$, CF = 1$/L and rF = 0.3L/kWh. The stochastic models and
algorithms are implemented using the PySP package in Pyomo [26]. IBM’s
CPLEX 12.6 mixed-integer solver is used to solve all subproblems. The ex-
periments were performed on Iowa State University’s Condo cluster, whose
individual blades consist of two 2.6 GHz 8-Core Intel E5-2640 v3 processors
and 128 GB of RAM.
4.1. Pre-Event Preparation Results
In this case, we have included 9 depots that are hosting a total of 27
crews, 9 dispatchable DGs, 8 MEGs, 3 MESs, 123 switches, 5 small PVs, 15
23



<!-- page 24/37 -->

large PVs, and 12 ESSs. The 9 DGs are rated at 300 kW and 250 kVAr.
The 5 small PVs are rated at 11kW∼22kW. The 15 large PVs are rated
at 500 kW. The 12 ESSs are rated at 500 kW/ 3500 kWh. The pre-event
preparation model of the large-scale system is solved in 10.2 hours with 10
damage scenarios.
The ﬁrst-stage decision variables (locations of MEGs,
MESs and crews) are shown in Figure 5. 27 crews are allocated to 9 diﬀerent
depots. The value inside the crew depot in Figure 5 represents the number
of crews assigned to that depot. Areas with large number of crews indicates
that the lines in the area have high damage probabilities.
Crew Depot
MEG
DG
Large PV+Battery
Small PV
MES
Figure 5: Resource allocation of large-system with the proposed model.
24



<!-- page 25/37 -->

As discussed in Section 3.2, we use the convergence metric to evaluate the
convergence speed of the proposed model. At the same time, we also compare
the computational speed with and without a soft-start solution. Soft-start
solution means that the previous computed solution in other instance will be
used as the starting point. The comparison result is shown in Figure 6. If the
convergence metric reaches the convergence threshold 0.01, the algorithm will
stop and obtain the optimal solution. The instance with soft-start solution
converges at 57 iteration and takes 10.2 hours. The case without soft-start
solution converges after 100 iteration and takes 24.3 hours.
To test the
solution quality with MRP, based on the limited generated damage scenarios,
the one-sided CI of the obtained solution is [0, 12.48%].
This small gap
indicates that our solution is stable and of high quality.
Figure 6: The convergence metric comparison with and without soft-start solutions.
25



<!-- page 26/37 -->

To evaluate the performance of the developed pre-event preparation model,
the model is compared to a base model. The base case is generated by the
following steps: (i) one MEG are prepositioned at the substations. (ii) Extra
MEG are prepositioned at high-priority loads. (iii) PV and ESS are not con-
sidered. (iv) Fuel is allocated to the MEGs such that they can operate for at
least 24 hours. (v) Crews are allocated evenly between depots. In this work,
we calculate average outage duration by dividing the sum of outage dura-
tions for the loads with the number of loads. To compare the performance of
the proposed model and the base model, we generate a random scenario and
test the response of the system. The generated scenario has 103 damaged
lines and they were aggregated to 34 damaged areas in Figure 7. Each circle
represents the repair time needed for the speciﬁc damaged area considering
all the aggregated damaged lines.
26



<!-- page 27/37 -->

Figure 7: Aggregated damaged areas.
The comparison between the base model and the proposed method is
shown in Figure. 8. In the base model, the total restored energy is 231,422.38
kWh and the average outage duration is 14.69 hours.
In the proposed
method, the total restored energy is 291,727.48 kWh and the average out-
age duration is 11.28 hours. Therefore, approximately 20.67% more loads
are served by the proposed method and the outage duration decreased by
30.22%.
27



<!-- page 28/37 -->

Figure 8: Comparison between base model and proposed method.
4.2. Impacts of Solar PV on System Resilience
To show the advantages of the PV systems, we test the response of the
system with the proposed method and diﬀerent PV penetration levels. As
discussed in Section 2.3.1, we consider three types of PV: (i) Type I PV,
which represents residential PV panels and the rated capacity is assumed to
be 6 kW; (ii) Type II PV, which represents mid-size PV systems and the
rated capacity is assumed to be 48 kW; (iii) Type III PV, which represents
large utility PV farm and the rated capacity is assumed to be 2000 kW.
Based on the number of diﬀerent types of PVs, we deﬁne 6 PV penetration
levels as 9%, 27%, 45%, 63%, 81%, and 99%. The number of Type I, II and
III PVs for each PV penetration levels is summarized in Table 1. To better
collaborate the setting of PV penetration, the number of dispatchable DGs
has been changed to 10 and the positions of those DGs have been changed
28



<!-- page 29/37 -->

accordingly. The rest of case settings keep the same.
Table 1: Number of diﬀerent types of PV
PV Penetration
Percentage
Type I
PV
Type II
PV
Type III
PV
9%
8
1
1
27%
24
4
3
45%
40
7
5
63%
63
9
7
81%
72
12
9
99%
88
15
11
Based on the results of Figure. 9, it can be observed that diﬀerent PV
penetration levels have diﬀerent allocation results of the ﬂexible resources,
including the positions of MEGs, MESs and number of repair crews.
29



<!-- page 30/37 -->

(c) 45% PV
(a) 9% PV
(b) 27% PV
(d) 63% PV
(e) 81% PV
(f) 99% PV
Crew Depot
MEG
DG
MES
Type III PV
Type II PV
Type I PV
Crew Depot
MEG
DG
MES
Type III PV
Type II PV
Type I PV
Crew Depot
MEG
DG
MES
Type III PV
Type II PV
Type I PV
Crew Depot
MEG
DG
MES
Type III PV
Type II PV
Type I PV
Crew Depot
MEG
DG
MES
Type III PV
Type II PV
Type I PV
Crew Depot
MEG
DG
MES
Type III PV
Type II PV
Type I PV
Figure 9: Pre-event resource allocation results with diﬀerent PV penetration levels.
30



<!-- page 31/37 -->

Figure. 10 shows the percentage of power served during the event, and af-
ter the repair process starts. Table 2 and Table 3 compare the amount of load
served and average outage duration with diﬀerent levels of PV penetration.
Figure 10: Load served percentage comparison of proposed model with various PV pene-
tration level and base model.
Based on the results from Figure. 10, Table 2 and Table 3, it can be seen
that the penetration of PV contributes to enhancing system resilience. Ap-
proximately 31.13% more loads are served compared to the base model when
the proposed method with 99% PV penetration is used. Also, the average
outage duration decreased by 31.12%. However, compared with the case of
81% PV penetration level, the proposed method with 99% PV penetration
does not have signiﬁcant improvement.
31



<!-- page 32/37 -->

Table 2: The amount of load served and resilience improvement with diﬀerent level of PV
penetration
PV Penetration
Percentage
Load Served
(kWh)
Resilience Improvement
Percentage(%)
0
251,210.72
-
9%
318,668.37
26.85
27%
335,525.77
33.56
45%
336,710.74
34.04
63%
344,588.22
37.17
81%
360,668.04
43.57
99%
364,785.93
45.21
Table 3: The amount of average outage duration and outage decreased percentage with
diﬀerent level of PV penetration
PV Penetration
Percentage
Average Outage
Duration (hour)
Outage Decreased
Percentage(%)
0
14.69
-
9%
12.33
16.07
27%
11.72
20.22
45%
11.65
20.69
63%
11.21
23.69
81%
10.45
28.86
99%
10.12
31.11
5. Conclusion
In this paper, we develop a two-stage stochastic pre-event resource allo-
cation method for upcoming extreme events, which enables faster and more
eﬃcient post-event restoration. The proposed pre-event method leverages the
32



<!-- page 33/37 -->

pre-allocation of mobile resources, fuel resources and labor resources. It also
facilitates the beneﬁts of distributed PV systems in resilience improvement
of distribution grids. According to the case studies, we have the following
observations: (i) Compared to the base model without pre-event resource
allocation, the proposed pre-event preparation model can serve more loads
and reduce the outage duration. (ii) Based on the response of the system
with diﬀerent PV penetration levels, it can be observed that the proposed
pre-event preparation model with high PV penetration can further improve
system resilience and reduce the outage duration. Therefore, PV systems
can play a critical role in improving distribution grid resilience and further
promote the renewable energy deployment. (iii) By considering the trade-oﬀ
between solution accuracy and computation eﬃciency, the result of MRP
indicates that the proposed model’s solutions with a limited number of sce-
narios can be very stable and of high quality. The scalability of the proposed
pre-event preparation model is veriﬁed with a large-scale system.
Acknowledgement
This work was supported by the U.S. Department of Energy Wind Energy
Technologies Oﬃce under Grant DE-EE0008956.
References
[1] A. M. Salman, Y. Li, M. G. Stewart, Evaluating system reliability and
targeted hardening strategies of power distribution systems subjected to
hurricanes, Reliability Engineering & System Safety 144 (2015) 319–333.
33



<!-- page 34/37 -->

[2] E. O. of the President, Economic beneﬁts of increasing electric grid re-
silience to weather outages, Technical Report, White House Tech. Rep.,
2020.
[3] A. Gholami, T. Shekari, S. Grijalva, Proactive management of micro-
grids for resiliency enhancement: An adaptive robust approach, IEEE
Trans. Sustain. Energy 10 (2019) 470–480.
[4] C. Wang, Y. Hou, F. Qiu, S. Lei, K. Liu, Resilience enhancement with
sequentially proactive operation strategies, IEEE Trans. Power Syst. 32
(2017) 2847–2857.
[5] M. Panteli, P. Mancarella, D. N. Trakas, E. Kyriakides, N. D. Hatziar-
gyriou,
Metrics and quantiﬁcation of operational and infrastructure
resilience in power systems, IEEE Trans. Power Syst. 32 (2017) 4732–
4742.
[6] S. Wang, B. R. Sarker, L. Mann, E. Triantaphyllou, Resource planning
and a depot location for electric power restoration, Euro. J. Oper. Res.
155 (2004) 22–43.
[7] A. Arif, Z. Wang, J. Wang, C. Chen, Power distribution system outage
management with co-optimization of repairs, reconﬁguration, and DG
dispatch, IEEE Trans. Smart Grid 9 (2018) 4109–4118.
[8] A. Arif, Z. Wang, C. Chen, B. Chen, A stochastic multi-commodity
logistic model for disaster preparation in distribution systems, IEEE
Trans. Smart Grid 11 (2020) 565–576.
34



<!-- page 35/37 -->

[9] B. Taheri, A. Safdarian, M. Moeini-Aghtaie, M. Lehtonen, Enhancing
resilience level of power distribution systems using proactive operational
actions, IEEE Access 7 (2019) 137378–137389.
[10] S. Lei, J. Wang, C. Chen, Y. Hou, Mobile emergency generator pre-
positioning and real-time allocation for resilient response to natural dis-
asters, IEEE Trans. Smart Grid 9 (2018) 2030–2041.
[11] S. Lei, C. Chen, H. Zhou, Y. Hou, Routing and scheduling of mobile
power sources for distribution system resilience enhancement,
IEEE
Trans. Smart Grid 10 (2019) 5650–5662.
[12] J. Kim, Y. Dvorkin, Enhancing distribution system resilience with mo-
bile energy storage and microgrids, IEEE Trans. Smart Grid 10 (2019)
4996–5006.
[13] S. Samara, M. F. Shaaban, A. H. Osman,
Optimal management of
mobile energy generation and storage systems, IEEE Access 8 (2020)
203890–203900.
[14] S. Belding, A. Walker, A. Watson, Will solar panels help when the
power goes out?, Technical Report, National Renewable Energy Tech.
Rep., 2020.
[15] R. T. Rockafellar, R. J.-B. Wets, Scenarios and policy aggregation in
optimization under uncertainty, Mathematics of operations research 16
(1991) 119–147.
[16] J.-P. Watson, D. L. Woodruﬀ, Progressive hedging innovations for a class
35



<!-- page 36/37 -->

of stochastic mixed-integer resource allocation problems, Computational
Management Science 8 (2011) 355–370.
[17] S. Ma, B. Chen, Z. Wang, Resilience enhancement strategy for distri-
bution systems under extreme weather events, IEEE Trans. Smart Grid
9 (2018) 1442–1451.
[18] S. Ma, S. Li, Z. Wang, F. Qiu, Resilience-oriented design of distribution
systems, IEEE Trans. Power Syst. 34 (2019) 2880–2891.
[19] B. Chen, C. Chen, J. Wang, K. L. Butler-Purry,
Sequential service
restoration for unbalanced distribution systems and microgrids, IEEE
Trans. Power Syst. 33 (2018) 1507–1520.
[20] A. Arif, Z. Wang, C. Chen, J. Wang, Repair and resource scheduling
in unbalanced distribution systems using neighborhood search, IEEE
Trans. Smart Grid 11 (2020) 673–685.
[21] F. Y. Melhem, O. Grunder, Z. Hammoudan, N. Moubayed, Energy man-
agement in electrical smart grid environment using robust optimization
algorithm, IEEE Trans. Industry Applications 54 (2018) 2714–2726.
[22] Q. Zhang, K. Dehghanpour, Z. Wang, Distributed CVR in unbalanced
distribution systems with PV penetration, IEEE Trans. Smart Grid 10
(2019) 5308–5319.
[23] EPRI, OPENDSS test circuits, Apr.2019. URL: https://sourceforge.
net/p/electricdss/discussion/beginners.html.
36



<!-- page 37/37 -->

[24] R. F. Arritt, R. C. Dugan, The IEEE 8500-node test feeder, in: IEEE
PES T&D Conference, 2010, pp. 1–6.
[25] S. Ma, Resilience-oriented design and proactive preparedness of electri-
cal distribution system, PhD Thesis (2020).
[26] W. E. Hart, C. D. Laird, J.-P. Watson, D. L. Woodruﬀ, G. A. Hackebeil,
B. L. Nicholson, J. D. Siirola, Pyomo-optimization modeling in python,
volume 67, Springer, 2017.
37
