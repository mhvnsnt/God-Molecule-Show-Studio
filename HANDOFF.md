# HANDOFF — God-Molecule-Show-Studio

**Last updated: 2026-11-22 (America/New_York).**
**Repo:** `mhvnsnt/God-Molecule-Show-Studio` (PUBLIC, ~303 MB), default branch `main`.
**Purpose of this file:** any agent that picks up work here reads this FIRST, then the linked docs. It states what we've done, where we're at, and what we're working toward — so the owner can say "go to this repo, pick up the work" and you just know. Update this file in the same PR whenever the state changes (add, don't delete).

## 1. What this repo is

The God Molecule show studio — "God molecule by TRIPPEDD Production studios". A show repo under the TRIPPEDD umbrella: production work, rigs, animation references, and the tooling around the God Molecule show. (Do not confuse it with `God-molecule-production-stage`, the separate private tooling repo — see §5.)

## 2. Where we're at

### DONE
- **Clobber recovery (2026-10-17):** `recover/god-molecule-clobber-2026` merged — the repo was recovered after a clobber, and the anti-clobber laws landed in `AGENTS.md` the same day.
- **Working method statement (2026-10-27):** `WORKING-METHOD.md` landed.

### IN PROGRESS
- **Open PRs — the Ashes rig repair thread:** #34 (Ashes standard rig: full part-separation repair — braids, hood outer/inner, jaw, neck, bust); #35 (Ashes TURNFIX: real mesh-deform head turn + nod, follow-on to #34). Next step: land #34 first, then #35 — the turn fix builds on the part-separation repair.
- Last push 2026-11-20 (method sync). No new show work recorded since 2026-10-27 beyond the rig PRs.

### BLOCKED
- Nothing recorded as blocked. If the rig repair stalls, the blocker and the route around it must be written down here — not left as a silent gap.

## 3. What we're working toward

The God Molecule show, built to the TRIPPEDD studio standard: rigs that actually turn (real mesh-deform head turn + nod, not a fake), parts properly separated, and every model assembled perfectly like its source or it does not ship. Bar for done: the Ashes rig passes its part-separation repair and turn fix, proven on the real model with his eyes on it.

## 4. Standing rules that apply here

- **Branch → PR → merge, always.** Never push to main directly. Add-only, zero-conflict PRs, no force pushes.
- **Checkpoint-and-save law:** CHECKPOINT.md first, update after every step; the repo is the save; resume, never restart.
- **No-temp-storage law:** nothing in /tmp or any wipeable location, ever. Everything goes straight into the repo or a durable folder the second it exists.
- **Real-source-only:** every part comes from the actual source code and files, wired up fully. No hand-tooled lookalikes, no fake panels.
- **Anti-clobber / no-data-loss:** never wipe or overwrite another lane's work — this repo was already clobbered once (2026-10-17) and recovered.
- **Pre-made parts first:** use existing parts/kits before building anything new.
- **No-gaps / solve-it law:** a gap or block is never the end of the work — route-switch until it's done or every reasonable route is exhausted with exact errors recorded.

## 5. Key files and paths

| What | Where |
|---|---|
| Agent rules (read first) | `AGENTS.md`, `WORKING-METHOD.md`, `ANIMATION-REFERENCE.md` |
| Docs | `docs/`, `production_conversations/` |
| App / source | `src/`, `index.html`, `server.ts`, `package.json` |
| Tooling | `tools/`, `config/`, `infra/`, `ops/` |
| Artifacts | `artifacts/`, `.trippedd_assets/`, `ai-body-replace/` |
| Sister repo (tooling, private) | `mhvnsnt/God-molecule-production-stage` — animation and Blender tooling |

## 6. Open decisions needing the owner

- **Rig repair scope (#34 / #35):** the part list (braids, hood, jaw, neck, bust) and the turn fix are the PRs' scope — if he wants more or less, that's his call, not a lane's.
- **Show direction past the rig:** what the next God Molecule milestone is after the rig passes — his call.

## 7. How to pick up

1. Read this HANDOFF.md first, then `AGENTS.md` and `ANIMATION-REFERENCE.md`.
2. Check the two open rig PRs (#34, then #35) before starting anything — land them in order.
3. Resume from the stated next step — never restart, never re-derive finished work.
4. Land work branch → PR → merge, add-only. Stage finished work to the repo as it lands.
5. Update this HANDOFF.md in the same PR when the state changes. Verify with your own eyes before claiming anything done.
