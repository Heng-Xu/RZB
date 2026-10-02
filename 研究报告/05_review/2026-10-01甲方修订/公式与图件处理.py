from pathlib import Path
import re,json
HERE=Path(__file__).parent;R=HERE.parents[1];TEXT=R/'03_MD/2026-10-01甲方修订';A=R/'02图表/2026-10-01甲方修订'
for p in sorted(TEXT.glob('0[1-6] *.md')):
 s=p.read_text()
 def display(m):
  tex=m[1]
  if '\\begin{aligned}' in tex:return m[0]
  # 将多个独立关系分行，保留同一式号。
  tag=re.search(r'\\tag\{[^}]+\}',tex)
  number=tag[0] if tag else ''
  bare=tex.replace(number,'').strip()
  parts=re.split(r',\s*\\qquad\s*|,\s*\\quad\s*(?=(?:[A-Za-z]|\\sum))',bare)
  if len(parts)>1 and len(bare)>85:
   bare='\\begin{aligned}\n'+'\\\\\n'.join(t.strip().replace('=','&=',1) if '=' in t and '\\leq' not in t and '\\geq' not in t else '&'+t.strip() for t in parts)+'\n\\end{aligned}'
  return '$$'+bare+number+'$$'
 s=re.sub(r'\$\$([\s\S]*?)\$\$',display,s)
 # 仅替换正文中已明确指向数学参数的字符。
 s=s.replace('对月份m，','对月份$m$，').replace('式中，a为','式中，$a$为').replace('单柜c_B','单柜$c_B$')
 p.write_text(s)
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
boxes=[(1,7.7,8,0.8,'核定指标与现状：容量、负荷、光伏、站级时序'),(1,6.15,8,.95,'形成输入：双向峰值、持续时间、增长率、工程费用'),(.4,4.4,2.9,1.05,'主变增容\n离散规格、第三台'),(3.55,4.4,2.9,1.05,'储能配置\n整数柜、持续支撑'),(6.7,4.4,2.9,1.05,'10 kV联络\n既有能力、新建项目'),(1,2.7,8,1.05,'统一容载比2.0起点后的四年寻优\n正常容量、单台退出、转供能力、负荷守恒'),(1,.7,8,1.2,'复算案例结果并进行7000组通用参数外推\n形成规划容载比区间及应用建议')]
for x,y,w,h,t in boxes:
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.07',facecolor='#eef2f5',edgecolor='#29465b',linewidth=1));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=11)
for a,b in [((5,7.68),(5,7.18)),((5,6.10),(1.85,5.56)),((5,6.10),(5,5.56)),((5,6.10),(8.15,5.56)),((1.85,4.32),(3.3,3.85)),((5,4.32),(5,3.85)),((8.15,4.32),(6.7,3.85)),((5,2.60),(5,2.02))]:ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'#29465b','lw':1})
fig.savefig(A/'technical_route.png',dpi=300,bbox_inches='tight');plt.close(fig)
(HERE/'图件字体说明.json').write_text(json.dumps({'中文字体':'方正仿宋_GBK','字体文件':'/usr/share/fonts/wps-office/FZFSK.TTF','西文字体':'Times New Roman','图内标题':'仅轴标签、图例与流程节点；图名在正文图下注明'},ensure_ascii=False,indent=2))
print('独立公式分行、行内参数与技术路线图已处理')
