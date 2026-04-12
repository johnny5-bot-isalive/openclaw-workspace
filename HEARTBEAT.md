# HEARTBEAT

When a heartbeat arrives, use the global backlog and Kanban in the Second Brain vault as the default execution spine.

## Canonical execution surfaces
- Backlog: `/mnt/g/My Drive/Obsidian Vaults/Second Brain/40 Agent Nexus/Backlog.md`
- Kanban: `/mnt/g/My Drive/Obsidian Vaults/Second Brain/40 Agent Nexus/Kanban.md`

## Heartbeat execution rule
1. Read the global Kanban.
2. Identify the current agent's name and find the highest-priority card assigned to that agent with status `doing` or `ready` that is not blocked.
3. If such a card exists, take one real step toward completing it, not just a status check.
4. Update the Kanban card immediately after the work is performed so status, next action, and outcome stay current.
5. Update any relevant project or working notes.
6. If no actionable Kanban card exists for the current agent, read the global Backlog.
7. Pull the highest-priority backlog item that should be owned by the current agent into the Kanban as `ready` or `doing`, and delete it from the Backlog when it is pulled.
8. Start working that newly pulled item immediately, then update the Kanban card state right after the work is performed.
9. Only reply `HEARTBEAT_OK` if there is no actionable unblocked Kanban card for the current agent, no eligible backlog item to pull for the current agent, no urgent issue, and no meaningful progress update to send.

## Current priorities
- Keep heartbeat execution-driven instead of status-driven.
- Ensure each agent advances its own assigned work from the shared global backlog and Kanban.
- Run the QMD pilot for the memory project after the global backlog/Kanban loop is in place.
- Keep shared Nexus notes, Johnny-specific memory notes, project tracker/state notes, and local workspace memory aligned as durable second-memory surfaces.

## Quiet-hours behavior
- If there is no meaningful progress, no urgent blocker, and no important completion/update to report, reply `HEARTBEAT_OK`.
- Otherwise send only a concise progress or blocker update.
