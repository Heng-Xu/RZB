"""只重绘扩展矩阵端点和11点分散系数敏感性图，保留其他38幅图。"""
from pathlib import Path
import hashlib
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.font_manager import fontManager,FontProperties
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from extend_matrix_scenarios import PUBLIC,SOURCE,REVIEW,write


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    proof=json.loads((REVIEW/'扩展数据独立核验.json').read_text())
    assert proof['状态']=='通过'
    assets=ROOT/'研究报告/02图表/当前版'
    fontManager.addfont('/usr/share/fonts/wps-office/FZFSK.TTF')
    settings={'font.family':['Times New Roman',FontProperties(fname='/usr/share/fonts/wps-office/FZFSK.TTF').get_name()],
              'font.size':11,'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False,
              'pdf.fonttype':42,'svg.fonttype':'path'}
    provenance=[]
    def save(fig,key,data,inputs,method):
        fig.tight_layout(pad=1.1)
        png=assets/(key+'.png')
        fig.savefig(png,dpi=360,facecolor='white')
        for suffix in ['pdf','svg']:fig.savefig(SOURCE/(key+'.'+suffix),facecolor='white')
        data.to_csv(SOURCE/(key+'.csv'),index=False)
        provenance.append(dict(图键=key,图件SHA256=sha(png),数据=str((SOURCE/(key+'.csv')).relative_to(ROOT)),
            数据SHA256=sha(SOURCE/(key+'.csv')),依据={str(p.relative_to(ROOT)):sha(p) for p in inputs},
            方法=method,检查='全部节点保留，坐标注明单位；未平滑或按预期趋势移动数据；柱形坐标从0起。'))
        plt.close(fig)
    with plt.rc_context(settings):
        source=PUBLIC/'负荷分散系数11点完整序列.csv';data=pd.read_csv(source)
        assert len(data)==11
        x=data['负荷分散系数'].to_numpy()
        fig,axes=plt.subplots(4,1,figsize=(6.8,7.4),sharex=True)
        axes[0].plot(x,data['容载比'],'o-',color='#32698c',markersize=4)
        axes[0].set_ylabel('容载比')
        axes[0].set_ylim(data['容载比'].min()-.10,data['容载比'].max()+.14)
        for i,(v,ratio) in enumerate(zip(x,data['容载比'])):
            if i==0 or abs(data['容载比'].iloc[i-1]-ratio)>.001:
                axes[0].annotate(f'{ratio:.2f}',(v,ratio),xytext=(0,6),textcoords='offset points',ha='center',fontsize=9)
        axes[1].bar(x,data['主变容量_MVA'],width=.012,color='#32698c');axes[1].set_ylabel('主变容量/MVA')
        axes[2].bar(x,data['储能额定功率_MW'],width=.012,color='#b18a3c');axes[2].set_ylabel('储能额定功率/MW')
        axes[3].step(x,data['新增联络合计_条'],where='mid',color='#333333')
        axes[3].plot(x,data['新增联络合计_条'],'s',color='#333333',markersize=4)
        axes[3].set_ylabel('新增联络/条');axes[3].set_ylim(0,max(data['新增联络合计_条'])+2)
        axes[3].yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        for ax in axes:
            ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
            ax.axvline(1.15,color='#777777',ls=':',lw=.8)
        axes[3].set_xticks(x,[f'{v:.2f}' for v in x],rotation=35)
        axes[3].set_xlabel('负荷分散系数')
        save(fig,'diversity_device_response',data,[source],
             '固定装机渗透率2.00、增长4%、电缆10%、转供40%、时长4h的11点完整序列；四面板共用分散系数横轴，1.15标出分档界。')
        table_path=assets/'计算表.json';table=json.loads(table_path.read_text())['lookup_matrix_2_high']
        rows=[[c.strip() for c in line.strip('|').split('|')] for line in table.splitlines() if line.startswith('|')]
        d=pd.DataFrame(rows[2:],columns=rows[0])
        low=d.iloc[:,2:].map(lambda v:float(v.split('～')[0])).to_numpy()
        high=d.iloc[:,2:].map(lambda v:float(v.split('～')[1])).to_numpy()
        labels=[g+' / '+e for g,e in d.iloc[:,:2].to_numpy()]
        cmap=LinearSegmentedColormap.from_list('matrix_window',['#ffffff','#32698c'])
        norm=Normalize(vmin=low.min(),vmax=high.max())
        fig,axes=plt.subplots(1,2,figsize=(6.8,7.0),sharey=True)
        for ax,values,title in zip(axes,[low,high],['推荐窗口下界','推荐窗口上界']):
            ax.imshow(values,aspect='auto',cmap=cmap,norm=norm,interpolation='nearest')
            ax.set_xticks(range(4),list(d.columns[2:]),rotation=35,ha='right')
            ax.set_yticks(range(12),labels,fontsize=9);ax.set_title(title,fontsize=12);ax.set_xlabel('初始转供率')
            for i in range(12):
                for j in range(4):
                    ax.text(j,i,f'{values[i,j]:.2f}',ha='center',va='center',fontsize=9,
                            color='white' if norm(values[i,j])>.58 else '#333333')
        axes[0].set_ylabel('年最大净负荷平均增长率 / 装机渗透率')
        fig.suptitle('电缆长度占比>30%、负荷分散系数>1.15',fontsize=12)
        save(fig,'lookup_matrix_bounds',d,[table_path,PUBLIC/'窗口与原始节点依据.json'],
             '同一数据分档和共同色阶；端点逐格对应六表中电缆高档、分散高档，基准宽度0.10，同一行按相邻代表水平中点局部缩窄。')
    write(REVIEW/'更新图件来源.json',dict(状态='待实际图件及PDF目视核验',图件=provenance,
        使用技能='scientific-visualization：核对原始数据保留、诚实编码及输出元数据；未采用期刊投稿规格。'))
    print('仅重绘2图，保留绘图CSV、PDF及SVG。')


if __name__=='__main__':main()
