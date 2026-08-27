<!--
source: D1_容载比理论/EN_PMC_substation_capacity_TOU_2022.pdf
sha256: 90276d7fe961b88e5c527a35373e1f8e5d24323be22dbeed7c21aa3d6fcf1e72
method: pymupdf
pages: 13
-->

<!-- page 1/13 -->

Citation: Xu, D.; Fu, Q.; Ye, L.; Lin,
W.; Qian, Y.; Zhang, K.; Yao, J. The
Optimal Sizing of Substation
Capacity in a Distribution Network,
Considering a Dynamic Time-of-Use
Pricing Mechanism. Sensors 2022, 22,
7173. https://doi.org/10.3390/
cs22197173
Academic Editor: Hossam A. Gabbar
Received: 4 September 2022
Accepted: 20 September 2022
Published: 21 September 2022
Publisher’s Note: MDPI stays neutral
with regard to jurisdictional claims in
published maps and institutional afﬁl-
iations.
Copyright:
© 2022 by the authors.
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
sensors
Article
The Optimal Sizing of Substation Capacity in a Distribution
Network, Considering a Dynamic Time-of-Use
Pricing Mechanism
Dajun Xu 1, Qiang Fu 1, Lun Ye 2,*, Wenyu Lin 1, Yuzhou Qian 1, Kebo Zhang 1 and Jiangang Yao 2
1
State Grid Ningbo Yinzhou Power Supply Company, Ningbo 315000, China
2
College of Electrical and Information Engineering, Hunan University, Changsha 410082, China
*
Correspondence: yeahlun@hnu.edu.cn
Abstract: Application of sensors in the smart grid has promoted the development of demand side
management (DSM). However, the incentives of DSM such as peak–valley time-of-use (TOU) price
will change the load pattern in the future; the substation capacity sizing will be further inﬂuenced
accordingly. This paper proposes a substation capacity sizing method in distribution network
considering DSM and establishes a peak-valley TOU pricing method based on the cost–beneﬁt
analysis of each participant in the TOU price. Compared with the conventional ﬁxed peak–valley
ratio, a dynamic division method is proposed to calculate the optimal pull-off ratio for the TOU
pricing. By considering the proposed TOU pricing method, a substation capacity sizing model for the
distribution network is further proposed. Finally, the economic beneﬁts of the two substation capacity
sizing schemes are compared and evaluated according to the selected economic indicators. The
results of the case study demonstrate that under the premise of reasonable pricing, considering the
impact of TOU on substation capacity sizing, the construction investment and the user cost of power
supply companies can be saved while meeting the power demand. The economy and rationality of
the planning scheme have been signiﬁcantly improved.
Keywords: time-of-use price; distribution network planning; substation capacity sizing; demand
side management; cost-beneﬁt analysis; peak load shifting
1. Introduction
With the development of the internet of things and sensors, demand side management
(DSM) has been widely implemented in the smart grid. The elasticity of market demand
has improved. Power supply companies have more choices in power supply and electricity
price strategies for the future, which makes the operation mode of the distribution network
more diversiﬁed [1–3]. A traditional distribution network planning scheme is formulated
according to the rigid demand of user load and socioeconomic development [4], in which
it is difﬁcult to consider the inﬂuence of DSM implementation in the power system and
formulate reasonable planning schemes. Therefore, it is necessary to take into account the
effect of DSM in distribution network planning to fully improve its feasibility, rationality,
and economy [5].
As the most commonly used economic measure of DSM, the peak–valley time-of-use
(TOU) price is the main way to reduce the maximum load [6]. The peak–valley TOU price is
an important stimulus provided by power supply companies to demand side users through
price leverage to implement integrated resource management in the smart grid [7,8]. It
divides an operation cycle (day, month, quarter, year, etc.) into three periods: peak, normal,
and valley. Based on the price at normal period, the peak–valley TOU price raises the price
at peak period and reduces the price at valley period. It can cut the peak and ﬁll the valley,
alleviate the peak period of the power supply pressure, and improve the system load rate;
the electricity cost of users will also be reduced. Moreover, research in [9,10] shows that the
Sensors 2022, 22, 7173. https://doi.org/10.3390/s22197173
https://www.mdpi.com/journal/sensors



<!-- page 2/13 -->

Sensors 2022, 22, 7173
2 of 13
implementation of the peak–valley TOU price can also effectively reduce the transmission
loss of electric energy in the distribution network. In this way, the peak–valley TOU price
can change the spatial and temporal distribution of the overall regional load by adjusting
the load characteristics of users, which can further reduce the electricity quantity that the
power supply company needs to supply due to the load growth and, ultimately, affect the
overall distribution network planning scheme.
Research and practical experience have demonstrated that the peak–valley TOU price
is not only an effective method of DSM but also an important measure for further promoting
the sustainable and harmonious development of society, the economy, energy, and the
environment [11–13]. At present, research on the peak–valley TOU price focuses on three
aspects: pricing method, users’ response to the peak–valley TOU price, and the cost-
effectiveness of DSM participants. Reference [14] studied the division of peak, normal,
and valley periods and their pricing methods and established the pricing model of the
electricity price in corresponding periods. References [15,16] optimized the pricing method
of the peak–valley TOU price by combining the price of the demand side and supply side.
References [17–19] obtained the demand response model and its corresponding algorithm
by studying the response behavior of the demand side after implementation of the TOU
price. In order to make the three DSM participants—i.e., power supply companies, users,
and the whole society—beneﬁt from the implementation of the TOU price, reference [20]
systematically analyzed the cost–beneﬁt of the three participants and established a practical
analysis model.
On the basis of the above, the load demand will change with the implementation of
the peak–valley TOU price, which will affect the distribution network planning. Substation
capacity sizing is one of the important parts of distribution network planning, which can
affect the construction investment, the grid structure, the physical-information coordination
based on situation awareness, and the power supply reliability. However, numerous
studies of distribution network planning considering the TOU are based on the ﬁxed TOU
price, regardless of the pricing and the division of the peak and valley. With the gradual
promotion of the peak–valley TOU price, it is necessary to study its dynamic impact on
future Smart Grid planning to develop a more reasonable and economic planning scheme.
The peak–valley TOU price mainly affects substation capacity sizing by adjusting the
maximum load, which cannot change the trend of load development. It can only affect the
implementation process of power system construction. Therefore, in this paper, a substation
capacity sizing method considering the dynamic peak–valley TOU price is proposed and
applied to substation capacity sizing to modify and verify its beneﬁt. In the proposed
method, the initial substation capacity sizing scheme is formulated without considering
the inﬂuence of the peak–valley TOU price. On the basis of the initial sizing scheme,
the inﬂuence of the dynamic peak–valley TOU price is determined on the basis of data
perception of the distribution network to modify the scheme, and cost–beneﬁt analysis is
conducted to obtain the ﬁnal sizing scheme. The results of the case study demonstrate that
considering the inﬂuence of the dynamic peak–valley TOU price in substation capacity
sizing under the premise of a reasonable price setting can save the cost for both power
supply companies and users.
2. Modeling of the Peak–Valley TOU Price
2.1. Dynamic Division of the Peak Valley Period
The reasonable peak–valley time division is the premise for obtaining the correspond-
ing reasonable peak–valley TOU price and achieving the good effect of peak load shifting.
In this paper, the time division method in [21] is used to determine the possibility of peak
and valley periods at each time point on the daily load curve.
Divide the peak and valley periods for 1 day of 24 h; set hi as the i-th division method
in total n divisions. The division set of the peak and valley periods can be represented as
H = {hi, i = 1, 2, 3,..., n}. In each division method hi, use the electricity price models of peak,
valley, and normal periods to optimize and compare the results of each division in H to



<!-- page 3/13 -->

Sensors 2022, 22, 7173
3 of 13
select the best method for peak load shifting. The optimization models of the electricity
price will be discussed in the next section.
2.2. Modeling the TOU Price
Suppose Ts, Tl, and Tv are the peak, level, and valley periods division in a day, re-
spectively, and that this satisﬁes Ts + Tl + Tv = 24 h. Ps, Pl, and Pv is the corresponding
electricity price of the three periods, respectively. Ws, Wl, and Wv represent the correspond-
ing electricity consumption of the three periods, respectively. P0 and W0 represent the
electricity price and electricity consumption in the whole day before the implementation
of the peak–valley TOU price, respectively. According to the overall goal of DSM imple-
mentation, the mathematical model of the peak–valley TOU price is established from the
following aspects:
1.
Proﬁt of power supply company
Before and after the implementation of the peak–valley TOU price, the electricity sales
revenue of the power supply company are G0 = P0W0 and G1 = PsWs + PlWl + PvWv, re-
spectively. The average daily reduction in the distribution network construction investment
due to the reduction in maximum load after the implementation of the peak–valley TOU
electricity price is Gt. To meet the principle of proﬁt for the power supply company, the
following relationship should be satisﬁed:
G1 + Gt ≥G0
(1)
2.
Beneﬁt of the user side
Suppose P1 is the average price after the implementation of the peak–valley time-of-use
price, according to the principle of user side beneﬁt:
P1 ≤P0
(2)
P1= PsWs + PlWl + PvWv
Ws + Wl + Wv
(3)
3.
Cost constraint
The electricity price in the valley period should be greater than its marginal cost:
Ce ≤Pv ≤Ps
(4)
4.
Prevention of peak–valley inversion
The peak–valley TOU price has limited regulation ability to load and must be regulated
within a certain proportion to prevent the phenomenon of peak–valley inversion with
excessive regulation, which is not conducive to the safe and stable operation of the power
system. Thus, the regulating capability of the peak–valley TOU price should satisfy:
−Fmax ≤Lhi(Ps, Pl, Pv, t) −L0(t)
L0(t)
≤Fmax
(5)
where Fmax is the maximum adjustable proportion of load, determined by the power supervi-
sion department according to the actual situation of the region. L0(t) and Lhi(Ps, Pl, Pv, t) are
the load values before and after the implementation of the peak–valley TOU price, respectively.
The main purpose of implementing DSM is to cut the peak and ﬁll the valley, so that
the peak–valley difference in the daily load curve is smaller. On the basis of the change and
distribution of the electricity price before and after the implementation of the peak–valley



<!-- page 4/13 -->

Sensors 2022, 22, 7173
4 of 13
TOU price, the optimal peak–valley TOU price model based on the division method hi is
proposed as follows:
obj.
min

max
0≤t≤24Lhi(Ps, Pl, Pv, t)

min

max
0≤t≤24Lhi(Ps, Pl, Pv, t) −min
0≤t≤24Lhi(Ps, Pl, Pv, t)

s.t.
G1 + Gt ≥G0
P1 ≤P0
−Fmax ≤Lhi(Ps, Pl, Pv, t) −L0(t)
L0(t)
≤Fmax
where max
0≤t≤24Lhi(Ps, Pl, Pv, t) and
min
0≤t≤24Lhi(Ps, Pl, Pv, t) are the maximum and minimum
load of the daily load curve Lhi under the peak–valley division method hi, respectively.
max
0≤t≤24Lhi(Ps, Pl, Pv, t) −min
0≤t≤24Lhi(Ps, Pl, Pv, t) is the peak–valley difference in the daily load
curve Lhi.
3. Cost–Beneﬁt Analysis and Electricity Pricing
3.1. Cost–Beneﬁt Analysis
The power supply company, the user, and government constitute the three main
participants in the implementation of the peak–valley TOU price [22]. The power supply
company is the main body that implements the electricity price strategy. The user is the
implementation object of the electricity price strategy, who gives feedback to the power
supply company through DSM. The government is responsible for leading and supervising
the implementation process of the electricity pricing strategy, which reﬂects the beneﬁts
of the whole society [23]. Therefore, to analyze the cost–beneﬁt of peak–valley TOU price
implementation, it is necessary to take into account its different impacts on the power
supply company, on the user, and on government (i.e., the whole society). The interests
of the user side need to be secured to facilitate their voluntary participation in DSM [24].
Moreover, in order to obtain government approval, it is also necessary to ensure that the
implementation of the electricity price strategy can beneﬁt the whole society.
Combined with the dynamic peak–valley TOU price model established above, this
section analyzes the cost, income, and proﬁt variation in the power supply company, the
user, and the whole society for a typical load day in distribution network planning. Set
∆Cp, ∆Bp, and ∆Ep as the changes of cost, proﬁt, and the proﬁt of the power supply
company before and after the implementation of the peak–valley TOU price, respectively.
∆Cu, ∆Bu, and ∆Eu are the changes of cost, proﬁt, and proﬁt of user before and after
the implementation of the peak–valley TOU price, respectively. ∆Cs, ∆Bs, and ∆Es are
the changes of cost, proﬁt, and proﬁt of user before and after the implementation of the
peak–valley TOU price, respectively. The cost–beneﬁt analysis is as follows.
3.1.1. Cost–Beneﬁt Changes in the Power Supply Company
Considering the inﬂuence of the peak–valley time-of-use price in distribution network
planning, the cost change in the power supply company consists of reduced construction
investment. Its value can be determined according to the average cost of reduced or post-
poned construction substation equipment, transmission, and distribution network frame
and its supporting facilities. The loss of electricity sales proﬁt caused by the implementation
of the peak–valley TOU electricity price constitutes the change in revenue in the power
supply company. Therefore, the cost–beneﬁt changes model is:
∆Cp = −Gt
(6)
∆Bp = (P1 −P0)W0
(7)



<!-- page 5/13 -->

Sensors 2022, 22, 7173
5 of 13
where Gt = ct∆Sm/365ny, ct is the substation capacity cost (106 RMB/MW). ∆Sm is the
difference in new substation capacity between the traditional distribution network planning
and the planning considering DSM measures. ny is the number of years in the planning
cycle. W0 represents the electricity consumption of the whole day before the peak–valley
TOU price is implemented. The user adjusts the electricity consumption period after the
peak–valley TOU price is implemented, but the normal production activities demand of the
user should still be guaranteed, so that the user’s electricity consumption can be assumed
to be unchanged.
3.1.2. Cost–Beneﬁt Changes in the User
The change in the user’s electricity cost is the change in electricity payment caused by
the change in the average electricity price after the implementation of the peak–valley TOU
price (ignoring the change in cost caused by the adjustment of the production process) [25].
The implementation of the peak–valley TOU price in distribution network planning has
little effect on user income, so the change in user income is ignored. The cost–beneﬁt change
model is:
∆Cu = (P1 −P0)W0
(8)
∆Bu = 0
(9)
3.1.3. Cost–Beneﬁt Changes in the Whole Society
Reduced investment by the power supply company after taking into account the
impact of the peak–valley TOU price in distribution network planning constitutes the
cost change in the whole society. The implementation of the peak–valley TOU price in
distribution network planning has little effect on the beneﬁts of the whole society, so the
change associated with this is ignored. The corresponding cost–beneﬁt changes model is:
∆Cs = −Gt
(10)
∆Bs = 0
(11)
3.1.4. Beneﬁt Analysis of the Three Participants
From Equations (6) to (11), it can be obtained that the proﬁt changes in the three par-
ticipants after considering the implementation of the peak–valley TOU price in distribution
network planning is:



∆Ep = ∆Bp −∆Cp
∆Eu = ∆Bu −∆Cu
∆Es = ∆Bs −∆Cs
(12)
3.2. Peak–Valley TOU Pricing
Figure 1 shows the calculation results of changes in user electricity cost and power sup-
ply company electricity sales proﬁt after DSM implementation in the form of a rectangular
coordinate diagram. It can be seen from the ﬁgure that when the calculation results are in
quadrant II, the corresponding DSM measures are beneﬁcial to both the user and the power
supply company. When the calculation results are in quadrant IV, it is unfavorable to both
the user and the power supply company. When the calculation results are in quadrants
I or III, the corresponding DSM measures are only beneﬁcial to either the power supply
company or the user.



<!-- page 6/13 -->

Sensors 2022, 22, 7173
6 of 13
0
+
+
-
u
C
Δ
pE

Powe r supply 
company
User
Profit
Loss
Powe r supply 
company
Powe r supply 
company
Powe r supply 
company
User
User
User
−
Figure 1. Changes in user electricity cost and power supply company electricity sales proﬁt after
DSM implementation.
The implementation of the peak–valley TOU price based on DSM should not only
ensure that the power supply company obtains more proﬁts, but also ensure that the user’s
electricity expenditure is reduced. In other words, to improve the enthusiasm of users to
participate in DSM, the calculation results of changes in user electricity cost and power
supply company electricity sales proﬁt after DSM implementation should be in quadrant II
of Figure 1. Therefore, it is necessary to set a reasonable peak–valley TOU price to ensure
the proﬁt of both the power supply company and the user. The setting of the peak–valley
TOU price is analyzed as follows.
3.2.1. Pricing in a Normal Period
Because the price in a normal period represents the overall electricity consumption
level in a region, this should not be affected by the implementation of the peak–valley TOU
price. Therefore, it can be assumed that the price in a normal period is equal to the average
price before the implementation of the peak–valley TOU price.
Pl = P0
(13)
3.2.2. Pricing in Peak and Valley Periods
Set the ﬂuctuation range of peak and valley electricity price relative to the normal
period as δs and δv, respectively. The corresponding electricity price is
Ps = P0(1 + δs)
(14)
Pv = P0(1 −δv)
(15)
Deﬁne pull-off ratio β as the ratio of peak and valley electricity price to the ﬂuctuation
of price in the normal period; that is,
β = δs
δv
(16)
Then, the following relationship for the electricity price of the user can be depicted:
P1 = P0

1 + δsWs −δvWv
Ws + Wl + Wv

(17)
P1
P0
= 1 + δsWs −δvWv
Ws + Wl + Wv
(18)



<!-- page 7/13 -->

Sensors 2022, 22, 7173
7 of 13
It can be seen from Equation (18) that to reduce the average price of the user, the value
of the pull-off ratio needs to satisfy β < Wv/Ws.
The investment cost of distribution network construction in the power supply com-
pany has the following relationship: Gt ∝∆Smax, ∆Smax = ∆Lmax/α cos θ, and Gt ∝∆Lmax,
that is
Gt = a∆Lmax
(19)
where ∆Smax represents the new substation capacity that can be reduced after the imple-
mentation of the peak–valley TOU price. ∆Lmax represents the maximum load change
before and after the implementation of the peak–valley TOU price. α is the load rate, cos θ
is the power factor.
The research on load transfer rate curve in the user response model established in
reference [26] shows that
∆Lmax = λsvLmax + λslLmax
(20)
where λsv and λsl is the load transfer rate of the peak–valley period and peak–normal
period, respectively. They have the following relationship with peak, normal, and valley
electricity prices:
λsv = ksv(Ps −Pv) + bsv = ksvP0(δs + δv) + bsv
(21)
λsl = ksl(Ps −Pl) + bsl = kslP0δs + bsl
(22)
where ksv and bsv are the slope and longitudinal intercept of load transfer rate curve in the
peak–valley period, respectively. ksl and bsl are the slope and longitudinal intercept of the
load transfer rate curve in the peak–normal period, respectively.
According to Equations (19) to (22), the following relationship can be acquired
Gt = ksδs + kvδv + m
(23)
where ks = aLmaxP0(ksv + ksl), kv = aLmaxP0ksv, m = aLmax(bsv + bsl).
According to Equations (6) to (8), (12), (17), and (23), it can be ascertained that
∆Bp = (P1 −P0)W0 = P0(δsWs −δvWv)
(24)
∆Ep = P0(δsWs −δvWv) + ksδs + kvδv + m
(25)
where P0, ks, kv, and m are ﬁxed values; and ∆Ep and ∆Cu are binary functions of δs and δv;
that is,
 ∆Ep = fp(δs, δv)
∆Cu = fu(δs, δv)
(26)
If the peak to valley electricity price ratio of the peak–valley TOU price in a region
changes little, it can be considered as a ﬁxed value:
K = Ps
Pv
= 1 + δs
1 −δv
(27)
According to Equations (16) and (27), it can be conducted that
(
δs = β(K−1)
K+β
δv = K−1
K+β
(28)
According to (28), ∆Ep and ∆Cu can be simpliﬁed as univariate functions of β:
 ∆Ep = fp(β)
∆Cu = fu(β)
(29)



<!-- page 8/13 -->

Sensors 2022, 22, 7173
8 of 13
Based on the above, through Equation (29), the research on the dynamic peak–valley
TOU price can be transformed into the analysis of the impact of the pull-off ratio on the
cost–beneﬁt of the power supply company, the user, and the whole society.
4. Case Study
In this case study, the annual maximum load day of the 110 kV distribution network
in a municipal level area is selected as the typical load day to verify the effectiveness
of the proposed method. The relevant data are collected from an actually implemented
project. Before the implementation of the peak–valley TOU price, the maximum hourly
load of a typical day is 7795 MW and the minimum hourly load is 4915 MW. The electricity
consumption for the peak, valley, and normal periods is 44,852 MWh, 50,431 MWh, and
54,956 MWh, respectively. The load data are shown in Table 1.
Table 1. Load data of a typical Day.
t
Load/(MW)
t
Load/(MW)
t
Load/(MW)
1:00
5120
9:00
7185
17:00
7300
2:00
5345
10:00
7350
18:00
7360
3:00
5210
11:00
7535
19:00
7795
4:00
4915
12:00
6710
20:00
7760
5:00
5445
13:00
6835
21:00
7300
6:00
5670
14:00
6935
22:00
6820
7:00
5970
15:00
6890
23:00
5825
8:00
6445
16:00
6870
24:00
5545
According to the time division method in Section 2.1, the results of the time period
division are as follows: peak period: 9:00–11:00, 17:00–21:00; valley period: 23:00–7:00;
normal period: the time period other than the peak and valley periods.
4.1. Power Demand Forecasting
According to the regional overall development planning and electricity load reporting
in the past three years, the spatial load forecasting method can be used to predict the load
in the next three years. The long-term newly increased load is forecasted using the load
density forecasting method [27]. The forecasting results in the next three years are shown
in Table 2.
Table 2. Long-term new load forecast.
Land Usage Type
Area/(km2)
Plot Ratio
Load Index/(W·m−2)
Demand Factor
Load/(MW)
Residence
53.37
1
50
0.6
1601.10
Culture, education, and health
2.32
0.8
60
1
110.20
Municipal Administration
2.22
0.8
50
1
88.38
Industrial
42.83
1
50
1
2140.96
Ofﬁce
1.72
1
80
1
136.85
Total (simultaneity rate 0.7)
102.46
/
/
/
2854.24
4.2. Setting of the Peak–Valley TOU Price
In the studied region, the average price is 0.59 RMB/kWh before the implementation of
the peak–valley TOU price, and the peak–valley price ratio K = 3.8. The pull-off ratio β takes
0 as the starting value and takes 7 typical values with an equal interval of 0.25. According
to the method in Section 3, the peak–valley TOU price can be calculated under each pull-off
ratio. Based on the dynamic peak–valley TOU price model, the load characteristics after
implementing the peak–valley TOU price can be simulated to obtain the daily maximum
load, the minimum load, and the maximum load transfer rate under different pull-off
ratios (the proportion of the transfer of the user’s maximum load to the normal and valley



<!-- page 9/13 -->

Sensors 2022, 22, 7173
9 of 13
periods to its original value). The coordinates of changes in the user electricity cost and the
power supply company electricity sales proﬁt in Figure 1 can also be calculated, as shown
in Table 3.
Table 3. Performance of different pull-off ratios.
β
Ps/(RMB/MWh)
Pv/(RMB/MWh)
Lmax/(MW)
Lmin/(MW)
λm
(∆Cu, ∆Ep)
0
590.000
155.263
7280
5179
0.066
(−1743.164, −1491.109)
0.25
691.975
182.099
7124
5267
0.086
(−1226.865, −871.614)
0.5
782.093
205.814
6991
5451
0.103
(−829.035, −384.286)
0.75
862.308
226.923
6847
5631
0.122
(−494.547, 49.745)
1
934.167
245.833
6861
5851
0.120
(−153.341, 71.985)
1.25
998.911
262.871
7062
5869
0.094
(33.441, 422.482)
1.5
1057.547
278.302
7293
5485
0.064
(219.358, 489.678)
With the change in the pull-off ratio, the proﬁt change curve between the power
supply company and the user can be calculated by Equations (6) to (9), and (14), as shown
in Figure 2.
2000
1500
1000
500
0
−500
−1000
−1500
−2000
Figure 2. Proﬁt change curve in company and user.
According to Table 3 and Figure 2, when the value of β is 0, 0.25, or 0.5, the user gains
but the power supply company loses. When the value of β is 1.25 or 1.5, the power supply
company gains but the user loses. When the value of β is 0.75 or 1, both the power supply
company and the user can beneﬁt. In conclusion, under a constant peak–valley electricity
price ratio, if the value of the pull-off ratio is reasonable (The value of β is in the shaded
area in Figure 2), the implementation of the peak–valley TOU price will make the proﬁt
change curve between the power supply company and the user in quadrant II of Figure 1,
so that the power supply company and the user can both proﬁt.
According to the survey of user feedback and relevant historical data after several
adjustments in the peak–valley TOU price ratio, combined with the peak–valley TOU
price model established in this paper, MatlabR2014a is used as the simulation platform
for regression ﬁtting the user feedback after the peak–valley TOU price is adopted. The
load curves after the implementation of the peak–valley TOU price are obtained. When
the pull-off ratio is 0.75 or 1, the load curves after the implementation of the peak–valley
TOU price are shown in Figure 3. According to the ﬁgure, after the implementation of the
dynamic peak–valley TOU price, the maximum load is signiﬁcantly reduced, the load rate
is increased, and the smoothness of the load curve is improved. When β = 0.75, after imple-
mentation of the peak–valley TOU price, the maximum load Lmax = 6847 MW, the minimum
load Lmin = 5631 MW, and the peak valley difference ∆Lsv = 1216 MW. When β = 1, after the
implementation of the peak–valley TOU price, the maximum load Lmax = 6861 MW, the
minimum load Lmin = 5851 MW, and the peak valley difference ∆Lsv = 1010 MW. Through



<!-- page 10/13 -->

Sensors 2022, 22, 7173
10 of 13
comparison, it can be seen that the maximum load difference is small when the pull-off
ratio is 0.75 and 1, but the peak valley difference at β = 1 is 206 MW less than that at β = 0.75,
and the load curve is smoother. Therefore, the peak–valley TOU price with β = 1 has been
selected for this paper to study its impact on substation capacity sizing.
Figure 3. Load curve of a typical load day.
4.3. Cost–Beneﬁt Analysis
After the implementation of the dynamic peak–valley TOU price, the peak period
electricity consumption of the typical load day is Ws = R
Ts L(T)dt = 38,659 MWh. The
electricity consumption of the normal period is Wl = R
Tl L(T)dt = 67,441 MWh. The
electricity consumption of the valley period is Wv = R
Tv L(T)dt = 44,139 MWh. From
the Table 3, Ps = 0.934 RMB/kWh, Pv = 0.246 RMB/kWh, ∆Cu = −153.341 × 105 RMB,
∆Ep = 71.385 × 105 RMB. According to Equations (6) to (12), the cost, income, and proﬁt
changes of each participant in the typical load day after considering the implementation
of the dynamic peak–valley TOU price in the substation capacity sizing can be calculated.
The results are shown in Table 4.
Table 4. Cost, income, and proﬁt changes of each participant.
Paticipants
Cost Change/105 RMB (∆C)
Income Change/105 RMB (∆B)
Proﬁt Change/105 RMB (∆E)
Power supply company
−269.552
−197.567
71.985
User
−153.341
0
−153.341
Whole society
−269.552
0
269.552
According to Table 4, the reduction in the average electricity price after the imple-
mentation of the dynamic TOU results in an income reduction of 1.97567 million yuan,
while the temporal shift in the maximum load leads to a reduction in the substation sizing
capacity, thus saving 2.69552 million yuan in the investment cost. In the end, the power
supply company can still make a proﬁt of 719,850 yuan. Moreover, the reduction in the
average electricity price also saves the users 1,533,410 yuan.
4.4. Substation Sizing
According to Reference [28], the maximum load transfer rate is only affected by the
price difference between the peak and valley periods. Table 3 shows that the maximum
load transfer rate in the ﬁrst year of the past three years is λm = 0.12; the load forecasting
results of each year can be modiﬁed after considering the effect of the dynamic peak–valley
TOU price on the basis of this.



<!-- page 11/13 -->

Sensors 2022, 22, 7173
11 of 13
On the basis of the assumption that the same peak–valley TOU price strategy will be
implemented in the planning period, the electricity price will remain unchanged. The power
demand forecast with β = 1 in the next three years and its correction results considering
the impact of DSM implementation are shown in Table 5. Taking into account the current
situation of the regional power grid and the annual load growth, the sizing of 110 kV
substations in the regional power grid in the next three years is preliminarily determined
(assuming that the load rate of the main transformer is 60% and the power factor is 0.9),
and the sizing results are modiﬁed after considering the implementation of the dynamic
peak–valley TOU price, as shown in Table 6.
Table 5. Power demand forecasting and its corresponding modiﬁed results considering DSM (MW).
Sizing Scheme
Maximum Load
Past Year 3
Future Year 1
Future Year 2
Future Year 3
Traditional sizing
7795
8575
9605
10,645
Modiﬁed sizing considering DSM
6861
7546
8453
9368
Table 6. 110 kV substation planning and its corresponding modiﬁed results considering DSM (MW).
Sizing Scheme
Item
Future Year 1
Future Year 2
Future Year 3
Traditional sizing
New transformer/set
23
31
31
Capacity/MVA
1449
1901
1940
Modiﬁed sizing considering DSM
New transformer/set
21
27
27
Capacity/MVA
1297
1701
1675
It can be seen from Table 6 that when taking into account the impact of the dynamic
peak–valley TOU price, the new substation capacity required in each year can be effectively
reduced. In this way, while meeting the electricity demand, the number of power grid
construction projects in the planning cycle is reduced, the planning investment is saved,
and the workload of the planners is also reduced. The additional substation capacity in the
planning period reduces from 5290 MVA to 4673 MVA.
4.5. Investment Cost of Substation
In Table 6, the investment cost of the substation capacity sizing in each year can be
estimated according to Gp = ct∆Sm (the unit substation capacity construction cost, take
106 yuan/MVA). The results are shown in Table 7.
Table 7. Comparison of the investment cost.
Planning Scheme (Million Yuan)
Future Year 1
Future Year 2
Future Year 3
Traditional planning
1449
1901
1940
Modiﬁed planning considering DSM
1297
1701
1675
As can be seen from Table 7, compared with the traditional planning method, the
proposed method has reduced the investment cost in each planning year. The reduction of
100 million yuan to 4.673 billion yuan of the new scheme, saving 11.67% of the investment
cost, proves that considering the inﬂuence of the dynamic TOU with a reasonable price
of electricity in the substation sizing can effectively reduce the investment in power grid
expansion and improve the economy of substation capacity sizing.
4.6. Veriﬁcation of the Modiﬁed Planning Scheme
Check the power balance of the two substation capacity sizing schemes, and the results
are shown in Table 8. According to Table 8, compared with the traditional sizing scheme,



<!-- page 12/13 -->

Sensors 2022, 22, 7173
12 of 13
the main transformer capacity in each year will be reduced after considering the impact of
the dynamic peak–valley TOU price on substation capacity sizing, but its corresponding
network supply load will also be reduced due to load transfer. The calculation results
show that the substation capacity load ratio in the substation capacity sizing scheme
considering the inﬂuence of the peak–valley TOU price is within a reasonable range, and
it is increased compared with the traditional sizing. The results show that the modiﬁed
sizing schemes considering DSM can enhance the adaptability of the power grid and the
ﬂexibility of dispatching.
Table 8. Load balance veriﬁcation.
Sizing Scheme
Item
Past Year 3
Future Year 1
Future Year 2
Future Year 3
Traditional sizing
Network supply load (MW)
7795
8575
9605
10,645
Capacity of the main
transformer(MVA)
14,410
15,895
17,760
19,700
Capacity load ratio
1.85
1.85
1.85
1.85
Modiﬁed sizing
considering DSM
Network supply load (MW)
6971
7668
8589
9493
Capacity of the main
transformer(MVA)
14,410
15,707
17,408
19,083
Capacity load ratio
2.07
2.05
2.03
2.01
5. Conclusions
This paper establishes a cost–beneﬁt analysis model of DSM participants for a future
smart grid with multiple information perception application after taking into account the
impact of the peak–valley TOU price in distribution network planning. Analysis in the case
study demonstrates that under a reasonable price setting (i.e., appropriate pull-off ratio)
in a different time period, the proﬁts of DSM participants will increase after considering
the implementation of the dynamic peak–valley TOU price in regional distribution net-
work planning. The proposed method also reﬂects the necessity of combining DSM with
distribution network planning.
Of course, there are some limitations in this study: the cost of implementing the
TOU price by power supply company and user is ignored, such as the cost of meter
transformation, publicity, and promotion, and overtime subsidies increased by the user due
to production plan adjustment. After the relevant data are collected in the future, a more
in-depth study of the inﬂuence of the ﬁxed price on the balanced relationship between the
power supply company and the user due to the implementation of the dynamic peak–valley
TOU price will need to be conducted.
In addition, after considering the inﬂuence of the peak–valley TOU price in distribution
network planning, the planned grid structure will inevitably change, which will further
affect the reliability of the power supply. The implementation of the peak–valley TOU price
will improve the reliability of the power supply. Therefore, the comprehensive impact of
these two aspects on the reliability of the power supply can be systematically studied in
the future.
Author Contributions: Conceptualization, D.X. and Q.F.; methodology, D.X.; software, Q.F. and L.Y.;
validation, L.Y. and W.L.; investigation, J.Y. and W.L.; resources, K.Z. and Y.Q.; data curation, J.Y.;
writing—original draft preparation, Q.F.; writing—review and editing, D.X. and Q.F. All authors
have read and agreed to the published version of the manuscript.
Funding: This research was supported by the Natural Science Foundation of Hunan Province of
China (Grant No. 2022JJ30214).
Institutional Review Board Statement: Not applicable.
Informed Consent Statement: Not applicable.
Data Availability Statement: Not applicable.



<!-- page 13/13 -->

Sensors 2022, 22, 7173
13 of 13
Conﬂicts of Interest: The authors declare no conﬂict of interest.
References
1.
Aras, S.; Mohammad, R.; Shahab, B.; Ranjbar, A.M. Integrated Demand Side Management Game in Smart Energy Hubs. IEEE
Trans. Smart Grid 2015, 6, 675–683.
2.
Xu, D.; Wu, Q.; Zhou, B.; Li, C.; Bai, L.; Huang, S. Distributed multi-energy operation of coupled electricity, heating and natural
gas networks. IEEE Trans. Sustain. Energy 2020, 11, 2457–2469. [CrossRef]
3.
Yang, H.; Li, C.; Shahidehpour, M.; Zhang, C.; Zhou, B.; Wu, Q.; Zhou, L. Multistage Expansion Planning of Integrated Biogas and
Electric Power Delivery System Considering the Regional Availability of Biomass. IEEE Trans. Sustain. Energy 2021, 12, 920–930.
[CrossRef]
4.
Zhu, J.; Zhou, X.; Zeng, P.; Zhang, H. Great Britain’s Transmission Grid Planning Method and Its Enlightenment to China’s Grid
Planning. J. Glob. Energy Interconnect. 2020, 3, 59–69.
5.
Zou, Y.; Wang, Q.; Chi, Y.; Wang, J.; Lei, C.; Zhou, N.; Xia, Q. Electric Load Proﬁle of 5G Base Station in Distribution Systems
Based on Data Flow Analysis. IEEE Trans. Smart Grid 2022, 13, 2452–2466. [CrossRef]
6.
Yang, H.; Wang, L.; Zhang, Y.; Tai, H.M.; Ma, Y.; Zhou, M. Reliability Evaluation of Power System Considering Time of Use
Electricity Pricing. IEEE Trans. Power Syst. 2019, 34, 1991–2002. [CrossRef]
7.
Zhou, B.; Yang, R.; Li, C.; Cao, Y.; Wang, Q.; Liu, J. Multiobjective Model of Time-of-Use and Stepwise Power Tariff for Residential
Consumers in Regulated Power Markets. IEEE Syst. J. 2018, 12, 2676–2687. [CrossRef]
8.
Wang, H.; Gao, Y. Real-time pricing method for smart grids based on complementarity problem. J. Mod. Power Syst. Clean Energy
2019, 7, 1280–1293. [CrossRef]
9.
Tan, Z.; Xie, P.; Wang, M.; Zhang, R. The optimal design of integrating interruptible price with peak-valley time-of-use power
price based on improving electricity efﬁciency. Trans. China Electrotech. Soc. 2009, 24, 161–168.
10.
Li, C.; Yang, H.; Shahidehpour, M.; Xu, Z.; Zhou, B.; Cao, Y.; Zeng, L. Optimal planning of islanded integrated energy system
with solar-biogas energy supply. IEEE Trans. Sustain. Energy 2020, 11, 2437–2448. [CrossRef]
11.
Shi, L.; Yang, F.; Liu, Y.; Wu, F. Multi-scenario user-side energy storage capacity optimization conﬁguration considering social
development. Power Syst. Prot. Control 2021, 49, 59–66.
12.
Ahsan, R.K.; Anzar, M.; Awais, S. Load forecasting, dynamic pricing and DSM in smart grid. Renew. Sustain. Energy Rev. 2016, 54,
1311–1322.
13.
Hai-Tra, N.; Usman, S.; Jorge, L.B.; ChangKyoo, Y. Optimal demand side management scheduling-based bidirectional regulation
of energy distribution network for multi-residential demand response with self-produced renewable energy. Appl. Energy 2022,
322, 119425.
14.
Ali, B.; Daryoush, H.; Octavian, B.; Mohammad, A.S.M. Optimal Real-Time Residential Thermal Energy Management for
Peak-Load Shifting With Experimental Veriﬁcation. IEEE Trans. Smart Grid 2019, 10, 5587–5599.
15.
Morteza, Z.O.; Sevda, Z.K.; Behnam, M.I.; Mehdi, A.; Hasan, M. Optimal Scheduling of Demand Response Aggregators in
Industrial Parks Based on Load Disaggregation Algorithm. IEEE Syst. J. 2022, 16, 945–953.
16.
Yu, R.; Yang, W.; Susanto, R. A Statistical Demand-Price Model with Its Application in Optimal Real-Time Price. IEEE Trans.
Smart Grid 2012, 3, 1734–1742. [CrossRef]
17.
Ceyhun, E.; Hakan, D.; Alejandro, R. Demand Response Management in Smart Grids with Heterogeneous Consumer Preferences.
IEEE Trans. Smart Grid 2015, 6, 3082–3094.
18.
Muhammad, B.R.; María, D.R.M. Minimizing pricing policies based on user load proﬁles and residential demand responses in
smart grids. Appl. Energy 2022, 310, 118492.
19.
Liu, J.; Han, X.; Han, W.; Zhang, L. Model and algorithm of customers’ responsive behavior under time-of-use price. Power Syst.
Technol. 2013, 10, 2973–2978.
20.
Chu, L.; Zhang, L.; Ni, Q.; Gao, C. New thoughts about network planning considering DSM based on current power system.
Power Demand Side Manag. 2010, 5, 9–13.
21.
Ding, N.; Wu, J.; Zou, Y. Research of peak and valley time period partition approach and TOU price on DSM. Autom. Electr. Power
Syst. 2001, 25, 9–12, 16.
22.
Fatma, Z.D.; Abdelmadjid, R. An Investigation into Pricing Policies in Smart Grids. Eng. Proc. 2022, 14, 15.
23.
Liu, H.; Chen, J. Power Demand Side Management; China Power Press: Beijing, China, 2015.
24.
Xu, D.; Zhou, B.; Wu, Q.; Chuang, C.Y.; Li, C.; Huang, S.; Chen, S. Integrated modelling and enhanced utilization of power-to-
ammonia for high renewable penetrated multi-energy systems. IEEE Trans. Power Syst. 2020, 35, 4769–4780. [CrossRef]
25.
Tu, J.; Zhou, M.; Song, X.; Luan, K. Research on Incentive Mechanism and Optimal Power Consumption Strategy for Residential
Users’ Participation in Peak Shaving of Power Grid. Power Syst. Technol. 2019, 43, 443–453.
26.
Su, M. Demand Response under Peak and Valley Time-of-Use Electricity Price. Value Eng. 2020, 39, 188–195.
27.
Li, T.; Wang, Y.; Zhang, N. Combining Probability Density Forecasts for Power Electrical Loads. IEEE Trans. Smart Grid 2020, 11,
1679–1690. [CrossRef]
28.
Wang, L.; Yang, H.; Ma, Y.; Zhang, D. Optimization Model of Multi-period Time of Use Strategy Considering Multiple Assessment
Indices. Electr. Power 2019, 52, 54–59.
