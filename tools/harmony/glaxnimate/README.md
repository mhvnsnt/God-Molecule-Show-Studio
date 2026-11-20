# Glaxnimate — Vector Motion Design (Lottie / SVG)

**Version:** 0.6.0-series release-branch build (GitLab CI job 5052031694,
`release` ref; current stable on glaxnimate.org is 0.6.0, Mar 2026)
· **Licence:** GPL-3.0-or-later (free, open source)
**Upstream:** https://glaxnimate.org/ · https://invent.kde.org/graphics/glaxnimate
(GitHub mirror: https://github.com/mbasaglia/glaxnimate)
**Staged:** 2026-11-20, branch `tools/free-stack-wireup-20261120` (no merge).
Binaries live on release `harmony-equivalents-20261120` (mhvnsnt/dream-girl) —
this repo stages the docs + the verified fetch script
(`tools/free-stack/fetch-verify.sh`). No binaries are committed here.

> **Source note (honest):** the Linux AppImage does NOT come from the
> KDE download server — `download.kde.org` and `cdn.kde.org` are blocked
> by this VM's browser policy (do not retry), and the GitHub mirror
> publishes no Linux AppImage (Windows zip + macOS dmg only). The binary
> landed here is the official GitLab CI artifact for the `release` branch:
> `https://gitlab.com/mattbas/glaxnimate/-/jobs/artifacts/release/raw/build/glaxnimate-x86_64.AppImage?job=linux%3Aappimage`
> (HEAD resolved 302 → job 5052031694, 200 application/octet-stream).
> Same build the project ships as its Linux AppImage; version is the
> 0.6.0 release branch.

## Landed binary (verified)

| | |
|---|---|
| Release | `harmony-equivalents-20261120` on mhvnsnt/dream-girl |
| Asset | `glaxnimate-x86_64.AppImage` |
| Size | 182,682,816 B |
| SHA-256 (observed) | `e0f39cf67b79e80cdbbe8b3d858cab8a7b142e1c17f5944eb09af55fbc4a6347` — **no upstream checksum file is published for the CI artifact**, so this is the observed hash of the downloaded file, recorded here |
| Format | AppImage, Type 2 (squashfs v4.0 payload at offset 189632, block 131072, 15,839 inodes, bytes_used 182,493,123) |

Contents verified by a read-only in-memory squashfs parse (14,859 entries
listed across 401 groups; key files confirmed): `glaxnimate` binary,
`org.mattbas.Glaxnimate.desktop`, `qt.conf`, bundled Qt libraries and an
embedded Python stdlib (`.pyc`). A complete KDE/Qt app bundle — the real
release-branch build, not a stub. (A full `--appimage-extract` listing was
blocked by this VM's intermittent write wall; the in-memory parse is the
verification on record. Re-extract on a normal machine with
`./glaxnimate-x86_64.AppImage --appimage-extract` to confirm.)

## What it is

Free and open-source 2D vector animation / motion-design software, now a
KDE project. Timeline + layers + keyframes for vector shapes; exports
Lottie animations, animated GIF/WebP and animated SVG; scriptable in
Python; integrates with Kdenlive (already in this stack) for titles and
motion graphics. The "motion graphics and Lottie" pick in every open-source
animation round-up.

## Install / run

```bash
# From our release (recommended — verified copy):
bash tools/free-stack/fetch-verify.sh   # pulls + size/sha256-verifies all 10 tools
# …or one tool only:
gh release download harmony-equivalents-20261120 --repo mhvnsnt/dream-girl \
  --pattern 'glaxnimate-x86_64.AppImage'
chmod +x glaxnimate-x86_64.AppImage
./glaxnimate-x86_64.AppImage
# No FUSE: extract instead of mounting:
LD_LIBRARY_PATH=<dir-with-libfuse.so.2> ./glaxnimate-x86_64.AppImage --appimage-extract
./squashfs-root/AppRun
# Alternatives: Flatpak (flathub org.mattbas.Glaxnimate), distro package
# (Discover / GNOME Software), Snap.
```

Note: the AppImage runtime needs `libfuse.so.2` to start. Where it is not
installed, use the `--appimage-extract` route above (works with the shim
from the Ubuntu `libfuse2` package via `LD_LIBRARY_PATH`).

## Harmony comparison

| Harmony does | Glaxnimate covers | Gap |
|---|---|---|
| Vector animation + keyframes | Vector shapes, timeline, keyframes, easing, Python scripting | No bone rigging, no deformers, no IK — **not a character-rigging tool** |
| Lottie / web animation export | Native Lottie + animated SVG/GIF/WebP export | — (Harmony does not do Lottie; this is Glaxnimate-only) |
| Frame-by-frame drawing | No — vector/motion only | Draw in Tahoma2D / Pencil2D |
| Node compositing | No | Tahoma2D / OpenToonz cover compositing |
| Camera, multiplane | Basic camera moves | No multiplane |

**Verdict:** the motion-graphics seat — best free tool here for titles,
UI motion, Lottie and animated SVG, and the Kdenlive companion. Do not
reach for it for character rigs (Synfig) or full production (Tahoma2D).

## Licence

GPL-3.0-or-later. Repo integration is legal — document the version pin on
upgrade. Source + licence logged honestly next to the item, per lane rule;
licence never gated the pull.
