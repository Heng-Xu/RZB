<!--
source: D3_运行特征/CN_CSEE_2026_robust_voltage_control.pdf
sha256: fd6d8305630adb13c235092b08725d805b960e3c12f6fc732c1746b6db3c9d7a
method: pymupdf
pages: 11
-->

<!-- page 1/11 -->

第 48 卷  第 1 期
2026 年 1 月
Vol. 48 No. 1
Jan. 2026
高比例分布式光伏接入下配电网电压有功-无功
鲁棒控制
Active-reactive power robust control for distribution network voltage under high-proportion 
distributed photovoltaic integration
龙宇，刘晓峰
*，刘怀，刘国宝，李峰，于子翔
LONG Yu，LIU Xiaofeng
*，LIU Huai，LIU Guobao，LI Feng，YU Zixiang
（南京师范大学 电气与自动化工程学院，南京 210023）
（School of Electrical and Automation Engineering，Nanjing Normal University，Nanjing 210023，China）
摘 要：随着配电网大规模接入分布式光伏，配电网电压波动及越限问题日益突出，且传统的单一电压控制方法难
以实现快速动态电压控制。为此，针对高渗透率分布式光伏接入下的配电网，提出一种分布式电源变流器及静止
无功补偿器协同作用下的鲁棒控制策略。搭建分布式电源和静止无功补偿器的电压控制模型。在分布式电源和
静止无功补偿器的控制模型基础上，引入电压灵敏度矩阵构建配电网-电压控制模型。通过将有功和无功电压控
制相配合，充分利用系统的有功调压能力，实现快速动态电压控制。在此基础上考虑配电网运行过程中带来的系
统参数不确定性并结合鲁棒H∞（系统传递函数的无穷范数）性能约束，设计鲁棒控制策略。基于IEEE 33节点系统，
搭建光伏出力波动及负荷突变场景进行算例分析，结果表明，所提策略实现了快速稳定的电压控制，能够有效抑制
外部扰动引起的电压波动，验证了所提策略协同控制的快速性和有效性。
关键词：高渗透率光伏；电压控制；鲁棒控制；有功-无功协同；统一控制模型
中图分类号：TK 01：TM 73   文献标志码：A   文章编号：2097-0706（2026）01 - 0067 - 11
Abstract：With the large-scale integration of distributed photovoltaic （PV） systems into distribution networks， voltage 
fluctuations and out-of-limit issues have become increasingly prominent， and traditional single voltage control methods 
struggle to achieve rapid dynamic voltage control. Therefore， for distribution networks with high-penetration distributed PV 
integration， a robust control strategy based on the coordinated operation of distributed power source converters and static 
var compensators was proposed. Voltage control models for distributed power sources and static var compensators were 
established. Based on the control models of distributed power sources and static var compensators， a voltage sensitivity 
matrix was introduced to construct a unified voltage control model for the distribution network. By coordinating active and 
reactive voltage control， the active voltage regulation capability of the system was fully utilized to achieve rapid dynamic 
voltage control. Considering the system parameter uncertainties arising during distribution network operation， a robust 
control strategy was designed incorporating robust H∞ performance constraints. Based on the IEEE 33-node system， case 
studies were conducted under scenarios of PV output fluctuations and sudden load changes. The results showed that the 
proposed strategy achieved rapid and stable voltage control and effectively suppressed voltage fluctuations caused by 
external disturbances， verifying the rapid response and effectiveness of the proposed control strategy.
Keywords：high-penetration photovoltaic； voltage control； robust control； active-reactive power synergy； unified control model
0 引言 
随着新能源渗透率的不断提高，光伏发电的出
力不确定性给电网稳定运行带来新的挑战。其固
有的间歇性和波动性易导致配电网电压波动，甚至
引发电压越限的问题，对电网电能质量和供电可靠
性构成严重影响
［1-2］。特别是在高渗透率场景下，传
统基于有载调压变压器和电容器组的电压调节方
法难以适应快速动态响应的要求
［3-4］。因此，研究适
应高比例光伏接入的配电网快速动态电压控制策
略，对保障配电网安全稳定运行具有重要意义。
目前，国内外学者在电压调节领域开展了广泛
DOI：10. 3969/j. issn. 2097-0706. 2026. 01. 007
基金项目：江苏省自然科学基金项目（BK20230384）
Natural Science Foundation of Jiangsu Province（BK20230384）
© Editorial Department of Integrated Intelligent Energy. This is an open access article under the CC BY-NC-ND license.



<!-- page 2/11 -->

第 48 卷 
研究。现有研究主要聚焦于配电网无功调压，通过
优化系统的无功出力来抑制电压波动
［5-6］。此方法
通过对分布式电源逆变器进行相角调节或直接改
变无功补偿设备的无功出力以实现电压稳定，是当
前最主流的方法。文献［7］提出一种结合无功功率
和带宽参数自适应调节的自抗扰策略，可抑制不同
故障引起的过电压。文献［8］提出基于模型预测的
多时间尺度优化调度方法，可有效降低系统网损及
节点电压偏差。文献［9］提出了一种光伏逆变器电
压控制策略，能够针对系统运行状态进行自适应无
功优化，在面对功率波动不确定性和模型参数不准
确性控制时具有优异的控制效果。尽管调节无功
功率是传统配电网电压控制的主要手段，但其在实
际运行中仍存在一定的局限性，尤其在高渗透率光
伏接入的配电网中，若系统过度依赖无功调压，可
能导致逆变器持续运行在功率因数极限值，加速设
备老化，影响其运行寿命。此外，系统中大量的无
功功率流入会显著增加线路电流，导致网络损耗上
升，降低系统运行的经济性。更为关键的是，传统
的无功优化算法受到计算周期或无功补偿装置机
械开关动作速度的限制，在响应速度方面存在一定
局限性，难以适应快速动态调压要求。
由于无功调压存在上述这些不足，所以近年来
有功调压作为补充手段也受到广泛关注。此方法
通过分布式光伏主动削减有功出力，以及使用储能
进行有功吸收，实现功率消纳，为配电网提供稳定
的电压支撑
［10-11］。特别是在线路电阻较大的末端网
络，电压特性呈现出新的规律，其末端线路的电阻
分量往往不可忽略，甚至可能接近或超过电抗分
量，此时有功功率对电压幅值的影响变得尤为显
著。任何有功潮流的改变，如分布式电源出力调整
或负荷投切，均能够产生明显的电压调节效果。文
献［12］提出了考虑负荷特性的光伏消纳方案，通过
建立一套综合的数据聚类方法，增强随机方案在模
拟中的真实性。文献［13］通过建立基于三层自适
应学习的光伏有功可调节能力评估模型，降低了通
信成本的同时提高了模型训练性能。文献［14］提
出了一种多设备结合的配电网有功-无功耦合电压
调节优化策略，相较于传统调压策略，有效降低了
系统运行成本和电压偏差。然而，分布式光伏发电
很大程度受到气候因素的影响。当天气忽然转晴
导致光伏出力突增时，由于系统中接入的储能容量
限制，无法完全进行有功功率消纳，这将会导致配
电网电压升高。此时系统不得不弃光，削减光伏有
功出力，造成发电收益损失。由于多设备结合的配
电网有功-无功耦合电压调节优化策略缺乏经济
性，故难以大规模持续应用。
单一的有功或无功调压策略存在上述缺陷，构建
基于有功-无功功率协同优势的控制策略，不仅能够
克服无功调压容量受限、有功调压经济性不足等问题，
还可以充分利用有功-无功协同调压的快速性与灵活
性，实现更精准、高效的动态电压控制。特别是在高
比例分布式光伏接入的场景下，采用有功-无功协同
调压，能在最大程度保证系统电压稳定的同时兼顾经
济性。为改善高比例光伏接入配电网的电能质量，国
内外学者已提出多种控制方法
［15-16］。文献［17］将储能
与分布式电源及无功调控设备协调优化，在兼顾系统
运行经济性与提升电能质量的同时，促进了光伏消
纳。文献［18］提出一种分布式优化控制策略，能够确
定电压控制器的最佳配置，该策略所需网络带宽更小，
响应时间更短。文献［19］以配电网区域无功控制现
状为切入点，建立了区域无功群控系统架构，实现了
新能源发电协同参与配电网无功优化控制。上述研
究主要从优化角度考虑配电网电压调节策略，但其调
节周期通常在分钟甚至小时级，难以满足高比例光伏
接入环境下对电压快速动态调节的需求。尤其在光
伏出力剧烈波动或负荷突变等场景下，这类基于优化
算法的电压控制策略存在明显的时效性不足问题。
针对上述研究的不足，本文聚焦于高比例光伏
接入下的配电网线路末端网络。该场景下线路电
阻较大，有功功率变化对电压影响显著，电压越限
问题尤为突出。为此，本文提出一种基于有功-无
功协同控制的配电网电压快速鲁棒控制策略，并在
现有电压控制模型基础上
［20-25］，通过设计鲁棒自适
应控制器实现电压快速稳定控制。考虑到静止无
功补偿器（Static Var Compensator，SVC）具有调节速
度快、可连续调节的特点，能够平滑快速地调节无
功出力，本文将SVC 作为无功调压的重要手段之
一。为充分利用有功、无功调压优势，所提策略采
用有功-无功协同调压方式，并针对系统中不同元
件建立统一的电压控制模型，进而基于此模型设计
状态反馈实时控制器，以保证系统在各种运行场景
下的稳定性与更快速的动态响应。首先，基于分布
式电源与SVC 的等效并网模型建立其电压控制模
型；其次，引入配电网电压灵敏度矩阵，构建系统有
功-无功协同电压控制模型；最后，结合鲁棒H∞性能
指标，设计系统整体鲁棒电压控制策略，并通过算
例仿真分析验证所提控制方法的有效性。
1 配电网统一电压控制 
本文旨在提出一种配电网电压鲁棒控制的有
效策略，特别关注高渗透率分布式光伏接入后对电
·
·68
© Editorial Department of Integrated Intelligent Energy. This is an open access article under the CC BY-NC-ND license.



<!-- page 3/11 -->

第 1 期
龙宇，等：高比例分布式光伏接入下配电网电压有功-无功鲁棒控制
压的影响。通过建立光伏、储能及SVC 的电压控制
模型，得到配电网整体统一控制模型。在此基础上
进行鲁棒控制设计，通过求解矩阵不等式得到系统
的鲁棒控制律，从而使配电网能够在系统出现外部
扰动时进行自适应调整以维持电压稳定。其中，构
建配电网统一电压控制模型是实现本文所提策略
的理论基石，其根本目的在于将系统中各类具有不
同电压调节特性的元件整合在一个统一的框架之
下，从而实现设备之间的协同控制和统一调度。然
而，系统在实际运行过程中存在一定的不确定性。
为抑制此类不确定性对系统运行的影响，引入鲁棒
控制理论进行分析，并设计鲁棒控制器以保证系统
的安全稳定运行。
1. 1　分布式电源电压控制模型　
分布式电源并网逆变器在配电网电压调节过程
中主要通过下垂控制策略参与。该策略依靠发电机
外特性，分别建立逆变器有功功率-频率和无功功率-
电压模型，实现逆变器输出频率和电压的自主调节。
分布式电源的下垂控制基本原理架构如图1所示（图
中：ωref
DG为分布式电源的频率参考值；U ref
DG为分布式电
源的输出电压参考值；Pref
DG，Qref
DG分别为分布式电源的有
功、无功功率参考值；PDG，QDG分别为分布式电源的有
功、无功功率输出值；kdrc，P，kdrc，Q分别为有功、无功下垂
系数（无量纲），分别表征有功功率偏差对频率的调节
灵敏度和无功功率偏差对电压的调节灵敏度，系数越
大，功率变化引起的频率/电压变化越显著；UDG为分布
式电源逆变器的输出电压；Lf，Cf分别为电容-电感（LC）
滤波环节的滤波电感、滤波电容；UPCC为公共连接点
（PCC）的电压，是分布式电源与电网连接点的电压；Lline，
Rline分别为并网线路的电感、电阻；iline为并网线路的电
流；Ug为电网的系统电压）。
根据图1所示的原理，忽略系统频率控制环节，
其无功-电压关系可通过线性关系描述。基于下垂
控制的分布式电源逆变器小信号模型如下
UDG = kdrc，Q(Qref
DG - QDG) + U ref
DG。
（1）
对式（1）引入并网电压反馈控制系数kDG，U，则电
压控制方程为
UDG = kdrc，Q[ kDG，U(
)
U ref
PCC - UPCC /s +
]
(
)
Qref
DG - QDG
+ U ref
DG，
（2）
式中：s为拉普拉斯算子；kDG，U为电压反馈控制系统
系数。
分布式电源并网逆变器经过滤波和并网线路
阻抗后接入配电网，其等效并网电路如图2所示。
由图2 可推出分布式电源等效并网方程，其线
路电压与电流的关系如下
ì
í
î
ï
ï
ï
ï
ïïï
ï
ï
UPCC，d = UDG + Rlineid + (
)
Lline + Lf (
)
did
dt - ωiq
UPCC，q = Rlineiq + (
)
Lline + Lf (
)
diq
dt + ωid
，
（3）
式中：UPCC，d，UPCC，q分别为并网电压在d，q轴上的分量；
id，iq分别为并网电流在d，q轴上的分量；ω为角速度；
t为时间。
根据式（3）可以看出，由于并网点电压与逆变
器输出电压之间存在非线性耦合，故将它们之间的
关系式进行简化后得到下式
UPCC，d = UDG + f (idq)，
（4）
式中：f ( )
idq 为并网电流d，q 轴分量的函数，用于表
示并网电流对并网电压的扰动作用。
为便于控制器的设计，假设式（4）中并网电压d
轴分量UPCC，d等于并网电压幅值UPCC，即UPCC=UPCC，d。
当分布式电源逆变器的输出电压参考值与并网点
电压参考值相等，即U ref
DG = U ref
PCC 时，将式（2）代入式
（4），并对其做重新整理，可得到如下分布式电源无
功-电压控制模型
ì
í
î
ïïï
ïïï
U̇
DG，Δ = ḟ ( )
idq - kdrc，QkDG，UUDG，Δ - kdrc，QQ̇
DG，Δ
UDG，Δ = U ref
DG - UPCC，d                                             
QDG，Δ = Qref
DG - QDG                                                
，（5）
式中：U̇
DG，Δ 为分布式电源电压偏差的变化率；ḟ ( )
idq
为并网电流的扰动变化率；UDG，Δ 为分布式电源接入
点的电压偏差；Q̇
DG，Δ 为分布式电源无功功率偏差的
变化率；QDG，Δ为分布式电源的无功功率偏差。
 ᐳ
ᔿ+
$
,#%#)8
ᒦ54D
+ 
DD
᧗ 
+ +#
 )᧗ 
л ᧗ 
drc,Q
k
ġ$'
REF
5$'
KDRC 0
REF
0$'
0$'
1$'
ILINE
,LINE
50##
5$'
,F
#F
5G
2LINE
 
 
 
 
REF
1$'
REF
图1　下垂控制等效并网模型
Fig. 1　Droop control equivalent grid-connected model
 ᐳ
ᔿ+
$
,#%#)8
ᒦ54D
ILINE
,LINE
50##
5$'
,F
#F
5G
2LINE
图2　分布式电源等效并网模型
Fig. 2　Distributed generation equivalent grid-connected model
·
·69
© Editorial Department of Integrated Intelligent Energy. This is an open access article under the CC BY-NC-ND license.



<!-- page 4/11 -->

第 48 卷 
1. 2　SVC电压控制模型　
在配电网中SVC是一种关键的柔性交流输电系
统设备，主要用于动态无功补偿和电压稳定控制。SVC
通过快速调节容性或感性无功功率（如晶闸管控制电
抗器（TCR）与晶闸管投切电容器（TSC）组合），对配电
网的无功功率进行实时补偿以维持系统电压稳定。
典型的SVC并网控制结构如图3所示。
图3 中SVC 控制结构不具有下垂特性，无法直
接对电压进行控制。在配电网调压过程中，由电网
给定的调压比例系数与系统功率和线路参数相关。
因此，通过无功功率及线路阻抗特性推导其电压控
制模型。建立的SVC 等效并网模型如图4 所示（图
中：Ui，Uj分别为逆变器i 和并网点j 的电压幅值；φi，
φj分别为SVC输出端的电压相位角和PCC电压相位
角；Iij为SVC到PCC的线路电流；Lij，Rij分别为SVC与
PCC之间的线路等效电感、电阻）。
由图4对SVC的无功-电压控制模型进行推导，
根据其等效并网模型，得到其输出到并网点的无功
功率QSVC为
QSVC = UiUj
Zij
sin(θij - φij) - Uj
2
Zij
sin θij，
（6）
式中：φij分别为逆变器i和并网点j的电压幅值、电压
相位差；Zij，θij分别为逆变器i与并网点j间的线路阻
抗、阻抗相角。
对式（6）进行小信号建模，其表达式为
ΔQSVC = ∂QSVC
∂φi
Δφi + ∂QSVC
∂Ui
ΔUi =
  SQφΔφi + SQUΔUi，
（7）
式中：ΔQSVC为SVC 注入电网无功功率变化量；SQφ，
SQU为耦合系数；ΔUi，Δφi分别为逆变器i 输出电压、
电压相位角变化量。
若不考虑相位角变化对系统的作用，则无功功
率变化量ΔQSVC与电压变化量ΔUi成正比。
综合以上对分布式电源电压控制模型的分析，
建立相似的SVC无功-电压控制模型如下
ì
í
î
ï
ï
ï
ï
ï
ï
U̇
SVC，Δ = ḟ ( )
idq -
1
SQU
kSVC，UUSVC，Δ -
1
SQU
Q̇
SVC，Δ
USVC，Δ = U ref
SVC - UPCC，d                                            
QSVC，Δ = Qref
SVC - QSVC                                               
，
（8）
式中：U̇
SVC，Δ 为SVC 并网点电压偏差的变化率；kSVC，U
为SVC 的电压反馈控制系数；USVC，Δ 为SVC 并网点
的电压偏差；U ref
SVC 为SVC 的电压参考值；Qref
SVC 为SVC
的无功功率参考值；Q̇
SVC，Δ为SVC无功功率偏差的变
化率；QSVC，Δ为SVC无功功率偏差。
1. 3　统一电压控制模型　
将系统中分布式电源和SVC 逆变器用一个统
一的模型来表示，其表达式如下
ì
í
î
ïïï
ïïï
U̇
n，Δ = anUn，Δ + bnun + cn
cn = ḟ (idq )                            
un = ΔQ̇
n                              
，
（9）
式中：n 为第n 个控制模型，n∈S，S 为SVC 和新能源
逆变器控制模型的集合；an，bn分别为1. 1 和1. 2 节
建立的电压控制模型中的不同系数；cn为设定扰动
量；U̇
n，Δ 为设备的电压偏差变化率；un为设定输入
量；ΔQ̇
n为设备的无功功率偏差变化率。
考虑有功功率对节点电压的影响，并结合上述对
无功电压控制模型的分析，可得有功-电压关系如下
U̇
n，Δ = anUn，Δ + kn，PΔṖ
n + cn，
（10）
式中：kn，P为有功控制系数；ΔṖ
n为有功输入量。
上述式（9）—（10）建立的电压控制模型中，各
节点仅考虑了自身接入的控制设备对其电压调节
作用，即各节点电压仅受本节点流入的有功、无功
功率的控制。然而，配电网实际运行中各节点电压
还会受到来自其他节点的作用，当一个节点的功率
发生变化时，其他节点电压也会有所变化。因此，
为建立统一电压控制模型，应综合考虑各节点控制
设备进行电压调节时对其他节点电压的影响，通过
引入电压灵敏度矩阵来量化各节点间的相互作用。
在配电网潮流计算中，一般直接通过对雅可比矩阵
J求逆，计算电压灵敏度矩阵，其计算过程如下
ì
í
î
ï
ï
ïïï
ï
ï
ï
ï
ï
ïïï
ï
ï
ï
é
ë
êêê
ù
û
úúú
ΔP
ΔQ = é
ë
êêê
ù
û
úúú
H
N
K
L
é
ë
êêê
ù
û
úúú
Δθ
ΔV = J é
ë
êêê
ù
û
úúú
Δθ
ΔV
é
ë
êêê
ù
û
úúú
Δθ
ΔV =
é
ë
ê
ê
ê
êê
ê
ê
ê
ù
û
ú
ú
ú
úú
ú
ú
ú
-
L
HL - KN
N
HL - KN
K
HL - KN
-
H
HL - KN
é
ë
êêê
ù
û
úúú
ΔP
ΔQ
，（11）
ᒦ5+ 
B8
 G ݳ
G+5
а!ח+ 
Ҽ!ח+ 
+ #G
@  
   
43#ᣅ њᮠ
4#2@ @ĉ
᧗  ݳ
43#
4#2
50##
50##
REF

图3　SVC并网控制结构
Fig. 3　SVC grid-connected control structure
36#
0##
,IJ
5IϤĞI
5JϤĞJ
2IJ
IIJ
图4　SVC等效并网模型
Fig. 4　SVC equivalent grid-connected model
·
·70
© Editorial Department of Integrated Intelligent Energy. This is an open access article under the CC BY-NC-ND license.



<!-- page 5/11 -->

第 1 期
龙宇，等：高比例分布式光伏接入下配电网电压有功-无功鲁棒控制
式中：ΔP，ΔQ分别为各节点有功、无功功率变化量向
量；Δθ，ΔV分别为各节点电压相角、电压幅值变化量
向量；H，N，K，L为潮流计算的雅可比系数矩阵。
根据式（11）可知，各节点电压受自身及其他节
点有功、无功功率的影响。因此，得到考虑各节点
间相互作用的第n个控制模型的电压表达式如下
Un = Un0 + ∑
m = 1
S
K UP
nm ΔPm + ∑
m = 1
S
K UQ
nm ΔQm，（12）
式中：Un，Un0分别为第n 个控制模型输出电压、稳态
电压；K UP
nm，K UQ
nm 分别为电压灵敏度矩阵内的参数，分
别表示节点m 注入单位有功、无功功率时，引起节
点n 电压的变化量；ΔPm，ΔQm 分别为节点m 注入电
网的有功功率变化量和无功功率变化量。
综合以上分析，可知配电网中接入的控制设备
除了能根据其电压调节特性来控制本节点电压外，
还能通过电压灵敏度矩阵作用于其他节点，因此，
可以建立一个包含所有控制节点的控制模型对其
进行分析。结合式（9），
（10），
（12）得到n 个控制模
型的配电网整体电压控制模型如下
ì
í
î
ï
ï
ï
ï
ï
ï
ïïï
ï
ï
ï
ï
ï
ï
ï
ï
ï
ï
ï
ïïï
ï
ï
ï
ï
ï
ï
ï
ẋ ( )t = Ax( )t + Bu( )t + Dw( )t                         
A =
é
ë
ê
ê
ê
ê
ê
ê
ê
ê
êêê
ê
ê
ê
ê
ê
ê
ê
ù
û
ú
ú
ú
ú
ú
ú
ú
ú
úúú
ú
ú
ú
ú
ú
ú
ú
a1
K UQ
12
K UQ
22
a2
⋯
K UQ
1n
K UQ
nn
an
K UQ
21
K UQ
11
a1
a2
⋯
K UQ
2n
K UQ
nn
an
⋮
⋮
⋱
⋮
K UQ
n1
K UQ
11
a1
K UQ
n2
K UQ
22
a2
⋯
an
               
x( )t = ΔU = [
]
ΔU1
ΔU2
⋯
ΔUn
T         
w( )t = [
]
f (
)
ΔP1
f (
)
ΔP2
⋯
f (
)
ΔPn
T
，
（13）
式中：ẋ ( )t 为配电网系统状态变量变化率；x（t）为配电
网系统状态变量；w（t）为系统扰动量；D为单位矩阵；
A为系统的参数矩阵；B，u（t）分别为配电网系统控制
变量和系统的参数矩阵，其中
B =
é
ë
ê
ê
ê
ê
ê
ê
ê
ê
êêê
ê
ê
ê
ê
ê
ê
ê
b1
K UQ
12
K UQ
22
b2
⋯
K UQ
1n
K UQ
nn
bn
K UQ
21
K UQ
11
b1
b2
⋯
K UQ
2n
K UQ
nn
bn
⋮
⋮
⋱
⋮
K UQ
n1
K UQ
11
b1
K UQ
n2
K UQ
22
b2
⋯
bn
ù
û
ú
ú
ú
ú
ú
ú
ú
ú
úúú
ú
ú
ú
ú
ú
ú
ú
bn + 1
K UP
12
K UP
22
bn + 2
⋯
K UP
1n
K UP
nn
b2n
K UP
21
K UP
11
bn + 1
bn + 2
⋯
K UP
2n
K UP
nn
b2n
⋮
⋮
⋱
⋮
K UP
n1
K UP
11
bn + 1
K UP
n2
K UP
22
bn + 2
⋯
b2n
，
u( )t = [
]
ΔQ̇
1
ΔQ̇
2
⋯
ΔQ̇
n
ΔṖ
1
ΔṖ
2
⋯
ΔṖ
n
T
。
2 配电网有功-无功鲁棒控制策略 
2. 1　有功-无功鲁棒控制模型　
配电网系统实际运行过程中存在诸多不确定
因素，如光伏、风电出力的随机性、用电负荷时变性
及线路参数变动等。这些不确定因素使雅可比矩
阵内部元素产生不确定波动，进而使系统电压灵敏
度矩阵呈现不确定变化特性。上述不确定因素将
直接影响引入了电压灵敏度矩阵的式（13）配电网
整体电压控制模型，具体表现为矩阵A，B 参数呈现
随时间变化的特性。针对系统参数的不确定变化，
根据式（11）对电压灵敏度的分析，可确定其运行时
参数变化范围。构建的含不确定性的系统状态空
间模型为
ì
í
î
ẋ = (
)
A + ΔA x + (
)
B + ΔB u + Dw
z = Cx
，（14）
式中：ẋ 为系统的状态向量x 对时间的导数；ΔA，ΔB
为系统不确定因素对矩阵A，B 影响的系数矩阵；z
为系统输出；C为系数矩阵。
综合上述分析，考虑将系统中表示不确定因素的
系数矩阵ΔA，ΔB分解为已知常数矩阵和未知但有界
的扰动矩阵2部分，以此描述系统中存在的各种不确
定性。不确定性变化对系数矩阵ΔA，ΔB的影响可表
示为
[ ΔA
ΔB ] = MF (t) [ E1
E2 ]，
（15）
式中：M为反映不确定性参数结构的常数矩阵；F（t）
为不确定矩阵，且F
T（t）F（t）≤I，I 为单位矩阵；E1，E2
为参数扰动对系数矩阵A，B的影响。
针对推导出的不确定性系统式（14），设计满足
闭环系统性能稳定的状态反馈控制律
u(t) = Kx(t)，
（16）
式中：K为增益矩阵。
考虑存在性能指标γ使得其对于有界外部扰动
为w，系统满足的鲁棒性约束如下




C[
]
sI - (
)
Α + BK
-1D
∞< γ。
（17）
为将系统节点电压控制在一定范围内，所
设计的控制器在运行时，通过计算出配电网实
际电压和系统参考电压U
ref 之间的偏差，将其作
为系统状态变量x；并通过求解得到状态反馈
控制律，随后计算得到控制变量u；最后对其进
·
·71
© Editorial Department of Integrated Intelligent Energy. This is an open access article under the CC BY-NC-ND license.



<!-- page 6/11 -->

第 48 卷 
行积分得到系统实际输入无功功率参考偏差
ΔQ
ref 和有功功率参考偏差ΔP
ref，实现系统的鲁
棒控制。
2. 2　控制策略稳定性分析　
为设计出符合性能指标的控制律u（t）=Kx（t），
故式（14）系统鲁棒控制模型为
ì
í
î
ï
ïïï
ẋ = Aˉx + Dw
z = Cx
Aˉ = A + BK + MF (t)(E1 + E2K )
。
（18）
针对性能指标γ>0，根据鲁棒控制理论，若存在
对称矩阵P，满足式（19）矩阵不等式约束条件，则能
保证上述控制系统实现稳定。
é
ë
êêê
ù
û
úúú
AˉTP + PAˉ + CTC
PD
DTP
-γ2I < 0。
（19）
上述不等式为非线性矩阵不等式，无法直接求
解，且其中包含时变不确定参数矩阵F（t），因此，考
虑消去时变不确定参数矩阵F（t）转换为线性矩阵
不等式进行求解。对式（19）分别左乘和右乘矩阵
diag（P
−1，I），并记X=P
−1可得
é
ë
êêê
ù
û
úúú
XAˉT + AˉX + γ-2DDT
XCT
CX
-I
< 0。
（20）
将Aˉ=A+BK+MF（t）（E1+E2K）代入式（20）可得
é
ë
êêêX (
)
A + BK
T + (
)
A + BK X + γ-2DDT
CX
ù
û
úúú
      XCT
-I
+
é
ë
êêê
ù
û
úúú
M
0 [
]
F(
)
E1 + E2K X
0 +                                   
 é
ë
ê
ê
ê
ù
û
ú
ú
ú
X(
)
E1 + E2K
T
0
[
]
F TM T
0 < 0。                  （21）
对于适当维度的实矩阵M，E 和实对称矩阵Y，
若对所有满足F
T（t）F（t）≤I的实矩阵F，存在常数ε>
0使得式（22）成立，则式（23）成立。
Y + εMM T + ε-1ETE < 0，
（22）
Y + MFE + ETF TM T < 0。
（23）
结合上式（21）和式（22）可得
é
ë
êêê
ù
û
úúú
εX (
)
A + BK
T + (
)
A + BK εX + εγ-2DDT
εXCT
εCX
-εI
+
é
ë
ê
ê
ê
ù
û
ú
ú
ú
MM T + εX(
)
E1 + E2K
T(
)
E1 + E2K εX
0
0
0
< 0。（24）
记V=εX，W=KV，并应用Schur 补引理即可得到
式（25）线性矩阵不等式。因此，针对给定的性能指
标γ>0，若存在对称正定实矩阵V 及适当维数的实
矩阵W，满足式（25）矩阵不等式约束条件，则能保证
上述电压鲁棒控制系统实现稳定，其鲁棒控制器可
通过式（26）表示。
é
ë
ê
êêê
ê
ù
û
ú
úúú
ú
AV + VAT + BW + W TBT + εγ-2I + MM T
CV
E1V + E2W
VCT
VE T
1 + W TE T
2
-εI
0
0
-I
< 0，
（25）
u(t) = Kx(t) = WV -1x(t)。
（26）
对于性能指标γ，若取值过大会导致系统对扰
动的抑制能力减弱，无法实现快速响应；若取值过
小，则会过度追求抗扰动性能，影响系统稳定
性。在设计过程中，通常采用迭代方法，寻找
使线性矩阵不等式有可行解的最小γ 值，该最
小值对应着最优的鲁棒性能。
3 算例分析 
3. 1　仿真参数　
上述式（25）线性矩阵不等式是一个标准的凸
优化问题，可通过数值计算工具进行求解，本文采
用Matlab的LMI工具箱进行求解。在控制器设计过
程中，性能指标γ 代表系统对外部扰动抑制能力的
强弱，为兼顾系统动态性能与鲁棒稳定性，经综合
权衡本文取性能指标γ=10。在Matlab 环境中构建
标准参数下的IEEE 33 节点系统进行仿真测试，以
评估所提有功-无功协同控制的配电网电压控制策
略的有效性。考虑实际工程场景，设置分布式电源
和SVC 的数量及分布节点，其网络结构如图5所示。
在IEEE 33 节点系统中，于18 节点接入1 个SVC、25
节点接入1 个分布式储能系统、4 节点接入1 个风力
发电系统、2，7，11，14，16，21，27，31节点接入5组光
伏发电系统。各分布式电源稳态时的输出功率
见表1。
设置分布式电源无功功率输出范围为［0，Qmax，DG］，
其中，Qmax，DG为分布式电源在功率因素限制下无功功
率输出的最大值。
3. 2　算例分析　
为全面评估所提控制策略的鲁棒性能，考虑通










       


 
  
       
36#
图5　IEEE 33节点配电网仿真拓扑图
Fig. 5　Simulation topology of IEEE 33-node 
distribution network
·
·72
© Editorial Department of Integrated Intelligent Energy. This is an open access article under the CC BY-NC-ND license.



<!-- page 7/11 -->

第 1 期
龙宇，等：高比例分布式光伏接入下配电网电压有功-无功鲁棒控制
过2种不同场景进行仿真。为了在可控条件下验证
所提策略的有效性，避免通信延迟对控制器响应速
度的评估产生影响，仿真基于理想通信假设。关于
非理想通信环境下的协同控制可参考基于有限通
信的电压控制方案
［26］，及关于通信时延方面的研
究
［27-28］。为系统性验证所提策略的有效性，本算例
考虑了配电网2 种典型运行工况，即光伏出力随时
间变化和负荷突变的过程。
为模拟光伏发电功率的动态变化过程，根据实
际情况设置0 —10 s 期间光伏出力保持不变；随后
在10 s 时模拟云层消散，光伏出力达到峰值；在35 s
时模拟云层遮挡，光伏出力迅速下降。天气变化对
分布式光伏出力的影响如图6所示。
在光伏出力变化且未引入鲁棒控制策略的情
况下，部分接入SVC 和分布式电源的节点电压变化
如图7 所示。仿真结果表明，光伏出力的动态变化
会引发显著的电压波动。其中，最高节点电压出现
在节点16，其电压标幺值最高升至1. 047；最低电压
在节点27，其电压标幺值最低至0. 989。这种电压
大幅波动的现象严重影响了配电网的电能质量和
供电可靠性。
针对上述问题，引入无功电压控制，得到系统
部分节点的电压情况如图8 所示。结果表明，光伏
出力突增引起各节点电压升高，此时分布式电源逆
变器和SVC 通过吸收无功的方式防止电压越限，但
单一无功控制调节效果有限，节点16 在12 s 时电压
标幺值出现较大峰值，超过1. 040。
在此基础上引入所提有功-无功协同控制策
略，通过协同各分布式电源与SVC 调整有功、无功
功率进行电压控制，得到节点电压情况如图9 所
示。仿真结果表明，所提策略能对电压波动进行快
速响应，且引入有功-无功协同控制策略后，相较
单一无功控制，其抑制各节点电压波动的效果更显
著。在光伏出力动态变化引起电压大幅波动的情
况下，系统仍可有效抑制电压波动，并迅速将节点
电压标幺值动态维持在0. 98~1. 02 的安全运行范
围内。且对于电压峰值有很好的抑制效果，节点
16 电压峰值有明显的下降，验证了所提策略的可
行性。
表1　各分布式电源稳态功率参数
Table 1　Steady-state power parameters for each distributed 
power supply
kW
接入节点编号
2
4
7
11
14
16
18
21
25
27
31
有功输出
200
400
380
300
210
280
0
320
350
300
260
无功输出
17
50
75
100
100
100
100
25
50
75
50
8&ݹԿ 
8&ݹԿ 
8&ݹԿ 
8&ݹԿ 
8&ݹԿ 
8&ݹԿ 
8&ݹԿ 
8&ݹԿ






ᰦLS







ݹԿ  K7
图6　天气变化对分布式光伏出力影响
Fig. 6　Impact of weather changes on distributed 
PV power output
8& 
8& 
8& 
8& 
8&
8& 






ᰦLS








8&+  ḷᒪ٬ 
图7　分布式光伏出力波动对节点电压影响
Fig. 7　Impact of distributed PV output fluctuations on 
node voltage










8&+  ḷᒪ٬ 
8& 
8& 
8& 
8& 
8&
8& 
ᰦLS
图8　单一无功控制下光伏出力波动对节点电压影响
Fig. 8　Impact of PV output fluctuations on node voltage under 
single reactive power control
·
·73
© Editorial Department of Integrated Intelligent Energy. This is an open access article under the CC BY-NC-ND license.



<!-- page 8/11 -->

第 48 卷 
调压过程中各节点接入设备的无功出力变化
如图10 所示。在10 s 时由于无功出力增大，系统中
分布式电源逆变器和SVC 均按照控制器设定吸收
一部分无功出力将电压降低至稳定区间；在35 s 时
增大无功出力来稳定电压。
搭建模拟光伏出力随时间变化及负荷突变同
时发生的场景，从而评估所提鲁棒控制策略在复杂
场景下的动态性能。将负荷突变放入已有的光伏
出力变化场景中，并设置其在20 s 时模拟负荷的瞬
时切除，继而在30 s时模拟负荷重新接入，各节点具
体负荷变化见表2。当系统中未加入所提鲁棒控制
策略时，部分节点电压变化如图11 所示。可以看
出，当系统同时存在光伏出力增大及负荷切除的情
况时，系统节点电压出现明显升高，存在比较严重
的末端电压越限问题，会影响到系统的安全稳定
运行。
在上述场景中引入无功（Q）电压控制得到的节
点电压变化如图12所示。结果表明，在光伏出力动
态变化及负荷突变同时发生的复杂场景下，系统能
够将节点电压标幺值维持在0. 98~1. 02的安全运行
范围内。接着在系统中加入有功（P）协同控制，得
到节点电压情况如图13所示。其中，调压过程中各
节点接入设备的无功出力变化如图14 所示。对比
图11中未加入鲁棒控制的情况，本文所提策略在光
伏出力波动且存在负荷投切的情况下，也能将节点
电压标幺值稳定维持在0. 98~1. 02，调压性能
良好。






ᰦLS






8& 
8& 
8& 
8& 
8&
8& 
8&+  ḷᒪ٬ 
图9　PQ协同控制下光伏出力波动对节点电压影响
Fig. 9　Impact of PV output fluctuations on node voltage under 
PQ synergy control






ᰦLS
 
 
 




ᰐ   K7
8& 
8& 
8& 
8& 
8&
8& 
图10　光伏出力波动对节点无功出力影响
Fig. 10　Impact of PV output fluctuations on node reactive power 
output






ᰦLS





8&+  ḷᒪ٬ 
8& 
8& 
8& 
8& 
8&
8& 
图11　负荷波动对节点电压影响
Fig. 11　Impact of load fluctuations on node voltage
表2　节点负荷变化
Table 2　Node load variations
负荷节点编号
8
12
18
24
28
切除时间/s
20
20
20
20
20
投入时间/s
30
30
30
30
30
负荷/（kV·A）
110+j50
15+j10
40+j15
400+j100
30+j5






ᰦLS




8&+  ḷᒪ٬ 
8& 
8& 
8& 
8& 
8&
8& 
图12　单一无功控制下负荷波动对节点电压影响
Fig. 12　Impact of load fluctuations on node voltage under single 
reactive power control
8& 
8& 
8& 
8& 
8&
8& 






ᰦLS






8&+  ḷᒪ٬ 
图13　PQ协同控制下负荷波动对节点电压影响
Fig. 13　Impact of load fluctuations on node voltage under PQ 
synergy control
·
·74
© Editorial Department of Integrated Intelligent Energy. This is an open access article under the CC BY-NC-ND license.



<!-- page 9/11 -->

第 1 期
龙宇，等：高比例分布式光伏接入下配电网电压有功-无功鲁棒控制
4 结束语 
本文针对高渗透率光伏接入导致的配电网电
压波动与越限问题，提出了一种基于统一电压控制
模型的有功-无功鲁棒自适应协同控制策略。通过
建立分布式电源、储能、SVC 的统一电压控制模型，
所提方法依据H∞性能指标进行鲁棒控制设计。仿
真结果表明，所提方法能在光伏出力波动和负荷变
化的情况下，通过协调有功-无功出力保证了配电
网电压处于安全区间内。
参考文献：
［1］廖家齐， 于若英， 刘瑜俊， 等. 基于自适应高斯混合模型
的含高渗透率分布式光伏电力系统风险评估［J］. 电力系
统保护与控制， 2024， 52（19）： 144-156.
LIAO Jiaqi， YU Ruoying， LIU Yujun， et al. Risk 
assessment of a power system with a high penetration of 
distributed photovoltaic based on self-adaptive Gaussian 
mixture model［J］. Power System Protection and Control， 
2024， 52（19）： 144-156.
［2］徐式蕴， 杨瑾瑜， 彭龙. 高渗透率光伏馈入受端电网暂
态电压稳定量化评估［J］. 电力系统自动化， 2025， 49
（9）： 125-134.
XU Shi Yun， YANG Jinyu， PENG Long. Quantitative 
evaluation of transient voltage stability for receiving-end grid 
with high penetration of photovoltaic［J］. Automation of 
Electric Power Systems， 2025， 49（9）： 125-134.
［3］贾雅君， 李涛， 席东民， 等. “交-直-储” 无通信协同的
农村低压配电网电压越限治理策略［J］. 电力系统自动
化， 2025， 49（13）： 195-207.
JIA Yajun， LI Tao， XI Dongmin， et al. Voltage limit 
violation mitigation strategy for rural low-voltage distribution 
network based on communicationless "AC-DC-energy 
storage" coordination［J］. Automation of Electric Power 
Systems， 2025， 49（13）： 195-207.
［4］欧杰宇， 张逸， 陈云飞， 等. 考虑多元设备调控特性的电能
质量分散式协同调控策略［J/OL］. 电网技术， 1-17 （2025-
03-13）［2025-05-13］. https：//doi.org/10.13335/j.1000-3673.
pst.2024.2225.
OU Yujie， ZHANG Yi， CHEN Yunfei， et al. Decentralized 
collaborative power quality control strategy considering the 
regulation characteristics of multivariate devices［J/OL］. Power 
grid technology， 1-17 （2025-03-13）［2025-05-13］．https：//
doi.org/10.13335/j.1000-3673.pst.2024.2225.
［5］王林， 孔小民， 周忠玉， 等. 云储能模式下的配电网分布
式光伏-储能无功优化方法［J］. 综合智慧能源， 2024， 46
（6）： 44-53.
WANG Lin， KONG Xiaomin， ZHOU Zhongyu， et al. 
Distributed photovoltaic-energy storage reactive power 
optimization method for distribution networks under cloud 
energy storage mode［J］. Integrated Intelligent Energy， 2024， 
46（6）： 44-53.
［6］葛磊蛟， 崔庆雪， 李昌禄， 等. 计及时延的智能配电网光
储就地-分布电压优化控制方法［J］. 电力系统保护与控
制， 2025， 53（4）： 48-58.
GE Leijiao， CUI Qingxue， LI Changlu， et al. Local-
distributed 
voltage 
optimization 
control 
method 
for 
photovoltaics and energy storage in a smart distribution 
network considering time delay［J］. Power System Protection 
and Control， 2025， 53（4）： 48-58.
［7］孟建辉， 袁新成， 吴鹏， 等. 结合无功自适应调节和改进
LADRC策略抑制HPFC全过程过电压控制方法［J/OL］. 电
工技术学报， 1-15 （2025-04-08）［2025-05-13］.https：//doi.
org/10.19595/j.cnki.1000-6753.tces.242279.
MENG Jianhui， YUAN Xincheng WU Peng， et al. Integrated 
control method for suppressing whole-process overvoltage in 
HPFC systems combining reactive power adaptive regulation 
with improved LADRC strategy［J/OL］. Transactions of China 
Electrotechnical Society， 1-15 （2025-04-08）［2025-05-13］.
https：//doi.org/10.19595/j.cnki.1000-6753.tces.242279.
［8］罗政杰， 任惠， 辛国雨， 等. 基于模型预测控制的高比例
可再生能源电力系统多时间尺度动态可靠优化调度［J］. 
太阳能学报， 2024， 45（6）： 150-160.
LUO Zhengjie， REN Hui， XIN Guoyu， et al. Multi-time 
scale dynamic reliable optimal scheduling of power system 
with high propottion renewable energy based on model 
predictive control［J］. Acta Energiae Solaris Sinica， 2024， 
45（6）： 150-160.
［9］杨浩， 王佳怡， 易文飞， 等. 知识-数据融合驱动的配电
网光伏逆变器电压/无功优化自适应控制［J］. 中国电机
工程学报， 2025， 45（22）： 8691-8706.
YANG Hao， WANG Jiayi， YI Wenfei， et al. Hybrid 
knowledge-data driven adaptive voltage/var optimization 
control of photovoltaic inverters in distribution networks［J］. 
Proceedings of the CSEE， 2025， 45（22）： 8691-8706.
［10］陈继开， 张嘉扬， 李浩茹， 等. 风电场静止同步调相机
有功功率-频率支撑能力分析与优化［J］. 电力系统自动
8& 
8& 
8& 
8& 
8&
8& 






ᰦLS
 
 
 




ᰐ   K7
图14　负荷波动对节点无功出力影响
Fig. 14　Impact of load fluctuations on node reactive power output
·
·75
© Editorial Department of Integrated Intelligent Energy. This is an open access article under the CC BY-NC-ND license.



<!-- page 10/11 -->

第 48 卷 
化， 2025， 49（22）： 68-78.
CHEN Jikai， ZHANG Jiayang， LI Haoru， et al. Analysis 
and optimization of active power and frequency support 
capability for static self-synchronous compensator in wind 
farm［J］. Automation of Electric Power Systems， 2025， 49
（22）： 68-78.
［11］胡泽春， 蔡福霖， 冯建洲. 兼顾新能源消纳与频率电压
支撑的电池储能系统优化规划［J］. 电力自动化设备， 
2024， 44（7）： 3-12.
HU Zechun， CAI Fulin， FENG Jianzhou. Optimal 
planning of battery energy storage system considering 
renewable energy consumption and frequency and voltage 
support［J］. Electric Power Automation Equipment， 2024， 
44（7）： 3-12.
［12］孙万通， 陈众， 陈慧霞， 等. 考虑负荷特性的光伏消纳能
力的模拟与评估［J］. 太阳能学报， 2024， 45（4）： 475-481.
SUN Wantong， CHEN Zhong， CHEN Huixia， et al. 
Simulation and evaluation of photovoitaic absorption capacity 
considering load characterristics［J］. Acta Energiae Solaris 
Sinica， 2024， 45（4）： 475-481.
［13］安芸帙， 崔明建， 韩一宁， 等. 基于数据隐私保护自适
应联邦学习的分布式光伏有功可调节能力评估方法
［J］. 中国电机工程学报， 2025， 45（21）： 8281-8294.
AN Yunzhi， CUI Mingjian， HAN Yining， et al. A distributed 
PV active power adjustability evaluation method based on self-
adaptive 
privacy-preserving 
federated 
learning ［J］. 
Proceedings of the CSEE， 2025， 45（21）： 8281-8294.
［14］付利达， 贾清泉， 孙玲玲， 等. 构网/跟网型光伏逆变器
混联的配电网有功无功双层调压策略［J］. 电力系统自
动化， 2025， 49（12）： 171-183.
FU Lida， JIA Qingquan， SUN Lingling， et al. Bi-level 
voltage regulation strategy for active and reactive power of 
distribution 
network 
with 
hybrid 
grid-forming/grid-
following photovoltaic inverters［J］. Automation of Electric 
Power Systems， 2025， 49（12）： 171-183.
［15］林泓宏， 余涛， 张桂源， 等. 基于数据驱动的高比例新
能源配电网无功优化算法［J］. 综合智慧能源， 2023， 45
（11）： 10-19.
LIN Honghong， YU Tao， ZHANG Guiyuan， et al. Data-
driven reactive power optimization algorithm for the 
distribution network with high proportion of renewable energy
［J］. Integrated Intelligent Energy， 2023， 45（11）： 10-19.
［16］郑虎虎， 叶剑华， 罗凤章. 主动配电网-交通网耦合系统
分布鲁棒规划方法［J］. 太阳能学报， 2025， 46（4）： 200-209.
ZHENG 
Huhu， 
YE 
Jianhua， 
LUO 
Fengzhang. 
Distributionally robust planning method for active distribution 
power-traffic network coupling systems［J］. Acta Energiae 
Solaris Sinica， 2025， 46（4）： 200-209.
［17］方石磊， 杨志淳， 闵怀东， 等. 高比例光伏下考虑移动
储能接入的柔性配电网协调优化策略［J］. 供用电， 
2025， 42（5）： 61-71.
FANG Shilei， YANG Zhichun， MIN Huaidong， et al. 
Coordinated optimization strategy of flexible distribution 
network considering mobile energy storage system integration 
under high proportion photovoltaic［J］. Distribution & 
Utilization， 2025， 42（5）： 61-71.
［18］VACCARO A， VELOTTO G， ZOBAA A F. A decentralized 
and cooperative architecture for optimal voltage regulation in 
smart grids［J］. IEEE Transactions on Industrial Electronics， 
2011， 58（10）： 4593-4602.
［19］李可雨， 王峰， 蔡德胜， 等. 新能源发电协同参与配电
网无功优化控制技术［J］. 供用电， 2023， 40（4）： 15-22.
LI Keyu， WANG Feng， CAI Desheng， et al. Optimized 
reactive power control technology in distribution network 
considering 
new 
energy 
resource 
aggregation ［J］. 
Distribution & Utilization， 2023， 40（4）： 15-22.
［20］冯昌森， 李邗邺， 汤飞霞， 等. 考虑配电系统拓扑变化
的电压控制深度强化学习方法［J］. 电力自动化设备， 
2025， 45（8）： 156-163.
FENG Changsen， LI Hanye， TANG Feixia， et al. Deep 
reinforcement learning method for voltage control considering 
topology change of distribution system［J］. Electric Power 
Automation Equipment， 2025， 45（8）： 156-163.
［21］靳先涛， 肖传亮， 彭克， 等. 基于分散复杂自适应体系
的配电网功率自平衡优化控制［J］. 电力系统自动化， 
2025， 49（12）： 101-109.
JIN Xiantao， XIAO Chuanliang， PENG Ke， et al. Optimal 
control of power self-balancing for distribution network 
based on decentralized complex adaptive system of systems
［J］. Automation of Electric Power Systems， 2025， 49
（12）： 101-109.
［22］张波， 张永康， 孙英钧， 等. 考虑光伏度电成本的配电
网数据-知识驱动优化调控策略［J］. 电力系统自动化， 
2025， 49（18）： 74-82.
ZHANG Bo， ZHANG Yongkang， SUN Yingjun， et al. 
Data-knowledge-driven optimal dispatch and control 
strategy for distribution network considering photovoltaic 
levelized cost of energy［J］. Automation of Electric Power 
Systems， 2025， 49（18）： 74-82.
［23］张从越， 窦晓波， 张章， 等. 基于变流器统一结构模型
的光伏高渗透配电网鲁棒自适应动态电压控制［J］. 中
国电机工程学报， 2020， 40（22）： 7306-7317.
ZHANG Congyue， DOU Xiaobo， ZHANG Zhang， et al. 
Robust adaptive dynamic voltage control for PV high-
penetration distribution network based on unified structure 
model of convertors［J］. Proceedings of the CSEE， 2020， 
40（22）： 7306-7317.
［24］曾瑶， 徐玉韬， 熊炜， 等. 计及DSTATCOM 和并网逆变
器协同的高比例分布式光伏配电网鲁棒控制策略［J］. 
广东电力， 2024， 37（6）： 1-10.
·
·76
© Editorial Department of Integrated Intelligent Energy. This is an open access article under the CC BY-NC-ND license.



<!-- page 11/11 -->

第 1 期
龙宇，等：高比例分布式光伏接入下配电网电压有功-无功鲁棒控制
ZENG Yao， XU Yutao， XIONG Wei， et al. Robust control 
strategy 
for 
high-proportion 
distributed 
photovoltaic 
distribution network considering coordination of DSTATCOM 
and grid-connected inverters［J］. Guangdong Electric Power， 
2024， 37（6）： 1-10.
［25］唐成虹， 董存， 戴睿鹏， 等. 基于模型预测控制的光伏
场站快速协同无功电压控制［J］. 电力系统保护与控制， 
2023， 51（17）： 80-90.
TANG Chenghong， DONG Cun， DAI Ruipeng， et al. Fast 
cooperative reactive voltage control for photovoltaic 
stations based on model predictive control［J］. Power 
System Protection and Control， 2023， 51（17）： 80-90.
［26］OLIVIER F， ARISTIDOU P， ERNST D， et al. Active 
management of low-voltage networks for mitigating 
overvoltages due to photovoltaic units［J］. IEEE Transactions 
on Smart Grid， 2016， 7（2）： 926-936.
［27］王力成， 杨宇， 杨晓东， 等. 考虑非完美通讯的高光伏
渗透率配电网实时电压协同控制［J］. 中国电机工程学
报， 2022， 42（11）： 4027-4039.
WANG Licheng， YANG Yu， YANG Xiaodong， et al. 
Real-time voltage cooperative control in distribution 
networks with high photovoltaic penetration considering 
imperfect communication［J］. Proceedings of the CSEE， 
2022， 42（11）： 4027-4039.
［28］朱卫卫， 朱清， 高文森， 等. 基于5G通信时延的配电网馈
线自动化切换方法［J］. 综合智慧能源， 2024， 46（5）： 1-11.
ZHU Weiwei， ZHU Qing， GAO Wensen， et al. Switching 
method for distribution network feeder automation system 
based on 5G communication delay ［J］. Integrated 
Intelligent Energy， 2024， 46（5）： 1-11.
（本文责编：周志恒） 
收稿日期：2025 - 08 - 18；修回日期：2025 - 10 - 10
上网日期：2026 - 01 - 19；附录网址：www.iienergy.cn
作者简介：
龙宇（2002），男，硕士生，从事配电网运行优化方面的研
究，241812139@njnu.edu.cn；
刘晓峰
*（1991），男，副教授，博士，从事需求侧管理和智
能配用电方面的研究，liuxiaofeng@njnu.edu.cn；
刘怀（1971），男，副教授，博士，从事综合能源系统优化
运行方面的研究，Liuhuai@njnu.edu.cn；
刘国宝（1993），男，副教授，博士，从事电力系统负荷频
率控制方面的研究，guobaoliu0709@njnu.edu.cn；
李峰（1992），男，讲师，博士，从事电力系统安全稳定分
析与控制方面的研究，lifeng_ee@nnu.edu.cn；
于子翔（2000），男，硕士生，从事电力市场动力学分析方
面的研究，13739116496@163.com。
*为通信作者。
·
·77
© Editorial Department of Integrated Intelligent Energy. This is an open access article under the CC BY-NC-ND license.
