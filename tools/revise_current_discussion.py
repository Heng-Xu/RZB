"""直接修订甲方批注讨论稿；只改包内正文、修订设置和修改者，不重建Word。"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
from datetime import datetime,timezone
import argparse,hashlib,json,re,sys
from lxml import etree as E
from docx import Document

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'研究报告/甲方反馈/10.11/供电公司讨论稿.docx'
REPORT=ROOT/'研究报告/04_word/研究报告终稿.docx'
REVIEW=ROOT/'研究报告/05_review/当前版/1013讨论稿批注修订'
BACKUP=ROOT/'研究报告/05_review/当前版/1013局部表述复核/修前快照/供电公司讨论稿.docx'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W};qn=lambda n:'{'+W+'}'+n
AUTHOR='xh'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xml(data):return E.fromstring(data)
def serialize(x):return E.tostring(x,xml_declaration=True,encoding='UTF-8',standalone=True)
def text(el):return ''.join(el.xpath('.//w:t[not(ancestor::w:del)]/text()',namespaces=NS))
def md_rows(value):
 return [[c.strip() for c in line.strip('|').split('|')] for line in value.splitlines() if line.startswith('|') and not re.fullmatch(r'[| :\-]+',line)]
def assets():
 a=ROOT/'研究报告/02图表/当前版'
 return json.loads((a/'计算表.json').read_text()),json.loads((a/'生成段落.json').read_text())

def content():
 t,s=assets();changes={
 4:'分布式光伏发展使主变同时承担晚间正向供电和日间反向输送任务，容量配置需结合两个方向的峰值及最大单台主变退出运行（N-1）后的供电安全要求，联合比较增容、联络与储能措施。',
 5:'',
 10:'DL/T 5729—2023《配电网规划设计技术导则》按负荷发展阶段给出容载比建议范围。2025年4月《配电网规划设计技术导则（修订稿）》第6.2.2.1条提出总体控制在1.5～2.0，并允许在建议范围内无法满足供电安全准则时结合实际适当提高[1]。',
 11:'本研究比较同一起点、相同供电约束下的刚性与弹性方案，以具体设备配置及费用解释容载比。方案通过所选静态工况校核；超过导则建议上限的必要性需结合建议范围内可选设备与转供方案另行论证。',
 20:'地区案例采用2022—2025年实际年度负荷和新能源规模回算。两类方案共用初始设备、候选网络和工程价格；邳州、市区初始主变容量分别为1463.50 MVA、2900.00 MVA，基期容载比均约2.00。建设过程为共同起点下的规划回算安排。（研究报告第5.1节）',
 21:'刚性方案新增容量按当年负荷的2.0倍控制，并采用储能及10 kV联络满足供电要求；当年负荷回落时保留上一年度在役主变容量，容载比可随之超过2.0。弹性方案按站级承载需求与评价期费用比选配置，最大容量由允许设备规格及可扩建位置确定。',
 23:'模型分别选取邳州26个、市区45个同期静态截面，覆盖区域正向峰值、日间最低净负荷及各站局部极值，逐一校核正常运行和各站最大单台主变N-1。故障站采用剩余主变容量，邻站采用正常可用容量，正常运行允许调整供区，故障后重新安排负荷转接。',
 24:'转供受送端可切负荷、共享馈线余量、联络有效能力和受端主变容量共同限制。既有转供依据变电站全停条件下的逐站统计建模，每站转出之和受原统计站外可供负荷与既有网络预算的较小值限制。地区全部电压等级负荷加权转供率为邳州约67%、市区约92%，用于说明网络背景；110 kV案例采用匹配站点的MW上限。区域内部转入、转出合计相等，新能源保留原站归属，转接后同步校核反向容量。（研究报告第3.6、5.2节）',
 25:'正向储能支撑持续时间分别采用邳州2 h、市区6 h，对应补齐8760小时曲线的95%峰值阈值下最长连续近峰时长。储能有效功率按额定功率与可用电量在给定时长内折算功率的较小值确定，可用电量系数为0.76；实际储能定容结合局部功率缺口及其持续过程。（研究报告第3.4、4.4节）',
 27:'采用混合整数线性优化联合确定主变规格、储能规模、联络建设及投运年份，以共同评价期费用最小为经济目标。主变和10 kV线路设备寿命均为40年，储能为25年；评价期为2021年末至2041年末，2022—2025年投运措施的新增建设、固定运维及期内更新费用按6%折现率折算至2021年末。',
 31:'表1汇总两类方案2025年年末在役规模及共同评价期费用，逐年新增工程和容量变化分别见表2、表3。',
 32:'表1 两地区2025年配置与评价期费用',
 34:'两地区刚性方案费用现值合计21790.82万元，弹性方案为15793.49万元，减少5997.33万元，约28%。',
 36:s['restore_cost_components'].split('\n\n')[0],
 37:s['restore_cost_components'].split('\n\n')[1],
 38:'费用比较对应上述具体可行方案。各措施费用按同一工程价格及评价期计算，容量、储能和联络的变化分别对应主变采购、储能投资及新增通道费用。',
 40:'邳州弹性方案2022年先增加240.50 MVA主变容量，降低了后续配储需求；刚性方案分两次完成相同的容量净增，但2025年储能额定能量为48.81 MWh，弹性方案为7.74 MWh。市区弹性方案在翟山变将一台40 MVA主变更换为63 MVA，净增23 MVA，最大80 MVA主变停运后的剩余容量由40 MVA提高至63 MVA；刚性方案保留原主变，新增5项联络满足相同工况要求。（研究报告第5.4、5.5节）',
 41:'主变按整台规格配置，更换较小主变或增加台数会改变N-1后的剩余容量。站间联络还需邻站具备承接余量，设备规格、站点分布和支援路径共同决定区域容量及费用。',
 43:'新购主变容量包含更换及扩建所采购设备的铭牌容量，净增容量为新购容量扣除同期被替换设备容量。例如，邳州弹性方案2022年新购483.50 MVA、替换243.00 MVA，净增240.50 MVA。表2、表3中的联络和储能为当年新增，主变容量为年末在役规模。',
 44:'表2 邳州弹性方案逐年措施',
 46:'邳州弹性方案2022年完成主要主变调整，年末容量达到1704.00 MVA，容载比2.07。2023年容量保持不变，负荷由825.00 MW降至761.23 MW，容载比升至2.24。2024年负荷恢复至862.66 MW，新增2项联络，容载比降至1.98。',
 47:'2025年主变容量继续保持1704.00 MVA，负荷增至956.45 MW，容载比降至1.78；当年新增6项联络及3.60 MW储能，对应额定能量7.74 MWh，四年累计新增联络14项。',
 49:'表3 市区弹性方案逐年措施',
 51:'市区弹性方案2022年新购63.00 MVA主变用于更换原40 MVA设备，净增23.00 MVA，年末容量2923.00 MVA，容载比2.04。2023年负荷增至1542.22 MW，沿用已有主变及联络，容载比降至1.90。四年均无新增联络和储能。',
 52:'2024年容量保持2923.00 MVA，负荷回落至1449.40 MW，容载比升至2.02；2025年负荷恢复至1528.82 MW，容载比降至1.91。两年的比值变化由年度负荷变化形成。',
 62:'两地区逐年配置体现各自的源荷、设备与网络条件。推广分析进一步采用独立五站模板，比较不同参数组合下的容量与配套工程。',
 65:'2025年4月《配电网规划设计技术导则（修订稿）》第6.2.2条将负荷增长、负荷分散和转移能力列为容载比影响因素，第7.4.2.2条要求结合新能源规模校核反向容量，并开展增容与储能比选[1]。六项参数据此覆盖源荷规模、网络支援及措施经济性。',
 66:'（1）分布式电源装机渗透率：同范围分布式电源装机容量与用户最大负荷之比，无量纲。该导则第6.5.4条给出指标定义，第7.4.2.2条联系反向承载校核；装机增长提高日间反向输送需求[1]。',
 67:'（2）年最大净负荷平均增长率：同范围起止年度年网供最大负荷的复合年平均增长率，以%/年表示。该导则第6.2.2.1条据此划分发展阶段；负荷增长同时影响容量需求与容载比分母[1]。',
 68:'（3）电缆长度占比：电缆长度占电缆与架空线路总长度的比例，以百分比表示。线路形式影响单位长度工程费用[2]；按架空24万元/km、电缆180万元/km加权，市区80%、邳州约11%分别对应单项3 km新增联络投资452.40万元、128.38万元。（研究报告第4.3节）',
 69:'（4）初始转供率：基期可转负荷与相应网供最大负荷之比，以百分比表示。该导则第6.2.2.1条及中压网络研究说明联络和转供能力与容量储备的关系[1][3]；参数通过既有网络支援影响新增工程。',
 70:'（5）储能支撑持续时间：给定功率缺口需要连续支撑的时长，单位h。储能定容同时考虑额定功率、可用能量及缺口持续过程[4][5]，持续时间延长会降低相同储能能量对应的有效支撑功率。',
 71:'（6）负荷分散系数：各站最大正向净负荷之和与区域同步曲线最大正向净负荷之比，无量纲。该导则第6.2.2条将其列为容量储备影响因素[1]；参数反映局部峰值相对区域同时峰值的分散程度。',
 72:'5.2 推广矩阵与查表条件',
 73:'五站模板每站初始两台50 MVA主变，区域基期网供峰值250 MW，按源荷分布及候选网络开展基期后第4年的静态比选。34686个联合组合中，32112个有效组合形成容载比区间。按电缆长度占比三档、储能支撑持续时间2/4/6 h、负荷分散系数1.00/1.10/1.15组织为27张矩阵、1296个单元，已计算容载比总体范围1.36～3.15。（研究报告第5.6节）',
 74:'表7列示电缆长度占比>30%、储能支撑持续时间4 h、负荷分散系数1.10时的矩阵。行按平均增长率和装机渗透率分组，列为初始转供率四档；储能持续时间和负荷分散系数分别按三个定值查表。',
 75:'表7 电缆长度占比>30%、储能支撑4 h、负荷分散系数1.10时的容载比区间',
 78:'表7中，装机渗透率≤1、平均增长率处于(4%,7%]时，初始转供率由≤30%档提高至>70%档，容载比区间由1.98～2.10降至1.52～1.78。较强的既有网络支援可利用邻站余量，减少部分本地主变需求。',
 79:'装机渗透率较高时，日间反向功率增大，主变与储能共同决定承载能力。源荷条件固定后，转供率对容量的作用还存在设备切换节点，表8进一步给出同一背景参数下的受控序列。',
 83:'（2）核实网络和经济条件。按馈线和邻站能力确定初始转供率，以电缆与架空线路长度统计电缆长度占比，结合工程造价折算联络费用，并按局部功率缺口确定储能支撑持续时间。',
 84:'（3）查找对应单元。先按电缆长度占比、储能支撑持续时间和负荷分散系数确定矩阵，再按平均增长率、装机渗透率及初始转供率查找容量区间。',
 88:'6.1 逐站转供能力与实际运行条件是否一致',
 89:'当前模型采用变电站全停条件下的转供统计，并将逐站可转负荷上限落实到110 kV站点。需结合现有联络运行方式，讨论统计转供能力在日常及故障工况下的可用程度，明确哪些通道和可切负荷能够用于站间支援。',
 90:'6.2 市区电缆长度占比与联络工程费用如何对应',
 91:'市区电缆长度占比采用80%，按参考造价折算的3 km新增联络投资为452.40万元。讨论典型联络的路径长度、敷设构成及综合工程价格是否与实际实施费用一致，并据本地工程依据完善费用比选。',
 }
 result=[['地区／方案','主变容量\nMVA','容载比','储能额定功率\nMW','累计新增联络\n条','费用现值\n万元']]
 annual={}
 cost=md_rows(t['new_cost_comparison'])
 for region,key,eng in [('邳州','new_pizhou_years','restore_pizhou_construction'),('市区','new_city_years','restore_city_construction')]:
  ys=md_rows(t[key]);es=md_rows(t[eng])
  for scheme in ['刚性','弹性']:
   row=next(r for r in ys[1:] if r[:2]==[scheme,'2025']);fee=next(r[2] for r in cost[1:] if r[:2]==[region,scheme])
   result.append([region+scheme,row[3],row[4],row[5],row[6],fee])
  rows=[['年份','当年新购主变\nMVA','当年新增联络\n条','当年新增储能\nMW','年末主变容量\nMVA','年末容载比']];prev=0
  for a in ys[1:]:
   if a[0]!='弹性':continue
   e=next(r for r in es[1:] if r[:2]==a[:2]);power=float(a[5]);rows.append([a[1],e[3],e[6],f'{power-prev:.2f}',a[3],a[4]]);prev=power
  annual[region]=rows
 # 这些表直接来自已完成三阶段核验的研究报告资产。
 tables={33:result,45:annual['邳州'],50:annual['市区'],76:md_rows(t['current_matrix_2_4_1.10'])}
 additions={
 53:[('p','按2021—2025年复合平均增长率统一分档，邳州约7%，属于中等增长，导则建议容载比1.7～1.9；其弹性方案2022—2024年高于建议上限，2025年进入范围。市区约1%，属于饱和期，建议1.5～1.7，四年均高于建议上限[1]。以2025年为例，市区负荷按1.7折算容量为2598.99 MVA，而共同初始容量已为2900.00 MVA，再增加23 MVA后形成1.91；既定初始设备与新增补强分别解释超出幅度。')],
 71:[('caption','表4 六项参数的采样节点与矩阵分类'),('table',md_rows(t['new_parameter_bins'])),
     ('p','参数与容载比采用固定其余五项后的组内相关，各组至少包含两个有效节点。各参数值与容载比分别减去组均值后汇总计算Pearson系数，保留零响应组；输入参数间关联采用同一有效情景库的相关矩阵。'),
     ('caption','表5 六项参数与容载比的组内相关'),('table',md_rows(t['current_controlled_correlations'])),
     ('p','装机渗透率的组内相关系数为0.88，对应反向容量需求随装机增长而提高。平均增长率、初始转供率分别为－0.80、－0.74，前者包含负荷增加对容载比分母的作用，后者反映邻站支援对新增容量及联络的替代。电缆长度占比、储能支撑持续时间、负荷分散系数分别为0.45、0.27、0.52，分别通过联络费用、储能有效功率和局部峰值任务影响设备比选。'),
     ('caption','表6 六项输入参数的Pearson相关矩阵'),('table',md_rows(t['current_input_correlations'])),
     ('p','ηC、ḡ、α、r₀、H、KD依次表示装机渗透率、平均增长率、电缆长度占比、初始转供率、储能支撑持续时间和负荷分散系数。电缆长度占比与初始转供率的Pearson系数为0.28，Spearman系数为0.24，其余输入配对的Pearson绝对值均不超过0.15。本情景库中这两项具有一定共同建设背景，其余参数的线性关联较弱；两项仍分别通过造价和既有网络能力影响配置。')],
 79:[('p','固定装机渗透率1.50、平均增长率4%、电缆长度占比10%、储能支撑持续时间4 h和负荷分散系数1.10，比较初始转供率的完整受控序列。'),
     ('caption','表8 固定源荷与线路条件下的初始转供率比较'),('table',md_rows(t['current_transfer_sequence'])),
     ('p','初始转供率由10%提高至30%时，主变容量由650 MVA降至550 MVA，容载比由2.22降至1.88；30%以后容量保持550 MVA，但新增联络继续减少，70%及以上采用相同配置。转供能力改善可以先减少主变需求，再体现为联络投资下降，容量的分段响应需结合设备组合与费用共同判断。')]
 }
 refs={}
 for p in Document(REPORT).paragraphs:
  if m:=re.match(r'^\[(\d+)\]',p.text):refs[int(m[1])]=p.text[m.end():].strip()
 additions[91]=[('heading','参考依据')]+[('reference',f'[{i}] '+refs[n]) for i,n in enumerate([7,12,8,10,28],1)]
 return changes,tables,additions

class Reviser:
 def __init__(self,root):
  self.root=root;ids=[int(v) for v in root.xpath('.//@w:id',namespaces=NS) if str(v).isdigit()]
  self.next=max(ids+[0])+1;self.date=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
 def mark(self,kind):
  x=E.Element(qn(kind));x.set(qn('id'),str(self.next));self.next+=1;x.set(qn('author'),AUTHOR);x.set(qn('date'),self.date);return x
 def replace(self,p,value):
  old=text(p)
  if old==value:return
  # 既有插入和删除容器原位保留，新增删除包裹其可见run，原作者与id继续保留。
  for r in list(p.xpath('.//w:r[not(ancestor::w:del)]',namespaces=NS)):
   if not r.xpath('./w:t|./w:br',namespaces=NS):continue
   parent=r.getparent();idx=parent.index(r);parent.remove(r)
   for t in r.xpath('.//w:t',namespaces=NS):t.tag=qn('delText')
   deletion=self.mark('del');deletion.append(r);parent.insert(idx,deletion)
  if value:
   insertion=self.mark('ins');run=E.Element(qn('r'));sample=p.find('.//'+qn('rPr'))
   if sample is not None:run.append(deepcopy(sample))
   chunks=value.split('\n')
   for i,chunk in enumerate(chunks):
    if i:run.append(E.Element(qn('br')))
    node=E.SubElement(run,qn('t'));node.set('{http://www.w3.org/XML/1998/namespace}space','preserve');node.text=chunk
   insertion.append(run)
   # 新文字放在原批注范围内，保留原批注ID与评论内容。
   tail=list(p.xpath('./w:commentRangeEnd|./w:r[w:commentReference]',namespaces=NS))
   for x in tail:p.remove(x)
   p.append(insertion)
   for x in tail:p.append(x)
  else:
   pr=p.find(qn('pPr'))
   if pr is None:pr=E.Element(qn('pPr'));p.insert(0,pr)
   rp=pr.find(qn('rPr'))
   if rp is None:rp=E.SubElement(pr,qn('rPr'))
   rp.append(self.mark('del'))
 def new_paragraph(self,template,value,kind='p'):
  p=E.Element(qn('p'));pr=template.find(qn('pPr'))
  if pr is not None:p.append(deepcopy(pr))
  if p.find(qn('pPr')) is None:p.insert(0,E.Element(qn('pPr')))
  pr=p.find(qn('pPr'));rp=E.SubElement(pr,qn('rPr'));rp.append(self.mark('ins'))
  ins=self.mark('ins');run=E.SubElement(ins,qn('r'));rpr=E.SubElement(run,qn('rPr'))
  rf=E.SubElement(rpr,qn('rFonts'));rf.set(qn('ascii'),'Times New Roman');rf.set(qn('hAnsi'),'Times New Roman');rf.set(qn('eastAsia'),'宋体' if kind=='caption' else '方正仿宋_GBK')
  sz=E.SubElement(rpr,qn('sz'));sz.set(qn('val'),'21' if kind=='caption' else '23')
  if kind=='heading':E.SubElement(rpr,qn('b'))
  node=E.SubElement(run,qn('t'));node.text=value;p.append(ins);return p
 def new_row(self,prototype,values,header=False):
  tr=E.Element(qn('tr'));trpr=E.SubElement(tr,qn('trPr'));trpr.append(E.Element(qn('cantSplit')));trpr.append(self.mark('ins'))
  if header:E.SubElement(trpr,qn('tblHeader'))
  cells=prototype.findall(qn('tc'))
  for i,value in enumerate(values):
   tc=deepcopy(cells[min(i,len(cells)-1)])
   for child in list(tc):
    if child.tag!=qn('tcPr'):tc.remove(child)
   p=E.SubElement(tc,qn('p'));oldp=cells[min(i,len(cells)-1)].find(qn('p'))
   if oldp is not None and oldp.find(qn('pPr')) is not None:p.append(deepcopy(oldp.find(qn('pPr'))))
   if p.find(qn('pPr')) is None:p.append(E.Element(qn('pPr')))
   for revision in list(p.xpath('./w:pPr/w:rPr/w:ins|./w:pPr/w:rPr/w:del',namespaces=NS)):revision.getparent().remove(revision)
   ind=p.find(qn('pPr')).find(qn('ind'))
   if ind is None:ind=E.SubElement(p.find(qn('pPr')),qn('ind'))
   for name in ['firstLine','firstLineChars','hanging','hangingChars','left','right','leftChars','rightChars']:ind.set(qn(name),'0')
   ins=self.mark('ins');r=E.SubElement(ins,qn('r'));rpr=E.SubElement(r,qn('rPr'));rf=E.SubElement(rpr,qn('rFonts'))
   for name in ['ascii','hAnsi']:rf.set(qn(name),'Times New Roman')
   rf.set(qn('eastAsia'),'宋体');sz=E.SubElement(rpr,qn('sz'));sz.set(qn('val'),'18')
   if header:E.SubElement(rpr,qn('b'))
   for j,part in enumerate(value.split('\n')):
    if j:E.SubElement(r,qn('br'))
    E.SubElement(r,qn('t')).text=part
   p.append(ins);tr.append(tc)
  return tr
 def new_table(self,template,values):
  tbl=deepcopy(template)
  for child in list(tbl):
   if child.tag==qn('tr'):tbl.remove(child)
  grid=tbl.find(qn('tblGrid'))
  if grid is None:grid=E.SubElement(tbl,qn('tblGrid'))
  for child in list(grid):grid.remove(child)
  width=8306;cols=len(values[0]);sizes=[width//cols]*cols;sizes[-1]+=width-sum(sizes)
  for size in sizes:E.SubElement(grid,qn('gridCol')).set(qn('w'),str(size))
  pr=tbl.find(qn('tblPr'));tw=pr.find(qn('tblW'));tw.set(qn('type'),'dxa');tw.set(qn('w'),str(width))
  for change in list(pr.findall(qn('tblPrChange'))):pr.remove(change)
  for i,row in enumerate(values):
   tr=self.new_row(template.findall(qn('tr'))[0 if i==0 else 1],row,i==0)
   for c,size in zip(tr.findall(qn('tc')),sizes):
    cp=c.find(qn('tcPr'));cw=cp.find(qn('tcW'));cw.set(qn('type'),'dxa');cw.set(qn('w'),str(size))
    ppr=c.find(qn('p')).find(qn('pPr'));kn=ppr.find(qn('keepNext'))
    if kn is None:kn=E.SubElement(ppr,qn('keepNext'))
    kn.set(qn('val'),'1' if len(values)<=8 and i<len(values)-1 else '0')
   tbl.append(tr)
  return tbl
 def replace_table(self,tbl,values):
  oldrows=tbl.findall(qn('tr'));oldgrid=deepcopy(tbl.find(qn('tblGrid')));new=self.new_table(tbl,values)
  for tr in oldrows:
   pr=tr.find(qn('trPr'))
   if pr is None:pr=E.Element(qn('trPr'));tr.insert(0,pr)
   if pr.find(qn('tblHeader')) is not None:
    previous=deepcopy(pr)
    for header in list(pr.findall(qn('tblHeader'))):pr.remove(header)
    change=self.mark('trPrChange');change.append(previous);pr.append(change)
   pr.append(self.mark('del'))
   for paragraph in tr.findall('.//'+qn('p')):self.replace(paragraph,'')
  # 新旧网格通过原生属性修订关联，拒绝xh修订可恢复原表。
  grid=tbl.find(qn('tblGrid'));grid.clear()
  for x in new.find(qn('tblGrid')):grid.append(deepcopy(x))
  change=self.mark('tblGridChange');change.append(oldgrid);grid.append(change)
  oldpr=deepcopy(tbl.find(qn('tblPr')));pr=tbl.find(qn('tblPr'))
  for c in list(pr):pr.remove(c)
  for c in new.find(qn('tblPr')):pr.append(deepcopy(c))
  change=self.mark('tblPrChange');change.append(oldpr);pr.append(change)
  for tr in new.findall(qn('tr')):tbl.append(tr)


def accept_view(root,author=None):
 r=deepcopy(root)
 # 仅供核验与临时排版预览；交付文件绝不接受已有修订。
 for row in list(r.xpath('.//w:tr',namespaces=NS)):
  dels=row.xpath('./w:trPr/w:del',namespaces=NS)
  if any(author is None or x.get(qn('author'))==author for x in dels):row.getparent().remove(row)
 for el in list(r.xpath('.//w:del|.//w:moveFrom',namespaces=NS)):
  if author is None or el.get(qn('author'))==author:
   if el.getparent() is not None:el.getparent().remove(el)
 for el in list(r.xpath('.//w:ins|.//w:moveTo',namespaces=NS)):
  if author is not None and el.get(qn('author'))!=author:continue
  parent=el.getparent()
  if parent is None:continue
  pos=parent.index(el)
  for c in list(el):parent.insert(pos,c);pos+=1
  parent.remove(el)
 for el in list(r.xpath('.//w:tblPrChange|.//w:tblGridChange',namespaces=NS)):
  if el.getparent() is not None:el.getparent().remove(el)
 return r

def write_package(path,original,replacements):
 temp=path.with_suffix('.tmp.docx')
 with ZipFile(temp,'w',ZIP_DEFLATED) as z:
  for info,data in original:z.writestr(info,replacements.get(info.filename,data))
 temp.replace(path)

def reject_xh(root):
 r=deepcopy(root)
 for p in list(r.xpath('.//w:p[w:pPr/w:rPr/w:ins[@w:author="xh"]]',namespaces=NS)):
  p.getparent().remove(p)
 for row in list(r.xpath('.//w:tr[w:trPr/w:ins[@w:author="xh"]]',namespaces=NS)):
  row.getparent().remove(row)
 for tbl in list(r.xpath('.//w:tbl[not(w:tr)]',namespaces=NS)):tbl.getparent().remove(tbl)
 for change in list(r.xpath('.//w:tblPrChange[@w:author="xh"]|.//w:tblGridChange[@w:author="xh"]|.//w:trPrChange[@w:author="xh"]',namespaces=NS)):
  parent=change.getparent();old=deepcopy(change[0]);parent.getparent().replace(parent,old)
 for deletion in list(r.xpath('.//w:del[@w:author="xh"]',namespaces=NS)):
  parent=deletion.getparent();pos=parent.index(deletion)
  for child in list(deletion):
   for t in child.xpath('.//w:delText',namespaces=NS):t.tag=qn('t')
   parent.insert(pos,child);pos+=1
  parent.remove(deletion)
 for insertion in list(r.xpath('.//w:ins[@w:author="xh"]',namespaces=NS)):
  insertion.getparent().remove(insertion)
 return r

def apply():
 REVIEW.mkdir(parents=True,exist_ok=True)
 assert TARGET.read_bytes()==BACKUP.read_bytes(),'原稿已变化，须重新核对逐段定位，禁止覆盖新的用户修改'
 with ZipFile(TARGET) as z:original=[(i,z.read(i.filename)) for i in z.infolist()];parts={i.filename:b for i,b in original}
 root=xml(parts['word/document.xml']);body=root.find(qn('body'));elements=list(body);changes,tables,additions=content();revision=Reviser(root);log=[]
 for index,value in changes.items():
  p=elements[index];assert p.tag==qn('p');before=text(p);revision.replace(p,value);log.append(dict(原段落=index,原文=before,新文=value))
 for index,values in tables.items():
  tbl=elements[index];assert tbl.tag==qn('tbl')
  if len(tbl.findall(qn('tr')))==len(values) and all(len(tr.findall(qn('tc')))==len(row) for tr,row in zip(tbl.findall(qn('tr')),values)):
   for tr,row in zip(tbl.findall(qn('tr')),values):
    for tc,value in zip(tr.findall(qn('tc')),row):revision.replace(tc.find(qn('p')),value)
  else:revision.replace_table(tbl,values)
 for index,items in additions.items():
  anchor=elements[index]
  for kind,value in items:
   if kind=='table':el=revision.new_table(elements[76],value)
   else:el=revision.new_paragraph(elements[32] if kind=='caption' else elements[90] if kind=='heading' else elements[53],value,kind)
   anchor.addnext(el);anchor=el
 settings=xml(parts['word/settings.xml']);track=settings.find(qn('trackRevisions'))
 if track is None:track=E.Element(qn('trackRevisions'));settings.insert(0,track)
 track.set(qn('val'),'true')
 core=xml(parts['docProps/core.xml']);cp={'cp':'http://schemas.openxmlformats.org/package/2006/metadata/core-properties','dcterms':'http://purl.org/dc/terms/'}
 core.find('cp:lastModifiedBy',cp).text=AUTHOR;core.find('dcterms:modified',cp).text=revision.date
 replacements={'word/document.xml':serialize(root),'word/settings.xml':serialize(settings),'docProps/core.xml':serialize(core)}
 record={'状态':'已修订，待原生与版面核验','源稿':str(TARGET.relative_to(ROOT)),'修前SHA256':sha(BACKUP),'研究报告SHA256':sha(REPORT),'修订作者':AUTHOR,'修改段落':log,'表格来源':tables,'新增表格与正文':additions,'仅修改包部件':list(replacements)}
 write_package(TARGET,original,replacements);record['修后SHA256']=sha(TARGET)
 (REVIEW/'修订核验.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 check()

def check():
 record=json.loads((REVIEW/'修订核验.json').read_text());assert sha(TARGET)==record['修后SHA256'],'修订文件在登记后发生变化'
 with ZipFile(BACKUP) as z:old={n:z.read(n) for n in z.namelist()}
 with ZipFile(TARGET) as z:new={n:z.read(n) for n in z.namelist()}
 assert new.keys()==old.keys(),'不得重建包或丢失部件'
 allowed=set(record['仅修改包部件'])
 assert all(new[k]==old[k] for k in new if k not in allowed),'未涉及的包部件被改动'
 assert new['word/comments.xml']==old['word/comments.xml'] and new['word/commentsExtended.xml']==old['word/commentsExtended.xml']
 before=xml(old['word/document.xml']);after=xml(new['word/document.xml'])
 rejected=reject_xh(after)
 old_content=[(E.QName(x).localname,text(x)) for x in before.find(qn('body'))]
 rejected_content=[(E.QName(x).localname,text(x)) for x in rejected.find(qn('body'))]
 assert rejected_content==old_content, '拒绝本轮xh修订须恢复原稿全部正文与表格'
 oldrev={(x.tag,x.get(qn('id')),x.get(qn('author'))) for x in before.xpath('.//w:ins|.//w:del',namespaces=NS)}
 newrev={(x.tag,x.get(qn('id')),x.get(qn('author'))) for x in after.xpath('.//w:ins|.//w:del',namespaces=NS)}
 assert oldrev<=newrev,'已有修订作者或id丢失'
 inserted=[x for x in after.xpath('.//w:ins|.//w:del|.//w:tblGridChange|.//w:tblPrChange|.//w:trPrChange',namespaces=NS) if (x.tag,x.get(qn('id')),x.get(qn('author'))) not in oldrev]
 assert inserted and all(x.get(qn('author'))==AUTHOR for x in inserted),'新修订作者须为xh'
 revision_ids=[x.get(qn('id')) for x in after.xpath('.//w:ins|.//w:del|.//w:tblPrChange|.//w:tblGridChange|.//w:trPrChange',namespaces=NS)]
 assert len(revision_ids)==len(set(revision_ids)), '修订ID不得重复'
 for tag in ['commentRangeStart','commentRangeEnd','commentReference']:
  assert sorted(before.xpath('.//w:'+tag+'/@w:id',namespaces=NS))==sorted(after.xpath('.//w:'+tag+'/@w:id',namespaces=NS)),tag+'被破坏'
 for row in after.xpath('.//w:tr[w:trPr/w:del[@w:author="xh"]]',namespaces=NS):
  assert not row.xpath('.//w:r/w:t[not(ancestor::w:del)]',namespaces=NS),'删除表行须同步标记单元格文字删除，防止WPS最终视图残留旧内容'
 settings=xml(new['word/settings.xml']);assert settings.find(qn('trackRevisions')).get(qn('val'))=='true'
 final=accept_view(after);body=final.find(qn('body'));paragraphs=[text(p) for p in body.findall(qn('p'))];visible='\n'.join(paragraphs)
 from check_report_policy import body_policy_errors
 policy=json.loads((ROOT/'tools/report_policy.json').read_text())
 assert not body_policy_errors([('供电公司讨论稿.docx',visible)],{},{},policy['forbidden_body_patterns'])
 for stale in ['线路成本系数','12600','648个','120219.30','84449.61','855.00','3324.00','40%为','局部六馈线','被动超限','统一采用4 h']:
  assert stale not in visible,'讨论稿旧结果或表述未清理:'+stale
 tables=body.findall(qn('tbl'));assert len(tables)==8,len(tables)
 rows=lambda tbl:[[text(tc).replace('\n','') for tc in tr.findall(qn('tc'))] for tr in tbl.findall(qn('tr'))]
 changes,expected,additions=content()
 for idx,tablepos in [(33,0),(45,1),(50,2),(76,6)]:
  left=[[v.replace('\n','') for v in row] for row in expected[idx]];assert rows(tables[tablepos])==left,('表格与当前报告不一致',idx)
 for tablepos,key in [(3,'new_parameter_bins'),(4,'current_controlled_correlations'),(5,'current_input_correlations'),(7,'current_transfer_sequence')]:
  t,_=assets();assert rows(tables[tablepos])==md_rows(t[key]),('补充表格不一致',key)
 assert len(visible)>5500 and '40年' in visible and '25年' in visible and '2041年' in visible
 touched=set(changes)|set(expected)|set(additions)
 # 原有正文节点在原位保留；未涉及段落逐节点字节复核。
 oldbody=list(before.find(qn('body')));afterbody=list(after.find(qn('body')))
 original_ids=[x.get('{http://schemas.microsoft.com/office/word/2010/wordml}paraId') for x in oldbody]
 unchanged=0
 for i,oldel in enumerate(oldbody):
  if i in touched:continue
  matches=[x for x in afterbody if original_ids[i] and x.get('{http://schemas.microsoft.com/office/word/2010/wordml}paraId')==original_ids[i]]
  if oldel.tag==qn('sectPr'):matches=[after.find(qn('body')).find(qn('sectPr'))]
  assert len(matches)==1 and E.tostring(matches[0])==E.tostring(oldel),('未涉及节点变化',i)
  unchanged+=1
 record.update(状态='原生核验通过，待WPS版面检查',保留已有修订=len(oldrev),新增修订=len(inserted),批注数=len(xml(new['word/comments.xml'])),未涉及原节点保持=unchanged,最终视图表格数=len(tables),研究报告SHA256=sha(REPORT))
 proof_path=REVIEW/'WPS版面核验.json'
 if proof_path.exists():
  proof=json.loads(proof_path.read_text())
  assert proof['DOCX_SHA256']==sha(TARGET),'WPS核验对应的DOCX已变化，须重新导出核验'
  assert proof['PDF_SHA256']==sha(ROOT/proof['PDF']),'WPS核验PDF发生变化'
  assert proof['状态']=='通过'
  record['状态']='原生修订及WPS版面核验通过'
 (REVIEW/'修订核验.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 (REVIEW/'最终视图正文.txt').write_text(visible+'\n')
 print(json.dumps({k:record[k] for k in ['状态','保留已有修订','新增修订','批注数','未涉及原节点保持','最终视图表格数']},ensure_ascii=False))

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
 apply() if args.apply else check()
