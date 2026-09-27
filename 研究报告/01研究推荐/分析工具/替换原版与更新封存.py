"""按用户2026-09-27授权替换推荐展示文件，保留旧版及原数值证据。"""
from pathlib import Path
import json, hashlib, shutil, zipfile, importlib.util, sys, os

ROOT=Path(__file__).resolve().parents[3]
NEW=ROOT/'研究报告/01研究推荐'
AUDIT=ROOT/'研究报告/00审查'
E=AUDIT/'证据'
MATRIX=ROOT/'实验/研究/rebuild_2026/source_audit/capacity_release_simulation/reserve_policy_v4/recommendation_matrix'
ARCHIVE=ROOT/'历史归档/推荐矩阵替换前-2026-09-27.zip'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    if ARCHIVE.exists():raise SystemExit('替换前归档已存在，请检查更新记录；禁止重复覆盖归档。')
    old=json.loads((E/'阶段0冻结清单.json').read_text())
    assert all((ROOT/r['path']).is_file() and sha(ROOT/r['path'])==r['sha256'] for r in old['files'])
    presentation=[MATRIX/'年度指标与推荐容载比矩阵.xlsx',MATRIX/'年度指标与推荐容载比说明.md',MATRIX/'推荐矩阵成果说明.md']
    audit_docs=[AUDIT/n for n in ['最终模型说明.md','公式与术语审查.md','结果冻结报告.md','阶段0完成报告.md']]
    manifests=[ROOT/'docs/FREEZE-MANIFEST-2026-09-27.json',E/'输入与原结果快照.json',E/'阶段0冻结清单.json',E/'阶段0冻结说明.md']
    archived=presentation+audit_docs+manifests
    with zipfile.ZipFile(ARCHIVE,'x',zipfile.ZIP_DEFLATED) as z:
        for p in archived:z.write(p,str(p.relative_to(ROOT)))
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        for p in archived:assert hashlib.sha256(z.read(str(p.relative_to(ROOT)))).hexdigest()==sha(p)
    shutil.copy2(NEW/'研究型推荐矩阵.xlsx',presentation[0])
    presentation[1].write_text((NEW/'研究型推荐方案.md').read_text()+'\n\n指标数学表达及依据见[指标定义与口径补充审查]('+os.path.relpath(NEW/'指标定义与口径补充审查.md',MATRIX)+')；年度容量与比率核对见[年度装机单位与比率校核]('+os.path.relpath(NEW/'年度装机单位与比率校核.md',MATRIX)+')。\n')
    presentation[2].write_text('# 推荐矩阵成果说明\n\n本目录推荐矩阵及说明已按用户授权替换为工程条件分层的研究版本。年度主变容量、储能配置、转供量、全路径成本和容载比仍来自原v4结果，未重求或修改。\n\n[推荐矩阵](年度指标与推荐容载比矩阵.xlsx)包含指标定义、工程分类研究范围、逐年优化案例、年度装机统计、指标与R关联、成本配对效应及内部删点敏感性。原版只分析指标间相关，本版补充指标与推荐R的描述关系。\n\n[推荐方法及适用范围](年度指标与推荐容载比说明.md)说明从年度案例到工程分类范围的归纳方式。三类已有多年度支持，两类只有一个案例，不发布单例区间。\n\n年度装机按用户确认的万千瓦统计，源荷比采用装机容量除以同范围用户最大用电负荷的定义。全县年度装机与分电压、29站范围尚未完全对齐，标准源荷比列暂不填确定值，不能把原出力代理比改名代入。完整五指标推荐仍待该口径闭合。\n\n旧版和旧冻结清单保存在历史归档，替换与重新封存记录见'+os.path.relpath(AUDIT/'推荐矩阵更新记录.md',MATRIX)+'。\n')
    p=audit_docs[0];text=p.read_text()
    text=text.replace('分县月度光伏表未注明绝对单位，仅允许使用同月相对比例。','原冻结场景只使用分县月度光伏同月相对比例，计算保持不变。用户于2026-09-27确认该表按万千瓦统计，本次补充年度容量分析据此换算；与2026年MW装机快照的量级校核支持这一单位。')
    text+='\n\n## 推荐矩阵补充审查\n\n按用户授权，年度案例展示已补充为工程条件分层的研究范围，设备与经济结果保持原值。标准源荷比采用装机容量除以同供电范围用户最大用电负荷；原出力与毛负荷代理比只保留为仿真辅助量。当前年度装机已经找到，单位已经确认，仍需闭合电压层级、29站供电范围及用户峰值口径。完整五指标矩阵未因此自动放行。详见《推荐矩阵更新记录》及研究推荐目录。\n';p.write_text(text)
    p=audit_docs[1];text=p.read_text()
    text=text.replace('### F13 历史反向及源荷代理比','### F13 历史反向及光伏出力与毛负荷代理比')
    text=text.replace('非同时源荷出力代理比','非同时光伏出力与毛负荷代理比')
    text=text.replace('| 源荷指标 | 非同时光伏出力与毛负荷代理比 | 不称装机/负荷峰值比 |',
                      '| 仿真辅助量 | 非同时光伏出力与毛负荷代理比 | 不称源荷比、装机渗透率或同步区域功率比 |\n| 源荷比 | 分布式电源装机渗透率 | 已并网装机容量除以同范围用户最大用电负荷；范围未闭合时不填确定值 |')
    text+='\n\n## 源荷比与五类指标补充依据\n\n源荷比的装机口径依据本地2025年4月《配电网规划设计技术导则（修订稿）》3.1.18与6.5.4。DL/T 2041-2025未定义这一指标，不能混用条号。原F13是仿真辅助量，补充研究采用的标准源荷比表达为：\n\n\\[\\eta_{\\mathrm{DG},y}=C_{\\mathrm{DG},y}/P_{\\mathrm{L},\\max,y}.\\]\n\nLaTeX：`\\eta_{\\mathrm{DG},y}=C_{\\mathrm{DG},y}/P_{\\mathrm{L},\\max,y}`。其中，年度\\(y\\)无量纲；\\(C_{\\mathrm{DG},y}\\)为同范围已并网分布式电源装机容量，单位MW；\\(P_{\\mathrm{L},\\max,y}\\)为同范围用户最大用电负荷，单位MW；\\(\\eta_{\\mathrm{DG},y}\\)无量纲，可乘100%表示。不是只替换F13名称，分子与分母都需要重新核对。\n\n五类指标的公式、变量、单位、参数范围及来源依据见[补充审查](../01研究推荐/指标定义与口径补充审查.md)。本次新增的指标与推荐R相关系数和案例包络属于研究统计，不是导则给出的容载比阈值。\n';p.write_text(text)
    p=audit_docs[2];p.write_text(p.read_text()+'\n\n## 经授权的推荐展示更新\n\n用户确认年度装机统计单位为万千瓦，并授权直接替换原版推荐展示。新矩阵补充工程分类、指标与R关联和成本配对效应。原始Excel、模型代码、所有CSV求解结果和18395条原数据登记值未修改。旧版与旧哈希清单已经归档，当前清单更新的是展示文件和审查说明，不表示重新计算或调整模型。标准源荷比的同范围用户峰值与装机归属仍未闭合，完整五指标推荐不放行。详见《推荐矩阵更新记录》。\n')
    p=audit_docs[3];p.write_text(p.read_text()+'\n\n## 推荐输入补充更新\n\n按用户2026-09-27确认，年度装机以万千瓦统计，原版推荐矩阵及说明已经替换。新增24条区域年度装机统计、48条历史地区与电压层级对照、指标与R的描述关联及五类工程条件展示。三类给出多年度案例最优值的研究范围，两类只列点值。它们属于补充研究底稿，标准源荷轴仍缺同边界数据，不将该矩阵表述为完整五维推荐。原求解数值和原准入登记没有变动。当前封存记录与旧版归档见[推荐矩阵更新记录](推荐矩阵更新记录.md)。\n')
    # 原409文件清单与491快照只更新三份展示文件，保留旧清单在归档中。
    replaced_keys={str(p.relative_to(ROOT)) for p in presentation}
    m=json.loads(manifests[0].read_text())
    for r in m['files']:
        if r['path'] in replaced_keys:
            r['previous_sha256']=r['sha256'];r['sha256']=sha(ROOT/r['path']);r['bytes']=(ROOT/r['path']).stat().st_size
    m['presentation_update']={'date':'2026-09-27','authorization':'用户：可以直接替换原版；年度容量按万千瓦统计和计算',
       'model_numeric_outputs_unchanged':True,'replacement_paths':sorted(replaced_keys),'previous_version_archive':str(ARCHIVE.relative_to(ROOT))}
    dump(manifests[0],m)
    snapshot=json.loads(manifests[1].read_text())
    for r in snapshot:
        if r['path'] in replaced_keys:
            r['previous_sha256']=r['sha256'];r['sha256']=sha(ROOT/r['path']);r['size']=(ROOT/r['path']).stat().st_size
            r['update_scope']='用户授权更新推荐展示；原始数据及求解结果不变'
    dump(manifests[1],snapshot)
    # 对所有旧登记文件逐项比较，只允许上述文档和登记清单改变。
    allowed={str(p.relative_to(ROOT)) for p in presentation+audit_docs+manifests}
    changed=[r['path'] for r in old['files'] if sha(ROOT/r['path'])!=r['sha256']]
    assert set(changed)<=allowed,changed
    protected=[r for r in old['files'] if r['path'] not in allowed]
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in protected)
    # 复用原核查方法；新的执行记录写到补充目录，不覆盖旧执行证据。
    sys.path.insert(0,str(ROOT/'实验/研究'))
    check=module('replacement_independent',AUDIT/'审计工具/独立核查.py').run()
    assert check['status']=='PASS',check['problems'];dump(NEW/'原模型与数据复核.json',check)
    delivery=module('replacement_delivery',AUDIT/'审计工具/核验交付.py')
    delivery.dump=lambda p,x:dump(NEW/'阶段0兼容性核验.json',x)
    delivery.main()
    from rebuild_2026.verify_frozen_v4 import verify
    numerical=verify();assert numerical['status']=='PASS'
    # 补充结果阅核：检查源荷空值、区间支持、成本对照与归档，不把缺项登记成通过。
    evidence={'status':'PASS','authorization':'可以直接替换原版；可以按照万千瓦单位做统计和计算',
       'archive':str(ARCHIVE.relative_to(ROOT)),'archive_sha256':sha(ARCHIVE),
       'archived_files':[{'path':str(p.relative_to(ROOT)),'old_sha256':next(r['sha256'] for r in old['files'] if r['path']==str(p.relative_to(ROOT)))} for p in archived if str(p.relative_to(ROOT)) in {r['path'] for r in old['files']}],
       'changed_old_registered_paths':changed,'protected_old_file_count':len(protected),
       'model_code_raw_inputs_and_csv_results_unchanged':True,'original_data_records_unchanged':18395,
       'model_checks':{'frozen_v4':numerical,'independent_checks':check['checks']},
       'complete_five_indicator_recommendation_status':'待同供电范围年度装机及用户最大用电负荷，不放行',
       'humanizer_review':'已逐篇核对：删除模板化判断，区分标准条款、研究定义及代理量；结论与样本支持对应'}
    dump(NEW/'原版替换与校验记录.json',evidence)
    update_note=AUDIT/'推荐矩阵更新记录.md'
    update_note.write_text('# 推荐矩阵更新记录\n\n本次更新依据用户确认的两项指令：直接替换原版推荐成果；年度装机按万千瓦进行统计和计算。更新前原版及旧冻结清单已经归档，原始数据、模型代码和CSV求解结果逐文件核对保持一致，18395条原登记数据未改写。\n\n现行入口为[研究型推荐矩阵](../01研究推荐/研究型推荐矩阵.xlsx)、[研究型推荐方案](../01研究推荐/研究型推荐方案.md)和[指标口径补充审查](../01研究推荐/指标定义与口径补充审查.md)。原实验目录中的同名推荐矩阵及说明同步替换。\n\n新矩阵用工程条件分层、增长分档和既有成本最优路径的年度R包络归纳研究范围，并补充指标与推荐R的描述关联。价格变化采用同条件配对，单例只列点值。源荷比采用装机与同范围用户最大用电负荷的定义，原出力代理比只作辅助量。完整五指标矩阵尚缺装机归属和用户峰值的范围闭合，不列不存在的数据。\n\n年度容量数据已找到24条原值，单位已经由用户确认；2026年MW快照与月度表的邳州量级差约0.215%。48条历史配置对照用于背景关联，不当作经济最优标签。\n\n本次复核未重求模型。原409文件登记通过，独立源表、约束与现金流核查'+str(check['checks'])+'项通过；阶段0交付来源、字典、JSON和PDF兼容核验通过。旧冻结是替换前版本，新清单登记当前展示文件；两个版本的差异和归档校验值见[替换记录](../01研究推荐/原版替换与校验记录.json)。\n\n旧版归档：[推荐矩阵替换前版本](../../历史归档/推荐矩阵替换前-2026-09-27.zip)。本次不生成正式Word或研究报告正文。\n')
    # 扩展阶段0清单；旧证据继续保留，新研究缺口继续明示。
    paths={ROOT/r['path'] for r in old['files']}
    paths.update(p for p in NEW.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.update([ARCHIVE,update_note])
    updated=dict(old);updated['version']='stage0_local_v4_with_research_matrix_2026-09-27'
    updated['files']=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)]
    updated['presentation_update_record']=str((NEW/'原版替换与校验记录.json').relative_to(ROOT))
    updated['source_unit_confirmation']='分县月度分布式光伏容量：万千瓦；用户2026-09-27确认'
    updated['complete_five_indicator_recommendation']='未完成同供电范围源荷轴，不放行最终推荐矩阵'
    updated['unresolved_items']=list(old['unresolved_items'])+['标准源荷比须闭合同年、同电压或同用户供电范围的装机容量与用户最大负荷']
    dump(E/'阶段0冻结清单.json',updated)
    digest=sha(E/'阶段0冻结清单.json');count=len(updated['files'])
    (E/'阶段0冻结说明.md').write_text('# 阶段0冻结说明\n\n当前清单登记'+str(count)+'个文件。模型和原CSV结果仍为本地v4；用户授权更新的推荐矩阵、公式与术语说明及补充分析纳入当前封存。旧版588文件清单及旧推荐成果已归档，不能继续用旧清单哈希核对更新后文件。\n\n当前清单SHA256：\n\n```text\n'+digest+'\n```\n\n运行`审计工具/核验冻结.py`可只读核对当前文件。清单自身及本说明不纳入循环哈希。新增研究矩阵的源荷轴仍缺同供电范围数据，文件一致不等于完整五维推荐已经放行。\n\n原值与展示更新范围详见《推荐矩阵更新记录》。复算补充分析时必须指定新的输出目录，不能覆盖封存成果。\n')
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in updated['files'])
    print(json.dumps({'status':'PASS','replaced_presentations':3,'protected_old_files':len(protected),
        'registered_files':count,'manifest_sha256':digest,'five_indicator_matrix_complete':False},ensure_ascii=False))

if __name__=='__main__':main()
