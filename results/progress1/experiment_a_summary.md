# Ringkasan Eksperimen A

- Data: 32 citra (falciparum + vivax; 16 tuning, 16 uji; 2 per spesies x stadium x split), resize 50%.
- Kanal terpilih untuk Otsu/adaptive: `b` (Lab b).
- Metode utama terbaik pada test: `Adaptive threshold` (mean Dice 0.1649).
- Pixel-if-else (tambahan) mean Dice: 0.1998.

## Mean Dice per metode (test)

```
method
Pixel if-else (tambahan)    0.1998
Adaptive threshold          0.1649
Otsu multilevel 3           0.0849
k-means k=3                 0.0252
```

## Catatan

- `Adaptive threshold`: Dice 0.1649; pixel precision 0.236, pixel recall 0.204; object recall 0.287, object precision 0.025; FP objek 276.5/citra.
- `Otsu multilevel 3`: Dice 0.0849; pixel precision 0.077, pixel recall 0.668; object recall 0.806, object precision 0.072; FP objek 257.2/citra.
- `k-means k=3`: Dice 0.0252; pixel precision 0.015, pixel recall 0.710; object recall 0.763, object precision 0.019; FP objek 183.3/citra.
- `Pixel if-else (tambahan)`: Dice 0.1998; pixel precision 0.200, pixel recall 0.245; object recall 0.464, object precision 0.037; FP objek 50.7/citra.

- Metode threshold global menangkap area luas (sel darah merah, tepi citra, artefak), sehingga pixel precision rendah meskipun recall piksel bisa tinggi.
- Pixel-if-else menghasilkan komponen paling sedikit, tetapi recall-nya rendah: sebagian parasit tidak lolos ambang warna.
- Eksperimen B (CLAHE, koreksi background, tekstur, kontrol negatif opening) dan Eksperimen C (morfologi, filter luas, object-level if-else) sudah dijalankan.