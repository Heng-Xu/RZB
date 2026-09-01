from __future__ import annotations

from pathlib import Path


def test_legacy_annual_model_refuses_default_execution(monkeypatch, capsys) -> None:
    from scripts import run_annual_model

    called = False

    def fail_if_called(_years: list[int]) -> Path:
        nonlocal called
        called = True
        raise AssertionError("legacy build must not run without an explicit archive flag")

    monkeypatch.setattr(run_annual_model, "build_outputs", fail_if_called)
    assert run_annual_model.main([]) == 2
    assert called is False
    captured = capsys.readouterr()
    assert "legacy archive" in captured.err.lower()
    assert "--legacy-archive-only" in captured.err
