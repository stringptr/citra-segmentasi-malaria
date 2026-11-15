# Progress: Rombak Total Notebook Preprocessing

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
1. Luas parasit per spesies/stadium: diganti dot/strip plot, tiap citra satu titik + garis rata-rata + label nilai (n=16 per spesies, n=8 per stadium).
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

## 2026-11-16: Data dibaca per stadium dulu, gabungan 32 di akhir

### Perubahan struktur `malaria_data_preprocessing.ipynb` (28 cells, dieksekusi penuh, 16 gambar)
1. **Bagian 2, per stadium dipisah.** Tiap stadium punya sel sendiri (`plot_stage(...)`): 4 crop *P. falciparum* di baris atas, 4 crop *P. vivax* di baris kedua, lalu histogram intensitas grayscale stadium itu (garis tipis = satu crop, area abu-abu = gabungan 4 crop, garis putus-putus = rata-rata intensitas).
2. **Bagian 2.5, ringkasan per stadium:** n, luas parasit, rata-rata dan std intensitas, persen piksel gelap per stadium x spesies (`results/data_preprocessing/ringkasan_per_stadium.csv`).
3. **Bagian 3, gabungan 32** seperti sebelumnya: grid 4x8 crop, dot plot luas parasit, histogram gabungan per spesies dan keseluruhan.
4. **Bagian 5, evaluasi per stadium:** Dice Otsu multilevel 3 dihitung per stadium (n=8), tabel `dice_per_stadium.csv`, plus histogram Dice per stadium dan histogram per spesies x stadium.
5. **Bagian 6, gabungan 32:** tabel ringkasan, boxplot, dot plot per kelompok, heatmap, histogram frekuensi (sama seperti versi sebelumnya).
6. **Bagian 4 (preprocessing):** demo tahapan tidak lagi 3 contoh; kini keempat stadium dipakai (ring, trophozoite, schizont, gametocyte, satu contoh *P. falciparum* masing-masing), jadi trophozoite ikut tampil walau stadium itu paling sulit disegmentasi.
7. Jumlah gambar naik dari 10 menjadi 17.

### Hasil Dice per stadium (rata-rata 8 citra)
| Stadium | P0 Lab b | P1 bg | P2 median | P3 CLAHE | P4 Reinhard |
|---|---|---|---|---|---|
| ring | 0.7156 | 0.4478 | 0.4653 | 0.4987 | 0.4724 |
| trophozoite | 0.5591 | 0.3969 | 0.3917 | 0.4254 | 0.4183 |
| schizont | 0.7279 | 0.4418 | 0.4508 | 0.4983 | 0.4634 |
| gametocyte | 0.8091 | 0.4639 | 0.4655 | 0.5195 | 0.5128 |

Gabungan 32 citra tetap: P0 Lab b Dice 0.7029, IoU 0.5737.

### Kesimpulan
- Lab b tertinggi di keempat stadium; semua tahap tambahan konsisten menurunkan Dice.
- Dice Lab b paling tinggi di gametocyte (0.809), paling rendah di trophozoite (0.559). Jarak Lab b ke varian berikutnya paling lebar di gametocyte (0.345), paling sempit di trophozoite (0.167).
- Trophozoite sulit untuk semua varian sekaligus, bukan hanya untuk satu varian.

### Catatan
- `ringkasan_per_stadium.csv` dan `dice_per_stadium.csv` adalah file hasil baru di `results/data_preprocessing/`.
- Ketidakkonsistenan label MP-IDB masih terlihat: crop ring falciparum nomor 1 dan 3 berasal dari citra sumber yang juga bertag schizont.

## 2026-11-16 (kedua): Histogram dipisah + 5 metode segmentasi

### Perubahan notebook `malaria_data_preprocessing.ipynb` (42 cells, 25 gambar)
1. **Histogram per stadium dipisah** dari tampilan crop. Tiap stadium kini punya dua figure: `plot_stage(st)` (8 crop saja) dan `plot_stage_hist(st)` (histogram 13x4.4 inci, dua panel spesies, garis rata-rata dan median).
2. **Bagian 5 baru: 5 metode segmentasi** pada kanal Lab b citra asli, semua dengan cleanup objek < 12 px:
   - M1 pixel if-else (`kanal < 115`, ambang tetap)
   - M2 Otsu satu ambang
   - M3 Otsu multilevel 3 (metode yang dipakai di evaluasi preprocessing)
   - M4 adaptive threshold (mean, blok 35, C=5)
   - M5 k-means (3 klaster intensitas, klaster tergelap = parasit)
3. Tabel Dice per metode x stadium, sapuan ambang tetap 95-140 (untuk membuktikan 115 pilihan terbaik), histogram Dice per metode x stadium, dan visual 28 panel (4 stadium x [Lab b, GT, 5 mask]).
4. Tabel gabungan 32 citra kini punya precision dan recall per metode.
5. Jumlah gambar naik dari 17 menjadi 25.

### Hasil metode segmentasi (gabungan 32 citra, kanal Lab b)
| Metode | Dice | IoU | Precision | Recall |
|---|---|---|---|---|
| M2 Otsu satu ambang | **0.7948** | **0.6802** | 0.8358 | 0.7533 |
| M5 k-means | 0.7323 | 0.6073 | 0.9780 | 0.6158 |
| M3 Otsu multilevel 3 | 0.7029 | 0.5737 | 0.9828 | 0.5822 |
| M1 pixel if-else (115) | 0.4820 | 0.3725 | 0.5163 | 0.6270 |
| M4 adaptive threshold | 0.3660 | 0.2288 | 0.7833 | 0.2442 |

Dice Otsu satu ambang per stadium: ring 0.805, trophozoite 0.686, schizont 0.827, gametocyte 0.861.

### Kesimpulan
- Ambang otomatis mengalahkan ambang tetap. Ambang tetap terbaik hasil sapuan 95-140 adalah 115 (Dice 0.482), jadi keunggulan Otsu bukan karena konstanta yang buruk.
- Otsu multilevel 3 dan k-means sangat presisi (0.98) tetapi recall rendah (0.58 / 0.62): parasit tipis ikut terpotong. Otsu satu ambang lebih seimbang.
- Adaptive threshold terburuk di semua stadium: yang tersisa hanya tepi tekstur, badan parasit hilang (recall 0.24).
- Urutan metode sama di keempat stadium, jadi kesimpulan ini tidak bergantung pada satu stadium saja.

### Catatan / langkah berikutnya
- Evaluasi preprocessing (Bagian 6) masih memakai Otsu multilevel 3. Karena Otsu satu ambang lebih tinggi, peringkat varian preprocessing perlu dicek ulang dengan Otsu tunggal sebelum diklaim final.
- File hasil baru: `results/data_preprocessing/dice_metode_per_stadium.csv` dan `summary_metode.csv`.

## 2026-11-16 (ketiga): Label gambar lebih rinci, em dash dibersihkan, bahasa dirapikan

### Perubahan
1. **Label crop per stadium** kini tiga baris: nama file, luas parasit dalam ribu piksel, dan nama citra sumber. Baris atas tetap 4 crop P. falciparum, baris bawah 4 crop P. vivax.
2. **Grid gabungan 32 crop**: judul tiap panel memuat nama file dan luas parasit, label spesies dipindah ke atas blok kolom, label stadium ke sisi kiri, jadi tidak lagi menimpa gambar.
3. **Histogram per stadium**: legenda dipindah ke bawah panel, dua kolom, berisi nama file tiap crop plus nilai rata-rata dan median, sehingga tidak menutupi kurva.
4. **Demo preprocessing**: judul tiap panel memakai nama tahap yang jelas (koreksi background, median 5x5, CLAHE, Reinhard) dan suptitle memuat nama file, spesies, stadium, luas parasit, serta citra sumber.
5. **Visual metode segmentasi**: tiap panel memuat nama metode dan parameternya plus Dice dan IoU, sedangkan panel pertama memuat nama file, stadium, dan luas parasit.
6. **Boxplot metode**: label sumbu-x dibungkus dua baris supaya tidak terpotong.
7. **Histogram per spesies dan stadium**: ditambah legenda varian preprocessing yang sebelumnya tidak ada.
8. Semua em dash dan en dash dihapus dari teks notebook maupun judul gambar. Isi PROGRESS.md juga dibersihkan.
9. Bahasa markdown ditulis ulang supaya lebih wajar, tanpa mengubah angka atau kesimpulan.

### Catatan
- Angka tidak berubah: Lab b Dice 0.7029 (gabungan 32), per stadium 0.7156 / 0.5591 / 0.7279 / 0.8091, metode segmentasi Otsu 0.7948 sampai adaptive 0.3660.
- Jumlah gambar tetap 25.
