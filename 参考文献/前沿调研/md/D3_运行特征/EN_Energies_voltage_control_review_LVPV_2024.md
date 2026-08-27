<!--
source: D3_运行特征/EN_Energies_voltage_control_review_LVPV_2024.pdf
sha256: 9eace7b80d2411b789729c9211d33377373b313debedf7c020bacaaefd76e6c6
method: pymupdf
pages: 24
-->

<!-- page 1/24 -->

Citation: Gao, X.; Zhang, J.; Sun, H.;
Liang, Y.; Wei, L.; Yan, C.; Xie, Y. A
Review of Voltage Control Studies on
Low Voltage Distribution Networks
Containing High Penetration
Distributed Photovoltaics. Energies
2024, 17, 3058. https://doi.org/
10.3390/en17133058
Academic Editor: Georgios
Christoforidis
Received: 10 May 2024
Revised: 28 May 2024
Accepted: 19 June 2024
Published: 21 June 2024
Copyright: © 2024 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed
under
the
terms
and
conditions of the Creative Commons
Attribution (CC BY) license (https://
creativecommons.org/licenses/by/
4.0/).
energies
Review
A Review of Voltage Control Studies on Low Voltage Distribution
Networks Containing High Penetration Distributed Photovoltaics
Xiaozhi Gao, Jiaqi Zhang
, Huiqin Sun, Yongchun Liang
, Leiyuan Wei *
, Caihong Yan and Yicong Xie
School of Electrical Engineering, Hebei University of Science and Technology, Shijiazhuang 050018, China;
gaoxiaozhi@hebust.edu.cn (X.G.); leap091@163.com (J.Z.); sunhuiqin65@gmail.com (H.S.);
lycocean@163.com (Y.L.); 2022102103@stu.hebust.edu.cn (C.Y.); yicong0701@163.com (Y.X.)
* Correspondence: leiywei@163.com
Abstract: Distributed photovoltaic (PV) in the distribution network accounted for an increasing
proportion of the distribution network, and the power quality of the distribution network of the
power quality problem is more and more significant. In this paper, the voltage regulation methods
for low-voltage distribution networks containing high-penetration PV are investigated. First, the
working principles of the four voltage control methods are introduced: energy storage system
configuration, regulating the reactive power output of PV inverters, restricting the active power
output of PV, adjusting the switching positions of on-load regulator trap changer and distribution
network reconfiguration, and then, in combination with the recent related research, the optimization
of each method is compared horizontally with its respective concerns and characteristics. The
optimization of each method is compared horizontally with the recent studies to find out the focus
and characteristics of each method, and the shortcomings of each method are explored. Coordinated
voltage control through multiple flexibility resources has become the mainstream voltage regulation
scheme, and distribution network voltage regulation is considered from the perspective of flexibility
resources. The three types of flexibility resources, namely, source, network, and storage, have been
widely used in distribution network voltage regulation. Although load-side resources have become
one of the main regulation resources of the new type of power system, the current study introduces
less about the participation of load-side flexibility resources in voltage regulation of LV distribution
networks and advancing the application of load-side resources in voltage regulation of LV distribution
networks is the focus of future research. Then, the important role of load-side flexibility resources
in voltage regulation is described in three parts, namely, the important role of load-side resources,
the development trend, and the suggestions for promoting the coordination of source-network-load-
storage flexibility resources, aiming to promote the application of load-side resources in voltage
regulation in LV distribution networks, and the suggestions and programs are proposed for the
technological challenges faced by voltage regulation. In the context of today’s new power system
emphasizing the interaction of source, network, load, and storage, new technologies and methods
for solving voltage problems in LV distribution networks are prospected, with a view to providing
certain reference value for the actual operation and optimization of distribution network systems.
Keywords: distributed photovoltaic; voltage overrun; distribution network; voltage regulation
1. Introduction
With the gradual increase in global demand for clean energy, photovoltaic (PV) power
generation, as a representative of renewable energy, is ushering in a moment of rapid
development. China has firmly established itself as the leader of the global PV market, and
according to data from the National Energy Administration (NEA), a new grid-connected
capacity of 216.30 GW will be added in 2023, a year-on-year increase of 148%, equivalent to
the sum of the new domestic installed capacity from 2019 to 2022. Among them, 120.014 GW
of centralized PV power plants and 96.286 GW of distributed PV, while the installed capacity
Energies 2024, 17, 3058. https://doi.org/10.3390/en17133058
https://www.mdpi.com/journal/energies



<!-- page 2/24 -->

Energies 2024, 17, 3058
2 of 24
of household PV among distributed PV reached 43.483 GW. The cumulative grid-connected
capacity as of the end of 2023 was 608.918 GW, of which 354.481 GW was centralized
PV power plants, 254.438 GW was distributed PV power plants, and 115.797 GW was
household PV.
Distributed PV has the characteristics of small investment scale, fast construction
speed, low entry threshold, wide development scope, and many subjects involved, etc.
Driven by policy support, technological progress, etc., it will still maintain rapid growth in
the future [1,2]. It is expected that by 2030, the installed capacity of distributed PV in China
will exceed 500 GW.
At the international level, the PV markets in Europe, the United States, and Asia are
also showing a booming trend, with the global PV new installations at 444 GW in 2023, up
76% year-on-year, with half of the incremental growth coming from China. The total global
PV installations reached 1552.3 GW in 2023 and are predicted to reach 1954.6 GW in 2024,
with 402.3 GW of new installations. The European Green New Deal is an important driver
for the development of PV and other clean technologies. Many European countries are
committed to increasing the proportion of renewable energy in the overall energy mix and
promoting the widespread use of green energy.
However, with the increased penetration of PV systems, power quality problems have
become significant, especially in distributed PV systems, where the imbalance between PV
output and load leads to reverse currents in the lines, causing voltage overruns. For the
voltage overrun caused by distributed PV grid-connected, voltage regulation becomes a key
factor affecting the stability of the system. In this paper, we will deeply analyze the current
status of PV development at home and abroad, combined with the power quality problem,
focusing on the voltage regulation of distribution networks containing distributed PV with
a high penetration rate in order to study the solution to ensure the reliable operation of
the power system. Currently, the configuration of the energy storage system [3], reactive
power regulation of PV inverter [4], active power reduction of PV [5], and tap action of
the on-load regulator transformer [6] become the key solutions to the problem of voltage
overrun of distribution network with high penetration of PV.
This review firstly summarizes and combs the voltage regulation methods for LV
distribution networks containing high penetration distributed PV at home and abroad,
firstly analyzes the voltage control methods for LV distribution networks based on energy
storage system configuration, reactive power regulation, active power curtailment, OLTC,
and distribution network reconfiguration, and then reviews the characteristics, adaptive
scenarios, strengths, and deficiencies of the four types of commonly used voltage control
methods, and then presents them in the form of tables. After that, voltage control methods
coordinated by multiple devices are analyzed; then voltage control is considered from
the perspective of flexibility resources, and the important role of load-side resources in
voltage regulation is analyzed from three parts focusing on the important role of load-side
flexibility resources in voltage regulation, the development trend of load-side resources,
and the suggestions to promote the coordination of source-grid-load-storage flexibility
resources, which have become one of the main regulation resources of the new type of
power system, aiming to Load-side resources have become one of the main regulating
resources in the new power system, and it aims to promote the application of load-side
resources in voltage regulation in low-voltage distribution networks. Challenges to the
development of voltage control in LV distribution networks are also analyzed for the
reference of related researchers.
2. Low-Voltage Distribution Network Voltage Regulation Methods and
Comparative Analysis
2.1. Energy Storage System Configuration
The working principle of this method is to utilize the energy storage system to store
electricity when the load demand is less than the distributed PV generation output, to avoid
reverse power flow at the point of common coupling (PCC), and to suppress overvoltage.



<!-- page 3/24 -->

Energies 2024, 17, 3058
3 of 24
Common energy storage systems include flywheel energy storage, pumped storage, elec-
trochemical energy storage, etc. [7]. Electrochemical energy storage is currently the main
choice due to its advantages of fast response time and flexible configuration. The PV energy
storage access system topology is shown in Figure 1.
Figure 1. Schematic diagram of a typical PV energy storage access system.
Cheng et al. [8] propose a two-layer coordinated planning model for the energy storage
system and its communication network (CN), considering the coupling effect of CPS (Cyber-
Physical Systems) to solve the voltage overrun problem. Zoning planning for PV energy
storage and constructing a two-layer coordinated planning model can solve the problem
of mismatch between load demand and PV output time and improve the voltage stability
of the distribution network [9]. Considering the two-layer nested model for distributed
energy storage (DES) planning, it can effectively improve the voltage security margin
and reduce the subsequent voltage management cost [10]. Zhang et al. [11] propose a
source-network-load-storage hierarchical coordinated optimal control strategy to cope with
the distribution grid scheduling problem caused by the county-wide PV grid integration,
which optimizes the energy storage measurement and the load side through the algorithm
to improve the convergence speed and the economic operation efficiency of the grid. The
two-tier planning model considers the energy storage system to have a better economy and
be more robust.
Chen et al. [12] propose a segmented compensation strategy to reduce the charging and
discharging frequency of the energy storage system while smoothing the power fluctuation
of distributed photovoltaic power generation, which improves the stability and lifetime of
the energy storage system. The study of the capacity, location, and scheduling of distributed
energy storage in unbalanced distribution networks can better cope with the uncertainties
involved in generating power sources and loads and effectively stabilize the distribution
network voltage [13,14]. Distributed control of the two stages of PV inverter and energy
storage is currently being applied more widely, using the storage charge state as a consistent
variable, which takes into account the capacity of the storage and achieves simultaneous
control of the storage power and charge state [15]. Nowadays, deep reinforcement learning
for optimal maintenance of distribution network voltage has become a research hotspot,
which can better match the photovoltaic power output and load demand characteristics
by considering the energy storage charge state to extend the storage capacity with the
established objectives and constraints [16].
Advantages of this method:
1.
It has a bidirectional regulation function, fast response speed, flexible configuration,
and significant economic benefits.
2.
It can provide energy for the system during peak power hours, which helps to improve
voltage quality and reduce network losses.



<!-- page 4/24 -->

Energies 2024, 17, 3058
4 of 24
3.
It can effectively stabilize the fluctuation of distributed photovoltaic power gen-
eration so that the photovoltaic power generation system is transformed from an
uncontrollable to a controllable power source, which enhances its operability in the
distribution network.
Disadvantages of this method:
1.
Most of the energy storage models used in the current study are simplified models,
which cannot accurately assess the utilization value of the energy storage cycle;
2.
a single business model for user-side energy storage, coupled with the frequent
occurrence of safety accidents in energy storage, which restricts its application on a
large scale;
3.
high cost of the energy storage device, short service life, and poor economics for
large-scale equipment.
2.2. PV Inverter Reactive Power Regulation
In low voltage distribution networks with large line R/X ratios, reactive power control
of PV inverters is an effective means of voltage regulation, which is economically optimal
for the control of this scheme compared to controlling PV active, distributed energy storage
active, and tapping devices [17].
In recent years, more and more low-voltage household photovoltaic power generation
is connected to the grid through inverters with reactive power regulation capability, and
the relationship between adjustable reactive power capacity and inverter capacity for [18]
Qmax
PV = ±
q
SIN2 −PPV2
(1)
In the formula: Qmax
PV is the maximum reactive power output capacity of the inverter;
PPV is the active power generated by the PV; SIN is the capacity of the inverter, which is
about 1.0~1.1 times of the rated active capacity [18].
Figure 2 shows the capacity curve of the PV inverter. p\Point A PV grid-connected
active power is the rated power Prated
PV
The maximum reactive power output capacity of the
inverter is ±Qmax1
PV . Only by appropriately increasing the capacity of the inverter can the
inverter obtain a strong reactive power regulation capability. Meanwhile, with the change
of PV grid-connected power, the inverter reactive capacity is in the process of dynamic
change, for example, in Figure 2, when the PV grid-connected active power is reduced to
βPrated
PV
(β ∈(0,1)), the inverter operation point is shifted from point A to point B, and the
maximum reactive power output capacity of the inverter is increased to ±Qmax2
PV ; at night,
the value of the adjustable reactive capacity is equal to the value of the inverter capacity
when the grid active output is 0 kW.
Figure 2. Schematic diagram of the active and reactive capacity of the inverter.



<!-- page 5/24 -->

Energies 2024, 17, 3058
5 of 24
Low-voltage distribution network reactive power control is mainly in situ, and the
mainstream strategies can be divided into two [17,19]: cosφ (P) control (with PV grid-
connected active PPV as the control input, adjusting the inverter reactive power to control
the grid-connected power factor of the PV inverters, cosφ), and Q(U) control (with the
PV grid-connected voltage magnitude, V, as the control input to achieve inverter reactive
power QPV regulation).
The method works on the principle that when the reverse power flow causes voltage
overruns, the distributed PV autonomously regulates its reactive power output, thus
keeping the node voltage in the normal operating range.
(1)
Q(U) control based on voltage magnitude at the grid point
Q(U) sag control is a classical voltage control method [20–22], and the control curve
is shown in Figure 3. When the PV grid-connected point voltage is higher than the target
voltage, the PV inverter absorbs reactive power to slow down the rise of the node voltage;
conversely, the PV inverter injects reactive power to slow down the fall of the node voltage;
when the grid-connected point voltage reaches the upper (lower) limit of the network
voltage, the PV inverter absorbs (injects) reactive power according to the maximum reactive
power capacity.
Figure 3. Q(U) control curve.
(2)
Active power output based cosφ (P) control
The cosφ (P) control is a typical reactive power control method to limit the network
voltage lift and excessive reactive power flow in the line, and the German PV grid-connected
standards committee proposed a control curve for distributed PV grid-connected [23], as
shown in Figure 4. When the PV grid-connected power exceeds 50% of the rated active
power, the PV inverter absorbs the reactive power to reduce the network voltage rise, and
at the same time, it should ensure that the power factor at the PV grid-connected point is
maintained within the range of ±0.95. China’s PV power plant grid connection standard
also stipulates that the power factor of the PV grid connection point should be maintained
within the range of ±0.95 [24]. This control method in the low-voltage distribution network
containing a high proportion of household PV, with strict limitations of the grid-connected
power factor of PV, cannot give full play to the reactive power regulation capability of
the inverter.
The current study usually divides the grid-connected PV power generation system
into three scenarios: over-voltage suppression, under-voltage suppression, and optimiza-
tion of network loss and power factor in order to make full use of the reactive voltage
control potential of the inverter [25]. By considering the active distribution network voltage
reactive power coordinated optimization control strategy under different voltage levels [26],



<!-- page 6/24 -->

Energies 2024, 17, 3058
6 of 24
the reactive power output is adjusted in real-time to suppress voltage overruns and fluctu-
ations [27]. Liu et al. [28] proposed a multi-timescale coordinated control method based
on reactive power/voltage optimization at the point of photovoltaic co-coupling (PCC),
which can adaptively regulate the reactive voltage of the PCC according to the real-time
variations of the PV and load outputs. Considering distributed coordinated voltage control
for PV storage, the reactive power of the PV inverter and active power regulation capability
of the storage system are reasonably utilized to avoid the regulation limitation problem
brought by single link control [29].
Figure 4. cosφ (P) control curve.
Simultaneous consideration of PV inverter reactive capacity regulation and reduction
of PV active curtailment are the commonly used voltage control methods. Optimizing the
reactive power capacity of smart PV inverters through a centralized active and reactive
power management system (CARPMS) can alleviate the voltage overrun problem [30].
Utilizing the reactive power capacity of inverters to regulate the system node voltage can
also effectively reduce the system network loss and PV active curtailment and largely
eliminate the impact of distributed renewable energy fluctuations on the system voltage in
the distribution network [31].
Liu et al. [32] propose a power control strategy based on the voltage magnitude and
line impedance at the grid-connection point, which utilizes the residual capacity of the
inverter when the voltage at the grid-connection point exceeds the upper limit to minimize
PV abandonment under the premise of ensuring voltage quality. Considering the capacity
characteristics of PV inverters and node voltage offset limitations, voltage control using
inverter reactive power can reduce the PV grid-connected active curtailment and, at the
same time, achieve the optimization of network losses [33]. Li et al. [34] propose an
adaptive two-layer stochastic approach that introduces a Volt/VAR control (VVC) scheme
to ensure voltage safety and efficient operation and a conditional value-at-risk (CVaR)
based risk assessment method. The method transforms the original nonlinear problem into
a mixed-integer linear programming (MILP) model, which ensures high-quality solutions
and computational performance and can effectively ensure system safety and reduce
operational costs and risks.
Zhang et al. [35] address the reactive power output of PV power supply seriously
threatening the reliable operation of PV inverter and proposes a data-driven voltage reac-
tive power optimization control strategy considering the reliability of PV inverter, which
utilizes the deep deterministic policy gradient algorithm (DDPG) to realize the voltage
reactive power control, and this method introduces reinforcement learning into voltage



<!-- page 7/24 -->

Energies 2024, 17, 3058
7 of 24
reactive power control of the distribution network so that the PV power supply partici-
pates in the reactive power regulation of the distribution network has become a current
research hotspot.
Advantages of this method:
1.
Full utilization of PV power generation as well as the reactive power output capacity
of PV inverters;
2.
Compared with the traditional centralized voltage regulation method, this method
belongs to the locally distributed control with fast response speed.
Disadvantages of this method:
1.
transmission lines flow through a large amount of reactive current will increase
network losses;
2.
reduce the feeder power factor, affecting the quality of power to the user;
3.
in the PV power generation rated active power conditions, its reactive power output
capacity is limited.
The methodology of voltage regulation for Energy storage system configuration and
inverter reactive power regulation section is summarized as shown in Table 1, which
includes the research methodology, concerns, and resources considered.
Table 1. Review of related work: Energy storage system configuration and inverter reactive power
regulation part.
References
Research Method
Focus
Utilized Resources
[8–10]
Two-tier planning model
voltage stability
PV, energy storage
[11]
Layered coordination optimization
Distribution Network Dispatch
Energy storage, load
[12–14]
Segmented compensation strategy
Voltage stability,
Reduced power fluctuations
PV, energy storage
[15]
Two-stage distributed control
energy storage charge state
PV, energy storage
[16]
deep reinforcement learning
voltage stability
PV, energy storage
[25–27]
Delineate optimization scenarios,
Distinguish voltage levels
Suppressing voltage overruns
PV
[28]
Coordinated control on multiple time scales
Adjustment of reactive voltage
PV, load
[29]
Distributed coordinated voltage control
Solving the problem of limited
control in a single link
PV, energy storage
[30,31]
CARPMS
Suppressing voltage overruns
PV reactive capacity,
Active reduction
[32,33]
Regulation using inverter
capacity characteristics
Reducing light abandonment,
Optimize network losses
Photovoltaic reactive capacity
[34]
Adaptive two-layer stochastic
approach, VVC
reduce costs
PV
[35]
Reinforcement learning: DDPG
Data Driver Voltage Control
PV
2.3. PV Active Power Reduction
The working principle of this method is to regulate the voltage by limiting the active
power of distributed PV. In low-voltage distribution networks, the method of controlling
reactive power to regulate voltage is less effective due to the large distribution network
line impedance ratio R/X. Controlling the active power output from distributed PV can
provide better voltage regulation.
As shown in Figure 5. represents the relationship between output active and reactive
power and voltage when local sag control is used for distributed PV. In the figure, Un
denotes the rated voltage of the node, and UUV and UOV denote the corresponding voltage
thresholds when the node has the risk of undervoltage and overvoltage, respectively. When



<!-- page 8/24 -->

Energies 2024, 17, 3058
8 of 24
the voltage at the grid point is lower than UOV, the distributed PV is running in MPPT
mode, and when the voltage at the grid point is higher than UOV, the distributed PV
reduces the active power, and Pcut represents the active power reduction.
Figure 5. Active and reactive power curves for distributed PV local control.
Reducing PV active power output through a voltage control strategy can realize
the effect of suppressing overvoltage, but only reducing PV active power output can
not improve the PV consumption-ability of the distribution network [36]. The currently
used method is to combine reactive power regulation and active power reduction, which
can provide a better voltage regulation effect. For example, Jameel et al. [30] propose a
centralized active and reactive power management system (CARPMS) to optimally utilize
the reactive power capacity of smart PV inverters and to control the amount of active power
curtailment in order to mitigate the voltage overrun problem. When the reactive power
capacity of the inverter is insufficient, a portion of the active power output from the PV is
curtailed according to priority to meet the reactive power demand of the system. At night
or when the system’s reactive power deficit is more severe, the PV inverter operates as a
static synchronous compensator [37].
Voltage control through in situ adaptive, considering active reduction and reactive
power regulation, can provide a better voltage regulation effect in real LV distribution
networks [38]. Utilizing smart inverters of PV systems to compensate reactive power in
real-time can reduce active curtailment and voltage distortion and reduce the requirements
on communication infrastructure as an advantage of voltage regulation [39].
Ma et al. [40] stabilize the output by improving the constant power control strategy
so that the active power curtailment control works even when the light intensity changes
drastically. Considering accurate prediction of the active power limit, real-time modulation
of the active power output of PV arrays can reduce the probability of voltage overruns
occurring [41].
When there is a risk of voltage overrun in the distribution network, the PV power
supply sets its active power limit value injected into the distribution network in real-time,
and the excess PV power is temporarily stored by relying on the energy storage equipment,
which can prevent voltage overrun fundamentally, and utilize the residual capacity of the
inverter to absorb the inductive reactive power and reduce the voltage of the distribution
network [42]. Considering the control strategy combining active curtailment and on-load
tap changer to solve the voltage overrun problem becomes a new research idea [43].



<!-- page 9/24 -->

Energies 2024, 17, 3058
9 of 24
Advantages of this method:
1.
As the distribution network has the characteristic of larger R/X, the active power
reduction has better regulation of overvoltage.
2.
This method can reduce the uneven distribution of current and voltage and reduce the
line loss and grid loss; there is no problem with network loss increase, feeder power
factor reduction, or line overload caused by reactive power regulation.
Disadvantages of this method:
1.
An unreasonable selection of parameters will lead to an increase in the amount of
active power reduction and losses.
2.
Active power reduction will affect the economy of distributed PV.
3.
The energy utilization efficiency of the PV system will be reduced, and the PV con-
sumption capacity will be reduced.
2.4. On-Load Regulator Transformer Tap Action and Distribution Network Reconfiguration
As shown in Figure 6, the principle of the tap adjustment method of the on-load
regulator transformer is to realize the voltage adjustment by adjusting the tap position of
the high-voltage winding to adapt to the changes of the incoming power supply and the
electrical load in the operation of the system when the voltage overrun problem occurs in
the line [44]. The purpose of adjusting the output voltage of the low-voltage winding at
any time is realized by switching the tap switch at any time and adjusting the tap position
of the high-voltage winding under the condition of carrying load to ensure the quality of
the output voltage.
Figure 6. On-load Tap Changer Operation in Transformer. The green arrow refers to the meaning of
the transformer high voltage side tap gradually decreasing from high to low, and is distinguished
from the black diagram of the five taps.
Yuan et al. [45] analyze the principle of the double-core symmetrical phase-shifting
transformer (DS-PST) and the application of trend regulation, which can transfer the active
power transmitted by high load-rate lines to low load-rate lines so as to make the distribu-
tion of system trend more balanced and effectively improve the transmission capacity of the
power system. Changing the control strategy of the on-load tap changer (OLTC), the first
controller (ANFIS-OC) in this strategy solves the voltage overrun problem due to low X/R
ratio and PV distributed generation by calculating the OLTC reference voltage based on
the minimum and maximum voltage magnitude of the grid [46]. Tang et al. [47] innovate
the voltage control architecture for distribution networks by considering the modeling of
the discrete control of on-load tap-changer transformers, which is applicable to the coordi-
nated control of a fundamentally developed network, as well as to the optimization-based
centralized control of a network with a fully articulated system.
Since the traditional OLTC for control means can no longer resist the impact of high
penetration distributed power sources on the grid, the dynamic reconfiguration of distribu-
tion networks containing distributed power sources is investigated. Transformer economic



<!-- page 10/24 -->

Energies 2024, 17, 3058
10 of 24
operation as a measure of grid energy saving and consumption reduction, distribution
network reconfiguration, distributed power reactive power coordination, and optimization
can make the distribution network a wider range of improved energy efficiency.
The integrated use of real-time phase measurement unit (PMU) data to coordinate the
optimal control of the battery energy storage system (BESS), OLTC, and solar PV inverters,
reduce the OLTC tapping operation, and increase the service life of the OLTC and BESS is a
feasible solution to improve the system performance [48]. Coordinated voltage regulation
by regulating the reactive power of inverter-type distributed power supply (DG) and OLTC
can reduce the operational burden of OLTC, using curve fitting techniques to achieve stable
regulation within the voltage range, solving the voltage overrun problem in the distribution
network, and providing a feasible way to improve the performance of the distribution
system [49].
In recent years, artificial intelligence algorithms based on randomization techniques
have been widely used in the field of optimization. Among the examples of intelligent
optimization algorithms applied to distribution network reconfiguration, it is summarized
that they mainly include artificial neural network algorithm, simulated annealing algorithm,
forbidden search algorithm, ant colony algorithm, particle swarm optimization algorithm,
and genetic algorithm, differential evolutionary algorithm, etc., and the use of a new type
of hybrid algorithms to carry out the reconfiguration of the distribution network becomes a
hot spot of today’s research [50].
Cui et al. [51] proposed a PV admittance capacity improvement model based on
network reconfiguration and reactive voltage regulation. Controllable distributed power
sources, OLTCs, castable capacitors, and distribution network reconfiguration are used as
regulation objects to effectively improve the PV admittance capacity of the distribution
system through distribution network reconfiguration and reactive voltage regulation. The
coordinated optimization of OLTCs, distribution static compensators (D-STATCOM), distri-
bution generation (DG), and distribution network reconfiguration can maximize the annual
cost savings and improve the voltage profile [52].
Advantages of this method:
1.
Adjusting the tap switch position of the on-load voltage regulator allows the trans-
former to be carried out in real time, and the system can respond quickly to voltage
overruns caused by fluctuations in PV power, thus improving the stability of the
power grid.
2.
The adjustment of the tap switch position of the transformer can be adapted to the
different operating conditions and the changes in the output of PV power, thus making
the system more flexible.
3.
It is economical and does not require additional equipment to realize voltage control.
4.
Transformer regulation can be combined with distribution network reconfiguration to
improve the efficiency of energy utilization.
Disadvantages of this method:
1.
Adjustment of the switch position of the on-load regulator transformer will lead to
transformer losses and current and magnetic losses will be generated during the
adjustment process, affecting the overall efficiency of the system.
2.
Although it is an instantaneous adjustment, the response speed of the on-load regula-
tor transformer is relatively slow.
3.
Frequent adjustment of the switch position of the transformer taps affects the life of
the equipment, and it is necessary to consider the durability of the equipment and the
cost of maintenance.
The methodology of PV active power reduction and OLTC and distribution network
reconfiguration section is summarized as shown in Table 2, which includes the research
methodology, concerns, and resources considered.



<!-- page 11/24 -->

Energies 2024, 17, 3058
11 of 24
Table 2. Review of related work: PV active power reduction and OLTC and distribution network
reconfiguration section.
References
Research Method
Focus
Utilized Resources
[36,37]
Determine active cuts based
on prioritization,
Inverter as static synchronous compensator
Meet system reactive power
requirements
PV, active reduction
[38,39]
Local adaptive voltage control
Reduced active cuts,
Reduced communication
requirements
PV, active reduction
[40,41]
Power prediction methods
voltage stability
PV, active reduction
[42]
Utilization of energy storage systems to
store electrical energy
Preventing voltage overruns
PV, energy storage,
active reduction
[43]
OLTC combined with active reduction
voltage stability
PV, active reduction, OLTC
[45]
trend regulation
Enhancement of power system
transmission capacity
PV, OLTC
[46]
Improved control strategies
Preventing voltage overruns
PV, OLTC
[47]
Distributed coordinated voltage control
Solving the problem of limited
control in a single link
PV, energy storage
[48,49]
Coordinate multiple resources with PMU
Optimize control
Enhances system performance,
Voltage Stability
PV, Energy Storage, OLTC
[51,52]
Regulation of multiple resources,
Modeling PV Consumption
Capacity Enhancement
Cost savings,
Improved voltage
PV, OLTC, network
reconfiguration
2.5. Comparative Analysis of Methods
According to the previous section, it can be seen that the above four types of methods
are able to solve the voltage overrun problem caused by high penetration distributed PV
access, but each method has its own advantages and limitations, and the comparative
analysis is shown in Table 3.
Table 3. Comparative analysis of four types of voltage regulation methods.
Energy Storage System
Configuration
PV Inverter
Reactive Power
Regulation
PV Active Power
Reduction
OLTC and
Distribution Network
Reconfiguration
Implementation costs
high
low
relatively low
low
Responsiveness
quick
quick
quick
slow
Adjustment
performance
excellent
excellent
relatively
excellent
poor
Network loss
minimize
rise
minimize
invariant
Economic gain
high
low
relatively low
high
Adjusting the difficulty
relatively hard
easy
easy
difficult
In summary, when solving the voltage overrun problem in the distribution network,
a single voltage regulation method has limited effect and is insufficient to meet the grid
connection requirements of high penetration distributed PV in most cases. Combining the
advantages and disadvantages of each voltage regulation method, research scholars have
proposed a coordinated control strategy with multiple methods.
For example, Zhang et al. [53] propose a coordinated voltage control strategy for OLTC
and energy storage system, which utilizes OLTC and energy storage system to achieve



<!-- page 12/24 -->

Energies 2024, 17, 3058
12 of 24
coarse and fine regulation of distribution network voltage, respectively, and effectively
suppresses voltage overruns through two-phase operation optimization with different time
scales and regulation ranges.
Tang et al. [54] analyze that the inverter-based reactive power control strategy has
limited voltage regulation capability, resulting in network loss and power factor index
degradation, while the storage-based active control strategy can relatively effectively reg-
ulate the voltage and optimize the network loss but a single active control has a greater
demand for storage capacity, which is not conducive to optimizing the network power
factor. Based on this, a coordinated control strategy of inverter reactive power and storage
active power is proposed, which can effectively regulate the network voltage, comprehen-
sively optimize the technical indexes of the grid, and reduce the requirement of energy
storage capacity.
Li et al. [42] propose an integrated control strategy of PV active reduction and inverter
reactive power. In case of voltage overrun risk in the distribution network, the PV power
supply sets its active power limit value injected into the distribution network in real-time to
prevent voltage overrun fundamentally and, at the same time, utilizes the residual capacity
of the inverter to absorb inductive reactive power in order to further reduce the voltage of
the distribution network and avoid unnecessary active reduction.
As shown in Figure 7, it can be seen that the mainstream method of solving the voltage
overrun problem in LV distribution networks today is to coordinate the control strategy
for voltage regulation through multiple methods, but there are still some problems to be
considered under such methods:
(1)
A PV grid-connected low voltage distribution network with a high proportion of poor
communication and measurement conditions affects the coordination and control
capability of the distribution network itself, often requiring the simultaneous use of
PV inverters, energy storage, OLTC, and other devices to suppress voltage overruns
and voltage fluctuations. When multiple devices are regulated at the same time,
there is a large difference in the regulation effect achieved by different regulation
sequences; while the economic cost of a single regulation of OLTC is high, the degree
of coordination of the source network and load needs to be improved, and the research
on the control model that considers the economic factors are still relatively small, and
the regulation sequences of the individual devices as well as the regulation economy
need to be further investigated.
(2)
The control objectives and scenarios of most of the current control methods are rel-
atively single, i.e., the control does not fully consider the operating scenarios of the
PV, and there is the problem of insufficient consideration of the network operation
index. Nowadays, a large number of new elements are integrated into the load side,
the load resources are more complex and variable, and it is more difficult to obtain
the basic data of the scaled flexible resources. However, in terms of data acquisition,
the load usually adopts probabilistic statistical data rather than measured data, which
is not representative of today’s changing load resources; in terms of model construc-
tion, simplified models are usually adopted, and the dynamic characteristics are
poorly displayed.
(3)
Compared with a low-voltage AC distribution network, a low-voltage DC distribution
network has the characteristics of small line loss, low cost, etc., household photovoltaic
and energy storage is also easier to access, and at the same time, has better power
supply reliability and power quality. The transition from low-voltage AC distribution
networks to low-voltage AC/DC hybrid distribution networks has become one of
the current trends in network development. The application of some new power
electronic equipment in low-voltage distribution networks is receiving attention, and
the application of new equipment in low-voltage distribution networks has to be
supplemented and improved.
(4)
Policy factors are the main driving force in promoting distributed household PV grid
connections, but they will eventually be regulated by the market mechanism. Based



<!-- page 13/24 -->

Energies 2024, 17, 3058
13 of 24
on certain price elements, the PV grid connection network voltage control and other
issues will be more reasonable.
Figure 7. Voltage regulation methods and analysis in LV distribution networks.
3. Flexibility of LV Distribution Networks Resource Voltage Regulation
With the large-scale grid connection of distributed PV, the source and load ends of the
power system show a high degree of uncertainty, the stable operation mechanism of the
power system is more diversified and complex, and the overall characteristics of the high
proportion of new energy power system have changed dramatically. The high penetration
rate of a high proportion of distributed PV leads to the lack of flexibility of the system in
local time, and it is difficult to guarantee the safe, reliable, and economic operation of the
new power system by relying only on the power side regulation. Demand-side resources
have the characteristics of wide distribution, small single capacity, and diversified means
of regulation, etc. The formation of the cluster effect can promote the development of a
power system from “source follows load” to “source-load interaction”, which can further
satisfy the demand for distributed power consumption.
The voltage regulation methods for high PV penetration in LV distribution networks
in the previous section have been introduced for the three types of flexibility resources
of source, network, and storage, i.e., considering the distributed PV itself for voltage
regulation, OLTC and distribution network reconfiguration for voltage regulation, and
energy storage system configuration for voltage regulation. Through comparative analysis,
it can be seen that the three types of flexibility resources, namely source, network, and
storage, have been widely used in distribution network voltage regulation, but there are
insufficient advantages and obvious defects in using one method alone. While analyzing
from the perspective of flexibility resources, load-side resources have become one of the
main regulating resources of the new power system, but the current study introduces
less about the participation of load-side flexibility resources in voltage regulation of LV



<!-- page 14/24 -->

Energies 2024, 17, 3058
14 of 24
distribution networks and advancing the application of load-side resources in voltage
regulation of LV distribution networks is the focus of future research. The following section
focuses on the analysis of load-side flexibility resources and describes the important role of
load-side resources in voltage regulation from three parts: the important role of load-side
resources, the development trend of load-side resources, and the proposal to promote the
coordination of source-network-load-storage flexibility resources.
3.1. Load-Side Flexibility Resource Voltage Regulation
Domestic and international views on flexibility resources are basically consistent,
with conventional power plants, energy storage, interconnected grids, and the demand
side being the main components of power system flexibility resources. However, the
rapid expansion of large-scale renewable energy grid connections and various end-use
electrification makes the power system pay more attention to the load-side flexibility, that is,
the demand-side flexibility. According to the experience of European power grid operation
and scheduling, fully utilizing the flexibility potential of demand-side resources can solve
the net load fluctuation problem caused by distributed power supply access and other
factors, make up for the lack of flexibility of the distribution network, and significantly
improve the economy, reliability, and flexibility of power system operation.
Demand-side flexibility resources mainly include adjustable loads, electric vehicles,
user-side energy storage, and other small and decentralized “producers and consumers”,
and with the continuous improvement of user-side intelligence and automation, demand-
side resources can give full play to their flexible and controllable potential to a greater extent.
Load-side resources have the ability to actively respond to system power fluctuations, and
controllable loads, as one of the means of demand-side management, can provide the
system with demand-side flexibility resources, and their rapid response capability can
meet the requirements of system load demand changes. However, due to the problems
of scattered demand-side resources, large differences in user energy use, and small size
of adjustable load, it is difficult for demand-side flexible resources to directly participate
in the centralized market, provide auxiliary services through aggregator agents and other
forms, and realize the unified management of internal decentralized resources by means of
advanced communication technology in order to realize the voltage regulation function.
The literature [55] proposes a game model between the distribution system and load
aggregator, where both the distribution system and load aggregator can obtain optimal
economic benefits and alleviate the pressure of distribution network voltage regulation
through demand response.
Considering the reactive power regulation capability of PV inverters and active distri-
bution voltage regulation based on demand response flexibility, the coordination between
PV inverters and demand response can be fully utilized to improve the power quality and
reliability of the distribution network [56]. In the LV distribution network system with
high penetration of PV power generation and electric vehicles, the bidirectional overrun
problem leads to the difficulty of realizing voltage regulation, and the utilization of flexible
loads through demand response can effectively carry out voltage regulation and reduce the
voltage overrun problem [57].
In [58], a two-layer optimization model for the coordinated allocation of multiple types
of reactive power compensation resources based on a “planning-operation” integration
framework is proposed for the reactive power voltage problem caused by large-scale
distributed new energy access. The framework takes into account the relationship between
“source and load”, and aims to improve voltage quality, consume new energy, and reduce
the impact of power back-feeding to adapt to the future development trend of the power
distribution system.
Power supply, interconnected grid, flexible loads, and energy storage in the power
system can provide a certain degree of flexibility [59]. Under a high proportion of new
energy access, there is the problem of increased volatility and stochasticity on the supply
side of the power system, and the system shortages and abandonment rates also increase



<!-- page 15/24 -->

Energies 2024, 17, 3058
15 of 24
the use of energy storage systems and interconnected grids to carry out the optimal ca-
pacity planning, which can satisfy the demand for system flexibility [60]. Establishing a
collaborative planning model for source-load-storage flexibility resources is a prioritized
option. An expected unserved ramping (EUR) metric is proposed, which can indicate the
amount of flexibility resources that still need to be invoked to meet the system demand
for further collaborative planning [61]. The collaborative planning model of source-load-
storage flexibility resources can meet the needs of distribution network power supply and
consumption by establishing a collaborative planning model [62]. The scheme can fully
consider the supply characteristics and network constraints of various types of resources,
realize the unified and coordinated planning of multiple flexibility resources, and optimize
the economy and flexibility of the power system [63].
Azarnia et al. [64] considered the dependency between power load and distribution
voltage and proposed a Robust Optimization (RO) model to reduce the occurrence of
voltage overruns by using Smart Grid technology, Voltage Reactive Control (VVC) unit
scheduling system equipment in real-time to keep the voltage in the permissible range so
that the cost and voltage overruns can be reduced by decreasing the computational error.
In summary, with the accelerated construction of the new power system, only con-
sidering the use of the power supply side, grid side, energy storage measurement of the
flexibility of resources has been difficult to meet the system’s safe and efficient operation
needs, it is necessary to release the flexibility of the demand-side resources regulating
capacity, “source-load interaction” will become a significant feature of the future power
system. Currently, the utilization of demand-side resources is a major hotspot, and the
form of utilization has gradually evolved from a single orderly power consumption and
energy efficiency management to a variety of functions, active participation, and market-
driven demand response resources. Considering the full utilization of load-side flexibility
resources in distribution network voltage regulation fits the future development trend of
the power system, further improves the flexibility of the distribution network, and plays a
certain effect on the voltage regulation and mitigation of voltage overrun.
3.2. Voltage Regulation of Source, Network, Load, and Storage Flexibility Resources
Each type of flexibility resource in the LV distribution network has its own advantages
and limitations. Focusing on technical characteristics and economics, the cost advantages of
considering demand response and distributed PV’s own regulation capability are obvious,
but the regulation capability is slightly insufficient, e.g., considering distributed PV itself
may result in active power curtailment, while energy storage system configurations have an
advantage in regulating the voltage capability, but they are more expensive. The advantage
of considering multiple flexibility resources for voltage regulation is that demand-side
response and energy storage systems, etc., share the spare capacity of the new power system
under a high proportion of new energy access to meet the power quality requirements
under high penetration of new energy and PV consumption requirements.
However, there are the following problems: the construction cost is slightly higher
than that of the planning scheme without flexibility constraints; the volatility of the new
energy output on the source side will lead to the dual problems of power supply shortage
and new energy abandonment; the regulation effect of considering only a single flexibility
resource is poor, i.e., the degree of coordination among the source, network, load, and
storage is still to be improved. For example, considering only load-side flexibility resources,
the voltage regulation range is small, and it is difficult to solve the problem of voltage
overrun in both directions.
Further improving the degree of coordination of source, network, load, and storage
flexibility resources, as well as scientifically and reasonably playing the role of demand-side
resources, have become the focus of attention for the high-quality development of electric
power in the medium and long term. The following section will discuss the important role
of load-side resources, the development trend of load-side resources, and the proposal to
promote the coordination of source, network, load, and storage flexibility resources.



<!-- page 16/24 -->

Energies 2024, 17, 3058
16 of 24
3.2.1. The Important Role of Load-Side Resources in New Power Systems
(1) Ease the contradiction between power supply and demand. With the acceleration
of the demand side development process, especially the deep integration of the power
network and transportation network, the difficulty of balancing supply and demand in the
power system gradually increases, and short-term load spikes occur frequently. Due to the
low substitution effect of photovoltaic capacity, under the trend of new energy as the main
source of power increment, the active play of load-side resources in power peak shaving
and valley filling will help to guarantee the balance of power supply and demand.
(2) Promote new energy consumption. PV power generation has strong randomness,
volatility, and intermittency. In the context of large-scale access to the grid by new energy
sources, relying solely on new power-side regulation resources to support new energy
consumption will face problems such as lower equipment utilization efficiency and higher
electricity costs. Load-side resources can respond up to the second level, with excellent
regulation capabilities, such as electric vehicles, user-side energy storage, central HVAC and
other demand-side resources can quickly respond to new energy ultra-short, short-cycle
scale regulation needs; traditional industrial and commercial loads and other load-side
resources can be based on incentives to actively participate in the system within the day
regulation needs; hydrogen and other emerging load-side resources and the new energy
depth of the coupling can meet the new energy multi-day or longer time scales, the new
energy or longer time scales. Emerging load-side resources, such as hydrogen energy, are
deeply coupled with new energy to meet the multi-day or longer time-scale regulation
demand of new energy [65].
(3) Enhance the energy efficiency level of the whole society. Load-side resources are
important intrinsic resources for the power system to tap its own energy-saving potential.
According to the classification of saving effect, they can be divided into adjustable power
resources and saving power resources, the former through load transfer, load regulation,
load interruption, and other regulation methods to replace or reduce the power supply,
power grid type of construction investment, and the latter through process optimization,
technological improvement, management enhancement, and other means to save demand-
side power and reduce the level of energy consumption.
3.2.2. Trends in Future Development of Load-Side Resources
(1) Load-side resources will become one of the main regulating resources of the new
power system. With the accelerated construction of the new power system, load-side
resources will gradually be elevated to the same status as the supply side, playing an
important role in ensuring the balance of power supply and demand and supporting the
consumption of new energy. Load-side resources can be adjusted with huge potential, and
some traditional industrial and commercial loads will still be the main load-side regulation
resources in the future due to their large scale and high electricity price sensitivity; emerging
load-side resources such as electric vehicles and customer-side energy storage, which are
fast-responsive and highly flexible, will certainly play an increasingly important role [66].
(2) Digitalization and intelligence accelerate the efficient use of load-side resources.
At present, big data, cloud computing, blockchain, 5G communication technology, and
other fields continue to innovate and breakthroughs, and in the future, with the massive
load-side resource access system, load-side resource digitization and intelligence become
an inevitable development trend, deepen the data analysis in the fields of user behavior
analysis and prediction, resource potential mining, accurate response implementation, etc.,
and strengthen the resource aggregation and invitation, multi-user interaction, source net-
work, load and storage coordination control and other aspects. The intelligent application
provides key support for the scientific utilization of load-side resources [67,68].
(3) Realize the deep integration of multiple energy sources on the load side. With the
acceleration of the development process, a new generation of energy use methods such as
integrated energy, vehicle-network interaction, microgrids, and virtual power plants are
flourishing, and the degree of coupling between multiple energy systems on the load side



<!-- page 17/24 -->

Energies 2024, 17, 3058
17 of 24
has increased. The boundaries of energy producers and energy consumers are gradually
blurred, and the power network, heat network, and transportation network to achieve
in-depth integration, electricity, heat, hydrogen, etc., to the power system as a hub for
mutual conversion and mutual aid, load-side resources will play an important role in
promoting the consumption of clean energy and the green and low-carbon transformation
of energy [69].
(4) The degree of marketization of load-side resources will be greatly increased. Load-
side resources are close to users and have natural marketization conditions. In the future,
various types of load-side resources will gradually transition from incentive compensation
to active participation in power market-oriented transactions, and the willingness and
ability of load-side resources to participate in system regulation will be accelerated. By
participating in the electric energy market, auxiliary service market, capacity market, and
other trading varieties, the commodity price attribute of load-side resources in the new type
of power system has been fully embodied, and the optimization and allocation efficiency of
load-side resources has been effectively enhanced [70].
3.2.3. Recommendations for Promoting the Coordination of Source, Network, Load, and
Storage Flexibility Resources
(1) Establish a long-term load-side resource incentive mechanism. Following the prin-
ciple of fairness and reasonableness, establish a long-term incentive mechanism, cultivate
the sense of participation of market players, guide large industrial and commercial users to
directly participate in demand response through the direct transaction mode of large users,
encourage power sales companies and comprehensive energy service companies to take on
the role of load aggregators, and promote the model of virtual power plants in cities with
more abundant electric vehicle and commercial building load resources. Multi-channel
mobilization of incentive funds, the formation of a long-term stable pool of funds, and the
gradual transformation of incentive-based demand response from a temporary and emer-
gency initiative to a normalized means of regulation will help to promote the coordinated
development of flexibility resources such as load-side resources [71].
(2) Improve the participation of load-side resources in the market mechanism. Enrich
the electric power spot market trading varieties, study and establish the load-side resources
to participate in the energy market, auxiliary services, capacity market organization mode,
establish and improve the market access mechanism and other content, improve the de-
mand response market-oriented trading regulatory system, and promote the formation
of the supply-side and demand-side joint participation, fair competition, market-oriented
trading model [72].
(3) Promote the technological progress of load-side resources. Vigorously develop
automatic demand response technology, load aggregation technology, power saving mea-
surement and verification technology, intelligent power consumption facilities, and intel-
ligent load control technology. Explore the “Internet+” intelligent power consumption
technology model and organization model. Through the extensive deployment of data col-
lection terminals for user information, grid information, and power generation information,
break the data barriers of source-network-load-storage, integrate system operation, market
transaction, and user electricity consumption data, improve the capacity of load-side big
data analysis, and realize the intelligent regulation and control of load-side resources [73].
In summary, the flexible adjustability of the load side in the LV distribution network
flexibility resources is particularly important. Voltage regulation through source, network,
load, and storage flexibility resources is shown in Figure 8. Consumption of PV in the
LV distribution network not only needs to be balanced locally but also should consider
inter-regional inter-supply and overall coordination of consumption through multi-energy
complementary and regional interconnection to improve the capacity of PV consumption
so as to dissolve the risk of network voltage overruns. Voltage control in the low-voltage
distribution network containing high-penetration distributed PV requires rational planning
of flexibility resources, considering the important role of load-side resources, rationally



<!-- page 18/24 -->

Energies 2024, 17, 3058
18 of 24
promoting the further coordinated development of source, network, load, and storage
flexibility resources, and fully exploring the flexibility potential of each side of the source-
network-load-storage as well as the grid’s role in supporting the flexibility of transmission,
in order to improve the flexibility and economy of the system [74].
 
Figure 8. Multi-flexibility resource voltage regulation.
4. Problems and Recommendations for Voltage Control
4.1. Challenges
Distribution grid voltage regulation methods containing high penetration distributed
PV and some of the problems in the mainstream methods mentioned above are as follows:
(1) When voltage regulation is carried out using a coordinated control strategy with
multiple methods, there is a problem of not considering the regulation sequence and
economy of multiple methods, and although the purpose of voltage regulation is achieved,
there are problems such as poor economy and low efficiency.
(2) In the process of low voltage distribution network modeling, the existing research
methods simplify the data, model, and parameter selection, lack of consideration of PV op-
eration scenarios, and have the problems of insufficient consideration of network operation
indexes and oversimplification of data, modeling and parameter selection.
(3) In the face of the sharp increase in electricity consumption of the whole society,
subject to environmental protection, geography, and other factors, it is difficult to take the
way of large-scale planning and construction of new lines to expand capacity and there is
the problem that the existing line structure can not meet the demand for electricity.
(4) The current household distributed PV consumption problem has a diversified
subject of interest; distribution system operators, load aggregators, and individual users



<!-- page 19/24 -->

Energies 2024, 17, 3058
19 of 24
have become the subject of interest, and how to maximize the benefits among multiple
subjects is a problem.
(5) Privacy leakage and communication inefficiency during voltage regulation in low
voltage distribution networks.
(6) In the process of voltage regulation, the degree of coordination of source, network,
load, and storage flexibility resources is insufficient, which makes it difficult to realize
the economic optimization and the best voltage regulation effect at the same time and the
consideration of multiple flexibility resources for voltage regulation is accompanied by
the complication of mathematical modeling and the increase in the difficulty of solving
the problems.
4.2. Recommendations to Address the above Issues
(1) Consider the regulation sequence and economy of coordinated control of multiple
voltage regulation methods. For the voltage problem caused by a high percentage of
PV access, considering the combination of multiple regulation methods can achieve the
purpose of cost reduction and efficiency improvement. Further research and additions
should be made in terms of improving the degree of coordination of the source network
and load, the regulation sequence of each device and the economics of regulation, and the
control model that considers economic factors.
(2) Accurately obtain basic data and fully consider PV operation scenarios and distribu-
tion network operation indexes. Further research is necessary to establish a multi-scenario,
multi-objective control model in low-voltage distribution networks containing a high
proportion of household PV power generation, taking into account the suppression of
network risk and optimization of network operation indexes, accurately obtaining basic
data, reasonably constructing the model, and improving the accuracy of the analysis results.
(3) Focus on new power electronic equipment low-voltage distribution network struc-
ture transformation. Solid-state tap transformers and other new power electronic equip-
ment have superior characteristics. The opening and closing operation of the thyristor can
be adjusted to the transformer ratio to avoid the wear and tear of the taps and enhance
the voltage regulation of the distribution network. The low-voltage AC distribution net-
work transitioned to a low-voltage AC and DC hybrid distribution network in the current
trend of network development. The low-voltage distribution network basically used a
no-load voltage regulator transformer. For the distribution network containing distributed
photovoltaic PV penetration rate will be further increased in the future, the transition of a
low-voltage AC distribution network to a low-voltage AC-DC hybrid distribution network
should be considered to carry out the OLTC transformation of low-voltage distribution
network and the application of new type of power electronic devices, which can jointly
complete the voltage regulation of low-voltage distribution network and ensure the quality
of power supply to the users.
(4) Considering load-side demand response and enhancing the economic and price
attributes of voltage control in low-voltage distribution networks. Currently, the state
has released a number of policies that are favorable to distributed PV construction, but
ultimately, distributed PV construction will be regulated by the market mechanism, and
the subject of interest in household PV consumption will become diversified. It can be
considered to establish a game and cooperation model of PV grid integration among
different interests, and related research will play a role in promoting PV grid integration.
For example, the distribution system operator influences the time of use of electricity
by subsidizing the reduction of the frequency of voltage violations. Load aggregators
help users schedule demand during the subsidy period, and individual users achieve low
electricity prices to maximize the profit of each subject.
(5) Focus on privacy protection techniques, enhance communication efficiency, and
consider artificial intelligence algorithms to cope with voltage overruns in distribution
networks. With the increasing share of distributed PV in the distribution network, voltage
overrun solutions combining front-end technologies and existing regulation methods need



<!-- page 20/24 -->

Energies 2024, 17, 3058
20 of 24
to be considered. The literature [75] considers the impact of distributed renewable energy
access on the voltage of low-voltage distribution networks and proposes a deep reinforce-
ment learning-based scheduling strategy for energy storage devices. The combination of
deep reinforcement learning algorithm and energy storage device scheduling is utilized
to mitigate the voltage overrun problem. The literature [76] proposes a reactive power
optimization method for distribution networks based on multi-intelligent body deep re-
inforcement learning. Multi-intelligent body DDPG is used to coordinate the control of
multiple controllable devices such as capacitors, on-load voltage regulator transformers,
and distributed power supplies. The literature [77] proposes a data-driven distributed
control method based on coherent multi-intelligence deep reinforcement learning, where
each inverter is modeled as an intelligent body, each intelligent body is responsible for
the controllable devices in a region, and the intelligences communicate with each other
to improve the coordination of control commands. It has high communication efficiency
and robustness to communication faults. Further exploring the application of front-end
technology in distribution network voltage management is one of the current research
hotspots, such as artificial intelligence, deep reinforcement learning, etc., to improve the
distribution network voltage regulation capability.
Voltage control methods applying multi-intelligent body learning, as mentioned in
the literature [78], consider the latest learning algorithms for voltage control in order to
drastically reduce the communication requirements and better protect the user’s privacy
to fulfill the current requirements of multi-source data fusion techniques considering
privacy protection.
(6) For the problem of insufficient coordination of source, network, load, and storage
flexibility resources, a comprehensive system model covering the characteristics, constraints,
and interactions of different resources is needed for effective coordinated scheduling, which
is still one of the research hotspots. Distributed control strategies can be used to realize the
coordinated management of flexible resources. The system is decomposed into multiple
subsystems, and distributed control algorithms are implemented on each subsystem to
achieve optimal management of the overall system. Advanced optimization algorithms are
used to achieve the goals of economic optimization and the best voltage regulation effect.
5. Conclusions
This review addresses the voltage overrun problem caused by high penetration dis-
tributed photovoltaic (PV) access to low-voltage distribution networks (LVDNs) and com-
prehends domestic and international research on voltage control methods for LVDNs.
Firstly, the working principles of four voltage control methods, namely, energy storage
system configuration, regulating reactive power output of PV inverters, limiting active
power output of PV, OLTC, and distribution network reconfiguration, are introduced, and
the characteristics of each method are presented in the form of a table, which summarizes
the advantages and defects of each method, and the four types of methods are compared
and analyzed according to different criteria. The use of a single voltage regulation method
has the problem of insufficient advantages and obvious defects, which is insufficient to
meet the requirements of high penetration rate distributed PV grid connection in most
cases, and the coordinated voltage control through multiple flexibility resources has become
the current mainstream voltage regulation scheme.
After that, voltage regulation is considered from the perspective of flexibility resources,
and the four voltage control methods in the previous section have been introduced for the
three types of flexibility resources, i.e., considering distributed photovoltaic (PV) voltage
regulation by itself, OLTC tap action and distribution network reconfiguration regulation,
and energy storage system configuration regulation. The three types of flexibility resources,
namely, source, network, and storage, have been widely used in distribution network
voltage regulation, while load-side resources have become one of the main regulation
resources of the new type of power system, but the current study introduces less about
the participation of load-side flexibility resources in LV distribution network voltage regu-



<!-- page 21/24 -->

Energies 2024, 17, 3058
21 of 24
lation, and advancing the application of load-side resources for voltage regulation in LV
distribution networks is the focus of future research.
Then, the important role of load-side resources for voltage regulation is described in
three parts, namely, the important role of load-side resources, the development trend of
load-side resources, and the suggestions for promoting the coordination of source-network-
load-storage flexibility resources, aiming to promote the application of load-side resources
for voltage regulation in LV distribution networks and to combine them with the three types
of flexibility resources of source-network-storage to achieve the purpose of controlling the
cost and improving the efficiency of voltage regulation.
Finally, recommendations and solutions are presented to address the technical chal-
lenges of voltage regulation in LV distribution networks containing high penetration
distributed PV. In the context of today’s new power systems emphasizing the interaction
of source, grid, load, and storage, new technologies and methods for solving the voltage
problems in LV distribution networks are envisioned, with the hope that this article can
provide some references for future research in this field.
Author Contributions: J.Z.: Conceptualization, Methodology, and Writing—review and editing. X.G.:
Investigation, Extensive literature review, Writing—original draft. H.S.: Methodology, Writing—review
and editing. Y.L.: Writing—review and editing. L.W.: Conceptualization and Methodology. C.Y.:
Conceptualization and Methodology. Y.X.: Conceptualization and Methodology. All authors have
read and agreed to the published version of the manuscript.
Funding: This research was funded by the Scientific Research Program for Colleges and Universities
in Hebei Province (QN2022028).
Conflicts of Interest: The funders had no role in the writing of the manuscript. The authors declare
no conflicts of interest.
References
1.
Zhang, Z.; Lyu, Q.; Zhang, J. Research Progress and Prospect of Distributed PV Power Generation Technology under the Goal of
emission peak and carbon neutrality. Sol. Energy 2023, 17–21. [CrossRef]
2.
National Development and Reform Commission; National Energy Administration. Renewable Energy Development Plan for the 14th
Five-Year Plan; NDRC [2021] No. 1445; National Development and Reform Commission: Beijing, China, 2022.
3.
Huang, S.; Ding, X.; Gao, Q.; Li, X.; Dong, Z. Active-Reactive Power Coordination Optimization in Distribution Network
Interconnected with Photovoltaic-Hydrogen-Energy Storage Systems. South. Power Syst. Technol. 2018, 12, 44–51.
4.
Cai, Y.; Tang, W.; Zhang, B.; Li, T.; Wang, Z. A Two-stage Volt-var Control in LV Distribution Networks with High Proportion of
Residential PVs. Power Syst. Technol. 2019, 43, 1271–1280.
5.
Ghosh, S.; Rahman, S.; Pipattanasomporn, M. Distribution voltage regulation through active power curtailment with PV inverters
and solar generation forecasts. IEEE Trans. Sustain. Energy 2017, 8, 13–22. [CrossRef]
6.
Zhou, C.; Gao, Q.; Liu, H. Real-time Voltage Control Strategy for Distribution Network Based on Demand Response Coordination
of Transformer and Load. Power Capacit. React. Power Compens. 2021, 42, 143–150.
7.
Chaudhary, P.; Rizwan, M. Voltage regulation mitigation techniques in distribution system with high PV penetration: A review.
Renew. Sustain. Energy Rev. 2018, 82, 3279–3287. [CrossRef]
8.
Cheng, Y.; Wang, S.; Zhao, Q.; Wang, K. Energy storage system planning method for improving photovoltaic hosting capacity in
cyber-physical system. In Proceedings of the 2nd International Conference on Electronic Materials and Information Engineering
(EMIE 2022), Hangzhou, China, 15–17 April 2022; pp. 1–5.
9.
Zhang, Y.; Yang, Y.; Zhang, X.; Pu, W.; Song, H. Planning Strategies for Distributed PV-Storage Using a Distribution Network
Based on Load Time Sequence Characteristics Partitioning. Processes 2023, 11, 540. [CrossRef]
10.
Wang, C.; Zhang, L.; Zhang, K.; Song, S.; Liu, Y. Distributed energy storage planning considering reactive power output of energy
storage and photovoltaic. Energy Rep. 2022, 8, 562–569. [CrossRef]
11.
Zhang, T.; Zhou, X.; Gao, Y.; Zhu, R. Optimal Dispatch of the Source-Grid-Load-Storage under a High Penetration of Photovoltaic
Access to the Distribution Network. Processes 2023, 11, 2824. [CrossRef]
12.
Chen, H.; Cheng, J.; Li, Z.; Abu-Siada, A.; Li, H. Distributed photovoltaic power fluctuation flattening strategy based on hybrid
energy storage. Front. Energy Res. 2023, 11, 1303522. [CrossRef]
13.
Li, Y.; Cai, H.; Wang, K.; Sun, X.; Zhou, L. Sequence Optimal Configuration of Distributed Energy Storage for Improving Voltage
Quality of Unbalanced Distribution Network. Electr. Power Constr. 2022, 43, 87–95.
14.
Zhao, B.; Ren, J.; Chen, J.; Lin, D.; Qin, R. Tri-level robust planning-operation co-optimization of distributed energy storage in
distribution networks with high PV penetration. Appl. Energy 2020, 279, 115768. [CrossRef]



<!-- page 22/24 -->

Energies 2024, 17, 3058
22 of 24
15.
Zhang, B.; Tang, W.; Cai, Y.; Wang, Z.; Li, T. Distributed Control Strategy of Residential Photovoltaic Inverter and Energy Storage
Based on Consensus Algorithm. Autom. Electr. Power Syst. 2020, 44, 86–94.
16.
Ma, M.; Du, W.; Wang, L.; Ding, C.; Liu, S. Research on the multi-timescale optimal voltage control method for distribution
network based on a DQN-DDPG algorithm. Front. Energy Res. 2023, 10, 1097319. [CrossRef]
17.
Sam, W.; Johan, D. Optimal local reactive power control by PV inverters. IEEE Trans. Sustain. Energy 2016, 7, 1624–1633.
18.
Kabiri, R.; Holmes, D.; McGrath, B.; Meegahapola, L. LV grid voltage regulation using transformer electronic tap changing, with
PV inverter reactive power injection. IEEE J. Emerg. Sel. Top. Power Electron. 2015, 3, 1182–1192. [CrossRef]
19.
Benoit, B.; Serdar, K.; Roman, B.; Antony, Z. Voltage control with PV inverters in low voltage networks-in depth analysis of
different concepts and parameterization criteria. IEEE Trans. Power Syst. 2017, 32, 177–185.
20.
Pham, H.; Rueda, J.; Erlich, I. Probabilistic evaluation of voltage and reactive power control methods of wind generators in
distribution networks. IET Renew. Power Gener. 2014, 9, 195–206. [CrossRef]
21.
Mokhtari, G.; Ghosh, A.; Nourbakhsh, G.; Ledwich, G. Smart robust resources control in LV network to deal with voltage rise
issue. IEEE Trans. Sustain. Energy 2013, 4, 1043–1050. [CrossRef]
22.
Vasquez, J.; Mastromauro, R.; Guerrero, J.; Liserre, M. Voltage support provided by a droop-controlled multifunctional inverter.
IEEE Trans. Ind. Electron. 2009, 56, 4510–4519. [CrossRef]
23.
EN 50160:2010; Voltage Characteristics of Electricity Supplied by Public Distribution Networks.
CENELEC: Brussels,
Belgium, 2010.
24.
GB/T 19964-2012; Technical Provisions on the Access of Photovoltaic Power Plants to Electric Power Systems. China Standard
Press: Beijing, China, 2012.
25.
Cai, Y.; Tang, W.; Zhang, L.; Xu, O. Multi-mode Voltage Control in Low Distribution Networks Based on Reactive Power
Regulation of Photovoltaic Inverters. Autom. Electr. Power Syst. 2017, 41, 133–141.
26.
Fu, Y.; Zhou, X.; Su, X. Adaptive and Coordinated Volt/Var Optimization for Unbalanced Active Distribution Networks of
Multiple Voltage Levels. Power Syst. Technol. 2018, 42, 2136–2147.
27.
Hu, Y.; Liu, W.; Wang, W. A Two-layer Volt-var Control Method in Rural Distribution Networks Considering Utilization of
Photovoltaic Power. IEEE Access 2020, 8, 118417–118425. [CrossRef]
28.
Liu, S.; Huang, W.; Zhang, Y. Multi-time scale coordinated control method for distribution network based on point of common
coupling reactive power/ voltage optimization of photovoltaic. Int. J. Smart Grid Clean Energy (SGCE) 2019, 8, 580–585. [CrossRef]
29.
Jiang, F.; Lin, Z.; He, G.; Wu, Z.; Fan, R. Coordinated Voltage Control of Distributed Photovoltaic-Energy-Storage Systems Based
on a Dynamic Consensus Algorithm. J. Tianjin Univ. (Sci. Technol.) 2021, 54, 1299–1308.
30.
Hassan, A.S.J.; Marikkar, U.; Prabhath, G.W.K.; Balachandran, A.; Bandara, W.G.C.; Ekanayake, P.B.; Godaliyadda, R.I.; Ekanayake,
J.B. A Sensitivity Matrix Approach Using Two-Stage Optimization for Voltage Regulation of LV Networks with High PV
Penetration. Energies 2021, 14, 6596. [CrossRef]
31.
Yang, C.; Liang, X.; Mao, L. Research on Voltage Control of Low Voltage System Based on High-proportion Photovoltaic Access.
Electr. Drive 2022, 52, 60–67.
32.
Liu, Y.; Qin, W.; Wang, L.; Han, X.; Wang, P. Voltage Control Strategy of PV Grid-connected Inverter in Low-voltage Distribution
Network with Reduction Amount of Light discarded. Acta Energ. Sol. Sin. 2020, 41, 151–159.
33.
Cai, Y.; Zhang, L.; Tang, W.; Xu, O.; Wang, J. A Voltage Control Strategy for LV Distribution Network with High Proportion
Residential PVs Considering Reactive Power Adequacy of PV Inverters. Power Syst. Technol. 2017, 41, 2799–2808.
34.
Li, Z.; Wu, L.; Xu, Y. Risk-averse coordinated operation of a multi-energy microgrid considering voltage/var control and thermal
flow: An adaptive stochastic approach. IEEE Trans. Smart Grid 2021, 12, 3914–3927. [CrossRef]
35.
Zhang, B.; Gao, Y. Data-driven voltage/var optimization control for active distribution network considering PV inverter reliability.
Electr. Power Syst. Res. 2023, 224, 109800. [CrossRef]
36.
Alyami, S.; Wang, Y.; Wang, C.; Zhao, J.; Zhao, B. Adaptive Real Power Capping Method for Fair Overvoltage Regulation of
Distribution Networks with High Penetration of PV Systems. IEEE Trans. Smart Grid 2014, 5, 2729–2738. [CrossRef]
37.
Yu, Z.; Tang, Y.; Dai, J.; Yi, J. Voltage/var Control Strategy of PV Plant Based on Adaptive Adjustment of Active Power. Power
Syst. Technol. 2020, 44, 1900–1907.
38.
Fang, J.; Wen, Z. Research on local adaptive voltage control strategy based on distributed PV. Power Syst. Prot. Control 2015, 43,
49–55.
39.
Ku, T.; Lin, C.; Chen, C.; Hsu, C.; Hsieh, W.; Hsieh, S. Coordination of PV inverters to mitigate voltage violation for load transfer
between distribution feeder with high penetration of PV installation. IEEE Trans. Ind. Appl. 2016, 52, 1167–1174. [CrossRef]
40.
Ma, N.; Xu, Y.; He, Z. Mitigation Strategy at Photovoltaic Grid-connected Point Based on Adaptive Power Control of Inverter.
Proc. CSU-EPSA 2022, 34, 100–107.
41.
Wang, Y.; Zhang, P.; Li, W.; Xiao, W.; Abdollahi, A. Online Overvoltage Prevention Control of Photovoltaic Generators in
Microgrids. IEEE Trans. Smart Grid 2012, 3, 2071–2078. [CrossRef]
42.
Li, Q.; Zhang, J. Solutions of Voltage Beyond Limits in Distribution Network with Distributed Photovoltaic Generators. Autom.
Electr. Power Syst. 2015, 39, 117–123.
43.
Stetz, T.; Manter, F.; Braun, M. Improved low voltage grid integration of photovoltaic systems in Germany. IEEE Trans. Sustain.
Energy 2013, 4, 534–542. [CrossRef]



<!-- page 23/24 -->

Energies 2024, 17, 3058
23 of 24
44.
Wu, K. Analysis on on-load voltage regulating transformer and its fault treatment. Electr. Power Equip. Manag. 2018, 45–47.
[CrossRef]
45.
Yuan, J.; Zhang, W.; Mei, J.; Gan, D.; Zhou, H.; Zheng, Y.; Liu, J. Independent Fast Phase Shifting Transformer: A Flexible and
High-Precision Power Flow Controller. IEEE Trans. Power Deliv. 2023, 38, 4410–4421. [CrossRef]
46.
Maataoui, Y.; Chekenbah, H.; Boutfarjoute, O.; Puig, V.; Lasri, R. A Coordinated Voltage Regulation Algorithm of a Power
Distribution Grid with Multiple Photovoltaic Distributed Generators Based on Active Power Curtailment and On-Line Tap
Changer. Energies 2023, 16, 5279. [CrossRef]
47.
Ilea, V.; Bovo, C.; Falabretti, D.; Merlo, M.; Arrigoni, C.; Bonera, R.; Rodolfi, M. Voltage control methodologies in active distribution
networks. Energies 2020, 13, 3293. [CrossRef]
48.
Khan, H.; Rihan, M. Real-time coordinated control of voltage regulation devices in a high PV penetrated weak distribution
network. Comput. Electr. Eng. 2023, 110, 108872. [CrossRef]
49.
Süleyman, T.; Tuba, G. The robust curve-fitting based method for coordinated voltage regulation with distributed generator and
OLTC in distribution network. Alex. Eng. J. 2023, 75, 243–259.
50.
Jia, H.; Zhu, X.; Cao, W. Distribution Network Reconfiguration Based on an Improved Arithmetic Optimization Algorithm.
Energies 2024, 17, 1969. [CrossRef]
51.
Cui, R.; Ding, Y.; Jia, W.; Cheng, Y.; Lu, J. PV hosting capacity improvement based on network reconfiguration and reactive
voltage regulation. Distrib. Util. 2023, 40, 18–24.
52.
Murty, V.; Ashwani, K. Optimal coordinate control of OLTC, DG, D-STATCOM, and reconfiguration in distribution system for
voltage control and loss minimization. Int. Trans. Electr. Energy Syst. 2019, 29, e2752. [CrossRef]
53.
Zhang, J.; Zhuang, H.; Liu, J.; Gao, H.; Zhang, L. Two-stage coordinated voltage control scheme of active distribution network
with voltage support of distributed energy storage system. Electr. Power Autom. Equip. 2019, 39, 15–21+29.
54.
Tang, W.; Cai, Y.; Li, T.; Xu, O. Distributed PV Consumption Control Strategy and Performance Analysis in Low Voltage
Distribution Network. Distrib. Energy 2018, 3, 1–12.
55.
Xu, L.; Xie, Q.; Zheng, L.; Hua, Y.; Shao, L.; Cui, J. Stackelberg-Game-Based Demand Response for Voltage Regulation in
Distribution Network with High Penetration of Electric Vehicles. Energies 2022, 15, 3654. [CrossRef]
56.
Sandip, G.; Tirthadip, G.; Kalyan, C. Optimal coordination between PV smart inverters and different demand response programs
for voltage regulation in distribution system. Int. Trans. Electr. Energy Syst. 2020, 31, e12765.
57.
Xie, Q.; Hui, H.; Ding, Y.; Ye, C.; Lin, Z. Use of demand response for voltage regulation in power distribution systems with flexible
resources. IET Gener. Transm. Distrib. 2020, 14, 883–892. [CrossRef]
58.
Zhu, D.; Zhou, Q.; Jia, Y.; Liu, F.; Zhu, D. Optimal allocation of reactive power resources in a new distribution system based on
the “source-load” multi-sequence scenario in a “planning-operation” fusion framework. Power Syst. Prot. Control 2023, 51, 62–78.
59.
Chen, X.; Lyu, J.; McElroy, M.; Han, X.; Nielsen, C.; Wen, J. Power system capacity expansion under higher penetration of
renewables considering flexibility constraints and low carbon policies. IEEE Trans. Power Syst. 2018, 33, 6240–6253. [CrossRef]
60.
Alismail, F.; Abdulgalil, M.; Khalid, M. Optimal coordinated planning of energy storage and tie-lines to boost flexibility with high
wind power integration. Sustainability 2021, 13, 2526. [CrossRef]
61.
Emmanuel, M.; Doubleday, K.; Cakir, B.; Markovi´c, M.; Hodge, B. A review of power system planning and operational models
for flexibility assessment in high solar energy penetration scenarios. Sol. Energy 2020, 210, 169–180. [CrossRef]
62.
Du, W.; Bai, K.; Li, H.; Zhang, L.; Liu, D. Source-Load-Storage Flexible Resource Optimization Planning that Takes into Account
Power Supply and Accommodation. Electr. Power Constr. 2023, 44, 13–23.
63.
Xun, Z.; Liu, J.; Xu, S.; Ma, C.; Wang, Y. Source-Load-Storage Flexibility Resource Coordinated Planning for High Proportion of
Renewable Energy. Power Syst. Clean Energy 2022, 38, 107–117.
64.
Azarnia, M.; Rahimiyan, M. Robust Volt-Var control of a smart distribution system under uncertain voltage-dependent load and
renewable production. Int. J. Electr. Power Energy Syst. 2022, 134, 107383. [CrossRef]
65.
Xu, W.; Gong, J.; Jin, X.; Wei, W.; Liang, S.; Wang, H. Optimal Energy Management of Aggregated Demand Side Resources in a
Microgrid–taking Office Buildings and Electric Vehicles as an Example. In Proceedings of the 2023 8th Asia Conference on Power
and Electrical Engineering (ACPEE), Tianjin, China, 14–16 April 2023; IEEE: Piscataway, NJ, USA, 2023; pp. 1091–1096.
66.
Mohanty, S.; Panda, S.; Sahu, B.; Rout, P. A genetic algorithm-based demand side management program for implementation of
virtual power plant integrating distributed energy resources. In Innovation in Electrical Power Engineering, Communication, and
Computing Technology: Proceedings of Second IEPCCT 2021; Springer: Singapore, 2022; pp. 469–481.
67.
Li, B.; Zhang, J.; Qi, B.; Li, D.; Shi, K. Block Chain: Supporting Technology of Demand Side Resources Participating in Grid
Interaction. Electr. Power Constr. 2017, 38, 1–8.
68.
Antonopoulos, I.; Robu, V.; Couraud, B.; Kirli, D.; Norbu, S.; Kiprakis, A.; Flynn, D.; Elizondo, S.; Wattam, S. Artificial intelligence
and machine learning approaches to energy demand-side response: A systematic review. Renew. Sustain. Energy Rev. 2020,
130, 109899. [CrossRef]
69.
Ratshitanga, M.; Mataifa, H.; Krishnamurthy, S.; Tshinavhe, N. Demand-Side Management as a Network Planning Tool: Review
of Drivers, Benefits and Opportunities for South Africa. Energies 2023, 17, 116. [CrossRef]
70.
Panda, S.; Mohanty, S.; Rout, P.K.; Sahu, B.K.; Parida, S.M.; Kotb, H.; Flah, A.; Tostado-Véliz, M.; Abdul Samad, B.; Shouran, M.
An insight into the integration of distributed energy resources and energy storage systems with smart distribution networks
using demand-side management. Appl. Sci. 2022, 12, 8914. [CrossRef]



<!-- page 24/24 -->

Energies 2024, 17, 3058
24 of 24
71.
Iwafune, Y.; Kazuhiko, O.; Kobayashi, Y.; Suzuki, K.; Shimoda, Y. Aggregation model of various demand-side energy resources in
the day-ahead electricity market and imbalance pricing system. Int. J. Electr. Power Energy Syst. 2023, 147, 108875. [CrossRef]
72.
Ostadijafari, M.; Jha, R.; Dubey, A. Demand-side participation via economic bidding of responsive loads and local energy
resources. IEEE Open Access J. Power Energy 2020, 8, 11–22. [CrossRef]
73.
Wang, C.; Shi, Z.; Liang, Z.; Li, Q.; Hong, B.; Huang, B.; Jiang, L. Key Technologies and Prospects of Demand-side Resource
Utilization for Power Systems Dominated by Renewable Energy. Autom. Electr. Power Syst. 2021, 45, 37–48.
74.
Nikoobakht, A.; Aghaei, J.; Shafie-khah, M.; Cataláo, J. Assessing increased flexibility of energy storage and demand response to
accommodate a high penetration of renewable energy sources. IEEE Trans. Sustain. Energy 2019, 10, 659–669. [CrossRef]
75.
Wang, S.; Du, L.; Fan, X.; Huang, Q. Deep reinforcement scheduling of energy storage systems for real-time voltage regulation in
unbalanced LV networks with high PV penetration. IEEE Trans. Sustain. Energy 2021, 12, 2342–2352. [CrossRef]
76.
Deng, Q.; Hu, D.; Cai, T.; Li, X.; Xu, X.; Peng, Y. Reactive power optimization strategy of distribution network based on multi
agent deep reinforcement learning. Adv. Technol. Electr. Eng. Energy 2022, 41, 10–20.
77.
Gao, Y.; Wang, W.; Yu, N. Consensus multi-agent reinforcement learning for voltage-var control in power distribution networks.
IEEE Trans. Smart Grid 2021, 12, 3594–3604. [CrossRef]
78.
Liu, H.; Wu, W. Federated reinforcement learning for decentralized voltage control in distribution networks. IEEE Trans. Smart
Grid 2022, 13, 3840–3843. [CrossRef]
Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
