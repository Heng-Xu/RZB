"""只读用户锁定的2021—2035案例，生成本轮报告局部资产与核验依据。"""
from pathlib import Path
import hashlib
import json
import re
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from 实验.研究.rebuild_2026.annual_demand_driven_2035_20261017 import model, prepare
from 实验.研究.rebuild_2026.case_parameters_20261012 import transfer_diagnostic

REPORT = ROOT / '研究报告'
ASSET = REPORT / '02图表/当前版'
REVIEW = REPORT / '05_review/当前版/1017甲方批注与逐年案例更新'
SOURCE = REPORT / '数据来源/当前版/1017报告案例更新'
PUBLIC = REPORT / '01研究推荐/当前版/逐年需求驱动2035_20261017'
LABELS = {'刚性': 'rigid', '弹性': 'elastic_capacity'}


def f(value):
    from decimal import Decimal, ROUND_HALF_UP
    return str(Decimal(str(round(float(value), 9))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))


def table(title, headers, rows, note=''):
    text = title + '\n\n| ' + ' | '.join(headers) + ' |\n| ' + ' | '.join(['---'] * len(headers)) + ' |\n'
    text += ''.join('| ' + ' | '.join(str(x) for x in row) + ' |\n' for row in rows)
    return text + ('\n注：' + note + '\n' if note else '')


def load():
    names = {}
    for line in transfer_diagnostic.MAPPING.read_text().splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 3:
            names[parts[-1]] = re.sub(r'^(?:110千伏|110\s*kV)', '', parts[1])
    inputs, powers, plans, fixed = {}, {}, {}, {}
    for region in ['pizhou', 'city']:
        inputs[region], powers[region] = prepare.load(region)
        for label, code in LABELS.items():
            folder = prepare.RAW / region / code
            plans[region, label] = json.loads((folder / 'summary.json').read_text())
            fixed[region, label] = {year: json.loads((folder / str(year) / 'adopted.json').read_text()) for year in range(2022, 2036)}
    return names, inputs, powers, plans, fixed


def served(inp, power, record, failed=-1):
    """固定原始采用预案直接回代；不另行寻优转供。"""
    ids = list(inp['stations'])
    out = np.zeros_like(power)
    incoming = np.zeros_like(power)
    existing = np.zeros(power.shape[0])
    added = np.zeros(power.shape[0])
    arcs = model.arcs(inp)
    active = {int(k): v for k, v in record['normal'].items()}
    if failed >= 0:
        for key, count in record['extra'].items():
            key = int(key)
            if arcs[key]['sa'] == failed:
                active[key] = active.get(key, 0) + count
    for key, count in active.items():
        arc = arcs[key]
        q = power[:, arc['sa']] * count / inp['block_count'][ids[arc['sa']]]
        out[:, arc['sa']] += q
        incoming[:, arc['sb']] += q
        (existing if arc['existing'] else added)[:] += abs(q)
    return power - out + incoming, out, incoming, existing, added


def assets():
    names, inputs, powers, plans, fixed = load()
    tables, sections, evidence = {}, {}, []
    costs, measures, components, decomposition, mix, necessary = [], [], [], [], [], []
    loading, directions, rank = [], [], []
    for region, cn in [('pizhou', '邳州'), ('city', '市区')]:
        inp = inputs[region]
        ids = list(inp['stations'])
        show = [j for j, sid in enumerate(ids) if sid in names]
        initial = np.array([station['initial_units'] + [0.] for station in inp['stations'].values()])
        peak2025 = powers[region][2025]
        pp, pn = peak2025.max(axis=0), -peak2025.min(axis=0)
        rates = abs(peak2025).max(axis=0) / (.95 * initial.sum(axis=1))
        for year in range(2022, 2026):
            rate = abs(powers[region][year]).max(axis=0)[show] / (.95 * initial.sum(axis=1)[show])
            loading.append([cn, year, f(100 * np.median(rate)), f(100 * rate.max())])
        directions.append([cn, len(show), sum(pp[j] >= pn[j] for j in show), sum(pp[j] < pn[j] for j in show), sum(rates[j] > 1 for j in show)])
        for j in sorted(show, key=lambda j: -rates[j])[:8]:
            rank.append([cn, names[ids[j]], f(initial[j].sum()), f(pp[j]), f(max(0, pn[j])), f(100 * rates[j]) + '%', '正向' if pp[j] >= pn[j] else '反向'])
        years, construction, transfer = [], [], []
        normal_cache = {}
        for label in LABELS:
            annual = plans[region, label]['annual']
            costs.append([cn, label, f(plans[region, label]['cost_npv_10k'])])
            components.append([cn, label] + [f(sum(row[key] for row in annual)) for key in ['transformer_npv_10k', 'storage_npv_10k', 'line_npv_10k']] + [f(plans[region, label]['cost_npv_10k'])])
            last = annual[-1]
            measures.append([cn, label, f(last['capacity_mva']), f(sum(row['purchased_transformer_mva'] for row in annual)), f(last['storage_nameplate_mw']), f(last['storage_mwh']), last['cumulative_lines']])
            for previous, row in zip(annual, annual[1:]):
                cap_contribution = (row['capacity_mva'] - previous['capacity_mva']) / row['peak_mw']
                load_contribution = previous['capacity_mva'] * (1 / row['peak_mw'] - 1 / previous['peak_mw'])
                decomposition.append([cn, label, row['year'], f(cap_contribution), f(load_contribution), f(row['clr'] - previous['clr'])])
            for row in annual:
                year = row['year']
                years.append([label, year, f(row['peak_mw']), f(row['capacity_mva']), f(row['clr']), f(row['storage_nameplate_mw']), row['cumulative_lines']])
                construction.append([label, year, f(row['net_capacity_increment_mva']), f(row['purchased_transformer_mva']), row['new_third_count'], f(row['new_storage_mwh']), row['new_lines'], f(row['added_lifecycle_npv_10k'])])
                if year == 2021:
                    continue
                power, record = powers[region][year], fixed[region, label][year]
                normal = served(inp, power, record)
                normal_cache[label, year] = normal
                for hour, title in [(int(power.sum(axis=1).argmax()), '区域正向峰值'), (int(power.sum(axis=1).argmin()), '区域最低净负荷')]:
                    net, out, inc, existing, added = normal
                    transfer.append([label, year, title, int((abs(out[hour]) > 1e-7).sum()), int((abs(inc[hour]) > 1e-7).sum()), f(abs(out[hour]).sum()), f(existing[hour]), f(added[hour]), f(abs(out[hour]).max()), f(abs(inc[hour]).max())])
                fault_total = fault_existing = 0.
                for failed in range(len(ids)):
                    net, out, inc, existing, added = served(inp, power, record, failed)
                    fault_total = max(fault_total, float((existing + added).max()))
                    fault_existing = max(fault_existing, float(existing.max()))
                necessary.append([cn, label, year, f((normal[3] + normal[4]).max()), f(normal[3].max()), f(fault_total), f(fault_existing)])
            final_record = fixed[region, label][2035]
            units = np.array(final_record['units'])
            modules = np.array(final_record['modules'])
            thirds = sum(units[j, 2] > 0 for j in show)
            mix.append([cn, label, len(show), len(show) - thirds, thirds, f(100 * thirds / len(show)) + '%', sum(modules[j] > 0 for j in show), f(sum(modules[j] for j in show) * .1)])
        tables[f'new_{region}_years'] = table(f'表5-0 {cn}逐年容量及措施', ['方案', '年份', '年网供最大负荷/MW', '主变容量/MVA', '容载比', '储能额定功率/MW', '累计新线/条'], years,
            '2021年为两方案共同的固定基期，储能及新线列为本次规划新增设备的累计在役规模。')
        tables[f'restore_{region}_construction'] = table(f'表5-0 {cn}逐年新增工程与费用', ['方案', '年份', '主变净增容量/MVA', '主变新购容量/MVA', '扩建主变/台', '新增储能额定能量/MWh', '新增联络/条', '当年措施现值/万元'], construction)
        tables[f'restore_{region}_transfer'] = table(f'表5-0 {cn}正常方式下的分工况转接任务', ['方案', '年份', '工况', '转出站数', '承接站数', '转接合计/MW', '既有边/MW', '新增边/MW', '单站最大转出/MW', '单站最大承接/MW'], [r for r in transfer if r[1] in [2022, 2025, 2030, 2035]], '列示代表年度，转接合计为沿已采用区段预案转接的净功率幅值之和。')
        sections[f'restore_{region}_transfer'] = ''
        first = plans[region, '弹性']['annual'][1]
        last = plans[region, '弹性']['annual'][-1]
        sections[f'new_{region}_results'] = (f'{cn}两方案2021年均保留{f(initial.sum())} MVA实际地区容量，2022年起按当年源荷选择新增工程。'
            f'弹性方案2022年净增{f(first["net_capacity_increment_mva"])} MVA，至2035年主变容量为{f(last["capacity_mva"])} MVA。年末配置与当年新增措施分别列示。\n')
        profiles = []
        for j in show:
            sid, name = ids[j], names[ids[j]]
            profile_rows, actions, storage_actions = [], [], []
            previous_u, previous_n = initial[j], 0
            for year in range(2022, 2036):
                record = fixed[region, '弹性'][year]
                units = np.array(record['units'])[j]
                changes = [f'{f(previous_u[k])} MVA更换为{f(units[k])} MVA' for k in [0, 1] if units[k] > previous_u[k] + 1e-7]
                if units[2] > previous_u[2] + 1e-7:
                    changes.append(f'扩建第三台{f(units[2])} MVA主变')
                if changes:
                    actions.append(f'{year}年' + '、'.join(changes))
                n = record['modules'][j]
                if n > previous_n:
                    storage_actions.append(f'{year}年{f((n - previous_n) * .1)} MW')
                previous_u, previous_n = units, n
            for label in LABELS:
                for year in [2021, 2025, 2030, 2035]:
                    if year == 2021:
                        units, n, out, inc, net = initial[j], 0, 0., 0., None
                    else:
                        record = fixed[region, label][year]
                        units, n = np.array(record['units'])[j], record['modules'][j]
                        normal = normal_cache[label, year]
                        h = int(powers[region][year].sum(axis=1).argmax())
                        net, out, inc = normal[0][h, j], normal[1][h, j], normal[2][h, j]
                    profile_rows.append([label, year, '+'.join(f(x) for x in units if x > 0), f(units.sum()), f(n * .1), '—' if year == 2021 else f(out), '—' if year == 2021 else f(inc), '—' if net is None else f(net)])
            key = f'restore_{region}_{sid}_profile'
            tables[key] = table(f'表5-0 {name}代表年度配置与正向峰值正常转接', ['方案', '年份', '主变组合/MVA', '总容量/MVA', '储能额定功率/MW', '转出/MW', '承接/MW', '转接后净负荷/MW'], profile_rows)
            elastic = fixed[region, '弹性'][2035]
            rigid = fixed[region, '刚性'][2035]
            eu, ru = np.array(elastic['units'])[j], np.array(rigid['units'])[j]
            em, rm = elastic['modules'][j], rigid['modules'][j]
            power = powers[region][2035]
            net, out, inc, _, _ = served(inp, power, elastic, j)
            bp = min(.1, .215 * .76 / max(1, inp['stations'][sid]['forward_duration_h'])) * em
            bn = min(.1, .215 * .76 / max(1, inp['stations'][sid]['reverse_duration_h'])) * em
            remain = .95 * (eu.sum() - eu.max())
            margin = np.minimum(remain + bp - net[:, j], remain + bn + net[:, j])
            h = int(margin.argmin())
            route = ''
            if abs(out[h, j]) + abs(inc[h, j]) > 1e-7:
                route = f'该小时按采用的固定区段预案，本站转出{f(out[h, j])} MW、承接{f(inc[h, j])} MW，转接后净负荷为{f(net[h, j])} MW。'
            else:
                route = f'该小时本站未转接负荷，净负荷为{f(net[h, j])} MW。'
            network=[]
            for k,arc in enumerate(model.arcs(inp)):
                count=elastic['normal'].get(str(k),0)
                if arc['sa']==j:count+=elastic['extra'].get(str(k),0)
                if not count or j not in (arc['sa'],arc['sb']):continue
                q=power[h,arc['sa']]*count/inp['block_count'][arc['source']]
                if abs(q)>1e-7:network.append((abs(q),names.get(arc['target'] if arc['sa']==j else arc['source'],'相邻站'),arc['sa']==j,q,arc['existing']))
            if network:
                amount,neighbor,is_source,q,existing=max(network)
                route+=f'其中与{neighbor}之间的主要通道承担{f(amount)} MW净功率转接，使用'+('既有通道。' if existing else '已投运新增联络。')
            if eu[2]>0 and ru[2]==0:
                implication='本站弹性方案新增第三台主变，改变了故障后剩余设备组合，可与刚性方案的配储及转接任务对应比较。'
            elif eu[2]==0 and ru[2]>0:
                implication='刚性方案在本站采用第三台主变，弹性方案保留两台结构，容量与配储差异需结合可用通道及邻站支援判断。'
            elif em!=rm:
                implication=f'两方案本站储能额定功率相差{f(abs(em-rm)*.1)} MW，差额与所列主变组合及年度固定转接任务共同形成局部供电安排。'
            elif abs(eu.sum()-ru.sum())>1e-7:
                implication='两方案本站储能规模相同，主变规格的差异主要体现为站内容量及故障后可用能力的变化。'
            else:
                implication='两方案本站最终主变和储能规模相同，局部设备采用结果保持一致。'
            difference = ('两方案本站主变总容量相同。' if abs(eu.sum() - ru.sum()) < 1e-7 else
                f'弹性方案本站主变容量较刚性'+('增加' if eu.sum() > ru.sum() else '减少')+f'{f(abs(eu.sum() - ru.sum()))} MVA。')
            action_text = '；'.join(actions) + '。' if actions else '2022—2035年保留初始主变组合。'
            storage_text = ('储能按本地支撑需求分批增加，新增额定功率为' + '、'.join(storage_actions) + '。') if storage_actions else '本站弹性方案各年未新增储能。'
            paragraphs = [f'#### {name}规划分析',
                f'该站2021年主变组合为' + '+'.join(f(x) for x in initial[j] if x > 0) + ' MVA。弹性方案' + action_text + storage_text,
                f'2025年最大正向、反向净负荷分别为{f(pp[j])} MW、{f(max(0, pn[j]))} MW，2035年分别为{f(power[:, j].max())} MW、{f(max(0, -power[:, j].min()))} MW。2035年刚性方案主变容量{f(ru.sum())} MVA、储能额定功率{f(rm * .1)} MW，弹性方案分别为{f(eu.sum())} MVA和{f(em * .1)} MW。' + difference,
                f'[[TABLE:{key}]]',
                f'2035年最大单台主变N-1后，弹性方案剩余主变容量为{f(eu.sum() - eu.max())} MVA，按0.95功率因数折算为{f(remain)} MW。储能正向有效支撑功率为{f(bp)} MW、反向有效吸收功率为{f(bn)} MW。全年本站故障工况中最小余量为{f(max(0, margin.min()))} MW。' + route,
                implication]
            profiles.append('\n\n'.join(paragraphs))
            evidence.append({'地区':cn,'站名':name,'station':sid,'最小余量_MW':float(margin.min()),'2035主变_MVA':float(eu.sum()),'2035刚性主变_MVA':float(ru.sum()),'储能正向有效功率_MW':float(bp),'储能反向有效功率_MW':float(bn),'最紧小时':h,'转接后净负荷_MW':float(net[h,j])})
        sections[f'restore_{region}_profiles'] = '\n\n'.join(profiles) + '\n'
    assert len(evidence) == 46
    tables['new_cost_comparison'] = table('表5-0 两地区2022—2035年新增方案费用比较', ['地区', '方案', '评价期费用现值/万元'], costs)
    tables['new_case_measures'] = table('表5-0 2035年在役措施及累计建设规模', ['地区', '方案', '在役主变/MVA', '累计新购主变/MVA', '储能功率/MW', '储能能量/MWh', '新增联络/条'], measures)
    tables['restore_cost_components'] = table('表5-0 主变、储能及联络费用现值', ['地区', '方案', '主变/万元', '储能/万元', '联络/万元', '合计/万元'], components)
    tables['restore_clr_decomposition'] = table('表5-0 规划容载比年度变化分解', ['地区', '方案', '年份', '容量变化贡献', '负荷变化贡献', '容载比净变化'], [row for row in decomposition if row[2] in [2022, 2023, 2024, 2025, 2030, 2035]], '列示历史回算年度及2030、2035年相对上一年的比值变化。')
    tables['restore_equipment_mix'] = table('表5-0 2035年站级展示范围内主变台数与配储站数', ['地区', '方案', '站数', '两台主变站数', '三台主变站数', '三台主变站占比', '配储站数', '储能额定功率/MW'], mix)
    tables['new_annual_loading'] = table('表3-0 两地区站级负载率', ['地区', '年份', '中位数/%', '最大值/%'], loading)
    tables['restore_direction'] = table('表3-0 站级展示范围内的功率方向及相对压力', ['地区', '站数', '正向幅值较大站数', '反向幅值较大站数', '站级负载率超过100%的站数'], directions)
    tables['restore_station_loading_rank'] = table('表3-0 2025年站级负载率较高的站', ['地区', '变电站', '初始公用主变总容量/MVA', '最大正向净负荷/MW', '最大反向净负荷/MW', '站级负载率', '主导方向'], rank)
    tables['current_necessary_transfers'] = table('表5-0 代表年度固定区段预案的最大转接功率', ['地区', '方案', '年份', '正常总量/MW', '正常既有边/MW', 'N-1总量/MW', 'N-1既有边/MW'], [row for row in necessary if row[2] in [2022, 2025, 2030, 2035]], '沿采用的正常固定及事故追加预案回代8760小时，分别列出各列最大值。')
    tables['new_baseline'] = table('表5-0 两地区共同基期及规划年度', ['地区', '2021主变容量/MVA', '2021年网供最大负荷/MW', '2021容载比', '规划年度'], [[cn, f(plans[r,'刚性']['annual'][0]['capacity_mva']), f(plans[r,'刚性']['annual'][0]['peak_mw']), f(plans[r,'刚性']['annual'][0]['clr']), '2022—2035'] for r,cn in [('pizhou','邳州'),('city','市区')]])
    rigid = sum(plans[r, '刚性']['cost_npv_10k'] for r in inputs)
    elastic = sum(plans[r, '弹性']['cost_npv_10k'] for r in inputs)
    sections['new_case_comparison'] = f'两地区2022—2035年新增工程按共同2041年评价截止期折现，刚性方案费用现值合计{f(rigid)}万元，弹性为{f(elastic)}万元，减少{f(rigid-elastic)}万元，降幅{f(100*(1-elastic/rigid))}%。\n'
    texts = []
    for region, cn in [('pizhou','邳州'),('city','市区')]:
        delta = [sum(row[key] for row in plans[region,'弹性']['annual'])-sum(row[key] for row in plans[region,'刚性']['annual']) for key in ['transformer_npv_10k','storage_npv_10k','line_npv_10k']]
        parts = '、'.join(name + ('增加' if v >= 0 else '减少') + f(v if v >= 0 else -v) + '万元' for name,v in zip(['主变','储能','联络'],delta))
        texts.append(f'{cn}弹性方案相对刚性的费用变化为{parts}，合计减少{f(-sum(delta))}万元。费用差由各年度实际采购及投运批次形成，具体替代关系结合逐站设备与通道配置分析。')
    sections['restore_cost_components'] = '\n\n'.join(texts)
    sections['restore_equipment_mix'] = '表中两台、三台主变站数按2035年实际采用组合统计。相同台数的站点仍可能采用不同额定容量，故障后剩余能力还需结合最大单台容量判断。配储站数与储能规模分别反映补充支撑的空间范围和总量。'
    aggregate=[]
    for year in [2021,2025,2030,2035]:
        for r,cn in [('pizhou','邳州'),('city','市区')]:
            for label in LABELS:
                row=next(x for x in plans[r,label]['annual'] if x['year']==year)
                aggregate.append([cn,label,year,f(row['capacity_mva']),f(row['clr']),f(row['storage_mwh']),row['cumulative_lines']])
    tables['uncompressed_annual_summary'] = table('表5-0 保留2021实际容量的代表年度汇总', ['地区','方案','年份','年末主变/MVA','容载比','年末储能/MWh','累计新联络/条'], aggregate)
    tables['uncompressed_cost_summary'] = table('表5-0 保留2021实际容量的方案费用', ['地区','方案','评价期费用现值/万元'], costs)
    tables['new_case_assumptions'] = table('表5-0 两地区共同计算条件', ['参数','设置','依据'], [
        ['基期/规划年度','2021/2022—2035','基期设备固定，年度承接上年在役资产'],
        ['源荷序列','每年8760小时','历史模板回算及区域预测同比缩放'],
        ['正向储能支撑持续时间','邳州2.00 h、市区6.00 h','地区95%峰值持续时间'],
        ['储能规格','100.00 kW/215.00 kWh','采购资料'],
        ['可用电量系数','0.76','SOC可用窗口与放电效率的研究取值[122]'],
        ['新购主变','31.50、50.00、63.00、80.00 MVA','按站限制，有预留位置时第三台50.00 MVA'],
        ['既有转供','逐站原始MW固定封顶','站级转供收资、路径及共享馈线余量'],
        ['新增联络转出区段','全站区段数的20%以内','研究情景假设，正常和事故追加共同占用'],
        ['新增联络投资','邳州128.38、市区452.40万元/项','地区电缆长度占比'],
        ['反向承载计算系数','正常及健康站取0.80，故障站取1.00','锁定方案的静态容量校核条件'],
        ['功率因数','0.95','统一折算'],
        ['主变更换组织','同一原主变位置全期最多更换一次','共同实施假设'],
        ['弹性工程选择','配套费用参考值20%以内优先减少联络，再比较总费用','研究工程优选条件']])
    return tables, sections, evidence


def sync(check=False):
    t, s, evidence = assets()
    table_path, section_path = ASSET/'计算表.json', ASSET/'生成段落.json'
    tables, sections = json.loads(table_path.read_text()), json.loads(section_path.read_text())
    if check:
        for k,v in t.items():
            assert tables[k] == v, '计算表.json:' + k
        for k,v in s.items():
            assert sections[k] == v, '生成段落.json:' + k
    else:
        tables.update(t); sections.update(s)
        tables['station_pressure'] = tables['station_pressure'].replace('| 变电站 |','| 110 kV变电站 |')
        tables['station_pressure'] = re.sub(r'110千伏(?=[^|\n]+变)', '', tables['station_pressure'])
        table_path.write_text(json.dumps(tables,ensure_ascii=False,indent=2)+'\n')
        section_path.write_text(json.dumps(sections,ensure_ascii=False,indent=2)+'\n')
        REVIEW.mkdir(parents=True,exist_ok=True)
        (REVIEW/'逐站固定预案回代核验.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
        SOURCE.mkdir(parents=True,exist_ok=True)
        pd.DataFrame(evidence).to_csv(SOURCE/'逐站2035核验.csv',index=False)
    assert all(r['最小余量_MW'] > -1e-5 for r in evidence)
    return {'状态':'通过','地区':2,'主方案':4,'年度记录':60,'逐站分析':46,'未求解或更改模型':True}


if __name__ == '__main__':
    print(json.dumps(sync('--check' in sys.argv),ensure_ascii=False))
