# MCP Servers for Creative Work

Research completed 2026-10-10 (retry after daemon restart). Exhaustive survey of Model Context Protocol
servers relevant to creative production: video, audio/music, image, 3D, design, writing, and
media/file management.

**Audience note (owner context):** FREE-FIRST bias. Every entry is marked:
- 🟢 FREE / local / no key needed
- 🟡 Free tier exists (key/credit required; watch usage)
- 🔴 Paid (credits/key required; document only)

Venv for testing: `~/workspace/tools/brain/mcp/venv` (Python 3.12).

---

## 1. Local / free media processing (no API key) — INSTALL PRIORITY

These are the servers you can run right now with zero cost. They cover bread-and-butter
work: resize/convert/crop images, audio convert/merge, markdown-from-anything.

### pixelpanda-mcp 🟢
- **Repo:** https://github.com/longsleevedanaid991/pixelpanda-mcp (also fork https://github.com/johan--/pixelpanda-mcp)
- **What:** 19+ local image tools that run fully offline (resize, crop, rotate, flip,
  grayscale, invert, round-corners, border, compress JPEG/WebP, merge images, format convert,
  opacity, profile-picture maker, blur, brightness/contrast/sharpness/saturation, watermark,
  pixelate, get_image_info) + 4 AI tools free 3 uses/day (bg removal, Real-ESRGAN upscale,
  text removal, image analysis).
- **Install:** `pip install pixelpanda-mcp` / `uvx pixelpanda-mcp`
- **API key:** optional — all local + 3 free AI uses/day work without one.
- **Why it matters:** zero-cost image ops for covers, thumbnails, asset prep. Real-ESRGAN
  upscale is the same model we already use.

### markitdown-mcp (Microsoft) 🟢
- **Repo:** https://github.com/microsoft/markitdown (package `markitdown-mcp`)
- **What:** converts PDF, PPTX, DOCX, XLSX, images (EXIF + OCR), audio (EXIF + transcription),
  HTML, CSV/JSON/XML, ZIP → clean Markdown for LLM context.
- **Install:** `pip install markitdown-mcp`, run `markitdown-mcp` (stdio) or `--http`.
- **Why it matters:** ingest ANY file into agent context — pitch decks, scripts, reference
  docs, audio metadata.

### imagesorcery-mcp 🟢
- **Repo:** https://github.com/sunriseapps/imagesorcery-mcp
- **What:** local image processing + bg removal, draw text/shapes, logos, watermarks, object
  detection and OCR via on-device pre-trained models. Nothing leaves the machine.
- **Why it matters:** privacy-safe image work.

### atx-mcp (gridhra) 🟢
- **Repo:** https://github.com/gridhra/atx-mcp
- **What:** deterministic, non-generative image editing via declarative recipes (crop, mask,
  layer, LUTs, EXIF/GPS strip, encode) saved as immutable revisions. Rust.
- **Why it matters:** reproducible deterministic edits with versioning — useful for
  asset pipelines where you need auditability.

### mcp-ffmpeg (bitscorp-mcp) 🟢
- **Repo:** https://github.com/bitscorp-mcp/mcp-ffmpeg
- **What:** Node server over FFmpeg: video resize, audio extraction, format conversion via
  natural language (built for Claude Desktop).
- **Why it matters:** natural-language video ops if you prefer MCP calling FFmpeg for you.

### maoxiaoke/mcp-media-processor 🟢
- **Repo:** https://github.com/maoxiaoke/mcp-media-processor
- **What:** Node server for advanced video + image processing (conversion, compression,
  editing) over MCP.

---

## 2. Audio / music / voice

### Official ElevenLabs MCP 🟡 (free tier: 10k credits/month)
- **Repo (deprecated local, now hosted):** https://github.com/harishpiyer/elevenlabs-mcp — NOTE: official
  local server is DEPRECATED in favor of the hosted MCP at `https://api.elevenlabs.io/v1/mcp`
  (OAuth, nothing to install).
- **Also:** https://github.com/tolak/elevenlabs-mcp (fork), https://github.com/MisterVitoPro/elevenlabs-mcp
  (adds SFX, speech-to-speech, multi-speaker dialogue, audio isolation, Scribe v2 STT,
  usage tracking — actively maintained community version).
- **What:** TTS, voice cloning, sound effects, voice conversion, transcription, audio isolation.
- **Free?** 10k chars/month free tier. We already use ElevenLabs voices heavily (TTS skill
  installed) — the community MisterVitoPro fork is the most useful: SFX generation + audio
  isolation in one server.

### reaper-mcp (TwelveTake Studios) 🟢 (needs REAPER installed)
- **Repo:** https://github.com/twelvetake-studios/reaper-mcp (v1.8.0, 179 tools, MCP Registry listed)
- **What:** Full REAPER DAW control from AI: mixing, mastering, MIDI composition, tracks,
  FX, routing, automation. Workflow helpers like `setup_sidechain_compression()`,
  `add_mastering_chain()` (ReaEQ→ReaComp→ReaEQ→ReaLimit), `add_parallel_compression()`,
  `create_bus()`, `get_project_summary()`. File-based communication — zero config.
- **Install:** clone + pip install; needs REAPER (free eval, $60 license) with dist API.
- **Free?** Server free; REAPER has generous free evaluation.
- **Why it matters:** the eventual "AI mixing engineer" — mixing/mastering our Suno/voice
  tracks. Suno-MCP author explicitly designed it to pair with reaper-mcp.

### suno-mcp (atomixnmc / seth-c-design fork) 🟡
- **Repo:** https://github.com/atomixnmc/suno-mcp (fork https://github.com/seth-c-design/suno-multi-mcp)
- **What:** real Suno AI integration: login (free tier works), text-prompt music gen,
  lyrics, MP3 download. FastMCP 2.12.
- **Free?** Suno free tier — yes.
- **Install:** clone, pip install.

### suno-hmnn-mcp (Sialki Labs) 🟡
- **Repo:** https://github.com/sialkilabs/suno-hmnn-mcp
- **What:** production-grade Suno bridge for v5.5 Pro/v5/v4: stem isolation
  (vocals/instrumental), 24-bit WAV export, lyrics, MIDI prompts, Clerk token rotation.
  MIT.
- **Free?** Uses your Suno account (free tier works).

### frankxai/suno-mcp-server 🟢 (text-first, no API)
- **Repo:** https://github.com/frankxai/suno-mcp-server
- **What:** prompt-strategy/music-ideation layer — Music DNA, Suno Style field crafting,
  arrangement direction. Does NOT generate audio; prepares high-quality Suno inputs.

### gaudio-developers-mcp 🟡
- **Repo:** https://github.com/gaudiolab-jp/gaudio-developers-mcp
- **What:** Gaudio audio AI API: stem separation (vocals/drums/bass/guitar/piano),
  dialogue/music/effects separation, AI lyrics sync.
- **Free?** API key required (check free tier).

### sound-mcp (SIAM-TheLegend) 🟢
- **Repo:** https://github.com/SIAM-TheLegend/sound-mcp
- **What:** remotely trigger customizable notification sounds via AI agents (npx).
- **Why:** tiny utility — agent notification sounds.

### ableton-vibe 🟢 (needs Ableton)
- **Repo:** https://github.com/androidStern/ableton-vibe
- **What:** MIDI track creation in Ableton Live via MCP.
- **Needs:** Ableton Live running.

### mcp-applemusic 🟢 (macOS only)
- **Repo:** https://github.com/kennethreitz/mcp-applemusic
- **What:** control Apple Music on macOS via AppleScript.

### MushroomFleet/TranscriptionTools-MCP 🟡
- **Repo:** https://github.com/MushroomFleet/TranscriptionTools-MCP
- **What:** transcript formatting, error repair, summarization with LLMs.

---

## 3. 3D / Blender

### ahujasid/mcp-for-blender (community plugin; the famous "Blender MCP") 🟢
- **Repo:** https://github.com/ahujasid/blender-mcp (renamed Sept 2026 to `mcp-for-blender`;
  PyPI package `mcp-for-blender`; `uvx blender-mcp` still works as wrapper). 29k+ stars.
- **What:** 36 tools — scene/object info, viewport screenshot, `execute_blender_code`,
  `describe_node_type`, `bpy_api_lookup`, Poly Haven (free CC0 HDRIs/textures/models),
  Sketchfab, Poly Pizza (low-poly), Hyper3D Rodin text/image-to-3D, Hunyuan3D, Tripo,
  `export_scene` (GLB/FBX).
- **Install:** `uvx mcp-for-blender` + Blender 3.0+ addon (repo install docs).
- **Free?** Free. Optional Premium $10/mo (25 gens) or $20/mo (40+10 high quality) for
  3D gen without own keys.
- **Safety note:** by default model can run ANY Python in Blender; set
  `BLENDER_MCP_SAFE_MODE=1`; 4 CVEs published in 2026 (incl. Poly Haven downloader path
  traversal — fixed). Disable telemetry: `DISABLE_TELEMETRY=true`.
- **Why it matters:** WE HAVE BLENDER at ~/workspace/tools/blender. This is the direct
  bridge for AI-driven 3D asset work in God Molecule / game pipelines.

### blender-mcp-ultra (carlosh7) 🟢
- **Repo:** https://github.com/carlosh7/blender-mcp
- **What:** 239 tools — modeling, texturing, lighting, animation, sim, rendering.
  Headless-ready, Windows/macOS/Linux.
- **Why:** biggest tool surface; compare against mcp-for-blender.

### mcp-blender (rfingadam / hoodtronik / donloquacious) 🟢
- **Repo:** https://github.com/rfingadam/mcp-blender
- **What:** 218 tools — full pipeline coverage (scene, mesh, material, modifiers, animation,
  render, export, baking, geo-nodes, sculpting, rigging, physics) + MSFS 2020/2024 pipeline
  + AI 3D gen multi-backend (Hyper3D Rodin, Meshy, Tripo, TripoSR-local, Stable Fast 3D,
  Hunyuan3D-local, ComfyUI) + Poly Haven built-in + self-refinement loop
  (render→analyze→refine against Ollama vision). MIT.

### Official Blender Lab MCP (Blender Foundation) 🟢
- **Distribution:** https://github.com/bpy-dev/blender-mcp (independent enhanced dist)
- **Docs:** blender.org/lab/mcp-server
- **What:** official, deliberately minimal — Blender addon + MCP server over TCP socket.
  The "safe" foundation option.

### tripo-mcp (VAST-AI-Research, official, alpha) 🟡
- **Repo:** https://github.com/VAST-AI-Research/tripo-mcp (v0.1.2 alpha)
- **What:** Tripo text-to-3D / image-to-3D as MCP (runs alongside BlenderMCP).
- **Free?** Tripo has free tier (300 credits to start).

---

## 4. Image / video / music generation (API-backed gateways)

### kie-cli-mcp (stuivertjep) 🟡
- **Repo:** https://github.com/stuivertjep/kie-cli-mcp
- **What:** CLI + MCP over kie.ai — cheapest market rates: Nano Banana Pro, Veo 3,
  Runway Aleph, Suno V5, ElevenLabs, Seedance, Seedream, Qwen, Flux, Wan, Midjourney,
  OpenAI Image 2. Async tasks, SQLite tracking, `wait_for_task`, prompts/resources.
- **Install:** npm/pip; needs KIE_API_KEY.
- **Why:** single key for ~everything generative. We already use Pollinations (free)
  for images — kie is the paid-upgrade path.

### mediamcp (legolev) 🟡
- **Repo:** https://github.com/legolev/mediamcp
- **What:** image gen/edit + Veo, Sora, Seedance video via OpenRouter / OpenAI-compatible
  APIs, resumable video jobs.

### atlascloudai/mcp-server 🟡
- **Repo:** https://github.com/atlascloudai/mcp-server
- **What:** aggregated API — image/video/3D/music/TTS/STT + balance tracking, dry_run
  flags, generation history. Suno, Seedance, Kling, Veo 3.1, Hunyuan 3D, ElevenLabs...

### kolbo-mcp 🟡
- **Repo:** https://github.com/zoharvan12/kolbo-mcp
- **What:** creative media suite: images (GPT Image, Nano Banana, Flux), video
  (Seedance, Veo, Kling, Hailuo), music (Suno), TTS (ElevenLabs), 3D, transcription,
  Visual DNA character consistency, Marketing Studio.

### pixazo-mcp 🟡
- **Repo:** https://github.com/Absgirdhar/pixazo-mcp
- **What:** 127 models — image, video, music, speech, 3D, upscaling, virtual try-on.
  Per-model servers (Nano Banana, Seedance, Runway, Flux).
- **Connect:** `claude mcp add pixazo https://gateway.pixazo.ai/pixazo/mcp` (OAuth;
  free to connect, usage billed at REST rates).

### Ace Data Cloud remote servers 🟡
- **URLs:** `https://suno.mcp.acedata.cloud/mcp`, `https://flux.mcp.acedata.cloud/mcp`,
  `https://seedream.mcp.acedata.cloud/mcp`, `https://nanobanana.mcp.acedata.cloud/mcp`,
  `https://luma.mcp.acedata.cloud/mcp`, `https://veo.mcp.acedata.cloud/mcp`,
  `https://seedance.mcp.acedata.cloud/mcp`
- **What:** zero-install hosted MCP endpoints (one Authorization header) for music,
  image, video gen.

### remotion-media-mcp 🟡
- **Repo:** https://github.com/ja3ooni/remotion-media-mcp — `npm install -g remotion-media-mcp`
- **What:** images (Nano Banana Pro), video (Veo 3.1), music (Suno V3.5–V5), SFX
  (ElevenLabs SFX V2), TTS (ElevenLabs), subtitles (local Whisper → SRT), asset library
  with optional Airtable.
- **Why:** built for Remotion video projects — matches our video-production lane.

### mcp-genmedia (Google Cloud Platform, official) 🔴
- **Repo:** https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio (experiments/mcp-genmedia)
- **What:** Go MCP servers for Gemini Image, Gemini TTS, Gemini Transcribe, Veo
  (video), Gemini Omni, Lyria (music), Chirp 3 HD, AVTool (ffmpeg compositing/conversion).
- **Needs:** Google Cloud project + ADC auth (paid).
- **Note:** Imagen servers dead since 2026-08-17.

### glif-mcp-server (official, hosted) 🟡
- **Repo:** https://github.com/glifxyz/glif-mcp-server
- **What:** official hosted agent from Glif: image, video, audio gen, transcription,
  chained multi-step workflows. Endpoint `https://glif.app/api/mcp`, OAuth 2.1, MIT.
- **Why:** we already use Glif agents in production (video pipelines) — this exposes
  them as MCP tools.

### GMKR/mcp-imagegen 🟡
- **Repo:** https://github.com/GMKR/mcp-imagegen — Together AI image gen via MCP.

### tomcat65/flux-images-mcp 🟡
- **Repo:** https://github.com/tomcat65/flux-images-mcp — Replicate Flux models: gen,
  modify, inpaint, browse stored images.

### CLOUDWERX-DEV/DiffuGen 🟢 (local Stable Diffusion)
- **Repo:** https://github.com/CLOUDWERX-DEV/DiffuGen — Stable Diffusion image gen via MCP
  in IDEs. Local = free (GPU needed).

### lalanikarim/comfy-mcp-server 🟢 (local ComfyUI)
- **Repo:** https://github.com/lalanikarim/comfy-mcp-server — generate images via remote
  ComfyUI server (FastMCP). Free if you run your own ComfyUI (we can — Kaggle/Colab).

### dali-mcp 🟢 (no API)
- **Repo:** https://github.com/Lulu-The-Narwhal/dali-mcp — score/rewrite image/video gen
  prompts (Veo 3, Sora, Kling, Midjourney, Flux) before generating. No key.

### clipy-mcp 🟢 (read-only)
- **Repo:** https://github.com/manovagyanik1/clipy-mcp — read-only access to Clipy screen
  recordings: search library, timestamped transcripts, AI summaries, key moments + frames.

### ytrnscrpt-mcp-server 🟢 + mcp-youtube-transcript (jkawamoto) 🟢
- **Repos:** https://github.com/index01d/ytrnscrpt-mcp-server, jkawamoto/mcp-youtube-transcript
- **What:** fetch/analyze YouTube transcripts via MCP. Free.
- **Why:** research lane (study creators, transcribe references).

---

## 5. Design

### Figma official MCP 🟢
- **Docs:** https://developers.figma.com/docs/figma-mcp-server/ — remote MCP server;
  pulls design context into code, generates design layers from VS Code; all Figma
  seats/plans. MCP catalog: https://www.figma.com/mcp-catalog/
- **Community:** https://github.com/ShiXiangYu1/Figma-Context-MCP (`npx figma-developer-mcp`).

### Canva MCP (official) 🟡
- **Docs:** https://www.canva.dev/docs/mcp/ — asset/design creation and collateral.

### Remotion MCP (official docs/context) 🟢
- **Docs:** https://www.remotion.dev/docs/ai/mcp
- **What:** Remotion-specific docs/context server — pairs with Remotion code video.

---

## 6. Writing / publishing

### book-writer-mcp 🟢
- **Repo:** https://github.com/arupmaity1/book-writer-mcp
- **What:** AI book/manuscript writing: story bible, style guide, continuity checker,
  HTML preview, KDP export (Markdown/DOCX), cover design specs, author bios.
- **Why:** OTTR books, lore bibles, show bibles.

### mcp-agent-docparser 🟢
- **Repo:** https://github.com/christofmilius/mcp-agent-docparser
- **What:** local MCP — fetch docs sites, strip nav, convert HTML→clean markdown for
  LLM context. Receipts for common stacks (React, MCP spec, Pydantic AI, etc.).

---

## 7. Media / file management & utilities

### motion-mcp (digitopvn) 🟢
- **Repo:** https://github.com/digitopvn/motion-mcp
- **What:** video pipeline skills/registry (hyperframes) — 21 skills, 164 scene blocks,
  223 components. No MCP server package itself (uses HeyGen hosted OAuth MCP beta).

### botverse-mcp (MkTurner74) 🟡
- **Repo:** https://github.com/MkTurner74/botverse-mcp
- **What:** video transcoding (MP4/WebM/ProRes/GIF/MP3) + doc conversion
  (PDF/DOCX/HTML/MD/XLSX) without AWS/FFmpeg setup.

### mcp-mistral-ocr (everaldo) 🟡
- **Repo:** https://github.com/everaldo/mcp-mistral-ocr — OCR on images/PDFs via
  Mistral AI (local + URL files).

### mcp-florence2 (jkawamoto) 🟢
- **Repo:** https://github.com/jkawamoto/mcp-florence2 — image/PDF captioning + text
  extraction with Florence-2 (local model, free).

### apple-intelligence-mcp (macOS only) 🟢
- **Repo:** https://github.com/falll2000/apple-intelligence-mcp
- **What:** 21 tools from macOS 26 on-device stack (Foundation Models, Vision, Speech,
  NL). 100% local, zero API cost. Not applicable to our Linux VM.

### dmmdea/offload-harness 🟢
- **Repo:** https://github.com/dmmdea/offload-harness
- **What:** free local Gemma cascade via llama.cpp + MCP: summarization/OCR/vision/
  whisper STT/image-audio-video GEN (HiDream-O1/SDXL, Wan 2.2, Chatterbox TTS via ComfyUI),
  SVG viz kit. Single Go binary. Interesting all-in-one local creative box — but heavy.

---

## 8. Awesome lists (keep for future mining)

- https://github.com/keysersoft/awesome-mcp-servers-2 (multimedia-processing.md)
- https://github.com/itswadesh/awesome-mcp-servers (multimedia-processing.md)
- https://github.com/unlockbillions/awesome-mcp-servers

---

## Installation test results (venv: `~/workspace/tools/brain/mcp/venv`, Python 3.12, 2026-10-10)

Harness: `~/workspace/tools/brain/mcp/mcp_test.py` — MCP stdio handshake
(initialize → notifications/initialized → tools/list).

| Server | Installed | Test result | Notes |
|---|---|---|---|
| **pixelpanda-mcp** 0.1.3 | ✅ pip | ✅ PASS — 32 tools listed; `tools/call get_image_info` on a real PNG returned correct dimensions/format | Functional call verified end-to-end. |
| **mcp-for-blender** 2.1.9 | ✅ pip | ✅ PASS — 9 tools listed (get_addon_status, disable_telemetry, get_scene_info, execute_blender_code, record_trajectory_feedback, look, generate_3d, search_assets, import_asset) | 2.x consolidated from 36 → 9 tools. Needs Blender addon running for live scene tools. |
| **markitdown-mcp** 0.0.1a3 | ✅ pip | ❌ FAIL — server hangs on startup (no response to initialize after 3+ min); also hangs on `--help` | Alpha bug. Library CLI (`markitdown` cmd, audamcp backend) works fine standalone — use that instead of the MCP wrapper. |
| **elevenlabs-mcp** 0.12.2 | ✅ pip | ⚠️ NOT TESTABLE — server refuses to boot without `ELEVENLABS_API_KEY` env var (ValueError at import) | Expected; needs the user's real key. Use with the key from their existing ElevenLabs setup. |

**Install config snippets** (for any MCP client, e.g. Claude Desktop config):

```json
{
  "mcpServers": {
    "pixelpanda": {
      "command": "/home/hatch/workspace/tools/brain/mcp/venv/bin/pixelpanda-mcp"
    },
    "blender": {
      "command": "/home/hatch/workspace/tools/brain/mcp/venv/bin/mcp-for-blender",
      "env": { "DISABLE_TELEMETRY": "true", "BLENDER_MCP_SAFE_MODE": "1" }
    },
    "elevenlabs": {
      "command": "/home/hatch/workspace/tools/brain/mcp/venv/bin/elevenlabs-mcp",
      "env": { "ELEVENLABS_API_KEY": "<key>" }
    }
  }
}
```

**Disk note:** installs stopped when disk hit 90%. venv total size ~600MB (mostly the
pre-existing numpy/scipy/numba audio stack from the prior worker; new packages add ~100MB).
Do NOT install more here until the disk-guardian cron runs its save-then-clean cycle.
Priorities if installing later: `kie-cli-mcp` (npm) for cheap gen-API access, reaper-mcp
for the DAW lane, suno-mcp for music.

## Recommended adoption order (for this operation)

1. **pixelpanda-mcp** — now, free, zero config. Image ops for covers/thumbnails/assets.
2. **mcp-for-blender** — now, free. Pairs with our Blender install for AI 3D asset work.
3. **elevenlabs-mcp** — add key → TTS/voice cloning/SFX as MCP tools (we already pay in
   usage; the free tier is 10k chars/mo).
4. **kie-cli-mcp** — when budget allows (cheapest per-call gen API aggregator:
   Nano Banana Pro, Veo 3, Suno V5, Flux...).
5. **reaper-mcp** — when REAPER is available on a workstation; the AI mixing engineer lane.
6. **glif-mcp-server** — zero-install, OAuth — exposes our existing Glif agents as MCP tools.
