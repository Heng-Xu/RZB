<!--
source: D6_决策方法/EN_Electronics_Fermatean_TOPSIS_power_sources_2025.pdf
sha256: 52f7e3cd6a007bb38f848284b4f0c1136308d22694a7ba2a934d2a6b586b6c9a
method: pymupdf
pages: 22
-->

<!-- page 1/22 -->

Academic Editor: Francisco
Javier Ruiz-Rodríguez
Received: 14 November 2025
Revised: 1 December 2025
Accepted: 3 December 2025
Published: 4 December 2025
Citation: Ye, L.; Li, J.; Yang, S.; Jiang,
L.; Liao, J.; Xu, B. An Improved
TOPSIS Method Using Fermatean
Fuzzy Sets for Techno-Economic
Evaluation of Multi-Type Power
Sources. Electronics 2025, 14, 4770.
https://doi.org/10.3390/
electronics14234770
Copyright: © 2025 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license
(https://creativecommons.org/
licenses/by/4.0/).
Article
An Improved TOPSIS Method Using Fermatean Fuzzy Sets for
Techno-Economic Evaluation of Multi-Type Power Sources
Lun Ye 1,2, Jichuan Li 3, Shengjie Yang 4,*, Lei Jiang 3, Jing Liao 1,2 and Binkun Xu 1,2
1
State Grid Hunan Electric Power Company Limited Economic & Technical Research Institute,
Changsha 410004, China; yelun92@126.com (L.Y.); liaojing987404@163.com (J.L.); 15575897727@189.cn (B.X.)
2
Energy Internet Supply and Demand Operation Hunan Provincial Key Laboratory, Changsha 410004, China
3
Hunan Power Exchange Center Co., Ltd., Changsha 410114, China; scottlee001@163.com (J.L.);
37836853@163.com (L.J.)
4
School of Computer Science, Hunan University of Technology and Business, Changsha 410205, China
*
Correspondence: yangsj16@hutb.edu.cn
Abstract
Scientific planning and optimal development of multi-type power sources are critical
prerequisites for supporting the robust evolution of emerging power systems. However,
existing techno-economic evaluation methods often face challenges such as higher-order
uncertainty and weight conflicts, making it difficult to provide reliable support for compar-
ing and selecting power source schemes. To address this, this paper proposes an improved
Technique for Order Preference by Similarity to an Ideal Solution (TOPSIS) method based
on Fermatean Fuzzy Sets (FFS) for techno-economic evaluation of multi-type power sources.
First, building on the traditional TOPSIS framework, we introduce Fermatean Fuzzy Sets
to construct a FF Hybrid Weighted Distance (FFHWD) measure. This measure simulta-
neously captures the subjective importance of evaluation indicators and decision-makers’
risk preferences. Second, we design a subjective-objective coupled weighting strategy inte-
grating Fuzzy Analytic Hierarchy Process (FAHP) and Entropy Weight Method (EWM) to
achieve dynamic weight balancing, effectively mitigating biases caused by single weighting
approaches. Finally, the FFHWD is integrated into the improved TOPSIS framework by
defining FF positive and negative ideal solutions. The comprehensive closeness coeffi-
cients of each power source scheme are calculated to enable robust ranking and optimal
selection of multi-type power source alternatives. Empirical analysis of five representative
power generation technologies—thermal power, hydropower, wind power, photovoltaics
(PV), and energy storage—demonstrates the following comprehensive techno-economic
ranking: hydropower > photovoltaics > thermal power > wind power > energy storage.
Hydropower achieves the highest closeness coefficient (−0.4198), whereas energy storage
yields the lowest value (−2.8704), effectively illustrating their respective advantages and
limitations within the evaluation framework. This research provides scientific decision-
making support and methodological references for optimizing multi-type power source
configurations and planning new power systems.
Keywords: multi-type power sources; techno-economic evaluation; Fermatean fuzzy;
TOPSIS; hybrid weighting
1. Introduction
Under the backdrop of accelerating energy structure transformation and building a
new power system centered on renewable energy, the scientific evaluation and optimal
Electronics 2025, 14, 4770
https://doi.org/10.3390/electronics14234770



<!-- page 2/22 -->

Electronics 2025, 14, 4770
2 of 22
selection of multi-type power technologies have emerged as a critical priority for ensuring
the security, stability, and low-carbon transition of power systems [1,2]. However, as
wind and solar photovoltaic energy gain increasing shares in the energy mix, and energy
storage systems develop into diverse flexible resources, power planning faces escalating
challenges: heightened uncertainties on both supply and demand sides, entangled techno-
economic indicators, and ambiguous long-term decision-making information [3,4]. Existing
evaluation methods often fail to address high-order uncertainties and conflicting weight
allocations, which undermines the reliability and precision of planning outcomes [5,6].
To address these limitations, this study proposes a novel framework to enhance decision-
making robustness and rationality in scheme selection. Such advancements will not only
support optimized power resource configurations but also advance coordinated planning
of multi-type energy systems and the construction of next-generation power grids.
In the field of techno-economic evaluation of power generation technologies, re-
searchers worldwide have explored various decision-making approaches to cope with
different types of uncertainty. For example, Younis et al. introduced a probabilistic hesitant
fuzzy set framework and developed a MARCOS-based multi-criteria decision-making
method capable of integrating heterogeneous information for comparing technologies such
as wind and solar power [7]. Building on the interplay between subjective knowledge and
objective data, Chen et al. combined a modified FAHP with the entropy weight method
to construct a hybrid weighting scheme, which they applied to evaluate the impacts of
decommissioning power plants on system reliability and economic performance [8]. In
another line of research, Li and Zhao proposed an enhanced fuzzy VIKOR approach for
performance evaluation of eco-industrial power plants, improving both weight deter-
mination and aggregation mechanisms to better support decision-making under fuzzy
environments [9]. Although these existing methods have proven effective in specific appli-
cation scenarios, they often face limitations such as computational intensity, sensitivity to
weight assignment, or insufficient ability to represent higher-order uncertainty. In contrast,
the TOPSIS method remains attractive due to its transparent logic, efficiency, robustness,
and intuitive interpretability. These advantages motivate the present study to adopt the
TOPSIS framework while extending it with Fermatean fuzzy sets and a hybrid weighted
distance measure, thereby addressing the challenges of uncertainty representation and
weight conflict that persist in modern power system techno-economic evaluation.
Most existing studies on the techno-economic evaluation of power generation technolo-
gies are conducted under deterministic information conditions, lacking effective methods
to address the inherent uncertainties in the evaluation process. Because the evaluation
involves multidimensional and complex indicators, experts often find it difficult to describe
them precisely using exact numerical values. As a result, the overall evaluation information
tends to be vague and imprecise. Against this background, the FFS was proposed as an
emerging fuzzy theory tool [10]. Compared with traditional Intuitionistic Fuzzy Sets (IFS)
and Pythagorean Fuzzy Sets (PFS), FFS not only considers the degrees of membership and
non-membership but also introduces a hesitation component. This allows it to represent a
broader range of uncertainty information and provides greater adaptability and flexibility
when dealing with complex evaluation problems [11,12]. Beyond these contributions,
several studies have incorporated Fermatean fuzzy theory into evaluation frameworks
to more effectively handle vagueness and hesitation in expert judgments. For instance,
Gul et al. developed a Fermatean fuzzy TOPSIS model for industrial risk assessment,
demonstrating its capability to quantify latent hazards [13]. Similarly, Yang and colleagues
constructed a decision-making framework using a Fermatean fuzzy integrated weighted
distance measure within the TOPSIS structure, enabling a more nuanced evaluation of
green and low-carbon ports under high uncertainty [14].



<!-- page 3/22 -->

Electronics 2025, 14, 4770
3 of 22
Meanwhile, distance serves as an essential tool for measuring differences between data
or variables, and it plays a pivotal role in multi-attribute decision-making methods [15,16].
For example, in the TOPSIS method, alternative schemes are ranked by calculating their
distances from the ideal solution. Therefore, constructing an effective distance measurement
approach has become a topic of significant research interest. Among various distance
measures, the Ordered Weighted Distance (OWD) method allows flexible control over the
influence of key data points by adjusting positional weights. This property has led to its
widespread integration into numerous aggregation tools, giving rise to multiple extended
forms. As a further development of OWD, the Hybrid Weighted Distance (HWD) method
combines both ordered and arithmetic weighting mechanisms. It simultaneously accounts
for the intrinsic importance of data and their positional influence during aggregation,
thereby overcoming the limitations of the traditional OWD approach.
In this study, the HWD method is extended to the Fermatean fuzzy environment, and
a new distance measure—FFHWD—is proposed to enhance the rationality and accuracy
of the evaluation process. At the same time, to identify the relative importance of evalu-
ation indicators, a comprehensive weighting model based on the FAHP and the EWM is
constructed, integrating both expert subjective judgment and objective data information.
Furthermore, the proposed FFHWD measure and the integrated weighting model are
incorporated into the TOPSIS framework, forming a novel techno-economic evaluation
model for multi-type power sources. This framework strategically integrates the TOPSIS
methodology’s inherent strengths—including structural transparency, computational effi-
ciency, result robustness, and interpretability—while innovatively embedding the FFHWD
measure and a hybrid weighting mechanism. This dual integration substantially enhances
the framework’s capacity to manage complex fuzzy information environments and estab-
lishes a more rigorous scientific foundation for weight determination through synergistic
combination of subjective expert judgment and objective data analytics. An empirical
analysis based on representative power sources in a Chinese province is conducted to verify
the applicability of the model. The proposed framework provides a more scientific and
robust decision-making basis for power project investment and operation management,
thereby improving the practical effectiveness of engineering economic evaluation.
2. Evaluation Index System Based on DEMATEL
2.1. Initial Evaluation Indicator System
Constructing a techno-economic evaluation index system for multi-type power sources
is the primary task of the assessment process, aiming to systematically and comprehen-
sively reveal the core characteristics and attributes of the evaluated objects. The scientific
soundness and rationality of the index system directly determine the accuracy and reliabil-
ity of the evaluation results. Therefore, during its construction, several key principles must
be strictly followed [17–20]. The selected indicators should be both scientific and practi-
cal, capable of objectively reflecting the techno-economic characteristics of power sources
with clear objectives and broad applicability. They should also exhibit measurability and
comparability, meaning that the indicator data can be easily obtained and allow for reliable
horizontal and vertical comparisons. At the same time, the system should be comprehen-
sive yet concise, covering all critical aspects of the techno-economic performance of power
sources while maintaining a clear structure and concise formulation. Finally, the indicators
should possess strong operability and independence to ensure ease of application and data
processing, while minimizing semantic overlap or redundancy. Based on these principles,
this study establishes the specific evaluation indicators for the techno-economic assessment
of multi-type power sources as follows [21–23].



<!-- page 4/22 -->

Electronics 2025, 14, 4770
4 of 22
(1)
Unit Electricity Cost. This indicator reflects the total cost incurred for generating
one kilowatt-hour of electricity over the entire life cycle of a power source. It is
typically measured by the LCOE; for energy storage systems, the cycle-based cost per
kilowatt-hour can be used instead. As the core metric for evaluating the economic
competitiveness of power sources, the unit electricity cost directly determines their
bidding capability in the electricity market and serves as the fundamental benchmark
for economic comparison among different power types.
(2)
Unit Capacity Investment Cost. This indicator represents the initial investment re-
quired to construct each kilowatt of installed capacity. It reflects the project’s financial
threshold and investment pressure, thus serving as an important reference for in-
vestors and decision-makers when assessing project feasibility.
(3)
Operation and Maintenance (O&M) Cost Ratio. This refers to the proportion of annual
O&M costs to the total annual generation revenue or overall cost. It indicates the
operational stability and long-term economic performance of a power source. A high
O&M cost ratio often implies a heavy operational burden and greater sensitivity of
profitability to fluctuations in fuel prices or market electricity prices.
(4)
Capacity Factor. Defined as the ratio of actual electricity generation to the theo-
retical maximum generation under full-load operation, this indicator measures the
“productivity” and utilization level of a power source. It reflects the combined ef-
fects of technological reliability and local resource conditions, thereby providing a
comprehensive view of the power source’s operational performance.
(5)
Start-Up and Regulation Characteristics. This composite performance indicator can
be decomposed into two aspects—start-up time and ramp rate—and can also be
evaluated systematically using Fermatean fuzzy numbers to quantify flexibility. In
power systems with a high penetration of renewable energy, the rapid response and
regulation capability of power sources play a crucial role in maintaining system
stability and mitigating output fluctuations.
(6)
Energy Conversion Efficiency. This indicator represents the ratio of output energy
to input energy. For power generation units, it corresponds to generation efficiency,
while for energy storage systems, it reflects round-trip efficiency. It directly illustrates
the technological advancement and energy utilization level of a system, where low
efficiency typically indicates higher energy losses and hidden costs.
(7)
Carbon Emission Intensity. Carbon emission intensity measures the amount of CO2-
equivalent emissions produced per kilowatt-hour of electricity generated. Under
the dual-carbon (carbon peaking and carbon neutrality) objectives, this indicator
has become a key parameter for assessing the environmental friendliness of power
sources. It directly affects their social acceptability, environmental costs, and long-term
development prospects.
2.2. Dimensionality Reduction of the Evaluation Indicators Using DEMATEL
The DEMATEL method analyzes structural relationships within complex evaluation
systems by calculating correlations among assessment indicators and classifying these
indicators into cause factors and effect factors, thereby determining the importance levels of
indicators within the evaluation system [24–26]. This study incorporates fuzzy mathematics
into the traditional DEMATEL approach to address assessment uncertainty arising from
semantic ambiguity. The correspondence between linguistic variables for expert judgments
and fuzzy numbers is presented in Table 1.



<!-- page 5/22 -->

Electronics 2025, 14, 4770
5 of 22
Table 1. Correspondence between linguistic variables and triangular fuzzy numbers.
Scale
Degree of Influence
Triangular Fuzzy Number (lij, mij, uij)
NO
No impact
(0, 0.1, 0.3)
VL
Slight impact
(0.1, 0.3, 0.5)
L
Minor impact
(0.3, 0.5, 0.7)
H
Significant impact
(0.5, 0.7, 0.9)
VH
Major impact
(0.7, 0.9, 1.0)
The steps for calculating centrality based on fuzzy DEMATEL are as follows:
(1)
Construct the initial direct influence matrix eB(k). According to the correspondence
between linguistic variables and fuzzy numbers in Table 1, the initial direct influence
matrix eB(k) provided by the k-th expert is obtained.
(2)
Calculate the normalized triangular fuzzy numbers (ls(k)
ij , ms(k)
ij , us(k)
ij ). Normalize
the triangular fuzzy numbers in the initial direct influence matrix eB(k) based on
Equations (1)–(3).
ls(k)
ij
=
l(k)
ij −minl(k)
ij
∆max
min
(1)
ms(k)
ij
=
m(k)
ij −minm(k)
ij
∆max
min
(2)
us(k)
ij
=
u(k)
ij −minu(k)
ij
∆max
min
(3)
where ∆max
min = maxu(k)
ij −minl(k)
ij
represents the difference between the right-hand value
and the left-hand value.
(3)
Calculate the comprehensive standardized value x(k)
ij . First, calculate the left and right
standard values L(k)
ij
and U(k)
ij
according to Equations (4) and (5). Then, calculate the
comprehensive standardized value x(k)
ij
based on Equation (6).
L(k)
ij
=
ms(k)
ij
1 + ms(k)
ij −ls(k)
ij
(4)
U(k)
ij
=
us(k)
ij
1 + us(k)
ij −ms(k)
ij
(5)
x(k)
ij
=
L(k)
ij (1 −L(k)
ij ) + U(k)
ij U(k)
ij
1 −L(k)
ij + U(k)
ij
(6)
(4)
Obtain the quantitative influence value b(k)
ij
determined by the k-th expert for factor i
on factor j.
b(k)
ij
= min
1≤k≤Kl(k)
ij + x(k)
ij ∆max
min
(7)
(5)
Calculate the direct influence matrix B.
bij =

b(1)
ij + b(2)
ij + · · · + b(k)
ij

/k
(8)



<!-- page 6/22 -->

Electronics 2025, 14, 4770
6 of 22
B = (bij)n×n
(9)
(6)
Calculate the comprehensive influence matrix T by first standardizing the data in B
according to Equation (10), and then obtaining the comprehensive influence matrix T
based on Equation (11).
G = B/ max
1≤i≤n
n
∑
j=1
bij
(10)
T = G + G2 + G3 + · · · + Gn
(11)
(7)
Calculate the causality degree and centrality. Aggregate the elements in T separately
by rows and columns, and calculate the influence degree mi and the affected degree
ei of each evaluation indicator according to Equations (12) and (13). The causality
degree ei and centrality mi can be calculated according to Equations (14) and (15).
fi =
n
∑
j=1
tij, i = 1, 2, . . . , n
(12)
ei =
n
∑
i=1
tij, j = 1, 2, . . . , n
(13)
ni = fi −ei
(14)
mi = fi + ei
(15)
If the causality degree ni > 0, it can be determined that the indicator is a causal factor;
otherwise, the factor is a result factor. The larger the centrality value mi, the stronger the
importance of the indicator in the entire evaluation system.
3. Combined Weighting Based on the Improved FAHP-EWM
3.1. Calculation of Subjective Weights Based on FAHP
In the techno-economic evaluation of multiple power generation technologies, experts’
judgments on the relative importance of indicators often involve fuzziness and uncertainty.
To address this, this study employs triangular fuzzy numbers to replace the precise values
used in the traditional Analytic Hierarchy Process (AHP), thereby constructing a fuzzy
judgment matrix. This approach effectively captures the fuzzy range and confidence level
of expert evaluations. By applying the principle of fuzzy number comparison, it determines
the ranking and weights of indicators, enhancing both the rationality and fault tolerance of
the weighting process, and better reflecting real-world decision-making scenarios [27,28].
3.1.1. Construction of the Fuzzy Judgment Matrix
Experts employ the triangular fuzzy scale of FAHP to perform pairwise comparisons
between each pair of criteria (i,j), assessing the relative importance of criterion i over
j [29–31]. The evaluation outcomes are then mapped to corresponding triangular fuzzy
numbers (lijk, mijk, uijk). For each expert k, fuzzy judgment values for all (i,j) criterion
pairs are obtained through the aforementioned method, resulting in the construction of a
complete fuzzy judgment matrix Ak.
Ak = (ηijk)n×n =


(l11k, m11k, u11k)
(l21k, m21k, u21k)
...
(ln1k, mn1k, un1k)
(l12k, m12k, u12k)
(l22k, m22k, u22k)
...
(ln2k, mn2k, un2k)
. . .
. . .
...
. . .
(l1nk, m1nk, u1nk)
(l2nk, m2nk, u2nk)
...
(lnnk, mnnk, unnk)


(16)



<!-- page 7/22 -->

Electronics 2025, 14, 4770
7 of 22
where n is the number of indicators; lijk and uijk are the left and right judgment boundaries
of the evaluation value, respectively, indicating the degree of fuzziness of the judgment.
The larger they are, the higher the fuzziness of the judgment. mijk is the median value
with a membership degree of 1, representing the most likely importance ratio judgment by
experts, which is determined using the 1–9 scale method similar to the traditional AHP
method. Among them, ηijk = (1,1,1), indicating that the indicator is equally important
to itself. Moreover, when ηijk = (lijk, mijk, uijk) is given, its inverse judgment must satisfy
ηjik =

1/uijk, 1/mijk, 1/lijk

, thus ensuring that the fuzzy judgment matrix meets the
requirements of reciprocity and consistency.
3.1.2. Calculation of Weights at This Hierarchical Level
The fuzzy comprehensive importance of indicator i relative to the other indicators,
denoted as Qik, is given as follows:
Qik =
 
n
∑
j=1
ηijk
!
⊗
 
n
∑
i=1
n
∑
j=1
ηijk
!−1
=





n
∑
j=1
lijk
n
∑
i=1
n
∑
j=1
uijk
,
n
∑
j=1
mijk
n
∑
i=1
n
∑
j=1
mijk
,
n
∑
j=1
uijk
n
∑
i=1
n
∑
j=1
lijk





−1
(17)
n
∑
j=1
ηijk =
 
n
∑
j=1
lijk,
n
∑
j=1
mijk,
n
∑
j=1
uijk
!
(18)
 
n
∑
i=1
n
∑
j=1
ηijk
!−1
=





1
n
∑
i=1
n
∑
j=1
uijk
,
1
n
∑
i=1
n
∑
j=1
mijk
,
1
n
∑
i=1
n
∑
j=1
lijk





−1
(19)
where
n
∑
j=1
ηijk represents the summation of triangular fuzzy numbers ηijk = (lijk, mijk, uijk),
and its summation rule follows the addition principle of triangular fuzzy numbers. When
two triangular fuzzy numbers are A = (l1, m1, u1) and B = (l2, m2, u2), their sum is
A + B = (l1 + l2, m1 + m2, u1 + u2), because the left and right boundaries and the center
value of triangular fuzzy numbers can be linearly superimposed independently, satisfying
the closure and additivity of fuzzy number addition.
The degree of possibility that the comprehensive importance of indicator i, compared
with the other indicators, is greater than that of indicator j(j = 1,2,. . .,n; j̸=i), is denoted as
d(xik) and is given as follows:
d(xik) =
min
j=1,2,...,n;j̸=i
"
lijk −uijk
(mijk −uijk) −(mijk −lijk), 1
#
(20)
The local fuzzy weight Wk of each indicator within the indicator set is given as follows:
Wk = {d(x1k), d(x2k), · · · , d(xnk)}
(21)
After normalization, the fuzzy weight set Wk’ is obtained as follows:
W′
k =

d′(x1k), d′(x2k), · · · , d′(xnk)
	
(22)
d′(xik) =
d(xik)
n
∑
i=1
d(xik)
(23)



<!-- page 8/22 -->

Electronics 2025, 14, 4770
8 of 22
Based on the fuzzy weight set, the subjective weight Ws is calculated using the
weighted arithmetic mean method as follows:
Ws = λkW′
k
(24)
where λk represents the weight of the k-th expert,
T
∑
k=1
λk = 1.
3.2. Calculation of Objective Weights Based on EWM
To overcome the potential bias introduced by subjective weighting, this study employs
the EWM to determine the objective weights of the evaluation indicators. This method
automatically calculates the weights based on the degree of variation in the indicator data,
thereby fully utilizing the information contained within the data itself. By minimizing
human interference, it enhances the objectivity and interpretability of the techno-economic
evaluation results for multiple power generation technologies [32].
3.2.1. Determination of System Entropy
Considering the safety condition of the j-th evaluation indicator as a system, the
information entropy value ej of this indicator can be derived according to the definition of
entropy as follows:
ej = −1
ln n
n
∑
i=1
yij ln yij
(25)
yij =
x′ij
n
∑
i=1
x′ij
(26)
3.2.2. Calculation of Weights
Based on the information entropy value of the j-th indicator, its weight wj within this
hierarchical level is calculated as follows:
ωj =
1 −ej
n
∑
j=1
(1 −ej)
(27)
The information entropy value ej may approach 1, in which case even a small change
in entropy can lead to an excessively large deviation in the calculated weight. To address
this issue, this study improves the weight calculation method. The modified weight ω′j is
computed as follows:
ω′
j =
n
∑
i=1
ei
n + 1 −ej
n
∑
j=1
 n
∑
i=1
ei
n + 1 −ej

(28)
The subjective weights Ws = (Ws1, Ws2, . . ., Wsn) and the objective weights
Wo = (Wo1, Wo2, . . ., Won) are obtained using the FAHP and EWMs, respectively. The calcu-
lation formula for the comprehensive weights is as follows:
ωj = δWs + (1 −δ)Wo
(29)
where δ ∈[0, 1].



<!-- page 9/22 -->

Electronics 2025, 14, 4770
9 of 22
4. Comprehensive Techno-Economic Evaluation Model for Multiple
Power Generation Technologies Based on FFHWD-TOPSIS
4.1. Overview of the Traditional TOPSIS Method
In the techno-economic evaluation of multiple power generation technologies, the
TOPSIS method ranks alternative schemes by quantifying their relative closeness to the
ideal solution. This approach fully utilizes the information contained in the original data
and clearly reveals the differences among alternatives. It offers a transparent computational
process and produces stable and reliable results [33,34]. In this study, TOPSIS is incorpo-
rated into the evaluation framework because of its effectiveness in handling multi-attribute
decision-making problems while integrating both subjective and objective weights. This
provides a clear and interpretable basis for the optimal selection of power generation
schemes. The modeling procedure is as follows:
Assume there are m alternative schemes, denoted as A1, A2, . . ., Am, and n decision
indicators, denoted as R1, R2, . . ., Rn. The decision matrix X = (xij)m*n constructed from the
original data is given as follows:
X =








x11
x12
· · ·
x1n
x21
x22
· · ·
x2n
...
...
...
...
xm1
xm2
· · ·
xmn








(30)
where xij represents the value of the j-th decision indicator for the i-th evaluation object.
(1)
Transform the original decision matrix X into the normalized decision matrix
Y = (yij)m*n using the following formula. Normalizing the original decision matrix
eliminates the influence of differing dimensions among indicators and resolves the
issue of incomparability between them.
yij =
xij
s
n
∑
i=1
x2
ij
(31)
(2)
Construct the weighted normalized decision matrix Z.
Z = (zij)m×n
(32)
zij = Wj × yij
(33)
where Wj represents the weight of the j-th evaluation indicator.
(3)
Determine the positive ideal solution S+ and the negative ideal solution S−. The
positive ideal solution represents the scenario in which all evaluation indicators
achieve their optimal values, while the negative ideal solution represents the scenario
in which all indicators reach their worst values.
s+
j = max

zij/1 ⩽i ⩽m
	
(34)
s−
j = min

zij/1 ⩽i ⩽m
	
(35)
(4)
Calculate the Euclidean distances of each alternative from the positive and negative
ideal solutions:



<!-- page 10/22 -->

Electronics 2025, 14, 4770
10 of 22
d+
i =
v
u
u
t
n
∑
j=1
(zij −s+
j )2 (i = 1, 2, · · · , m)
(36)
d−
i =
v
u
u
t
n
∑
j=1
(zij −s−
j )2 (i = 1, 2, · · · , m)
(37)
(5)
Calculate the relative closeness Ci of each evaluation object using the following
formula. A larger Ci value indicates that the evaluation object is closer to the ideal
solution, whereas a smaller Ci value indicates closer proximity to the negative ideal
solution. The evaluation objects are then ranked according to the magnitude of their
relative closeness values.
Ci =
d−
i
d+
i + d−
i
(38)
Despite the well-structured framework and computational simplicity of the tradi-
tional TOPSIS method that have contributed to its widespread adoption in multi-attribute
decision-making (MADM) domains, several critical limitations emerge, particularly in eval-
uation scenarios involving high uncertainty and strong fuzziness such as new energy power
generation technologies. Firstly, the conventional TOPSIS assumes deterministic or precise
numerical values for evaluation inputs, whereas practical techno-economic assessments of
power generation systems often involve expert judgments characterized by fuzziness and
hesitation. This discrepancy may result in information loss or bias during decision-making
processes. Secondly, the default application of Euclidean distance to measure proximity
between alternatives and ideal solutions fails to adequately account for variations in indica-
tor importance and ranking sensitivity. The distance metric exhibits notable vulnerability
to conflicting weight assignments, making evaluation outcomes excessively sensitive to
extreme values or localized data fluctuations.
4.2. Fermatean Fuzzy Hybrid Weighted Distance
Given the limitations of traditional TOPSIS, it is essential to construct a distance metric
with enhanced expressive capability and robustness to improve its adaptability in handling
fuzzy, multi-scale evaluation information. This study introduces FFS to characterize mem-
bership, non-membership, and hesitation degrees in expert judgments [35–39], and further
develops the FFHWD as a novel distance metric. This approach simultaneously integrates
subjective-objective weights, positional weights, and fuzzy information while maintaining
methodological simplicity. The proposed improvement preserves the structural integrity of
traditional TOPSIS while significantly enhancing its stability and discriminative capability
in complex techno-economic evaluations of power generation technologies.
First, let X be a non-empty set. The expression of an FFS Y belonging to X is given
as follows:
Y = {⟨xi, µY(xi), νY(xi)⟩|xi ∈X}
(39)
where µY(xi) : X →[0, 1] is termed as ‘the membership degree of the factor xi in the set
Y’, and vY(xi) : X →[0, 1] is indicated as ‘the non-membership degree of the factor xi in
the set Y’. In addition, 0 ≤[µY(xi)]3 + [νY(xi)]3 ≤1 for all xi ∈X. For a FFS Y and xi ∈X,
τ =
3q
1 −[µY(xi)]3 −[νY(xi)]3 is the indeterminacy degree of xi to Y.



<!-- page 11/22 -->

Electronics 2025, 14, 4770
11 of 22
For simplicity, the FFN is denoted as α = ⟨µY, νY⟩. Let λ be a positive real number, and
let α = ⟨µY, νY⟩, α1 = ⟨µY1, νY1⟩, and α2 = ⟨µY2, νY2⟩be three FFNs defined on a non-empty
set X. The corresponding operational definitions of these FFNs are given as follows:
α1 ⊕α2 =

3q
µ3
Y1 + µ3
Y2 −µ3
Y1µ3
Y2, νY1νY2

(40)
α1 ⊗α2 =

µY1µY2, 3q
v3
Y1 + v3
Y2 −v3
Y1v3
Y2

(41)
λα =

3q
1 −(1 −µ3
Y)λ, vλ
Y

(42)
αc = ⟨νY, µY⟩
(43)
For a FFN α = ⟨µY, νY⟩, the functions S(Y) = µ3
Y −ν3
Y and A(Y) = µ3
Y + ν3
Y are
defined as the score function and the accuracy function of α, respectively. If S(α1) < S(α2),
then α1 < α2; if S(α1) = S(α2), then
(
A(α1) < A(α2) ⇒α1 < α2
A(α1) = A(α2) ⇒α1 = α2
.
For two FFNs, α1 = ⟨µY1, νY1⟩and α2 = ⟨µY2, νY2⟩, the distance between them can be
defined as follows:
d(α1, α2) = 1
2
µ3
Y1 −µ3
Y2
 +
ν3
Y1 −ν3
Y2
 +
τ3
Y1 −τ3
Y2


(44)
Let A = (α1, α2, . . . , αn) be a set of FFNs, and let w = (w1, w2, . . . , wn)T be the weight
vector corresponding to these fuzzy numbers. Then, the Fermatean fuzzy weighted averag-
ing (FFWA) operator is defined as follows:
FFWA(α1, α2, . . . , αn) =
n
∑
j=1
wjαj
(45)
To provide a more comprehensive characterization of both subjective and objective
information in the evaluation of power supply schemes, this study adopts the concept of
the HWD proposed in [40] and develops a FFHWD measure. This measure integrates both
the intrinsic importance of each indicator and its positional weight within the sequence.
By doing so, it more reasonably captures the decision-maker’s risk preferences and the
inherent differences within the data, thereby enhancing the overall comprehensiveness and
reliability of the evaluation results [41,42].
For two sets of FFNS A = (α1, α2, . . . , αn) and B = (α′1, α′2, . . . , α′n), their FFHWD is
defined as:
FFHWDw,ω(A, B) =
n
∑
j=1
wj

ed

ασ(j), α′
σ(j)

(46)
where ed

ασ(j), α′
σ(j)

denotes the j-th largest of the weighted individual distance
.
d
 αj, α′j
 = nωjd
 αj, α′j

, j = 1, 2, . . . , n, ω = (ω1, . . . , ωn)T is the weight vector related
to the individual d
 αj, α′j

, with ωj ∈[0, 1] and their sum is 1. w = (w1, . . . , wn)T is the
weight vector for FFHWD measure. The balancing parameter n acts as a balance role.
4.3. Comprehensive Evaluation Framework Based on FFHWD-TOPSIS
Based on the previously established FFHWD measure and the combined weight-
ing model, this section proposes a complete FFHWD-TOPSIS framework for the techno-
economic evaluation of multiple power generation technologies. The proposed framework
aims to systematically integrate subjective and objective information under a fuzzy envi-



<!-- page 12/22 -->

Electronics 2025, 14, 4770
12 of 22
ronment, providing a clear and operational procedure for scheme optimization. The main
steps are illustrated in Figure 1.
Initial evaluation indicators
Start
Establish evaluation indicator system
DEMATEL processing
Objects to be evaluated
Expert evaluation matrix
Comprehensive evaluation information
FFHWD-TOPSIS method
FAHP
EWM
Integrated weights
Positive ideal solution (PIS) B+
Negative ideal solution (NIS) Bെ
FFHWD(Bi, B+)
FFHWD(Bi, Bെ)
Closeness
Ranking of Alternatives
End
 
Figure 1. Flowchart of techno-economic evaluation for multi-type power sources.
(1)
Construct the Fermat-type decision matrix. Expert ek(k = 1, 2, . . . , K) evaluates the
criterion Cj(j = 1, 2, . . . , m) under the evaluation object Bi(i = 1, 2, . . . , n) in the
form of FFN, denoted as γk =
D
αk
ij, βk
ij
E
. Therefore, the fuzzy soft decision matrix
Pk =
h
γk
ij
i
n×m of the k-th expert can be obtained:
Pk =


D
αk
11, βk
11
E
D
αk
12, βk
12
E
· · ·
D
αk
1m, βk
1m
E
D
αk
21, βk
21
E
D
αk
22, βk
22
E
· · ·
D
αk
2m, βk
2m
E
...
...
...
...
D
αk
n1, βk
n1
E
D
αk
n2, βk
n2
E
· · ·
D
αk
nm, βk
nm
E


n×m
(47)
(2)
Normalize the individual decision matrices of experts. Let the normalized criterion
value be gij(i = 1, 2, . . . , n; j = 1, 2, . . . , m).
(3)
Apply the FFWA operator, combined with the weight of each expert ek(k = 1, 2, . . . , K)
denoted as εk, to aggregate the decision matrices of all experts, thereby obtaining the
overall fuzzy soft decision matrix P =

γij

n×m(i = 1, 2, . . . , n; j = 1, 2, . . . , m):
P =


D
f
α11, f
β11
E
D
f
α12, f
β12
E
· · ·
D
g
α1m, g
β1m
E
D
f
α21, f
β21
E
D
f
α22, f
β22
E
· · ·
D
g
α2m, g
β2m
E
...
...
...
...
D
g
αnm, g
βnm
E
D
g
αnm, g
βnm
E
· · ·
D
g
αnm, g
βnm
E


n×m
(48)



<!-- page 13/22 -->

Electronics 2025, 14, 4770
13 of 22
(4)
Apply the combined weighting method presented in Section 3 to determine the
comprehensive weights of each indicator.
(5)
Calculate the Fermatean fuzzy PIS B+ and Fermatean fuzzy NIS B−as follows:
B+ =

C1(B+), C2(B+), . . . , Cn(B+)
	 =

max
i

S(γij)
j = 1, 2, . . . , n

(49)
B−=

C1(B−), C2(B−), . . . , Cn(B−)
	 =

min
i

S(γij)
j = 1, 2, . . . , n

(50)
(6)
Calculate the deviations between each alternative Bi and the FF PIS B+ and NIS B−,
denoted as FFHWDw,ω(Bi, B+) and, respectively.
(7)
Calculate the closeness value ς(Bi) for each alternative solution Bi(i = 1, 2, . . . , n).
ζ(Bi) =
FFHWDw,ω(Bi, B−)
max(FFHWDw,ω(Bi, B−)) −
FFHWDw,ω(Bi, B+)
min(FFHWDw,ω(Bi, B+))
(51)
(8)
Sort all alternative schemes in descending order based on the closeness degree ς(Bi)
calculated in the previous step, and determine the optimal scheme.
5. Case Studies
5.1. Selection of Evaluation Indicators
To validate the effectiveness of the proposed techno-economic evaluation model, five
representative power generation technologies were selected as case studies: thermal power
(B1), hydropower (B2), wind power (B3), photovoltaics (B4), and energy storage (B5). This
combination encompasses traditional fossil fuels, renewable energy sources, and flexible
resources, comprehensively reflecting the techno-economic characteristics and structural
differences across multi-type power generation systems. The evaluation framework consists
of seven core indicators: C1 (levelized cost of electricity, LCOE), C2 (capacity factor), C3
(start-up and regulation characteristics), C4 (energy conversion efficiency), C5 (carbon
emission intensity), C6 (specific investment cost), and C7 (operational and maintenance
cost ratio), which systematically characterize the techno-economic performance of different
power sources. Based on this framework, domain experts were invited to assess the
interrelationships among the aforementioned indicators using the linguistic variables
defined in Table 1. The DEMATEL method was then applied to structurally analyze
the evaluation results. As an illustrative example, the data from Expert 1 are presented
in Table 2.
Table 2. Expert 1’s influence degree judgments for evaluation indicators.
Evaluation Indicator
C1
C2
C3
C4
C5
C6
C7
C1
NO
L
VH
H
VH
VH
H
C2
H
NO
VH
H
H
L
VH
C3
VH
H
NO
VH
VH
VH
H
C4
L
VH
VH
NO
H
H
VH
C5
VH
H
VH
L
NO
VH
H
C6
VL
VL
L
H
VL
NO
L
C7
L
VL
L
VL
VL
L
NO
Based on the correspondence between linguistic variables and fuzzy numbers in
Table 1, and combined with the data in Table 2, the initial direct influence matrix provided
by Expert 1 is as follows:



<!-- page 14/22 -->

Electronics 2025, 14, 4770
14 of 22
eB(1) =


(0, 0.1, 0.3)
(0.3, 0.5, 0.7)
(0.7, 0.9, 1.0)
(0.5, 0.7, 0.9)
(0.7, 0.9, 1.0)
(0.7, 0.9, 1.0)
(0.5, 0.7, 0.9)
(0.5, 0.7, 0.9)
(0, 0.1, 0.3)
(0.7, 0.9, 1.0)
(0.5, 0.7, 0.9)
(0.5, 0.7, 0.9)
(0.3, 0.5, 0.7)
(0.7, 0.9, 1.0)
(0.7, 0.9, 1.0)
(0.5, 0.7, 0.9)
(0, 0.1, 0.3)
(0.7, 0.9, 1.0)
(0.7, 0.9, 1.0)
(0.7, 0.9, 1.0)
(0.5, 0.7, 0.9)
(0.3, 0.5, 0.7)
(0.7, 0.9, 1.0)
(0.7, 0.9, 1.0)
(0, 0.1, 0.3)
(0.5, 0.7, 0.9)
(0.5, 0.7, 0.9)
(0.7, 0.9, 1.0)
(0.7, 0.9, 1.0)
(0.5, 0.7, 0.9)
(0.7, 0.9, 1.0)
(0.3, 0.5, 0.7)
(0, 0.1, 0.3)
(0.7, 0.9, 1.0)
(0.5, 0.7, 0.9)
(0.1, 0.3, 0.5)
(0.1, 0.3, 0.5)
(0.3, 0.5, 0.7)
(0.5, 0.7, 0.9)
(0.1, 0.3, 0.5)
(0, 0.1, 0.3)
(0.3, 0.5, 0.7)
(0.3, 0.5, 0.7)
(0.1, 0.3, 0.5)
(0.3, 0.5, 0.7)
(0.1, 0.3, 0.5)
(0.1, 0.3, 0.5)
(0.3, 0.5, 0.7)
(0, 0.1, 0.3)


Based on Equations (1)–(9), the initial direct influence matrix can be obtained
as follows:
B(1) =


0.1333
0.5
0.8667
0.7
0.8667
0.8667
0.7
0.7
0.1333
0.8667
0.7
0.7
0.5
0.8667
0.8667
0.7
0.1333
0.8667
0.8667
0.8667
0.7
0.5
0.8667
0.8667
0.1333
0.7
0.7
0.8667
0.8667
0.7
0.8667
0.5
0.1333
0.8667
0.7
0.3
0.3
0.5
0.7
0.3
0.1333
0.5
0.5
0.3
0.5
0.3
0.3
0.5
0.1333


Subsequently, by integrating the opinions of the remaining experts and applying the
traditional DEMATEL method, the influence degree, affected degree, causality degree, and
centrality of the evaluation indicators were calculated using Equations (10)–(15), with the
detailed results presented in Table 3.
Table 3. Specific calculation results of evaluation indicators.
Evaluation
Indicator
Nfluence
Degree fi
Affected
Degree ei
Causality
Degree ni
Centrality
mi
Normalized
Centrality
C1
1.1108
0.7000
0.4108
1.8108
0.349
C2
1.0730
0.9644
0.1086
2.0374
0.733
C3
1.1276
1.0674
0.0602
2.1950
1.000
C4
1.1071
0.9194
0.1877
2.0265
0.715
C5
0.9156
0.8789
0.0367
1.7945
0.321
C6
0.6203
1.0601
−0.4398
1.6804
0.128
C7
0.6203
0.9845
−0.3642
1.6048
0.000
The centrality analysis in Table 3 indicates that evaluation indicator C7 has the lowest
influence on the overall system, followed by C6. To simplify model complexity and focus
on core elements, this study retains the five key indicators C1–C5 for subsequent evaluation.
Based on this framework, four senior experts in power system planning (E1–E4) were
invited to conduct evaluations using FFNs. Prior to the formal assessment, experts were
provided with a Fermatean Fuzzy Number Operations Manual to define the semantic
scales for the membership degree µ (“confidence in superior indicator performance”)
and non-membership degree ν (“confidence in inferior indicator performance”). Experts
were instructed to adhere to the constraint µ3 + ν3 ≤1. A structured questionnaire was
employed to independently assess FFNs for the five power generation technologies across
the five indicators. The questionnaire utilized a 9-point linguistic variable system mapped
to FFNs to ensure consistent interpretation among experts. The raw evaluation data are
detailed in Table 4.



<!-- page 15/22 -->

Electronics 2025, 14, 4770
15 of 22
Table 4. Decision matrix of experts.
Expert
Alternative
C1
C2
C3
C4
C5
E1
B1
(0.61,
0.61)
(0.69,
0.34)
(0.66,
0.32)
(0.78,
0.16)
(0.62,
0.36)
B2
(0.60,
0.41)
(0.65,
0.41)
(0.81,
0.51)
(0.57,
0.26)
(0.86,
0.82)
B3
(0.47,
0.70)
(0.73,
0.56)
(0.71,
0.43)
(0.44,
0.24)
(0.66,
0.55)
B4
(0.39,
0.47)
(0.72,
0.35)
(0.83,
0.32)
(0.65,
0.54)
(0.84,
0.66)
B5
(0.78,
0.53)
(0.57,
0.67)
(0.75,
0.23)
(0.90,
0.72)
(0.55,
0.58)
E2
B1
(0.55,
0.90)
(0.71,
0.48)
(0.77,
0.07)
(0.78,
0.35)
(0.65,
0.33)
B2
(0.63,
0.36)
(0.49,
0.82)
(0.67,
0.58)
(0.81,
0.23)
(0.39,
0.26)
B3
(0.66,
0.55)
(0.58,
0.73)
(0.74,
0.64)
(0.76,
0.75)
(0.57,
0.52)
B4
(0.84,
0.24)
(0.76,
0.64)
(0.87,
0.51)
(0.82,
0.64)
(0.67,
0.42)
B5
(0.65,
0.37)
(0.60,
0.42)
(0.67,
0.23)
(0.81,
0.68)
(0.79,
0.33)
E3
B1
(0.64,
0.33)
(0.76,
0.42)
(0.66,
0.53)
(0.88,
0.37)
(0.70,
0.23)
B2
(0.82,
0.21)
(0.86,
0.43)
(0.64,
0.23)
(0.79,
0.41)
(0.47,
0.77)
B3
(0.67,
0.48)
(0.81,
0.47)
(0.59,
0.45)
(0.78,
0.44)
(0.39,
0.14)
B4
(0.51,
0.20)
(0.66,
0.41)
(0.81,
0.54)
(0.60,
0.27)
(0.68,
0.55)
B5
(0.71,
0.21)
(0.82,
0.43)
(0.77,
0.54)
(0.84,
0.32)
(0.84,
0.45)
E4
B1
(0.54,
0.22)
(0.46,
0.65)
(0.78,
0.53)
(0.58,
0.43)
(0.73,
0.43)
B2
(0.57,
0.21)
(0.62,
0.40)
(0.85,
0.74)
(0.73,
0.57)
(0.64,
0.31)
B3
(0.58,
0.65)
(0.69,
0.41)
(0.74,
0.31)
(0.38,
0.86)
(0.81,
0.38)
B4
(0.80,
0.60)
(0.60,
0.15)
(0.57,
0.31)
(0.50,
0.65)
(0.70,
0.45)
B5
(0.47,
0.34)
(0.58,
0.23)
(0.65,
0.52)
(0.67,
0.52)
(0.83,
0.32)
To mitigate potential sampling bias caused by the limited number of participating
experts, this study applied 1000 bootstrap iterations to resample the expert evaluation
matrices and calculate confidence intervals for the closeness coefficients of all alternatives.
The results demonstrate that the rankings of all alternatives remain consistent within the
95% confidence interval, indicating the evaluation results exhibit strong robustness.
5.2. Model Application and Analysis
Based on the original expert evaluation data presented in Table 1, and considering
their respective weights (0.3, 0.2, 0.25, 0.25), a collective decision matrix was obtained
through weighted integration. Subsequently, the group evaluation results for the five
power generation schemes were calculated, as shown in Table 5.



<!-- page 16/22 -->

Electronics 2025, 14, 4770
16 of 22
Table 5. Collective decision matrix.
C1
C2
C3
C4
C5
B1
(0.5880,
0.5005)
(0.6540,
0.4655)
(0.7120,
0.3750)
(0.7550,
0.3180)
(0.6735,
0.3390)
B2
(0.6535,
0.3000)
(0.6630,
0.4945)
(0.7495,
0.5115)
(0.7130,
0.3690)
(0.6135,
0.5680)
B3
(0.5855,
0.6025)
(0.7100,
0.5340)
(0.6935,
0.4470)
(0.5740,
0.5470)
(0.6120,
0.3990)
B4
(0.6125,
0.3890)
(0.6830,
0.3730)
(0.7680,
0.4105)
(0.6340,
0.5200)
(0.7310,
0.5320)
B5
(0.6590,
0.3705)
(0.6410,
0.4500)
(0.7140,
0.3800)
(0.8095,
0.5620)
(0.7405,
0.4325)
Based on the group evaluation results in Table 5, the score function S(Y) for each
power generation scheme was first calculated to quantify their overall performance, as
illustrated in Figure 2. On this basis, and according to Equations (39) and (40), the positive
and negative ideal solutions B+ and B−under the Fermatean fuzzy environment were
determined. The results are summarized in Table 6, providing the foundation for the
subsequent distance calculation and scheme ranking.
Figure 2. Score functions of each power generation scheme.
Table 6. Fermatean fuzzy positive ideal solution B+ and negative ideal solution B−.
C1
C2
C3
C4
C5
B+
(0.6535,
0.3000)
(0.6830,
0.3730)
(0.7680,
0.4105)
(0.7550,
0.3180)
(0.7405,
0.4325)
B−
(0.5855,
0.6025)
(0.6630,
0.4945)
(0.6935,
0.4470)
(0.5740,
0.5470)
(0.6135,
0.5680)
To scientifically assess the relative importance of each evaluation indicator in the com-
prehensive assessment process, the FAHP and EWMs were used to calculate the subjective
and objective weights of each indicator, respectively. These were then combined using a
fusion weighting approach with δ = 0.5. The results are presented in Table 7. As shown
in the table, indicator C4 ranks first in both weighting methods, with a combined weight
of 0.3145, indicating that its central role is reinforced by both data variation and expert
consensus. Indicator C3 follows with a weight of 0.242, highlighting the key importance
of the capacity factor in the evaluation. In contrast, C1 has the smallest weight of 0.087,
suggesting a relatively limited influence. Overall, the integrated weighting results strike a



<!-- page 17/22 -->

Electronics 2025, 14, 4770
17 of 22
balance between subjective judgment and objective data, thereby enhancing the scientific
rigor and credibility of the evaluation.
Table 7. Weights of index.
C1
C2
C3
C4
C5
FAHP
0.102
0.191
0.223
0.273
0.211
EWM
0.072
0.130
0.261
0.356
0.181
Integrated weights
0.087
0.1605
0.242
0.3145
0.196
To evaluate the overall performance of each power supply scheme, the FFHWD
distances between each alternative and the Fermatean fuzzy positive and negative ideal
solutions, FFHWD(Bi, B+) and FFHWD(Bi, B−), were first calculated. Based on these results,
a weight vector was determined using an ordered weighted operator derived from the
normal distribution. In this case, the vector was set as (0.112, 0.236, 0.304, 0.236, 0.112)T.
Subsequently, the relative closeness values ς(Bi) were computed to measure how close
each alternative is to the ideal solution. According to the closeness values presented in
Table 8, the five power supply types can be ranked in terms of their techno-economic
performance as follows: Hydropower (B2) exhibits the highest closeness value (–0.4198),
indicating the best overall performance. Photovoltaic power (B4) and thermal power (B1)
rank second and third, respectively. In contrast, wind power (B3) and energy storage (B5)
show relatively low closeness values (–1.8562 and –2.8704, respectively). This suggests that
both technologies are less competitive in the current evaluation framework—particularly
energy storage, which performs poorly across several key indicators, leading to a lower
overall ranking.
Table 8. Integrated weighted distance between alternatives with PIS and NIS.
FFHWD(Bi, B+)
FFHWD(Bi, B−)
ς(Bi)
Ranking
B1
0.0921
0.0979
−0.8736
3
B2
0.0864
0.1521
−0.4198
1
B3
0.1448
0.0829
−1.8562
4
B4
0.0608
0.0767
−0.5003
2
B5
0.2056
0.0827
−2.8704
5
Additionally, to systematically evaluate the impact of parameter δ, we conducted a
sensitivity analysis. Table 9 presents the ranking outcomes of various power generation
types and their corresponding relative closeness values when parameter δ is assigned
different numerical values.
Table 9. Comparison of relative closeness and ranking orders under different parameter values.
δ
ς(B1)
ς(B2)
ς(B3)
ς(B4)
ς(B5)
Ranking Order
δ = 0.1
−0.7504
−0.4042
−1.7762
−0.5211
−2.7086
B2 > B4 > B1 > B3 > B5
δ = 0.3
−0.8078
−0.4148
−1.8304
−0.5176
−2.7853
B2 > B4 > B1 > B3 > B5
δ = 0.5
−0.8736
−0.4198
−1.8562
−0.5003
−2.8704
B2 > B4 > B1 > B3 > B5
δ = 0.7
−0.9386
−0.4257
−1.8869
−0.4762
−2.9437
B2 > B4 > B1 > B3 > B5
δ = 0.9
−1.0113
−0.4319
−1.9101
−0.4537
−3.0216
B2 > B4 > B1 > B3 > B5
This sensitivity analysis demonstrates that the evaluation results exhibit high robust-
ness when parameter δ varies within the range of 0.1 to 0.9: the ranking of the five power
generation types remains consistently B2 > B4 > B1 > B3 > B5 without any positional changes.
As δ increases, the relative closeness values of all alternatives decrease overall, but their



<!-- page 18/22 -->

Electronics 2025, 14, 4770
18 of 22
relative gaps remain stable, confirming the method’s low sensitivity to variations in the
proportion of subjective and objective weighting. Notably, hydropower (B2) consistently
ranks first, while energy storage (B5) shows a significant gap from the optimal solution
(differing by over 2.0), highlighting its current technological and economic disadvantages.
5.3. Comparative Analysis for Model Validation
5.3.1. Comparison of Different Distance Measurement Methods
To verify the effectiveness and superiority of the proposed FFHWD method, a compar-
ative analysis was conducted against two existing distance measures—FWAD and FOWD.
Specifically, in the third step of the evaluation framework, the FWAD and FOWD measures
were, respectively, applied to calculate the distances between each alternative and the
Fermatean fuzzy positive (B+) and negative (B−) ideal solutions. Based on these calcula-
tions, two comparative evaluation frameworks were established, namely FWAD-TOPSIS
and FOWD-TOPSIS. The corresponding relative closeness values of each evaluation object
under the two frameworks were then obtained. The results are presented in Table 10
and Figure 3.
Table 10. Closeness ς(Bi) of the alternative Bi.
B1
B2
B3
B4
B5
ς1(Bi)
−0.4502
−0.1094
−1.1026
−0.5584
−1.9577
ς2(Bi)
−1.3088
−0.4489
−1.8914
−0.1387
−3.4457
-4
-3
-2
-1
0
B5
B4
B3
B2
B1
 FFHWD-TOPSIS
 FFWAD-TOPSIS
 FFOWD-TOPSIS
Figure 3. Relative closeness under different frameworks.
As shown by the ranking results above, the evaluation order obtained by FFWAD-
TOPSIS is B2 > B1 > B4 > B3 > B5, while that of FOWD-TOPSIS is B4 > B2 > B1 > B3 > B5.
The two methods identify B2 and B4 as the optimal alternatives, respectively, and exhibit
noticeable differences in their overall rankings. The main reason lies in their weighting
mechanisms. FFWAD focuses solely on the objective weights of different criteria and fails
to incorporate the experts’ subjective judgments. In contrast, FOWD captures the sub-
jective preferences of decision-makers but overlooks the inherent importance differences
among indicators. By comparison, the FFHWD method proposed in this study integrates
the strengths of both bounded and arithmetic weighting schemes. It effectively balances
subjective and objective information, thereby achieving more comprehensive data inte-
gration in the evaluation process and enhancing the rationality and stability of the final
ranking results.



<!-- page 19/22 -->

Electronics 2025, 14, 4770
19 of 22
5.3.2. Comparison of Different Evaluation Methods
To thoroughly validate the validity and robustness of the proposed FFHWD-TOPSIS
evaluation method, a systematic comparison is conducted against three widely adopted
multi-criteria decision-making (MCDM) approaches in the field of energy system assess-
ment: the VIKOR method based on the compromise solution principle, the MARCOS
method integrating reference ideal solutions, and the classical hierarchical weighting
AHP method. Table 11 summarizes the ranking outcomes of alternatives derived from
these methods.
Table 11. Comparative results of different evaluation methods.
Evaluation Method
Ranking Result
VIKOR
B2 > B1 > B4 > B3 > B5
MARCOS
B2 > B4 > B1 > B3 > B5
AHP
B2 > B1 > B3 > B4 > B5
FFHWD-TOPSIS
B2 > B4 > B1 > B3 > B5
The comparative results show that all four methods consistently rank hydropower (B2)
as the top choice and energy storage (B5) as the least preferred, validating the consensus
in evaluation outcomes. The primary discrepancy lies in the ranking of thermal power
(B1) and photovoltaics (B4): VIKOR and AHP prioritize thermal power over photovoltaics,
whereas MARCOS and the proposed FFHWD-TOPSIS method yield superior rankings
for photovoltaics. This discrepancy arises from the proposed method’s use of Fermatean
fuzzy sets to effectively capture higher-order uncertainties in evaluation information,
combined with a hybrid weighted distance measure that simultaneously accounts for
indicator importance and decision-makers’ risk preferences. This dual mechanism enhances
the scientific rigor of weight assignment and the rationality of distance calculations, thereby
improving the robustness and interpretability of the ranking results. In contrast, traditional
methods exhibit limitations in handling fuzziness and integrating weights, making them
more prone to ranking biases.
Although the FFHWD-TOPSIS framework and the MARCOS method generate iden-
tical ranking outcomes in this specific numerical case, this consistency does not indicate
equivalent modeling capabilities or decision robustness between the two approaches. The
alignment in final rankings primarily results from the strong dominance relationships
among the five alternatives across multiple critical criteria. These inherently stable ranking
patterns can be captured by diverse multi-criteria decision-making techniques. More im-
portantly, the methodological strengths of the FFHWD-TOPSIS approach extend beyond
consistent results in a single dataset, manifesting more significantly in the following aspects:
(1)
Enhanced higher-order uncertainty handling capability. While the MARCOS method
relies on standardized deterministic numerical inputs, FFHWD-TOPSIS explicitly in-
corporates Fermatean fuzzy membership degrees, non-membership degrees, and hesi-
tation margins, enabling a more expressive representation of fuzzy expert knowledge.
(2)
Integrated hybrid weighting mechanism combining subjective and objective elements.
The FFHWD measure simultaneously considers both inherent criterion importance
and positional risk preferences, overcoming the purely data-driven limitations of
MARCOS and effectively mitigating weight conflict sensitivity issues.
(3)
Superior ranking stability under parameter and data perturbations. As demonstrated
in the sensitivity analysis, our approach maintains ranking robustness across varia-
tions in mixed weight proportions, whereas the MARCOS method lacks this flexible
robustness modeling capability.



<!-- page 20/22 -->

Electronics 2025, 14, 4770
20 of 22
In summary, FFHWD-TOPSIS does not merely pursue numerical discrepancies with
classical approaches on isolated datasets, but demonstrates superior generalization poten-
tial and expanded modeling capabilities in handling multi-source uncertainties, conflicting
criteria integration, and disturbance resistance. The core objective of this comparative anal-
ysis is not to assert universal numerical superiority, but to validate that even under strong
dominance structures, the proposed method can generate consistent and interpretable
stable outcomes comparable to established MCDM techniques, while equipping evaluators
with extended capabilities to address more complex fuzzy environments. This dual advan-
tage constitutes its critical practical value in multi-type power generation assessment for
next-generation power systems.
6. Conclusions
This study introduces a novel TOPSIS-based framework (FFHWD-TOPSIS) that in-
tegrates Fermatean fuzzy sets with a hybrid weighted distance measure and a combined
FAHP–EWM weighting strategy, addressing higher-order uncertainty and weight conflicts
in techno-economic evaluation. The FFHWD measure captures both subjective importance
and decision-maker risk preferences and is integrated into an improved TOPSIS model via
Fermatean fuzzy positive and negative ideal solutions.
(1)
Performance ranking: The FFHWD-TOPSIS model was applied to five representative
power sources (thermal, hydropower, wind, photovoltaic, and energy storage) using
expert evaluations. The computed closeness coefficients rank hydropower (B2) highest
in overall performance (best techno-economic score), with photovoltaic (B4) and
thermal power (B1) in second and third place, respectively. In contrast, wind power
(B3) and energy storage (B5) have much lower closeness values and thus appear less
competitive under the current evaluation framework.
(2)
Comparative analysis: Compared to existing Fermatean-fuzzy TOPSIS variants using
FWAD or FOWD distance measures, the proposed FFHWD-TOPSIS yields more bal-
anced and stable rankings. By effectively blending objective and subjective weighting
information, the method enhances the rationality and consistency of the final ranking.
These findings demonstrate that the FFHWD-TOPSIS framework provides reli-
able, nuanced decision support for optimizing multi-type power source configurations
under uncertainty.
Author Contributions: Conceptualization, L.Y., S.Y. and L.J.; methodology, J.L. (Jichuan Li); vali-
dation, L.Y. and L.J.; formal analysis, B.X.; resources, S.Y.; data curation, J.L. (Jichuan Li); writing—
original draft preparation, L.J.; writing—review and editing, L.Y.; visualization, B.X.; supervision, J.L.
(Jing Liao); project administration, S.Y. All authors have read and agreed to the published version of
the manuscript.
Funding: This research was funded by State Grid Hunan Electric Power Company Science and
Technology Project (5216A2250006).
Data Availability Statement: The data is included in the article.
Conflicts of Interest: Authors Lun Ye, Jing Liao and Binkun Xu were employed by the company State
Grid Hunan Electric Power Company Limited Economic & Technical Research Institute. Authors
Jichuan Li and Lei Jiang were employed by the company Hunan Power Exchange Center Co., Ltd.
The remaining author declares that the research was conducted in the absence of any commercial or
financial relationships that could be construed as a potential conflict of interest.



<!-- page 21/22 -->

Electronics 2025, 14, 4770
21 of 22
References
1.
Srettiwat, N.; Safari, M.; Olcay, H.; Malina, R. A techno-economic evaluation of solar-powered green hydrogen production for
sustainable energy consumption in Belgium. Int. J. Hydrogen Energy 2023, 48, 39731–39746. [CrossRef]
2.
Brumana, G.; Franchini, G.; Ghirardi, E.; Perdichizzi, A. Techno-economic optimization of hybrid power generation systems:
A renewables community case study. Energy 2022, 246, 123427. [CrossRef]
3.
Shakeel, M.R.; Mokheimer, E.M. A techno-economic evaluation of utility scale solar power generation. Energy 2022, 261, 125170.
[CrossRef]
4.
Liu, T.; Yang, J.; Yang, Z.; Duan, Y. Techno-economic feasibility of solar power plants considering PV/CSP with electrical/thermal
energy storage system. Energy Convers. Manag. 2022, 255, 115308. [CrossRef]
5.
Meng, F.; Chen, X.; Zhang, Y. Consistency-based linear programming models for generating the priority vector from interval
fuzzy preference relations. Appl. Soft Comput. 2016, 41, 247–264. [CrossRef]
6.
Tan, C.; Chen, X. Generalized archimedean intuitionistic fuzzy averaging aggregation operators and their application to
multicriteria decision-making. Int. J. Inf. Technol. Decis. Mak. 2016, 15, 311–352. [CrossRef]
7.
Younis, M.; Ashraf, S.; Abdullah, S.; Shahid, T.; KC, G. Strategic MARCOS model for optimizing renewable energy investments
under Pythagorean hesitant fuzzy assessments. Adv. Fuzzy Syst. 2025, 1, 6193403. [CrossRef]
8.
Chen, H.; Sun, W.; Zou, X.; Hu, D.; Yu, T.; Shao, W. Evaluation method of power source reaching service term based on fuzzy
analytical Hierar-chy process and the entropy weight method. J. Power Supply 2025, 23, 290–297.
9.
Li, N.; Zhao, H. Performance evaluation of eco-industrial thermal power plants by using fuzzy GRA-VIKOR and combination
weighting techniques. J. Clean. Prod. 2016, 135, 169–183. [CrossRef]
10.
Senapati, T.; Yager, R.R. Fermatean fuzzy weighted averaging/geometric operators and its application in multi-criteria decision-
making methods. Eng. Appl. Artif. Intell. 2019, 85, 112–121. [CrossRef]
11.
Büyüközkan, G.; Uztürk, D.; Ilıcak, Ö. Fermatean fuzzy sets and its extensions: A systematic literature review. Artif. Intell. Rev.
2024, 57, 138. [CrossRef]
12.
Deng, Z.; Wang, J. New distance measure for Fermatean fuzzy sets and its application. Int. J. Intell. Syst. 2022, 37, 1903–1930.
[CrossRef]
13.
Gul, M.; Lo, H.W.; Yucesan, M. Fermatean fuzzy TOPSIS-based approach for occupational risk assessment in manufacturing.
Complex Intell. Syst. 2021, 7, 2635–2653. [CrossRef]
14.
Yang, S.; Pan, Y.; Zeng, S. Decision making framework based Fermatean fuzzy integrated weighted distance and TOPSIS for
green low-carbon port evaluation. Eng. Appl. Artif. Intell. 2022, 114, 105048. [CrossRef]
15.
Zeng, S.; Gu, J.; Peng, X. Low-carbon cities comprehensive evaluation method based on Fermatean fuzzy hybrid distance measure
and TOPSIS. Artif. Intell. Rev. 2023, 56, 8591–8607. [CrossRef]
16.
Liu, D.; Liu, Y.; Chen, X. The new similarity measure and distance measure of a hesitant fuzzy linguistic term set based on a
linguistic scale function. Symmetry 2018, 10, 367. [CrossRef]
17.
Li, X.; Pan, L.; Zhang, J. Development status evaluation and path analysis of regional clean energy power generation in China.
Energy Strategy Rev. 2023, 49, 101139. [CrossRef]
18.
Qi, L.; Dou, W.; Hu, C.; Zhou, Y.; Yu, J. A context-aware service evaluation approach over big data for cloud applications. IEEE
Trans. Cloud Comput. 2015, 8, 338–348. [CrossRef]
19.
Yang, Y.; Yang, F.; Chen, J.; Zeng, Y.; Liu, L. Pythagorean fuzzy Bonferroni mean with weighted interaction operator and its
application in fusion of online multidimensional ratings. Int. J. Comput. Intell. Syst. 2022, 15, 94. [CrossRef]
20.
Liu, L.; Bin, Z.; Shi, B.; Cao, W. Sustainable supplier selection based on regret theory and QUALIFLEX method. Int. J. Comput.
Intell. Syst. 2020, 13, 1120–1133. [CrossRef]
21.
Liu, J.; Chen, H.; Zhao, S.; Pan, P.; Wu, L.; Xu, G. Evaluation and improvements on the flexibility and economic performance of a
thermal power plant while applying carbon capture, utilization & storage. Energy Convers. Manag. 2023, 290, 117219. [CrossRef]
22.
Xu, X.; Pan, B.; Yang, Y. Large-group risk dynamic emergency decision method based on the dual influence of preference transfer
and risk preference. Soft Comput.-A Fusion Found. Methodol. Appl. 2018, 22, 7479–7490. [CrossRef]
23.
Wang, Y.; Lee, S.; Li, C.; Umair, M.; Yakhyaeva, I. Techno-economic evaluation of solar photovoltaic power production in China
for sustainable development and the environment. Environ. Dev. Sustain. 2024, 1–30. [CrossRef]
24.
Braga, I.F.; Ferreira, F.A.; Ferreira, J.J.; Correia, R.J.; Pereira, L.F.; Falcão, P.F. A DEMATEL analysis of smart city determinants.
Technol. Soc. 2021, 66, 101687. [CrossRef]
25.
Gedam, V.V.; Raut, R.D.; Priyadarshinee, P.; Chirra, S.; Pathak, P.D. Analysing the adoption barriers for sustainability in the
Indian power sector by DEMATEL approach. Int. J. Sustain. Eng. 2021, 14, 471–486. [CrossRef]
26.
Zhang, J.; Li, J.; You, J. Research on influencing factors of cost control of centralized photovoltaic power generation project based
on DEMATEL-ISM. Sustainability 2024, 16, 5289. [CrossRef]
27.
Kara, E.; Onat, M.R.; Demir, M.E.; Kinaci, O.K. Techno-economic analysis of offshore renewable energy farms in Western Spain
using fuzzy AHP & TOPSIS methodology. Renew. Energy 2025, 242, 122361. [CrossRef]



<!-- page 22/22 -->

Electronics 2025, 14, 4770
22 of 22
28.
Heo, E.; Kim, J.; Boo, K.J. Analysis of the assessment factors for renewable energy dissemination program evaluation using fuzzy
AHP. Renew. Sustain. Energy Rev. 2010, 14, 2214–2220. [CrossRef]
29.
Li, X.; Chen, X. D-intuitionistic hesitant fuzzy sets and their application in multiple attribute decision making. Cogn. Comput.
2018, 10, 496–505. [CrossRef]
30.
Meng, F.; Tang, J.; Wang, P.; Chen, X. A programming-based algorithm for interval-valued intuitionistic fuzzy group decision
making. Knowl. -Based Syst. 2018, 144, 122–143. [CrossRef]
31.
Li, X.; Chen, X. Value determination method based on multiple reference points under a trapezoidal intuitionistic fuzzy
environment. Appl. Soft Comput. 2018, 63, 39–49. [CrossRef]
32.
Ma, X.; Zhao, Z. Investment efficiency evaluation of electric power substation projects by stages using the EWM-DEA model. Int.
J. Ind. Syst. Eng. 2024, 46, 34–57. [CrossRef]
33.
Chen, Z.S.; Yang, Y.; Wang, X.J.; Chin, K.S.; Tsui, K.L. Fostering linguistic decision-making under uncertainty: A proportional
interval type-2 hesitant fuzzy TOPSIS approach based on Hamacher aggregation operators and andness optimization models. Inf.
Sci. 2019, 500, 229–258. [CrossRef]
34.
Afrane, S.; Ampah, J.D.; Jin, C.; Liu, H.; Aboagye, E.M. Techno-economic feasibility of waste-to-energy technologies for investment
in Ghana: A multicriteria assessment based on fuzzy TOPSIS approach. J. Clean. Prod. 2021, 318, 128515. [CrossRef]
35.
Göçer, F. A novel extension of Fermatean fuzzy sets into group decision making: A study for prioritization of renewable energy
technologies. Arab. J. Sci. Eng. 2024, 49, 4209–4228. [CrossRef]
36.
Bouraima, M.B.; Ayyildiz, E.; Qian, S.; Aydin, N. A robust three-dimensional Fermatean fuzzy approach for comprehensive
strategy selection for photovoltaic energy development. Environ. Dev. Sustain. 2025, 1–40. [CrossRef]
37.
Yang, Y.; Chen, Z.S.; Chen, Y.H.; Chin, K.S. Interval-valued Pythagorean fuzzy Frank power aggregation operators based on an
isomorphic Frank dual triple. Int. J. Comput. Intell. Syst. 2018, 11, 1091–1110. [CrossRef]
38.
Ren, J.; Hu, C.H.; Yu, S.Q.; Cheng, P.F. An extended EDAS method under four-branch fuzzy environments and its application in
credit evaluation for micro and small entrepreneurs. Soft Comput. 2021, 25, 2777–2792. [CrossRef]
39.
Liu, D.; Chen, X.; Peng, D. Cosine distance measure between neutrosophic hesitant fuzzy linguistic sets and its application in
multiple criteria decision making. Symmetry 2018, 10, 602. [CrossRef]
40.
Xu, Z.; Xia, M. Distance and similarity measures for hesitant fuzzy sets. Inf. Sci. 2011, 181, 2128–2138. [CrossRef]
41.
Donghai, L.; Yuanyuan, L.; Xiaohong, C. The new similarity measure and distance measure between hesitant fuzzy linguistic
term sets and their application in multi-criteria decision making. J. Intell. Fuzzy Syst. 2019, 37, 995–1006. [CrossRef]
42.
Meng, F.; Chen, X. The symmetrical interval intuitionistic uncertain linguistic operators and their application to decision making.
Comput. Ind. Eng. 2016, 98, 531–542. [CrossRef]
Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
