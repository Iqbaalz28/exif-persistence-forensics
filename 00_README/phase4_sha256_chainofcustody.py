"""
DF06 Kelompok 6 — FASE 4: SHA-256 Hash + Chain of Custody Manifest
Operator : Iqbal Rizky Maulana
Date     : 2026-10-01
Purpose  : Menghitung SHA-256 semua 30 baseline images dan membuat
           chain-of-custody manifest (CSV + JSON).

CATATAN: Setelah fase ini selesai, 01_BASELINE/ TIDAK BOLEH dimodifikasi lagi.
"""

import hashlib
import csv
import json
from datetime import datetime
from pathlib import Path

# ── Konfigurasi ───────────────────────────────────────────────────────────────
BASELINE_DIR  = Path(__file__).parent.parent / "01_BASELINE"
GROUND_TRUTH  = Path(__file__).parent.parent / "02_GROUND_TRUTH"
OPERATOR      = "Iqbal Rizky Maulana"
TIMESTAMP     = datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

print("=" * 70)
print("DF06 Kelompok 6 — SHA-256 Baseline Hash + Chain of Custody")
print("=" * 70)
print(f"Timestamp  : {TIMESTAMP}")
print(f"Operator   : {OPERATOR}")
print(f"Source     : {BASELINE_DIR.resolve()}")
print("-" * 70)

files = sorted(BASELINE_DIR.glob("*.jpg"))
if not files:
    print("[ERROR] Tidak ada file .jpg di 01_BASELINE/")
    raise SystemExit(1)

# ── Hitung SHA-256 ─────────────────────────────────────────────────────────────
manifest_rows = []
coc_rows = []

for i, f in enumerate(files, start=1):
    evidence_id = f"E{i:03d}"
    sha = sha256_file(f)
    size = f.stat().st_size

    manifest_rows.append({
        "evidence_id":   evidence_id,
        "filename":      f.name,
        "size_bytes":    size,
        "sha256":        sha,
        "source":        "synthetic / PIL generated",
        "created_at":    TIMESTAMP,
        "status":        "baseline",
        "operator":      OPERATOR,
        "notes":         "EXIF metadata written; DO NOT MODIFY after this point",
    })

    coc_rows.append({
        "timestamp":    TIMESTAMP,
        "evidence_id":  evidence_id,
        "action":       "sha256_hash_baseline",
        "from":         str(BASELINE_DIR.resolve()),
        "to":           str(GROUND_TRUTH.resolve()),
        "hash":         sha,
        "verification": "computed",
        "operator":     OPERATOR,
        "notes":        f"baseline locked; file size {size} bytes",
    })

    print(f"  {evidence_id}  {f.name}  {size:>8} bytes  {sha[:16]}...")

print("-" * 70)
print(f"Total: {len(files)} files hashed")

# ── Simpan manifest ke 02_GROUND_TRUTH ────────────────────────────────────────
GROUND_TRUTH.mkdir(exist_ok=True)

# SHA-256 plain text (untuk audit cepat)
sha_txt = GROUND_TRUTH / "baseline_sha256.txt"
with open(sha_txt, "w", encoding="utf-8") as f:
    f.write(f"# DF06 Kelompok 6 — Baseline SHA-256 Manifest\n")
    f.write(f"# Generated: {TIMESTAMP}\n")
    f.write(f"# Operator : {OPERATOR}\n\n")
    for row in manifest_rows:
        f.write(f"{row['sha256']}  {row['filename']}\n")
print(f"\nSHA-256 manifest : {sha_txt}")

# Evidence manifest CSV
manifest_csv = GROUND_TRUTH / "evidence_manifest.csv"
fieldnames_m = ["evidence_id","filename","size_bytes","sha256","source","created_at","status","operator","notes"]
with open(manifest_csv, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames_m)
    w.writeheader()
    w.writerows(manifest_rows)
print(f"Evidence manifest: {manifest_csv}")

# Chain-of-custody CSV
coc_csv = GROUND_TRUTH / "chain_of_custody.csv"
fieldnames_c = ["timestamp","evidence_id","action","from","to","hash","verification","operator","notes"]
with open(coc_csv, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames_c)
    w.writeheader()
    w.writerows(coc_rows)
print(f"Chain of custody : {coc_csv}")

# JSON manifest (machine-readable)
manifest_json = GROUND_TRUTH / "evidence_manifest.json"
with open(manifest_json, "w", encoding="utf-8") as fh:
    json.dump(manifest_rows, fh, indent=2, ensure_ascii=False)
print(f"JSON manifest    : {manifest_json}")

print()
print("=" * 70)
print("FASE 4 SELESAI — Baseline LOCKED. Jangan ubah 01_BASELINE/ lagi.")
print("=" * 70)
