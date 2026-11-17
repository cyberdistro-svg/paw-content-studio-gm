# Router Model Generatif (snapshot 5 Nov 2026 — drift-prone)

Sumber snapshot: Artificial Analysis T2V leaderboard (diakses 5 Nov 2026), katalog default higgsfield-ai/skills v0.14.0, README OpenMontage (provider list), lisensi repo .
**Sebelum menjanjikan model/harga: cek katalog live.**

## 0. Higgsfield — hanya project GO Markets

Akun Higgsfield (workspace GO Markets) hanya untuk project GO Markets. Ragu apakah brief termasuk GO Markets → tanya Hendra, jangan generate. Eksekusi job dilakukan pabrik lewat tiket; di chat: estimasi biaya + persetujuan Hendra sebelum tiket dikirim.

Biaya terukur 5 Nov 2026: z_image 0,15 · gpt_image_2_5 0,25 (high 2k ≈2,75) · nano_banana_2 2 · kling3_0 5 s 10 · seedance_2_5 5 s 1080p 80 kredit. Urutan hemat: still murah → setujui → I2V `kling3_0` → `seedance_2_5` hanya shot hero. Cek ulang harga di katalog live sebelum menjanjikan.

Tie-breaker: lisensi HIJAU > KUNING; sudah ada akun/API key > daftar baru.

## 1. Kartu skor (isi per kandidat, 1–5)

| Dimensi | Pertanyaan |
|---|---|
| Kecocokan tugas | Model ini memang untuk jenis shot ini (T2V, I2V, avatar, produk)? |
| Kualitas | ELO/arena + contoh nyata sejenis |
| Kontrol | first/last frame, reference image, kamera, seed, durasi, rasio 9:16 |
| Keandalan | Tingkat gagal, antrean, batas konten |
| Biaya | USD per detik/gambar × jumlah take |
| Latensi | Waktu tunggu per job |
| Kontinuitas | Bisa jaga identitas/produk/gaya antar shot? |

Tie-breaker: lisensi HIJAU > KUNING; sudah ada akun/API key > daftar baru.

## 2. Kapabilitas × jalur

| Kapabilitas | Premium tertutup (API/gateway) | Open / lokal | Catatan |
|---|---|---|---|
| Video T2V/I2V | Wan 3.0, Seedance 2.5, MiniMax H3, Kling 3.0, Veo 3.1, Runway Gen-4.5, FLUX 3 video (cek AA) | LTX-2 (audio), Wan2.2, HunyuanVideo-1.5, SkyReels-V2 | Video generatif berat → API atau GPU sewaan (lewat pabrik) |
| Video + audio sinkron | Seedance 2.x, Veo 3.x | LTX-2 | Jangan pakai audio generatif untuk VO utama |
| Gambar (desain, teks) | GPT Image 2.5, Nano Banana 2/Pro, Seedream v5, FLUX 2/3, Recraft (vektor/logo) | Qwen-Image, FLUX.1-schnell | Teks final tetap ditimpa kode |
| Edit gambar multi-referensi | Nano Banana 2 Edit, GPT Image edit, Seedream edit | Qwen-Image-Edit | Wajah orang nyata = butuh izin |
| Avatar bicara / lip-sync | HeyGen, Kling avatar/lip-sync | InfiniteTalk, LatentSync, MuseTalk | Label "AI" wajib |
| TTS / VO | Gemini TTS (suara "Sadachbia" disukai Hendra), ElevenLabs | Chatterbox (MIT; Melayu, bukan Indonesia), CosyVoice, Kokoro (tanpa Indonesia) | Uji pelafalan istilah trading |
| Musik | Suno, ElevenLabs music | ACE-Step 1.5 (MIT, <4 GB, lokal OK) | Tanpa lagu berhak cipta |
| SFX | ElevenLabs SFX | freesound.org (cek lisensi per file) | |
| STT / caption | — | faster-whisper, whisperX | Lokal OK |
| Hapus latar / upscale | — | BiRefNet, Real-ESRGAN | Lokal OK |
| Motion grafis/teks/UI | — | HyperFrames, Remotion, kode | **Selalu** kode (lewat tiket pabrik) |

## 3. Pola biaya

- Mulai dari **1 sampel murah** (still atau klip 3–5 s resolusi rendah) → persetujuan → baru resolusi/durasi penuh.
- Hitung: `take × durasi × harga/detik` per shot; jumlahkan; tampilkan sebelum generate.
- Catat biaya nyata per aset di `<proyek>/biaya.csv` (aset, model, detik, USD, lolos/ditolak).
- Batas default tanpa bertanya: USD 5 per proyek. Lebih → tanya Hendra.

## 4. Konsistensi lintas shot

| Objek | Teknik |
|---|---|
| Produk (indikator, app, HP) | Still disetujui jadi *first frame* (dan *last frame* bila model mendukung) |
| Karakter/maskot | Satu set referensi (depan/samping/3⁄4) dipakai semua shot; atau ID/LoRA terlatih |
| Gaya | Satu blok gaya (palet, grade, grain, lensa) disalin utuh |
| Suara | Satu voice ID + kecepatan + gaya, disimpan di `prompts.md` |
