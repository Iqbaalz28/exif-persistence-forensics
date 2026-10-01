"""
DF06 Kelompok 6 — Generate expected_tags.csv
Membuat ground truth CSV dari baseline_metadata.json.
30 images x 9 tags = 270 baris minimum.
"""
import json, csv
from pathlib import Path

BASE_DIR  = Path(__file__).parent.parent
json_path = BASE_DIR / "02_GROUND_TRUTH" / "baseline_metadata.json"
csv_path  = BASE_DIR / "02_GROUND_TRUTH" / "expected_tags.csv"

# 9 tag wajib yang diuji — mapping nama ExifTool → nama kolom ground truth
# Catatan: GPS ditampilkan dalam dua bentuk oleh ExifTool (raw & Composite).
# Kita pakai nilai dari [GPS] group (raw) sebagai expected.
TAGS_OF_INTEREST = {
    "DateTimeOriginal": "DateTimeOriginal",
    "Make":             "Make",
    "Model":            "Model",
    "Software":         "Software",
    "Artist":           "Artist",
    "Copyright":        "Copyright",
    "UserComment":      "UserComment",
    "GPSLatitude":      "GPSLatitude",
    "GPSLongitude":     "GPSLongitude",
}

# Nilai expected (deterministik — sesuai yang kita tulis di write_exif_metadata.py)
EXPECTED_COMMON = {
    "DateTimeOriginal": "2026:01:15 10:20:30",
    "Make":             "DF06-LAB",
    "Model":            "SyntheticCam-1",
    "Software":         "DF06-Generator v1.0",
    "Artist":           "Kelompok6-DF06",
    "Copyright":        "Educational Synthetic Dataset DF06 2026",
    "GPSLatitude":      "0 deg 0' 0.00\"",
    "GPSLongitude":     "0 deg 0' 0.00\"",
}

# Load JSON hasil export ExifTool
with open(json_path, encoding="utf-8-sig") as f:
    data = json.load(f)

rows = []
for entry in data:
    # ExifTool JSON: SourceFile = path file
    src = Path(entry.get("SourceFile", "")).name
    stem = Path(src).stem  # e.g. "IMG_01"

    for tag_name in TAGS_OF_INTEREST:
        # Cari nilai di JSON (bisa ada di berbagai group, ambil yg pertama)
        observed = None
        for key, val in entry.items():
            # key format: "Group:TagName" atau "TagName"
            key_tag = key.split(":")[-1] if ":" in key else key
            if key_tag == tag_name:
                observed = str(val)
                break

        # Tentukan expected value
        if tag_name == "UserComment":
            expected_val = f"{stem} controlled EXIF metadata DF06"
        else:
            expected_val = EXPECTED_COMMON.get(tag_name, "")

        rows.append({
            "filename":       src,
            "tag_name":       tag_name,
            "expected_value": expected_val,
            "observed_value": observed if observed else "[NOT FOUND]",
            "match":          "YES" if observed and observed.strip() == expected_val.strip() else "REVIEW",
            "source_stage":   "baseline_after_exif_write",
            "notes":          "",
        })

# Tulis CSV
fieldnames = ["filename", "tag_name", "expected_value", "observed_value", "match", "source_stage", "notes"]
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

total = len(rows)
matched = sum(1 for r in rows if r["match"] == "YES")
review  = sum(1 for r in rows if r["match"] == "REVIEW")

print(f"expected_tags.csv saved: {csv_path}")
print(f"Total rows   : {total}  (expected >= 270)")
print(f"Match = YES  : {matched}")
print(f"Match = REVIEW: {review}")
print()
if review > 0:
    print("Rows needing review:")
    for r in rows:
        if r["match"] == "REVIEW":
            print(f"  {r['filename']} | {r['tag_name']}")
            print(f"    expected : {r['expected_value']}")
            print(f"    observed : {r['observed_value']}")
else:
    print("[OK] All expected values match observed values.")
