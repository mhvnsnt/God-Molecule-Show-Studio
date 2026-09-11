# Production Conversation Log — 2026-09-11 (Oral protrusion gate)

**Logged by:** Grok (xAI)  
**Repo:** mhvnsnt/TRIPPEDD-Production-studios-

## Problem

Survey reported teeth/gum/tongue at 0% while renders showed a pink object in the mouth. Profile confirmed a pink plank past the lips. Rays hit cavity material in front of the aperture plane.

**Placement bug, not missing anatomy.** GNM oral donor exists; mouth_sock/cavity liner sat in front of the measured lip plane.

## Fix (ready to commit)

### tools/character/build_mars_oral_bridge.py
- Explicit lip plane from measured mouth frame
- Recess every oral donor mesh behind the plane (`--recess`, default 0.008)
- Inward-only solidify on cavity cutter (`offset=-1`)
- PROTRUSION_FAIL if any oral mesh/cutter crosses the lip plane

### tools/character/survey_oral_aperture.py
- Per-object protrusion measurement
- Anatomy fractions only for rays that clear the lip plane
- Cavity-in-front-of-plane counted as protrusion, not missing teeth

## Gate

PASS only when protrusion_gate=PASS, open profile shows cavity behind lips, and human reviews the contact sheet.

## Identity

MARS_CANONICAL never replaced.
