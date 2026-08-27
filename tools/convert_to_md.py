#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通用文档转Markdown工具。支持 PDF / DOCX / DOC → .md

用法：
    python tools/convert_to_md.py --input <源目录> --output <输出目录>
    python tools/convert_to_md.py --input 参考文献/ --output 分析/md_cache/参考文献/ --force
    python tools/convert_to_md.py --input 课题前期资料/ --output 分析/md_cache/课题前期资料/

转换策略：
  PDF  → PyMuPDF（主）→ pdfplumber（备）
  DOCX → python-docx（保留标题层级 + 表格）
  DOC  → libreoffice --headless 先转 DOCX，再走 DOCX 路径
  CEB  → 跳过（超星专有格式，无开源工具）
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Optional

SUPPORTED_EXTS = {".pdf", ".docx", ".doc"}
SKIP_EXTS = {".ceb", ".xlsx", ".xls"}


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ── PDF ──────────────────────────────────────────────────────────────────────

def _pdf_pymupdf(pdf_path: Path) -> tuple[Optional[str], int]:
    try:
        import fitz
    except ImportError:
        return None, 0
    try:
        doc = fitz.open(pdf_path)
        try:
            n = len(doc)
            blocks = []
            for i in range(n):
                text = doc[i].get_text("text") or ""
                blocks.append(f"\n\n<!-- page {i+1}/{n} -->\n\n{text.rstrip()}\n")
            return "\n".join(blocks).strip() + "\n", n
        finally:
            doc.close()
    except Exception as e:
        print(f"[WARN] pymupdf 失败 {pdf_path.name}: {e}", file=sys.stderr)
        return None, 0


def _pdf_pdfplumber(pdf_path: Path) -> tuple[Optional[str], int]:
    try:
        import pdfplumber
    except ImportError:
        return None, 0
    try:
        blocks = []
        with pdfplumber.open(pdf_path) as pdf:
            n = len(pdf.pages)
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                blocks.append(f"\n\n<!-- page {i}/{n} -->\n\n{text.rstrip()}\n")
        return "\n".join(blocks).strip() + "\n", n
    except Exception as e:
        print(f"[WARN] pdfplumber 失败 {pdf_path.name}: {e}", file=sys.stderr)
        return None, 0


def convert_pdf(path: Path) -> tuple[Optional[str], int, str]:
    md, n = _pdf_pymupdf(path)
    if md and md.strip():
        return md, n, "pymupdf"
    md, n = _pdf_pdfplumber(path)
    if md and md.strip():
        return md, n, "pdfplumber"
    return None, 0, "failed"


# ── DOCX ─────────────────────────────────────────────────────────────────────

def _iter_block_items(parent):
    from docx.document import Document as _Document
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table, _Cell
    from docx.text.paragraph import Paragraph

    parent_elm = parent.element.body if isinstance(parent, _Document) else parent._tc
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def convert_docx(path: Path) -> tuple[Optional[str], int, str]:
    try:
        from docx import Document
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError:
        return None, 0, "failed"
    try:
        doc = Document(str(path))
        lines: list[str] = []
        para_count = 0
        for block in _iter_block_items(doc):
            if isinstance(block, Paragraph):
                text = (block.text or "").rstrip()
                if not text:
                    lines.append("")
                    continue
                sname = (block.style.name or "") if block.style else ""
                if sname.startswith("Heading 1") or sname == "Title":
                    lines.append(f"# {text}")
                elif sname.startswith("Heading 2"):
                    lines.append(f"## {text}")
                elif sname.startswith("Heading 3"):
                    lines.append(f"### {text}")
                elif sname.startswith("Heading 4"):
                    lines.append(f"#### {text}")
                elif sname.startswith("Heading"):
                    lines.append(f"##### {text}")
                else:
                    lines.append(text)
                para_count += 1
            elif isinstance(block, Table):
                lines.append("")
                rows = [[c.text.strip().replace("\n", " / ") for c in row.cells] for row in block.rows]
                if rows:
                    hdr = rows[0]
                    lines.append("| " + " | ".join(hdr) + " |")
                    lines.append("| " + " | ".join("---" for _ in hdr) + " |")
                    for row in rows[1:]:
                        row = (row + [""] * len(hdr))[:len(hdr)]
                        lines.append("| " + " | ".join(row) + " |")
                lines.append("")
        return "\n".join(lines).strip() + "\n", para_count, "python-docx"
    except Exception as e:
        print(f"[WARN] docx 失败 {path.name}: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return None, 0, "failed"


# ── DOC (via libreoffice) ─────────────────────────────────────────────────────

def convert_doc(path: Path) -> tuple[Optional[str], int, str]:
    lo = shutil.which("libreoffice") or shutil.which("soffice")
    if not lo:
        return None, 0, "failed-no-libreoffice"
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            result = subprocess.run(
                [lo, "--headless", "--convert-to", "docx", "--outdir", tmpdir, str(path)],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                print(f"[WARN] libreoffice 转换失败: {result.stderr[:200]}", file=sys.stderr)
                return None, 0, "failed-libreoffice"
            # 找到输出的 docx
            out_files = list(Path(tmpdir).glob("*.docx"))
            if not out_files:
                return None, 0, "failed-no-output"
            md, n, method = convert_docx(out_files[0])
            if md:
                return md, n, f"libreoffice+{method}"
            return None, 0, "failed"
        except subprocess.TimeoutExpired:
            return None, 0, "failed-timeout"
        except Exception as e:
            print(f"[WARN] doc 转换异常 {path.name}: {e}", file=sys.stderr)
            return None, 0, "failed"


# ── Orchestration ─────────────────────────────────────────────────────────────

def process_file(
    src: Path,
    out_path: Path,
    manifest: dict,
    src_key: str,
    force: bool,
    dry_run: bool,
) -> dict:
    sha = sha256_of_file(src)
    prior = manifest.get(src_key, {})
    if not force and prior.get("sha256") == sha and prior.get("ok") and out_path.exists():
        return {**prior, "status": "cached"}

    if dry_run:
        return {"source": src_key, "sha256": sha, "status": "pending"}

    ext = src.suffix.lower()
    if ext == ".pdf":
        md, n, method = convert_pdf(src)
        n_key = "pages"
    elif ext == ".docx":
        md, n, method = convert_docx(src)
        n_key = "paragraphs"
    elif ext == ".doc":
        md, n, method = convert_doc(src)
        n_key = "paragraphs"
    else:
        return {"source": src_key, "status": "skipped", "reason": ext}

    record: dict = {
        "source": src_key,
        "output": str(out_path),
        "sha256": sha,
        "method": method,
        n_key: n,
        "ok": False,
        "status": "",
    }

    if not md or not md.strip():
        record["status"] = "failed"
        return record

    header = (
        f"<!--\nsource: {src_key}\nsha256: {sha}\nmethod: {method}\n{n_key}: {n}\n-->\n\n"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(header + md, encoding="utf-8")
    record["ok"] = True
    record["status"] = "converted"
    record["bytes"] = out_path.stat().st_size
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="批量转换文档为Markdown")
    parser.add_argument("--input", required=True, help="源目录（递归扫描）")
    parser.add_argument("--output", required=True, help="输出目录（镜像结构）")
    parser.add_argument("--force", action="store_true", help="忽略缓存强制重转")
    parser.add_argument("--dry-run", action="store_true", help="只列出将要做的事")
    args = parser.parse_args()

    input_dir = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()
    manifest_path = output_dir / "_manifest.json"

    if not input_dir.exists():
        print(f"[ERROR] 源目录不存在: {input_dir}", file=sys.stderr)
        return 1

    sources = sorted(
        p for p in input_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    )
    skipped_exts = sorted(
        p for p in input_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SKIP_EXTS
    )

    if not sources:
        print(f"[WARN] 未找到可转换文件（{input_dir}）")
        for p in skipped_exts:
            print(f"  跳过(不支持): {p.name}")
        return 0

    print(f"[INFO] 发现 {len(sources)} 个可转换文件，{len(skipped_exts)} 个跳过")
    for p in skipped_exts:
        print(f"  [跳过] {p.name} ({p.suffix})")

    manifest: dict = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    n_converted = n_cached = n_failed = 0
    results: dict = {}

    for i, src in enumerate(sources, 1):
        rel = str(src.relative_to(input_dir))
        out_path = (output_dir / rel).with_suffix(".md")
        print(f"[{i:02d}/{len(sources)}] {src.name}")
        try:
            rec = process_file(src, out_path, manifest, rel, args.force, args.dry_run)
        except Exception as e:
            rec = {"source": rel, "status": "exception", "error": str(e), "ok": False}
            traceback.print_exc()

        results[rel] = rec
        manifest[rel] = {k: v for k, v in rec.items() if k != "status"}
        status = rec.get("status", "?")
        if status == "converted":
            n_converted += 1
            print(f"       -> {rec.get('method')} OK ({rec.get('pages', rec.get('paragraphs', '?'))})")
        elif status == "cached":
            n_cached += 1
            print(f"       -> cached")
        elif status == "pending":
            print(f"       -> (dry-run)")
        else:
            n_failed += 1
            print(f"       -> {status}")

    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    print(f"\n[DONE] converted={n_converted} cached={n_cached} failed={n_failed} total={len(sources)}")
    return 0 if n_failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
