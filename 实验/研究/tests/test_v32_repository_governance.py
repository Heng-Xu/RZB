from __future__ import annotations

from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = RESEARCH_ROOT.parents[1]


SUPERSEDED_ACTIVE_PHRASES = (
    "当前 model_contract.yaml 已为 3.1.0",
    "严格路径起点与不限制路径不同",
    "两路径累计年化成本只作各自口径下的结果，不作跨口径",
    "S0=2×P2021 为正式基线",
    "严格路径从不同归一起点",
)


def test_active_handoffs_are_short_v32_only_documents() -> None:
    for relative in ("prompt.md", "NEXT-SESSION-PROMPT.md"):
        text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert len(text.splitlines()) <= 220, relative
        assert "model-v3.2-autonomous-review" in text, relative
        assert "3.2.0" in text and "frozen" in text.lower(), relative
        assert "results/runs/real-2021-2025-v32-frozen" in text, relative
        assert not any(phrase in text for phrase in SUPERSEDED_ACTIVE_PHRASES), relative


def test_memory_index_uses_current_git_and_contract_before_historical_sessions() -> None:
    index = (PROJECT_ROOT / "memory/INDEX.md").read_text(encoding="utf-8")
    assert "model-v3.2-autonomous-review" in index
    assert "contract=3.2.0 frozen" in index
    assert "claude_session_1.txt" in index
    assert "HISTORICAL / SUPERSEDED" in index
    assert "进度接管最高优先级" not in index


def test_former_current_handoffs_are_explicitly_historical() -> None:
    historical = (
        PROJECT_ROOT / "claude_session_1.txt",
        PROJECT_ROOT
        / "memory/sessions/2026-08-27/1519-Git基线推送与Claude优先级登记.md",
        PROJECT_ROOT
        / "memory/sessions/2026-08-27/1552-ChatGPT接管复核与方案讨论基线.md",
    )
    for path in historical:
        header = "\n".join(path.read_text(encoding="utf-8").splitlines()[:8])
        assert "HISTORICAL / SUPERSEDED" in header, path


def test_formal_v32_entrypoints_never_reference_legacy_annual_model() -> None:
    paths = [
        RESEARCH_ROOT / "scripts/run_all.py",
        *sorted((RESEARCH_ROOT / "scripts").glob("*v32*.py")),
        *sorted((RESEARCH_ROOT / "src").glob("v32*.py")),
        *sorted((PROJECT_ROOT / ".github/workflows").glob("v32-*.yml")),
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "run_annual_model" not in text, path
        assert "src.annual_modeling" not in text, path


def test_frozen_client_facing_artifacts_do_not_contain_v2_scheme_or_denominator() -> None:
    frozen = RESEARCH_ROOT / "results/runs/real-2021-2025-v32-frozen"
    files = [
        frozen / "manifest.json",
        frozen / "formal_result_notes.md",
        *sorted(frozen.glob("formal_matrix_*.csv")),
        *sorted(frozen.glob("formal_matrix_*.md")),
        *sorted(frozen.glob("rcap_*summary.csv")),
    ]
    forbidden = ("SCHEME_C0", "SCHEME_A", "SCHEME_B", "固定干预前分母")
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden), path
