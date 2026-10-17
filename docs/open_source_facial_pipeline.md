# Open-source facial pipeline decision record

## Purpose

This repo is the character/creative authority. TRIPPEDD remains the executable production, evidence, QC, provenance, and delivery authority. Open-source components are used as implementation tools; none may replace `MARS_CANONICAL`.

## Selected stack

1. **MediaPipe** — primary 478-point facial landmark source for the landmark stage. Use the current MediaPipe Tasks/Face Landmarker path rather than resurrecting unsupported legacy solution APIs.
2. **Blender Rigify** — rig-generation foundation where it fits the actual Mars topology. Do not force a generic metarig onto Mars; topology/weights and semantic eyelid controls must be validated against the real MARS_LOD2 geometry.
3. **OpenSeeFace** — optional independent tracking cross-check for animation stability. It is not the canonical landmark source and must never overwrite the MediaPipe/MVMP evidence.
4. **Rhubarb Lip Sync** — existing audio-to-mouth timing helper in TRIPPEDD. It remains downstream of the actual facial rig and cannot be used to fake a successful blink/eyelid rig.

## Anti-regression rules

- Never substitute `MARS_source.glb`, donor geometry, generated head geometry, or a screenshot-derived mesh for `assets/source_models/MARS_LOD2.glb`.
- Never turn hand-drawn placement marks into canonical landmarks. They are visual constraints for validation only.
- Never declare the rig healthy from telemetry alone. Require human-visible PNG evidence.
- Never let an independent tracker silently redefine canonical landmark identity.
- Keep eyelid upper/lower semantics separate from socket placement and from blink actuation.
- Measure brow and lid placement in the same head frame used for the no-specular/clipping evidence.

## Required production sequence

`MARS_LOD2.glb` → `MVMP 478` → semantic eyelids → eye sockets → face rig → actual blink → PNG evidence → brow/eyelid measurements → PASS/FAIL

## Why these choices

MediaPipe is the authoritative open-source landmark implementation because it is actively maintained and exposes the relevant face-landmark tooling. OpenSeeFace is retained only as an independent stability check because its own documentation explicitly describes its landmarks as optimized for avatar animation rather than exact image fitting. Rhubarb is limited to its existing downstream mouth-timing role.

The operator placement plates in `artifacts/evidence/mars_placement_plates/` are the visual reference layer that all agents should inspect before changing eyelid, brow, socket, or nostril placement.
