# Environment — DF06 Kelompok 6

## Identitas

- **Kelompok:** 6
- **Topik:** Ketahanan Metadata EXIF terhadap Transformasi Citra
- **Operator:** Iqbal Rizky Maulana
- **Tanggal Setup:** 2026-10-01
- **Waktu Setup:** 01:29–01:40 WIB

## Spesifikasi Sistem

> Catatan: Spesifikasi hardware dicatat berdasarkan informasi sistem aktual.
> Kolom yang tidak dapat diverifikasi otomatis diberi placeholder.

| Komponen | Nilai |
|---|---|
| OS | Windows (versi tercatat dari sistem aktual) |
| Python | 3.13.7 |
| Python Path | `python` |
| pip | 25.2 |

## Tool yang Digunakan

| Tool | Versi | Path |
|---|---|---|
| Python | 3.13.7 | `python` |
| pip | 25.2 | — |
| Pillow | 12.0.0 | `site-packages (Python env)` |
| pandas | 2.3.3 | `site-packages (Python env)` |
| matplotlib | 3.10.7 | `site-packages (Python env)` |
| ExifTool | 13.59 | `exiftool\exiftool.exe` |

## Struktur Folder Kerja

```
DF06_KELOMPOK6\
├── 00_README\          ← dokumentasi, script, log
├── 01_BASELINE\        ← 30 JPEG baseline (READ-ONLY setelah hash)
├── 02_GROUND_TRUTH\    ← manifest hash, metadata JSON, expected_tags.csv
├── 03_TRANSFORMED\     ← hasil transformasi (8 subfolder)
│   ├── resize\
│   ├── recompress_q95\
│   ├── recompress_q75\
│   ├── recompress_q50\
│   ├── convert_png\
│   ├── convert_jpeg\
│   ├── stripped\
│   └── screenshot_like\
├── 04_EXIFTOOL\        ← raw JSON output ExifTool
├── 05_PARSER2\         ← raw JSON output Pillow parser
├── 06_RAW_RESULTS\     ← SHA-256 manifest, runtime logs
├── 07_ANALYSIS\        ← CSV analisis, notebook, figures\
├── 08_SCREENSHOTS\     ← screenshot representatif
└── 09_REPORT\          ← mini-paper final
```

## Catatan PATH

ExifTool telah ditambahkan ke User PATH Windows pada 2026-10-01.
Path: `exiftool`

Untuk sesi PowerShell baru, verifikasi dengan:
```powershell
exiftool -ver
```
