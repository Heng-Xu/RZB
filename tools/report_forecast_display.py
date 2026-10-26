"""从已锁定年度预测表提取报告展示值，不修改预测或模型输入。"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'研究报告/数据来源/当前版/逐年需求驱动2035_20261017'
PV_FORECAST_TO_MW = 10.0  # 原预测与月度统计均为万千瓦；原表交叉核验见来源记录。


def forecasts():
    return {region: list(csv.DictReader((SOURCE/f'{region}_预测增长率.csv').open(encoding='utf-8-sig')))
            for region in ['city', 'pizhou']}


def average(values, first, last):
    return (values[last]/values[first])**(1/(last-first))-1


def assets(table, shown, inputs):
    data = forecasts()
    rows = {r: {int(x['year']): x for x in data[r]} for r in data}
    load, pv = [], []
    from case_horizon import end_year
    last_year = end_year()
    for year in range(2025, last_year + 1):
        values = [year]
        for region in ['city', 'pizhou']:
            row = rows[region][year]
            values += [shown(float(row['forecast_load_mw'])),
                       shown(float(inputs[region]['annual_observed_peak_mw'][str(year)]))]
        load.append(values)
        row = rows['city'][year]
        assert row['pv_factor'] == rows['pizhou'][year]['pv_factor']
        factor = float(row['pv_factor'])
        pv.append([year, shown(float(row['pv_index'])*PV_FORECAST_TO_MW), shown(factor),
                   shown(491.18*factor), shown(1559.64*factor)])
    load_avg = []
    for first, last in [(a, b) for a, b in [(2025, 2030), (2030, 2035)] if b <= last_year]:
        load_avg.append([f'{first}—{last}'] + [shown(100*average(
            {y: float(row['forecast_load_mw']) for y, row in rows[r].items()}, first, last))+'%'
            for r in ['city', 'pizhou']])
    return {
        'forecast_load': table('表3-0 两地区区域负荷预测及110 kV电网规划预测峰值',
            ['年份', '市区区域预测/MW', '市区110 kV预测峰值/MW', '邳州区域预测/MW', '邳州110 kV预测峰值/MW'], load,
            '2025年为基准，110 kV电网规划预测峰值按区域负荷预测的增长比例确定。'),
        'forecast_load_growth': table('表3-0 负荷预测对应的分阶段年最大净负荷平均增长率',
            ['时期', '市区', '邳州'], load_avg),
        'forecast_pv': table('表3-0 光伏预测相对规模及两地区装机容量',
            ['年份', '全市光伏装机容量预测/MW', '相对2025年倍数', '市区装机/MW', '邳州装机/MW'], pv)}
