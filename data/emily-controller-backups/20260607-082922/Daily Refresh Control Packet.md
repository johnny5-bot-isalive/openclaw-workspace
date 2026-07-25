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
- Ranking now uses the 2026-06-01 resume-attainability recalibration: resume / market-language / realistic interview path carries 20 points, scope/seniority carries 20 points, and large-company Senior Director roles should usually be labeled Stretch / low-probability rather than Priority target.

## Current live monitored set
| Rank | Score | Company | Title | State | Work model | Geography | Last confirmed | Link |
| ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | 74 | Smartsheet | Senior Manager, Product Operations | active | Remote eligible | US | 2026-06-05 | <https://job-boards.greenhouse.io/smartsheet/jobs/7743581> |
| 2 | 71 | DoorDash | Director, Ads Platform Strategy & Operations, Ads & Promotions | active | Not stated | Multi-location incl. Seattle, WA | 2026-06-05 | <https://job-boards.greenhouse.io/doordashusa/jobs/7844173> |
| 3 | 70 | Rithum | Director, Product Operations & Planning | active | Remote | US | 2026-06-05 | <https://job-boards.greenhouse.io/rithum/jobs/7914605> |
| 4 | 69 | Celigo | Senior Ecommerce Director | active | Remote | US | 2026-06-05 | <https://job-boards.greenhouse.io/celigo/jobs/7696555> |
| 5 | 69 | Tebra | Director, GTM Technology | active | Remote | US | 2026-06-05 | <https://job-boards.greenhouse.io/tebra/jobs/4682524005> |
| 6 | 68 | Nordstrom | Sr. Director, Digital Merchandising - N.com and eCommerce | active | Not stated | Seattle, WA | 2026-06-05 | <https://nordstrom.wd501.myworkdayjobs.com/en-US/nordstrom_careers/job/Seattle-WA/Sr-Director--Digital-Merchandising---Ncom-and-eCommerce_R-844667> |
| 7 | 67 | Tebra | Director, Customer Success Operations | active | Remote | US | 2026-06-05 | <https://job-boards.greenhouse.io/tebra/jobs/4682483005> |

## Current local-market state
- The local market is not exhaustive, but recent local-first passes have still been low-yield.
- Same-day Hunter/Sammy collector handoffs plus Johnny's local snapshot were available by 2026-06-05 controller reconciliation, so this pass stayed in minimum-budget controller mode rather than broad local rediscovery.
- Current direct-validated local survivors remain DoorDash and Nordstrom.
- Today's highest-impact local deltas resolved out rather than in: Stackline's rerun still centered a Seattle-hybrid Professional Services / retail-media client-delivery Director role at $160,000-$190,000 base plus an Associate Director brand-operations role at $140,000-$160,000 base below Emily's locked floor.

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
- 2026-06-05: reconciled the available same-day Hunter + Sammy collector handoffs plus Johnny's local snapshot, then directly confirmed all 7 monitored roles still live on 2026-06-05. Controller added one bounded direct Greenhouse API pressure-test cluster and kept Hunter's two Stackline Seattle leads out: **Director, Strategy & E-commerce Insights** remained a Seattle-hybrid / 4-days-in-office Professional Services / retail-media client-delivery role at $160,000-$190,000 base, while **Associate Director, Brand Operations** remained a Seattle-hybrid / 4-days-in-office commerce-operations adjacency with a $140,000-$160,000 base band below Emily's locked floor. The ranked live set stays at 7, and the local slice stays at two direct-validated survivors: DoorDash and Nordstrom.
- 2026-06-04: reconciled the available same-day Hunter + Sammy collector handoffs plus Johnny's local snapshot, then directly confirmed all 7 monitored roles still live on 2026-06-04. Controller added one bounded direct Lever pressure-test and kept Brooks Running — Senior Director, Owned Brand Experiences out as the same brand-experience / events / loyalty stretch with an explicit four-days-per-week Seattle office requirement; Hunter's Remitly signal also stayed too weakly validated for promotion after the direct careers fetch failed to expose a usable posting row. The ranked live set stays at 7, and the local slice stays at two direct-validated survivors: DoorDash and Nordstrom.
- 2026-06-03: reconciled same-day Hunter + Sammy collector handoffs plus Johnny's local snapshot, then directly confirmed all 7 monitored roles still live on 2026-06-03. Nordstrom — Sr. Director, Digital Merchandising - N.com and eCommerce now normalizes from `new` to `active` after a third straight direct confirmation. Controller direct Greenhouse/API pressure-tests kept Hasbro — Principal Technical Product Manager - Hasbro Direct, Hasbro — Director Analytics WOTC, and The Pokémon Company International — Sr. Corporate Strategy Manager out of the monitored set because they resolved to technical product / analytics leadership or strategy-chief-of-staff shapes rather than Emily's cleaner operations lanes.
- 2026-06-02: reconciled same-day Hunter + Sammy collector handoffs plus Johnny's local snapshot, then directly confirmed all 7 monitored roles still live on 2026-06-02. Controller direct Greenhouse pressure-tests kept Smartsheet — Senior Director, Transformation & Business Operations out as a Bellevue / remote-eligible Customer Excellence chief-of-staff / post-sale transformation stretch despite a $205,000-$285,000 base band, and another Stackline rerun still resolved to hybrid client-services / below-floor leads rather than a new add.
- 2026-06-01 evening calibration: per Jaret's feedback, reweighted scoring so resume / market-language / realistic interview attainability carries 20 points and scope/seniority carries 20 points. This moved Senior Director roles out of the top priority slots: Smartsheet now ranks #1 as the cleanest attainable functional fit, DoorDash #2 as the strongest local Director-level option, and Senior Director roles are treated as Stretch / low-probability unless a future pass finds a credible referral or compressed-leveling path.
- 2026-06-01: reconciled same-day Hunter + Sammy collector handoffs plus Johnny's local snapshot, then directly confirmed Rithum — Director, Services Operations & Planning is now closed after its Greenhouse URL redirected to the generic board and the live Rithum board no longer listed the title or job id `7767181`. Same-pass controller Workday validation promoted Hunter's Nordstrom — Sr. Director, Digital Merchandising - N.com and eCommerce into the monitored set as a new Seattle local add with a $190,000-$300,000 base range, while same-day ATS/company evidence kept the other 6 monitored roles live on 2026-06-01. The ranked live set stays at 7, and the local slice expands from DoorDash-only to DoorDash plus Nordstrom.
- Supporting artifacts: [Live Role Shortlist](Live%20Role%20Shortlist.md), [Role State Ledger](Role%20State%20Ledger.md), [Refresh Delta Log](Refresh%20Delta%20Log.md), [Local Market Coverage Map](Local%20Market%20Coverage%20Map.md), [2026-06-05 - Hunter Collector Handoff](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Agent%20Handoffs/2026-06-05%20-%20Hunter%20Collector%20Handoff.md), [2026-06-05 - Sammy Collector Handoff](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Agent%20Handoffs/2026-06-05%20-%20Sammy%20Collector%20Handoff.md), [2026-06-05 - Daily Refresh Local Snapshot](Generated/2026-06-05%20-%20Daily%20Refresh%20Local%20Snapshot.md)

#emily-job-search #control-packet #refresh
