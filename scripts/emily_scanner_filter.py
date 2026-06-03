#!/usr/bin/env python3
"""Emily-specific filter/ranking layer for raw scanner output.

Reads a raw artifact produced by scripts/emily_scanner_dry_run.py and writes a
review-only filtered artifact. This script does not mutate Obsidian canonical
state, send messages, submit applications, or treat scanner output as truth.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "config" / "emily_scanner_targets.yaml"
DEFAULT_RAW_GLOB = str(REPO_ROOT / "data" / "emily-scanner" / "raw" / "*.json")
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "emily-scanner" / "filtered"

ROLE_FAMILY_SIGNALS = {
    "ecommerce_operations": ["ecommerce", "e-commerce", "commerce", "marketplace"],
    "digital_operations": ["digital", "platform", "systems", "operations", "ops"],
    "web_operations": ["web", "site", "website"],
    "content_operations": ["content", "taxonomy", "localization"],
    "creative_operations_systems": ["creative operations", "creative ops", "asset", "production workflow"],
    "digital_transformation": ["transformation", "change management", "enablement", "ai transformation", "automation"],
    "omnichannel_or_merchandising_operations": ["omnichannel", "merchandising", "merchandise", "retail planning"],
    "operations_heavy_gtm": ["gtm technology", "go-to-market", "gtm", "strategy & operations", "strategy and operations", "services operations", "business operations", "planning"],
}

NEGATIVE_SIGNALS = {
    "lifecycle/growth-marketing specialization": ["lifecycle", "growth marketing", "crm marketing", "retention marketing"],
    "brand/experiential retail drift": ["brand experiences", "experiential", "events", "retail stores", "consumer insights", "loyalty"],
    "patient/customer-care support lane": ["patient", "clinical", "customer care", "support operations", "customer support"],
    "pure sales/account role": ["account executive", "sales manager", "sales representative", "partnerships manager"],
    "engineering/product-only lane": ["software engineer", "data engineer", "product manager", "designer", "scientist"],
    "people/finance/org-design transformation drift": ["workforce", "people planning", "organizational design", "financial planning"],
}

LOCAL_TERMS = ["seattle", "bellevue", "bothell", "redmond", "kirkland", "duvall", "woodinville", "washington", " wa", "us, washington"]
REMOTE_US_TERMS = ["united states - remote", "remote, united states", "remote us", "remote, us", "united states"]
GEO_MISMATCH_TERMS = ["canada", "ontario", "british columbia", "india", "philippines", "uk", "london", "germany"]


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def latest_raw_path() -> Path:
    paths = sorted(glob.glob(DEFAULT_RAW_GLOB))
    if not paths:
        raise FileNotFoundError(f"No raw scanner artifacts match {DEFAULT_RAW_GLOB}")
    return Path(paths[-1])


def norm_url(url: str | None) -> str:
    if not url:
        return ""
    return url.split("?")[0].rstrip("/").lower()


def load_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("targets"), list):
        raise ValueError(f"Invalid config: {path}")
    return data


def build_target_maps(config: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    target_by_id = {t["id"]: t for t in config.get("targets", [])}
    seed_by_url: dict[str, str] = {}
    for target in config.get("targets", []):
        for url in target.get("known_role_urls") or []:
            seed_by_url[norm_url(url)] = target.get("seed_status", "")
            gh_match = re.search(r"gh_jid=(\d+)", url)
            if gh_match:
                seed_by_url[f"gh_jid={gh_match.group(1)}"] = target.get("seed_status", "")
    return target_by_id, seed_by_url


def seed_status_for(candidate: dict[str, Any], seed_by_url: dict[str, str]) -> str | None:
    raw_url = str(candidate.get("url") or "").lower()
    normalized = norm_url(raw_url)
    if normalized in seed_by_url:
        return seed_by_url[normalized]
    for key, value in seed_by_url.items():
        if key.startswith("gh_jid=") and key in raw_url:
            return value
    return None


def text_for(candidate: dict[str, Any]) -> str:
    pieces = [
        candidate.get("title"), candidate.get("location"), candidate.get("salary_text"),
        candidate.get("raw_department"), candidate.get("raw_team"), candidate.get("employment_type"),
    ]
    return " ".join(str(p) for p in pieces if p).lower()


def role_family(candidate: dict[str, Any]) -> tuple[str, list[str]]:
    text = text_for(candidate)
    signals: list[str] = []
    for family, terms in ROLE_FAMILY_SIGNALS.items():
        if any(term in text for term in terms):
            signals.append(family)
    if any(s in signals for s in ["ecommerce_operations", "digital_operations", "operations_heavy_gtm"]):
        return "strong", signals
    if signals:
        return "plausible", signals
    if candidate.get("company") in {"DoorDash", "Rithum", "Tebra", "Toast"} and norm_url(candidate.get("url")):
        return "plausible", ["target-company calibration requires manual review"]
    return "unknown", []


def disqualifiers(candidate: dict[str, Any]) -> list[str]:
    text = text_for(candidate)
    found: list[str] = []
    for reason, terms in NEGATIVE_SIGNALS.items():
        if any(term in text for term in terms):
            found.append(reason)
    title = str(candidate.get("title") or "").lower()
    if re.search(r"\b(intern|assistant|coordinator|specialist|associate)\b", title) and "associate director" not in title:
        found.append("too junior for calibrated seniority")
    return found


def seniority_fit(candidate: dict[str, Any]) -> str:
    title = str(candidate.get("title") or "").lower()
    if "associate director" in title or re.search(r"\bdirector\b", title) or title.startswith("head of") or " head " in title:
        return "strong"
    if "senior manager" in title or "principal program" in title or "program director" in title:
        return "plausible"
    if re.search(r"\b(manager|lead)\b", title):
        return "too_junior"
    if re.search(r"\b(vp|vice president|chief|cxo)\b", title):
        return "too_senior_or_stretch"
    return "unknown"


def locality_fit(candidate: dict[str, Any], target: dict[str, Any] | None) -> str:
    loc_text = " ".join(str(candidate.get(k) or "") for k in ["location", "raw_team", "raw_department"]).lower()
    if any(term in loc_text for term in LOCAL_TERMS):
        return "local_strong"
    if any(term in loc_text for term in GEO_MISMATCH_TERMS) and not any(term in loc_text for term in REMOTE_US_TERMS):
        return "geography_mismatch"
    if any(term in loc_text for term in REMOTE_US_TERMS):
        return "remote_us_plausible"
    if target and target.get("locality_priority") == "remote_us_allowed" and "remote" in loc_text:
        return "remote_us_plausible"
    return "unknown"


def compensation_fit(candidate: dict[str, Any], floor: int) -> str:
    text = str(candidate.get("salary_text") or "")
    if not text:
        return "not_visible"
    nums = [int(n.replace(",", "")) for n in re.findall(r"\$?\s*(\d{2,3}(?:,\d{3})+|\d{6})", text)]
    # Also handle compact 155000-style numbers if present.
    if not nums:
        nums = [int(n) for n in re.findall(r"\b(\d{6})\b", text)]
    if not nums:
        return "ambiguous_floor" if "$" in text or "salary" in text.lower() or "compensation" in text.lower() else "not_visible"
    low, high = min(nums), max(nums)
    if low >= floor:
        return "clears_floor"
    if high >= floor:
        return "ambiguous_floor"
    return "misses_floor"


def decision(candidate: dict[str, Any], seed_by_url: dict[str, str], role_fit: str, seniority: str, locality: str, comp: str, disq: list[str]) -> tuple[str, list[str], str]:
    seed = seed_status_for(candidate, seed_by_url)
    reasons: list[str] = []
    confidence = "medium"

    if candidate.get("source_status") not in {"listed", "detail_live"}:
        return "likely_removal_candidate", [f"Source status is {candidate.get('source_status')}; needs manual recheck before any canonical update."], "medium"

    if seed == "active_shortlist":
        reasons.append("Configured as an active shortlist/monitored role and scanner still lists it.")
        if comp in {"clears_floor", "ambiguous_floor", "not_visible"}:
            reasons.append("Kept despite scanner caveats so current known live roles survive the filter for EJS-022 validation.")
        return "still_live", reasons, "high"

    if seed in {"disqualified_calibration", "near_miss"}:
        reasons.append(f"Configured as {seed.replace('_', ' ')}; preserve as calibration rather than promoting automatically.")
        return "disqualified_false_positive", reasons + (disq or ["Seed target is a known calibration/near-miss case."]), "high"

    hard_disq = list(disq)
    if seniority == "too_junior":
        hard_disq.append("seniority below Emily calibrated target")
    if locality == "geography_mismatch":
        hard_disq.append("geography does not match Seattle/local or remote-US allowance")
    if comp == "misses_floor":
        hard_disq.append("visible compensation misses $180k base floor")

    if hard_disq and role_fit not in {"strong", "plausible"}:
        return "disqualified_false_positive", hard_disq, "medium"
    if hard_disq:
        return "needs_manual_review", ["Has some positive signal but also concrete disqualifier(s)."] + hard_disq, "medium"
    if role_fit in {"strong", "plausible"} and seniority in {"strong", "plausible"} and locality in {"local_strong", "remote_us_plausible", "local_plausible", "unknown"} and comp != "misses_floor":
        return "new_candidate", ["Matches one or more Emily role-family signals and clears initial seniority/locality/compensation screen."], "medium"
    return "needs_manual_review", ["Insufficient signal for promotion or disqualification from scanner fields alone."], "low"


def review_priority_score(bucket: str, role_fit: str, seniority: str, locality: str, comp: str, disq: list[str]) -> int:
    score = 0
    score += {"strong": 30, "plausible": 18, "weak": 8, "unknown": 0, "out_of_lane": -20}.get(role_fit, 0)
    score += {"strong": 25, "plausible": 15, "unknown": 0, "too_junior": -18, "too_senior_or_stretch": -8}.get(seniority, 0)
    score += {"local_strong": 20, "local_plausible": 16, "remote_us_plausible": 12, "unknown": 0, "geography_mismatch": -30}.get(locality, 0)
    score += {"clears_floor": 15, "ambiguous_floor": 8, "not_visible": 2, "misses_floor": -25}.get(comp, 0)
    score += {"still_live": 10, "new_candidate": 5, "needs_manual_review": 0, "likely_removal_candidate": -15, "disqualified_false_positive": -35}.get(bucket, 0)
    score -= 10 * len(disq)
    return max(0, min(100, score))


def filter_candidate(candidate: dict[str, Any], target_by_id: dict[str, dict[str, Any]], seed_by_url: dict[str, str], floor: int, reviewed_at: str) -> dict[str, Any]:
    target = target_by_id.get(candidate.get("target_id"))
    role_fit, signals = role_family(candidate)
    disq = disqualifiers(candidate)
    seniority = seniority_fit(candidate)
    locality = locality_fit(candidate, target)
    comp = compensation_fit(candidate, floor)
    bucket, reasons, confidence = decision(candidate, seed_by_url, role_fit, seniority, locality, comp, disq)
    effective_role_fit = "out_of_lane" if bucket == "disqualified_false_positive" and not signals else role_fit
    return {
        "company": candidate.get("company"),
        "title": candidate.get("title"),
        "url": candidate.get("url"),
        "decision_bucket": bucket,
        "review_priority_score": review_priority_score(bucket, effective_role_fit, seniority, locality, comp, disq),
        "reasons": reasons,
        "matching_signals": signals,
        "disqualifiers": disq,
        "role_family_fit": effective_role_fit,
        "seniority_fit": seniority,
        "locality_fit": locality,
        "compensation_fit": comp,
        "confidence": confidence,
        "compared_to_obsidian_state": None,
        "reviewed_at": reviewed_at,
        "raw_candidate_ref": {"target_id": candidate.get("target_id"), "observed_at": candidate.get("observed_at"), "source_status": candidate.get("source_status")},
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Filter Emily scanner raw output into review buckets")
    p.add_argument("--raw", type=Path, default=None, help="Raw scanner artifact; defaults to latest")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--no-write", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    raw_path = args.raw or latest_raw_path()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    config = load_config(args.config)
    target_by_id, seed_by_url = build_target_maps(config)
    floor = int(config.get("emily_fit_baseline", {}).get("compensation_floor_base_usd", 180000))
    reviewed_at = utc_now()
    filtered = [filter_candidate(c, target_by_id, seed_by_url, floor, reviewed_at) for c in raw.get("candidates", [])]
    filtered.sort(key=lambda c: (c["review_priority_score"], c["decision_bucket"] == "still_live"), reverse=True)
    counts: dict[str, int] = {}
    for item in filtered:
        counts[item["decision_bucket"]] = counts.get(item["decision_bucket"], 0) + 1
    artifact = {
        "schema_version": 1,
        "record_type": "emily_scanner_filtered_run",
        "raw_artifact": str(raw_path),
        "reviewed_at": reviewed_at,
        "guardrails": config.get("guardrails", {}),
        "candidate_count": len(filtered),
        "bucket_counts": counts,
        "candidates": filtered,
    }
    output_path = None
    if not args.no_write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = reviewed_at.replace(":", "").replace("-", "")
        output_path = args.output_dir / f"emily-scanner-filtered-{stamp}.json"
        output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"raw_artifact": str(raw_path), "candidate_count": len(filtered), "bucket_counts": counts, "output_path": str(output_path) if output_path else None}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
