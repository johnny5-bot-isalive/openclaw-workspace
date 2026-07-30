# Heartbeat tasks for Sammy Scraper

## Current state: EJS-035 — await BDA post-interview status

Priority: **Blocked pending Emily's next BDA update**

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

1. Read Project Rules, the project board, the BDA role context, the BDA presentation context, and the BDA child backlog.
   - Use the exact Sammy-owned dispatch target above. Do not dispatch to `agent:main:discord:channel:1498012283983364146`; cross-agent session visibility is intentionally disabled.
2. Do not resume presentation production, repeat deadline reminders, or monitor the old working-package Gmail thread. The final nine-slide PDF was recorded as locked and sent to the hiring manager at 11:00 a.m. PT on 2026-07-28.
3. Check the exact BDA session only for a new Emily status update. Do not message Emily merely because the status is unchanged.
4. If Emily provides a post-interview update, record only the confirmed facts in the rehearsal checklist, BDA role/subproject context, child backlog, and EJS-035 Kanban card. Do not infer whether the interview occurred or its outcome.
5. If no BDA update exists, use the heartbeat for current job availability: live-role revalidation, bounded discovery, shortlist hygiene, and digest readiness.
6. Prefer silent progress. Notify only for a meaningful role-state change, completed deliverable, blocker, or decision Emily/Jaret must make.
7. Do not monitor or reactivate Nordstrom, Tebra, or other parked application blockers.
8. Treat all external collection as read-only. Do not apply, contact recruiters or hiring managers, log into portals, or take public action without explicit approval.

## Application-packet pause

Effective 2026-07-12, Jaret paused all application-packet automation.

- Previous packet sends, including Rithum `EJS-030`, are historical only.
- No standing approval exists for future packet creation or packet review emails.
- Application packets resume only when Jaret explicitly asks for a named role packet.
- Jaret's explicit activation of EJS-035 authorizes the BDA interview-presentation backlog only; it does not resume unrelated application packets.
- This pause does not block routine job-search refresh, role discovery, shortlist maintenance, or Emily-facing digest/report sends that are about job availability rather than application packets.
- If a paused packet/gate/decision ever needs Emily or Jaret, ask in Discord or email Emily with Jaret CC'd; do not route the ask only to Obsidian.

## Current search state

- EJS-035 is in `Blocked` awaiting Emily's post-interview status; no presentation-production work is authorized without new evidence.
- There are no authorized role-specific cards in `Doing`.
- Blocked application-tailoring cards should stay parked unless Jaret explicitly reopens one.
- Current heartbeat work is job-availability monitoring and digest readiness unless Emily supplies a BDA update.

Format rule:
- Keep job-search updates concise, link-first, and explicit about confidence or evidence gaps.
- Treat all external role postings as read-only evidence.
- Do not apply, log into portals, contact recruiters/hiring managers, send outreach, or take public action without explicit approval.
