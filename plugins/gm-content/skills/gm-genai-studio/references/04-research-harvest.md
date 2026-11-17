# Riset & Panen Sumber

## 1. Urutan alat

| Butuh | Alat | Catatan |
|---|---|---|
| Fakta, angka, berita | WebSearch → WebFetch | Default; kutipan ≤ 15 kata, sisanya parafrase |
| Halaman berat JS / banyak halaman | Firecrawl (API, atau MCP `firecrawl-mcp-server` MIT) | Kunci di env `FIRECRAWL_API_KEY`, **jangan** ditempel di chat/log |
| Self-host tanpa biaya per halaman | crawl4ai (Apache-2.0) di server sendiri | Server Firecrawl AGPL — boleh dipakai internal, jangan disematkan ke SaaS |
| Satu halaman → markdown cepat | Jina Reader (`r.jina.ai/<url>`, repo Apache) | Bila WebFetch gagal render |
| Video: metadata, subtitle, komentar | `yt-dlp` | Lihat §2 |
| Tren | TikTok Creative Center, Google Trends, vidIQ, 1of10 | Catat tanggal akses |
| Paper/model baru | huggingface.co/papers, Artificial Analysis | |

## 2. yt-dlp — resep

```bash
pip install -U yt-dlp
# metadata + subtitle otomatis (tanpa unduh video)
yt-dlp --skip-download --write-info-json --write-auto-subs --sub-langs "id.*,en.*" -o "riset/%(id)s.%(ext)s" "<url>"
# komentar (pertanyaan nyata audiens → ide konten)
yt-dlp --skip-download --write-comments --extractor-args "youtube:max_comments=300" -o "riset/%(id)s" "<url>"
# daftar video satu channel (judul, view, durasi) tanpa unduh
yt-dlp --flat-playlist --print "%(id)s\t%(view_count)s\t%(duration)s\t%(title)s" "<channel_url>/videos"
# referensi untuk analisis (≤720p)
python scripts/ref_dna.py "<url>" --out proyek/ref_dna
```
Kalau YouTube meminta login/cookie: `--cookies-from-browser chrome` hanya di PC Hendra dan hanya untuk akunnya sendiri; jangan menyimpan cookie di repo/log.

## 3. Analisis outlier (pola 1of10)

1. Tarik daftar video channel pesaing/rujukan (`--flat-playlist`).
2. Hitung `view / median view channel` → video dengan rasio ≥ 3 = outlier.
3. Untuk tiap outlier: judul, hook 3 detik pertama (`ref_dna.py`), format, durasi → tabel pola.
4. Ide = pola outlier × topik GO Markets × bukti resmi yang ada.

## 4. Etika & kepatuhan

- Unduhan hanya untuk analisis internal atau konten milik sendiri/berizin; **tidak** diunggah ulang.
- Hormati robots.txt dan ToS situs saat crawl massal; batasi laju.
- Data pribadi (nama, kontak) dari komentar tidak disimpan.
- Setiap klaim di naskah → `sumber.md` (URL + tanggal akses).
