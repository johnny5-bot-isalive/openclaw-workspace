# OpenClaw Workspace

This repository is the working memory and operating surface for Jaret's OpenClaw setup.

It is not the OpenClaw source repo. It is the assistant's home directory: identity, memory, standing rules, heartbeat behavior, helper scripts, and small local operational notes live here.

## What this workspace is for

- storing durable assistant context and operating rules
- keeping short-term and long-term memory in plain Markdown
- holding local notes that should not live in shared upstream docs
- driving recurring work through heartbeat, Kanban, and backlog notes
- keeping a lightweight audit trail of important setup decisions

## Key files

- `AGENTS.md` - workspace rules, memory policy, cron standing orders, and trust boundaries
- `SOUL.md` - assistant voice and personality guidance
- `USER.md` - facts about the human being helped
- `MEMORY.md` - curated long-term memory
- `memory/YYYY-MM-DD.md` - append-only daily notes and session memory
- `HEARTBEAT.md` - operational heartbeat instructions
- `TOOLS.md` - local environment notes and important paths
- `IDENTITY.md` - assistant identity metadata
- `bin/` - small local helper scripts, when needed

## Important external paths

### Obsidian Second Brain

- Windows: `G:\My Drive\Obsidian Vaults\Second Brain`
- WSL/Linux: `/mnt/g/My Drive/Obsidian Vaults/Second Brain`

### Canonical execution board

- Backlog: `/mnt/g/My Drive/Obsidian Vaults/Second Brain/40 Agent Nexus/Backlog.md`
- Kanban: `/mnt/g/My Drive/Obsidian Vaults/Second Brain/40 Agent Nexus/Kanban.md`

## Operating model

This workspace uses a split-memory model:

- `MEMORY.md` and `memory/` are lightweight runtime continuity
- Obsidian is the durable collaborative second brain
- QMD is the local fuzzy note-retrieval layer
- exact lookup should still prefer `read`, `grep`, or ripgrep-style searches

## Heartbeat behavior

Heartbeat work is execution-driven, not status-driven.

In practice that means:

1. check the Kanban first
2. advance an active Johnny card if one exists
3. otherwise pull the next eligible backlog item into the Kanban
4. keep Backlog and Kanban reconciled in the same turn
5. report progress or a blocker, not empty churn

## Automation currently in use

- daily update approval prompt: 9:00 AM America/Los_Angeles
- daily retrospective: 12:10 AM America/Los_Angeles
- workspace sync: 5:00 AM America/Los_Angeles

The update check asks in `#mission-control` when a new OpenClaw build is available.
The workspace sync is a markdown/docs commit-and-push job for this repo. Its primary job is to push the current workspace state to `origin`, and it stays silent unless it hits a blocker.

## Trust boundary

This workspace contains private operating context.

For this setup, the private Discord space operated by Jaret is trusted, including:

- `#mission-control` (`channel:1491545112562503924`)
- heartbeat channel (`channel:1493275133228351538`)

Those channels may be treated like main-session surfaces for reading and updating workspace operating files when the conversation is clearly with Jaret.

## QMD notes

On this machine, default to CPU-only QMD use:

```bash
QMD_LLAMA_GPU=off npx -y @tobilu/qmd status
QMD_LLAMA_GPU=off npx -y @tobilu/qmd query "..."
```

Preferred retrieval split:

- QMD for fuzzy semantic note search
- `memory_search` for runtime memory recall
- `read`/`grep` for exact lookup

## Related repositories and docs

- OpenClaw source: `https://github.com/openclaw/openclaw`
- Local OpenClaw docs: `/home/jaret/.npm-global/lib/node_modules/openclaw/docs`
- Docs mirror: `https://docs.openclaw.ai`

## Notes

Keep this repo plain Markdown first. Prefer simple files, durable paths, and small explicit rules over clever automation that becomes hard to trust.
