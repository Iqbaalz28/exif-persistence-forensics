# EXIF Persistence Forensics 🔍📸

> A Controlled Experimental Study Evaluating EXIF Metadata Persistence Across Common Image Transformations Using Python Pillow.

[![Digital Forensics](https://img.shields.io/badge/Subject-Digital%20Forensics-blue.svg)]()
[![Python Pillow](https://img.shields.io/badge/Library-Pillow%2012.0.0-green.svg)]()
[![ExifTool](https://img.shields.io/badge/Tool-ExifTool%2013.59-orange.svg)]()

Repository ini berisi keseluruhan artefak dan laporan dari penelitian forensik digital mengenai persistensi metadata EXIF di bawah pemrosesan gambar rutin. Proyek ini dikembangkan sebagai bagian dari **Modul 06 Digital Forensics, Universitas Pendidikan Indonesia**.

## 📖 Ringkasan Penelitian

Metadata EXIF pada gambar sering diandalkan dalam investigasi forensik untuk mencari informasi *timestamp*, geolokasi, dan atribusi perangkat. Namun, gambar sering diproses ulang (kompresi, *resize*, konversi format) baik oleh platform online, aplikasi pesan, maupun alat pihak ketiga. Penelitian ini menguji secara saintifik ketahanan metadata EXIF tersebut ketika diproses menggunakan library pemrosesan standar **Python Pillow (versi 12.0.0)**. 

Menggunakan pendekatan *ground-truth* dengan **30 gambar dataset sintetis** deterministik, penelitian ini mengeksekusi 8 transformasi umum dan membandingkan kondisinya sebelum dan sesudah.

**Temuan Utama:**
- Transformasi yang menggunakan API default `Image.save()` pada Pillow (termasuk *resize*, perubahan JPEG quality 95/75/50, hingga konversi ke PNG) menghasilkan **0.0% retention rate** dari metadata EXIF aslinya.
- Hasil ini menunjukkan bahwa *absence of EXIF metadata* tidak dapat secara otomatis diinterpretasikan sebagai manipulasi atau upaya pengaburan yang disengaja (deliberate stripping). Pemrosesan melalui pipeline default tertentu akan menghasilkan efek hilangnya metadata secara utuh.

**📄 Selengkapnya dapat dibaca pada Paper Akademik kami:** 
👉 **[Mini-Paper: EXIF Metadata Persistence](09_REPORT/mini_paper_DF06_Kelompok6.md)**

---

## 📂 Struktur Repositori Utama

Penelitian ini dirancang secara deterministik sehingga hasil eksperimen sepenuhnya dapat direplikasi dan diaudit.

| Folder / Direktori | Deskripsi |
|---|---|
| [`00_README/`](00_README/) | Repositori skrip sumber (Python) lengkap untuk menjalankan *pipeline* dari pembuatan dataset hingga *charting*. |
| [`01_BASELINE/`](01_BASELINE/) | 30 dataset JPEG sintetis awal berisikan EXIF data (Read-Only). |
| [`02_GROUND_TRUTH/`](02_GROUND_TRUTH/) | Dokumen *Chain of Custody*, spesifikasi tag *expected*, dan *SHA-256 file baseline*. |
| [`03_TRANSFORMED/`](03_TRANSFORMED/) | Artefak gambar pasca-transformasi (mencakup 8 kondisi berbeda). |
| [`04_EXIFTOOL/`](04_EXIFTOOL/) | Raw ekstraksi log JSON dan klasifikasi status metadata (*Missing/Retained/Changed*) oleh ExifTool. |
| [`07_ANALYSIS/`](07_ANALYSIS/) | Master log agregasi, hasil uji determinisme (replikasi), hingga figur diagram visual (*png*). |
| [`09_REPORT/`](09_REPORT/) | Mini-paper komprehensif dalam format Markdown beserta laporan audit awal. |
| [`10_REFERENCES/`](10_REFERENCES/) | PDF literatur jurnal/sumber rujukan yang dianalisis dalam Mini Paper. |

---

## 🛠️ Reproducibility (Instruksi Replikasi Eksperimen)

Untuk menguji ulang data dan klaim penelitian, Anda dapat mengeksekusi kembali seluruh eksperimen. Diasumsikan environment Anda menggunakan instalasi: `Python 3.13.x`, `Pillow 12.0.0`, `pandas`, `matplotlib`, dan **`ExifTool 13.59`** yang dapat diakses di system `PATH`.

**Pipeline Eksekusi Replikasi:**
```powershell
# Jalankan command ini dari root direktori (DF06_KELOMPOK6)
python 00_README/phase6_transform.py          # Eksekusi 8 transformasi terhadap 30 gambar baseline
python 00_README/phase7_exiftool_extract.py   # Ekstraksi massal metadata EXIF ke JSON
python 00_README/phase7b_exiftool_classify.py # Penilaian retention rate setiap tag
python 00_README/phase8_pillow_parser.py      # Pengujian perbandingan dengan Pillow Exif Parser
python 00_README/phase9_master_csv.py         # Penggabungan master csv tabel komparatif
python 00_README/phase10_13_analysis_viz.py   # Komputasi statistik akhir dan render figure diagram
```

---

## 👥 Authors

**Kelompok 6** (Digital Forensics Semester 5 - 2026)
* **Iqbal Rizky Maulana**
* **Muhammad Rangga Nur Praditha**
* **Gherry Alviart**
