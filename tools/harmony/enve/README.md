# Enve — Vector Animation with Rigging

**Version:** continuous-linux build, asset dated 2021-06-22, commit `d919d4d`
(filename `enve-d919d4d-9_25_22-x86_64.AppImage`) · **Licence:** GPL-3.0
(free, open source)
**Upstream:** https://github.com/MaurycyLiebner/enve
**Staged:** 2026-11-20, branch `tools/free-stack-wireup-20261120` (no merge).
Binaries live on release `harmony-equivalents-20261120` (mhvnsnt/dream-girl) —
this repo stages the docs + the verified fetch script
(`tools/free-stack/fetch-verify.sh`). No binaries are committed here.

> **STALE-PROJECT FLAG (honest):** the upstream repo's last push was
> 2022-09-25 and the newest Linux binary is the 2021-06-22 continuous build.
> Enve is effectively unmaintained upstream. It still runs and its vector +
> rigging toolset is real, but do not plan new production on it without an
> eval — Synfig (actively maintained, 1.5.5, 2026) is the live rigging pick.
> The brief's `mavenrain/enve` repo does not exist (404); the real repo is
> `MaurycyLiebner/enve`.

## Landed binary (verified)

| | |
|---|---|
| Release | `harmony-equivalents-20261120` on mhvnsnt/dream-girl |
| Asset | `enve.AppImage` (upstream name `enve-d919d4d-9_25_22-x86_64.AppImage`) |
| Size | 150,658,760 B (matches upstream asset size exactly) |
| SHA-256 (observed) | `00b7081f0dfb8545c6eee31034407305cf63c630a002bd391fa1504eab01b1c0` — **no upstream checksum file is published for the continuous builds**, so this is the observed hash of the downloaded file, recorded here |
| Format | AppImage, Type 2 (squashfs payload, magic `hsqs` at offset 32401) |

Contents verified by `--appimage-extract` (exit 0, 373 MB extracted):
`AppRun`, `io.github.maurycyliebner.enve.desktop` (Name=enve,
Exec=enve, Comment="Create 2D Animations", MimeType=application/vnd.enve-project),
`usr/bin/enve` (16,236,544 B), `qt.conf`, `usr/share/{applications,doc,icons,metainfo,mime}`.

## What it is

Flexible, user-expandable 2D animation software for Linux and Windows:
vector animation with rigging, effects, audio, and a plugin/expandable
architecture. The closest in spirit to a lightweight Harmony for
motion-graphics-style vector scenes with bones.

## Install / run

```bash
# From our release (recommended — verified copy):
bash tools/free-stack/fetch-verify.sh   # pulls + size/sha256-verifies all 10 tools
# …or one tool only:
gh release download harmony-equivalents-20261120 --repo mhvnsnt/dream-girl \
  --pattern 'enve.AppImage'
chmod +x enve.AppImage
./enve.AppImage
# No FUSE: extract instead of mounting:
LD_LIBRARY_PATH=<dir-with-libfuse.so.2> ./enve.AppImage --appimage-extract
./squashfs-root/AppRun
```

Note: the AppImage runtime needs `libfuse.so.2` to start. Where it is not
installed, use the `--appimage-extract` route above (works with the shim
from the Ubuntu `libfuse2` package via `LD_LIBRARY_PATH`).

## Harmony comparison

| Harmony does | Enve covers | Gap |
|---|---|---|
| Vector drawing + rigging | Vector shapes, rigging, keyframe animation, effects | Smaller feature set; no deformer depth of Harmony |
| Frame-by-frame drawing | Weak — vector-first, not a drawing tool | Draw in Tahoma2D / Pencil2D, rig/animate here or in Synfig |
| Node compositing | No node schematic | Tahoma2D / OpenToonz cover compositing |
| Camera, multiplane | Basic camera moves | No multiplane |
| Stability / maintenance | **Stale since 2022** — no upstream fixes coming | Prefer Synfig for anything new; keep Enve as a spare vector/rigging seat |

**Verdict:** a real, working Harmony-class vector/rigging seat, landed and
verified — but superseded as the live pick by Synfig (maintained) and
Tahoma2D (full production tool). Keep for its expandable/plugin architecture
and as a fallback.

## Licence

GPL-3.0. Repo integration is legal — document the version pin on upgrade.
Source + licence logged honestly next to the item, per lane rule; licence
never gated the pull.
