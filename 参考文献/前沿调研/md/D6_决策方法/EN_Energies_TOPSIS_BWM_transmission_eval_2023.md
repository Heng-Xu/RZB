<!--
source: D6_决策方法/EN_Energies_TOPSIS_BWM_transmission_eval_2023.pdf
sha256: f5d642f207e15bbf960e4a1a8c1a5824c421918de52eeb977720408d5e78fc7e
method: pymupdf
pages: 21
-->

<!-- page 1/21 -->

Citation: Zeng, W.; Fan, J.; Ren, Z.;
Liu, X.; Lv, S.; Cao, Y.; Xu, X.; Liu, J.
Economic Evaluation Method of
Modern Power Transmission System
Based on Improved Technique for
Order of Preference by Similarity to
Ideal Solution (TOPSIS) and
Best-Worst Method-Anti-Entropy
Weight. Energies 2023, 16, 7242.
https://doi.org/10.3390/en16217242
Academic Editor: Oscar Duque-Perez
Received: 4 September 2023
Revised: 20 October 2023
Accepted: 23 October 2023
Published: 25 October 2023
Copyright:
© 2023 by the authors.
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
Article
Economic Evaluation Method of Modern Power Transmission
System Based on Improved Technique for Order of Preference
by Similarity to Ideal Solution (TOPSIS) and Best-Worst
Method-Anti-Entropy Weight
Wenhui Zeng 1, Jiayuan Fan 2, Zhichao Ren 1, Xiaoyu Liu 1, Shuang Lv 3, Yuqian Cao 4,*, Xiao Xu 4
and Junyong Liu 4
1
State Grid Sichuan Economic Research Institute, Chengdu 610095, China
2
State Grid Sichuan Information & Communication Company, Chengdu 610299, China
3
State Grid Sichuan Electric Power Company Chengdu Power Supply, Chengdu 610041, China
4
School of Electrical Engineering, Sichuan University, Chengdu 610017, China
*
Correspondence: caopinno@gmail.com
Abstract: As the demand for power supply increases, the investment in the power transmission
system constantly increases. An accurate economic evaluation of the power transmission system is
essential for future investment decisions and management. Applying a single method in economic
evaluation leads to excessive subjective consciousness and unreasonable weight allocation. The
Euclidean distance in the traditional TOPSIS method only partially works on the condition that the
criteria are linearly correlated. To solve these problems, an economic evaluation method based on
improved TOPSIS and BWM-anti-entropy weight is proposed. For the assignment of weights, the
method retains the advantages of subjective and objective weighting methods based on the Nash
equilibrium, breaks through the limitation of utilizing a single method, which contributes to one-sided
results, and enhances the scientiﬁc rigor and rationality of the comprehensive weighting process.
Furthermore, based on comprehensive weights, the method improves the TOPSIS by introducing the
Mahalanobis distance and Pearson correlation coefﬁcients, which can eliminate the inﬂuence of linear
correlation. Finally, ten 500 kV transmission and transformation projects are analyzed and ranked to
verify the method’s feasibility. Empirical analysis shows that the method can effectively evaluate the
economic beneﬁts of the power transmission system.
Keywords: power transmission system; economic evaluation; best-worst method (BWM); anti-
entropy weight method; Nash equilibrium; improved TOPSIS
1. Introduction
Energy and environmental problems are becoming increasingly prominent, and elec-
trical energy is an indispensable secondary energy source in society. As the industry has
progressed in recent years, electricity consumption has steadily increased, resulting in
elevated demands for power supply reliability and safety. The power transmission system
is an integral part of the electric power system—which includes transmission lines, sub-
stations, and related equipment—inﬂuencing the quality of power supply and economic
and social development. The power transmission system has a signiﬁcant investment scale
and a long construction period [1]. Therefore, the economics of power system projects in
terms of proﬁtability, liabilities, etc. need to be quantiﬁed and comprehensively evaluated
for managerial decision-making and planning.
A comprehensive evaluation uses scientiﬁc, feasible methods to evaluate and analyze
all aspects of the evaluation: object behavior, multi-indicator, and multi-level. Some studies
have concluded that the economic evaluation of the power transmission system focuses
Energies 2023, 16, 7242. https://doi.org/10.3390/en16217242
https://www.mdpi.com/journal/energies



<!-- page 2/21 -->

Energies 2023, 16, 7242
2 of 21
on cost and beneﬁt. Based on the cost–beneﬁt analysis, the scores for multiple power
transmission systems can be calculated and ranked [2]. According to the characteristics of
the power system project, the economic evaluation of the project is divided into two parts:
ﬁnancial analysis and economic cost-effectiveness analysis [3]. Subsequently, increasing
numbers of people are researching and improving the evaluation system and criteria for
power transmission systems. A two-tier indicator system for investment effectiveness
evaluation was established, considering both unit- and macro-investment effectiveness [4].
To combine the metrics of investment effectiveness and investment efﬁciency, the criteria of
comprehensive economic evaluation can be categorized into basic, modiﬁed, and appraisal
criteria [5]. Existing research provides an important reference for the economic evaluation
of the power system in this paper. This paper considers the three perspectives of time,
value, and efﬁciency to establish a comprehensive evaluation system from the three aspects
of proﬁtability, solvency, and development capability.
Regarding models and methods for the economic evaluation of power transmission
systems, many relevant research studies already exist in the ﬁeld of MCDA. Multi-criteria
decision analysis (MCDA) is a complex ﬁeld of decision-making disciplines for problems
with multiple criteria and multiple choices that can be used for economic evaluation [6]. The
core methods and techniques are WSM, TOPSIS, AHP, PROMETHEE, ELECTRE, COMET,
and SIMUS [7]. The weighted sum method (WSM) is the most commonly used [8] for
assessment and decision-making in a single dimension. The analytical hierarchy process
(AHP) uses a hierarchical structure to decompose a complex problem to evaluate the
objectives at the top of the structure [9]. The ELECTRE method can be iterated to provide a
ranking of alternatives based on consistency and thresholds [10]. The combined approaches
are also proposed, and some previous research conducted a comprehensive analysis by
establishing a fuzzy synthetic evaluation model using the hierarchical analysis method [11].
Pareto optimal function and merit criterion methods are also employed to enhance project
comparison and decision-making [12,13]. In the study [14], which optimizes the fuzzy
synthetic evaluation model, a hierarchy evaluation model for fuzzy analysis is built based
on a novel comprehensive fuzzy evaluation operator. However, this model relies too much
on subjectivity. A combination of the entropy weighting method and gray correlation
analysis is employed to address the challenges posed by incomplete information and the
subjective nature of weights. Then, the improved gray correlation analysis method is used
to arrive at the optimal solution [15]. Based on the content and characteristics of speciﬁc
projects in the power system, this paper proposes the improved TOPSIS method. TOPSIS
is a multi-criteria decision analysis method that can be used to evaluate objects across
multiple areas with satisfactory results [16]. The original TOPSIS method is likely to lead
to the problem of rank reversal when changing the number of items to be evaluated [17],
and the TOPSIS method can be improved by introducing the absolute ideal solution [18,19].
The absolute ideal solution provides initial support for our improvements to TOPSIS. We
ﬁnd that indicators are often correlated, and that correlation leads to partial failure of the
Euclidean distance in traditional TOPSIS [20,21]. Although many methods and software
have been applied to build evaluation systems and accurately evaluate the economics of
power transmission systems, few weights can balance subjective experience and objective
data.
Previous studies have often used single-dimension weights to evaluate economics,
with some articles considering only subjective weights [22,23] (AHP, BWM), and some
articles considering only objective weights [24,25](EWM, PCA). Combinations of subjective
and objective methods are also often used in the ﬁeld of evaluation [26,27]. The construction
of the coupling coordination model is dependent on the coordination of weights estimated
by AHP and EWM methods [28]. In the paper [29], a novel hybrid multi-criteria decision-
making (MCDM) approach is devised for offshore wind turbine selection by assignment
of weights using ANP and EWM. Given the limitations of assigning weights to a single
dimension, we propose the BWM-anti-entropy weight method in this paper, which utilizes



<!-- page 3/21 -->

Energies 2023, 16, 7242
3 of 21
a game theory model to balance subjective and objective weights. Game theory models can
ultimately result in more efﬁciently comprehensive weights [30].
In summary, based on comprehensive weights and absolute ideal solutions, the TOP-
SIS method can be improved using the Mahalanobis distance and Pearson’s correlation
coefﬁcient. This ﬁnal improved TOPSIS method is more scientiﬁc and logical.
The key processes of the improved TOPSIS method are illustrated in Figure 1.
Economic evaluation flowchart
Raw data
Data pre-
processing
Objective 
weights
Subjective 
weights
Comprehensive 
weights
Improved 
TOPSIS
Economic
evaluation
ranking
Importance 
scoring
Pearson correlation
coefficient
Weighted 
Mahalanobis
distance
Ideal solution
 
Figure 1. Economic evaluation ﬂowchart.
Other contents are organized as follows: The economic evaluation system of power
transmission systems is constructed in Section 2, focusing on three aspects and determining
the speciﬁc evaluation criteria. In Section 3, the subjective weights and objective weights are
calculated, then an integrated weighting model is established by applying the game theory.
Section 4 outlines the deﬁciencies of the traditional TOPSIS method and introduces the
improved TOPSIS method utilizing the Mahalanobis distance and Pearson coefﬁcient. In
Section 5, the comparison analysis is carried out on the speciﬁc data of 500 kV transmission
and transformation projects to acquire the evaluation results for the proposed criterion
system, model, and improved method.
2. The System of Criteria for Economic Evaluation
The comprehensive evaluation of economic efﬁciency in this paper is based on the
ﬁnancial evaluation criterion system.
According to the characteristics of the power transmission system and the theory
of ﬁnancial evaluation criteria, this paper establishes the evaluation system from three
perspectives: ﬁnancial proﬁtability, ﬁnancial solvency, and ﬁnancial development capabil-
ity [31]. The evaluation of comprehensive economic efﬁciency is carried out mainly from
the perspectives of time, value, and efﬁciency [32,33], and these three perspectives are
substantially equivalent, which means that many of the criteria are consistent at their core.
Under each perspective, the appropriate criteria should be selected for the description.
The information on different criteria is used for the economic evaluation of the power
transmission system. The speciﬁc criteria system is shown in Table 1.
Table 1. Economic evaluation criteria system.
Level Target
Level 1 Criteria
Level 2 Criteria
Criteria Code
Criteria Type
Economic evaluation
method of the power
transmission system
Financial Proﬁtability
Return on Investment
C1
Forward
Net Present Value
C2
Forward
Payback Period
C3
Backward
Internal Rate of Return
C4
Forward



<!-- page 4/21 -->

Energies 2023, 16, 7242
4 of 21
Table 1. Cont.
Level Target
Level 1 Criteria
Level 2 Criteria
Criteria Code
Criteria Type
Financial Solvency
Asset Liability Ratio
C5
Backward
Current Ratio
C6
Intermediate Value
Financial Development
Capability
Proﬁt Growth Rate
C7
Forward
1.
Return on Investment (ROI)
ROI is a performance assessment used to evaluate the efﬁciency of an investment or to
compare the efﬁciency of many different investments. ROI directly measures the amount
of return on a particular investment relative to the cost of the investment. The ratio and
proﬁtability of the power transmission system have a signiﬁcant positive correlation. The
calculation formula is deﬁned as shown in Equation (1) [34]:
ROI = A
I × 100%
(1)
where A is Annual net income, I is total investment (including construction investment
and working capital).
2.
Net Present Value (NPV)
Net present value (NPV) is the equivalent present value of the net cash ﬂow for
each year of the power transmission system life cycle discounted at a given discount rate,
calculated as shown in Equation (2) [34]:
NPV =
n
∑
t=0
(CI −CO)(1 + ic)−t
(2)
where CI is cash inﬂows by year, CO is cash outﬂows by year, n is the whole life cycle of
the power transmission system, including the construction period and operation period.
3.
Payback Period (Pt)
The payback period is the time required to recover the entire investment in a power
transmission system in terms of its net income, usually in years. The payback period
ends when a transmission system’s net beneﬁts equal the total initial investment. This
number of years to recover the investment. This paper uses a static payback period without
considering the time value. The formula is expressed in Equation (3) [34]:
∑(CI −CO)t = 0 t = 1 · · · · · · Pt
(3)
where CI −CO is net cash ﬂow.
4.
Internal Rate of Return (IRR)
The internal rate of return (IRR) is the discount rate when the cumulative present
value of the net cash ﬂow over the life cycle of the power transmission system is zero.
Internal rate of return (IRR) is the main dynamic evaluation criterion used to examine the
proﬁtability of the power transmission system, reﬂecting the proﬁtability of the whole
investment during its life. This is given by Equation (4) [34]:
n
∑
t=0
(CI −CO)(1 + IRR)−t = 0
(4)
where CI −CO is net cash ﬂow, n is the whole life cycle of the power transmission system,
including the construction period and operation period.



<!-- page 5/21 -->

Energies 2023, 16, 7242
5 of 21
5.
Asset Liability Ratio (ALR)
Asset liability ratio refers to the percentage of total liabilities to total assets, reﬂecting
the degree of ﬁnancial risk and the liabilities of power transmission systems. This is given
by Equation (4) [34]:
ALR = TL
TA × 100%
(5)
where TL is total liabilities, TA is total assets.
6.
Current Ratio (CR)
The current ratio reﬂects the ability of the power transmission system to repay the
current outstanding liabilities each year. It is an essential indicator of the short-term
solvency of the power transmission system. The calculation formula [34] is:
Current Ratio =
Current Assets
Current Liabilities × 100%
(6)
7.
Proﬁt Growth Rate
The proﬁt growth rate refers to the growth rate of the net proﬁt of the power transmis-
sion system in the current period compared with the net proﬁt in the previous period, and
the larger the indicator’s value, the stronger the proﬁtability [34].
Proﬁt Growth Rate =
Net proﬁt for the period
Net proﬁt of the previous period × 100%
(7)
The economic evaluation criteria system is shown in Figure 2.
Financial 
Profitability
Economic Evaluation
Financial 
Solvency
Financial 
Development 
Capability
Return 
On 
Invest
ment
Net 
Present 
Value
Payback 
Period
Current 
Ratio
Internal 
Rate Of 
Return
Profit 
Growth 
Rate
Asset 
Liability 
Ratio
 
Figure 2. Economic evaluation criteria system.
3. Comprehensive Weighting Solution Model
3.1. Subjective Weight Solving Based on the BWM Method
The BWM is proposed to determine the subjective weights of the criteria [35]. In
the past, the most common method was the AHP method, which compares any two
indicators with each other to determine the evaluation matrix of the indicators. This
requires n(n −1)/2 comparisons to determine the n2 −n data [36]. Compared to the
AHP method, the BWM is less cumbersome and data-intensive, reducing errors caused



<!-- page 6/21 -->

Energies 2023, 16, 7242
6 of 21
by confused thinking. The BWM makes it easier to pass the consistency test, making the
results more reliable [37].
The BWM (best-worst method) is frequently used in multi-criteria decision-making [38].
Experts select the most important and least important criteria based on experience and
practical engineering needs, then compare the best criterion with the rest of the criteria,
and then compare the worst criterion with the rest. An integer value of 1–9 reﬂects the
relative signiﬁcance among the indicators. The speciﬁc procedures are as follows:
STEP 1: Identify the inﬂuencing factors of multi-criteria evaluation issues and establish
a set of criteria {c1, c2, · · · , cn} based on the inﬂuencing factors of different aspects.
STEP 2: Identify the most important criterion and the least important criterion.
STEP 3: Compare the best, worst, and other criteria separately to create two vectors that
characterize relative preferences. AB = (aB1, aB2, · · · , aBn), AW = (a1W, a2W, · · · , anW).
For the criteria system of the power transmission system, two scoring tables are
established, as shown in Tables 2 and 3.
Table 2. Scoring the relative importance of the best criterion.
c1
c2
c3
. . .
c7
CB
aB1
aB2
aB3
. . .
aB7
Table 3. Scoring the relative importance of the worst criterion.
c1
c2
c3
. . .
c7
CW
a1W
a2W
a3W
. . .
a4W
STEP 4: Build a mathematical subjecting model and ﬁnd the best solution to obtain
the objective optimal weights. The mathematical planning [35] is as follows:
s.t.

















 ωB
ωj −aBj
 ⩽l

ωj
ωW −ajW
 ⩽l, j = 1, 2, · · · , n
n
∑
j=1
ωj = 1
ωj ⩾0
(8)
where ωB is the weight of CB, ωj is the weight of the base vector Cj, i.e., the actual weight
of the criteria, ωW is the weight of CW, aBj is the value of the importance of CB relative to
Cj, ajW is the value of the importance of Cj relative to CW.
STEP 5: Use the following formula [35] to calculate CR; CR = 0 represents complete
consistency. The closer it is to 0, the better the consistency.
CR = l∗
CI
(9)
where the l obtained by Equation (8) is called l∗, CI is a constant.
3.2. Objective Weight Solving Based on the Anti-Entropy Method
The entropy value is frequently mentioned when seeking objective weights in multi-
criteria decision-making models. Both entropy and anti-entropy methods share a key
feature: they solve for objective weights [39]. These two approaches both believe that the
volatility in the data of a criterion is positively correlated with its weight. If this criterion is
approximately equal for each power transmission system, then the weight corresponding
to this criterion should be small. The essence of information entropy is the expected value
of the amount of information.



<!-- page 7/21 -->

Energies 2023, 16, 7242
7 of 21
The entropy method has been improved to become the anti-entropy method. It has
the characteristic that the stronger the volatility of the criterion, the smaller the entropy
value and the larger the weight coefﬁcient [40]. The speciﬁc procedure of the anti-entropy
weight method is as follows:
STEP 1: The initial matrix must be created and normalized for a comprehensive
evaluation model with subjects of evaluation and criteria.
The matrix with m subjects and n criteria is X =
 xij

m×n:
X =


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


(10)
The initial matrix is normalized using the vector normalization method:
rij =
xij
s
m
∑
i=1
x2
ij
(11)
The matrix is normalized to eliminate the effect of the physical dimensions, and the
normalized matrix R is obtained.
R =


r11
r12
· · ·
r1n
r21
r22
· · ·
r2n
...
...
...
...
rm1
rm2
· · ·
rmn


(12)
STEP 2: Calculate the share of the i subject under the j criterion and consider it as the
probability used in the relative entropy calculation.
pij =
xij
m
∑
i=1
xij
(13)
where pij is considered as the probability of the i subject under the j criterion.
The anti-entropy ej is calculated in Equation (14) [25]:
ej = −
1
ln m
m
∑
i=1
pij ln(1 −pij)
(14)
For each criterion, its objective weight is calculated in Equation (15) [25]:
ωS
j =
1 −ej
n −
n
∑
i=1
ej
, j = 1, 2, · · · , n
(15)
where ωS
j is the anti-entropy weight of the criterion j.
3.3. Coordination of Subjective and Objective Weights Based on Game Theory
Subjective weighting methods such as BWM depend heavily on experts’ personal
experiences and ideas and have some limitations. The objective weighting method is based
on the data but may deviate from the actual situation. The BWM-anti-entropy weighting
method is combinatorial. It is based on game theory’s ideology and considers subjective
and objective weights. The BWM-anti-entropy weighting method regroups the two sets of
weights into a more scientiﬁc and reasonable combined weighting.



<!-- page 8/21 -->

Energies 2023, 16, 7242
8 of 21
The comprehensive weighting method, which averages the two sets of weights, is
unreasonable and does not effectively eliminate the shortcomings of the two weighting
methods. Using game theory, this method takes Nash equilibrium as the optimum goal,
coordinates the two sets of weights to ﬁnd a balance, and makes the discrepancy between
the ﬁnal comprehensive weights and the two original sets of weights as minimal as possible
to derive a set of more scientiﬁc comprehensive weights.
STEP 1: Obtain the weights of each criterion by subjective and objective methods,
respectively. A basic set of weights u = {u1, u2, . . . , ul} is constructed based on this. The
arbitrary linear combination of these vectors constructs the set of comprehensive weights.
u =
2
∑
k=1
gkuT
k , gk > 0
(16)
where u1 is the subjective weight, u2 is the objective weight, gk and is the linear coefﬁcient
that needs to be optimized using the model.
STEP 2: Optimize gk using a game-theoretic model that minimizes the deviation u
from each uk. The following policy response model [41] is used:
min∥u −ui∥2(i = 1, 2)
(17)
STEP 3: Utilize the differential property to convert the matrix constraints for the
optimal solution:
u1uT
1
u2uT
1
u2uT
1
u2uT
2
g1
g2

=
u1uT
1
u2uT
2

(18)
Solve the equation (g1, g2, . . . , gl) normalization process:
g∗
k = gk/
2
∑
k=1
gk
(19)
u∗=
2
∑
k=1
g∗
k · uT
k
(20)
Optimization problems such as comprehensive weights can also be solved using
Lagrange multipliers. To make the comprehensive weight closer to both objective and
subjective weights, the function is established [42] as follows:
minF =
n
∑
j=1
uj
 
ln uj
u∗
j
!
+
n
∑
j=1
uj
 
ln uj
uS
j
!
(21)
where uj is the optimal combination weight, u∗
j is the subjective weight, and uS
j is the
objective weight.
The equation solved by the Lagrange multiplier is shown as Equation (22) [42].
uj =
u∗
j uS
j
n
∑
j=1
u∗
j uS
j
(22)
4. An Improved TOPSIS
4.1. A Solution to the TOPSIS Reverse Order Problem
The TOPSIS method constructs the multi-indicator problem’s ideal and negative ideal
solutions. It ranks the feasible solutions based on the evaluation criterion of the distance
approximate to the absolutely ideal solution and away from the absolutely negative ideal
solution.



<!-- page 9/21 -->

Energies 2023, 16, 7242
9 of 21
In the traditional TOPSIS method, the reversal of order is a very prone problem for
sorting multiple solutions. The root cause of the reverse order is the change in the ideal
and negative ideal solutions of the decision problem after the addition of a new decision
solution, which leads to a change in the evaluation criteria and, thus, to a change in the
order of the superiority of the solutions [43].
If this relative ideal solution can be abandoned and absolute ideal and negative ideal
solutions are deﬁned, order reversal will not occur. More precisely, no solution is better
than the absolute ideal solution or worse than the negative ideal solution in a valid decision
region. Based on this concept, we deﬁne the absolutely positive ideal solution for the
beneﬁt-based criteria as follows: S+ = (1, 1, · · · , 1). Likewise, we deﬁne the absolutely
negative ideal solution as follows: S−= (0, 0, · · · , 0).
4.2. Improved TOPSIS Based on Mahalanobis Distance
The Mahalanobis distance is irrelevant to the measurement scale and is not inﬂuenced
by the magnitude. The covariance between criteria is added to measure the association
between them. By doing so, the effect of correlation between the criteria on the distance
measurement is to some extent reduced. The fundamentals of TOPSIS and the Mahalanobis
distance are detailed in Appendix A.
The equation [44] for the Mahalanobis distance of A and B:
d(A, B) =
q
(A −B)TΣ−1(A −B)
(23)
where ∑is the covariance matrix.
The Mahalanobis distance only considers the covariance between the criteria. How-
ever, it solves the problem of different magnitudes between criteria and overcomes the
problem of linear correlation of the criteria. However, the inverse covariance matrix only
characterizes the ﬂuctuation of the criteria compared to the mean, which may overestimate
the inﬂuence between criteria, leading to inconsistent results. The Mahalanobis distance
can be improved. Firstly, it would be better to use the Pearson correlation coefﬁcient in
comparison to the covariance [45]. This is because the magnitude of the criterion inﬂuences
the covariance and avoids the signiﬁcant differences in values that lead to poor correlation.
The Pearson correlation coefﬁcient is limited to [−1, 1], which is more reasonable. Secondly,
the Mahalanobis distance should be added to the comprehensive weights obtained in the
previous section to calculate the distance more scientiﬁcally. In summary, the improved
expression of the weighted Mahalanobis distance is as follows:
(A, B) =
q
(A −B)T∆T ∑
−1 ∆(A −B)
(24)
∆= diag(√ω1, √ω2, · · · , √ωn)
where ∑is the Pearson correlation coefﬁcient matrix, and (ω1, ω2, · · · , ωn) are the compre-
hensive weights.
The steps of the improved TOPSIS comprehensive evaluation model are shown below:
STEP 1: Calculate the Pearson correlation coefﬁcient between each criterion.
STEP 2: Conduct a normalization of different types of metrics (beneﬁt-based, cost-
based, intermediate value)
For beneﬁt-based criteria [44]:
xij






xij −min
1≤i≤nxij

/

max
1≤i≤nxij −min
1≤i≤nxij

max
1≤i≤nxij ̸= min
1≤i≤nxij
1
max
1≤i≤nxij = min
1≤i≤nxij
(25)



<!-- page 10/21 -->

Energies 2023, 16, 7242
10 of 21
For cost-based criteria [44]:
xij






max
1≤i≤nxij −xij

/

max
1≤i≤nxij −min
1≤i≤nxij

max
1≤i≤nxij ̸= min
1≤i≤nxij
1
max
1≤i≤nxij = min
1≤i≤nxij
(26)
For intermediate-value criteria:
M = max
xij −xbest
	
(27)
xij





1 −|xij−xbest|
M
max
1≤i≤nxij ̸= min
1≤i≤nxij
1
max
1≤i≤nxij = min
1≤i≤nxij
(28)
STEP 3: Calculate the distance from the ith subject to the absolutely positive ideal
subject D(Pi, S+) and the distance to the absolutely negative ideal subject D(Pi, S−), re-
spectively, with Equations (29) and (30).
D
 Pi, S+ =
q
(xi −S+)T∆TΣ−1∆(xi −S+)
(29)
D
 Pi, S− =
q
(xi −S−)T∆TΣ−1∆(xi −S−)
(30)
where xi is the vector of normalized data on the criteria for the ith subject, and ∑is the
Pearson correlation coefﬁcient matrix.
STEP 4: Calculate the relative closeness. A large relative closeness value responds to
an economically efﬁcient subject [44].
Ci =
D(Pi, S−)
D(Pi, S−) + D(Pi, S+)
(31)
5. Example Analysis and Comparison
Transmission and transformation projects are the basic projects for the realization of
the transmission system, which is responsible for the construction and maintenance of the
lines and facilities required for the transmission system. This section analyzes data related
to ten 500 kV transmission and transformation projects. These projects are comprehensively
evaluated using the improved TOPSIS and BWM-anti-entropy weight method. First, the
subjective and objective weights are sought, and then the comprehensive weights are
obtained by applying game theory. Finally, a comprehensive evaluation of the ten projects
is carried out based on the calculated comprehensive weights and the improved TOPSIS
method.
5.1. Weighting Solution
5.1.1. Subjective Weights
The preferences of each criterion concerning the best and worst criterion are calculated
in the order of 1 to 9, according to the order of comparing the best criterion with the other
indicators and the other indicators with the worst criterion.
Select the Best: Return on Investment
Select the Worst: Proﬁt Growth Rate
The speciﬁc scores are detailed in Table 4.



<!-- page 11/21 -->

Energies 2023, 16, 7242
11 of 21
Table 4. Scoring the relative importance of the best and worst criteria.
C1
C2
C3
C4
C5
C6
C7
CB
1
2
3
2
5
6
7
CW
7
6
4
5
3
3
1
The results of the consistency test calculated according to the formula are:
Input-Based, CR = 0.261
Associated Threshold = 0.314
CR < Associated Threshold; so, the pairwise comparison consistency level is acceptable.
After solving the mathematical planning, the optimal weights of BWM are shown in
Table 5. The percentages and comparisons for the criteria are shown in Figure 3.
Table 5. Subjective weights.
Subjective
Weights
C1
C2
C3
C4
C5
C6
C7
0.323
0.188
0.125
0.188
0.075
0.063
0.038
Figure 3. Subjective weights.
5.1.2. Objective Weights
In this paper, anti-entropy weighting is applied for the objective weighting solution.
This method derives its principle from the coefﬁcient of variation and entropy weights.
Seven criteria are normalized for ten 500 kV transmission projects. The normalized
matrix is detailed in Table 6.
The anti-entropy and weights of each criterion obtained according to the relevant
formula of the anti-entropy weighting method are listed in Table 7.
The weights and anti-entropy derived from the anti-entropy weights method can be
seen: Net Present Value and Return On Investment have higher volatility and thus higher
anti-entropy and weights. The data of other criteria do not change too much, and the
weights are within a reasonable range.



<!-- page 12/21 -->

Energies 2023, 16, 7242
12 of 21
Table 6. Vector normalization.
Project Code
Return on
Investment
Net Present
Value
Payback
Period
Internal Rate
of Return
Asset
Liability
Ratio
Current
Ratio
Proﬁt
Growth Rate
P1
0.3532
0.1591
0.3737
0.2903
0.3157
0.3074
0.4416
P2
0.3532
0.1120
0.1925
0.3736
0.2894
0.2886
0.3865
P3
0.5564
0.0343
0.2864
0.4885
0.2736
0.4811
0.2562
P4
0.3263
0.2968
0.3251
0.3699
0.3262
0.3098
0.2542
P5
0.2523
0.1248
0.2459
0.2698
0.3315
0.2746
0.2767
P6
0.3499
0.0724
0.3121
0.3535
0.3262
0.3027
0.4336
P7
0.2187
0.2103
0.4262
0.1351
0.2421
0.3520
0.2629
P8
0.1817
0.2202
0.3728
0.1609
0.2999
0.2534
0.1256
P9
0.2052
0.3472
0.3013
0.2799
0.3052
0.2746
0.2334
P10
0.1591
0.7232
0.2575
0.2836
0.4210
0.2534
0.3485
Table 7. Anti-entropy and subjective weights.
Return on
Investment
Net Present
Value
Payback
Period
Internal Rate
of Return
Asset
Liability
Ratio
Current
Ratio
Proﬁt
Growth Rate
Anti-entropy
0.0533
0.0771
0.0480
0.0512
0.0468
0.0480
0.0507
Weights
0.1475
0.1510
0.1391
0.1446
0.1379
0.1391
0.1396
5.1.3. Optimal Comprehensive Weights
Neither subjective nor objective weights can fully cover the information provided by
the criteria. This section calculates the comprehensive weights using the Nash equilibrium
and Lagrange multiplier methods.
According to the game model given by the Nash equilibrium in this paper, the co-
efﬁcients of the combination of subjective and objective weights, which satisfy the Nash
equilibrium, are 0.2241 g2 = 0.7758. The combined Nash weights obtained by combin-
ing the two weights by the coefﬁcients: u∗= {0.26, 0.17, 0.12, 0.18, 0.11, 0.10, 0.06}. The
percentages and comparisons for the criteria are detailed in Figure 4.
Figure 4. Nash weights.
The Lagrange multiplier method can also solve the problem of ﬁnding the extrema un-
der a set of constraints. Solving the objective function with the Lagrange multiplier method



<!-- page 13/21 -->

Energies 2023, 16, 7242
13 of 21
yields the optimal combination of weights: u∗= {0.27, 0.17, 0.13, 0.18, 0.11, 0.09, 0.05}. A
comparison of the two sets of basic weights (subjective, objective) and the two sets of
combined weights (Nash, Lagrange) is shown in Figure 5.
Figure 5. Comparison of different weighting methods.
This section solves the comprehensive weights in two separate approaches. Comparing
the two combined weights, the Nash and Lagrange weights are very similar, and both are
between the subjective weights and objective weights. In this paper, Nash weight is chosen
as the comprehensive weight of BWM-anti-entropy.
5.2. An Improved TOPSIS Method to Calculate Score Evaluation
The Pearson correlation coefﬁcient matrix between the seven criteria Σ is shown in
Figure 6.
1
2
3
4
5
6
7
1
2
3
4
5
6
7
1
0.59
0.19
0.83
0.37
0.82
0.29
0.59
1
0.04
0.28
0.72
0.48
0.09
0.19
0.04
1
0.58
0.40
0.12
0.26
0.83
0.28
0.58
1
0.09
0.54
0.35
0.37
0.72
0.40
0.09
1
0.53
0.27
0.82
0.48
0.12
0.54
0.29
0.09
0.26
C
C
C
C
C
C
C
C
C
C
C
C
C
C
−
−
−
−
−
−
−
−
−
−
Σ =
−
−
−
−
−
−
−
0.54
1
0.03
0.35
0.27
0.03
1




















−


−




Figure 6. Pearson correlation coefﬁcient matrix.
As can be seen from this Pearson correlation coefﬁcient matrix, some of these criteria
are strongly correlated. If we continue to use the Euclidean distance, it will lead to the
failure of the Euclidean distance and will be unable to correctly assess the distance from the
actual projects to the ideal projects. At the same time, using the inverse Pearson coefﬁcient
matrix as a substitute for the inverse covariance matrix will reduce the inﬂuence of the
magnitude to a certain extent and more reasonably measure the degree of correlation
between the criteria.



<!-- page 14/21 -->

Energies 2023, 16, 7242
14 of 21
The data-processed results in advance by Max-Min normalization are detailed in
Table 8.
Table 8. Max-Min normalization.
Project Code
Return on
Investment
Net Present
Value
Payback
Period
Internal Rate
of Return
Asset
Liability
Ratio
Current
Ratio
Proﬁt
Growth Rate
P1
0.4886
0.4953
0.2245
0.4390
0.5882
0.2500
1.0000
P2
0.4886
0.1128
1.0000
0.6748
0.7353
0.1630
0.8258
P3
1.0000
0.0000
0.5984
1.0000
0.8235
1.0000
0.4136
P4
0.4208
0.3811
0.4325
0.6642
0.5294
0.2609
0.4071
P5
0.2345
0.1313
0.7714
0.3813
0.5000
0.0978
0.4784
P6
0.4801
0.0553
0.4882
0.6179
0.5294
0.2283
0.9747
P7
0.1499
0.2555
0.0000
0.0000
1.0000
0.4565
0.4346
P8
0.0567
0.2699
0.2286
0.0732
0.6765
0.0000
0.0000
P9
0.1160
0.4541
0.5345
0.4098
0.6471
0.0978
0.3412
P10
0.0000
1.0000
0.7219
0.4203
0.0000
0.0000
0.7055
The comprehensive weights and Pearson correlation coefﬁcient matrices obtained
from the Nash game model are used in TOPSIS to solve for the Mahalanobis distance.
The equation is used to ﬁnd the Mahalanobis distance and the relative closeness of the
evaluated solutions to the absolutely positive ideal projects and the negative ideal projects,
and the evaluation projects are ranked according to the closeness. High relative closeness
indicates that the project should be good. The Mahalanobis distance and closeness ranking
are shown in Table 9.
Table 9. Mahalanobis distance and closeness ranking.
Distance of Positive Solution
Distance of Negative Solution
Relative Closeness
Rank
P3
0.6934
1.1312
0.6200
1
P1
0.7582
0.7644
0.5020
2
P2
1.1716
1.0347
0.4690
3
P10
1.6661
1.1719
0.4129
4
P4
0.9828
0.6726
0.4063
5
P6
1.0899
0.6780
0.3835
6
P7
1.3983
0.8604
0.3809
7
P5
1.2656
0.7283
0.3653
8
P9
1.3010
0.6603
0.3367
9
P8
1.1567
0.4296
0.2708
10
After comparing the data with the ﬁnal distance and closeness in Table 9, it can be
seen that the relative closeness of P3 is the highest. This is mainly because the two criteria
with the highest weights, Return on Investment and Internal Rate of Return, are optimal. In
contrast, for the cost-based criterion Asset Liability Ratio, P1 is low. For P8, all four criteria
characterizing proﬁtability (c1~c4) are low, leading to poor evaluation results.
5.3. SIMUS and Traditional TOPSIS Solving
So far some of the more popular MCDM methods are AHP, TOPSIS, SPOTIS, COMET,
SIMUS, etc. The SPOTIS method no longer performs relative comparisons between projects
to avoid ranking reversal and forms a stable score preference ranking [43]. The core idea
of COMET (characteristic object method) is to assign a score or ranking to each object
by comparing the similarity between the object and a set of characteristic objects such as
the Euclidean distance and cosine similarity [46]. COMET needs more information. The
SIMUS method is not based on the same principles as these methods. It uses a linear
programming algorithm to generate the Pareto efﬁcient matrix, i.e., efﬁcient results matrix,



<!-- page 15/21 -->

Energies 2023, 16, 7242
15 of 21
thus obtaining an optimal solution (scores) for each criterion. The Pareto efﬁcient matrix is
analyzed vertically, and the total score and ranking of each project is found based on the
weights of the objective data (efﬁcient results matrix ranking). The method then re-scored
each project from a horizontal analysis perspective based on the ERM, forming a new
matrix called the project dominant matrix (PDM). Even though the scores generated from
the two perspectives are different, the ranking of the corresponding scores from the two
perspectives is the same and stable.
In this paper, the traditional TOPSIS method and SIMUS method are used for compre-
hensive economic evaluation, respectively. The results are eventually compared with those
of the proposed improved TOPSIS based on BWM-anti-entropy weight to demonstrate the
feasibility of the method.
5.3.1. Traditional TOPSIS Solving
The traditional TOPSIS method considers the weights and determines the optimal and
worst projects based on the decision matrix, immediately followed by the calculation of the
Euclidean distance and closeness ranking.
The normalized matrix is detailed in Table 6. The optimal comprehensive weights
are determined as Nash weights calculated by Section 5.1.3. The Euclidean distance and
closeness ranking are shown in Table 10.
Table 10. Euclidean distance and closeness ranking.
Distance of Positive Solution
Distance of Negative Solution
Relative Closeness
Rank
P10
0.2403
0.3004
0.5556
1
P3
0.2876
0.2722
0.4862
2
P4
0.2334
0.1796
0.4349
3
P2
0.2821
0.1846
0.3956
4
P9
0.2681
0.1578
0.3704
5
P1
0.2805
0.1596
0.3588
6
P6
0.3015
0.1640
0.3523
7
P5
0.3152
0.1155
0.2681
8
P7
0.3262
0.1076
0.2481
9
P8
0.3366
0.0892
0.2096
10
5.3.2. SIMUS Solving
The sequential interactive model for urban systems (SIMUS) is a model developed to
support urban planning and management decisions and is now mostly used in MCDM.
Based on linear programming, SIMUS is immune to rank reversal [47]. An important
feature of the SIMUS model is its sequential interactivity, which means that the model runs
as an iterative process, with each step based on the results of the previous step.
In this study, SIMUS V.3.13, an open-source software that has a vast user commu-
nity [48], is used for evaluation to determine the optimal or most viable solution. The
speciﬁc steps are as follows:
STEP 1: Create a project and enter the number of criteria and alternatives as shown in
Figure 7.
STEP 2: Create and normalize a decision matrixThe results were the same as in Table 6.
STEP 3: Start analysis, then export the efﬁcient result matrix (ERM) and the project
dominance matrix (PDM). The results are detailed in Tables 11 and 12.



<!-- page 16/21 -->

Energies 2023, 16, 7242
16 of 21
 
Figure 7. Criteria and alternatives in SIMUS.
Table 11. Normalized efﬁcient result matrix.
P1
P2
P3
P4
P5
P6
P7
P8
P9
P10
C1
1.00
C2
1.00
C3
0.27
0.73
C4
0.81
0.19
C5
1.00
C6
0.29
0.63
0.08
C7
0.65
0.35
Sum of Column (SC)
0.65
1.81
0.29
0.27
0.00
0.35
1.63
0.08
0.19
1.73
Participation Factor (PF)
1
2
1
1
0
1
2
1
1
2
Norm. Participation Factor
(NPF)
0.14
0.29
0.14
0.14
0.00
0.14
0.29
0.14
0.14
0.29
Final Result (SC × NPF)
0.09
0.52
0.04
0.04
0.00
0.05
0.46
0.01
0.03
0.49
Table 12. Project dominance matrix.
P1
P2
P3
P4
P5
P6
P7
P8
P9
P10
Row
Sum
Net
P1
0.65
0.65
0.65
0.65
0.30
0.65
0.65
0.65
0.65
5.50
−0.50
P2
1.81
1.81
1.81
1.81
1.81
1.81
1.81
1.62
1.81
16.1
11.1
P3
0.29
0.29
0.29
0.29
0.29
0.21
0.29
0.29
2.24
−4.01
P4
0.27
0.27
0.27
0.27
0.27
0.27
0.27
0.27
2.16
−4.30
P5
0.00
−7.00
P6
0.35
0.35
0.35
0.35
0.35
0.35
0.35
0.35
2.80
−3.50
P7
1.63
1.63
1.34
1.63
1.63
1.63
1.55
1.63
1.63
14.3
9.30
P8
0.08
0.08
0.08
0.08
0.08
0.08
0.08
0.56
−6.20
P9
0.19
0.19
0.19
0.19
0.19
0.19
0.19
0.19
1.52
−5.10
P10
1.73
1.73
1.73
1.46
1.73
1.73
1.73
1.73
1.73
15.3
10.3
Column sum
6.00
5.00
6.34
6.46
7.00
6.30
5.00
6.76
6.62
5.00
Final Result in ERM and NET in PDM are the scores of 10 projects from two perspec-
tives based on linear programming and mathematical calculations by the SIMUS method.
A high score represents a suitable program.
5.3.3. Comparative Analysis of Evaluation Result
All four sets of scores (traditional and improved relative closeness, NET, and Final
Result) were obtained by three different methods or perspectives to rank the example
projects, as shown in Table 13. The rankings obtained by the ERM and the DPM are
identical. A comparison of the results of the three methods is shown in Figure 8.



<!-- page 17/21 -->

Energies 2023, 16, 7242
17 of 21
Table 13. Comparison of evaluation scores and rankings.
Rank
TOPSIS Method
SIMUS Method
Traditional TOPSIS
Improved TOPSIS
ERM
PDM
Project
Score
Project
Score
Project
Score
Project
Score
1
P10
0.5556
P3
0.6200
P2
0.52
P2
11.1
2
P3
0.4862
P1
0.5020
P10
0.49
P10
10.3
3
P4
0.4349
P2
0.4690
P7
0.46
P7
9.3
4
P2
0.3956
P10
0.4129
P1
0.09
P1
−0.5
5
P9
0.3704
P4
0.4063
P6
0.05
P6
−3.5
6
P1
0.3588
P6
0.3835
P3
0.04
P3
−4.01
7
P6
0.3523
P7
0.3809
P4
0.04
P4
−4.3
8
P5
0.2681
P5
0.3653
P9
0.03
P9
−5.1
9
P7
0.2481
P9
0.3367
P8
0.01
P8
−6.2
10
P8
0.2096
P8
0.2708
P5
0
P5
−7
 
Figure 8. Comparison of evaluation scores.
Differing methods often lead to varying rankings and preferences in MCDA. Using
appropriate coefﬁcients to test the similarity of the rankings would promote a better, more
responsible decision [49]. ρ Spearman, τ Kendall, and γ Goodman-Kruskal coefﬁcients are
commonly used to check the similarity of rankings [50].
In the comparison analysis using traditional coefﬁcients, the effect of the placement of a
pair of adjacent alternatives on similarity is the same for each position in the ranking. In rank
correlation analysis using traditional coefﬁcients, interchanging the top two rankings has a
commensurate effect to swapping the bottom two on the outcome [51]. This is not rational
in MCDA. Hence, a new coefﬁcient WS is proposed to compare the similarity between the
rankings, making the differences within the top-ranked intervals more signiﬁcant [52]:
WS = 1 −
n
∑
i=1
 
2−Rxi ·
Rxi −Ryi

max{|1 −Rxi|, |N −Rxi|}
!
(32)
where WS is a value of the similarity coefﬁcient, N is a length of ranking, and Rxi and Ryi
mean the place in the ranking for i-th element in respectively ranking x and ranking y. The
result of the WS coefﬁcient is detailed in Table 14.



<!-- page 18/21 -->

Energies 2023, 16, 7242
18 of 21
Table 14. WS coefﬁcient between the three rankings.
WS
Traditional TOPSIS
Improved TOPSIS
SIMUS Method
Traditional TOPSIS
1.0000
0.7167
0.6865
Improved TOPSIS
0.7167
1.0000
0.5809
SIMUS Method
0.6865
0.5809
1.0000
The comparison results are shown in Tables 13 and 14. The rankings of all three
methods have some relatively strong correlation, which follows common sense. The higher
correlation between traditional TOPSIS and improved TOPSIS may be because they both
use the composite weights derived in the previous section, whereas the SIMUS method
focuses on iterating to ﬁnd the best in the objective data through linear programming. The
highest score in the SIMUS method is also because P2 performs well in C5 and C7. The
weights of C5 and C7 in comprehensive weights are very small, so P2 is not ranked as high
in the TOPSIS method.
It can be seen in Table 13 that there are some deviations in the ranking results formed
by the improved TOPSIS and the traditional TOPSIS. For example, the rankings of P1 and P9
in the two sets of results differ considerably, which is due to the more signiﬁcant correlation
in the indicator system. The improved TOPSIS method is not affected by correlation and
magnitude. In contrast, the traditional Euclidean distance is affected by correlation, which
leads to the problem of reversed ordering.
In summary, both the individual and comparative analyses have effectively demon-
strated the rationality and feasibility of the improved TOPSIS method based on the
weighted Mahalanobis distance and the absolute ideal solution proposed in this paper in
the economic evaluation of power systems.
6. Conclusions
This paper proposes a comprehensive evaluation method based on improved TOPSIS
and BWM-anti-entropy weighting. It applies to the power transmission system, which
beneﬁts the investment decision and management. The conclusions are as follows:
1.
The economic comprehensive evaluation model enhances the tedious process of the
traditional AHP method of two-by-two comparison of criteria, and the consistency
and reliability of the results are higher. While adding objective weights, the optimal
coordination of weights is solved by the Nash equilibrium and Lagrange multiplier
methods, respectively. Weights become more accurate and reasonable.
2.
Improving the TOPSIS method using the Mahalanobis distance and comprehensive
weights solves the problem of Euclidean distance failure and inverse order when the
linear correlation between criteria is high. Applying the Pearson correlation coefﬁcient
rather than covariance circumvents the problems caused by covariance’s inconsistency
in magnitude between criteria.
3.
A comprehensive evaluation of the power transmission system economy was achieved
by ranking the relative closeness of ten 500 kV transmission projects to the positive
and negative ideal projects. The economic evaluation was performed using the
traditional TOPSIS, improved TOPSIS, and SIMUS methods for economic integration,
respectively. A comparative analysis was implemented to analyze the differences
between the three rankings and their causes. The results indicate that this method
provides both an economic evaluation of the power transmission systems and a
reﬂection of the closeness of each criterion to the ideal situation. The evaluation
criteria system is characterized by its comprehensiveness and objectivity, while the
evaluation process is conducted scientiﬁcally and reasonably. As a result, the ﬁnal
evaluation conclusion possesses a high degree of credibility.
Based on comprehensive weights, the method improves the TOPSIS by introducing
the Mahalanobis distance and Pearson correlation coefﬁcients, which can eliminate the
inﬂuence of linear correlation. This method is essentially a multi-attribute decision-making



<!-- page 19/21 -->

Energies 2023, 16, 7242
19 of 21
(MADM) method that breaks through the limitations of single-dimension weights. The
evaluation can also be expanded to include safety factors and sensitivity, etc. The research
object can also be expanded to an entire power grid in a region. Hence, this method is
widely applied and can be implemented in the economic analysis of additional diverse
subjects. The TOPSIS method will be extended to multi-attribute group decision-making
issues.
Author Contributions: Methodology, W.Z., J.F., Z.R., X.L., Y.C. and X.X.; Writing—original draft,
Y.C.; Writing—review & editing, X.X.; Visualization, S.L.; Supervision, J.L. All authors have read and
agreed to the published version of the manuscript.
Funding: This work was supported by the Science and Technology Project of State Grid Sichuan
Electric Power Company (521996220002).
Data Availability Statement: No new data were created or analyzed in this study. Data sharing is
not applicable to this article.
Conﬂicts of Interest: The authors declare no conﬂict of interest.
Appendix A
As shown in Figure A1, using two dimensions as an example, point B is apparently
more of an outlier than point A from a statistical point of view. Nevertheless, if we calculate
the Euclidean distance of these two points to the center O of the point group, point A
is more out of the group. This unreasonable conclusion occurs because there is a linear
correlation between x1 and x2. To avoid the negative inﬂuence of this correlation, the
coordinate system can be rotated counterclockwise by a certain angle into a new coordinate
system y1Oy2.
1x
1y
A
B
2y
O
1y
A
B
2y
O
A
B
1x
2x
1y
2y
O
Rotate
Standardise
Figure A1. Mahalanobis distance.
Under the new coordinate system y1 and y2 are uncorrelated, and, after the normaliza-
tion transformation, the elliptical point group becomes a circular point group. Currently,
the Euclidean distance calculated according to the formula is the Mahalanobis distance. It



<!-- page 20/21 -->

Energies 2023, 16, 7242
20 of 21
is not difﬁcult to see that the Mahalanobis distance from point A to point O is shorter than
the Mahalanobis distance from point B to point O.
References
1.
Fadaeenejad, M.; Saberian, A.M.; Fadaee, M.; Radzi, M.A.M.; Hizam, H.; AbKadir, M.Z.A. The present and future of smart power
grid in developing countries. Renew. Sustain. Energy Rev. 2014, 29, 828–834. [CrossRef]
2.
Tinnium, K.; Rastgoufard, P.; Duvoisin, P.F. Probabilistic ranking of large scale transmission projects. Electr. Power Syst. Res. 1997,
42, 21–25. [CrossRef]
3.
Kishore, T.S.; Singal, S.K. Optimal economic planning of power transmission lines: A review. Renew. Sustain. Energy Rev. 2014, 39,
949–974. [CrossRef]
4.
Yang, J.; Xiang, Y.; Wang, Z.; Dai, J.; Wang, Y. Optimal investment decision of distribution network with investment ability and
project correlation constraints. Front. Energy Res. 2021, 9, 728834. [CrossRef]
5.
He, Y.; Liu, Y.; Li, M.; Zhang, Y. Beneﬁt evaluation and mechanism design of pumped storage plants under the background of
power market reform—A case study of China. Renew. Energy 2022, 191, 796–806. [CrossRef]
6.
Kut, P.; Pietrucha-Urbanik, K. Most Searched Topics in the Scientiﬁc Literature on Failures in Photovoltaic Installations. Energies
2022, 15, 8108. [CrossRef]
7.
Pohekar, S.D.; Ramachandran, M. Application of multi-criteria decision making to sustainable energy planning—A review. Renew.
Sustain. Energy Rev. 2004, 8, 365–381. [CrossRef]
8.
Samanta, S.; Chakraborty, J.; Dutta, S.B. Village Level Landslide Probability Analysis Based on Weighted Sum Method of Multi-
Criteria Decision-Making Process of Darjeeling Himalaya, West Bengal, India. In Geospatial Technology for Environmental Hazards;
Shit, P.K., Pourghasemi, H.R., Bhunia, G.S., Das, P., Narsimha, A., Eds.; Springer International Publishing: Cham, Switzerland,
2022; pp. 391–414. [CrossRef]
9.
Tavana, M.; Soltanifar, M.; Santos-Arteaga, F.J. Analytical hierarchy process: Revolution and evolution. Ann. Oper. Res. 2023, 326,
879–907. [CrossRef]
10.
Zahid, K.; Akram, M.; Kahraman, C. A new ELECTRE-based method for group decision-making with complex spherical fuzzy
information. Knowl.-Based Syst. 2022, 243, 108525. [CrossRef]
11.
Naseem, A.; Ullah, K.; Akram, M.; Božani´c, D.; ´Cirovi´c, G. Assessment of Smart Grid Systems for Electricity Using Power
Maclaurin Symmetric Mean Operators Based on T-Spherical Fuzzy Information. Energies 2022, 15, 7826. [CrossRef]
12.
Barros, J.R.P.; Melo, A.C.G.; da Silva, A.M.L. An approach to the explicit consideration of unreliability costs in transmission
expansion planning. In Proceedings of the 2004 International Conference on Probabilistic Methods Applied to Power Systems,
Ames, IA, USA, 12–16 September 2004; pp. 927–932.
13.
Minoia, A.; Ernst, D.; Dicorato, M.; Trovato, M.; Ilic, M. Reference transmission network: A game theory approach. IEEE Trans.
Power Syst. 2006, 21, 249–259. [CrossRef]
14.
Chen, P.; Wu, F.; Huang, Z.; Chen, Y. Fuzzy Comprehensive Evaluation of Power Suppliers Based on Combination Weighting. In
Proceedings of the 2nd International Conference on Engineering Management and Information Science, EMIS 2023, Chengdu,
China, 24–26 February 2023. [CrossRef]
15.
Zhong, Y.; Wang, H.; Lv, H.; Guo, F. A vertical handoff decision scheme using subjective-objective weighting and grey relational
analysis in cognitive heterogeneous networks. Ad Hoc Netw. 2022, 134, 102924. [CrossRef]
16.
Behzadian, M.; Khanmohammadi Otaghsara, S.; Yazdani, M.; Ignatius, J. A state-of the-art survey of TOPSIS applications. Expert
Syst. Appl. 2012, 39, 13051–13069. [CrossRef]
17.
Ren, L.; Zhang, Y.; Wang, Y.; Sun, Z. Comparative Analysis of a Novel M-TOPSIS Method and TOPSIS. Appl. Math. Res. EXpress
2007, 2007, abm005. [CrossRef]
18.
Aires, R.F.D.F.; Ferreira, L. A new approach to avoid rank reversal cases in the TOPSIS method. Comput. Ind. Eng. 2019, 132,
84–97. [CrossRef]
19.
Yang, B.; Zhao, J.; Zhao, H. A robust method for avoiding rank reversal in the TOPSIS. Comput. Ind. Eng. 2022, 174, 108776.
[CrossRef]
20.
Chakraborty, S. TOPSIS and Modiﬁed TOPSIS: A comparative analysis. Decis. Anal. J. 2022, 2, 100021. [CrossRef]
21.
Huang, R.; Cui, C.; Sun, W.; Towey, D. Poster: Is Euclidean Distance the best Distance Measurement for Adaptive Random
Testing? In Proceedings of the 2020 IEEE 13th International Conference on Software Testing, Validation and Veriﬁcation (ICST),
Porto, Portugal, 24–28 October 2020; pp. 406–409.
22.
Sadeghi, M.; Ameli, A. An AHP decision making model for optimal allocation of energy subsidy among socio-economic subsectors
in Iran. Energy Policy 2012, 45, 24–32. [CrossRef]
23.
Kamgar, R.; Hateﬁ, S.M.; Majidi, N. A Fuzzy Inference System in Constructional Engineering Projects to Evaluate the Design
Codes for RC Buildings. Civ. Eng. J. 2018, 4, 2155. [CrossRef]
24.
Sun, L.; Miao, C.; Yang, L. Ecological-economic efﬁciency evaluation of green technology innovation in strategic emerging
industries based on entropy weighted TOPSIS method. Ecol. Indic. 2017, 73, 554–558. [CrossRef]
25.
Bayram, B.Ç. Evaluation of forest products trade economic contribution by entropy-TOPSIS: Case study of Turkey. BioResources
2020, 15, 1419–1429. [CrossRef]



<!-- page 21/21 -->

Energies 2023, 16, 7242
21 of 21
26.
Yang, J.; Dong, X.; Liu, S. Safety Risks of Primary and Secondary Schools in China: A Systematic Analysis Using AHP–EWM
Method. Sustainability 2022, 14, 8214. [CrossRef]
27.
He, Z.; Cao, H.; Hu, Q.; Zhang, Y.; Nan, X.; Li, Z. Optimization of apple irrigation and N fertilizer in Loess Plateau of China based
on ANP-EWM-TOPSIS comprehensive evaluation. Sci. Hortic. 2023, 311, 111794. [CrossRef]
28.
Zhang, Y.; Khan, S.U.; Swallow, B.; Liu, W.; Zhao, M. Coupling coordination analysis of China’s water resources utilization
efﬁciency and economic development level. J. Clean. Prod. 2022, 373, 133874. [CrossRef]
29.
Ma, Y.; Xu, L.; Cai, J.; Cao, J.; Zhao, F.; Zhang, J. A novel hybrid multi-criteria decision-making approach for offshore wind turbine
selection. Wind Eng. 2021, 45, 1273–1295. [CrossRef]
30.
Peng, J.; Zhang, J. Urban ﬂooding risk assessment based on GIS- game theory combination weight: A case study of Zhengzhou
City. Int. J. Disaster Risk Reduct. 2022, 77, 103080. [CrossRef]
31.
Basilio, M.P.; De Freitas, J.G.; Kämpffe, M.G.F.; Bordeaux Rego, R. Investment portfolio formation via multicriteria decision aid: A
Brazilian stock market study. J. Model. Manag. 2018, 13, 394–417. [CrossRef]
32.
Evers, S.; Goossens, M.; De Vet, H.; Van Tulder, M.; Ament, A. Criteria list for assessment of methodological quality of economic
evaluations: Consensus on Health Economic Criteria. Int. J. Technol. Assess. Health Care 2005, 21, 240–245. [CrossRef]
33.
He, Y.; Liu, W.; Jiao, J.; Guan, J. Evaluation method of beneﬁts and efﬁciency of grid investment in China: A case study. Eng. Econ.
2018, 63, 66–86. [CrossRef]
34.
Chang, K.-P. Corporate Finance: A Systematic Approach; Springer Nature: Singapore, 2023. [CrossRef]
35.
Rezaei, J. Best-worst multi-criteria decision-making method. Omega 2015, 53, 49–57. [CrossRef]
36.
Al-Harbi, K.M.A.-S. Application of the AHP in project management. Int. J. Proj. Manag. 2001, 19, 19–27. [CrossRef]
37.
Basílio, M.P.; Pereira, V.; Costa, H.G.; Santos, M.; Ghosh, A. A Systematic Review of the Applications of Multi-Criteria Decision
Aid Methods (1977–2022). Electronics 2022, 11, 1720. [CrossRef]
38.
Ayan, B.; Abacıo˘glu, S.; Basilio, M.P. A Comprehensive Review of the Novel Weighting Methods for Multi-Criteria Decision-
Making. Information 2023, 14, 285. [CrossRef]
39.
Zhang, W.; Lu, J.; Zhang, Y. Comprehensive Evaluation Index System of Low Carbon Road Transport Based on Fuzzy Evaluation
Method. Procedia Eng. 2016, 137, 659–668. [CrossRef]
40.
Wang, W.; Li, H.; Hou, X.; Zhang, Q.; Tian, S. Multi-Criteria Evaluation of Distributed Energy System Based on Order Relation-
Anti-Entropy Weight Method. Energies 2021, 14, 246. [CrossRef]
41.
Lai, C.; Chen, X.; Chen, X.; Wang, Z.; Wu, X.; Zhao, S. A fuzzy comprehensive evaluation model for ﬂood risk based on the
combination weight of game theory. Nat. Hazards 2015, 77, 1243–1259. [CrossRef]
42.
Rockafellar, R.T. Lagrange Multipliers and Optimality. Siam Rev. 1993, 35, 183–238. [CrossRef]
43.
Dezert, J.; Tchamova, A.; Han, D.; Tacnet, J.-M. The SPOTIS Rank Reversal Free Method for Multi-Criteria Decision-Making
Support. In Proceedings of the 2020 IEEE 23rd International Conference on Information Fusion (FUSION), Rustenburg, South
Africa, 6–9 July 2020; pp. 1–8. [CrossRef]
44.
Papathanasiou, J.; Ploskas, N. Multiple Criteria Decision Aid: Methods, Examples and Python Implementations; Springer International
Publishing: Cham, Switzerland, 2018; Volume 136. [CrossRef]
45.
Asuero, A.G.; Sayago, A.; González, A.G. The Correlation Coefﬁcient: An Overview. Crit. Rev. Anal. Chem. 2006, 36, 41–59.
[CrossRef]
46.
Sałabun, W. The Characteristic Objects Method: A New Distance-based Approach to Multicriteria Decision-making Problems.
J. Multi-Criteria Decis. Anal. 2015, 22, 37–50. [CrossRef]
47.
Valencia Polytechnic University, INGENIO, Valencia, Spain; Munier, N. A New Approach to the Rank Reversal Phenomenon in
MCDM with the SIMUS Method. Mult. Criteria Decis. Mak. 2016, 11, 137–152. [CrossRef]
48.
Munier, N.; Hontoria, E.; Jiménez-Sáez, F. Strategic Approach in Multi-Criteria Decision Making: A Practical Guide for Complex
Scenarios; Springer International Publishing: Cham, Switzerland, 2019; Volume 275. [CrossRef]
49.
Ishizaka, A.; Siraj, S. Are multi-criteria decision-making tools useful? An experimental comparative study of three methods. Eur.
J. Oper. Res. 2018, 264, 462–471. [CrossRef]
50.
Mulliner, E.; Malys, N.; Maliene, V. Comparative analysis of MCDM methods for the assessment of sustainable housing
affordability. Omega 2016, 59, 146–156. [CrossRef]
51.
Blest, D.C. Rank Correlation—An Alternative Measure. Aust. Htmlent Glyphamp Asciiamp N. Z. J. Stat. 2000, 42, 101–111.
[CrossRef]
52.
Krzhizhanovskaya, V.V.; Závodszky, G.; Lees, M.H.; Dongarra, J.J.; Sloot, P.M.A.; Brissos, S.; Teixeira, J. (Eds.) Computa-
tional Science—ICCS 2020. In Proceedings of the 20th International Conference, Amsterdam, The Netherlands, 3–5 June 2020;
Proceedings, Part II. Springer International Publishing: Cham, Switzerland, 2020; Volume 12138. [CrossRef]
Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
