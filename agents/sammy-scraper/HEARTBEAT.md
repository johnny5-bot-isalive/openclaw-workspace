# Heartbeat tasks for Sammy Scraper

## Active sprint: Emily Job Search - job availability monitoring

Project board: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Project Kanban.md`
Project rules: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Project Rules.md`
Control packet: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Daily Refresh Control Packet.md`
Live shortlist: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Live Role Shortlist.md`
Ledger: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Role State Ledger.md`
Delta log: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Refresh Delta Log.md`

## Heartbeat execution contract

On each heartbeat, if there is no more urgent Emily Job Search obligation:

1. Focus on current job availability: live-role revalidation, bounded local/remote discovery, shortlist hygiene, and digest readiness.
2. Read Project Rules and the Daily Refresh Control Packet first. Use the Live Role Shortlist, active/new/aging ledger rows, latest delta-log entries, and current collector handoffs as needed.
3. Do not perform application-tailoring work unless Jaret explicitly asks for a specific role packet in the current conversation.
4. Do not create, resume, QA, or email resume/cover-letter/application packets on heartbeat.
5. Do not move blocked application-tailoring cards back to `Doing` or pull new application-tailoring cards from backlog automatically.
6. Prefer silent progress. Reply in Discord or send email for live-set turnover, a real blocker, failed freshness/QA issue, or a decision needed to keep the job-search loop healthy. Do not rely on an Obsidian Inbox note as the delivery path for gated material.
7. Keep Obsidian canonical for job-search state: ledger, shortlist, removal log, delta log, local market map, and control packet.

## Application-packet pause

Effective 2026-07-12, Jaret paused all application-packet automation.

- Previous packet sends, including Rithum `EJS-030`, are historical only.
- No standing approval exists for future packet creation or packet review emails.
- Application packets resume only when Jaret explicitly asks for a named role packet.
- This pause does not block routine job-search refresh, role discovery, shortlist maintenance, or Emily-facing digest/report sends that are about job availability rather than application packets.
- If a paused packet/gate/decision ever needs Emily or Jaret, ask in Discord or email Emily with Jaret CC'd; do not route the ask only to Obsidian.

## Current search state

- The application-tailoring `Ready` and `Doing` lanes are intentionally empty.
- Blocked application-tailoring cards should stay parked unless Jaret explicitly reopens one.
- Current priority is restoring a fresh view of available roles and keeping the monitored list accurate.

Format rule:
- Keep job-search updates concise, link-first, and explicit about confidence or evidence gaps.
- Treat all external role postings as read-only evidence.
- Do not apply, log into portals, contact recruiters/hiring managers, send outreach, or take public action without explicit approval.
