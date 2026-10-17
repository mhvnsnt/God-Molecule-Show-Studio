# CREATIVE TOOLKIT CATALOG — the full free arsenal

Everything here is $0 to use: open source, freemium, or proprietary-free.
Three tiers: **A** = pulled into this kit and Pocket Studio (scriptable here),
**B** = desktop/mobile apps for his hands, **C** = heavy/GPU work via
Colab/Kaggle notebooks on his free GPU.

---

## TIER A — in this kit (wired into Pocket Studio)

| Tool | Does | Replaces | Verify |
|---|---|---|---|
| `audio-sep/run_demucs.py` | vocal/drum/bass separation (Demucs htdemucs) | Lalal.ai / paid stem splitters | stems decode, 4 files out |
| `audio-sep/run_beats.py` | beat/BPM + click track (aubio, librosa fallback) | manual beat-mapping | BPM sane on test track |
| `audio-sep/run_stretch.py` | Paulstretch extreme time-stretch | Paulstretch app | output = stretch × input |
| `midi/render_midi.py` | MIDI → WAV, built-in numpy GM synth (no soundfont) | FluidSynth + 140MB soundfont | renders test .mid |
| `mesh3d/convert.py` | 3D convert GLB/OBJ/STL/PLY + stats (trimesh) | online converters | round-trip converts |
| `autocut/run_autocut.py` | Triller-style beat auto-cut | Triller auto-cut | mp4 out, cuts on beats |
| `cover/run_cover.py` | album cover maker | Canva cover templates | 3000×3000 jpg out |

**Honest limits:** Demucs is CPU-slow here (~1–2 min per audio minute);
for big jobs run it on Colab GPU instead. The numpy MIDI synth is GM-ish,
not a sampled orchestra — great for beds and sketches, not final orchestral
mockups (that's what Tier B/C is for).

---

## TIER B — for his hands (install yourself, NOT in this repo)

### Audio — the "FL Studio mixed with BandLab" shelf
- **LMMS** (free, open, Win/Mac/Linux) — the FL Studio lookalike: patterns,
  piano roll, built-in synths. Best first DAW if FL's workflow is home.
  → episode scoring, beat-making. lmms.io
- **Cakewalk by BandLab** (FREE, Windows) — was $600 SONAR Platinum, now $0.
  Full pro DAW: unlimited tracks, pro mixing, VST3. → final episode mixes.
- **Ardour** (open, Win/Mac/Linux) — pro-grade DAW, no track limits.
  → serious audio post when Cakewalk isn't an option.
- **BandLab** (free, web + Android/iOS) — the actual BandLab: mobile-first,
  social, cloud. → sketching ideas on the phone, collaborations.
- **Vital** (free tier) / **Surge XT** (open) — modern wavetable synths.
  → bass, leads, sound design. Vital's free tier is generous.
- **Valhalla Supermassive** (FREE) — the reverb/delay everyone uses.
  → space and atmosphere on vocals/scores.

### Video — the "CapCut mixed with Adobe" shelf
- **DaVinci Resolve** (free tier, Win/Mac/Linux) — the free tier is 90% of
  Studio: pro edit + color + Fairlight audio + Fusion VFX. → episode assembly,
  color, finishing. (Not open source, but $0 and the strongest free editor.)
- **Kdenlive** (open) / **Shotcut** (open) — lighter timeline editors.
  → quick cuts when Resolve is overkill.
- **OpenCut** (open, in this kit's orbit) — the open-source CapCut;
  web + desktop. → CapCut-style quick edits without the subscription.
- **Natron** (open) — After-Effects-like node compositing.
  → VFX shots, green screen, motion graphics.

### Design — the "Canva mixed with Photoshop" shelf
- **Penpot** (open, self-hostable) — the open Canva/Figma. We can self-host
  it for him. → thumbnails, cards, channel art, design systems.
- **Photopea** (free, browser) — Photoshop in a tab, opens PSDs.
  → quick photo edits with zero install.
- **Inkscape** (open, vector) / **GIMP** (open, raster) / **Krita** (open,
  painting+animation) — the classic trio. → logos, posters, painted art.
- **MyPaint** (open) — infinite-canvas brush heaven. → brushes and
  painterly art; pairs with Krita.
- **Brushes:** Krita's built-in pack + community bundles (all free) cover
  99% of brush needs — watercolor, ink, chalk, textured.

### Animation — the "FlipaClip" shelf
- **Tahoma2D** (open) — friendliest frame-by-frame 2D. → hand-drawn shots.
- **OpenToonz** (open, Ghibli's tool) — the full studio beast.
- **Blender Grease Pencil** — 2D drawn inside 3D space. → hybrid shots.
- **Pencil2D** (open) — dead-simple frame-by-frame for quick gags.

### 3D — the 3D shelf
- **Blender** (open — already at `~/workspace/tools/blender/`) — modeling,
  rigging, animation, rendering. The hub of all 3D work here.
- **Mixamo** (FREE, Adobe) — auto-rigger + huge mocap animation library.
  **This is the NO FAKE ANIMATION law's best friend:** real motion clips
  instead of snapping bodies between poses. → character animation.
- **Daz 3D** (free base) — posed characters fast. → background actors,
  reference poses.
- **Unreal Engine** (free until $1M revenue) / **Unity** (free tier) /
  **Godot** (open) — real-time engines. → game work, real-time cinematics.
- **MakeHuman** (open) — parametric human generator. → base meshes.
- **ArmorPaint** (open) — Substance-Painter-like 3D texture painting.
  → painting character/prop textures.
- **Material Maker** (open) — procedural PBR materials. → tileable
  textures, stylized surfaces.
- **Meshroom** / **COLMAP** (open) — photogrammetry: photos → 3D models.
  → real-world props and sets from phone photos.

---

## TIER C — notebook pattern (his free GPU, like the Pocket Studio fix)

These need a GPU, so they ship as Colab/Kaggle notebooks he runs himself —
same pattern as `Pocket_Studio_Colab.ipynb`. Notebooks live next to this
catalog; JSON-validated, GPU cells not executed here.

- **ComfyUI notebook** — node-based AI image/video generation (the open
  Stable-Diffusion studio). → key art, style frames, AI-assisted backgrounds.
  Needs ~8GB VRAM — fits Colab free T4 with light models.
- **RVC notebook** (Retrieval-based Voice Conversion) — voice → voice
  conversion, trained on ~10 min of audio. **Directly serves our
  leprechaun-voice work:** record/approve a read, convert any line into it.
  → character voices, the V1/V2 leprechaun line, ADR.
- **TripoSR notebook** — single image → 3D model in seconds (open,
  runs on free T4). → props, background models from concept art.
  (TRELLIS is the heavier, higher-quality alternative — same notebook
  pattern when he wants it.)

---

## What goes where (episode work → tool)

| Episode job | Reach for |
|---|---|
| Score beds / jingles | LMMS or Cakewalk (compose) → `midi/render_midi.py` (quick render) → Valhalla (space) |
| Dialogue cleanup / remix | `run_demucs.py` (isolate vocals) → Cakewalk/Ardour (mix) |
| Sound design | `run_stretch.py` (washes, risers) → Vital/Surge (synth hits) |
| Beat-synced edits | `run_beats.py` (BPM map) → `run_autocut.py` (Triller-style cut) |
| Thumbnails / cards / covers | Penpot / Photopea → Pocket Studio `textcard`, `cover` |
| Hand-drawn shots | Tahoma2D / OpenToonz → EbSynth propagation (in kit) |
| 3D characters | Blender + Mixamo clips (NO FAKE ANIMATION) → ArmorPaint textures |
| Photos → 3D props | Meshroom/COLMAP, or TripoSR notebook from concept art |
| AI key art | ComfyUI notebook |
| Character voices | RVC notebook (train on approved reads) |
