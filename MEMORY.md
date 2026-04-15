# MEMORY.md

Long-term curated memory for this workspace.

- OpenClaw is running as a systemd-managed user service in this environment.
- Native OpenClaw cron is configured for a daily 9:00 AM America/Los_Angeles update approval prompt, a 12:10 AM daily retrospective, a 3:00 AM Dreaming sweep, a 5:00 AM workspace sync, and a weekly Sunday 9:30 AM `MEMORY.md` hygiene review.
- The daily update check now runs as an isolated cron job that checks `openclaw update status` and announces in `#mission-control` only when an update is available, so Jaret gets an explicit approval prompt before any manual update happens.
- The workspace sync is an overnight docs-focused commit-and-push job for `/home/jaret/repos/openclaw-workspace`; it prioritizes pushing the current workspace state to `origin` and stays silent unless there is a blocker.
- Obsidian is implemented as a durable second-memory and collaboration layer, with plain Markdown as the system of record and plugins treated as optional accelerators.
- The active Obsidian vault root for the memory project is `G:\My Drive\Obsidian Vaults\Second Brain` on Windows, which maps to `/mnt/g/My Drive/Obsidian Vaults/Second Brain` in WSL/Linux. This path should be treated as durable setup memory and reused instead of re-asking.
- MiniMax M2.7 is configured as the default subagent model for lower-cost grunt work, while the main agent default remains `openai-codex/gpt-5.4`.
- Max is the named MiniMax grunt-work subagent and should be the default choice for repetitive setup, cleanup, indexing, evaluation passes, and other low-risk execution-heavy tasks unless there is a clear reason to keep the work with Johnny directly.
- QMD is now adopted as a CLI-first local retrieval layer for workspace and Obsidian notes on this machine. Default to CPU-only usage (`QMD_LLAMA_GPU=off`). Use QMD for fuzzy semantic cross-note search, `memory_search` for native runtime recall, and ripgrep for exact lookup. QMD is not a source of truth, and MCP exposure is deferred for now.
- Jaret approved the future workflow direction of keeping one control-plane heartbeat while moving active projects toward project-scoped sessions and local boards. The durable plan lives in Obsidian under `40 Agent Nexus/Projects/Project-Scoped Workflow/`, with OpenCode Setup designated as the first pilot once the registry/template layer is built.
- OpenClaw 2026.4.12 is installed. Relevant takeaways for this setup: bundled Codex provider/app-server harness support, better Active Memory and QMD recall behavior, cron/heartbeat reliability fixes, and a CLI update fix for stale post-update runtime imports.
