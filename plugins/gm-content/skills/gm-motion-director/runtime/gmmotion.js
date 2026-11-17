/* gmmotion.js (R2: +z, rx, ry, clipT/B, bright; grain()) — runtime gerak deterministik untuk GM Motion Director.
 * Setiap frame = fungsi murni dari waktu t (detik). Tidak ada requestAnimationFrame,
 * tidak ada CSS animation/transition, tidak ada Math.random tanpa seed.
 * Renderer (scripts/render.mjs) memanggil window.__GMM.seek(t) lalu memotret frame.
 * Lisensi: MIT. Tanpa dependensi.
 */
(function () {
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, p) => a + (b - a) * p;

  // Ease terukur — angka dari studi momen pro (lihat references/02-motion-craft.md)
  const ease = {
    linear: t => t,
    softLand: t => 1 - Math.pow(1 - t, 4),            // default MASUK: mendarat melambat
    expoOut: t => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t)),
    snapSettle: t => { const c = 1.25; const u = t - 1; return 1 + (c + 1) * u * u * u + c * u * u; }, // overshoot ~8%
    exitIn: t => t * t * t,                              // KELUAR: mempercepat
    inOut: t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
    drift: t => t,                                        // gerak latar konstan
  };

  // PRNG ber-seed (mulberry32) — wajib untuk data/chart/partikel prosedural
  function rng(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  const DEF = { x: 0, y: 0, z: 0, scale: 1, rotate: 0, rx: 0, ry: 0, opacity: 1, blur: 0, clip: 0, clipL: 0, clipT: 0, clipB: 0, bright: 1 };

  function Timeline(opts) {
    this.width = opts.width || 1080;
    this.height = opts.height || 1920;
    this.fps = opts.fps || 30;
    this.duration = opts.duration;
    this.tracks = [];   // {els, prop, from, to, start, dur, ease}
    this.calls = [];    // {start, dur, fn}
    this.cues = [];     // {t, name, gain}
    this.scenes = [];   // {sel, start, end}
  }

  // to(selector, {opacity:[0,1], y:[80,0], ...}, start, dur, ease)
  Timeline.prototype.to = function (sel, props, start, dur, easeName) {
    const els = typeof sel === 'string' ? Array.from(document.querySelectorAll(sel)) : [].concat(sel);
    if (!els.length) console.warn('[gmmotion] selector kosong:', sel);
    for (const prop in props) {
      const [from, to] = props[prop];
      this.tracks.push({ els, prop, from, to, start, dur: Math.max(dur, 1e-6), ease: ease[easeName || 'softLand'] || ease.softLand });
    }
    return this;
  };

  // stagger: selector banyak elemen, tiap elemen mulai start + i*gap
  Timeline.prototype.stagger = function (sel, props, start, dur, gap, easeName) {
    Array.from(document.querySelectorAll(sel)).forEach((el, i) => this.to(el, props, start + i * gap, dur, easeName));
    return this;
  };

  // call(fn(p, t), start, dur): untuk counter, gambar SVG, kamera, dll. p = progres 0..1 (sudah di-ease kalau easeName diberi)
  Timeline.prototype.call = function (fn, start, dur, easeName) {
    this.calls.push({ fn, start, dur: Math.max(dur, 1e-6), ease: ease[easeName || 'linear'] });
    return this;
  };

  // scene(selector, start, end): elemen hanya tampil di [start,end) → hard cut
  Timeline.prototype.scene = function (sel, start, end) {
    this.scenes.push({ els: Array.from(document.querySelectorAll(sel)), start, end });
    return this;
  };

  // cue(t, nama, gain): titik suara (whoosh/hit/tick/riser/sub) untuk scripts/sfx.py
  Timeline.prototype.cue = function (t, name, gain) { this.cues.push({ t, name, gain: gain == null ? 1 : gain }); return this; };

  Timeline.prototype.seek = function (t) {
    for (const s of this.scenes) {
      const on = t >= s.start && t < s.end;
      s.els.forEach(el => (el.style.visibility = on ? 'visible' : 'hidden'));
    }
    const state = new Map();
    const order = this.tracks.slice().sort((a, b) => a.start - b.start);
    for (const tr of order) {
      for (const el of tr.els) {
        let st = state.get(el); if (!st) { st = { set: {} }; state.set(el, st); }
        if (t < tr.start) { if (!(tr.prop in st.set)) { st[tr.prop] = tr.from; st.set[tr.prop] = 1; } continue; }
        const p = tr.ease(clamp((t - tr.start) / tr.dur));
        st[tr.prop] = lerp(tr.from, tr.to, p); st.set[tr.prop] = 1;
      }
    }
    for (const [el, s] of state) {
      const v = k => (k in s.set ? s[k] : DEF[k]);
      if (['x','y','z','scale','rotate','rx','ry'].some(k => k in s.set)) el.style.transform = `translate3d(${v('x')}px, ${v('y')}px, ${v('z')}px) rotateX(${v('rx')}deg) rotateY(${v('ry')}deg) rotate(${v('rotate')}deg) scale(${v('scale')})`;
      if ('opacity' in s.set) el.style.opacity = v('opacity');
      if ('blur' in s.set || 'bright' in s.set) {   // hanya sentuh filter bila dianimasikan (jangan timpa filter CSS)
        const b = v('blur'), br = v('bright');
        const f = (b > 0.05 ? `blur(${b}px) ` : '') + (Math.abs(br - 1) > 0.002 ? `brightness(${br})` : '');
        el.style.filter = f || 'none';
      }
      if ('clip' in s.set || 'clipL' in s.set || 'clipT' in s.set || 'clipB' in s.set)
        el.style.clipPath = `inset(${v('clipT')}% ${v('clip')}% ${v('clipB')}% ${v('clipL')}%)`;
    }
    for (const c of this.calls) {
      const p = c.ease(clamp((t - c.start) / c.dur));
      c.fn(p, t);
    }
  };

  // grain(canvas, t, opts): film grain deterministik per frame (seed dari nomor frame)
  function grain(cv, t, fps, amt) {
    const ctx = cv.getContext('2d'), w = cv.width, h = cv.height;
    const img = ctx.createImageData(w, h), d = img.data, r = rng(Math.round(t * (fps || 30)) * 7919 + 13);
    for (let i = 0; i < d.length; i += 4) { const g = (r() * 255) | 0; d[i] = d[i + 1] = d[i + 2] = g; d[i + 3] = amt || 255; }
    ctx.putImageData(img, 0, 0);
  }

  window.GMMotion = {
    ease, rng, clamp, lerp, grain,
    create(opts) {
      const tl = new Timeline(opts);
      window.__GMM = {
        get duration() { return tl.duration; }, fps: tl.fps, width: tl.width, height: tl.height,
        seek: t => tl.seek(t), cues: () => tl.cues,
      };
      // pratinjau di browser biasa: putar dengan jam dinding, ?t=3.2 untuk membekukan frame
      const q = new URLSearchParams(location.search);
      if (!navigator.webdriver && !q.has('render')) {
        if (q.has('t')) { requestAnimationFrame(() => tl.seek(parseFloat(q.get('t')))); }
        else { const t0 = performance.now(); const loop = () => { tl.seek(((performance.now() - t0) / 1000) % tl.duration); requestAnimationFrame(loop); }; requestAnimationFrame(loop); }
      }
      return tl;
    },
  };
})();
