# OPERATIONS.md - Event Runbooks

Load this file only when the current task is a matching system event or operations workflow.

## OpenClaw update check — `[CRON-UPDATE-CHECK]`

When the main session receives the exact system event `[CRON-UPDATE-CHECK]`:

1. Execute `openclaw update status` and `openclaw --version` immediately. Do **not** use bare `openclaw version` for the current version; on this install it hangs.
2. If no update is available, do not send any Discord message.
3. If an update is available, identify both the installed/current version from `openclaw --version` and the target version from update status, then read the official release notes for that target version before asking for approval.
4. Extract the changes that matter for the current setup, especially new capabilities, behavior changes, deprecations, migrations, safety changes, and anything relevant to the current gateway, channels, memory, cron, WSL, ACP, or workspace setup.
5. Write or update a concise durable pre-update review note at `/mnt/c/Users/Jaret/Obsidian/The Nexus/00 Inbox/OpenClaw Update Review.md` with the target version, setup-relevant takeaways, and any workspace/config follow-ups that should happen immediately after the update.
6. If an update is available, send a short approval prompt that mentions the target version and says the release-note review is already captured in the inbox note.
7. Do not install or restart anything from the check job.

This standing order is persistent and is intended to be triggered by the native OpenClaw cron job named `Daily OpenClaw update check`.

When Jaret approves an OpenClaw update and the update is installed successfully:

1. Re-open the pre-update review note and the official release notes if needed.
2. Apply or persist the setup-relevant changes that should land immediately after the update, including workspace/config cleanup, new capability adoption, and retired-workaround removal when appropriate.
3. Update short-term memory and, when appropriate, `MEMORY.md`, `AGENTS.md`, or `TOOLS.md` so useful changes persist.
4. Use those release-note takeaways in future behavior by preferring new native capabilities over older workarounds and avoiding deprecated patterns.
5. Include a concise release-notes brief in the final post-update confirmation, including the new version number and the most relevant changes for the current setup.

## Weekly MEMORY hygiene — `[CRON-MEMORY-HYGIENE]`

When the main session receives the exact system event `[CRON-MEMORY-HYGIENE]`:

1. Review recent `memory/YYYY-MM-DD.md` files, prioritizing the last 7 days and extending slightly further back only if needed for continuity.
2. Treat this as a trusted-context `MEMORY.md` hygiene pass, not a transcript summary.
3. Promote into `MEMORY.md` only items that are clearly durable, reusable, and likely to matter beyond the current day or session, such as:
   - stable preferences
   - reusable environment or setup facts
   - recurring workflow rules
   - durable lessons learned
   - decisions that materially changed future work
4. Do not promote transient status notes, resolved one-off troubleshooting details, routine chronology, or speculative ideas that have not proven durable.
5. Prune or tighten `MEMORY.md` only when an entry is clearly duplicated, superseded, no longer true, or too vague to remain useful.
6. If uncertain, prefer keeping the existing `MEMORY.md` entry and capture ambiguity in daily memory or a working note instead of pruning aggressively.
7. Update short-term memory or Obsidian notes only when that materially helps preserve context around the change.
8. Stay silent unless a blocker appears or the pass made a meaningful durable-memory change worth surfacing briefly.

This standing order is persistent and is intended to be triggered by the native OpenClaw cron job named `Weekly MEMORY hygiene review`, scheduled for Sundays at 9:30 AM America/Los_Angeles.

## Workspace sync — `[CRON-WORKSPACE-SYNC]`

When the main session receives the exact system event `[CRON-WORKSPACE-SYNC]`:

1. Treat pushing the current workspace state to `origin` as the primary goal.
2. From `/home/jaret/repos/openclaw-workspace`, inspect the repo before acting and include untracked markdown/docs files plus tracked docs deletions, not just already-tracked modifications.
3. Stage the eligible workspace docs state, commit it with an AI-generated summary, and push the result to `origin` in the same turn.
4. If there is nothing eligible to sync, stay silent.
5. Send a Discord notification only if the sync fails or if merge conflicts occur.
6. If the sync succeeds cleanly, stay silent on Discord.

This standing order is persistent and is intended to be triggered by the native OpenClaw cron job named `[CRON-WORKSPACE-SYNC]`, scheduled for 5:00 AM America/Los_Angeles.

## Daily retrospective — `[CRON-DAILY-RETRO]`

When the main session receives the exact system event `[CRON-DAILY-RETRO]`:

1. Determine the retrospective date, yesterday in America/Los_Angeles.
2. Treat `memory/YYYY-MM-DD.md` as internal execution memory, not the human-facing retrospective. Do not copy or paraphrase it wholesale into the daily log.
3. Read the global Kanban as the primary operational source.
4. Scan all Discord channel sessions from the last 24 hours as secondary context.
5. Read the existing daily log for the retrospective date if it exists.
6. Read relevant shared and agent working notes only when they add missing context, clarify a decision, or explain why work moved the way it did.
7. Write a completed daily log entry to `70 History/Daily Logs/YYYY-MM-DD.md` as a curated human-facing closeout, not a raw transcript. Use these sections:
   - **Summary**
   - **Completed**
   - **Lessons learned**
   - **Decisions made**
   - **New backlog items**
   - **Still active / carry forward**
8. Keep the daily log concise. Prefer synthesis over chronology, and omit low-value details already captured in local memory files, chat transcripts, or ordinary working notes.
9. For each completed Kanban card, copy it to `99 Archive/Kanban Archive/YYYY-MM.md`, retaining card id, title, owner, completed date, result, and source project. Remove completed cards from the live Kanban.
10. Keep active `Ready`, `Doing`, and `Blocked` cards on the live Kanban.
11. Stay silent on Discord unless the retrospective fails outright, a major blocker surfaces, or a significant new follow-up backlog item was created.

This standing order is persistent and is triggered by the native OpenClaw cron job named `[CRON-DAILY-RETRO]`, scheduled for 00:10 America/Los_Angeles daily.
