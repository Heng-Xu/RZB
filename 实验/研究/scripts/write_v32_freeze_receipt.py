#!/usr/bin/env python3
"""生成 v3.2 冻结包的可审计验证收据。"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any


SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha(value: str, field: str) -> str:
    value = str(value).strip()
    if SHA_RE.fullmatch(value) is None:
        raise ValueError(f"{field} must be a 40-character commit SHA")
    return value.lower()


def _git_head(root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=Path(root),
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise ValueError("cannot determine checkout commit SHA")
    return _sha(completed.stdout.strip(), "checkout_verified_sha")


def build_freeze_verification_receipt(
    *,
    frozen_root: Path,
    output_path: Path,
    generated_from_commit_sha: str | None = None,
    package_commit_sha: str | None = None,
    checkout_verified_sha: str | None = None,
    last_verified_commit_sha: str | None = None,
    workflow_run_id: str | None = None,
    verification_timestamp: str | None = None,
    test_result: str = "PASS",
    core_artifact_verification: str = "PASS",
) -> dict[str, Any]:
    frozen_root = Path(frozen_root).resolve()
    manifest_path = frozen_root / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    generated = generated_from_commit_sha or manifest.get("generated_from_commit_sha") or manifest.get("validation_commit_sha")
    if not generated:
        raise ValueError("generated_from_commit_sha is unavailable")
    checkout_root = frozen_root.parents[2]
    checkout = checkout_verified_sha or os.environ.get("V32_VALIDATION_COMMIT_SHA") or _git_head(checkout_root)
    package = package_commit_sha or manifest.get("package_commit_sha") or generated
    verified = last_verified_commit_sha or os.environ.get("V32_LAST_VERIFIED_COMMIT_SHA") or checkout
    timestamp = verification_timestamp or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    receipt = {
        "schema_version": "v3.2.freeze-verification-receipt.v1",
        "status": "PASS" if test_result == "PASS" and core_artifact_verification == "PASS" else "FAIL",
        "frozen_manifest_path": str(manifest_path.relative_to(checkout_root)),
        "frozen_manifest_sha256": _sha256(manifest_path),
        "manifest_validation_commit_sha": _sha(str(manifest.get("validation_commit_sha", "")), "manifest_validation_commit_sha"),
        "generated_from_commit_sha": _sha(str(generated), "generated_from_commit_sha"),
        "package_commit_sha": _sha(str(package), "package_commit_sha"),
        "checkout_verified_sha": _sha(str(checkout), "checkout_verified_sha"),
        "last_verified_commit_sha": _sha(str(verified), "last_verified_commit_sha"),
        "verification_workflow_run_id": str(workflow_run_id or os.environ.get("GITHUB_RUN_ID") or "local"),
        "verification_timestamp": timestamp,
        "test_result": str(test_result),
        "core_artifact_verification": str(core_artifact_verification),
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--generated-from-commit-sha")
    parser.add_argument("--package-commit-sha")
    parser.add_argument("--checkout-verified-sha")
    parser.add_argument("--last-verified-commit-sha")
    parser.add_argument("--workflow-run-id")
    parser.add_argument("--verification-timestamp")
    parser.add_argument("--test-result", default="PASS")
    parser.add_argument("--core-artifact-verification", default="PASS")
    args = parser.parse_args()
    receipt = build_freeze_verification_receipt(
        frozen_root=args.frozen_root,
        output_path=args.output,
        generated_from_commit_sha=args.generated_from_commit_sha,
        package_commit_sha=args.package_commit_sha,
        checkout_verified_sha=args.checkout_verified_sha,
        last_verified_commit_sha=args.last_verified_commit_sha,
        workflow_run_id=args.workflow_run_id,
        verification_timestamp=args.verification_timestamp,
        test_result=args.test_result,
        core_artifact_verification=args.core_artifact_verification,
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
