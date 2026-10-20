"""Recompute research figure data; export standalone plots and SVG mark fragments.

No slide files are written. All inference uses the full CSV data. The native
slide polylines use geometric simplification below 0.45 canvas pixels, solely
to keep the editable DrawingML path size manageable.
"""
from pathlib import Path
import csv, json, statistics, math
from collections import defaultdict
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
for font in Path('/usr/share/fonts/truetype/msttcorefonts').glob('Arial*.ttf'):
    font_manager.fontManager.addfont(str(font))

P=Path(__file__).resolve().parent
R=P/'sources/historical_model/results'
F=P/'figures'; F.mkdir(exist_ok=True)
rows=list(csv.DictReader((R/'ea_converge.csv').open()))
groups=defaultdict(list)
for r in rows:
    if int(r['K'])==40: groups[r['algo'],int(r['gen'])].append(float(r['hv']))
reference=statistics.mean(groups['classic',800])
stats={a:[] for a in ['classic','nsga3','fg','repair_only','warmstart_only']}
for a in stats:
    for g in sorted(k[1] for k in groups if k[0]==a):
        v=[x/reference for x in groups[a,g]]
        stats[a].append({'gen':g,'mean':statistics.mean(v),'sd':statistics.stdev(v),'runs':v})
stations=list(csv.DictReader((R/'ea_county_strategy_over2.csv').open()))
stations.sort(key=lambda r:float(r['slr']))
colors={'classic':'#102B46','nsga3':'#426D9B','fg':'#087E83','repair_only':'#B87232','warmstart_only':'#7C8791'}
names={'classic':'NSGA-II','nsga3':'NSGA-III','fg':'EPG-NSGA-II','repair_only':'Repair-only','warmstart_only':'Seeding-only'}

mpl.rcParams.update({'font.family':'Arial','font.size':11,'axes.labelsize':11,
 'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.8,
 'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'})

def export(fig,name):
    for ext in ['svg','pdf','png']:
        dest=F/(name+'.'+ext)
        fig.savefig(dest,dpi=450)
        if ext=='svg':
            dest.write_text('\n'.join(line.rstrip() for line in dest.read_text().splitlines())+'\n')
    plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,3.8),layout='constrained')
for a,ls in [('classic','-'),('nsga3','--'),('fg','-')]:
    s=stats[a]; x=np.array([v['gen'] for v in s]); y=np.array([v['mean'] for v in s]); sd=np.array([v['sd'] for v in s])
    ax.fill_between(x,y-sd,y+sd,color=colors[a],alpha=.1,lw=0)
    ax.plot(x,y,color=colors[a],ls=ls,lw=2.1 if a=='fg' else 1.5,label=names[a])
ax.axhline(1,color='#7C8791',ls=':',lw=1)
ax.set(xlim=(0,800),ylim=(0,1.1),xlabel='Generation',ylabel='Normalized hypervolume')
ax.legend(frameon=False,loc='lower right',fontsize=10)
ax.grid(axis='y',color='#E6EDF0',lw=.6)
export(fig,'convergence_K40')

fig,ax=plt.subplots(figsize=(4.6,3.7),layout='constrained')
ax.axhline(2,color='#B87232',lw=1,ls='--')
ax.scatter([float(v['slr']) for v in stations],[float(v['R_star']) for v in stations],s=48,facecolor='#087E83',edgecolor='white',lw=.7,zorder=3)
ax.set(xlim=(1.7,3.6),ylim=(1.2,3),xlabel='Source-load ratio',ylabel='Selected CLR')
ax.grid(axis='y',color='#E6EDF0',lw=.6)
export(fig,'station_heterogeneity_K20')

order=['classic','nsga3','warmstart_only','repair_only','fg']
fig,ax=plt.subplots(figsize=(4.7,3.4),layout='constrained')
ax.axvline(1,color='#A3ADB5',lw=.8,ls=':')
for i,a in enumerate(order):
    v=stats[a][-1]
    ax.scatter(v['runs'],np.array([i,i,i])+np.array([-.08,0,.08]),s=28,facecolor='white',edgecolor=colors[a],lw=1.2,zorder=3)
    ax.plot([v['mean']],[i],marker='|',ms=16,mew=2.4,color=colors[a],ls='none')
ax.set(yticks=range(5),yticklabels=[names[a] for a in order],xlim=(.96,1.07),xlabel='Final normalized hypervolume')
ax.invert_yaxis();ax.grid(axis='x',color='#E6EDF0',lw=.6)
export(fig,'ablation_K40')

def simplify(points,tol=.45):
    if len(points)<3:return points
    first=np.asarray(points[0]);last=np.asarray(points[-1]);vec=last-first
    arr=np.asarray(points);length=np.linalg.norm(vec)
    delta=arr-first
    dist=np.linalg.norm(delta,axis=1) if length==0 else np.abs(vec[0]*delta[:,1]-vec[1]*delta[:,0])/length
    ix=int(np.argmax(dist))
    if dist[ix]>tol:return simplify(points[:ix+1],tol)[:-1]+simplify(points[ix:],tol)
    return [points[0],points[-1]]

# These frame choices belong to the revised page plan, not a guessed data scale.
area=(105,354,725,582)
def xy(g,v):return (area[0]+g/800*(area[2]-area[0]),area[3]-v/1.1*(area[3]-area[1]))
def fmt(points):return ' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
fragments=[]
for a in ['classic','fg']:
    s=stats[a]
    upper=simplify([xy(v['gen'],v['mean']+v['sd']) for v in s])
    lower=simplify([xy(v['gen'],v['mean']-v['sd']) for v in s])
    mean=simplify([xy(v['gen'],v['mean']) for v in s])
    fragments.append(f'<polygon id="curve-{a}-sd" points="{fmt(upper+lower[::-1])}" fill="{colors[a]}" fill-opacity="0.10"/>')
    dash=' stroke-dasharray="7,5"' if a=='nsga3' else ''
    fragments.append(f'<polyline id="curve-{a}-mean" points="{fmt(mean)}" fill="none" stroke="{colors[a]}" stroke-width="{2.8 if a=="fg" else 2}"{dash}/>')
(F/'convergence_marks.fragment.svg').write_text('\n'.join(fragments)+'\n')
scatter=[]
for v in stations:
    x=775+(float(v['slr'])-1.7)/1.9*390
    y=492-(float(v['R_star'])-1.2)/1.8*265
    scatter.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.8" fill="#087E83" stroke="#FFFFFF" stroke-width="1.2"/>')
(F/'station_marks.fragment.svg').write_text('\n'.join(scatter)+'\n')
dots=[]
for i,a in enumerate(order):
    v=stats[a][-1];y=371+i*43
    for j,h in enumerate(v['runs']):
        x=1000+(h-.96)/.11*190
        dots.append(f'<circle cx="{x:.2f}" cy="{y+(j-1)*4:.2f}" r="4.5" fill="#FFFFFF" stroke="{colors[a]}" stroke-width="1.6"/>')
    x=1000+(v['mean']-.96)/.11*190
    dots.append(f'<line x1="{x:.2f}" y1="{y-8}" x2="{x:.2f}" y2="{y+8}" stroke="{colors[a]}" stroke-width="3"/>')
(F/'ablation_marks.fragment.svg').write_text('\n'.join(dots)+'\n')
manifest={'source_files':['sources/historical_model/results/ea_converge.csv','sources/historical_model/results/ea_county_strategy_over2.csv'],
 'normalization':'all K=40 HV divided by mean NSGA-II final HV at generation 800',
 'uncertainty':'sample SD across 3 independent runs at each generation, ddof=1',
 'excluded_rows':'other K values excluded only for the preselected K=40 panel; all K=40 generations/runs used',
 'missing':'none within the reported termination of each algorithm; EPG ends at 400 and is not extended to 800',
 'geometry_simplification_tolerance_px':.45,'smoothing':'none',
 'endpoints':{a:stats[a][-1] for a in order},
 'convergence_reference':reference,'station_n':20,'station_CLR_range':[1.55,2.64],
 'figure_destination':'16:9 English conference slides P02 and P04, not journal submission',
 'standalone_exports':'SVG and PDF vectors; PNG 450 dpi; no title/callout embedded in standalone data layers'}
(F/'provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
(P/'analysis/research_plot_data.json').write_text(json.dumps({'convergence':stats,'stations':stations},indent=2)+'\n')
print('Full-data scientific figures and native mark fragments prepared.')
print('Native path points per mean:',{a:len(simplify([xy(v['gen'],v['mean']) for v in stats[a]])) for a in ['classic','nsga3','fg']})
print('Final raw/mean ranges:',min(min(stats[a][-1]['runs']) for a in order),max(max(stats[a][-1]['runs']) for a in order))
