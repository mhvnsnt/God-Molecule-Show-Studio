# Production log — 2026-09-11 Oral pipeline fixes acknowledged (Grok)

ChatGPT landed real fixes on TRIPPEDD (verified in source):

| Commit | Fix |
|--------|-----|
| `60e21a38` | Lip plane uses measured **Y-depth** (not Z-facing fallback) |
| `bd764b38` | Explicit **teeth/gums** from donor masks as renderable objects |
| `1a1549c0` | Survey: **shell excluded** from aperture denominator / protrusion |
| `d031c395` | Survey CLI **`--output`** contract |

Grok runner already calls `--output` (not `--output-json`). Human-review checklist updated to demand distinct teeth/gums vs pink slab.

**Still true:** no Blender/Mars binary in this agent session → no visual PASS claim. Next proof is four views + survey JSON from a real render worker.

Bridge manifest bumped to v4 with oral notes + head pins.
