# 02 — Craft gerak (angka, bukan perasaan)

Angka di bawah diadaptasi dari studi 53 momen motion profesional di `tejashmakwana/motionmaxxing` (Apache-2.0) + praktik industri. Anggap sebagai default; boleh dilanggar hanya dengan alasan yang ditulis di storyboard.

## Durasi (30 fps)

| Gerak | Frame | Detik |
|---|---|---|
| Median gerak apa pun | 10 | 0,33 |
| Masuk elemen utama | 11–12 | 0,36–0,40 |
| Fade opacity | 6 | 0,20 |
| Blur → tajam | 7–8 | 0,23–0,27 |
| Keluar (exit) | 5–6 | 0,17–0,20 |
| Stagger antar item | 3–4 | 0,08–0,14 |
| Kamera push/drift latar | sepanjang scene | 2–6 |
| Hold teks minimum | — | 0,8 + 0,25/kata |

## Easing (nama di `runtime/gmmotion.js`)

| Nama | Kurva | Pakai untuk |
|---|---|---|
| `softLand` | quart-out | **default MASUK** — 58% gerak pro mendarat melambat |
| `expoOut` | expo-out | masuk sangat cepat lalu halus (angka, label) |
| `snapSettle` | back-out, overshoot ≈8% | kartu/chip/CTA yang "mengunci" |
| `exitIn` | cubic-in | **KELUAR** — mempercepat, lalu dipotong |
| `inOut` | cubic in-out | perpindahan A→B di dalam frame, kamera |
| `drift` | linear | gerak latar konstan, partikel, kamera lambat |

GSAP padanan: softLand=`power3.out`/`quart.out`, expoOut=`expo.out`, snapSettle=`back.out(1.25)`, exitIn=`power2.in`, inOut=`power2.inOut`. Remotion: `Easing.out(Easing.poly(4))`, `Easing.bezier(...)`, `spring({damping: 200})` untuk tanpa pantulan.

## Pola masuk yang terlihat mahal

1. **Scale-down + blur**: dari 1,3–1,6× blur 10–16 px → 1× tajam (hook, wordmark).
2. **Slide pendek + softLand**: dari y+40…+220 px. Makin besar elemen, makin pendek jaraknya.
3. **Mask reveal**: teks muncul dari balik garis (clip-path inset) — kinetic typography premium.
4. **Grow from edge**: bar/zona/garis tumbuh dari titik asalnya (bukan dari tengah, bukan dari 0 skala).
5. **Stagger kata/huruf** 0,04–0,11 s — kata penting terakhir, beri warna aksen.
6. **Kamera push 3–8%** selama scene hero → tidak pernah ada frame mati.
6b. **Kamera bernapas per adegan** (pelajaran studi kasus MT5, 15 Okt 2026): bungkus semua konten dalam satu `#all`, dorong `scale 1→1,07` + geser naik ±36 px sepanjang tiap adegan, reset di titik cut (tersembunyi oleh cut on motion). Drift < ~1,5%/detik terbaca "diam" oleh mata dan oleh `qa.py`.
7. **Parallax** 2–3 lapis (latar 0,3×, tengah 0,6×, depan 1×).

## Transisi

- Default **hard cut on motion**: elemen scene A mulai keluar (exitIn) 0,15–0,2 s sebelum cut, scene B masuk bergerak di frame pertama.
- **Whip/slide** (seluruh layer bergeser 1 layar dalam 0,18 s) untuk ganti topik.
- **Match cut**: bentuk di akhir scene A = bentuk di awal scene B (kartu → layar HP).
- **One continuous camera** (gaya onetake): kamera tak pernah cut, scene berikut tumbuh dari yang sebelumnya — mahal dikerjakan, pakai untuk launch film.
- Crossfade hanya untuk perubahan suasana lambat (≥ 0,5 s). Dissolve di reel sosial = lemah.

## Ritme & musik

- Kunci tempo: 100–120 BPM untuk promo; 1 beat = 0,5–0,6 s. Cut dan hit jatuh di beat (atau di kata VO — VO menang atas musik).
- Pola energi: hook kuat → turun sedikit (bukti) → naik (fitur cepat) → resolve (end card).

## Tipografi di video

- Judul 96–160 px (1080 lebar), body ≥ 44 px, caption ≥ 48 px dengan bayangan/latar.
- Letter-spacing judul −0,03 s/d −0,045 em; angka harga/statistik `tabular-nums` + font mono.
- Maks 2 keluarga font. Maks 3 berat. Tidak ada teks di bawah 26 px (tidak terbaca di HP).

## "Never ship" (tanda video AI murahan)

Page chrome/label sudut/timecode · teks melayang tanpa grid · semua elemen fade-in bersamaan · scale 0→1 · bounce berlebihan · glow neon di semua kartu · gradien ungu-pink generik · stok ikon emoji · font sistem default · logo diputar 360° · transisi "star wipe"/3D cube · musik keras menutupi VO · frame hitam di awal · end card > 2 s diam · teks terpotong zona UI TikTok.
