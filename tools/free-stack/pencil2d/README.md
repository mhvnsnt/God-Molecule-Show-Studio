# Pencil2D — Hand-Drawn Frame-by-Frame (TVPaint slot)

**Version:** 0.7.2 (release tag `v0.7.2`) · **Licence:** GPL-2.0
**Upstream:** https://github.com/pencil2d/pencil — https://www.pencil2d.org/
**Staged:** 2026-11-20, branch `tools/free-stack-wireup-20261120` (no merge).
Binaries live on release `production-stack-free-20261120` (mhvnsnt/dream-girl) —
this repo stages the docs + the verified fetch script
(`tools/free-stack/fetch-verify.sh`). No binaries are committed here.
Source: dream-girl branch `tools/production-stack-free`, sweep doc
`tools/production-stack-free/sweep/pencil2d/README.md`.

## Verdict

PULLED and verified. The TVPaint-equivalent find of this sweep: a free,
open-source, raster+vector hand-drawn animation tool — the closest free
pen-first frame-by-frame tool not already in the stack. (OpenToonz and
Krita already cover adjacent ground; Pencil2D is the lightweight,
single-purpose traditional-animation option.)

## Facts (verified 2026-11-20)

- Version: **0.7.2** (release tag `v0.7.2`)
- Source: https://github.com/pencil2d/pencil — https://www.pencil2d.org/
- Licence: **GPL-2.0** (repo metadata, 2026-11-20)
- Repo last push: 2026-11-13 (active; a commit was pushed 2026-09-14
  per the project's own record)
- Platforms: Windows, macOS, Linux, FreeBSD
- Features: raster + vector layers in one timeline, bitmap/vector/camera/
  sound layers, onion skinning, direct export to MP4, AVI, animated GIF,
  PNG sequences. No automatic tweening, no skeletal bones — every
  in-between is drawn by hand (by design).

## Binary pulled

- File: `pencil2d-linux-amd64-v0.7.2.AppImage`
- Size: 60,471,800 bytes (matches published release asset size exactly)
- SHA-256: `4034b036258b6a13d4540911ebce085f31ee18a9dacf438845ac71998d42ff91`
- Release: `production-stack-free-20261120` on mhvnsnt/dream-girl
  (asset listed with size 60471800)
- Note: the project publishes no SHA256SUMS file for this release, so
  verification is size-exact + GitHub release provenance, not a
  hash-against-published-sums check (unlike AniCraft/Rigby2D).

## Get it / run it

```bash
bash tools/free-stack/fetch-verify.sh   # pulls + size/sha256-verifies all 10 tools
# …or one tool only:
gh release download production-stack-free-20261120 --repo mhvnsnt/dream-girl \
  --pattern 'pencil2d-linux-amd64-v0.7.2.AppImage'
chmod +x pencil2d-linux-amd64-v0.7.2.AppImage
./pencil2d-linux-amd64-v0.7.2.AppImage --appimage-extract
./squashfs-root/usr/bin/pencil2d --version
```

Run notes (verified 2026-11-20): `--appimage-extract` exit 0, no FUSE
needed. Extracted 154M. Contents: `AppRun`,
`org.pencil2d.Pencil2D.desktop`, `usr/bin/pencil2d`, `qt.conf`.
`--version` exits 0 under xvfb; GUI alive at 25s.

## Stage it serves

Hand-drawn frame-by-frame / cel animation — the TVPaint slot for roughs,
timing tests, and simple hand-drawn cuts. Lightweight complement to
Tahoma2D/OpenToonz, not a replacement for either.

## Honest limits

- No bones, no tweening, no mesh deformation — pure traditional
  frame-by-frame. Anything rigged still goes through Blender Grease
  Pencil / Rigby2D / DragonBones.
- Small volunteer project; 0.7.2 is the current stable, not a
  studio-scale pipeline.
- Grease Pencil stays the rig/animation core.

## Licence

GPL-2.0. Source + licence logged honestly next to the item, per lane
rule; licence never gated the pull.
