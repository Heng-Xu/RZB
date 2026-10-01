from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[3];A=ROOT/'研究报告/02图表/2026-10-01重构';D=ROOT/'研究报告/01研究推荐/2026-10-01条件矩阵/基准'
headers=['地区','年份','有反送任务站数','反向主导站数','最大绝对峰/MW','最大峰站号'];data=[]
for reg,name in [('pizhou','邳州'),('city','市区')]:
 with (D/reg/'elastic_stations.csv').open(encoding='utf-8-sig') as f:allrows=list(csv.DictReader(f))
 for y in range(2022,2026):
  a=[r for r in allrows if int(r['year'])==y];peak=lambda r:max(float(r['forward_mw']),float(r['reverse_mw']));ma=max(a,key=peak)
  data.append([name,y,sum(float(r['reverse_mw'])>0 for r in a),sum(float(r['reverse_mw'])>float(r['forward_mw']) for r in a),f'{peak(ma):.3f}',ma['station']])
p=A/'计算表.json';t=json.loads(p.read_text());t['direction_dominance']='表3-13 建模任务的主导方向与最大绝对峰（式3-6）\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in data);p.write_text(json.dumps(t,ensure_ascii=False,indent=2))
(Path(__file__).parent/'方向分布复算.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
