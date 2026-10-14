<!--
INSTRUCTION GATE: every section below is REQUIRED and checked by CI
(.github/workflows/instruction-gate.yml). Empty / placeholder sections fail the PR.
Why: agents were substituting a faster method than the one the owner named
(e.g. a crop instead of the Smart/Magic Cut he asked for). See AGENTS.md law 15 "Lock the method".
Docs-only PRs that touch only .md files may use the `docs-only` label instead.
-->

## Owner instruction (verbatim quote)
> Paste the owner's exact words. Do not paraphrase.

## Method the owner specified
<!-- The tool / technique / process he named, e.g. "Smart Cut in the existing project file". Write "owner did not specify a method" only if that is literally true. -->

## Method actually used
<!-- Must match the line above. If it differs, list it under Deviations with his approval. -->

## Deviations (none / list, each with owner approval link)
<!-- Write exactly `none`, or one bullet per deviation, each with a link or #ref to where the owner approved it. -->

## Proof (paths to files, frames, test output)
<!-- One bullet per path, in backticks, e.g. - `renders/promo/frame_0120.png`. Every path must exist in this PR's diff or in the repo. -->

## Self-check: I verified the result against the literal instruction
- [ ] I re-read the verbatim instruction above and the result does exactly what it says, using the method it names.
