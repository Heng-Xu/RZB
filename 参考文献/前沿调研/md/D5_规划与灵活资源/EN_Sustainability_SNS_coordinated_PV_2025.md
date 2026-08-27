<!--
source: D5_规划与灵活资源/EN_Sustainability_SNS_coordinated_PV_2025.pdf
sha256: a6e1e296e6db92e65f368b1d1bdad7a062af4ec973250801702d6bc1f2788c64
method: pymupdf
pages: 32
-->

<!-- page 1/32 -->

 
 
 
 
Sustainability 2025, 17, 5324 
https://doi.org/10.3390/su17125324 
Article 
Sustainable Distribution Network Planning for Enhancing PV 
Accommodation: A Source–Network–Storage Coordinated  
Stochastic Approach 
Jing Wang 1, Chenzhang Chang 2, Jian Le 1,3,*, Xiaobing Liao 4 and Weihao Wang 1 
1 School of Electrical Engineering and Automation, Wuhan University, Wuhan 430072, China; 
whu_wangj@whu.edu.cn (J.W.); 2020302191679@whu.edu.cn (W.W.) 
2 School of Science and Engineering, The Chinese University of Hong Kong, Shenzhen 518172, China; 
120090204@link.cuhk.edu.cn 
3 Institute of Next Generation Power Systems and International Standards, Wuhan University,  
Wuhan 430072, China 
4 College of Electrical and Electronic Engineering, Wuhan Institute of Technology, Wuhan 430073, China; 
xbliao@whu.edu.cn 
* Correspondence: lejian@whu.edu.cn 
Abstract: To address the impacts of source load temporal–spatial uncertainties on distri-
bution network planning considering the global transition towards sustainable energy 
systems with high-penetration photovoltaic (PV) integration, this paper proposes a 
source–network–storage coordinated stochastic planning method. A temporal–spatial 
correlation probability model for PV output and load demand is constructed based on 
Copula theory. Scenario generation and eﬃcient reduction are achieved through Monte 
Carlo sampling and K-means clustering, extracting representative daily scenarios that 
preserve the temporal–spatial characteristics. A coordinated planning model targeting the 
minimization of comprehensive costs is established to holistically optimize PV deploy-
ment, energy storage system (ESS) conﬁguration, and network expansion schemes. Simu-
lations on typical distribution network systems demonstrate that the proposed method, 
by integrating temporal–spatial correlation modeling and multi-element collaborative de-
cision-making, signiﬁcantly improves PV accommodation capacity and reduces planning 
costs while improving the overall economic eﬃciency of distribution network planning. 
This study provides a robust technical pathway for developing economically viable and 
resilient distribution networks capable of integrating large-scale renewable energy, 
thereby contributing to the decarbonization of the power sector and advancing the goals 
of sustainable energy development. 
Keywords: sustainable energy system; source–network–storage collaborative planning; 
PV accommodation; Copula theory; stochastic scenarios 
 
1. Introduction 
With the vigorous development and utilization of PV in distribution networks [1,2], 
the uncertainty of its output and the volatility of loads have brought great challenges to 
the balance of energy supply and demand [3]. At the same time, the load growth requires 
the expansion of the distribution network framework, and the unreasonable structure will 
seriously aﬀect the operation of the system [4,5]. The ESS has the ability of bidirectional 
regulation [6]. The collaborative planning of ESS and PV can greatly improve the 
Academic Editor: Joshua M. Pearce 
Received: 17 April 2025 
Revised: 3 June 2025 
Accepted: 5 June 2025 
Published: 9 June 2025 
Citation: Wang, J.; Chang, C.; Le, J.; 
Liao, X.; Wang, W. Sustainable  
Distribution Network Planning for 
Enhancing PV Accommodation: A 
Source–Network–Storage  
Coordinated Stochastic Approach. 
Sustainability 2025, 17, 5324. https:// 
doi.org/10.3390/su17125324 
Copyright: © 2025 by the authors. 
Licensee MDPI, Basel, Switzerland. 
This article is an open access article 
distributed under the terms and 
conditions of the Creative Commons 
Attribution (CC BY) license 
(https://creativecommons.org/license
s/by/4.0/).



<!-- page 2/32 -->

Sustainability 2025, 17, 5324 
2 of 32 
 
utilization rate of PV [7,8]; optimize resource allocation; and improve the reliability, secu-
rity, and ﬂexibility of distribution network operation [9,10]. Therefore, considering the 
uncertainty of PV output and load demand, it is of great practical signiﬁcance to study the 
distribution network planning scheme, including site selection and capacity determina-
tion of PV and ESS, as well as network expansion. 
Currently, a large number of scholars have conducted in-depth research on the plan-
ning problem of distribution networks. Reference [11] proposed a novel hybrid optimiza-
tion algorithm that combines clonal selection principle and particle swarm optimization 
to optimize the capacity and location of DG in the power system. References [12–14] stud-
ied the optimal allocation of ESS with the aim of improving system economy. The above 
literature has only modeled the distribution network planning problem considering the 
optimal allocation of DG or ESS. In distribution network planning, however, the joint 
planning of PV and ESS is of great signiﬁcance to enhance the capacity of a distribution 
network to consume the power generation of PV and reduce the loss of resources [15,16]. 
Reference [17] employed PSO for optimal PV–DG and BESS allocation, enabling dynamic 
and static network reconﬁguration to minimize losses, improve voltage proﬁles, and en-
hance system loadability. Reference [18] established a two-step approach to conﬁgure the 
power and capacity of the ESS through scheduling and control strategies. Reference [19] 
proposed a bi-level programming approach and developed an improved binary particle 
swarm optimization algorithm based on chaos optimization to achieve the optimal joint 
planning of DG and ESS. There have been many studies on the distribution network plan-
ning problem for the optimal allocation of DG and ESS, but few studies have fully inves-
tigated the model for the collaborative planning of source–network–storage. 
The randomness of load and PV will pose a great challenge to the planning of distri-
bution networks [20]. To address the uncertainty problem of load and PV, Reference [21] 
proposed a time series-based planning method for modeling the load demand and PV 
output variations in a single day. In order to solve the time series model containing PV, 
the study adopted the Monte Carlo method to simulate diﬀerent scenarios by random 
sampling to obtain more accurate planning results. The method takes into account time 
series changes, but because it does not consider the diﬀerent load demand and PV output 
of diﬀerent days, it results in less accurate planning results. Reference [22] established a 
coordinated planning model for distributed wind power and transmission lines by com-
prehensively considering investment costs, environmental beneﬁts, and power supply re-
liability. However, under this planning framework, the generator output is assumed to be 
constant, which deviates from real-world conditions and fails to account for uncertainty. 
To address the uncertainty problem of multiple scenarios, Reference [23] proposed a wind 
power scenario simulation method to analyze the random characteristics of wind power 
output, integrating improved forecasting, nonparametric kernel distribution, and a BR 
scene reduction model. 
In summary of the above research and analysis, this paper ﬁrst establishes a proba-
bilistic model of source load temporal–spatial correlation based on Copula theory to deal 
with the randomness of the PV outputs and load and generates the source load correlation 
output curves of a typical daily scenario by the Monte Carlo method and K-means clus-
tering algorithm. Then, aiming at enhancing the eﬃcient consumption of PV and the eco-
nomics of distribution network planning, the collaborative planning of source–network–
storage is studied based on stochastic scenarios, and the joint planning model of PV, ESS, 
and grid expansion is established. Finally, the eﬀectiveness of the proposed method to 
improve the PV absorption capacity and the economy of distribution network planning is 
veriﬁed by simulation analysis of 25-node and 54-node arithmetic examples.



<!-- page 3/32 -->

Sustainability 2025, 17, 5324 
3 of 32 
 
2. Source Load Temporal–Spatial Correlation Scenarios 
2.1. Probabilistic Model of Source Load Temporal–Spatial Correlation Based on Copula Theory 
In the correlation coeﬃcient discriminant, Kendall correlation coeﬃcient and Spear-
man correlation coeﬃcient [24] are often used to assess the goodness of ﬁt. Both of the 
rank correlation coeﬃcients are statistical analyses that reﬂect the degree of rank correla-
tion and are used to measure the degree of association between two variables. In the good-
ness of ﬁt discrimination of Copula functions, the rank correlation coeﬃcients of each 
Copula function can be compared with the rank correlation coeﬃcients of the sample data. 
By calculating these correlation coeﬃcients and observing how close they are to the cor-
relation coeﬃcients of the sample data, the goodness of ﬁt of the Copula function to the 
sample data can be assessed. The closer the data, the better the ﬁt, indicating that the cor-
responding Copula function is the most appropriate. This approach helps to select the 
most suitable model to characterize the data among multiple Copula functions. 
Let the load and PV output be U and V, respectively. (u1, v1) and (u2, v2) are any two 
sample observations of its output (U, V). The two values are independent of each other. If 
(u1, v1)·(u2, v2) > 0, then (u1, v1) and (u2, v2) are considered consistent; otherwise, (u1, v1) and 
(u2, v2) are considered inconsistent. 
Kendall rank correlation coeﬃcient is ρk 
ρ
−
=
−
k
2(
)
(
1)
a
b
N N
 
(1)
where a denotes the number of pairs of samples with consistent output in (U, V); b denotes 
the number of pairs of samples with inconsistent output in (U, V); N denotes the total 
number of sampling points; and N is taken as 24 in this paper, i.e., the step size is 1 h. 
Spearman rank correlation coeﬃcient is ρs 
ρ
=
=
=
−
−
=
−
−



1
s
1
2
2
1
(
)(
)
(
)
(
)
N
i
i
i
N
N
i
i
i
i
c
c d
d
c
c
d
d
 
(2)
where ci denotes the rank of ui in (u1, u2, …, uN); di denotes the rank of vi in (v1, v2, …, vN): 
=
= 
1
N
i
i
c
c
N
; 
=
=
1
N
i
i
d
d
N
. 
The Euclidean distance discriminant [25] is an eﬀective method to assess the similar-
ity or diﬀerence between objects in a multidimensional space. The Euclidean distance dis-
criminant also plays an important role in the goodness of ﬁt discrimination of Copula 
functions. This method compares the Euclidean distance of each Copula function with the 
Euclidean distance of the empirical Copula function for the sample data. The calculation 
of the Euclidean distance is based on the formula of the distance between points in a mul-
tidimensional space, which measures the sum of the diﬀerences between two points in 
each dimension. Here, each Copula function and the empirical Copula function of the 
sample data can be regarded as points in a multidimensional space with dimensions de-
termined by the parameters of the Copula function or other relevant features. 
By comparing these Euclidean distances, it is possible to conclude which Copula 
function provides a better ﬁt to the sample data. In general, the smaller the Euclidean 
distance is, the closer the two objects are in the multidimensional space, i.e., the more 
similar they are. Therefore, the smaller the Euclidean distance is, the more similar the 
Copula function is to the empirical Copula of the sample data, and the better the ﬁt is.



<!-- page 4/32 -->

Sustainability 2025, 17, 5324 
4 of 32 
 
Let (xi, yi) (i = 1, 2, …, n) be a sample of the (X, Y) two-dimensional variable and Fn(xi) 
and Fn(yi) be the empirical cumulative distribution functions of the two-dimensional var-
iable (X, Y), respectively. The empirical Copula function for the sample is calculated as 
(
)
(
)
=
= 


[
] [
]
1
1
( , )
n
i
n
i
n
n
F
x
u
G
y
v
i
C
u v
I
I
n
 
(3)
where 
⋅[ ]
I
  denotes the characteristic function. When 

( )
n
i
F x
u , there exists 
(
)
=

[
]
1
n
i
F
x
u
I
; otherwise, 
(
)
=

[
]
0
n
i
F
x
u
I
. It is the same for 
(
)
[
]
n
i
G
y
v
I
. 
The most appropriate function is discriminated by comparing the magnitude of the 
squared Euclidean distance: 
=
=
−

2
2
1
,
(
)
(
)
,
n
n
i
i
e
i
i
i
d
C
u v
C
u v
 
(4)
where 
=
( )
i
n
i
u
F x
 , 
=
( )
i
n
i
v
G y
 . 
⋅()
eC
  denotes the empirical Copula function. The 
smaller 
2d  is, the better the ﬁt of the function. 
Nonparametric kernel density estimation is a nonparametric test that characterizes 
the distribution of data directly from a sample of real data [26]. Assume that the data 
sample probabilistic density function and its nonparametric kernel density estimation is 
=
=
−
=
−
=


1
1
1
1
( )
(
)
(
)
n
n
i
i
i
i
x
x
F x
K x
x
K
n
nh
h
 
(5)
where x denotes a sample of random variables 
…
1
2
,
,
n
x x
x ; n denotes the sample space; 
h denotes the window, and h > 0; ( )
Kx  denotes the kernel function. 
Nonparametric kernel density estimation focuses on the selection of the kernel func-
tion and bandwidth. ( )
Fx  inherits the continuity and diﬀerentiability of 
 ()
K
, and the 
window h aﬀects the ﬁt. The kernel function 
 ()
K
 is a probabilistic density function that 
conforms to non-negativity, integrates to 1, and has a mean of 0. The commonly used 
 ()
K
 
is the following Gaussian function: 
=
−
2
1
1
( )
exp(
)
2
2π
K x
x
 
(6)
For the construction of the probabilistic model of source load temporal–spatial cor-
relation based on Copula theory, an estimation of parameter θ is required, which can ef-
fectively simplify the complex calculation process of the traditional joint distribution 
model. The estimation of parameter θ adopts the correlation index method, which can be 
indirectly determined by calculating the correlation index of the samples. 
The parameters θ of the Gumbel Copula, Clayton Copula, and Frank Copula func-
tions are estimated by using maximum likelihood. To ensure the accuracy of these param-
eters, the Kendall rank correlation coeﬃcient τ was further adopted in this paper for test-
ing. 
Based on the probabilistic model of the load demand and PV output, while fully con-
sidering the temporal–spatial correlation between them, a probabilistic model of source 
load temporal–spatial correlation is established by using Copula theory. This model can 
more accurately describe and predict the temporal–spatial correlation between load de-
mand and PV output, which lays the foundation for the planning and operation optimi-
zation of distribution networks.



<!-- page 5/32 -->

Sustainability 2025, 17, 5324 
5 of 32 
 
The diagram for generating the probabilistic model of source load temporal–spatial 
correlation based on Copula theory is shown in Figure 1. 
Use the load and photovoltaic data of a 
region, and process the actual data.
According to the formula to calculate the probability 
distribution of load and PV. Calculate the probability 
density function and the rank correlation coefficient.
Use maximum likelihood to estimate the 
parameters of Copula function, and 
eventually generate the Copula model.
Use goodness-of-fit evaluation to select an 
appropriate Copula model and establish the 
probabilistic model of source-load temporal-spatial 
correlation.
Start
End
 
Figure 1. Probabilistic model generation process diagram. 
2.2. Scenario Generation Based on the Monte Carlo Method 
Scenario generation is a key step in the uncertainty modeling of distribution net-
works. It aims to quantify uncertainty using deterministic information, thereby construct-
ing discrete probabilistic scenarios that are deterministic. This process relies on probabil-
istic forecasting and generates a series of scenarios to reﬂect the uncertainty between the 
source and load. When selecting uncertainty factors, they usually need to be determined 
according to speciﬁc decision problems. In existing research, factors such as PV genera-
tion, load demand, forecasting errors, and variability characteristics are often considered 
as signiﬁcant uncertainty factors. This paper speciﬁcally focuses on two key factors: PV 
generation and load demand. 
Compared to directly using stochastic programming, the scenario generation method 
comprehensively describes the uncertainty of source load through a large number of sce-
narios, making the model closer to the actual planning problem of distribution networks. 
The generated scenarios can precisely represent the uncertainty probability distribution 
with discrete deterministic samples, fully reﬂecting the temporal and spatial characteris-
tics. This method not only improves the accuracy and reliability of the model but also 
helps optimize the operational decisions of the distribution network, enhancing the over-
all performance of the power system. 
In dealing with the probabilistic model of source load temporal–spatial correlation 
generated based on Copula theory, this paper employs the Monte Carlo method [27] for 
scenario sampling to generate a large number of source load temporal–spatial correlation 
scenarios. The speciﬁc steps for generating these scenarios based on the Monte Carlo 
method are as follows: 
After obtaining the probabilistic model of source load temporal–spatial correlation 
based on Copula theory, we need to perform sampling to generate a large number of sam-
ples for subsequent analysis. The main steps of the sampling process are as follows: 
(1) Randomly generate numbers 
⋅⋅⋅
1
2
,
, , n
a a
a  within the interval [0, 1].



<!-- page 6/32 -->

Sustainability 2025, 17, 5324 
6 of 32 
 
(2) 
=
1
1
u
a  represent the marginal distribution function value of one random variable, 
and 
2
u  represent the marginal distribution function value of another random vari-
able. 
2
u  can be obtained by the pre-selected optimal Copula function C, calculated 
by Equation (7): 
(
)
∂
=
∂

1
2
2
1
,
,
,
n
C u u
u
a
u
 
(7)
(3) 
n
u  is the value of the n-th function, which can be determined using Equation (8): 
−
−
−
−
−
∂
∂
∂
∂
=
∂
∂
∂
∂




1
1
2
1
2
1
1
1
2
1
1
2
1
(
,
,
,
)
(
,
,
,
,1)
n
n
n
n
n
n
n
C u u
u
u u
u
a
C u u
u
u u
u
 
(8)
(4) 
Repeating the above process k times, it is able to obtain k sets of peripheral distribu-
tion function values containing n random variables. 
(5) 

1
2
(
,
,
,
)
j
j
nj
u u
u
 can be transformed into a joint distribution function scenario by solv-
ing the inverse function 
−
=
1(
)
i
i
i
x
F
u
, where =
⋅⋅⋅
1,2, ,
j
T, and T is the total number of 
days. 
Inverse function calculations are involved in analyzing the correlation between both 
PV and load. First, the Copula probability model is used to derive the peripheral distribu-
tion functions of PV output and load demand. Subsequently, inverse function calculations 
are performed for each of these two peripheral distribution functions. This approach en-
sures that the temporal–spatial correlation between PV output and load demand is fully 
considered in the generated scenarios. 
The stages of scene generation are shown in Figure 2. 
Probabilistic model of source-load temporal-spatial 
correlation for each time period
,
(
,
)
1,2,
,24
(
)
(
)
(
)
i
i
n
i
i
i
i
X
Y
F
x y
C F
x
F
y
i
=
=

1
1
1
2
2
2
24
24
24
(
)
(
,
,
,
),
,
,
(
)
F u v
F
u
v
F
u
v





)
,
(
)
(
i
i
i
i
i
i
X
Y
u
F
x
v
F
y
=
=
Generation of source-load daily curves
Random
sampling
1
2
24
1
2
24
u
u
u
v
v
v








1
1
(
)
( )
i
i
i
i
X
i
i
Y
x
F
u
y
F
v
−
−


=


=




1
2
24
1
2
24
x
x
x
y
y
y








1
2
3
…
3649
3650
Generation of source-load annual curves
1
2
24
1
1
1
2
24
1
1
1
1
x
y
x
x
y
y








2
24
2
2
2
2
24
2
2
2
1
1
x
y
x
x
y
y








2
24
3
3
3
2
24
3
3
3
1
1
x
y
x
x
y
y








2
24
3649
3649
3649
2
24
3649
3649
36
1
49
1x
x
x
y
y
y








2
24
3650
3650
3650
2
24
3650
3650
36
1
50
1x
x
x
y
y
y








 
Figure 2. Steps for generating source load temporal–spatial correlation scenarios.



<!-- page 7/32 -->

Sustainability 2025, 17, 5324 
7 of 32 
 
2.3. Scenario Reduction Based on the K-Means Clustering Algorithm 
While scenario analysis requires a large number of scenarios to reduce uncertainty, 
too many scenarios will greatly increase the computational burden of stochastic optimi-
zation. Therefore, it is necessary to reduce the large number of scenarios generated by the 
scenario analysis to a smaller set of representative scenarios, which is called scene reduc-
tion. That is, from the given initial scene set S, select some scenes that meet the conditions 
to form a reserved scene set R, so that the reserved scene set R can be representative as 
much as possible, and the abandoned scenes form a deleted scene set D. 
The main scenario reduction methods include simultaneous backward reduction, fast 
forward reduction, and clustering analysis methods such as K-means and K-medoids. Alt-
hough the implementation processes diﬀer, the objective of these reduction methods is 
consistent. However, when dealing with a large number of scenarios, the K-means clus-
tering algorithm stands out due to its speed advantage in clustering. 
The scenario reduction ﬂowchart based on the K-means clustering algorithm is 
shown in Figure 3. 
Use the Elbow method and silhouette coefficient 
to calculate and determine the value of K, and 
identify the initial cluster centroids.
Assign each sample point to the cluster 
represented by the nearest centroid.
Replace the centroids with the center of 
the sample points in each cluster.
Repeat the iteration until the centroids remain 
unchanged or the maximum number of 
iterations or tolerance range is reached.
Output the reduced representative 
daily scenarios.
Start
End
 
Figure 3. Scene reduction process diagram. 
3. Source–Network–Storage Collaborative Planning Model Based on 
Stochastic Scenarios 
3.1. Objective Function 
The source–network–storage collaborative planning model, developed in this paper, 
primarily considers three types of investment costs: PV curtailment penalty costs, grid 
expansion investment costs, and ESS investment costs. These three aspects are used to 
construct the objective function for minimizing the annual distribution network compre-
hensive cost: 
=
+
+

L in
E
in v
e
S S
P V
m in
(
)
C
C
C
C
 
(9)



<!-- page 8/32 -->

Sustainability 2025, 17, 5324 
8 of 32 
 
Ω
Ω
Ω
Ω
Ω
Ω
δ
δ
∈
=
∈
∈
∈
∈
∈

−





+

=
=
=



S
PV
S
L
S
ESS
PV
PV
PV
PV
,
, ,
, ,
1
length
line
p
ESS
e
e
e
,
,
PV
Line
,
E S
L
,
S
365
( )(
)
( )(
)
T
i s
i t s
i t s
s
t
i
ij
s
ij
i s
i
i s
j
i
i s
i
s
s
i
C
c
x
s P
P
c
L
c
C
C
c
x
x
s
E
P
 
(10)
where 
inv
C  represents the annual distribution network comprehensive cost; 
PV
C
 repre-
sents the annualized PV curtailment penalty cost; 
Line
C
 represents the grid expansion in-
vestment cost; 
ESS
C
 represents the annualized ESS investment/operation and maintenance 
cost; 
PV
c
 represents the PV curtailment penalty cost coefficient; 
PV
,i s
x
 is a binary decision 
variable, where 
PV
,i s
x
 = 1 if PV is installed at node i, and 
PV
,i s
x
 = 0 otherwise; 
( )
δ
s  repre-
sents the probability of the typical scenario; 
PV
, ,
i t s
P
 represents the predicted power output of 
the PV connected to node i at time t in scenario s; 
PV
, ,
i t s
P
 represents the active power output 
of the PV connected to node i at time t in scenario s; 
L
,
i j
s
x
 is a binary decision variable, 
where 
L
,
i j
s
x
 = 1 if node i is connected to node j, and 
L
,
i j
s
x
 = 0 otherwise; 
line
c
 represents 
the cost per unit length for building the transmission line, and 
length
ij
L
 represents the length 
of the transmission line; 
ESS
,i s
x  is a binary decision variable, where 
ESS
,i s
x  = 1 if ESS is installed 
at node i, and 
ESS
,i s
x  = 0 otherwise; 
e
ic  and 
p
ic  represent the unit capacity investment/op-
eration and maintenance costs for ESS at node i and the unit power investment/operation 
and maintenance costs, respectively; 
e
,i s
E
 represents the rated capacity of the ESS; 
e
,i s
P
 
represents the rated power of the ESS; ΩS  represents the set of scenarios; 
PV
Ω
 represents 
the set of candidate PV connection nodes; 
L
Ω  represents the set of distribution network 
grid lines; and 
ESS
Ω
 represents the set of candidate ESS connection nodes. 
3.2. Constraints 
3.2.1. Constraints of Distributed PV 
The increase in PV capacity will lead to overvoltage issues in the grid. To address 
this problem, this paper adopts the Optimal Inverter Dispatch [28] (OID) strategy, which 
controls the active and reactive power of PV simultaneously. The operating range of PV 
under the OID strategy is illustrated in Figure 4. 
θ
PV
Q
PV
S
PV
P
PV
P
 
Figure 4. PV operating area under the OID strategy. 
• 
Constraints of Operation



<!-- page 9/32 -->

Sustainability 2025, 17, 5324 
9 of 32 
 
PV,x
PV,x
PV,x
PV,x
PV,x
PV,x
PV,x
PV,x
θ
θ
≤
≤


+
≤
−
≤
≤
≤





−
×
≤
×
−
×
−
≤
−

≤
+
×
PV
, ,
, ,
2
2
PV
2
, ,
, ,
, ,
, ,
, ,
, ,
PV
PV
,
, ,
,
PV
PV
PV
PV
, ,
,
, ,
, ,
,
0
)
tan
t
(
)
(
(
)
(1
)
(
n
)
a
1
i t s
i t s
i t s
i t s
i t s
i t s
i t s
i t s
i s
i t s
i s
i t s
i s
i t s
i t s
i s
i
i
P
P
P
Q
S
P
Q
P
M
x
P
M
x
P
M
x
P
P
M
x
 
(11)
where 
PV
, ,
i t s
Q
 represents the reactive power of the PV connected to node i at time t in sce-
nario s; 
PV
, ,
it s
S  represents the rated capacity of the PV connected to node i at time t in sce-
nario s; θi   represents the power factor angle of the PV; 
PV,x =
PV
PV
, ,
,
, ,
i t s
i s
i t s
P
x P
  and 
PV,x =
PV
PV
, ,
,
, ,
i t s
i s
i t s
Q
x Q
 are intermediate auxiliary variables. M represents a suﬃciently large pos-
itive number. 
• 
Constraints of Nominal Capacity 
≤
≤
PV
PV
, ,
,max
0
i t s
i
S
S
 
(12)
where 
，
PV
max
iS
 represents the maximum capacity of PV that can be installed at node i. 
• 
Constraints of the Number of PV 
L
PV
=
≤

1
PV
,s
N
i
i
N
x
 
(13)
where 
L
N
 represents the number of nodes, and 
PV
N
 represents the maximum number 
of PV installations allowed in the distribution network. 
3.2.2. Constraints of ESS 
Given that the changes in PV output do not exactly match the changes in load de-
mand, PV can only adopt the curtailment strategy to satisfy the above stringent con-
straints based on substation power, node voltage, and branch current limits in the distri-
bution network. The source–network–storage collaborative planning method proposed in 
this paper makes full use of the PV in the distribution network by introducing ESS to 
smooth voltage ﬂuctuation and improves the capacity of the distribution network to con-
sume PV generation. 
• 
Constraints of Operation



<!-- page 10/32 -->

Sustainability 2025, 17, 5324 
10 of 32 
 
e,x
e,x
ch
e,ch
ch
e
ch
e
ch
ch
e,ch
dis
e,dis
dis
ch
ch
dis
η
η
+
≤
−
≤
≤
≤
≤
=
+
−
Δ
≤
−
×
≤
≤
×
×
−
≤
≤
,
,
, ,
,
, ,
,
dis
ESS
, ,
, ,
,
, ,
,
, ,
,
, ,
, ,
, -1,
, ,
,
,
,
,
, ,
,
0.2
0.9
(1
0
0
(
)
)
i t s
i t s
i s
i t s
i s
i t s
i s
i t
i s
i s
i t s
i s
i t s
s
i t s
i t
s
i t s
i
s
i
i t
i
s
i
i t s
s
u
u
x
P
P
P
P
P
E
E
P
t
E
E
E
M
u
P
M
u
P
M
u
P ,ch
e
ch
dis
e,dis
dis
e
dis
e,dis
e
dis
e,x
e
e,x
e












≤
+
×
−
−
×
≤
≤
×
−
×
−
≤
≤
+
×
−
−
×
≤
≤
×
−
×
−
≤
≤
+
×
−

,
, ,
, ,
,
,
,
,
,
,
ESS
ESS
,
,
ESS
ESS
,
,
,
,
,
,
,
,
, ,
(1
)
(1
)
(1
)
(1
)
(1
)
i s
s
s
i s
i s
i t s
i t
i s
i t s
i s
i t s
i s
i s
i t s
s
i s
s
s
i s
i
i
i
i
P
M
u
M
u
P
M
u
P
M
u
P
P
M
u
M
E
M
E
M
E
x
x
x
x
E
M









 
(14)
where 
ch
, ,
i t s
u
 and 
dis
, ,
i t s
u
 are binary decision variables, representing the two states of ESS: 
charging state and discharging state, respectively; 
ch
, ,
i t s
P
 and 
dis
, ,
i t s
P
 represent the charging 
power and discharging power of the ESS, respectively; 
, ,
i t s
E
 represents the energy stored 
in the ESS at node i at time t; 
ch,
η
i  represents the charging eﬃciency of the ESS at node i; 
dis
η
,i  represents the discharging eﬃciency of the ESS at node i; Δt  represents the sched-
uling time interval of the ESS; 
e
e
,ch =
ch
,
,
,
,s
i s
i t
i s
P
u
P , 
,dis
dis
e
e
=
,
,
,
,
i
s
s
t
i
i s
P
u P , and 
e
ESS
e,x =
,
,
,
i
i
s
s
i s
E
x
E
 represent 
intermediate auxiliary variables. 
• 
Constraints of the Rated Power 
e
e
e
≤
≤
ESS
ESS
,
,min
,
,
,max
i s
i
i s
i s
i
x
P
P
x
P
 
(15)
where 
e
,min
iP
 and 
e
,max
iP
 represent the lower and upper limits of the rated power of the ESS, 
respectively. 
• 
Constraints of the Rated Capacity 
e
e
≤
≤
ESS
,
,
,max
0
i s
i s
i
E
x
E
 
(16)
where 
e
,max
iE
 represents the upper limit of the rated capacity of the ESS. 
• 
Constraints of the Number of ESS 
L
ESS
=
≤

1
ESS
,s
N
i
i
N
x
 
(17)
where 
ESS
N
 represents the maximum number of ESS installations allowed in the distri-
bution network. 
3.2.3. Constraints of Grid Expansion 
This section adopts a radial topology. Considering single-commodity ﬂow con-
straints (SCF) [29] and the quantitative relationship between nodes and edges, the distri-
bution network expansion model is constructed. The single-commodity ﬂow constraints 
ensure the connectivity of the graph in the form of virtual ﬂows.



<!-- page 11/32 -->

Sustainability 2025, 17, 5324 
11 of 32 
 
• 
Single-Commodity Flow Constraints 
L
L
L
Ω
Ω
∈
∈



∈
−
+
−
=

≤
≤
∀
+


, ,
, ,
( )
L
L
0
0
,
, ,
( )
,
(
)
(
)
1
\
ji t s
i
ij t s
j
ij s
j
ij t s
ij s
ij
i
ij
M
F
x
x
F
i
N
R
x
F
M
x
 
(18)
where 
, ,
ji t s
F
 and 
, ,
ij t s
F
 represent the virtual power ﬂowing from node j to node i and 
from node i to node j at time t in scenario s, respectively; 1 represents the virtual load at a 
regular node; 
0
ij
x
 is an undirected binary integer constant, indicating whether an initial 
transmission line has been constructed between node i and j. If such a line exists, 
0
ij
x
 = 1; 
otherwise, 
0
ij
x
 = 0. R represents the number of substation nodes. 
• 
Constraints of the Quantitative Relationship Between Nodes and Edges 
L
L
Ω
∈
+
=
−

0
L
,
( )
(
)
ij
ij s
ij
x
x
N
R  
(19)
• 
Constraints of Grid Expansion 
+
≤
L
0
,
1
i j s
i j
x
x
 
(20)
3.2.4. Constraints of Power Flow 
Considering the addition of grid expansion constraints, constraints on the branch cir-
cuit power need to be included. This paper adopts second-order cone relaxation (SOCR) 
[30,31] to convexly relax the power ﬂow equations. The transformed mixed-integer sec-
ond-order cone programming (MISOCP) power ﬂow model is as follows: 
• 
Power Flow Model 
→
→
→
→
=
−
−
=
−
−
−
−
+
≤
−
−
+
+
−
+




, ,
, ,
, ,
, ,
:
:
, ,
, ,
, ,
, ,
:
:
, ,
, ,
, ,
, ,
L
,
0
2
2
, ,
,
L
,
0
,
,
(
)
(
)
2(
)
(1
)
(
)
(
)
2
2
ij
s
i t s
jk t s
ij t s
ij ij t s
k j
k
i i
j
i t s
jk t s
ij t s
ij ij t
t
k j
k
i i
j
i t s
j t s
ij
ij t s
ij
ij t
t
ij
ij
i
s
ij s
ij
ij
ij
t
ij
ij t
j
s
s
p
P
P
r l
q
Q
Q
x l
v
v
r P
x Q
M
x
r
x
l
Q
P
l
x
x
x
V













≤
,
,
2
, +
i
ij
i
t
t
t
l
V
 
(21)
where 
, ,
i t s
p
 and 
, ,
its
q  represent the active and reactive power injections at node j at time 
t in scenario s, respectively; 
, ,
jk t s
P
 and 
, ,
jk t s
Q
 represent the active and reactive power ﬂows 
out of node j at time t in scenario s, respectively; 
, ,
ij t s
P
 and 
, ,
ij t s
Q
 represent the active and 
reactive power ﬂowing into node j at time t in scenario s, respectively; 
ijr  and 
ijx  rep-
resent the resistance and reactance on branch ij; 
, ,
ijt s
l
 represents the square of the current 
on branch ij at time t in scenario s; 
, ,
i t s
v
 and 
, ,
j t s
v
 represent the square of the voltage at 
node i and j at time t in scenario s, respectively; 
,
ij t
l
 represents the square of the current 
on branch ij at time t, and 
2
,
ij t
ij
l
I
=
; 
,i t
V
 represents the square of the voltage at node i 
at time t, and 
2
,i t
i
V
U
=
.



<!-- page 12/32 -->

Sustainability 2025, 17, 5324 
12 of 32 
 
• 
Constraints of the Voltage 
≤
≤
, ,
i
i t s
i
v
v
v  
(22)
where 
i
v
 and 
i
v
 represent the upper and lower limits of the square of the voltage at 
node i, respectively. 
• 
Constraints of the Current 
+


, ,
,
L
0
0
(
)
ij
ij
ij
ij
t s
s
l
x
x l  
(23)
where 
ijl
 represents the upper limit of the square of the current on branch ij. 
• 
Constraints of the Power 


≤
≤
≤

≤
, ,
, ,
,
i
i t s
i
i
i t s
i
p
p
p
q
q
q
 
(24)
where 
i
p  and 
i
p  represent the minimum and maximum active power of the substa-
tion generator at node i, respectively; 
i
q
 and 
i
q
 represent the minimum and maxi-
mum reactive power of the substation generator at node i, respectively. 
• 
Constraints of the Branch Circuit Power 

−


+
+
−
+
+




,
, ,
,
,
, ,
,
m
L
0
max
L
0
max
L
0
ax
L
0
max
(
)
(
)
(
)
(
)
ij
ij
ij
ij
ij
ij
ij
ij
ij
ij
ij
i
j
s
t s
s
j
i
ij
s
t s
s
x
x P
P
x
x P
x
x Q
Q
x
x Q
 
(25)
where 
m ax
ij
P
  and 
m ax
ij
Q
  represent the maximum values of active power and reactive 
power on branch ij, respectively. 
3.2.5. Constraints of Other Equipment 
With the increasing penetration of PV, the current reversal may occur in the distribu-
tion network during oﬀ-peak hours. This problem can be mitigated by installing reactive 
power compensation devices in the distribution network. If voltage problems arise due to 
the high proportion of PV generation, an on-load tap changer (OLTC) can be equipped in 
the distribution network to stabilize its operation [32]. 
• 
Constraints on the Operation of Group-Cutting Capacitors (CBs) 
+
−
=
=
≤






∈
=
≤

1
lim
,
,
CB
CB
1
CB
CB
CB
,
, ,
CB
CB
CB
, ,
, ,
0
,
Z
i t s
i t s
i
i t s
i
i t s
T
t
i
t
B
B
Q
n
q
n
N
n
 
(26)
where 
CB
, ,
i t s
Q
 represents the actual compensation power delivered by the CB at node i at 
time t in scenario s; 
CB
, ,
i t s
n
 represents the number of CB units in operation at node i at time 
t in scenario s; 
CB
iq
 represents the compensation power of a single CB unit; 
CB
i
N
 repre-
sents the maximum number of CB units at node i; 
lim
CB
B  represents the action frequency 
limit of the CB units within T scheduling periods in a day; 
,CB
t
iB
 is a 0–1 integer variable 
representing the decision: if the CB is operated, 
,CB
t
iB
 = 1; otherwise, 
,CB
t
iB
 = 0.



<!-- page 13/32 -->

Sustainability 2025, 17, 5324 
13 of 32 
 
• 
Constraints on the Operation of Static Var Compensation (SVC) 
≤
≤
SVC
SVC
SVC
,min
, ,
,max
i
i t s
i
Q
Q
Q
 
(27)
where 
SVC
, ,
i t s
Q
 represents the optimized reactive power adjustment for each phase of the 
SVC connected at node i at time t in scenario s; 
SVC
,min
iQ
 and 
SVC
,max
iQ
 represent the lower and 
upper limits of the adjustable reactive power for each phase of the SVC, respectively. 
• 
Constraints on the Operation of the On-load Tap Changer (OLTC) 
Figure 5 shows the branch model with an OLTC. The constraints on the operation of 
the OLTC are as follows: 
ij
z
o
i
j
k
,i t
S
,i t
U
,
,
,
ij t
ij t
I
S
,j t
U
,j t
S
,
k t
U
,
,
,
jk t
jk t
I
S
:1
ijk
 
Figure 5. Branch model with the OLTC. 
λ
λ
λ
λ
λ
=
=
=
=
+ Δ
≤
−
≤
−
≤
≤
=
+ Δ
≤
−
≤
−
≤
≤


min
, ,
, ,
, ,
, ,
0
, ,
, ,
, ,
, ,
, ,
min
, ,
, ,
, ,
, ,
0
, ,
, ,
, ,
, ,
, ,
, ,
0
2
0
(1
)
0
2
0
(1
)
0
2
ij
ij
ij
K
n
ij t s
ij
j t s
ij t s
ij n t
n
j t s
ij n t
ij n t
ij n t
ij n t
N
n
o t s
ij
ij t s
ij t s
ij n t
n
ij t s
ij n t
ij n t
ij n t
ij n t
N
n
ij n t
n
m
k
v
k
x
v
x
M
x
M
v
k
m
k
y
m
y
M
y
M
















≤

ij
K
 
(28)
where 
, ,
o t s
v
 represents the square of the voltage at node i at time t; 
, ,
ij t s
N
 represents the 
tap position of the OLTC installed on branch ij at time t in scenario s; 
, ,
ij t s
k
 represents the 
transformation ratio of the OLTC installed on branch ij at time t in scenario s; Δ ijk  rep-
resents the unit adjustment step of the OLTC; 
ij
K  represents the number of tap positions 
of the OLTC; 
m a x
ij
k
 and 
m in
ij
k
 represent the amplitude of the transformation ratio of the 
OLTC on branch ij; 
λ
=
, ,
, ,
, ,
ij n t
ij n t
j t s
x
v
 and 
λ
=
, ,
, ,
, ,
ij n t
ij n t
ij t s
y
m
 are auxiliary variables; and 
λ , ,
ij n t  represents the combination of {0,1}. 
4. Case Study 
4.1. System Setup for the Case Study 
To verify the eﬀectiveness of the proposed source–network–storage collaborative 
planning method based on stochastic scenarios for improving the eﬃcient utilization of 
PV and the economic planning of the distribution network, this paper uses the 25-bus 
system and 54-bus system shown in Figures 6 and 7 as models and uses YALMIP and the 
solver GUROBI to solve the problem. The planning results for the distribution network 
under diﬀerent scenarios are solved on a personal computer with an Intel Core(TM) i5-



<!-- page 14/32 -->

Sustainability 2025, 17, 5324 
14 of 32 
 
11320H CPU, 3.20 GHz, using MATLAB R2020b. As shown in Table 1, four schemes are 
set up: 
Scheme 1: Only considers grid expansion. 
Scheme 2: Consider grid expansion, PV siting and capacity setting, OLTC adjustment, 
and reactive power compensation. 
Scheme 3: Consider grid expansion, ESS siting and capacity setting, OLTC adjust-
ment, and reactive power compensation. 
Scheme 4: Consider grid expansion, PV siting and capacity setting, ESS siting and 
capacity setting, OLTC adjustment, and reactive power compensation. 
The system parameters and equipment parameters for the case study are provided 
in Tables 2–8.  
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
18
19
20
21
22
23
24
25
 
Figure 6. 25-bus system. 
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
18
19
20
21
22
23
24
25
51
52
54
53
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
 
Figure 7. The 54-bus system. 
Table 1. Scheme settings. 
Scheme 
Grid Expansion 
PV Siting and Capac-
ity Setting 
ESS Siting and Capacity 
Setting 
Reactive Power 
Compensation 
OLTC 
1 
√ 
— 
— 
— 
— 
2 
√ 
√ 
— 
√ 
√ 
3 
√ 
— 
√ 
√ 
√ 
4 
√ 
√ 
√ 
√ 
√



<!-- page 15/32 -->

Sustainability 2025, 17, 5324 
15 of 32 
 
Table 2. System parameter information. 
Parameter 
25-Bus System 
54-Bus System 
Substation active power/kW 
[0, 5000] 
[0, 10,000] 
Substation reactive power/kW 
[0, 2500] 
[0, 5000] 
Limit of bus voltage/p.u. 
[0.95, 1.05] 
[0.95, 1.05] 
Upper limit of branch power/MVA 
10 
10 
Upper limit of branch current/p.u. 
1 
1 
Reference voltage/kV 
12.66 
12.66 
Reference power/MW 
10 
10 
Table 3. PV parameter information. 
Limitations of PV 
25-Bus System 
54-Bus System 
Installation quantity limit in Scheme 1 
0 
0 
Installation quantity limit in Scheme 2 
[2, 5] 
[3, 8] 
Installation quantity limit in Scheme 3 
0 
0 
Installation quantity limit in Scheme 4 
[3, 8] 
[5, 10] 
Maximum installation capacity at buses/MW 
1.5 
3 
Table 4. ESS parameter information. 
Limitations of ESS 
25-Bus System 
54-Bus System 
Installation quantity limit in Scheme 1 
0 
0 
Installation quantity limit in Scheme 2 
0 
0 
Installation quantity limit in Scheme 3 
[1, 5] 
[1, 8] 
Installation quantity limit in Scheme 4 
[1, 5] 
[1, 8] 
Rated power/MW 
2 
2 
Charging efficiency 
0.9 
0.9 
Discharging efficiency 
1 
1 
Limit of SOC 
[0.2, 0.9] 
[0.2, 0.9] 
Table 5. CB parameter information. 
Limitations of CB 
25-Bus System 
54-Bus System 
Buses to be installed in Scheme 1 
— 
— 
Buses to be installed in Scheme 2 
21 
13 
Buses to be installed in Scheme 3 
21 
13 
Buses to be installed in Scheme 4 
21 
13 
Reactive power per compensation unit/kVar 
50 
50 
Maximum number of compensation units 
4 
4 
Maximum number of CB operations per day 
5 
5 
Table 6. SVC parameter information. 
Limitations of SVC 
25-Bus System 
54-Bus System 
Buses to be installed in Scheme 1 
— 
— 
Buses to be installed in Scheme 2 
18 
6 
Buses to be installed in Scheme 3 
18 
6 
Buses to be installed in Scheme 4 
18 
6 
Compensation range/kVar 
[−200, 300] 
[−200, 300]



<!-- page 16/32 -->

Sustainability 2025, 17, 5324 
16 of 32 
 
Table 7. OLTC parameter information. 
Limitations of OLTC 
25-Bus System 
54-Bus System 
Branches to be installed in Scheme 1 
— 
— 
Branches to be installed in Scheme 2 
1–22, 3–23, 14–24, 21–25 
5–52, 6–51, 41–53, 50–54 
Branches to be installed in Scheme 3 
1–22, 3–23, 14–24, 21–25 
5–52, 6–51, 41–53, 50–54 
Branches to be installed in Scheme 4 
1–22, 3–23, 14–24, 21–25 
5–52, 6–51, 41–53, 50–54 
Transformer ratio 
[0.95, 1.05] 
[0.95, 1.05] 
Tap change step value of the transformer 
0.01 
0.01 
Number of taps on the transformer 
10 
10 
Table 8. Cost information. 
Costs 
Value 
PV curtailment penalty/(CNY/kWh) 
3.6 
Annualized investment cost per unit capacity of ESS/(CNY/kWh) 
1270 
Annualized investment cost per unit power of ESS/(CNY/kWh) 
1650 
Unit length construction cost of the line/(CNY10,000/km) 
36.2 
To evaluate the power supply reliability of the planning scheme, this study intro-
duces the Expected Energy Not Supplied (EENS) as an evaluation metric. EENS refers to 
the amount of energy that cannot be delivered to users due to insuﬃcient supply capacity 
over a given period. It is calculated using the following formula: 
S
Sup
Load
, ,
, ,
1
365
( )(
)
T
i t s
i t s
s
t
i
EENS
s
P
P
t
Ω
Ω
δ
+
∈
=
∈
=
−
× Δ

 
(29)
Su p
P V
L in e
d is
ch
, ,
, ,
, ,
, ,
, ,
i t s
i t s
i t s
i t s
i t s
P
P
P
P
P
=
+
+
−
 
(30)
where 
Load
, ,
i t s
P
 represents the load power of node i at time t in scenario s; 
Sup
, ,
i t s
P
 represents 
the supplied power of node i at time t in scenario s; 
Line
, ,
i t s
P
 represents the transmission 
power of lines connected to node i at time t in scenario s; ( ) +
⋅
 represents taking the pos-
itive part (i.e., the value is counted only when the load exceeds the supplied power); Ω 
represents the set of all nodes; 
t
Δ  represents the time step. 
4.2. Analysis of Stochastic Scenarios 
The goodness of ﬁt of diﬀerent Copula functions was evaluated using the correlation 
coeﬃcient method and the Euclidean distance method. The most suitable Copula function 
was selected based on these results, as shown in Table 9. 
Table 9. Fit degree discrimination of diﬀerent functions. 
 
Normal Copula 
t-Copula Gumbel Copula Clayton Copula Frank Copula Sample Data 
Kendall rank correla-
tion coefficient 
−0.078 
−0.091 
1.457 × 10−6 
7.729 × 10−7 
−0.089 
−0.082 
Spearman rank corre-
lation coefficient 
−0.087 
−0.133 
2.936 × 10−6 
1.169 × 10−6 
−0.127 
−0.122 
Squared Euclidean 
distance 
0.842 
107.173 
2.169 
2.749 
0.226 
0 
As shown in Table 9, compared to other methods, the correlation coefficient obtained 
by the Frank Copula method has a better fit with the sample data and a smaller Euclidean 
distance to the empirical Copula. Although the correlation coefficient of t-Copula is



<!-- page 17/32 -->

Sustainability 2025, 17, 5324 
17 of 32 
 
acceptable, its Euclidean distance to the empirical Copula is large, indicating that its fitting 
performance is not ideal. Therefore, t-Copula is not suitable as the optimal fitting function. 
After comprehensive consideration, Frank Copula is selected for data fitting in this paper to 
ensure the accuracy and reliability of the fitting results. 
The Monte Carlo method is used to perform random sampling for each time period in 
the source load temporal–spatial correlation probabilistic model based on Copula theory. In 
this process, the number of load and PV output scenarios is set to 3650 to ensure the ran-
domness and diversity of the scenarios. Through this method, a large number of source load 
temporal–spatial correlation scenarios are generated, as shown in Figure 8. 
04：00
0
500
1000
1500
2000
2500
3000
PV output / kW
Time
0
2000
4000
6000
8000
10,000
12,000
14,000
16,000
18,000
20,000
Load demand / kW
08：00
12：00
16：00
20：00
24：00
 
Figure 8. Scene generation. 
To ensure computational accuracy while maximizing efficiency, the K-means cluster-
ing algorithm is employed to reduce the 3650 source load temporal–spatial correlation sce-
narios. The clustering algorithm is based on the computation of the sum of squared errors 
(SSE), silhouette efficiency (SE), and the similarity coefficient between scenarios. The opti-
mal number of clusters is defined as the number of clusters where the SSE is small and the 
SE is large. The number of clusters is varied from 1 to 15, and the SSE and SC indices for 
each cluster are calculated and plotted as curves. By examining the SSE and SC curves, the 
appropriate number of clusters is determined to be four. The 3650 scenarios are then divided 
into four clusters, resulting in four typical source load temporal–spatial correlation scenar-
ios. The algorithm process is shown in Figure 9, and the resulting output curves for the typ-
ical scenarios are shown in Figure 10. The details of each typical scenario are provided in 
Table 10. 
Start
Extract the data and generate the correlation curve
End
Calculate the correlation indicators
Select the number of clusters based on the and SC
Obtain the cluster centers
Classify all the scenarios
Regenerate the cluster centers
Output the scenarios and their probabilities
？
ε
Δ ≤
N
Y
1
2
3
4
5
6
SSE
SE
SSE
SE
 
Figure 9. Typical scene generation algorithm ﬂow.



<!-- page 18/32 -->

Sustainability 2025, 17, 5324 
18 of 32 
 
04：00
800
1000
1200
1400
1600
PV output / kW
Time
Scenario 1
Scenario 2
Scenario 3
Scenario 4
0
2500
5000
7500
10,000
12,500
15,000
Load demand / kW
08：00
12：00
16：00
20：00
24：00
 
Figure 10. Typical day scenarios based on Copula theory. 
Table 10. Typical scenario probability based on Copula theory. 
Typical Daily Scenarios 
Probability 
1 
0.3907 
2 
0.0696 
3 
0.2444 
4 
0.2953 
By observing Figure 10, it can be seen that, during speciﬁc time periods, the variation 
trends of PV output and load in diﬀerent scenarios exhibit a certain degree of correlation: 
they either increase or decrease simultaneously or show opposite trends. This correlation 
is not accidental but is due to the source load temporal–spatial correlation probability 
model based on Copula theory. This model eﬀectively captures the temporal–spatial cor-
relation between source and load outputs, thereby reducing the impact of uncertainties 
on the distribution network. Therefore, the source load temporal–spatial correlation sce-
narios generated by this model can accurately simulate the source load temporal–spatial 
correlation of the region, providing an important reference value for distribution network 
planning. 
To more intuitively demonstrate this correlation, the source load output curves from 
Scenario 1, which has the highest probability of occurrence, are selected for comparison, 
as shown in Figure 11. By comparing these curves, the dynamic relationship between the 
source and load outputs becomes more clearly visible. 
04：00
800
1000
1200
1400
1600
PV output / kW
Time
0
2500
5000
7500
10,000
12,500
15,000
Load demand / kW
08：00
12：00
16：00
20：00
24：00
 
Figure 11. Source load output curve under Scenario 1. 
From Figure 11, it can be observed that both the load demand curve and the PV out-
put curve exhibit ﬂuctuations. These ﬂuctuations are primarily due to variations in



<!-- page 19/32 -->

Sustainability 2025, 17, 5324 
19 of 32 
 
sunlight intensity at diﬀerent times of the day and people’s electricity consumption habits. 
Notably, PV output is almost zero at night, while, during the daytime, from sunrise to 
sunset, it shows higher output levels. At the same time, the load also shows a distinct 
upward trend after sunrise, indicating that PV generation output and load demand are 
positively correlated in terms of both time and space, in most cases. 
Further observation of the PV output curve and the load curve reveals that, at certain 
times, the degree of variation for both curves is quite similar, for example, between 6 a.m. 
and 2 p.m. At other times, such as between 2 p.m. and 8 p.m., their variation trends are 
the opposite. This suggests that the relationship between PV generation output and load 
demand is not ﬁxed but can show either a positive or negative correlation, depending on 
the speciﬁc situation. This variation closely reﬂects the real-world scenario, illustrating 
the complex relationship between load demand and PV output. 
Therefore, by applying the obtained source load temporal–spatial correlation typical 
scenarios to the source–network–storage collaborative planning model for the distribution 
network, the correlation between source and load can be more accurately reﬂected. This 
model design ensures that the results are more aligned with actual operating conditions, 
contributing to improving the economic eﬃciency of distribution network planning and 
enhancing its operational reliability. By fully considering the temporal–spatial correlation 
between source and load, it becomes possible to better optimize resource allocation, im-
prove energy utilization eﬃciency, and ensure that the distribution network can maintain 
eﬃcient and stable operation when facing various complex scenarios. 
4.3. Analysis of the 25-Bus System Planning Results 
To facilitate the presentation of the results, the PV conﬁguration, ESS conﬁguration, 
and network expansion planning results in this paper are all based on Scenario 1, which 
has the highest probability. According to the Scenario 1 case results, the PV and ESS plan-
ning conﬁguration results for the 25-bus system under diﬀerent schemes are shown in 
Tables 11 and 12, respectively. The cost comparisons under diﬀerent schemes are shown 
in Table 13. 
Table 11. PV planning and conﬁguration results in diﬀerent schemes. 
System 
Scheme 
Installed Bus 
Installed Capacity/MW 
Total Generation/MWh 
25-bus system 
2 
10, 12, 19 
9.85 
7019.54 
4 
10, 12, 16, 19 
11.82 
9502.61 
Table 12. ESS planning and conﬁguration results in diﬀerent schemes. 
System 
Scheme 
Installed Bus 
Total Installed Apparent Power/kVA 
Total Installed Capacity/kWh 
25-bus system 
3 
5, 16 
1100 
1600 
4 
2, 11, 17 
1700 
2200 
Table 13. Cost comparison of 25-bus system planning in diﬀerent schemes. 
 
Scheme 1 
Scheme 2 
Scheme 3 
Scheme 4 
ESS investment cost/CNY10,000 
0 
0 
227.3 
343.13 
Curtailment penalty cost/CNY10,000 
0 
1354.24 
0 
42.64 
Grid expansion cost/CNY10,000 
618.24 
589.23 
640.23 
589.26 
Distribution network comprehensive 
cost/CNY10,000 
618.24 
1943.47 
867.53 
975.03 
EENS 
0 
0 
0 
0 
Solving time/s 
145.27 
269.27 
194.94 
846.69



<!-- page 20/32 -->

Sustainability 2025, 17, 5324 
20 of 32 
 
From Table 11, it can be observed that, compared to Scheme 2, Scheme 4 increases 
the installed capacity of PV by 20%, and the total PV generation in the distribution net-
work increases by approximately 35.37%. From Table 13, it can be seen that, compared to 
Scheme 1, Scheme 2 and Scheme 4 result in increases of approximately 214.36% and 
57.71% in the distribution network comprehensive cost, respectively, while the PV in-
stalled capacity increases by 9.85 MW and 11.82 MW, and the total generation rises from 
0 to 7019.54 MWh and 9502.61 MWh. The curtailment penalty costs in Scheme 2 are higher 
than those in Scheme 4 due to the increase in PV grid-connected capacity without appro-
priate ESS deployment. 
From Table 12, it can be observed that, compared to Scheme 3, the total installed ap-
parent power of ESS in Scheme 4 increases by approximately 54.55%, and the total in-
stalled capacity increases by 37.7%. From Table 13, it can be seen that, compared to Scheme 
1, Scheme 3 and Scheme 4 result in increases of approximately 40.32% and 57.71% in the 
distribution network comprehensive cost, respectively, while the total installed capacity 
of ESS increases from 0 to 1.6 MWh and 2.2 MWh. The ESS investment cost in Scheme 4 is 
signiﬁcantly higher than in Scheme 3, which is due to the increased demand for ESS re-
sulting from the higher PV grid-connected capacity. 
Based on the network construction data obtained from the solution, combined with 
the above planning and conﬁguration results, the network topology diagrams after the 
25-bus system planning for diﬀerent schemes can be obtained, as shown in Figure 12. 
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
18
19
20
21
22
23
24
25
 
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
18
19
20
21
22
23
24
25
PV
PV
PV
CB
SVC
OLTC
OLTC
OLTC
OLTC
 
(a) 
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
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
ESS
ESS
CB
SVC
OLTC
OLTC
OLTC
OLTC
 
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
18
19
20
21
22
23
24
25
CB
SVC
OLTC
OLTC
OLTC
OLTC
PV
PV
PV
PV
ESS
ESS
ESS
 
(c) 
(d) 
Figure 12. Planning results of the 25-bus system in diﬀerent schemes. (a) Planning results of Scheme 
1. (b) Planning results of Scheme 2. (c) Planning results of Scheme 3. (d) Planning results of Scheme 
4.



<!-- page 21/32 -->

Sustainability 2025, 17, 5324 
21 of 32 
 
The hourly node voltage distribution within a single day for the 25-bus system under 
diﬀerent schemes is shown in Figure 13. 
04:0008:00
12:00
16:00
20:00
24:00
5
10
15
20
25
0.950
0.975
1.000
1.025
1.050
0.9632
0.9719
0.9806
0.9892
0.9979
1.007
1.015
1.024
1.033
1.041
1.050
 
04:0008:0012:00
16:00
20:00
24:00
5
10
15
20
25
0.950
0.975
1.000
1.025
1.050
0.9646
0.9731
0.9817
0.9902
0.9988
1.007
1.016
1.024
1.033
1.041
1.050
 
(a) 
(b) 
04:0008:00
12:00
16:00
20:00
24:00
5
10
15
20
25
0.950
0.975
1.000
1.025
1.050
0.9704
0.9784
0.9863
0.9943
1.002
1.010
1.018
1.026
1.034
1.042
1.050
 
04:0008:0012:00
16:00
20:00
24:00
5
10
15
20
25
0.950
0.975
1.000
1.025
1.050
0.9794
0.9865
0.9935
1.001
1.008
1.015
1.022
1.029
1.036
1.043
1.050
 
(c) 
(d) 
Figure 13. The 25-bus voltage distribution under Scenario 1 in diﬀerent schemes. (a) Scheme 1. (b) 
Scheme 2. (c) Scheme 3. (d) Scheme 4. 
It is evident that, although the voltage distribution in the 25-bus system under all 
four schemes remains within the safe range, there are noticeable diﬀerences in the distri-
bution patterns. Compared to Scheme 1, Scheme 2 shows higher voltage ﬂuctuations due 
to the integration of PV, with the voltage at the connection points being too high. In 
Scheme 3, the optimization of ESS conﬁguration helps smooth the voltage ﬂuctuations by 
charging during low load demand and discharging during high load demand, slightly 
alleviating the system’s voltage ﬂuctuations. Scheme 4, compared to Scheme 2, adopts the 
“PV + ESS” collaborative planning and conﬁguration, signiﬁcantly optimizing the sys-
tem’s voltage peaks and valleys by leveraging the characteristics of ESS, thereby reducing 
the system’s voltage ﬂuctuation. 
Based on Table 13 and Figure 14, it can be observed that the distribution network 
comprehensive cost of Scheme 4 is signiﬁcantly lower than that of Scheme 2, with a re-
duction of approximately 44.88%. Although Scheme 4 increases the ESS investment cost, 
the “PV + ESS” collaborative planning greatly reduces the curtailment penalty costs by 
enhancing the distribution network’s ability to absorb PV generation, thereby improving 
the economic eﬃciency of the distribution network planning. Compared to Scheme 3, 
Scheme 4 increases the cost by only about 12.39% while increasing PV power generation 
by 9502.61 MWh, thereby enhancing the distribution network’s capacity for PV integra-
tion and power absorption. Furthermore, the calculation results of EENS show that, under 
all the schemes, the system is able to fully meet the load demand, and no supply shortages 
occur in any scenario.



<!-- page 22/32 -->

Sustainability 2025, 17, 5324 
22 of 32 
 
1
2
3
4
0
300
600
900
1200
1500
1800
2100
Distribution network 
comprehensive cost / ¥10,000
Scheme
0
2000
4000
6000
8000
10,000
Total PV generation / MWh
Cost
Power generation
 
Figure 14. Distribution network comprehensive cost and total PV generation. 
A comparison of the distribution network comprehensive cost, total PV installed ca-
pacity, and total PV generation before and after considering the source load correlation 
scenarios is shown in Table 14. After considering the source load temporal–spatial corre-
lation scenarios, all schemes show a slight improvement compared to the schemes that do 
not consider these correlations. The typical daily scenarios generated using the source 
load temporal–spatial correlation probabilistic model based on Copula theory signiﬁ-
cantly mitigate the impact of source load uncertainty on the distribution network, enhance 
the network’s capacity for PV grid integration and absorption, and ultimately reduce the 
distribution network comprehensive cost, achieving an improvement in economic bene-
ﬁts. 
Table 14. The system comparison before and after the source load temporal–spatial correlation sce-
nario is considered. 
Considering the Source Load 
Temporal–Spatial Correlation 
Scenario 
Scheme 
Distribution Network Compre-
hensive Cost 
/CNY10,000 
Installed Capac-
ity of PV/MW 
Total PV Genera-
tion/MWh 
Yes 
1 
618.24 
0 
0 
2 
1943.47 
9.85 
7019.54 
3 
867.53 
0 
0 
4 
975.03 
11.82 
9502.61 
No 
1 
624.25 
0 
0 
2 
2165.97 
9.06 
6661.62 
3 
906.87 
0 
0 
4 
1193.95 
11.397 
8716.16 
4.4. Analysis of the 54-Bus System Planning Results 
The PV and ESS planning conﬁguration results for the 54-bus system under diﬀerent 
schemes are shown in Tables 15 and 16, respectively. The cost comparison under diﬀerent 
schemes is shown in Table 17. 
Table 15. PV planning and conﬁguration results under Scenario 1 in diﬀerent schemes. 
System 
Scheme 
Installed Bus 
Installed Capacity/MW 
Total Generation/MWh 
54-bus system 
2 
22, 26, 43 
17.37 
14,103.26 
4 
3, 25, 22, 27, 43 
21.73 
17,975.25



<!-- page 23/32 -->

Sustainability 2025, 17, 5324 
23 of 32 
 
Table 16. ESS planning and conﬁguration results under Scenario 1 in diﬀerent schemes. 
System 
Scheme 
Installed Bus 
Total Installed Apparent Power/kVA 
Total Installed Capacity/kWh 
54-bus system 
3 
8, 25, 37 
2000 
2600 
4 
8, 19, 32, 34 
3200 
4200 
Table 17. Cost comparison of 54-bus system planning under Scenario 1 in diﬀerent schemes. 
 
Scheme 1 
Scheme 2 
Scheme 3 
Scheme 4 
ESS investment cost/CNY10,000 
0 
0 
354.62 
478.16 
Curtailment penalty cost/CNY10,000 
0 
2088.36 
0 
102.35 
Grid expansion cost/CNY10,000 
1375.24 
1366.61 
1469.27 
1284.51 
Distribution network comprehensive 
cost/CNY10,000 
1375.24 
3454.97 
1823.89 
1865.02 
EENS 
0 
0 
0 
0 
Solving time/s 
769.20 
12 146.62 
1289.46 
1753.08 
As shown in Table 15, compared to Scheme 2, Scheme 4 increases the PV installed 
capacity by approximately 25.1%, and the total PV generation in the distribution network 
increases by about 27.45%. From Table 17, it can be seen that, compared to Scheme 1, both 
Scheme 2 and Scheme 4 increase the distribution network comprehensive cost by approx-
imately 151.23% and 35.61%, respectively. However, the PV installation capacity increases 
by 17.37 MW and 21.73 MW, and total generation increases from 0 to 14,103.26 MWh and 
17,975.25 MWh, respectively. The curtailment penalty in Scheme 2 is higher than in 
Scheme 4 due to the increased PV grid integration capacity without a reasonable ESS con-
ﬁguration. 
As shown in Table 16, compared to Scheme 3, Scheme 4 increases the total installed 
apparent power of ESS by approximately 70.27%, and the total installed capacity increases 
by 64%. From Table 17, it can be seen that, compared to Scheme 1, both Scheme 3 and 
Scheme 4 increase the distribution network comprehensive cost by approximately 32.62% 
and 35.61%, respectively. Meanwhile, the total installed ESS capacity increases from 0 to 
2.6 MWh and 4.2 MWh. The ESS investment cost in Scheme 4 is signiﬁcantly higher than 
in Scheme 3, as the increased PV grid integration capacity has raised the demand for ESS. 
Based on the network construction data obtained from the solution, combined with 
the above planning and conﬁguration results, the network topology diagrams after the 
54-bus system planning for diﬀerent schemes can be obtained, as shown in Figure 15. 
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
18
19
20
21
22
23
24
25
51
52
54
53
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
 
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
18
19
20
21
22
23
24
25
51
52
54
53
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
OLTC
OLTC
OLTC
OLTC
CB
SVC
PV
PV
PV
 
(a) 
(b)



<!-- page 24/32 -->

Sustainability 2025, 17, 5324 
24 of 32 
 
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
18
19
20
21
22
23
24
25
51
52
54
53
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
ESS
ESS
ESS
OLTC
OLTC
OLTC
OLTC
CB
SVC
 
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
18
19
20
21
22
23
24
25
51
52
54
53
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
OLTC
OLTC
OLTC
OLTC
CB
SVC
ESS
PV
PV
PV
PV
PV
ESS
ESS
ESS
 
(c) 
(d) 
Figure 15. Planning results of the 54-bus system in diﬀerent schemes. (a) Planning results of Scheme 
1. (b) Planning results of Scheme 2. (c) Planning results of Scheme 3. (d) Planning results of Scheme 
4. 
The hourly node voltage distribution within a single day for the 54-bus system under 
diﬀerent schemes is shown in Figure 16. 
04：0008：0012：00
16：00
20：00
24：00
9
18
27
36
45 54
0.950
0.975
1.000
1.025
1.050
0.9958
1.001
1.007
1.012
1.017
1.023
1.028
1.034
1.039
1.045
1.050
 
04：0008：0012：00
16：00
20：00
24：00
9
18
27
36
45 54
0.950
0.975
1.000
1.025
1.050
0.9608
0.9697
0.9786
0.9876
0.9965
1.005
1.014
1.023
1.032
1.041
1.050
 
(a) 
(b) 
04：0008：0012：00
16：00
20：00
24：00
9
18
27
36
45 54
0.950
0.975
1.000
1.025
1.050
0.9970
1.002
1.008
1.013
1.018
1.024
1.029
1.034
1.039
1.045
1.050
 
04：0008：0012：00
16：00
20：00
24：00
9
18
27
36
45 54
0.950
0.975
1.000
1.025
1.050
0.9608
0.9697
0.9786
0.9876
0.9965
1.005
1.014
1.023
1.032
1.041
1.050
 
(c) 
(d) 
Figure 16. The 54-bus voltage distribution under Scenario 1 in diﬀerent schemes. (a) Scheme 1. (b) 
Scheme 2. (c) Scheme 3. (d) Scheme 4. 
It is evident that, although the voltage distribution in the 54-bus system under all 
four schemes is within the safe range, the distribution diagrams show signiﬁcant diﬀer-
ences. Compared to Scheme 1, in Scheme 2, due to the integration of PV, the voltage at the 
connection points becomes too high, leading to a noticeable increase in the system’s volt-
age volatility. Scheme 3, compared to Scheme 1, adopts an optimized ESS conﬁguration,



<!-- page 25/32 -->

Sustainability 2025, 17, 5324 
25 of 32 
 
charging during low load demand and discharging during high load demand, thereby 
smoothing the peaks and valleys and slightly alleviating the system’s voltage volatility. 
Scheme 4, compared to Scheme 2, adopts the “PV + ESS” collaborative planning and con-
ﬁguration, signiﬁcantly optimizing the system’s voltage peaks and valleys by leveraging 
the characteristics of ESS, thereby reducing the system’s voltage ﬂuctuation. 
Based on Table 17 and Figure 17, it can be observed that the distribution network 
comprehensive cost of Scheme 4 is signiﬁcantly lower than that of Scheme 2, with a re-
duction of approximately 46.02%. Although Scheme 4 increases the ESS investment cost, 
the “PV + ESS” collaborative planning greatly reduces the curtailment penalty costs by 
enhancing the distribution network’s ability to absorb PV generation, thereby improving 
the economic eﬃciency of the distribution network planning. Compared to Scheme 3, 
Scheme 4 increases the cost by only about 2.23% while increasing PV power generation 
by 17 975.25 MWh, thereby enhancing the distribution network’s capacity for PV integra-
tion and power absorption. Furthermore, the calculation results of EENS show that, under 
all the schemes, the system is able to fully meet the load demand, and no supply shortages 
occur in any scenario. 
1
2
3
4
0
600
1200
1800
2400
3000
3600
Scheme
0
4000
8000
12,000
16,000
20,000
Cost
Power generation
Distribution network 
comprehensive cost / ¥10,000
Total PV generation / MWh
 
Figure 17. Distribution network comprehensive cost and total PV generation. 
The comparison of the distribution network comprehensive cost, total PV installed ca-
pacity, and total PV generation before and after considering the source load correlation sce-
narios is shown in Table 18. After considering the source load temporal–spatial correlation 
scenarios, all schemes show a slight improvement compared to the schemes that do not con-
sider these correlations. The typical daily scenarios generated using the source load tem-
poral–spatial correlation probabilistic model based on Copula theory significantly mitigate 
the impact of source load uncertainty on the distribution network, enhance the network’s 
capacity for PV grid integration and absorption, and ultimately reduce the distribution net-
work comprehensive cost, achieving an improvement in economic benefits. 
Table 18. The system comparison before and after the source load temporal–spatial correlation sce-
nario is considered. 
Considering the Source Load 
Temporal–Spatial Correlation 
Scenarios 
Scheme 
Distribution Network Compre-
hensive Cost 
/CNY10,000 
Installed Capac-
ity of PV/MW 
Total PV Gener-
ation/MWh 
Yes 
1 
1375.24 
0 
0 
2 
3454.97 
17.37 
14,103.26 
3 
1823.89 
0 
0 
4 
1865.02 
21.73 
17,975.25 
No 
1 
1441.24 
0 
0 
2 
3506.60 
16.24 
12,462.55 
3 
1923.49 
0 
0 
4 
1983.69 
20.62 
16,953.81



<!-- page 26/32 -->

Sustainability 2025, 17, 5324 
26 of 32 
 
4.5. Sensitivity Analysis 
4.5.1. Analysis of the Impact of PV and Load Forecasting Errors 
To further evaluate the robustness of the proposed method under forecast deviations, 
we have extended our analysis by introducing ±10% forecast errors into both PV genera-
tion and load demand based on the four typical daily scenarios already constructed via 
the Copula approach (as shown in Figure 10). 
Speciﬁcally, we considered two extreme error scenarios: 
(1) +10% Error Scenario (Pessimistic forecast): Actual PV output is 10% higher and load 
demand is 10% lower than forecasted. 
(2) −10% Error Scenario (Optimistic forecast): Actual PV output is 10% lower and load 
demand is 10% higher than forecasted. 
Based on these two error scenarios, the source–network–storage collaborative plan-
ning under the Scheme 4 setting is performed again for the 25-bus system, and the plan-
ning results are compared with the planning results of the original scenario that do not 
take the prediction errors into account, and the results are shown in Table 19. 
Table 19. Planning and conﬁguration results considering forecasting errors. 
 
Indicator 
Original Scenario 
+10% Error Scenario 
−10% Error Scenario 
PV 
Installed bus 
10, 12, 16, 19 
10, 12, 16, 19 
10, 12, 16, 19 
Installed capacity/MW 
11.82 
12.15 
11.60 
Total generation/MWh 
9502.61 
10,570.3 
8510.2 
ESS 
Installed bus 
2, 11, 17 
2, 11, 17 
2, 11, 17 
Total installed apparent 
power/kVA 
1700 
1780 
1620 
Total installed capac-
ity/kWh 
2200 
2350 
2050 
Cost compari-
son 
ESS investment 
cost/CNY10,000 
343.13 
365.8 
320.5 
Curtailment penalty 
cost/CNY10,000 
42.64 
65.3 
28.5 
Grid expansion 
cost/CNY10,000 
589.26 
598.5 
580.1 
Distribution network 
comprehensive 
cost/CNY10,000 
975.03 
1029.60 
929.10 
The comparison shows that PV and ESS siting decisions remain stable, and their ca-
pacity conﬁgurations adapt ﬂexibly based on the system operation conditions under each 
error scenario. In the +10% error case, increased PV output and reduced load demand lead 
to more PV curtailment risk, prompting the model to increase the ESS capacity to absorb 
excess energy. This results in a rise in total system cost from 9.75 million CNY to 10.30 
million CNY. 
Conversely, in the −10% error case, a higher load and lower PV output allow the more 
direct consumption of PV energy, reducing the need for ESS. The system cost accordingly 
decreases to 9.29 million CNY due to a lower curtailment penalty and ESS investment. 
These results demonstrate that the proposed planning method can adaptively adjust 
to forecast uncertainties while maintaining planning stability, especially in siting deci-
sions. The model eﬀectively mitigates the impact of forecast errors without causing dis-
ruptive changes to the overall planning scheme.



<!-- page 27/32 -->

Sustainability 2025, 17, 5324 
27 of 32 
 
4.5.2. Comparative Analysis of Diﬀerent Scenario Reduction Methods 
To verify the rationality and eﬀectiveness of the K-means clustering algorithm 
adopted in this study for scenario reduction, this section selects the typical simultaneous 
backward reduction (SBR) method as a benchmark for comparison. A comparative anal-
ysis is conducted in terms of computational eﬃciency and comprehensive cost, with the 
results summarized in Table 20. 
Table 20. Performance comparison between K-means and SBR. 
Method 
Scenario Reduction Compu-
tation Time/s 
Comprehensive Cost of 25-
Bus System/CNY10,000 
Comprehensive Cost of 54-
Bus System/CNY10,000 
K-means 
6.5 
975.03 
1865.02 
SBR 
362.3 
942.65 
1808.70 
As shown in Table 20, in terms of scenario reduction computation time, the K-means 
method requires only 8.5 s, whereas the SBR method takes as long as 362.3 s. This indicates 
that K-means signiﬁcantly outperforms SBR in computational eﬃciency. The results 
clearly demonstrate that the K-means method has a substantial computational advantage 
when handling large-scale uncertain scenarios, contributing to an improved overall 
model-solving eﬃciency and scalability. 
Regarding the optimization results, the comprehensive cost obtained using the K-
means method is 3.44% and 3.11% higher than that of SBR in the 25-bus and 54-bus sys-
tems, respectively. Although there is a certain degree of cost deviation, the diﬀerences are 
relatively small and fall within an acceptable range in practical engineering applications. 
This indicates that, while signiﬁcantly enhancing the reduction eﬃciency, the K-means 
method still retains the statistical characteristics of the original scenarios to a reasonable 
extent. 
Therefore, considering both computational eﬃciency and the quality of the planning 
results, the adoption of the K-means clustering algorithm as the scenario reduction 
method in this study represents a well-balanced and rational choice between solution ac-
curacy and computational feasibility. This method not only ensures that the planning out-
comes remain of high reference value but also greatly improves the solution eﬃciency, 
meeting the practical needs of planning tasks. 
4.5.3. Analysis of the Impact of Cost Coeﬃcients 
To further investigate the impact of key economic parameters on planning decisions, 
this section conducts a sensitivity analysis on several core cost coeﬃcients, including the 
investment cost of ESS, the PV curtailment penalty, and the unit length construction cost 
of the line. By examining how variations in these coeﬃcients inﬂuence the PV and ESS 
conﬁguration, curtailment penalty cost, grid expansion, and system comprehensive cost 
in Scheme 4 of the 25-bus system, the trade-oﬀs in planning strategies under diﬀerent 
economic constraints are analyzed. The results are presented in Tables 21–23. 
Table 21. Impact of ESS investment cost variations on key planning indicators. 
Variation in ESS 
Investment Cost 
Installed Capacity 
of PV/MW 
Total Installed Ca-
pacity of 
ESS/kWh 
Curtailment Pen-
alty 
Cost/CNY10,000 
Grid Expansion 
Cost/CNY10,000 
Distribution Net-
work COMPREHEN-
SIVE 
Cost/CNY10,000 
0.5 
12.85 
2850 
20.15 
575.60 
791.57 
0.8 
12.05 
2300 
38.10 
586.50 
919.90 
1.0 
11.82 
2200 
42.64 
589.26 
975.03



<!-- page 28/32 -->

Sustainability 2025, 17, 5324 
28 of 32 
 
1.2 
11.75 
2100 
48.50 
591.80 
1039.00 
1.5 
11.25 
1600 
75.80 
601.50 
1102.95 
Table 22. Impact of PV curtailment penalty variations on key planning indicators. 
Variation in PV 
Curtailment Pen-
alty 
Installed Capacity 
of PV/MW 
Total Installed Ca-
pacity of 
ESS/kWh 
Curtailment Pen-
alty 
Cost/CNY10,000 
Grid Expansion 
Cost/CNY10,000 
Distribution Net-
work Comprehen-
sive 
Cost/CNY10,000 
0.5 
12.50 
2050 
25.30 
580.50 
930.90 
0.8 
11.90 
2180 
39.10 
587.80 
967.10 
1.0 
11.82 
2200 
42.64 
589.26 
975.03 
1.2 
11.75 
2280 
48.15 
592.60 
996.65 
1.5 
11.30 
2580 
50.95 
598.20 
1047.95 
Table 23. Impact of line construction cost variations on key planning indicators. 
Variation in Line 
Construction Cost 
Installed Capacity 
of PV/MW 
Total Installed Ca-
pacity of 
ESS/kWh 
Curtailment Pen-
alty 
Cost/CNY10,000 
Grid Expan-
sion 
Cost/CNY10,
000 
Distribution Network 
COMPREHENSIVE 
Cost/CNY10,000 
0.5 
12.65 
1950 
30.50 
330.15 
670.85 
0.8 
11.90 
2150 
40.70 
505.60 
884.10 
1.0 
11.82 
2200 
42.64 
589.26 
975.03 
1.2 
11.78 
2250 
43.50 
685.30 
1079.60 
1.5 
11.50 
2450 
48.10 
738.60 
1168.20 
Table 21 shows that the investment cost of ESS has a signiﬁcant impact on the plan-
ning scheme. As the ESS investment cost decreases, the total installed capacity of ESS in 
the system exhibits a clear upward trend. Meanwhile, improved storage economics pro-
mote greater PV utilization, leading to an increase in the installed capacity of PV and a 
substantial reduction in curtailment penalty cost. Consequently, the distribution network 
comprehensive cost decreases signiﬁcantly with the reduction in ESS costs. Conversely, 
when the ESS investment cost rises, the ESS capacity decreases, PV utilization is restricted, 
curtailment increases, and the total system cost rises. 
Table 22 indicates that the PV curtailment penalty coeﬃcient signiﬁcantly aﬀects the 
system’s curtailment control strategy and storage conﬁguration. When the penalty coeﬃ-
cient is low, the system exhibits a higher tolerance for curtailment, possibly planning more 
the installed capacity of PV while allowing greater curtailment. Under this condition, the 
demand for ESS capacity is relatively low, and the distribution network comprehensive 
cost may decrease due to the reduced investment in curtailment mitigation and storage. 
As the penalty coeﬃcient increases, the system strictly controls curtailment to avoid high 
penalties, primarily by increasing the ESS capacity. However, an excessively high penalty 
coeﬃcient may lead to overinvestment in mitigation measures aimed at minimizing cur-
tailment, thereby increasing the distribution network comprehensive cost. Therefore, set-
ting a reasonable PV curtailment penalty coeﬃcient is crucial to balancing PV utilization 
promotion and economic cost control. 
Table 23 reveals that the unit length construction cost of the line directly impacts the 
total investment in grid expansion and indirectly inﬂuences PV and ESS conﬁguration 
strategies. When the line cost is low, grid expansion becomes more economical for ena-
bling long-distance PV transmission and utilization. Under these conditions, the system 
may increase the installed capacity of PV while reducing the reliance on local storage, 
resulting in a decreased total installed capacity of ESS. Conversely, when line construction



<!-- page 29/32 -->

Sustainability 2025, 17, 5324 
29 of 32 
 
costs are high, grid expansion becomes expensive, and the system tends to minimize reli-
ance on line expansion by increasing the local ESS capacity or adjusting the PV layout to 
achieve nearby utilization. Although the physical scale of grid expansion may be con-
strained, the grid expansion cost still rises due to the high unit construction cost. 
5. Conclusions 
This paper addresses the uncertainty of PV output and load demand by establishing 
a source load temporal–spatial correlation probabilistic model based on Copula theory. 
The Monte Carlo method is used to generate numerous source load temporal–spatial cor-
relation scenarios. Then, the K-means clustering algorithm is applied to reduce the vast 
scenario set, ensuring that the variability of the PV output and load demand is preserved 
while improving the computational eﬃciency, resulting in representative typical daily 
scenarios. On this basis, a source–network–storage collaborative planning model based 
on stochastic scenarios is established with the objective of minimizing the annual distri-
bution network comprehensive cost. Through comparative analysis of case studies with 
25-bus and 54-bus systems, the following conclusions are drawn: 
(1) By establishing a source load temporal–spatial correlation probabilistic model based 
on Copula theory and applying the Monte Carlo method and K-means clustering 
algorithm for scenario generation and reduction, four typical daily scenarios were 
obtained while preserving the variability of PV output and load demand. The results 
demonstrate that a small number of typical daily scenarios can eﬀectively describe 
the uncertainty and temporal–spatial correlation of PV output and load demand var-
iations while avoiding the curse of dimensionality during the solution process, fur-
ther ensuring the computational eﬃciency. 
(2) Comparing planning schemes with and without considering source load temporal–
spatial correlation, the schemes that account for this correlation consistently perform 
slightly better. They eﬀectively mitigate the impact of PV and load uncertainty on the 
distribution network, enhance the network’s capacity for PV integration and con-
sumption, reduce the distribution network comprehensive cost, and achieve an in-
crease in economic beneﬁts. 
(3) Comparing planning schemes with and without considering source load temporal–
spatial correlation, the schemes that account for this correlation consistently perform 
slightly better. They eﬀectively mitigate the impact of PV and load uncertainty on the 
distribution network, enhance the network’s PV hosting capacity, reduce the distri-
bution network comprehensive cost, and contribute to the development of more sus-
tainable distribution networks. 
Table 24 clearly shows a comparison of the key characteristics between the method 
proposed in this paper and the existing research methods. 
Table 24. A comparison between the method proposed in this paper and the existing research meth-
ods. 
Comparison 
Dimension 
Proposed Method in This Paper 
General Characteristics of Existing Research 
Methods (Based on Literature Review) 
Scope of plan-
ning object co-
ordination 
Source–network–storage coordinated planning: 
Uniﬁed optimization of PV siting and sizing, ESS 
siting and sizing, and distribution network expan-
sion, pursuing system-level global optimum. 
Focuses on optimizing single types of distributed 
resources (e.g., DG or ESS) or achieves only source-
storage coordination, with insuﬃcient considera-
tion of the expansion and interactive eﬀects of the 
distribution network, making system-level global 
optimization diﬃcult.



<!-- page 30/32 -->

Sustainability 2025, 17, 5324 
30 of 32 
 
Handling of 
source load 
temporal–spa-
tial correlation 
Explicitly models and accurately captures the com-
plex, non-linear temporal–spatial correlation be-
tween PV output and load demand via Copula the-
ory, signiﬁcantly enhancing scenario realism and 
planning accuracy. 
Ignores complex source load correlations or adopts 
simpliﬁed assumptions of independence or linear 
correlation, failing to accurately reﬂect complex in-
teractions in real systems and leading to insuﬃ-
ciently reﬁned uncertainty descriptions. 
Quality of sce-
nario genera-
tion and reduc-
tion 
Generates massive annual random scenarios via 
Monte Carlo sampling, then eﬃciently reduces 
them using K-means clustering to obtain typical 
daily scenarios that reﬂect both annual diversity 
and retain key temporal characteristics. 
Scenario generation methods may be simplistic 
(e.g., typical day method) or, while using random 
sampling, may not fully account for variations 
across diﬀerent periods (e.g., inter-day), resulting 
in insuﬃcient representativeness and diversity of 
scenarios. 
Planning objec-
tive and overall 
beneﬁts 
Aims to enhance eﬃcient PV accommodation and 
the overall economics of distribution network 
planning, striving to achieve dual improvements 
in the PV hosting capacity and economic beneﬁts 
through comprehensive coordination and reﬁned 
modeling. 
The objective may focus on local optimization (e.g., 
speciﬁc equipment economics or performance indi-
cators), or due to a lack of comprehensive coordi-
nation and reﬁned uncertainty/correlation han-
dling, PV hosting potential may not be fully ex-
ploited, and the overall system economics and ro-
bustness to uncertainty need improvement. 
Despite the promising results achieved in this study, several directions remain open 
for further research and development: 
(1) Multi-objective coordinated planning and Pareto analysis: 
This paper promotes PV utilization indirectly by incorporating the curtailment pen-
alty cost into the comprehensive cost function. Future work may explicitly formulate a 
multi-objective optimization model that simultaneously considers planning economy, 
system reliability, and maximization of renewable energy integration (or minimization of 
carbon emissions). Solving such multi-objective problems and analyzing the resulting Pa-
reto frontier can provide decision-makers with more intuitive and informative trade-oﬀ 
analyses among competing objectives. 
(2) Validation and extension of the proposed method to more complex and realistic 
distribution networks: 
This study primarily uses typical radial feeders as test systems. Future research will 
further validate and extend the proposed method on more complex benchmark networks, 
such as the IEEE 123-bus system, or on real-world utility distribution feeders. The feasi-
bility, computational performance, and planning eﬀectiveness of the method under com-
plex topologies will be systematically evaluated. In addition, future work will explore the 
relaxation accuracy of power ﬂow modeling under non-radial structures, as well as the 
development of coordinated control strategies in multi-source, multi-loop distribution 
systems, laying a solid foundation for real-world engineering applications. 
Author Contributions: Conceptualization, J.W., J.L., and X.L.; Data curation, C.C.; Formal analysis, 
J.W. and C.C.; Funding acquisition, J.L.; Investigation, J.W. and X.L.; Methodology, C.C.; Project 
administration, J.L.; Resources, X.L.; Software, X.L.; Supervision, J.L.; Validation, C.C.; Visualiza-
tion, C.C. and X.L.; Writing—original draft, J.W.; Writing—review and editing, J.W., J.L., and W.W. 
All authors have read and agreed to the published version of the manuscript. 
Funding: This research was funded by the National Key Research and Development Program of 
China, grant number 2022YFF0610601. 
Institutional Review Board Statement: Not applicable. 
Informed Consent Statement: Not applicable.



<!-- page 31/32 -->

Sustainability 2025, 17, 5324 
31 of 32 
 
Data Availability Statement: The data that support the ﬁndings of this study are available from the 
corresponding author upon reasonable request. 
Conﬂicts of Interest: The authors declare no conﬂicts of interest. 
References 
1. 
Ding, T.; Li, C.; Yang, Y.; Jiang, J.; Bie, Z.; Blaabjerg, F. A Two-Stage Robust Optimization for Centralized-Optimal Dispatch of 
Photovoltaic 
Inverters 
in 
Active 
Distribution 
Networks. 
IEEE 
Trans. 
Sustain. 
Energy 
2017, 
8, 
744–754. 
https://doi.org/10.1109/TSTE.2016.2605926. 
2. 
Jafari, M.R.; Parniani, M.; Ravanji, M.H. Decentralized Control of OLTC and PV Inverters for Voltage Regulation in Radial 
Distribution 
Networks 
with 
High 
PV 
Penetration. 
IEEE 
Trans. 
Power 
Deliv. 
2022, 
37, 
4827–4837. 
https://doi.org/10.1109/TPWRD.2022.3160375. 
3. 
Le, J.; Lang, H.; Liao, X.; Wang, J.; Mao, T. Aﬃnely Adjustable Robust Optimization Method for Active Distribution Network 
Based on Generalized Linear Polyhedral. Autom. Electr. Power Syst. 2023, 47, 138–148. 
4. 
Ayalew, M.; Khan, B.; Giday, I.; Mahela, O.P.; Khosravy, M.; Gupta, N.; Senjyu, T. Integration of Renewable Based Distributed 
Generation for Distribution Network Expansion Planning. Energies 2022, 15, 1378. https://doi.org/10.3390/en15041378. 
5. 
Mahdavi, M.; Kimiyaghalam, A.; Alhelou, H.H.; Javadi, M.S.; Ashouri, A.; Catalão, J.P.S. Transmission Expansion Planning 
Considering Power Losses, Expansion of Substations and Uncertainty in Fuel Price Using Discrete Artiﬁcial Bee Colony Algo-
rithm. IEEE Access 2021, 9, 135983–135995. https://doi.org/10.1109/ACCESS.2021.3116802. 
6. 
Li, C.; Feng, C.; Li, J.; Hu, D.; Zhu, X. Comprehensive Frequency Regulation Control Strategy of Thermal Power Generating 
Unit and ESS Considering Flexible Load Simultaneously Participating in AGC. J. Energy Storage 2023, 58, 106394. 
https://doi.org/10.1016/j.est.2022.106394. 
7. 
Ye, G.; Qian, X.; Yang, X.; Zhao, L.; Shang, J.; Wu, M.; Zhao, T. Planning of PV-ESS System for Distribution Network Considering 
PV Penetration. In Proceedings of the 2020 IEEE 3rd International Conference on Electronics Technology (ICET), Chengdu, 
China, 8–12 May 2020; pp. 339–343. 
8. 
Memarzadeh, G.; Keynia, F. A New Hybrid CBSA-GA Optimization Method and MRMI-LSTM Forecasting Algorithm for PV-
ESS Planning in Distribution Networks. J. Energy Storage 2023, 72, 108582. https://doi.org/10.1016/j.est.2023.108582. 
9. 
Wang, Y.; Jiang, Y.; Liu, H.; Pan, T. Research on Coordinated Planning for Wind-PV-ESS Integration into the Distribution Grid 
Based on Presentative Scenarios. In Proceedings of the 2024 7th International Conference on Energy, Electrical and Power En-
gineering (CEEPE), Yangzhou, China, 26–28 April 2024; pp. 1378–1382. 
10. 
Cho, K.-H.; Kim, J.; Byeon, G.; Son, W. Optimal Sizing Strategy and Economic Analysis of PV-ESS for Demand Side Manage-
ment. J. Electr. Eng. Technol. 2024, 19, 2859–2874. https://doi.org/10.1007/s42835-023-01734-2. 
11. 
Bhadoria, V.S.; Pal, N.S.; Shrivastava, V. Artiﬁcial Immune System Based Approach for Size and Location Optimization of Dis-
tributed Generation in Distribution System. Int. J. Syst. Assur. Eng. Manag. 2019, 10, 339–349. https://doi.org/10.1007/s13198-019-
00779-9. 
12. 
Pompern, N.; Premrudeepreechacharn, S.; Siritaratiwat, A.; Khunkitti, S. Optimal Placement and Capacity of Battery Energy 
Storage System in Distribution Networks Integrated with PV and EVs Using Metaheuristic Algorithms. IEEE Access 2023, 11, 
68379–68394. https://doi.org/10.1109/ACCESS.2023.3291590. 
13. 
Tao, L.; Gao, Y.; Cao, L.; Zhu, H. Distributed Real-Time Pricing for Smart Grid Considering Sparse Constraints and Integration 
of Distributed Energy and Storage Devices. Compel-Int. J. Comput. Math. Electr. Electron. Eng. 2021, 40, 978–996. 
https://doi.org/10.1108/COMPEL-04-2021-0135. 
14. 
Zhang, Y.; Ren, S.; Dong, Z.Y.; Xu, Y.; Meng, K.; Zheng, Y. Optimal Placement of Battery Energy Storage in Distribution Net-
works Considering Conservation Voltage Reduction and Stochastic Load Composition. IET Gener. Transm. Distrib. 2017, 11, 
3862–3870. https://doi.org/10.1049/iet-gtd.2017.0508. 
15. 
Liu, T.; Chen, J.; Zhang, W.; Zhang, Y. Joint Planning for PV-SESS-MESS in Distribution Network towards 100% Self-Consump-
tion of PV via Consensus-Based ADMM. J. Energy Storage 2024, 90, 111747. https://doi.org/10.1016/j.est.2024.111747. 
16. 
Qi, C.; Wang, K.; Fu, Y.; Li, G.; Han, B.; Huang, R.; Pu, T. A Decentralized Optimal Operation of AC/DC Hybrid Distribution 
Grids. IEEE Trans. Smart Grid 2018, 9, 6095–6105. https://doi.org/10.1109/TSG.2017.2703582. 
17. 
Mukhopadhyay, B.; Das, D. Multi-Objective Dynamic and Static Reconﬁguration with Optimized Allocation of PV-DG and 
Battery Energy Storage System. Renew. Sustain. Energy Rev. 2020, 124, 109777. https://doi.org/10.1016/j.rser.2020.109777.



<!-- page 32/32 -->

Sustainability 2025, 17, 5324 
32 of 32 
 
18. 
Gu, G.; Yang, P.; Tang, B.; Wang, D.; Lai, X. A Method for Improving the Balance Ability of Distribution Networks Through 
Source-Load-Storage 
Collaborative 
Optimization. 
Proc. 
Chin. 
Soc. 
Electr. 
Eng. 
2024, 
44, 
5097–5109. 
https://doi.org/10.13334/j.0258-8013.pcsee.231648. 
19. 
Li, Y.; Feng, B.; Wang, B.; Sun, S. Joint Planning of Distributed Generations and Energy Storage in Active Distribution Networks: 
A Bi-Level Programming Approach. Energy 2022, 245, 123226. https://doi.org/10.1016/j.energy.2022.123226. 
20. 
Sannigrahi, S.; Ghatak, S.R.; Acharjee, P. Multi-Scenario Based Bi-Level Coordinated Planning of Active Distribution System 
Under Uncertain Environment. IEEE Trans. Ind. Appl. 2020, 56, 850–863. https://doi.org/10.1109/TIA.2019.2951118. 
21. 
Deng, H.; Zheng, Y.; Zhang, X.; Zeng, F.; Zheng, R. Distributed Power Planning and Reactive Power Optimization Strategies 
Considering Timing Scenarios. J. Guizhou Univ. (Nat. Sci.) 2023, 40, 74–81. https://doi.org/10.15958/j.cnki.gdxbzrb.2023.02.12. 
22. 
Lü, B.; Yan, W.; Zhao, X.; Yu, J. Coordinated Allocation of Tie Lines and DWGs Considering Random Energy. Proc. Chin. Soc. 
Electr. Eng. 2013, 33, 145–152+23. https://doi.org/10.13334/j.0258-8013.pcsee.2013.34.020. 
23. 
Ji, X.; Li, C.; Xie, B.; Wang, Y.; Wang, Q. A Wind Power Scenario Simulation Method Considering Trend and Randomness. In 
Proceedings of the 16th Annual Conference of China Electrotechnical Society; Liang, X., Li, Y., He, J., Yang, Q., Eds.; Springer Nature 
Singapore: Singapore, 2022; pp. 1043–1050. 
24. 
Xiao, C.; Ye, J.; Esteves, R.M.; Rong, C. Using Spearman′s Correlation Coeﬃcients for Exploratory Data Analysis on Big Dataset. 
Concurr. Comput. Pract. Exp. 2016, 28, 3866–3878. https://doi.org/10.1002/cpe.3745. 
25. 
Alzaid, A.A.; Alhadlaq, W.M. A New Family of Archimedean Copulas: The Half-Logistic Family of Copulas. Mathematics 2024, 
12, 101. https://doi.org/10.3390/math12010101. 
26. 
Rosenblatt, M. Remarks on Some Nonparametric Estimates of a Density Function. Ann. Math. Stat. 1956, 27, 832–837. 
https://doi.org/10.1214/aoms/1177728190. 
27. 
Zhao, L.; Zeng, Y.; Li, Y.; Peng, D.; Wang, Y. Coordinated Planning of Power Systems under Uncertain Characteristics Based on 
the Multilinear Monte Carlo Method. Energies 2023, 16, 7761. https://doi.org/10.3390/en16237761. 
28. 
Ebeed, M.; Abdel-Fatah, S.; Kamel, S.; Nasrat, L.; Jurado, F.; Harrison, A. Incorporating Photovoltaic Inverter Capability into 
Stochastic Optimal Reactive Power Dispatch through an Enhanced Artiﬁcial Gorilla Troops Optimizer. IET Renew. Power Gener. 
2023, 17, 3267–3288. https://doi.org/10.1049/rpg2.12841. 
29. 
Lavorato, M.; Franco, J.F.; Rider, M.J.; Romero, R. Imposing Radiality Constraints in Distribution System Optimization Prob-
lems. IEEE Trans. Power Syst. 2012, 27, 172–180. https://doi.org/10.1109/TPWRS.2011.2161349. 
30. 
Bobo, L.; Venzke, A.; Chatzivasileiadis, S. Second-Order Cone Relaxations of the Optimal Power Flow for Active Distribution 
Grids: Comparison of Methods. Int. J. Electr. Power Energy Syst. 2021, 127, 106625. https://doi.org/10.1016/j.ijepes.2020.106625. 
31. 
Chowdhury, M.M.-U.-T.; Kamalasadan, S.; Paudyal, S. A Second-Order Cone Programming (SOCP) Based Optimal Power Flow 
(OPF) Model with Cyclic Constraints for Power Transmission Systems. IEEE Trans. Power Syst. 2024, 39, 1032–1043. 
https://doi.org/10.1109/TPWRS.2023.3247891. 
32. 
Sarimuthu, C.R.; Ramachandaramurthy, V.K.; Agileswari, K.R.; Mokhlis, H. A Review on Voltage Control Methods Using On-
Load Tap Changer Transformers for Networks with Renewable Energy Sources. Renew. Sustain. Energy Rev. 2016, 62, 1154–1161. 
https://doi.org/10.1016/j.rser.2016.05.016. 
Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual au-
thor(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to 
people or property resulting from any ideas, methods, instructions or products referred to in the content.
