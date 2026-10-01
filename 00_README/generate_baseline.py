"""
DF06 Kelompok 6 — Generate 30 Baseline JPEG Images
Operator : Iqbal Rizky Maulana
Date     : 2026-10-01
Purpose  : Membuat 30 gambar JPEG sintetis sebagai baseline dataset
           untuk eksperimen ketahanan metadata EXIF.

Reproducibility:
  - Seed deterministik: random.Random(6000 + i) per gambar
  - Ukuran tetap: 640 x 480 px
  - Format: JPEG quality=90
  - Nama file: IMG_01.jpg s/d IMG_30.jpg
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random
import time
import hashlib
import os

# ── Konfigurasi ──────────────────────────────────────────────────────────────
OUT_DIR = Path(__file__).parent.parent / "01_BASELINE"
IMG_WIDTH, IMG_HEIGHT = 640, 480
JPEG_QUALITY = 90
NUM_IMAGES = 30
SEED_BASE = 6000

# ── Buat folder output ───────────────────────────────────────────────────────
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("DF06 Kelompok 6 — Baseline Image Generator")
print("=" * 60)
print(f"Output dir  : {OUT_DIR.resolve()}")
print(f"Resolution  : {IMG_WIDTH} x {IMG_HEIGHT} px")
print(f"JPEG quality: {JPEG_QUALITY}")
print(f"Total images: {NUM_IMAGES}")
print(f"Seed base   : SEED_BASE + i  ({SEED_BASE}+1 s/d {SEED_BASE}+{NUM_IMAGES})")
print("-" * 60)

start_total = time.time()
created_files = []

for i in range(1, NUM_IMAGES + 1):
    r = random.Random(SEED_BASE + i)

    # Background color (per-image seed)
    bg_color = (r.randrange(30, 200), r.randrange(30, 200), r.randrange(30, 200))
    im = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), bg_color)
    draw = ImageDraw.Draw(im)

    # Horizontal gradient strips untuk variasi visual
    strip_h = IMG_HEIGHT // 8
    for s in range(8):
        sc = (r.randrange(20, 230), r.randrange(20, 230), r.randrange(20, 230))
        draw.rectangle([0, s * strip_h, IMG_WIDTH, (s + 1) * strip_h], fill=sc)

    # Label teks identifikasi
    label = f"DF06-{i:02d}  SYNTHETIC"
    draw.rectangle([10, 10, 260, 44], fill=(0, 0, 0))
    draw.text((15, 15), label, fill=(255, 255, 0))

    # Label resolusi dan nomor seed
    draw.text((15, 52), f"640x480  seed={SEED_BASE+i}", fill=(200, 200, 200))

    # Titik-titik warna acak (variasi visual antar gambar)
    for _ in range(40):
        x = r.randrange(IMG_WIDTH - 20)
        y = r.randrange(IMG_HEIGHT - 20)
        rc = (r.randrange(256), r.randrange(256), r.randrange(256))
        draw.ellipse((x, y, x + 20, y + 20), fill=rc)

    # Garis diagonal acak
    for _ in range(5):
        x1, y1 = r.randrange(IMG_WIDTH), r.randrange(IMG_HEIGHT)
        x2, y2 = r.randrange(IMG_WIDTH), r.randrange(IMG_HEIGHT)
        lc = (r.randrange(256), r.randrange(256), r.randrange(256))
        draw.line((x1, y1, x2, y2), fill=lc, width=2)

    # Simpan
    out_path = OUT_DIR / f"IMG_{i:02d}.jpg"
    im.save(out_path, "JPEG", quality=JPEG_QUALITY)

    # Hitung SHA-256 segera setelah dibuat
    sha256 = hashlib.sha256(out_path.read_bytes()).hexdigest()
    size_bytes = out_path.stat().st_size
    created_files.append((out_path.name, size_bytes, sha256))

    print(f"  [{i:02d}/30] {out_path.name}  {size_bytes:>7,} bytes  {sha256[:16]}…")

elapsed = time.time() - start_total

# ── Ringkasan ────────────────────────────────────────────────────────────────
print("-" * 60)
print(f"[OK] {len(created_files)} baseline images created in {elapsed:.2f}s")
print(f"    Total size: {sum(s for _, s, _ in created_files):,} bytes")

# Verifikasi jumlah file di folder
actual_count = len(list(OUT_DIR.glob("*.jpg")))
print(f"    Files in 01_BASELINE: {actual_count}")
if actual_count != NUM_IMAGES:
    print(f"[WARN] Expected {NUM_IMAGES}, found {actual_count}")
else:
    print("    Count check: OK")
print("=" * 60)
