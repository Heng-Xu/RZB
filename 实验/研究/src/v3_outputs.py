"""v3 正式 CSV/Markdown/DOCX 产物和审查清单。"""
from __future__ import annotations

import hashlib
import json
import math
import re
import zipfile
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd


class V3OutputError(ValueError):
    """正式产物字段或发布门禁不满足。"""


MACHINE_COLUMNS = {
    "region_id",
    "source_ref",
    "source_version",
    "transformation",
    "scenario_id",
    "quality_flag",
    "source_sha256",
}

WORD_PATH_LABELS = {
    "PATH_ACTUAL_2021_2025": "2021—2025 实际（事实对照）",
    "PATH_OPT_CLR_UNBOUNDED": "不限制容载比优化",
    "PATH_OPT_CLR_LE_2": "控制容载比不超过 2.0 优化",
}

WORD_REQUIRED_DISPLAY_FIELDS = {
    "asset_scope_id",
    "evidence_grade",
    "recommended_clr_interval",
    "recommended_clr_center",
    "recommended_clr_interval_effective_samples",
    "recommended_clr_interval_method",
    "capacity_base_mva",
    "positive_peak_base_mw",
    "reverse_peak_base_mw",
    "strict_path_incremental_cost",
    "positive_capacity_gap_mw",
    "reverse_hosting_gap_mw",
    "positive_gap_device_count",
    "reverse_gap_device_count",
    "measure_trigger_constraint",
    "recommended_measure",
}

WORD_PATH_FIELDS = {
    f"{path_id}_{metric}"
    for path_id in WORD_PATH_LABELS
    for metric in ("clr_2025", "cumulative_eac")
}

WORD_DISPLAY_GROUPS: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    (
        "口径与推荐结论",
        (
            ("资产范围", "asset_scope_id"),
            ("证据等级", "evidence_grade"),
            ("推荐容载比区间", "recommended_clr_interval"),
            ("推荐容载比中心值", "recommended_clr_center"),
            ("措施触发约束", "measure_trigger_constraint"),
            ("推荐措施", "recommended_measure"),
        ),
    ),
    (
        "推荐区间依据",
        (
            ("推荐区间有效样本数", "recommended_clr_interval_effective_samples"),
            ("推荐区间形成方法", "recommended_clr_interval_method"),
        ),
    ),
    (
        "2025 年容载比",
        tuple(
            (f"2025 年容载比｜{WORD_PATH_LABELS[path_id]}", f"{path_id}_clr_2025")
            for path_id in WORD_PATH_LABELS
        ),
    ),
    (
        "累计年化成本",
        tuple(
            (f"累计年化成本｜{WORD_PATH_LABELS[path_id]}", f"{path_id}_cumulative_eac")
            for path_id in WORD_PATH_LABELS
        )
        + (("严格约束增量成本", "strict_path_incremental_cost"),),
    ),
    (
        "设备与负荷口径",
        (
            ("公用变容量（MVA）", "capacity_base_mva"),
            ("正向最大净负荷（MW）", "positive_peak_base_mw"),
            ("反向峰值（MW）", "reverse_peak_base_mw"),
        ),
    ),
    (
        "缺口与设备数",
        (
            ("正向容量缺口（MW）", "positive_capacity_gap_mw"),
            ("反向承载缺口（MW）", "reverse_hosting_gap_mw"),
            ("正向缺口设备数", "positive_gap_device_count"),
            ("反向缺口设备数", "reverse_gap_device_count"),
        ),
    ),
)

WORD_EVIDENCE_LABELS = {
    "EVIDENCE_A": "A 级",
    "EVIDENCE_B": "B 级",
    "EVIDENCE_C": "C 级",
}

WORD_MEASURE_LABELS = {
    "storage": "储能",
    "new_third_transformer": "新建第三台主变",
    "none": "无",
    "无": "无",
}

WORD_TRIGGER_LABELS = {
    "positive_capacity_gap": "正向容量缺口",
    "reverse_hosting_gap": "反向承载缺口",
    "none": "无缺口触发",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if bool(pd.isna(value)):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _format_word_value(field: str, value: Any) -> str:
    """按 v3 主表规则把矩阵字段转换为中文人工审查值。"""
    if value is None:
        return "未提供"
    try:
        if bool(pd.isna(value)):
            return "未提供"
    except (TypeError, ValueError):
        pass

    if isinstance(value, str):
        text = value.strip()
        if text == "未识别":
            return "未识别（设备动作成本未闭合）"
        if text in {"不可行", "未形成推荐", "未形成同步反向峰值", "未提供"}:
            return text
        if field == "evidence_grade":
            return WORD_EVIDENCE_LABELS.get(text, "证据缺口")
        if field == "asset_scope_id":
            return {"operating_2025": "2025 年运行口径"}.get(text, "范围：" + text)
        if field == "recommended_measure":
            labels: list[str] = []
            for item in re.split(r"[;,]", text):
                item = item.strip()
                if not item:
                    continue
                labels.append(WORD_MEASURE_LABELS.get(item, "未形成唯一推荐"))
            return "、".join(dict.fromkeys(labels)) or "未形成唯一推荐"
        if field == "measure_trigger_constraint":
            labels = [
                WORD_TRIGGER_LABELS.get(item.strip(), "数据证据不足")
                for item in text.split(";")
                if item.strip()
            ]
            return "、".join(dict.fromkeys(labels)) or "数据证据不足"
        if field == "recommended_clr_interval":
            return text.replace("-", "–")
        return text

    if field == "recommended_clr_interval_effective_samples" or field.endswith("_device_count"):
        return str(int(value))
    if field == "recommended_clr_center" or field.endswith("_clr_2025"):
        return f"{float(value):.3f}"
    if field.endswith("_cumulative_eac") or field == "strict_path_incremental_cost":
        return f"{float(value):,.2f}"
    if field.endswith("_gap_mw") or field in {"capacity_base_mva", "positive_peak_base_mw"}:
        return f"{float(value):,.2f}"
    return _text(value)


def _build_word_rows(matrix: pd.DataFrame, voltage: int) -> list[dict[str, Any]]:
    """构造固定行序的 Word 展示行，不依赖 DataFrame 列顺序。"""
    required = WORD_REQUIRED_DISPLAY_FIELDS | WORD_PATH_FIELDS
    missing = sorted(required - set(matrix.columns))
    if missing:
        raise V3OutputError(f"matrix missing Word display fields: {missing}")
    if set(matrix["voltage_kv"].astype(int)) != {int(voltage)}:
        raise V3OutputError(f"Word matrix voltage mismatch for {voltage} kV")
    if len(matrix) != 8 or matrix["region_id"].duplicated().any():
        raise V3OutputError("formal matrix must contain eight unique regions")

    normalized = matrix.copy()
    normalized["region_id"] = normalized["region_id"].astype(str)
    regions = sorted(normalized["region_id"].tolist())
    lookup = normalized.set_index("region_id").loc[regions]
    rows: list[dict[str, Any]] = [
        {
            "kind": "header",
            "field": None,
            "cells": ["指标", *[f"片区{index:02d}" for index in range(1, 9)]],
        }
    ]
    for group, fields in WORD_DISPLAY_GROUPS:
        rows.append({"kind": "group", "field": None, "cells": [group]})
        for label, field in fields:
            rows.append(
                {
                    "kind": "data",
                    "field": field,
                    "cells": [label]
                    + [_format_word_value(field, lookup.loc[region, field]) for region in regions],
                }
            )
    return rows


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def _run_xml(text: str, *, bold: bool = False, color: str = "404040", size: int = 18) -> str:
    font = (
        '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="宋体" '
        'w:cs="Arial"/>'
    )
    weight = '<w:b/><w:bCs/>' if bold else ""
    return (
        f"<w:r><w:rPr>{font}{weight}<w:color w:val=\"{color}\"/>"
        f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr>'
        f'<w:t xml:space="preserve">{escape(str(text))}</w:t></w:r>'
    )


def _paragraph_xml(
    text: str,
    *,
    style: str = "Normal",
    align: str | None = None,
    bold: bool = False,
    color: str = "404040",
    size: int = 18,
    space_after: int = 80,
) -> str:
    alignment = f'<w:jc w:val="{align}"/>' if align else ""
    return (
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/><w:spacing w:after="{space_after}"/>'
        f"{alignment}</w:pPr>{_run_xml(text, bold=bold, color=color, size=size)}</w:p>"
    )


def _cell_shading(kind: str, field: str | None, text: str, first_col: bool) -> tuple[str, str]:
    if kind == "header":
        return "1F4E78", "FFFFFF"
    if kind == "group":
        return "5B9BD5", "FFFFFF"
    if first_col:
        return "F2F2F2", "17365D"
    if text in {"不可行", "未形成唯一推荐", "未形成推荐", "未提供"}:
        return "FCE4D6", "9C0006"
    if text == "未识别（设备动作成本未闭合）" or text == "未形成同步反向峰值":
        return "FFF2CC", "7F6000"
    if field == "evidence_grade" and text == "C 级":
        return "FCE4D6", "9C0006"
    if field and ("PATH_OPT_CLR_LE_2" in field or field == "strict_path_incremental_cost"):
        return "FFF2CC", "7F6000"
    if field in {"recommended_clr_interval", "recommended_clr_center", "recommended_measure"}:
        return "E2F0D9", "375623"
    return "FFFFFF", "404040"


def _table_cell_xml(
    text: str,
    *,
    width: int,
    kind: str,
    field: str | None,
    first_col: bool,
) -> str:
    fill, color = _cell_shading(kind, field, text, first_col)
    bold = kind in {"header", "group"} or first_col
    size = 17 if kind == "group" else 16
    return (
        f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>'
        f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
        '<w:vAlign w:val="center"/></w:tcPr>'
        f'<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:after="0"/></w:pPr>'
        f"{_run_xml(text, bold=bold, color=color, size=size)}</w:p></w:tc>"
    )


def _table_row_xml(row: dict[str, Any], widths: list[int]) -> str:
    kind = str(row["kind"])
    cells: list[str] = row["cells"]
    if kind == "group":
        group_text = str(cells[0])
        total_width = sum(widths)
        cell = (
            f'<w:tc><w:tcPr><w:tcW w:w="{total_width}" w:type="dxa"/>'
            '<w:gridSpan w:val="9"/><w:shd w:val="clear" w:color="auto" w:fill="5B9BD5"/>'
            '<w:vAlign w:val="center"/></w:tcPr>'
            f'<w:p><w:pPr><w:jc w:val="left"/><w:spacing w:after="0"/></w:pPr>'
            f'{_run_xml(group_text, bold=True, color="FFFFFF", size=17)}</w:p></w:tc>'
        )
        return f'<w:tr><w:trPr><w:cantSplit/></w:trPr>{cell}</w:tr>'

    row_properties = '<w:trPr><w:cantSplit/>'
    if kind == "header":
        row_properties += "<w:tblHeader/>"
    row_properties += "</w:trPr>"
    rendered = "".join(
        _table_cell_xml(
            str(text),
            width=widths[index],
            kind=kind,
            field=row.get("field"),
            first_col=index == 0,
        )
        for index, text in enumerate(cells)
    )
    return f"<w:tr>{row_properties}{rendered}</w:tr>"


def _table_xml(rows: list[dict[str, Any]]) -> str:
    widths = [3100] + [1547] * 8
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for width in widths)
    borders = (
        '<w:tblBorders><w:top w:val="single" w:sz="4" w:color="B4C7E7"/>'
        '<w:left w:val="single" w:sz="4" w:color="B4C7E7"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="B4C7E7"/>'
        '<w:right w:val="single" w:sz="4" w:color="B4C7E7"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="D9E2F3"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="D9E2F3"/></w:tblBorders>'
    )
    table_rows = "".join(_table_row_xml(row, widths) for row in rows)
    return (
        '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblLayout w:type="fixed"/>'
        f"{borders}</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{table_rows}</w:tbl>"
    )


def _document_xml(title: str, rows: list[dict[str, Any]], voltage: int) -> str:
    note = (
        "说明：110 kV 为正式推荐矩阵；Word 为人工审查层，精确查值以同目录 CSV/Markdown 为准。"
        if voltage == 110
        else "说明：35 kV 为辅助分析矩阵，不替代 110 kV 正式推荐；严格路径不可行的片区不形成正式唯一推荐。"
    )
    subtitle = "8 片区｜2021 年共同基准｜2022—2025 年决策期｜2025 年价格口径"
    footnotes = [
        "注：正式容载比只使用同电压等级公用变容量除以该路径、该年度同步正向最大净负荷；反向峰值和反向承载力单列。",
        "注：推荐区间来自不限制容载比成本最小可行结果及已验证敏感性结果；“未识别”不等于 0，“不可行”不等于缺失。",
        "注：数据映射、异常值、历史范围、成本闭合和跨年光伏快照见“实验/研究/分析/v3真实数据问题补充说明_供甲方汇报.md”。",
    ]
    paragraphs = (
        _paragraph_xml(title, style="Title", align="center", bold=True, color="17365D", size=32, space_after=100)
        + _paragraph_xml(subtitle, align="center", color="404040", size=17, space_after=100)
        + _paragraph_xml(note, align="left", color="7F6000" if voltage == 35 else "404040", size=17, space_after=150)
    )
    postscript = "".join(_paragraph_xml(text, color="595959", size=15, space_after=45) for text in footnotes)
    section = (
        '<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter"/>'
        '<w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/>'
        '<w:pgMar w:top="709" w:right="680" w:bottom="709" w:left="680"/>'
        '<w:cols w:num="1"/></w:sectPr>'
    )
    return (
        f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}"><w:body>{paragraphs}'
        f"{_table_xml(rows)}{postscript}{section}</w:body></w:document>"
    )


def _styles_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W_NS}">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="宋体"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:rPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="80"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:qFormat/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="黑体"/><w:b/><w:color w:val="17365D"/><w:sz w:val="32"/></w:rPr></w:style>
  <w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:basedOn w:val="Normal"/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:color="B4C7E7"/><w:left w:val="single" w:sz="4" w:color="B4C7E7"/><w:bottom w:val="single" w:sz="4" w:color="B4C7E7"/><w:right w:val="single" w:sz="4" w:color="B4C7E7"/><w:insideH w:val="single" w:sz="4" w:color="D9E2F3"/><w:insideV w:val="single" w:sz="4" w:color="D9E2F3"/></w:tblBorders></w:tblPr></w:style>
</w:styles>'''


def _footer_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="{W_NS}">
  <w:p><w:pPr><w:jc w:val="center"/></w:pPr>{_run_xml("v3 真实数据｜Word 人工审查层｜精确查值以同目录 CSV 为准｜第 ", color="808080", size=14)}<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>
</w:ftr>'''


def _content_types_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="{CONTENT_TYPES_NS}">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
</Types>'''


def _root_relationships_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_REL_NS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''


def _document_relationships_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_REL_NS}">
  <Relationship Id="rIdFooter" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
</Relationships>'''


def write_transposed_word_matrix(matrix: pd.DataFrame, path: Path, *, title: str) -> None:
    """写入第一列为指标、后续列为脱敏片区的转置式 DOCX。"""
    required = {"region_id", "voltage_kv"}
    if not required <= set(matrix.columns):
        raise V3OutputError(f"matrix missing {sorted(required - set(matrix.columns))}")
    voltage = int(matrix["voltage_kv"].iloc[0])
    rows = _build_word_rows(matrix, voltage)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml())
        archive.writestr("_rels/.rels", _root_relationships_xml())
        archive.writestr("word/document.xml", _document_xml(title, rows, voltage))
        archive.writestr("word/styles.xml", _styles_xml())
        archive.writestr("word/footer1.xml", _footer_xml())
        archive.writestr("word/_rels/document.xml.rels", _document_relationships_xml())


def _write_csv(path: Path, frame: pd.DataFrame) -> None:
    if frame.empty:
        raise V3OutputError(f"refusing to publish empty output: {path.name}")
    frame.to_csv(path, index=False, lineterminator="\n", float_format="%.10g")


def build_v3_artifacts(
    output_dir: Path,
    matrix_110: pd.DataFrame,
    matrix_35: pd.DataFrame,
    path_year_results: pd.DataFrame,
    path_action_results: pd.DataFrame,
    path_cost_breakdown: pd.DataFrame,
    contract_path: Path,
    *,
    problem_log: str = "",
    network_check: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """生成两套矩阵、Word、技术附表、问题台账和发布 manifest。"""
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for matrix, voltage in ((matrix_110, 110), (matrix_35, 35)):
        if set(matrix["voltage_kv"].astype(int)) != {voltage}:
            raise V3OutputError(f"matrix voltage mismatch for {voltage} kV")
        if len(matrix) != 8:
            raise V3OutputError(f"{voltage} kV matrix must contain eight regions")
    _write_csv(output_dir / "county_110_recommendation_matrix.csv", matrix_110)
    _write_csv(output_dir / "county_35_recommendation_matrix.csv", matrix_35)
    write_transposed_word_matrix(matrix_110, output_dir / "county_110_recommendation_matrix.docx", title="110 kV 县区正式推荐矩阵")
    write_transposed_word_matrix(matrix_35, output_dir / "county_35_recommendation_matrix.docx", title="35 kV 县区辅助矩阵")
    _write_csv(output_dir / "path_year_results.csv", path_year_results)
    _write_csv(output_dir / "path_action_results.csv", path_action_results if not path_action_results.empty else pd.DataFrame({"status": ["no_action"]}))
    _write_csv(output_dir / "path_cost_breakdown.csv", path_cost_breakdown)
    qx = path_year_results[path_year_results.get("region_id", pd.Series(dtype=str)).astype(str).eq("QX-00005")].copy()
    if qx.empty:
        qx = pd.DataFrame([{"region_id": "QX-00005", "status": "not_available"}])
    _write_csv(output_dir / "qx00005_path_validation.csv", qx)
    if network_check is None:
        network_check = pd.DataFrame(
            [
                {
                    "scope": "110/35 kV internal capacity network screen",
                    "status": "not_run_in_output_builder",
                    "method": "capacity_network_contingency_screen",
                    "precise_ac_or_dc_claim": False,
                    "visible_in_client_matrix": False,
                }
            ]
        )
    _write_csv(output_dir / "内部容量网络压力检查.csv", network_check)
    (output_dir / "问题台账.md").write_text(
        "# v3 问题与修正台账\n\n" + (problem_log or "无新增问题。") + "\n",
        encoding="utf-8",
    )
    output_files = {
        path.name: {"sha256": _sha256(path), "bytes": path.stat().st_size}
        for path in sorted(output_dir.iterdir(), key=lambda item: item.name)
        if path.is_file() and path.name != "manifest.json"
    }
    manifest = {
        "dataset_id": "real_2021_2025",
        "contract_version": "3.1.0",
        "contract_sha256": _sha256(Path(contract_path)),
        "formal_matrices": {"110kv_rows": 8, "35kv_rows": 8},
        "voltage_separation": True,
        "formal_paths": ["PATH_ACTUAL_2021_2025", "PATH_OPT_CLR_UNBOUNDED", "PATH_OPT_CLR_LE_2"],
        "word_presentation_version": "3.1",
        "word_presentation_spec": "docs/WORD-MATRIX-PRESENTATION-SPEC.md",
        "output_files": output_files,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def recommended_clr_interval(
    frontier: pd.DataFrame,
    *,
    region_id: str,
    near_optimal_band: float = 0.05,
) -> dict[str, Any]:
    """从弹性扫描前沿导出县区推荐容载比区间。

    规则（契约 ``elasticity_sweep.recommendation_rule``，继承 2026-08-09
    冻结方案）：仅取可行点；近优带为累计在役 EAC 不高于最低成本
    ``(1 + near_optimal_band)`` 的 Rcap 点集；带内储能柜数或扩容量不一致
    即视为措施翻转，只给区间不给精确值。
    """
    sub = frontier[frontier["region_id"].astype(str).eq(str(region_id)) & frontier["feasible"].astype(bool)]
    if sub.empty:
        return {
            "region_id": region_id,
            "interval_low": None,
            "interval_high": None,
            "point_estimate": None,
            "interval_only": True,
            "reason": "no_feasible_point",
        }
    numeric = sub[pd.to_numeric(sub["rcap"], errors="coerce").notna()].copy()
    numeric["rcap"] = pd.to_numeric(numeric["rcap"])
    costs = pd.to_numeric(numeric["cumulative_in_service_eac_wanyuan"], errors="coerce")
    valid = numeric[costs.notna()]
    if valid.empty:
        return {
            "region_id": region_id,
            "interval_low": None,
            "interval_high": None,
            "point_estimate": None,
            "interval_only": True,
            "reason": "no_numeric_cost",
        }
    costs = pd.to_numeric(valid["cumulative_in_service_eac_wanyuan"])
    best = float(costs.min())
    band = valid[costs <= best * (1.0 + near_optimal_band)]
    low = float(band["rcap"].min())
    high = float(band["rcap"].max())
    flipped = (
        pd.to_numeric(band["storage_modules"], errors="coerce").nunique() > 1
        or pd.to_numeric(band["expansion_mva"], errors="coerce").round(3).nunique() > 1
    )
    point = low if (low == high and not flipped) else None
    return {
        "region_id": region_id,
        "interval_low": low,
        "interval_high": high,
        "point_estimate": point,
        "interval_only": bool(point is None),
        "near_optimal_rcap_points": sorted(float(value) for value in band["rcap"]),
        "best_rcap": float(valid.loc[costs.idxmin(), "rcap"]),
        "unbounded_feasible": bool(sub["rcap"].astype(str).eq("unbounded").any()),
    }
