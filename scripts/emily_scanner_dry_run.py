#!/usr/bin/env python3
"""Read-only ATS scanner dry-run for the Emily Job Search project.

This script reads config/emily_scanner_targets.yaml, queries public ATS job-board
endpoints, and writes a dated raw-candidate artifact. It never logs in, submits
forms, applies to jobs, sends email, or mutates Obsidian canonical notes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import requests
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "config" / "emily_scanner_targets.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "emily-scanner" / "raw"
USER_AGENT = "OpenClaw Emily scanner dry-run/0.1 (+read-only public ATS check)"


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data and data.strip():
            self.parts.append(data.strip())

    def text(self) -> str:
        return " ".join(self.parts)


def html_to_text(value: Any) -> str:
    if not value:
        return ""
    parser = TextExtractor()
    parser.feed(str(value))
    return re.sub(r"\s+", " ", html.unescape(parser.text())).strip()


def extract_salary_text(*values: Any) -> str | None:
    text = " \n".join(html_to_text(v) for v in values if v)
    if not text:
        return None
    # Capture compact compensation snippets without pretending to normalize pay.
    patterns = [
        r"(?:\$\s?\d{2,3}[\d,]*(?:\.\d+)?\s*(?:-|–|to)\s*\$?\s?\d{2,3}[\d,]*(?:\.\d+)?(?:\s?(?:USD|CAD))?(?:\s?(?:base|salary|annually|per year|/year|yr))?)",
        r"(?:base salary|salary range|compensation range|pay range)[^.]{0,220}",
    ]
    snippets: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            snippet = re.sub(r"\s+", " ", match.group(0)).strip(" .;,")
            if snippet and snippet not in snippets:
                snippets.append(snippet)
            if len(snippets) >= 3:
                break
        if snippets:
            break
    return " | ".join(snippets) if snippets else None


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def session(timeout: int) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json,text/html;q=0.8,*/*;q=0.5"})
    s.request_timeout = timeout  # type: ignore[attr-defined]
    return s


def fetch_json(s: requests.Session, url: str) -> tuple[int, Any, str | None]:
    try:
        resp = s.get(url, timeout=getattr(s, "request_timeout", 20), allow_redirects=True)
    except requests.RequestException as exc:
        return 0, None, f"request_error: {exc}"
    if resp.status_code >= 400:
        return resp.status_code, None, f"http_{resp.status_code}"
    try:
        return resp.status_code, resp.json(), None
    except ValueError as exc:
        return resp.status_code, None, f"json_error: {exc}"


def greenhouse_candidates(s: requests.Session, target: dict[str, Any], observed_at: str) -> tuple[list[dict[str, Any]], list[str]]:
    token = target.get("provider_config", {}).get("board_token")
    if not token:
        return [], ["missing provider_config.board_token"]
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    status_code, payload, err = fetch_json(s, url)
    if err:
        return [], [f"{target['id']}: {err} from {url}"]
    jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
    candidates: list[dict[str, Any]] = []
    for job in jobs:
        location = job.get("location") or {}
        departments = job.get("departments") or []
        offices = job.get("offices") or []
        raw_department = ", ".join(d.get("name", "") for d in departments if d.get("name")) or None
        raw_team = ", ".join(o.get("name", "") for o in offices if o.get("name")) or None
        content = job.get("content") or ""
        metadata = job.get("metadata") or []
        metadata_text = " ".join(str(item.get("value", "")) for item in metadata if isinstance(item, dict))
        candidates.append({
            "company": target["company"],
            "target_id": target["id"],
            "title": job.get("title") or "",
            "location": location.get("name") or "",
            "url": job.get("absolute_url") or target.get("ats_url"),
            "provider": target["provider"],
            "observed_at": observed_at,
            "source_status": "listed",
            "salary_text": extract_salary_text(content, metadata_text),
            "raw_department": raw_department,
            "raw_team": raw_team,
            "employment_type": None,
            "travel_text": None,
            "source_payload_ref": None,
            "extraction_notes": [f"greenhouse_public_api_status={status_code}"],
        })
    return candidates, []


def lever_candidates(s: requests.Session, target: dict[str, Any], observed_at: str) -> tuple[list[dict[str, Any]], list[str]]:
    slug = target.get("provider_config", {}).get("company_slug")
    if not slug:
        return [], ["missing provider_config.company_slug"]
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    status_code, payload, err = fetch_json(s, url)
    if err:
        return [], [f"{target['id']}: {err} from {url}"]
    postings = payload if isinstance(payload, list) else []
    candidates: list[dict[str, Any]] = []
    for posting in postings:
        categories = posting.get("categories") or {}
        lists = posting.get("lists") or []
        list_text = " ".join(item.get("text", "") + " " + item.get("content", "") for item in lists if isinstance(item, dict))
        description = " ".join(str(posting.get(k) or "") for k in ["description", "descriptionPlain", "additional"])
        candidates.append({
            "company": target["company"],
            "target_id": target["id"],
            "title": posting.get("text") or "",
            "location": categories.get("location") or "",
            "url": posting.get("hostedUrl") or posting.get("applyUrl") or target.get("ats_url"),
            "provider": target["provider"],
            "observed_at": observed_at,
            "source_status": "listed",
            "salary_text": extract_salary_text(description, list_text),
            "raw_department": categories.get("department"),
            "raw_team": categories.get("team"),
            "employment_type": categories.get("commitment"),
            "travel_text": None,
            "source_payload_ref": None,
            "extraction_notes": [f"lever_public_api_status={status_code}"],
        })
    return candidates, []


def scan_target(s: requests.Session, target: dict[str, Any], observed_at: str) -> tuple[list[dict[str, Any]], list[str]]:
    provider = target.get("provider")
    if provider == "greenhouse_job_boards":
        return greenhouse_candidates(s, target, observed_at)
    if provider == "lever":
        return lever_candidates(s, target, observed_at)
    return [], [f"{target.get('id', '<unknown>')}: unsupported provider {provider!r}"]


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or not isinstance(data.get("targets"), list):
        raise ValueError(f"Invalid scanner config: {path}")
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emily Job Search read-only ATS scanner dry-run")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--target", action="append", default=[], help="Target id or company to include; may repeat")
    parser.add_argument("--include-disabled", action="store_true")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--polite-delay", type=float, default=None, help="Override per-request delay between targets")
    parser.add_argument("--no-write", action="store_true", help="Print summary only; do not write artifact")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Default posture; retained for explicitness")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    selected = {v.lower() for v in args.target}
    targets = []
    for target in config["targets"]:
        if not args.include_disabled and not target.get("enabled", False):
            continue
        if selected and target.get("id", "").lower() not in selected and target.get("company", "").lower() not in selected:
            continue
        targets.append(target)

    observed_at = utc_now()
    started = time.time()
    http = session(args.timeout)
    all_candidates: list[dict[str, Any]] = []
    errors: list[str] = []
    provider_defaults = config.get("provider_defaults", {}) or {}

    for index, target in enumerate(targets):
        candidates, target_errors = scan_target(http, target, observed_at)
        all_candidates.extend(candidates)
        errors.extend(target_errors)
        if index < len(targets) - 1:
            default_delay = provider_defaults.get(target.get("provider"), {}).get("polite_delay_seconds", 1.5)
            time.sleep(args.polite_delay if args.polite_delay is not None else float(default_delay))

    artifact = {
        "schema_version": 1,
        "record_type": "emily_scanner_raw_run",
        "dry_run": True,
        "config_path": str(args.config),
        "observed_at": observed_at,
        "duration_seconds": round(time.time() - started, 2),
        "targets_scanned": [t["id"] for t in targets],
        "guardrails": config.get("guardrails", {}),
        "candidate_count": len(all_candidates),
        "error_count": len(errors),
        "errors": errors,
        "candidates": all_candidates,
    }

    output_path = None
    if not args.no_write:
        stamp = observed_at.replace(":", "").replace("-", "")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = args.output_dir / f"emily-scanner-raw-{stamp}.json"
        output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "dry_run": True,
        "targets_scanned": artifact["targets_scanned"],
        "candidate_count": len(all_candidates),
        "error_count": len(errors),
        "output_path": str(output_path) if output_path else None,
    }, indent=2, ensure_ascii=False))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
