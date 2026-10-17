# Autonomous Studio Vision + Tool Contract

Agents receive actual rendered images through MCP ImageContent and durable artifact references. Vision-capable cloud models (GPT, Claude, Gemini, Grok) remain provider adapters; Qwen3-VL is the local open-source vision backend. Open WebUI is the visual workspace and ComfyUI is the generative-media workspace.

Every image artifact records sha256, source job/run, canonical asset identity, camera/view, frame number, dimensions, timestamp, provenance and QC status. Text claims never substitute for pixels.

Tool families: filesystem/workspace, GitHub operations, allowlisted shell, Blender/render, FFmpeg/ffprobe, OpenCV/PySceneDetect/Tesseract/Whisper, ComfyUI, image inspection, contact sheets, evidence validation, and sandboxed browser/research.

Never commit model/API/GitHub/Drive/private-repository secrets.