from pathlib import Path
import json
HERE=Path(__file__).parent;R=HERE.parents[1];A=R/'02图表/当前版'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
font_manager.fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF')
font_manager.fontManager.addfont('/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf')
fz=font_manager.FontProperties(fname='/usr/share/fonts/wps-office/FZFSK.TTF').get_name()
plt.rcParams.update({'font.family':['Times New Roman',fz],'font.size':11,'axes.unicode_minus':False})
fig,ax=plt.subplots(figsize=(6.7,5.4));ax.set_xlim(0,10);ax.set_ylim(0,9);ax.axis('off')
boxes=[(1,7.7,8,0.8,'分析源荷特征、供电区域类别与负荷分散系数'),(1,6.15,8,.95,'结合净负荷峰值、95%峰值持续时间\n年最大净负荷平均增长率及工程投资开展分析'),(.4,4.4,2.9,1.05,'主变增容与扩建\n额定容量、建设条件'),(3.55,4.4,2.9,1.05,'储能配置\n额定功率、额定能量'),(6.7,4.4,2.9,1.05,'10 kV联络\n线路类型、转供能力'),(1,2.7,8,1.05,'同一起点开展四年建设措施与费用比较\n校核正反向净负荷、主变N-1及站间负荷转接'),(1,.7,8,1.2,'归纳25200组技术经济情景的容量配置结果\n形成432组分类容载比推荐区间及研究结论')]
for x,y,w,h,t in boxes:
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.07',facecolor='#eef2f5',edgecolor='#29465b',linewidth=1));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=11)
for a,b in [((5,7.68),(5,7.18)),((5,6.10),(1.85,5.56)),((5,6.10),(5,5.56)),((5,6.10),(8.15,5.56)),((1.85,4.32),(3.3,3.85)),((5,4.32),(5,3.85)),((8.15,4.32),(6.7,3.85)),((5,2.60),(5,2.02))]:ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'#29465b','lw':1})
fig.savefig(A/'technical_route.png',dpi=300,bbox_inches='tight');plt.close(fig)
(HERE/'图件字体说明.json').write_text(json.dumps({'中文字体':'方正仿宋_GBK','字体文件':'/usr/share/fonts/wps-office/FZFSK.TTF','西文字体':'Times New Roman','图内标题':'仅轴标签、图例与流程节点；图名在正文图下注明'},ensure_ascii=False,indent=2))
print('技术路线图更新完成')
