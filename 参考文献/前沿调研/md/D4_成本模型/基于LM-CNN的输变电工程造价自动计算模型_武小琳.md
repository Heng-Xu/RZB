<!--
source: D4_成本模型/基于LM-CNN的输变电工程造价自动计算模型_武小琳.pdf
sha256: da1cbd3d67114a729106fcdfa2c1d74a3e5e3117b6ed613a993fa9d835915905
method: pymupdf
pages: 7
-->

<!-- page 1/7 -->

 
基于LM-CNN 的输变电工程造价自动计算模型
武小琳2，栾凌1，潘连武2，李海龙2
(1. 国网辽宁省电力有限公司沈阳供电公司，辽宁 沈阳　110000；2. 国网辽宁省电力
有限公司，辽宁 沈阳　110006)
 
 
摘　要：输变电工程造价计算作为造价管控技术的核心环节，其计算模型的好坏直接影响输变电工程造价
管控效能。然而现有模型往往不能兼顾计算速度、精确性与稳定性。为解决上述问题，首先，针对输变电
工程造价中的实际需求确定模型的输入与输出，构建卷积神经网络模型；然后，将历史造价数据作为样本
输入网络模型，得到网络输出；最后，针对期望输出与实际输出相差较大的问题，利用列文伯格-马夸尔
特算法对卷积神经网络的权重参数进行优化，完成模型训练。该模型结合列文伯格-马夸尔特算法与卷积
神经网络模型的优点，相比于反向传播（BP）神经网络与梯度下降法-卷积神经网络（GD-CNN）具有更高
的预测精度与稳定性，提高了输变电工程造价的计算效果。
关键词：输变电工程；列文伯格-马夸尔特算法；卷积神经网络；自动计算模型；造价管控
DOI：10.11930/j.issn.1004-9649.202103063
 
 
 
0    引言
随着中国各行业的发展与工业现代化程度的
显著提高，对各类工程造价管控过程的可视化、
可控化要求日益增加[1]。近年来，电力行业飞速
发展，但输变电工程造价管控技术的改进相对于
蓬勃发展的电力工程建设而言略显滞后，给输变
电工程的造价工作带来了诸多影响[2]。为改善这
一问题，亟须建立有效考虑各项因素的输变电工
程造价自动计算模型。
诸多专家学者对输变电工程造价模型展开了
深入研究。文献[3] 建立了一种输变电工程造价预
测模型，利用熵权法选择样本特征，降低数据维
度，减少模型计算量，但粒子群优化算法（particle
swarm optimization，PSO）的局部搜索能力较弱，
搜索精度不高；文献[4] 提出了采用遗传算法与
PSO 的径向基神经网络造价预测算法，并对2 种
算法的预测结果进行了对比，径向基神经网络的
应用需要充足的样本数据，而随着样本的增加训
练时间也会大幅增加，影响模型计算速度；文献[5]
应用基于PSO 优化的极限学习机模型对输变电工
程造价预测展开分析，但极限学习机模型训练速
度较慢，达不到理想的计算速度；文献[6] 从输
变电工程造价的各类费用角度出发，构建了支持
向量机（support vector machines，SVM）模型对输
变电工程造价进行预测；文献[7] 利用基于高斯-
萤火虫算法优化的SVM 构建输变电工程造价预测
模型，提高了模型的预测精度，文献[6-7] 中的
SVM 模型受核函数选择影响较大，且大样本适应
能力较差；文献[8] 应用主成分分析法与反向传
播（back propagation，BP）神经网络对输变电工
程造价进行建模；文献[9] 将小波神经网络（wavelet
neural network，WNN）与多元线性回归相结合，
提高了模型在输变电工程造价预测中的动态表
现；文献[10] 利用人工免疫算法优化BP 神经网
络的全局参数，并结合多组工程实例验证模型性
能；文献[8-10] 所采用的BP 神经网络与WNN 均
容易出现过拟合，模型实际应用效果不佳。对于
电力行业来说，输变电工程造价的自动计算应该
具有较高的准确性、稳定性与计算速度。上述几
种模型均分别存在计算速度慢、计算精度不足或
计算难度过高等问题[11]。
为解决上述问题，本文采用结构更优的卷积
神经网络（convolutional neural network, CNN）模型
收稿日期：2021−03−09； 修回日期：2022−05−09。
基金项目：国家电网有限公司科技项目（SGLNSY00HLJS
2002775）。
第 56 卷 第 2 期
中国电力
Vol. 56, No. 2
2023 年 2 月
ELECTRIC POWER
Feb. 2023
157



<!-- page 2/7 -->

与更稳定的列文伯格-马夸尔特（Levenberg-Marquart,
LM）优化算法，建立满足输变电工程项目的工程
量自动计算[12]、材料消耗自动计算、工程结算自
动计算的统一计算模型。
 
1    基于LM 算法优化的CNN 模型
 
1.1    卷积神经网络
人工智能的蓬勃发展推动了各行业技术的飞
速进步，近年来随着人工智能在各领域的广泛应
用，以CNN[13-15] 为代表的深度学习算法在植物病
害识别、电力负荷预测与新冠肺炎影像学诊断等
诸多领域均取得了很好的效果。
从层级角度来看，CNN 由多组交叠布置的卷
积层与池化层、1 组或多组全连接层与输出层组
成。交叠布置的卷积层与池化层能够较好地提取
数据特征，其中携带共享权重的卷积核按设定步
长扫过对应维度的数据窗口，对数据进行初步特
征提取。卷积核每扫过1 个区域将与其覆盖的数
据进行卷积运算，经过非线性函数激活后输出给
池化层，其数学表达式为
Xp = R
■|||||||■
n
∑
i = 1
n
∑
j = 1
Xc
i, jWc
i, j +bc
■|||||||■
（1）
Xp
R(·)
n
Xc
i, j
i
j
Wc
i, j
i
j
bc
式中：
为池化层的某一数据，是卷积核每次移
动所做运算的1 个输出值；
为非线性ReLu 激
活函数；为卷积核的维度；
为在卷积层被卷
积核覆盖的数据样本中第行列的样本元素；
为卷积核上第行列的元素即携带权重；
为
该卷积层的偏置量。池化层一般选择最大池化，
即选取滤波器中的最大值作为输出。ReLu 函数与
最大池化计算表达式分别为
R(x) = max(0, x)
（2）
Xf = max
(
Xp
i, j
)
（3）
x
Xf
Xf
Xp
i, j
i
j
式中：为函数自变量；
为池化层输出，若池
化层后面连接全连接层，则
为全连接层的1 个
数据；
为池化层滤波器中第行列的数据。对
于复杂的输变电工程造价计算问题，其影响造价
结果的数据特征较多，因此需要池化层来简化数
据维度，减少模型的计算量，进一步提取数据特
征，提高模型训练速度。
通过几组交叠布置的卷积层与池化层提取特
征后，再将所有特征输入全连接层，与一般全连
接神经网络类似，全连接层对所有特征求取加权
和，在通过全连接层非线性激活函数激活，其数
学表达式为
Y = S
■||||||■
m
∑
i = 1
wf
iXf
i +bf
■||||||■
（4）
Y
S (·)
m
wf
i
Xf
i
i
bf
式中：
为全连接层的1 个输出；
为非线性
Sigmoid 激活函数；
为该全连接层神经元个数；
为全连接层连接权重；
为全连接层第个神经
元元素；
为全连接层的偏置量。Sigmoid 函数表
达式为
S (x) =
1
1+e−x
（5）
从网络模型角度来看，综合考虑影响输变
电工程造价各环节的有关因素，建立初步数学模
型为
H = σ(u,v, r, t)
（6）
H
σ
u
v
r
t
式中：
为输变电工程造价计算中的具体结果；
为各影响因素与输变电工程造价输出间的非线
性映射关系；为技术层面影响因素向量；为组
织层面影响因素向量；为外部环境层面影响因
素向量；为造价参数层面影响因素向量。
在造价预测工作中，首先收集历史造价管控
数据作为训练集输入CNN 进行学习，随后网络模
型将自动提取数据特征并计算网络输出，该输出
值与工程实际造价数据对比，求取输出数据误
差，再通过优化算法进行权重修正[16]，如此迭代
至网络收敛。再将待办工程数据输入网络便可得
到输变电工程造价的精确预测值[17]。
 
1.2    LM 权重优化算法
目前，常用的神经网络权重优化算法主要有
梯度下降法（gradient descent, GD）、牛顿法、共
轭梯度法、高斯-牛顿法、LM 算法[18] 等。其中，
GD 是当前的主流算法，但是由于其收敛是沿着
负梯度方向下降，因此导致其收敛速度十分缓
慢。而牛顿法因为其计算过程中每次迭代都要计
算1 次Hessian 矩阵，所以其计算的过程十分复
杂。高斯-牛顿法虽然找到了1 个Jacobian 矩阵代
替Hessian 矩阵进行计算，极大地提高了计算速
度，但是若Hessian 矩阵不满秩则无法进行迭代。
中国电力
第 56 卷
158



<!-- page 3/7 -->

而LM 法可有效解决Hessian 矩阵不满秩或不正定
的情况，同时保障了高效计算。LM 算法求解的
增量方程为
(JTJ +µI)δP = JT∆
（7）
J
JT
J
µ
I
∆
δP
式中：为对误差权重修正的雅可比矩阵；
为
对误差权重修正的阵的转置；
为阻尼项；为
单位矩阵；为误差修正量；
为增量。
δP
在得到输变电工程造价预测数据后，通过初
始向量变化法得到误差函数，求得雅可比矩阵，
并通过构造增量方程得到每次修正后的增量
，
并用于判断迭代是否收敛。并通过雅可比矩阵与
误差修正量进行CNN 的权重优化，权重优化表达
式为
Wk+1 = Wk + J−1∆k
（8）
Wk+1
k +1
Wk
k
J−1
∆k
式中：
为第
次迭代修正后的权重值；
为第次迭代修正后的权重值；
为雅可比矩
阵的逆矩阵。误差修正量
是第k 次迭代所得输
出与真实值的差值，其计算表达式为
∆k = y−f(Wk)
（9）
y
f(Wk)
Wk
式中：为模型输出对应的真实值。在网络权重
修正过程中，造价影响因素已经输入网络且保持
不变，可视为常量，因此
是
为自变量时
的网络输出，即造价预测值。
µ
µ
µ
LM 算法与GD 算法跟牛顿法的区别在于值
的大小，在此算法中
值可根据需要自行调整。
当
值最大时意味着误差达到最小值，此时学习
停止。
将LM 算法与CNN 相结合，得到改进后的
CNN 模型，其模型流程如图1 所示。
 
2    基于LM-CNN 的输变电工程造价自动
计算模型
输变电工程造价的影响因子主要有技术、组
织、外部环境和造价参数4 类[19]。技术层面上包
含主变压器容量、电气设备的选择、配电装置的
规划、主接线方式和高压断路器台数等；组织层
面上为项目建设技术服务费、工程管理水平、施
工人员技术水平等；外部环境层面上交通运输情
况、征用耕地、站址选择、林地面积和地质条件
等；造价参数层面包含税金、人工费、机具使用
费和设备材料价格等[20]。基于列文伯格-马夸尔特
卷积神经网络（Levenberg-Marquart convolutional
neural network，LM-CNN）的输变电工程造价计算
模型如图2 所示。
 
 
技术层数据
数据输入
LM 算法权值修正
造
价
计
算
网
络
训
练
组织层数据
依据计算问题进行数据筛选
环境层数据
造价层数据
完成训练
判断收敛
计算结果
全连接
池化
池化
卷积
卷积
网络更新
重新迭代
卷
积
神
经
网
络
输出、制表
是
否
 
图 2   基于LM-CNN 的输变电工程造价计算模型
Fig. 2    LM-CNN-based cost calculation model for power
transmission and transformation projects
 
 
模型以技术层、组织层、环境层、造价层数
据作为特征数据库，针对不同计算问题进行强相
 
开始
模型训练?
误差下降?
满足精度?
是
增大阻尼系数
求解增量模型
更新雅可比矩阵 J k
更新增量方程
(J kTJ k+μI)δP=J kTΔ
更新阻尼系数
迭代次数 k=k+1
结果输出
误差分析
计算模型输出
保存模型
模型精度分析
网路权值修正
是
是
否
否
卷积、池化
数据特征提取
设定初值 V0
终止条件 ε
阻尼条件 μ
模型应用
测试
训练
否
数据整备、数据集划分, 列特征向量: (u, v, r, t)
 
图 1   LM-CNN 模型流程
Fig. 1    Flow chart of LM-CNN model
 
第 2 期
武小琳等：基于LM-CNN 的输变电工程造价自动计算模型
159



<!-- page 4/7 -->

关性的数据特征筛选，确定模型输入输出[21]。例
如在进行输变电工程单位容量造价金额计算时，
模型的输入着重提取变压器容量、变压器单价、
征地补偿等技术层与环境层数据，模型的输出为
单位容量造价。
此时网络的输入输出关系以可看作为以输入
数据为自变量，以输出值为因变量的1 个非线性
函数。在造价工作中，将相同特征的数值输入网
络即可得到输出的预测值[22]。
 
3    算例分析
 
3.1    样本数据
本文采用近几年实际结算的输变电工程造价
数据[3] 作为原始样本，并在Matlab 环境下进行仿
真实验，部分原始数据如表1 所示。本文应用前
18 组数据作为训练集用于模型训练，后6 组数据
作为测试集用于检验计算精确度。在相同数据集
条件下进行单位容量造价仿真计算实验，并将本
文提出的LM-CNN 模型的计算结果与基于GD 算
法优化的CNN 模型和BP 神经网络模型进行对比。
 
3.2    数据处理
利用模型对工程造价进行预测时，需要对历
史数据进行分析与处理。由于输变电工程造价样
本数据中存在不同数据特征值相差较大的情况，
在网络训练过程中，数据值较大的特征相比于数
据值较小的特征具有一定程度的数值优势，影响
网络训练效果[23]。因此，在数据输入网络模型前
要先对数据进行归一化。归一化通过算法将全部
数据以特征自身数值的最大最小值为基准将该特
征的所有数值变为（0，1）之间的数，可以在很
大程度上提高网络训练质量[24]。
 
3.3    结果分析
µ0
10−3
ε
10−7
本文在相同参数条件下对3 种模型进行训
练，其中LM 算法的阻尼系数
设置为
；3 种
模型的收敛精度均设置为
，初始权重设置为
随机值；此外，LM 与GD 算法优化的CNN 模型
均参照式（1）~（6）建立且模型结构相同。LM-
CNN 模型训练效果如图3 所示。
通过网络迭代次数与训练时间对比模型计算
速度。其中，LM-CNN 模型的迭代次数最低，其
次是BP 神经网络与GD-CNN 模型。在训练时间
上，LM-CNN 模型的训练时间略大于BP 神经网
络，而GD-CNN 模型训练用时最多。这是由于
LM 算法具有快速收敛的优点，使得LM-CNN 模
型迭代次数最少，又因为CNN 模型结构较为复
杂，单次网络迭代所需要的时间更多，因此
BP 神经网络的训练时间反而更低。
虽然BP 神经网络具有更优的计算速度，但
是BP 神经网络的预测精度却并不理想。LM-
CNN、GD-CNN 和BP 神经网络模型计算的测试集
 
表 1   输变电工程造价历史数据样本
Table 1   Samples of historical cost data of power transmission and transformation projects
工程
编号
单位容量
造价/(元·(kV·A)–1)
主控
面积/m2
主变压器
容量/(MV·A)
主变压器
单价/(万元·台–1)
电缆/
万元
高压断路器
单价/(万元·台–1)
二次设备
单价/(万元·站–1)
征地补偿/
万元
1
218.7
1 924.0
120.0
644.0
51.3
4.0
441.0
117.3
2
343.3
4 327.0
240.0
819.0
112.7
6.0
813.0
227.2
…
…
…
…
…
…
…
…
…
23
278.1
4 156.0
180.0
603.0
123.0
2.0
710.3
138.0
24
306.5
2 531.0
120.0
578.5
72.0
4.0
498.5
189.7
 
0
0.2
0.4
0.6
0.8
1.0
y
0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9
1.0
y*
数据点；
拟合线；
参照线
y*=y
 
图 3   LM-CNN 模型训练效果
Fig. 3    Training effect of LM-CNN model
 
中国电力
第 56 卷
160



<!-- page 5/7 -->

预测结果如图4 所示，它们的平均预测精度分别
为97.87%、96.43% 和94.26%。
 
 
1
2
3
4
5
6
测试集样本编号
200
220
240
260
280
300
320
340
360
单位容量造价/元
真实值；
LM-CNN；
GD-CNN；
BP
 
图 4   网络模型预测结果对比
Fig. 4    Comparison of prediction results of
network models
 
 
均方根误差可以更加明显地表达模型的整体
预测性能，3 种模型的均方根误差分别为7.38 元/
(kV·A)、12.17 元/(kV·A) 和23.28 元/(kV·A)。其中
LM-CNN 模型预测结果的均方根误差更小，总体
预测精度更高。
为进一步分析模型预测结果，本文对比了
3 种网络模型的相对误差[25] 分布，如图5 所示。
由于BP 神经网络为全连接神经网络，容易出现
过拟合现象，使模型在测试集的计算结果中表现
不理想，致使BP 神经网络的相对误差波动更
大。此外，GD 算法容易使模型陷入局部最优，
因此基于LM 算法训练的CNN 模型具有更好的精
度与稳定性。
 
 
1
2
3
4
5
6
测试集样本编号
0
0.02
0.04
0.06
0.08
0.10
0.12
0.14
0.16
0.18
相对误差
LM-CNN 预测值；
GD-CNN 预测值；
BP 预测值
 
图 5   各模型相对误差表现
Fig. 5    Relative error performance of each model
  
4    结论
本文建立了基于CNN 的输变电工程造价自动
计算模型，利用LM 权重优化算法对模型参数进
行优化，并通过算例验证了模型在输变电工程单
位容量造价上的预测精确度。在LM-CNN、GD-
CNN 与BP 神经网络3 种模型预测对比中发现LM-
CNN 表现最优，其次是GD-CNN 模型；在3 种模
型的计算速度上，LM-CNN 模型略高于BP 神经网
络，但BP 神经网络的计算精度较低；相比GD 算
法，经过LM 算法优化的CNN 模型具有更好的收
敛表现，训练速度快，预测结果也更加稳定。本
次算例的不足之处在于历史数据样本数量相对较
少，没有检验模型在大样本情况下的计算表现。
参考文献：
林正冲, 戚思睿, 苟吉伟, 等. 新电改形势下集中化大型数据中心战
略投资和商业模式[J]. 中国电力, 2021, 54(11): 37–46.
LIN  Zhengchong,  QI  Sirui,  GOU  Jiwei,  et  al.  Strategic  investment
and business models of large centralized data centers under the new
power system reform[J]. Electric Power, 2021, 54(11): 37–46.
[1]
陈洪彦, 蒋文新, 郭晓丹. 输变电工程造价分析信息平台建设研
究[J]. 工业技术经济, 2016, 35(4): 101–108.
CHEN  Hongyan,  JIANG  Wenxin,  GUO  Xiaodan.  Research  on  the
construction  of  information  platform  about  cost  analysis  in  power
transmission  and  transform  project[J].  Journal  of  Industrial
Technological & Economics, 2016, 35(4): 101–108.
[2]
何勇萍, 俱鑫, 雍浩, 等. 基于PSO-SVR 的输变电工程造价权重预
测模型建立及分析[J]. 自动化技术与应用, 2020, 39(3): 98–102.
HE Yongping, JU Xin, YONG Hao, et al. Establishment and analysis
for  weight  prediction  model  of  transmission  and  transformation
project  cost  based  on  PSO-SVR[J].  Techniques  of  Automation  and
Applications, 2020, 39(3): 98–102.
[3]
NIU  Dongxiao,  HUA  Fuyu,  LI  Bingjie,  et  al.  Research  on  neural
network prediction of power transmission and transformation project
cost  based  on  GA-RBF  and  PSO-RBF[J].  Applied  Mechanics  and
Materials, 2014, 644-650: 2526–2531.
[4]
于波, 肖艳利, 刘尚科, 等. 基于PSO-ELM 算法的输变电工程造价
预测分析[J]. 信息技术, 2019, 43(4): 148–151, 156.
YU Bo, XIAO Yanli, LIU Shangke, et al. Cost prediction model of
transmission  and  transformation  engineering  based  on  PSO-ELM
[5]
第 2 期
武小琳等：基于LM-CNN 的输变电工程造价自动计算模型
161



<!-- page 6/7 -->

algorithm[J]. Information Technology, 2019, 43(4): 148–151, 156.
王宁宁, 王飞, 尹彦涛, 等. 基于支持向量机的变电工程造价预测研
究[J]. 建筑经济, 2016, 37(5): 48–52.
WANG Ningning, WANG Fei, YIN Yantao, et al. Research on cost
predicting  of  power  transformation  projects  based  on  SVM[J].
Construction Economy, 2016, 37(5): 48–52.
[6]
宋宗耘, 牛东晓, 肖鑫利, 等. 基于改进萤火虫算法优化SVM 的变
电工程造价预测[J]. 中国电力, 2017, 50(3): 168–173.
SONG  Zongyun,  NIU  Dongxiao,  XIAO  Xinli,  et  al.  Substation
engineering  cost  forecasting  method  based  on  modified  firefly
algorithm  and  support  vector  machine[J].  Electric  Power,  2017,
50(3): 168–173.
[7]
妙旭娟, 刘锦明, 高亮, 等. 基于主成分分析法和神经网络的技改工
程造价预测模型[J]. 内蒙古科技与经济, 2019(19): 37–40, 42.
MIAO  Xujuan,  LIU  Jinming,  GAO  Liang,  et  al.  Cost  prediction
model of technical renovation project based on principal component
analysis and neural network[J]. Inner Mongolia Science Technology
& Economy, 2019(19): 37–40, 42.
[8]
王鑫, 安磊, 张妍. 基于REGR-WNN 组合变权模型的输变电工程
造价预测[J]. 中国电力企业管理, 2016(13): 93–96.
WANG  Xin,  AN  Lei,  ZHANG  Yan.  Cost  prediction  of  power
transmission  and  transformation  project  based  on  REGR-WNN
combined  variable  weight  model[J].  China  Power  Enterprise
Management, 2016(13): 93–96.
[9]
王晓建, 朱婷涵, 劳咏昶, 等. 基于人工免疫优化神经网络的输变电
工程造价评估[J]. 浙江电力, 2018, 37(7): 62–67.
WANG  Xiaojian,  ZHU  Tinghan,  LAO  Yongchang,  et  al.  Cost
evaluation of power transmission and transformation project based on
artificial  immune  optimization  neural  network[J].  Zhejiang  Electric
Power, 2018, 37(7): 62–67.
[10]
LU  Y,  NIU  D  X,  QIU  J  P,  et  al.  Prediction  technology  of  power
transmission  and  transformation  project  cost  based  on  the
decomposition-integration[J]. Mathematical Problems in Engineering,
2015, 2015: 1–11.
[11]
郭琦, 付继业, 李珺, 等. 基于BIM 的输变电设计与造价信息共享
研究[J]. 工程经济, 2016, 26(1): 32–35.
GUO  Qi,  FU  Jiye,  LI  Jun,  et  al.  Research  on  power  transmission
design  and  cost  information  sharing  based  on  BIM[J].  Engineering
Economy, 2016, 26(1): 32–35.
[12]
ZANG H X, CHENG L L, DING T, et al. Hybrid method for short-
term  photovoltaic  power  forecasting  based  on  deep  convolutional
neural  network[J].  IET  Generation,  Transmission  &  Distribution,
[13]
2018, 12(20): 4557–4567.
周俊煌, 黄廷城, 谢小瑜, 等. 视频图像智能识别技术在输变电系统
中的应用研究综述[J]. 中国电力, 2021, 54(1): 124–134, 166.
ZHOU Junhuang, HUANG Tingcheng, XIE Xiaoyu, et al. Review of
application  research  of  video  image  intelligent  recognition
technology  in  power  transmission  and  distribution  systems[J].
Electric Power, 2021, 54(1): 124–134, 166.
[14]
汪际峰, 李鹏, 梁锦照, 等. 电力系统数字化历程与发展趋势[J]. 南
方电网技术, 2021, 15(11): 1–8.
WANG Jifeng, LI Peng, LIANG Jinzhao, et al. Development history
and trends of power system digitalization[J]. Southern Power System
Technology, 2021, 15(11): 1–8.
[15]
熊一, 詹智红, 柯方超, 等. 基于改进BP 神经网络的变电站检修运
维成本预测[J]. 电力科学与技术学报, 2021, 36(4): 44–52.
XIONG Yi, ZHAN Zhihong, KE Fangchao, et al. Overhaul operation
and maintenance cost prediction of substation based on improved BP
neural  network[J].  Journal  of  Electric  Power  Science  and
Technology, 2021, 36(4): 44–52.
[16]
XU  C  C,  WANG  Y,  YE  K,  et  al.  Research  on  transmission  line
project  cost  forecast  method  based  on  BP  neural  network[J].  IOP
Conference Series:Materials Science and Engineering, 2019, 688(5):
055074.
[17]
SHI Q Q, XU Q, ZHANG J P. Amended DV-hop scheme based on
N-gram  model  and  weighed  LM  algorithm[J].  Electronics  Letters,
2020, 56(5): 247–250.
[18]
张宏运, 马震, 乔欢欢. 输变电工程造价管理发展趋势及优化研
究[J]. 华东电力, 2012, 40(4): 544–547.
ZHANG  Hongyun,  MA  Zhen,  QIAO  Huanhuan.  Cost  management
development  and  optimization  for  power  transmission  and
transformation  projects[J].  East  China  Electric  Power,  2012,  40(4):
544–547.
[19]
伍也凡, 刘浩田, 肖振锋, 等. 考虑源-网-荷不确定性的增量配电网
规划研究综述[J]. 电力系统保护与控制, 2021, 49(8): 177–187.
WU  Yefan,  LIU  Haotian,  XIAO  Zhenfeng,  et  al.  Review  of
incremental distribution network planning considering the uncertainty
of  source-network-load[J].  Power  System  Protection  and  Control,
2021, 49(8): 177–187.
[20]
LIU D N, ZHANG X, GAO C C, et al. Cost management system of
electric  power  engineering  project  based  on  project  management
theory[J].  Journal  of  Intelligent  &  Fuzzy  Systems,  2018,  34(2):
975–984.
[21]
耿鹏云, 安磊, 王鑫. 基于数据挖掘技术的输电工程造价预测模型
[22]
中国电力
第 56 卷
162



<!-- page 7/7 -->

的建立与实现[J]. 现代电子技术, 2018, 41(4): 157–160.
GENG  Pengyun,  AN  Lei,  WANG  Xin.  Establishment  and
implementation of power transmission project's cost forecast model
based on data mining technology[J]. Modern Electronics Technique,
2018, 41(4): 157–160.
张旭东, 李飞, 刘迪, 等. 基于CNN 的产消群需求响应滚动优化策
略[J]. 中国电力, 2021, 54(2): 78–89.
ZHANG  Xudong,  LI  Fei,  LIU  Di,  et  al.  CNN-based  rolling
optimization  strategy  for  prosumer  group  in  demand  response[J].
Electric Power, 2021, 54(2): 78–89.
[23]
黄小龙. 基于蒙特卡洛法的输变电工程造价风险评估模型研
究[J]. 现代电子技术, 2017, 40(20): 178–180.
HUANG  Xiaolong.  Study  on  Monte-Carlo  method  based  risk
assessment  model  of  power  transmission  project  cost[J].  Modern
[24]
Electronics Technique, 2017, 40(20): 178–180.
郝海风, 朱承治, 彭晶. 基于小样本数据的输变电工程造价估算的
建模与仿真[J]. 自动化与仪器仪表, 2019(11): 157–160.
HAO Haifeng, ZHU Chengzhi, PENG Jing. Modeling and simulation
of cost estimation for transmission and distribution engineering based
on  small  sample  data[J].  Automation  &  Instrumentation,  2019(11):
157–160.
[25]
作者简介：
武小琳（1981—），女，硕士，高级工程师，从事工
程造价管理研究，E-mail：37318544@qq.com；
栾凌（1978—），女，通信作者，硕士，高级经济
师，从事工程造价管理研究，E-mail：Luanling19780225@
163.com。
（责任编辑　于静茹）
LM-CNN-based Automatic Cost Calculation Model for Power Transmission and
Transformation Projects
WU Xiaolin2, LUAN Ling1, PAN Lianwu2, LI Hailong2
(1. Shenyang Power Supply Company of State Grid Liaoning Electric Power Co., Ltd., Shenyang 110000, China; 2. State Grid Liaoning
Electric Power Co., Ltd., Shenyang 110006, China)
Abstract: The cost calculation of power transmission and transformation project is the core part of cost control technology. The
quality of the cost calculation model directly affects the efficiency and reliability of the cost management of power transmission and
transformation projects. However, the existing models cannot reconcile the computational speed, accuracy and stability. Considering
above-mentioned problems, firstly, a convolutional neural network model is constructed with its input and output determined
according to the practical cost requirements of the power transmission and transformation projects. Then, the historical cost data are
input into the network model as samples to calculate the network output. Finally, in view of the big difference between the expected
output and the actual output, the Levenberg-Marquart algorithm is utilized to optimize the weight parameters of the convolutional
neural network to complete the model training. Compared with the BP neural network and GD-CNN, the proposed model with higher
prediction accuracy and stability combines the advantages of Levenberg-Marquart algorithm and convolutional neural network model
to improve the calculation effect of power transmission and transformation project cost.
This work is supported by Science and Technology Project of SGCC (No.SGLNSY00HLJS2002775).
Keywords: power transmission and transformation project; Levenberg-Marquart algorithm; convolutional neural network; automatic
calculation model; cost control
第 2 期
武小琳等：基于LM-CNN 的输变电工程造价自动计算模型
163
