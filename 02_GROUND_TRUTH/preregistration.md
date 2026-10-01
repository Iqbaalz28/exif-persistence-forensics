# Pre-registration — DF06 Kelompok 6
# Ketahanan Metadata EXIF terhadap Transformasi Citra

**Tanggal penetapan:** 2026-10-01  
**Operator:** Iqbal Rizky Maulana  
**Status:** LOCKED — Tidak boleh diubah setelah eksperimen utama dimulai  

---

## 1. Research Questions (Final)

| ID  | Research Question |
|-----|-------------------|
| RQ1 | Metadata EXIF mana yang bertahan/hilang setelah resize, recompress, format conversion, dan metadata stripping? |
| RQ2 | Transformasi mana yang menghasilkan kehilangan metadata terbesar? |
| RQ3 | Apakah hasil extraction ExifTool konsisten dengan parser kedua (Pillow)? |

---

## 2. Metadata yang Diuji

9 tag EXIF wajib per gambar:

| # | Tag Name         | Expected Value (semua file)                          | Catatan                     |
|---|-----------------|------------------------------------------------------|-----------------------------|
| 1 | DateTimeOriginal | `2026:01:15 10:20:30`                               | Sama untuk semua 30 gambar  |
| 2 | Make             | `DF06-LAB`                                          | Sama untuk semua 30 gambar  |
| 3 | Model            | `SyntheticCam-1`                                    | Sama untuk semua 30 gambar  |
| 4 | Software         | `DF06-Generator v1.0`                               | Sama untuk semua 30 gambar  |
| 5 | Artist           | `Kelompok6-DF06`                                    | Sama untuk semua 30 gambar  |
| 6 | Copyright        | `Educational Synthetic Dataset DF06 2026`           | Sama untuk semua 30 gambar  |
| 7 | UserComment      | `IMG_XX controlled EXIF metadata DF06`              | Unik per file (XX = nomor)  |
| 8 | GPSLatitude      | `0 deg 0' 0.00"`                                    | Koordinat fiktif non-sensitif |
| 9 | GPSLongitude     | `0 deg 0' 0.00"`                                    | Koordinat fiktif non-sensitif |

---

## 3. Jumlah Kasus

| Kondisi             | Parameter          | Jumlah File | Case ID Prefix         |
|---------------------|--------------------|-------------|------------------------|
| Original (baseline) | —                  | 30          | DF06-ORIG-XX-R1        |
| Resize              | 50% dimension      | 30          | DF06-RSZ-XX-R1         |
| JPEG Recompress     | quality=95         | 30          | DF06-RCQ95-XX-R1       |
| JPEG Recompress     | quality=75         | 30          | DF06-RCQ75-XX-R1       |
| JPEG Recompress     | quality=50         | 30          | DF06-RCQ50-XX-R1       |
| Format Conversion   | JPEG→PNG→JPEG      | 30          | DF06-CONV-XX-R1        |
| Metadata Stripping  | ExifTool -all=     | 30          | DF06-STRIP-XX-R1       |
| Screenshot-like     | PIL re-encode      | 30          | DF06-SCR-XX-R1         |

**Total kasus:** 8 kondisi × 30 gambar = **240 gambar**  
**Total observasi:** 240 × 9 tag × 2 tool = **4,320 observasi**

---

## 4. Transformasi dan Parameter

| Transformasi     | Metode                                          | Output dir                    |
|------------------|-------------------------------------------------|-------------------------------|
| resize           | PIL `Image.resize((320,240), LANCZOS)`, quality=90 | `03_TRANSFORMED/resize/`   |
| recompress_q95   | PIL `Image.save(..., quality=95)`               | `03_TRANSFORMED/recompress_q95/` |
| recompress_q75   | PIL `Image.save(..., quality=75)`               | `03_TRANSFORMED/recompress_q75/` |
| recompress_q50   | PIL `Image.save(..., quality=50)`               | `03_TRANSFORMED/recompress_q50/` |
| convert_png      | PIL JPEG→PNG; PNG→JPEG quality=90              | `03_TRANSFORMED/convert_jpeg/` |
| stripped         | `exiftool -all= -overwrite_original`            | `03_TRANSFORMED/stripped/`   |
| screenshot_like  | PIL open → new Image canvas → paste → save JPEG | `03_TRANSFORMED/screenshot_like/` |

---

## 5. Definisi Status Tag

| Status      | Definisi                                                                                          |
|-------------|---------------------------------------------------------------------------------------------------|
| retained    | Tag hadir dan nilainya **identik** dengan expected_value di ground truth                         |
| changed     | Tag hadir tetapi nilainya **berbeda** dari expected_value                                         |
| missing     | Tool mendukung tag tersebut, tetapi tag **tidak ditemukan** pada file transformed                |
| unsupported | Tool/parser **tidak dapat membaca** tag ini (bukan karena transformasi, tetapi keterbatasan parser) |

**Catatan penting:** `unsupported` TIDAK otomatis berarti `missing`. Parser kedua (Pillow) memiliki keterbatasan pada GPS tags dan beberapa custom tags. Status ini harus dibedakan.

---

## 6. Retention Formula

```
Retention Rate (per kondisi) = jumlah tag berstatus "retained"
                               ─────────────────────────────────────────
                               jumlah tag "eligible" (retained + changed + missing)

Catatan: "unsupported" DIKELUARKAN dari denominator (bukan eligible).
         "changed" TIDAK dihitung sebagai retained.
```

Perhitungan dilakukan:
- Per transformasi (kolom `transformation`)
- Per tag (kolom `tag_name`)
- Per tool (kolom `tool`)
- Overall (semua transformasi non-original, ExifTool)

---

## 7. Parser Comparison Rule

- **ExifTool 13.59** → tool utama
- **Pillow 12.0.0** (via `img.getexif()`) → parser kedua
- Perbandingan hanya dilakukan pada **tag yang dapat dibaca kedua parser**
- Tag yang `unsupported` di Pillow dilaporkan terpisah sebagai **parser coverage gap**
- Disagreement = tag dibaca oleh ExifTool tapi hasilnya berbeda dengan Pillow (untuk tag yang sama-sama supported)

---

## 8. Jumlah Replikasi

- **Minimum 3 replikasi** untuk transformasi utama (resize, recompress_q75, stripped)
- Replikasi dilakukan dengan menjalankan ulang script transformasi
- Runtime dicatat per replikasi
- Output yang deterministik (hash identik antar replikasi) dicatat sebagai reproducibility=YES

---

## 9. Failed-Run Handling

- **Failed run TIDAK boleh dihapus**
- Failed run diberi status `failed` di kolom `status` dengan keterangan di kolom `notes`
- Reproducibility rate = jumlah run dengan output identik / total run (hanya untuk konfigurasi yang direplikasi)
- Jika error terjadi pada transformasi: file tetap dicatat, output kosong dicatat sebagai missing

---

## 10. Quality Gate Pre-registration

- [ ] 30 baseline images dengan SHA-256 ✅ (selesai Fase 4)
- [ ] 9 tag ground truth per image ✅ (expected_tags.csv 270 baris)
- [ ] minimal 5 jenis transformasi → 8 transformasi (melebihi minimum)
- [ ] GPS koordinat non-sensitif ✅ (0°0'0" N/E, Teluk Guinea)
- [ ] Pre-registration ditetapkan SEBELUM eksperimen utama dimulai ✅

---

*Pre-registration ini DIKUNCI sebelum eksperimen Fase 6 dimulai. Perubahan definisi setelah melihat hasil tidak diperbolehkan.*
