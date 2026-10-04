"""10.03甲方反馈对应的当前费用参数；历史实验默认值保留。"""
from .joint_lifecycle_optimizer import cost_factors as historical_cost_factors
from .joint_lifecycle_optimizer import npv_factor, YEARS

TRANSFORMER_LIFE=40
LINE_LIFE=40
STORAGE_LIFE=25
TRANSFORMER_OM=.042
LINE_OM=.022
STORAGE_OM=.03
DISCOUNT_RATE=.06
CABLE_TOTAL_10K_PER_KM=180.0
OVERHEAD_10K_PER_KM=24.0
LINE_TYPES={'架空为主':.10,'电缆为主':.90}

def line_capex(cable_fraction):
    if not 0<=cable_fraction<=1:
        raise ValueError('电缆长度占比应在0至1之间')
    return 3*((1-cable_fraction)*OVERHEAD_10K_PER_KM+cable_fraction*CABLE_TOTAL_10K_PER_KM)+6

def cost_factors():
    return {
        'transformer':{y:npv_factor(y,DISCOUNT_RATE,TRANSFORMER_LIFE,TRANSFORMER_OM) for y in YEARS},
        'line':{y:npv_factor(y,DISCOUNT_RATE,LINE_LIFE,LINE_OM) for y in YEARS},
        'storage':{y:npv_factor(y,DISCOUNT_RATE,STORAGE_LIFE,STORAGE_OM) for y in YEARS},
        'discount_rate':DISCOUNT_RATE,'transformer_life_years':TRANSFORMER_LIFE,
        'line_life_years':LINE_LIFE,'storage_life_years':STORAGE_LIFE,
        'transformer_fixed_om_rate':TRANSFORMER_OM,'line_fixed_om_rate':LINE_OM,
        'storage_fixed_om_rate':STORAGE_OM,
    }
