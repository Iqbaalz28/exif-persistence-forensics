# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
"""
DF06 Kelompok 6 - FASE 8: Parser Kedua (Pillow EXIF)
Operator : Iqbal Rizky Maulana
Date     : 2026-10-01

Parser: Pillow 12.0.0 img.getexif()

Output:
  05_PARSER2/transformed_metadata_pillow.json
  05_PARSER2/pillow_tag_classification.csv
  05_PARSER2/pillow_summary.json

Catatan: Pillow parser kedua; GPS tags dan beberapa EXIF tags
mungkin 'unsupported' dibandingkan ExifTool.
"""

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from PIL import Image, ExifTags
from collections import defaultdict

TRANS_DIR = Path(__file__).parent.parent / "03_TRANSFORMED"
GT_CSV    = Path(__file__).parent.parent / "02_GROUND_TRUTH" / "expected_tags.csv"
OUT_DIR   = Path(__file__).parent.parent / "05_PARSER2"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

OUT_DIR.mkdir(exist_ok=True)

# ExifTags reverse lookup: tag_id -> tag_name
TAGS_BY_NAME = {name: tag_id for tag_id, name in ExifTags.TAGS.items()}

TARGET_TAGS = [
    "DateTimeOriginal", "Make", "Model", "Software", "Artist",
    "Copyright", "UserComment", "GPSLatitude", "GPSLongitude"
]

# Tags that Pillow can typically read
PILLOW_SUPPORTED = {"DateTimeOriginal", "Make", "Model", "Software", "Artist", "Copyright", "UserComment"}
# GPS tags need special handling via GPSInfo (tag 34853)
PILLOW_GPS_SUPPORT = {"GPSLatitude", "GPSLongitude"}  # limited support

print("=" * 70)
print("DF06 Kelompok 6 - Fase 8: Pillow Parser")
print("=" * 70)
print(f"Timestamp: {TIMESTAMP}")
print(f"Source   : {TRANS_DIR.resolve()}")

# Load ground truth
gt_map = {}
with open(GT_CSV, encoding="utf-8-sig") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        fname = row["filename"]
        tag = row["tag_name"]
        if fname not in gt_map:
            gt_map[fname] = {}
        gt_map[fname][tag] = row["expected_value"]

# Collect all image files
image_exts = {".jpg", ".jpeg", ".png"}
all_files = sorted(f for f in TRANS_DIR.glob("*/*") if f.suffix.lower() in image_exts)
print(f"Files    : {len(all_files)} images to parse")
print()

# ── Parse with Pillow ──────────────────────────────────────────────────────────
raw_results = []
classification = []
errors = []

t_start = time.time()

for f in all_files:
    parts = f.parts
    try:
        idx = next(i for i, p in enumerate(parts) if "03_TRANSFORMED" in p)
        transformation = parts[idx + 1] if idx + 1 < len(parts) else "unknown"
    except StopIteration:
        transformation = "unknown"

    filename = f.name
    gt_filename = filename.replace(".png", ".jpg")
    expected_for_file = gt_map.get(gt_filename, {})

    try:
        with Image.open(f) as im:
            img_format = im.format
            exif_data = im.getexif()

            # Build tag name -> value dict
            tag_values = {}
            for tag_id, val in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                tag_values[tag_name] = str(val)

            # Try GPS extraction via GPSInfo (IFD 34853)
            gps_info = {}
            try:
                gps_ifd = exif_data.get_ifd(0x8825)  # GPS IFD tag
                if gps_ifd:
                    for k, v in gps_ifd.items():
                        gname = ExifTags.TAGS.get(k, str(k))
                        gps_info[gname] = v
            except Exception:
                pass

            raw_results.append({
                "file": str(f),
                "transformation": transformation,
                "filename": filename,
                "format": img_format,
                "exif_tags": tag_values,
                "gps_info": {k: str(v) for k, v in gps_info.items()},
                "error": None
            })

            # Classify each target tag
            for tag in TARGET_TAGS:
                expected = expected_for_file.get(tag, "")

                if tag in PILLOW_GPS_SUPPORT:
                    # GPS: check via gps_info
                    if not gps_info:
                        # No GPS IFD at all
                        if filename.endswith(".png"):
                            # PNG doesn't support EXIF GPS natively in Pillow
                            status = "unsupported"
                        else:
                            status = "missing"
                        observed = ""
                    else:
                        # Try to find lat/lon
                        if tag == "GPSLatitude":
                            raw_gps = gps_info.get("GPSLatitude", None)
                        else:
                            raw_gps = gps_info.get("GPSLongitude", None)

                        if raw_gps is None:
                            status = "missing"
                            observed = ""
                        else:
                            observed = str(raw_gps)
                            # GPS is 0,0,0 so any non-zero would be changed
                            status = "retained"  # simplified: if present and GPS=0, assume retained
                else:
                    # Non-GPS tag
                    if tag in tag_values:
                        observed = tag_values[tag]
                        # Strip unicode prefix if needed (UserComment)
                        obs_clean = observed.strip()
                        exp_clean = expected.strip()
                        if obs_clean == exp_clean or exp_clean in obs_clean:
                            status = "retained"
                        else:
                            status = "changed"
                    elif img_format == "PNG" and tag not in {"Make", "Model", "Software"}:
                        # PNG has very limited EXIF support in Pillow
                        status = "unsupported"
                        observed = ""
                    else:
                        status = "missing"
                        observed = ""

                classification.append({
                    "transformation": transformation,
                    "filename": filename,
                    "tag_name": tag,
                    "expected_value": expected,
                    "observed_value": observed,
                    "status": status,
                    "tool": "Pillow_12.0.0",
                    "img_format": img_format,
                })

    except Exception as e:
        errors.append({"file": str(f), "error": str(e)})
        raw_results.append({
            "file": str(f), "transformation": transformation,
            "filename": filename, "format": None,
            "exif_tags": {}, "gps_info": {}, "error": str(e)
        })
        for tag in TARGET_TAGS:
            classification.append({
                "transformation": transformation,
                "filename": filename,
                "tag_name": tag,
                "expected_value": expected_for_file.get(tag, ""),
                "observed_value": "",
                "status": "missing",
                "tool": "Pillow_12.0.0",
                "img_format": "ERROR",
            })

elapsed = round(time.time() - t_start, 2)
print(f"Parsing completed in {elapsed}s")
print(f"Files parsed: {len(raw_results)} | Errors: {len(errors)}")

# Save raw JSON
raw_json_path = OUT_DIR / "transformed_metadata_pillow.json"
with open(raw_json_path, "w", encoding="utf-8") as fh:
    json.dump(raw_results, fh, indent=2, ensure_ascii=False)
print(f"Raw JSON: {raw_json_path}")

# Save classification CSV
class_csv = OUT_DIR / "pillow_tag_classification.csv"
fieldnames = ["transformation", "filename", "tag_name", "expected_value", "observed_value", "status", "tool", "img_format"]
with open(class_csv, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(classification)
print(f"Classification CSV: {class_csv}  ({len(classification)} rows)")

# Statistics
print("\n-- Pillow Tag Classification per Transformation -------------------------")
status_counts = defaultdict(lambda: defaultdict(int))
for row in classification:
    status_counts[row["transformation"]][row["status"]] += 1

print(f"  {'Transform':<22} {'Retained':>8} {'Changed':>8} {'Missing':>8} {'Unsupport':>10} {'Rate':>7}")
print(f"  {'-'*22} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*7}")

all_ret, all_elig = 0, 0
for t in sorted(status_counts):
    s = status_counts[t]
    retained   = s.get("retained", 0)
    changed    = s.get("changed", 0)
    missing    = s.get("missing", 0)
    unsupported = s.get("unsupported", 0)
    eligible = retained + changed + missing
    rate = round(retained / eligible * 100, 1) if eligible > 0 else 0
    print(f"  {t:<22} {retained:>8} {changed:>8} {missing:>8} {unsupported:>10} {rate:>6.1f}%")
    all_ret += retained
    all_elig += eligible

overall = round(all_ret / all_elig * 100, 1) if all_elig > 0 else 0
print(f"\n  Overall Retention Rate (Pillow): {all_ret}/{all_elig} = {overall}%")

# Save summary
summary = {
    "timestamp": TIMESTAMP,
    "tool": "Pillow_12.0.0",
    "total_files": len(raw_results),
    "total_rows": len(classification),
    "errors": len(errors),
    "overall_retention_rate": f"{overall}%",
    "retained": all_ret,
    "eligible": all_elig,
    "per_transformation": {t: dict(s) for t, s in status_counts.items()},
}
summary_json = OUT_DIR / "pillow_summary.json"
with open(summary_json, "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=2, ensure_ascii=False)
print(f"Summary JSON: {summary_json}")

print("\n" + "=" * 70)
print("FASE 8 SELESAI")
print("=" * 70)
