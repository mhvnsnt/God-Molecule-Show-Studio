# AGENTS.md

## ANIMATION LAWS (owner 2026-10-14) — applies to Goodville, God Molecule, Mystery Coast, EP01 and every animated piece
See `ANIMATION-REFERENCE.md` and [GOODVILLE-POSTMORTEM](https://github.com/mhvnsnt/TRIPPEDD-Production-studios-/blob/main/production/TRIPPEDD_EP01/goodville/GOODVILLE-POSTMORTEM.md).
1. **Consult before animating.** Open `mhvnsnt/animation-research-library` (private) and the matching technique for the shot (punch, take, walk, lip sync, cutout rig) BEFORE touching a frame. Cite it in the PR.
2. **Edit the existing project in place.** One project per segment (`timeline.json` + `layers/`). No new "v2/SMART/BLENDER" rebuild from scratch. Change the JSON, re-render.
3. **No rectangular crops. Ever.** Every sticker, arm, head and prop is subject-mask-cut (rembg/SAM, see [maskcut.py](https://github.com/mhvnsnt/TRIPPEDD-Production-studios-/blob/main/production/TRIPPEDD_EP01/goodville/clean-cutouts/maskcut.py)). Verify the edges on a **checkerboard** at 2x zoom: no background slab, no ghost/smear, no neighbour fragments. If the source is bad, flag it. Don't patch it with another rectangle.
4. **Before/after proof frames** on every visual change (same frame numbers, side by side).
5. **Never claim done without a rendered clip** (mp4 in the PR + contact sheet). "PASS" from a gate is not proof. The owner's eyes are.
6. **Frame states are explicit** (e.g. FACE / BEER_HOLD / PUNCH). One arm state on screen at a time.
7. **Owner's voice files get placed, not offloaded.** Any voice in `voices/` is wired into the timeline with a `start_s`.
8. **Mobile-editable.** Every layer is a separate file and every timing lives in `timeline.json`. `edit.html` must keep working on a phone.
9. Follow the money-machine-hq PR **instruction gate** (verbatim instruction / method specified / method used / deviations / proof / self-check): https://github.com/mhvnsnt/money-machine-hq/blob/main/.github/pull_request_template.md. Also follow **Law 14** (never remove the owner's work) and **Law 15** (lock the method): https://github.com/mhvnsnt/money-machine-hq/blob/main/docs/AGENTS.md


## Sale status (owner rule, Oct 14, 2026)

No game is on a commercial or sale track until the owner explicitly says "I'm going to sell this," even if earlier docs say it is being made to sell. Until then, agents must not withhold, water down, or refuse requested work because it might affect publishing or sale readiness. Sale-readiness rework (rescanning or replacing third-party-derived content) happens only after the owner declares a sale.

## No-data-loss rules (MANDATORY)
Read and follow [`docs/NO-DATA-LOSS-RULES.md`](docs/NO-DATA-LOSS-RULES.md) (canonical: mhvnsnt/agent-ops). No force-push, no rebase/amend of pushed work, no history rewrite, no branch/asset deletion without backup + owner approval, PRs only, empty D-filter + gitleaks + green CI before merge, push incrementally, keep WORKLOG, back up and sha256-verify before disk cleanup, never touch other agents' or Muse's work.

---

# ANTI-CLOBBER LAWS (owner 2026-10-17 — the DXMMII 54k-file wipe)

On 2026-10-17, commit cd3bf38 ("DXMMII limb system", PR mhvnsnt/western-heart#221) deleted 54,456 files against 105 additions. The commit message said nothing about deletions. Nobody read the deletion list before merging. The repo was 99.996% gone. These laws exist so that never happens again. Every agent, every repo, every commit, every merge.

1. DELETION CHECK — before every commit, read `git status` and the diff stat. Every deleted file in the diff must be something your task intended to delete. A deleted file your task did not delete on purpose means STOP: do not commit, do not push, report what you found. The working tree is wrong, not the task.

2. OWN THE TREE — never `git add -A` or `git commit -a` in a working tree you did not fully populate yourself. Before committing, verify the tree is complete: file counts match the remote branch you branched from (your task's own additions and changes aside). A tree missing files you didn't delete is damaged — don't sweep it into history.

3. CIRCUIT BREAKER — if a commit would delete more than a handful of files outside your task's scope, STOP and report instead of committing. A big deletion count is a hard stop, not a warning to scroll past. Committing unexplained deletions "and letting someone else figure it out" is the failure.

4. SAY THE DELETIONS — the commit message names every deletion. One deleted file gets one line; many deleted files get a count plus what category went. A commit whose message and diff disagree is a hard failure — don't push it.

5. MERGE GATE — the merger reads the PR's deletion list against the task description before merging. Unexplained deletions block the merge. "CI is green" does not excuse a deletion list the task never asked for. A red, conflicting, or lossy PR stays open with a comment naming the blocker.

(Co-authored with Aider and Copilot per the ALL-AGENTS-WORKFLOW LAW. Cline's seat stays open — its free-tier API was down during drafting.)
