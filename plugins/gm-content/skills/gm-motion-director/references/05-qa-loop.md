# 05 — Loop QA: render → lihat → perbaiki → ulang

Agen tidak bisa "menonton" video. Ia bisa **melihat still**. Maka video diubah kembali jadi lembar kontak, dinilai, diperbaiki. Ini yang membedakan hasil pro dari hasil sekali-jadi.

## Loop

```
render.mjs  →  qa.py (gerbang mesin + sheet.png)  →  LIHAT sheet.png  →  daftar masalah  →  edit  →  render ulang
                                                         ↑______________ sampai semua gerbang lolos ______________|
```

1. `python scripts/qa.py out.mp4 --platform tiktok --n 24 --cols 8` → JSON + `out.sheet.png`.
   - Area merah transparan di lembar = zona UI platform (TikTok/Reels/Shorts). Teks/logo penting tidak boleh di situ.
2. **Buka gambar lembar kontak** (Read tool / buka file gambar). Nilai G1, G4, G5, G7, G8 satu per satu, tulis temuan.
3. Untuk detail: still resolusi penuh di detik tertentu: `ffmpeg -ss 4.2 -i out.mp4 -frames:v 1 f.png` atau buka komposisi `index.html?t=4.2`.
4. Render parsial untuk iterasi cepat: `node render.mjs index.html part.mp4 --from 2.4 --to 6.8 --no-audio`.
5. Maks **5 putaran**. Masih gagal → laporkan gerbang yang gagal + alasan, jangan klaim selesai.

## Tabel diagnosis cepat

| Gejala di qa.py / sheet | Penyebab umum | Perbaikan |
|---|---|---|
| `dead_runs` tersebar di semua adegan | drift latar terlalu halus (< ~1,5%/s) | kamera bernapas per adegan (lihat 02 §6b) |
| `dead_runs` di awal scene | elemen sudah mendarat, belum ada gerak sekunder | tambah drift kamera 3–8% atau parallax latar |
| `dead_runs` panjang di tengah | jeda antar beat | potong jeda, atau isi dengan gerak data (counter, garis tergambar) |
| `end_hold_s` > 1,6 | end card terlalu lama | pendekkan durasi total |
| `end_hold_s` < 0,4 | masih ada drift di end card | hentikan semua drift ≤ 1,2 s sebelum akhir |
| `G6_loudness` gagal | puncak SFX tinggi / tanpa loudnorm | render.mjs sudah loudnorm; kalau audio eksternal: `-af loudnorm=I=-14:TP=-1.5:LRA=11` |
| teks di zona merah | layout tidak memakai zona aman | pindah ke kolom aman (lihat `07`) |
| frame hitam pertama | scene belum tampil di t=0 | pastikan scene pertama mulai 0 dan elemen hook sudah terlihat ≤ frame 3 |
| font fallback (huruf beda) | font belum termuat | `@font-face` lokal + renderer menunggu `document.fonts` |
| teks kabur/bergetar | transform subpiksel + blur sisa | blur → 0 di akhir tween; `will-change` tidak perlu |

## Laporan akhir (format)

```
VIDEO   : out/promo.mp4 (1080x1920, 30fps, 12.0s, AAC, -14.1 LUFS)
MESIN   : G0 ✓  G2 ✓  G3 ✓ (1.2s)  G6 ✓
MATA    : G1 ✓ semua teks terbaca, di luar zona TikTok | G4 ✓ | G5 ✓ | G7 ✓ Arctic Prism | G8 ✓ label "ilustrasi" + disclaimer 1.5s
PUTARAN : 2 (putaran 1: dead frames 0.43–1.13s & 2.9–3.3s → drift + reveal lebih awal)
```
