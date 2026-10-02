from pathlib import Path
import json,csv
HERE=Path(__file__).parent;R=HERE.parents[1];A=R/'02图表/2026-10-01甲方修订';D=R/'01研究推荐/2026-10-01甲方修订';TEXT=R/'03_MD/2026-10-01甲方修订'
t=json.loads((A/'计算表.json').read_text());rows=[]
for c,name in [('pizhou','邳州'),('city','市区')]:
 def read(s):return list(csv.DictReader((D/'统一起点基准'/c/(s+'_years.csv')).open(encoding='utf-8-sig')))
 for r,e in zip(read('rigid'),read('elastic')):rows.append([name,int(r['year'])-2021,f'{float(r["clr"]):.4f}',f'{float(e["clr"]):.4f}',f'{float(e["clr"])-float(r["clr"]):.4f}'])
def table(key,title,head,rows):t[key]=title+'\n\n| '+' | '.join(head)+' |\n| '+' | '.join(['---']*len(head))+' |\n'+''.join('| '+' | '.join(map(str,row))+' |\n' for row in rows)
table('rigid_elastic_clr_comparison','表5-0 刚性与弹性容载比逐年对照',['地区','仿真年','刚性容载比','弹性容载比','弹性与刚性差值'],rows)
table('rigid_elastic_interpretation','表5-0 刚性与弹性方案的技术经济比较',['比较内容','刚性方案','弹性方案'],[
 ['仿真起点','同区县容载比2.0','同区县容载比2.0'],['指标条件','各年不超过2.0','各年2.001～2.6'],['技术条件','正常、反向、全负荷单台退出、持续在役及转供守恒','与刚性相同'],['增容、储能及联络','三类措施共同寻优','三类措施共同寻优'],['第4年两地区在役储能','502.4 MW/1080.160 MWh','2.8 MW/6.020 MWh'],['新增措施全寿命费用现值','208566.29万元','35683.63万元'],['推荐判断','作为比较基准','费用降低82.89%，优先采用']])
matrix=json.loads((D/'通用推荐矩阵.json').read_text())
for row in matrix:row['刚性容载比控制上限']='2.0'
(D/'通用推荐矩阵.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2))
table('general_matrix','表5-0 刚性基准与通用弹性容载比推荐区间',['分布式电源装机渗透率','年负荷平均增长率','95%峰值持续时间','主变与线路成本比','主变与储能成本比','刚性上限','推荐弹性容载比'],[[r[k] for k in ['分布式电源装机渗透率','年负荷平均增长率','95%峰值持续时间','主变与线路成本比','主变与储能成本比_3h','刚性容载比控制上限','推荐容载比区间']] for r in matrix])
(A/'计算表.json').write_text(json.dumps(t,ensure_ascii=False,indent=2))
p=TEXT/'05 第五章 弹性容载比寻优与规划建议.md';s=p.read_text();s=s.replace('### 5.4.3 全寿命费用与配置差异','### 5.4.3 刚性与弹性方案的对比')
key='[[SECTION:cost_results]]';s=s.replace(key,'[[TABLE:rigid_elastic_clr_comparison]]\n\n'+key)
key='[[TABLE:measure_totals]]';s=s.replace(key,key+'\n\n[[TABLE:rigid_elastic_interpretation]]\n\n在相同技术校核、负荷和价格条件下，弹性方案提高主变配置，减少退出工况所需储能，两地区新增措施全寿命费用现值降低82.89%，经济性优于刚性。刚性方案保留为规划比较基准，后续建议以弹性指标及其设备组合开展比选。')
s=s.replace('### 5.7.1 按参数区间选择规划范围','### 5.7.1 优先采用弹性指标确定规划范围')
key='规划初期先统一区县与电压等级';s=s.replace(key,'根据两地区技术经济对比，推荐采用弹性方案：仿真第4年邳州容载比2.2118、市区2.2102，对应方案均通过所设技术约束，新增措施费用低于刚性。推广到其他片区时，以通用矩阵确定弹性指标比选范围，同时保留2.0刚性上限方案计算费用差，选取满足技术条件且费用较低的组合。\n\n'+key)
p.write_text(s)
# 为下一轮摘要/结论生成保留刚弹对比。
p=HERE/'完成摘要与结论.py';s=p.read_text()
start=s.index("f'案例结果显示，");end=s.index("',\n'在案例参数",start)
s=s[:start]+'''f'案例第4年邳州刚性、弹性容载比分别为1.9574、2.2118，市区为1.9523、2.2102。两地区刚性、弹性方案新增措施全寿命费用现值分别为{x["刚性合计万元"]:.2f}万元和{x["弹性合计万元"]:.2f}万元，弹性费用降低82.89%。弹性方案增加主变、减少静态退出工况所需储能，在相同技术约束与参考价格下经济性优于刚性。392个站年的容量、守恒与费用复算通过'''+s[end:]
s=s.replace('矩阵用于前期规划范围选取，具体方案依据实际资产、线路和工程价格继续校核。','规划建议优先采用弹性指标确定比选范围，保留刚性基准进行费用对照，并以实际资产、线路和工程价格核定具体方案。')
s=s.replace('### 6.1.3 两地区完成约束下的四年联合寻优','### 6.1.3 弹性方案在案例技术经济比较中优于刚性')
s=s.replace('### 6.2.1 依据标准参数选择比选范围','### 6.2.1 优先采用弹性指标，保留刚性费用基准')
s=s.replace('先核定区县同电压等级公用主变容量','两地区仿真第4年推荐采用邳州2.2118、市区2.2102的弹性方案。该方案在与刚性相同的技术约束下满足容量需求，全寿命费用现值合计降低82.89%。其他片区依据通用矩阵选择弹性范围，同时保留2.0刚性上限方案作为费用对照，形成具体推荐。\n\n先核定区县同电压等级公用主变容量')
p.write_text(s)
print('刚弹容载比、费用和配置对比以及明确推荐已加强')
