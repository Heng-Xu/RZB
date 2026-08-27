#!/usr/bin/env python3
"""Export local OpenAI Codex session transcripts to Markdown.

Python port of memory/codex.ps1 (Export-CodexChats.ps1) for Linux, where pwsh
is unavailable. Fully local: reads Codex JSONL session files from CODEX_HOME
(default ~/.codex); does not call Codex or any API.

Usage:
  ./codex_export.py                          # latest session only
  ./codex_export.py --all                    # all active sessions
  ./codex_export.py --days 31                # sessions updated in last 31 days (implies --all)
  ./codex_export.py --all --include-archived --backup-raw
  ./codex_export.py --input <rollout.jsonl>
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def get_codex_home() -> Path:
    import os
    home = os.environ.get("CODEX_HOME", "").strip()
    return Path(home) if home else Path.home() / ".codex"


def text_from_content(content) -> str:
    """Extract input_text/output_text/text items, joined by newline."""
    parts = []
    if not isinstance(content, list):
        return ""
    for item in content:
        if not isinstance(item, dict):
            continue
        if item.get("type") in ("input_text", "output_text", "text"):
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text)
    return "\n".join(parts)


def is_runtime_noise(text) -> bool:
    """Detect IDE/runtime-injected pseudo-user messages.

    Sessions recorded with disable_response_storage lack event_msg/user_message
    records, so user text falls back to response_item entries which can carry
    environment/instruction context the user never typed.
    """
    if not isinstance(text, str):
        return False
    stripped = text.lstrip()
    return (
        stripped.startswith("<environment_context>")
        or stripped.startswith("<user_instructions>")
        or stripped.startswith("<INSTRUCTIONS>")
        or stripped.startswith("# AGENTS.md instructions")
        or "<environment_context>" in text
        or "<turn_aborted>" in text
    )


def parse_session(path: Path):
    """Parse one rollout JSONL into (meta dict, messages list)."""
    records = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"警告: 跳过损坏的 JSON {path}:{lineno}", file=sys.stderr)

    if not records:
        print(f"警告: 无可读记录 {path}", file=sys.stderr)
        return None, None

    session_id = ""
    cwd = ""
    session_timestamp = ""

    for record in records:
        if record.get("type") == "session_meta":
            payload = record.get("payload") or {}
            session_id = str(payload.get("id") or payload.get("session_id") or "")
            cwd = str(payload.get("cwd") or "")
            session_timestamp = str(payload.get("timestamp") or "")
            if not session_timestamp and record.get("timestamp"):
                session_timestamp = str(record["timestamp"])
            break

    # Prefer event_msg/user_message: response_item/user may carry IDE/runtime
    # context the user never typed.
    has_user_events = any(
        r.get("type") == "event_msg"
        and isinstance(r.get("payload"), dict)
        and r["payload"].get("type") == "user_message"
        for r in records
    )
    has_assistant_responses = any(
        r.get("type") == "response_item"
        and isinstance(r.get("payload"), dict)
        and r["payload"].get("type") == "message"
        and r["payload"].get("role") == "assistant"
        for r in records
    )

    messages = []  # dicts: timestamp, role, text

    def add(ts, role, text):
        if isinstance(text, str) and text.strip() and not is_runtime_noise(text):
            messages.append({"timestamp": ts, "role": role, "text": text.strip()})

    for record in records:
        rtype = record.get("type", "")
        ts = str(record.get("timestamp") or "")
        payload = record.get("payload")

        if rtype == "event_msg" and isinstance(payload, dict):
            etype = payload.get("type", "")
            if etype == "user_message":
                add(ts, "用户", payload.get("message"))
            elif etype == "agent_message" and not has_assistant_responses:
                add(ts, "Codex", payload.get("message"))
            elif etype in ("thread_name_updated", "thread_title_updated"):
                pass  # handled below
        elif rtype == "response_item" and isinstance(payload, dict):
            if payload.get("type") != "message":
                continue
            role = payload.get("role", "")
            if role == "assistant" or (role == "user" and not has_user_events):
                add(ts, "Codex" if role == "assistant" else "用户",
                    text_from_content(payload.get("content")))

    # Thread title from name-update events.
    thread_title = ""
    for record in records:
        if record.get("type") != "event_msg":
            continue
        payload = record.get("payload")
        if not isinstance(payload, dict):
            continue
        if payload.get("type") in ("thread_name_updated", "thread_title_updated"):
            for field in ("name", "title", "thread_name"):
                candidate = payload.get(field)
                if isinstance(candidate, str) and candidate.strip():
                    thread_title = candidate.strip()
                    break
            if thread_title:
                break

    # Drop exact adjacent duplicates from multiple Codex surfaces.
    deduped = []
    prev_key = None
    for msg in messages:
        key = f"{msg['role']}\n{msg['text']}"
        if key != prev_key:
            deduped.append(msg)
        prev_key = key

    if not thread_title:
        first_user = next((m for m in deduped if m["role"] == "用户"), None)
        if first_user:
            single = re.sub(r"\s+", " ", first_user["text"]).strip()
            thread_title = single[:60] + "…" if len(single) > 60 else single
    if not thread_title:
        thread_title = "Codex 会话"

    meta = {
        "session_id": session_id or path.stem,
        "cwd": cwd,
        "timestamp": session_timestamp,
        "title": thread_title,
    }
    return meta, deduped


def export_session(path: Path, out_dir: Path, backup_raw: bool) -> Path | None:
    meta, messages = parse_session(path)
    if meta is None:
        return None

    date_prefix = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d_%H%M%S")
    safe_id = re.sub(r"[/\\<>:\"|?*\x00-\x1f]", "_", f"{date_prefix}-{meta['session_id']}")
    out_path = out_dir / f"{safe_id}.md"

    lines = [f"# {meta['title']}", ""]
    lines.append(f"- 会话 ID：`{meta['session_id']}`")
    if meta["timestamp"]:
        lines.append(f"- 会话时间：{meta['timestamp']}")
    if meta["cwd"]:
        lines.append(f"- 工作目录：`{meta['cwd']}`")
    lines.append(f"- 原始文件：`{path}`")
    lines.append(f"- 导出时间：{datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %z')}")
    lines.extend(["", "---", ""])

    for msg in messages:
        heading = f"## {msg['role']}"
        if msg["timestamp"]:
            heading += f" · {msg['timestamp']}"
        lines.extend([heading, "", msg["text"], ""])

    out_path.write_text("\n".join(lines), encoding="utf-8")

    if backup_raw:
        raw_dir = out_dir / "raw-jsonl"
        raw_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, raw_dir / path.name)

    print(f"导出: {out_path}")
    return out_path


def collect_files(codex_home: Path, include_archived: bool) -> list[Path]:
    roots = []
    active = codex_home / "sessions"
    if active.is_dir():
        roots.append(active)
    if include_archived:
        archived = codex_home / "archived_sessions"
        if archived.is_dir():
            roots.append(archived)

    files = [p for root in roots for p in root.rglob("rollout-*.jsonl") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", help="导出指定的 rollout JSONL 文件（或包含它的目录）")
    parser.add_argument("--output", default="codex-export", help="输出目录（默认 ./codex-export）")
    parser.add_argument("--all", action="store_true", help="导出全部会话而非仅最新一个")
    parser.add_argument("--days", type=int, default=0,
                        help="只导出最近 N 天内更新的会话（隐含 --all）")
    parser.add_argument("--include-archived", action="store_true", help="同时扫描 archived_sessions")
    parser.add_argument("--backup-raw", action="store_true", help="同时复制原始 JSONL 到 raw-jsonl/")
    args = parser.parse_args()

    codex_home = get_codex_home()
    if not codex_home.is_dir():
        print(f"错误: 未找到 Codex 主目录 {codex_home}", file=sys.stderr)
        return 1

    if args.input:
        src = Path(args.input).expanduser().resolve()
        if not src.exists():
            print(f"错误: 输入路径不存在 {src}", file=sys.stderr)
            return 1
        files = sorted(src.rglob("*.jsonl") if src.is_dir() else [src],
                       key=lambda p: p.stat().st_mtime, reverse=True)
    else:
        files = collect_files(codex_home, args.include_archived)

    if args.days > 0:
        cutoff = datetime.now() - timedelta(days=args.days)
        files = [f for f in files if datetime.fromtimestamp(f.stat().st_mtime) >= cutoff]

    if not args.all and args.days <= 0:
        files = files[:1]

    if not files:
        print(f"错误: 在 {codex_home} 下未找到会话 JSONL 文件", file=sys.stderr)
        return 1

    out_dir = Path(args.output).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    exported = 0
    for f in files:
        try:
            if export_session(f, out_dir, args.backup_raw):
                exported += 1
        except Exception as exc:  # noqa: BLE001 - keep exporting remaining files
            print(f"警告: 导出失败 {f}: {exc}", file=sys.stderr)

    print()
    print(f"完成。共导出 {exported}/{len(files)} 个会话，输出目录: {out_dir.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
