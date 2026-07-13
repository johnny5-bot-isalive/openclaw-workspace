---
name: emily-application-tailoring
description: Tailor Emily Brown's resume, cover letter, Emily-friendly application artifacts, and application-support packet for one specific job role at a time. Use for Emily Job Search role-application work, including role/company research, hiring-team research, job-posting variant analysis, master-resume evidence mapping, selecting the best accomplishments, choosing resume length/version, drafting a cover letter, building reusable application answers, producing DOCX/HTML/PDF artifacts as appropriate, tracking per-role status, and QA before Emily submits the application herself.
---

# Emily Application Tailoring

Use this skill for one role at a time. Do not batch multiple companies in one drafting pass.

## Core rule

Maximize Emily's interview odds by making the application packet obviously relevant to the specific role while staying truthful, source-grounded, and human-reviewable.

Never submit applications, message recruiters, contact hiring teams, or log into job portals without explicit approval. Emily is the submitter for now; produce materials she can review, tweak, and upload herself. Jaret approved routine per-role review emails on 2026-06-09: after a role's resume and cover letter pass QA, email the review artifacts to Emily at `emily.brown.ops@gmail.com` with Jaret CC'd at `jaretjb@gmail.com`. This approval is only for review/handoff email, not application submission or outreach.

## Project sources

Start in the Emily Job Search Obsidian project:

- Project rules: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Project Rules.md`
- Live ranked roles: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Live Role Shortlist.md`
- Master resume folder: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Resumes/`
- Master resume note: `Resumes/Resume Master Draft.md` when present
- Positioning guide: `Resumes/Resume and Cover Letter Positioning Guide.md`
- Application answer bank: `Applications/Application Answer Bank.md`
- Application tailoring tracker: `Applications/Application Tailoring Tracker.md`
- Role ledger / evidence notes as needed for the role

If multiple resume files exist, choose the best base for the role. Prefer the canonical markdown master for reasoning, then use DOCX/PDF variants only when formatting/final deliverable requirements matter.

Emily's current employer may be named. Do not invent metrics, responsibilities, tools, reporting lines, relationships, or credentials.

## Workflow

### 1. Create/confirm one role work item

Confirm the target role is the next highest-ranked incomplete role unless Jaret explicitly overrides the order.

Record:
- company
- title
- rank/score if available
- canonical posting URL
- output folder path under `Resumes/<Company-or-Role>/`
- current status in `Applications/Application Tailoring Tracker.md`: research, draft, artifact-build, QA, blocked, ready for Emily review, or sent to Emily/Jaret for review

### 2. Gather role intelligence

Use direct/primary sources first. Research enough to make a better packet, not enough to stall.

Check:
- official posting and ATS metadata/body
- alternate versions of the same posting: company careers page, ATS page, LinkedIn, job-board mirrors, recruiter reposts, cached snippets, or saved source notes
- similar current/past postings at the company for the same function/team
- company/product strategy, recent announcements, investor/blog/news context, and business priorities
- likely team, function, hiring manager, recruiter, and reporting line if public and relevant
- public hiring-team profiles only for professional context: vocabulary, priorities, org structure, shared background patterns, and likely interview emphasis
- interview reviews or anonymous reports only as weak, caveated evidence

Do not rely on personal/private details. Do not contact anyone.

### 3. Decode what the role really wants

Write a compact role-fit diagnosis:
- role mission in plain English
- 6-10 must-have capabilities
- hidden signals: seniority, operating style, metrics ownership, stakeholder map, systems/tools, business problem, likely interview themes
- ATS/recruiter keywords to include naturally
- risks: too senior, too technical, too sales-heavy, too strategy-only, travel/work model, compensation, domain mismatch

### 4. Map Emily's evidence

Build an evidence map from the master resume and prior tailored packets:
- best accomplishments for each role requirement
- strongest metrics/results to promote
- bullets to rewrite, compress, remove, or move up
- transferable experience that needs clearer framing
- unsupported claims that must not be used
- gaps to address in the cover letter or interview prep

Use Emily's strongest recurring proof patterns:
- enterprise digital operations at scale
- eCommerce/web/app ecosystem ownership
- GTM and launch governance
- operating model design and process standardization
- cross-functional influence without relying only on formal authority
- executive performance readouts and analytics-informed prioritization
- measurable revenue, upgrade, velocity, cost, launch, or scale outcomes

### 5. Choose the resume strategy

Determine the best application narrative and resume shape for this role.

Decide:
- target positioning headline/summary
- dominant themes: digital operations, eCommerce, content operations, transformation, GTM operations, merchandising/site experience, product operations, customer-success operations, or program leadership
- ideal length: one page, tight two page, or full two page
- which base resume/version to start from
- which accomplishments deserve top-third placement
- which older/lower-fit content to compress or remove
- whether the role is a Priority target or Stretch / low-probability
- which risk needs mitigation in the cover letter

Default guidance:
- Use one page only when the role is narrower/senior-manager-like and the proof can remain strong.
- Use a tight two-page resume for Director/Senior Director roles where leadership scope, metrics, and older Nordstrom/Microsoft proof materially improve fit.
- Do not let a two-page version become a history dump; every section must earn its space for the role.

### 6. Draft the packet

Produce review-ready markdown/source first, then final Emily-friendly artifacts. Prefer editable DOCX through the local `docx-builder` route; if DOCX is unavailable or lower quality, deliver HTML or PDF plus source markdown. Before creating DOCX files, read `/home/jaret/repos/openclaw-workspace/skills/docx-builder/SKILL.md`. Include:
- tailored resume headline/summary
- tailored core skills/keywords section
- rewritten experience bullets using only truthful evidence
- optional selected accomplishments section if it improves scanability
- concise cover letter specific to the company and role
- optional application-question answers when the posting suggests likely prompts
- short recruiter/application note if useful
- reusable application-question answers or updates for `Applications/Application Answer Bank.md` when a prompt recurs

Keep the voice confident, specific, and plain-English. Avoid keyword stuffing and consultant jargon.

Final deliverables for each role must include Emily-friendly resume and cover-letter files, plus a markdown research/QA packet. Prefer editable `.docx` files when they can be produced and verified cleanly. Primary DOCX route: draft clean structured sections, convert them into the `docx-builder` JSON spec, run `node skills/docx-builder/scripts/create_docx.mjs <input-spec.json> <output.docx>` from `/home/jaret/repos/openclaw-workspace`, then verify the DOCX exists and inspect its zip/XML structure before reporting success. Use the bundled fallback `scripts/markdown_to_docx.py` only if the preferred builder is unavailable or unsuitable. Use HTML/PDF when that is the more reliable format for Emily to open. If DOCX is not possible or not good enough, say so plainly in the packet and deliver HTML/PDF instead; do not block the role solely on DOCX tooling.

### 7. QA before handoff

Run a final gate:
- every claim traceable to Emily's actual resume/evidence
- job-title/company/location details correct
- role keywords included naturally
- no fabricated hiring-manager relationship or insider claim
- current employer naming is acceptable
- resume length choice is justified
- cover letter names specific company/role reasons
- resume and cover letter exist in Emily-friendly format (DOCX preferred; HTML/PDF acceptable when DOCX is not practical) and open/inspect cleanly enough for review
- `Applications/Application Tailoring Tracker.md` is updated
- `Applications/Application Answer Bank.md` is updated when reusable answers were drafted or improved
- no application, outreach, portal login, recruiter contact, hiring-manager contact, or public action has occurred; approved review email to Emily/Jaret is allowed after QA
- remaining questions/blockers are explicit

Output the final packet with:
1. Research brief with links
2. Role-fit diagnosis
3. Resume strategy and ideal length
4. Tailored resume draft/sections
5. Cover letter draft
6. Final artifact file paths for resume and cover letter, noting format and whether DOCX was possible
7. Review email status: not yet sent, sent with message ID, or blocked by transport/QA
8. Questions for Emily/Jaret before final polish
9. QA checklist


## Durable tracking

At the end of each role pass, update `Applications/Application Tailoring Tracker.md` with:
- status
- output paths
- resume length/version decision
- cover-letter status
- reusable answer-bank updates
- remaining questions/blockers
- review email status/message ID and whether Emily/Jaret review has happened

Keep role-specific artifacts under `Resumes/<Company-or-Role>/` using stable filenames that include the company, role shorthand, and date.

## Stop conditions

Stop and ask Jaret when:
- the role requires an application question that needs Emily's personal preference or consent
- evidence would require login/private access
- the best positioning would materially stretch Emily's background
- a claim would imply Director/Senior Director authority, tool depth, domain expertise, team ownership, or hiring-team connection that is not directly supported
- a hiring-manager/team claim is uncertain but would affect strategy
- no reliable Emily-friendly artifact can be produced or verified in DOCX, HTML, or PDF
- external send/submission is requested outside the approved Emily/Jaret review-handoff email; Emily is submitting applications herself for now
