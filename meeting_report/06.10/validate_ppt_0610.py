from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "06.10"
PPT_PATH = REPORT_DIR / "battery_trajectory_group_meeting_20260610.pptx"
SUMMARY_PATH = REPORT_DIR / "ppt_generation_summary.json"

DATASETS = ("HUST", "XJTU", "MIT", "TJU")
WINDOWS = ("010", "020", "040", "080")
FULL_ROW_LABELS = {
    "Hybrid 主线",
    "LSTM",
    "LSTM-PINN",
    "xPatch-DT",
    "BatteryGPT",
}
ABLATION_ROW_LABELS = {"主线", "去 BV 损失"}
METRIC_KEYS = ("rmse_mean", "rmse_std", "mape_mean", "mape_std")
BEST_METRIC_KEYS = ("rmse_mean", "mape_mean")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_metric_cells(table: dict, *, expected_labels: set[str]) -> None:
    labels = {row["label"] for row in table["rows"]}
    require(labels == expected_labels, f"{table['dataset']} row labels mismatch: {labels}")
    for row in table["rows"]:
        require(set(row["metrics"]) == set(METRIC_KEYS), f"{table['dataset']} metric keys mismatch")
        for key in METRIC_KEYS:
            parts = row["metrics"][key]
            require(len(parts) == len(WINDOWS), f"{table['dataset']} {row['label']} {key} missing windows")
            for part in parts:
                require(part["text"] != "-", f"{table['dataset']} {row['label']} {key} has missing value")
                require(isinstance(part["best"], bool), f"{table['dataset']} {row['label']} {key} best flag invalid")
    for key in BEST_METRIC_KEYS:
        for idx, win in enumerate(WINDOWS):
            winners = [row["label"] for row in table["rows"] if row["metrics"][key][idx]["best"]]
            require(winners, f"{table['dataset']} {key} fixed{win} has no best marker")


def main() -> None:
    require(PPT_PATH.exists(), f"missing PPT: {PPT_PATH}")
    require(SUMMARY_PATH.exists(), f"missing summary: {SUMMARY_PATH}")

    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    require(summary["slides"] == 3, "summary slide count must be 3")
    prs = Presentation(PPT_PATH)
    require(len(prs.slides) == 3, "PPT slide count must be 3")

    require(set(summary["full_tables"]) == set(DATASETS), "full table datasets mismatch")
    require(set(summary["ablation_tables"]) == set(DATASETS), "ablation table datasets mismatch")

    for dataset in DATASETS:
        full_table = summary["full_tables"][dataset]
        ablation_table = summary["ablation_tables"][dataset]
        validate_metric_cells(full_table, expected_labels=FULL_ROW_LABELS)
        validate_metric_cells(ablation_table, expected_labels=ABLATION_ROW_LABELS)

    mit_sources = summary["full_tables"]["MIT"]["source_files"]
    require(
        "Four_models_20260605_seed_summary.csv" in mit_sources["LSTM"]["010"],
        "MIT fixed010 should come from 20260605 four-model summary",
    )
    require(
        "Four_models_20260606_seed_summary.csv" in mit_sources["LSTM"]["040"],
        "MIT fixed040 should come from 20260606 four-model summary",
    )
    require(summary["paper_outline"]["has_image_placeholder"], "paper outline slide must retain image placeholder")
    require("BV" in summary["paper_outline"]["summary_text"], "paper summary should mention BV")

    print("validate_ppt_0610: ok")


if __name__ == "__main__":
    main()
