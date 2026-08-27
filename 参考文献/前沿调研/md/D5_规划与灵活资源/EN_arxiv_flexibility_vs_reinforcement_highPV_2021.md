<!--
source: D5_规划与灵活资源/EN_arxiv_flexibility_vs_reinforcement_highPV_2021.pdf
sha256: 45fda0763b520e4c099f285a3a28ae55757bd156e12e580d0736b045885a3fd2
method: pymupdf
pages: 7
-->

<!-- page 1/7 -->

Distributed ﬂexibility as a cost-effective alternative
to grid reinforcement
Jordan Holweger, Christophe Ballif, Nicolas Wyrsch
Photovoltaics and thin ﬁlm electronics laboratory (PV-LAB)
´Ecole Polytechnique F´ed´erale de Lausanne (EPFL), Institute of Electrical and Micro Engineering (IEM)
Neuchˆatel, Switzerland
{jordan.holweger, christophe.ballif, nicolas.wyrsch}@epﬂ.ch
Abstract—The deployment of distributed photovoltaics (PV) in
low-voltage networks may cause technical issues such as voltage
rises, line ampacity violations, and transformer overloading
for distribution system operators (DSOs). These problems may
induce high grid reinforcement costs. In this work, we assume the
DSO can control each prosumer’s battery and PV system. Under
such assumptions, we evaluate the cost of providing ﬂexibility
and compare it with grid reinforcement costs. Our results
highlight that using distributed ﬂexibility is more proﬁtable than
reinforcing a low-voltage network until the PV generation covers
145% of the network annual energy demand.
Index Terms—PV, ﬂexibility, grid reinforcement cost, battery,
optimal power-ﬂow
I. INTRODUCTION
The fast deployment of distributed photovoltaics (PV)
causes numerous challenges to distribution system operators
(DSOs). The imbalance between local generation and load
can create technical problems in low-voltage grids, such as
line ampacity violations, overvoltage, and transformer over-
loading [1]. A DSO must take countermeasures such as grid
reinforcement (GR) [2], [3]. Alternatively, future distributed
PV systems might provide a signiﬁcant degree of ﬂexibility to
reduce the need for GR. Indeed, battery energy storage systems
(BESSs) [4], inverter reactive power capability [5], [6], [7],
and active power curtailment (APC) are possible solutions to
increase a network’s ﬂexibility and mitigate GR costs [8].
Recent literature demonstrated that BESSs might increase a
network’s PV hosting capacity but are not competitive with
GR [9], [10]. This work compares the GR cost with the cost of
harvesting distributed ﬂexibility, particularly BESS, APC, and
inverter reactive power capabilities for various PV penetration
levels.
II. NOTATION AND BASIC FORMULAS
This section aims to present the basic notation and symbols
used in this paper. This work analyses a low-voltage grid
with connected prosumers with a BESS, which are considered
as static loads or generators injecting active and reactive
power Pi,t, Qi,t at their grid connection points. The active
power consists of the PV generation P PV
i,t , the active power
curtailment P cur
i,t , the BESS’s exchange power P bat
i,t
(positive
when discharging), and the uncontrollable load P load
i,t
. Fig. 1
illustrates the power balance of each prosumer.
Fig. 1. System power balance.
Sets:
• B, L, S sets of buses, lines, and prosumers’ systems (S ⊂
B) respectively.
• Ltr set of transformer branches (pair of bus (ik) with i
the high-voltage bus).
Parameters:
• j = √−1 imaginary number.
• P load
i
uncontrollable active power load at bus i.
• P PV
i
PV generation at bus i.
• Gik, Bik conductance/susceptance on line (ik).
• x, x upper and lower limit for variable x.
• x+, x−positive and negative part of x.
• qmax
r
inverter
reactive
power
capabilities
ratio
(MVAr/MW).
• cimp, cexp import and export tariff (consumer perspec-
tive).
• L, r component lifetime and interest rate to calculate the
annualisation factor R.
Variables:
• P bat
i,t , battery active power (positive when discharging).
• P cur
i,t , PV active power curtailment uncontrollable active
power load at bus i.
• QPV
i,t PV inverter reactive power injection.
• Str
i transformer apparent power.
• Vi,t, Iik,t voltage magnitude at bus i and current in line
(ik) and time t.
• ˆθik,t voltage angle difference between bus i and k at time
t.
22nd Power Systems Computation Conference
PSCC 2022
Porto, Portugal — June 27 – July 1, 2022
arXiv:2109.07305v1  [eess.SY]  15 Sep 2021



<!-- page 2/7 -->

AC load ﬂow equations:
Pi,t =
(
P PV
i,t −P cur
i,t + P bat
i,t −P load
i,t
i ∈S
0
i ∈B −S
(1a)
Qi,t =
(
QPV
i,t
i ∈S
0
i ∈B −S
(1b)
Pi,t = Vi,t
X
k∈B
Vk,t

Gik cos ˆθik,t + Bik sin ˆθik,t

(1c)
Qi,t = Vi,t
X
k∈B
Vk,t

Gik sin ˆθik,t −Bik cos ˆθik,t

(1d)
Iik,t = (Gik + jBik) · (Vi,t −Vk,t)
(1e)
Network operation constraints:
V ≤Vi,t ≤V
∀
i ∈B
(2a)
Iik,t ≤I
∀
(ik) ∈L
(2b)
Str
i = |Vi,t · Iik,t| ≤S
tr
i
∀
(ik) ∈Ltr
(2c)
III. METHODOLOGY
The methodology is based on a sequential approach. First,
following the method described in [11], the BESS’s capacity
Ebat
capand its optimal control trajectory are optimised for each
prosumer with a ﬁxed PV penetration (ﬁxed PV capacity for
each system, P PV
cap). The optimisation problem aims to min-
imise the total cost of ownership of each BESS-PV system (3a)
composed of the sum of the annualised BESS capital cost and
the system operating cost (3b), subject to the power balance
(1a). The operating costs (3b) are the cost of exchanging
energy with the grid under an import and export tariff (from a
prosumer’s perspective) cimp and cexp, respectively. As the PV
capacity is ﬁxed, it does not appear in the objective function.
The term σ (3c) is a regularisation cost whose aim is to
minimise battery usage. The annualisation factor R depends
on the considered lifetime L and interest rate r. More details
about the PV and BESS model can be found in [11].
Second, the load ﬂow problem (1a)-(1e) is solved at each
point in time to calculate the network variable states, Vi,t, Iik,t,
and Str
i . Then, the annualised cost of GR (4a) is calculated
as the sum of the cost of replacing lines (4b) because of line
ampacity violation (4d), and the cost of replacing transformers
due to an apparent power limit violation (4e). The annualisa-
tion factor Rgrid is calculated as in (3d). The cost of replacing
a line is proportional to the line length dl and its speciﬁc cost
per unit of length cline. The cost of replacing a transformer is
simply the product of the transformer cost per unit of capacity
ctrafo and the new maximum apparent power maxt Str
t .
Third, distinct time domains t ∈Πm, m = 1 . . . M are
constructed in which network constraints (2a)-(2c) are not
satisﬁed. These contiguous time steps represent intervention
periods in which the DSO must undertake actions to prevent
violations of network constraints. To model these actions, we
solve an optimal power-ﬂow problem for each period Πm
with the goal of minimizing the PV curtailed energy (5a),
which determines where and when to charge or discharge the
batteries, inject or absorb reactive power (within the inverter
capability, qmax
r
constraints (5c)), and perform APC. Due to
the multi-period nature of this problem, any action altering
the battery state of the charge proﬁle may have consequences
in the future. To prevent such distortion, the BESS’s energy
content at the beginning and end of the intervention period
should match the original energy content from the optimal
control trajectory (5b). We implemented this constraint in the
POWERMODELS [12] library that we used to solve the optimal
power-ﬂow problem. Note that the BESS model is slightly
different in POWERMODELS than in [11]. Typically in the
former implementation, we neglected the active power losses,
did not consider injection impedance, and assumed that the
battery cannot provide reactive power.
Finally, the cost of providing ﬂexibility is deﬁned as the
difference between the operating costs evaluated after solving
(5a) OPEX′
i and the original operating cost OPEXi from
optimal control trajectory (3a). The methodology is graphically
summarised in Fig. 2. We further distinguish the case where
storage is available and can be controlled by the DSO from
the case where no storage is available. In the latter case P bat
is removed from the power balance, and PV curtailment and
reactive power injection are the only options available to the
DSO.
min
Ebat
cap,P batOPEX + σ + R ·
 cbat
F
+ cbat · Ebat
cap

(3a)
OPEX =
T
X
t=1

P −
t · cimp
t
−P +
t · cexp
t

(3b)
σ =
T
X
t=1
P +bat · 10−6
(3c)
R = r · (1 + r)L
(1 + r)L −1
(3d)
Creinf = Rgrid · (Creinf,line + Creinf,trafo)
(4a)
Creinf,line =
X
(l)∈L
δl · cline · dl
(4b)
Creinf,trafo = δtr · ctrafo ·

max
t
Str
t

(4c)
δl =
(
1
if maxt Il,t > Imax
0
otherwise
(4d)
δtr =
(
1
if maxt Str
t > Str,max
0
otherwise
(4e)
min
P cur
i,t ,P bat,QPV
i,t
X
i∈S,t∈Πm
P cur
i,t
(5a)
E′,bat
i,t
= Ebat
i,t
for t =

Πm, Πm
	
i ∈S
(5b)
−qmax
r
· P PV
cap,i ≤QPV
i,t ≤qmax
r
· P PV
cap,i
(5c)
∆OPEX =
X
i
OPEX′
i −OPEXi
(6)
22nd Power Systems Computation Conference
PSCC 2022
Porto, Portugal — June 27 – July 1, 2022



<!-- page 3/7 -->

Start
End
PV scenario s = 1
Solve optimal BESS
capacity and control
trajectory (3a)-(3d)
Solve load ﬂow
equations (1a)-(1e)
Evaluate GR cost (4a)-(4c)
Find set of continuous
intervention periods
t ∈Πm ↔(2a)-(2c) not
satisﬁed m = 1 . . . M
First intervention
period m = 1
Initialize grid exchange
P ′
i,t = Pi,t
∀i, t
Solve optimal power ﬂow
problem (5a) s.t. (1a)-
(1e), (2a)-(2c) and (5b),
update P ′
i,t
∀i, t ∈Πm
m = m + 1
m > M
Evaluate cost of
providing ﬂexibility (6)
s = s + 1
s > S
yes
no
yes
no
Fig. 2. Workﬂow of the methodology.
IV. CASE STUDY
The CIGRE low-voltage network [13], depicted in Fig. 4,
serves as our test case. Loads and PV generation proﬁles
cover one year at 15- min resolution. The load proﬁles come
from an internal load database acquired over several projects
[14], [15]. They have been allocated to each network bus,
minimising the sum of the differences between the CIGRE
loads’ apparent power and the 99th quantile of the internal
load proﬁles. Similarly, the roofs’ characteristics that give the
PV potential capacity are drawn from a building database
from the Swiss building registry1, minimising the sum of the
differences between the annual allocated electricity demand
and the building estimated electricity demand. The annual
energy demand and maximum PV potential capacity for each
prosumer are listed in Table I. The total annual energy demand
and PV capacities are 1050 MWh and 1500 kW, respectively.
Each prosumer’s BESS capacity and control trajectory is
optimised using a time-of-use tariff reported in Table II. The
import rate is 23.92
cts
kWh during peak hours and 15.16
cts
kWh
1https://www.housing-stat.ch/fr/accueil.html
during off-peak hours. The export rate is 8.16
cts
kWh all the
time. The cost of a BESS cbat is assumed to be 182
CHF
kWh,
with a ﬁxed component cbat
F
= 0, as reported in Table III.
The BESS capacities reported in Table I correspond to the
optimised capacities at the maximum PV capacity.
The number of modules giving the maximum potential PV
capacity for each system is scaled by an arbitrary number
(reported in red in Fig. 5) to construct various PV penetration
scenarios. The number of modules is then rounded to the
nearest integer. To prevent an unrealistically small installation,
we assume that if the resulting PV levelised cost of electricity
is greater than a threshold of 23.92
cts
kWh (corresponding to the
high import rate), the resulting PV capacity is set to zero for
this scenario. The PV levelised cost of electricity is calculated
assuming a PV lifetime of 25 years, a discount rate of 3%,
a PV cost of 83 cts
W , and a ﬁxed cost of 10’050 CHF. This
process is graphically summarised in Fig. 3. The PV and
battery capacity indicated in Fig. 4 and Table I corresponds
to the maximum PV penetration scenario (scale = 100%). The
global horizontal and diffuse irradiance data are extracted from
a weather station in Pully 2.
Start
Arbitrary scale 0 < α ≤1
End
nmod: # number
of PV modules
nmod
max: # number of PV
modules corresponding
to maximum PV capacity
nmod = round(α · nmod
max)
Calculate PV levelised cost
of electricity as in [16]
nmod
=
(
nmod
if LCOE ≤cimp
0
otherwise
P PV
cap = nmod · P mod
Fig. 3. Determination of the installed PV capacity for a particular system.
We assumed the costs for GR of the transformer and
lines are 60 kCHF
MVA and 70 kCHF
km . The transformer’s and lines’
lifetime is assumed to be 30 years, as reported in Table III.
V. RESULTS
Fig. 6 illustrates a typical operating day of the maximum PV
penetration scenario. As the total PV generation increases, the
C0-C1 transformer’s apparent power exceeds the rated capac-
ity (transformer loading above 100% in Fig. 6a). Similarly, the
voltage level exceeds 1.05 pu in bus C13. This is caused by an
excess of PV energy, as illustrated in Fig. 6b for the system
2Data available at https://gate.meteoswiss.ch/idaweb
22nd Power Systems Computation Conference
PSCC 2022
Porto, Portugal — June 27 – July 1, 2022



<!-- page 4/7 -->

Fig. 4. Illustration of the CIGRE low-voltage network adapted from [13].
TABLE I
SYSTEMS DATA
Annual demand
PV max capacity
Battery capacity
(MWh)
(kW)
(kWh)
R1
598.97
447.09
141.13
R11
6.09
8.19
2.89
R15
6.13
6.30
2.18
R16
5.58
24.89
2.48
R17
5.29
44.74
2.30
R18
19.82
64.27
4.71
I2
2.88
6.93
1.21
C1
360.34
678.35
87.96
C12
5.89
19.53
1.39
C13
11.73
40.64
4.83
C14
7.02
53.25
3.69
C17
5.84
17.64
2.37
C18
6.56
18.90
3.10
C19
7.34
36.86
2.65
C20
3.59
10.08
1.09
Total
1053.08
1477.69
263.97
TABLE II
TARIFF
Hours
Tariff (cts/kWh)
cimp
Mon-Fri 06h-22h
23.92
Mon-Fri 22h-06h
15.16
Sat-Sun all-day
15.16
cexp
8.16
located in bus C1. To resolve such problems, a signiﬁcant
fraction of the PV energy needs to be curtailed, and the battery
TABLE III
SYSTEM, NETWORK, AND BATTERY PARAMETERS
Param.
Unit
Value
T
-
35040
TS
s
900
L
years
9
r
-
0.03
V , V
pu
0.95-1.05
I
kA
1
Str
kVA
see Fig. 4
ctrafo
kCHF/MVA
60
cline
kCHF/km
70
rgrid
-
0.03
Lgrid
years
30
cbat
CHF/kWh
182
cbat
F
CHF
0
qmax
r
MVAr/MW
0.4
power proﬁle is modiﬁed compared to its original trajectory
(see Fig. 6c for the same system). The corresponding battery
state of charge trajectory is kept untouched except during the
intervention period, as depicted in Fig. 6d.
In the previous example, the intervention period is about
10 hours long. Fig. 7 shows the distribution of the duration
of the intervention periods as well as the total duration of the
interventions. As PV penetration increases, the intervention
duration tends to increase. The total duration of the inter-
ventions increases to about 1300 hours (4 hours per day on
average). No signiﬁcant difference is observed between the
case with storage and the case without storage. Table IV
22nd Power Systems Computation Conference
PSCC 2022
Porto, Portugal — June 27 – July 1, 2022



<!-- page 5/7 -->

reports the number of hours when the transformer experi-
ences overloading and buses experience overvoltage. No line
overloading is observed. Transformer overloading is observed
starting at a PV penetration of 70%. It occurs for 5 hours only.
Bus overvoltage occurs starting at a PV penetration of 119%
and the cumulative time is about 30 hours. The differences
between the case with storage and the case without storage
are insigniﬁcant. These results highlight that, for this network,
the limiting component is the transformer loading. This can
be easily solved by curtailing PV energy.
As reported in Table V, an insigniﬁcant fraction of the total
PV energy needs to be curtailed at a PV penetration of 70%.
At the maximum PV penetration and considering no storage,
8.4% of the 1660 MWh needs to be curtailed. Using storage
reduces this quantity to 2.9%. The amount of curtailed PV
energy impacts the ﬁnancial performance of the systems.
The cost of providing ﬂexibility is reported in Fig. 8.
As it reduces the amount of curtailed PV energy, storage
signiﬁcantly reduces the cost of ﬂexibility. This cost has to
be compared with the GR cost. As no line-overloading is
observed, we perform a sensitivity analysis on the transformer
speciﬁc cost around its nominal value (60 kCHF
MVA ). For an
optimistic case where the transformers cost 12
kCHF
MVA , using
distributed ﬂexibility is proﬁtable up to a PV penetration of
110%. This break-even point moves to 145% for a 60 kCHF
MVA
transformer. Above such a price, it is always proﬁtable to
utilise distributed ﬂexibility for all PV penetrations.
VI. DISCUSSION
The results highlight that distributed ﬂexibility is proﬁtable
over GR for a signiﬁcant range of PV penetrations. Several
underlying assumptions need to be discussed. First, both PV
and storage investment costs are assumed to be undertaken by
the prosumers. We do not tackle the question of the optimal
sizing of BESS and PV systems as in [17] but ﬁx the PV
capacity to generate a realistic PV penetration scenario and
only solve the optimal BESS capacity problem instead. At this
stage, grid support activities like PV curtailment and deviation
of the BESS’s optimal control trajectory are not considered
as future revenue. Thus, we assume that the DSO itself does
0.00
0.25
0.50
0.75
1.00
1.25
1.50
PV penetration (-)
0.0
0.2
0.4
0.6
0.8
1.0
1.2
1.4
1.6
(-)
10%
30%
50%
60%
70%
80%
90%
100%
PV hosting
PV network hosting
0
2
4
6
8
10
12
14
16
Number of PV installations
# inst.
Fig. 5. PV hosting and PV network hosting ratio (left axis) and the number
of installed systems (right axis, maximum is 15 systems). The red dashed
lines are the selected PV penetration scenarios. The numbers indicated in red
are the scale used to vary the PV capacity.
00:00
30-May
03:00 06:00 09:00 12:00 15:00 18:00 21:00
−50
0
50
100
150
200
250
300
350
Trafo C0-C1 loading (%)
Transformer
original
modified
0.975
1.000
1.025
1.050
1.075
1.100
1.125
1.150
1.175
Bus C13 voltage (pu)
Bus voltage
original
modified
(a) Transformer loading level and bus voltage.
grid exchange
load
PV
curtailed power
battery
00:00
04:00
08:00
12:00
16:00
20:00
00:00
2019-05-30
−500
0
500
(b) Original system operation.
00:00
04:00
08:00
12:00
16:00
20:00
00:00
2019-05-30
−500
0
500
 
(c) Modiﬁed system operation.
00:00
04:00
08:00
12:00
16:00
20:00
00:00
2019-05-30
0.0
0.2
0.4
0.6
State of charge (-)
original
modified
(d) State of charge evolution during a day.
Fig. 6. Illustration of the network and one system active power for one day,
for the 100% PV capacity scenario.
0.11 0.39
0.7
0.86 1.02 1.19 1.36 1.58
PV penetration (-)
0.0
2.5
5.0
7.5
10.0
12.5
15.0
Inter. length (h)
Case
w/ storage
w/o storage
0
500
1000
1500
2000
Time (h)
Cumulated time
 (w/ storage)
Fig. 7. Duration distribution (left axis). Averages are indicated with a square
and outliers with a diamond. The total intervention time is on the right axis.
not undertake the risk of investing in distributed storage. This
discards the question of the proﬁtability of BESSs for such a
grid support application as addressed by [9], [10].
A second strong assumption is buried in the BESS’s opti-
mal control trajectory. Such optimisation problems assume a
perfect forecast of the uncontrollable load and PV generation.
22nd Power Systems Computation Conference
PSCC 2022
Porto, Portugal — June 27 – July 1, 2022



<!-- page 6/7 -->

TABLE IV
SUMMARY OF THE NETWORK VIOLATIONS FOR THE CASE WITH STORAGE.
ANY DIFFERENCES BETWEEN THE CASE WITHOUT AND WITH STORAGE
ARE INDICATED BETWEEN BRACKETS.
Transformer overloading
Bus overvoltage
time (h)
max (%)
time (h)
max (pu)
PV penetration
11%
-
-
-
-
39%
-
-
-
-
70%
5
110
-
-
86%
44
134
-
-
102%
173(+2)
158
-
-
119%
523(+7)
186
29(+1)
1.06
136%
799(+5)
215
439(+3)
1.07
158%
1044(+16)
246
846(+6)
1.09
TABLE V
ENERGY CURTAILED AND PV PRODUCTION
Energy curtailed (%)
Generation (MWh)
w/ storage
w/o storage
PV penetration
11%
0.0
0
115
39%
0.0
0.0
409
70%
0.0
0.0
742
86%
0.0
0.1
907
102%
0.0
0.8
1076
119%
0.3
2.6
1253
136%
0.9
5.4
1435
158%
2.9
8.4
1660
0.25
0.50
0.75
1.00
1.25
1.50
PV penetration (-)
0
2
4
6
8
Annualized cost (kCHF/year)
Flexibility w/ storage
Flexibility w/o storage
Transf. 12 kCHF/MVA
Transf. 30 kCHF/MVA
Transf. 60 kCHF/MVA
Transf. 90 kCHF/MVA
Transf. 120 kCHF/MVA
Fig. 8. Annual cost of providing ﬂexibility versus grid reinforcement.
Similarly, the optimal power-ﬂow problem also relies on a
similar assumption. To turn such a concept into practice, there
is a need for dedicated control algorithms that take load and
generation uncertainties into account and that minimise future
impacts on individual system operation.
Third, the costs of providing ﬂexibility and GR are com-
pared by annualising the operating and investment costs. This
implies that the system would operate identically for the
following 30 years without considering the future evolution
of the technology cost and PV deployment. Our approach
must be seen as an evaluation tool to estimate where GR
should be undertaken, typically in networks with a high PV
penetration potential. Future work may repeat such a study
for a wider range of networks with different topologies and
load characteristics and extract insights to better understand
the proﬁtability of distributed ﬂexibility.
Finally, we neglected the additional cost of remote control of
the prosumers. Those costs can be covered by the savings the
DSO makes from using distributed ﬂexibility instead of GR.
From another perspective, those savings could be redistributed
to the prosumers as a reward for contributing to the network
ﬂexibility. As a potential approach, one could deﬁne the
ﬂexibility capacity P ﬂex
cap as the sum of the PV and BESS’s
power capacity (curtailment and charging can be seen as
virtual loads). The difference between the GR and the cost
of ﬂexibility in Fig. 8 corresponds to the DSO’s savings,
which could be redistributed to prosumers according to their
ﬂexibility capacity. The value of the ﬂexibility capacity could
be deﬁned as:
Cﬂex,value = Creinf −∆OPEX
Rgrid
·
1
P
i P ﬂex
cap
(7)
This quantity can be seen as a one-time subsidy to the
prosumer’s system. The value of the ﬂexibility capacity is
reported in Fig. 9. The ﬂexibility capacity value decreases
more signiﬁcantly without storage. For a typical reinforcement
cost of 60
kCHF
MVA , such value lies in 20-30 CHF/kW, which
corresponds to about 5-10% of the 420 CHF/kW Swiss PV
one-time subsidy3.
0.25
0.50
0.75
1.00
1.25
1.50
PV penetration (-)
0
20
40
60
Capacity flexibility value (CHF/kW)
reinf. cost (kCHF/MVA)
12.0
30.0
60.0
90.0
120.0
case
w/ storage
w/o storage
Fig. 9. Flexibility capacity value.
VII. CONCLUSION
This work aims to complement the recent literature on how
to price and reward ﬂexibility. We presented an approach to
assess the cost of distributed ﬂexibility and grid reinforcement
in a low-voltage network for several PV penetration levels.
Our approach starts with optimising the BESS’s capacity
and optimal control trajectory for each prosumer located in
the network. The PV capacity is ﬁxed to control the PV
penetration at the network scale but could be included in
the optimisation problem. The second step is to solve the
load ﬂow equations to evaluate potential violations of net-
work constraints (bus overvoltage, line ampacity violation,
and transformer overloading). At this stage, we evaluate the
cost of grid reinforcement. Then for each continuous period
3Appendix 2.1, ch2.3 of OEnER https://www.fedlex.admin.ch/eli/cc/2017/
766/fr#lvl d1384e202/lvl d1384e203/lvl 2
22nd Power Systems Computation Conference
PSCC 2022
Porto, Portugal — June 27 – July 1, 2022



<!-- page 7/7 -->

when violations of constraints were observed, we solved
an optimisation problem aiming to minimise the amount of
curtailed PV energy. This mimics an action undertaken by the
DSO to keep the network safe. As this action is a deviation of
the prosumers’ optimal control trajectory, the associated cost
overrun is paid to the prosumers. These cost overruns are con-
sidered to be the cost of providing ﬂexibility. We compared the
cost of grid reinforcement and providing ﬂexibility. Distributed
ﬂexibility is more proﬁtable than grid reinforcement when the
need for grid reinforcement arises. We showed that a BESS
signiﬁcantly lowers the cost of providing ﬂexibility compared
to considering only PV curtailment. The BESS’s proﬁtability
is ensured by the deﬁnition of the objective function of
the ﬁrst-stage optimisation, which minimises the prosumer’s
energy bill. Such a scheme transfers the risk of investing in a
BESS from the DSO to the prosumers, assuming a sufﬁcient
incentive, e.g. an electricity tariff, exists to encourage the latter
to invest in such technology. Future work may consider more-
advanced electricity tariffs and evaluate how a DSO could
select the most appropriate tariff to encourage investment in
ﬂexibility capacity and to lower the distributed ﬂexibility cost.
We also discussed a fair approach to reward ﬂexibility as a
one-time contribution to the prosumer’s system. Finally, we
showed that distributed ﬂexibility is more proﬁtable than grid
reinforcement for PV penetration up to 110-145%.
Future work should focus on control algorithms taking
into account load and PV generation uncertainties. Possible
deployment schemes for a practical application should also be
investigated.
REFERENCES
[1] R.
Viral
and
D.
K.
Khatod,
“Optimal
planning
of
distributed
generation
systems
in
distribution
system:
A
review,”
Renewable
and
Sustainable
Energy
Reviews,
vol.
16,
pp.
5146–5165,
2012.
[Online].
Available:
https://ac.els-cdn.com/
S1364032112003498/1-s2.0-S1364032112003498-main.pdf?{ }tid=
1a77bac0-150b-433b-b132-14e5445f007f{&}acdnat=1524565811{ }
0d26ba10fe49eb9777e61ed733dae58b
[2] A. Scheidler, L. Thurner, and M. Braun, “Heuristic optimisation for
automated distribution system planning in network integration studies,”
IET Renewable Power Generation, vol. 12, no. 5, pp. 530–538, mar
2018.
[3] T. Vu, “A stochastic methodology to determine reinforcement cost of
power distribution grid for integrating increasing share of renewable en-
ergies and electric vehicles,” International Conference on the European
Energy Market, EEM, vol. 2018-June, 2018.
[4] N. Hashemipour, T. Niknam, J. Aghaei, H. Farahmand, M. Korpas,
M. Shaﬁe-Khah, G. J. Osorio, and J. P. S. Catalao, “A linear multi-
objective operation model for smart distribution systems coordinating
tap-changers, photovoltaics and battery energy storage,” in 2018 Power
Systems Computation Conference (PSCC).
IEEE, jun 2018.
[5] F. Olivier, P. Aristidou, D. Ernst, and T. Van Cutsem, “Active Man-
agement of Low-Voltage Networks for Mitigating Overvoltages Due to
Photovoltaic Units,” IEEE Transactions on Smart Grid, vol. 7, no. 2,
pp. 926–936, 2016.
[6] F. Olivier, “Solutions for integrating photovoltaic panels into low-voltage
distribution networks,” Ph.D. dissertation, Li`ege Universit´e, 2018.
[7] G. Prionistis, T. Souxes, and C. Vournas, “Voltage stability support of-
fered by active distribution networks,” Electric Power Systems Research,
vol. 190, 2021.
[8] K. Spiliotis, A. I. R. Gutierrez, and R. Belmans, “Demand ﬂexibility ver-
sus physical network expansions in distribution grids,” Applied Energy,
vol. 182, pp. 613–624, nov 2016.
[9] R. Gupta, F. Sossan, and M. Paolone, “Countrywide PV hosting capacity
and energy storage requirements for distribution networks: The case of
switzerland,” Applied Energy, vol. 281, p. 116010, jan 2021.
[10] R. Gupta, A. Pena-Bello, K. N. Streicher, C. Roduner, Y. Farhat,
D. Th¨oni, M. K. Patel, and D. Parra, “Spatial analysis of distribution
grid capacity and costs to enable massive deployment of PV, electric
mobility and electric heating,” Applied Energy, vol. 287, p. 116504, apr
2021.
[11] L. Bloch, J. Holweger, C. Ballif, and N. Wyrsch, “Impact of advanced
electricity tariff structures on the optimal design, operation and prof-
itability of a grid-connected PV system with energy storage,” Energy
Informatics, vol. 2, no. 1, p. 16, 2019.
[12] C. Coffrin, R. Bent, K. Sundar, Y. Ng, and M. Lubin, “Powermodels.jl:
An open-source framework for exploring power ﬂow formulations,” in
2018 Power Systems Computation Conference (PSCC), June 2018, pp.
1–8.
[13] K. Strunz, C. Abbey, C. Andrieu, R. C. Campbell, and R. Fletcher,
“Benchmark Systems for Network Integration of Renewable and Dis-
tributed Energy Resources,” CIGRE, Tech. Rep. July, 2009.
[14] L. Perret, J. Fahrni, N. Wyrsch, Y. Riesen, S. Puddu, S. Weber, and
D. Pfacheco Barzallo, “FLEXI Determining the ﬂexibilization potential
of the electricity demand,” Fedral ofﬁce for energy, Tech. Rep., 2015.
[15] L. Perret, Y. Chevillat, N. Wyrsch, L. Bloch, J. Holweger, S. Weber,
and M. P´eclat, “Flexi 2 D´eterminer le potentiel de ﬂexibilisation de la
demande d’´electricit´e des m´enages,” Fedral ofﬁce for energy, Tech. Rep.,
2019.
[16] C. S. Lai and M. D. McCulloch, “Levelized cost of electricity for solar
photovoltaic and electrical energy storage,” Applied Energy, vol. 190,
pp. 191–203, mar 2017.
[17] J. Holweger, L. Bloch, C. Ballif, and N. Wyrsch, “Mitigating the impact
of distributed PV in a low-voltage grid using electricity tariffs,” Electric
Power Systems Research, vol. 189, p. 106763, 2020. [Online]. Available:
https://www.sciencedirect.com/science/article/pii/S0378779620305666
22nd Power Systems Computation Conference
PSCC 2022
Porto, Portugal — June 27 – July 1, 2022
