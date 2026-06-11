# Heartbeat tasks for Sammy Scraper

## Active sprint: Emily Job Search — application tailoring

Project board: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Project Kanban.md`
Project rules: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Project Rules.md`
Application skill: `/home/jaret/repos/openclaw-workspace/skills/emily-application-tailoring/SKILL.md`
Tracker: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Application Tailoring Tracker.md`
Answer bank: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Application Answer Bank.md`

## Heartbeat execution contract

On each heartbeat, if there is no more urgent Emily Job Search obligation:

1. Read Project Rules, the Project Kanban `Doing` lane, the Application Tailoring Tracker, and the application-tailoring skill.
2. Advance the first incomplete `Doing` card with concrete research, drafting, artifact-building, QA, or tracker work.
3. Keep `Doing` limited to 1-3 cards. Pull from `Ready` only when current `Doing` work is complete or blocked; otherwise ask before changing the one-role-at-a-time ordering.
4. Prefer silent progress. Reply to Jaret only for a completed milestone, real blocker, failed safety/preflight check, proposed canonical workflow change, or unexpectedly important finding.
5. After a role's resume and cover letter pass QA, send the review artifacts by email to Emily (`emily.brown.ops@gmail.com`) with Jaret CC'd (`jaretjb@gmail.com`) under Jaret's 2026-06-09 standing approval, then record the message ID/status. Applications, outreach, recruiter contact, portal login, form submission, public action, and any other non-routine email still require explicit approval. Emily submits applications herself for now.
6. Keep Obsidian canonical. Generated artifacts are deliverables for review/submission by Emily, not authorization to mutate role state or submit externally.

## Current first task

Start/continue `EJS-029, Tailor application packet for DoorDash — Director, Ads Platform Strategy & Operations, Ads & Promotions`.

Format rule:
- Prefer editable DOCX when practical and cleanly verifiable. Before generating DOCX, read `/home/jaret/repos/openclaw-workspace/skills/docx-builder/SKILL.md`.
- Primary DOCX route: structured content → docx-builder JSON spec → `node skills/docx-builder/scripts/create_docx.mjs <input-spec.json> <output.docx>` from `/home/jaret/repos/openclaw-workspace` → verify file exists and inspect zip/XML.
- If DOCX is unavailable or lower quality, deliver HTML or PDF plus source markdown for traceability/future edits.
- Do not block a role solely because DOCX is imperfect if HTML/PDF is the better current handoff format.

When a role is complete or genuinely blocked, update the tracker and Kanban, then move the next ranked incomplete application-tailoring card from Backlog into `Doing` before treating the project as clear. Do not return Emily Job Search to manual cadence while the Application Tailoring Tracker still has ranked roles in `backlog`, `research`, `draft`, `artifact-build`, or `qa`.
