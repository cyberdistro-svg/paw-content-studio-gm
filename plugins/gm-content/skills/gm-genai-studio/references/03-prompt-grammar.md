# Tata Bahasa Prompt

## 1. Video (urutan penting → kurang penting)

```
[SHOT & KAMERA] [SUBJEK + atribut] [AKSI berurutan] [SCENE/latar + waktu] [CAHAYA]
[GAYA/GRADE] [AUDIO bila model mendukung] [DURASI, RASIO]
```
Contoh (B-roll emas, 9:16, 5 s):
"Slow dolly-in, 50mm, f/2, eye level. A single gold bar on a dark walnut trading desk, faint chart glow reflected on its surface. Dust particles drift through a narrow window light beam. Late night, cool blue monitor spill vs warm tungsten key. Cinematic, subtle film grain, teal-amber grade. 5 seconds, vertical 9:16."

Kosakata kamera:
- **Ukuran shot**: ECU · CU · MS · WS · EWS
- **Gerak**: static · dolly in/out · truck · pan · tilt · orbit · crane up/down · handheld · whip pan · rack focus
- **Focal**: 14 mm sangat lebar · 24 mm lebar dinamis · 35 mm sinematik alami · 50 mm standar · 85 mm potret
- **Aperture**: f/1.4 bokeh lembut · f/4 seimbang · f/11 tajam depan-belakang
- **Tinggi/sudut**: ground · eye · overhead/top-down · low angle · high angle · dutch
- **Lensa/bodi** (rasa): anamorphic (flare horizontal) · vintage prime (lembut) · macro · 16mm film (grain) · 70mm large format (megah)

Aturan: satu aksi utama per klip ≤ 5 s; sebut urutan aksi ("first…, then…"); hindari kata kualitas kosong ("8K masterpiece") — ganti dengan cahaya & lensa spesifik.

## 2. Gambar produk — pilih mode dulu

| Mode | Kerangka |
|---|---|
| studio | produk + latar netral/sweep + key light softbox 45° + rim + bayangan kontak |
| lifestyle | produk dipakai di tempat nyata (meja trader, kafe), tangan/aksi, cahaya alami |
| close-up tangan | crop ketat, tangan memegang/menyentuh, DoF dangkal |
| pin 2:3 | vertikal, moodboard, ruang negatif atas untuk teks |
| hero banner | lebar 16:9/21:9, subjek di sepertiga, ruang kosong untuk headline |
| carousel | 3–10 slide satu bahasa visual, urutan cerita |
| ad pack | variasi terkendali (latar/sudut/warna) dari satu master |
| conceptual | melayang, percikan, surreal, CGI |
| restyle | ubah suasana/musim gambar yang ada, struktur dikunci |

Layar app/platform di dalam gambar: **tempel screenshot asli** lewat kode/komposit, jangan minta model menggambar UI.

## 3. Thumbnail / cover

1. Tulis ≥ 5 konsep **jujur** dari beberapa kerangka: hasil-dulu (before/after), konflik, rahasia/celah informasi, angka besar (yang benar), wajah+emosi, objek aneh.
2. Pilih satu: **satu fokus**, kontras tinggi, terbaca di 120 px lebar.
3. Teks 2–4 kata, ditimpa deterministik (HTML/PIL). Model generatif hanya untuk latar/subjek.
4. Referensi thumbnail orang lain = analisis energi/komposisi saja, **tidak** dikirim sebagai input generasi.
5. Rasio: 16:9 YouTube · 9:16 Shorts/Reels/TikTok cover · 4:5 feed IG.
6. Variasi: maks 4 per putaran, tiap variasi diberi label (emosi/kamera/warna).

## 4. Faceless video — tiga mode

| Mode | Kapan | Visual |
|---|---|---|
| Explainer ilustrasi | konsep trading, edukasi | diagram/ilustrasi berurutan + motion kode untuk angka |
| Channel motion cepat | hook viral, listicle | potongan 1,5–3 s, B-roll generatif + teks kinetik |
| Picture story | cerita/dokumenter | still sinematik + pan/zoom, narasi kuat |

## 5. Blok asumsi (bila brief samar)

Jangan berhenti bertanya. Tulis di atas usulan:
```
ASUMSI (bisa diarahkan ulang): rasio 9:16 · 30–45 s · VO Gemini "Sadachbia" · gaya Arctic Prism · CTA join Telegram · anggaran ≤ USD 3
```
Lanjut kerja; Hendra cukup mengoreksi baris yang salah.
