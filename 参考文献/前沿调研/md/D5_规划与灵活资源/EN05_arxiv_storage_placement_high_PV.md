<!--
source: D5_规划与灵活资源/EN05_arxiv_storage_placement_high_PV.pdf
sha256: 7f6e8f249de8a6948a704373649ba60dde3aa24ff071b47040f88e1c54f5127d
method: pymupdf
pages: 6
-->

<!-- page 1/6 -->

Storage Placement and Sizing in a Distribution Grid
with high PV-Generation
Benjamin Matthiss, Arghavan Momenifarahani, Jann Binder
Zentrum für Sonnenenergie- und Wasserstoff-Forschung Baden-Württemberg
Stuttgart, Germany
Email: benjamin.matthiss@zsw-bw.de
Abstract—With the increasing penetration of renewable re-
sources in the distribution grid, the demand for alternatives to
grid reinforcement measures rises. One possible solution is the use
of battery systems to balance the power ﬂow at crucial locations
in the grid. Hereby the optimal location and size of the system
has to be determined in regards of investment and grid stabilizing
effect. In this paper the optimal placement and sizing of battery
storage systems for grid stabilization in a small distribution grid
in southern Germany with high PV- penetration is investigated
and compared to a grid heuristical reinforcement strategy.
Keywords—smart grids, power grids, energy storage, batteries,
power supply, renewable energy sources, energy management
I.
INTRODUCTION
Nowadays, the rapid increment penetration of renewable
energy resources into the distribution network can cause in-
creased stress to the distribution system such as overvoltage
situations or the exceeding of line ratings. Furthermore, the
sustained need to establish a balance between energy demand
and supply requires new solutions to enhance the reliable
operation of the power system. Battery energy storage systems
(BESS) are being proposed as a measure to enable the integra-
tion of more renewable energy generation into the distribution
grid without the need for curtailing renewable generations or
reinforcing the grid. The availability of storage also allows to
maximize the energy efﬁciency, decrease the network losses
as well as being able to deliver control or reserve energy to
the grid. In this paper, the optimal placement and sizing of
a battery energy storage system (BESS) for grid relief in a
PV rich distribution grid are investigated. The method used is
based on a linearized load ﬂow method and will be tested with
data from a real distribution grid.
II.
LITERATURE REVIEW
In the above mentioned context, battery storage systems
connected to the distribution grid are the focus of numerous
studies [1–6]. Batteries can be used to reduce distribution
system losses, removing existing hindrances to the integration
of renewable distributed generation, contributing to voltage
and frequency regulation [7, 8], facilitating peak shaving or
decreasing the need of network expansion [9]. However, on
account of the speciﬁc application and operational strategy,
there is a need for an appropriate procedure to size and
site the mentioned systems to minimize the costs and losses
[10]. Additionally, the objective function in different method-
ologies implies considerable variation in outcomes of the
cost-optimized placement and sizing of the BESS. Network
structure, the renewable resource positions, and line-ﬂow limits
can also have impacts on optimal storage placement [11]. The
mathematical techniques to calculate the problem of optimal
siting and sizing the storage, which is in general non-convex
and high dimensional, are classiﬁed into analytic techniques,
artiﬁcial intelligence techniques, classical techniques or other
assorted techniques [10, 12]. Motalleb et al. [13], proposed a
heuristic method to ﬁnd the optimal locations and capacity of
multi-purpose battery energy storage system (BESS) taking ac-
count of distribution and transmission parts. Fossati et al. [14]
found the optimal power capacity of a BESS that minimizes
the operating cost of the microgrid based on genetic methods.
A fuzzy expert system determines the power delivered or
taken from the storage system. The advantage of the proposed
algorithm is its easy adaptation to different types of microgrids.
In [15], the economic optimal allocation of the energy storage
is explored based on net present value using matrix-real-coded
genetic algorithm techniques. The upside of this method is
taking complete and overall design aspects into consideration.
In [16, 17] the articles give a dissertation on how to minimize
the sum of operation cost and to realize the optimal site and
size the BESS based on particle swarm optimization (PSO).
The objective in [18] is to enhance frequency control and
reduce an operating cost by integrating the load shedding
scheme with optimal sizing of BESS. The results depict the
better performance of frequency control based on PSO in
comparison with an analytic algorithm with load shedding
scheme. However, the issue identiﬁed in heuristic methods
is that they require huge calculations, and it is uncertain if
they converge to the global optimal solution. In [10] a second
order cone program (SOCP) convex relaxation of the power
ﬂow equations for optimal sizing and siting of BESS with a
lower computational burden is presented. Hereby the objective
function is formulated in two different manners: minimizing
investment vs. power losses and minimizing investment vs. op-
erational cost beneﬁts in a variable price market. As discussed
in [19] the load and generation balancing of interconnected
renewable resources and energy storage can be controlled
using a dynamic energy price. The problem is formulated in a
stochastic dynamic program over a ﬁnite horizon with the aim
to minimize the long-term average cost of used electricity as
well as investment in storage.
III.
COST ANALYSIS
In this section follows an overview of the costs considered
for battery placement and grid reinforcement. These are im-
arXiv:2001.05814v1  [eess.SY]  16 Jan 2020



<!-- page 2/6 -->

portant to asses the optimal placement and sizing of battery
systems correctly.
A. Levelized Cost of Electricity
Looking at energy costs, the concept of levelized cost
of energy (LCOE) is the center of attention as a signiﬁcant
practical as well as a transparent method for a cost and
efﬁciency analysis which assists to establish a comparison
with respect to costs between each individual alternative for
energy generation. The key concept of LCOE, in a simpliﬁed
manner, is the division of complete lifetime costs consisting
of investments, operations, fuel outlay, local and ﬁnancing
conditions over electricity generation. A progressive research
is conducted to elaborate the substantial attributes of LCOE,
for instance, Fraunhofer ISE in [20] gives a dissertation to the
present and future market evolution of clean resources such
as PV, wind turbines and bio-gas and predicts the regarded
LCOE for different resources till 2035 based on the scenarios
deﬁned for market expansion in Germany. The authors in
[21] carried out research on Mauritius island and put the
generation resources potential and island particular costs under
consideration to ﬁnd out the LCOE of technologies. The LCOE
results from different resources are put into application to
prioritize the energy systems in a cost-effective way. In [22],
the article addresses three different types of PV-systems, and
LCOE enables to obtain a comparison of these types under
Morocco’s climate and helps the decision-making process.
B. Levelized Cost of Energy Storage
The cost of energy storage plays an important role in
economic decision making. In practice, determining a criterion
to compute the storage cost is not easy. Further, in contrast
with energy generation resources, energy storage technologies
are being employed for different services such as a buffer in
a dispatchable generation, peak shaving or to increase self-
consumption. Therefore, the parameters which intervene in
each case are different. An easy cost comparison of storage
technologies is only possible when they are considered in a
common location, application, and type. Battery storage has
the property of being deployed in a distributed fashion. To
determine the investment cost of a battery storage system,
levelized cost of energy storage (LCOES) is measured in euro
per charged kWh and depends on speciﬁc characteristics such
as cycle lifespan, depth of discharge and round trip storage
efﬁciency. The LCOES provides the customer a great insight
into the price per kWh and helps to choose the appropriate
battery by taking economic aspects into account.
The computation of the LCOES follows the deﬁnition of
the LCOE formulation. For instance, in [23, 24], LCOES is
formulated based on LCOE while instead of using fuel cost,
charging cost is utilized and generated electricity is replaced
by discharged electricity.
To estimate the total costs of energy storage placement
correctly it is necessary to split up the costs into the power
dependent and the capacity dependent costs. In [25] the relative
component costs of battery storage systems are examined in
a long-term storage market analysis, performed since 2014.
Hereby, the total costs are split up into the cell costs, the power
electronics, and the peripheral system costs. For residential
systems, the relative costs for the power electronic components
result in 42 % of the total system costs. In this paper, it is
assumed that the power electronics cost rise linearly with the
rated system power of the battery. The estimated LCOES of
the battery system were taken from [26] for the year 2019.
The cost used for the battery placement are shown in Table I.
TABLE I.
BATTERY INSTALLATION COSTS FOR 2019.
type
perc.
costs/value
capacity
42 %
130 e/kWh
periphery
28 %
87 e/kWh
power electronics
30 %
93 e/kW
installation
-
20 000 e/batt
batt. lifetime
-
10 yr
C. Grid Reinforcement Costs
For the speciﬁc expansion costs, the two main shares
for cables and installation costs are taken into account. The
speciﬁc costs for the cables or lines depending on the line
type are displayed in Table II.
However, the amounts for laying the cables vary greatly,
depending on the condition of the ground. For arable land
about 20 000 e/km can be expected, but for stony ground the
amount doubles (40 000 e/km). In urban areas, where roads
have to be rebuilt, the costs raise up to 80 000 e/km [27]. For
the installation of another cable in parallel, it is assumed that
the installation costs increase by about 15 % with each added
line.
For the calculation of the annual costs, the useful lifespan
of the lines still has to be determined. For underground cables,
a lifespan of 40 years are generally assumed [28] and the
normal operating life in accordance with the Electricity Grid
Charges Ordinance is also 40 years [29].
TABLE II.
GRID REINFORCEMENT COSTS.
line type
cost type
costs
0.4 kV, 4 × 50 mm
installation
60 000 e/km
acquisition
3500 e/km
0.4 kV, 4 × 120 mm
installation
60 000 e/km
acquisition
9900 e/km
0.4 kV, 4 × 150 mm
installation
60 000 e/km
acquisition
12 000 e/km
parallel line installation
installation
additional 15%
of installation costs
Trafo, 630 kVA
total
21 000 e
IV.
INPUT DATA AND SCENARIO
In this paper real measurement data (load and irradiation)
from a German distribution grid with high PV penetration is
used to investigate the effects of different storage placements
and grid reinforcement scenarios.
A. PV Generation
To establish a worst case scenario for the grid loading
induced by distributed generation a maximum PV penetration
scenario was created. Hereby the roof area of the buildings as
well as the azimuth and tilt angles were estimated to calculate



<!-- page 3/6 -->

3
6
9
12 15 18 21 24 27 30 33 36 39 42 45 48 51 54 57 60 63 66 69 72 75 78 81 84 87 90 93 96 99 102 105 108 111 114
bus
1.00
1.01
1.02
1.03
1.04
1.05
1.06
voltage [p.u.]
Fig. 1.
Voltage distribution for a day with high solar PV generation and no batter or energy curtailment. The voltage limit is 1.05 p.u., which is clearly passed
get 
: bus with
max voltage violation
Busv
get line segments
from base node to 
Busv
reinforce line
segment
select next segment 
OK 
voltage at  
Busv
violates constraints
reinforced grid
Fig. 2.
Flowchart of the heuristic grid reinforcement algorithm. The method
shown above is repeated for all branches.
the in-plane irradiance. It was assumed that the usable roof
area for PV installations is 80 % share of the total roof area.
With this information and the knowledge about the module size
and type an estimate of the maximum possible PV-capacity
was established which was called PPV, max. To model the PV
generation within the network the Python library PVLIB [30]
was used. This package includes all necessary functions to
model the complete chain from the measured irradiance (GHI,
DNI, DHI) to the inverter AC output power.
B. Simulation Scenario
Because of the computational complexity of the problem
(distribution grid with 106 nodes), it is not possible to optimize
in a single shot over one year. To capture the major grid stress
for the battery placement, a worst case period has been selected
from the measured data. The selected time-span is 3 days long
and shows the highest consecutive net load (generation minus
load) of the whole dataset.
Different simulation scenarios have been created to evalu-
ate the dependency on voltage limitation and PV-penetration.
The selected PV penetrations are 50 % and 80 % relative to
PPV, max. The maximum allowed voltage deviation are 3 % and
5 % from the nominal voltage.
V.
APPROACH
In this section we will brieﬂy describe the methods we used
for the automated grid reinforcement and the battery placement
algorithm. As the speciﬁc goal of the paper is to compare
optimal battery placement with grid reinforcement alternatives
such as curtailment of renewable generation to relax the grid
stress are not taken into account.
A. Grid Reinforcement
The grid reinforcement was calculated with a heuristic ap-
proach. Hereby the critical nodes of each branch are identiﬁed
and the grid is reinforced until the given voltage limits are met
at the corresponding nodes. The procedure of the algorithm is
shown in Fig 2. The algorithm chooses always the cheapest
option for the reinforcement based on the costs shown in
Table II. Hereby it is also evaluated whether it is cheaper to
install multiple smaller lines in parallel or to install a larger
line.
B. Battery Sizing and Placement
The algorithm is based on a linearized loadﬂow method
presented in [31] and the optimization framework which is
used in [32]. The time resolution of the algorithm is 1 hour.
This can be justiﬁed with the properties of the battery system:
The battery capacity is larger than the 1h times the max. rated
power of the battery. Furthermore, the reaction time of the
battery is very fast. Therefore the battery can compensate for
the ﬂuctuations within this hour and the average power over
this time span can be used for the optimization. The simulation
period as mentioned before is three days. Therefore multiple



<!-- page 4/6 -->

3
6
9
12 15 18 21 24 27 30 33 36 39 42 45 48 51 54 57 60 63 66 69 72 75 78 81 84 87 90 93 96 99 102 105 108 111 114
bus
1.00
1.01
1.02
1.03
1.04
1.05
voltage [p.u.]
Fig. 3.
Voltage distribution for a day with high solar PV generation and one installed battery. In this case the voltage limit is obeyed at all nodes. The algorithm
selected a battery placement at bus 65 and 93 to avoid voltage limit violations.
charging cycles are captured. This implies that the possibility
to discharge the battery before the next cycle is ensured by the
algorithm. Otherwise, the optimal size of the battery can not
be calculated correctly.
The optimization places the battery storage units based on
the costs shown in Table I and at the same time calculates
an optimized charge trajectory for the batteries. Furthermore,
constraints can be included, e.g. the number of batteries the
algorithm is allowed to place.
This can be shown by an example calculation: In Fig. 1
the voltage situation within the grid is shown for a day with
high solar PV generation and without an installed battery nor
curtailment of PV-generation. The voltage limit within the
grid is 1.05 p.u., which is surpassed in two branches here.
In Fig. 3 the result of the optimization allowing one battery
and curtailment is shown: The voltage limits are obeyed at all
times. The algorithm chose to place the battery at bus 65 with
a size of 83 kWh. The size is determined with the help of the
provided irradiation and load proﬁles.
VI.
RESULTS
In this section, the results of the above-mentioned al-
gorithms in the given simulation scenario are shown and
evaluated.
A. Grid Reinforcement
The grid reinforcement algorithm has shown to be com-
putationally effective and at the same time sufﬁcient to fulﬁll
the task of calculating a cost-effective grid reinforcement. As
it is a heuristic algorithm, the global optimality of the solution
cannot be guaranteed. For radial distribution grids although a
high-quality solution can be assumed. In Fig. 5 a comparison
of the bus voltages of the original grid and the reinforced one
is displayed. It can be seen that the algorithm added additional
elements to reinforce the grid until the voltage limits are met at
all nodes. The resulting reinforcement is shown in Fig. 4. The
red edges of the graph indicate the reinforced line segments.
Only the line segments with voltage problems were reinforced,
in this case, three out of four branches.
Fig. 4.
Graph diagram of the reinforced grid. The yellow node indicates
the transformer and all the blue nodes are busses. The red edges indicate
reinforced line segments.
TABLE III.
EXAMPLE RESULT OF THE GRID REINFORCEMENT
ALGORITHM: OVERVIEW OF THE INSTALLED ASSETS AND COSTS
from bus
to bus
n parallel
type
cost [kC]
1
105
2
NAYY 4 × 120 SE
109.50
1
73
2
NAYY 4 × 120 SE
109.50
1
106
3
NAYY 4 × 120 SE
131.10
2
28
1
NAYY 4 × 120 SE
87.90
2
104
2
NAYY 4 × 120 SE
109.50
3
61
1
NAYY 4 × 120 SE
87.90
3
73
2
NAYY 4 × 120 SE
109.50
6
43
1
NAYY 4 × 50 SE
81.50
6
68
2
NAYY 4 × 120 SE
109.50
28
29
1
NAYY 4 × 50 SE
81.50
29
30
1
NAYY 4 × 50 SE
81.50
50
57
1
NAYY 4 × 120 SE
87.90
50
61
1
NAYY 4 × 120 SE
87.90
56
57
1
NAYY 4 × 120 SE
87.90
63
70
2
NAYY 4 × 120 SE
109.50
63
69
2
NAYY 4 × 120 SE
109.50
65
70
2
NAYY 4 × 120 SE
109.50
65
106
1
NAYY 4 × 120 SE
87.90
68
100
2
NAYY 4 × 120 SE
109.50
69
100
2
NAYY 4 × 120 SE
109.50
104
105
2
NAYY 4 × 120 SE
109.50



<!-- page 5/6 -->

0
20
40
60
80
100
bus #
1.00
1.01
1.02
1.03
1.04
1.05
1.06
voltage [p.u.]
original
reinforced
Fig. 5.
Voltage comparison of the original and the reinforced grid. In this
case a voltage limit of 1.03 p.u. was used.
The selection of the line types depends on the amount of
reinforcement needed to meet the voltage constraints. In this
example, the algorithm chose to use 18 times a cable of the
type NAYY 4 × 120 SE and three times the smaller NAYY
4 × 50 SE (see Table III). As the transformer loading was still
within the limits it was not replaced or reinforced.
B. Battery Placement
The results of the battery placement are summed up in
Table IV for the different scenarios. For the scenario of a 50 %
penetration and a maximum voltage deviation of 5 % relative to
Vnom no battery placement is needed. If the maximum voltage
deviation is decreased to 3 %, 2 batteries have to be placed.
For the scenario with 80 % PV penetration a maximum voltage
deviation of 5 % relative to Vnom, the locations of the batteries
stay almost the same as before, but the sizes increase. If the
maximum voltage deviation is decreased to 3 % in this case,
a third battery has to be added. The results are additionally
shown in Fig. 6 and Fig. 7. Here the placements for the 80 %
PV penetration and both voltage limitations are shown in a
graph.
TABLE IV.
LOCATION AND SIZE OF THE BATTERY
PV pen.
∆Vmax
batt. 1
batt. 2
batt. 3
[PPV, max]
[Vnom]
C [kWh]
bus #
C [kWh]
bus #
C [kWh]
bus #
50 %
5 %
-
-
-
-
-
-
3 %
57
30
120
42
-
-
80 %
5 %
68
30
149
43
-
-
3 %
497
29
426
45
116
59
In all cases the placement of the battery stays almost the
same but varies just slightly by one or two buses. This indicates
that the solution surface is relatively ﬂat with respect to the
battery position in the grid.
C. Comparison
In this section, the results of the battery placement and the
grid reinforcement algorithm will be compared. In contrast to
the previous section (VI-B) some constraint on the number
of batteries to place are added to investigate the sensitivity
on the number of batteries installed. Therefore two additional
scenarios are introduced: one where the number of batteries is
ﬁxed to 5 and one with 10 batteries.
Fig. 6.
Battery placement for a PV penetration of 50 % PPV, max and a
maximum voltage deviation of 3 %.
Fig. 7.
Battery placement for a PV penetration of 80 % PPV, max and a
maximum voltage deviation of 3 %.
The results regarding the absolute investment costs are
shown in Table V. The cheapest solution for the given scenarios
is the installation of batteries to maintain the grid voltage sta-
bility. The costs increase with additional batteries, although the
individual size of the batteries decreases. The most expensive
option regarding the investment costs is grid reinforcement.
A more interesting comparison is the yearly costs. In this
case, the maintenance costs for the battery as well as the
grid are neglected, as they vary greatly. As mentioned before,
the lifetime for the battery is assumed to be 10 yr and the
lifetime for the cables 40 yr. The results of this comparison
are shown in Table VI. The result is similar to the investment
costs, although the difference between the battery placement
and the grid reinforcement is less pronounced.
TABLE V.
INVESTMENT COST COMPARISON
PV pen.
∆Vmax
grid reinf.
5 batt.
10 batt.
unconstr.
[PPV, max]
[Vnom]
[ke]
[ke]
[ke]
[ke]
[n batt.]
50 %
3%
710
113
163
83
2
5%
-
-
-
-
-
80 %
3%
1679
290
340
287
3
5%
488
104
154
74
2



<!-- page 6/6 -->

TABLE VI.
YEARLY COST COMPARISON (ASSUMED LIFETIME:
BATTERY=10 YR, CABLE=40 YR)
PV pen.
∆Vmax
grid reinf.
5 batt.
10 batt.
unconstr.
[PPV, max]
[Vnom]
[ke]
[ke]
[ke]
[ke]
[n batt.]
50%
3%
18
11
16
8
2
5%
0
0
0
0
0
80%
3%
42
29
34
29
3
5%
12
10
15
7
2
VII.
CONCLUSION AND OUTLOOK
In this paper, we presented two algorithms: one for the
automated placement and sizing of battery storage systems
within a distribution grid and another algorithm for automated
grid reinforcements. Both algorithms have shown to work and
fulﬁll their task and avoid grid overloading for the suggested
implementations. These algorithms can now be used to evalu-
ate the possible solutions for distribution grids with congestion
problems.
The results presented in this paper are only valid for
the given scenario. However, the algorithm is capable of
incorporating additional congestion management options such
as the curtailment of renewable generation, load shifting, etc.
These possibilities will be elaborated in a following paper.
REFERENCES
[1]
B. Dunn, H. Kamath, and J.-M. Tarascon, “Electrical energy storage for
the grid: A battery of choices,” Science, vol. 334, no. 6058, pp. 928–
935, Nov. 18, 2011.
[2]
K. Divya and J. Østergaard, “Battery energy storage technology
for power systems—an overview,” Electric Power Systems Research,
vol. 79, no. 4, pp. 511–520, Apr. 2009.
[3]
M. Beaudin, H. Zareipour, A. Schellenberglabe, and W. Rosehart,
“Energy storage for mitigating the variability of renewable electricity
sources: An updated review,” Energy for Sustainable Development,
vol. 14, no. 4, pp. 302–314, Dec. 2010.
[4]
B. S. Dunn, H. Kamath, and J.-M. Tarascon, “Electrical energy storage
for the grid: A battery of choices.” Science, vol. 334 6058, pp. 928–35,
2011.
[5]
H. L. Ferreira, R. Garde, G. Fulli, W. Kling, and J. P. Lopes,
“Characterisation of electrical energy storage technologies,” Energy,
vol. 53, pp. 288–298, May 2013.
[6]
C. Mateo, Á. Sánchez, P. Frías, A. Rodriguez-Calvo, and J. Reneses,
“Cost–beneﬁt analysis of battery storage in medium-voltage distribu-
tion networks,” IET Generation, Transmission & Distribution, vol. 10,
no. 3, pp. 815–821, Feb. 18, 2016.
[7]
A. Oudalov, D. Chartouni, and C. Ohler, “Optimizing a battery energy
storage system for primary frequency control,” IEEE Transactions on
Power Systems, vol. 22, no. 3, pp. 1259–1266, Aug. 2007.
[8]
S. Aditya and D. Das, “Battery energy storage for load frequency
control of an interconnected power system,” Electric Power Systems
Research, vol. 58, no. 3, pp. 179–185, Jul. 2001.
[9]
P. Lazzeroni and M. Repetto, “Optimal planning of battery systems for
power losses reduction in distribution grids,” Electric Power Systems
Research, vol. 167, pp. 94–112, Feb. 2019.
[10]
E. Grover-Silva, R. Girard, and G. Kariniotakis, “Optimal sizing and
placement of distribution grid connected battery systems through an
SOCP optimal power ﬂow algorithm,” Applied Energy, vol. 219,
pp. 385–393, Jun. 2018.
[11]
S. Bose, D. F. Gayme, U. Topcu, and K. M. Chandy, “Optimal
placement of energy storage in the grid,” in 2012 IEEE 51st IEEE
Conference on Decision and Control (CDC), Maui, HI, USA: IEEE,
Dec. 2012, pp. 5605–5612.
[12]
P. Prakash and D. K. Khatod, “Optimal sizing and siting techniques
for distributed generation in distribution systems: A review,” Renewable
and Sustainable Energy Reviews, vol. 57, pp. 111–130, May 2016.
[13]
M. Motalleb, E. Reihani, and R. Ghorbani, “Optimal placement and siz-
ing of the storage supporting transmission and distribution networks,”
Renewable Energy, vol. 94, pp. 651–659, Aug. 2016.
[14]
J. P. Fossati, A. Galarza, A. Martín-Villate, and L. Fontán, “A method
for optimal sizing energy storage systems for microgrids,” Renewable
Energy, vol. 77, pp. 539–549, May 2015.
[15]
C. Chen, S. Duan, T. Cai, B. Liu, and G. Hu, “Optimal allocation
and economic analysis of energy storage system in microgrids,” IEEE
Transactions on Power Electronics, vol. 26, no. 10, pp. 2762–2773,
Oct. 2011.
[16]
A. Arabali, M. Ghofrani, and M. Etezadi-Amoli, “Cost analysis of
a power system using probabilistic optimal power ﬂow with energy
storage integration and wind generation,” International Journal of
Electrical Power & Energy Systems, vol. 53, pp. 832–841, Dec. 2013.
[17]
A. Ahmadian, M. Sedghi, M. Aliakbar-Golkar, A. Elkamel, and M.
Fowler, “Optimal probabilistic based storage planning in tap-changer
equipped distribution network including PEVs, capacitor banks and
WDGs: A case study for iran,” Energy, vol. 112, pp. 984–997, Oct.
2016.
[18]
T. Kerdphol, Y. Qudaih, and Y. Mitani, “Battery energy storage system
size optimization in microgrid using particle swarm optimization,”
in IEEE PES Innovative Smart Grid Technologies, Europe, Istanbul,
Turkey: IEEE, Oct. 2014, pp. 1–6.
[19]
P. Harsha and M. Dahleh, “Optimal management and sizing of energy
storage under dynamic pricing for the efﬁcient integration of renewable
energy,” IEEE Transactions on Power Systems, vol. 30, no. 3, pp. 1164–
1181, May 2015.
[20]
C. Kost and T. Schlegl, “Levelized cost of electricity- renewable energy
technologies,” Fraunhofer ISE, Mar. 2018.
[21]
R. P. Shea and Y. K. Ramgolam, “Applied levelized cost of electricity
for energy technologies in a small island developing state: A case study
in mauritius,” Renewable Energy, vol. 132, pp. 1415–1424, Mar. 2019.
[22]
A. Allouhi, R. Saadani, M. Buker, T. Kousksou, A. Jamil, and M.
Rahmoune, “Energetic, economic and environmental (3e) analyses and
LCOE estimation of three technologies of PV grid-connected systems
under different climates,” Solar Energy, vol. 178, pp. 25–36, Jan. 2019.
[23]
I. Pawel, “The cost of storage – how to calculate the levelized
cost of stored energy (LCOE) and applications to renewable energy
generation,” Energy Procedia, vol. 46, pp. 68–77, 2014.
[24]
A. Belderbos, E. Delarue, and W. D’haeseleer, Calculating the levelized
cost of electricity storage? eng, 2016.
[25]
M. Müller, L. Viernstein, C. N. Truong, A. Eiting, H. C. Hesse, R.
Witzmann, and A. Jossen, “Evaluation of grid-level adaptability for
stationary battery energy storage system applications in Europe,” en,
Journal of Energy Storage, vol. 9, pp. 1–11, Feb. 2017.
[26]
V. Bansal, “Building A Bankable Solar + Energy Storage Project,” en,
p. 7, 2019.
[27]
L. Rupp, M. Brunner, and S. Tenbohlen, “Einﬂuss dezentraler
Wärmepumpen auf die Netzausbaukosten des Niederspannungsnetzes,”
de, Jan. 2015.
[28]
Hofman and Oswald, “Vergleich Erdkabel – Freileitung im 110-kV-
Hochspannungsbereich,” Tech. Rep., 2010.
[29]
K. Heuck, K.-D. Dettmann, and D. Schulz, Elektrische Energiever-
sorgung Erzeugung, Übertragung und Verteilung elektrischer Energie
für Studium und Praxis, German. Wiesbaden: Vieweg+Teubner, 2010,
OCLC: 1015863663.
[30]
W. F. Holmgren, C. W. Hansen, and M. A. Mikofski, “Pvlib python: A
python package for modeling solar energy systems,” Journal of Open
Source Software, vol. 3, no. 29, p. 884, Sep. 2018.
[31]
B. Matthiss, M. Kraft, and J. Binder, “Fast Probabilistic Load Flow
for Non-Radial Distribution Grids,” in 2018 IEEE International Con-
ference on Environment and Electrical Engineering and 2018 IEEE
Industrial and Commercial Power Systems Europe (EEEIC / I CPS
Europe), Jun. 2018, pp. 1–6.
[32]
B. Matthiss, A. Momenifarahani, K. Ohnmeiss, and M. Felder, “In-
ﬂuence of Demand and Generation Uncertainty on the Operational
Efﬁciency of Smart Grids,” Dec. 5, 2018. arXiv: 1812.01886 [cs].
