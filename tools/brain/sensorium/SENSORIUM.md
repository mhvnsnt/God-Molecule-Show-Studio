# Sensorium — The Director's Brain

**Path:** `~/workspace/tools/brain/sensorium/`

Multimodal AI systems that see, hear, and judge together — not as separate pipelines. This is the "director's brain" layer: aesthetic judgment, anomaly detection, and cross-modal reasoning.

## Components

### taste — `aesthetic.py`
Aesthetic quality + Wizard-Gang style-lock scoring per frame.
- **taste** (0..1): general no-reference aesthetic quality
- **style_hold** (0..1): 1.0 = holds 2D cartoon, 0.0 = drifted into 3D/photoreal
- Trained on EP02 AI-slop audit labels (2026-10-09)
- **style_flicker**: std of style_hold over a shot (high = AI texture popping)

### smell — `anomaly.py`
Unsupervised anomaly detection. The episode is its own baseline.
- IsolationForest on visual features (glitch frames, black frames, render failures)
- Temporal pop detection (morph pops, single-frame glitches — classic AI tells)
- Audio anomalies (dropouts, clipping, sudden level jumps)

### sync — `sync.py`
Cross-modal reasoning: does what we SEE match what we HEAR?
- A/V sync via envelope cross-correlation (±1s lag search)
- Flags: "talking head, no speech" (muted/lost dialogue), "speech, frozen face" (disembodied voice)

### multimodal — `multimodal.py`
Vision + audio understood TOGETHER via joint embeddings.
- `joint_similarity()`: "these two moments feel the same" across both modalities
- `cross_modal_search()`: "find me another moment that looks AND sounds like this"
- `coherence()`: does the sound follow the action? (sound design quality check)
- `caption()`: heuristic multimodal captioning

## Usage

```bash
V=~/workspace/tools/ai-qc/venv/bin/python
S=~/workspace/tools/brain/sensorium/sensorium.py

$V $S sense episode.mp4 --t0 50 --t1 70    # full director's-brain pass
$V $S taste frame.png                       # aesthetic score
$V $S sync episode.mp4 120 130              # A/V sync check
$V $S smell episode.mp4                     # anomaly report
$V $S rank                                  # rank EP02 segments by style drift
```

## Integration with ai-qc

The sensorium builds on `~/workspace/tools/ai-qc/` (video_qc, audio_qc). It adds the judgment layer on top of the detection layer:
- **ai-qc**: "who's talking?" / "is there audio here?"
- **sensorium**: "does this look good?" / "does the sound match the picture?" / "something's off here"

## Known limitations

- MediaPipe FaceLandmarker barely fires on cartoon style — sync.py falls back to motion envelopes
- webrtcvad broken in venv — energy-based VAD fallback used
- Style-hold model trained on EP02-specific labels; retrain for other shows
- CPU-only; all models are lightweight (sklearn + numpy + OpenCV)

## Test status

Built and code-reviewed 2026-10-11. Integration tests with ai-qc venv pending full run.
