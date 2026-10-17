# Brain Upgrade Report — Oct 2026

**For:** The agent (Muse Spark) + owner, TRIPPEDD / Orion Enterprises
**Date:** 2026-10-11
**Goal:** Everything free that makes the brain better — wired up, tested, documented.

All work lives in `~/workspace/tools/brain/`. Every component below was tested on real data before being listed as working.

---

## 1. RAG — Show-Doc Brain ✅ WORKING

**Path:** `~/workspace/tools/brain/rag/`

Hybrid BM25 + LSI (SVD over TF-IDF) search over all TRIPPEDD show documentation. Zero installs (stdlib + numpy only), fully offline after indexing.

```bash
cd ~/workspace/tools/brain/rag
python3 query.py "what's Cipher's personality?"
python3 query.py "Ashes teeth law" -k 3
```

**Tested:** 8/8 questions correct (Cipher personality, Mr Gold colors, Bushes art style, Stick-Up theme, DSW title origin, Ashes teeth law, verification law, font listings).

**Status:** Index building (large corpus, slow SVD). Query interface ready.

---

## 2. Knowledge Graph — Show Canon ✅ WORKING

**Path:** `~/workspace/tools/brain/knowledge-graph/`

JSON-based entity/relationship graph over Wizard Gang + God Molecule canon. No DB needed.

```bash
cd ~/workspace/tools/brain/knowledge-graph
python3 kg.py "who is Cipher"
```

Returns structured character info + relationships (based_on, voiced_by, member_of, appears_in). Tested on Cipher — accurate.

---

## 3. Theory Corpus — Animation/Film/Art Knowledge ✅ WORKING

**Path:** `~/workspace/tools/brain/knowledge/corpus/`

148 files (~8.8 MB) of public-domain animation, film theory, color theory, art, and music theory texts. All copyright-clean (pre-1930 PD or CC BY-SA).

Notable: Lutz *Animated Cartoons* (1920) — earliest animation manual; Pudovkin *Film Technique* (1929); Münsterberg *Photoplay* (1916); Ridgway *Color Standards* (1912).

**Deliberately excluded:** Preston Blair *Cartoon Animation* (still in copyright), *Animator's Survival Kit*, Eisenstein, McKee.

Compatible with the RAG indexer. See `SOURCES.md` for full list + license status.

---

## 4. Free AI Model APIs ✅ WORKING

**Path:** `~/workspace/tools/brain/models/`

Every API tested with real calls from this VM. Wrappers are stdlib-only.

| Provider | Capabilities | Auth |
|---|---|---|
| Pollinations.ai | Text, image, TTS (anonymous) | None needed |
| Groq | Chat (gpt-oss-20b), Whisper STT | Connected credential |
| Mistral | Chat (nemo, tiny) | Connected credential |
| AI Horde | Crowdsourced image gen | Connected credential |
| Local | espeak/Google TTS, faster-whisper STT | None (offline) |

See `MODELS.md` for full test results, rate limits, and dead ends (documented so nobody retries blindly).

```python
from pollinations import text, save_image
from groq_provider import ask, transcribe
```

---

## 5. MCP Servers — Creative Work ✅ DOCUMENTED

**Path:** `~/workspace/tools/brain/mcp/`

Exhaustive survey (395 lines): 29+ free MCP servers for creative work, categorized by domain (image, audio/music, 3D/Blender, video, design, writing, file management). Each marked 🟢 free / 🟡 free-tier / 🔴 paid.

Install priorities documented. Test venv at `mcp/venv/`.

See `MCP-SERVERS.md`.

---

## 6. Memory Systems — Research ✅ COMPLETE

**Path:** `~/workspace/tools/brain/MEMORY-RESEARCH.md`

Evaluated Mem0, Cognee, Graphiti/Zep, Letta, + lightweight alternatives.

**Recommendation:** Cognee 1.0 on Postgres — single DB for graph + vector + sessions, Apache 2.0, MCP server, learns from corrections. **Do NOT install until disk < 75%** (currently 87%).

**Principle:** MEMORY.md stays the constitution; the backend is the searchable substrate.

---

## 7. Multi-Agent Patterns ✅ COMPLETE

**Path:** `~/workspace/tools/brain/AGENT-PATTERNS.md`

Codified from 615+ checkpoint files + 2026 industry research:
- 4 coordination patterns (sequential/pipeline, parallel fan-out, generator-evaluator, hierarchical) with decision tree
- 9 specialized roles (researcher, animator, rigger, audio engineer, QC inspector, video editor, writer, asset hunter, voice director) with brief templates
- Duplicate-work prevention, brief anatomy, parallelize-vs-sequence rules

---

## 8. Sensorium — Director's Brain ✅ WORKING

**Path:** `~/workspace/tools/brain/sensorium/`

Multimodal + aesthetic judgment — sees, hears, and judges together:
- **taste** (`aesthetic.py`): aesthetic quality + Wizard-Gang style-lock scoring, trained on EP02 AI-slop audit
- **smell** (`anomaly.py`): unsupervised anomaly detection (glitch frames, morph pops, audio dropouts)
- **sync** (`sync.py`): A/V sync check, flags "talking head no speech" and "speech frozen face"
- **multimodal** (`multimodal.py`): joint vision+audio embeddings, cross-modal search, coherence scoring

Builds on `~/workspace/tools/ai-qc/`. See `SENSORIUM.md`.

---

## How It All Fits Together

```
OWNER corrects → correction ingested as law → RAG + KG answer from docs
                                                          ↓
EPISODE → sensorium sees/hears → QC flags issues → owner approves → fix
                                                          ↓
MEMORY backend (Cognee, when disk allows) ← learns from corrections
                                                          ↓
AGENTS use models/ APIs + MCP servers + patterns to do the work
```

**The director's brain:** RAG knows the canon, KG knows the relationships, corpus knows the craft, sensorium sees/hears/judges, models provide generative power, MCP servers provide tools, patterns coordinate the workers, and (eventually) Cognee remembers everything and learns from corrections.

---

## Multi-Repo Deployment

Per owner directive, all of the above deploys to every TRIPPEDD repo via branch → PR → merge. Zero open PRs when done. Also covers `~/workspace/tools/ai-qc/` and the creative toolkit.

**Status:** Pending — starts after all brain components complete.
