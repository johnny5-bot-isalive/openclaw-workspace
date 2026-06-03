#!/usr/bin/env python3
"""Generate a compact review-only scanner summary from reconciled output.

This script creates an internal markdown summary for Sammy/Jaret review. It never
sends email, triggers digest delivery, submits applications, logs in, fills
forms, or mutates canonical Obsidian role-state notes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
VAULT = Path("/mnt/c/Users/Jaret/Obsidian/The Nexus")
PROJECT = VAULT / "40 Agent Nexus/Projects/Emily Job Search"
DEFAULT_RECONCILED_GLOB = str(REPO_ROOT / "data" / "emily-scanner" / "reconciled" / "*.json")
DEFAULT_OUTPUT_DIR = PROJECT / "Scanner Summaries"

GUARDRAIL = "Review-only scanner evidence. Do not email, apply, outreach, log in, fill forms, trigger scanner-based digest sends, or mutate canonical role state from this summary alone."


def today_iso() -> str:
    return dt.datetime.now(dt.UTC).date().isoformat()


def latest_reconciled_path() -> Path:
    paths = sorted(glob.glob(DEFAULT_RECONCILED_GLOB))
    if not paths:
        raise FileNotFoundError(f"No reconciled scanner artifacts match {DEFAULT_RECONCILED_GLOB}")
    return Path(paths[-1])


def link(url: str | None, label: str = "source") -> str:
    if url and str(url).startswith("http"):
        return f"[{label}]({url})"
    return label if not url else str(url)


def bucket(items: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    return [x for x in items if x.get("reconciliation_bucket") == name]


def top(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return sorted(items, key=lambda x: x.get("review_priority_score", 0), reverse=True)[:limit]


def table(items: list[dict[str, Any]], limit: int | None = None) -> str:
    rows = items[:limit] if limit else items
    if not rows:
        return "_None._\n"
    out = ["| Role | Score | Source | Why / note |", "| --- | ---: | --- | --- |"]
    for item in rows:
        role = f"{item.get('company', '')} — {item.get('title', '')}".replace("|", "/")
        score = str(item.get("review_priority_score", ""))
        source = link(item.get("url"))
        reasons = item.get("reasons") or []
        note = item.get("compared_to_obsidian_state") or "; ".join(reasons[:2]) or "manual review needed"
        out.append(f"| {role} | {score} | {source} | {str(note).replace('|', '/')} |")
    return "\n".join(out) + "\n"


def write_summary(reconciled_path: Path, output_dir: Path, output_path: Path | None = None, top_n: int = 10) -> Path:
    data = json.loads(reconciled_path.read_text(encoding="utf-8"))
    candidates = data.get("candidates", [])
    counts = data.get("reconciliation_bucket_counts", {})
    already = bucket(candidates, "already_monitored")
    adds = top(bucket(candidates, "potential_add"), top_n)
    disq = top(bucket(candidates, "scanner_disqualified"), min(8, top_n))
    historical = bucket(candidates, "known_historical_record")
    manual = bucket(candidates, "manual_review_unmatched")
    missing = data.get("current_live_missing_from_scan", [])
    created = today_iso()
    content = f"""---
type: "scanner-summary"
status: "draft"
created: "{created}"
project: "Emily Job Search"
review_only: true
source_artifact: "{reconciled_path}"
---
# {created} - Scanner Summary Review

## 0. Review-only gate
{GUARDRAIL}

This summary is an internal scanner-review/dashboard surface. It is **not** an Emily-facing digest, not a send trigger, and not canonical role state.

## 1. Run snapshot
- Reconciled artifact: [`{reconciled_path.name}`](file://{reconciled_path})
- Candidate count: {data.get('candidate_count', len(candidates))}
- Already monitored: {counts.get('already_monitored', 0)}
- Potential adds needing direct review: {counts.get('potential_add', 0)}
- Scanner-disqualified false positives: {counts.get('scanner_disqualified', 0)}
- Known historical resurfacing records: {counts.get('known_historical_record', 0)}
- Manual-review/noisy unmatched records: {counts.get('manual_review_unmatched', 0)}

## 2. Dashboard recommendation
Use this as a **Sammy/Jaret internal review widget** before a discovery or digest-prep pass. Do **not** include it directly in Emily-facing digest copy yet; translate any accepted finding into normal plain-English role notes only after direct review and canonical updates.

Best use:
- quick count check after scanner runs,
- shortlist coverage-gap warning,
- top potential-add queue for direct review,
- noise/false-positive pressure gauge.

Do not use for:
- automatic ledger/shortlist mutation,
- removal decisions from scanner absence,
- scanner-triggered emails,
- application or outreach workflows.

## 3. Already monitored roles seen by scanner
{table(already)}

## 4. Current shortlist coverage gaps
Treat these as scanner coverage limits, not stale/closed evidence.

"""
    if missing:
        content += "| Role | State | Last confirmed live | Source | Note |\n| --- | --- | --- | --- | --- |\n"
        for item in missing:
            role = f"{item.get('company')} — {item.get('title')}".replace("|", "/")
            content += f"| {role} | `{item.get('state','')}` | {item.get('last_confirmed_live','')} | {link(item.get('url'))} | Missing from scanner output; direct source review controls freshness. |\n"
    else:
        content += "_None._\n"
    content += f"""
## 5. Top potential adds for direct review
These are not recommendations to add or apply. They are a review queue.

{table(adds)}

## 6. False-positive / noise pressure
{table(disq)}

## 7. Historical records resurfacing
{table(historical)}

## 8. Manual-review noise
{len(manual)} records were unmatched/noisy after filtering. Treat the count as scan-quality telemetry, not as a task list.

## 9. Digest-facing rule
If a scanner finding is accepted after direct review, convert it into normal digest language through [Digest Render Contract](../Digest%20Render%20Contract.md): plain English, direct job link, no scanner/research mechanics, no `validated/still resolves/freshness/live set` phrasing, and no send until the normal refresh/render/QA gate permits it.

#emily-job-search #scanner #summary #review-only
"""
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = output_dir / f"Scanner Summary Review - {created}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate an internal review-only scanner summary")
    p.add_argument("--reconciled", type=Path, default=None)
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--top", type=int, default=10)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    reconciled = args.reconciled or latest_reconciled_path()
    out = write_summary(reconciled, args.output_dir, args.output, args.top)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
