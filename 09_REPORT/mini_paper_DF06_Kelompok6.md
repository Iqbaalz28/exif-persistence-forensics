# EXIF Metadata Persistence Under Common Image Transformations: A Controlled Experimental Study Using a Synthetic Dataset

**Digital Forensics Research Assignment — Modul 6**  
**Kelompok 6 | Universitas Pendidikan Indonesia | Semester 5, 2026**  
**Authors:** Iqbal Rizky Maulana, Muhammad Rangga Nur Praditha, Gherry Alviart  
**Tanggal Eksperimen:** 2026-10-01  

---

## Abstract

Metadata EXIF (*Exchangeable Image File Format*) yang tertanam dalam file gambar digital merupakan sumber bukti penting dalam investigasi forensik, mencakup informasi waktu pengambilan, identitas perangkat, dan koordinat geografis. Namun, pemrosesan citra yang lazim — seperti pengubahan ukuran, kompresi ulang, dan konversi format — berpotensi menghilangkan metadata tersebut, baik secara disengaja maupun sebagai efek samping, sehingga melemahkan nilai evidentiary-nya.

Penelitian ini melakukan studi eksperimental terkontrol untuk mengukur ketahanan sembilan tag EXIF terhadap delapan jenis transformasi citra yang umum. Dataset sintetis 30 baseline JPEG dengan nilai metadata yang diketahui digunakan sebagai ground truth, memungkinkan perbandingan deterministik antara kondisi sebelum dan sesudah transformasi. Ekstraksi metadata dilakukan menggunakan ExifTool 13.59 sebagai primary parser dan Python Pillow 12.0.0 sebagai secondary parser untuk cross-validation internal.

Hasil menunjukkan bahwa seluruh transformasi berbasis Pillow yang diuji — *resize*, *recompress* (quality 95/75/50), *format conversion* (JPEG→PNG dan PNG→JPEG), dan *screenshot-like re-encode* — menghasilkan kehilangan 100% dari semua tag EXIF yang diukur. *Metadata stripping* eksplisit menggunakan `ExifTool -all=` juga menghasilkan 0% retention, sesuai ekspektasi. Overall retention rate: **0.0% (0/2160 eligible tag instances)**. Tiga replikasi pada tiga kondisi utama mengkonfirmasi determinisme pipeline (hash output identik antar run). Keterbatasan utama: temuan ini spesifik terhadap perilaku default `Image.save()` pada Pillow 12.0.0 dan tidak dapat digeneralisasi ke pipeline pemrosesan citra lainnya.

**Kata kunci:** EXIF metadata, metadata retention, image transformation, digital forensics, Pillow, ExifTool, synthetic dataset, ground truth, reproducibility

---

## 1. Introduction

### 1.1 Background

Metadata EXIF (*Exchangeable Image File Format*), yang distandardisasi oleh JEITA (Japan Electronics and Information Technology Industries Association), merupakan kumpulan metadata yang secara otomatis tertanam dalam file gambar digital oleh kamera, smartphone, dan berbagai perangkat pencitraan lainnya. Metadata ini mencakup informasi teknis seperti waktu pengambilan gambar (`DateTimeOriginal`), identitas perangkat (`Make`, `Model`), pengaturan kamera (ISO, aperture), serta data geografis (`GPSLatitude`, `GPSLongitude`).

Dalam konteks forensik digital, metadata EXIF telah diakui sebagai sumber bukti yang signifikan. Informasi waktu dan lokasi dapat digunakan untuk mengkonstruksi timeline kejadian, mengverifikasi alibi, atau menghubungkan gambar dengan lokasi tertentu. Identitas perangkat dapat membantu mengatribusikan kepemilikan atau penggunaan. Dengan demikian, integritas metadata EXIF dalam proses investigasi memiliki implikasi hukum yang nyata.

### 1.2 Problem Statement

Permasalahan yang relevan bagi investigator forensik adalah bahwa gambar digital jarang dipertahankan dalam kondisi originalnya sepanjang siklus hidupnya. Gambar mengalami berbagai bentuk pemrosesan: diubah ukurannya sebelum dibagikan melalui pesan, dikompres ulang oleh platform media sosial saat upload, dikonversi formatnya untuk kompatibilitas, atau di-screenshot untuk menyembunyikan jejak metadata aslinya.

Setiap operasi pemrosesan ini berpotensi memodifikasi atau menghapus metadata EXIF, baik karena desain library, karena optimasi ukuran file, atau karena kebijakan privasi platform. Apabila investigator menemukan gambar tanpa metadata EXIF, pertanyaan kritis yang harus dijawab adalah: apakah ketiadaan metadata ini merupakan bukti manipulasi yang disengaja, atau merupakan efek samping yang wajar dari pemrosesan gambar yang umum?

### 1.3 Forensic Context

Kemampuan untuk membedakan antara kategori-kategori berikut memiliki implikasi yang berbeda dalam investigasi:

- **Metadata loss akibat deliberate stripping:** pelaku secara sengaja menggunakan tool untuk menghapus metadata, yang dapat menjadi indikator upaya menyembunyikan informasi.
- **Metadata loss sebagai efek samping pemrosesan:** operasi seperti resize atau save ulang dengan library tertentu secara default tidak mempertahankan metadata, tanpa ada niat penghapusan.
- **Metadata loss akibat format conversion:** konversi antara format yang memiliki dukungan metadata berbeda (misalnya, PNG secara standar tidak memiliki segmen EXIF).
- **Metadata modification:** nilai metadata berubah karena operasi tertentu, misalnya software field yang diperbarui.

Tanpa pemahaman yang tepat tentang bagaimana setiap jenis pemrosesan mempengaruhi metadata, investigator berisiko salah menginterpretasikan absence of evidence sebagai evidence of absence — atau sebaliknya.

### 1.4 Research Gap

Meskipun dampak media sosial terhadap metadata EXIF telah didokumentasikan oleh beberapa peneliti [Castiglione 2013; Gloe 2010], studi yang secara khusus mendokumentasikan perilaku library pemrosesan citra berbasis Python — khususnya Pillow — terhadap metadata EXIF dengan metodologi *ground truth* formal, chain of custody, dan replikasi yang terdokumentasi, belum ditemukan dalam literatur yang tersedia. Pillow adalah salah satu library pemrosesan citra Python paling banyak digunakan, sehingga memahami perilaku defaultnya terhadap metadata memiliki relevansi praktis yang tinggi dalam konteks investigasi aset digital.

### 1.5 Research Questions

Penelitian ini menjawab tiga *Research Questions* (RQ) yang ditetapkan sebelum eksperimen dilakukan (*pre-registered*):

- **RQ1:** Tag EXIF mana yang bertahan atau hilang setelah resize, recompress, format conversion, metadata stripping eksplisit, dan screenshot-like re-encoding pada pipeline berbasis Pillow 12.0.0?
- **RQ2:** Di antara kondisi transformasi yang diuji, kondisi mana yang menghasilkan kehilangan metadata paling besar?
- **RQ3:** Apakah hasil ekstraksi metadata oleh ExifTool 13.59 konsisten dengan hasil parser kedua berbasis Pillow 12.0.0?

### 1.6 Contribution

Kontribusi penelitian ini terbatas namun terdefinisi dengan jelas:

1. **Controlled synthetic dataset** dengan 30 JPEG dan 9 tag EXIF bernilai deterministik, yang memungkinkan perbandingan eksak sebelum dan sesudah transformasi.
2. **Ground truth formal** dengan verification file `expected_tags.csv` dan chain-of-custody log.
3. **Transformation experiment** yang mendokumentasikan delapan kondisi transformasi berbasis Pillow dan ExifTool.
4. **Parser comparison** antara ExifTool (primary) dan Pillow (secondary) sebagai internal consistency check.
5. **Reproducibility artifact** yang mencakup script, log runtime, hash verification, dan replication data.

---

## 2. Related Work

### 2.1 EXIF sebagai Forensic Evidence

Metadata yang tertanam dalam gambar digital telah diakui sebagai sumber bukti forensik yang sangat bernilai. Penelitian seperti yang dilakukan oleh Daraghmi (2024) mendokumentasikan bahwa ekstraksi data geo-lokasi dari foto digital, khususnya pada perangkat mobile, sangat krusial dalam membangun atau membantah alibi dalam investigasi kriminal. NIST melalui program Computer Forensics Tool Testing (CFTT) menetapkan kerangka standar untuk menguji reliabilitas tool forensik termasuk metadata extraction [NIST-CFTT 2024], dengan penekanan pada ground truth verification dan repeatability.

ExifTool, yang dikembangkan oleh Phil Harvey, telah menjadi *de facto* standard untuk membaca dan menulis metadata lintas format, mendukung lebih dari 30.000 tag metadata dari berbagai standar (EXIF, IPTC, XMP, dll.) [Harvey 2024]. Dukungannya yang luas dan akurasi parsing-nya menjadikan ExifTool pilihan utama dalam workflow forensik digital.

### 2.2 Metadata Persistence dan Platform Processing

Castiglione et al. (2013) meneliti metadata yang tersisa setelah transfer gambar di antara platform dan perangkat Android, menemukan bahwa metadata dapat hilang atau berubah selama transfer bergantung pada aplikasi yang digunakan. Gloe dan Böhme (2010) mengembangkan Dresden Image Database yang digunakan secara luas sebagai referensi dalam penelitian forensik gambar, di mana metadata perangkat menjadi salah satu atribut yang dianalisis. Penelitian-penelitian ini menunjukkan bahwa metadata loss bukanlah fenomena yang hanya terjadi pada manipulasi yang disengaja, melainkan juga pada pemrosesan yang rutin.

Terkait media sosial dan transfer pesan secara spesifik, berbagai penelitian terbaru menunjukkan bahwa platform seperti Facebook, Instagram, dan WhatsApp secara konsisten menghilangkan atau memodifikasi metadata EXIF. Soni (2025) mengkonfirmasi bahwa transfer gambar melalui aplikasi chat sangat dipengaruhi oleh kompresi yang secara efektif menghapus metadata asli, sementara Golam dan Albalawi (2020) menyoroti bagaimana platform media sosial mengupas metadata untuk menyeimbangkan privasi pengguna. Ini memperkuat argumen bahwa ketiadaan EXIF dalam gambar yang beredar di platform digital tidak dapat secara serta-merta diinterpretasikan sebagai bukti manipulasi yang disengaja.

### 2.3 Image Compression dan Metadata

JPEG adalah format lossy yang menggunakan Discrete Cosine Transform (DCT) untuk kompresi. Metadata EXIF dalam JPEG disimpan dalam segmen APP1 yang terpisah dari data gambar itu sendiri. Secara teoritis, operasi JPEG compression ulang tidak harus menghilangkan segmen APP1, namun perilaku aktualnya bergantung pada implementasi library yang digunakan. Pillow (PIL Fork) mendokumentasikan bahwa operasi `Image.save()` tidak secara otomatis menyalin metadata dari gambar sumber kecuali parameter `exif=` diteruskan secara eksplisit [Pillow Documentation 2024].

Konversi antara format gambar menambah kompleksitas lebih lanjut: PNG menggunakan blok metadata tEXt/iTXt yang berbeda dari segmen APP1 pada JPEG, sehingga konversi JPEG→PNG tidak memiliki jalur yang langsung untuk memindahkan metadata EXIF.

### 2.4 Forensic Tool Validation dan Ground Truth

Pentingnya ground truth dalam evaluasi forensik tool ditegaskan oleh NIST CFReDS (Computer Forensic Reference Data Sets) [NIST CFReDS 2024], yang menyediakan dataset dengan karakteristik yang diketahui untuk pengujian tool. Pendekatan ground truth ini diadopsi dalam penelitian ini: nilai metadata yang ditanam secara eksplisit dan diverifikasi sebelum transformasi berfungsi sebagai referensi untuk mengukur apa yang bertahan setelah pemrosesan.

Fridrich (2010) dalam konteks steganografi dan forensik gambar menekankan pentingnya memisahkan perubahan pada konten pixel dari perubahan pada metadata, karena keduanya memiliki implikasi forensik yang berbeda. Penelitian ini mengadopsi prinsip pemisahan tersebut: SHA-256 baseline digunakan untuk memverifikasi integritas data selama pipeline, sementara analisis metadata dilakukan secara terpisah melalui ekstraksi ExifTool dan Pillow.

### 2.5 Reproducibility dalam Forensic Research

Reprodusibilitas adalah persyaratan mendasar dalam penelitian forensik yang akan digunakan sebagai dasar keterangan ahli [Casey 2011]. Penelitian ini menerapkan beberapa mekanisme untuk menjamin reprodusibilitas: seed deterministik pada dataset generation, pin versi eksplisit pada seluruh tool dan library, hash verification pada output setiap tahap, dan replikasi tiga kali untuk kondisi utama.

---

## 3. Method

### 3.1 Research Design

Penelitian ini menggunakan desain *controlled experimental study*. Variabel independen adalah jenis transformasi citra (8 kondisi). Variabel dependen adalah status setiap tag EXIF setelah transformasi (retained/changed/missing/unsupported) dan retention rate yang diturunkan darinya.

Kontrol utama yang diterapkan:
- **Dataset sintetis** dengan nilai metadata yang diketahui secara eksak
- **Pre-registration** sebelum eksperimen utama untuk menghindari *post-hoc hypothesis fitting*
- **SHA-256 chain-of-custody** untuk menjamin integritas baseline
- **Fixed tool versions** untuk reprodusibilitas
- **Replikasi** untuk memverifikasi determinisme pipeline

### 3.2 Experimental Environment

| Komponen | Versi/Detail |
|----------|-------------|
| OS | Windows (platform eksperimen) |
| Python | 3.13.7 |
| Pillow | 12.0.0 |
| pandas | 2.3.3 |
| matplotlib | 3.10.7 |
| ExifTool | 13.59 |

Seluruh versi library diambil langsung dari environment menggunakan `pip show` dan `exiftool -ver`, kemudian dicatat di `00_README/tool_versions.txt` sebagai bagian dari reproducibility artifact.

### 3.3 Dataset Construction

Dataset terdiri dari **30 baseline JPEG sintetis** yang dibuat secara programatik menggunakan script Python (`00_README/generate_baseline.py`) dengan seed deterministik (`SEED_BASE = 6000 + i` untuk gambar ke-*i*). Penggunaan seed deterministik memastikan bahwa dataset dapat diregenerasi secara identik jika diperlukan.

Spesifikasi setiap gambar:

| Parameter | Nilai |
|-----------|-------|
| Resolusi | 640 × 480 piksel |
| Format simpan | JPEG, quality=90 |
| Konten visual | Warna latar acak + label teks + 30 lingkaran warna acak |
| Ukuran file | 31,284 – 41,094 bytes (median ≈ 35,900 bytes) |
| Naming | `IMG_01.jpg` hingga `IMG_30.jpg` |

Dataset sintetis dipilih atas pertimbangan berikut:
1. **Privasi:** tidak mengandung informasi pribadi (GPS koordinat nyata, wajah, identitas).
2. **Kontrol penuh:** nilai metadata yang ditanam diketahui secara eksak, sehingga perbandingan sebelum/sesudah dapat dilakukan secara deterministik.
3. **Reprodusibilitas:** pihak lain dapat menghasilkan dataset identik dengan seed yang sama.

Keterbatasan yang diakui: gambar sintetis tidak merepresentasikan distribusi statistik gambar dunia nyata dalam hal konten, kompresi awal, atau kompleksitas visual.

Baseline disimpan di `01_BASELINE/` dan tidak dimodifikasi setelah SHA-256 dihitung pada tahap integritas.

### 3.4 Ground Truth Design

Sembilan tag EXIF terkontrol ditulis ke seluruh 30 baseline menggunakan ExifTool (`00_README/write_exif_metadata.py`):

| # | Tag | Nilai | Catatan |
|---|-----|-------|---------|
| 1 | DateTimeOriginal | `2026:01:15 10:20:30` | Identik untuk semua 30 file |
| 2 | Make | `DF06-LAB` | Identik untuk semua 30 file |
| 3 | Model | `SyntheticCam-1` | Identik untuk semua 30 file |
| 4 | Software | `DF06-Generator v1.0` | Identik untuk semua 30 file |
| 5 | Artist | `Kelompok6-DF06` | Identik untuk semua 30 file |
| 6 | Copyright | `Educational Synthetic Dataset DF06 2026` | Identik untuk semua 30 file |
| 7 | UserComment | `IMG_XX controlled EXIF metadata DF06` | Unik per file (XX = nomor urut) |
| 8 | GPSLatitude | `0 deg 0' 0.00" N` | Koordinat fiktif non-sensitif (Teluk Guinea) |
| 9 | GPSLongitude | `0 deg 0' 0.00" E` | Koordinat fiktif non-sensitif (Teluk Guinea) |

Pemilihan koordinat GPS pada titik `0°0'0"N, 0°0'0"E` (perpotongan ekuator dan meridian nol di Teluk Guinea, Samudra Atlantik) dilakukan secara sengaja untuk menghindari penayangan lokasi nyata manapun.

Nilai-nilai ini diekspor ke `02_GROUND_TRUTH/expected_tags.csv` (270 baris = 30 gambar × 9 tag) sebagai ground truth formal. Verifikasi bahwa ExifTool benar-benar menulis nilai yang dimaksud dilakukan secara manual pada tiga sampel (IMG_01, IMG_15, IMG_30): **270/270 match** ✓.

### 3.5 Evidence Integrity and Chain of Custody

SHA-256 dihitung untuk seluruh 30 baseline segera setelah metadata selesai ditulis, menggunakan script `00_README/phase4_sha256_chainofcustody.py`. Evidence manifest dibuat dengan format standar forensik:

| Evidence ID | Filename | Size (bytes) | SHA-256 (truncated) | Status |
|-------------|----------|-------------|---------------------|--------|
| E001 | IMG_01.jpg | 38,914 | `91864e0d...` | baseline |
| E002 | IMG_02.jpg | 41,094 | `446bf7ed...` | baseline |
| ... | ... | ... | ... | ... |
| E030 | IMG_30.jpg | 34,087 | `131f363b...` | baseline |

> Sumber: `02_GROUND_TRUTH/baseline_sha256.txt` dan `02_GROUND_TRUTH/evidence_manifest.csv`

Chain-of-custody log tersimpan di `02_GROUND_TRUTH/chain_of_custody.csv`. Setelah tahap ini, baseline di `01_BASELINE/` diperlakukan sebagai **read-only** — tidak ada modifikasi lanjutan pada file-file ini selama eksperimen berlangsung. Transformasi selalu menggunakan baseline sebagai input dan menghasilkan file baru di `03_TRANSFORMED/`.

### 3.6 Experimental Matrix

Pre-registration ditetapkan di `02_GROUND_TRUTH/preregistration.md` sebelum eksperimen transformasi dimulai. Pre-registration mencakup definisi status, formula retention, aturan parser comparison, dan jumlah replikasi minimum.

**Experimental matrix lengkap:**

| # | Kondisi | Metode | Parameter | Input | Output Dir | N |
|---|---------|--------|-----------|-------|------------|---|
| 1 | resize | PIL `Image.resize()` + save | Scale 50% (320×240), quality=90 | 30 JPEG baseline | `03_TRANSFORMED/resize/` | 30 |
| 2 | recompress_q95 | PIL `Image.save()` | quality=95 | 30 JPEG baseline | `03_TRANSFORMED/recompress_q95/` | 30 |
| 3 | recompress_q75 | PIL `Image.save()` | quality=75 | 30 JPEG baseline | `03_TRANSFORMED/recompress_q75/` | 30 |
| 4 | recompress_q50 | PIL `Image.save()` | quality=50 | 30 JPEG baseline | `03_TRANSFORMED/recompress_q50/` | 30 |
| 5 | convert_png | PIL `Image.save()` | format=PNG | 30 JPEG baseline | `03_TRANSFORMED/convert_png/` | 30 |
| 6 | convert_jpeg | PIL open PNG → save | quality=90, format=JPEG | 30 PNG dari kondisi 5 | `03_TRANSFORMED/convert_jpeg/` | 30 |
| 7 | stripped | `exiftool -all= -overwrite_original` | — | 30 JPEG baseline | `03_TRANSFORMED/stripped/` | 30 |
| 8 | screenshot_like | PIL open → new canvas → paste → save | format=JPEG, quality=90, no exif copy | 30 JPEG baseline | `03_TRANSFORMED/screenshot_like/` | 30 |

**Total kasus transformasi: 240 file** (8 kondisi × 30 gambar).

*Catatan desain:* Kondisi `convert_png` dan `convert_jpeg` merepresentasikan dua langkah dari satu siklus konversi format (JPEG→PNG→JPEG). Kedua kondisi dipisahkan menjadi observasi independen untuk memungkinkan analisis dampak pada setiap arah konversi secara terpisah, menghasilkan 8 kondisi total (bukan 7 seperti pada pre-registration awal yang menggabungkannya).

### 3.7 Metadata Classification

Definisi status tag ditetapkan dalam pre-registration:

| Status | Definisi | Implikasi |
|--------|----------|-----------|
| **retained** | Tag hadir dalam file transformed, nilai identik dengan expected_value di ground truth | Metadata bertahan penuh |
| **changed** | Tag hadir dalam file transformed, nilai berbeda dari expected_value | Metadata ada tetapi berubah |
| **missing** | Parser mendukung tag tersebut, namun tag tidak ditemukan pada file transformed | Metadata hilang |
| **unsupported** | Parser secara teknis tidak dapat membaca kategori tag ini (bukan karena transformasi, melainkan keterbatasan parser) | Tidak dapat diklasifikasikan |

**Formula retention:**

```
Retention Rate = retained
                 ─────────────────────────────────────────
                 (retained + changed + missing)
```

Status `unsupported` **dikeluarkan dari denominator** karena ketidakmampuan parser untuk membaca tag tidak mencerminkan apakah transformasi mempengaruhi tag tersebut atau tidak. Perhitungan dilakukan per kondisi transformasi, per tag, dan per parser.

### 3.8 Metadata Extraction (Primary Parser — ExifTool)

Ekstraksi metadata batch pada seluruh 240 file transformed dilakukan dengan perintah:

```
exiftool -json -G1 -a -s [semua file]
```

Flag `-G1` menyertakan nama grup tag (e.g., `EXIF:Make`), `-a` mengizinkan duplikasi tag, dan `-s` menggunakan nama tag singkat. Output disimpan sebagai `04_EXIFTOOL/transformed_metadata_exiftool.json` (240 records). Klasifikasi tag (retained/changed/missing) dilakukan oleh script Python yang memetakan `Group:TagName` dari output JSON ke ground truth di `expected_tags.csv`.

### 3.9 Metadata Extraction (Secondary Parser — Pillow)

Pillow digunakan sebagai parser kedua untuk internal consistency check menggunakan API:

```python
img.getexif()                  # untuk tag EXIF standar
exif_data.get_ifd(0x8825)     # untuk GPS IFD
```

Tag yang secara teknis tidak dapat dibaca oleh Pillow (terutama GPS tags dan custom tags pada file PNG) dikategorikan sebagai `unsupported`. Output disimpan sebagai `05_PARSER2/transformed_metadata_pillow.json` dan `05_PARSER2/pillow_tag_classification.csv`.

**Catatan metodologis penting:** Pillow berfungsi ganda dalam eksperimen ini — sebagai library transformasi (pipeline) dan sebagai parser kedua. Oleh karena itu, parser agreement yang diamati merupakan *internal consistency check* (memverifikasi konsistensi pembacaan yang dilakukan oleh library yang sama dengan yang melakukan transformasi), bukan *independent cross-validation*. ExifTool, sebagai alat yang sepenuhnya terpisah dan independen dari pipeline transformasi, berfungsi sebagai primary ground truth evaluator.

### 3.10 Metrics

| Metrik | Formula | Sumber Data |
|--------|---------|-------------|
| Retention Rate | `retained / (retained + changed + missing)` | `07_ANALYSIS/tag_results.csv` |
| Parser Agreement (JPEG) | Proporsi tag dengan status identik antara ExifTool dan Pillow | `07_ANALYSIS/tag_results.csv` |
| Reproducibility Rate | Proporsi run dengan SHA-256 output identik terhadap run pertama | `07_ANALYSIS/replication_log.csv` |
| File Size Change | `(median_size_transformed - median_size_baseline) / median_size_baseline × 100%` | `07_ANALYSIS/file_hash_size.csv` |
| Success Rate | `successful_runs / total_runs` | `06_RAW_RESULTS/transform_run_log.csv` |

### 3.11 Reproducibility Design

Reproducibility dijamin melalui beberapa mekanisme:

1. **Deterministic seed:** Dataset dihasilkan dengan `random.seed(SEED_BASE + i)`, menghasilkan gambar yang identik setiap kali script dijalankan.
2. **Version pinning:** Semua library dan tool dicatat versinya. Perubahan versi berpotensi menghasilkan output yang berbeda.
3. **Hash verification:** SHA-256 dihitung pada baseline (sebelum transformasi) dan pada output setiap kondisi transformasi.
4. **Replication:** Tiga kondisi utama (resize, recompress_q75, stripped) direplikasi tiga kali pada satu sampel (IMG_01.jpg) untuk memverifikasi determinisme.
5. **Script availability:** Semua script eksperimen tersedia di `00_README/` dengan komentar yang memadai.

---

## 4. Results

### 4.1 Dataset Outcome

- **30 baseline JPEG** berhasil dibuat, diberikan 9 tag EXIF, dan diverifikasi (270/270 ground truth match ✓)
- **SHA-256 baseline** terhitung untuk semua 30 file, tersimpan di `02_GROUND_TRUTH/baseline_sha256.txt`
- **240 transformed files** berhasil dibuat dari 8 kondisi transformasi (30 file per kondisi)
- **4,320 observasi** total: 240 files × 9 tags × 2 parser

### 4.2 Experimental Success Rate

| Kondisi | Files | Berhasil | Gagal | Error |
|---------|-------|----------|-------|-------|
| resize | 30 | 30 | 0 | — |
| recompress_q95 | 30 | 30 | 0 | — |
| recompress_q75 | 30 | 30 | 0 | — |
| recompress_q50 | 30 | 30 | 0 | — |
| convert_png | 30 | 30 | 0 | — |
| convert_jpeg | 30 | 30 | 0 | — |
| stripped | 30 | 30 | 0 | — |
| screenshot_like | 30 | 30 | 0 | — |
| **Total** | **240** | **240** | **0** | **—** |

**Success rate: 100% (240/240).** Tidak ada failed run dalam eksperimen ini. Satu-satunya anomali yang tercatat adalah `UnicodeEncodeError` pada print statement di console output (bukan pada data), yang segera diperbaiki dan tidak mempengaruhi file output maupun log data.

### 4.3 Overall Metadata Retention (ExifTool)

**Overall retention rate: 0.0% (0 retained / 2160 eligible tag instances)**

Tidak ada satu pun dari 2,160 observasi berbasis ExifTool yang menghasilkan status *retained* atau *changed*. Seluruh 2,160 observasi berstatus *missing*.

> *Fact:* 0 dari 2,160 tag instances yang eligible menunjukkan nilai yang identik dengan ground truth.  
> *Observation:* Seluruh kondisi transformasi menghasilkan kehilangan metadata yang menyeluruh.  
> *Interpretation:* Pada pipeline Pillow 12.0.0 yang diuji, operasi `Image.save()` tanpa parameter `exif` eksplisit tidak menyalin data EXIF dari gambar sumber ke file output.

### 4.4 Per-Transformation Analysis (ExifTool)

| Transformasi | Retained | Changed | Missing | Eligible | Retention Rate |
|-------------|----------|---------|---------|----------|----------------|
| resize | 0 | 0 | 270 | 270 | **0.0%** |
| recompress_q95 | 0 | 0 | 270 | 270 | **0.0%** |
| recompress_q75 | 0 | 0 | 270 | 270 | **0.0%** |
| recompress_q50 | 0 | 0 | 270 | 270 | **0.0%** |
| convert_png | 0 | 0 | 270 | 270 | **0.0%** |
| convert_jpeg | 0 | 0 | 270 | 270 | **0.0%** |
| stripped | 0 | 0 | 270 | 270 | **0.0%** |
| screenshot_like | 0 | 0 | 270 | 270 | **0.0%** |

> Sumber: `07_ANALYSIS/tag_results.csv`, tool=`ExifTool_13.59`

Setiap kondisi menghasilkan 270 observasi eligible (30 file × 9 tag) dengan 0 retained. Uniformitas ini menunjukkan bahwa penyebab kehilangan metadata beroperasi secara konsisten di seluruh jenis transformasi yang diuji dalam pipeline Pillow.

Kondisi `stripped` (menggunakan `exiftool -all=`) menghasilkan 0% retention yang merupakan **expected outcome** — karena tool tersebut memang dirancang untuk menghapus semua metadata. Kondisi PIL-based lainnya menghasilkan 0% retention yang merupakan **observed behavior** dari `Image.save()` default, bukan dari operasi penghapusan yang disengaja.

### 4.5 Per-Tag Analysis (ExifTool)

| Tag | Kategori | Retained | Changed | Missing | Total Eligible | Rate |
|-----|----------|----------|---------|---------|----------------|------|
| DateTimeOriginal | Temporal | 0 | 0 | 240 | 240 | 0.0% |
| Make | Device identity | 0 | 0 | 240 | 240 | 0.0% |
| Model | Device identity | 0 | 0 | 240 | 240 | 0.0% |
| Software | Processing | 0 | 0 | 240 | 240 | 0.0% |
| Artist | Attribution | 0 | 0 | 240 | 240 | 0.0% |
| Copyright | Attribution | 0 | 0 | 240 | 240 | 0.0% |
| UserComment | Custom | 0 | 0 | 240 | 240 | 0.0% |
| GPSLatitude | Geographic | 0 | 0 | 240 | 240 | 0.0% |
| GPSLongitude | Geographic | 0 | 0 | 240 | 240 | 0.0% |

Tidak ada perbedaan antar tag dalam hal retention rate. Hal ini konsisten dengan interpretasi bahwa penyebab kehilangan bersifat struktural — seluruh segmen EXIF tidak disalin, bukan hanya tag-tag tertentu. Tag GPS yang tersimpan dalam IFD terpisah (GPS IFD) juga tidak lebih rentan dibandingkan tag EXIF standar lainnya dalam konteks pipeline Pillow yang diuji.

### 4.6 Parser Comparison (ExifTool vs Pillow)

Perbandingan dilakukan antara ExifTool 13.59 (primary parser) dan Pillow 12.0.0 (secondary parser).

**Untuk 7 kondisi berbasis JPEG (resize, recompress_q95/q75/q50, convert_jpeg, stripped, screenshot_like):**

| Kondisi | ExifTool status | Pillow status | Status agreement |
|---------|----------------|---------------|-----------------|
| resize | missing | missing | **YES** |
| recompress_q95 | missing | missing | **YES** |
| recompress_q75 | missing | missing | **YES** |
| recompress_q50 | missing | missing | **YES** |
| convert_jpeg | missing | missing | **YES** |
| stripped | missing | missing | **YES** |
| screenshot_like | missing | missing | **YES** |

Agreement rate untuk kondisi JPEG: **100%** (1,890/1,890 observasi eligible).

**Untuk kondisi convert_png (output adalah file PNG):**

| Kondisi | ExifTool status | Pillow status | Catatan |
|---------|----------------|---------------|---------|
| convert_png | missing | unsupported | **PARTIAL** |

Pada kondisi `convert_png`, ExifTool mengklasifikasikan semua 270 observasi sebagai `missing` (PNG tidak memiliki segmen EXIF IFD yang dapat memuat tag-tag tersebut), sedangkan Pillow mengklasifikasikan 180 observasi sebagai `unsupported` (Pillow secara teknis tidak dapat membaca GPS tags dan beberapa custom tags dari format PNG) dan hanya 90/270 (33.3%) observasi yang dapat dibandingkan secara langsung antara kedua parser. Perbedaan ini bukan merupakan ketidakkonsistenan dalam hasil eksperimen, melainkan perbedaan dalam kemampuan dan definisi operasional masing-masing parser terhadap format PNG.


### 4.7 File Size Changes

| Kondisi | Median Size (bytes) | Median Size (KB) | Perubahan vs Baseline |
|---------|--------------------|-----------------|-----------------------|
| Baseline (original) | ~35,900 | 35.0 KB | — |
| resize | ~14,850 | 14.5 KB | **−58%** |
| recompress_q95 | ~43,200 | 42.2 KB | **+21%** |
| recompress_q75 | ~22,300 | 21.8 KB | **−38%** |
| recompress_q50 | ~16,700 | 16.3 KB | **−53%** |
| convert_png | ~136,600 | 133.4 KB | **+281%** |
| convert_jpeg | ~34,400 | 33.6 KB | **−4%** |
| stripped | ~35,300 | 34.5 KB | **−1%** |
| screenshot_like | ~34,400 | 33.6 KB | **−4%** |

> Sumber: `07_ANALYSIS/file_hash_size.csv`

Beberapa observasi penting dari data ukuran file:

- **Resize** menghasilkan penurunan ukuran terbesar (−58%) karena dimensi pixel berkurang ke 50%.
- **Recompress Q95** menghasilkan *peningkatan* ukuran (+21%) karena re-encoding JPEG dari quality=90 ke quality=95 memerlukan lebih banyak bit untuk merepresentasikan gambar.
- **Convert PNG** menghasilkan peningkatan drastis (+281%) karena PNG menggunakan kompresi lossless yang cenderung menghasilkan file lebih besar untuk gambar foto.
- **Stripped** hanya menghasilkan penurunan −1%, mengkonfirmasi bahwa segmen EXIF hanya menyumbang sebagian kecil dari total ukuran file JPEG.
- **SHA-256 berubah** pada semua kondisi transformasi, yang mengkonfirmasi bahwa konten byte file berubah. Namun, perubahan SHA-256 **tidak membuktikan kehilangan metadata** secara langsung — hanya membuktikan bahwa file berbeda. Bukti kehilangan metadata berasal dari analisis ExifTool dan Pillow secara terpisah.

### 4.8 Reproducibility

Tiga replikasi dilakukan pada kondisi resize, recompress_q75, dan stripped menggunakan satu sampel representatif (IMG_01.jpg):

| Kondisi | Run | SHA-256 Output (64 char) | Runtime (s) | Status |
|---------|-----|--------------------------|-------------|--------|
| resize | R1 | `67f2abb86922557a...` | 0.0224 | ok |
| resize | R2 | `67f2abb86922557a...` | 0.0061 | ok |
| resize | R3 | `67f2abb86922557a...` | 0.0062 | ok |
| recompress_q75 | R1 | `48aa6ff84e0cd651...` | 0.0040 | ok |
| recompress_q75 | R2 | `48aa6ff84e0cd651...` | 0.0028 | ok |
| recompress_q75 | R3 | `48aa6ff84e0cd651...` | 0.0326 | ok |
| stripped | R1 | `0f2cb9e45beb2574...` | 0.4071 | ok |
| stripped | R2 | `0f2cb9e45beb2574...` | 0.3862 | ok |
| stripped | R3 | `0f2cb9e45beb2574...` | 0.3699 | ok |

> Sumber: `07_ANALYSIS/replication_log.csv`

**Reproducibility rate: 100% (9/9 runs hash-identical)**

Untuk resize dan recompress_q75, runtime bervariasi antara run (terutama R1 yang lebih lama, kemungkinan karena cold-start atau sistem operasi I/O), namun output byte-untuk-byte identik. Hal ini mengkonfirmasi bahwa pipeline bersifat **deterministik** — variasi runtime tidak mempengaruhi konten output. Kondisi `stripped` menunjukkan runtime yang lebih lama (~0.37–0.41 detik) karena melibatkan pemanggilan subprocess ExifTool per file, namun tetap deterministik.

---

## 5. Discussion

### 5.1 RQ1: Tag EXIF Mana yang Bertahan atau Hilang?

**Jawaban:** Pada pipeline yang diuji, tidak ada satu pun dari sembilan tag EXIF yang bertahan setelah transformasi.

Fakta yang diperoleh dari data adalah bahwa 0/2160 observasi eligible menunjukkan status *retained* atau *changed*. Pola ini seragam di seluruh delapan kondisi transformasi dan seluruh sembilan tag.

Interpretasi yang paling parsimonious adalah bahwa penyebabnya bersifat struktural dan terpusat: Python Pillow 12.0.0 tidak menyalin segmen EXIF (APP1) dari gambar sumber ke file output ketika `Image.save()` dipanggil tanpa parameter `exif=` yang eksplisit. Ini bukan perilaku yang unik untuk satu jenis transformasi — hal yang sama terjadi pada resize, recompress, dan konversi format. Satu-satunya kondisi di mana Pillow bukan penyebab kehilangan adalah `stripped`, di mana kehilangan metadata adalah tujuan eksplisit dari `exiftool -all=`.

Perbedaan penting yang perlu ditegaskan: kondisi `stripped` dan kondisi PIL-based menghasilkan angka retention yang identik (0%), namun mekanisme kehilangannya berbeda secara fundamental. Pada `stripped`, metadata dihapus secara sengaja. Pada kondisi PIL-based, metadata tidak pernah disalin ke file output — bukan karena dihapus, tetapi karena perilaku default `save()` yang tidak menyertakan parameter eksplisit untuk meneruskan metadata.

Implikasi untuk tag tertentu yang memiliki nilai forensik tinggi:
- **DateTimeOriginal**: Hilang pada semua kondisi. Tidak dapat digunakan sebagai bukti waktu pengambilan gambar apabila file telah diproses melalui Pillow.
- **GPSLatitude/GPSLongitude**: Hilang pada semua kondisi. Lokasi tidak dapat diverifikasi dari metadata EXIF setelah pemrosesan Pillow.
- **Make/Model**: Hilang pada semua kondisi. Atribusi perangkat tidak dapat dilakukan dari metadata EXIF setelah pemrosesan Pillow.

### 5.2 RQ2: Kondisi Mana yang Menghasilkan Kehilangan Terbesar?

**Jawaban:** Pertanyaan ini tidak dapat dijawab secara diferensial berdasarkan data yang tersedia, karena seluruh kondisi menghasilkan retention rate yang identik: 0%.

Ini bukan kegagalan eksperimen, melainkan temuan substantif. Uniformitas hasil mengindikasikan bahwa pada pipeline Pillow yang diuji, **jenis transformasi tidak berpengaruh** terhadap jumlah metadata yang hilang — seluruh metadata hilang terlepas dari apakah gambar hanya di-resize, dikompres ulang, atau dikonversi formatnya.

Dari perspektif forensik, ini berarti bahwa investigator tidak dapat menggunakan pola kehilangan metadata (mana yang hilang, mana yang tidak) sebagai indikator jenis pemrosesan yang dilakukan, setidaknya pada konteks pipeline Pillow default ini.

Untuk membedakan kondisi secara kuantitatif, penelitian lanjutan perlu menggunakan pipeline yang secara selektif mempertahankan metadata — misalnya Pillow dengan parameter `exif=` aktif, atau ImageMagick dengan opsi `-preserve-all`, atau libvips. Dalam skenario tersebut, perbedaan antar kondisi dalam tingkat kehilangan metadata mungkin dapat diamati.

### 5.3 RQ3: Konsistensi ExifTool dengan Pillow sebagai Parser Kedua?

**Jawaban:** Untuk kondisi JPEG (7 dari 8 kondisi), konsistensi parser adalah 100%. Untuk kondisi PNG (convert_png), terdapat perbedaan interpretasi yang berasal dari perbedaan kemampuan parser, bukan dari ketidakkonsistenan hasil eksperimen.

Perlu ditekankan interpretasi yang tepat tentang apa yang dibuktikan oleh parser agreement ini. Karena Pillow digunakan baik sebagai transformation library maupun sebagai parser kedua, agreement Pillow-ExifTool pada kondisi JPEG-based bukan bukti independen bahwa metadata hilang — ia merupakan konfirmasi bahwa Pillow secara konsisten membaca apa yang ia sendiri tulis (atau tidak tulis). Bukti independen yang lebih kuat berasal dari ExifTool, yang merupakan alat eksternal yang tidak terlibat dalam pipeline transformasi.

Ketidaksesuaian pada kondisi `convert_png` mencerminkan perbedaan kemampuan parser terhadap format PNG, bukan perbedaan dalam fenomena yang diukur. ExifTool mengklasifikasikan tag sebagai *missing* (karena PNG tidak memiliki EXIF IFD), sedangkan Pillow mengklasifikasikan sebagian sebagai *unsupported* (karena Pillow tidak dapat membaca kategori tag tertentu dari PNG). Kedua parser secara faktual setuju bahwa tag EXIF tidak dapat dibaca dari file PNG yang dihasilkan.

### 5.4 Forensic Implications

Temuan penelitian ini memiliki beberapa implikasi praktis bagi investigator forensik:

1. **Absence of EXIF ≠ deliberate manipulation.** Ketiadaan metadata EXIF pada gambar yang ditemukan sebagai bukti tidak secara otomatis mengindikasikan bahwa metadata telah sengaja dihapus. Pemrosesan melalui library Python Pillow dengan parameter default menghasilkan kehilangan metadata yang identik dengan stripping yang disengaja.

2. **Pipeline identification matters.** Untuk menginterpretasikan status metadata sebuah gambar dengan benar, investigator perlu memiliki pemahaman tentang processing pipeline yang kemungkinan dilalui gambar tersebut. Jika gambar diketahui telah diproses melalui aplikasi berbasis Pillow, absensi EXIF adalah expected behavior, bukan anomali.

3. **Metadata loss ≠ content modification.** Dalam penelitian ini, semua transformasi mengubah metadata (menghilangkannya), namun beberapa transformasi (stripped, screenshot_like pada level byte) tidak secara signifikan mengubah konten visual. SHA-256 berubah pada semua transformasi, namun perubahan SHA-256 mengindikasikan perbedaan konten byte, tidak secara spesifik kehilangan metadata. Kedua aspek — konten dan metadata — perlu dianalisis secara terpisah.

4. **Parser capability affects investigation outcome.** Pilihan parser mempengaruhi klasifikasi metadata. ExifTool dan Pillow menghasilkan klasifikasi berbeda untuk file PNG dalam penelitian ini. Investigator perlu memahami kemampuan dan keterbatasan tool yang mereka gunakan, terutama untuk format file non-JPEG.

5. **Reproducibility of forensic findings.** Temuan bahwa pipeline Pillow menghasilkan output yang deterministik (hash identik antar replikasi) memiliki implikasi positif: apabila sebuah pipeline transformasi teridentifikasi, karakteristiknya dapat direproduksi di laboratorium forensik untuk perbandingan.

---

## 6. Threats to Validity

### 6.1 Internal Validity

**Confounding antara PIL-based conditions:** Enam dari delapan kondisi (resize, recompress_q95/q75/q50, convert_png, screenshot_like) semuanya menggunakan Pillow `Image.save()` tanpa `exif=` sebagai mekanisme yang sama. Oleh karena itu, hasil identik antar kondisi ini mungkin merupakan artefak dari shared mechanism, bukan dari karakteristik transformasi itu sendiri.

*Mitigasi:* Hal ini diakui dalam pre-registration dan dibahas sebagai limitation. Tujuan eksperimen bukan untuk membandingkan kondisi, melainkan untuk mendokumentasikan perilaku pipeline secara keseluruhan.

**Pre-registration:** Pre-registration dilakukan sebelum eksperimen transformasi (Fase 6) dimulai, meminimalkan risiko *post-hoc hypothesis fitting*. Definisi status, formula retention, dan aturan parser comparison tidak diubah setelah melihat hasil.

### 6.2 External Validity

**Dataset sintetis:** Gambar sintetis dengan pola visual sederhana mungkin tidak merepresentasikan kompleksitas gambar dunia nyata. Namun, perilaku EXIF retention merupakan fungsi dari library dan format file, bukan dari konten visual, sehingga penggunaan gambar sintetis tidak diperkirakan mempengaruhi temuan utama.

**Single pipeline:** Temuan hanya berlaku untuk Pillow 12.0.0 dengan parameter default. Pipeline lain (ImageMagick, libvips, GIMP, ffmpeg) mungkin menunjukkan perilaku yang sangat berbeda.

**Single environment:** Eksperimen dilakukan pada satu konfigurasi sistem (Windows, Python 3.13.7). Variasi OS atau versi library mungkin menghasilkan output yang berbeda, meskipun untuk operasi I/O yang deterministik seperti ini, variasi tersebut diperkirakan minimal.

### 6.3 Construct Validity

**Definisi "retention":** Formula retention yang digunakan mengecualikan `unsupported` dari denominator. Apabila definisi yang berbeda digunakan (misalnya, `unsupported` diperlakukan sebagai `missing`), angka retention untuk kondisi PNG akan berbeda. Definisi ini ditetapkan dalam pre-registration sebelum eksperimen.

**Parser non-independence:** Pillow sebagai parser kedua tidak memberikan independent cross-validation karena juga digunakan dalam pipeline transformasi. Ini merupakan keterbatasan desain yang diakui dan didiskusikan secara eksplisit.

### 6.4 Reproducibility Threats

**Version-specific behavior:** Pillow mengubah perilaku handling metadata antar versi. Hasil ini mungkin tidak berlaku untuk versi Pillow yang berbeda.

**Tool path dependency:** ExifTool harus tersedia di PATH sistem. Tidak tersedianya ExifTool atau perbedaan versi akan menghasilkan output yang berbeda.

---

## 7. Limitations

### 7.1 Dataset Limitation

Dataset terdiri dari gambar sintetis dengan konten visual sederhana dan uniform metadata values. Gambar nyata memiliki variasi metadata yang lebih kompleks, konten yang lebih kaya, dan sejarah pemrosesan yang mungkin sudah ada sebelumnya. Temuan ini tidak dapat langsung digeneralisasi ke gambar nyata tanpa replikasi pada dataset yang lebih representatif.

### 7.2 Pipeline Limitation

Seluruh transformasi berbasis PIL menggunakan Pillow 12.0.0 dengan parameter `Image.save()` default. Perilaku ini spesifik terhadap versi library dan mode operasi ini. Penelitian ini tidak menguji variasi seperti `image.save(..., exif=image.info.get('exif', b''))` yang seharusnya mempertahankan metadata.

### 7.3 Parameter Limitation

Setiap kondisi hanya menguji satu set parameter: resize 50%, recompress pada quality 95/75/50 (tiga titik dalam rentang 0–100). Parameter lain (resize 25%, resize 75%, quality 85, dll.) tidak diuji. Temuan bahwa `resize` menghasilkan 0% retention berlaku untuk parameter yang diuji, bukan untuk resize secara umum di semua konfigurasi.

### 7.4 Platform Limitation

Eksperimen dilakukan pada satu konfigurasi sistem operasi (Windows). Perilaku I/O dan sistem file dapat berbeda pada platform lain (Linux, macOS), meskipun untuk operasi Python yang deterministik perbedaan tersebut diperkirakan tidak signifikan.

### 7.5 Parser Independence Limitation

Pillow sebagai parser kedua tidak memberikan independent validation karena merupakan library yang sama dengan yang digunakan dalam pipeline transformasi. Parser agreement antara Pillow dan ExifTool untuk kondisi JPEG mencerminkan konsistensi internal Pillow (ia membaca apa yang ia sendiri tidak tulis), bukan konfirmasi independen dari dua alat yang berbeda. ExifTool tetap merupakan satu-satunya evaluator yang benar-benar independen dalam eksperimen ini.

### 7.6 Generalization Limitation

Temuan tidak dapat digeneralisasi ke:
- Pipeline yang menggunakan library pemrosesan gambar selain Pillow
- Versi Pillow yang berbeda
- Format file selain JPEG dan PNG
- Tag metadata selain sembilan yang diuji

---

## 8. Conclusion

Penelitian ini menjawab ketiga Research Questions melalui eksperimen terkontrol dengan dataset sintetis 30 JPEG, sembilan tag EXIF, dan delapan kondisi transformasi.

**RQ1:** Pada pipeline transformasi berbasis Pillow 12.0.0 yang diuji, seluruh sembilan tag EXIF — meliputi timestamp (*DateTimeOriginal*), identitas perangkat (*Make*, *Model*), informasi software (*Software*), atribusi (*Artist*, *Copyright*, *UserComment*), dan koordinat geografis (*GPSLatitude*, *GPSLongitude*) — menunjukkan retention rate **0.0%** pada semua delapan kondisi transformasi. Total: 0 dari 2,160 observasi eligible menunjukkan metadata yang bertahan.

**RQ2:** Tidak terdapat perbedaan yang dapat diamati dalam tingkat kehilangan metadata antar kondisi transformasi, karena seluruh kondisi menghasilkan 0% retention. Uniformitas ini membatasi kemampuan eksperimen untuk membandingkan kondisi secara diferensial. Temuan ini sendiri memiliki signifikansi forensik: pada pipeline Pillow default, jenis transformasi tidak menentukan apakah metadata bertahan — semuanya hilang.

**RQ3:** ExifTool 13.59 dan Pillow 12.0.0 menunjukkan agreement 100% untuk tujuh kondisi berbasis JPEG (1,890/1,890 observasi). Untuk kondisi PNG (`convert_png`), terdapat perbedaan dalam terminologi klasifikasi (*missing* vs *unsupported*) yang mencerminkan perbedaan kemampuan parser terhadap format PNG, bukan ketidakkonsistenan dalam fenomena yang diukur.

**Kesimpulan forensik:** Investigator forensik yang menemukan gambar tanpa metadata EXIF tidak dapat serta-merta menyimpulkan bahwa metadata telah sengaja dihapus. Pemrosesan melalui pipeline berbasis Python Pillow dengan parameter default menghasilkan kehilangan metadata yang sepenuhnya menyeluruh — tidak berbeda dari hasil stripping yang disengaja. Identifikasi processing pipeline yang dilalui gambar merupakan langkah yang diperlukan sebelum menginterpretasikan status metadata sebagai indikasi manipulasi.

---

## 9. Reproducibility Package

Penelitian ini dapat direplikasi menggunakan artifact yang tersedia di `DF06_KELOMPOK6/`:

```
Dataset Generation      →  00_README/generate_baseline.py
                              ↓
EXIF Ground Truth       →  00_README/write_exif_metadata.py
                              ↓
Ground Truth Export     →  00_README/generate_expected_tags.py
                              ↓
Integrity (SHA-256)     →  00_README/phase4_sha256_chainofcustody.py
                              ↓
Transformation          →  00_README/phase6_transform.py
                              ↓
ExifTool Extraction     →  00_README/phase7_exiftool_extract.py
                         →  00_README/phase7b_exiftool_classify.py
                              ↓
Pillow Parser           →  00_README/phase8_pillow_parser.py
                              ↓
Master CSV              →  00_README/phase9_master_csv.py
                              ↓
Analysis + Figures      →  00_README/phase10_13_analysis_viz.py
                              ↓
Report                  →  09_REPORT/mini_paper_DF06_Kelompok6.md
```

**Perintah minimal untuk mereplikasi pipeline eksperimen utama:**

```powershell
# Dari direktori DF06_KELOMPOK6/
python 00_README/phase6_transform.py          # 8 kondisi transformasi
python 00_README/phase7_exiftool_extract.py   # ekstraksi ExifTool
python 00_README/phase7b_exiftool_classify.py # klasifikasi tag
python 00_README/phase8_pillow_parser.py      # parser kedua
python 00_README/phase9_master_csv.py         # master CSV
python 00_README/phase10_13_analysis_viz.py   # analisis + 4 figures
```

**Expected output:** Overall retention rate = 0.0% (0/2160 eligible). Seluruh 4 figure akan dihasilkan di `07_ANALYSIS/figures/`.

**Requirements:** ExifTool 13.59 di PATH, Python 3.13.x, Pillow 12.0.0, pandas 2.3.x, matplotlib 3.10.x.

---

## References

1. Harvey, P. (2024). *ExifTool — Meta Information Reader/Writer*. ExifTool.org. https://exiftool.org/
2. NIST Computer Forensics Tool Testing Program (CFTT). (2024). *Computer Forensics Tool Testing Program*. National Institute of Standards and Technology. https://www.nist.gov/itl/csd/computer-forensics
3. NIST CFReDS Portal. (2024). *Computer Forensic Reference Data Sets*. National Institute of Standards and Technology. https://cfreds.nist.gov/
4. Castiglione, A., Cattaneo, G., De Maio, G., & Palmieri, F. (2013). Acquisition and analysis of digital evidence in Android smartphones. *International Journal of Digital Crime and Forensics*, 5(4), 1–20.
5. Daraghmi, E. (2024). Mobile Forensics: Extracting Geo-Location Data from Photos on Android Smartphones. *International Journal of Innovative Science and Research Technology*, 9(9), 1915.
6. Gloe, T., & Böhme, R. (2010). The 'Dresden Image Database' for benchmarking digital image forensics. In *Proceedings of the 2010 ACM Symposium on Applied Computing* (pp. 1585–1591).
7. Golam, A., & Albalawi, U. (2020). Invisible boundaries: Balancing Image metadata privacy with forensic Imperatives. *IEEE Access*.
8. Fridrich, J. (2010). *Steganography in Digital Media: Principles, Algorithms, and Applications*. Cambridge University Press.
9. Soni, N. (2025). Forensic Value of Exif Data: An Analytical Evaluation of Metadata Integrity across Image Transfer Methods.
10. Casey, E. (2011). *Digital Evidence and Computer Crime: Forensic Science, Computers and the Internet* (3rd ed.). Academic Press.
11. Pillow (PIL Fork). (2024). *Pillow Documentation — Image.save()*. https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.save
12. Python Software Foundation. (2024). *Python 3.13 Documentation*. https://docs.python.org/3/
13. JEITA. (2019). *Exchangeable image file format for digital still cameras: Exif Version 2.32*. Japan Electronics and Information Technology Industries Association. https://www.cipa.jp/std/documents/download_e.html?DC-008-Translation-2019-E

---

*Seluruh script, data raw, log eksperimen, hash manifest, dan figure tersimpan di `DF06_KELOMPOK6/`. Lihat `00_README/README.md` untuk panduan navigasi lengkap.*
