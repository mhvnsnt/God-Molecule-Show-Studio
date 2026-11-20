# Kdenlive — Primary Free Video Editor (NLE)

**Version:** 26.08.3 (released 2026-11-07; maintenance release of
the 26.08 series, includes an important security fix for manipulated
`.kdenlive` project files — upgrade advised by the project)
· **Licence:** GPL-3.0 (KDE project)
**Upstream:** https://kdenlive.org/ — downloads at
https://download.kde.org/stable/kdenlive/26.08/linux/
**Staged:** 2026-11-20, branch `tools/free-stack-wireup-20261120` (no merge).
Binaries live on release `production-stack-free-20261120` (mhvnsnt/dream-girl) —
this repo stages the docs + the verified fetch script
(`tools/free-stack/fetch-verify.sh`). No binaries are committed here.
Source: dream-girl branch `tools/production-stack-free`, sweep doc
`tools/production-stack-free/sweep/kdenlive/README.md`.

## Verdict

PULLED and verified. The PRIMARY free video editor for the stack:
stable, actively maintained, current release. Olive (see `../olive/`)
is the secondary/alpha editor only.

## Facts (verified 2026-11-20)

- Version: **26.08.3** (released 2026-11-07; maintenance release of
  the 26.08 series, includes an important security fix for manipulated
  `.kdenlive` project files — upgrade advised by the project)
- Source: https://kdenlive.org/ — downloads at
  https://download.kde.org/stable/kdenlive/26.08/linux/
- Licence: **GPL-3.0** (KDE project; GPL per the project's own pages
  and every independent listing checked)
- Platforms: Linux (AppImage / Flatpak — the only two Linux formats
  the Kdenlive team supports), Windows, macOS, BSD
- Features: multi-track non-linear editing, nested sequences,
  multicam, 3-point editing, markers, automatic backups, proxy
  editing, motion tracking, colour correction, video scopes
  (histogram, vectorscope, RGB parade, waveform), subtitling,
  speech-to-subtitles.

## Binary pulled

- File: `kdenlive-26.08.3-x86_64.AppImage`
- Size: 214,346,232 bytes (confirmed by Content-Length from the KDE
  mirror and by the completed download)
- SHA-256: `2c8322edfc86605e4c98a78a019310d9b4fc46bb8e94e6fe313dc7dd987e7671`
  (published by KDE alongside the AppImage; verified locally with
  `sha256sum -c`)
- Release: `production-stack-free-20261120` on mhvnsnt/dream-girl

## Get it / run it

```bash
bash tools/free-stack/fetch-verify.sh   # pulls + size/sha256-verifies all 10 tools
# …or one tool only:
gh release download production-stack-free-20261120 --repo mhvnsnt/dream-girl \
  --pattern 'kdenlive-26.08.3-x86_64.AppImage'
chmod +x kdenlive-26.08.3-x86_64.AppImage
./kdenlive-26.08.3-x86_64.AppImage --appimage-extract
./squashfs-root/usr/bin/kdenlive
```

Run notes (verified 2026-11-20): `--appimage-extract` exit 0, no FUSE
needed. Contents: `AppRun`, `org.kde.kdenlive.desktop`,
`usr/bin/kdenlive`, `usr/bin/kdenlive_render`, plus bundled
`ffmpeg`/`ffplay`/`ffprobe`. The stock AppImage needs `libOpenGL.so.0` —
provide it with a symlink shim to the system `libGL.so.1` plus the
vendored libEGL, and the GUI reaches its welcome/splash under
`dbus-run-session` + xvfb.

**GPU route:** GPU-accelerated preview/effects go via the GPU route —
Kaggle GPU, Colab, Lightning AI, or Oracle — with the shim above in
place. The Flatpak (`org.kde.kdenlive`) is the project's other supported
Linux route.

## Stage it serves

Video editing — the primary editor: cutting episodes, assembling
renders, subtitles, colour. This is the editing slot's real answer.

## Honest limits

- Needs proxies for smooth playback of heavy footage on low-end
  systems (the project's own guidance).
- The 26.08.3 AppImage is ~200 MB; Flatpak is the project's other
  supported Linux route.

## Licence

GPL-3.0. Source + licence logged honestly next to the item, per lane
rule; licence never gated the pull.
