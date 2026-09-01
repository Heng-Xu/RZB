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


def test_freeze_workflow_and_receipt_model_three_commit_sha_roles() -> None:
    workflow = (
        ROOT.parents[1] / ".github/workflows/v32-freeze-verification.yml"
    ).read_text(encoding="utf-8")
    receipt = (ROOT / "scripts/write_v32_freeze_receipt.py").read_text(encoding="utf-8")
    for field in (
        "generated_from_commit_sha",
        "package_commit_sha",
        "checkout_verified_sha",
        "last_verified_commit_sha",
        "frozen_manifest_sha256",
        "verification_workflow_run_id",
    ):
        assert field in receipt
    assert "write_v32_freeze_receipt.py" in workflow
    assert "freeze_verification_receipt.json" in workflow
