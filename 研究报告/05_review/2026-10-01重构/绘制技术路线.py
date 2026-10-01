from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from 整理数据与图表 import plt,save,COLORS
from matplotlib.patches import FancyBboxPatch
fig,ax=plt.subplots(figsize=(7.2,5.3));ax.set_xlim(0,10);ax.set_ylim(0,8.1);ax.axis('off')
def box(x,y,w,h,title,detail,color):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.08,rounding_size=0.08',facecolor='white',edgecolor=color,linewidth=1.1))
 ax.text(x+w/2,y+h*.69,title,ha='center',va='center',fontsize=11,color=color,fontweight='bold')
 ax.text(x+w/2,y+h*.28,detail,ha='center',va='center',fontsize=9.2,color='#262626',linespacing=1.4)
def arrow(a,b):ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color=COLORS[0],lw=1.0))
box(.1,6.75,9.8,1.0,'统计范围与共同起点核定','区县110 kV负荷代理、站级设备与类别；原表换算光伏及前两年回推',COLORS[0])
box(.1,4.95,4.5,1.1,'运行任务','正反向独立峰、绝对峰与95%峰段\n四年加权增长及源荷、电量背景',COLORS[0])
box(5.4,4.95,4.5,1.1,'工程费用','新购整台、第三台、整数储能与联络\n初始投资、运维、更新及现值',COLORS[1])
arrow((2.35,6.75),(2.35,6.05));arrow((7.65,6.75),(7.65,6.05))
box(.1,2.95,9.8,1.15,'2022—2025年四路径联合寻优','年度资产非减、双向容量与静态退出服务量、正常转接守恒\n最低费用 → 同费用容量偏好 → 固定布局减少转接',COLORS[0])
arrow((2.35,4.95),(2.35,4.1));arrow((7.65,4.95),(7.65,4.1))
box(.1,1.2,4.5,1.1,'条件矩阵','12个价格条件＋6个技术情景\n逐年推荐指标及对应措施',COLORS[0])
box(5.4,1.2,4.5,1.1,'结果核对','逐站余量、资产状态、转接总量\n投运现金流与经济排序',COLORS[1])
arrow((2.35,2.95),(2.35,2.3));arrow((7.65,2.95),(7.65,2.3))
ax.text(5,.45,'原始收资定位及处理记录由独立数据来源说明保存',ha='center',fontsize=9.5,color='#555555')
save('technical_route')
