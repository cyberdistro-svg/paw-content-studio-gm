#!/usr/bin/env python3
"""sfx.py — "suara juga kode": sintesis SFX + music bed dari cues.json (ditulis render.mjs).
Pakai: python sfx.py cues.json out.wav [--no-bed] [--bpm 100]
Nama cue: whoosh | hit | tick | riser | sub | chime | pop
Tanpa sampel berlisensi; semua dibangkitkan numpy (aman komersial).
Untuk video final klien/broker: ganti bed dengan musik berlisensi lewat render.mjs --audio musik.wav.
"""
import json, sys, wave
import numpy as np

SR = 48000
rs = np.random.default_rng(7)  # seed tetap = deterministik

def env(n, a, r):
    e = np.ones(n); a = max(1, int(a * SR)); r = max(1, int(r * SR))
    e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r) ** 2
    return e

def lowpass(x, cut):
    # satu-kutub, cukup untuk mewarnai noise
    a = np.exp(-2 * np.pi * cut / SR); y = np.zeros_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc; y[i] = acc
    return y

def whoosh(d=0.42):
    n = int(d * SR); x = rs.standard_normal(n)
    cut = np.linspace(400, 6000, n) ** 1.0
    y = np.zeros(n); acc = 0.0
    for i in range(n):
        a = np.exp(-2 * np.pi * cut[i] / SR); acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y * env(n, d * 0.7, d * 0.3) * 1.6

def hit(d=0.5):
    n = int(d * SR); t = np.arange(n) / SR
    f = 120 * np.exp(-t * 18) + 45
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    click = rs.standard_normal(n) * np.exp(-t * 400) * 0.3
    return (body + click) * 0.9

def sub(d=1.2):
    n = int(d * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (38 + 20 * np.exp(-t * 4)) * t) * np.exp(-t * 2.2) * 0.9

def tick(d=0.06):
    n = int(d * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 90) * 0.35

def pop(d=0.12):
    n = int(d * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (900 - 500 * t / d) * t) * np.exp(-t * 40) * 0.4

def chime(d=1.6):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k, (f, g) in enumerate([(880, 1), (1318.5, .55), (1760, .3), (2637, .15)]):
        y += g * np.sin(2 * np.pi * f * t) * np.exp(-t * (2.5 + k))
    return y * 0.35

def riser(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * np.cumsum(np.linspace(200, 900, n)) / SR) * 0.25
    noise = lowpass(rs.standard_normal(n), 3000) * 0.8
    return (tone + noise) * (t / d) ** 2

GEN = dict(whoosh=whoosh, hit=hit, sub=sub, tick=tick, pop=pop, chime=chime, riser=riser)
PRE = dict(riser=1.0)  # riser BERAKHIR di titik cue

def bed(dur, bpm=100):
    """Pad minor hangat + denyut kick ringan. Bukan musik final — penanda tempo."""
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    chords = [[220, 261.6, 329.6], [196, 246.9, 293.7], [174.6, 220, 261.6], [196, 246.9, 329.6]]
    bar = 4 * 60 / bpm
    for i in range(int(dur / bar) + 1):
        s = int(i * bar * SR); e = min(n, int((i + 1) * bar * SR))
        if s >= n: break
        tt = t[s:e] - t[s]
        for f in chords[i % 4]:
            for det in (-0.6, 0.6):
                y[s:e] += np.sin(2 * np.pi * (f + det) * tt) * 0.05
        y[s:e] *= env(e - s, 0.4, 0.4)
    beat = 60 / bpm
    for k in range(int(dur / beat)):
        s = int(k * beat * SR); seg = hit(0.25)[: max(0, min(n - s, int(0.25 * SR)))] * 0.18
        y[s:s + len(seg)] += seg
    return lowpass(y, 2500)

def main():
    src, out = sys.argv[1], sys.argv[2]
    bpm = float(sys.argv[sys.argv.index('--bpm') + 1]) if '--bpm' in sys.argv else 100
    data = json.load(open(src, encoding='utf-8'))
    dur, off = data['duration'], data.get('offset', 0)
    n = int(dur * SR) + SR
    mix = np.zeros(n)
    if '--no-bed' not in sys.argv:
        b = bed(dur + 1, bpm); mix[: len(b)] += b[:n]
    duck = np.ones(n)
    for c in data['cues']:
        g = GEN.get(c['name'])
        if not g: print('cue tak dikenal:', c['name']); continue
        s = g() * c.get('gain', 1)
        start = int((c['t'] - off - PRE.get(c['name'], 0)) * SR)
        if start < 0: s = s[-start:]; start = 0
        end = min(n, start + len(s)); mix[start:end] += s[: end - start]
        if c['name'] in ('hit', 'sub'):
            d = int(0.25 * SR); duck[start:start + d] = np.minimum(duck[start:start + d], np.linspace(0.6, 1, len(duck[start:start + d])))
    mix *= duck
    fade = int(0.6 * SR); end = int(dur * SR); mix = mix[:end]; mix[-fade:] *= np.linspace(1, 0, fade)
    mix = np.tanh(mix * 1.2)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89  # puncak ~ -1 dBFS
    st = np.stack([mix, mix], 1)
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype('<i2').tobytes())
    print('audio ->', out, f'{dur:.2f}s, {len(data["cues"])} cue')

if __name__ == '__main__':
    main()
