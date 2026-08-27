<!--
source: D5_规划与灵活资源/CN_CSEE_distributed_PV_2024.pdf
sha256: ab3039a85044f8254c6361208643eb600db5d6dfa2b3f9e46c40a2bcf904e248
method: pymupdf
pages: 15
-->

<!-- page 1/15 -->

第48 卷 第1 期 
电  网  技  术 
Vol. 48 No. 1 
2024 年1 月 
Power System Technology 
Jan. 2024 
文章编号：1000-3673（2024）01-0184-13    中图分类号：TM 721    文献标志码：A    学科代码：470·40 
新型电力系统下分布式光伏规模化并网运行
关键技术探讨
栗峰1，丁杰1，周才期2，雍维桢3，黄越辉1，王建学3，许晓慧1 
（1．中国电力科学研究院有限公司，北京市 海淀区 100192； 
2．国家电力调度控制中心，北京市 西城区 100031； 
3．西安交通大学电气工程学院，陕西省 西安市 710049） 
 
Key Technologies of Large-scale Grid-connected Operation of 
Distributed Photovoltaic Under New-type Power System 
LI Feng1, DING Jie1, ZHOU Caiqi2, YONG Weizhen3, HUANG Yuehui1, WANG Jianxue3, XU Xiaohui1 
(1. China Electric Power Research Institute, Haidian District, Beijing 100192, China; 
2. National Power Dispatching and Control Center, Xicheng District, Beijing 100031, China; 
3. School of Electrical Engineering, Xi’an Jiaotong University, Xi’an 710049, Shaanxi Province, China) 
1ABSTRACT: Promoting the large scale grid connection of 
distributed photovoltaic (PV) is an important measure to 
achieve the goal of "carbon peaking and carbon neutrality" and 
to construct the new-type power system. Based on this 
background, this paper discusses the key technologies for the 
large-scale grid-connected operation of the distributed PV for 
the new-type power system. Firstly, the development status, the 
grid-connected modes, and the operation modes of the 
distributed PV are summarized and elaborated, and the 
challenges brought by the large-scale distributed PV access to 
the power grid dispatching and operation are analyzed. 
Secondly, in the face of the above challenges, the key 
technologies for the system scheduling and operation are 
discussed from the perspectives of information integration, 
monitoring 
and 
prediction, 
balanced 
dispatching, 
and 
aggregation controlling, in order to assist in the transformation 
and upgrading of the power grid regulation modes. Then, 
considering the actual engineering needs, a distributed PV 
technology standard system that meets the safe and stable 
operation of the power grid is conceived, with a view to 
promoting the distributed PV to be "observable, measurable, 
schedulable, controllable, and friendly interactable". Finally, 
the advanced experiences of the large-scale grid-connected 
operation of the distributed PV in some foreign countries are 
investigated and sorted out, and suggestions on the topics of the 
distributed PV in China, such as grid-connection collaboration 
exploration, operation service support and market transaction 
                                                        
基金项目：国家重点研发计划项目(2022YFB2402900)。 
Project Supported by National Key Research & Development 
Program of China (2022YFB2402900). 
participation, are made. 
KEY WORDS: new-type power system; distributed PV; 
grid-connected operation; key technologies; standard system 
摘要：推进分布式光伏规模化并网是实现“碳达峰碳中和”
目标和构建新型电力系统的重要举措。基于此背景探讨面向
新型电力系统的分布式光伏规模化并网运行关键技术。首先，
归纳并阐述分布式光伏发展现状、并网方式及运行模式，分
析大规模分布式光伏接入给电网调度运行带来的挑战。其次，
面对上述挑战，从信息集成、监测预测、平衡调度、聚合控
制等视角提出系统调度运行关键技术，助力电网调控模式转
型升级。然后，考虑实际工程需求，构思满足电网安全稳定
运行的分布式光伏技术标准体系，以期促使分布式光伏“可
观可测、可调可控、友好互动”。最后，调研并梳理国外分
布式光伏规模化并网运行先进经验，并对我国分布式光伏并
网协同探索、运行服务支持及市场交易参与等课题提出建议。 
关键词：新型电力系统；分布式光伏；并网运行；关键技术；
标准体系 
DOI：10.13335/j.1000-3673.pst.2023.0771 
0  引言 
为构建适应新能源占比逐渐提高的新型电力
系统，推动能源清洁低碳转型，以“整县屋顶光伏
开发”“‘光伏+’综合利用”“千家万户沐光行
动”等大规模分布式光伏灵活接入和就近消纳为导
向的新政策、新模式(统称“规模化并网”模式)应
运而生。光伏发电将由以集中式为主向集中式与分
布式并举转变[1-3]，与风力发电逐步成为我国主体电



<!-- page 2/15 -->

第48 卷 第1 期 
电  网  技  术 
185 
源之一，常规电源则逐渐从发电主体转变为基础保
障性和系统调节性资源[4-5]。伴随着新型电力系统构
建，分布式光伏将呈高密度、规模化并网态势，且
嵌入多电压等级配网，与主网耦合度加大，使得系统
运行特性发生重大改变，主要体现在以下几方面： 
1）海量分布式光伏并网发电逐步影响系统安
全特性[6]。随着分布式光伏接入比例不断升高，常
规机组开机空间被进一步挤压，系统“高比例可再
生能源”、“高比例电力电子设备”特征愈发明显，
转动惯量和阻尼不断降低，调频、调压能力持续下
降，威胁系统安全稳定运行。 
2）高渗透分布式光伏加大电网午间低谷保消
纳和晚间高峰保供给的难度[7]。分布式光伏发电具
有强随机性和波动性，与本地负荷之间存在时间不
平衡性，净负荷曲线易出现“鸭型曲线”现象，系
统发用电平衡、实时调度等过程中不确定性增多，
全额消纳代价变大，影响系统运行经济性。 
3）分布式光伏使配电系统逐渐网格化、有源
化、主动化[8]。分布式光伏规模化并网使配电网由
放射状无源网变为具有海量电源点的网格有源网，
出现发用电关系相互转换、主网与配网间潮流频繁
转向与大幅波动等现象，对主动配电网功率控制、
电压调节、通信方式等提出更高要求。 
4）现行标准难以满足分布式光伏规模化并网
需求[9]。与常规机组和集中式新能源场站相比，分
布式光伏因标准不完善易出现涉网性能差、设备故
障率高、运维能力弱、逆变器和通信装置受到外界
攻击等运行风险，分布式光伏低标准并网及运行引
起的连锁脱网概率也显著增大。 
面对分布式光伏规模化并网带来的电力系统
形态转变，电力系统调控技术和管理模式亟需革新
升级。本文立足工程实践，阐述我国分布式光伏并
网运行概念与特征，研判分布式光伏规模化并网给
电力系统运行带来的风险与挑战，探讨高比例分布
式光伏电力系统调度运行关键技术，构建适应大规
模分布式光伏友好接入的标准体系，以促进分布式
光伏与电网的深度融合和友好交互。 
1  我国分布式光伏并网运行概述 
1.1  分布式光伏发展现状 
分布式光伏规模化开发和并网是优化能源结
构和构建新型电力系统的重要举措，近年来我国在
战略规划、技术攻关、科技创新等领域陆续出台了
诸多分布式光伏支持政策(详见附录A 表A1)。在政
策、市场及技术的驱动下，2021 年，我国分布式光
伏新增容量首次超过集中式光伏，具有里程碑意   
义[10]，“十四五”期间拟新增分布式光伏容量超过 
1 亿kW[11]。截至2022 年底，我国分布式光伏累计
装机容量157.62GW，接入35kV、20/10kV、380/220V
电压等级的容量占比约为3%、30%、67%；电站累
计数量超过400 万户/座，其中99%以上接入中低压
配电网，呈现“单机小、数量多、电压低、分布无
规律”等特点。山东、河北、浙江等多个地区局部
电网分布式光伏发电占当地负荷的最大比重超过
100%，且范围和比重仍在不断扩大[12]。 
1.2  光伏发电主要并网方式 
目前我国光伏发电主要包括集中式并网和分
散式并网2 种方式。在以整县开发、“光伏+”为
代表的政策支撑下，分布式光伏规模化并网将成为
清洁能源利用的主要方式之一，该方式实行统筹规
划、集中接入和联合管理，关键设备的一致性和涉
网性能得到有效改善，发电利用率和运行维护得到
有效保障，同时也会引起电压越限、潮流反送、线
损增加等问题。与分散式并网方式相比，分布式光
伏规模化并网多以运营商或电网为主体开展统一
规划、选址定容和有序并网，最大程度提升用户用
能清洁性。不同并网方式下光伏接入特性、运营管
理和市场参与等存在较大差异，如表1 所示。 
表1  光伏发电主要并网方式对比 
Table 1  Comparison of main grid-connected modes of PV 
power generation 
研究对象
集中式光伏 
分布式光伏 
并网方式
1. 集中式并网
2. 分散式并网 
3. 规模化并网 
容量规模
4. 10MW级 
5.  kW级 
6.  MW级 
接入位置
7. 电源侧 
8. 用户侧 
9. 用户侧 
电压等级
10. 35kV及以上
11. 35kV及以下 
12. 35kV及以下 
利用模式
13. 远距离输送
为主 
14. 就地消纳 
15. 就近消纳为主
涉网性能
16. 具备频率、
电压适应性 
17. 设备性能不一，
耐频耐压程度低
18. 设备性能差异小，
耐频耐压能力增强
功能特点
19. 具备可观可
测、可调可控
能力 
20. 部分可观可测、
可调可控，经济
成本高 
21. 部分可观可测、
可调可控，经济成本
较低 
管理难度
22. 容易 
23. 困难 
24. 适中 
市场化
程度 
25. 市场参与度
较高 
26. 聚合难、动力不
足、市场程度低
27. 可聚合参与市
场，潜力和动力大
1.3  分布式光伏典型运行模式 
在政策支持和市场激励下，我国分布式光伏发
展伴随微电网[13]、聚合商[14]、虚拟电厂[15]、多能源
系统[16]、综合能源服务[17]等新理念、新技术呈多元
化发展态势，如表2 所示，这些模式的共同特点是
将并网电压等级较低且偏向用户侧的分布式资源



<!-- page 3/15 -->

186 
栗峰等：新型电力系统下分布式光伏规模化并网运行关键技术探讨 
Vol. 48 No. 1 
表2  分布式光伏典型运行模式 
Table 2  Typical operation modes of distributed PV 
运行模式 
核心要义 
微电网 
由分布式光伏、储能与负荷组成且具备调节能力的
小型供用电系统，可并离网运行。 
聚合商 
借用第三方将分散的用户侧资源进行整合，作为 
中间层参与电网响应调控。 
虚拟电厂 
通过先进通信技术将分布式电源、储能、可控负荷等
资源整合成一个有机整体，参与系统调控和交易。
多能源系统 
利用先进信息物理系统管理电、热、气等多种能源，
通过不同能源的集成和转换，促进分布式光伏消纳。
综合能源服务
含太阳能、天然气、生物质等多种分布式资源的 
多能互补和综合利用服务。 
进行有效整合并参与系统运行和用户交易。分布式
光伏规模化并网将进一步推动上述运行模式应用
与发展，新的运行模式也将不断涌现，对电网的智
能管控水平和接纳能力提出更为迫切的要求。 
2  分布式光伏规模化并网带来的挑战 
随着分布式光伏规模化发展和接入，电力系统
信息感知和调控能力不足，现有技术手段难以做到
全面“可观、可测、可调、可控”，调控管理体系
无法适应新形势发展要求，进一步加剧对系统调度
运行的挑战。 
2.1  “可观可测”程度较低 
分布式光伏信息采集和传输环节错综复杂，技
术支撑手段不足[18]。因短期迸发式增长，分布式光
伏采集、传输、监视等业务量和数据量呈指数上升，
各地区缺乏统一信息接入方案，影响数据记录的准
确度与可靠性；以中低压并网为主的分布式光伏存
在监视数据缺失、运行信息延迟、安全防护薄弱等
问题，数据可获取性和可利用率不高，致使网供负
荷进一步失真，给系统调度运行和业务应用带来极
大的安全隐患。 
电网缺乏在线实时监测预警，难以保证高渗透
率分布式光伏的安全性[19]。分布式光伏接入较为随
意，并未考虑网架接纳能力与就近负荷匹配度，容
易引起局部地区线路、变压器过载以及中低压配电
网向高压配电网甚至主干电网倒送功率；设备参数
多元性以及技术支撑滞后性使得电网精准建模难
度加大，传统电网潮流计算、静态稳定分析、短路
电流计算等校核手段准确度下降；分布式光伏大量
接入还会导致可切馈线有源化加剧，进而降低电网
对分布式发电运行的风险感知、量化评估及防控预
警能力，影响系统调控运行。 
分布式光伏因随机性、波动性和间歇性特点，
预测难度较大[20]。光伏发电预测依赖气象监测、数
值天气预报(numerical weather prediction，NWP)和
运行数据等信息。考虑经济成本及安装条件等因
素，分布式光伏尚不具备气象监测和NWP 信息，
且鲜有功率预测系统，给系统负荷和潮流带来极大
不确定性；与集中式相比，分布式光伏功率预测结
果置信度较低，其就近消纳将对并网母线负荷预
测、电网阻塞、多层级功率平衡及系统正负备用留
取等造成困扰。 
2.2  “可调可控”能力偏弱 
电力平衡调度难度提升，系统灵活性资源稀缺[21]。 
分布式光伏规模化并网以中低压为主，暂未全额纳
入电网发用电平衡体系，同时分布式光伏发电与负
荷用电重合叠加，使得电网调峰特征发生显著变
化；分布式光伏装机比重持续增加，但其电力电量
支撑能力与常规电源及集中式新能源相比存在较
大差距，未能形成可靠替代能力，一方面等效减少
常规机组平均出力和利用小时数，另一方面又对常
规机组调峰深度和响应速度有苛刻要求，加剧了系
统平衡的矛盾。 
系统调频能力受到影响，新的稳定性问题显现[22]。 
分布式光伏规模化并网将替代部分常规同步电源，
导致受端电网等效惯量进一步降低，抗扰动能力不
断下降，出现新的稳定分析与控制等问题；分布式
光伏规模化并网将消纳大量负荷，低频低压可切负
荷量相继减少，将出现午间可切负荷量大幅降低的
风险，影响电网三道防线安全。英国“89”大停电
事故中，分布式光伏因涉网性能参数弱导致频率抗
扰动能力差，先后出现2 次集中脱网，扩大事故影
响范围[23]。 
局域调压能力下降，电能质量受到较大影响
[24]。区别于常规电网单点辐射状结构，分布式发电
受地理位置及配网线路电阻较大、电抗较小等影
响，极易出现光伏大发/小发抬高/拉低配电线路及
台区的末端电压，引起电压越限、三相不平衡等问
题；现有自动电压控制(automatic voltage control，
AVC)体系鲜有接入分布式光伏场站，网络末端电压
偏差和越限风险加剧，原有AVC 系统为平抑分布
式光伏并网点电压波动，频繁启停降低设备使用寿命。 
场站并网设备性能偏低，难以直接调控[25]。分
布式光伏主要安装在配用侧，其并网时间、地点、
厂商不一，设备“遥控、遥调”水平参差不齐，无
法有效接收主站调度指令；此外，单个场站装机容
量小、地理位置分散、功率波动大，直接控制难度
大、成本高，进一步削弱光伏调节能力。



<!-- page 4/15 -->

第48 卷 第1 期 
电  网  技  术 
187 
3  高比例分布式光伏电力系统调度运行关
键技术 
为主动应对分布式光伏规模化并网带来的挑
战，本文结合工程实践需求从分布式光伏“可观、 
可测、可调、可控”出发，分别对信息集成、监测
预测、平衡调度、聚合控制等关键技术及其关联支
撑关系进行探讨，以期为电网安全稳定运行及系统
优化调度提供综合解决措施，如图1 所示。 
快速
发展
可测
可调
可控
可观
系统稳定问题显现，
场站支撑水平有限
分布式光伏规模化发
展必要性
分布式光伏规模化并
网带来的挑战
高比例分布式光伏调
度运行关键技术
不同发展阶段分布式
光伏调度运行成效
源荷双侧不确定性
增强，平衡难度大
承载监测缺失，功率
预测难度大
信息感知能力不足，
数据传输量大
面向电网友好支撑的分布式光
伏聚合控制技术
参与市场行为的分布式光伏自
适应控制技术
系统调节能力下降情况下的多
级协同平衡调度技术
考虑主配网约束的分布式光伏
接入电网承载监测和预警技术
基于不完全量测数据的分层分
级功率预测技术
多元信息采集、集成传输和安
全防护技术
分布式光伏安
全可靠并网
和高效运行
分布式光伏柔
性灵活可控和
主动响应
分布式光伏主
动支撑电网和
参与市场交易
......
不
同
发
展
阶
段
解决
措施
新能源占比逐步提
升的新型电力系统
用户侧太阳能资
源高效利用
预期
成效
 
图1  高比例分布式光伏电力系统调度运行技术路径 
Fig. 1  Technology path of high proportion distributed PV power system scheduling and operation 
3.1  分布式光伏“可观”：信息感知与广域集成 
技术 
分布式光伏设备种类多样、安装环境复杂，准
确、持续的发电运行和气象监测数据是其性能分
析、功率预测和运行控制的前提和基础。信息采集
和数据传输是实现电力调控中心对分布式光伏“可
观”的2 个重要环节。在信息采集环节，现有研究
主要利用智能电表[26]、小微传感器[27]、边缘计算终
端[28]等设备实现电气参数的采集，利用气象传感器
[29]等设备实现气象数据的采集。在数据传输环节，
分布式光伏除采用有线传输(如光纤网络、电力载
波)外，还可考虑无线传输；因接入灵活、成本低等
优势，无线传输已获得较大范围应用，但在运行控
制方面仍有一定局限性[30]。分布式光伏常见通信方
式及特点如表3 所示。 
随着新兴技术发展，分布式光伏数据汇集方式
面临变革。在信息采集环节，考虑到分布式光伏存
在采集设备缺失或质量不高等问题，可利用数据之 
表3  分布式光伏常见通信方式 
Table 3  Common communication modes of distributed PV 
传输 
方式 
通信 
媒介 
优点 
缺点 
有线 
传输 
光纤 
网络 
传输稳定、容量大、
频带宽、可靠性高
传输成本高，受场站 
所在位置影响较大 
电力 
载波 
无需重新架设网络，
传输速度快 
仅在一个配电范围内 
传送，易受信号干扰 
无线 
传输 
无线 
专网 
成本低，固定带宽，
支持“四遥” 
须额外配置安全接入区， 
增加投资与运维成本 
无线 
公网 
复用移动网络，成本
低，支持遥信、遥测
遥调、遥控易受外部攻击，
运行控制风险大 
间的关联性实现虚拟采集，以提升信息感知的覆盖
面[31]。在数据传输环节，第五代移动通信技术(5th 
generation mobile communication technology，5G)逐
渐兴起，可以有效提升数据传输速率和容量，为海
量分布式光伏接入提供基础支撑[32]。考虑信息安全
和数据质量需求，结合先进通信技术，构建分层级、
高安全传输的新型信息集成接入架构，以服务高比
例分布式光伏并网，如图2 所示。 
分布式光伏
运行及气象
信息感知
多层级分布
式光伏信息
集成与聚合
分布式光伏
数据安全
传输与防护
聚合商/主站端
用户侧/场站端
分布式光伏多元信息感知
技术与经
济性分析
信息传感
态势感知
边缘计算
数据清洗
多元异构数据
台
账
数
据
运
行
工
况
电
气
数
据
非
电
气
量
集成与聚合
5
G
技
术
信
息
集
成
聚
合
同
步
灵
活
组
网
参与
电网
双向
互动
虚拟电厂
微电网
聚合商等
先进通信技术
安全防护技术
信息加密技术
 
图2  分布式光伏分层级信息采集、集成及传输架构 
Fig.2  Distributed PV hierarchical information collection, 
integration and transmission architecture 
大规模分布式光伏并网位置灵活、涉及主体多
样，感知技术存在差异，未来应重点考虑：1）经
济可靠采集。在满足性能要求的前提下进一步降低
采集过程成本，提升数据获取和交互的经济性；考
虑到数据异常情况，须在底层做好采集信息的辨识
和清洗。2）安全高效传输。针对不同应用场景，



<!-- page 5/15 -->

188 
栗峰等：新型电力系统下分布式光伏规模化并网运行关键技术探讨 
Vol. 48 No. 1 
选择适配场景的通信方式，保证数据传输高效性；
考虑外部攻击等因素，对数据进行加密处理，提升
数据传输安全性。 
3.2  分布式光伏“可测”：监测预警与集群预测 
技术 
在“可观”的基础上，进一步实现系统状态监
测预警和光伏集群功率预测，一方面聚焦当下电网
复杂运行特征，整体把控系统状态，另一方面关注
未来光伏功率输出情况，局部掌握光伏出力，实现
分布式光伏规模化并网重点环节“预知”。 
在分布式光伏规模化接入背景下，电网运行面
临更多不确定性，也更易出现各种异常状况。为此，
需要对系统运行状态尤其是分布式光伏运行工况
进行监测，以便及时预警各种风险情况，保证电网
安全性[33]。监测对象及关键指标主要包括两大类，
第一类是分布式光伏消纳水平及其对负荷的贡献
程度，包括分布式光伏功率渗透率、容量渗透率和
能量渗透率等[34]；第二类是电网各节点实时接纳分
布式光伏的空间和能力，主要采用分布式光伏承载
力来衡量。在工程实践中，承载力计算主要基于“规
划运行相结合、主配协同互校核”原则，主网应考
虑网架结构、潮流状态、系统稳定运行等刚性约束，
实时监控并合理评估电网各节点新能源可接纳裕
度，实现网架建设规划与新能源运行消纳有效协
同；配网应满足分布式光伏并网带来的热稳定评
估、电压偏差校核、短路电流校核、谐波校核等技
术要求，并纳入全网新能源消纳评估模型进行调
峰、断面等安全校核，实现高比例分布式光伏并网
在线监测和危机预警。 
当分布式光伏发电功率高于本地负荷，即出现
功率倒送现象时，传统的配电系统将从无源网变为
有源网。为提升对配电网中分布式光伏发电功率的
监测能力，基于变-线-台-户挂接关系实现网络拓扑
识别，追溯倒送功率在配电网中的分布情况，实现
分布式光伏接入电力系统的精准描绘，为不同拓扑
层级源荷预测、供需平衡、故障定位和集群调控等
提供智慧拓扑网图。 
随着数字孪生技术的兴起，给系统监测带来新
的思路[35]。通过布设大量传感器，精准感知物理电
网运行状态，并将其映射到数字空间生成虚拟电
网。虚拟电网和物理电网基本信息完全相同，同时
随物理电网的变化持续更新。通过对虚拟电网和物
理电网的联合监测，既可以实时掌握电网状态，又
能够尽早发现薄弱环节，保证高比例分布式光伏运
行安全性[36]。 
除在线监测以满足实时调控以外，同步考量多
时空、高精度的光伏发电预测，辅助电力电量平衡
调度和市场交易。现有研究多面向集中式新能源场
站[37]，运行信息和气象数据相对完备，但分布式光
伏预测面临单站预测成本高昂、气象监测数据缺失
等问题。经工程实践探索，在电网侧采用分层预测
或区域预测等方式对分布式光伏集群进行发电预
测。其中，分层预测是将光伏并网点按照智慧拓扑
网图进行追溯，实现电网拓扑多层级光伏汇聚、监
测(见图3)，利用NWP 气象资源网格化插值实现分
层聚类预测；区域预测是按光伏安装地理位置划
分，利用区域内集中式场站气象和预测数据，基于
统计升尺度实现行政区域内统一预测。考虑预测方
法的多样性，构建多时间尺度分布式光伏集群预测
评价指标，如式(1)—(3)，科学分析各种预测方法的
特点，以提高光伏预测精度。 
 
2
D
M
rmse
1
1
(
)
n
i
i
i
i
P
P
E
n
C




 
(1) 
 
mae
D
M
1
1
|
|
n
i
i
i
E
P
P
n




 
(2) 
 
R
rmse
(1
) 100%
C
E



 
(3) 
式中：Ermse 为均方根误差，表明预测偏差的相对情
况；Emae 为平均绝对偏差，表明预测偏差的数值大
小；CR 为预测精度；n 表示样本个数，可实现不同
时间尺度统计；PDi、PMi、Ci 分别表示i 时刻的实
际功率、预测功率和开机容量。 
0.4kV分布式光伏
分布式光伏
运行数据
调度管辖分
布式光伏
运营商分布
式光伏
用户侧分布
式光伏
气象资源类
运行数据
典型气象站
监测数据
数值天气
预报数据
0.4kV分布式光伏
10kV馈线汇集
10kV馈线汇集
10kV母线汇集
35kV母线汇集
110kV主变汇集110kV主变汇集
220kV主变聚合
分层汇集和监测
分层超短期
预测
分层短期预测
分层中长期
短期预测
概率预测及
置信区间
运行及预测
评价
分布式光伏
功率预测
调度
数据网
无线
专网
用采
转发
调度
数据网
E文本
接入
预测
结果
运行
数据
拓扑
信息
预报
数据
台账
数据
 
图3  分布式光伏集群分层预测思路 
Fig. 3  Hierarchical prediction ideas for  
distributed PV clusters 
当前工程实践中集中式光伏预测以物理方法
为主，但很难对全量分布式光伏构建精确单体物理
预测模型，应用局限性较大。在大数据技术加持下，
可采用数据驱动方法改善光伏预测质量。考虑站点
和气象的时空相关性，利用数据增强技术实现缺失
数据重构，为分布式光伏预测奠定基础[38]；对于具
有历史数据的站点，采用神经网络学习多因素之间
的复杂映射关系，提升光伏预测准确率[39]。



<!-- page 6/15 -->

第48 卷 第1 期 
电  网  技  术 
189 
经过大量探索和实践，分布式光伏规模化量测
已取得初步成效，但仍有很多地方须研究：1）拓
扑动态追溯。考虑分布式光伏以中低压配电网接入
为主，图模信息多处于繁琐无序和动态变化中，主
配网关联度弱，亟需突破全电压等级分布式光伏拓
扑动态拼接和自动追溯技术，构建“光伏并网地图
+电网一张图”。2）预测精度提升。一方面应开展
分布式气象监测装置优化配置，建立多方协同的预
测共享机制，完善数据资源获取途径，另一方面须
研究雾霾、雪灾、日食等极端或转折性天气对全域
光伏发电预测的量化影响，提高光伏预测鲁棒性。 
3.3  分布式光伏“可调”：多级协同与平衡调度 
技术 
新能源发电占比不断提升及其自身的随机性
和波动性导致传统电力电量平衡模式将难以适应
未来电力系统的发展需求[5]，因分布式发电引发的
峰谷差特性改变及保供挑战已不可忽略。新型电力
系统运行特性由传统大电网统一平衡模式逐步向
大电网与微电网协同、局部电网自平衡的模式转
变，系统调度运行模式将从“统调发电联合调度”
向“主配微网多级协同、源网荷储协调控制”转   
变[5]。系统不确定性因素愈加复杂、多变，传统的
优化调度模型已无法满足高比例分布式光伏电力
系统。为适应不同发展阶段、不同渗透率分布式光
伏并网运行，基于场景分析对不确定性因素进行建
模，即：将系统中不确定性因素作为随机变量纳入
模型中，观察和等待随机变量的实现进而进行决 
策[40]，如式(4)所示。 
 
min
(
)
s.t.
(
)
F
 f x
  g
g x
g







，
，
 
(4) 
式中：F 表示优化目标，一般为系统运行成本最小，
也可转化技术指标，如网损最小、新能源消纳最大
等，f 表示目标函数；g 代表不等式约束，g 和g 分
别为不等式约束的上下限；ξ 代表系统中不确定变
量，包括光伏、负荷等不确定性因素；x 表示传统
确定性电源决策变量，包括上游供电、可控机组等
确定性因素。 
伴随分布式光伏高渗透并网运行，系统调节能
力和设备支撑能力持续下降，构建新型平衡调度体
系成为调控运行升级的重点方向。新型平衡调度方
式应更注重电力系统的整体性、概率性和灵活性。
其中，整体性是在国-网-省协同调控的基础上进一
步实现省-地-县分层分区电力电量平衡，建立国-网
-省-地/县-集群纵向贯通的分布式光伏并网与运行
体系，在大电网层面进一步优化系统运行方式提升
消纳空间，在局部电网实现线路-台区-设备级分布
式资源内部优化、自平衡及自治愈，以“整体性”
视角满足大系统供需平衡、小系统自平衡及上下多
层级联动。 
概率性是通过概率建模和风险评估实现多重
不确定性的有效量化，以降低源荷双重不确定性造
成的失衡影响。考虑分布式光伏装机及发电占比不
断提升，构建含集中式和分布式的光伏发电预测置
信区间，采用场景、不确定集等方法描述相关因素
的不确定性，即在式(4)中将不同分布式光伏渗透率
所对应的不确定变量ξ 纳入风险量化的概率优化调
控模型，通过充裕性、安全性等指标对系统风险进
行分析评估，满足不同区域、不同发展阶段下分布
式光伏规模化并网对系统运行带来的影响。 
灵活性是指电力系统中资源在不同时间尺度
和不同方向上的供给能力相较于需求的充裕度水
平满足要求，即在满足安全性约束前提下通过灵活
性改造或增加灵活性资源扩大优化模型中约束条
件的上下限，灵活性平衡的概率形式[41]如式(5)所
示。与传统平衡方式不同的是，新型系统平衡调度
不再是源随荷动，而是源荷互动、源网荷储协同和
灵活性平衡；与已有系统灵活性评估不同的是，分
布式发电不仅对供给侧灵活性产生影响，同时对需
求侧灵活性带来变化，通过供给侧灵活性与需求侧
灵活性概率分布卷差计算[41]，进而获得系统灵活性
裕量概率分布和度量指标。在实践中，利用聚合商、
虚拟电厂等运行模式，横向汇集分布式可调节资源
并实现内部资源的最佳调度，纵向与集中式大电网
形成互补，充分挖掘广域源网荷储等灵活潜力，提
升系统充裕性和安全性。 
 
Pr(
)
Pr(
)
i
j
i S
j D
X
Y
X
Y









 
(5) 
式中：X 和Y 分别表示灵活性供给侧和需求侧的随
机变量；表示充裕度阈值，式(5)表明灵活性资源
供给能力小于灵活性需求的概率或风险低于给定
阈值；S 为供给侧灵活性资源的集合；Xi 表示第i
个资源的供给量；D 为需求侧灵活性资源的集合；
Yj 表示第j 个资源的需求量；Pr()表示求取概率。 
综上所述，新型电力系统平衡调度方式是在现
有集中式大电网电力电量平衡的基础上，进一步形
成考虑分布式资源参与的多时空、多级协同的概率
平衡模式，如图4 所示。 
随着市场化改革的深入，参与系统平衡调度的
分布式资源愈发丰富。多样化可调节资源通常隶属



<!-- page 7/15 -->

190 
栗峰等：新型电力系统下分布式光伏规模化并网运行关键技术探讨 
Vol. 48 No. 1 
中长期(月、年)
日前-日内
实时调控
国调
网调
省调
地调/
县调
集群/
微网等
场站/
设备
供需预测
运行方式
调峰分析
集群划分
信息上传
拓扑追溯
功率预测
分层协同
现货交易
超功率预测
检修计划
多场景模拟
可调汇集
ACE控制
电量预测
承载监测
省间互济
功率控制
集群控制
在线监测
调度策略
平衡调度
承载评估
受电计划
 
图4  分布式光伏参与系统调度的新型平衡调度方式 
Fig. 4  A new balance method for distributed PV 
participation in system scheduling 
不同主体，各个主体之间存在信息壁垒，想要实现
合作必须仰仗隐私保护技术[42]。利用区块链[43]、差
分隐私[44]、同态加密[45]、联邦学习[46]等方法，可为
多主体创造安全协同环境，以促进多灵活资源联合
调节，提升局域电力电量平衡水平。 
分布式光伏规模化并网推动平衡体系革新升
级，仍有不少问题待探讨：1）灵活资源储备。高
比例分布式光伏接入加剧了系统的不确定性，有必
要按科学比例对不同类型、不同功能的灵活资源进
行储备，提升电网调节能力，维护系统多维平衡。
2）时空平衡协调。时间尺度上，通过滚动时域优
化实现多时间尺度调度，以消减源荷预测误差；空
间尺度上，挖掘电动汽车等移动负荷潜力，提高局
部发用电匹配度，缓解网络阻塞问题。 
3.4  分布式光伏“可控”：聚合控制与自适应控制
技术 
在技术和市场驱动下，分布式光伏亟需突破如
何在弱可观、可测下实现安全、经济的可调、可控
难题。考虑到单个光伏场站调节能力有限，且可能
处于“全黑”状态，可基于集群思想，将同一馈线
或台变范围内分布式资源进行聚合，对外作为单个
主体接收调度指令，对内协调各个设备完成共同目
标，实现集群调节与协调控制，在平抑分布式光伏
发电不确定性的基础上进一步参与系统有功、无功
与紧急控制等支撑，具体技术模型如图5 所示。在
未来市场环境下，根据电网调峰调频辅助服务或
削峰填谷需求响应等信号，在满足系统安全约束
下分布式光伏实行自适应控制，实现综合效益最
大化。 
主动配电网中，大多数节点都接有大量分布式
光伏资源，为更好地管理和利用这些资源，首先对
其进行集群划分。文献[47]介绍了分布式发电集群
的概念，即地理和电气上接近或互补的多个分布式
资源构成的分布式发电集合。集群划分方法主要包
括聚类分析[48]、社团发现[49]等，这些方法综合考虑
分布式资源的输出特性和空间位置，实现分布式资
源集群的高效划分。以集群为主体，建立“主配协
同-群间协调-集群自律”的多层协调控制体系，对
外参与系统整体调度，一方面接受上级调度指令调
节有功/无功功率，增强电网灵活性，另一方面控制
逆变器模拟同步机提供惯量支撑，改善系统稳定
性；对内协调单元个体控制，采用一致性算法优化
多分布式资源有功功率分配，设计自适应策略实现
各分布式资源并网电压控制。 
然而，传统调控方法基于物理模型，建模及实
践均需要详细的系统参数，这对大规模分布式光伏
而言亦很难实现。因此，有专家学者将目光转向数
据驱动的强化学习[50]。强化学习是一种关注智能体
如何在不确定性环境中做出顺序决策以最大化累 
上层
下层
分布式光伏集群实时调度指令
电网承载力监测
及实时运行状态
设备实时监测及
运行状态
目标函数：系统运行成本最小
模型约束：潮流约束、支路功率约束、节点
电压约束、设备出力约束、集群出力约束等
分布式光伏集
群实时出力
分布式光伏集
群超短期预测
逆变器控制指令
目标函数：系统收益最大
模型约束：支路功率、节点电
压、光伏出力等约束
群内分布式光伏
实时出力评估
群内节点负荷需
求实时预测
局部电网实时优化控制模型
集群1群内优化分布式光伏功率分配模型
群间协调
集群N群内优化
分配模型
集群M群内优化分
配模型
逆变器控制指令
逆变器控制指令
群间协调
群间协调
 
图5  分布式光伏集群分层控制技术模型 
Fig. 5  Distributed PV cluster hierarchical control technology model



<!-- page 8/15 -->

第48 卷 第1 期 
电  网  技  术 
191 
 
积奖励的机器学习方法，其以历史数据为基础，在
离线条件下进行训练，通过反馈学习到最优策略，
进而应用到在线场景中。例如面临高比例分布式光
伏并网，强化学习能综合考虑多种不确定性因素，
为系统提供智能调度策略，实现电网在线实时能量
管理[51]。 
未来，当分布式光伏大规模参与系统调节和友
好支撑时，必然需要对分布式光伏的调节性能、发
电利用率和经济效益进行综合权衡，系统运行场景
更加复杂、受控对象更多、不确定性更强，整体目
标达成困难，应当进一步深化：1）多参数表征。
聚合以分布式光伏为代表的分布式资源，详细分析
各类资源运行特性，采用统一化方法描述其功能参
数，提升集群的容量备用、削峰填谷、惯量支撑等
能力。2）多方法融合。随着电力系统不确定性程
度增大，单一方法适应性逐渐下降，应结合机理分
析与数据驱动方法，综合多种人工智能方法，更好
解决高比例分布式光伏配电网调控难题。 
4  新型分布式光伏并网运行标准体系 
在分布式光伏规模化并网的趋势下，新型电力
系统标准体系建设应聚焦在加强分布式光伏并网
友好性、提升新能源电力系统智能调控水平、促进
分布式电力交易和市场化运营等方面，以期促进系
统安全稳定运行和分布式光伏健康高质量发展。 
4.1  我国分布式光伏并网运行标准现状及问题 
经过十余年的发展，我国初步建立了分布式光
伏标准体系(如图6 所示)，发布与并网运行相关的
国际标准、国家标准及行业标准等40 余项(代表性
标准见附录A 表A2)，基本解决并网周期长、投资
成本高等问题。近年来，分布式光伏标准化工作快
速发展，其重点任务是解决分布式光伏涉网性能
弱、发电调控难等问题。如GB 38755—2019《电力 
分布
式光
伏现
行标
准体
系
通用与基础
技术要求
规划与设计
施工与建设
并网与运行
设备与检测
其他技术管理
并网测试
运行控制
通信保护
评估管理
 
图6  我国现行分布式光伏标准体系 
Fig. 6  Current distributed PV standard system in China 
系统安全稳定导则》规定35kV 并网的分布式电源
应具备快速调压、调峰和一次调频能力，对于系统
电压、频率的波动应具有一定的耐受能力；
GB/T29319—2012《光伏发电系统接入配电网技术
规定》要求10kV 及以下电压等级且三相并网的光
伏发电系统应具备参与电力系统调频、调峰、调压、
故障穿越、功率预测、电压及频率适应性等能力。 
与集中式光伏相比，分布式光伏并网运行标准
主要存在以下不足：1）受修订周期等因素影响，
不同标准内技术指标存在差异；2）过去分布式光
伏发电量占负荷比重较低，技术和管理重视程度不
够，标准制定进程缓慢；3）当前面向低压分布式
光伏的技术标准和条款内容较少，多参考中高电压
等级，常出现入网检测成本高、系统支撑手段弱和
管理权责不够明晰等现象。 
4.2  国外分布式光伏并网运行标准借鉴 
1）国际组织标准。IEEE 1547 是最早设计和发
布分布式发电并网的标准，涵盖分布式电源测试、
通信、监测和控制等技术要求；IEEE 1547—2018《分
布式能源与电力系统相关接口的互联互通要求》修
订后增加无功功率/电压调节、有功功率控制/频率异
常响应、电压穿越等支撑功能；IEC/TS 62786—2017
《分布式能源与电网的连接》规定分布式电源接入
配电网设计、运行和连接的原则和技术要求；正处
在草案制定期的IEC/TS 63276《配电网接纳分布式
电源承载力评估导则》拟规定电网接纳分布式电源
承载力的运行及评估等技术要求。 
2）典型国家标准。德国要求分布式光伏中压
接入满足VDE-AR-N 4110—2018《发电系统接入中
压电网并网技术要求》，低压接入满足VDE-AR-N 
4105—2018《发电系统接入低压电网并网规范》，
具体而言，分布式光伏在故障穿越能力方面要具备
低电压穿越能力，并满足高电压穿越要求；在频率
适应性方面能实现有功-频率响应；在电压适应性方
面拥有一定无功-电压调节范围。英国BS EN 50438
—2007《微型发电机与公共低压配电网并联连接的
要求》分别对20kV 以下并网且不超过5MW 和
5MW 以上的分布式电源并网提出安全运行、继电
保护、电能质量等初步技术要求；BS EN 50549-1
—2019《发电厂与低压配电网并联的要求》和BS 
EN 50549-2—2019《发电厂与中压配电网并联的要
求》分别对B 型及以下的发电厂接入低压和中压配
电网提出具体并网要求，其中中压部分明确了分布
式电源频率抗扰性和电压抗扰性、主动频率响应、
无功控制模式等技术规定。在“89”大停电事故之



<!-- page 9/15 -->

192 
栗峰等：新型电力系统下分布式光伏规模化并网运行关键技术探讨 
Vol. 48 No. 1 
后，英国将进一步完善分布式电源并网适应性、孤
岛保护等技术要求[52]。 
与国外相比，我国分布式光伏并网运行标准在
功率控制、故障穿越、耐频/耐压适应性等方面的要
求与国际组织标准整体相近，但普遍低于以德国、
英国为代表的国家标准，且在数据校核与订正、集
群预测与控制、风险防控与预警、市场交易与运营
等方面存在一定缺失。 
4.3  分布式光伏规模化并网运行标准体系构建 
考虑到分布式光伏接入位置及容量不同，在大
型工商业等屋顶加装分布式光伏多采用35kV 或
10(6)kV 接入电网，在小型工商业、党政机关、学
校、医院等公共建筑屋顶加装分布式光伏多采用380V
接入电网，在居民屋顶加装分布式光伏多采用220V
接入电网。综合考虑国内外分布式光伏并网运行技术
与管理特性，可将分布式光伏划分为A、B 两类。 
A类分布式光伏：通过35kV并网，以及10(6)kV
直接接入公共电网；B 类分布式光伏：通过10(6)kV 
接入用户侧，以及380/220V 并网。以GB/T33592
— 2017 《分布式电源并网运行控制规范》和
GB/T33593—2017《分布式电源并网技术要求》为
例，并网运行技术要求见附录A 表A3。为适应新
型电力系统运行特性，A 类分布式光伏应进一步提
升一次调频、快速调压、主动调峰、耐频耐压等能
力；B 类分布式光伏须弥补信息集成和安全传输、
集群预测和集群控制等标准空白，并逐步向A 类靠
拢；电网应推进调度管理、运行消纳、监测预警等
技术标准修订；监管部门应牵头制定分布式光伏市
场化交易等管理规范。 
为适应新型电力系统发展需求，详细分析现行
分布式光伏标准与国外标准及工程实践的差距，建
议构建涵盖“整县开发”“沐光行动”等促进产业
规范发展的新型分布式光伏并网运行标准体系，如
图7 结构树所示，以满足电网安全、调控运行和市
场化交易等需求。 
新型电力系统下分布式光伏并网运行标准体系
涉网提升
监测预测
调度运行
控制保护
评估预警
信息接入
市场运营
分
布
式
光
伏
接
入
配
电
网
技
术
规
范
分
布
式
光
伏
信
息
接
入
与
集
成
技
术
分
布
式
光
伏
并
网
安
全
防
护
技
术
分
布
式
光
伏
接
入
配
网
涉
网
测
试
要
求
分
布
式
光
伏
电
站
故
障
穿
越
检
测
技
术
分
布
式
光
伏
接
入
电
网
调
试
与
验
收
分
布
式
光
伏
接
入
配
电
网
监
控
技
术
分
布
式
光
伏
发
电
功
率
预
测
及
评
价
分
布
式
光
伏
数
据
质
量
核
查
与
订
正
分
布
式
光
伏
发
电
调
度
运
行
管
理
规
定
分
布
式
光
伏
集
群
预
测
与
控
制
技
术
分
布
式
光
伏
厂
网
双
向
互
动
技
术
规
范
分
布
式
发
电
系
统
建
模
与
并
网
仿
真
分
布
式
光
伏
接
入
配
电
网
运
行
控
制
分
布
式
光
伏
继
电
保
护
与
安
全
自
动
装
置
分
布
式
光
伏
接
入
电
网
承
载
力
评
估
分
布
式
光
伏
并
网
风
险
防
控
预
警
技
术
分
布
式
光
伏
电
站
运
行
指
标
与
评
估
分
布
式
光
伏
市
场
化
价
格
机
制
规
范
分
布
式
光
伏
市
场
化
运
营
机
制
设
计
面
向
分
布
式
主
体
的
交
易
平
台
建
设
 
图7  新型分布式光伏并网运行标准体系结构树 
Fig. 7  New distributed PV grid-connected operation standard system structure tree 
5  分布式光伏并网运行典型经验启示与发
展建议 
5.1  国外大规模分布式光伏并网运行经验启示 
为加速能源低碳转型，很多国家在配用侧接入
大量分布式光伏，不少地区人均光伏已超过1kW，
率先实现高渗透率分布式发电并网和运行。这些国
家在并网协同、运行服务及市场交易等方面积累了
丰富经验，可为我国工程实践以启迪。 
在并网协同上，意大利探索“光伏+储能”“光
伏+热泵”“光伏+电动汽车”等模式以深挖分布式
光伏并网潜力[53]；德国光伏发展迅猛，住宅、车站
的屋顶及大桥、公路的两侧都可安装并网分布式光
伏[54]；瑞士计划利用光伏取代核电，大力发展光伏
建筑一体化[53]；瑞士基于地理信息系统构建“光伏
地图”，为用户提供光伏资源测算、并网分析及电
量评估等支撑[53]；瑞典建设诸多零能耗建筑，利用
分布式光伏和太阳能集热满足用户的用能需求[55]。 
在运行服务上，德国分布式光伏大规模运行过
程中产生电压升高、设备过载、系统平衡和频率安
全等问题，利用扩建中低压电网和改善系统灵活性
实现光伏承载力的提升[56]；美国利用图神经网络捕
捉相邻分布式光伏的时空相关性，提升分布式光伏
数据质量和预测精度[57]；澳大利亚高比例分布式光
伏配电网运行过程中出现电压大幅波动、潮流极易
反向和系统难以稳定等现象，通过完善标准体系和



<!-- page 10/15 -->

第48 卷 第1 期 
电  网  技  术 
193 
发展虚拟电厂降低分布式光伏带来的影响[58]。 
在市场交易上，德国通过组建平衡集群基团，
在内部供需无法平衡时逐步向上一层级购买平衡
服务[56]；澳大利亚大力建设光储虚拟电厂，积极推
动虚拟电厂参与电力市场频率控制辅助服务[59]；斯
洛文尼亚实施净计量政策，鼓励用户配置分布式光
伏，确保光伏就地或就近利用[60]；奥地利推出支持
居民P2P 电力交易的能源社区，帮助用户节省电费
的同时也提高清洁能源利用率[60]。 
5.2  新型电力系统下分布式光伏并网运行发展建议 
在我国，分布式光伏规模化发展和并网是构建
以“安全高效、清洁低碳、柔性灵活、智慧融合”
为特征的新型电力系统的重要组成部分，未来仍将
持续高速发展。与此同时，大规模分布式光伏接入
会对电网安全造成极大影响，系统调度运行将迎来
重大变革。通过上述理论、技术及标准剖析，融合
国外先进经验，归纳形成如下建议： 
1）加强分布式资源并网协同，提升用户侧灵
活调节能力。 
加强分布式光伏与储能、电动汽车、可控负荷
等协同技术研究和应用实践，促进多种分布式资源
能量互补与协调控制；因地制宜分析分布式光伏与
储能配置比例关系，创新储能运营模式以实现分布
式发电集群优化调度；推动分布式光伏与储能等灵
活性资源聚合调控技术及管理模式，发展多样化隐
私保护技术，营造多主体安全协同环境，激励多资
源共同调节，增强系统灵活性；研究云边协同的多
类型、多尺度数据融合技术，实现分布式光伏高质
量可观可测；攻关兼顾可靠性与经济性的分布式光
伏频率、电压友好支撑技术，进一步提升分布式光
伏涉网性能。 
2）优化电网运行服务，增强系统调控水平和
广域平衡能力。 
滚动评估分布式光伏规模化并网对系统安全
经济运行的影响，优化电网调节方式，提升分布式
光伏接纳能力；构建贯穿国-网-省-地-县/集群的分
布式光伏调度运行框架，推动系统调度管理模式向
自下而上的分层集群聚合模式转变；研究含高比例
分布式光伏的电力系统绿色低碳调度方法和风险
防控预警技术，以台区为单元实现局部电网的自平
衡与分布式资源的统一调度；借用数字技术挖掘分
布式光伏融入电网的信息-物理特征，结合仿真技术
将物理实体映射到虚拟空间，打造数字孪生电网，
提升调度运行多场景模拟推演能力；依托人工智能
技术将现行调控模式转变为模型-数据混合驱动，充
分利用现有数据资源，促进电网调控智慧升级。 
3）推动分布式光伏参与市场交易，促进绿色
发展和效益提升。 
健全新能源发电市场机制，分析分布式光伏场
站与集中式新能源、常规机组的市场关系，完善其
与常规机组深度调峰的补偿机制，合理疏导分布式
发电带来的系统成本提升；鼓励清洁能源优先发
电，探索分布式光伏参与绿电、绿证交易机制，逐
步将分布式光伏纳入碳排放权交易市场范畴；建立
分布式发电市场化交易平台，促进分布式光伏参与
中长期、现货等市场交易，鼓励分布式光伏提供调
频、备用、无功等辅助服务。 
6  结论 
分布式光伏逐步成为我国如期实现双碳目标
和落实乡村振兴战略的重要力量，如何以技术驱动
促进提质降本、引导分布式光伏有序并网和高效消
纳，是当前重点和热点内容之一。为此，本文结合
最新研究动态，从工程角度探讨了分布式光伏规模
化并网运行关键技术，得出以下结论： 
1）分布式光伏规模化并网趋势明显，给系统
运行带来重大挑战。目前我国分布式光伏发展迅
猛，支持政策层出不穷，并网方式逐渐从分散式并
网过渡到规模化并网，随之也出现多种运行模式，
然而高比例分布式光伏接入会给电力系统带来诸
多问题，同时也会制约分布式光伏发展进程。 
2）分布式光伏规模化并网促使电力系统调控
模式革新升级。结合电网业务和场站运行需求，从
多个方面探讨新形势下电网调度运行关键技术，助
力构建适应大规模分布式光伏并网、保障系统安全
稳定运行的先进电网能量管理体系，提升新型电力
系统分层分群平衡能力及新能源消纳水平。 
3）分布式光伏规模化并网运行对标准体系构
建提出迫切要求。充分借鉴国外先进经验，建立涵
盖信息接入、涉网提升、监测预测、调度运行、控
制保护、评估预警及市场运营等环节的标准体系架
构，期望推动分布式光伏规范化发展、促进电网安
全稳定经济运行。 
附录见本刊网络版(http://www.dwjs.com.cn/CN/1000- 
3673/current.shtml)。 
参考文献 
[1] 
梁志峰，夏俊荣，孙檬檬，等．数据驱动的配电网分布式光伏承
载力评估技术研究[J]．电网技术，2020，44(7)：2430-2438． 
LIANG Zhifeng，XIA Junrong，SUN Mengmeng，et al．Data driven 
assessment of distributed photovoltaic hosting capacity in distribution



<!-- page 11/15 -->

194 
栗峰等：新型电力系统下分布式光伏规模化并网运行关键技术探讨 
Vol. 48 No. 1 
network[J]．Power System Technology，2020，44(7)：2430-2438(in 
Chinese) ． 
[2] 
薛金花，叶季蕾，陶琼，等．面向不同投资主体的分布式光伏运
营策略研究[J]．电网技术，2017，41(1)：93-98． 
XUE Jinhua，YE Jilei，TAO Qiong，et al．Operating strategy of 
distributed PV system for different investors[J] ．Power System 
Technology，2017，41(1)：93-98(in Chinese) ． 
[3] 
许晓艳，黄越辉，刘纯，等．分布式光伏发电对配电网电压的影
响及电压越限的解决方案[J]．电网技术，2010，34(10)：140-146． 
XU Xiaoyan，HUANG Yuehui，LIU Chun，et al． Influence of 
distributed photovoltaic generation on voltage in distribution network 
and solution of voltage beyond limits s[J]．Power System Technology，
2010，34(10)：140-146(in Chinese) ． 
[4] 
卓振宇，张宁，谢小荣，等．高比例可再生能源电力系统关键技
术及发展挑战[J]．电力系统自动化，2021，45(9)：171-191． 
ZHUO Zhenyu，ZHANG Ning，XIE Xiaorong，et al．Key technologies 
and developing challenges of power system with high proportion of 
renewable energy[J]．Automation of Electric Power Systems，2021，
45(9)：171-191(in Chinese)． 
[5] 
张智刚，康重庆．碳中和目标下构建新型电力系统的挑战与展望
[J]．中国电机工程学报，2022，42(8)：2806-2819． 
ZHANG Zhigang，KANG Chongqing．Challenges and prospects for 
constructing the new-type power system towards a carbon neutrality 
future[J]．Proceedings of the CSEE，2022，42(8)：2806-2819(in 
Chinese)． 
[6] 
谢小荣，贺静波，毛航银，等．“双高”电力系统稳定性的新问
题及分类探讨[J]．中国电机工程学报，2021，41(2)：461-475． 
XIE Xiaorong，HE Jingbo，MAO Hangyin，et al．New issues and 
classification of power system stability with high shares of renewables 
and power electronics[J]．Proceedings of the CSEE，2021，41(2)：
461-475(in Chinese)． 
[7] 
李明节，陈国平，董存，等．新能源电力系统电力电量平衡问题
研究[J]．电网技术，2019，43(11)：3979-3986． 
LI Mingjie，CHEN Guoping，DONG Cun，et al．Research on power 
balance of high proportion renewable energy system[J]．Power 
System Technology，2019，43(11)：3979-3986(in Chinese)． 
[8] 
GHADI M J，GHAVIDEL S，RAJABI A，et al．A review on economic 
and technical operation of active distribution systems[J]．Renewable 
and Sustainable Energy Reviews，2019，104：38-53． 
[9] 
张晶，胡纯瑾，高志远，等．能源互联网技术标准体系架构设计
及需求分析[J]．电网技术，2022，46(8)：3038-3048． 
ZHANG Jing，HU Chunjin，GAO Zhiyuan，et al．Architecture design 
and requirement analysis of technical standard system for energy 
internet[J]．Power System Technology，2022，46(8)：3038-3048(in 
Chinese)． 
[10] 国家能源局．我国光伏发电并网装机容量突破3 亿千瓦分布式发
展成为新亮点[EB/OL]．(2022-01-20)[2023-02-16]．http://www.nea. 
gov.cn/2022-01/20/c_1310432517.htm． 
[11] 三十一省“十四五”光伏装机目标超390GW[EB/OL]．(2023-01-28) 
[2023-02-09]．https://mp.weixin.qq.com/s/KeFSgaOv7ImG3-k0tF 
dwvw． 
[12] 2022-2028 年中国分布式光伏行业市场现状分析及发展前景展望
报告[R]．北京：智研咨询，2022． 
[13] JIRDEHI M A，TABAR V S，GHASSEMZADEH S，et al．Different 
aspects of microgrid management：A comprehensive review[J]．
Journal of Energy Storage，2020，30：101457． 
[14] HU Junjie，ZHOU Huayanran，LI Yang，et al．Multi-time scale energy 
management strategy of aggregator characterized by photovoltaic 
generation and electric vehicles[J]．Journal of Modern Power Systems 
and Clean Energy，2020，8(4)：727-736． 
[15] ROUZBAHANI H M，KARIMIPOUR H，LEI Lei．A review on 
virtual power plant for energy management[J]．Sustainable Energy 
Technologies and Assessments，2021，47：101370． 
[16] GUELPA E ，BISCHI A，VERDA V ，et al ．Towards future 
infrastructures for sustainable multi-energy systems：A review[J]．
Energy，2019，184：2-21． 
[17] 戚艳，刘敦楠，徐尔丰，等．面向园区能源互联网的综合能源服
务关键问题及展望[J]．电力建设，2019，40(1)：123-132． 
QI Yan，LIU Dunnan，XU Erfeng，et al．Key issues and prospects of 
integrated energy service for energy internet in park[J]．Electric Power 
Construction，2019，40(1)：123-132(in Chinese)． 
[18] 朱彦名，徐潇源，严正，等．面向电力物联网的含可再生能源配
电网运行展望[J]．电力系统保护与控制，2022，50(2)：176-187． 
ZHU Yanming，XU Xiaoyuan，YAN Zheng，et al．Prospect of 
renewable energy integrated distribution network operation in the 
power internet of things[J]．Power System Protection and Control，
2022，50(2)：176-187(in Chinese)． 
[19] 李鹏，习伟，蔡田田，等．数字电网的理念、架构与关键技术[J]．
中国电机工程学报，2022，42(14)：5002-5016． 
LI Peng，XI Wei，CAI Tiantian，et al．Concept，architecture and key 
technologies of digital power grids[J]．Proceedings of the CSEE，2022，
42(14)：5002-5016(in Chinese)． 
[20] AHMED R，SREERAM V，MISHRA Y，et al．A review and 
evaluation of the state-of-the-art in PV solar power forecasting：
Techniques and optimization[J]．Renewable and Sustainable Energy 
Reviews，2020，124：109792． 
[21] IMPRAM S，NESE S V，ORAL B．Challenges of renewable energy 
penetration on power system flexibility：A survey[J]．Energy Strategy 
Reviews，2020，31：100539． 
[22] 汪梦军，郭剑波，马士聪，等．新能源电力系统暂态频率稳定分
析与调频控制方法综述[J]．中国电机工程学报，2023，43(5)：
1672-1693． 
WANG Mengjun，GUO Jianbo，MA Shicong，et al．Review of 
transient frequency stability analysis and frequency regulation control 
methods for renewable power systems[J]．Proceedings of the CSEE，
2023，43(5)：1672-1693(in Chinese)． 
[23] 孙华东，许涛，郭强，等．英国“89”大停电事故分析及对中国
电网的启示[J]．中国电机工程学报，2019，39(21)：6183-6191． 
SUN Huadong，XU Tao，GUO Qiang，et al．Analysis on blackout in 
Great Britain power grid on August 9th，2019 and its enlightenment to 
power grid in China[J]．Proceedings of the CSEE，2019，39(21)：
6183-6191(in Chinese)． 
[24] 刘文龙，吕志鹏，刘海涛．电力电子化配电台区形态发展以及运
行控制技术综述[J]．中国电机工程学报，2023，43(13)：4899-4921． 
LIU Wenlong ，LÜ Zhipeng ，LIU Haitao ．An overview of 
morphological development and operation control technology of 
power electronics dominated distribution area[J]．Proceedings of the 
CSEE，2023，43(13)：4899-4921(in Chinese)． 
[25] 陈皓勇，谭碧飞，伍亮，等．分层集群的新型电力系统运行与控
制[J]．中国电机工程学报，2023，43(2)：581-594． 
CHEN Haoyong，TAN Bifei，WU Liang，et al．Operation and control 
of the new power systems based on hierarchical clusters[J] ．
Proceedings of the CSEE，2023，43(2)：581-594(in Chinese)． 
[26] WANG Yi，CHEN Qixin，HONG Tao，et al．Review of smart meter 
data analytics：Applications，methodologies，and challenges[J]．IEEE 
Transactions on Smart Grid，2019，10(3)：3125-3148． 
[27] 李立浧，蔡泽祥，唐文虎，等．透明电网理论框架与关键技术[J]．
中国工程科学，2022，24(4)：32-43． 
LI Licheng，CAI Zexiang，TANG Wenhu，et al．Theoretical 
framework and key technologies of transparent power grid[J]．



<!-- page 12/15 -->

第48 卷 第1 期 
电  网  技  术 
195 
Strategic Study of CAE，2022，24(4)：32-43(in Chinese)． 
[28] 白昱阳，黄彦浩，陈思远，等．云边智能：电力系统运行控制的
边缘计算方法及其应用现状与展望[J]．自动化学报，2020，46(3)：
397-410． 
BAI Yuyang，HUANG Yanhao，CHEN Siyuan，et al．Cloud-edge 
intelligence：Status quo and future prospective of edge computing 
approaches and applications in power system operation and control[J]．
Acta Automatica Sinica，2020，46(3)：397-410(in Chinese)． 
[29]  姚小龙．分布式光伏发电全气象系统及区域出力预测方法研究
[D]．杭州：浙江工业大学，2019． 
[30] 刘林，祁兵，李彬，等．面向电力物联网新业务的电力通信网需
求及发展趋势[J]．电网技术，2020，44(8)：3114-3128． 
LIU Lin，QI Bing，LI Bin，et al．Requirements and developing trends 
of electric power communication network for new services in electric 
internet of things[J]．Power System Technology，2020，44(8)：
3114-3128(in Chinese)． 
[31] GE Leijiao，DU Tianshuo，LI Changlu，et al．Virtual collection for 
distributed photovoltaic data ：Challenges ，methodologies ，and 
applications[J]．Energies，2022，15(23)：8783． 
[32] 张宁，杨经纬，王毅，等．面向泛在电力物联网的5G 通信：技术
原理与典型应用[J]．中国电机工程学报，2019，39(14)：4015-4024． 
ZHANG Ning，YANG Jingwei，WANG Yi，et al．5G communication 
for the ubiquitous internet of things in electricity：Technical principles 
and typical applications[J]．Proceedings of the CSEE，2019，39(14)：
4015-4024(in Chinese)． 
[33] 孙名扬，于芳，赵家庆，等．新一代调控系统一体化运维架构及
关键技术[J]．电力系统自动化，2019，43(22)：217-223． 
SUN Mingyang，YU Fang，ZHAO Jiaqing，et al．Integrated 
operation/maintenance architecture and key technologies of new 
generation dispatching and control system[J]．Automation of Electric 
Power Systems，2019，43(22)：217-223(in Chinese)． 
[34] 赵波，肖传亮，徐琛，等．基于渗透率的区域配电网分布式光伏
并网消纳能力分析[J]．电力系统自动化，2017，41(21)：105-111． 
ZHAO Bo，XIAO Chuanliang，XU Chen，et al．Penetration based 
accommodation capacity analysis on distributed photovoltaic 
connection in regional distribution network[J]．Automation of Electric 
Power Systems，2017，41(21)：105-111(in Chinese)． 
[35] 赵鹏，蒲天骄，王新迎，等．面向能源互联网数字孪生的电力物
联网关键技术及展望[J]．中国电机工程学报，2022，42(2)：447-457． 
ZHAO Peng，PU Tianjiao，WANG Xinying，et al．Key technologies 
and perspectives of power internet of things facing with digital twins 
of the Energy Internet[J]．Proceedings of the CSEE，2022，42(2)：
447-457(in Chinese)． 
[36] 杜晓东，赵建利，刘科研，等．基于数字孪生的光伏高比例配电
网过载风险预警方法[J]．电力系统保护与控制，2022，50(9)：136- 
144． 
DU Xiaodong，ZHAO Jianli，LIU Keyan，et al．Digital twin early 
warning method study for overload risk of distribution network with a 
high proportion of photovoltaic access[J]．Power System Protection 
and Control，2022，50(9)：136-144(in Chinese)． 
[37] 赖昌伟，黎静华，陈博，等．光伏发电出力预测技术研究综述[J]．
电工技术学报，2019，34(6)：1201-1217． 
LAI Changwei，LI Jinghua，CHEN Bo，et al．Review of photovoltaic 
power output prediction technology[J] ．Transactions of China 
Electrotechnical Society，2019，34(6)：1201-1217(in Chinese)． 
[38] 乔颖，孙荣富，丁然，等．基于数据增强的分布式光伏电站群短
期功率预测(一)：方法框架与数据增强[J]．电网技术，2021，45(5)：
1799-1808． 
QIAO Ying，SUN Rongfu，DING Ran，et al．Distributed photovoltaic 
station cluster gridding short-term power forecasting part I ：
Methodology and data augmentation[J]．Power System Technology，
2021，45(5)：1799-1808(in Chinese)． 
[39] SIMEUNOVIĆ J，SCHUBNEL B，ALET P J，et al．Spatio-temporal 
graph neural networks for multi-site PV power forecasting[J]．IEEE 
Transactions on Sustainable Energy，2022，13(2)：1210-1220． 
[40] 黎静华，谢育天，曾鸿宇，等．不确定优化调度研究综述及其在
新型电力系统中的应用探讨[J]．高电压技术，2022，48(9)：3447- 
3464． 
LI Jinghua，XIE Yutian，ZENG Hongyu，et al．Research review of 
uncertain optimal scheduling and its application in new-type power 
systems[J]．High Voltage Engineering，2022，48(9)：3447-3464 (in 
Chinese)． 
[41] 鲁宗相，李海波，乔颖．高比例可再生能源并网的电力系统灵活
性评价与平衡机理[J]．中国电机工程学报，2017，37(1)：9-20． 
LU Zongxiang，LI Haibo，QIAO Ying．Flexibility evaluation and 
supply/demand balance principle of power system with high-penetration 
renewable electricity[J]．Proceedings of the CSEE，2017，37(1)：
9-20(in Chinese)． 
[42] 郭庆来，田年丰，孙宏斌．支撑能源互联网协同优化的隐私计算
关键技术[J]．电力系统自动化，2023，47(8)：2-14． 
GUO Qinglai，TIAN Nianfeng，SUN Hongbin．Key technologies of 
privacy computation supporting collaborative optimization of Energy 
Internet[J]．Automation of Electric Power Systems，2023，47(8)：
2-14(in Chinese)． 
[43] 单俊嘉，董子明，胡俊杰，等．基于区块链技术的产消者P2P 电
能智能交易合约[J]．电网技术，2021，45(10)：3830-3839． 
SHAN Junjia，DONG Ziming，HU Junjie，et al．P2P smart power 
trading contract based on blockchain technology[J]．Power System 
Technology，2021，45(10)：3830-3839(in Chinese)． 
[44] ZHAO Daduan，ZHANG Chenghui，CAO Xiangyang，et al．
Differential privacy energy management for islanded microgrids with 
distributed consensus-based ADMM algorithm[J]．IEEE Transactions 
on Control Systems Technology，2023，31(3)：1018-1031． 
[45] CHENG Zheyuan，YE Feng，CAO Xianghui，et al．A homomorphic 
encryption-based private collaborative distributed energy management 
system[J]．IEEE Transactions on Smart Grid，2021，12(6)：5233-5243． 
[46] 周毅斌，肖浩，裴玮，等．基于纵向联邦学习的微电网群协同优
化运行与策略进化[J]．电力系统自动化，2023，47(11)：121-132． 
ZHOU Yibin，XIAO Hao，PEI Wei，et al．Collaborative optimization 
operation and strategy evolution of microgrid cluster based on vertical 
federated learning[J]．Automation of Electric Power Systems，2023，
47(11)：121-132(in Chinese)． 
[47] 盛万兴，吴鸣，季宇，等．分布式可再生能源发电集群并网消纳
关键技术及工程实践[J]．中国电机工程学报，2019，39(8)：2175- 
2186． 
SHENG Wanxing，WU Ming，JI Yu，et al．Key techniques and 
engineering practice of distributed renewable generation clusters 
integration[J]．Proceedings of the CSEE，2019，39(8)：2175-2186(in 
Chinese)． 
[48] DING Jinjin，ZHANG Qian，HU Shijun，et al．Clusters partition and 
zonal voltage regulation for distribution networks with high 
penetration of PVs[J]．IET Generation，Transmission & Distribution，
2018，12(22)：6041-6051． 
[49] ZHAO Bo，XU Zhicheng，XU Chen，et al．Network partition-based 
zonal voltage control for distribution networks with distributed PV 
systems[J]．IEEE Transactions on Smart Grid，2018，9(5)：4087-4098． 
[50] 毕聪博，唐聿劼，罗永红，等．电力系统优化控制中强化学习方
法应用及挑战[J/OL]．中国电机工程学报：1-24[2023-03-28]．
https://doi.org/10.13334/j.0258-8013.pcsee.223433． 
BI Congbo，TANG Yujie，LUO Yonghong，et al．Review on critical



<!-- page 13/15 -->

196 
栗峰等：新型电力系统下分布式光伏规模化并网运行关键技术探讨 
Vol. 48 No. 1 
problems in reinforcement learning methods applied in power system 
optimization and control scenarios[J/OL]．Proceedings of the CSEE：
1-24[2023-03-28]．https://doi.org/10.13334/j.0258-8013.pcsee. 
223433(in Chinese)． 
[51] WANG Shengyi ，DU Liang ，FAN Xiaoyuan ，et al ．Deep 
reinforcement scheduling of energy storage systems for real-time 
voltage regulation in unbalanced LV networks with high PV 
penetration[J]．IEEE Transactions on Sustainable Energy，2021，12(4)：
2342-2352． 
[52] 方勇杰．英国“89”停电事故对频率稳定控制技术的启示[J]．电
力系统自动化，2019，43(24)：1-5． 
FANG Yongjie．Reflections on frequency stability control technology 
based on the blackout event of 9 August 2019 in UK[J]．Automation 
of Electric Power Systems，2019，43(24)：1-5(in Chinese)． 
[53] 碳中和目标下欧洲和中国需要装多少光伏?[EB/OL]．(2021-02- 
01)[2022-11-05]．https://mp.weixin.qq.com/s/49uEdr27wWHFN6TR- 
aXZ_w． 
[54] 碳中和论坛|德国2050 光伏发展情景(战略篇)[EB/OL]．(2021-08- 
09)[2022-11-05]．https://mp.weixin.qq.com/s/vsIelrmb9bEr5UEd5 
te_SA． 
[55] 原创文章|瑞典零能耗建筑实地考察与分析[EB/OL]．(2020-12-02) 
[2022-11-05]．https://mp.weixin.qq.com/s/_0Ro1buj3TRUJFNA8V0 
DCg． 
[56] 德国光伏发展启示[EB/OL]．(2018-03-09)[2022-11-05]．https://mp. 
weixin.qq.com/s/ybzCBMzY85Gh52H7DhgH6Q． 
[57] 李亦言，胡荣兴，宋立冬，等．机器学习在智能配用电领域中的
应用：北美工程实践概述[J]．电力系统自动化，2021，45(16)：99-113． 
LI Yiyan，HU Rongxing，SONG Lidong，et al．Application of machine 
learning in field of smart power distribution and utilization：Overview 
of engineering practice in North America[J]．Automation of Electric 
Power Systems，2021，45(16)：99-113(in Chinese)． 
[58] STRINGER N，BRUCE A，MACGILL I，et al．Consumer-led 
transition ：Australia's world-leading distributed energy resource 
integration efforts[J]．IEEE Power and Energy Magazine，2020，18(6)：
20-36． 
[59] 李嘉媚，艾芊，殷爽睿．虚拟电厂参与调峰调频服务的市场机制
与国外经验借鉴[J]．中国电机工程学报，2022，42(1)：37-55． 
LI Jiamei，AI Qian，YIN Shuangrui．Market mechanism and foreign 
experience of virtual power plant participating in peak-regulation and 
frequency-regulation[J]．Proceedings of the CSEE，2022，42(1)：
37-55(in Chinese)． 
[60] 直播课件分享|浅议-奥地利和斯洛文尼亚的光伏市场发展及对中
国的启示[EB/OL]．(2020-12-14)[2022-11-05]．https://mp.weixin. 
qq.com/s/8APTrYMUZl_-bsl8L3Czjg． 
 
 
在线出版日期：2023-07-03。 
收稿日期：2023-05-09。 
作者简介： 
栗峰(1989)，男，工程师，研究方向为新型电
力系统战略、分布式发电调度运行，E-mail：lifeng@
epri.sgcc.com.cn； 
丁杰(1962)，男，研究员级高级工程师，研究
方向为水电及新能源调度运行与控制，E-mail：
dingjie@epri.sgcc.com.cn； 
周才期(1987)，男，高级工程师，研究方向为
水电及新能源调度运行与控制，E-mail：zhoucaiqi@
sgcc.com.cn； 
雍维桢(1996)，男，通信作者，博士研究生，
研究方向为水-能耦合系统优化调度、用户侧能量
管理，E-mail：yongweizhen@stu.xjtu.edu.cn； 
黄越辉(1979)，女，教授级高级工程师，研究
方向为新能源并网及调度运行技术，E-mail：
huangyh@epri.sgcc.com.cn； 
王建学(1976)，男，教授，博士生导师，研究
方向为电力系统规划与运行、电力市场与用能侧运
营，E-mail：jxwang@mail.xjtu.edu.cn； 
许晓慧(1981)，男，教授级高级工程师，研究
方向为分布式新能源调度运行管理、智慧能源技
术，E-mail：xuxiaohui@epri.sgcc.com.cn。 
栗峰 
 
（责任编辑  马晓华）



<!-- page 14/15 -->

 
附录A 
表A1  近几年国家支撑分布式光伏发展及并网相关政策 
Table A1  National policies of supporting the development and grid connection of distributed PV in recent years 
时间 
国家政策 
政策方向 
核心内心及关键点 
2023 年6 月 
《关于印发开展分布式光伏接入电
网承载力及提升措施评估试点工作
的通知》(国能综通新能 
〔2023〕74 号) 
技术攻关 
充分发挥分布式光伏在推进我国新型能源体系建设中的积极作用，科学合理
评估分布式光伏接入电网的承载能力，研究分析接网承载力及提升措施，
着力解决分布式光伏接网受限等问题。 
2023 年6 月 
国家能源局组织发布 
《新型电力系统发展蓝皮书》 
技术攻关 
构建全景观测、精准控制、主配协同的新型有源配电网调度模式，满足分布
式新能源规模化开发及并网需要；加强分布式新能源可控可调、聚合协调优
化、电压协调控制技术等技术攻关，推动局部区域电力电量自平衡。 
2023 年3 月 
《关于组织开展农村能源革命试点
县建设的通知》 
(国能发新能〔2023〕23 号) 
技术攻关 
提升农村电网的可再生能源承载力，鼓励利用新建住宅屋顶、厂房和 
公共建筑屋顶等建一定比例光伏，加强光伏高效发电、并网和 
运行控制等技术研发应用。 
2022 年5 月 
《关于促进新时代新能源高质量发
展的实施方案》 
(国办函〔2022〕39 号) 
技术攻关 
加强有源配电网(主动配电网)规划、设计、运行方法研究， 
提高配电网智能化水平和接入分布式新能源的能力，合理确定 
配电网接入分布式新能源的比例。 
2022 年4 月 
《“十四五”能源领域 
科技创新规划》 
科技创新 
开展储能与分布式电源协同聚合、分布式光伏与可调可控负荷 
互动技术攻关，突破多种分布式资源协同控制和调配管理技术， 
提高配网对分布式光伏的接纳。 
2022 年1 月 
《关于加快建设全国统一电力市场
体系的指导意见》 
(发改体改〔2022〕118 号) 
战略规划 
鼓励分布式光伏主体与周边用户交易，完善微电网、 
存量小电网、增量配电网与大电网间运行调度机制， 
增强就近消纳和安全运行能力。 
2021 年10 月
《国务院关于印发2030 年前碳达峰
行动方案的通知》 
(国发〔2021〕23 号) 
技术攻关 
坚持集中式与分布式并举，加快智能光伏产业创新升级和 
特色应用，创新“光伏＋”模式，推进光伏发电多元布局， 
支持分布式新能源合理配置储能系统。 
2021 年10 月
《关于印发“十四五”可再生能源发
展规划的通知》 
(发改能源〔2021〕1445 号) 
战略规划 
坚持集中式与分布式并举，全面推进分布式光伏开发，规范 
有序推进整县(区)屋顶分布式光伏开发，构建适应 
大规模分布式可再生能源并网的智能配电网。 
2021 年9 月 
《公布整县(市、区)屋顶分布式光伏
开发试点名单的通知》 
(国能综通新能〔2021〕84 号) 
战略规划 
技术攻关 
全国试点676 个整县光伏，电网企业要在电网承载力分析基础上， 
充分考虑分布式光伏大规模接入需要，做好屋顶分布式 
光伏接网服务和调控运行管理。 
2021 年3 月 
《中华人民共和国国民经济和社会
发展第十四个五年规划和 
2035 年远景目标纲要》 
战略规划 
坚持集中式和分布式并举，加快发展东中部分布式能源， 
提高电力系统互补互济和智能调节、清洁能源消纳和存储能力。 
2020 年4 月 
《关于2020 年光伏发电上网电价政
策有关事项的通知》 
(发改价格[2020]511 号) 
战略规划 
明确了采用“自发自用、余量上网”模式和“全额上网” 
模式的工商业分布式光伏发电项目全发电量补贴标准， 
促进分布式光伏发展。 
 
表A2  分布式光伏技术典型标准体系表 
Table A2  Typical standard system of distributed PV technology 
序号
标准号 
名称 
类型
发布时间
主要内容 
1 
IEC TS 63276
配电网接纳分布式电源
承载力评估导则 
国际
标准
待定 
标准规定了电网接纳分布式电源承载力评估的一般原则和技术要求，包括热稳定
评估、短路电流校核、电压偏差校核、谐波校核和电网承载力等级划分等。 
2 
IEC TS 62786
—2017 
分布式能源与电网的
连接 
国际
标准
2017-04-01
标准规定了接入配电网的分布式电源的原则和技术要求。适用于分布式电源接入
配电网的规划、设计、运行和连接，包括一般要求、连接方案、正常工作范围等。
3 
GB/T 34932
—2017 
分布式光伏发电系统
远程监控技术规范 
国标
2017-11-01
标准规定了35kV 及以下分布式光伏发电系统远程监控的架构及配置、主站功能、
子站要求、通信、主站性能、子站性能和主站环境条件等技术要求。 
4 
GB/T 33593
—2017 
分布式电源并网 
技术要求 
国标
2017-05-12
标准规定了分布式电源接入电网设计、建设和运行应遵循的一般原则和技术要
求。适用于通过35kV 及以下电压等级接入电网的新建、改建和扩建分布式电源。
5 
GB/T 33592
—2017 
分布式电源并网运行
控制规范 
国标
2017-05-12
标准规定了35kV 及以下并网分布式电源在并网离网控制、有功无功功率控制、
电网异常响应、通信与自动化、继电保护及安全自动装置等运行控制要求。 
6 
GB/T 33342
—2016 
户用分布式光伏发电
并网接口技术规范 
国标
2016-12-13
标准规定了总容量30kW 及以下，通过380V/220V 接入的户用分布式光伏发电并
网接口遵循的一般原则、技术要求及其设备要求。 
7 
GB/T 31999
—2015 
光伏发电系统接入配电
网特性评价技术规范
国标
2015-09-11
标准规定了通过380V 电压等级线路接入电网，以及通过10(6)kV 接入配电网的
光伏发电系统并网特性评价的基本内容和方法。



<!-- page 15/15 -->

 
序号
标准号 
名称 
类型
发布时间
主要内容 
8 
GB/T 30152
—2013 
光伏发电系统接入配电
网检测规程 
国标
2013-12-17
标准规定了通过380V 电压等级接入电网，以及10(6)kV 电压等级接入用户侧的
光伏发电系统接入配电网的检测项目、检测条件、检测设备和检测步骤等。 
9 
GB/T 29319
—2012 
光伏发电系统接入配电
网技术规定 
国标
2012-12-31
标准规定了通过380V 电压等级接入电网，以及通过10(6)kV 光伏发电系统接入
电网运行应遵循的一般原则和技术要求。 
10 
DL/T 2041—
2019 
分布式电源接入电网承
载力评估导则 
行标
2019-06-04
标准规定了电网接纳分布式电源承载力评估的一般原则和技术要求，包括热稳定
评估、短路电流校核、电压偏差校核、谐波校核和电网承载力等级划分等。 
11 
NB/T 10204
—2019 
分布式光伏发电低压并
网接口装置技术要求
行标
2019-06-04
标准规定了400V 以下电压等级接入低压配电网的分布式光伏发电系统接入低压
配电网接口装置的分类、使用条件、结构、安全与电磁兼容要求。 
12 
NB/T 33013
—2014 
分布式电源孤岛运行控
制规范 
行标
2014-10-15
标准规定了计划孤岛运行状态下的以同步发电机、感应发电机、变流器等形式接
入35kV 及以下电压等级电网的分布式电源应满足的运行控制要求。 
13 
NB/T 32015
—2013 
分布式电源接入配电网
技术规定 
行标
2013-11-28
标准规定了分布式电源通过35kV 及以下电压等级接入电网运行应遵循的 
一般原则和技术要求。 
 
表A3  国家标准对分布式光伏并网运行参数要求 
Table A3  Requirements of national standards for distributed PV grid-connected operating parameters 
技术要求 
A 类分布式光伏 
B 类分布式光伏 
35kV
10(6)kV 公共电网 
10(6)kV 用户侧 
380V 
220V 
有功功率控制 
应具有有功功率调节能力，输出功率偏差及功率变化率应符
合电网调度机构给定值，并能根据电网频率值、电网调度机
构指令等信号调节电源有功功率输出 
若向公用电网输送电力，应具备接受电网 
调度指令进行功率控制的能力 
暂无 
要求 
无功电压调节 
并网点处功率因数和电压调节能力
满足指定范围可调，并可参与并网
点的电压调节，应具备接受电网调
度机构无功电压指令功能 
不向公用电网输电
能时宜具备无功控
制功能；反之宜具备
无功电压控制功能 
不同形式接入电网的分布式电源并网点处 
功率因数应能按规定范围要求可调 
暂无 
要求 
电压适应性 
0.85pu≤U≤1.1pu 时， 
应能正常运行； 
1.1pu< U <1.35pu 时， 
应在2s 内与电网断开； 
1.35pu≤U 时，应在0.2s 内与 
电网断开 
0.85pu≤U≤1.1pu 时，连续运行； 
U <0.5pu 或1.35pu≤U 时，最大分闸时间不超过0.2s； 
0.5pu≤U <0.85pu 或1.1pu< U <1.35pu 时，最大分闸时间不超过2s 
故障穿越 
宜具备一定的低电压穿越能力 
暂无要求 
频率适应性 
宜具备一定的耐受系统频率 
异常的能力 
当电网频率超出49.5~50.2Hz 范围时，应在0.2s 内与电网断开 
调度运行 
应能实时采集并网运行信息， 
并上传调度部门；配置遥控装置
的，应能接受、执行 
电网调度指令 
上传电流、电压和发电量等信息  
暂无 
要求 
功率预测 
其运营管理方宜进行发电预测，
向电网调度机构报送次 
日发电计划 
暂无要求 
信息通信 
应采用专网通信，具备与调度间
进行数据通信的能力，具备上传
信息及接受调度指令的能力， 
满足二次安全防护要求 
可采用无线、光纤、载波等通信方式；采用无线时， 
应采取信息通信安全防护措施 
暂无 
要求 
继电保护 
具备电压保护、频率保护、线路
保护、防孤岛保护等，将保护定
期检验结果和涉网保护定值上报
调度备案 
具备电压保护、频率保护等 
暂无 
要求
