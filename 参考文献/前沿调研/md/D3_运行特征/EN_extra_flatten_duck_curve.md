<!--
source: D3_运行特征/EN_extra_flatten_duck_curve.pdf
sha256: d841ad4d98838e04d23ecafed601e5a945587e519fa3ce7b4d42f34272b26947
method: pymupdf
pages: 5
-->

<!-- page 1/5 -->

Flattening the Duck Curve: A Case for Distributed
Decision Making
Rabab Haider∗, Giulio Ferro†, Michela Robba†, and Anuradha M. Annaswamy∗
∗Mechanical Engineering, Massachusetts Institute of Technology, Cambridge, USA
† DIBRIS, University of Genoa, Genoa, Italy
Email: rhaider@mit.edu, giulio.ferro@edu.unige.it, michela.robba@unige.it, aanna@mit.edu
Abstract—The large penetration of renewable resources has
resulted in rapidly changing net loads, resulting in the char-
acteristic “duck curve”. The resulting ramping requirements of
bulk system resources is an operational challenge. To address
this, we propose a distributed optimization framework within
which distributed resources located in the distribution grid are
coordinated to provide support to the bulk system. We model the
power ﬂow of the multi-phase unbalanced distribution grid using
a Current Injection (CI) approach, which leverages McCormick
Envelope based convex relaxation to render a linear model. We
then solve this CI-OPF with an accelerated Proximal Atomic
Coordination (PAC) which employs Nesterov type acceleration,
termed NST-PAC. We evaluate our distributed approach against a
local approach, on a case study of San Francisco, California, using
a modiﬁed IEEE-34 node network and under a high penetration
of solar PV, ﬂexible loads, and battery units. Our distributed
approach reduced the ramping requirements of bulk system
generators by up to 23%.
Index Terms—Distribution grid, Distributed optimization, En-
ergy storage
I. INTRODUCTION
The push towards decarbonization of the electric grid has
seen an explosive growth in renewable energy installation.
The state of California generates approximately 25% of its
electricity demand from solar resources, resulting in the char-
acteristic “duck curve” in net system load [1]. This new
operating condition, where dispatchable bulk resources must
quickly meet the large and rapid change in electricity demand,
introduces challenges to grid operators. Storage offers one so-
lution, as a ﬂexible and low-inertia resource, however remains
too expensive for utility-scale system-wide adoption. Instead,
we propose system operators look towards the distribution
grid to provide some support. Small-scale consumer owned
distributed energy resources (DERs) which include rooftop
PV with inverters, demand response, and batteries can provide
support to the bulk grid.
Recent works in this area are [2] which proposes a game
theoretic framework for dynamic pricing, and [3] which shifts
thermal cooling loads of residential units to mitigate duck
curve effects. Where these works rely on local approaches
with assets locally providing the mitigation mechanisms, our
This material is based upon work partially supported by the MathWorks
Mechanical Engineering Fellowship, U.S. Department of Energy under Award
Number DE-IA0000025, NSF CPS-DFG Joint award 1932406, and the
DIBRIS-UNIGE on institutional funding SEED 2019.
proposed work takes a systems-approach. We leverage dis-
tributed optimization to deploy resources over a larger spacial
area of the distribution grid to enhance mitigation strategies
while suitably accommodating global network constraints.
The main contribution of the paper pertains to the distributed
coordination of DERs across a large region of the distribution
grid to mitigate the duck curve. This coordination is accom-
plished by leveraging the variable power factor setting of PV
inverters, ﬂexible loads to reduce consumption, and distributed
storage devices such as community batteries. This central
contribution is realized by formulating the global optimization
problem as an optimal power ﬂow, and employing a current-
injection (CI) based linear model describing the power physics
of the unbalanced distribution grid. The CI-based OPF is
solved in a distributed fashion, using a Proximal Atomic
Coordination (PAC) approach [4] with Nesterov acceleration,
called NST-PAC. We evaluate the performance on a modiﬁed
IEEE-34 node network, using load and generation data for San
Francisco. Our results show the successful mitigation of the
duck curve through the coordination of spatially distributed
DERs.
In Sections II and III we introduce the CI power ﬂow model
for the unbalanced distribution grid, and the accelerated dis-
tributed optimization algorithm called NST-PAC. In Section IV
we carry out a numerical case study, comparing local and
distributed paradigms. We provide conclusions in Section V.
II. CURRENT INJECTION MODEL
The distribution grid is a highly unbalanced network, with
many single- and two-phase lines and corresponding loads. As
DER penetration increases, many of which are added to single-
phase lines, the network will become more unbalanced. In light
of this, power ﬂow models which assume balanced ﬂow [5]
or those which are valid for only a small range of angle im-
balances [6] cannot suitably describe the future grid. Further,
the faster timescales of operation due to renewable variability
and ﬂexibility requirements need a model which is simple and
results in OPF problems which are computationally tractable.
For this reason, there is interest in developing scalable linear
models for the unbalanced grid, and leveraging distributed
computation and algorithms to solve the OPF problem.
In this work, we utilize the Current Injection (CI) model,
a linear model for multi-phase unbalanced distribution grids.
The CI model takes a similar approach to the Bus Injection
arXiv:2111.06361v2  [math.OC]  2 Feb 2022



<!-- page 2/5 -->

Model, wherein all nodal power injections are modeled as
current injections, and all phasor variables are represented in
Cartesian coordinates. The 3-phase impedance matrix is used
to describe the self and mutual inductance between phases to
model the coupling of phases that are common to a distribution
grid. The non-convexity of the AC-OPF and the subsequent
nonlinearity of SOCP and SDP convexiﬁcation strategies typ-
ically used are avoided in the CI approach by leveraging
McCormick Envelope (MCE) based convex relaxation [7] for
the bilinear power relations. The MCE uses the convex hull
representation of bilinear terms to render a linear OPF model.
Suitable pre-processing techniques can be utilized to determine
adequate bounds on the nodal voltages and currents to ensure
a tight convex relaxation.
A. Problem Formulation
We denote a general distribution network as a graph
Γ(N, E), where N := {1, ..., N} denotes the set of nodes,
E := {(m, n)} denotes the set of edges, and each phase is
expressed as φ ∈P, P = {a, b, c}. The CI-OPF for the
network is then written as1:
min
x f (x)
(1a)
AV = ZIﬂow
(1b)
IR = Re

AT Iﬂow

,
II = Im

AT Iﬂow

(1c)
P φ
j = V φ,R
j
Iφ,R
j
+ V φ,I
j
Iφ,I
j
(1d)
Qφ
j = −V φ,R
j
Iφ,I
j
+ V φ,I
j
Iφ,R
j
(1e)
P φ
j ≤P φ
j ≤P φ
j ,
Qφ
j ≤Qφ
j ≤Qφ
j
(1f)
V φ,R
j
≤V φ,R
j
≤V φ,R
j
,
V jφ,I ≤V φ,I
j
≤V φ,I
j
(1g)
Iφ,R
j
≤Iφ,R
j
≤Iφ,R
j
,
Iφ,I
j
≤Iφ,I
j
≤Iφ,I
j
(1h)
where x =

IR II V R V I P Q IR
ﬂow II
ﬂow

is the decision
vector for the CI-OPF problem; I, V, P, Q denote the vector
of nodal current injections, voltages, and real/reactive power
injections respectively; Iﬂow denotes the vector of line currents;
A ∈R3N×3N is the 3-phase graph incidence matrix; Z is
the system impedence matrix. We use xR and xI to denote
the real and imaginary components of a complex number x;
overbar x and underbar x denote the upper and lower limits
of a variable x; Re(·) and Im(·) denote the real and imaginary
components of a complex number. Constraint (1b) describes
the generalized Ohm’s law, (1c) describe Kirchhoff’s Current
Law, and (1d)-(1e) are the deﬁnitions of real and reactive
power. Constraints (1d)-(1h) are for all nodes j ∈N, per
each phase φ ∈P, and for all time t. The convex relaxation
of the CI-OPF problem through McCormick envelopes adds
additional constraints to the problem namely (1h), concerning
the minimum and maximum limits of injected current at each
phase of each node. The determination of these upper and
lower bounds on nodal current is not trivial. An effective
heuristic to deﬁne these values is presented in [9].
1For brevity, we omit the McCormick Envelope relaxation of the bilinear
terms and the pre-processing step. See [8], [9] for details
B. Model of DERs
We use active sign convention, such that nodal injections are
positive. The PV units are modelled as a generator with vari-
able power factor (pf), equipped with a multiphase inverter,
where the ratio of P and Q determine the pf setting:
P φ
j tan(cos−1(−pf)) ≤Qφ
j ≤P φ
j tan(cos−1(pf))
(2)
Flexible loads are reductions in real power demand (reactive
power loads are ﬁxed), and are modelled as a percentage
reduction from the forecasted load. The power constraints
are modiﬁed as P j(t) = P j(t) ∗(1 −αDR
j (t)), by recall-
ing the use of active sign convention. For inﬂexible loads,
P j = P j, P j ≤0. Prosumers, which are nodes where both
load and generation are present, are modelled with additional
variables representing both load and generation, P L and P G
respectively. For prosumers, the inverter is modelled on P G
and QG, and load ﬂexibility is modelled on P L. Variables P L
and P G are both nonnegative, and the same for reactive power.
Pj = P G
j −P L
j ,
P G
j
≥0, P L
j ≥0
(3a)
Qj = QG
j −QL
j ,
QL
j ≥0
(3b)
P j = P G
j −P L
j ,
P j = P G
j −P L
j
(3c)
Qj = QG
j −QL
j ,
Qj = QG
j −QL
j
(3d)
Battery storage devices are modelled using the power charge
and discharge, P sc
j (t) and P sd
j (t) respectively for node j and
time t. These are nonnegative variables. The state of charge,
bj(t), is calculated as an integral constraint using the actions
of the previous period and the initial state of charge, b0
j :=
bj(t = 0). We model charge and discharge efﬁciencies (ηC
j
and ηD
j ), self-discharge rate (ηself
j ), and impose a minimum
state of charge (bj) to ensure battery health. We assume all
batteries operate at unity power factor, i.e. Qj = 0
∀t.
Pj = 1
ηD
j
P sd
j (t) −ηC
j P sc
j (t)
(4a)
0 ≤P sd
j ≤P
sd
j ,
0 ≤P sc
j ≤P
sc
j
(4b)
bj(t) = (1 −ηself
j )bj(t −1) + ηC
j P sc
j (t) −1
ηD
j
P sd
j (t)
(4c)
bj ≤bj(t) ≤bj
(4d)
The storage model introduces a dependency on control action
in one period to previous periods. The other DERs and loads
do not have inter-temporal constraints, so constraints (1)-(3)
are simply replicated for each time step t.
III. PAC-BASED DISTRIBUTED IMPLEMENTATION
In this section we introduce a PAC-based distributed opti-
mization algorithm to coordinate a large number of spatially
distributed DERs at the grids edge. Consider a global optimiza-
tion problem composed of equality and inequality constraints,
which may be coupled in time
min
x
S
X
i=1
fi(x)
s. t.
Gx = b,
Hx ≤d
(5)



<!-- page 3/5 -->

where P
i∈S fi (x) represents the total objective function.
Problem (5) can be distributed into K = {1, ..., k, ...K}
separate coupled optimization problems, denoted as atoms.
We use a decomposition proﬁle which separates the vector
of variables x into two sets: L = {Lj,
∀j ∈K} and O =
{Oj,
∀j ∈K}, which represent the partition of decision
variables “owned” and “copied” by atom j. The set of total
variables (owned and copied) by an atom is denoted as T. The
decomposition proﬁle also separates the constraints into sets
owned by each atom, as C = {Cj,
∀j ∈K}. The notion of
variables copies are used to satisfy the coupling in constraints
and/or objective function. In the context of the CI model, the
power physics of the grid (1b)-(1c) result in these coupling
constraints. Note that the CI does not have coupling introduced
by inequality constraints, however the decomposition can be
trivially extended to coupled inequality constraints. Using the
decomposition proﬁle, we obtain:
min
aj
P
j∈K fj (aj)
subj. to:



Gjaj = bj,
for all j ∈K
Hjaj ≤dj,
for all j ∈K
Bja = 0,
for all j ∈K
(6)
where aj is atom j’s variables (both owned and copied),
fj (aj) is the atomic objective function, and Gj, bj, Hj, and
dj represent the submatrix or subvector of G, b, H, and d
respectively. Finally, B is in incidence matrix over the owned
and copied atomic variables, deﬁned as
Bm
i
≜



−1,
if i is ‘owned‘ and m a related ‘copy‘
1,
if m is ‘owned‘ and i a related ‘copy‘
0,
otherwise
We then use Bj (Bj) to denote the relevant incoming (out-
going) edges of the directed graph for atom-j. To fully paral-
lelize the optimization, we introduce coordination constraints,
which must be satisﬁed for every atom. These require all
atomic copied variables in a given jth atom to equal the value
of their corresponding owned in ith atom, i ̸= j:
Bja = 0
∀j ∈K
(7)
A. An Accelerated Algorithm: NST-PAC
We next present an accelerated variant of the PAC algorithm
in [4], which includes time-varying gains and Nesterov type
acceleration [10], called NST-PAC. The NST-PAC is a primal-
dual method with ℓ2 and proximal regularization, Nesterov
type acceleration for both primal and dual variables, and
privacy-preserving features. We begin by forming the atomic
Lagrangian function:
L (a, µ, ν) =
X
j∈K
h
fj
 aj

+ µT
j (Gjaj −bj) + νT
j Bja
i
=
X
j∈K
h
fj
 aj

+ µT
j (Gjaj −bj) + νT Bjaj
i
≜
X
j∈K
Lj
 aj, µj, ν
.
(8)
The algorithm is carried out as below:
aj [τ + 1] = argmin
aj∈R|Tj |

Lj
 aj, ˆµj [τ] , ˆν [τ]
+ ρjγj
2
Gjaj −bj
2
2
+ρjγj
2
Bjaj
2
2 +
1
2ρj
aj −aj [τ]
2
2

,
(9)
ˆaj [τ + 1] = aj [τ + 1] + αj[τ + 1](aj [τ + 1] −aj [τ])
(10)
µj [τ + 1] = ˆµj [τ] + ρjγj(Gjˆaj [τ + 1] −bj)
(11)
ˆµj [τ + 1] = µj [τ + 1] + φj[τ + 1](µj [τ + 1] −µj [τ])
(12)
Communicate ˆajfor all j ∈[K] with neighbors
(13)
νj [τ + 1] = ˆνj [τ] + ρjγjBjˆaj [τ + 1]
(14)
ˆνj [τ + 1] = νj [τ + 1] + θj[τ + 1](νj [τ + 1] −νj [τ])
(15)
Communicate ˆνj for all j ∈[K] with neighbors
(16)
where ρj, γj are atom-varying over-relaxation and step-size
parameters, respectively. The proposed NST-PAC uses ℓ2
regularization terms rather than the prox-linear variant in PAC.
Further, both primal and dual variables are accelerated using
Nesterov type acceleration, to speed up convergence. Further,
we extend the privacy-preserving feature of the PAC algorithm
to both the primal and dual variables, by using three iteration-
varying and atom speciﬁc parameters for the accelerated terms,
αj [τ] > αmin
j
, φj [τ] > φmin
j
and θj [τ] > θmin
j
. In the
original algorithm privacy is kept only for dual variables.
A detailed analysis of convergence rate, communication and
computational complexity, and privacy are provided in [4].
IV. CASE STUDY
We consider a case study of San Francisco, California, using
the IEEE-34 node network as a proxy for the distribution grid.
The load data from the IEEE datasheet serves as the daily
average load, and the 24-hr load proﬁles are obtained from
the ODEI dataset from NREL for the Typical Meteorological
Year [11]. All loads are assumed to have a constant power
factor of 0.95. The network loads are classiﬁed as residential
or commercial loads based on the size of the load, by matching
the load levels of the IEEE-34 network with the TMY data.
Commercial loads include retail space, small and medium
ofﬁce buildings, primary school, medium and large restaurants,
and a hospital. The network is modiﬁed to include DERs
which include clusters of rooftop photovoltaic (PV) units,
ﬂexible loads, and three battery storage units. The penetration
of PV is 38%, as measured by the ratio of nameplate capacity
to average system load. This high DER penetration scenario is
a reasonable projection given the RPS initiatives in California.
Each PV unit is assumed to be equipped with an inverter
with corresponding power electronic control, which can be
operated at variable power factor in the range of 0.8 to
1. PV curtailment is not considered. The ﬂexible loads are
modelled as typical residential cooling loads for California
[12]. Variations in nodal demand response are obtained by
shifting the baseline proﬁle obtained from [12] in time and
space, with both following zero-mean Gaussian distributions
with variances of 0.075 and 0.1 respectively. The three battery



<!-- page 4/5 -->

Residential Loads 
Commercial Loads
Batteries
No load
Fig. 1: Topology of IEEE-34 network. PV units and ﬂexible
loads are present throughout the network.
units are a 450kW-120kWh community unit2 at node 6, a
cluster of 40 Tesla Powerwall+ batteries (each 13.5kW-5kWh)
at node 19, and a 800kW-185kWh hospital unit at node 27.
Any load not met by local generation (or storage) is assumed
to be served by the bulk grid at the point of common coupling
(PCC), at node 1 in the network (j = 1). Figure 1 shows the
network topology.
A. Scenarios
We consider three scenarios, as below:
• Scenario A: Baseline. All PV inverters operate at unity
pf, and batteries and ﬂexible loads are not present.
• Scenario B: Local control. Each DER owner operates its
devices and manages its loads.
• Scenario C: Distributed control. All devices and loads are
coordinated using the NST-PAC algorithm.
Scenario A quite trivially is the characteristic duck curve,
where the high PV generation at unity power factor results in
large ramping requirements of transmission-level generators.
Scenario B is a local approach, where each agent will mini-
mize its peak load throughout the day. This serves as a very
rough approximation of reducing the ramping requirements
of bulk resources, by noticing that the largest ramp typically
coincides with the peak demand in the evening. This action can
be motivated by the fact that consumers can be charged based
on their peak energy consumption. To leverage the capabilities
of the storage devices, neighbouring nodes are clustered with
the battery. Residential loads (and corresponding DERs) at
nodes 3, 4, and 5, share the community battery at node
6. Residential loads at node 20 and the primary school at
node 21 share the cluster of Tesla Powerwall+ batteries at
node 19. The hospital at node 26 is assumed to own and
operate the battery at node 27. All remaining nodes are
treated as independent agents. After clustering, there are a
total of 26 agents in the network, each managing its own
consumption and generation, to minimize its peak load. The
multi-period optimization problem solved by each agent is
a simple power balance, where any load in excess of local
generation is assumed to be served by the bulk system. The
power physics between nodes within a cluster is not modelled.
The objective function is flocal(y) = maxt {−P(t)}, where
y =

P, Q, P L, P G, QL, QG, P sd, P sc
.
2Modeled on the Ellenbrook unit from the PowerBank trail, Australia [13]
Scenario C is the PAC-based approach which requires
coordination between the devices. This approach accommo-
dates system-level constraints including grid power physics,
and minimizes the ramping requirements at the PCC. In
Scenario C, the PAC agents solve the CI-based multi-phase
unbalanced OPF, to minimize the objective function f(x)
which minimizes the difference in power supplied by the
PCC from one hour to the next. The function is fPAC(x) =

P
φ∈P P φ
1 (t) −P φ
1 (t −1)
.
B. Results and Discussion
Each scenario was simulated on the IEEE-34 node network.
Figure 3 shows the net load served by the bulk system. The
load curve for Scenario A shows the characteristic high ramps
down and up when solar generation begins and ends. Scenario
B provides minimal improvement, reducing the load for most
hours of the day, while Scenario C effectively leverages the
DERs to reduce the ramping requirements. Note that the
objective function reduces the hour-to-hour change in load,
and to do so, increases load during the hours of peak PV
generation (roughly 10am to 4pm) to charge the batteries,
which are then discharged in the late evening to reduce the
net load. The magnitude of hour-to-hour ramping is shown in
Figure 4. Notably, the local optimization of Scenario B, which
minimizes the peak load throughout the day as a proxy for
minimizing the load ramp in the evening, is not able to suitably
reduce the ramping requirement. The distributed optimization
approach, on the other hand, is able to leverage system-
wide information and coordinate the DERs to provide grid-
level support, as needed by the bulk system. This coordinated
approach is able to reduce ramping requirements throughout
the day, with a 23% reduction in ramping requirements at the
4pm peak. Table I presents the total ramping reduction for
Scenarios B and C, as compared to the baseline in A, and the
computational run times. As expected, the proposed distributed
coordination signiﬁcantly outperforms the local approach, with
28% reduction in ramping required. The local approach is
unable to provide any reduction. Unsurprisingly, the local
approach takes less time to reach a decision (albeit an inferior
one), while the distributed approach takes considerably longer
(completing 1000 iterations). However, computational time of
20s is still well within the acceptable time-frame for decision
making, and enables DERs to provide bulk-level support.
We next investigate the impact of the battery units’ initial
state of charge. We run each Scenario for (1) Minimum SOC
where initial capacity is at 45, 0, and 160 kWh; (2) Mid SOC
where initial capacity is at 120, 400, and 400 kWh; and (3)
Full SOC where initial capacity is at 450, 540, and 800 kWh,
respectively for batteries at nodes 6, 19, and 27. Figure 2 plots
the SOC of each battery unit for the three cases. The usage
pattern in each of the cases is very similar, with charging in
the early morning and afternoon to build up storage capacity
for the evening. Interestingly, the ﬁnal SOC are non-zero for
the three cases, and are quite similar, suggesting the batteries
may be able to retain a higher minimum charge to be used
as backup power in the case of emergencies. The batteries



<!-- page 5/5 -->

(a) Minimum initial SOC
(b) Mid initial SOC
(c) Full initial SOC
Fig. 2: State of charge of each storage device for Scenario C, with different initial state of charge for each battery.
Fig. 3: Net load serviced by the bulk system, for each scenario.
These plots do not include power loss over lines.
Fig. 4: Magnitude of ramping required by bulk system gener-
ators for each scenario.
provide ﬂexibility to increase or decrease load throughout the
day, as required by the grid. The plots for net load are quite
similar for all three cases, and so have been omitted.
V. CONCLUSION
We presented and evaluated a distributed approach to co-
ordinate DERs to provide services to the bulk system. We
leverage a CI-based linear model of the unbalanced grid, and
an accelerated PAC-based algorithm called NST-PAC. Our
case study on a modiﬁed IEEE-34 node network shows how
distributed techniques can leverage information from different
A (Baseline)
B (Local)
C (Proposed)
Total ramping need (kW)
3923.7
3941.0
2839.4
Ramping reduction
-
-0.44%
27.63%
Mean run time per agent
-
0.0947s
16.97s
TABLE I: Summary of results for Scenarios A thru C. Sce-
nario A is baseline with no decision making, so no ramping
reduction or computational time to report.
resources to successfully mitigate the duck curve, reducing
ramping requirements of bulk system generators by up to 23%.
This framework can be extended to include electric vehicles,
by modeling the vehicle-to-grid capabilities and correspond-
ing cost of battery cycling and lifetime degradation in the
optimization problem. Using such an approach throughout
the distribution grid can reduce the challenges of the new
operating condition resulting from high solar and renewable
penetration, reduce system costs, and improve renewable
integration. Future work will concern the development of
faster distributed algorithms applicable to nonconvex costs and
constraints, with discrete and continuous controls.
REFERENCES
[1] CAISO, “California ISO demand response and energy efﬁciency
roadmap: Maximizing preferred resources,” 2013.
[2] M. Sheha, K. Mohammadi, and K. Powell, “Solving the duck curve
in a smart grid environment using a non-cooperative game theory
and dynamic pricing proﬁles,” Energy Conversion and Management,
vol. 220, p. 113102, 2020.
[3] I. Calero, C. A. Ca˜nizares, K. Bhattacharya, and R. Baldick, “Duck-
curve mitigation in power grids with high penetration of pv generation,”
IEEE Transactions on Smart Grid, vol. 13, no. 1, pp. 314–329, 2021.
[4] J. Romvary, G. Ferro, R. Haider, and A. M. Annaswamy, “A distributed
proximal atomic coordination algorithm,” IEEE Transactions on Auto-
matic Control, 2021. doi: 10.1109/TAC.2021.3053907.
[5] L. Gan, N. Li, U. Topcu, and S. H. Low, “Exact convex relaxation of
optimal power ﬂow in radial networks,” IEEE Transactions on Automatic
Control, vol. 60, no. 1, pp. 72–87, 2014.
[6] B. A. Robbins and A. D. Dom´ınguez-Garc´ıa, “Optimal reactive power
dispatch for voltage regulation in unbalanced distribution systems,” IEEE
Transactions on Power Systems, vol. 31, no. 4, pp. 2903–2913, 2015.
[7] G. P. McCormick, “Computability of global solutions to factorable
nonconvex programs: Part i — convex underestimating problems,”
Mathematical Programming, vol. 10, no. 1, p. 147–175, 1976.
[8] G. Ferro, M. Robba, D. D’Achiardi, R. Haider, and A. M. Annaswamy,
“A distributed approach to the optimal power ﬂow problem for un-
balanced and mesh networks,” IFAC-PapersOnLine, vol. 53, no. 2,
pp. 13287–13292, 2020. 21th IFAC World Congress.
[9] G. Ferro, Competitive and Cooperative Approaches to the Balancing
Market in Distribution Grids.
PhD thesis, Universit`a degli studi di
Genova, 2020.
[10] Y. E. Nesterov, “A method for solving the convex programming problem
with convergence rate o (1/kˆ 2),” in Dokl. akad. nauk Sssr, vol. 269,
pp. 543–547, 1983.
[11] National Renewable Energy Laboratory, “Commercial and residential
hourly load proﬁles for all TMY3 locations in the United States [data
set],” 2014. doi:10.25984/1788456.
[12] D. Olsen, M. Sohn, M. A. Piette, and S. Kiliccote, “Demand response
availability proﬁles for California in the year 2020,” LBNL Report, 2014.
[13] P. M. Tagabe, “The power of community batteries: bringing renewables
to the masses,” Energy Magazine, Aug 2020.
