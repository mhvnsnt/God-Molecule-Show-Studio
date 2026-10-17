#!/usr/bin/env python3
"""
audio_qc.py — Audio analysis for episode QC.

Gives an AI agent "ears": speech activity detection, silence gaps,
speaker-change detection, and voice-mismatch detection (is the voice
at timestamp T the expected character's voice?).

No torch needed. Uses librosa + webrtcvad + sklearn.
"""
import subprocess
import numpy as np


def extract_audio(video_path, out_wav="/tmp/aiqc_audio.wav", sr=16000):
    """Pull mono 16kHz audio from a video file."""
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", video_path,
        "-ac", "1", "-ar", str(sr), "-c:a", "pcm_s16le", out_wav,
    ], check=True)
    return out_wav


def load_audio(path, sr=16000):
    import librosa
    y, _ = librosa.load(path, sr=sr, mono=True)
    return y


def speech_activity(y, sr=16000, frame_ms=30, aggressiveness=2):
    """Boolean array: is there speech in each frame? (webrtcvad)."""
    import webrtcvad
    vad = webrtcvad.Vad(aggressiveness)
    frame_len = int(sr * frame_ms / 1000)
    n = len(y) // frame_len
    out = np.zeros(n, dtype=bool)
    for i in range(n):
        f = y[i * frame_len:(i + 1) * frame_len]
        pcm = (np.clip(f, -1, 1) * 32767).astype(np.int16).tobytes()
        try:
            out[i] = vad.is_speech(pcm, sr)
        except Exception:
            out[i] = False
    return out


def energy_activity(y, sr=16000, frame_s=0.1, db_threshold=-40):
    """Boolean array from RMS energy — catches any audible content."""
    import librosa
    hop = int(sr * frame_s)
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    db = librosa.amplitude_to_db(rms, ref=np.max(rms) if np.max(rms) > 0 else 1.0)
    return db > db_threshold, db


def find_silence_gaps(y, sr=16000, min_gap_s=2.0, db_threshold=-40):
    """Return [(start_s, end_s)] of silent regions >= min_gap_s."""
    active, _ = energy_activity(y, sr, db_threshold=db_threshold)
    frame_s = 0.1
    gaps, start = [], None
    for i, a in enumerate(active):
        if not a and start is None:
            start = i
        elif a and start is not None:
            dur = (i - start) * frame_s
            if dur >= min_gap_s:
                gaps.append((start * frame_s, i * frame_s))
            start = None
    if start is not None and (len(active) - start) * frame_s >= min_gap_s:
        gaps.append((start * frame_s, len(active) * frame_s))
    return gaps


def mfcc_profile(y, sr=16000, n_mfcc=20):
    """Mean+std MFCC vector — a lightweight voice fingerprint."""
    import librosa
    m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return np.concatenate([m.mean(axis=1), m.std(axis=1)])


def speaker_segments(y, sr=16000, n_speakers=3, seg_s=2.0):
    """
    Cluster fixed-length segments into n_speakers voices via MFCC+KMeans.
    Returns [(start_s, end_s, speaker_id)].
    Catches "wrong voice on a line" when compared against references.
    """
    from sklearn.cluster import KMeans
    import librosa
    seg_len = int(sr * seg_s)
    vecs, times = [], []
    for i in range(0, len(y) - seg_len, seg_len):
        seg = y[i:i + seg_len]
        if np.sqrt(np.mean(seg ** 2)) < 1e-4:
            continue
        vecs.append(mfcc_profile(seg, sr))
        times.append(i / sr)
    if not vecs:
        return []
    X = np.stack(vecs)
    km = KMeans(n_clusters=min(n_speakers, len(X)), n_init=10, random_state=0)
    labels = km.fit_predict(X)
    return [(t, t + seg_s, int(l)) for t, l in zip(times, labels)]


def voice_match_score(y_test, y_ref, sr=16000):
    """
    Cosine similarity between MFCC fingerprints (0..1).
    ~0.9+ = same voice, <0.75 = likely different voice.
    NOTE: blunt metric — prefer VoiceModel.classify() for speaker ID.
    """
    a = mfcc_profile(y_test, sr)
    b = mfcc_profile(y_ref, sr)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


class VoiceModel:
    """
    Per-character voice classifier from reference samples.
    z-scored rich features (MFCC+deltas, pitch, spectral shape/contrast).
    Usage:
        vm = VoiceModel.load_or_build(ref_dir)   # ref_dir has voice-<char>-*.mp3
        pred, dists = vm.classify(y)
    """

    def __init__(self, centroids, mu, sd):
        self.centroids = centroids  # char -> z-scored centroid
        self.mu = mu
        self.sd = sd

    @staticmethod
    def fingerprint(y, sr=16000):
        import librosa
        feats = []
        m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        d1 = librosa.feature.delta(m)
        feats += [m.mean(1), m.std(1), d1.mean(1), d1.std(1)]
        f0, _, _ = librosa.pyin(y, fmin=50, fmax=600, sr=sr)
        f0 = f0[~np.isnan(f0)]
        feats.append(np.array([np.median(f0) if len(f0) else 0,
                               f0.std() if len(f0) else 0]))
        cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        roll = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        feats.append(np.array([cent.mean(), roll.mean(), bw.mean()]))
        feats.append(contrast.mean(1))
        return np.concatenate(feats)

    @classmethod
    def build(cls, ref_dir, sr=16000):
        import glob, os
        import librosa
        chars = {}
        for f in sorted(glob.glob(os.path.join(ref_dir, "voice-*.mp3"))):
            base = os.path.basename(f).lower()
            y, _ = librosa.load(f, sr=sr, mono=True)
            if len(y) < sr:
                continue
            char = None
            for c in ("static", "cipher", "sombra", "ashes", "echo",
                      "onyx", "theory", "kiko", "hollow", "narrator"):
                if f"voice-{c}" in base or f"-{c}-" in base or base.startswith(f"voice-{c}"):
                    char = c
                    break
            if char is None:
                continue
            chars.setdefault(char, []).append(cls.fingerprint(y, sr))
        allv = np.stack([v for vs in chars.values() for v in vs])
        mu, sd = allv.mean(0), allv.std(0) + 1e-9
        centroids = {k: ((np.stack(vs).mean(0) - mu) / sd)
                     for k, vs in chars.items() if vs}
        return cls(centroids, mu, sd)

    def classify(self, y, sr=16000):
        """Returns (predicted_char, {char: distance}). Lowest distance wins."""
        v = (self.fingerprint(y, sr) - self.mu) / self.sd
        d = {k: float(np.linalg.norm(v - c)) for k, c in self.centroids.items()}
        return min(d, key=d.get), d

    def check(self, y, expected_char, sr=16000, margin=1.5):
        """
        Is this the expected character's voice?
        Returns (verdict, predicted, dists). MISMATCH if another char is
        closer by >= margin, UNCERTAIN if within margin.
        """
        pred, d = self.classify(y, sr)
        if pred == expected_char:
            return "MATCH", pred, d
        exp_d = d.get(expected_char, float("inf"))
        if d[pred] + margin < exp_d:
            return "MISMATCH", pred, d
        return "UNCERTAIN", pred, d


def check_voice_at(video_path, t_start, t_end, expected_char,
                   ref_dir="/home/hatch/workspace/voice-delivery", sr=16000):
    """
    "Is the voice between t_start and t_end the expected character's voice?"
    expected_char: 'static' | 'cipher' | 'sombra' | ...
    Returns (verdict, predicted, dists).
    """
    wav = extract_audio(video_path)
    y = load_audio(wav, sr)
    seg = y[int(t_start * sr):int(t_end * sr)]
    vm = VoiceModel.build(ref_dir, sr)
    return vm.check(seg, expected_char, sr)


if __name__ == "__main__":
    import sys, json
    # usage: audio_qc.py <video> --gaps | --speakers N | --check t0 t1 ref_voice
    video = sys.argv[1]
    wav = extract_audio(video)
    y = load_audio(wav)
    sr = 16000
    if "--gaps" in sys.argv:
        print(json.dumps(find_silence_gaps(y, sr), indent=1))
    elif "--speakers" in sys.argv:
        n = int(sys.argv[sys.argv.index("--speakers") + 1])
        print(json.dumps(speaker_segments(y, sr, n_speakers=n), indent=1))
    elif "--check" in sys.argv:
        i = sys.argv.index("--check")
        t0, t1, char = float(sys.argv[i+1]), float(sys.argv[i+2]), sys.argv[i+3]
        v, p, d = check_voice_at(video, t0, t1, char)
        print(json.dumps({"verdict": v, "predicted": p,
                          "distances": {k: round(x, 2) for k, x in d.items()}}))
