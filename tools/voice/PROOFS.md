# PROOFS — voice tools (kokoro + piper)

Date: 2026-10-07. venv: `~/workspace/venvs/respull`.

## kokoro (WIRED)

- `pip install kokoro soundfile` — OK (Kokoro-82M, Apache-2.0).
- Weights (~330MB: `kokoro-v1_0.pth` + `config.json` + `voices/af_heart.pt`,
  hexgrad/Kokoro-82M) — downloaded via curl (the sandbox proxy stalls
  `huggingface_hub`/httpx streaming downloads) and placed into a
  hand-built HF cache at `~/workspace/tmp/respull-scratch/hf`
  (`HF_HUB_OFFLINE=1` for the run). Also note: the sandbox `no_proxy`
  IPv6 literals crash httpx — strip `::` entries before any HF download
  (see `~/TOOLS.md`).
- Smoke test:

      HF_HUB_OFFLINE=1 python3 kokoro_voice.py \
        "The council does not explain itself. It declares." -o kokoro_test.wav

- Result: `kokoro_test.wav` — **3.55s @ 24kHz**, voice `af_heart`.
  Audio verified real speech (`volumedetect`: mean −26.6 dB, max −10.2 dB).
- Hash: `1868854d80c399e8f2df7cbe91d16aeff3f10fc54dd235bb07f9af75e5e41d13`

## piper (WIRED)

- `pip install piper-tts` — OK (piper-tts 1.8.0, **GPL-3.0** — standalone
  local process, quarantined per program `docs/LICENSE_QUARANTINE.md`).
- Voice: `en_US-lessac-medium.onnx` (63MB) downloaded via
  `python3 -m piper.download_voices` into `models/` (first download was
  truncated by the proxy → `InvalidProtobuf`; re-downloaded with curl
  resume and verified loadable by onnxruntime).
- Smoke test:

      python3 piper_voice.py "The council does not explain itself. It declares." \
        -o piper_test.wav

- Result: `piper_test.wav` — **3.05s @ 22050Hz**. Audio verified real
  speech (`volumedetect`: mean −15.5 dB, max −0.0 dB).
- Hash: `517caf9ec6e08a60c61a9ea71ae283e7ba67a598e29f253e014b7c1093a679cd`
