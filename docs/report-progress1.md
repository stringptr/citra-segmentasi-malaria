# **PROJECT**

# **ANALISIS DATA CITRA BIOMEDIK**

# **SEGMENTASI PARASIT MALARIA PADA CITRA MIKROKOPIS**

![][image1]

Disusun oleh:

| Fathul Fajar Nur Ikhsan | L0224018 |
| :---- | :---- |
| Satria Manggala Putra Pratama | L0224024 |
| Adrian Farrel Aziz Yatyoga | L0224040  |

**PROGRAM STUDI SAINS DATA**  
**FAKULTAS TEKNOLOGI INFORMASI DAN SAINS DATA**  
**UNIVERSITAS SEBELAS MARET**  
**2026**

# **BAB I**

# **PENDAHULUAN**

1. **Latar belakang**

   Pemeriksaan apusan darah, misalnya untuk mendeteksi fase ring stage parasit Plasmodium falciparum, saat ini masih dilakukan secara manual dan sangat bergantung pada pengalaman pemeriksa. Kondisi ini menimbulkan beberapa tantangan. Pertama, adanya variasi antarpemeriksa membuat hasil pemeriksaan bersifat subjektif, melelahkan, dan sulit direproduksi. Kedua, ukuran objek yang diamati sangat kecil, karena rata-rata luas parasit P. falciparum dan P. vivax hanya sekitar 0,06% dari luas citra. Ketiga, kondisi citra sering tidak ideal akibat iluminasi latar yang tidak seragam, tepi citra yang overexposed, serta warna yang berubah seiring usia apusan.

   Dengan kondisi tersebut, pendekatan yang hanya mengandalkan satu threshold global hampir pasti gagal. Selain itu, kesalahan kecil pada tahap awal segmentasi akan merambat dan merusak keseluruhan pipeline analisis berikutnya, sehingga tahap segmentasi perlu dirancang dan dievaluasi dengan cermat.

   

   2. **Celah Penelitian**

   Terdapat tiga hal yang membentuk celah penelitian pada tema ini.

1. Diagnosis manual: akurasi bergantung pada mata, pengalaman, dan kejelian pemeriksa, sehingga terdapat peluang untuk mengukur kualitas pendekatan otomatis secara objektif.  
2. Lompatan langsung ke deep learning: pendekatan ini membutuhkan GPU, data berukuran besar, dan menghasilkan keputusan yang sulit dijelaskan.  
3. Preprocessing yang jarang diuji: kontribusi setiap tahap preprocessing tidak diukur secara sistematis.  
   Peluang penelitian terletak pada pipeline klasik yang transparan, ringan, dan dapat dijelaskan, sebagai fondasi sebelum beralih ke model yang lebih kompleks.  
     
   3. **Rumusan Masalah**

   Pertanyaan utama penelitian ini adalah: bagaimana pengaruh pemilihan kanal warna, filtering, CLAHE, dan koreksi background terhadap akurasi segmentasi parasit malaria? Pertanyaan tersebut dirinci menjadi dua sub-pertanyaan berikut.

1. Tahap preprocessing mana yang paling membantu, yaitu yang menaikkan akurasi (Dice) dan menurunkan jumlah false positive?  
2. Bagaimana penanganan objek kecil, yaitu apakah filter dan operasi morfologi justru menghapus parasit asli?

   4. **Batasan Masalah**  
1. Segmentasi yang dilakukan bersifat biner (parasit dan bukan parasit).  
2. Tidak ada pelatihan model, sehingga seluruh metode berupa pengolahan citra klasik.  
3. Penelitian tidak mencakup klasifikasi spesies.  
4. Data dibatasi pada citra P. falciparum dari MP-IDB, dengan subset 20 citra yang dipilih secara acak dengan seed tetap, terdiri atas 10 citra untuk tuning parameter dan 10 citra untuk pengujian.

   

   5. **Tujuan**

   Tujuan penelitian ini adalah membangun pipeline segmentasi parasit malaria dan mengukur dampak setiap tahap preprocessing terhadap kualitas segmentasi. Luaran yang diharapkan adalah hasil segmentasi, perbandingan dengan ground truth, dan contoh kasus gagal beserta analisis penyebabnya.

   

   6. **Manfaat**  
1. Baseline terbuka: menjadi pembanding bagi metode lain dan memudahkan reproduksi hasil.  
2. Bahan ajar: menjadi contoh alur pengolahan citra end-to-end.  
3. Peta empiris tahap preprocessing yang layak digunakan untuk segmentasi objek kecil.

   7. **Penelitian Sebelumnya**

   Beberapa penelitian terdahulu yang menjadi rujukan tema ini adalah sebagai berikut.

1. Aris dan kawan-kawan (2023) mengembangkan kerangka pengolahan citra yang tangguh untuk pengenalan parasit malaria multi-stage pada citra thick smear dan thin smear.  
2. Sora-Cardenas dan kawan-kawan (2025) meneliti deteksi dan klasifikasi parasit malaria serta leukosit berbasis citra, disertai penilaian kualitas apusan darah dengan pewarnaan Romanowsky.  
3. Swastika dan kawan-kawan (2021) menunjukkan bahwa preprocessing yang efektif pada citra thin blood smear dapat meningkatkan deteksi parasit malaria menggunakan deep learning.  
   Penelitian-penelitian tersebut menunjukkan pentingnya preprocessing, tetapi kontribusi tiap tahap pada pipeline klasik untuk segmentasi parasit yang sangat kecil belum diuji secara sistematis. Hal inilah yang diisi oleh proyek ini.  
     
   

# **BAB II**

# **DASAR TEORI**

1. ## **Malaria dan Pemeriksaan Apusan Darah**

   ## Malaria disebabkan oleh parasit genus Plasmodium. Empat spesies yang tercakup pada dataset penelitian ini adalah P. falciparum, P. vivax, P. malariae, dan P. ovale. Diagnosis umumnya dilakukan dengan memeriksa apusan darah di bawah mikroskop untuk menemukan parasit pada berbagai tahap hidup, yaitu ring, trophozoite, schizont, dan gametocyte. Karena dilakukan secara manual, hasil pemeriksaan bergantung pada keahlian pemeriksa.

2. ## **Dataset MP-IDB**

   ## MP-IDB (Malaria Parasite Image Database) dikembangkan oleh Loddo, Di Ruberto, Kocher, dan Prod'Hom (2019) dan dirilis dengan lisensi MIT. Karakteristik dataset ini dirangkum pada tabel berikut.

| Aspek | Keterangan |
| ----- | ----- |
| Akuisisi citra | Mikroskop Leica DM2000, perbesaran 100×, format PNG, resolusi 2592 × 1944 piksel, 24-bit |
| Ground truth | Mask tingkat piksel hanya untuk parasit; sel darah merah tidak dianotasi |
| Kelas | P. falciparum, P. vivax, P. malariae, P. ovale; terdapat pula pembagian tahap ring, trophozoite, schizont, gametocyte |
| Jumlah data | Menurut Dataset Ninja: 210 citra dengan 1.407 objek terlabel (103 P. falciparum, 40 P. vivax, 37 P. malariae, 29 P. ovale) |
| Ukuran objek | Rata-rata luas parasit P. falciparum sekitar 0,06% dari luas citra |
| Sumber unduhan | datasetninja.com/mp-idb (sekitar 697 MB) dan github.com/andrealoddo/MP-IDB |

   ## Catatan: penulis dataset melaporkan 229 citra dengan 840 kandidat parasit, sedangkan Dataset Ninja melaporkan 210 citra dengan 1.407 objek. Perbedaan angka ini perlu diverifikasi pada repositori asli sebelum angka dicantumkan pada laporan akhir, demikian pula rincian jumlah citra per spesies dan format anotasi.

   

3. ## **Tahapan Pengolahan Citra Digital**

   ## Proyek ini menerapkan beberapa tahap dari diagram pengolahan citra digital (Gonzalez dan Woods, 2018), yang diuraikan berikut.

1. ## Image Acquisition.    Tahap pemerolehan citra digital beserta mask referensi. Pada tahap ini dilakukan pemuatan data, resize, dan pemeriksaan histogram tiap kanal untuk memahami distribusi intensitas.

2. ## Colour Image Processing.    Pengolahan berdasarkan ruang warna. Pada penelitian ini dibandingkan grayscale, kanal hijau pada ruang warna RGB, dan kanal pada ruang warna Lab. Kanal hijau umumnya memberikan kontras yang baik pada parasit yang berwarna keunguan, sedangkan ruang Lab memisahkan informasi luminans dari informasi warna.

3. ## Image Restoration.    Upaya mengurangi degradasi seperti noise. Median filter dipakai karena mampu meredam noise impulsif sambil mempertahankan tepi, sedangkan Gaussian filter dipakai sebagai pembanding.

4. ## Image Enhancement.    Perbaikan kontras, dalam hal ini CLAHE (Contrast Limited Adaptive Histogram Equalization) yang memeratakan histogram secara lokal dengan batas penguatan kontras (Zuiderveld, 1994). CLAHE dapat memperjelas parasit secara visual, tetapi berpotensi menguatkan noise.

5. ## Morphological Processing (koreksi background).    Iluminasi latar yang tidak seragam dikoreksi dengan memperkirakan background menggunakan grayscale closing berukuran besar, lalu citra dikurangi atau dibagi dengan background tersebut. Closing dipilih, bukan opening, karena objek yang ingin dihilangkan dari estimasi background (sel dan parasit) lebih gelap daripada latarnya. Opening justru akan menghapus objek gelap tersebut dari hasil sehingga tidak sesuai tujuan. Ukuran structuring element harus lebih besar daripada parasit dan sel yang berdekatan.

6. ## Ekstraksi Fitur Pra-Segmentasi.    Pemanfaatan fitur warna atau intensitas, tekstur (GLCM atau LBP), dan statistik lokal sebagai informasi tambahan sebelum segmentasi.

7. ## Segmentation.    Pemisahan parasit dari latar belakang. Metode yang dipakai adalah Otsu multi-level (baseline), adaptive thresholding, dan k-means. Metode Otsu menentukan threshold yang memaksimalkan varians antarkelas (Otsu, 1979). Adaptive thresholding menghitung threshold secara lokal sehingga lebih tahan terhadap iluminasi tidak seragam. K-means mengelompokkan piksel berdasarkan kemiripan fitur.

8. ## Morphological Processing (pasca-segmentasi).    Pembersihan mask melalui opening, closing, connected components, dan filter luas untuk membuang komponen kecil yang bukan parasit.

9. ## Representation and Description.    Penggambaran objek melalui luas, keliling, dan circularity, lalu distribusinya dibandingkan antara mask ahli dan mask prediksi.

   ## Object Recognition, Image Compression, dan watershed tidak digunakan pada proyek ini karena tidak diperlukan untuk menjawab pertanyaan penelitian.

   ## 

4. ## **Tantangan Pemisahan Parasit dari Sel Darah Merah**

   ## Sel darah merah juga lebih gelap daripada latar yang terang. Akibatnya, threshold satu tingkat pada satu kanal akan menangkap sel darah merah dan parasit sekaligus. Parasit umumnya lebih gelap dan lebih keunguan daripada sitoplasma sel, sehingga diperlukan lebih dari dua kelas intensitas. Solusinya adalah Otsu 3 kelas atau k-means dengan k \= 3, lalu mengambil kelas yang paling gelap atau paling ungu. Jumlah cluster divalidasi secara visual. Inti sel darah putih, trombosit, dan pewarnaan yang tidak rata tetap dapat tertangkap sebagai false positive. Hal ini dicatat sebagai keterbatasan dan tidak dipaksakan untuk dihilangkan seluruhnya.

   ##  

5. ## **Metrik Evaluasi**

   ## Tingkat piksel dihitung per citra, kemudian diringkas dengan mean, median, dan standar deviasi.

* ## Dice \= 2 \|P ∩ G\| / (\|P\| \+ \|G\|)

* ## IoU \= \|P ∩ G\| / \|P ∪ G\|

  ## dengan P adalah mask prediksi dan G adalah mask ground truth dari ahli.

  ## Tingkat objek. Karena parasit sangat kecil, nilai Dice dapat berubah drastis hanya karena selisih beberapa piksel di tepi. Oleh karena itu ditambahkan metrik berikut.

* ## Recall: persentase parasit pada mask ahli yang tumpang-tindih dengan setidaknya satu komponen prediksi.

* ## Precision: persentase komponen prediksi yang tumpang-tindih dengan parasit pada mask ahli.

* ## FP per citra: rata-rata jumlah false positive per citra.

  ## 	

# **BAB III**

# **METODOLOGI**

1. ## **Alur Umum**

   ## Prinsip yang dipegang adalah mengubah satu blok pada satu waktu dan menjaga blok lainnya tetap, lalu membandingkan hasil pada citra uji yang sama. Setiap tahap diuji, bukan diasumsikan memberikan perbaikan.

2. ## **Data dan Subset**

1. ## Data yang digunakan adalah citra P. falciparum dari MP-IDB (103 citra, rata-rata sekitar 12 parasit per citra).

2. ## Diambil 20 citra secara acak dengan seed tetap agar subset dapat direproduksi.

3. ## Citra diperkecil sekitar 50% agar proses cepat. Interpolasi biasa digunakan untuk citra, sedangkan nearest neighbor digunakan untuk mask agar mask tetap biner.

4. ## Subset dibagi menjadi 10 citra untuk tuning parameter (ambang dan ukuran kernel) dan 10 citra untuk pengujian. Data uji tidak disentuh saat memilih parameter sehingga parameter tidak menyesuaikan diri terhadap data uji.

3. ## **Tingkat Pengerjaan**

| Tingkat | Isi |
| ----- | ----- |
| Minimum | Memuat citra dan mask, pemilihan kanal warna, median filter, Otsu, opening dan closing, filter luas, evaluasi Dice dan IoU, serta visualisasi overlay |
| Target | Ditambah CLAHE, koreksi background, adaptive thresholding, k-means, metrik tingkat objek, dan deskripsi bentuk |

   ## 

4. ## **Pipeline Pengolahan Citra**

| Tahap | Teknik yang diterapkan | Status |
| ----- | ----- | ----- |
| Akuisisi | Memuat citra dan mask, resize, cek histogram per kanal | Minimum |
| Warna | Membandingkan grayscale, kanal hijau RGB, dan kanal Lab | Minimum |
| Restorasi | Median filter; Gaussian filter sebagai pembanding | Minimum |
| Enhancement | CLAHE pada kanal terpilih | Target |
| Morfologi pra-segmentasi | Estimasi background dengan closing besar, lalu kurangi atau bagi | Target |
| Ekstraksi fitur pra-segmentasi | Fitur warna atau intensitas, tekstur (GLCM atau LBP), statistik lokal | Minimum atau Target |
| Segmentasi | Otsu multi-level (baseline), adaptive thresholding, k-means | Minimum atau Target |
| Morfologi pasca-segmentasi | Opening, closing, connected components, filter luas | Minimum |
| Representasi pasca-segmentasi | Luas, keliling, circularity; membandingkan mask ahli dan mask prediksi | Target |

   ## 

5. ## **Rancangan Eksperimen**

1. ## Eksperimen A    Perbandingan metode segmentasi. Dengan preprocessing minimal yang sama (kanal terpilih dan median filter), dibandingkan Otsu multi-level, adaptive thresholding, dan k-means. Seluruhnya dievaluasi dengan prosedur yang sama.

2. ## Eksperimen B    Pengaruh preprocessing. Satu metode segmentasi dipilih sebagai baseline (misalnya Otsu multi-level), lalu preprocessing divariasikan dengan menambahkan satu per satu: tanpa tambahan, median filter, CLAHE, koreksi background, ekstraksi fitur, dan kombinasi terbaik. Untuk koreksi background, opening diuji sebagai kontrol negatif guna membuktikan bahwa closing merupakan pilihan yang tepat.

3. ## Eksperimen C    Pengaruh morfologi pasca-segmentasi. Mask dibandingkan sebelum dan sesudah opening atau closing serta filter luas, dengan tiga ambang luas (kecil, sedang, besar). Diamati perubahan Dice, IoU, jumlah komponen, dan apakah parasit asli ikut terhapus (ditandai penurunan recall).

   ## Hasil yang tidak mendukung dugaan tetap merupakan temuan yang sah. Sebagai contoh, CLAHE dapat memperjelas parasit secara visual, tetapi menurunkan Dice karena noise ikut menguat.

   ## 

6. ## **Evaluasi dan Visualisasi**

   ## Evaluasi memakai metrik pada Subbab 2.5, dihitung per citra lalu diringkas dengan mean, median, dan standar deviasi, sehingga tidak hanya satu angka agregat yang ditampilkan. Visualisasi untuk tiap contoh terdiri atas citra asli, hasil preprocessing, mask biner, dan overlay (mask ahli berwarna hijau, prediksi berwarna merah).

   ## Pada ekspektasi hasil, tidak ditetapkan target angka tertentu. Pada objek sekecil ini, metode klasik wajar menghasilkan Dice sedang dan false positive yang cukup banyak. Nilai proyek terletak pada analisis tahap mana yang membantu, tahap mana yang merugikan, dan mengapa.

7. ## **Risiko dan Mitigasi**

| Risiko | Mitigasi |
| ----- | ----- |
| Citra besar sehingga proses lambat | Gunakan subset kecil, resize sekitar 50%, dan simpan hasil antara |
| False positive banyak | Otsu multi-level atau k-means k \= 3, filter luas, dan laporkan precision tingkat objek |
| Parasit kecil terhapus oleh filter luas | Uji beberapa ambang luas dan pantau recall, bukan hanya Dice |
| Format anotasi berbeda dari dugaan | Tulis fungsi pemuat dan uji pada satu citra di hari pertama |
| Preprocessing tidak menaikkan metrik | Hasil tetap valid; bahas penyebabnya dan laporkan sebagai temuan |
| Parameter terlalu disesuaikan dengan data uji | Tetapkan parameter pada 10 citra tuning, lalu uji pada citra lainnya |

   ## 

8. ## **Urutan Pengerjaan**

1. ## Persiapan: mengunduh dataset, memeriksa format, menampilkan beberapa citra beserta mask, memilih subset, dan memisahkan citra tuning.

2. ## Baseline (tingkat minimum): membangun pipeline dasar dan fungsi evaluasi, lalu menjalankannya pada seluruh subset.

3. ## Eksperimen (tingkat target): menambahkan CLAHE, koreksi background, adaptive thresholding, dan k-means, lalu menjalankan Eksperimen A sampai C.

4. ## Analisis: menyusun tabel hasil, memilih contoh keberhasilan dan kegagalan, dan mencari penyebabnya.

5. ## Laporan: menuliskan tujuan, dasar teori, hasil, pembahasan, dan keterbatasan.

## 

9. ## **Keterbatasan**

   ## Penelitian ini hanya menggunakan citra dari satu mikroskop, mask ground truth hanya tersedia untuk parasit, dan metode yang dipakai bersifat klasik tanpa pembelajaran. Artefak seperti inti sel darah putih, trombosit, dan pewarnaan tidak rata diperkirakan tetap lolos sebagai false positive.

   ## 

   ## 

# **Daftar Pustaka**

# 

Aris, T.A., Abdul Nasir, A.S., Mustafa, W.A., Mashor, M.Y., Haryanto, E.V., dan Mohamed, Z. (2023). Robust Image Processing Framework for Intelligent Multi-Stage Malaria Parasite Recognition of Thick and Thin Smear Images. Diagnostics, 13(3), 511\. DOI: 10.3390/diagnostics13030511.

Gonzalez, R.C., dan Woods, R.E. (2018). Digital Image Processing (edisi ke-4). Pearson.

Loddo, A., Di Ruberto, C., Kocher, M., dan Prod'Hom, G. (2019). MP-IDB: The Malaria Parasite Image Database for Image Processing and Analysis. Dalam Processing and Analysis of Biomedical Information, Lecture Notes in Computer Science, Springer, hlm. 57 sampai 65\. DOI: 10.1007/978-3-030-13835-6\_7.

Otsu, N. (1979). A Threshold Selection Method from Gray-Level Histograms. IEEE Transactions on Systems, Man, and Cybernetics, 9(1), 62 sampai 66\.

Sora-Cardenas, J., Fong-Amaris, W.M., Salazar-Centeno, C.A., Castañeda, A., Martínez-Bernal, O.D., Suárez, D.R., dan Martínez, C. (2025). Image-Based Detection and Classification of Malaria Parasites and Leukocytes with Quality Assessment of Romanowsky-Stained Blood Smears. Sensors, 25(2), 390\. DOI: 10.3390/s25020390.

Swastika, W., Kristianti, G.M., dan Widodo, R.B. (2021). Effective preprocessed thin blood smear images to improve malaria parasite detection using deep learning. Journal of Physics: Conference Series, 1869, 012092\. DOI: 10.1088/1742-6596/1869/1/012092.

Zuiderveld, K. (1994). Contrast Limited Adaptive Histogram Equalization. Dalam P.S. Heckbert (Ed.), Graphics Gems IV, Academic Press, hlm. 474 sampai 485\.

[image1]: <data:image/png;base64,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>