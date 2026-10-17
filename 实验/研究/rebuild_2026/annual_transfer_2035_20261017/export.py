"""逐年方案、逐站措施、切换预案与便携技术报告。"""
import csv
import json
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from . import model as m, prepare as p
from .verify import CASES

LABEL={'rigid':'刚性','elastic_reserve':'弹性工程优选'}


def fixed(value):
    clean=Decimal(str(value)).quantize(Decimal('0.000000001'),rounding=ROUND_HALF_UP)
    return format(clean.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP),'.2f')
FIELDS={'year':'年份','peak_mw':'规划峰值_MW','capacity_mva':'年末容量_MVA','clr':'容载比','common_floor':'共同下限',
    'purchased_transformer_mva':'当年新购主变_MVA','net_capacity_increment_mva':'当年净增容量_MVA','replaced_capacity_mva':'当年替换原容量_MVA',
    'new_third_count':'当年新增第三台_台','storage_nameplate_mw':'年末储能功率_MW','storage_mwh':'年末储能_MWh',
    'new_storage_mwh':'当年新增储能_MWh','new_lines':'当年新增联络_条','cumulative_lines':'年末累计新增联络_条',
    'transformer_capex_10k':'当年主变投资_万元','storage_capex_10k':'当年储能投资_万元','line_capex_10k':'当年联络投资_万元',
    'construction_capex_10k':'当年工程投资_万元','added_lifecycle_npv_10k':'当年工程费用现值_万元',
    'cumulative_lifecycle_npv_10k':'累计费用现值_万元','transformer_npv_10k':'当年主变费用现值_万元',
    'storage_npv_10k':'当年储能费用现值_万元','line_npv_10k':'当年联络费用现值_万元'}


def rows(path):
    return list(csv.DictReader(path.open(encoding='utf-8-sig')))


def markdown(headers,data):
    return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+
        ['|'+'|'.join(str(v) for v in row)+'|' for row in data])


def add_sheet(book,name,data):
    ws=book.create_sheet(name);columns=list(data[0]);ws.append(columns)
    for r in data:ws.append([float(Decimal(str(r[k])).quantize(Decimal('0.000000001'),rounding=ROUND_HALF_UP))
                              if isinstance(r.get(k),float) else r.get(k) for k in columns])
    ws.freeze_panes='C2';ws.auto_filter.ref=ws.dimensions
    for cell in ws[1]:
        cell.font=Font(name='方正仿宋_GBK',bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='244B70')
        cell.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
    ws.row_dimensions[1].height=42
    for i,row in enumerate(ws.iter_rows(min_row=2),2):
        for cell in row:
            cell.font=Font(name='方正仿宋_GBK',size=10)
            cell.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
            if isinstance(cell.value,float):cell.number_format='0.00%' if '增量率' in columns[cell.column-1] else '0.00'
            if i%2==0:cell.fill=PatternFill('solid',fgColor='F2F5F8')
    for j,col in enumerate(columns,1):ws.column_dimensions[get_column_letter(j)].width=min(32,max(13,len(col)*1.4))
    return ws


def main():
    proof=json.loads((p.REVIEW/'逐年方案独立核验.json').read_text());assert proof['verified']
    all_years=[];differences=[];stations=[];projects=[];switching=[];review=[];plans={};forecasts=[];baseline_checks=[];reserve_changes=[]
    for region,name in p.REGIONS.items():
        inp,powers=p.load(region);aa=m.arcs(inp)
        ff={'region':'地区','year':'年份','forecast_load_mw':'预测总负荷_MW','pv_index':'全市光伏装机指数',
            'load_factor':'负荷相对2025倍数','pv_factor':'光伏相对2025倍数','load_yoy':'负荷同比增量率',
            'pv_yoy':'光伏同比增量率','load_interpolated':'负荷为插值','pv_interpolated':'光伏为插值'}
        forecasts.extend({ff[k]:v for k,v in row.items()} for row in p.forecasts(region))
        for case in CASES:
            root=p.RAW/region/case;s=json.loads((root/'summary.json').read_text());plans[region,case]=s
            if case=='rigid':
                baseline=json.loads((root/'baseline_check.json').read_text())
                baseline_checks.extend(dict(地区=name,年份=2021,方式='固定原供区零切换检验',故障站=r['failed'],
                    检验小时数=r['checked_hours'],约束不满足小时数=r['violating_hours'],最大约束缺口_MW=r['max_deficit_mw']) for r in baseline['records'])
            all_years.extend(dict(地区=name,方案=LABEL[case],**{FIELDS[k]:v for k,v in r.items()}) for r in s['annual'])
            old={sid:dict(unit_1_mva=v['initial_units'][0],unit_2_mva=v['initial_units'][1],unit_3_mva=0.,storage_modules=0)
                 for sid,v in inp['stations'].items()}
            for r in rows(root/'stations.csv'):
                y=int(r['year']);sid=r['station'];u=[float(r[f'unit_{i}_mva']) for i in (1,2,3)];before=old[sid]
                n=int(r['storage_modules']);newp=sum(u[j] for j in (0,1) if u[j]>float(before[f'unit_{j+1}_mva'])+1e-6)+u[2]-float(before['unit_3_mva'])
                stations.append(dict(地区=name,方案=LABEL[case],年份=y,变电站=sid,主变1_MVA=u[0],主变2_MVA=u[1],主变3_MVA=u[2],
                    年末容量_MVA=sum(u),当年新购主变_MVA=newp,当年净增容量_MVA=sum(u)-sum(float(before[f'unit_{i}_mva']) for i in (1,2,3)),
                    年末储能柜数=n,年末储能_MWh=n*.215,当年新增储能_MWh=(n-int(before['storage_modules']))*.215))
                old[sid]=r
            emap={e['id']:e for e in inp['network']['edges']}
            for r in rows(root/'projects.csv'):
                e=emap[r['id']];projects.append(dict(地区=name,方案=LABEL[case],投运年=int(r['year']),联络编号=r['id'],
                    站1=e['station_a'],站2=e['station_b'],馈线端1=e['a'],馈线端2=e['b'],容量_MW=e['capacity_mw'],依据=e['basis']))
            for y in inp['years']:
                r=json.loads((root/str(y)/'adopted.json').read_text());ref=json.loads((root/str(y)/'economic_reference.json').read_text())
                if case=='elastic_reserve':
                    parent=json.loads((p.RAW/region/'elastic_balanced'/str(y)/'adopted.json').read_text())
                    reserve_changes.append(dict(地区=name,年份=y,配套优选原容量_MVA=parent['annual']['capacity_mva'],
                        追加备用后容量_MVA=r['annual']['capacity_mva'],累计增加备用容量_MVA=r['annual']['capacity_mva']-parent['annual']['capacity_mva'],
                        当年提高采购额定容量_MVA=r['selection']['capacity_selection']['extra_capacity_mva'],
                        当年追加费用现值_万元=r['annual']['added_lifecycle_npv_10k']-parent['annual']['added_lifecycle_npv_10k'],
                        当年采用费用现值_万元=r['annual']['added_lifecycle_npv_10k'],当年可行参考费用现值_万元=r['economic_reference']['objective'],
                        相对参考增量率=r['selection']['premium'],储能_MWh=r['annual']['storage_mwh'],联络_条=r['annual']['cumulative_lines']))
                for item in r['check']['records']:
                    review.append(dict(地区=name,方案=LABEL[case],年份=y,故障站=item['failed'],校核小时数=item['checked_hours'],
                        失败小时数=item['violating_hours'],最大约束缺口_MW=item['max_deficit_mw'],最小安全余量_MW=item['minimum_margin_mw']))
                allocated={sid:0 for sid in inp['stations']}
                for field,mode in [('normal','正常固定'),('extra','事故追加')]:
                    for key,count in sorted(r[field].items(),key=lambda kv:int(kv[0])):
                        a=aa[int(key)];sid=a['source'];first=allocated[sid]+1;allocated[sid]+=count
                        switching.append(dict(地区=name,方案=LABEL[case],年份=y,方式=mode,事故站=sid if field=='extra' else '',
                            原属站=sid,接收站=a['target'],路径=a['id'],源馈线组=a['a'],受端馈线=a['b'],
                            区段起号=first,区段止号=allocated[sid],区段数=count,本站总区段数=inp['block_count'][sid],
                            同转源荷比例=count/inp['block_count'][sid],
                            净功率峰值上界_MW=float(abs(powers[y][:,a['sa']]).max()*count/inp['block_count'][sid]),
                            路径性质='既有事故能力代理' if a['existing'] else '新增付费候选'))
                assert all(count<=inp['block_count'][sid] for sid,count in allocated.items())
        rigid,elastic=plans[region,'rigid']['annual'],plans[region,'elastic_reserve']['annual']
        for a,b in zip(rigid,elastic):
            assert a['year']==b['year'] and a['common_floor']==b['common_floor'] and a['peak_mw']==b['peak_mw']
            differences.append(dict(地区=name,年份=a['year'],规划峰值_MW=a['peak_mw'],共同下限=a['common_floor'],
                刚性容量_MVA=a['capacity_mva'],弹性容量_MVA=b['capacity_mva'],容量差_弹减刚_MVA=b['capacity_mva']-a['capacity_mva'],
                刚性容载比=a['clr'],弹性容载比=b['clr'],容载比差_弹减刚=b['clr']-a['clr'],
                刚性储能_MWh=a['storage_mwh'],弹性储能_MWh=b['storage_mwh'],储能差_弹减刚_MWh=b['storage_mwh']-a['storage_mwh'],
                刚性累计联络_条=a['cumulative_lines'],弹性累计联络_条=b['cumulative_lines'],联络差_弹减刚_条=b['cumulative_lines']-a['cumulative_lines'],
                刚性累计费用现值_万元=a['cumulative_lifecycle_npv_10k'],弹性累计费用现值_万元=b['cumulative_lifecycle_npv_10k'],
                费用差_弹减刚_万元=b['cumulative_lifecycle_npv_10k']-a['cumulative_lifecycle_npv_10k']))
    assumptions=[dict(项目=k,说明=v) for k,v in [
        ('起点与覆盖','2021地区总容量保留原表：市区3113.50MVA、邳州2027.00MVA；逐站设备组合按归档2025容量比例标定。2021固定，2022起补强。'),
        ('源荷预测','2021—2025原年度峰值及同期净负荷模板；2026—2035负荷与光伏分别按新预测相对2025倍数外推，缺年等增量插值。光伏只取比例。'),
        ('容载比','年末110kV主变铭牌容量/同口径年度规划峰值。未来峰值由原110kV统计峰值乘负荷增长倍数，非全市总负荷直接替换。'),
        ('下限与控制','同地区同年度下限一致，按相应五年期增长率分档；刚性新增容量受2.0控制并保留既有容量，弹性取消新增容量上限。'),
        ('正常供区','年内固定正常供区，已有统计转供通道不用于正常优化；新增付费联络可形成固定供区调整。'),
        ('事故切换','保留正常供区方案，仅允许故障站原属区段向直接相邻站追加转供；全年同一事故预案，健康站不连锁重排。'),
        ('区段与接线组','同站负荷与光伏按同一比例整区段移动，分段全期不变。采用不超过2MW的保守代理区段；每个代理馈线组最多5段、3个受端馈线、2座邻站。'),
        ('标准与假设','依据2025年4月修订稿9.2.1.1—9.2.1.2设置组、段和余量边界；统一2MW、固定预案及正常既有禁用为保守研究设定，电缆网不冒称受架空2MW强制条款约束。'),
        ('共享资源','源端区段总量、既有J列上界、同一路径容量、受端馈线余量及主变余量共同限制；共享资源同时占用。'),
        ('储能','0.10MW/0.215MWh整柜，按min(额定功率,额定电量×0.76/持续时间)计算有效支撑；市区正向6h、邳州2h。逐小时静态校核不含连续SOC调度。'),
        ('工程优选','固定上年已采用资产，本年度费用基准5%以内，先使储能与联络均不高于自身费用参考，随后在剩余包络内优选已采购主变额定容量并逐年保持；未施加刚弹排序约束。'),
        ('费用','新购容量为替换及扩建采购铭牌容量之和，净增容量再扣被替换容量；费用以2021为现值基年、评价至2041，寿命40/40/25年，维护4.2%/2.2%/3%，折现6%。'),
        ('数据适用性','候选连接及等比例源荷区段含研究代理，2025线路收资用于结构和能力上界，早期年份并非竣工网络复原；已有缺测补值标识保留。'),
    ]]
    frames={'逐年对比':differences,'逐年措施明细':all_years,'逐站逐年配置':stations,'联络逐项工程':projects,
        '固定区段切换预案':switching,'备用容量优选影响':reserve_changes,'全年安全核验':review,'2021固定基线检验':baseline_checks,'预测增长率':forecasts,'定义与假设':assumptions}
    book=Workbook();book.remove(book.active)
    for name,data in frames.items():
        p.write_csv(p.PUBLIC/(name+'.csv'),data);add_sheet(book,name,data)
    wbpath=p.PUBLIC/'两区县2021至2035逐年方案.xlsx';book.save(wbpath)
    readback=load_workbook(wbpath,data_only=True);cells=0
    for name,data in frames.items():
        actual=list(readback[name].values);expected=[list(data[0])]+[[r.get(k) for k in data[0]] for r in data]
        assert len(actual)==len(expected)
        for a,b in zip(actual,expected):
            for x,v in zip(a,b):
                if isinstance(v,float):assert abs(x-v)<max(1e-8,abs(v)*1e-12),(name,x,v)
                else:assert ('' if x is None else x)==('' if v is None else v),(name,x,v)
                cells+=1
    readback.close();p.dump(p.REVIEW/'工作簿回读.json',dict(verified=True,cells=cells,path=str(wbpath.relative_to(p.ROOT)),sha256=p.sha(wbpath)))
    build_report(plans,differences,all_years,proof,assumptions)
    print('EXPORTED_ANNUAL',cells,len(switching),flush=True)


def build_report(plans,differences,all_years,proof,assumptions):
    title='两区县2021—2035逐年规划与转供约束影响'
    summaries=[];findings={};counterexamples=[]
    for region,name in p.REGIONS.items():
        rs=plans[region,'rigid'];es=plans[region,'elastic_reserve'];r,e=rs['annual'][-1],es['annual'][-1]
        summaries.append(f'{name}2035年：弹性容量{e["capacity_mva"]:.2f} MVA、容载比{e["clr"]:.2f}，刚性分别为{r["capacity_mva"]:.2f} MVA、{r["clr"]:.2f}；储能{fixed(r["storage_mwh"])}→{fixed(e["storage_mwh"])} MWh，累计新增联络{r["cumulative_lines"]}→{e["cumulative_lines"]}条。')
        points=[a for a in differences if a['地区']==name and a['年份']>2021]
        exceptions=[a['年份'] for a in points if a['容量差_弹减刚_MVA']<-1e-6 or a['储能差_弹减刚_MWh']>1e-6 or a['联络差_弹减刚_条']>0]
        if exceptions:counterexamples.append(f'{name}在{join_years(exceptions)}年出现至少一项排序例外。')
        nodes=[a['year'] for a in es['annual'][1:] if a['net_capacity_increment_mva']>1e-7]
        rigid_nodes=[a['year'] for a in rs['annual'][1:] if a['net_capacity_increment_mva']>1e-7]
        lower_cost=(rs['cost_npv_10k']-es['cost_npv_10k'])/rs['cost_npv_10k']
        delta={k:sum(a[k+'_npv_10k'] for a in es['annual'])-sum(a[k+'_npv_10k'] for a in rs['annual'])
               for k in ('transformer','storage','line')}
        findings[region]=(f'弹性增容年份为{join_years(nodes)}，刚性为{join_years(rigid_nodes)}。'
            + ('市区早期地区容量超过刚性新增控制范围，弹性在2022年提前增容，减少了对新增联络的依赖。'
               if region=='city' else '邳州初期地区容量较充足，弹性针对局部约束先作少量增容；2031年后光伏反向承载压力加大，两方案储能均继续增加。')+
            f'至2035年，弹性相对刚性净多容量{e["capacity_mva"]-r["capacity_mva"]:.2f} MVA，'
            f'储能差{fixed(e["storage_mwh"]-r["storage_mwh"])} MWh，联络差{e["cumulative_lines"]-r["cumulative_lines"]:+d}条。'
            f'全期新增工程费用现值为刚性{rs["cost_npv_10k"]:.2f}万元、弹性{es["cost_npv_10k"]:.2f}万元，弹性相对变化{-lower_cost:.2%}。'
            f'费用差额（弹减刚）由主变{delta["transformer"]:+.2f}万元、储能{delta["storage"]:+.2f}万元和联络{delta["line"]:+.2f}万元共同构成。')
    # 各段的表与图共享已回读的原始结果，HTML只在此生成一次规范载荷。
    summary='\n\n'.join(summaries)
    definitions='2021为固定设备起点，2022—2035逐年决定新增工程并承接上年资产。容载比为年末主变铭牌容量除以同口径年度规划峰值。储能表示年末额定电量，联络表示自2022年起累计新增条数；当年新增与年末累计在明细中分别列示。新购主变容量包含替换采购，净增容量扣除被替换容量。'
    limits=('本次为现有资料下的代理区段规划。候选接线并未全部闭合到真实线路，负荷与光伏按站内等比例划分。'
        '2021地区容量来自原表，逐站双主变组合为比例标定，早期净负荷沿用2025空间模板按年度统计峰值缩放。'
        '2021固定基线的零切换缺口单列，2022年起补强后逐小时通过。'
        '全年检查使用补齐的8760小时序列，原缺测标识保留；储能按持续时间折算静态支撑，尚不包含连续SOC运行。'
        '费用按具体可行配置回算，年度参考与界限记录保留，当前方案未证明为全期联合全局最优。')
    method=('两方案同地区同年度使用相同下限、源荷、区段及供电安全条件。刚性保持既有容量，新增容量受容载比2.0控制；弹性取消该新增控制。'
        '既有统计转供能力仅用于事故，新增付费联络可形成固定正常供区。事故保留正常方案，只追加切换故障站原属区段，不通过健康站连锁腾容量。'
        '区段负荷与光伏共同切换，正常及各站事故预案在年内共用。路径热限、共享馈线余量、既有转供总量和接收主变能力同时约束。'
        '参考2025年4月《配电网规划设计技术导则（修订稿）》的接线组、分段和余量要求，采用全期不超过2MW的保守代理区段，以及每代理馈线组最多5段、3个受端馈线、2座邻站。'
        '统一2MW及固定切换预案是研究设定，电缆网适用范围单独说明。'
        '弹性在每年经济参考费用5%以内，要求储能与联络均不高于自身费用参考，先等权压低两项相对规模，再用剩余费用包络提高当年已采购主变规格并在后年保持。同容量增量优先提高N-1剩余容量。费用基准由原费用参考配置在新增备用容量后的既有设备上固定复核，不重新称为费用最优。该5%按当年工程费用现值计算。')
    validation=f'4套方案均包含2021—2035共15个年度。2022—2035合计完成{proof["full_hour_pairs"]:,}个小时—工况组合的独立校核，主模型最大约束误差{proof["max_matrix_error"]:.2e}，费用重算最大差额{proof["max_cost_error_10k"]:.2e}万元。每年的正常接线及事故预案共同覆盖全年。'
    md=['# '+title,'','## 主要结果','',summary,'','## 比较口径','',definitions]
    for region,name in p.REGIONS.items():
        md.extend(['','## '+name+'逐年变化','',findings[region],'',markdown(
            ['年份','峰值/MW','刚性容量/MVA','弹性容量/MVA','刚性容载比','弹性容载比','刚性储能/MWh','弹性储能/MWh','刚性联络/条','弹性联络/条'],
            [[a['年份'],f'{a["规划峰值_MW"]:.2f}',f'{a["刚性容量_MVA"]:.2f}',f'{a["弹性容量_MVA"]:.2f}',
              f'{a["刚性容载比"]:.2f}',f'{a["弹性容载比"]:.2f}',fixed(a['刚性储能_MWh']),fixed(a['弹性储能_MWh']),
              a['刚性累计联络_条'],a['弹性累计联络_条']] for a in differences if a['地区']==name])])
    md.extend(['','## 转供和工程选择','',method,'','## 核验与适用范围','',validation,'',limits])
    if counterexamples:md.extend(['','排序例外：'+' '.join(counterexamples)])
    else:md.extend(['','2022—2035各年度弹性容量不低于刚性，储能与累计联络不高于刚性；相等年份照实保留。'])
    md.extend(['','## 工程判断','',
        '先比较容量控制首次起作用的年份，再核对增容是否替代了当年的储能或联络，并检查此前已投运设施的保留影响。'
        '用于工程立项前，应优先核实本方案实际采用的区段与接收路径，再以真实源荷曲线校核持续运行；路径核实结果会改变具体条数与费用。'])
    (p.PUBLIC/'逐年变化与影响说明.md').write_text('\n'.join(md))
    source=dict(id='annual_plan',label='两区县逐年规划原始解及独立核验',path='研究报告/试算/20261017_区段转供逐年2035',
        query=dict(engine='Python/HiGHS',language='python',description='固定上年设备的逐年优化；整区段源荷绑定；全年静态供区矩阵复核',
            tables_used=['city/rigid/summary.json','city/elastic_reserve/summary.json','pizhou/rigid/summary.json','pizhou/elastic_reserve/summary.json'],
            metric_definitions=dict(clr='年末主变容量/年度规划峰值',storage='年末额定储能MWh',ties='2022起累计新增10kV联络条数',cost='2021基年、评价至2041的新增工程现值')))
    manifest=dict(version=1,surface='report',title=title,generatedAt=datetime.now(timezone.utc).isoformat(),
                  sources=[source],blocks=[],charts=[],tables=[],cards=[])
    datasets={};blocks=manifest['blocks']
    def textblock(id,body,sourced=False):
        block=dict(id=id,type='markdown',body=body)
        if sourced:block['sourceId']='annual_plan'
        blocks.append(block)
    textblock('title','# '+title);textblock('summary','## 主要结果\n\n'+summary,True)
    textblock('definitions','## 比较口径\n\n'+definitions)
    for region,name in p.REGIONS.items():
        textblock(region+'_finding','## '+name+'逐年变化\n\n'+findings[region],True)
        dataset=region+'_comparison';datasets[dataset]=[r for r in differences if r['地区']==name]
        cid=region+'_clr';manifest['charts'].append(dict(id=cid,title=name+'逐年容载比',subtitle='2021—2035年，两方案同年度规划峰值相同',
            type='line',dataset=dataset,sourceId='annual_plan',valueFormat='number',
            palette=dict(kind='categorical'),legend=dict(position='bottom'),settings=dict(showPoints='always'),
            series=[dict(field='刚性容载比',label='刚性',color='blue',lineStyle='solid'),
                    dict(field='弹性容载比',label='弹性工程优选',color='yellow',lineStyle='dashed')],
            encodings=dict(x=dict(field='年份',type='ordinal',label='年份'),y=dict(fields=['刚性容载比','弹性容载比'],type='quantitative',label='容载比'),
                tooltip=[dict(field=k,type='quantitative',label=k) for k in
                    ['刚性容量_MVA','弹性容量_MVA','规划峰值_MW','刚性储能_MWh','弹性储能_MWh']])))
        blocks.append(dict(id=cid+'_block',type='chart',chartId=cid))
        tid=region+'_detail';did=region+'_comparison';datasets[did]=[r for r in differences if r['地区']==name]
        columns=['年份','刚性容量_MVA','弹性容量_MVA','刚性容载比','弹性容载比','刚性储能_MWh','弹性储能_MWh','刚性累计联络_条','弹性累计联络_条']
        manifest['tables'].append(dict(id=tid,title=name+'逐年配置对比',dataset=did,sourceId='annual_plan',
            defaultSort=dict(field='年份',direction='asc'),columns=[dict(field=k,label=k,type='text') if k=='年份' else dict(field=k,label=k,type='number',format='number') for k in columns]))
        blocks.append(dict(id=tid+'_block',type='table',tableId=tid))
    textblock('resource_intro','## 末年配套设施\n\n储能按额定电量比较，联络按累计新增条数比较。两图分别使用各自单位；年内新增节点和历年累计值见逐年表。')
    datasets['terminal']=[r for r in differences if r['年份']==2035]
    for key,title2 in [('储能_MWh','2035年储能配置'),('累计联络_条','2035年累计新增联络')]:
        cid='terminal_storage' if key=='储能_MWh' else 'terminal_ties'
        manifest['charts'].append(dict(id=cid,title=title2,type='bar',dataset='terminal',sourceId='annual_plan',
            valueFormat='number',palette=dict(kind='categorical'),legend=dict(position='bottom'),settings=dict(groupMode='grouped'),
            series=[dict(field='刚性'+key,label='刚性',color='blue'),dict(field='弹性'+key,label='弹性工程优选',color='yellow')],
            encodings=dict(x=dict(field='地区',type='nominal',label='地区'),
                y=dict(fields=['刚性'+key,'弹性'+key],type='quantitative',label=key))))
        if key!='储能_MWh':textblock('ties_reading','联络图表示规划期内累计建设数量。既有资产没有计入新增条数，具体候选路径及投运年在工作簿中逐项列示。')
        blocks.append(dict(id=cid+'_block',type='chart',chartId=cid))
    textblock('method','## 转供与逐年工程选择\n\n'+method)
    textblock('validation','## 核验与适用范围\n\n'+validation+'\n\n'+limits,False)
    if counterexamples:textblock('exceptions','### 排序例外\n\n'+' '.join(counterexamples),True)
    textblock('action','## 工程判断\n\n'+md[-1])
    display={key:[{k:(str(v) if k=='年份' else float(fixed(v)) if isinstance(v,float) else v) for k,v in row.items()} for row in data]
             for key,data in datasets.items()}
    artifact=dict(surface='report',manifest=manifest,snapshot=dict(version=1,status='ready',datasets=display),sources=[source])
    p.dump(p.PUBLIC/'artifact.json',artifact)
    p.dump(p.SOURCE/'报告结构与图表口径.json',dict(delivery='portable HTML',audience='technical',
        question='固定区段及局部事故转供下，两地区2021—2035逐年刚弹方案如何变化',
        structure=['技术摘要','比较口径','两地区逐年结果及图表','末年配套设施','模型方法','验证与局限','工程判断'],
        specification_mapping='定义前置于图表；方法单列；局限与核验合并；下一步及路径资料缺口合并于工程判断',
        charts=[dict(id=c['id'],family=c['type'],question=c['title'],rows=len(datasets[c['dataset']]),
            temporal_points=15 if c['type']=='line' else None,palette_policy='hard two-root cap: blue/gold',
            distinction='方案图例及分组/折线位置；准确数值保留逐年表',fields=c['encodings']) for c in manifest['charts']],
        omitted_annual_storage_chart='逐年表用于查阅具体新增节点，另以末年分组柱状图概括配套设施差异，避免重复折线',
        assumptions=assumptions,counterexamples=counterexamples))


def join_years(values):
    return '、'.join(map(str,values)) if values else '无新增'


if __name__=='__main__':main()
