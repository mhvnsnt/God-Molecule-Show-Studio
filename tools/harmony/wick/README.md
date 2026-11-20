# Wick Editor — Flash-Style Vector Animation + Games

**Version:** 1.19.0 (pre-release, 2020-12-11) · **Licence:** GPL-3.0
(free, open source)
**Upstream:** https://www.wickeditor.com/ · https://github.com/Wicklets/wick-editor
**Staged:** 2026-11-20, branch `tools/free-stack-wireup-20261120` (no merge).
Binaries live on release `harmony-equivalents-20261120` (mhvnsnt/dream-girl) —
this repo stages the docs + the verified fetch script
(`tools/free-stack/fetch-verify.sh`). No binaries are committed here.

> **STALE-DESKTOP FLAG (honest):** the newest official DESKTOP release is
> the 1.19.0 pre-release from 2020-12-11 — the desktop Electron builds have
> not been re-cut since, though the web editor at editor.wickeditor.com and
> the community forum stayed active into 2026, and a community fork
> (Candlestick) carries the spirit forward. The 1.19.0 Linux AppImage is
> real and verified below; treat it as a stable-but-old seat, not a live
> project. The brief's `wickeditor/wick-editor` repo does not exist (404);
> the real repo is `Wicklets/wick-editor`.

## Landed binary (verified)

| | |
|---|---|
| Release | `harmony-equivalents-20261120` on mhvnsnt/dream-girl |
| Asset | `Wick.Editor-1.19.0.AppImage` (upstream name `Linux_Wick.Editor-1.19.0.AppImage`) |
| Size | 216,087,317 B (matches upstream asset size exactly) |
| SHA-256 (observed) | `92ff24c6f162e0144108d6dd47bf5f6d6ca6972d405c21b73c6da3a7d35f059b` — **no upstream checksum file is published for this release**, so this is the observed hash of the downloaded file, recorded here |
| Format | AppImage, Type 2 (squashfs v4.0 payload at offset 188392, block 131072, 112 inodes, bytes_used 215,673,152) |

Contents verified by a read-only in-memory squashfs parse (111/111 entries
resolved, 0 unresolved — no FUSE on this VM, so no mount; the parse reads
the superblock, inode table and directory table directly):
root: `.DirIcon`, `AppRun` (2,352 B), `LICENSE.electron.txt`,
`LICENSES.chromium.html`, `chrome-sandbox`, `chrome_100_percent.pak`,
`chrome_200_percent.pak`, `icudtl.dat` (10,426,784 B), `libEGL.so`,
`libGLESv2.so`, `libffmpeg.so`, `locales/` (53 `*.pak` files),
`natives_blob.bin`, `resources/` (`app.asar` 523,476,862 B uncompressed,
`app-update.yml`), `resources.pak`, `snapshot_blob.bin`, `swiftshader/`,
`usr/` (`lib/`, `share/icons/hicolor/.../apps/wick-editor.png`),
`v8_context_snapshot.bin`, `wick-editor` binary (115,543,344 B),
`wick-editor.desktop` (176 B), `wick-editor.png`.
A complete Electron app — the real desktop build, not a stub.

## What it is

A free and open-source tool for creating games, animations and everything
in-between, in the browser or on the desktop — Adobe Flash in spirit:
vector drawing, frame-by-frame animation, symbols, motion tweens, a
timeline, and in-editor JavaScript scripting so clips can be interactive
games. Runs at editor.wickeditor.com with nothing to install; this AppImage
is the offline desktop (Electron) build of the same editor.

## Install / run

```bash
# From our release (recommended — verified copy):
bash tools/free-stack/fetch-verify.sh   # pulls + size/sha256-verifies all 10 tools
# …or one tool only:
gh release download harmony-equivalents-20261120 --repo mhvnsnt/dream-girl \
  --pattern 'Wick.Editor-1.19.0.AppImage'
chmod +x Wick.Editor-1.19.0.AppImage
./Wick.Editor-1.19.0.AppImage
# No FUSE: extract instead of mounting:
LD_LIBRARY_PATH=<dir-with-libfuse.so.2> ./Wick.Editor-1.19.0.AppImage --appimage-extract
./squashfs-root/AppRun
# Or just use the web editor: https://editor.wickeditor.com/
```

Note: the AppImage runtime needs `libfuse.so.2` to start. Where it is not
installed, use the `--appimage-extract` route above (works with the shim
from the Ubuntu `libfuse2` package via `LD_LIBRARY_PATH`).

## Harmony comparison

| Harmony does | Wick covers | Gap |
|---|---|---|
| Vector drawing + timeline | Vector drawing, timeline, symbols, motion tweens | No bone rigging, no deformers, no IK |
| Frame-by-frame | Yes — Flash-style frame-by-frame | No X-sheet / pegs / camera |
| Interactivity / scripting | In-editor JavaScript, games + interactive clips | Nothing like this in Harmony — a Wick-only strength |
| Node compositing | No | Tahoma2D / OpenToonz cover compositing |
| Maintenance | **Desktop builds stale since 2020** (web editor + forum live) | Prefer the web editor or Synfig for anything new |

**Verdict:** the Flash-shaped seat in the stack — best free option for
quick vector cartoons and interactive/game-like clips. Not a Harmony
replacement (no rigging, no compositing, old desktop build), but the only
tool here that does timeline + code, and the most approachable for fast
sketches.

## Licence

GPL-3.0. Repo integration is legal — document the version pin on upgrade.
Source + licence logged honestly next to the item, per lane rule; licence
never gated the pull.
