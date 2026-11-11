<!-- page: 1 -->

Rancangan Proyek Pengolahan Citra Digital 

# **Segmentasi Parasit Malaria pada Citra Mikroskopis dengan Metode Pengolahan Citra Klasik** 

Dataset: MP-IDB (Malaria Parasite Image Database)  |  Bahasa: Python (OpenCV, scikit-image) 

## **1. Ringkasan dan Pertanyaan Penelitian** 

Proyek ini menerapkan beberapa tahap dari diagram pengolahan citra digital (akuisisi, enhancement, restoration, morphological processing, segmentation, dan representation) untuk memisahkan parasit malaria dari latar belakang pada citra apusan darah. Fokus utamanya bukan pada satu algoritma, melainkan pada **bagaimana setiap tahap preprocessing memengaruhi kualitas segmentasi** , yang diukur terhadap mask referensi dari ahli. 

#### **Pertanyaan penelitian:** 

_Bagaimana pengaruh teknik preprocessing (pemilihan kanal warna, filtering, CLAHE, dan koreksi background) terhadap akurasi segmentasi parasit malaria menggunakan thresholding dan clustering klasik?_ 

Metode yang dipakai tidak memerlukan pelatihan model, jadi proyek ini tetap ringan dan bisa dikerjakan tanpa GPU. 

## **2. Dataset: MP-IDB** 

Ringkasan berikut diambil dari halaman Dataset Ninja dan deskripsi penulis dataset. Detail struktur file perlu dicek saat mengunduh. 

|**Aspek**|**Keterangan**|
|---|---|
|Sumber dan lisensi|Loddo, Di Ruberto, Kocher, dan Prod'Hom (2019). Lisensi MIT.|
|Akuisisi citra|Mikroskop Leica DM2000, perbesaran 100×, PNG 2592 × 1944 piksel, 24-bit.<br>Semua gambar dari satu mikroskop.|
|Ground truth|Mask tingkat piksel**hanya untuk parasit**. Sel darah merah tidak dianotasi.|
|Kelas|Empat spesies: falciparum, vivax, malariae, ovale. Tersedia pula pembagian<br>tahap: ring, trophozoite, schizont, gametocyte.|
|Jumlah data|Dataset Ninja: 210 gambar dengan 1.407 objek. Deskripsi penulis: 229<br>gambar dengan 840 kandidat parasit. Angka berbeda, jadi periksa repo aslinya<br>sebelum menulis angka di laporan.|
|Ukuran objek|Parasit kecil. Rata-rata luas parasit falciparum sekitar 0,06% dari luas gambar.|
|Masalah citra|Iluminasi latar tidak seragam, tepi overexposed, dan warna bervariasi karena<br>usia apusan. Thresholding sederhana bisa terganggu.|
|Sumber unduhan|datasetninja.com/mp-idb (format Supervisely, sekitar 697 MB) atau repo<br>GitHub asli (andrealoddo/MP-IDB).|



Halaman 1

<!-- page: 2 -->

### **Subset data yang digunakan** 

- Fokus ke P. falciparum: 103 gambar pada Dataset Ninja, rata-rata sekitar 12 parasit per gambar, sehingga statistik evaluasinya lebih stabil. 

- Ambil **30 sampai 40 gambar** secara acak dengan seed tetap, bukan seluruh dataset. 

- Perkecil gambar (misalnya 50%) agar proses cepat. Gunakan interpolasi biasa untuk citra dan **nearest neighbor untuk mask** agar mask tetap biner. 

- Bagi subset menjadi **sekitar 10 gambar untuk tuning parameter** (ambang, ukuran kernel) dan sisanya untuk pengujian. Tidak ada pelatihan model, tetapi pemisahan ini mencegah parameter disesuaikan terhadap data uji. 

## **3. Ruang Lingkup: Tiga Tingkat Pengerjaan** 

Agar proyek tetap wajar, pekerjaan dibagi menjadi tiga tingkat. Tingkat minimum sudah cukup untuk proyek yang utuh. Tingkat berikutnya ditambahkan jika waktu tersedia. 

|**Tingkat**|**Isi**|**Perkiraan beban**|
|---|---|---|
|Minimum|Memuat citra dan mask, kanal hijau atau Lab, median filter,<br>Otsu, opening/closing dan filter luas, evaluasi Dice/IoU,<br>visualisasi overlay.|Ringan|
|Target|Ditambah CLAHE, koreksi background, adaptive thresholding,<br>k-means, tabel eksperimen preprocessing, metrik tingkat<br>objek, deskripsi bentuk.|Sedang|
|Bonus (opsional)|Normalisasi warna (gray-world atau histogram matching),<br>klasifikasi tahap parasit dari fitur bentuk dan warna, uji<br>kompresi JPEG.|Sedang sampai berat|



## **4. Alur Sistem dan Pemetaan ke Diagram** 

|**Tahap pada diagram**|**Teknik yang diterapkan**|**Kesulitan**|**Status**|
|---|---|---|---|
|Image Acquisition|Memuat citra dan mask, memperkecil<br>ukuran, memeriksa histogram tiap kanal.|Mudah|Minimum|
|Colour Image Processing|Membandingkan grayscale, kanal hijau RGB,<br>dan kanal Lab.|Mudah|Minimum|
|Image Restoration|Median filter; Gaussian filter sebagai<br>pembanding.|Mudah|Minimum|
|Image Enhancement|CLAHE pada kanal terpilih.|Mudah|Target|
|Morphological Processing<br>(koreksi background)|Perkirakan background dengan grayscale<br>closing berukuran besar, lalu kurangi atau<br>bagi citra dengan background tersebut.|Sedang|Target|
|Segmentation|Otsu (baseline), adaptive thresholding,<br>k-means.|Sedang|Minimum (Otsu)<br>Target (lainnya)|



Halaman 2

<!-- page: 3 -->

|**Tahap pada diagram**|**Teknik yang diterapkan**|**Kesulitan**|**Status**|
|---|---|---|---|
|Morphological Processing<br>(pasca-segmentasi)|Opening, closing, connected components,<br>filter luas.|Mudah|Minimum|
|Representation &|Luas, keliling, circularity; bandingkan|Mudah|Target|
|Description|distribusinya antara mask ahli dan mask<br>prediksi.|||



**Tidak dipakai:** Object Recognition, Image Compression, dan watershed. Ketiganya tidak diperlukan untuk menjawab pertanyaan penelitian, dan tidak semua kotak pada diagram harus diimplementasikan. 

### **Catatan teknis penting** 

**Koreksi background.** Parasit dan sel berwarna lebih gelap daripada latar yang terang. Maka estimasi background dilakukan dengan **grayscale closing** (yang mengisi objek gelap kecil), bukan opening. Alternatifnya adalah blur Gaussian atau median berukuran sangat besar. Ukuran structuring element harus lebih besar daripada parasit dan sel yang berdekatan. 

**Tantangan utama segmentasi.** Sel darah merah juga lebih gelap daripada latar, sehingga threshold satu tingkat pada satu kanal akan menangkap sel dan parasit sekaligus. Parasit umumnya lebih gelap dan lebih keunguan daripada sitoplasma sel. Karena itu gunakan **multi-level Otsu (3 kelas) atau k-means dengan k = 3** , lalu ambil kelas yang paling gelap atau paling ungu. Periksa dulu pada beberapa gambar sebelum memilih kanal. Inti sel darah putih, trombosit, dan artefak pewarnaan bisa ikut tertangkap sebagai false positive. Catat ini sebagai keterbatasan, jangan berusaha menghilangkan semuanya. 

## **5. Eksperimen** 

### **Eksperimen A: perbandingan metode segmentasi** 

Gunakan preprocessing minimal yang sama (kanal terpilih dan median filter), lalu bandingkan Otsu (multi-level), adaptive thresholding, dan k-means. Semuanya dievaluasi dengan prosedur yang sama. 

### **Eksperimen B: pengaruh preprocessing** 

Pilih satu metode segmentasi sebagai baseline (misalnya multi-level Otsu), lalu variasikan preprocessing-nya. 

|**No.**|**Preprocessing**|**Segmentasi**|
|---|---|---|
|1|Tidak ada (kanal terpilih saja)|Baseline|
|2|Median filter|Baseline|
|3|CLAHE|Baseline|
|4|Koreksi background|Baseline|
|5|Kombinasi terbaik dari percobaan 2 sampai 4|Baseline|



Halaman 3

<!-- page: 4 -->

Hasil yang tidak mendukung dugaan tetap sah. CLAHE bisa membuat parasit lebih jelas secara visual, tetapi menurunkan Dice karena noise ikut menguat. Itu temuan yang layak dibahas. 

### **Eksperimen C: pengaruh morfologi pasca-segmentasi** 

Bandingkan mask sebelum dan sesudah opening/closing dan filter luas. Coba tiga nilai ambang luas (kecil, sedang, besar). Amati perubahan Dice, IoU, jumlah komponen, dan apakah parasit asli ikut terhapus (turunnya recall). 

## **6. Evaluasi** 

**Tingkat piksel** (per gambar, laporkan rata-rata, median, dan simpangan baku): 

Dice = 2 |P ∩ G| / (|P| + |G|) 

IoU = |P ∩ G| / |P ∪ G| 

dengan P adalah mask prediksi dan G adalah mask ahli. 

**Tingkat objek.** Karena parasit sangat kecil, Dice bisa sangat berubah hanya karena selisih beberapa piksel di tepi. Tambahkan metrik objek sederhana: 

- **Recall:** persentase parasit pada mask ahli yang tumpang-tindih dengan setidaknya satu komponen prediksi. 

- **Precision:** persentase komponen prediksi yang tumpang-tindih dengan parasit pada mask ahli. 

- Rata-rata jumlah false positive per gambar. 

**Visualisasi** untuk tiap contoh: citra asli, hasil preprocessing, mask biner, dan overlay (mask ahli berwarna hijau, prediksi berwarna merah). 

**Ekspektasi.** Jangan menargetkan angka tertentu. Pada objek sekecil ini, metode klasik wajar menghasilkan Dice sedang dan cukup banyak false positive. Nilai proyek terletak pada analisis: tahap mana yang membantu, tahap mana yang merugikan, dan mengapa. 

## **7. Risiko dan Cara Mengatasinya** 

|**Risiko**|**Penanganan**|
|---|---|
|Gambar besar sehingga proses<br>lambat|Perkecil gambar, gunakan subset 30 sampai 40 gambar, simpan hasil<br>antara agar tidak dihitung ulang.|
|Banyak false positive (sel darah<br>merah, inti sel darah putih,<br>artefak)|Multi-level Otsu atau k-means k = 3, filter luas, dan laporkan precision<br>tingkat objek.|
|Parasit kecil ikut terhapus oleh<br>filter luas|Uji beberapa ambang luas pada Eksperimen C dan pantau recall.|
|Format anotasi berbeda dari<br>dugaan|Pada hari pertama, tulis fungsi pemuat dan uji pada satu gambar:<br>tampilkan citra dan mask berdampingan.|
|Preprocessing tidak meningkatkan<br>metrik|Ini hasil yang valid. Bahas penyebabnya (misalnya noise ikut menguat<br>atau detail kecil hilang).|



Halaman 4

<!-- page: 5 -->

|**Risiko**|**Penanganan**|
|---|---|
|Parameter terlalu disesuaikan<br>dengan data uji|Tentukan parameter pada gambar tuning, lalu uji pada gambar lainnya.|



Halaman 5

<!-- page: 6 -->

## **8. Urutan Pengerjaan** 

1. **Persiapan.** Unduh dataset, periksa format, tampilkan beberapa citra beserta mask, pilih subset, dan pisahkan gambar tuning. 

2. **Baseline (tingkat minimum).** Bangun pipeline dasar dan fungsi evaluasi, lalu jalankan pada seluruh subset. 

3. **Eksperimen (tingkat target).** Tambahkan CLAHE, koreksi background, adaptive thresholding, dan k-means, lalu jalankan Eksperimen A sampai C. 

4. **Analisis.** Susun tabel hasil, pilih contoh keberhasilan dan kegagalan, dan cari penyebabnya. 

5. **Laporan.** Tuliskan tujuan, dasar teori tiap tahap yang dipakai, hasil, serta pembahasan dan keterbatasan. 

## **9. Catatan Perubahan dari Rancangan Awal** 

Bagian ini merangkum koreksi yang dilakukan agar proyek tetap realistis dan teknisnya tepat. 

|**Bagian**|**Perbaikan**|
|---|---|
|Ketersediaan mask|Rancangan awal masih meragukan keberadaan mask. Setelah dicek,<br>MP-IDB memiliki mask tingkat piksel untuk parasit, jadi tidak perlu berganti<br>dataset. Perlu diingat mask hanya untuk parasit, bukan untuk sel darah<br>merah.|
|Koreksi background|Diubah dari opening menjadi closing, karena objek yang ingin dihilangkan<br>dari estimasi background (sel dan parasit) lebih gelap daripada latarnya.|
|Cakupan data|Dari seluruh dataset menjadi subset 30 sampai 40 gambar falciparum yang<br>diperkecil, dengan pemisahan gambar tuning dan uji.|
|Tantangan segmentasi|Rancangan awal menganggap parasit cukup mudah dipisahkan karena lebih<br>gelap. Kenyataannya sel darah merah juga gelap, sehingga ditambahkan<br>multi-level Otsu atau k-means k = 3.|
|Evaluasi|Ditambah metrik tingkat objek (recall, precision, false positive), karena Dice<br>pada objek yang sangat kecil tidak stabil.|
|Eksperimen B|Disederhanakan dari enam menjadi lima konfigurasi; kombinasi hanya<br>untuk preprocessing yang terbukti membantu.|
|Object Recognition dan<br>klasifikasi|Dikeluarkan dari bagian wajib dan dipindahkan ke opsi bonus agar fokus<br>tetap pada segmentasi.|
|Struktur proyek|Ditambahkan tiga tingkat pengerjaan (minimum, target, bonus) supaya ada<br>versi minimal yang pasti selesai.|



Referensi dataset: Loddo, A., Di Ruberto, C., Kocher, M., dan Prod'Hom, G. (2019). MP-IDB: The Malaria Parasite Image Database for Image Processing and Analysis. Dalam Processing and Analysis of Biomedical Information, Springer, hlm. 57–65. 

Halaman 6