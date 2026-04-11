# MEMORY.md

Long-term curated memory for this workspace.

- OpenClaw is running as a systemd-managed user service in this environment.
- Native OpenClaw cron is configured for a daily update check and a 3:00 AM workspace sync.
- Hold the OpenClaw 2026.4.9 update until after the first automated 3:00 AM workspace sync has completed cleanly.
- Obsidian is being implemented as a durable second-memory and collaboration layer, with plain Markdown as the system of record and plugins treated as optional accelerators.
- MiniMax M2.7 is configured as the default subagent model for lower-cost grunt work, while the main agent default remains `openai-codex/gpt-5.4`.
