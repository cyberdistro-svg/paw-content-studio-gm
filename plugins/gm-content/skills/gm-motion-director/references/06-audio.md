# 06 — Audio: suara juga kode

Video promo bisu kehilangan separuh dampaknya. Tiga lapis: **VO** (otoritas waktu) > **SFX** (menegaskan gerak) > **musik** (energi).

## SFX sintetis (`scripts/sfx.py`)

Komposisi menandai cue: `tl.cue(t, 'whoosh'|'hit'|'tick'|'pop'|'chime'|'riser'|'sub', gain)`. `render.mjs` menulis `*.cues.json`, `sfx.py` mensintesis semuanya (numpy, seed tetap, aman komersial) + bed pad sederhana, lalu mux + `loudnorm -14 LUFS`.

| Cue | Pakai di |
|---|---|
| `whoosh` | cut/whip/slide besar |
| `hit` | elemen hero mendarat, beat pertama |
| `pop` / `tick` | chip, label, poin daftar |
| `riser` (berakhir DI cue) | menjelang reveal/end card |
| `sub` | reveal logo/end card |
| `chime` | wordmark/brand |

Aturan: maks 1 SFX menonjol per 0,25 s; SFX ≥ 6 dB di bawah VO.

## Musik

- Bed sintetis `sfx.py` = penanda tempo, cukup untuk draft & internal.
- Final klien/broker: musik **berlisensi komersial** (YouTube Audio Library dengan atribusi sesuai, Pixabay Music, Artlist/Epidemic bila punya langganan). Simpan bukti lisensi di folder proyek. Mux: `node render.mjs index.html out.mp4 --audio music_mix.wav`.
- Duck musik −8…−12 dB di bawah VO (sidechain: `ffmpeg -filter_complex "[1:a][0:a]sidechaincompress=threshold=0.05:ratio=8[m]"`).

## Voice-over → waktu visual (VO adalah jam)

1. Naskah: 2,3–2,8 kata/detik (Bahasa Indonesia santai). 15 s ≈ 35–40 kata.
2. Suara: rekaman Hendra/talent, atau TTS (ElevenLabs bila ada API key; Edge-TTS `id-ID-ArdiNeural`/`id-ID-GadisNeural` gratis untuk draft).
3. Timestamp kata: `pip install faster-whisper` → `model.transcribe("vo.wav", word_timestamps=True, language="id")` → `words.json`.
4. Di komposisi: muat `words.json`, jadwalkan setiap perubahan visual di awal kata kuncinya (bukan tebakan detik).
5. Caption terbakar dari `words.json` (2–4 kata per kartu, kata aktif disorot warna aksen).

## Target loudness

| Kanal | Integrated | True peak |
|---|---|---|
| TikTok/Reels/Shorts/IG | −14 LUFS | ≤ −1 dBTP |
| YouTube | −14 LUFS | ≤ −1 dBTP |
| Webinar/presentasi | −16 LUFS | ≤ −1 dBTP |
