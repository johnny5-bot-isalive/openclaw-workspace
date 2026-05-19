# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Current Local Notes

### OpenClaw CLI

- Use `openclaw --version` to check the installed/current OpenClaw version.
- Do not use bare `openclaw version` for version checks on this install; it currently hangs.

### Obsidian

- The Nexus vault (Windows): `C:\Users\Jaret\Obsidian\The Nexus`
- The Nexus vault (WSL via /mnt/c): `/mnt/c/Users/Jaret/Obsidian/The Nexus`
- Project registry note: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Project Registry.md`
- Global backlog note: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Backlog.md`
- Global Kanban note: `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Kanban.md`
- Editing rule: for Obsidian vault paths under `/mnt/c/Users/Jaret/Obsidian/The Nexus`, do **not** use `apply_patch`; that tool is sandbox-limited to the workspace and will fail on vault paths outside it. Prefer `write`, `edit`, or controlled `exec` instead.

### QMD

- `qmd` is installed globally at `/home/jaret/.npm-global/bin/qmd`
- Default exact-search usage: `qmd search "..."`
- Default semantic-search usage: `QMD_LLAMA_GPU=off qmd query "..."`
- Common checks: `qmd status` and `qmd collection list`
- Canonical vault-backed collections now cover the active numbered vault folders except excluded areas: `00 Inbox`, `10 Spaces`, `20 Library`, `40 Agent Nexus`, and `70 History`
- Use QMD first for fuzzy semantic note retrieval across workspace and Obsidian notes
- Prefer `memory_search` for OpenClaw runtime memory recall
- Prefer grep/read for exact text or exact path lookups

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
