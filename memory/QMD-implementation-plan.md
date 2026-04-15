# QMD Implementation Plan

Date: 2026-04-11
Owner: Johnny 5
Status: adopted for local pilot use

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

Adopt QMD for local pilot use now.

Do not wire it deeply into everything yet.
The pilot succeeded well enough to justify CLI-first usage on this machine, but MCP/server integration should wait until the operating model is more settled and the retrieval patterns are better documented.

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

## Current operating model

Pilot result summary:
- QMD is working well enough to adopt as a local retrieval layer for the memory project.
- The pilot corpus was installed and configured successfully with collections for `workspace-memory`, `agent-nexus`, `openclaw-space`, and `daily-logs`.
- File indexing, context attachment, embeddings, lexical search, and hybrid query all worked.
- CPU-only mode is required on this machine to avoid a Vulkan build/runtime path.
- Query expansion can drift on smaller corpora, so QMD should be used with deliberate query patterns rather than treated as a magical default.

Recommended operating model:
- Use QMD as a local CLI-first retrieval tool.
- Keep QMD out of the source-of-truth role.
- Prefer CPU-only execution by default on this machine.
- Delay MCP exposure until normal CLI usage patterns are stable and documented.

Recommended usage split:
- Use `memory_search` for native OpenClaw memory and prior-work recall.
- Use `grep`/`find`/direct reads for exact path, filename, or literal-text lookups.
- Use QMD when the question is fuzzy, cross-note, semantic, or spans both workspace and Obsidian memory surfaces.

Recommended local command pattern:

```bash
QMD_LLAMA_GPU=off npx -y @tobilu/qmd --help
QMD_LLAMA_GPU=off npx -y @tobilu/qmd status
QMD_LLAMA_GPU=off npx -y @tobilu/qmd query "active obligations layer"
```

If collection maintenance is needed later, keep using the same CPU-only prefix.

## Decision summary

Current decision:
- adopt QMD as local retrieval infrastructure for this memory project setup
- keep it CLI-first and CPU-only by default on this machine
- keep QMD as retrieval infrastructure, not memory authority
- defer MCP/server integration until its niche and workflow ergonomics are clearer

## Open questions

1. Should the workspace side expand beyond `memory/**` plus `MEMORY.md` to include selected root operating notes like `AGENTS.md` and `HEARTBEAT.md`?
2. Should the corpus expand to selected OpenClaw reference notes from `20 Library/OpenClaw Reference/**`, or stay tight for signal quality?
3. What reindex cadence is acceptable in practice: manual only, on-demand, or periodic?
4. At what point would MCP exposure add enough value to justify the extra integration surface?

## Recommended next action

Next concrete step: document the QMD operating model in the shared/Johnny working notes so the vault and workspace memory surfaces stay aligned with the successful pilot outcome.
