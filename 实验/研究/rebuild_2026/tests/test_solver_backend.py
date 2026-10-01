"""后端替换须保留最优成本，并在次级排序中服从已有费用约束。"""
import pytest
from rebuild_2026.annual_no_tie_investment_submodel import LinearModel


def test_highspy_and_scipy_agree_then_warm_start_respects_cost(monkeypatch):
    def solve(backend):
        monkeypatch.setenv('XUZHOU_MILP_BACKEND',backend)
        model=LinearModel()
        a=model.variable(2);b=model.variable(2);c=model.variable(3)
        model.constraint({a:1,b:1,c:1},lower=1)
        _,cost=model.solve(stage='minimum_cost')
        assert cost==pytest.approx(2)
        model.constraint({a:2,b:2,c:3},upper=cost+1e-5)
        model.costs=[-1,-2,-5]
        x,reserve=model.solve(stage='reserve')
        assert x.tolist()==pytest.approx([0,1,0])
        assert reserve==pytest.approx(-2)
        return x,cost
    x,cost=solve('scipy');xx,cc=solve('highspy')
    assert xx.tolist()==pytest.approx(x.tolist()) and cc==pytest.approx(cost)


def test_highspy_does_not_accept_infeasible_model(monkeypatch):
    monkeypatch.setenv('XUZHOU_MILP_BACKEND','highspy')
    model=LinearModel();x=model.variable(1)
    model.constraint({x:1},lower=2)
    with pytest.raises(ValueError,match='Infeasible'):model.solve(stage='infeasible_case')


def test_fixed_device_layout_reoptimizes_continuous_dispatch_with_zero_gap(monkeypatch):
    monkeypatch.setenv("XUZHOU_MILP_BACKEND", "highspy")
    model = LinearModel()
    device = model.variable(2)
    transfer = model.variable(0, upper=3, integer=0)
    model.constraint({device: 3, transfer: 1}, lower=4)
    selected, cost = model.solve(stage="equipment")
    assert cost == pytest.approx(2)
    model.lower_bounds[device] = model.upper_bounds[device] = round(float(selected[device]))
    model.integrality[device] = 0
    model.costs = [0, 1]
    result, dispatch = model.solve(stage="dispatch_at_selected_layout")
    assert result[device] == pytest.approx(1)
    assert dispatch == pytest.approx(1)
    assert model.solve_history[-1]["mip_gap"] == 0
    assert model.solve_history[-1]["status"] == "optimal"
