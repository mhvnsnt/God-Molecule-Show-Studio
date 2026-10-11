#!/usr/bin/env python3
"""render_midi.py — MIDI file -> WAV using a built-in numpy GM-ish synth.
No FluidSynth binary, no 140MB SoundFont: pure numpy voices
(piano/strings/brass/bass/lead/pad + channel-10 drum kit).
Good for score beds, jingles, sketching cues.

Usage: render_midi.py --input song.mid --output song.wav [--sr 44100]
"""
import argparse
import numpy as np
import soundfile as sf

SR = 44100


def adsr(n, sr, a, d, s, r, gate):
    """ADSR envelope; gate = note length in samples (sustain holds till release)."""
    na, nd, nr = int(a * sr), int(d * sr), int(r * sr)
    sus = max(0, gate - na - nd)
    env = np.zeros(na + nd + sus + nr)
    if na: env[:na] = np.linspace(0, 1, na)
    if nd: env[na:na + nd] = np.linspace(1, s, nd)
    if sus: env[na + nd:na + nd + sus] = s
    if nr: env[na + nd + sus:] = np.linspace(s, 0, nr)
    return env[:n] if len(env) >= n else np.pad(env, (0, n - len(env)))


def tone(freq, n, harmonics, sr=SR):
    t = np.arange(n) / sr
    y = np.zeros(n)
    for h, amp in harmonics:
        y += amp * np.sin(2 * np.pi * freq * h * t)
    return y


# program family -> (harmonics, adsr[a,d,s,r])
FAMILIES = {
    "piano":  ([(1, 1.0), (2, .4), (3, .2), (4, .1)], (.005, .4, .0, .3)),
    "pluck":  ([(1, 1.0), (2, .5), (3, .25)], (.005, .25, .0, .15)),
    "organ":  ([(1, .8), (2, .5), (3, .4), (4, .3)], (.02, .05, .9, .1)),
    "strings": ([(1, .7), (2, .4), (3, .3), (4, .2), (5, .15)], (.15, .2, .8, .3)),
    "brass":  ([(1, .8), (2, .6), (3, .5), (4, .3)], (.08, .1, .8, .15)),
    "reed":   ([(1, 1.0), (3, .4), (5, .2)], (.05, .1, .85, .1)),
    "flute":  ([(1, 1.0), (2, .2), (3, .08)], (.06, .1, .85, .12)),
    "bass":   ([(1, 1.0), (2, .3)], (.01, .1, .7, .1)),
    "lead":   ([(1, .7), (2, .35), (3, .35), (4, .2)], (.01, .05, .9, .1)),
    "pad":    ([(1, .6), (2, .3), (3, .2), (4, .15)], (.4, .3, .8, .5)),
    "bell":   ([(1, 1.0), (2, .3), (3, .15), (5, .1)], (.005, 1.2, .0, .4)),
}


def family_for_program(p):
    if 0 <= p <= 7: return "piano"
    if 8 <= p <= 15: return "bell"
    if 16 <= p <= 23: return "organ"
    if 24 <= p <= 31: return "pluck"
    if 32 <= p <= 39: return "bass"
    if 40 <= p <= 55: return "strings"
    if 56 <= p <= 63: return "brass"
    if 64 <= p <= 71: return "reed"
    if 72 <= p <= 79: return "flute"
    if 80 <= p <= 87: return "lead"
    if 88 <= p <= 95: return "pad"
    return "pluck"


def drum(note, vel, sr=SR):
    dur = {"kick": .35, "snare": .25, "hat": .08, "ohat": .3,
           "tom": .3, "cym": 1.2, "clap": .2}.get
    n = int(sr * 1.5)
    t = np.arange(n) / sr
    rng = np.random.default_rng(note)
    if note == 36:  # kick
        f = 150 * np.exp(-t * 25) + 45
        y = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 9)
    elif note in (38, 40):  # snare
        y = (rng.standard_normal(n) * .5 + np.sin(2 * np.pi * 190 * t) * .5) * np.exp(-t * 18)
    elif note in (42, 44):  # closed hat
        y = rng.standard_normal(n) * np.exp(-t * 90)
        y = np.convolve(y, np.ones(4) / 4, mode="same")
    elif note == 46:  # open hat
        y = rng.standard_normal(n) * np.exp(-t * 12)
        y = np.convolve(y, np.ones(4) / 4, mode="same")
    elif note in (41, 43, 45, 47, 48, 50):  # toms
        base = 120 + (note - 41) * 25
        y = np.sin(2 * np.pi * base * t) * np.exp(-t * 10)
    elif note in (49, 51, 52, 55, 57):  # cymbals
        y = rng.standard_normal(n) * np.exp(-t * 4)
        y = np.convolve(y, np.ones(3) / 3, mode="same")
    elif note == 39:  # clap
        y = rng.standard_normal(n) * np.exp(-t * 30)
    else:
        y = np.sin(2 * np.pi * 220 * t) * np.exp(-t * 12)
    return (y * vel)[:int(sr * 1.5)]


def render(mid_path, sr=SR):
    import mido
    mid = mido.MidiFile(mid_path)
    notes = []  # (start_s, end_s, pitch, vel, program, is_drum)
    for track in mid.tracks:
        abs_t = 0
        tempo = 500000
        prog = 0
        sounding = {}
        for msg in track:
            abs_t += mido.tick2second(msg.time, mid.ticks_per_beat, tempo)
            if msg.type == "set_tempo":
                tempo = msg.tempo
            elif msg.type == "program_change" and msg.channel != 9:
                prog = msg.program
            elif msg.type == "note_on" and msg.velocity > 0:
                sounding[(msg.channel, msg.note)] = (abs_t, msg.velocity / 127, prog)
            elif msg.type in ("note_off",) or (msg.type == "note_on" and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in sounding:
                    st, vel, pr = sounding.pop(key)
                    notes.append((st, abs_t, msg.note, vel, pr, msg.channel == 9))
    for key, (st, vel, pr) in list(sounding.items()):
        ch, note = key
        notes.append((st, st + 1.0, note, vel, pr, ch == 9))
    if not notes:
        return np.zeros(sr), sr
    total = max(e for _, e, *_ in notes) + 1.0
    out = np.zeros(int(total * sr) + sr)
    for st, en, pitch, vel, prog, is_drum in notes:
        if is_drum:
            y = drum(pitch, vel, sr)
        else:
            freq = 440.0 * 2 ** ((pitch - 69) / 12)
            n = int((en - st) * sr) + int(.5 * sr)
            harms, (a, d, s, r) = FAMILIES[family_for_program(prog)]
            y = tone(freq, n, harms, sr) * adsr(n, sr, a, d, s, r, int((en - st) * sr))
            y = y * vel * .5
        o = int(st * sr)
        seg = y[:len(out) - o]
        out[o:o + len(seg)] += seg
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak * .89
    return out, sr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--sr", type=int, default=SR)
    a = ap.parse_args()
    y, sr = render(a.input, a.sr)
    sf.write(a.output, y, sr)
    print(f"rendered -> {len(y)/sr:.1f}s @ {sr}Hz")


if __name__ == "__main__":
    main()
