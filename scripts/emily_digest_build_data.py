from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote

import yaml

SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
SUBSECTION_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
ROLE_HEADING_RE = re.compile(r"^###\s+(\d+)\)\s+\[(.*?)\s+—\s+(.*?)\]\((.*?)\)\s*$", re.MULTILINE)
ROLE_BLOCK_HEADING_RE = re.compile(r"^##\s+(\d+)\)\s+\[(.*?)\s+—\s+(.*?)\]\((.*?)\)\s*$", re.MULTILINE)
FIELD_LINE_RE = re.compile(r"^-\s+\*\*(.+?)\*\*\s*(.*)$")
SCORE_LINE_RE = re.compile(r"^-\s+(.*?):\s*(\d+)/(\d+)\s+—\s+(.*)$")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
MESSAGE_ID_RE = re.compile(r"message[_ ]id\s+`?([A-Za-z0-9]+)`?", re.IGNORECASE)

RUBRIC_KEY_MAP = {
    "scope / seniority": "scope_seniority",
    "role fit": "role_fit",
    "compensation": "compensation",
    "geography / work model": "geography_work_model",
    "travel fit": "travel_fit",
    "resume fit": "resume_fit",
    "resume / attainability": "resume_fit",
    "resume / attainability match": "resume_fit",
    "resume / market-language / interview-attainability match": "resume_fit",
}

REQUIRED_ROLE_FIELDS = [
    "quick_read",
    "key_highlights",
    "key_risk",
    "rubric",
    "total_score",
]


class BuildError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Emily digest render YAML from canonical project notes.")
    parser.add_argument("--digest", required=True, help="Path to digest markdown draft/example")
    parser.add_argument("--project-dir", help="Optional project directory override")
    parser.add_argument("--output", help="Optional output YAML path")
    parser.add_argument("--comparison", help="Optional comparison markdown report path")
    parser.add_argument("--review-mode", choices=["infer", "true", "false"], default="infer")
    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise BuildError(f"Required file not found: {path}") from exc


def extract_section(markdown: str, heading: str) -> str | None:
    matches = list(SECTION_RE.finditer(markdown))
    for index, match in enumerate(matches):
        if match.group(1).strip().lower() != heading.lower():
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        return markdown[start:end].strip()
    return None


def extract_subsections(markdown: str) -> list[tuple[str, str]]:
    matches = list(SUBSECTION_RE.finditer(markdown))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections.append((heading, markdown[start:end].strip()))
    return sections


def parse_markdown_table(markdown: str) -> list[dict[str, str]]:
    lines = [line.rstrip() for line in markdown.splitlines() if line.strip()]
    table_lines = [line for line in lines if line.strip().startswith("|")]
    if len(table_lines) < 2:
        return []
    header = [cell.strip() for cell in table_lines[0].strip().strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < len(header):
            cells += [""] * (len(header) - len(cells))
        rows.append({header[i]: cells[i] for i in range(len(header))})
    return rows


def strip_angle_brackets(value: str) -> str:
    value = value.strip()
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1]
    return value


def parse_subject(markdown: str) -> str:
    section = extract_section(markdown, "Approved subject line") or extract_section(markdown, "Subject line")
    if not section:
        raise BuildError("Could not find approved subject line in digest draft.")
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    if not lines:
        raise BuildError("Subject line section was empty.")
    return lines[0].strip("`")


def parse_signoff(markdown: str) -> str:
    match = re.search(r"\nBest,\s*\n([^\n]+)\s*$", markdown.strip(), re.MULTILINE)
    if not match:
        raise BuildError("Could not find digest signoff.")
    return match.group(1).strip()


def parse_links_section(markdown: str) -> dict[str, str]:
    section = extract_section(markdown, "Links")
    if not section:
        return {}
    links: dict[str, str] = {}
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        line = line[2:]
        if ":" not in line:
            continue
        label, rest = line.split(":", 1)
        label = label.strip().lower()
        rest = rest.strip()
        match = LINK_RE.search(rest)
        if match:
            links[label] = match.group(2)
        else:
            links[label] = rest
    return links


def parse_digest_roles(markdown: str) -> list[dict[str, Any]]:
    top_roles = extract_section(markdown, "Top roles right now")
    if not top_roles:
        raise BuildError("Could not find 'Top roles right now' section in digest draft.")

    matches = list(ROLE_HEADING_RE.finditer(top_roles))
    if not matches:
        raise BuildError("Could not parse any digest role blocks.")

    roles: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        rank = int(match.group(1))
        company = match.group(2).strip()
        title = match.group(3).strip()
        url = match.group(4).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(top_roles)
        block = top_roles[start:end].strip()
        role: dict[str, Any] = {
            "rank": rank,
            "company": company,
            "title": title,
            "canonical_url": url,
            "key_highlights": [],
            "rubric": {},
        }
        in_score_breakdown = False
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            field_match = FIELD_LINE_RE.match(line)
            if field_match:
                field_name = field_match.group(1).strip().rstrip(":").lower()
                value = field_match.group(2).lstrip(": ").strip()
                if field_name == "quick read":
                    role["quick_read"] = value
                elif field_name == "key highlights":
                    role["key_highlights"] = [part.strip() for part in value.split(";") if part.strip()]
                elif field_name == "key risk factor":
                    role["key_risk"] = value
                elif field_name == "score breakdown":
                    in_score_breakdown = True
                elif field_name == "total":
                    total_match = re.match(r"(\d+)/(\d+)", value)
                    if total_match:
                        role["total_score"] = int(total_match.group(1))
                continue
            if in_score_breakdown and line.startswith("- "):
                score_match = SCORE_LINE_RE.match(line)
                if score_match:
                    label = score_match.group(1).strip().lower()
                    score = int(score_match.group(2))
                    maximum = int(score_match.group(3))
                    reason = score_match.group(4).strip()
                    if label == "total":
                        role["total_score"] = score
                    else:
                        rubric_key = RUBRIC_KEY_MAP.get(label)
                        if rubric_key:
                            role["rubric"][rubric_key] = {
                                "score": score,
                                "max": maximum,
                                "reason": reason,
                            }
                continue
        for field in REQUIRED_ROLE_FIELDS:
            if field not in role or role[field] in (None, "", [], {}):
                raise BuildError(f"Digest role block missing required field '{field}' for rank {rank}.")
        roles.append(role)
    return roles


def parse_digest_changes(markdown: str) -> dict[str, list[str]]:
    section = extract_section(markdown, "What changed since the last update")
    mapping = {"new": [], "moved_up": [], "removed_or_stale": []}
    if not section:
        return mapping
    for raw_line in section.splitlines():
        line = raw_line.strip()
        match = FIELD_LINE_RE.match(line)
        if not match:
            continue
        label = match.group(1).strip().rstrip(":").lower()
        value = match.group(2).lstrip(": ").strip()
        if value.lower() in {"none", "none."}:
            items: list[str] = []
        else:
            items = [value]
        if label == "new":
            mapping["new"] = items
        elif label == "moved up":
            mapping["moved_up"] = items
        elif label in {"removed / stale / closed", "removed / closed"}:
            mapping["removed_or_stale"] = items
    return mapping


def parse_quick_notes(markdown: str) -> list[str]:
    section = extract_section(markdown, "Quick notes")
    if not section:
        return []
    notes = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            notes.append(line[2:].strip())
    return notes


def parse_shortlist(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    section = extract_section(read_text(path), "Current live set")
    if not section:
        raise BuildError("Could not find 'Current live set' table in Live Role Shortlist.md")
    rows = parse_markdown_table(section)
    mapping: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        company = row.get("Company", "").strip()
        title = row.get("Title", "").strip()
        mapping[(company, title)] = {
            "rank": int(row.get("Rank", "0") or 0),
            "score": int((row.get("Score", "0") or "0").replace(",", "")),
            "work_model": row.get("Work model", "").strip(),
            "geography": row.get("Geography", "").strip(),
            "last_confirmed_live": row.get("Last confirmed live", "").strip(),
            "canonical_url": strip_angle_brackets(row.get("Canonical link", "").strip()),
            "evidence": row.get("Evidence", "").strip(),
            "state": row.get("State", "").strip(),
        }
    return mapping


def parse_ledger(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    section = extract_section(read_text(path), "Ledger")
    if not section:
        raise BuildError("Could not find 'Ledger' table in Role State Ledger.md")
    rows = parse_markdown_table(section)
    mapping: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        company = row.get("Company", "").strip()
        title = row.get("Title", "").strip()
        mapping[(company, title)] = {
            "current_state": row.get("Current state", "").strip(),
            "current_rank": (row.get("Current rank", "") or "").strip(),
            "score": (row.get("Score", "") or "").strip(),
            "last_confirmed_live": row.get("Last confirmed live", "").strip(),
            "last_reviewed": row.get("Last reviewed", "").strip(),
            "canonical_url": strip_angle_brackets(row.get("Canonical URL", "").strip()),
            "evidence_note": row.get("Evidence note", "").strip(),
            "notes": row.get("Notes", "").strip(),
        }
    return mapping


def parse_delta_entries(path: Path) -> list[tuple[str, dict[str, str]]]:
    markdown = read_text(path)
    entries: list[tuple[str, dict[str, str]]] = []
    current_heading: str | None = None
    current_fields: dict[str, str] = {}
    in_entries = False
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.strip() == "## Entries":
            in_entries = True
            continue
        if not in_entries:
            continue
        if line.startswith("### "):
            if current_heading is not None:
                entries.append((current_heading, current_fields))
            current_heading = line[4:].strip()
            current_fields = {}
            continue
        if current_heading and line.strip().startswith("- ") and ":" in line:
            body = line.strip()[2:]
            label, value = body.split(":", 1)
            current_fields[label.strip().lower()] = value.strip()
    if current_heading is not None:
        entries.append((current_heading, current_fields))
    return entries


def choose_delta_entry(entries: list[tuple[str, dict[str, str]]], digest_date: str) -> tuple[str, dict[str, str]] | None:
    matches = [(heading, fields) for heading, fields in entries if heading.startswith(digest_date)]
    if not matches:
        return None
    return matches[-1]


def parse_comparison_report(path: Path) -> tuple[dict[tuple[str, str], dict[str, str]], dict[tuple[str, str], str]]:
    markdown = read_text(path)
    table_section = extract_section(markdown, "Full comparison table") or ""
    rows = parse_markdown_table(table_section)
    table_map: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        company = row.get("Company", "").strip()
        title_cell = row.get("Title", "").strip()
        title_match = LINK_RE.search(title_cell)
        title = title_match.group(1).strip() if title_match else title_cell
        table_map[(company, title)] = {
            "salary_range": row.get("Salary range", "").strip(),
            "work_model": row.get("Work model", "").strip(),
        }

    radar_map: dict[tuple[str, str], str] = {}
    matches = list(ROLE_BLOCK_HEADING_RE.finditer(markdown))
    for index, match in enumerate(matches):
        company = match.group(2).strip()
        title = match.group(3).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        block = markdown[start:end]
        image_match = IMAGE_RE.search(block)
        if image_match:
            radar_map[(company, title)] = image_match.group(1).strip()
    return table_map, radar_map


def infer_review_mode(mode: str, digest_path: Path) -> bool:
    if mode == "true":
        return True
    if mode == "false":
        return False
    return True


def infer_date(digest_path: Path) -> str:
    match = DATE_RE.search(digest_path.name)
    if not match:
        raise BuildError(f"Could not infer digest date from filename: {digest_path.name}")
    return match.group(1)


def infer_output_path(project_dir: Path, digest_date: str) -> Path:
    return project_dir / "Render Data" / f"Emily Digest Render Data - {digest_date}.yaml"


def infer_project_dir(source_path: Path) -> Path:
    """Find the Emily Job Search project root from a dated artifact path."""
    for candidate in [source_path.parent, *source_path.parents]:
        if (candidate / "Live Role Shortlist.md").exists() and (candidate / "Role State Ledger.md").exists():
            return candidate
    return source_path.parent


def infer_comparison_path(project_dir: Path, digest_date: str) -> Path | None:
    reports_dir = project_dir.parents[2] / "20 Library" / "Research Reports" / "Emily Job Search"
    candidates = [
        reports_dir / "Comparison Reports" / f"Emily Digest Comparison Report - {digest_date}.md",
        project_dir / f"Emily Digest Comparison Report - {digest_date}.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def rel_path(path: Path, base_dir: Path) -> str:
    return os.path.relpath(path, base_dir).replace(os.sep, "/")


def rel_url(path: Path, base_dir: Path) -> str:
    return quote(rel_path(path, base_dir), safe="/-_.")


def normalize_local_asset(raw: str, source_file: Path, base_dir: Path) -> str:
    if not raw or raw.startswith(("http://", "https://", "data:")):
        return raw
    resolved = (source_file.parent / unquote(raw)).resolve()
    return rel_url(resolved, base_dir)


def date_range_label_from_subject(subject: str) -> str:
    if "—" in subject:
        return subject.split("—", 1)[1].strip()
    return subject


def build_payload(
    digest_path: Path,
    project_dir: Path,
    comparison_path: Path | None,
    review_mode: bool,
) -> dict[str, Any]:
    digest_markdown = read_text(digest_path)
    digest_date = infer_date(digest_path)
    subject = parse_subject(digest_markdown)
    signoff = parse_signoff(digest_markdown)
    digest_roles = parse_digest_roles(digest_markdown)
    digest_changes = parse_digest_changes(digest_markdown)
    quick_notes = parse_quick_notes(digest_markdown)
    link_targets = parse_links_section(digest_markdown)

    shortlist = parse_shortlist(project_dir / "Live Role Shortlist.md")
    ledger = parse_ledger(project_dir / "Role State Ledger.md")
    delta_entries = parse_delta_entries(project_dir / "Refresh Delta Log.md")
    delta_entry = choose_delta_entry(delta_entries, digest_date)

    comparison_table: dict[tuple[str, str], dict[str, str]] = {}
    radar_assets: dict[tuple[str, str], str] = {}
    if comparison_path and comparison_path.exists():
        comparison_table, radar_assets = parse_comparison_report(comparison_path)

    roles: list[dict[str, Any]] = []
    for role in digest_roles:
        key = (role["company"], role["title"])
        shortlist_row = shortlist.get(key)
        if not shortlist_row:
            raise BuildError(f"Role from digest draft not found in live shortlist: {key[0]} / {key[1]}")
        ledger_row = ledger.get(key, {})
        comparison_row = comparison_table.get(key, {})

        salary_range = comparison_row.get("salary_range", "")
        radar_asset = radar_assets.get(key, "")
        if radar_asset and comparison_path:
            radar_asset = normalize_local_asset(radar_asset, comparison_path, project_dir)

        role_payload = {
            "rank": role["rank"],
            "company": role["company"],
            "title": role["title"],
            "canonical_url": shortlist_row.get("canonical_url") or role["canonical_url"],
            "work_model": comparison_row.get("work_model") or shortlist_row.get("work_model", ""),
            "geography": shortlist_row.get("geography", ""),
            "salary_range": salary_range,
            "quick_read": role["quick_read"],
            "key_highlights": role["key_highlights"],
            "key_risk": role["key_risk"],
            "total_score": role["total_score"],
            "rubric": role["rubric"],
            "radar_asset": radar_asset,
        }
        # Preserve current shortlist/ledger reality over the digest draft when ranks or links drift.
        if shortlist_row.get("rank") and shortlist_row["rank"] != role_payload["rank"]:
            role_payload["rank"] = shortlist_row["rank"]
        if shortlist_row.get("score") and shortlist_row["score"] != role_payload["total_score"]:
            role_payload["total_score"] = shortlist_row["score"]
        if ledger_row.get("canonical_url"):
            role_payload["canonical_url"] = ledger_row["canonical_url"]
        roles.append(role_payload)

    comparison_markdown_rel = None
    comparison_html_name = None
    if comparison_path and comparison_path.exists():
        comparison_markdown_rel = rel_path(comparison_path, project_dir)
        comparison_html_name = rel_path(
            comparison_path.with_suffix(".html"),
            project_dir,
        )

    send_log = {
        "approval_required": False,
        "approved_by": "Standing recurring-send permission reaffirmed by Jaret via Discord on 2026-05-20",
        "sent_at": "",
        "message_id": "",
    }
    if delta_entry:
        _, delta_fields = delta_entry
        blockers = delta_fields.get("blockers / follow-ups", "")
        digest_impact = delta_fields.get("digest-impacting changes", "")
        if "Jaret approved" in blockers or "first approved live digest" in digest_impact:
            send_log["approved_by"] = "Jaret"
        message_match = MESSAGE_ID_RE.search(digest_impact)
        if message_match:
            send_log["message_id"] = message_match.group(1)
            send_log["sent_at"] = digest_date

    comparison_target = comparison_html_name or link_targets.get("full comparison report", "")
    payload = {
        "digest_date": digest_date,
        "date_range_label": date_range_label_from_subject(subject),
        "review_mode": review_mode,
        "author_name": signoff,
        "subject": subject,
        "delivery": {
            "to": "emily.brown.ops@gmail.com",
            "cc": ["jaretjb@gmail.com"],
        },
        "source_artifacts": {
            "digest_markdown": digest_path.relative_to(project_dir).as_posix(),
            "comparison_markdown": comparison_markdown_rel or "",
        },
        "output_artifacts": {
            "email_html": f"Rendered Emails/Emily Digest Email - {digest_date}.html",
            "email_text": f"Rendered Emails/Emily Digest Email - {digest_date}.txt",
            "comparison_html": comparison_html_name or "",
            "approval_packet_markdown": f"Approval Packets/Emily Digest Approval Packet - {digest_date}.md",
        },
        "roles": sorted(roles, key=lambda item: item["rank"]),
        "changes": digest_changes,
        "quick_notes": quick_notes,
        "links": {
            "comparison_report_label": "Full comparison report",
            "comparison_report_target": comparison_target,
            "shortlist_note": "Live Role Shortlist.md",
        },
        "send_log": send_log,
    }
    return payload


def main() -> int:
    args = parse_args()
    digest_path = Path(args.digest).resolve()
    if not digest_path.exists():
        print(f"ERROR: Digest file not found: {digest_path}", file=sys.stderr)
        return 2

    project_dir = Path(args.project_dir).resolve() if args.project_dir else infer_project_dir(digest_path)
    digest_date = infer_date(digest_path)
    comparison_path = Path(args.comparison).resolve() if args.comparison else infer_comparison_path(project_dir, digest_date)
    output_path = Path(args.output).resolve() if args.output else infer_output_path(project_dir, digest_date)
    review_mode = infer_review_mode(args.review_mode, digest_path)

    try:
        payload = build_payload(digest_path, project_dir, comparison_path, review_mode)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
        print(f"Wrote render data: {output_path}")
        return 0
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
