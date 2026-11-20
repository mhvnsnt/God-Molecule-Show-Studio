# Harmony Equivalents — Comparison

Free Toon Boom Harmony-class tools, pulled full and verified 2026-11-20
(lane `harmony-equivalents`, owner order 2026-11-20 ~12:08 EST).
Release: `harmony-equivalents-20261120` on mhvnsnt/dream-girl.
Staged here on branch `tools/free-stack-wireup-20261120` (no merge) —
binaries live on the release; this repo stages the docs + the verified
fetch script (`tools/free-stack/fetch-verify.sh`).
Source: dream-girl branch `tools/harmony-equivalents`.

## What Harmony does (the bar)

Toon Boom Harmony is the paid studio standard for 2D animation: vector +
bitmap drawing, cut-out rigging with deformers and inverse kinematics,
traditional frame-by-frame, a node-based compositing view, multiplane
camera, lip sync, effects, and clean export. No single free tool covers
all of it. The free stack composes instead — each tool below covers a
slice, and Tahoma2D (already wired) is the spine.

## Already wired — NOT re-pulled here

| Tool | Version | Where it lives | Role |
|---|---|---|---|
| **Tahoma2D** | 1.6.3 | dream-girl main `tools/tahoma2d/` + binary in release `toolchain-dcc-v1` (`Tahoma2D-linux-clang.tar.gz`, 328,382,822 B) | **Best overall Harmony equivalent in the stack.** Toonz/Ghibli lineage: Xsheet, onion skin, pegs, cameras, effects, headless renderer, bundled Rhubarb lip sync + ffmpeg. Drawing + production + compositing. |
| OpenToonz | 1.8.0 | Docs only, cape-jones PR #165 (`production/tools/opentoonz/README.md`) | Node-based compositing (Schematic/Fx room) — closest free equivalent to Harmony's compositing. Upstream ships NO Linux binary (Flatpak `io.github.OpenToonz` is the route); Tahoma2D carries the role. |
| Pencil2D | 0.7.2 | Release `production-stack-free-20261120` | Frame-by-frame bitmap+vector drawing, onion skin. Beginner drawing seat. |
| AniCraft | 0.2.1 | Release `production-stack-free-20261120` | Flash-style vector animation (Rust, early alpha): shape tweens, Bone tool, camera layer. |
| Rigby2D | 0.5.1 | Release `production-stack-free-20261120` | 2D rigging. |
| Kdenlive / Olive | 26.08.3 / nightly | Release `production-stack-free-20261120` | Video editing / compositing finish. |
| Douga | build 1116 | Release `production-stack-free-20261120` | Line-test / in-between helper (Windows build). |

## Landed in this lane (full binaries on `harmony-equivalents-20261120`)

| Tool | Version | Licence | Asset | Size | SHA-256 | Harmony slice it covers |
|---|---|---|---|---|---|---|
| **Synfig Studio** | 1.5.5 (2026-03-16) | GPLv2+ | `SynfigStudio-1.5.5-linux64.appimage` | 115,539,968 | `b85aabc26f690a0c150d2143c656c17f358b73abbedf8d01007f15a7a95740e9` (matches upstream checksum) | **Rigging + auto-tweening** — bone/skeleton rigs, IK, shape morphing, 50+ layers. Closest free Harmony-class rigging tool. |
| **Enve** | continuous-linux, commit `d919d4d` (2021-06-22) | GPL-3.0 | `enve.AppImage` (upstream `enve-d919d4d-9_25_22-x86_64.AppImage`) | 150,658,760 | `00b7081f0dfb8545c6eee31034407305cf63c630a002bd391fa1504eab01b1c0` (observed; no upstream checksum published) | Vector animation + rigging, effects, expandable/plugin architecture. **Stale upstream (last push 2022-09-25)** — spare seat, not the live pick. |
| **Wick Editor** | 1.19.0 pre-release (2020-12-11) | GPL-3.0 | `Wick.Editor-1.19.0.AppImage` (upstream `Linux_Wick.Editor-1.19.0.AppImage`) | 216,087,317 | `92ff24c6f162e0144108d6dd47bf5f6d6ca6972d405c21b73c6da3a7d35f059b` (observed; no upstream checksum published) | Flash-style vector drawing + timeline + symbols + motion tweens + **in-editor JavaScript (games/interactive)**. **Desktop builds stale since 2020** (web editor + forum live). |
| **Glaxnimate** | 0.6.0 (KDE, Mar 2026) — release-branch CI AppImage, GitLab job 5052031694 | GPL-3.0-or-later | `glaxnimate-x86_64.AppImage` | 182,682,816 | `e0f39cf67b79e80cdbbe8b3d858cab8a7b142e1c17f5944eb09af55fbc4a6347` (observed; no upstream checksum published) | Vector motion design, Lottie/SVG, keyframe animation, Python scripting. **Not character rigging** — motion-graphics seat. |

## Doc-only (honest gaps — no binary landed)

| Tool | Why no binary | Next step |
|---|---|---|
| Animation Paper v5.0 Beta 3 | Free beta for Linux x86_64/ARM64 exists, but the download page exposes no direct URL (JS buttons); none found by search. | Browser lane clicks through and captures the file URL. |
| TupiTube Desk 0.2.22 | No GitHub releases; official download is form-gated at maefloresta.com. Beginner-grade, 2020-stale. | Browser lane (low priority) — only if cheap; form-only = close as form-gated. |

## Skipped (per brief, not chased)

ToonSquid (iPad-only), RoughAnimator / Callipeg (paid — never a purchase
list), FlipaClip (mobile-only). Established honest negative (not chased
again): NO Harmony / TVPaint / Moho / Spine decomp or recomp exists.

## Verdict — which is the best Harmony equivalent?

**Overall: Tahoma2D 1.6.3 — already wired, still the best.**
Full production tool (drawing, Xsheet, pegs, cameras, effects, headless
render) from the Toonz/Ghibli lineage. Nothing newly pulled beats it as a
single Harmony stand-in.

**Best NEW pull: Synfig Studio 1.5.5.** It is the one thing Tahoma2D does
not do natively at the same depth: bone-rigged cut-out characters with
automatic vector tweening. For the show's needs (rig a character, pose
keys, let the tweener do the in-betweens), Synfig is the gap-closer, and it
is actively maintained (2026 release).

**Best for motion graphics / Lottie: Glaxnimate 0.6.0.** Vector motion
design, Lottie + animated SVG export, Kdenlive integration. Not a
character-rigging tool — use it for titles, UI motion, and web/app
animation.

**Stack that covers Harmony:** Tahoma2D (draw/produce/composite) +
Synfig (rig/tween) + Glaxnimate (motion graphics/Lottie) + Wick
(Flash-style quick cartoons + interactive) + Pencil2D (frame-by-frame
drawing) + Kdenlive/Olive (edit/finish). Enve stays as a spare
vector/rigging seat; Animation Paper joins the rough/line-test stage once
its binary lands.

## How to use

Each tool has its own README under `tools/harmony/<tool>/` with version,
licence, landed size/SHA-256, install/run steps (including the
no-FUSE `--appimage-extract` route), and its Harmony
comparison table. Binaries live on release `harmony-equivalents-20261120`
— pull them with `tools/free-stack/fetch-verify.sh` (size + SHA-256
checked, no re-download of already-verified binaries), then run.

## Licence note

Licence never gated a pull — every item's licence and source are logged
honestly next to it. GPLv2+ (Synfig), GPL-3.0 (Enve, Wick),
GPL-3.0-or-later (Glaxnimate), proprietary-free-beta (Animation Paper),
GPL-2.0-or-later (TupiTube), Modified BSD (OpenToonz), BSD/GPL mix
(Tahoma2D lineage).
