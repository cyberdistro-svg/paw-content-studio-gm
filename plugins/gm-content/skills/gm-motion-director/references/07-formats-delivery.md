# 07 — Format, zona aman, paket kirim

## Rasio & resolusi

| Kanal | Rasio | Resolusi | fps | Durasi ideal |
|---|---|---|---|---|
| TikTok / Reels / Shorts | 9:16 | 1080×1920 | 30 (60 untuk UI cepat) | 9–30 s |
| IG/FB feed | 4:5 | 1080×1350 | 30 | 10–30 s |
| Feed persegi / iklan | 1:1 | 1080×1080 | 30 | 6–15 s |
| YouTube / webinar / web hero | 16:9 | 1920×1080 (4K: 3840×2160) | 30/60 | 30–120 s |
| Hero loop web (tanpa suara) | 16:9 / 21:9 | 1920×1080 | 30 | 6–12 s loop mulus |

Desain **9:16 dulu**, lalu turunkan: susun layout dengan kolom isi tengah sehingga 1:1 dan 4:5 cukup di-crop/di-reflow (lebih baik: komposisi kedua dengan `width/height` beda, timeline sama).

## Zona aman 9:16 (1080×1920)

| Platform | Atas | Bawah | Kanan | Kiri |
|---|---|---|---|---|
| TikTok | 160 | 480 | 150 | 60 |
| Reels | 220 | 420 | 120 | 60 |
| Shorts | 150 | 380 | 130 | 60 |

Konten penting: kotak x 70–920, y 200–1440 aman untuk ketiganya. `qa.py --platform` menggambar zona ini di lembar kontak.

## Encode

```bash
# master (dari render.mjs): H.264 CRF 16, yuv420p, +faststart, AAC 192k 48kHz
# varian ringan untuk kirim WA/Telegram:
ffmpeg -i master.mp4 -c:v libx264 -crf 23 -preset slow -c:a aac -b:a 128k -movflags +faststart kirim.mp4
# GIF/WebP pratinjau:
ffmpeg -i master.mp4 -vf "fps=15,scale=480:-1" -loop 0 preview.webp
# thumbnail (frame terkuat):
ffmpeg -ss 2.8 -i master.mp4 -frames:v 1 thumb.png
# ProRes 4444 dengan alpha (untuk editor/broker): render dengan latar transparan lalu
ffmpeg -framerate 30 -i frames/%05d.png -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le alpha.mov
```

## Paket kirim (per video)

```
<proyek>/
  brief.md  storyboard.md  world.md
  src/ (komposisi + fonts + assets)
  out/<nama>_9x16.mp4  <nama>_1x1.mp4  <nama>_16x9.mp4  <nama>_bisu.mp4
  out/thumb.png  out/captions.srt  out/qa.json  out/sheet.png
  LICENSES.md  (font, musik, aset pihak ketiga, logo broker)
```
Penamaan: `TANGGAL_produk_kanal_rasio_vN.mp4`, mis. `20261117_promo_tiktok_9x16_v2.mp4`.
