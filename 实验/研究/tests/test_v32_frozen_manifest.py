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
