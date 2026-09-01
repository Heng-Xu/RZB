from __future__ import annotations

from pathlib import Path

import pytest

from src.v32_contract import V32ContractError, validation_commit_sha


ROOT = Path(__file__).resolve().parents[1]


def test_validation_sha_uses_explicit_ci_checkout_commit(monkeypatch) -> None:
    expected = "a" * 40
    monkeypatch.setenv("V32_VALIDATION_COMMIT_SHA", expected)
    assert validation_commit_sha(ROOT) == expected


def test_validation_sha_rejects_non_commit_ref(monkeypatch) -> None:
    monkeypatch.setenv("V32_VALIDATION_COMMIT_SHA", "model-v3.2-autonomous-review")
    with pytest.raises(V32ContractError, match="40-character commit SHA"):
        validation_commit_sha(ROOT)


def test_formal_run_and_scan_manifests_record_validation_sha() -> None:
    paths = (
        ROOT / "src/v32_actual_pipeline.py",
        ROOT / "src/v32_frontier.py",
        ROOT / "src/v32_sensitivity.py",
        ROOT / "scripts/build_v32_formal_outputs.py",
    )
    for path in paths:
        assert '"validation_commit_sha"' in path.read_text(encoding="utf-8"), path
