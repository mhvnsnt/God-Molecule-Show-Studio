# Memory System Research — Oct 2026

**For:** Muse Spark (the agent) + owner, TRIPPEDD / Orion Enterprises operation
**Date:** 2026-10-10
**Goal:** Evaluate the state of the art in *free/self-hostable* agent memory systems and recommend what to adopt.

**Current state (what we have now):**
- `~/MEMORY.md` — curated long-term memory (facts, people, laws, incidents)
- `~/memory/*.md` — daily logs; `~/memory/people/`, `~/memory/groups/` — relationship pages
- `muse.memory_search` / `muse.memory_get` / `muse.memory_explain` — tool-based recall
- `~/workspace/agent-ops/checkpoints/` — machine-readable task state (JSON) for 600+ tasks

This is **markdown-based semantic memory** with tool-driven recall. It works, but it has real gaps:
1. **No episodic memory** — can't ask "what did we do the week of Oct 1?" or "how many times has the owner corrected me about X?" without grep archaeology.
2. **No graph relationships** — memories are files, not a queryable entity graph ("everything about Marshead GLB" is scattered).
3. **No procedural memory** — corrections become laws in AGENTS.md by hand; the system doesn't *learn* from failures automatically.
4. **Recall is retrieval-only** — `memory_search` matches text, not meaning across rewordings; no temporal reasoning ("what changed about the tractor price?").
5. **Subagents don't share memory** — each worker starts cold; shared context lives only in briefs and checkpoints.

---

## Systems evaluated

### 1. Mem0 (mem0ai/mem0) — the biggest community

**What it is:** A memory layer for AI agents: automatic extraction of facts/preferences from conversations, stored in a hybrid vector + KV + graph store, retrievable by semantic search. Also ships **OpenMemory** — a self-hosted memory app with a web UI and MCP server.

**Cost:** OSS core (Apache 2.0). Hosted cloud has free tier, then $19–$249/mo. Graph features are paywalled on cloud (~$249/mo tier).

**Self-hostable:** Yes — `docker compose up -d` from the mem0 repo's OpenMemory folder. Local stack: OpenMemory MCP server (`localhost:8765`), Qdrant vector DB (`localhost:6333`), web UI (`localhost:3000`). Embeddings via Ollama (`nomic-embed-text`, free, local). Neo4j optional for graph memory.

**Memory types:** Semantic (facts/preferences). Weak episodic, no procedural memory.

**Fit here:**
- ✅ Free self-hosted path is real (Qdrant + Ollama, no API keys)
- ✅ MCP server means the agent can query it as a tool — fits this environment's tool-based architecture
- ✅ Huge community (~63K stars), MCP + 21 framework integrations, AWS partnership (exclusive memory for Strands SDK)
- ✅ Supports per-`user_id` memory — good for separating the owner's stuff from side-chat stuff
- ❌ Graph memory is Pro-tier only on cloud; self-hosted graph needs Neo4j (another DB to operate)
- ❌ It's a *conversational personalization* tool at heart — built for chatbots remembering user preferences, not for a production studio's episodic/procedural memory
- ⚠️ Benchmarks are disputed (their LoCoMo numbers vs Zep's are contested) — treat "10x" claims as marketing

**Integration difficulty:** Medium. Docker compose stack (~3 containers). Embeddings can be local (Ollama). LLM for memory extraction can be a local/cheap model — no OpenAI key strictly needed.

### 2. Cognee (topg/cognee) — "one brain, every agent" — **TOP PICK**

**What it is:** An open-source AI memory *platform*: ingestion pipeline (ECL) turns text/docs/code/audio transcripts into a knowledge graph + vector store, all inside **one Postgres instance** (graph backend on Postgres, pgvector for embeddings, SQL session cache). Exports to an open format (COGX). Ships MCP server, Python + TypeScript SDKs, LangGraph integration, and a Rust core for edge use.

**Cost:** Fully free and open (Apache 2.0, full features, no caps). Commercial cloud exists but is optional.

**Self-hostable:** Yes — `pip install "cognee[postgres]"`, everything runs on a single Postgres. Local dev even runs fully embedded (SQLite/LanceDB/Kuzu) with no services at all.

**Memory types:** Semantic + graph relational. The differentiator: **memory that improves with use** — when agents retrieve/correct/reuse info, those interactions become signals and cognee learns which facts matter, which are stale, which sources workers actually rely on. Closest thing in the field to *procedural* learning from corrections.

**Fit here — strong:**
- ✅ **Single Postgres = minimal ops.** We do not have to run Qdrant + Neo4j + Redis + an app server. One DB is the whole brain. (Disk is at 87% — this matters.)
- ✅ MCP server means it plugs straight into the agent tool environment
- ✅ "One brain, every agent" — all subagents read/write the same memory backend. Directly fixes the "workers start cold" problem.
- ✅ Graph memory is a *core feature*, not paywalled (unlike Mem0's cloud)
- ✅ Corrections dying in one chat is exactly our current pain (the owner corrects, we write a law by hand). Cognee's learning-from-correction design is the closest off-the-shelf match to "the brain gets better when he corrects us."
- ✅ Export is open (COGX) — no lock-in if we outgrow it
- ⚠️ Newer/smaller community (~30K stars), still evolving fast — docs move

**Integration difficulty:** Low-Medium. Postgres is already the simplest DB to run. The MCP server is the clean integration point.

### 3. Graphiti (getzep/graphiti) — temporal knowledge graph

**What it is:** The open-source engine behind Zep. A **bi-temporal knowledge graph** — it tracks entities and relationships with *when they were true* and *when we learned it*. Native temporal reasoning ("what did we believe about the budget in September vs now?").

**Cost:** OSS (Apache 2.0) engine is free. The hosted Zep product is cloud-only (Community Edition was deprecated in 2025) and starts ~$25/mo.

**Self-hostable:** Yes for Graphiti itself, but you assemble the stack: Neo4j (or FalkorDB) + an LLM for extraction. Zep-as-a-service is cloud-only.

**Memory types:** Semantic-temporal. Excellent at time-indexed episodic-ish memory: "what did we know and when."

**Fit here:**
- ✅ Best temporal reasoning in the field — real answer to our episodic-memory gap ("what changed about the tractor listing price?")
- ✅ Strong multi-hop queries (entity → relationship → entity), which vector-only search can't do
- ❌ **Ops burden:** needs Neo4j managed, plus heavy graph construction (~600K tokens/conversation claimed in one disputed study — treat as directional, but the cost is real)
- ❌ Background graph building means freshly ingested info isn't immediately retrievable — bad for live conversation memory
- ❌ Overkill for the "remember this preference" case; built for enterprise relational reasoning
- ⚠️ Zep CE deprecation means self-hosters are on the lower-level Graphiti API, not the polished product

**Integration difficulty:** Medium-High. Graph DB ops + extraction pipeline tuning.

### 4. Letta (letta-ai/letta, formerly MemGPT) — OS-inspired agent memory

**What it is:** The full agent runtime from the MemGPT research (UC Berkeley). Memory as an **OS hierarchy**: core memory (always in context), recall memory (conversational history), archival memory (the agent edits it itself). Unique: **the agent controls its own memory** — it writes to archival memory with function calls. Sleep-time compute: background processing during idle time.

**Cost:** Free and open (Apache 2.0) self-hosted server. Cloud API exists (free tier ~3 agents).

**Self-hostable:** Yes — Letta server via Docker.

**Memory types:** Semantic + partial episodic (conversation archival). No graph. No procedural.

**Fit here:**
- ✅ Self-editing memory is a genuinely different paradigm — the agent *chooses* what to remember, which matches how this operation already works (curated MEMORY.md)
- ✅ Sleep-time compute = background memory consolidation during idle — attractive for a 24/7 operation
- ✅ Native multi-agent support
- ❌ **It's a full agent runtime, not a memory layer.** Adopting Letta means adopting its agent framework — we'd be replacing our architecture, not augmenting it. This environment (Muse Spark, tool-based) doesn't run on Letta's agent loop.
- ❌ Temporal reasoning is weak (noted in comparisons: Letta's LoCoMo score comes from flat files, not real memory)
- ⚠️ Integration = rewrite, not upgrade

**Integration difficulty:** High. Wrong layer of the stack for us — it's a framework, we need a memory *backend*.

### 5. LangMem / LangGraph BaseStore — the incumbent for LangGraph shops

**What it is:** LangChain's first-party memory: `BaseStore`/`PostgresStore` + LangMem for semantic/profile memory. If you build on LangGraph, this is "do nothing and get memory."

**Fit here:** We don't run on LangGraph. Mentioned for completeness; not applicable to this tool-based agent architecture.

### 6. Lightweight alternatives (worth knowing)

- **claude-mem** — tiny self-hosted MCP memory with *timeline* queries (memories by date range) + semantic search. No graph. Good "step 1" episodic add-on, very cheap to run.
- **Hindsight** — newer OSS (MIT): one-Docker-command, embedded Postgres, multi-strategy retrieval. The "I want cognee's simplicity with even less setup" option. Watch it.
- **Hand-rolled pgvector** — extremely common in practice; a single table with embeddings and timestamps covers 70% of the episodic need with ~50 lines of code. Honest fallback if no new dependency is wanted.
- **Mengram / Scholar Agent** — niche/research-focused; not a fit here.

---

## Comparison table

| | Mem0 + OpenMemory | **Cognee 1.0** | Graphiti (Zep engine) | Letta |
|---|---|---|---|---|
| License | Apache 2.0 | Apache 2.0 | Apache 2.0 | Apache 2.0 |
| Free self-hosted | Yes (Docker) | **Yes (pip + Postgres)** | Yes (DIY stack) | Yes (Docker) |
| DBs to operate | Qdrant (+Opt Neo4j) | **1: Postgres** | Neo4j/FalkorDB | Postgres + pgvector |
| Graph memory | Paywalled on cloud | **Core feature** | Core feature | No |
| Temporal/episodic | Weak | Medium | **Best-in-class** | Partial |
| Learns from corrections | No | **Yes (design goal)** | No | Via self-edit |
| MCP server | Yes | Yes | No | Yes |
| Community | ~63K ★ | ~30K ★ | ~30K ★ | ~24K ★ |
| Integration fit | Medium | **High** | Medium-Low | Low (framework) |

---

## Recommendation

### Pick #1: Cognee 1.0 on Postgres — the memory backend

It solves our biggest gaps (graph relationships + correction-learning + one shared backend for all subagents) with the smallest ops footprint (one Postgres, already the DB we know). MCP server plugs into the tool environment.

### Pick #2: Mem0 OpenMemory self-hosted — the conversational memory sidecar

Biggest community, simplest Docker story, proven at "remember the user's preferences across chats." Use it *only* for the conversational/personalization slice if Cognee's retrieval doesn't cover it. Not both at once — avoid two brains.

### What NOT to adopt
- **Zep Cloud** — money, vendor lock-in, cloud-only. Graphiti engine is the only sane Zep-adjacent path, and Cognee covers the same ground with less ops.
- **Letta** — right ideas, wrong layer. It's an agent framework; we're not rebuilding the agent.
- **Don't replace MEMORY.md** — whatever we adopt, the markdown files stay the *curated source of truth* (laws, owner decisions, identity). The memory backend is the *searchable substrate*; MEMORY.md is the constitution. A nightly or weekly job syncs curated entries into the backend, never the reverse without review.

### Concrete integration steps (run when disk < 75% — currently 87%, so RESEARCH ONLY for now)

**Phase 0 — prerequisites (do first, free):**
1. Free disk below 75% per the disk management law. The memory stack needs ~2–5 GB headroom (Postgres data + models).
2. Confirm Postgres available locally or install (`apt install postgresql` / docker). If Docker: one container.
3. Confirm Python 3.10+ and `pip install "cognee[postgres]"` in a venv (record `pip freeze` to `~/workspace/agent-ops/venv-manifests/` per the disk law).

**Phase 1 — stand up Cognee (half a day):**
4. Set env: `DB_PROVIDER=postgres`, `VECTOR_DB_PROVIDER=pgvector`, `GRAPH_DATABASE_PROVIDER=postgres`, `CACHE_BACKEND=postgres`, host/user/db.
5. Start the Cognee MCP server; register it as an MCP tool server for the agent (and note it in `~/TOOLS.md`).
6. Embeddings: start with a light local embedder (or a free API tier) — keep embeddings local to stay free.

**Phase 2 — ingest the existing memory (one day):**
7. Write `~/workspace/tools/brain/ingest_memory.py`: walks `~/MEMORY.md`, `~/memory/*.md`, `~/memory/people/`, `~/memory/groups/`, `~/AGENTS.md` standing rules, and `~/workspace/agent-ops/checkpoints/*.json` (task summaries); feeds each as a dated document to Cognee with metadata `{source, date, kind: fact|decision|law|person|task}`.
8. Checkpoint manifests (`steps_completed`, `decisions`, `blockers`) go in as *episodic* records — this is the first time 600+ task histories become queryable.
9. Spot-check retrieval: "what did we decide about Mr. Gold's color?" / "which rig repairs failed in October?" must return real answers before going further.

**Phase 3 — wire into the workflow (ongoing):**
10. Add a standing rule: workers write a 3-line "what happened" summary to the memory backend at task end (checkpoint `status completed` hook calls it).
11. Owner corrections get ingested *same-day* with kind `law` — this is the correction-learning loop Cognee is built for.
12. Weekly: a cron reviews low-confidence/stale entries (cognee's staleness signals) and proposes MEMORY.md updates for the owner to approve.

**Phase 4 (optional) — Mem0 OpenMemory sidecar:**
13. Only if Phase 3 shows a gap in conversational preference recall. `docker compose up` OpenMemory + Qdrant + Ollama, register MCP, scope to `user_id=owner`.

**Do NOT install anything now.** Disk is at 87%; the hard ceiling is 88%. This doc is the plan. Run Phase 0 only after the disk guardian gets us under 75%.

---

## Sources
- Comparison survey (danzakon/dan-life, 2026-03): https://github.com/danzakon/dan-life/blob/HEAD/research/reports/20260308-agent-memory-comparison.md
- Open-source memory systems audit (Hindsight blog, 2026-08): https://github.com/shaikroshni2008-coder/hindsight/blob/HEAD/hindsight-docs/blog/2026-08-05-open-source-agent-memory-systems.md
- Mem0 vs Letta vs Zep vs Mengram comparison: https://github.com/alibaizhanov/mengram/blob/HEAD/blog/03-mem0-vs-letta-vs-zep-vs-mengram.md
- LangGraph beads-memory competitive brief (2026-07): https://github.com/masterkidan/langgraph-beads-memory/blob/HEAD/docs/superpowers/specs/2026-07-31-beads-memory-competitive-brief.md
- Cognee 1.0 Postgres writeup: https://github.com/philipcoller-777/cognee
- Multi-agent orchestration research (ob-1, 2026-09): https://github.com/overbrilliant/ob-1/blob/HEAD/docs/research/multi-agent-orchestration.md
- Agent memory solution survey (ai-asset-registry, 2026-05): https://github.com/solaius/ai-asset-registry/blob/HEAD/agent-memory/research/02-solution-survey.md
- Multi-agent architecture patterns (DZone, 2026-09): https://dzone.com/articles/multi-agent-systems-architecture-patterns
