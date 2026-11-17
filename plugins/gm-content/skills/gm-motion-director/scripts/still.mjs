#!/usr/bin/env node
// still.mjs — ambil frame diam di detik tertentu (iterasi cepat tanpa render penuh).
// Pakai: node still.mjs <index.html> <out.png> 0.5,2.8,4.6 [--w 360] [--chrome path]
import { execSync } from 'node:child_process';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
const a = process.argv.slice(2); const [html, out, ts] = a; const opt = (k, d) => { const i = a.indexOf('--' + k); return i >= 0 ? a[i + 1] : d; };
let pw; for (const n of ['playwright', 'playwright-core']) { try { pw = await import(n); break; } catch {} try { pw = await import(pathToFileURL(join(execSync('npm root -g').toString().trim(), n, 'index.mjs')).href); break; } catch {} }
const ch = opt('chrome', process.env.CHROME_PATH);
const b = await pw.chromium.launch(ch ? { executablePath: ch } : {});
const p = await b.newPage();
await p.goto(pathToFileURL(resolve(html)).href + '?render=1');
await p.waitForFunction(() => window.__GMM && document.fonts.status === 'loaded');
const m = await p.evaluate(() => ({ w: __GMM.width, h: __GMM.height }));
await p.setViewportSize({ width: m.w, height: m.h });
const times = ts.split(',').map(Number), W = Number(opt('w', 360)), H = Math.round(W * m.h / m.w);
const imgs = [];
for (const t of times) { await p.evaluate(x => __GMM.seek(x), t); imgs.push((await p.screenshot({ type: 'jpeg', quality: 90 })).toString('base64')); }
const sheet = await b.newPage({ viewport: { width: W * times.length, height: H + 30 } });
await sheet.setContent(`<body style="margin:0;background:#111;display:flex">${imgs.map((s, i) => `<div style="width:${W}px;color:#ddd;font:14px monospace"><img src="data:image/jpeg;base64,${s}" style="width:${W}px;height:${H}px;display:block">${times[i]}s</div>`).join('')}</body>`);
await sheet.screenshot({ path: out });
await b.close(); console.log('still ->', out);
