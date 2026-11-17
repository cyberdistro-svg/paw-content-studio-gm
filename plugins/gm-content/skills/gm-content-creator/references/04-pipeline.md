# 04 — Pipeline produksi, repurpose, lokalisasi

Diadaptasi dari **krillinai/OpenCreator** (Apache-2.0): workspace kreator yang memakai agen sebagai mesin, dengan skill `subtitle → tts → render-horizontal/vertical → cover`, `pipeline` (validasi rencana dry-run), versi per revisi, dan memori global/proyek/thread. Kita ambil **polanya**, bukan aplikasinya (aplikasinya opsional dipasang — lihat bawah).

## Jalur produksi

| Jalur | Kapan | Alat |
|---|---|---|
| **Motion/faceless** | promo produk, before/after, list | motion kode (tiket pabrik) |
| **Screen tutorial** | cara pakai | OBS / Playwright `recordVideo` / `mobile-mcp`; potong ffmpeg |
| **Talking head** | personal brand, live clip | kamera HP 4K 30fps, cahaya depan; jump cut + caption |
| **AI B-roll** | ilustrasi abstrak | Higgsfield/Kling/Veo (label AI bila realistis), tidak untuk "bukti" |

## Rencana pipeline (wajib ditulis sebelum eksekusi — gaya `krillinai-pipeline` dry-run)

```json
{ "id": "gm_20261117_showcase_v1",
  "steps": [
    {"do": "screenshot", "in": "https://…", "out": "work/page.png"},
    {"do": "tts", "in": "naskah.txt", "voice": "id-ID-ArdiNeural", "out": "work/"},
    {"do": "render", "tpl": "templates/showcase-9x16", "audio": "work/vo.mp3", "out": "work/nocap.mp4"},
    {"do": "captions", "in": "work/words.json", "burn": ["work/nocap.mp4", "out/final.mp4"]},
    {"do": "qa", "in": "out/final.mp4"} ] }
```
Cek dulu: semua input ada, alat terpasang, durasi VO cocok dengan template. Setiap revisi → `_v2`, `_v3` (jangan menimpa).

## Repurpose (1 long → banyak short)

1. `transcribe.py` video panjang → `transcript.txt` bertimestamp.
2. Pilih 3–6 momen: kalimat yang berdiri sendiri, ada hook di 3 detik pertama, 20–50 s, satu ide.
3. `reframe.py long.mp4 clip1.mp4 --from 312.4 --to 351.0 --mode blurfill` (layar/chart) atau `--mode crop --x 0.45` (wajah).
4. Caption ulang dari potongan `words.json` (geser waktu ke 0), tambah hook teks layar di 0–2 s.

## Lokalisasi (terjemah + dubbing)

`transcribe.py` → terjemahkan per segmen dengan LLM (pertahankan istilah trading, panjang kalimat ±10%) → `tts.py --voice en-US-AndrewNeural` → atur kecepatan (`atempo` 0,9–1,15) agar pas durasi → caption bahasa target. Selalu tandai "AI dubbed" bila suara sintetis meniru pembicara asli; **jangan kloning suara orang tanpa izin tertulis**.
