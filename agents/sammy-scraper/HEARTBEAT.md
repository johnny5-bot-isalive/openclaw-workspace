# Heartbeat tasks for Sammy Scraper

## Active sprint: EJS-035 — BDA second-interview presentation

Priority: **P0 through Wednesday, 2026-07-29**

Project board: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Project Kanban.md`
Project rules: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Project Rules.md`
BDA role context: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Resumes/BDA Program Operations/PROJECT.md`
BDA presentation context: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Resumes/BDA Program Operations/Interview Presentation/PROJECT.md`
BDA child backlog: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Resumes/BDA Program Operations/Interview Presentation/01 Planning/BACKLOG.md`
Dispatch target: `agent:sammy:discord:channel:1498012283983364146`
Control packet: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Daily Refresh Control Packet.md`
Live shortlist: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Live Role Shortlist.md`
Ledger: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Role State Ledger.md`
Delta log: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Refresh Delta Log.md`

## Heartbeat execution contract

On each heartbeat:

1. Read Project Rules, the BDA role context, the BDA presentation context, and the BDA child backlog.
   - Use the exact Sammy-owned dispatch target above. Do not dispatch to `agent:main:discord:channel:1498012283983364146`; cross-agent session visibility is intentionally disabled.
2. While EJS-BDA-PRES-12 is active, check Gmail once per heartbeat for Emily's response to the BDA working-package email (`threadId: 19f9b18b92ebd4dd`; query: `from:emily.brown.ops@gmail.com subject:"BDA presentation working package" newer_than:7d`).
   - This monitor is BDA-only. Do not monitor or reactivate Nordstrom, Tebra, or other parked application blockers.
   - If a reply arrives, read only that thread, capture Emily's timing/voice/evidence/logistics feedback in the rehearsal checklist, and immediately continue EJS-BDA-PRES-12.
   - If no reply exists, do not report it as a blocker. Continue any dependency-independent BDA prep; otherwise return `HEARTBEAT_OK`.
3. Execute the next dependency-eligible BDA presentation task. Continue the critical path in backlog order as dependencies clear.
4. For EJS-BDA-PRES-02/04, follow the shared Mode 2 research playbook. Create the brief and process log before the first new external search; keep all collection read-only.
5. After each task, update the child backlog status/output links, presentation `PROJECT.md` current phase/next action, and parent EJS-035 Kanban card.
6. Treat missing submission instructions as non-blocking until packaging/delivery. Do not pause research, evidence mapping, strategy, or storyboard work for them.
7. Never use or revise the pre-research outline under `99 Archive`; the research-backed storyboard begins only after tasks 02–07 are complete.
8. Prefer silent progress. Notify the Discord channel only for a real blocker, a decision Emily/Jaret must make, a review/rehearsal handoff, or a material completed deliverable.
9. If the next BDA task cannot progress safely during a heartbeat, use the remaining heartbeat for current job availability: live-role revalidation, bounded discovery, shortlist hygiene, and digest readiness.
10. When EJS-BDA-PRES-12 is complete, move EJS-035 to `Done`, remove the BDA reply monitor above, and return the Emily Job Search registry cadence from `every-heartbeat` to a manual/non-sprint cadence unless Jaret has activated new work.

## Application-packet pause

Effective 2026-07-12, Jaret paused all application-packet automation.

- Previous packet sends, including Rithum `EJS-030`, are historical only.
- No standing approval exists for future packet creation or packet review emails.
- Application packets resume only when Jaret explicitly asks for a named role packet.
- Jaret's explicit activation of EJS-035 authorizes the BDA interview-presentation backlog only; it does not resume unrelated application packets.
- This pause does not block routine job-search refresh, role discovery, shortlist maintenance, or Emily-facing digest/report sends that are about job availability rather than application packets.
- If a paused packet/gate/decision ever needs Emily or Jaret, ask in Discord or email Emily with Jaret CC'd; do not route the ask only to Obsidian.

## Current search state

- EJS-035 is the only authorized role-specific card in `Doing`.
- Blocked application-tailoring cards should stay parked unless Jaret explicitly reopens one.
- Current P0 priority is the BDA presentation critical path; job-availability monitoring is secondary until the presentation backlog is complete or temporarily unable to progress.

Format rule:
- Keep job-search updates concise, link-first, and explicit about confidence or evidence gaps.
- Treat all external role postings as read-only evidence.
- Do not apply, log into portals, contact recruiters/hiring managers, send outreach, or take public action without explicit approval.
