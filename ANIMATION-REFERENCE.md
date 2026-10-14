# Animation reference: use it before you animate

**Library:** [`mhvnsnt/animation-research-library`](https://github.com/mhvnsnt/animation-research-library) (private). It's legal-only:
- public-domain cartoons (Fleischer, Popeye, PD Looney Tunes) from the Internet Archive
- Blender Studio open-movie production files (CC-BY: boards, animatics, rigs, scenes)
- Pepper&Carrot source art
- technique breakdowns sorted by production stage: script → boards → animatic → model sheet → rig → scene → final

**How agents use it here**
1. Find the shot type (punch, take, walk, lip sync, cutout rig, smear) in the library's technique index. Read it and cite it in the PR.
2. Pull pieces from this repo's kits, mask-cut them (no rectangles), and check them on a checkerboard.
3. Edit the segment's existing `timeline.json` and layers in place, then render.
4. Ship before/after frames and the rendered clip. Done means a clip exists.

**Rules:** this repo's `AGENTS.md` → "ANIMATION LAWS", plus the money-machine-hq [instruction gate](https://github.com/mhvnsnt/money-machine-hq/blob/main/.github/pull_request_template.md) and [Laws 14 & 15](https://github.com/mhvnsnt/money-machine-hq/blob/main/docs/AGENTS.md).

**Worked example:** `https://github.com/mhvnsnt/TRIPPEDD-Production-studios-/tree/main/production/TRIPPEDD_EP01/goodville/segment-dino-story` (layered, mobile-editable, voice synced) and [GOODVILLE-POSTMORTEM.md](https://github.com/mhvnsnt/TRIPPEDD-Production-studios-/blob/main/production/TRIPPEDD_EP01/goodville/GOODVILLE-POSTMORTEM.md).
