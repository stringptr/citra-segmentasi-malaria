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

## 2026-11-16 (keempat): Dokumen penjelasan notebook

### Yang dibuat
- `docs/penjelasan_notebook_data_preprocessing.md`: penjelasan lengkap isi notebook dalam bahasa Indonesia, 14 bagian.
  Isinya: gambaran besar dan cara menjalankan, asal data dan cara mask GT didekode, penjelasan tiap bagian notebook (per stadium, gabungan, preprocessing, lima metode segmentasi, evaluasi), rumus Dice/IoU/precision/recall, tabel semua parameter, daftar file hasil CSV, temuan utama, keterbatasan, skrip reproduksi mandiri, dan daftar istilah.
- Skrip reproduksi di dokumen sudah diuji: menghasilkan Dice gabungan 0.7948, sama dengan angka Otsu satu ambang di notebook.

### Catatan
- Angka di dokumen diambil dari CSV hasil notebook, bukan diketik ulang dari ingatan.
- Semua em dash dihapus, istilah asing dijelaskan dalam kalimat terpisah.

## 2026-11-16 (kelima): Penanda ground truth di semua gambar dan koreksi arti anotasi

### Permintaan
Pengguna sulit membedakan sel darah merah, sel darah putih, dan parasit di gambar, jadi minta parasit ditandai sesuai ground truth di semua gambar.

### Temuan penting
1. **Anotasi MP-IDB adalah sel darah merah terinfeksi, bukan badan parasit.** Bukti: mask stadium ring luasnya 18 sampai 23 ribu piksel dan mengisi sekitar 75 persen kotak pembatasnya, sedangkan parasit ring hanya sepersekian ukuran sel. Jadi seluruh angka Dice dan IoU di notebook ini sebenarnya mengukur segmentasi sel terinfeksi.
2. **Lima pasang crop duplikat, hanya 27 sel unik dari 32 crop.** Pasangan itu: falciparum ring 1 dengan schizont 1, ring 3 dengan schizont 2, ring 4 dengan schizont 3, trophozoite 2 dengan gametocyte 3, dan vivax ring 1 dengan vivax gametocyte 2. Penyebabnya pemilihan crop mengambil objek terbesar tanpa melihat stadium, padahal nama file sumber memuat dua stadium.
3. Kolom `parasite_area_px` di `metadata.csv` menyimpan luas sel terinfeksi, bukan luas parasit.

### Yang diubah di notebook
1. Bagian baru **1.1** berisi penjelasan apa yang sebenarnya dianotasi, tabel ciri visual sel darah merah sehat, sel terinfeksi, sel darah putih, dan parasit, plus figure contoh satu crop per stadium dengan perbesaran 4 kali.
2. Contoh figure itu sengaja dipilih yang morfologinya jelas: `falciparum_ring_2`, `falciparum_trophozoite_1`, `falciparum_schizont_3`, `falciparum_gametocyte_1`. Crop pertama per stadium tidak dipakai karena ring 1 justru tampak seperti schizont.
3. Helper baru `gt_overlay` (area hijau transparan 0.15 plus garis hijau) dan `gt_contour` (garis saja). Dipakai di tampilan crop per stadium, grid 32 citra, demo preprocessing, dan visual lima metode segmentasi.
4. Istilah "luas parasit" diganti "luas sel terinfeksi" di judul gambar dan tabel. Kolom CSV `ringkasan_per_stadium.csv` ikut berubah menjadi `luas_sel_terinfeksi_ribu_px`.
5. Kesimpulan menambah dua butir: arti penanda dan catatan lima pasang crop duplikat.
6. Baris prosa yang menyelip di sel import dihapus, karena membuat notebook gagal dieksekusi lewat nbconvert.

### Angka
Tidak berubah. Lab b gabungan Dice 0.7029, IoU 0.5737. Per stadium 0.7156 / 0.5591 / 0.7279 / 0.8091. Otsu satu ambang 0.7948.

### File yang berubah
- `malaria_data_preprocessing.ipynb` (44 sel, 26 gambar, tanpa error)
- `docs/penjelasan_notebook_data_preprocessing.md` (koreksi arti ground truth, bagian 1.1, bagian 2.5, temuan, keterbatasan, glosarium)
- `results/data_preprocessing/ringkasan_per_stadium.csv` (nama kolom)
- `PROGRESS.md`

## 2026-11-16 (keenam): Video MP4 1920x1080 bersuara

### Hasil
- `video_segmentasi_malaria.mp4`, 1920x1080, 30 fps, H.264 + AAC, durasi 8 menit 1 detik, 16 scene.
- Disimpan di root folder Project (`/home/archian/Kuliah/Semester5/ADCB/Project/`), bukan di repo, supaya tidak menambah 47 MB ke git.

### Isi video
1. Judul, 2. masalah yang ingin diselesaikan, 3. inti MP-IDB dan kenapa segmentasi dipilih, 4. data 32 crop, 5. arti anotasi sel terinfeksi, 6. ciri sel darah merah, sel darah putih, dan parasit, 7. kesulitan per stadium, 8. lima varian preprocessing, 9. hasil preprocessing, 10. lima metode segmentasi, 11. hasil metode, 12. Dice per stadium, 13. kenapa tanpa train dan test serta protokol yang lebih jujur, 14. catatan data duplikat, 15. kesimpulan, 16. penutup.

### Cara dibuat
- Slide 1920x1080 disusun dari data dan citra notebook (bukan tangkapan layar), memakai Carlito.
- Animasi: kamera zoom dan geser bergantian, elemen masuk bertahap (fade dan naik 16 px), progress bar di bawah.
- Narasi bahasa Indonesia memakai suara neural `id-ID-GadisNeural`. Tiap kalimat disintesis terpisah dengan rate dan pitch berbeda (rate 0 sampai +5 persen, pitch -2 sampai +4 Hz), jeda antar kalimat 0,26 detik, supaya tidak datar.
- Skrip di `/tmp/opencode/video/`: `scenes.py` (slide dan elemen), `render.py` (animasi, kamera, encode), `make_audio2.py` (narasi), `build_assets.py` (grafik dan panel citra).

### Catatan
- Video ini belum diuji dengan penonton; penilaian intonasi dan tempo masih subjektif.
- Angka di video sama dengan notebook: Lab b 0.7029, per stadium 0.7156 / 0.5591 / 0.7279 / 0.8091, Otsu satu ambang 0.7948.

## 2026-11-16 (ketujuh): Bagian terbaik vs terburuk di notebook

### Permintaan
Menambahkan perbandingan metode dan preprocessing terbaik dengan yang terburuk, lalu menjelaskan kenapa yang terburuk bisa buruk. Diminta masuk ke notebook dan PROGRESS.

### Yang ditambahkan
Bagian baru **8. Terbaik dan terburuk: apa bedanya** (Kesimpulan bergeser jadi bagian 9):
1. Tabel semua lima metode dengan Dice, IoU, precision, recall, rasio luas mask terhadap ground truth, jumlah komponen, dan fraksi piksel dekat batas. Disimpan ke `results/data_preprocessing/perbandingan_metode.csv`.
2. Figure kasus terburuk adaptive per stadium, satu citra unik tiap stadium, dibandingkan Otsu pada citra yang sama. Judul memuat Dice dan rasio luas.
3. Grafik tiga penyebab: rasio luas 0.89 lawan 0.31, recall 0.75 lawan 0.25, komponen 14 lawan 45.
4. Tabel dan contoh visual P0 lawan P1 untuk preprocessing, disimpan ke `perbandingan_preprocessing.csv`.

### Temuan
- **Adaptive buruk bukan karena mask hanya berupa garis tepi.** Fraksi piksel dekat batas hanya 0.08, sama rendahnya dengan Otsu. Penyebabnya, ambang lokal membandingkan piksel dengan rata rata blok 35 piksel, sehingga di dalam sel yang tebal hanya bagian paling gelap yang lolos. Luas yang tertangkap 31 persen, mask pecah jadi 45 komponen, recall 0.25.
- **Precision adaptive 0.83 terlihat tinggi tetapi menyesatkan**, karena bintik yang lolos hampir semua berada di dalam sel. Yang gagal adalah cakupan.
- **Kasus terburuk ekstrem:** `falciparum_trophozoite_2.png` hanya tertangkap 0.07 luas ground truth, Dice 0.127, padahal Otsu 0.789 di citra yang sama.
- **P1 koreksi background** menurunkan recall 0.58 ke 0.29 dan rasio luas 0.59 ke 0.33, karena closing morfologi menganggap badan sel sebagai latar lalu menguranginya. Contoh `falciparum_gametocyte_2.png`: Dice 0.843 turun ke 0.517, luas 0.73 turun ke 0.36.
- Angka precision dan recall di bagian ini dirata-ratakan per citra, sedangkan tabel metode di Bagian 7 menjumlahkan piksel. Perbedaan kecil ini dijelaskan di 8.2 supaya tidak bingung.

### Catatan
- Figure contoh memilih citra dengan sumber berbeda tiap stadium, supaya tidak menampilkan sel duplikat yang sama dua kali.
- Butir kesimpulan tentang adaptive ikut diperbaiki: bukan 'hanya tepi tekstur', tetapi mask terlalu hemat piksel (luas 0.31, 45 komponen, recall 0.25).
- Notebook dieksekusi ulang: 53 sel, 29 gambar, tanpa error. Angka lama tidak berubah: Otsu 0.7948, adaptive 0.3660, P0 0.7029, P1 0.4376.

### File yang berubah
- `malaria_data_preprocessing.ipynb`
- `results/data_preprocessing/perbandingan_metode.csv` (baru)
- `results/data_preprocessing/perbandingan_preprocessing.csv` (baru)
- `PROGRESS.md`

## 2026-11-18 (kedua): Protokol 2 train / 2 test dijalankan di notebook

### Yang diubah
1. **Bagian baru 4.1** di `malaria_data_preprocessing.ipynb`: pembagian tetap 2 train / 2 test. Tiap grup spesies x stadium berisi empat crop, file `_1` dan `_2` jadi train dan `_3` dan `_4` jadi test, 16 citra per sisi. Nomor dibaca dari nama file, bukan urutan baris metadata. Ada assert yang menghentikan eksekusi kalau ada grup yang namanya bukan berakhiran 1 sampai 4.
2. **Sel baru** menulis `results/data_preprocessing/split_train_test.csv`: filename, spesies, stadium, citra sumber, split, dan penanda `sel_duplikat`.
3. **Bagian 5 (lima metode segmentasi) ikut dipisah.** Ambang tetap pixel if-else kini dipilih dari train lewat sapuan 95 sampai 140, bukan dari seluruh 32 citra.
4. **Bagian 6, 7, dan 8.3 (rantai preprocessing) diubah**: tiap tabel dan figure memuat train dan test terpisah, bukan angka gabungan 32 citra. Aturan pemilihan: varian terbaik dipilih hanya dari train, angka test dilaporkan apa adanya.
5. **Bagian 8.1 dan 8.2 sengaja dibiarkan memakai gabungan 32 citra**, karena bagian itu diagnosis kenapa adaptive gagal, bukan klaim performa. Ada catatan protokol di teksnya.
6. **Sel baru** menulis `results/data_preprocessing/per_image_dice_test.csv`: Dice tiap citra test untuk lima varian dan lima metode, plus selisih berpasangan terhadap P0.
7. Notebook kini 56 sel dan 29 gambar, dijalankan penuh tanpa error.

### Hasil train dan test

Preprocessing, segmentasi Otsu multilevel 3, Dice train / test / gabungan 32:

| Varian | Train | Test | Gabungan 32 |
|---|---|---|---|
| P0_Lab_b | 0.6832 | 0.7226 | 0.7029 |
| P1_bg_correct | 0.4102 | 0.4650 | 0.4376 |
| P2_median | 0.4091 | 0.4775 | 0.4433 |
| P3_clahe | 0.4584 | 0.5126 | 0.4855 |
| P4_reinhard | 0.4368 | 0.4967 | 0.4667 |

Metode segmentasi pada kanal Lab b, Dice train / test:

| Metode | Train | Test |
|---|---|---|
| Otsu satu ambang | 0.7518 | 0.8379 |
| k-means, 3 klaster | 0.6845 | 0.7562 |
| Otsu multilevel 3 | 0.6832 | 0.7226 |
| Pixel if-else, ambang 130 | 0.4950 | 0.3864 |
| Adaptive, blok 35, C 5 | 0.3125 | 0.4194 |

### Temuan
- Peringkat preprocessing sama di train dan di test: P0 terbaik, lalu P3, P4, P2, P1. Kesimpulan "Lab b saja sudah paling baik" bertahan di kedua sisi.
- Hanya satu citra test, `falciparum_trophozoite_4.png`, yang membuat P1 sampai P4 mengalahkan P0. Jadi 15 dari 16 citra test tetap menurun, dengan rata-rata selisih sekitar -0.21 sampai -0.26 Dice.
- **Sapuan ambang di train memilih 130 (train 0.4950), bukan 115.** Tetapi di test ambang 130 hanya 0.3864, sementara 115 mencapai 0.5627. Ambang yang menang di train dengan 16 citra tidak ikut menang di test. Ini contoh konkret pemilihan yang gagal pindah ke test.
- Pixel if-else ambang 130 punya precision 0.27 dan recall 0.92: ambangnya longgar, mask meluber, jadi Dice-nya rendah meski recall tinggi.
- Urutan metode sama di train dan test, kecuali di test adaptive (0.4194) menyalip pixel if-else (0.3864). Di train adaptive tetap terburuk.
- **Jaring pengaman lolos.** Dice gabungan 32 citra tetap sama dengan laporan lama: P0 0.7029, P1 0.4376, P2 0.4433, P3 0.4855, P4 0.4667, Otsu satu ambang 0.7948, Otsu multilevel 3 0.7029, adaptive 0.3660. Artinya train dan test memang 32 citra yang sama, jadi pembagiannya tidak mengubah data.

### Catatan
- Bug yang ketemu saat menjalankan: sel `dice_iou` dan `_clean` ikut terhapus saat sumber sel metode ditulis ulang, sudah dikembalikan sebelum run final.
- k-means bergeser sedikit antar versi OpenCV: 0.7214 di CSV lama, 0.7401 pada run dengan OpenCV 4.14 di workspace ini. Semua angka lain identik. Ini perlu disebut sebagai keterbatasan kecil.
- Dua dari 16 citra test memakai sel yang juga muncul di train: `falciparum_ring_3` dengan `falciparum_schizont_2`, dan `falciparum_trophozoite_2` dengan `falciparum_gametocyte_3`. Keduanya tercatat di `split_train_test.csv` pada kolom `sel_duplikat`.
- `docs/penjelasan_notebook_data_preprocessing.md` yang disebut di catatan lama tidak ada di repo ini, jadi belum ikut diperbarui.

### File yang berubah
- `malaria_data_preprocessing.ipynb` (56 sel, 29 gambar)
- `results/data_preprocessing/split_train_test.csv` (baru)
- `results/data_preprocessing/per_image_dice_test.csv` (baru)
- `results/data_preprocessing/summary.csv`
- `results/data_preprocessing/dice_per_stadium.csv`
- `results/data_preprocessing/summary_metode.csv`
- `results/data_preprocessing/dice_metode_per_stadium.csv`
- `results/data_preprocessing/perbandingan_preprocessing.csv`
- `results/data_preprocessing/perbandingan_metode.csv`
- `PROGRESS.md`, `session.md`

## 2026-11-18 (ketiga): Bagian 6 perbandingan menyeluruh

Bagian ini menjawab tiga hal yang tidak bisa dijawab rantai P0 sampai P4: apakah Lab b lebih baik daripada grayscale, apakah tiap langkah masih berguna kalau berdiri sendiri, dan apakah tiap langkah berguna ketika langkah lain tetap ada. Posisinya sebelum evaluasi rantai per stadium, sesuai permintaan.

### Yang diubah
1. **Bagian 6 baru** di `malaria_data_preprocessing.ipynb`, tujuh sel: pengantar dan daftar varian, sel perhitungan 14 varian, tabel hasil, tabel pembanding Otsu satu ambang, dan sel penyimpan CSV.
2. **Penomoran bagian lama digeser**: evaluasi preprocessing per stadium 6 menjadi 7, gabungan 32 citra 7 menjadi 8, terbaik dan terburuk 8 menjadi 9, kesimpulan 9 menjadi 10. Semua rujukan "Bagian N" di teks ikut diperbaiki.
3. **Empat belas varian** dihitung dengan segmentasi yang sama: 2 baseline grayscale, 4 varian tunggal di atas Lab b, 4 rantai kumulatif P0 sampai P3, dan 4 leave one out dari rantai penuh P3.
4. **Selisih berpasangan dan uji Wilcoxon** ditambahkan per citra, bukan hanya rata-rata kelompok.
5. **Kesimpulan (Bagian 10)** ditambah empat butir: perbandingan grayscale, varian tunggal, leave one out, dan ketergantungan pada metode segmentasi.
6. Kedua baseline grayscale dihitung: rata-rata RGB (dipakai sebagai baseline utama) dan berbobot `cv2` (pembanding, karena itu yang dipakai histogram Bagian 2).

### Hasil, Otsu multilevel 3

| Varian | Train | Test | 32 citra | Selisih vs pembanding | p |
|---|---|---|---|---|---|
| B1 grayscale rata-rata RGB | 0.5612 | 0.6616 | 0.6114 | -0.0915 vs P0 | 0.008 |
| B2 grayscale berbobot cv2 | 0.5980 | 0.7114 | 0.6547 | -0.0482 vs P0 | 0.100 |
| S1 koreksi background saja | 0.4102 | 0.4650 | 0.4376 | -0.2653 vs P0 | < 0.001 |
| S2 median saja | 0.6922 | 0.7055 | 0.6988 | -0.0041 vs P0 | 0.070 |
| S3 CLAHE saja | 0.5543 | 0.6116 | 0.5830 | -0.1199 vs P0 | < 0.001 |
| S4 Reinhard saja | 0.6770 | 0.7378 | 0.7074 | +0.0045 vs P0 | 0.904 |
| P0 kanal Lab b | 0.6832 | 0.7226 | 0.7029 | acuan | - |
| P3 rantai penuh | 0.4584 | 0.5126 | 0.4855 | -0.2174 vs P0 | < 0.001 |
| L tanpa koreksi background | 0.5443 | 0.6146 | 0.5795 | +0.0940 vs P3 | < 0.001 |
| L tanpa median | 0.4641 | 0.5188 | 0.4914 | +0.0060 vs P3 | 0.489 |
| L tanpa CLAHE | 0.4091 | 0.4775 | 0.4433 | -0.0421 vs P3 | < 0.001 |

### Temuan
- **Lab b lebih baik daripada grayscale, tetapi jaraknya bergantung rumus.** Selisih +0.0915 terhadap rata-rata RGB dengan p 0.0079. Terhadap grayscale berbobot `cv2` hanya +0.0482 dan tidak signifikan (p 0.0998).
- **Koreksi background merugikan karena langkahnya sendiri**, bukan karena urutannya. Berdiri sendiri di atas Lab b hasilnya 0.4376, identik dengan P1. Ini bukti paling bersih untuk klaim itu.
- **Median dan Reinhard netral kalau berdiri sendiri.** Median 0.6988 (p 0.070), Reinhard 0.7074 (p 0.904) terhadap P0. Keduanya baru turun ketika ditempel setelah koreksi background.
- **CLAHE berguna di dalam rantai, merugikan kalau sendirian.** Sendiri 0.583, tetapi membuangnya dari rantai penuh menurunkan Dice ke 0.4433 (p < 0.001). Efek yang bergantung konteks.
- **Membuang koreksi background paling menolong**, +0.0940 dengan p 0.0004. Membuang median hampir tidak berpengaruh (p 0.489).
- **Peringkat bergantung metode segmentasi.** Dengan Otsu satu ambang, 10 dari 14 varian berubah peringkat, dan median sendiri (0.8013) serta Reinhard sendiri (0.8069) mengalahkan P0 (0.7948). Klaim "Lab b saja sudah paling baik" hanya berlaku untuk Otsu multilevel 3.
- **Pemeriksaan konsistensi lolos.** `S1_bg_correct` sama dengan `P1_bg_correct`, dan `L_tanpa_clahe` sama dengan `P2_median`, karena pipeline-nya memang identik. Angka gabungan 32 citra P0 sampai P4 juga tidak berubah dari laporan sebelumnya.

### Catatan
- Notebook dijalankan penuh tanpa error dengan kernel `.venv` repo (numpy 2.5.5, OpenCV 5.1.0, scipy 1.18.1). Seluruh CSV lama yang sudah di-commit tidak berubah satu angka pun setelah run ini, termasuk k-means, jadi hasilnya reprodusibel di versi OpenCV ini.
- Bagian `PROGRESS.md` sesi 18.17 sampai 19.21 sempat hilang saat pull mengambil versi Satria. Salinannya ada di `/tmp/opencode/PROGRESS-lokal.md`, belum digabungkan ke sini.
- `docs/penjelasan_notebook_data_preprocessing.md` diperbarui: bagian baru bernomor 7, nomor bagian sesudahnya digeser, tabel file hasil, temuan utama, dan keterbatasan ikut disesuaikan.

### File yang berubah
- `malaria_data_preprocessing.ipynb` (65 sel, dijalankan penuh)
- `results/data_preprocessing/perbandingan_menyeluruh.csv` (baru)
- `results/data_preprocessing/perbandingan_menyeluruh_otsu1.csv` (baru)
- `results/data_preprocessing/per_image_semua_varian.csv` (baru)
- `docs/penjelasan_notebook_data_preprocessing.md`
- `PROGRESS.md`

Tambahan kecil sesudahnya: di 6.1 dan di dokumen penjelasan ditambahkan tabel padanan "P0 sendiri sampai P4 sendiri" terhadap varian tunggal (S1 sampai S4), supaya jelas bahwa tiap langkah sudah dinilai tanpa langkah sebelumnya. Hanya teks markdown yang berubah, notebook tidak dijalankan ulang dan angkanya tidak bergeser.

## 2026-11-18 (keempat): Bagian 7 baseline dan varian tunggal

Baseline grayscale dan empat varian tunggal dipisah dari Bagian 6, karena dua kelompok itu menjawab pertanyaan yang berbeda dari rantai. Bagian 6 sekarang hanya berisi rantai P0 sampai P3 dan leave one out. Semua bagian sesudahnya digeser satu nomor: per stadium jadi 8, gabungan 32 citra jadi 9, terbaik dan terburuk jadi 10, kesimpulan jadi 11.

### Yang diubah
1. **Bagian 6 dipangkas**: judul jadi "Rantai preprocessing dan leave one out", tabel pengantar tinggal dua baris, tabel hasil dan plot titik hanya menampilkan varian rantai dan leave one out. Sel perhitungan tetap menghitung 14 varian karena Bagian 7 memakainya, dan CSV gabungan tetap lengkap.
2. **Bagian 7 baru, delapan sel**: pengantar, tabel keseluruhan, tabel per stadium train dan test, figure per stadium, figure per spesies dan stadium, heatmap, tabel Otsu satu ambang, dan figure contoh kanal dasar yang dipindah dari Bagian 6.
3. **Heatmap** varian kali stadium dan varian kali spesies, train dan test, gayanya sama dengan heatmap di Bagian 10.
4. **Rujukan nomor dirapikan**: 8.2 yang basi jadi 10.2, tabel 8.1 jadi 10.1, Bagian 8 jadi 9, Bagian 9.3 jadi 10.3 di teks Bagian 10, serta rujukan di kesimpulan.
5. Notebook kini **73 sel dan 34 gambar**, dijalankan penuh tanpa error.

### Hasil

Angka tidak bergeser dari laporan sebelumnya. Baseline Otsu multilevel 3: B1 grayscale rata-rata RGB 0.6114, B2 grayscale `cv2` 0.6547, P0 0.7029. Varian tunggal: S1 0.4376, S2 0.6988, S3 0.5830, S4 0.7074.

### Temuan
- Dengan Otsu satu ambang, **6 dari 7 varian di Bagian 7 berubah peringkat**. Hanya Reinhard sendiri yang tetap paling tinggi (0.8069). Baseline grayscale jatuh paling dalam, B1 dari 0.6114 ke 0.5568 dan B2 ke 0.5610, jadi keunggulan Lab b justru melebar di metode itu.
- Di semua stadium dan kedua sisi, B1 selalu di bawah P0. Selisih terbesar ada di stadium ring test, 0.7086 lawan 0.7960.
- `S1_bg_correct` dan `P1_bg_correct` tetap identik, sama seperti `L_tanpa_clahe` dan `P2_median`, jadi pemeriksaan konsistensi masih lolos.

### Catatan
- Verifikasi dijalankan lewat venv sementara `/tmp/opencode/vtest` (numpy 2.5.5, OpenCV 4.14.0). Angka k-means tetap 0.7401 seperti run sebelumnya di versi OpenCV ini.
- Dua CSV baru hanya ringkasan untuk Bagian 7. `perbandingan_menyeluruh.csv` dan `per_image_semua_varian.csv` tidak dipecah supaya tetap satu sumber untuk kedua bagian.

### File yang berubah
- `malaria_data_preprocessing.ipynb` (73 sel, 34 gambar)
- `results/data_preprocessing/perbandingan_baseline_tunggal.csv` (baru)
- `results/data_preprocessing/dice_baseline_tunggal_per_stadium.csv` (baru)
- `PROGRESS.md`, `session.md`

## 2026-11-19: Deck presentasi 16 slide

Dibuat dari notebook terbaru setelah commit Satria `8bf5e09`, jadi penomoran mengikuti 11 bagian dan angka baseline serta varian tunggal diambil dari `perbandingan_baseline_tunggal.csv`.

### Isi deck `docs/presentation-final.pptx`
1. Judul, masalah (anotasi sel bukan parasit), data 32 crop dengan montase semuanya.
2. Metode: rantai P0 sampai P4, lima metode segmentasi dengan contoh mask, protokol 2 train 2 test.
3. Hasil: tabel rantai, leave one out, baseline grayscale, varian tunggal dengan heatmap, ketergantungan pada metode segmentasi, tabel lima metode, Dice per stadium.
4. Temuan, batasan, kesimpulan.
5. Catatan pembicara di tiap slide menyebut file CSV sumber angkanya.

### Verifikasi
- Semua angka diambil dari CSV, tidak ada yang diketik dari prosa.
- OOXML lolos `validate.py` dari skill pptx.
- Pemeriksaan geometri sendiri: tidak ada bentuk keluar slide, tidak ada kotak teks meluap, tidak ada tumpang tindih.
- Render visual memakai renderer sendiri dari geometri PPTX, karena LibreOffice tidak terpasang di mesin ini. Jadi tampilan di PowerPoint bisa sedikit berbeda pada pembulatan teks.

### Catatan
- File `docs/presentation-final.pptx` belum di-commit.
- Gambar diambil dari output tersimpan notebook (110 dpi), bukan diekspor ulang. Pada slide dengan figure lebar, teks di dalam gambar kecil dan sebaiknya dibaca dari CSV atau dari notebook.

### Tema disesuaikan dengan UI portfolio
- Deck baru `docs/presentation-final-green.pptx`, 16 slide, tema neobrutalis seperti web portfolio: latar putih bertitik, border tinta 2px, bayangan keras 6px, label mono huruf besar berspasi, judul Space Grotesk.
- Aksen merah `#e10600` diganti hijau `#0b7f3b`, tint `#e7f5ec`. Slide judul dan penutup memakai latar tinta `#111827`.
- Palet dan gaya diambil dari `src/index.css` di proyek portfolio (kelas `card`, `label`, `chip`).
- Font Space Grotesk dan JetBrains Mono sudah terpasang di sistem, jadi tidak perlu menyematkan font.
- `docs/presentation-final.pptx` (tema lama) tetap ada sebagai pembanding.

### Revisi tema: putih penuh, diagram alur, gambar besar
- Semua slide kini berlatar putih bergrid titik, termasuk judul dan penutup. Tidak ada slide gelap.
- Slide 2 baru berisi diagram alur enam tahap. Mermaid CLI tidak terpasang di mesin ini, jadi diagram digambar sebagai bentuk native PowerPoint agar tajam dan muat satu slide; sumber Mermaid-nya disimpan di `docs/progress.mmd` dan sudah dirender lewat kroki untuk memastikan alurnya terbaca.
- Gambar yang sebelumnya berbagi slide dengan tabel dipindah ke slide sendiri dengan lebar sampai 12,1 inci. Grid mask 4 stadium dipecah jadi dua slide, ring dan trophozoite lalu schizont dan gametocyte.
- Deck kini 22 slide: judul, diagram, masalah, data, montase, varian, panel varian, metode, dua slide mask, protokol, rantai, leave one out, baseline, kanal, varian tunggal, peringkat, metode hasil, per stadium, temuan, batasan, kesimpulan.
- Catatan pembicara tetap ada di semua slide dan menyebut CSV sumbernya.


## 2026-11-19 (kedua): Deck lengkap, semua figure notebook masuk

Deck baru `docs/presentation-lengkap.pptx`, 50 slide 16:9, tema putih aksen hijau yang sama. Deck 22 slide sebelumnya tetap ada sebagai versi pendek.

### Isi
- 34 figure notebook dipetakan ke 35 slide (`cell5`, `cell9` sampai `cell68`, termasuk histogram per stadium dan histogram frekuensi Dice). Satu figure mask 4 stadium dipecah dua slide.
- Bagian 6 dan 7 notebook kini lengkap: tabel rantai P0 sampai P4, grafik leave one out, tabel leave one out dengan nilai p, tabel baseline grayscale, bar tujuh varian per stadium, grafik tiga kanal per spesies dan stadium, heatmap empat panel, dan contoh visual kanal.
- Tiap slide figure memakai satu visual besar dengan dua sampai empat butir penjelasan. Slide 3 memuat peta slide per bagian.
- Catatan pembicara tiap slide menyebut file CSV sumber.

### Angka baru yang muncul saat pemeriksaan
- Median sendiri mengungguli P0 di 4 dari 8 kelompok spesies x stadium (`dice_baseline_tunggal_per_stadium.csv`), meski gabungan 32 citra P0 unggul tipis 0,7029 lawan 0,6988.
- Di trophozoite test, grayscale cv2 0,6756 mengalahkan P0 0,5257.
- P0 di atas 0,8 pada 7 dari 16 citra di train dan 7 di test (`per_image_semua_varian.csv`).
- Karena temuan itu, butir 3 slide Temuan diberi catatan bahwa "median netral" hanya berlaku untuk gabungan 32 citra.

### Verifikasi
- `validate.py` skill pptx lolos.
- Pemeriksaan geometri sendiri: tidak ada bentuk keluar slide, teks meluap, atau tumpang tindih.
- Pratinjau dirender dari geometri PPTX karena LibreOffice tidak terpasang. Pembungkusan teks di PowerPoint bisa sedikit berbeda.

### Catatan
- 50 slide terlalu panjang untuk 15 menit. Untuk presentasi, slide per stadium (8 sampai 15, 19 sampai 22) bisa dijadikan lampiran.
- Belum ada ekstraksi fitur di notebook saat itu. Bagian 11 hanya segmentasi dan metrik. Fitur bentuk atau tekstur untuk klasifikasi belum dikerjakan (dikerjakan 2026-11-24).
- File belum di-commit.

## 2026-11-24: Bagian 11 area putih dan Bagian 12 ekstraksi fitur + klasifikasi

### Git
- `git pull --ff-only` di branch `feat/ian`: `Already up to date`. Tidak ada commit baru di remote.
- `feat/ian` sudah 14 commit di depan `origin/main`, dan `origin/main` tidak punya commit yang belum ada di branch ini. Tidak ada merge.
- Perubahan lokal dari sesi sebelumnya tetap utuh: `PROGRESS.md`, notebook, 32 PNG, dan dua CSV di `results/preprocessing_stages`.

### Bagian 11: penanganan area putih
- Kriteria area kosong: `L >= 240` di Lab dan warna hampir netral, `|a-128| <= 10` serta `|b-128| <= 10`.
- Delapan crop terkena, semuanya P. vivax. Terluas `vivax_schizont_2` 50,0 persen luas crop, lalu `vivax_trophozoite_3` 38,8 persen.
- Pengisian memakai `cv2.inpaint` metode Telea radius 5. Hanya `vivax_schizont_1` yang 11,4 persen area putihnya menimpa sel, sisanya di bawah 0,2 persen.
- Dice P0 gabungan 32 citra 0,7029 menjadi 0,7004. Pada delapan citra itu 0,4965 menjadi 0,4866. Empat citra tidak berubah, empat turun 0,02 sampai 0,03.
- Kesimpulan: pengisian bukan cara menaikkan Dice, karena area putih hampir seluruhnya di latar. Bagian 5 sampai 10 tetap memakai citra asli, hanya Bagian 12 yang memakai citra terisi.
- File baru: `results/data_preprocessing/area_putih.csv` dan `area_putih_dice.csv`.

### Bagian 12: ekstraksi fitur dan klasifikasi
- 24 fitur per crop, diukur dari mask ground truth: 7 bentuk, 10 warna termasuk kontras terhadap cincin latar, 7 tekstur (GLCM, Laplacian, entropi).
- Akurasi cross validation, baseline 0,500 untuk spesies dan 0,250 untuk stadium:

| Target | Model | LOO | GroupKFold | LOGO |
|---|---|---|---|---|
| Spesies | LogReg | 0,938 | 0,938 | 0,938 |
| Spesies | RF | 0,969 | 0,938 | 0,969 |
| Stadium | LogReg | 0,250 | 0,438 | 0,375 |
| Stadium | RF | 0,250 | 0,500 | 0,406 |

- Spesies mudah, stadium sulit. Rentang stadium 0,250 sampai 0,500 dengan baseline 0,250. LOGO dipakai sebagai rujukan karena 32 crop hanya mewakili 27 sel.
- Fitur bentuk saja memberi 0,719 untuk spesies, sedangkan warna dan tekstur saja 0,938. Dua fitur teratas `a_rata` dan `b_rata`, jadi keunggulan spesies sebagian besar ciri batch pewarnaan, bukan morfologi.
- Stadium per spesies: P. falciparum 0,562, P. vivax 0,250. Dengan 16 citra per spesies angka itu belum layak dipercaya.
- Confusion matrix stadium: schizont 6 dari 8 ditebak ring, karena mask yang dipakai adalah sel terinfeksi, bukan parasit.
- File baru: `fitur_per_crop.csv`, `klasifikasi_fitur.csv`, dan `klasifikasi_kelompok_fitur.csv`.

### Perubahan kode
- Notebook 73 sel menjadi 85 sel, dijalankan penuh tanpa error dalam 73,7 detik.
- Kesimpulan bergeser dari Bagian 11 ke Bagian 13. Daftar isi di sel 0 ditambah dua butir, dan kesimpulan dapat satu butir baru.
- `requirement.txt` ditambah `scikit-learn`, karena notebook sekarang memakainya dan sebelumnya belum terpasang.
- Satu perbaikan pada sel ringkasan fitur: `groupby(...).reindex(...)` diganti `groupby(...)[FEATURES].mean().reindex(...)`, karena `reindex` tidak ada pada objek GroupBy.

### Verifikasi
- Eksekusi penuh tanpa error. Empat gambar baru dirender dan diperiksa manual: panel sebelum dan sesudah inpainting, scatter PCA bersama heatmap fitur, dua confusion matrix, dan kepentingan fitur.
- Angka lama tidak bergeser: `summary.csv` P0 tetap 0,7029, dan CSV lama di `results/data_preprocessing` tidak berubah.
- Angka markdown dicocokkan dengan keluaran sel: 0,4965 ke 0,4866, serta 0,562 dan 0,250 untuk stadium per spesies.

### Catatan
- Semua angka klasifikasi adalah batas atas, karena fitur diambil dari mask ground truth, bukan mask prediksi.
- Bukti area putih dihitung ulang setiap kali notebook dijalankan, tidak disimpan sebagai gambar terpisah.
- Sudah di-commit sebagai `99c25cf` dan di-push ke `origin/feat/ian`.
- Perubahan lama yang tidak ikut di-commit: 32 PNG yang pikselnya identik dengan HEAD hanya beda kompresi, dua CSV di `results/preprocessing_stages`, dan berkas deck di `docs/`.
