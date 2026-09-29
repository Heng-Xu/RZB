"""独立复核本轮两区县四方案的年度排序、成本与敏感性结果。"""

import json
from pathlib import Path

from .baseline_2021 import read_csv


ROOT = Path(__file__).resolve().parent / "outputs"
REGIONS = {"pizhou": "ordered_guide_pizhou_n1",
           "city": "ordered_guide_city_n1"}
YEARS = (2022, 2023, 2024, 2025)
MARGIN = 0.001
TOL = 1e-7


def audit(root=ROOT):
    portfolio = {}
    for region, folder in REGIONS.items():
        directory = root / folder
        summaries = {row["scheme"]: row for row in json.loads(
            (directory / "summary.json").read_text(encoding="utf-8"))}
        assert set(summaries) == {"rigid", "elastic"}
        rows = {scheme: {int(row["year"]): row for row in read_csv(
            directory / f"{scheme}_years.csv")}
                for scheme in summaries}
        for scheme in rows:
            assert set(rows[scheme]) == set(YEARS)
            assert summaries[scheme]["mip_gap"] < TOL
            assert summaries[scheme]["baseline_2021_capacity_mva"] > 0
            previous_capacity = summaries[scheme]["baseline_2021_capacity_mva"]
            for year in YEARS:
                current = rows[scheme][year]
                capacity = float(current["capacity_mva"])
                load = float(current["net_peak_proxy_mw"])
                assert capacity + TOL >= previous_capacity
                assert abs(float(current["clr"]) - capacity / load) < TOL
                assert float(current["new_storage_energy_mwh"]) >= 0
                previous_capacity = capacity
        assert (summaries["elastic"]["objective_npv_10k"] + TOL <
                summaries["rigid"]["objective_npv_10k"])
        for year in YEARS:
            assert (float(rows["elastic"][year]["clr"]) + TOL >=
                    float(rows["rigid"][year]["clr"]) + MARGIN)
            assert float(rows["rigid"][year]["clr"]) <= (2 if region == "pizhou" else 1.8) + TOL
        portfolio[region] = {"summary": summaries, "years": rows}
    for scheme in ("rigid", "elastic"):
        for year in YEARS:
            assert (float(portfolio["city"]["years"][scheme][year]["clr"]) + MARGIN <=
                    float(portfolio["pizhou"]["years"][scheme][year]["clr"]) + TOL)

    sensitivity = {}
    for row in read_csv(root / "ordered_guide_cost_sensitivity.csv"):
        key = (row["changed_component"], float(row["price_scale"]))
        group = sensitivity.setdefault(key, {})
        group[(row["region_id"], row["scheme"])] = row
    assert len(sensitivity) == 5
    for case, group in sensitivity.items():
        assert len(group) == 4, case
        for region in ("QX-00005", "QX-00007"):
            assert (float(group[(region, "elastic")]["lifecycle_npv_10k"]) + TOL <
                    float(group[(region, "rigid")]["lifecycle_npv_10k"]))
            for year in YEARS:
                assert (float(group[(region, "elastic")][f"clr_{year}"]) + TOL >=
                        float(group[(region, "rigid")][f"clr_{year}"]) + MARGIN)
        for scheme in ("rigid", "elastic"):
            for year in YEARS:
                assert (float(group[("QX-00007", scheme)][f"clr_{year}"]) + MARGIN <=
                        float(group[("QX-00005", scheme)][f"clr_{year}"]) + TOL)

    result = {
        "status": "PASS",
        "annual_years_checked": list(YEARS),
        "scheme_count": 4,
        "sensitivity_case_count": len(sensitivity),
        "rigid_cost_10k": sum(portfolio[r]["summary"]["rigid"]["objective_npv_10k"]
                              for r in REGIONS),
        "elastic_cost_10k": sum(portfolio[r]["summary"]["elastic"]["objective_npv_10k"]
                                for r in REGIONS),
        "checks": ["same district elastic cost below rigid",
                   "same district elastic annual CLR above rigid",
                   "city annual CLR below Pizhou by scheme",
                   "post-2021 capacity nondecreasing",
                   "annual CLR arithmetic",
                   "five sensitivity scenarios preserve the three comparisons"],
    }
    result["elastic_saving_10k"] = result["rigid_cost_10k"] - result["elastic_cost_10k"]
    (root / "ordered_guide_result_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(audit())
