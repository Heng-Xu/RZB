<!--
source: D6_决策方法/EN_Energies_grid_planning_adaptability_AHP_CRITIC_2024.pdf
sha256: 3242446612bdd263a34a7e43eaaf3c4b2a96c6b268802a6ca7a4459a09676ed7
method: pymupdf
pages: 24
-->

<!-- page 1/24 -->

 
 
 
 
Energies 2024, 17, 3672. https://doi.org/10.3390/en17153672 
www.mdpi.com/journal/energies 
Article 
Adaptability Evaluation of Power Grid Planning Scheme  
for Novel Power System Considering Multiple  
Decision Psychology 
Yuqing Wang 1,2,*, Chaochen Yan 2, Zhaozhen Wang 2 and Jiaxing Wang 2 
1 State Key Laboratory of Alternate Electrical Power System with Renewable Energy Sources, North China 
Electric Power University, Beijing 102206, China 
2 Department of Economic Management, North China Electric Power University, Baoding 071000, China; 
ycc@ncepu.edu.cn (C.Y.); 220232218003@ncepu.edu.cn (Z.W.); 220222218095@ncepu.edu.com (J.W.) 
* Correspondence: yuqingwang@ncepu.edu.cn 
Abstract: With a substantial fraction of renewable energy integrated into the electrical grid, the new 
power system urgently requires grid planning scheme displaying adaptability to diﬀerent energy 
types and their volatility. Considering the indeterminacy of renewable energy generation output 
and the diﬀerent attitudes of decision-makers towards its risk, this paper proposes an adaptability 
assessment methodology for power grid planning schemes considering multiple decision psychol-
ogy. First, an evaluation indicator framework is established based on the adaptive requirements of 
the grid planning for novel power system, and the weights of indicators are calculated based on an 
improved AHP-CRITIC combination weighting method. Second, improved cumulative prospect 
theory (ICPT) is adopted to improve to the calculation method of the distance between the evalua-
tion program and the positive and negative ideal programs in the GRA and TOPSIS, which eﬀec-
tively characterize the diﬀerent decision-making psychologies, and a combination evaluation model 
is constructed based on a cooperative game (CG), namely, an adaptability evaluation model of grid 
planning schemes for novel power systems based on GRA-TOPSIS integrating CG and ICPT. Fi-
nally, the proposed model serves to evaluate grid planning schemes of three regions in China’s 14th 
Five-Year Plan. The evaluation results show that the adaptability of the schemes varies under diﬀer-
ent decision-making psychologies, and under the risk-aggressive and loss-sensitive decision-mak-
ing psychologies, grid planning scheme of Region 1 with the greatest accommodation capacity of 
renewable energy is preferable. 
Keywords: novel power system; adaptability evaluation; grid planning; decision psychology;  
combination evaluation 
 
1. Introduction 
With the increasing energy crisis and environmental pollution, China is committed to 
constructing a novel power system mainly composed of new energy to promote the clean 
and low-carbon transformation of energy [1]. In the future, the substantial integration of 
renewable energy generation will emerge as a pivotal characteristic of the novel power sys-
tem, but its stochastic and intermittent nature will pose a serious challenge to the existing 
power grid [2,3]. In view of the central position of the power grid in power transmission 
and distribution, the adaptability of its planning scheme is decisive for ensuring the stable 
operation and economic benefits of the novel power system [4,5]. Therefore, there is an im-
mediate need to assess the adaptability of the grid planning approaches for novel power 
system to efficiently identify the weaknesses, rationally construct the grid, and offer guid-
ance for ensuring the system’s future economic and stable functioning [6]. 
Citation: Wang, Y.; Yan, C.; Wang, 
Z.; Wang, J. Adaptability Evaluation 
of Power Grid Planning Scheme for 
Novel Power System Considering 
Multiple Decision Psychology.  
Energies 2024, 17, 3672. https:// 
doi.org/10.3390/en17153672 
Academic Editor: Javier Contreras 
Received: 31 May 2024 
Revised: 8 July 2024 
Accepted: 22 July 2024 
Published: 25 July 2024 
 
Copyright: © 2024 by the authors. Li-
censee MDPI, Basel, Switzerland. 
This article is an open access article 
distributed under the terms and con-
ditions of the Creative Commons At-
tribution (CC BY) license (https://cre-
ativecommons.org/licenses/by/4.0/).



<!-- page 2/24 -->

Energies 2024, 17, 3672 
2 of 24 
 
 
Recently, academics have conducted extensive research on evaluating the adaptabil-
ity of grid planning schemes for emerging power systems. In [7], the authors pointed out 
that the grid planning for a novel power system should adapt to the new challenges 
brought by the development of new energy sources, and more attention should be paid to 
the adaptability of diﬀerent energy types and the volatility of diﬀerent power sources. In 
[8], the authors believed that upon the interconnection of a substantial proportion of re-
newable energy sources to the grid, a comprehensive assessment of the grid planning 
scheme’s adaptability must encompass both the grid’s intrinsic properties and its interac-
tions with external factors. This constituted a vital aspect in evaluating and appraising the 
grid’s construction quality, serving as a feedback mechanism for enhancing subsequent 
construction quality and operational performance of the grid planning. 
In assessing the adaptability of distribution network planning, the technical indica-
tors for instance capacity expansion margin, power supply capacity margin, and expanda-
bility were proposed to construct an evaluation index system, and then AHP methodology 
was employed to derive the comprehensive score of the planning scheme [9]. In [8], some 
technical indicators, for instance, load ratio, current, power quality, operating life, and 
new energy utilization rate, were considered to construct an adaptability evaluation index 
system of distribution network planning schemes; entropy weight and the AHP method 
were adopted to calculate weight; then, TOPSIS was used to construct the evaluation 
model. In [10], the complexity of the grid structure after the signiﬁcant integration of re-
newable energy sources was considered, and for the planning of distribution network un-
der the big data environment, the adaptability evaluation index system was established 
by selecting technical indicators from ﬁve perspectives: grid structure, power supply ca-
pacity, equipment level, load characteristics, and grid integration of new elements; then, 
the planning scheme was evaluated employing the back propagation neural network 
(BNPP) method. On this basis, in [11], the authors considered the economic and environ-
mental beneﬁts brought about by the substantial integration of renewable energy sources 
into the grid, proposed an evaluation index system of distribution grid planning adapta-
bility, which contains equipment operation status, power supply reliability, economy, and 
environmental friendliness, and adopted a variety of empowerment methods for com-
bined empowerment; evaluation results were obtained through the AHP method. 
In assessing the adaptability of transmission grid planning, in [12], the efficiency ben-
efits of transmission grid planning scheme were considered to propose the evaluation index 
system of system scale, development, and environment. Then G1 method and GRA method 
were adopted for combination assignment, and the fuzzy comprehensive evaluation ap-
proach was employed to derive the assessment outcomes. In [13], the evaluation index sys-
tem was formulated encompassing the dimensions of economy, technology, reliability, and 
new energy acceptance capacity, and the “Over-Average Penalty” entropy weight method 
was employed to allocate weights to the indicators; then, a comprehensive evaluation 
method based on high penetration of new energy (HPNE) was proposed. Moreover, in [14], 
the impact of flexibility and vulnerability on the grid planning scheme was considered, and 
the IFAHP method was adopted for the assignment of indicators and comprehensive eval-
uation. 
In summary, the current study exhibits the following weaknesses: (1) mainly, studies 
are focused separately on the adaptability evaluation of the transmission or distribution net-
work, while few studies consider the coordination factors among all levels of a power grid, 
and the new needs generated by the grid planning for a novel power system, to construct 
the evaluation index system; (2) in the process of grid planning for novel power system, due 
to the significant uncertainty in the renewable energy power, it is necessary to fully consider 
the different attitudes of decision-makers towards risk when constructing the evaluation 
model. However, current studies generally ignore the influence of decision-making psycho-
logical factors on the evaluation results, and tend to use a single evaluation model, which 
may lead to a large limitation in the results. Thus, it is difficult to comprehensively reflect



<!-- page 3/24 -->

Energies 2024, 17, 3672 
3 of 24 
 
 
the complexity of the real decision-making environment, which may lead to bias or conflict 
in the practical application. 
Therefore, this paper introduces a methodology for assessing the adaptability of power 
grid planning schemes for a novel power system considering multiple decision psychology, 
and the key contributions of this paper are outlined as follows: 
(1) A comprehensive evaluation index system of power grid planning adaptability is es-
tablished, which comprehensively addresses the emerging requirements of grid plan-
ning for the novel power system, including economy adaptability, energy structure 
adaptability, power grid structure adaptability, reliability adaptability, and environ-
ment adaptability. 
(2) An improved cumulative prospect theory (ICPT) is introduced into the evaluation 
model to eﬀectively characterize the diﬀerent decision-making psychologies, which 
enhances the adaptability to the uncertainty of renewable energy and makes the eval-
uation results more realistic. 
(3) A combination evaluation method based on a cooperative game (CG) is constructed, 
fully contributing to the advantages of diﬀerent evaluation models to make the eval-
uation results fairer. 
The subsequent sections of this paper are structured as follows: In Section 2, the adap-
tive requirement of grid adaptive planning for novel power system are analyzed. Section 3 
describes the adaptability evaluation index system of power grid planning scheme for novel 
power system. Section 4 presents the weighting method and adaptability evaluation model 
of grid planning scheme for novel power system based on GRA-TOPSIS integrating CG and 
ICPT. Section 5 presents case studies and comparative analysis of the results. Lastly, Section 
6 concludes this study. 
2. Adaptive Requirements of Grid Planning for Novel Power System 
In the context of developing a novel power system characterized by a high integration 
of renewable energy sources, the characteristics of the power grid have undergone tremen-
dous changes: from passive network to active network, from one-way to two-way power 
flow, from pure consumption to both production and consumption, from rigid demand to 
adjustable and controllable, and from source–network coordination to source–network–
load–storage coordination [15]. Therefore, due to the transformation of the distinctive fea-
tures of the power grid, power grid planning is facing many new demands, as shown in 
Figure 1: 
Digital Transformation 
Of The Grid
Improve Economic 
Adaptability
Growth Of New 
Energy Carrying 
Capacity
Improve Adaptability 
Of Energy Structure
Load
Power
Mismatch Of Source-
Load Centers
Improve Adaptability 
Of Energy Structure
Increased Demand For 
Safe And Security 
Supply Of Electricity
Improve Reliability 
Adaptability
Dual Carbon Goals
Improve Environmental 
Adaptability
Features Of Novel 
Power System
Requirements Of 
Power Grid Planning 
 
Figure 1. Adaptive demand of grid planning for novel power system.



<!-- page 4/24 -->

Energies 2024, 17, 3672 
4 of 24 
 
 
2.1. Adaptive Requirements for Economic  
To propel the transformation and upgrading of the power system, the power grid 
needs to accelerate its digital transformation urgently. This will enable it to optimize the 
allocation of multiple factors, eﬀectively fulﬁll its platform role, and facilitate the in-depth 
development of the energy revolution [16]. In this process, the ﬁrst step in power grid 
planning is to focus on the economic aspect of each link, including sourcing, networking, 
loading, and storage. It is crucial to fully consider the impact of various power sources, 
electric vehicles, and energy storage on load forecasting. This comprehensive approach 
enhances the overall planning concept, shifting the focus from the main power grid to the 
broader power system extension. The second consideration is to anticipate the increase in 
electricity demand and load, implementing proactive planning and construction of the 
power grid. This foresighted approach ensures eﬃcient scalability and adaptability of the 
grid network. Furthermore, enhancing the deployment of intelligent terminals and im-
proving the distribution communication network are essential. These actions boost the 
observability, measurability, adjustability, and controllability of the power grid, thereby 
enhancing its internal rate of return. Ultimately, this translates into a reduction in the 
overall lifecycle expenditure of power grid development. 
2.2. Adaptive Requirements for Energy Structure  
In the novel power system, non-fossil energy sources, notably hydroelectric, wind, 
and solar power, will progressively emerge as the primary sources of installed capacity 
and electricity generation [17]. Nevertheless, China faces a persistent challenge of mis-
matched distribution between clean energy resources and demand, with water resources 
concentrated in the southwest, wind and solar resources predominantly in the “Three-
North” regions, and electricity demand heavily skewed towards the eastern, central, and 
southern regions [18]. Ultrahigh-voltage transmission emerges as a pivotal solution for 
facilitating long-distance, large-scale power transmission, thereby enhancing new energy 
integration capabilities and mitigating wind and solar curtailment issues [19]. As new en-
ergy sources integrate on a massive scale, cross-regional power transmission will inevita-
bly escalate. Consequently, power grid planning necessitates the development of ultra-
high-voltage and various levels of power grids to enhance the power grid’s capacity to 
accept new energy sources. 
2.3. Adaptive Requirements for Grid Structure  
Under the “Peak Carbon and Carbon Neutral” goal, the penetration rate of distrib-
uted power generation and the proportion of electricity to end energy consumption will 
continue to increase [20]. Emerging new loads, represented by electric vehicles, will scale 
up signiﬁcantly, leading to the normalization of the integrated production and sales 
model. As new energy sources are increasingly integrated into the power grid on a large 
scale, issues such as equipment overload and declining power quality are gradually be-
coming prominent, placing higher demands on the substation capacity. When planning 
the grid, the ﬂexible coordination between the transmission and distribution networks 
should be considered, and the potential for transformation and intelligent upgrade of grid 
construction should be enhanced at the planning stage to facilitate the harmonious inte-
gration of large-scale new energy sources with the power grid [21]. At the same time, sub-
station full stop and turn rate should be improved. When the power outage is caused by 
special circumstances, the power grid structure should respond positively enough to 
transfer the power load to other normally operating substation buses and quickly restore 
power supply. 
2.4. Adaptive Requirements for Reliability  
Considering economic globalization, the establishment of a contemporary industrial 
system is speeding up, the eco-friendly transition of conventional industries is picking up



<!-- page 5/24 -->

Energies 2024, 17, 3672 
5 of 24 
 
 
pace, and the high-tech manufacturing sector is gradually emerging as the primary cata-
lyst for progress. As people’s expectations for an improved quality of life rise, there arises 
a critical requirement for power grid design to holistically enhance the electricity supply 
quality [22]. Moreover, the substantial share of renewable energy power ﬂuctuations 
transforms the initial unidirectional random demand alteration system into a bidirectional 
random modiﬁcation system, resulting in challenges such as diminished inertia and in-
suﬃcient voltage support capabilities. To safeguard grid security and elevate power qual-
ity standards, it is imperative to augment investments in reliability during the planning 
phase. 
2.5. Adaptive Requirements for Environment  
Traditional power grid planning aims to enhance the economic eﬃciency of the sys-
tem while meeting speciﬁc stability and reliability criteria. Under the “Peak Carbon and 
Carbon Neutral” goal, power grid planning should prioritize safety and environmental 
friendliness. Building upon the existing standards for reliability and cost-eﬀectiveness, 
power grid planning must now incorporate heightened environmental protection 
measures. The focus of planning and design needs to shift from solely ensuring safety to 
achieving a balance between safety and sustainability. 
3. Construction of Evaluation Index System  
This paper adheres to the principles of scientiﬁc rigor, comprehensiveness, independ-
ence, applicability, and operability in the construction of the index system. An adaptabil-
ity evaluation index system of power grid planning scheme for novel power system is 
established by integrating the adaptive requirement of grid adaptive planning for novel 
power system. This index system encompasses ﬁve key dimensions, including economic 
adaptability, energy structure adaptability, grid structure adaptability, reliability adapta-
bility, and environment adaptability. The adaptability evaluation index system are shown 
in Table 1. 
Table 1. Adaptability evaluation index system of power grid planning scheme for novel power system. 
First-Level Indicators 
Second-Level Indicators 
Economic Adaptability (C1) 
Elasticity coeﬃcient of power production (C11) 
Investment revenue expansion ratio (C12) 
Additional load capacity per unit investment (C13) 
Additional electricity supply per unit investment (C14) 
Energy Structure Adaptability (C2) 
Proportion of clean energy (C21) 
Capacity to accommodate renewable energy (C22) 
Grid Structure Adaptability (C3) 
Substation full stop and turn rate (C31) 
Capacity ratio of transformer (C32) 
Capacity expansion margin of substation (C33) 
Remaining interval ratio (C34) 
Line capacity-to-load ratio (C35) 
Line loss rate (C36) 
Reliability Adaptability (C4) 
N-1 pass rate of power lines (C41) 
N-1 pass rate of transformers (C42) 
Voltage compliance rate (C43) 
Mean power supply reliability (C44) 
Environment Adaptability (C5) 
CO2 emission reduction (C51) 
NOX emission reduction (C52) 
SO2 emission reduction (C53)



<!-- page 6/24 -->

Energies 2024, 17, 3672 
6 of 24 
 
 
3.1. Economic Adaptability 
Economic adaptability refers to the adaptability and support capacity of a new power 
grid project to future economic development. The load growth rate of the region is directly 
aﬀected by the level of local economic development. As the load increases, the maximum 
transmission capacity of the grid will be insuﬃcient to supply the load demand. So, the 
capacity construction and economic cost of spare capacity for future development should 
be balanced in the grid planning, which enhance the grid’s ability to resist uncertainties 
in the future. Therefore, this paper proposes that secondary indicators of economic adapt-
ability include elasticity coeﬃcient of power production, investment revenue expansion 
ratio, additional load capacity per unit investment, and additional electricity supply per 
unit investment [23]. 
3.2. Energy Structure Adaptability 
In the assessment of power grid planning, energy structure adaptability constitutes 
a pivotal evaluation dimension, assessing the grid’s capacity to accommodate shifts in 
energy composition. Amid the ongoing transformation of energy mix and the prolifera-
tion of renewable energy sources, grid planning necessitates a comprehensive considera-
tion of clean energy’s share within the energy structure, along with the grid’s resilience to 
integrate new energy forms, ultimately ensuring grid stability and optimizing energy uti-
lization eﬃciency. Therefore, this paper proposes that secondary indicators of energy 
structure adaptability include the proportion of clean energy and capacity to accommo-
date renewable energy. 
3.3. Grid Structure Adaptability 
The evaluation framework for energy grid structural adaptability primarily aims to 
secure that the grid can ﬂexibly and eﬀectively respond to various load changes, resource 
allocations, and emergencies. These measures guarantee a stable supply of electricity and 
improve a power supply reliability, thereby fostering optimal resource allocation and en-
abling sustainable grid development. Therefore, this paper proposes that secondary indi-
cators of grid structure adaptability include substation full stop and turn rate, capacity 
ratio of transformer, capacity expansion margin of substation, remaining interval ratio, 
line capacity-to-load ratio, and line loss rate [24]. 
3.4. Reliability Adaptability 
In the evaluation of grid planning, reliability adaptability is essential metric for meas-
uring whether the grid system can provide power supply to customers in a continuous 
and stable manner when facing various uncertainties. The integration of large-scale re-
newable energy into the grid presents new challenges to the reliability of the grid, espe-
cially considering the randomness in both power supply and load during summer and 
winter load peaks. Therefore, this paper proposes that secondary indicators of reliability 
adaptability include the N-1 pass rate of power lines, N-1 pass rate of transformers, volt-
age compliance rate, and mean power supply reliability [8,25]. 
3.5. Environment Adaptability 
As global attention to climate change and environmental protection continues to grow, 
the power sector, as one of the major areas of energy consumption and greenhouse gas emis-
sions, bears an important responsibility for reducing environmental impacts. Considering 
environmental constraints, the impact of high-ratio renewable energy integration on miti-
gating grid-connected emissions must be assessed. This assessment is crucial for evaluating 
the planning scheme’s compatibility with impending environmental demands. Therefore, 
this paper proposes that secondary indicators of environment adaptability include CO2 
emission reduction, NOX emission reduction, and SO2 emission reduction.



<!-- page 7/24 -->

Energies 2024, 17, 3672 
7 of 24 
 
 
4. Construction of Evaluation Method Considering Multiple Decision Psychology  
4.1. Framework of the Evaluation Method 
The volatility, intermittency, and randomness in renewable energy output in a novel 
power system have a profound impact on grid planning. The risk attitude of decision-
makers directly leads to the extent to which the grid planning scheme can adapt to the 
grid-connected capacity of renewable energy in advance. Therefore, this paper considers 
the impact of multiple psychological factors of decision-makers on evaluation results and 
expands the cumulative prospect theory into an improved method that includes multiple 
risk attitudes and multiple proﬁt and loss attitudes. On this basis, in order to weaken the 
one-sidedness of the results caused by a single evaluation method, this paper combines 
the subjective and objective factors in the evaluation process and the impact of diﬀerent 
measures on the evaluation results. The evaluation results of the GRA method are more 
subjective and based on geometric similarity measures, while the evaluation results of the 
TOPSIS method are more objective and based on distance similarity. We combined these 
two methods with ICPT to build two diﬀerent evaluation models, namely, ICPT-GRA and 
ICPT-TOPSIS. Then, in order to ensure the fairness and rationality of the evaluation re-
sults, the results of the two evaluation models were scientiﬁcally coupled based on the 
ideas of CG and overall diﬀerence maximization. In addition, in order to improve the ac-
curacy of the weights, this paper considers the impact of subjective and objective factors 
on the weights and adopts an improved AHP and CRITIC indicator combination 
weighting method. Based on the above, this paper proposes an adaptability evaluation 
method of grid planning scheme for a novel power system considering multiple decision 
psychology. 
Figure 2 shows the ﬂow chart of the adaptability evaluation method of the grid plan-
ning scheme for a novel power system considering multiple decision psychology. Firstly, 
the subjective weight of the improved AHP method is obtained based on expert scores, 
the objective weight of the CRITIC method is obtained based on the original evaluation 
data, and the optimal combination weight is obtained based on the minimum deviation 
combination weighting method. Secondly, the comprehensive prospect values are calcu-
lated based on the ICPT-GRA method and the ICPT-TOPSIS method. Finally, based on 
CG and overall diﬀerence maximization, the combined weight coeﬃcient of the results of 
the two evaluation methods is obtained, and the combined comprehensive prospect value 
is calculated, which is the evaluation result. 
Combination weighting model based on improved AHP and CRITIC
Improved 
AHP method
CRITIC 
method
subjective 
weight
objective 
weight
Combination weighting model based on 
deviation minimization
Optimal combination weight
GRA-TOPSIS evaluation model integrating CG and ICPT
ICPT-GRA 
ICPT-TOPSIS
Preliminary comprehensive 
prospect value 1
Preliminary comprehensive 
prospect value 2
Combination evaluation method 
based on cooperative game
Combination evaluation method 
weight coefficient
Combined comprehensive prospect 
value
 
Figure 2. Flow chart of adaptability evaluation method of grid planning scheme for novel power 
system considering multiple decision psychology.



<!-- page 8/24 -->

Energies 2024, 17, 3672 
8 of 24 
 
 
4.2. Weighting Method Based on Improved AHP-CRITIC 
4.2.1. Subjective Weight Calculation Based on Improved AHP  
At present, AHP is a method widely used in power grid planning evaluation, and 
mostly uses a 1–9 scale to weigh the signiﬁcance between indicators to determine the 
weight value. However, in actual engineering, it is diﬃcult for decision-makers to make 
such detailed distinctions between the diﬀerences in indicators, resulting in errors; and 
when calculating weights, decisions may not be made when the judgment matrix dissat-
isﬁes the consistency check. In response to the above problems, this paper proposes a 
method by assigning a three-scale value based on the signiﬁcance of every two indicators 
to improve the judgment matrix. And by constructing a consistency matrix to omit the 
consistency check step, the calculation process is simpliﬁed, and the decision-making ef-
ﬁciency and accuracy are improved. The key steps for improvement are as follows: 
(1) Improved judgment matrix 
A three-scale evaluation method on the basis of the importance of elements is intro-
duced in this paper, categorized as signiﬁcant, equally signiﬁcant, and insigniﬁcant. This 
approach requires only the comparison of whether elements are important, without the 
need to compare their relative importance. This makes for a more intuitive matrix con-
struction, omitting the step of the consistency test of judgment matrix, and eventually 
simplifying subsequent calculations. Additionally, it becomes easier to determine the de-
gree of importance between indicators. The speciﬁc steps of matrix construction are as 
follows: 
(a) Experts select the importance of each indicator; 
(b) Based on the opinions of experts, a judgment matrix 
(
)
ij
n n
A
a
×
=
 is formed, with the 
following parameters: 
 
1,
0,
 
 
 
 
e
1,
   
 
 
  
  
   
  
 
 
  
ij
Element j is less significa
e
nt than i
a
The significance of
i and j is same
Element j is mor
n
l men
e significa t than i
t


= 
−
 
(1)
where 
ij
a  represents the value obtained from comparing the element i  with the ele-
ment j . When i
j
=
, it is stipulated that holds the same level of importance when com-
pared to itself, that is, 
0
iia =
. 
ii
a  is the comparison of the element itself. When i
j
≠
, 
the element j  is less signiﬁcant than the element i  and the value is assigned as 1, oth-
erwise as −1.  
(2) Improve matrix consistency 
One approach to determine the signiﬁcance of each element in AHP is through the 
empirical method, but because people’s understanding of things is subjective, it may fail 
to capture objective facts accurately. Traditional AHP requires consistency testing of the 
judgment matrix because of discontinuity in expert judgment on multi-indicator. If it is 
inconsistent, mathematical methods need to be used to adjust it, thereby increasing the 
computational complexity of the problem. However, if a consistent matrix can be con-
structed from the start, the consistency test can be omitted, allowing for the matrix to in-
herently satisfy the consistency requirements and thus simplifying the process of matrix 
calculation. 
(3) Construct an antisymmetric matrix 
Let there be n -order real matrices 
ij
n n
A
a
×


= 

 and 
ij
n n
B
b
×


= 

, where 
1,2,
, ;
i
n
=

1,2,
,
j
n
=

. 
Deﬁnition 1. For a real matrix A  , if 
1,2,
,
j
n
=

 , and there is always 
ij
ji
a
a
= −
 , then it is 
called an antisymmetric matrix A .



<!-- page 9/24 -->

Energies 2024, 17, 3672 
9 of 24 
 
 
Based on Equation (1) and incorporating expert opinions, the judgment matrices A
is constructed. From deﬁnition 1, it can be seen that the matrix A  must be an antisym-
metric matrix, and the size of the matrix varies according to the number of indicators. 
11
12
1
1
21
22
2
2
1
1
2
j
n
j
n
i
i
ij
in
n
n
ij
nn
a
a
a
a
a
a
a
a
A
a
a
a
a
a
a
a
a








= 



























 
(2)
(4) Solve the optimal transfer matrix 
Deﬁnition 2. If the antisymmetric matrix A  satisﬁes 
ij
ik
kj
a
a
a
=
+
, then the matrix A  must 
be a transfer matrix. If matrix A  is a transfer matrix, it is necessary to fulﬁll the above condition 
for all k  less than or equal to the dimension of matrix. Among them, 
ik
a  a is the element in i
th row and k th column of matrix A , and 
kj
a  is the element in k th row and j k th column of 
matrix A . 
Deﬁnition 3. For transfer matrix 
A  , if B   is the optimal transfer matrix of 
A  , then 
(
)
1
1
n
n
ij
ij
i
j
b
a
=
=
∑∑
−
 must obtain the minimum value, where 
ijb  is the element in row i th row and 
column j th column of the transfer matrix B . 
Theorem 1. If A  is an antisymmetric matrix, then the optimal transfer matrix B  satisﬁes the 
following: 
(
)
1
1
n
ij
ik
jk
k
b
a
a
n
=
=
∑
−
 
(3)
Reasoning 1. Because of the property of antisymmetric matrix A , the optimal transfer matrix B  
must satisfy the following: 
(
)
1
1
n
ij
ik
kj
k
b
a
a
n
=
=
∑
+
 
(4)
From Theorem 1 or Reasoning 1, the optimal transfer matrix of B can be obtained: 
11
12
1
1
21
22
2
2
1
2
1
2
j
n
j
n
i
i
ij
in
n
n
ij
nn
b
b
b
b
b
b
b
b
B
b
b
b
b
b
b
b
b








= 



























 
(5)
where 
(
)
(
)
1
1
1
1
n
n
ij
ik
jk
ik
kj
k
k
b
a
a
a
a
n
n
=
=
=
∑
−
=
∑
+
. 
(5) Solve the consistency matrix 
Deﬁnition 4. For matrix A , if 
, ,
i j k
N
∀
∈
, there is 
ik
kj
ij
a a
a
=
, which is called a completely 
consistent matrix A .



<!-- page 10/24 -->

Energies 2024, 17, 3672 
10 of 24 
 
 
Reasoning 2. For the antisymmetric matrix A , if matrix B  is an optimal transfer matrix of A , 
when 
*
B
A
e
=
, 
*
A  is a completely consistent matrix of A . 
It can be derived from Theorem 2 that the matrix B  can be converted into a com-
pletely consistent matrix 
*
A . 
11
12
1
1
21
22
2
2
*
1
2
1
2
j
n
j
n
i
i
ij
in
n
n
ij
nn
a
a
a
a
a
a
a
a
A
a
a
a
a
a
a
a
a
∗
∗
∗
∗
∗
∗
∗
∗
∗
∗
∗
∗
∗
∗
∗








= 



























 
(6)
where 
*
ij
a
 is the element in i th row and j th column of 
*
A , 
(
)
exp
ij
ij
a
b
∗=
. 
*
A  is the 
completely consistency matrix of A , which satisﬁes consistency requirements and guar-
antees the information of A  to the maximum extent.  
(6) Calculate the weight value 
The weight value of indicators signiﬁes the signiﬁcance of elements in this layer rel-
ative to the previous layer. Determining these values can be simpliﬁed to computing the 
principal eigenvalues and eigenvectors of the matrix. The eigenvectors of the consistency 
matrix 
*
A , which corresponds to the eigen roots, must satisfy 
*
A W
W
λ
=
. In this equa-
tion, 
*
A  is the eigenvector; λ  is the eigen root. This paper identiﬁes the eigenvectors 
associated with the largest eigenvalues through the method of the square root, and the 
speciﬁc steps are as follow:  
(a) The n th root of the product for the elements in each row of 
*
A  are calculated. 
1
,
1,2,
, ;
1,2,
,
n
n
i
ij
j
W
a
i
n j
n
∗
=
=
∏
=
=


 
(7)
where 
i
W  is the n th root of the product of the elements of the i  row. 
(b) The values of the elements of each row are processed to the n th power and recorded 
as vectors 
T
1
2
,
,
,
n
W
W W
W


= 


 
(8)
(c) 
Through the step of normalizing W , the weight obtained: 
1
i
i
n
j
j
W
W
W
=
=
∑
 
(9)
where 
j
W  is for the elements of the j th column of the n th root of the product  
[
]
T
1
2
,
,
,
n
W
W W
W
=

 
(10)
W  in Equation (10) is the eigenvector which is corresponding to the maximum eigen-
value λ , that is, the eventual weight value. 
4.2.2. Objective Weight Calculation Based on CRITIC  
This paper uses the CRITIC method to calculate the objective weight of indicators 
based on the amount of information in the indicator data [26]. When weights are deter-
mined by this method, not only is the amount of information contained in the indicator 
considered, but the contrast and the conﬂict between diﬀerent solutions and indicators 
are also regarded. Therefore, the results are more objective and reasonable.



<!-- page 11/24 -->

Energies 2024, 17, 3672 
11 of 24 
 
 
4.2.3. Combination Weight Calculation Based on Deviation Minimization 
Using a single method of subjective empowerment or objective empowerment will 
lead to diﬀerences and defects in evaluation results. The objective function aims to mini-
mize the sum of the squares of the diﬀerences between “the deviation between the im-
proved AHP weight and the combination weight” and “the CRITIC weight and the devi-
ation between the combination weight”. The combination weight and the subjective and 
objective weights are solved, respectively, when the sum of squares of deviations is mini-
mized and the optimal combined weight result is solved, in which the minimization prob-
lem is solved with respect to the variable β . 
(
)
(
)
2
2
1
min
m
i
i
i
i
i
z
u
W
u
V
=


= ∑
−
+
−

 
(11)
i
i
(1
)
i
u
W
V
β
β
=
+
−
 
(12)
Among them, 
iu  is the comprehensive weight of the i th indicator after combining 
the two weighting methods that are represented as a linear combination of 
i
W  and 
iV ; 
β  is the proportion of the subjective preference coeﬃcient weight in the combination 
weight; 
i
W  is the improved analytic hierarchy process weight of the i th indicator; 1
β
−
 
is the proportion of the objective preference coeﬃcient in the combination weight; and 
iV
is the CRITIC weight of the i th indicator. 
4.3. Adaptability Evaluation Model Based on GRA-TOPSIS Integrating CG and ICPT 
4.3.1. ICPT Method 
Cumulative prospect theory focuses on the irrational behavior of decision-makers 
and reﬂects bounded rational behavior by establishing a value function. However, the ex-
isting value function does not distinguish the risk preference type and proﬁt and loss at-
titude of decision-makers [27]. This paper expands the value range of the decision-making 
risk preference coeﬃcient; proposes an improved prospect value function for three risk 
attitudes, radical, balanced, and cautious; and adds parameters δ  to adjust the decision-
maker’s outlook proﬁt and loss attitude [28]. The details are as follows: 
(
)
(Δ ) ,Δ
0
( Δ ) ,Δ
0
x
x
v
x
x
x
α
β
δ
θ

∆
= −
−
<


 
(13)
where 
(
)
Δ
v
x  is the prospect value; Δx  is the diﬀerence between the evaluation plan 
value and the reference plan value −1~1, which is the value under standard circumstances. 
If Δ
0
x, then the prospect value is the income value Δ
0
x; otherwise, it is the loss value 
v−; α
β
、
 are the parameters of risk attitude from diﬀerent decision-maker; δ  is the 
decision-maker’s sensitivity coeﬃcient to returns; θ  is the sensitivity coeﬃcient of the 
decision-maker to the loss. 
The improved traditional prospect theory is shown in Figure 3. The value range of 
α
β
、
 is expanded and decision-makers are divided into three types. If 0
,
1
α β
<
< , then 
the decision-maker is a radical type; if 
,
1
α β = , then the decision-maker is a balanced 
type; if 
,
1
α β > , then the decision-maker is a cautious type. Traditional prospect theory 
is only a cautious decision-making model. 
A new prospect value function parameter δ  is added to adjust the decision-maker’s 
attitude towards proﬁt and loss. If the decision-maker is more sensitive to prospect losses 
than to prospect losses, then let 
1
δ
θ
>
= ; if the decision-maker is more sensitive to pro-
spective losses than to prospective gains, then 
1
θ
δ
>
= ; if the decision-maker is equally 
sensitive to prospective gains and losses, then make 
1
θ
δ
=
= .



<!-- page 12/24 -->

Energies 2024, 17, 3672 
12 of 24 
 
 
Based on the improved prospect value function and using the cumulative functional 
to optimize the decision weight, the comprehensive prospect value of ICPT can be ob-
tained: 
(
)
(
)
1
1
n
n
j
ij
i
ij
i
i
i
V
v
v
π
ω
π
ω
+
+
−
−
=
=
=
+
∑
∑
 
(14)
where 
j
V  is the comprehensive prospect value of the j  th plan; 
ij
ij
v
v
+
−
、
 are, respec-
tively, the positive and negative prospect values of the i th plan under the j th indicator; 
(
)
i
π
ω
+
, 
(
)
i
π
ω
−
 are, respectively, the decision weight functions of the positive and neg-
ative prospect values corresponding to the i  th indicator weight 
i
ω  ; 
1,2,
, ,
i
n
=
…
1,2,
,
j
m
=
…
. The decision weight function is as below: 
(
)
(
)
(
)
(
)
1
1
1
1
i
i
i
i
i
i
i
i
γ
γ
γ
γ
γ
γ
γ
γ
ω
π
ω
ω
ω
ω
π
ω
ω
ω
+
+
+
+
−
−
−
−
+
−

=




+
−








=




+
−






 
(15)
where γ
γ
+
−
、
 are the ﬁtting parameters; usually, the values are 
0.61,
0.69
γ
γ
+
−
=
=
 
[29]. 
Balancer
Radical
Cautious
v(x)
Δx
 
Figure 3. Improved prospect value function. 
4.3.2. ICPT-GRA Method 
The GRA method determines the closeness based on the geometric similarity be-
tween the comparison sequence curve and the reference sequence curve. The greater the 
gray correlation degree, the closer the comparison sequence is to the reference sequence 
[30]. According to the standardized evaluation matrix, the positive and negative ideal 
schemes are established as reference schemes, and the Dun’s gray correlation coeﬃcient 
between each evaluation scheme and the positive and negative ideal schemes under each 
evaluation index is calculated [31]. 
The gray correlation coeﬃcient 
 
ij
ξ
 between the reference plan sequence 
'
0x  and 
the plan sequence 
'
jx  to be evaluated with respect to the i th indicator is as follows: 
0
0
0
0
0
min min |
|
max max |
|
|
|
max min
|
|
j
i
i
ij
i
i
ij
ij
i
ij
i
i
i
ij
x
x
x
x
x
x
x x
x
ρ
ξ
ρ
′
′
′
′
′
′
′
′
−
+
−
−
=
−
+
 
(16)



<!-- page 13/24 -->

Energies 2024, 17, 3672 
13 of 24 
 
 
where 
'
'
0
ij
i
x
x
、
 are the evaluation values of the index 
'
'
0
jx
x
、
, respectively; ρ  is the res-
olution coeﬃcient, which generally takes the value 0.5 [32]. 
Any evaluation plan should be a gain compared with the negative ideal plan, so its 
prospect value should be a positive number; similarly, any evaluation plan should be a 
loss compared with the positive ideal plan, so its prospect value should be a negative 
number. 
The prospect value function of the ICPT-GRA method takes the positive ideal solu-
tion as a reference: 
{
}
1
1
1
 
 
 
 
 
  
1
 
 
 
 
 
  
.
ij
ij
ij
ij
v
Take the negative ideal solution as a reference
v
Take the positive ideal solution as a reference
α
β
δ
ξ
θ
ξ
+
−
−
+



=
⋅
−






= −⋅−
−



,
；
,
 
(17)
where 
ij
ij
ξ
ξ
+
−
、
 are the coeﬃcients of gray correlation for the i th plan and the positive 
and negative ideal plans under the j th index, respectively; 
1ij
v
+  is the positive prospect 
value of the j th plan and the negative ideal plan with respect to the i th index; 
1ij
v
− is 
the positive prospect value of the j th plan and the positive ideal plan with respect to the 
i th index negative prospect value. Combining Equation (14), we can obtain the compre-
hensive prospect value 
1 j
V  of the ﬁrst solution using the ICPT-GRA method (the ﬁrst 
evaluation method in this paper). 
4.3.3. ICPT-TOPSIS Method 
The basic idea of the TOPSIS method is to use Euclidean distance to measure the 
distance between the evaluation object and the positive and negative ideal solutions [33]. 
As shown in Table 1, there is a correlation between the secondary indicators in environ-
ment adaptability. If calculated using the Euclidean TOPSIS method, it will lead to biased 
ranking results. Mahalanobis distance can eliminate the impact of indicator correlation, 
but it requires that the number of evaluation objects must be greater than the number of 
indicators, so it is not suitable for power grid planning adaptability evaluation, while co-
sine similarity (CS) is not interfered with by the correlation of indicators, and there is no 
requirement for the relationship between the number of indicators and the number of 
evaluation objects [34]. Therefore, this paper uses cosine similarity as the ranging algo-
rithm of the TOPSIS method. 
(
)
(
)
'
'
2
i min
'
'
2
max
 
 
 
 
 
  
 
 
 
 
 
 
,
 
ij
ij
ij
ij
i
v
x
x
Take the negative ideal solution as a reference
v
x
x
Take the postive ideal solution as a reference
α
β
δ
θ
+
−

=
⋅
−




= −⋅−
−



；
；
，
 
(18)
(
)
(
)
2
2
2
ij
ij
i
ij
i
v
v
v
π
ω
π
ω
+
+
−
−
=
⋅
+
⋅
 
(19)
where 
2ij
v+  is the positive prospect value of the j th plan and the negative ideal plan with 
respect to the i th index; 
2ij
v− is the negative prospect value of the j th plan and the pos-
itive ideal plan with respect to the i th index; 
'
min
ix
, 
'
max
ix
are, respectively, the negative 
and positive ideal plans in the standard evaluation matrix index value; 
2ij
v
 is the com-
prehensive prospect value of the j th plan with regard to the i th index. The comprehen-
sive prospect matrix is 
(
)
(
)
2
2
ij
j
n m
m
V
v
v
×
=
=
.



<!-- page 14/24 -->

Energies 2024, 17, 3672 
14 of 24 
 
 
(
)
2
2
1
2
2
2
2
2
2
1
1
sim
,
cos
(
)
(
)
n
ia
ib
i
a
b
ab
n
n
ia
ib
i
i
v
v
v
v
v
v
θ
=
=
=
⋅
=
=
⋅
∑
∑
∑
 
(20)
2
2max
2min
0.5(
)
avg
v
v
v
=
+
 
(21)
2
2
2max
2
2
2max
1
2
2
2
2min
2
2
2min
1
2
sin(
,
)
1
(
,
)
log (
)
2
sin(
,
)
1
(
,
)
log (
)
2
j
avg
avg
j
j
avg
avg
j
v
v
v
v
d v
v
v
v
v
v
d v
v




−
−
+
=
+
=

−
−
 
(22)
(
)
(
)
(
)
2
2min
2
2
2min
2
2max
,
,
,
j
j
j
j
d v
v
V
d v
v
d v
v
=
+
 
(23)
where 
2 j
v
 is the comprehensive prospect column vector of the j th plan; 
2max
v
, 
2min
v
 
are the comprehensive prospect column vectors of the positive and negative ideal plans, 
respectively; 
2 j
V
 is the comprehensive prospect value of the j th ICPT-TOPSIS method 
(the second evaluation method in this paper). 
4.3.4. Integrating CG and ICPT GRA-TOPSIS Method 
Using the TOPSIS method to evaluate the adaptability of power grid planning 
schemes, if the evaluation index data are limited, it may lead to large errors in the evalu-
ation results [35]. The GRA method is suitable for comprehensive evaluation in gray en-
vironments with incomplete information [36]. The evaluation results of the TOPSIS 
method are more objective, while the GRA method has the subjective color of dividing the 
optimal value of the gray index; the TOPSIS method is based on distance measurement, 
while the GRA method is based on geometric similarity [37]. In view of the advantages 
and disadvantages of the TOPSIS method and the GRA method, this article adopts the 
combined evaluation method of ICPT-GRA and ICPT-TOPSIS (ICPT-GRA-TOPSIS 
method). In order to determine the combined evaluation coeﬃcient, this paper uses the 
CG method, which has a relatively small total system error. However, the feasibility of 
using the average value as the benchmark value of this method needs further study, and 
it is not suitable for the combination of two evaluation methods. The combination coeﬃ-
cient has no solution [38]. Therefore, this paper improves the CG combination evaluation 
method, uses variance maximization as a measurement standard, and constructs an inte-
grated CG and ICPT GRA-TOPSIS combination evaluation model and overall diﬀerence 
maximization to solve the problem of artiﬁcial setting of benchmark values, the limited 
number of combination evaluation methods, and other issues. 
The comprehensive prospect values obtained by the ICPT-GRA method and the 
ICPT-TOPSIS method are standardized as follows: 
min
*
max
min
kj
k
kj
k
k
V
V
V
V
V
−
=
−
 
(24)
*
*
kj
k
kj
k
V
V
e
s
−
=
 
(25)



<!-- page 15/24 -->

Energies 2024, 17, 3672 
15 of 24 
 
 
(
)
*
*
1
2
*
*
1
1
1
1
m
k
kj
j
m
k
kj
k
j
V
V
m
s
V
V
m
=
=

=



=
−

−

∑
∑
 
(26)
where 
kj
V  is the comprehensive prospect value of the k th evaluation method for the j
th plan; 
min
k
V
, 
max
k
V
 are, respectively, the minimum and maximum comprehensive pro-
spect values of the k th evaluation method; 
*
kj
V , 
kj
V  are the standardized processing re-
sults; 
*
k
V , 
ks  are the average values of all plans of the k th evaluation method’s standard 
deviations, respectively. 
(
)
T
T
T
maxJ
LHL
L ee
L
=
=
 
(27)
where 
[
]
(
)
1 2
1
2
,
1,
0
1,2
k
L
l l
l
l
l
k
=
+
=
>
=
 ; H  is the variance information matrix of the 
combined evaluation model; 
(
)2
kj
m
e
e
×
=
. 
Let 
{
}
( )
1,2,
,
,
,
G
g
f
G u f
=
…
⊂
 be a real-valued function deﬁned on the set 2G  , 
and let 
( )
( )
u f
J
f
=
.  
( )
( )
{ }
(
)
1
0
g
k
u
u G
u
k
φ
=
=



∑

 
(28)
If 
( )
u f
 satisﬁes the above conditions, it is called the characteristic function of the 
cooperative game [
]
,
G u , where 
( )
J
f
 is the variance information matrix of the alliance 
f  for combined evaluation. 
( )
{ }
(
|
|)!(|
| 1)!
( )
(
)
!
k
f
g
f
f
u
u f
u f
k
g
ϕ
−
−
=
−
−




∑
 
(29)
k
ϕ  is the Shapely value, which represents the average contribution of the k th eval-
uation method in the cooperative game. After normalizing the obtained Shapely values, 
the combined evaluation weight coeﬃcient determined by the cooperative exchange is as 
follows: 
( )
( )
( )
( )
1
/
g
k
k
k
k
u
u
l
u G
u G
ϕ
ϕ
=
=
∑
 
(30)
5. Example Analysis 
5.1. Basic Data and Standardized Processing 
In this paper, grid planning schemes from three regions encompassed by China’s 
14th Five-Year Plan are designated as the evaluation subjects. The adaptability evaluation 
model of grid planning scheme for novel power system based on GRA-TOPSIS integrating 
CG and ICPT is applied to assess the degree of adaptability and identify the limitations 
inherent in each regional grid planning scheme. 
The region-speciﬁc data were transformed into isotropic indicators, which were then 
converted to positive indicators and rendered dimensionless prior to presentation in Table 
2.



<!-- page 16/24 -->

Energies 2024, 17, 3672 
16 of 24 
 
 
Table 2. Standardized data. 
Indicators 
Region 1 
Region 2 
Region 3 
C11 
0.6200 
0.6000 
0.9800 
C12 
0.8627 
0.8013 
0.8480 
C13 
0.8460 
0.5331 
0.7840 
C14 
0.7578 
0.6525 
0.8867 
C21 
0.6421 
0.5262 
0.5575 
C22 
0.5846 
0.6048 
0.5408 
C31 
0.7541 
0.8230 
0.6997 
C32 
0.4710 
0.9058 
0.7609 
C33 
1.0000 
0.6750 
0.9300 
C34 
1.0000 
0.9555 
1.0000 
C35 
0.8036 
0.8794 
0.7851 
C36 
0.6584 
0.6569 
0.6996 
C41 
0.9000 
1.0000 
0.8300 
C42 
0.7456 
0.6616 
0.7144 
C43 
0.7546 
0.8750 
0.8449 
C44 
0.9709 
0.7750 
0.9340 
C51 
0.6121 
0.5538 
0.5645 
C52 
0.6411 
0.6554 
0.3992 
C53 
0.5839 
0.5209 
0.6227 
5.2. Weighting of Indicators  
Using the improved AHP method, expert opinions are collected and scores for each 
indicators are obtained according to Equations (1)–(10); the average value is taken as sub-
jective weights W = (0.0672, 0.037, 0.0579, 0.0774, 0.0761, 0.0525, 0.0395, 0.0903, 0.0168, 
0.0254, 0.054, 0.0373, 0.084, 0.0703, 0.0782, 0.0821, 0.0301, 0.0117, 0.0122)T. Meanwhile, we 
used the RANCOM method [39], which takes into account the inaccuracy of expert judg-
ment, to calculate the value of indicator weights as W′ = (0.0654, 0.0354, 0.0498, 0.0787, 
0.0759, 0.0498, 0.0327, 0.1057, 0.0215, 0.0265, 0.0504, 0.0363, 0.0873, 0.0669, 0.0683, 0.0928, 
0.0239, 0.0193, 0.0134)T, where the diﬀerence in weight under the two methods is minimal 
and the results are consistent. 
The CRITIC method was employed to compute the index information quantity and 
corresponding objective weights, with the outcomes presented in Table 3. 
Table 4 displays the comprehensive weights of each indicator, derived from the inte-
gration of subjective and objective weights. Notably, reliability and grid structure exhibit 
a heightened inﬂuence in assessing grid planning adaptability, particularly through indi-
cators like N-1 pass rate of power lines and mean power supply reliability, which are in-
timately tied to this metric. Conversely, environmental adaptability demonstrates a lesser 
impact. 
Table 3. Objective weights. 
Evaluation Indicators 
i
G  
iV  
Evaluation Indicators 
i
G  
iV  
C11 
0.8402  
0.0498  
C35 
1.3243  
0.0785  
C12 
0.6686  
0.0397  
C36 
0.8448  
0.0501  
C13 
0.6666  
0.0395  
C41 
1.2951  
0.0768  
C14 
0.7340  
0.0435  
C42 
0.6796  
0.0403  
C21 
0.7453  
0.0442  
C43 
1.2499  
0.0741  
C22 
1.2320  
0.0731  
C44 
0.6662  
0.0395  
C31 
0.6853  
0.0406  
C51 
0.7662  
0.0454  
C32 
1.2692  
0.0753  
C52 
1.1607  
0.0688  
C33 
0.6674  
0.0396  
C53 
0.6995  
0.0415  
C34 
0.6653  
0.0395



<!-- page 17/24 -->

Energies 2024, 17, 3672 
17 of 24 
 
 
Table 4. Combined weights. 
First-Level Indicators 
Combined Weights 
Second-Level Indicators Combined Weights 
C1 
0.1969 
C11 
0.0601 
C12 
0.0383 
C13 
0.0476 
C14 
0.0509 
C2 
0.1210 
C21 
0.0492 
C22 
0.0718 
C3 
0.2936 
C31 
0.0388 
C32 
0.0873 
C33 
0.0364 
C34 
0.0341 
C35 
0.0548 
C36 
0.0422 
C4 
0.03065 
C41 
0.0825 
C42 
0.0672 
C43 
0.0764 
C44 
0.0804 
C5 
0.07940 
C51 
0.0315 
C52 
0.0235 
C53 
0.0244 
5.3. Adaptability Evaluation of Grid Planning Scheme for Novel Power System Based on GRA-
TOPSIS Integrating CG and ICPT 
5.3.1. Evaluating Based on ICPT-GRA 
Using the geometric similarity of the GRA method, the grey correlation coeﬃcient 
between the planning scheme and the positive and negative ideal schemes is separately 
calculated. To investigate the inﬂuence of the limited psychological behaviors of the deci-
sion-makers in grid scheduling on the evaluation results, the ICPT-GRA method, which 
takes into account the psychology of decision-making, introduces the cumulative prospect 
theory on the basis of the grey correlation coeﬃcient, and the comprehensive prospect 
value of each evaluation scheme is calculated. The ﬁnal evaluation scores and ranking 
results of each scheme, as shown in Table 5. This section takes the more radical loss-sen-
sitive psychological evaluation of decision-makers as an example for analysis. It is con-
sistent with the most conservative mindset held by grid planning decision-makers to en-
sure reliable and safe operation of the system, for which 
1,
1,
2.25
α
β
δ
θ
=
=
=
=
. 
Table 5. Overall scores and ranking results in ICPT-GRA method. 
Sample 
Positive Ideal Solu-
tion Distance 
Negative Ideal So-
lution Distance 
Comprehensive 
Prospect Value of 
ICPT-GRA  
Ranking Results in 
ICPT-GRA  
Region 1 
0.6555 
0.5990 
1.7874 
1 
Region 2 
0.5998 
0.6037 
0.5395 
3 
Region 3 
0.6312 
0.5659 
1.6623 
2 
5.3.2. Evaluating Based on ICPT-TOPSIS 
According to the TOPSIS method, the Euclidean distance between the decision ma-
trix and the positive and negative ideal schemes is separately acquired. Combined with 
the cumulative prospect theory, the ICPT-TOPSIS method considering the decision psy-
chology applies cosine similarity to obtain the comprehensive prospect value of each in-
dex of the schemes, as shown in Table 6.



<!-- page 18/24 -->

Energies 2024, 17, 3672 
18 of 24 
 
 
Table 6. Overall scores and ranking results in ICPT-TOPSIS method. 
Sample 
Positive Ideal Solu-
tion Distance 
Negative Ideal So-
lution Distance 
Comprehensive 
Prospect Value of 
ICPT-TOPSIS  
Ranking Results in 
ICPT-TOPSIS  
Region 1 
0.6138 
0.6873 
0.33364 
2 
Region 2 
0.46540. 
0.5548 
0.1974 
3 
Region 3 
0.6973 
0.4213 
0.4064 
1 
5.3.3. Combination Evaluation Based on CG 
Considering the advantages and disadvantages of the ICPT-GRA and ICPT-TOPSIS 
evaluation methods, their combined prospective values are normalized to obtain the var-
iance information matrix. Based on the variance maximization principle, the optimal 
weights for the combined evaluation methods are derived by calculating the shapely val-
ues of individual evaluation techniques. Combined with the results of the improved com-
bination assignment, the comprehensive evaluation scores and ranking results of GRA-
TOPSIS integrating CG and ICPT methods are shown in the Table 7. 
Table 7. Overall scores and ranking results in GRA-TOPSIS integrating CG and ICPT method. 
Sample 
Comprehensive Prospect Value of GRA-
TOPSIS Integrating CG and ICPT Method  
Ranking Results in GRA-TOPSIS Inte-
grating CG and ICPT Method 
Region 1 
0.9879 
1 
Region 2 
0.2983 
3 
Region 3 
0.9100 
2 
Comparison of the results in Tables 5–7 reveals that the combination evaluation not 
only evaluates the optimal scheme explicitly from the overall dimension, but also widens 
the gap between diﬀerent schemes, which makes up for the shortcomings of a single eval-
uation method. Figure 4 shows the comprehensive evaluation results of ICPT-GRA, ICPT-
TOPSIS, and GRA-TOPSIS integrating CG and ICPT. Figures 5 and 6 show the ﬁrst-level 
indicator scores for each scheme under the ICPT-GRA and ICPT-TOPSIS methods. Alt-
hough both evaluation methods are based on the relative distances of positive and nega-
tive ideal scenarios, there are large diﬀerences in their overall scenario and ﬁrst-level in-
dicator scores. As can be seen from Figures 2 and 3, the scores for each ﬁrst-level indicator 
under the ICPT-GRA method of evaluation are relatively balanced, while the ICPT-TOP-
SIS method makes a more signiﬁcant distinction between the strengths and weaknesses 
of the ﬁrst-level indicators. For Region 1, economic adaptability and adaptability of grid 
structure are evaluated poorly in the ICPT-GRA method, but they are signiﬁcantly worse 
in the ICPT-TOPSIS method. That is, when evaluating the overall scenario, the ICPT-TOP-
SIS method highlights the worse structures in the scenario, while the ICPT-GRA method 
can distinguish the better overall scenario more intuitively. The evaluation approach that 
incorporates the combination of CG assigns weights based on the marginal contribution 
of each evaluation method, thereby addressing the limitations of single-method evalua-
tions and quantitatively fusing the outcomes from two individual evaluation techniques. 
Combined with the results of the scenarios in Table 3, it can be seen that Region 1 has 
the highest overall rating, Region 3 occupies second place, and Region 2 is the worst. The 
safe and reliable operation of the grid is the prerequisite for evaluating the adaptability of 
the grid planning scheme, which has the largest weight, as high as 0.3065. Among them, 
the two indicators of mean power supply reliability and N-1 pass rate of power lines de-
termine the safety and reliability of the grid, the combined weight of two accounting for 
more than 53.15%. The strengths of Region 1 in terms of reliability adaptability, in partic-
ular the mean power supply reliability and N-1 pass rate of lines, make its overall score 
stand out among the three scenarios. Region 1 has signiﬁcant advantages in terms of 
adaptability of energy structure, reliability adaptability, and environmental adaptability.



<!-- page 19/24 -->

Energies 2024, 17, 3672 
19 of 24 
 
 
This region is equipped with a certain scale of installed renewable energy capacity and 
realizes the transfer of power resources in time through large-capacity energy storage to 
ensure the controllability of grid ﬂuctuations, so that the proportion of clean energy and 
the mean reliability of power supply are increased by 18.78% and 30.17%, respectively. 
Compared with other regions, the signiﬁcant increase in the proportion of its clean energy 
makes the environmental adaptability of the region better than that of other regions. At 
the same time, limited by the scale of renewable energy installed capacity and line capac-
ity ratio, the ability to increase load and power supply by subsequent unit investment is 
insuﬃcient in Region 1. The planning scheme of Region 2 has the largest transformer ca-
pacity–load ratio and large available capacity, which is more conducive to the access of a 
high proportion of new energy sources. Despite the capacity to integrate new energy 
sources, there is a mismatch between the scale of renewable energy sources and the grid 
structure planning, resulting in grid line redundancy. The ineﬃciency can lead to in-
creased operational costs and underutilized infrastructure. The primary cause is the lack 
of synchronization between renewable energy development and grid planning, leading to 
oversupply in certain grid lines and insuﬃcient supply in others. Region 3 focuses on 
wind power, due to the large diﬀerences in the seasonal distribution of wind resources, 
resulting in the overall power supply of the project being overly dependent on the gener-
ation of traditional thermal power units. This reliance on thermal power is primarily due 
to the intermittent nature of wind energy and the lack of suﬃcient storage or backup re-
newable sources to compensate for periods of low wind availability. The eﬃcient use of 
existing thermal power plants and strategic deployment of renewable resources make it 
outstanding in terms of economic adaptability and grid structure adaptability, and rela-
tively balanced power supply reliability capacity. 
Region 1
Region 2
Region 3
0
0.2
0.4
0.6
0.8
1
Value
ICPT-GRA
ICPT-TOPSIS
GRA-TOPSIS 
Integrating CG 
and ICPT
 
Figure 4. Comparison of the assessment results of 3 evaluation methods. 
 
Figure 5. The scores of the ﬁrst-level indicators in ICPT-GRA.



<!-- page 20/24 -->

Energies 2024, 17, 3672 
20 of 24 
 
 
 
Figure 6. The scores of the ﬁrst-level indicators in ICPT-TOPSIS. 
Considering the limited psychological behavior of the planning decision-makers, the 
results of the evaluation of the ﬁst and secondary indicators under the planning scenarios 
for the three districts based on the ICPT-GRA-TOPSIS methodology are shown in Figures 
7 and 8. 
 
Figure 7. The scores of the ﬁrst-level indicators in GRA-TOPSIS integrating CG and ICPT. 
 
Figure 8. The scores of the second-level indicators in GRA-TOPSIS integrating CG and ICPT. 
5.4. Sensitivity Analysis Based on Multiple Psychology of Decision-Maker on the Evaluation of 
Planning Schemes 
In this paper, decision-making psychology is taken as a sensitive factor that is intro-
duced into the GRA-TOPSIS integrating CG and ICPT method combined evaluation 
model for the adaptive evaluation of grid planning schemes. The personalities of diﬀerent 
decision-makers are classiﬁed as radical, balanced, or cautious based on the improved 
cumulative prospect theory. Combining these three psychological behaviors as well as 
proﬁt–loss attitudes to explore their inﬂuence on the comprehensive evaluation and



<!-- page 21/24 -->

Energies 2024, 17, 3672 
21 of 24 
 
 
ranking results of regional planning schemes, the constructed six combinations of psycho-
logical parameters for grid planning decision-making are shown in Table 8, Figure 9 
shows the results of the comprehensive rating evaluation of the six combinations, and 
Figure 10 shows the results of the evaluation of the ﬁrst-level indicators under multiple 
psychology in the case of Region 1. 
Table 8. Combination of mental parameters for decision-makers. 
Sequence 
α  
β  
δ  
θ  
Risk Attitudes of De-
cision-Maker  
Proﬁt–Loss Attitude 
of Decision-Maker 
1 
0.4 
0.4 
1 
2.25 
Radical 
Loss-sensitive 
2 
1 
1 
1 
2.25 
Balanced 
3 
1.9 
1.9 
1 
2.25 
Cautious 
4 
0.4 
0.4 
2.25 
1 
Radical 
Proﬁt-sensitive 
5 
1 
1 
2.25 
1 
Balanced 
6 
1.9 
1.9 
2.25 
1 
Cautious 
From the Figure 9, it can be seen that in the case of the decision-maker having the 
same proﬁt–loss attitude, the three diﬀerent decision-making mindsets of radical, bal-
anced, and cautious evaluate the value of the integrated prospect value of the same 
scheme diﬀerently, but the rank of three regions remains consistent, which proves the 
validity in accurately evaluating the value of diﬀerent schemes and informing decision-
makers. Furthermore, for the more cautious, with a loss-sensitive attitude, the higher the 
prospect value of the scheme is assessed at, while for the less aggressive, with a lower 
prospect value of the scheme under the proﬁt-sensitive attitude, it suggests that a diﬀer-
ence in the personality/mindset of grid planning decision-makers will produce diﬀerent 
selection outcomes for scenario evaluation. Under the same risk attitude, the proﬁt-sensi-
tive type evaluates the prospect value of the scheme 42.5% higher than the loss-sensitive 
type on average. When the prospect value of Regions 2 and 3 tends to zero, the evaluation 
value of Region 1 remains around 0.3, which means that under the most conservative and 
negative planning mindset proposed in this paper, the planning scheme of Region 1 still 
has a great prospect of revenue and planning application value. That is, the decision-mak-
ers believe that the planning scheme in Region 1 has a larger prospect of gain and can bear 
a controllable risk of loss. The more radical the loss-sensitive decision-maker is, the lower 
the prospective value of the scenario is considered for the same proﬁt–loss attitude, while 
the opposite is true for the gain-sensitive decision-maker. In region 1, the diﬀerence in the 
evaluation of the indictor in adaptability of energy structure across risk attitudes for loss-
sensitive attitudes is less than 0.02, which shows that the adaptability of the energy struc-
ture is less considered to be signiﬁcantly aﬀected by the psychology of decision-makers. 
Nevertheless, the prospect value of economic adaptability varies by as much as 0.57 across 
diﬀerent decision-making mindsets, which means this level of indicator is the most sensi-
tive to the mentalities of decision-makers. 
 
Figure 9. Results of multiple psychological comprehensive evaluation of decision-makers.



<!-- page 22/24 -->

Energies 2024, 17, 3672 
22 of 24 
 
 
  
Figure 10. Results of the evaluation of ﬁrst-level indicators under multiple psychology in Region 1. 
6. Conclusions 
To foster the eﬃcient utilization and consumption of renewable energy sources, this 
paper proposes an adaptability evaluation of power grid planning scheme for a novel 
power system considering multiple decision psychology. Compared with the existing 
studies, this paper analyzes the demand for the adaptability of grid planning for a novel 
power system in depth, constructs an index system based on it to characterize the adapt-
ability of the planning scheme more comprehensively, and builds an adaptability evalua-
tion model of grid planning scheme for a novel power system based on GRA-TOPSIS in-
tegrating CG and ICPT, so as to more accurately reﬂect the evaluation results of the ex-
perts based on diﬀerent decision-making mentalities in the real environment. After the 
simulation and analysis of the algorithms, subsequent conclusions can be drawn, as fol-
lows: 
(1) In the evaluation of the adaptability of grid planning for novel power system, grid 
structure adaptability and reliability adaptability have a greater impact. 
(2) It is considered that the diﬀerent risk and loss attitudes of decision-makers can eﬀec-
tively improve the accuracy of the evaluation results, and radical proﬁt-sensitive de-
cision-making psychology pays more attention to economic adaptability. 
(3) The ICPT-TOPSIS method can better identify the weakness of the evaluation scheme, 
while the ICPT-GRA method can distinguish the better overall scenario more intui-
tively, and the combination evaluation method based on CG eﬀectively combines the 
advantages of these two diﬀerent methods. 
In the future, we will consider the diﬀerent identities and backgrounds of decision-
makers to build a more credible evaluation model, and carry out extensive empirical eval-
uations to guide power grid planning and promote the high-quality development of new 
energy. 
Author Contributions: Y.W. and C.Y. contributed to conception and design of this study; method-
ology and validation, C.Y. and Z.W.; investigation, Z.W. and J.W.; writing—original draft prepara-
tion, Y.W. and C.Y.; writing—review and editing, Z.W. and J.W.; visualization, Z.W. and J.W. All 
authors have read and agreed to the published version of the manuscript. 
Funding: This research was funded by Natural Science Foundation of Hebei Province, grant number 
G2022502004, Specia Fund for Basic Scientiﬁc Research Business Expenses of Central Universities, 
grant number 2023MS156. 
Data Availability Statement: Data are contained within the article.



<!-- page 23/24 -->

Energies 2024, 17, 3672 
23 of 24 
 
 
Conﬂicts of Interest: The authors declare no conﬂicts of interest. 
References 
1. 
Wu, J.; Chen, Y.; Yu, L.; Li, G.; Li, J. Has the evolution of renewable energy policies facilitated the construction of a new power 
system for China? A system dynamics analysis. Energy Policy 2023, 183, 113798. 
2. 
Li, R.; Hu, Y.; Wang, X.; Zhang, B.; Chen, H. Estimating the impacts of a new power system on electricity prices under dual 
carbon targets. J. Clean. Prod. 2024, 438, 140583. 
3. 
Bo, H.; Xie, K.G.; Shao, C.Z.; Pan, C.; Lin, C.; Zhao, Y. Commentary on Risk of New Power System Under Goals of Carbon 
Emission Peak and Carbon Neutrality: Characteristics, indices and Assessment Methods. Autom. Electr. Power Syst. 2023, 47, 1–
15. 
4. 
Liao, Z.; Kally, J.; Ru, S. Probabilistic modeling of renewable energy sources in smart grids: A stochastic optimization perspec-
tive. Sustain. Cities Soc. 2024, 109, 105522. 
5. 
Wu, Y.; Fang, J.; Ai, X.; Xue, X.; Cui, S.; Chen, X.; Wen, J. Robust co-planning of AC/DC transmission network and energy storage 
considering uncertainty of renewable energy. Appl. Energy 2023, 339, 120933. 
6. 
Li, F.; Yang, J.; Shen, S.; Zhu, K.; Qian, J.; Yan, C. Adaptability Evaluation of Power Grid Planning Scheme Based on Improved 
AHP-CRITIC-TOPSIS with High Proportion of Renewable Energy. In Proceedings of the 2023 IEEE International Conference 
on 
Power 
Science 
and 
Technology 
(ICPST), 
Kunming, 
China, 
5–7 
May 
2023; 
pp. 
623–630,doi: 
10.1109/ICPST56889.2023.10165456.. 
7. 
Yin, L.; Wei, X. Multigroup diﬀerential evolutionary and multilayer Taylor dynamic network planning for zero-carbon grid 
extension model with user satisfaction. Energy Convers. Manag. 2023, 297, 117753. 
8. 
Huang, Y.S.; Jiang, Y.Q.; Wang, J. Research on Adaptability Evaluation of Distribution Network Based on Improved TOPSIS-
PSO-SVM. Electron. Sci. Technol. 2022, 35, 54–63. 
9. 
Lu, X.Q.; Ye, Y.; Cao, C.; Meng, J.H.; Tang, H.; He, J. Comprehensive evaluation method of distribution network planning for 
distributed photovoltaic access. J. North China Electr. Power Univ. (Nat. Sci. Ed.) 2022, 51, 1–10. 
10. 
Zhang, Z.; Yang, H.Y.; Gao, X.T.; Wang, J.; Wang, Q. Research on Evaluation Method of Distribution Network Planning Scheme 
Adaptability Based on BPNN Model. Distrib. Util. 2021, 38, 56–63+88. 
11. 
He, X.; Gao, C.; Cao, H.Z.; Li, Y.; Yu, T. Index evaluation of distribution network based on improved analytic hierarchy process. 
Electr. Meas. Instrum. 2022, 59, 93–99. 
12. 
An, Z.; Wei, N.; Liu, S.; Chen, Q.F.; Xing, D. An Eﬃciency and Beneﬁt Evaluation Method for New Transmission Network 
Planning Based on Production Simulation. Power Syst. Clean Energy 2024, 40, 73–83. 
13. 
Zhang, J.; Gao, C.; Wang, T.; Duan, Y.; Xu, M.; Guo, Z. A Dynamic Evaluation Method for High-Permeability New Energy 
Distribution Network Planning Considering Multistage Development Trends. Front. Energy Res. 2022, 10, 958892. 
14. 
Lu, L.; Zhou, H.; Cai, S.; Liao, Y.; Jiang, L.; Wang, Y. Comprehensive Evaluation of Transmission Network Planning Schemes 
Based on IFAHP. In Proceedings of the 2020 4th International Conference on HVDC (HVDC), Xi’an, China, 6–9 November 2020; 
pp. 375–381. 
15. 
Si, J.D.; Wu, X.; Guo, Q.S.; Cai, H.; Cheng, L. Review of Flexible Interconnection of Regional Grids Interconnection Planning 
and Operation Techniques for High Percentage of Renewable Energy Consumption. Power Syst. Technol. 2024, 48, 2272–2286. 
16. 
Gao, Y.; Gao, Q.C. Serve the high-quality development of the power grid with standard digital innovation. State Grid News China 
2024, 1. https://doi.org/10.28266/n.cnki.ngjdw.2024.000403. 
17. 
Fan, W.; Fan, Y.; Tan, Z.; Ju, L.; Yao, X. Distributionally robust optimization model for virtual power plant participation in 
electricity carbon market based on multi-layer beneﬁt sharing. Syst. Eng.-Theory Pract. 2024, 44, 661–683. 
18. 
Wang, Z.; Lu, X.; Zhuang, M.; Zhang, C.; Chen, S. Spatial Optimization of Wind-PV Hybrid Energy Systems for the Three-North 
Region in China. J. Glob. Energy Interconnect. 2020, 3, 97–104. 
19. 
Gu, J.M.; Song, Y.T.; Liu, X.Y.; Zhu, S.X.; Lei, Y. Design of Security Defense System for UHV Power Grids under the Dual Carbon 
Background. Electr. Drive 2024, 1–6. https://doi.org/10.19457/j.1001-2095.dqcd25196. 
20. 
Tian, C.; Liu, Y.; Zhang, G.; Yang, Y.; Yan, Y.; Li, C. Transfer learning based hybrid model for power demand prediction of large-
scale electric vehicles. Energy 2024, 300, 131461. 
21. 
Wang, J.H. Exploration of Power Grid Planning Method Based on New Energy Consumption Under the “Dual Carbon” Goal. 
Electr. Eng. 2023, S1, 237–239. 
22. 
Zhang, Y.; Xiang, R.M.; Zheng, Z.H. Industrial User Decision Model Considering Diﬀerentiated Power Quality Services in the 
Context of Carbon Market. Proc. CSEE 2024, 1–14. 
23. 
Lu, Y.F.; Liu, D.; Zhang, Y. Construction Sequence Planning of Power Transmission and Transformation Projects Based on Game 
Theory Combined Weighting and Improved Technique for Order Preference by Similarity to Ideal Solution. Sci. Technol. Eng. 
2024, 24, 4124–4131. 
24. 
Fang, H.; Shang, L.; Dong, X.; Tian, Y. High Proportion of Distributed PV Reliability Planning Method Based on Big Data. 
Energies 2023, 16, 7692. 
25. 
Zhang, K.; Zhao, Q.; Wang, S.; Liang, F.; Ni, J.F. Construction and calculation method of comprehensive evaluation index re-
ﬂecting distributed photovoltaic hosting capacity of distribution network. Distrib. Util. 2024, 41, 3–11.



<!-- page 24/24 -->

Energies 2024, 17, 3672 
24 of 24 
 
 
26. 
Zhao, S.Q.; Tang, S.F. Comprehensive evaluation of transmission network planning scheme based on improved analytic hierar-
chy process, CRITIC method and TOPSIS. Electr. Power Autom. Equip. 2019, 39, 143–148+162. 
27. 
Ilbahar, E.; Kahraman, C.; Cebi, S. Risk assessment of renewable energy investments: A modiﬁed failure mode and eﬀect anal-
ysis based on prospect theory and intuitionistic fuzzy AHP. Energy 2022, 239, 121907. 
28. 
Cao, Y.; Li, G.J. Comprehensive evaluation of island isolated microgrid dispatch considering multiple decision psychology. 
Control Decis. 2022, 37, 1591–1600. 
29. 
Liu, Y.; Gaun, X.; Li, Y.C. Multi-attribute decision making based on comprehensive hesitation fuzzy entropy. Control Decis. 2024, 
39, 2022–2030. 
30. 
Qu, K.Q.; Qiao, J.M.; Mao, L.; Zhu, S.J.; Zhao, J.B. Optimal Conﬁguration and Site-selection Evaluation Method for Shared En-
ergy Storage Stations. Mod. Electr. Power 2024, 1–9. https://doi.org/10.19725/j.cnki.1007-2322.2023.0313. 
31. 
He, L.J.; Li, W.F.; Zhang, Y. Multi-objective optimization method based on grey synthetic incidence analysis. Control Decis. 2020, 
35, 1134–1142. 
32. 
Zhao, H.; Hao, X. Location decision of electric vehicle charging station based on a novel grey correlation comprehensive evalu-
ation multi-criteria decision method. Energy 2024, 299, 131356. 
33. 
Wang, L.; Yang, J.; Qu, B.; Pang, C. Multi-Objective Optimization of an Organic Rankine Cycle (ORC) for a Hybrid Solar–Waste 
Energy Plant. Energies 2024, 17, 1810. 
34. 
Akram, F.; Ahmad, T.; Sadiq, M. An integrated fuzzy adjusted cosine similarity and TOPSIS based recommendation system for 
information system requirements selection. Decis. Anal. J. 2024, 11, 100443. 
35. 
Aiello, G.; Quaranta, S.; Inguanta, R.; Certa, A.; Venticinque, M. A Multi-Criteria Decision-Making Framework for Zero Emis-
sion Vehicle Fleet Renewal Considering Lifecycle and Scenario Uncertainty. Energies 2024, 17, 1371. 
36. 
Çakiroğlu, R.; Çinici, O.K.; Asal, Ş.; Acır, A. Multi-objective optimization of the hydrogen fuel production of a solar-based 
cobalt-chlorine (Co–Cl) thermochemical cycle with grey relational analysis. Int. J. Hydrogen Energy 2024, 68, 360–373. 
37. 
Zhang, X.; Duan, X. Evaluating water resource carrying capacity in Pearl River-West River economic Belt based on portfolio 
weights and GRA-TOPSIS-CCDM. Ecol. Indic. 2024, 161, 111942. 
38. 
Chen, Y.T.; Chen, G.H.; Li, M.J. Research on Determining Weights of Combination Evaluation Method Using Cooperative 
Games. Chin. J. Manag. Sci. 2005, 13, 89–94 
39. 
Więckowski, J.; Kizielewicz, B.; Shekhovtsov, A.; Sałabun, W. RANCOM: A novel approach to identifying criteria relevance 
based on inaccuracy expert judgments. Eng. Appl. Artif. Intell. 2023, 122, 106114. 
Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual au-
thor(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to 
people or property resulting from any ideas, methods, instructions or products referred to in the content.
