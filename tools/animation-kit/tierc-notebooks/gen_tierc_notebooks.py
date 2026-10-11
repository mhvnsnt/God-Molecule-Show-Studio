#!/usr/bin/env python3
"""Generate the Tier C GPU notebooks (ComfyUI, RVC, TripoSR).
Run: python3 gen_tierc_notebooks.py  ->  writes 3 .ipynb files.
GPU cells are NOT executed here; notebooks are JSON-validated only."""
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__))


def nb(cells):
    return {"nbformat": 4, "nbformat_minor": 5,
            "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"},
                         "accelerator": "GPU"},
            "cells": cells}


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(True)}


def code(src):
    return {"cell_type": "code", "metadata": {},
            "execution_count": None, "outputs": [], "source": src.splitlines(True)}


COMFY = nb([
    md("# ComfyUI on Colab — AI image/video generation\n"
       "Node-based Stable Diffusion studio on your free Colab GPU.\n\n"
       "**Phone steps:** Runtime → Run all → open the tunnel URL from the last cell.\n"
       "Build workflows visually: text-to-image, img2img, upscaling, animation frames."),
    code("# 1) system + ComfyUI\n"
         "!pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu121\n"
         "!git clone https://github.com/comfyanonymous/ComfyUI\n"
         "%cd ComfyUI\n"
         "!pip install -q -r requirements.txt\n"
         "!pip install -q onnxruntime-gpu  # optional, for some nodes"),
    code("# 2) a fast light model: SDXL Turbo (~7GB, great on free T4)\n"
         "!mkdir -p models/checkpoints\n"
         "!wget -q --show-progress -O models/checkpoints/sd_xl_turbo_1.0_fp16.safetensors "
         "https://huggingface.co/stabilityai/sdxl-turbo/resolve/main/sd_xl_turbo_1.0_fp16.safetensors"),
    code("# 3) launch + public link (cloudflared works on Colab's network)\n"
         "!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /tmp/cf\n"
         "!chmod +x /tmp/cf\n"
         "import subprocess, time\n"
         "srv = subprocess.Popen(['python', 'main.py', '--port', '8188'])\n"
         "time.sleep(8)\n"
         "tun = subprocess.Popen(['/tmp/cf', 'tunnel', '--url', 'http://localhost:8188'],\n"
         "                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)\n"
         "import re\n"
         "url = ''\n"
         "for _ in range(60):\n"
         "    line = tun.stdout.readline()\n"
         "    m = re.search(r'https://[\\w.-]+\\.trycloudflare\\.com', line)\n"
         "    if m:\n"
         "        url = m.group(0); break\n"
         "print('OPEN ON YOUR PHONE:', url)\n"
         "srv.wait()  # keep alive; Runtime -> Interrupt to stop"),
    md("## Tips\n"
       "- Queue a prompt, then **Queue Prompt** — 4 steps is enough with Turbo.\n"
       "- Save workflows you like (the .json) — they go straight into the repo.\n"
       "- For video: add AnimateDiff nodes (install via ComfyUI Manager in the UI).\n"
       "- Disk: Colab gives ~100GB; models live in `models/checkpoints/`."),
])

RVC = nb([
    md("# RVC on Colab — voice conversion (record a read, convert any line into it)\n"
       "Retrieval-based Voice Conversion. **Directly serves our leprechaun-voice work:**\n"
       "approve a voice read once, then convert any new line into that same voice.\n\n"
       "**Phone steps:** Runtime → Run all → open the gradio link from the last cell.\n"
       "Training needs ~10 min of clean voice audio and ~30-60 min on a T4."),
    code("# 1) RVC + deps\n"
         "!git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion\n"
         "%cd Retrieval-based-Voice-Conversion\n"
         "!pip install -q -r requirements.txt\n"
         "!pip install -q gradio fairseq  # fairseq needed for hubert"),
    code("# 2) pretrained base models (needed for training AND inference)\n"
         "!mkdir -p assets/pretrained_v2 assets/hubert\n"
         "!wget -q -O assets/hubert/hubert_base.pt "
         "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt\n"
         "!wget -q -O assets/pretrained_v2/f0G32k.pth "
         "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/f0G32k.pth\n"
         "!wget -q -O assets/pretrained_v2/f0D32k.pth "
         "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/pretrained_v2/f0D32k.pth\n"),
    code("# 3) launch the WebUI with a public link\n"
         "# Upload training audio in the UI: Train tab -> dataset -> 1-click train.\n"
         "# Then Infer tab: pick your model, upload/convert any line.\n"
         "!python infer-web.py --colab --pycmd python --share --port 7860"),
    md("## Voice-model workflow (the leprechaun pipeline)\n"
       "1. Get 10+ min of clean approved voice (the V1 leprechaun line looped/extended works as a seed, but more variety is better).\n"
       "2. Train tab → name it (e.g. `leprechaun_v1`) → train (~30-60 min on T4).\n"
       "3. Infer tab → convert any new dialogue line into the leprechaun voice.\n"
       "4. Download the `.pth` → commit to the repo so the voice is never lost (salvage law)."),
])

TRIPO = nb([
    md("# TripoSR on Colab — image → 3D model in seconds\n"
       "Open image-to-3D (VAST-AI-Research/TripoSR). Upload concept art or a\n"
       "photo, get a GLB/OBJ back. Runs fine on a free T4.\n\n"
       "**Phone steps:** Runtime → Run all → open the gradio link → upload image → download model."),
    code("# 1) TripoSR + deps\n"
         "!pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu121\n"
         "!git clone https://github.com/VAST-AI-Research/TripoSR\n"
         "%cd TripoSR\n"
         "!pip install -q -r requirements.txt\n"
         "!pip install -q gradio rembg onnxruntime trimesh"),
    code("# 2) weights (auto-download from HF on first run; pin here explicitly)\n"
         "from huggingface_hub import snapshot_download\n"
         "snapshot_download('stabilityai/TripoSR', local_dir='weights')\n"
         "print('weights ok')"),
    code("# 3) Gradio UI: image in -> GLB + OBJ out\n"
         "import gradio as gr, torch, numpy as np, trimesh\n"
         "from PIL import Image\n"
         "from tsr.system import TSR\n"
         "from tsr.utils import remove_background, resize_foreground, to_gradio_3d_orientation\n"
         "\n"
         "model = TSR.from_pretrained('stabilityai/TripoSR', config_name='config.yaml', weight_name='model.ckpt')\n"
         "model.cuda(); model.renderer.set_chunk_size(8192)\n"
         "\n"
         "def image_to_3d(img, mc_resolution=256):\n"
         "    img = remove_background(img)\n"
         "    img = resize_foreground(img, 0.85)\n"
         "    scene = model.reconstruct([img], chunk_size=8192)\n"
         "    mesh = to_gradio_3d_orientation(scene[0].get_mesh()).as_mesh()\n"
         "    mesh.export('/tmp/tripo_out.glb'); mesh.export('/tmp/tripo_out.obj')\n"
         "    return '/tmp/tripo_out.glb', '/tmp/tripo_out.obj'\n"
         "\n"
         "gr.Interface(fn=image_to_3d,\n"
         "             inputs=[gr.Image(type='pil', label='Concept art / photo'),\n"
         "                     gr.Slider(64, 512, value=256, step=64, label='Marching-cubes resolution')],\n"
         "             outputs=[gr.Model3D(label='GLB preview'), gr.File(label='OBJ download')],\n"
         "             title='TripoSR — image to 3D').launch(share=True)"),
    md("## Notes\n"
       "- Best input: clean character/prop on plain background (rembg runs first anyway).\n"
       "- Output is untextured-ish geometry — detail it in Blender, paint in ArmorPaint.\n"
       "- Heavier alternative: TRELLIS (better quality, needs more VRAM) — same notebook pattern."),
])

for name, n in [("ComfyUI_Colab", COMFY), ("RVC_Colab", RVC), ("TripoSR_Colab", TRIPO)]:
    p = os.path.join(OUT, name + ".ipynb")
    json.dump(n, open(p, "w"), indent=1)
    # validate
    d = json.load(open(p))
    assert d["nbformat"] == 4
    for c in d["cells"]:
        if c["cell_type"] == "code":
            src = "".join(c["source"])
            # strip IPython magics (!cmd, %cd) before syntax check
            py = "\n".join(l for l in src.splitlines()
                           if not l.lstrip().startswith(("!", "%")))
            compile(py, "<cell>", "exec")
    print("ok:", p, "-", len(d["cells"]), "cells")
