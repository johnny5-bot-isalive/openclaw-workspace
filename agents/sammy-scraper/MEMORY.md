# MEMORY.md

Durable research-specific memory. Keep this file lean: do not store project-specific rules here; store them in the relevant project note and keep only a pointer.

## General research preferences

- Jaret prefers a markdown-first workflow, with Obsidian as the durable source of truth.
- For large research topics, collect sources and iterative reports in a topic-dedicated folder instead of dropping only one final brief.
- For blocked research surfaces, prefer APIs and aggregators before browser-based fallback.
- Browser-based research is an explicit exception path, not the default.
- The local OpenClaw browser lane is operational in this environment. Sammy may use the `browser` tool plus the `browser-automation` skill for bounded read-only inspection when lighter lanes are insufficient.
- Playwright-backed browser actions are working here now, including direct tab open, `navigate`, and `snapshot` in both `aria` and `ai` formats.
- Keep browser use bounded and read-only: no stealth, captcha bypass, login automation, high-volume crawling, or outbound actions.
- Research outputs should stay concise, link-first, and explicit about uncertainty or remaining evidence gaps.
- Review/approval routing preference: when Sammy needs Jaret to review or approve something, use the active project workflow. For Emily Job Search specifically, do not route gated material only to Obsidian because Emily does not have vault access; ask in Discord or send email to Emily with Jaret CC'd.

## Project rule pointers

- Emily Job Search standing rules live in `/mnt/c/Users/Jaret/Obsidian/The Nexus/40 Agent Nexus/Projects/Emily Job Search/Project Rules.md`. Read that note for current search, digest, delivery, wording, routing, and QA rules; do not rely on older promoted-memory fragments for this project. Current durable rule: routine Emily-facing digest/report emails do **not** need per-send approval after refresh, render, and attachment QA pass; send to Emily with Jaret CC'd unless a blocker/QA/freshness/transport/judgment exception exists. For gated/decision material, ask in Discord or email Emily with Jaret CC'd rather than using Obsidian Inbox as the action queue.
