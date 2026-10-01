# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
"""
DF06 Kelompok 6 - FASE 7: ExifTool Extraction dari Semua Transformed Files
Operator : Iqbal Rizky Maulana
Date     : 2026-10-01

Output:
  04_EXIFTOOL/transformed_metadata_exiftool.json  -- raw ExifTool JSON output
  04_EXIFTOOL/exiftool_extraction_log.csv         -- log per file
"""

import subprocess
import csv
import json
import time
from datetime import datetime
from pathlib import Path

EXIFTOOL     = r"E:\UNIVERSITAS PENDIDIKAN INDONESIA\APP\exiftool\exiftool.exe"
TRANS_DIR    = Path(__file__).parent.parent / "03_TRANSFORMED"
OUT_DIR      = Path(__file__).parent.parent / "04_EXIFTOOL"
OPERATOR     = "Iqbal Rizky Maulana"
TIMESTAMP    = datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

OUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("DF06 Kelompok 6 - Fase 7: ExifTool Extraction")
print("=" * 70)
print(f"Timestamp: {TIMESTAMP}")
print(f"Source   : {TRANS_DIR.resolve()}")

# Kumpulkan semua file transformed (JPEG dan PNG)
all_files = sorted(TRANS_DIR.glob("*/*"))
image_exts = {".jpg", ".jpeg", ".png"}
all_files = [f for f in all_files if f.suffix.lower() in image_exts]
print(f"Files    : {len(all_files)} images found")
print()

# ── Jalankan ExifTool batch (satu call untuk semua file) ──────────────────────
t0 = time.time()
print("Running ExifTool batch extraction...")

cmd = [EXIFTOOL, "-json", "-G1", "-a", "-s"] + [str(f) for f in all_files]
result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=300)

elapsed_total = round(time.time() - t0, 2)
print(f"ExifTool completed in {elapsed_total}s  (returncode={result.returncode})")

if result.returncode not in (0, 1):  # ExifTool returns 1 for warnings
    print(f"[ERROR] ExifTool stderr: {result.stderr[:500]}")
    raise SystemExit(1)

# Parse JSON output
raw_json = result.stdout
try:
    records = json.loads(raw_json)
except json.JSONDecodeError as e:
    print(f"[ERROR] JSON parse failed: {e}")
    # Try to save raw for debugging
    (OUT_DIR / "raw_exiftool_stdout.txt").write_text(raw_json, encoding="utf-8")
    raise

print(f"Records parsed: {len(records)}")

# ── Simpan raw JSON ────────────────────────────────────────────────────────────
raw_json_path = OUT_DIR / "transformed_metadata_exiftool.json"
with open(raw_json_path, "w", encoding="utf-8") as fh:
    json.dump(records, fh, indent=2, ensure_ascii=False)
print(f"Raw JSON saved: {raw_json_path}")

# ── Buat extraction log per file ───────────────────────────────────────────────
# Target tags yang kita uji
TARGET_TAGS = [
    "DateTimeOriginal", "Make", "Model", "Software", "Artist",
    "Copyright", "UserComment", "GPSLatitude", "GPSLongitude"
]

extraction_log = []

for rec in records:
    source_path = Path(rec.get("SourceFile", ""))
    # Determine transformation from parent dir name
    parts = source_path.parts
    # Find 03_TRANSFORMED in path, next part is transformation name
    try:
        idx = next(i for i, p in enumerate(parts) if "03_TRANSFORMED" in p)
        transformation = parts[idx + 1] if idx + 1 < len(parts) else "unknown"
    except StopIteration:
        transformation = "unknown"

    filename = source_path.name

    # Extract tag values - ExifTool -s -G1 output format: "GroupName:TagName"
    # The JSON keys will be like "EXIF:DateTimeOriginal", "IFD0:Make", etc.
    tag_values = {}
    for key, val in rec.items():
        for tag in TARGET_TAGS:
            if key.endswith(":" + tag) or key == tag:
                tag_values[tag] = str(val)

    # Log each found tag
    for tag in TARGET_TAGS:
        val = tag_values.get(tag, None)
        extraction_log.append({
            "transformation": transformation,
            "filename": filename,
            "tag_name": tag,
            "found": "yes" if val is not None else "no",
            "observed_value": val if val is not None else "",
        })

log_csv_path = OUT_DIR / "exiftool_extraction_log.csv"
fieldnames = ["transformation", "filename", "tag_name", "found", "observed_value"]
with open(log_csv_path, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(extraction_log)
print(f"Extraction log : {log_csv_path}  ({len(extraction_log)} rows)")

# ── Summary per transformation ─────────────────────────────────────────────────
print()
print("-- Summary per transformation ------------------------------------------")
from collections import defaultdict
trans_stats = defaultdict(lambda: {"found": 0, "missing": 0, "files": set()})
for row in extraction_log:
    t = row["transformation"]
    trans_stats[t]["files"].add(row["filename"])
    if row["found"] == "yes":
        trans_stats[t]["found"] += 1
    else:
        trans_stats[t]["missing"] += 1

for t in sorted(trans_stats):
    s = trans_stats[t]
    n_files = len(s["files"])
    found = s["found"]
    missing = s["missing"]
    total = found + missing
    rate = round(found / total * 100, 1) if total > 0 else 0
    print(f"  {t:<22}: {n_files:>2} files | {found:>3} found / {missing:>3} missing | {rate}% tag presence")

print()
print("=" * 70)
print("FASE 7 SELESAI")
print("=" * 70)
