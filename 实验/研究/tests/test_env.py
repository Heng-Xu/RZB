import linopy, yaml, pathlib

def test_lp_solve():
    m = linopy.Model()
    x = m.add_variables(lower=0, name="x")
    m.add_constraints(x >= 3)
    m.add_objective(1 * x)
    m.solve(solver_name="highs")
    assert abs(float(x.solution) - 3.0) < 1e-6

def test_params_keys():
    p = yaml.safe_load(open(pathlib.Path(__file__).parents[1] / "params.yaml", encoding="utf-8"))
    assert set(["tau_max","beta","eta","k_ol","r_cap_scheme_a","costs","milp","synthetic"]) <= set(p)
