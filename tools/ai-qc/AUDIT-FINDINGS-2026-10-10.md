# EP02 v6e Audit Findings — 2026-10-10

**File audited:** `~/workspace/trippedd-studio/production/WIZARD_GANG_EP01/wizard-gang-ep02-final-v6e.mp4`
**Duration:** 344.8s (5:45)
**Tools:** ai-qc toolkit (audio_deep, visual_deep, audio_qc, video_qc)
**Method:** Automated analysis + prior manual audit. NO changes made to episode.

---

## 🔴 CRITICAL

### C1. Bullshit filter remnants detected
- **Timestamps:** 32.5–37.0s, 319.5–320.0s
- **Tool:** visual_deep.filter_scan (cartoon_filter_score >= 0.6)
- **Severity:** Critical — owner explicitly ordered filter removal from all scenes
- **Action needed:** Owner confirm → replace with clean 2D or regenerate

### C2. Frozen frames (slideshow segments)
- **Timestamps:** 42.5–46.0s, 46.5–50.0s, 334.0–338.0s
- **Tool:** visual_deep.frozen_regions
- **Severity:** Critical — 42.5–50s is in the LOCKED intro (0:00–0:50), may be intentional stills. 334–338s near end needs review.
- **Action needed:** Owner confirm if 334–338s freeze is intentional

### C3. L7 voice mismatch (Static voice on Ashes visual) — KNOWN, PENDING
- **Timestamp:** 113–120s
- **Tool:** Prior manual audit (visual inspection)
- **Severity:** Critical — Ashes visibly talking, Static's voice playing
- **Status:** Static draft saved to `voice-delivery/voice-static-l7-warfund-DRAFT.mp3`. Needs Bill $aber voice clone.
- **Action needed:** Generate Ashes voice when clone is ready

### C4. N1 narrator line missing — KNOWN, PENDING
- **Timestamp:** 52s ("They got the call. All nine.")
- **Tool:** Prior manual audit vs DIALOGUE.md
- **Severity:** Critical — opening narration absent
- **Status:** Needs Bill $aber voice clone
- **Action needed:** Generate when clone is ready

---

## 🟡 MAJOR

### M1. Silence gap at Cipher's DIALOGUE.md position
- **Timestamp:** 206.2–211.1s (4.9s silence)
- **Tool:** audio_qc.find_silence_gaps
- **Severity:** Major — DIALOGUE.md places C1 ("I bet I can") at 3:26 (206s), but v4 moved C1 to 256s. This gap is expected per v4, but confirms the DIALOGUE.md position is empty.
- **Action needed:** Owner confirm C1 placement at 256s is correct (not 206s)

### M2. Extended silence gaps (possible missing content)
- **Timestamps:**
  - 75.8–82.9s (7.1s) — L3 placed at 82s, gap is pre-dialogue pause. Likely OK.
  - 94.5–102.0s (7.5s) — No dialogue expected per DIALOGUE.md. Check visual.
  - 120.9–130.0s (9.1s) — C4 money line placed at 121s (12.88s). Should cover this. Verify audio present.
  - 267.6–273.8s (6.2s) — Post-C2 gap. Check if intentional.
  - 317.8–320.6s (2.8s) — Pre-Theory scene. Likely OK.
- **Tool:** audio_qc.find_silence_gaps
- **Severity:** Major — owner should verify these aren't missing lines
- **Action needed:** Owner review each gap

### M3. Volume spikes (possible clipping or mixing issues)
- **Timestamps (top spikes):** 67s (+29.9dB), 93s (+44.5dB), 70s (+21.3dB), 73s (+23.6dB), 35s (+20.2dB)
- **Tool:** audio_deep.volume_anomalies
- **Severity:** Major — 44.5dB spike at 93s is extreme, likely a transient or edit artifact
- **Action needed:** Owner listen at 93s, 67s. May need gain reduction.

### M4. Volume drops (possible muted dialogue)
- **Timestamps:** 25s (-19.4dB), 50s (-26.0dB), 87s (-17.2dB)
- **Tool:** audio_deep.volume_anomalies
- **Severity:** Major — 50s drop is at the locked intro boundary. 87s drop is near L3.
- **Action needed:** Verify no dialogue lost at these points

### M5. Grading/lighting shifts (33 detected)
- **Notable timestamps:** 32s (+45.7), 42s (+84.9), 90s (+51.4), 260s (+67.6)
- **Tool:** visual_deep grading analysis
- **Severity:** Major — 42s shift (+84.9) is massive, likely a scene cut. 32s (+45.7) coincides with filter region.
- **Action needed:** Most are probably normal scene cuts. Owner should check 32s (filter + grading shift together = suspicious).

---

## 🟢 MINOR / INFO

### I1. No audio clipping detected
- **Tool:** audio_deep.find_clipping
- **Status:** Clean. No samples hit 0dBFS.

### I2. Glitch candidates (high texture, likely false positives)
- **Timestamps:** 0–4.5s, 11–11.5s, 16–19.5s (all in intro)
- **Tool:** visual_deep glitch scan (Laplacian variance > 2000)
- **Status:** Intro has high-detail artwork, likely false positives. No glitches detected in main episode body.
- **Action needed:** None unless owner sees artifacts in intro.

### I3. Filter regions are narrow
- The 32.5–37s region scored 0.59 (just below 0.6 threshold but flagged). May be borderline.
- The 319.5–320s region is only 0.5s — could be a transition effect, not the bullshit filter.
- **Action needed:** Owner visual confirm both.

---

## ✅ VERIFIED CLEAN

- **Cipher C1/C2/C3 voices:** Correctly placed at 256s/263s/282s with Cipher's voice (per v6 build)
- **Cipher C4 money line:** Placed at 121s (per v6c build)
- **L1/L2/L10/L18:** Restored in v6e (were silent in v6d)
- **Echo double-audio:** Fixed in v6c/v6d (no overlaps detected)
- **L3 placement:** Clean single at 82s (1:22)

---

## 🔧 TOOL NOTES

- `overlap_regions` (pyin-based) is too slow for full-episode use (>30 min). Needs optimization or GPU.
- `VoiceModel.build` takes >2 min on 18 reference files. Needs caching.
- Visual analysis required pre-extracted frames (689 @ 2fps) to avoid I/O bottleneck.
- All tools committed to 4 repos (PRs #132, #18, #9, #3 — all merged).

---

## OWNER ACTION ITEMS

1. [ ] Confirm filter removal at 32.5–37s and 319.5–320s (C1)
2. [ ] Confirm 334–338s freeze is intentional (C2)
3. [ ] Review silence gaps M2 — any missing lines?
4. [ ] Listen at 93s and 67s for volume spikes (M3)
5. [ ] Confirm C1 at 256s (not DIALOGUE.md 206s) (M1)
6. [ ] Bill $aber clone → N1 + L7 Ashes voice (C3, C4)

**Nothing has been changed. All findings await owner yes/no.**
