<!--
source: 短篇/Preliminary Study for Autonomous Evolutionary Multitasking Method Design.pdf
sha256: 555ed462b62180e57a6bdae7d2587344a1938a403b93e7e9934f27ed1d6f5185
method: pymupdf
pages: 2
-->

<!-- page 1/2 -->

Preliminary Study for Autonomous Evolutionary
Multitasking Method Design
Yuxiao Huang
Department of Data Science and Artiﬁcial Intelligence
The Hong Kong Polytechnic University
Hong Kong SAR
yuxiao.huang@polyu.edu.hk
Liang Feng
College of Computer Science
Chongqing University
Chongqing, China
liangf@cqu.edu.cn
Xuebin Lv
College of Computer Science
Chongqing University
Chongqing, China
lyuxuebin@cqu.edu.cn
Kay Chen Tan
Department of Data Science and Artiﬁcial Intelligence
The Hong Kong Polytechnic University
Hong Kong SAR
kctan@polyu.edu.hk
Abstract—Evolutionary Multi-task Optimization (EMTO) en-
hances optimization performance by sharing knowledge across
optimization tasks. While existing knowledge transfer methods
can improve optimization performance, they often require signif-
icant domain expertise that consume huge expert resources. To
handle this problem, we introduce a preliminary LLM-assisted
framework that autonomously designs knowledge transfer meth-
ods for EMTO without human intervention. Empirical studies
on WCCI competition benchmarks demonstrate that the knowl-
edge transfer methods designed by our proposed framework
can achieve superior performance against existing hand-crafted
knowledge transfer approaches.
Index Terms—Automatic Transfer Optimization, LLM-assisted
Algorithm Design
I. INTRODUCTION
T
HE paradigm of Evolutionary Multi-task Optimization
(EMTO) shows advances by facilitating the knowledge
sharing across multiple related optimization tasks [1]. Central
to EMTO’s success are the knowledge transfer methods that
capture knowledge building-blocks for improved search per-
formance. However, existing EMTO’s designs often demand
deep domain expertise and extensive manual efforts [1].
Studies on large language models (LLMs) have revealed
their strong aptitude for optimization tasks, encompassing
both combinatorial and numerical domains [2]. However,
while these applications show good results, they often suf-
fer from scalability issues when applied to high-dimensional
optimization problems [3]. To overcome these limitations,
researchers have begun using LLMs not as solvers, but as
autonomous agents that design or enhance optimization strate-
gies [4]. Inspired by this direction, we propose an LLM-
assisted framework that autonomously generates effective and
efﬁcient knowledge transfer models for EMTO tasks. The
framework employs few-shot chain-of-thought prompts to
guide LLMs through the design space, enabling automatic
exploration of novel structures within KTM. Furthermore, the
proposed framework also integrates a multi-objective opti-
mization method that balances transfer quality with compu-
tational cost, ensuring both effectiveness and efﬁciency are
considered. Our contributions include:
• Introducing the LLM-driven framework for autonomous
KTM design in EMTO.
• Applying prompt engineering to generate scalable and
high-performing KTMs without expert knowledge.
• Empirical studies demonstrate that the generated models
outperform the hand-crafted approaches across diverse
EMTO scenarios.
II. METHODOLOGY
The paper proposes an optimization approach using large
language models (LLMs) to facilitate the autonomous gener-
ation of high-quality knowledge transfer methods (KTMs) for
EMTO. By formulating KTM generation as a multi-objective
search problem, the framework simultaneously optimizes for
effectiveness (task performance) and efﬁciency (computational
runtime), offering a scalable alternative to hand-crafted trans-
fer methods. At the heart of the framework is a general-
purpose LLM prompted to generate executable KTM designs.
To compensate for the LLM’s lack of inherent knowledge
about EMTO, we develop a structured prompting mechanism
called Few-Shot Chain-of-Thought (FSCOT), which guides
the LLM through a reasoned sequence of design steps, en-
couraging the generation of clear, adaptable, and efﬁcient
algorithm logic. FSCOT prompts deﬁne elements such as
problem pairing, transfer strategies, and solution transfor-
mation within deﬁned constraints—ensuring functional and
interpretable output.
The proposed framework begins with the LLM generat-
ing an initial population of candidate KTMs using FSCOT-
informed prompts. Each KTM is evaluated across a suite of
EMTO tasks, with its normalized value and runtime recorded.
2025 International Conference on Machine Intelligence and Nature-Inspired Computing (MIND)
979-8-3315-8768-0/25/$31.00 ©2025 IEEE
243
2025 International Conference on Machine Intelligence and Nature-Inspired Computing (MIND) | 979-8-3315-8768-0/25/$31.00 ©2025 IEEE | DOI: 10.1109/MIND67540.2025.11351758
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:51:04 UTC from IEEE Xplore.  Restrictions apply.



<!-- page 2/2 -->

A non-dominated sorting strategy is applied to identify Pareto-
optimal KTM candidates that balance both objectives. In each
generation, effective KTMs are selected via roulette wheel
selection. Next, the LLM will be prompted to synthesize
new KTMs based on the structure and performance of these
selected parents. With a small probability, mutation is intro-
duced by prompting the LLM to revise an existing powerful
KTM, maintaining the format while introducing exploratory
changes. In the KTM evolution loop, generated KTMs are
continuously evaluated and compared, with the poorest KTMs
in the population replaced to preserve competitive selection
pressure. This evolution loop proceeds for a predeﬁned num-
ber of generations, resulting in a ﬁnal set of KTMs, which
reﬂect the optimal trade-off between search performance and
computational cost.
Through the integration of multi-objective optimization,
guided prompt engineering, and iterative KTM evolution,
the proposed framework enables autonomous discovery of
efﬁcient and effective transfer strategies—eliminating manual
effort across diverse EMTO scenarios.
III. EXPERIMENTAL STUDY
TABLE I: Comparison of normalized ﬁtness values and aver-
age execution times for VCM, SMM, and the top-performing
KTM (KTM∗), automatically generated by the proposed
method, tested on MTSOO benchmarks across 10 runs. The
superior result in each case is indicated in bold.
Benchmark
VCM
SMM
KTM∗
Nor.V
Time
Nor.V
Time
Nor.V
Time
WCCI1
0.81
76.53
0.55
94.84
0.19
67.79
WCCI2
0.75
81.82
0.20
103.41
0.03
77.25
WCCI3
0.96
79.64
0.88
99.25
0.69
94.85
WCCI4
0.89
80.01
0.83
100.00
0.45
69.30
WCCI5
0.98
83.19
0.92
103.79
0.78
126.65
WCCI6
1.00
80.26
0.86
103.01
0.69
69.16
WCCI7
0.89
84.93
0.84
106.24
0.70
242.21
WCCI8
0.91
84.34
0.94
104.39
0.80
87.40
WCCI9
0.93
83.32
0.96
102.71
0.71
74.55
WCCI10
0.94
83.74
0.98
103.22
0.82
75.35
The proposed framework was evaluated on the CEC2024
MTSOO test suite, which includes ten benchmarks of 50
diverse 50-D tasks derived from classic functions (e.g., Sphere,
Rosenbrock, Ackley). The proposed KTM is compared with
two hand-crafted methods: Vertical Crossover (VCM) [5] and
Solution Mapping with Autoencoder (SMM) [6]. All methods
use the same optimizer [7] with a population of 100, 100 gen-
erations, and 10,000 evaluation times per task. Our framework
maintains a KTM population of 10 for up to 10 generations,
and the LLM runs at temperature 0.5 for prompt-driven code
generation. Performance is measured by normalized values and
runtime (lower is better).
Table I summarizes the performance of the most effective
KTM (i.e., KTM∗) across WCCI benchmarks, based on the
lowest normalized values over 10 runs, compared to VCM
and SMM. While VCM had the shortest runtimes but weakest
transfer ability, SMM offered slight improvements with longer
processing. KTM∗consistently achieved superior results in
both ‘Nor.V’ and ‘Time’. For instance, on WCCI1, it yielded
signiﬁcantly better metrics than both baselines. Competitive
results can also be observed across other benchmarks, conﬁrm-
ing the adaptability and efﬁciency of LLM-designed KTMs in
diverse EMTO conﬁgurations.
IV. CONCLUSION
This paper introduces an LLM-assisted framework for au-
tonomously designing KTMs in EMTO, mitigating the reliance
on expert-crafted models. By combining few-shot prompting
with multi-objective optimization, it balances transfer quality
and efﬁciency. Experimental results on ten 50-task benchmarks
demonstrate that the LLM-generated KTMs signiﬁcantly out-
perform hand-crafted EMTO methods in both accuracy and
runtime, highlighting the framework’s adaptability and scala-
bility for EMTO.
In the future, we would like to extend this approach to
broader EMTO landscapes and integrating more advanced
prompt strategies to enhance model diversity and generaliza-
tion in real-world applications.
V. ACKNOWLEDGEMENTS
This work was supported in part by the National Key R&D
Program of China under Grant 2022YFC3801700; and in
part by the National Natural Science Foundation of China
under Grant U21A20512; and in part by the Research Grants
Council of the Hong Kong SAR under Grant C5052-23G,
Grant PolyU 15229824, Grant PolyU 15218622, and Grant
PolyU 15215623; and in part by the PolyU Start-up Fund
for Research Assistant Professor (RAPs) through the Strategic
Hiring Scheme under Grant P0045620.
REFERENCES
[1] K. C. Tan, L. Feng, and M. Jiang, “Evolutionary transfer optimization-a
new frontier in evolutionary computation research,” IEEE Computational
Intelligence Magazine, vol. 16, no. 1, pp. 22–33, 2021.
[2] X. Wu, S.-h. Wu, J. Wu, L. Feng, and K. C. Tan, “Evolutionary
computation in the era of large language model: Survey and roadmap,”
arXiv preprint arXiv:2401.10034, 2024.
[3] S. Liu, C. Chen, X. Qu, K. Tang, and Y.-S. Ong, “Large language models
as evolutionary optimizers,” arXiv preprint arXiv:2310.19046, 2023.
[4] B. Romera-Paredes, M. Barekatain, A. Novikov, M. Balog, M. P. Kumar,
E. Dupont, F. J. Ruiz, J. S. Ellenberg, P. Wang, O. Fawzi et al.,
“Mathematical discoveries from program search with large language
models,” Nature, vol. 625, no. 7995, pp. 468–475, 2024.
[5] R. Hashimoto, H. Ishibuchi, N. Masuyama, and Y. Nojima, “Analysis
of evolutionary multi-tasking as an island model,” in Proceedings of the
genetic and evolutionary computation conference companion, 2018, pp.
1894–1897.
[6] L. Feng, L. Zhou, J. Zhong, A. Gupta, Y.-S. Ong, K.-C. Tan, and
A. K. Qin, “Evolutionary multitasking via explicit autoencoding,” IEEE
transactions on cybernetics, vol. 49, no. 9, pp. 3457–3470, 2018.
[7] J. Blank and K. Deb, “Pymoo: Multi-objective optimization in python,”
Ieee access, vol. 8, pp. 89 497–89 509, 2020.
244
Authorized licensed use limited to: CHINA UNIVERSITY OF MINING AND TECHNOLOGY. Downloaded on June 30,2026 at 04:51:04 UTC from IEEE Xplore.  Restrictions apply.
