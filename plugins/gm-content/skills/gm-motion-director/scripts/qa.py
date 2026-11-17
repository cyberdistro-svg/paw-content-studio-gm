#!/usr/bin/env python3
"""qa.py — gerbang kualitas otomatis + lembar kontak untuk DILIHAT agen.
Pakai: python qa.py video.mp4 [--sheet sheet.png] [--cols 6] [--n 24] [--platform tiktok|reels|shorts|feed|youtube] [--lufs -14]
Keluar kode 0 = lolos gerbang mesin (G0,G2,G3,G6). G1/G4/G5 tetap WAJIB dinilai dengan MATA dari lembar kontak.
Butuh: ffmpeg/ffprobe, numpy, Pillow.
"""
import json, subprocess, sys, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def arg(k, d=None):
    return sys.argv[sys.argv.index('--' + k) + 1] if '--' + k in sys.argv else d

def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

# Zona aman 9:16 (px pada 1080x1920). Teks/logo penting DILARANG di area ini.
SAFE = {
    'tiktok': dict(top=160, bottom=480, left=60, right=150),
    'reels': dict(top=220, bottom=420, left=60, right=120),
    'shorts': dict(top=150, bottom=380, left=60, right=130),
    'feed': dict(top=60, bottom=60, left=60, right=60),
    'youtube': dict(top=54, bottom=54, left=96, right=96),
}

def main():
    src = sys.argv[1]
    plat = arg('platform', 'tiktok'); target = float(arg('lufs', -14))
    rep = {'file': src, 'gates': {}, 'notes': []}
    pr = json.loads(sh(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', src]).stdout)
    v = next(s for s in pr['streams'] if s['codec_type'] == 'video')
    a = next((s for s in pr['streams'] if s['codec_type'] == 'audio'), None)
    W, H = int(v['width']), int(v['height']); num, den = map(int, v['r_frame_rate'].split('/')); fps = num / den
    dur = float(pr['format']['duration'])
    rep['meta'] = dict(width=W, height=H, fps=round(fps, 3), duration=round(dur, 3), vcodec=v['codec_name'], pix_fmt=v.get('pix_fmt'), audio=bool(a))
    g0 = v['codec_name'] == 'h264' and v.get('pix_fmt') in ('yuv420p',) and dur > 0.5
    if v.get('pix_fmt') == 'yuvj420p': rep['notes'].append('pix_fmt yuvj420p (full range) — encode ulang: -vf scale=out_range=tv,format=yuv420p -color_range tv')
    rep['gates']['G0_render_valid'] = g0
    if not a: rep['notes'].append('Tidak ada audio. Video promo tanpa suara kehilangan ~50% dampak — tambahkan SFX/VO kecuali memang diminta bisu.')

    # frame kecil abu-abu untuk analisis gerak
    w = 48; h = int(round(H * w / W / 2) * 2)   # resolusi rendah: grain/noise film rata, gerak nyata tetap terdeteksi
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vf', f'scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    diff = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    still = diff < 0.25   # di 48 px: drift/grain halus < 0.25, gerak nyata > 1
    # akhir: hitung end hold
    k = 0
    for s in still[::-1]:
        if not s: break
        k += 1
    end_hold = k / fps
    runs, i = [], 0
    body = still[: len(still) - k]
    while i < len(body):
        if body[i]:
            j = i
            while j < len(body) and body[j]: j += 1
            if j - i > 3: runs.append((round(i / fps, 2), round(j / fps, 2), j - i))
            i = j
        else: i += 1
    rep['gates']['G2_no_dead_frames'] = len(runs) == 0
    rep['dead_runs'] = runs[:20]
    rep['gates']['G3_end_hold'] = 0.4 <= end_hold <= 1.6
    rep['end_hold_s'] = round(end_hold, 2)
    # frame hitam di awal
    bd = sh(['ffmpeg', '-v', 'info', '-i', src, '-vf', 'blackdetect=d=0.1:pic_th=0.98', '-an', '-f', 'null', '-']).stderr
    blacks = re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', bd)
    if blacks and float(blacks[0][0]) < 0.05: rep['notes'].append(f'Dibuka dengan layar hitam {blacks[0]} — hook detik pertama terbuang.')
    # loudness
    if a:
        lo = sh(['ffmpeg', '-v', 'info', '-i', src, '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
        I = re.findall(r'I:\s+(-?[\d.]+) LUFS', lo); TP = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', lo)
        if I:
            li = float(I[-1]); tp = float(TP[-1]) if TP else 0
            rep['loudness'] = dict(integrated_lufs=li, true_peak_dbfs=tp, target=target)
            rep['gates']['G6_loudness'] = abs(li - target) <= 1.5 and tp <= -0.5
            if not rep['gates']['G6_loudness']:
                rep['notes'].append(f'Normalisasi: ffmpeg -i in.mp4 -c:v copy -af loudnorm=I={target}:TP=-1:LRA=11 out.mp4')

    # lembar kontak + zona aman
    sheet = arg('sheet', re.sub(r'\.mp4$', '', src) + '.sheet.png')
    n = int(arg('n', 24)); cols = int(arg('cols', 6))
    times = [dur * (i + 0.5) / n for i in range(n)]
    tw = 300; th = int(tw * H / W)
    img = Image.new('RGB', (cols * tw, ((n + cols - 1) // cols) * (th + 22)), (18, 18, 22))
    d = ImageDraw.Draw(img)
    z = SAFE.get(plat, SAFE['feed']) if H > W else SAFE['youtube']
    sx, sy = tw / 1080 if H > W else tw / 1920, th / 1920 if H > W else th / 1080
    for idx, t in enumerate(times):
        png = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', src, '-frames:v', '1', '-vf', f'scale={tw}:{th}', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
        from io import BytesIO
        try: im = Image.open(BytesIO(png)).convert('RGB')
        except Exception: continue
        ov = ImageDraw.Draw(im, 'RGBA')
        ov.rectangle([0, 0, tw, z['top'] * sy], fill=(255, 0, 80, 40))
        ov.rectangle([0, th - z['bottom'] * sy, tw, th], fill=(255, 0, 80, 40))
        ov.rectangle([tw - z['right'] * sx, 0, tw, th], fill=(255, 0, 80, 40))
        x, y = (idx % cols) * tw, (idx // cols) * (th + 22)
        img.paste(im, (x, y)); d.text((x + 6, y + th + 4), f'{t:5.2f}s', fill=(230, 230, 230))
    img.save(sheet)
    rep['contact_sheet'] = sheet
    rep['eye_gates_todo'] = ['G1 teks terbaca & ejaan benar', 'G4 satu hero per frame', 'G5 tanpa page chrome/label debug', 'G7 brand: warna/logo/font sesuai', 'G8 klaim & disclaimer benar (finansial)']
    ok = all(rep['gates'].values())
    rep['machine_pass'] = ok
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
