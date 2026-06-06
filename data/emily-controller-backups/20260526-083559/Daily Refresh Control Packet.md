---
type: "project-note"
status: "active"
created: "2026-05-19"
project: "Emily Job Search"
---
# Daily Refresh Control Packet

## Purpose
Small first-read packet for the recurring Emily Job Search loop. Use this before opening the large historical notes.

This packet exists to keep daily runs under timeout. It should be updated after each completed refresh and should stay compact.

## Current guardrails
- Local-first within roughly 1 hour of Duvall; remote expansion only after a fresh local saturation check.
- FTE only, base salary target/floor is $180k+, travel under 25%.
- Approved lanes: eCommerce / digital operations, digital transformation, content/content operations, creative operations with systems/process scope, omnichannel / merchandising operations, and operations-heavy GTM.
- Include credible Associate Director, Director, Head-of, Senior Manager, Program Director / Principal Program Lead, Digital Program Manager, and equivalent senior operator roles when scope/pay/geography fit.
- Do not cap the master monitored list because the email body may cap at 10.
- Routine every-other-day Emily-facing digest emails are standing-send approved after refresh, render, and attachment QA pass; keep Jaret CC'd. Hold only for blockers, unusual risk, failed QA, missing freshness evidence, transport/auth failure, or a substantive decision needing human judgment. Do not send from the daily research cron.
- Scanner/search-agent outputs are evidence only. Sammy/controller owns canonical Obsidian writes.

## Current live monitored set
| Rank | Score | Company | Title | State | Work model | Geography | Last confirmed | Link |
| ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | 79 | Celigo | Senior Ecommerce Director | active | Remote | US | 2026-05-22 | <https://www.celigo.com/careers/senior-ecommerce-director-6/> |
| 2 | 79 | Rithum | Director, Services Operations & Planning | active | Remote | US | 2026-05-22 | <https://job-boards.greenhouse.io/rithum/jobs/7767181> |
| 3 | 75 | DoorDash | Director, Ads Platform Strategy & Operations, Ads & Promotions | active | Not stated | Seattle, WA | 2026-05-22 | <https://job-boards.greenhouse.io/doordashusa/jobs/7844173> |
| 4 | 74 | Tebra | Director, GTM Technology | active | Remote | US | 2026-05-22 | <https://job-boards.greenhouse.io/tebra/jobs/4682524005> |
| 5 | 72 | Rithum | Director, Product Operations & Planning | active | Remote | US | 2026-05-22 | <https://job-boards.greenhouse.io/rithum/jobs/7914605> |
| 6 | 71 | Tebra | Director, Customer Success Operations | active | Remote | US | 2026-05-22 | <https://job-boards.greenhouse.io/tebra/jobs/4682483005> |
| 7 | 70 | Smartsheet | Senior Manager, Product Operations | new | Remote eligible | US | 2026-05-22 | <https://job-boards.greenhouse.io/smartsheet/jobs/7743581> |

## Current local-market state
- The local market is not exhaustive, but recent local-first passes have been low-yield.
- Current direct-validated local survivor: DoorDash only.
- Smartsheet — Senior Manager, Product Operations joined the live shortlist on 2026-05-22, but the direct Greenhouse posting is `Remote Eligible` / `-REMOTE, USA-`, so it does not count as a Seattle/Eastside local survivor.
- Latest local near-misses / false positives: Stackline Strategy & E-commerce Insights, Stackline Programmatic Retail Media Strategy, Smartsheet Analytics Engineering & BI Platform, Smartsheet Customer Experience Strategy & Programs, Headway lifecycle/design-systems roles, Rover lifecycle strategy, Nordstrom reverse inventory product management, REI membership marketing, Brooks owned brand experiences.
- Breville / Sage / ChefSteps remains weakly verifiable; official CSOD routes have failed or fallen into restricted/error flows.
- Keep sampling local direct boards, but do not let the daily fast pass become a full pattern audit every day.

## Scenario-based read rules
### Fast daily survivor pass
Read first:
- This packet
- [Live Role Shortlist](Live%20Role%20Shortlist.md)
- active/new/aging rows from [Role State Ledger](Role%20State%20Ledger.md), not the whole table when a script can extract them
- latest 1-2 entries from [Refresh Delta Log](Refresh%20Delta%20Log.md)

Do:
- Revalidate current live roles via direct company/ATS pages.
- Check one bounded local discovery slice or consume fresh search-agent handoff artifacts.
- Update canonical files only for real changes.
- Stay quiet unless there is turnover, blocker, or quality issue.

### Removal / closure scenario
Also read:
- [Role Removal Log](Role%20Removal%20Log.md)
- affected role row in the ledger

Do:
- Mark the role closed/stale/disqualified/applied/ignored.
- Remove from shortlist.
- Add a removal-log row.
- Add one compact delta-log entry.

### New discovery scenario
Also read:
- [Role Fit Rubric and Query Pack](Role%20Fit%20Rubric%20and%20Query%20Pack.md) only for the relevant lane/query family
- [Local Market Coverage Map](Local%20Market%20Coverage%20Map.md) current status and relevant company cluster only
- latest search-agent handoff files, if present

Do:
- Validate direct source, pay, geography, title/scope, and travel.
- Add plausible roles to ledger; add to shortlist only if they clear monitored-list quality.

### Pattern-audit scenario
Run only when triggered by stale local coverage, two quiet discovery passes, or explicit request.
Read broader history as needed:
- full Local Market Coverage Map
- relevant query-pack sections
- recent research notes
- scanner/search-agent artifacts

Budget:
- Timebox external attempts and stop when the evidence batch is decision-useful.
- Prefer one strong research note over many repeated probes.

### Digest prep scenario
Read:
- Live Role Shortlist
- latest refresh note / delta entry
- Digest Render Contract, Pipeline Spec, and Send Workflow

Do:
- Render and QA artifacts.
- Send routine Emily-facing digest emails under standing permission once refresh, render, and attachment QA pass; hold only for blockers, unusual risk, failed QA, missing freshness evidence, transport/auth failure, or a substantive decision needing human judgment.

## Parallel search-agent protocol
Use additional search agents as evidence collectors, not canonical writers.

Recommended lanes:
- Sammy collector: live-role revalidation plus targeted ATS/remote evidence collection in parallel.
- Hunter: local-board / local ATS web research collector in parallel.
- Johnny: local deterministic helper for generated snapshots, consistency checks, render/package QA, and scriptable file work in parallel.
- Max: optional simple local utility helper for deterministic file/script/render tasks when Johnny is busy or the task naturally belongs in the send/render lane.
- Sammy/controller: final judgment, canonical Obsidian writes, and Jaret-facing summaries after the collector wave.
- Remote fallback lanes run only after local saturation is documented; collectors gather evidence, Sammy/controller decides.

Each collector should write or return a compact handoff with:
- source URLs checked
- role candidates found
- direct validation status
- pay/geography/travel signals
- fit reason and caveat
- reject reason for false positives
- confidence level

Sammy/controller then dedupes, scores, and updates canonical Obsidian notes in this order: ledger → shortlist → removal log → delta log → local market map → this packet.

## Daily agent timing
- **08:05 PT — parallel collector wave:**
  - Hunter: local-board / local ATS discovery and false-positive logging.
  - Sammy collector: current live-role direct revalidation plus small targeted ATS/remote probe when useful.
  - Johnny: local active-state snapshot and consistency checks.
- **08:25 PT — Sammy/controller:** reconcile Hunter + Sammy + Johnny artifacts, verify only high-impact deltas, update canonical state only when needed.
- **Digest days:** Sammy drafts content/judgment; Johnny or Max can handle deterministic render/QA/local utility support; routine Emily-facing sends proceed under standing permission after QA passes, with Jaret CC'd.

## Last refresh snapshot
- 2026-05-22: all 6 previously monitored live roles were revalidated through same-day direct ATS/company evidence, and controller direct Greenhouse pressure-testing added Smartsheet — Senior Manager, Product Operations as a new rank-7 remote monitor after confirming `Remote Eligible` / `-REMOTE, USA-`, a $170,000-$230,000 base range, and strong product-operations scope. Smartsheet — Director, Analytics Engineering & BI Platform stayed out on finance/revenue analytics-engineering drift, and the local live slice still remained DoorDash only.
- Supporting artifacts: [2026-05-22 - Hunter Collector Handoff](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Agent%20Handoffs/2026-05-22%20-%20Hunter%20Collector%20Handoff.md), [2026-05-22 - Sammy Collector Handoff](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Agent%20Handoffs/2026-05-22%20-%20Sammy%20Collector%20Handoff.md), [2026-05-22 - Daily Refresh Local Snapshot](Generated/2026-05-22%20-%20Daily%20Refresh%20Local%20Snapshot.md)

#emily-job-search #control-packet #refresh
