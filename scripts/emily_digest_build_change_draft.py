from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml


class ChangeDraftError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Emily digest change bullets and delta-log stub from bundle diffs.")
    parser.add_argument("--current", required=True, help="Path to current render-data YAML")
    parser.add_argument("--previous", help="Path to previous render-data YAML; auto-detects if omitted")
    parser.add_argument("--output", help="Optional output markdown path")
    parser.add_argument("--pass-type", default="daily refresh", help="Pass type label for the proposed delta entry")
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ChangeDraftError(f"Missing YAML file: {path}") from exc
    except yaml.YAMLError as exc:
        raise ChangeDraftError(f"Could not parse YAML {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ChangeDraftError(f"YAML root must be an object: {path}")
    return data


def normalize_key(role: dict[str, Any]) -> tuple[str, str]:
    return (str(role.get("company") or "").strip(), str(role.get("title") or "").strip())


def role_label(role: dict[str, Any]) -> str:
    company = str(role.get("company") or "").strip()
    title = str(role.get("title") or "").strip()
    return f"{company} — {title}"


def role_link_label(role: dict[str, Any]) -> str:
    url = str(role.get("canonical_url") or "").strip()
    label = role_label(role)
    if url:
        return f"[{label}]({url})"
    return label


def format_list(items: list[str]) -> str:
    return "; ".join(items) if items else "none."


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def rel_link(path: Path, base_dir: Path) -> str:
    rel = os.path.relpath(path, base_dir).replace(os.sep, "/")
    return quote(rel, safe='/-_.')


def infer_project_dir(source_path: Path) -> Path:
    """Find the Emily Job Search project root from a dated artifact path."""
    for candidate in [source_path.parent, *source_path.parents]:
        if (candidate / "Live Role Shortlist.md").exists() and (candidate / "Role State Ledger.md").exists():
            return candidate
    return source_path.parent


def find_previous(current_path: Path) -> Path:
    parent = current_path.parent
    candidates = sorted(parent.glob("Emily Digest Render Data - *.yaml"))
    candidates = [path for path in candidates if path.resolve() != current_path.resolve()]
    if not candidates:
        raise ChangeDraftError("Could not auto-detect a previous render-data YAML; pass --previous explicitly.")
    return candidates[-1]


def compare_roles(previous_roles: list[dict[str, Any]], current_roles: list[dict[str, Any]]) -> dict[str, Any]:
    previous = {normalize_key(role): role for role in previous_roles}
    current = {normalize_key(role): role for role in current_roles}

    added_keys = [key for key in current if key not in previous]
    removed_keys = [key for key in previous if key not in current]
    shared_keys = [key for key in current if key in previous]

    added = [current[key] for key in sorted(added_keys, key=lambda item: current[item].get("rank", 999))]
    removed = [previous[key] for key in sorted(removed_keys, key=lambda item: previous[item].get("rank", 999))]

    moved_up: list[str] = []
    moved_down: list[str] = []
    score_changes: list[str] = []
    canonical_updates: list[str] = []

    for key in shared_keys:
        prev = previous[key]
        cur = current[key]
        prev_rank = int(prev.get("rank", 999))
        cur_rank = int(cur.get("rank", 999))
        prev_score = prev.get("total_score")
        cur_score = cur.get("total_score")
        prev_url = str(prev.get("canonical_url") or "").strip()
        cur_url = str(cur.get("canonical_url") or "").strip()

        if cur_rank < prev_rank:
            moved_up.append(f"{cur.get('company')} moved from #{prev_rank} to #{cur_rank}.")
        elif cur_rank > prev_rank:
            moved_down.append(f"{cur.get('company')} moved from #{prev_rank} to #{cur_rank}.")

        if prev_score != cur_score and prev_score is not None and cur_score is not None:
            delta = int(cur_score) - int(prev_score)
            direction = "+" if delta > 0 else ""
            score_changes.append(f"{cur.get('company')} score changed from {prev_score} to {cur_score} ({direction}{delta}).")

        if prev_url and cur_url and prev_url != cur_url:
            canonical_updates.append(f"{role_label(cur)} canonical URL updated from <{prev_url}> to <{cur_url}>.")

    return {
        "added": added,
        "removed": removed,
        "moved_up": moved_up,
        "moved_down": moved_down,
        "score_changes": score_changes,
        "canonical_updates": canonical_updates,
    }


def build_change_bullets(diff: dict[str, Any]) -> dict[str, list[str]]:
    new_items = [f"{role_link_label(role)} was added to the live shortlist at #{role.get('rank')}." for role in diff["added"]]
    moved_up_items = list(diff["moved_up"])
    removed_items = [f"{role_link_label(role)} dropped out of the current live shortlist." for role in diff["removed"]]
    return {
        "new": new_items,
        "moved_up": moved_up_items,
        "removed_or_stale": removed_items,
    }


def build_digest_impact(diff: dict[str, Any], change_bullets: dict[str, list[str]]) -> str:
    parts: list[str] = []
    parts.extend(change_bullets["new"])
    parts.extend(change_bullets["moved_up"])
    parts.extend(change_bullets["removed_or_stale"])
    parts.extend(diff["canonical_updates"])
    if diff["score_changes"]:
        parts.extend(diff["score_changes"])
    if not parts:
        return "none; live set remains stable."
    return " ".join(parts)


def build_markdown(current_path: Path, previous_path: Path, current: dict[str, Any], previous: dict[str, Any], pass_type: str, link_base_dir: Path) -> str:
    current_roles = current.get("roles") or []
    previous_roles = previous.get("roles") or []
    if not isinstance(current_roles, list) or not isinstance(previous_roles, list):
        raise ChangeDraftError("Both render-data files must contain a roles list.")

    diff = compare_roles(previous_roles, current_roles)
    change_bullets = build_change_bullets(diff)
    digest_impact = build_digest_impact(diff, change_bullets)

    current_date = str(current.get("digest_date") or "").strip()
    previous_date = str(previous.get("digest_date") or "").strip()
    if not current_date:
        raise ChangeDraftError("Current render data is missing digest_date.")

    current_link = rel_link(current_path, link_base_dir)
    previous_link = rel_link(previous_path, link_base_dir)

    lines = [
        "---",
        'type: "project-note"',
        'status: "draft"',
        'created: "2026-04-28"',
        'project: "Emily Job Search"',
        "---",
        f"# Emily Digest Change Draft — {current_date}",
        "",
        "## Purpose",
        f"Auto-generated first-pass change bullets by diffing the current digest bundle against the prior bundle ({previous_date or 'unknown previous date'}).",
        "",
        "## Proposed render-data `changes` block",
        "```yaml",
        "changes:",
        f"  new: {yaml.safe_dump(change_bullets['new'], sort_keys=False, default_flow_style=True).strip()}",
        f"  moved_up: {yaml.safe_dump(change_bullets['moved_up'], sort_keys=False, default_flow_style=True).strip()}",
        f"  removed_or_stale: {yaml.safe_dump(change_bullets['removed_or_stale'], sort_keys=False, default_flow_style=True).strip()}",
        "```",
        "",
        "## Proposed digest `What changed since the last update` section",
        f"- **New:** {format_list(change_bullets['new'])}",
        f"- **Moved up:** {format_list(change_bullets['moved_up'])}",
        f"- **Removed / stale / closed:** {format_list(change_bullets['removed_or_stale'])}",
        "",
        "## Proposed Refresh Delta Log entry",
        f"### {current_date}",
        f"- Pass type: {pass_type}",
        f"- Roles added to live shortlist: {format_list([role_label(role) for role in diff['added']])}",
        f"- Roles promoted / re-ranked: {format_list(diff['moved_up'] + diff['moved_down'])}",
        "- Roles downgraded to aging / stale: none.",
        f"- Roles removed and why: {format_list([f'{role_label(role)} removed from the live shortlist because it no longer appears in the current bundle.' for role in diff['removed']])}",
        "- Freshness checks completed: [fill in from the direct-source checks for this pass]",
        f"- Canonical URL updates: {format_list(diff['canonical_updates'])}",
        f"- Digest-impacting changes: {digest_impact}",
        "- Blockers / follow-ups: [fill in if needed]",
        f"- Supporting notes: [current render data]({current_link}), [previous render data]({previous_link})",
        "",
        "## Raw diff summary",
        f"- Added roles: {format_list([role_label(role) for role in diff['added']])}",
        f"- Removed roles: {format_list([role_label(role) for role in diff['removed']])}",
        f"- Rank changes: {format_list(diff['moved_up'] + diff['moved_down'])}",
        f"- Score changes: {format_list(diff['score_changes'])}",
        f"- Canonical URL changes: {format_list(diff['canonical_updates'])}",
        "",
        "## Notes",
        "- This draft is intentionally first-pass only; freshness evidence and removal reasons should still be verified against the direct-source checks before log/save/send use.",
        "- Stable no-change days should mostly collapse to `none; live set remains stable.` once verified.",
        "",
        "#emily-job-search #digest #delta #generated",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    current_path = Path(args.current).resolve()
    if not current_path.exists():
        print(f"ERROR: Current render-data file not found: {current_path}", file=sys.stderr)
        return 2
    previous_path = Path(args.previous).resolve() if args.previous else find_previous(current_path)

    try:
        current = load_yaml(current_path)
        previous = load_yaml(previous_path)
        project_dir = infer_project_dir(current_path)
        output_path = Path(args.output).resolve() if args.output else (project_dir / "Digest Change Drafts" / f"Emily Digest Change Draft - {current.get('digest_date', 'unknown')}.md").resolve()
        markdown = build_markdown(current_path, previous_path, current, previous, args.pass_type, output_path.parent)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        print(f"Wrote change draft: {output_path}")
        return 0
    except ChangeDraftError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
