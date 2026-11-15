# Progress — Rombak Total: Notebook Preprocessing

Tanggal: 2026-11-15

## Yang dikerjakan

1. **Notebook baru** `malaria_parasite_preprocessing.ipynb` (16 cells, sudah dieksekusi penuh dengan output terisi). Fokus hanya tahapan preprocessing untuk segmentasi parasit malaria (malaria = parasit *Plasmodium*, bukan virus), merombak total notebook Progress 1.

2. **Data:** 40 crop parasit dari `malaria_images/` (5 per stadium × 2 spesies: *P. falciparum*, *P. vivax*). Mask ground truth didekode langsung dari anotasi bitmap Supervisely (`mp-idb-DatasetNinja`), dipotong ke jendela crop (bbox ± 80 px).

3. **Tahapan preprocessing yang diuji** (ablation kumulatif, satu tahap ditambah per varian):
   - P0: konversi warna ke kanal Lab **b** (baseline, tanpa preprocessing lain)
   - P1: P0 + koreksi background dengan closing morfologi besar
   - P2: P1 + median filter (k=5)
   - P3: P2 + CLAHE (kontrol)
   - P4: P2 + normalisasi warna Reinhard (alternatif CLAHE)
   Segmentasi downstream: Otsu multilevel 3, polarity gelap, cleanup luas kecil (12 px).

4. **Hasil (mean Dice / IoU, 40 crop):**

   | Pipeline | Dice | IoU | Recall |
   |---|---|---|---|
   | P0_Lab_b | **0.6760** | **0.5458** | 0.5540 |
   | P1_bg_correct | 0.4403 | 0.2913 | 0.2980 |
   | P2_median | 0.4424 | 0.2940 | 0.3005 |
   | P3_clahe | 0.4844 | 0.3306 | 0.3417 |
   | P4_reinhard | 0.4532 | 0.3039 | 0.3109 |

   **Temuan:** pada crop yang sudah terpusat parasit, **Lab b saja sudah paling baik**; semua tahap tambahan justru menurunkan Dice (terutama koreksi background yang memangkas recall 0.55 → 0.30). Ini berbeda dari Progress 1 pada citra penuh (bg closing membantu, Dice 0.264): karakter crop (objek di tengah, background poligonal lebih bersih) membuat koreksi background tidak lagi diperlukan, bahkan merugikan.

5. **Visualisasi yang tersedia di notebook:** citra + histogram tiap tahap, boxplot Dice per pipeline, bar chart per spesies dan per stadium, galeri overlay best/worst (hijau = miss, merah = false positive, ungu = benar).

6. **File hasil:** `results/preprocessing_stages/per_image_metrics.csv` dan `summary.csv`.

## Perbaikan teknis selama proses

- `opencv-python-headless` dan `scikit-image` di-install ke `/home/archian/.venv` (tidak ada sebelumnya).
- Bug decoder mask: bitmap anotasi ada yang grayscale 1-channel, diperbaiki agar menangani 2 dan 3 channel.
- Bug arah koreksi background: awalnya `bg - chan` membuat parasit jadi terang dan polarity 'dark' gagal total (Dice 0.09); diperbaiki ke `chan - bg`.

## Yang belum / catatan

- Notebook Progress 1 yang lama tidak dihapus, tetap ada sebagai arsip; rombakan bersifat menambah notebook baru.
- Kesimpulan tahap preprocessing ini berlaku untuk skenario crop terpusat; untuk citra penuh (stadium tangkapan asli) hasil Progress 1 tetap rujukannya.

## 2026-11-15 (kedua): Notebook eksplorasi data + preprocessing

### Yang dikerjakan
1. Notebook baru `malaria_data_preprocessing.ipynb` (13 cells, dieksekusi penuh): bagian 1-3 eksplorasi data (tabel metadata 40 crop, grid semua crop per spesies x stadium, boxplot luas parasit, histogram grayscale rata-rata per spesies), bagian 4-5 preprocessing (5 varian kumulatif dengan citra + histogram per tahap pada 3 contoh) dan evaluasi Otsu multilevel 3 vs mask GT.
2. Hasil sama dengan notebook sebelumnya: P0 Lab b terbaik (Dice 0.676, IoU 0.546), tahap tambahan menurunkan Dice.
3. File hasil: `results/data_preprocessing/summary.csv`.

### Catatan teknis
- Histogram rata-rata perlu resize seragam (256x256) karena ukuran crop berbeda-beda.
- Ada ketidakkonsistenan label di MP-IDB: satu citra sumber bertag ganda ring + schizont stage.

### Kesimpulan
- Data 40 crop didominasi parasit besar (luas 12-23 ribu px); ring falciparum dan vivax punya profil grayscale berbeda.
- Urutan kerja "data dulu, lalu preprocessing" sesuai alur presentasi; notebook ini bisa jadi materi presentasi utama.

## 2026-11-15 (ketiga): Dataset crop dikurangi jadi 32

### Yang dikerjakan
1. Regenerasi crop: 4 citra per stadium per spesies (4 stadium x 2 spesies) = 32 file di `malaria_images/`; 40 file lama dipindah ke `malaria_images/_backup_40/`.
2. `malaria_images/metadata.csv` ditulis ulang jadi 32 baris.
3. Grid di `malaria_data_preprocessing.ipynb` diubah dari 5 kolom jadi 4 (dinamis), dan kedua notebook (`malaria_data_preprocessing.ipynb`, `malaria_parasite_preprocessing.ipynb`) dieksekusi ulang supaya semua output konsisten dengan 32 crop.

### Hasil baru (32 crop)
| Pipeline | Dice | IoU |
|---|---|---|
| P0 Lab b | 0.7029 | 0.5737 |
| P1 + koreksi background | 0.4376 | 0.2867 |
| P2 + median | 0.4433 | 0.2923 |
| P3 + CLAHE | 0.4855 | 0.3299 |
| P4 + Reinhard | 0.4667 | 0.3133 |

Kesimpulan tidak berubah: Lab b saja terbaik; tahap tambahan menurunkan Dice.

### Catatan
- Folder `_backup_40` berisi 40 crop versi lama (cadangan, tidak dipakai notebook).
- Seleksi crop: parasit terbesar per citra sumber, lalu 4 citra terbesar per grup (spesies x stadium), tanpa duplikat sumber.

## 2026-11-15 (keempat): Perbaikan visualisasi statistik

### Masalah
Boxplot per grup (spesies/stadium) tidak layak karena hanya 4 titik per grup; kotak dan whisker jadi artefak interpolasi, bukan distribusi nyata.

### Perbaikan
1. Luas parasit per spesies/stadium: diganti dot/strip plot — tiap citra satu titik + garis rata-rata + label nilai (n=16 per spesies, n=8 per stadium).
2. Dice per pipeline: boxplot dipertahankan (n=32) tetapi ditimpa titik tiap citra, outlier box dimatikan.
3. Baru: sebaran Dice per citra menurut spesies x stadium (n=4 per grup), ditampilkan sebagai titik + garis rata-rata.
4. Notebook `malaria_parasite_preprocessing.ipynb` juga diubah: boxplot Dice + titik per citra.
5. Kedua notebook dieksekusi ulang; angka tetap sama (Lab b Dice 0.7029).

### Kesimpulan
Visualisasi kini menunjukkan jumlah sampel yang sebenarnya; pembaca bisa melihat setiap citra, bukan hanya ringkasan yang menyamarkan n kecil.

## 2026-11-15 (kelima): Tambah heatmap dan histogram frekuensi

### Yang ditambahkan (notebook `malaria_data_preprocessing.ipynb`)
1. Heatmap Dice: pipeline x stadium, dan pipeline x spesies (angka di tiap sel).
2. Histogram frekuensi Dice: gabungan semua citra x pipeline (n=32x5=160) dengan garis median, dan histogram per pipeline.
3. Notebook dieksekusi ulang; total gambar di notebook 10.

### Kesimpulan
Heatmap memperlihatkan Lab b konsisten tertinggi di semua stadium dan kedua spesies, sedangkan P1-P4 makin buruk di stadium kecil (ring).
