"""独立准备两地区2021—2035输入，不回写已定稿模型。"""
import copy
import json
import math

import numpy as np

from ..forecast_2035_20261017 import run as forecast
from ..two_district_ordered_guide_run import guide_range

base = forecast.base
ROOT = base.ROOT
RAW = ROOT/'研究报告/试算/20261017_区段转供逐年2035'
PUBLIC = ROOT/'研究报告/01研究推荐/当前版/区段转供逐年2035_20261017'
SOURCE = ROOT/'研究报告/数据来源/当前版/区段转供逐年2035_20261017'
REVIEW = ROOT/'研究报告/05_review/当前版/1017区段转供逐年2035'
REGIONS = {'city':'市区', 'pizhou':'邳州'}
dump, write_csv, sha = forecast.dump, forecast.write_csv, forecast.sha


def forecasts(region):
    section = '## 2.' if region == 'city' else '## 3.'
    rows = forecast.table_values(section)
    headers = [s.strip() for s in rows[0].strip('|').split('|')]
    cells = [s.strip() for s in rows[2].strip('|').split('|')]
    load = {int(h[:4]):float(v) for h,v in zip(headers,cells) if h[:4].isdigit()}
    pv = {int(v[0]):float(v[1]) for row in forecast.table_values('## 1.')
          for v in [[x.strip() for x in row.strip('|').split('|')]] if v[0].isdigit()}
    # 2024年底有全年节点，2024年10月节点不混入年度增长率。
    pv[2024] = 510.
    given_load, given_pv = set(load), set(pv)
    for values in (load,pv):
        nodes = sorted(values)
        for y in range(2025,2036):
            if y not in values:
                a=max(k for k in nodes if k<y); b=min(k for k in nodes if k>y)
                values[y]=values[a]+(values[b]-values[a])*(y-a)/(b-a)
    return [dict(region=REGIONS[region], year=y, forecast_load_mw=load[y], pv_index=pv[y],
                 load_factor=load[y]/load[2025], pv_factor=pv[y]/pv[2025],
                 load_yoy=load[y]/load[y-1]-1 if y>2025 else None,
                 pv_yoy=pv[y]/pv[y-1]-1 if y>2025 else None,
                 load_interpolated=y not in given_load,pv_interpolated=y not in given_pv)
            for y in range(2025,2036)]


def prepare(region):
    for p in (RAW,PUBLIC,SOURCE,REVIEW):p.mkdir(parents=True,exist_ok=True)
    out=RAW/region;out.mkdir(exist_ok=True)
    inp,_,original=base.prepare(region,'annual_2021');inp=copy.deepcopy(inp)
    ids=list(inp['stations']);annual=forecasts(region)
    data=np.load(forecast.PROFILES/f'{region}_stations.npz')
    order=[list(data['station_ids']).index(s) for s in ids]
    raw=data['power_mw'][:,order]
    net=raw*inp['annual_observed_peak_mw']['2025']/raw.sum(axis=1).max()
    scale=inp['annual_observed_peak_mw']['2025']/raw.sum(axis=1).max()
    code='QX-00007' if region=='city' else 'QX-00014'
    rows=base.old.old.base.previous.rows(forecast.PROXY)
    # 区县匿名编号从当前模型的站集合核对，避免猜测编号。
    proxies={r['model_station_id']:r for r in rows if r['model_station_id'] in ids
             and r['voltage_kv']=='110' and r['year']=='2025' and r['variant']=='night_central'}
    assert set(proxies)==set(ids),(region,set(ids)-set(proxies))
    central=np.array([float(proxies[s]['gross_load_proxy_mw_2025']) for s in ids])*scale
    daytime=np.isin(np.arange(8760)%24,np.arange(8,18))
    generation=np.where(daytime[:,None],np.maximum(central[None,:]-net,0.),0.)
    demand=net+generation
    assert np.max(abs(demand-generation-net))<1e-9
    powers={y:net*inp['annual_observed_peak_mw'][str(y)]/inp['annual_observed_peak_mw']['2025']
            for y in range(2021,2026)}
    inp['years']=list(range(2022,2036));inp['fixed_baseline_year']=2021
    floors={str(y):guide_range(inp['growth_rate'])[0] for y in range(2021,2026)}
    for a in annual:
        y=a['year']
        if y>2025:
            powers[y]=demand*a['load_factor']-generation*a['pv_factor']
            inp['annual_observed_peak_mw'][str(y)]=inp['annual_observed_peak_mw']['2025']*a['load_factor']
            first,last=(2025,2030) if y<=2030 else (2030,2035)
            values={v['year']:v['forecast_load_mw'] for v in annual}
            floors[str(y)]=guide_range((values[last]/values[first])**.2-1)[0]
    # 区段等分仅是现有资料下的可复现代理。全期同一划分，负荷和光伏按同一比例移动。
    # 2MW保守设计值同时限制最大负荷/光伏/净功率，不宣称电缆一律受架空条款限制。
    envelope=np.maximum(demand.max(axis=0)*annual[-1]['load_factor'],
                        generation.max(axis=0)*annual[-1]['pv_factor'])
    envelope=np.maximum(envelope,np.max([np.abs(p).max(axis=0) for p in powers.values()],axis=0))
    inp['block_count']={s:max(1,math.ceil(envelope[j]/2.)) for j,s in enumerate(ids)}
    inp['common_floor_by_year']=floors
    for kind,life,om in [('transformer',forecast.TRANSFORMER_LIFE,forecast.TRANSFORMER_OM),
                         ('line',forecast.LINE_LIFE,forecast.LINE_OM),('storage',forecast.STORAGE_LIFE,forecast.STORAGE_OM)]:
        inp['cost_factors'][kind]={str(y):forecast.factor(y,life,om) for y in inp['years']}
    # 事故转供统计保留为上界，随年度正向负荷缩放；不再匹配地区平均转供率。
    evidence={r['station']:r for r in inp['station_transfer_evidence']}
    for y,p in powers.items():
        inp['existing_transfer_budget_by_year_mw'][str(y)]={s:min(evidence[s]['transferable_mw'],
            (inp['station_transfer_rates'][s] or 0.)*max(0.,float(p[:,j].max()))) for j,s in enumerate(ids)}
    inp.update(normal_supply_area_fixed=True,normal_transfer_policy='年内固定付费联络供区方案；既有统计通道只用于事故',
        contingency_policy='正常方案保留，仅故障站原属区段向直接相邻接收站追加切换；年内预案跨工况共用',
        block_policy='同站等比例源荷区段；全期区段不变、整区段切换；各代理馈线组最多5段、3个联络端点、2座邻站',
        block_peak_design_mw=2., max_blocks_per_feeder_group=5,
        procurement_policy='2021初始容量固定，2022—2035同一主变位置最多更换一次，投运资产逐年保留',
        scope='两地区2021固定基期、2022—2035逐年滚动；固定区段及局部事故转供的8760小时静态校核',
        forecast_basis=dict(source=str(forecast.FORECAST.relative_to(ROOT)),sha256=sha(forecast.FORECAST),
            historical='2021—2025原统计峰值与同期净负荷模板保持',
            future='2025代理负荷与光伏分别乘最新负荷及全市光伏相对2025比例；缺年等增量插值',
            peak='110kV原2025统计峰值按预测负荷比例外推；不直接替换成全市总负荷',
            decomposition='08—18时按归档夜间中位代理分解，2025逐点还原；空间分布为研究代理',
            lower='2022—2025沿用历史平均增长率分档，未来每五年用预测负荷复合增长率分档，两方案一致',
            network='原候选连接保留为代理可达范围，既有EQ不作为真实竣工线路；区段约束后不再自由重配',
            switching='正常方案及各站事故预案在年内所有小时共用；故障只追加转出故障站原属区段'))
    dump(out/'inputs.json',inp)
    np.savez_compressed(out/'hourly.npz',**{str(y):p for y,p in powers.items()})
    np.savez_compressed(out/'base_components.npz',net_2025=net,demand_proxy=demand,generation_proxy=generation,
                        observed=data['observed'][:,order],station_ids=np.array(ids))
    write_csv(SOURCE/f'{region}_预测增长率.csv',annual)
    dump(SOURCE/f'{region}_来源与假设.json',dict(inputs_sha256=sha(out/'inputs.json'),forecast=inp['forecast_basis'],
        sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in
            (forecast.FORECAST,original/'inputs.json',forecast.PROFILES/f'{region}_stations.npz',forecast.PROXY)],
        initial_capacity_mva=inp['initial_capacity_mva'],fitted_station_baseline=inp['baseline_treatment'],
        baseline_reconstruction_error_mw=float(abs(demand-generation-net).max())))
    print('PREPARED',region,inp['initial_capacity_mva'],sum(inp['block_count'].values()),flush=True)
    return inp,powers


def load(region):
    root=RAW/region
    if not (root/'inputs.json').exists():return prepare(region)
    inp=json.loads((root/'inputs.json').read_text());assert inp['forecast_basis']['sha256']==sha(forecast.FORECAST)
    data=np.load(root/'hourly.npz');return inp,{int(y):data[y] for y in data.files}


if __name__=='__main__':
    for region in REGIONS:prepare(region)
