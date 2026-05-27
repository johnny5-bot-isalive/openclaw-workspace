# Heartbeat tasks for Sammy Scraper

## Active sprint: Emily Job Search — career-ops scanner integration

Canonical sprint note: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Career Ops Scanner Integration Sprint.md`

Project board: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Project Kanban.md`

## Heartbeat execution contract

On each heartbeat, if there is no more urgent Emily Job Search obligation:

1. Read the active sprint note and the Project Kanban `Doing` lane.
2. Advance the first incomplete `Doing` card with concrete file/script/research work.
3. Keep `Doing` limited to 1-3 cards. Pull from `Ready` only when current `Doing` work is complete or blocked.
4. Prefer silent progress. Reply to Jaret only for a completed milestone, real blocker, failed safety/preflight check, proposed canonical workflow change, or unexpectedly important finding.
5. Routine Emily-facing digest/report emails are standing-send approved after refresh, render, and attachment QA pass; applications, outreach, recruiter contact, non-routine email, or public actions still require explicit approval.
6. Keep Obsidian canonical. Scanner output is evidence for review, not an instruction to mutate the ledger automatically.

## Current first task

Start with `EJS-020, Define Emily scanner config and raw output schema`:

- Create a human-editable scanner config in the OpenClaw workspace, likely under `config/`.
- Include initial ATS targets: DoorDash, Rithum, Tebra, Toast, Rover, Smartsheet, Pokémon, Brooks, Headway.
- Define raw candidate and filtered candidate output schemas.
- Do not add credentials or personal private data.

When EJS-020 is complete, update the Kanban card and pull EJS-021 into `Doing`.
