# God Molecule voice tools — character voices (all keyless, local, free)

Two TTS engines wired for character line reads. No API keys, no accounts,
no cloud — everything runs on the box.

## Tools

| Tool | Command | Notes |
|---|---|---|
| `kokoro_voice.py` | `python3 kokoro_voice.py "TEXT" -o line.wav` | Kokoro-82M (Apache-2.0). ~300MB weights download once to `$HF_HOME`. 24kHz WAV. Multiple US/UK voices. |
| `piper_voice.py` | `python3 piper_voice.py "TEXT" -o line.wav` | Piper (fast, low-RAM). Voice `.onnx` in `models/`. 22kHz WAV. |

## Setup

```bash
source ~/workspace/venvs/respull/bin/activate
pip install kokoro soundfile piper-tts
# kokoro weights (~300MB, one-time):
HF_HOME=~/workspace/tmp/respull-scratch/hf python3 kokoro_voice.py "test" -o /tmp/t.wav
# piper voice model (~60MB, one-time):
mkdir -p models && cd models
python3 -m piper.download_voices en_US-lessac-medium
```

## Usage

```bash
python3 kokoro_voice.py "The council does not explain itself. It declares." \
    -o council_line.wav
python3 kokoro_voice.py "Line one." --voice af_bella --speed 0.95 -o line1.wav
python3 kokoro_voice.py script.txt --file -o vo.wav

python3 piper_voice.py "The council does not explain itself. It declares." \
    -o council_piper.wav
python3 piper_voice.py "..." -o slow.wav --length-scale 1.25
```

Kokoro voices: `af_heart af_bella af_nicole af_sarah am_adam am_michael`
(US, `--lang a`); `bf_emma bf_isabella bm_george bm_lewis` (UK, `--lang b`).

## License notes

- Kokoro: Apache-2.0 — safe to prototype and ship.
- Piper (`piper-tts`): **GPL-3.0** — runs as a separate local process, never
  linked into shipping code. Stays quarantined per the program's
  `docs/LICENSE_QUARANTINE.md` until a license audit clears it (owner law).
  The pre-existing `voiceover.py` in the video_pipeline dirs uses it the same way.

## Proof

`PROOFS.md` — smoke-test commands, artifact hashes.
