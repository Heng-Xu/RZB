<!--
source: D5_规划与灵活资源/CN_powergen_active_distribution_2024.pdf
sha256: bbe2203c1473eabbd7214945c14338cc0681cedf27d798b3f9682d6516b217d8
method: pymupdf
pages: 11
-->

<!-- page 1/11 -->

第 45 卷 第 1 期
 2024 年 2 月
Vol.45 No.1
Feb. 2024
发
电
技
术
发
电
技
术
Power Generation Technology
高比例新能源接入的主动配电网规划综述
刘洪波，刘珅诚，盖雪扬，刘永发，阎禹同
（东北电力大学电气工程学院，吉林省 吉林市 132012）
Overview of Active Distribution Network Planning With High Proportion 
of New Energy Access
LIU Hongbo, LIU Shencheng, GAI Xueyang, LIU Yongfa, YAN Yutong
(School of Electrical Engineering, Northeast Electric Power University, Jilin 132012, Jilin Province, China)
摘要
摘要：新能源以分布式电源的形式接入配电网，给系统带
来了不可控性、随机性和波动性问题。借助现代电力电
子、信息通信及自动控制等技术，灵活可控的主动配电网
成为发展趋势，其中主动配电网规划是近年来研究的热点
之一。综合国内外在这一领域的研究成果，对主动配电网
规划相关研究内容及其方法进行总结、分析及展望。对主
动配电网基本结构进行了描述，介绍了配电网组成元素的
特点；根据其控制变量的不同，对主动配电网规划模型进
行了归类，总结了模型中的优化目标；针对常用模型求解
算法及其优缺点进行分析、总结；通过对关键性问题的讨
论，分析了未来主动配电网的发展趋势。
关键词
关键词：电力系统；主动配电网规划；新能源；分布式
电源
ABSTRACT: The new energy is connected to the 
distribution network in the form of distributed generation, 
which brings uncontrollability, randomness and volatility to 
the system. With the help of modern power electronics, 
information and communication and automatic control 
technologies, the active distribution network with flexibility 
and controllability has become a development trend. The 
active distribution network planning is one of the major 
research fields in recent years. Based on the research results 
in this field at home and abroad, the research contents and 
methods of active distribution network planning were 
summarized, analyzed and prospected. The basic structure of 
the active distribution network was described, and the 
characteristics of the components of the distribution network 
were introduced. According to the different control variables, 
the planning models of active distribution network were 
classified, the optimization objectives in the model were 
summarized. The commonly used model solving algorithms 
and their advantages and disadvantages were analyzed and 
summarized. Through the discussion of key issues, the 
development trend of active distribution network in the future 
was analyzed.
KEY WORDS: electric power system; active distribution 
network planning; new energy; distributed generation
0　引言
　引言
配电网是电力系统的重要组成部分，科学合
理地规划配电网，可提高电力系统的可靠性与经
济性，提升电网的供电质量，减少运营商的投资
运维成本。传统配电网的电力潮流从上端变电站
单一流向负荷节点，只需采用必要的容量裕度即
可应对可能的场景，相当于被动配电网。分布式
电源、分布式供电系统的出现，尤其是风、光等
高渗透率新能源发电接入系统对潮流约束、可靠
性约束的冲击，给系统带来了不可控性、随机性
和波动性问题[1]。为解决在配电侧兼容这类间歇
式可再生能源、提升绿色能源利用率、改变一次
能源结构等问题，具有灵活可控特性的主动配电
网(active distribution network，ADN)应运而生[2-3]。
主动配电网借助现代电力电子、自动化以及
信息通信等技术，通过源−网−荷综合主动管理措
施进行协调优化，是具有灵活拓扑结构的公共配
电网[4]。主动配电网能够有效应对大量分布式电
源的并网并进行集成管理，减少弃风弃光，发挥
DOI：10.12096/j.2096-4528.pgt.22106        中图分类号：TK 01; TM 715
基金项目：国家电网有限公司总部管理科技项目(5100-
202226021A-1-1-ZN)。
Project Supported by Science and Technology Project of State Grid 
Corporation of China (5100-202226021A-1-1-ZN).



<!-- page 2/11 -->

Vol.45 No.1
刘洪波等
刘洪波等：高比例新能源接入的主动配电网规划综述
高比例新能源接入的主动配电网规划综述
多类型分布式电源并网的积极作用，以提升系统
经济性和可靠性[5]。
与传统配电网相比，主动配电网的主动性体
现在以下方面[6]：1）能够通过先进的信息通信技
术(information and communication technology，
ICT)及自动化技术，实现系统特定运行目标的最
优；2）具备动态的技术标准以实现定制供电；3）
具备灵活的网络结构以有效应对双向的潮流特性；
4）采用分散式管理，可进行精确的模拟计算。
本文综合主动配电网规划领域的研究成果，
介绍主动配电网的基本结构及组成元素特点，对
主动配电网规划模型进行归类，分析关键性问题，
总结相关求解算法，并对未来发展趋势进行展望。
1　主动配电网基本结构及组成元素
　主动配电网基本结构及组成元素
主动配电网除了从上级电网得到电能外，还
可以由风电、光伏等分布式新能源供电。主动配
电网还存在以燃气轮机、内燃机等传统分布式电
源为主的冷热电联供系统，以及多类型储能系统
(如机械储能、化学储能等)，同时，还包含电动
汽车(electric vehicle，EV)、微网等可交互系统。
主动配电网中可以通过需求响应策略对负荷用电
行为进行有效引导。这样，具有多种分布式电源、
多功能交互系统以及需求响应的用户构成了主动
配电网基本结构[7]，如图1所示。所含有的规划元
素包括电源类型、分布及容量，储能类型、位置
及容量等。根据地区的负荷特点、用电需求，可
选择不同的规划元素进行合理规划。
传统可控的分布式电源(如燃气轮机、燃料电
池)与分布式可再生能源形成互补发电系统，在一
定程度上平衡风、光出力的波动性[8]。因此，如
何合理规划可控性分布式电源与不可控性分布式
电源的容量、出力匹配，是分布式电源合理接入
主动配电网需要解决的问题之一。
微网在分布式电源合理接入主动配电网方面
具备优势。微网是由分布式电源、储能装置、能
量转换装置、相关负荷和监控、保护装置汇集而
成的小型发配电系统。微网常态方式下与主动配
电网并联运行，紧急情况下可以通过合理配置解
列点孤立运行[9]。微网虽然不涉及用户互动管理，
但是可以将分散的分布式电源、分布式储能系统、
柔性负荷等多种分布式设备合理结合起来，并且
不需要分布式就地控制器，只需采用常规量测装
置就能实现对整个电网的控制。因此，以微网群
形式接入主动配电网能够提高系统的可靠性和供
电质量，这是未来配电系统的发展趋势[10]。
储能设备能很好地解决高渗透分布式电源并
网所带来的能源消纳问题[11-12]。储能设备可以通过
对主动配电网充放电来实现平衡发电与负荷需求，
从而起到调节电压、降低网损、削峰填谷的作用，
还可以解决因保用电可靠性而带来的发电成本提
高问题。储能系统具有多种形式，其中蓄电池因
具有高效性与经济性而成为规划方案中储能设备
的首选[13]。高功率、高能量密度的蓄电池(如钠硫
电池)可通过公共交通运输系统在一定范围内实现
动态的储能增减配置，具备良好的移动潜力和巨
大的发展空间[14]。氢储综合系统作为化学储能的
重要形式，近年来也受到广泛关注。文献[15]研
究了电制氢(power-to-hydrogen，P2H)技术在提高
主动配电网的灵活性、促进新能源消纳等方面的
应用。
电动汽车作为一种新型清洁用电设备，有可
能成为移动储能设备，具备解决能源消纳问题的
潜力，因此充电桩安装位置、接入容量等电动汽
车相关设备、配置优化开始被纳入主动配电网规
划方案中[16]。然而，电动汽车充放电基础设施与
上级电网
变电站
化学储能、
机械储能等
储能系统
风力、光伏等
分布式能源
冷热电联供
微
网
电能双向传输
电能单向传输
信息流
需求
侧响应
负荷
电动
汽车
图1 主动配电网基本结构
主动配电网基本结构
Fig. 1 Active distribution network
152



<!-- page 3/11 -->

第 45 卷 第 1 期
发
电
技
术
发
电
技
术
风光互补系统的容量配比还需进一步研究。
需求侧响应与用户用电行为相伴而生，用户
可通过响应价格信号或者激励机制改变用电行为，
有效促进新能源的消纳[17]。用户的互动管理是主
动配电网区别于传统配电网的显著特征，主动配
电网可以通过改变用户的用电方式、负荷柔性控
制等实现需求侧管理。目前，大多数规划方案选
择特定激励模式的需求侧响应特性，但价格型需
求响应在能源消纳方面更具优势。文献[18]根据
电动汽车的需求侧响应特性，使电动汽车可以有
序充放电，同时考虑分布式电源相关性，对分布
式电源和充电桩的投资−运行进行协同配置，可实
现对系统负荷峰谷差的调节。
主动配电网考虑多种主动管理方式[19]，在提
升系统稳定方面具备明显优势，能够有效应对分
布式电源的接入。主动配电网可通过管理电压电
流、分布式电源的出力等参数实现主动潮流管理，
通过调节变压器分接头、接入无功补偿设备等实
现主动电压调整，通过网络重构合理地改变潮流
分布。文献[20]考虑有载调压变压器、分组投切
电容器等多种主动管理手段，构建主动配电网分
层鲁棒规划模型，对主动配电网进行升级改造。
2　主动配电网规划模型
　主动配电网规划模型
2.1　数学模型
　数学模型
传统配电网规划模型包括最大化变电站所带
负荷的变电站模型，最小化线路投资、运行费用
的网架规划模型，以及变电站网架联合规划模
型[21]。主动配电网规划模型与传统配电网规划模
型相似，但主动配电网在规划阶段不仅要考虑各
种不确定性工况，还要考虑多种电源的源−网协调
优化问题[22]。
主动配电网规划模型一般为多目标、非线性
的混合整数优化问题。由于不同目标之间可能存
在互斥关系，因此主动配电网规划一般采用多层
规划模型来解决优化问题。在多层规划模型中，
最上层作为规划层面对自身最优目标进行寻优且
反馈给下一层，下一层同时考虑上一层的结果进
行自身目标的寻优后，将包含自身最优的结果反
馈给上一层进行相应调整，通过这种层层递进、
反复循环的过程，形成主目标最优、次目标相对
最优的方案。其模型公式表示如下：
ì
í
î
ïïï
ïïï
min
x1
f1 (x1x2xn )       
s.t.ì
í
î
g1 (x1x2xn )≤0
h1 (x1x2xn )= 0
(1)
x2由下面式子得到：
ì
í
î
ïïï
ïïï
min
x2
f2 (x1x2xn )       
s.t.ì
í
î
g2 (x1x2xn )≤0
h2 (x1x2xn )= 0
(2)
…
ì
í
î
ïïï
ïïï
min
xn
fn (x1x2xn )       
s.t.ì
í
î
gn (x1x2xn )≤0
hn (x1x2xn )= 0
(n)
式中：xi (i=1, 2, …, n)为规划模型的控制变量；fi 
为规划方案的优化目标；gi (×)与hi (×)分别为规划模
型的不等式约束与等式约束。
式(1)一般作为规划模型的规划层，是规划方
案主要的优化目标；式(2)—(n)一般作为运行层，
包含一些次要优化目标，同时帮助主要优化目标
达到最优解。
2.2　控制变量
　控制变量
选择控制变量也就是选择进行规划的对象。
主动配电网模型的控制变量一般可分为规划层面、
运行层面2 种。运行层面控制变量一般为电压质
量、网络损耗、电源出力等规划方案中需要突显
的指标。规划层面控制变量大体可分为2 类：一
类是电源规划，如分布式电源、充电站等选址定
容；另一类是在电源规划的基础上，考虑多种因
素且以电网建设为主的综合规划[23]。
1）电源规划
电源规划直接影响规划区域配电网的结构及
系统运行的经济性、可靠性，合理的电源规划能
够保证配电网未来的扩容，并为系统的安全稳定
运行提供合适的裕度。例如，文献[24]将能源互
联配电网的能源耦合设备和分布式电源的选址定
容作为决策变量，所构建模型为电源规划的经济
性和可靠性提供了参考。
2）综合规划
计及多种设备和技术融入的综合规划，考虑
153



<!-- page 4/11 -->

Vol.45 No.1
刘洪波等
刘洪波等：高比例新能源接入的主动配电网规划综述
高比例新能源接入的主动配电网规划综述
了电源选址定容、网架建设、主动管理等技术协
调作用。例如，文献[25]通过建立主动配电网3层
模型，将规划环节中的网架建设、分布式电源的
选址定容以及不同时段的运行管理相结合。文献
[26]采用双层规划模型，建立以线路升级改造、
分布式电源和储能系统的选址定容为决策变量的
上层模型，以各时序场景下分布式电源出力及其
功率因数、分组电容投切、变压器分接头档位、
负荷削减系数、储能系统充放电功率、智能软开
关(soft open point，SOP)各端口有功/无功输出为
决策变量的下层模型，从而形成了含SOP 主动配
电网源−网−荷−储协调的综合规划。
2.3　优化目标
　优化目标
主动配电网的优化目标可以分为经济类目标、
技术类目标和环保类目标[10,27]。
各种设备的投资运维成本、分布式电源运营
商收益、配电网运行商收益、网损成本、储能套
利、用户利益、用户满意度、弃风弃光成本、主
网购电成本等是经济类目标优化的重点，也是规
划层面通常考虑的优化目标[12,24,28]。
技术类目标与规划方案重点关注的领域有关，
包括分布式电源接入位置、电源出力及其渗透率，
主动配电网电压质量、电压偏差，设备的安全性、
可靠性指标等。例如，文献[29]对储能电池总体
效率、允许放电深度、使用寿命等技术类目标进
行规划。
环保类目标(如可再生能源消纳水平、环境污
染指数、碳排放、可再生能源补贴等)近年来逐渐
被纳入规划目标中，此类规划目标可转换为经济
类指标出现在规划层面或运行层面。
同时，计及经济、技术、环保等多目标规划
是近年来研究的热点问题之一[30-31]。例如，文献
[30]以分布式电源渗透率、风光消纳水平、经济
效益以及电压偏差指标作为优化目标，建立了多
目标规划模型。
2.4　约束条件
　约束条件
由于配电网中规划元素的增加以及主动管理
的引入，需同时考虑多方面的约束条件，以保证
主动配电网有效运行。约束条件分为等式约束与
不等式约束，无论是传统配电网还是主动配电网，
考虑潮流约束及节点电压、支路电流不越限约束
等网络安全约束是系统正常运行的基础。
当分布式电源接入主动配电网时，需要考虑
接入分布式电源的节点功率平衡、安装数量等约
束；当储能接入主动配电网时，需要对储能装置
的功率、容量等进行约束；当电动汽车接入主动
配电网时，需要对电动汽车的充电效率、充电站
容量等进行约束；考虑不同需求响应时，还有调
节系数、可中断负荷、激励负荷量等约束。文献
[32]将风光储与充电站进行协同规划，考虑对电
动汽车的充电需求约束，针对主动管理的方式对
变压器分接头档位、次数进行约束，并将场景的
机会约束融入潮流计算中，以提高计算效率。
3　主动配电网模型求解算法及多目标处理
　主动配电网模型求解算法及多目标处理
3.1　求解算法
　求解算法
传统配电网规划常采用启发式算法，这种算
法发展比较成熟完备，但由于其基于直观和经验
进行构造，缺少随机元素，给定输入，得到对应
的固定输出，因此得到的可行解与最优解的偏离
程度一般不可预计。文献[33]为解决主动配电网
发生故障时一部分会转化为计划孤岛(即孤岛分
割)问题，提出采用前瞻性贪婪算法这种启发式算
法求解1-nkp模型。
目前，应用于主动配电网规划模型的求解算
法主要分为以下2 类[34]：一类是数学优化算法，
这类算法适用于小规模系统，求解精度高，能得
到理论上的最优解，但是若系统规模增大，求解
难度也随之提高；另一类则是发展迅速的元启发
式算法，这类算法适用于大规模系统，计算效率
高，通用强，但是容易陷入局部最优解，计算速
度会随系统的增加变得缓慢，并且算法仍依赖经
验来选择参数。因此，对元启发式算法的改进问
题还需进行研究。
3.1.1　数学优化算法
对于一些线性问题，可直接采用分支定界算
法、Benders分解、内点法等数学优化算法，或借
助CPLEX、GUROBI、Mosek 求解器进行求解。
文献[13]所构建模型的决策变量只有2个，约束条
件较多，与元启发式算法相比，采用数学优化算
154



<!-- page 5/11 -->

第 45 卷 第 1 期
发
电
技
术
发
电
技
术
法进行求解更好，因此最终采用动态规划算法解
决液流电池的配置问题。
目前，数学优化算法大多采用松弛变换先将
非线性问题转化为线性问题，再借助求解器进行
求解。文献[11]在目标松弛变换的基础上又采用ε-
松弛法，用多面体来近似二阶锥，以提高求解的
速度。文献[18-20,35-40]均采用二阶锥松弛变换将
非线性问题转化为线性问题，目前研究已证明这
种线性化过程并不影响优化精度。文献[35-36]中
由于模型采用智能算法时求解效率低下，因此采
用二阶锥松弛变换将模型转化为线性度更好的二
阶锥模型，并结合Benders分解进行求解。
3.1.2　元启发式算法
对于越来越复杂、规模越来越大的主动配电
网模型，元启发式算法尤其是人工鱼群算法、粒
子群算法、遗传算法等在求解速度、搜索效率方
面表现良好，并且不需要对繁杂的约束条件、目
标函数进行处理，已广泛应用于主动配电网规划
模型的求解中。但元启发式算法自身存在收敛速
度慢、编译复杂、易陷入局部最优、依赖参数等
缺点，需要进行改进。目前，对元启发式算法的
改进大致分为以下3个方向。
1）对初始种群进行改进
对目标种群进行优化可以避免伪随机数列的
影响，同时减少落后种群不必要的迭代，显著提
高求解速度。文献[25]考虑线路数量的不同和可
能发生的变化，采用特殊编码方式将线路映射到
0~1的连续区间，生成特殊种群，实现快速求解。
文献[30]采用Logistic 映射生成混沌初始化序列，
对种群的位置与速度进行优化，有效地提升了收
敛速度和全局寻优的效果。文献[31]采用帐篷混
沌映射生成初始种群，针对目标问题对根树优化
算法进行改进，提出离散型根树优化算法。
2）对自身参数进行改进
元启发式算法中的部分参数对搜寻、收敛能
力等影响巨大，针对这些参数进行改进，可以提
高寻优能力、摆脱局部解、提升收敛速度。文献
[41]针对粒子群算法更新公式中惯性权重因子影
响全局搜索能力的问题，对惯性权重因子进行改
进，将其从1线性降低到0，并在算法中加入交叉
与变异，通过多次计算得到最佳解集。文献[35]
针对遗传算法编码方式复杂、求解效率低等问题，
提出了基于正态分布思想并结合进化策略中离散
重组操作的正态分布交叉(normal distribution 
crossover，NDX)算子，以代替原有的模拟二进制
交叉(simulated binary crossover，SBX)算子对交叉
过程进行模拟，提升解的搜索能力，减轻局部最
优问题。文献[42]采用混合整数编码算子求解初
始个体，采用混合整数变异算子求解变异个体，
以提高求解效率。
3）融合其他算法
融合其他智能算法可以使当前算法拥有所融
合算法的显著优点，但同时也要考虑对2 种算法
融合后的局限性进行改进。文献[5]为减少计算时
长，采用差分算法的变异交叉策略替代标准和声
搜索算法的音量调整和初始随机选取新解的过程，
结合并行计算技术提出了并行差分和声搜索算法。
文献[43]采用应用于快速非支配遗传算法的快速
非支配法，根据各非支配解的拥挤−距离赋值，选
择每次迭代中的最优解，得到Pareto 最优前沿的
一组多样性解集。
3.2　多目标处理
　多目标处理
主动配电网规划模型常通过对多目标进行规
划得到最优解，求解模型前要对多目标进行处理，
处理方式大致分为2 种。一种通常出现在采用数
学优化算法求解的多目标模型中，这类方案常采
用权重系数法[11-12,18,31,44]，在多个目标函数前加上权
重，从而转化为单个目标函数。但权重系数的选
择通常依靠经验，权重大小的确定较为主观。
另一种则是基于Pareto 多目标的智能优化算
法[17,28,30,43]。与权重系数法不同，这种方法是对多
目标赋予同样的权重，得到一组处于最优前沿的
解集。解集尽可能展现不同目标的多种可能性，
规划方案可以通过对某个指标的侧重来选择其中
一组解，但这种方法求解时间长、计算量大。文
献[43]基于Pareto的多目标改进粒子群算法，得到
10种可供决策者选择的最优备选方案集合。
4　主动配电网关键问题的处理
　主动配电网关键问题的处理
在主动配电网规划设计过程中，普遍出现的
155



<!-- page 6/11 -->

Vol.45 No.1
刘洪波等
刘洪波等：高比例新能源接入的主动配电网规划综述
高比例新能源接入的主动配电网规划综述
问题是由于规划元素(如分布式电源的出力、电
价、负荷需求响应等)存在随机性，给主动配电网
实际运行管理带来了不确定性。此外，追求切合
实际的方案不仅要考虑传统的投资运营方，还要
逐渐向用户、当地管理者、第三方投资者等多个
主体倾斜。
4.1　主动配电网不确定性特征处理
　主动配电网不确定性特征处理
在规划方案选择规划元素阶段，分析所选元
素的变化特性和规律，对具有不确定性的元件进
行模拟建模，模拟越精细，越能体现配电网运行
的实际工况[45]。
模拟建模的方法有2 种：一种为体现时序特
性的场景分析法，多用于在时间序列上能够呈现
一定规律的规划元素建模；另一种为以概率模型
为首的数学理论分析方法，常结合大量历史数据，
用于在统计层面呈现一定规律的规划元素建模。
4.1.1　场景分析法
场景分析法包含场景的生成与削减2 部分[46]。
场景的生成可以用真实的数据或者概率统计数据
按照时间序列生成所需场景，对生成的多场景进
行分析，可使规划结果更加精确、符合实际。在
场景削减中，场景数量的确定存在计算工作量与
计算精度间的矛盾。过多的场景可以充分体现数
据所含有的特征，体现多样性的同时也造成了计
算负担、计算效率低下等问题；过少的场景虽然
提升了计算速度，但计算精度下降，使场景多样
性、代表性缺失。场景分析法大致分为以下2类：
1）选取四季典型日场景[8,20,32,47-49]进行分析。
但这类方法选择场景过于简略，将其应用于各季
日气候差异不明显的地区，或者是通过计算场景
出现概率来选取场景进行分析的方案，存在一定
的局限性。将负荷按特性分类，并计及风电、光
伏出力特点以及二者之间的互补特性，选择四季
典型日场景，可具有更好的参考性[8]。
2）基于实际数据或预测数据建立多场景后，
通过聚类算法对场景进行削减[5,17,25,30-31,43,50-51]。这类
方法通常因为多种变量物理意义不同，先采用均
一化的方法进行处理，再根据场景数量对单维变
量进行聚类，最后对场景进行组合。如何确定方
案所需场景数量(即聚类中心数量)、如何组合单
维场景模拟实际场景，是这类方法研究的主要问
题。文献[30]采用改进模糊C均值聚类算法对风−
光−荷样本进行聚类，在聚类过程中通过计算样本
与聚类中心的欧式距离，并利用以此建立的隶属
度函数进行分类，重复步骤，以达到场景分类的
效果。
在场景数量选择方面，文献[43]采用k均值聚
类算法将负荷和可再生能源的365 种场景聚类为
典型场景，引入戴维斯柏丁指数来确定合适的聚
类数量。文献[51]除引入戴维斯柏丁指数外，还
引入后向场景削减法、联合概率分布，根据最优
聚类状态自行设定初始的聚类中心，删减调整聚
类中心步骤，并联合时序场景进行聚类，在保证
削减后场景拟合精度的同时极大地减少了运算量。
在场景组合方面，通常采用遍历法对场景进
行组合，这种方法精度高但计算复杂。针对单维
场景的组合，目前考虑分布式电源出力之间的相
关性，可为不同场景的组合分析提供参考。如风
速较大的天气常伴随着阴天出现，睛空万里的天
气风速一般较低。考虑分布式电源出力的相关性，
可以使场景组合从首尾顺序组合到有针对性地组
合，能够更贴近所模拟实际地区。文献[18,36-37]
从变量的角度考虑了相关性。文献[36]首先利用
Spearman 秩相关系数对不确定性变量之间的概率
相关性进行表征，然后通过Cholesky 分解进行独
立变换，将原始变量转化为相互独立的随机变量，
从而可以研究不同不确定性变量之间的相关性对
规划决策的影响。
4.1.2　概率模型方法
目前，常采用数学上的概率模型对风速、光
照等不确定性量进行模拟，可通过已有概率密度
或者通过数学方法模拟出概率密度来描述不确定
性，如风速、光照强度分别与Weibull分布、Beta
分布相符，通常采用这2 种概率模型来模拟风光
变化[52-53]。另外，可在概率模型的基础上结合采样
法(如蒙特卡洛、拉丁超立方、重要采样法等)生
成模拟风光出力的场景，但采用概率模型在描述
其时间相关的特性方面表现较差。文献[18,25,41,
44]采用蒙特卡洛模拟对风速、光照进行采样。文
献[26,52]则采用拉丁超立方采样对不确定性进行
156



<!-- page 7/11 -->

第 45 卷 第 1 期
发
电
技
术
发
电
技
术
处理。文献[43]针对风光概率模型进行改进，并
在用正态分布模拟的随机负荷基础上加入时序模
型，使概率模型能够有效地捕捉时序性，体现各
可再生能源与负荷的相关性。
4.1.3　随机网络、模糊理论等方法
除了应用广泛的概率模型以外，区间理
论[38-39,43,48,53]、随机网络理论、模糊理论[24,29,42]等数
学理论也可解决不确定性问题。文献[40]在对光
伏采用Beta 模型的基础上引入区间分布概率，进
一步精确描述其不确定性。文献[28]引入条件风
险价值改进置信区间上下限的计算方法，采用条
件置信区间表示光伏出力。文献[24]考虑到风光
目标函数实际上为随机变量，采用基于Minimin
形式的随机机会约束规划模型建立目标函数。
4.2　多利益主体
　多利益主体、时间相关规划问题
时间相关规划问题
规划方案与时间长短息息相关，考虑时间的
规划可以得到更加精细的规划方案，能够应对不
同的工况。与时间相关的规划方案通常包括以
下2种：
1）以年甚至10 年为单位的规划问题和以小
时为单位的运行问题之间的多时间尺度协调规划
方案。文献[33]建立了双层规划模型，上层以长
期规划为目标，考虑长期的经济效益、系统可靠
性以及环保性；下层以短期运行为目标，考虑不
同时段的套利以及故障发生后快速恢复的能力。
2）中长期规划通常指多阶段规划。多阶段规
划分为2 类：一类为每个阶段分别寻优；另一类
为多阶段统一规划，即每个阶段可能不是最优，
但可以保证总方案最优。多阶段统一规划的主要
难点在于，规划阶段数量、状态变量、参数取值
的选择较难，与其他方法相比，优势不明显[23]。
不同时间尺度之间的相互影响使得多阶段、
多时间模型求解更加复杂，因此与时间相关的规
划发展缓慢。
由于规划方案更注重经济性，主要考虑投资
方的收益，但是多种类型的能源、多样的技术融
入意味着主动配电网的规划方案向着考虑多方主
体利益的方向发展，通过多方利益博弈得到相对
较优的方案[54]。文献[55]在规划时考虑到电网公司
以及第三方公司的利益，可以更好地对分布式电
源和储能装置进行选址定容，决定哪一方对某种
能源进行大力投资，实现利益最大化、系统可靠
性最优化。
5　结论
　结论
1）主动配电网规划方案的难点在于对规划元
素不确定性的处理。不同元素的不确定性差异明
显，特别体现在与时间序列的密切相关性上，如
分布式新能源的出力、居民的用电行为、电动汽
车的使用习惯等。因此，基于时间维度对规划元
素进行分析建模，充分反映不同元素的实际运行
情况，在一定程度上将不确定性变为规律性，可
使规划方案变得更为合理。
2）在掌握规划元素不确定性的基础上，根据
当地电源、负荷及电网特点，考虑各元素间的耦
合关系，即不同元素之间的互补与互斥联系。考
虑这种相关性的规划方案能使投资、运维等经济
性指标显著提升，也可以提高系统的安全可靠性。
3）在大力开发利用可再生能源的过程中以及
在多种能源全面发展的形势下，电能作为不同形
态能源的纽带，可以将不同特性的能源进行耦合，
使大量多形态的分布式电源接入配电网中，而配
电网运行规划与用户的用电可靠性、电能质量直
接相关。因此，研究能容纳多种能源、平衡协调
出力、满足多种负荷需求的主动配电网规划是发
展的必然趋势。随着多种类型能源的并网互动，
配电网结构日益复杂，导致控制变量、优化目标、
约束条件的数量激增，加剧了计算负担，因此，
有效的建模方法和高效的求解手段是解决未来规
划方案的关键技术条件。
参考文献
参考文献
[1]
季玉琦，王涛，史少彧，等．含分布式电源的配电网
功率优化模式影响因素分析[J]．电力科学与技术学
报，2023，38(1)：97-107．
JI Y Q，WANG T，SHI S Y，et al．Analysis of 
influencing factors of power optimization modes in 
distribution network containing distributed generations
[J]．Journal of Electric Power Science and Technology，
2021，49(15)：38-46．
[2]
席向东，侯香臣，萨仁高娃，等．计及电压预测的主
157



<!-- page 8/11 -->

Vol.45 No.1
刘洪波等
刘洪波等：高比例新能源接入的主动配电网规划综述
高比例新能源接入的主动配电网规划综述
动配电网分布式电源在线优化决策方法[J]．电力建
设，2022，43(11)：24-32．
XI X D，HOU X C，SAREN G W，et al．Online 
optimization 
decision 
algorithm 
for 
distributed 
generations considering voltage prediction in active 
distribution network[J]．Electric Power Construction，
2022，43(11)：24-32．
[3]
刘建伟，李学斌，刘晓鸥．有源配电网中分布式电源
接入与储能配置[J]．发电技术，2022，43(3)：
476-484．
LIU J W，LI X B，LIU X O．Distributed power 
access and energy storage configuration in active 
distribution network[J]．Power Generation Technology，
2022，43(3)：476-484．
[4]
李振坤，黄滢，李谅，等．计及需求侧响应的主动
配电网多时间尺度优化调度[J]．电力建设，2023，
44(3)：36-48．
LI Z K，HUANG Y，LI L，et al．Multi-time scale 
optimal dispatching of active distribution network 
considering demand-side response[J]．Electric Power 
Construction，2023，44(3)：36-48．
[5]
孙旻，张大，余愿，等．计及投资方收益与主动配电
网管理的分布式光伏电源规划[J]．智慧电力，2020，
48(9)：56-62．
SUN M，ZHANG D，YU H，et al．Planning of
distributed photovoltaic generations considering investor
benefits and active distribution network management[J]．
Smart Power，2020，48(9)：56-62．
[6]
张建华，曾博，张玉莹，等．主动配电网规划关键问
题与研究展望[J]．电工技术学报，2014，29(2)：
13-23．
ZHANG J H，ZENG B，ZHANG Y Y，et al．Key 
issues and research prospects of active distribution 
network 
planning[J]．
Transactions 
of 
China 
Electrotechnical Society，2014，29(2)：13-23．
[7]
邓正臣．主动配电网规划研究与综述[J]．科技创新与
应用，2021，11(12)：56-58．
DENG Z C．Research and summary of active 
distribution 
network 
planning[J]．
Technology 
Innovation and Application，2021，11(12)：56-58．
[8]
高红均，刘俊勇．考虑不同类型DG和负荷建模的主
动配电网协同规划[J]．中国电机工程学报，2016，
36(18)：4911-4922．
GAO H J，LIU J Y．Coordinated planning considering 
different types of DG and load in active distribution 
network[J]．Proceedings of the CSEE，2016，36(18)：
4911-4922．
[9]
范明天，张祖平，苏傲雪，等．主动配电系统可行技
术的研究[J]．中国电机工程学报，2013，33(22)：
12-18．
FAN M T，ZHANG Z P，SU A X，et al．Enabling 
technologies 
for 
active 
distribution 
systems[J]．
Proceedings of the CSEE，2013，33(22)：12-18．
[10] 李睿．主动配电系统协同规划模型与方法[D]．北京：
北京交通大学，2018．
LI R．Cooperative planning models and methods of 
active power distribution systems[D]．Beijing：Beijing 
Jiaotong University，2018．
[11] 项恩新，王科，关静恩，等．基于凸松弛的主动配电
网储能与无功补偿协同规划[J]．电力系统及其自动化
学报，2020，32(10)：63-69．
XIANG E X，WANG K，GUAN J E，et al．
Collaborative planning for energy storage and reactive 
power compensation in active distribution network based 
on convex relaxation method[J]．Proceedings of the 
CSU-EPSA，2020，32(10)：63-69．
[12] 粟世玮，张谦，熊炜，等．含高渗透可再生能源的动
态网络重构与无功电压调整协同优化[J]．电网与清洁
能源，2023，39(1)：100-110．
SU S W，ZHANG Q，XIONG W，et al．
Coordination 
optimization 
of 
dynamic 
network 
reconfiguration and reactive power voltage regulation 
with high penetration renewable energy generation[J]．
Power System and Clean Energy，2023，39(1)：
100-110．
[13] 方金涛，龚庆武．考虑需求响应并计及液流电池动态
特性的主动配电网系统储能优化配置[J]．智慧电力，
2019，47(11)：1-8．
FANG J T，GONG Q W．Optimal allocation of energy 
storage system in active distribution network considering 
demand response and dynamic characteristics of VRB
[J]．Smart Power，2019，47(11)：1-8．
[14] 文劲宇，周博，魏利屾．中国未来电力系统储电网初
探[J]．电力系统保护与控制，2022，50(7)：1-10．
WEN J Y，ZHOU B，WEI L S．Preliminary study on 
an energy storage grid for future power system in China
[J]．Power System Protection and Control，2022，
50(7)：1-10．
[15] 李佳蓉，林今，邢学韬，等．主动配电网中基于统一
运行模型的电制氢(P2H)模块组合选型与优化规划[J]．
中国电机工程学报，2021，41(12)：4021-4033．
LI J R，LIN J，XING X T，et al．Technology 
portfolio selection and optimal planning of power-to-
hydrogen (P2H) modules in active distribution network
[J]．Proceedings of the CSEE，2021，41(12)：4021-
4033．
158



<!-- page 9/11 -->

第 45 卷 第 1 期
发
电
技
术
发
电
技
术
[16] 蔡黎，张权文，代妮娜，等．规模化电动汽车接入主
动配电网研究进展综述[J]．智慧电力，2021，49(6)：
75-82．
CAI L，ZHANG Q W，DAI N N，et al．Review on 
research progress of large-scale electric vehicle access 
to active distribution network[J]．Smart Power，2021，
49(6)：75-82．
[17] 朱文广，廖志军，刘洪，等．考虑需求响应与高比例
可再生能源接入的主动配电网扩展规划[J]．电力系统
及其自动化学报，2019，31(5)：84-91．
ZHU W G，LIAO Z J，LIU H，et al．Expansion 
planning for active distribution network considering 
demand response and high ratio of renewable energy 
access[J]．Proceedings of the CSU-EPSA，2019，
31(5)：84-91．
[18] 刘晋源，吕林，高红均，等．计及分布式电源和电动
汽车特性的主动配电网规划[J]．电力系统自动化，
2020，44(12)：41-48．
LIU J Y，LYU L，GAO H J，et al．Planning of active 
distribution network considering characteristics of 
distributed 
generator 
and 
electric 
vehicle[J]．
Automation of Electric Power Systems，2020，44(12)：
41-48．
[19] 谢仕炜，胡志坚，王珏莹，等．基于不确定随机网络
理论的主动配电网多目标规划模型及其求解方法[J]．
电工技术学报，2019，34(5)：1038-1054．
XIE S W，HU Z J，WANG J Y，et al．A multi-
objective planning model of active distribution network 
based on uncertain random network theory and its 
solution algorithm[J]．Transactions of China Electro-
technical Society，2019，34(5)：1038-1054．
[20] 高红均，刘俊勇，魏震波，等．主动配电网分层鲁棒
规划模型及其求解方法[J]．中国电机工程学报，
2017，37(5)：1389-1401．
GAO H J，LIU J Y，WEI Z B，et al．A bi-level 
robust planning model of active distribution network and 
its solution method[J]．Proceedings of the CSEE，
2017，37(5)：1389-1401．
[21] 王明渊，何凯，王木．基于配网规划等值曲线的输
配电网协调规划[J]．电力科学与技术学报，2022，
37(6)：46-54．
WANG M Y，HE K，WANG M．Coordinated 
transmission & distribution network expansion planning 
based on project-net revenue curve of distribution 
network[J]．Journal of Electric Power Science and 
Technology，2022，37(6)：46-54．
[22] 王杰，王维庆，王海云，等．考虑越限风险的主动配
电网中DG、SOP 与ESS 的两阶段协调规划[J]．电力
系统保护与控制，2022，50(24)：71-82．
WANG J，WANG W Q，WANG H Y，et al．Two-
stage coordinated planning of DG，SOP and ESS in an 
active distribution network considering violation risk[J]．
Power System Protection and Control，2022，50(24)：
71-82．
[23] 邢海军，程浩忠，张沈习，等．主动配电网规划研究
综述[J]．电网技术，2015，39(10)：2705-2711．
XING H J，CHENG H Z，ZHANG S X，et al．
Review of active distribution network planning[J]．
Power System Technology，2015，39(10)：2705-
2711．
[24] 赵丽萍，张书伟，张雪岩，等．基于随机机会约束规
划的面向能源互联的主动配电网选址定容方法[J]．电
力系统保护与控制，2020，48(14)：121-129．
ZHAO L P，ZHANG S W，ZHANG X Y，et al．
Locating and sizing method for energy interconnection 
oriented active distribution networks based on stochastic 
chance constrained programming[J]．Power System 
Protection and Control，2020，48(14)：121-129．
[25] 刘洪，郑楠，葛少云，等．内嵌需求响应与优化运行
策略的主动配电系统源网协同规划[J]．电力系统自动
化，2020，44(3)：89-97．
LIU H，ZHENG N，GE S Y，et al．Coordinated 
planning of source and network in active distribution 
system with demand response and optimized operation 
strategy[J]．Automation of Electric Power Systems，
2020，44(3)：89-97．
[26] 张忠会，雷大勇，李俊，等．基于自适应ε-支配多目
标粒子群算法的含SOP的主动配电网源−网−荷−储双
层协同规划模型[J]．电网技术，2022，46(6)：2199-
2212．
ZHANG Z H，LEI D Y，LI J，et al．Source-network-
load-storage bi-level collaborative planning model of 
active distribution network with SOP based on adaptive 
ε-dominating multi-objective particle swarm optimization 
algorithm[J]．Power System Technology，2022，46(6)：
2199-2212．
[27] 严艺芬，吴文宣，张逸．主动配电网规划关键问题研
究[J]．电气技术，2016(11)：1-5．
YAN Y F，WU W X，ZHANG Y．Important issues in 
planning of active distribution system[J]．Electrical 
Engineering，2016(11)：1-5．
[28] 温丰瑞，李华强，温翔宇，等．主动配电网中计及灵
活性不足风险的储能优化配置[J]．电网技术，2019，
43(11)：3952-3962．
WEN F R，LI H Q，WEN X Y，et al．Optimal 
allocation of energy storage systems considering 
159



<!-- page 10/11 -->

Vol.45 No.1
刘洪波等
刘洪波等：高比例新能源接入的主动配电网规划综述
高比例新能源接入的主动配电网规划综述
flexibility deficiency risk in active distribution network
[J]．Power System Technology，2019，43(11)：3952-
3962．
[29] DAGHI M，SEDGHI M，AHMADIAN A，et al．
Factor analysis based optimal storage planning in active 
distribution 
network 
considering 
different 
battery 
technologies[J]．Applied Energy，2016，183：456-
469．
[30] 张永会，鹿丽，潘超，等．计及风−光−荷时序特性的
主动配电网源−储规划策略[J]．电力系统保护与控
制，2020，48(20)：48-56．
ZHANG Y H，LU L，PAN C，et al．Planning 
strategies 
of 
source-storage 
considering 
wind-
photovoltaic-load time characteristics[J]．Power System 
Protection and Control，2020，48(20)：48-56．
[31] SANNIGRAHI S，GHATAK S R ，ACHARJEE P．
Multi-scenario based bi-level coordinated planning of 
active distribution system under uncertain environment
[J]．IEEE Transactions on Industry Applications，
2019(99)：1．
[32] 孔顺飞，胡志坚，谢仕炜，等．计及风光储与充电站
的主动配电网双层协同规划[J]．电测与仪表，2019，
56(17)：60-68．
KONG S F，HU Z J，XIE S W，et al．Bi-level 
collaborative planning of active distribution network 
considering wind-solar-storage and charging stations[J]．
Electrical Measurement & Instrumentation，2019，
56(17)：60-68．
[33] YU Y，MA S．1-neighbour knapsack problem and 
prospective greedy algorithm of intentional islanding in 
active 
distribution 
network[J]．
Science 
China 
Technological Sciences，2014，57(3)：568-577．
[34] 肖白，郭蓓．配电网规划研究综述与展望[J]．电力自
动化设备，2018，38(12)：200-211．
XIAO B，GUO B．Review and prospect of distribution 
network planning[J]．Electric Power Automation 
Equipment，2018，38(12)：200-211．
[35] 凌松，张莹．计及相关性的主动配电网动态鲁棒规划
方法研究[J]．电力系统保护与控制，2021，49(10)：
178-187．
LING S，ZHANG Y．Research on a dynamic robust 
planning method for an active distribution network 
considering correlation[J]．Power System Protection 
and Control，2021，49(10)：178-187．
[36] 韩璟琳，袁建普，胡诗尧，等．考虑多元随机因素概
率相关性的主动配电网规划研究[J]．智慧电力，
2020，48(9)：23-29．
HAN J L，YUAN J P，HU S Y，et al．Active 
distribution network planning considering probability 
correlation of multiple random factors[J]．Smart Power，
2020，48(9)：23-29．
[37] XING H，CHENG H，ZHANG Y，et al．Active 
distribution network expansion planning integrating 
dispersed energy storage systems[J]．IET Generation，
Transmission & Distribution，2016，10(3)：638-644．
[38] DONG L，LI J，PU T，et al．Distributionally robust 
optimization model of active distribution network 
considering uncertainties of source and load[J]．Journal 
of Modern Power Systems and Clean Energy，2019，
7(6)：1585-1595．
[39] NICK M，CHERKAOUI R，PAOLONE M．Optimal 
allocation of dispersed energy storage systems in active 
distribution networks for energy balance and grid support
[J]．IEEE Transactions on Power Systems，2014，
29(5)：2300-2310．
[40] LUO Y，NIE Q，YANG D，et al．Robust optimal 
operation of active distribution network based on 
minimum confidence interval of distributed energy beta 
distribution[J]．Journal of Modern Power Systems and 
Clean Energy，2021(2)：423-430．
[41] MAHDAVI S，HEMMATI R，JIRDEHI M A．Two-
level planning for coordination of energy storage 
systems and wind-solar-diesel units in active distribution 
networks[J]．Energy，2018，151：954-965．
[42] 马瑞，罗心仪，肖麟祥．基于随机模糊机会约束的主
动配电网分布式风电双层规划模型[J]．电力科学与技
术学报，2021，36(3)：46-55．
MA R，LUO X Y，XIAO L X．Distributed wind 
power 
bi-level 
programming 
model 
for 
active 
distribution network based on stochastic fuzzy chance 
constraint[J]．Journal of Electric Power Science and 
Technology，2021，36(3)：46-55．
[43] LI R，WANG W，WU X，et al．Cooperative 
planning model of renewable energy sources and energy 
storage units in active distribution systems：a bi-level 
model and Pareto analysis[J]．Energy，2019，168：
30-42．
[44] MOKRYANI G．Active distribution networks planning 
with integration of demand response[J]．Solar Energy，
2015，122：1362-1370．
[45] 黄亦昕．考虑严重运行受限场景的含高渗透率可再生
能源电网规划研究[D]．杭州：浙江大学，2021．
HUANG Y X．Research on power system planning 
with high penetration of renewable energy considering 
severely restricted scenarios[D]．Hangzhou：Zhejiang 
University，2021．
160



<!-- page 11/11 -->

第 45 卷 第 1 期
发
电
技
术
发
电
技
术
[46] 徐健玮，马刚，高丛，等．基于风光场景生成的综合
能源系统日前−日内优化调度[J]．分布式能源，
2022，7(4)：18-27．
XU J W，MA G，GAO C，et al．Day-ahead and intra-
day optimal scheduling of integrated energy systems 
based on scenario generation[J]．Distributed Energy，
2022，7(4)：18-27．
[47] 章姝俊，钱啸，白聪，等．面向多应用场景的储能系
统优化配置方法[J]．浙江电力，2022，41(5)：22-31．
ZHANG S J，QIAN X，BAI C，et al．Optimal 
configuration method of energy storage system oriented 
to multiapplication scenarios[J]．Zhejiang Electric 
Power，2022，41(5)：22-31．
[48] 任智君，郭敏铧，郭红霞，等．电源−用户互动模式
下的主动配电网分布式电源规划[J]．可再生能源，
2019，37(11)：1643-1649．
REN Z J，GUO M H，GUO H X，et al．Active 
distribution network planning method under power-user 
interaction mode[J]．Renewable Energy Resources，
2019，37(11)：1643-1649．
[49] BORGES C L T，MARTINS V F．Multistage 
expansion planning for active distribution networks 
under demand and distributed generation uncertainties
[J]．International Journal of Electrical Power & Energy 
Systems，2012，36(1)：107-116．
[50] 初壮，孙健浩，赵蕾，等．考虑风光与负荷时序特性
的主动配电网分布式电源优化配置[J]．电力建设，
2022，43(11)：53-62．
CHU Z，SUN J H，ZHAO L，et al．Optimal 
configuration of distributed power generation in active 
distribution network considering the characteristics of 
wind power and load time series[J]．Electric Power 
Construction，2022，43(11)：53-62．
[51] 孙建梅，胡嘉栋，蔚芳．基于改进场景聚类法的主动
配电网中分布式电源准入容量规划[J]．科学技术与工
程，2021，21(1)：194-200．
SUN J M，HU J D，YU F．Active distribution 
network power admission capacity planning based on 
improved 
scene 
clustering 
method[J]．
Science 
Technology and Engineering，2021，21(1)：194-200．
[52] 张沈习，袁加妍，程浩忠，等．主动配电网中考虑需
求侧管理和网络重构的分布式电源规划方法[J]．中国
电机工程学报，2016，36(S1)：1-9．
ZHANG S X，YUAN J Y，CHENG H Z，et al．
Optimal distributed generation planning in active 
distribution 
network 
considering 
demand 
side 
management 
and 
network 
reconfiguration[J]．
Proceedings of the CSEE，2016，36(S1)：1-9．
[53] MOKRYANI G，HU Y F，PILLAI P，et al．Active 
distribution networks planning with high penetration of 
wind power[J]．Renewable Energy，2017，104：
40-49．
[54] 张翔，廖海君，周振宇，等．含规模化5G 基站租赁
共享储能的配电网混合博弈优化调度[J]．电测与仪
表，2023，60(5)：23-32．
ZHANG X，LIAO H J，ZHOU Z Y，et al．Hybrid 
game optimal dispatching for distribution network with 
large-scale 5G base station leasing shared energy storage
[J]．Electrical Measurement ＆ Instrumentation，2023，
60(5)：23-32．
[55] 郭红霞，任智君．考虑不同投资主体储能运行策略的
主动配电网多目标规划[J]．智慧电力，2019，
47(11)：22-28．
GUO H X，REN Z J．Multi-objective planning for 
active distribution network considering energy storage 
operation strategies under different investment entities
[J]．Smart Power，2019，47(11)：22-28．
  收稿日期
收稿日期：2023-06-25。
作者简介
作者简介：
刘洪波(1973)，女，博士，副教授，
主要研究方向为电力系统规划运行、电
力系统稳定与控制，liuhb@neepu.edu.cn；
刘珅诚(1997)，男，硕士研究生，
主要研究方向为主动配电网规划，
763673068@qq.com。
(责任编辑 尚彩娟)
161
