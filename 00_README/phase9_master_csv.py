# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
"""
DF06 Kelompok 6 - FASE 9: Item-Level Classification + Master CSV (tag_results.csv)
Operator : Iqbal Rizky Maulana
Date     : 2026-10-01

Menggabungkan hasil ExifTool dan Pillow ke dalam satu CSV master
sesuai field yang ditetapkan dalam pre-registration dan modul.

Output: 07_ANALYSIS/tag_results.csv
"""

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

EXIFTOOL_CLASS = Path(__file__).parent.parent / "04_EXIFTOOL" / "exiftool_tag_classification.csv"
PILLOW_CLASS   = Path(__file__).parent.parent / "05_PARSER2" / "pillow_tag_classification.csv"
TRANS_SHA_CSV  = Path(__file__).parent.parent / "06_RAW_RESULTS" / "transformed_sha256.csv"
RUN_LOG_CSV    = Path(__file__).parent.parent / "06_RAW_RESULTS" / "transform_run_log.csv"
OUT_DIR        = Path(__file__).parent.parent / "07_ANALYSIS"
TIMESTAMP      = datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")
OPERATOR       = "Iqbal Rizky Maulana"

OUT_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("DF06 Kelompok 6 - Fase 9: Master tag_results.csv")
print("=" * 70)
print(f"Timestamp: {TIMESTAMP}")

# ── Load SHA-256 lookup ────────────────────────────────────────────────────────
sha_map = {}  # {(transformation, filename): (sha256, size)}
with open(TRANS_SHA_CSV, encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        key = (row["transformation"], row["filename"])
        sha_map[key] = (row["sha256"], row["size_bytes"])

print(f"SHA lookup entries: {len(sha_map)}")

# ── Load runtime lookup ────────────────────────────────────────────────────────
runtime_map = defaultdict(float)  # {(transformation, filename): runtime_sec}
with open(RUN_LOG_CSV, encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        # Map transformation name
        trans = row["transformation"]
        param = row["parameter"]
        # Build key matching transformed sha csv
        if "95" in param:
            t_key = "recompress_q95"
        elif "75" in param:
            t_key = "recompress_q75"
        elif "50" in param:
            t_key = "recompress_q50"
        else:
            t_key = trans
        key = (t_key, row["filename"])
        runtime_map[key] = float(row.get("runtime_sec", 0))

print(f"Runtime lookup entries: {len(runtime_map)}")

# ── Build case_id counter ──────────────────────────────────────────────────────
TRANSFORM_CODES = {
    "resize": "RSZ",
    "recompress_q95": "RCQ95",
    "recompress_q75": "RCQ75",
    "recompress_q50": "RCQ50",
    "convert_png": "CPNG",
    "convert_jpeg": "CJPG",
    "stripped": "STRIP",
    "screenshot_like": "SCR",
}

TRANSFORM_PARAMS = {
    "resize": "50pct_320x240",
    "recompress_q95": "quality_95",
    "recompress_q75": "quality_75",
    "recompress_q50": "quality_50",
    "convert_png": "JPEG_to_PNG",
    "convert_jpeg": "JPEG_PNG_JPEG",
    "stripped": "exiftool_all=",
    "screenshot_like": "PIL_new_canvas",
}

# ── Load and merge both parser CSVs ──────────────────────────────────────────
all_rows = []
case_counter = 1

for csv_path, tool_name in [(EXIFTOOL_CLASS, "ExifTool_13.59"), (PILLOW_CLASS, "Pillow_12.0.0")]:
    with open(csv_path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            trans  = row["transformation"]
            fname  = row["filename"]
            tag    = row["tag_name"]

            # source_id: extract image number
            stem = Path(fname).stem  # e.g. IMG_01
            num  = stem.split("_")[-1] if "_" in stem else "00"

            code = TRANSFORM_CODES.get(trans, "UNK")
            case_id = f"DF06-{code}-{num}-R1"
            param   = TRANSFORM_PARAMS.get(trans, "")

            # sha256 & size
            sha_key = (trans, fname)
            sha, size = sha_map.get(sha_key, ("", ""))

            # runtime
            rt_key = (trans, fname.replace(".png", ".jpg"))
            runtime = runtime_map.get(rt_key, 0.0)
            if runtime == 0.0:
                # Try direct key
                rt_key2 = (trans, fname)
                runtime = runtime_map.get(rt_key2, 0.0)

            all_rows.append({
                "case_id":         case_id,
                "source_id":       f"E{num}",
                "transformation":  trans,
                "parameter":       param,
                "tag_name":        tag,
                "expected_value":  row["expected_value"],
                "tool":            tool_name,
                "observed_value":  row["observed_value"],
                "status":          row["status"],
                "file_sha256":     sha,
                "file_size":       size,
                "runtime_sec":     round(runtime, 4),
                "notes":           f"img_format={row.get('img_format','NA')}",
            })
            case_counter += 1

print(f"Total rows assembled: {len(all_rows)}")

# ── Save master CSV ────────────────────────────────────────────────────────────
fields = [
    "case_id", "source_id", "transformation", "parameter",
    "tag_name", "expected_value", "tool", "observed_value",
    "status", "file_sha256", "file_size", "runtime_sec", "notes"
]
out_csv = OUT_DIR / "tag_results.csv"
with open(out_csv, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    w.writerows(all_rows)
print(f"Master CSV: {out_csv}  ({len(all_rows)} rows)")

# ── Quick status summary ───────────────────────────────────────────────────────
status_count = defaultdict(int)
for row in all_rows:
    status_count[row["status"]] += 1

print("\n-- Status Summary (all rows, both parsers) --------------------------------")
for s, c in sorted(status_count.items()):
    print(f"  {s:<15} : {c:>6} rows")

total = sum(status_count.values())
print(f"  {'TOTAL':<15} : {total:>6} rows")

print("\n" + "=" * 70)
print("FASE 9 SELESAI")
print("=" * 70)
