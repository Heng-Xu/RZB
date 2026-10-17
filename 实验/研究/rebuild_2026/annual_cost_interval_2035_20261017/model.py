"""保留固定预案与安全约束，按最近更换年份控制原主变位置。"""
import numpy as np

from ..annual_demand_driven_2035_20261017 import model as parent
from . import prepare as p

arcs, layout, verify = parent.arcs, parent.layout, parent.verify


def locked_positions(last_replacement_year, year, interval=p.INTERVAL):
    last = np.asarray(last_replacement_year, dtype=int)
    assert np.all((last == 0) | (last < year))
    return (last > 0) & (year - last < interval)


def build(inp, power, year, case, old, oldn, built, last_replacement_year, selected):
    assert case in p.CASES
    return parent.build(inp, power, year, case, old, oldn, built,
                        locked_positions(last_replacement_year, year, inp['replacement_interval_years']), selected)
