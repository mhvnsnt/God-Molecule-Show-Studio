#!/usr/bin/env python3
"""
multimodal.py — Vision + audio understood TOGETHER, not as two pipelines.

JointEmbedder: per time-window, visual features (mean over frames) and
audio features are concatenated into one joint vector, standardized, and
projected with PCA into a compact joint embedding space. In that space:

  - joint_similarity(seg_a, seg_b): cosine similarity of joint embeddings
    ("these two moments feel the same" across BOTH modalities)
  - cross_modal_search(query window): nearest windows by joint embedding
    ("find me another moment that looks AND sounds like this")
  - coherence(): does the SOUND follow the ACTION? Pearson correlation
    between the visual-motion envelope and the audio-energy envelope.
    High coherence = sound design glued to picture (action scenes);
    low coherence with high audio energy = possible dub/score mismatch.

  - caption(window): heuristic multimodal caption from joint features —
    loud/quiet x still/moving x speech-like/music-like. A toy, but it
    reasons across modalities instead of in silos.

No neural multimodal model (ImageBind / VideoLLaMA need GPU + torch;
see SENSORIUM.md for the roadmap). This is the CPU-runnable version:
statistical joint embeddings, honest about what they are.

CPU-only: sklearn + numpy + OpenCV + librosa.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from features import (visual_vector, audio_vector, sample_video_frames,
                      extract_audio_mono)


class JointEmbedder:
    """
    Fit on one video (or a corpus): learns the scaler + PCA that define
    the joint space. Then embed any window of any video.
    """

    def __init__(self, n_components=8, window_s=2.0, sr=16000):
        self.n_components = n_components
        self.window_s = window_s
        self.sr = sr
        self.scaler_ = None
        self.pca_ = None

    # ------------------------------------------------------------ fit ---
    def _window_vectors(self, video_path):
        """Joint raw vectors, one per window_s across the video."""
        y, sr, tmp = extract_audio_mono(video_path, sr=self.sr)
        try:
            frames = list(sample_video_frames(video_path,
                                              sample_fps=4.0))
            if not frames:
                return np.zeros((0, 1)), []
            win = self.window_s
            t_max = frames[-1][0]
            vecs, spans = [], []
            n_win = int(sr * win)
            i = 0
            t = 0.0
            while t + win <= t_max + 1e-6:
                # visual: mean of frame vecs in window
                fvecs = [visual_vector(f) for ft, f in frames
                         if t <= ft < t + win]
                v = np.mean(fvecs, axis=0) if fvecs else np.zeros(14)
                # audio
                a0 = int(t * sr)
                a = audio_vector(y[a0:a0 + n_win], sr=sr)
                vecs.append(np.concatenate([v, a]))
                spans.append((round(t, 2), round(t + win, 2)))
                t += win
            return np.array(vecs), spans
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    def fit(self, video_path):
        from sklearn.preprocessing import StandardScaler
        from sklearn.decomposition import PCA
        X, self.spans_ = self._window_vectors(video_path)
        if len(X) < self.n_components + 1:
            raise ValueError("video too short to fit joint space")
        self.scaler_ = StandardScaler().fit(X)
        self.pca_ = PCA(n_components=self.n_components,
                        random_state=7).fit(self.scaler_.transform(X))
        self.train_spans_ = self.spans_
        return self

    # ---------------------------------------------------------- embed ---
    def embed_window(self, video_path, t0, t1):
        """Joint embedding for an arbitrary window of a video."""
        y, sr, tmp = extract_audio_mono(video_path, sr=self.sr)
        try:
            fvecs = [visual_vector(f) for _, f in
                     sample_video_frames(video_path, sample_fps=4.0,
                                         t0=t0, t1=t1)]
            v = np.mean(fvecs, axis=0) if fvecs else np.zeros(14)
            a0, a1 = int(t0 * sr), int(t1 * sr)
            a = audio_vector(y[a0:a1], sr=sr)
            x = np.concatenate([v, a]).reshape(1, -1)
            z = self.pca_.transform(self.scaler_.transform(x))
            return z[0] / (np.linalg.norm(z[0]) + 1e-9)
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    # -------------------------------------------------------- compare ---
    @staticmethod
    def similarity(e1, e2):
        return float(np.dot(e1, e2))

    def cross_modal_search(self, video_path, q0, q1, top_n=5,
                           exclude=(None, None)):
        """
        Given query window [q0,q1], find the top_n most similar windows
        in the fitted corpus by JOINT embedding (looks+sound together).
        Returns [(span, similarity)].
        """
        q = self.embed_window(video_path, q0, q1)
        scored = []
        for (s0, s1) in self.train_spans_:
            if exclude[0] is not None and not (s1 <= exclude[0]
                                              or s0 >= exclude[1]):
                continue
            e = self.embed_window(video_path, s0, s1)
            scored.append(((s0, s1), self.similarity(q, e)))
        scored.sort(key=lambda x: -x[1])
        return scored[:top_n]

    # ------------------------------------------------------ coherence ---
    def coherence(self, video_path, t0=0.0, t1=None):
        """
        Does the sound follow the action? Pearson r between:
          visual: mean abs frame-difference (motion envelope), 4 fps
          audio:  RMS energy envelope, 250ms windows
        Returns (r, n_points). r near 1 = tightly glued sound design.
        """
        import cv2
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"cannot open {video_path}")
        src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(1, int(round(src_fps / 4.0)))
        motion, prev, idx = [], None, 0
        start = int(t0 * src_fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start)
        idx = start
        end = int(t1 * src_fps) if t1 else int(1e12)
        while idx < end:
            ok, frame = cap.read()
            if not ok:
                break
            if (idx - start) % step == 0:
                g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(
                    np.float32) / 255.0
                if prev is not None:
                    motion.append(float(np.abs(g - prev).mean()))
                prev = g
            idx += 1
        cap.release()

        y, sr, tmp = extract_audio_mono(video_path, sr=self.sr)
        try:
            w = sr // 4
            a0 = int(t0 * sr)
            a1 = int(t1 * sr) if t1 else len(y)
            seg = y[a0:a1]
            energy = np.array([np.sqrt(np.mean(seg[i:i + w] ** 2)) + 1e-9
                               for i in range(0, len(seg) - w, w)])
            n = min(len(motion), len(energy))
            if n < 8:
                return 0.0, n
            m = np.array(motion[:n])
            e = energy[:n]
            if m.std() < 1e-9 or e.std() < 1e-9:
                return 0.0, n
            r = float(np.corrcoef(m, e)[0, 1])
            return r, n
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    # -------------------------------------------------------- caption ---
    def caption(self, video_path, t0, t1):
        """
        Heuristic multimodal caption: combines loudness, motion,
        speech-likeness and brightness into one line. Toy, but it
        reads both streams at once.
        """
        y, sr, tmp = extract_audio_mono(video_path, sr=self.sr)
        try:
            a0, a1 = int(t0 * sr), int(t1 * sr)
            seg = y[a0:a1] if a1 > a0 else y[:sr]
            rms = float(np.sqrt(np.mean(seg ** 2)) + 1e-9)
            a = audio_vector(seg, sr=sr)
            # speech-like: strong mid MFCC energy + moderate zcr
            speechy = float(a[8] + a[9] + a[10])  # mfcc00..02 region
            fvecs = [visual_vector(f) for _, f in
                     sample_video_frames(video_path, sample_fps=4.0,
                                         t0=t0, t1=t1)]
            bright = float(np.mean([v[2] for v in fvecs])) if fvecs \
                else 50.0
            # motion between first/last sampled frame
            motion = "moving" if len(fvecs) > 1 and float(
                np.linalg.norm(fvecs[-1] - fvecs[0])) > 3.0 else "still"
            loud = ("loud" if rms > 0.08 else "quiet"
                    if rms < 0.015 else "mid-volume")
            sound = "speech" if speechy > -20 else "music/sfx"
            look = "bright" if bright > 55 else "dark" if bright < 40 \
                else "mid-tone"
            return (f"{t0}-{t1}s: {loud} {sound} over {motion}, "
                    f"{look} picture")
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass
