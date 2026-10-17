#!/usr/bin/env python3
"""
Wan Animate pipeline status checker — runs on the VM (CPU only).

Checks:
1. Can we run Wan 2.2 Animate locally? (No — no GPU)
2. What's the recommended free path?
3. Are CPU-based alternatives available? (FFmpeg cartoon filter, OpenCV stylization)

Usage: python3 check_pipeline.py
"""

import shutil
import subprocess
import sys


def check_gpu():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                              "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def check_tool(name):
    return shutil.which(name) is not None


def main():
    print("=" * 60)
    print("Wan 2.2 Animate Pipeline Status")
    print("=" * 60)

    # GPU check
    gpu = check_gpu()
    print(f"\n[GPU] {gpu if gpu else 'NONE — no NVIDIA GPU detected'}")

    # RAM check
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    kb = int(line.split()[1])
                    print(f"[RAM] {kb // 1024 // 1024} GB total")
                    break
    except FileNotFoundError:
        print("[RAM] Unknown")

    # Wan requirements vs reality
    print("\n--- Wan 2.2 Animate requirements ---")
    print("  Minimum: 16GB VRAM (FP8 quantized)")
    print("  Recommended: 24GB VRAM (RTX 4090)")
    print("  Disk: ~27GB for full ComfyUI setup")
    if gpu:
        print("  Status: GPU found — may be runnable, check VRAM")
    else:
        print("  Status: CANNOT RUN LOCALLY — no GPU")
        print("  Free path: Kaggle T4 (16GB VRAM, ~30hrs/week)")
        print("  Notebook: colab-wan-animate.ipynb in this directory")

    # CPU-based alternatives
    print("\n--- CPU-based alternatives (available on this VM) ---")
    tools = {
        "ffmpeg": "Video processing, cartoon filters",
        "python3": "OpenCV stylization scripts",
    }
    for tool, desc in tools.items():
        status = "AVAILABLE" if check_tool(tool) else "MISSING"
        print(f"  [{status}] {tool} — {desc}")

    # EbSynth note
    print("\n--- EbSynth ---")
    print("  CPU-only, free — BUT Windows/Mac only, no Linux build.")
    print("  Cannot run on this VM. Needs a Windows/Mac machine.")

    print("\n" + "=" * 60)
    print("RECOMMENDATION: Use Kaggle T4 free tier with")
    print("colab-wan-animate.ipynb for character replacement.")
    print("=" * 60)


if __name__ == "__main__":
    main()
