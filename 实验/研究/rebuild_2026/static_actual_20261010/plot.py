"""导出静态试算的容载比与费用图。"""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/xuzhou-pilot-mpl')
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .run import OUT


def run():
    d=json.loads((OUT/'结果汇总.json').read_text())
    plt.rcParams.update({'font.family':'FZFangSong-Z02','axes.unicode_minus':False,'font.size':12})
    fig,axes=plt.subplots(1,3,figsize=(15,4.5),layout='constrained')
    for ax,name in zip(axes[:2],('市区','邳州')):
        for label,color in [('刚性·允许储能','#75889b'),('弹性·允许储能','#126f75')]:
            rr=[r for r in d['annual'] if r['地区']==name and r['方案']==label]
            ax.plot([r['年份'] for r in rr],[r['方案容载比'] for r in rr],marker='o',label=label.split('·')[0],color=color,linewidth=2)
        ax.axhline(2,color='#aaa',linestyle='--',linewidth=1)
        ax.set_xticks([2022,2023,2024,2025]);ax.set_ylabel('容载比');ax.set_title(name)
        ax.grid(axis='y',alpha=.2);ax.legend(frameon=False)
    ax=axes[2]
    for j,r in enumerate(d['comparison']):
        for dx,key,label,color in [(-.18,'刚性费用现值_万元','刚性','#75889b'),(.18,'弹性费用现值_万元','弹性','#126f75')]:
            value=r[key]/10000
            ax.bar(j+dx,value,width=.32,color=color,label=label if j==0 else None)
            ax.text(j+dx,value+.08,f'{value:.2f}',ha='center',fontsize=11)
    ax.set_xticks([0,1],['市区','邳州']);ax.set_ylabel('评价期新增措施费用现值 / 亿元')
    ax.set_ylim(0,10);ax.legend(frameon=False);ax.grid(axis='y',alpha=.2)
    for ax in axes:
        ax.spines[['top','right']].set_visible(False)
    fig.savefig(OUT/'两地容载比及费用.png',dpi=180)
    fig.savefig(OUT/'两地容载比及费用.pdf')
    plt.close(fig)


if __name__=='__main__':run()
