<!--
source: D6_决策方法/基于改进ELECTRE法的电网规划投资多准则融合决策方法_程智余.pdf
sha256: e9b9ff12f478bd994d82b103773193efe823f10f4f995fa8da1adaa854ff09a2
method: pymupdf
pages: 7
-->

<!-- page 1/7 -->

 
基于改进ELECTRE 法的电网规划投资
多准则融合决策方法
程智余1，朱晓虎2，李建青2
(1. 国网安徽省电力有限公司，安徽 合肥　230000；
2. 国网安徽省电力有限公司经济技术研究院，安徽 合肥　230000)
 
 
摘　要：电网规划投资决策不仅要考虑项目投入产出效益，而且要考虑地区投资环境和企业管理水平对项
目投资的约束。为统筹协调电网规划投资决策中主观经验与客观数据、定性指标与定量指标、项目属性与
环境属性，提出一种基于改进消去与选择转换法（elimination et choice translating reality，ELECTRE）的电网规
划投资多准则决策方法。首先，提出电网规划投资中效益、效率与效能多准则融合决策理念；其次，构建
电网规划投资决策指标体系；再次，运用归档赋值法和偏好策略表对ELECTRE 法进行改进，构建基于改
进ELECTRE 法的电网规划投资决策模型，提出电网规划投资决策流程；最后，通过案例验证方法的可行
性。研究结果表明，该方法提升了投资效益、效率与效能，可为有关部门开展电网规划投资决策提供参考。
关键词：电网规划；投资决策；多准则融合；指标体系
DOI：10.11930/j.issn.1004-9649.202201086
 
 
 
0    引言
电网规划的投资决策是实现电网项目从规划
到运行的核心，也是电网企业投资精益化管理的
关键。新一轮电力体制改革背景下，电网投资行
为、成本及运营效率的监管进一步加强[1]。一方
面，电网企业陆续制定工作方案和管理办法，建
立“花钱问效”机制，进行电网投资决策的实践
探索；另一方面，创新与之相适应的电网规划投
资决策方法，提升投资决策的科学化水平，成为
亟须解决的关键问题。
新形势下，电网规划投资决策呈现出管理精
益化、投资精准化的新特点，对项目投入产出效率
和基于地区投资环境的精准施策提出了更高要求。
目前已有诸多电网规划投资决策方法的相关
研究。文献[2] 提出一种基于全生命周期投入产
出效益的电网规划精准投资决策方法。文献[3]
基于神经网络方法构建了电网投资评估模型。文
献[4] 从项目投入产出、项目投资溢出效应、电
网企业管理水平、电网企业经济指标4 个维度选
取指标，提出基于平衡计分表的电网项目投资评
估决策方法。文献[5] 采用K-均值聚类分析改进
DEA 方法开展电网投资决策。文献[6] 提出一种
基于资产负债率的多地区电网投资决策方法。总
体来看，现有电网投资决策研究主要侧重于对电
网项目自身经济性以及项目所产生外部效益的评
估，忽略了项目所在地区投资环境对电网规划投
资决策的影响，无法满足“花钱问效”理念下电
网精准投资的需求。
电网规划投资决策是一个复杂的决策过程，
应统筹考虑主观经验判断与客观数值分析、定性
与定量指标评估、项目属性与投资环境。鉴于
此，本文提出一种基于改进消去与选择转换法
（elimination et choice translating reality，ELECTRE）
的电网规划投资多准则融合决策方法。首先，提
出电网规划投资多准则决策理念；其次，构建与
多准则融合理念相适应的电网规划投资指标体
系；再次，针对多准则融合决策的特点，采取归
档赋值方式将定性指标转化为定量指标，结合效
用理论构建决策偏好策略表，刻画效益、效率、
收稿日期：2022−01−24； 修回日期：2022−03−29。
基金项目：国家电网公司科技项目（SGAHJY00ZXJS
2000036）。
第 55 卷 第 11 期
中国电力
Vol. 55, No. 11
2022 年 11 月
ELECTRIC POWER
Nov. 2022
59



<!-- page 2/7 -->

效能的多准则融合程度，并进一步提出基于改进
ELECTRE 法的电网规划投资决策模型；然后，提
出基于改进ELECTRE 法的电网规划投资多准则
决策流程；最后，通过案例进行分析验证。
 
1    投资理念及指标体系
投资效益是对特定电网项目或一定时空范围
内电网投资活动在经济、安全、社会等方面取得
的实际或预期效果的表征。效率、效能分别反映
了对特定电网项目或一定时空范围内电网投资活
动投入产出关系和电网投资活动管理水平。“花
钱问效”理念下，电网规划投资决策既要考虑单
体项目效益，又要反映项目所在区域投资效率和
效能。
对于电网规划投资，电网项目经济性、地区
投资环境优劣与企业管理水平是决定电网规划投
资的关键要素，决策过程应当统筹兼顾效益、效
率和效能。电网规划投资多准则特性分析如表1
所示。
效益评估准则反映电网规划投资“精益化”
程度，聚焦电网项目经济、安全、社会效益。效
率测度准则反映电网规划投资“精准化”程度，
评估拟投项目所在区域的整体投入产出情况。效
能监审准则反映电网规划投资“精细化”程度，
体现所在地区企业对于电网投资建设的管理水平
和运营能力。这3 条准则的区别在于，效益评估
侧重对电网项目的评估，效率测度和效能监审侧
重对电网所在地区投资环境的评估。
 
 
表 1   电网规划投资多准则特性分析
Table 1   Multi-criteria characteristic analysis of power
grid planning investment
序号准则名称
决策信息
决策对象
体现理念
1
效益准则
效益评估
拟投项目情况
精益化
2
效率准则
效率测度
拟投项目所在区域情况
精准化
3
效能准则
效能监审
拟投项目管理主体情况
精细化
 
 
为开展电网规划的效益评估、效率测度和效
能监审，本文构建了电网规划投资多准则决策指
标体系，如表2 所示。
 
2    面向电网规划投资多准则融合决策的
改进ELECTRE 法
ELECTRE 法能够有效求解多属性决策问题，
其基本思想是在两方案之间构造其支配关系，然后
从方案支配关系网中根据支配关系强弱选择出最
满意的方案。其突出特点是方案间相对优劣性概
念比较清晰，排序结果更加合理，但要求所有指
标均为定量指标，无法应用于有定性指标的分析
评估；此外由于效益、效率、效能指标对于电网
规划投资决策的影响不同，需要正确衡量三者权重。
本文运用归档赋值方法对定性指标进行量
化，结合经济学效用理论的理念构建偏好策略表
 
表 2   电网规划投资多准则决策指标体系
Table 2   Multi-criteria decision-making index system for power grid planning investment
评估准则
指标
数学表达
效益评估
经济效益
单位投资增供电量
计划新增电量/项目投资
投资造价先进程度
（全省项目平均单位造价–项目平价单位造价）/全省项目平均单位造价
安全效益
定性指标
社会效益
定性指标
 
效率测度
单位电网投资经济效益提升率
（各单位当年售电收入/各单位前3年电网投资）/
（各单位上年售电收入/各单位上年前3年电网投资）×100%
单位电网投资经济效益贡献率
（各单位当年售电收入/各单位前3年电网投资）/
（省公司当年售电收入/省公司前3年电网投资）×100%
单位电网新增容量运行效率
35 kV及以上新增容量利用效率×50%+10 kV新增配变利用效率×50%
效能监审
建设进度告警率
建设进度告警项目个数/在建项目个数×100%
投资采集告警率
投资完成采集值校验告警项目个数/在建项目个数×100%
年度投资完成偏差率
|本年投资完成值–本年投资计划值|之和/本年投资计划值之和×100%
中国电力
第 55 卷
60



<!-- page 3/7 -->

实现多准则融合，在此基础上将改进ELECTRE
法运用于电网规划投资决策。
 
2.1    评价指标计算
电网投资效益指标包括经济、安全和社会效
益指标。
（1）经济效益指标。文献[7-27] 对于各类评
估方法在投资评估中的应用已经十分成熟。此处
采用变异系数法生成经济效益指标权重，计算项
目经济效益得分。
（2）安全效益和社会效益指标。从安全效益
角度对电网项目归档分类，如表3 所示。I 类-
IV 类4 档得分分别为90、70、50、30。基于社会
效益划分将电网项目归档分类，如表4 所示。按
照强和弱两档分别赋值，强档85 分，弱档50
分。运用客观赋权法确定指标权重，加权生成社
会效益得分。
（3）采用变异系数法确定经济、安全、社会
效益指标权重，最终确定投资效益得分。
效率测度指标和效能监审指标均属于定量指
标，两者均采用变异系数法生成子指标相应权
重，然后分别计算项目所在地区效率测度和效能
监审指标得分。
 
2.2    效益、效率、效能准则融合
电网规划投资决策优劣，直接取决于对效
益、效率、效能3 条准则影响的准确刻画程度。
准则融合越有效，对项目投入产出、地区投资环
境、企业管理水平三者影响的刻画越契合实际，
评估结果越能满足“花钱问效”理念的要求。
微观经济学效用理论认为，消费者决策行为
偏好某商品，则该商品能为其提供高于其他商品
的实际效用。偏好可以根据客观指标，也可以基
于因心理感受而给出的主观判断。借鉴该理论，
通过引入偏好策略表，反映和刻画多准则融合的
具体策略。
偏好策略表通过对实际投资场景模拟，形成
一系列适用于不同投资场景的准则融合策略，如
表5 所示。每条策略反映特定场景下对效益、效
率、效能准则的偏好程度，即3 条准则在电网规
划投资决策中的影响权重大小。“高”“中”“低”
分别表示偏好程度在0.6~1、0.3~0.6、0~0.3 之间。
 
表 3   考虑安全效益的项目分类
Table 3    Grid project classification considering
safety benefits
项目
分类
序号
项目特征
I类
（1）已列入规划，符合公司战略或有政策支持
（2）解决局部失稳风险；解决一般及以上风险
（3）解决正常运行方式下增容、扩建、新建输变电工
程；两年内不投产会导致周边接近过载
（4）两年内投产220～110 kV变电站配套工程
（5）解决长期成片低电压的新增35 kV及以上项目
II类
（1）解决电网不满足N–1问题、线路卡脖子等
（2）解决现状电网一级电力事件风险
（3）解决正常运行下负载率超70%、历史负荷增长率达
5%以上且下级负荷难以转移的问题
（4）解决季节性成片低电压新增35 kV及以上项目
III类
（1）解决110 kV及以下电网开关遮断容量不满足短路电
流要求项目
（2）因设备运行状况差，更换未到报废期残旧设备或线
路的改造项目
IV类
（1）地区容载比超上限，无明显新增负荷，仅优化网架
结构项目
（2）解决不影响正常运行的单变问题项目
（3）老旧线路扩容性改造工程
 
表 4   考虑社会效益的项目分类
Table 4    Grid project classification considering
social benefits
项目分类
特征描述
社会效益赋值
营商民生绿色协同
I类
服务社会发展，显著改善供电
强
弱
弱
强
II类
已取得核准并明确在建电源送出
项目；重要用户配套送电工程
弱
弱
弱
强
III类
服务社会发展，较好改善供电
弱
强
弱
强
IV类
列入规划，接入系统方案已审定
弱
弱
强
强
V类
需安排资金回购电源自建工程
强
弱
弱
弱
 
表 5   电网规划投资多准则偏好策略
Table 5    Preference strategy for power grid planning
investment
序号
采取策略
准则偏好
效益
效率
效能
（1）
效益、效率、效能并重策略
中
中
中
（2）
效益、效率优先策略
中
中
低
（3）
效益、效能优先策略
中
低
中
（4）
效率、效能优先策略
低
中
中
（5）
效益优先策略
高
低
低
（6）
效率优先策略
低
高
低
（7）
效能优先策略
低
低
高
第 11 期
程智余等：基于改进ELECTRE 法的电网规划投资多准则融合决策方法
61



<!-- page 4/7 -->

为进一步精确刻画准则偏好程度，采用主观
赋权法，确定3 条准则在电网投资决策评估中的
影响权重。
 
2.3    改进ELECTRE 法数学模型
在定性指标量化处理并通过偏好策略表确定
准则融合方式后，采用改进ELECTRE 法构建电
网规划投资决策模型。
（1）基于项目效益评估、效率测度和效能监
审得分，形成m×3 阶决策矩阵X。其中，xij 为矩
阵元素，表示第i 个电网项目第j 个准则得分；
m 为电网项目总数。
x′
ij
（2）将决策矩阵X 进行归一化处理，得到
m×3 阶标准化矩阵X'。其中，
为矩阵的元素，
表示第i 个项目第j 个准则的归一化得分。
（3）将效益、效率、效能准则影响权重代入
标准化矩阵，得到m×3 阶加权决策矩阵R。其
中，rij 为矩阵的元素，表示第i 个项目第j 个准则
的加权得分，其计算式为
rij = x′
ijω j
（1）
式中：ωj 为第j 个准则的权重。
（4）将项目库中电网项目排序，序号分别
为1、2、···、m。对于每一对项目k 和项目l，效
益、效率、效能准则集J={1,2,3}被划分成2 个不
相交的子集，前者由项目k 中加权得分不低于项
目l 的准则组成，称为项目k 对项目l 的和谐集
Hkl；后者由项目k 中加权得分低于项目l 的准则
组成，称为项目k 对项目l 的不和谐集Bkl。
（5）基于和谐集Hkl，构造m×m 阶的和谐性
矩阵C，判断不同项目间效益、效率、效能准则
权重的相对优劣。其中，ckl 为矩阵的元素，表示
项目k 对项目l 的和谐指数，其计算式为
ckl =
∑
j∈Hkl
ωj
∑
j∈J
ωj
（2）
ckl 越大，则项目k 的准则权重高于项目l 的程
度越大。
（6）基于不和谐集Bkl，构造m×m 阶不和谐
矩阵D，反映不同项目效益、效率、效能得分相
对优劣。其中，dkl 为矩阵的元素，表示项目k 对
项目l 的不和谐指数，其计算式为
dkl =
max
j∈Bkl
|||rk j −rlj
|||
max
j∈J
|||rk j −rlj
|||
（3）
dkl 越大，则项目k 的效益、效率、效能评分
劣于项目l 的程度越大。
（7）根据和谐性矩阵C 和不和谐矩阵D，确
定m×m 阶的综合性支配矩阵E，反映不同项目多
准则融合决策下综合效果的相对优劣。其中，
ekl 为矩阵的元素，表示项目k 对项目l 的支配关
系指数，其计算式为
ekl = ckl −dkl
（4）
ekl 越大，则项目k 支配项目l 的强度越大，项
目k 在评估中越优于项目l。
（8）基于综合性支配矩阵，计算每个项目的
净支配指数ζk，其计算式为
ζk =
m
∑
i=1,i≠k
(eki −eik),k = 1,2,··· ,m
（5）
ζk 可以反映项目在准则融合下的投资综合效
用，ζk 越大，则项目投资效用越好。
（9）按ζk 从大到小将项目排序，根据排序结
果，开展电网规划投资决策评估优选。
 
2.4    决策流程
基于改进ELECTRE 法的电网规划投资多准则
融合决策流程如图1 所示。
 
3    算例分析
根据实际调研情况，选择某省待建项目库中
16 个市区范围内134 个电网项目（220 kV、110 kV）
作为本次实证分析对象。
假定该省2021 年新建电网年度投资规模为
5 亿元。其中刚性项目30 个，直接纳入规划，投
资额共计3.27 亿元，剩下1.73 亿元为弹性项目年
度投资规模。弹性项目库中，安全提升型和需求
驱动型项目分别有29 个和75 个，投资额分配比
为1∶1，则2021 年该省安全提升型和需求驱动型
弹性项目年度投资规模均为0.865 亿元。
以安全提升型项目为例，运用改进ELECTRE
法开展电网规划投资决策。基于对该省电网项目
特性以及地区投资环境、企业管理能力综合分
析，选取策略五（效益优先策略）进行多准则融
中国电力
第 55 卷
62



<!-- page 5/7 -->

合，求得效益、效率、效能准则权重分别为0.539、
0.297、0.164。
在此基础上，对安全提升型项目集构造和谐
性矩阵C1 和不和谐矩阵D1，并进一步确定综合
性支配矩阵E1。
计算每个项目净支配指数ζk，根据ζk 排序，
确定电网规划投资决策。最终安全提升型项目规
划投资决策结果如表6 所示。
 
4    结语
本文以提升电网规划投资精准度为目标，提
出一种基于改进ELECTRE 法的电网规划投资多
准则融合决策方法，实现了项目投入产出效益、
地区投资环境效益、企业管理效能的有效融合，
符合“花钱问效”理念下电网规划投资精益化、
精准化、精细化的要求。该方法具有较强的理论
价值和实践意义，可为政府部门和电网企业提供
决策支撑。
参考文献：
中共中央, 国务院. 关于进一步深化电力体制改革的若干意见(中
发〔2015〕9 号)[Z].
[1]
张全, 代贤忠, 韩新阳, 等. 基于全生命周期投入产出效益的电网规
划精准投资方法[J]. 中国电力, 2018, 51(10): 171–177.
ZHANG Quan, DAI Xianzhong, HAN Xinyang, et al. An accurate
investment method of power grid based on full life cycle input-output
benefit[J]. Electric Power, 2018, 51(10): 171–177.
[2]
张志强, 黄欣, 季玉华. 基于神经网络的电网投资决策评估模型构
建[J]. 企业经济, 2020, 39(9): 136–142.
[3]
何小平, 崔巍, 樊晓伟, 等. 电网大中型基建项目投资评估研究[J].
能源与环保, 2017, 39(11): 76–81.
HE Xiaoping, CUI Wei, FAN Xiaowei, et al. Research on investment
evaluation of large and medium sized infrastructure in power grid[J].
China Energy and Environmental Protection, 2017, 39(11): 76–81.
[4]
彭道鑫, 董士波, 王玲. 基于高质量发展的电网投资效率效益评估
体系研究[J]. 建筑经济, 2019, 40(12): 107–114.
PENG Daoxin, DONG Shibo, WANG Ling. Research on efficiency
and  benefit  evaluation  system  of  power  grid  investment  based  on
high  quality  development[J].  Construction  Economy,  2019,  40(12):
107–114.
[5]
张鹏飞, 柳璐, 杨卫红, 等. 基于资产负债率的多地区电网投资能力
测算方法[J]. 电力系统及其自动化学报, 2018, 30(6): 85–89.
ZHANG  Pengfei,  LIU  Lu,  YANG  Weihong,  et  al.  Assessment
[6]
 
表 6   安全提升型项目规划投资决策结果
Table 6    Planning investment decision-making results of
security-enhance projects
项目名称
效益
得分
效率
得分
效能
得分
净支配
指数
当年投资/
万元
B市220 kV
变电站工程
0.94
0.95
0.72
20.94
1 600
J市220 kV
变电站配套
0.88
0.98
0.74
16.96
700
A市220 kV
输变电
0.94
1.00
0.30
14.98
600
G市110 kV
变电扩建
0.92
0.59
0.81
10.68
1 000
O市220 kV
输变电工程
0.91
0.54
0.83
7.22
800
B市220 kV
输变电配套
0.67
0.95
0.72
5.73
650
M市110 kV
变电站扩建
0.89
0.78
0.26
4.49
531
J市110 kV
输变电工程
0.63
0.98
0.74
4.37
2 500
 
开始
结束
确定年度电网投资总体额度
刚性项目进入项目盘子
对每类弹性项目分别排序
计算年度弹性项目投资总额度
项目依次纳入投资计划
年度投资额度
是否用完？
是
否
基于改进 ELECTRE 法生成
弹性项目净支配指数
弹性项目分类，并确定每类
弹性项目投资比重
 
图 1   基于改进ELECTRE 法的电网规划投资多准则
融合决策流程
Fig. 1    Multi-criteria fusion decision-making process for
power grid planning investment based on improved
ELECTRE
 
第 11 期
程智余等：基于改进ELECTRE 法的电网规划投资多准则融合决策方法
63



<!-- page 6/7 -->

method for investment capacity of multi-area electric power systems
based on debt-to-asset ratio[J]. Proceedings of the CSU-EPSA, 2018,
30(6): 85–89.
方宇娟, 王秀丽, 师婧, 等. 计及新能源接入的省级电网效率效益评
估[J]. 电网技术, 2017, 41(7): 2138–2145.
FANG Yujuan, WANG Xiuli, SHI Jing, et al. Research on operation
and  economic  efficiency  evaluation  of  provincial  power  grid  with
integrated  renewable  energy[J].  Power  System  Technology,  2017,
41(7): 2138–2145.
[7]
程曦, 吴霜, 王静怡, 等. 输配电价改革背景下电网项目多阶段投资
优化决策研究[J]. 电力系统保护与控制, 2021, 49(15): 116–123.
CHENG Xi, WU Shuang, WANG Jingyi, et al. Research on multi-
stage  investment  optimization  of  power  grid  projects  under
transmission  and  distribution  price  reform[J].  Power  System
Protection and Control, 2021, 49(15): 116–123.
[8]
刘巍, 李锰, 李秋燕, 等. 基于改进遗传算法的电网投资组合预测方
法[J]. 电力系统保护与控制, 2020, 48(8): 78–85.
LIU Wei, LI Meng, LI Qiuyan, et al. Power grid portfolio forecasting
method  based  on  an  improved  genetic  algorithm[J].  Power  System
Protection and Control, 2020, 48(8): 78–85.
[9]
金强, 杨卫红, 王涛, 等. 考虑混合储能调频需求的独立微电网投资
优化[J]. 电力科学与技术学报, 2021, 36(1): 52–62.
JIN  Qiang,  YANG  Weihong,  WANG  Tao,  et  al.  Research  on
investment  optimization  of  standalone  microgrid  considering
frequency  modulation  with  hybrid  energy  storage[J].  Journal  of
Electric Power Science and Technology, 2021, 36(1): 52–62.
[10]
谭忠富, 谭彩霞, 余雪, 等. 基于混合布谷鸟算法的智能电网多业务
组合投资决策优化[J]. 智慧电力, 2021, 49(4): 51–57,88.
TAN Zhongfu, TAN Caixia, YU Xue, et al. Multi-business portfolio
investment  decision  optimization  of  smart  grid  based  on  hybrid
cuckoo algorithm[J]. Smart Power, 2021, 49(4): 51–57,88.
[11]
王梓珺, 王承民, 闫涛, 等. 基于序列线性关联度分析的配电网可靠
性投资估算方法研究[J]. 全球能源互联网, 2022, 5(1): 55–61.
WANG  Zijun,  WANG  Chengmin,  YAN  Tao,  et  al.  Research  on
distribution  network  reliability  investment  estimation  method  based
on  sequence  linearization  correlation  analysis[J].  Journal  of  Global
Energy Interconnection, 2022, 5(1): 55–61.
[12]
蔡张花, 单立, 刘福炎, 等. 基于负债率限制的电网企业投资能力研
究[J]. 价值工程, 2015, 34(9): 213–214.
CAI  Zhanghua,  SHAN  Li,  LIU  Fuyan,  et  al.  Investment  capacity
research for power grid enterprises based on debt ratio limit[J]. Value
Engineering, 2015, 34(9): 213–214.
[13]
沈润. 基于层次分析法的电网生产项目优选排序模型研究[J]. 通
信电源技术, 2019, 36(12): 24–25.
SHEN  Run.  Study  on  optimization  ranking  model  for  power  grid
production projects based on analytic hierarchy process[J]. Telecom
Power Technology, 2019, 36(12): 24–25.
[14]
王昭聪, 潘学萍, 马倩. 基于“奖优罚劣”线性变换改进前景理论
的电网建设项目多属性投资排序方法[J]. 电网技术, 2019, 43
(6): 2154–2164.
WANG  Zhaocong,  PAN  Xueping,  MA  Qian.  Multi-attribute
investment ranking method for power grid project construction based
on  improved  prospect  theory  of  “ rewarding  good  and  punishing
bad” linear transformation[J]. Power System Technology, 2019, 43
(6): 2154–2164.
[15]
黄晨洋, 严正, 杨火明, 等. 输配电价改革对省级电网投资的影响及
动态评估方法[J]. 电网技术, 2018, 42(10): 3291–3298.
HUANG Chenyang, YAN Zheng, YANG Huoming, et al. Impacts of
TDP reform on investment of provincial power grid and its dynamic
evaluation  method[J].  Power  System  Technology,  2018,  42(10):
3291–3298.
[16]
汪志才, 蔡晔, 谭玉东, 等. 考虑功能差异的输变电项目效益评价及
投资优化方法[J]. 中国电力, 2019, 52(11): 175–184.
WANG Zhicai, CAI Ye, TAN Yudong, et al. A method for benefit
evaluation  and  investment  optimization  considering  functional
differences  in  transmission  and  transformation  projects[J].  Electric
Power, 2019, 52(11): 175–184.
[17]
汪荣华, 杜英, 苟全峰, 等. 考虑输配电价改革的省级电网规划投资
效率效益评估[J]. 电力建设, 2020, 41(11): 135–144.
WANG  Ronghua,  DU  Ying,  GOU  Quanfeng,  et  al.  Evaluation  of
planning investment efficiency and benefit of provincial power grid
considering  the  reform  transmission  and  distribution  prices[J].
Electric Power Construction, 2020, 41(11): 135–144.
[18]
肖潇. 配电网精准投资评价体系的构建与运用[J]. 价值工程,
2019, 38(11): 59–61.
XIAO  Xiao.  Construction  and  application  of  accurate  investment
evaluation  system  for  distribution  network[J].  Value  Engineering,
2019, 38(11): 59–61.
[19]
黄锐, 王洪森. 复杂因素驱动下电网项目投资收益及其风险研
究[J]. 科技创新导报, 2020, 17(15): 171–172.
[20]
程亮, 胡卫利, 胡蔚, 等. 电网基建项目投资决策方法研究[J]. 电网
与清洁能源, 2014, 30(12): 84–90.
CHENG Liang, HU Weili, HU Wei, et al. Decision making on the
construction investment of a power grid project[J]. Power System and
[21]
中国电力
第 55 卷
64



<!-- page 7/7 -->

Clean Energy, 2014, 30(12): 84–90.
刘映晗. 电网项目经济效益评价机制在投资决策中的应用[J]. 中
国管理信息化, 2020, 23(17): 28–29.
[22]
熊振东, 梁锦照, 陈旭. 电网建设项目投资效益评估方法研究[J].
供用电, 2009, 26(5): 42–44,49.
XIONG  Zhendong,  LIANG  Jinzhao,  CHEN  Xu.  Research  on  the
method  of  investment  benefit  assessment  of  power  network
construction  project[J].  Distribution  &  Utilization,  2009,  26(5):
42–44,49.
[23]
章德娥. 电网规划与投资计划管理综合方法初探[J]. 中国管理信
息化, 2018, 21(2): 90–91.
[24]
刘旭娜, 魏俊, 张文涛, 等. 基于信息熵和模糊分析法的配电网投资
效益评估及决策[J]. 电力系统保护与控制, 2019, 47(12): 48–56.
LIU  Xuna,  WEI  Jun,  ZHANG  Wentao,  et  al.  Investment  benefits
evaluation and decision for distribution network based on information
entropy and fuzzy analysis method[J]. Power System Protection and
Control, 2019, 47(12): 48–56.
[25]
何凯, 王剑晓, 王佳伟, 等. 基于全成本电价的电网规划方案评估与
[26]
优选[J]. 中国电力, 2020, 53(3): 66–75.
HE  Kai,  WANG  Jianxiao,  WANG  Jiawei,  et  al.  Evaluation  and
optimization of power network planning scheme based on total-cost
price[J]. Electric Power, 2020, 53(3): 66–75.
李娜, 李朝阳, 周进, 等. 考虑投资均衡和效益性的中压配电网投资
分配[J]. 中国电力, 2021, 54(12): 143–149.
LI  Na,  LI  Chaoyang,  ZHOU  Jin,  et  al.  Investment  allocation  for
medium-voltage  distribution  networks  considering  investment
equilibrium and benefits[J]. Electric Power, 2021, 54(12): 143–149.
[27]
作者简介：
程智余（1966—），男，硕士，高级工程师，从事电
力建设管理、电力经济研究，E-mail：1553878681@qq.com；
朱晓虎（1974—），男，硕士，高级经济师，从事电
力造价、电力经济管理研究，E-mail：928729820@qq.com；
李建青（1985—），女，通信作者，硕士，高级经济
师，从事电力造价研究，E-mail：283093599@qq.com。
（责任编辑　于静茹）
A Multi-criteria Fusion Decision-Making Method for Power Grid Planning
Investment Based on Improved ELECTRE Method
CHENG Zhiyu1, ZHU Xiaohu2, LI Jianqing2
(1. State Grid Anhui Electric Power Co., Ltd., Hefei 230000, China; 2. State Grid Anhui Economic and
Technology Research Institute Co., Ltd., Hefei 230000, China)
Abstract: The investment decision-making of power grid planning not only needs considering the project benefits, but also needs
considering the regional investment environment and enterprise management levels. In order to realize the effective unification of
subjective experience and objective data, qualitative and quantitative indicators, project and environment, a multi-criteria fusion
decision-making method for power grid planning investment based on improved ELECTRE method is proposed. Firstly, the concept
of multi-criteria fusion decision-making of benefit, efficiency and effectiveness is proposed. Secondly, a power grid planning
investment decision-making index system is established. Then, the filing assignment method and preference strategy are used to
improve the ELECTRE method, and a power grid planning investment decision-making model is proposed based on the improved
ELECTRE method, and the decision-making process for power grid planning investment is proposed. Finally, the feasibility of the
proposed method is verified through case analysis. The research results show that the proposed method improves the benefit,
efficiency and effectiveness of investment, which can provide a reference for relevant departments to make decisions for power grid
planning investment.
This work is supported by Science and Technology Project of SGCC (No.SGAHJY00ZXJS2000036).
Keywords: power grid planning; investment decision-making; multi-criteria fusion; index system
第 11 期
程智余等：基于改进ELECTRE 法的电网规划投资多准则融合决策方法
65
