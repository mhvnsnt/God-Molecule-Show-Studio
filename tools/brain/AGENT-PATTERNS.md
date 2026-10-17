# Multi-Agent Patterns for Creative Production — Oct 2026

**For:** Muse Spark operation (parent agent = orchestrator/supervisor; workers = subagents, depth 2).
**Date:** 2026-10-10

This document codifies how this operation actually runs multi-agent work — grounded in
`~/workspace/agent-ops/` (CHECKPOINT_PROTOCOL.md, IDEMPOTENCY.md, RESUME_BRIEF_TEMPLATE.md, 615+ checkpoint files)
and the standing laws in `~/AGENTS.md` — plus industry patterns (2026 research) that map onto our real setup.

**One-line model:** The parent is the *supervisor*: it decomposes, briefs, and integrates. Workers are *specialists*
with narrow lanes, checkpointed state, and verifiable outputs. This is the industry's dominant production topology
(orchestrator-worker) — it just runs here with hand-written briefs and JSON checkpoints instead of a framework.

---

## 1. Coordination patterns (when to use which)

### Pattern A: Sequential pipeline — default for creative work
`Research → brief → generate → QC → fix → deliver.` Each stage consumes the previous output, one agent at a time.

- **Use when:** order matters, each step has a clear contract, quality gates are the point.
- **Examples here:** character render pipeline (pose → render → QC inspection → fix); font pipeline (specimen → owner approval → commercial); voice (clone test → owner listens → decision).
- **Strength:** 0% coordination failures — workers can't conflict because they never overlap. Auditable: the checkpoint chain is the paper trail.
- **Failure mode:** the telephone game — errors compound down the chain; each handoff degrades context. Fix: pass *artifacts* (files, frames), never summaries-of-summaries, between stages. (This is the lesson of the Luck-of-the-Irish incident: "contents, not filenames.")

### Pattern B: Parallel fan-out / fan-in — for independent shards
Spawn N workers on independent, non-overlapping slices, then merge.

- **Use when:** work divides cleanly and slices don't touch each other (per-character renders, per-font commercials, per-episode research waves).
- **Rule:** slices must be defined by the *parent* up front (character list, episode list, file manifest). Never let workers self-assign slices — that's how duplicate work happens.
- **Merge step is mandatory:** one agent (parent or a merge worker) integrates results. Fan-out without a named merger = 615 checkpoints and nobody knowing what's done.
- **Failure mode:** two workers writing the same path after a restart. Fix: per-task scratch dirs + done-manifests (IDEMPOTENCY.md rules 1, 2, 5).

### Pattern C: Generator-evaluator loop — for quality-critical output
Generator produces, independent evaluator critiques against a checklist, generator fixes, repeat until pass.

- **Use when:** quality >> cost, and the check is mechanizable (QC inspector role below).
- **Cost note:** industry data puts reflexive loops at ~2.3× baseline cost. Use sparingly: renders, final cuts, published artifacts — not drafts.
- **Our version:** the deliverable verification law ("a worker's 'verified' is a CLAIM, not a fact") is a manual generator-evaluator loop with the owner/parent as evaluator. The upgrade is an automated QC worker with defect checklists.

### Pattern D: Hierarchical (supervisor of supervisors)
For large builds: parent → lane leads → workers.

- **Use when:** a build has distinct lanes (e.g., WG EP02: voice lane, visual lane, music lane) each too big for one worker.
- **Our evidence:** this is how the EP02 pipeline actually ran (pose extraction / EbSynth / Kaggle notebook / repair crew / music mapping as separate tracked lanes). It works, but coordination overhead rises — lane leads must own checkpoints, not just vibes.
- **Cap depth at 3** (we're at depth 2/2 max for subagents — lane leads are just workers with a merge brief).

### What NOT to use
- **Peer-to-peer / swarm:** no boss, agents negotiate. Undebuggable at 2 a.m.; no place for "one throat to choke." Rejected for production work.
- **Handoff chains without the supervisor in the loop:** context degrades at every handoff and nobody owns the outcome. Our model keeps the parent as the integration point.

### Decision tree (adapted from industry, tuned for us)
```
Is the sequence of steps known in advance?
  Yes -> Sequential pipeline (Pattern A) — most reliable, our default
  No  -> Can the task be split into independent slices defined UP FRONT?
           Yes, fixed count -> Parallel fan-out + named merger (Pattern B)
           Yes, dynamic     -> Parent supervises workers on demand (orchestrator-worker)
           No               -> Single worker with good tools (don't multiply agents)
Is the output quality-verifiable by checklist?
  Yes -> Add a QC evaluator loop (Pattern C) on the final artifact
Is the build bigger than ~3 workers?
  Yes -> Group into lanes with lane leads (Pattern D), cap depth at 3
```

---

## 2. Specialized subagent roles for creative work

Each role: **job** (what it does), **brief template** (what the parent must include), **tools** (what it needs),
**verification** (how the parent checks its output — worker claims are never trusted on sight).

### 2.1 Researcher
- **Job:** Gather facts, comps, references, technique surveys. Writes a research doc (markdown) into the right repo's `docs/`.
- **Brief template:** topic + scope boundaries (what's in/out) + source bar (primary sources, no inventing) + output path + "branch → PR → merge, 0 open PRs" + checkpoint id.
- **Tools:** browser.search, browser.open, file read/write, git.
- **Verification:** spot-check 3+ sources yourself; check the doc exists at the path; confirm PR merged, not just opened. (Real example: `ad-research.json` — research doc delivered to 4 repos via PRs.)

### 2.2 Animator / Render worker
- **Job:** Generate or repair character renders / animation frames / motion clips in the show's locked art style.
- **Brief template:** character + attire + pose spec + **art style lock** (which show bible, style refs paths) + framing law (full arm reach, T-pose rules) + output paths + white-void version requirement + checkpoint id.
- **Tools:** media.generate image/video, file read, blender/rig tools, git.
- **Verification:** **Parent opens every image itself** (deliverable verification law). Limb-by-limb check: each arm/leg segment, joints, hands, feet, left/right symmetry, feet above ground plane, facing matches movement. For video: sample frames across the whole timeline + automated pose checks (MediaPipe). Worker must attach proof: which frames checked, per-shot checklist.

### 2.3 Rigger
- **Job:** Rig repair, weight painting, viseme/mouth packs on GLBs.
- **Brief template:** GLB path + diagnosis first (`diagnose_rig.py` — diagnose-before-repair law) + repair plan addressing what the diagnosis found + no-repair-without-diagnosis + checkpoint id.
- **Tools:** Blender headless, rig-repair tooling, file read/write, git.
- **Verification:** run the diagnostic suite again after repair; diff rest-pose angles; render turntable frames and inspect. Never accept "weights fixed" without the numbers.

### 2.4 Audio engineer
- **Job:** Voice cloning tests, dialogue placement, BGM mapping, final mix prep.
- **Brief template:** source audio refs + line list + output format (WAV/MP3) + loudness/normalization spec + delivery path (Messenger vs link — per audio/video delivery laws) + checkpoint id.
- **Tools:** tts/voice-clone pipeline, ffmpeg, file read.
- **Verification:** confirm duration AND audible non-silent levels programmatically; confirm it plays through the *actual delivery path* (in-chat attachments show 0:00 on the owner's phone — the incident that created the law). Voice samples: also delivered via Messenger to Mars Fmmg, MP3, labeled.

### 2.5 QC inspector (the evaluator in Pattern C)
- **Job:** Independent verification pass over another worker's deliverable against a defect checklist. Never the same worker that made it.
- **Brief template:** artifact paths + defect checklist (feet/facing/clipping/likeness/audio levels/format) + "report defects with frame numbers/file:line, do not fix" + checkpoint id.
- **Tools:** file/image read, ffprobe, frame extraction, MediaPipe or equivalent.
- **Verification:** the inspector's report must include evidence (frame numbers, crops, measurements). A QC report that says "looks good" with no evidence gets sent back — same as the generator's "verified."

### 2.6 Video editor / assembler
- **Job:** Cut assembly: ffmpeg timelines, segment ordering, slate gaps, export.
- **Brief template:** segment order doc (locked) + source clip paths + export spec (codec/res/fps) + cut-notes path + checkpoint id.
- **Tools:** ffmpeg, ffprobe, file read/write.
- **Verification:** ffprobe the output (duration, streams); pull frames at segment boundaries and confirm order matches the locked doc; watch the full cut once (frames across whole timeline, not the first 10 seconds).

### 2.7 Writer / show-bible worker
- **Job:** Show bibles, episode skeletons, premise banks, dialogue — under style locks and canon.
- **Brief template:** canon sources (which bible is #1 — e.g., God Molecule hierarchy A>B>C) + style lock + what's decided vs open + "nothing invented" (no new canon, names, factions without owner say-so) + output path + checkpoint id.
- **Tools:** file read/write, memory search.
- **Verification:** diff claims against the cited bible; check for invented proper nouns (the recurring failure mode). Owner reads before voice/boards — draft status is explicit.

### 2.8 Asset hunter / archivist
- **Job:** Find footage/assets across Drive, repos, chat uploads, B2; build evidence-based asset maps; salvage content into repos/cloud ASAP (salvage law).
- **Brief template:** what to find + everywhere to look (branches, history, Drive, artifacts) + "contents not filenames — extract frames, map against shots" (the structural fix from the Luck-of-the-Irish correction) + destination repo/path + checkpoint id.
- **Tools:** git (all branches + history), Drive/B2 CLIs, ffmpeg frame extraction, file read.
- **Verification:** parent opens the asset map and at least one claimed asset; confirm byte counts/hashes for anything "verified."

### 2.9 Voice director (casting lane)
- **Job:** Run voice tests: generate test lines per candidate voice, package for the owner to hear and decide.
- **Brief template:** character + reference voice + 3 test lines (short, character-revealing) + delivery (Messenger MP3 per audio law) + "owner decides, worker never picks" + checkpoint id.
- **Tools:** voice-clone pipeline, messenger send.
- **Verification:** files exist, playable, correct lines; sent via the proven path. The owner is the only evaluator — no worker substitutes its taste.

---

## 3. Brief anatomy (every worker brief must contain)

From the checkpoint laws + resume template + real failures, the non-negotiable brief fields:

1. **Checkpoint:** parent writes `checkpoints/<name>.json` via `ckpt.sh` *before* spawn (parent-side checkpoint law). Brief says: "heartbeat this checkpoint, don't create it."
2. **One-line goal** — what "done" looks like, measurable.
3. **Lane boundaries** — what this worker owns and what it must NOT touch (paths, repos, branches). Prevents duplicate work and collisions.
4. **Art/style locks** — which bible/style applies; reference paths.
5. **Output contract** — exact paths, naming (deterministic from inputs), formats.
6. **Verification it must self-run** — the checklist it must complete and *attach evidence for*.
7. **Git discipline** — branch name, incremental commits, branch → PR → merge, never force-push, 0 open PRs, push (don't ask).
8. **Resume behavior** — read checkpoint → RESUME_BRIEF_TEMPLATE.md → IDEMPOTENCY.md → verify → continue. Never redo completed steps without verifying they're missing.
9. **Final report format** — what was done, proof (frames checked, files, hashes, PR links), what remains, blockers.

What kills workers, from the record:
- **No checkpoint before first write** → restart = total loss (parent-side law exists because of this).
- **Filenames as conclusions** → worker reports "found X" from a filename; contents say otherwise.
- **"Verified" with no evidence** → sent back, not forwarded.
- **Shared scratch paths** → two workers corrupt each other after restart reshuffling.
- **Re-push/re-send without verifying** → duplicates, double-posts, double charges.

---

## 4. Avoiding duplicate work

1. **One owner per slice.** The parent assigns slices; workers never self-assign. Slice = character, episode, file manifest, or path prefix.
2. **Done-manifests are machine truth.** For any loop over N items, `~/workspace/<task>/done.json` lists completed items; the worker checks it before each item and appends *after* outputs are written and verified. The checkpoint's `steps_completed` is the human summary.
3. **Deterministic output names** keyed by input (`judas-classic.webp` from `JUDAS_classic.glb`). A re-run produces the same filename; existing valid output = skip.
4. **Write temp, then move.** Never write final paths directly; stale `.tmp-*` files are cleaned on resume.
5. **Verify before redoing.** If a checkpoint claims a step is done, `ls` the outputs / `git log` — don't trust, don't redo blindly. If outputs are missing, the step is NOT done.
6. **Record-then-act for irreversible steps** (push, publish, send, delete): check precondition → act → record in checkpoint AND manifest immediately.
7. **Decisions live in the checkpoint** (`checkpoint.sh decide`), not chat — chat doesn't survive a restart.
8. **The watchdog cron** (every ~15 min) auto-resumes stale checkpoints — but only what was checkpointed. No checkpoint = no resurrection.

## 5. Checkpoint protocol (summary — full spec in agent-ops)

- Worker: `init` first (or heartbeat the parent-written one), `beat` every ≤10 min, `step` per completed unit, `next` on plan change, `decide` on binding decisions, `status completed|failed|stalled` at end.
- Re-spawned worker reads: checkpoint → RESUME_BRIEF_TEMPLATE.md → IDEMPOTENCY.md → verifies → continues. Reports: done-before-restart / done-after-resume / remaining.
- Schema: `task_id, agent_id, repo, branch, goal, status, spawned_at, last_heartbeat, steps_completed, next_steps, key_paths, decisions, blockers, resume_prompt`.

## 6. Parallelize vs sequence — quick rules

- **Parallelize** when: slices are independent AND defined up front AND the merge step has a named owner. (Per-character renders, per-font packs, research waves.)
- **Sequence** when: each stage's input is the previous stage's output, or a quality gate stands between stages. (Stills → owner approval → animation; specimen → approval → commercial.)
- **Never parallelize** what shares a file, a repo branch's merge base, a GPU, or the owner's attention (two voice tests landing at once = he hears neither).
- **Evaluator loops** run sequential by nature: generate → inspect → fix.
- When in doubt: **sequence first**. Parallel is an optimization, not a default — coordination failures rise with communication complexity (industry data: sequential 0%, parallel ~8%, hierarchical ~12%).

---

## Sources & local references
- Local: `~/workspace/agent-ops/CHECKPOINT_PROTOCOL.md`, `IDEMPOTENCY.md`, `RESUME_BRIEF_TEMPLATE.md`, `checkpoints/` (615 files), `~/AGENTS.md` (standing laws)
- Multi-agent orchestration research: https://github.com/overbrilliant/ob-1/blob/HEAD/docs/research/multi-agent-orchestration.md
- Architecture patterns (DZone, 2026-09): https://dzone.com/articles/multi-agent-systems-architecture-patterns
- Task-coordinator skill (nexus-hub): https://github.com/bendourthe/nexus-hub/blob/HEAD/catalog/skills/orchestration/task-coordinator/SKILL.md
- A2A / supervisor trade-offs: https://www.linkedin.com/pulse/multi-agent-orchestration-supervisor-patterns-a2a-where-sukumar-uveyc
