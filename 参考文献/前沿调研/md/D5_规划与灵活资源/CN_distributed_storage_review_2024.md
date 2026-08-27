<!--
source: D5_规划与灵活资源/CN_distributed_storage_review_2024.pdf
sha256: 7ad080d3778f035461c0dbf6c60fe6b337c79488b1ddf31fcf1d79346d81015a
method: pymupdf
pages: 12
-->

<!-- page 1/12 -->

 
新型配电网分布式储能系统方案及配置研究综述
黄海泉
 1，黄晓巍
 1，姜望
 1，王媛媛
 1，王言方
 1，丁浩
 1，左杰文
 2，✉，夏晨阳
 2
（1. 国网江苏省电力有限公司盐城市大丰区供电分公司, 江苏 盐城 224000；
2. 中国矿业大学 电气学院, 江苏 徐州 221000）
摘要： [目的]随着“双碳”目标以及各地推出的新能源配置储能政策的推行，文章进一步明确分布式储能在新型配电
网中发挥的作用及储能系统配置方案。[方法]首先，总结归纳新型配电网分布式储能系统的配置需求，根据不同应
用需求分析了分布式光伏储能系统的结构；其次，为了实现配置储能经济最大化，结合各地配置储能政策要求，阐
明分布式储能系统的配置方法；最后，归纳分析了当前选址定容的常用算法，在此基础上给出研究建议。[结果]配
置储能需在明确需求的基础上，选择合适的拓扑结构，基于配网供电稳定性、安全性、经济性等指标综合优化给出配置方案。
[结论]分布式储能技术是新型配电网的关键技术，是解决配电网安全稳定运行的重要手段，需要进一步研究其优化
配置方案及相关调控技术，才能更好地发挥作用。
关键词： 分布式储能；光伏系统；新型配电网；储能配置；选址定容
中图分类号：TM7；TK11
文献标志码：A
文章编号：2095-8676(2024)04-0042-12
DOI： 10.16516/j.ceec.2024.4.05　　OA： https://www.energychina.press/
论文二维码
A Review of Distributed Energy Storage System Solutions and Configurations for
New Distribution Grids
HUANG Haiquan
1, HUANG Xiaowei
1, JIANG Wang
1, WANG Yuanyuan
1, WANG Yanfang
1, DING Hao
1, ZUO Jiewen
2, ✉,
XIA Chenyang
2
（1. State Grid Jiangsu Electric Power Co., Ltd. Yancheng Da feng District Power Supply Branch, Yancheng 224000, Jiangsu, China；
 2. School of Electrical Engineering, China University of Mining and Technology, Xuzhou 221000, Jiangsu, China）
Abstract: [Introduction] With the advancement of the "dual carbon" goals and the introduction of new energy allocation and storage
policies in various regions, there is a need to further clarify the role of distributed energy storage in the new types of distribution networks
and the configuration of associated energy storage system. [Method] This paper began by summarizing the configuration requirements of
the distributed energy storage systems for the new distribution networks, and further considered the structure of distributed photovoltaic
energy  storage  system  according  to  different  application  needs.  To  maximize  the  economic  aspect  of  configuring  energy  storage,  in
conjunction  with  the  policy  requirements  for  energy  allocation  and  storage  in  various  regions,  the  paper  clarified  the  methods  for
configuring distributed energy storage systems and summarized the commonly used algorithms for determining the location and capacity.
Based on this, research suggestions were proposed. [Result] Proper configuration of energy storage should be based on clear demands,
selecting the appropriate topology and offering a configuration plan that is optimized by comprehensively considering indicators such as
power  supply  stability,  security,  and  economic  efficiency  of  the  distribution  network.  [Conclusion] Distributed  energy  storage
technology  is  the  key  aspect  of  the  new  distribution  networks  and  an  essential  means  to  ensure  the  safe  and  stable  operation  of
distribution  networks.  To  harness  its  full  potential,  further  research  into  its  optimal  configuration  and  related  control  technologies  is
 
 
收稿日期：2023-01-07　 　修回日期：2023-04-04
基金项目：国家自然科学基金青年科学基金项目“四桥臂有源电力滤波器脉宽调制机理及电流预测控制研究”（51407184）
 
第 11 卷　第 4 期
南方能源建设
Vol. 11　No. 4
2024 年 7 月
SOUTHERN ENERGY CONSTRUCTION
Jul. 2024
引用格式：黄海泉，黄晓巍，姜望，等. 新型配电网分布式储能系统方案及配置研究综述[J]. 南方能源建设，2024，11（4）：42-53. HUANG Haiquan,
HUANG Xiaowei, JIANG Wang, et al. A review of distributed energy storage system solutions and configurations for new distribution grids [J]. Southern
energy construction, 2024, 11(4): 42-53. DOI： 10.16516/j.ceec.2024.4.05.



<!-- page 2/12 -->

necessary.
Key words: distributed energy storage; photovoltaic system; new distribution network; energy storage configuration; site selection and
capacity determination
2095-8676 © 2024 Energy China GEDI. Publishing services by Energy Observer Magazine Co., Ltd. on behalf of Energy China GEDI.
This is an open access article under the CC BY-NC license (https: //creativecommons.org/licenses/by-nc/4.0/).
 
  
0    引言
随着“碳达峰”“碳中和”国家政策的提出
[1]，一
场宏大的能源革命拉开了序幕，这注定了新能源产
业将会有高质量的改变与发展。为了实现2030 年
前“碳达峰”、2060 年前“碳中和”，储能作为实现这
一目标的关键技术，具有重大战略意义，且已经成为
当下研究的热点。
国家能源局的数据显示，在“双碳”目标的指引
下，高比例具有不确定性的可再生能源及负荷接入
新型配电网，可再生能源的渗透率不断提升，要求电
力系统加速转型。接入新型配电网的分布式资源出
力具有波动性和随机性，不能提供持续稳定的可控
功率，增加了新型配电网调度的困难。大量分布式
资源带来的配电网双向潮流、三相不平衡、谐波、电
压越限等电能质量问题需要解决
[2]，如何去消纳新型
配电网的分布式资源是大量学者研究的目标。配置
分布式储能是有效解决上述问题的措施之一，利用
分布式储能具有响应快、配置灵活、建设周期短等
优势，可以实现对配电网调峰调频和无功补偿，有助
于分布式资源就地消纳，实现对分布式资源的灵活
调控，改善新型配电网电能质量问题
[3]。2021 年发
布的《关于加快推动新型储能发展的指导意见》明确
提出：要围绕分布式新能源探索储能融合发展新场
景，鼓励利用不间断电源、电动汽车、用户侧储能等
分散式储能设施，推动新型储能与可再生能源协同
发展。储能技术的应用将对我国能源产业的重构转
变具有关键作用，其在电源侧、电网侧和用户侧的不
同场景应用，可确保新型配电网的安全稳定运行。
分布式储能系统的研究是建设分布式智能电网
的重要课题，明晰其相关技术的发展现状并进一步
探索其发展方向对于分布式储能的有效利用至关重
要。本文基于大规模分布式资源接入新型配电网的
场景，分析当前分布式储能系统拓扑结构的特点和
配置方案，探讨新型配电网分布式光伏配置储能的
难点和发展趋势。
  
1    分布式储能系统配置需求分析
新型配电网新能源配置储能成为必要趋势，大
量研究已经从理论及实践方面证实储能系统在配电、
用户侧的分布式应用的可行性。
  
1.1    储能配置的必要性
根据中国化学与物理电源行业协会储能应用分
会出品的《2022 储能产业应用研究报告》以及近6 a
储能行业报告，以电化学储能为例，如图1 所示。从
2017 年开始，装机容量越来越高，到2021 年，电化学
储能的规模已经达到5 117.1 MW，2022 年电化学储
能总装机规模更是增长迅速，累计总装机规模达到
11 GW。
 
 
装机容量/MW
12 000
10 000
8 000
6 000
4 000
2 000
0
2017
423.2 1 072.7 1 079.6
3 269.2
5 117.1
11 000
2018
2019
2020
t/年
2021
2022
图1　2017～2022 年电化学储能装机容量
Fig. 1　Installed capacity of electrochemical energy storage
in recent six years
 
在新型配电网中，分布式光伏的高比例接入给
新型配电网带来了沉重负担：（1）光伏发电的高峰期
和用电高峰期不一致，且导致新型配电网由单向潮
流变为双向潮流，引起潮流流动不确定并且增加了
网络损耗；（2）配电网电能光伏容量越来越大，局部
配电网将会出现电压偏差、三相不平衡度、电压波
动、频率偏差、电网谐波等电能质量超标的问题。
分布式储能系统有能力解决以上问题。在光伏
发电高峰期将多余的电能存储起来，用于用电高峰
期，从而缓解电网负荷压力，让分布式光伏能够成为
可调可控的电源；利用储能设备能够抑制谐波、改善
第 4 期
黄海泉，等：新型配电网分布式储能系统方案及配置研究综述
43



<!-- page 3/12 -->

电压、补偿无功，改善电能质量，防止电气设备受到
损坏
[4]。
  
1.2    面向需求的分布式储能系统功能分析
配置储能是新型配电网中必不可少的1 个环节，
配置储能系统需要充分发挥其功效最大限度满足多
方面需求。
  
1.2.1    削峰填谷
分布式光伏大规模接入配电网使得电网中高峰
负荷增加，电网负荷的峰谷差越发扩大，电网调峰压
力剧增。新型配电网中传统的调峰策略主要有建立
经济分时电价、传统机械储能以及扩大发电测装机
容量等方法
[5]。随着分布式电源接入容量增加，这类
办法已经不能满足新型配电网的需求，必须配合分
布式储能才能有效解决高峰负荷压力。新型配电网
分布式光伏配置储能对削峰填谷的效果如图2
所示。
 
 
注：1−储能系统放电；2−储能系统充电。
2
1
荷
负
力
电
6:00
12:00
18:00
24:00
2
t
图2　削峰填谷示意图
Fig. 2　Schematic diagram of peak cutting and valley filling
 
实现削峰填谷的优化调度，需要有合理的控制
策略。文献[6] 研究储能技术如何实现削峰填谷，为
目前储能政策提供研究基础。文献[7] 考虑到经济
性，将储能成本与治理效果结合作为调峰的综合评
价标准，给出了优化模型，以解决削峰填谷的出力优
化问题。人工智能优化算法也被大量运用在削峰填
谷的优化问题上。文献[8] 采用人工鱼群算法建立
了基于削峰填谷策略的经济优化调度模型。文
献[9] 将储能系统应用在能量调度，采用改进多目标
粒子优化算法进行寻优，实现削峰填谷，并且提高电
能质量。文献[10] 研究削峰填谷的经济性，给出不
同场景下配置储能容量及基于粒子群算法的优化策略。
为了保证新型配电网的运行稳定，同时获得更
大的经济效益，需要更加深入研究制定削峰填谷的
优化策略，充分发挥储能系统的性能优势。
  
1.2.2    调频
传统机组调频速度慢、时间长，各个国家都出现
由于高比例的新能源而导致重大的频率安全事故
[11]。
分布式储能系统具有响应速度快、双向调节的优势，
能够有效地对电网进行调频，达到高效精准的效果。
图3 为当前配电网储能系统配置示意图，储能
系统可以放在位置1 处联合光伏等新能源参与调频，
也可以单独设置在位置2 参与调频
[12]。目前主要以
辅助传统机组参与调频为主，将新能源与储能进行
结合调频也有示范应用，例如，中国华能蒙城风电
40 MW/40 WMh 储能项目。
 
 
储能
电池 1
Buck-
Boost
DC/AC
AC/DC
Buck-
Boost
储能
电池 2
DFIG
图3　储能系统接入位置示意图
Fig. 3　Schematic diagram of access position of energy
storage system
 
进一步探寻联合光伏等新能源共同参与调频是
储能系统研究的1 个关注方向。面对越来越复杂的
配电网络，现有的储能调频模型较难充分将新能源
与配电网融合。文献[13] 改进了万有引力搜索算法
的自适应下垂控制策略，使光伏调频性能更加优越，
文献[14] 改进一次调频下垂控制方法。文献[15] 研
究锂电池储能电站一次调频的集成设计，通过试验
优化平滑频率波动。以上文献研究一次调频的各种
策略，随着新型配电网的发展，调频的方法趋向于与
新型能源联合调频。文献[16] 指出目前联合新能源
储能调频存在的问题，对未来研究方向给出建议。
文献[17] 提出风电、储能、电动汽车联合调频控制
策略，通过实验储能系统能够弥补风电场参与系统
调频造成频率二次跌落不足，验证该策略的有效性。
  
1.2.3    分布式能源消纳
选取配电网某日的等效净负荷运行曲线，如图4
所示。当分布式光伏的出力大于新型配电网中负荷
功率时，会出现功率的倒送，该现象一般发生在一天
中负荷处在低谷的时候
[18]。合理配置分布式储能系
统不仅能够解决这一问题，还能利用倒送功率在新
44
南方能源建设
第 11 卷



<!-- page 4/12 -->

型配电网负荷功率较大时释放，使配电网安全且经
济运行。
 
2 000
1 000
功率/kV
0
−1 000
−2 000
0:00
4:00
8:00
12:00
t
16:00 20:00 24:00
配电台区负荷曲线
弃光区
图4　分布式能源消纳示意图
Fig. 4　Schematic diagram of distributed energy consumption
 
合理配置分布式储能系统容量是解决分布式能
源消纳的关键问题。文献[19] 结合江西新能源接入
背景，分析分布式储能如何解决当地分布式资源消
纳，根据配置方案，给出2025 年新能源消纳的计算
结果，总结分布式储能对新能源消纳提升能力。文
献[20] 指出提升配电网对新能源的消纳比例需要将
新能源与分布式储能系统容量协调配置，这是解决
新能源消纳的大趋势。文献[21] 依据式（1）配置和
调度储能资源。
PDES = PPV −Pref
（1）
式中：
PDES ——分布式储能需求功率（kW）；
PPV  ——分布式光伏出力（kW）；
Pref  ——参考功率（kW）。
但式（1）仅从参考功率考虑分布式储能的调度。
在配置分布式储能时，一方面要保证容量满足需求，
另一方面需要充分考虑其经济性。
更多的学者更多考虑经济性，基于分布式储能
的技术特征，采取不同控制策略配置储能。文献[22]
兼顾经济性和风电消纳效果最优，建立储能系统容
量优化配置模型，制定容量配置方案。文献[23] 以
电网净收益为目标，实现经济最大化，建立了分布式
光伏储能系统优化配置模型，既能解决分布式光伏
消纳的问题，又能使电网收益提高。文献[24] 利用
功率谱密度（PSD）分析风电出力特征，研究储能系
统频率控制方法，提高电网抗干扰能力，促进消纳，
减少经济损失。
  
1.2.4    提升电网安全运行稳定性
分布式能源高比例接入，配电网中电压频率等
指标出现波动，这严重影响了电网的安全，大量学者
提出必须配置储能以达到稳定配电网电压、提高电
能质量的目的。
文献[25] 优化储能控制部分的PI 参数效应，提
出参数优化控制策略，有效地抑制电压波动。文献[26]
构建了配电网电压的一致性算法流程，并通过改进
的多目标锥模型实现储能协同电压控制。更多的学
者通过确定优化函数目标，采取智能算法寻优，实现
平抑电压波动的目的。文献[27] 研究了储能系统对
电能质量的影响，兼顾稳定电压和经济性，提出分布
式储能系统优化配置策略。文献[28] 使分布式光伏
与储能协调控制，以电压波动为目标函数，通过粒子
群寻优证实了提出的控制策略有效性。文献[29] 研
究由光伏与复合储能构成的复合拓扑下的双层优化
策略，建立了电压波动抑止模型，采用改进量子粒子
群算法实现优化。文献[30] 选择电压偏差和网损最
小为目标函数，提出了新能源与储能的双层电压无
功协调控制策略。实现合理调度与分配资源，保证
了电网的安全。
新型配电网的安全稳定固然重要，未来还更应
该考虑分布式能源和储能系统如何协调控制实现经
济最大化，这是新型配电网面临的关键技术难题。
  
2    新型配电网分布式储能系统架构
为了满足以上功能需求，需要根据系统的架构，
比较目前常用的分布式储能拓扑，选择合适的分布
式储能设备。
  
2.1    分布式储能系统架构
综合以上分析，分布式储能系统是新型配电网
必不可少的组成部分，是新能源推广应用的保障。
依据能量转换形式
[31]，新型储能技术目前有物理储
能、电化学储能和电磁储能，如图5 所示。其中物理
储能结构主要优势体现在短时间内提供大量功率，
不间断的供电；电磁储能结构主要优势体现在响应
速度非常快，功率密度较高；应用较为广泛的电化学
储能结构主要优势体现在容量大、响应快。
依据新型配电网的应用场景，分布式储能系统
一方面可以配合分布式能源并入电网，另一方面又
能单独接入电网，改善负荷特性，架构如图6 所示。
其中分布式储能系统配合光伏并网，该架构主
要组成部分为光伏发电系统、储能系统以及并网部
第 4 期
黄海泉，等：新型配电网分布式储能系统方案及配置研究综述
45



<!-- page 5/12 -->

分。光伏发电系统是光伏电池板组通过升压变换器
接入直流母线；储能系统则是储能电池通过双向变
换器接入直流母线，双向逆变器实现了母线电压的
逆变，从而将光伏和储能接入配电网
[32]，具体拓扑如
图7 所示。
 
 
光伏
电池
储能
电池
DC/DC
DC/AC
电网
DC/DC
图7　分布式光伏储能系统并网架构
Fig. 7　Grid connection architecture of distributed photovoltaic
energy storage system
 
分布式光伏是由许多的光电组列板，从太阳光
处吸收大量的能源，再将太阳光转化成电量的系统。
分布式光伏电源的数学模型如式（2）所示。
I = Iph −Is
{
exp
[q(U + IRs)
AKT
]
−1
}
−U + IRs
Rsh
（2）
式中：
Iph  ——光电流（A）；
Is   ——二极管饱和电流（A）；
q   ——电荷值（1.6×10
-19 C）；
U  ——光伏电池输出电压（V）；
I    ——光伏电池输出电流（A）；
Rs  ——光伏电阻（Ω）；
A   ——二极管理想因子，数值一般取1~2；
K   ——玻尔兹曼系数（1.36×10
-23 J/K）；
T   ——绝对温度（K）；
Rsh ——二极管并联电阻（Ω）。
储能系统单独接入电网能缓解电源波动。分布
式储能系统主要是由两部分构成：电化学储能单元
和储能配套设备。其系统构成如图8 所示。
 
 
储能变流器
PCS
能量管理系统
EMS
电池管理系统
BMS
电池组
提供信息
提供信息
控制指令
控制指令
提供信息
提
供
信
息
控
制
指
令
放
电
充
电
图8　电化学储能系统构成
Fig. 8　Composition of electrochemical energy storage system
 
电化学储能系统的组成单元相对固定，主要是
电池组、储能变流器（Power Conversion System，PCS）、
能量管理系统（Energy Management System，EMS）和
电池管理系统（Battery Management System，BMS）组
成
[33]。BMS 是对电池充电以及放电进行管理，其作
用是让整个储能系统能够稳定运行，提供安全可靠
的保障。众多学者对BMS 进行研究，设计BMS 遵
循预防为主，控制保障的原则，BMS 对储能系统有
着系统调控的功能。PCS 作为电力变换器件，承担
电池组与电网间的能量转换。同时PCS 能够与
BMS 互相提供状态信息，达到控制电压等需求。储
能PCS 的核心是交直流可控转换技术，现有技术类
型分为低压拓扑和基于链式结构的高压拓扑，未来
主要优化路径有：提升单机功率；采用更合理的电路
 
新型储能技术
物理储能
电化学储能
电磁储能
飞轮储能
压缩空气储能
超级电容器
超导储能
超级电容器
超导储能
超级电容器
超导储能
图5　新型储能技术分类
Fig. 5　Classification of new energy storage technologies
 
~
10 kV
380 V
光伏
储能
储能
图6　分布式储能系统架构
Fig. 6　Architecture of distributed energy storage system
46
南方能源建设
第 11 卷



<!-- page 6/12 -->

拓扑结构；模块集成提高整体运作效率。EMS 通过
对PCS 和BMS 的数据采集和信息监控，对PCS 和
BMS 控制其运行，将信息汇总，全方位地掌控整套
系统的运行情况，并做出相关决策，保证储能系统安
全有效的进行。EMS 未来发展的重要方向是智能运
维，通过专业的运营维护及安全监控降低储能系统
的成本。
  
2.2    分布式储能拓扑结构研究
在分布式光伏系统中，DC/DC 电路是实现最大
功率跟踪的核心组成，一般以Buck DC/DC 作为其
转换电路
[34]。而对于储能系统的双向DC/DC 电路，
一般采用非隔离型，其原因是拓扑结构简单并且容
易控制，使整个PCS 的效率得到提升，特别适合用于
新能源配置储能系统。目前使用较多的为半桥式、
Sepic-Zeta、Cuk 以及Buck-boost，4 种变换器拓扑结
构如图9 所示，其特点总结如表1 所示，可根据应用
场地、效率需求等因素综合选择。
 
 
Vi
C1
Q1
Q2
L1
C2
Vo
(a) 半桥式变换器
Vi
C1
Q1
Q2
L1
C3
L2
C2
Vo
(b) Sepic-Zeta 变换器
Vi
C1 Q1
Q2
L1
C3
L2
C2
Vo
(c) Cuk 变换器
Vi
C1
Q1
Q2
L1
C2
Vo
(d) Buck-Boost 变换器
图9　基本DC/DC 变换器
Fig. 9　Basic DC/DC converter
 
在光伏储能系统中，双向AC/DC 逆变电路是另
一核心组成
[35]，常见的AC/DC 逆变电路拓扑分为单
相和三相，以单相拓扑结构为例，有双向半桥、双
Buck 式以及单相双向全桥等类型，如图10 所示。
3 种拓扑特点比较如表2 所示。
 
 
A
V
C1
Q1
Q2
Lac
C2
vac
B
(a) 双向半桥式
V
C1
Q1
Q2
Lac1
C2
vac
B
Lac2
A1
A2
D1
D2
(b) 双 Buck 型
V
C1
Q1
Q3
Lac1
vac
B
A
Q2
Q4
(c) 双向全桥式
图10　基本双向AC/DC 逆变电路拓扑
Fig. 10　Basic bidirectional AC/DC inverter circuit topology
 
 
 
表 2　常用双向AC/DC 变换器比较
Tab. 2　Comparison of common AC/DC converters
双向AC/DC变换器
特点
双向半桥式
结构简单，但可靠性较低
双Buck型
可靠性好，但功率密度较低
双向全桥式
结构简单，能够实现四象限运行
 
以上拓扑因其效率高、结构简单的特点得到广
泛使用，根据功率等级的不同选择变流器，不同的拓
扑结构决定了储能设备的生产成本和效率，所以研
发低成本高效率的变流器是研究的趋势和方向。
基于常用拓扑，为了寻求更高的效率，众多学者
 
表 1　常用DC/DC 变换器比较
Tab. 1　Comparison of common DC/DC converters
双向DC/DC变换器
特点
半桥式
实现电压升降，输出电压稳定
Sepic-Zeta
提供隔离，效率高、抗干扰能力强
Cuk
输出纹波小、电压调节范围大
Buck-Boost
提供隔离，体积小、成本低
第 4 期
黄海泉，等：新型配电网分布式储能系统方案及配置研究综述
47



<!-- page 7/12 -->

探讨了改进方案。文献[36-37] 研究储能现状，对储
能结构和控制进行分析改进，从而提升储能设备的
效率。文献[38] 研究新型的双向储能器，减少1 个
DC/DC 环节改进储能系统，增加变流器的可靠性，保
证高效率。文献[39] 研发出基于开关电容的新型多
电平逆变电路，将此技术引入到光伏逆变器中，能让
光伏逆变器电路拓扑灵活简单，输出特性更优，配合
储能系统实现高效率运行。文献[40] 提出了1 种高
效率的非隔离光伏并网逆变器拓扑，能实现无漏电
流光伏并网、软开关，高质量、高效率并网。文献[41]
分析储能系统的电路、拓扑，提出光储一体化变流器
控制策略，提高控制性能，保障高效率运行。
研究分布式储能系统架构，能够更好依据需求
选择合适的拓扑，提升并网友好度，也能保证配电网
的安全。但目前分布式光伏配置储能成本较高，还
应继续从改进设备方面研究如何降低成本。
  
3    分布式储能系统配置方法
为了进一步推动可再生能源高质量发展，在新
型配电网中，需根据功能和场景需求，探讨储能配套
的合理模式，除了选择合理系统架构外，应从多方面
考虑储能配置方案。
  
3.1    各地光伏配置储能要求
为推进新能源逐步渗透的配电网安全稳定运行，
我国各省份在国家政策的指导下纷纷制定了相应的
配置储能要求。大多数省份设定的配置储能要求不
低于装机容量的10%，有的省份要求较高，需要不低
于15%。统计各地的储能配置如表3 所示。
由表3 可以看出，大多数地区对储能配置的要
求都不低于10%，个别地区对储能配置要求较高。
各地区发布相关的政策指标为各项分布式光伏储能
工程项目提供标准。
  
3.2    分布式储能选址定容研究现状分析
全国各地相继出台储能最低配置政策，意味着
配备储能将会成为分布式电源规划的重要一环，其
中，储能如何选址定容才能实现最优目标规划。储
能容量和选址对配电网的影响很大，若容量太大，成
本太大，经济性低，则不能达到储能配合分布式电源
调控配电网的作用。因此，储能系统如何选址、定容
实现最优目标也是储能配置的关键问题之一。
目前，大多数研究以经济性指标作为储能选址
定容的目标函数，除此之外，网损最低、平抑波动、
削峰填谷等综合性指标也常作为选址定容的目标函
数。确定目标函数之后，给出相应的约束进行数学
建模。一般是以功率平衡、节点电压、电流、装机容
量等作为约束条件。分布式光伏配置储能进行选址
定容这一问题属于多目标、多约束、非线性规划的
 
表 3　各地储能配置政策
Tab. 3　Policies for energy storage allocation in different regions
时间
地区
政策
配储比例
配储时长/h
2021.01
青海
《支持储能产业发展的若干措施（试行）》
高于10%
2
2021.03
江西
《关于做好2021年新增光伏发电项自竞争优选有关工作的通知》
高于10%
1
2021.05
甘肃
关于“十四五”第一批风电、光伏发电项目开发建设有关事项的通知
高于10%
2
2021.06
湖北
关于2021年平价新能源项目开发建设有关事项的通知
高于10%
2
2021.07
宁夏
《关于加快促进自治区储能健康有序发展的通知（征求意见稿）》
高于10%
2
2021.08
安徽
关于2021年风电、光伏发电开发建设有关事项的通知（征求意见稿）
高于10%
2
2021.08
内蒙古
关于2021年风电、光伏发电开发建设有关事项的通知
高于15%
1
2021.09
义乌
《关于推力原网荷储协调发展和加快区域光伏产业发展的实施细则》
高于10%
2
2021.09
江苏
关于我省2021年光伏发电项目市场化并网有关事项的通知
高于10%
2
2021.10
广西
2021年市场化并网陆上风电、光伏发电多能互补一体化项目建设方案的通知
高于15%
3
2021.11
山东
关于公布2021年市场化并网项目名单的通知
高于10%
2
2022.01
上海
《上海市发展改革委关于公布金山海上风电场一期项目竞争配需工作方案的通知》
高于20%
2~4
2022.03
福建
关于组织开展2022年集中式光伏电站试点申报工作的通知
高于10%
4
2022.05
辽宁
《辽宁省2022年光伏发电示范项目建设方案》
高于15%
2
48
南方能源建设
第 11 卷



<!-- page 8/12 -->

问题
[42]，为了求解选址定容，大多数学者会采取适当
的智能优化算法，使整体寻优效果更好。选址定容
一般性流程思路如图11 所示。
 
 
开始
建立数学模型，选取
选址定容目标函数
采取合适的智能优化
算法求解
全局最优解为选址定
容最终结果
输出最优解
结束
图11　选址定容一般性流程
Fig. 11　General process of site selection and capacity
determination
 
众多学者使用不同的算法求解选址定容的难题，
如图12 所示。智能算法如今被广泛应用在选址定
容的问题中。文献[43] 采用NSGA 解决社区储能容
量配置的多目标非线性问题。文献[44] 提出基于精
英集的改进粒子群算法，以最小网损和电压波动为
目标的储能选址定容的优化方法。文献[45] 分析配
置储能的必要性，采用双层决策模型分别建立目标
函数，采用麻雀搜索算法进行寻优，配置储能容量。
文献[46] 改进了杂草入侵算法，优化改进建立储能
容量优化模型，并且采用粒子群算法和遍历算法对
光伏储能系统进行了协同配置优化。文献[47] 首先
建立多目标优化模型，考虑储能系统的成本，采用遗
传算法求解优化模型，最后在IEEE24 节点中仿真，
求解了不同光伏容量的储能最优配置。
 
建模优化算法
智能算法
强化学习
联合算法
Q 学习
SA+Q 学习
单目标
多目标
PSO
SA
GA
MOPSO
NSGAⅡ
BA
SA+PSO
COBL+PSO
图12　选址定容优化算法
Fig. 12　Optimization algorithm for location and capacity
determination
 
联合算法求解优化模型的方法也被学者采用。
文献[48] 考虑经济性，利用重心反向学习结合粒子
群算法求解建立的光伏储能选址定容的模型，最后
验证了模型的可行性。文献[49] 同样考虑成本经济
性，以投资运行成本作为目标，考虑储能接入位置等
约束条件建立双层优化模型，外层采用遗传算法，内
层采用粒子群算法优化储能配置容量。文献[50] 基
于改进的Q 学习提出联合调频策略并对储能容量进
行配置。
上述研究成果对储能选址定容的研究方法进行
分析，同时采用不同的算法进行优化改进，具体总结
如表4 所示。依据不同的应用需求，考虑设备条件，
选择不同的目标函数和求解算法，能够有效地实现
分布式储能选址定容。这些方法能够解决配电网中
储能的布局和容量配置的问题，加强了分布式光伏
的消纳以及能源利用。
 
 
表 4　选址定容典型方法
Tab. 4　Typical methods for site selection and capacity determination
文献编号
优化目标
约束条件
算法
44
最小网损，电压波动最小
光伏出力，线路长度，潮流约束
粒子群算法
45
储能系统总成本最低
充放电约束，功率成本约束
麻雀搜索算法
46
满足性能指标的弃光成本
功率供需平衡，功率波动
遍历算法
47
储能系统成本，网损最少
充放电约束，功率约束
遗传算法
48
经济性，环保性，可靠性
功率潮流、节点电压约束，电池约束
粒子群算法
50
投资成本，维护成本
机组调节能力，容量约束
Q学习
  
第 4 期
黄海泉，等：新型配电网分布式储能系统方案及配置研究综述
49



<!-- page 9/12 -->

4    结论
可再生能源呈现高比例、规模化接入配电网，为
了构建安全稳定的新型配电网，需要解决新能源消
纳问题。储能技术能够削峰填谷、调频、促进新能
源出力消纳以及改善电网电能质量，可在一定程度
上解决大规模新能源并网的问题，因此在配电网中
配置储能非常必要。
目前，储能技术处在发展阶段，针对如何更加经
济地发挥分布式储能作用并实现灵活调控目标的技
术需求，需要进一步开展以下研究工作：（1）充分挖
掘分布式储能电网安全稳定运行的调节能力，针对
多元化应用场景，以解决新能源消纳、电压越限、调
频等问题和经济运行为目标，研究配电网储能系统
的最优配置和调控；（2）研究和开发多功能分布式储
能系统优化控制策略，实现其高效运行；（3）针对单
一储能系统及未来的混合储能技术应用于配电网灵
活调控时，探讨配电网管理平台如何提供技术支撑。
为积极响应国家政策，应不断完善储能技术，合
理评估储能在配电网的功能和实现目标，通过多目
标优化方法配置和调控储能系统，实现新型配电网
的稳定安全运行。
参考文献： 
 LIU C Y, TAN X, LIU Y F. Building a new-type power system
to  promote  carbon  peaking  and  carbon  neutrality  in  the  power
industry  in  China 
[J].  Chinese  journal  of  urban  and
environmental  studies,  2022,  10（2）:  2250009.  DOI:  10.1142/
S2345748122500099.
[1]
 张兴, 李明, 郭梓暄, 等. 新能源并网逆变器控制策略研究综述
与展望  [J]. 全球能源互联网, 2021, 4（5）: 506-515. DOI: 10.
19705/j.cnki.issn2096-5125.2021.05.010.
ZHANG X, LI M, GUO Z X, et al. Review and perspectives on
control strategies for renewable energy grid-connected inverters
[J]. Journal of global energy interconnection, 2021, 4（5）: 506-
515. DOI: 10.19705/j.cnki.issn2096-5125.2021.05.010.
[2]
 WANG C Y, ZHANG L, ZHANG K, et al. Distributed energy
storage  planning  considering  reactive  power  output  of  energy
storage and photovoltaic [J]. Energy reports, 2022, 8（Suppl.10）:
562-569. DOI: 10.1016/J.EGYR.2022.05.155.
[3]
 杨海晶, 贾学翠, 高东学, 等. 分布式储能在电力系统的应用及
现状分析 [J]. 电器与能效管理技术, 2018（3）: 47-52. DOI: 10.
16628/j.cnki.2095-8188.2018.03.010.
YANG H J, JIA X C, GAO D X, et al. Application and present
situation analysis of distributed energy storage in power system
[J]. Electrical & energy management technology, 2018（3）: 47-
[4]
52. DOI: 10.16628/j.cnki.2095-8188.2018.03.010.
 张哲深. 含高比例光伏电力系统中光储联合系统的优化控
制 [D]. 吉林: 东北电力大学, 2021. DOI: 10.27008/d.cnki.gdbdc.
2021.000187.
ZHANG Z S. Optimal control of photovoltaic and energy storage
hybrid  system  in  high-proportion  photovoltaic  power  systems
[D].  Jilin:  Northeast  Electric  Power  University,  2021.  DOI:
10.27008/d.cnki.gdbdc.2021.000187.
[5]
 RANA M, ROMLIE M F, ABDULLAH M F, et al. A novel peak
load shaving algorithm for isolated microgrid using hybrid PV-
BESS system  [J]. Energy, 2021, 234: 121157. DOI: 10.1016/J.
ENERGY.2021.121157.
[6]
 潘宇航, 王青松, 陈力. 应用于电网侧削峰填谷的储能系统配
置及日出力优化策略 [J]. 供用电, 2022, 39（7）: 9-16. DOI: 10.
19421/j.cnki.1006-6357.2022.07.002.
PAN Y H, WANG Q S, CHEN L. Energy storage configuration
and scheduling optimization strategy applied to peak shaving and
valley filling on the grid side [J]. Distribution & utilization, 2022,
39（7）: 9-16. DOI: 10.19421/j.cnki.1006-6357.2022.07.002.
[7]
 何力. 考虑削峰填谷策略的微电网经济性优化调度研究 [C]//
浙江省电力学会. 浙江省电力学会2021 年度优秀论文集, 浙
江, 2022 年7 月. 北京: 中国电力出版社, 2022: 10. DOI: 10.269
14/c.cnkihy.2022.018164.
HE  L.  Study  on  economic  optimal  dispatch  of  microgrid
considering  peak  shaping  and  valley  filling  strategy  [C]//
Zhejiang Electric Power Society. Proceedings of 2021 Excellent
Papers of Zhejiang Electric Power Society, Zhejiang, July, 2022.
Beijing: China Electric Power Press, 2022: 10. DOI: 10.26914/
c.cnkihy.2022.018164.
[8]
 邵振, 邹晓松, 袁旭峰, 等. 基于改进多目标粒子群优化算法的
配电网削峰填谷优化  [J]. 科学技术与工程, 2020, 20（10）:
3984-3989. DOI: 10.3969/j.issn.1671-1815.2020.10.028.
SHAO Z, ZOU X S, YUAN X F, et al. Optimization of peak load
shifting  in  distribution  network  based  on  improved  mopso
algorithm [J]. Science technology and engineering, 2020, 20（10）:
3984-3989. DOI: 10.3969/j.issn.1671-1815.2020.10.028.
[9]
 郭斌. 储能在新能源及用户侧削峰填谷的经济性评估研
究 [D]. 上海: 东华大学, 2022. DOI: 10.27012/d.cnki.gdhuu.2022.
000177.
GUO B. Economic evaluation of energy storage in new energy
and  user-side  peak  shaving  and  valley  filling  [D].  Shanghai:
Donghua  University,  2022.  DOI:  10.27012/d.cnki.gdhuu.2022.
000177.
[10]
 陈雪梅, 陆超, 韩英铎. 电力系统频率问题浅析与频率特性研
究综述  [J]. 电力工程技术, 2020, 39（1）: 1-9. DOI: 10.12158/j.
2096-3203.2020.01.001.
CHEN  X  M,  LU  C,  HAN  Y  D.  Review  of  power  system
frequency problems and frequency dynamic characteristics  [J].
Electric power engineering technology, 2020, 39（1）: 1-9. DOI:
10.12158/j.2096-3203.2020.01.001.
[11]
 侯涛. 辅助新型电力系统调频的电化学储能控制策略 [D]. 吉
[12]
50
南方能源建设
第 11 卷



<!-- page 10/12 -->

林:  东北电力大学,  2022.  DOI:  10.27008/d.cnki.gdbdc.2022.
000048.
HOU  T.  Control  strategy  of  battery  energy  storage  system
participating  in  frequency  regulation  in  the  new  power  system
[D].  Jilin:  Northeast  Electric  Power  University,  2022.  DO1:
10.27008/d.cnki.gdbdc.2022.000048.
 李谦. 光伏发电参与电网频率调节的研究  [D]. 北京: 华北电
力大学（北京）, 2021. DOI: 10.27140/d.cnki.ghbbu.2021.000899.
LI  Q.  Research  on  the  participation  of  photovoltaic  power
generation in frequency regulation of power grid  [D]. Beijing:
North  China  Electric  Power  University  (Beijing),  2021.  DOI:
10.27140/d.cnki.ghbbu.2021.000899.
[13]
 YAN  L  Q,  SHUI  T,  XUE  T  L,  et  al.  Comprehensive  control
strategy considering hybrid energy storage for primary frequency
modulation  [J]. Energies, 2022, 15（11）: 4079. DOI: 10.3390/
EN15114079.
[14]
 王立娜, 谭丽平, 徐志强, 等. 锂电池储能电站一次调频设计优
化及验证 [J]. 储能科学与技术, 2022, 11（12）: 3862-3871. DOI:
10.19799/j.cnki.2095-4239.2022.0410.
WANG L N, TAN L P, XU Z Q, et al. Lithium battery energy
storage  power  station  primary  frequency  modulation  design
optimization  and  verification  [J].  Energy  storage  science  and
technology, 2022, 11（12）: 3862-3871. DOI: 10.19799/j.cnki.20
95-4239.2022.0410.
[15]
 SUO  D  N.  Research  on  primary  frequency  modulation  control
strategy of wind power based on energy storage  [J]. Journal of
physics:  conference  series,  2022,  2237（1）:  012021.  DOI:  10.
1088/1742-6596/2237/1/012021.
[16]
 娄为, 翟海保, 许凌, 等. 风电-储能-电动汽车联合调频控制策
略研究  [J]. 可再生能源, 2021, 39（12）: 1648-1654. DOI: 10.
3969/j.issn.1671-5292.2021.12.014.
LOU W, ZHAI H B, XU L, et al. Research on control strategy of
WG-ESS-PEV  joint  frequency  modulation  [J].  Renewable
energy resources, 2021, 39（12）: 1648-1654. DOI: 10.3969/j.issn.
1671-5292.2021.12.014.
[17]
 ZHAO  Z  Y,  ZHAO  T  Q,  XU  P,  et  al.  A  double-layer  voltage
control model for distributed photovoltaic in distribution network
[J]. Journal of physics: conference series, 2022, 2404（1）: 012004.
DOI: 10.1088/1742-6596/2404/1/012004.
[18]
 彭怀德, 王欣, 杨超. 江西新能源消纳与储能应用前景分析 [J].
江西电力, 2021, 45（8）: 7-11. DOI: 10.3969/j.issn.1006-348X.
2021.08.003.
PENG  H  D,  WANG  X,  YANG  C.  Analysis  on  the  application
prospect of new energy consumption and storage in Jiangxi  [J].
Jiangxi electric power, 2021, 45（8）: 7-11. DOI: 10.3969/j.issn.
1006-348X.2021.08.003.
[19]
 GOLPÎRA  H,  MESSINA  A  R,  BEVRANI  H.  Emulation  of
virtual  inertia  to  accommodate  higher  penetration  levels  of
distributed generation in power grids  [J]. IEEE transactions on
power systems, 2019, 34（5）: 3384-3394. DOI: 10.1109/TPWRS.
2019.2908935.
[20]
 彭占磊, 杨之乐, 杨文强, 等. 电化学储能参与电力系统规划运
行方法综述  [J]. 综合智慧能源, 2022, 44（6）: 37-44. DOI: 10.
3969/j.issn.2097-0706.2022.06.004.
PENG Z L, YANG Z L, YANG W Q, et al. Review on planning
and  operation  methods  for  power  system  with  participation  of
electrochemical energy storage systems [J]. Integrated intelligent
energy, 2022, 44（6）: 37-44. DOI: 10.3969/j.issn.2097-0706.2022.
06.004.
[21]
 王海华, 陆冉, 曹炜, 等. 规模风电并网条件下储能系统参与辅
助调峰服务容量配置优化研究  [J]. 电工电能新技术, 2019,
38（6）: 42-49. DOI: 10.12067/ATEEE1803022.
WANG H H, LU R, CAO W, et al. Optimal capacity allocation
of energy storage system participating auxiliary peak regulation
in large-scale wind power integration  [J]. Advanced technology
of electrical engineering and energy, 2019, 38（6）: 42-49. DOI: 10.
12067/ATEEE1803022.
[22]
 曹金京. 面向新能源消纳的分布式光伏储能系统优化配
置  [J]. 自动化应用, 2021（4）: 4-6. DOI: 10.19769/j.zdhy.20
21.04.002.
CAO  J  J.  Optimal  configuration  of  distributed  photovoltaic
energy  storage  system  for  new  energy  consumption  [J].
Automation application, 2021（4）: 4-6. DOI: 10.19769/j.zdhy.20
21.04.002.
[23]
 刘卫健, 黎淑娟, 黄际元, 等. 储能参与风电并网系统的波动平
抑控制研究  [J]. 电器与能效管理技术, 2018（16）: 41-47, 66.
DOI: 10.16628/j.cnki.2095-8188.2018.16.009.
LIU W J, LI S J, HUANG J Y, et al. Study on smoothing the
fluctuation of energy storage system in grid with wind power [J].
Electrical & energy management technology, 2018（16）: 41-47,
66. DOI: 10.16628/j.cnki.2095-8188.2018.16.009.
[24]
 GAO  Y,  ZHOU  S  D,  KANG  X  G,  et  al.  Research  on  grid-
connected  photovoltaic  energy  storage  to  stabilize  power
fluctuations  [J].  Journal  of  physics:  conference  series,  2022,
2355（1）: 012028. DOI: 10.1088/1742-6596/2355/1/012028.
[25]
 黄彦景. 考虑用户侧储能协同的配电网电压质量控制技术研
究  [D]. 广州: 广东工业大学, 2022. DOI: 10.27029/d.cnki.
ggdgu.2022.001811.
HUANG Y J. Research on voltage quality control technology of
distribution  network  considering  energy  storage  cooperation  at
user side [D]. Guangzhou: Guangdong University of Technology,
2022. DOI: 10.27029/d.cnki.ggdgu.2022.001811.
[26]
 王一飞, 董新伟, 杨飞, 等. 基于配电网电压质量的分布式储能
系统优化配置研究 [J]. 热力发电, 2020, 49（8）: 126-133. DOI:
10.19666/j.rlfd.202003082.
WANG Y F, DONG X W, YANG F, et al. Optimal configuration
of distributed energy storage system based on voltage quality of
distribution network [J]. Thermal power generation, 2020, 49（8）:
126-133. DOI: 10.19666/j.rlfd.202003082.
[27]
 孙永辉, 赵树野, 张秀路, 等. 考虑分布式光伏与储能联合的区
域电网电压稳定性控制方法  [J]. 可再生能源, 2022, 40（8）:
1115-1122. DOI: 10.13941/j.cnki.21-1469/tk.2022.08.010.
[28]
第 4 期
黄海泉，等：新型配电网分布式储能系统方案及配置研究综述
51



<!-- page 11/12 -->

SUN Y H, ZHAO S Y, ZHANG X L, et al. Distributed energy
storage  coordinated  operation  strategy  for  improving  voltage
stability of regional power grid [J]. Renewable energy resources,
2022, 40（8）: 1115-1122. DOI: 10.13941/j.cnki.21-1469/tk.2022.
08.010.
 孙阔, 张雪菲, 迟福建, 等. 光伏电站复合储能电压波动抑制双
层优化控制方法 [J]. 可再生能源, 2022, 40（3）: 402-409. DOI:
10.13941/j.cnki.21-1469/tk.2022.03.015.
SUN K, ZHANG X F, CHI F J, et al. Optimal configuration and
control  strategy  of  hybrid  energy  storage  system  for  smoothing
wind power fluctuations  [J]. Renewable energy resources, 2022,
40（3）: 402-409. DOI: 10.13941/j.cnki.21-1469/tk.2022.03.015.
[29]
 傅美平, 毛建容, 宋锐, 等. 大型新能源富集地区储能电站电压
无功控制策略 [J]. 电器与能效管理技术, 2022（2）: 88-94. DOI:
10.16628/j.cnki.2095-8188.2022.02.014.
FU M P, MAO J R, SONG R, et al. Voltage and reactive power
control  strategy  of  energy  storage  power  stations  in  large  new
energy  enriched  areas  [J].  Electrical  &  energy  management
technology,  2022（2）:  88-94.  DOI:  10.16628/j.cnki.2095-8188.
2022.02.014.
[30]
 穆佳豪. 有源配电网中分布式储能多目标优化配置研究 [D].
汉中: 陕西理工大学, 2022. DOI: 10.27733/d.cnki.gsxlg.2022.
000280.
MU  J  H.  Research  on  multi-objective  optimal  configuration  of
distributed  energy  storage  in  active  distribution  network  [D].
Hanzhong:  Shaanxi  University  of  Technology,  2022.  DOI:
10.27733/d.cnki.gsxlg.2022.000280.
[31]
 熊力颖, 何晓琼, 韩鹏程, 等. 基于改进控制策略的交直流独立
光储电源系统  [J]. 电气工程学报, 2022, 17（3）: 95-103. DOI:
10.11985/2022.03.011.
XIONG  L  Y,  HE  X  Q,  HAN  P  C,  et  al.  AC-DC  independent
optical storage power system based on improved control strategy
[J]. Journal of electrical engineering, 2022, 17（3）: 95-103. DOI:
10.11985/2022.03.011.
[32]
 ZHANG  Q,  PEI  W  H,  LIU  X  D.  Advances  in  electrochemical
energy storage systems  [J]. Electrochem, 2022, 3（2）: 225-228.
DOI: 10.3390/ELECTROCHEM3020014.
[33]
 田中利. 单相光伏储能逆变系统及其控制方法的研究 [D]. 扬
州: 扬州大学, 2019. DOI: 10.27441/d.cnki.gyzdu.2019.000416.
TIAN  Z  L.  Study  on  single-phase  photovoltaic  energy  storage
inverter  system  and  its  control  method  [D].  Yangzhou:
Yangzhou  University,  2019.  DOI:  10.27441/d.cnki.gyzdu.2019.
000416.
[34]
 汤伟. 一种光伏储能逆变器的研究与实现  [D]. 扬州: 扬州大
学, 2022. DOI: 10.27441/d.cnki.gyzdu.2022.002532.
TANG W. Research and implementation of a photovoltaic energy
storage  inverter  [D].  Yangzhou:  Yangzhou  University,  2022.
DOI: 10.27441/d.cnki.gyzdu.2022.002532.
[35]
 张克勇, 王冠瑞, 耿新, 等. 含高比例光-储单元的主动配电网并
网功率分布式协同控制策略 [J]. 电力科学与技术学报, 2022,
37（2）: 147-155. DOI: 10.19781/j.issn.1673-9140.2022.02.017.
[36]
ZHANG  K  Y,  WANG  G  R,  GENG  X,  et  al.  Distributed
cooperative  control  strategy  for  grid-connected  power  in  ADN
with  high  proportion  of  PV-ESS  units  [J].  Journal  of  electric
power science and technology, 2022, 37（2）: 147-155. DOI: 10.
19781/j.issn.1673-9140.2022.02.017.
 李建林, 方知进, 谭宇良, 等. 电化学储能系统在整县制屋顶光
伏中应用前景分析  [J]. 太阳能学报, 2022, 43（4）: 1-12. DOI:
10.19912/j.0254-0096.tynxb.2022-0084.
LI J L, FANG Z J, TAN Y L, et al. Application prospect analysis
of  electrochemical  energy  storage  technology  in  county-wide
rooftop  photovoltaic  system  [J].  Acta  energiae  solaris  sinica,
2022, 43（4）: 1-12. DOI: 10.19912/j.0254-0096.tynxb.2022-0084.
[37]
 张耀文, 张政权, 刘庆想, 等. 新型双向储能变流器分析与研究
[J]. 太阳能学报, 2022, 43（4）: 82-89. DOI: 10.19912/j.0254-
0096.tynxb.2020-0183.
ZHANG  Y  W,  ZHANG  Z  Q,  LIU  Q  X,  et  al.  Analysis  and
research of new bidirectional energy storage converter  [J]. Acta
energiae  solaris  sinica,  2022,  43（4）:  82-89.  DOI:  10.19912/j.
0254-0096.tynxb.2020-0183.
[38]
 张国鑫. 基于开关电容和混合PWM 的高增益多电平光伏逆变
器 [D]. 广州: 广东工业大学, 2022. DOI: 10.27029/d.cnki.ggdgu.
2022.001308.
ZHANG G X. High-gain multilevel photovoltaic inverter based
on  switched-capacitor  and  hybrid  PWM  [D].  Guangzhou:
Guangdong University of Technology, 2022. DOI: 10.27029/d.cn
ki.ggdgu.2022.001308.
[39]
 王垚, 汤亚芳, 郝正航, 等. 新型高效率无漏电流单相非隔离光
伏逆变器 [J]. 电网与清洁能源, 2022, 38（2）: 121-128. DOI: 10.
3969/j.issn.1674-3814.2022.02.017.
WANG Y, TANG Y F, HAO Z H, et al. A novel single-phase non-
isolated  photovoltaic  inverter  with  no  leakage  current  and  high
efficiency [J]. Power system and clean energy, 2022, 38（2）: 121-
128. DOI: 10.3969/j.issn.1674-3814.2022.02.017.
[40]
 郑越. 光储一体化变流器控制策略及并网/离网切换技术研究
[D]. 兰州: 兰州理工大学, 2021. DOI: 10.27206/d.cnki.ggsgu.
2021.000750.
ZHENG Y. Research on control strategy and grid-connected/off-
grid  switching  technology  of  integrated  photovoltaic  energy
storage  converter  [D].  Lanzhou:  Lanzhou  University  of
Technology, 2021. DOI: 10.27206/d.cnki.ggsgu.2021.000750.
[41]
 王子琪. 含风光区域电网的储能选址定容及能量管理研究
[D]. 北京: 华北电力大学(北京), 2021. DOI: 10.27140/d.cnki.
ghbbu.2021.001443.
WANG  Z  Q.  Research  on  the  location  and  capacity  of  energy
storage and energy management of regional power grid with wind
and  solar  energy  [D].  Beijing:  North  China  Electric  Power
University  (Beijing),  2021.  DOI:  10.27140/d.cnki.ghbbu.2021.
001443.
[42]
 陆燕娟. 含电动汽车的社区微网储能容量配置及能量管理策
略研究 [D]. 无锡: 江南大学, 2021. DOI: 10.27169/d.cnki.gwqgu.
2021.000900.
[43]
52
南方能源建设
第 11 卷



<!-- page 12/12 -->

LU  Y  J.  Research  on  energy  storage  allocation  and  energy
management strategy of community micro-grid including electric
vehicles [D]. Wuxi: Jiangnan University, 2021. DOI: 10.27169/d.
cnki.gwqgu.2021.000900.
 梁芳玉. 计及配电网网损和电压波动的分布/集中式光储选址
定容研究  [D]. 南京: 南京理工大学, 2021. DOI: 10.27241/d.
cnki.gnjgu.2021.001649.
LIANG  F  Y.  Distributed/centralized  energy  storage  palacement
and  capacity  selection  considering  distribution  network  power
losses and voltage swings  [D]. Nanjing: Nanjing University of
Science & Technology, 2021. DOI: 10.27241/d.cnki.gnjgu.2021.
001649.
[44]
 王泽. 基于双层决策模型的用户侧储能优化配置方法 [D]. 太
原:  太原理工大学,  2021.  DOI:  10.27352/d.cnki.gylgu.2021.
000588.
WANG  Z.  Optimal  configuration  method  of  user-side  energy
storage  based  on  two-layer  decision  model  [D].  Taiyuan:
Taiyuan  University  of  Technology,  2021.  DOI:  10.27352/d.
cnki.gylgu.2021.000588.
[45]
 曹希桓. 光储充一体化充电站配置优化方法研究  [D]. 兰州:
兰州理工大学, 2021. DOI: 10.27206/d.cnki.ggsgu.2021.000062.
CAO  X  H.  Research  on  optimization  method  of  charge  station
configuration for integrated storage and charging  [D]. Lanzhou:
Lanzhou  University  of  Technology,  2021.  DOI:  10.27206/
d.cnki.ggsgu.2021.000062.
[46]
 张德隆, MUBAARAK S, 蒋思宇, 等. 基于概率潮流的光伏电
站中储能系统的优化配置方法  [J]. 储能科学与技术, 2021,
10（6）: 2244-2251. DOI: 10.19799/j.cnki.2095-4239.2021.0151.
ZHANG  D  L,  MUBAARAK  S,  JIANG  S  Y,  et  al.  Optimal
allocation  method  of  energy  storage  in  PV  station  based  on
probabilistic  power  flow  [J].  Energy  storage  science  and
technology, 2021, 10（6）: 2244-2251. DOI: 10.19799/j.cnki.2095-
4239.2021.0151.
[47]
 赵立军, 张秀路, 韩丽维, 等. 基于多场景的配电网分布式光伏
及储能规划  [J]. 现代电力, 2022, 39（4）: 460-468. DOI: 10.
19725/j.cnki.1007-2322.2021.0257.
ZHAO  L  J,  ZHANG  X  L,  HAN  L  W,  et  al.  Distributed
photovoltaic  generation  and  energy  storage  planning  of
distribution  network  based  on  multi  scenarios  [J].  Modern
electric power, 2022, 39（4）: 460-468. DOI: 10.19725/j.cnki.1007-
2322.2021.0257.
[48]
 彭伟, 郑连清, 郑天文. 分布式光伏储能系统的优化配置方法
[J]. 四川电力技术, 2022, 45（1）: 45-49, 94. DOI: 10.16527/j.
issn.1003-6954.20220110.
PENG  W,  ZHENG  L  Q,  ZHENG  T  W.  Optimal  configuration
method  of  distributed  photovoltaic  energy  storage  system  [J].
Sichuan electric power technology, 2022, 45（1）: 45-49, 94. DOI:
[49]
10.16527/j.issn.1003-6954.20220110.
 王丹. 基于改进多智能体Q 学习的多源联合调频控制策略及
储能容量配置研究  [D]. 吉林: 东北电力大学, 2022. DOI:
10.27008/d.cnki.gdbdc.2022.000122.
WANG D. Research on multi-source joint frequency regulation
control strategy and energy storage capacity allocation based on
improved  multi-agent  Q-learning  [D].  Jilin:  Northeast  Electric
Power  University,  2022.  DOI:  10.27008/d.cnki.gdbdc.2022.000
122.
[50]
作者简介：
黄海泉（第一作者）
1982-，男，高级工程师，学士，主要从事配农
网工程管理和配农网运维检修研究工作（e-
mail）huanghq82@icloud.com。
黄晓巍
1981-，男，学士，主要从事电力输配电技术研究工作（e-mail）
55071298@qq.com。
姜望
1984-，男，学士，主要从事电力基建技术研究工作（e-mail）
19197988@qq.com。
王媛媛
1984-，女，学士，主要从事电力调度技术研究工作（e-mail）
5456077@qq.com。
王言方
1991-，男，学士，主要从事配网工程管理和配网运检技术研究
工作（e-mail）976165718@qq.com。
丁浩
1996-，男，助理工程师，硕士，主要从事配电线路巡检工作（e-
mail）591193125@qq.com。
左杰文（通信作者）
1999-，男，硕士，主要研究光伏储能配置技
术工作（e-mail）1351073729@qq.com。
夏晨阳
1982-，男，高级工程师，教授，博士，从事高校教学与科研工作
（e-mail）18260722082@163.com。
（编辑　孙舒）
第 4 期
黄海泉，等：新型配电网分布式储能系统方案及配置研究综述
53
