# AnimLab — God-Molecule-Show-Studio

Role in this repo: Draw → Rig/Tween → Composite → Finish, feeding tools/video_pipeline for assembly.

## What it is

AnimLab is a free animation studio by KevesDev (itch.io: `kevesdev`, AnimLab page).
Vector drawing, pegs, rigging (Bone / Game Bone / Curve / Envelope), node-graph
compositing, multi-camera timeline, audio mixer, 3D primitives, MP4/PNG export.

- **Cost:** freeware — $0. **NOT open-source** — there is no public source repo.
- **Live version:** **v0.2.26** (itch page updated 2026-11-20 15:50 UTC, verified 2026-11-20).
- **Home:** itch.io AnimLab page (KevesDev). No public repo exists — the itch page is the source of truth.

## Full file list (v0.2.26, itch page 2026-11-20)

| File | Size |
|---|---|
| Windows Setup.exe | 131 MB |
| Windows .msi | 179 MB |
| macOS .dmg | 89 MB |
| Linux AppImage | 196 MB |
| Linux .deb | 75 MB |
| Linux .rpm | 75 MB |
| Linux arm64 .deb | 71 MB |
| Android .apk | 66 MB |

This repo uses the **Linux .deb** (workstation) and the **Android .apk** (phone — the
owner is phone-only, so the .apk matters: AnimLab on Android is the way he can open,
review and test rigs directly).

## $0 checkout route (proven working)

1. Open the itch.io AnimLab page.
2. Set the price to **$0.00**.
3. Click **"No thanks, just take me to the downloads"**.
4. No email, no account, no payment. The download page lists all files above.

Download-page links carry tokens that expire in ~30 minutes — always fetch a fresh
download-page URL and pass it to `fetch-animlab.sh` as `$1`; never hardcode a link.

## Install

### Linux (.deb)
```sh
sudo dpkg -i animlab_*_amd64.deb
sudo apt-get install -f   # only if dpkg reports missing dependencies
animlab                   # launch (binary name may vary — check /usr/bin/animlab*)
```

### Android (.apk)
```sh
# On the phone: download the .apk from the itch download page, tap it, allow
# "Install unknown apps" for the browser/files app if asked, install.
# Or from a workstation with adb:
adb install animlab_*.apk
```

## Binary status — UNFETCHED (honest)

**As of 2026-11-20 the AnimLab binaries are UNFETCHED.** Reason: itch.io returned
HTTP 429 (rate-limited) and browser transfer limits blocked the download during the
fetch attempt. No binary is staged in this repo and none is claimed to be here.

When the fetch lands, binaries go to the repo Release named in `fetch-animlab.sh`
— never committed as blobs in the tree. Re-run `fetch-animlab.sh` with a fresh
download-page URL (see that script).

## Pipeline slot

See `PIPELINE-STAGE.md` in this folder for exactly where AnimLab slots into this
show's pipeline.
