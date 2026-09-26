import csv

from rebuild_2026.hourly_source_profile import OUTPUT_DIR
from rebuild_2026.model_consistency_audit import build_checks


def test_rebuild_outputs_reconcile_without_claiming_guide_feasibility():
    checks = build_checks()
    assert len(checks) == 151
    assert all(row["status"] == "pass" for row in checks)
    assert any("不是导则认证" in row["note"] for row in checks)


def test_audit_detects_broken_synchronous_station_sum(tmp_path):
    source = OUTPUT_DIR / "annual_forward_station_scenes_2021_2025.csv"
    with source.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    rows[0]["estimated_station_net_load_mw"] = str(float(rows[0]["estimated_station_net_load_mw"]) + 1)
    modified = tmp_path / source.name
    with modified.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    checks = build_checks(overrides={source.name: modified})
    assert any(row["check_id"] == "synchronous_forward_sum" and row["status"] == "fail" for row in checks)
