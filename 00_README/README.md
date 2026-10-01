# DF06 Kelompok 6 — README

> **Eksperimen:** Ketahanan Metadata EXIF terhadap Transformasi Citra  
> **Anggota:** Iqbal Rizky Maulana · Muhammad Rangga Nur Praditha · Gherry Alviart  
> **Tanggal Eksperimen:** 2026-10-01  

---

## Struktur Folder

```
DF06_KELOMPOK6/
├── 00_README/                    # Skrip, log, dokumentasi
│   ├── tool_versions.txt         # Versi tool aktual
│   ├── environment.md            # Detail environment
│   ├── experiment_log.md         # Log per tahap eksperimen
│   ├── generate_baseline.py      # Generate 30 baseline JPEG
│   ├── generate_baseline_csv.py  # CSV log baseline generation
│   ├── write_exif_metadata.py    # Tulis 9 tag EXIF ke baseline
│   ├── generate_expected_tags.py # Buat expected_tags.csv
│   ├── phase4_sha256_chainofcustody.py  # SHA-256 + manifest
│   ├── phase6_transform.py       # 8 transformasi eksperimen
│   ├── phase7_exiftool_extract.py       # ExifTool batch extraction
│   ├── phase7b_exiftool_classify.py     # Tag classification ExifTool
│   ├── phase8_pillow_parser.py          # Pillow parser kedua
│   ├── phase9_master_csv.py             # Master tag_results.csv
│   └── phase10_13_analysis_viz.py       # Analysis + 4 figures
├── 01_BASELINE/                  # 30 baseline JPEG (READ-ONLY)
│   └── IMG_01.jpg ... IMG_30.jpg
├── 02_GROUND_TRUTH/              # Ground truth dan manifest
│   ├── baseline_sha256.txt       # SHA-256 semua baseline
│   ├── baseline_metadata.json    # Raw ExifTool output baseline
│   ├── expected_tags.csv         # 270 baris ground truth
│   ├── evidence_manifest.csv     # Evidence manifest (E001-E030)
│   ├── evidence_manifest.json    # JSON version
│   ├── chain_of_custody.csv      # Chain of custody log
│   └── preregistration.md        # Pre-registration (LOCKED)
├── 03_TRANSFORMED/               # Output transformasi
│   ├── resize/                   # 30 file (50%, 320x240)
│   ├── recompress_q95/           # 30 file (JPEG quality=95)
│   ├── recompress_q75/           # 30 file (JPEG quality=75)
│   ├── recompress_q50/           # 30 file (JPEG quality=50)
│   ├── convert_png/              # 30 file (JPEG→PNG)
│   ├── convert_jpeg/             # 30 file (PNG→JPEG round-trip)
│   ├── stripped/                 # 30 file (ExifTool -all=)
│   └── screenshot_like/          # 30 file (PIL new canvas)
├── 04_EXIFTOOL/                  # Raw ExifTool output
│   ├── transformed_metadata_exiftool.json
│   ├── exiftool_extraction_log.csv
│   ├── exiftool_tag_classification.csv  (2160 rows)
│   └── exiftool_summary.json
├── 05_PARSER2/                   # Pillow parser output
│   ├── transformed_metadata_pillow.json
│   ├── pillow_tag_classification.csv  (2160 rows)
│   └── pillow_summary.json
├── 06_RAW_RESULTS/               # Run logs dan SHA-256
│   ├── baseline_generate_log.csv
│   ├── exif_write_log.csv
│   ├── exif_write_reference.json
│   ├── transform_run_log.csv
│   └── transformed_sha256.csv
├── 07_ANALYSIS/                  # Analisis dan visualisasi
│   ├── tag_results.csv           # Master CSV (4320 rows)
│   ├── retention_summary.csv     # Retention rate per transform/tag
│   ├── file_hash_size.csv        # File size + SHA-256 (270 rows)
│   ├── replication_log.csv       # Replikasi 3x (9 rows)
│   └── figures/
│       ├── fig1_retention_per_transform.png
│       ├── fig2_heatmap_transform_tag.png
│       ├── fig3_parser_agreement.png
│       └── fig4_filesize_distribution.png
├── 08_SCREENSHOTS/
└── 09_REPORT/
    └── mini_paper_DF06_Kelompok6.md # Laporan Utama (Mini-paper)
```

---

## Laporan Utama (Mini-Paper)
Laporan akhir yang memenuhi persyaratan Modul 6 (scientific mini-paper 6-10 halaman) dapat diakses di:
[`09_REPORT/mini_paper_DF06_Kelompok6.md`](09_REPORT/mini_paper_DF06_Kelompok6.md)

---

## Quick Replication Guide

Untuk mereplikasi satu eksperimen representatif dari awal:

```powershell
# Pastikan berada di direktori DF06_KELOMPOK6/
# cd path\to\DF06_KELOMPOK6

# Step 1: Generate baseline
python 00_README\generate_baseline.py

# Step 2: Tulis EXIF metadata
python 00_README\write_exif_metadata.py

# Step 3: Hitung SHA-256 baseline
python 00_README\phase4_sha256_chainofcustody.py

# Step 4: Jalankan semua transformasi
python 00_README\phase6_transform.py

# Step 5: Ekstrak metadata (ExifTool)
python 00_README\phase7_exiftool_extract.py
python 00_README\phase7b_exiftool_classify.py

# Step 6: Parser kedua (Pillow)
python 00_README\phase8_pillow_parser.py

# Step 7: Build master CSV
python 00_README\phase9_master_csv.py

# Step 8: Analysis + figures
python 00_README\phase10_13_analysis_viz.py
```

**Expected result:** Overall retention rate = 0.0% (Pillow Image.save() tidak menyalin EXIF).

---

## Key Finding

> Seluruh tag EXIF hilang pada semua 8 kondisi transformasi ketika menggunakan Python Pillow 12.0.0 dengan `Image.save()` default (tanpa parameter `exif=`). Hasil ini deterministik dan terreplikasi (3 replikasi, hash identik).

---

## Data Provenance

Semua angka dalam mini-paper dapat ditelusuri ke:

| Angka | Sumber |
|-------|--------|
| 0% retention rate | `07_ANALYSIS/tag_results.csv`, kolom `status` |
| 240 transformed files | `06_RAW_RESULTS/transform_run_log.csv` |
| 3 replikasi deterministik | `07_ANALYSIS/replication_log.csv` |
| File size statistics | `07_ANALYSIS/file_hash_size.csv` |
| SHA-256 baseline | `02_GROUND_TRUTH/baseline_sha256.txt` |

---

## Ethical Statement

- Dataset sintetis; tidak ada informasi pribadi, koordinat rumah, atau identitas nyata.
- GPS koordinat: 0°0'0"N 0°0'0"E (Teluk Guinea — non-sensitif).
- Tidak ada file malware, data breach, atau data orang lain.
