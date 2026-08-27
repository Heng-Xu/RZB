<!--
source: D6_决策方法/基于改进的AHP-CRITIC组合赋权与可拓评估模型的配电网综合评价方法_罗宁.pdf
sha256: f06b730fd65769eb5111b14581b6b6f1589a05ed82fc47c8f65cb6dc8465bdf6
method: pymupdf
pages: 11
-->

<!-- page 1/11 -->

第49 卷 第16 期                            电力系统保护与控制                              Vol.49 No.16 
2021 年8 月16 日                        Power System Protection and Control                          Aug. 16, 2021 
 
DOI: 10.19783/j.cnki.pspc.201235 
基于改进的AHP-CRITIC 组合赋权与可拓评估模型的 
配电网综合评价方法 
罗 宁
1，贺墨琳
1，高 华
1，姜志筠
2，张天东
2，赵佳伟
2，吴国鼎
2，李 智
2，胡 钋
2 
 (1.贵州电网有限责任公司电网规划研究中心，贵州 贵阳 550003；2.武汉大学电气与自动化学院，湖北 武汉 430072) 
摘要：针对配电网综合评价问题，提出了一种改进的基于最小二乘的AHP-CRITIC 组合赋权与可拓评估模型。针
对单一赋权法具有一定偏向性的问题，通过层次分析法和CRITIC 法分别确定主观权重与客观权重，构建基于最
小二乘的组合赋权模型并采用遗传算法求解，从而确定综合权重。针对传统可拓评估模型中经典域确定的主观性，
引入三角模糊数对其进行构建。针对现有关联度与等级变量特征值计算的准确性问题，分别提出了关联度的修正
方法与等级扩展方法。算例表明，所提方法能够对配电网进行科学合理的分类，评价结果可信度高。 
关键词：配电网评价；改进AHP-CRITIC 法；改进可拓评估模型；最小二乘法；遗传算法 
Comprehensive evaluation method for a distribution network based on improved AHP-CRITIC  
combination weighting and an extension evaluation model 
LUO Ning1, HE Molin1, GAO Hua1, JIANG Zhijun2, ZHANG Tiandong2, ZHAO Jiawei2, WU Guoding2, LI Zhi2, HU Po2 
(1. Power Grid Planning and Research Center, Guizhou Power Grid Co., Ltd., Guiyang 550003, China; 
2. School of Electrical Engineering and Automation, Wuhan University, Wuhan 430072, China) 
Abstract: For comprehensive evaluation of a distribution network, this paper proposes an improved AHP-CRITIC 
combination weighting and extension evaluation model based on least squares. Since the single weighting method has a 
certain bias, the subjective weight and the objective weight are determined by an Analytic Hierarchical Process (AHP) and 
CRITIC method respectively. A combined weighting model based on least squares is constructed and solved by a genetic 
algorithm to determine the comprehensive weight. The subjectivity of the classic domain determination in the extension 
evaluation model is constructed by introducing triangular fuzzy numbers. To ensure the accuracy of the existing 
correlation degree and the calculation accuracy of the eigenvalues of the rank variables, we propose a correlation degree 
correction method and the rank expansion method. The calculation example shows that the method can classify the 
distribution network scientifically and reasonably, and the evaluation result has high credibility. 
This work is supported by the National Natural Science Foundation of China (No. 51777142) and the Electric Power 
Planning Special Research Project of Guizhou Power Grid Co., Ltd. (No. 060000QQ00190011). 
Key words: distribution network evaluation; improved AHP-CRITIC method; improved extension evaluation model; 
least squares method; genetic algorithm 
0  引言 
科学、合理地评价配电网，有利于较为准确地
定位其运行中的薄弱环节、提高供电效率以及制定 
 
基金项目：国家自然科学基金项目资助(51777142)；贵州电网
有限责任公司电力规划专题研究项目资助(060000QQ00190011) 
配电网未来的发展战略，对优化资源配置、提高运
行经济性具有重要意义。围绕如何对配电网进行快
速、准确的评价，诸多学者进行了多方面的研究，
取得了一定的成果。在赋权方法上：文献[1]运用
AHP 法对配电网进行风险评估，文献[2]提出了一种
新的判断矩阵的构造方法对AHP 法进行改进，简化
了运算过程，文献[3]则将AHP 与三角模糊数结合，



<!-- page 2/11 -->

罗 宁，等   基于改进的AHP-CRITIC 组合赋权与可拓评估模型的配电网综合评价方法            - 87 - 
 
提出了一种模糊多属性赋权方法，文献[4]采用了区
间层次分析法进行赋权，这些赋权方法主观性较强；
在客观赋权方面，文献[5]运用主成分分析法进行配
电网指标权重分配，文献[6-9]运用CRITIC 法求得
客观权重，强化了指标间的差异性，文献[10-11]运
用熵权法进行权重分配与配电网评估。主、客观赋
权方法均无法兼顾权重的主观性和客观性，而组合
赋权法能有效地综合二者优点。文献[12-13]按照比
例对主、客观权重加权求得综合权重，但该方法具
有较大主观性，文献[14]提出了一种依据最小鉴别
信息原理求取综合权重的方法，文献[15-17]则基于
最小二乘法组合主客观权重，但传统最小二乘法组
合赋权具有一定的局限性。在评价方法上，文献
[18-23]运用了TOPSIS 法，通过计算贴近度进行评
价，文献[24]构建多级可拓评估模型，对配电网经
济效益进行评价。但现有可拓评估模型主要具有如
下三点局限性： 
1) 通过主观判断直接赋予经典域区间，主观随
意性较强； 
2) 无法准确反映指标经典域区间长度变化对
关联度计算结果的影响； 
3) 仅根据所确定的等级来计算等级变量特征
值，因此当评价对象位于最低等级或最高等级时，
将会丢失最低等级左侧与最高等级右侧的信息，从
而会造成这两个等级计算不准确的情况。 
针对上述问题，本文提出了一种改进的基于最
小二乘的AHP-CRITIC 组合赋权方法。通过改进传
统最小二乘法赋权中评价值计算方法进行合理赋
权；引入三角模糊数确定各指标在各等级下的经典
域区间；提出了一种关联度函数计算方法，能够反
映区间长度变化对关联度的影响；提出了一种等级
扩展方法，通过对最高与最低等级进行扩展，补充
相应的关联度信息，使得等级变量特征值计算更为
精确。 
1   指标体系构建 
根据指标体系构建应满足全面性、合理性、独
立性的原则，本文构建配电网评价指标体系如图1
所示。其中：设3 个一级指标，即效果类指标、特
征类指标、技术类指标；设6 个二级指标，即供电
可靠性、经济效益、社会效益、负荷供应能力、网
络结构水平、智能化水平；设33 个三级指标。 
 
图1 配电网评价指标体系 
Fig. 1 Evaluation index system of distribution network
本文所构建配电网评价指标体系覆盖全面，既
包含了配电网评价中的部分经典指标，又采用了反
映现代配电网特性的新颖指标，部分指标说明如下。 
1) 单位配电容量供电量



<!-- page 3/11 -->

- 88 -                                         电力系统保护与控制   
 
单位配电容量供电量是当年供电量与变压器总
容量的比值，反映配电网变压器的供电效率，其值
越大说明变压器容量的整体利用率越高，越小则说
明利用率越低，即 
100%
=
×
当年供电量
单位配电容量供电量
变压器总容量
 
2) 单位售电量GDP 
单位售电量GDP 是地区国民生产总值与配电
网总售电量的比值，反映地区配电网的电力供应对
国民经济的贡献程度，即 
GDP
100%
=
×
地区国民生产总值
单位售电量
配电网总售电量
 
3) 电力弹性系数 
电力弹性系数是供电量年均增长率与地区国民
生产总值年均增长率的比值，反映配电网的经济发
展适应性，即 
100%
GDP
=
×
供电量年均增长率
电力弹性系数
区域
年均增长率
 
4) 新能源电量上网率 
新能源电力上网率是新能源发电量与地区电网
总装机容量的比值，反映配电网新能源发电建设情
况，即 
100%
=
×
新能源发电量
新能源电量上网率
地区电网总装机容量
 
2  基于改进的AHP-CRITIC 组合赋权 
2.1 层次分析法 
层次分析法(AHP)是一种主观赋权法，其主要
步骤如下述。 
1) 构建判断矩阵 
根据表1 所示1~9 标度，参考专家意见，进行
各指标间重要性的判断，并以比值表示判断结果，
构建判断矩阵。 
表1 判断矩阵1~9 标度对应表 
Table 1 Judgment matrix 1 ~ 9 scale correspondence table 
取值 
重要性程度 
1 
同等重要 
3 
略微重要 
5 
一般重要 
7 
非常重要 
9 
极端重要 
2) 一致性检验 
求取判断矩阵的最大特征值，依照式(1)、式(2)
计算一致性比率CR 值，若满足
0.1
CR <
，则认为判
断矩阵通过一致性检验。 
 
1
m
n
CI
n
λ −
=
−
              (1) 
CR
CI RI
=
              (2) 
式中：
m
λ 为判断矩阵的最大特征值；n 为判断矩阵
的阶数；CI 为一致性指标；RI 为随机一致性指标。 
3) 求解权重 
对通过一致性检验的判断矩阵，以其归一化的
特征向量作为权向量，求得权重
(
1,2,
, )
j j
n
ϕ
=
"
。 
2.2 CRITIC 法 
CRITIC 法各个指标的客观权重是通过指标数
据中蕴含的信息量计算得到的，而信息量是由指标
间的标准差和相关系数进行表示的。作为熵权法的
一种改进，它充分表现出指标间的差异性与冲突性，
具有很强的实用性。其具体计算步骤如下所述。 
1) 指标标准化 
由于指标量纲不同，需要对指标进行标准化处
理，于是由指标矩阵S (维数为m
n
×
，m 为样本数，
n 为指标数)得到标准化矩阵
′
S 。效益型指标的标准
化处理式为 
min(
)
max(
)
min(
)
ij
j
ij
j
j
s
s
s
s
s
−
′ =
−
          
(3) 
成本型指标的标准化处理式为 
( )
max
max(
)
min(
)
j
ij
ij
j
j
s
s
s
s
s
−
′ =
−
          
(4) 
对于区间型指标，采用三角形区间变化进行处
理，设最优属性值为
op
s ，指标容许区间为
,
j
j
a a
′
′′
⎡
⎤
⎣
⎦，
ja′ 为该指标无法容忍下限，ja′′ 为该指标无法容忍上
限，其标准化处理式为 
(
) (
)
(
) (
)
op
op
op
op
op
op
1
1
0
ij
j
j
ij
ij
ij
j
ij
j
ij
j
ij
j
s
s
s
a
a
s
s
s
s
s
a
s
s
s
a
s
a
s
a
⎧
′
′
−
−
−
⎪⎪
′
′′
′′
=
−
−
−
<
⎨
⎪
′
′′
<
>
⎪⎩
≤
≤
≤
或
 (5) 
2) 标准矩阵标准差、相关系数确定 
CRITIC 法以标准差和相关系数反映各指标间
的差异性与冲突性。标准化矩阵
′
S 的各指标的标准
差和指标间的相关系数计算式分别为 
(
)
2
1
1
1,2,
,
m
j
ij
j
i
s
s
j
n
m
ξ
=
′
′
=
−
=
∑
"
     
(6) 
)
(
(
)
cov
,
,
,
1,2,
,
ij
i
j
i
j
r
S S
i j
n
ξ ξ
′
′
=
=
"
    
(7) 
式中：
jξ 为第j 个指标的标准差；
ijr 为第i 个指标



<!-- page 4/11 -->

罗 宁，等   基于改进的AHP-CRITIC 组合赋权与可拓评估模型的配电网综合评价方法            - 89 - 
 
与第j 个指标间的相关系数；
iS′ 、
jS′ 分别为标准化
矩阵
′
S 的第i 、j 列。 
3) 计算客观权重 
第j 个指标所包含的信息量
j
E 的计算式为 
(
)
1
1
n
j
j
ij
i
E
r
ξ
=
=
−
∑
            (8) 
j
E 越大，表示该指标所蕴含的信息量越大，则
该指标在评价体系中所占的权重也就越大。 
将第j 个指标的信息量占总信息量的比重作为
该指标的客观权重
j
σ ，其计算式为 
1
n
j
j
j
j
E
E
σ
=
=
∑
              (9) 
2.3 改进的最小二乘法组合赋权 
层次分析法具有一定的主观局限性。CRITIC
法无法根据实际情况做出适合的主观偏向，过于依
赖原始数据，具有较大的客观局限性。因此需要进
行组合赋权，设其权重为
j
w ，则第i 个评价对象的
评价值为 
( )
1
1,2,
,
,
1,2,
,
n
i
j
ij
j
f
w
w
s
i
m
j
n
=
′
=
⋅
=
=
∑
"
"
  (10) 
显然，综合权重
j
w 对应的评价值
( )
if
w 与主观权
重
j
ϕ 对应的评价值
( )
if
ϕ 以及与客观权重
j
σ 对应的
评价值
( )
if
σ 偏差应越小越好，据此传统的基于最小
二乘法的AHP 和CRITIC 组合赋权的计算式为 
(
)
(
)
2
2
1
1
1
min
s.t.
1
0
m
n
j
j
ij
j
j
ij
i
j
n
j
j
i
F
w
s
w
s
w
w
ϕ
σ
=
=
=
⎧
⎡
⎤
⎡
⎤
′
′
=
−
+
−
⎪
⎣
⎦
⎣
⎦
⎪⎨
⎪
=
≥
⎪⎩
∑∑
∑
(11) 
利用式(10)无法对评价对象进行清晰分类，且
其仅采用权重与标准化矩阵相乘计算评价值，而线
性相乘法仅能反映评价值计算中的线性部分，无法
准确反映评价值大小，并且最小二乘法式(11)仅通
过式(10)表示评价值，因而无法准确地确定综合权
重。为此，本文采用等级变量特征值来衡量评价对
象的最终排序结果，提出了一种基于等级变量特征
值的改进最小二乘法组合赋权方法。其将传统评价
值替换为等级变量特征值，后者为输入权重的函数，
即输入一组权重，经可拓评估模型关联度计算等步
骤，得出一组对应的等级变量特征值。改进后的最
小二乘组合赋权模型为 
( )
( )
(
)
( )
( )
(
)
2
2
1
1
min
s.t.
1
s.t.
min(
,
)
max(
,
)
m
i
i
i
i
i
n
j
j
j
j
j
j
j
F
T w
T
T w
T
w
w
ϕ
σ
ϕ σ
ϕ σ
=
=
⎧
=
−
+
−
⎪
⎪⎪⎨
=
⎪
⎪
⎪⎩
∑
∑
≤
≤
 
(12)
 
式中，
( )
iT w 、
( )
iT ϕ 、
( )
iT σ 表示当输入权重分别
为w 、ϕ 、σ 时，第i 个评价对象的等级变量特征
值，其计算方法如式(31)。 
本文采用遗传算法对式(12)进行求解，为了解
决其易陷入局部最优且收敛速度慢的问题，做出两
点改进：(1) 采用均匀分区多种群初始化方法，以使
初始种群分布尽可能均匀；(2) 采用自适应的交叉概
率
cp 和变异概率
m
p ，其计算式分别为 
max
c0
avg
max
min
c
c0
avg
,
,
f
f
p
f
f
f
f
p
p
f
f
′
−
⎧
′
⎪
−
= ⎨
⎪
′ <
⎩
≥
      (13) 
max
m0
avg
max
min
m
m0
avg
,
,
f
f
p
f
f
f
f
p
p
f
f
−
⎧
⎪
−
= ⎨
⎪
<
⎩
≥
       (14) 
式中：f ′ 为进行交叉操作的两个个体中适应度值较
大的一个；f 为进行变异操作的个体适应度值；
max
f
、
min
f
和
avg
f
分别为种群最大、最小和平均适
应度值；
c0
p 和
m0
p
为(0,1)内的常数。对交叉和变异
后的新种群采用竞赛选择法不断进行选择，最终获
得综合权重。 
3   基于改进的可拓评估模型的评价方法 
基于引言中所述传统可拓评估模型的局限性，
本文提出了一种改进的可拓评估模型。通过引入三
角模糊数确定经典域区间，克服传统模型的主观随
意性；通过添加一系数，修正关联度计算式，以反
映可拓评估模型中经典域区间长度变化对关联度的
影响；通过等级扩展，保证最低等级与最高等级两侧
关联度的完整性，从而提高了等级变量特征值计算的
准确性。构建改进的可拓评估模型具体步骤如下述。 
1) 利用三角模糊数确定评价等级与经典域 
可拓评估模型通过有序三元组
(
)
,
,
R
N C V
=
来
表述评价对象及其指标。N 表示评价对象，C 表示
各指标，V 表示该事物各指标对应的量值。 
根据配电网的具体情况和评价标准，将配电网
评价等级共分为q 个等级，由各等级的具体情况确



<!-- page 5/11 -->

- 90 -                                         电力系统保护与控制   
 
定其下各指标所对应的经典域，为提高经典域设置
的准确性，本文引入三角模糊数确定经典域的上下
界，通过有序三元组形式表示经典域Rp，即 
(
)
(
)
(
)
1
1
1
1
1
1
1
(
,
,
) , (
,
,
)
(
,
,
) , (
,
,
)
(
,
,
) , (
,
,
)
l
o
u
l
o
u
p
p
p
p
p
p
l
o
u
l
o
u
p
j
jp
jp
jp
jp
jp
jp
l
o
u
l
o
u
n
np
np
np
np
np
np
N
C
a
a
a
b
b
b
R
C
a
a
a
b
b
b
C
a
a
a
b
b
b
⎡
⎤
⎢
⎥
⎢
⎥
⎢
⎥
= ⎢
⎥
⎢
⎥
⎢
⎥
⎢
⎥
⎢
⎥
⎣
⎦
#
#
#
#
 
 (15) 
式中：(
)
,
,
l
o
u
jp
jp
jp
a
a
a
为第p 个等级下第j 个指标所
对应经典域下界的三角模糊数，表示经典域下界位
于区间(
)
,
l
u
jp
jp
a
a
内，且其估计值为
o
jp
a ；同理，
(
)
,
,
l
o
u
jp
jp
jp
b
b
b
为经典域上界的三角模糊数，表示经典
域上界位于区间(
)
,
l
u
jp
jp
b
b
内，且其估计值为
o
jp
b 。 
由于区间数难以直接计算，故而采用期望模糊
连续区间数算子(EFC-OWG 算子)，将三角模糊数转
化为确定值，即 
(
)
(
)
1
1
2
l
o
o
u
jp
jp
jp
jp
jp
a
a
a
a
a
η
η
−
=
+
+
      (16) 
(
)
(
)
1
1
2
l
o
o
u
jp
jp
jp
jp
jp
b
b
b
b
b
η
η
−
=
+
+
      (17) 
式中，η 为风险偏好程度参数，本文取值为0.5。 
2) 确定各指标节域 
在基于经典域确定各指标的取值范围时，本文
设定节域
tR 为经典域的极限取值范围，即 
1
1
1
1
1
(
,
)
(
,
)
(
,
)
t
t
t
t
j
jt
j
jt
jt
n
nt
n
nt
nt
N
C
V
N
C
a
b
R
C
V
C
a
b
C
V
C
a
b
⎡
⎤
⎡
⎤
⎢
⎥
⎢
⎥
⎢
⎥
⎢
⎥
⎢
⎥
⎢
⎥
=
=
⎢
⎥
⎢
⎥
⎢
⎥
⎢
⎥
⎢
⎥
⎢
⎥
⎣
⎦
⎣
⎦
#
#
#
#
#
#
#
#
   
(18) 
式中，
jt
a 、
jt
b 为在所有等级下第j 个指标所对应
的下界和上界，即该指标容许取值范围。 
3) 关联度函数与等级变量特征值的计算 
各等级关联度与取值点到各等级经典域区间的
距离
(
,
)
j
jp
v V
ρ
有关，因此可构造如下关联度函数： 
(
)
(
)
(
)
(
)
,
,
,
,
j
jp
j
jp
jp
jp
j
jp
j
jp
j
jt
j
jp
v V
v
V
V
D
v V
v
V
v V
v V
ρ
ρ
ρ
ρ
⎧
⎪
−
∈
⎪⎪
= ⎨
⎪
∉
⎪
−
⎪⎩
   (19) 
其中 
  
(
)
,
2
2
jp
jp
jp
jp
j
jp
j
a
b
b
a
v V
v
ρ
+
−
=
−
−
    
(20) 
jp
jp
jp
V
b
a
=
−
            (21) 
 
(
)
,
2
2
jt
jt
jt
jt
j
jt
j
a
b
b
a
v V
v
ρ
+
−
=
−
−
     
(22) 
jt
jt
jt
V
b
a
=
−
            (23) 
这种计算方法具有一定的局限性。如图2(a)和
图2(b)所示，当
j
jp
v
V
∉
时，若经典域区间的长度变
长，则表示指标值的点与区间的相关程度应更高，
反之，若区间长度变短，则点与区间的相关程度应
更低。但是依照传统的可拓评估模型关联度的计算
方法，此时这两种情况下点到经典域区间的距离均
为
( ,( , ))
v a b
v
a
ρ
=
−
，因而无法计及区间长度变化
对于关联度的影响。 
 
图2 区间长度变化对关联度影响示意图 
Fig. 2 Schematic diagram of the influence of interval length 
changes on the degree of association 
对此，本文提出一种改进的可拓评估模型，即在
式(19)中添加一个能反映区间长度变化的系数λ ： 
(
)
(
)
(
)
(
)
,
,
,
,
j
jp
j
jp
jp
jp
j
jp
j
jp
j
jt
j
jp
v V
v
V
V
D
v V
v
V
v V
v V
ρ
ρ
λ
ρ
ρ
λ
⎧
⎪
−
∈
⎪⎪
= ⎨
⋅
⎪
∉
⎪
−
⋅
⎪⎩
  (24) 
其中 
(
)
jt
jt
jp
jp
b
a
q
b
a
λ
−
=
⋅
−
           (25) 
利用式(19)中的经典域区间长度
jp
jp
b
a
−
与式
(23)中的节域长度
jt
jt
b
a
−
来计算λ ，并且将其置于
式(24)中形成
(
,
)
j
jp
v V
ρ
λ
⋅
，其原理是以每个经典域
的平均长度为标准，若实际经典域长度大于平均长
度，则通过该系数可反映出区间长度变长所造成的
关联度增大，反之，则可反映出区间长度变短所造
成的关联度减小，从而解决了区间长度变化对于关
联度计算准确性的影响问题。



<!-- page 6/11 -->

罗 宁，等   基于改进的AHP-CRITIC 组合赋权与可拓评估模型的配电网综合评价方法            - 91 - 
 
利用式(24)，每一个评价对象都可得一个其各
指标与对应的各评价等级的关联度矩阵
n q
×
D
。通过
所求权重
j
w 和第j 个指标对应第p 个评价等级的
关联度
jp
D ，便可得第i 个评价对象对第p 个评价等
级的关联度
ip
K (
1, 2,
,
i
m
=
"
, 
1, 2,
,
p
q
=
"
)，即 
1
n
ip
j
jp
j
K
w D
=
= ∑
              
(26) 
从
ip
K 中可以得到第i 个评价对象与所有等级
的最大关联度
0
ip
K
，即 
0
max(
),
1,2,
,
ip
i
K
K
i
m
=
=
"
       (27) 
0
ip
K
的所属列数
0p 即为第i 个评价对象所属的
等级。 
等级变量特征值可以更加精确地表示评价对象
的所属等级，其原理为将关联度归一化后，计算等
级的期望值，以此对同等级下各配电网进行排序比
较。但在评价对象属于最高等级或最低等级的情况
下，这种归一化方法只会考虑单侧信息，而丢失另
一侧信息，从而所得出的等级变量特征值可能与所
属等级不相符。因此，本文提出了一种等级扩展法，
首先利用式(28)，取原设等级数除以4 后的整数部
分作为需要扩展的等级数，再利用式(29)计算第j
个指标扩展等级的长度。最后利用式(30)对关联度
矩阵进行归一化，再依据式(31)计算等级变量特征
值，即 
4
add
q
q
⎡⎤
= ⎢⎥
⎣⎦
             (28) 
jt
jt
add
j
b
a
V
q
−
=
          (29) 
min(
)
max(
)
min(
)
ip
i
ip
i
i
K
K
K
K
K
−
′ =
−
        (30) 
1
1
1,2,
,
l
l
i
ip
ip
p
p
T
pK
K
i
m
=
=
′
′
=
=
∑
∑
"
     (31) 
增加了扩展级的等级变量特征值计算，有效避
免了上述最高等级或最低等级处丢失单侧信息的问
题，使得计算结果更加准确。 
4   算例分析 
应用本文所提出的基于改进的AHP-CRITIC 组
合赋权与可拓评估模型的配电网综合评价方法，根
据图1 所示的指标体系，对贵州省配电网进行综合
评价。 
1) 基于AHP 的权重 
构造一级指标的判断矩阵、各一级指标下二级
指标间的判断矩阵与各二级指标下三级指标间的判
断矩阵，求得一级指标对目标层的权重和各下级指
标占对应上级指标的权重，依次相乘即为各三级指
标对目标层的权重，如表2 所示。 
表2 基于AHP 的三级指标对目标层的权重 
Table 2 Weight of the third-level index based on  
AHP to the target layer 
指标
C1 
C2 
C3 
"  
C31 
C32 
C33 
权重
0.114
0.072
0.045
"  
0.025 
0.014
0.088
2) 基于CRITIC 的权重 
根据式(3)—式(5)得到贵州省九个市配电网评
价指标标准化后的指标矩阵，利用式(6)—式(9)计算
其标准差与相关系数，据此得出信息量，进而确定
各三级指标对目标层的权重，如表3 所示。 
表3 基于CRITIC 的三级指标对目标层的权重 
Table 3 Weight of the third-level indicators based on  
CRITIC to the target layer 
指标
C1 
C2 
C3 
"  
"  
C31 
C32
C33
权重
0.002
0.024
0.045
"  
"  
0.030 
0.060
0.035
3) 经典域 
本文将贵州省配电网评价等级划分为4 个等
级，分别为不合格(1 级)、合格(2 级)、良好(3 级)
和优秀(4 级)，各三级指标在4 个等级下相应的经典
域如表4 所示。 
将表4 中33 个三级指标按其类型分为效益型
指标、成本型指标与区间型指标，据此分别按式
(3)—式(5)对经典域进行归一化处理。 
4) 三级指标的权重 
本文采用遗传算法求解改进后的最小二乘法组
合赋权模型的权重，当代数达到61 代时，目标函数
基本收敛，如图3 所示。各三级指标综合权重如表
5 所示。 
 
图3 目标函数的收敛情况 
Fig. 3 Convergence of the objective function



<!-- page 7/11 -->

- 92 -                                         电力系统保护与控制   
 
表4 各二级指标在4 个等级下相应的经典域 
Table 4 Corresponding classic domains of each secondary index under four levels 
指标 
1 级(不合格) 
2 级(合格) 
3 级(良好) 
4 级(优秀) 
供电可靠率RS-3 
(0.9895,0.99,0.9925)~ 
(0.9923,0.9925,0.9927) 
(0.9923,0.9925,0.9927)~ 
(0.9945,0.995,0.9956) 
(0.9945,0.995,0.9956)~ 
(0.9970,0.9975,0.9978) 
(0.9970,0.9975,0.9978)~ 
(0.9998,1,1) 
综合电压合格率 
(0.9790,0.98,0.9805)~ 
(0.9878,0.99,0.9915) 
(0.9878,0.99,0.9915)~ 
(0.9923~0.9925~0.9927) 
(0.9923~0.9925~0.9927)
~(0.9937,0.9950,0.9961) 
(0.9937,0.9950,0.9961)~ 
(0.9971,1,1) 
110 kV 主变N-1 通过率 
(17,20,22)~(38,40,41) 
(38,40,41)~(55,60,65) 
(55,60,65)~ (75,80,83) 
(75,80,83)~(95,100,100) 
110 kV 线路N-1 通过率 
(17,20,22)~(38,40,41) 
(38,40,41)~(55,60,65) 
(55,60,65)~ (75,80,83) 
(75,80,83)~(95,100,100) 
35 kV 主变N-1 通过率 
(17,20,22)~(38,40,41) 
(38,40,41)~(55,60,65) 
(55,60,65)~ (75,80,83) 
(75,80,83)~(95,100,100) 
35 kV 线路N-1 通过率 
(17,20,22)~(58,60,65) 
(38,40,41)~(55,60,65) 
(55,60,65)~ (75,80,83) 
(75,80,83)~(95,100,100) 
用户年均停电时间 
(28,30,32) 
(23,25,26) 
(18,20,21) 
(9,10,11)~(4,5,6.5) 
低电压用户比例 
(10,12,14)~(8,9,10) 
(8,9,10)~(4.5,6,6.5) 
(4.5,6,6.5)~(2,3,4.5) 
(2,3,4.5)~(0.3,1,2) 
110 kV 及以下综合线损率 
(10,12,14)~(8,9,10) 
(8,9,10)~(4.5,6,6.5) 
(4.5,6,6.5)~(2,3,4.5) 
(2,3,4.5)~(0.3,1,2) 
10 kV 及以下综合线损率 
(10,12,14)~(8,9,10) 
(8,9,10)~(4.5,6,6.5) 
(4.5,6,6.5)~(2,3,4.5) 
(2,3,4.5)~(0.3,1,2) 
单位配电容量供电量 
(0,0,0.025)~ 
(0.15,0.2,0.35) 
(0.15,0.2,0.35)~ 
(0.33,0.4,0.41) 
(0.33,0.4,0.41)~ 
(0.53,0.6,0.79) 
(0.53,0.6,0.79)~(0.73,0.8,0.89)
单位电网投资增供负荷 
(0,0,0.15)~ (2.16,3,4.25) 
(2.16,3,4.25)~ 
(4.47,6,7.54) 
(4.47,6,7.54)~ 
(8.34,9,10.17) 
(8.34,9,10.17)~ 
(11.93,12,12.24) 
单位售电量GDP 
(8.75,9,10.06)~ 
(10.66,11,12.08) 
(10.66,11,12.08)~ 
(12.33,13,14.75) 
(12.33,13,14.75)~ 
(15.27,16,17.37) 
(15.27,16,17.37)~ 
(17.24,18,19.42) 
用户满意度 
(73,75,78)~ (80,82,85) 
(80,82,85)~ (85,87,88) 
(85,87,88)~ (90,93,95) 
(90,93,95)~(97,100,100) 
电力弹性系数 
(0,0,0.15)~ (45,50,63) 
(45,50,63)~ (75,80,86) 
(75,80,86)~ (96,100,105) 
(96,100,105)~(117,120,123) 
清洁能源消纳率 
(0.9695,0.97,0.9713)~ 
(0.9789,0.98,0.9814) 
(0.9789,0.98,0.9814)~ 
(0.9878,0.99,0.9909) 
(0.9878,0.99,0.9909)~ 
(0.9946,0.9950,0.9998) 
(0.9946,0.9950,0.9998)~ 
(0.9984,1,1) 
110 kV 容载比 
(1,1.1,1.2)~(1.38,1.4,1.47)
(1.38,1.4,1.47)~ 
(1.51,1.6,1.73) 
(1.51,1.6,1.73)~ 
(1.75,1.8,1.88) 
(1.75,1.8,1.88)~(1.89,1.9,1.95)
35 kV 容载比 
(1,1.1,1.2)~(1.38,1.4,1.47)
(1.38,1.4,1.47)~ 
(1.51,1.6,1.73) 
(1.51,1.6,1.73)~ 
(1.75,1.8,1.88) 
(1.75,1.8,1.88)~(1.89,1.9,1.95)
户均配变容量 
(1.33,1.5,1.74)~ 
(1.95,2,2.34) 
(1.95,2,2.34)~ 
(2.34,2.5,2.76) 
(2.34,2.5,2.76)~ 
(2.72,3,3.34) 
(2.72,3,3.34)~(3.37,3.5,3.51) 
中压配电网重载线路占比 
(13.48,15,17.16)~ 
(10.58,12,13.96) 
(10.58,12,13.96)~ 
(7.32,9,9.27) 
(7.32,9,9.27)~ 
(5.78,6,6.38) 
(5.78,6,6.38)~(3.79,4,5.39) 
中压配电网重载配变占比 
(9.17,10,11.23)~ 
(7.71,8,8.84) 
(7.71,8,8.84)~ 
(4.37,5,5.67) 
(4.37,5,5.67)~ 
(2.86,3,3.33) 
(2.86,3,3.33)~(0.42,1,1.64) 
典型接线比例 
(55.77,60,65.19)~ 
(76.79,80,83.76) 
(76.79,80,83.76)~ 
(87.43,90,92.47) 
(87.43,90,92.47)~ 
(93.28,95,96.18) 
(93.28,95,96.18)~ 
(95.33,10,100) 
站间联络率 
(0,0,0)~ (38.67,40,43.82) 
(38.67,40,43.82)~ 
(51.38,60,73.28) 
(51.38,60,73.28)~ 
(74.29,80,97.27) 
(74.29,80,97.27)~ 
(95.33,10,100) 
线路可转供电率 
(0,0,0)~ (17.89,20,37.96) 
(17.89,20,37.96)~ 
(43.28,50,52.48) 
(43.28,50,52.48)~ 
(61.28,70,85.68) 
(61.28,70,85.68)~ 
(95.33,100,100) 
中压线路平均负载率 
(8.5,10,11.5)~ 
(23.36,30,36.02) 
(23.36,30,36.02)~ 
(37.38,40,42.38) 
(37.38,40,42.38)~ 
(43.67,50,58.29) 
(43.67,50,58.29)~ 
(59.42,60,63.42) 
高损耗配变台数比例 
(2.52,3,3.51)~ 
(1.95,2,2.05) 
(1.95,2,2.05)~ 
(1.36,1.5,1.83) 
(1.36,1.5,1.83)~ 
(0.75,1,1.24) 
(0.75,1,1.24)~(0.45,0.5,0.64) 
线路平均分段数 
(0,0,0)~ (1.95,2,2.05) 
(1.95,2,2.05)~ 
(2.47,3,3.93) 
(2.47,3,3.93)~ 
(3.87,4,4.17) 
(3.87,4,4.17)~(4.53,5,5.67) 
线路绝缘化率 
(0,0,0)~ (18.79.20.21.34) 
(18.79.20.21.34)~ 
(28.37,40,52.39) 
(28.37,40,52.39)~ 
(55.27,60,62.29) 
(55.27,60,62.29)~ 
(66.43,80,82.58) 
线路电缆化率 
(0,0,0)~ (3.4,5,6.75) 
(3.4,5,6.75)~ 
(8.82,10,11.38) 
(8.82,10,11.38)~ 
(13.28,15,21.68) 
(13.28,15,21.68)~ 
(23.53,25,27.53) 
智能电表覆盖率 
(88.67,90,92.72)~ 
(92.17,93,94.19) 
(92.17,93,94.19)~ 
(94.27,95,97.45) 
(94.27,95,97.45)~ 
(97.92,98,99.23) 
(97.92,98,99.23)~ 
(95.33,100,100) 
配电自动化覆盖率 
(0,0,0)~ (27.5,30,32.5) 
(27.5,30,32.5)~ 
(45.5,50,55.5) 
(45.5,50,55.5)~ 
(66.5,70,73.5) 
(66.5,70,73.5)~(86.5,90,92.5)
新能源电量上网比例 
(0,0,0)~ (16.5,20,24.5) 
(16.5,20,24.5)~ 
(45.5,50,55.5) 
(45.5,50,55.5)~ 
(66.5,70,73.5) 
(66.5,70,73.5)~(86.5,90,92.5)
通信数据网覆盖率 
(16,20,23)~ (47.8,50,51.9)
(47.8,50,51.9)~ 
(64.5,70,77.5) 
(64.5,70,77.5)~ 
(86.5,90,92.5) 
(86.5,90,92.5)~ 
(95.33,100,100)



<!-- page 8/11 -->

罗 宁，等   基于改进的AHP-CRITIC 组合赋权与可拓评估模型的配电网综合评价方法            - 93 - 
 
表5 各三级指标的综合权重 
Table 5 Comprehensive weight of each third indicator 
指标 
C1 
C2 
C3 
C4 
C5 
C6 
C7 
C8 
C9 
C10 
C11 
权重 
0.021 
0.025 
0.043 
0.035 
0.037 
0.015 
0.043 
0.029 
0.038 
0.015 
0.027 
指标 
C12 
C13 
C14 
C15 
C16 
C17 
C18 
C19 
C20 
C21 
C22 
权重 
0.040 
0.029 
0.009 
0.043 
0.043 
0.037 
0.038 
0.026 
0.032 
0.002 
0.021 
指标 
C23 
C24 
C25 
C26 
C27 
C28 
C29 
C30 
C31 
C32 
C33 
权重 
0.031 
0.014 
0.027 
0.030 
0.043 
0.035 
0.043 
0.039 
0.003 
0.043 
0.043 
5) 九市配电网所属等级与排序结果 
利用式(24)，计算贵州省九市配电网的三级指
标与4 个等级及扩展级的关联度矩阵，其中贵阳市
配电网部分三级指标与4 个等级及扩展级的关联度
如表6 所示。 
根据式(26)将所求得综合权重与对应关联度相 
乘并求和，得到贵州省九市配电网与4 个等级及扩
展级的关联度如表7 所示。 
加入扩展级后，补充了最低等级左侧与最高等
级右侧的信息，使得等级变量特征值的计算更为准
确，根据式(28)—式(31)，可得九市配电网所属等级
与等级变量特征值，如表8 所示。 
表6 贵阳市配电网部分三级指标与4 个等级及扩展级的关联度 
Table 6 Correlation between some third-level indicators and four levels of the distribution network in Guiyang 
指标 
扩展级 
1 级 
2 级 
3 级 
4 级 
扩展级 
C1 
-0.646 4 
-0.557 4 
-0.406 2 
-0.123 0 
 0.241 6 
-0.302 8 
C2 
-0.606 8 
-0.211 2 
-0.108 1 
 0.334 7 
-0.194 8 
-0.329 5 
C3 
-0.396 6 
-0.177 4 
0.267 2 
-0.083 2 
-0.296 2 
-0.416 2 
C4 
-0.582 5 
-0.474 9 
-0.293 9 
0.110 4 
-0.050 1 
-0.342 5 
… 
 … 
… 
… 
… 
… 
… 
C32 
-0.007 9 
0.008 9 
-0.432 9 
-0.701 9 
-0.766 8 
-0.798 4 
C33 
-0.760 3 
-0.605 4 
-0.503 4 
-0.180 6 
0.431 9 
-0.142 0 
表7 贵州省九市配电网与4 个等级及扩展级的关联度 
Table 7 Correlation between the distribution network of nine cities in Guizhou province and four grades 
对象 
扩展级 
1 级 
2 级 
3 级 
4 级 
扩展级 
贵阳 
-0.639 1 
-0.474 2 
-0.343 3 
-0.154 8 
-0.044 2 
-0.262 9 
遵义 
-0.477 1 
-0.279 9 
-0.109 3 
-0.111 4 
-0.284 1 
-0.415 6 
六盘水 
-0.510 3 
-0.338 9 
-0.174 9 
-0.150 6 
-0.195 0 
-0.360 8 
安顺 
-0.458 1 
-0.222 8 
-0.106 7 
-0.112 7 
-0.306 5 
-0.444 6 
凯里 
-0.495 2 
-0.320 9 
-0.169 5 
-0.131 3 
-0.194 5 
-0.397 4 
都匀 
-0.499 9 
-0.232 9 
-0.136 6 
-0.142 4 
-0.303 5 
-0.411 1 
兴义 
-0.497 3 
-0.226 9 
-0.093 8 
-0.107 5 
-0.270 1 
-0.422 6 
毕节 
-0.466 5 
-0.172 9 
-0.182 3 
-0.244 0 
-0.306 3 
-0.430 3 
铜仁 
-0.483 0 
-0.199 3 
-0.180 5 
-0.197 0 
-0.288 6 
-0.405 6 
表8 基于传统评估方法与改进评估方法的贵州省九市配电网评价结果(括号内为传统方法的评价结果) 
Table 8 Evaluation results of the distribution network of nine cities in Guizhou Province based on the traditional evaluation 
 methods and the improved evaluation methods (the evaluation results of traditional methods in brackets) 
级别等 
贵阳市 
遵义市 
六盘水 
安顺市 
凯里市 
都匀市 
兴义市 
毕节市 
铜仁市 
所属级别 
4(4) 
2(3) 
3(3) 
2(2) 
3(3) 
2(2) 
2(3) 
1(1) 
2(3) 
等级变量特征值 
3.38 
(3.37) 
2.62 
(2.84) 
2.95 
(2.92) 
2.41 
(2.05) 
2.86 
(2.97) 
2.59 
(2.30) 
2.58 
(2.74) 
2.36 
(2.29) 
2.67 
(2.90) 
排名 
1(1) 
5(5) 
2(3) 
8(9) 
3(2) 
6(7) 
7(6) 
9(8) 
4(4)



<!-- page 9/11 -->

罗 宁，等   基于改进的AHP-CRITIC 组合赋权与可拓评估模型的配电网综合评价方法            - 94 - 
 
6) 九市配电网二级指标评价结果及对比 
利用可拓评估模型，可以得到贵州省九市配电
网六个二级指标的评价结果，如图4 所示。 
 
图4 九市配电网六个二级指标的评价结果 
Fig. 4 Evaluation results of six second-level indicators of the 
distribution network in nine cities 
由图4 可知，贵阳市配电网在各二级指标下得
分均较为优秀，因此在综合评价中排名首位，凯里
市配电网与都匀市配电网在供电可靠性方面表现也
较为突出，但在经济效益方面还有待提高，而毕节
配电网则明显在供电可靠性方面得分较为一般，应
在这方面加大投资。 
7) 与传统评价方法对比分析 
本文方法与传统方法所求权重对比如图5 所
示。由图5 可知，利用本文方法所求得的权重在整
体趋势上与利用传统方法所求得的权重相近，具有
一定的可信度，但是经济效益等指标的权重却高于
由传统方法所求得的权重，符合新时代配电网对经
济效益的较高要求，此外，网络结构水平下相关三
级指标的权重也高于由传统方法所求得的权重，符
合现代配电网的发展方向。因此本文所提的赋权方
法较传统赋权方法更加合理、准确。 
 
图5 本文方法与传统方法所求权重对比 
Fig. 5 Comparison between the weights of the method in this 
paper and the traditional method 
由表8 可知，由两种方法得到的评价结果整体
接近，同时也存在差异。其中：传统方法下毕节市
配电网的等级分类为1 级，等级变量特征值的计算
结果为2.29，而安顺市配电网等级变量特征值低于
毕节市配电网，但其等级分类却为2 级，可见由于
传统方法最高等级右侧与最低等级左侧信息丢失，
导致传统方法等级分类与等级变量特征值不相符的
结果；而采用改进后的可拓评估模型进行计算，毕
节市配电网的等级变量特征值低于安顺市，符合等
级评价结果，从而解决了传统方法等级分类与等级
变量特征值不相符的问题。六盘水市与凯里市排名
发生调换，从原始数据分析，六盘水市配电网除了
在负荷供应能力下相关指标略低于凯里市配电网
外，在其余指标方面表现优异，尤其是在占有较大
权重的供电可靠性下的相关指标方面显著高于凯里
市配电网的对应指标，故而本文的评价结果更加符
合实际情况。由此可知，本文所提出的方法较传统
方法更加具有可信度与合理性。 
5   结论 
本文提出了一种改进的基于最小二乘的AHP- 
CRITIC 组合赋权方法，由理论分析与实例计算可
得以下结论： 
1) 利用改进后的最小二乘赋权方法所得到的
结果更加准确、合理； 
2) 引入三角模糊数所确定的各指标在各等级
下的经典域区间更为合理，从而解决了传统方法在
这一问题上的主观随意性； 
3) 计及经典域区间长度变化对关联度的影响，
使得关联度计算结果更加准确； 
4) 避免最低与最高等级两侧关联度信息丢失
的等级扩展法，使得等级变量特征值计算结果更加
准确。 
综上所述，本文方法能够对配电网进行科学、
系统、合理的分类与排序，进而对配电网做出准确、
符合实际情况的评价。 
参考文献 
[1]  刘秋华, 董丹丹, 韩韬. 基于层次分析法的配电网风
险评估指标体系研究[J]. 电气技术, 2016(9): 39-42. 
LIU Qiuhua, DONG Dandan, HAN Tao. Research on risk 
assessment index system for distribution network based 
on analytic hierarchy process[J]. Electrical Engineering, 
2016(9): 39-42. 
[2]  何艺, 秦丽娟. 基于改进AHP 和熵权法的计量自动化
终端质量综合评价研究[J]. 电测与仪表, 2015, 52(23): 
58-62.



<!-- page 10/11 -->

罗 宁，等   基于改进的AHP-CRITIC 组合赋权与可拓评估模型的配电网综合评价方法            - 95 - 
 
HE Yi, QIN Lijuan. Research on comprehensive 
assessment of metering automation terminal quality based 
on the improved AHP and entropy method[J]. Electrical 
Measurement & Instrumentation, 2015, 52(23): 58-62. 
[3]  葛婷, 陈艳波, 汪颖翔. 基于三角模糊多属性决策的
配电网投资效益评价[J]. 电网与清洁能源, 2018, 
34(10): 12-20. 
GE Ting, CHEN Yanbo, WANG Yingxiang. Investment 
benefit evaluation of the distribution network based on 
triangular fuzzy multiple attribute decision making[J]. 
Power System and Clean Energy, 2018, 34(10): 12-20.  
[4]  邢晓敏, 何铁新, 吴卓, 等. 配电网运行状态评估递阶
模型构建及评价方法研究[J]. 智慧电力, 2019, 47(4): 
81-86. 
XING Xiaomin, HE Tiexin, WU Zhuo, et al. Construction 
of hierarchical model and evaluation method for 
distribution network operation status evaluation[J]. Smart 
Power, 2019, 47(4): 81-86. 
[5]  谢晓帆, 刘秋林, 李斌, 等. 基于主成分分析法与对应
分析法的县域配电网状况评估[J]. 智慧电力, 2018, 
46(6): 68-73. 
XIE Xiaofan, LIU Qiulin, LI Bin, et al. Evaluation of 
country distribution network status based on principal 
component analysis and correspondence analysis[J]. 
Smart Power, 2018, 46(6): 68-73. 
[6]  管新建, 刘文康, 胡栋. 基于CRITIC 权的污染指数法
在清潩河水质评价中的应用[J]. 水电能源科学, 2017, 
35(8): 49-52. 
GUAN Xinjian, LIU Wenkang, HU Dong. Application of 
pollution index method in water quality evaluation of 
Qingyihe river based on CRITIC weight[J]. Water 
Resources and Power, 2017, 35(8): 49-52. 
[7]  王瑛, 蒋晓东, 张璐. 基于改进的CRITIC 法和云模型
的科技奖励评价研究[J]. 湖南大学学报: 自然科学版, 
2014, 41(4): 118-124. 
WANG Ying, JIANG Xiaodong, ZHANG Lu. Research 
on the evaluation of science and technological awards 
based on improved CRITIC method and cloud model[J]. 
Journal of Hunan University: Natural Science, 2014, 
41(4): 118-124. 
[8]  张婕, 黄舒舒. 基于模糊优选和CRITIC 法的电力碳排
放权区域初始分配—以华东电网区域为例[J]. 环境保
护科学, 2015, 41(3): 62-66. 
ZHANG Jie, HUANG Shushu. Regional Initial allocation 
of carbon emission in the power industry based on fuzzy 
optimization and CRITIC methods—taking the region of 
East China Grid as an example[J]. Environmental 
Protection Science, 2015, 41(3): 62-66. 
[9]  汪顺生, 黄天元, 陈豪, 等. 基于CRITIC 赋权的模糊
综合评判模型在水质评价中的应用[J]. 水电能源科学, 
2018, 36(6): 48-51. 
WANG Shunsheng, HUANG Tianyuan, CHEN Hao, et al. 
Application of fuzzy comprehensive evaluation model 
based CRITIC weighting in water quality evaluation[J]. 
Water Resources and Power, 2018, 36(6): 48-51. 
[10] 南钰, 宋瑞卿, 陈鹏, 等. 基于改进熵权-灰色关联法
的配电网可靠性影响因素分析[J]. 电力系统保护与控
制, 2019, 47(24): 101-107. 
NAN Yu, SONG Ruiqing, CHEN Peng, et al. Study on 
the factors influencing the reliability analysis in 
distribution network based on improved entropy weight 
gray correlation analysis algorithm[J]. Power System 
Protection and Control, 2019, 47(24): 101-107. 
[11] 宗祥瑞, 昌冲. 基于熵权法的电网运行状态特征分析
与评价[J]. 电力系统及其自动化学报, 2016, 28(增刊1): 
1-5. 
ZONG Xiangrui, CHANG Chong. Analysis and evaluation 
of operation state characteristics of power grid based on 
entropy weight method[J]. Proceedings of the CSU-EPSA, 
2016, 28(S1): 1-5. 
[12] 李明亮, 李克钢, 秦庆词, 等. 基于改进组合赋权- 
TOPSIS 法的岩爆倾向性评判模型[J]. 中国安全生产
科学技术, 2020, 16(3): 74-80. 
LI Mingliang, LI Kegang, QIN Qingci, et al. Judgment 
model of rock burst tendency based on improved 
combination weighting-TOPSIS method[J]. Journal of 
Safety Science and Technology, 2020, 16(3): 74-80. 
[13] 李晓星, 杜军凯, 傅尧. 基于变异系数和熵权组合赋
权的正态云水质综合评价模型[J]. 水电能源科学, 
2017, 35(10): 55-58. 
LI Xiaoxing, DU Junkai, FU Yao. Water quality 
evaluation model of normal cloud based on coefficient 
variation and entropy weight[J]. Water Resources and 
Power, 2017, 35(10): 55-58. 
[14] 赵书强, 汤善发. 基于改进层次分析法、CRITIC 法与
逼近理想解排序法的输电网规划方案综合评价[J]. 电
力自动化设备, 2019, 39(3): 143-148, 162. 
ZHAO Shuqiang, TANG Shanfa. Comprehensive evaluation 
of transmission network planning scheme based on 
improved analytic hierarchy process, CRITIC method 
and TOPSIS[J]. Electric Power Automation Equipment, 
2019, 39(3): 143-148, 162. 
[15] 邓红雷, 戴栋, 李述文. 基于层次分析-熵权组合法的
架空输电线路综合运行风险评估[J]. 电力系统保护与
控制, 2017, 45(1): 28-34. 
DENG Honglei, DAI Dong, LI Shuwen. Comprehensive



<!-- page 11/11 -->

罗 宁，等   基于改进的AHP-CRITIC 组合赋权与可拓评估模型的配电网综合评价方法            - 96 - 
 
operation risk evaluation of overhead transmission line 
based on hierarchical analysis-entropy weight method[J]. 
Power System Protection and Control, 2017, 45(1): 
28-34. 
[16] LI Gengyin, LI Guodong, ZHOU Ming. Comprehensive 
evaluation model of wind power accommodation ability 
based on macroscopic and microscopic indicators[J]. 
Protection and Control of Modern Power Systems, 2019, 
4(3): 215-226. DOI: 10.1186/s41601-019-0132-6.  
[17] 赵金先, 张英, 武丹丹, 等. 基于WSR-组合赋权的地
铁钻爆法施工安全灰色聚类评价[J]. 工程管理学报, 
2018, 32(6): 109-114. 
ZHAO Jinxian, ZHANG Ying, WU Dandan, et al. Safety 
grey clustering evaluation of subway drilling and blasting 
method-a study based on WSR-combination weighting 
method[J]. Journal of Engineering Management, 2018, 
32(6): 109-114. 
[18] 徐斌, 马骏, 陈青, 等. 基于改进AHP-TOPSIS 法的经
济开发区配电网综合评价指标体系和投资策略研究[J]. 
电力系统保护与控制, 2019, 47(22): 35-44.  
XU Bin, MA Jun, CHEN Qing, et al. Research on 
comprehensive evaluation index system and investment 
strategy of economic development zone distribution network 
based on improved AHP-TOPSIS method[J]. Power System 
Protection and Control, 2019, 47(22): 35-44. 
[19] 胡元潮, 阮江军, 杜志叶, 等. 基于TOPSIS 法的变电
站一次设备智能化评估[J]. 电力自动化设备, 2012, 
32(12): 22-27. 
HU Yuanchao, RUAN Jiangjun, DU Zhiye, et al. Evaluation 
of substation primary equipment intellectualization based 
on TOPSIS[J]. Electric Power Automation Equipment, 
2012, 32(12): 22-27. 
[20] 姚历毅, 罗萍萍, 项胤兴, 等. 具有抗逆序及权重自适
应的黑启动方案评估方法[J]. 中国电力, 2019, 52(3): 
87-94. 
YAO Liyi, LUO Pingping, XIANG Yinxing, et al. 
Evaluation 
method 
of 
black 
start 
scheme 
with 
anti-reverse order and weight adaptive[J]. Electric Power, 
2019, 52(3): 87-94. 
[21] 刘文霞, 李鹤, 赵天阳, 等. 风电多点并网的网源协调
输电网扩展规划[J]. 现代电力, 2015, 32(1): 38-45. 
LIU Wenxia, LI He, ZHAO Tianyang, et al. Coordination 
of generation and transmission expansion planning for 
wind power integration at multi-points[J]. Modern Electric 
Power, 2015, 32(1): 38-45. 
[22] 李慧玲, 芦新波, 刘大川, 等. 基于AHP-TOPSIS 的电
力能效项目综合评价[J]. 现代电力, 2014, 31(4): 88-94. 
LI Huiling, LU Xinbo, LIU Dachuan, et al. A 
comprehensive evaluation method for power energy 
efficiency project based on AHP-TOPSIS[J]. Modern 
Electric Power, 2014, 31(4): 88-94. 
[23] 莫一夫, 张勇军. 基于变权灰关联的智能配电网用电
可靠性提升对象优选[J]. 电力系统保护与控制, 2019, 
47(5): 26-34. 
MO Yifu, ZHANG Yongjun. Optimal object selection of 
power utilization reliability promotion for smart 
distribution grid based on weighted grey correlation[J]. 
Power System Protection and Control, 2019, 47(5): 
26-34. 
[24] 陈源, 王璐, 黄友珍, 等. 基于多级可拓评价法的配电
网规划经济效益评估模型[J]. 中国电力, 2016, 49(10): 
159-164. 
CHEN Yuan, WANG Lu, HUANG Youzhen, et al. 
Economic benefit evaluation model of distribution network 
planning based on multi-level extension evaluation 
method[J]. Electric Power, 2016, 49(10): 159-164. 
  
收稿日期：2020-10-14；    修回日期：2020-10-29  
作者简介： 
罗  宁(1986—)，女，硕士，工程师，研究方向为电网
规划等；E-mail: 547091372@qq.com 
贺墨琳(1989—)，女，硕士，工程师，研究方向为电网
规划等；E-mail: morning8998@163.com 
高  华(1978—)，男，硕士，高级工程师，研究方向为
电网规划等。E-mail: 13885093161@139.com 
(编辑 魏小丽)
