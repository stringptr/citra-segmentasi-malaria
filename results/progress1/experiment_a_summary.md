# Ringkasan Eksperimen A

- Data: 20 citra P. falciparum (10 tuning, 10 uji), resize 50%.
- Kanal terpilih untuk Otsu/adaptive: `b` (Lab b).
- Metode utama terbaik pada test: `Adaptive threshold` (mean Dice 0.0972).
- Pixel-if-else (tambahan) mean Dice: 0.0845.

## Mean Dice per metode (test)

```
method
Adaptive threshold          0.0972
Otsu multilevel 3           0.0878
Pixel if-else (tambahan)    0.0845
k-means k=3                 0.0320
```

## Catatan

- `Adaptive threshold`: Dice 0.0972; pixel precision 0.348, pixel recall 0.105; object recall 0.100, object precision 0.000; FP objek 159.9/citra.
- `Otsu multilevel 3`: Dice 0.0878; pixel precision 0.071, pixel recall 0.272; object recall 0.342, object precision 0.012; FP objek 321.5/citra.
- `k-means k=3`: Dice 0.0320; pixel precision 0.017, pixel recall 0.719; object recall 0.744, object precision 0.038; FP objek 322.6/citra.
- `Pixel if-else (tambahan)`: Dice 0.0845; pixel precision 0.151, pixel recall 0.095; object recall 0.147, object precision 0.015; FP objek 36.8/citra.

- Metode threshold global menangkap area luas (sel darah merah, tepi citra, artefak), sehingga pixel precision rendah meskipun recall piksel bisa tinggi.
- Pixel-if-else menghasilkan komponen paling sedikit, tetapi recall-nya rendah: sebagian parasit tidak lolos ambang warna.
- Eksperimen B (CLAHE, koreksi background, tekstur, kontrol negatif opening) sudah dijalankan; Eksperimen C (morfologi, filter luas, object-level if-else) belum dijalankan.