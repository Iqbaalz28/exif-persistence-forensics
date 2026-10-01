# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
"""
DF06 Kelompok 6 - FASE 7 FIX: ExifTool Extraction Parser + Tag Classification
Operator : Iqbal Rizky Maulana
Date     : 2026-10-01

Masalah ditemukan: Pillow save() tidak menyalin EXIF secara default.
Semua PIL-based transformations (resize, recompress, convert, screenshot_like)
menghasilkan file TANPA tag EXIF.

Hanya ExifTool-based stripping yang memiliki perbedaan: stripped file
tidak memiliki EXIF bukan karena Pillow, tapi karena ExifTool -all=.

Ini adalah temuan VALID yang harus dicatat secara akurat.

Output:
  04_EXIFTOOL/exiftool_tag_classification.csv  -- per tag × file × transform
  04_EXIFTOOL/exiftool_summary.json
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict

EXIFTOOL_JSON = Path(__file__).parent.parent / "04_EXIFTOOL" / "transformed_metadata_exiftool.json"
GT_CSV        = Path(__file__).parent.parent / "02_GROUND_TRUTH" / "expected_tags.csv"
OUT_DIR       = Path(__file__).parent.parent / "04_EXIFTOOL"
TIMESTAMP     = datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

TARGET_TAGS = [
    "DateTimeOriginal", "Make", "Model", "Software", "Artist",
    "Copyright", "UserComment", "GPSLatitude", "GPSLongitude"
]

# Tag name mapping: ExifTool -G1 -s output uses "Group:TagName" format
# We need to search across all groups
def extract_tag_from_record(rec, tag_name):
    """Extract tag value from ExifTool -G1 -s JSON record."""
    for key, val in rec.items():
        # Match "EXIF:DateTimeOriginal" or "IFD0:Make" or direct "TagName"
        if key == tag_name or key.endswith(":" + tag_name):
            return str(val)
    return None

print("=" * 70)
print("DF06 Kelompok 6 - Fase 7 Fix: ExifTool Tag Classification")
print("=" * 70)
print(f"Timestamp: {TIMESTAMP}")

# Load ExifTool raw JSON
with open(EXIFTOOL_JSON, encoding="utf-8") as fh:
    records = json.load(fh)
print(f"Records: {len(records)}")

# Load expected values from ground truth
gt_map = {}  # {filename: {tag: expected_value}}
with open(GT_CSV, encoding="utf-8-sig") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        fname = row["filename"]
        tag = row["tag_name"]
        if fname not in gt_map:
            gt_map[fname] = {}
        gt_map[fname][tag] = row["expected_value"]

print(f"Ground truth entries: {sum(len(v) for v in gt_map.values())}")

# Build classification rows
classification = []

for rec in records:
    source_path = rec.get("SourceFile", "")
    parts = Path(source_path).parts

    # Determine transformation
    try:
        idx = next(i for i, p in enumerate(parts) if "03_TRANSFORMED" in p)
        transformation = parts[idx + 1] if idx + 1 < len(parts) else "unknown"
    except StopIteration:
        transformation = "unknown"

    filename = Path(source_path).name
    # Normalize filename (PNG conversion uses .png, map back to .jpg for GT lookup)
    gt_filename = filename.replace(".png", ".jpg")
    expected_for_file = gt_map.get(gt_filename, {})

    for tag in TARGET_TAGS:
        observed = extract_tag_from_record(rec, tag)
        expected = expected_for_file.get(tag, "")

        if observed is None:
            status = "missing"
        elif observed.strip() == expected.strip():
            status = "retained"
        else:
            status = "changed"

        # UserComment ExifTool may add "charset=ASCII" prefix
        if status == "changed" and tag == "UserComment":
            # ExifTool often reports: "charset=ASCII IMG_01 controlled EXIF metadata DF06"
            if expected in observed:
                status = "retained"

        # GPSLatitude/Longitude: normalize comparison (0 deg 0' 0.00")
        if status == "changed" and tag in ("GPSLatitude", "GPSLongitude"):
            # Allow fuzzy match for GPS representations
            obs_clean = observed.replace(" ", "").replace("'", "").replace('"', "").lower()
            exp_clean = expected.replace(" ", "").replace("'", "").replace('"', "").lower()
            if obs_clean == exp_clean or "0deg0'" in observed:
                status = "retained"

        classification.append({
            "transformation": transformation,
            "filename": filename,
            "tag_name": tag,
            "expected_value": expected,
            "observed_value": observed if observed is not None else "",
            "status": status,
            "tool": "ExifTool_13.59",
        })

# Save classification CSV
class_csv = OUT_DIR / "exiftool_tag_classification.csv"
fieldnames = ["transformation", "filename", "tag_name", "expected_value", "observed_value", "status", "tool"]
with open(class_csv, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(classification)
print(f"\nClassification CSV: {class_csv}  ({len(classification)} rows)")

# Summary statistics
print("\n-- Retention Statistics per Transformation (ExifTool) ------------------")
trans_stats = defaultdict(lambda: {"retained": 0, "changed": 0, "missing": 0, "total": 0})
for row in classification:
    t = row["transformation"]
    s = row["status"]
    trans_stats[t][s] = trans_stats[t].get(s, 0) + 1
    trans_stats[t]["total"] += 1

all_eligible = 0
all_retained = 0

print(f"  {'Transform':<22} {'Retained':>8} {'Changed':>8} {'Missing':>8} {'Total':>6} {'Rate':>7}")
print(f"  {'-'*22} {'-'*8} {'-'*8} {'-'*8} {'-'*6} {'-'*7}")
for t in sorted(trans_stats):
    s = trans_stats[t]
    eligible = s.get("retained", 0) + s.get("changed", 0) + s.get("missing", 0)
    retained = s.get("retained", 0)
    changed  = s.get("changed", 0)
    missing  = s.get("missing", 0)
    rate = round(retained / eligible * 100, 1) if eligible > 0 else 0
    print(f"  {t:<22} {retained:>8} {changed:>8} {missing:>8} {eligible:>6} {rate:>6.1f}%")
    all_eligible += eligible
    all_retained += retained

overall_rate = round(all_retained / all_eligible * 100, 1) if all_eligible > 0 else 0
print(f"\n  Overall Retention Rate (ExifTool): {all_retained}/{all_eligible} = {overall_rate}%")

# Tag-level summary
print("\n-- Retention Statistics per Tag (ExifTool, all transforms) -------------")
tag_stats = defaultdict(lambda: {"retained": 0, "changed": 0, "missing": 0})
for row in classification:
    tag_stats[row["tag_name"]][row["status"]] = tag_stats[row["tag_name"]].get(row["status"], 0) + 1

print(f"  {'Tag':<25} {'Retained':>8} {'Changed':>8} {'Missing':>8} {'Rate':>7}")
print(f"  {'-'*25} {'-'*8} {'-'*8} {'-'*8} {'-'*7}")
for tag in TARGET_TAGS:
    s = tag_stats[tag]
    retained = s.get("retained", 0)
    changed  = s.get("changed", 0)
    missing  = s.get("missing", 0)
    eligible = retained + changed + missing
    rate = round(retained / eligible * 100, 1) if eligible > 0 else 0
    print(f"  {tag:<25} {retained:>8} {changed:>8} {missing:>8} {rate:>6.1f}%")

# Save summary JSON
summary = {
    "timestamp": TIMESTAMP,
    "tool": "ExifTool_13.59",
    "total_records": len(records),
    "total_rows": len(classification),
    "overall_retention_rate": f"{overall_rate}%",
    "retained": all_retained,
    "eligible": all_eligible,
    "per_transformation": {t: dict(s) for t, s in trans_stats.items()},
    "per_tag": {t: dict(s) for t, s in tag_stats.items()},
}
summary_json = OUT_DIR / "exiftool_summary.json"
with open(summary_json, "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=2, ensure_ascii=False)
print(f"\nSummary JSON: {summary_json}")
print("=" * 70)
print("FASE 7 FIX SELESAI")
print("=" * 70)
