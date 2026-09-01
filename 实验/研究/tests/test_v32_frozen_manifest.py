from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frozen_manifest_hashes_match_current_contract_and_dataset() -> None:
    frozen = ROOT / "results/runs/real-2021-2025-v32-frozen/manifest.json"
    manifest = json.loads(frozen.read_text(encoding="utf-8"))
    assert manifest["contract_sha256"] == _sha256(ROOT / "model_contract.yaml")
    assert manifest["processed_manifest_sha256"] == _sha256(
        ROOT / "data/processed/real_2021_2025/manifest.json"
    )
    assert len(manifest["validation_commit_sha"]) == 40
    int(manifest["validation_commit_sha"], 16)


def test_frozen_manifest_records_complete_sensitivity_inventory() -> None:
    frozen_root = ROOT / "results/runs/real-2021-2025-v32-frozen"
    manifest = json.loads((frozen_root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["model_version"] == "3.2.0"
    assert manifest["sensitivity_scenario_count"] == 17
    assert manifest["joint_sensitivity_scenario_count"] == 6
    assert len(manifest["sensitivity_scenarios"]) == 17


def test_frozen_manifest_output_hashes_match_packaged_files() -> None:
    frozen_root = ROOT / "results/runs/real-2021-2025-v32-frozen"
    manifest = json.loads((frozen_root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["output_files"]
    for relative_path, evidence in manifest["output_files"].items():
        path = frozen_root / relative_path
        assert path.is_file(), relative_path
        assert evidence["bytes"] == path.stat().st_size, relative_path
        assert evidence["sha256"] == _sha256(path), relative_path
