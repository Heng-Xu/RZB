"""储能持续时间表：用完整精度折算功率及费用，仅在展示时保留两位小数。"""
from decimal import Decimal, ROUND_HALF_UP


def effective_power(duration):
    duration = Decimal(str(duration))
    if duration <= 0:
        raise ValueError('支撑持续时间须大于零')
    return min(Decimal('1.00'), Decimal('2.15') * Decimal('0.76') / duration)


def shown(value):
    return str(Decimal(str(value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))


def storage_duration_table():
    lines = ['表4-0 持续时间与储能有效功率', '',
             '| 储能支撑持续时间/h | 10柜额定能量/MWh | 可用电量系数 | 储能有效支撑功率/MW | 单位有效功率投资/万元·MW⁻¹ |',
             '| --- | --- | --- | --- | --- |']
    for duration in [1, 2, 4, 6, 8]:
        power = effective_power(duration)
        cost = Decimal('210.456262') / power
        lines.append('| ' + ' | '.join([shown(duration), '2.15', '0.76', shown(power), shown(cost)]) + ' |')
    return '\n'.join(lines) + '\n\n'
