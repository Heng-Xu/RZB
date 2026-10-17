"""重点站独立加减抽核、成果哈希及正式报告上下文衔接。"""
import json
from pathlib import Path

import numpy as np

from . import model as m, prepare as p
from .export import FILENAME


def update_memory(proof, readback, probes):
    lines = ['# 当前工作：四年更换间隔下按当年总费用逐年比选','',
        '本轮按用户同意的讨论结论重算两地区2021—2035年方案。正式六章、Word/WPS PDF及冻结采用案例未替换。',
        '', '## 模型与入口','',
        '入口：`实验/研究/rebuild_2026/annual_cost_interval_2035_20261017`。原始解：`研究报告/试算/20261017_四年间隔总费用2035/{city,pizhou}/{rigid,elastic}`。',
        '', '2021容量固定为市区3113.50 MVA、邳州2027.00 MVA。2022—2035逐年以上年在役设备和当年源荷求解。'
        '两次原主变位置更换年份之差至少为4，为研究工程实施假设；基期既往更换年份缺失，从2022年记录。'
        '主变、储能、付费联络投运后逐年承接。新购31.5、50、63、80 MVA，允许扩建位置第三台按50 MVA。',
        '', '刚性、弹性共同使用当年新增主变、储能和联络总费用现值目标，取消配套费用20%容差和少建联络优先阶段。'
        '共同容载比下限、逐站转供MW预算、路径和源馈线组、受端余量、初始容量及锁定经济参数不变。'
        '刚性保留新增容量2.0控制，弹性取消该控制；无刚弹结果排序约束。',
        '', '原时序库按路径和哈希继承，未重复复制。历史源荷为模板回算和补值序列，2025转供收资用于早期年度，EQ拓扑和区段为研究代理。'
        '邳州2021固定设备的事故缺口单列，未加入基期虚拟储能。储能按额定功率与可用电量/时长静态校核，无连续SOC优化。',
        '', '## 结果','']
    for region,name in p.REGIONS.items():
        for case in p.CASES:
            s = json.loads((p.RAW/region/case/'summary.json').read_text())
            a = s['annual'][-1]
            maximum = max(h['solver']['mip_gap'] for h in s['history'])
            lines.append(f'{name}2035{case}：容量{a["capacity_mva"]:.2f} MVA，容载比{a["clr"]:.2f}，'
                f'年末储能{a["storage_nameplate_mw"]:.2f} MW（{a["storage_mwh"]:.2f} MWh），'
                f'累计新增联络{a["cumulative_lines"]}条，费用现值{s["cost_npv_10k"]:.2f}万元。年度最大条件费用间隙{maximum:.2%}。')
            lines.append('')
    lines.extend(['后期停止新增储能的能力检验逐年继承本轮上年资产，固定已有储能，原主变位置取四年间隔允许的最大候选规格。'
        '分别固定已有联络和开放新增联络自由选择，可行配置再核对全年。此为单年反事实，非连续不新增储能链。',''])
    for name in p.REGIONS.values():
        for mode in ('只新增主变','新增主变及联络'):
            years = [str(r['年份']) for r in probes['rows'] if r['地区']==name and r['检验']==mode and r['结论']=='可行']
            lines.append(f'{name}2031—2035，{mode}且不新增储能的可行年份：'+('、'.join(years) if years else '无')+'。')
    lines.extend(['', '原设备表46座有对应站点中，9座预留扩建容量超过50 MVA：63 MVA五座、80 MVA一座、100 MVA三座，均为1个预留位置。'
        '扩建工程造价原表仅提供50 MVA实例。本轮第三台候选仍为50 MVA，超过50 MVA的工程费用存在资料缺口；不可行结论仅对当前候选集成立。',
        '', '费用按具体可行方案列示，年度条件下界和间隙保留，不宣称全期联合最优。前后比较同时改变更换间隔和选择顺序，差额为合并影响。',
        '', '## 交付与核验','',f'工作簿：`{(p.PUBLIC/FILENAME).relative_to(p.ROOT)}`。前两页为两地区左右对照，另列后期新增措施、前后版本比较、费用分项、第三台资料边界、更换履历、切换预案及能力检验。',
        '', f'四套方案{proof["full_hour_pairs"]:,}个小时—工况组合通过独立复核。最大矩阵误差{proof["max_matrix_error"]:.2e}，'
        f'费用误差{proof["max_cost_error_10k"]:.2e}万元，工作簿{readback["cells"]:,}格回读。',
        '',f'来源：`{p.SOURCE.relative_to(p.ROOT)}`；核验：`{p.REVIEW.relative_to(p.ROOT)}`。'
        '首轮能力探测误将开放候选线设为全部必须建设，已退出结论并归档；修正自由选择后重跑，加入可行域包含关系回归检查。'
        '市区从2031起加强费用搜索并连续承接后续年度，初次候选另存试算目录。正式报告现有源、原生Word及WPS PDF三阶段复核通过。',''])
    (p.ROOT/'memory/current.md').write_text('\n'.join(lines))


def run():
    proof = json.loads((p.REVIEW/'逐年方案独立核验.json').read_text())
    readback = json.loads((p.REVIEW/'工作簿回读.json').read_text())
    probes = json.loads((p.REVIEW/'后期能力检验.json').read_text())
    formal = json.loads((p.REVIEW/'既有报告三阶段复核.json').read_text())
    assert proof['verified'] and readback['verified'] and probes['verified'] and formal['verified']
    update_memory(proof,readback,probes)
    spots, maxerror = [], 0.
    for region in p.REGIONS:
        inp, powers = p.load(region)
        ids, aa = list(inp['stations']), m.arcs(inp)
        for case in p.CASES:
            for y in (2022,2025,2030,2035):
                r = json.loads((p.RAW/region/case/str(y)/'adopted.json').read_text())
                u, n = np.array(r['units']), np.array(r['modules'])
                normal = {int(k):v for k,v in r['normal'].items()}
                extra = {int(k):v for k,v in r['extra'].items()}
                for j in {int(np.argmax(n)),int(np.argmax(u.sum(1)))}:
                    worst = float('inf')
                    for failed in range(-1,len(ids)):
                        active = normal.copy()
                        if failed>=0:
                            for k,count in extra.items():
                                if aa[k]['sa']==failed:
                                    active[k] = active.get(k,0)+count
                        served = powers[y][:,j].copy()
                        for k,count in active.items():
                            a = aa[k]
                            q = powers[y][:,a['sa']]*count/inp['block_count'][a['source']]
                            if a['sa']==j:
                                served -= q
                            if a['sb']==j:
                                served += q
                        firm = .95*(u[j].sum()-(u[j].max() if failed==j else 0.))
                        bp = min(.1,.215*.76/max(1,inp['stations'][ids[j]]['forward_duration_h']))*n[j]
                        bn = min(.1,.215*.76/max(1,inp['stations'][ids[j]]['reverse_duration_h']))*n[j]
                        margin = min(float(np.min(firm+bp-served)),
                                     float(np.min(firm*(1. if failed==j else .8)+bn+served)))
                        assert margin>=-1e-5,(region,case,y,j,failed,margin)
                        maxerror = max(maxerror,max(0.,-margin))
                        worst = min(worst,margin)
                    spots.append(dict(地区=p.REGIONS[region],方案=case,年份=y,变电站=ids[j],
                        校核小时数=8760,工况数=len(ids)+1,最小余量_MW=worst))
    p.write_csv(p.REVIEW/'重点站逐时独立加减核对.csv',spots)
    p.dump(p.REVIEW/'交付核验.json',dict(verified=True,confidence='附适用条件用于研究比较',
        full_hour_pairs=proof['full_hour_pairs'],spot_station_years=len(spots),max_spot_error_mw=maxerror,
        max_matrix_error=proof['max_matrix_error'],max_cost_error_10k=proof['max_cost_error_10k'],workbook_cells=readback['cells'],
        late_probes=len(probes['rows']),formal_checks=formal,
        caveats=['历史源荷为回算及补值序列；2025转供收资用于早期年度，EQ为研究代理',
            '储能为静态时长支撑，无连续SOC；费用是逐年条件候选，年度下界不作全期最优界',
            '后期无新增储能检验为单年极限能力反事实；第三台与新增站址未凭空扩展'],
        scope='本轮新增两地区逐年模型、表格与核验；正式六章、Word、WPS PDF和冻结采用案例未替换'))
    paths = set()
    initial_archive = p.RAW.parent/'20261017_四年间隔总费用2035_市区初次候选'
    recovery_archive = p.RAW.parent/'20261017_四年间隔总费用2035_市区恢复归档'
    for directory in (Path(__file__).parent,p.RAW,p.PUBLIC,p.SOURCE,p.REVIEW,initial_archive,recovery_archive):
        paths.update(v for v in directory.rglob('*') if v.is_file() and '__pycache__' not in v.parts and v.suffix!='.log')
    manifest_path = p.REVIEW/'交付与核对清单.json'
    paths.discard(manifest_path)
    paths.update(p.ROOT/name for name in ('prompt.md','memory/current.md','memory/archive/2026-10-17-四年间隔总费用重算前.md'))
    formal_paths = [p.ROOT/'研究报告/01研究推荐/当前版/报告数据采用版本.json',
        p.ROOT/'研究报告/04_word/研究报告终稿.docx',p.ROOT/'研究报告/04_word/研究报告终稿.pdf']
    paths.update(formal_paths)
    p.dump(manifest_path,dict(状态='逐年可行方案已核对',files=[dict(path=str(v.relative_to(p.ROOT)),sha256=p.sha(v))
        for v in sorted(paths)],scope='四年更换间隔及年度总费用比选；两地区2021—2035方案与后期能力检验'))
    context_path = p.ROOT/'研究报告/05_review/当前版/工作上下文衔接.json'
    previous_context = p.REVIEW/'继承基线/研究报告/05_review/当前版/工作上下文衔接.json'
    context = json.loads(previous_context.read_text())
    for name,row in context['上下文变更'].items():
        assert p.sha(p.ROOT/row['原件归档']) == row['原SHA256']
        row['现SHA256'] = p.sha(p.ROOT/name)
    proof_path = p.REVIEW/'逐年方案独立核验.json'
    context.update(独立成果清单=str(manifest_path.relative_to(p.ROOT)),独立成果清单SHA256=p.sha(manifest_path),
        独立核验记录=str(proof_path.relative_to(p.ROOT)),独立核验记录SHA256=p.sha(proof_path),
        前次上下文归档=str(previous_context.relative_to(p.ROOT)))
    p.dump(context_path,context)
    print('AUDIT_INTERVAL',len(spots),'station-years,',len(paths),'files',flush=True)


if __name__=='__main__':
    run()
