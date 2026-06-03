#!/usr/bin/env python3
"""Generate review-only Emily tailoring packets from role-evaluation notes.

This helper is deliberately local and side-effect-light: it reads a completed
role evaluation plus canonical positioning notes, then writes a draft Markdown
packet. It never sends email, submits applications, logs in, fills forms, or
mutates Obsidian role-state notes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path
from typing import Any

VAULT = Path("/mnt/c/Users/Jaret/Obsidian/The Nexus")
PROJECT = VAULT / "40 Agent Nexus/Projects/Emily Job Search"
DEFAULT_MASTER = PROJECT / "Resumes/Resume Master Draft.md"
DEFAULT_POSITIONING = PROJECT / "Resumes/Resume and Cover Letter Positioning Guide.md"
DEFAULT_OUTPUT_DIR = PROJECT / "Resumes/Tailoring Drafts"

REVIEW_GUARDRAIL = "Review-only draft. Do not email, apply, submit, contact recruiters, log in, fill forms, or mutate canonical role state without the normal approval gates."


def today_iso() -> str:
    return dt.datetime.now(dt.UTC).date().isoformat()


def slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return value[:80] or "role"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        data[key.strip()] = val.strip().strip('"')
    return data, body


def section(text: str, heading_prefix: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading_prefix)}.*$", re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return ""
    next_h = re.search(r"^##\s+", text[m.end() :], re.MULTILINE)
    end = m.end() + next_h.start() if next_h else len(text)
    return text[m.end() : end].strip()


def first_frontmatter_or_line(meta: dict[str, str], body: str, key: str, label: str) -> str:
    if meta.get(key):
        return meta[key]
    m = re.search(rf"^- {re.escape(label)}:\s*(.+)$", body, re.MULTILINE)
    return m.group(1).strip() if m else ""


def compact_excerpt(text: str, heading: str, max_chars: int = 1200) -> str:
    sec = section(text, heading)
    if not sec:
        return "_No explicit section found in source evaluation._"
    sec = sec.strip()
    return sec if len(sec) <= max_chars else sec[: max_chars - 20].rstrip() + "…"


def make_packet(evaluation_path: Path, master_path: Path, positioning_path: Path, output_dir: Path, output_path: Path | None = None) -> Path:
    evaluation_text = evaluation_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(evaluation_text)
    master_text = master_path.read_text(encoding="utf-8") if master_path.exists() else ""
    positioning_text = positioning_path.read_text(encoding="utf-8") if positioning_path.exists() else ""

    company = first_frontmatter_or_line(meta, body, "company", "Company") or "Company"
    role = first_frontmatter_or_line(meta, body, "role", "Role") or "Role"
    source = first_frontmatter_or_line(meta, body, "source", "Source URL") or ""
    created = today_iso()

    role_summary = compact_excerpt(body, "A. Role summary")
    fit_rationale = compact_excerpt(body, "B. Emily-fit rationale")
    caveats = compact_excerpt(body, "C. Caveats, blockers, and mitigation")
    tailoring_plan = compact_excerpt(body, "F. Resume-tailoring plan")
    story_angles = compact_excerpt(body, "G. Interview and story angles")
    app_answers = compact_excerpt(body, "H. Draft application answers")

    master_summary = section(master_text, "Professional Summary") or "_Resume master summary not found._"
    leadership_focus = section(master_text, "Leadership Focus") or "_Leadership focus not found._"
    positioning_rules = section(positioning_text, "Resume rules to reuse") or "_Positioning guide resume rules not found._"
    cover_letter_rules = section(positioning_text, "Cover letter rules to reuse") or "_Positioning guide cover-letter rules not found._"

    title = f"{created} - {company} - {role} tailoring packet"
    source_line = f"- Source: [{source}]({source})" if source.startswith("http") else f"- Source: {source or 'not provided'}"
    content = f"""---
type: "tailoring-packet"
status: "draft"
created: "{created}"
project: "Emily Job Search"
company: "{company}"
role: "{role}"
source_evaluation: "{evaluation_path}"
review_only: true
---
# {title}

## 0. Review-only gate
- {REVIEW_GUARDRAIL}
- External action status: **none**
- Canonical state status: **not updated from this packet**
- Human review required before any submitted resume, application answer, email, outreach, login, or form submission.

## 1. Source evidence
- Role evaluation: [{evaluation_path.name}](file://{evaluation_path})
{source_line}
- Resume baseline: [Resume Master Draft](../Resume%20Master%20Draft.md)
- Positioning guide: [Resume and Cover Letter Positioning Guide](../Resume%20and%20Cover%20Letter%20Positioning%20Guide.md)

### Role summary excerpt
{role_summary}

### Fit rationale excerpt
{fit_rationale}

### Caveats / blockers excerpt
{caveats}

## 2. Tailoring strategy from evaluation
{tailoring_plan}

## 3. Baseline positioning to preserve
### Current master summary
{master_summary}

### Current leadership focus
{leadership_focus}

### Reusable resume rules
{positioning_rules}

## 4. Draft resume direction
### Headline options
- **Option A:** Digital Operations, eCommerce & Launch Excellence Leader
- **Option B:** Enterprise Digital Operations & GTM Systems Leader
- **Option C:** Digital Platform, Workflow & Transformation Operations Leader

### Summary adaptation checklist
- Keep Emily framed as an enterprise operator, not a narrow content producer.
- Name the role's strongest matching lane from the evaluation: digital ops / eCommerce ops / web ops / content ops / creative ops systems / transformation / operations-heavy GTM.
- Preserve truthful scale: ~1.2B annual customer interactions, 40+ concurrent monthly initiatives, 3,000+ annual launches, 200+ page portfolio, 200% velocity gain, 50% SLA reduction, $500K savings, 117% YoY revenue increase, 50% upgrade lift.
- Add role-specific language only when it is supported by the evaluation or known resume evidence.

### Bullet-selection plan
| Resume area | Bring forward | Use when role needs | Caution |
| --- | --- | --- | --- |
| AT&T current role | GTM/launch strategy, 40+ initiatives, executive analytics cadence, revenue/upgrade outcomes | senior operating ownership, commercial impact, cross-functional prioritization | Do not overstate formal product/engineering ownership. |
| AT&T digital ops role | workflows, operating standards, launch governance, 3,000+ launches, 200% velocity, 50% SLA reduction, $500K savings | systems/process scale, operating model design, delivery reliability | Keep content-production framing subordinate to operations. |
| AT&T principal PM role | DAM/CMS implementation, platform constraints, strategy-led delivery model | platform/tooling fluency, transformation foundation | Avoid turning this into a tools list. |
| Microsoft/Bing Ads | advertising-adjacent content engine and global web launches | ad/eCommerce/GTM adjacency | Do not claim ad-tech/ad-ops ownership unless Emily confirms it. |
| Nordstrom | early eCommerce and digital campaign delivery | retail/eCommerce credibility | Keep brief unless retail/luxury/eCommerce is central. |

## 5. Cover letter / note direction
{cover_letter_rules}

Suggested proof structure:
1. Enterprise scale and role-relevant operating lane.
2. Operating model / launch governance / workflow systems evidence.
3. Measurable business outcome tied to the role's needs.

## 6. Interview/story angles
{story_angles}

## 7. Draft application answers, if useful
{app_answers}

Do not use any draft answer externally until a human verifies every claim and approves submission.

## 8. Truthfulness and approval checklist
- [ ] Every tailored claim traces to the role evaluation, source posting, master resume, or known Emily history.
- [ ] Any uncertain tools/domains are listed as questions rather than claims.
- [ ] No unsupported claims about Salesforce, Snowflake, SQL, GenAI ownership, ad-tech/ad-ops ownership, offshore resources, budget authority, or formal people-management scope.
- [ ] No canonical role-state note was changed from this packet alone.
- [ ] No email/application/outreach/login/form submission happened.
- [ ] Human review completed before any external use.

## 9. Open questions for Emily/Jaret
- Which role-specific claims need Emily confirmation before finalizing?
- Are there missing examples around tools, vendors, data workflows, automation, people leadership, or campaign lifecycle ownership?
- Should this packet become a final resume variant, stay as a draft, or be rejected?

#emily-job-search #resume #tailoring #review-only
"""
    if output_path is None:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{created} - {slugify(company)} - {slugify(role)} tailoring packet.md"
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a review-only Emily tailoring packet from a role evaluation")
    parser.add_argument("evaluation", type=Path, help="Path to a completed role-evaluation markdown note")
    parser.add_argument("--master", type=Path, default=DEFAULT_MASTER)
    parser.add_argument("--positioning", type=Path, default=DEFAULT_POSITIONING)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = make_packet(args.evaluation, args.master, args.positioning, args.output_dir, args.output)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
