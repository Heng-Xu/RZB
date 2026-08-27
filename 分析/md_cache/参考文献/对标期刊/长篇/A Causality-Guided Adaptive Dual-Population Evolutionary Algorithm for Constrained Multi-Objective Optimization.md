<!--
source: 长篇/A Causality-Guided Adaptive Dual-Population Evolutionary Algorithm for Constrained Multi-Objective Optimization.pdf
sha256: 64b55c184ab306211342657d03717c51815492c0876766c99c3e9184bc5553cf
method: pymupdf
pages: 6
-->

<!-- page 1/6 -->

A Causality-Guided Adaptive Dual-Population
Evolutionary Algorithm for Constrained
Multi-Objective Optimization
1st Jiachun Huang†
Shantou University
Guangdong, China
22jchuang1@stu.edu.cn
4th Jiaping Hu
Shantou University
Guangdong, China
23jphu@stu.edu.cn
7th Junjie Yao
University of Electronic Science
and Technology of China
Sichuan, China
21jjyao@stu.edu.cn
2nd Zhaojun Wang†
Shantou University
Guangdong, China
17zjwang@stu.edu.cn
5th Biao Xu
Shantou University
Guangdong, China
xubiao@stu.edu.cn
8th Yun Li
University of Electronic Science
and Technology of China
Sichuan, China
Yun.li@ieee.org
3rd Wenji Li∗
Shantou University
Guangdong, China
liwj@stu.edu.cn
6th Shushan Huang∗
Shantou University
Guangdong, China
sshuang@stu.edu.cn
9th Zhun Fan∗
University of Electronic Science
and Technology of China
Sichuan, China
fanzhun@uestc.edu.cn
Abstract—Most existing constrained multi-objective evolution-
ary algorithms primarily rely on heuristic search and em-
pirically designed operators, often overlooking the underlying
causal relationships between decision variables and objective
functions. This limitation reduces their ability to avoid deceptive
regions in the search space and increases the risk of premature
convergence, particularly in problems with complex feasible
regions. To tackle this challenge, we propose a novel causality-
guided adaptive dual-population evolution for constrained multi-
objective optimization algorithm (named CAD-CMOEA). The
proposed CAD-CMOEA first employs an information-geometric
causal inference method to model causal effects between decision
variables and objectives, identifying the positive or negative
influence of each variable. Based on this insight, a causality-
aware genetic operator is developed by integrating competitive
cooperative optimization strategies with Gaussian perturbation,
enabling guided and directional variation to produce high-quality
offspring. To further balance convergence and diversity, we
propose a new dual-population co-evolution mechanism: one
population explores high-quality solutions within the feasible
region, while another population investigates promising areas
near the infeasible boundary, thereby strengthening global search
capabilities. Experimental results on LIR-CMOP1-14 benchmark
problems demonstrate that CAD-CMOEA outperforms eight
state-of-the-art algorithms in terms of IGD and HV metrics,
confirming its effectiveness in causal modeling, search efficiency
and solution quality.
Index Terms—causal intervention, constrained multi-objective
optimization,
dual-population
collaborative
optimization,
MOEA/D
∗Corresponding authors.
† These authors contributed equally to this work.
I. INTRODUCTION
Multi-objective optimization problems (MOPs) are common
in real-world applications such as engineering design [1],
scheduling [2], and intelligent control [3], where multiple
conflicting objectives make the solution process challenging.
Multi-objective evolutionary algorithms (MOEAs) have gained
attention for their ability to handle complex search spaces
without relying heavily on problem-specific knowledge. In
practice, many problems also involve equality and inequality
constraints, leading to constrained multi-objective optimization
problems (CMOPs) with increased complexity [4].
To address constraints in CMOPs, various methods have
been proposed, including penalty functions [5], ϵ-constraint
techniques [6], repair operations [7], and strategies that sepa-
rate feasible and infeasible sub-populations [8]. While effec-
tive in certain cases, these approaches face key limitations.
Most rely on heuristic rules or empirical tuning and lack
the ability to extract useful knowledge from optimization
data, limiting their stability and generalization in complex or
dynamic environments. Additionally, in problems with sparse
feasible regions or highly non-linear constraints, they often
suffer from low search efficiency and are prone to local optima
or stagnation.
A more fundamental limitation of mainstream constraint
handling methods is their focus on numerical feasibility, while
lacking the ability to model deeper dependencies among vari-
ables, constraints, and objectives. These approaches often treat
the problem as a black box, emphasizing adaptive correction
2025 International Conference on Machine Intelligence and Nature-Inspired Computing (MIND)
979-8-3315-8768-0/25/$31.00 ©2025 IEEE
217
2025 International Conference on Machine Intelligence and Nature-Inspired Computing (MIND) | 979-8-3315-8768-0/25/$31.00 ©2025 IEEE | DOI: 10.1109/MIND67540.2025.11351801
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:49:06 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 2/6 -->

and feasibility guidance without exploring which variables
causally affect feasibility or whether causal paths exist be-
tween objectives. Relying mainly on empirical or statistical
correlations, they fail to capture the underlying structural
information of complex coupled systems, limiting both search
efficiency and interpretability.
Causal inference, as advanced by Pearl [9], has seen rapid
progress in AI and machine learning, offering interpretable and
stable models by explicitly modeling relationships between
variables. It has been successfully applied in reinforcement
learning [10], feature selection [11], and policy planning [12],
enhancing both performance and adaptability in complex envi-
ronments. However, its integration into evolutionary optimiza-
tion (especially for CMOPs) remains largely unexplored. Most
MOEAs still rely on heuristics and numerical search paths,
overlooking causal dependencies among variables, objectives,
and constraints. In real-world problems, some decision vari-
ables may directly influence constraints, while objectives may
have indirect effects via mediators. Modeling these causal
structures could greatly enhance search effectiveness, inter-
pretability, and robustness, offering a new theoretical and
algorithmic direction for evolutionary optimization.
Based on this, we propose a novel causality-guided adaptive
dual-population evolutionary algorithm for constrained multi-
objective optimization, named CAD-CMOEA. The algorithm
enhances the search process by leveraging causal relationships
between decision variables and objectives to efficiently explore
feasible, high-quality solutions. The main contributions are:
1) Introducing
information
geometry
causal
inference
(IGCI) to model causal relationships between decision
variables and objectives, providing structural guidance
for search direction and strategy selection.
2) Designing a genetic operator that combines causal in-
ference with Gaussian perturbation. By identifying pos-
itive/negative influences and applying a competitive-
cooperative strategy, the operator improves performance
in complex search spaces.
3) Employing a dual-population collaborative framework
that combines different constraint-handling methods to
enhance feasible solution quality and search diversity,
improving overall optimization performance in complex
feasible regions.
The structure of this paper is organized as follows: Section
II provides a detailed introduction to the primary mechanisms
and methods proposed in this study; Section III presents
the experimental results and performance analysis; Section
IV summarizes the paper and proposes directions for future
research.
II. PROPOSED METHOD
A. Causal Relationship Discovery Based on Information Ge-
ometry
In CMOPs, not all decision variables have a significant
impact on the objective function. Failure to identify these
“key variables” leads to wasted computational resources and
slower convergence. To address this issue, this paper intro-
duces Information Geometric Causal Inference (IGCI) [13],
which automatically detects variables that directly influence
the objective. IGCI is based on a causal inference principle: if
X causes Y (X →Y ), the distribution pX(x) is independent
of the mapping function ϕ, such that Y
= ϕ(X); this
independence typically breaks when the direction is reversed
Y →X. For example, if pX(x) = 1 over [0, 1] and f is
continuous and differentiable, then:
PY (y) =
1
f ′(f −1(y))
(1)
where, PY (y) depends on f ′(x), highlighting the asymmetry
that IGCI leverages to infer causal direction and identify key
variables. By exploiting this property, IGCI evaluates whether
the independence condition holds and, based on this assess-
ment, determines the causal relationship between variables and
the correct causal direction.
More specifically, if the following equality holds:
Z 1
0
log ϕ′(x) · pX(x) dx =
Z 1
0
log ϕ′(x) dx
(2)
where, ϕ′(x) denotes the derivative of the function ϕ, and
pX(x) represents the probability density function of the
variable X. The above equality implies that there exists no
statistical dependence between the distribution of X and the
derivative of the function ϕ, which is consistent with the
non-synergy assumption underlying the true causal direction.
Accordingly, X is regarded as the causal antecedent of Y , that
is, the causal direction X →Y is assumed to hold.
To further quantify the causal effect between variables
and the objectives, this paper employs the Kullback–Leibler
divergence (KL divergence) from information theory as a
measurement tool. If X is indeed a cause of Y , then the KL
divergence difference between X and Y should be less than
0. This difference is referred to as the causal effect value. The
specific formula for this calculation is as follows:
CX→Y = D(pX∥EX) −D(pY ∥EY )
(3)
where, D(p∥q) denotes the KL divergence between the dis-
tribution p and the reference distribution q, and EX and EY
denote the families of reference distributions for X and Y ,
respectively (e.g. uniform or Gaussian distributions).
In implementation, a causal model is individually con-
structed for each decision variable dimension xi with respect
to the objective f(x). The existence of a causal relationship
is assessed using Eq.(2) and Eq.(3). Subsequently, the causal
effect vectors corresponding to all decision variables in the
population are extracted and utilized to guide offspring opti-
mization in subsequent stages.
B. Causality-aware Genetic Operator
In CMOEAs, the generation of high-quality offspring is a
critical factor in improving overall optimization performance.
To address this, a causality-aware genetic operator is proposed
in this study. The operator integrates the IGCI method [13]
218
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:49:06 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 3/6 -->

with the competitive swarm optimizer (CSO) strategy [14].
By quantifying the causal influence of decision variables on
objective functions, the operator employs differentiated search
strategies across variables, thereby facilitating the generation
of more targeted and high-quality offspring. The offspring gen-
eration process consists of two primary stages: (1) CSO-guided
offspring generation mechanism; (2) an adaptive perturbation
guided by causal information.
In the first stage, the operator partitions the current popu-
lation into a winner population (WP) and a loser population
(LP) based on non-dominated sorting. Subsequently, for each
individual in the LP, a winner–loser update strategy, derived
from the CSO, is employed to generate preliminary offspring.
This mechanism guides inferior solutions toward superior
ones, thereby enhancing the overall search efficiency. The
specific update equation is defined as follows:
vl(t + 1) = r1vl(t) + r2 (xw(t) −xl(t))
+ r3ψ (¯x(t), xl(t))
(4)
xl(t + 1) = xl(t) + vl(t + 1),
(5)
where, r1, r2 and r3 are random vectors sampled from
the interval (0, 1). The vectors xl(t) and xw(t) denote the
corresponding solutions from the LP and WP at iteration t,
respectively. The vector ¯x(t) represents the mean position of
the current population. The function ψ(·) serves as a guidance
mechanism constructed based on population-level statistical
information.
In the second phase, the operator further refines the analysis
of causal directionality among decision variables. It leverages
the previously identified causal relationships between decision
variables and objectives. Specifically, it utilizes the causal-
effect vector derived during the initialization phase, along
with the results of non-dominated sorting. For each decision
variable, the operator calculates the difference between its
values in WP and LP, assuming equal population sizes. The
sign of this difference is used to determine the direction of
influence. A positive value indicates a positive causal effect
on the objective. A negative value suggests a negative effect.
Based on this criterion, the decision variables are partitioned
into two sets: positively causal variables (ind1) and negatively
causal variables (ind2). Subsequently, the operator computes
the variance of the causal-effect vector within each set. These
variances are denoted as σ2
1 for ind1 and σ2
2 for ind2, respec-
tively. A Gaussian sampling mechanism is then employed to
perturb the corresponding variables. This perturbation process
is used to generate a new generation of solutions. The update
rule is defined as follows:
PopDec{ind1} = N(0, σ2
1) ∗WinDec{ind1}
+ LosDec{ind1}
(6)
PopDec{ind2} = N(0, σ2
2) ∗WinDec{ind2}
+ LosDec{ind2}
(7)
PopDec ∈{LosDec, WinDec}
(8)
where, N(0, σ2) denotes a Gaussian distribution with zero
mean and variance σ2. WinDec and LosDec represent the
decision variables of individuals in WP and LP, respectively,
both having dimensions of N/2×D. This mechanism reflects
an adaptive regulation of perturbation intensity based on
variable sensitivity. For variables exhibiting larger variances,
which indicate greater divergence in causal effects, stronger
perturbations are introduced to enhance global exploration.
Conversely, for variables with smaller variances, reflecting
more consistent causal effects, weaker perturbations are ap-
plied to facilitate more precise local search.
C. Framework of CAD-CMOEA
Algorithm 1: Procedure of CAD-CMOEA
Input: Population size N, number of objectives M,
max generations before model update gmax
Output: Non-dominated and feasible solution set
Poparchive
1 Pop1 ←Initialize(N, M);
2 Pop2 ←Initialize(N, M);
3 flag ←1;
4 Poparchive ←select N solutions from Pop1 ∪Pop2
using NSGA-II;
5 while termination condition is not met do
6
fr ←IGCI(Pop1 ∪Pop2);
7
off1 ←generate N offspring from Pop1 via
CI-aware operator;
8
off2 ←generate N offspring from Pop2 via
CI-aware operator;
9
Pop1 ←Poparchive ∪Pop1 ∪off1 ∪off2;
10
Pop2 ←Poparchive ∪Pop2 ∪off1 ∪off2;
11
Pop1 ←Select N individuals from Pop1 using
MOEA/D-Epsilon with constraint handling;
12
if Pop2 has converged and flag = 1 then
13
Pop2 ←Select N individuals from Pop2 using
PPS-SPEA-II with constraint handling;
14
flag ←2;
15
else
16
Pop2 ←Select N individuals from Pop2 using
PPS-SPEA-II without constraint handling;
17
flag ←1;
18
end
19
Poparchive ←select N solutions from
Poparchive ∪Pop1 ∪Pop2 using NSGA-II;
20 end
21 return Poparchive
This study incorporates causal inference and causality-aware
genetic operators into the CCMO framework [15], and pro-
poses a novel optimization algorithm, called CAD-CMOEA.
Algorithm 1 comprises the following three key components:
(1) Initialization: The IGCI method is employed to quantify
the causal relationships between decision variables and
objective value, thereby identifying the key decision
219
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:49:06 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 4/6 -->

Initialization
Population 1
Population 2
Population 1 ∪Offspring
Base on PPS-SPEA-II 
Environmental 
Selection
Base on MOEA/D-
Epsilon Environmental 
Selection
Output Non-
dominated 
Feasible Solutions
CSO Optimization
Gaussian Sampling 
Mechanism Generates 
Offspring
Causality-aware Genetic Operator
IGCI Obtains 
Causal Effects
Causal Inference
Population 2 ∪Offspring
Fig. 1: Procedures of the proposed CAD-CMOEA.
variables. This step provides theoretical support for sub-
sequent directional search, enhancing both optimization
accuracy and computational efficiency.
(2) Pop1 Optimization Process: Upon identifying the key de-
cision variables, offspring are generated using causality-
aware genetic operators. Environmental selection is con-
ducted using the MOEA/D-Epsilon mechanism [16],
which ensures the feasibility of solutions and promotes
population diversity.
(3) Pop2 Optimization Process: The optimization process of
Pop2 is similar to that of Pop1, but there are notable
differences during the search phase. The PPS [17] is
integrated with SPEA-II [18] to form the PPS-SPEA-II
algorithm, which is employed for environmental selec-
tion.
Algorithm 1 outlines the procedure of CAD-CMOEA. Ini-
tially, two populations, Pop1 and Pop2, are created, and IGCI
is used to compute the causal-effect vector fr (Lines 1–3). A
flag variable is set to 1 to indicate the search phase of Pop2
(Line 4). NSGA-II is then applied to the combined populations
to generate a non-dominated archive Pop archive (Line 5).
In each iteration, causality-aware genetic operators generate
offspring off1 and off2, which are merged with their parents
to update Pop1 and Pop2 (Lines 7–10). MOEA/D-Epsilon is
used in Pop1 to promote feasibility and diversity (Line 11).
For Pop2, if convergence is detected and flag = 1, PPS-
SPEA-II is used with constraint handling, and flag is set to
2; otherwise, constraints are ignored to encourage exploration
(Lines 13–17). Finally, NSGA-II is applied to Pop archive,
Pop1, and Pop2 to update the archive (Line 19).
To evaluate the convergence of Pop2, we employ a multi-
metric threshold. Convergence is considered to be achieved
when the rate of change in IGD and HV over the last 10
generations is below a predefined threshold, and the maximum
change between the ideal and worst points does not exceed
0.001. Furthermore, convergence is enforced after 70% of the
maximum iterations, even if these conditions are not fully
satisfied. This ensures a smooth transition to the constrained
optimization phase and guides the population toward conver-
gence to the constrained Pareto front (CPF).
To
handle
constraints,
we
apply
different
constraint-
handling techniques to Pop1 and Pop2. Specifically, for
Pop1, the Epsilon-constraint mechanism dynamically adjusts
constraint tightness based on the proportion of feasible solu-
tions. It tightens the constraints when this proportion is low
and relaxes them when it is high. Once 80% of the generations
are completed, Epsilon is set to zero to ensure convergence
toward the feasible region. For Pop2, constraints are initially
ignored to promote progress toward the Pareto front (PF). They
are then gradually introduced to guide convergence toward
the CPF. This strategy balances exploration and convergence,
preventing early local entrapment while improving solution
quality.
III. EXPERIMENTAL STUDY
A. Experimental Setup
To evaluate CAD-CMOEA, we conducted experiments on
the LIR-CMOP benchmark suite [16], comparing it with eight
well-known CMOEAs: CCMO [15], CTAEA [19], EMCMO
[20], NSGA-II [21], PPS [17], ToP [22], CMOES [23], MFO-
SPEA2 [24]. Experimental settings are as follows:
• Decision variables: 60 for all LIR-CMOP1–14 problems.
• Population size: 100 for LIR-CMOP1–12; 105 for LIR-
CMOP13–14.
• Each algorithm runs independently 30 times per problem,
with 300,000 function evaluations per run.
• Comparison algorithms use parameter settings as recom-
mended in their original papers.
B. Experimental Results
On the LIR-CMOP 1–14 benchmark suite, CAD-CMOEA
and six comparative algorithms are each run 30 times. IGD
results are summarized in Table I, with the best values
highlighted in bold. According to the Wilcoxon rank-sum test,
‘+’, ‘−’, and ‘=’ denote whether a comparing algorithm is
significantly better, worse, or statistically similar to CAD-
CMOEA. The results show that CAD-CMOEA outperforms
most of the compared algorithms across the majority of test
problems.
To evaluate the proposed algorithm, two representative
problems (LIR-COMP 3 and LIR-COMP 8) are selected.
LIR-COMP 3 has multiple narrow, discrete feasible regions,
making CPF coverage and diversity maintenance difficult.
LIR-COMP 8 contains large infeasible areas in the objective
space, hindering effective convergence to the CPF.
For LIR-COMP 3, Fig. 2 illustrates the population search
performance of the proposed CAD-CMOEA in comparison
with eight other comparing algorithms. As shown in Fig.
220
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:49:06 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 5/6 -->

TABLE I. Comparison of IGD and HV values between CAD-CMOEA and other state-of-the-art algorithms on LIR-CMOP1–14.
Symbols ‘+’, ‘−’, and ‘=’ indicate results significantly better, worse, or statistically similar to those of CAD-CMOEA,
respectively.
Problem
Metrics
CCMO
CTAEA
EMCMO
NSGA-II
ToP
PPS
CMOES
MFO-SPEA2
CAD-CMOEA
LIR-CMOP1-14
IGD
3/11/0
2/11/1
2/11/1
0/14/0
0/14/0
1/12/1
3/9/2
0/14/0
—
(+/−/=)
HV
2/11/1
2/10/2
2/11/1
0/14/0
0/14/0
1/10/3
3/10/1
0/13/1
—
(b)CCMO
(a)CAD-CMOEA
(c)EMCMO
(d)CTAEA
(f)NSGA-II
(e)PPS
(g)Top
(h)CMOES
(i)MFO-SPEA2
Fig. 2: The feasible non-dominated solutions with the median
IGD indicator are obtained on LIR-COMP3.
2(a) and Fig. 2(e), both CAD-CMOEA and PPS successfully
capture the entire CPF. CAD-CMOEA achieves this through
its dual-population mechanism: one population exploits feasi-
ble high-quality solutions, while the other explores potential
areas using PPS-SPEA-II, with co-evolution enhancing CPF
coverage. PPS identifies the full CPF by initially ignoring
constraints and converging along the UPF, laying the ground-
work for later constraint handling. However, as shown in
Table I, CAD-CMOEA achieves a significantly lower IGD,
indicating better search accuracy and convergence on LIR-
COMP 3. In contrast, the remaining algorithms fail to achieve
full CPF coverage, as shown in Fig. 2(a)– Fig. 2(d) and Fig.
2(f)– Fig. 2(i). This deficiency primarily arises from their
convergence-oriented search tendencies, which compromise
diversity preservation. Consequently, after identifying certain
segments of the CPF, these algorithms tend to become trapped
in local regions due to the discontinuities among different CPF
segments, ultimately failing to discover the remaining portions
of the front.
For the LIR-COMP 8, Fig. 3 presents a comparative analysis
of the population search performance of the proposed CAD-
CMOEA and eight other benchmark algorithms. It is evident
that CAD-CMOEA successfully captures the entire CPF, as
shown in Fig. 3(a). This result benefits from the algorithm’s
key optimization designs: by incorporating causality-based
variable influence information and a Gaussian perturbation
mechanism, the search intensity and direction are adaptively
adjusted, improving solution quality and accelerating conver-
gence toward the Pareto front. Meanwhile, CAD-CMOEA
employs a dual-population cooperative mechanism, where one
population ensures solution feasibility while the other explores
potential regions. Through information exchange between the
two populations, the algorithm enhances search coverage and
global exploration capability, ultimately enabling accurate
identification of the complete CPF. In contrast, although
CCMO, EMCMO, CTAEA, PPS, CMOES and MFO-SPEA2
demonstrate partial convergence toward the CPF, none are
able to achieve full coverage, as illustrated in Fig. 3(b)– Fig.
3(e) and Fig. 3(h)– Fig. 3(i). This limitation primarily stems
from their convergence-biased strategies in individual updating
and mating selection, coupled with the absence of effective
diversity preservation mechanisms. As a result, populations
tend to become trapped in local regions of the front and are
unable to escape from local optima, thereby constraining their
ability to discover the complete CPF. The search limitations
of NSGA-II and ToP are even more pronounced, as depicte
in Fig. 3(f) and Fig. 3(g). Both algorithms fail to traverse
several large-scale infeasible regions, ultimately resulting in
incomplete coverage of the feasible front in the objective
space.
IV. CONCLUSION
Most existing CMOEAs rely on empirical parameter tuning
or heuristic rules, lacking systematic modeling of problem
structures, which often leads to inefficient search and poor CPF
approximation. To address this, we propose a novel causality-
guided adaptive dual-population evolutionary algorithm, CAD-
CMOEA. It leverages causal inference to uncover relation-
ships between decision variables and objectives, enabling the
design of causality-aware genetic operators for high-quality
solution generation. A dual-population co-evolution mecha-
nism is employed, where the primary population searches
for feasible solutions and the auxiliary population explores
potentially feasible regions, enhancing both convergence and
diversity. Experiments on the LIR-CMOP benchmark show
that CAD-CMOEA effectively captures causal dependencies
and outperforms six state-of-the-art algorithms in IGD metric.
However, real-world optimization problems often involve
complex and implicit causal structures, making it challenging
to identify clear relationships between decision variables and
objectives. To tackle this, future work will explore learning-
221
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:49:06 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 6/6 -->

(b)CCMO
(a)CAD-CMOEA
(c)EMCMO
(d)CTAEA
(f)NSGA-II
(e)PPS
(g)Top
(h)CMOES
(i)MFO-SPEA2
Fig. 3: The feasible non-dominated solutions with the median
IGD indicator are obtained on LIR-COMP8.
based methods to embed problems into lower-dimensional
spaces that facilitate causal decomposition and reveal hidden
dependencies. Causal learning will also be extended to capture
relationships involving constraints. Additionally, adaptive and
dynamic causal regulation mechanisms will be developed to
improve the accuracy and robustness of inference, ultimately
enhancing search efficiency and generalization across diverse
constrained optimization problems.
ACKNOWLEDGMENT
This research was supported in part by the National
Science
and
Technology
Major
Project
(grant
number
2021ZD0111502), the National Natural Science Foundation
of China (grant numbers 62441612, 62176147, 62476163),
the Science and Technology Planning Project of Guangdong
Province of China (grant number 2021JC06X549), the Science
and Technology Special Funds Project of Guangdong Province
of China (grant numbers STKJ2021176, STKJ2021019), the
Guangdong Basic and Applied Basic Research Founda-
tion(grant numbers 2022A1515110660, 2023B1515120020,
2024A1515012450), and the STU Scientific Research Foun-
dation for Talents (grant numbers NTF21001, NTF22030).
REFERENCES
[1] W. Li, Z. Wang, R. Mai, P. Ren, Q. Zhang, Y. Zhou, N. Xu, J. Zhuang,
B. Xin, L. Gao et al., “Modular design automation of the morphologies,
controllers, and vision systems for intelligent robots: a survey,” Visual
Intelligence, vol. 1, no. 2, pp. 1–28, 2023.
[2] S. Mahmud, A. Abbasi, R. K. Chakrabortty, and M. J. Ryan, “A self-
adaptive hyper-heuristic based multi-objective optimisation approach
for integrated supply chain scheduling problems,” Knowledge-Based
Systems, vol. 251, p. 109190, 2022.
[3] Y. Xie, D. Wang, and J. Qiao, “Dynamic multi-objective intelligent
optimal control toward wastewater treatment processes,” Science China
Technological Sciences, vol. 65, no. 3, pp. 569–580, 2022.
[4] W. Li, Y. Qiu, Z. Wang, B. Xu, Z. Hao, Q. Zhang, Y. Li, and Z. Fan,
“Surrogate-assisted neural learning and evolutionary optimization for ex-
pensive constrained multi-objective problems,” Swarm and Evolutionary
Computation, vol. 97, p. 102020, 2025.
[5] Q. Yu, C. Yang, G. Dai, L. Peng, and J. Li, “A novel penalty function-
based interval constrained multi-objective optimization algorithm for
uncertain problems,” Swarm and Evolutionary Computation, vol. 88,
p. 101584, 2024.
[6] S. Song, K. Zhang, L. Zhang, and N. Wu, “A dual-population algorithm
based on self-adaptive epsilon method for constrained multi-objective
optimization,” Information Sciences, vol. 655, p. 119906, 2024.
[7] J. Jelovica and Y. Cai, “Improved multi-objective structural optimization
with adaptive repair-based constraint handling,” Engineering Optimiza-
tion, vol. 56, no. 1, pp. 118–137, 2024.
[8] S. Zhao, X. Hao, L. Chen, T. Yu, X. Li, and W. Liu, “Two-stage bidi-
rectional coevolutionary algorithm for constrained multi-objective opti-
mization,” Swarm and Evolutionary Computation, vol. 92, p. 101784,
2025.
[9] J. Pearl, “Causal inference: history, perspectives, adventures, and unifi-
cation (an interview with Judea Pearl),” Observational Studies, vol. 8,
no. 2, pp. 23–36, 2022.
[10] S. Yang, B. Yang, Z. Zeng, and Z. Kang, “Causal inference multi-agent
reinforcement learning for traffic signal control,” Information Fusion,
vol. 94, pp. 243–256, 2023.
[11] X. Lai, H. Li, and Y. Pan, “A combined model based on feature selection
and support vector machine for pm2. 5 prediction,” Journal of Intelligent
& Fuzzy Systems, vol. 40, no. 5, pp. 10 099–10 113, 2021.
[12] H. Deng, B. Yang, M.-Y. Chow, D. Zhu, G. Yao, C. Chen, X. Guan,
and D. Srinivasan, “A decision-dependent hydrogen supply infrastructure
planning approach considering causality between vehicles and stations,”
IEEE Transactions on Sustainable Energy, vol. 15, no. 3, pp. 1914 –
1932, 2024.
[13] B. Li, Y. Yang, P. Yang, G. Li, K. Tang, and A. Zhou, “Causal Inference
Based Large-Scale Multi-Objective Optimization,” IEEE Transactions
on Evolutionary Computation, vol. 29, pp. 444 – 458, 2025.
[14] Y. Tian, X. Zheng, X. Zhang, and Y. Jin, “Efficient large-scale multi-
objective optimization based on a competitive swarm optimizer,” IEEE
Transactions on Cybernetics, vol. 50, no. 8, pp. 3696–3708, 2019.
[15] Y. Tian, T. Zhang, J. Xiao, X. Zhang, and Y. Jin, “A coevolutionary
framework for constrained multiobjective optimization problems,” IEEE
Transactions on Evolutionary Computation, vol. 25, no. 1, pp. 102–116,
2020.
[16] Z. Fan, W. Li, X. Cai, H. Huang, Y. Fang, Y. You, J. Mo, C. Wei,
and E. Goodman, “An improved epsilon constraint-handling method in
MOEA/D for CMOPs with large infeasible regions,” Soft Computing,
vol. 23, pp. 12 491–12 510, 2019.
[17] Z. Fan, W. Li, X. Cai, H. Li, C. Wei, Q. Zhang, K. Deb, and E. Goodman,
“Push and pull search for solving constrained multi-objective optimiza-
tion problems,” Swarm and Evolutionary Computation, vol. 44, pp. 665–
679, 2019.
[18] E. Zitzler, M. Laumanns, and L. Thiele, “SPEA2: Improving the strength
pareto evolutionary algorithm,” TIK Report, vol. 103, 2001.
[19] K. Li, R. Chen, G. Fu, and X. Yao, “Two-archive evolutionary algorithm
for constrained multiobjective optimization,” IEEE Transactions on
Evolutionary Computation, vol. 23, no. 2, pp. 303–315, 2018.
[20] K. Qiao, K. Yu, B. Qu, J. Liang, H. Song, and C. Yue, “An evolutionary
multitasking optimization framework for constrained multiobjective op-
timization problems,” IEEE Transactions on Evolutionary Computation,
vol. 26, no. 2, pp. 263–277, 2022.
[21] K. Deb, A. Pratap, S. Agarwal, and T. Meyarivan, “A fast and elitist
multiobjective genetic algorithm: NSGA-II,” IEEE Transactions on
Evolutionary Computation, vol. 6, no. 2, pp. 182–197, 2002.
[22] Z.-Z. Liu and Y. Wang, “Handling constrained multiobjective optimiza-
tion problems with constraints in both the decision and objective spaces,”
IEEE Transactions on Evolutionary Computation, vol. 23, no. 5, pp.
870–884, 2019.
[23] F. Ming, W. Gong, and Y. Jin, “Even search in a promising region
for constrained multi-objective optimization,” IEEE/CAA Journal of
Automatica Sinica, vol. 11, no. 2, pp. 474–486, 2024.
[24] R. Jiao, B. Xue, and M. Zhang, “A multiform optimization framework
for constrained multiobjective optimization,” IEEE Transactions on
Cybernetics, vol. 53, no. 8, pp. 5165–5177, 2022.
222
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:49:06 UTC from IEEE Xplore.  Restrictions apply.
