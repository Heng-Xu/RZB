from pathlib import Path
from zipfile import ZipFile
import json,hashlib,datetime,shutil,subprocess
import pymupdf
root=Path.cwd();r=root/'研究报告/05_review/当前版/1020矩阵窗口与有功限值修正';prior=root/'研究报告/05_review/当前版/1019推广矩阵扩展';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
word=root/'研究报告/04_word/研究报告终稿.docx';pdf=word.with_suffix('.pdf');m=json.loads((r/'final约束检查.json').read_text());assert m['状态']=='通过' and m['WordSHA256']==sha(word) and m['PDFSHA256']==sha(pdf)
with ZipFile(word) as z:a={n:z.read(n) for n in z.namelist()}
with ZipFile('/tmp/matrix-correct-pass2.docx') as z:b={n:z.read(n) for n in z.namelist()}
assert a==b
shutil.copy2('/tmp/matrix-correct-pass2.docx',r/'WPS实际导出输入.docx')
x=pymupdf.open('/tmp/matrix-correct-pass1.pdf');y=pymupdf.open(pdf);assert len(x)==len(y);diff=[]
for i,(p,q) in enumerate(zip(x,y)):
 if p.get_pixmap(matrix=pymupdf.Matrix(.5,.5)).samples!=q.get_pixmap(matrix=pymupdf.Matrix(.5,.5)).samples:diff.append(i+1)
assert set(diff)<={2,3},diff
write(r/'最终导出一致性.json',{'状态':'通过','ZIP部件数':len(a),'部件差异':[],'实际导出输入SHA256':sha(r/'WPS实际导出输入.docx'),'两轮PDF页数':len(y),'不同页面':diff,'说明':'第二轮实际输入与交付Word每个ZIP部件完全相同；两轮差异仅为已更新的目录页。'})
pages=json.loads((r/'版面/改动页面索引.json').read_text())['页码'];now=datetime.datetime.now().astimezone().isoformat()
write(r/'WPS版面核验.json',{'状态':'通过','实际核验时间':now,'DOCX':str(word.relative_to(root)),'PDF':str(pdf.relative_to(root)),'DOCX_SHA256':sha(word),'PDF_SHA256':sha(pdf),'实际导出输入':str((r/'WPS实际导出输入.docx').relative_to(root)),'实际导出输入SHA256':sha(r/'WPS实际导出输入.docx'),'导出方式':'WPS隔离临时桌面直接打开原生Word副本导出；关闭批注输出，保留书签与超链接，更新目录缓存后重开导出。','目视页码':pages,'目视结论':['目录46项、真实页码及链接目标通过自动逐项比对，并查看两页目录。','第3.5.2节采样表分散系数行显示1.05—1.25、步长0.02、11点。','8.00MW文字及三行原生公式完整居中，未涉及的区段参考规模7.49MW保持。','六张矩阵完整并与288单元数据逐格对应，端点图中文标签及共同色阶完整。','表5-75四档容载比2.05、2.14、2.26、2.43各列一次，配套措施范围与原始节点对应；图保留11点。'],'核验指标':m})
f=json.loads((r/'事实与历史措辞核对.json').read_text());f.update(状态='通过',实际记录时间=now,DOCX_SHA256=sha(word),PDF_SHA256=sha(pdf));write(r/'事实与历史措辞核对.json',f)
f=json.loads((r/'更新图件来源.json').read_text());f.update(状态='通过',实际目视核验='已查看两幅PNG及PDF第157、166页；全部节点与矩阵端点对应，无标签截断。');write(r/'更新图件来源.json',f)
# 原始仿真、费用与年度案例保持；只更新本轮采用说明及展示。
assembly=json.loads((r/'原版局部装配.json').read_text())
(root/'memory/current.md').write_text(f'''# 当前工作：四项局部修正已完成

新增联络统一采用折算后的有功上限8.00 MW，原区段有效规模7.49 MW较低，锁定原始库、年度案例与费用保持。

矩阵基准窗口宽0.10，代表定位网格0.02，同一行接近的不同容量水平以中点接续并局部缩窄，真实平台保留。原11点联合设计及288单元代表节点保持。表5-75采用已有库中装机2.00、增长4%、电缆10%、转供40%、支撑4h的完整11点，正文按容量合并为四行，图和工作簿保留完整数据；3.5.2采样表及说明同步11点。

当前清稿上局部替换{assembly['替换正文块']}块，保留{assembly['保留原XML正文块']}块及11条批注，普通模式。683段正文中9段局部修改，其余逐字继承。源稿、原生Word与WPS PDF三阶段和改动页目视通过，最终{m['PDF页数']}页、六章正文{m['六章正文页数']}页，31组原生公式、40图、46项目录与95项文献对应。实际WPS输入与交付Word全部{len(a)}个ZIP部件相同。

本轮记录：研究报告/05_review/当前版/1020矩阵窗口与有功限值修正。维护入口tools/build_current_report.py。并行PPT不在本轮范围。
''')
(r/'本次四项局部修正说明.md').write_text('''# 四项局部修正

1. 新增联络工程限值按折算后的有功上限直接写8.00 MW，同步文字、原生公式与模板表。区段参考规模低于该上限，原始计算不变。
2. 窗口改为0.10基准宽，代表值按0.02网格定位；接近的容量水平以中点接续、局部缩窄，保留真实平台和较大容量间隔。
3. 表5-75选已有库中的四容量平台场景，按相同容量合并11点为四行；储能、联络、费用给出原始节点范围，图保留11点。
4. 第3.5.2节文字及采样表同步1.05—1.25、步长0.02、11点。

仅调整上述关联文字、表格和两幅图。上一版六章源、Word、PDF及展示数据保留原件，当前Word保留全部11条原批注、关闭修订。源稿、原生Word及最终WPS PDF检查、改动页目视均通过。
''')
# 备份均已逐项核验；未改的同内容文件直接引用既有原件，减少无关重复。
link=json.loads((r/'上一版交付衔接.json').read_text());needed=set(f['依据SHA256']) if '依据SHA256' in f else set()
needed=set(json.loads((r/'事实与历史措辞核对.json').read_text())['依据SHA256']);removed=[]
for name,item in link['原件映射'].items():
 p=root/name;q=root/item['path']
 if q!=p and sha(p)==item['SHA256'] and item['path'] not in needed:
  assert q!=p and sha(q)==item['SHA256']
  item['path']=name;q.unlink();removed.append({'重复备份':str(q.relative_to(root)),'保留原件':name,'SHA256':item['SHA256']})
write(r/'上一版交付衔接.json',link)
if removed or not (r/'重复备份核对.json').exists():write(r/'重复备份核对.json',{'状态':'通过','说明':'仅移除本轮刚生成且与现存原件逐字节一致的重复备份，原始资料和所有变化前原件保持。','记录':removed})
for p in sorted((r/'上一版交付原件').rglob('*'),key=lambda p:-len(p.parts)):
 if p.is_dir() and not any(p.iterdir()):p.rmdir()
# 新版本登记包含上一版的原件证据及本次实际文件。
parent=json.loads((prior/'交付登记.json').read_text());files=set(parent['当前文件SHA256']);files.update(n for n in subprocess.check_output(['git','diff','--name-only','-z'],text=True).split('\0') if n and not n.startswith('研究报告/PPT/'))
for p in r.rglob('*'):
 if p.is_file() and not {'修前原件','上一版交付原件'}&set(p.relative_to(r).parts) and p.name not in ['交付登记.json','final独立核验.json','docx独立核验.json']:files.add(str(p.relative_to(root)))
files.add('memory/archive/2026-10-20-矩阵窗口与有功限值修正前.md')
for name,item in parent['历史定档原件'].items():assert sha(root/item['原件归档'])==item['原SHA256'],name
write(r/'交付登记.json',{'状态':'三阶段核验及逐段复核通过','用户范围':'四项局部修正；用户要求最小化，沿用现有仿真数据与报告结构。','交付原文件':[str(word.relative_to(root)),str(pdf.relative_to(root))],'当前文件SHA256':{n:sha(root/n) for n in sorted(files)},'历史定档原件':parent['历史定档原件'],'文字复核':{'正文段落':683,'本轮修改段落':9,'规则扫描代替逐段判断':False},'核验入口':['tools/build_current_report.py --check-only','tools/verify_extended_matrix.py'],'说明':'已有完整11点库不重算；当前清稿最小化局部装配，11条原批注全部保留。'})
print('交付登记',len(files),'项，重复备份删除',len(removed),'项，ZIP部件',len(a),'PDF目录差异',diff)
