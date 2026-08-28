from pathlib import Path

from scripts.plot_v32_formal_outputs import _plot_10kv_case_boundary


def test_10kv_case_boundary_figure_is_generated_as_a_code_only_schematic(
    tmp_path: Path,
) -> None:
    output = _plot_10kv_case_boundary(tmp_path, "DejaVu Sans")

    assert output == tmp_path / "10kv_local_case_boundary.png"
    assert output.is_file()
    assert output.stat().st_size > 0
