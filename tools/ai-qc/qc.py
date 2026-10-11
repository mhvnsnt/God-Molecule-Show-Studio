#!/usr/bin/env python3
"""
qc.py — Unified episode QC. One command, real answers.

    qc.py audit <video>            full pass: silence gaps, talking regions,
                                   speaker clusters, mismatches vs dialogue
    qc.py who <video> <t>          who's on screen + is anyone talking at t?
    qc.py voice <video> <t0> <t1> <character>
                                   is the voice at t0-t1 the expected character?
                                   (character: static, cipher, sombra, ...)
    qc.py deep-audio <video>       emotion/prosody, music vs speech,
                                   clipping, volume anomalies, overlaps
    qc.py deep-visual <video>      frozen frames, grading shifts,
                                   filter signature, glitches, text overlays
    qc.py mesh <file.glb|.obj>     3D asset QC: degenerate tris, NaN verts,
                                   bad weights, missing textures, bad nodes
    qc.py motion <video>           optical flow, still regions, camera shake
    qc.py pose <video> <t>         full-body pose + T-pose check at t
    qc.py hands <video> <t>        hand tracking at t
    qc.py music <video>            BGM segments with BPM + key
    qc.py ocr-frame <video> <t>    text/OCR in frame at t
    qc.py subs <video>             burned-in subtitle scan
    qc.py anomaly <video>          cross-modal anomalies (the NOSE)
    qc.py direct <video>           full director synthesis (the BRAIN)

Voice references live in ~/workspace/voice-delivery/:
    voice-static-*.mp3, voice-cipher-*.mp3, voice-sombra-h3.mp3, ...

Run with the ai-qc venv: ~/workspace/tools/ai-qc/venv/bin/python qc.py ...
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_qc
import video_qc
import audio_deep
import visual_deep
import mesh_qc
import motion
import music
import ocr
import anomaly
import director
import surgery  # noqa: F401  (imported for CLI use)


def cmd_audit(video):
    print("== extracting audio ==", flush=True)
    wav = audio_qc.extract_audio(video)
    y = audio_qc.load_audio(wav)
    sr = 16000

    print("== silence gaps (>=2s) ==", flush=True)
    gaps = audio_qc.find_silence_gaps(y, sr)
    print(json.dumps({"silence_gaps_s": gaps}, indent=1))

    print("== talking regions (mouth visibly moving) ==", flush=True)
    talking = video_qc.talking_regions(video)
    print(json.dumps({"talking_regions_s": talking}, indent=1))

    print("== cross-check: talking but silent ==", flush=True)
    suspects = []
    for ts, te in talking:
        mid = (ts + te) / 2
        # audio energy in that window
        seg = y[int(ts * sr):int(te * sr)]
        if len(seg) == 0:
            continue
        db = 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)
        if db < -45:
            suspects.append({"window": [ts, te], "audio_db": round(float(db), 1),
                             "issue": "mouth moving, no dialogue audio"})
    print(json.dumps({"talking_but_silent": suspects}, indent=1))

    print("== speaker clusters (n=4) ==", flush=True)
    segs = audio_qc.speaker_segments(y, sr, n_speakers=4)
    # compress consecutive same-speaker
    comp = []
    for s in segs:
        if comp and comp[-1][2] == s[2]:
            comp[-1] = (comp[-1][0], s[1], s[2])
        else:
            comp.append([s[0], s[1], s[2]])
    print(json.dumps({"speaker_clusters": comp}, indent=1))
    print("\nDone. Compare speaker cluster IDs against DIALOGUE.md character map.")


def cmd_who(video, t):
    n_faces = video_qc.face_count_at(video, t)
    series = video_qc.mouth_openness_series(video, sample_fps=5)
    # nearest sample
    near = min(series, key=lambda s: abs(s[0] - t)) if series else (t, 0, False)
    print(json.dumps({
        "t": t,
        "faces_on_screen": n_faces,
        "mouth_open": near[2] and near[1] > 0.08,
        "mouth_openness": near[1],
    }, indent=1))


def cmd_voice(video, t0, t1, expected_char):
    verdict, pred, d = audio_qc.check_voice_at(video, t0, t1, expected_char)
    print(json.dumps({"window": [t0, t1], "expected": expected_char,
                      "verdict": verdict, "predicted": pred,
                      "distances": {k: round(x, 2) for k, x in d.items()}}, indent=1))


def cmd_deep_audio(video):
    print("== deep audio: clipping / volume / overlaps / music ==", flush=True)
    wav = audio_deep.extract_audio(video)
    import librosa
    y, _ = librosa.load(wav, sr=16000, mono=True)
    sr = 16000
    print(json.dumps({
        "clipping": audio_deep.find_clipping(y, sr),
        "volume_anomalies": audio_deep.volume_anomalies(y, sr),
        "overlaps": audio_deep.overlap_regions(y, sr),
    }, indent=1))
    print("== music vs speech map ==", flush=True)
    print(json.dumps({"segments": audio_deep.music_vs_speech(y, sr)}, indent=1))


def cmd_deep_visual(video):
    print("== deep visual: frozen / grading / filter / glitch ==", flush=True)
    print(json.dumps({
        "frozen_regions": visual_deep.frozen_regions(video),
        "grading_shifts": visual_deep.grading_shifts(video),
        "filter_regions": visual_deep.filter_scan(video),
        "glitches": visual_deep.glitch_scan(video),
    }, indent=1))


def cmd_mesh(path):
    if path.lower().endswith(".glb"):
        r = mesh_qc.audit_glb(path)
    elif path.lower().endswith(".obj"):
        r = {"file": path, "issues": mesh_qc.audit_obj(path), "stats": {}}
    else:
        print(json.dumps({"error": "need .glb or .obj"}))
        return
    print(json.dumps(r, indent=1))


def cmd_motion(video):
    print(json.dumps({
        "still_regions": motion.still_regions(video),
        "camera_shake": motion.camera_shake(video),
    }, indent=1))


def cmd_pose(video, t):
    poses = motion.pose_at(video, t)
    out = []
    for p in poses:
        if "note" in p:
            out.append(p)
            continue
        tp, ap, ang = motion.tpose_check(p)
        out.append({"pose": p, "is_tpose": tp, "is_apose": ap,
                    "arm_angle": ang})
    print(json.dumps(out, indent=1))


def cmd_hands(video, t):
    print(json.dumps(motion.hand_tracking_at(video, t), indent=1))


def cmd_music(video):
    import subprocess
    import librosa
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video,
                    "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
                    "/tmp/aiqc_qc_music.wav"], check=True)
    y, _ = librosa.load("/tmp/aiqc_qc_music.wav", sr=16000)
    print(json.dumps({"music_segments": music.music_segments(y)},
                     indent=1))


def cmd_ocr_frame(video, t):
    print(json.dumps(ocr.frame_text(video, t), indent=1))


def cmd_subs(video):
    print(json.dumps({"subtitles": ocr.subtitle_scan(video)}, indent=1))


def cmd_anomaly(video):
    print(json.dumps({
        "av_sync": anomaly.av_sync_anomalies(video),
        "lighting_jumps": anomaly.lighting_jumps(video),
        "audio_mismatch": anomaly.audio_scene_mismatch(video),
        "shot_anomalies": anomaly.shot_duration_anomalies(video),
    }, indent=1))


def cmd_direct(video):
    """Full director synthesis: run everything, combine into notes."""
    print("== gathering signals (this takes a few minutes) ==", flush=True)
    import librosa
    wav = audio_qc.extract_audio(video, "/tmp/aiqc_direct.wav")
    y = audio_qc.load_audio(wav)
    sr = 16000
    findings = {}
    print("-- audio --", flush=True)
    findings["clipping"] = audio_deep.find_clipping(y, sr)
    findings["volume_anomalies"] = audio_deep.volume_anomalies(y, sr)
    findings["overlaps"] = audio_deep.overlap_regions(y, sr)
    findings["silence_gaps"] = audio_qc.find_silence_gaps(y, sr)
    print("-- visual --", flush=True)
    findings["frozen_regions"] = visual_deep.frozen_regions(video)
    findings["grading_shifts"] = visual_deep.grading_shifts(video)
    findings["filter_regions"] = visual_deep.filter_scan(video)
    findings["glitches"] = visual_deep.glitch_scan(video)
    print("-- cross-modal --", flush=True)
    findings["av_sync"] = anomaly.av_sync_anomalies(video)
    findings["lighting_jumps"] = anomaly.lighting_jumps(video)
    findings["audio_mismatch"] = anomaly.audio_scene_mismatch(video)
    findings["shot_anomalies"] = anomaly.shot_duration_anomalies(video)
    print("-- voice check on dialogue regions --", flush=True)
    vm = audio_qc.VoiceModel.build("/home/hatch/workspace/voice-delivery", sr)
    # check each 10s window that has speech
    vad = audio_qc.speech_activity(y, sr)
    frame_s = 0.03
    mismatches = []
    for w0 in range(0, int(len(y) / sr) - 10, 10):
        i0, i1 = int(w0 / frame_s), int((w0 + 10) / frame_s)
        if i1 < len(vad) and vad[i0:i1].mean() > 0.3:
            seg = y[w0 * sr:(w0 + 10) * sr]
            pred, d = vm.classify(seg, sr)
            # flag if predicted voice is far from all others (confident)
            # and note it; human maps to expected character via DIALOGUE.md
            ds = sorted(d.values())
            if len(ds) > 1 and ds[1] - ds[0] > 2.0:
                mismatches.append({"window": [w0, w0 + 10],
                                   "predicted": pred,
                                   "confidence_gap": round(ds[1] - ds[0], 2)})
    findings["voice_mismatches"] = mismatches
    print("== director notes ==", flush=True)
    notes = director.synthesize(findings)
    print(director.format_notes(notes))
    # save raw findings too
    with open("/tmp/aiqc_direct_findings.json", "w") as f:
        json.dump({"findings": findings,
                   "notes": notes}, f, indent=1, default=str)
    print("\nRaw findings: /tmp/aiqc_direct_findings.json")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "audit":
        cmd_audit(sys.argv[2])
    elif cmd == "who":
        cmd_who(sys.argv[2], float(sys.argv[3]))
    elif cmd == "voice":
        cmd_voice(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5])
    elif cmd == "deep-audio":
        cmd_deep_audio(sys.argv[2])
    elif cmd == "deep-visual":
        cmd_deep_visual(sys.argv[2])
    elif cmd == "mesh":
        cmd_mesh(sys.argv[2])
    elif cmd == "motion":
        cmd_motion(sys.argv[2])
    elif cmd == "pose":
        cmd_pose(sys.argv[2], float(sys.argv[3]))
    elif cmd == "hands":
        cmd_hands(sys.argv[2], float(sys.argv[3]))
    elif cmd == "music":
        cmd_music(sys.argv[2])
    elif cmd == "ocr-frame":
        cmd_ocr_frame(sys.argv[2], float(sys.argv[3]))
    elif cmd == "subs":
        cmd_subs(sys.argv[2])
    elif cmd == "anomaly":
        cmd_anomaly(sys.argv[2])
    elif cmd == "direct":
        cmd_direct(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
