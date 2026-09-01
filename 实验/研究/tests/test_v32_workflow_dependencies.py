from __future__ import annotations

from pathlib import Path

import yaml

from scripts.run_v32_sensitivity_suite import FORMAL_SCENARIOS


RESEARCH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = RESEARCH_ROOT.parents[1]
POLICY_PATH = PROJECT_ROOT / ".github/v32-dependency-policy.yaml"


def _load_yaml(path: Path) -> dict:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_dependency_policy_covers_every_v32_workflow() -> None:
    policy = _load_yaml(POLICY_PATH)
    configured = set(policy["workflows"])
    actual = {path.name for path in (PROJECT_ROOT / ".github/workflows").glob("v32-*.yml")}
    assert configured == actual


def test_heavy_workflows_have_dispatch_sha_and_declared_dependency_paths() -> None:
    policy = _load_yaml(POLICY_PATH)
    groups = policy["path_groups"]
    for name, group_names in policy["workflows"].items():
        workflow_path = PROJECT_ROOT / ".github/workflows" / name
        workflow = _load_yaml(workflow_path)
        triggers = workflow["on"]
        assert "workflow_dispatch" in triggers, name
        text = workflow_path.read_text(encoding="utf-8")
        assert "V32_VALIDATION_COMMIT_SHA" in text, name
        assert "inputs.target_ref || github.sha" in text, name

        if name == "v32-model-ci.yml":
            actual_paths = set(triggers["pull_request"]["paths"])
        else:
            actual_paths = set(triggers["push"]["paths"])
        required = {
            path
            for group_name in group_names
            for path in groups[group_name]
        }
        assert required <= actual_paths, f"{name} missing {sorted(required - actual_paths)}"


def test_processed_manifest_is_an_explicit_heavy_model_dependency() -> None:
    policy = _load_yaml(POLICY_PATH)
    for name in policy["heavy_workflows"]:
        workflow = _load_yaml(PROJECT_ROOT / ".github/workflows" / name)
        paths = set(workflow["on"]["push"]["paths"])
        assert "实验/研究/data/processed/real_2021_2025/**" in paths, name
        assert "实验/研究/model_contract.yaml" in paths, name
        assert "实验/研究/model_contract_v3_2_overlay.yaml" in paths, name


def test_heavy_workflow_changes_do_not_fan_out_to_every_heavy_run() -> None:
    policy = _load_yaml(POLICY_PATH)
    for name in policy["heavy_workflows"]:
        workflow = _load_yaml(PROJECT_ROOT / ".github/workflows" / name)
        paths = set(workflow["on"]["push"]["paths"])
        assert f".github/workflows/{name}" in paths, name
        assert ".github/workflows/v32-*.yml" not in paths, name


def test_chronology_workflow_uses_current_v32_actions_without_retirements() -> None:
    text = (
        PROJECT_ROOT / ".github/workflows/v32-chronology-preflight.yml"
    ).read_text(encoding="utf-8")
    assert "run_v32_actual_baseline" in text
    assert "_retirement_candidates" not in text
    assert "real-2021-2025-contract-v3" not in text


def test_sensitivity_workflow_runs_every_formal_scenario() -> None:
    path = PROJECT_ROOT / ".github/workflows/v32-actual-sensitivity.yml"
    workflow = _load_yaml(path)
    matrix = workflow["jobs"]["parameter-scenario"]["strategy"]["matrix"]["include"]
    assert {item["scenario"] for item in matrix} == set(FORMAL_SCENARIOS)
    assert "EXPECTED_SCENARIO_COUNT: '17'" in path.read_text(encoding="utf-8")
