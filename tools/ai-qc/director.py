#!/usr/bin/env python3
"""
director.py — The BRAIN. Multi-modal reasoning over all QC findings.

Takes findings from every module and synthesizes them the way a human
director would: "at 3:42 the lighting shifts AND the voice doesn't
match AND there's blockiness — this whole shot is a bad composite."

Input: dict of {module: findings} (from qc.py full run).
Output: prioritized director notes, each combining related signals.

Severity: critical > major > minor > note.
"""
import json


def _t_of(f):
    """Extract a representative timestamp from a finding dict."""
    if isinstance(f, (list, tuple)) and len(f) >= 1 \
            and isinstance(f[0], (int, float)):
        return float(f[0])
    if isinstance(f, dict):
        if "t" in f:
            return float(f["t"])
        if "window" in f:
            return float(f["window"][0])
    return None


def _near(a, b, tol=5.0):
    return abs(a - b) <= tol


def synthesize(findings):
    """
    findings: {
      "voice_mismatches": [...], "av_sync": [...], "clipping": [...],
      "volume_anomalies": [...], "frozen": [...], "grading_shifts": [...],
      "filter_regions": [...], "glitches": [...], "lighting_jumps": [...],
      "likeness_drift": [...], "overlaps": [...], "silence_gaps": [...],
      ...
    }
    Returns [director_note], each:
      {"t": s, "severity": "...", "title": "...", "signals": [...],
       "suggestion": "..."}
    """
    notes = []

    def add(t, severity, title, signals, suggestion=""):
        notes.append({"t": round(float(t), 1), "severity": severity,
                      "title": title, "signals": signals,
                      "suggestion": suggestion})

    # --- composite failure: multiple visual signals at same timestamp ---
    visuals = []
    for key in ("grading_shifts", "filter_regions", "glitches",
                "lighting_jumps", "likeness_drift"):
        for f in findings.get(key, []):
            t = _t_of(f)
            if t is not None:
                visuals.append((t, key, f))
    # cluster visuals within 5s
    used = set()
    for i, (t, key, f) in enumerate(visuals):
        if i in used:
            continue
        cluster = [(t, key, f)]
        for j, (t2, k2, f2) in enumerate(visuals):
            if j != i and j not in used and _near(t, t2):
                cluster.append((t2, k2, f2))
                used.add(j)
        used.add(i)
        if len(cluster) >= 2:
            keys = sorted(set(k for _, k, _ in cluster))
            add(t, "major",
                f"Composite problem at {t:.0f}s ({len(cluster)} visual signals)",
                [f"{k}: {f}" for _, k, f in cluster],
                "This shot likely needs re-render or replacement, "
                "not a tweak.")

    # --- voice + mouth mismatch ---
    for f in findings.get("voice_mismatches", []):
        t = _t_of(f)
        if t is None:
            continue
        av = [a for a in findings.get("av_sync", [])
              if _t_of(a) is not None and _near(_t_of(a), t)]
        sev = "critical" if not av else "major"
        add(t, sev, f"Wrong voice at {t:.0f}s", [f"voice: {f}"] +
            [f"av: {a}" for a in av],
            "Replace with correct character voice file.")

    # --- silent mouths ---
    for f in findings.get("av_sync", []):
        if isinstance(f, dict) and f.get("kind") == "mouth_no_audio":
            t = _t_of(f)
            add(t, "major", f"Talking with no dialogue at {t:.0f}s",
                [f"av: {f}"],
                "Character mouth moves but no line plays — needs dialogue.")

    # --- audio problems ---
    for t0, t1 in findings.get("clipping", []):
        add(t0, "major", f"Audio clipping at {t0:.0f}s",
            [f"clipping: {t0}-{t1}s"], "Reduce gain in mix.")
    for t, kind, db in findings.get("volume_anomalies", []):
        sev = "major" if kind == "drop" else "minor"
        add(t, sev, f"Volume {kind} ({db}dB) at {t:.0f}s",
            [f"volume: {kind} {db}dB"],
            "Check mix automation at this point.")
    for t0, t1 in findings.get("overlaps", []):
        add(t0, "minor", f"Overlapping voices at {t0:.0f}s",
            [f"overlap: {t0}-{t1}s"],
            "Verify intentional (crowd) or fix timing.")

    # --- frozen / still ---
    for w in findings.get("frozen_regions", []) + \
            findings.get("still_regions", []):
        t0 = w[0] if isinstance(w, (list, tuple)) else _t_of(w)
        if t0:
            add(t0, "major", f"Frozen/still segment at {t0:.0f}s",
                [f"frozen: {w}"],
                "Slideshow or stuck render — needs real animation.")

    # --- silence gaps in dialogue-heavy episode ---
    for t0, t1 in findings.get("silence_gaps", []):
        if t1 - t0 > 8:  # long gaps only; short ones are scene transitions
            add(t0, "note", f"Long silence {t0:.0f}-{t1:.0f}s",
                [f"gap: {t0}-{t1}s"],
                "Confirm intentional (dramatic pause) or missing audio.")

    # --- sort by severity then time ---
    order = {"critical": 0, "major": 1, "minor": 2, "note": 3}
    notes.sort(key=lambda n: (order.get(n["severity"], 9), n["t"]))

    # --- dedupe near-identical ---
    dedup = []
    for n in notes:
        if not any(d["title"] == n["title"] and _near(d["t"], n["t"], 3)
                   for d in dedup):
            dedup.append(n)
    return dedup


def format_notes(notes):
    """Human-readable director notes."""
    lines = []
    for n in notes:
        lines.append(f"[{n['severity'].upper()}] {n['t']:.0f}s — {n['title']}")
        for s in n["signals"][:4]:
            lines.append(f"    · {s}")
        if n["suggestion"]:
            lines.append(f"    → {n['suggestion']}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    # usage: director.py findings.json
    with open(sys.argv[1]) as f:
        findings = json.load(f)
    notes = synthesize(findings)
    print(format_notes(notes))
    print(f"\n{len(notes)} director notes.")
