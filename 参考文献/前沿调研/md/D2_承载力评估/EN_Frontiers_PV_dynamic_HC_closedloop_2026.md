<!--
source: D2_承载力评估/EN_Frontiers_PV_dynamic_HC_closedloop_2026.pdf
sha256: e3821432999483d4d1b9f077a7fa8bff7636eccbc38d7d6c4ab9bec9b9275770
method: pymupdf
pages: 13
-->

<!-- page 1/13 -->

 
TYPE Original Research
PUBLISHED 20 May 2026
DOI 10.3389/fenrg.2026.1823435
OPEN ACCESS
EDITED BY
Xizhen Xue,
Nanyang Technological 
University, Singapore
REVIEWED BY
Huayi Wu,
Independent Researcher, 
Guangzhou, China
Feng Li,
Nanjing Normal University, China
*CORRESPONDENCE
Junzhuo Shu,
 15706864948@163.com
RECEIVED 05 March 2026
REVISED 03 April 2026
ACCEPTED 15 April 2026
PUBLISHED 20 May 2026
CITATION
Shu J, Zhao C, Chu B, Wang Y, Wu G 
and Li B (2026) A closed-loop 
framework for PV dynamic hosting 
capacity: integrating physics-informed 
forecasting and stability constraints.
Front. Energy Res. 14:1823435.
doi: 10.3389/fenrg.2026.1823435
COPYRIGHT
© 2026 Shu, Zhao, Chu, Wang, Wu and 
Li. This is an open-access article 
distributed under the terms of the 
Creative Commons Attribution License 
(CC BY). The use, distribution or 
reproduction in other forums is 
permitted, provided the original 
author(s) and the copyright owner(s) are 
credited and that the original 
publication in this journal is cited, in 
accordance with accepted academic 
practice. No use, distribution or 
reproduction is permitted which does 
not comply with these terms.
A closed-loop framework for PV 
dynamic hosting capacity: 
integrating physics-informed 
forecasting and stability 
constraints
Junzhuo Shu*, Chenhui Zhao, Bingshang Chu, Yanhui Wang, 
Guodong Wu and Bo Li
Xuejiawan Power Supply Company of Inner Mongolia Electric Power (Group) Co. Ltd., Ordos, China
The escalating penetration of distributed photovoltaic (PV) generation 
exacerbates the conflict between capacity planning and operational safety, 
primarily due to source-side stochasticity and grid-side fragility. As a pivotal 
quantitative benchmark for grid planning and operation, hosting capacity 
determines the maximum permissible PV integration level that safeguards system 
reliability against operational violations. However, traditional hosting capacity 
assessments, often relying on static snapshots, are inadequate for capturing 
the dynamic coupling among source-side volatility, Static Voltage Stability 
Margin (SVSM), and active control capabilities. To address these challenges, 
this paper proposes a closed-loop analytical framework for Dynamic Hosting 
Capacity (DHC) assessment. First, a physics-informed deterministic forecasting 
model is developed to accurately track PV output volatility and generate Key 
Stress Scenarios (KSS) that characterize realistic operational risks. Subsequently, 
a stability-constrained optimization model is formulated, which explicitly 
incorporates SVSM as a hard constraint to prevent voltage collapse during critical 
heavy-load transitions. To further enhance grid accommodation capability, a 
hierarchical active support mechanism is introduced, employing a centralized-
distributed cooperative control strategy to expand the feasible solution space. 
Case studies on a modified IEEE 33-bus system demonstrate that while SVSM 
constraints reveal latent stability risks by limiting capacity during peak load 
periods, the proposed active support effectively relaxes binding constraints, 
increasing the DHC by approximately 34% compared to passive scenarios. This 
study provides a rigorous, data-driven methodology for balancing safety margins 
with asset utilization in active distribution networks. 
KEYWORDS
active distribution network, cooperative control, distributed photovoltaic, dynamic 
hosting capacity, physics-informed deterministic forecasting, static voltage stability 
 
1 Introduction
The global imperative for carbon neutrality is driving a fundamental transformation 
in power distribution networks, characterized by the rapid integration of Distributed 
Photovoltaic (DPV) generation (Astero, 2023). While DPV is pivotal for decarbonization, its 
high penetration introduces substantial stochasticity and volatility to the grid, challenging
Frontiers in Energy Research
01
frontiersin.org



<!-- page 2/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
 the traditional paradigm of “passive distribution network” 
operation (Zhang et al., 2023). As DPV integration approaches 
saturation in many regions, the distribution network faces 
a dual challenge: the “source-side randomness” stemming 
from intermittent solar irradiance, and the “grid-side stability” 
constraints caused by bidirectional power flows and reduced 
system inertia (Gu et al., 2024). In this context, accurately evaluating 
the Hosting Capacity (HC)—defined as the maximum amount of 
DPV that can be accommodated without violating operational 
constraints—has become a critical task for grid planning and 
operation.
Despite the structural importance of HC assessment, 
existing methodologies face critical limitations in addressing 
the fragmentation between forecasting, assessment, and control. 
Traditional HC assessment often relies on “static snapshot” methods 
or deterministic time-series analysis based on historical data 
(Meng et al., 2024). These approaches typically assume that future 
operating conditions will mirror historical worst-case scenarios 
(Shen et al., 2025). However, in the volatile context of modern 
distribution networks—subject to unpredictable weather variations 
and complex load behaviors—this assumption is frequently violated 
(Tang et al., 2024). Neglecting the high-frequency volatility and 
intermittency of DPV output leads to assessment results that are 
either risky (underestimating uncertainty) or overly conservative 
(ignoring the probability of extreme events), resulting in the 
misallocation of grid assets (Li et al., 2023).
Furthermore, a critical gap emerges in the academic discourse 
regarding the integration of stability constraints and active 
control into the assessment framework. Conventional assessments 
predominantly focus on steady-state power quality indicators, 
such as voltage deviation and thermal loading (Wang et al., 2020; 
Asaad et al., 2023). However, with the increasing integration of 
power electronic interfaces, the Static Voltage Stability Margin 
(SVSM)—the distance to the voltage collapse point—has become 
a limiting factor, especially during heavy-load, low-irradiance 
periods (Werkie et al., 2025; Rahman et al., 2021). Recently, data-
driven approaches using machine learning have been actively 
explored to overcome the computational bottlenecks of traditional 
SVSM analysis, enabling rapid, quasi-real-time stability evaluations 
(Bogod et al., 2024; Li et al., 2022). Despite these methodological 
advancements, directly integrating data-driven SVSM as a dynamic 
hard constraint within hosting capacity optimization remains 
largely unaddressed. Neglecting SVSM can lead to “static safety 
but dynamic instability,” creating hidden risks that conventional 
static or low-resolution methods fail to detect (Yang et al., 2022). 
Simultaneously, advanced voltage control strategies, such as volt-
var control of smart inverters and soft open points, are often 
treated as operational tools rather than planning resources (Sun 
Abbreviations: ADMM, Alternating direction method of multipliers; ADN, 
Active distribution network; CPF, Continuation power flow; CSI, Clear sky 
irradiance; DG, Distributed generation; DHC, Dynamic hosting capacity; 
DNN, Deep neural network; DPV, Distributed photovoltaic; HC, Hosting 
capacity; KSS, Key stress scenarios; LSTM, Long short-term memory; 
MAPE, Mean absolute percentage error; MPPT, Maximum power point 
tracking; MSE, Mean squared error; PSO, Particle swarm optimization; PV, 
Photovoltaic; RMSE, Root mean square error; SVG, Static var generator; 
SVM, Support vector machine; SVSM, Static voltage stability margin; xLSTM, 
Extended long short-term memory.
and Qiu, 2021). Recent state-of-the-art studies have demonstrated 
the immense potential of distributed coordination—such as multi-
agent systems and the Alternating Direction Method of Multipliers 
(ADMM)—in mitigating voltage issues and managing congestion 
in active distribution networks (ADNs) (Yu et al., 2024). While 
these pivotal works theoretically prove that active distributed 
management can expand flexible or dynamic hosting capacity, 
this “Control-Assessment Decoupling” means that the potential 
of active support mechanisms to relax binding constraints is rarely 
quantified in the planning stage (Al-Amin et al., 2026), leading to 
a significant underestimation of the grid’s true hosting capability 
(Han, 2025; Trinh and Chung, 2024).
Specifically, the misalignment between operational capabilities 
and planning assumptions constitutes a fundamental bottleneck. 
In traditional planning paradigms, voltage regulation devices 
are often modeled with conservative, fixed setpoints to simplify 
calculations (Hu et al., 2020). However, in modern ADNs, smart 
inverters and SVGs possess sub-second response capability that 
can dynamically suppress voltage excursions (Hamedi et al., 2023). 
Although recent research has made strides in data-driven real-time 
voltage control (Liu et al., 2025), ignoring this regulation reserve in 
capacity evaluation essentially renders the assessed hosting capacity 
a static, worst-case boundary, rather than a dynamic, technically 
feasible limit. Therefore, establishing a mathematical linkage that 
maps these high-speed distributed control dynamics into steady-
state planning margins is imperative for unlocking the true potential 
of grid infrastructure.
To bridge these gaps, this paper proposes a closed-loop 
analytical framework that integrates physics-informed feature 
extraction, stability-constrained assessment, and hierarchical active 
support. Unlike previous studies that focus on optimizing a 
single algorithm, this work aims to reveal the nonlinear coupling 
mechanisms among prediction, stability, and control. Specifically, 
we construct a data flow that transforms high-fidelity predicted 
trajectories into discrete stress scenarios, enforces SVSM as a hard 
constraint to ensure robustness, and incorporates a centralized-
distributed cooperative control strategy to expand the feasible 
solution space.
The main contributions of this paper are summarized as follows.
1. High-Fidelity Capture of “Volatility Effect”: We establish 
a mapping from temporal volatility features to capacity 
boundaries, revealing how higher confidence requirements 
non-linearly contract the Dynamic Hosting Capacity (DHC). 
By integrating a physics-informed deterministic forecasting 
model, we generate KSS that capture true operational risks 
more accurately than arbitrary worst-case assumptions.
2. Quantification of the “Truncation Effect” of Stability: By 
integrating the SVSM into the assessment model, we identify 
and quantify the capacity reduction caused by stability risks 
during heavy-loading transitions. This approach addresses 
the limitation of conventional methods that overlook the 
bifurcation point proximity, ensuring system robustness 
under extreme conditions.
3. Quantification of the “Gain Effect” of Active Support: We 
propose a hierarchical control mechanism and quantify 
its benefit in terms of capacity expansion. Through a 
centralized-distributed cooperative control strategy utilizing 
Frontiers in Energy Research
02
frontiersin.org



<!-- page 3/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
FIGURE 1
Stability-constrained DHC assessment and support framework.
the Alternating Direction Method of Multipliers (ADMM), 
we demonstrate that active voltage support can significantly 
recover the capacity lost due to uncertainty and stability 
constraints, effectively converting control capabilities into 
additional hosting capacity.
2 Overall framework of 
stability-constrained DHC assessment
To comprehensively address the coupling mechanisms between 
PV volatility, voltage stability, and active control, this study proposes 
a unified closed-loop analytical framework structured into three 
interconnected phases, as illustrated in Figure 1.
First, a physics-informed feature extraction module is 
constructed to handle source-side stochasticity. By introducing 
Clear Sky Irradiance (CSI) for physical normalization and 
employing a CSI-xLSTM network, this phase generates high-
resolution deterministic forecast trajectories, which are further 
condensed into KSS to represent extreme operational risks. 
Subsequently, a stability-constrained capacity assessment model 
transforms these scenarios into a baseline DHC. Unlike static 
methods, this module innovatively integrates the SVSM as a 
hard constraint to prevent voltage collapse during heavy-load 
transitions, utilizing a Deep Neural Network (DNN) surrogate-
assisted optimization to ensure computational efficiency. Finally, 
a hierarchical active support mechanism is introduced to expand 
the feasible solution space. Through a centralized-distributed 
cooperative control strategy based on ADMM, this phase creates 
a feedback loop that quantifies the relaxation effect of active voltage 
regulation on binding constraints, thereby recovering the capacity 
lost to uncertainty and stability limits and yielding the robust, 
maximized Final DHC. 
3 Mathematical modeling and 
algorithm design
3.1 Physics-informed deterministic 
forecasting
The power output of PV systems is fundamentally governed 
by astronomical laws, such as the Earth’s rotation and revolution 
(Chen et al., 2023). Consequently, it exhibits significant periodicity 
and non-stationarity. Utilizing raw data directly for predictive 
modeling often makes it difficult to decouple deterministic trends 
from stochastic fluctuations (Hewamalage et al., 2023). To address 
Frontiers in Energy Research
03
frontiersin.org



<!-- page 4/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
FIGURE 2
Schematic of physics-informed feature extraction.
this, this paper introduces Clear Sky Irradiance (CSI) as a physical 
benchmark for data denoising.
The clear sky irradiance at time t, denoted as Icbr(t), is defined as 
the theoretical solar radiation intensity under cloudless conditions. 
Its calculation model is expressed as Equation 1:
Iclr(t) = Isc · ε · (sin ϕ sin δ + cos ϕ cos δ cos ω)
(1)
where Isc represents the solar constant, ε is the correction factor for 
the sun-earth distance, and ϕ,δ,ω denote the local latitude, solar 
declination angle, and hour angle, respectively.
Furthermore, the clear sky index kcs(t) is defined to normalize 
the original measured irradiance Imeas(t), as shown in Equation 2:
kcs(t) = Imeas(t)
Iclr(t)
(2)
As illustrated in Figure 2, the raw irradiance data (Imeas) contains 
both the deterministic diurnal cycle and stochastic fluctuations. 
By applying the proposed physical normalization, the clear sky 
index (kcs) effectively removes the bell-shaped trend, isolating 
the pure stochastic components caused by cloud movement. This 
stationary feature significantly enhances the learning efficiency of 
the subsequent neural network.
The transformed sequence eliminates the deterministic 
components associated with seasonal and diurnal variations. Its 
numerical fluctuations solely reflect stochastic meteorological 
processes, 
such 
as 
cloud 
shading. 
This 
transformation 
significantly enhances data stationarity, thereby facilitating 
the subsequent model in accurately capturing stochastic 
uncertainties (Boardman et al., 2025).
Addressing the potential scarcity of historical PV data and the 
complex temporal dependencies inherent in the series, this study 
adopts an Extended Long Short-Term Memory (xLSTM) network 
integrated with physical constraints. The superiority of xLSTM 
over standard recurrent architectures lies in its exponential gating 
mechanism and revised memory structures. Solar irradiance data 
is characterized by a superposition of low-frequency diurnal trends 
and high-frequency turbulence caused by cloud motion. Standard 
LSTMs often struggle to retain high-frequency signal details over 
long sequence horizons due to the forgetting gate bias. The xLSTM, 
by contrast, enhances the gradient flow and memory capacity, 
allowing the model to simultaneously capture the macrotrend of 
clear-sky cycles and the micro-fluctuations of rapid shading events. 
This dual-capture capability is crucial for identifying the insufficient 
voltage support scenarios.
The proposed framework comprises an embedding network, a 
recovery network, a generator, and a discriminator. The generator 
utilizes random noise to synthesize latent trajectories, while the 
discriminator is tasked with distinguishing between real and 
synthetic trajectories. The incorporation of xLSTM enables the 
model to capture long-term temporal correlations in PV output 
more effectively. The min-max game objective function of the model 
is formulated as Equation 3:
L = 1
N
N
∑
t=1
(Preal(t) −Ppred(t))
2
(3)
The objective function aims to minimize the Mean Squared 
Error (MSE) between the predicted PV output Ppred(t) and the actual 
measurement Preal(t) .
Finally, based on the high-precision deterministic forecast, KSS 
are identified to capture the most restrictive operating conditions. 
Instead of relying on static worst-case assumptions, we extract 
critical time steps by analyzing the temporal alignment between the 
predicted PV curve and the load profile. 
1. Maximum Reverse Power Flow Scenario: Defined at the time 
step tmax where the net injected power Pnet(t) = P
pred
pv (t) −
Pload(t) reaches its maximum positive value. This captures the 
risk of voltage violation due to surplus generation.
Frontiers in Energy Research
04
frontiersin.org



<!-- page 5/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
FIGURE 3
Identification of KSS in feature space.
2. Insufficient Voltage Support Scenario: Defined at the time 
step tmin where a rapid drop in PV output coincides with a 
heavy load level. This characterizes the risk of voltage collapse 
when active support is suddenly withdrawn.
The distribution of these scenarios is visualized in Figure 3. 
Unlike traditional methods that rely on a single worst-case snapshot, 
our approach identifies distinct clusters of operational risks. The 
Reverse Flow scenarios (marked in red) concentrate in the low-load 
region, while Ramp Risk scenarios (marked in orange) appear in the 
high-load, high-volatility quadrant. This selective extraction ensures 
that the subsequent stability assessment focuses on the most binding 
boundary conditions.
3.2 Stability-constrained capacity 
assessment model
Based on the KSS generated in the feature extraction stage, a 
dynamic optimization model is established to determine the DHC. 
Unlike traditional assessment methods that predominantly focus 
on steady-state limits, this framework innovatively integrates the 
SVSM as a core constraint. The primary objective is to maximize the 
total permissible penetration of DPV across the network over the 
evaluation horizon T, formulated as Equation 4:
max F =
T
∑
t=1
∑
 i∈NPV
PPV,i,t
(4)
where NPV represents the set of PV nodes, PPV,i,t represents the 
active power output of the PV unit at node i at time t. This 
objective is subject to three categories of operational constraints 
under the identified KSS: (i) Power Flow Constraints, which ensure 
the balance of active and reactive power according to Kirchhoff’s 
laws; (ii) Voltage Deviation Constraints, requiring nodal voltages 
Vi,t to remain within the permissible range [Vmin,Vmax]; and (iii) 
Thermal Constraints, ensuring branch power flows do not exceed 
line ratings.
A critical limitation of conventional assessment is the neglect 
of voltage stability in high-impedance networks. The operating 
point may approach the voltage collapse point even when voltage 
magnitudes appear normal. To address this, the SVSM constraint is 
enforced. The SVSM is quantified by the loadability factor λ, defined 
as the multiplier by which the net load can be increased before 
the power flow Jacobian matrix becomes singular. The constraint is 
expressed as Equation 5:
λmax,t ≥ηthreshold,∀t ∈T
(5)
where λmax,t is the maximum loading margin calculated via 
Continuation Power Flow (CPF), and ηthreshold is the required 
safety margin.
Solving this problem is computationally intensive due to the 
iterative nature of CPF. To achieve quasi-real-time assessment, a 
surrogate-assisted strategy is employed. A DNN is trained offline 
to map the input vector x = [PPV,Pload] to the binary stability status 
S. The optimization search is then accelerated by a Hybrid Particle 
Swarm Optimization (PSO) algorithm, where the fitness function 
incorporates the surrogate prediction, as shown in Equation 6:
Fitness(x) = { ∑PPV, if fDNN(x) ≥τ
−∞,
otherwise
(6)
where fDNN is the probability output of the surrogate model and 
τ is the decision threshold (set to 0.5 to align with the perfectly 
balanced training dataset). To strictly prevent false negatives and 
ensure a conservative assessment, the surrogate acts as a rapid 
pre-filter during the heuristic search. Subsequently, any optimal 
candidate passing this threshold is subjected to the exact physical 
CPF model for final verification (as shown in Figure 1), thereby 
balancing computational speed with absolute operational accuracy.
Specifically, the DNN surrogate employs a MLP architecture 
comprising three hidden layers with 128, 64, and 32 neurons, 
respectively. The ReLU activation function is applied across all 
hidden layers to facilitate gradient flow, while a Sigmoid activation 
at the output layer generates the binary classification probability. To 
train this surrogate, an offline dataset comprising 50,000 samples 
was generated utilizing Latin Hypercube Sampling (LHS) to explore 
the comprehensive operational space of PPV and Pload. The rigorous 
CPF algorithm was executed for each sample to assign the ground-
truth stability label. To prevent model bias caused by the natural 
scarcity of unstable operating points, the dataset was balanced using 
a hybrid approach: conducting high-density targeted sampling near 
the theoretical stress boundaries, followed by the application of 
the Synthetic Minority Over-sampling Technique (SMOTE). This 
ensured an exact 1:1 class distribution between stable and unstable 
scenarios in the final training corpus.
To validate the fidelity of the surrogate model, Figure 4 visualizes 
its decision boundary in a two-dimensional projection. The model 
successfully demarcates the Safe Zone from the Risk Zone, correctly 
identifying that system instability is triggered by the combination 
of high system load and insufficient reactive power support. This 
high-precision classification capability justifies its use in the online 
optimization loop.
3.3 Hierarchical active support and 
capacity feedback mechanism
To convert operational voltage regulation potential into 
assessable hosting capacity, this paper establishes a hierarchical 
Frontiers in Energy Research
05
frontiersin.org



<!-- page 6/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
FIGURE 4
Visualization of the stability decision boundary learned by the surrogate model.
active support mechanism. Unlike traditional passive assessments, 
this framework actively utilizes controllable resources to expand 
the feasible solution space. The mechanism consists of a two-stage 
cooperative control strategy and a quantification module that links 
control performance to capacity planning. 
3.3.1 Two-stage hierarchical cooperative control
To balance response speed with global optimality, a distributed 
control model is formulated. The primary objective is to minimize 
system voltage deviation and power losses, subject to power flow and 
device operational constraints, as shown in Equations 7–13:
min F = ∑(SV
k )
2 + ∑γiPi
loss
s.t.V2
i = gi(P,Q)
(P,Q) ∈Ω
(7)
P̲DG
i
≤PDG
i,t ≤P
DG
i
,Q̲ DG
i
≤QDG
i,t ≤Q
DG
i
(8)
P̲PV
i
≤PPV
i,t ≤P
PV
i ,(PPV
i,t )
2 + (QPV
i,t )
2 ≤(SPV
i )
2
(9)
Q̲ SVG
i
≤QSVG
i,t
≤Q
SVG
i
(10)
V̲ i,t ≤Vi,t ≤Vi,t
(11)
Pi,t = PLoad
i,t
−PPV
i,t −PDG
i,t
(12)
Qi,t = QLoad
i,t
−QSVG
i,t
−QPV
i,t −QDG
i,t
(13)
Solving this optimization problem centrally is computationally 
prohibitive for real-time applications. Therefore, a hierarchical 
strategy combining millisecond-level autonomy and minute-level 
coordination is adopted. 
3.3.1.1 Layer 1: millisecond-level autonomous response
To cope with rapid solar irradiance fluctuations, a fast response 
mechanism based on global voltage sensitivity is employed. The 
sensitivity matrix S, derived from the inverse Jacobian of the polar 
coordinate power flow equations, quantifies the direct response of 
nodal voltage to power injections:
[ Δθ
ΔV ] = J−1[ ΔP
ΔQ ] = [SPθ
SQθ
SPV
SQV][ ΔP
ΔQ ]
(14)
Based on the system Lagrangian of Equation 10, the gradient 
of the objective function with respect to active and reactive power 
injections serve as the control signal. The global sensitivities SP
i,t and 
SQ
i,t are derived as:
SP
i,t =
∂L
∂PDG
i,t
= S
Ploss
i,t
+ γiPloss
i
(15)
SP
i,t =
∂L
∂PDG
i,t
= S
Ploss
i,t
+ γiPloss
i
(16)
In the first stage, these sensitivity indices allow local devices to 
autonomously adjust their output in the direction of steepest descent 
for voltage violation mitigation, achieving quasi-instantaneous 
regulation without waiting for global optimization convergence.
However, it is crucial to acknowledge that the voltage 
sensitivity matrices defined in Equations 14–16 inherently rely 
on a linear approximation of the power flow equations. While 
highly effective for small-magnitude, high-frequency stochastic 
fluctuations, this linear assumption inevitably degrades as the system 
operating point approaches the stability boundary characterized 
Frontiers in Energy Research
06
frontiersin.org



<!-- page 7/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
TABLE 1 Configuration of the modified IEEE 33-bus system.
Device 
type
Node index 
(bus no.)
Capacity/
Parameters
Control 
mode
DPV 1
13
0.3 MW
MPPT/Droop
DPV 2
17
0.2 MW
MPPT/Droop
DPV 3
24
0.4 MW
MPPT/Droop
DPV 4
30
0.2 MW
MPPT/Droop
DPV 5
32
0.1 MW
MPPT/Droop
SVG 1
17
±0.8 Mvar
Constant 
Q/Remote
SVG 2
32
±0.4 Mvar
Constant 
Q/Remote
Load model
All load buses
Peak: 
3.715MW + j2.3 
Mvar
Constant power 
(P,Q)
by strong nonlinearities—such as those encountered during the 
KSS identified in Section 3.1. However, within the proposed 
hierarchical framework, this sensitivity-based approximation 
serves exclusively as the Layer one response (millisecond-level), 
prioritizing computational speed to track rapid solar transients. 
The inherent “approximation drift” caused by intense nonlinearity 
under heavy-load stress is systematically corrected by Layer 2. 
The subsequent minute-level ADMM coordination is explicitly 
formulated as a non-linear optimization model (Equation 7), which 
recalculates the exact global power flow and eliminates residual 
voltage violations caused by local greedy linear control, thereby 
guaranteeing operational safety even at the stability margins. 
3.3.1.2 Layer 2: minute-level ADMM coordination
While local autonomy handles high-frequency fluctuations, it 
may lead to suboptimal solutions or boundary violations between 
control areas. To ensure global consistency, the ADMM is applied.
By introducing boundary variables (xbound) and consistency 
variables (z), the coupling constraints between regions are 
decoupled. The augmented Lagrangian function for each region 
k is constructed as Equation 17:
L(xk,z,λ) = f(xk) + ∑
k∈Nk
(λT
kl(xk,bound −zkl) + ρ
2‖xk,bound −zkl‖2
2)
(17)
Through the iterative update of primal variables, dual multipliers 
(λ), and consistency variables, the algorithm eliminates residual 
voltage violations caused by local greedy control, ensuring the 
system operates within safety margins. 
3.3.2 Quantifying control gain for DHC 
assessment
This section connects operational control with planning and 
evaluation. Unlike the traditional DHC evaluation model before, 
which treats voltage as a rigid constraint, the multi-region, multi-
time-scale collaborative control proposed in this section provides 
active voltage support capabilities for the distribution network. To 
quantify the improvement in PV hosting capacity resulting from 
this capability, an active support evaluation model considering 
voltage relaxation constraints is established. Its core principle is to 
transform the adjustment potential of the control system, operating 
autonomously at the second level and collaboratively at the minute 
level, into dynamic relaxation variables for voltage constraints 
in the evaluation model, thereby mathematically expanding the 
feasible region. 
3.3.2.1 Quantifying control capability as evaluation slack
First, for the layer-internal, second-level autonomous method 
based on global sensitivity, the ultimate capability of this dynamic 
process can be statically quantified in the evaluation model. The 
voltage regulation capability provided by layer-internal autonomy 
for node i can be expressed as the weighted aggregation of the 
remaining reactive power capacity of all controllable regulation 
resources within region k with respect to the voltage sensitivity of 
that node, i.e., as shown in Equation 18:
εi,intra = ∑
j∈Ωctrl
(SPV
ij · ΔPj,t + SQV
ij
· ΔQj,t)
(18)
where Ωctrl represents the set of controllable devices belonging to 
the same control area as node i; SPV
ij ,SQV
ij  represent the active power-
voltage sensitivity and reactive power-voltage sensitivity elements 
calculated; and ΔPj,t,ΔQj,t represents the maximum active power 
and reactive power adjustment amounts that can be utilized at node 
j. 
3.3.2.2 Interlayer collaborative relaxation variable 
quantization
For multi-region minute-level coordination based on ADMM, 
the additional voltage improvement capability εi,inter brought about 
by inter-layer collaboration is obtained by solving a simplified linear 
programming subproblem aimed at maximizing regional boundary 
voltage support. Specifically, to obtain the inter-layer relaxation 
component εi,intra for target node i, we construct the following 
linear programming subproblem aimed at maximizing boundary 
voltage support. This model simulates the ultimate effect of the 
ADMM algorithm in extreme operating conditions, where network 
resources are shifted towards heavily loaded regions, as shown in 
Equations 19–21:
max εi,intra = ∑
b∈BK
(SQV
ib · ΔQb + SPV
ib · ΔPb)
(19)
s.t.0 ≤ΔQb ≤ΔQmax
b,N
(20)
Vmin
b
≤Vner
b −SN
bbΔQb ≤Vmax
b
(21)
where BK represents the set of all boundary nodes in region K; 
Equation 20 represents the domain support capacity constraint, 
meaning that the boundary injected power ΔQb cannot exceed the 
remaining capacity ΔQmax
b,N  of the adjacent nodes; and Equation 21 
represents the ADMM collaborative consistency relaxation 
constraint, meaning that the boundary voltage change due to 
injected power cannot cause the domain voltage Vner
b  to exceed 
its limits. 
Frontiers in Energy Research
07
frontiersin.org



<!-- page 8/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
FIGURE 5
Comparison of PV power forecasting results among different methods.
TABLE 2 Performance comparison of feature extraction methods.
Model
RMSE
MAE
MAPE (%)
SVM
0.029
0.021
6.34
LSTM
0.045
0.027
8.06
Proposed method
0.027
0.015
4.53
4 Experiment results
To validate the effectiveness of the proposed framework, numerical 
simulations were performed on a modified IEEE 33-bus distribution 
system. The dataset covers a 60-day operating period with a 
15-min resolution (96 steps/day), incorporating multi-dimensional 
features such as solar irradiance, temperature, and wind speed. 
This period corresponds to the summer months (July-August), 
deliberately selected to encapsulate the most restrictive operational 
conditions. During this season, the grid confronts overlapping stress 
factors: annual peak load demands driven by cooling requirements, 
coupled with high-amplitude PV volatility caused by frequent summer 
convective cloud shading. A CSI-xLSTM generative model is trained 
to capture the stochastic volatility of PV generation. The system 
configuration, including the spatial distribution of DG and SVGs, 
is detailed in Table 1. All load buses are modeled as constant power (P, 
Q) nodes to reflect realistic demand profiles. 
The predictive performance of the proposed method is 
compared against traditional baselines, including Support Vector 
Machine (SVM) and Long Short-Term Memory (LSTM) networks. 
As illustrated in Figure 5, the baseline models exhibit noticeable 
phase lags and smoothing effects during rapid irradiance transitions. 
In contrast, the CSI-xLSTM framework tracks the actual trajectory 
with high fidelity, effectively capturing the sharp power dip around 
12:30 caused by cloud shading.
Table 2 provides a comprehensive quantitative validation of 
the model’s performance. The proposed CSI-xLSTM framework 
demonstrates superior predictive fidelity, minimizing the Root 
Mean Square Error (RMSE) and Mean Absolute Percentage Error 
(MAPE) to 0.027% and 4.53%, respectively. This substantial 
reduction in prediction error creates a robust foundation for the 
subsequent assessment, ensuring that the generated KSS capture 
genuine stochastic volatility rather than numerical artifacts.
Based on the generated KSS, the DHC is evaluated. Figure 6 
contrasts the results between the traditional method (steady-state 
voltage constraints only) and the proposed stability-constrained 
framework.
Distinctly, as the system approaches peak load (approx. 19:00), 
the traditional method erroneously suggests a high hosting capability. 
However, the proposed framework identifies a severe truncation effect 
on capacity peaks. This occurs because the heavy load profile drives 
the operating point toward the “nose” of the P-V curve, activating the 
SVSM hard constraint. The hatched Risk Zone in Figure 6 represents 
capacity that is statically feasible but dynamically unstable, highlighting 
the necessity of stability constraints. 
From a physical perspective, it is imperative to note that the severity 
of the “Truncation Effect” observed in Figure 6 is theoretically sensitive 
to the assumed load characteristics. In this study, as detailed in Table 1, 
loads are modeled as constant power (PQ) nodes. This assumption acts 
as the most conservative scenario for voltage stability; under a pure 
PQ model, an incipient voltage drop forces the load to draw higher 
current to maintain constant power, which subsequently triggers 
heavier line drops and accelerates the approach to the P-V curve “nose” 
point. Conversely, if voltage-dependent loads—such as the constant 
impedance components typical in ZIP models—were prevalent, the 
power demand would naturally diminish alongside nodal voltage sags. 
This inherent self-relieving property would delay voltage collapse 
and increase the physical SVSM. Consequently, the presence of 
voltage-dependent loads would render the stability constraint less 
binding, theoretically mitigating the truncation effect and further 
Frontiers in Energy Research
08
frontiersin.org



<!-- page 9/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
FIGURE 6
Impact of SVSM constraints on dynamic hosting capacity and the identification of hidden stability risks.
FIGURE 7
Convergence performance of the distributed ADMM coordination 
algorithm.
expanding the DHC. By adopting the strict PQ model, the proposed 
framework deliberately evaluates the conservative lower bound of 
hosting capacity to guarantee robust planning margins, though 
future operational models may integrate dynamic ZIP characteristics 
for refined assessments. 
Before evaluating the final hosting capacity, the computational 
performance of the hierarchical coordination layer is verified. 
As shown in Figure 7, the ADMM-based algorithm exhibits robust 
convergence on the modified IEEE 33-bus system. Both primal and 
dual residuals decrease to the tolerance level within 30 iterations, 
confirming that the proposed active support mechanism can be 
executed efficiently within the minute-level operational window.
To achieve this consistent convergence across highly variable 
operational conditions, the penalty parameter ρ was not fixed 
empirically but implemented with a dynamic residual-balancing 
strategy. Specifically, ρ is adaptively updated at the end of each 
iteration to maintain the primal and dual residuals within a 
similar magnitude. If the primal residual significantly exceeds the 
dual residual, ρ is increased to penalize boundary consistency 
violations more heavily; conversely, it is decreased if the dual residual 
dominates. This self-tuning mechanism eliminates the need for 
manual parameter tuning and successfully prevents algorithmic 
stalling, facilitating the rapid convergence observed.
To verify the effectiveness of the hierarchical collaborative control 
strategy proposed in this study for increasing the available capacity 
of distributed photovoltaic systems in distribution networks, this 
section sets up two sets of comparative experiments. By simulating 
photovoltaic DHC under different modes in the IEEE 33-bus system, 
the expansion effect of the active grid support mechanism on the 
feasible region boundary is quantitatively analyzed. 
This experiment selects typical daily load and photovoltaic 
output curves, and compares the impact of the following two 
operating modes on the DHC evaluation results under the same 
prediction uncertainty level (confidence level α = 90%) and SVSM 
constraint (SVSM ≥10%).
To evaluate the spatial impact of the proposed control 
framework, Figure 8 illustrates the nodal voltage profiles along the 
IEEE 33-bus feeder during a critical period of high PV generation. 
Under the Passive Integration (Mode 1), the system suffers from 
severe over-voltage violations at two distinct clusters—Buses 10–17 
and 31–32—with peak magnitudes reaching approximately 1.08 p. 
u., significantly exceeding the statutory 1.05 p. u. safety limit. These 
spatial violations constitute the primary bottleneck that truncates 
the hosting capacity in traditional assessments.
In contrast, the Proposed Active Support (Mode 2)—which 
integrates the hierarchical coordination mechanism—effectively 
suppresses these voltage excursions. As shown in the blue 
profile, the nodal voltages across the entire feeder are regulated 
back within the permissible 1.05 p. u. boundary. The shaded 
“Voltage Violation Mitigation” area quantifies the effectiveness 
Frontiers in Energy Research
09
frontiersin.org



<!-- page 10/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
FIGURE 8
Comparison of voltage profiles along the IEEE 33-bus system under passive and active support modes.
TABLE 3 Sensitivity of dynamic hosting capacity to different SVSM safety margins.
Stability margin η
Static DHC (MW)
Stability-constrained 
DHC (MW)
Capacity reduction (%)
Min. Nodal voltage 
(p.u.)
η = 0.05
6.42
5.85
8.8
0.962
η = 0.10
6.42
5.12
20.2
0.968
η = 0.15
6.42
4.45
30.6
0.975
η = 0.20
6.42
3.82
40.5
0.981
TABLE 4 Quantitative enhancement of hosting capacity under different modes.
Control strategy 
(mode)
Total daily energy 
(MWh)
Max. Instantaneous 
HC (MW)
Avg. Loadability 
factor (λ)
Improvement rate 
(%)
M1: Passive integration
18.5
2.45
10.05
-
M2: Local droop control
21.2
3.10
11.12
+14.6%
M3: Cooperative (proposed)
24.8
4.25
12.28
+34.1%
of the proposed cooperative control in relaxing binding voltage 
constraints. This spatial regulation capability is the fundamental 
driver for the “Gain Effect” observed in the capacity expansion 
results, successfully converting control potential into additional PV 
integration headroom.
As quantified in Table 3, there is a clear trade-off between grid 
stability and PV accommodation. While traditional assessments 
remain constant, the proposed stability-constrained DHC non-
linearly contracts as the required safety margin η increases. Notably, 
even when nodal voltages are within the 0.95–1.05 p. u. range, a 
high stability requirement (η = 0.20) can reduce the permissible 
capacity by over 40%, highlighting the necessity of including SVSM 
in planning.
In the passive scenario (M1), significant voltage violations occur 
at buses 10–17 and 31–32, with peak magnitudes exceeding 1.08 
p. u., which directly limits the further integration of DPV. By 
contrast, the proposed cooperative control effectively regulates the 
nodal voltages back within the statutory 1.05 p. u. limit. The shaded 
“Voltage Violation Mitigation” area highlights the effectiveness of 
the centralized-distributed coordination in relaxing binding voltage 
constraints.
Table 4 provides a quantitative summary of the hosting 
capacity enhancement under three different modes. To ensure 
reproducibility, the local droop control baseline (M2) is 
configured in strict accordance with the IEEE 1547–2018 
standard for smart inverter Volt-Var functions, featuring a voltage 
deadband of ±0.02 p. u. and triggering maximum reactive 
power support at the 0.95 and 1.05 p. u. statutory limits. While 
M2 provides a moderate improvement of 14.6%, the proposed 
hierarchical cooperative control (M3) achieves a substantial 
Frontiers in Energy Research
10
frontiersin.org



<!-- page 11/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
FIGURE 9
Spatial distribution of PV hosting capacity feasible regions across typical network nodes.
gain of 34.1%, increasing the total daily energy integration to 
24.8 MWh. Furthermore, M3 maintains the highest average 
loadability factor (λ), demonstrating that active control not 
only expands the feasible capacity region but also enhances the 
overall grid stability. These results validate the “Gain Effect” 
of active support, proving that coordinating local autonomous 
responses with global optimization can significantly recover 
the hosting capacity previously lost to uncertainty and stability
risks.
To further reveal the spatial universality of the proposed 
method, Figure 9 illustrates the P-Q operating envelopes for nine 
representative nodes across the network. While nodes near the 
substation show limited marginal gains due to strong grid stiffness, 
the weak nodes at the feeder ends exhibit a dramatic expansion in 
their feasible regions. By actively utilizing the reactive power support 
(negative X-axis), the proposed framework effectively overcomes 
the voltage bottlenecks that previously constrained these nodes, 
verifying the Gain Effect reported in Table 4. 
5 Discussion
5.1 The necessity of coupling prediction 
and stability
The results underscore the critical nonlinear coupling among 
prediction uncertainty, voltage stability, and active control. 
Traditional assessments often treat these elements in isolation, 
Frontiers in Energy Research
11
frontiersin.org



<!-- page 12/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
leading to capacity estimates that are either overly optimistic 
(ignoring stability) or overly conservative (ignoring control). Our 
comparative analysis reveals that during peak load transitions, the 
system’s binding constraint shifts from simple voltage deviation 
to voltage stability margins. The proposed CSI-xLSTM framework 
outperforms traditional baselines by effectively capturing high-
frequency fluctuations, thereby generating realistic stress scenarios 
that trigger these stability limits. This proves that high-fidelity 
forecasting is not merely a data requirement but a prerequisite for 
identifying hidden stability risks.
From a practical deployment standpoint, determining the 
optimal safety margin (η) explored in Table 3 should not be a 
one-size-fits-all static assumption. Distribution System Operators 
(DSOs) are advised to determine this threshold through a localized 
risk-cost analysis. Practically, the optimal η should be dynamically 
tailored based on the empirical error bounds of the regional 
forecasting tools—where higher prediction uncertainty necessitates 
a larger stability buffer—and the economic trade-off between the 
financial cost of limiting PV integration and the reliability penalties 
of a potential voltage collapse. 
5.2 The economic value of Virtual Capacity
The Gain Effect observed in the case studies—a 34.1% increase 
in hosting capacity—translates directly into economic benefits. 
By utilizing the proposed hierarchical control to relax binding 
constraints, utilities can defer capital-intensive grid reinforcements. 
The derived “Voltage Violation Mitigation” area can be interpreted 
as Virtual Capacity created by software algorithms rather than 
hardware investment. This suggests that future distribution network 
planning should prioritize the deployment of communication and 
control layers alongside physical infrastructure. 
5.3 Scalability and future work
While the current study validates the framework on a balanced 
IEEE 33-bus system, its application to larger, unbalanced three-
phase networks presents additional challenges. The ADMM-based 
coordination demonstrates good scalability due to its distributed 
nature, but communication latency in real-world deployments 
could degrade the millisecond-level response assumed in Layer 
1. Future work will focus on integrating robust control strategies 
that account for packet loss and delays. Additionally, expanding 
the SVSM constraints to account for phase imbalance will be 
crucial for practical implementation in low-voltage residential
feeders. 
6 Conclusion
This study proposes a closed-loop analytical framework for 
Dynamic Hosting Capacity assessment that integrates physics-
informed feature extraction, stability-constrained optimization, and 
hierarchical active support. Experimental validation on the IEEE 
33-bus system confirms that while SVSM constraints are essential 
for preventing voltage collapse during critical load transitions, the 
proposed centralized-distributed cooperative control effectively 
counteracts the resulting capacity contraction. By recovering 
approximately 20%–34% of the hosting capacity compared 
to passive scenarios, this methodology provides a rigorous, 
data-driven tool for Distribution System Operators to balance 
operational safety with asset utilization, facilitating a paradigm 
shift from passive acceptance to active, stability-aware renewable
integration.
Data availability statement
The original contributions presented in the study are included in 
the article/supplementary material, further inquiries can be directed 
to the corresponding author.
Author contributions
JS: Investigation, Writing – original draft, Conceptualization, 
Writing – review and editing, Methodology. CZ: Methodology, 
Writing – original draft, Formal Analysis, Investigation. BC: 
Methodology, Investigation, Supervision, Writing – original draft, 
Project administration, Funding acquisition. YW: Validation, 
Writing – review and editing, Methodology, Data curation, 
Visualization. GW: Formal Analysis, Writing – original draft, 
Software, Investigation. BL: Writing – review and editing, Validation, 
Methodology, Visualization. 
Funding
The author(s) declared that financial support was received for 
this work and/or its publication. This research was funded by 
Inner Mongolia Power Company, grant number No.: 2025-3-9 and 
the APC was funded by Inner Mongolia Power Company 2025 
Science and Technology Project "Research and Application of Key 
Technologies for Distributed PV Hosting Capacity Assessment and 
Voltage Active Support in Distribution Networks for New-Type 
Power Systems". The funder was not involved in the study design, 
collection, analysis, interpretation of data, the writing of this article, 
or the decision to submit it for publication.
Conflict of interest
Authors JS, CZ, BC, YW, GW, and BL were employed by 
Xuejiawan Power Supply Company of Inner Mongolia Electric 
Power (Group) Co. Ltd.
Generative AI statement
The author(s) declared that generative AI was not used in the 
creation of this manuscript.
Any alternative text (alt text) provided alongside figures in 
this article has been generated by Frontiers with the support of 
artificial intelligence and reasonable efforts have been made to 
ensure accuracy, including review by the authors wherever possible. 
If you identify any issues, please contact us.
Frontiers in Energy Research
12
frontiersin.org



<!-- page 13/13 -->

Shu et al.
10.3389/fenrg.2026.1823435
Publisher’s note
All claims expressed in this article are solely those of the 
authors and do not necessarily represent those of their affiliated 
organizations, or those of the publisher, the editors and the 
reviewers. Any product that may be evaluated in this article, or claim 
that may be made by its manufacturer, is not guaranteed or endorsed 
by the publisher.
References
Al-Amin, Shafiullah, G. M., Shoeb, M., and Ferdous, S. M.(2026). Enhancing EV hosting 
capacity in distribution networks using WAPE-Based dynamic control. Sustainability
18(2), 589. doi:10.3390/su18020589
Asaad, A., Ali, A., Mahmoud, K., Shaaban, M. F., Lehtonen, M., Kassem, A. M., 
et al. (2023). Multi‐objective optimal planning of EV charging stations and renewable 
energy resources for smart microgrids. Energy Sci. & Eng. 11 (3), 1202–1218. 
doi:10.1002/ese3.1385
Astero, P. (2023). Recent advances toward carbon-neutral power system. Electricity 4 
(3), 253–255. doi:10.3390/electricity4030015
Boardman, E. N., Boisramé, G. F., Wigmosta, M. S., Shriver, R. K., and Harpold, 
A. A. (2025). Improving model calibrations in a changing world: controlling for 
nonstationarity after mega disturbance reduces hydrological uncertainty. Hydrology 
Earth Syst. Sci. 29 (22), 6333–6352. doi:10.5194/hess-29-6333-2025
Bogodorova, T., Osipov, D., and Vanfretti, L. (2024). Fast small signal stability 
assessment using deep convolutional neural networks. Electr. Power Syst. Res. 235, 
110853. doi:10.1016/j.epsr.2024.110853
Chen, G., Zhang, T., Qu, W., and Wang, W. (2023). Photovoltaic power prediction based 
on VMD-BRNN-TSP. Mathematics 11 (4), 1033. doi:10.3390/math11041033
Gu, T., Lv, Q., Fan, Q., Li, B., Lin, C., Zhang, H., et al. (2024). Two-stage distributionally 
robust assessment method for distributed PV hosting capacity of flexible distribution 
networks. Energy Rep. 11, 2266–2278. doi:10.1016/j.egyr.2024.01.079
Hamedi, M., Shayeghi, H., Seyedshenava, S., Safari, A., Younesi, A., Bizon, N., 
et al. (2023). Developing an integration of smart-inverter-based hosting-capacity 
enhancement in dynamic expansion planning of PV-penetrated LV distribution 
networks. Sustainability 15 (14), 11183. doi:10.3390/su151411183
Han, L. (2025). Key technologies and review of hosting capacity assessment for 
distributed photovoltaic integration into distribution network. Appl. Comput. Eng. 148, 
75–82. doi:10.54254/2755-2721/2025.23378
Hewamalage, H., Ackermann, K., and Bergmeir, C. (2023). Forecast evaluation for data 
scientists: common pitfalls and best practices. Data Min. Knowl. Discov. 37 (2), 788–832. 
doi:10.1007/s10618-022-00894-5
Hu, R., Wang, W., Chen, Z., Wu, X., Jing, L., Ma, W., et al. (2020). Coordinated voltage 
regulation methods in active distribution networks with soft open points. Sustainability
12 (22), 9453. doi:10.3390/su12229453
Li, Y., Zhang, M., and Chen, C. (2022). A deep-learning intelligent system incorporating 
data augmentation for short-term voltage stability assessment of power systems. Appl. 
Energy 308, 118347, doi:10.1016/j.apenergy.2021.118347
Li, G., Ma, H., Zhang, L., Wang, H., and He, H. (2023). “Probabilistic assessment 
of photovoltaic hosting capacity in distribution network via sparse polynomial chaos 
expansion,” in 2023 3rd power system and green energy conference (PSGEC). Shanghai, 
China, 191–196.
Liu, Q., Guo, Y., and Xu, T. (2025). Robust deep reinforcement learning for inverter-
based volt-var control in partially observable distribution networks. Appl. Energy 399: 
126445, doi:10.1016/j.apenergy.2025.126445
Meng, L., Yang, X., Zhu, J., Wang, X., and Meng, X. (2024). Network partition 
and distributed voltage coordination control strategy of active distribution 
network system considering photovoltaic uncertainty. Appl. Energy 362, 122846. 
doi:10.1016/j.apenergy.2024.122846
Rahman, S., Saha, S., Islam, S. N., Arif, M. T., Mosadeghy, M., Haque, M. E., et al. (2021). 
Analysis of power grid voltage stability with high penetration of solar PV systems. IEEE 
Trans. Industry Appl. 57 (3), 2245–2257. doi:10.1109/tia.2021.3066326
Shen, C., Liu, H., Wang, J., Yang, Z., and Hai, C. (2025). Kullback–leibler 
divergence-based distributionally robust chance-constrained programming for PV 
hosting capacity assessment in distribution networks. Sustainability 17 (5), 2022. 
doi:10.3390/su17052022
Sun, X., and Qiu, J. (2021). Two-stage volt/var control in active distribution networks 
with multi-agent deep reinforcement learning method. IEEE Trans. Smart Grid 12 (4), 
2903–2912. doi:10.1109/tsg.2021.3052998
Tang, Y., Sun, S., Zhao, B., Ni, C., Che, L., and Li, J. (2024). Distributed photovoltaic 
generation aggregation approach considering distribution network topology. Energies
17 (12), 2990. doi:10.3390/en17122990
Trinh, P. H., and Chung, I. Y. (2024). Integrated active and reactive 
power control methods for distributed energy resources in distribution 
systems for enhancing hosting capacity. Energies 17 (7), 1642. doi:10.3390/
en17071642
Wang, J., Ye, N., and Ge, L. (2020). Steady-state power quality synthetic evaluation based 
on the triangular fuzzy BW method and interval VIKOR method. Appl. Sci. 10 (8), 2839. 
doi:10.3390/app10082839
Werkie, Y. G., Nyakoe, G. N., and Wekesa, C. W. (2025). Power system voltage stability 
assessment and control strategies: state-of-the-art review. J. Electr. Comput. Eng. 2025 
(1), 6667482. doi:10.1155/jece/6667482
Yang, Y., Lin, S., Wang, Q., Xie, Y., Liu, M., and Li, Q. (2022). Optimization 
of static voltage stability margin considering uncertainties of wind power 
generation. IEEE Trans. Power Syst. 37 (6), 4525–4540. doi:10.1109/tpwrs.2022.
3152215
Yu, P., Wan, C., Qin, H., Lao, K. W., Song, Y., and Ju, P. (2024). Centralized-
distributed coordinated voltage control of active distribution networks with 
renewables. IEEE Trans. Sustain. Energy 16 (3), 1504–1517. doi:10.1109/tste.2024.
3484763
Zhang, T., Zhou, X., Gao, Y., and Zhu, R. (2023). Optimal dispatch of the source-
grid-load-storage under a high penetration of photovoltaic access to the distribution 
network. Processes 11 (10), 2824. doi:10.3390/pr11102824
Frontiers in Energy Research
13
frontiersin.org
