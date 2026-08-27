<!--
source: D1_容载比理论/CN_zgdl_flexible_interconnection_multiV_2025.pdf
sha256: 0b308be751502cb6113981a03eb160ab3e85f67b6ca5fcf83d51925fd072fe4f
method: pymupdf
pages: 7
-->

<!-- page 1/7 -->

 
考虑综合收益的多电压等级配电网柔性
互联装置协同规划方法
贺春光1，王林峰1，曹媛1，安佳坤1，雷子健2，宋关羽2，冀浩然2
(1. 国网河北省电力有限公司经济技术研究院，河北 石家庄　050000；2. 智能电网教育部重点实验室
（天津大学），天津　300072)
 
 
摘　要：提出了一种考虑综合收益的多电压等级配电网柔性互联装置协同规划方法，通过优化配置智能软
开关等柔性互联装置在多电压等级配电网中的安装位置和容量，改善运行时潮流分布并支撑故障时供电恢
复，提升系统的经济性、可靠性综合指标。基于河北某实际配电网数据开展算例研究，验证所提方法的有
效性，并分析该方法对高比例分布式电源接入下配电网经济性、安全性、可靠性的提升。
关键词：配电网；规划设计；柔性互联装置；智能软开关
DOI：10.11930/j.issn.1004-9649.202401080
 
 
 
0    引言
配电网作为分布式电源高效利用的关键平
台，是推动能源结构转型的重要支撑[1-5]。分布式
电源（distributed generators，DGs）的大规模接入
加剧了配电网运行状态的波动，为配电网的安全
运行带来了巨大挑战[6-10]。随着电力电子器件的
发展，以智能软开关（soft open point，SOP）为代
表的柔性互联装置，逐步接入配电网以替代传统
的联络开关，形成高度灵活可控的柔性配电网
（flexible distribution network，FDN），极大提高
了配电网运行的灵活性和可控性[4-7]。
SOP 技术理念自提出以来，已获得了国内外
学界、工业界的众多关注，并取得了一定的理论
和实践基础。从配电网正常运行时的优化控制来
看，SOP 主要起到优化潮流分布、降低电压越
限、减小系统损耗的作用[11-12]；从配电网故障场
景的供电恢复来看，SOP 还起到提供电压支撑、
减小停电范围、辅助供电恢复的作用[13-14]。针对
SOP 进行位置容量配置的相关研究已有一定成
果。文献[15] 建立计及配电网网络重构的SOP 三
层规划模型，并采用基于二阶锥优化的混合方法
求解。文献[16] 提出了兼顾经济性、可靠性的
SOP 选址优化，实现了配电网电压偏差和经济性
的改善，但是没有计及故障停电损失和SOP 在系
统故障时发挥的作用。文献[17] 提出了考虑SOP
对配电网经济性、可靠性影响的双层选址定容规
划模型。目前，同时考虑SOP 经济性、可靠性综
合收益的规划方法较少。为了SOP 的进一步推广
和应用，充分考虑各方面综合因素并将其作为规
划考量指标是非常有必要的。
此外，目前的配电网柔性互联方案大多集中
在同一电压等级下、同一馈线下，而多电压等级
配电网涉及的馈线、节点更多，柔性互联的实际
需求和潜力也更大[18]。不同配电区域的分布式电
源出力和负荷特性差异显著，通过在多电压等级
间实现柔性互联，有助于整体改善配电网各层
级、各区域的运行状况，并发挥其互补支撑潜
力[19-20]。多电压等级柔性互联配电网的相关研究
目前大多集中在运行控制层面，缺乏有效的规划
方法。综上所述，目前亟须一种计及综合收益的
面向多电压等级柔性互联配电网的SOP 选址定容
规划方法，以合理规划设计多电压等级配电网的
柔性互联方案。
为充分体现SOP 在多电压等级FDN 中的作
用，本文提出考虑经济性、可靠性综合收益的多
收稿日期：2024−01−18； 修回日期：2024−08−03。
基金项目：国网河北省电力有限公司科学技术项目
（SGHEJY00GHJS2200093）。
第 58 卷 第 1 期
中国电力
Vol. 58, No. 1
2025 年 1 月
ELECTRIC POWER
Jan. 2025
78



<!-- page 2/7 -->

电压等级SOP 协同规划方法。考虑FDN 典型运行
场景和预想故障场景，建立耦合正常运行调度和
故障辅助供电恢复环节的SOP 协同规划模型。借
助混合整数二阶锥规划方法进行求解，并在河北
省某实际配电网算例中进行测试，优化配置最大
化经济性、可靠性收益的SOP 装设方案，实现了
多电压等级配电网的柔性互联方案设计，有效提
升高比例DG 接入下FDN 运行的经济性和可靠性。
 
1    考虑综合收益的SOP 规划模型求解
多电压等级FDN 中，可以通过合理配置SOP
实现区域内与区域间的多电压等级柔性互联，充
分利用各区域内分布式电源和负荷特性的显著差
异，并整体优化FDN 运行时潮流分布和电压水
平。为了充分体现SOP 在FDN 正常运行时的改善
潮流分布作用和故障时的辅助支撑供电恢复能
力，本文提出考虑综合收益的SOP 规划模型，以
得到SOP 的最优装设位置与容量。
 
1.1    目标函数
将SOP 的建设运维成本和SOP 接入后FDN 的
年运行损耗成本、年停电损失成本作为SOP 规划
的综合目标函数，具体如下。
f
1）综合目标函数为
min f = f I + f O + f E + f R
（1）
f I
f O
f E
f R
式中：
为SOP 年投资建设成本；
为SOP 年运
行维护成本；
为FDN 年运行损耗成本；
为
FDN 年停电损失成本。
f I
2）SOP 年投资建设成本
为
f I = d(1+d)y
(1+d)y −1
∑
ij∈ΩSOP
cSOP
ij
SSOP
i j
（2）
ΩSOP
d
y
SSOP
ij
i j
cSOP
i j
ij
式中：
为配电网所有SOP 集合；
为贴现
率；为SOP 的经济使用年限；
为安装在支
路
上SOP 的容量；
为
处SOP 单位容量投
资成本。
f O
3）SOP 年运行维护成本
为
f O = η
∑
i j∈ΩSOP
cSOP
ij
SSOP
ij
（3）
η
式中：为SOP 年运行维护费用系数。
f E
4）FDN 年运行损耗成本
为
f E = 365cPELOSS
（4）
ELOSS =
NH
∑
h=1
NT
∑
t=1
ρh

∑
ij∈Ωb
rijI2
h,t,ij +
∑
ij∈ΩSOP
PSOP,L
h,t,ij
（5）
Ωb
cP
ELOSS
NH
NT
rij
ij
I2
h,t,i j
h
t
ij
PSOP,L
h,t,i
h
t
i
ρh
h
式中：
为配电网所有支路集合；
为单位电
价；
为整个配电网1 天内运行损耗的期望
值，包括线路损耗和SOP 损耗；
为运行场景个
数，
为单个场景中时间断面数；
为支路
的
电阻值，
为场景下时刻支路
电流幅值的
平方；
为场景下时刻安装在节点上SOP
的损耗；
为场景的概率。
f R
5）FDN 年停电损失成本
计算方法详见文
献[17]。
 
1.2    约束条件
为优化SOP 的装设位置及容量并同时模拟多
电压等级FDN 的正常运行和故障后供电恢复过
程，需要考虑以下约束。
规划过程中考虑电力电子模块单台容量的限
制，设定SOP 的最小配置容量，并考虑多电压等
级SOP 的协同规划建设，对应SOP 多电压等级协
同规划建设约束为
mij≤δSOP
ij
MSOP
（6）
SSOP
ij
= smodulemij
（7）
∑
i j∈ΩSOP
δSOP
ij
≤NSOP,I
（8）
∑
ij∈ΩSOP
δSOP
ij
≤NSOP,II, ∀i ∈Ωn
（9）
δSOP
ij
i j
MSOP
smodule
mi j
ij
NSOP,I
NSOP,II
Ωn
式中：
为表示
处SOP 是否装设的变量；
为SOP 装设上限；
为SOP 的单位配置容量；
为非负整数变量，表示安装在支路
上的SOP
模组数量；
、
分别为配电网SOP 装设
数量上限、单个节点SOP 装设数量上限；
为配
电网节点的集合。
基于典型日运行场景，以节点电压、线路潮
流、线路损耗、DG 出力、SOP 出力等作为优化
变量，建立典型运行场景下FDN 经济性约束，包
括配电网潮流、配电网运行、分布式光伏运行、
SOP 等约束可参考文献[21-23]。
基于预想的故障场景，建立FDN 在故障后供
电恢复场景下的可靠性运行约束，以节点电压、
第 1 期
贺春光等：考虑综合收益的多电压等级配电网柔性互联装置协同规划方法
79



<!-- page 3/7 -->

负荷恢复系数、线路拓扑状态、线路潮流、线路
损耗、DG 出力、SOP 出力、SOP 状态等作为优
化变量。建立故障场景下FDN 可靠性约束，具体
包括配电网辐射运行、配电网潮流、运行、分布
式光伏运行、SOP 运行、SOP 协调供电恢复、节
点电压等约束。
 
1.3    SOP 二阶锥规划求解
本文依据上述模型建立SOP 运行规划耦合的
单层规划模型，分别选取FDN 典型的运行场景和
预想故障场景，并借助混合整数二阶锥规划的方
法，调用商用求解器Cplex 求解，具体的规划流
程如图1 所示。得到的规划结果包含最优的
SOP 接入位置和容量，以及规划方案对应的各项
指标。
 
 
开始
输入算例参数及信息
生成SOP规划场景集：
1. 典型运行场景，依据输入典型日运行曲线
2. 预想故障场景，依据最大故障损失原则选取
建立考虑综合收益的配电网SOP多电压等级协同规划模型
输出SOP最优规划建设方案
结束
Cplex求解
典型运行场景FDN经济性约束
SOP规划建设约束
锥转化及二阶锥规划
故障场景FDN可靠性约束
建设&运维
成本
运行损耗成本
停电损失成本
混合整数二阶锥规划模型
综合成本
最小
 
图 1   SOP 规划流程
Fig. 1    Flow chart of SOP planning
 
2    算例分析
 
2.1    多电压等级配电网算例
本文选取河北省某实际多电压等级配电网的
局部作为算例，规划设计SOP 的最优配置方案并
验证所提规划方法的有效性。该区域2021 年列入
国家整县屋顶分布式光伏开发试点，光伏开发容
量超过160 MW，具有光伏装机容量大、分布广
等特点，但也使得当地电网出现潮流返送、电压
越限、线损增加等问题，危及配电网运行经济性、
安全性。该算例主要涉及3 个变电站及4 条10 kV
馈线，覆盖配电网的中、高电压等级。算例共计
含有241 个节点和239 条支路，共计55 个节点有
光伏接入，光伏的功率因数均为1.0。算例首端
平衡节点设定为110 kV 变电站S1 的节点2 和
220 kV 变电站S2 的节点1、节点2，其电压水平
分别为1.0 p.u.、1.03 p.u.、1.03 p.u.。算例中各区域
的负荷情况、DG 接入情况简要记录在表1 中。
 
 
表 1   算例基本情况
Table 1   Basic information of the case study
区域
节点数
有功负荷/
MW
无功负荷/
(MV·A)
DG接入/
MW
馈线A
45
3.19
1.36
2.18
馈线B
37
3.21
1.37
13.91
馈线C
63
4.77
2.03
1.18
馈线D
81
6.76
2.88
2.94
变电站S1
8
38.00
18.00
36.20
变电站S2
7
142.40
57.60
95.10
总计
241
198.33
83.24
151.51
 
SOP 装设上限为5 MV·A，单位配置容量为
0.1 MV·A；损耗系数为0.02；10 kV 馈线处SOP 单
位投资成本为800 元/(kV·A)，变电站内SOP 单位
容量投资成本为500 元/(kV·A)；贴现率为0.08，
使用年限为20 年，运行维护费用系数为0.01；故
障侧节点电压下限为1.0 p.u.，上限为1.05 p.u.。
为保证配电网安全稳定运行，10 kV 线路电流
幅值上限设为1 000 A，其他线路设为200 p.u.；
FDN 安全运行电压范围设为0.95 p.u.~1.05 p.u.。负
荷和DG 出力曲线如图2 所示，共考虑2 个典型
日的运行曲线作为SOP 规划考虑的典型运行场
景，每个场景包含12 个时间断面。预想故障仅考
虑算例中10 kV 线路的三相接地故障，通过线性
插值的方法获得各线路故障率，再根据停电造成
损失最大原则选取其中60 条线路故障作为SOP 规
划考虑的预想故障场景。线路故障修复时长为5 h，
分段开关动作时间为1 h，SOP 恢复供电时间为
5 min。算例中单位停电损失成本为10 元/(kW·h)，
中国电力
第 58 卷
80



<!-- page 4/7 -->

电价为0.5 元/(kW·h）。
 
2.2    优化方案效果分析与验证
为充分验证本文提出规划方法的有效性和体
现SOP 在多电压等级配电网中的显著作用，针对
上述算例给出如下3 种方案进行对比分析。
方案1：不规划SOP，得到配电网的初始运行
状态；
方案2：不规划SOP，允许弃光和弃负荷，并
以1.8 元/(kW·h) 和0.06 元/(kW·h) 的惩罚系数计入
运行损耗成本，优化得到满足运行条件的配电网
运行状态和年综合成本；
方案3：考虑中高压SOP 的协同规划建设，
以配电网年综合成本最小配置SOP。
使用提出的规划方法以及商业求解器Cplex
对上述方案进行求解，得到各方案对应目标函数
值以及SOP 最优配置方案。执行优化计算的计算
机处理器为Intel Xeon Gold 6226R，主频为2.90 GHz，
内存为383 GB，软件环境为Windows10，求解器
精度设置为1%。3 种方案的优化结果、方案3 对
应的SOP 最优配置结果分别如表2~3 所示。方案
1 给出了该配电网的初始运行状态，其中存在电
压越限、220 kV 变电站潮流倒送等问题。方案
2 模拟了通过弃光、弃负荷解决上述问题的场
景，但是成本的大幅增长严重降低了系统经济
性，并且没有提升系统可靠性。注意方案2 中的
停电损失成本也略高于方案1，这主要是由于求
解器精度限制导致的数值误差。
相比于方案1 和方案2，方案3 在充分考虑配
电网各方面综合成本的基础上，通过在关键位置
合理装设SOP 有效降低了FDN 的运行损耗和故障
停电损失，同时也实现了减少电压越限、减少潮
流倒送的目标。方案3 对应的SOP 装设结果如图3
所示。通过多电压等级SOP 的协同规划与配合，
实现了馈线间、台区间的柔性互联与能量互补。
方案1 中，线路损耗较大，当用电负荷达到高峰
或光伏出力达到高峰时，馈线电压越限严重，配
电网运行经济性较差。
馈线B 和馈线D 各节点的电压最值分布如
图4~5 所示。可以看出，方案3 中优化配置SOP 后，
系统电压水平得到明显改善，各节点电压可以维
持在安全运行范围[0.95,1.05] 内。避免了重负荷
时馈线末端电压越下限情况及DG 出力过多时
DG 接入处电压越上限情况，保障了配电网的安
全性、可靠性，也降低了线路损耗成本。
 
3    结语
为应对大规模新型源荷接入给多电压等级配
电网安全经济运行带来的挑战，本文提出考虑综
 
表 2   各方案下的优化结果
Table 2   Optimization results in the three schemes
方案1
方案2
方案3
综合成本/万元
—
457.3
357.7
SOP建设&运维成本/万元
—
0
129.1
运行损耗成本/万元
158.5
320.7
158.1
停电损失成本/万元
135.5
136.6
70.5
节点电压范围(p.u.)
0.94-1.07
0.95-1.05
0.95-1.05
S2最大反向负载率/%
2.6
0
0
 
00:00
04:00
08:00
12:00
16:00
20:00
24:00
时刻
a) 典型场景1
b) 典型场景2
00:00
04:00
08:00
12:00
16:00
20:00
24:00
时刻
0
0.2
0.4
0.6
0.8
1.0
水平 (p.u.)
水平 (p.u.)
负荷；
光伏出力
负荷；
光伏出力
0
0.2
0.4
0.6
0.8
1.0
 
图 2   负荷与DG 出力曲线
Fig. 2    Operation curves of load and DG
 
表 3   方案3 对应的SOP 最优配置
Table 3   Optimal designs of SOP in the third scheme
SOP装设位置
SOP装设容量/
(MV·A)
SOP装设位置
SOP装设容量/
(MV·A)
A20-B2
0.5
B32-D79
0.3
A42-C59
0.4
B35-D76
0.2
C45-B28
0.2
S1.1–S1.2
1.2
B7-D53
1.8
S1.7–S1.8
4.1
B23-D78
0.5
—
—
第 1 期
贺春光等：考虑综合收益的多电压等级配电网柔性互联装置协同规划方法
81



<!-- page 5/7 -->

合收益的多电压等级配电网SOP 协同规划方法，
以合理规划未来配电网多端、多电压柔性互联设
计。所提方法能够在规划中有效考虑配电网运行
损耗、故障停电损失、SOP 成本等方面因素，获
得经济性、可靠性综合性能最优的SOP 建设方
案。同时，通过对多电压等级配电网中SOP 进行
 
110 kV配电线路
5.1 km
馈线A
1
6
7
8
9
10
11
2
3
4
5
15
16
18
12
13
20
22
19
24
27
21
17
23
26
29
30
32
34
37
40
43
45
31
33
25
28
35
38
44
36
39
41
42
14
36
馈线D
1
2
3
4
5
6
8
9
10
11
13
12
15
16
14
18
23
19
20
21
7
22
24
26
28
30
31
33
42
40
46
32
35 38 45
48
34
39 44
37 43 47
36
41
50
54
49
52
56
58
51
59
60
61
62
53
55
57
63
66
70
71
64
67
72
75
79
65
68
73
76
69
74
78
77
80
81
17
25 27 29
2
6
1
4
5
7
8
3
11
9
26
10
12
14
13
30
31
15
18
19
16
17
27
28
29
32
33
34
35
37
20
22 24
21
23
25
馈线B
北
110 kV
35 kV
10 kV
220 kV
输
电
网
1
2
3
4
5
6
7
110 kV 变电站S1
1
2
3
4
5
6
7
8
220 kV
变电站S3
12.9 km
普通节点
SOP接入节点
光伏
馈线C
27
1
2
3
5
11
12
4
6
7
8
9
10
13
16
19
20
26
32
25
31
30
34
36
37
40
44
49
48
52
47
50
51
54
57
60
62
63
55
58
61
53
56
59
15
14
18
29
33
22
35
39
42
46
43
38
45
17
21
28
23
24
41
0.4 MV·A
0.2 MV·A
1.8 MV·A
0.3 MV·A
0.2 
MV·A
0.5 MV·A
220 kV变电站S2
1.2 MV·A
4.1 MV·A
0.5 MV·A
 
图 3   SOP 规划结果
Fig. 3    Optimization results of SOP
 
0.95
1 3 5 7 9 11 13 15 17 19
节点
21 23 25
37
35
33
31
29
方案Ⅰ；
方案Ⅲ
27
1.00
电压 (p.u.)
1.05
1.10
 
图 4   馈线B 节点电压最值
Fig. 4    Maximum and minimum voltage of nodes in
Feeder B
 
1
8
17
25
33
节点
41
49
73
81
65
57
方案Ⅰ；
方案Ⅲ
0.95
1.00
电压 (p.u.)
1.05
1.10
 
图 5   馈线D 节点电压最值
Fig. 5    Maximum and minimum voltage of nodes in
Feeder D
中国电力
第 58 卷
82



<!-- page 6/7 -->

合理规划，解决了算例中出现的电压越限、潮流
倒送等问题。配电网中源荷的不确定性对SOP 的
规划会产生一定影响，当前SOP 的协同规划方法
仍具有一定的局限性。未来可结合负荷、分布式
电源的概率性分布对模型进行改进，并继续结合
多端柔性互联、储能等技术探索配电网未来柔性
互联新形态。
参考文献：
 
 张俊成, 黎敏, 刘志文, 等. 基于改进交替方向乘子法的配电网柔性
负荷分层集群调控方法[J]. 中国电力, 2024, 57(1): 140–147.
ZHANG Juncheng, LI Min, LIU Zhiwen, et al. Hierarchical cluster
control  method  for  flexible  load  in  distribution  network  based  on
improved alternating direction multiplier method[J]. Electric Power,
2024, 57(1): 140–147.
[1]
 王金丽, 李丰胜, 解芳, 等. “双碳” 战略背景下新型配电系统技
术标准体系[J]. 中国电力, 2023, 56(5): 22–31.
WANG Jinli, LI Fengsheng, XIE Fang, et al. Research on technical
standard  system  of  new  distribution  system  under  double-carbon
strategy[J]. Electric Power, 2023, 56(5): 22–31.
[2]
 徐非非, 冯华, 覃洪培, 等. 计及不确定性的配电网分布式光伏承载
能力区间分析方法[J]. 浙江电力, 2023, 42(11): 86–95.
XU Feifei, FENG Hua, QIN Hongpei, et al. An analysis method of
DPV  hosting  capacity  interval  in  distribution  networks  under
uncertainties[J]. Zhejiang Electric Power, 2023, 42(11): 86–95.
[3]
 李泽成, 孙燕盈. 新型电力系统下考虑分布式光伏并网的配电网可
靠性评估[J]. 山东电力技术, 2023, 50(5): 1–5, 47.
LI  Zecheng,  SUN  Yanying.  Reliability  evaluation  of  distribution
network  considering  flexible  grid  connection  of  distributed
photovoltaic  power  generations[J].  Shandong  Electric  Power,  2023,
50(5): 1–5, 47.
[4]
 吴启亮, 谭彩霞, 章雷其, 等. 配电网与分布式电氢耦合系统的交互
策略研究[J]. 浙江电力, 2024, 43(2): 115–125.
WU  Qiliang,  TAN  Caixia,  ZHANG  Leiqi,  et  al.  A  study  on  the
interactive strategy for distribution networks and distributed electro-
hydrogen coupled systems[J]. Zhejiang Electric Power, 2024, 43(2):
115–125.
[5]
 黄强, 李宽, 丁敬明, 等. 含分布式光伏接入的有源配电网故障区段
定位新方法[J]. 山东电力技术, 2023, 50(11): 68–74.
HUANG  Qiang,  LI  Kuan,  DING  Jingming,  et  al.  A  novel  fault
section  location  method  of  active  distribution  network  with  the
[6]
integration of distributed photovoltaic[J]. Shandong Electric Power,
2023, 50(11): 68–74.
 仲泽天, 李梦月, 王加澍, 等. 一种有源配电网分布式光伏消纳能力
评估方法[J]. 电网与清洁能源, 2023, 39(2): 60–68.
ZHONG Zetian, LI Mengyue, WANG Jiashu, et al. An assessment
method  for  distributed  photovoltaic  absorption  capacity  of  active
distribution  networks[J].  Power  System  and  Clean  Energy,  2023,
39(2): 60–68.
[7]
 武永强, 张一帆, 王宇强, 等. 基于分布式和微服务技术的电能质量
监测系统设计与应用[J]. 内蒙古电力技术, 2023, 41(6): 84–89.
WU Yongqiang, ZHANG Yifan, WANG Yuqiang, et al. Design and
application of power quality monitoring system based on distributed
and  microservice  technology[J].  Inner  Mongolia  Electric  Power,
2023, 41(6): 84–89.
[8]
 李翠萍, 朱文超, 李军徽, 等. 分布式电源接入中压配电网的运行方
案研究[J]. 东北电力大学学报, 2023, 43(4): 57–64.
LI  Cuiping,  ZHU  Wenchao,  LI  Junhui,  et  al.  Research  on  the
operation scheme of distributed generation access to medium voltage
distribution  network[J].  Journal  of  Northeast  Electric  Power
University, 2023, 43(4): 57–64.
[9]
 杨旭, 王瑞, 余畅文, 等. 基于改进灰狼优化算法的分布式能源系统
优化调度[J]. 内蒙古电力技术, 2023, 41(1): 26–33.
YANG Xu, WANG Rui, YU Changwen, et al. Optimal scheduling of
distributed energy system based on improved grey wolf optimization
algorithm[J]. Inner Mongolia Electric Power, 2023, 41(1): 26–33.
[10]
 LI  P,  JI  H  R,  WANG  C  S,  et  al.  Coordinated  control  method  of
voltage and reactive power for active distribution networks based on
soft open point[J]. IEEE Transactions on Sustainable Energy, 2017,
8(4): 1430–1442.
[11]
 WANG  X  X,  YANG  W  Q,  LIANG  D.  Multi-objective  robust
optimization  of  hybrid  AC/DC  distribution  networks  considering
flexible interconnection devices[J]. IEEE Access, 2021, 9: 166048–
166057.
[12]
 宋毅, 孙充勃, 李鹏, 等. 基于智能软开关的有源配电网供电恢复方
法[J]. 中国电机工程学报, 2018, 38(15): 4390–4398, 4639.
SONG  Yi,  SUN  Chongbo,  LI  Peng,  et  al.  SOP  based  supply
restoration  method  of  active  distribution  networks  using  soft  open
point[J]. Proceedings of the CSEE, 2018, 38(15): 4390–4398, 4639.
[13]
 LI  P,  JI  J,  JI  H  R,  et  al.  Self-healing  oriented  supply  restoration
method  based  on  the  coordination  of  multiple  SOPs  in  active
distribution networks[J]. Energy, 2020, 195: 116968.
[14]
 王杰, 王维庆, 王海云, 等. 主动配电网中考虑条件风险价值的智能
[15]
第 1 期
贺春光等：考虑综合收益的多电压等级配电网柔性互联装置协同规划方法
83



<!-- page 7/7 -->

软开关的规划方法[J]. 电力系统保护与控制, 2022, 50(2): 1–11.
WANG  Jie,  WANG  Weiqing,  WANG  Haiyun,  et  al.  Planning
method  of  soft  open  point  for  an  active  distribution  network
considering  conditional  value-at-risk[J].  Power  System  Protection
and Control, 2022, 50(2): 1–11.
 张孝军, 林湘宁, 吴宇奇, 等. 兼顾微配网运行经济性与可靠性的智
能软开关选址优化[J]. 电力系统自动化, 2021, 45(8): 138–145.
ZHANG  Xiaojun,  LIN  Xiangning,  WU  Yuqi,  et  al.  Sitting
optimization of soft open point considering operation economy and
reliability  of  micro-distribution  network[J].  Automation  of  Electric
Power Systems, 2021, 45(8): 138–145.
[16]
 赵金利, 陈昊, 宋关羽, 等. 考虑可靠性收益的配电网智能软开关规
划方法[J]. 电力系统自动化, 2020, 44(10): 22–31.
ZHAO Jinli, CHEN Hao, SONG Guanyu, et al. Planning method of
soft  open  point  in  distribution  network  considering  reliability
benefits[J].  Automation  of  Electric  Power  Systems,  2020,  44(10):
22–31.
[17]
 孙充勃, 原凯, 李鹏, 等. 基于SOP 的多电压等级混联配电网运行
二阶锥规划方法[J]. 电网技术, 2019, 43(5): 1599–1605.
SUN  Chongbo,  YUAN  Kai,  LI  Peng,  et  al.  A  second-order  cone
programming  method  for  hybrid  multiple  voltage  level  distribution
networks  based  on  soft  open  points[J].  Power  System  Technology,
2019, 43(5): 1599–1605.
[18]
 王成山, 宋关羽, 李鹏, 等. 基于智能软开关的智能配电网柔性互联
技术及展望[J]. 电力系统自动化, 2016, 40(22): 168–175.
WANG  Chengshan,  SONG  Guanyu,  LI  Peng,  et  al.  Research  and
[19]
prospect  for  soft  open  point  based  flexible  interconnection
technology for smart distribution network[J]. Automation of Electric
Power Systems, 2016, 40(22): 168–175.
 李科, 田春筝, 刘巍, 等. 配电网多电压级协调供电模型及过渡方
案[J]. 电力系统及其自动化学报, 2017, 29(3): 126–130.
LI Ke, TIAN Chunzheng, LIU Wei, et al. Multi-voltage coordinated
power supply model of distribution grid and its transition scheme[J].
Proceedings of the CSU-EPSA, 2017, 29(3): 126–130.
[20]
 BARAN  M  E,  WU  F  F.  Network  reconfiguration  in  distribution
systems for loss reduction and load balancing[J]. IEEE Transactions
on Power Delivery, 2002, 4(2): 1401–1407.
[21]
 FARIVAR  M,  LOW  S  H.  Branch  flow  model:  relaxations  and
convexification:  Part  I[J].  IEEE  Transactions  on  Power  Systems,
2013, 28(3): 2554–2564.
[22]
 JIAN J, LI P, YU H, et al. Multi-stage supply restoration of active
distribution  networks  with  SOP  integration[J].  Sustainable  Energy,
Grids and Networks, 2022, 29: 100562.
[23]
作者简介：
贺春光（1979—），男，通信作者，硕士，高级工程
师（教授级），从事配电网规划技术研究，E-mail：
jyy_hecg@he.sgcc.com.cn；
王林峰（1979—），男，硕士，高级工程师，从事电
力技术经济、工程造价分析、电网规划技术研究，E-mail：
jyy_wanglf@he.sgcc.com.cn。
（责任编辑　杨彪）
Collaborative Planning Method of Flexible Interconnection Devices for Multi-
Voltage Level Distribution Network Considering Integrated Profits
HE Chunguang1, WANG Linfeng1, CAO Yuan1, AN Jiakun1, LEI Zijian2, SONG Guanyu2, JI Haoran2
(1. State Grid Hebei Economic and Technological Research Institute, Shijiazhuang 050000, China; 2. Key Laboratory of Smart Grid of
Ministry of Education (Tianjin University), Tianjin 300072, China))
Abstract: To avoid the above problems, a collaborative planning method of flexible interconnection devices for distribution
networks is proposed considering integrated profits. With the installation location and capacity of soft open point (SOP) optimized in
multi-voltage level distribution networks, the operation in normal and the supply restoration in fault are both improved, promoting
the system’s integrated indicators of economy and reliability. Finally, the case study is conducted based on an actual distribution
network data in Hebei province, verifying the effectiveness of the proposed method and analyzing the improvement of economy,
safety, and reliability.
This  work  is  supported  by  Science  and  Technology  Project  of  State  Grid  Hebei  Electric  Power  Co.,  Ltd.  (No.SGHEJY00GHJS
2200093).
Keywords: distribution network; plan and design; flexible interconnection device; soft open point
中国电力
第 58 卷
84
