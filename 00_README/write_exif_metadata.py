"""
DF06 Kelompok 6 — Write Controlled EXIF Metadata to 30 Baseline Images
Operator : Iqbal Rizky Maulana
Date     : 2026-10-01
Purpose  : Menulis 9 tag EXIF terkontrol ke setiap baseline JPEG
           menggunakan ExifTool via subprocess.

Tag yang ditulis:
  DateTimeOriginal, Make, Model, Software, Artist, Copyright,
  UserComment, GPSLatitude, GPSLongitude

GPS: 0 deg 0 min 0 sec N / 0 deg 0 min 0 sec E
     (Teluk Guinea — koordinat publik non-sensitif, tidak terkait lokasi pribadi)

PENTING: Script ini menggunakan -overwrite_original.
         Setelah selesai, baseline TIDAK BOLEH dimodifikasi lagi.
"""

import subprocess
import time
from pathlib import Path

# ── Konfigurasi ───────────────────────────────────────────────────────────────
EXIFTOOL = r"E:\UNIVERSITAS PENDIDIKAN INDONESIA\APP\exiftool\exiftool.exe"
BASELINE_DIR = Path(__file__).parent.parent / "01_BASELINE"

# Metadata terkontrol — nilai sama untuk semua gambar, kecuali UserComment
METADATA_COMMON = {
    "DateTimeOriginal": "2026:01:15 10:20:30",
    "Make":             "DF06-LAB",
    "Model":            "SyntheticCam-1",
    "Software":         "DF06-Generator v1.0",
    "Artist":           "Kelompok6-DF06",
    "Copyright":        "Educational Synthetic Dataset DF06 2026",
    "GPSLatitude":      "0 0 0",
    "GPSLatitudeRef":   "N",
    "GPSLongitude":     "0 0 0",
    "GPSLongitudeRef":  "E",
}
# UserComment: unik per file (menyertakan nama file)
# Format: "<stem> controlled EXIF metadata DF06"

# ── Jalankan ──────────────────────────────────────────────────────────────────
print("=" * 65)
print("DF06 Kelompok 6 — EXIF Metadata Writer")
print("=" * 65)
print(f"ExifTool : {EXIFTOOL}")
print(f"Target   : {BASELINE_DIR.resolve()}")
print(f"Tags     : DateTimeOriginal, Make, Model, Software, Artist,")
print(f"           Copyright, UserComment, GPSLatitude, GPSLongitude")
print(f"GPS      : 0 deg 0' 0\" N / 0 deg 0' 0\" E (Teluk Guinea, fiktif)")
print("-" * 65)

files = sorted(BASELINE_DIR.glob("*.jpg"))
if not files:
    print("[ERROR] Tidak ada file .jpg di 01_BASELINE")
    raise SystemExit(1)

success_count = 0
fail_count = 0
results = []

start_total = time.time()

for f in files:
    stem = f.stem  # e.g. "IMG_01"
    user_comment = f"{stem} controlled EXIF metadata DF06"

    cmd = [
        EXIFTOOL,
        "-overwrite_original",
        f"-DateTimeOriginal={METADATA_COMMON['DateTimeOriginal']}",
        f"-Make={METADATA_COMMON['Make']}",
        f"-Model={METADATA_COMMON['Model']}",
        f"-Software={METADATA_COMMON['Software']}",
        f"-Artist={METADATA_COMMON['Artist']}",
        f"-Copyright={METADATA_COMMON['Copyright']}",
        f"-UserComment={user_comment}",
        f"-GPSLatitude={METADATA_COMMON['GPSLatitude']}",
        f"-GPSLatitudeRef={METADATA_COMMON['GPSLatitudeRef']}",
        f"-GPSLongitude={METADATA_COMMON['GPSLongitude']}",
        f"-GPSLongitudeRef={METADATA_COMMON['GPSLongitudeRef']}",
        str(f),
    ]

    t0 = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0

    ok = result.returncode == 0
    status = "OK" if ok else "FAIL"
    if ok:
        success_count += 1
    else:
        fail_count += 1

    results.append({
        "file": f.name,
        "status": status,
        "runtime_sec": round(elapsed, 3),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    })

    stdout_short = result.stdout.strip().replace("\n", " ")[:50]
    print(f"  [{status}] {f.name:>12}  {elapsed:.3f}s  {stdout_short}")

elapsed_total = time.time() - start_total

print("-" * 65)
print(f"Results  : {success_count} OK / {fail_count} FAIL  (total {elapsed_total:.2f}s)")

if fail_count > 0:
    print("[WARN] Ada file yang gagal — lihat detail di bawah:")
    for r in results:
        if r["status"] == "FAIL":
            print(f"  {r['file']}: {r['stderr']}")

print("=" * 65)

# ── Simpan run log ─────────────────────────────────────────────────────────────
import csv, json
from datetime import datetime

log_dir = Path(__file__).parent.parent / "06_RAW_RESULTS"
log_dir.mkdir(exist_ok=True)

# CSV log
csv_path = log_dir / "exif_write_log.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["file", "status", "runtime_sec", "stdout", "stderr"])
    w.writeheader()
    w.writerows(results)
print(f"\nRun log saved : {csv_path}")

# JSON metadata reference (nilai yang ditulis)
meta_ref = {f["file"]: {**METADATA_COMMON, "UserComment": f"{Path(f['file']).stem} controlled EXIF metadata DF06"} for f in results}
json_path = log_dir / "exif_write_reference.json"
with open(json_path, "w", encoding="utf-8") as fh:
    json.dump(meta_ref, fh, indent=2, ensure_ascii=False)
print(f"Metadata ref  : {json_path}")
print()
print("NEXT: Verifikasi 3 file sampel dengan:")
print(f'  & "{EXIFTOOL}" -G1 -a -s 01_BASELINE\\IMG_01.jpg')
print(f'  & "{EXIFTOOL}" -G1 -a -s 01_BASELINE\\IMG_15.jpg')
print(f'  & "{EXIFTOOL}" -G1 -a -s 01_BASELINE\\IMG_30.jpg')
