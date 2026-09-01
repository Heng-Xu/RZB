from __future__ import annotations

import json
from pathlib import Path

from scripts.write_v32_freeze_receipt import build_freeze_verification_receipt


def test_freeze_receipt_keeps_package_generation_verification_and_checkout_shas_distinct(
    tmp_path: Path,
) -> None:
    frozen = tmp_path / "frozen"
    frozen.mkdir()
    manifest = frozen / "manifest.json"
    manifest.write_text(
        json.dumps({"model_version": "3.2.0", "validation_commit_sha": "a" * 40}),
        encoding="utf-8",
    )
    output = tmp_path / "freeze_verification_receipt.json"
    receipt = build_freeze_verification_receipt(
        frozen_root=frozen,
        output_path=output,
        generated_from_commit_sha="a" * 40,
        package_commit_sha="b" * 40,
        checkout_verified_sha="c" * 40,
        last_verified_commit_sha="c" * 40,
        workflow_run_id="33466902676",
        verification_timestamp="2026-09-01T00:00:00Z",
        test_result="PASS",
        core_artifact_verification="PASS",
    )
    assert receipt["generated_from_commit_sha"] == "a" * 40
    assert receipt["package_commit_sha"] == "b" * 40
    assert receipt["checkout_verified_sha"] == "c" * 40
    assert receipt["last_verified_commit_sha"] == "c" * 40
    assert receipt["verification_workflow_run_id"] == "33466902676"
    assert len(receipt["frozen_manifest_sha256"]) == 64
    assert receipt["test_result"] == "PASS"
    assert receipt["core_artifact_verification"] == "PASS"
    assert json.loads(output.read_text(encoding="utf-8")) == receipt
