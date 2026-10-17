#!/usr/bin/env python3
"""
audio_deep.py — Deeper audio analysis for episode QC (vertical scale).

- Emotion/prosody: pitch + energy dynamics -> arousal/valence estimate
- Music vs speech: spectral features distinguish dialogue from BGM/SFX
- Clipping detection: samples at/near digital max
- Volume anomalies: sudden drops, spikes, fade issues
- Overlap detection: two voices talking at once (cross-correlation of
  left/right or spectral doubling)

No torch. librosa + numpy + scipy only.
"""
import numpy as np


def extract_audio(video_path, out_wav="/tmp/aiqc_deep.wav", sr=16000):
    import subprocess
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", video_path,
        "-ac", "1", "-ar", str(sr), "-c:a", "pcm_s16le", out_wav,
    ], check=True)
    return out_wav


def prosody_profile(y, sr=16000, win_s=2.0):
    """
    Per-window emotion/prosody estimate.
    Returns [(t, arousal, valence)] where:
      arousal 0..1: high = loud/fast/pitchy (excited, angry, manic)
      valence -1..1: rough estimate from spectral tilt + pitch contour
    Cipher's manic scenes should show high arousal; Kiko's emotional
    BGM scene should show low arousal.
    """
    import librosa
    win = int(sr * win_s)
    hop = win // 2
    out = []
    for i in range(0, len(y) - win, hop):
        seg = y[i:i + win]
        t = i / sr
        rms = np.sqrt(np.mean(seg ** 2)) + 1e-9
        # pitch
        f0, _, _ = librosa.pyin(seg, fmin=50, fmax=600, sr=sr)
        f0v = f0[~np.isnan(f0)]
        pitch_mean = np.median(f0v) if len(f0v) else 0
        pitch_std = f0v.std() if len(f0v) else 0
        # spectral tilt (bright = higher valence-ish)
        spec = np.abs(np.fft.rfft(seg)) + 1e-9
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        centroid = float(np.sum(freqs * spec) / np.sum(spec))
        # arousal: normalized energy + pitch variance
        arousal = float(np.clip(
            0.5 * np.log10(rms * 100 + 1) +
            0.3 * np.clip(pitch_std / 80, 0, 1) +
            0.2 * np.clip((pitch_mean - 80) / 200, 0, 1), 0, 1))
        # valence: brighter + rising pitch = positive-ish
        valence = float(np.clip(
            0.6 * np.clip((centroid - 1500) / 3000, -1, 1) +
            0.4 * np.clip((pitch_mean - 120) / 150, -1, 1), -1, 1))
        out.append((round(t, 1), round(arousal, 2), round(valence, 2)))
    return out


def music_vs_speech(y, sr=16000, win_s=3.0):
    """
    Per-window classification: speech / music / sfx / silence.
    Uses: zero-crossing rate variance, spectral flux, chroma stability,
    harmonic/percussive ratio.
    Returns [(t_start, t_end, label, confidence)].
    """
    import librosa
    win = int(sr * win_s)
    hop = win
    out = []
    for i in range(0, len(y) - win + 1, hop):
        seg = y[i:i + win]
        t0, t1 = i / sr, (i + win) / sr
        rms = np.sqrt(np.mean(seg ** 2))
        if rms < 1e-4:
            out.append((round(t0, 1), round(t1, 1), "silence", 1.0))
            continue
        zcr = librosa.feature.zero_crossing_rate(seg)[0]
        zcr_var = float(zcr.std())
        # harmonic vs percussive
        D = np.abs(librosa.stft(seg))
        H, P = librosa.decompose.hpss(D)
        harm_ratio = float(np.sum(H) / (np.sum(H) + np.sum(P) + 1e-9))
        # chroma stability (music has stable pitch classes)
        chroma = librosa.feature.chroma_stft(S=D, sr=sr)
        chroma_stab = float(1.0 - np.mean(np.std(chroma, axis=1)))
        # speech: high zcr variance, moderate harmonic ratio
        # music: stable chroma, high harmonic ratio
        # sfx: low harmonic ratio, erratic
        if chroma_stab > 0.55 and harm_ratio > 0.6:
            label, conf = "music", min(0.95, chroma_stab)
        elif zcr_var > 0.02 and 0.3 < harm_ratio < 0.85:
            label, conf = "speech", 0.8
        elif harm_ratio < 0.3:
            label, conf = "sfx", 0.7
        else:
            label, conf = "mixed", 0.5
        out.append((round(t0, 1), round(t1, 1), label, round(conf, 2)))
    return out


def find_clipping(y, sr=16000, thresh=0.99, min_run_ms=5):
    """
    Return [(t_start, t_end)] where the signal clips (>= thresh).
    Clipping = distortion, must be fixed in mix.
    """
    clip = np.abs(y) >= thresh
    run = int(sr * min_run_ms / 1000)
    out, start = [], None
    for i, c in enumerate(clip):
        if c and start is None:
            start = i
        elif not c and start is not None:
            if i - start >= run:
                out.append((round(start / sr, 2), round(i / sr, 2)))
            start = None
    if start is not None and len(clip) - start >= run:
        out.append((round(start / sr, 2), round(len(clip) / sr, 2)))
    return out


def volume_anomalies(y, sr=16000, win_s=1.0, drop_db=12, spike_db=10):
    """
    Find sudden volume drops/spikes vs local median.
    Returns [(t, kind, delta_db)].
    Catches: accidental mutes, pop-in SFX, ducking errors.
    """
    import librosa
    hop = int(sr * win_s)
    rms = librosa.feature.rms(y=y, hop_length=hop)[0] + 1e-9
    db = 20 * np.log10(rms)
    # local median over 10s window
    from scipy.ndimage import median_filter
    med = median_filter(db, size=10, mode="nearest")
    out = []
    for i in range(len(db)):
        d = db[i] - med[i]
        t = round(i * win_s, 1)
        if d <= -drop_db and db[i] > -60:
            out.append((t, "drop", round(float(d), 1)))
        elif d >= spike_db:
            out.append((t, "spike", round(float(d), 1)))
    # merge adjacent
    merged = []
    for t, k, d in out:
        if merged and merged[-1][1] == k and t - merged[-1][0] < 3:
            continue
        merged.append((t, k, d))
    return merged


def overlap_regions(y, sr=16000, win_s=1.0):
    """
    Detect probable overlapping voices via spectral complexity:
    two simultaneous voices show bimodal pitch + elevated spectral
    flatness vs a single voice.
    Returns [(t_start, t_end)] of suspected overlaps.
    """
    import librosa
    win = int(sr * win_s)
    hop = win // 2
    out, start = [], None
    for i in range(0, len(y) - win, hop):
        seg = y[i:i + win]
        t = i / sr
        f0, _, _ = librosa.pyin(seg, fmin=50, fmax=600, sr=sr)
        f0v = f0[~np.isnan(f0)]
        # bimodal pitch = two voices
        overlap = False
        if len(f0v) > 20:
            hist, _ = np.histogram(f0v, bins=10)
            peaks = np.sum(hist > np.max(hist) * 0.4)
            overlap = peaks >= 2 and f0v.std() > 60
        if overlap and start is None:
            start = t
        elif not overlap and start is not None:
            if t - start >= 1.0:
                out.append((round(start, 1), round(t, 1)))
            start = None
    if start is not None:
        out.append((round(start, 1), round(len(y) / sr, 1)))
    return out


if __name__ == "__main__":
    import sys, json
    import librosa
    video = sys.argv[1]
    wav = extract_audio(video)
    y, _ = librosa.load(wav, sr=16000, mono=True)
    sr = 16000
    if "--prosody" in sys.argv:
        print(json.dumps(prosody_profile(y, sr), indent=1))
    elif "--music" in sys.argv:
        print(json.dumps(music_vs_speech(y, sr), indent=1))
    elif "--clip" in sys.argv:
        print(json.dumps(find_clipping(y, sr), indent=1))
    elif "--vol" in sys.argv:
        print(json.dumps(volume_anomalies(y, sr), indent=1))
    elif "--overlap" in sys.argv:
        print(json.dumps(overlap_regions(y, sr), indent=1))
    else:
        print(json.dumps({
            "clipping": find_clipping(y, sr),
            "volume_anomalies": volume_anomalies(y, sr),
            "overlaps": overlap_regions(y, sr),
        }, indent=1))
