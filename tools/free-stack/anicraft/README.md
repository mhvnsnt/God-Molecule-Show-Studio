# AniCraft — Clean-Room Adobe Animate (Rust)

**Version:** 0.2.1 (release tag `v0.2.1`) · **Licence:** Apache-2.0
**Upstream:** https://github.com/storytold/anicraft
**Staged:** 2026-11-20, branch `tools/free-stack-wireup-20261120` (no merge).
Binaries live on release `production-stack-free-20261120` (mhvnsnt/dream-girl) —
this repo stages the docs + the verified fetch script
(`tools/free-stack/fetch-verify.sh`). No binaries are committed here.
Source: dream-girl branch `tools/production-stack-free`, sweep doc
`tools/production-stack-free/sweep/anicraft/README.md`.

## Verdict

PULLED and verified. The decomp/recomp find of this sweep: a clean-room,
open-source 2D animation editor written from scratch in pure Rust,
file-compatible with Adobe Animate (XFL/FLA, SWF) per the project
description. This is the closest thing in the sweep to a free
reimplementation of a paid animation tool — and it is real, released, and
runnable on Linux.

## Facts (verified 2026-11-20)

- Version: **0.2.1** (release tag `v0.2.1`)
- Source: https://github.com/storytold/anicraft
- Licence: **Apache-2.0** (repo metadata, 2026-11-20)
- Repo last push: 2026-11-20 (active — pushed the same day as this sweep)
- Note: a second repo of the same name, `soof-golan/anicraft`, describes
  itself as "file-compatible with Adobe Animate (XFL/FLA, SWF)" but has
  NO releases; the `storytold/anicraft` repo is the one shipping builds.

## Binary pulled

- File: `anicraft-0.2.1-linux-x86_64.AppImage`
- Size: 19,024,376 bytes (matches published release asset size exactly)
- SHA-256: `352456384d1e82f373d836dcbcd9f1473b1603c5c9c7b185d763218470091b31`
- Verified against the project's published `SHA256SUMS.txt`: **OK**
- Release: `production-stack-free-20261120` on mhvnsnt/dream-girl
  (asset listed with size 19024376)

## Get it / run it

```bash
bash tools/free-stack/fetch-verify.sh   # pulls + size/sha256-verifies all 10 tools
# …or one tool only:
gh release download production-stack-free-20261120 --repo mhvnsnt/dream-girl \
  --pattern 'anicraft-0.2.1-linux-x86_64.AppImage'
chmod +x anicraft-0.2.1-linux-x86_64.AppImage
./anicraft-0.2.1-linux-x86_64.AppImage --appimage-extract
./squashfs-root/AppRun
```

Run notes (verified 2026-11-20): `--appimage-extract` exit 0, no FUSE
needed. Extracted 44M. Contents: `AppRun`,
`ai.storyteller.anicraft.desktop`, `usr/bin/anicraft`,
`usr/bin/anicraft-cli`. The `anicraft-cli` binary is the headless path:
`anicraft-cli render --sample` exits 0 and renders a real 1280x720 PNG.
For GUI use, the CLI is the working path where `libxkbcommon-x11.so` is
missing (apt broken on that box) — the CLI does not need it.

## Stage it serves

2D vector/raster animation authoring — the Adobe Animate slot. Candidate
for Animate-format (XFL/FLA) interchange; NOT a Grease Pencil core
replacement. Grease Pencil stays the rig/animation core.

## Honest limits

- v0.2.1 is early (0.x). No production history on our shots yet.
- FLA compatibility is claimed by the sibling fork's description, not
  yet proven by us against a real .fla — a follow-up lane must test it.
- No Windows/macOS testing done here (Linux AppImage only).

## Licence

Apache-2.0. Source + licence logged honestly next to the item, per lane
rule; licence never gated the pull.
