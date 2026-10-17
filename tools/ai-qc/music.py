#!/usr/bin/env python3
"""
music.py — Music analysis for episode QC and BGM work.

- Beat/tempo detection: BPM, beat positions (for syncing cuts to music)
- Key detection: musical key via chroma (for BGM matching)
- Music fingerprinting: Shazam-like chroma landmarks (identify if a
  segment matches a known reference track)
- Source separation note: Demucs needs GPU — documented for cloud use

librosa only. CPU.
"""
import numpy as np


def tempo_and_beats(y, sr=16000):
    """
    Returns {"bpm": float, "beats": [t_seconds], "confidence": 0..1}.
    """
    import librosa
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr).tolist()
    # confidence: onset strength autocorrelation peak
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    ac = np.correlate(onset, onset, mode="full")[len(onset):]
    conf = float(ac[1:50].max() / (ac[0] + 1e-9)) if len(ac) > 50 else 0.0
    return {"bpm": round(float(tempo), 1),
            "beats": [round(t, 2) for t in beat_times[:64]],
            "confidence": round(min(conf, 1.0), 2)}


def detect_key(y, sr=16000):
    """
    Musical key via chroma template matching (Krumhansl profiles).
    Returns {"key": "C major", "confidence": 0..1}.
    """
    import librosa
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)
    # Krumhansl major/minor profiles
    major = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
                      2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                      2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    names = ["C", "C#", "D", "D#", "E", "F",
             "F#", "G", "G#", "A", "A#", "B"]
    best, best_key = -1, ""
    for i in range(12):
        for prof, suffix in ((major, "major"), (minor, "minor")):
            rotated = np.roll(prof, i)
            corr = float(np.corrcoef(chroma, rotated)[0, 1])
            if corr > best:
                best, best_key = corr, f"{names[i]} {suffix}"
    return {"key": best_key, "confidence": round(max(best, 0), 2)}


def chroma_fingerprint(y, sr=16000, win_s=5.0):
    """
    Compact music fingerprint: per-window chroma mean vector.
    Compare two fingerprints with cosine similarity to detect
    "is this BGM the same as that reference track?"
    Returns [(t, [12 chroma values])].
    """
    import librosa
    win = int(sr * win_s)
    out = []
    for i in range(0, len(y) - win + 1, win):
        seg = y[i:i + win]
        c = librosa.feature.chroma_cqt(y=seg, sr=sr).mean(axis=1)
        out.append((round(i / sr, 1), [round(float(x), 3) for x in c]))
    return out


def fingerprint_match(fp1, fp2):
    """
    Cosine similarity between two chroma fingerprints (0..1).
    >0.85 = very likely same music.
    """
    v1 = np.array([x for _, x in fp1]).ravel()
    v2 = np.array([x for _, x in fp2]).ravel()
    n = min(len(v1), len(v2))
    if n == 0:
        return 0.0
    v1, v2 = v1[:n], v2[:n]
    return float(np.dot(v1, v2) /
                 (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9))


def music_segments(y, sr=16000):
    """
    Find contiguous music regions with their tempo/key.
    Returns [{"start": s, "end": s, "bpm": x, "key": "..."}].
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import audio_deep
    segs = audio_deep.music_vs_speech(y, sr)
    out, cur = [], None
    for t0, t1, label, conf in segs:
        if label == "music" and cur is None:
            cur = [t0, t1]
        elif label == "music" and cur is not None:
            cur[1] = t1
        elif cur is not None:
            s0, s1 = int(cur[0] * sr), int(cur[1] * sr)
            chunk = y[s0:s1]
            info = {"start": cur[0], "end": cur[1]}
            try:
                info.update(tempo_and_beats(chunk, sr))
                info.update(detect_key(chunk, sr))
            except Exception:
                pass
            out.append(info)
            cur = None
    if cur is not None:
        s0, s1 = int(cur[0] * sr), int(cur[1] * sr)
        info = {"start": cur[0], "end": cur[1]}
        try:
            info.update(tempo_and_beats(y[s0:s1], sr))
            info.update(detect_key(y[s0:s1], sr))
        except Exception:
            pass
        out.append(info)
    return out


def noise_profile(y, sr=16000, win_s=1.0):
    """
    Background noise floor estimation per window.
    Returns [(t, noise_floor_db)].
    Rising floor = encroaching hum/hiss; useful for mix QC.
    """
    import librosa
    hop = int(sr * win_s)
    S = np.abs(librosa.stft(y, hop_length=hop))
    # noise floor ~= 10th percentile of magnitudes per frame
    floor = np.percentile(S, 10, axis=0)
    db = 20 * np.log10(floor + 1e-9)
    return [(round(i * win_s, 1), round(float(v), 1))
            for i, v in enumerate(db)]


if __name__ == "__main__":
    import sys, json
    import librosa
    video = sys.argv[1]
    import subprocess
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video,
                    "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
                    "/tmp/aiqc_music.wav"], check=True)
    y, _ = librosa.load("/tmp/aiqc_music.wav", sr=16000)
    if "--tempo" in sys.argv:
        print(json.dumps(tempo_and_beats(y), indent=1))
    elif "--key" in sys.argv:
        print(json.dumps(detect_key(y), indent=1))
    elif "--noise" in sys.argv:
        print(json.dumps(noise_profile(y), indent=1))
    else:
        print(json.dumps({"music_segments": music_segments(y)}, indent=1))
