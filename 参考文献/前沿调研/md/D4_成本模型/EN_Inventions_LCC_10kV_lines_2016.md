<!--
source: D4_成本模型/EN_Inventions_LCC_10kV_lines_2016.pdf
sha256: 85a1374575d899b5a94e5f841581fbc7e7f46cdb1e433f4978012c142bf77c64
method: pymupdf
pages: 21
-->

<!-- page 1/21 -->

inventions
Article
Life Cycle Cost Analysis of Three Types of Power
Lines in 10 kV Distribution Network
Zhenyu Zhu 1, Siyao Lu 1, Bingtuan Gao 1,*, Tao Yi 2 and Bin Chen 2
1
School of Electrical Engineering, Southeast University, Nanjing 210096, China; 220152190@seu.edu.cn (Z.Z.);
220142182@seu.edu.cn (S.L.)
2
State Grid Fujian Electric Power Research Institute, Fuzhou 350007, China; 220152248@seu.edu.cn (T.Y.);
220152222@seu.edu.cn (B.C.)
*
Correspondence: gaobingtuan@seu.edu.com; Tel.: +86-25-8379-4163
Academic Editor: Josep M. Guerrero
Received: 18 August 2016; Accepted: 28 September 2016; Published: 10 October 2016
Abstract: There are three types of power lines in the 10 kV distribution network in China, i.e.,
copper power cables, overhead power conductors and aluminum alloy power cables. It is necessary
to give a comprehensive evaluation to choose the type of power line in some delicate practical
engineering. This paper presents a life cycle cost (LCC)-based analysis method for the three types
of power lines. An LCC model of the power line in the 10 kV distribution network is established,
which considers four parts: investment cost, operation and maintenance cost, failure cost and discard
cost. A detailed calculation model for the four parts is presented, and to calculate the failure cost, the
Monte Carlo algorithm is employed to simulate the values of expected energy not supplied (EENS).
Two practical 10 kV power line projects in Fujian Province in China were analyzed based on the
proposed LLC model and corresponding developed software, which has helped the power company
select the appropriate power line successfully.
Keywords: power line; distribution network; life cycle costs; Monte Carlo
1. Introduction
As we all known, the distribution network is one of the main sections of the power system and
takes the heavy responsibilities of social and economic development. Additionally, the 10 kV power
lines play signiﬁcant roles in the distribution network in China. Currently, three kinds of distribution
lines are used widely, including copper cable, overhead conductor and aluminum alloy cable. In China,
traditional distribution power lines are almost all copper cable and overhead conductor. In recent
years, the application of aluminum alloy cables is becoming more extensive in the distribution network.
The quantity of copper resources has been found in China to be about 89.72 million tons since 1949.
However, the quantity of aluminum resources has been found to be much more than copper, which is
about 3.87 billion tons. This indicates that China is lacking copper resources, but rich in aluminum
resources, which highlights the advantages of using aluminum alloy in electric cables. As a result, it is
necessary to study which kind of cable is the most economical in different practical situations.
There are many methods to modeling the economy of practical engineering projects,
representatively including the net present value method, the uniform annual value method, the
payback period method and the life cycle cost (LCC) method. The net present value method is a kind of
simple method used to evaluate the investment project. This method uses the net present beneﬁt and
net present investment cost to ﬁgure out the net present value, then according to the net present value
to evaluate the project [1,2]. The uniform annual value method is to convert the whole cash ﬂow or net
present value to the annual average net value according to the investment necessary remuneration rate.
It usually only contains the investment cost and the discard cost [3]. The payback period method is a
Inventions 2016, 1, 20; doi:10.3390/inventions1040020
www.mdpi.com/journal/inventions



<!-- page 2/21 -->

Inventions 2016, 1, 20
2 of 21
static method that is used to calculate the time to recover the total investment cost. It should be under
the normal operating conditions and take the amortization of intangible assets into consideration.
The payback period is measured by the rate of recovering the initial investment [4,5]. However, these
methods do not take the whole service life of a project into consideration, so their analyses are not
comprehensive. In some countries, such as America, a typical method was employed to measure the
economic difference among different plans, called the life cycle cost analysis (LCCA) [6–8]. LCCA is
an evaluation method of the project cost, which includes the investment cost of the project, also the
operation and maintenance cost, failure cost and all the other costs until the end of the engineering
project. The method evaluates the economic advantages and disadvantages of an engineering project
by comparing the whole cost of different plans during the whole life of it. Until now, some results
have been achieved in many engineering ﬁelds, which can provide experiences and references to other
applications. In [9], LCCA is used to calculate the greenhouse gas emissions of the small autonomous
hybrid power systems (SAHPS), which contributes to a better solution of the optimum economic
and environmental performance of SAHPS. With respect to power distribution planning, LCCA can
be used to establish the multi-objective function to ﬁnd the optimal location and capacity of future
substations, considering economy, reliability and safety [10].
The LCCA is a relatively comprehensive method in the economic evaluation of a project.
However, few quantitative research works were done for the LCC of the 10 kV distribution lines,
especially aluminum alloy cable, which has not been widely used. As a result, this paper aims to
concentrate on the LCC of the 10 kV distribution lines and to compare the three types of power lines in
two practical projects by quantitative analysis. During the calculation of the failure cost, the existing
LCCA method is based on the historical data of a past similar project. However, few historical data of
aluminum alloy cable can be found or be used. Therefore, to calculate the failure cost, it is necessary to
propose another method that takes the high randomness of the failure rate into consideration. In this
paper, a risk assessment model is proposed to evaluate the failure cost in the LCC, and the Monte
Carlo algorithm is employed to simulate the values of expected energy not supplied (EENS). The main
contributions of this paper are as follows.
•
A LCC model of the 10 kV distribution power lines is proposed, containing investment cost,
operation and maintenance cost, failure cost and discard cost.
•
A risk assessment model is proposed by using the Monte Carlo algorithm to evaluate the
failure cost.
•
Quantitative analysis and the comparison of the LCC of the 10 kV distribution lines are presented.
The rest of the paper is organized as follows. In Section 2, we divide the whole life of the
power cable into four parts, including investment, operation and maintenance, failure and discard.
By analyzing each part, the whole LCC model is established. On this basis, in Section 3, an LCC
evaluation software is developed to help calculate the LCC in projects. After that, two practical cases
in Fujian province in China are analyzed, using the model and software that we have proposed. At last,
conclusions are given in Section 4.
2. The Life Cycle Cost (LCC) Model
The LCC model of a power line is a model that analyzes the whole costs of a power line engineering
project, including design and construction, operation and maintenance, failure and discard. It takes
the safety and reliability of the line as the premise, the cost of the whole life cycle to be least as
the target, evaluating the different power lines to ﬁnd out the optimal power line plan in a project.
In order to improve the applicability of the model, the model of all kinds of power distribution lines is
considered [11]. Referring to a practical engineering project, the basic LCC framework is determined,
which is shown in Figure 1.
According to Figure 1, we have:
LCC = Ci + Co + Cf + Cd
(1)



<!-- page 3/21 -->

Inventions 2016, 1, 20
3 of 21
where Ci is the investment cost, Co is the operation and maintenance cost, Cf is the failure cost and
Cd is the discard cost. It should be noted that the above four components are already discounted into
present values. Speciﬁc modeling and analysis will be presented in the following parts.
LCC of 10 kV 
Distribution 
Power Lines
Investment Cost
Operation and 
Maintenance 
Cost
Failure Cost
Discard Cost
Design and Installation Cost
Other Cost
Purchasing Cost of Fixed Assets
Energy Consumption Cost
Inspection and Maintenance Cost
Recondition Cost
Other Cost
Repair Cost
Punishment Cost
Removal Disposal Cost
Subsequent Treatment Cost
Residual Cost
Early Retirement Loss
Cable, Accessories, 
Land acquisition
Line measure fee, 
Accessories, 
Land acquisition, Machine,
Transportation, Labor,
 Service charges
In cable cores, 
In insulating medium
Environmental inspection,
 Professional inspection,
Ground temperature 
detection,
 Induction current testing
Labor, Machine, Material
Direct punishment cost,
Indirect punishment cost
Labor, Machine, 
Transportation
Land usage, 
Remove pole-tower,
Leveling land
Wire, Accessories
Figure 1. Basic life cycle cost (LCC) framework.
2.1. Investment Cost
The investment cost of a power line is a one-time cost that is paid during the design, installation
and commissioning, before the project is ofﬁcially put into operation. It is symbolized as Ci. It mainly
includes the purchasing cost of ﬁxed assets and the design and installation cost. To express the whole
investment cost, we have:
Ci
=
Cf i + Cci + Coi
(2)
Cf i
=
(Cmi + Cai + Cli)I1
(3)
where Cf i is the purchasing cost of ﬁxed assets, including the purchasing cost of the cable Cmi and
the purchasing cost of accessories Cai, and if it is an overhead conductor, it should also include the land
acquisition cost Cli. For ﬁxed assets, because of its time value, which means it has a different value
at different time points, it is necessary to consider the discount coefﬁcient I1 according to the service
life [12]. However, we discount the cost to the present, so I1 = 1. Cci is the cost for the design and
installation of the line, including the line measure cost, special tools and the initial cost of spare parts,
machinery and transportation cost, labor and service charges, installation and commissioning cost, etc.
Coi is other costs, including the cost of possible forest cutting and foundation construction, etc.
2.2. Operation and Maintenance Cost
After the construction of the power line is completed, it will be put into operation. At this stage,
some costs will be produced, that is the operation and maintenance costs. We use Co to represent the



<!-- page 4/21 -->

Inventions 2016, 1, 20
4 of 21
operation and maintenance cost, which includes the total cost in the operation period of a power line.
We have:
Co
=
(Ceo + Clo + Cco + Coo)I2
(4)
I2
=
(1 + i)n −1
i(1 + i)n
(5)
where Ceo is the energy consumption cost, which means the energy loss of a power line converted to
money; Cio is the inspection and maintenance cost, including inspection machine cost, tool cost and
labor cost; Cco is the recondition cost, including recondition machine cost, material cost, service cost
and labor cost; other possible costs are included in Coo; I2 is also a discount coefﬁcient, in which i is the
annual discount rate and n is the service life.
2.2.1. Energy Consumption Cost
After the power line is put into operation, the main operation cost is the energy consumption cost,
which is related to the physical characteristics and operation state of the line. According to [13,14],
for overhead conductors, we can formulate the energy consumption cost as follows:
Ceo = 3I2
maxRLTrP(1 + ip)np −1
ip
× 10−6
(6)
where Imax is the maximum load current; R is the AC resistance; L is the length of the power line; T is
the operating hour of one year; r is the annual average load rate; P is the cost price of electricity per
kilowatt; ip is the annual increasing rate of the electricity price; np is calculation years.
For cables, beside the energy consumption in cable cores, which is calculated before, the energy
consumption in the dielectric medium should be calculated, as well. We have:
C′′
eo
=
Ceo + C′
eo
(7)
C′
eo
=
2π fU2C tan δTLP(1 + ip)np −1
ip
× 10−6
(8)
where C′
eo is the energy consumption in the dielectric medium; f is the frequency of the electric system;
U is the operation line voltage; C is the working capacitance of cable per phase; tan δ is the value of
the dielectric loss tangent.
Therefore, Equation (7) is the total energy consumption cost for cables.
2.2.2. Maintenance Cost
In order to ensure the safety and reliability of the power line, power companies need to have
regular inspection and maintenance of the power line. The cost consumed can be formulated as follows:
Clo = (p1t1 + p2t2)Ln
(9)
where p1 is the inspection cost each time, including the environmental inspection cost, professional
inspection cost, ground temperature detection cost and induction current testing cost; p2 is the regular
maintenance cost; L is the length of the line; n is the service life; t1 is the inspection cycle; t2 is the
maintenance cycle.



<!-- page 5/21 -->

Inventions 2016, 1, 20
5 of 21
2.2.3. Recondition Cost
When the power line is running for a period of time, it is necessary to recondition it to eliminate
the hidden trouble and ensure the stability of the line. The cost consumed can be formulated as follows:
Cco = pLn
t
(10)
where p is the inspection cost each time; t is the inspection cycle; L is the length of the line; n is the
service life.
2.3. Failure Cost
2.3.1. Risk Assessment Model
The failure cost of the power line is inﬂuenced by multiple factors, which are deﬁned as economic
losses caused by power outages. Power companies need to schedule maintenance when power lines
have faults. Maintenance cost is related to fault times, which can be calculated as:
Ccm f = λNCm f
(11)
where Ccm f is the maintenance cost; λN is fault time; Cm f is the average maintenance cost of each fault
for the cable, which includes labor cost, equipment cost and material cost.
Apart from maintenance, the line fault will also break the power supply, which may cause loss to
power companies. The loss cost can be separated into two parts: direct failure cost and indirect failure
cost. Direct failure cost can be considered from the perspective of interruption cost [15,16]. In this
paper, the expected energy not supplied is used to characterize the magnitude of the direct failure cost,
which can be described as:
Cd f = pEENS
(12)
where Cd f is the direct failure cost; p is the purchase and marketing price differentials of electricity,
which generally is 0.3; EENS is the value of the expected energy not supplied, which can be
calculated as:
EENS = λNLT
(13)
where L is load to the cable supply; T is the time for fault maintenance. Load can be obtained by
predicting, although there often is a certain deviation. The actual load can be calculated as follows:
L = LE (1 −Ld)
(14)
where LE is the predictive value of the load; Ld is the deviation rate of predictive value LE, which obeys
the law of a normal distribution [17]. The corresponding probability density function is deﬁned as:
f (Ld) =
1
√
2πσ
exp
 
−(Ld −Ed)2
2σ2
!
(15)
where Ed is the mean value of the load forecasting deviation rate; σ2 is the variance of the load
forecasting deviation rate. The maintenance process of the fault is inﬂuenced by many factors, such
as location, weather condition, maintenance level, and so on. Fault maintenance time is a random
variable, which obeys an exponential distribution [18]. The corresponding probability density function
is deﬁned as:
f (T) = µe−µT
(16)
where µ is the distributed parameter, the reciprocal if which is the mean value of the fault maintenance
time TE, namely TE = 1
µ.



<!-- page 6/21 -->

Inventions 2016, 1, 20
6 of 21
The indirect failure cost includes the cost of compensation, the impact on social production and
the credibility of power companies. Because some adverse effects cannot be measured by money, it is
difﬁcult to estimate the indirect losses. The direct failure cost and a reasonable coefﬁcient a can be used
to indicate the value of indirect failure cost, namely,
Ci f = aCd f
(17)
where Ci f is the indirect failure cost. For different kinds of users, the social impact caused by supply
interruption is different. Thus, the corresponding coefﬁcient a is different for users. The Delphi method
can be used to obtain the value of coefﬁcient a.
In summary, the failure cost includes the maintenance cost caused by the fault and the direct
failure cost and the indirect failure cost caused by supply interruption, which can be described as:
C′
f
=
Ccm f + Cd f + Ci f
=
Ccm f + (1 + a) pEENS
=
λN
h
Cm f + (1 + a) pLT
i
(18)
where C′
f denotes the failure cost.
Equipment maintenance risk, lack of power supply risk, reputation risk, social impact risk and
compensation risk are fully considered when calculating the failure cost. Thus, the failure cost can not
only measure the loss caused by supply interruption and inﬂuence the reliability of the system, but also
measure the adverse impact of the social production and reputation of the electric power company.
2.3.2. Risk Assessment Method
Model of the Fault Rate
From Equation (18), we can see that the value of the failure cost has a close relationship with the
fault times. Failure of the cable is the result of the common interaction of itself and the external factors.
The main factors of the cable itself include material defects, improper installation process, and so on.
Meanwhile, the main external factors include external damage, insulation aging, chemical corrosion,
insulation moisture and other factors. These factors constitute the source of the risk of cable failure.
The running state of the cable within the whole life cycle can also be expressed by the failure rate.
The relationship between fault times and the failure rate can be described as follows [19]:
λ = 100λN
Tel
(19)
where λ is the failure rate, Te is the exposure time corresponding to the failure times and l is the length
of the cable. For the convenience of comparison between different cable failure costs and the use of the
fault cost model, fault times λN in Equation (18) are replaced by the failure rate λ.
Therefore, the failure cost per 100 km of cable per year Cf can be calculated as:
Cf = λ
h
Cm f + (1 + a) pLT
i
(20)
As shown in Figure 2, the failure rate in the whole life cycle of the cable is the curve with time,
which is called the bathtub curve. In the ﬁrst stage, quality problems caused by manufacturing will be
exposed, which result in a high failure rate; in the third stage of the life cycle, aging of the cable causes
the failure rate to increase gradually. However, the duration of the ﬁrst stage is very short. Meantime,
the cable usually will be replaced before reaching the third stage, and the time of the third stage is
short. In this paper, we assume that the failure rate does not change with time during the entire life



<!-- page 7/21 -->

Inventions 2016, 1, 20
7 of 21
cycle when calculating the failure cost. Namely, the failure rate of each year is the same and can be
obtained from history data statistics.
Failure Simulation Method
The Monte Carlo method is a stochastic simulation method based on probability and statistical
theory [20] , which is used to simulate the random process of cable failure when calculating the failure
cost. The speciﬁc steps are:
•
Firstly, the normal distribution probability model of the deviation rate of the predictive load
and the exponential distribution of the probability distribution of the fault maintenance time
are established;
•
Then, sampling the values of predictive load and fault maintenance time;
•
Finally, calculating the indexes by the statistical method.
Time
Failure Rate
steady
state
wear out 
failure
λ(t)
t
infant
mortality
Figure 2. Proﬁle of the failure rate.
For the failure cost model above, the Monte Carlo method can be applied to get the value of the
expected energy-not-supplied EENS, which is related to the two random variables, predictive load and
fault maintenance time. For each value of load L, it has corresponding probability P1 (L). Similarly,
for each fault maintenance time T, it has corresponding probability P2 (T). Let ES denote the result of
an experiment, namely,
ES (L, T) = λLT
(21)
Load L and failure maintenance time T are random variables. Thus, the result of an experiment
also is a random variable, the expected value of which can be calculated as:
E (ES (L, T)) = ∑ES (L, T) P1 (L) P2 (T)
(22)
where E (ES (L, T)) denotes the expected value of ES (L, T), which can be estimated as follows:
ˆE (ES (L, T)) = 1
N
N
∑
i=1
ESi (Li, Ti)
(23)
where ˆE (ES (L, T)) is the estimate of the expected value of ES (L, T); N is the sampling times; Li is
the value of the load for the i-th sample; Ti is the value of the load for the i-th sample; ESi (Li, Ti) is
the result of the i-th sample. From Equation (23), one can see that ˆE (ES (L, T)) is not the truth-value



<!-- page 8/21 -->

Inventions 2016, 1, 20
8 of 21
of E (ES (L, T)). Due to the fact that ES (L, T) is a random variable, expected value ˆE (ES (L, T)) is a
random variable, the error of which is determined by its variance.
V
  ˆE (ES (L, T))
 = V (ES (L, T))
N
(24)
where V
  ˆE (ES (L, T))

is the variance of the estimate of E (ES (L, T)); V (ES (L, T)) is the variance of
ES (L, T), which can be estimated as follows:
ˆV (ES (L, T)) = 1
N
N
∑
i=1

ESi (Li, Ti) −ˆE (ES (L, T))
2
(25)
Equation (24) indicates that the estimation error is proportional to the variance V (ES (L, T)) and is
inversely proportional to the sampling times N. The convergence criterion of the Monte Carlo method
is based on the error of ˆE (ES (L, T)), which is the estimated value of E (ES (L, T)). The criterion is
usually expressed as follows:
U =
q
V
  ˆE (ES (L, T))

ˆE (ES (L, T))
(26)
where U is the variance coefﬁcient. Then, we can get:
U =
q
V(ES(L,T))
N
ˆE (ES (L, T))
(27)
Therefore,
N =
V (ES (L, T))
 U ˆE (ES (L, T))
2
(28)
From Equation (28), one can see that the amount of the calculation of the Monte Carlo method
has little inﬂuence on the size or complexity of the system.
2.3.3. Line Fault Simulation
Based on the failure cost risk assessment model and the probability distribution model of load
and failure maintenance time above, MATLAB R2013a (MathWorks, Natick, MA, USA) is used to
realize the random simulation process of the line fault. The risks of copper cable and aluminum alloy
cable are simulated in the numerical simulations. Assuming that two types of cable are under the
same condition of operation, the system parameters are as follows: the load power of the cable supply
L = 300 kW; the expectation of the 4load forecasting deviation rate is 1.06%; the variance of the load
forecasting deviation rate is 0.87%; the coefﬁcient between the indirect failure cost and the direct
failure cost a = 20; the average maintenance cost of the fault for cable Cm f = 0.2 million RMB per
100 km. The convergence criterion of the Monte Carlo simulation is the variance coefﬁcient of the
expected energy not supplied less than 0.01. The failure rate and the mean failure maintenance time
of aluminum alloy cable and copper cable are obtained from State Grid Company. The failure rate
of the aluminum alloy cable is 2.2-times per year per 100 km, while the failure rate of copper cable is
two-times per year per 100 km. The mean failure maintenance time of aluminum alloy cable is TE = 8 h
per time, while the mean failure maintenance time of copper cable is TE = 8.8 h per time. Simulation
results are shown in Figures 3 and 4. We can see that the simulation of the energy-not-supplied for
both cables can be convergent after 3000-times of sampling. The expected energy-not-supplied of the
aluminum alloy cable is EENSc = 5253.59 kW·h, while it is EENSc = 4847.78 kW·h for copper cable.



<!-- page 9/21 -->

Inventions 2016, 1, 20
9 of 21
×104
0
500
1000
1500
2000
2500
3000
0
0.5
1
1.5
2
2.5
3
3.5
4
4.5
5
Iterations
Energy Not Supplied(kW·h)
 
 
Experiment
Average
Figure 3. Expected energy not supplied for the aluminum alloy cable.
×104
0
500
1000
1500
2000
2500
3000
0
0.5
1
1.5
2
2.5
3
3.5
4
4.5
Iterations
Energy Not Supplied(kW·h)
 
Experiment
Average
Figure 4. Expected energy not supplied for the copper cable.
2.4. Discard Cost
Discard cost Cd refers to the cost that is used to clean up and destroy the engineering project after
its service life has ended. Part of the equipment has residual value, which can be sold to get some
economic beneﬁts. The discard cost of the power line includes the economic loss of early retirement
and removal disposal cost, and it should have the residual cost subtracted. We have:
Cd
=
(Crd + Cdd −Csd)I3
(29)
I3
=
1
(1 + i)n
(30)
where Crd is the economic loss of early retirement; Cdd is the removal disposal cost; Csd is the residual
cost; I3 is the discount rate of the last year.
For cables, residual cost can be divided into:
Cdd = Cld + Cmd + Ctd + Cgd
(31)



<!-- page 10/21 -->

Inventions 2016, 1, 20
10 of 21
where Cld is the labor cost for removing the line; Cmd is the machine cost for removing the line; Ctd is
the transportation cost; Cgd is the land usage cost, which is converted by the land volume occupied by
the insulation and sheath materials.
The residual cost Csd can be formulated as:
Csd=McLPc + ∑MiLPi
(32)
where Mc is the metal weight of the line per kilometer; L is the length of the line; Pc is the unit price of
the discarded metal of the line; Mi is the metal weight of the accessories per kilometer; Pi is the unit
price of the discarded metal of the accessories.
For overhead conductors, the discard cost does not include the land usage cost because of no
insulation and sheath materials. However, Cf d, which is the cost of removing the pole tower and
leveling land, should be included. Therefore, we have:
C′
d = Crd + Cld + Cmd + Ctd + Ced + Cf d −Csd
(33)
2.5. Discussion of Three Types of Cable
Until now, the model of each period of LCC has been established. Combining the four parts
together, Equation (1) can be obtained as the LCC model of the power lines. For different types of
power lines, the main methods of calculating LCC cost are similar. However, there are some detailed
differences. For instance, the accessories of aluminum alloy cable and overhead conductor are different,
resulting in their different investment cost; the cables have energy consumption in the insulating
medium when calculating operation and maintenance cost, but the overhead conductor does not;
the overhead conductor does not have land usage cost, but has leveling land cost compared to cables.
Therefore, one should take notice of these differences.
3. Software Development and Case Analysis
3.1. Software Development
To improve the convenience of the LCC model for power lines in the distribution network and
make it easy to use, an LCC evaluation software based on the model we have built is developed.
The software is designed with object-oriented programming ideas. C++ is used as the development
language, and Microsoft Visual Studio 2010 (Microsoft, Redmond, WA, USA) is used as the integrated
development tool. The ﬂow chart of the software is shown in Figure 5, and parts of the interface are
shown in Figure 6.
The software calculates the LCC of a power line according to the data provided by the power
company and the parameters of the line and uses the line graphs and the bar charts to visually display
the results of each part, which can make the user clear of the ratio of each part at a glance and can
provide a better reference for the LCC control or the cable selection based on LCC. The whole software
is divided into ﬁve parts, and they are the investment cost part, the operation and maintenance cost
part, the failure cost part, the discard cost part and the total cost part. Each part uses a separate
interface. The ﬁrst four computing interfaces have their own data input frame, the result display
frame and the drawing module. The last total cost interface is used to compare each part of the cost,
using bar charts and line graphs to clearly show the proportion and the trend of each part of the cost.
When the software initializes, each data input frame has a default value. If users want to change the
data, they can input new data to the data input frame manually. The input parameters will be imported
into the background program and handled. Then, the software will update the calculated results and
draw the line graphs and bar charts in real time. The software has a high running efﬁciency and is
easy to operate; therefore, it greatly improves the convenience of the application of the LCC model in
practical power line projects.



<!-- page 11/21 -->

Inventions 2016, 1, 20
11 of 21
Start
Select 
Calculation Part 
Select Line Type
Modify Default Data
Modify Data
Calculate the Cost
Draw Bar Charts
Draw Line Graphs
Data is Reasonable
Finish
N
Y
Y
N
Figure 5. Flow chart of the software.
AAC
CC
OC
Load
Length(km)
Years
Discount Rate
Land Acquisition
Wire Cost
(RMB/km)
(RMB/km)
(RMB/km)
(RMB/km)
(RMB/km)
Accessories Cost
Installation Cost
Other Cost
Calculation
Clear
1.437
30
0.05
278
800
800
400
Cancel
Investment Cost Operation Cost
Failure Cost
Discard Cost
Total Cost
167000
836000
84000
751100
754200
813500
85400
158700
29900
70600
71000
22500
1167300
1883500
983400
58455
566109
20807
15.65
Price
(RMB)
(RMB)
(RMB)
(RMB)
(RMB)
(RMB)
(RMB)
Total Cost
Investment Cost
Land Acquisition
Wire Cost
Accessories Cost
Installation Cost
Other Cost
Investment Cost
AAC
CC
OC
Data and Figure Export
Parameters
OC
Figure 6. Calculation interface of the software. AAC, aluminum alloy cable; CC, copper cable;
OC, overhead conductor.



<!-- page 12/21 -->

Inventions 2016, 1, 20
12 of 21
3.2. Case 1
According to the LCC model that has been built, we choose two practical engineering projects
in Fujian province of China for case analysis, using the LCC calculation software. The ﬁrst case is a
10-kV power line in a southern county of Fujian province, and aluminum alloy cable, copper cable
and overhead conductor are used, respectively. Taking the practical situation into consideration, the
model of aluminum alloy cable is YJLHV22-3 × 300; the model of the copper cable is YJV22-3 × 240;
and the model of the overhead conductor is LGJ-240. The purchasing parameters, physical parameters,
operation and maintenance parameters, failure parameters and discard parameters are respectively
shown in Tables 1–5. For convenience, the aluminum alloy cable is abbreviated as ACC, the copper
cable as CC and the overhead conductor as OC.
We calculate the LCC of this power line in a design life of 30 years. The results are drawn in
Figures 7–11.
Table 1. Purchasing parameters in Case 1. AAC, aluminum alloy cable; CC, copper cable; OC, overhead
conductor.
Parameter
AAC
CC
OC
Purchasing Cost of Wire (RMB)
167,000
836,000
84,000
Purchasing Cost of Accessories (RMB)
751,100
754,200
813,500
Land Acquisition Cost (RMB)
800
800
400
Design and Installation Cost (RMB)
85,400
158,700
29,900
Other Cost (RMB)
70,600
71,000
22,500
Table 2. Physical parameters in Case 1.
Parameter
AAC
CC
OC
Wire Length (m)
1437
1437
1437
Maximum Load Current (A)
430
430
430
Line Voltage (kV)
10
10
10
AC Resistance (Ω)
0.131
0.0972
0.132
Operating Hour of One Year (h)
8760
8760
8760
Annual Average Load Rate (%)
45.66
45.66
45.66
Frequency (Hz)
50
50
50
Phase Working Capacity (µF)
0.341
0.330
0
Dielectric Loss Tangent
0.008
0.008
0
Table 3. Operation and maintenance parameters in Case 1.
Parameter
AAC
CC
OC
Electricity Purchasing Price (RMB)
0.4
0.4
0.4
Electricity Sale Price (RMB)
0.5
0.5
0.5
Price Annual Increasing Rate (%)
2.0
2.0
2.0
Annual Discount Rate (%)
5
5
5
Inspection Cost (RMB)
125,300
91,100
5600
Inspection Cycle (times per year)
1
1
1
Maintenance Cost (RMB)
6300
4353
5853
Maintenance Cycle (times per year)
12
12
12
Recondition Cost (RMB)
8350
6530
8780
Recondition Cycle (times per year)
12
12
12



<!-- page 13/21 -->

Inventions 2016, 1, 20
13 of 21
Table 4. Failure parameters in Case 1.
Parameter
AAC
CC
OC
Load Power (kW·h)
4300
4300
4300
Expectation of Load Forecasting Deviation Rate
1.06
1.06
1.06
Variance of Load Forecasting Deviation Rate
0.66
0.87
0.95
Failure Rate (times/year·100 km)
2.2
2
2.1
Average Failure Maintenance Time (h)
8
8.8
6
Coefﬁcient between Indirect Failure Cost and Direct Failure Cost
20
20
20
Average Repair Cost (RMB/km)
3740
3566
2114
Table 5. Discard parameters in Case 1.
Parameter
AAC
CC
OC
Removal Disposal Cost (RMB)
10,345
13,753
3129
Subsequent Treatment Cost (RMB)
2047.7
2047.7
8372
Metal Weight of Wire (t/km)
2.44
6.41
1.108
Metal Weight of Accessories (t/km)
0.3
0.3
1.0
Recycling Price of Aluminum Alloy (RMB/t)
12,110
–
–
Recycling Price of Copper (RMB/t)
–
30,800
–
Recycling Price of Steel (RMB/t)
–
–
5500
Service Life (Year)
LCC ×106 (RMB)
Aluminum Alloy Cable
Copper Cable
Overhead Conductor
0
1
2
3
4
5
6
7
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
Figure 7. LCC during 30 years in Case 1.
Aluminum 
Alloy Cable
Copper
Cable
Overhead
Conductor
Investment Cost
 ×105 (RMB)
0
2
4
6
8
10
12
14
16
18
20
Figure 8. Investment cost during 30 years in Case 1.



<!-- page 14/21 -->

Inventions 2016, 1, 20
14 of 21
Service Life (Year)
Operation Cost
×106 (RMB)
1
3
5
7
9
11
13
15
17
19
21
23
25
27
29
0
1
2
3
4
5
6
Aluminum Alloy Cable
Copper Cable
Overhead Conductor
Figure 9. Operation and maintenance cost during 30 years in Case 1.
Service Life (Year)
Failure Cost
×105 (RMB)
1
3
5
7
9
11
13
15
17
19
21
23
25
27
29
0
2
4
6
8
10
12
14
Aluminum Alloy Cable
Copper Cable
Overhead Conductor
Figure 10. Failure cost during 30 years in Case 1.
-30
-25
-20
-15
-10
-5
0
Discard Cost
×104 (RMB)
Service Life (Year)
1
3
5
7
9
11
13
15
17
19
21
23
25
27
29
Aluminum Alloy Cable
Copper Cable
Overhead Conductor
Figure 11. Discard cost during 30 years in Case 1.



<!-- page 15/21 -->

Inventions 2016, 1, 20
15 of 21
3.2.1. Case 1 Result Analysis
From Figures 7–11, the detailed analyses are as follows.
Each part of LCC
•
Investment cost:
From Figure 8, it is clear that the overhead conductor is the most economical line, while the
copper cable requires the highest investment cost.
•
Operation and maintenance cost:
Figure 9 indicates that the overhead conductor is still the most economical line, but the aluminum
alloy cable becomes the most expensive line in this period.
•
Failure cost:
From Figure 10, it can be seen that the aluminum alloy cable has the least failure cost, while the
overhead conductor has the most.
•
Discard cost:
Figure 11 illustrates that the copper cable has the least discard cost while the overhead conductor
has the top cost. It is necessary to point out that the discard cost is negative because the residual
cost of power lines is actually a kind of income. By recycling and selling the discard power line
materials, the income can be used to offset the cost in other parts. As a result, the lower the
discard cost is, the more it does to reduce the total LCC.
Inﬂuence degree of each part to LCC
In Case 1, the load rate is low; therefore, the operation and maintenance cost does not have the
biggest inﬂuence on the LCC. Figures 8–11 indicate that the investment cost takes the most part of the
LCC while the failure cost and the discard cost have a minor inﬂuence on the LCC.
LCC balance point
From Figure 7, it can be seen that the LCC line graph of aluminum alloy cable has an intersection
with the LCC line graph of the copper cable in the ninth year. This indicates that when the service
life is less than nine years, the aluminum alloy cable has an economic advantage. However, due to
short length and low load rate of the line, the advantage is not obvious. When the service life is longer
than nine years, the copper cable is more economical. Although the investment cost of copper cable is
higher, the energy loss is smaller, which leads to an advantage in long-term operation.
It is clear that the overhead conductor has an obvious economic advantage throughout the whole
service life compared to other lines, due to two characteristics of the overhead conductor: the low
investment cost and the low maintenance cost.
Therefore, when designing short-length and low load rate power lines, represented by Case 1,
the overhead conductor is the most economical.
3.3. Case 2
The second line is a dual-circuit 10-kV power line, which is in a northern county of Fujian
province. The model of aluminum alloy cable is YJLHV22-3 × 400; the model of the copper cable is
YJV22-3 × 300; and the model of the overhead conductor is LGJ-240. The calculation parameters are
shown in Tables 6–10.
The LCC of this power line is ﬁgured out in a lifespan of 30 years. The line graphs are shown in
Figures 12–16.



<!-- page 16/21 -->

Inventions 2016, 1, 20
16 of 21
Table 6. Purchasing parameters in Case 2.
Parameter
AAC
CC
OC
Purchasing Cost of Wire (RMB)
817,000
3,249,000
288,000
Purchasing Cost of Accessories (RMB)
119,800
112,100
77,200
Land Acquisition Cost (RMB)
800
800
400
Design and Installation Cost (RMB)
467,500
597,000
865,500
Other Cost (RMB)
100,600
107,500
33,600
Table 7. Physical parameters in Case 2.
Parameter
AAC
CC
OC
Wire Length (m)
4908
4908
4908
Maximum Load Current (A)
495
495
495
Line Voltage (kV)
10
10
10
AC Resistance (Ω)
0.103
0.0788
0.132
Operating Hour of One Year (h)
8760
8760
8760
Annual Average Load Rate (%)
62.79
62.79
62.79
Frequency (Hz)
50
50
50
Phase Working Capacity (µF)
0.382
0.370
0
Dielectric Loss Tangent
0.008
0.008
0
Table 8. Operation and maintenance parameters in Case 2.
Parameter
AAC
CC
OC
Electricity Purchasing Price (RMB)
0.2
0.2
0.2
Electricity Sale Price (RMB)
0.5
0.5
0.5
Price Annual Increasing Rate (%)
2.0
2.0
2.0
Annual Discount Rate (%)
5
5
5
Inspection Cost (RMB)
250,600
182,200
18,800
Inspection Cycle (times per year)
1
1
1
Maintenance Cost (RMB)
4410
3208
1984
Maintenance Cycle (times per year)
12
12
12
Recondition Cost (RMB)
6614
4812
2976
Recondition Cycle (times per year)
12
12
12
Table 9. Failure parameters in Case 2.
Parameter
AAC
CC
OC
Load Power (kW·h)
4950
4950
4950
Expectation of Load Forecasting Deviation Rate
1.06
1.06
1.06
Variance of Load Forecasting Deviation Rate
0.66
0.87
0.95
Failure Rate (times/year·100 km)
2.2
2
2.1
Average Failure Maintenance Time (h)
8
8.8
6
Coefﬁcient between Indirect Failure Cost and Direct Failure Cost
20
20
20
Average Repair Cost (RMB/km)
6588
10,980
2745



<!-- page 17/21 -->

Inventions 2016, 1, 20
17 of 21
Table 10. Discard parameters in Case 2.
Parameter
AAC
CC
OC
Removal Disposal Cost (RMB)
17,666
23,486
5344
Subsequent Treatment Cost (RMB)
3496.9
3496.9
14,297
Metal Weight of Wire (t/km)
3.252
8.01
2.655
Metal Weight of Accessories (t/km)
0.3
0.3
1.0
Recycling Price of Aluminum Alloy (RMB/t)
12,110
–
–
Recycling Price of Copper (RMB/t)
–
30,800
–
Recycling Price of Steel (RMB/t)
–
–
5500
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 2526 27 28 29 30
Aluminum Alloy Cable
Copper Cable
Overhead Conductor
LCC ×106 (RMB)
0
5
10
15
20
25
Service Life (Year)
Figure 12. LCC during 30 years in Case 2.
Aluminum 
Alloy Cable
Copper
Cable
Overhead
Conductor
Investment Cost
 ×105 (RMB)
0
10
20
30
40
50
Figure 13. Investment cost during 30 years in Case 2.



<!-- page 18/21 -->

Inventions 2016, 1, 20
18 of 21
1
3
5
7
9
11
13
15
17
19
21
23
25
27
29
Aluminum Alloy Cable
Copper Cable
Overhead Conductor
Operation Cost
×106 (RMB)
0
2
4
6
8
10
12
14
16
18
Service Life (Year)
Figure 14. Operation and maintenance cost during 30 years in Case 2.
0
5
10
15
20
25
30
1
3
5
7
9
11
13
15
17
19
21
23
25
27
29
Aluminum Alloy Cable
Copper Cable
Overhead Conductor
Failure Cost
×105 (RMB)
Service Life (Year)
Figure 15. Failure cost during 30 years in Case 2.
1
3
5
7
9
11
13
15
17
19
21
23
25
27
29
Aluminum Alloy Cable
Copper Cable
Overhead Conductor
Discard Cost 
×105 (RMB)
-14
-12
-10
-8
-6
-4
-2
0
Service Life (Year)
Figure 16. Discard cost during 30 years in Case 2.



<!-- page 19/21 -->

Inventions 2016, 1, 20
19 of 21
3.3.1. Case 2 Result Analysis
From Figures 12–16, the detailed analyses are as follows.
Each part of LCC
•
Investment cost:
Figure 13 shows that the investment cost of the overhead conductor is the least, while the
investment cost of copper cable is the highest.
•
Operation and maintenance cost:
Figure 14 indicates that the operation and maintenance cost of copper cable is the least. However,
the aluminum alloy cable and overhead conductor are similar.
•
Failure cost:
From Figure 15, it can be seen that the failure cost of aluminum alloy cable is less than copper,
cable and the failure cost of copper cable is less than the overhead conductor.
•
Discard cost:
Figure 16 illustrates that the discard cost of copper cable is the least, while the discard cost of the
overhead conductor is the most.
Inﬂuence degree of each part to LCC
In Case 2, due to the high load rate, the operation and maintenance cost becomes the most
important inﬂuence factor of the LCC. Figures 13–16 show that the investment cost takes the second
place, and the failure cost and the discard cost still have a minor inﬂuence on the LCC.
LCC balance point
From Figure 12, it can be seen that the LCC balance point of the three lines appears at the
7th–8th year. In other words, when the service life is less than seven years, the copper cable is the most
expensive, resulting from its high investment cost. Besides, the LCC of the aluminum alloy cable and
the overhead conductor are very similar before the eighth year. As a result, choosing which type of
line depends on the appearance requirements.
When the service life is longer than the eighth year, the copper cable gradually forms an economic
advantage. For this high load rate and dual-circuit line, although the investment cost of the aluminum
alloy cable is only 38% of the copper cable, the operation energy loss of the copper cable is much
less than the other two types of lines. Therefore, from a long-term perspective, the copper cable is a
better choice.
4. Conclusions
In this paper, the LCC of the 10 kV power line is studied. The power lines’ LCC model is
established by analyzing each period of its life cycle, which include the investment period, operation
and maintenance period, failure period and discard period. Besides, the economic differences among
the aluminum alloy cable, copper cable and overhead conductor are compared through two practical
engineering projects in Fujian province in China by an LCC evaluation software we developed. In these
two cases, the LCC of a distribution power line is closely related to its working condition. The analysis
results can be summarized as follows.
•
Considering line length and capacity:
When the line length is relatively short and its capacity is relatively small, the investment cost
has the biggest inﬂuence on the LCC. Therefore, a low investment cost line is the better choice.
However, when the line length is relatively long and its capacity is relatively large, the operation
and maintenance cost takes the ﬁrst place in the LCC, which leads to the low energy loss line
becoming a better choice.



<!-- page 20/21 -->

Inventions 2016, 1, 20
20 of 21
•
Considering service life:
When the service life is less than 10 years, the aluminum alloy cable or the overhead conductor is
better than the copper cable. However, when the service life is more than 10 years, the copper
cable is more economical.
This paper provides a kind of LCC model used in engineering applications for cable selection and
can be a reference for further research on the LCC of the 10-kV power line.
Acknowledgments: The work is ﬁnancial supported by State Grid Fujian Electric Power Research Institute of
China (SGTYHT/14-JS-190). The authors would like to appreciate the reviewers for their valuable comments
and suggestions.
Author Contributions: All authors conceived and designed the study. Zhengyu Zhu, Siyao Lu, Tao Yi and
Bin Chen performed the data analysis; Zhenyu Zhu and Bingtuan Gao wrote the paper; Zhenyu Zhu, Bingtuan Gao
and Siyao Lu reviewed and edited the manuscript; All authors read and approved the manuscript.
Conﬂicts of Interest: The authors declare no conﬂict of interest.
References
1.
Neumann, K.; Zimmermann, J. Procedures for Resource Leveling and Net Present Value Problems in Project
Scheduling with General Temporal and Resource Constraints. Eur. J. Oper. Res. 2000, 127, 425–443.
2.
Baroum, M.S.; Patterson, J.H. The Development of Cash Flow Weight Procedures for Maximizing the Net
Present Value of a Project. J. Opera. Manag. 2014, 14, 209–227.
3.
Anceaume, E.; Busnel, Y.; Gambs, S. Characterizing the Adversarial Power in Uniform and Ergodic Peer
Sampling. In Proceedings of the 1st International Workshop on Algorithms and Models for Distributed
Event Processing Collocated with the 25th International Symposium on Distributed Computing, Rome, Italy,
25–27 August 2011; pp. 12–19.
4.
Gorshkov, A.S.; Rymkevich, P.P.; Nemova, D.V.; Vatin, N.I. Method of calculating the payback period of
investment for renovation of building facades. Constr. Unique Build. Struct. 2014, 2, 82–106.
5.
Mahlia, T.M.I.; Razak, H.A.; Nursahida, M.A. Life cycle cost analysis and payback period of lighting retroﬁt
at the University of Malaya. Renew. Sustain. Energy Rev. 2011, 15, 1125–1132.
6.
Georgakellos, D.A. Climate change external cost appraisal of electricity generation systems from a life cycle
perspective: The case of Greece. J. Clean. Prod. 2012, 32, 124–140.
7.
Hutchinson, T.; Burgess, S.; Herrmann, G. Current hybrid-electric powertrain architectures: Applying
empirical design data to life cycle assessment and whole-life cost analysis. Appl. Energy 2014, 119, 314–329.
8.
Perera, A.T.D.; Attalage, R.A.; Perera, K.K.C.K.; Dassanayake, V.P.C. Designing standalone hybrid energy
systems minimizing initial investment, life cycle cost and pollutant emission. Energy 2013, 54, 220–230.
9.
Katsigiannis, Y.A.; Georgilakis, P.S.; Karapidakis, E.S. Multiobjective genetic algorithm solution to the
optimum economic and environmental performance problem of small autonomous hybrid power systems
with renewables. IET Renew. Power Gener. 2010, 4, 404–419.
10.
Georgilakis, P.S.; Hatziargyriou, N.D. A review of power distribution planning in the modern power systems
era: Models, methods and future research. Electr. Power Syst. Res. 2015, 121, 89–100.
11.
Li, M.J.; Ou, Y.Q.; Cai, D.H.; Mo, S.J.; Shen, H.Y. Research on Life-Cycle Reliability Costs of Transmission
Lines. Smart Grid 2014, 4, 21–25.
12.
Zhou, L.; Ge, Y.J. Determination of Discount Rate in Whole Life Economic Analysis. Shanghai Highway 2007,
26, 51–54. (In Chinese)
13.
DL/T 686-1999, Guide of Calculation of Grid Energy Loss; Electric Power Industry: Tokyo, Japan, 1999.
(In Chinese)
14.
JB/T 10181-2000, Calculation of the Current Rating of Electric Cables; Electric Power Industry: Tokyo, Japan,
2000. (In Chinese)
15.
Patrik, H.; Vladimiro, M.; Manuel, A.M.; Lina, B. Multiobjective Optimization Applied to Maintenance
Policy for Electrical Networks. IEEE Trans. Power Syst. 2007, 22, 1675–1682.
16.
Dang, P.; Su, H.; Liu, B.; Zheng, Q.; Zheng, W.; Wang, L. Life Cycle Assessment of Aluminum Alloy Cable
and Copper Cable. J. Environ. Eng. Technol. 2014, 4, 74–79.



<!-- page 21/21 -->

Inventions 2016, 1, 20
21 of 21
17.
Chen, Y.; Ma, L.; Mu, G.; Zhang, X.; Fan, G. Comparison Studies on Two Types of Accuracy Criteria for
Short-term Load Forecast. Autom. Electr. Power Syst. 2003, 27, 73–77.
18.
Liu, G.; Cao, J.; Lu, Y.; Tan, G. Selection Criteria of High-voltage Aubmarine Cables for Offshore Wind Farms
by Life Cycle Cost. High Volt. Eng. 2015, 41, 2674–2680. (In Chinese)
19.
Li, L.; Liu, F.; Xie, G. The Research on Overhead Line Selection Based on the Life Cycle Cost Theory. J. North
China Electr. Power Univ. 2010, 37, 23–28.
20.
Yang, L.; Dai, Y.; Li, N. A Forecasting Method for Project Cost Probability at Completion Based on Monte
Carlo Simulation. Comput. Simul. 2014, 31, 301–304.
c⃝2016 by the authors; licensee MDPI, Basel, Switzerland. This article is an open access
article distributed under the terms and conditions of the Creative Commons Attribution
(CC-BY) license (http://creativecommons.org/licenses/by/4.0/).
