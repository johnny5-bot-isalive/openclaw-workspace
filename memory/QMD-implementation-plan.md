# QMD Implementation Plan

Date: 2026-04-11
Owner: Johnny 5
Status: proposed

## Goal

Evaluate and adopt QMD as a local retrieval layer for the memory project where it adds real value, without bloating or replacing the existing split:

- native OpenClaw memory for active retrieval inside agent workflows
- workspace markdown memory for lightweight operational continuity
- Obsidian for durable collaborative/project memory

## What QMD appears to be

QMD is a local hybrid retrieval system for docs and notes.

Based on the upstream repo, it provides:
- BM25 full-text search
- vector semantic search
- hybrid query mode with reranking
- local GGUF-backed models via node-llama-cpp
- CLI, Node SDK, and MCP server modes
- collection/context modeling that can improve retrieval quality
- agent-friendly outputs like JSON, files lists, and direct document fetches

## Why it is interesting for this project

QMD could help in places where our current memory surfaces are strong at storage and organization, but weaker at broad local retrieval across notes and documentation.

Most promising uses:
1. searching across a larger Obsidian vault and workspace markdown corpus
2. feeding higher-quality local context into coding agents and MCP-capable tools
3. reducing dependence on ad hoc grep/find flows when semantic retrieval matters
4. supporting a future "active obligations" layer by making project-state notes easier to retrieve reliably

## Where QMD should fit

Recommended role:
- QMD should be an optional local retrieval engine sitting beside Obsidian and workspace markdown, not a source of truth.
- It should index the durable markdown corpus.
- It should not become another place where humans must manually maintain state.

Recommended source-of-truth split:
- OpenClaw native memory: active assistant retrieval and runtime continuity
- workspace memory files: lightweight execution state and local operating notes
- Obsidian vault: durable human-readable project memory
- QMD: retrieval/index/query layer over the markdown corpus

## Recommendation

Adopt QMD in phases.

Do not wire it deeply into everything yet.
Start with a small proof of value on the memory-project corpus, evaluate search quality and operational cost, then decide whether to expose it through MCP for agents.

## Risks and constraints

1. Model/runtime overhead
- QMD downloads and runs several local models.
- This adds disk, CPU, RAM, and possibly slow first-run behavior.

2. Corpus ambiguity
- We need to decide exactly what corpus QMD should index.
- If the Obsidian vault is outside this workspace, we should avoid duplicating content just for indexing.

3. Maintenance overhead
- If indexing requires frequent babysitting, it will work against the goal of a calm memory system.

4. Potential duplication/confusion
- If we are not explicit, users may confuse storage layers with retrieval layers.

5. Multilingual edge cases
- If the vault expands beyond English, embedding model choice may matter.

## Proposed phased plan

### Phase 1, confirm environment and corpus

Confirmed environment:
- Obsidian vault root: `/mnt/g/My Drive/Obsidian Vaults/Second Brain`
- Workspace root: `/home/jaret/repos/openclaw-workspace`

Proposed pilot corpus, first pass:
1. Workspace markdown execution/memory set, indexed in place:
   - `/home/jaret/repos/openclaw-workspace/memory/**/*.md`
   - `/home/jaret/repos/openclaw-workspace/MEMORY.md`
   - optionally later: selected root operating notes like `AGENTS.md` and `HEARTBEAT.md`
2. Obsidian memory-project set, indexed in place:
   - `/mnt/g/My Drive/Obsidian Vaults/Second Brain/40 Agent Nexus/**/*.md`
   - `/mnt/g/My Drive/Obsidian Vaults/Second Brain/10 Spaces/OpenClaw/**/*.md`
   - `/mnt/g/My Drive/Obsidian Vaults/Second Brain/70 History/Daily Logs/**/*.md`
3. Defer broad library indexing until after pilot validation:
   - exclude most of `20 Library/**` on the first pass to keep signal tight
   - exclude `.obsidian/**`, attachments, and archive content

Recommendation:
- index in place, not via duplicated curated copies
- use separate collections for workspace, agent-nexus, openclaw-space, and daily-logs so retrieval quality can be compared by source

Exit criteria:
- exact folders selected
- no ambiguity about source of truth

### Phase 2, local proof of concept

1. Install QMD.
2. Create a dedicated test index for the memory project.
3. Add 1 to 3 collections only.
4. Add clear collection/path context for each collection.
5. Run indexing and embedding.
6. Evaluate real queries from current work.

Suggested evaluation queries:
- qmd implementation plan
- active obligations layer
- Obsidian graph rules
- Max cleanup worker
- OpenClaw update hold / release notes

Success criteria:
- better retrieval than grep for fuzzy/project questions
- acceptable latency on this machine
- manageable setup and reindex workflow

### Phase 3, workflow integration

If Phase 2 is good enough:

1. Add a lightweight wrapper or documented commands for repeated use.
2. Decide whether to expose QMD through MCP for ACP/Claude/Codex-style workflows.
3. Define a minimal reindex cadence:
   - manual
   - on demand
   - or periodic if cheap and reliable
4. Document when to use:
   - native memory_search
   - plain grep/find/read
   - QMD query/search/get

Exit criteria:
- QMD has a clear niche instead of overlapping everything

### Phase 4, obligations integration

If QMD proves useful, use it to support the active obligations layer by ensuring task and state notes are easy to retrieve semantically.

Important: QMD should help retrieve obligations, not become the place where obligations are authored.

## Initial recommended commands

Current environment check:
- `@tobilu/qmd` is not installed yet
- Node: `v25.9.0`
- npm: `11.12.1`
- pnpm: `10.33.0`
- package metadata confirms CLI binary `qmd` is provided by `@tobilu/qmd` version `2.1.0`

Concrete next commands:

```bash
npm install -g @tobilu/qmd
qmd --help
```

Then, if install succeeds, create pilot collections for the defined corpus with collection-specific masks/paths rather than one broad vault import.

Draft collection flow:

```bash
qmd collection add /home/jaret/repos/openclaw-workspace/memory --name workspace-memory --mask "**/*.md"
qmd collection add "/mnt/g/My Drive/Obsidian Vaults/Second Brain/40 Agent Nexus" --name agent-nexus --mask "**/*.md"
qmd collection add "/mnt/g/My Drive/Obsidian Vaults/Second Brain/10 Spaces/OpenClaw" --name openclaw-space --mask "**/*.md"
qmd collection add "/mnt/g/My Drive/Obsidian Vaults/Second Brain/70 History/Daily Logs" --name daily-logs --mask "**/*.md"
```

If QMD requires explicit single-file support for `MEMORY.md`, either:
- add a small workspace-root collection with a narrower mask, or
- duplicate that one file into a pilot notes subset only if the CLI cannot address it directly.

## Decision summary

Best current move:
- do a focused proof of concept
- keep QMD as retrieval infrastructure, not memory authority
- only add MCP/server integration after we verify local value

## Open questions

1. Should the first workspace collection include only `memory/**` plus `MEMORY.md`, or also root operating notes like `AGENTS.md` and `HEARTBEAT.md`?
2. Should the first pilot stay limited to memory-project material, or include selected OpenClaw reference notes from `20 Library/OpenClaw Reference/**`?
3. Do we want QMD primarily for local CLI use, MCP use, or both?
4. How much background indexing/maintenance is acceptable?

## Recommended next action

Next concrete step: create the QMD pilot collections from the confirmed workspace/vault corpus, then install and test QMD against real project queries.
