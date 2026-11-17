#!/usr/bin/env python3
"""ref_dna.py — GenAI Studio: ubah video referensi jadi "DNA" terukur.

Pakai:  python ref_dna.py <url|file.mp4> [--out DIR] [--threshold 0.30] [--max-keyframes 24]
Hasil:  DIR/dna.json, DIR/dna.md (kerangka 5-aspek untuk diisi lewat penglihatan),
        DIR/contact.jpg (lembar kontak keyframe), DIR/kf_XX.jpg

Butuh: ffmpeg + ffprobe. Opsional: yt-dlp (URL), numpy+Pillow (klasifikasi gerak),
faster-whisper (transkrip). Semua angka = ukuran mesin; label gerak = heuristik.
Video referensi hanya untuk analisis internal — jangan diunggah ulang (lihat SKILL.md).
"""
import argparse, json, os, re, shutil, statistics, subprocess, sys

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)

def need(tool):
    if not shutil.which(tool):
        sys.exit(f"[ref_dna] '{tool}' tidak ditemukan. Pasang dulu (mis. apt/winget install ffmpeg).")

def fetch(src, out):
    """URL -> unduh <=720p + info + subtitle otomatis. File lokal -> dipakai apa adanya."""
    if os.path.exists(src):
        return os.path.abspath(src), {}
    ytdlp = [sys.executable, "-m", "yt_dlp"] if run([sys.executable, "-m", "yt_dlp", "--version"]).returncode == 0 \
        else ([shutil.which("yt-dlp")] if shutil.which("yt-dlp") else None)
    if not ytdlp:
        sys.exit("[ref_dna] butuh yt-dlp untuk URL: pip install -U yt-dlp")
    tmpl = os.path.join(out, "ref.%(ext)s")
    r = run(ytdlp + ["-f", "bv*[height<=720]+ba/b[height<=720]/b", "--merge-output-format", "mp4",
                     "--write-info-json", "--write-auto-subs", "--write-subs", "--sub-langs", "id.*,en.*",
                     "--sub-format", "vtt", "--no-playlist", "-o", tmpl, src])
    if r.returncode != 0:
        sys.exit("[ref_dna] yt-dlp gagal:\n" + r.stderr[-1500:])
    vid = next((os.path.join(out, f) for f in os.listdir(out) if f.startswith("ref.") and f.endswith(".mp4")), None)
    info = {}
    ij = os.path.join(out, "ref.info.json")
    if os.path.exists(ij):
        d = json.load(open(ij, encoding="utf-8"))
        info = {k: d.get(k) for k in ("title", "uploader", "channel", "upload_date", "view_count",
                                      "like_count", "comment_count", "duration", "webpage_url", "tags")}
    return vid, info

def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path])
    d = json.loads(r.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    fr = v.get("avg_frame_rate", "0/1").split("/")
    fps = float(fr[0]) / float(fr[1]) if len(fr) == 2 and float(fr[1]) else 0.0
    w, h = int(v.get("width", 0)), int(v.get("height", 0))
    ratio = "9:16" if h > w * 1.5 else "16:9" if w > h * 1.5 else "1:1" if abs(w - h) < 0.1 * max(w, h, 1) else f"{w}:{h}"
    return {"duration": float(d.get("format", {}).get("duration", 0)), "width": w, "height": h,
            "fps": round(fps, 2), "aspect": ratio, "has_audio": a is not None}

def detect_cuts(path, thr):
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-filter:v", f"select='gt(scene,{thr})',showinfo",
             "-an", "-f", "null", "-"])
    return sorted({round(float(m), 3) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)})

def loudness(path):
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-vn", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[0-9.]+) LUFS", r.stderr)
    s = run(["ffmpeg", "-hide_banner", "-i", path, "-af", "silencedetect=n=-40dB:d=0.4", "-vn", "-f", "null", "-"])
    sil = sum(float(x) for x in re.findall(r"silence_duration: ([0-9.]+)", s.stderr))
    return (float(m[-1]) if m else None), round(sil, 2)

def grab(path, t, dst, w=360):
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", path,
         "-frames:v", "1", "-vf", f"scale={w}:-2", dst])
    return os.path.exists(dst)

def motion_score(path, a, b, tmpdir):
    """Selisih rata-rata 3 frame dalam satu shot (0..255). None bila numpy/Pillow tak ada."""
    try:
        import numpy as np
        from PIL import Image
    except Exception:
        return None
    ts = [a + (b - a) * f for f in (0.2, 0.5, 0.8)]
    arrs = []
    for i, t in enumerate(ts):
        p = os.path.join(tmpdir, f"_m{i}.jpg")
        if grab(path, t, p, 160):
            arrs.append(np.asarray(Image.open(p).convert("L"), dtype="float32"))
            os.remove(p)
    if len(arrs) < 2:
        return None
    return round(float(sum(abs(arrs[i + 1] - arrs[i]).mean() for i in range(len(arrs) - 1)) / (len(arrs) - 1)), 2)

def contact_sheet(paths, dst, cols):
    """Lembar kontak berlabel nomor shot. Pillow bila ada; jika tidak, ffmpeg concat (jalan juga di Windows)."""
    try:
        from PIL import Image, ImageDraw
        ims = [Image.open(p).convert("RGB") for p in paths]
        w = 240; h = max(int(im.height * w / im.width) for im in ims)
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (w + 4) + 4, rows * (h + 4) + 4), "white")
        for i, (im, p) in enumerate(zip(ims, paths)):
            im = im.resize((w, int(im.height * w / im.width)))
            x, y = 4 + (i % cols) * (w + 4), 4 + (i // cols) * (h + 4)
            sheet.paste(im, (x, y))
            ImageDraw.Draw(sheet).text((x + 6, y + 4), os.path.basename(p)[3:-4], fill="yellow")
        sheet.save(dst, quality=88)
        return
    except ImportError:
        pass
    lst = dst + ".txt"
    with open(lst, "w", encoding="utf-8") as f:
        f.writelines(f"file '{os.path.abspath(p).replace(chr(92), '/')}'\n" for p in paths)
    rows = (len(paths) + cols - 1) // cols
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-vf", f"scale=240:-2,tile={cols}x{rows}:padding=4:color=white", "-frames:v", "1", dst])
    os.remove(lst)

def motion_label(score):
    if score is None:
        return "tidak_diukur"
    return "statis" if score < 1.5 else "still_bergerak(pan/zoom)" if score < 6 else "klip_gerak"

def transcript(path, out):
    vtt = [f for f in os.listdir(out) if f.endswith(".vtt")]
    if vtt:
        txt = open(os.path.join(out, vtt[0]), encoding="utf-8", errors="ignore").read()
        lines = [l for l in txt.splitlines() if l and "-->" not in l and not l.startswith(("WEBVTT", "Kind:", "Language:"))]
        dedup = [l for i, l in enumerate(lines) if i == 0 or l != lines[i - 1]]
        return {"sumber": "subtitle " + vtt[0], "teks": re.sub(r"<[^>]+>", "", " ".join(dedup))[:6000]}
    try:
        from faster_whisper import WhisperModel
    except Exception:
        return {"sumber": "tidak ada (pasang faster-whisper untuk transkrip)", "teks": ""}
    model = WhisperModel("small", device="auto", compute_type="int8")
    segs, info = model.transcribe(path, vad_filter=True)
    segs = list(segs)
    return {"sumber": f"faster-whisper small ({info.language})", "teks": " ".join(s.text.strip() for s in segs)[:6000],
            "kata_pertama_detik": round(segs[0].start, 2) if segs else None}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", default="ref_dna_out")
    ap.add_argument("--threshold", type=float, default=0.30)
    ap.add_argument("--max-keyframes", type=int, default=24)
    a = ap.parse_args()
    need("ffmpeg"); need("ffprobe")
    os.makedirs(a.out, exist_ok=True)
    vid, info = fetch(a.src, a.out)
    meta = probe(vid)
    cuts = [c for c in detect_cuts(vid, a.threshold) if 0.05 < c < meta["duration"] - 0.05]
    bounds = [0.0] + cuts + [meta["duration"]]
    shots = [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1) if bounds[i + 1] - bounds[i] > 0.04]
    lens = [round(b - s, 2) for s, b in shots]
    step = max(1, len(shots) // a.max_keyframes + (1 if len(shots) % a.max_keyframes else 0))
    shot_rows, kfs = [], []
    for i, (s, b) in enumerate(shots):
        row = {"no": i + 1, "mulai": round(s, 2), "selesai": round(b, 2), "durasi": round(b - s, 2)}
        if i % step == 0 and len(kfs) < a.max_keyframes:
            kp = os.path.join(a.out, f"kf_{i + 1:03d}.jpg")
            if grab(vid, (s + b) / 2, kp):
                row["keyframe"] = os.path.basename(kp); kfs.append(kp)
            sc = motion_score(vid, s, b, a.out)
            row["gerak_skor"], row["gerak"] = sc, motion_label(sc)
        shot_rows.append(row)
    if kfs:
        contact_sheet(kfs, os.path.join(a.out, "contact.jpg"), min(6 if meta["aspect"] == "9:16" else 4, len(kfs)))
    lufs, sil = loudness(vid) if meta["has_audio"] else (None, None)
    labels = [r["gerak"] for r in shot_rows if "gerak" in r and r["gerak"] != "tidak_diukur"]
    dna = {
        "sumber": a.src, "info_platform": info, "teknis": meta,
        "ritme": {"jumlah_shot": len(shots), "cut_per_menit": round(len(cuts) / max(meta["duration"], 1e-6) * 60, 1),
                  "shot_rata2_detik": round(statistics.mean(lens), 2) if lens else None,
                  "shot_median_detik": round(statistics.median(lens), 2) if lens else None,
                  "cut_pertama_detik": cuts[0] if cuts else None,
                  "ambang_scene": a.threshold},
        "gerak_ringkas": {l: labels.count(l) for l in sorted(set(labels))},
        "audio": {"lufs_terintegrasi": lufs, "total_hening_detik": sil},
        "transkrip": transcript(vid, a.out), "shot": shot_rows,
        "contact_sheet": "contact.jpg" if kfs else None,
        "catatan": "Angka = ukuran mesin. Label gerak = heuristik selisih frame; verifikasi dengan melihat keyframe.",
    }
    json.dump(dna, open(os.path.join(a.out, "dna.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    r = dna["ritme"]
    md = f"""# DNA Referensi — {info.get('title') or os.path.basename(a.src)}

**Teknis:** {meta['duration']:.1f} s · {meta['width']}x{meta['height']} ({meta['aspect']}) · {meta['fps']} fps · audio {'ya' if meta['has_audio'] else 'tidak'}
**Ritme (mesin):** {r['jumlah_shot']} shot · {r['cut_per_menit']} cut/menit · rata2 {r['shot_rata2_detik']} s · median {r['shot_median_detik']} s · cut pertama {r['cut_pertama_detik']} s
**Gerak (heuristik):** {dna['gerak_ringkas'] or 'tidak diukur'}
**Audio:** {lufs} LUFS · hening total {sil} s
**Transkrip:** {dna['transkrip']['sumber']}

> Isi bagian di bawah dengan MELIHAT contact.jpg + keyframe. Tulis N/A bila tidak berlaku — jangan dikosongkan diam-diam.

## Hook (0–3 s)
- Visual pertama:
- Kalimat/teks pertama:
- Teknik hook (pertanyaan / klaim tak terduga / hasil dulu / konflik / pola-putus):

## 5 aspek per kelompok shot
| Shot | Subjek | Gerak subjek | Scene (+overlay teks terpisah) | Framing | Kamera (lensa, tinggi, sudut, fokus, gerak) |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Rupa
- Palet dominan:
- Tipografi / caption:
- Transisi:

## Struktur naratif & CTA
-

## Yang DIPERTAHANKAN / DIUBAH (untuk konten GO Markets)
| Pertahankan (ritme, struktur, energi) | Ubah (topik, identitas, aset, klaim) |
|---|---|
|  |  |
"""
    open(os.path.join(a.out, "dna.md"), "w", encoding="utf-8").write(md)
    print(json.dumps({"ok": True, "out": os.path.abspath(a.out), "shot": len(shots), "cut_per_menit": r["cut_per_menit"],
                      "keyframe": len(kfs), "lufs": lufs}, ensure_ascii=False))

if __name__ == "__main__":
    main()
