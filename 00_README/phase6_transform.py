# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
"""
DF06 Kelompok 6 - FASE 6: Eksperimen Transformasi (8 Kondisi)
Operator : Iqbal Rizky Maulana
Date     : 2026-10-01

Transformasi yang dijalankan:
  1. resize        — 50% dimension (320x240), quality=90
  2. recompress_q95 — JPEG quality=95
  3. recompress_q75 — JPEG quality=75
  4. recompress_q50 — JPEG quality=50
  5. convert_jpeg  — JPEG → PNG → JPEG (round-trip), quality=90
  6. stripped      — ExifTool -all= (hapus semua metadata)
  7. screenshot_like — PIL re-encode tanpa copy EXIF (simulasi screenshot)

Output: 03_TRANSFORMED/<kondisi>/IMG_XX.jpg
        06_RAW_RESULTS/transformed_sha256.csv
        06_RAW_RESULTS/transform_run_log.csv

ATURAN: Baseline 01_BASELINE/ TIDAK boleh ditimpa.
        Setiap transformasi menghasilkan file BARU.
"""

import hashlib
import csv
import time
import subprocess
import shutil
import json
from datetime import datetime
from pathlib import Path
from PIL import Image

# ── Konfigurasi ───────────────────────────────────────────────────────────────
EXIFTOOL     = r"E:\UNIVERSITAS PENDIDIKAN INDONESIA\APP\exiftool\exiftool.exe"
BASELINE_DIR = Path(__file__).parent.parent / "01_BASELINE"
TRANS_DIR    = Path(__file__).parent.parent / "03_TRANSFORMED"
RAW_DIR      = Path(__file__).parent.parent / "06_RAW_RESULTS"
OPERATOR     = "Iqbal Rizky Maulana"
TIMESTAMP    = datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

# ── Buat output directories ────────────────────────────────────────────────────
conditions = ["resize", "recompress_q95", "recompress_q75", "recompress_q50",
              "convert_png", "convert_jpeg", "stripped", "screenshot_like"]
for c in conditions:
    (TRANS_DIR / c).mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(exist_ok=True)

print("=" * 75)
print("DF06 Kelompok 6 — Fase 6: Transformasi Eksperimen")
print("=" * 75)
print(f"Timestamp: {TIMESTAMP}")
print(f"Source   : {BASELINE_DIR.resolve()}")
print(f"Output   : {TRANS_DIR.resolve()}")
print()

files = sorted(BASELINE_DIR.glob("*.jpg"))
if not files:
    print("[ERROR] Tidak ada file di 01_BASELINE/")
    raise SystemExit(1)

run_log = []   # untuk transform_run_log.csv
hash_log = []  # untuk transformed_sha256.csv

# ═══════════════════════════════════════════════════════════════════════════════
# Transformasi 1: RESIZE (320×240, 50% dari 640×480)
# ═══════════════════════════════════════════════════════════════════════════════
print("-- [1/7] RESIZE (320x240) ----------------------------------------------")
t_start = time.time()
ok_count, fail_count = 0, 0
for f in files:
    t0 = time.time()
    out = TRANS_DIR / "resize" / f.name
    try:
        with Image.open(f) as im:
            resized = im.resize((320, 240), Image.LANCZOS)
            resized.save(out, format="JPEG", quality=90)
        elapsed = round(time.time() - t0, 4)
        sha = sha256_file(out)
        run_log.append({"transformation":"resize","parameter":"50pct_320x240","filename":f.name,"output":str(out),"status":"ok","runtime_sec":elapsed,"error":""})
        hash_log.append({"transformation":"resize","filename":f.name,"size_bytes":out.stat().st_size,"sha256":sha})
        ok_count += 1
        print(f"  OK  {f.name} → {out.name}  ({elapsed:.3f}s)")
    except Exception as e:
        elapsed = round(time.time() - t0, 4)
        run_log.append({"transformation":"resize","parameter":"50pct_320x240","filename":f.name,"output":str(out),"status":"fail","runtime_sec":elapsed,"error":str(e)})
        fail_count += 1
        print(f"  FAIL {f.name}: {e}")
t_total = round(time.time() - t_start, 2)
print(f"  >> resize: {ok_count} OK / {fail_count} FAIL  | total {t_total}s")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# Transformasi 2: RECOMPRESS quality=95
# ═══════════════════════════════════════════════════════════════════════════════
print("-- [2/7] RECOMPRESS quality=95 -----------------------------------------")
t_start = time.time()
ok_count, fail_count = 0, 0
for f in files:
    t0 = time.time()
    out = TRANS_DIR / "recompress_q95" / f.name
    try:
        with Image.open(f) as im:
            im.save(out, format="JPEG", quality=95)
        elapsed = round(time.time() - t0, 4)
        sha = sha256_file(out)
        run_log.append({"transformation":"recompress","parameter":"quality_95","filename":f.name,"output":str(out),"status":"ok","runtime_sec":elapsed,"error":""})
        hash_log.append({"transformation":"recompress_q95","filename":f.name,"size_bytes":out.stat().st_size,"sha256":sha})
        ok_count += 1
        print(f"  OK  {f.name}  ({elapsed:.3f}s)")
    except Exception as e:
        elapsed = round(time.time() - t0, 4)
        run_log.append({"transformation":"recompress","parameter":"quality_95","filename":f.name,"output":str(out),"status":"fail","runtime_sec":elapsed,"error":str(e)})
        fail_count += 1
        print(f"  FAIL {f.name}: {e}")
t_total = round(time.time() - t_start, 2)
print(f"  >> recompress_q95: {ok_count} OK / {fail_count} FAIL  | total {t_total}s")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# Transformasi 3: RECOMPRESS quality=75
# ═══════════════════════════════════════════════════════════════════════════════
print("-- [3/7] RECOMPRESS quality=75 -----------------------------------------")
t_start = time.time()
ok_count, fail_count = 0, 0
for f in files:
    t0 = time.time()
    out = TRANS_DIR / "recompress_q75" / f.name
    try:
        with Image.open(f) as im:
            im.save(out, format="JPEG", quality=75)
        elapsed = round(time.time() - t0, 4)
        sha = sha256_file(out)
        run_log.append({"transformation":"recompress","parameter":"quality_75","filename":f.name,"output":str(out),"status":"ok","runtime_sec":elapsed,"error":""})
        hash_log.append({"transformation":"recompress_q75","filename":f.name,"size_bytes":out.stat().st_size,"sha256":sha})
        ok_count += 1
        print(f"  OK  {f.name}  ({elapsed:.3f}s)")
    except Exception as e:
        elapsed = round(time.time() - t0, 4)
        run_log.append({"transformation":"recompress","parameter":"quality_75","filename":f.name,"output":str(out),"status":"fail","runtime_sec":elapsed,"error":str(e)})
        fail_count += 1
        print(f"  FAIL {f.name}: {e}")
t_total = round(time.time() - t_start, 2)
print(f"  >> recompress_q75: {ok_count} OK / {fail_count} FAIL  | total {t_total}s")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# Transformasi 4: RECOMPRESS quality=50
# ═══════════════════════════════════════════════════════════════════════════════
print("-- [4/7] RECOMPRESS quality=50 -----------------------------------------")
t_start = time.time()
ok_count, fail_count = 0, 0
for f in files:
    t0 = time.time()
    out = TRANS_DIR / "recompress_q50" / f.name
    try:
        with Image.open(f) as im:
            im.save(out, format="JPEG", quality=50)
        elapsed = round(time.time() - t0, 4)
        sha = sha256_file(out)
        run_log.append({"transformation":"recompress","parameter":"quality_50","filename":f.name,"output":str(out),"status":"ok","runtime_sec":elapsed,"error":""})
        hash_log.append({"transformation":"recompress_q50","filename":f.name,"size_bytes":out.stat().st_size,"sha256":sha})
        ok_count += 1
        print(f"  OK  {f.name}  ({elapsed:.3f}s)")
    except Exception as e:
        elapsed = round(time.time() - t0, 4)
        run_log.append({"transformation":"recompress","parameter":"quality_50","filename":f.name,"output":str(out),"status":"fail","runtime_sec":elapsed,"error":str(e)})
        fail_count += 1
        print(f"  FAIL {f.name}: {e}")
t_total = round(time.time() - t_start, 2)
print(f"  >> recompress_q50: {ok_count} OK / {fail_count} FAIL  | total {t_total}s")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# Transformasi 5: FORMAT CONVERSION (JPEG → PNG, simpan sebagai PNG)
# ═══════════════════════════════════════════════════════════════════════════════
print("-- [5a/7] FORMAT CONVERSION: JPEG -> PNG --------------------------------")
t_start = time.time()
ok_count, fail_count = 0, 0
for f in files:
    t0 = time.time()
    out = TRANS_DIR / "convert_png" / (f.stem + ".png")
    try:
        with Image.open(f) as im:
            im.save(out, format="PNG")
        elapsed = round(time.time() - t0, 4)
        sha = sha256_file(out)
        run_log.append({"transformation":"convert_png","parameter":"JPEG_to_PNG","filename":f.name,"output":str(out),"status":"ok","runtime_sec":elapsed,"error":""})
        hash_log.append({"transformation":"convert_png","filename":out.name,"size_bytes":out.stat().st_size,"sha256":sha})
        ok_count += 1
        print(f"  OK  {f.name} → {out.name}  ({elapsed:.3f}s)")
    except Exception as e:
        elapsed = round(time.time() - t0, 4)
        run_log.append({"transformation":"convert_png","parameter":"JPEG_to_PNG","filename":f.name,"output":str(out),"status":"fail","runtime_sec":elapsed,"error":str(e)})
        fail_count += 1
        print(f"  FAIL {f.name}: {e}")
t_total = round(time.time() - t_start, 2)
print(f"  >> convert_png: {ok_count} OK / {fail_count} FAIL  | total {t_total}s")
print()

# ── 5b: PNG → JPEG (round trip) ───────────────────────────────────────────────
print("-- [5b/7] FORMAT CONVERSION: PNG -> JPEG (round-trip) ------------------")
t_start = time.time()
ok_count, fail_count = 0, 0
for f in files:
    t0 = time.time()
    png_path = TRANS_DIR / "convert_png" / (f.stem + ".png")
    out = TRANS_DIR / "convert_jpeg" / f.name   # back to .jpg
    try:
        with Image.open(png_path) as im:
            rgb = im.convert("RGB")
            rgb.save(out, format="JPEG", quality=90)
        elapsed = round(time.time() - t0, 4)
        sha = sha256_file(out)
        run_log.append({"transformation":"convert_jpeg","parameter":"PNG_to_JPEG_q90","filename":f.name,"output":str(out),"status":"ok","runtime_sec":elapsed,"error":""})
        hash_log.append({"transformation":"convert_jpeg","filename":f.name,"size_bytes":out.stat().st_size,"sha256":sha})
        ok_count += 1
        print(f"  OK  {png_path.name} → {out.name}  ({elapsed:.3f}s)")
    except Exception as e:
        elapsed = round(time.time() - t0, 4)
        run_log.append({"transformation":"convert_jpeg","parameter":"PNG_to_JPEG_q90","filename":f.name,"output":str(out),"status":"fail","runtime_sec":elapsed,"error":str(e)})
        fail_count += 1
        print(f"  FAIL {f.name}: {e}")
t_total = round(time.time() - t_start, 2)
print(f"  >> convert_jpeg: {ok_count} OK / {fail_count} FAIL  | total {t_total}s")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# Transformasi 6: METADATA STRIPPING (ExifTool -all=)
# ═══════════════════════════════════════════════════════════════════════════════
print("-- [6/7] METADATA STRIPPING (ExifTool -all=) ---------------------------")
t_start = time.time()
ok_count, fail_count = 0, 0
for f in files:
    t0 = time.time()
    out = TRANS_DIR / "stripped" / f.name
    shutil.copy2(f, out)    # copy baseline dulu
    try:
        result = subprocess.run(
            [EXIFTOOL, "-overwrite_original", "-all=", str(out)],
            capture_output=True, text=True, timeout=30
        )
        elapsed = round(time.time() - t0, 4)
        if result.returncode == 0:
            sha = sha256_file(out)
            run_log.append({"transformation":"stripped","parameter":"exiftool_all=","filename":f.name,"output":str(out),"status":"ok","runtime_sec":elapsed,"error":""})
            hash_log.append({"transformation":"stripped","filename":f.name,"size_bytes":out.stat().st_size,"sha256":sha})
            ok_count += 1
            print(f"  OK  {f.name}  ({elapsed:.3f}s)")
        else:
            run_log.append({"transformation":"stripped","parameter":"exiftool_all=","filename":f.name,"output":str(out),"status":"fail","runtime_sec":elapsed,"error":result.stderr})
            fail_count += 1
            print(f"  FAIL {f.name}: {result.stderr[:80]}")
    except Exception as e:
        elapsed = round(time.time() - t0, 4)
        run_log.append({"transformation":"stripped","parameter":"exiftool_all=","filename":f.name,"output":str(out),"status":"fail","runtime_sec":elapsed,"error":str(e)})
        fail_count += 1
        print(f"  FAIL {f.name}: {e}")
t_total = round(time.time() - t_start, 2)
print(f"  >> stripped: {ok_count} OK / {fail_count} FAIL  | total {t_total}s")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# Transformasi 7: SCREENSHOT-LIKE RE-ENCODE
# (PIL open → new Image canvas → paste pixel data → save JPEG, NO EXIF copy)
# ═══════════════════════════════════════════════════════════════════════════════
print("-- [7/7] SCREENSHOT-LIKE RE-ENCODE -------------------------------------")
t_start = time.time()
ok_count, fail_count = 0, 0
for f in files:
    t0 = time.time()
    out = TRANS_DIR / "screenshot_like" / f.name
    try:
        with Image.open(f) as im:
            # Extract raw pixel data only, discard all metadata
            rgb_data = im.convert("RGB")
            new_img = Image.new("RGB", rgb_data.size)
            new_img.paste(rgb_data)
            new_img.save(out, format="JPEG", quality=90)
        elapsed = round(time.time() - t0, 4)
        sha = sha256_file(out)
        run_log.append({"transformation":"screenshot_like","parameter":"PIL_new_canvas_no_exif","filename":f.name,"output":str(out),"status":"ok","runtime_sec":elapsed,"error":""})
        hash_log.append({"transformation":"screenshot_like","filename":f.name,"size_bytes":out.stat().st_size,"sha256":sha})
        ok_count += 1
        print(f"  OK  {f.name}  ({elapsed:.3f}s)")
    except Exception as e:
        elapsed = round(time.time() - t0, 4)
        run_log.append({"transformation":"screenshot_like","parameter":"PIL_new_canvas_no_exif","filename":f.name,"output":str(out),"status":"fail","runtime_sec":elapsed,"error":str(e)})
        fail_count += 1
        print(f"  FAIL {f.name}: {e}")
t_total = round(time.time() - t_start, 2)
print(f"  >> screenshot_like: {ok_count} OK / {fail_count} FAIL  | total {t_total}s")
print()

# ═══════════════════════════════════════════════════════════════════════════════
# SIMPAN LOGS
# ═══════════════════════════════════════════════════════════════════════════════
# Run log CSV
run_log_csv = RAW_DIR / "transform_run_log.csv"
fieldnames_r = ["transformation","parameter","filename","output","status","runtime_sec","error"]
with open(run_log_csv, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames_r)
    w.writeheader()
    w.writerows(run_log)
print(f"Run log CSV       : {run_log_csv}")

# Hash log CSV
hash_csv = RAW_DIR / "transformed_sha256.csv"
fieldnames_h = ["transformation","filename","size_bytes","sha256"]
with open(hash_csv, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames_h)
    w.writeheader()
    w.writerows(hash_log)
print(f"Transformed SHA256: {hash_csv}")

# Count summary
print("\n-- SUMMARY ----------------------------------------------------------")
from collections import Counter
cnt = Counter(r["transformation"] for r in run_log)
ok_cnt = Counter((r["transformation"],r["status"]) for r in run_log)
for trans in cnt:
    n_ok   = ok_cnt.get((trans,"ok"), 0)
    n_fail = ok_cnt.get((trans,"fail"), 0)
    print(f"  {trans:<20} : {n_ok:>2} OK / {n_fail} FAIL")

total_files = len(hash_log)
print(f"\nTotal output files: {total_files}")
print("=" * 75)
print("FASE 6 SELESAI — Verifikasi jumlah file di setiap subfolder 03_TRANSFORMED/")
print("=" * 75)
