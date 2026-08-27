<!--
source: 长篇/LLM-MTPSO_ Large Language Model-Assisted Multi-Task Particle Swarm Optimization for Imbalanced Classification.pdf
sha256: 4ef2d862a11a9b8fc8190e9b8466cecf0c5fac7e9d0aa7912d41bcd888d62d67
method: pymupdf
pages: 6
-->

<!-- page 1/6 -->

LLM-MTPSO: Large Language Model-Assisted
Multi-task Particle Swarm Optimization for
Imbalanced Classification
1st Guanghua Lv
College of Computer Science and Software Engineering
Shenzhen University
Shenzhen, China
2400101051@mails.szu.edu.cn
3rd Jiping Lin
Digital Grid Research Institute Co., Ltd.
China Southern Power Grid
Guangzhou, China
lin ji ping@163.com
2nd Jiahui Wang
College of Computer Science and Software Engineering
Shenzhen University
Shenzhen, China
2210274046@mails.szu.edu.cn
4th Yu Zhou*
College of Computer Science and Software Engineering
Shenzhen University
Shenzhen, China
zhouyu 1022@126.com
Abstract—Imbalanced data widely exists in security-prioritized
domains, where minority classes often bring a disproportionately
high risk. Especially in multi-class scenarios, challenges arise not
only from the imbalance between majority and minority classes,
but also from the difficulty in separating minority classes and
their underrepresentation in the training data. To address these
issues, this paper adopts a One-Versus-One decomposition strat-
egy to transform the multi-class problem into multiple binary
subtasks. This formulation naturally increases the visibility of mi-
nority classes. Furthermore, we propose a large language model-
assisted multi-task particle swarm optimization (LLM-MTPSO)
algorithm. Each subtask is independently optimized via PSO,
while a LLM is leveraged to semantically fuse optimal solutions
among similar subtasks. This mechanism facilitates knowledge
transfer and refinement at the solution level, enhancing the
model’s capacity to recognize minority patterns. Experiments on
nine imbalanced datasets show that the test results of our method
in terms of imbalanced classification accuracy outperform four
classical methods. The ablation experiments indicate that the
introduction of LLM promotes information sharing among sub-
tasks, thus improving the algorithm performance.
Index Terms—imbalanced classification, large language model,
multi-task learning, particle swarm optimization
I. INTRODUCTION
In the domain of industrial fault diagnosis, medical analysis,
and financial fraud detection, imbalanced data is prevalent.
As more types of data are continuously increasing in volume,
identifying the minority classes in massive imbalance datasets
has become increasingly challenging. If at least one class
in the dataset represents significantly fewer instances than
other classes, the dataset is classified as imbalanced [1]. In
real-world industrial scenarios, machines typically remain in
normal operating conditions, resulting in a significant surplus
of healthy samples compared to fault samples [2]. However,
∗Corresponding author.
despite the extremely low proportion of fault samples, they
often exist diverse failure modes (e.g., bearing wear, shaft mis-
alignment, rotor imbalance). These abnormal vibration signals
with diverse types may indicate equipment failures and directly
affect production safety. Therefore, although the number of
minority class samples is small, they carry the core risks of
system safety. Their importance is not proportional to the
quantity but directly related to the consequences. Considering
imbalanced data classification scenarios, several researchers
have made numerous innovative studies. These studies can
roughly be divided into two categories [3]: the first type is
data-level improvement and the second type is algorithm-level
optimization.
Improvements at the data-level mainly focus on sampling,
including upsampling and downsampling, to rebalance the
number of classes in the original dataset. Oversampling (such
as SMOTE and its variants [4], [5]) alleviates the imbalance
problem by synthesizing minority class samples, while under-
sampling (such as ensemble-based methods like EasyEnsem-
ble [6]) strategically reduces majority class data to retain key
information. However, these methods have inherent limita-
tions: oversampling risks amplifying the noise of the minority
class, and undersampling may discard valuable majority-class
patterns. Especially in complex and imbalanced scenarios,
challenges in generalization and distribution distortion still
exist. At the algorithm level, many methods attempt to adapt
standard classifiers to better handle class imbalance. Cost-
sensitive learning (CSL) is a classical approach that incor-
porates manually defined cost matrices to penalize misclas-
sification of minority classes [7]. However, manual design is
often difficult to generalize and may introduce human bias.
In contrast, evolutionary algorithms (EAs), which simulate
natural selection and genetic variation, have gained attention
2025 International Conference on Machine Intelligence and Nature-Inspired Computing (MIND)
979-8-3315-8768-0/25/$31.00 ©2025 IEEE
107
2025 International Conference on Machine Intelligence and Nature-Inspired Computing (MIND) | 979-8-3315-8768-0/25/$31.00 ©2025 IEEE | DOI: 10.1109/MIND67540.2025.11351785
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:15 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 2/6 -->

for their ability to perform global optimization without requir-
ing gradient information or explicit priors [8]–[10]. Recent
studies have explored EAs in various forms, such as multi-
objective genetic programming [11], set-based feature selec-
tion (FS) [12], and particle swarm optimization (PSO) variants
with customized operators [13], [14]. Despite their success,
most traditional EAs treat all instances equally, making them
prone to favoring the majority class and overlooking minority-
specific patterns. This often leads to biased classifiers with
reduced generalization in extremely imbalanced scenarios [2].
Since 2022, the rise of large language models (LLMs)
has brought new vitality to various fields, offering powerful
capabilities in semantic modeling and contextual reasoning.
To overcome the limitations of traditional EAs in handling
imbalanced classification, we propose a large language model-
assisted multi-task PSO (LLM-MTPSO) framework. By de-
composing the original task into multiple One-Versus-One
(OVO) subtasks, the model allows for finer-grained learning
of minority class distinctions and reduces optimization bias.
Furthermore, LLMs are leveraged to semantically fuse optimal
solutions from similar tasks, enhancing the overall knowledge
integration at the solution level. This synergy between task
decomposition and LLM-guided fusion enables the algorithm
to better capture minority-relevant patterns. Experimental re-
sults on nine imbalanced datasets validate the effectiveness
of the proposed method compared with several representative
baselines.
II. RELATED WORK
In recent years, Multi-Task Learning (MTL) has gradually
demonstrated advantages in imbalanced classification prob-
lems. MTL splits complex original tasks into multiple sub-
tasks, such as the OVO or One-Versus-Rest (OVR) structure,
enhancing the local exposure of minority class samples to
alleviate biases dominated by majority classes [15]. In the
field of high-dimensional FS, EAs are widely used for sub-
task optimization due to their gradient-free property and global
search capability. For example, MEL [16], PSO-based multi-
task evolutionary learning significantly improves FS perfor-
mance through independent particle swarms and information
sharing mechanisms. Although the combination of MTL and
EAs has made theoretical and experimental breakthroughs, it
still has critical limitations [17]. When sub-tasks have severe
class imbalance, EAs often optimize for overall performance,
ignoring the personalized optimization needs of minority
classes. This may lead to negative transfer or majority class
bias, affecting model generalization.
Recent studies have explored introducing semantic or
knowledge-aware mechanisms into EAs to enhance the refined
performance of migration strategies. For instance, some works
introduce gradient coordination mechanisms like PCGrad [18]
to reduce conflicts between sub-tasks, but these methods
primarily focus on numerical optimization rather than semantic
levels [19]. In the domain of EAs, researchers have proposed
population structure-aware strategies like co-evolution and
multi-factor evolution [20], yet these still rely on explic-
itly predefined task interactions and lack automatic semantic
alignment mechanisms. Meanwhile, LLMs have demonstrated
exceptional capabilities in semantic understanding and con-
text modeling. Recent attempts have combined LLMs with
EAs, such as LMPSO [21] introducing prompt-based semantic
update mechanisms in PSO, and using LLMs for automatic
generation of evolutionary operators [22]–[24]. Additionally,
embedding LLMs into PSO processes by replacing poorly
performing particle positions with LLM suggestions can ef-
fectively reduce model evaluation costs [25].
However, a key limitation persists in existing methods.
Although MTL facilitates problem decomposition and knowl-
edge transfer, the interaction between sub-tasks still relies
heavily on manually crafted structures, which often overlook
latent inter-task correlations. This leads to rigid and frequently
suboptimal knowledge sharing. To overcome this, we introduce
LLMs as semantic bridges that fuse solutions from similar
tasks within the joint MTL and EA framework. By modeling
semantic affinities, LLMs guide context-aware information
flow and can adaptively emphasize minority-class learning.
Unlike existing studies that primarily focus on prompt tun-
ing or single-task enhancements, our approach enables both
independent sub-task optimization and selective cross-task
integration. This represents a novel direction, as no prior work
has systematically explored sub-task level semantic fusion for
imbalanced classification.
III. PROPOSED METHOD
As shown in Fig. 1(a), samples from different classes in
the original dataset are paired to form multiple binary sub-
datasets. Each sub-dataset corresponding to an independent
sub-task focuses on a unique class pair. During the sub-task
optimization phase, the PSO algorithm is employed to search
for optimal solution in each sub-task’s classification model. By
dynamically adjusting particle positions and velocities, PSO
efficiently explores potential distribution patterns of minority
class samples in sub-feature spaces. Additionally, those in-
volving overlapping classes are grouped into similar task sets.
Within each set, sub-tasks form a knowledge-sharing network
as neighbor nodes. In the iterative optimization process, sub-
tasks can dynamically utilize the historical results of adjacent
modules, and integrate them into new feature information
through the LLM, thus expanding the solution space. Finally,
a soft voting strategy is adopted to probabilistically weight
and fuse predictions from all sub-tasks. The above process
is as shown in Algorithm 1. This design enables semantic-
driven collaboration across sub-tasks while preserving task-
specific optimization. The LLM acts as a mediator that selec-
tively propagates informative knowledge, especially benefiting
minority-class discrimination.
A. Binary Multi-task PSO
In our proposed framework, the original dataset is decom-
posed into a set of OVO binary sub-tasks, each independently
optimized by PSO with a dedicated particle population. This
108
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:15 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 3/6 -->

Fig. 1. Points of different colors represent data of different categories. (a) the way of data partitioning in the algorithm of this paper. (b) an example of using
a LLM for co-evolution in a set of similar tasks. Assume that the current evolving population is S1, and its similar populations are S5 and Sn.
Algorithm 1 LLM-MTPSO Framework
1: Configure algorithm parameters
2: Decompose data into OVO binary classification tasks
3: for each task in task list do
4:
Perform preliminary optimization for the current task
5: end for
6: for each task in task list do
7:
Identify similar tasks for knowledge transfer
8:
Explore the solution space guided by a LLM
9: end for
10: Aggregate final classification results via soft voting
decomposition enhances the visibility of minority classes in
pairwise comparisons by explicitly separating class pairs.
Each particle is represented by a real-valued position vector
X(t)
i
∈Rd and a velocity vector V(t)
i
∈Rd, where d denotes
the solution space dimensionality. Its evolution is guided by
the personal best P(t)
i
and the task-specific global best G(t).
The update rules for the i-th particle at iteration t + 1 are:
V(t+1)
i
= w · V(t)
i
+ c1 · r1 · (P(t)
i
−X(t)
i )
+ c2 · r2 · (G(t) −X(t)
i )
(1)
X(t+1)
i
= X(t)
i
+ V(t+1)
i
,
(2)
where w, c1, c2 are hyperparameters controlling inertia and
acceleration; r1, r2 ∼U(0, 1) are random values drawn from
a uniform distribution [26].
When multiple sub-tasks share overlapping samples, they
are grouped as neighboring tasks. For knowledge transfer, we
introduce a crossover operation between the global best of the
current task G(t) and that of a randomly selected neighbor
G(t)
neighbor. This strategy allows the algorithm to incorporate
complementary information across tasks without requiring
full model retraining. By leveraging the structural similarity
among neighboring tasks, the crossover not only facilitates
knowledge reuse but also encourages adaptive exploration in
underrepresented decision regions. The updated global best
ˆG(t) is calculated as:
ˆG(t) = (1 −cr) · G(t) + cr · G(t)
neighbor,
(3)
where cr ∈[0, 1] is the crossover rate. If the new position
ˆG(t) yields better fitness than the current G(t), it will replace
the current global best and be propagated to all particles
for subsequent updates. This mechanism enhances swarm
diversity and mitigates the risk of premature convergence.
B. LLM-assisted Exploration of Diversity
To enhance the search diversity and facilitate cross-task
knowledge transfer, we introduce a LLM as a knowledge
explorer that drives co-evolution among similar tasks. As
illustrated in Fig. 1(b), the LLM acts as an intelligent fusion
engine that collects global best solutions from multiple popu-
lations and provides guidance for generating new exploratory
solutions. Unlike conventional strategies that rely solely on
stochastic variation or fixed fusion rules, LLM can adaptively
capture latent semantic associations between tasks, offering
109
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:15 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 4/6 -->

more context-aware and informed search directions. This se-
mantic reasoning capability helps overcome the limitations of
manually designed transfer operators.
During the evolutionary process, sub-tasks that share over-
lapping samples are grouped into similar task sets (e.g., S1,
S5, and Sn). At each iteration, the global best positions from
the current population and its similar neighbors are fed into the
LLM in the form of real-valued vectors. Each vector represents
the feature weights of a solution, where each element lies in
[0, 1], indicating the importance of a corresponding feature.
This structure allows the LLM to operate on a unified semantic
space, making it feasible to generalize across different task
sets. As shown in Algorithm 2, a prompt is constructed to
instruct the LLM to act as a FS expert, assisting in fusing
knowledge from multiple related tasks. The input consists of
global best position vectors from the current population and its
neighbors, and the LLM outputs a new exploratory candidate
ˆG(t). The position ˆG(t) is evaluated by the fitness function
f(·) and compared with the current global best G(t):
G(t) =
( ˆG(t),
if f( ˆG(t)) < f(G(t)),
G(t),
otherwise.
(4)
If the new candidate provides a better fitness, it replaces the
current global best and is propagated to all particles to guide
their updates in the next iteration. In addition, the invocation
of LLM is not unlimited. We stipulate that it is invoked once
every f = 10 iterations, and for other iterations, formula 3 is
used for random crossover to explore diversity. This hybrid
design balances the computational cost of LLM calls with
the benefits of semantic-level knowledge fusion, ensuring both
efficiency and effectiveness during the optimization process.
Algorithm 2 LLM-assisted Fusion
Require: Iteration index t, fusion frequency f, LLM call
probability p, current global best G(t), group global bests
G, weighting factor α
1: if f > 0 and t mod f = 0 then
2:
if G̸ = ∅and rand() < p then
3:
Collect global best vectors from G and current G(t)
4:
Construct prompt and invoke LLM
5:
Generate binary mask using a random threshold
6:
Evaluate fitness of the fused solution
7:
if fused fitness improves over current G(t) then
8:
Update G(t) in a crossover way
9:
Apply random perturbation and clip values
10:
Update current global best and its fitness value
11:
end if
12:
end if
13: end if
This LLM-assisted mechanism introduces semantic-level
diversity into the swarm, allowing knowledge to flow across
tasks while respecting the problem structure. As a result,
the optimization process not only preserves the local con-
vergence behavior of each sub-population but also gains
enhanced global exploration ability through semantically in-
formed knowledge fusion.
IV. EXPERIMENT AND ANALYSIS
A. Parameter Settings and Datasets
The relevant parameters for algorithm design are sum-
marized in Table I. Among them, the cognitive and social
acceleration coefficients (c1 and c2) are both set to 1.49445,
following the constriction coefficient configuration recom-
mended by [27]. For LLM-based fusion, the crossover rate
cr is randomly initialized in (0, 1) and adaptively selected
from [0.6, 0.9] to promote meaningful knowledge transfer.
The datasets used in the experiment is selected from [28].
The dataset consists of two parts. One part is the TE bench-
mark, and the other part is the industrial dataset in the real
world. The dataset information is summarized in Table II.
The industrial dataset is derived from a bearing test rig that
simulates actual working conditions, including vibration data
of 4 fault types under 4 working conditions (2 loads × 2
speeds). Sampled at 25.6 kHz, it undergoes extraction of
33-dimensional features and is divided into a 200-sample
imbalanced training set and the remaining test set.
B. Compared Algorithms and Evaluation Metrics
We compared with four imbalanced ensemble algorithms
on the industrial dataset and the TE dataset. These algo-
rithms include Self-paced Ensemble [29], BalanceCascade [6],
SMOTEBoost [30], and AsymBoost [31]. Among them, Self-
paced Ensemble is an ensemble method based on the self-
paced learning strategy. It effectively addresses the data imbal-
ance problem by gradually screening samples and dynamically
adjusting the ensemble model. Similar to BalanceCascade, it
mainly balances the data distribution through sample under-
sampling. On the other hand, SMOTEBoost increases the num-
ber of minority class samples through sample oversampling,
and AsymBoost adjusts the model’s learning process by as-
signing different weights to samples of different classes. Com-
pared with these techniques, our method emphasizes multi-task
evolutionary optimization, enabling sub-task specialization and
richer representation learning for minority classes. In addition,
the integration of LLM facilitates solution-level knowledge
fusion across related tasks, complementing local learning with
semantic-aware guidance.
In this study, the optimization objective of our proposed
algorithm is defined as the minimization of 1−G-mean, which
reflects the trade-off between sensitivity and specificity and is
particularly suitable for evaluating performance on imbalanced
classification tasks. Additionally, to evaluate the classification
performance, we adopt Balanced Accuracy (BAC) as the
evaluation metric. BAC is widely used in imbalanced learning
scenarios, as it provides a fair evaluation across classes by
equally weighting sensitivity and specificity. It is defined as
follows:
BAC = 1
2

TP
TP + FN +
TN
TN + FP

(5)
110
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:15 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 5/6 -->

TABLE I
ALGORITHM CONFIGURATION PARAMETERS
Parameter
Description
rmp
Random mating probability for cross-task knowledge
transfer, set to 0.6
T
Total number of iterations (default: 100)
cr
Crossover rate for LLM-based fusion, randomly ini-
tialized in (0, 1), later selected from [0.6, 0.9]
d
Number of features in the dataset
N
Number of particles in the swarm, set to d // 3
c1
Cognitive coefficient, set to 1.49445
c2
Social coefficient, set to 1.49445
w
Inertia weight, become smaller as the number of
iterations increases
TABLE II
DETAILS OF DATASETS USED IN THE EXPERIMENT
Dataset
number
Dataset
type
Imbalanced
ratio
Conditions of
manufacture
1
industry
10
1200rpm 0N
2
industry
10
1200rpm 3000N
3
industry
10
600rpm 0N
4
industry
10
600rpm 3000N
5,6,7,8,9
TE
10,20,30,40,50
–
where TP, TN, FP, and FN denote the numbers of true
positives, true negatives, false positives, and false negatives,
respectively.
C. Results and Analysis
As shown in Table III, we compared the average test
performance of these methods. The optimal BAC obtained
on each dataset will be shown in bold. Significance testing
is represented by the column ST. The column ST represents
the statistical Wilcoxon significance test results of the corre-
sponding method relative to LLM-MTPSO (significance level
is 5%). ”+” or ”−” indicates that the result is significantly
better or worse than LLM-MTPSO, and ”≈” indicates that
their performance is similar.
The results clearly demonstrate the superior performance
of LLM-MTPSO in most cases. Specifically, LLM-MTPSO
achieves the highest BAC scores on seven datasets. In datasets
Fig. 2.
Ablation study on the impact of LLM. The results show that
incorporating the LLM module improves the BAC across most datasets.
TABLE III
BAC PERFORMANCE COMPARISON ACROSS DATASETS.
Dataset
number
Method
Mean(std)
ST
1
SelfpacedEnsemble
0.80(0.01)
−
BalanceCascade
0.80(0.01)
−
SMOTEBoost
0.91(0.01)
−
AsymBoost
0.90(0.01)
−
LLM-MTPSO
0.96(0.01)
2
SelfpacedEnsemble
0.77(0.02)
−
BalanceCascade
0.71(0.02)
−
SMOTEBoost
0.97(0.01)
≈
AsymBoost
0.97(0.01)
≈
LLM-MTPSO
0.98(0.01)
3
SelfpacedEnsemble
0.72(0.01)
−
BalanceCascade
0.72(0.01)
−
SMOTEBoost
0.87(0.01)
−
AsymBoost
0.85(0.01)
−
LLM-MTPSO
0.88(0.01)
4
SelfpacedEnsemble
0.82(0.02)
−
BalanceCascade
0.81(0.01)
−
SMOTEBoost
0.90(0.01)
≈
AsymBoost
0.90(0.01)
≈
LLM-MTPSO
0.91(0.02)
5
SelfpacedEnsemble
0.51(0.01)
≈
BalanceCascade
0.50(0.01)
≈
SMOTEBoost
0.42(0.01)
−
AsymBoost
0.38(0.01)
−
LLM-MTPSO
0.51(0.01)
6
SelfpacedEnsemble
0.48(0.01)
≈
BalanceCascade
0.48(0.01)
≈
SMOTEBoost
0.32(0.01)
−
AsymBoost
0.30(0.01)
−
LLM-MTPSO
0.49(0.01)
7
SelfpacedEnsemble
0.44(0.01)
−
BalanceCascade
0.44(0.01)
−
SMOTEBoost
0.31(0.01)
−
AsymBoost
0.26(0.01)
−
LLM-MTPSO
0.46(0.01)
8
SelfpacedEnsemble
0.38(0.01)
−
BalanceCascade
0.39(0.01)
−
SMOTEBoost
0.31(0.01)
−
AsymBoost
0.26(0.01)
−
LLM-MTPSO
0.43(0.01)
9
SelfpacedEnsemble
0.41(0.01)
≈
BalanceCascade
0.41(0.01)
≈
SMOTEBoost
0.27(0.01)
−
AsymBoost
0.24(0.01)
−
LLM-MTPSO
0.41(0.01)
1–4, LLM-MTPSO consistently outperforms all baselines. For
the TE datasets (i.e., datasets 5–9), the overall BAC values
are generally lower. Nevertheless, LLM-MTPSO consistently
maintains a leading position with competitive results across
these challenging benchmarks. Statistical testing results further
confirm the significance of the improvements, with most
comparisons showing either superiority (–) or statistical equiv-
alence (≈). These observations validate the effectiveness and
robustness of LLM-MTPSO in handling imbalanced classifi-
cation tasks to some extent.
To verify the impact of the LLM component proposed
in this paper on the overall algorithm, we conducted an
ablation study. As shown in Fig. 2, removing the LLM module
results in a performance drop on most datasets, while some
datasets remain stable. In contrast, incorporating LLM-assisted
fusion generally improves the BAC, especially on datasets with
111
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:15 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 6/6 -->

higher classification difficulty. These results demonstrate that
the LLM component contributes positively to performance and
plays a supportive role in enhancing the generalization ability
of the proposed LLM-MTPSO framework.
V. CONCLUSIONS
In this work, we proposed an LLM-assisted multi-task op-
timization framework to address the challenge of imbalanced
classification, especially the difficulty in recognizing minor-
ity classes. By decomposing the original multiclass problem
into a series of binary subtasks and leveraging LLMs to
fuse knowledge across related tasks, our method effectively
enhances minority class representation and improves classifi-
cation performance. Experimental results on four real-world
industrial datasets and five TE datasets indicated that the
proposed approach achieves a superior performance compared
to traditional ensemble methods. Additionally, this framework
demonstrates the potential of integrating LLMs as semantic-
level knowledge aggregators in evolutionary optimization.
ACKNOWLEDGMENT
This work was supported by grants from the Guangdong
Science and Technology Programme 2024B0101120003, the
Natural Science Foundation China 72271168, the Shenzhen
Science and Technology Program KJZD20230923114111021,
the Guangdong Basic and Applied Basic Research Foundation
2024A1515012485, and the Shenzhen Fundamental Research
Program JCYJ20220810112354002.
REFERENCES
[1] S. Ertekin, J. Huang, L. Bottou, and L. Giles, “Learning on the border:
active learning in imbalanced data classification,” in Proceedings of the
sixteenth ACM conference on Conference on information and knowledge
management, 2007, pp. 127–136.
[2] Y. Yu, L. Guo, H. Gao, and Y. Liu, “Pcwgan-gp: A new method
for imbalanced fault diagnosis of machines,” IEEE Transactions on
Instrumentation and Measurement, vol. 71, pp. 1–11, 2022.
[3] U. Bhowan, M. Johnston, and M. Zhang, “Developing new fitness
functions in genetic programming for classification with unbalanced
data,” IEEE Transactions on Systems, Man, and Cybernetics, Part B
(Cybernetics), vol. 42, no. 2, pp. 406–421, 2011.
[4] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, “Smote:
synthetic minority over-sampling technique,” Journal of artificial intel-
ligence research, vol. 16, pp. 321–357, 2002.
[5] H. Han, W.-Y. Wang, and B.-H. Mao, “Borderline-smote: a new over-
sampling method in imbalanced data sets learning,” in International
conference on intelligent computing.
Springer, 2005, pp. 878–887.
[6] X.-Y. Liu, J. Wu, and Z.-H. Zhou, “Exploratory undersampling for
class-imbalance learning,” IEEE Transactions on Systems, Man, and
Cybernetics, Part B (Cybernetics), vol. 39, no. 2, pp. 539–550, 2008.
[7] W. Pei, B. Xue, M. Zhang, L. Shang, X. Yao, and Q. Zhang, “A survey
on unbalanced classification: How can evolutionary computation help?”
IEEE Transactions on Evolutionary Computation, 2023.
[8] H.-L. Liu, L. Chen, K. Deb, and E. D. Goodman, “Investigating the
effect of imbalance between convergence and diversity in evolutionary
multiobjective algorithms,” IEEE Transactions on Evolutionary Compu-
tation, vol. 21, no. 3, pp. 408–425, 2016.
[9] Z. Ren, T. Lin, K. Feng, Y. Zhu, Z. Liu, and K. Yan, “A systematic
review on imbalanced learning methods in intelligent fault diagnosis,”
IEEE Transactions on Instrumentation and Measurement, vol. 72, pp.
1–35, 2023.
[10] E. H. C´ardenas, H. A. Camargo, and Y. J. T´upac, “Imbalanced datasets
in the generation of fuzzy classification systems-an investigation using a
multiobjective evolutionary algorithm based on decomposition,” in 2016
IEEE International Conference on Fuzzy Systems (FUZZ-IEEE). IEEE,
2016, pp. 1445–1452.
[11] Y. Qing, C. Ma, Y. Zhou, X. Zhang, and H. Xia, “Cooperative coevo-
lutionary multiobjective genetic programming for microarray data clas-
sification,” in Proceedings of the genetic and evolutionary computation
conference, 2021, pp. 804–811.
[12] H. Saadatmand and M.-R. Akbarzadeh-T, “Many-objective jaccard-
based evolutionary feature selection for high-dimensional imbalanced
data classification,” IEEE Transactions on Pattern Analysis and Machine
Intelligence, 2024.
[13] Y. Zhang, Y.-H. Wang, D.-W. Gong, and X.-Y. Sun, “Clustering-guided
particle swarm feature selection algorithm for high-dimensional imbal-
anced data with missing values,” IEEE Transactions on Evolutionary
Computation, vol. 26, no. 4, pp. 616–630, 2021.
[14] D. Moldovan, I. Anghel, T. Cioara, and I. Salomie, “Adapted binary
particle swarm optimization for efficient features selection in the case
of imbalanced sensor data,” Applied Sciences, vol. 10, no. 4, p. 1496,
2020.
[15] Y. Zhang and Q. Yang, “A survey on multi-task learning,” IEEE
transactions on knowledge and data engineering, vol. 34, no. 12, pp.
5586–5609, 2021.
[16] X. Wang, H. Shangguan, F. Huang, S. Wu, and W. Jia, “Mel: efficient
multi-task evolutionary learning for high-dimensional feature selection,”
IEEE Transactions on Knowledge and Data Engineering, 2024.
[17] W. Chen, K. Yang, Z. Yu, Y. Shi, and C. P. Chen, “A survey on
imbalanced learning: latest research, applications and future directions,”
Artificial Intelligence Review, vol. 57, no. 6, p. 137, 2024.
[18] T. Yu, S. Kumar, A. Gupta, S. Levine, K. Hausman, and C. Finn, “Gra-
dient surgery for multi-task learning,” Advances in neural information
processing systems, vol. 33, pp. 5824–5836, 2020.
[19] H. E. Cagnini, S. C. D. Dˆores, A. A. Freitas, and R. C. Barros, “A
survey of evolutionary algorithms for supervised ensemble learning,”
The Knowledge Engineering Review, vol. 38, p. e1, 2023.
[20] Y. Feng, L. Feng, S. Liu, S. Kwong, and K. C. Tan, “Towards multi-
objective high-dimensional feature selection via evolutionary multitask-
ing,” Swarm and Evolutionary Computation, vol. 89, p. 101618, 2024.
[21] Y. Shinohara, J. Xu, T. Li, and H. Iba, “Large language models as
particle swarm optimizers,” arXiv preprint, 2025.
[22] N. van Stein and T. B¨ack, “Llamea: A large language model evolutionary
algorithm for automatically generating metaheuristics,” IEEE Transac-
tions on Evolutionary Computation, 2024.
[23] Y. Shinohara, J. Xu, T. Li, and H. Iba, “Large language models as
particle swarm optimizers,” arXiv preprint arXiv:2504.09247, 2025.
[24] F. Liu, X. Lin, S. Yao, Z. Wang, X. Tong, M. Yuan, and Q. Zhang,
“Large language model for multiobjective evolutionary optimization,” in
International Conference on Evolutionary Multi-Criterion Optimization.
Springer, 2025, pp. 178–191.
[25] S. Hameed, B. Qolomany, S. B. Belhaouari, M. Abdallah, J. Qadir,
and A. Al-Fuqaha, “Large language model enhanced particle swarm
optimization for hyperparameter tuning for deep learning models,” IEEE
Open Journal of the Computer Society, 2025.
[26] J. Kennedy and R. Eberhart, “Particle swarm optimization,” in Proceed-
ings of ICNN’95-international conference on neural networks, vol. 4.
ieee, 1995, pp. 1942–1948.
[27] M. Clerc and J. Kennedy, “The particle swarm-explosion, stability, and
convergence in a multidimensional complex space,” IEEE transactions
on Evolutionary Computation, vol. 6, no. 1, pp. 58–73, 2002.
[28] Y. Zhou, L. Gao, D. Wang, W. Wu, Z. Zhou, and T. Ye, “Imbalanced
multifault diagnosis via improved localized feature selection,” IEEE
Transactions on Instrumentation and Measurement, vol. 72, pp. 1–11,
2023.
[29] Z. Liu, W. Cao, Z. Gao, J. Bian, H. Chen, Y. Chang, and T.-Y. Liu, “Self-
paced ensemble for highly imbalanced massive data classification,” in
2020 IEEE 36th international conference on data engineering (ICDE).
IEEE, 2020, pp. 841–852.
[30] N. V. Chawla, A. Lazarevic, L. O. Hall, and K. W. Bowyer, “Smoteboost:
Improving prediction of the minority class in boosting,” in European
conference on principles of data mining and knowledge discovery.
Springer, 2003, pp. 107–119.
[31] P. Viola and M. Jones, “Fast and robust classification using asymmetric
adaboost and a detector cascade,” Advances in neural information
processing systems, vol. 14, 2001.
112
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:48:15 UTC from IEEE Xplore.  Restrictions apply.
