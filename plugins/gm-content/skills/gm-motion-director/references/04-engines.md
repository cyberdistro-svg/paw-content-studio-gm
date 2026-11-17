# 04 — Engine, pemasangan, kapan pakai apa

Prinsip: **video adalah fungsi waktu.** Engine apa pun wajib *seekable* — renderer bisa meminta frame ke-n tanpa memutar dari awal. Dilarang: `requestAnimationFrame` sebagai jam, CSS `animation/transition`, `setTimeout`, `Math.random()` tanpa seed, video latar yang tidak disinkron ke t.

## Matriks keputusan

| Engine | Bahasa | Kekuatan | Kelemahan | Lisensi | Pakai bila |
|---|---|---|---|---|---|
| **gmmotion** (`runtime/`) | HTML/CSS/JS | nol dependensi, deterministik, jalan di sandbox mana pun | fitur minimal (tween, scene, cue) | MIT | default promo/reel; agen lemah |
| **HyperFrames** (heygen-com) | HTML + GSAP | `data-*` timing, katalog blok, lint/preview/render CLI, dibuat untuk agen | Node 22+ | Apache-2.0 | promo kompleks, butuh blok siap pakai |
| **Remotion** | React/TSX | props → ribuan varian, Studio, captions, maps, Lambda | lisensi perusahaan untuk tim >3 orang (cek remotion.pro) | Remotion License | template massal broker, data-driven |
| **Motion Canvas** | TS generator | diagram presisi, sinkron VO, editor | ekosistem kecil | MIT | diagram alur sistem/arsitektur |
| **Manim CE** | Python | matematika/konsep, transformasi bentuk | estetika "akademis" kecuali distyling | MIT | edukasi R:R, probabilitas, statistik |
| **Three.js** | JS (di HTML) | 3D real-time, kaca/kristal, kamera | perlu seek manual (`renderer.render` per t) | MIT | produk 3D, HP berputar |
| **Blender** | Python (bpy) | fotoreal, partikel, Cycles | berat, render lambat | GPL (output bebas) | hero shot 3D sinematik |
| **Theatre.js** | JS | sequencer visual untuk Three.js | pengembangan v-next privat | Apache-2.0 | koreografi kamera 3D rumit |
| **GSAP** | JS | timeline & easing kelas industri, SplitText, MorphSVG | lisensi "no charge" Webflow — bukan OSI; jangan bangun builder animasi saingan Webflow | GreenSock std | di dalam HyperFrames/HTML |
| **anime.js** | JS | ringan, MIT, seekable (`.seek(ms)`) | — | MIT | alternatif GSAP yang benar-benar open source |
| **Lottie** | JSON | vektor ringan untuk app/web | bukan untuk video panjang | MIT | ikon/loader di webapp & mobile |
| **animate.css** | CSS | — | CSS animation tidak seekable | MIT | **jangan** untuk render video; hanya UI web |
| **FFmpeg** | CLI | encode, mux, concat, overlay, loudnorm, rasio | — | LGPL/GPL | selalu |


## Pasang (lakukan sendiri, jangan suruh pengguna)

```bash
# dasar (semua jalur)
node -v            # ≥18 (HyperFrames: ≥22)
ffmpeg -version    # Windows: winget install Gyan.FFmpeg | Ubuntu: sudo apt-get install -y ffmpeg
python -m pip install numpy pillow          # untuk sfx.py & qa.py
npm i -D playwright && npx playwright install chromium   # atau pakai Chrome terpasang: --chrome "C:\Program Files\Google\Chrome\Application\chrome.exe"

# HyperFrames
npx skills add heygen-com/hyperframes      # skill resmi untuk agen
npx hyperframes init my-video && cd my-video && npx hyperframes preview && npx hyperframes render

# Remotion
npx create-video@latest                     # lalu: npx skills add remotion-dev/skills
npx remotion studio ; npx remotion render <CompId> out.mp4

# Motion Canvas
npm init @motion-canvas@latest

# Manim CE
pip install manim     # butuh cairo/pango; Windows: choco install manimce
manim -qh scene.py MyScene

# Blender headless
blender -b -P build_scene.py -- --out out/ ; blender -b scene.blend -a
```

## Pola seek per engine

- **gmmotion**: `tl.to(sel, {prop:[from,to]}, start, dur, ease)` → renderer memanggil `__GMM.seek(t)`.
- **GSAP**: `const tl = gsap.timeline({paused:true}); window.__timelines['id']=tl;` renderer memanggil `tl.seek(t)`. Untuk gmmotion-renderer: `window.__GMM = {width,height,fps,duration, seek:t=>tl.seek(t), cues:()=>[]}`.
- **anime.js**: `const a = anime.timeline({autoplay:false})` → `a.seek(t*1000)`.
- **Three.js**: semua posisi = f(t); di `seek(t)` hitung pose lalu `renderer.render(scene, cam)`; `preserveDrawingBuffer:true`.
- **Remotion**: hanya `useCurrentFrame()` + `interpolate()`/`spring()`; jangan state/efek berbasis waktu nyata.

## Rekaman layar produk (bukti nyata > mockup)

- Web: Playwright `page.video` atau screenshot per langkah, 2× DPR, lalu tempel sebagai `<img>`/`<video>` dalam bingkai perangkat. Untuk `<video>`, sinkronkan: `video.currentTime = t - start` di `seek` dan tunggu event `seeked`.
- Mobile: `mobile-mcp` (screenshot/rekam emulator) atau `adb shell screenrecord`.
- Desktop (platform, MT5): OBS/rekaman layar; potong dengan `ffmpeg -ss A -to B -c copy`.
