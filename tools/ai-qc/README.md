# AI-QC Toolkit

Gives AI agents actual perceptual understanding of video/audio — no more
"verified" after checking 2 frames.

## Quick start

```bash
V=~/workspace/tools/ai-qc/venv/bin/python
Q="$V ~/workspace/tools/ai-qc/qc.py"

# Who's on screen + are they talking at 2:05?
$Q who episode.mp4 125

# Is the voice at 4:16-4:22 really Cipher's?
$Q voice episode.mp4 256 262 cipher

# Full audit: silence gaps, talking regions, speaker clusters
$Q audit episode.mp4
```

## What it does

| Command | Tool | What it catches |
|---------|------|-----------------|
| `qc.py who <v> <t>` | MediaPipe FaceLandmarker | Who's on screen, is their mouth moving |
| `qc.py voice <v> <t0> <t1> <char>` | Voice classifier (MFCC+pitch+spectral) | Wrong voice on a line (e.g. Static's voice on Cipher's line) |
| `qc.py audit <v>` | All of the above | Silence gaps, talking-with-no-audio, speaker changes |

## Voice model

`audio_qc.VoiceModel` — per-character classifier built from reference
samples in `~/workspace/voice-delivery/voice-<char>-*.mp3`.
Validated 15/16 on reference set (the 1 miss was a narrator file
misclassified by the test harness's filename heuristic, not the model).

Characters with references: static, cipher, sombra, narrator.
Add new voices by dropping `voice-<name>-*.mp3` files in voice-delivery/.

## Individual modules

- `audio_qc.py` — speech activity (webrtcvad), energy-based silence gaps,
  MFCC speaker clustering, VoiceModel classifier
- `video_qc.py` — mouth openness via MediaPipe FaceLandmarker (478 pts),
  talking regions, scene-change detection, face counting

## Tested on

EP02 v6e (2026-10-10):
- Cipher C1 at 256s → correctly identified as cipher
- L7 at 113s → correctly identified as static (not cipher) — catches the
  "wrong voice" class of bug automatically
- Cipher money scene at 125s → 1 face, mouth open (talking confirmed)
- Silence gaps correctly found at scene transitions

## Requirements

Self-contained venv at `venv/` (librosa, webrtcvad, scikit-learn,
opencv-python, mediapipe). Model at `models/face_landmarker.task` (3.7MB).

No torch, no GPU, no API keys needed. Runs on CPU in seconds.

## Not yet wired (needs GPU/cloud)

- Wav2Lip / SadTalker (automated lip-sync) — use via cloud GPU
- pyannote.audio (neural diarization) — needs torch + HF token
- RIFE (frame interpolation) — needs GPU
These are documented for when cloud GPU is available.
