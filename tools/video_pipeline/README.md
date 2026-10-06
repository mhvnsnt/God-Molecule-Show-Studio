# God Molecule video_pipeline — reproducible promo production in-repo

Same zero-cost stack as TRIPPEDD / money-machine-hq: promos are build
artifacts, reproducible from a shot list + script. Storyboard first
(owner law) — no procedural bone-wiggling promos, no fake gameplay.

| Tool | Command |
|---|---|
| `promo_assemble.py` | `python3 promo_assemble.py shotlist.json -o promo.mp4` |
| `voiceover.py` (Piper TTS, keyless) | `python3 voiceover.py script.json -o vo.wav` |
| `sfx.py` (12-recipe SFX kit) | `python3 sfx.py --all -d sfx/` |
| `auto_caption.py` (faster-whisper word timestamps) | `python3 auto_caption.py vo.wav -o caps.srt --model-dir ~/workspace/tmp/fw-tiny` |
| `concept_batch.py` (Pollinations storyboards, no key) | `python3 concept_batch.py prompts.txt -d boards/` |

Proven 2026-10-06: `money-machine-hq/pipeline/video/proof/el_toro_recut/el_toro_recut_50s.mp4`
(50.0s @ 1920×1080, titles + captions + VO + music + SFX, frames verified).

Box deps: moviepy 2.1.2, ffmpeg 8.1.2, piper-tts + en_US-lessac-medium,
faster-whisper, Pillow, numpy.
