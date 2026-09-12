# World Visual Language v1

The canonical world-color contract lives at `config/world_visual_language.json`.

## Authority

The schema identifier is:

`trippedd.world-visual-language/v1`

The production renderer, Rocket-compatible control plane, and future Blender/MCP adapters must consume this contract rather than maintaining independent palette constants.

## Episode 1

`EP01_MARS_AWARENESS` uses world seed `742918` and the event `MARS_EYE_CONTACT`.

The intended progression is:

`neutral_white` → `cosmic_blue` → `mars_awakened` → `violet_dream` → `world_transition`

Direct eye contact is the narrative trigger for the visible change in starfield and atmosphere.

## Renderer rule

A profile is a deterministic parameter set, not a final image. Rendering remains responsible for producing real pixels. The control plane must report `IMAGE_UNAVAILABLE`, `QC_PENDING`, `FAILED`, or `BLOCKED` when the corresponding evidence does not exist.

## OSS integration boundary

OpenImageIO/OpenEXR remain artifact-inspection tools; Blender remains scene/render execution truth; OpenCue remains optional dispatch infrastructure; OpenRV/xSTUDIO remain review surfaces. None becomes a second production authority.

## Mars performance

Facial animation is downstream of the same production graph and should eventually consume typed controls for blinking, gaze, eyebrows, nostrils, jaw/mouth, expression, speech/lip-sync, breathing and hair secondary motion.
