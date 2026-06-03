#!/usr/bin/env python3
"""Reconcile Emily scanner filtered output against Obsidian state.

This is a dry-run comparison helper. It reads scanner output plus Obsidian
Role State Ledger / Live Role Shortlist and writes review artifacts only. It
must not mutate canonical shortlist or ledger notes.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import io
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
VAULT = Path("/mnt/c/Users/Jaret/Obsidian/The Nexus")
PROJECT = VAULT / "40 Agent Nexus/Projects/Emily Job Search"
LEDGER = PROJECT / "Role State Ledger.md"
SHORTLIST = PROJECT / "Live Role Shortlist.md"
DEFAULT_FILTERED_GLOB = str(REPO_ROOT / "data" / "emily-scanner" / "filtered" / "*.json")
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "emily-scanner" / "reconciled"
DEFAULT_REPORT_DIR = VAULT / "20 Library/Research Reports/Emily Job Search/Research Runs"

LIVE_STATES = {"new", "active", "aging"}


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def latest_filtered_path() -> Path:
    paths = sorted(glob.glob(DEFAULT_FILTERED_GLOB))
    if not paths:
        raise FileNotFoundError(f"No filtered scanner artifacts match {DEFAULT_FILTERED_GLOB}")
    return Path(paths[-1])


def strip_md(text: str) -> str:
    text = text.strip()
    if text.startswith("<") and text.endswith(">"):
        return text[1:-1]
    m = re.search(r"\[([^\]]+)\]\(([^)]+)\)", text)
    if m:
        return m.group(2)
    return text.replace("\\|", "|").strip()


def normalize_title(title: str | None) -> str:
    if not title:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def normalize_url(url: str | None) -> str:
    if not url:
        return ""
    url = strip_md(url).split("?")[0].rstrip("/").lower()
    return url


def gh_jid(url: str | None) -> str | None:
    if not url:
        return None
    m = re.search(r"gh_jid=(\d+)", url)
    return m.group(1) if m else None


def url_keys(url: str | None) -> set[str]:
    raw = strip_md(url or "")
    keys = {normalize_url(raw)} if raw else set()
    jid = gh_jid(raw)
    if jid:
        keys.add(f"gh_jid:{jid}")
    return {k for k in keys if k}


def parse_table(path: Path, required_columns: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    headers: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            if in_table:
                break
            continue
        cells = [c.strip() for c in next(csv.reader(io.StringIO(line.strip().strip("|")), delimiter="|", escapechar="\\"))]
        if not headers:
            if all(col in cells for col in required_columns):
                headers = cells
                in_table = True
            continue
        if all(re.fullmatch(r":?-{3,}:?", c.strip()) for c in cells):
            continue
        if len(cells) < len(headers):
            cells += [""] * (len(headers) - len(cells))
        row = {headers[i]: cells[i] for i in range(min(len(headers), len(cells)))}
        rows.append(row)
    return rows


def build_state_indexes(ledger_rows: list[dict[str, str]], shortlist_rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    by_url: dict[str, dict[str, str]] = {}
    by_company_title: dict[str, dict[str, str]] = {}
    for row in ledger_rows:
        company = row.get("Company", "")
        title = row.get("Title", "")
        state = row.get("Current state", "")
        canonical = row.get("Canonical URL", "")
        record = {"source": "ledger", "company": company, "title": title, "state": state, "url": strip_md(canonical), "last_confirmed_live": row.get("Last confirmed live", ""), "last_reviewed": row.get("Last reviewed", "")}
        for key in url_keys(canonical):
            by_url[key] = record
        by_company_title[f"{company.lower()}::{normalize_title(title)}"] = record
    for row in shortlist_rows:
        company = row.get("Company", "")
        title = row.get("Title", "")
        state = row.get("State", "")
        canonical = row.get("Canonical link", "")
        record = {"source": "shortlist", "company": company, "title": title, "state": state, "url": strip_md(canonical), "last_confirmed_live": row.get("Last confirmed live", ""), "rank": row.get("Rank", ""), "score": row.get("Score", "")}
        for key in url_keys(canonical):
            by_url[key] = record
        by_company_title[f"{company.lower()}::{normalize_title(title)}"] = record
    return by_url, by_company_title


def find_match(candidate: dict[str, Any], by_url: dict[str, dict[str, str]], by_company_title: dict[str, dict[str, str]]) -> dict[str, str] | None:
    for key in url_keys(candidate.get("url")):
        if key in by_url:
            return by_url[key]
    key = f"{str(candidate.get('company') or '').lower()}::{normalize_title(candidate.get('title'))}"
    return by_company_title.get(key)


def reconcile_candidate(candidate: dict[str, Any], match: dict[str, str] | None) -> dict[str, Any]:
    out = dict(candidate)
    bucket = candidate.get("decision_bucket")
    if match:
        state = (match.get("state") or "").lower()
        if state in LIVE_STATES:
            comparison = f"already monitored in {match['source']} as {state}"
            reconciliation_bucket = "already_monitored"
        elif state in {"closed", "stale", "disqualified", "applied", "ignored", "archived"}:
            comparison = f"known historical {match['source']} record is {state}; keep as calibration/manual-review evidence"
            reconciliation_bucket = "known_historical_record"
        else:
            comparison = f"matched existing {match['source']} record with state {state or 'unknown'}"
            reconciliation_bucket = "matched_existing_unknown_state"
    elif bucket == "new_candidate":
        comparison = "not found in current ledger/shortlist by URL or exact company-title; potential add after direct review"
        reconciliation_bucket = "potential_add"
    elif bucket == "disqualified_false_positive":
        comparison = "not promoted; scanner/filter marked as false positive with disqualifier(s)"
        reconciliation_bucket = "scanner_disqualified"
    else:
        comparison = "not found in current ledger/shortlist; manual review only"
        reconciliation_bucket = "manual_review_unmatched"
    out["compared_to_obsidian_state"] = comparison
    out["reconciliation_bucket"] = reconciliation_bucket
    if match:
        out["obsidian_match"] = match
    return out


def markdown_link(url: str, label: str = "source") -> str:
    return f"[{label}]({url})" if url else "source missing"


def table_rows(items: list[dict[str, Any]], fields: list[str], limit: int | None = None) -> str:
    subset = items[:limit] if limit else items
    if not subset:
        return "_None._\n"
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for item in subset:
        vals: list[str] = []
        for field in fields:
            if field == "Role":
                vals.append(f"{item.get('company')} — {item.get('title')}")
            elif field == "Source":
                vals.append(markdown_link(str(item.get("url") or "")))
            elif field == "Observed":
                vals.append(str((item.get("raw_candidate_ref") or {}).get("observed_at") or item.get("reviewed_at") or ""))
            elif field == "Score":
                vals.append(str(item.get("review_priority_score", "")))
            elif field == "Bucket":
                vals.append(f"`{item.get('reconciliation_bucket') or item.get('decision_bucket')}`")
            elif field == "Why":
                vals.append("; ".join((item.get("reasons") or [])[:2]).replace("|", "/"))
            elif field == "Uncertainty":
                vals.append(str(item.get("compared_to_obsidian_state") or "").replace("|", "/"))
            else:
                vals.append(str(item.get(field, "")).replace("|", "/"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"


def write_report(report_path: Path, artifact: dict[str, Any], current_live_missing: list[dict[str, str]]) -> None:
    candidates = artifact["candidates"]
    counts: dict[str, int] = {}
    for c in candidates:
        counts[c["reconciliation_bucket"]] = counts.get(c["reconciliation_bucket"], 0) + 1
    already = [c for c in candidates if c["reconciliation_bucket"] == "already_monitored"]
    adds = [c for c in candidates if c["reconciliation_bucket"] == "potential_add"]
    disq = [c for c in candidates if c["reconciliation_bucket"] == "scanner_disqualified"]
    historical = [c for c in candidates if c["reconciliation_bucket"] == "known_historical_record"]
    manual = [c for c in candidates if c["reconciliation_bucket"] == "manual_review_unmatched"]
    top_adds = sorted(adds, key=lambda c: c.get("review_priority_score", 0), reverse=True)[:15]
    top_disq = sorted(disq, key=lambda c: c.get("review_priority_score", 0), reverse=True)[:12]
    content = f"""---
type: "research-run"
status: "complete"
created: "2026-05-17"
project: "Emily Job Search"
card: "EJS-023"
---
# 2026-05-17 - scanner dry-run reconciliation

## Summary

Dry-run reconciliation compared the latest scanner filtered artifact against [Role State Ledger](../../../../40%20Agent%20Nexus/Projects/Emily%20Job%20Search/Role%20State%20Ledger.md) and [Live Role Shortlist](../../../../40%20Agent%20Nexus/Projects/Emily%20Job%20Search/Live%20Role%20Shortlist.md). This report is evidence for review only and makes **no automatic canonical mutations**.

- Filtered input: [`{Path(artifact['filtered_artifact']).name}`](file://{artifact['filtered_artifact']})
- Reconciled JSON: [`{Path(artifact['reconciled_artifact']).name}`](file://{artifact['reconciled_artifact']})
- Candidates compared: {artifact['candidate_count']}
- Already monitored / still live: {counts.get('already_monitored', 0)}
- Potential adds requiring direct review: {counts.get('potential_add', 0)}
- Scanner-disqualified false positives: {counts.get('scanner_disqualified', 0)}
- Known historical records resurfacing in scanner output: {counts.get('known_historical_record', 0)}
- Manual-review unmatched/noisy records: {counts.get('manual_review_unmatched', 0)}

## Already monitored / still live

{table_rows(already, ['Role', 'Source', 'Observed', 'Score', 'Bucket', 'Uncertainty'])}

## Current shortlist coverage gaps

These are current live shortlist roles not matched in the configured scanner output. Treat as coverage limits, not removals, unless a later direct source check confirms closure.

"""
    if current_live_missing:
        content += "| Role | State | Last confirmed live | Canonical source | Note |\n| --- | --- | --- | --- | --- |\n"
        for row in current_live_missing:
            content += f"| {row['company']} — {row['title']} | `{row['state']}` | {row.get('last_confirmed_live','')} | {markdown_link(row.get('url',''))} | Not covered by the current Greenhouse/Lever scanner target output; do not mark stale from scanner absence alone. |\n"
    else:
        content += "_None._\n"
    content += f"""
## Potential adds for manual review

Top-ranked scanner candidates not found in the current ledger/shortlist. These are **not** canonical adds yet; they need direct posting review, lane judgment, and compensation/geography confirmation.

{table_rows(top_adds, ['Role', 'Source', 'Observed', 'Score', 'Bucket', 'Why', 'Uncertainty'])}

## False positives / disqualified calibration

Scanner output the filter rejected with plain-English reasons.

{table_rows(top_disq, ['Role', 'Source', 'Observed', 'Score', 'Bucket', 'Why'])}

## Known historical records resurfacing

{table_rows(historical, ['Role', 'Source', 'Observed', 'Score', 'Bucket', 'Why', 'Uncertainty'], limit=20)}

## Manual-review noise

{len(manual)} scanner records did not match canonical state and did not clear the filter strongly enough for potential-add treatment. Most are broad company-board noise and should stay out of the ledger unless a future targeted pass surfaces direct fit evidence.

## Uncertainty and manual-review notes

- Scanner absence is not closure evidence for companies/providers outside this configured scan, especially Celigo's company-hosted page.
- Greenhouse URLs may appear as board URLs, job IDs, or `gh_jid` links; this reconciliation normalizes exact URLs and Greenhouse job IDs where visible, then falls back to exact company-title matches.
- Potential adds are ranked for review queueing only. Do not update [Role State Ledger](../../../../40%20Agent%20Nexus/Projects/Emily%20Job%20Search/Role%20State%20Ledger.md) or [Live Role Shortlist](../../../../40%20Agent%20Nexus/Projects/Emily%20Job%20Search/Live%20Role%20Shortlist.md) until Sammy/Jaret review the direct posting evidence.
- No email, application, outreach, login, or form submission was performed.

#emily-job-search #scanner #research-run #dry-run
"""
    report_path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Dry-run reconcile Emily scanner output against Obsidian state")
    p.add_argument("--filtered", type=Path, default=None)
    p.add_argument("--ledger", type=Path, default=LEDGER)
    p.add_argument("--shortlist", type=Path, default=SHORTLIST)
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    filtered_path = args.filtered or latest_filtered_path()
    filtered = json.loads(filtered_path.read_text(encoding="utf-8"))
    ledger_rows = parse_table(args.ledger, ["Company", "Title", "Current state", "Canonical URL"])
    shortlist_rows = parse_table(args.shortlist, ["Rank", "Score", "Company", "Title", "State", "Canonical link"])
    by_url, by_company_title = build_state_indexes(ledger_rows, shortlist_rows)
    reconciled = [reconcile_candidate(c, find_match(c, by_url, by_company_title)) for c in filtered.get("candidates", [])]
    counts: dict[str, int] = {}
    for c in reconciled:
        counts[c["reconciliation_bucket"]] = counts.get(c["reconciliation_bucket"], 0) + 1
    scanner_url_keys = set()
    scanner_company_titles = set()
    for c in filtered.get("candidates", []):
        scanner_url_keys.update(url_keys(c.get("url")))
        scanner_company_titles.add(f"{str(c.get('company') or '').lower()}::{normalize_title(c.get('title'))}")
    current_live_missing: list[dict[str, str]] = []
    for row in shortlist_rows:
        record = {"company": row.get("Company", ""), "title": row.get("Title", ""), "state": row.get("State", ""), "url": strip_md(row.get("Canonical link", "")), "last_confirmed_live": row.get("Last confirmed live", "")}
        keys = url_keys(row.get("Canonical link", ""))
        ct = f"{record['company'].lower()}::{normalize_title(record['title'])}"
        if not (keys & scanner_url_keys) and ct not in scanner_company_titles:
            current_live_missing.append(record)
    reviewed_at = utc_now()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = reviewed_at.replace(":", "").replace("-", "")
    output_path = args.output_dir / f"emily-scanner-reconciled-{stamp}.json"
    artifact = {
        "schema_version": 1,
        "record_type": "emily_scanner_reconciled_run",
        "filtered_artifact": str(filtered_path),
        "reconciled_artifact": str(output_path),
        "reviewed_at": reviewed_at,
        "candidate_count": len(reconciled),
        "reconciliation_bucket_counts": counts,
        "current_live_missing_from_scan": current_live_missing,
        "candidates": reconciled,
    }
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report_path = args.report_dir / "2026-05-17 - scanner dry-run reconciliation.md"
    write_report(report_path, artifact, current_live_missing)
    print(json.dumps({"filtered_artifact": str(filtered_path), "reconciled_artifact": str(output_path), "report_path": str(report_path), "candidate_count": len(reconciled), "reconciliation_bucket_counts": counts, "current_live_missing_from_scan": current_live_missing}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
