# App Layer — Creative Tools

Desktop + web **applications** that sit above the animation-kit pipeline
tools (EbSynth, RIFE, cartoonize, etc.). Every tool here is **free and
open-source** — no paid APIs, no cards, standing law.

> Status note 2026-10-10: Penpot self-host is still PENDING (see below);
> everything else is either cloned locally or installable on demand.

## 1. OpenCut — video editing (replaces CapCut)

- **Local clone:** `~/workspace/video-fix-tools/opencut` (MIT)
- **Status — classic vs rewrite:** OpenCut is being rewritten from the
  ground up (Rust core, headless mode, MCP server for AI agents,
  plugin-first architecture). **Use the CLASSIC version today**
  (`opencut-classic` / [opencut.app](https://opencut.app)); the rewrite
  lives at [new.opencut.app](https://new.opencut.app) until it takes over.
  The headless mode + MCP server in the rewrite is the future automation
  path for agent-driven commercial assembly.
- **Replaces:** CapCut / Premiere for quick cuts, pacing, captions, music beds.
- **Repo work it relates to:** TRIPPEDD commercials (Luck of the Irish,
  Green Iris, trippy cards), YouTube Shorts batches, font commercials
  (`font-wizard/pipeline/make_commercial.py` output), episode assembly.

## 2. Penpot — design & layout (replaces Canva/Figma)

- **Self-hosted URL:** PENDING — see blocker below.
- **What it is:** open-source Canva/Figma alternative, self-hosted via
  Docker Compose (frontend + backend + exporter + postgres + redis).
- **Blocker (2026-10-10):** disk on this VM is at 86% with a hard ceiling
  of 88% (owner popup at 90%). Docker + Penpot images need ~2.5–4GB, which
  would breach the ceiling — deployment waits until the disk-space-guardian
  frees backup-verified bulk. The dead-worker notes from the original
  attempt are preserved in the `penpot-selfhost-and-appwire` checkpoint.
- **Replaces:** Canva/Figma for thumbnails, ID cards, specimen/sales
  sheets, key-art comps, promo layouts.
- **Repo work it relates to:** TRIPPEDD network cards ("STAY TRIPPEDD",
  wavy trippy + black-background variants), Font Wizard specimen sheets
  (SPECIMEN-FIRST LAW — specimens are the sales page + owner review),
  YouTube thumbnails (VIRAL UPLOAD LAW — always custom, high-contrast).

## 3. Tahoma2D / OpenToonz — frame-by-frame 2D animation (desktop FlipaClip)

- **OpenToonz source:** `~/workspace/video-fix-tools/opentoonz`
  (build-from-source; the Studio Ghibli production tool, open-sourced).
- **Tahoma2D:** the friendlier OpenToonz fork — NOT cloned yet; pull it
  when a hand-drawn lane actually starts.
- **Replaces:** FlipaClip-style rough 2D animation on desktop; complements
  the kit's scripted headless Blender Grease Pencil (`grease-pencil/`).
- **Repo work it relates to:** hand-drawn 2D segments — In the Bushes
  (kid-drawing lo-fi style lock), TRIPPEDD interstitials (wavy trippy),
  2D character FX passes.

## 4. Inkscape / GIMP / Krita — the graphics trio

| Tool | Role | Kit feed |
|---|---|---|
| **Inkscape** (vector) | Graffiti logo lockups, sticker line art, title cards | feeds `tracing/` raster→SVG pipeline |
| **GIMP** (raster) | Photo cleanup, card/thumbnail composites, texture prep | feeds EbSynth sources, card builds |
| **Krita** (painting) | Painted keyframes for EbSynth rotoscope | the Luck of the Irish commercial v3 method: painted keyframe → EbSynth propagation |

- Not installed on this VM yet — `apt install` on demand per lane.
- **Replaces:** Illustrator/Photoshop/Procreate for the whole network.
- **Repo work it relates to:** EbSynth keyframe painting, font specimen
  sheets, trippy cards, thumbnails, key art.

## Wiring (KIT WIRING LAW)

Per the 2026-10-10 standing rule, every new media tool gets wired into
Pocket Studio (`pocket-studio/server.py` + the Colab notebook) AND into the
animation-kit in all production repos — no tool lives only in one
conversation. When Penpot deploys, its URL lands here and in Pocket Studio.
