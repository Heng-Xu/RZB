<!--
source: 长篇/Multi-Objective Genetic Algorithms in Designing Redundant Water Distribution Systems.pdf
sha256: 12ff571e0f0d4780a213e67e55505f16511d1fd7ea433c67b525f00f7be52ea7
method: pymupdf
pages: 6
-->

<!-- page 1/6 -->

 
Multi-Objective Genetic Algorithms in Designing 
Redundant Water Distribution Systems 
 
Matteo Nicolini 
Polytechnic Department of Engineering and Architecture 
University of Udine 
Udine, Italy 
matteo.nicolini@uniud.it 
Abstract—Water supply and distribution systems are critical 
infrastructures whose design heavily influences the operating 
conditions during unexpected demands. Rapid urbanization, 
increasing leakage and ageing infrastructures are the main factors 
responsible for poor performance under different scenarios. 
Water distribution networks have to be designed with the aim of 
reliability, but also with the need of containing costs. In these last 
decades, several Evolutionary Algorithms have been proposed for 
solving such problems, obtaining successful results. The paper 
aims at comparing the performance of two multi-objective genetic 
algorithms in solving a relatively simple optimization problem, for 
which the complete Pareto front has been calculated. The tests 
have been performed on the problem of designing the pipes of a 
two-loop water distribution network where the first objective is the 
minimization of the cost and the second objective is the 
maximization of the redundancy, expressed as the average 
pressure surplus above a minimum required value. The 
performance indices considered keep into account both the 
exploration and the exploitation capabilities of the algorithms. 
Keywords—Water supply, Pressure, Leakages, Reliability, 
Pareto frontier 
I. INTRODUCTION 
Multi-objective evolutionary algorithms (EAs) for the 
planning and management of water supply systems have been 
increasingly adopted in these last decades, especially for the 
resolution of problems with two criteria, the first generally 
represented by costs and the second expressed as some measure 
of the network performance. 
References [1] and [2] were among the first to adopt, 
respectively, a single and a multi-objective EA for the 
rehabilitation of a pressurized network system, minimizing costs 
and, in the second case, maximizing also the benefits. Besides 
the minimization of total cost, [3] introduced the maximization 
of a resilience index, [4] the minimization of the maximum 
pressure deficit at nodes, while [5] took into consideration the 
reliability of the network as an objective to be maximized, an 
approach followed also by [6]. 
In subsequent years, several other approaches were proposed. 
[7] introduced a genetically adaptive multi-objective algorithm, 
[8] a multi-objective particle swarm optimization, [9] a multi-
objective cuckoo-search, while [10] a multi-objective genetic 
algorithm for least cost design and resiliency maximization. 
The best-known approximation of the true Pareto front using 
five standard multi-objective evolutionary algorithms was 
obtained by [11], while [12] used the decomposition method to 
show that it performs better than NSGA-II [13]. A new hybrid 
multi-objective EA was further developed by [14]. An approach 
based on non-dominated sorting differential evolution was 
developed by [15] and [16] for water distribution systems (WDS) 
optimization, including cost and resilience. In these last years, 
further research has been carried out by many authors, especially 
on improving the exploitation capabilities of the algorithms, [17] 
and [18]; in particular, [19] adopted a hybrid NSGA-II algorithm, 
augmented with a random multi-point crossover operator. 
In this work, the performance of two multi-objective genetic 
algorithms (GAs) has been analyzed with reference to a two-
objective optimization problem, for which the Pareto frontier has 
been thoroughly calculated. The tests have been performed on 
the problem of designing the size of the pipes of a two-loop 
water distribution network for which minimization of cost and 
maximization of redundancy are the main objectives. A global 
performance index (the hypervolume, [20]) was compared with 
some more specific indices already introduced by [21], 
quantifying the performance of the solutions in terms of 
exploration and exploitation in approaching the true Pareto 
frontier. 
The paper is organized as follows: Section II presents the 
mathematical formulation of the problem and the benchmark 
network, while Section III illustrates the two multi-objective 
GAs adopted, together with the performance metrics considered; 
Section IV shows the results obtained, and Section V draws 
some concluding remarks. 
II. THE OPTIMIZATION PROBLEM AND THE BENCHMARK 
NETWORK 
The problem of WDS optimization with two conflicting 
objectives is usually aimed at maximizing some performance of 
the network, for example in terms of the reliability, of the 
resilience, or of the redundancy, and minimizing the total costs 
for construction and management. In this work, given the 
theoretical nature of the analyses, a relatively simple problem 
has been assumed, in order to calculate the entire Pareto front. 
A. Analytical formulation 
The problem is formulated as composed of two objective 
functions: the first is aimed at minimizing the overall cost of the 
pipes in the network; the second is the maximization of the 
average pressure surplus at the nodes, with reference to a 
minimum design threshold. In this context, the pressure value at 
2025 International Conference on Machine Intelligence and Nature-Inspired Computing (MIND)
979-8-3315-8768-0/25/$31.00 ©2025 IEEE
101
2025 International Conference on Machine Intelligence and Nature-Inspired Computing (MIND) | 979-8-3315-8768-0/25/$31.00 ©2025 IEEE | DOI: 10.1109/MIND67540.2025.11351874
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:54 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 2/6 -->

each node should always be above the required level, which is a 
constraint for delivering adequate flow to customers. Actually, 
according to the several scenarios and variable working 
conditions to which a system is subjected, both negative 
deviations (deficit) and pressure surplus from the required 
minimum are possible. The mathematical formulation is: 
𝑚𝑖𝑛 𝑓1( 𝑑1, 𝑑2, . . . , 𝑑𝑁𝑝) = ∑
∑
𝑐(𝑑𝑖)𝐿𝑖𝑗
𝑁𝑝
𝑗=1
𝑖∈𝐷
  
() 
𝑚𝑎𝑥 𝑓2( 𝑑1, 𝑑2, . . , 𝑑𝑁𝑝) = ∑
𝐻𝑘−𝐻𝑘
𝑟𝑒𝑞
𝑁𝑛
𝑁𝑛
𝑘=1
         
  () 
Eq. (1) and eq. (2) are subjected to the following physical 
constraints: 
 
∑
𝑄𝑖
𝑖∈𝑛𝑘
−∑
𝑄𝑗
𝑗∈𝑚𝑘
= 𝑄𝑒,𝑘 
() 
 
∑
ℎ𝑓,𝑖
𝑖∈𝑝𝑗
= ∆𝐸𝑗 
() 
Eq. (3) represents water balance (continuity) at each node, 
while eq. (4) the energy conservation along path j . Moreover, 
the following constraints have to be satisfied: 
 
𝐻𝑘≥𝐻𝑘
𝑟𝑒𝑞 
() 
 
𝑑min ≤𝑑𝑖≤𝑑max  , 𝑖∈ℕ 
() 
Eq. (5) requires a minimum required value at each junction, 
while eq. (6) constrains the problem to a discrete set of 
commercial diameters. In the preceding equations, the symbols 
have the following meaning: 
- d1, d2,…, dNp are the Np decision variables representing the 
number of pipes to be designed 
- c (di) and Lij are the cost per unit length and the total length 
of the link j with diameter di 
- D is the set of the ND available commercial diameters 
(ranging from a minimum value, dmin , and a maximum, dmax) 
- Nn is the number of nodes where flow delivery to customers 
takes place (they are also called junctions); each junction, k, is 
characterized by an actual value of piezometric head, Hk , and a 
required one, Hkreq  (note that the piezometric head is the sum of 
the ground elevation and the pressure) 
- Qi,k and Qj,k represent the nk and mk flows, respectively, 
entering or leaving junction k 
- Qe,k is the delivered flow to customers at junction k 
- pj is the number of links belonging to path j  
- hf,i is the head (energy) loss along link i of the path j  
- ΔEj is the head loss along path j: in a closed loop ΔEj = 0 
The optimization problem is solved through a coupling 
between multi-objective GAs and the EPANET v. 3.0 hydraulic 
network simulator [22], adopted to solve the system of equations 
(3) and (4). In particular, the following expression for the unit 
head loss in a pipe has been assumed (CHW is the Hazen-Williams 
roughness coefficient): 
 
ℎ𝑓= 10.668
𝑄1.852𝐿
𝐶𝐻𝑊
1.852𝑑4.871 
() 
B. Benchmark network adopted for the analysis 
The two-loop network shown in Fig. 1 was selected for the 
numerical simulations: it is a well-known literature system 
adopted for benchmark, [1]; all the pipelines have a length of 
1000 m each, and a Hazen-Williams coefficient equal to 130. Fig. 
1 (above) shows the nodal characteristics, while the available 
commercial diameters are (in inches): 1, 2, 3, 4, 6, 8, 10, 12, 14, 
16, 18, 20, 22, 24, with unit costs (in $/m), respectively, of 2, 5, 
8, 11, 16, 23, 32, 50, 60, 90, 130, 170, 300, 550. Fig. 1 (below) 
shows a sketch with the definitions of the actual and the required 
piezometric heads at nodes, together with some examples of 
pressure deficit or surplus. 
Fig. 1. Above: Two-loop network selected for the simulations, and nodal data. 
Below: schematic representation of actual and required piezometric head 
at nodes. 
C. Complete enumeration of the search space and Pareto 
optimal solutions (POS) belonging to the frontier 
The search space of the optimization problem is made up of 
148 solutions and has been entirely explored with an enumerative 
technique. In other words, all solutions have been simulated and 
their main characteristics have been calculated. This allowed the 
derivation of the true Pareto frontier of the problem, which has 
been limited to configurations ranging from the one with the 
lowest cost satisfying all pressure constraints, 419,000 $, to that 
with a maximum cost of 500,000 $. This region has been called 
the Region Of Interest (ROI), and is useful for the calculation of 
some performance metrics, as explained thereafter. 
In particular, 11957 are the solutions within such region of 
the objective function space, and only 33 of them are Pareto 
optimal: Tab. I lists their characteristics in terms of the value of 
the two objective functions, while Fig. 2 their representation in 
the ROI. Notable is the great difference in pressure surplus 
102
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:54 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 3/6 -->

between the first and the second POS, indicating an increase in 
redundancy with little additional cost. 
TABLE I.  
PARETO OPTIMAL SOLUTIONS OF THE PROBLEM 
N. 
Cost ($) 
Average 
surplus (m) 
N. 
Cost ($) 
Average 
surplus (m) 
1 
419000 
6.9956 
18 
460000 
12.5351 
2 
420000 
9.8255 
19 
463000 
12.5485 
3 
423000 
9.8381 
20 
466000 
12.9696 
4 
427000 
9.8808 
21 
469000 
12.9859 
5 
430000 
9.9017 
22 
472000 
13.0174 
6 
436000 
10.7175 
23 
475000 
13.0586 
7 
438000 
10.8633 
24 
476000 
13.4298 
8 
439000 
11.4440 
25 
479000 
13.4560 
9 
442000 
11.5177 
26 
482000 
13.5157 
10 
445000 
11.6188 
27 
485000 
13.6001 
11 
446000 
11.8679 
28 
488000 
13.6664 
12 
448000 
11.9876 
29 
490000 
13.7791 
13 
451000 
12.0117 
30 
493000 
13.7834 
14 
452000 
12.0302 
31 
494000 
13.8983 
15 
454000 
12.0610 
32 
497000 
13.9918 
16 
455000 
12.1849 
33 
500000 
13.9999 
17 
458000 
12.4410 
 
 
 
Fig. 2. Representation of all the solutions within the region of interest, with 
the Pareto optimal solutions evidentiated  
III. MULTI-OBJECTIVE GAS AND PERFORMANCE METRICS 
A. NSGA-II and Controlled NSGA-II (CNSGA-II) 
NSGA-II is an algorithm originally introduced by [13]. Its 
main advantage is that it relies on a crowded tournament selector 
based on the rank of the competing individuals and on their 
crowding distance. Thus, NSGA-II incorporates elitism and it 
does not need to set the value of the niche radius, which is a 
parameter that typically affected the performance of the 
previously introduced NSGA.  
However, NSGA-II suffers because of the way elitism is 
performed: in multi-objective optimization, all solutions 
residing in the first rank are equally good, and have to be 
considered as elite individuals to be kept from one generation to 
the next. But, during the evolution of NSGA-II, often the current 
population is mostly made of individuals of the first rank, and 
these might still be far from the true Pareto front. In such case, 
the elitist approach causes a removal of solutions of non-elitist 
fronts and, as a result, the search process may suffer from 
stagnation or premature convergence. 
The Controlled NSGA-II is an algorithm developed by [23]: 
it is very similar to NSGA-II, but it performs elitism in a 
controlled way, that is, instead of keeping all individuals of rank 
one, each front is forced to have an exponentially decreasing 
number of solutions. In this way, a subset of all non-dominated 
fronts are forced to coexist in the new population, which is 
typically more diverse than that of NSGA-II. Fig. 3 shows the 
difference between the algorithms. 
If we denote with N the size of the population and with K the 
number of fronts into which the current population has been 
sorted, the number of individuals belonging to the i-th front, ni, 
admitted to the next population is given by the following relation 
(r is a reduction factor, r < 1): 
 
𝑛𝑖= 𝑁
1−𝑟
1−𝑟𝐾𝑟𝑖−1 
() 
B. Improvements for the algorithms 
In analyzing the problem of WDS optimization, there are 
some issues that should be addressed and that the algorithms 
proposed in the literature do not directly take into account. A 
first consideration derives from the huge extension of the Pareto 
frontier: in fact, there are solutions that, although mathematically 
optimal, are of no practical interest; therefore, the problem of 
limiting the search to a small area of the frontier arises. 
Fig. 3. Schematic representation of elitism in NSGA-II and Contolled NSGA-
II. 
 
103
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:54 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 4/6 -->

A second issue concerns the discrete nature of the problem, 
so that the search space is actually formed by a finite set of 
possible configurations. During the evolution process, the 
presence of several copies of the same solutions in the optimal 
front may be a cause of premature convergence, preventing the 
exploitation of the algorithm. 
The first issue has been addressed by adding to the second 
objective function a negative penalty term which depends on the 
deviation from the maximum allowable budget, B (p > 0 is a 
penalty factor): 
 
𝑓2
∗= 𝑓2 − 𝑝∙[∑
∑
𝑐(𝑑𝑖)𝐿𝑖𝑗
𝑁𝑝
𝑗=1
𝑖∈𝐷
−𝐵]     
() 
In other words, we penalize the redundancy of those 
solutions having cost beyond that of the budget (for the problem 
examined, B  = 500,000 $).  
The second problem was solved by introducing an additional 
dominance, the epsilon dominance. For a problem with two 
objectives, the first to be minimized and the second to be 
maximized, the classical Pareto dominance can be written as: 
 
(𝑓1
𝑎≤𝑓1
𝑏∩𝑓2
𝑎≥𝑓2
𝑏) ∩(𝑓1
𝑎< 𝑓1
𝑏∪𝑓2
𝑎> 𝑓2
𝑏) 
() 
while in the case of the epsilon dominance, the previous 
relation is transformed into (ε1 and ε2 are small numbers): 
 [(𝑓1
𝑎≤𝑓1
𝑏+ 𝜀1) ∩(𝑓2
𝑎≥𝑓2
𝑏−𝜀2)] ∩[(𝑓1
𝑎< 𝑓1
𝑏+ 𝜀1) ∪
(𝑓2
𝑎> 𝑓2
𝑏−𝜀2)] 
 
() 
The two algorithms described above, NSGA-II and CNSGA-
II, have been modified in order to implement the concept of 
epsilon dominance: the aim of the numerical simulations was to 
verify the impact of these variations on the performance of the 
algorithms. 
C. Performance metrics 
The analyses carried out included two types of performance 
indicators, namely: 
• the hypervolume (HV), a single scalar quantifying the 
amount of the objective function space dominated by the 
Pareto front that the algorithm gradually evolves: since 
the exact frontier of the problem is known, it was decided 
to normalize this index with respect to the maximum 
value of the frontier in the ROI; 
• two indices that quantify, respectively, the convergence 
of the current front towards the real one (convergence 
index, CI, a measure for the exploitation) and the 
distribution of individuals of the generic population 
along the current front (sparsity index of solutions, SI, a 
measure for the exploration). 
The convergence index, CI, is calculated as: 
 
𝐶𝐼=
𝑁𝑓
𝑃𝑂𝑆
𝑁𝑃𝑂𝑆(1 −𝛿) 
() 
where 𝑁𝑓
𝑃𝑂𝑆represents the number of Pareto-optimal 
solutions (POS) ‘found’ by the algorithm at the generic iteration; 
𝑁𝑃𝑂𝑆= 33 is the dimension of P*, that is, the set of POS reported 
in Tab. I. 𝛿 indicates the average of the Euclidean distances 
(normalized with respect to the ROI) of all the individuals 
residing within the ROI from the respective closest Pareto-
efficient solution, and is expressed as: 
𝛿=
1
𝑁𝑅𝑂𝐼∑𝛿𝑖
𝑖
=
1
𝑁𝑅𝑂𝐼∑√(
𝑓1,𝑖
𝑃𝑂𝑆−𝑓1,𝑖
𝑓1,𝑚𝑎𝑥−𝑓1,𝑚𝑖𝑛)
2
+ (
𝑓2,𝑖
𝑃𝑂𝑆−𝑓2,𝑖
𝑓2,𝑚𝑎𝑥−𝑓2,𝑚𝑖𝑛)
2
𝑖
 
() 
where 𝑁𝑅𝑂𝐼 is the number of individuals at the generic 
generation within the region of interest, 𝑓1,𝑖 and 𝑓2,𝑖 are, 
respectively, the cost and the average pressure surplus of the i-
th individual, 𝑓1,𝑖
𝑃𝑂𝑆 and 𝑓2,𝑖
𝑃𝑂𝑆 the same quantities referred to the 
Pareto-optimal solution closest to the i-th individual. (The fact 
that there exists at least one individual closest to a POS is a 
necessary condition to qualify it as being reached, and is 
important for the calculation of the sparsity index.) 𝑓1,𝑚𝑎𝑥 = 
500,000, 𝑓1,𝑚𝑖𝑛 = 419,000, 𝑓2,𝑚𝑎𝑥 = 13.9999, 𝑓2,𝑚𝑖𝑛 = 6.9956; 
these four values delimiting the ROI are reported in Tab. I.  
The sparsity index, SI, is calculated as: 
 
𝑆𝐼=
𝑁𝑟𝑃𝑂𝑆
𝑁𝑃𝑂𝑆(1 −
𝑧𝑚𝑎𝑥
𝑁𝑃𝑂𝑆) (1 −𝜎adim)        
() 
where 𝑁𝑟
𝑃𝑂𝑆 represents the number of POS in P* that have 
been reached by at least one individual in the current population. 
Of course, every solution found by the algorithm lying on the 
real frontier is also reached, but the converse is not necessarily 
true. 𝑧𝑚𝑎𝑥 is the maximum number of adjacent optimal solutions 
not reached, and 𝜎adim takes into account the actual distribution 
of the individuals around the reached Pareto-optimal solutions. 
For further details about the indices see [21]. 
IV. RESULTS AND DISCUSSION 
The simulations performed, on one hand, had the aim of 
comparing the hypervolume metric to the other proposed 
performance indices; on the other, they had the purpose of 
evaluating the improvement, if any, related to the introduction of 
the epsilon dominance. 
Tab. II and Tab. III report the results for NSGA-II and 
CNSGA-II, respectively, obtained with populations of 50 
individuals, mutation probability of adjacent type equal to 1/8 = 
0.125, and 500 generations per run. Note that the mutation 
probability is the inverse of the chromosome’s length, and has 
been kept constant throughout the simulations. The crossover 
probability, of uniform type, was varied between 0 and 1. The 
results represent the average and standard deviation values 
obtained after carrying out 10 runs for every crossover 
probability, each with a different initial seed. 
TABLE II.  
RESULTS FOR NSGA-II 
Performance 
metrics 
Crossover probability, pc 
Mean 
0.00 
0.25 
0.50 
0.75 
1.00 
104
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:54 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 5/6 -->

HVmean 
0.924 
0.924 
0.915 
0.947 
0.990 
0.940 
HVstd dev 
0.142 
0.142 
0.138 
0.104 
0.009 
0.107 
CImean 
0.639 
0.651 
0.477 
0.521 
0.719 
0.601 
CIstd dev 
0.322 
0.326 
0.362 
0.332 
0.203 
0.309 
SImean 
0.684 
0.691 
0.612 
0.636 
0.735 
0.672 
SIstd dev 
0.190 
0.207 
0.205 
0.183 
0.090 
0.175 
Nf POSmean 
21.1 
21.5 
15.8 
17.3 
23.8 
19.900 
Nf POSstd dev 
10.6 
10.8 
11.9 
10.9 
6.6 
10.160 
Nr POSmean 
25.2 
25.3 
24.5 
25.2 
28.1 
25.660 
Nr POSstd dev 
4.6 
4.9 
4.8 
4.1 
2.0 
4.080 
zmax, mean 
3.4 
3.3 
3.4 
2.7 
2.0 
2.960 
zmax, std dev 
2.8 
2.9 
2.8 
2.1 
0.6 
2.240 
 
TABLE III.  
RESULTS FOR CNSGA-II 
Performance 
metrics 
Crossover probability, pc 
Mean 
0.00 
0.25 
0.50 
0.75 
1.00 
HVmean 
0.985 
0.955 
0.951 
0.956 
0.987 
0.967 
HVstd dev 
0.016 
0.106 
0.105 
0.106 
0.011 
0.069 
CImean 
0.607 
0.632 
0.595 
0.687 
0.658 
0.636 
CIstd dev 
0.298 
0.270 
0.296 
0.293 
0.248 
0.281 
SImean 
0.659 
0.647 
0.610 
0.685 
0.715 
0.663 
SIstd dev 
0.161 
0.158 
0.173 
0.165 
0.104 
0.152 
Nf POSmean 
20.1 
20.9 
19.7 
22.7 
21.8 
21.040 
Nf POSstd dev 
9.8 
8.9 
9.7 
9.6 
8.1 
9.220 
Nr POSmean 
26.0 
25.4 
24.7 
26.8 
27.7 
26.120 
Nr POSstd dev 
3.0 
4.0 
4.2 
4.3 
2.2 
3.540 
zmax, mean 
1.8 
2.6 
2.7 
2.5 
2.0 
2.320 
zmax, std dev 
0.4 
2.2 
2.1 
2.2 
0.8 
1.540 
Tables IV and V report the results with reference to the 
modified algorithms, the parameters remaining unchanged. 
From the results, some considerations can be drawn. 
Although there is a general agreement between the values of 
the hypervolume and those of the sparsity and convergence 
indices, there are also some situations in which high values of 
the hypervolume do not correspond to better values of the others. 
One reason is because there are some Pareto optimal solutions 
whose contribution to the hypervolume is only marginal. In 
addition, such discrepancy depends on the shape of the frontier 
and, in particular, on the values of the two objective functions of 
the POS: the problem examined is discrete in nature, and, given 
a value of the cost (first objective), several solutions have that 
value, with different diameters, but with tiny differences in the 
pressure surplus (second objective). This gives rise to very 
similar hypervolume indices, which is a geometric measure in 
the objective space, but likely different values of the other 
metrics, in particular the convergence index and the number of 
POS found, 𝑁𝑓
𝑃𝑂𝑆. On the contrary, the hypervolume is well 
correlated with the number of POS reached, 𝑁𝑟
𝑃𝑂𝑆, especially 
with associated low standard deviation. 
The CNSGA-II is better than the NSGA-II with respect to all 
performance indices and is also characterized by lower standard 
deviation values. 
There is a notable dependence of the performance of the 
algorithms on the variation of the crossover probability. On the 
contrary, the mutation probability was kept constant, because 
some simulations conducted by varying such parameter did not 
show a similar trend. 
Better performances are obtained with the modifications 
made by adding the epsilon dominance: observing Tab. IV and 
Tab. V, a clear improvement in the index values can be noticed, 
especially in the case of the CNSGA-II. 
All the algorithms have difficulties in finding the entire 
Pareto front in one run: this is evident from the values obtained 
for the 𝑁𝑓
𝑃𝑂𝑆 index, both in terms of the mean and of the standard 
deviation. As mentioned before, this can be ascribed to the 
discrete nature of the problem and, above all, to the specific 
values of the objective functions. 
TABLE IV.  
RESULTS FOR  𝜀-NSGA-II 
Performance 
metrics 
Crossover probability, pc 
Mean 
0.00 
0.25 
0.50 
0.75 
1.00 
HVmean 
0.959 
0.926 
0.959 
0.952 
0.990 
0.957 
HVstd dev 
0.107 
0.143 
0.106 
0.105 
0.008 
0.094 
CImean 
0.738 
0.696 
0.760 
0.580 
0.722 
0.699 
CIstd dev 
0.271 
0.353 
0.258 
0.319 
0.189 
0.278 
SImean 
0.783 
0.754 
0.775 
0.712 
0.790 
0.763 
SIstd dev 
0.173 
0.232 
0.168 
0.188 
0.108 
0.174 
Nf POSmean 
24.4 
23.0 
25.1 
19.2 
23.9 
23.120 
Nf POSstd dev 
8.9 
11.6 
8.5 
10.5 
6.2 
9.140 
Nr POSmean 
28.1 
27.5 
28.1 
26.6 
28.3 
27.720 
Nr POSstd dev 
4.3 
5.8 
4.2 
4.3 
2.1 
4.140 
zmax, mean 
2.4 
3.2 
2.7 
2.6 
1.8 
2.540 
zmax, std dev 
2.2 
2.9 
2.2 
2.3 
0.7 
2.060 
TABLE V.  
RESULTS FOR 𝜀-CNSGA-II 
Performance 
metrics 
Crossover probability, pc 
Mean 
0.00 
0.25 
0.50 
0.75 
1.00 
HVmean 
0.997 
0.986 
0.991 
0.986 
0.991 
0.990 
HVstd dev 
0.003 
0.013 
0.009 
0.013 
0.009 
0.009 
CImean 
0.866 
0.637 
0.768 
0.637 
0.768 
0.735 
CIstd dev 
0.053 
0.272 
0.184 
0.266 
0.165 
0.188 
SImean 
0.829 
0.739 
0.781 
0.723 
0.789 
0.772 
SIstd dev 
0.061 
0.120 
0.089 
0.103 
0.104 
0.095 
Nf POSmean 
28.6 
21.1 
25.4 
21.1 
25.4 
24.320 
105
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:54 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 6/6 -->

Nf POSstd dev 
1.7 
8.9 
6.0 
8.7 
5.4 
6.140 
Nr POSmean 
30.1 
27.9 
28.7 
27.6 
28.7 
28.600 
Nr POSstd dev 
1.4 
2.5 
1.8 
2.0 
2.2 
1.980 
zmax, mean 
2.0 
1.9 
2.0 
2.1 
1.7 
1.940 
zmax, std dev 
0.8 
0.5 
0.8 
0.7 
0.5 
0.660 
 
V. CONCLUDING REMARKS 
The work has presented the results of a series of simulations 
aimed at defining the performance of two evolutionary 
algorithms adopted for the multi-objective, optimal design of 
pressurized water distribution systems. The two objective 
functions considered are the total cost and the average pressure 
surplus, which is a good measure for the redundancy and hence 
the reliability of the network. 
Some ad hoc indices were introduced in order to measure the 
exploration and exploitation capabilities of the algorithms, and 
to compare their values to those of the hypervolume, a widely 
index used in the literature. The algorithms were then modified 
to overcome problems typically present in the optimization of 
water distribution networks, that is, limited extension of the 
Pareto frontier of interest and discrete nature of the problem. The 
proposed indices allowed to confirm the validity of the 
hypervolume as a global measure of the performance of a multi-
objective GA even in this particular problem case considered, 
although with some exceptions due to the particular values of the 
objective functions. 
The modifications introduced for keeping into account ε-
dominance allowed to obtain better results in terms of 
convergence and sparsity indices, if compared to the original 
versions of the same algorithms. 
REFERENCES 
[1] 
D.A. Savic, and G.A. Walters, “Genetic algorithms for least-cost design 
of water distribution networks,” J. Water Resour. Plann. Manage., vol. 
123, no. 2, pp. 67-76, February 1997. 
[2] 
D. Halhal, G.A. Walters, D. Ouazar, and D.A. Savic, “Water network 
rehabilitation with structured messy genetic algorithm,” J. Water Resour. 
Plann. Manage., vol. 123, no. 3, pp. 137-146, May 1997. 
[3] 
E. Todini, “Looped water distribution networks design using a resilience 
index based heuristic approach,” Urban Water, vol. 2, no. 2, pp. 115-122, 
June 2000. 
[4] 
P.B. Cheung, L.F.R. Reis, K.T.M. Formiga, F.H. Chaudry, and W.C.G. 
Ticona, “Multiobjective evolutionary algorithms applied to the 
rehabilitation of a water distribution system: a comparative study,” in 
EMO ’03: Proc. 2nd Int. Conf. on Evolutionary Multi-Criterion 
Optimization, C.M. Fonseca et al., Eds. Springer-Verlag, 2003, pp. 677-
691. 
[5] 
T.D. Prasad, and N. Park, “Multiobjective genetic algorithms for design 
of water distribution networks,” J. Water Resour. Plann. Manage., vol. 
130, no. 1, pp. 73-82, January 2004. 
[6] 
R. Farmani, G.A. Walters, and D.A. Savic, “Trade-off between Total Cost 
and Reliability for Anytown Water Distribution Network,” J. Water 
Resour. Plan. Manag., vol. 131, no. 3, pp. 161–171, May 2005. 
[7] 
D. Raad, A. Sinske, and J. Van Vuuren, “Robust multi-objective 
optimization for water distribution system design using a meta-
metaheuristic,” International Transactions in Operational Research, vol. 
16, no. 5, pp. 595–626, July 2009. 
[8] 
I. Montalvo, J. Izquierdo, S. Schwarze, and R. Pérez-García, “Multi-
objective particle swarm optimization applied to water distribution 
systems design: an approach with human interaction,” Mathematical and 
Computer Modelling, vol. 52, no. 7–8, pp. 1219–1227, October 2010. 
[9] 
Q. Wang, S. Liu, H. Wang, and D.A. Savic, “Multi-objective cuckoo 
search for the optimal design of water distribution systems,” in Civil 
Engineering and Urban Planning, S. Qu and S. Lin, Eds. ASCE, Reston, 
VA, USA, 2012, pp. 402–405. 
[10] A. Ostfeld, N. Oliker, and E. Salomons, “Multiobjective optimization for 
least cost design and resiliency of water distribution systems,” Journal of 
Water Resources Planning and Management, vol. 140, no. 12, August 
2013. 
[11] Q. Wang, M. Guidolin, D. Savic, and Z. Kapelan, “Two-objective design 
of benchmark problems of a water distribution system via 
MOEAs:towards the best-known approximation of the true Pareto front,” 
Journal of Water Resources Planning and Management, vol. 141, no. 3, 
July 2014. 
[12] J. Yazdi, “Decomposition based multi-objective evolutionary algorithms 
for design of large-scale water distribution networks,” Water Resources 
Management, vol. 30, no. 8, pp. 2749–2766, June 2016. 
[13] K. Deb, S. Agrawal, A. Pratap, and T. Meyarivan, “A fast elitist non-
dominated sorting genetic algorithm for multi-objective optimization: 
NSGA-II”, Proc. Sixth Conference on Parallel Problem Solving from 
Nature, 2000, pp. 849-858. 
[14] Q. Wang, D.A. Savic, and Z. Kapelan, “GALAXY: a new hybrid MOEA 
for the optimal design of Water Distribution Systems,” Water Resources 
Research, vol. 53, no. 3, pp. 1997–2015, February 2017. 
[15] N. Moosavian, and B.J. Lence, “Nondominated sorting differential 
evolution algorithms for multiobjective optimization of water distribution 
systems,” Journal of Water Resources Planning and Management, vol. 
143, no. 4, November 2016. 
[16] N. Moosavian, and B.J. Lence, “Fittest individual referenced differential 
evolution algorithms for optimization of water distribution networks,” 
Journal of Computing in Civil Engineering, vol. 33, no. 6, November 2019. 
[17] S.N. Poojitha, and V. Jothiprakash, “Hybrid differential evolution and 
krill herd algorithm for the optimal design of water distribution networks,” 
Journal of Computing in Civil Engineering, vol. 36, no. 1, October 2021. 
[18] S. Sirsant, and M. Janga Reddy, “Improved MOSADE algorithm 
incorporating Sobol sequences for multi-objective design of Water 
Distribution Networks,” Applied Soft Computing, vol. 120, May 2022. 
[19] M. Naveen Naidu, A. Vasan, M.R.R. Varma, and M.B. Patil, 
“Multiobjective design of water distribution networks using modified 
NSGA-II algorithm,” Water Supply, vol. 23, no. 3, pp. 1220-1233, 
February 2023. 
[20] M. Fleischer, “The measure of Pareto optima,” in: Proc. EMO ’03, 2nd Int. 
Conf. on Evolutionary Multi-Criterion Optimization, Faro, Portugal, 2003, 
pp. 519-533. 
[21] M. Nicolini, “A two-level evolutionary approach to multi-criterion 
optimization of water supply systems”, in: Proc. EMO ’05, 3rd Int. Conf. 
on Evolutionary Multi-Criterion Optimization, Guanajuato, Mexico, 2005, 
pp. 736-751. 
[22] L.A. Rossmann, “An Overview of EPANET Version 3.0,” Proc. of the 
12th Annual Conference on Water Distribution Systems Analysis, Tucson, 
Arizona, USA, 2010. 
[23] K. Deb, and T. Goel, “Controlled elitist non-dominated sorting genetic 
algorithms for better convergence,” in Proc. EMO ’01, 1st Int. Conf. on 
Evolutionary Multi-Criterion Optimization, Zurich, Switzerland, 2001, pp. 
67-81. 
 
106
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:54 UTC from IEEE Xplore.  Restrictions apply.
