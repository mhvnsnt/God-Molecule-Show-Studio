# Free AI Model APIs — tested 2026-10-10/11

Every entry below was tested with a **real API call from this VM**. Nothing
is listed as working unless a call returned real output. $0 only, no credit
cards anywhere.

Wrappers live in this directory; each module is stdlib-only (`urllib`) plus
the `dynamic_credentials` surrogate helper for connected credentials — no
raw keys are ever stored or printed.

## ✅ WORKING — wired up

### Pollinations.ai — `pollinations.py` (anonymous, no signup, no key)
| Capability | Function | Test result |
|---|---|---|
| Text / chat | `text(prompt)` | ✅ returned text (legacy `text.pollinations.ai`) |
| Text-to-image | `image(prompt)` / `save_image()` | ✅ 768×768 JPEG downloaded, verified with ffprobe |
| Text-to-speech | `tts(text)` / `save_tts()` | ✅ real 1.46s MP3 from `gen.pollinations.ai/audio` |
| Multimodal / vision (reasoning) | — | via `text()` with vision-capable model names |
| Rate limit | ~1 anonymous req / 15s |

### Groq — `groq_provider.py` (free tier, connected `custom.groq` credential)
| Capability | Function | Test result |
|---|---|---|
| Chat | `chat()` / `ask()` | ✅ `openai/gpt-oss-20b` returned exact expected string |
| Speech-to-text | `transcribe(path)` | ✅ `whisper-large-v3-turbo` perfectly transcribed test clip |
| Models (2026-10-11) | `list_models()` | gpt-oss-20b/120b, qwen3.8-27b, allam-2-7b, whisper-large-v3(-turbo), orpheus TTS ×2, prompt-guard |
| Free limits | ~30 RPM / 1K req/day chat; ~20 RPM / 2K req/day Whisper |
| Note | No vision models currently exposed on Groq free tier |
| Quirk | `gpt-oss` models are reasoning models: keep `max_tokens` generous (default 1024). With a tiny budget (e.g. 20–50) all tokens go to reasoning and `content` returns empty with `finish_reason: length` |

### Mistral — `mistral_provider.py` (free tier $10/mo credits, connected `custom.mistral`)
| Capability | Function | Test result |
|---|---|---|
| Chat | `chat()` / `ask()` | ✅ `open-mistral-nemo`, `mistral-tiny-latest` returned expected output |
| Note | `mistral-small-latest` hit 429 at test time — free-tier per-minute cap |

### AI Horde — `ai_horde.py` (free crowdsourced GPUs, connected `custom.ai-horde`)
| Capability | Function | Test result |
|---|---|---|
| Text-to-image | `generate_image()` | ✅ job submitted, completed instantly, real 512×512 WebP downloaded & verified |
| Account | Mhvnsnt#544274, 0 kudos — still worked |

### Local / keyless voice — `local_voice.py` (no accounts at all)
| Capability | Function | Test result |
|---|---|---|
| TTS (robotic, offline) | `espeak_tts()` | ✅ 1.8s WAV, ffprobe-verified |
| TTS (natural-ish) | `google_tts()` | ✅ keyless Google Translate TTS, 2.6s MP3 verified |
| Speech-to-text | `transcribe()` | ✅ faster-whisper `tiny`, perfect transcript of test clip |
| Quirk | `no_proxy` IPv6 entries crash huggingface_hub — stripped automatically in module |

## ❌ TESTED, NOT WORKING (documented so nobody retries blindly)

| API | Result |
|---|---|
| Groq Orpheus TTS | 400 `model_terms_required` — org admin must accept terms at console.groq.com first |
| Mistral OCR (`mistral-ocr-latest`) | 429 rate-limited at test time — NOT verified working |
| Vercel AI Gateway | 403 — requires a credit card on file even for free credits |
| edge-tts (Microsoft) | pip-installed fine, but the websocket handshake is mangled by this VM's egress proxy (`WSServerHandshakeError 101`) — may work on other networks |
| DuckDuckGo duckchat | No `x-vqd-4` token issued from this network — dead end |
| Pollinations video (`gen.pollinations.ai/video`) | 401 — API key required (signup at enter.pollinations.ai) |
| Pollinations vision via `gen.pollinations.ai/v1/chat/completions` | 401 — API key required |
| AI Horde text generation | Submitted OK, returned EMPTY text — unreliable, no wrapper |

## 📝 NEEDS SIGNUP (not tested — no key available to test with)

| API | Free terms | Why untested |
|---|---|---|
| Google Gemini (AI Studio) | Free tier, no card, 1M context, vision+audio+video | Needs API key from aistudio.google.com (browser OAuth flow — not doable headless) |
| OpenRouter `:free` models | ~21 free models, no card; 50 req/day until $10 credit purchase | Needs account + API key |
| Cerebras | Free tier, very fast, no card | Needs account + API key |
| LLM7.io | 100K tokens/day free token | Needs free token from dash.llm7.io |
| NVIDIA NIM | Free preview models | Needs verified NVIDIA account + key |
| Hugging Face Inference | Free tier effectively $0.10/mo (dead for real use); ZeroGPU exists | Needs user token; not wired |
| Puter.js | "User-pays", keyless in browser | Requires browser consent dialog — can't call server-side |
| OnlyMusic / Sonauto | 5 free songs no-signup | Web UI only, no API |

## Quick start

```python
from pollinations import text, save_image, save_tts
from groq_provider import ask, transcribe as groq_stt
from mistral_provider import ask as mistral_ask
from ai_horde import generate_image
from local_voice import espeak_tts, google_tts, transcribe as local_stt

print(ask("Summarize this plot beat in one line: ..."))
save_image("wizard in a neon swamp, cartoon style", "/tmp/shot1.jpg")
save_tts("Damn, shit's wild.", "/tmp/line1.mp3", voice="nova")
print(groq_stt("/tmp/line1.mp3"))
```

Run all smoke tests: `python3 test_all.py`

## Environment notes
- All HTTP calls send a browser User-Agent: Groq/Mistral edges return
  Cloudflare 1010 to default Python UAs from this VM.
- Connected credentials (`custom.groq`, `custom.mistral`,
  `custom.ai-horde`) resolve via authd surrogates at request time — wrappers
  never see raw keys. If a 401/403 appears, check the request carried the
  surrogate before assuming the key is bad.
