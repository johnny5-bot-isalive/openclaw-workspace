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


class PacketError(Exception):
    pass


def infer_project_dir(source_path: Path) -> Path:
    """Find the Emily Job Search project root from a dated artifact path."""
    for candidate in [source_path.parent, *source_path.parents]:
        if (candidate / "Live Role Shortlist.md").exists() and (candidate / "Role State Ledger.md").exists():
            return candidate
    return source_path.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Emily digest approval packet from render data + current deltas.")
    parser.add_argument("--data", required=True, help="Path to Emily Digest Render Data YAML")
    parser.add_argument("--project-dir", help="Optional explicit project directory override")
    parser.add_argument("--output", help="Optional output markdown path override")
    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise PacketError(f"Required file not found: {path}") from exc


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(read_text(path))
    except yaml.YAMLError as exc:
        raise PacketError(f"Could not parse YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise PacketError("Render data YAML must parse to an object.")
    return data


def extract_section(markdown: str, heading: str) -> str | None:
    matches = list(SECTION_RE.finditer(markdown))
    for index, match in enumerate(matches):
        if match.group(1).strip().lower() != heading.lower():
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        return markdown[start:end].strip()
    return None


def parse_delta_entries(markdown: str) -> list[tuple[str, dict[str, str]]]:
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


def link_to(rel_path: str, label: str) -> str:
    return f"[{label}]({quote(rel_path, safe='/-_.')})"


def rel_posix(path: Path, base_dir: Path) -> str:
    return os.path.relpath(path, base_dir).replace(os.sep, "/")


def rebase_markdown_links(markdown: str, old_base: Path, new_base: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            return match.group(0)
        base, *frag = target.split("#", 1)
        anchor = "#" + frag[0] if frag else ""
        resolved = (old_base / unquote(base)).resolve()
        return link_to(rel_posix(resolved, new_base) + anchor, label)
    return re.sub(r"\[([^\]]+)\]\(([^)\n]+)\)", repl, markdown)


def exists_mark(path: Path | None) -> str:
    return "yes" if path and path.exists() else "no"


def recommendation(data: dict[str, Any]) -> tuple[str, list[str]]:
    send_log = data.get("send_log") or {}
    review_mode = bool(data.get("review_mode"))
    approval_required = bool(send_log.get("approval_required", False))
    approved_by = (send_log.get("approved_by") or "").strip()
    sent_at = (send_log.get("sent_at") or "").strip()
    message_id = (send_log.get("message_id") or "").strip()

    reasons: list[str] = []
    if sent_at or message_id:
        reasons.append("This packet already records a completed send for the current digest bundle.")
        if approved_by:
            reasons.append(f"Approval is already recorded from {approved_by}.")
        return "Already sent — use a fresh digest bundle before sending again.", reasons

    if approval_required and not approved_by:
        reasons.append("This bundle is not covered by standing routine-send permission, so hold until Jaret approves or resolves the exception.")
        if review_mode:
            reasons.append("The bundle is still marked draft-only.")
        return "Hold for exception handling.", reasons

    if approval_required and approved_by and review_mode:
        reasons.append(f"Approval is recorded from {approved_by}, but the bundle is still marked draft-only.")
        return "Approval recorded, but clear draft-only status before sending.", reasons

    if approval_required and approved_by:
        reasons.append(f"Approval is recorded from {approved_by} and the bundle is not marked review-only.")
        return "Ready for send preflight.", reasons

    reasons.append("Standing recurring-send permission is recorded for routine every-other-day digest sends.")
    return "Ready for send preflight.", reasons


def build_packet(data_path: Path, project_dir: Path, output_path: Path) -> str:
    data = load_yaml(data_path)
    digest_date = str(data.get("digest_date") or "").strip()
    if not digest_date:
        raise PacketError("digest_date is required in render data YAML.")

    output_artifacts = data.get("output_artifacts") or {}
    source_artifacts = data.get("source_artifacts") or {}
    delivery = data.get("delivery") or {}
    send_log = data.get("send_log") or {}
    links = data.get("links") or {}
    roles = data.get("roles") or []
    changes = data.get("changes") or {}
    quick_notes = data.get("quick_notes") or []

    digest_md = project_dir / source_artifacts.get("digest_markdown", "")
    comparison_md = project_dir / source_artifacts.get("comparison_markdown", "") if source_artifacts.get("comparison_markdown") else None
    email_html = project_dir / output_artifacts.get("email_html", "") if output_artifacts.get("email_html") else None
    email_text = project_dir / output_artifacts.get("email_text", "") if output_artifacts.get("email_text") else None
    comparison_html = project_dir / output_artifacts.get("comparison_html", "") if output_artifacts.get("comparison_html") else None

    delta_markdown = read_text(project_dir / "Refresh Delta Log.md")
    delta_entry = choose_delta_entry(parse_delta_entries(delta_markdown), digest_date)
    delta_heading = delta_entry[0] if delta_entry else digest_date
    delta_fields = delta_entry[1] if delta_entry else {}

    approval_recommendation, recommendation_reasons = recommendation(data)

    link_base_dir = output_path.parent
    draft_link = link_to(rel_posix(digest_md, link_base_dir), digest_md.stem) if digest_md.exists() else digest_md.name
    render_data_link = link_to(rel_posix(data_path, link_base_dir), data_path.stem)
    email_html_link = link_to(rel_posix(email_html, link_base_dir), email_html.name) if email_html and email_html.exists() else (email_html.name if email_html else "")
    email_text_link = link_to(rel_posix(email_text, link_base_dir), email_text.name) if email_text and email_text.exists() else (email_text.name if email_text else "")
    comparison_md_link = link_to(rel_posix(comparison_md, link_base_dir), comparison_md.stem) if comparison_md and comparison_md.exists() else ""
    comparison_html_link = link_to(rel_posix(comparison_html, link_base_dir), comparison_html.name) if comparison_html and comparison_html.exists() else ""

    comparison_html_text = read_text(comparison_html) if comparison_html and comparison_html.exists() else ""
    svg_count = comparison_html_text.count("<svg")
    missing_local_asset = "Missing local asset" in comparison_html_text
    missing_local_image_asset = "Missing local image asset" in comparison_html_text
    attachment_qa_pass = bool(roles) and svg_count == len(roles) and not missing_local_asset and not missing_local_image_asset

    related_lines = [f"- Digest draft: {draft_link}", f"- Render data: {render_data_link}"]
    if email_html_link:
        related_lines.append(f"- HTML preview: {email_html_link}")
    if email_text_link:
        related_lines.append(f"- Text fallback: {email_text_link}")
    if comparison_md_link:
        related_lines.append(f"- Comparison report (markdown): {comparison_md_link}")
    if comparison_html_link:
        related_lines.append(f"- Comparison report (HTML): {comparison_html_link}")

    role_summary = ", ".join(f"#{role['rank']} {role['company']} ({role['total_score']})" for role in roles)
    changes_new = changes.get("new") or []
    changes_up = changes.get("moved_up") or []
    changes_removed = changes.get("removed_or_stale") or []

    delta_supporting = rebase_markdown_links(delta_fields.get("supporting notes", ""), project_dir, output_path.parent)
    blockers = delta_fields.get("blockers / follow-ups", "")
    digest_changes = delta_fields.get("digest-impacting changes", "")

    lines = [
        "---",
        'type: "project-note"',
        'status: "active"',
        'created: "2026-04-28"',
        'project: "Emily Job Search"',
        "---",
        f"# Emily Digest Approval Packet — {digest_date}",
        "",
        "## Purpose",
        "Auto-generated approval packet for the current Emily digest bundle.",
        "",
        "## Approval snapshot",
        f"- **Recommendation:** {approval_recommendation}",
        f"- **Approval required:** {'yes' if send_log.get('approval_required', False) else 'no'}",
        f"- **Approved by:** {send_log.get('approved_by') or 'not yet recorded'}",
        f"- **Send mode:** {'draft-only' if data.get('review_mode') else 'send-ready'}",
        f"- **Sent at:** {send_log.get('sent_at') or 'not yet sent'}",
        f"- **Message id:** {send_log.get('message_id') or 'not yet sent'}",
        "",
        "## Current digest bundle",
        f"- **Subject:** `{data.get('subject', '')}`",
        f"- **Author:** {data.get('author_name', '')}",
        f"- **Recipient:** `{delivery.get('to', '')}`",
        f"- **CC:** {', '.join(f'`{item}`' for item in delivery.get('cc', [])) if delivery.get('cc') else 'none recorded'}",
        f"- **Role summary:** {role_summary or 'none recorded'}",
        "",
        "## Generated packet artifacts",
        *related_lines,
        "",
        "## Approval checks",
        f"- Digest draft exists: {exists_mark(digest_md)}",
        f"- Render-data sidecar exists: {exists_mark(data_path)}",
        f"- HTML preview exists: {exists_mark(email_html)}",
        f"- Text fallback exists: {exists_mark(email_text)}",
        f"- Comparison markdown exists: {exists_mark(comparison_md)}",
        f"- Comparison HTML exists: {exists_mark(comparison_html)}",
        f"- Recipient still matches project rule: {'yes' if delivery.get('to') == 'emily.brown.ops@gmail.com' else 'no'}",
        f"- CC still includes Jaret: {'yes' if 'jaretjb@gmail.com' in (delivery.get('cc') or []) else 'no'}",
        "",
        "## Attachment QA",
        f"- Comparison HTML inline `<svg` count: {svg_count}",
        f"- Digest role count: {len(roles)}",
        f"- `Missing local asset` marker: {'present' if missing_local_asset else 'absent'}",
        f"- `Missing local image asset` marker: {'present' if missing_local_image_asset else 'absent'}",
        f"- **Result:** {'pass' if attachment_qa_pass else 'fail'}",
        "",
        f"## Current delta summary ({delta_heading})",
        f"- **New:** {'; '.join(changes_new) if changes_new else 'none.'}",
        f"- **Moved up:** {'; '.join(changes_up) if changes_up else 'none.'}",
        f"- **Removed / stale / closed:** {'; '.join(changes_removed) if changes_removed else 'none.'}",
    ]

    if digest_changes:
        lines.append(f"- **Digest-impacting changes from log:** {digest_changes}")
    if blockers:
        lines.append(f"- **Blockers / follow-ups from log:** {blockers}")
    if delta_supporting:
        lines.append(f"- **Supporting notes from log:** {delta_supporting}")

    lines.extend([
        "",
        "## Recommendation rationale",
        *[f"- {reason}" for reason in recommendation_reasons],
        "",
        "## Quick notes carried into send",
    ])
    if quick_notes:
        lines.extend(f"- {note}" for note in quick_notes)
    else:
        lines.append("- none.")

    lines.extend([
        "",
        "## Guardrails",
        "- Routine every-other-day Emily-facing digest emails are standing-send approved after refresh, render, and attachment QA pass; keep Jaret CC'd.",
        "- Do not send Jaret-only review emails by default.",
        "- Hold for Jaret only if there is a blocker, unusual risk, broken rendering/attachment QA, missing freshness evidence, transport/auth failure, or a substantive decision that needs human judgment.",
        "- Max may render/send mechanically but should not rewrite the report content.",
        "- Do not use broad inbox reads as routine send preflight.",
        "",
        "## Related",
        f"- {link_to(rel_posix(project_dir / 'Digest Send Workflow.md', output_path.parent), 'Digest Send Workflow')}",
        f"- {link_to(rel_posix(project_dir / 'Digest Render Pipeline Spec.md', output_path.parent), 'Digest Render Pipeline Spec')}",
        f"- {link_to(rel_posix(project_dir / 'Refresh Delta Log.md', output_path.parent), 'Refresh Delta Log')}",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    data_path = Path(args.data).resolve()
    if not data_path.exists():
        print(f"ERROR: Render data file not found: {data_path}", file=sys.stderr)
        return 2
    project_dir = Path(args.project_dir).resolve() if args.project_dir else infer_project_dir(data_path)

    data = load_yaml(data_path)
    suggested_output = (data.get("output_artifacts") or {}).get("approval_packet_markdown")
    if args.output:
        output_path = Path(args.output).resolve()
    elif suggested_output:
        output_path = (project_dir / suggested_output).resolve()
    else:
        digest_date = str(data.get("digest_date") or "unknown")
        output_path = (project_dir / f"Emily Digest Approval Packet - {digest_date}.md").resolve()

    try:
        packet = build_packet(data_path, project_dir, output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(packet, encoding="utf-8")
        print(f"Wrote approval packet: {output_path}")
        return 0
    except PacketError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
