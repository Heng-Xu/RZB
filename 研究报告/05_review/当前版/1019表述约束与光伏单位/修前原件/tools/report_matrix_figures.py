"""重绘五参数矩阵端点及两组有响应的完整设备序列。"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT/'研究报告/05_review/当前版/1016矩阵分区与文献补充'
SOURCE = ROOT/'研究报告/数据来源/当前版/矩阵分区_20261016'


def parameter_devices(save):
    from sync_current_report_results import PUBLIC, controlled_sequences
    path = PUBLIC/'统一有效样本.csv'
    sequences = controlled_sequences(pd.read_csv(path))
    for name, field, key, title in [
        ('cable', '电缆长度占比', 'cable_device_response', '电缆造价条件与设备替代'),
        ('diversity', '负荷分散系数', 'diversity_device_response', '局部高峰条件与设备配置')]:
        data = sequences[name]; values = data[field].to_numpy(); x = np.arange(len(data))
        labels = [f'{v*100:.0f}%' if name == 'cable' else f'{v:.2f}' for v in values]
        fig, axes = plt.subplots(3, 1, figsize=(6.8, 7.1), sharex=True)
        axes[0].plot(x, data['容载比'], 'o-', color='#32698c')
        axes[0].set_ylabel('容载比'); axes[0].set_title(title, fontsize=14)
        axes[0].set_ylim(data['容载比'].min()-.12, data['容载比'].max()+.17)
        for i, v in enumerate(data['容载比']): axes[0].text(i, v+.035, f'{v:.2f}', ha='center', fontsize=11)
        axes[1].bar(x-.18, data['主变容量_MVA'], .34, color='#32698c', label='主变容量/MVA')
        axes[1].set_ylabel('主变容量/MVA'); axes[1].set_ylim(0, 950)
        axes[2].bar(x-.18, data['储能额定功率_MW'], .34, color='#b18a3c', label='储能额定功率/MW')
        axes[2].set_ylabel('储能额定功率/MW')
        other = axes[2].twinx(); other.plot(x+.18, data['新增联络合计_条'], 's--', color='#333333', label='新增联络/条')
        other.set_ylabel('新增联络/条'); other.set_ylim(0, 14); other.set_yticks([0, 3, 6, 9, 12])
        axes[2].legend(loc='upper left', fontsize=9); other.legend(loc='upper right', fontsize=9)
        for ax in axes: ax.grid(axis='y', alpha=.16)
        axes[2].set_xticks(x, labels); axes[2].set_xlabel(field)
        save(fig, key, data, [path], '参数改变时哪些设备替代、容载比何处切换',
             '完整节点的比值曲线及设备分面图', '全部容载比大于2，完整保留响应及真实平台')


def lookup_bounds(save):
    asset = ROOT/'研究报告/02图表/当前版'
    table = json.loads((asset/'计算表.json').read_text())['lookup_matrix_2_1.10']
    rows = [[c.strip() for c in line.strip('|').split('|')] for line in table.splitlines() if line.startswith('|')]
    data = pd.DataFrame(rows[2:], columns=rows[0])
    low = data.iloc[:,2:].map(lambda x: float(x.split('～')[0])).to_numpy()
    high = data.iloc[:,2:].map(lambda x: float(x.split('～')[1])).to_numpy()
    labels = [g+' / '+e for g,e in data.iloc[:,:2].to_numpy()]
    fig, axes = plt.subplots(1,2,figsize=(6.8,7.0),sharey=True)
    vmin, vmax = low.min(), high.max()
    for ax, values, title in zip(axes,[low,high],['推荐带下界','推荐带上界']):
        ax.imshow(values,aspect='auto',cmap=LinearSegmentedColormap.from_list('bounds',['#ffffff','#32698c']),vmin=vmin,vmax=vmax)
        ax.set_xticks(range(4),list(data.columns[2:]),rotation=35,ha='right')
        ax.set_yticks(range(12),labels,fontsize=10);ax.set_title(title,fontsize=13);ax.set_xlabel('初始转供率')
        for i in range(12):
            for j in range(4):ax.text(j,i,f'{values[i,j]:.2f}',ha='center',va='center',fontsize=9,
                                    color='white' if values[i,j]>(vmin+vmax)/2 else '#333333')
    axes[0].set_ylabel('年最大净负荷平均增长率 / 装机渗透率')
    fig.suptitle('电缆长度占比>30%、负荷分散系数1.10',fontsize=13)
    save(fig,'lookup_matrix_bounds',data,[asset/'计算表.json',ROOT/'研究报告/01研究推荐/当前版/参数联合情景_20261012/统一有效样本.csv'],
         '电缆分区内推荐带端点怎样分布','同色阶端点热图','同一行按转供档容量下界设置相邻档共用界值')


def main():
    import expand_report_figures as figures
    SOURCE.mkdir(parents=True, exist_ok=True)
    figures.SOURCE = SOURCE
    parameter_devices(figures.save); lookup_bounds(figures.save)
    old = ROOT/'研究报告/05_review/当前版/1016图文扩充与术语复核/新增图件来源与图形选择.json'
    inherited = json.loads(old.read_text())
    for row in inherited:
        for path, digest in list(row['原始依据'].items()):
            if figures.sha(ROOT/path) != digest:
                snapshot = AUDIT/'修前快照'/path
                assert figures.sha(snapshot) == digest, '继承图件来源未保留：'+path
                del row['原始依据'][path]
                row['原始依据'][str(snapshot.relative_to(ROOT))] = digest
    inherited = [row for row in inherited if row['图键'] not in ['lookup_matrix_bounds','energy_capacity_storage']]
    (AUDIT/'新增图件来源与图形选择.json').write_text(json.dumps(inherited+figures.MAP,ensure_ascii=False,indent=2)+'\n')
    print('重绘3图，继承24图来源及不可变原件')


if __name__ == '__main__': main()
