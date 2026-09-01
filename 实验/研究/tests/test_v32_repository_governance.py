from __future__ import annotations

from pathlib import Path
import re

import yaml


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


def test_complete_memory_cannot_leave_old_governance_work_in_active_handoffs() -> None:
    current = (PROJECT_ROOT / "memory/current.md").read_text(encoding="utf-8")
    status = re.search(r"状态：`?([A-Z_]+)`?", current)
    assert status, "memory/current.md must expose a machine-readable status"
    if status.group(1) != "COMPLETE":
        return
    stale = (
        "本轮正在处理",
        "待完成",
        "正在处理契约逐时审批状态",
        "联合压力情景",
        "冻结复现",
    )
    for relative in ("prompt.md", "NEXT-SESSION-PROMPT.md"):
        text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert not any(phrase in text for phrase in stale), relative


def test_active_handoff_validation_sha_if_present_matches_current_memory() -> None:
    memory = (PROJECT_ROOT / "memory/current.md").read_text(encoding="utf-8")
    memory_shas = set(re.findall(r"(?i)\b[0-9a-f]{40}\b", memory))
    labels = r"(?:latest|full|完整|模型验证|validation)[^\n]{0,80}?SHA"
    for relative in ("prompt.md", "NEXT-SESSION-PROMPT.md"):
        text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        for line in text.splitlines():
            if re.search(labels, line, flags=re.IGNORECASE):
                shas = set(re.findall(r"(?i)\b[0-9a-f]{40}\b", line))
                assert shas <= memory_shas, relative


def test_active_handoffs_do_not_reintroduce_v31_core_definitions() -> None:
    forbidden = (
        "严格路径起点与不限制路径不同",
        "两路径累计年化成本只作各自口径下的结果，不作跨口径",
        "S0=2×P2021 为正式基线",
        "成本不可直接比较",
        "SCHEME_C0",
        "SCHEME_A",
        "SCHEME_B",
        "固定干预前分母",
    )
    for relative in ("prompt.md", "NEXT-SESSION-PROMPT.md"):
        text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert not any(phrase in text for phrase in forbidden), relative


def test_primary_policy_explicitly_disables_retirement_and_downsize_candidates() -> None:
    agents = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "v3.2 primary policy model 不启用减容或退役候选" in agents
    contract = yaml.safe_load(
        (RESEARCH_ROOT / "model_contract.yaml").read_text(encoding="utf-8")
    )
    assert contract["optimization"]["retirement_candidates_in_primary_policy_model"] is False


def test_secondary_standardized_benchmark_has_a_reproducible_isolated_artifact() -> None:
    contract = yaml.safe_load(
        (RESEARCH_ROOT / "model_contract.yaml").read_text(encoding="utf-8")
    )
    benchmark = contract["standardized_policy_benchmark"]
    if not benchmark.get("enabled"):
        return
    runner = RESEARCH_ROOT / "scripts/run_v32_secondary_standardized_benchmark.py"
    artifact = RESEARCH_ROOT / "results/runs/real-2021-2025-v32-secondary-standardized-benchmark"
    assert runner.is_file()
    manifest_path = artifact / "manifest.json"
    assert manifest_path.is_file()
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert manifest["role"] == "secondary_standardized_counterfactual_benchmark"
    assert manifest["primary_policy_model"] is False
    assert manifest["direct_client_cost_conclusion_allowed"] is False
    assert manifest["formula"] == "S_norm_0 = 2.0 * P_plus_2021"
    assert "formal_matrix_110kv.csv" not in manifest.get("files", {})


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


def test_active_report_sources_do_not_regress_to_superseded_model_language() -> None:
    chapter_root = PROJECT_ROOT / "研究报告/初稿/章节"
    files = sorted(chapter_root.glob("第*章_*.md"))
    forbidden = (
        "SCHEME_C0",
        "SCHEME_A",
        "SCHEME_B",
        "固定干预前分母",
        "成本不可直接比较",
        "正式结果同时保留折现率",
        "40 台主变对应的连续曲线",
        "反向扩容",
        "作为安全审查",
        "年度资产白名单",
        "质量门禁",
        "负荷 seed",
    )
    client_name_forbidden = (
        "墩集",
        "河湾",
        "王沟",
        "墩南",
        "河炮",
        "河东",
        "邳州",
        "睢宁",
        "新沂",
        "沛县",
        "丰县",
        "铜山",
        "贾汪",
    )
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden), path
        assert not any(token in text for token in client_name_forbidden), path


def test_report_chapters_are_synchronized_with_full_draft() -> None:
    chapter_root = PROJECT_ROOT / "研究报告/初稿/章节"
    full = (chapter_root / "研究报告全文初稿.md").read_text(encoding="utf-8")
    for path in sorted(chapter_root.glob("第*章_*.md")):
        assert path.read_text(encoding="utf-8").strip() in full, path


def test_report_discloses_joint_sensitivity_and_soc_record_granularity() -> None:
    chapter_root = PROJECT_ROOT / "研究报告/初稿/章节"
    chapter4 = (chapter_root / "第四章_基于实际工程的电网建设成本模型.md").read_text(
        encoding="utf-8"
    )
    chapter6 = (chapter_root / "第六章_典型案例验证.md").read_text(
        encoding="utf-8"
    )
    assert "17 个参数场景，其中 1 个为基准复现控制、16 个为敏感性扰动" in chapter4
    assert "6 个非笛卡尔联合压力场景" in chapter4
    assert "稳健近优下限仍分别为 2.5 和 2.3" in chapter4
    assert "10 个定向场景的结果均为 ROBUST" in chapter4
    assert "40 条站点—方案审计记录" in chapter6
    assert "7 个实际配置储能的站点—方案组合" in chapter6
    assert "61320 条逐时记录" in chapter6
