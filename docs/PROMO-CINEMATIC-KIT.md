# Promo & Cinematic Kit: inputs for God Molecule

This repo's characters can go through the **Promo & Cinematic Kit** in money-machine-hq: [https://github.com/mhvnsnt/money-machine-hq/tree/main/tracks/promo-cinematic-kit](https://github.com/mhvnsnt/money-machine-hq/tree/main/tracks/promo-cinematic-kit) (worked example: [How El Toro de Oro was made](https://github.com/mhvnsnt/money-machine-hq/tree/main/tracks/promo-cinematic-kit/HOW-EL-TORO-WAS-MADE.md)). It makes **character promos and commercials, FMV-style intros, in-game cutscenes (pre-rendered or real-time), Titantron loops and trailers.**

## The pipeline, in short
1. **Rig check:** a rigged GLB → run this game's skin-weight/bind repair → probe sheet. Don't animate a broken or unrigged mesh.
2. **Shot list:** pick a template (`shot-templates/` in the kit) and time every shot to the second.
3. **Music** is written to the cut times (seeded, -14 LUFS, true peak ≤ -1 dBTP), or the owner's own track.
4. **Render:** headless fixed-frame Three.js/React-Three-Fiber + Playwright (no foot sliding: walk speed matched to the clip).
5. **Graphics:** cards and lower thirds drawn in code (Pillow + OFL fonts). **Every word comes from the canon file.** Gaps are labelled PLACEHOLDER.
6. **Encode + proof:** ffmpeg x264 CRF 17, then check frames that someone actually looked at, and before/after stills.

## This repo's inputs
| Input | In this repo |
|---|---|
| Rigged character GLBs | Mars proxies: `.trippedd_assets/mars_proxy.glb`, `tools/character/Marshead_Tripo_63779a1f.glb` (Tripo mesh, **not rigged**: rig it first, or use TRIPPEDD's `MARS_rigged.glb`) |
| Canon / lore file | `docs/GOD-MOLECULE-UNIFIED-BIBLE.md`, `docs/research/wave2/BIBLE-ADDITIONS.md` |
| Environments | Gaussian-splat world theme: `docs/GOD_MOLECULE_3D_WORLD_SPLAT_THEME.md` |

**Note:** Best fits are the FMV-intro and episode-trailer templates.

## Rules
- Use only original or commercially licensed characters, environments and motion in anything released or sold. Studied or teardown material is never a promo input.
- Never invent canon, and never generate a new face for an existing character. Use the owner's own voice only, never a cloned voice.
