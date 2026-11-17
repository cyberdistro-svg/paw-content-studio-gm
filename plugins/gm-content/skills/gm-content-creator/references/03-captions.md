# 03 — Caption karaoke & edit ritme

Gaya referensi (video README/DLSS): huruf tebal kapital, putih, **kata aktif kuning**, outline hitam tebal + bayangan, 2–4 kata per kartu, posisi tengah layar, pop kecil saat kata berganti.

## Alur

```bash
python scripts/transcribe.py vo.wav work/ --lang id --device cuda   # words.json (atau tts.py menghasilkan words.json langsung)
python scripts/captions.py work/words.json work/cap.ass --srt work/cap.srt --upper --words 3 \
       --burn master_nocap.mp4 master.mp4 --fontsdir fonts/
```

## Spesifikasi default (`captions.py`)

| Parameter | Default 1080×1920 | Catatan |
|---|---|---|
| Font | font bersih tebal (mis. Plus Jakarta Sans ExtraBold, OFL) | ganti bila brand kit GO Markets mengunci font |
| Ukuran | 92 px | 72–110 px tergantung kepadatan |
| Kata per kartu | 3 | 1–2 untuk talking head energik |
| Warna sorot | `#FFD400` | broker: warna aksen brand kit |
| Outline / bayangan | 7 px / 3 px | wajib di atas video ramai |
| Posisi y | 1180 (≈ 61%) | di luar zona UI TikTok bawah (480 px) & kanan (150 px) |
| Kapital | `--upper` | kapital lebih terbaca untuk ≤ 3 kata |

Koreksi ejaan: whisper sering salah istilah trading (XAUUSD, CHoCH, order block). Perbaiki `words.json` sebelum membakar — buat daftar kamus istilah trading.

## Ritme edit

- Ganti visual tiap 1,5–3 s: cut, punch-in 110–120% (ffmpeg `zoompan`/crop), B-roll, teks.
- Jump cut pada jeda > 0,35 s di talking head (`ffmpeg silencedetect` → potong).
- SFX tipis di pergantian (whoosh/pop).
- Musik −20 s/d −24 LUFS di bawah VO; VO akhir −14 LUFS.
