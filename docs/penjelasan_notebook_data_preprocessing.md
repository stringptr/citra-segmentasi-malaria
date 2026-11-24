# Penjelasan Lengkap Notebook `malaria_data_preprocessing.ipynb`

Dokumen ini menjelaskan isi notebook secara utuh: data yang dipakai, apa yang dikerjakan tiap bagian, kenapa parameternya begitu, bagaimana membaca setiap gambar dan tabel, sampai angka hasil dan keterbatasannya. Tujuannya supaya kamu tidak perlu membuka notebook untuk memahami alurnya.

Penulis dokumen: OpenBot, 17 November 2026.
Sumber angka: notebook versi terakhir (53 sel, 29 gambar) dan file CSV di `results/data_preprocessing/`.

Riwayat revisi singkat: revisi 18 November menambah Bagian 7 tentang perbandingan menyeluruh (grayscale, varian tunggal, rantai, leave one out) dan menggeser nomor bagian sesudahnya. Versi 16 November belum memuat Bagian 9 (perbandingan terbaik dengan terburuk). Revisi ini menambahkannya, memperbaiki penjelasan kenapa adaptive threshold gagal, dan menambah dua file CSV baru. Revisi 24 November menambah Bagian 11 tentang area putih dan Bagian 12 tentang ekstraksi fitur serta klasifikasi, lalu menggeser nomor bagian dokumen.

---

## 1. Gambaran besar

Notebook ini menjawab dua pertanyaan terpisah, dan sengaja dipisah urutannya:

1. **Seperti apa datanya?** 32 crop parasit malaria dari dua spesies dan empat stadium, dibaca satu stadium demi satu stadium, bukan langsung digabung.
2. **Preprocessing dan segmentasi mana yang bekerja?** Lima varian preprocessing dan lima metode segmentasi diuji terhadap mask ground truth, hasilnya dibaca per stadium lalu digabung.

Alurnya:

| Bagian | Isi |
|---|---|
| 1 | Muat 32 crop, metadata, dan mask ground truth |
| 2 | Data per stadium: gambar crop dan histogram terpisah untuk ring, trophozoite, schizont, gametocyte |
| 2.5 | Tabel ringkasan angka per stadium dan spesies |
| 3 | Gabungan 32 citra: grid semua crop, distribusi luas parasit, histogram gabungan |
| 4 | Tahapan preprocessing P0 sampai P4 dengan gambar dan histogram per tahap |
| 5 | Lima metode segmentasi: pixel if-else, Otsu, Otsu multilevel 3, adaptive, k-means |
| 6 | Evaluasi preprocessing per stadium |
| 7 | Evaluasi gabungan 32 citra, heatmap, histogram frekuensi, perbandingan metode |
| 8 | Terbaik dan terburuk: Otsu lawan adaptive, P0 lawan P1, beserta penyebabnya |
| 9 | Kesimpulan |

Cara menjalankan: buka di Jupyter, pilih kernel `python3` dari `/home/archian/.venv`, lalu Run All. Pustaka yang dibutuhkan ada di `requirement.txt` (numpy, opencv-python-headless, scikit-image, pandas, matplotlib, Pillow).

Kalau ingin menjalankan tanpa membuka Jupyter:

```bash
cd citra-segmentasi-malaria
/home/archian/.venv/bin/jupyter nbconvert --to notebook --execute \
  --inplace malaria_data_preprocessing.ipynb
```

### 1.1 Koreksi penting: yang dianotasi adalah sel darah merah terinfeksi

Anotasi MP-IDB menandai **seluruh sel darah merah yang terinfeksi**, bukan badan parasitnya. Buktinya, mask untuk stadium ring luasnya sekitar 18 sampai 23 ribu piksel dan mengisi sekitar 75 persen kotak pembatasnya, padahal parasit ring hanya sepersekian dari ukuran sel. Parasitnya sendiri berada di dalam area itu tanpa anotasi terpisah.

Konsekuensi yang perlu diingat:

- Semua angka Dice dan IoU di notebook ini mengukur **segmentasi sel darah merah terinfeksi**, bukan segmentasi parasit.
- Kolom `parasite_area_px` di `metadata.csv` menyimpan luas sel terinfeksi, walaupun namanya menyebut parasit. Label "luas parasit" pada gambar sudah diganti menjadi "luas sel terinfeksi".
- Kalau nanti tujuannya benar benar memisahkan badan parasit, anotasi baru perlu dibuat, karena data acuan yang sekarang tidak memisahkannya.

---

## 2. Data yang dipakai

### 2.1 Asal data

Dataset MP-IDB (malaria parasite image database) berisi citra mikroskopis darah dengan pewarnaan Giemsa, plus anotasi Supervisely berupa bitmap untuk tiap sel darah merah yang terinfeksi. Dari situ diambil 32 crop, disimpan sebagai PNG di `malaria_images/`, dengan pola nama `{spesies}_{stadium}_{nomor}.png`, misalnya `falciparum_ring_2.png`.

Komposisinya 4 stadium dikali 2 spesies dikali 4 crop, jadi 32 citra. Cara memilihnya: diambil parasit terbesar pada tiap citra sumber, lalu empat citra terbesar per kelompok spesies dan stadium, tanpa memakai citra sumber yang sama dua kali dalam satu kelompok.

### 2.2 Dua dimensi label yang sering tertukar

- **Spesies**: *P. falciparum* dan *P. vivax*. Ini jenis parasitnya.
- **Stadium**: ring, trophozoite, schizont, gametocyte. Ini tahap perkembangan parasit dalam satu siklus hidup, berurutan. Ring bentuknya cincin kecil, trophozoite lebih besar dan aktif makan, schizont berisi banyak merozoit, gametocyte bentuknya memanjang seperti pisang.

Jadi "ring falciparum" dan "schizont falciparum" adalah stadium berbeda dari spesies yang sama, bukan dua hal yang bisa dibandingkan sebagai satu kategori.

Catatan label: ada lima pasang crop yang memakai sel yang sama tetapi diberi stadium berbeda, yaitu dari citra sumber `1408161544-0001-S_R.jpg` (falciparum ring 1 dan schizont 1), `1408161544-0002-R_S.jpg` (falciparum ring 3 dan schizont 2), `1408161544-0003-R_S.jpg` (falciparum ring 4 dan schizont 3), `1603223711-0002-T_G.jpg` (falciparum trophozoite 2 dan gametocyte 3), dan `1703121298-0012-G_R.jpg` (vivax ring 1 dan vivax gametocyte 2).

Nama file sumber memang memuat dua stadium sekaligus, sedangkan pemilihan crop mengambil objek terbesar tanpa melihat stadium. Akibatnya dari 32 crop hanya ada 27 sel unik, dan pada tiap pasangan satu label stadiumnya pasti salah. Perbaikan yang disarankan: pilih objek berdasarkan stadium di nama file sumber, bukan sekadar objek terbesar.

### 2.3 Isi `malaria_images/metadata.csv`

Satu baris per crop. Kolom yang dipakai notebook:

| Kolom | Arti |
|---|---|
| `filename` | nama file PNG crop |
| `species` | `falciparum` atau `vivax` |
| `stage` | stadium, misalnya `ring stage` |
| `source_image` | nama citra asli MP-IDB asal crop |
| `parasite_area_px` | luas sel darah merah terinfeksi dalam piksel, dihitung dari anotasi. Namanya masih menyebut parasit karena mengikuti metadata lama |
| `bbox_x`, `bbox_y`, `bbox_w`, `bbox_h` | kotak pembatas sel terinfeksi pada citra asli |

Ukuran crop tidak seragam, berkisar 300 sampai 400 piksel per sisi, tergantung besar sel yang terinfeksi.

### 2.4 Cara mask ground truth dibuat

Ground truth adalah mask biner yang menandai piksel mana yang termasuk sel darah merah terinfeksi menurut anotasi manusia. Notebook tidak menyimpan mask sebagai file terpisah, tetapi mendekode ulang dari anotasi Supervisely. Langkahnya:

1. Baca `mp-idb-DatasetNinja/ds/ann/{source_image}.json`.
2. Untuk tiap objek, data bitmap disimpan dalam bentuk base64 dan dikompres zlib. Setelah didekode, ambil kanal alpha (atau kanal tunggal kalau gambarnya grayscale), lalu jadikan biner.
3. Tempelkan bitmap itu ke kanvas seukuran citra asli pada posisi `origin` milik objek. Kalau satu citra punya beberapa parasit, semuanya digabung dengan operasi OR.
4. Potong kanvas sesuai kotak crop, tetapi dilebihkan **80 piksel** ke setiap arah (`PAD = 80`). Tujuannya supaya di sekitar parasit masih ada latar, karena segmentasi butuh latar untuk memisahkan objek.
5. Hasilnya mask boolean seukuran crop, disimpan di list `gts`, berpasangan dengan citra di list `crops`.

Margin 80 piksel ini sama dengan notebook sebelumnya, jadi perbandingan antar notebook tetap setara.

### 2.5 Cara membaca penanda hijau

Sejak revisi ini, setiap gambar yang menampilkan citra diberi penanda ground truth: **area hijau transparan dengan garis hijau**. Artinya satu hal saja, yaitu area yang dianotasi sebagai sel darah merah terinfeksi. Parasitnya ada di dalam area itu dan tidak punya penanda sendiri.

Untuk membedakan isi citra, pakai ciri berikut:

| Objek | Ciri visual | Penanda |
|---|---|---|
| Sel darah merah sehat | paling banyak, ukuran hampir seragam, bulat atau lonjong, sitoplasma merah muda pucat, tanpa inti | tidak ditandai |
| Sel darah merah terinfeksi | satu sel yang lebih gelap atau berubah bentuk dibanding tetangganya | area dan garis hijau |
| Sel darah putih | jauh lebih besar dari sel darah merah, inti biru keunguan besar dan padat, sitoplasma bergranula, jumlahnya sedikit | tidak ditandai, dikenali dari ukuran dan warna |
| Parasit | struktur kecil di dalam sel hijau, dengan bentuk khas per stadium | tidak punya penanda sendiri |

Cara menemukan parasit di dalam sel hijau, per stadium:

- **ring**: satu titik biru gelap kecil dengan lingkaran sitoplasma tipis di sekelilingnya.
- **trophozoite**: gumpalan sitoplasma biru yang lebih besar dan bentuknya tidak beraturan.
- **schizont**: kumpulan titik titik kecil berwarna biru di dalam sel.
- **gametocyte**: badan memanjang seperti pisang, dengan butir pigmen gelap di tengahnya.

Bagian 1.1 di notebook memakai satu contoh terbaik per stadium, yaitu `falciparum_ring_2.png`, `falciparum_trophozoite_1.png`, `falciparum_schizont_3.png`, dan `falciparum_gametocyte_1.png`, dengan perbesaran empat kali supaya bentuk parasitnya kelihatan. Contohnya sengaja dipilih yang morfologinya paling jelas, bukan asal crop pertama.

Penanda yang sama dipakai di seluruh notebook: tampilan crop per stadium, grid 32 citra, demo lima varian preprocessing, dan visual lima metode segmentasi. Pada demo preprocessing dan visual metode, yang digambar hanya garis hijaunya, tanpa isi area, supaya nilai piksel dan bentuk mask tetap terbaca.

---

## 3. Bagian 2: membaca data per stadium

### 3.1 Kenapa dipisah

Kalau 32 crop langsung ditampilkan dalam satu grid, perbedaan antar stadium tenggelam. Histogram gabungan juga hanya menunjukkan satu puncak besar yang menyesatkan, karena distribusi intensitas tiap stadium berbeda. Karena itu tiap stadium ditampilkan dua kali:

- **tampilan crop**, 4 *P. falciparum* di baris atas dan 4 *P. vivax* di baris bawah, tiap panel diberi nama file, luas sel terinfeksi, dan citra sumber. Sel yang terinfeksi diwarnai hijau transparan dan digaris hijau;
- **tampilan histogram**, satu figure tersendiri yang lebih besar.

### 3.2 Cara membaca histogram per stadium

- Tiap garis tipis berwarna adalah satu crop.
- Area abu-abu adalah histogram rata-rata keempat crop spesies itu. Caranya, tiap crop di-resize ke 256x256 lebih dulu, lalu nilainya dirata-ratakan piksel demi piksel. Resize perlu karena ukuran crop berbeda-beda.
- Garis hitam putus-putus adalah rata-rata intensitas gabungan, garis merah titik-titik adalah median.
- Sumbu-x adalah intensitas grayscale 0 sampai 255. Angka kecil berarti gelap, angka besar berarti terang.

Intensitas grayscale dipakai di sini, bukan kanal Lab b, karena tujuannya melihat karakter pewarnaan Giemsa apa adanya, tanpa preprocessing. Segmentasi nanti tetap memakai kanal Lab b.

### 3.3 Angka statistik per stadium

Dari `ringkasan_per_stadium.csv`:

| Stadium | Spesies | n | Luas sel terinfeksi (ribu px) | Rata-rata intensitas | Median | Simpangan baku |
|---|---|---|---|---|---|---|
| ring | P. falciparum | 4 | 19.75 | 181.27 | 187.0 | 22.29 |
| ring | P. vivax | 4 | 20.63 | 183.69 | 188.5 | 23.06 |
| trophozoite | P. falciparum | 4 | 11.03 | 166.88 | 168.0 | 18.64 |
| trophozoite | P. vivax | 4 | 17.01 | 204.35 | 209.8 | 22.17 |
| schizont | P. falciparum | 4 | 17.85 | 178.74 | 183.0 | 22.86 |
| schizont | P. vivax | 4 | 24.05 | 200.97 | 207.5 | 22.98 |
| gametocyte | P. falciparum | 4 | 11.96 | 168.06 | 173.3 | 22.32 |
| gametocyte | P. vivax | 4 | 23.44 | 161.37 | 164.5 | 19.53 |

Yang bisa dibaca dari tabel ini:

- Parasit terkecil ada di trophozoite falciparum (11.03 ribu piksel), terbesar di schizont vivax (24.05 ribu piksel). Selisihnya sekitar dua kali, jadi satu ambang tetap yang sama untuk semua citra memang rawan.
- Distribusi intensitas *P. vivax* cenderung lebih terang pada stadium ring, trophozoite, dan schizont, lalu berbalik lebih gelap pada gametocyte. Artinya tidak ada satu nilai intensitas yang cocok untuk semua kelompok.
- Simpangan baku 18 sampai 23 menunjukkan sebaran yang lebar di dalam satu kelompok kecil. Karena itu mean saja tidak cukup, histogram dan titik per citra dipakai sebagai pelengkap.

---

## 4. Bagian 3: gabungan 32 citra

Isinya tiga hal, semuanya versi gabungan dari Bagian 2:

1. **Grid 32 crop**, baris adalah stadium, kolom adalah spesies. Label spesies diletakkan di atas blok kolom, label stadium di sisi kiri. Tiap panel memuat nama file dan luas sel terinfeksi, dengan area ground truth diwarnai hijau.
2. **Dot plot luas sel terinfeksi**, dipisah per spesies dan per stadium. Satu titik satu citra, garis hitam adalah rata-rata. Ini pengganti boxplot, karena dengan n = 4 atau 8 boxplot hanya menggambar ulang empat titik itu dan terlihat seperti distribusi padahal bukan.
3. **Histogram gabungan** per spesies dan keseluruhan. Gunanya menunjukkan bahwa penggabungan menyatukan beberapa puncak yang aslinya terpisah, dan itu justru alasan Bagian 2 dibuat.

---

## 5. Bagian 4: lima varian preprocessing

Semua varian bekerja pada kanal warna Lab, khususnya kanal b. Variannya bertingkat, tiap varian menambah satu langkah di atas varian sebelumnya.

### 5.1 Apa itu Lab b

Ruang warna Lab memisahkan terang (`L`) dari dua sumbu warna (`a` dari hijau ke merah, `b` dari biru ke kuning). Pada pewarnaan Giemsa, parasit tampak kebiruan atau keunguan, sedangkan sel darah merah dan latarnya lebih merah atau kekuningan. Akibatnya parasit jatuh di nilai b yang rendah, dan latar di nilai b yang tinggi. Satu kanal saja sudah memisahkan objek dari latar, tanpa perlu threshold per kanal RGB.

### 5.2 Langkah tiap varian

| Kode | Nama | Langkah |
|---|---|---|
| P0 | `P0_Lab_b` | konversi RGB ke Lab, ambil kanal b. Tidak ada langkah lain |
| P1 | `P1_bg_correct` | P0 lalu koreksi background: estimasi latar dengan closing morfologi disk radius 25, kurangkan dari kanal, regangkan ke 0 sampai 255 |
| P2 | `P2_median` | P1 lalu median filter 5x5 |
| P3 | `P3_clahe` | P2 lalu CLAHE, `clipLimit` 2.0, grid 8x8 |
| P4 | `P4_reinhard` | normalisasi warna Reinhard ke rata-rata dan simpangan baku dataset, lalu P1 dan median 5x5 |

Penjelasan istilah:

- **Closing morfologi** adalah dilasi lalu erosi dengan bentuk tertentu. Dengan disk besar, hasilnya perkiraan latar yang halus karena objek kecil ikut terisi.
- **Median filter** mengganti tiap piksel dengan nilai tengah tetangganya. Derau grain hilang, tepi objek relatif tetap.
- **CLAHE** (contrast limited adaptive histogram equalization) menaikkan kontras lokal dengan batas agar tidak berlebihan.
- **Reinhard** adalah normalisasi warna statistik: distribusi warna tiap citra digeser dan diskalakan supaya mirip referensi.

### 5.3 Yang ditampilkan

Untuk tiap stadium, satu crop *P. falciparum* ditampilkan lima kali (citra asli, P1, P2, P3, P4) dengan histogram di bawahnya. Suptitle memuat nama file, spesies, stadium, luas sel terinfeksi, dan citra sumber. Batas ground truth digambar sebagai garis hijau di setiap panel, supaya jelas bagian mana yang seharusnya dipertahankan preprocessing.

Yang perlu disadari saat melihat gambar itu: P1 sampai P4 menampilkan kanal hasil olahan, bukan kanal b mentah. Jadi citra asli di panel pertama tidak bisa dibandingkan warnanya langsung, tetapi histogramnya bisa dibandingkan bentuknya.

### 5.4 Hasil

Dice rata-rata per stadium, segmentasi Otsu multilevel 3 (dari `dice_per_stadium.csv`):

| Stadium | n | P0 Lab b | P1 bg | P2 median | P3 CLAHE | P4 Reinhard |
|---|---|---|---|---|---|---|
| ring | 8 | **0.7156** | 0.4478 | 0.4653 | 0.4987 | 0.4724 |
| trophozoite | 8 | **0.5591** | 0.3969 | 0.3917 | 0.4254 | 0.4183 |
| schizont | 8 | **0.7279** | 0.4418 | 0.4508 | 0.4983 | 0.4634 |
| gametocyte | 8 | **0.8091** | 0.4639 | 0.4655 | 0.5195 | 0.5128 |

Gabungan 32 citra (dari `summary.csv`):

| Varian | Dice | IoU |
|---|---|---|
| P0 Lab b | **0.7029** | **0.5737** |
| P1 koreksi background | 0.4376 | 0.2867 |
| P2 median | 0.4433 | 0.2923 |
| P3 CLAHE | 0.4855 | 0.3299 |
| P4 Reinhard | 0.4667 | 0.3133 |

### 5.5 Kenapa Lab b menang

Crop sudah terpusat pada parasit, dengan margin latar 80 piksel. Pada kondisi seperti itu kanal b sudah memisahkan parasit dengan baik, sehingga langkah tambahan hanya mengubah distribusi nilai. Koreksi background, misalnya, membuang komponen yang rata dan lambat berubah, padahal parasit yang tipis justru sebagian besar tersusun dari komponen seperti itu. Akibatnya parasit ring yang dindingnya tipis banyak hilang, dan Dice turun paling dalam pada P1. Angka rincinya dibahas di Bagian 9: recall turun dari 0.58 menjadi 0.29, dan luas mask dari 0.59 menjadi 0.33 kali ground truth.

Ini berbeda dari eksperimen pada citra penuh di Progress 1, di mana koreksi background justru membantu. Bedanya jelas: citra penuh punya latar yang tidak rata dan banyak objek lain, sedangkan crop sudah bersih.

---

## 6. Bagian 5: lima metode segmentasi

Semua metode dijalankan pada kanal Lab b citra asli (bukan hasil P1 sampai P4), supaya perbandingannya hanya menguji metode, bukan preprocessing. Semua mask lalu dibersihkan dari objek yang luasnya di bawah 12 piksel (`MIN_AREA = 12`).

### 6.1 Penjelasan tiap metode

| Kode | Metode | Parameter | Ide dasar |
|---|---|---|---|
| M1 | Pixel if-else | ambang tetap 115 | tiap piksel diputuskan sendiri, `mask = kanal < 115` |
| M2 | Otsu satu ambang | otomatis per citra | cari satu ambang yang memaksimalkan varians antar dua kelompok piksel |
| M3 | Otsu multilevel 3 | 3 kelas | cari dua ambang, ambil kelas tergelap |
| M4 | Adaptive threshold | blok 35, C 5 | ambang berbeda untuk tiap lingkungan piksel |
| M5 | k-means | 3 klaster | kelompokkan piksel berdasarkan intensitas, klaster tergelap jadi parasit |

- **Otsu** memilih ambang dengan memaksimalkan varians antar kelas. Metode ini otomatis, tetapi mengasumsikan gambar punya dua kelompok besar, yaitu objek dan latar.
- **Otsu multilevel** membagi histogram menjadi tiga kelas. Kelas tergelap dianggap parasit, kelas tengah sering berisi tepi parasit atau bagian sel darah, kelas terang adalah latar. Karena hanya kelas tergelap yang diambil, hasilnya lebih ketat.
- **Adaptive threshold** menghitung ambang lokal di jendela 35x35. Cocok untuk latar yang bergradasi, tetapi pada citra bertekstur justru ikut mengambil tekstur.
- **k-means** mengelompokkan nilai piksel menjadi tiga pusat, lalu semua piksel dimasukkan ke pusat terdekat. Karena memakai 4.000 piksel contoh agar cepat, hasilnya bisa berbeda sedikit tiap kali dijalankan kalau benih acaknya berbeda.

**Kenapa 115?** Ambang tetap itu disapu dulu dari 95 sampai 140 dengan langkah 5. Hasil sapuan menunjukkan 115 memberi Dice tertinggi (0.482), lebih tinggi dari 120 (0.454) dan 125 (0.439). Jadi membandingkan metode otomatis dengan angka 115 adalah perbandingan yang adil, bukan sengaja memakai ambang buruk.

### 6.2 Hasil per stadium

Dice rata-rata (dari `dice_metode_per_stadium.csv`):

| Stadium | n | Pixel if-else | Otsu | Otsu multilevel 3 | Adaptive | k-means |
|---|---|---|---|---|---|---|
| ring | 8 | 0.5339 | **0.8054** | 0.7156 | 0.3570 | 0.7490 |
| trophozoite | 8 | 0.3060 | **0.6864** | 0.5591 | 0.3866 | 0.6026 |
| schizont | 8 | 0.5237 | **0.8267** | 0.7279 | 0.3919 | 0.7411 |
| gametocyte | 8 | 0.5645 | **0.8609** | 0.8091 | 0.3284 | 0.8365 |

### 6.3 Hasil gabungan 32 citra

Dari `summary_metode.csv`:

| Metode | Dice | IoU | Precision | Recall |
|---|---|---|---|---|
| Otsu satu ambang | **0.7948** | **0.6802** | 0.8358 | 0.7533 |
| k-means 3 klaster | 0.7323 | 0.6073 | 0.9780 | 0.6158 |
| Otsu multilevel 3 | 0.7029 | 0.5737 | 0.9828 | 0.5822 |
| Pixel if-else 115 | 0.4820 | 0.3725 | 0.5163 | 0.6270 |
| Adaptive blok 35 | 0.3660 | 0.2288 | 0.7833 | 0.2442 |

Urutan ini sama di keempat stadium, jadi kesimpulannya tidak bergantung pada satu stadium saja.

### 6.4 Cara membaca hasil itu

- **Otsu satu ambang menang** karena ambangnya menyesuaikan tiap citra dan tidak terlalu ketat, sehingga parasit utuh ikut terambil.
- **Otsu multilevel 3 dan k-means punya precision hampir 1.0** (0.98), artinya hampir tidak ada piksel latar yang salah dianggap parasit. Tetapi recall-nya 0.58 dan 0.62, jadi sekitar 40 persen luas parasit tidak terambil. Mask-nya rapi tetapi bolong.
- **Pixel if-else** paling lemah presisinya (0.52) karena ambang tetap yang sama tidak cocok untuk semua citra, sebagian citra terlalu gelap dan sebagian terlalu terang.
- **Adaptive threshold** paling buruk, tetapi alasannya bukan "yang terambil hanya tepi". Mask adaptive justru jarang menempel di tepi ground truth. Yang terjadi adalah ambang lokal hanya meloloskan bagian paling gelap di dalam sel, sehingga luas yang tertangkap 0.31 dari ground truth dan mask pecah jadi sekitar 45 bintik (recall 0.25). Penjelasan lengkap beserta angkanya ada di Bagian 9.
- **Dice sekitar 0.70 sampai 0.79 pada objek kecil** seperti parasit dalam crop ini masih wajar untuk metode klasik tanpa pembelajaran mesin. Untuk perbandingan, model deep learning pada tugas sejenis biasanya di atas 0.85, tetapi butuh data latih yang jauh lebih banyak dari 32 citra.

---

## 7. Bagian 6: perbandingan menyeluruh

Bagian 6 di notebook menjawab tiga hal yang tidak bisa dijawab rantai P0 sampai P4 sendirian: apakah kanal Lab b lebih baik daripada grayscale, apakah tiap langkah masih berguna kalau dipakai sendiri, dan apakah tiap langkah berguna ketika langkah lain tetap ada. Rantai P0 sampai P4 lalu dilaporkan per stadium di Bagian 7 notebook.

Semua angka memakai pembagian 2 train dan 2 test dan segmentasi Otsu multilevel 3, lalu diulang dengan Otsu satu ambang supaya kelihatan apakah urutannya bergantung metode segmentasi.

### 7.1 Varian yang diuji

| Kelompok | Varian | Isi |
|---|---|---|
| Baseline | B1 grayscale rata-rata RGB | (R + G + B) / 3, dibulatkan |
| Baseline | B2 grayscale berbobot `cv2` | 0,299 R + 0,587 G + 0,114 B |
| Tunggal | S1 koreksi background | `bg_correct(lab_b(img))` |
| Tunggal | S2 median | `median(lab_b(img))` |
| Tunggal | S3 CLAHE | `clahe(lab_b(img))` |
| Tunggal | S4 Reinhard | `lab_b(reinhard(img))`, tanpa koreksi background dan tanpa median |
| Rantai | P0 sampai P3 | tiap varian menambah satu langkah di atas varian sebelumnya |
| Leave one out | rantai penuh P3 dengan satu langkah dibuang | tanpa bg, tanpa median, tanpa CLAHE |

Padanan dengan permintaan "P0 sendiri sampai P4 sendiri":

| Maksud | Varian | Isinya |
|---|---|---|
| P0 sendiri | `P0_Lab_b` | kanal b saja |
| P1 sendiri | `S1_bg_correct` | kanal b + koreksi background, identik dengan P1 |
| P2 sendiri | `S2_median` | kanal b + median, tanpa koreksi background |
| P3 sendiri | `S3_clahe` | kanal b + CLAHE, tanpa koreksi background dan tanpa median |
| P4 sendiri | `S4_reinhard` | Reinhard lalu kanal b, tanpa koreksi background dan tanpa median |
| Berlapis | P0 sampai P4 di Bagian 7 notebook | tiap varian dinilai sendiri-sendiri, tetapi definisinya memakai langkah sebelumnya |

Varian tunggal sengaja ditaruh di atas kanal Lab b, bukan di atas grayscale. Segmentasi selalu butuh satu kanal dasar, jadi kalau kanal dasarnya ikut diganti, hasilnya tidak bisa dipakai menilai langkah itu sendiri. Dengan begitu P0 menjadi pembanding yang tepat, karena bedanya hanya satu langkah. Perbandingan kanal diukur terpisah oleh B1 dan B2.

Catatan: `S1_bg_correct` dan `P1_bg_correct` hasilnya identik karena keduanya pipeline yang sama. Pasangan itu berfungsi sebagai pemeriksaan konsistensi, bukan temuan baru. Hal yang sama berlaku untuk `L_tanpa_clahe` dan `P2_median`.

### 7.2 Hasil

| Varian | Kelompok | Dice train | Dice test | Dice 32 | Selisih vs pembanding | p | Dice Otsu1 32 |
|---|---|---|---|---|---|---|---|
| B1 grayscale rata-rata RGB | baseline | 0.5612 | 0.6616 | 0.6114 | -0.0915 (P0) | 0.008 | 0.5568 |
| B2 grayscale berbobot `cv2` | baseline | 0.5980 | 0.7114 | 0.6547 | -0.0482 (P0) | 0.100 | 0.5610 |
| S1 koreksi background saja | tunggal | 0.4102 | 0.4650 | 0.4376 | -0.2653 (P0) | < 0.001 | 0.5835 |
| S2 median saja | tunggal | 0.6922 | 0.7055 | 0.6988 | -0.0041 (P0) | 0.070 | 0.8013 |
| S3 CLAHE saja | tunggal | 0.5543 | 0.6116 | 0.5830 | -0.1199 (P0) | < 0.001 | 0.6058 |
| S4 Reinhard saja | tunggal | 0.6770 | 0.7378 | 0.7074 | +0.0045 (P0) | 0.904 | 0.8069 |
| P0 kanal Lab b | rantai | 0.6832 | 0.7226 | 0.7029 | +0.0000 (P0) | pembanding | 0.7948 |
| P1 bg correct | rantai | 0.4102 | 0.4650 | 0.4376 | -0.2653 (P0) | < 0.001 | 0.5835 |
| P2 median | rantai | 0.4091 | 0.4775 | 0.4433 | -0.2596 (P0) | < 0.001 | 0.5800 |
| P3 CLAHE | rantai | 0.4584 | 0.5126 | 0.4855 | -0.2174 (P0) | < 0.001 | 0.6125 |
| L rantai penuh P3 | leave one out | 0.4584 | 0.5126 | 0.4855 | +0.0000 (P3) | pembanding | 0.6125 |
| L tanpa koreksi background | leave one out | 0.5443 | 0.6146 | 0.5795 | +0.0940 (P3) | < 0.001 | 0.6112 |
| L tanpa median | leave one out | 0.4641 | 0.5188 | 0.4914 | +0.0060 (P3) | 0.489 | 0.5971 |
| L tanpa CLAHE | leave one out | 0.4091 | 0.4775 | 0.4433 | -0.0421 (P3) | < 0.001 | 0.5800 |

Kolom selisih memakai pembanding yang tertulis di sebelahnya: baseline dan varian tunggal dibandingkan dengan P0, sedangkan leave one out dibandingkan dengan rantai penuh P3. Nilai p dari uji Wilcoxon berpasangan pada 32 citra; p di bawah 0,05 berarti selisihnya konsisten searah, bukan karena satu dua citra.

### 7.3 Cara membaca hasilnya

- **Lab b lebih baik daripada grayscale, tetapi jaraknya bergantung rumus grayscale.** Grayscale rata-rata RGB 0.6114, Lab b 0.7029, selisih +0.0915 dengan p 0.0079. Grayscale berbobot `cv2` 0.6547 dan selisihnya terhadap Lab b tidak signifikan (p 0.0998). Jadi klaim "Lab b lebih baik" paling kuat dibanding rata-rata RGB, dan lebih lemah dibanding grayscale berbobot.
- **Koreksi background merugikan karena langkahnya sendiri, bukan karena urutannya.** Berdiri sendiri di atas Lab b, hasilnya 0.4376, sama persis dengan P1 di dalam rantai. Ini bukti bahwa langkah itu merusak sinyal parasit pada crop yang sudah terpusat.
- **Median dan Reinhard netral kalau berdiri sendiri, tetapi berbeda di dalam rantai.** Median sendiri 0.6988 (p 0.0697 terhadap P0, tidak nyata) dan Reinhard sendiri 0.7074 (p 0.90). Di dalam rantai keduanya turun karena ditempel setelah koreksi background, yang sudah membuang komponen halus.
- **CLAHE berguna di dalam rantai, merugikan kalau sendirian.** Sendiri 0.583. Di rantai penuh, membuang CLAHE menurunkan Dice dari 0.4855 ke 0.4433 dengan p di bawah 0.001. Ini contoh efek yang bergantung konteks.
- **Membuang koreksi background paling menolong.** Rantai penuh 0.4855, tanpa koreksi background 0.5795, selisih +0.0940 dengan p 0.0004. Membuang median hampir tidak mengubah apa pun (0.4914, p 0.489).
- **Urutan varian bergantung metode segmentasi.** Dengan Otsu satu ambang, 10 dari 14 varian berubah peringkat. Median sendiri (0.8013) dan Reinhard sendiri (0.8069) malah mengalahkan P0 (0.7948). Karena itu setiap klaim soal langkah preprocessing harus menyebut metode segmentasinya.

### 7.4 File hasil

- `perbandingan_menyeluruh.csv` berisi tabel di atas untuk Otsu multilevel 3.
- `perbandingan_menyeluruh_otsu1.csv` berisi angka Otsu satu ambang dan peringkat kedua metode.
- `per_image_semua_varian.csv` berisi Dice tiap citra untuk keempat belas varian, lengkap dengan spesies, stadium, dan split.

---

## 8. Bagian 7 dan 8: evaluasi

### 8.1 Bagian 7, evaluasi preprocessing per stadium

Sama seperti tabel di 5.4, tetapi di sini fokusnya pembacaan: tabel Dice per stadium, histogram Dice per stadium untuk lima varian, dan histogram per spesies dan stadium.

Cara membaca histogramnya: sumbu-x Dice (0 sampai 1), sumbu-y jumlah citra. Garis titik-titik vertikal adalah rata-rata kelompok itu. Kalau garis-garis varian menumpuk rapat, artinya varian itu memberi hasil mirip pada kelompok tersebut. Pada stadium trophozoite, garis P0 jauh di kanan sementara P1 sampai P4 menumpuk di kiri, tanda bahwa semua langkah tambahan merugikan di stadium itu.

### 8.2 Bagian 8, gabungan

Isinya:

1. **Tabel ringkasan** lima varian, Dice dan IoU, 32 citra.
2. **Boxplot** Dice per citra untuk tiap varian, dengan titik tiap citra ditimpa di atasnya dan outlier box dimatikan. Kotak hanya alat bantu visual, titiknya yang jadi bukti.
3. **Dot plot per kelompok**, delapan kelompok spesies dan stadium, Dice dirata-ratakan atas lima varian.
4. **Heatmap**, varian dikali stadium dan varian dikali spesies, dengan angka di tiap sel dan colorbar 0 sampai 1.
5. **Histogram frekuensi**, satu untuk semua 160 nilai Dice (32 citra kali 5 varian) dengan garis median, satu lagi per varian.
6. **Tabel metode segmentasi gabungan** dengan precision dan recall, ditambah boxplot per metode.

---

## 9. Bagian 9: terbaik dan terburuk, apa bedanya

Bagian ini membandingkan pemenang dengan juru kunci secara langsung, lalu mencari penyebabnya dari angka, bukan dari kesan melihat gambar. Yang dibandingkan ada dua pasang: **Otsu satu ambang lawan adaptive threshold** di sisi metode, dan **P0 kanal Lab b lawan P1 koreksi background** di sisi preprocessing.

Empat ukuran tambahan dipakai untuk menjelaskan penyebabnya:

| Ukuran | Arti | Cara membacanya |
|---|---|---|
| Rasio luas | luas mask dibagi luas ground truth | 1.0 berarti luasnya pas, 0.3 berarti hanya sepertiga sel yang tertangkap |
| Recall | bagian ground truth yang berhasil ditangkap | makin kecil, makin banyak sel yang hilang |
| Komponen | jumlah bercak terpisah dalam satu mask | satu sel seharusnya satu atau dua komponen, bukan puluhan |
| Fraksi dekat batas | bagian mask yang berjarak maksimal 2 piksel dari tepi ground truth | untuk menguji dugaan mask hanya berupa garis tepi |

Semua ukuran di Bagian 9 dirata-ratakan **per citra**, bukan dijumlahkan dari semua piksel. Tabel metode di Bagian 8 memakai penjumlahan piksel. Dua cara itu sah, tetapi hasilnya berbeda sedikit. Contohnya precision Otsu 0.90 di sini dan 0.84 di Bagian 8. Selisihnya bukan kesalahan hitung, hanya cara rata-ratanya yang berbeda, dan di Bagian 9 cara per citra dipakai supaya satu citra besar tidak mendominasi.

### 9.1 Tabel semua metode

Tabel ini muncul di notebook tepat setelah paragraf pembuka Bagian 9, sebelum subbagian 8.1 notebook. Rinciannya dari `perbandingan_metode.csv`, diurutkan dari Dice tertinggi:

| Metode | Dice | IoU | Precision | Recall | Rasio luas | Komponen | Dekat batas |
|---|---|---|---|---|---|---|---|
| Otsu satu ambang | **0.795** | **0.680** | 0.900 | 0.748 | 0.895 | 14.5 | 0.068 |
| k-means 3 klaster | 0.721 | 0.597 | 0.974 | 0.605 | 0.619 | 8.4 | 0.059 |
| Otsu multilevel 3 | 0.703 | 0.574 | 0.981 | 0.580 | 0.590 | 7.7 | 0.052 |
| Pixel if-else 115 | 0.482 | 0.373 | 0.660 | 0.580 | 1.132 | 37.1 | 0.055 |
| Adaptive blok 35 | 0.366 | 0.229 | 0.833 | 0.245 | 0.309 | 45.2 | 0.082 |

Tabel ini memisahkan dua jenis kegagalan yang sering tercampur:

- **Terlalu hemat mengambil piksel.** Adaptive (luas 0.31, recall 0.25) dan Otsu multilevel 3 serta k-means (luas sekitar 0.6) termasuk di sini. Precision tinggi, tetapi sekitar 40 persen atau lebih luas sel tidak terambil.
- **Terlalu banyak mengambil piksel.** Pixel if-else justru sebaliknya: luas mask 1.13 kali ground truth dan precision 0.66, jadi ambang tetapnya ikut mengambil latar. Recall-nya mirip Otsu (0.58 lawan 0.75), tetapi lebihan pikselnya menjatuhkan Dice.

Kolom komponen menunjukkan hal yang sama dari sisi lain. Otsu menghasilkan sekitar 14 bercak per citra, sedangkan adaptive 45. Untuk satu sel dalam satu crop, 45 bercak berarti mask-nya terpecah pecah.

### 9.2 Kenapa adaptive threshold buruk

Dugaan awal yang muncul saat melihat gambar adalah "mask-nya cuma garis tepi". Angka kolom dekat batas menolak dugaan itu: adaptive 0.082, Otsu 0.068. Keduanya sama rendah. Jadi piksel yang lolos bukan garis tepi, melainkan bercak di dalam sel.

Penyebab sebenarnya ada pada cara ambang lokal bekerja:

1. **Adaptive membandingkan tiap piksel dengan rata rata blok 35 piksel di sekitarnya.** Di dalam sel yang cukup tebal, rata rata lokal sudah gelap, sehingga hanya bagian yang sedikit lebih gelap dari rata rata itu yang lolos. Badan sel yang warnanya merata tidak pernah lolos.
2. **Yang tersisa adalah bintik paling gelap**, biasanya tekstur parasit atau butir pigmen. Rata rata mask hanya menutupi 0.31 luas ground truth, dan terpecah menjadi sekitar 45 komponen per citra.
3. **Precision 0.833 terlihat bagus, tetapi menyesatkan.** Bintik yang lolos hampir semuanya memang berada di dalam sel, jadi tidak banyak kesalahan lebihan. Yang gagal adalah cakupan: recall 0.245, artinya sekitar tiga perempat luas sel tidak pernah diambil.
4. **Pada kasus ekstrem efeknya besar.** Di `falciparum_trophozoite_2.png`, mask adaptive hanya menutupi 0.07 luas ground truth sehingga Dice 0.127, padahal Otsu di citra yang sama mencapai 0.789.

Empat citra contoh di subbagian 8.1 notebook adalah kasus Dice adaptive terendah di tiap stadium, satu citra unik per stadium, ditampilkan berdampingan dengan ground truth dan Otsu pada citra yang sama. Sumber citranya dijaga berbeda supaya tidak menampilkan sel duplikat dua kali, karena ada lima pasang crop yang memakai sel sama (lihat 2.2).

### 9.3 Preprocessing terburuk: P1 koreksi background

Kedua varian dinilai dengan segmentasi yang sama, yaitu Otsu multilevel 3, jadi perbedaannya murni dari preprocessing. Dari `perbandingan_preprocessing.csv`:

| Varian | Dice | IoU | Precision | Recall | Rasio luas | Komponen |
|---|---|---|---|---|---|---|
| P0 Lab b | **0.703** | **0.574** | 0.981 | 0.580 | 0.590 | 7.7 |
| P1 koreksi background | 0.438 | 0.287 | 0.925 | 0.294 | 0.326 | 19.6 |

Polanya sama dengan adaptive. Precision P1 masih tinggi, 0.925, tetapi recall jatuh dari 0.580 ke 0.294 dan luas mask dari 0.590 ke 0.326. Jumlah komponennya juga naik dari 7.7 ke 19.6, tanda mask mulai terpecah.

### 9.4 Kenapa koreksi background justru merugikan

- **Yang dikurangi adalah badan sel itu sendiri.** Closing morfologi dengan disk radius 25 menghasilkan perkiraan latar yang halus. Ketika hasilnya dikurangkan dari kanal b, bagian yang luas dan rata ikut terbuang, termasuk sitoplasma sel. Yang tersisa hanya struktur tipis dan gelap.
- **Contoh satu citra memperjelas.** Pada `falciparum_gametocyte_2.png`, Dice P0 0.843 turun menjadi 0.517 setelah koreksi background, dan luas mask turun dari 0.73 menjadi 0.36 kali ground truth.
- **Untuk citra penuh, langkah ini tetap masuk akal**, seperti pada Progress 1. Di citra penuh latarnya lebar dan tidak rata, jadi memperkirakan lalu mengurangkannya membantu. Di crop yang sudah terpusat pada satu sel, latar hanya bagian kecil di pinggir, sehingga koreksi background membuang sinyal yang justru dibutuhkan.

Kesimpulan Bagian 9: baik di metode maupun di preprocessing, yang terburuk bukan yang salah mengambil latar, melainkan yang **terlalu hemat mengambil piksel**. Precision tinggi tidak menolong kalau sebagian besar sel tidak pernah terambil, dan itulah sebabnya recall harus dibaca bersama Dice.

---

## 10. Bagian 11 dan 12: area putih, ekstraksi fitur, klasifikasi

Dua bagian terakhir berbeda arah dari bagian sebelumnya. Bagian 11 memperbaiki cacat citra, Bagian 12 memakai citra itu untuk menebak label.

### 10.1 Bagian 11, area putih

Delapan crop P. vivax punya piksel yang sudah mentok terang. Kriterianya, nilai `L` di kanal Lab minimal 240 dari 255 dan warnanya hampir netral, yaitu selisih `a` dan `b` maksimal 10 dari titik netral 128. Di area itu tidak ada gradasi yang bisa dibaca karena nilainya sudah menempel di batas atas, sehingga histogram dan fitur tekstur ikut melenceng.

**Inpainting** adalah pengisian lubang pada citra dengan menaksir warna dari piksel sekelilingnya. Metode Telea menarik warna dari batas lubang ke arah dalam, jadi hasilnya halus dan tidak menambah tekstur palsu. Radius 5 piksel dipakai karena bintiknya kecil dan tersebar.

| Crop | Luas area putih | Bagian yang menimpa sel | Dice sebelum | Dice sesudah |
|---|---|---|---|---|
| vivax_schizont_2 | 50,0% | 0,0% | 0,374 | 0,349 |
| vivax_trophozoite_3 | 38,8% | 0,2% | 0,503 | 0,503 |
| vivax_schizont_1 | 30,3% | 11,4% | 0,697 | 0,697 |
| vivax_ring_2 | 30,2% | 0,0% | 0,456 | 0,435 |
| vivax_trophozoite_4 | 15,5% | 0,0% | 0,509 | 0,509 |
| vivax_ring_4 | 12,9% | 0,0% | 0,510 | 0,510 |
| vivax_trophozoite_2 | 12,0% | 0,0% | 0,460 | 0,427 |
| vivax_schizont_3 | 4,2% | 0,0% | 0,464 | 0,464 |

Empat hal yang terbaca.

- **Masalahnya milik satu batch.** Kedelapan crop berasal dari P. vivax. Di P. falciparum paling banyak 0,2 persen, yaitu `falciparum_ring_2`, sisanya nol.
- **Area putih hampir seluruhnya di latar.** Hanya `vivax_schizont_1` yang 11,4 persen area putihnya menimpa sel. Sisanya di bawah 0,2 persen.
- **Dice tidak membaik, dan memang bukan itu tujuannya.** Gabungan 32 citra 0,7029 menjadi 0,7004. Pada delapan citra itu 0,4965 menjadi 0,4866. Empat citra tidak berubah sama sekali, empat turun 0,02 sampai 0,03 karena ambang Otsu ikut bergeser.
- **Karena itu angka lama tidak diubah.** Bagian 5 sampai 10 tetap memakai citra asli, dan hanya Bagian 12 yang memakai citra terisi, karena fitur tekstur lebih mudah tertipu dataran putih daripada Dice.

### 10.2 Bagian 12, fitur yang diambil

Dua puluh empat fitur per crop, dibagi tiga kelompok.

| Kelompok | Fitur | Jumlah |
|---|---|---|
| Bentuk sel | luas, keliling, kebulatan, soliditas, kepadatan bbox, eksentrisitas, rasio sumbu | 7 |
| Warna di dalam sel | rata-rata dan simpangan L, a, b, kontras terhadap cincin latar, fraksi piksel gelap dan pucat | 10 |
| Tekstur | GLCM kontras, keseragaman, energi, korelasi, ketidaksamaan, kekasaran Laplacian, entropi | 7 |

**GLCM** adalah matriks pasangan nilai piksel yang bertetangga, dipakai untuk mengukur kasar halusnya tekstur. **Kebulatan** bernilai 1 untuk lingkaran sempurna. **Soliditas** adalah luas sel dibagi luas selubung cembungnya, jadi turun kalau bentuknya berlekuk atau berlubang.

Semua fitur diukur dari **mask ground truth**, bukan dari mask prediksi. Tujuannya supaya yang diuji kemampuan fitur, bukan kualitas segmentasi.

### 10.3 Hasil klasifikasi

Tiga skema validasi dipakai bersamaan.

- **LOO**, satu crop dikeluarkan tiap putaran.
- **GroupKFold**, lima lipatan yang dipisah menurut sel sumber.
- **LOGO**, satu sel sumber dikeluarkan tiap putaran. Ini yang paling jujur, karena lima pasang crop berasal dari sel yang sama tetapi dilabeli stadium berbeda.

| Target | Model | LOO | GroupKFold | LOGO | Baseline |
|---|---|---|---|---|---|
| Spesies | LogReg | 0,938 | 0,938 | 0,938 | 0,500 |
| Spesies | RF | 0,969 | 0,938 | 0,969 | 0,500 |
| Stadium | LogReg | 0,250 | 0,438 | 0,375 | 0,250 |
| Stadium | RF | 0,250 | 0,500 | 0,406 | 0,250 |

Kelompok fitur dipisah untuk melihat sumber sinyalnya.

| Fitur yang dipakai | Spesies | Stadium |
|---|---|---|
| Bentuk saja | 0,719 | 0,250 |
| Warna dan tekstur saja | 0,938 | 0,250 |

Kalau stadium diuji di dalam satu spesies, hanya P. falciparum yang bergerak, 0,562 dengan GroupKFold empat lipatan, sedangkan P. vivax tepat di baseline 0,250.

### 10.4 Cara membaca hasil ini

- **Spesies hampir seluruhnya dikenali dari warna.** `a_rata` dan `b_rata` adalah dua fitur teratas random forest. Kedua spesies di dataset ini dipindai dan diwarnai pada sesi berbeda, jadi sebagian besar yang dipelajari model adalah ciri batch pewarnaan, bukan morfologi parasit.
- **Bentuk saja masih memberi 0,719.** Artinya ukuran dan kebulatan sel memang berbeda antara kedua spesies pada data ini, tetapi asal sediaannya juga berbeda, jadi belum bisa disebut diagnostik.
- **Stadium sulit.** Hasilnya 0,250 sampai 0,500 dengan baseline 0,25, dan arah angkanya berubah antar skema validasi; pada LOO hasilnya tepat di baseline. Dengan 32 citra dan 27 sel unik, itu belum layak dipercaya.
- **Ini batas atas.** Fitur diukur dari ground truth. Pada pemakaian nyata mask harus diprediksi lebih dulu, dan Dice P0 baru 0,70, jadi galat segmentasi akan menurunkan akurasi.
- **Confusion matrix memperlihatkan schizont paling sering ditebak ring**, 6 dari 8. Penyebabnya masuk akal: mask yang dipakai adalah sel terinfeksi, bukan parasit, sehingga bentuk parasit yang membedakan stadium tidak ikut terukur.

---

## 11. Metrik: rumus dan artinya

Semua metrik dihitung dari perbandingan mask prediksi dengan mask ground truth, piksel demi piksel.

| Metrik | Rumus | Arti singkat |
|---|---|---|
| Dice | 2TP / (2TP + FP + FN) | kedekatan keseluruhan, setara F1 untuk piksel |
| IoU | TP / (TP + FP + FN) | perbandingan irisan dengan gabungan, lebih ketat dari Dice |
| Precision | TP / (TP + FP) | dari yang ditebak parasit, berapa persen benar |
| Recall | TP / (TP + FN) | dari parasit yang sebenarnya, berapa persen tertangkap |

TP adalah piksel parasit yang benar terdeteksi, FP piksel latar yang salah dianggap parasit, FN parasit yang terlewat.

Dice dan IoU selalu bergerak bersama, dan nilainya berkisar 0 sampai 1. IoU selalu lebih kecil dari Dice untuk mask yang sama. Precision tinggi dengan recall rendah berarti mask rapi tetapi bolong, sedangkan precision rendah dengan recall tinggi berarti mask menangkap banyak tetapi berantakan.

---

## 12. Semua parameter di satu tempat

| Parameter | Nilai | Dipakai di | Alasan |
|---|---|---|---|
| `PAD` | 80 px | pembuatan mask ground truth | menyisakan latar di sekitar parasit |
| `MIN_AREA` | 12 px | semua metode segmentasi | membuang bintik derau dan sisa tepi |
| ambang tetap | 115 | pixel if-else | hasil sapuan 95 sampai 140, Dice tertinggi |
| kelas Otsu multilevel | 3 | P0 sampai P4 | memisahkan parasit, tepi, dan latar |
| blok adaptive | 35 px | adaptive threshold | cukup besar untuk satu parasit kecil |
| konstanta C adaptive | 5 | adaptive threshold | toleransi terhadap variasi lokal |
| klaster k-means | 3 | k-means | parasit, tepi, latar |
| contoh k-means | 4.000 piksel | k-means | mempercepat, hasil mendekati pemakaian semua piksel |
| median filter | 5x5 | P2, P4 | derau grain Giemsa |
| disk closing | radius 25 | P1, P4 | memperkirakan latar |
| CLAHE | clip 2.0, grid 8x8 | P3 | kontras lokal terkendali |
| ukuran histogram | 256x256 | histogram gabungan | menyamakan ukuran crop |
| radius tepi | 2 px | fraksi dekat batas di Bagian 9 | cukup untuk menandai piksel yang menempel di tepi mask |

Satu catatan soal rata-rata: semua metrik per stadium dan per kelompok dirata-ratakan per citra, sedangkan tabel gabungan di Bagian 8 menjumlahkan piksel lebih dulu. Bagian 9 memakai rata-rata per citra.

---

## 13. File hasil

Semua ada di `results/data_preprocessing/`:

| File | Isi |
|---|---|
| `ringkasan_per_stadium.csv` | 8 baris, statistik data per stadium dan spesies: n, luas sel terinfeksi (kolom `luas_sel_terinfeksi_ribu_px`), rata-rata, median, simpangan baku intensitas |
| `dice_per_stadium.csv` | Dice lima varian preprocessing per stadium (4 baris) |
| `summary.csv` | Dice dan IoU lima varian preprocessing, gabungan 32 citra |
| `dice_metode_per_stadium.csv` | Dice lima metode segmentasi per stadium |
| `summary_metode.csv` | Dice, IoU, precision, recall lima metode, gabungan 32 citra |
| `perbandingan_metode.csv` | Rincian lima metode dengan rata-rata per citra: Dice, IoU, precision, recall, rasio luas, jumlah komponen, fraksi dekat batas |
| `perbandingan_preprocessing.csv` | Rincian P0 dan P1 dengan kolom yang sama seperti di atas, dinilai dengan Otsu multilevel 3 |
| `perbandingan_menyeluruh.csv` | Dice train, test, dan gabungan 32 citra untuk 14 varian, plus selisih berpasangan dan nilai p Wilcoxon |
| `perbandingan_menyeluruh_otsu1.csv` | Angka yang sama dengan Otsu satu ambang, plus peringkat kedua metode |
| `per_image_semua_varian.csv` | Dice tiap citra untuk 14 varian, dengan spesies, stadium, dan split |
| `split_train_test.csv` | Pembagian 2 train dan 2 test tiap kelompok, termasuk penanda sel duplikat |
| `per_image_dice_test.csv` | Dice tiap citra test untuk lima varian dan lima metode, plus selisih terhadap P0 |
| `area_putih.csv` | Luas area putih tiap crop, bagian yang menimpa sel, dan jumlah bintik |
| `area_putih_dice.csv` | Dice P0 sebelum dan sesudah inpainting, per crop |
| `fitur_per_crop.csv` | 24 fitur bentuk, warna, dan tekstur tiap crop, plus spesies, stadium, dan split |
| `klasifikasi_fitur.csv` | Akurasi dan F1 untuk dua target, dua model, tiga skema validasi |
| `klasifikasi_kelompok_fitur.csv` | Akurasi LOGO kalau hanya bentuk atau hanya warna dan tekstur yang dipakai |

Notebook juga menampilkan tabel metadata lengkap dan rincian tiap crop di Bagian 1. Tabel yang muncul di layar tetapi tidak disimpan ke CSV adalah tabel itu, karena isinya sama dengan `metadata.csv`.

---

## 14. Temuan utama

1. **Lab b saja sudah cukup** untuk crop terpusat, dibandingkan rantai yang sekarang dipakai. Semua langkah tambahan menurunkan Dice, dari 0.7029 menjadi 0.44 sampai 0.49. Yang paling merugikan koreksi background, dengan recall hanya 0.29. Dibanding grayscale rata-rata RGB, Lab b unggul 0.0915 (p 0.0079), tetapi dibanding grayscale berbobot `cv2` selisihnya tidak nyata (p 0.0998).
2. **Tingkat kesulitan berbeda antar stadium.** Lab b memberi Dice 0.809 di gametocyte tetapi hanya 0.559 di trophozoite. Jadi satu angka rata-rata untuk 32 citra menyembunyikan masalah di stadium tertentu.
3. **Ambang otomatis mengalahkan ambang tetap.** Otsu satu ambang 0.795 dibanding pixel if-else 0.482, dan selisih itu bukan karena ambang tetap yang dipilih buruk. Pixel if-else kalah karena terlalu banyak mengambil piksel: luas mask 1.13 kali ground truth, precision 0.66.
4. **Ada dua jenis kegagalan, dan keduanya terlihat dari recall serta rasio luas.** Terlalu hemat mengambil piksel (adaptive, Otsu multilevel 3, k-means, P1) memberi precision tinggi tetapi separuh sel hilang. Terlalu banyak mengambil piksel (pixel if-else) memberi recall cukup tetapi menambah latar. Hanya Otsu satu ambang yang seimbang di keduanya.
5. **Adaptive threshold tidak cocok di sini, dan penyebabnya bukan mask berupa garis tepi.** Fraksi piksel dekat batas hanya 0.082, sama rendahnya dengan Otsu 0.068. Penyebabnya, ambang lokal membandingkan piksel dengan rata rata blok 35 piksel, sehingga di dalam sel yang tebal hanya bagian paling gelap yang lolos. Luas yang tertangkap 0.31, mask pecah jadi 45 komponen, recall 0.25.
6. **Precision tinggi bisa menyesatkan.** Precision adaptive 0.833 dan P1 0.925 terlihat bagus, tetapi bintik atau sisa piksel yang lolos hampir semuanya memang berada di dalam sel, sehingga lebihan sedikit. Yang gagal adalah cakupan.
7. **Efek satu langkah bergantung konteks, dan urutannya bergantung metode segmentasi.** Membuang koreksi background dari rantai penuh menaikkan Dice ke 0.5795, sedangkan CLAHE justru menolong di dalam rantai padahal merugikan kalau sendirian (0.583). Dengan Otsu satu ambang, 10 dari 14 varian berubah peringkat. Jadi klaim "langkah ini berguna" harus menyebut pembandingnya dan metode segmentasinya.
8. **Area putih hanya berarti di P. vivax, dan mengisinya tidak menaikkan Dice.** Delapan crop punya piksel jenuh terang, terluas `vivax_schizont_2` separuh luas crop. Setelah diinpainting, Dice gabungan justru 0,7029 menjadi 0,7004. Area itu hampir seluruhnya di latar, jadi yang berubah hanya statistik warna dan tekstur.
9. **Spesies mudah ditebak dari warna, stadium tidak.** Spesies 0,938 sampai 0,969, stadium 0,250 sampai 0,500 dengan baseline 0,25. Fitur bentuk saja memberi 0,719 untuk spesies, sedangkan warna dan tekstur saja 0,938. Karena kedua spesies berasal dari sesi pewarnaan berbeda, keunggulan itu sebagian besar ciri batch.
10. **Yang diukur adalah sel terinfeksi, bukan badan parasit.** Anotasi MP-IDB melingkupi seluruh sel darah merah yang terinfeksi, jadi angka Dice 0.70 sampai 0.79 itu angka segmentasi sel, bukan segmentasi parasit.

---

## 15. Keterbatasan yang perlu disebut kalau hasil ini dipakai

- **Sampel kecil.** Empat citra per kelompok. Rata-rata per kelompok mudah bergeser kalau satu citra berubah, jadi angka per kelompok jangan diperlakukan sebagai estimasi populasi.
- **Perbandingan preprocessing tetap memakai Otsu multilevel 3 sebagai acuan utama.** Versi Otsu satu ambang sekarang ikut dilaporkan di Bagian 7, dan hasilnya memang mengubah peringkat 10 dari 14 varian. Karena itu peringkat resmi di Bagian 7 notebook hanya berlaku untuk Otsu multilevel 3.
- **Ambang pixel if-else dipilih dari train, dan pilihannya gagal pindah ke test.** Sapuan 95 sampai 140 di 16 citra train memilih ambang 130 (Dice train 0.4950), tetapi di 16 citra test ambang 130 hanya 0.3864 sementara ambang 115 mencapai 0.5627. Metode lain tidak punya parameter yang dicari, jadi perbandingan antar metode tetap wajar, tetapi angka mutlak pixel if-else jangan dibaca sebagai performa pada citra baru.
- **Mask ground truth berasal dari anotasi bitmap, bukan dari dokter yang menggambar ulang.** Kualitas anotasi ikut menentukan nilai Dice.
- **Lima pasang crop duplikat.** Dari 32 crop hanya ada 27 sel unik, karena pemilihan crop mengambil objek terbesar dari citra sumber yang bertag dua stadium. Pada tiap pasangan, satu label stadiumnya salah. Daftar pasangannya ada di bagian 2.2.
- **Ground truth tidak memisahkan parasit dari selnya.** Semua metode diuji untuk menangkap sel terinfeksi, sehingga metode yang bagus di sini belum tentu bagus untuk memisahkan badan parasit di dalam sel.
- **k-means memakai 4.000 contoh piksel acak**, jadi hasil bisa bergeser sedikit antar jalannya program.
- **Segmentasi klasik tanpa pelatihan.** Semua metode di sini memakai aturan tetap, bukan model yang belajar dari data. Karena itu train dan test di sini berfungsi sebagai holdout untuk memilih varian dan ambang, bukan uji generalisasi model.
- **Peringkat varian bergantung metode segmentasi.** Dari 14 varian, 10 berubah peringkat antara Otsu multilevel 3 dan Otsu satu ambang. Klaim tentang langkah preprocessing hanya berlaku untuk metode yang dipakai saat menilainya.
- **Fitur diukur dari mask ground truth.** Akurasi klasifikasi di Bagian 12 adalah batas atas. Pada pemakaian nyata mask harus diprediksi lebih dulu, dan Dice P0 yang baru 0,70 akan menurunkan akurasi itu.
- **Klasifikasi memakai 32 baris yang hanya mewakili 27 sel.** Validasi LOGO dipakai untuk menutup kebocoran dari lima pasang crop duplikat, tetapi jumlahnya tetap terlalu kecil untuk kesimpulan yang kuat.
- **Pemisahan spesies tercampur asal sediaan.** Kedua spesies dipindai dan diwarnai pada sesi berbeda, jadi fitur warna yang memisahkan spesies tidak bisa dipakai sebagai bukti morfologi.
- **Kanal dasar dan langkah preprocessing diuji terpisah.** Baseline grayscale hanya diuji dengan Otsu, belum dengan kelima metode segmentasi, jadi belum ada tabel silang antara rumus grayscale dan metode segmentasi.

---

## 16. Kalau ingin mengulang evaluasi tanpa notebook

Inti perhitungannya hanya beberapa langkah. Contoh skrip mandiri:

```python
import cv2, json, base64, zlib, io
import numpy as np, pandas as pd
from PIL import Image
from skimage.filters import threshold_multiotsu
from skimage.morphology import remove_small_objects

ROOT = "citra-segmentasi-malaria"
PAD, MIN_AREA = 80, 12
meta = pd.read_csv(f"{ROOT}/malaria_images/metadata.csv")

cache = {}
def gt_mask(source, r):
    if source not in cache:
        ann = json.load(open(f"{ROOT}/mp-idb-DatasetNinja/ds/ann/{source}.json"))
        full = np.zeros((ann["size"]["height"], ann["size"]["width"]), np.uint8)
        for o in ann["objects"]:
            png = zlib.decompress(base64.b64decode(o["bitmap"]["data"]))
            a = np.array(Image.open(io.BytesIO(png)))
            bm = (a[..., -1] if a.ndim == 3 else a) > 0
            h, w = bm.shape
            oy, ox = o["bitmap"]["origin"][1], o["bitmap"]["origin"][0]
            full[oy:oy+h, ox:ox+w] |= bm.astype(np.uint8)
        cache[source] = full
    x, y, w, h = int(r.bbox_x), int(r.bbox_y), int(r.bbox_w), int(r.bbox_h)
    return cache[source][max(0, y-PAD):y+h+PAD, max(0, x-PAD):x+w+PAD].astype(bool)

def dice(pred, gt):
    tp = (pred & gt).sum()
    return 2 * tp / (pred.sum() + gt.sum() + 1e-9)

def lab_b(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2LAB)[:, :, 2]

def seg_otsu(chan):
    t, _ = cv2.threshold(chan, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return remove_small_objects(chan < t, max_size=MIN_AREA - 1, connectivity=2)

rows = []
for _, r in meta.iterrows():
    img = cv2.cvtColor(cv2.imread(f"{ROOT}/malaria_images/{r.filename}"), cv2.COLOR_BGR2RGB)
    gt = gt_mask(r.source_image, r)
    rows.append({"filename": r.filename, "species": r.species, "stage": r.stage,
                 "dice": dice(seg_otsu(lab_b(img)), gt)})

df = pd.DataFrame(rows)
print(df.groupby(["species", "stage"]).dice.mean().round(4))
print("gabungan:", round(df.dice.mean(), 4))
```

Kalau skrip ini dijalankan, angka gabungannya harus mendekati 0.7948, yaitu Dice Otsu satu ambang pada seluruh 32 citra.

---

## 17. Daftar istilah

| Istilah | Arti |
|---|---|
| crop | potongan citra di sekitar satu sel terinfeksi, hasil pemotongan dari citra mikroskop penuh |
| ground truth | kebenaran acuan, di sini mask sel darah merah terinfeksi hasil anotasi manusia |
| sel darah merah terinfeksi | sel darah merah yang di dalamnya ada parasit, dan area inilah yang dianotasi |
| sel darah putih | sel imun yang jauh lebih besar dari sel darah merah, berinti besar dan bergranula, tidak dianotasi di dataset ini |
| citra mikroskopis | gambar dari mikroskop, diambil dari sediaan darah di kaca objek |
| pewarnaan Giemsa | pewarna yang membuat parasit tampak biru keunguan dan sel darah merah tampak merah muda |
| kanal warna | satu komponen nilai dari ruang warna, misalnya kanal b pada Lab |
| intensitas | tingkat kecerahan piksel, 0 paling gelap sampai 255 paling terang |
| histogram | grafik jumlah piksel untuk tiap nilai intensitas |
| threshold | ambang nilai yang memisahkan parasit dari latar |
| Otsu | metode memilih ambang otomatis dari bentuk histogram |
| multilevel | ambang lebih dari satu tingkat, membagi histogram menjadi beberapa kelas |
| adaptive threshold | ambang yang nilainya berbeda di tiap bagian gambar |
| k-means | metode mengelompokkan data menjadi k kelompok berdasarkan kemiripan nilai |
| morfologi | operasi bentuk pada mask, seperti dilasi, erosi, opening, closing |
| dilasi | menebalkan objek pada mask |
| erosi | menipiskan objek pada mask |
| closing | dilasi lalu erosi, menutup lubang kecil dan menyambung bagian yang berdekatan |
| median filter | penggantian nilai piksel dengan nilai tengah tetangganya, untuk meredam derau |
| CLAHE | pemerataan histogram adaptif dengan batas kontras |
| Reinhard | normalisasi warna berdasarkan rata-rata dan simpangan baku |
| Dice | ukuran kemiripan dua mask, 1 berarti identik |
| IoU | perbandingan irisan dan gabungan dua mask |
| precision | proporsi tebakan parasit yang benar |
| recall | proporsi parasit sebenarnya yang berhasil ditangkap |
| true positive, false positive, false negative | berturut-turut: benar terdeteksi, salah dianggap parasit, parasit terlewat |
| rasio luas | luas mask prediksi dibagi luas ground truth, 1.0 berarti pas |
| komponen terhubung | satu kelompok piksel yang saling bersentuhan; satu sel sehat seharusnya satu komponen |
| fraksi dekat batas | bagian mask yang letaknya maksimal 2 piksel dari tepi ground truth |
| fitur | angka yang diringkas dari citra, misalnya luas atau rata-rata warna, untuk dipakai model |
| area kosong | piksel yang sudah jenuh terang dan tidak lagi membawa gradasi |
| inpainting | pengisian lubang citra dengan menaksir warna dari piksel sekelilingnya |
| GLCM | matriks pasangan nilai piksel bertetangga, dasar ukuran tekstur |
| klasifikasi | penebakan label kategorikal, di sini spesies dan stadium |
| cross validation | pengujian dengan membagi data bergiliran menjadi latihan dan ujian |
| LOGO | leave one group out, satu kelompok, di sini satu sel sumber, dikeluarkan tiap putaran |
