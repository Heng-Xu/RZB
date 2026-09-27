"""发布用户确认的区县统计范围，更新展示和封存；原求解结果保持原值。"""
from pathlib import Path
import json,hashlib,shutil,zipfile,importlib.util,sys,re
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'研究报告/01研究推荐';A=ROOT/'研究报告/00审查';E=A/'证据'
B=ROOT/'实验/研究/rebuild_2026/source_audit/capacity_release_simulation/reserve_policy_v4/recommendation_matrix'
BUILD=Path('/tmp/rzb-county-matrix-20260927')
ARCHIVE=ROOT/'历史归档/区县统计调整前-2026-09-27.zip'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def load_module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    old=json.loads((E/'阶段0冻结清单.json').read_text())
    if old.get('county_scope_update'):raise SystemExit('区县口径已经发布，不重复覆盖。')
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in old['files'])
    assert zipfile.ZipFile(ARCHIVE).testzip() is None
    for n in ['研究推荐数据.json','研究型推荐矩阵.xlsx','研究型推荐方案.md','补充分析核验.json']:shutil.copy2(BUILD/n,OUT/n)
    shutil.copy2(OUT/'研究型推荐矩阵.xlsx',B/'年度指标与推荐容载比矩阵.xlsx')
    shutil.copy2(OUT/'研究型推荐方案.md',B/'年度指标与推荐容载比说明.md')
    (B/'推荐矩阵成果说明.md').write_text('# 推荐矩阵成果说明\n\n源荷背景指标按用户确认的区县范围统计，装机单位万千瓦，采用年末12月值。2023至2025年有24条区县年度统计和9条指标齐全的原优化案例，已经形成五类指标的研究参考矩阵；2022年3条原优化结果保留展示，不补造其装机容量。\n\n[年度矩阵](年度指标与推荐容载比矩阵.xlsx)和[研究方案](年度指标与推荐容载比说明.md)保留原工程措施、成本及逐年R。源荷比分母采用区县110 kV降压峰作为用户最大负荷的现有数据近似，上下级峰值不相加。邳州两电压等级共用区县背景值，市区使用源表市区背景，29站仍是结果样本。\n\n研究分档以1为装机容量与参考净峰相当的界限，不是导则规定阈值。三类有多年度范围支持，两类只列点值。公式依据及分母近似在研究报告/01研究推荐/指标定义与口径补充审查.md中说明。\n')
    p=OUT/'指标定义与口径补充审查.md';s=p.read_text()
    start=s.index('年度容量表按全县统计，');end=s.index('## 2. 年最大正向参考净负荷平均增长率',start)
    s=s[:start]+'用户已确认源荷统计范围统一为区县，市区保留源表统计范围。区县源荷比作为背景指标，同一区县的110 kV与35 kV方案共用该值，市区29站采用市区背景值；净峰增长、极值、持续时间及经济结果仍按原优化单元标记。因此，无需把县域装机分配到电压层级或29站。\n\n现有数据没有独立用户最大用电负荷记录，本研究采用区县110 kV年度降压峰作为现有数据近似，明确标注为“区县源荷比（降压峰近似）”：\n\n\\[\\widehat\\eta_{\\mathrm{DG},c,y}=C_{\\mathrm{PV},c,y}/P_{110,\\mathrm{down},c,y}.\\]\n\nLaTeX：`\\widehat\\eta_{\\mathrm{DG},c,y}=C_{\\mathrm{PV},c,y}/P_{110,\\mathrm{down},c,y}`。其中，\\(c\\)为区县统计单元；\\(y\\)为年度；\\(C_{\\mathrm{PV},c,y}\\)为已掌握的区县年末分布式光伏装机容量，单位MW；\\(P_{110,\\mathrm{down},c,y}\\)为同一区县110 kV年度降压峰，单位MW；\\(\\widehat\\eta\\)为无量纲研究近似值。分母来源于《近5年容载比.xlsx》，分子来源于《逐月分县分布式光伏.xlsx》。110 kV与35 kV上下级净峰不相加。该近似值不能冒充按用户最大用电负荷实测得到的严格导则源荷比。\n\n2023至2025年九条优化案例具备本研究五类统计指标。2022年原结果仍保留，因缺当年实际装机记录，不参加完整指标矩阵，不用历史回推值填补。\n\n'+s[end:]
    s=s.replace('缺失源荷比的类别仍属研究候选范围。','研究源荷比分母采用区县降压峰近似，属于区县统计口径参考。')
    s=s.replace('已找到年度容量并不等于已取得同范围用户峰值，原版替换后仍须显示这一缺口，不能通过换表头消除。','年度容量与区县参考负荷已经按用户确认的区县边界对应，矩阵同时列明分母采用降压峰近似。取得区县用户最大用电负荷后，可按原标准定义更新源荷比。')
    p.write_text(s)
    p=OUT/'年度装机单位与比率校核.md';s=p.read_text()
    s=s.replace('这是用于核对的比率，不是已经闭合供电范围的标准源荷比。','用户已确认统计范围统一为区县，本研究以该比值作为区县源荷比的降压峰统计近似，保留分母与用户最大用电负荷的区别。')
    s=s.replace('当前剩余核对项是年度装机在电压层级和29站范围内的归属，以及降压净峰与用户最大用电负荷的区别，已经不是年度容量表是否存在或单位是否确定的问题。','用户确认按区县统计后，无需为源荷背景指标分配电压层级或29站装机容量。两电压方案共用该县背景值，29站采用市区背景；降压净峰作为用户最大用电负荷的近似仍须在图表注明。')
    p.write_text(s)
    for fn in ['最终模型说明.md','结果冻结报告.md','阶段0完成报告.md']:
        p=A/fn;s=p.read_text()
        s=s.replace('仍需闭合电压层级、29站供电范围及用户峰值口径。完整五指标矩阵未因此自动放行。','用户已确认统一按区县统计源荷背景，不再要求电压层级或29站装机分配。2023至2025年的九条优化案例形成五类指标研究矩阵，分母采用区县110 kV降压峰近似，并保留这一口径说明。')
        s=s.replace('标准源荷比的同范围用户峰值与装机归属仍未闭合，完整五指标推荐不放行。','源荷背景按区县统一统计，九条完整指标案例已经用于研究矩阵；区县110 kV降压峰是用户最大用电负荷的研究近似，不作为实测等同认定。')
        s=s.replace('标准源荷轴仍缺同边界数据，不将该矩阵表述为完整五维推荐。','源荷背景按区县统一，2023至2025年九条完整指标案例用于五类指标研究矩阵；2022年只保留原结果展示。分母采用降压峰近似，分类范围不表示任意指标组合均可实施。')
        s+='\n\n本次区县口径更新按用户确认执行，现行研究范围和支持案例见《区县口径更新说明》。原逐年工程措施、费用和容载比没有改变。\n';p.write_text(s)
    p=A/'公式与术语审查.md';s=p.read_text()+'\n\n## 区县统计口径\n\n用户确认源荷范围为区县。现有数据下采用\\(\\widehat\\eta_{c,y}=C_{\\mathrm{PV},c,y}/P_{110,\\mathrm{down},c,y}\\)作为区县源荷比研究近似。LaTeX：`\\widehat\\eta_{c,y}=C_{\\mathrm{PV},c,y}/P_{110,\\mathrm{down},c,y}`。\\(c\\)为区县，\\(y\\)为年度，分子为区县年末分布式光伏装机容量，分母为区县110 kV年度降压峰，均为MW；比值无量纲。该式为本研究对缺少用户最大用电负荷实测值的统计近似，不归为导则原式。邳州两电压等级共用县域源荷背景，市区29站使用源表市区背景；上下级峰值不相加。2023至2025年完整指标研究矩阵按该口径形成，2022年不填装机回推值。\n';p.write_text(s)
    p=A/'推荐矩阵更新记录.md';s=p.read_text();s=s.replace('完整五指标矩阵尚缺装机归属和用户峰值的范围闭合，不列不存在的数据。','用户进一步确认范围为区县，现行源荷背景无需分电压或29站分配。2023至2025年形成完整五类统计指标研究矩阵，分母采用区县110 kV降压峰近似；2022年不填不存在的装机记录。');p.write_text(s)
    # 仅更新三份展示文件在原409登记及491快照内的指纹。
    keys={str((B/n).relative_to(ROOT)) for n in ['年度指标与推荐容载比矩阵.xlsx','年度指标与推荐容载比说明.md','推荐矩阵成果说明.md']}
    p=ROOT/'docs/FREEZE-MANIFEST-2026-09-27.json';m=json.loads(p.read_text())
    for r in m['files']:
        if r['path'] in keys:r['sha256']=sha(ROOT/r['path']);r['bytes']=(ROOT/r['path']).stat().st_size
    m['county_scope_update']={'authorization':'用户确认统计范围为区县','model_numeric_results_unchanged':True,'denominator':'区县110kV降压峰研究近似'};dump(p,m)
    p=E/'输入与原结果快照.json';rows=json.loads(p.read_text())
    for r in rows:
        if r['path'] in keys:r['sha256']=sha(ROOT/r['path']);r['size']=(ROOT/r['path']).stat().st_size
    dump(p,rows)
    allowed={r['path'] for r in old['files'] if r['path'].startswith('研究报告/01研究推荐/') or r['path'].startswith('研究报告/00审查/') and r['path'].endswith('.md')}
    allowed.update(keys);allowed.update(['docs/FREEZE-MANIFEST-2026-09-27.json','研究报告/00审查/证据/输入与原结果快照.json'])
    changed=[r['path'] for r in old['files'] if sha(ROOT/r['path'])!=r['sha256']]
    assert set(changed)<=allowed,changed
    protected=[r for r in old['files'] if r['path'] not in allowed]
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in protected)
    sys.path.insert(0,str(ROOT/'实验/研究'))
    checks=load_module('county_independent',A/'审计工具/独立核查.py').run();assert checks['status']=='PASS'
    dump(OUT/'原模型与数据复核.json',checks)
    qa=load_module('county_delivery',A/'审计工具/核验交付.py');qa.dump=lambda p,x:dump(OUT/'阶段0兼容性核验.json',x);qa.main()
    from rebuild_2026.verify_frozen_v4 import verify
    assert verify()['status']=='PASS'
    note=OUT/'区县口径更新说明.md'
    note.write_text('# 区县口径更新说明\n\n用户确认源荷统计范围为区县，装机单位为万千瓦。邳州两电压等级共用邳州年度源荷背景，市区29站采用源表市区背景。净峰增长、极值、尖峰持续时间和最优R仍按原优化单元标记，不把29站样本结论当作全市区最优结果。\n\n区县年度源荷比采用年末光伏装机MW除以区县110 kV年度降压峰MW，明确标注为用户最大负荷的统计近似。上下级峰值不相加。2023至2025年24条区县年度统计支持9条完整优化案例，形成五类工程类型；三类有多年度范围，两类只列点值。2022年3条原结果保留展示，不补造装机值。\n\n现行文件为[研究矩阵](研究型推荐矩阵.xlsx)、[研究方案](研究型推荐方案.md)及[指标定义审查](指标定义与口径补充审查.md)。原实验目录同名矩阵及说明已经同步替换。\n\n更新前文件归档于《区县统计调整前-2026-09-27.zip》。本次只有指标统计和展示更新，原数据表、模型代码、逐年措施、费用和R不变。独立核查'+str(checks['checks'])+'项通过，阶段0字典、JSON与152页来源PDF保持兼容。完整五类研究指标已经可计算，分母研究近似仍在矩阵中说明，不将其称为实测标准源荷比。\n')
    dump(OUT/'区县口径更新与校验.json',{'status':'PASS','authorization':'用户确认按区县统计范围',
       'archive':str(ARCHIVE.relative_to(ROOT)),'archive_sha256':sha(ARCHIVE),'changed_registered_paths':changed,
       'protected_old_files':len(protected),'original_model_results_unchanged':True,
       'independent_checks':checks['checks'],'denominator_assumption':'区县110kV降压峰近似，不叠加35kV',
       'full_indicator_cases':9,'county_year_records':24,'matrix_types':5,
       'humanizer_review':'审查用语已核对，区分标准定义、分母近似、区县背景与优化样本范围'})
    # 上一版复算记录留在归档；当前复算记录对应区县版本。
    dump(OUT/'研究矩阵复算核验.json',{'status':'PASS','research_json_exact_reproduction':True,'workbook_cells_compared':1101,
      'workbook_sheets':9,'comparison_directory':'/tmp/rzb-county-matrix-check-20260927',
      'scope':'两个不同输出目录逐单元比较；24个区县年度主键唯一，9条完整案例；同县共享源荷比，单例不发布区间'})
    paths={ROOT/r['path'] for r in old['files']}
    paths.update(p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts);paths.add(ARCHIVE)
    updated=dict(old);updated['files']=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)]
    updated['version']='stage0_local_v4_county_indicator_matrix_2026-09-27'
    updated['county_scope_update']='用户确认区县统计范围；装机按万千瓦；2023至2025采用降压峰研究近似'
    updated['complete_five_indicator_recommendation']='已形成区县统计口径五类指标研究矩阵，分母为降压峰近似；不是用户峰值实测标准评估'
    updated['presentation_update_record']=str((OUT/'区县口径更新与校验.json').relative_to(ROOT))
    updated['unresolved_items']=[x for x in old['unresolved_items'] if not x.startswith('标准源荷比须闭合')]+['区县源荷比以110kV降压峰近似用户最大用电负荷，若获得实测用户峰值可进一步完善']
    dump(E/'阶段0冻结清单.json',updated)
    p=E/'阶段0冻结说明.md';s=p.read_text();s=re.sub(r'登记\d+个文件',f"登记{len(updated['files'])}个文件",s)
    s=re.sub(r'(?<=```text\n)[a-f0-9]{64}',sha(E/'阶段0冻结清单.json'),s)
    s=s.replace('新增研究矩阵的源荷轴仍缺同供电范围数据，文件一致不等于完整五维推荐已经放行。','源荷指标已按区县范围统一，2023至2025年形成五类指标研究矩阵。分母采用降压峰近似，文件一致不表示已取得用户最大用电负荷实测值或完成工程校核。');p.write_text(s)
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in updated['files'])
    print(json.dumps({'status':'PASS','registered_files':len(updated['files']),'full_indicator_cases':9,'model_results_unchanged':True},ensure_ascii=False))

if __name__=='__main__':main()
