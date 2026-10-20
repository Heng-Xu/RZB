from pathlib import Path
import json,hashlib,sys,datetime,difflib
root=Path.cwd();sys.path.insert(0,'tools');from report_prose_review import collect
review=root/'研究报告/05_review/当前版/1020矩阵窗口与有功限值修正';prior=root/'研究报告/05_review/当前版/1019推广矩阵扩展'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old=json.loads((prior/'正文逐段复核.json').read_text())['正文段落'];hs={r['SHA256'] for r in old};current=collect(root,include_discussion=False)
reasons=[
 '第3.5.2节取样说明与表格及当前11点设计一致，其余指标的定义与已核验相关系数保持。',
 '仅将新增联络工程上限明确为折算后的8.00MW；403条线路分类及7.49MW较低区段负荷保持，未改变锁定计算。',
 '成本段同步8.00MW有功上限，保留区段、共享及受端约束和费用计价条件。',
 '真实中位代表节点保持，基准窗口改为0.10，定位网格0.02，按同一行不同容量水平的中点局部缩窄；逐窗包含原始可行方案，真实平台及回升保留。',
 '四窗逐项对应电缆低档、分散低档、增长高档、装机中档的实际288单元数据，接续界值与方法一致。',
 '采用已有完整库中装机2.00、增长4%、电缆10%、转供40%、支撑4h的11点，表按相同容量合并四行，图保留全部节点。',
 '1.11/1.21/1.25三个容量切换点和26/34/50MVA增量与原记录一致；储能8.80MW替代及联络6至5、5至7的变化均有对应节点。',
 '1.21与1.25设备组合及全序列费用4310.32至8339.97万元逐点核对，无把相同数值作为变化；平台内配套措施完整保留。',
 '结论仅将固定0.20宽窗改为基准0.10、接近水平中点接续及局部缩窄，其余结论和相关数值保持。']
changed=[r for r in current if r['SHA256'] not in hs];assert len(changed)==len(reasons)==9
for r,reason in zip(changed,reasons):r.update(复核结论='通过',理由=reason)
for r in current:
 if r['SHA256'] in hs:r.update(复核结论='通过',理由='与上一版已核读正文逐字一致，按SHA256继承事实与文字复核。')
write(review/'正文逐段复核.json',{'状态':'通过','规则扫描代替逐段判断':False,'继承记录':str((prior/'正文逐段复核.json').relative_to(root)),'继承SHA256':sha(prior/'正文逐段复核.json'),'本次修改段落':len(changed),'正文段落':current})
write(review/'本次局部复核.json',{'状态':'通过','段落':changed,'表格复核':['候选采样表仅同步负荷分散系数11点行，其他12行保持。','六表288单元与两组典型8单元按同一新窗口规则生成，原始代表节点保持。','表5-75四行容载比分别2.05、2.14、2.26、2.43，配套范围逐点核对；11点原始数据和图保留。','五站模板表仅同步8.00MW上限，原7.49MW区段规模保持。'],'公式复核':'仅将原式3-23的F_new行改为8.00MW并同步符号解释；保留三行原生公式，其余30组公式不改。','图件复核':'已查看两幅更新PNG，所有11节点保留，端点图逐格对应矩阵，字体及坐标完整。'})
facts=json.loads((prior/'事实与历史措辞核对.json').read_text());refs={}
for name,digest in facts['依据SHA256'].items():
 p=root/name
 if sha(p)!=digest:
  p=review/'上一版交付原件'/name;assert p.exists() and sha(p)==digest,name
 refs[str(p.relative_to(root))]=digest
for p in [review/'有功限值修正依据.json',review/'扩展数据独立核验.json',review/'独立LP核验.json',review/'本次局部复核.json',root/'研究报告/01研究推荐/当前版/负荷分散系数扩展_20261019/窗口与原始节点依据.json']:
 refs[str(p.relative_to(root))]=sha(p)
facts.update(状态='数据及源稿核验通过，待WPS最终版面',实际记录时间=datetime.datetime.now().astimezone().isoformat(),依据SHA256=refs,本轮已解决事项=['8MW有功上限','0.10基准窗口及局部接续缩窄','表5-75四容量平台合并','3.5.2负荷分散系数11取样点同步'],本轮核验={'设计节点':127578,'有效节点':112437,'原始库保持':True,'独立LP节点':json.loads((review/'独立LP核验.json').read_text())['节点数'],'容量平台':[600,626,660,710],'切换点':[1.11,1.21,1.25]})
facts['原始缺口及适用条件']=[v for v in facts['原始缺口及适用条件'] if not v.startswith('8.00 MVA')]+['本轮仅将工程有功上限明确为8.00MW；原区段有效转供7.49106117MW较低，原始求解及锁定费用保持。窗口为中部容量初选范围，原始极值及真实平台另行保留。']
write(review/'事实与历史措辞核对.json',facts)
for p in sorted((root/'研究报告/03_MD/当前版').glob('0[1-6] *.md')):
 before=(review/'修前原件'/p.relative_to(root)).read_text();diff=''.join(difflib.unified_diff(before.splitlines(True),p.read_text().splitlines(True),fromfile='修前/'+p.name,tofile='修后/'+p.name));(review/(p.stem+'_差异.diff')).write_text(diff or '本章未修改。\n')
print('正文',len(current),'段；局部修改',len(changed),'段，其余逐字继承。')
