#!/usr/bin/env python3
"""Batch pose extraction for 19 drifted EP02 shots."""
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home() / "workspace"
NORM = BASE / "trippedd-studio/production/WIZARD_GANG_EP01/ep02-normalized"
OUT = BASE / "video-fix-tools/pose-extract/ep02-poses"
EXTRACT = BASE / "video-fix-tools/pose-extract/extract_pose.py"
VENV_PY = BASE / "video-fix-tools/pose-extract/venv/bin/python"
CKPT = BASE / "agent-ops/checkpoints/ep02-pose-extraction.json"

# (clip_num, timestamp_label, description)
SHOTS = [
    (2,  "1:00", "council chamber"),
    (4,  "1:20", "council table"),
    (5,  "1:30", "echo graffiti"),
    (6,  "1:40", "street crew lineup"),
    (8,  "2:00", "static at table"),
    (9,  "2:10", "static closeup"),
    (13, "2:50", "grill scene"),
    (14, "3:00", "dice game"),
    (15, "3:10", "arcade echo"),
    (16, "3:20", "basketball"),
    (17, "3:30", "bodega"),
    (18, "3:40", "night market"),
    (20, "4:00", "bridge exchange"),
    (21, "4:10", "parking garage"),
    (22, "4:20", "skate park"),
    (23, "4:30", "podcast studio"),
    (24, "4:40", "carnival"),
    (25, "4:50", "fireworks rooftop"),
    (26, "5:00", "pier kiko"),
]

def heartbeat(done_count):
    ckpt = json.loads(CKPT.read_text())
    ckpt["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ckpt["notes"] = f"Processed {done_count}/{len(SHOTS)} shots"
    CKPT.write_text(json.dumps(ckpt, indent=2))

def main():
    start_idx = 0
    # Resume: skip shots that already have skeleton.mp4
    manifest_path = OUT / "manifest.csv"
    done_clips = set()
    if manifest_path.exists():
        with open(manifest_path) as f:
            for row in csv.DictReader(f):
                if row.get("status") == "done":
                    done_clips.add(int(row["clip"]))

    rows = []
    # Load existing rows for resume
    if manifest_path.exists():
        with open(manifest_path) as f:
            rows = list(csv.DictReader(f))

    for i, (clip_num, ts, desc) in enumerate(SHOTS):
        if clip_num in done_clips:
            print(f"[{i+1}/{len(SHOTS)}] clip-{clip_num:02d} ({ts} {desc}): SKIPPED (already done)")
            continue

        clip_file = NORM / f"clip-{clip_num:02d}.mp4"
        out_dir = OUT / f"shot-{clip_num:02d}"
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"[{i+1}/{len(SHOTS)}] Processing clip-{clip_num:02d}.mp4 ({ts} {desc})...")
        result = subprocess.run(
            [str(VENV_PY), str(EXTRACT), "--input", str(clip_file), "--out-dir", str(out_dir)],
            capture_output=True, text=True, timeout=600,
        )

        # Parse detection rate from output
        detection_rate = 0.0
        total_frames = 0
        for line in result.stdout.split("\n"):
            if "detection rate" in line.lower() or "detected" in line.lower():
                print(f"    {line.strip()}")

        # Count frames in poses.json
        poses_path = out_dir / "poses.json"
        status = "failed"
        if poses_path.exists():
            try:
                poses = json.loads(poses_path.read_text())
                total_frames = len(poses) if isinstance(poses, list) else len(poses.get("frames", []))
                # Count frames with detections (key is "people" in this pipeline)
                detected = 0
                frame_list = poses if isinstance(poses, list) else poses.get("frames", [])
                for fr in frame_list:
                    people = fr.get("people", fr.get("persons", fr.get("poses", [])))
                    if people and len(people) > 0:
                        # Check if landmarks are non-trivial (not all zeros)
                        first = people[0]
                        if isinstance(first, list) and len(first) > 0:
                            # List of landmark dicts
                            xs = [lm.get("x", 0) for lm in first if isinstance(lm, dict)]
                            if xs and max(xs) - min(xs) > 0.01:
                                detected += 1
                        elif isinstance(first, dict):
                            detected += 1
                detection_rate = detected / total_frames if total_frames else 0
                status = "done"
            except Exception as e:
                print(f"    ERROR parsing poses.json: {e}")

        flag = ""
        if detection_rate < 0.5 and status == "done":
            flag = "LOW_DETECTION_NEEDS_DWPOSE"

        print(f"    -> {status}: {total_frames} frames, {detection_rate:.1%} detection {flag}")

        # Update or add row
        row = {
            "shot": f"shot-{clip_num:02d}",
            "clip": clip_num,
            "timestamp": ts,
            "description": desc,
            "clip_file": str(clip_file),
            "frames": total_frames,
            "detection_rate": f"{detection_rate:.3f}",
            "skeleton_mp4": str(out_dir / "skeleton.mp4"),
            "poses_json": str(out_dir / "poses.json"),
            "preview_png": str(out_dir / "preview.png"),
            "status": status,
            "flag": flag,
        }
        # Replace existing row for this clip or append
        rows = [r for r in rows if int(r["clip"]) != clip_num]
        rows.append(row)
        rows.sort(key=lambda r: int(r["clip"]))

        # Write manifest incrementally
        with open(manifest_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=row.keys())
            w.writeheader()
            w.writerows(rows)

        heartbeat(len([r for r in rows if r["status"] == "done"]))

    print(f"\nDone. Manifest: {manifest_path}")
    done = len([r for r in rows if r["status"] == "done"])
    low = len([r for r in rows if r["flag"]])
    print(f"Completed: {done}/{len(SHOTS)}, flagged for DWPose: {low}")

if __name__ == "__main__":
    main()
