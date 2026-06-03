#!/usr/bin/env python3
"""Safely apply a reviewed Emily Job Search controller decision packet.

This intentionally does *not* search the web or make fit judgments. The agent
still owns judgement; this script owns the brittle mechanical Obsidian edits:

- Role State Ledger table upserts
- Live Role Shortlist table upserts/removals
- Role Removal Log appends when supplied
- Refresh Delta Log dated entry insert/replace
- Local Market Coverage Map targeted status/company/table updates
- Daily Refresh Control Packet current live table and snapshot/local bullets

Default mode is dry-run. Use --apply only after reviewing the diff. Every apply
creates timestamped backups of changed files.
"""
from __future__ import annotations

import argparse
import copy
import csv
import datetime as dt
import difflib
import io
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
VAULT = Path("/mnt/c/Users/Jaret/Obsidian/The Nexus")
PROJECT = VAULT / "40 Agent Nexus/Projects/Emily Job Search"

FILES = {
    "ledger": PROJECT / "Role State Ledger.md",
    "shortlist": PROJECT / "Live Role Shortlist.md",
    "removal": PROJECT / "Role Removal Log.md",
    "delta": PROJECT / "Refresh Delta Log.md",
    "local": PROJECT / "Local Market Coverage Map.md",
    "packet": PROJECT / "Daily Refresh Control Packet.md",
}

LIVE_STATES = {"new", "active", "aging"}
REMOVED_STATES = {"closed", "stale", "disqualified", "applied", "ignored", "archived"}


class DecisionError(ValueError):
    pass


def today_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise DecisionError("decision packet must be a JSON object")
    return data


def normalize_title(title: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def strip_md_link(value: str | None) -> str:
    text = (value or "").strip()
    if text.startswith("<") and text.endswith(">"):
        return text[1:-1]
    m = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", text)
    if m:
        return m.group(1)
    return text


def normalize_url(url: str | None) -> str:
    raw = strip_md_link(url)
    if not raw:
        return ""
    return raw.split("?")[0].rstrip("/").lower()


def row_key(row: dict[str, str]) -> tuple[str, str]:
    company = row.get("Company", row.get("company", ""))
    title = row.get("Title", row.get("title", ""))
    return company.lower().strip(), normalize_title(title)


def role_key(role: dict[str, Any]) -> tuple[str, str]:
    return str(role.get("company", "")).lower().strip(), normalize_title(str(role.get("title", "")))


def split_md_row(line: str) -> list[str]:
    raw = line.strip().strip("|")
    return [c.strip() for c in next(csv.reader(io.StringIO(raw), delimiter="|", escapechar="\\"))]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.strip()) for c in cells)


def clean_cell(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("\n", " ").strip()
    return text.replace("|", "/")


def md_url(url: str | None) -> str:
    raw = strip_md_link(url)
    if not raw:
        return ""
    if raw.startswith("http://") or raw.startswith("https://"):
        return f"<{raw}>"
    return raw


def md_row(row: dict[str, Any], headers: list[str]) -> str:
    return "| " + " | ".join(clean_cell(row.get(h, "")) for h in headers) + " |"


@dataclass
class MarkdownTable:
    heading: str
    headers: list[str]
    separator: str
    rows: list[dict[str, str]]
    before: str
    after: str
    prefix: str
    suffix: str

    def render(self) -> str:
        body = self.before
        if body and not body.endswith("\n"):
            body += "\n"
        body += "| " + " | ".join(self.headers) + " |\n"
        body += self.separator.rstrip() + "\n"
        for row in self.rows:
            body += md_row(row, self.headers) + "\n"
        if self.after:
            if not body.endswith("\n\n"):
                body = body.rstrip("\n") + "\n\n"
            body += self.after.lstrip("\n")
        if self.suffix and not body.endswith("\n\n"):
            body = body.rstrip("\n") + "\n\n"
        return self.prefix + body + self.suffix.lstrip("\n")


def section_end_after(text: str, start: int) -> int:
    """Find the end of a level-2 section, preserving final tag lines."""
    candidates: list[int] = []
    for pattern in (r"(?m)^## ", r"(?m)^#[A-Za-z0-9_-]+"):
        m = re.search(pattern, text[start:])
        if m:
            candidates.append(start + m.start())
    return min(candidates) if candidates else len(text)


def extract_table(text: str, heading: str, required_headers: list[str]) -> MarkdownTable:
    m = re.search(rf"(?m)^## {re.escape(heading)}\s*$", text)
    if not m:
        raise DecisionError(f"missing heading ## {heading}")
    section_end = section_end_after(text, m.end())
    prefix = text[: m.end()] + "\n"
    section = text[m.end() : section_end]
    suffix = text[section_end:]

    lines = section.splitlines()
    header_idx = None
    headers: list[str] = []
    for i, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        cells = split_md_row(line)
        if all(h in cells for h in required_headers):
            header_idx = i
            headers = cells
            break
    if header_idx is None:
        raise DecisionError(f"missing table under ## {heading}")
    if header_idx + 1 >= len(lines):
        raise DecisionError(f"table under ## {heading} has no separator")
    sep_line = lines[header_idx + 1]
    if not is_separator(split_md_row(sep_line)):
        raise DecisionError(f"table under ## {heading} has invalid separator")

    before = "\n".join(lines[:header_idx]).strip("\n")
    table_tail = lines[header_idx + 2 :]
    rows: list[dict[str, str]] = []
    after_lines: list[str] = []
    in_after = False
    for line in table_tail:
        if line.strip().startswith("|") and not in_after:
            cells = split_md_row(line)
            if len(cells) < len(headers):
                cells += [""] * (len(headers) - len(cells))
            rows.append({headers[i]: cells[i] for i in range(len(headers))})
        elif not line.strip() and not in_after:
            continue
        else:
            in_after = True
            after_lines.append(line)
    after = "\n".join(after_lines).strip("\n")
    return MarkdownTable(heading, headers, sep_line, rows, before, after, prefix, suffix)


def replace_section_body(text: str, heading: str, body: str) -> str:
    m = re.search(rf"(?m)^## {re.escape(heading)}\s*$", text)
    if not m:
        raise DecisionError(f"missing heading ## {heading}")
    section_end = section_end_after(text, m.end())
    if not body.startswith("\n"):
        body = "\n" + body
    if not body.endswith("\n\n"):
        body = body.rstrip("\n") + "\n\n"
    return text[: m.end()] + body + text[section_end:].lstrip("\n")


def find_existing_index(rows: list[dict[str, str]], role: dict[str, Any], url_header: str) -> int | None:
    target_url = normalize_url(str(role.get("canonical_url") or role.get("url") or ""))
    target_key = role_key(role)
    if url_header:
        for i, row in enumerate(rows):
            if target_url and normalize_url(row.get(url_header, "")) == target_url:
                return i
    for i, row in enumerate(rows):
        if row_key(row) == target_key:
            return i
    return None


def upsert_ledger(text: str, decision: dict[str, Any]) -> str:
    table = extract_table(text, "Ledger", ["Company", "Title", "Current state", "Canonical URL"])
    for role in decision.get("roles", []):
        if role.get("ledger", True) is False:
            continue
        idx = find_existing_index(table.rows, role, "Canonical URL")
        existing = copy.deepcopy(table.rows[idx]) if idx is not None else {h: "" for h in table.headers}
        existing.update(
            {
                "Company": role.get("company", existing.get("Company", "")),
                "Title": role.get("title", existing.get("Title", "")),
                "Current state": role.get("state", existing.get("Current state", "")),
                "Current rank": "" if role.get("rank") in (None, "") else str(role.get("rank")),
                "Score": "" if role.get("score") in (None, "") else str(role.get("score")),
                "Last confirmed live": role.get("last_confirmed_live", existing.get("Last confirmed live", "")),
                "Last reviewed": role.get("last_reviewed", decision.get("date", existing.get("Last reviewed", ""))),
                "Canonical URL": md_url(role.get("canonical_url", existing.get("Canonical URL", ""))),
                "Evidence note": role.get("evidence_note", existing.get("Evidence note", "")),
                "Notes": role.get("notes", existing.get("Notes", "")),
            }
        )
        if idx is None:
            table.rows.append(existing)
        else:
            table.rows[idx] = existing
    return table.render()


def upsert_shortlist(text: str, decision: dict[str, Any]) -> str:
    table = extract_table(text, "Current live set", ["Rank", "Score", "Company", "Title", "State", "Canonical link"])
    for role in decision.get("roles", []):
        state = str(role.get("state", "")).lower()
        idx = find_existing_index(table.rows, role, "Canonical link")
        include = bool(role.get("shortlist", state in LIVE_STATES)) and state in LIVE_STATES
        if not include:
            if idx is not None:
                del table.rows[idx]
            continue
        existing = copy.deepcopy(table.rows[idx]) if idx is not None else {h: "" for h in table.headers}
        existing.update(
            {
                "Rank": str(role.get("rank", existing.get("Rank", ""))),
                "Score": str(role.get("score", existing.get("Score", ""))),
                "Company": role.get("company", existing.get("Company", "")),
                "Title": role.get("title", existing.get("Title", "")),
                "State": role.get("state", existing.get("State", "")),
                "Work model": role.get("work_model", existing.get("Work model", "")),
                "Geography": role.get("geography", existing.get("Geography", "")),
                "Last confirmed live": role.get("last_confirmed_live", existing.get("Last confirmed live", "")),
                "Canonical link": md_url(role.get("canonical_url", existing.get("Canonical link", ""))),
                "Evidence": role.get("evidence_note", role.get("evidence", existing.get("Evidence", ""))),
            }
        )
        if idx is None:
            table.rows.append(existing)
        else:
            table.rows[idx] = existing
    table.rows.sort(key=lambda r: int(r.get("Rank") or 9999))
    return table.render()


def append_removals(text: str, decision: dict[str, Any]) -> str:
    removal_roles = [r for r in decision.get("roles", []) if r.get("removal")]
    if not removal_roles:
        return text
    table = extract_table(text, "Entries", ["Removal date", "Company", "Title", "New state"])
    for role in removal_roles:
        rem = role["removal"]
        row = {
            "Removal date": rem.get("date", decision.get("date", "")),
            "Company": role.get("company", ""),
            "Title": role.get("title", ""),
            "Previous rank": rem.get("previous_rank", role.get("previous_rank", "")),
            "Prior state": rem.get("prior_state", "active"),
            "New state": role.get("state", rem.get("new_state", "")),
            "Canonical URL": md_url(role.get("canonical_url", "")),
            "Removal reason": rem.get("reason", ""),
            "Evidence": rem.get("evidence", role.get("evidence_note", "")),
        }
        dup = any(
            existing.get("Removal date") == row["Removal date"]
            and row_key(existing) == row_key(row)
            and existing.get("New state") == row["New state"]
            for existing in table.rows
        )
        if not dup:
            table.rows.insert(0, row)
    return table.render()


def upsert_delta(text: str, decision: dict[str, Any]) -> str:
    entry = decision.get("delta_entry")
    if not entry:
        return text
    date = decision.get("date")
    if not date:
        raise DecisionError("date is required when delta_entry is supplied")
    entry = entry.strip()
    if not entry.startswith(f"### {date}"):
        raise DecisionError("delta_entry must start with the dated heading, e.g. ### YYYY-MM-DD — daily refresh")
    marker = "## Entries\n"
    if marker not in text:
        raise DecisionError("Refresh Delta Log is missing ## Entries")
    pattern = rf"(?ms)^### {re.escape(date)}[^\n]*\n.*?(?=^### \d{{4}}-\d{{2}}-\d{{2}}|\Z)"
    if re.search(pattern, text):
        return re.sub(pattern, entry + "\n\n", text, count=1)
    return text.replace(marker, marker + entry + "\n\n", 1)


def upsert_local_map(text: str, decision: dict[str, Any]) -> str:
    local = decision.get("local_market") or {}
    if not local:
        return text
    status_bullet = local.get("status_bullet")
    if status_bullet:
        body_match = re.search(r"(?ms)^## Current status\n(?P<body>.*?)(?=^## )", text)
        if not body_match:
            raise DecisionError("Local Market Coverage Map missing ## Current status")
        body = body_match.group("body")
        date = decision.get("date", "")
        same_date = rf"(?m)^- {re.escape(date)} [^\n]+(?:\n(?!- ).*)*"
        bullet = status_bullet.strip()
        if re.search(same_date, body):
            body = re.sub(same_date, bullet, body, count=1)
        elif bullet not in body:
            lines = body.splitlines()
            insert_at = min(2, len(lines))
            lines.insert(insert_at, bullet)
            body = "\n".join(lines) + "\n"
        text = text[: body_match.start("body")] + body + text[body_match.end("body") :]

    for company, line in (local.get("company_cluster_updates") or {}).items():
        pattern = rf"(?m)^- {re.escape(company)} \([^\n]*\)$"
        replacement = line.strip()
        if not replacement.startswith(f"- {company} "):
            raise DecisionError(f"company_cluster_updates[{company}] must be the full bullet line")
        if re.search(pattern, text):
            text = re.sub(pattern, replacement, text, count=1)
        else:
            raise DecisionError(f"could not find company cluster bullet for {company}")

    live_rows = local.get("validated_local_live_roles") or []
    if live_rows:
        table = extract_table(text, "Validated local live roles", ["Company", "Title", "Status"])
        for row_in in live_rows:
            idx = find_existing_index(table.rows, row_in, "")
            row = {
                "Company": row_in.get("company", ""),
                "Title": row_in.get("title", ""),
                "Geography / work model": row_in.get("geography_work_model", ""),
                "Comp signal": row_in.get("comp_signal", ""),
                "Status": row_in.get("status", "live"),
                "Notes": row_in.get("notes", ""),
            }
            if idx is None:
                table.rows.append(row)
            else:
                table.rows[idx] = row
        text = table.render()
    return text


def update_control_packet(text: str, shortlist_text: str, decision: dict[str, Any]) -> str:
    shortlist = extract_table(shortlist_text, "Current live set", ["Rank", "Score", "Company", "Title", "State", "Canonical link"])
    lines = [
        "| Rank | Score | Company | Title | State | Work model | Geography | Last confirmed | Link |",
        "| ---: | ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in shortlist.rows:
        lines.append(
            md_row(
                {
                    "Rank": row.get("Rank", ""),
                    "Score": row.get("Score", ""),
                    "Company": row.get("Company", ""),
                    "Title": row.get("Title", ""),
                    "State": row.get("State", ""),
                    "Work model": row.get("Work model", ""),
                    "Geography": row.get("Geography", ""),
                    "Last confirmed": row.get("Last confirmed live", ""),
                    "Link": row.get("Canonical link", ""),
                },
                ["Rank", "Score", "Company", "Title", "State", "Work model", "Geography", "Last confirmed", "Link"],
            )
        )
    text = replace_section_body(text, "Current live monitored set", "\n".join(lines) + "\n")

    packet = decision.get("control_packet") or {}
    if packet.get("local_market_state"):
        bullets = packet["local_market_state"]
        if isinstance(bullets, list):
            body = "\n".join(b.strip() for b in bullets) + "\n"
        else:
            body = str(bullets).strip() + "\n"
        text = replace_section_body(text, "Current local-market state", body)
    if packet.get("last_refresh_snapshot"):
        snapshot = packet["last_refresh_snapshot"]
        if isinstance(snapshot, list):
            body = "\n".join(s.strip() for s in snapshot) + "\n"
        else:
            body = str(snapshot).strip() + "\n"
        text = replace_section_body(text, "Last refresh snapshot", body)
    return text


def validate_decision(decision: dict[str, Any]) -> None:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(decision.get("date", ""))):
        raise DecisionError("decision.date must be YYYY-MM-DD")
    if not isinstance(decision.get("roles", []), list):
        raise DecisionError("decision.roles must be a list")
    for i, role in enumerate(decision.get("roles", [])):
        for field in ("company", "title", "state"):
            if not role.get(field):
                raise DecisionError(f"roles[{i}].{field} is required")
        state = str(role["state"]).lower()
        if state in LIVE_STATES and role.get("shortlist", True):
            for field in ("rank", "score", "work_model", "geography", "last_confirmed_live", "canonical_url"):
                if role.get(field) in (None, ""):
                    raise DecisionError(f"live shortlist role {role['company']} — {role['title']} missing {field}")
        if state in REMOVED_STATES and role.get("shortlist") is True:
            raise DecisionError(f"removed role {role['company']} — {role['title']} cannot have shortlist=true")


def apply_decision(decision: dict[str, Any], files: dict[str, Path]) -> dict[Path, str]:
    originals = {name: path.read_text(encoding="utf-8") for name, path in files.items()}
    updated = dict(originals)
    updated["ledger"] = upsert_ledger(updated["ledger"], decision)
    updated["shortlist"] = upsert_shortlist(updated["shortlist"], decision)
    updated["removal"] = append_removals(updated["removal"], decision)
    updated["delta"] = upsert_delta(updated["delta"], decision)
    updated["local"] = upsert_local_map(updated["local"], decision)
    updated["packet"] = update_control_packet(updated["packet"], updated["shortlist"], decision)
    return {files[name]: text for name, text in updated.items() if text != originals[name]}


def diff_for(path: Path, before: str, after: str) -> str:
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=str(path) + " (before)",
            tofile=str(path) + " (after)",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision", type=Path, required=True, help="Reviewed controller decision JSON")
    parser.add_argument("--apply", action="store_true", help="Write changes. Default is dry-run diff only.")
    parser.add_argument("--backup-dir", type=Path, default=REPO_ROOT / "data/emily-controller-backups")
    parser.add_argument("--project-dir", type=Path, default=PROJECT)
    args = parser.parse_args()

    files = dict(FILES)
    if args.project_dir != PROJECT:
        files = {name: args.project_dir / path.name for name, path in FILES.items()}

    decision = read_json(args.decision)
    validate_decision(decision)
    originals = {path: path.read_text(encoding="utf-8") for path in files.values()}
    changes = apply_decision(decision, files)

    if not changes:
        print(json.dumps({"status": "no_changes", "changed_files": []}, indent=2))
        return 0

    for path, after in changes.items():
        print(diff_for(path, originals[path], after))

    if args.apply:
        backup_root = args.backup_dir / today_stamp()
        backup_root.mkdir(parents=True, exist_ok=True)
        for path, after in changes.items():
            backup_path = backup_root / path.name
            shutil.copy2(path, backup_path)
            path.write_text(after, encoding="utf-8")
        print(json.dumps({"status": "applied", "changed_files": [str(p) for p in changes], "backup_dir": str(backup_root)}, indent=2))
    else:
        print(json.dumps({"status": "dry_run", "changed_files": [str(p) for p in changes], "hint": "rerun with --apply after reviewing diff"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
