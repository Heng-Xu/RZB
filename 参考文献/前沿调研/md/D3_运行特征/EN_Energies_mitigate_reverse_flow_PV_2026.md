<!--
source: D3_运行特征/EN_Energies_mitigate_reverse_flow_PV_2026.pdf
sha256: b708bcb1ea93704a38080e40790421358c8e828118ee86a0b1f981741af50754
method: pymupdf
pages: 24
-->

<!-- page 1/24 -->

Academic Editor: José Matas
Received: 28 January 2026
Revised: 11 February 2026
Accepted: 17 February 2026
Published: 19 February 2026
Copyright: © 2026 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license.
Article
Strategies to Mitigate Reverse Power Flow in Distribution
Networks with High Penetration of Solar Photovoltaic Generation
Ivan Santos Pereira 1
, Gustavo da Costa Vergara 1
, Jesús M. López-Lezama 2
, Nicolás Muñoz-Galenao 2
and Lina Paola Garcés Negrete 1,*
1
Electrical, Mechanical and Computer Engineering School, Federal University of Goiás (UFG),
Av. Universitária No. 1488, Goiânia 74605-010, Brazil; ivan.santos@discente.ufg.br (I.S.P.);
gustavo.vergara@discente.ufg.br (G.d.C.V.)
2
Research Group in Efficient Energy Management (GIMEL), Departamento de Ingeniería Eléctrica,
Universidad de Antioquia, Calle 67 No. 56-108, Medellin 050010, Colombia;
jmaria.lopez@udea.edu.co (J.M.L.-L.); nicolas.munoz@udea.edu.co (N.M.-G.)
*
Correspondence: lina_negrete@ufg.br
Abstract
The power industry has undergone significant recent changes due to the growing demand
for a cleaner and more sustainable energy mix. In this context, the Brazilian government
began encouraging distributed generation (DG), making photovoltaic generation a strong
trend in the country. However, the expansion of DG may cause negative impacts on the
grid, such as reverse power flow (RPF) and overvoltages, which motivates research aimed
at mitigating these effects. This study proposes strategies to mitigate RPF in distribution
networks with high penetration of photovoltaic generation and evaluates their impacts
on the electrical system. Three strategies were analyzed: a battery energy storage system
(BESS), a control mechanism using a Grid Zero inverter, and PV Curtailment. The strategies
were implemented in OpenDSS on a real distribution network located in São Paulo, Brazil.
The assessment involved analyzing power flow in critical transformers and at the substation,
as well as monitoring bus voltages and network energy losses. The quantitative results
demonstrate that BESS allocation was the superior strategy, reducing technical losses by
61.3% and fully mitigating reverse power flow under steady-state conditions. The Grid
Zero inverter eliminated power injection into the grid; however, it increased substation
dependency by 59% compared to the baseline scenario. PV curtailment, although achieving
the smallest reduction in RPF, proved to be the most effective technique for power quality,
limiting the average voltage rise to 0.7%.
Keywords: reverse power flow; photovoltaic solar generation; OpenDSS; electric power
distribution networks; simulation
1. Introduction
The energy transition stands among the most significant trends in today’s power
sector. The formulation of the Sustainable Development Goals (SDGs) by the United
Nations underscores the global concern of sustainability, understood as the ability to
meet present needs without compromising those of future generations. Among the goals
established to promote sustainability, SDG 7 is particularly notable, as it aims to ensure
universal access to clean and renewable energy [1]. The fundamental principle is that a
sustainable society must be able to meet its energy demands through sources that do not
harm the environment or intensify climate change. As a result, governments around the
Energies 2026, 19, 1069
https://doi.org/10.3390/en19041069



<!-- page 2/24 -->

Energies 2026, 19, 1069
2 of 24
world have come under pressure from society to encourage the adoption of clean and
renewable energy sources.
Electricity generation in Brazil is predominantly based on renewable sources, as shown
in Table 1 [2]. This profile is largely attributable to long-standing public policies that have
promoted renewable energy development, reinforcing the country’s historical dependence
on hydropower while enabling the expansion of other renewable technologies, including
wind, solar, and biomass. Within this framework, and as part of broader strategies to
increase the share of sustainable sources in the national energy mix and to accelerate the
energy transition with private-sector involvement, the Brazilian government established a
regulatory framework for distributed generation (DG). This process began in 2012 with
Resolution No. 482 issued by the Brazilian National Electric Energy Agency (ANEEL) and
was later consolidated through the Legal Framework for Distributed Generation, enacted
in 2022 [3,4].
Table 1. Electricity generation sources in Brazil.
Generation Source
Participation (%)
Installed Capacity (MW)
Hydropower
42.6
110,238
Solar Photovoltaic
24.1
62,388
Wind
13.3
34,473
Natural Gas
7.7
19,869
Biomass and Biogas
7.0
18,022
Oil and Other Fossil Fuels
3.0
7832
Coal
1.5
3951
Nuclear
0.8
1990
Importation
3.2
8170
The attractiveness of the partial energy credit compensation system, which allows
consumers to offset their electricity bills by injecting surplus generation in the distribution
system, has driven the growth of solar photovoltaic generation, which currently predom-
inates among DG systems in Brazil. According to data from the Brazilian Photovoltaic
Solar Energy Association (ABSOLAR), between 2021 and October 2025, the installed ca-
pacity of solar photovoltaic power increased from 14,415 MW to 62,388 MW, representing
a growth of 330.6% in only four years [5]. Of this total, approximately 68% comes from
DG, which further highlights the relevance of this sector [6]. Unfortunately, the increasing
penetration of solar photovoltaic generation into the power grid may also lead to significant
technical challenges for electricity utilities. The occurrence of the so-called “duck curve”, a
phenomenon in which a period of low demand coincides with the peak generation of pho-
tovoltaic plants, is frequent in industrial environments with large distributed generation
systems and in power networks with high levels of solar energy penetration [7].
The reversal of power flow—occurring when DG units inject electricity into the dis-
tribution system as their production exceeds local demand—can lead to several technical
challenges, including bus overvoltage and transformer overloading, thereby jeopardizing
the safe and efficient operation of the electrical network [8–10].
The interest in harnessing the benefits provided by DG, together with the need to miti-
gate the adverse effects it may cause, has motivated numerous studies aimed at attenuating
reverse power flow (RPF), mitigating voltage rise issues, and improving reliability [11–13].
In the specialized literature, several studies can be found that propose strategies to mini-
mize these technical impacts. The authors of [14] showed that the optimized allocation of
BESS can effectively reduce energy losses across several benchmark distribution test sys-
tems, while simultaneously limiting RPF in distribution networks. In this case, the authors
also implement reactive control (RC); nonetheless, smart inverters (SIs) were not considered.
https://doi.org/10.3390/en19041069



<!-- page 3/24 -->

Energies 2026, 19, 1069
3 of 24
In [15], the authors propose several strategies to mitigate overvoltages in a benchmark
distribution network with high photovoltaic penetration. Among these, two strategies
are shown to be effective in both controlling overvoltages and mitigating reverse power
flows: battery-based self-consumption and PV curtailment. In [16], several technologies
aimed at mitigating RPF in distribution systems are analyzed, including SIs and BESS. The
study concludes that these devices can enhance the electrical system and reduce impacts on
centralized resources, although their implementation requires significant structural modifi-
cations. The study focuses on the integration of Distributed Energy Resources (DERs) in
distribution networks; however, it does not present real-world applications and is limited
to a purely theoretical analysis.
In [17], the authors propose an approach for the optimal siting and sizing of a BESS to
mitigate RPF in a PV power plant connected to a real distribution system in Thailand. The
analysis is divided into three scenarios, each considering a different PV plant capacity. The
results show that the proposed BESS configuration effectively reduces RPF, enhances the
smoothing of the distribution load curve, and contributes to both energy loss reduction
and lower peak power demand. In [18], the authors analyze RPF caused by solar PV
integration in low-voltage network branches of a real distribution system in Ghana. Using
predictive models derived from simulation data, they estimate average levels of RPF and
line overloading at maximum PV penetration. The results further indicate that total branch
losses are minimized when PV penetration reaches its highest level. A hybrid algorithm
is proposed in [19] to monitor RPF caused by DERs in benchmark IEEE test systems. The
proposed approach combines an impedance-based method with a power balance index.
Flexible AC power flow control is proposed in [20] to mitigate RPF in distribution networks
with PV generation and BESS. The authors evaluate the proposed approach through a series
of tests conducted on a real radial distribution system derived from the electricity networks
of New South Wales, Australia. An approach to identify possible scenarios of RPF and
feasible solutions are proposed in [21]. In this case, the authors present their results using a
benchmark IEEE test system instead of a real distribution system.
Studies that assess the impacts of photovoltaic systems and propose strategies to
mitigate the adverse effects of RPF are essential for providing technical guidance to utilities
in monitoring distribution networks and preventing potential damage. As highlighted in
the literature review, most of these studies are conducted using benchmark distribution
systems. While this ensures result reproducibility due to data availability, it also limits
the demonstration of the real-world applicability of many proposed approaches. Table 2
summarizes the main features of previous studies on RPF in distribution systems, as well
as the mitigation strategies adopted, where PVC denotes photovoltaic curtailment. Note
that the proposed approach stands out for considering not only a real distribution system
but also real irradiance data. Furthermore, three different strategies are implemented to
mitigate RPF. The first strategy involves allocating BESS at the buses of the generating units,
allowing them to absorb surplus energy during periods of excess generation and discharge
it to supply consumers when demand exceeds generation. This control can be implemented
in a straightforward manner through electronic inverters in current photovoltaic systems.
The second strategy consists of directly blocking the injection of energy into the grid
through inverters that monitor the power flow at the bus and are designed to prevent flow
reversal, equipment commonly employed in Grid Zero systems. Finally, the third strategy
involves dynamically limiting the rated power of photovoltaic modules through a control
implemented in an inverter that uses the bus voltage as a reference signal.
https://doi.org/10.3390/en19041069



<!-- page 4/24 -->

Energies 2026, 19, 1069
4 of 24
Table 2. Comparison of reviewed studies to mitigate RPF in distribution systems.
Ref
Real System
Real Irradiance Data
Strategies
Yes
No
Yes
No
BESS
SI
PVC
RC
[14]
x
x
x
x
[15]
x
x
x
x
[16]
x
x
x
[17]
x
x
x
[18]
x
x
x
[19]
x
x
x
[20]
x
x
x
x
[21]
x
x
x
This Study
x
x
x
x
x
All simulations were carried out using OpenDSS, developed by the Electric Power
Research Institute (EPRI) [22]. The tests were applied to a distribution network in the state
of São Paulo over a two-day period, using real solar irradiance data for the modeling of
photovoltaic modules and the definition of their operating conditions.
To summarize, the main features and contributions of this research are as follows:
•
The proposed approach leverages Geographic Information System (GIS) georeferenc-
ing to collect real solar irradiance data and is validated using a real distribution system
to assess its effectiveness in mitigating RPF.
•
Three different strategies for mitigating reverse power flow are implemented and
compared, namely the use of BESS, smart inverters, and photovoltaic curtailment.
•
All simulations are carried out using OpenDSS, a free and open-source software that
enables the modeling and analysis of distribution networks, ensuring accessibility and
reproducibility of the results for the scientific community.
2. Materials and Methods
The methodology of this work initially comprises the description of the technical data
of the network used in the simulations, including the definition of photovoltaic module
parameters and the criteria for selecting the buses for their installation. Subsequently, the
process of extracting, processing, and georeferencing irradiance data is detailed, which
serve as input variables for the modeling of photovoltaic modules. Finally, the three case
studies adopted are presented, detailing their implementation in the software and the
expected results.
The electrical network data were imported into Python 3.11.9 to generate the OpenDSS
version 10.1.0.1 scripts with their corresponding parameters. Using the geographic coordi-
nates of each network bus, the buses were associated with grid cells. The irradiance data
acquisition process consisted of creating equidistant points spaced at 500 m covering the
feeder area, for which irradiance data were downloaded. These data were then processed
in Python, linked to the corresponding grid cell of each point, and used to compute both
the overall average and the hourly average irradiance values for each bus.
2.1. Network Data and System Modeling with Distributed Generation
The distribution network used is a real and simplified system of a feeder circuit in
the state of São Paulo. This electrical network comprises 2932 buses interconnected by
2622 distribution line segments, 335 step-down transformers, and 333 loads. The system is
three-phase, unbalanced, and operates at medium voltage (13.8 kV) and low voltage (380 V
phase-to-phase or 220 V phase-to-ground). To ensure reproducibility, all the information
used in the research is available in [23].
https://doi.org/10.3390/en19041069



<!-- page 5/24 -->

Energies 2026, 19, 1069
5 of 24
2.1.1. Line Segments
The distribution line segments interconnect the buses of the electrical system and
operate at both voltage levels of the network. The information related to these lines is
presented in Table 3. In this case, the first column indicates the label of the line segments as
provided by the utility. In addition to this information, the original database also includes
conductances (G0 and G1) and susceptances (B0 and B1), both expressed in µS.
Table 3. Distribution Line Segments.
Line
Phase
Origin Bus
Destination Bus
Length (m)
R0 (Ω)
R1 (Ω)
2964
ABC
2963
2964
48.21
0.096
0.074
2965
ABC
2964
2965
27.46
0.054
0.042
2966
ABC
2965
2966
435.71
0.043
0.026
2967
ABC
2966
2967
37.07
0.045
0.027
2968
ABC
2967
2968
35.43
0.043
0.025
2969
ABC
2968
2969
36.55
0.044
0.026
2970
ABC
2969
2970
35.22
0.043
0.025
2971
ABC
2970
2971
33.26
0.040
0.024
...
...
...
...
...
...
...
2.1.2. Loads
The load data were organized according to the standard of Table 4. The parameters
considered relevant for modeling in OpenDSS include nominal voltage, number of phases,
apparent, active, and reactive power, as well as the power factor. The power values reported
for the loads correspond to the maximum values for each load and were obtained from the
local electric utility. Most loads in the network are three-phase, although single-phase loads
are also present. All loads operate at low voltage: three-phase loads at 380 V and single-
phase loads at 220 V. In addition, load curves were assigned to the consumption points
to enable the visualization of energy consumption variations throughout the day. These
curves were modeled using three typical profiles (residential, commercial, and industrial),
based on the study presented in [24], representing different types of consumers. The curves,
illustrated in Figure 1, were randomly distributed among the loads of the network.
Table 4. Load Data.
Node
Phase
kVA
kW
kvar
PF (%)
2400
ABC
21.09
18.65
9.96
88.21
2406
ABC
18.49
16.38
8.75
88.21
2424
ABC
16.28
14.39
7.68
88.21
2438
ABC
43.54
38.48
20.55
88.21
2448
A
31.35
27.65
14.89
88.05
2452
ABC
55.38
48.97
26.15
88.21
2454
ABC
16.01
14.17
7.57
88.21
2472
ABC
28.49
25.25
13.49
88.21
2481
ABC
23.82
21.05
11.24
88.21
2518
A
0.42
0.37
0.20
88.05
2522
A
0.50
0.44
0.23
88.05
2531
A
1.30
1.15
0.62
88.05
2539
A
1.61
1.42
0.76
88.05
2544
A
0.10
0.09
0.05
88.05
...
...
...
...
...
...
https://doi.org/10.3390/en19041069



<!-- page 6/24 -->

Energies 2026, 19, 1069
6 of 24
Figure 1. Load Curves.
It is important to note that the distribution network used in the study is a simpli-
fied model, which implies that each load does not represent an individual consumer, but
an aggregate consumption point connected to the secondary side of a step-down trans-
former. Therefore, no explicit power limits were considered for low voltage loads in the
modeling framework.
2.1.3. Transformers
All distribution transformers in the network are step-down units, reducing the
medium-voltage level (13.8 kV) to either 380 V or 220 V. Transformers that step down
to 380 V are three-phase, while those that step down to 220 V are single-phase. All trans-
formers are connected in a delta–wye configuration and exhibit typical apparent power
ratings ranging from 5 kVA to 300 kVA. Table 5 shows the format of the data used. In
addition to the listed information, the original database also provides the positive-sequence
impedance in per unit (p.u.).
Table 5. Presentation of Transformer Data.
From Bus
To Bus
Phase
kVA
Primary (kVLL)
Secondary
(kVLL)
Connection
68
69
B
15
13.8
0.22
D-Yg
73
74
ABC
112
13.8
0.38
D-Yg
59
76
ABC
112
13.8
0.38
D-Yg
...
...
...
...
...
...
...
2.1.4. PVSystem
The photovoltaic modules were installed at the 90 buses of the distribution network
that exhibited the highest power demands. The calculation of the rated power of each
module was performed using Equation (1) which was developed using a strategy analogous
to that adopted for the sizing of photovoltaic generators in [25].
Pmodule = C(p.u.) · Pload · 30 −Tmin
0.8 · PSH · 30
(1)
https://doi.org/10.3390/en19041069



<!-- page 7/24 -->

Energies 2026, 19, 1069
7 of 24
where
•
C (p.u.) represents the load consumption in per unit at the same bus where the
generator is allocated. This value is obtained using the load curve assigned to the
corresponding bus.
•
Pload is the rated power of the load installed at the bus, expressed in kW.
•
Tmin corresponds to the energy consumption value associated with the availability
charge, in accordance with ANEEL regulations. This represents the amount that will
always be billed by the utility, even if the consumer does not consume any energy
during the billing period. For single-phase loads, the value is 30 kWh, while for
three-phase loads it is 100 kWh [26].
•
Peak Sun Hours (PSH) refer to the number of daily hours during which solar radiation
would have an intensity equivalent to 1000 W/m2 (1 kW/m2) to generate the same to-
tal daily energy received at the site. They were empirically calculated using irradiance
data collected through GIS. The irradiance data were obtained from satellite sources
using the Python pvlib library. For the test system, this value was calculated based
on the regional irradiance data, collected from the same satellite-derived dataset, and
results in 5.18 h.
In Equation (1), a constant value of 0.8 was included to account for the energy losses of
the inverter. The power ratings of the modules calculated using Equation (1) were inserted
into the software as the maximum power point (Pmpp) of each generator. The irradiance
curves assigned to the modules were defined based on the obtained data and processed
as described in the next subsection. The irradiance curves were subsequently normalized
using a factor of 0.98 kW/m2. For the remaining technical parameters of the generators,
such as the inverter efficiency curve as a function of input power and the temperature curve,
typical values provided in the OpenDSS tutorials were adopted [27]. The photovoltaic
modules were modeled using the element PVSystem from OpenDSS and all the parameters
mentioned. Finally, the number of phases of each module was defined in accordance with
the type of load connected to the corresponding bus.
Note that the substation was configured with a per-unit voltage of 1.05 and three-phase
and single-phase short-circuit power levels of 20 MVA and 21 MVA, respectively. These
values are traditionally adopted for systems with characteristics similar to those of the
test system.
2.2. Data Extraction via GIS
This study stands out for employing irradiance data derived from a satellite-based
dataset in the modeling of photovoltaic modules, ensuring greater fidelity in the simulation
of the analyzed scenarios. The acquisition and processing of these data were carried out
using the method presented in [28], which employs the libraries pvlib, pandas, geopandas,
matplotlib and shapely in Python, in addition to Geographic Information System (GIS) tools.
Based on this procedure, daily irradiance curves were generated and subsequently assigned
to the feeder buses according to their respective geographic coordinates.
To facilitate the understanding of the method, its description is organized into
two stages: (i) data extraction and (ii) assignment of these data to the system buses.
2.2.1. Extraction of Irradiance Data
The data used in this study were obtained through the library pvlib python [29], which
accesses the databases of the PV-GIS platform (Photovoltaic Geographical Information System).
This platform is an online tool developed to provide solar irradiance data and photovoltaic
module performance information for any region of the world, with the exception of the
North and South Poles. The platform is managed by Joint Research Centre, a European
https://doi.org/10.3390/en19041069



<!-- page 8/24 -->

Energies 2026, 19, 1069
8 of 24
Commission service for science and knowledge that provides independent scientific advice
to support European Union policies. The database used in this study is “PVGIS-SARAH3”.
To determine the coordinates from which the irradiance data would be collected, the
following information is indicated [28].
•
The initial coordinate: The geographic coordinate [960,200, 8,142,500] was selected
as the initial coordinate and defined as a vector. This coordinate represents the first
sampling point.
•
An equation to generate the new sampling points: A point is parameterized around
another point using a radius and an angle. In other words, the equation makes it
possible to obtain a new point (X2,Y2) from an initial point (X1,Y1) by shifting it in a
direction defined by the angle kπ/2 by a given distance p, as shown in Equation (2).
"
X2
Y2
#
=
"
X1
Y1
#
+ p
"
sin( kπ
2 )
cos( kπ
2 )
#
(2)
In this work, the step distance p between the points was defined as 500 m, and k is a
constant that assumes integer values from 0 to 4. Using this equation, new points were
generated up to a maximum radius of 7 km, restricted to the feeder area, which has an
extension of 14 km. Figure 2 illustrates the process of creating these sampling points.
In Figure 2, Point 1, shown in green, corresponds to the point generated in the
first iteration, while point 2, shown in orange, represents the point obtained in the
second iteration, calculated from the coordinates of point 1. To facilitate visualization,
points that would originally overlap were displayed side by side. Thus, point 1 and
the point identified as “k = 3” (in orange) occupy the same position, as do point 2
and the point identified as “k = 1” (in green). However, the process does not generate
overlapping points; whenever a newly generated point coincides with an existing one,
it is simply discarded. In this work, a total of 841 points were generated, covering the
entire area occupied by the feeder.
•
Irradiance data acquisition: Using the Python pvlib library, irradiance records were
obtained for the coordinates of the 841 generated points. The retrieved data correspond
to the period from 2011 to 2015 and are provided as global irradiance values for each
hour of every day within this interval. The selection of this period was based on data
availability, following the methodology adopted in [28].
•
Calculation of hourly averages: After extraction, the irradiance data were stored
in a Python list, and from this data, both the average irradiance values for each
point—using records from 2011 to 2015 and disregarding null values—and the hourly
average irradiance values at each point were calculated, obtained by grouping the
measurements according to the hour of the day. The former were used to generate a
grid with different color intensities representing the irradiance level at each location,
while the latter served as the basis for constructing the irradiance curves employed in
the modeling of the photovoltaic modules.
2.2.2. Allocation and Processing of Irradiance Data
Once the irradiance data were extracted, the following procedure was carried out [28]:
•
Creation of Irradiance Grids: Using Equation (3), four new points are generated from
each sampled point generated in the previous procedure. The new points serve as the
vertices of the squares that make up the grid.
"
X2
Y2
#
=
"
X1
Y1
#
+ p
√
2
2
"
sin( kπ
4 )
cos( kπ
4 )
#
(3)
https://doi.org/10.3390/en19041069



<!-- page 9/24 -->

Energies 2026, 19, 1069
9 of 24
The above equation is applied iteratively until all 841 sampled points have been
processed. This procedure is illustrated in Figure 3.
•
Assignment of Irradiance Values to the Grid: The formed grids are polygons whose
geographic coordinates have been recorded in a GeoDataFrame. After their creation, the
average irradiance values and the hourly average irradiance values were incorporated
into the GeoDataFrame of the grids.
•
Irradiance Data Allocation to the Buses: For this purpose, the geographic coordinates
of the system buses were cross-referenced with those of the grids created in the
previous steps. It was necessary to load the electric grid data into the code in Python
and convert it into a GeoDataFrame containing each bus and its respective geographic
coordinate. Finally, the buses were assigned the irradiance data from the grids in
which they were spatially located.
Figure 2. Creation of the sampling points.
Figure 3. Generation of Points for Grid Formation.
The grids were plotted on a map with their respective average irradiance values, and
the network data were subsequently modeled for the creation of the map shown in Figure 4.
https://doi.org/10.3390/en19041069



<!-- page 10/24 -->

Energies 2026, 19, 1069
10 of 24
Figure 4. Feeder map and irradiance intensity levels.
2.3. Case Studies
The case studies were defined by comparing the original electrical grid with the grid
incorporating DG, and evaluating its performance after applying three different strategies
to mitigate RPF.
In all cases, the simulation mode used was daily for a 48-h period (two days). This
mode was chosen to allow the observation of the effects of generation and consumption
variations throughout the day and, additionally, to enable the analysis of battery operation
under steady-state conditions. This is due to the fact that, in OpenDSS, the batteries start the
simulation fully charged, which influences their operational behavior during the first day.
2.3.1. Base Case
The electric grid was initially simulated in its normal operating state, without the
presence of photovoltaic plants. The conditions obtained under this configuration allow
for a comparison of the grid’s performance after the integration of photovoltaic plants and
after the application of the evaluated RPF mitigation strategies. Thus, the results of this
base case serve as a reference for the analysis of the other simulated scenarios.
2.3.2. DG Base Case
The electric grid was simulated considering the allocation of 90 photovoltaic solar
plants, selected among the load buses with the highest installed power. Together, these
90 buses represent approximately 66% of the feeder’s total consumption power, character-
izing a scenario of high photovoltaic solar generation penetration.
The modeling of the photovoltaic modules follows the procedure described in
Section 2.1.4. The solar plants were allocated to the 45 loads with the highest nominal
power. The evaluated strategies were applied only to these buses, as implementing them to
all solar-equipped buses would be economically unfeasible. Table 6 presents the descriptive
statistics of the 45 allocated solar plants.
Table 6. Descriptive statistics of the allocated solar plants.
Statistic
Value (kVA)
Mean
43.9787
Standard deviation
15.9996
https://doi.org/10.3390/en19041069



<!-- page 11/24 -->

Energies 2026, 19, 1069
11 of 24
Table 6. Cont.
Statistic
Value (kVA)
Minimum
31.9115
25th percentile
35.3804
Median (50th percentile)
39.5613
75th percentile
48.7586
Maximum
133.7897
2.3.3. Case 1—Battery Storage System
This case corresponds to the electric grid of the standard scenario with distributed
generation (90 solar plants), augmented by the allocation of 45 batteries installed at the
45 buses with the highest load power. Each battery has a nominal power equal to twice
the installed power of the load at its respective bus, as well as a storage capacity equal to
eight times its own nominal power.
The sizing of these two parameters was carried out empirically, after observing that
the simulations exhibited better performance in mitigating RPF when the adopted power
was equivalent to twice the load. In comparison, adopting a power equal to the load for the
battery connected to the same bus resulted in inferior performance, even when the stored
energy was sized to be numerically equivalent to 20 times its nominal power. Power losses
and RPF levels were increased in the last case because the amount of energy that needed to
be injected to neutralize the reverse flow, at certain times, exceeded the battery’s maximum
power capacity, limiting its ability to fully mitigate RPF.
The battery’s storage capacity was sized to ensure operational autonomy for up to 8 h,
based on the understanding that continuous periods of generation surplus or demand for
energy supply do not exceed this interval.
The batteries’ charge and discharge curve was calculated to simulate the operation
of an electronic inverter capable of monitoring the power flow at the bus. The curve was
designed to mitigate RPF, absorbing excess energy and then injecting it when consumption
exceeds generation. For this calculation, DG Base Case was first simulated, and the genera-
tion curve s of the PV Systems were extracted and compared with the load curves (Load
Shapes) from the same bus. The batteries’ curves were calculated by subtracting the load
curve values for the generation curve values.
2.3.4. Case 2—Inverter of a Grid Zero System
This case considers the grid operating with an inverter capable of monitoring the
power flow and blocking the export of energy from the photovoltaic plants to the network,
thereby mitigating RPF. Since this control is not directly implemented in OpenDSS, it was
manually implemented using the element “generator” of the software. The generation curves
of the PV Systems were extracted from the DG Base Case and modified so that subsequent
generation would not exceed the bus load. Therefore, generation was kept unchanged
while consumption remained higher than it, and was only adjusted at moments when
generation would surpass consumption, at which point it was set to match it. This new
generation curve was used in the modeling of the 45 generators located at the buses with
the highest load density in the network, while the remaining 45 generators were kept
constant and identical to those in DG Base Case.
2.3.5. Case 3—PV Curtailment
In this case, the electric grid was simulated with a control that limits the energy
generation of the PV Systems using the bus voltage as a reference. The proposed control was
implemented using the “InvControl” element, which performs inverter control in OpenDSS
https://doi.org/10.3390/en19041069



<!-- page 12/24 -->

Energies 2026, 19, 1069
12 of 24
controlling the injection of active or reactive power based on an analyzed parameter, such
as the bus voltage.
Given the characteristic of the software’s native control OpenDSS, which prioritizes
nodal variables over the direct monitoring of power flow in the branches, the adopted
strategy was based on the direct physical correlation between the occurrence of RPF and
the rise in voltage levels [15]. Thus, the control function (Volt–Watt), native to OpenDSS
was parameterized to act in the joint mitigation of RPF at the transformer and overvoltages
at the buses, and was applied to the 45 buses with the highest loads.
The inverter control followed the relationship defined in Figure 5, limiting the active
power (Pmpp) in per unit according to the voltage recorded at the bus. Additionally, the
OpenDSS inverter parameter “delta P” was set to 0.3, defining the maximum allowed
variation in output power between consecutive control intervals.
Figure 5. Power Injection vs. Bus Voltage.
3. Tests and Results
System performance was assessed by analyzing bus voltage profiles, technical energy
losses, substation energy demand, and RPF measured at selected points within the network.
This comprehensive evaluation enables a clear comparison of the benefits and limitations
associated with each strategy, thereby supporting informed conclusions regarding their
practical feasibility, operational suitability, and the potential adaptations required for real-
world implementation.
3.1. Reverse Power Flow
3.1.1. Base Case
To enhance the objectivity of the analysis, attention was focused on the two transform-
ers exhibiting the most severe RPF conditions, namely those with the highest magnitudes of
injected power, as well as on the substation output to assess the overall system behavior. For
comparison purposes, Figures 6–8 present the power flow profiles of these elements under
the Base Case scenario, which represents the distribution network without photovoltaic
generation. In all cases, the reported power flows correspond to three-phase values.
Note that the power flow profiles of Transformers 28 and 70 follow the residential
and industrial load curves, respectively, as these are the only load types connected to the
secondary sides of the corresponding transformers. The monitoring and recording of the
power flow of these elements were performed using the “Monitor” element of OpenDSS.
https://doi.org/10.3390/en19041069



<!-- page 13/24 -->

Energies 2026, 19, 1069
13 of 24
Figure 6. Power Flow of Transformer 28 in the Base Case.
Figure 7. Power Flow of Transformer 70 in the Base Case.
Figure 8. Power Flow at the Substation Output in the Base Case.
https://doi.org/10.3390/en19041069



<!-- page 14/24 -->

Energies 2026, 19, 1069
14 of 24
3.1.2. DG Base Case
Figures 9–11 are also included as reference cases for comparison with the three mit-
igation strategies evaluated in this work. The corresponding scenario is generically re-
ferred to as the “DG Base Case,” representing the distribution network with the inte-
gration of 90 photovoltaic plants. For completeness, the Base Case curves for the same
elements—corresponding to the network without photovoltaic generation—are also dis-
played in the figures. A simple analysis reveals a pronounced pattern of RPF in both the
transformers and at the substation output, indicating a concerning scenario for the network
in question.
The two transformers selected for the analysis (28 and 70), are three-phase transformers
with nominal powers of 225 kVA and 112.5 kVA, respectively. Therefore, transformer 70 is
overloaded, as the RPF recorded reached peaks of 125 kW. This also represents a critical
scenario for this study case.
Figure 9. Power Flow of Transformer 28 in DG Base Case.
Figure 10. Power Flow of Transformer 70 in DG Base Case.
https://doi.org/10.3390/en19041069



<!-- page 15/24 -->

Energies 2026, 19, 1069
15 of 24
Figure 11. Power Flow at the Substation Output in DG Base Case.
3.1.3. Case 1—Battery Storage System
The results for Case 1 are presented in Figures 12–14. In this scenario, 45 BESS were
allocated at the buses with the highest nominal load levels. The results show an almost
complete attenuation of RPF on the second day of the simulation, that is, after the initial
24 h period. The behavior observed during the first day reflects the transient operation
associated with the batteries starting at a 100% state of charge, which limits their ability
to absorb all excess energy during this interval. For validation purposes, the system
performance on the second day is considered representative of cyclic steady-state operation,
during which the batteries fully absorb surplus generation and effectively mitigate RPF.
3.1.4. Case 2—Inverter of a Grid Zero System
The simulation results for Case 2 are illustrated in Figures 15–17, which correspond to
the transformers and the substation input analyzed in this study, as well as to the remaining
network elements affected by the proposed method.
Figure 12. Power Flow of Transformer 28 in Case 1 (Batteries).
https://doi.org/10.3390/en19041069



<!-- page 16/24 -->

Energies 2026, 19, 1069
16 of 24
Figure 13. Power Flow of Transformer 70 in Case 1 (Batteries).
Figure 14. Power Flow at the Substation Output in Case 1 (Batteries).
Figure 15. Power Flow of Transformer 28 in Case 2 (Grid Zero).
https://doi.org/10.3390/en19041069



<!-- page 17/24 -->

Energies 2026, 19, 1069
17 of 24
Figure 16. Power Flow of Transformer 70 in Case 2 (Grid Zero).
Figure 17. Power Flow at the Substation Output in Case 2 (Grid Zero).
Case 2 represents the operation of electronic inverters that restrict energy injection into
the grid by manually shaping the generation output curve. As expected, the results exhibit
an almost complete suppression of reverse power flow at the two analyzed transformers.
However, applying this control strategy to only 45 buses proved insufficient to fully
eliminate reverse power flow at the substation output. Similar to the PV Curtailment
approach, this outcome highlights the main economic trade-off associated with the method:
network protection is achieved through aggressive generation curtailment, which directly
affects the photovoltaic system’s payback by discarding available energy.
3.1.5. Case 3—PV Curtailment
Figures 18–20 illustrate the power flows of the sampled elements for Case 3, in which
the PV Curtailment was applied. A more irregular behavior can be observed, as RPF was not
eliminated in transformer 70, and in transformer 28, the attenuation of the flow led to the
return of consumption predominance over generation, even during peak solar incidence
periods. Therefore, the strategy was less effective in mitigating the RPF of transformer
70 compared to the strategies in Case 1 and Case 2.
https://doi.org/10.3390/en19041069



<!-- page 18/24 -->

Energies 2026, 19, 1069
18 of 24
Figure 18. Power Flow of Transformer 28 in Case 3 (PV Curtailment).
Figure 19. Power Flow of Transformer 70 in Case 3 (PV Curtailment).
Figure 20. Power Flow at the Substation Output in Case 3 (PV Curtailment).
https://doi.org/10.3390/en19041069



<!-- page 19/24 -->

Energies 2026, 19, 1069
19 of 24
The reduced effectiveness of PV Curtailment in mitigating RPF is primarily attributed
to the physical characteristics of the network. In low-impedance (strong) circuits, substan-
tial power injections may occur without inducing significant voltage deviations, rendering
Volt–Watt control schemes largely insensitive to reverse current flow at the point of con-
nection. Nevertheless, despite this limitation at the local level, the strategy achieved a
noticeable reduction in RPF at the substation output, effectively attenuating upstream
reverse flows and improving overall system performance.
3.2. Energy Injected into the Network
In a more general scenario, the power flows of all 335 transformers were compu-
tationally analyzed to calculate the total amount of energy injected into the grid by the
photovoltaic modules in each case. The transformer power flows were exported to CSV
(Excel) files, whose data were read and managed via Python for the total sum of all negative
instantaneous powers. As a result of this procedure, it was concluded that there was an
injection of 47,737.24 kWh in DG Base Case; 23,925.45 kWh in Case 1; 17,105.15 kWh in
Case 2; and 21,074 kWh in Case 3. All cases reduced the amount of energy injected, with
Case 2 showing the largest reduction and Case 1 the smallest. However, some observations
should be noted:
(1) Case 2 presents the results of an ideal inverter operation, simulated through a
manually designed generation curve and assigned to a generator.
(2) Case 1 was influenced by the initial state of the battery, since the battery starts the
simulation fully charged due to the configuration of OpenDSS. Therefore, it cannot absorb
all the excess energy to mitigate the RPF on the first day, as already observed in the figures
showing the power flow of transformers 70 and 28. As a result, the energy injected ended
up being higher for this case.
3.3. Voltage Levels
The evaluation of bus voltage levels was performed using the “Monitor” element
of OpenDSS, which can be configured to record hourly values of voltage, current, and
instantaneous power for a specific network element. A total of 333 monitors were deployed
to track the voltage at the output terminals of all loads in the system. The recorded bus
voltages were compared against those obtained in the Base Case, and the differences were
computed to quantify voltage rises or drops across the network.
To ensure a more objective presentation of the results, the average percentage voltage
rise was computed for each study case by considering all buses in the network. In addition,
the maximum percentage voltage rise observed in each scenario was also determined.
These metrics are summarized in Table 7.
Table 7. Voltage Levels at Network Buses.
Study Cases
Average Percentage Rise (%)
Maximum Percentage Rise (%)
DG Base Case
1.1210
5.2416
Case 1
1.2319
4.3721
Case 2
1.0347
5.0665
Case 3
0.7005
3.1257
From the results, it was observed that Case 3, the PV Curtailment, showed the greatest
reduction in voltage rise among the three proposed cases, likely because it synchronized
the reduction of energy injection with the voltage peaks. Case 1 exhibited the highest
average voltage rise, while Case 2 presented the highest individual voltage peak among the
three cases. Despite differing efficiencies in reducing voltage rises, all three cases achieved
better results than DG Base Case, which showed the highest voltage increase levels.
https://doi.org/10.3390/en19041069



<!-- page 20/24 -->

Energies 2026, 19, 1069
20 of 24
3.4. Energy Losses and Energy Supplied by the Substation
The analysis of energy losses was carried out using the element “Energymeter”, from
OpenDSS, which is associated with an element and is capable of obtaining energy losses,
maximum power demand, and the energy flow recorded in the network downstream of the
element to which the meter is assigned (Energymeter). The meter in question was installed
on the distribution line segment connected to the system substation and was used to record
energy losses, as well as the energy supplied by the substation in each of the cases. The
results are illustrated in Figure 21.
Figure 21. Network Technical Losses in Each Case.
The two cases with the highest energy losses were the Base Case and the DG Base
Case, with losses of 3077 kWh and 2312 kWh, respectively. Thus, it can be observed that
the three evaluated strategies provided technical improvements to the electrical network in
this regard.
It is worth noting that, when allocating 30 photovoltaic plants to the buses with the
highest load density of Base Case—following the same modeling and bus selection criteria
as in DG Base Case—the network presented losses of 2143 kWh, a value lower than that
of DG Base Case (2312 kWh), in which 90 photovoltaic modules were installed. This
result indicates that, in DG Base Case, the electrical network may already be operating
near or beyond its accommodation capacity, as the increase in photovoltaic generation
ended up increasing losses compared to the case with fewer modules, thereby reducing
operational efficiency.
Regarding Cases 1, 2, and 3, the adoption of the strategies allowed a reduction in
energy losses from the Base Case by 61.36% in Case 1, 44.72% in Case 2, and 37.73% in
Case 3. In comparison, DG Base Case reduced losses by only 24.86%. The allocation of
batteries to mitigate RPF, a strategy tested in Case 1, produced the best results regarding
losses, followed by Cases 2 and 3, respectively.
This result can be explained by the fact that the allocation of batteries favors local
energy storage within the system, reducing losses related to transportation through the
distribution lines and energy conversion in the transformers.
It is important to highlight that the results of Case 1 were superior, despite the fact
that the allocated batteries could not mitigate part of the RPF on the first day due to the
https://doi.org/10.3390/en19041069



<!-- page 21/24 -->

Energies 2026, 19, 1069
21 of 24
initial configuration. In other words, it is possible that the steady-state operation of the
batteries could produce even better results.
Finally, the energy supply analysis yielded the results shown in Table 8, which presents
the overall results of the simulation involving the most important operational parameters of
the network. According to this analysis, Cases 1, 2, and 3 reduced the amount of energy the
substation had to supply to the network compared to the Base Case; however, only Case 1
achieved a lower substation demand than the DG Base Case. The substation supplied the
network with 42,781 MWh in Case 1, 51,038 MWh in DG Base Case, 81,164 MWh in Case 2,
and 81,806 MWh in Case 3.
The logical conclusion is that, although the allocation of photovoltaic modules reduced
the amount of energy the substation had to supply—which was 140,694 MWh in the Base
Case—the implementation of inverters that limit energy injection into the network, as in
Cases 2 and 3, increased the distribution network’s demand for energy from the substation.
This indicates that Case 1 provided benefits, while Cases 2 and 3 caused detriment to the
network compared to DG Base Case, since reducing the amount of energy that needs to
be supplied by large central power plants is one of the main objectives of government
incentives for the solar energy sector.
Table 8. Electrical Network Operation Parameters.
Study Cases
Energy Supplied by
the Substation (kWh)
Energy Losses (kWh)
Maximum Voltage
Rise (%)
Energy Injected into
the Network (kWh)
Base Case
140,694
3077
0%
0
DG Base Case
51,038
2312
5.2416%
47,737.24
Case 1
42,781
1189
4.3721%
23,925.45
Case 2
81,164
1701
5.0665%
17,105.15
Case 3
81,806
1916
3.1257%
21,074.21
It was observed that the strategy of allocating batteries to the buses with the highest
power injections—adopted in Case 1—was the one that provided the greatest reduction in
both the energy demand from the substation and the technical losses in the network.
The strategy of PV Curtailment (Case 3), which consisted of controlling the power
injected by the photovoltaic modules based on the bus voltage, proved to be the most
effective in mitigating voltage rise, and is therefore the most efficient approach for
preventing overvoltage.
On the other hand, Case 2, which simulated the ideal performance of inverters capable
of monitoring the bus power flow to control energy injection, presented the best results
in reducing the energy injected into the network. It is worth noting, however, that the
performance of Case 1 in this regard was limited by the initial configuration of the battery.
The analysis of power flow in transformers 70 and 28 indicated greater suppression of
RPF in Case 1, considering only the period in which the battery operated properly on the
second day. Regarding the flow at the substation output, the three cases showed similar
results, in which they attenuated a large part of the 2 MW three-phase reverse flow.
The fact that none of the strategies managed to fully mitigate this flow raises questions
about the scale of investments that would need to be made if a scenario similar to this were
encountered in practice.
4. Conclusions
The analysis conducted in this study shows that RPF represents a significant impact
associated with the increasing penetration of photovoltaic generation in distribution net-
works. To address this issue, three mitigation strategies are proposed: (i) the allocation
https://doi.org/10.3390/en19041069



<!-- page 22/24 -->

Energies 2026, 19, 1069
22 of 24
of battery energy storage systems; (ii) the use of inverters operating under a Grid Zero
scheme, which prevent power injection into the network by monitoring the power flow
at the connection bus; and (iii) the implementation of inverters that regulate the power
injected by photovoltaic modules as a function of the bus voltage.
Among the three evaluated scenarios, the battery allocation strategy achieved the
best overall performance. It demonstrated high effectiveness in suppressing RPF, reducing
technical losses, and significantly lowering the demand for energy supplied by the sub-
station. This reduction in substation demand also translates into decreased reliance on
energy generated by large centralized power plants, thereby aligning with public policies
that promote the integration of distributed generation.
It is concluded that no universal solution exists, as the results obtained for the test sys-
tem indicate distinct trade-offs among the evaluated strategies. The BESS-based approach
exhibits superior technical performance, effectively eliminating RPF and reducing power
losses, albeit at the expense of higher investment costs. In contrast, curtailment-based
strategies (Grid Zero and Volt–Watt) shift the burden toward operational inefficiency and
are therefore viable mainly in scenarios where utilities impose penalties for RPF or enforce
strict injection limits. Additionally, the PV curtailment strategy shows further potential
for application in distribution systems experiencing overvoltage issues, yielding positive
results in mitigating this condition. Future work will incorporate real-world inverter
constraints to provide a more realistic and comprehensive assessment.
Author Contributions: Conceptualization, I.S.P., G.d.C.V. and L.P.G.N.; methodology, I.S.P., G.d.C.V.
and L.P.G.N.; software, I.S.P., G.d.C.V. and L.P.G.N.; validation, I.S.P., G.d.C.V. and L.P.G.N.; formal
analysis, I.S.P., G.d.C.V., J.M.L.-L., N.M.-G. and L.P.G.N.; investigation, I.S.P., G.d.C.V., J.M.L.-L.,
N.M.-G. and L.P.G.N.; resources, I.S.P., G.d.C.V., J.M.L.-L., N.M.-G. and L.P.G.N.; data curation,
I.S.P., G.d.C.V. and L.P.G.N.; writing—original draft preparation, I.S.P., G.d.C.V. and L.P.G.N.;
writing—review and editing, I.S.P., G.d.C.V., J.M.L.-L., N.M.-G. and L.P.G.N.; visualization, I.S.P.,
G.d.C.V., J.M.L.-L., N.M.-G. and L.P.G.N.; supervision, I.S.P., G.d.C.V., J.M.L.-L., N.M.-G. and L.P.G.N.;
project administration, I.S.P., G.d.C.V. and L.P.G.N.; funding acquisition, I.S.P., G.d.C.V. and L.P.G.N.
All authors have read and agreed to the published version of the manuscript.
Funding: This research was supported by the Programa de Apoio à Pós-Graduação (PROAP)
of CAPES—Coordenação de Aperfeiçoamento de Pessoal de Nível Superior. Process SEI/UFG
No. 23070.034610/2025-45.
Data Availability Statement: The original contributions presented in this study are included in the
article. Further inquiries can be directed to the corresponding author.
Acknowledgments: The authors acknowledge the Conselho Nacional de Desenvolvimento Científico
e Tecnológico (CNPq) for the support provided for the development of this work through Call
CNPq/MCTI/FNDCT No. 18/2021—Track A—Emerging Groups, process No. 408898/2021-6. The
authors also acknowledge the Graduate Program in Electrical and Computer Engineering (PPGEEC)
at the Federal University of Goiás and the Department of Electrical Engineering at Universidad
de Antioquia.
Conflicts of Interest: The authors declare no conflicts of interest.
References
1.
United Nations. Sustainable Development Goals. Available online: https://brasil.un.org/pt-br/sdgs (accessed on 28 May 2025).
2.
Canal Solar. Energia Solar Amplia Participação na Matriz Elétrica Enquanto Outras Fontes Recuam. Available online: https:
//canalsolar.com.br/energia-solar-participacao-matriz-eletrica-2/ (accessed on 7 July 2025).
3.
Official Gazette of the Union. Brazil. Law No. 14,300 of 6 January 2022: Legal Framework for Distributed Generation.
Available online: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/lei/l14300.htm (accessed on 22 June 2025).
https://doi.org/10.3390/en19041069



<!-- page 23/24 -->

Energies 2026, 19, 1069
23 of 24
4.
Brazilian Electricity Regulatory Agency (ANEEL). Normative Resolution No. 482 of 17 April 2012. Available online: https:
//www.aneel.gov.br/sala-de-imprensa-detalhe/resolucao-normativa-no-482-de-17-de-abril-de-2012 (accessed on 22 June 2025).
5.
Brazilian Photovoltaic Solar Energy Association (ABSOLAR). Infographic on the Photovoltaic Solar Energy Market.
Available online: https://www.absolar.org.br/mercado/infografico/ (accessed on 28 May 2025).
6.
Agência Brasil. With 22% of the Electricity Matrix, Solar Energy Is the Second Largest Source in the Country. Available online:
https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2025-03/com-22-da-matriz-eletrica-energia-solar-e-a-2-maior-
fonte-do-pais (accessed on 28 March 2025).
7.
Ferreira, G.F. Analysis of Power Flow Inversion in an Industrial Electrical Installation with Photovoltaic Solar Energy Generation.
Bachelor’s Thesis, Federal University of Goiás, Goiânia, Brazil, 2024. Available online: http://repositorio.bc.ufg.br/handle/ri/26
128 (accessed on 27 May 2025).
8.
Stecanella, P.A.J.; Vieira, D.; Vasconcelos, M.V.L.; Ferreira Filho, A.D.L. Statistical Analysis of Photovoltaic Distributed Generation
Penetration Impacts on a Utility Containing Hundreds of Feeders. IEEE Access 2020, 8, 175009–175019. [CrossRef]
9.
Saldarriaga-Zuluaga, S.D.; López-Lezama, J.M.; Muñoz-Galeano, N. Optimal Coordination of Over-Current Relays in Microgrids
Using Unsupervised Learning Techniques. Appl. Sci. 2021, 11, 1241. [CrossRef]
10.
Pérez Posada, A.F.; Villegas, J.G.; López-Lezama, J.M. A Scatter Search Heuristic for the Optimal Location, Sizing and Contract
Pricing of Distributed Generation in Electric Distribution Systems. Energies 2017, 10, 1449. [CrossRef]
11.
León, L.F.; Martinez, M.; Ontiveros, L.J.; Mercado, P.E. Devices and Control Strategies for Voltage Regulation under the Influence
of Photovoltaic Distributed Generation: A Review. IEEE Lat. Am. Trans. 2022, 20, 731–745. [CrossRef]
12.
Landbrug, A.G.; Dranka, G.G.; Vasques de Oliveira, R. Voltage Control Approach with Dynamic Voltage Reference for PV
Distributed Generation Operating under Cloud-Induced Shading Conditions. IEEE Access 2025, 13, 49092–49106. [CrossRef]
13.
Karngala, A.K.; Singh, C.; Xie, L. Predictive Reliability Assessment of Distribution Grids with Residential Distributed Energy
Resources. CSEE J. Power Energy Syst. 2025, 11, 2598–2609. [CrossRef]
14.
Silva, D.J.; Belati, E.A.; López-Lezama, J.M.; Pourakibari-Kasmaei, M. Optimal Allocation and Operation of Battery Energy
Storage Systems with Photovoltaic Generation in Modern Distribution Networks: A New Hybrid Approach. IET Renew. Power
Gener. 2025, 19, e70114. [CrossRef]
15.
Camilo, F.M.; Castro, R.; Almeida, M.E.; Pires, V.F. Assessment of Overvoltage Mitigation Techniques in Low-Voltage Distribution
Networks with High Penetration of Photovoltaic Microgeneration. IET Renew. Power Gener. 2018, 12, 649–656. [CrossRef]
16.
Hasan, S.; Tan, C.S.; Toh, C.L. Reverse Power Flow in Distribution Networks: Impacts, Challenges, Issues, and Technologies.
In Proceedings of the 2024 IEEE 22nd Student Conference on Research and Development (SCOReD); IEEE: New York, NY, USA, 2024;
pp. 19–24. [CrossRef]
17.
Unahalekhaka, P.; Sripakarach, P. Reduction of Reverse Power Flow Using the Appropriate Size and Installation Position of a
BESS for a PV Power Plant. IEEE Access 2020, 8, 102897–102906. [CrossRef]
18.
Majeed, I.B.; Nwulu, N.I. Reverse Power Flow Due to Solar Photovoltaic in the Low Voltage Network. IEEE Access 2023,
11, 44741–44758. [CrossRef]
19.
Dahe, N.A.; Saliba, L.; Mougharbel, I.; Kanaan, H.Y.; Saad, M. Hybrid Algorithm for Monitoring Reverse Power Flow Caused
by Distributed Renewable Energy Sources. In Proceedings of the 5th International Conference on Renewable Energies for Developing
Countries (REDEC); IEEE: New York, NY, USA, 2020; pp. 1–4. [CrossRef]
20.
Ranamuka, D.; Muttaqi, K.M.; Sutanto, D. Flexible AC Power Flow Control in Distribution Systems by Coordinated Control of
Distributed Solar-PV and Battery Energy Storage Units. IEEE Trans. Sustain. Energy 2020, 11, 2054–2062. [CrossRef]
21.
Holguin, J.P.; Rodriguez, D.C.; Ramos, G. Reverse Power Flow (RPF) Detection and Impact on Protection Coordination of
Distribution Systems. IEEE Trans. Ind. Appl. 2020, 56, 2393–2401. [CrossRef]
22.
Electric Power Research Institute (EPRI). OpenDSS Manual. Available online: https://sourceforge.net/projects/electricdss/files/
OpenDSS/OpenDSSManual.pdf/download (accessed on 15 June 2025).
23.
Santos Pereira, I. Strategies-to-Mitigate-Reverse-Power-Flow—Paper. GitHub Repository. 2025. Available online: https://github.
com/Ivanictor/Strategies-to-Mitigate-Reverse-Power-Flow---Paper (accessed on 10 February 2026).
24.
Andrades, G.C.B.; Calaça, M.S.A. Simulation of the Operation of Electric Power Distribution Systems Using OpenDSS. Bachelor’s
Thesis, Federal University of Goiás, Goiânia, Brazil 2016. (In Portuguese)
25.
Pinho, J.T.; Galdino, M.A. (Eds.) Engineering Manual for Photovoltaic Systems; CEPEL/CRESESB: Rio de Janeiro, Brazil, 2014.
26.
Brazilian Electricity Regulatory Agency (ANEEL). Normative Resolution No. 1,000 of 20 December 2021: Establishes the
Rules for the Provision of the Public Electricity Distribution Service. Official Gazette of the Union. Available online: https:
//www2.aneel.gov.br/cedoc/ren20211000.html (accessed on 2 January 2024).
27.
Radatz, P. OpenDSS Time-Series: Introduction. YouTube Tutorial, Introductory Video of the OpenDSS Time-Series Series. Avail-
able online: https://www.youtube.com/watch?v=FbITFvo-vJg&list=PLhdRxvt3nJ8yBSb1r64NB0JS5XHinBgGa (accessed on
15 June 2025).
https://doi.org/10.3390/en19041069



<!-- page 24/24 -->

Energies 2026, 19, 1069
24 of 24
28.
Arantes, P.C.G. Spatial Simulation of Distributed Generation Integration in Electric Power Distribution Networks. Bachelor’s
Thesis, Federal University of Goiás, Goiânia, Brazil, 2023. (In Portuguese)
29.
Pvlib Python Development Team. Pvlib Python (Version 0.9.4). Available online: https://pvlib-python.readthedocs.io/en/stable/
(accessed on 15 June 2025).
Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
https://doi.org/10.3390/en19041069
