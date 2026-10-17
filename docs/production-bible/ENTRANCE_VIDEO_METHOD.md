# Entrance Video Method — the El Toro de Oro production bible

**What this is:** the exact, step-by-step method behind the approved El Toro de Oro 50-second entrance video (v1, built Oct 4 2026 CT), plus the v2 rig/QA layer that was added after. Every command, file, tool, version and license is listed so any agent (Grok Bot, Muse/Ashes, MoneyManBusch, Repo Co Dev) can rebuild it bit-for-bit and make the next one for any character in any TRIPPEDD game.

**Status labels used here:** DONE (verified, bytes exist), PARTIAL (started, not finished), NOT DONE, UNKNOWN (never treat UNKNOWN as PASS).

**Canonical copies:** this file lives at `docs/production-bible/ENTRANCE_VIDEO_METHOD.md` in money-machine-hq, Bannon, TRIPPEDD-Production-studios- and God-Molecule-Show-Studio. Source of truth for the code is **mhvnsnt/money-machine-hq**:
- `tracks/entrance-kit/samples/el-toro-de-oro/` (approved deliverable, PR #4)
- `tracks/promo-cinematic-kit/samples/el-toro-de-oro/scripts/` (the hand-built v1 scripts, same bytes as box `/workspace/offers/entrance-kit/`, `SHA256SUMS` verified)
- `tracks/promo-cinematic-kit/pipeline/` (the same build as one command: `make kit CONFIG=kit.json`)
- `tracks/promo-cinematic-kit/HOW-EL-TORO-WAS-MADE.md` (plain-English walkthrough + honest improve list)
- `tracks/promo-cinematic-kit/templates/`, `tools/grid.py`, `tools/rerender_shot.py` (PR #16: shot-list templates + in-place fix tool)
- branch `feat/entrance-kit-v2-el-toro` → `tracks/promo-cinematic-kit/examples/el-toro-v2/` (v2 rig/clip/theme work, PARTIAL)
- Bannon `tools/promo-pack-kit/` (beat grid, 12 defect gates, side-by-side proof) and `tools/video/` (OTIO EDLs, assembler, encode profiles)
- Box (shared machine) `/workspace/rig-repair/` (Blender headless rig repair + rig QA matrix)

---

## 0. The rules that made it work (read first)

1. **His own model, his own canon.** Only the owner's rigged GLB is ever on screen. No AI faces, no stand-in humans, no real wrestler names/likenesses, no cloned themes.
2. **Every on-screen word traces to a canon line** (`Bannon/canon/00_cast_and_world.md`). Unknown facts are dropped or read **"parts unknown"**; v1 showed a grey `[PLACEHOLDER - NOT IN CANON]` hometown, which was later removed (see §12). Never invent.
3. **The music is the clock.** One beat grid drives cuts, flashes, pyro, lower thirds and walk cadence.
4. **Probe before you render.** 4 test frames per clip on the real model; reject clips that T-pose, close the feet, or slide.
5. **Never regenerate over existing work.** Fixes are per-shot re-renders into a new version (`rerender_shot.py`), old version kept.
6. **Proof or it didn't happen** (`media-proof-standard` skill): reopened bytes, SHA-256, full decode, check frames actually looked at, before/after pairs of the same frame.

---

## 1. Toolchain (exact versions on the box, Oct 2026) and licenses

| Tool | Version | Used for | License |
|---|---|---|---|
| ffmpeg (Debian build) | 7.1.5-0+deb13u1 | encode, mux, decode gate, frame extraction, concat | LGPL-2.1+/GPL-2+ (build includes libx264, GPL-2) |
| libx264 / AAC (ffmpeg native) | bundled | H.264 CRF 17 video, AAC 320k audio | GPL-2 / LGPL |
| Node.js / npm | 20.19.2 / 9.2.0 | headless renderer | MIT |
| Google Chrome (headless, SwiftShader software WebGL) | 154.0.8037.57 | renders WebGL frames without a GPU | Chrome: Google ToS freeware; SwiftShader Apache-2.0 |
| playwright-core | ^1.55.0 | drives headless Chrome | Apache-2.0 |
| three.js | ^0.186.0 | 3D scene, GLB loading, skinning, shadows | MIT |
| React / react-dom | 19.2.x | scene graph host | MIT |
| @react-three/fiber | ^9.7.0 | three.js in React (game's own renderer) | MIT |
| Vite + @vitejs/plugin-react | ^8.2.0 / ^5.2.0 | serves the render page + imports game code unmodified | MIT |
| simplex-noise | ^4.0.3 | camera drift / shake | MIT |
| fzstd | ^0.1.1 | decodes the game's zstd-packed baked clips | MIT |
| Python | 3.13.5 | music, post, proof | PSF |
| numpy | 2.5.3 | DSP, compositing | BSD-3 |
| scipy | 1.18.1 | filters, reverb convolution, resampling | BSD-3 |
| Pillow | 12.3.0 | all graphics (logo, cards, lower thirds, shards) | MIT-CMU (HPND) |
| pyloudnorm | >=0.1.1 | -14 LUFS normalization (BS.1770) | MIT |
| pygltflib | 1.16.5 | GLB inspection | MIT |
| Blender (headless) | 4.2.3 LTS (`/workspace/rig-repair/tools/blender-4.2.3-linux-x64`) | rig repair, weight transfer (v2 / rig-repair lane) | GPL-3 |
| OpenTimelineIO (Bannon `tools/video/beat_edl.py`) | per `tools/video/requirements-video.txt` | EDL as `.otio` | Apache-2.0 |
| Fonts: Anton, Oswald | from Google Fonts | logo/name (Anton), text (Oswald) | SIL OFL 1.1 (license files ship next to the fonts) |
| tesseract (optional) | system | OCR banned-name check on frames | Apache-2.0 |

**Motion source license: UNKNOWN.** The baked clips are from the game's `schwarzerblitz` bank in `brutalfistgrokversionten/public/motion/baked/` (some names reference real people, e.g. `JOHNSON*`; names never appear on screen). Fine for the owner's own sample; **confirm license or replace with the owner's mocap/CC0 (CMU, ACCAD, 100STYLE, Quaternius) before any paid client kit.**

Setup (one time):
```bash
cd money-machine-hq/tracks/promo-cinematic-kit/pipeline
make setup            # python3 -m venv .venv && pip install -r requirements.txt ; cd render && npm ci
# Chrome must exist at /usr/bin/google-chrome (playwright-core uses the system browser)
```

---

## 2. Pre-production (before any pixel)

1. **Pick the character and audit assets.** El Toro was picked because: own rigged model (`brutalfistgrokversionten/public/models/EL_TORO_DE_ORO.glb`, 1 skinned mesh, 58 bones, Mixamo-style), masked (no face risk), richest canon (epithet, 2 signatures, 2 finishers), strong palette (gold/red).
2. **Extract canon facts** (`Bannon/canon/00_cast_and_world.md` line 29): `EL TORO DE ORO / THE GOLDEN BULL`, `FINISHER: EL GRITO DE LA BESTIA`, `SIGNATURE: EL CUERNO DORADO (RUNNING SPEAR)`, show `OFF THE TOP ROPE`. Hometown: **not in canon** (the owner floated "Spain" in `MUSE_MISSION_BRIEF.md` but never confirmed) → not shown.
3. **Write the beat grid** (§6) and the shot list (§7) as JSON before rendering. Generate/verify with:
```bash
python3 tracks/promo-cinematic-kit/tools/grid.py tracks/promo-cinematic-kit/templates/titantron_loop.json --table
python3 Bannon/tools/promo-pack-kit/scene_grid.py --template el_toro --bpm 120 --table   # reproduces v1 cuts: hit 4.00 s, walk-out 12-19 s, 1200 frames @ 24 fps / 1500 @ 30
```
4. **Write `kit.json`** (pipeline config): name, epithet, show, logo lines, facts (`hometown` may be `null` → dropped), GLB + `game_root`, `repair` mode, likeness portrait + crop, clip per slot, music key/mode/BPM/seed, full color palette, emblem, watermark. The El Toro one is `pipeline/kit.json`.
```bash
python run_kit.py kit.json --stage check     # validates config, prints the frame timeline; renders nothing
```

---

## 3. Model and rig (load, repair, QA)

### 3.1 v1 (what the approved video actually used)
- The renderer imports the **game's own load chain unmodified** from `game_root` (`/workspace/vten-main-audit` = brutalfistgrokversionten main): texture restore → **skin-weight repair (398 weights fixed on El Toro)** → bind-space repair (0 bones moved).
- **Distant-weight re-bind turned OFF** (`"repair": "skin"`) — that step builds a slab artifact on some models.
- Scaled to the game standard **1.85 m**, feet on the canvas.
- **Calibration:** clips are authored on `BANNON_rigged.glb`; its hips height (**0.16523**) is read once (logged as `canonHipsY`) so root motion is rescaled to El Toro's skeleton. That model is never shown.
- **Binding gate:** every clip has 23 tracks (22 bone rotations + hips position). Render aborts if any clip binds < 8 tracks; El Toro bound **23/23 on every shot** (`work/eng/render_report.json`).
- Known v1 defect left in: a **pale left-shoulder skin flap** in some poses (title card, S6b).

### 3.2 Shoulder fix / skin-weight repair (v2, PARTIAL)
Branch `feat/entrance-kit-v2-el-toro`, `examples/el-toro-v2/build/rig/`:
```bash
python3 build/rig/repair_weights.py  EL_TORO_DE_ORO.glb EL_TORO_DE_ORO_v2.glb      # same mesh + 58-bone skeleton, weights only
python3 build/rig/eval_weights.py proof/weights_eval.json v1=v1.dec.glb v2=v2.dec.glb clips=STRUT,TAUNT,...
python3 build/rig/heat_sheet.py ...                                                 # per-vertex stretch heat map (top row v1, bottom v2)
```
Measured on 445 poses: worst-case edge stretch p99.9 **18.3 → 9.0**; edges stretched >1.5x **734k → 417k**; bind pose deviation 4e-6; no NaNs; seams checked (welded duplicates stay together). Muse's re-weights scored worse on this model (30.2 / 40.1), so v2 starts from the original. **Accept a weight fix only if stretch drops AND bind pose is unchanged AND the heat map shows fewer red triangles at the shoulder.**

### 3.3 Full rig repair for broken models (box `/workspace/rig-repair/`)
```bash
/workspace/rig-repair/tools/blender-4.2.3-linux-x64/blender -b -P /workspace/rig-repair/repair_rig.py -- IN.glb OUT.glb --target mixamo --mode auto --height 1.85 --report OUT.report.json
python3 /workspace/rig-repair/make_matrix.py   # writes MATRIX.md: every model x 6 test clips, PASS/FAIL (stretch, ground, collapse, effector, L/R swap, facing, no-skin)
```
Route A = keep skeleton, fix weights/alignment; Route B = no skin → landmark detection + template skeleton (`templates/mixamo65.json`) + weight transfer. Never overwrites input.

### 3.4 Rotation-error and deformation gates (Bannon `tools/promo-pack-kit/`)
```bash
python3 tools/promo-pack-kit/promo_gates.py --metrics shot_metrics/            # PASS/FAIL per gate per shot, exit 1 on any fail
python3 tools/promo-pack-kit/promo_gates.py --self-test                        # MUST exit 1 (fails the bundled v1 defects)
python3 tools/promo-pack-kit/sbs_proof.py ...                                  # v1|v2 side-by-side + fix checklist footer
```
Gates: rotation error ≤ 3.0° (owner QA chart: Bannon v1 ≈ 5.1°, Cody ≈ 7.0°, El Toro walk-out after repair 4.2° = NOT FIXED), feet planted, facing == movement, no skin flap, no ribbon/exploded geometry, no foot slide, no rope crossing, no broken poses. **Caveat:** today the gates evaluate a metrics JSON someone measured; the hardening PR (Muse lane) makes them measure the GLB directly. Until that lands, the measured numbers must come from `eval_weights.py` / rig-repair matrix, recorded with file SHA-256.

---

## 4. Animation clips, retargeting, staging

- Clips: baked game motion `public/motion/baked/<NAME>.json` (zstd-packed tracks decoded with fzstd by the game's own decoder). No El Toro-specific clips existed in v1, so these were borrowed (labelled STAND-IN in docs):

| Slot | Clip | Len | Use |
|---|---|---|---|
| stance | GRAFSTANCE | 1.58 s loop | S1, S4b |
| intro_pose | JOHNSONINTROPOSE | 3.75 s | S2 (from 0.4 s at 0.75x), S6b (0.6 s at 0.85x), title cards frozen at 3.25 s |
| walk | SHAZWALK | 0.92 s loop | S3 at 0.9167x → one 2-step cycle = exactly 2 beats |
| entrance | SHAZENTRANCE | 3.29 s | S4a, stretched over 4 s (0.8225x) |
| slow_pose | JOHNSONINTROPOSE2 | 3.75 s | S5 at 0.5x slow-mo |
| win_pose | JOHNSONWINPOSE | 2.67 s | S6a (0.9x) |

- **Probe stage** (rejects bad clips before the long render):
```bash
python run_kit.py kit.json --stage probe     # 4 frames per slot -> out/<slug>/probe_sheet.png ; LOOK at it
```
  Rejected for El Toro: Bannon-bank LOCO_STRUT and TAUNT_* (arms near T-pose, feet together on this rig).
- **No-slide walk:** `public/motion/stride_speed.json` gives SHAZWALK = 1.016 m/s authored; root travel = 1.016 × 0.9167 m/s (rate × authored speed).
- **Facing fix:** per shot, body facing is measured from the arm bones and the character is yawed to the target, so a clip's hip twist can't point him wrong.
- **Retargeting other rigs/mocap:** `/workspace/rig-repair/scripts/retarget_clip.py` (bone-name map via `names.mjs`, Mixamo/UAL conventions); v2 clip authoring in `el-toro-v2/build/anim/build_clips.py` + `clip_io.py` (writes game-format baked JSON) and `sheet.py` (contact sheet per clip). Missing moves (taunts, grapples, dives) are **authored on his rig**, not skipped; preview each one on the actual model.

---

## 5. Ring, arena, lighting, crowd, pyro

- **v1 set:** the game's ring (`stage: "void"`): ring + canvas + ropes from the game's stage code in a black void. Lights: the game's ring light + two gold back spots (`light_a #ffcf6a`, `light_b #ffb347`), PCF shadows, a shadow-catcher plane for transparent card plates.
- **v1 crowd:** none (honest defect). **v1 pyro:** 2D (post, §9).
- **v2 (PARTIAL, code only, not verified in a finished frame):** `el-toro-v2/build/render/src/arena.ts` (original crowd band with phone-light twinkles, haze, entrance stage, moving beams, coloured rims — all logo-free) and `pyro.ts` (3D fountains the camera passes, light flash on the character). Rope occlusion per shot: `build/proof/rope_occlusion.py` (fixes the v1 S4a rope across the torso).
- Background swap trick for other projects: render the character RGBA with a locked camera, composite over arena plates (`/workspace/intro-movie/arenas`).

Render command (one browser per shot, crash → retry up to 5x, re-run resumes):
```bash
python run_kit.py kit.json --stage render
# equivalent single shot:
cd pipeline/render && KIT_GAME_ROOT=/workspace/vten-main-audit KIT_ALLOW=/workspace/vten-main-audit/public/models \
  node render.mjs --config ../out/<slug>/work/kit.resolved.json --out ../out/<slug>/work/eng --shots S3_WALK
```
Output: `work/eng/<SHOT>/f_00000.png …` (RGBA 1920×1080) + `render_report.json`. ~11 min for ~1,400 frames on the shared 8-core box (SwiftShader).

---

## 6. Beat grid and EDL

30 fps, 120 BPM → **1 beat = 15 frames, 1 bar = 60 frames = 2 s**; 1,500 frames = 50.000 s; every cut on a bar line. `frames_per_beat = fps*60/BPM`. Timeline (from `--stage check`):

| Shot | Frames | Beats | Time | Content | Camera |
|---|---|---|---|---|---|
| S1_SIL | 0–119 | 0–8 | 0–4 s | silhouette push-in, black from f112 (dead air) | low slow dolly in |
| S2_CARD | 120–359 | 8–24 | 4–12 s | **hit at 4.0 s**: logo slam, white flash, gold shards | slow push |
| S3_WALK | 360–569 | 24–38 | 12–19 s | walk-out corner→centre, lower third #1 in | tracking ¾ follow |
| S4A_ENTR | 570–689 | 38–46 | 19–23 s | entrance gesture | slow orbit |
| S4B_CLOSE | 690–839 | 46–56 | 23–28 s | mask close-up | orbit at head |
| S5_SLOW | 840–1079 | 56–72 | 28–36 s | slow-mo breakdown, letterbox 132 px, 55% sat | low orbit |
| S6A_WIDE | 1080–1229 | 72–82 | 36–41 s | crane, pyro, shards, lower third #2 | crane down/across |
| S6B_MED | 1230–1379 | 82–92 | 41–46 s | hero pose | gentle push |
| END_CARD | 1380–1499 | 92–100 | 46–50 s | title card, flash, fade from 49 s | still |

Lower thirds: beats 28–48 (f420–720: name, epithet·show, facts) and 74–86 (f1110–1290: signature). Intentional off-beat (`dead_air` at beat 7.5) must be marked intentional in the grid JSON.

EDL formats: shot JSON (`templates/*.json` → `tools/grid.py`), OTIO (`Bannon/tools/video/beat_edl.py` → `.otio`, 2 tracks + beat/phrase markers), and the per-project `edit.json` used by `rerender_shot.py` (§11). **Keep the EDL in git next to the renders.**

---

## 7. Music (generated in code, deterministic)

`pipeline/music/theme.py` (+ `bfsynth.py`, an unmodified copy of the intro-movie DSP helpers). 100% numpy/scipy synthesis: no samples, loops, presets, MIDI, AI music or network.
```bash
python run_kit.py kit.json --stage music    # ~15 s -> entrance_theme.wav (48 kHz/24-bit) + .mp3 (LAME 320)
```
- E **Phrygian dominant** (E F G# A B C D), 120 BPM, 25 bars = 2,400,000 samples, seed **4072026** (re-renders bit-identical: WAV sha256 `b23393b7f327…`).
- Structure: 0–3.75 s pre-roll (sub swell, 7 tom pulses, reverse riser) → **3.75–4.0 s hard-zeroed dead air** → 4.0 s HIT (sub boom 120→30 Hz, noise crack, inharmonic "gold bell" partials on 330 Hz ×1/2.76/5.40/8.93/13.34/18.64, ~140 crystalline pings) → stomp intro → main riff + brass melody (12–28 s) → halftime breakdown (28–36 s) → reprise (36–46 s) → final hit 46 s, fade 48.6–49.9 s, silence to 50.0 s.
- Instruments: synth drums; 2 guitar "takes" (3 saws, amp sim at 96 kHz, panned); bass an octave under; brass (3 detuned saws, filter blat, scoop, delayed vibrato, 2 s hall).
- Master: **-14 LUFS** (pyloudnorm). v1 true peak -0.85 dBTP (too hot); v2 theme -1.35 dBTP with +2.8 dB sub on the hit (owner has not listened yet).
- For a real song (e.g. Stick-Up "Out My Body"), use the owner-supplied file and beat JSON (`Bannon/stickup/audio/`) instead; never rip audio from YouTube.

---

## 8. Titantron name plate, cards, fonts (all code-drawn, Pillow + numpy)

`pipeline/post/gfx.py` + `compose.py`:
- **Logo:** horns emblem (two tapering Bézier horns + diamond, 4× supersampled) over "EL TORO" (Anton, big) and "DE ORO" (smaller, side rules). Gold = 4-stop vertical gradient (`metal_top/mid/mid2/bot`), dark outline, bevel highlight, soft drop shadow.
- **Card background:** red→black radial glow, 18 slowly rotating gold rays, fine diagonal texture.
- **Title cards:** hero pose rendered RGBA (`CARD_STILL` 1920×1080, `CARD_STILL_V` 1080×1920) with shadow catcher, composited: 16:9 = logo left/char right; 9:16 = logo, epithet, char filling the rest.
- **Lower third:** slanted panel 1240×210 (`panel` colour, 215 alpha), gold top stripe, likeness bust inset from the game portrait (`public/portraits/likeness/el_toro_de_oro.png`, crop `[150,40,410,300]`), name in gold Anton 70, `EPITHET · SHOW` in Oswald 28, facts in Oswald 26 (placeholder facts grey; `null` facts are skipped). Slides in/out with cubic ease over 10 frames at y=820.
- **Watermark:** "SAMPLE ENTRANCE KIT · OFF THE TOP ROPE", top right, ~60% opacity.
- Fonts: `pipeline/fonts/Anton-Regular.ttf`, `Oswald.ttf` + OFL texts.

---

## 9. Post / compositing / ffmpeg chain

`python run_kit.py kit.json --stage post` runs `post/compose.py <kit.resolved.json>`; every frame is a pure function of its frame number (multiprocessing pool, `KIT_WORKERS`), piped as raw RGB to ffmpeg:
1. Grade gold: lift (12,6,0), gain (1.08,1.0,0.86), contrast 1.12, sat 1.1; vignette.
2. S1: silhouette grade (gain `silhouette_gain`, contrast 1.5, gamma 2.2 ×0.55, floor gradient), tom-pulse flicker, **black from beat 7.5**.
3. Beat flashes (bar downbeats big, beats 2/4 small), big flashes on hit/reprise/final, strobe on halftime snare.
4. Pyro: 2D spark fountains both bottom corners every bar (70 sparks/side, gravity, motion streaks, white-hot→orange).
5. Shards: 46 gold triangles on hit, reprise, final hit.
6. Breakdown: 55% saturation + 132 px letterbox.
7. Lower thirds, watermark.
8. Encode:
```bash
ffmpeg -f rawvideo -pix_fmt rgb24 -s 1920x1080 -r 30 -i - -i entrance_theme.wav -map 0:v -map 1:a \
  -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart -t 50.000 entrance_video.mp4
```
Stills only: `--stage stills`. Contact sheet: `--stage sheet`. Report + hashes: `--stage report` (`run_report.json`).
Bannon alternatives for footage-based edits: `tools/video/assemble_character_video.py` (sting → name card → footage → end card, two-pass loudnorm), `make_beat_edit.py`, `caption.py`, `make_thumbnail.py`, `encode_profiles.sh` (draft/delivery/archive presets).

---

## 10. Proof (media-proof-standard, applied)

```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate entrance_video.mp4   # 50.000 s, h264 1920x1080 30/1, aac
ffmpeg -v error -i entrance_video.mp4 -f null -                                                                   # full decode, must print nothing
for t in 6 16 33 46.5; do ffmpeg -v error -ss $t -i entrance_video.mp4 -frames:v 1 check_frame_${t}s.png; done   # then LOOK at each
sha256sum * > SHA256SUMS
```
Plus: `proof_before_*` (raw render on grey) / `proof_after_*` (finished) at frames 60, 240, 450, 960, 1300 and both cards; audio: LUFS, true peak, RMS of the dead-air window (must be 0) and of the hit. Write PROOF.md (what was checked, by whom, what's still wrong) and PROVENANCE.md (every input path + SHA-256, tools/versions, licenses, how music was made). Regression: `pipeline/kit.json` rebuilds the sample with bit-identical WAV and cards (`pipeline/examples/EL_TORO_REGRESSION.md`). Agents can't hear audio — say so and ask the owner to listen. Never claim to have "watched" a video.

---

## 11. Fixing a shipped video (edit in place, never regenerate)

Project layout in git: `edit.json` (EDL: fps, size, audio, version, shots with frame ranges, segment paths, `render_cmd`), `segments/<shot>.vN.mp4`, `renders/<project>_vN.mp4`, `proof/`, `assets.json`.
```bash
python3 tracks/promo-cinematic-kit/tools/rerender_shot.py PROJECT_DIR --shot walk_out                    # runs the shot's render_cmd
python3 tracks/promo-cinematic-kit/tools/rerender_shot.py PROJECT_DIR --shot walk_out --segment fixed.mp4 # or use a pre-rendered fix
```
It conforms the new segment frame-exact, concats with the untouched segments (`-c:v copy`), re-muxes the same audio, writes `vN+1` (refuses to overwrite), full-decodes it, bumps `edit.json` (old segment kept in `history`), and writes before/after proof + SHA-256s.

---

## 12. Worked fix: hometown placeholder removed (Oct 14 2026)

No canon hometown exists, so the line was **dropped** (not invented). Method: set `"hometown": null` in a copy of `kit.json`, re-render only S3_WALK, S4A_ENTR, S4B_CLOSE (frames 360–839, the lower-third #1 window), compose those frames with the same post code, and splice them in with `rerender_shot.py --shot walk_out` into `entrance_video_v2.mp4`. v1 stays untouched. Proof: `samples/el-toro-de-oro/fix-hometown/` in money-machine-hq (PR #16).

---

## 13. Honest gaps (from HOW-EL-TORO-WAS-MADE.md §11/§13)
Shoulder flap in v1 (v2 weights PARTIAL), borrowed clips (license UNKNOWN), no crowd/stage/titantron in v1, 2D pyro, rope across torso in S4a, no 9:16 video, no 3D Blender title card, synth-sounding theme, hit at 4.0 s (offer promised ≤2 s). v2 status: `examples/el-toro-v2/STATUS.md`.

## 14. Checklist for the next character
1. Canon facts table (source line per word; unknown → drop or "parts unknown").
2. GLB audit: skins/joints/skinned prims/textures; rig-repair matrix row PASS or repaired.
3. Weight eval + heat map; rotation-error ≤ 3°; gates PASS (`promo_gates.py`).
4. `kit.json` → `--stage check` → `--stage probe` (look) → `music` (or owner track + beat JSON) → `render` → `post`.
5. Proof (§10), PROOF.md, PROVENANCE.md, SHA256SUMS.
6. Save via PR; auto-merge only if clean, CI green, nothing deleted (`.github/workflows/pr-clean-merge.yml`). Never post/publish without the owner's OK.
