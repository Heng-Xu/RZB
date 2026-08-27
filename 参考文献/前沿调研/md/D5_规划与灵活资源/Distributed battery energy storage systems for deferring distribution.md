<!--
source: D5_规划与灵活资源/Distributed battery energy storage systems for deferring distribution.pdf
sha256: fff9b73a802a629e9b15818096234c2ba6a4ebef110a2a2eacdc330ce0162868
method: pymupdf
pages: 9
-->

<!-- page 1/9 -->

Research Papers
Distributed battery energy storage systems for deferring distribution 
network reinforcements under sustained load growth scenarios
Miguel Martínez a,*, Carlos Mateo a, Tomas G´omez a, Beatriz Alonso b, Pablo Frías a
a Institute for Research in Technology (IIT), School of Engineering (ICAI), Universidad Pontificia Comillas, Spain
b i-DE Redes El´ectricas Inteligentes, Spain
A R T I C L E  I N F O
Keywords:
Distribution network planning
Energy storage systems
Reinforcements
Genetic algorithms
A B S T R A C T
Energy storage systems can be leveraged in electricity distribution network planning as mitigation alternatives to 
traditional grid reinforcements if they are strategically installed and operated to reduce congestion and voltage 
limit violations. This paper examines the technical and economic viability of distributed battery energy storage 
systems owned by the system operator as an alternative to distribution network reinforcements. The case study 
analyzes the installation of battery energy storage systems in a real 500-bus Spanish medium voltage grid under 
sustained load growth scenarios. The results show that, in general, dedicated battery energy storage systems are 
only a cost-efficient alternative in distribution system planning under very specific conditions, such as when low 
load growth rates are expected. Nevertheless, they are only required for peak shaving a few days per year. For the 
analyzed case study, the recoverable portion of their total cost through deferral of distribution system upgrades is 
higher than the fraction of cycles required for peak shaving under all sustained load growth scenarios. Therefore, 
it is also explored if mobile battery energy storage systems, capital grants, and revenue stacking can enable 
battery energy storage systems to become an efficient distribution system planning alternative.
1. Introduction
Electricity distribution networks (DNs) are undergoing a major 
transition driven by the increasing penetration of distributed energy 
resources (DERs). Higher levels of electrification and the need to inte­
grate higher shares of DERs have put a spotlight on distribution network 
planning (DNP). Distribution system operators (DSOs) are facing new 
challenges due to the growing electrification of energy demand and 
DERs connected to DNs. However, the digitalization of grids allows 
DSOs to benefit from valuable services achieved by a smart operation of 
DERs, such as energy storage systems (ESSs) [1]. Therefore, strategically 
installed and operated DERs could be leveraged in DNP as non-wires 
alternatives to reinforcements in DNs [2].
In the European Union, Article 36 of the Directive (EU) 2019/944 
does not generally allow DSOs to own, develop, manage, or operate ESSs 
unless they are fully integrated network components (i.e., ESSs cannot 
be used to buy or sell energy in electricity markets) and have received 
approval from the national regulatory authority. Nevertheless, the Eu­
ropean Commission has recently recommended that system operators 
assess further whether ESSs can be a more cost-effective alternative to 
conventional investments in DN upgrades [3]. For instance, distribution- 
system-connected ESSs can mitigate network component overloads, 
reduce the intermittency of renewable generation, improve power 
quality, and control voltage fluctuations [4].
In this context, the study of the optimal sizing and location of 
distributed ESSs in DNP has gained attraction in the scientific literature 
[5]. ESSs are highly flexible DERs that can be used for different appli­
cations and planning objectives [6]. The most common application, 
considered in [7–9], is obtaining a benefit from energy arbitrage by 
charging the ESS when electricity is cheap and generating energy by 
discharging the ESS during high-demand periods. However, ESSs can 
also provide benefits during the operation of the DN by reducing energy 
losses, enhancing voltage regulation, improving reliability, and avoiding 
overloads [10]. Furthermore, ESSs installed at DNs could provide ser­
vices to the transmission network and reduce the uncertainty from 
distributed generation (DG) [11]. All these applications offer different 
benefits to the power system: transmission and distribution grid re­
inforcements deferral, frequency and non-frequency ancillary services, 
energy arbitrage, reduction in peaking generation capacity, higher 
integration of intermittent renewable energy, and emissions reduction 
[12].
Distribution investment deferrals are not typically included in bat­
tery energy storage system (BESS) portfolios that stack multiple revenue 
* Corresponding author.
E-mail address: Miguel.Martinez@iit.comillas.edu (M. Martínez). 
Contents lists available at ScienceDirect
Journal of Energy Storage
journal homepage: www.elsevier.com/locate/est
https://doi.org/10.1016/j.est.2024.113404
Received 9 April 2024; Received in revised form 17 July 2024; Accepted 14 August 2024  
Journal of Energy Storage 100 (2024) 113404 
Available online 29 August 2024 
2352-152X/© 2024 Elsevier Ltd. All rights are reserved, including those for text and data mining, AI training, and similar technologies.



<!-- page 2/9 -->

streams. The most common combinations include energy arbitrage, 
frequency restoration services, and renewable energy generation inte­
gration [13]. Besides, the specific conditions under which ESSs could 
become a viable alternative as a grid asset for deferring grid re­
inforcements in DNs have not been sufficiently addressed in the litera­
ture. Most studies combine several of the aforementioned benefits in the 
objective function to minimize the total cost of the system [7–9,12] or 
perform a multi-objective optimization [10,14]. However, objectives 
that bring greater benefits to the power system (e.g., energy arbitrage, 
resiliency, etc.) are more prominent in determining the optimal solution 
in these papers.
On the other hand, some authors have focused on analyzing how 
ESSs can be strategically used as a mitigation alternative for grid 
congestion in DNs [15–21]. Optimal charging and discharging sched­
uling of BESSs have been addressed to defer substation reinforcements 
[15], to avoid voltage and overload problems [16], to perform peak 
shaving [17], and to reduce electric vehicle (EV) charging peak load 
[18]. None of these papers optimize a combination of BESS installation 
and grid upgrade investment decisions. The optimal sizing of distributed 
BESS in DNs for voltage regulation and peak load shaving under high 
solar photovoltaic penetrations is addressed in [19]. In [20], it is 
analyzed how distribution system security of supply can be enhanced by 
providing the additional required capacity through a combination of ESS 
and real-time thermal rating monitoring. Nevertheless, the probabilistic 
analysis used in [20] does not perform any optimization and is limited to 
mitigating congestion at the substation. The distribution network is not 
modeled in [20], and the cost of reinforcements is an estimation based 
on the distance from the substation.
A techno-economic analysis of installing ESSs to mitigate grid 
congestion caused by high EV uptakes in several distribution grids is 
studied in [21], but varying peak load and load growth conditions are 
not evaluated. In [22], it is suggested that the optimal conditions for 
deferring network upgrades with BESSs is a scenario where the expected 
load growth rate is small, and the deferred investment is expensive. 
However, this theoretical discussion is not supported by a case study. 
The option value of dynamic line rating and ESS was analyzed in [23] for 
a small test grid under six load and DG scenarios. Nevertheless, the 
planning horizon in [23] is shorter than the ESS's useful life, and it 
cannot be concluded whether it is a viable planning alternative. 
Therefore, further research is needed to determine when the installation 
of ESSs can be used in practice to defer or avoid DN reinforcements 
under sustained load growth conditions.
Moreover, recent studies have identified mobile BESSs as an 
emerging resource for improving resilience [24,25], increasing the share 
of renewable energy and EV fast charging stations [26], and reducing 
generation curtailment and energy losses [27]. To the authors' knowl­
edge, this study is the first to assess whether moving a BESS to another 
location could offset the additional shipping and installation costs by 
reducing the project duration when investing in a BESS as a network 
planning alternative.
This study analyzes whether the optimal installation of BESSs can be 
a techno-economic alternative to postpone investments in network re­
inforcements under sustained load growth scenarios. This paper focuses 
on DNP. Hence, BESSs are viewed as fully integrated network compo­
nents owned and operated by the DSO to reduce the loading of the DN 
during peak hours. The main contributions of this paper are:
• Assessing whether the optimal installation of DSO-owned BESSs in 
distribution systems can serve as a techno-economic planning 
alternative to network reinforcements. The optimal combination of 
investments in network reinforcements and BESSs is obtained with 
the proposed methodology, which employs a genetic algorithm (GA) 
that locates and sizes distributed BESSs to minimize investment costs 
in the DN.
• Determining the portion of the total cost over the life of a BESS that 
can be recouped by deferring DN upgrades under different load 
growth scenarios. This is illustrated by a case study of a real 500-bus 
Spanish DN.
• Evaluating the potential of novel approaches to enhance the techno- 
economic viability of BESS installations in DNP. These include mo­
bile BESSs, capital grants, and revenue stacking with other grid 
services.
The remainder of this paper is organized as follows. Section 2 de­
scribes the proposed methodology for evaluating the distributed 
installation of ESSs in DNs as an alternative to defer investments in 
distribution network reinforcement. Section 3 applies this methodology 
to a real Spanish DN, which serves as a case study. Then, in Section 4, the 
results of the case study are studied under different load growth rates. 
Finally, conclusions are drawn in Section 5.
2. Methodology
This section presents a deterministic model that combines distrib­
uted BESSs and traditional network reinforcements in DNP. As afore­
mentioned, intelligent planning and operation of distributed BESSs can 
provide several benefits to DNs, such as reducing the loading of the DN 
during peak demand hours. Thus, DSOs can optimize their costs in DNP 
by considering the installation of distributed BESSs as an option to 
postpone or avoid traditional network reinforcements. This methodol­
ogy aims to find the optimal combination of distributed BESSs and 
network reinforcements that minimize DNP costs while satisfying the 
grid operational limits. Equivalent annual costs are used to compare 
these grid assets with different lifetimes fairly. The average useful life of 
BESSs is significantly shorter than that of power lines and transformers.
This paper assumes that the DSO will own and operate the distrib­
uted BESSs as a flexible network asset to reduce distribution system 
costs. Note that the unbundling of the electricity sector in many coun­
tries does not currently allow DSOs to profit from arbitrage in wholesale 
electricity markets. Initially, the only system benefit considered by this 
methodology to motivate DSO investments in BESS as a network asset is 
the deferral of DN reinforcements. Therefore, it is assumed that the DSOs 
will operate BESSs based on a peak shaving strategy to reduce the 
loading of DN equipment during days with high demand [28]. Recon­
figuration, contingencies, and other singular operating conditions are 
not modeled in the proposed methodology. Nevertheless, a sensitivity 
analysis regarding the benefits of stacking other ancillary services pro­
vided by distributed BESS will also be analyzed later in the case study.
Regarding the distributed installation of BESSs, the proposed meth­
odology optimizes their location and capacity. The methods employed to 
find the optimal location, sizing, and control strategies of ESSs in DNP 
can be classified into four categories: analytical methods, exhaustive 
search, mathematical programming, and metaheuristics [29]. The main 
issue with analytical methods is that they do not perform any 
Nomenclature
BESS
Battery energy storage system
DER
Distributed energy resource
DN
Distribution network
DNP
Distribution network planning
DSO
Distribution system operator
DG
Distributed generation
ESS
Energy storage system
EV
Electric vehicle
GA
Genetic algorithm
HV
High voltage
LV
Low voltage
MV
Medium voltage
M. Martínez et al.                                                                                                                                                                                                                              
Journal of Energy Storage 100 (2024) 113404 
2



<!-- page 3/9 -->

optimization. On the other hand, exhaustive search methods guarantee 
finding the optimal solution within a discrete search space, but they 
require long computing times and are not practical for large-scale DNP 
studies. Moreover, various mathematical programming techniques have 
been developed to convert the optimal power flow problem for siting 
and sizing ESSs into mixed-integer linear programming (MILP) [23,30] 
or mixed-integer second-order cone programming model (MISOCP) 
[11]. Finally, the high complexity behind this problem, which involves 
large amounts of binary decision variables and the nonlinear relation­
ships of power flows in electricity systems, has also resulted in many 
papers that propose different meta-heuristic algorithms to solve this 
optimization problem [5].
Although metaheuristics do not guarantee convergence to the global 
optimum, many authors have shown that a variety of them can produce 
reasonable solutions in practice, including GA [7,31,32], Non- 
dominated Sorting Genetic Algorithm – II (NSGA-II) [10], Differential 
Evolution [33], Particle Swarm Optimization [34], and Artificial Bee 
Colony [35]. The proposed methodology uses a GA to handle this 
complexity and allow its application for large-scale real DNs.
The input data sets for this model include electrical and economic 
data for utility-scale BESSs, a catalog with techno-economic data for 
new network equipment, electrical and topological data of the DN, and 
daily load profiles for all loads and DG units. The model outputs are the 
optimal location and size of BESS units, network reinforcements, and 
DNP equivalent annual cost.
2.1. Genetic algorithm
The objective of the DSO in DNP is to define investments according to 
planning criteria to maintain a reliable and efficient distribution electric 
system. In this paper, both distributed BESSs and traditional network 
reinforcements are considered candidate investments to avoid thermal 
and voltage limit violations. Although the unit cost of BESSs (€/kWh) is 
considered as a constant input parameter, the overall cost of BESSs in­
vestments is derived from the number of BESSs and their capacity 
(kWh). Thus, the decision variables for installing distributed BESSs are 
their capacity and location.
These decisions are modeled in the GA by characterizing individuals, 
the candidate solutions in the GA, based on the capacity and allocation 
node for each distributed BESS. Thus, each individual's genome is a 
sequence of pairs of decision variables for each distributed BESS. The 
first element (i.e., odd entries) determines its capacity in kWh, denoted 
as xi, and the second (i.e., even entries) gives the DN bus where it is 
installed, denoted as zi. The codification of the individuals is illustrated 
in Fig. 1, with an example of three BESSs to be deployed in a grid. In the 
illustrative example in Fig. 1, BESS 1 represents a 250 kWh BESS located 
at bus 34 of the distribution grid. Similarly, 1500 kWh and 725 kWh 
would be installed at nodes 497, and 421, respectively. Note that the 
number of decision variables, BESS capacity and location, in every in­
dividual is twice that of the number of BESSs to be deployed in the grid.
The objective function of the model (1) is to minimize the equivalent 
annual cost of all investments in distributed BESSs (CBESS) and tradi­
tional network reinforcements (CDNR). As aforementioned, equivalent 
annual costs are used to fairly compare the cost of these grid assets 
which have significantly different useful lives.1
min CBESS + CDNR
(1) 
The annual cost of BESSs (2) is obtained as the sum of all installed 
capacities multiplied by their annualized cost (EACBESS), expressed in 
€/MWh-yr. 
CBESS = EACBESS⋅
∑
i xi
(2) 
On the other hand, the annual cost of investments in DN re­
inforcements is derived as a function of the siting and sizing of BESS 
decisions (3). Note that traditional network reinforcements are not 
considered decision variables. Each individual in the GA population 
represents a fixed set of BESS installations, and the DSO can only solve 
the remaining grid limit violations by reinforcing the DN. The optimal 
DN reinforcement decisions are always the same for a given set of BESS 
installations. For instance, if the size of the BESSs performing peak 
shaving is not enough to resolve the congestion of a power line, then that 
power line will have to be upgraded. Section 2.2 describes in detail the 
function for computing the annual cost of investments in DN 
reinforcements. 
CDNR = f(xi, zi)
(3) 
Besides, the installation of distributed BESSs is constrained to a 
maximum BESS capacity (X) that can be installed at a single bus (4). 
Fig. 1. Illustrative example of a GA individual chromosome codification for 
3 BESSs.
Fig. 2. Flowchart of GA.
1 In this paper, it is assumed a useful life of 16 years for BESSs and 40 years 
for power lines and transformers.
M. Martínez et al.                                                                                                                                                                                                                              
Journal of Energy Storage 100 (2024) 113404 
3



<!-- page 4/9 -->

Finally, constraints (5) and (6) guarantee that BESSs are installed in one 
of the candidate buses. The variable zi denotes the bus at which the BESS 
is installed, so it is defined as an integer variable (6). If no investment in 
BESS is made, zi takes a value of zero. Otherwise, it takes the value of the 
bus where the BESS is installed and, thus, the maximum value zi can take 
is the number of buses (NBUS) in the DN. 
xi ≤X
(4) 
0 ≤zi ≤NBUS
(5) 
zi ∈ℤ
(6) 
Fig. 2 shows a flowchart of the GA. After reading the input data, an 
initial population is created with randomly selected individuals. Then, 
the necessary reinforcements are computed (see Section 2.2), and the 
fitness function is evaluated for each individual. If the GA does not 
converge, a new generation of candidate solutions is used for the next 
iteration. This new population is generated by mutation and recombi­
nation of the genomes from selected individuals with the best fitness 
values. The GA stops when the maximum number of iterations is reached 
or the best fitness function value has converged.
2.2. Computation of required investments in network reinforcements
This section describes how network reinforcements are selected for 
each individual in the GA, which determines a fixed set of BESS in­
stallations. First, the power profile of the distributed BESSs is added at 
the nodes where they are installed. The generation/consumption profile 
for each BESS is computed based on its capacity. It is assumed that the 
BESS is operated to perform peak shaving, thereby reducing the aggre­
gate peak load in the DN. Then, a power flow analysis is run. The total 
cost of traditional network reinforcements (CDNR) for given locations and 
capacities of distributed BESSs are obtained by resolving all deviations 
from grid limits after this power flow analysis. Two types of re­
inforcements may be necessary: i) overloads of power lines or trans­
formers are solved by investing in a new element with a higher power 
rating, and ii) voltage issues are addressed by reinforcing some of its 
upstream branches to reduce their impedance and, as a result, their 
voltage drop.
Resolving voltage limit violations is not a simple task. The rein­
forcement of a branch reduces its voltage drop, but it also affects the 
voltage of all downstream nodes in radial DNs. To select which branches 
should be reinforced first, all branches are ranked by a KPI that measures 
the resulting voltage deviations after reinforcing that branch to reduce 
its voltage drop: 
KPI =
∑
i
(
Vdevi–MVReinf
i,l
•
(
1 −
1
nMAX
l
) )
(7) 
where Vdev is the vector of voltage deviations from the limit at each bus 
i, MVReinf is the sensitivity matrix that measures the impact of reinforcing 
branch l on the voltage of bus i, and nMAX
l 
is the maximum number of 
equivalent parallel lines of branch l to reinforce. The monotonicity of 
decreasing nominal ampacities is enforced by imposing an upper limit 
on nMAX
l
so that the nominal capacity of branch l cannot exceed the ca­
pacity of its upstream branch.
Once the KPI for each branch is computed, the candidate branch with 
the lowest KPI value is reinforced. This process of selecting the optimal 
branch to be reinforced is repeated until all voltage issues have been 
solved.
3. Case study
A real 20 kV rural DN, operated by i-DE in Spain, is analyzed in this 
case study. This DN consists of 500 buses and 504 branches, but it is 
operated radially with five open branches. Its power lines extend over a 
distance of 243 km, and the DN is connected to the HV grid by means of a 
20 MVA HV/MV substation. In the case study, it is assumed that there 
are no technical violations at LV, allowing consumers and DG to be 
represented as the aggregation of demand and generation at the distri­
bution MV/LV transformers. Based on their location and type (i.e., in­
dustrial or residential), their hourly loading profile for a peak demand 
day is assigned. First, unitary hourly profiles are obtained from the 
measured aggregated hourly demand of each type of customer, differ­
entiated by access tariff, in Spain [36]. Then, these unitary profiles are 
multiplied by the contracted power at each connection point.
An equipment catalog for new network equipment (i.e., BESSs, 
power lines, and transformers) is also given as input to the model. As 
shown in Fig. 3, the aggregate load curve has a nighttime peak lasting 3 
h. Therefore, it is assumed that the DSO can invest in a BESS that can 
provide a maximum of 3 MW for 4 h.2 In the base scenario, peak demand 
plus power losses result in a substation load of 20.24 MVA, slightly 
exceeding the substation capacity limit by 1 %. An annual equivalent 
cost for BESSs of 40.6 €/kWh-yr.3 is used for this case study [37]. In 
addition, the cost of power lines and transformers is determined based 
on the reference investment and operation and maintenance values 
defined by the Spanish regulation [38]. Then, the equivalent annual cost 
is calculated for each asset, considering a discount rate of 5.58 % [39] 
and an expected useful life of 40 years for power lines and transformers 
[38] and 16 years for ESSs [37].
4. Results
This section presents the results of the case study, which analyzes the 
techno-economic viability of the distributed BESSs in DNP as an alter­
native to DN reinforcements under different load growth scenarios. The 
GA has been implemented using the off-the-shelf GA solver in MATLAB, 
and MATPOWER [40] is employed for power flow analysis.
First, the GA-based model is used to optimally locate and size 
Fig. 3. Loading of HV/MV substation for a peak load day in the base 
case scenario.
2 Given that evening peak lasts for 3 h, it is assumed that the battery will be 
discharged at its rated power for a maximum of 4 h. Besides, the rated power of 
the BESSs is limited to 3 MW because the difference between the peak demand 
and the demand at off-peak hours at midday does not exceed 3 MW in any of the 
scenarios.
3 This reference value is derived by annualizing the installation, operation 
and decommission reference costs for a 1 MW-4 h lithium ferrophosphate (LFP) 
BESS over a lifetime of 16 years.
M. Martínez et al.                                                                                                                                                                                                                              
Journal of Energy Storage 100 (2024) 113404 
4



<!-- page 5/9 -->

distributed BESS to reduce the cost of conventional network re­
inforcements in a scenario where the rating of the substation trans­
former is exceeded during peak demand hours. From a DNP perspective, 
peak shaving is only required when the limits of the existing DN infra­
structure are exceeded. The aggregate load profile for this base case 
scenario was presented previously in Fig. 3. It is assumed that this profile 
is representative of the 20 days with the highest demand in the year. 
According to the GA model, the optimal investment decision for this 
base case scenario is to install a 715 kWh BESS at bus 498, which is 
located at the end of the sub-feeder with the highest peak demand. This 
result seems very promising as it yields 50,000 €/yr. in annual cost 
savings from deferring conventional investments in DN reinforcements, 
mainly from avoiding a new substation transformer investment. 
Nevertheless, this result is just an illustration of one scenario, and the 
aggregate load will probably continue to increase over the project's 
lifetime.
Fig. 4 illustrates a sensitivity of the cost savings per year achieved by 
installing a 715 kWh BESS at bus 498 to the peak load of the HV/MV 
substation. In Fig. 4, the annual cost savings refer to the difference be­
tween the equivalent annual costs of the deferred grid reinforcements 
and the BESS. This sensitivity analysis shows that there is only a narrow 
range of peak load conditions, colored in blue in Fig. 4., where the 
distributed BESS is an economical alternative to defer network re­
inforcements. If the substation is not overloaded, the distributed BESS 
might be useful to postpone a few power line reinforcements, but it is not 
an economical solution. This is illustrated in the orange-colored area of 
Fig. 4, where the deferral of power line upgrades for some loading in­
tervals compensates for part of the BESS cost, but it is not sufficient to 
justify an investment in a BESS.
When the overload of the substation transformer is small, it is more 
economical to reduce its loading by installing a BESS with just enough 
capacity to avoid the congestion of the transformer. Upgrading the 
substation transformer to a higher rating (e.g., 40 MVA) will have the 
same cost if its original rating is expected to be exceeded by 1 MVA or 19 
MVA. However, because of the very high unit costs (in €/MWh) for BESS 
installation, it is only efficient to install BESS if the overload of the 
substation is small and it is only required to provide peak shaving for a 
few hours.
Where permitted by the regulation, the DSO may consider other 
options to improve the economic viability of BESS investments, such as 
mobile BESSs, capital grants, and stacking multiple services provided to 
the power system by BESSs. Although the installation of third-party- 
owned BESS is beyond the scope of this study, the revenue stacking 
analysis could also inform the BESS owner of the fraction of the BESS 
cost that can be recovered by providing a flexibility service to defer 
network reinforcements.
4.1. Sensitivity to sustained eak demand growth
The net present value (NPV) of investing in a 715kWh BESS at bus 
498 (the optimal solution selected by the GA) is analyzed for different 
constant interannual growth rates of peak demand over the 16 years of 
the BESS lifetime in the upper plot of Fig. 5. When demand grows very 
slowly, the BESS is effective in keeping the loading of power lines and 
transformers below their nominal rating during several years. The bot­
tom plot in Fig. 5 shows that the number of years that the BESS can 
postpone the reinforcement of the HV/MV substation sharply decreases 
for higher load growth rates. This can be seen in Fig. 5 where the NPV of 
installing this BESS is only positive for interannual growth rates up to 
0.16 %. Alternatively, in this case study, the BESSs should be enough to 
defer the substation reinforcement for at least 5 or 6 years. Although the 
BESS investment can yield high distribution system cost reductions for 
small load growth rates, this window is quite narrow, and the NPV 
significantly decreases if the resulting load growth is slightly higher than 
expected. Therefore, for distributed BESSs to be an efficient alternative 
to traditional DN upgrades, considering network investment deferral as 
the only revenue stream to justify the investment in distributed BESSs, 
the expected aggregated peak demand growth rate should be low, and 
the load forecast should have little uncertainty.
4.2. Mobile battery energy storage systems
Mobile BESSs have been considered by estimating the annual cost of 
the project for a smaller time window (see Appendix A). The project 
length indicates the time the mobile BESS unit is installed at each 
location during its useful life. For instance, a project length of 8 years 
means that the BESS unit is installed at 2 different DNs and is used for 
peak shaving during 8 years at each of them. The total cost of mobile 
BESS increases significantly as the project length decreases because the 
BESS unit is moved more frequently. This results in higher project- 
related costs (e.g., shipping and installing the BESS at the new site) 
that have to be assumed at every different location. On the other hand, 
the advantage of mobile BESS units is that they are a more flexible 
Fig. 4. Evolution of the annual cost reduction from installing a 715kWh BESS 
at bus 498 as the aggregate peak demand is increased.
Fig. 5. NPV of investing in a 715kWh BESS at bus 498 (upper plot) and number 
of years the substation reinforcement is deferred (lower plot) for different 
interannual growth rates of peak demand during a 16-year period.
M. Martínez et al.                                                                                                                                                                                                                              
Journal of Energy Storage 100 (2024) 113404 
5



<!-- page 6/9 -->

option, as they can still be used for peak shaving at another location if 
the load growth becomes too high and the BESS unit is no longer able to 
defer a network reinforcement.
Fig. 6 illustrates the NPV of a 715kWh mobile BESS for different 
interannual growth rates of peak demand and project lengths. At high 
load growth rates, mobile BESSs show their advantage over dedicated 
BESSs that remain at the same location for 16 years. In Fig. 5, the BESS is 
only used for one year to defer the reinforcement of the substation. 
Conversely, in Fig. 6, the NPV increases for shorter project durations as 
the mobile BESSs can be used at more grids or locations. Nevertheless, 
despite higher utilization rates, the NPV at high load growth rates re­
mains negative due to the high equivalent annual costs of mobile BESSs. 
For project durations between 4 and 8 years, mobile BESSs are viable 
only up to a 0.25 % interannual load growth rate. In Fig. 6, the window 
of load growth rates where mobile BESSs are an economic alternative to 
network reinforcements is not significantly extended compared to the 
maximum 0.16 % load growth rate obtained in the previous section for 
non-mobile BESSs. Therefore, the main drawbacks for mobile BESSs are 
uncertainties in estimating the costs of mobile BESSs, increased project 
complexity and lower cost reductions for small load growth rates.
4.3. BESS cost reduction and revenue stacking
Learning rates, capital grants, and stacking multiple ancillary ser­
vices are modeled based on the assumption that each of these options 
could allow for a reduction in the fraction of the cost of the BESS asset 
that will need to be recovered through the deferral of network upgrades. 
Despite the recent increase in BESS costs due to inflation, it is expected 
that utility-scale BESS costs will reduce by 25 % in 2030 based on a 7 % 
learning rate [37]. In Fig. 7, this scenario (depicted in orange) does not 
provide much improvement. Thus, further revenue streams or BESS cost 
reduction will be required to make BESSs an interesting alternative 
under higher load growth scenarios. A reduction of 75 % of BESS costs is 
required in this case study for the investment to be profitable under all 
load growth scenarios.
Where allowed by the regulation, stacking the benefits of multiple 
ancillary services could significantly increase the viability of installing 
BESS for DSOs, as shown in Fig. 7. This could be achieved because the 
number of peak days per year when the BESS is required for peak 
shaving is small (e.g., 20 peak days in this case study). Only 10 % of the 
BESS cycles over its lifetime will be used for peak shaving, and from 
Fig. 7, at least 25 % of the total BESS cost is expected to be recovered 
under all load growth rates considered. Thus, in this case study, the BESS 
unit, by deferring network investments, would recover at least a portion 
of its installation cost proportional to the percentage of cycles over its 
useful life that it is used for peak shaving. Where allowed by the regu­
lation, combining peak shaving with the provision of other grid services 
should be considered to make installing BESS a profitable alternative in 
DNP, especially when high load growth rates are expected.
This result is also interesting from the perspective of third-party- 
owned BESS, as it informs of the value for the distribution system of a 
peak shaving service to defer network reinforcements. A BESS, which is 
owned by a third party, can participate in electricity markets and have a 
wider range of revenue streams. Although DSOs would not own the 
BESS, they could only contract congestion management and voltage 
control services from third parties when needed. In the European Union, 
this alternative is currently being discussed in the proposal for the 
Network Code on Demand Response [41].
5. Conclusions
This paper has analyzed whether the installation of distributed BESSs 
could be a techno-economic alternative to conventional network re­
inforcements under sustained load growth scenarios in a case study for a 
real 500-bus Spanish DN. The results illustrate that installing dedicated 
distributed BESSs can reduce peak loading in DNs and, thus, reduce the 
need for grid reinforcements in DNP. Nevertheless, the conditions under 
which BESSs become a cost-effective alternative are very specific, 
requiring small interannual load growth rates. These results highlight 
that BESS costs are still high compared to traditional DN reinforcements, 
which remain the best option when very high load growth is expected 
since power lines and transformers can provide electricity continuously 
if their rating is not exceeded. The reason for investing in BESS when 
small interannual load growths are expected is that the BESS is only 
required for peak shaving during a few peak load hours per year.
Moreover, the extended project duration of 16 years makes it diffi­
cult to recover the investments if demand is expected to increase rapidly. 
The capacity of BESS becomes insufficient to maintain the grid within its 
operating limits during peak load hours in a few years. Mobile BESSs 
have also been analyzed as an alternative for shortening the project 
duration and redeploying the BESS at another location.
The principal findings of the case study are:
Fig. 6. NPV of investing in a 715kWh mobile BESS at bus 498 for different 
interannual growth rates of peak demand and different project lengths (i.e., 
years the mobile BESS remains in this location).
Fig. 7. NPV of investing in a 715kWh BESS at bus 498 for different interannual 
growth rates of peak demand during a 16-year period. The different curves 
represent fractions of the total BESS cost that must be recovered from deferring 
investments in traditional network reinforcements.
M. Martínez et al.                                                                                                                                                                                                                              
Journal of Energy Storage 100 (2024) 113404 
6



<!-- page 7/9 -->

• Dedicated DSO-owned distributed BESSs are not usually a cost- 
effective option to delay network reinforcements in DN unless the 
DSO is certain that low load growth rates are expected.
• Considering distributed BESSs as mobile assets is not enough to make 
them a cost-efficient DNP alternative for medium or high sustained 
load growth scenarios. Increased utilization of the BESS does not 
overcome high transportation and installation costs at different 
locations.
• For all scenarios of sustained load growth in the case study, the 
portion of the BESS total cost that could be recouped through 
deferral of network reinforcements was higher than the fraction of 
total cycles required for peak shaving over their lifetime. If the 
remaining cycles of the BESS were used to provide additional cost- 
effective grid services, the BESS would become an economically 
viable solution. Thus, where allowed by the regulation, DSOs should 
consider combining network reinforcement deferral with other sys­
tem benefits (e.g., resilience) to increase BESS utilization hours and 
make them a cost-efficient network asset.
Regarding the last point, the system benefits achieved by grid rein­
forcement deferral would cover around 25 % of the investment under 
almost all interannual load growth rates that have been studied. Given 
that the BESS is only used for peak shaving during a few peak load days 
during the year, there is still room to leverage the BESS to provide other 
ancillary services that would result in additional benefits.
One limitation of the case study is that only one distribution grid has 
been analyzed. This study should be extended in future research to 
analyze more grids and scenarios (e.g., non-uniform load growth, future 
sustainable development scenarios with high adoption of heat pumps 
and EVs, etc.). Such studies could be complementary to the results of this 
paper to obtain a better understanding of the role of BESS in the DNP 
under a wider range of grid conditions. Another limitation of this study 
is the unavailability of data from real-world experiences, given that this 
application of BESSs is still relatively novel. Although the comprehen­
sive data for the electricity distribution grid was available through 
collaboration with the DSO, information on the costs for mobile BESS 
projects is scarce.
Besides replicating this case study in other grids and planning sce­
narios, future work should analyze in more detail the synergies that 
emerge from combining the deferral of investments in network re­
inforcements with other benefits, such as enhanced system reliability. 
Furthermore, an emerging alternative is for DSOs to contract congestion 
management and voltage control services from third-party-owned BESSs 
only when needed, instead of owning the BESS themselves. Therefore, 
future work should also compare the installation of DSO-owned BESSs 
with flexibility services provided by BESSs and DERs owned by third 
parties. Finally, this methodology could be adapted to analyze how 
BESSs can defer DN reinforcements under increasing DG penetration 
levels.
CRediT authorship contribution statement
Miguel Martínez: Writing – original draft, Visualization, Software, 
Methodology, Investigation, Conceptualization. Carlos Mateo: Writing 
– review & editing, Supervision, Methodology, Conceptualization. 
Tomas G´omez: Writing – original draft, Supervision, Methodology, 
Conceptualization. Beatriz Alonso: Writing – review & editing, Vali­
dation, Data curation. Pablo Frías: Writing – review & editing, 
Supervision.
Declaration of competing interest
The authors declare the following financial interests/personal re­
lationships which may be considered as potential competing interests: 
This paper is based on the research carried out in the Flexener project, 
funded by the “Centro para el Desarrollo Tecnol´ogico Industrial” (CDTI) 
of the Spanish Ministry of Science and Innovation, financed by the call 
“Misiones CDTI 2019” (project MIG-20201002).
Data availability
The data that has been used is confidential.
Acknowledgments
The authors would like thank Dr. Jose Pablo Chaves-´Avila and David 
Martín for their helpful guiding comments. This paper is based on the 
research carried out in the Flexener project, funded by the “Centro para 
el Desarrollo Tecnol´ogico Industrial” (CDTI) of the Spanish Ministry of 
Science and Innovation, financed by the call “Misiones CDTI 2019” 
(project MIG-20201002).
Table II 
Equivalent annual costs for power lines.
Identifier
Type
N◦of conductors
Capacity [MVA]
Investment cost [€/km]
O&M cost [€/km-yr.]
Equivalent annual cost [€/km-yr.]
MV-OL-1A
Overhead
1
6.06
58,518
607
4,292
MV-OL-1B
Overhead
1
9.53
65,020
675
4,770
MV-OL-1C
Overhead
1
14.72
71,522
742
5,246
MV-OL-2A
Overhead
2
12.12
77,829
808
5,709
MV-OL-2B
Overhead
2
19.05
86,476
897
6,343
MV-OL-2C
Overhead
2
29.44
95,124
987
6,978
MV-OL-3A
Overhead
3
18.19
90,117
935
6,610
MV-OL-3B
Overhead
3
28.58
100,131
1,039
7,345
MV-OL-3C
Overhead
3
44.17
110,144
1,143
8,079
MV-UC-1A
Underground
1
7.79
118,212
1,227
8,672
MV-UC-1B
Underground
1
12.99
131,347
1,363
9,635
MV-UC-1C
Underground
1
17.32
144,482
1,499
10,598
MV-UC-2A
Underground
2
15.59
197,415
2,049
14,482
MV-UC-2B
Underground
2
25.98
219,350
2,276
16,090
MV-UC-2C
Underground
2
34.64
241,285
2,504
17,699
MV-UC-3A
Underground
3
23.38
258,885
2,687
18,991
MV-UC-3B
Underground
3
38.97
287,650
2,985
21,100
MV-UC-3C
Underground
3
51.96
316,415
3,284
23,211
M. Martínez et al.                                                                                                                                                                                                                              
Journal of Energy Storage 100 (2024) 113404 
7



<!-- page 8/9 -->

Appendix A. Equipment techno-economic data
The cost of mobile BESS has been estimated by breaking down the components of the investment cost for a 1 MW-4 h LFP battery [37]. The first 
category accounts for the cost of the mobile BESS that will be exploited over a battery lifetime of 16 years in different locations. The BESS cost includes 
the battery modules, container, cabling, switchgear, HVAC, power conversion equipment, and energy management system. On the other hand, there 
are project-related costs for shipping and installing the BESS that will have to be assumed at each different location and, thus, have to be recovered 
while the BESS stays at that location. This second category includes project development, engineering and construction, system integration (including 
shipment of the BESS to the new site and onsite installation of HVAC, fire, and power conversion equipment), and grid integration. The resulting 
equivalent annual costs for BESS, depending on the years that the BESS remains at each location, are shown in Table I.
Table I 
Equivalent annual cost for mobile BESS given the number of years that the BESS stays at each location.
Years at the same location
16
8
4
2
1
Equivalent annual cost [€/kWh-yr.]
40.60
51.04
73.08
117.86
207.77
In addition, Table II shows the equivalent annual costs (i.e., annuitized investment cost plus annual operation and maintenance costs) for each type 
of power line in the catalog. These investment and O&M costs are determined based on the reference values in the Spanish regulation [38]. To 
compute equivalent annual costs, 5.58 % is used as the discount rate [39], and it is assumed that they have an expected life of 40 years. Moreover, for 
the 66/20 kV substation transformer, it is assumed that the investment cost is 19,223 €/MVA and the O&M costs are 517 €/MVA-yr. The resulting 
equivalent annual cost for the substation transformer is 1728 €/MVA-yr.
References
[1] M.T. Lawder, B. Suthar, P.W.C. Northrop, S. De, C.M. Hoff, O. Leitermann, M. 
L. Crow, S. Santhanagopalan, V.R. Subramanian, Battery energy storage system 
(BESS) and battery management system (BMS) for grid-scale applications, Proc. 
IEEE 102 (2014) 1014–1030, https://doi.org/10.1109/JPROC.2014.2317451.
[2] B. Mukhopadhyay, D. Das, Optimal multi-objective long-term sizing of distributed 
energy resources and hourly power scheduling in a grid-tied microgrid, Sustainable 
Energy, Grids and Networks 30 (2022) 100632, https://doi.org/10.1016/j. 
segan.2022.100632.
[3] European Commission, COMMISSION RECOMMENDATION of 14 March 2023 on 
Energy Storage – Underpinning a Decarbonised and Secure EU Energy System. 
https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023H0320(01, 
2023 (accessed July 23, 2023).
[4] M. Kleinberg, N.S. Mirhosseini, F. Farzan, J. Hansell, A. Abrams, W. Katzenstein, 
J. Harrison, M.A. Jafari, Energy storage valuation under different storage forms 
and functions in transmission and distribution applications, Proc. IEEE 102 (2014) 
1073–1083, https://doi.org/10.1109/JPROC.2014.2324995.
[5] L.A. Wong, V.K. Ramachandaramurthy, P. Taylor, J.B. Ekanayake, S.L. Walker, 
S. Padmanaban, Review on the optimal placement, sizing and control of an energy 
storage system in the distribution network, J Energy Storage 21 (2019) 489–504, 
https://doi.org/10.1016/j.est.2018.12.015.
[6] H. Saboori, R. Hemmati, S.M.S. Ghiasi, S. Dehghan, Energy storage planning in 
electric power distribution networks – a state-of-the-art review, Renew. Sust. 
Energ. Rev. 79 (2017) 1108–1121, https://doi.org/10.1016/j.rser.2017.05.171.
[7] G. Carpinelli, G. Celli, S. Mocci, F. Mottola, F. Pilo, D. Proto, Optimal integration of 
distributed energy storage devices in smart grids, IEEE Trans Smart Grid 4 (2013) 
985–995, https://doi.org/10.1109/TSG.2012.2231100.
[8] H. Saboori, R. Hemmati, Maximizing DISCO profit in active distribution networks 
by optimal planning of energy storage systems and distributed generators, Renew. 
Sust. Energ. Rev. 71 (2017) 365–372, https://doi.org/10.1016/j.rser.2016.12.066.
[9] S.F. Santos, D.Z. Fitiwi, M. Shafie-Khah, A.W. Bizuayehu, C.M.P. Cabrita, J.P. 
S. Catalao, New multistage and stochastic mathematical model for maximizing RES 
hosting capacity—part I: problem formulation, IEEE Trans Sustain Energy 8 (2017) 
304–319, https://doi.org/10.1109/TSTE.2016.2598400.
[10] G. Celli, F. Pilo, G. Pisano, G.G. Soma, Distribution energy storage investment 
prioritization with a real coded multi-objective Genetic Algorithm, Electr. Power 
Syst. Res. 163 (2018) 154–163, https://doi.org/10.1016/j.epsr.2018.06.008.
[11] J.H. Yi, R. Cherkaoui, M. Paolone, D. Shchetinin, K. Knezovic, Optimal co-planning 
of ESSs and line reinforcement considering the dispatchability of active 
distribution networks, IEEE Trans. Power Syst. 38 (2023) 2485–2499, https://doi. 
org/10.1109/TPWRS.2022.3181069.
[12] C. Gu, J. Wang, Y. Zhang, Q. Li, Y. Chen, Optimal energy storage planning for 
stacked benefits in power distribution network, Renew. Energy 195 (2022) 
366–380, https://doi.org/10.1016/j.renene.2022.06.029.
[13] J. Hjalmarsson, K. Thomas, C. Bostr¨om, Service stacking using energy storage 
systems for grid applications – a review, J Energy Storage 60 (2023) 106639, 
https://doi.org/10.1016/j.est.2023.106639.
[14] N.B. Arias, J.C. Lopez, S. Hashemi, J.F. Franco, M.J. Rider, Multi-objective sizing of 
battery energy storage systems for stackable grid applications, IEEE Trans Smart 
Grid 12 (2021) 2708–2721, https://doi.org/10.1109/TSG.2020.3042186.
[15] H. Mehrjerdi, E. Rakhshani, A. Iqbal, Substation expansion deferral by multi- 
objective battery storage scheduling ensuring minimum cost, J Energy Storage 27 
(2020) 101119, https://doi.org/10.1016/j.est.2019.101119.
[16] W. van Westering, H. Hellendoorn, Low voltage power grid congestion reduction 
using a community battery: design principles, control and experimental validation, 
Int. J. Electr. Power Energy Syst. 114 (2020) 105349, https://doi.org/10.1016/j. 
ijepes.2019.06.007.
[17] A. Inaolaji, X. Wu, R. Roychowdhury, R. Smith, Optimal allocation of battery 
energy storage systems for peak shaving and reliability enhancement in 
distribution systems, J Energy Storage 95 (2024) 112305, https://doi.org/ 
10.1016/j.est.2024.112305.
[18] L. Yao, Z. Damiran, W.H. Lim, Optimal charging and discharging scheduling for 
electric vehicles in a parking station with photovoltaic system and energy storage 
system, Energies (Basel) 10 (2017) 550, https://doi.org/10.3390/en10040550.
[19] Y. Yang, H. Li, A. Aichhorn, J. Zheng, M. Greenleaf, Sizing strategy of distributed 
battery storage system with high penetration of photovoltaic for voltage regulation 
and peak load shaving, IEEE Trans Smart Grid 5 (2014) 982–991, https://doi.org/ 
10.1109/TSG.2013.2282504.
[20] D.M. Greenwood, N.S. Wade, P.C. Taylor, P. Papadopoulos, N. Heyward, 
A probabilistic method combining electrical energy storage and real-time thermal 
ratings to defer network reinforcement, IEEE Trans Sustain Energy 8 (2017) 
374–384, https://doi.org/10.1109/TSTE.2016.2600320.
[21] A. Navon, R. Nitskansky, E. Lipman, J. Belikov, N. Gal, A. Orda, Y. Levron, Energy 
storage for mitigating grid congestion caused by electric vehicles: a techno- 
economic analysis using a computationally efficient graph-based methodology, 
J Energy Storage 58 (2023) 106324, https://doi.org/10.1016/j.est.2022.106324.
[22] R.H. Byrne, T.A. Nguyen, D.A. Copp, B.R. Chalamala, I. Gyuk, Energy management 
and optimization methods for grid energy storage systems, IEEE Access 6 (2018) 
13231–13260, https://doi.org/10.1109/ACCESS.2017.2741578.
[23] S. Giannelos, I. Konstantelos, G. Strbac, Option value of dynamic line rating and 
storage, in: 2018 IEEE International Energy Conference (ENERGYCON), IEEE, 
2018, pp. 1–6, https://doi.org/10.1109/ENERGYCON.2018.8398811.
[24] J. Kim, Y. Dvorkin, Enhancing distribution system resilience with mobile energy 
storage and microgrids, IEEE Trans Smart Grid 10 (2018) 4996–5006, https://doi. 
org/10.1109/TSG.2018.2872521.
[25] H. Saboori, Enhancing resilience and sustainability of distribution networks by 
emergency operation of a truck-mounted mobile battery energy storage fleet, 
Sustainable Energy, Grids and Networks 34 (2023) 101037, https://doi.org/ 
10.1016/j.segan.2023.101037.
[26] H.M.A. Ahmed, H.F. Sindi, M.A. Azzouz, A.S.A. Awad, Optimal sizing and 
scheduling of mobile energy storage toward high penetration levels of renewable 
energy and fast charging stations, IEEE Transactions on Energy Conversion 37 
(2022) 1075–1086, https://doi.org/10.1109/TEC.2021.3116234.
[27] S. Xia, Z. Wang, X. Gao, W. Li, Optimal planning of mobile energy storage in active 
distribution network, IET Smart Grid (2023), https://doi.org/10.1049/stg2.12139.
[28] S. Giannelos, P. Djapic, D. Pudjianto, G. Strbac, Quantification of the energy 
storage contribution to security of supply through the F-factor methodology, 
Energies (Basel) 13 (2020) 826, https://doi.org/10.3390/en13040826.
[29] M. Zidar, P.S. Georgilakis, N.D. Hatziargyriou, T. Capuder, D. ˇSkrlec, Review of 
energy storage allocation in power distribution networks: applications, methods 
and future research, IET Gener. Transm. Distrib. 10 (2016) 645–652, https://doi. 
org/10.1049/iet-gtd.2015.0447.
[30] Y.M. Atwa, E.F. El-Saadany, Optimal allocation of ESS in distribution systems with 
a high penetration of wind energy, IEEE Trans. Power Syst. 25 (2010) 1815–1822, 
https://doi.org/10.1109/TPWRS.2010.2045663.
[31] O. Babacan, W. Torre, J. Kleissl, Siting and sizing of distributed energy storage to 
mitigate voltage impact by solar PV in distribution systems, Sol. Energy 146 (2017) 
199–208, https://doi.org/10.1016/j.solener.2017.02.047.
M. Martínez et al.                                                                                                                                                                                                                              
Journal of Energy Storage 100 (2024) 113404 
8



<!-- page 9/9 -->

[32] M.H. Roos, D.A.M. Geldtmeijer, H.P. Nguyen, J. Morren, J.G. Slootweg, Optimizing 
the technical and economic value of energy storage systems in LV networks for 
DNO applications, Sustainable Energy, Grids and Networks 16 (2018) 207–216, 
https://doi.org/10.1016/j.segan.2018.08.001.
[33] Y. Zhang, Z.Y. Dong, F. Luo, Y. Zheng, K. Meng, K.P. Wong, Optimal allocation of 
battery energy storage systems in distribution networks with high wind power 
penetration, IET Renewable Power Generation 10 (2016) 1105–1113, https://doi. 
org/10.1049/iet-rpg.2015.0542.
[34] Y. Zheng, Z.Y. Dong, F.J. Luo, K. Meng, J. Qiu, K.P. Wong, Optimal allocation of 
energy storage system for risk mitigation of DISCOs with high renewable 
penetrations, IEEE Trans. Power Syst. 29 (2014) 212–220, https://doi.org/ 
10.1109/TPWRS.2013.2278850.
[35] J.J. Jamian, M.W. Mustafa, H. Mokhlis, M.A. Baharudin, Simulation study on 
optimal placement and sizing of battery switching station units using artificial bee 
colony algorithm, Int. J. Electr. Power Energy Syst. 55 (2014) 592–601, https:// 
doi.org/10.1016/j.ijepes.2013.10.009.
[36] REE, ESIOS, (2023). https://www.esios.ree.es/en (accessed March 5, 2024).
[37] V. Viswanathan, K. Mongird, R. Franks, X. Li, V. Sprenkle, R. Baxter, 2022 Grid 
Energy Storage Technology Cost and Performance Assessment, 2022.
[38] Orden IET/2660/2015, Ministerio de Industria, Energía y Turismo. https://www. 
boe.es/buscar/doc.php?id=BOE-A-2015-13488, 2015 (accessed September 2, 
2022).
[39] CNMC, Acuerdo por el que se aprueba la propuesta de metodología de c´alculo de la 
tasa de retribuci´on financiera de las actividades de transporte y distribuci´on de 
energía el´ectrica para el segundo periodo regulatorio 2020–2025, 2018.
[40] R.D. Zimmerman, C.E. Murillo-S´anchez, R.J. Thomas, MATPOWER: steady-state 
operations, planning, and analysis tools for power systems research and education, 
IEEE Trans. Power Syst. 26 (2011) 12–19, https://doi.org/10.1109/ 
TPWRS.2010.2051168.
[41] ENTSO-e, DSO Entity & ENTSO-E Public consultation on Network Code for 
Demand Response. https://consultations.entsoe.eu/markets/public-consultation-n 
etworkcode-demand-response/, 2023. (Accessed 5 March 2024).
M. Martínez et al.                                                                                                                                                                                                                              
Journal of Energy Storage 100 (2024) 113404 
9
