from __future__ import annotations

import argparse
import base64
import html
import math
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import yaml
from markdown_it import MarkdownIt

REQUIRED_TOP_LEVEL = [
    "digest_date",
    "date_range_label",
    "review_mode",
    "author_name",
    "subject",
    "delivery",
    "source_artifacts",
    "output_artifacts",
    "roles",
    "changes",
    "quick_notes",
]

RUBRIC_ORDER = [
    ("scope_seniority", "Scope / seniority", 20),
    ("role_fit", "Role fit", 25),
    ("compensation", "Compensation", 15),
    ("geography_work_model", "Geography / work model", 15),
    ("travel_fit", "Travel fit", 5),
    ("resume_fit", "Resume / attainability", 20),
]

AUDIENCE_COPY_BANNED_PHRASES = [
    "still resolves",
    "still resolved",
    "resolves today",
    "direct posting",
    "direct page",
    "direct careers page",
    "direct greenhouse",
    "direct lever",
    "direct source",
    "freshness",
    "recalibrat",
    "validation",
    "validated",
    "live enough",
    "post still",
    "posting still",
    "still live",
    "current live set",
    "live monitored set",
    "survivor",
    "pattern-audit",
    "in-lane survivor",
]

SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
CODE_RE = re.compile(r"`([^`]+)`")
IMAGE_TAG_RE = re.compile(r'<img\s+src="([^"]+)"\s+alt="([^"]*)"\s*/?>')
LINK_TAG_RE = re.compile(r'<a href="([^"]+)">(.+?)</a>')
FIGURE_PARAGRAPH_RE = re.compile(r'<p>(<figure.*?</figure>)</p>', re.DOTALL)
TABLE_RE = re.compile(r'<table>.*?</table>', re.DOTALL)
ROLE_SECTION_RE = re.compile(r'(<h2>\d+\).*?)(?=<h2>\d+\)|\Z)', re.DOTALL)


class ValidationError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Emily digest email artifacts from YAML + markdown.")
    parser.add_argument("--data", required=True, help="Path to Emily Digest Render Data YAML")
    parser.add_argument("--project-dir", help="Optional explicit project directory override")
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"YAML sidecar not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValidationError(f"Could not parse YAML sidecar: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError("YAML sidecar must parse to a mapping/object.")
    return data


def require(value: Any, label: str) -> Any:
    if value is None or value == "" or value == []:
        raise ValidationError(f"Missing required field: {label}")
    return value


def validate_audience_copy(text: str, label: str) -> None:
    """Reject source-validation/process wording in Emily-facing copy fields."""
    lowered = text.lower()
    hits = [phrase for phrase in AUDIENCE_COPY_BANNED_PHRASES if phrase in lowered]
    if hits:
        raise ValidationError(
            f"{label} contains internal process/source-validation wording that should not appear in Emily-facing copy: "
            + ", ".join(sorted(set(hits)))
        )


def resolve_path(base_dir: Path, raw: str | None) -> Path | None:
    if not raw:
        return None
    path = Path(raw)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def infer_project_dir(source_path: Path) -> Path:
    """Find the Emily Job Search project root from a dated artifact path."""
    for candidate in [source_path.parent, *source_path.parents]:
        if (candidate / "Live Role Shortlist.md").exists() and (candidate / "Role State Ledger.md").exists():
            return candidate
    return source_path.parent


def extract_section(markdown: str, heading: str) -> str | None:
    matches = list(SECTION_RE.finditer(markdown))
    for index, match in enumerate(matches):
        if match.group(1).strip().lower() != heading.lower():
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        return markdown[start:end].strip()
    return None


def extract_markdown_metadata(markdown: str) -> dict[str, str | None]:
    subject_block = extract_section(markdown, "Approved subject line") or extract_section(markdown, "Subject line")
    body_block = extract_section(markdown, "Body")

    subject = None
    if subject_block:
        lines = [line.strip() for line in subject_block.splitlines() if line.strip()]
        if lines:
            subject = lines[0].strip("`")

    signoff_name = None
    signoff_match = re.search(r"\nBest,\s*\n([^\n]+)\s*$", markdown.strip(), re.MULTILINE)
    if signoff_match:
        signoff_name = signoff_match.group(1).strip()

    intro = None
    if body_block:
        paragraphs = [p.strip() for p in body_block.split("\n\n") if p.strip()]
        if paragraphs:
            intro = "\n\n".join(paragraphs)

    return {
        "subject": subject,
        "signoff_name": signoff_name,
        "intro": intro,
    }


def inline_markdown_to_html(text: str) -> str:
    escaped = html.escape(text)
    escaped = LINK_RE.sub(lambda m: f'<a href="{html.escape(m.group(2), quote=True)}" style="color:#2563eb;">{m.group(1)}</a>', escaped)
    escaped = BOLD_RE.sub(r"<strong>\1</strong>", escaped)
    escaped = CODE_RE.sub(r"<code style=\"background:#f3f4f6;padding:1px 4px;border-radius:4px;\">\1</code>", escaped)
    return escaped


def strip_frontmatter(markdown: str) -> str:
    if not markdown.startswith("---\n"):
        return markdown
    end = markdown.find("\n---\n", 4)
    if end == -1:
        return markdown
    return markdown[end + 5 :].lstrip()


def inline_local_images(rendered_html: str, base_dir: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        raw_src = html.unescape(match.group(1))
        alt = html.escape(html.unescape(match.group(2)))
        if raw_src.startswith(("http://", "https://", "data:")):
            return (
                f'<figure style="margin:18px 0;text-align:center;"><img src="{html.escape(raw_src, quote=True)}" '
                'style="max-width:100%;height:auto;border:1px solid #e5e7eb;border-radius:12px;"/>'
                f'<figcaption style="margin-top:8px;font-size:13px;color:#6b7280;">{alt}</figcaption></figure>'
            )

        resolved = (base_dir / unquote(raw_src)).resolve()
        if not resolved.exists():
            raise ValidationError(f"Missing local image asset referenced by markdown: {resolved}")
        if resolved.suffix.lower() == ".svg":
            svg = resolved.read_text(encoding="utf-8")
            if "<svg" in svg:
                if "style=" not in svg.split(">", 1)[0]:
                    svg = svg.replace("<svg ", '<svg style="width:100%;height:auto;display:block;margin:0 auto;" ', 1)
                else:
                    svg = svg.replace("max-width:100%;height:auto;display:block;margin:0 auto;", "width:100%;height:auto;display:block;margin:0 auto;")
            return (
                '<figure style="margin:18px 0;text-align:center;padding:0;border:1px solid #e5e7eb;border-radius:14px;background:#ffffff;overflow:hidden;">'
                f'{svg}'
                f'<figcaption style="margin:8px 0 10px 0;font-size:13px;color:#6b7280;">{alt}</figcaption></figure>'
            )

        mime = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }.get(resolved.suffix.lower())
        if mime:
            encoded = base64.b64encode(resolved.read_bytes()).decode("ascii")
            return (
                '<figure style="margin:18px 0;text-align:center;">'
                f'<img src="data:{mime};base64,{encoded}" alt="{alt}" '
                'style="max-width:100%;height:auto;border:1px solid #e5e7eb;border-radius:12px;"/>'
                f'<figcaption style="margin-top:8px;font-size:13px;color:#6b7280;">{alt}</figcaption></figure>'
            )
        return f'<p><a href="{html.escape(raw_src, quote=True)}">{alt or html.escape(raw_src)}</a></p>'

    return IMAGE_TAG_RE.sub(replace, rendered_html)


def generate_radar_svg(role: dict[str, Any], digest_date: str) -> str:
    labels = [
        ("scope_seniority", "Scope"),
        ("role_fit", "Role fit"),
        ("compensation", "Comp"),
        ("geography_work_model", "Geo"),
        ("travel_fit", "Travel"),
        ("resume_fit", "Resume"),
    ]
    center_x = 220
    center_y = 240
    max_r = 135.3
    angles = [-math.pi / 2 + i * (2 * math.pi / 6) for i in range(6)]

    def point(angle: float, radius: float) -> tuple[float, float]:
        return (center_x + radius * math.cos(angle), center_y + radius * math.sin(angle))

    def pts_str(points: list[tuple[float, float]]) -> str:
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="440" height="440" viewBox="0 0 440 440">',
        '  <rect width="100%" height="100%" fill="white" />',
        f'  <text x="220" y="26" text-anchor="middle" font-size="18" font-weight="600" fill="#24292f">{html.escape(str(role["company"]))} radar</text>',
        f'  <text x="220" y="46" text-anchor="middle" font-size="12" fill="#57606a">Emily digest score profile • total {role["total_score"]}/100 • {html.escape(str(digest_date))}</text>',
    ]

    for level in range(1, 6):
        radius = max_r * level / 5
        parts.append(
            f'  <polygon points="{pts_str([point(angle, radius) for angle in angles])}" fill="none" stroke="#d0d7de" stroke-width="1" />'
        )

    for angle in angles:
        x, y = point(angle, max_r)
        parts.append(f'  <line x1="{center_x}" y1="{center_y}" x2="{x:.1f}" y2="{y:.1f}" stroke="#d0d7de" stroke-width="1" />')

    label_positions = [
        (220.0, 92.7, "middle"),
        (364.2, 176.3, "start"),
        (364.2, 343.6, "start"),
        (220.0, 427.3, "middle"),
        (75.8, 343.7, "end"),
        (75.8, 176.3, "end"),
    ]
    for (_, label), (x, y, anchor) in zip(labels, label_positions):
        parts.append(f'  <text x="{x}" y="{y}" font-size="13" text-anchor="{anchor}" fill="#24292f">{html.escape(label)}</text>')

    role_points = []
    for (key, _), angle in zip(labels, angles):
        entry = role["rubric"][key]
        role_points.append(point(angle, max_r * (entry["score"] / entry["max"])))
    parts.append(f'  <polygon points="{pts_str(role_points)}" fill="#54aeff55" stroke="#0969da" stroke-width="2" />')
    for x, y in role_points:
        parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="#0969da" />')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def ensure_radar_assets(data: dict[str, Any], base_dir: Path) -> None:
    """Create/refresh radar SVGs declared by the render-data sidecar before HTML rendering."""
    digest_date = str(data["digest_date"])
    for role in data.get("roles", []):
        raw_asset = role.get("radar_asset")
        if not raw_asset:
            continue
        asset_path = Path(unquote(str(raw_asset)))
        if not asset_path.is_absolute():
            asset_path = (base_dir / asset_path).resolve()
        ensure_parent(asset_path)
        asset_path.write_text(generate_radar_svg(role, digest_date), encoding="utf-8")


def style_anchor_tags(rendered_html: str) -> str:
    return LINK_TAG_RE.sub(lambda m: f'<a href="{m.group(1)}" style="color:#2563eb;">{m.group(2)}</a>', rendered_html)


def wrap_tables(rendered_html: str) -> str:
    def replace(match: re.Match[str]) -> str:
        table = match.group(0)
        header_row = table.split('</tr>', 1)[0]
        header_count = header_row.count('<th ') + header_row.count('<th>')
        table_class = 'wide-table' if header_count > 6 else 'overview-table'
        table = table.replace('<table>', f'<table class="{table_class}">', 1)
        return f'<div class="table-scroll {table_class}-wrap">{table}</div>'

    return TABLE_RE.sub(replace, rendered_html)


def wrap_role_cards(rendered_html: str) -> str:
    return ROLE_SECTION_RE.sub(lambda m: f'<section class="role-card">{m.group(1)}</section>', rendered_html)


def render_markdown_document(markdown: str, *, base_dir: Path) -> str:
    body = strip_frontmatter(markdown)
    rendered = MarkdownIt("default").render(body)
    rendered = style_anchor_tags(rendered)
    rendered = inline_local_images(rendered, base_dir)
    rendered = FIGURE_PARAGRAPH_RE.sub(r"\1", rendered)
    rendered = wrap_tables(rendered)
    rendered = wrap_role_cards(rendered)
    return rendered


def validate_bundle(data: dict[str, Any], base_dir: Path) -> dict[str, Path | None]:
    for field in REQUIRED_TOP_LEVEL:
        require(data.get(field), field)

    author_name = require(data.get("author_name"), "author_name")
    if not isinstance(author_name, str) or not author_name.strip():
        raise ValidationError("author_name must be non-empty text")

    delivery = require(data.get("delivery"), "delivery")
    if not isinstance(delivery, dict):
        raise ValidationError("delivery must be a mapping/object")
    require(delivery.get("to"), "delivery.to")
    require(delivery.get("cc"), "delivery.cc")
    if delivery["to"] != "emily.brown.ops@gmail.com":
        raise ValidationError("delivery.to must remain emily.brown.ops@gmail.com unless the project rule changes.")
    if "jaretjb@gmail.com" not in delivery["cc"]:
        raise ValidationError("delivery.cc must include jaretjb@gmail.com unless the project rule changes.")

    roles = require(data.get("roles"), "roles")
    if not isinstance(roles, list):
        raise ValidationError("roles must be a list")
    if not 1 <= len(roles) <= 10:
        raise ValidationError(f"roles must contain between 1 and 10 entries, got {len(roles)}")

    seen_ranks: set[int] = set()
    for idx, role in enumerate(roles, start=1):
        if not isinstance(role, dict):
            raise ValidationError(f"roles[{idx}] must be an object")
        rank = require(role.get("rank"), f"roles[{idx}].rank")
        if rank in seen_ranks:
            raise ValidationError(f"Duplicate role rank detected: {rank}")
        seen_ranks.add(rank)
        for key in ["company", "title", "canonical_url", "quick_read", "key_highlights", "key_risk", "total_score", "rubric"]:
            require(role.get(key), f"roles[{idx}].{key}")
        validate_audience_copy(str(role["quick_read"]), f"roles[{idx}].quick_read")
        validate_audience_copy(str(role["key_risk"]), f"roles[{idx}].key_risk")
        if not isinstance(role["key_highlights"], list) or len(role["key_highlights"]) < 1:
            raise ValidationError(f"roles[{idx}].key_highlights must contain at least one item")
        for highlight_idx, highlight in enumerate(role["key_highlights"], start=1):
            validate_audience_copy(str(highlight), f"roles[{idx}].key_highlights[{highlight_idx}]")
        rubric = role["rubric"]
        if not isinstance(rubric, dict):
            raise ValidationError(f"roles[{idx}].rubric must be an object")
        rubric_total = 0
        for rubric_key, _, rubric_max in RUBRIC_ORDER:
            entry = require(rubric.get(rubric_key), f"roles[{idx}].rubric.{rubric_key}")
            if not isinstance(entry, dict):
                raise ValidationError(f"roles[{idx}].rubric.{rubric_key} must be an object")
            score = require(entry.get("score"), f"roles[{idx}].rubric.{rubric_key}.score")
            reason = require(entry.get("reason"), f"roles[{idx}].rubric.{rubric_key}.reason")
            entry_max = require(entry.get("max"), f"roles[{idx}].rubric.{rubric_key}.max")
            if entry_max != rubric_max:
                raise ValidationError(
                    f"roles[{idx}].rubric.{rubric_key}.max should be {rubric_max}, got {entry_max}"
                )
            if not isinstance(score, int):
                raise ValidationError(f"roles[{idx}].rubric.{rubric_key}.score must be an integer")
            if score < 0 or score > rubric_max:
                raise ValidationError(
                    f"roles[{idx}].rubric.{rubric_key}.score must be between 0 and {rubric_max}"
                )
            if not isinstance(reason, str) or not reason.strip():
                raise ValidationError(f"roles[{idx}].rubric.{rubric_key}.reason must be non-empty text")
            rubric_total += score
        if rubric_total != role["total_score"]:
            raise ValidationError(
                f"roles[{idx}] total_score mismatch: expected {rubric_total}, got {role['total_score']}"
            )

    require(data.get("changes"), "changes")
    for key in ["new", "moved_up", "removed_or_stale"]:
        if key not in data["changes"]:
            raise ValidationError(f"changes.{key} is required")
        for item_idx, item in enumerate(data["changes"].get(key) or [], start=1):
            validate_audience_copy(str(item), f"changes.{key}[{item_idx}]")

    quick_notes = require(data.get("quick_notes"), "quick_notes")
    if not isinstance(quick_notes, list) or not quick_notes:
        raise ValidationError("quick_notes must be a non-empty list")
    for note_idx, note in enumerate(quick_notes, start=1):
        validate_audience_copy(str(note), f"quick_notes[{note_idx}]")

    source_artifacts = require(data.get("source_artifacts"), "source_artifacts")
    output_artifacts = require(data.get("output_artifacts"), "output_artifacts")
    if not isinstance(source_artifacts, dict) or not isinstance(output_artifacts, dict):
        raise ValidationError("source_artifacts and output_artifacts must be objects")

    digest_md = resolve_path(base_dir, require(source_artifacts.get("digest_markdown"), "source_artifacts.digest_markdown"))
    comparison_md = resolve_path(base_dir, source_artifacts.get("comparison_markdown"))
    email_html = resolve_path(base_dir, require(output_artifacts.get("email_html"), "output_artifacts.email_html"))
    email_text = resolve_path(base_dir, require(output_artifacts.get("email_text"), "output_artifacts.email_text"))
    comparison_html = resolve_path(base_dir, output_artifacts.get("comparison_html"))

    if digest_md is None or not digest_md.exists():
        raise ValidationError(f"Digest markdown source not found: {digest_md}")
    if comparison_md is not None and not comparison_md.exists():
        raise ValidationError(f"Comparison markdown source not found: {comparison_md}")

    return {
        "digest_md": digest_md,
        "comparison_md": comparison_md,
        "email_html": email_html,
        "email_text": email_text,
        "comparison_html": comparison_html,
    }


def render_text(data: dict[str, Any], intro: str | None) -> str:
    lines: list[str] = []
    lines.append(f"Subject: {data['subject']}")
    lines.append("")
    if intro:
        lines.append(intro.strip())
        lines.append("")
    lines.append("Top roles right now")
    for role in sorted(data["roles"], key=lambda r: r["rank"]):
        lines.append("")
        lines.append(f"{role['rank']}) {role['company']} — {role['title']}")
        lines.append(f"Link: {role['canonical_url']}")
        lines.append(f"Quick read: {role['quick_read']}")
        lines.append("Key highlights: " + "; ".join(role["key_highlights"]))
        lines.append(f"Key risk factor: {role['key_risk']}")
        lines.append("Score breakdown:")
        for rubric_key, label, rubric_max in RUBRIC_ORDER:
            entry = role["rubric"][rubric_key]
            lines.append(f"- {label}: {entry['score']}/{rubric_max} — {entry['reason']}")
        lines.append(f"- Total: {role['total_score']}/100")

    lines.append("")
    lines.append("What changed since the last update")
    for label, key in [("New", "new"), ("Moved up", "moved_up"), ("Removed / stale / closed", "removed_or_stale")]:
        items = data["changes"].get(key) or []
        rendered = "; ".join(items) if items else "None."
        lines.append(f"- {label}: {rendered}")

    lines.append("")
    lines.append("Quick notes")
    for note in data["quick_notes"]:
        if note:
            lines.append(f"- {note}")

    lines.append("")
    lines.append("Best,")
    lines.append(data["author_name"])
    return "\n".join(lines).rstrip() + "\n"


def render_html(data: dict[str, Any], intro: str | None) -> str:
    role_blocks: list[str] = []
    for role in sorted(data["roles"], key=lambda r: r["rank"]):
        highlights = "; ".join(role["key_highlights"])
        rubric_items = "".join(
            f'<li style="margin:0 0 4px 0;"><strong>{label}:</strong> {entry["score"]}/{rubric_max} — {inline_markdown_to_html(entry["reason"])}</li>'
            for (rubric_key, label, rubric_max) in RUBRIC_ORDER
            for entry in [role["rubric"][rubric_key]]
        )
        role_blocks.append(
            f'''<section style="margin:0 0 18px 0;padding:16px;border:1px solid #e5e7eb;border-radius:14px;background:#ffffff;">
<div style="font-size:18px;font-weight:700;margin:0 0 10px 0;">{role['rank']}) <a href="{html.escape(role['canonical_url'], quote=True)}" style="color:#111827;text-decoration:none;">{html.escape(role['company'])} — {html.escape(role['title'])}</a></div>
<div style="font-size:14px;line-height:1.6;margin:0 0 6px 0;"><strong>Quick read:</strong> {inline_markdown_to_html(role['quick_read'])}</div>
<div style="font-size:14px;line-height:1.6;margin:0 0 6px 0;"><strong>Key highlights:</strong> {inline_markdown_to_html(highlights)}</div>
<div style="font-size:14px;line-height:1.6;margin:0 0 10px 0;"><strong>Key risk factor:</strong> {inline_markdown_to_html(role['key_risk'])}</div>
<div style="font-size:14px;font-weight:700;margin:0 0 6px 0;">Score breakdown</div>
<ul style="margin:0 0 8px 0;padding-left:18px;list-style-position:outside;font-size:14px;line-height:1.5;">{rubric_items}</ul>
<div style="font-size:14px;font-weight:700;">Total: {role['total_score']}/100</div>
</section>'''
        )

    change_blocks = []
    for label, key in [("New", "new"), ("Moved up", "moved_up"), ("Removed / stale / closed", "removed_or_stale")]:
        items = data["changes"].get(key) or []
        rendered = "; ".join(items) if items else "None."
        change_blocks.append(
            f'<li style="margin:0 0 6px 0;"><strong>{label}:</strong> {inline_markdown_to_html(rendered)}</li>'
        )

    quick_notes = "".join(
        f'<li style="margin:0 0 6px 0;">{inline_markdown_to_html(note)}</li>' for note in data["quick_notes"] if note
    )

    intro_html = ""
    if intro:
        intro_html = "".join(
            f'<p style="font-size:15px;line-height:1.6;margin:0 0 12px 0;">{inline_markdown_to_html(paragraph.strip())}</p>'
            for paragraph in intro.split("\n\n")
            if paragraph.strip()
        )

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(data['subject'])}</title>
</head>
<body style="margin:0;padding:0;background:#f6f8fb;font-family:Arial,Helvetica,sans-serif;color:#1f2937;">
  <div style="max-width:760px;margin:0 auto;padding:24px 16px;">
    <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;overflow:hidden;">
      <div style="padding:24px;border-bottom:1px solid #e5e7eb;">
        <div style="font-size:26px;font-weight:700;margin:0 0 8px 0;">{html.escape(data['subject'])}</div>
        <div style="font-size:14px;color:#6b7280;">Digest date: {html.escape(str(data['digest_date']))}</div>
      </div>
      <div style="padding:24px;">
        {intro_html}
        <div style="font-size:20px;font-weight:700;margin:12px 0 12px 0;">Top roles right now</div>
        {''.join(role_blocks)}
        <div style="font-size:20px;font-weight:700;margin:20px 0 10px 0;">What changed since the last update</div>
        <ul style="margin:0 0 0 18px;padding:0;font-size:14px;line-height:1.5;">{''.join(change_blocks)}</ul>
        <div style="font-size:20px;font-weight:700;margin:20px 0 10px 0;">Quick notes</div>
        <ul style="margin:0 0 0 18px;padding:0;font-size:14px;line-height:1.5;">{quick_notes}</ul>
        <p style="font-size:15px;line-height:1.6;margin:24px 0 0 0;">Best,<br>{html.escape(data['author_name'])}</p>
      </div>
    </div>
  </div>
</body>
</html>
'''


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    args = parse_args()
    data_path = Path(args.data).resolve()
    base_dir = Path(args.project_dir).resolve() if args.project_dir else infer_project_dir(data_path)

    try:
        data = load_yaml(data_path)
        paths = validate_bundle(data, base_dir)
        digest_md = paths["digest_md"]
        digest_text = digest_md.read_text(encoding="utf-8")
        metadata = extract_markdown_metadata(digest_text)

        md_subject = metadata.get("subject")
        if md_subject and md_subject != data["subject"]:
            raise ValidationError(
                f"Subject mismatch between markdown ('{md_subject}') and YAML ('{data['subject']}')."
            )

        md_signoff = metadata.get("signoff_name")
        if md_signoff and md_signoff != data["author_name"]:
            raise ValidationError(
                f"Signoff mismatch between markdown ('{md_signoff}') and YAML ('{data['author_name']}')."
            )

        intro = metadata.get("intro") or "Hi Emily,\n\nHere’s your latest shortlist update."
        validate_audience_copy(intro, "digest intro")
        text_output = render_text(data, intro)
        html_output = render_html(data, intro)

        ensure_parent(paths["email_text"])
        ensure_parent(paths["email_html"])
        paths["email_text"].write_text(text_output, encoding="utf-8")
        paths["email_html"].write_text(html_output, encoding="utf-8")

        comparison_md = paths.get("comparison_md")
        comparison_html = paths.get("comparison_html")
        if comparison_md and comparison_html:
            ensure_radar_assets(data, base_dir)
            comp_body = comparison_md.read_text(encoding="utf-8")
            comp_html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(comparison_md.stem)}</title>
  <style>
    body {{ margin:0; padding:0; background:#f6f8fb; font-family:Arial,Helvetica,sans-serif; color:#1f2937; }}
    .report-shell {{ max-width:900px; margin:0 auto; padding:24px 16px; }}
    .report-card {{ background:#ffffff; border:1px solid #e5e7eb; border-radius:16px; padding:24px; line-height:1.6; overflow:hidden; }}
    .report-card h1 {{ font-size:30px; line-height:1.2; margin:0 0 16px 0; }}
    .report-card h2 {{ font-size:22px; line-height:1.3; margin:28px 0 12px 0; }}
    .report-card p, .report-card li {{ font-size:15px; }}
    .report-card ul {{ padding-left:22px; }}
    .table-scroll {{ overflow-x:auto; overflow-y:hidden; margin:14px 0 20px 0; background:#ffffff; -webkit-overflow-scrolling:touch; }}
    .report-card table {{ width:100%; border-collapse:collapse; margin:0; font-size:13px; }}
    .report-card table.overview-table {{ width:100%; table-layout:fixed; }}
    .report-card table.wide-table {{ width:100%; min-width:980px; table-layout:fixed; }}
    .report-card th, .report-card td {{ border:1px solid #d0d7de; padding:9px 8px; vertical-align:top; white-space:normal; word-break:normal; overflow-wrap:normal; }}
    .report-card table.overview-table th:nth-child(1), .report-card table.overview-table td:nth-child(1) {{ width:42px; }}
    .report-card table.overview-table th:nth-child(2), .report-card table.overview-table td:nth-child(2) {{ width:86px; }}
    .report-card table.overview-table th:nth-child(3), .report-card table.overview-table td:nth-child(3) {{ width:160px; word-break:normal; overflow-wrap:normal; }}
    .report-card table.overview-table th:nth-child(4), .report-card table.overview-table td:nth-child(4) {{ width:124px; }}
    .report-card table.overview-table th:nth-child(5), .report-card table.overview-table td:nth-child(5) {{ width:118px; }}
    .report-card table.overview-table th:nth-child(6), .report-card table.overview-table td:nth-child(6) {{ width:72px; }}
    .report-card th {{ background:#f3f4f6; text-align:left; }}
    .report-card code {{ background:#f3f4f6; padding:1px 4px; border-radius:4px; }}
    .report-card figure svg {{ width:100%; height:auto; display:block; margin:0 auto; }}
    .role-card {{ margin:20px 0 0 0; padding:18px 18px 16px 18px; border:1px solid #e5e7eb; border-radius:16px; background:#fbfdff; box-shadow:0 1px 2px rgba(16,24,40,0.04); }}
    .role-card h2 {{ margin:0 0 12px 0; font-size:20px; }}
    .role-card > ul {{ margin:0; padding-left:0; list-style:none; }}
    .role-card > ul > li {{ margin:0 0 8px 0; }}
    .role-card ul ul {{ margin:8px 0 0 0; padding-left:18px; list-style:disc outside; }}
    .role-card ul ul li {{ margin:0 0 6px 0; }}
    .role-card figure {{ margin:16px 0; }}
  </style>
</head>
<body>
  <div class="report-shell">
    <div class="report-card">
      {render_markdown_document(comp_body, base_dir=comparison_md.parent)}
    </div>
  </div>
</body>
</html>
'''
            ensure_parent(comparison_html)
            comparison_html.write_text(comp_html, encoding="utf-8")

        print(f"Rendered text email: {paths['email_text']}")
        print(f"Rendered HTML email: {paths['email_html']}")
        if comparison_md and comparison_html:
            print(f"Rendered comparison HTML: {comparison_html}")
        return 0
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
