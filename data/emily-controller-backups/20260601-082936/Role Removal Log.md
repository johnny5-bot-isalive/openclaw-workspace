---
type: "project-note"
status: "active"
created: "2026-04-27"
project: "Emily Job Search"
---
# Role Removal Log

## Purpose
Audit trail for roles removed from the live monitored shortlist.

## Fields to capture
- removal date
- company
- title
- previous rank
- prior state
- new state
- canonical URL when available
- removal reason
- supporting evidence note

## Entries
| Removal date | Company | Title | Previous rank | Prior state | New state | Canonical URL | Removal reason | Evidence |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| 2026-05-19 | Toast | Director, Marketing AI Transformation | 5 | active | closed | <https://careers.toasttab.com/jobs/director-marketing-ai-transformation-remote-united-states?gh_jid=7904911> | Direct role URL stopped resolving and Toast's current careers sitemap no longer carried the role slug, so it no longer clears the live-monitoring bar. | [2026-05-19 - daily refresh with Toast closure and remote replacement adds](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Research%20Runs/2026-05-19%20-%20daily%20refresh%20with%20Toast%20closure%20and%20remote%20replacement%20adds.md) |
| 2026-05-16 | Zillow | Director, GTM Enablement | 4 | new | closed | <https://zillow.wd5.myworkdayjobs.com/en-US/Zillow_Group_External/job/Director--GTM-Enablement_P750002> | Direct Workday revalidation on 2026-05-16 now exposes `postingAvailable: false` on the apply/detail surfaces, so the role no longer clears the live-monitoring bar. | [2026-05-16 - daily refresh with Zillow and Instacart exits plus Tebra and Toast adds](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Research%20Runs/2026-05-16%20-%20daily%20refresh%20with%20Zillow%20and%20Instacart%20exits%20plus%20Tebra%20and%20Toast%20adds.md) |
| 2026-05-16 | Instacart | Senior Director, Enterprise Delivery and Growth | 5 | active | disqualified | <https://www.instacart.careers/job?id=7813002> | The direct Instacart careers page still resolves, but the posting now limits hiring to Ontario, Alberta, British Columbia, and Nova Scotia, includes only a Canadian pay range of $264,000-$278,500 CAD, and marks `applicantLocationRequirements` as `CA`, so it no longer clears Emily's geography fit. | [2026-05-16 - daily refresh with Zillow and Instacart exits plus Tebra and Toast adds](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Research%20Runs/2026-05-16%20-%20daily%20refresh%20with%20Zillow%20and%20Instacart%20exits%20plus%20Tebra%20and%20Toast%20adds.md) |
| 2026-05-12 | AT&T | Director - Digital Customer Growth | 1 | active | closed | <https://www.att.jobs/job/bothell/director-digital-customer-growth/117/94259458112> | The direct job detail URL now returns a 404 / Custom Job Error, and same-pass checks on AT&T's own Bothell location, Bothell corporate, and search pages no longer surface the title, so the role no longer clears the live-monitoring bar. | [2026-05-12 - daily refresh with AT&T closure and local follow-up](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Research%20Runs/2026-05-12%20-%20daily%20refresh%20with%20AT%26T%20closure%20and%20local%20follow-up.md) |
| 2026-05-09 | onX | Director, Enterprise Digital Transformation | 4 | active | closed | <https://job-boards.greenhouse.io/onxmaps/jobs/4656391006> | Direct Greenhouse recheck on 2026-05-09 no longer resolves to the posting and instead redirects to the generic onX jobs board with `?error=true`, so the role no longer clears the live-monitoring bar. | [2026-05-09 - daily refresh with onX closure and Seattle adds](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Research%20Runs/2026-05-09%20-%20daily%20refresh%20with%20onX%20closure%20and%20Seattle%20adds.md) |
| 2026-05-08 | Zillow | Director, Sales & Partner Enablement | 4 | new | closed | <https://zillow.wd5.myworkdayjobs.com/en-US/Zillow_Group_External/job/Director--Sales-Partner-and-Enablement_P748603> | Direct Workday validation on 2026-05-08 now exposes `postingAvailable: false`, so the prior monitored Zillow enablement opening no longer clears the live-monitoring bar. | [2026-05-08 - daily refresh with Zillow turnover and local-zero pattern](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Research%20Runs/2026-05-08%20-%20daily%20refresh%20with%20Zillow%20turnover%20and%20local-zero%20pattern.md) |
| 2026-05-07 | onX | Senior Director, Product Content Operations | 4 | active | applied | <https://job-boards.greenhouse.io/onxmaps/jobs/4666240006> | Emily applied, so this role should be removed from the live monitored shortlist and suppressed from future recommendation digests. | Jaret update in #emily-job-search on 2026-05-07 |
| 2026-05-07 | REI | Director of Creative Operations | 5 | active | applied | <https://www.rei.jobs/jobs/29724?lang=en-us> | Emily applied, so this role should be removed from the live monitored shortlist and suppressed from future recommendation digests. | Jaret update in #emily-job-search on 2026-05-07 |
| 2026-05-06 | Stanley 1913 | Director, Customer Experience | 5 | active | closed | <https://job-boards.greenhouse.io/stanley1913-us/jobs/5177768008> | Direct Greenhouse validation now redirects the old posting URL to `https://job-boards.greenhouse.io/stanley1913-us?error=true`, and the live Stanley board no longer lists the title. | [2026-05-06 - daily refresh with Stanley closure and local pattern-audit rerun](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Research%20Runs/2026-05-06%20-%20daily%20refresh%20with%20Stanley%20closure%20and%20local%20pattern-audit%20rerun.md) |
| 2026-05-04 | Loop | Director, Design | 3 | new | disqualified | <https://jobs.lever.co/loopreturns/a88f9540-4922-4f41-a598-098e3624acbe> | Direct Lever validation kept the role live and well-paid, but the geography language now limits this opening to Columbus, OH or ET/CT hub locations, so it no longer clears Emily's location fit. | [2026-05-04 - daily refresh with Loop disqualification and Stackline pattern-audit check](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Research%20Runs/2026-05-04%20-%20daily%20refresh%20with%20Loop%20disqualification%20and%20Stackline%20pattern-audit%20check.md) |
| 2026-05-01 | Brooks Running | Senior Manager, Retail Planning & Business Operations | 9 | new | closed | <https://jobs.lever.co/brooksrunning/ded2e2ab-ac9a-477b-ac9e-c1b9dbfbe7df> | Direct Lever page now explicitly shows `Job no longer available`, so the role no longer clears the live-monitoring bar. | [2026-05-01 - daily refresh with Brooks removals and Celigo link correction](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Research%20Runs/2026-05-01%20-%20daily%20refresh%20with%20Brooks%20removals%20and%20Celigo%20link%20correction.md) |
| 2026-05-01 | Brooks Running | Vice President, US Wholesale | 10 | new | closed | <https://jobs.lever.co/brooksrunning/32dc9b18-876c-4665-b440-a930de928b65> | Direct Lever page now explicitly shows `Job no longer available`, so the role no longer clears the live-monitoring bar. | [2026-05-01 - daily refresh with Brooks removals and Celigo link correction](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Research%20Runs/2026-05-01%20-%20daily%20refresh%20with%20Brooks%20removals%20and%20Celigo%20link%20correction.md) |
| 2026-04-27 | Omada Health | Senior Director, Enterprise Launch Excellence and GTM | 2 | active | closed | <https://job-boards.greenhouse.io/omadahealth/jobs/7722234> | Direct Greenhouse role stopped resolving and the current Omada openings page no longer lists the title. | [Live refresh pass](../../../20%20Library/Research%20Reports/Emily%20Job%20Search/Research%20Runs/2026-04-27%20-%20live%20digest%20refresh%20pass.md) |

## Rules
- Log every removal from [Live Role Shortlist](Live%20Role%20Shortlist.md).
- Do not silently drop `applied` or `ignored` roles; keep them visible here for future suppression.

#emily-job-search #watchlist #audit
