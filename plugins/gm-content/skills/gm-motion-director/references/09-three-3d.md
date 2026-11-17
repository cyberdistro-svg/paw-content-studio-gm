# 09 — Preview 3D dengan Three.js di atas gmmotion

Pola umum untuk animasi 3D di atas gmmotion (Three.js UMD ada di `templates/three-3d/three.min.js`). Contoh scene bawaan tidak disertakan: bangun scene dari pola di bawah, mulai dari still dulu.

## Pola
- **Satu kanvas WebGL** `#gl` (1080×1920, `alpha:true`, `preserveDrawingBuffer:true`) diletakkan di dalam `#all`, di bawah lapisan 2D. CSS tetap dipakai untuk teks, kartu, dan caption, sehingga teks tetap tajam.
- **Deterministik.** Tidak ada RAF dan tidak ada jam. `tl.call((p,t) => GL.render(dir(t)), 0, D)` dipanggil di setiap seek. `dir(t)` mengembalikan `{mode, cam:{pos,target,fov,roll}, chart|device:{...}}` per adegan. Kamera diinterpolasi antar kunci dengan `inOut`, atau `linear` untuk drift.
- **Urutan boot:** muat font (`document.fonts.load`), lalu `await GL.init()`, baru `GMMotion.create()`. Renderer menunggu `window.__GMM`, jadi aset 3D sudah siap sebelum frame pertama.
- **Tekstur dari file://** akan ter-*taint* di WebGL. Embed sebagai data-URL (`assets_b64.js`: `window.TEX={...}`), atau gambar sendiri di canvas.
- **Pakai build UMD** `three@0.160.0/build/three.min.js`, karena ES module gagal di file://. `RoomEnvironment` tidak ada di UMD, jadi buat env PMREM dari kubah gradasi plus beberapa softbox (`makeEnv`).
- **Zona/glow:** `MeshBasicMaterial` + `toneMapped:false` + `EdgesGeometry`. Material physical dengan emissive di bawah ACES jadi kusam. Pivot geometri di tepi kiri (`geo.translate(.5,0,0)`) supaya zona "tumbuh dari tepi".
- **Label 3D:** canvas → `PlaneGeometry`, bukan Sprite, supaya ikut perspektif. Taruh di z +0.75 agar ada parallax.
- **Exploded view:** putar grup device (ry −0.5, rx +0.2), jangan orbit kamera, supaya tumpukan tetap di tengah frame. Jarak antar lapis 0.85–2.4 unit.
- **Framing 9:16:** panel lebar terlalu kecil kalau difoto frontal. Pakai sudut 3/4 sepanjang sumbu waktu (kamera di x ±9…13), sehingga chart menjorok ke kedalaman. Adegan gelap diberi scrim gradasi atas/bawah dan headline putih (`.head.light`).

## Render
- Chrome di Windows memakai GPU (ANGLE D3D11). Sandbox Linux memakai SwiftShader; ini cukup untuk still, tapi lambat. `render.mjs` sudah membawa `--ignore-gpu-blocklist --enable-unsafe-swiftshader`.
- **Screenshot PNG 1080×1920 ≈ 1,1 s/frame, JPEG q96 ≈ 0,13 s.** Selalu pakai `--mblur 2` (otomatis JPEG) atau `--jpeg`. Video 2 menit dengan mblur 2 ≈ 25–40 menit di RTX 2060, dan A/B bisa dirender paralel.
- Cek still di sandbox dulu (`still.mjs`), baru render penuh di PC.
