import argparse
import glob
import json
import os
import subprocess


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def build_animation_slice(asset_path, rhubarb_json):
    logs = ["[PIPELINE] Initializing animation vertical slice..."]

    if not os.path.isfile(asset_path):
        return {"status": "BLOCKED", "reason": "Canonical asset missing", "logs": logs}
    if not os.path.isfile(rhubarb_json):
        return {"status": "BLOCKED", "reason": "REAL_AUDIO_REQUIRED: Rhubarb JSON missing", "logs": logs}

    logs += [
        "[AUDIO] Rhubarb cue file supplied; no transcript is invented.",
        "[FACE] Source mode: AUDIO",
    ]

    root = os.path.dirname(asset_path)
    proxy_path = asset_path.replace(".glb", "_proxy.glb")
    rig_path = proxy_path.replace(".glb", "_rigged.glb")
    frames_dir = os.path.join(root, "frames")
    evidence_dir = os.path.join(root, "visual_evidence")
    os.makedirs(frames_dir, exist_ok=True)

    proxy_script = os.path.join(os.path.dirname(__file__), "proxy_generator.py")
    p = run(["python3", proxy_script, asset_path, proxy_path])
    if not os.path.isfile(proxy_path):
        return {"status": "BLOCKED", "reason": "Proxy generation failed", "logs": logs + [p.stderr[-4000:]]}
    logs.append("[PROXY] Generated; canonical source remains untouched.")

    rig_script = os.path.join(os.path.dirname(__file__), "rig_proxy.py")
    r = run(["blender", "--background", "--python", rig_script, "--", proxy_path, rig_path])
    if not os.path.isfile(rig_path):
        return {"status": "BLOCKED", "reason": "Rig generation failed", "logs": logs + [r.stderr[-4000:]]}
    logs.append("[RIG] Rig package generated.")

    anim_script = os.path.join(os.path.dirname(__file__), "animate_rig.py")
    a = run(["blender", "--background", "--python", anim_script, "--", rig_path, frames_dir, rhubarb_json])
    frame_files = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
    if a.returncode != 0 or not frame_files:
        return {"status": "BLOCKED", "reason": "REAL_RENDER missing or animation failed", "logs": logs + [a.stdout[-4000:], a.stderr[-4000:]]}
    logs.append(f"[RENDER] REAL_RENDER: {len(frame_files)} PNG frames.")

    evidence_script = os.path.join(os.path.dirname(__file__), "make_visual_evidence.py")
    e = run(["python3", evidence_script, frames_dir, "--out", evidence_dir])
    if e.returncode != 0 or not os.path.isfile(os.path.join(evidence_dir, "CONTACT-SHEET.png")):
        return {"status": "BLOCKED", "reason": "VISUAL_EVIDENCE missing", "logs": logs + [e.stdout[-4000:], e.stderr[-4000:]]}
    logs.append("[EVIDENCE] CONTACT-SHEET.png generated for human inspection.")

    return {
        "status": "SUCCESS",
        "sourceMode": "AUDIO",
        "frames": frame_files,
        "visualEvidence": os.path.join(evidence_dir, "CONTACT-SHEET.png"),
        "logs": logs,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("asset")
    ap.add_argument("--rhubarb-json", required=True)
    args = ap.parse_args()
    result = build_animation_slice(args.asset, args.rhubarb_json)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "SUCCESS" else 1)
