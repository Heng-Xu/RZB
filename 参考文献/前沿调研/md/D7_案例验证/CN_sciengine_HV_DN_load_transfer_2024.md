<!--
source: D7_案例验证/CN_sciengine_HV_DN_load_transfer_2024.pdf
sha256: 6f458abedf5f6369f4f8fcc4f17a0cafb781351c11ff71d5c657d6a999f0951f
method: pymupdf
pages: 12
-->

<!-- page 1/12 -->

•电气工程•
DOI:10.15961/j.jsuese.201600269
基于功能单元的高压配电网负荷转供分层优化模型
金　勇
1,2，刘俊勇
1，张　曦
1，李　阳
1，刘友波
1，左坤雨
1
(1. 四川大学 电气信息学院，四川  成都 610065；2. 国网成都供电公司，四川 成都 610041)
摘　要:本文提出一种基于功能单元的高压配电网负荷转供分层优化模型以疏缓愈来愈复杂的城市电网阻塞，即
将城市电网抽象为上层220 kV供电通道和下层110 kV功能单元组的简化模型。上层模型中，通过功能单元可达性
矩阵定义“通道分配因子”引导单元组内负载在各供电通道的分配，定义“容载协调比例”协调“容”“载”间的不
平衡关系，并将二者作为粒子编码，利用算法初始化通道分配因子及容载协调比例，生成网络负载预分布；下层
模型中，事先枚举“有效供电路径矩阵”反映单元组内负载的实际分布，定义贴近度反映单元组内负载的实际分
配与通道分配因子的贴近程度，根据上层模型生成的通道分配因子及容载协调比例，引导下层各变电单元组的
实际负载及协调量向上层贴近。将上下层目标函数之和作为粒子群算法的适应度函数，即可形成上层全网有功
负载预分布引导，下层功能单元组交互执行的求解策略，使负载分布逐渐趋于合理的均衡状态，并在潮流校验的
前提下利用算法的迭代更新使系统负载分布逐渐趋于均衡。以离散二进制编码代表每一种操作序列，采用模糊
综合评价方法评估网络从初态到终态不同过渡方案下系统的安全水平，在优化方案确定后，制定一个在连续操
作下安全水平较优的操作序列，以保证每一步操作都能使电网运行在控制阈值范围内。利用某城市电网局部系
统验证了方法的有效性与在线分析的适用性。
关键词:高压配电网；负荷转供；功能单元；粒子群算法；模糊评价；动作序列操作序列
中图分类号:TM732　　　　　文献标志码:A　　　　　文章编号:2096-3246（2017）03-0179-12
Bi-level Model Based on Functional Units for Optimizing High-level Voltage Distribution Network
JIN Yong1,2，LIU Junyong1，ZHANG Xi1，LI Yang1，LIU Youbo1，ZUO Kunyu1
(1. School of Electrical Eng. and Info., Sichuan Univ., Chengdu 610065, China; 2. State Grid Chengdu Electrical Power Bureau, Chengdu 610016, China)
Abstract: In order to mitigate the complex congestion problem of urban power transimission network, a load transferring strategy for high-level
voltage distribution network (HVDN) with a novel bi-level programming model based on functional units (group) was presented. In the bi-level
model, the upper model was designed to guide the reasonable load allocation of the system and balance the transformer capacity and load, so the
channel allocation factor and load-capacity coordination were both taken as the particle coding of PSO, and then the load pre-allocation of the sys-
tem was determined by the channel allocation factor and load-capacity coordination; The lower model was established to reflect the closing de-
gree of the channel allocation factor and the actual load distribution identified by available power supply marix. Therefore, the actual load alloca-
tion and load-capacity coordination of the lower model whould be close to those of the upper. The objective function for the whole model was the
sum of the upper and lower, where the load pre-allcation and feedback were interactively executed and the optimal balance of the system load
whould be got under the power flow checking. At last, the transferring sequence was determined by fuzzy evaluation with discrete binary code to
assess the operational security which is the best scheme of continues operation. The proposed model can be efficiently solved for online analysis
and was verified by using the practical HVDN of an urban power system.
Key words: high-voltage distribution network (HVDN);load transfer;functional units (group);PSO;fuzzy evaluation;transfer sequence
高压配电网是输电网（220 kV及以上）与中压配
电网（10 kV及以下）之间的过渡电网和联系纽带配
电网作为联系电力系统与终端电能用户的重要环节，
是保证城市电网供电质量、提高电网安全经济运行
的关键环节之一。近年来，随着国民经济的发展，城
市化进程的加快，城镇电力负荷发展迅猛，然而城市
收稿日期:2016 – 03 – 22
基金项目:国家高技术研究发展计划资助项目（2014AA051901）
作者简介:金　勇（1978—）, 男, 博士生. 研究方向: 电力系统、智能配电网与电力市场. E-mail: junkcity78@163.com
————————— http://jsuese.ijournals.cn　　http://jsuese.scu.edu.cn —————————
第 49 卷 第 3 期
工 程 科 学 与 技 术
Vol. 49 No. 3
2017 年 5 月
ADVANCED ENGINEERING SCIENCES
May 2017



<!-- page 2/12 -->

110 kV高压配电网的建设却与实际发展产生了脱节。
由于通道制约、落点不足等诸多内外部问题，220 kV
变电站容量不足或负载分配不均的问题日益凸显，
为缓解近年来城市电网高峰时段输电断面阻塞与变
压器短期过载风险频繁发生的现象，调度员不得不
面临进行大面积较大时空范围下的负荷转供操作的
难题。由于缺乏有效的高压配电网在线分析工具，基
于经验或人工试凑的转供策略已难以满足配网经济
实时运行的要求，针对目前的现实情况，有必要就高
压配电网转供特征提出一种快速解算模型。
负荷转供的本质是一种网络重构，而高压配电
网的负荷转供更是一种有约束的多目标大规模非线
性组合非凸组合优化问题，通常是以达到某项性能
或指标最优的0–1混合整数规划模型，继而采用智能
算法求解。但现有研究大多针对10～35 kV的中低压
配电网重构求解问题，多是以降低网络损耗[1]、保证
供电可靠性[2]、优化电压[3]等作为求解目标，很少以
网络负载均衡等城市电网安全评估作为优化方向。
目前重构算法采用的方法一般有基于启发式规则的
支路交换法，传统数学优化法及随机搜索算法等。以
文献[4–7]为代表的支路交换法通过改变网络中环路
断开开关的位置，计算各节点注入电流的差异，寻找
最优重构状态，该方法计算快速，但只针对局部区域
考量，缺乏整体的把握。以文献[8–9]的分支界定法为
代表的数学优化方法将配网重构问题放在线性层面
解答，但其计算方式为直流潮流，负荷等效为恒定有
功负荷，虽然计算简单，但涉及到大规模潮流转移问
题时会产生较大误差。目前研究较多的随机搜索算
法[10–14]借助现代计算机强大的计算能力在庞大的解
空间中搜索令某一指标最优的重构方案，该方法能
够有效处理带有复杂网络约束及强非线性的重构问
题，但存在计算时间长，求解效率低，容易陷入局部
最优等问题。
对于既存在220 kV环网结构，又存在110 kV辐射
状结构的高压配电网，上述方法并不适用，且目前针
对高压配电网特点的重构策略研究较少，为此本文
通过分析高压配电网220 kV及110 kV网络的差异及
联系，抽象出功能单元组的概念，并在此基础上提出
一种基于功能单元的高压配电网负荷转供分层优化
模型，通过上层模型形成网络负载预分布，引导下层
功能单元组执行预分布方案，将下层执行结果反馈
给上层，评估负载预分布方案的优劣，形成上层引
导，下层执行的交互式求解策略，使负载分布逐渐趋
于合理的均衡状态，同时采用模糊综合评价方法评
估网络从初态到终态不同过渡方案下系统的安全水
平。某城市110 kV系统算例仿真表明该方法能够有
效削减决策空间，适用于城市高压配电网负荷转供
的在线分析。
1   高压配电网拓扑分析
在中国，根据电压等级将电网主要分为特高压
电网（500 kV及以上）、输电网（220～500 kV）和配电
网。其中，配电网又分为高压配电网（110、35 kV）、中
压配电网（20、10 kV）和低压配电网（0.4 kV、380/220
V）。作者从最基本的110 kV高压配电网站内结构、站
间联络关系出发，抽象出功能单元（组）的概念，并在
此基础上设计策略解决输电网（220 kV）的阻塞控制
难题。
1.1   基本功能单元
功能单元的作用是将电能从高压侧传送到低压
侧。对于110 kV系统而言，传送电能的关键设备为
110 kV变电站主变压器。根据站内设备功能，定义功
能单元。
功能单元：110 kV系统中，将电能从高压侧传递
至低压侧的设备组，包括110 kV主变、高压侧变压器刀
闸及低压侧变压器刀闸，该设备组以字母U表示，见图1。
图1中，P表示该功能单元传递的有功功率。当变
压器处于在线状态时，P为有效功能单元。由于城市
高压配电网无功补偿情况良好，为简化问题，只考虑
有功负载的均衡问题。
1.1.1    基于功能单元的站内结构表达
城市高压配电网中，110 kV变电站主要由2～3卷
容量为30～60 MVA的变压器组成，站内接线方式主
要有单母分段、内桥及其与线变组的T接组合两种，
分别如图2（a）、（b）所示。
以图2（a）所示接线方式为例，在实际运行中共
有4种典型运行方式。由于功能单元更关注传输的有
功功率及其联接的供电通道，因此功能单元的4种典
型站内连接方式可表达为如图3所示结构。图3中，
U1～U2为110 kV变电站功能单元。
1.1.2    基于功能单元的站间联络表达
110 kV变电站通常至少配置一条备供线路，网
 
儈঻חᔰޣ
ਈ঻ಘ
ѝ঻חᔰޣ
110 kV
10 kV
U
สᵜ䝽⭥ᇩ䟿অݳ
P, cos φ
P, cos φ
图 1　基本功能单元
Fig.1　Functional units
 
180
工程科学与技术
第 49 卷



<!-- page 3/12 -->

络中存在大量的以站间联络形式为主的备供路径，
运行方式极其多样。图4为某城市高压配电网局部拓
扑结构。以功能单元为顶点，以站内母联开关及备供
路径为边，则某城市局部高压配电网站间联络关系
可表达为如图5所示。
图5中：Ui表示功能单元，U1～U19为110 kV变电站
功能单元；Si表示电网中各个电源点，S1～S6为220 kV
变电站；虚线表示该供电路径处于非连通状态。由于
U7为“线变组”，在实际运行中与其他设备联络脆
弱，灵活性不高，因此本文不予考虑。
1.1.3    功能单元组
从图5可看出，在110 kV系统中存在着一些相互
之间有直接或潜在连接关系的功能单元，它们由一
个或多个220 kV站的110 kV出线供电，将这些220 kV
站的110 kV出线称为供电通道，并据此推演出功能
单元组的概念。
A
A
A
功能单元组：假设网络中共有n个功能单元，定
义其可达性矩阵
，其中，为n×n阶方阵， 中各元
素定义为：
Aij =
{ 1,若Ui到Uj至少存在一条通路；
0,否则
（1）
A
A
式中：
ij表示矩阵第i行第j列元素；Ui和Uj的连通可
达性分析可采取文献[6]所提的基于邻接矩阵的可达
性矩阵求法，此处不再赘述。
A
将可达性矩阵进行初等行列变换，得到形如式
（2）的方阵:
A′ =

Aα
···
O
...
...
O
···
Aγ

（2）
Aα、Aγ分别表示α×α及γ ×γ
α或γ
Aα各列向量在A
rα
rα
α
rα
Gα
式中，O表示全“0”矩阵，
维
全“1”方阵。该方阵表示与之关联的
个功能单
元是全连通的。取出
中对应的列序
数，记作
。其中，
为包含个元素的序列，
中每一
个元素分别对应了某个功能单元的序数。因此，定义
功能单元组
为：
Gα = {Ui|i ∈rα}
（3）
以图6所示的简单结构为例进行具体说明。图
6中，S1～S3为220 kV变电站，U1～U6为110 kV变电站
功能单元。
 
P1
P2
P1
P2
P3
P4
Ā㓯ਈ㓴ā
(a) অ⇽࠶⇥
(b) ޵ẕ৺ަо㓯ਈ㓴ⲴT᧕㓴ਸ
图 2　110 kV变电站主要站内接线方式
Fig.2　Primary inner diagram of 110 kV substation
 
 
U1
U2
P1
P2
U1
U2
U2ཡ᭸U1ཡ᭸
P1
P2
U1
U2
P1
P2
U1
U2
P1
P2
U1
U2
P1
P2
U1
U2
P1
P2
U1
U2
P1+P2
P1+P2
ᯩᔿ1
ᯩᔿ2
ᯩᔿ3
ᯩᔿ4
ᯝᔰ
䰝ਸ
图 3　功能单元站内结构表达方式
Fig.3　Illustration of inner connection based on functional
units
 
 
U1
U2
U3
U4
U5
U6
U8
U9
U10
U11
U12
U14
U15
U18
U19
S5
S4
S3
S2
S1
U16
U17
U13
U7
P1
P2
P5 P6
P3
P4
P7 P8
P9
P10
P11
P12
P17
P18
P19
P20
P13
P14
P15
P16
图 4　城市高压配电网局部拓扑结构示意图
Fig.4　Functional diagram of urban network
 
 
U1
U2
U3
U4
U5
U6
U8
U9
U10
U11
U12
U14
U15
U18
U19
S5
S4
S3
S2
S1
U16
U17
U13
U7
P1
Γ11
Γ12
Γ42
Γ43
Γ33
Γ32
Γ21
Γ53
P2
P5
P6+P7
P3
P4
P7
P8
P9
P10
P11
P12
P17
P18
P19
P13
P14
P15
P16
图 5　基于功能单元的站间结构表达
Fig.5　Illustration of outside connection based on function-
al units
 
第 3 期
金　勇，等：基于功能单元的高压配电网负荷转供分层优化模型
181



<!-- page 4/12 -->

为体现一般性，特意将编号打乱。由图6易知关
于Ui和Uj的可达性矩阵为：
1
2
3
4
5
6
A =

1
0
1
1
1
0
0
1
0
0
0
1
1
0
1
1
1
0
1
0
1
1
1
0
1
0
1
1
1
0
0
1
0
0
0
1

（4）
式中，矩阵最上面的数字1～6代表列编号，即是图6
中功能单元编号。
A
A′
将矩阵进行行列变换，得到
为：
1
5
3
4
2
6
A′ =

1
1
1
1
0
0
1
1
1
1
0
0
1
1
1
1
0
0
1
1
1
1
0
0
0
0
0
0
1
1
0
0
0
0
1
1

（5）
Aα、Aγ
式中，
分别为：
Aα =

1
1
1
1
1
1
1
1
1
1
1
1
1
1
1
1

, Aγ =
[ 1
1
1
1
]
。
Gα、Gγ
Aα、Aγ各列在A
rα、rγ
由式（5）可知，该结构共有2个功能单元组，分别
为
。对比
中对应的列序数，可
得到
为：
{ rα = {1,3,4,5}；
rγ = {2,6}
（6）
Gα、Gγ
因此功能单元组
所包含的设备表达为：
{Gα = {U1,U3,U4,U5}；
Gγ = {U2,U6}
（7）
功能单元组是实现负荷转供的最小可操作单
位，通过调整组内不同的拓扑结构，能够改变负载在
各供电通道的分配比例，从而实现负荷在各220 kV
变电站间的转供，达到负载率均衡的目的。
1.1.4    单元组有效供电路径矩阵
在功能单元组内（以下简称单元组），各功能单
元不能失电，且单元组内不能出现220 kV/110 kV电
磁环网，因此采用有效供电路径模型描述单元组内
拓扑结构。
假设某一单元组内有功能单元的个数为n，供电
通道数为N。定义第i个功能单元到第j个供电通道的
有效供电路径为n×N维矩阵Rus，有：
Rus(ξij) =

ξ11
···
ξ1N
...
...
ξn1
···
ξnN

（8）
ξij
ξij
ξij
ξi1,ξi2,··· ,ξiN
式中，
表示该功能单元可达的供电通道。若可达
到第j个供电通道，则
=1；否则，
=0。由于不能出
现电磁环网，一个功能单元一次只能选择一条供电
路径，故第i行元素
中只有一个为“1”。对
于某运行初始方式，通过采用基于堆栈操作的深
度搜索算法，可得到满足拓扑约束条件的初态供电
路径矩阵Rus.initial，因为若为实际运行状态，该矩阵不
存在失电功能单元，不会形成电磁环网，且为常数矩
阵。
定义单元组负载向量Lp如下：
Lp = (P(U1),P(U2),··· ,P(Un))
（9）
式中，P（Ui）表示功能单元Ui所带负载的大小。由于
Rus反映了Ui和Sj间的可达性关系，据此可定义负载
分配矩阵D如下：
D = LpRus
（10）
式中，D为一个1×N维行向量，D中元素表示各供电通
道所带负载大小。由D即可算出某一供电通道在单元
组总负载中的分配比例为：
ρj =
Dj
∑
j
Dj
×100%
（11）
∑
j
Dj
式中，ρj表示第j个供电通道中所带负载比例，Dj表示
D中第j个元素，
表示对D中所有元素求和。
2   基于功能单元的分层优化模型
由于110 kV功能单元组不同的拓扑结构决定了
各220 kV变电站负载率及线路传输功率，为避免输
电阻塞、变电站负载分布不均，采用2层结构的优化
模型，并用粒子群算法求解：上层优化模型中，利用
算法生成通道分配因子及容载协调比例，根据这两
种参数生成网络负载预分布；下层优化模型中，根据
上层生成的通道分配因子及容载协调比例，引导下
层各110 kV功能单元组负载分布状态及协调比例不
断向上层确定的负载预分布贴近，最后进行潮流校
验。利用算法的迭代更新机制使负载分布逐渐趋于
均衡。其示意图如图7所示，其中，S1～S5为220 kV
变电站。
 
U1
U2
U3
U4
U5
U6
S3
S2
S1
图 6　简单结构示意图
Fig.6　Schematic diagram of functional units
 
182
工程科学与技术
第 49 卷



<!-- page 5/12 -->

τm
j
τm
j
τm
j
图7中，
表示220 kV电源点Sj在功能单元组
Gm的通道分配因子，hm表示功能单元组Gm的容载协
调比例，虚圆圈表示协调前单元组总负载，实圆圈表
示协调后单元组总负载，ρj
m表示220 kV电源点Sj在功
能单元组Gm所占负载实际比例。
的作用是引导
ρj
m向
贴近，最终实现220 kV变电站负载均衡。
2.1   上层优化模型
上层优化模型主要为满足220 kV变电站负载均
衡，同时避免输电通道阻塞。
2.1.1    通道分配因子和均衡度
τm
j
以图5所示的网络结构为例，图5中共有：5个电
源点，即S1，S2，…，S5；8个供电通道，即Γ11、Γ12、Γ21、
Γ32、Γ33、Γ42、Γ43、Γ53，其中，Γjm表示电源点Sj与功能
单元组G m 间的供电通道；3 个功能单元组，即
G1={U1，U2，U3，U4，U5，U6}，G2={U8，U9，U10，U11，
U12，U13}，G3={U14，U15，U16，U17，U18，U19}。据此定
义通道分配因子：
表示220 kV电源点Sj通过供电通
道Γj
m向功能单元组Gm分割的负载比例，且满足约束
条件如下：
n
∑
j=1
τm
j = 1
（12）
τm
j
τ1
1 +τ1
2 = 1
式中，n为系统内220 kV电源点Sj总数，
为与功能单
元组Gm相关的全部通道分配因子。以图5所示的单元
组G1为例，有
。
通道分配因子确定后，各220 kV变电站Sj的负载
率可由式（13）计算：
κ(Sj) =
n
∑
m=1
(Pm
j )′τm
j /P j(max)
（13）
κ(S j)
τm
j
(Pm
j )′
Pj(max)
式中，
为220 kV变电站Sj的负载率，
为与电源
点Sj相关的通道分配因子，
为与电源点Sj相关的
功能单元组Gm协调后的总有功功率，
为电源点
Sj的极限有功功率。
为满足负载率均衡，以2 – 范数形式描述220
kV变电站负载均衡程度为：
K = ||κ(Sj)−k0||2。
k0 = 1
N
∑
κ(Sj)
其中，
表示平均负载率。
2.1.2    容载协调比例和协调度
由于负载和容量之间有时存在量的不平衡关
系，导致无论采用何种分配方式都不合理，因此在某
约束条件下没有可行解。据此定义容载协调比例，以
协调容量和负载间量的不平衡关系。
hm ≤hmax
m
P′
m
容载协调比例：hm为单元组Gm切去的有功负荷
占组内总负荷的比例，有
。Pm为单元组Gm在
协调前的总有功负荷，则协调后单元组Gm的总负荷
，计算如下：
P′
m = Pm(1−hm)
（14）
为保证供电可靠性，组内被协调的负荷总量不
能过多，因此定义协调度，反映协调后各单元组的负
载总体水平。
协调度为全网络总的容载协调水平，用H表示，
计算如下：
H =
∑
m
hm
（15）
在优化过程中，应保证H尽可能小。H越大，则容
量与负载的关系越不和谐；若H超过可接受的水平，
则应从规划层面考虑增加设备投资以提高电网的支
撑能力，满足供电需求。
2.1.3    上层优化模型
上层模型应保证全网变电站负载最均衡且协调
度最小，因此目标函数应为两者之和的最小值。其约
束条件应分别满足式（12）的条件约束、容载协调比
例的限额约束、线路传输功率约束以及节点电压约
束，则上层优化模型如下：
F = min(ω1K +ω2H)
s.t.
n
∑
j=1
τm
j = 1,
0 ≤hm ≤hmax
m ,
Sil ≤Smax
il ,
µmin
j
≤µ j ≤µmax
j
,
ω1 +ω2 = 1
（16）
S il
式中：
为电源点Si、Sl间线路传输视在功率；μj为220
kV电源点Sj电压；ω1、ω2分别为K、H权重，其和为1。
 
PSO㇇⌅
൷㺑ᓖ
䍤䘁ᓖ
䍤䘁ഐᆀ
䍤䘁ഐᆀ
൷㺑ሬੁഐᆀ
ᇩ䖭ॿ䈳∄ֻ
䍏䖭亴࠶ᐳ
ॿ䈳ᓖ
кቲ
лቲ
S5
S4
S3
S2
S1
τ1,1
h2
h1
ρ1,1G1
G2
τ5,1
τ2,1
ρ5,1
ρ2,1
τ4,2
ρ4,2
τ3,2
ρ3,2
图 7　模型求解示意图
Fig.7　Schematic diagram of model programming
 
第 3 期
金　勇，等：基于功能单元的高压配电网负荷转供分层优化模型
183



<!-- page 6/12 -->

2.2   下层优化模型
下层优化模型通过调整各功能单元组拓扑结
构，使单元组内负载分配向通道分配因子贴近，实现
有功负载均衡。
2.2.1    贴近因子与贴近度
为描述单元组内负载实际分配比例与通道分配
因子的贴近程度，定义贴近因子为单元组内负载实
际分配比例关于通道分配因子的离差平方和的平方
根，表达式如下：
cm =
v
t nm
∑
j=1
(ρm
j −τm
j )2
（17）
τm
j
ρm
j
Γm
j
式中，cm为功能单元组Gm的贴近因子，nm为向功能单
元组Gm直接供电的220 kV电源点总数，
为与单元
组Gm相关的通道分配因子，
为所有与单元组m相
连的供电通道
的实际负载分配比例。
cm表征了组内负载在各供电通道的实际分配状
态与由通道分配因子产生的负载预分配状态的合同
性。cm越大，则与预分配状态差异越大，反之越小。
由于受单元组内拓扑约束的限制，组内负载分
配比例不一定能够很好地贴近通道分配因子，即某
种均衡方案受网络拓扑结构的影响，实现难度很大。
为此定义贴近度来描述均衡方案对网络拓扑结构的
适应性，表达式如下：
χ =
∑
m
cm
（18）
χ
式中，为均衡方案的贴近程度，其值越小表明均衡
方案对网络拓扑结构的适应性越强。
2.2.2    协调向量
由于上层确定了容载协调比例，则下层功能单
元组应按照比例切去一定量的负荷。而组内各功能
单元所带的负荷成分不尽相同，有些单元所含重要
负荷比例很大，可切负荷比例小；有些单元所带负荷
可切比例大。据此定义协调向量，反映组内各功能单
元可协调的负载量大小。
协调向量：由组内各功能单元可协调的负载比
例组成的向量，表达式如下：
X = (x1, x2,··· , xn)
（19）
0 ≤x1 ≤1
式中：xi为功能单元Gi可协调的负载比例，
；
n为组内功能单元总数。则协调后各功能单元的负载
大小计算如下：
P′
i = Pi −Pmhm ×
Pixi
ni
∑
i=1
Pixi
（20）
ni
∑
i=1
Pixi
式中，ni为功能单元组Gm中功能单元的个数，Pixi为
功能单元Gi实际可协调的负载量，
为功能单元
Pmhm
P′
i
组Gm总的实际可协调负载量，
为由上层容载协
调比例确定的单元组Gm的负载协调量，Pi、
分别为协调
前后功能单元Gi的有功负荷。
2.2.3    开关动作次数
通过枚举单元组有效供电路径矩阵Rus，完成通
道分配因子的贴近后，将Rus与初态供电路径矩阵
Rus.intial进行对比，得到开关动作次数表达式如下：
O =
∑
|Rus(i, j)−Rus.initial(i, j)|
2
（21）
式（21）表示将Rus与Rus.intial矩阵中所有对应元素
求差，并取绝对值，再将结果求和，最后除以2得到开
关动作次数。
2.2.4    下层优化模型
下层优化模型应保证与上层模型最贴近，且开
关动作次数最小，因此其目标函数应为两者之和的
最小值。其约束条件应分别满足有无功潮流等式约
束、110 kV网络节点电压约束以及线路传输功率约
束，则下层优化模型如下：
f =min(ω1χ+ω2O)
s.t.
Pi = ui
N
∑
j=1
u j(gij cos θij +bij sin θij)
Qi = ui
N
∑
j=1
uj(gij sin θij −bij cos θij)
umin
i
≤ui ≤umax
i
S min
pq ≤S pq ≤S max
pq
ω3 +ω4 = 1
（22）
S pq
χ
式中：ui为110 kV节点电压；
为110 kV网络节点p、
q间传输视在功率；Pi、Qi分别为110 kV节点有功无功
约束；ω3、ω4分别为
和O的权重，其和应为1。
2.3   基于粒子群优化算法的求解策略
粒子群优化算法具有实现简单，收敛速度快等
特点，易于满足在线分析实时性的需求，因此采用粒
子群优化算法求解该模型。
2.3.1    编码方式
以通道分配因子及容载协调比例为变量，编码为：
xi = {τ1
1,τ2
1,··· ,τ1
2,τ2
2,··· ,h1,··· ,hN′}；
N′
∑
m=1
τm
j = 1,∀j = 1,2,··· ,n。
（23）
N′
式中，xi为第i个粒子位置，n为系统内220 kV电源点
Sj总数，
为功能单元组数量。
2.3.2    适应度函数
粒子位置确定后，可根据式（16）确定220 kV变
电站负载预分布，得到关于上层均衡度和协调度的
184
工程科学与技术
第 49 卷



<!-- page 7/12 -->

总和指标F；由式（22）确定功能单元组对通道分配因
子的贴近度及动作次数，得到下层关于贴近度和动
作次数权衡后的指标f。将F、f二者作为粒子群算法的
适应度函数，综合反映上层均衡策略及下层功能单
元组的贴近程度，其表达式如下：
Fobj = min(F + f)
（24）
2.3.3    求解流程
采用粒子群优化算法求解该模型。首先，生成上
层通道分配因子和容载协调比例，由式（16）形成网
络负载预分布；然后，通过枚举下层功能单元组的有
效供电路径矩阵Rus，根据式（22）计算贴近度，找到
贴近度最小的有效供电路径矩阵，利用算法的迭代
更新机制，使得F、f不断减小，最终使网络负载分布
趋于合理的均衡状态。粒子位置和速度更新过程如下：
vk+1
id = ωvk
id +c1rk
1(pbestk
id −xk
id)+c2rk
2(gbestk
id −xk
id) （25）
xk+1
id = xk
id +vk+1
id
（26）
vk
id
xk
id
rk
1 rk
2
式中：
为粒子i的第d维在第k次迭代时的速度；
为
粒子i的第d维在第k次迭代时的位置；ω为惯性因子，
反映了粒子保持原有速度的能力，ω越大，则粒子的
全局搜索能力越强，反之，粒子越倾向于局部搜索；
c1、c2为学习因子，反映了粒子追随自身历史最优位
置和种群最优位置的能力；、为[0，1]间的随机数。
算法求解流程如下：
1）随机初始化m个粒子位置，即通道分配因子及
容载协调比例。
2）根据式（16）计算负载在220 kV网络中的预分布。
χ
3）枚举各功能单元组有效供电矩阵Rus，按式
（22）计算贴近度，并选择
值最小的拓扑状态。
4）进行潮流校验，检验是否满足式（16）、（22）中
的网络约束。
5）根据式（24）计算适应度函数。
6）判断是否满足退出条件。若“是”，则退出；若
“否”，则转到步骤7）。
7）按式（25）、（26）更新粒子速度和位置，转到步骤2）。
算法求解流程如图8所示。
需要说明的是：在单元组贴近步骤中，各单元组
的贴近过程是相互独立的，因此可采取分布式并行
计算结构从而能够进一步提高求解速度。
3   基于模糊评价的操作序列判定
为解决断面阻塞与变压器过载风险，调度员需
在长时间内操作多个开关，其重构过程是一个长时
间动态过程。因此在确定了开关动作方案后，需要制
定一个在连续控制下安全水平较优的操作序列，以
保证系统能够安全的从初态过渡到终态。
由于在倒闸操作过程中，不同的调度员侧重的
安全指标有所不同，而衡量系统安全水平指标的优
劣并未有明确的划分标准，因此，采用模糊评价的方
法评估历次倒闸操作中系统的安全水平。将系统安
全指标模糊化，以隶属度函数大小来反映安全指标
的优劣。给不同的指标赋予不同的权重，从而满足调
度员相应的需求。
3.1   问题模型
在开关操作的每一步，都应保证系统的电压偏
差、线路负载率及变压器负载率在可接受的水平内。
定义第i步操作对系统的影响评估如下：
εi = ω5
1
p
p
∑
j=1
v
(i)
j +ω6
1
q
q
∑
k=1
l
(i)
k +ω7
1
r
r∑
m=1
s
(i)
m
（27）
v
(i)
j
l
(i)
k
s
(i)
m
ω5、ω6、ω7
ω5+ω6+ω7=1
式中：
为第i步操作后节点j的电压隶属度，计算式
见式（28）；
为第i步操作后线路k的负载率隶属度，
计算式见式（29）；
为第i步操作220 kV变电站m的
负载率隶属度，计算式见式（30）；
为3个指
标的权重，且
。式（28）～（30）中，3个指
标的函数图像分别如图9（a）、（b）、（c）所示。
v
(i)
j =

0, V(i)
j < Vmin；
V(i)
j −Vmin
Vnorm −Vmin
, Vmin ≤V(i)
j ≤Vnorm；
Vmax −V(i)
j
Vmax −Vnorm
, Vnorm ≤V(i)
j ≤Vmax；
0, V(i)
j ≥Vmax
（28）
V(i)
j
式中：
为在第i步操作中节点j的电压幅值；Vmin、
Vmax分别为正常运行时电压的最大最小标幺值，文中
取0.95和1.05；Vnorm为基准电压标幺值，文中取1。
 
ᔰ࿻
䲿ᵪ⭏ᡀmњ㕆⸱њփ
䇑㇇൷㺑ᓖǃॿ䈳ᓖ
᷊Ѯᴹ᭸׋⭥䐟ᖴ⸙䱥
▞⍱ṑ傼
䇑㇇䘲ᓄᓖ࠭ᮠ
䗃ࠪᴰ㓸ᤃᢁ⣦ᘱ
㔃ᶏ
ս㖞ᴤᯠ
кቲ˖สҾ൷
㺑ሬੁഐᆀ৺
ᇩ䖭ॿ䈳∄ֻ
Ⲵ䍏䖭亴࠶ᐳ
лቲ˖┑䏣㖁
㔌㓖ᶏⲴঅݳ
㓴䍤䘁ㆆ⮕
൷㺑ᓖ
ॿ䈳ᓖ
䍤䘁ᓖ
ᴤᯠ⁑ඇ
ᱟ੖᭦ᮋᡆ䗮ࡠ
ᴰབྷ䘝ԓ⅑ᮠ"
N
Y
图 8　粒子群算法流程图
Fig.8　Flow chart of BPSO
 
第 3 期
金　勇，等：基于功能单元的高压配电网负荷转供分层优化模型
185



<!-- page 8/12 -->

l
(i)
k =

l(i)
k
Lmin
,0 ≤l(i)
k ≤Lmin；
1,Lmin ≤l(i)
k ≤Lmax；
L+ −l(i)
k
L+ −Lmax
,Lmax ≤l(i)
k ≤L+；
0,l(i)
k > L+
（29）
l(i)
k
式中：
为第i步倒闸操作线路k负载率；Lmin、Lmax分
别为正常运行时线路负载率最小、最大取值；L+为线
路所能承受的最大负载率，文中取1.5。
s
(i)
m =

S (i)
m
Sopt
,0 ≤S (i)
m ≤Sopt;
Smax −S (i)
m
Smax −Sopt
,Sopt ≤S (i)
m ≤Smax;
0,S (i)
m > Smax
（30）
S (i)
m
S opt
式中：
为第i步倒闸操作220 kV站m负载率；
为
变电站最佳负载率，文中取0.8。
定义n步倒闸操作后总的适应度函数如下：
Θ =
n
∑
i=1
εi
（31）
3.2   基于二进制粒子群优化算法的求解流程
通过双层模型计算得到最优解后，调度员需在
长时间内操作多个开关，才能从越限初态转移到最
优终态。因此有必要制定一个安全水平最优的操作
序列，保证倒闸过程中系统始终运行在安全边界以
内。采用二进制粒子群优化算法求解该模型。为排除
不可行的编码方案，提高编码效率，将操作序列空间
映射到二进制空间中，以离散二进制编码表示每一
种操作序列，具体过程如下：
将最优拓扑终态与越限初始状态对比，得到动
作开关集合σ，如下：
σ = {a1,a2,··· ,an}
（32）
ϕ
式中：ai为需要动作的第i组开关对，即闭合一个开
关，断开另一个开关；集合的大小n就是开关总的操
作次数。对集合中的元素进行全排列，可得到n!种操
作序列，构成操作序列判定问题的求解空间为：
ϕ = [ϕ1,ϕ2,··· ,ϕN
]
（33）
ϕi
ϕi
ϕ
ϕ1
000···000
|      {z      }
NDP
ϕ2
000···001
|      {z      }
NDP
式中：N=n!；
为1×n维操作序列向量，每一个
都对
应了一种操作顺序。令N′=N-1，将N′转换为二进制码
NB，其位数为NDP，至此可用不超过NB的NDP位二进制
码来表示解空间，即粒子编码
 为
，
为
，以此类推。
 
不同的粒子位置对应着不同的动作顺序，利用
算法的迭代更新机制搜索最优动作序列。粒子位置
和速度的更新过程如式（34）、（35）、（36），公式的推
导过程此处不再赘述。
vk+1
id = ωvk
id +c1rk
1(pbestk
id −xk
id)+c2rk
2(gbestk
id −xk
id) （34）
sigmoid(vk+1
id ) = 1/(1+exp(−vk+1
id ))
（35）

xk+1
id = 1,ρk+1
id < sigmoid(vk+1
id )；
xk+1
id = 0,ρk+1
id ≥sigmoid(vk+1
id )
（36）
二进制粒子群算法与普通粒子群算法的主要差
异在于粒子位置的更新过程是由式（35）所示的“S”
函数决定，它实际上反映了粒子“翻转”的概率。速度
越大，则越倾向“1”；反之，则越倾向“0”。
4   算例分析
4.1   算例说明
以某城市局部高压配电系统为例，基于功能单
元的拓扑结构示意图如图10所示。
图10中，共有6个功能单元组，转供路径、母联开
关多达44个，高峰时期总负荷830 MW。
4.2   算例验证
初始状态下，220 kV变电站和线路负载的分布
见表1、2。
从表1、2可看出，全网负载分布极不均衡，部分
变电站重载（如S1、S2、S6），而部分变电站轻载（如
S3、S5）。线路负载率超标的线路有S3–S5，已经严重超
限额。以第2.2.3节所述流程进行负载均衡，将变电站
负载率控制在不同水平下，首先不考虑动作次数限
制，对所提出的方案进行测试，得到结果如图11所示。
由图11（a）、（b）可知：当变电站负载率约束逐渐
降低时，均衡度数值有了明显降低，但贴近度数值有
 
䍏䖭⦷
⭥঻
䳦኎ᓖ
䳦኎ᓖ
Vmin
Vmax
Vnorm
Lmin
Lmax
L+
1
1
(a) ⭥঻䳦኎ᓖ
(b) 㓯䐟䍏䖭⦷䳦኎ᓖ
䍏䖭⦷
䳦኎ᓖ
Sopt
Smax
1
(c) ਈ⭥ㄉ䍏䖭⦷䳦኎ᓖ
图 9　3种指标隶属度函数
Fig.9　Membership functions of three indices
 
186
工程科学与技术
第 49 卷



<!-- page 9/12 -->

所增大，说明为了实现全网负载更均衡，下层模型贴
近上层策略的难度越来越大，但有一定的均衡效果。
负载率控制在90%和80%以下时，都没有出现减负荷
情况，只是动作次数有了明显升高（由3次增加为
8次）。当约束进一步降低时，如图11（c）所示，将负载
率控制在70%以下时已没有可行方案，必须采取协调
措施来协调容量和负载间量的关系（切负荷比例为
8%），在新的状态下实现负载均衡，尽管均衡化效果
相较于图11（a）、（b）最优，但付出了减负荷代价，且
贴近效果并非最佳，变电站实际负载率和动作次数
均有所上升。
 
表 1　变电站负载率初始工况
Tab.1　 Initial load ratio of 220 kV substations
 
变电站
S1
S2
S3
S4
S5
S6
负载率/%
94.9
87.5
30
47.2
16.9
95.2
 
 
表 2　线路负载率初始工况
Tab.2　 Initial load ratio of 220 kV lines
 
线路
负载率/%
BS–S1
85
BS–S2
78
BS–S3
83
BS–S4
79
S1–S2
64
S1–S5
43
S1–S6
87
S3–S5
129
S4–S5
23
S4–S6
32
 
 
(a) 220 kV㌫㔏㔃ᶴ 
(b) 110 kV㌫㔏ࡍ࿻ᐕߥ
অݳ㓴3
অݳ㓴1
অݳ㓴2
অݳ㓴4
অݳ㓴5
অݳ㓴6
U1
U2
U3
U4
U5
U6
U8
U9
U10
U11
U12
U14
U15
U18
U19
U20
U22
U21
U23
U24
U25
U26
U33
U34
U32
U31
U30
U29
U28
U27
S5
S6
S3
S4
S2
S1
U16
U17
U13
U7
550 kVㄉ
S5
S6
BS
S4
S3
S2
S1
z15
z02
z01
z03
z04
z35
z45
z46
z16
图 10　基于功能单元的某城市局部高压配电系统拓扑结
构示意图
Fig.10　Functional structure of a local urban HVDN based
on functional unit
 
 
 ࡍ࿻ᐕߥ
䍏䖭⦷90%ԕлˈ
ࣘ֌⅑ᮠн䲀
(a) ᧗ࡦ൘90%ԕл, н䲀ࣘ֌⅑ᮠ 
 ࡍ࿻ᐕߥ
䍏䖭⦷80%ԕлˈ
ࣘ֌⅑ᮠн䲀
(b) ᧗ࡦ൘80%ԕл, н䲀ࣘ֌⅑ᮠ 
൷㺑ᓖK: 0.1;
ॿ䈳ᓖH: 0.08;
䍤䘁ᓖX: 0.27;
ࣘ֌⅑ᮠ: 6。
൷㺑ᓖK: 0.32;
ॿ䈳ᓖH: 0;
䍤䘁ᓖX: 0.26;
ࣘ֌⅑ᮠ: 8。
൷㺑ᓖK: 0.6; 
ॿ䈳ᓖH: 0;
䍤䘁ᓖX: 0.2;
ࣘ֌⅑ᮠ: 3。
 ࡍ࿻ᐕߥ
 䍏䖭⦷70%ԕлˈ
ࣘ֌⅑ᮠн䲀
(c) ᧗ࡦ൘70%ԕл, н䲀ࣘ֌⅑ᮠ
S5
S6
S4
S3
S2
S1
1.0
0.8
0.6
0.4
0.2
0
1.0
0.8
0.6
0.4
0.2
0
1.0
0.8
0.6
0.4
0.2
0
S5
S6
S4
S3
S2
S1
S5
S6
S4
S3
S2
S1
图 11　不同负载率水平下的均衡性控制效果
Fig.11　Balancing effects of substation under different load
controls
 
第 3 期
金　勇，等：基于功能单元的高压配电网负荷转供分层优化模型
187



<!-- page 10/12 -->

所提出的方案对220 kV线路传输功率的控制效
果如图12所示。
初始工况下，220 kV输电线路S3–S5严重超热稳
定极限运行，通过算法重构后极大缓解。
考虑到实际操作过程中，倒闸操作次数不宜过
多，因此在适应度函数中加入动作次数约束。比如，
考虑负载率水平控制在70%下的均衡场景，将动作次
数控制在5次以下的均衡结果与不限动作次数的图
11（c）做对比，得到结果如图13所示。
从图13可知，加入了动作次数约束后，均衡方案
的实现难度增加，均衡度较图11（c）不考虑动作次数
约束的结果而言，其形状略微畸形，均衡度K数值偏
大，说明均衡效果下降；更重要一点是由于限制了动
作次数，使得“容”“载”协调力度加大，负载量由
8%上升并超过了27%，这说明了均衡性、协调度和动
作次数优化在一定运行空间下的矛盾性。
4.3   性能比较
将本文提出的方案与文献[15]所述的基于环路
编码方案进行比较，求解本文第4.1节所述算例，得到
不同网络规模下的计算时间，对比结果见图14。
由图14可知，本文方法较文献[15]方法而言，计
算时间明显降低，且随网络规模的增加，本文方法优
越性更加明显。这是因为文献[15]采用环路编码的策
略，由于高压配电网多环态非深度的特点，会造成网
络中存在大量的环，导致文献[15]所述方案控制变量
激增，并且网络中会存在多条支路共环的情况，因
此，在解环的过程中还需要花费额外的计算时间处
理，导致计算时间大大增加。
4.4   开关动作序列判定
由于配电网中开关的闭合、断开行为总是成对
出现，以保证辐射性结构，因此可将动作行为成对出
现的2个开关组合成一个动作组。为满足动作次数限
制，以负载率控制在90%水平下为例进行分析。对比
网络初态和终态，得到开关动作组如表3所示。
ω5、ω6、ω7
采用第3节所述动作序列判定方法，采取第3.1节
中不同的权重（
）分配方案，得到的可行动
作序列如表4所示。
3种不同权重取值对系统安全水平的影响分别
如图15（a）、（b）、（c）所示。
从图15可看出，不同权重对系统安全水平的影
 
BS−S1
BS−S2
BS−S3
BS−S4
S1−S2
S1−S5
S1−S6
S3−S5
S4−S5
S4−S6
0.0
0.2
0.4
0.6
0.8
1.0
1.2
1.4
㓯䐟㕆ਧ
䍏䖭⦷/%
ࡍ࿻ᐕߥ
䍏䖭⦷90%ԕл
䍏䖭⦷80%ԕл
䍏䖭⦷70%ԕл
 
图 12　不同负载率水平下的220 kV线路控制效果
Fig.12　Balancing effects of 220 kV lines under different load controls
 
 
ࡍ࿻ᐕߥ
䍏䖭⦷70%ԕлˈ
ࣘ֌⅑ᮠ≤5
൷㺑ᓖK: 0.29;
ॿ䈳ᓖH: 0.27;
䍤䘁ᓖX: 0.29;
ࣘ֌⅑ᮠ: 5。
S5
S6
S4
S3
S2
S1
1.0
0.8
0.6
0.4
0.2
0
图 13　负载率控制在70%以下，动作次数限制在5次以下
Fig.13　Balancing effects of substation under 70% load
control and five transferring actions
 
 
30
40
50
60
35
45
55
2
10
4
6
8
12
14
16
ਈ⭥ㄉњᮠ
䇑㇇ᰦ䰤/s
18
ᵜ᮷ᯩ⌅
᮷⥞[15]ᯩ⌅
图 14　不同算法的计算时间对比
Fig.14　Comparisonof computation time under different
methods
 
188
工程科学与技术
第 49 卷



<!-- page 11/12 -->

ω5 > ω6、ω7
ω6 > ω5、ω7
响。例如，图15（a） 中的方案1更加侧重电压偏差
（
），则在倒闸操作过程中，其最低节点电
压比另外两种方案明显高一些，即电压偏差最小。图15（b）
中的方案2更侧重线路负载率（
 
），则在倒
闸操作过程中，其最大线路负载率比另外两种方案
明显低很多。
5   结　论
城市电网普遍面临尖峰时期大功率潮流转移难
题。这种大范围、大规模的负荷转供操作，传统配网
重构方法并不适用，且也缺乏相关优化运行模型支
撑。本文的研究弥补了高压配电网负荷转供在线分
析工具的不足，为调度员实施大范围负荷转供提供
在线决策依据。所提方法具有以下特点：
1）分析了110 kV高压配电网的站内和站间拓扑
结构，提出了功能单元组及供电通道的物理模型，有
效规避了采用传统“0–1开关状态模型+智能算法”方
案在计算负担重、不可行解多和稳定性差等方面的
劣势。
2）构建双层优化模型，通过上层引导、下层贴近
的交互式求解方式有效降低了变量维度，提高了计
算速度，适用于城市高压配电网负荷转供问题的在
线分析。
3）在双层优化策略确定后，采用模糊综合评价
方法评估网络从初态到终态不同过渡方案下系统的
安全水平，并分析不同权重取值对系统安全水平的
影响，为调度员优化倒闸操作顺序提供定量判据，有
效提高系统安全水平。
本文尚未考虑分布式能源消纳、充电负荷支撑
下的高压配电网安全保障目标，还需进一步研究连
续时间内高压配电网运行拓扑的自适应调整策略及
其快速求解算法。未来研究应重点探讨计及快速工
况变化下，关口无功倒送、短路电流越限等复杂约
束，形成更全面的高压配电网弹性运行理论和方法。
参考文献：
Sarma N D R,Rao K S P.A new 0–1 integer programming
method of feeder reconfiguration for loss minimization in
distribution systems[J].Electric Power Systems Research,
1995,33(2):125–131.
[1]
Yin Xiaogen,He Junjia,Bai Zhaodong.Reconfiguration of
distribution network based on reliability analysis[J].
Huazhong University of Science & Technology(Nature Sci-
ence Edition),2003,31(1):86–88.[尹小根,何俊佳,白照东.考
虑供电可靠性的配电网络重构[J].华中科技大学学报(自
[2]
 
表 3　开关动作组
Tab.3　 Transferring action group for switches
 
组编号
开关状态
断开
闭合
①
U4–U5
U3–U4
②
U8–U9
U9–U10
③
U16–U17
U17–U18
④
U26–S2
U25–U26
 
 
表 4　3种权重动作序列
Tab.4　 Sequence for 3 action weights
 
方案
ω5
ω6
ω7
动作序列
方案1
0.5
0.25
0.25
④①③②
方案2
0.25
0.5
0.25
②①③④
方案3
0.25
0.25
0.5
②④①③
 
 
20
40
60
80
100
᳔໻㒓䏃䋳䕑⥛/%
ᮍḜ
(b) ω6>ω5ǃω7 ϟ3⾡ᮍḜⱘ᳔໻㒓䏃䋳䕑⥛↨䕗 
20
40
60
80
100
᳔໻বय़఼䋳䕑⥛/%
ᮍḜ
(c) ω7>ω5ǃω6 ϟ3⾡ᮍḜⱘ᳔໻বय़఼䋳䕑⥛↨䕗 
0.2
0.4
0.6
0.8
1.0
ᮍḜ1
ᮍḜ2
ᮍḜ3
ᮍḜ1
ᮍḜ2
ᮍḜ3
ᮍḜ1
ᮍḜ2
ᮍḜ3
᳔Ԣ⬉य़ᷛᑎؐ
ᮍḜ
(a) ω5>ω6ǃω7 ϟ3⾡ᮍḜⱘ᳔Ԣ㡖⚍⬉य़↨䕗 
图 15　3种权重动作序列的指标对比
Fig.15　Comparison of three action weights
 
第 3 期
金　勇，等：基于功能单元的高压配电网负荷转供分层优化模型
189



<!-- page 12/12 -->

然科学版),2003,31(1):86–88.]
Tapia-Juárez R,Espinosa-Juárez E.Multi-objective reconfig-
uration of radial distribution networks considering voltage
sags[C]//Proceedings of the 2013 IEEE International Au-
tumn Meeting on Power,Electronics and Computing (RO-
PEC).Piscataway:IEEE,2013:1–6.
[3]
Gupta N,Swarnkar A,Niazi K R.A modified branch-ex-
change heuristic algorithm for large-scale distribution net-
works reconfiguration[C]//Proceedings of the 2012 IEEE
Power and Energy Society General Meeting.Piscataway:
IEEE,2012:1–7.
[4]
Sun Jian,Jiang Daozhuo.A new multi-objective algorithm
for distribution network reconfiguration[J].Automation of
Electric Power Systems,2003,27(20):57–61.[孙健,江道
灼.一种多目标配电网络重构新算法[J].电力系统自动
化,2003,27(20):57–61.]
[5]
Zhang Bingda,Liu Yang.A distribution network reconfigur-
ation algorithm based on evolutionary programming muta-
tion operator[J].Power System Technology,2012,36(4):
202–206.[张炳达,刘洋.应用进化规划变异算子的配电网
重构算法[J].电网技术,2012,36(4):202–206.]
[6]
Li Peng,Jiang Hui,Sun Qian,et al.Distribution network re-
configuration based on group search optimizer[J].Power
System Technology,2010,34(12):114–118.[李鹏,江辉,孙
芊,等.基于群搜索优化算法的配电网重构[J].电网技
术,2010,34(12):114–118.]
[7]
Huang Wei,Ji Shuangquan.A distribution network reconfig-
uration method via rapid network loss reduction based on
dual feeders[J].Automation of Electric Power Systems,
2015,39(5):75–80.[黄伟,纪双全.基于馈线偶的配电网快
速减小网损重构方法[J].电力系统自动化,2015,39(5):
75–80.]
[8]
Wang Chun,Cheng Haozhong.Reconfiguration of distribu-
tion network based on plant growth simulation algorithm[J].
Proceedings of the CSEE,2007,27(19):50–55.[王淳,程浩
忠.基于模拟植物生长算法的配电网重构[J].中国电机工
[9]
程学报,2007,27(19):50–55.]
Lu Lin,Luo Qi,Liu Junyong,et al.A hierarchical structure
poly-particle swarm optimization algorithm[J].Journal of
Sichuan University(Engineering Science Edition),2008,
40(5):171–176.[吕林,罗绮,刘俊勇,等.一种基于多种群分
层的粒子群优化算法[J].四川大学学报(工程科学版),2008,
40(5):171–176.]
[10]
Li Zhenkun,Chen Xingying,Yu Kun,et al.Hybrid particle
swarm optimization for distribution network reconfigura-
tion[J].Proceedings of the CSEE,2008,28(31):35–41.[李振
坤,陈星莺,余昆,等.配电网重构的混合粒子群算法[J].中
国电机工程学报,2008,28(31):35–41.]
[11]
Li Chuanjian,Liu Qianjin.A distribution network reconfigur-
ation algorithm based on Multi-agent system and minimum
spanning tree led by particle swarm optimization[J].Power
System Protection and Control,2011,39(6):24–28.[李传
健,刘前进.基于Multi-agent和粒子群引导最小生成树的配
电网重构算法[J].电力系统保护与控制,2011,39(6):24–
28.]
[12]
Cárcamo-Gallardo A,García-Santander L,Pezoa J E.Greedy
reconfiguration algorithms for medium-voltage distribution
networks[J].IEEE Transactions on Power Delivery,2009,
24(1):328–337.
[13]
Li Zhenkun,Chen Xingying,Yu Kun,et al.A hybrid particle
swarm optimization approach for distribution network re-
configuration problem[C]//Proceedings of the 2008 IEEE
Power and Energy Society General Meeting-Conversion
and Delivery of Electrical Energy in the 21st Century.Pis-
cataway:IEEE,2008:1–7.
[14]
Wang Chun,Cheng Haozhong.Reconfiguration of distribu-
tion network based on plant growth simulation algorithm[J].
Proceedings of the CSEE,2007,27(19):50–55.[王淳,程浩
忠.基于模拟植物生长算法的配电网重构[J].中国电机工
程学报,2007,27(19):50–55.]
[15]
（编辑　赵　婧）
 
引用格式:Jin Yong,Liu Junyong,Zhang Xi,et al. Bi-level model based on functional units for optimizing high-level voltage
distribution network[J].Advanced Engineering Sciences,2017,49(3):179–190.[金勇，刘俊勇，张曦，等.基于功能单元的高压
配电网负荷转供分层优化模型[J].工程科学与技术,2017,49(3):179–190.]
190
工程科学与技术
第 49 卷
