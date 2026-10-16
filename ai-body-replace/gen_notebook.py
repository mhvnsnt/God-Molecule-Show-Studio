#!/usr/bin/env python3
"""Generate cape_jones_viggle_kaggle.ipynb — Kaggle GPU T4 Viggle-Animate
AI body replacement notebook.

WHAT THIS DOES:
    driving video (you doing motion) + reference image (Cape Jones)
    → Cape Jones performing YOUR motion. Free, unlimited, no paywall.

WHY: The owner was hitting Viggle's paywalls — login required, video limits,
24-hour waits. Viggle-Animate went open-source in 2026 (33.1B MiniMax-H3
finetune). This notebook runs it on his own Kaggle T4 GPU.

HOW IT WORKS:
    1. Installs ComfyUI + Viggle-Animate custom nodes on Kaggle
    2. Downloads quantized models (pruned INT8 = 21GB, fits T4 with offloading)
    3. User uploads: driving_video.mp4 + character.png (via notebook file upload)
    4. Runs the Viggle-Animate workflow via ComfyUI API (headless)
    5. Outputs: character performing the motion → /kaggle/working/

MODELS (all from HuggingFace, downloaded on Kaggle — never locally):
    - diffusion: drbaph/Viggle-Animate-ComfyUI → minimax_h3_ref2va_viggle_pruned_int8_convrot.safetensors (21GB)
    - lora:      drbaph/Viggle-Animate-ComfyUI → viggle_animate_dmd_lora_r64.safetensors (0.94GB, recommended)
    - text_cond: drbaph/Viggle-Animate-ComfyUI → text_cond/fixed_embed_fwd_anyframe.safetensors
    - vae:       Kijai/MiniMax-H3-experimental → minimax_h3_video_vae_int8_convrot.safetensors (3.17GB, low VRAM)

Total download: ~25GB. Kaggle has fast bandwidth, takes ~10-15 min.

VRAM: T4 has 16GB. The pruned INT8 model + CPU offloading works but is slow.
Expect ~5-10 min for a 124-frame clip (5 sec @ 24fps). Longer clips use the
chunked workflow.

Upload the .ipynb to Kaggle's notebook editor (browser lane).
"""
import json

BRANCH = "ai-body-replace"
RAW = (f"https://raw.githubusercontent.com/mhvnsnt/cape-jones/"
       f"{BRANCH}/production/ai-body-replace")


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def code(src):
    return {"cell_type": "code", "metadata": {},
            "execution_count": None, "outputs": [], "source": src}


cells = [
md("""# Cape Jones — Viggle-Animate AI Body Replacement on Kaggle T4 GPU

**What this does:** You upload a video of yourself doing something + a picture of Cape Jones → the notebook puts Cape Jones on your body, doing your exact motion. **Free. Unlimited. No paywall. No 24-hour wait.**

**Before running:** Settings (right panel) → **Accelerator: GPU T4 x2**, **Internet: ON**. Then **Run All**.

**How to use (dead simple):**
1. Run all cells below (takes ~20 min first time — downloads models)
2. When you see **"👆 UPLOAD YOUR FILES HERE"**, upload:
   - `driving_video.mp4` — video of YOU doing the motion (keep it under 10 sec)
   - `character.png` — picture of Cape Jones (or any character)
3. Run the last cell → get your video back

**Pipeline in this notebook:**
1. GPU check (must be Tesla T4)
2. Install ComfyUI + Viggle-Animate custom nodes
3. Download quantized models from HuggingFace (~25GB, ~10-15 min)
4. ⏸️ **YOU upload driving_video.mp4 + character.png**
5. Run Viggle-Animate workflow (character replacement)
6. Output video → `/kaggle/working/cape-jones-body-replace.mp4`
"""),

code('''# === Cell 1: GPU check ===
import subprocess
r = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                    "--format=csv"], capture_output=True, text=True)
print(r.stdout.strip() or "NO GPU VISIBLE -- enable Accelerator: GPU in Settings!")
assert "Tesla T4" in r.stdout, "Expected a Tesla T4"
print("\\n✅ T4 confirmed. Let's build your body-replacement studio.")
'''),

code('''# === Cell 2: Install ComfyUI + Viggle-Animate nodes ===
import subprocess, sys, os

COMFY = "/kaggle/working/ComfyUI"
if not os.path.isdir(COMFY):
    print("Cloning ComfyUI...")
    subprocess.run(["git", "clone", "--depth", "1",
                    "https://github.com/comfyanonymous/ComfyUI.git", COMFY],
                   check=True)
else:
    print("ComfyUI already cloned.")

print("Installing ComfyUI deps (this takes a few minutes)...")
subprocess.run([sys.executable, "-m", "pip", "-q", "install",
                "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cu121"],
               check=True)
subprocess.run([sys.executable, "-m", "pip", "-q", "install", "-r",
                os.path.join(COMFY, "requirements.txt")], check=True)

# Viggle-Animate custom nodes
NODES = os.path.join(COMFY, "custom_nodes")
VIGGLE_NODES = os.path.join(NODES, "ComfyUI-Viggle-Animate-H3")
if not os.path.isdir(VIGGLE_NODES):
    print("Cloning Viggle-Animate custom nodes...")
    subprocess.run(["git", "clone", "--depth", "1",
                    "https://github.com/Saganaki22/ComfyUI-Viggle-Animate-H3.git",
                    VIGGLE_NODES], check=True)
else:
    print("Viggle-Animate nodes already cloned.")

# Video Helper Suite (for loading/saving video in ComfyUI)
VHS = os.path.join(NODES, "ComfyUI-VideoHelperSuite")
if not os.path.isdir(VHS):
    print("Cloning Video Helper Suite...")
    subprocess.run(["git", "clone", "--depth", "1",
                    "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git",
                    VHS], check=True)
    subprocess.run([sys.executable, "-m", "pip", "-q", "install", "-r",
                    os.path.join(VHS, "requirements.txt")], check=True)
else:
    print("Video Helper Suite already cloned.")

print("\\n✅ ComfyUI + nodes installed.")
'''),

code('''# === Cell 3: Download Viggle-Animate models from HuggingFace (~25GB) ===
# These go to /kaggle/working/ — NOT to your local machine. Kaggle has fast bandwidth.
import subprocess, os

BASE = "/kaggle/working/ComfyUI/models"
DMODEL = os.path.join(BASE, "diffusion_models")
LORA = os.path.join(BASE, "loras")
TCOND = os.path.join(BASE, "text_cond")
VAE = os.path.join(BASE, "vae")
for d in [DMODEL, LORA, TCOND, VAE]:
    os.makedirs(d, exist_ok=True)

MODELS = [
    # (filename, dest_dir, HF URL) — pruned INT8 = VRAM-friendly for T4
    ("minimax_h3_ref2va_viggle_pruned_int8_convrot.safetensors", DMODEL,
     "https://huggingface.co/drbaph/Viggle-Animate-ComfyUI/resolve/main/diffusion_models/minimax_h3_ref2va_viggle_pruned_int8_convrot.safetensors"),
    ("viggle_animate_dmd_lora_r64.safetensors", LORA,
     "https://huggingface.co/drbaph/Viggle-Animate-ComfyUI/resolve/main/loras/viggle_animate_dmd_lora_r64.safetensors"),
    ("fixed_embed_fwd_anyframe.safetensors", TCOND,
     "https://huggingface.co/drbaph/Viggle-Animate-ComfyUI/resolve/main/text_cond/fixed_embed_fwd_anyframe.safetensors"),
    ("minimax_h3_video_vae_int8_convrot.safetensors", VAE,
     "https://huggingface.co/Kijai/MiniMax-H3-experimental/resolve/main/minimax_h3_video_vae_int8_convrot.safetensors"),
]

for fname, ddir, url in MODELS:
    out = os.path.join(ddir, fname)
    if os.path.exists(out) and os.path.getsize(out) > 100_000_000:
        print(f"✅ {fname} already present ({os.path.getsize(out)/1e9:.1f} GB)")
    else:
        print(f"⬇️  Downloading {fname}...")
        subprocess.run(["wget", "-q", "--show-progress", url, "-O", out], check=True)
        print(f"✅ {fname} done ({os.path.getsize(out)/1e9:.1f} GB)")

print("\\n✅ All models downloaded. Your studio is ready.")
'''),

md("""## 👆 UPLOAD YOUR FILES HERE

**In the Kaggle notebook file panel (right side), upload these two files to `/kaggle/working/`:**

1. **`driving_video.mp4`** — A video of YOU doing the motion.
   - Keep it under 10 seconds (124 frames @ 24fps is the sweet spot)
   - Good lighting, full body visible, simple background works best
   - MP4 format

2. **`character.png`** — A picture of the character to put on your body.
   - Cape Jones, or any character you want
   - Clear, front-facing image works best
   - PNG or JPG

**Once both files are uploaded, run the next cell.**"""),

code('''# === Cell 4: Verify uploads ===
import os

DRIVING = "/kaggle/working/driving_video.mp4"
CHAR = "/kaggle/working/character.png"
# Also accept .jpg for character
if not os.path.exists(CHAR):
    for ext in [".jpg", ".jpeg", ".JPG", ".PNG"]:
        alt = f"/kaggle/working/character{ext}"
        if os.path.exists(alt):
            CHAR = alt
            break

assert os.path.exists(DRIVING), f"❌ Upload driving_video.mp4 to /kaggle/working/ first!"
assert os.path.exists(CHAR), f"❌ Upload character.png to /kaggle/working/ first!"

import subprocess
# Check video properties
r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=nb_frames,r_frame_rate,duration,width,height",
                    "-of", "default=noprint_wrappers=1", DRIVING],
                   capture_output=True, text=True)
print("Driving video:")
print(r.stdout)
print(f"Character image: {CHAR} ({os.path.getsize(CHAR)/1e6:.1f} MB)")
print("\\n✅ Both files ready. Running body replacement next...")
'''),

code('''# === Cell 5: Run Viggle-Animate body replacement ===
# This starts ComfyUI headless, loads the workflow, and runs it via API.
import subprocess, os, sys, time, json, shutil

COMFY = "/kaggle/working/ComfyUI"
WORKFLOW_SRC = "/kaggle/working/viggle_workflow_api.json"

# Copy input files to ComfyUI input dir
INPUT_DIR = os.path.join(COMFY, "input")
os.makedirs(INPUT_DIR, exist_ok=True)
shutil.copy("/kaggle/working/driving_video.mp4", os.path.join(INPUT_DIR, "driving_video.mp4"))
# Find character image
for ext in [".png", ".jpg", ".jpeg", ".JPG", ".PNG"]:
    src = f"/kaggle/working/character{ext}"
    if os.path.exists(src):
        shutil.copy(src, os.path.join(INPUT_DIR, "character" + ext))
        CHAR_FILE = "character" + ext
        break

# Download the pre-built workflow from the repo
WF_URL = "RAW_PLACEHOLDER/viggle_workflow_api.json"
print(f"Downloading workflow...")
subprocess.run(["wget", "-q", WF_URL, "-O", WORKFLOW_SRC], check=True)
print("✅ Workflow loaded.")

# Start ComfyUI server in background (lowvram mode for T4)
print("Starting ComfyUI server...")
server = subprocess.Popen(
    [sys.executable, "main.py", "--listen", "127.0.0.1", "--port", "8188",
     "--lowvram", "--disable-auto-launch"],
    cwd=COMFY, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(25)  # Wait for server startup
print("✅ ComfyUI server running.")
print(f"\\nNext: the workflow runs via API. This takes ~5-10 min for 124 frames.")
print(f"Character file: {CHAR_FILE}")
'''),

code('''# === Cell 6: Execute workflow via ComfyUI API and download result ===
import json, urllib.request, urllib.parse, time, os, uuid

with open("/kaggle/working/viggle_workflow_api.json") as f:
    workflow = json.load(f)

# Update workflow with our input filenames
for node_id, node in workflow.items():
    if node.get("class_type") == "VHS_LoadVideo":
        # Point to our driving video
        for k in node.get("inputs", {}):
            if "video" in k.lower():
                node["inputs"][k] = "driving_video.mp4"
    if node.get("class_type") == "LoadImage":
        node["inputs"]["image"] = CHAR_FILE

client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_history(prompt_id):
    req = urllib.request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
    return json.loads(urllib.request.urlopen(req).read())

print("Queueing Viggle-Animate workflow...")
resp = queue_prompt(workflow)
prompt_id = resp['prompt_id']
print(f"Prompt ID: {prompt_id}")
print("Rendering... (this takes ~5-10 minutes for 124 frames)")

# Poll for completion
start = time.time()
while True:
    time.sleep(15)
    hist = get_history(prompt_id)
    if prompt_id in hist:
        status = hist[prompt_id].get('status', {})
        if status.get('completed', False):
            break
        if 'failed' in str(status.get('status_str', '')).lower():
            print(f"❌ Failed: {status}")
            break
    elapsed = (time.time() - start) / 60
    print(f"  ... still rendering ({elapsed:.1f} min elapsed)")

print("\\n✅ Done! Finding output video...")
# Find output in ComfyUI output dir
OUT_DIR = "/kaggle/working/ComfyUI/output"
for root, dirs, files in os.walk(OUT_DIR):
    for f in sorted(files, reverse=True):
        if f.endswith('.mp4'):
            src = os.path.join(root, f)
            dst = "/kaggle/working/cape-jones-body-replace.mp4"
            import shutil
            shutil.copy(src, dst)
            print(f"✅ Output saved: {dst} ({os.path.getsize(dst)/1e6:.1f} MB)")
            break
    break

import subprocess
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of", "default=noprint_wrappers=1",
                    "/kaggle/working/cape-jones-body-replace.mp4"],
                   capture_output=True, text=True)
print(f"Duration: {r.stdout.strip()}")
print("\\n🎬 Download cape-jones-body-replace.mp4 from the right panel → Output!")
'''),
]

# Replace placeholder with actual RAW URL
nb_json = {"cells": cells, "metadata": {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.10.0"}},
    "nbformat": 4, "nbformat_minor": 4}

# Inject RAW URL into cell 5
for cell in nb_json["cells"]:
    if cell["cell_type"] == "code":
        src = cell["source"] if isinstance(cell["source"], str) else "".join(cell["source"])
        if "RAW_PLACEHOLDER" in src:
            src = src.replace("RAW_PLACEHOLDER", RAW)
            cell["source"] = src

with open("/home/hatch/workspace/cape-jones-build/kaggle-viggle/cape_jones_viggle_kaggle.ipynb", "w") as f:
    json.dump(nb_json, f, indent=1)

print("Generated: cape_jones_viggle_kaggle.ipynb")
print(f"Cells: {len(cells)}")
