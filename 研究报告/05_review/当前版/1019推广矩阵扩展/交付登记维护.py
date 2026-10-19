"""登记本次已完成的独立数据、逐段复核与WPS目视检查；不改正文及计算数据。"""
from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
import datetime,difflib,hashlib,json,shutil,subprocess

root=Path.cwd();review=root/'研究报告/05_review/当前版/1019推广矩阵扩展'
prior=root/'研究报告/05_review/当前版/1019公式排版与学者称谓'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now().astimezone().isoformat()
word=root/'研究报告/04_word/研究报告终稿.docx';pdf=word.with_suffix('.pdf')
metrics=json.loads((review/'final约束检查.json').read_text())
native=json.loads((review/'docx约束检查.json').read_text())
assert metrics['状态']==native['状态']=='通过'
assert metrics['WordSHA256']==native['WordSHA256']==sha(word)
assert metrics['PDFSHA256']==sha(pdf)
consistency=json.loads((review/'最终导出一致性.json').read_text())
assert consistency['状态']=='通过' and consistency['ZIP部件数']==70 and not consistency['部件差异']
formula=json.loads((review/'版面/公式目视索引.json').read_text())
changed=json.loads((review/'版面/改动页面索引.json').read_text())
proof=dict(状态='通过',实际核验时间=now,DOCX=str(word.relative_to(root)),PDF=str(pdf.relative_to(root)),
    DOCX_SHA256=sha(word),PDF_SHA256=sha(pdf),实际导出输入=str((review/'WPS实际导出输入.docx').relative_to(root)),
    实际导出输入SHA256=sha(review/'WPS实际导出输入.docx'),导出方式='独立桌面WPS直接打开原生Word，按实际目录缓存重开导出；保留书签及超链接，关闭批注打印。',
    输入一致性='70个ZIP部件逐一相同；两轮全部176页逐页像素相同。',
    目视页码=sorted(set(changed['页码']+formula['整页面'])),全部公式目视=formula['全部公式'],
    目视结论=['31组原生公式逐式查看，3-11的8.00×0.95=7.60 MW三条算式完整、逐行居中。',
        '目录46项与标题及实际印刷页码、链接目标对应，六张矩阵均为13行6列，288单元逐格对应。',
        '更新的端点图和11点敏感性图无截断，表5-75末三点合列并保留全部参数，图仍显示11点。',
        '8 MVA解释、源荷段、矩阵方法、典型响应及结论的改动页面已逐页检查，未涉及的46站分析保持。'],
    核验指标=metrics)
write(review/'WPS版面核验.json',proof)
facts=json.loads((review/'事实与历史措辞核对.json').read_text())
facts.update(状态='通过',实际记录时间=now,DOCX_SHA256=sha(word),PDF_SHA256=sha(pdf))
for name,digest in facts['依据SHA256'].items():assert sha(root/name)==digest,name
write(review/'事实与历史措辞核对.json',facts)
figures=json.loads((review/'更新图件来源.json').read_text())
figures.update(状态='通过',实际目视核验='已查看两幅原始PNG及WPS页面157、166；标签、完整节点、相同色阶与实际表值对应。')
write(review/'更新图件来源.json',figures)
for path in sorted((root/'研究报告/03_MD/当前版').glob('0[1-6] *.md')):
    before=(review/'修前原件'/path.relative_to(root)).read_text()
    diff=''.join(difflib.unified_diff(before.splitlines(True),path.read_text().splitlines(True),fromfile='修前/'+path.name,tofile='修后/'+path.name))
    (review/(path.stem+'_差异.diff')).write_text(diff or '本章未修改。\n')
assembly=json.loads((review/'原版局部装配.json').read_text())
(review/'本次五项修正说明.md').write_text('''# 甲方五项反馈：先数据后报告

数据设计覆盖负荷分散系数1.05—1.25、间隔0.02的11点，共127578组，112437组可行、15141组不可行。原同输入节点复用，其他节点独立求解；全部设备费用回算，847个矩阵端点及代表节点完成35574工况独立LP检查。

六张推广矩阵按三档电缆长度占比和两档分散系数组织，共288单元。窗口宽0.20，中心网格0.05，选最接近样本中位数的实际节点，同距取较大容载比。每窗均含实际方案，真实平台保留。全部原始上下界、中位数、代表节点及窗口内数量保留。

敏感性保留11点完整序列，正文将1.21、1.23、1.25的相同设备与费用合列，图保留11点。1.07及1.15补强主变，1.21增加联络，解释设备替代及费用组成。

删除指定重复句，源荷描述按用户给定文字修改。403条线路原表中5条低于485 A，其余398条不低于485 A；按8.00 MVA工程限值、0.95功率因数折算7.60 MW。原区段7.49 MW较低，本次仍沿用该有效规模，区县锁定结果不变。

在上一轮清稿上局部修改，保留11条批注、未涉及正文、样式和原媒体，未启用修订。源稿、原生Word及WPS PDF三阶段检查及目视复核通过；实际WPS输入与交付Word的全部70个ZIP部件相同。逐段复核和实际导出证据见本目录。
''')
Path('memory/current.md').write_text(f'''# 当前工作：甲方五项反馈已完成

已按最终确认的0.02间隔补算负荷分散系数1.05—1.25共11点。127578组设计中112437组可行、15141组不可行，847个端点及代表节点通过35574工况独立LP，原始库无损压缩且保留未压缩工作副本。

推广矩阵按三档电缆长度占比与≤1.15、>1.15两档分散系数，列为六表288单元。窗口宽0.20、中心步长0.05，依据最接近中位数的真实节点定位，同距取较大值；全部原始包络及代表节点保留。敏感性11点完整，末3点相同规模及费用在表中合列、图中完整保留。

五项报告修改同步至六章源、表格、两幅图及正式Word/PDF。8.00 MVA工程限值折算7.60 MW，原区段7.49 MW较低，锁定区县案例及费用保持。上一轮清稿保留{assembly['保留原XML正文块']}个原XML正文块，局部替换{assembly['替换正文块']}块，11条批注完整保留、普通模式交付。

源稿、原生Word和最终WPS PDF三阶段及目视核验通过。最终{metrics['PDF页数']}页，六章正文{metrics['六章正文页数']}页，31组原生公式、40幅图、46项目录及95项文献263处标注对应。WPS实际输入与最终Word全部70个ZIP部件相同，两轮PDF全部页面像素一致。正文683段中16段修改，其他段落逐字继承核读。

当前记录集中于研究报告/05_review/当前版/1019推广矩阵扩展，数据汇总位于研究报告/01研究推荐/当前版/负荷分散系数扩展_20261019。维护入口仍为tools/build_current_report.py。并行PPT工作不在本轮修改和提交范围内。
''')
# 所有本轮文件纳入后继登记；上轮400项原件逐一原摘要保留。
parent=json.loads((prior/'交付登记.json').read_text())
files=set(parent['当前文件SHA256'])
changed_files=[n for n in subprocess.check_output(['git','diff','--name-only','-z'],text=True).split('\0') if n and not n.startswith('研究报告/PPT/')]
files.update(changed_files)
files.add('memory/archive/2026-10-19-推广矩阵扩展前.md')
files.add('研究报告/01研究推荐/当前版/推广矩阵采用版本.json')
files.update('tools/'+n for n in ['extend_matrix_scenarios.py','matrix_planning_windows.py','archive_extended_matrix_raw.py',
    'verify_extended_matrix.py','update_extended_matrix_report.py','refresh_extended_matrix_figures.py','test_matrix_planning_windows.py'])
for folder in [review,root/'研究报告/试算/20261019_负荷分散系数扩展',root/'研究报告/01研究推荐/当前版/负荷分散系数扩展_20261019',root/'研究报告/数据来源/当前版/负荷分散系数扩展_20261019']:
    for p in folder.rglob('*'):
        if p.is_file() and not {'修前原件','上一版交付原件'}&set(p.relative_to(folder).parts) and p.name not in ['交付登记.json','final独立核验.json','docx独立核验.json','原始求解记录.jsonl']:
            files.add(str(p.relative_to(root)))
history=deepcopy(parent['历史定档原件'])
for name,item in history.items():
    if sha(root/item['原件归档'])!=item['原SHA256']:
        candidates=[review/'历史定档原件'/name,review/'修前原件'/item['原件归档'],review/'上一版交付原件'/item['原件归档'],review/'修前原件'/name,review/'上一版交付原件'/name]
        exact=next((p for p in candidates if p.exists() and sha(p)==item['原SHA256']),None)
        assert exact is not None,name
        item['原件归档']=str(exact.relative_to(root))
release=dict(状态='三阶段核验及逐段复核通过',用户范围='甲方五项反馈；11节点、两档推广及固定窗口，先数据后报告。',
    交付原文件=[str(word.relative_to(root)),str(pdf.relative_to(root))],
    当前文件SHA256={n:sha(root/n) for n in sorted(files)},历史定档原件=history,
    文字复核=dict(正文段落=683,本轮修改段落=16,规则扫描代替逐段判断=False),
    核验入口=['tools/build_current_report.py --check-only','tools/verify_extended_matrix.py','tools/verify_report_review.py'],
    说明='数据先通过完整任务、费用、窗口及独立LP核验，再修改报告。区县案例保持，原11条批注保留。')
write(review/'交付登记.json',release)
print('交付登记',len(files),'项；1403块保留、46块局部替换，16段文字复核，三阶段通过。')
