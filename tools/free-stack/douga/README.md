# Douga — Pen-First Cel Animation with a Real Dope Sheet

**Version:** build 1116, updated 2026-11-17 13:18 UTC · **Licence:** free
(free exports carry a small "made with douga.app" watermark — see below)
**Upstream:** https://douga.app — download page https://keihoag.itch.io/douga (author: keihoag)
**Staged:** 2026-11-20, branch `tools/free-stack-wireup-20261120` (no merge).
Binaries live on release `production-stack-free-20261120` (mhvnsnt/dream-girl) —
this repo stages the docs + the verified fetch script
(`tools/free-stack/fetch-verify.sh`). No binaries are committed here.
Source: dream-girl branch `tools/production-stack-free`, sweep doc
`tools/production-stack-free/sweep/douga/README.md`.

## Verdict

VERIFIED REAL and LANDED. Pen-first cel animation with a real dope sheet —
the TVPaint-adjacent slot for hand-drawn timing work. **Windows 10/11,
64-bit ONLY** — there is no Linux or macOS build.

## Facts (verified 2026-11-20)

- Page: https://keihoag.itch.io/douga (author: keihoag)
- Price: **free · no installer · no account**
- Tagline: "Pen-first cel animation with a real dope sheet."
- Platform: **Windows 10 / 11, 64-bit ONLY** — `douga.exe`, Direct3D 11;
  Wacom / XP-Pen / Huion / Surface Pen. No Linux build, no macOS build.
- Features: pressure-sensitive brush engine (ink, pencil, splatter,
  marker, airbrush; custom `.dbrush` files), stabilizer, perspective/
  grid/symmetry guides, drop a GLB/GLTF/OBJ to trace over, real dope
  sheet (keys, holds, loops, exposure on ones/twos, warm/cool onion
  skin), scenes > cuts > layers, managed palettes (`.dpal`), one `.dga`
  file per project.
- Export: PNG sequence, GIF, APNG, H.264 MP4 with sound, built in.
- Status: beta, one person's program. "It draws, it times, it saves, it
  exports." Vector layers + more of the shooting stage (glow, focus,
  motion blur) are next, not shipped.
- Official site: https://douga.app

## Watermark (honest — do not present Douga as watermark-free)

**Exports from an unlicensed copy carry a small "made with douga.app"
line in the bottom-right corner**; a licence key from douga.app/buy
removes it. The tool itself is free; the watermark-free export is paid.
Log it honestly.

## Binary landed

- Version build 1116, updated 2026-11-17 13:18 UTC. Windows build zip.
- LANDED on Release `production-stack-free-20261120` (mhvnsnt/dream-girl):
  asset `browser-download-20261120T160026.367892390Z-0-douga-windows.zip`,
  3,766,009 B, sha256
  `bf3bd41c5593736caf4b7d74ebcf4c00c52766691c3596f3d3c7b34a9ea0b774`.
- Contents verified: `Douga/douga.exe` 6,263,648 B, `EULA.txt`,
  `lang/en.ini` + `ja.ini`, plugins (effects blur/levels/mosaic/noise/
  sample_invert/smooth, ffmpeg exporter). Zip extracts clean (16 entries).
- Related plugins NOT pulled: `douga-rig-import.zip` 190 kB,
  `brush_convert` 279 kB, `video_import` 83 kB, `update_check` 85 kB,
  `poses` 13 MB.

## Get it

```bash
bash tools/free-stack/fetch-verify.sh   # pulls + size/sha256-verifies all 10 tools
# …or one tool only (Windows):
gh release download production-stack-free-20261120 --repo mhvnsnt/dream-girl \
  --pattern '*douga-windows.zip'
# Unzip on Windows 10/11 64-bit and run Douga/douga.exe. No installer, no account.
```

Run notes: Windows-only, so it is staged for Windows use — it was
verified here by clean zip extraction + file list, not by running it.

## Stage it serves

Pen-first cel animation with a real dope sheet — the TVPaint-adjacent
slot for hand-drawn timing work. Complements Pencil2D (Linux, pulled)
and Tahoma2D (in stack).

## Honest limits

- Windows-only. Beta, single author. Watermark on free exports.
- Grease Pencil stays the rig/animation core.

## Licence

Free (proprietary freeware, one author). Source + licence logged honestly
next to the item, per lane rule; licence never gated the pull.
