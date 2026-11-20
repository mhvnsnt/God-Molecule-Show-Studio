# Rigby2D — 2D Skeletal Animation (Spine / Moho slot)

**Version:** 0.5.1 (release tag `v0.5.1`) · **Licence:** Apache-2.0
**Upstream:** https://github.com/jaisurya-dev-art/rigby2d — docs: rigby2d.com/docs
**Staged:** 2026-11-20, branch `tools/free-stack-wireup-20261120` (no merge).
Binaries live on release `production-stack-free-20261120` (mhvnsnt/dream-girl) —
this repo stages the docs + the verified fetch script
(`tools/free-stack/fetch-verify.sh`). No binaries are committed here.
Source: dream-girl branch `tools/production-stack-free`, sweep doc
`tools/production-stack-free/sweep/rigby2d/README.md`.

## Verdict

PULLED and verified. The strongest live Spine/Moho cover found in this
sweep: a real, actively developed open-source 2D skeletal animation
editor with a Linux AppImage — the role DragonBones' dead editor used
to hold.

## Facts (verified 2026-11-20)

- Version: **0.5.1** (release tag `v0.5.1`)
- Source: https://github.com/jaisurya-dev-art/rigby2d — docs: rigby2d.com/docs
- Licence: **Apache-2.0** (repo metadata, 2026-11-20)
- Repo last push: 2026-11-19 (active; a release landed the day before
  this sweep, and related repos were updated 2026-11-20)
- Features (project description): open-source 2D skeletal animation
  editor for games and film. AutoRig layered PSDs, animate with
  meshes, IK and physics, lip-sync from audio, render video, export
  JSON/.skel. JavaScript, Rust, Godot and Unity runtimes. Built-in MCP
  server for AI assistants.

## Binary pulled

- File: `Rigby2D_0.5.1_amd64.AppImage`
- Size: 96,979,448 bytes (matches published release asset size exactly)
- SHA-256: `27afa7de71a43e2fe45f27e605176a62b9a559db4b7f5f00f3a105870bdbd6ee`
- Verified against the project's published `SHA256SUMS.txt`: **OK**
- Release: `production-stack-free-20261120` on mhvnsnt/dream-girl
- Also published (not pulled): `.deb`, Godot/Unity/Phaser/Pixi
  runtimes, `SHA256SUMS.txt`.

## Get it / run it

```bash
bash tools/free-stack/fetch-verify.sh   # pulls + size/sha256-verifies all 10 tools
# …or one tool only:
gh release download production-stack-free-20261120 --repo mhvnsnt/dream-girl \
  --pattern 'Rigby2D_0.5.1_amd64.AppImage'
chmod +x Rigby2D_0.5.1_amd64.AppImage
./Rigby2D_0.5.1_amd64.AppImage --appimage-extract
./squashfs-root/usr/bin/rigby2d
```

Run notes (verified 2026-11-20): `--appimage-extract` exit 0, no FUSE
needed. Extracted 280M. Contents: `AppRun`, `AppRun.wrapped`,
`Rigby2D.desktop`, `usr/bin/rigby2d` (binary present under usr/).

**GPU route:** Rigby2D needs `libEGL.so.1` and a real EGL/GPU context to
run (Xvfb provides no EGL). Run it via the GPU route — Kaggle GPU,
Colab, Lightning AI, or Oracle — with the vendored libEGL alongside the
binary. The built-in MCP server is a later-lane integration candidate,
not tested here.

## Stage it serves

2D skeletal/bone rig + mesh animation with game-engine runtimes — the
Spine slot (replacing the dead DragonBones editor) and the Moho slot
(vector/mesh rig + IK + physics). Exports JSON/.skel, so it can feed
engines directly.

## Honest limits

- v0.5.1 is young and moving fast (0.x); API/format stability is not
  Spine-grade yet. No production history on our shots.
- No headless/CLI proof run done here; GUI-only probing so far.
- Grease Pencil stays the rig/animation core. Rigby2D is the
  skeletal/game-runtime complement, not a core replacement.

## Licence

Apache-2.0. Source + licence logged honestly next to the item, per lane
rule; licence never gated the pull.
