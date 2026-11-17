#!/usr/bin/env node
// render.mjs — render komposisi gmmotion (HTML) jadi MP4 deterministik, frame demi frame.
// Pakai: node render.mjs <komposisi/index.html> <out.mp4> [--fps 30] [--from 0] [--to <detik>] [--no-audio] [--chrome <path>]
// Butuh: Node 18+, ffmpeg di PATH, Python 3 + numpy (untuk audio), paket playwright (npm i -D playwright)
//        dan browser: `npx playwright install chromium` ATAU Chrome terpasang (otomatis dicoba).
import { spawn, execSync } from 'node:child_process';
import { writeFileSync, existsSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf('--' + k); return i >= 0 ? args[i + 1] : d; };
const flag = k => args.includes('--' + k);
const VALUED = ['--fps', '--from', '--to', '--chrome', '--audio', '--lufs', '--mblur', '--shutter'];
const [inHtml, outMp4] = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && VALUED.includes(args[i - 1])));
if (!inHtml || !outMp4) { console.error('pakai: node render.mjs <index.html> <out.mp4> [--fps 30] [--no-audio]'); process.exit(2); }
const here = dirname(fileURLToPath(import.meta.url));

async function loadPlaywright() {
  for (const name of ['playwright', 'playwright-core']) {
    try { return await import(name); } catch {}
    try { const root = execSync('npm root -g').toString().trim(); return await import(pathToFileURL(join(root, name, 'index.mjs')).href); } catch {}
  }
  console.error('Playwright tidak ditemukan. Jalankan: npm i -D playwright && npx playwright install chromium'); process.exit(3);
}

const { chromium } = await loadPlaywright();
const launchOpts = { args: ['--force-color-profile=srgb', '--disable-lcd-text', '--font-render-hinting=none', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'] };   // WebGL: GPU bila ada, SwiftShader bila tidak
const chromePath = opt('chrome', process.env.CHROME_PATH);
let browser;
try { browser = await chromium.launch(chromePath ? { ...launchOpts, executablePath: chromePath } : launchOpts); }
catch { browser = await chromium.launch({ ...launchOpts, channel: 'chrome' }); }

const page = await browser.newPage({ deviceScaleFactor: 1 });
const url = pathToFileURL(resolve(inHtml)).href + '?render=1';
page.on('console', m => { if (m.type() === 'warning' || m.type() === 'error') console.log('[page]', m.text()); });
await page.goto(url, { waitUntil: 'load' });
await page.waitForFunction(() => window.__GMM && document.fonts && document.fonts.status === 'loaded');
const meta = await page.evaluate(() => ({ w: __GMM.width, h: __GMM.height, fps: __GMM.fps, d: __GMM.duration }));
await page.setViewportSize({ width: meta.w, height: meta.h });
const fps = Number(opt('fps', meta.fps));
const t0 = Number(opt('from', 0)), t1 = Number(opt('to', meta.d));
const total = Math.round((t1 - t0) * fps);
console.log(`render ${meta.w}x${meta.h} @${fps}fps, ${t1 - t0}s = ${total} frame`);

const silent = outMp4.replace(/\.mp4$/i, '') + '.video.mp4';
// Motion blur asli: --mblur N mengambil N sub-frame dalam rentang shutter (default 180° = 0.5 frame) lalu dirata-rata.
const MB = Math.max(1, Number(opt('mblur', 1))), SH = Number(opt('shutter', 0.5));
const JPG = MB > 1 || args.includes('--jpeg');   // PNG 1080x1920 ±1,1 s/frame di Chrome Windows; JPEG q96 ±0,13 s (pakai --jpeg)
const vf = MB > 1 ? ['-vf', `tmix=frames=${MB},select='eq(mod(n\\,${MB})\\,${MB - 1})',setpts=PTS-STARTPTS,scale=in_range=full:out_range=tv,format=yuv420p`, '-r', String(fps)]  : JPG ? ['-vf', 'scale=in_range=full:out_range=tv,format=yuv420p'] : [];
const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps * MB), '-i', '-', ...vf,
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-movflags', '+faststart', silent], { stdio: ['pipe', 'inherit', 'inherit'] });
const started = Date.now();
for (let i = 0; i < total; i++) {
  for (let k = 0; k < MB; k++) {
    const t = t0 + i / fps + (MB > 1 ? (k / MB) * SH / fps : 0);
    await page.evaluate(tt => window.__GMM.seek(tt), t);
    const buf = await page.screenshot({ type: JPG ? 'jpeg' : 'png', quality: JPG ? 96 : undefined });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  if (i % fps === 0) process.stdout.write(`\r  frame ${i}/${total}${MB > 1 ? ' x' + MB + ' mblur' : ''}  (${((Date.now() - started) / 1000).toFixed(0)}s)`);
}
ff.stdin.end();
await new Promise((r, j) => ff.on('close', c => (c === 0 ? r() : j(new Error('ffmpeg gagal ' + c)))));
const cues = await page.evaluate(() => (window.__GMM.cues ? window.__GMM.cues() : []));
await browser.close();
console.log('\n  video selesai:', silent);

const cuesPath = outMp4.replace(/\.mp4$/i, '') + '.cues.json';
writeFileSync(cuesPath, JSON.stringify({ duration: t1 - t0, offset: t0, cues }, null, 2));
const userAudio = opt('audio', null);   // VO/musik milik sendiri; SFX dari cue tetap dicampur di bawahnya (matikan: --no-sfx)
const py = process.platform === 'win32' ? 'python' : 'python3';
const base = outMp4.replace(/\.mp4$/i, '');
if (flag('no-audio')) { execSync(`ffmpeg -y -v error -i "${silent}" -c copy "${outMp4}"`); }
else {
  const ln = `loudnorm=I=${opt('lufs', -14)}:TP=-1.5:LRA=11`;
  if (!userAudio) {
    const wav = base + '.sfx.wav';
    execSync(`${py} "${join(here, 'sfx.py')}" "${cuesPath}" "${wav}"`, { stdio: 'inherit' });
    execSync(`ffmpeg -y -v error -i "${silent}" -i "${wav}" -map 0:v -map 1:a -c:v copy -af ${ln} -ar 48000 -c:a aac -b:a 192k -shortest -movflags +faststart "${outMp4}"`, { stdio: 'inherit' });
  } else if (flag('no-sfx')) {
    execSync(`ffmpeg -y -v error -i "${silent}" -i "${userAudio}" -map 0:v -map 1:a -c:v copy -af apad,${ln} -ar 48000 -c:a aac -b:a 192k -shortest -movflags +faststart "${outMp4}"`, { stdio: 'inherit' });
  } else {
    const wav = base + '.sfx.wav';
    execSync(`${py} "${join(here, 'sfx.py')}" "${cuesPath}" "${wav}" --no-bed`, { stdio: 'inherit' });
    execSync(`ffmpeg -y -v error -i "${silent}" -i "${userAudio}" -i "${wav}" -filter_complex "[1:a]apad[vo];[2:a]volume=0.32[fx];[vo][fx]amix=inputs=2:duration=first:normalize=0,${ln}[a]" -map 0:v -map "[a]" -c:v copy -ar 48000 -c:a aac -b:a 192k -shortest -movflags +faststart "${outMp4}"`, { stdio: 'inherit' });
  }
}
console.log('SELESAI ->', outMp4);
