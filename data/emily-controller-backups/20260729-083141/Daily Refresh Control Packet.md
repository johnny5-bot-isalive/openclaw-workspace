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
- FTE only, base salary target/floor is $135k+, travel under 25%.
- The salary floor was lowered from $180k to $135k on 2026-07-12 because the prior floor was not surfacing enough opportunities. Reconsider prior salary-only disqualifications when the role now clears $135k; keep rejecting weak-scope, poor-lane, high-travel, or non-FTE roles. Poor geography should usually become a location/priority constraint rather than a permanent reject.
- Approved lanes: eCommerce / digital operations, digital transformation, content/content operations, creative operations with systems/process scope, omnichannel / merchandising operations, operations-heavy GTM, and corporate strategy / Chief-of-Staff-style roles when the actual scope owns operating-model, governance, planning, transformation, or cross-functional execution work.
- Include credible Associate Director, Director, Head-of, Senior Manager, Program Director / Principal Program Lead, Digital Program Manager, and equivalent senior operator roles when scope/pay/geography fit.
- Do not cap the master monitored list because the email body may cap at 10.
- Routine every-other-day Emily-facing digest emails are standing-send approved after refresh, render, and attachment QA pass; keep Jaret CC'd. Hold only for blockers, unusual risk, failed QA, missing freshness evidence, transport/auth failure, or a substantive decision needing human judgment. Do not send from the daily research cron.
- Scanner/search-agent outputs are evidence only. Sammy/controller owns canonical Obsidian writes.
- Ranking now uses the 2026-06-01 resume-attainability recalibration: resume / market-language / realistic interview path carries 20 points, scope/seniority carries 20 points, and large-company Senior Director roles should usually be labeled Stretch / low-probability rather than Priority target.

## Current live monitored set
| Rank | Score | Company | Title | State | Work model | Geography | Last confirmed | Link |
| ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | 76 | Life360 | Director, DTC Growth and Web Experience | new | Remote-first | US / Canada | 2026-07-29 | <https://job-boards.greenhouse.io/life360/jobs/8649099002> |
| 2 | 74 | Hasbro | Director, GTM Program Management & Analytics | new | Not stated | Renton, WA | 2026-07-29 | <https://job-boards.greenhouse.io/hasbro/jobs/4297680009> |
| 3 | 73 | DoorDash | Director, Customer Experience Strategy & Operations | new | Not stated | Seattle, WA | 2026-07-29 | <https://job-boards.greenhouse.io/doordashusa/jobs/7983379> |
| 4 | 72 | DoorDash | Senior Manager, Consumer Discovery - Strategy & Operations | new | Not stated | Seattle, WA / San Francisco, CA / New York, NY | 2026-07-29 | <https://job-boards.greenhouse.io/doordashusa/jobs/7604521> |
| 5 | 71 | Hasbro | Senior Program Manager, DTC Platform Performance | new | Hybrid, 3 days onsite | Renton, WA | 2026-07-29 | <https://job-boards.greenhouse.io/hasbro/jobs/4250536009> |
| 6 | 70 | REI | Enterprise Operations Process Design Director | new | Not stated | Seattle, WA | 2026-07-29 | <https://www.rei.jobs/careers-home/jobs/29847?lang=en-us> |
| 7 | 70 | Hasbro | Sr. Manager, Commercial Strategy - North America | new | Not stated | Renton, WA | 2026-07-29 | <https://job-boards.greenhouse.io/hasbro/jobs/4249882009> |
| 8 | 69 | Chewy | Associate Director Business Planning & Strategy | new | Not stated | Bellevue, WA | 2026-07-29 | <https://careers.chewy.com/us/en/job/R28935/Associate-Director-Business-Planning-Strategy> |
| 9 | 69 | Tebra | Director, GTM Operations | active | Remote | US | 2026-07-29 | <https://job-boards.greenhouse.io/tebra/jobs/4708633005> |
| 10 | 68 | Nintendo | Manager, eShop - Publisher Developer Relations | new | Hybrid | Redmond, WA | 2026-07-29 | <https://careers.nintendo.com/jobs/4183836009> |
| 11 | 68 | Nordstrom | Senior Manager Business Management, Inventory | new | Hybrid | Seattle, WA | 2026-07-28 | <https://nordstrom.wd501.myworkdayjobs.com/en-US/nordstrom_careers/job/Seattle-WA/Senior-Manager-Business-Management--Inventory---HYBRID--Seattle-WA-_R-855414> |
| 12 | 68 | Nordstrom | Sr. Director, Digital Merchandising - N.com and eCommerce | active | Not stated | Seattle, WA | 2026-07-28 | <https://nordstrom.wd501.myworkdayjobs.com/en-US/nordstrom_careers/job/Seattle-WA/Sr-Director--Digital-Merchandising---Ncom-and-eCommerce_R-844667> |
| 13 | 67 | Chime | Lead, Strategic Initiatives, Operations and Member Experience | new | Remote | US | 2026-07-28 | <https://boards.greenhouse.io/chime/jobs/8609157002?gh_jid=8609157002> |
| 14 | 66 | OfferUp | Principal Product Manager - Local Business | new | Hybrid | Bellevue, WA | 2026-07-28 | <https://job-boards.greenhouse.io/offerup/jobs/7984105> |
| 15 | 66 | DoorDash | Manager, Digital Ordering - Strategy & Operations | new | Not stated | Seattle, WA | 2026-07-28 | <https://job-boards.greenhouse.io/doordashusa/jobs/8010907> |
| 16 | 65 | Airtable | Senior Manager, Marketing AI Operations | new | Remote | US | 2026-07-28 | <https://job-boards.greenhouse.io/airtable/jobs/8382119002> |
| 17 | 65 | Aurora Solar | Senior Business Operations Manager | new | Remote | US | 2026-07-28 | <https://jobs.ashbyhq.com/aurorasolar/6b64833e-42e5-4bf4-9079-93ac58d2b529> |
| 18 | 64 | TikTok | TikTok Shop - Strategy and Operations Managers, Shoptab | new | Not stated | Seattle, WA | 2026-07-28 | <https://lifeattiktok.com/search/7611384715448813829> |
| 19 | 63 | TikTok | TikTok Shop - Product Operations Manager, Livestream | new | Not stated | Seattle, WA | 2026-07-28 | <https://lifeattiktok.com/search/7628447363740911877> |

## Current local-market state
- 2026-07-29 digest freshness gate: all ten email roles remained live on direct company/ATS sources with expected IDs, locations, and non-empty posting content. Tebra job `4708633005` now carries the ATS title **Director, GTM Operations**; canonical notes and the digest bundle were normalized from the older **Director, GTM Technology** label. Rank, score, remote status, and `$200,000-$228,000` Zone 1 base are unchanged.
- 2026-07-28 late heartbeat Hasbro board correction: added **Sr. Manager, Commercial Strategy - North America** at rank 7 / score 70 after direct Greenhouse board/API validation showed the Renton role live with `$120,500-$180,700` base and substantive eCommerce/channel planning, launch readiness, scorecard, revenue/margin, and cross-functional execution ownership. The monitored set returns to 19 roles; Hasbro enters the top 10 and Nordstrom Inventory moves to rank 11.
- 2026-07-28 heartbeat fallback revalidation: removed Rithum **Director, Americas Field & Partner Operations** as closed after the direct Greenhouse API returned HTTP 404 and the current 23-job Rithum board contained neither job ID `8003710` nor the exact title. The monitored set now contains 18 roles; the top 10 is unchanged.
- The local market is not exhaustive, and the lowered $135k floor means prior salary-only local disqualifications should be reconsidered when still live and otherwise plausible.
- The July 27 digest predates this turnover. Future digest bundles must use the current 19-role canonical state; no application, outreach, or public action was taken from this controller pass.
- Next-digest baseline: replace the now-closed DoorDash **Director, New Verticals - Retail Strategy & Operations** at prior email rank 2 with Hasbro **Director, GTM Program Management & Analytics** at current rank 2; add Hasbro **Sr. Manager, Commercial Strategy - North America** at current rank 7; keep the remaining current top 10 in canonical order, move Nordstrom Inventory below the email top-10 cutoff, and omit closed Rithum from any expanded companion set. The [July 29 email draft](Digest/Drafts/Emily%20Digest%20Draft%20-%202026-07-29.md), [render-data sidecar](Digest/Render%20Data/Emily%20Digest%20Render%20Data%20-%202026-07-29.yaml), rendered email, and ten-role companion report now exist. The July 29 direct-source freshness gate passed and the Tebra title was normalized to **Director, GTM Operations**. The corrected bundle was rerendered and deterministic attachment QA passed: ranks 1–10 are unique, all ten canonical links are unique, rubric sums match, radar fields are complete, the companion contains ten inline SVGs, and no missing-asset marker appears. Transport preflight passed, and the routine digest was sent to Emily with Jaret CC'd at 5:30 a.m. PDT on July 29, with the HTML comparison report attached. Gmail message ID: `19faddaa4b542d58`.

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
- [Role Fit Rubric and Query Pack](Role%20Evaluation/Role%20Fit%20Rubric%20and%20Query%20Pack.md) only for the relevant lane/query family
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
- [Live Role Shortlist](Live%20Role%20Shortlist.md)
- latest refresh note / delta entry from [Refresh Delta Log](Refresh%20Delta%20Log.md)
- [Digest Render Contract](Digest/Digest%20Render%20Contract.md), [Digest Render Pipeline Spec](Digest/Digest%20Render%20Pipeline%20Spec.md), and [Digest Send Workflow](Digest/Digest%20Send%20Workflow.md)

Do:
- Render and QA artifacts under `Digest/`: drafts in `Digest/Drafts/`, sidecars in `Digest/Render Data/`, email bodies in `Digest/Rendered Emails/`, approval/send packets in `Digest/Approval Packets/`, and change drafts in `Digest/Change Drafts/`.
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
- 2026-07-29 digest freshness gate: all ten email roles remained live. Tebra job `4708633005` was normalized to its current ATS title, **Director, GTM Operations**; no rank, score, compensation, geography, or work-model change was required.
- 2026-07-28 late heartbeat Hasbro local-board correction: added **Sr. Manager, Commercial Strategy - North America** at rank 7 / score 70 after direct Greenhouse validation. The current live set contains 19 roles; Hasbro enters the top 10 and Nordstrom Inventory moves to rank 11.
- 2026-07-28 heartbeat fallback revalidation after the controller wave: removed Rithum **Director, Americas Field & Partner Operations** as closed after direct Greenhouse API and current-board confirmation, then completed direct-source checks across all 18 surviving roles. The current live set then contained 18 roles; the top 10 was unchanged.
- 2026-07-27 controller reconciliation after collector wave: no live-set change; all 19 monitored roles remained live, and bounded direct checks kept the Brooks, Tebra Customer Success, and stale Scribd leads out.
- 2026-07-25 manual application-state update: marked Chewy **Associate Director, Homepage and Program Merchandising** applied, removed it from the live monitored shortlist, and reranked the remaining 19 roles with Life360 at rank 1.

#emily-job-search #control-packet #refresh
