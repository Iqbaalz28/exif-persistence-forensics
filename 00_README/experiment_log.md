# Experiment Log — DF06 Kelompok 6

> Log ini diperbarui setiap kali sebuah tahap eksperimen selesai.
> Format: satu entry per tahap. Jangan hapus entry yang mencatat error/failed run.

---

## Experiment Log — Step 00: Orientasi dan Audit Instruksi

- **Date:** 2026-10-01
- **Time:** 01:22–01:28 WIB
- **Operator:** Iqbal Rizky Maulana
- **Case:** DF06-SETUP-00
- **Objective:** Membaca dan memahami instruksi tugas; menetapkan experimental matrix, struktur folder, roadmap, dan checklist.
- **Command:** — (tidak ada eksekusi eksperimen)
- **Input:** Dokumen panduan tugas Kelompok 6 (Modul 6 Digital Forensics Research Assignment)
- **Output:** Fase 0 orientation document
- **SHA-256:** —
- **Runtime:** —
- **Result:** Experimental matrix, checklist, roadmap, dan struktur folder ditetapkan.
- **Error:** Tidak ada.
- **Validation:** Semua requirement dari modul teridentifikasi.
- **Status:** PASS

---

## Experiment Log — Step 01: Persiapan Environment

- **Date:** 2026-10-01
- **Time:** 01:28–01:40 WIB
- **Operator:** Iqbal Rizky Maulana
- **Case:** DF06-SETUP-01
- **Objective:** Membuat struktur folder, memverifikasi tool, mencatat versi.
- **Command:**
  ```
  python --version
  pip show Pillow pandas matplotlib
  exiftool -ver
  New-Item -ItemType Directory (semua subfolder)
  ```
- **Input:** —
- **Output:**
  - Folder `DF06_KELOMPOK6\` dengan 17 subfolder terbuat
  - `00_README\tool_versions.txt` terbuat
  - `00_README\environment.md` terbuat
  - `00_README\experiment_log.md` terbuat
- **SHA-256:** —
- **Runtime:** ~12 menit (termasuk instalasi ExifTool manual oleh operator)
- **Result:**
  - Python 3.13.7 ✅
  - Pillow 12.0.0 ✅
  - pandas 2.3.3 ✅
  - matplotlib 3.10.7 ✅
  - ExifTool 13.59 ✅
  - Semua folder terbuat ✅
- **Error:** ExifTool tidak langsung dikenali di PATH sebelum User PATH diperbarui.
- **Validation:** `exiftool -ver` mengembalikan `13.59` setelah PATH diperbarui.
- **Status:** PASS

---


---

## Experiment Log — Step 02: Generate 30 Baseline Images

- **Date:** 2026-10-01
- **Time:** 01:47–01:50 WIB
- **Operator:** Muhammad Rangga Nur Praditha
- **Case:** DF06-BASELINE-01
- **Objective:** Membuat 30 JPEG sintetis sebagai baseline dataset eksperimen.
- **Command:** `python 00_README/generate_baseline.py`
- **Input:** Script `generate_baseline.py` (seed deterministik SEED_BASE=6000)
- **Output:**
  - 30 file JPEG di `01_BASELINE\` (IMG_01.jpg s/d IMG_30.jpg)
  - Log CSV di `06_RAW_RESULTS\baseline_generate_log.csv`
- **SHA-256:** Dihitung per file — lihat `06_RAW_RESULTS\baseline_generate_log.csv`
- **Runtime:** ~26 detik
- **Result:**
  - 30 file terbuat ✓
  - Total size: 1,060,737 bytes
  - Ukuran per file: 30,766 – 40,576 bytes
  - Resolusi: 640×480 px
  - Format: JPEG quality=90
- **Error:** UnicodeEncodeError pada karakter emoji di terminal summary (tidak mempengaruhi file output). Script diperbaiki.
- **Validation:** `Get-ChildItem 01_BASELINE\*.jpg | Measure-Object` → Count: 30 ✓
- **Status:** PASS

---

## Experiment Log — Step 03: Penulisan Metadata EXIF + Ground Truth

- **Date:** 2026-10-01
- **Time:** 01:57–01:59 WIB
- **Operator:** Iqbal Rizky Maulana
- **Case:** DF06-EXIF-01
- **Objective:** Menulis 9 tag EXIF terkontrol ke 30 baseline; ekspor ground truth ke JSON dan CSV.
- **Command:**
  ```
  python 00_README/write_exif_metadata.py
  exiftool -json -G1 -a -s 01_BASELINE/*.jpg > 02_GROUND_TRUTH/baseline_metadata.json
  python 00_README/generate_expected_tags.py
  ```
- **Input:** 30 JPEG di `01_BASELINE\` (sebelumnya tanpa metadata)
- **Output:**
  - 30 JPEG diperbarui dengan EXIF (in-place, `-overwrite_original`)
  - `06_RAW_RESULTS\exif_write_log.csv` — run log per file
  - `06_RAW_RESULTS\exif_write_reference.json` — referensi nilai yang ditulis
  - `02_GROUND_TRUTH\baseline_metadata.json` — raw ExifTool output semua baseline
  - `02_GROUND_TRUTH\expected_tags.csv` — 270 baris ground truth (30x9 tag)
- **Tags ditulis:** DateTimeOriginal, Make, Model, Software, Artist, Copyright, UserComment, GPSLatitude, GPSLongitude
- **GPS:** 0 deg 0' 0" N / 0 deg 0' 0" E (Teluk Guinea, koordinat fiktif non-sensitif)
- **Runtime:** 21.11 detik (30 file via ExifTool subprocess)
- **Result:**
  - 30 OK / 0 FAIL ✓
  - Verifikasi manual 3 sampel (IMG_01, IMG_15, IMG_30): 9 tag hadir dan benar ✓
  - expected_tags.csv: 270 baris, 270 match YES, 0 REVIEW ✓
- **Error:** JSONDecodeError BOM saat baca JSON — diperbaiki dengan encoding utf-8-sig. Tidak mempengaruhi data.
- **Validation:** expected_tags.csv 270/270 match ✓
- **Status:** PASS
- **Catatan:** Baseline di `01_BASELINE/` tidak dimodifikasi lagi setelah tahap ini. SHA-256 resmi dihitung pada Step 04.

---

## Experiment Log — Step 04: SHA-256 + Chain of Custody

- **Date:** 2026-10-01
- **Time:** 10:47–10:48 WIB
- **Operator:** Iqbal Rizky Maulana
- **Case:** DF06-HASH-01
- **Objective:** Menghitung SHA-256 semua 30 baseline dan membuat evidence manifest + chain-of-custody.
- **Command:** `python 00_README/phase4_sha256_chainofcustody.py`
- **Input:** 30 JPEG di `01_BASELINE/`
- **Output:**
  - `02_GROUND_TRUTH/baseline_sha256.txt` — plain text SHA-256
  - `02_GROUND_TRUTH/evidence_manifest.csv` — 30 rows (E001-E030)
  - `02_GROUND_TRUTH/chain_of_custody.csv` — CoC log
  - `02_GROUND_TRUTH/evidence_manifest.json` — machine-readable
- **SHA-256:** E001=91864e0d..., E002=446bf7ed..., ... (lihat baseline_sha256.txt)
- **Runtime:** ~1 menit
- **Result:** 30 files hashed ✓ | evidence manifest created ✓
- **Error:** Tidak ada.
- **Validation:** All 30 evidence IDs assigned, manifest complete.
- **Status:** PASS
- **Catatan:** Baseline dikunci — tidak ada modifikasi lagi setelah tahap ini.

---

## Experiment Log — Step 05: Pre-registration

- **Date:** 2026-10-01
- **Time:** 10:48–10:49 WIB
- **Operator:** Gherry Alviart
- **Case:** DF06-PREREG-01
- **Objective:** Menetapkan definisi retained/changed/missing/unsupported, formula retention, dan aturan parser sebelum eksperimen utama.
- **Command:** — (dokumen dibuat secara manual)
- **Output:** `02_GROUND_TRUTH/preregistration.md`
- **SHA-256:** —
- **Runtime:** —
- **Result:** Pre-registration dikunci ✓ | 8 kondisi, 9 tag, 3 replikasi minimal ✓
- **Error:** Tidak ada.
- **Status:** PASS

---

## Experiment Log — Step 06: Eksperimen Transformasi (7 Kondisi)

- **Date:** 2026-10-01
- **Time:** 10:49–10:51 WIB
- **Operator:** Iqbal Rizky Maulana
- **Case:** DF06-TRANS-01
- **Objective:** Menjalankan 7 transformasi pada 30 baseline image.
- **Command:** `python 00_README/phase6_transform.py`
- **Input:** 30 JPEG di `01_BASELINE/`
- **Output:** 210 file di `03_TRANSFORMED/` (7 kondisi × 30 file = 210 JPEG/PNG)
  - Plus 30 file `convert_png/*.png` = total 240 output files
- **SHA-256:** lihat `06_RAW_RESULTS/transformed_sha256.csv`
- **Runtime:** ~17s total (terlama: stripped 15.13s karena ExifTool per-file)
- **Result:**
  - resize: 30 OK / 0 FAIL ✓
  - recompress_q95: 30 OK / 0 FAIL ✓
  - recompress_q75: 30 OK / 0 FAIL ✓
  - recompress_q50: 30 OK / 0 FAIL ✓
  - convert_png: 30 OK / 0 FAIL ✓
  - convert_jpeg: 30 OK / 0 FAIL ✓
  - stripped: 30 OK / 0 FAIL ✓
  - screenshot_like: 30 OK / 0 FAIL ✓
- **Error:** UnicodeEncodeError pada print awal — diperbaiki dengan sys.stdout.reconfigure.
- **TEMUAN KRITIS:** Pillow Image.save() tidak menyalin EXIF secara default.
  Semua kondisi PIL menghasilkan file tanpa tag EXIF.
- **Validation:** 240 output files terbuat ✓
- **Status:** PASS

---

## Experiment Log — Step 07: ExifTool Extraction

- **Date:** 2026-10-01
- **Time:** 10:51–10:56 WIB
- **Operator:** Muhammad Rangga Nur Praditha
- **Case:** DF06-EXTRACT-01
- **Objective:** Ekstrak metadata semua 240 transformed files menggunakan ExifTool.
- **Command:** `python 00_README/phase7_exiftool_extract.py` + `phase7b_exiftool_classify.py`
- **Input:** 240 files di `03_TRANSFORMED/`
- **Output:**
  - `04_EXIFTOOL/transformed_metadata_exiftool.json` — raw JSON (240 records)
  - `04_EXIFTOOL/exiftool_tag_classification.csv` — 2160 rows (240 files × 9 tags)
  - `04_EXIFTOOL/exiftool_summary.json`
- **Runtime:** 1.59s (batch ExifTool call)
- **Result:** 240 records parsed ✓
  - Semua 8 transformasi: 0 tag found (0% retention)
  - Konfirmasi: Pillow tidak menyalin EXIF → semua tag missing
- **Validation:** Manual check `exiftool recompress_q95/IMG_01.jpg` → no EXIF tags ✓
- **Status:** PASS (hasil valid sebagai temuan penelitian)

---

## Experiment Log — Step 08: Pillow Parser (Parser Kedua)

- **Date:** 2026-10-01
- **Time:** 10:57 WIB
- **Operator:** Iqbal Rizky Maulana
- **Case:** DF06-PARSER2-01
- **Objective:** Ekstrak metadata menggunakan Pillow sebagai parser kedua.
- **Command:** `python 00_README/phase8_pillow_parser.py`
- **Output:**
  - `05_PARSER2/transformed_metadata_pillow.json`
  - `05_PARSER2/pillow_tag_classification.csv` — 2160 rows
- **Runtime:** 0.22s
- **Result:** 240 files parsed, 0 errors ✓
  - Retention 0% (konfirmasi ExifTool)
  - PNG files: 180 baris unsupported (Pillow GPS/custom tag limitation)
- **Status:** PASS

---

## Experiment Log — Step 09: Master CSV (tag_results.csv)

- **Date:** 2026-10-01
- **Time:** 10:57–10:58 WIB
- **Case:** DF06-ANALYSIS-01
- **Output:** `07_ANALYSIS/tag_results.csv` — 4320 rows (2 parsers × 240 files × 9 tags)
- **Status:** PASS

---

## Experiment Log — Step 10-13: Analysis + Replikasi + Visualisasi

- **Date:** 2026-10-01
- **Time:** 10:59–11:00 WIB
- **Case:** DF06-ANALYSIS-02
- **Output:**
  - `07_ANALYSIS/retention_summary.csv`
  - `07_ANALYSIS/file_hash_size.csv` — 270 rows
  - `07_ANALYSIS/replication_log.csv` — 9 rows (3 kondisi × 3 replikasi)
  - `07_ANALYSIS/figures/fig1_retention_per_transform.png`
  - `07_ANALYSIS/figures/fig2_heatmap_transform_tag.png`
  - `07_ANALYSIS/figures/fig3_parser_agreement.png`
  - `07_ANALYSIS/figures/fig4_filesize_distribution.png`
- **Replikasi:** resize/recompress_q75/stripped → 3 runs → consistent=YES (deterministik)
- **Retention Rate (ExifTool):** 0.0% (0/2160 eligible)
- **Status:** PASS
